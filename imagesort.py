import argparse
import configparser
import os
import shutil
from pathlib import Path

import torch
from PIL import Image
from huggingface_hub.utils import disable_progress_bars
from huggingface_hub.utils import logging as hf_hub_logging
from transformers import (
    AutoModel,
    AutoProcessor,
    BlipForConditionalGeneration,
    BlipProcessor,
    CLIPModel,
    CLIPProcessor,
)
from transformers.utils import logging as hf_logging
from sentence_transformers import SentenceTransformer, util

hf_logging.set_verbosity_error()
hf_logging.disable_progress_bar()
hf_hub_logging.set_verbosity_error()
disable_progress_bars()


INPUT_FOLDER = Path(__file__).parent / "input"
OUTPUT_FOLDER = Path(__file__).parent / "output"
CONFIG_PATH = Path(__file__).parent / "config.ini"
CONFIG_TEMPLATE_PATH = Path(__file__).parent / "config.example.ini"

CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"
SIGLIP_MODEL_NAME = "google/siglip-so400m-patch14-384"
BLIP_MODEL_NAME = "Salesforce/blip-image-captioning-base"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}


def to_feature_tensor(output):
    if isinstance(output, torch.Tensor):
        return output
    if hasattr(output, "pooler_output") and output.pooler_output is not None:
        return output.pooler_output
    if hasattr(output, "last_hidden_state"):
        return output.last_hidden_state.mean(dim=1)
    raise TypeError(f"Unsupported model output type: {type(output)}")


def load_categories(config_path: Path):
    if not config_path.exists():
        raise FileNotFoundError(f"Missing config file: {config_path}")

    categories = []
    in_categories = False

    with open(config_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line or line.startswith(";") or line.startswith("#"):
                continue

            if line.startswith("[") and line.endswith("]"):
                section_name = line[1:-1].strip().lower()
                in_categories = section_name == "categories"
                continue

            if not in_categories:
                continue

            if "=" not in line:
                continue

            printed_name, labels_part = line.split("=", 1)
            p = printed_name.strip()
            if not p:
                continue

            label = labels_part.strip()
            if label:
                categories.append((p, label))

    if not categories:
        raise ValueError("No categories found in [categories] section.")
    return categories


def resolve_config_path():
    if CONFIG_PATH.exists():
        return CONFIG_PATH
    if CONFIG_TEMPLATE_PATH.exists():
        shutil.copy(str(CONFIG_TEMPLATE_PATH), str(CONFIG_PATH))
        print(f"Created local config from template: {CONFIG_PATH.name}")
        return CONFIG_PATH
    raise FileNotFoundError(
        f"Missing config files: {CONFIG_PATH} and {CONFIG_TEMPLATE_PATH}"
    )


def load_settings(config_path: Path):
    if not config_path.exists():
        raise FileNotFoundError(f"Missing config file: {config_path}")

    cfg = configparser.ConfigParser(strict=False)
    cfg.optionxform = str
    cfg.read(config_path, encoding="utf-8")

    defaults = {
        "architecture": "clip",
        "mode": "console",
        "console_order": "input",
        "result_location": "input",
        "top_k": "3",
    }
    settings = defaults.copy()

    if "settings" in cfg:
        section = cfg["settings"]
        for key in defaults.keys():
            value = section.get(key, fallback=defaults[key]).strip()
            if value:
                settings[key] = value

    return settings


def parse_args():
    parser = argparse.ArgumentParser(
        description="Image sorting/listing tool. If no paths are provided, uses ./input",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Image files and/or directories to process recursively.",
    )
    return parser.parse_args()


def collect_image_entries(input_args):
    entries = []
    seen = set()

    if not input_args:
        default_root = INPUT_FOLDER
        if not default_root.exists():
            raise FileNotFoundError(f"Input folder does not exist: {default_root}")
        for p in default_root.rglob("*"):
            if p.is_file() and p.suffix.lower() in VALID_EXTS:
                rp = p.resolve()
                if rp not in seen:
                    entries.append({"image": p, "source_root": default_root})
                    seen.add(rp)
        return entries

    for raw in input_args:
        path = Path(raw)
        if not path.exists():
            raise FileNotFoundError(f"Input path does not exist: {path}")

        if path.is_file():
            if path.suffix.lower() in VALID_EXTS:
                rp = path.resolve()
                if rp not in seen:
                    entries.append({"image": path, "source_root": path.parent})
                    seen.add(rp)
            continue

        for p in path.rglob("*"):
            if p.is_file() and p.suffix.lower() in VALID_EXTS:
                rp = p.resolve()
                if rp not in seen:
                    entries.append({"image": p, "source_root": path})
                    seen.add(rp)

    return entries


def write_sidecar_txt(image_path: Path, text: str):
    output_file_path = image_path.with_suffix(".txt")
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(text)


def move_or_copy_image_to_root(image_path: Path, source_root: Path, target_root: Path, move_file: bool):
    try:
        rel_path = image_path.relative_to(source_root)
    except ValueError:
        rel_path = Path(image_path.name)
    target_path = target_root / rel_path
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if image_path.resolve() == target_path.resolve():
        return image_path

    if move_file:
        shutil.move(str(image_path), str(target_path))
    else:
        shutil.copy(str(image_path), str(target_path))
    return target_path


def route_sorted_image(image_path: Path, source_root: Path, category_name: str, result_location: str):
    category_path = category_name.replace("/", os.sep).replace("\\", os.sep)

    if result_location == "input":
        target_root = source_root / category_path
        move_file = True
    elif result_location == "copy_to_output":
        target_root = OUTPUT_FOLDER / category_path
        move_file = False
    elif result_location == "move_to_output":
        target_root = OUTPUT_FOLDER / category_path
        move_file = True
    else:
        raise ValueError("RESULT_LOCATION must be: input, copy_to_output, move_to_output")

    target_folder = target_root
    target_folder.mkdir(parents=True, exist_ok=True)
    target_path = target_folder / image_path.name

    if image_path.resolve() == target_path.resolve():
        print(f"Unchanged: {image_path.name} (already in target)")
        return

    if move_file:
        shutil.move(str(image_path), str(target_path))
        action = "Moved"
    else:
        shutil.copy(str(image_path), str(target_path))
        action = "Copied"
    print(f"{action}: {image_path.name} -> {target_folder}")


def print_console_input_order(results):
    for result in results:
        best = result["matches"][0]
        print(f"{result['image'].name} -> {best['printed']} ({best['score']:.4f})")
        for rank, match in enumerate(result["matches"], start=1):
            print(f"  {rank}. {match['printed']} | score={match['score']:.4f}")


def print_console_category_order(results):
    grouped = {}
    for result in results:
        best_category = result["matches"][0]["printed"]
        grouped.setdefault(best_category, []).append(result)

    for category in sorted(grouped.keys()):
        print(f"[{category}]")
        for result in grouped[category]:
            best = result["matches"][0]
            print(f"  {result['image'].name} ({best['score']:.4f})")


def main():
    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    config_path = resolve_config_path()
    settings = load_settings(config_path)
    categories = load_categories(config_path)
    printed_names = [c[0] for c in categories]
    vector_labels = [c[1] for c in categories]

    image_entries = collect_image_entries(args.paths)
    if not image_entries:
        print("No images found.")
        return

    architecture = settings["architecture"].lower().strip()
    mode = settings["mode"].lower().strip()
    console_order = settings["console_order"].lower().strip()
    result_location = settings["result_location"].lower().strip()
    top_k = int(settings["top_k"])

    if architecture not in {"clip", "siglip", "t5"}:
        raise ValueError("ARCHITECTURE must be one of: clip, siglip, t5")
    if mode not in {"console", "text", "sort"}:
        raise ValueError("MODE must be one of: console, text, sort")
    if console_order not in {"input", "category"}:
        raise ValueError("CONSOLE_ORDER must be one of: input, category")
    if result_location not in {"input", "copy_to_output", "move_to_output"}:
        raise ValueError("RESULT_LOCATION must be one of: input, copy_to_output, move_to_output")
    if top_k < 1:
        raise ValueError("TOP_K must be >= 1")

    model_id = (
        CLIP_MODEL_NAME if architecture == "clip"
        else SIGLIP_MODEL_NAME if architecture == "siglip"
        else BLIP_MODEL_NAME
    )
    print(f"Architecture: {architecture}")
    print(f"Model: {model_id}")
    print(f"Mode: {mode}")
    print(f"Result location: {result_location}")
    print(f"Top K: {top_k}")
    print(f"Images: {len(image_entries)}")
    print(f"Device: {device}")

    results = []

    if architecture == "clip":
        processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
        model = CLIPModel.from_pretrained(CLIP_MODEL_NAME).to(device)
        model.eval()
        model.requires_grad_(False)
        text_inputs = processor(text=vector_labels, return_tensors="pt", padding=True).to(device)

        with torch.no_grad():
            text_features = model.get_text_features(**text_inputs)
            text_features = to_feature_tensor(text_features)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        for entry in image_entries:
            image_path = entry["image"]
            input_image = Image.open(image_path).convert("RGB")
            image_inputs = processor(images=input_image, return_tensors="pt").to(device)
            with torch.no_grad():
                image_features = model.get_image_features(**image_inputs)
                image_features = to_feature_tensor(image_features)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                similarity = torch.matmul(image_features, text_features.T).squeeze(0)

            topk = similarity.topk(min(top_k, len(vector_labels)))
            matches = []
            for idx, score in zip(topk.indices.tolist(), topk.values.tolist()):
                matches.append({
                    "printed": printed_names[idx],
                    "vector": vector_labels[idx],
                    "score": float(score),
                })
            results.append({"image": image_path, "source_root": entry["source_root"], "matches": matches})

    elif architecture == "siglip":
        processor = AutoProcessor.from_pretrained(SIGLIP_MODEL_NAME)
        model = AutoModel.from_pretrained(SIGLIP_MODEL_NAME).to(device)
        model.eval()
        model.requires_grad_(False)

        for entry in image_entries:
            image_path = entry["image"]
            input_image = Image.open(image_path).convert("RGB")
            inputs = processor(
                text=vector_labels,
                images=input_image,
                padding="max_length",
                return_tensors="pt",
            ).to(device)
            with torch.no_grad():
                outputs = model(**inputs)
                probs = torch.sigmoid(outputs.logits_per_image).squeeze(0)

            topk = probs.topk(min(top_k, len(vector_labels)))
            matches = []
            for idx, score in zip(topk.indices.tolist(), topk.values.tolist()):
                matches.append({
                    "printed": printed_names[idx],
                    "vector": vector_labels[idx],
                    "score": float(score),
                })
            results.append({"image": image_path, "source_root": entry["source_root"], "matches": matches})

    elif architecture == "t5":
        processor = BlipProcessor.from_pretrained(BLIP_MODEL_NAME)
        model = BlipForConditionalGeneration.from_pretrained(BLIP_MODEL_NAME).to(device)
        model.eval()
        model.requires_grad_(False)

        sentence_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        label_embeddings = sentence_model.encode(vector_labels, convert_to_tensor=True)

        for entry in image_entries:
            image_path = entry["image"]
            input_image = Image.open(image_path).convert("RGB")
            inputs = processor(images=input_image, return_tensors="pt").to(device)
            with torch.no_grad():
                generated_ids = model.generate(**inputs, max_length=20)
                caption = processor.decode(generated_ids[0], skip_special_tokens=True)

            caption_embedding = sentence_model.encode([caption], convert_to_tensor=True)
            similarities = util.pytorch_cos_sim(caption_embedding, label_embeddings).squeeze(0)

            topk = similarities.topk(min(top_k, len(vector_labels)))
            matches = []
            for idx, score in zip(topk.indices.tolist(), topk.values.tolist()):
                matches.append({
                    "printed": printed_names[idx],
                    "vector": vector_labels[idx],
                    "score": float(score),
                })
            results.append({"image": image_path, "source_root": entry["source_root"], "matches": matches})

    if mode == "console":
        if console_order == "category":
            print_console_category_order(results)
        else:
            print_console_input_order(results)
        return

    if mode == "text":
        for result in results:
            best = result["matches"][0]["printed"]
            image_path = result["image"]
            if result_location == "copy_to_output":
                image_path = move_or_copy_image_to_root(
                    result["image"],
                    result["source_root"],
                    OUTPUT_FOLDER,
                    move_file=False,
                )
            elif result_location == "move_to_output":
                image_path = move_or_copy_image_to_root(
                    result["image"],
                    result["source_root"],
                    OUTPUT_FOLDER,
                    move_file=True,
                )
            write_sidecar_txt(image_path, best)
            print(f"Wrote txt: {image_path.with_suffix('.txt').name}")
        return

    if mode == "sort":
        for result in results:
            best = result["matches"][0]["printed"]
            route_sorted_image(result["image"], result["source_root"], best, result_location)
        return


if __name__ == "__main__":
    main()

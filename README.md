# ImageSortingCLIP

Unified image categorization script with 3 architectures:

- `clip`
- `siglip`
- `t5` (BLIP captioning + sentence embedding similarity)

## Setup

1. **Create Virtual Environment**: Create a virtual environment manually, or run the `venv_create.bat` script to automatically create a Python virtual environment.
2. **Install Dependencies**: If you didn't install the packages in the previous step, activate the environment (`venv\Scripts\activate.bat`) and run:
3. ```bash
   pip install -r requirements.txt
   ```

## Configuration

Defaults are versioned in [`config.example.ini`](./config.example.ini).

Local settings are read from `config.ini`:
- If `config.ini` exists, it is used.
- If `config.ini` is missing, the script automatically creates it from `config.example.ini` on first run.

Edit your local `config.ini`:

- `[settings]`
  
  - `architecture`: `clip | siglip | t5`
  - `mode`: `console | text | sort`
  - `console_order`: `input | category` (used only when `mode=console`)
  - `result_location`: `input | copy_to_output | move_to_output` (used when `mode=text` or `mode=sort`)
  - `top_k`: number of matches to compute/print

- `[categories]`
  
  - Left side of `=`: printed/output category name
  - Right side of `=`: one vector-search label used for matching
  - To map many labels into one category, repeat the same left-side category on multiple lines

Example:

```ini
[categories]
black_and_white_drawing = black and white drawing
```

## Usage

Run with default input folder (`./input`):

```bash
py imagesort.py
```

Run on specific directory:

```bash
py imagesort.py "C:\path\to\images"
```

Run on multiple directories/files:

```bash
py imagesort.py "C:\images\a" "C:\images\b" "C:\images\one_file.png"
```

## Modes

- `mode=console`
  
  - Prints predictions only.
  - `console_order=input`: keeps original discovered order.
  - `console_order=category`: groups output by best predicted category.

- `mode=text`
  
  - Writes `<image>.txt` with best category label.
  - `result_location=input`: write next to original image.
  - `result_location=copy_to_output`: copy image to `./output` first, then write txt there.
  - `result_location=move_to_output`: move image to `./output` first, then write txt there.

- `mode=sort`
  
  - Places image into predicted category subfolder.
  - `result_location=input`: sorts in-place under input/source root.
  - `result_location=copy_to_output`: copies into `./output/<category>/`.
  - `result_location=move_to_output`: moves into `./output/<category>/`.

## Script

Main script:

- [`imagesort.py`](./imagesort.py)

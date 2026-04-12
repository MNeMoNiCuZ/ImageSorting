# ImageSorting

`imagesort.py` classifies images against your configured categories, using one of:
- `clip`
- `siglip`
- `t5` (BLIP captioning + sentence similarity)

It can:
- print predictions (`log` mode),
- write comma-separated tags to `.txt` sidecars (`text` mode, uses `top_k`),
- sort images into category folders (`sort` mode).

## Setup

1. Create/activate your virtual environment (`venv_create.bat` is included if needed).
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Copy template config:
```bash
copy config.example.ini config.ini
```
4. Edit `config.ini`.

## Configuration

Settings come from [`config.ini`](./config.ini).

`[settings]`:
- `architecture`: `clip | siglip | t5`
- `mode`: `log | text | sort`
- `log_order`: `input | category` (used by `mode=log`)
- `result_location`: `input | output` (used by `mode=text` and `mode=sort`)
- `sort_operation`: `copy | move` (used by `mode=sort`)
- `top_k`: integer `>= 1` (used for top matches and `text` tags)

`[categories]`:
- Left side of `=` is the output/printed category name.
- Right side of `=` is the matching label.
- Repeat the same left side to map multiple labels into one category.

Current template example:
```ini
[categories]
man = man
woman = woman
environment = landscape
environment = environment
house = house
cartoon = cartoon
manga = manga
object = object
food = food
animal = animal
```

## Usage

Default input folder (`./input`):
```bash
py imagesort.py
```

Specific path(s):
```bash
py imagesort.py "C:\path\to\images"
py imagesort.py "C:\images\a" "C:\images\b" "C:\images\one_file.png"
```

## Mode behavior

`mode=log`:
- Prints matches only.
- `log_order=input`: original discovered order.
- `log_order=category`: grouped by best predicted category.

`mode=text`:
- Writes `<image>.txt` with comma-separated top tags (from `top_k`).
- `result_location=input`: writes next to source image.
- `result_location=output`: writes to mirrored path under `./output`.

`mode=sort`:
- Sorts images into category folders.
- `result_location=input`: sort under source/input root.
- `result_location=output`: sort under `./output/<category>/`.
- `sort_operation=copy`: copy file to sorted location.
- `sort_operation=move`: move file to sorted location.

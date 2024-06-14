# Introduction
The purpose of this tool is to help you quickly sort through files / datasets where an image may have multiple additional files sharing the same name (such as .txt or .caption or more).

The tool shows you an image, and you press a configured button or hotkey to move the image and all the supplementary files into a target output folder.

It's useful for categorizing and sorting files quickly and effortlessly.

![image](https://github.com/MNeMoNiCuZ/ImageSorting/assets/60541708/2a834a38-05ba-493c-b885-9f72905bae04)

https://github.com/MNeMoNiCuZ/ImageSorting/assets/60541708/d4863089-e24e-45c3-ae55-3b0e47f11b74

# Requirements
Developed on Python 3.12.

`tkinter`

`PIL` / `pillow`

# Installation
`git clone https://github.com/MNeMoNiCuZ/ImageSorting`
`pip install pillow`

# Usage Instructions
- Double-click to launch `main.py` or run `py main.py` from CLI
- Go to the `Setup` menu and pick: `Select Image Folder` from the menu
- Browse to where you have your images
  - It will automatically include images in subfolders recursively
- Go to the `Setup` menu and pick: `Add Category` from the menu
  - Choose a name for your button/category
  - Browse to where you want to move files matching this category
  - Optional: Add a single-button hotkey (letters and numbers) to this action
- Repeat until you have all categories you need
- Go to the `File` menu and pick: `Save Project As` from the menu to save your project
> [!IMPORTANT]
> Restart the program after adding or editing your categories. There's a bug where the hotkeys don't load until you restart.

- Click buttons, sort images, profit!


# Known Issues
- [ ]   There is no undo functionality.
- [ ]   Does not actively rescale GUI. Only refreshes when you sort an image.
- [ ]   The hotkey for newly added or edited categories does not work until you restart.
- [ ]   Support hotkeys better, including special keys.
- [ ]   Capitalize hotkeys in UI.
- [ ]   Make buttons activate when you use a hotkey.

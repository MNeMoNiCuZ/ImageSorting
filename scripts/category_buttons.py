# category_buttons.py
import tkinter as tk
import shutil
import os
from tkinter import messagebox
from .logger import log_error, log_info
from .image_display import display_images as show_images

# Define the number of buttons per row
BUTTONS_PER_ROW = 6  # You can adjust this number as needed

def setup_category_buttons(buttons_frame, config, button_bg_color, button_fg_color, image_frame, thumbnails_frame):
    for widget in buttons_frame.winfo_children():
        widget.destroy()

    buttons_container = tk.Frame(buttons_frame, bg=buttons_frame.cget("bg"))
    buttons_container.pack(expand=True)

    row_frame = None
    for index, category in enumerate(config.get("categories", [])):
        if index % BUTTONS_PER_ROW == 0:
            row_frame = tk.Frame(buttons_container, bg=buttons_frame.cget("bg"))
            row_frame.pack(fill=tk.X)
        add_sorting_button(row_frame, category["name"], category["path"], category.get("hotkey"), button_bg_color, button_fg_color, config, image_frame, thumbnails_frame)

def add_sorting_button(frame, category_name, category_path, hotkey=None, bg_color=None, fg_color=None, config=None, image_frame=None, thumbnails_frame=None):
    button = tk.Button(frame, text=f"{category_name} ({hotkey if hotkey else ''})", command=lambda: sort_files(category_path, config, image_frame, thumbnails_frame),
                       bg=bg_color, fg=fg_color, font=("Helvetica", 16), padx=5, pady=10, width=20)
    button.pack(side=tk.LEFT, padx=5, pady=5)

def sort_files(destination_path, config, image_frame, thumbnails_frame):
    current_image_path = config.get('current_image_path')
    current_image_index = config.get('current_image_index', 0)
    print(f"Button pressed for {destination_path}")
    if current_image_path:
        print(f"Current image path: {current_image_path}")
        move_files(current_image_path, destination_path)
        config['current_image_index'] += 1
        if config['current_image_index'] < len(config.get('images', [])):
            update_display(config, image_frame, thumbnails_frame)
        else:
            messagebox.showinfo("Sorting Complete", "All files have been sorted.")
            clear_display(image_frame, thumbnails_frame)
    else:
        print("No current image path set.")

def move_files(image_path, destination_path):
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    try:
        shutil.move(image_path, destination_path)
        supplementary_files = get_supplementary_files(image_path)
        for file in supplementary_files:
            shutil.move(file, destination_path)
        log_info(f"Moved {image_path} to {destination_path}")
    except Exception as e:
        log_error(f"Error moving files: {e}")

def get_supplementary_files(image_path):
    folder = os.path.dirname(image_path)
    name, _ = os.path.splitext(os.path.basename(image_path))
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.startswith(name) and not f.endswith(('jpg', 'jpeg', 'png', 'webp', 'gif'))]

def update_display(config, image_frame, thumbnails_frame):
    images = config.get("images", [])
    current_image_index = config.get('current_image_index', 0)
    if current_image_index < len(images):
        config['current_image_path'] = images[current_image_index]
        display_images(config, image_frame, thumbnails_frame)
    else:
        config['current_image_path'] = ""
        print("No more images to display.")

def display_images(config, image_frame, thumbnails_frame):
    remaining_images = config.get('images', [])[config.get('current_image_index', 0):]
    show_images(image_frame, thumbnails_frame, remaining_images)

def clear_display(image_frame, thumbnails_frame):
    for widget in image_frame.winfo_children():
        widget.destroy()
    for widget in thumbnails_frame.winfo_children():
        widget.destroy()

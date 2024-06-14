# file_operations.py
import tkinter as tk
from tkinter import filedialog, messagebox
from .image_display import display_images
from .file_manager import validate_folder
from .logger import log_error, log_info
from .config_manager import load_config_file, save_config_file
from .category_buttons import setup_category_buttons
from .ui_refresh import refresh_ui
from .hotkey_utils import bind_hotkeys

def select_folder(root, image_frame, thumbnails_frame, console_frame, config):
    folder_path = filedialog.askdirectory()
    if folder_path:
        images, duplicates = validate_folder(folder_path)
        if duplicates:
            show_duplicates_warning(root, duplicates)
            log_error(f"Duplicate image names found: {duplicates}")
            update_console(console_frame, f"Duplicate image names found:\n" + "\n".join(duplicates))
        else:
            config['images'] = images
            display_images(image_frame, thumbnails_frame, images)
            config['chosen_folder'] = folder_path
            log_info(f"Folder {folder_path} selected and validated successfully.")
            config['current_image_index'] = 0
            config['current_image_path'] = images[0] if images else ""

def show_duplicates_warning(root, duplicates):
    duplicates_message = "Duplicate image names found:\n" + "\n".join(duplicates)
    messagebox.showwarning("Duplicates Found", duplicates_message)

def load_project(root, image_frame, thumbnails_frame, buttons_frame, console_frame, config):
    file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        reload_configuration(root, image_frame, thumbnails_frame, buttons_frame, console_frame, config, file_path)

def reload_configuration(root, image_frame, thumbnails_frame, buttons_frame, console_frame, config, file_path):
    new_config = load_config_file(file_path)
    config.clear()
    config.update(new_config)
    for widget in buttons_frame.winfo_children():
        widget.destroy()
    setup_category_buttons(buttons_frame, config, "#444444", "#ffffff", image_frame, thumbnails_frame)
    if 'chosen_folder' in config:
        images, duplicates = validate_folder(config['chosen_folder'])
        if not duplicates:
            config['images'] = images
            display_images(image_frame, thumbnails_frame, images)
            config['current_image_index'] = 0
            config['current_image_path'] = images[0] if images else ""
    refresh_ui(config, image_frame, thumbnails_frame, buttons_frame, console_frame if console_frame else buttons_frame)
    
    # Bind hotkeys after loading the configuration
    bind_hotkeys(root, config, image_frame, thumbnails_frame)

def save_project_as(config):
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        relevant_config = {key: config[key] for key in ['categories', 'chosen_folder'] if key in config}
        save_config_file(relevant_config, file_path)

def update_console(console_frame, message):
    for widget in console_frame.winfo_children():
        widget.destroy()
    console_label = tk.Label(console_frame, text=message, fg="white", bg="black", anchor="w")
    console_label.pack(fill=tk.BOTH)

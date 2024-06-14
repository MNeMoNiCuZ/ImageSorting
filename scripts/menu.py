# menu.py
import tkinter as tk
from .file_operations import load_project, save_project_as
from .category_management import add_category, edit_categories
from .file_operations import select_folder

def setup_menu(root, config, image_frame, thumbnails_frame, buttons_frame, console_frame, menu_color):
    menu_bar = tk.Menu(root, bg=menu_color, fg="#ffffff")
    root.config(menu=menu_bar)

    file_menu = tk.Menu(menu_bar, tearoff=0, bg=menu_color, fg="#ffffff")
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Load Project", command=lambda: load_project(root, image_frame, thumbnails_frame, buttons_frame, console_frame, config))
    file_menu.add_command(label="Save Project As", command=lambda: save_project_as(config))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)

    setup_menu = tk.Menu(menu_bar, tearoff=0, bg=menu_color, fg="#ffffff")
    menu_bar.add_cascade(label="Setup", menu=setup_menu)
    setup_menu.add_command(label="Select Image Folder", command=lambda: select_folder(root, image_frame, thumbnails_frame, console_frame, config))
    setup_menu.add_command(label="Add Category", command=lambda: add_category(buttons_frame, config, "#444444", "#ffffff", image_frame, thumbnails_frame))
    setup_menu.add_command(label="Edit Categories", command=lambda: edit_categories(buttons_frame, config, "#444444", "#ffffff", image_frame, thumbnails_frame))

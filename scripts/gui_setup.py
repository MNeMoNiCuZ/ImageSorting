# gui_setup.py
import tkinter as tk
from .menu import setup_menu
from .category_buttons import setup_category_buttons, sort_files  # Import sort_files
from .logger import setup_logger, log_info
from .hotkey_utils import bind_hotkeys  # Import from hotkey_utils

def setup_gui(root, config):
    setup_logger()  # Initialize logging

    # Define colors for the GUI
    bg_color = "#2e2e2e"  # Main background color
    button_bg_color = "#444444"
    button_fg_color = "#ffffff"

    root.configure(bg=bg_color)
    
    # Main frame that holds all other frames
    main_frame = tk.Frame(root, bg=bg_color, bd=0)  # Remove border
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Thumbnails frame on the left side
    thumbnails_frame = tk.Frame(main_frame, bg=bg_color, width=200, bd=0)  # Consistent background color, no border
    thumbnails_frame.grid(row=0, column=0, rowspan=2, sticky="ns")

    # Canvas for the thumbnails (without scrollbar)
    canvas = tk.Canvas(thumbnails_frame, bg=bg_color, width=200, bd=0, highlightthickness=0)  # Consistent background color, no border
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Frame inside the canvas for thumbnails
    scrollable_frame = tk.Frame(canvas, bg=bg_color, bd=0)  # Consistent background color, no border
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    # Create a window inside the canvas
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Frame for displaying the main image
    image_frame = tk.Frame(main_frame, bg=bg_color, bd=0)  # No border
    image_frame.grid(row=0, column=1, sticky="nsew")

    # Frame for category buttons
    buttons_frame = tk.Frame(main_frame, bg=bg_color, bd=0)  # No border
    buttons_frame.grid(row=1, column=1, sticky="ew")

    # Frame for console output (extra details)
    console_frame = tk.Frame(main_frame, bg=bg_color, bd=0)  # No border
    console_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

    # Configure the grid layout
    main_frame.grid_rowconfigure(0, weight=3)  # Image frame gets most space
    main_frame.grid_rowconfigure(1, weight=1)  # Buttons frame gets less space
    main_frame.grid_rowconfigure(2, weight=0)  # Console frame gets the least space
    main_frame.grid_columnconfigure(1, weight=1)  # Main content column gets all available space

    # Set up the menu
    setup_menu(root, config, image_frame, scrollable_frame, buttons_frame, console_frame, bg_color)
    
    # Set up category buttons
    setup_category_buttons(buttons_frame, config, button_bg_color, button_fg_color, image_frame, scrollable_frame)
    
    # Print debug message before binding hotkeys
    print("About to bind hotkeys...")

    # Bind hotkeys
    bind_hotkeys(root, config, image_frame, scrollable_frame)

    # Print debug message after binding hotkeys
    print("Hotkeys binding complete")

def handle_hotkey_press(event, path, config, image_frame, thumbnails_frame):
    print(f"Hotkey '{event.keysym}' pressed for path '{path}'")
    sort_files(path, config, image_frame, thumbnails_frame)

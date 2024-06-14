import tkinter as tk
from .category_buttons import update_display  # Ensure this import is correct

def refresh_ui(config, image_frame, thumbnails_frame, buttons_frame, console_frame):
    print("Refreshing UI...")  # Debug statement
    print(f"Config during refresh: {config}")  # Debug statement

    if 'current_image_path' in config:
        update_display(config, image_frame, thumbnails_frame)
        update_console(console_frame, f"Refreshed UI with current image: {config['current_image_path']}")
    else:
        update_console(console_frame, "No image currently loaded")
        print("No image currently loaded")  # Debug statement

def update_console(console_frame, message):
    for widget in console_frame.winfo_children():
        widget.destroy()
    console_label = tk.Label(console_frame, text=message, fg="white", bg="black", anchor="w")
    console_label.pack(fill=tk.BOTH)

# image_display.py
from PIL import Image, ImageTk
import tkinter as tk
import os

def format_size(size):
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

def display_images(image_frame, thumbnails_frame, images):
    if not images:
        return

    current_image_path = images[0]
    image = Image.open(current_image_path)
    image.thumbnail((image_frame.winfo_width(), image_frame.winfo_height()), Image.LANCZOS)  # Use LANCZOS for high-quality downsampling
    photo = ImageTk.PhotoImage(image)

    for widget in image_frame.winfo_children():
        widget.destroy()

    file_info = get_file_info(current_image_path)
    info_label = tk.Label(image_frame, text=file_info, bg="#2e2e2e", fg="white", anchor="center")
    info_label.pack(fill=tk.X)

    image_label = tk.Label(image_frame, image=photo, bg="#2e2e2e")
    image_label.image = photo
    image_label.pack(expand=True)

    for widget in thumbnails_frame.winfo_children():
        widget.destroy()

    # Only load the next 10 images
    next_images = images[:10]

    for thumb_path in next_images:
        thumb_image = Image.open(thumb_path)
        thumb_image.thumbnail((300, 300), Image.LANCZOS)
        thumb_photo = ImageTk.PhotoImage(thumb_image)
        thumb_label = tk.Label(thumbnails_frame, image=thumb_photo, bg="#2e2e2e", width=200, anchor="center", bd=0, highlightthickness=0)  # Consistent background color, no border
        thumb_label.image = thumb_photo
        thumb_label.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

def get_file_info(image_path):
    file_size = os.path.getsize(image_path)
    readable_size = format_size(file_size)
    image = Image.open(image_path)
    width, height = image.size
    supplementary_files = get_supplementary_files(image_path)
    supplementary_extensions = [os.path.splitext(file)[1][1:] for file in supplementary_files]  # Remove leading dot
    
    file_name = os.path.basename(image_path)
    info = f"{file_name}|{'|'.join(supplementary_extensions)} - {width}x{height}px, {readable_size}"
    
    return info


def get_supplementary_files(image_path):
    folder = os.path.dirname(image_path)
    name, _ = os.path.splitext(os.path.basename(image_path))
    return [f for f in os.listdir(folder) if f.startswith(name) and not f.endswith(('jpg', 'jpeg', 'png', 'webp', 'gif'))]

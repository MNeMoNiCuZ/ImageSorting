# category_management.py
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
from .config_manager import save_config_file
from .category_buttons import setup_category_buttons, add_sorting_button
from .hotkey_utils import bind_hotkeys

VALID_HOTKEYS = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")

def add_category(buttons_frame, config, bg_color, fg_color, image_frame=None, thumbnails_frame=None):
    name = simpledialog.askstring("Category Name", "Enter the name of the category:")
    path = filedialog.askdirectory(title="Select Folder for Category")
    if name and path:
        while True:
            hotkey = simpledialog.askstring("Hotkey", "Enter the hotkey for this category (optional):")
            if not hotkey or (hotkey and hotkey in VALID_HOTKEYS):
                break
            else:
                messagebox.showerror("Invalid Hotkey", "Please enter a valid single character hotkey (a-z, A-Z, 0-9).")
        
        category = {"name": name, "path": path, "hotkey": hotkey}
        if "categories" not in config:
            config["categories"] = []
        config["categories"].append(category)
        
        # Refresh the category buttons and re-bind hotkeys
        setup_category_buttons(buttons_frame, config, bg_color, fg_color, image_frame, thumbnails_frame)
        bind_hotkeys(buttons_frame.master, config, image_frame, thumbnails_frame)
        print("Successfully added and bound new category")

def edit_categories(buttons_frame, config, bg_color, fg_color, image_frame=None, thumbnails_frame=None):
    for widget in buttons_frame.winfo_children():
        widget.destroy()

    categories = config.get("categories", [])
    for category in categories:
        add_sorting_button(buttons_frame, category["name"], category["path"], category.get("hotkey"), bg_color, fg_color, config, image_frame, thumbnails_frame)

    edit_window = tk.Toplevel()
    edit_window.title("Edit Categories")
    edit_window.configure(bg="#2e2e2e")
    edit_window.geometry("600x400")

    listbox = tk.Listbox(edit_window, bg="#2e2e2e", fg="white")
    listbox.pack(fill=tk.BOTH, expand=True)

    for i, category in enumerate(categories):
        hotkey_display = f" [{category.get('hotkey')}]" if category.get('hotkey') else ""
        listbox.insert(tk.END, f"{category['name']} ({category['path']}){hotkey_display}")

    def delete_category():
        selected = listbox.curselection()
        if selected:
            index = selected[0]
            del categories[index]
            edit_window.destroy()
            edit_categories(buttons_frame, config, bg_color, fg_color, image_frame, thumbnails_frame)
            print("Successfully deleted category and reloaded UI")

    def edit_category():
        selected = listbox.curselection()
        if selected:
            index = selected[0]
            category = categories[index]
            new_name = simpledialog.askstring("Edit Category Name", "Enter the new name for the category:", initialvalue=category["name"])
            new_path = filedialog.askdirectory(title="Select New Folder for Category", initialdir=category["path"])
            if new_name and new_path:
                while True:
                    new_hotkey = simpledialog.askstring("Edit Hotkey", "Enter the new hotkey for this category (optional):", initialvalue=category.get("hotkey", ""))
                    if not new_hotkey or (new_hotkey and new_hotkey in VALID_HOTKEYS):
                        break
                    else:
                        messagebox.showerror("Invalid Hotkey", "Please enter a valid single character hotkey (a-z, A-Z, 0-9).")
                categories[index] = {"name": new_name, "path": new_path, "hotkey": new_hotkey}
                edit_window.destroy()
                edit_categories(buttons_frame, config, bg_color, fg_color, image_frame, thumbnails_frame)
                bind_hotkeys(buttons_frame.master, config, image_frame, thumbnails_frame)  # Rebind hotkeys
                print("Successfully edited category and reloaded UI")

    btn_frame = tk.Frame(edit_window, bg="#2e2e2e")
    btn_frame.pack(fill=tk.X)
    delete_button = tk.Button(btn_frame, text="Delete", command=delete_category, bg="#444444", fg="white")
    delete_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
    edit_button = tk.Button(btn_frame, text="Edit", command=edit_category, bg="#444444", fg="white")
    edit_button.pack(side=tk.RIGHT, fill=tk.X, expand=True)

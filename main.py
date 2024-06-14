# main.py
import tkinter as tk
from scripts.gui_setup import setup_gui

def main():
    root = tk.Tk()
    root.title("Image Sorting Tool")
    root.geometry("1200x800")
    config = {}  # Initialize config dictionary here
    setup_gui(root, config)
    root.mainloop()

if __name__ == "__main__":
    main()

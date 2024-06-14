# hotkey_utils.py

from .category_buttons import sort_files

def bind_hotkeys(root, config, image_frame, thumbnails_frame):
    print("Executing bind_hotkeys...")
    for category in config.get("categories", []):
        hotkey = category.get("hotkey")
        if hotkey:
            try:
                # Use default arguments in lambda to capture the current values
                print(f"Binding hotkey '{hotkey}' for category '{category['name']}'")
                root.bind(f"<KeyPress-{hotkey}>", lambda event, path=category["path"], cfg=config, img_frame=image_frame, thumb_frame=thumbnails_frame: sort_files(path, cfg, img_frame, thumb_frame))
                print(f"Successfully bound hotkey '{hotkey}' for category '{category['name']}'")
            except Exception as e:
                print(f"Failed to bind hotkey '{hotkey}' for category '{category['name']}': {e}")

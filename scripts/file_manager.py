import os

def scan_folder(folder_path):
    images = []
    duplicates = []
    file_dict = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                name, ext = os.path.splitext(file)
                if name in file_dict:
                    duplicates.append(os.path.join(root, file))
                else:
                    file_dict[name] = os.path.join(root, file)
    images = list(file_dict.values())
    return images, duplicates

def validate_folder(folder_path):
    images, duplicates = scan_folder(folder_path)
    if duplicates:
        print(f"Duplicate image names found: {duplicates}")
    return images, duplicates

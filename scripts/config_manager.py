import json
import os

def load_config_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

def save_config_file(config, file_path):
    with open(file_path, 'w') as file:
        json.dump(config, file, indent=4)

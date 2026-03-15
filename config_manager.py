import json
import os

DEFAULT_CONFIG = {
    "window_x": 100,
    "window_y": 100,
    "window_width": 400,
    "window_height": 150,
    "current_step": 0,
    "client_txt_path": "",
    "theme": "Exile Dark",
    "opacity": 0.85,
    "compact_mode": False,
    "base_font_size": 13
}

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # Ensure all default keys exist
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

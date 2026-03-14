import json
import os

CHARACTERS_FILE = os.path.join(os.path.dirname(__file__), "characters.json")

DEFAULT_CHARACTER_CONFIG = {
    "current_step": 0,
    "completed_data": {},
    "highwater_mark": 0,
    "opacity": 0.85,
    "base_font_size": 9,
    "window_x": 100,
    "window_y": 100,
    "window_width": 400,
}


def _default_data():
    return {
        "active": "Default",
        "characters": {
            "Default": DEFAULT_CHARACTER_CONFIG.copy()
        }
    }


def load_characters():
    if os.path.exists(CHARACTERS_FILE):
        try:
            with open(CHARACTERS_FILE, "r") as f:
                data = json.load(f)
            if not isinstance(data.get("characters"), dict) or not data["characters"]:
                return _default_data()
            active = data.get("active")
            if active not in data["characters"]:
                data["active"] = next(iter(data["characters"]))
            for name, cfg in data["characters"].items():
                for key, val in DEFAULT_CHARACTER_CONFIG.items():
                    if key not in cfg:
                        cfg[key] = val
            return data
        except Exception:
            pass
    return _default_data()


def save_characters(data):
    with open(CHARACTERS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_active_character(data):
    return data.get("active", "Default")


def get_character_config(data, name):
    chars = data.get("characters", {})
    return chars.get(name, DEFAULT_CHARACTER_CONFIG.copy())


def set_active_character(data, name):
    if name in data.get("characters", {}):
        data["active"] = name


def add_character(data, name):
    if "characters" not in data:
        data["characters"] = {}
    if name not in data["characters"]:
        data["characters"][name] = DEFAULT_CHARACTER_CONFIG.copy()


def delete_character(data, name):
    chars = data.get("characters", {})
    if name not in chars or len(chars) <= 1:
        return
    del chars[name]
    if data.get("active") == name:
        data["active"] = next(iter(chars))

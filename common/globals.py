import json
import ast
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT_DIR / "common"
CONFIG_FILE = CONFIG_DIR / "config.json"

class Config:

    def get_config(key:str) -> str | None:
        if not CONFIG_FILE.is_file():
            return "Config file does not exist."
        try:
            with open(CONFIG_FILE, "r") as f:
                config_data = json.load(f)
            if key in config_data:
                return config_data[key]
        except Exception as e:
            return f"Error: {e}"
        return

    def set_config(key:str, value:str) -> str | None:
        if not CONFIG_FILE.is_file():
            return "Config file does not exist."
        try:
            parsed_value = ast.literal_eval(value)
        except ValueError as e:
            return f"ValueError: {e}"
        try:
            with open(CONFIG_FILE, "r") as f:
                config_data = json.load(f)
            config_data[key] = parsed_value
            with open(CONFIG_FILE, "w") as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            return f"Error: {e}"
        return

    def delete_config(key:str) -> str | None:
        if not CONFIG_FILE.is_file():
            return "Config file does not exist."
        try:
            with open(CONFIG_FILE, "r") as f:
                config_data = json.load(f)
            deleted_value = config_data.pop(key, None)
            if not deleted_value:
                return f"Key {key} not found."
            with open(CONFIG_FILE, "w") as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            return f"Error: {e}"
        return
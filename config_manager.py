import json
import shutil
from pathlib import Path
import sys

class ConfigManager:
    def __init__(self, config_file_path, names_file_path):
        self.CONFIG_FILE = config_file_path
        self.NAMES_FILE = names_file_path
        self.settings = {}
        self.names = {}
        self.output_mappings = {}
        self.migrate_configs()
        self.load_settings()
        self.load_names()

    def migrate_configs(self):
        old_config_file = "config.json"
        old_names_file = "names.json"
        if Path(old_config_file).exists():
            shutil.move(old_config_file, self.CONFIG_FILE)
        if Path(old_names_file).exists():
            shutil.move(old_names_file, self.NAMES_FILE)

    def load_settings(self):
        try:
            with open(self.CONFIG_FILE, "r") as f:
                self.settings = json.load(f)
            if "ip" not in self.settings or "port" not in self.settings:
                raise KeyError("Missing 'ip' or 'port' in settings")
            if "theme" not in self.settings:
                self.settings["theme"] = "dark"
            if "confirm_before_switch" not in self.settings:
                self.settings["confirm_before_switch"] = False
            if "output_mappings" not in self.settings:
                self.settings["output_mappings"] = {}
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = {"ip": "192.168.1.230", "port": 20107, "theme": "dark", "confirm_before_switch": False, "output_mappings": {}}
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        self.output_mappings = {int(k): v for k, v in self.settings["output_mappings"].items()}

    def save_settings(self, ip, port, confirm_before_switch, output_mappings, theme=None):
        self.settings["ip"] = ip
        self.settings["port"] = port
        self.settings["confirm_before_switch"] = confirm_before_switch
        self.settings["output_mappings"] = output_mappings
        if theme:
            self.settings["theme"] = theme
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)
        self.output_mappings = {int(k): v for k, v in self.settings["output_mappings"].items()}

    def load_names(self):
        try:
            with open(self.NAMES_FILE, "r") as f:
                self.names = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.names = {
                "presets": {"default": {"inputs": {}, "outputs": {}}},
                "current_preset": "default",
            }

    def save_names(self):
        with open(self.NAMES_FILE, "w") as f:
            json.dump(self.names, f, indent=4)

    def get_theme_stylesheet(self, theme_name):
        if theme_name == "dark":
            if getattr(sys, 'frozen', False):
                stylesheet_path = Path(sys._MEIPASS) / "styles" / "dark_theme.qss"
            else:
                stylesheet_path = Path("styles/dark_theme.qss")
            try:
                with open(stylesheet_path, "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                print(f"Warning: Stylesheet not found at {stylesheet_path}")
                return ""
        return "" # Clear stylesheet for default/light theme

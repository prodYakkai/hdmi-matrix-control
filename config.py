import os
import sys
from pathlib import Path

APP_NAME = "hdmi-matrix-ctrl"

def get_config_dir():
    """Returns the platform-specific user config directory."""
    if sys.platform == "win32":
        return Path(os.environ["APPDATA"]) / APP_NAME
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    else:  # Linux and other UNIX-like systems
        return Path.home() / ".config" / APP_NAME

CONFIG_DIR = get_config_dir()
CONFIG_FILE = CONFIG_DIR / "config.json"
NAMES_FILE = CONFIG_DIR / "names.json"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)

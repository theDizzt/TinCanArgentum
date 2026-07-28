from pathlib import Path


# This module lives beside main.py, so its parent is the application root.
PROJECT_ROOT = Path(__file__).resolve().parent
MAIN_FILE = PROJECT_ROOT / "main.py"
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
FONT_DIR = PROJECT_ROOT / "font"
LOCALES_DIR = PROJECT_ROOT / "locales"
RANKCARD_DIR = CONFIG_DIR / "rankcard"

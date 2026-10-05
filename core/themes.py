# core/themes.py
import os, json, glob, sys
from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import QApplication

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEMES_DIR = os.path.join(ROOT, "themes")
CONFIG = os.path.join(ROOT, "config.json")


def list_themes():
    """{'acid': 'Acid', 'nord': 'Nord', ...}"""
    os.makedirs(THEMES_DIR, exist_ok=True)
    out = {}
    for p in glob.glob(os.path.join(THEMES_DIR, "*.json")):
        key = os.path.basename(p)[:-5]
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            out[key] = data.get("name", key)
        except Exception:
            out[key] = key
    return out


def current_theme():
    if not os.path.exists(CONFIG):
        return "acid"
    try:
        with open(CONFIG, "r", encoding="utf-8") as f:
            return json.load(f).get("theme", "acid")
    except Exception:
        return "acid"


def set_theme(key):
    """Меняет тему и перезапускает приложение."""
    data = {}
    if os.path.exists(CONFIG):
        try:
            with open(CONFIG, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    data["theme"] = key
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # перезапуск
    QProcess.startDetached(sys.executable, sys.argv)
    QApplication.instance().quit()
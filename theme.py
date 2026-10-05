# theme.py
import json, os

_here = os.path.dirname(os.path.abspath(__file__))
_cfg_path = os.path.join(_here, "config.json")
_themes_dir = os.path.join(_here, "themes")

DEFAULTS = {
    "ACCENT": "#C6FF4A", "CARD": "#111112", "BG": "#0B0B0C",
    "PANEL": "#0E0E10", "DIM": "#4A4A4A", "TEXT": "#E8E8E8",
    "SUB": "#8A8A8A", "LINE": "#1C1C1E",
}

# какой файл темы сейчас выбран
current_theme = "acid"

if os.path.exists(_cfg_path):
    try:
        with open(_cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        current_theme = cfg.get("theme", "acid")
    except Exception:
        pass

# загружаем саму тему
_theme_file = os.path.join(_themes_dir, current_theme + ".json")
if os.path.exists(_theme_file):
    try:
        with open(_theme_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k in DEFAULTS:
            if k in data:
                DEFAULTS[k] = data[k]
    except Exception:
        pass

ACCENT = DEFAULTS["ACCENT"]
CARD   = DEFAULTS["CARD"]
BG     = DEFAULTS["BG"]
PANEL  = DEFAULTS["PANEL"]
DIM    = DEFAULTS["DIM"]
TEXT   = DEFAULTS["TEXT"]
SUB    = DEFAULTS["SUB"]
LINE   = DEFAULTS["LINE"]

FONT_UI   = "Segoe UI"
FONT_MONO = "Consolas"


def card_style(radius=20):
    return f"QFrame {{ background:{CARD}; border:none; border-radius:{radius}px; }}"


def panel_style(radius=12):
    return f"QFrame {{ background:{PANEL}; border:none; border-radius:{radius}px; }}"


def input_style(size=17):
    return f"""
        QLineEdit {{
            background:transparent; border:none; outline:none;
            color:{TEXT}; font: 500 {size}pt '{FONT_UI}';
            padding: 10px 26px 18px 26px;
            selection-background-color: {ACCENT};
            selection-color: #0B0B0C;
        }}
        QLineEdit:focus {{ border:none; outline:none; }}
    """
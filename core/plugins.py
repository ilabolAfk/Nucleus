# core/plugins.py
import os, importlib.util, traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS_DIR = os.path.join(ROOT, "plugins")


class PluginAPI:
    def __init__(self):
        self.loaded = []

    def action(self, prefix, title, icon, subtitle=""):
        from registry import action
        return action(prefix, title, icon, subtitle)

    def notify(self, title, text):
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            for w in app.topLevelWidgets():
                if hasattr(w, "tray"):
                    w.tray.showMessage(title, text)
                    return
        except Exception:
            pass


def load_plugins():
    os.makedirs(PLUGINS_DIR, exist_ok=True)
    api = PluginAPI()
    for fn in sorted(os.listdir(PLUGINS_DIR)):
        if not fn.endswith(".py") or fn.startswith("_"):
            continue
        path = os.path.join(PLUGINS_DIR, fn)
        try:
            spec = importlib.util.spec_from_file_location(fn[:-3], path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "register"):
                mod.register(api)
                api.loaded.append(fn)
                print(f"[plugin] загружен: {fn}")
        except Exception as e:
            print(f"[plugin] ОШИБКА в {fn}: {e}")
            traceback.print_exc()
    return api.loaded
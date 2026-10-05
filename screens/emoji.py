# screens/emoji.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QLabel, QApplication, QListView, QListWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
import qtawesome as qta
from theme import ACCENT, TEXT, SUB, DIM, PANEL, LINE, FONT_UI

try:
    import emoji as _emoji_mod
    HAS_EMOJI = True
except ImportError:
    HAS_EMOJI = False


# словарь-фолбэк, если пакет emoji не установлен
FALLBACK = {
    "лица": ["😀","😃","😄","😁","😆","😅","😂","🤣","😊","😇","🙂","🙃",
             "😉","😌","😍","🥰","😘","😗","😙","😚","😋","😛","😝","🤪",
             "🤨","🧐","🤓","😎","🥳","😏","😒","😞","😔","😟","😕","🙁",
             "☹️","😣","😖","😫","😩","🥺","😢","😭","😤","😠","😡","🤬"],
    "жесты": ["👍","👎","👌","✌️","🤞","🤟","🤘","👏","🙌","🙏","💪","👋",
              "🤙","👈","👉","👆","👇","☝️","✋","🤚","🖐","🖖","👊","✊"],
    "животные": ["🐶","🐱","🐭","🐹","🐰","🦊","🐻","🐼","🐨","🐯","🦁","🐮",
                 "🐷","🐸","🐵","🐔","🐧","🐦","🐤","🦆","🦅","🦉","🦇","🐺"],
    "еда": ["🍏","🍎","🍐","🍊","🍋","🍌","🍉","🍇","🍓","🍒","🍑","🍍",
            "🥝","🍅","🥑","🍔","🍟","🍕","🌭","🥪","🌮","🌯","🍜","🍣"],
    "символы": ["❤️","🧡","💛","💚","💙","💜","🖤","🤍","💔","❣️","💕","💞",
                "✨","⭐","🌟","💫","⚡","🔥","💥","💯","✅","❌","⚠️","ℹ️"],
}
CATEGORIES = list(FALLBACK.keys())


class EmojiScreen(QWidget):
    def __init__(self, back_cb):
        super().__init__()
        self.back_cb = back_cb
        root = QHBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        # левая колонка — категории
        self.cats = QListWidget()
        self.cats.setFixedWidth(140)
        self.cats.setStyleSheet(f"""
            QListWidget {{ background:transparent; border:none; outline:none;
                color:{SUB}; font: 11pt '{FONT_UI}'; }}
            QListWidget::item {{ padding:9px 12px; border-radius:8px; }}
            QListWidget::item:selected {{ background:{PANEL}; color:{ACCENT}; }}
        """)
        for c in CATEGORIES:
            self.cats.addItem(QListWidgetItem(
                qta.icon("fa5s.tag", color=SUB), c))
        self.cats.currentRowChanged.connect(self._render)
        root.addWidget(self.cats)

        # правая — поиск + сетка
        right = QVBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("поиск: fire, огонь, dog…")
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background:{PANEL}; color:{TEXT}; border:none;
                border-radius:10px; padding:10px 14px;
                font: 11pt '{FONT_UI}';
            }}
        """)
        self.search.textChanged.connect(self._search)
        right.addWidget(self.search)

        self.hint = QLabel("клик — в буфер обмена")
        self.hint.setStyleSheet(f"color:{DIM}; font: 9pt '{FONT_UI}';")
        right.addWidget(self.hint)

        self.grid = QListWidget()
        self.grid.setViewMode(QListView.ViewMode.IconMode)
        self.grid.setResizeMode(QListView.ResizeMode.Adjust)
        self.grid.setIconSize(QSize(0, 0))
        self.grid.setGridSize(QSize(52, 52))
        self.grid.setSpacing(4)
        self.grid.setMovement(QListView.Movement.Static)
        self.grid.setStyleSheet(f"""
            QListWidget {{ background:transparent; border:none; outline:none; }}
            QListWidget::item {{ border-radius:10px; color:{TEXT}; }}
            QListWidget::item:selected {{ background:{PANEL}; }}
            QListWidget::item:hover {{ background:{PANEL}; }}
        """)
        self.grid.itemClicked.connect(self._copy)
        right.addWidget(self.grid, 1)

        wrap = QWidget()
        wrap.setLayout(right)
        root.addWidget(wrap, 1)

        self._render(0)

    def _render(self, idx):
        if idx < 0:
            return
        cat = CATEGORIES[idx]
        items = FALLBACK.get(cat, [])
        self._fill(items)

    def _search(self, q):
        q = q.strip().lower()
        if not q:
            self._render(max(self.cats.currentRow(), 0))
            return
        pool = []
        for lst in FALLBACK.values():
            pool.extend(lst)
        # фильтр по имени через пакет emoji, если есть
        if HAS_EMOJI:
            try:
                hits = []
                for e, data in _emoji_mod.EMOJI_DATA.items():
                    names = data.get("en", "") + " " + data.get("ru", "")
                    if q in names.lower():
                        hits.append(e)
                if hits:
                    pool = hits
            except Exception:
                pass
        self._fill(pool)

    def _fill(self, items):
        self.grid.clear()
        for e in items:
            it = QListWidgetItem(e)
            it.setFont(QFont("Segoe UI Emoji", 20))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addItem(it)

    def _copy(self, item):
        QApplication.clipboard().setText(item.text())
        self.hint.setText(f"скопировано: {item.text()}")
# screens/tutorial.py
import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
import qtawesome as qta
from theme import ACCENT, TEXT, SUB, DIM, PANEL, LINE, FONT_UI, FONT_MONO

DB = "nucleus.db"
META_KEY = "tutorial_done"


def _db():
    db = sqlite3.connect(DB)
    db.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
    return db


def tutorial_done() -> bool:
    db = _db()
    row = db.execute("SELECT v FROM meta WHERE k=?", (META_KEY,)).fetchone()
    db.close()
    return bool(row and row[0] == "1")


def mark_tutorial_done():
    db = _db()
    db.execute("INSERT OR REPLACE INTO meta(k, v) VALUES (?, '1')", (META_KEY,))
    db.commit()
    db.close()


def reset_tutorial():
    db = _db()
    db.execute("DELETE FROM meta WHERE k=?", (META_KEY,))
    db.commit()
    db.close()


SLIDES = [
    {
        "icon": "fa5s.braille",
        "title": "Добро пожаловать в Nucleus",
        "text": (
            "Один экран для всего: запускай команды, веди заметки, строй "
            "графики, следи за системой — всё по одному хоткею.\n\n"
            "Вызывается из любого места:  Ctrl + Space"
        ),
    },
    {
        "icon": "fa5s.keyboard",
        "title": "Ввод и навигация",
        "text": (
            "Печатай название действия или префикс — список фильтруется.\n\n"
            "↑ ↓ — навигация\n"
            "⏎   — выполнить\n"
            "Esc — назад / скрыть окно"
        ),
    },
    {
        "icon": "fa5s.calculator",
        "title": "Префиксы — быстрый доступ",
        "text": (
            "=   Калькулятор (пусто = экран с графиком и таблицей)\n"
            ">   Shell-команда\n"
            "@   Открыть папку или файл\n"
            "#   Заметки с Markdown\n"
            ":   Эмодзи\n"
            "%   Система (CPU, RAM, графики)\n"
            "~   Таймер  (5m, 1h30m, 90s)\n"
            "?   Помощь и этот туториал"
        ),
    },
    {
        "icon": "fa5s.chart-line",
        "title": "Совет: графики и заметки",
        "text": (
            "Открой  =  → вкладка «График».\n"
            "Можно писать несколько функций через  ;  — они отобразятся "
            "разными цветами.\n\n"
            "Заметки (#) сохраняются автоматически и живут в nucleus.db "
            "рядом с приложением."
        ),
    },
    {
        "icon": "fa5s.check-circle",
        "title": "Готово",
        "text": (
            "Всё готово к работе. Если забудешь что-то — открой  ?  "
            "(Помощь). Оттуда же можно перезапустить этот туториал."
        ),
    },
]


class TutorialScreen(QWidget):
    def __init__(self, back_cb):
        super().__init__()
        self.back_cb = back_cb
        self.idx = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(20)

        # карточка слайда
        self.card = QFrame()
        self.card.setStyleSheet(
            f"QFrame {{ background:{PANEL}; border:none; border-radius:16px; }}")
        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(36, 36, 36, 36)
        card_lay.setSpacing(18)

        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(self.icon)

        self.title = QLabel()
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(
            f"color:{TEXT}; font: 700 22pt '{FONT_UI}'; background:transparent;")
        card_lay.addWidget(self.title)

        self.text = QLabel()
        self.text.setWordWrap(True)
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setStyleSheet(
            f"color:{SUB}; font: 12pt '{FONT_MONO}'; background:transparent;")
        card_lay.addWidget(self.text)

        root.addWidget(self.card, 1)

        # точки-индикаторы
        dots_row = QHBoxLayout()
        dots_row.addStretch()
        self.dots = []
        for _ in SLIDES:
            d = QLabel("●")
            d.setStyleSheet(f"color:{LINE}; font: 12pt '{FONT_MONO}';")
            dots_row.addWidget(d)
            self.dots.append(d)
        dots_row.addStretch()
        root.addLayout(dots_row)

        # кнопки
        btns = QHBoxLayout()
        btns.setSpacing(10)

        self.skip = QPushButton("Пропустить")
        self.skip.setCursor(Qt.CursorShape.PointingHandCursor)
        self.skip.setStyleSheet(self._btn_ghost())
        self.skip.clicked.connect(self.finish)

        self.prev = QPushButton(qta.icon("fa5s.arrow-left", color=SUB), " Назад")
        self.prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev.setStyleSheet(self._btn_ghost())
        self.prev.clicked.connect(self._prev)

        self.next = QPushButton("Далее ")
        self.next.setIcon(qta.icon("fa5s.arrow-right", color="#0B0B0C"))
        self.next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next.setStyleSheet(self._btn_primary())
        self.next.clicked.connect(self._next)

        btns.addWidget(self.skip)
        btns.addStretch()
        btns.addWidget(self.prev)
        btns.addWidget(self.next)
        root.addLayout(btns)

        QShortcut(QKeySequence("Return"), self, self._next)
        QShortcut(QKeySequence("Enter"),  self, self._next)
        QShortcut(QKeySequence("Left"),   self, self._prev)
        QShortcut(QKeySequence("Right"),  self, self._next)

        self._render()

    def _render(self):
        s = SLIDES[self.idx]
        self.icon.setPixmap(qta.icon(s["icon"], color=ACCENT).pixmap(56, 56))
        self.title.setText(s["title"])
        self.text.setText(s["text"])
        for i, d in enumerate(self.dots):
            d.setStyleSheet(
                f"color:{ACCENT if i == self.idx else LINE};"
                f"font: 12pt '{FONT_MONO}';")
        self.prev.setEnabled(self.idx > 0)
        last = self.idx == len(SLIDES) - 1
        self.next.setText("Начать " if last else "Далее ")
        self.next.setIcon(qta.icon(
            "fa5s.check" if last else "fa5s.arrow-right", color="#0B0B0C"))

    def _next(self):
        if self.idx < len(SLIDES) - 1:
            self.idx += 1
            self._render()
        else:
            self.finish()

    def _prev(self):
        if self.idx > 0:
            self.idx -= 1
            self._render()

    def finish(self):
        mark_tutorial_done()
        self.back_cb()

    def _btn_primary(self):
        return f"""
            QPushButton {{
                background:{ACCENT}; color:#0B0B0C; border:none;
                border-radius:10px; padding:10px 20px;
                font: 600 11pt '{FONT_UI}';
            }}
            QPushButton:hover {{ background:#D6FF6A; }}
            QPushButton:disabled {{ background:{LINE}; color:{DIM}; }}
        """

    def _btn_ghost(self):
        return f"""
            QPushButton {{
                background:transparent; color:{SUB}; border:1px solid {LINE};
                border-radius:10px; padding:10px 20px;
                font: 600 11pt '{FONT_UI}';
            }}
            QPushButton:hover {{ color:{TEXT}; }}
            QPushButton:disabled {{ color:{DIM}; border-color:{LINE}; }}
        """
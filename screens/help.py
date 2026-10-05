# screens/help.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QScrollArea, QFrame, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt
import qtawesome as qta
from theme import (ACCENT, TEXT, SUB, DIM, PANEL, LINE, FONT_UI, FONT_MONO)
from screens.tutorial import reset_tutorial


HELP_DATA = [
    {"prefix": "=", "icon": "fa5s.calculator", "title": "Калькулятор",
     "syntax": "= <выражение>",
     "examples": ["= 2+2*sin(pi/3)", "= sqrt(144)", "= log10(1000)"],
     "notes": "Пустое поле — открывает экран: выражение, график, таблица.",
     "target": "calc"},
    {"prefix": ">", "icon": "fa5s.terminal", "title": "Выполнить",
     "syntax": "> <shell-команда>",
     "examples": ["> ls", "> git status", "> ipconfig"],
     "notes": "На Windows идёт через PowerShell. Таймаут — 30 сек.",
     "target": None},
    {"prefix": "@", "icon": "fa5s.folder-open", "title": "Открыть",
     "syntax": "@ <путь>",
     "examples": ["@ C:\\Users", "@ .", "@ D:\\projects"],
     "notes": "Открывает папку или файл в проводнике.", "target": None},
    {"prefix": "#", "icon": "fa5s.sticky-note", "title": "Заметки",
     "syntax": "#",
     "examples": ["#"],
     "notes": "Редактор Markdown с живым превью и автосохранением.",
     "target": "notes"},
    {"prefix": ":", "icon": "fa5s.smile", "title": "Эмодзи",
     "syntax": ":",
     "examples": [":", ":fire", ":cat"],
     "notes": "Сетка + поиск по имени и тегам. Клик — в буфер.",
     "target": "emoji"},
    {"prefix": "%", "icon": "fa5s.heartbeat", "title": "Система",
     "syntax": "%",
     "examples": ["%"],
     "notes": "Кольца CPU/RAM/Диск, график 60 сек, топ-5 процессов.",
     "target": "system"},
    {"prefix": "~", "icon": "fa5s.stopwatch", "title": "Таймер",
     "syntax": "~ [время]",
     "examples": ["~", "~ 5m", "~ 1h30m", "~ 90s"],
     "notes": "Пусто — экран со спиннерами. С аргументом — сразу старт.",
     "target": "timer"},
    {"prefix": "?", "icon": "fa5s.question-circle", "title": "Помощь",
     "syntax": "?",
     "examples": ["?"],
     "notes": "Этот экран.", "target": "help"},
]


class HelpCard(QFrame):
    def __init__(self, item, on_try=None):
        super().__init__()
        self.on_try = on_try
        self.setStyleSheet(
            f"QFrame {{ background:{PANEL}; border:none; border-radius:14px; }}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(10)

        head = QHBoxLayout()
        head.setSpacing(10)
        ico = QLabel()
        ico.setPixmap(qta.icon(item["icon"], color=ACCENT).pixmap(20, 20))
        ico.setFixedWidth(24)
        title = QLabel(item["title"])
        title.setStyleSheet(
            f"color:{TEXT}; font: 600 13pt '{FONT_UI}'; background:transparent;")
        head.addWidget(ico); head.addWidget(title); head.addStretch()
        if on_try:
            btn = QPushButton(qta.icon("fa5s.arrow-right", color="#0B0B0C"), "")
            btn.setToolTip("Открыть")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"""
                QPushButton {{ background:{ACCENT}; border:none; border-radius:8px; }}
                QPushButton:hover {{ background:#D6FF6A; }}
            """)
            btn.clicked.connect(on_try)
            head.addWidget(btn)
        lay.addLayout(head)

        syn = QLabel(item["syntax"])
        syn.setStyleSheet(f"""
            color:{ACCENT}; font: 12pt '{FONT_MONO}';
            background:#0B0B0C; border-radius:8px; padding:8px 12px;
        """)
        lay.addWidget(syn)

        for ex in item.get("examples", []):
            lab = QLabel("  " + ex)
            lab.setStyleSheet(
                f"color:{SUB}; font: 10pt '{FONT_MONO}'; background:transparent;")
            lay.addWidget(lab)

        if item.get("notes"):
            note = QLabel(item["notes"])
            note.setWordWrap(True)
            note.setStyleSheet(
                f"color:{DIM}; font: 10pt '{FONT_UI}'; background:transparent;")
            lay.addWidget(note)


class HelpScreen(QWidget):
    def __init__(self, back_cb):
        super().__init__()
        self.back_cb = back_cb

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # верхняя строка: поиск + кнопка туториала
        top = QHBoxLayout()
        top.setSpacing(10)

        self.search = QLineEdit()
        self.search.setPlaceholderText("поиск по помощи…  (git, timer, markdown)")
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background:{PANEL}; color:{TEXT}; border:none;
                border-radius:10px; padding:12px 16px;
                font: 12pt '{FONT_UI}';
                selection-background-color:{ACCENT}; selection-color:#0B0B0C;
            }}
        """)
        self.search.textChanged.connect(self._filter)
        top.addWidget(self.search, 1)

        tut_btn = QPushButton(qta.icon("fa5s.graduation-cap", color="#0B0B0C"),
                              " Пройти туториал заново")
        tut_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        tut_btn.setStyleSheet(f"""
            QPushButton {{
                background:{ACCENT}; color:#0B0B0C; border:none;
                border-radius:10px; padding:12px 16px;
                font: 600 10pt '{FONT_UI}';
            }}
            QPushButton:hover {{ background:#D6FF6A; }}
        """)
        tut_btn.clicked.connect(self._restart_tutorial)
        top.addWidget(tut_btn)

        root.addLayout(top)

        # скролл с карточками
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background:transparent; border:none; }}
            QScrollBar:vertical {{ background:transparent; width:8px; margin:0; }}
            QScrollBar::handle:vertical {{
                background:{LINE}; border-radius:4px; min-height:30px;
            }}
            QScrollBar::handle:vertical:hover {{ background:{SUB}; }}
            QScrollBar::add-line, QScrollBar::sub-line {{ height:0; }}
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background:transparent;")
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(0, 0, 8, 0)
        self.grid.setSpacing(14)

        scroll.setWidget(self.container)
        root.addWidget(scroll, 1)

        # футер с хоткеями
        foot = QHBoxLayout()
        foot.setSpacing(16)
        for k, v in [("ctrl+space", "показать/скрыть"),
                     ("esc", "назад"),
                     ("↑↓", "навигация"),
                     ("⏎", "выполнить")]:
            kb = QLabel(k)
            kb.setStyleSheet(
                f"color:{SUB}; font: 10pt '{FONT_MONO}';"
                f"border:1px solid {LINE}; border-radius:4px; padding:2px 8px;")
            lb = QLabel(v)
            lb.setStyleSheet(f"color:{DIM}; font: 10pt '{FONT_UI}';")
            foot.addWidget(kb); foot.addSpacing(4); foot.addWidget(lb)
        foot.addStretch()
        root.addLayout(foot)

        self._render(HELP_DATA)

    def _render(self, items):
        while self.grid.count():
            it = self.grid.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()

        for i, item in enumerate(items):
            target = item.get("target")
            on_try = (lambda t=target: self._try(t)) if target else None
            card = HelpCard(item, on_try=on_try)
            self.grid.addWidget(card, i // 2, i % 2)

        self.grid.setRowStretch(self.grid.rowCount(), 1)

    def _filter(self, text):
        q = text.strip().lower()
        if not q:
            self._render(HELP_DATA)
            return
        hits = []
        for item in HELP_DATA:
            blob = " ".join([
                item["prefix"], item["title"], item["syntax"],
                " ".join(item.get("examples", [])),
                item.get("notes", ""),
            ]).lower()
            if q in blob:
                hits.append(item)
        self._render(hits)

    def _try(self, target):
        app = self.window()
        if hasattr(app, "open_screen"):
            app.open_screen(target)

    def _restart_tutorial(self):
        reset_tutorial()
        app = self.window()
        if hasattr(app, "open_screen"):
            app.open_screen("tutorial")
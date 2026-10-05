# main.py
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import subprocess, math, ast, os, webbrowser
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QListWidget, QListWidgetItem,
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QMenu, QSystemTrayIcon,
    QAbstractItemView, QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, QTimer, QEvent
from PyQt6.QtGui import (
    QKeySequence, QShortcut, QColor, QPainter, QPainterPath, QFont, QAction
)
import qtawesome as qta

from theme import (ACCENT, DIM, TEXT, SUB, LINE, FONT_UI, FONT_MONO,
                   card_style, input_style)
from registry import action, search, REGISTRY

from screens.notes    import NotesScreen
from screens.calc     import CalcScreen
from screens.emoji    import EmojiScreen
from screens.system   import SystemScreen
from screens.timer    import TimerScreen, parse_time
from screens.help     import HelpScreen
from screens.tutorial import TutorialScreen, tutorial_done

from core.plugins import load_plugins
from core.themes  import list_themes, current_theme, set_theme


# ─────────────── простые экшены ───────────────
@action(">", "Выполнить", "fa5s.terminal", "shell-команда")
def shell(q):
    cmd = q.lstrip(">").strip()
    if not cmd:
        return "> "
    if os.name == "nt":
        ps_cmd = "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;" + cmd
        try:
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=30)
            out = (proc.stdout or "") + (proc.stderr or "")
            return out.strip() or "(пусто)"
        except FileNotFoundError:
            try:
                proc = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True,
                    encoding="oem", errors="replace", timeout=30)
                out = (proc.stdout or "") + (proc.stderr or "")
                return out.strip() or "(пусто)"
            except Exception as e:
                return f"ошибка: {e}"
        except subprocess.TimeoutExpired:
            return "таймаут 30 сек"
        except Exception as e:
            return f"ошибка: {e}"
    try:
        proc = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30)
        out = (proc.stdout or "") + (proc.stderr or "")
        return out.strip() or "(пусто)"
    except subprocess.TimeoutExpired:
        return "таймаут 30 сек"
    except Exception as e:
        return f"ошибка: {e}"


@action("=", "Калькулятор", "fa5s.calculator", "выражение · дроби · график")
def calc(q):
    expr = q.lstrip("=").strip()
    if not expr:
        return "__SCREEN__calc"
    allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    try:
        tree = ast.parse(expr, mode="eval")
        return str(eval(compile(tree, "<c>", "eval"),
                        {"__builtins__": {}}, allowed))
    except Exception as e:
        return f"ошибка: {e}"


@action("@", "Открыть", "fa5s.folder-open", "папка или файл")
def open_path(q):
    path = q.lstrip("@").strip().strip('"')
    if not path:
        return "@ "
    if not os.path.exists(path):
        return f"не найдено: {path}"
    try:
        os.startfile(path)
    except AttributeError:
        subprocess.Popen(["xdg-open", path])
    return f"открыто: {path}"


@action("g", "Найти в Google", "fa5s.search", "откроет браузер")
def google(q):
    query = q.lstrip("g").strip()
    if not query:
        return "g "
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"ищу: {query}"


@action("yt", "YouTube", "fa5b.youtube", "поиск видео")
def yt(q):
    query = q.lstrip("yt").strip()
    if not query:
        return "yt "
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return f"YouTube: {query}"


@action("#", "Заметки", "fa5s.sticky-note", "markdown-редактор")
def _notes(_):
    return "__SCREEN__notes"


@action(":", "Эмодзи", "fa5s.smile", "сетка + поиск")
def _emoji(_):
    return "__SCREEN__emoji"


@action("%", "Система", "fa5s.heartbeat", "CPU · RAM · графики")
def _sys(_):
    return "__SCREEN__system"


@action("~", "Таймер", "fa5s.stopwatch", "5m · 1h30m — или пусто = экран")
def _timer(q):
    arg = q.lstrip("~").strip()
    if not arg:
        return "__SCREEN__timer"
    secs = parse_time(arg)
    if not secs:
        return f"не понял: {arg}"
    return f"__TIMER_START__{secs}"


@action("?", "Помощь", "fa5s.question-circle", "шпаргалка + туториал + темы")
def _help(_):
    return "__SCREEN__help"


# ─────────────── строка списка ───────────────
class Row(QWidget):
    def __init__(self, a, active=False):
        super().__init__()
        self._active = active
        self.setFixedHeight(52)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(22, 0, 22, 0)
        lay.setSpacing(16)

        self.bar = QFrame()
        self.bar.setFixedSize(2, 26)
        self.bar.setStyleSheet(
            f"background:{ACCENT if active else 'transparent'};"
            "border:none; border-radius:1px;")

        self.ico = QLabel()
        self.ico.setPixmap(qta.icon(a["icon"],
                                    color=ACCENT if active else DIM).pixmap(18, 18))
        self.ico.setFixedWidth(24)

        title = QLabel(a["title"])
        title.setStyleSheet(
            f"color:{TEXT if active else SUB};"
            f"font: 500 13pt '{FONT_UI}'; background:transparent;")

        sub = QLabel(a.get("subtitle", ""))
        sub.setStyleSheet(
            f"color:{DIM}; font: 10pt '{FONT_MONO}'; background:transparent;")

        lay.addWidget(self.bar); lay.addWidget(self.ico); lay.addWidget(title)
        lay.addStretch(); lay.addWidget(sub)

    def set_active(self, active):
        self._active = active
        self.bar.setStyleSheet(
            f"background:{ACCENT if active else 'transparent'};"
            "border:none; border-radius:1px;")
        self.update()

    def paintEvent(self, e):
        if not self._active:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(2, 4, self.width() - 4, self.height() - 8, 12, 12)
        c = QColor(ACCENT); c.setAlpha(22)
        p.fillPath(path, c)


SCREEN_PREFIXES = {"#", ":", "%", "?", "~", "="}


class Nucleus(QWidget):
    MAX_ROWS = 7
    ROW_H    = 52

    TOP_H    = 44
    INPUT_H  = 60
    FOOT_H   = 56
    WIDTH    = 820

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.Tool
                            | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(self.WIDTH)

        self.card = QFrame(self)
        self.card.setStyleSheet(card_style(20))

        # top
        top = QHBoxLayout()
        top.setContentsMargins(26, 20, 26, 4)
        mark = QLabel()
        mark.setPixmap(qta.icon("fa5s.braille", color=ACCENT).pixmap(16, 16))
        self.hint = QLabel("что хочешь сделать?")
        self.hint.setStyleSheet(
            f"color:{DIM}; font: 10pt '{FONT_MONO}'; background:transparent;")
        esc = QLabel("esc")
        esc.setStyleSheet(
            f"color:{DIM}; font: 10pt '{FONT_MONO}'; background:transparent;"
            f"border:1px solid {LINE}; border-radius:4px; padding:1px 6px;")
        top.addWidget(mark); top.addSpacing(10); top.addWidget(self.hint)
        top.addStretch(); top.addWidget(esc)

        # input
        self.input = QLineEdit()
        self.input.setStyleSheet(input_style(17))

        # list
        self.list = QListWidget()
        self.list.setStyleSheet(f"""
            QListWidget {{
                background:transparent; border:none; outline:none;
            }}
            QListWidget::item {{
                border:none; outline:none; padding:0;
            }}
            QListWidget::item:selected {{
                background:transparent; border:none;
            }}
            QScrollBar:vertical {{
                background:transparent; width:6px; margin:0;
            }}
            QScrollBar::handle:vertical {{
                background:{SUB}; border-radius:3px; min-height:24px;
            }}
            QScrollBar::handle:vertical:hover {{
                background:{ACCENT};
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                height:0; border:none; background:none;
            }}
            QScrollBar::add-page, QScrollBar::sub-page {{
                background:transparent;
            }}
        """)
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.list.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerItem)

        self.input.wheelEvent = lambda e: self.list.wheelEvent(e)

        # stack экранов
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Ignored
        )
        self.screens = {
            "notes":    NotesScreen(self.back),
            "calc":     CalcScreen(self.back),
            "emoji":    EmojiScreen(self.back),
            "system":   SystemScreen(self.back),
            "timer":    TimerScreen(self.back),
            "help":     HelpScreen(self.back),
            "tutorial": TutorialScreen(self.back),
        }
        for w in self.screens.values():
            self.stack.addWidget(w)

        # главный экран
        main_wrap = QWidget()
        mwl = QVBoxLayout(main_wrap)
        mwl.setContentsMargins(0, 0, 0, 0)
        mwl.setSpacing(0)
        mwl.addWidget(self.input)
        mwl.addWidget(self.list)
        self.stack.insertWidget(0, main_wrap)
        self.stack.setCurrentIndex(0)

        # footer
        foot = QHBoxLayout()
        foot.setContentsMargins(26, 10, 26, 20)
        for k, v in [("↑↓", "навигация"), ("⏎", "выполнить"),
                     ("esc", "назад/скрыть")]:
            kb = QLabel(k)
            kb.setStyleSheet(
                f"color:{SUB}; font: 10pt '{FONT_MONO}'; background:transparent;"
                f"border:1px solid {LINE}; border-radius:4px; padding:1px 7px;")
            lb = QLabel(v)
            lb.setStyleSheet(
                f"color:{DIM}; font: 10pt '{FONT_UI}'; background:transparent;")
            foot.addWidget(kb); foot.addSpacing(4)
            foot.addWidget(lb); foot.addSpacing(16)
        foot.addStretch()

        inner = QVBoxLayout(self.card)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(0)
        inner.addLayout(top)
        inner.addWidget(self.stack)
        inner.addLayout(foot)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.card)

        self.input.textChanged.connect(self.refresh)
        self.input.returnPressed.connect(self.execute)
        self.list.currentRowChanged.connect(self._on_row)
        self.list.itemClicked.connect(lambda _: self.execute())

        QShortcut(QKeySequence("Return"), self, self.execute)
        QShortcut(QKeySequence("Enter"),  self, self.execute)
        QShortcut(QKeySequence("Escape"), self, self.escape)
        QShortcut(QKeySequence("Ctrl+K"), self, lambda: self.input.clear())

        self._drag_pos = None
        self.card.installEventFilter(self)

        self._build_tray()
        self.input.setFocus()

    # ── перетаскивание окна ──
    def eventFilter(self, obj, ev):
        if obj is self.card:
            if ev.type() == QEvent.Type.MouseButtonPress:
                if ev.button() == Qt.MouseButton.LeftButton:
                    if ev.position().y() < 60:
                        self._drag_pos = (ev.globalPosition().toPoint()
                                          - self.frameGeometry().topLeft())
                        return True
            elif ev.type() == QEvent.Type.MouseMove:
                if self._drag_pos is not None:
                    self.move(ev.globalPosition().toPoint() - self._drag_pos)
                    return True
            elif ev.type() == QEvent.Type.MouseButtonRelease:
                self._drag_pos = None
                return True
        return super().eventFilter(obj, ev)

    # ── навигация ──
    def open_screen(self, name):
        if name not in self.screens:
            return
        idx = list(self.screens.keys()).index(name) + 1
        self.stack.setCurrentIndex(idx)
        self.hint.setText(name)
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.resize(1000, 700)

    def back(self):
        self.stack.setCurrentIndex(0)
        self.hint.setText("что хочешь сделать?")
        self.setFixedWidth(self.WIDTH)
        self.input.clear()
        self.input.setFocus()
        QTimer.singleShot(0, self._fit_window)

    def escape(self):
        if self.stack.currentIndex() != 0:
            self.back()
        else:
            self.hide()

    def keyPressEvent(self, e):
        if self.stack.currentIndex() != 0:
            super().keyPressEvent(e)
            return

        n = self.list.count()
        if n == 0:
            super().keyPressEvent(e)
            return

        r = self.list.currentRow()

        if e.key() == Qt.Key.Key_Down:
            if r < n - 1:
                self.list.setCurrentRow(r + 1)
            return

        if e.key() == Qt.Key.Key_Up:
            if r > 0:
                self.list.setCurrentRow(r - 1)
            return

        if e.key() == Qt.Key.Key_PageDown:
            new_r = min(r + self.MAX_ROWS, n - 1)
            self.list.setCurrentRow(new_r)
            return

        if e.key() == Qt.Key.Key_PageUp:
            new_r = max(r - self.MAX_ROWS, 0)
            self.list.setCurrentRow(new_r)
            return

        if e.key() == Qt.Key.Key_Home:
            self.list.setCurrentRow(0)
            return

        if e.key() == Qt.Key.Key_End:
            self.list.setCurrentRow(n - 1)
            return

        super().keyPressEvent(e)

    # ── трей ──
    def _build_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(qta.icon("fa5s.braille", color=ACCENT))
        self.tray.setToolTip("Nucleus")

        menu = QMenu()
        a1 = QAction("Показать / скрыть", self)
        a1.triggered.connect(self.toggle)

        a_note = QAction(qta.icon("fa5s.sticky-note", color=SUB),
                         "Новая заметка", self)
        a_note.triggered.connect(lambda: (self.show(), self.open_screen("notes")))

        a_help = QAction("Помощь", self)
        a_help.triggered.connect(lambda: (self.show(), self.open_screen("help")))

        a_tut = QAction("Туториал заново", self)
        a_tut.triggered.connect(lambda: (self.show(), self.open_screen("tutorial")))

        themes_menu = QMenu("Тема", menu)
        cur = current_theme()
        for key, label in list_themes().items():
            act = QAction(label + ("  ✓" if key == cur else ""), self)
            act.triggered.connect(lambda _, k=key: set_theme(k))
            themes_menu.addAction(act)

        a4 = QAction("Выход", self)
        a4.triggered.connect(QApplication.instance().quit)

        menu.addAction(a1); menu.addSeparator()
        menu.addAction(a_note)
        menu.addAction(a_help); menu.addAction(a_tut)
        menu.addSeparator()
        menu.addMenu(themes_menu)
        menu.addSeparator(); menu.addAction(a4)
        self.tray.setContextMenu(menu)

        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle()

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show(); self.raise_(); self.activateWindow()
            self.input.setFocus()

    # ── список ──
    def refresh(self, text):
        results = search(text)
        self.list.clear()
        for i, a in enumerate(results):
            w = Row(a, active=(i == 0))
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, self.ROW_H))
            item.setData(Qt.ItemDataRole.UserRole, a)
            self.list.addItem(item)
            self.list.setItemWidget(item, w)

        if results:
            self.list.setCurrentRow(0)
            self._on_row(0)

        QTimer.singleShot(0, self._fit_window)

    def _fit_window(self):
        """
        Окно показывает не более MAX_ROWS строк.
        Список — ровно эта же высота (видимая зона).
        Скролл делает QListWidget сам, потому что элементов больше, чем помещается.
        """
        count = self.list.count()

        if count == 0:
            self.list.setFixedHeight(0)
            if self.stack.currentIndex() == 0:
                self.setFixedWidth(self.WIDTH)
                self.setFixedHeight(self.TOP_H + self.INPUT_H + self.FOOT_H)
            return

        # ─── КЛЮЧЕВОЕ: высота списка = ВИДИМАЯ зона, не весь контент ───
        visible = min(count, self.MAX_ROWS)
        view_h = visible * self.ROW_H
        self.list.setFixedHeight(view_h)

        if self.stack.currentIndex() != 0:
            return

        total = self.TOP_H + self.INPUT_H + view_h + self.FOOT_H
        self.setFixedWidth(self.WIDTH)
        self.setFixedHeight(total)

        # прокрутить к текущей строке (если уже выбрана не первая)
        cur = self.list.currentRow()
        if cur >= 0:
            self.list.scrollToItem(
                self.list.item(cur),
                QAbstractItemView.ScrollHint.EnsureVisible
            )

    def _on_row(self, row):
        for i in range(self.list.count()):
            it = self.list.item(i)
            w = self.list.itemWidget(it)
            if w:
                w.set_active(i == row)
                a = it.data(Qt.ItemDataRole.UserRole)
                w.ico.setPixmap(qta.icon(
                    a["icon"], color=ACCENT if i == row else DIM).pixmap(18, 18))
        # прокрутка к выбранной строке
        if row >= 0:
            it = self.list.item(row)
            if it:
                self.list.scrollToItem(
                    it, QAbstractItemView.ScrollHint.EnsureVisible
                )

    # ── выполнение ──
    def execute(self):
        self.input.setFocus()
        it = self.list.currentItem()
        if it is None and self.list.count() > 0:
            it = self.list.item(0)
            self.list.setCurrentRow(0)
        if it is None:
            return

        a = it.data(Qt.ItemDataRole.UserRole)
        text = self.input.text().strip()
        prefix = a["prefix"]

        if text == "" or text == prefix:
            if prefix in SCREEN_PREFIXES:
                try:
                    out = a["run"](prefix)
                except Exception as e:
                    out = f"ошибка: {e}"

                if isinstance(out, str) and out.startswith("__SCREEN__"):
                    name = out.replace("__SCREEN__", "")
                    self.input.clear()
                    self.open_screen(name)
                    return
                if isinstance(out, str) and out.startswith("__TIMER_START__"):
                    secs = int(out.replace("__TIMER_START__", ""))
                    self.input.clear()
                    self.open_screen("timer")
                    t = self.screens["timer"]
                    t.total = t.left = secs
                    t.toggle()
                    return
                self.input.setText(out.splitlines()[0] if out else "")
                self.input.setFocus()
                return

            self.input.setText(prefix + " ")
            self.input.setFocus()
            return

        try:
            out = a["run"](text)
        except Exception as e:
            out = f"ошибка: {e}"

        if isinstance(out, str) and out.startswith("__SCREEN__"):
            name = out.replace("__SCREEN__", "")
            self.input.clear()
            self.open_screen(name)
            return
        if isinstance(out, str) and out.startswith("__TIMER_START__"):
            secs = int(out.replace("__TIMER_START__", ""))
            self.input.clear()
            self.open_screen("timer")
            t = self.screens["timer"]
            t.total = t.left = secs
            t.toggle()
            return

        self.input.setText(out.splitlines()[0] if out else "")
        self.input.setFocus()

    def showEvent(self, e):
        super().showEvent(e)
        self.input.setFocus()
        QTimer.singleShot(0, self._fit_window)


def install_hotkey(window):
    try:
        from pynput import keyboard
    except ImportError:
        print("pynput не установлен — Ctrl+Space не сработает.")
        return

    def on_activate():
        QTimer.singleShot(0, window.toggle)

    hk = keyboard.GlobalHotKeys({"<ctrl>+<space>": on_activate})
    hk.daemon = True
    hk.start()


def main():
    load_plugins()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setFont(QFont(FONT_UI, 11))

    w = Nucleus()
    g = app.primaryScreen().availableGeometry()
    w.resize(w.WIDTH, 400)
    w.move(g.center().x() - w.width() // 2, g.top() + 80)

    if not tutorial_done():
        w.open_screen("tutorial")
    else:
        w.refresh("")

    w.show()
    install_hotkey(w)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
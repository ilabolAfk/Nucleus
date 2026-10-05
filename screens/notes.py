# screens/notes.py
import sqlite3, os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QTextEdit, QTextBrowser, QPushButton, QLabel, QSplitter, QLineEdit,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
import qtawesome as qta
import markdown
from theme import (ACCENT, TEXT, SUB, DIM, PANEL, LINE,
                   FONT_UI, FONT_MONO)

DB = "nucleus.db"


def _db():
    db = sqlite3.connect(DB)
    db.execute("""CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, body TEXT,
        ts DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    return db


class NotesScreen(QWidget):
    def __init__(self, back_cb):
        super().__init__()
        self.back_cb = back_cb
        self.current_id = None
        self._dirty = False

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── левая колонка ──
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(18, 18, 12, 18)
        ll.setSpacing(10)

        head = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("поиск…")
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background:{PANEL}; color:{TEXT};
                border:none; border-radius:8px;
                padding:8px 12px; font: 10pt '{FONT_UI}';
            }}
        """)
        self.search.textChanged.connect(self.reload_list)
        head.addWidget(self.search)

        add_btn = QPushButton()
        add_btn.setIcon(qta.icon("fa5s.plus", color="#0B0B0C"))
        add_btn.setFixedSize(34, 34)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{ background:{ACCENT}; border:none; border-radius:8px; }}
            QPushButton:hover {{ background:#D6FF6A; }}
        """)
        add_btn.clicked.connect(self.new_note)
        head.addWidget(add_btn)
        ll.addLayout(head)

        self.list = QListWidget()
        self.list.setStyleSheet(f"""
            QListWidget {{ background:transparent; border:none; outline:none;
                color:{SUB}; font: 11pt '{FONT_UI}'; }}
            QListWidget::item {{ padding:10px 12px; border-radius:8px; }}
            QListWidget::item:selected {{ background:{PANEL}; color:{TEXT}; }}
        """)
        self.list.currentItemChanged.connect(self._on_select)
        ll.addWidget(self.list)

        # ── правая колонка ──
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(12, 18, 18, 18)
        rl.setSpacing(10)

        bar = QHBoxLayout()
        bar.setSpacing(4)
        for icon, tip, wrap in [
            ("fa5s.bold", "Жирный", "**"),
            ("fa5s.italic", "Курсив", "*"),
            ("fa5s.code", "Код", "`"),
            ("fa5s.font", "Заголовок", "# "),
            ("fa5s.list-ul", "Список", "- "),
            ("fa5s.quote-right", "Цитата", "> "),
            ("fa5s.link", "Ссылка", "[текст](url)"),
            ("fa5s.table", "Таблица", "| a | b |\n|---|---|\n| 1 | 2 |\n"),
        ]:
            b = QPushButton()
            b.setIcon(qta.icon(icon, color=SUB))
            b.setToolTip(tip)
            b.setFixedSize(32, 32)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{ background:transparent; border:none; border-radius:6px; }}
                QPushButton:hover {{ background:{PANEL}; }}
            """)
            b.clicked.connect(lambda _, w=wrap: self._wrap(w))
            bar.addWidget(b)
        bar.addStretch()

        del_btn = QPushButton()
        del_btn.setIcon(qta.icon("fa5s.trash-alt", color="#FF6B6B"))
        del_btn.setToolTip("Удалить заметку")
        del_btn.setFixedSize(32, 32)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{ background:transparent; border:none; border-radius:6px; }}
            QPushButton:hover {{ background:{PANEL}; }}
        """)
        del_btn.clicked.connect(self.delete_note)
        bar.addWidget(del_btn)
        rl.addLayout(bar)

        split = QSplitter(Qt.Orientation.Horizontal)
        split.setStyleSheet(f"QSplitter::handle {{ background:{LINE}; width:1px; }}")

        self.editor = QTextEdit()
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background:{PANEL}; color:{TEXT}; border:none;
                border-radius:12px; padding:14px;
                font: 11pt '{FONT_MONO}';
                selection-background-color:{ACCENT}; selection-color:#0B0B0C;
            }}
        """)
        self.editor.textChanged.connect(self._on_edit)

        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(True)
        self.preview.setStyleSheet(f"""
            QTextBrowser {{
                background:{PANEL}; color:{TEXT}; border:none;
                border-radius:12px; padding:14px;
                font: 11pt '{FONT_UI}';
            }}
        """)

        split.addWidget(self.editor)
        split.addWidget(self.preview)
        split.setSizes([400, 400])
        rl.addWidget(split, 1)

        # индикатор автосейва
        self.saved = QLabel("")
        self.saved.setStyleSheet(
            f"color:{DIM}; font: 9pt '{FONT_MONO}'; background:transparent;")
        rl.addWidget(self.saved)

        root.addWidget(left, 1)
        root.addWidget(right, 2)

        # автосейв
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(600)
        self._save_timer.timeout.connect(self._save)

        self.reload_list()

    # ── helpers ──
    def _wrap(self, wrap):
        cur = self.editor.textCursor()
        sel = cur.selectedText()
        if wrap.startswith("[") and wrap.endswith(")"):
            cur.insertText(f"[{sel or 'текст'}](url)")
        elif wrap.startswith("|"):
            cur.insertText(wrap)
        else:
            cur.insertText(f"{wrap}{sel or 'текст'}{wrap}")
        self.editor.setFocus()

    def reload_list(self):
        q = self.search.text().strip().lower()
        db = _db()
        rows = db.execute(
            "SELECT id, COALESCE(title,''), COALESCE(body,''), ts "
            "FROM notes ORDER BY ts DESC").fetchall()
        db.close()
        self.list.blockSignals(True)
        self.list.clear()
        for id_, title, body, ts in rows:
            first = (title or body.split("\n")[0])[:60]
            if q and q not in (first + body).lower():
                continue
            it = QListWidgetItem(qta.icon("fa5s.file-alt", color=SUB),
                                 first or "без названия")
            it.setData(Qt.ItemDataRole.UserRole, id_)
            self.list.addItem(it)
        self.list.blockSignals(False)

    def new_note(self):
        # сначала сохраним текущую
        if self._dirty:
            self._save()

        db = _db()
        cur = db.execute("INSERT INTO notes(title, body) VALUES (?, ?)", ("", ""))
        db.commit()
        nid = cur.lastrowid
        db.close()
        self.reload_list()
        for i in range(self.list.count()):
            if self.list.item(i).data(Qt.ItemDataRole.UserRole) == nid:
                self.list.setCurrentRow(i)
                break

    def _on_select(self, cur, _prev):
        # сохраняем предыдущую перед переключением
        if self._dirty:
            self._save()

        if not cur:
            self.current_id = None
            self.editor.blockSignals(True)
            self.editor.clear()
            self.editor.blockSignals(False)
            self.preview.clear()
            return

        nid = cur.data(Qt.ItemDataRole.UserRole)
        db = _db()
        row = db.execute("SELECT body FROM notes WHERE id=?", (nid,)).fetchone()
        db.close()
        self.current_id = nid
        self.editor.blockSignals(True)
        self.editor.setPlainText(row[0] if row else "")
        self.editor.blockSignals(False)
        self._dirty = False
        self.saved.setText("")
        self._render()

    def _on_edit(self):
        self._dirty = True
        self.saved.setText("изменено…")
        self._render()
        self._save_timer.start()

    def _render(self):
        md = self.editor.toPlainText()
        try:
            html = markdown.markdown(md, extensions=["fenced_code", "tables"])
        except Exception:
            html = md
        self.preview.setHtml(f"""
            <style>
                body {{ color:{TEXT}; font-family:'{FONT_UI}'; font-size:11pt; }}
                h1,h2,h3 {{ color:{ACCENT}; }}
                code {{ background:#0B0B0C; color:{ACCENT}; padding:2px 4px;
                       border-radius:4px; font-family:'{FONT_MONO}'; }}
                pre {{ background:#0B0B0C; padding:10px; border-radius:8px; }}
                a {{ color:{ACCENT}; }}
                table {{ border-collapse:collapse; }}
                td,th {{ border:1px solid {LINE}; padding:4px 8px; }}
            </style>
            {html}""")

    def _save(self):
        if self.current_id is None:
            return
        body = self.editor.toPlainText()
        title = body.split("\n", 1)[0][:80] if body else ""
        db = _db()
        db.execute("UPDATE notes SET body=?, title=?, ts=CURRENT_TIMESTAMP WHERE id=?",
                   (body, title, self.current_id))
        db.commit()
        db.close()
        self._dirty = False
        self.saved.setText("сохранено")
        QTimer.singleShot(1500, lambda: self.saved.setText(""))
        self.reload_list()

    def delete_note(self):
        if self.current_id is None:
            return
        r = QMessageBox.question(self, "Удалить?",
                                 "Точно удалить заметку?",
                                 QMessageBox.StandardButton.Yes |
                                 QMessageBox.StandardButton.No)
        if r != QMessageBox.StandardButton.Yes:
            return
        db = _db()
        db.execute("DELETE FROM notes WHERE id=?", (self.current_id,))
        db.commit()
        db.close()
        self.current_id = None
        self._dirty = False
        self.editor.clear()
        self.preview.clear()
        self.reload_list()

    def hideEvent(self, e):
        # сохраняем при уходе с экрана
        if self._dirty:
            self._save()
        super().hideEvent(e)
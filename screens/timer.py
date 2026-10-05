# screens/timer.py
import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSpinBox,
                             QPushButton, QLabel, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import qtawesome as qta
from theme import ACCENT, TEXT, SUB, DIM, PANEL, LINE, FONT_UI, FONT_MONO

TIME_RE = re.compile(r"^\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?\s*(?:(\d+)\s*s)?\s*$", re.I)

def parse_time(s):
    s = s.strip().lower()
    if not s: return None
    if ":" in s:
        parts = [int(p) for p in s.split(":") if p.strip().isdigit()]
        if len(parts) == 2: return parts[0]*60 + parts[1]
        if len(parts) == 3: return parts[0]*3600 + parts[1]*60 + parts[2]
        return None
    if s.isdigit(): return int(s)*60
    m = TIME_RE.match(s)
    if not m or not any(m.groups()): return None
    h, mi, se = (int(x) if x else 0 for x in m.groups())
    return (h*3600 + mi*60 + se) or None


class TimerScreen(QWidget):
    def __init__(self, back_cb):
        super().__init__()
        self.back_cb = back_cb
        self.left = 0
        self.total = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.addStretch()

        self.big = QLabel("00:00")
        self.big.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.big.setStyleSheet(f"color:{ACCENT}; font: 700 64pt '{FONT_MONO}';")
        root.addWidget(self.big)

        spin_row = QHBoxLayout()
        spin_row.addStretch()
        self.h = self._spin(0, 23, "ч"); self.h.setValue(0)
        self.m = self._spin(0, 59, "м"); self.m.setValue(25)
        self.s = self._spin(0, 59, "с"); self.s.setValue(0)
        for w in (self.h, self.m, self.s):
            spin_row.addWidget(w)
        spin_row.addStretch()
        root.addLayout(spin_row)

        btns = QHBoxLayout()
        btns.addStretch()
        self.btn = QPushButton(qta.icon("fa5s.play", color="#0B0B0C"), " Старт")
        self.btn.setStyleSheet(self._btn())
        self.btn.clicked.connect(self.toggle)
        reset = QPushButton(qta.icon("fa5s.redo", color=SUB), " Сброс")
        reset.setStyleSheet(self._btn2())
        reset.clicked.connect(self.reset)
        btns.addWidget(self.btn); btns.addWidget(reset)
        btns.addStretch()
        root.addLayout(btns)
        root.addStretch()

        self.tick = QTimer(self)
        self.tick.setInterval(1000)
        self.tick.timeout.connect(self._on_tick)

    def _spin(self, lo, hi, suf):
        sp = QSpinBox()
        sp.setRange(lo, hi); sp.setSuffix(" " + suf); sp.setFixedWidth(90)
        sp.setStyleSheet(f"""
            QSpinBox {{
                background:{PANEL}; color:{TEXT}; border:1px solid {LINE};
                border-radius:10px; padding:8px 10px;
                font: 14pt '{FONT_MONO}';
            }}
        """)
        return sp

    def toggle(self):
        if self.tick.isActive():
            self.tick.stop()
            self.btn.setText(" Старт")
            self.btn.setIcon(qta.icon("fa5s.play", color="#0B0B0C"))
        else:
            if self.left <= 0:
                self.total = self.left = (self.h.value()*3600
                                          + self.m.value()*60
                                          + self.s.value())
            if self.left > 0:
                self.tick.start()
                self.btn.setText(" Пауза")
                self.btn.setIcon(qta.icon("fa5s.pause", color="#0B0B0C"))

    def reset(self):
        self.tick.stop()
        self.left = 0
        self.big.setText("00:00")
        self.btn.setText(" Старт")
        self.btn.setIcon(qta.icon("fa5s.play", color="#0B0B0C"))

    def _on_tick(self):
        self.left -= 1
        if self.left <= 0:
            self.tick.stop()
            self.big.setText("00:00")
            QApplication.beep()
            self.btn.setText(" Старт")
            self.btn.setIcon(qta.icon("fa5s.play", color="#0B0B0C"))
            return
        m, s = divmod(self.left, 60)
        h, m = divmod(m, 60)
        self.big.setText(f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}")

    def _btn(self):
        return f"""
            QPushButton {{ background:{ACCENT}; color:#0B0B0C; border:none;
                border-radius:10px; padding:10px 22px;
                font: 600 12pt '{FONT_UI}'; }}
            QPushButton:hover {{ background:#D6FF6A; }}
        """
    def _btn2(self):
        return f"""
            QPushButton {{ background:{PANEL}; color:{SUB}; border:1px solid {LINE};
                border-radius:10px; padding:10px 22px;
                font: 600 12pt '{FONT_UI}'; }}
            QPushButton:hover {{ color:{TEXT}; }}
        """
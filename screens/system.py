# screens/system.py
import os, collections
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
import qtawesome as qta
import pyqtgraph as pg
from theme import ACCENT, TEXT, SUB, DIM, PANEL, LINE, FONT_UI, FONT_MONO

try:
    import psutil
    HAS_PS = True
except ImportError:
    HAS_PS = False


class Ring(QWidget):
    """Кольцевой индикатор 0..100."""
    def __init__(self, label, icon):
        super().__init__()
        self.setFixedSize(140, 140)
        self.value = 0
        self.label = label
        self.icon = icon

    def set_value(self, v):
        self.value = max(0, min(100, v))
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(15, 15, 110, 110)

        # фон
        pen = QPen(QColor(LINE), 10)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawArc(rect, 0, 360 * 16)

        # значение
        col = QColor(ACCENT)
        if self.value > 80: col = QColor("#FF6B6B")
        elif self.value > 60: col = QColor("#FFD166")
        pen = QPen(col, 10)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawArc(rect, 90 * 16, -int(self.value * 3.6 * 16))

        # иконка
        ic = qta.icon(self.icon, color=col).pixmap(20, 20)
        p.drawPixmap(int(rect.center().x() - 10),
                     int(rect.center().y() - 34), ic)

        # проценты
        p.setPen(QColor(TEXT))
        p.setFont(QFont(FONT_MONO, 16, QFont.Weight.Bold))
        p.drawText(rect.adjusted(0, 10, 0, 0),
                   Qt.AlignmentFlag.AlignCenter, f"{self.value:.0f}%")

        # подпись
        p.setPen(QColor(SUB))
        p.setFont(QFont(FONT_UI, 9))
        p.drawText(rect.adjusted(0, 60, 0, 0),
                   Qt.AlignmentFlag.AlignCenter, self.label)


class SystemScreen(QWidget):
    def __init__(self, back_cb):
        super().__init__()
        self.back_cb = back_cb
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        # кольца
        rings = QHBoxLayout()
        rings.setSpacing(18)
        self.cpu = Ring("CPU", "fa5s.microchip")
        self.ram = Ring("RAM", "fa5s.memory")
        self.dsk = Ring("Диск", "fa5s.hdd")
        for r in (self.cpu, self.ram, self.dsk):
            rings.addWidget(r)
        rings.addStretch()
        root.addLayout(rings)

        # график CPU/RAM
        self.plot = pg.PlotWidget(background=PANEL)
        self.plot.showGrid(x=False, y=True, alpha=0.15)
        self.plot.getAxis("left").setPen(LINE)
        self.plot.getAxis("bottom").setPen(LINE)
        self.plot.getAxis("left").setTextPen(SUB)
        self.plot.getAxis("bottom").setTextPen(SUB)
        self.plot.setYRange(0, 100)
        self.plot.setMouseEnabled(x=False, y=False)
        self.plot.addLegend(offset=(10, 10))
        self.curve_cpu = self.plot.plot(pen=pg.mkPen(ACCENT, width=2), name="CPU")
        self.curve_ram = self.plot.plot(pen=pg.mkPen("#7DD3FC", width=2), name="RAM")

        self.hist_cpu = collections.deque([0] * 60, maxlen=60)
        self.hist_ram = collections.deque([0] * 60, maxlen=60)

        wrap = QWidget()
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(14, 14, 14, 14)
        wl.addWidget(self.plot)
        wrap.setStyleSheet(f"background:{PANEL}; border-radius:12px;")
        root.addWidget(wrap, 1)

        # топ процессов
        self.top = QLabel("—")
        self.top.setStyleSheet(f"""
            color:{SUB}; font: 10pt '{FONT_MONO}';
            background:{PANEL}; border-radius:12px; padding:14px;
        """)
        root.addWidget(self.top)

        self.tick = QTimer(self)
        self.tick.setInterval(1000)
        self.tick.timeout.connect(self._update)
        self.tick.start()
        self._update()

    def _update(self):
        if not HAS_PS:
            self.top.setText("поставь psutil: pip install psutil")
            return
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        dsk = psutil.disk_usage(os.path.abspath(os.sep)).percent

        self.cpu.set_value(cpu)
        self.ram.set_value(ram)
        self.dsk.set_value(dsk)

        self.hist_cpu.append(cpu)
        self.hist_ram.append(ram)
        self.curve_cpu.setData(list(self.hist_cpu))
        self.curve_ram.setData(list(self.hist_ram))

        procs = []
        for p in psutil.process_iter(["name", "cpu_percent", "memory_percent"]):
            try:
                procs.append((p.info["name"] or "?",
                              p.info["cpu_percent"] or 0,
                              p.info["memory_percent"] or 0))
            except Exception:
                pass
        procs.sort(key=lambda x: -x[1])
        lines = ["  ".join(["ТОП ПРОЦЕССОВ".ljust(20), "CPU", "RAM"])]
        for n, c, m in procs[:5]:
            lines.append(f"{n[:20].ljust(20)}  {c:5.1f}  {m:4.1f}")
        self.top.setText("\n".join(lines))

    def hideEvent(self, e):
        self.tick.stop()
        super().hideEvent(e)

    def showEvent(self, e):
        super().showEvent(e)
        self.tick.start()
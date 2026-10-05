# screens/calc.py
import math, ast, csv, os
from fractions import Fraction
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
    QFileDialog, QFrame, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
import qtawesome as qta
import numpy as np
import pyqtgraph as pg
import sympy as sp
from theme import ACCENT, TEXT, SUB, DIM, PANEL, LINE, FONT_UI, FONT_MONO


# ─────────────── парсер обыкновенных дробей ───────────────
class FractionParser:
    def __init__(self, text):
        self.text = text
        self.i = 0
        self.n = len(text)

    def parse(self):
        try:
            v = self._expr()
            self._skip_ws()
            if self.i != self.n:
                return None
            return v
        except Exception:
            return None

    def _skip_ws(self):
        while self.i < self.n and self.text[self.i].isspace():
            self.i += 1

    def _peek(self):
        self._skip_ws()
        return self.text[self.i] if self.i < self.n else ""

    def _expr(self):
        v = self._term()
        while True:
            c = self._peek()
            if c == "+":
                self.i += 1
                v = v + self._term()
            elif c == "-":
                self.i += 1
                v = v - self._term()
            else:
                return v

    def _term(self):
        v = self._factor()
        while True:
            c = self._peek()
            if c == "*":
                self.i += 1
                v = v * self._factor()
            elif c == "/":
                self.i += 1
                r = self._factor()
                if r == 0:
                    raise ZeroDivisionError
                v = v / r
            else:
                return v

    def _factor(self):
        v = self._atom()
        if self._peek() == "**":
            self.i += 2
            e = self._factor()
            if e.denominator != 1:
                return Fraction(float(v) ** float(e))
            return v ** int(e)
        return v

    def _atom(self):
        c = self._peek()
        if c == "(":
            self.i += 1
            v = self._expr()
            if self._peek() != ")":
                raise ValueError("нет )")
            self.i += 1
            return v
        if c == "-":
            self.i += 1
            return -self._atom()
        if c == "+":
            self.i += 1
            return self._atom()
        return self._number()

    def _number(self):
        self._skip_ws()
        start = self.i
        while self.i < self.n and self.text[self.i].isdigit():
            self.i += 1
        int_part = self.text[start:self.i]

        save = self.i
        self._skip_ws()
        if (self.i < self.n and self.text[self.i].isdigit() and int_part):
            start2 = self.i
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1
            num = self.text[start2:self.i]
            if self.i < self.n and self.text[self.i] == "/":
                self.i += 1
                start3 = self.i
                while self.i < self.n and self.text[self.i].isdigit():
                    self.i += 1
                den = self.text[start3:self.i]
                if den:
                    return Fraction(int(int_part)) + Fraction(int(num), int(den))
            self.i = save

        if self.i < self.n and self.text[self.i] == "/":
            self.i += 1
            start2 = self.i
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1
            den = self.text[start2:self.i]
            if not int_part or not den:
                raise ValueError("плохая дробь")
            return Fraction(int(int_part), int(den))

        if not int_part:
            raise ValueError("нет числа")
        return Fraction(int(int_part))


def try_fraction(expr: str):
    for ch in expr:
        if ch.isalpha() or ch == "." or ch == "_":
            return None, None
    p = FractionParser(expr)
    v = p.parse()
    if v is None:
        return None, None
    if v.denominator == 1:
        return v, str(v.numerator)
    return v, f"{v.numerator}/{v.denominator}"


# ─────────────── экран калькулятора ───────────────
class CalcScreen(QWidget):
    def __init__(self, back_cb):
        super().__init__()
        self.back_cb = back_cb
        self._ans = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)

        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border:none; background:transparent; }}
            QTabBar::tab {{
                background:transparent; color:{SUB};
                padding:8px 16px; font: 10pt '{FONT_UI}';
                border:none;
            }}
            QTabBar::tab:selected {{ color:{ACCENT}; }}
        """)
        tabs.addTab(self._tab_expr(),  qta.icon("fa5s.calculator", color=SUB),  "Выражение")
        tabs.addTab(self._tab_frac(),  qta.icon("fa5s.percentage", color=SUB),  "Дроби")
        tabs.addTab(self._tab_eq(),    qta.icon("fa5s.superscript", color=SUB), "Уравнения")
        tabs.addTab(self._tab_plot(),  qta.icon("fa5s.chart-line", color=SUB),  "График")
        tabs.addTab(self._tab_table(), qta.icon("fa5s.table", color=SUB),       "Таблица")
        tabs.setCurrentIndex(0)
        self.tabs = tabs
        root.addWidget(tabs)

    def open_tab(self, idx):
        self.tabs.setCurrentIndex(idx)

    # ─────────────── 1. Выражения ───────────────
    def _tab_expr(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 10, 0, 0)
        lay.setSpacing(10)

        top = QFrame()
        top.setStyleSheet(
            f"QFrame {{ background:{PANEL}; border:none; border-radius:12px; }}")
        tl = QHBoxLayout(top)
        tl.setContentsMargins(14, 10, 14, 10)
        tl.setSpacing(10)

        self.expr = QLineEdit()
        self.expr.setPlaceholderText("2+2*sin(pi/3)   ·   sqrt(144)   ·   ans*2")
        self.expr.setStyleSheet(self._inp())
        self.expr.returnPressed.connect(self._calc)

        go = QPushButton(qta.icon("fa5s.equals", color="#0B0B0C"), " Решить")
        go.setStyleSheet(self._btn()); go.clicked.connect(self._calc)

        tl.addWidget(self.expr, 1); tl.addWidget(go)
        lay.addWidget(top)

        res_card = QFrame()
        res_card.setStyleSheet(
            f"QFrame {{ background:{PANEL}; border:none; border-radius:12px; }}")
        rl = QVBoxLayout(res_card)
        rl.setContentsMargins(20, 24, 20, 24)
        rl.setSpacing(6)

        self.res = QLabel("—")
        self.res.setStyleSheet(
            f"color:{ACCENT}; font: 700 26pt '{FONT_MONO}'; background:transparent;")
        self.res.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.res.setMinimumHeight(60)
        self.res.setWordWrap(True)

        self.err = QLabel("")
        self.err.setStyleSheet(
            f"color:#FF6B6B; font: 10pt '{FONT_MONO}'; background:transparent;")
        self.err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.err.setMinimumHeight(20)

        rl.addWidget(self.res)
        rl.addWidget(self.err)
        lay.addWidget(res_card, 1)

        hist_lbl = QLabel("История")
        hist_lbl.setStyleSheet(
            f"color:{SUB}; font: 10pt '{FONT_UI}'; background:transparent;")
        lay.addWidget(hist_lbl)

        self.history = QListWidget()
        self.history.setFixedHeight(160)
        self.history.setStyleSheet(f"""
            QListWidget {{
                background:{PANEL}; color:{TEXT}; border:none;
                border-radius:12px; padding:6px;
                font: 11pt '{FONT_MONO}'; outline:none;
            }}
            QListWidget::item {{ padding:6px 10px; border-radius:6px; }}
            QListWidget::item:selected {{ background:#1A1A1C; color:{ACCENT}; }}
        """)
        self.history.itemClicked.connect(self._from_history)
        lay.addWidget(self.history)

        return w

    def _from_history(self, item):
        txt = item.text()
        if "=" in txt:
            self.expr.setText(txt.split("=", 1)[0].strip())
            self._calc()

    def _calc(self):
        expr = self.expr.text().strip()
        if not expr:
            return

        env = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        env.update({
            "ans": self._ans,
            "pi": math.pi, "e": math.e, "tau": math.tau,
            "inf": math.inf, "nan": math.nan,
            "log": math.log10, "ln": math.log,
            "log2": math.log2, "log10": math.log10,
            "root": lambda x, n=2: x ** (1 / n),
        })

        try:
            v_frac, s_frac = try_fraction(expr)
            if v_frac is not None:
                self._ans = float(v_frac)
                self.res.setText(s_frac)
                if v_frac.denominator != 1:
                    self.err.setText(f"≈ {float(v_frac):.10g}")
                else:
                    self.err.setText("")
                self._push_history(expr, s_frac)
                return

            expr_py = expr.replace("^", "**")
            tree = ast.parse(expr_py, mode="eval")
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom, ast.Attribute)):
                    raise ValueError("запрещённая конструкция")
                if isinstance(node, ast.Call):
                    fname = getattr(node.func, "id", None)
                    if fname and fname not in env and fname not in {
                        "abs", "round", "min", "max", "sum",
                        "int", "float", "pow", "divmod",
                    }:
                        raise ValueError(f"функция '{fname}' не разрешена")

            value = eval(compile(tree, "<calc>", "eval"),
                         {"__builtins__": {
                             "abs": abs, "round": round, "min": min,
                             "max": max, "sum": sum, "int": int,
                             "float": float, "pow": pow, "divmod": divmod,
                         }},
                         env)

            if isinstance(value, float):
                out = str(int(value)) if value.is_integer() else f"{value:.10g}"
            else:
                out = str(value)

            self._ans = value
            self.res.setText(out)
            self.err.setText("")
            self._push_history(expr, out)

        except SyntaxError:
            self.res.setText("—")
            self.err.setText("не могу разобрать выражение")
        except ZeroDivisionError:
            self.res.setText("—")
            self.err.setText("деление на ноль")
        except ValueError as ve:
            self.res.setText("—")
            self.err.setText(str(ve))
        except Exception as ex:
            self.res.setText("—")
            self.err.setText(f"ошибка: {ex}")

    def _push_history(self, expr, out):
        entry = f"{expr}  =  {out}"
        for i in range(self.history.count()):
            if self.history.item(i).text() == entry:
                self.history.takeItem(i); break
        self.history.insertItem(0, entry)
        while self.history.count() > 30:
            self.history.takeItem(self.history.count() - 1)

    # ─────────────── 2. Дроби ───────────────
    def _tab_frac(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 10, 0, 0)
        lay.setSpacing(10)

        top = QFrame()
        top.setStyleSheet(
            f"QFrame {{ background:{PANEL}; border:none; border-radius:12px; }}")
        tl = QHBoxLayout(top)
        tl.setContentsMargins(14, 10, 14, 10)
        tl.setSpacing(10)

        self.frac = QLineEdit("1/2 + 3/4")
        self.frac.setPlaceholderText("1/2 + 3/4   ·   2/3 * 3/4   ·   1 1/2 + 2 1/3")
        self.frac.setStyleSheet(self._inp())
        self.frac.returnPressed.connect(self._calc_frac)

        go = QPushButton(qta.icon("fa5s.percentage", color="#0B0B0C"), " Считать")
        go.setStyleSheet(self._btn()); go.clicked.connect(self._calc_frac)

        tl.addWidget(self.frac, 1); tl.addWidget(go)
        lay.addWidget(top)

        res_card = QFrame()
        res_card.setStyleSheet(
            f"QFrame {{ background:{PANEL}; border:none; border-radius:12px; }}")
        rl = QVBoxLayout(res_card)
        rl.setContentsMargins(20, 24, 20, 24)
        rl.setSpacing(8)

        self.frac_res = QLabel("—")
        self.frac_res.setStyleSheet(
            f"color:{ACCENT}; font: 700 30pt '{FONT_MONO}'; background:transparent;")
        self.frac_res.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frac_res.setMinimumHeight(70)

        self.frac_dec = QLabel("")
        self.frac_dec.setStyleSheet(
            f"color:{SUB}; font: 12pt '{FONT_MONO}'; background:transparent;")
        self.frac_dec.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.frac_mix = QLabel("")
        self.frac_mix.setStyleSheet(
            f"color:{DIM}; font: 11pt '{FONT_MONO}'; background:transparent;")
        self.frac_mix.setAlignment(Qt.AlignmentFlag.AlignCenter)

        rl.addWidget(self.frac_res)
        rl.addWidget(self.frac_dec)
        rl.addWidget(self.frac_mix)
        lay.addWidget(res_card, 1)

        hint = QLabel(
            "Поддержка:  +  -  *  /  **  ( )   ·   смешанные дроби '1 1/2'   ·   "
            "результат всегда несократимый"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(
            f"color:{DIM}; font: 10pt '{FONT_UI}'; background:transparent;")
        lay.addWidget(hint)

        return w

    def _calc_frac(self):
        expr = self.frac.text().strip()
        if not expr:
            return
        try:
            v, s = try_fraction(expr)
            if v is None:
                self.frac_res.setText("—")
                self.frac_dec.setText("не похоже на дробное выражение")
                self.frac_mix.setText("")
                return

            self.frac_res.setText(s)

            if v.denominator == 1:
                self.frac_dec.setText(f"целое: {v.numerator}")
                self.frac_mix.setText("")
            else:
                self.frac_dec.setText(f"десятичное: ≈ {float(v):.10g}")
                sign = "-" if v < 0 else ""
                av = abs(v)
                if av.numerator > av.denominator:
                    whole = av.numerator // av.denominator
                    rem = av.numerator % av.denominator
                    self.frac_mix.setText(
                        f"смешанное: {sign}{whole} {rem}/{av.denominator}")
                else:
                    self.frac_mix.setText("")

        except ZeroDivisionError:
            self.frac_res.setText("—")
            self.frac_dec.setText("деление на ноль")
            self.frac_mix.setText("")
        except Exception as e:
            self.frac_res.setText("—")
            self.frac_dec.setText(f"ошибка: {e}")
            self.frac_mix.setText("")

    # ─────────────── 3. Уравнения ───────────────
    def _tab_eq(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 10, 0, 0)
        lay.setSpacing(10)

        top = QFrame()
        top.setStyleSheet(
            f"QFrame {{ background:{PANEL}; border:none; border-radius:12px; }}")
        tl = QHBoxLayout(top)
        tl.setContentsMargins(14, 10, 14, 10)
        tl.setSpacing(10)

        lbl = QLabel("уравнение:")
        lbl.setStyleSheet(
            f"color:{SUB}; font: 10pt '{FONT_UI}'; background:transparent;")

        self.eq = QLineEdit("x^2 - 4 = 0")
        self.eq.setPlaceholderText("x^2 - 4 = 0   ·   x^3 - 6x^2 + 11x - 6 = 0")
        self.eq.setStyleSheet(self._inp())
        self.eq.returnPressed.connect(self._solve)

        go = QPushButton(qta.icon("fa5s.play", color="#0B0B0C"), " Решить")
        go.setStyleSheet(self._btn()); go.clicked.connect(self._solve)

        tl.addWidget(lbl); tl.addWidget(self.eq, 1); tl.addWidget(go)
        lay.addWidget(top)

        self.eq_res = QLabel("—")
        self.eq_res.setWordWrap(True)
        self.eq_res.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.eq_res.setStyleSheet(f"""
            color:{TEXT}; font: 12pt '{FONT_MONO}';
            background:{PANEL}; border-radius:12px; padding:18px;
        """)
        self.eq_res.setMinimumHeight(240)
        self.eq_res.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)

        lay.addWidget(self.eq_res, 1)
        return w

    def _solve(self):
        raw = self.eq.text().strip()
        if not raw:
            return
        try:
            x = sp.Symbol("x")
            raw_py = raw.replace("^", "**")

            if "=" in raw_py:
                left, right = raw_py.split("=", 1)
                eq = sp.Eq(sp.sympify(left), sp.sympify(right))
                solutions = sp.solve(eq, x)

                lines = [f"Уравнение:  {raw}", ""]
                if not solutions:
                    lines.append("  нет решений")
                else:
                    for i, s in enumerate(solutions, 1):
                        try:
                            approx = sp.N(s, 8)
                        except Exception:
                            approx = "—"
                        lines.append(f"  x{i} = {s}")
                        if str(s) != str(approx):
                            lines.append(f"        ≈ {approx}")
            else:
                expr = sp.sympify(raw_py)
                simplified = sp.simplify(expr)
                lines = [
                    f"Выражение:  {raw}",
                    "",
                    f"  упрощённо:  {simplified}",
                    f"  значение:   {sp.N(simplified, 8)}",
                ]
                if x in simplified.free_symbols:
                    roots = sp.solve(simplified, x)
                    if roots:
                        lines.append("")
                        lines.append("  корни:")
                        for i, r in enumerate(roots, 1):
                            lines.append(f"    x{i} = {r}")

            self.eq_res.setText("\n".join(lines))

        except Exception as e:
            self.eq_res.setText(f"не могу разобрать: {e}")

    # ─────────────── 4. График ───────────────
    def _tab_plot(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 10, 0, 0)
        lay.setSpacing(10)

        top = QFrame()
        top.setStyleSheet(
            f"QFrame {{ background:{PANEL}; border:none; border-radius:12px; }}")
        top_lay = QHBoxLayout(top)
        top_lay.setContentsMargins(14, 10, 14, 10)
        top_lay.setSpacing(10)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet(
                f"color:{SUB}; font: 10pt '{FONT_UI}'; background:transparent;")
            return l

        self.fx = QLineEdit("sin(x)*x")
        self.fx.setPlaceholderText("sin(x)  ·  sin(x); cos(x); x**2/10")
        self.fx.setStyleSheet(self._inp())
        self.fx.setMinimumWidth(240)

        self.xmin = QLineEdit("-10"); self.xmin.setFixedWidth(60)
        self.xmax = QLineEdit("10");  self.xmax.setFixedWidth(60)
        self.xmin.setStyleSheet(self._inp()); self.xmax.setStyleSheet(self._inp())

        draw = QPushButton(qta.icon("fa5s.play", color="#0B0B0C"), " Построить")
        draw.setStyleSheet(self._btn()); draw.clicked.connect(self._plot)

        clear = QPushButton(qta.icon("fa5s.eraser", color=SUB), " Очистить")
        clear.setStyleSheet(self._btn2()); clear.clicked.connect(self._clear_plot)

        top_lay.addWidget(lbl("f(x) =")); top_lay.addWidget(self.fx, 1)
        top_lay.addWidget(lbl("от"));     top_lay.addWidget(self.xmin)
        top_lay.addWidget(lbl("до"));     top_lay.addWidget(self.xmax)
        top_lay.addWidget(draw); top_lay.addWidget(clear)
        lay.addWidget(top)

        self.plot = pg.PlotWidget(background=PANEL)
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.getAxis("bottom").setPen(LINE)
        self.plot.getAxis("left").setPen(LINE)
        self.plot.getAxis("bottom").setTextPen(SUB)
        self.plot.getAxis("left").setTextPen(SUB)
        self.plot.setLabel("bottom", "x")
        self.plot.setLabel("left", "f(x)")

        self.vline = pg.InfiniteLine(angle=90, movable=False,
                                     pen=pg.mkPen(SUB, style=Qt.PenStyle.DashLine))
        self.hline = pg.InfiniteLine(angle=0, movable=False,
                                     pen=pg.mkPen(SUB, style=Qt.PenStyle.DashLine))
        self.plot.addItem(self.vline, ignoreBounds=True)
        self.plot.addItem(self.hline, ignoreBounds=True)
        self.plot.scene().sigMouseMoved.connect(self._on_mouse)

        lay.addWidget(self.plot, 1)

        self.fx.returnPressed.connect(self._plot)
        self.xmin.returnPressed.connect(self._plot)
        self.xmax.returnPressed.connect(self._plot)
        return w

    def _on_mouse(self, pos):
        if not hasattr(self, "plot") or self.plot.scene() is None:
            return
        if self.plot.sceneBoundingRect().contains(pos):
            pt = self.plot.getPlotItem().vb.mapSceneToView(pos)
            self.vline.setPos(pt.x())
            self.hline.setPos(pt.y())

    def _clear_plot(self):
        self.plot.clear()
        self.plot.addItem(self.vline, ignoreBounds=True)
        self.plot.addItem(self.hline, ignoreBounds=True)

    def _plot(self):
        try:
            xmin = float(self.xmin.text()); xmax = float(self.xmax.text())
            x = np.linspace(xmin, xmax, 1500)
            allowed = {k: getattr(np, k) for k in dir(np) if not k.startswith("_")}
            allowed["x"] = x
            self._clear_plot()

            exprs = [e.strip() for e in self.fx.text().split(";") if e.strip()]
            colors = [ACCENT, "#7DD3FC", "#E0AAFF", "#FFD166", "#FF6B6B"]
            for i, expr in enumerate(exprs):
                try:
                    y = eval(expr, {"__builtins__": {}}, allowed)
                    self.plot.plot(x, y,
                                   pen=pg.mkPen(colors[i % len(colors)], width=2),
                                   name=expr)
                except Exception as e:
                    self.plot.addItem(pg.TextItem(f"{expr}: {e}", color="#FF6B6B"))
        except Exception as e:
            self._clear_plot()
            self.plot.addItem(pg.TextItem(f"ошибка: {e}", color="#FF6B6B"))

    # ─────────────── 5. Таблица ───────────────
    def _tab_table(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        top = QHBoxLayout()

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet(
                f"color:{SUB}; font: 10pt '{FONT_UI}'; background:transparent;")
            return l

        self.tfx = QLineEdit("x^2")
        self.tfx.setStyleSheet(self._inp())
        self.t_from = QLineEdit("-5"); self.t_from.setFixedWidth(60)
        self.t_to   = QLineEdit("5");  self.t_to.setFixedWidth(60)
        self.t_step = QLineEdit("1");  self.t_step.setFixedWidth(60)
        self.t_from.setStyleSheet(self._inp())
        self.t_to.setStyleSheet(self._inp())
        self.t_step.setStyleSheet(self._inp())

        go = QPushButton(qta.icon("fa5s.play", color="#0B0B0C"), " Заполнить")
        go.setStyleSheet(self._btn()); go.clicked.connect(self._fill_table)
        exp = QPushButton(qta.icon("fa5s.file-csv", color=SUB), " CSV")
        exp.setStyleSheet(self._btn2()); exp.clicked.connect(self._export_csv)

        top.addWidget(lbl("f(x) =")); top.addWidget(self.tfx)
        top.addWidget(lbl("x от"));   top.addWidget(self.t_from)
        top.addWidget(lbl("до"));     top.addWidget(self.t_to)
        top.addWidget(lbl("шаг"));    top.addWidget(self.t_step)
        top.addWidget(go); top.addWidget(exp)
        lay.addLayout(top)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["x", "f(x)"])
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background:{PANEL}; color:{TEXT}; border:none;
                border-radius:12px; gridline-color:{LINE};
                font: 11pt '{FONT_MONO}';
            }}
            QHeaderView::section {{
                background:transparent; color:{SUB};
                border:none; padding:6px; font: 10pt '{FONT_UI}';
            }}
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(self.table, 1)
        return w

    def _fill_table(self):
        try:
            fx = self.tfx.text().replace("^", "**")
            a = float(self.t_from.text()); b = float(self.t_to.text())
            step = float(self.t_step.text())
            xs = np.arange(a, b + step/2, step)
            allowed = {k: getattr(np, k) for k in dir(np) if not k.startswith("_")}
            self.table.setRowCount(len(xs))
            for i, x in enumerate(xs):
                allowed["x"] = x
                try:
                    y = eval(fx, {"__builtins__": {}}, allowed)
                except Exception:
                    y = "—"
                self.table.setItem(i, 0, QTableWidgetItem(f"{x:g}"))
                self.table.setItem(i, 1, QTableWidgetItem(f"{y}"))
        except Exception as e:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("ошибка"))
            self.table.setItem(0, 1, QTableWidgetItem(str(e)))

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить CSV", "table.csv", "*.csv")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["x", "f(x)"])
            for r in range(self.table.rowCount()):
                wr.writerow([
                    self.table.item(r, 0).text() if self.table.item(r, 0) else "",
                    self.table.item(r, 1).text() if self.table.item(r, 1) else "",
                ])

    # ─────────────── стили ───────────────
    def _inp(self):
        return f"""
            QLineEdit {{
                background:{PANEL}; color:{TEXT}; border:none;
                border-radius:8px; padding:8px 12px;
                font: 11pt '{FONT_MONO}';
                selection-background-color:{ACCENT}; selection-color:#0B0B0C;
            }}
        """

    def _btn(self):
        return f"""
            QPushButton {{
                background:{ACCENT}; color:#0B0B0C; border:none;
                border-radius:8px; padding:8px 14px;
                font: 600 10pt '{FONT_UI}';
            }}
            QPushButton:hover {{ background:#D6FF6A; }}
        """

    def _btn2(self):
        return f"""
            QPushButton {{
                background:{PANEL}; color:{SUB}; border:1px solid {LINE};
                border-radius:8px; padding:8px 14px;
                font: 600 10pt '{FONT_UI}';
            }}
            QPushButton:hover {{ color:{TEXT}; }}
        """
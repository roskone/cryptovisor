"""Оформление окна: фон с мягкими цветными пятнами, рейл с иконками, панель вкладок."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QSize
from PySide6.QtGui import QPainter, QRadialGradient, QColor, QLinearGradient, QPen, QRegion, QPainterPath, QFont
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QButtonGroup

from . import theme
from .draw import font


class Backdrop(QWidget):
    """Размытые цветные пятна на тёмном фоне — «обои» за стеклянной панелью."""

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        if theme.VARIANT == "editor":
            p.fillRect(r, theme.RAIL)
            return
        p.fillRect(r, QColor("#07080b"))
        blobs = [
            (0.12, 0.10, 0.55, "#2a3f8f"),
            (0.85, 0.15, 0.45, "#5b2e8a"),
            (0.70, 0.95, 0.55, "#1d5f7a"),
            (0.25, 0.90, 0.40, "#3b2a6b"),
        ]
        for fx, fy, fr, col in blobs:
            c = QPointF(r.width() * fx, r.height() * fy)
            g = QRadialGradient(c, max(r.width(), r.height()) * fr)
            g.setColorAt(0.0, QColor(col))
            g.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(g)
            p.drawRect(r)


class GlassPanel(QFrame):
    """Скруглённая тёмная панель с тонкой рамкой; содержимое обрезается маской."""
    RADIUS = 14

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Glass")

    def resizeEvent(self, event):
        if theme.VARIANT == "editor":
            self.clearMask()
        else:
            path = QPainterPath()
            path.addRoundedRect(QRectF(self.rect()), self.RADIUS, self.RADIUS)
            self.setMask(QRegion(path.toFillPolygon().toPolygon()))
        super().resizeEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if theme.VARIANT == "editor":
            p.fillRect(self.rect(), theme.BG)
            return
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        p.setPen(QPen(theme.BORDER, 1))
        p.setBrush(theme.BG)
        p.drawRoundedRect(r, self.RADIUS, self.RADIUS)


class Logo(QWidget):
    def __init__(self, parent=None, size: int = 30):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        if theme.VARIANT == "editor":
            # монохромный знак, как логотипы в референсах
            p.setPen(QPen(theme.TEXT, 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(r.adjusted(2, 2, -2, -2), 7, 7)
            p.setFont(font(int(r.height() * 0.45), QFont.Weight.Bold))
            p.setPen(theme.TEXT)
            p.drawText(r, Qt.AlignmentFlag.AlignCenter, "К")
            return
        g = QLinearGradient(r.topLeft(), r.bottomRight())
        g.setColorAt(0, QColor("#5b8def"))
        g.setColorAt(1, QColor("#7c4dff"))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(g)
        p.drawRoundedRect(r, 8, 8)
        p.setFont(font(int(r.height() * 0.5), QFont.Weight.Bold))
        p.setPen(QColor("#ffffff"))
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, "К")



class TabBar(QFrame):
    """Вкладки алгоритмов + справа переключатель режима и «пилюля» с номером шага."""
    algo_selected = Signal(str)
    mode_selected = Signal(bool)   # True = дешифрование
    theme_toggle = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TabBar")
        self.setFixedHeight(40)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 12, 0)
        lay.setSpacing(0)
        lay.addSpacing(10)
        lay.addWidget(Logo(size=24))
        lay.addSpacing(10)
        self.group = QButtonGroup(self)
        self.tabs: dict[str, QPushButton] = {}
        editor = theme.VARIANT == "editor"
        for key, name, glyph in (("caesar", "Цезарь", "⇄"), ("xor", "XOR", "⊕"),
                                 ("transposition", "Перестановка", "▦")):
            b = QPushButton(f"{glyph if editor else '▢'}   {name}" + ("      ×" if editor else ""))
            b.setObjectName("Tab")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            self.group.addButton(b)
            self.tabs[key] = b
            lay.addWidget(b)
            b.clicked.connect(lambda _=False, k=key: self.algo_selected.emit(k))
        lay.addStretch(1)

        self.pill = QLabel("Шаг 0 / 0")
        self.pill.setObjectName("Pill")
        lay.addWidget(self.pill)
        lay.addSpacing(12)

        self.seg_group = QButtonGroup(self)
        self.btn_enc = QPushButton("Шифрование" if editor else "◆  Шифр")
        self.btn_dec = QPushButton("Дешифрование" if editor else "◇  Дешифр")
        for b, dec in ((self.btn_enc, False), (self.btn_dec, True)):
            b.setObjectName("Seg")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            self.seg_group.addButton(b)
            lay.addWidget(b)
            b.clicked.connect(lambda _=False, d=dec: self.mode_selected.emit(d))
            lay.addSpacing(4)
        self.btn_enc.setChecked(True)
        lay.addSpacing(8)
        self.btn_theme = QPushButton("◐")
        self.btn_theme.setObjectName("Seg")
        self.btn_theme.setToolTip("Сменить тему оформления (T)")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.clicked.connect(self.theme_toggle)
        lay.addWidget(self.btn_theme)

    def sync(self, algo: str, decrypt: bool):
        self.tabs[algo].setChecked(True)
        (self.btn_dec if decrypt else self.btn_enc).setChecked(True)

    def set_step(self, pos: int, total: int):
        self.pill.setText(f"Шаг {pos} / {total}")

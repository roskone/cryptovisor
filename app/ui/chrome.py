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
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.RADIUS, self.RADIUS)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))
        super().resizeEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        p.setPen(QPen(theme.BORDER, 1))
        p.setBrush(theme.BG)
        p.drawRoundedRect(r, self.RADIUS, self.RADIUS)


class Logo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        g = QLinearGradient(r.topLeft(), r.bottomRight())
        g.setColorAt(0, QColor("#5b8def"))
        g.setColorAt(1, QColor("#7c4dff"))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(g)
        p.drawRoundedRect(r, 8, 8)
        p.setFont(font(15, QFont.Weight.Bold))
        p.setPen(QColor("#ffffff"))
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, "К")


class Rail(QFrame):
    """Узкая колонка слева: логотип и иконки-действия."""
    keys = Signal()
    fullscreen = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Rail")
        self.setFixedWidth(52)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 12, 8, 12)
        lay.setSpacing(6)
        lay.addWidget(Logo(), 0, Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(10)
        self.btn_keys = self._btn("?", "Показать / скрыть подсказку по клавишам", checkable=True)
        self.btn_keys.setChecked(True)
        self.btn_keys.clicked.connect(self.keys)
        lay.addWidget(self.btn_keys, 0, Qt.AlignmentFlag.AlignHCenter)
        lay.addStretch(1)
        self.btn_full = self._btn("⤢", "Полный экран (F)")
        self.btn_full.clicked.connect(self.fullscreen)
        lay.addWidget(self.btn_full, 0, Qt.AlignmentFlag.AlignHCenter)

    @staticmethod
    def _btn(glyph: str, tip: str, checkable: bool = False) -> QPushButton:
        b = QPushButton(glyph)
        b.setObjectName("RailBtn")
        b.setToolTip(tip)
        b.setCheckable(checkable)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        return b


class TabBar(QFrame):
    """Вкладки алгоритмов + справа переключатель режима и «пилюля» с номером шага."""
    algo_selected = Signal(str)
    mode_selected = Signal(bool)   # True = дешифрование

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TabBar")
        self.setFixedHeight(40)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 12, 0)
        lay.setSpacing(0)
        self.group = QButtonGroup(self)
        self.tabs: dict[str, QPushButton] = {}
        for key, name in (("caesar", "Цезарь"), ("xor", "XOR"), ("transposition", "Перестановка")):
            b = QPushButton(f"▢   {name}")
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
        self.btn_enc = QPushButton("◆  Шифр")
        self.btn_dec = QPushButton("◇  Дешифр")
        for b, dec in ((self.btn_enc, False), (self.btn_dec, True)):
            b.setObjectName("Seg")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            self.seg_group.addButton(b)
            lay.addWidget(b)
            b.clicked.connect(lambda _=False, d=dec: self.mode_selected.emit(d))
            lay.addSpacing(4)
        self.btn_enc.setChecked(True)

    def sync(self, algo: str, decrypt: bool):
        self.tabs[algo].setChecked(True)
        (self.btn_dec if decrypt else self.btn_enc).setChecked(True)

    def set_step(self, pos: int, total: int):
        self.pill.setText(f"Шаг {pos} / {total}")

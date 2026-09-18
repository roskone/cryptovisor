"""Примитивы рисования, общие для всех сцен."""
from __future__ import annotations

from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontDatabase, QPainterPath

from . import theme


def font(size: int, weight: int = QFont.Weight.Normal, mono: bool = False) -> QFont:
    """Unbounded для интерфейса; в теме «editor» всё «внутри редактора» — моноширинным."""
    if mono and theme.VARIANT == "editor":
        f = QFont()
        f.setFamilies(["Menlo", "Consolas", "DejaVu Sans Mono"])
        f.setStyleHint(QFont.StyleHint.Monospace)
    else:
        f = QFont(theme.FONT)
    f.setPixelSize(size)
    f.setWeight(weight)
    return f


_line_no = 0
_line_y = -1e9


def begin_lines():
    """Сбрасывает нумерацию строк гуттера перед отрисовкой сцены."""
    global _line_no, _line_y
    _line_no, _line_y = 0, -1e9


def ease(t: float) -> float:
    """Плавное замедление (ease-out cubic)."""
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a: QPointF, b: QPointF, t: float) -> QPointF:
    return QPointF(a.x() + (b.x() - a.x()) * t, a.y() + (b.y() - a.y()) * t)


def with_alpha(c: QColor, a: float) -> QColor:
    c2 = QColor(c)
    c2.setAlphaF(max(0.0, min(1.0, a)))
    return c2


def draw_background(p: QPainter, rect: QRectF, spacing: int = 24):
    p.fillRect(rect, theme.BG)
    if theme.VARIANT == "editor":
        # гуттер с номерами строк вместо точечной сетки
        p.fillRect(QRectF(0, 0, 34, rect.height()), theme.PANEL)
        p.setPen(QPen(theme.BORDER_SOFT, 1))
        p.drawLine(QPointF(34, 0), QPointF(34, rect.height()))
        return
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(theme.DOT)
    x = spacing
    while x < rect.width():
        y = spacing
        while y < rect.height():
            p.drawEllipse(QPointF(x, y), 1.2, 1.2)
            y += spacing
        x += spacing


def _gutter_number(p: QPainter, y: float):
    """Номер строки в гуттере слева (тема «editor»)."""
    global _line_no, _line_y
    if abs(y - _line_y) < 4:      # блоки на одной строке получают один номер
        return
    _line_no += 1
    _line_y = y
    p.setFont(font(11, QFont.Weight.Normal, mono=True))
    p.setPen(theme.DIM)
    p.drawText(QRectF(0, y - 13, 30, 18), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
               str(_line_no))


def draw_card(p: QPainter, rect: QRectF, title: str | None = None, radius: float = 12,
              bg: QColor | None = None, border: QColor | None = None):
    bg = bg or theme.CARD
    border = border or theme.BORDER
    if theme.VARIANT == "editor":
        # плоский блок: тонкая рамка без заливки, заголовок как комментарий кода
        p.setPen(QPen(theme.BORDER_SOFT, 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(rect, 6, 6)
        if title:
            _gutter_number(p, rect.y() + 18)
            p.setFont(font(11, QFont.Weight.Normal, mono=True))
            p.setPen(theme.DIM)
            p.drawText(QRectF(rect.x() + 14, rect.y() + 8, rect.width() - 28, 18),
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "// " + title.lower())
        return
    p.setPen(QPen(border, 1))
    p.setBrush(bg)
    p.drawRoundedRect(rect, radius, radius)
    if title:
        p.setFont(font(11, QFont.Weight.Bold))
        p.setPen(theme.MUTED)
        p.drawText(QRectF(rect.x() + 14, rect.y() + 8, rect.width() - 28, 18),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, title.upper())


def draw_label(p: QPainter, x: float, y: float, text: str, color: QColor | None = None, size: int = 11):
    if theme.VARIANT == "editor":
        _gutter_number(p, y)
        p.setFont(font(11, QFont.Weight.Normal, mono=True))
        p.setPen(theme.DIM)
        p.drawText(QPointF(x, y), "// " + text.lower())
        return
    p.setFont(font(size, QFont.Weight.Bold))
    p.setPen(color or theme.MUTED)
    p.drawText(QPointF(x, y), text.upper())


def draw_text(p: QPainter, rect: QRectF, text: str, size: int = 14, color: QColor | None = None,
              weight: int = QFont.Weight.Normal, align=Qt.AlignmentFlag.AlignCenter, mono: bool = False):
    p.setFont(font(size, weight, mono))
    p.setPen(color or theme.TEXT)
    p.drawText(rect, align, text)


def draw_cell(p: QPainter, rect: QRectF, text: str, state: tuple[QColor, QColor, QColor],
              size: int | None = None, radius: float = 8, mono: bool = False, alpha: float = 1.0,
              glow: bool = False, weight: int = QFont.Weight.DemiBold):
    bg, border, fg = state
    if theme.VARIANT == "editor":
        mono, radius, glow = True, 6, False
    if glow:
        for i, a in ((6, 0.05), (3, 0.10)):
            p.setPen(QPen(with_alpha(border, a * alpha), i * 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(rect.adjusted(-i, -i, i, i), radius + i, radius + i)
    p.setPen(QPen(with_alpha(border, alpha), 1.5 if glow else 1))
    p.setBrush(with_alpha(bg, alpha))
    p.drawRoundedRect(rect, radius, radius)
    if text:
        if size is None:
            size = int(rect.height() * 0.42)
        if text == " ":
            text, fg = "␣", theme.MUTED
        draw_text(p, rect, text, size, with_alpha(fg, alpha), weight, mono=mono)


def layout_row(x: float, y: float, n: int, avail: float, max_cell: float = 56, gap: float = 6,
               min_cell: float = 14) -> list[QRectF]:
    """Раскладывает n квадратных ячеек в строку, ужимая их при нехватке места."""
    if n <= 0:
        return []
    cell = min(max_cell, (avail - gap * (n - 1)) / n)
    cell = max(min_cell, cell)
    return [QRectF(x + i * (cell + gap), y, cell, cell) for i in range(n)]


def draw_arrow(p: QPainter, a: QPointF, b: QPointF, color: QColor, width: float = 2.5,
               curve: float = 0.0, head: float = 9):
    """Стрелка из a в b; curve > 0 — изгиб вверх (в пикселях)."""
    path = QPainterPath(a)
    if curve:
        ctrl1 = QPointF(a.x(), a.y() - curve)
        ctrl2 = QPointF(b.x(), b.y() - curve)
        path.cubicTo(ctrl1, ctrl2, b)
        # направление у конца
        tangent = QPointF(b.x() - ctrl2.x(), b.y() - ctrl2.y())
    else:
        path.lineTo(b)
        tangent = QPointF(b.x() - a.x(), b.y() - a.y())
    p.setPen(QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPath(path)
    length = (tangent.x() ** 2 + tangent.y() ** 2) ** 0.5 or 1
    ux, uy = tangent.x() / length, tangent.y() / length
    left = QPointF(b.x() - ux * head - uy * head * 0.6, b.y() - uy * head + ux * head * 0.6)
    right = QPointF(b.x() - ux * head + uy * head * 0.6, b.y() - uy * head - ux * head * 0.6)
    p.setBrush(color)
    p.setPen(Qt.PenStyle.NoPen)
    tri = QPainterPath(b)
    tri.lineTo(left)
    tri.lineTo(right)
    tri.closeSubpath()
    p.drawPath(tri)


def draw_badge(p: QPainter, center: QPointF, text: str, bg: QColor, fg: QColor | None = None, r: float = 11):
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(bg)
    p.drawEllipse(center, r, r)
    draw_text(p, QRectF(center.x() - r, center.y() - r, 2 * r, 2 * r), text, int(r * 1.1), fg or theme.BG,
              QFont.Weight.Bold)

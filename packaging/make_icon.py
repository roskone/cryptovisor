"""Генерирует иконку приложения: assets/icon.png (256px) и assets/icon.ico (16–256px).

Запуск: python packaging/make_icon.py
"""
from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QGuiApplication, QImage, QPainter, QColor, QPen, QFont, QLinearGradient, QFontDatabase

ROOT = Path(__file__).resolve().parents[1]


def render(size: int) -> QImage:
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    r = QRectF(0, 0, size, size)
    radius = size * 0.22
    # тёмная плитка с тонкой рамкой
    p.setPen(QPen(QColor("#33353d"), max(1, size * 0.02)))
    p.setBrush(QColor("#16171c"))
    p.drawRoundedRect(r.adjusted(size * 0.02, size * 0.02, -size * 0.02, -size * 0.02), radius, radius)
    # три «бита» — синий, розовый, зелёный, как ячейки в сцене
    cell = size * 0.2
    gap = size * 0.06
    total = 3 * cell + 2 * gap
    x0 = (size - total) / 2
    y0 = size * 0.28
    for i, (bg, border) in enumerate((("#18264a", "#7aa2f7"), ("#3a1628", "#f0527a"), ("#182618", "#9ece6a"))):
        rc = QRectF(x0 + i * (cell + gap), y0, cell, cell)
        p.setPen(QPen(QColor(border), max(1, size * 0.02)))
        p.setBrush(QColor(bg))
        p.drawRoundedRect(rc, cell * 0.2, cell * 0.2)
    # цифры 1 0 1 (в маленьких размерах пропускаем — нечитаемо)
    if size >= 48:
        f = QFont("Menlo")
        f.setStyleHint(QFont.StyleHint.Monospace)
        f.setPixelSize(int(cell * 0.65))
        f.setBold(True)
        p.setFont(f)
        for i, ch in enumerate("101"):
            rc = QRectF(x0 + i * (cell + gap), y0, cell, cell)
            p.setPen(QColor("#ffffff"))
            p.drawText(rc, Qt.AlignmentFlag.AlignCenter, ch)
    # нижняя полоса-«результат»
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#2a2b32"))
    p.drawRoundedRect(QRectF(x0, y0 + cell + size * 0.1, total, size * 0.08), size * 0.03, size * 0.03)
    p.setBrush(QColor("#7aa2f7"))
    p.drawRoundedRect(QRectF(x0, y0 + cell + size * 0.1, total * 0.55, size * 0.08), size * 0.03, size * 0.03)
    p.end()
    return img


def main():
    app = QGuiApplication([])
    out = ROOT / "assets"
    render(256).save(str(out / "icon.png"))
    render(512).save(str(out / "icon@2x.png"))
    # .ico: Qt пишет только один размер; собираем многоразмерный вручную (формат ICO простой)
    sizes = (16, 24, 32, 48, 64, 128, 256)
    pngs = []
    for s in sizes:
        buf = render(s)
        from PySide6.QtCore import QBuffer, QIODevice
        b = QBuffer()
        b.open(QIODevice.OpenModeFlag.WriteOnly)
        buf.save(b, "PNG")
        pngs.append(bytes(b.data()))
    import struct
    header = struct.pack("<HHH", 0, 1, len(sizes))
    offset = 6 + 16 * len(sizes)
    entries = b""
    for s, data in zip(sizes, pngs):
        entries += struct.pack("<BBBBHHII", s % 256, s % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    (out / "icon.ico").write_bytes(header + entries + b"".join(pngs))
    print("icons written to", out)


if __name__ == "__main__":
    main()

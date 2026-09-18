"""Точка входа: Криптовизор — интерактивный визуализатор шифров."""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase

from app.ui.main_window import MainWindow
from app.ui import theme


def resource_dir() -> Path:
    """Папка assets: рядом с исходниками или внутри собранного бандла (PyInstaller)."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / "assets"


def load_fonts():
    for ttf in sorted((resource_dir() / "fonts").glob("*.ttf")):
        QFontDatabase.addApplicationFont(str(ttf))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Криптовизор")
    app.setStyle("Fusion")
    load_fonts()
    f = QFont("Unbounded")
    f.setPixelSize(12)
    app.setFont(f)
    app.setStyleSheet(theme.QSS)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

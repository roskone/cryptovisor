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


THEMES = ("glass", "editor")


class App:
    """Держит текущее окно и пересоздаёт его при смене темы, сохраняя параметры."""

    def __init__(self, app: QApplication, variant: str):
        self.app = app
        self.win: MainWindow | None = None
        self.switch(variant)

    def switch(self, variant: str):
        theme.apply(variant)
        self.app.setStyleSheet(theme.QSS)
        old = self.win
        win = MainWindow()
        win.theme_toggle.connect(self.toggle)
        if old is not None:
            win.sidebar.set_params(old.sidebar.params())
            win.setGeometry(old.geometry())
            if old.isFullScreen():
                win.showFullScreen()
            else:
                win.show()
            win.go_to(old.pos)
            old.close()
        else:
            win.show()
        self.win = win

    def toggle(self):
        cur = THEMES.index(theme.VARIANT)
        self.switch(THEMES[(cur + 1) % len(THEMES)])


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Криптовизор")
    app.setStyle("Fusion")
    load_fonts()
    f = QFont("Unbounded")
    f.setPixelSize(12)
    app.setFont(f)
    variant = "editor" if "--editor" in sys.argv else "glass"
    holder = App(app, variant)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

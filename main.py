"""Точка входа: Криптовизор — интерактивный визуализатор шифров."""
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from app.ui.main_window import MainWindow
from app.ui.theme import QSS


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Криптовизор")
    app.setStyle("Fusion")
    app.setStyleSheet(QSS)
    f = app.font()
    f.setPixelSize(14)
    app.setFont(f)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

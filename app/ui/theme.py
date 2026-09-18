"""Палитра и таблица стилей (QSS) приложения."""
from PySide6.QtGui import QColor

BG = QColor("#0e1014")
PANEL = QColor("#14171d")
CARD = QColor("#191d25")
BORDER = QColor("#282d38")
TEXT = QColor("#e8eaf0")
MUTED = QColor("#8a90a0")
ACCENT = QColor("#7c9cff")
YELLOW = QColor("#ffd166")
GREEN = QColor("#4ade80")
RED = QColor("#f87171")
PINK = QColor("#f472b6")
DOT = QColor("#232833")

# Состояния ячеек: (фон, рамка, текст)
CELL_FUTURE = (QColor("#181c24"), QColor("#2a2f3a"), QColor("#6f7585"))
CELL_DONE = (QColor("#12271b"), QColor("#2f7a4a"), QColor("#d9fbe5"))
CELL_CURRENT = (QColor("#3a3110"), QColor("#ffd166"), QColor("#ffffff"))
CELL_KEY = (QColor("#1a2240"), QColor("#7c9cff"), QColor("#dfe6ff"))
CELL_KEY_CURRENT = (QColor("#27346a"), QColor("#a9bdff"), QColor("#ffffff"))
CELL_EMPTY = (QColor("#13161c"), QColor("#232833"), QColor("#4a5060"))

QSS = """
QWidget {
    color: #e8eaf0;
    font-family: ".AppleSystemUIFont", "Segoe UI", sans-serif;
    font-size: 14px;
}
QMainWindow, QStackedWidget#Scenes { background: #0e1014; }
QFrame#Sidebar { background: #14171d; border-right: 1px solid #282d38; }
QFrame#Transport { background: #14171d; border-top: 1px solid #282d38; }
QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; }

QLabel#AppTitle { font-size: 19px; font-weight: 700; letter-spacing: 0.2px; }
QLabel#AppSubtitle { color: #8a90a0; font-size: 12px; }
QLabel#Section { color: #8a90a0; font-size: 11px; font-weight: 700; letter-spacing: 1.2px; margin-top: 6px; }
QLabel#Hint { color: #6f7585; font-size: 12px; }
QLabel#Kbd { color: #8a90a0; font-size: 12px; }
QLabel#StepCounter { color: #8a90a0; font-size: 13px; }
QLabel#StepText { font-size: 20px; padding: 2px 4px; }
QLabel#Error { color: #f87171; font-size: 16px; }

QLineEdit, QSpinBox {
    background: #191d25; border: 1px solid #2a2f3a; border-radius: 8px;
    padding: 8px 10px; font-size: 15px; selection-background-color: #7c9cff;
}
QLineEdit:focus, QSpinBox:focus { border-color: #7c9cff; }
QSpinBox::up-button, QSpinBox::down-button { width: 0; border: none; }

QPushButton {
    background: #1c2029; border: 1px solid #2a2f3a; border-radius: 8px;
    padding: 8px 12px; color: #e8eaf0;
}
QPushButton:hover { background: #242938; }
QPushButton:pressed { background: #1a1e28; }
QPushButton:checked { background: #26325a; border-color: #7c9cff; color: #ffffff; }
QPushButton:disabled { color: #4a5060; border-color: #22262f; }

QPushButton#Algo { text-align: left; padding: 11px 14px; font-size: 15px; font-weight: 600; }
QPushButton#Seg { padding: 7px 8px; font-weight: 600; }
QPushButton#Transport { font-size: 18px; min-width: 44px; min-height: 40px; padding: 4px 10px; }
QPushButton#Play { font-size: 15px; font-weight: 700; min-height: 40px; padding: 4px 18px;
                   background: #7c9cff; color: #0e1014; border: none; }
QPushButton#Play:hover { background: #93adff; }
QPushButton#Play:checked { background: #ffd166; color: #0e1014; }

QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 5px; border: 1px solid #2a2f3a; background: #191d25; }
QCheckBox::indicator:checked { background: #7c9cff; border-color: #7c9cff; }
QRadioButton { spacing: 8px; }
QRadioButton::indicator { width: 16px; height: 16px; border-radius: 8px; border: 1px solid #2a2f3a; background: #191d25; }
QRadioButton::indicator:checked { background: #7c9cff; border: 4px solid #191d25; outline: 1px solid #7c9cff; }

QSlider::groove:horizontal { height: 4px; background: #2a2f3a; border-radius: 2px; }
QSlider::handle:horizontal { width: 16px; height: 16px; margin: -6px 0; background: #7c9cff; border-radius: 8px; }
QSlider::sub-page:horizontal { background: #7c9cff; border-radius: 2px; }

QScrollArea { border: none; }
QScrollBar:vertical { width: 8px; background: transparent; }
QScrollBar::handle:vertical { background: #2a2f3a; border-radius: 4px; min-height: 30px; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QToolTip { background: #191d25; color: #e8eaf0; border: 1px solid #2a2f3a; padding: 4px 8px; }
"""

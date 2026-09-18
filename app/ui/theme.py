"""Палитра и таблица стилей (QSS). Стиль: тёмная «стеклянная» IDE-панель."""
from PySide6.QtGui import QColor

FONT = "Unbounded"

# Базовые поверхности
BG = QColor("#0d0f12")          # редактор / сцена
PANEL = QColor("#171a1f")       # боковая панель
RAIL = QColor("#121417")        # узкий рейл с иконками
CARD = QColor("#14171b")
BORDER = QColor("#2a2e35")
BORDER_SOFT = QColor("#1f2329")
TEXT = QColor("#e6e8ec")
MUTED = QColor("#8b909a")
DIM = QColor("#5b6068")
DOT = QColor("#1c2026")

# Акценты (как в референсе: синий для активного, оранжевый для «строк»/ключа, зелёный для готового)
ACCENT = QColor("#5b8def")
ACCENT_SOFT = QColor("#2b3f6b")
WARM = QColor("#e8a86b")
GREEN = QColor("#5ccb7e")
RED = QColor("#f2707a")

# Состояния ячеек: (фон, рамка, текст)
CELL_FUTURE = (QColor("#15181c"), QColor("#262a31"), QColor("#6a6f78"))
CELL_DONE = (QColor("#122219"), QColor("#2f6b45"), QColor("#d9f5e2"))
CELL_CURRENT = (QColor("#1a2a4d"), QColor("#5b8def"), QColor("#ffffff"))
CELL_KEY = (QColor("#2a1f14"), QColor("#7a5230"), QColor("#f3d5b5"))
CELL_KEY_CURRENT = (QColor("#3d2a15"), QColor("#e8a86b"), QColor("#ffffff"))
CELL_EMPTY = (QColor("#111316"), QColor("#1f2329"), QColor("#44494f"))

QSS = f"""
QWidget {{
    color: #e6e8ec;
    font-family: "{FONT}";
    font-size: 12px;
    font-weight: 400;
}}
QMainWindow {{ background: #0d0f12; }}
QWidget#Glass {{ background: transparent; }}

/* ── рейл ── */
QFrame#Rail {{ background: #121417; border-right: 1px solid #22262c; }}
QPushButton#RailBtn {{
    background: transparent; border: none; border-radius: 8px;
    min-width: 36px; max-width: 36px; min-height: 36px; max-height: 36px;
    font-size: 16px; color: #8b909a;
}}
QPushButton#RailBtn:hover {{ background: #1d2127; color: #e6e8ec; }}
QPushButton#RailBtn:checked {{ background: #1f2a44; color: #9dbcff; }}

/* ── боковая панель ── */
QFrame#Sidebar {{ background: #171a1f; border-right: 1px solid #22262c; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; }}
QLabel#PanelTitle {{ font-size: 12px; font-weight: 500; color: #e6e8ec; }}
QLabel#SectionHead {{ font-size: 11px; font-weight: 500; color: #c9cdd4; }}
QFrame#SectionLine {{ background: #22262c; max-height: 1px; min-height: 1px; border: none; }}
QLabel#Hint {{ color: #6f747d; font-size: 10px; font-weight: 300; }}
QLabel#Kbd {{ color: #9aa0a9; font-size: 10px; font-weight: 400; }}
QLabel#KbdDesc {{ color: #6f747d; font-size: 10px; font-weight: 300; }}
QLabel#FieldLabel {{ color: #8b909a; font-size: 10px; }}

QPushButton#Item {{
    background: transparent; border: none; border-radius: 6px; text-align: left;
    padding: 6px 10px; font-size: 11px; color: #c9cdd4;
}}
QPushButton#Item:hover {{ background: #1f2329; color: #e6e8ec; }}
QPushButton#Item:checked {{ background: #1f2a44; color: #ffffff; }}

QLineEdit, QSpinBox {{
    background: #0f1114; border: 1px solid #2a2e35; border-radius: 6px;
    padding: 7px 10px; font-size: 12px; selection-background-color: #5b8def;
}}
QLineEdit:focus, QSpinBox:focus {{ border-color: #5b8def; }}
QLineEdit:disabled, QSpinBox:disabled {{ color: #5b6068; border-color: #1f2329; }}
QSpinBox::up-button, QSpinBox::down-button {{ width: 0; border: none; }}

QCheckBox {{ spacing: 8px; font-size: 11px; color: #c9cdd4; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 1px solid #2a2e35; background: #0f1114; }}
QCheckBox::indicator:checked {{ background: #5b8def; border-color: #5b8def; }}
QRadioButton {{ spacing: 8px; font-size: 11px; color: #c9cdd4; }}
QRadioButton::indicator {{ width: 14px; height: 14px; border-radius: 7px; border: 1px solid #2a2e35; background: #0f1114; }}
QRadioButton::indicator:checked {{ background: #5b8def; border: 3px solid #0f1114; outline: 1px solid #5b8def; }}

/* ── вкладки ── */
QFrame#TabBar {{ background: #121417; border-bottom: 1px solid #22262c; }}
QPushButton#Tab {{
    background: transparent; border: none; border-right: 1px solid #22262c; border-radius: 0;
    padding: 0 18px; min-height: 38px; font-size: 11px; color: #8b909a;
}}
QPushButton#Tab:hover {{ color: #e6e8ec; background: #16191e; }}
QPushButton#Tab:checked {{ color: #ffffff; background: #0d0f12; border-bottom: 2px solid #5b8def; }}
QLabel#Pill {{
    background: #1a1d22; border: 1px solid #2a2e35; border-radius: 14px;
    padding: 5px 14px; font-size: 10px; color: #c9cdd4;
}}
QPushButton#Seg {{
    background: transparent; border: 1px solid #2a2e35; border-radius: 6px;
    padding: 4px 10px; font-size: 10px; color: #8b909a;
}}
QPushButton#Seg:checked {{ background: #1f2a44; border-color: #3b5590; color: #ffffff; }}
QPushButton#Seg:hover {{ color: #e6e8ec; }}

/* ── транспорт ── */
QFrame#Transport {{ background: #121417; border-top: 1px solid #22262c; }}
QLabel#StepText {{ font-size: 16px; font-weight: 400; padding: 2px 4px; }}
QLabel#Error {{ color: #f2707a; font-size: 14px; }}
QLabel#StepCounter {{ color: #8b909a; font-size: 11px; }}
QPushButton#Transport {{
    background: #1a1d22; border: 1px solid #2a2e35; border-radius: 8px;
    font-size: 15px; min-width: 42px; min-height: 36px; padding: 2px 8px; color: #e6e8ec;
}}
QPushButton#Transport:hover {{ background: #22262c; }}
QPushButton#Transport:disabled {{ color: #44494f; border-color: #1f2329; }}
QPushButton#Play {{
    font-size: 12px; font-weight: 500; min-height: 36px; padding: 2px 18px;
    background: #5b8def; color: #ffffff; border: none; border-radius: 8px;
}}
QPushButton#Play:hover {{ background: #6f9cf5; }}
QPushButton#Play:checked {{ background: #e8a86b; color: #14171b; }}
QPushButton#Play:disabled {{ background: #1f2329; color: #44494f; }}

QSlider::groove:horizontal {{ height: 3px; background: #2a2e35; border-radius: 1px; }}
QSlider::handle:horizontal {{ width: 14px; height: 14px; margin: -6px 0; background: #5b8def; border-radius: 7px; }}
QSlider::sub-page:horizontal {{ background: #5b8def; border-radius: 1px; }}

QScrollBar:vertical {{ width: 6px; background: transparent; }}
QScrollBar::handle:vertical {{ background: #2a2e35; border-radius: 3px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QToolTip {{ background: #1a1d22; color: #e6e8ec; border: 1px solid #2a2e35; padding: 4px 8px; font-size: 10px; }}
"""

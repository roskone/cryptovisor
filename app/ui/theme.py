"""Палитра и QSS: плоский тёмный редактор кода."""
from PySide6.QtGui import QColor

FONT = "Unbounded"
MONO = "Menlo, Consolas, monospace"

_C = QColor


def _cells(future, done, current, key, key_current, empty):
    return dict(CELL_FUTURE=future, CELL_DONE=done, CELL_CURRENT=current, CELL_KEY=key,
                CELL_KEY_CURRENT=key_current, CELL_EMPTY=empty)


PALETTES = {
    "editor": dict(
        BG=_C("#131418"), PANEL=_C("#0f1013"), RAIL=_C("#0c0d10"), CARD=_C("#16171c"),
        BORDER=_C("#262830"), BORDER_SOFT=_C("#1e2026"), TEXT=_C("#e8e8ea"), MUTED=_C("#8b8b94"),
        DIM=_C("#5a5b64"), DOT=_C("#1a1b20"),
        ACCENT=_C("#7aa2f7"), ACCENT_SOFT=_C("#1c2745"), WARM=_C("#f0527a"), GREEN=_C("#9ece6a"),
        RED=_C("#f7768e"), AMBER=_C("#e0af68"),
        **_cells((_C("#1a1b21"), _C("#2c2e37"), _C("#767880")),
                 (_C("#182618"), _C("#4a7a3a"), _C("#d9f0c8")),
                 (_C("#18264a"), _C("#7aa2f7"), _C("#ffffff")),
                 (_C("#2c161f"), _C("#7a2a44"), _C("#f5c6d4")),
                 (_C("#3a1628"), _C("#f0527a"), _C("#ffffff")),
                 (_C("#111216"), _C("#22232a"), _C("#44454d"))),
    ),
}

QSS = ""


def hexs(c: QColor) -> str:
    return c.name()


def _build_qss() -> str:
    P = PALETTES["editor"]
    h = {k: c.name() for k, c in P.items() if isinstance(c, QColor)}
    editor = True
    radius = "6px" if editor else "8px"
    row_sel = "#1f2026" if editor else "#1f2a44"
    row_sel_text = "#ffffff"
    tab_active_bg = h["BG"] if editor else h["BG"]
    tab_border = f"border-bottom: 2px solid {h['ACCENT']};" if not editor else "border-bottom: none;"
    play_bg = h["WARM"] if editor else h["ACCENT"]
    play_fg = "#ffffff"
    play_checked = h["AMBER"]
    pill_radius = "14px"
    seg_radius = "12px" if editor else "6px"
    seg_bg = "#16171c" if editor else "transparent"
    seg_checked = "#2a2b32" if editor else "#1f2a44"
    seg_checked_border = "#34363e" if editor else "#3b5590"
    return f"""
QWidget {{ color: {h['TEXT']}; font-family: "{FONT}"; font-size: 12px; font-weight: 400; }}
QMainWindow {{ background: {h['BG']}; }}
QWidget#Glass {{ background: transparent; }}

QFrame#Rail {{ background: {h['RAIL']}; border-right: 1px solid {h['BORDER']}; }}
QPushButton#RailBtn {{
    background: transparent; border: none; border-radius: 8px;
    min-width: 36px; max-width: 36px; min-height: 36px; max-height: 36px;
    font-size: 16px; color: {h['MUTED']};
}}
QPushButton#RailBtn:hover {{ background: {row_sel}; color: {h['TEXT']}; }}
QPushButton#RailBtn:checked {{ background: {row_sel}; color: {h['TEXT']}; }}

QFrame#Sidebar {{ background: {h['PANEL']}; border-right: 1px solid {h['BORDER']}; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; }}
QLabel#PanelTitle {{ font-size: 12px; font-weight: 500; color: {h['TEXT']}; }}
QLabel#SectionHead {{ font-size: {'9px' if editor else '11px'}; font-weight: 500; color: {h['DIM'] if editor else '#c9cdd4'}; }}
QFrame#SectionLine {{ background: {h['BORDER']}; max-height: 1px; min-height: 1px; border: none; }}
QLabel#Hint {{ color: {h['DIM']}; font-size: 10px; font-weight: 300; }}
QLabel#Kbd {{ color: {h['MUTED']}; font-size: 10px; }}
QLabel#KbdDesc {{ color: {h['DIM']}; font-size: 10px; font-weight: 300; }}
QLabel#FieldLabel {{ color: {h['MUTED']}; font-size: 10px; }}

QPushButton#Item {{
    background: transparent; border: none; border-radius: {radius}; text-align: left;
    padding: {'7px 10px' if editor else '6px 10px'}; font-size: 11px; color: {h['MUTED'] if editor else '#c9cdd4'};
}}
QPushButton#Item:hover {{ background: {h['BORDER_SOFT']}; color: {h['TEXT']}; }}
QPushButton#Item:checked {{ background: {row_sel}; color: {row_sel_text}; }}

QLineEdit, QSpinBox {{
    background: {h['BG']}; border: 1px solid {h['BORDER']}; border-radius: {radius};
    padding: 7px 10px; font-size: 12px; selection-background-color: {h['ACCENT']};
    {'font-family: ' + MONO + ';' if editor else ''}
}}
QLineEdit:focus, QSpinBox:focus {{ border-color: {h['ACCENT']}; }}
QLineEdit:disabled, QSpinBox:disabled {{ color: {h['DIM']}; border-color: {h['BORDER_SOFT']}; }}
QSpinBox::up-button, QSpinBox::down-button {{ width: 0; border: none; }}

QCheckBox {{ spacing: 8px; font-size: 11px; color: {h['TEXT']}; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 1px solid {h['BORDER']}; background: {h['BG']}; }}
QCheckBox::indicator:checked {{ background: {h['ACCENT']}; border-color: {h['ACCENT']}; }}
QRadioButton {{ spacing: 8px; font-size: 11px; color: {h['TEXT']}; }}
QRadioButton::indicator {{ width: 14px; height: 14px; border-radius: 7px; border: 1px solid {h['BORDER']}; background: {h['BG']}; }}
QRadioButton::indicator:checked {{ background: {h['ACCENT']}; border: 3px solid {h['BG']}; outline: 1px solid {h['ACCENT']}; }}

QFrame#TabBar {{ background: {h['RAIL'] if editor else '#121417'}; border-bottom: 1px solid {h['BORDER']}; }}
QPushButton#Tab {{
    background: transparent; border: none; border-right: 1px solid {h['BORDER']}; border-radius: 0;
    padding: 0 16px; min-height: 38px; font-size: 11px; color: {h['MUTED']};
}}
QPushButton#Tab:hover {{ color: {h['TEXT']}; background: {h['BORDER_SOFT']}; }}
QPushButton#Tab:checked {{ color: #ffffff; background: {tab_active_bg}; {tab_border} }}
QLabel#Pill {{
    background: {seg_bg if editor else '#1a1d22'}; border: 1px solid {h['BORDER']}; border-radius: {pill_radius};
    padding: 5px 14px; font-size: 10px; color: {h['TEXT']};
}}
QPushButton#Seg {{
    background: {seg_bg}; border: 1px solid {h['BORDER']}; border-radius: {seg_radius};
    padding: 4px 12px; font-size: 10px; color: {h['MUTED']};
}}
QPushButton#Seg:checked {{ background: {seg_checked}; border-color: {seg_checked_border}; color: #ffffff; }}
QPushButton#Seg:hover {{ color: {h['TEXT']}; }}

QFrame#Transport {{ background: {h['RAIL'] if editor else '#121417'}; border-top: 1px solid {h['BORDER']}; }}
QPushButton#BottomTab {{
    background: transparent; border: none; border-bottom: 2px solid transparent; border-radius: 0;
    padding: 6px 2px; margin-right: 18px; font-size: 9px; color: {h['DIM']};
}}
QPushButton#BottomTab:hover {{ color: {h['TEXT']}; }}
QPushButton#BottomTab:checked {{ color: {h['TEXT']}; border-bottom: 2px solid {h['AMBER']}; }}
QLabel#StepText {{ font-size: {'15px' if editor else '16px'}; padding: 2px 4px; {'font-family: ' + MONO + ';' if editor else ''} }}
QLabel#Error {{ color: {h['RED']}; font-size: 14px; }}
QLabel#StepCounter {{ color: {h['MUTED']}; font-size: 11px; }}
QListWidget#Journal {{
    background: transparent; border: none; font-family: {MONO}; font-size: 12px; color: {h['MUTED']};
    outline: none;
}}
QListWidget#Journal::item {{ padding: 1px 6px; border: none; }}
QListWidget#Journal::item:selected {{ background: #1f3d22; color: {h['TEXT']}; }}
QPushButton#Transport {{
    background: {'#16171c' if editor else '#1a1d22'}; border: 1px solid {h['BORDER']}; border-radius: {radius};
    font-size: 15px; min-width: 42px; min-height: 36px; padding: 2px 8px; color: {h['TEXT']};
}}
QPushButton#Transport:hover {{ background: {row_sel}; }}
QPushButton#Transport:disabled {{ color: {h['DIM']}; border-color: {h['BORDER_SOFT']}; }}
QPushButton#Play {{
    font-size: 12px; font-weight: 500; min-height: 36px; padding: 2px 18px;
    background: {play_bg}; color: {play_fg}; border: none; border-radius: {radius};
}}
QPushButton#Play:hover {{ background: {h['ACCENT']}; }}
QPushButton#Play:checked {{ background: {play_checked}; color: #111111; }}
QPushButton#Play:disabled {{ background: {h['BORDER_SOFT']}; color: {h['DIM']}; }}

QSlider::groove:horizontal {{ height: 3px; background: {h['BORDER']}; border-radius: 1px; }}
QSlider::handle:horizontal {{ width: 14px; height: 14px; margin: -6px 0; background: {h['ACCENT']}; border-radius: 7px; }}
QSlider::sub-page:horizontal {{ background: {h['ACCENT']}; border-radius: 1px; }}

QScrollBar:vertical {{ width: 6px; background: transparent; }}
QScrollBar::handle:vertical {{ background: {h['BORDER']}; border-radius: 3px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QToolTip {{ background: {h['PANEL']}; color: {h['TEXT']}; border: 1px solid {h['BORDER']}; padding: 4px 8px; font-size: 10px; }}
"""


globals().update(PALETTES["editor"])
QSS = _build_qss()

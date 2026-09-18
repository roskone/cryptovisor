"""Панель вкладок над сценой."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel, QButtonGroup



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
        for key, name, glyph in (("caesar", "Цезарь", "⇄"), ("xor", "XOR", "⊕"),
                                 ("transposition", "Перестановка", "▦")):
            b = QPushButton(f"{glyph}   {name}      ×")
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
        self.btn_enc = QPushButton("Шифрование")
        self.btn_dec = QPushButton("Дешифрование")
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

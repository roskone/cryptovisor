"""Левая панель в стиле дерева проекта: секции с «▾», строки-элементы, поля ввода."""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup,
                               QLineEdit, QSpinBox, QWidget, QCheckBox, QRadioButton,
                               QSizePolicy, QScrollArea)


@dataclass
class Params:
    algo: str            # caesar | xor | transposition
    text: str
    decrypt: bool
    caesar_shift: int
    xor_key_mode: str    # num | str
    xor_key_num: int
    xor_key_str: str
    trans_key: str
    major_steps: bool


ALGOS = [
    ("caesar", "Шифр Цезаря", "#9ece6a"),
    ("xor", "XOR", "#bb9af7"),
    ("transposition", "Перестановка", "#ff9e64"),
]

HOTKEYS = [
    ("Пробел / →", "шаг вперёд"),
    ("←", "шаг назад"),
    ("Home / End", "в начало / в конец"),
    ("Enter", "авто-режим"),
    ("+ / −", "быстрее / медленнее"),
    ("1 · 2 · 3", "алгоритм"),
    ("E / D", "шифр / дешифр"),
    ("M", "крупные шаги"),
    ("F", "полный экран"),
    ("Esc", "выйти из поля"),
]


class PageSwitch(QWidget):
    """Контейнер страниц: видима только одна, остальные скрыты и не занимают места."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)
        self._pages: list[QWidget] = []

    def addWidget(self, w: QWidget):
        self._pages.append(w)
        self._lay.addWidget(w)
        w.setVisible(len(self._pages) == 1)

    def setCurrentIndex(self, idx: int):
        for i, w in enumerate(self._pages):
            w.setVisible(i == idx)


class Section(QWidget):
    """Секция дерева: заголовок «▾ Название» + содержимое с отступом, линия-разделитель снизу."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        head = QLabel(f"▾   {title.upper()}")
        head.setObjectName("SectionHead")
        head.setContentsMargins(12, 10, 12, 8)
        lay.addWidget(head)
        self.body = QWidget()
        self.body_lay = QVBoxLayout(self.body)
        self.body_lay.setContentsMargins(14, 0, 12, 12)
        self.body_lay.setSpacing(6)
        lay.addWidget(self.body)
        line = QFrame()
        line.setObjectName("SectionLine")
        lay.addWidget(line)

    def add(self, w):
        if isinstance(w, QWidget):
            self.body_lay.addWidget(w)
        else:
            self.body_lay.addLayout(w)


def dot_icon(color: str, size: int = 10) -> QIcon:
    pm = QPixmap(size * 2, size * 2)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(color))
    p.drawEllipse(size // 2, size // 2, size, size)
    p.end()
    return QIcon(pm)


def item_button(text: str, dot: str) -> QPushButton:
    """Строка-элемент с цветной точкой-статусом."""
    b = QPushButton(text)
    b.setIcon(dot_icon(dot))
    b.setIconSize(QSize(20, 20))
    b.setObjectName("Item")
    b.setCheckable(True)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b


def hint(text: str) -> QLabel:
    h = QLabel(text)
    h.setObjectName("Hint")
    h.setWordWrap(True)
    return h


def field_label(text: str) -> QLabel:
    lab = QLabel(text)
    lab.setObjectName("FieldLabel")
    return lab


class Sidebar(QFrame):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(250)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # заголовок панели, как «Page Code ⓘ»
        head = QWidget()
        hl = QHBoxLayout(head)
        hl.setContentsMargins(14, 12, 12, 10)
        title = QLabel("Параметры")
        title.setObjectName("PanelTitle")
        info = QLabel("ⓘ")
        info.setObjectName("Hint")
        info.setToolTip("Всё пересчитывается автоматически при вводе")
        hl.addWidget(title)
        hl.addStretch(1)
        hl.addWidget(info)
        outer.addWidget(head)
        line = QFrame()
        line.setObjectName("SectionLine")
        outer.addWidget(line)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        inner = QWidget()
        scroll.setWidget(inner)
        outer.addWidget(scroll, 1)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Алгоритм ──
        sec = Section("Алгоритм")
        self.algo_group = QButtonGroup(self)
        self.algo_buttons: dict[str, QPushButton] = {}
        for key, name, dot in ALGOS:
            btn = item_button(name, dot)
            self.algo_group.addButton(btn)
            self.algo_buttons[key] = btn
            sec.add(btn)
        self.algo_buttons["caesar"].setChecked(True)
        self.algo_group.buttonClicked.connect(self._on_algo)
        lay.addWidget(sec)

        # ── Режим ──
        sec = Section("Режим")
        self.btn_enc = item_button("Шифровать", "#7aa2f7")
        self.btn_dec = item_button("Дешифровать", "#f0527a")
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.btn_enc)
        self.mode_group.addButton(self.btn_dec)
        self.btn_enc.setChecked(True)
        self.mode_group.buttonClicked.connect(lambda _: self._emit())
        sec.add(self.btn_enc)
        sec.add(self.btn_dec)
        lay.addWidget(sec)

        # ── Текст ──
        sec = Section("Текст")
        self.text = QLineEdit("Привет, мир!")
        self.text.setMaxLength(40)
        self.text.setPlaceholderText("до 40 символов")
        self.text.textChanged.connect(self._emit)
        sec.add(self.text)
        self.text_hint = hint("")
        sec.add(self.text_hint)
        lay.addWidget(sec)

        # ── Ключ ──
        sec = Section("Ключ")
        self.key_stack = PageSwitch()
        sec.add(self.key_stack)
        lay.addWidget(sec)

        # Цезарь
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)
        row = QHBoxLayout()
        row.addWidget(field_label("Сдвиг"))
        self.caesar_shift = QSpinBox()
        self.caesar_shift.setRange(-32, 32)
        self.caesar_shift.setValue(3)
        self.caesar_shift.valueChanged.connect(self._emit)
        row.addWidget(self.caesar_shift, 1)
        v.addLayout(row)
        v.addWidget(hint("Латиница — 26 букв, кириллица — 33 (с Ё). Регистр сохраняется."))
        self.key_stack.addWidget(w)

        # XOR
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)
        self.xor_num_radio = QRadioButton("Число 0–255")
        self.xor_str_radio = QRadioButton("Строка (циклически)")
        self.xor_str_radio.setChecked(True)
        v.addWidget(self.xor_num_radio)
        self.xor_key_num = QSpinBox()
        self.xor_key_num.setRange(0, 255)
        self.xor_key_num.setValue(42)
        v.addWidget(self.xor_key_num)
        v.addWidget(self.xor_str_radio)
        self.xor_key_str = QLineEdit("ключ")
        self.xor_key_str.setMaxLength(16)
        v.addWidget(self.xor_key_str)
        v.addWidget(hint("CP1251: 1 символ = 1 байт. При дешифровании можно ввести hex «4A 2F …»."))
        self.xor_num_radio.toggled.connect(self._sync_xor)
        self.xor_key_num.valueChanged.connect(self._emit)
        self.xor_key_str.textChanged.connect(self._emit)
        self.key_stack.addWidget(w)

        # Перестановка
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)
        self.trans_key = QLineEdit("КЛЮЧ")
        self.trans_key.setMaxLength(10)
        self.trans_key.setPlaceholderText("слово или цифры, напр. 3142")
        self.trans_key.textChanged.connect(self._emit)
        v.addWidget(self.trans_key)
        v.addWidget(hint("Слово — столбцы нумеруются по алфавиту букв ключа. Цифры — явный порядок чтения."))
        self.key_stack.addWidget(w)

        # ── Показ ──
        sec = Section("Показ")
        self.major = QCheckBox("Крупные шаги")
        self.major.setToolTip("По символу / байту / столбцу вместо бита и ячейки (M)")
        self.major.toggled.connect(self._emit)
        sec.add(self.major)
        lay.addWidget(sec)

        lay.addStretch(1)

        self._sync_xor()
        self._on_algo(None)

    # ── события ──
    def _on_algo(self, _btn):
        self.key_stack.setCurrentIndex(list(self.algo_buttons).index(self.algo()))
        self._emit()

    def _sync_xor(self):
        num = self.xor_num_radio.isChecked()
        self.xor_key_num.setEnabled(num)
        self.xor_key_str.setEnabled(not num)
        self._emit()

    def _emit(self, *_):
        self.changed.emit()

    # ── публичное API ──
    def algo(self) -> str:
        for key, btn in self.algo_buttons.items():
            if btn.isChecked():
                return key
        return "caesar"

    def set_algo(self, key: str):
        self.algo_buttons[key].setChecked(True)
        self._on_algo(None)

    def set_decrypt(self, dec: bool):
        (self.btn_dec if dec else self.btn_enc).setChecked(True)
        self._emit()

    def toggle_major(self):
        self.major.setChecked(not self.major.isChecked())

    def set_params(self, prm: Params):
        """Восстанавливает состояние (используется при смене темы)."""
        self.blockSignals(True)
        self.text.setText(prm.text)
        self.caesar_shift.setValue(prm.caesar_shift)
        (self.xor_num_radio if prm.xor_key_mode == "num" else self.xor_str_radio).setChecked(True)
        self.xor_key_num.setValue(prm.xor_key_num)
        self.xor_key_str.setText(prm.xor_key_str)
        self.trans_key.setText(prm.trans_key)
        self.major.setChecked(prm.major_steps)
        (self.btn_dec if prm.decrypt else self.btn_enc).setChecked(True)
        self.algo_buttons[prm.algo].setChecked(True)
        self.blockSignals(False)
        self._on_algo(None)

    def set_text_hint(self, text: str):
        self.text_hint.setText(text)
        self.text_hint.setVisible(bool(text))

    def params(self) -> Params:
        return Params(
            algo=self.algo(),
            text=self.text.text(),
            decrypt=self.btn_dec.isChecked(),
            caesar_shift=self.caesar_shift.value(),
            xor_key_mode="num" if self.xor_num_radio.isChecked() else "str",
            xor_key_num=self.xor_key_num.value(),
            xor_key_str=self.xor_key_str.text(),
            trans_key=self.trans_key.text(),
            major_steps=self.major.isChecked(),
        )

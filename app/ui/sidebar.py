"""Левая панель: выбор алгоритма, входные данные, настройки."""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup,
                               QLineEdit, QSpinBox, QStackedWidget, QWidget, QCheckBox, QRadioButton,
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
    ("caesar", "1", "Шифр Цезаря", "сдвиг букв по алфавиту"),
    ("xor", "2", "XOR", "побитовое сложение по модулю 2"),
    ("transposition", "3", "Перестановка", "столбцовая, по ключевому слову"),
]

HOTKEYS = [
    ("Пробел / →", "шаг вперёд"),
    ("←", "шаг назад"),
    ("Home / End", "в начало / в конец"),
    ("Enter", "авто-воспроизведение"),
    ("+ / −", "быстрее / медленнее"),
    ("1 · 2 · 3", "выбор алгоритма"),
    ("E / D", "шифровать / дешифровать"),
    ("M", "крупные шаги"),
    ("F", "полный экран"),
    ("Esc", "выйти из поля ввода"),
]


class AutoStack(QStackedWidget):
    """QStackedWidget, высота которого равна высоте текущей страницы, а не максимальной."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentChanged.connect(lambda _: self.updateGeometry())

    def sizeHint(self):
        w = self.currentWidget()
        return w.sizeHint() if w else super().sizeHint()

    def minimumSizeHint(self):
        w = self.currentWidget()
        return w.minimumSizeHint() if w else super().minimumSizeHint()


def section(text: str) -> QLabel:
    lab = QLabel(text)
    lab.setObjectName("Section")
    return lab


class Sidebar(QFrame):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(320)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        inner = QWidget()
        scroll.setWidget(inner)
        outer.addWidget(scroll)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(20, 22, 20, 20)
        lay.setSpacing(10)

        title = QLabel("Криптовизор")
        title.setObjectName("AppTitle")
        sub = QLabel("пошаговая визуализация шифров")
        sub.setObjectName("AppSubtitle")
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addSpacing(8)

        # ── Алгоритм ──
        lay.addWidget(section("Алгоритм"))
        self.algo_group = QButtonGroup(self)
        self.algo_buttons: dict[str, QPushButton] = {}
        for key, num, name, desc in ALGOS:
            btn = QPushButton(f"{num}   {name}")
            btn.setObjectName("Algo")
            btn.setCheckable(True)
            btn.setToolTip(desc)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.algo_group.addButton(btn)
            self.algo_buttons[key] = btn
            lay.addWidget(btn)
        self.algo_buttons["caesar"].setChecked(True)
        self.algo_group.buttonClicked.connect(self._on_algo)

        # ── Режим ──
        lay.addWidget(section("Режим"))
        mode_row = QHBoxLayout()
        mode_row.setSpacing(6)
        self.btn_enc = QPushButton("Шифровать")
        self.btn_dec = QPushButton("Дешифровать")
        for b in (self.btn_enc, self.btn_dec):
            b.setObjectName("Seg")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            mode_row.addWidget(b)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.btn_enc)
        self.mode_group.addButton(self.btn_dec)
        self.btn_enc.setChecked(True)
        self.mode_group.buttonClicked.connect(lambda _: self._emit())
        lay.addLayout(mode_row)

        # ── Текст ──
        lay.addWidget(section("Текст"))
        self.text = QLineEdit("Привет, мир!")
        self.text.setMaxLength(40)
        self.text.setPlaceholderText("до 40 символов")
        self.text.textChanged.connect(self._emit)
        lay.addWidget(self.text)
        self.text_hint = QLabel("")
        self.text_hint.setObjectName("Hint")
        self.text_hint.setWordWrap(True)
        lay.addWidget(self.text_hint)

        # ── Ключ (зависит от алгоритма) ──
        lay.addWidget(section("Ключ"))
        self.key_stack = AutoStack()
        self.key_stack.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        lay.addWidget(self.key_stack)

        # Цезарь
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        row = QHBoxLayout()
        row.addWidget(QLabel("Сдвиг"))
        self.caesar_shift = QSpinBox()
        self.caesar_shift.setRange(-32, 32)
        self.caesar_shift.setValue(3)
        self.caesar_shift.valueChanged.connect(self._emit)
        row.addWidget(self.caesar_shift, 1)
        v.addLayout(row)
        h = QLabel("Латиница — 26 букв, кириллица — 33 (с Ё). Регистр сохраняется.")
        h.setObjectName("Hint")
        h.setWordWrap(True)
        v.addWidget(h)
        self.key_stack.addWidget(w)

        # XOR
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
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
        self.xor_hint = QLabel("Текст кодируется в CP1251: 1 символ = 1 байт = 8 бит.\n"
                               "В режиме дешифрования можно ввести hex: «4A 2F …».")
        self.xor_hint.setObjectName("Hint")
        self.xor_hint.setWordWrap(True)
        v.addWidget(self.xor_hint)
        self.xor_num_radio.toggled.connect(self._sync_xor)
        self.xor_key_num.valueChanged.connect(self._emit)
        self.xor_key_str.textChanged.connect(self._emit)
        self.key_stack.addWidget(w)

        # Перестановка
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        self.trans_key = QLineEdit("КЛЮЧ")
        self.trans_key.setMaxLength(10)
        self.trans_key.setPlaceholderText("слово или цифры, напр. 3142")
        self.trans_key.textChanged.connect(self._emit)
        v.addWidget(self.trans_key)
        h = QLabel("Слово: столбцы нумеруются по алфавиту букв ключа.\n"
                   "Цифры: явный порядок чтения столбцов.")
        h.setObjectName("Hint")
        h.setWordWrap(True)
        v.addWidget(h)
        self.key_stack.addWidget(w)

        # ── Показ ──
        lay.addWidget(section("Показ"))
        self.major = QCheckBox("Крупные шаги (по символу / столбцу)")
        self.major.toggled.connect(self._emit)
        lay.addWidget(self.major)

        # ── Горячие клавиши ──
        lay.addWidget(section("Клавиши"))
        for keys, desc in HOTKEYS:
            row = QHBoxLayout()
            k = QLabel(keys)
            k.setObjectName("Kbd")
            k.setFixedWidth(100)
            dsc = QLabel(desc)
            dsc.setObjectName("Hint")
            row.addWidget(k)
            row.addWidget(dsc, 1)
            lay.addLayout(row)
        lay.addStretch(1)

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

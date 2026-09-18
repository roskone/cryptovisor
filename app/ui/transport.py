"""Нижняя панель: вкладки Шаг / Журнал / Клавиши, управление воспроизведением."""
from __future__ import annotations

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSlider,
                               QStackedWidget, QWidget, QListWidget, QListWidgetItem, QButtonGroup,
                               QGridLayout)

from .sidebar import HOTKEYS

_TAG = re.compile(r"<[^>]+>")


def plain(html: str) -> str:
    return _TAG.sub("", html).replace("&nbsp;", " ").replace("&amp;", "&")


class Transport(QFrame):
    first = Signal()
    prev = Signal()
    next = Signal()
    last = Signal()
    play_toggled = Signal(bool)
    speed_changed = Signal(int)   # мс на шаг
    jump = Signal(int)            # клик по строке журнала

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Transport")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 0, 22, 14)
        lay.setSpacing(6)

        # ── вкладки нижней панели ──
        tabs = QHBoxLayout()
        tabs.setContentsMargins(0, 0, 0, 0)
        tabs.setSpacing(0)
        self.tab_group = QButtonGroup(self)
        self.tab_buttons = []
        for i, name in enumerate(("ШАГ", "ЖУРНАЛ", "КЛАВИШИ")):
            b = QPushButton(name)
            b.setObjectName("BottomTab")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            self.tab_group.addButton(b, i)
            self.tab_buttons.append(b)
            tabs.addWidget(b)
        tabs.addStretch(1)
        lay.addLayout(tabs)
        self.tab_buttons[0].setChecked(True)
        self.tab_group.idClicked.connect(self._on_tab)

        self.pages = QStackedWidget()
        self.pages.setFixedHeight(84)
        lay.addWidget(self.pages)

        # страница «Шаг»
        self.step_text = QLabel("Введите данные слева, затем нажмите «Шаг» или пробел")
        self.step_text.setObjectName("StepText")
        self.step_text.setTextFormat(Qt.TextFormat.RichText)
        self.step_text.setWordWrap(True)
        self.step_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.pages.addWidget(self.step_text)

        # страница «Журнал»
        self.journal = QListWidget()
        self.journal.setObjectName("Journal")
        self.journal.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.journal.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.journal.itemClicked.connect(lambda it: self.jump.emit(self.journal.row(it) + 1))
        self.pages.addWidget(self.journal)

        # страница «Клавиши»
        keys = QWidget()
        grid = QGridLayout(keys)
        grid.setContentsMargins(4, 4, 4, 0)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(2)
        cols = 4
        for i, (k, d) in enumerate(HOTKEYS):
            r, c = divmod(i, cols)
            kl = QLabel(k)
            kl.setObjectName("Kbd")
            dl = QLabel(d)
            dl.setObjectName("KbdDesc")
            grid.addWidget(kl, r, c * 2)
            grid.addWidget(dl, r, c * 2 + 1)
        grid.setColumnStretch(cols * 2, 1)
        self.pages.addWidget(keys)

        # ── кнопки ──
        row = QHBoxLayout()
        row.setSpacing(8)
        self.btn_first = self._btn("⏮", "В начало (Home)")
        self.btn_prev = self._btn("◀", "Шаг назад (←)")
        self.btn_play = QPushButton("▶  Авто")
        self.btn_play.setObjectName("Play")
        self.btn_play.setCheckable(True)
        self.btn_play.setToolTip("Авто-воспроизведение (Enter)")
        self.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next = self._btn("▶", "Шаг вперёд (пробел / →)")
        self.btn_last = self._btn("⏭", "В конец (End)")
        for b in (self.btn_first, self.btn_prev, self.btn_play, self.btn_next, self.btn_last):
            row.addWidget(b)
        self.btn_first.clicked.connect(self.first)
        self.btn_prev.clicked.connect(self.prev)
        self.btn_next.clicked.connect(self.next)
        self.btn_last.clicked.connect(self.last)
        self.btn_play.toggled.connect(self.play_toggled)

        self.counter = QLabel("")
        self.counter.setObjectName("StepCounter")
        row.addSpacing(14)
        row.addWidget(self.counter)
        row.addStretch(1)

        speed_lab = QLabel("Скорость")
        speed_lab.setObjectName("StepCounter")
        row.addWidget(speed_lab)
        self.speed = QSlider(Qt.Orientation.Horizontal)
        self.speed.setRange(1, 10)
        self.speed.setValue(5)
        self.speed.setFixedWidth(160)
        self.speed.setToolTip("+ / − на клавиатуре")
        self.speed.valueChanged.connect(lambda v: self.speed_changed.emit(self.interval_ms()))
        row.addWidget(self.speed)
        lay.addLayout(row)

    @staticmethod
    def _btn(text, tip) -> QPushButton:
        b = QPushButton(text)
        b.setObjectName("Transport")
        b.setToolTip(tip)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        return b

    def _on_tab(self, idx: int):
        self.pages.setCurrentIndex(idx)

    def interval_ms(self) -> int:
        v = self.speed.value()
        return int(2000 - (v - 1) * (1850 / 9))

    def nudge_speed(self, delta: int):
        self.speed.setValue(self.speed.value() + delta)

    def set_state(self, pos: int, total: int, text: str, error: bool = False):
        self.counter.setText(f"{pos} / {total}")
        self.step_text.setObjectName("Error" if error else "StepText")
        self.step_text.style().unpolish(self.step_text)
        self.step_text.style().polish(self.step_text)
        self.step_text.setText(text)
        self.btn_first.setEnabled(pos > 0)
        self.btn_prev.setEnabled(pos > 0)
        self.btn_next.setEnabled(pos < total)
        self.btn_last.setEnabled(pos < total)
        self.btn_play.setEnabled(total > 0)

    def set_journal(self, texts: list[str], pos: int):
        """Журнал: все шаги моноширинным списком, пройденные — ярче, текущий — выделен."""
        if self.journal.count() != len(texts):
            self.journal.clear()
            width = len(str(len(texts)))
            for i, t in enumerate(texts, 1):
                self.journal.addItem(QListWidgetItem(f"{i:>{width}}   {plain(t)}"))
        self.journal.blockSignals(True)
        self.journal.clearSelection()
        if pos > 0:
            self.journal.setCurrentRow(pos - 1)
            self.journal.scrollToItem(self.journal.item(pos - 1))
        self.journal.blockSignals(False)

    def set_playing(self, playing: bool):
        self.btn_play.blockSignals(True)
        self.btn_play.setChecked(playing)
        self.btn_play.setText("⏸  Пауза" if playing else "▶  Авто")
        self.btn_play.blockSignals(False)

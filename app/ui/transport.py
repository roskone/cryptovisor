"""Нижняя панель управления воспроизведением и пояснение текущего шага."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSlider, QSizePolicy


class Transport(QFrame):
    first = Signal()
    prev = Signal()
    next = Signal()
    last = Signal()
    play_toggled = Signal(bool)
    speed_changed = Signal(int)   # мс на шаг

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Transport")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 12, 22, 14)
        lay.setSpacing(8)

        self.step_text = QLabel("Введите данные слева, затем нажмите «Шаг» или пробел")
        self.step_text.setObjectName("StepText")
        self.step_text.setTextFormat(Qt.TextFormat.RichText)
        self.step_text.setWordWrap(True)
        self.step_text.setMinimumHeight(52)
        self.step_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        lay.addWidget(self.step_text)

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

    def interval_ms(self) -> int:
        # 1 → 2000 мс, 10 → 150 мс
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

    def set_playing(self, playing: bool):
        self.btn_play.blockSignals(True)
        self.btn_play.setChecked(playing)
        self.btn_play.setText("⏸  Пауза" if playing else "▶  Авто")
        self.btn_play.blockSignals(False)

"""Главное окно: связывает панель ввода, сцены и транспорт; обрабатывает горячие клавиши."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QAction
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
                               QLineEdit, QSpinBox, QApplication)

from .sidebar import Sidebar, Params
from .transport import Transport
from .chrome import TabBar
from .scenes.caesar_scene import CaesarScene
from .scenes.xor_scene import XorScene
from .scenes.transposition_scene import TranspositionScene
from ..core import caesar, xor, transposition
from ..core.steps import Step, CipherError


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Криптовизор — пошаговая визуализация шифров")
        self.resize(1440, 900)

        self.steps: list[Step] = []
        self.pos = 0
        self.major_only = False

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar()
        root.addWidget(self.sidebar)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)
        self.tabbar = TabBar()
        right.addWidget(self.tabbar)
        self.scenes = {
            "caesar": CaesarScene(),
            "xor": XorScene(),
            "transposition": TranspositionScene(),
        }
        self.stack = QStackedWidget()
        self.stack.setObjectName("Scenes")
        for s in self.scenes.values():
            self.stack.addWidget(s)
        right.addWidget(self.stack, 1)
        self.transport = Transport()
        right.addWidget(self.transport)
        root.addLayout(right, 1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.setInterval(self.transport.interval_ms())

        self.sidebar.changed.connect(self.rebuild)
        self.tabbar.algo_selected.connect(self.sidebar.set_algo)
        self.tabbar.mode_selected.connect(self.sidebar.set_decrypt)
        self.transport.jump.connect(self.go_to)
        self.transport.first.connect(lambda: self.go_to(0))
        self.transport.prev.connect(self.step_back)
        self.transport.next.connect(self.step_forward)
        self.transport.last.connect(lambda: self.go_to(len(self.steps)))
        self.transport.play_toggled.connect(self.set_playing)
        self.transport.speed_changed.connect(self.timer.setInterval)

        self._setup_shortcuts()
        self.rebuild()
        self.stack.currentWidget().setFocus()

    # ── горячие клавиши ──
    def _setup_shortcuts(self):
        def sc(keys, slot):
            for k in (keys if isinstance(keys, (list, tuple)) else [keys]):
                s = QShortcut(QKeySequence(k), self)
                s.setContext(Qt.ShortcutContext.WindowShortcut)
                s.activated.connect(slot)

        sc(["Space", "Right"], self.step_forward)
        sc("Left", self.step_back)
        sc("Home", lambda: self.go_to(0))
        sc("End", lambda: self.go_to(len(self.steps)))
        sc(["Return", "Enter"], self.toggle_play)
        sc(["+", "="], lambda: self.transport.nudge_speed(1))
        sc(["-", "_"], lambda: self.transport.nudge_speed(-1))
        sc("1", lambda: self.sidebar.set_algo("caesar"))
        sc("2", lambda: self.sidebar.set_algo("xor"))
        sc("3", lambda: self.sidebar.set_algo("transposition"))
        sc("E", lambda: self.sidebar.set_decrypt(False))
        sc("D", lambda: self.sidebar.set_decrypt(True))
        sc("M", self.sidebar.toggle_major)
        sc(["F", QKeySequence.StandardKey.FullScreen, "F11"], self.toggle_fullscreen)
        sc("Escape", self._escape)

    def _escape(self):
        w = QApplication.focusWidget()
        if isinstance(w, (QLineEdit, QSpinBox)):
            self.stack.currentWidget().setFocus()
        elif self.isFullScreen():
            self.showNormal()

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    # ── построение шагов ──
    def rebuild(self):
        self.set_playing(False)
        prm: Params = self.sidebar.params()
        self.major_only = prm.major_steps
        self.tabbar.sync(prm.algo, prm.decrypt)
        scene = self.scenes[prm.algo]
        self.stack.setCurrentWidget(scene)
        self.sidebar.set_text_hint("")
        try:
            ctx, self.steps = self._build(prm)
        except CipherError as e:
            self.steps = []
            scene.set_context(None)
            self.transport.set_state(0, 0, str(e), error=True)
            self.tabbar.set_step(0, 0)
            return
        scene.set_context(ctx)
        self.pos = 0
        self.transport.journal.clear()
        self._show(animate=False)

    def _build(self, prm: Params):
        if prm.algo == "caesar":
            steps = caesar.caesar_steps(prm.text, prm.caesar_shift, prm.decrypt)
            shift = -prm.caesar_shift if prm.decrypt else prm.caesar_shift
            return {"text": prm.text, "shift": shift}, steps
        if prm.algo == "xor":
            data, was_hex = xor.parse_input(prm.text, allow_hex=prm.decrypt)
            key = xor.parse_key(prm.xor_key_mode, prm.xor_key_num, prm.xor_key_str)
            steps = xor.xor_steps(data, key)
            result = xor.xor_bytes(data, key)
            hint = "Результат hex: " + " ".join(f"{b:02X}" for b in result)
            if prm.decrypt:
                hint += "   → «" + result.decode(xor.ENCODING, errors="replace") + "»"
            self.sidebar.set_text_hint(hint)
            return {"data": data, "key": key, "was_hex": was_hex, "key_mode": prm.xor_key_mode}, steps
        if prm.decrypt:
            steps = transposition.decrypt_steps(prm.text, prm.trans_key)
        else:
            steps = transposition.encrypt_steps(prm.text, prm.trans_key)
        base = steps[0].data
        ctx = {k: base[k] for k in ("headers", "ranks", "order", "rows", "cols", "source", "mode")}
        return ctx, steps

    # ── навигация ──
    def _show(self, animate: bool = True):
        scene = self.stack.currentWidget()
        if self.pos == 0:
            scene.set_step(None, animate=False)
            self.transport.set_state(0, len(self.steps), "Готово. Нажмите «Шаг» (пробел), чтобы начать")
        else:
            step = self.steps[self.pos - 1]
            scene.set_step(step, animate=animate)
            self.transport.set_state(self.pos, len(self.steps), step.text)
        self.tabbar.set_step(self.pos, len(self.steps))
        self.transport.set_journal([s.text for s in self.steps], self.pos)
        if self.pos >= len(self.steps):
            self.set_playing(False)

    def go_to(self, pos: int):
        self.pos = max(0, min(len(self.steps), pos))
        self._show(animate=True)

    def step_forward(self):
        if self.pos >= len(self.steps):
            return
        self.pos += 1
        if self.major_only:
            while self.pos < len(self.steps) and not self.steps[self.pos - 1].major:
                self.pos += 1
        self._show()

    def step_back(self):
        if self.pos <= 0:
            return
        self.pos -= 1
        if self.major_only:
            while self.pos > 0 and not self.steps[self.pos - 1].major:
                self.pos -= 1
        self._show()

    # ── авто-воспроизведение ──
    def set_playing(self, playing: bool):
        if playing and self.pos >= len(self.steps):
            self.pos = 0
            self._show(animate=False)
        if playing and self.steps:
            self.timer.start()
        else:
            self.timer.stop()
            playing = False
        self.transport.set_playing(playing)

    def toggle_play(self):
        self.set_playing(not self.timer.isActive())

    def _tick(self):
        if self.pos >= len(self.steps):
            self.set_playing(False)
            return
        self.step_forward()

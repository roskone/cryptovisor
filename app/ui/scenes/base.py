"""Базовый класс сцены: хранит контекст и текущий шаг, анимирует переход."""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, QVariantAnimation, QEasingCurve, QRectF, Property
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget

from ..draw import draw_background, draw_text, font
from .. import theme
from ...core.steps import Step


class Scene(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(640, 420)
        self.ctx: dict[str, Any] | None = None
        self.step: Step | None = None
        self._progress = 1.0
        self._anim = QVariantAnimation(self)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_anim)
        self.anim_duration = 380

    def _on_anim(self, v):
        self._progress = float(v)
        self.update()

    def get_progress(self) -> float:
        return self._progress

    progress = Property(float, get_progress)

    def set_context(self, ctx: dict[str, Any] | None):
        self.ctx = ctx
        self.step = None
        self._anim.stop()
        self._progress = 1.0
        self.update()

    def set_step(self, step: Step | None, animate: bool = True):
        self.step = step
        self._anim.stop()
        if animate and step is not None:
            self._anim.setDuration(self.anim_duration)
            self._progress = 0.0
            self._anim.start()
        else:
            self._progress = 1.0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(self.rect())
        draw_background(p, rect)
        if self.ctx is None:
            draw_text(p, rect, "Введите данные слева, чтобы начать", 18, theme.MUTED)
            return
        self.paint_scene(p, rect)
        p.end()

    def paint_scene(self, p: QPainter, rect: QRectF):  # переопределяется в наследниках
        raise NotImplementedError

    def mousePressEvent(self, event):
        self.setFocus()
        super().mousePressEvent(event)

"""Общая модель шага визуализации.

Каждый алгоритм превращает входные данные в список Step. Шаг хранит
полный снимок состояния, нужный для отрисовки, поэтому сцена может
показать любой шаг напрямую, без «проигрывания» предыдущих.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Step:
    text: str                      # пояснение для лектора (простой HTML допустим)
    major: bool = True             # «крупный» шаг — граница символа/байта/столбца
    data: dict[str, Any] = field(default_factory=dict)


class CipherError(ValueError):
    """Ошибка во входных данных (пустой текст, неверный ключ и т.п.)."""

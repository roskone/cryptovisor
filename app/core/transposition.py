"""Столбцовая перестановка (columnar transposition).

Ключ — слово («КЛЮЧ») или последовательность цифр («3142»).
Текст записывается в таблицу по строкам, столбцы читаются в порядке,
который задаёт ключ.
"""
from __future__ import annotations

from math import ceil

from .steps import Step, CipherError

PAD = "_"


def parse_key(key: str) -> tuple[list[str], list[int]]:
    """Возвращает (заголовки столбцов, ранг каждого столбца 0..n-1)."""
    key = key.strip()
    if len(key) < 2:
        raise CipherError("Ключ должен содержать минимум 2 символа")
    if key.isdigit():
        nums = [int(c) for c in key]
        if sorted(nums) != list(range(1, len(nums) + 1)):
            raise CipherError("Числовой ключ должен быть перестановкой 1..n, например 3142")
        return list(key), [x - 1 for x in nums]
    if any(c.isspace() for c in key):
        raise CipherError("Ключ не должен содержать пробелов")
    up = key.upper()
    # ранг буквы: сортируем пары (буква, позиция) — одинаковые буквы идут слева направо
    order = sorted(range(len(up)), key=lambda i: (up[i], i))
    ranks = [0] * len(up)
    for rank, col in enumerate(order):
        ranks[col] = rank
    return list(up), ranks


def read_order(ranks: list[int]) -> list[int]:
    """Индексы столбцов в порядке чтения (по возрастанию ранга)."""
    return sorted(range(len(ranks)), key=lambda c: ranks[c])


def _empty_grid(rows: int, cols: int) -> list[list[str | None]]:
    return [[None] * cols for _ in range(rows)]


def _snapshot(grid):
    return [row[:] for row in grid]


def encrypt_steps(text: str, key: str) -> list[Step]:
    if not text:
        raise CipherError("Введите текст")
    headers, ranks = parse_key(key)
    cols = len(headers)
    rows = ceil(len(text) / cols)
    padded = text.ljust(rows * cols, PAD)
    order = read_order(ranks)
    grid = _empty_grid(rows, cols)
    steps: list[Step] = []
    base = {"headers": headers, "ranks": ranks, "order": order, "rows": rows, "cols": cols,
            "source": padded, "mode": "enc"}

    # Фаза 1: заполняем таблицу по строкам
    for i, ch in enumerate(padded):
        r, c = divmod(i, cols)
        grid[r][c] = ch
        is_pad = i >= len(text)
        desc = (f"Записываем <b>‘{ch}’</b> в строку {r + 1}, столбец {c + 1}"
                if not is_pad else
                f"Дополняем таблицу символом <b>‘{PAD}’</b> (строка {r + 1}, столбец {c + 1})")
        steps.append(Step(desc, major=(c == cols - 1), data={
            **base, "phase": "fill", "grid": _snapshot(grid), "src_index": i,
            "cell": (r, c), "output": "", "ranks_shown": 0,
        }))

    # Фаза 2: нумеруем столбцы по ключу
    for k, c in enumerate(order):
        desc = (f"Столбец <b>‘{headers[c]}’</b> получает номер <b>{k + 1}</b> "
                f"— {'по алфавиту' if not key.strip().isdigit() else 'по ключу'}")
        steps.append(Step(desc, major=True, data={
            **base, "phase": "order", "grid": _snapshot(grid), "src_index": None,
            "cell": None, "col": c, "output": "", "ranks_shown": k + 1,
        }))

    # Фаза 3: читаем столбцы в порядке ключа
    output = ""
    for k, c in enumerate(order):
        for r in range(rows):
            output += grid[r][c]
            desc = (f"Читаем столбец <b>{k + 1}</b> (‘{headers[c]}’), строка {r + 1}: "
                    f"<b>‘{grid[r][c]}’</b>")
            steps.append(Step(desc, major=(r == rows - 1), data={
                **base, "phase": "read", "grid": _snapshot(grid), "src_index": None,
                "cell": (r, c), "col": c, "output": output, "ranks_shown": cols,
                "out_index": len(output) - 1,
            }))
    return steps


def decrypt_steps(cipher: str, key: str) -> list[Step]:
    if not cipher:
        raise CipherError("Введите текст")
    headers, ranks = parse_key(key)
    cols = len(headers)
    if len(cipher) % cols != 0:
        raise CipherError(f"Длина шифртекста ({len(cipher)}) должна делиться на длину ключа ({cols})")
    rows = len(cipher) // cols
    order = read_order(ranks)
    grid = _empty_grid(rows, cols)
    steps: list[Step] = []
    base = {"headers": headers, "ranks": ranks, "order": order, "rows": rows, "cols": cols,
            "source": cipher, "mode": "dec"}

    # Фаза 1: нумеруем столбцы
    for k, c in enumerate(order):
        steps.append(Step(f"Столбец <b>‘{headers[c]}’</b> получает номер <b>{k + 1}</b>",
                          major=True, data={
            **base, "phase": "order", "grid": _snapshot(grid), "src_index": None,
            "cell": None, "col": c, "output": "", "ranks_shown": k + 1,
        }))

    # Фаза 2: заполняем столбцы в порядке ключа
    i = 0
    for k, c in enumerate(order):
        for r in range(rows):
            grid[r][c] = cipher[i]
            desc = (f"Символ <b>‘{cipher[i]}’</b> → столбец <b>{k + 1}</b> (‘{headers[c]}’), "
                    f"строка {r + 1}")
            steps.append(Step(desc, major=(r == rows - 1), data={
                **base, "phase": "fill", "grid": _snapshot(grid), "src_index": i,
                "cell": (r, c), "col": c, "output": "", "ranks_shown": cols,
            }))
            i += 1

    # Фаза 3: читаем по строкам
    output = ""
    for r in range(rows):
        for c in range(cols):
            output += grid[r][c]
            steps.append(Step(f"Читаем строку {r + 1}, столбец {c + 1}: <b>‘{grid[r][c]}’</b>",
                              major=(c == cols - 1), data={
                **base, "phase": "read", "grid": _snapshot(grid), "src_index": None,
                "cell": (r, c), "col": None, "output": output, "ranks_shown": cols,
                "out_index": len(output) - 1,
            }))
    return steps


def encrypt(text: str, key: str) -> str:
    return encrypt_steps(text, key)[-1].data["output"]


def decrypt(cipher: str, key: str) -> str:
    return decrypt_steps(cipher, key)[-1].data["output"]

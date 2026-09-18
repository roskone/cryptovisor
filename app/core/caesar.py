"""Шифр Цезаря с поддержкой латиницы и кириллицы."""
from __future__ import annotations

from .steps import Step, CipherError

LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CYRILLIC = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def alphabet_for(ch: str) -> str | None:
    up = ch.upper()
    if up in LATIN:
        return LATIN
    if up in CYRILLIC:
        return CYRILLIC
    return None


def shift_char(ch: str, shift: int) -> tuple[str, dict]:
    """Сдвигает один символ. Возвращает (результат, подробности для сцены)."""
    alphabet = alphabet_for(ch)
    if alphabet is None:
        return ch, {"is_letter": False, "alphabet": None}
    n = len(alphabet)
    upper = ch.isupper()
    pos = alphabet.index(ch.upper())
    new_pos = (pos + shift) % n
    out = alphabet[new_pos]
    if not upper:
        out = out.lower()
    return out, {
        "is_letter": True,
        "alphabet": alphabet,
        "upper": upper,
        "pos_src": pos,
        "pos_dst": new_pos,
        "wrapped": not (0 <= pos + shift < n),
    }


def caesar_steps(text: str, shift: int, decrypt: bool = False) -> list[Step]:
    if not text:
        raise CipherError("Введите текст")
    eff = -shift if decrypt else shift
    steps: list[Step] = []
    output = ""
    for i, ch in enumerate(text):
        out, info = shift_char(ch, eff)
        output += out
        data = {
            "index": i,
            "src": ch,
            "dst": out,
            "shift": eff,
            "code_src": ord(ch),
            "code_dst": ord(out),
            "output": output,
            **info,
        }
        if info["is_letter"]:
            n = len(info["alphabet"])
            sign = "+" if eff >= 0 else "−"
            text_desc = (
                f"<b>‘{ch}’</b> — позиция {info['pos_src']} &nbsp;→&nbsp; "
                f"({info['pos_src']} {sign} {abs(eff)}) mod {n} = {info['pos_dst']} "
                f"&nbsp;→&nbsp; <b>‘{out}’</b>"
            )
            if info["wrapped"]:
                text_desc += " &nbsp;<span style='color:#ffd166'>(переход через край алфавита)</span>"
        else:
            text_desc = f"<b>‘{ch}’</b> — не буква, остаётся без изменений"
        steps.append(Step(text=text_desc, major=True, data=data))
    return steps


def caesar(text: str, shift: int, decrypt: bool = False) -> str:
    eff = -shift if decrypt else shift
    return "".join(shift_char(c, eff)[0] for c in text)

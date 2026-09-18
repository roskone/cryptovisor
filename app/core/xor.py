"""Побитовый XOR с ключом-числом или ключом-строкой.

Текст кодируется в CP1251, чтобы каждый символ (в т.ч. кириллица)
занимал ровно один байт — так на экране один символ = 8 бит.
"""
from __future__ import annotations

import re

from .steps import Step, CipherError

ENCODING = "cp1251"
_HEX_RE = re.compile(r"^[0-9a-fA-F]{2}([\s,]*[0-9a-fA-F]{2})*$")


def encode_text(text: str) -> bytes:
    try:
        return text.encode(ENCODING)
    except UnicodeEncodeError as e:
        raise CipherError(f"Символ «{e.object[e.start]}» нельзя закодировать в CP1251") from e


def parse_input(text: str, allow_hex: bool) -> tuple[bytes, bool]:
    """Возвращает (байты, was_hex). В режиме дешифрования принимаем hex."""
    stripped = text.strip()
    if not stripped:
        raise CipherError("Введите текст")
    if allow_hex and _HEX_RE.match(stripped):
        clean = re.sub(r"[\s,]", "", stripped)
        return bytes.fromhex(clean), True
    return encode_text(text), False


def parse_key(mode: str, key_num: int, key_str: str) -> bytes:
    if mode == "num":
        if not 0 <= key_num <= 255:
            raise CipherError("Числовой ключ должен быть от 0 до 255")
        return bytes([key_num])
    if not key_str:
        raise CipherError("Введите ключ")
    return encode_text(key_str)


def byte_repr(b: int) -> str:
    """Печатный символ для байта или «·», если непечатный."""
    ch = bytes([b]).decode(ENCODING, errors="replace")
    return ch if ch.isprintable() and ch != "�" else "·"


def bits(b: int) -> list[int]:
    return [(b >> (7 - i)) & 1 for i in range(8)]


def xor_steps(data: bytes, key: bytes) -> list[Step]:
    if not data:
        raise CipherError("Введите текст")
    if not key:
        raise CipherError("Введите ключ")
    steps: list[Step] = []
    output = bytearray()
    for bi, tb in enumerate(data):
        ki = bi % len(key)
        kb = key[ki]
        tbits, kbits = bits(tb), bits(kb)
        rbits: list[int | None] = [None] * 8
        for bit in range(8):
            rbits[bit] = tbits[bit] ^ kbits[bit]
            done_byte = bit == 7
            if done_byte:
                output.append(tb ^ kb)
            step_data = {
                "byte_index": bi,
                "bit_index": bit,
                "t_byte": tb,
                "k_byte": kb,
                "key_index": ki,
                "t_bits": tbits,
                "k_bits": kbits,
                "r_bits": list(rbits),
                "output": bytes(output),
                "byte_done": done_byte,
            }
            desc = (
                f"Байт {bi + 1}, бит {bit + 1}: &nbsp;"
                f"<b>{tbits[bit]}</b> ⊕ <b>{kbits[bit]}</b> = <b>{rbits[bit]}</b>"
            )
            if done_byte:
                res = tb ^ kb
                desc += (
                    f" &nbsp;→&nbsp; байт готов: 0x{tb:02X} ⊕ 0x{kb:02X} = "
                    f"<b>0x{res:02X}</b> (‘{byte_repr(res)}’)"
                )
            steps.append(Step(text=desc, major=done_byte, data=step_data))
    return steps


def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

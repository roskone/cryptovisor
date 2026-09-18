"""Сцена шифра Цезаря: строка текста, лента алфавита со стрелкой сдвига, формула, результат."""
from __future__ import annotations

from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtGui import QPainter, QFont, QPen

from .base import Scene
from .. import theme
from ..draw import (draw_cell, draw_label, draw_text, draw_card, draw_arrow, layout_row,
                    ease, with_alpha, draw_badge, font)
from ...core.caesar import LATIN


class CaesarScene(Scene):
    def paint_scene(self, p: QPainter, rect: QRectF):
        ctx, step = self.ctx, self.step
        text: str = ctx["text"]
        shift: int = ctx["shift"]
        d = step.data if step else None
        idx = d["index"] if d else -1
        t = ease(self._progress)
        m = 40
        W = rect.width() - 2 * m
        y = 34

        # ── Исходный текст ────────────────────────────────────────────────
        draw_label(p, m, y, "Исходный текст")
        y += 12
        cells = layout_row(m, y, len(text), W, max_cell=60)
        for i, r in enumerate(cells):
            if i < idx:
                state, glow = theme.CELL_DONE, False
            elif i == idx:
                state, glow = theme.CELL_CURRENT, True
            else:
                state, glow = theme.CELL_FUTURE, False
            draw_cell(p, r, text[i], state, glow=glow)
        cell_h = cells[0].height() if cells else 54
        y += cell_h + 40

        # ── Лента алфавита ────────────────────────────────────────────────
        alphabet = (d["alphabet"] if d and d["is_letter"] else None) or ctx.get("last_alphabet") or LATIN
        card_h = 150
        card = QRectF(m, y, W, card_h)
        sign = "+" if shift >= 0 else "−"
        draw_card(p, card, f"Алфавит ({len(alphabet)} букв) · сдвиг {sign}{abs(shift)}")
        strip_y = card.y() + 78
        strip = layout_row(card.x() + 18, strip_y, len(alphabet), card.width() - 36, max_cell=44, gap=4)
        is_letter = bool(d and d["is_letter"])
        pos_src = d["pos_src"] if is_letter else -1
        pos_dst = d["pos_dst"] if is_letter else -1
        for i, r in enumerate(strip):
            if i == pos_src:
                state = theme.CELL_CURRENT
            elif i == pos_dst and t > 0.85:
                state = theme.CELL_DONE
            else:
                state = theme.CELL_FUTURE
            draw_cell(p, r, alphabet[i], state, size=int(r.height() * 0.48), glow=(i in (pos_src, pos_dst) and t > 0.85))
            # индекс под ячейкой
            draw_text(p, QRectF(r.x(), r.bottom() + 2, r.width(), 14), str(i), 10, theme.MUTED)

        if is_letter:
            n = len(alphabet)
            # положение стрелки: движется по ленте на shift позиций (с переходом через край)
            cur = (pos_src + shift * t)
            wrapped_now = cur >= n or cur < 0
            cur_mod = cur % n
            src_c = QPointF(strip[pos_src].center().x(), strip[pos_src].top() - 4)
            cell_w = strip[0].width() + 4
            dst_x = strip[0].center().x() + cur_mod * cell_w
            dst_c = QPointF(dst_x, strip[0].top() - 4)
            if wrapped_now:
                # рисуем «хвост» до края и продолжение с другого края
                edge_x = strip[-1].right() + 6 if shift > 0 else strip[0].left() - 6
                draw_arrow(p, src_c, QPointF(edge_x, src_c.y()), with_alpha(theme.WARM, 0.5),
                           curve=36)
                start_x = strip[0].left() - 6 if shift > 0 else strip[-1].right() + 6
                draw_arrow(p, QPointF(start_x, src_c.y()), dst_c, theme.WARM, curve=36)
                draw_text(p, QRectF(card.x(), card.y() + 30, card.width(), 20),
                          f"переход через край: mod {n}", 13, theme.WARM, QFont.Weight.DemiBold)
            else:
                draw_arrow(p, src_c, dst_c, theme.WARM, curve=36)
            # подпись сдвига над стрелкой
            mid_x = (src_c.x() + dst_c.x()) / 2 if not wrapped_now else card.center().x()
            draw_badge(p, QPointF(mid_x, strip_y - 34), f"{sign}{abs(shift)}", theme.WARM, r=14)
        elif d:
            draw_text(p, QRectF(card.x(), card.y() + 30, card.width(), 24),
                      "символ не входит в алфавит — сдвиг не применяется", 14, theme.MUTED)
        y += card_h + 24

        # ── Формула и коды ────────────────────────────────────────────────
        left = QRectF(m, y, W * 0.58 - 10, 132)
        right = QRectF(left.right() + 20, y, W - left.width() - 20, 132)
        draw_card(p, left, "Вычисление")
        draw_card(p, right, "Коды символов")
        if d:
            src, dst = d["src"], d["dst"]
            if is_letter:
                n = len(alphabet)
                lines = [
                    (f"‘{src}’  →  позиция {pos_src}", theme.TEXT),
                    (f"({pos_src} {sign} {abs(shift)}) mod {n}  =  {pos_dst}", theme.WARM),
                    (f"позиция {pos_dst}  →  ‘{dst}’", theme.GREEN),
                ]
            else:
                lines = [(f"‘{src}’ — не буква", theme.TEXT), ("остаётся как есть", theme.MUTED),
                         (f"→ ‘{dst}’", theme.GREEN)]
            for k, (txt, col) in enumerate(lines):
                draw_text(p, QRectF(left.x() + 18, left.y() + 30 + k * 32, left.width() - 36, 30),
                          txt, 21, col, QFont.Weight.DemiBold, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                          mono=True)
            cs, cd = d["code_src"], d["code_dst"]
            rows = [(f"‘{src}’", cs, theme.TEXT), (f"‘{dst}’", cd, theme.GREEN)]
            for k, (lab, code, col) in enumerate(rows):
                ry = right.y() + 36 + k * 42
                draw_text(p, QRectF(right.x() + 18, ry, 50, 30), lab, 20, col, QFont.Weight.DemiBold,
                          Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, mono=True)
                draw_text(p, QRectF(right.x() + 70, ry, 90, 30), f"{code:>5}", 18, theme.MUTED,
                          align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, mono=True)
                bits = f"{code:b}"
                bits = bits.zfill(8 if code < 256 else 16)
                draw_text(p, QRectF(right.x() + 160, ry, right.width() - 178, 30), bits, 18, col,
                          align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, mono=True)
        else:
            draw_text(p, QRectF(left.x(), left.y() + 20, left.width(), left.height() - 20),
                      "Нажмите «Шаг» или пробел", 16, theme.MUTED)
        y += 132 + 36

        # ── Результат ─────────────────────────────────────────────────────
        draw_label(p, m, y, "Результат")
        y += 12
        out = d["output"] if d else ""
        cells = layout_row(m, y, len(text), W, max_cell=60)
        for i, r in enumerate(cells):
            if i < len(out) - 1:
                draw_cell(p, r, out[i], theme.CELL_DONE)
            elif i == len(out) - 1:
                draw_cell(p, r, out[i], theme.CELL_CURRENT, alpha=0.35 + 0.65 * t, glow=True)
            else:
                draw_cell(p, r, "", theme.CELL_EMPTY)

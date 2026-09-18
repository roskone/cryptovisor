"""Сцена XOR: байты текста и ключа, побитовая панель 3×8, таблица истинности, результат."""
from __future__ import annotations

from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtGui import QPainter, QFont, QPen

from .base import Scene
from .. import theme
from ..draw import draw_cell, draw_label, draw_text, draw_card, layout_row, ease, with_alpha, font
from ...core.xor import byte_repr, bits


class XorScene(Scene):
    def paint_scene(self, p: QPainter, rect: QRectF):
        ctx, step = self.ctx, self.step
        data: bytes = ctx["data"]
        key: bytes = ctx["key"]
        d = step.data if step else None
        bi = d["byte_index"] if d else -1
        bit = d["bit_index"] if d else -1
        ki = d["key_index"] if d else -1
        t = ease(self._progress)
        m = 56 if theme.VARIANT == "editor" else 40
        W = rect.width() - 2 * m
        y = 34

        # ── Байты текста ──────────────────────────────────────────────────
        src_title = "Шифртекст (hex)" if ctx.get("was_hex") else "Текст · CP1251 · 1 символ = 1 байт"
        draw_label(p, m, y, src_title)
        y += 12
        cells = layout_row(m, y, len(data), W, max_cell=60)
        for i, r in enumerate(cells):
            done = i < bi or (i == bi and d and d["byte_done"] and t > 0.9)
            state = theme.CELL_DONE if done else theme.CELL_CURRENT if i == bi else theme.CELL_FUTURE
            self._byte_cell(p, r, data[i], state, glow=(i == bi))
        cell_h = cells[0].height() if cells else 54
        y += cell_h + 34

        # ── Байты ключа ───────────────────────────────────────────────────
        key_label = "Ключ · число 0–255" if len(key) == 1 and ctx.get("key_mode") == "num" else \
            f"Ключ · {len(key)} байт · повторяется циклически"
        draw_label(p, m, y, key_label)
        y += 12
        kcells = layout_row(m, y, len(key), W, max_cell=60)
        for i, r in enumerate(kcells):
            state = theme.CELL_KEY_CURRENT if i == ki else theme.CELL_KEY
            self._byte_cell(p, r, key[i], state, glow=(i == ki))
        if d and len(key) > 1:
            draw_text(p, QRectF(kcells[-1].right() + 16, y, 300, kcells[0].height()),
                      f"ключ[{bi} mod {len(key)} = {ki}]", 15, theme.ACCENT,
                      align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, mono=True)
        y += kcells[0].height() + 40

        # ── Побитовая панель ──────────────────────────────────────────────
        panel_h = 268
        truth_w = 230
        panel = QRectF(m, y, W - truth_w - 20, panel_h)
        truth = QRectF(panel.right() + 20, y, truth_w, panel_h)
        draw_card(p, panel, "Побитовая операция")
        draw_card(p, truth, "Таблица истинности")

        label_w = 240
        bits_x = panel.x() + label_w
        bits_avail = panel.width() - label_w - 24
        row_gap = 70
        rows_y = [panel.y() + 44, panel.y() + 44 + row_gap, panel.y() + 44 + 2 * row_gap]
        if d:
            tb, kb = d["t_byte"], d["k_byte"]
            tbits, kbits, rbits = d["t_bits"], d["k_bits"], d["r_bits"]
            rb_partial = sum((b or 0) << (7 - i) for i, b in enumerate(rbits) if b is not None)
        else:
            tb = kb = None
            tbits = kbits = [None] * 8
            rbits = [None] * 8

        # вертикальная подсветка текущего бита
        rows_rects = [layout_row(bits_x, ry, 8, bits_avail, max_cell=56, gap=8) for ry in rows_y]
        if d:
            col = rows_rects[0][bit]
            band = QRectF(col.x() - 6, rows_y[0] - 8, col.width() + 12,
                          rows_y[2] + rows_rects[2][0].height() - rows_y[0] + 16)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(with_alpha(theme.WARM, 0.08))
            p.drawRoundedRect(band, 10, 10)

        def row_label(k, title, value_txt, col):
            r = QRectF(panel.x() + 16, rows_y[k], label_w - 64, rows_rects[k][0].height())
            draw_text(p, QRectF(r.x(), r.y(), r.width(), r.height() / 2), title, 12, theme.MUTED,
                      QFont.Weight.Bold, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            draw_text(p, QRectF(r.x(), r.y() + r.height() / 2, r.width(), r.height() / 2), value_txt,
                      13, col, QFont.Weight.DemiBold, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                      mono=True)

        if d:
            row_label(0, "ТЕКСТ", f"‘{byte_repr(tb)}’ = {tb:>3} = 0x{tb:02X}", theme.TEXT)
            row_label(1, "КЛЮЧ", f"‘{byte_repr(kb)}’ = {kb:>3} = 0x{kb:02X}", theme.ACCENT)
            done_all = all(b is not None for b in rbits)
            res_txt = f"‘{byte_repr(rb_partial)}’ = {rb_partial:>3} = 0x{rb_partial:02X}" if done_all else "…"
            row_label(2, "РЕЗУЛЬТАТ", res_txt, theme.GREEN)
        else:
            row_label(0, "ТЕКСТ", "—", theme.MUTED)
            row_label(1, "КЛЮЧ", "—", theme.MUTED)
            row_label(2, "РЕЗУЛЬТАТ", "—", theme.MUTED)

        # строки битов
        for i, r in enumerate(rows_rects[0]):
            st = theme.CELL_CURRENT if i == bit else (theme.CELL_DONE if i < bit else theme.CELL_FUTURE)
            draw_cell(p, r, "" if tbits[i] is None else str(tbits[i]), st, mono=True, glow=(i == bit))
        for i, r in enumerate(rows_rects[1]):
            st = theme.CELL_KEY_CURRENT if i == bit else theme.CELL_KEY
            draw_cell(p, r, "" if kbits[i] is None else str(kbits[i]), st, mono=True, glow=(i == bit))
        for i, r in enumerate(rows_rects[2]):
            v = rbits[i]
            if v is None:
                draw_cell(p, r, "", theme.CELL_EMPTY, mono=True)
            elif i == bit:
                # появление результата: масштаб + прозрачность
                s = 0.6 + 0.4 * t
                rr = QRectF(r.center().x() - r.width() * s / 2, r.center().y() - r.height() * s / 2,
                            r.width() * s, r.height() * s)
                draw_cell(p, rr, str(v), theme.CELL_DONE, size=int(r.height() * 0.5), mono=True,
                          alpha=0.3 + 0.7 * t, glow=True)
            else:
                draw_cell(p, r, str(v), theme.CELL_DONE, mono=True)
        # операторы между строками
        op_x = bits_x - 32
        draw_text(p, QRectF(op_x - 14, rows_y[0] + rows_rects[0][0].height() / 2 + row_gap / 2 - 14, 28, 28),
                  "⊕", 22, theme.WARM, QFont.Weight.Bold)
        draw_text(p, QRectF(op_x - 14, rows_y[1] + rows_rects[1][0].height() / 2 + row_gap / 2 - 14, 28, 28),
                  "=", 22, theme.GREEN, QFont.Weight.Bold)
        # разделитель над результатом
        sep_y = rows_y[2] - 10
        p.setPen(QPen(theme.BORDER, 1))
        p.drawLine(QPointF(bits_x, sep_y), QPointF(rows_rects[2][-1].right(), sep_y))
        # номера битов
        for i, r in enumerate(rows_rects[2]):
            draw_text(p, QRectF(r.x(), r.bottom() + 4, r.width(), 14), f"бит {7 - i}", 9, theme.DIM)

        # таблица истинности
        table = [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]
        tx, ty = truth.x() + 18, truth.y() + 40
        draw_text(p, QRectF(tx, ty, 60, 22), "a", 13, theme.MUTED, QFont.Weight.Bold, mono=True)
        draw_text(p, QRectF(tx + 64, ty, 60, 22), "b", 13, theme.MUTED, QFont.Weight.Bold, mono=True)
        draw_text(p, QRectF(tx + 128, ty, 70, 22), "a ⊕ b", 13, theme.MUTED, QFont.Weight.Bold, mono=True)
        for k, (a, b, c) in enumerate(table):
            ry = ty + 30 + k * 46
            active = d is not None and (tbits[bit], kbits[bit]) == (a, b)
            rr = QRectF(tx - 6, ry - 4, truth.width() - 24, 40)
            if active:
                p.setPen(QPen(theme.WARM, 1))
                p.setBrush(with_alpha(theme.WARM, 0.12))
                p.drawRoundedRect(rr, 8, 8)
            col = theme.TEXT if active else theme.MUTED
            draw_text(p, QRectF(tx, ry, 60, 32), str(a), 20, col, QFont.Weight.DemiBold, mono=True)
            draw_text(p, QRectF(tx + 64, ry, 60, 32), str(b), 20, col, QFont.Weight.DemiBold, mono=True)
            draw_text(p, QRectF(tx + 128, ry, 70, 32), str(c), 20,
                      theme.GREEN if active else col, QFont.Weight.Bold, mono=True)
        draw_text(p, QRectF(truth.x(), truth.bottom() - 34, truth.width(), 24),
                  "1, если биты различаются", 12, theme.MUTED)
        y += panel_h + 36

        # ── Результат ─────────────────────────────────────────────────────
        draw_label(p, m, y, "Результат · hex и символ")
        y += 12
        out = d["output"] if d else b""
        cells = layout_row(m, y, len(data), W, max_cell=60)
        for i, r in enumerate(cells):
            if i < len(out) - 1:
                self._byte_cell(p, r, out[i], theme.CELL_DONE)
            elif i == len(out) - 1:
                self._byte_cell(p, r, out[i], theme.CELL_CURRENT, alpha=0.35 + 0.65 * t, glow=True)
            else:
                draw_cell(p, r, "", theme.CELL_EMPTY)

    @staticmethod
    def _byte_cell(p, r: QRectF, b: int, state, glow=False, alpha=1.0):
        """Ячейка байта: символ сверху, hex снизу."""
        draw_cell(p, r, "", state, glow=glow, alpha=alpha)
        bg, border, fg = state
        h = r.height()
        draw_text(p, QRectF(r.x(), r.y() + h * 0.08, r.width(), h * 0.52), byte_repr(b),
                  int(h * 0.42), with_alpha(fg, alpha), QFont.Weight.DemiBold)
        draw_text(p, QRectF(r.x(), r.y() + h * 0.58, r.width(), h * 0.36), f"{b:02X}",
                  int(h * 0.24), with_alpha(theme.MUTED if state is not theme.CELL_CURRENT else fg, alpha),
                  mono=True)


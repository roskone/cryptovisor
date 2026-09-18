"""Сцена столбцовой перестановки: исходная строка, таблица с ключом, порядок чтения, результат."""
from __future__ import annotations

from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtGui import QPainter, QFont, QPen

from .base import Scene
from .. import theme
from ..draw import (draw_cell, draw_label, draw_text, draw_card, layout_row, ease, lerp,
                    with_alpha, draw_badge, draw_arrow)


class TranspositionScene(Scene):
    def paint_scene(self, p: QPainter, rect: QRectF):
        ctx, step = self.ctx, self.step
        d = step.data if step else None
        headers: list[str] = ctx["headers"]
        ranks: list[int] = ctx["ranks"]
        order: list[int] = ctx["order"]
        rows, cols = ctx["rows"], ctx["cols"]
        source: str = ctx["source"]
        mode = ctx["mode"]
        phase = d["phase"] if d else None
        t = ease(self._progress)
        m = 40
        W = rect.width() - 2 * m
        y = 34

        # ── Исходная строка ───────────────────────────────────────────────
        src_index = d["src_index"] if d else None
        n_src_done = 0
        if d:
            if phase == "fill":
                n_src_done = src_index  # текущий ещё «летит»
            elif phase in ("order", "read"):
                n_src_done = len(source) if (mode == "dec" or phase == "read" or d["ranks_shown"] > 0) else 0
                if mode == "dec" and phase == "order":
                    n_src_done = 0
        draw_label(p, m, y, "Шифртекст" if mode == "dec" else "Исходный текст")
        y += 12
        src_cells = layout_row(m, y, len(source), W, max_cell=60)
        for i, r in enumerate(src_cells):
            if i < n_src_done:
                draw_cell(p, r, source[i], theme.CELL_DONE)
            elif i == src_index:
                draw_cell(p, r, source[i], theme.CELL_CURRENT, alpha=1 - 0.6 * t, glow=True)
            else:
                draw_cell(p, r, source[i], theme.CELL_FUTURE)
        cell_h = src_cells[0].height() if src_cells else 54
        y += cell_h + 34

        # ── Таблица ───────────────────────────────────────────────────────
        avail_h = rect.height() - y - 150
        side_w = 300
        table_area = QRectF(m, y, W - side_w - 20, avail_h)
        side = QRectF(table_area.right() + 20, y, side_w, avail_h)
        draw_card(p, table_area, f"Таблица {rows} × {cols}")
        draw_card(p, side, "Порядок столбцов по ключу")

        gap = 8
        header_h = 74
        cell = min(88, (table_area.width() - 40 - gap * (cols - 1)) / cols,
                   (table_area.height() - header_h - 60 - gap * (rows - 1)) / max(rows, 1))
        cell = max(cell, 18)
        grid_w = cols * cell + (cols - 1) * gap
        gx = table_area.center().x() - grid_w / 2
        gy = table_area.y() + 36 + header_h

        ranks_shown = d["ranks_shown"] if d else 0
        active_col = d.get("col") if d else None
        grid = d["grid"] if d else [[None] * cols for _ in range(rows)]
        cur_cell = d["cell"] if d else None

        def cell_rect(r, c) -> QRectF:
            return QRectF(gx + c * (cell + gap), gy + r * (cell + gap), cell, cell)

        # заголовки: буква ключа + номер (если уже присвоен)
        for c in range(cols):
            hr = QRectF(gx + c * (cell + gap), gy - header_h, cell, header_h - 10)
            rank_visible = ranks[c] < ranks_shown
            is_active = phase == "order" and active_col == c
            state = theme.CELL_KEY_CURRENT if (is_active or (phase == "read" and active_col == c)) else theme.CELL_KEY
            draw_cell(p, QRectF(hr.x(), hr.y(), hr.width(), hr.height() * 0.62), headers[c], state,
                      size=int(cell * 0.42), glow=is_active)
            if rank_visible:
                a = t if is_active else 1.0
                draw_badge(p, QPointF(hr.center().x(), hr.bottom() - 4),
                           str(ranks[c] + 1), with_alpha(theme.YELLOW, a), r=12)
        # подсветка активного столбца при чтении
        if phase in ("read",) and active_col is not None:
            band = cell_rect(0, active_col).united(cell_rect(rows - 1, active_col)).adjusted(-5, -5, 5, 5)
            p.setPen(QPen(with_alpha(theme.GREEN, 0.5), 1))
            p.setBrush(with_alpha(theme.GREEN, 0.07))
            p.drawRoundedRect(band, 10, 10)
        if phase == "fill" and mode == "dec" and active_col is not None:
            band = cell_rect(0, active_col).united(cell_rect(rows - 1, active_col)).adjusted(-5, -5, 5, 5)
            p.setPen(QPen(with_alpha(theme.YELLOW, 0.5), 1))
            p.setBrush(with_alpha(theme.YELLOW, 0.06))
            p.drawRoundedRect(band, 10, 10)

        out = d["output"] if d else ""
        out_index = d.get("out_index") if d else None
        # ячейки
        for r in range(rows):
            for c in range(cols):
                rr = cell_rect(r, c)
                ch = grid[r][c]
                if ch is None:
                    draw_cell(p, rr, "", theme.CELL_EMPTY)
                    continue
                is_cur = cur_cell == (r, c)
                if phase == "fill" and is_cur:
                    # символ прилетает из исходной строки
                    start = src_cells[src_index].center()
                    pos = lerp(start, rr.center(), t)
                    draw_cell(p, rr, "", theme.CELL_EMPTY)
                    fly = QRectF(pos.x() - rr.width() / 2, pos.y() - rr.height() / 2, rr.width(), rr.height())
                    draw_cell(p, fly, ch, theme.CELL_CURRENT, glow=True)
                elif phase == "read" and is_cur:
                    draw_cell(p, rr, ch, theme.CELL_CURRENT, glow=True)
                elif phase == "read" and _already_read(mode, order, rows, cols, cur_cell, r, c):
                    draw_cell(p, rr, ch, theme.CELL_DONE, alpha=0.55)
                else:
                    draw_cell(p, rr, ch, theme.CELL_DONE)

        # ── Боковая панель: порядок ───────────────────────────────────────
        sx, sy = side.x() + 18, side.y() + 42
        draw_text(p, QRectF(sx, sy, side.width() - 36, 20), f"ключ: {''.join(headers)}", 14, theme.MUTED,
                  align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, mono=True)
        sy += 30
        for k, c in enumerate(order):
            visible = k < ranks_shown
            ry = sy + k * 36
            active = active_col == c and phase in ("order", "read", "fill")
            if active:
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(with_alpha(theme.YELLOW, 0.12))
                p.drawRoundedRect(QRectF(sx - 8, ry - 3, side.width() - 20, 32), 8, 8)
            col = theme.TEXT if visible else theme.MUTED
            draw_badge(p, QPointF(sx + 12, ry + 13), str(k + 1), theme.YELLOW if visible else theme.BORDER,
                       theme.BG if visible else theme.MUTED, r=12)
            draw_text(p, QRectF(sx + 34, ry, side.width() - 60, 26),
                      f"столбец ‘{headers[c]}’  (№{c + 1} слева)" if visible else "?", 15, col,
                      align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        note_y = side.bottom() - 62
        note = ("Столбцы читаются сверху вниз\nв порядке номеров" if mode == "enc"
                else "Шифртекст заполняет столбцы\nв порядке номеров, читаем по строкам")
        draw_text(p, QRectF(side.x() + 14, note_y, side.width() - 28, 50), note, 12, theme.MUTED)
        y = table_area.bottom() + 34

        # ── Результат ─────────────────────────────────────────────────────
        draw_label(p, m, y, "Результат")
        y += 12
        out_cells = layout_row(m, y, len(source), W, max_cell=60)
        for i, r in enumerate(out_cells):
            if i < len(out) - 1:
                draw_cell(p, r, out[i], theme.CELL_DONE)
            elif i == len(out) - 1 and phase == "read":
                start = cell_rect(*cur_cell).center()
                pos = lerp(start, r.center(), t)
                draw_cell(p, r, "", theme.CELL_EMPTY)
                fly = QRectF(pos.x() - r.width() / 2, pos.y() - r.height() / 2, r.width(), r.height())
                draw_cell(p, fly, out[i], theme.CELL_CURRENT, glow=True)
            else:
                draw_cell(p, r, "", theme.CELL_EMPTY)


def _already_read(mode, order, rows, cols, cur, r, c) -> bool:
    """Была ли ячейка (r, c) уже прочитана до текущей ячейки cur."""
    if cur is None:
        return False
    cr, cc = cur
    if mode == "enc":
        return order.index(c) < order.index(cc) or (c == cc and r < cr)
    return (r, c) < (cr, cc)

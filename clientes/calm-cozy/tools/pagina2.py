"""Página 2 de los libros Calm & Cozy: "This book belongs to", How to Play con íconos
y un mini ejemplo por tipo de puzzle (sopa, sudoku, laberinto), aviso de soluciones y copyright.

Sigue la línea de la p2 con íconos de Big Print Word Hunt (generar.instructions_icons).
"""
import html
import random
import re

import puzzles as PZ
from generar import ICON, icon

ICON.update({
    "grid9": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18M15 3v18M3 9h18M3 15h18"/>',
    "norep": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7.5 8.5l9 7M16.5 8.5l-9 7"/>',
    "start": '<path d="M3 12h13M12 7l5 5-5 5"/><path d="M21 4v16"/>',
    "path": '<path d="M4 20V13h7V6h9"/><circle cx="4" cy="20" r="1.4"/><path d="M17 3l3 3-3 3"/>',
    "cup": '<path d="M4 9h12v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M16 11h1.5a2.5 2.5 0 0 1 0 5H16"/>'
           '<path d="M8 3.5c0 1.5 1.5 1.5 1.5 3M12 3.5c0 1.5 1.5 1.5 1.5 3"/>',
})

CSS = """
.p2 {{ width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; }}
.p2 .belongs {{ width: 100%; font-size: 16pt; font-weight: 700; display: flex; align-items: flex-end; gap: 0.1in;
               margin: 0.02in 0 0.22in; }}
.p2 .belongs span {{ flex: 1; border-bottom: 1.5px solid #111; height: 1.2em; }}
.p2 .howbox {{ border: 2px solid #111; border-radius: 12px; padding: 0.03in 0.36in; font-size: 22pt; font-weight: 700;
              margin: 0 0 0.16in; }}
.p2 .card {{ width: 100%; display: flex; align-items: center; gap: 0.3in; border: 1.5px solid #111; border-radius: 14px;
            padding: 0.2in 0.24in; margin-bottom: 0.18in; }}
.p2 .ex {{ flex: none; width: 2.05in; display: flex; justify-content: center; }}
.p2 .ex svg {{ width: 100%; height: auto; max-height: 1.95in; }}
.p2 .txt {{ flex: 1; }}
.p2 .txt h2 {{ font-size: 17pt; margin: 0 0 0.06in; }}
.p2 .step {{ display: flex; align-items: center; gap: 0.12in; font-size: 13.5pt; line-height: 1.25; margin: 0.06in 0; }}
.p2 .step .ico {{ flex: none; }}
.p2 .solnote {{ width: 100%; display: flex; align-items: center; justify-content: center; gap: 0.14in;
               font-size: 15pt; margin-top: 0.04in; }}
.p2 .copyright {{ position: static; margin-top: auto; margin-bottom: 0.12in; width: 100%; border-top: 1.5px solid #999; padding-top: 0.1in;
                 font-size: 9pt; color: #444; text-align: center; line-height: 1.35; }}
"""


def _word_example():
    rows = ["TEARBN", "SCUPWH", "OJAFED", "CYVLGR", "KPNEMO", "BWIDFU"]
    marks = [(0, 0, 0, 2), (1, 0, 4, 0), (1, 1, 4, 4)]  # TEA →, SOCK ↓, CALM ↘
    cell, n = 30, len(rows)
    inside = set()
    out = [f'<svg viewBox="-8 -8 {n*cell+16} {n*cell+16}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect x="-6" y="-6" width="{n*cell+12}" height="{n*cell+12}" rx="8" fill="#fff" stroke="#111" stroke-width="2.5"/>']
    for r1, c1, r2, c2 in marks:
        dr, dc = (r2 > r1) - (r2 < r1), (c2 > c1) - (c2 < c1)
        for t in range(max(abs(r2 - r1), abs(c2 - c1)) + 1):
            inside.add((r1 + dr * t, c1 + dc * t))
        out.append(f'<line x1="{c1*cell+cell/2}" y1="{r1*cell+cell/2}" x2="{c2*cell+cell/2}" y2="{r2*cell+cell/2}" '
                   'stroke="#111" stroke-width="25" stroke-linecap="round"/>')
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            fill = "#fff" if (r, c) in inside else "#111"
            out.append(f'<text x="{c*cell+cell/2}" y="{r*cell+cell/2+7}" text-anchor="middle" font-size="19" '
                       f'font-weight="700" font-family="Liberation Sans, Arial" fill="{fill}">{ch}</text>')
    out.append("</svg>")
    return "".join(out)


def _sudoku_example():
    box = [[5, 3, 2], [6, 0, 1], [9, 8, 4]]  # falta el 7
    cell = 56
    s = 3 * cell
    out = [f'<svg viewBox="-6 -6 {s+12} {s+12}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect x="0" y="0" width="{s}" height="{s}" fill="#fff"/>']
    for i in range(4):
        w = 6 if i in (0, 3) else 2.5
        out.append(f'<line x1="{i*cell}" y1="0" x2="{i*cell}" y2="{s}" stroke="#111" stroke-width="{w}" stroke-linecap="square"/>')
        out.append(f'<line x1="0" y1="{i*cell}" x2="{s}" y2="{i*cell}" stroke="#111" stroke-width="{w}" stroke-linecap="square"/>')
    for r in range(3):
        for c in range(3):
            x, y = c * cell + cell / 2, r * cell + cell / 2 + 12
            if box[r][c]:
                out.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="34" font-weight="700" '
                           f'font-family="Liberation Sans, Arial" fill="#111">{box[r][c]}</text>')
            else:
                out.append(f'<circle cx="{x}" cy="{r*cell+cell/2}" r="21" fill="#111"/>'
                           f'<text x="{x}" y="{y}" text-anchor="middle" font-size="34" font-weight="700" '
                           f'font-family="Liberation Sans, Arial" fill="#fff">7</text>')
    out.append("</svg>")
    return "".join(out)


def _maze_example():
    mz = PZ.make_maze(random.Random(4), 6, 6)
    cell, lw = 30, 5
    svg = PZ.maze_svg(mz, solve=True, cell=cell, lw=lw)
    W, H = 6 * cell, 6 * cell
    # las flechas de entrada y salida quedan fuera del viewBox original: se amplía
    return re.sub(r'class="maze" viewBox="[^"]*"', f'viewBox="{-cell} {-lw} {W + 2*cell} {H + 2*lw}"', svg, count=1)


def css():
    return CSS.format()


def page2(book, sol_start):
    def steps(rows):
        return "".join(f'<div class="step">{icon(ic, "0.27in")}<span>{tx}</span></div>' for ic, tx in rows)

    cards = [
        (_word_example(), "Word Search", [
            ("list", "Look for each word from the list."),
            ("lens", "Words go across, down or diagonally. <b>Never backwards.</b>"),
            ("pencil", "Circle it in the grid and cross it off."),
        ]),
        (_sudoku_example(), "Easy Sudoku", [
            ("grid9", "Fill each empty square with <b>1 to 9</b>."),
            ("norep", "No repeats in any <b>row</b>, <b>column</b> or <b>3&times;3 box</b>."),
            ("check", "Each puzzle has only one solution."),
        ]),
        (_maze_example(), "Mazes", [
            ("start", "Start at the arrow on the left."),
            ("path", "Find the one path to the arrow on the right."),
            ("pencil", "Use a pencil so you can try again."),
        ]),
    ]
    body = "".join(f'<div class="card"><div class="ex">{ex}</div><div class="txt"><h2>{t}</h2>{steps(st)}</div></div>'
                   for ex, t, st in cards)
    copyright = ""
    if book.get("author"):
        copyright = (f'<div class="copyright">Copyright &copy; {book.get("year", "")} {html.escape(book["author"])}. '
                     'All rights reserved. No part of this book may be reproduced in any form without written '
                     'permission from the authors.</div>')
    return ('<div class="p2"><div class="belongs">This book belongs to<span></span></div>'
            f'<div class="howbox">How to Play</div>{body}'
            f'<div class="solnote">{icon("cup", "0.4in")}<span><b>Take your time. Stuck? Solutions start on page '
            f'{sol_start}.</b></span></div>{copyright}</div>')

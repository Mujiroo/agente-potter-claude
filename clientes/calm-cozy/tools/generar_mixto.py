#!/usr/bin/env python3
"""Generador de los libros híbridos "Calm & Cozy" (sopas de letras + sudokus + laberintos).

Entrada: JSON con
  {
    "title": "Calm & Cozy Puzzles", "subtitle": "...", "volume": "Vol. 1",
    "trim": [8.5, 11], "size": 15, "seed": 1, "author": "...", "year": 2026,
    "word_puzzles": [{"theme": "Cozy Mornings", "words": [9 palabras]}, ...],
    "sudokus": 20, "mazes": 10
  }
Salida: HTML de páginas listo para imprimir a PDF con Chrome.

Orden del libro: título, instrucciones, los puzzles intercalados (sopas, y cada
cierto tramo un sudoku o un laberinto) y al final todas las soluciones.

Uso: generar_mixto.py libro.json salida.html
"""
import html
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "libro-sopa-de-letras", "tools"))

import puzzles as PZ  # noqa: E402
import pagina2  # noqa: E402
from generar import FORWARD, build, words_block  # noqa: E402
from generar import grid_svg as _grid_svg  # noqa: E402


def grid_svg(grid, placed=None):
    """La grilla de generar.py con aire entre las letras del borde y el marco (en 13x13 quedaban pegadas)."""
    s = len(grid) * 40
    svg = _grid_svg(grid, placed)
    svg = svg.replace(f'viewBox="0 0 {s} {s}"', f'viewBox="-14 -14 {s+28} {s+28}"', 1)
    return svg.replace(f'<rect x="1.5" y="1.5" width="{s-3}" height="{s-3}" rx="10"',
                       f'<rect x="-11" y="-11" width="{s+22}" height="{s+22}" rx="14"', 1)

GUTTER, OUTSIDE, TOP, BOTTOM = 0.6, 0.5, 0.5, 0.7


def css(w, h):
    live = w - GUTTER - OUTSIDE
    return f"""
@page {{ size: {w}in {h}in; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: 'Liberation Sans', Arial, sans-serif; color: #111; }}
.page {{ width: {w}in; height: {h}in; padding: {TOP}in {OUTSIDE}in {BOTTOM}in {GUTTER}in; position: relative;
        page-break-after: always; display: flex; flex-direction: column; align-items: center; overflow: hidden; }}
.page.even {{ padding-left: {OUTSIDE}in; padding-right: {GUTTER}in; }}
.num {{ position: absolute; bottom: 0.34in; left: {GUTTER}in; right: {OUTSIDE}in; text-align: center; font-size: 11pt; }}
.even .num {{ left: {OUTSIDE}in; right: {GUTTER}in; }}
.tag {{ font-size: 11pt; color: #555; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 0.06in; }}
h1 {{ font-size: 26pt; margin: 0 0 0.16in; text-align: center; }}
.grid {{ width: {live:.2f}in; height: {live:.2f}in; }}
.grid text {{ font-size: 26px; font-weight: 700; font-family: 'Liberation Sans', Arial; }}
.words {{ display: flex; justify-content: space-between; gap: 0.12in; width: {live:.2f}in; margin-top: 0.22in; }}
.words ul {{ list-style: none; margin: 0; padding: 0; }}
.words li {{ font-size: 16pt; font-weight: 700; line-height: 1.5; text-transform: uppercase; white-space: nowrap; }}
.sudoku {{ width: {min(live, 6.2):.2f}in; height: {min(live, 6.2):.2f}in; }}
.maze {{ width: {live:.2f}in; }}
.hint {{ font-size: 13pt; color: #444; margin-top: 0.22in; text-align: center; }}
.title-page {{ justify-content: center; text-align: center; }}
.title-page .big {{ font-size: 46pt; font-weight: 900; line-height: 1.05; }}
.title-page .sub {{ font-size: 22pt; margin-top: 0.18in; font-weight: 700; }}
.title-page .vol {{ font-size: 15pt; margin-top: 0.14in; letter-spacing: 3px; }}
.title-page .note {{ font-size: 14pt; margin-top: 0.5in; color: #555; }}
.instr {{ width: 100%; font-size: 15pt; line-height: 1.45; text-align: left; }}
.instr h1 {{ text-align: left; }}
.instr li {{ margin-bottom: 0.1in; }}
.sol2 {{ display: flex; flex-wrap: wrap; gap: 0.3in; justify-content: center; width: 100%; }}
.sol2 .item {{ width: 45%; text-align: center; font-size: 12pt; }}
.sol2 .sudoku, .sol2 .maze {{ width: 100%; height: auto; }}
.page.center {{ justify-content: center; }}
.page.center .sudoku {{ width: 7in; height: 7in; }}
.hint {{ }}
.title-page .tp-author {{ font-family: 'Playfair Display', serif; font-size: 14pt; letter-spacing: 6px; }}
.title-page .tp-script {{ font-family: 'Caveat', cursive; font-size: 60pt; line-height: 1; margin-top: 0.35in; }}
.title-page .tp-title {{ font-family: 'Playfair Display', serif; font-size: 66pt; font-weight: 700; letter-spacing: 6px; line-height: 1; }}
.title-page .tp-sub {{ font-family: 'Playfair Display', serif; font-size: 18pt; margin-top: 0.2in; }}
.title-page .tp-icons {{ display: flex; gap: 0.45in; justify-content: center; align-items: center; margin-top: 0.55in; }}
.title-page .tp-icons > div {{ width: 1.55in; }}
.title-page .tp-icons svg {{ width: 100%; height: auto; }}
.title-page .tp-vol {{ font-family: 'Playfair Display', serif; font-size: 16pt; letter-spacing: 5px; margin-top: 0.55in; }}
.title-page .tp-note {{ font-size: 13pt; color: #444; margin-top: 0.15in; }}
.sol6 {{ display: grid; grid-template-columns: repeat(2, 2.45in); gap: 0.16in 0.9in; justify-content: center; width: 100%; margin-top: 0.1in; }}
.sol6 .item, .sol4 .item {{ text-align: center; font-size: 12pt; }}
.sol6 .sudoku {{ width: 2.45in; height: 2.45in; }}
.sol4 {{ display: grid; grid-template-columns: repeat(2, 3.45in); gap: 0.35in 0.4in; justify-content: center; width: 100%; margin-top: 0.15in; }}
.sol4 .maze {{ width: 3.45in; height: auto; }}
.copyright {{ position: absolute; bottom: 0.9in; left: 0; right: 0; text-align: center; font-size: 9pt; color: #444; }}
"""


def main(src, dst):
    book = json.load(open(src, encoding="utf-8"))
    w, h = book.get("trim", [8.5, 11])
    size = book.get("size", 15)
    rng = random.Random(book.get("seed", 1))
    pages = []

    def page(body, cls=""):
        n = len(pages) + 1
        parity = "even" if n % 2 == 0 else "odd"
        num = f'<div class="num">{n}</div>' if n > 1 else ""
        pages.append(f'<section class="page {parity} {cls}">{body}{num}</section>')

    cv = book.get("cover", {})
    if cv:
        page(f'<div class="tp-author">{html.escape(cv["author"].upper())}</div>'
             f'<div class="tp-script">{html.escape(cv["script"])}</div>'
             f'<div class="tp-title">{html.escape(cv["title"])}</div>'
             f'<div class="tp-sub">Word Search &middot; Easy Sudoku &middot; Mazes</div>'
             f'<div class="tp-icons"><div>{pagina2._word_example()}</div><div>{pagina2._sudoku_example()}</div>'
             f'<div>{pagina2._maze_example()}</div></div>'
             f'<div class="tp-vol">{html.escape(book.get("volume", "").upper())}</div>'
             f'<div class="tp-note">{html.escape(book.get("tagline", ""))}</div>', "title-page")
    else:
        page(f'<div class="big">{html.escape(book["title"])}</div>'
             f'<div class="sub">{html.escape(book.get("subtitle", ""))}</div>'
             f'<div class="vol">{html.escape(book.get("volume", ""))}</div>'
             f'<div class="note">{html.escape(book.get("tagline", ""))}</div>', "title-page")

    n_words, n_sud, n_maze = len(book["word_puzzles"]), book.get("sudokus", 0), book.get("mazes", 0)
    total = n_words + n_sud + n_maze
    tips = book.get("tips_page", False)
    sol_start = 3 + total + (1 if tips else 0)
    if book.get("instructions_style") == "icons":
        page(pagina2.page2(book, sol_start))
        if tips:
            page(pagina2.page3())
    else:
        page('<div class="instr"><h1>How to Play</h1>'
             '<p><b>Word searches.</b> Find every word from the list in the grid. Words read '
             '<b>left to right</b> or <b>top to bottom</b> — across, down or diagonally. '
             'No words are spelled backwards.</p>'
             '<p><b>Sudoku.</b> Fill the grid so every row, every column and every 3x3 box '
             'contains the numbers 1 to 9, with no repeats. Every puzzle has one single solution.</p>'
             '<p><b>Mazes.</b> Start at the arrow on the left and find your way to the arrow on the right. '
             'There is only one path through.</p>'
             f'<p>Take your time — and if you get stuck, the solutions start on page {sol_start}.</p>'
             '<p><b>Relax and enjoy.</b></p></div>'
             + (f'<div class="copyright">Copyright &copy; {book.get("year", "")} {html.escape(book.get("author", ""))}. '
                'All rights reserved.</div>' if book.get("author") else ""))

    # secuencia: 4 sopas, 1 sudoku; cada 4 sudokus, 1 laberinto; lo que sobre va al final
    seq = []
    wq, sud_left, maze_left = list(range(n_words)), n_sud, n_maze
    sud_done = 0
    while wq or sud_left or maze_left:
        progress = False
        for _ in range(4):
            if wq:
                seq.append(("w", wq.pop(0)))
                progress = True
        if sud_left:
            seq.append(("s", None))
            sud_left -= 1
            sud_done += 1
            progress = True
            if maze_left and sud_done % 4 == 0:
                seq.append(("m", None))
                maze_left -= 1
        elif maze_left:
            seq.append(("m", None))
            maze_left -= 1
            progress = True
        if not progress:
            break

    # se generan antes y se ordenan: los sudokus de más pistas a menos, los laberintos de camino corto a largo
    sud_pool = sorted((PZ.make_easy_sudoku(rng) for _ in range(n_sud)), key=lambda t: -t[2])
    maze_pool = sorted((PZ.make_maze(rng, 17, 17) for _ in range(n_maze)), key=lambda m: len(m["path"]))
    solved_w, solved_s, solved_m = [], [], []
    wi = si = mi = 0
    for kind, idx in seq:
        if kind == "w":
            p = book["word_puzzles"][idx]
            wi += 1
            grid, placed = build(p["words"], size, rng, FORWARD)
            solved_w.append((wi, p, grid, placed))
            page(f'<div class="tag">Word Search {wi}</div><h1>{html.escape(p["theme"])}</h1>'
                 f'{grid_svg(grid)}{words_block(p["words"])}')
        elif kind == "s":
            si += 1
            pz, sol, givens = sud_pool[si - 1]
            solved_s.append((si, pz, sol))
            page(f'<div class="tag">Sudoku {si}</div><h1>Easy</h1>{PZ.sudoku_svg(pz)}'
                 '<div class="hint">Fill in 1 to 9 — no repeats in any row, column or box.</div>', "center")
        else:
            mi += 1
            mz = maze_pool[mi - 1]
            solved_m.append((mi, mz))
            page(f'<div class="tag">Maze {mi}</div><h1>Find the Way</h1>{PZ.maze_svg(mz)}'
                 '<div class="hint">Start at the arrow on the left, finish at the arrow on the right.</div>', "center")

    page('<div class="divider"><div class="tp-script">Solutions</div>'
         '<div class="tp-sub">Word Search &middot; Easy Sudoku &middot; Mazes</div></div>', "title-page")
    for i, p, grid, placed in solved_w:
        page(f'<div class="tag">Word Search {i}</div><h1>{html.escape(p["theme"])}</h1>'
             f'{grid_svg(grid, placed)}{words_block(p["words"])}')
    for k in range(0, len(solved_s), 6):  # seis sudokus por página (2 x 3)
        items = "".join(f'<div class="item">{PZ.sudoku_svg(pz, sol, cell=46)}<div>Sudoku {i}</div></div>'
                        for i, pz, sol in solved_s[k:k + 6])
        page(f'<div class="tag">Solutions</div><h1>Sudoku</h1><div class="sol6">{items}</div>')
    for k in range(0, len(solved_m), 4):  # cuatro laberintos por página (2 x 2)
        items = "".join(f'<div class="item">{PZ.maze_svg(mz, solve=True, cell=26, lw=6)}<div>Maze {i}</div></div>'
                        for i, mz in solved_m[k:k + 4])
        page(f'<div class="tag">Solutions</div><h1>Mazes</h1><div class="sol4">{items}</div>')

    if book.get("thanks_page"):
        page(pagina2.thanks_page(book), "center")
    from portada_cozy import font_css
    fonts = font_css()
    with open(dst, "w", encoding="utf-8") as f:
        f.write(f'<!doctype html><html><head><meta charset="utf-8">'
                f'<title>{html.escape(book["title"])} (interior)</title>'
                f'<style>{fonts}{css(w, h)}{pagina2.css()}</style></head><body>{"".join(pages)}</body></html>')
    print(f"{len(pages)} páginas {w}x{h} | sopas {wi} · sudokus {si} · laberintos {mi} -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

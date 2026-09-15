#!/usr/bin/env python3
"""Generador de libros de sopa de letras (serie de Pedro).

Entrada: un JSON con el libro:
  {
    "title": "AISLE HUNT!", "subtitle": "Supermarket Word Search",
    "size": 15, "seed": 1,
    "puzzles": [{"theme": "Fruits" (opcional), "words": ["APPLE", ...9]}, ...]
  }
Salida: un HTML de páginas 8.5x11" (1 título, 1 instrucciones, N puzzles, N soluciones),
que se imprime a PDF con Chrome (agent-browser pdf).

Uso: generar.py libro.json salida.html
"""
import html
import json
import random
import sys

DIRS = [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def clean(word):
    return "".join(c for c in word.upper() if c.isalpha())


def build(words, size, rng, tries=2000):
    """Coloca las palabras (largas primero); devuelve grilla y posiciones."""
    for _ in range(50):
        grid = [[None] * size for _ in range(size)]
        placed = {}
        ok = True
        for w in sorted(words, key=lambda x: -len(clean(x))):
            letters = clean(w)
            if len(letters) > size:
                raise ValueError(f"'{w}' no cabe en una grilla de {size}")
            for _ in range(tries):
                dr, dc = rng.choice(DIRS)
                r, c = rng.randrange(size), rng.randrange(size)
                er, ec = r + dr * (len(letters) - 1), c + dc * (len(letters) - 1)
                if not (0 <= er < size and 0 <= ec < size):
                    continue
                cells = [(r + dr * i, c + dc * i) for i in range(len(letters))]
                if all(grid[y][x] in (None, letters[i]) for i, (y, x) in enumerate(cells)):
                    for i, (y, x) in enumerate(cells):
                        grid[y][x] = letters[i]
                    placed[w] = cells
                    break
            else:
                ok = False
                break
        if ok:
            for y in range(size):
                for x in range(size):
                    if grid[y][x] is None:
                        grid[y][x] = rng.choice(ALPHA)
            # cada palabra debe aparecer UNA sola vez, si no la solución es ambigua
            if all(occurrences(grid, clean(w)) == 1 for w in words):
                return grid, placed
    raise RuntimeError(f"No pude colocar: {words}")


def occurrences(grid, letters):
    n = len(grid)
    count = 0
    for r in range(n):
        for c in range(n):
            for dr, dc in DIRS:
                er, ec = r + dr * (len(letters) - 1), c + dc * (len(letters) - 1)
                if 0 <= er < n and 0 <= ec < n and all(
                        grid[r + dr * k][c + dc * k] == letters[k] for k in range(len(letters))):
                    count += 1
    # un palíndromo se lee igual al revés: cuenta doble en la misma posición
    return count // 2 if letters == letters[::-1] else count


def grid_svg(grid, placed=None):
    n = len(grid)
    cell = 40
    s = n * cell
    out = [f'<svg class="grid" viewBox="0 0 {s} {s}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect x="1" y="1" width="{s-2}" height="{s-2}" rx="10" fill="none" stroke="#222" stroke-width="2.5"/>']
    if placed:
        for cells in placed.values():
            (y1, x1), (y2, x2) = cells[0], cells[-1]
            out.append(f'<line x1="{x1*cell+cell/2}" y1="{y1*cell+cell/2}" x2="{x2*cell+cell/2}" '
                       f'y2="{y2*cell+cell/2}" stroke="#cfcfcf" stroke-width="30" stroke-linecap="round"/>')
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            out.append(f'<text x="{x*cell+cell/2}" y="{y*cell+cell/2}" text-anchor="middle" '
                       f'dominant-baseline="central">{ch}</text>')
    out.append("</svg>")
    return "".join(out)


def words_block(words):
    cols = [words[i:i + 3] for i in range(0, len(words), 3)]
    return '<div class="words">' + "".join(
        "<ul>" + "".join(f"<li>{html.escape(w)}</li>" for w in col) + "</ul>" for col in cols) + "</div>"


def header(kind, i, p):
    """Con temática: rótulo chico + tema. Sin temática: solo 'Puzzle N'."""
    if p.get("theme"):
        return f'<div class="tag">{kind} {i}</div><h1>{html.escape(p["theme"])}</h1>'
    return f'<div class="tag">&nbsp;</div><h1>{kind} {i}</h1>'


CSS = """
@page { size: 8.5in 11in; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: 'Liberation Sans', Arial, sans-serif; color: #111; }
.page { width: 8.5in; height: 11in; padding: 0.75in; position: relative;
        page-break-after: always; display: flex; flex-direction: column; align-items: center; }
.num { position: absolute; bottom: 0.4in; left: 0; right: 0; text-align: center; font-size: 12pt; }
h1 { font-size: 30pt; margin: 0 0 0.05in; text-align: center; letter-spacing: .5px; }
.tag { font-size: 13pt; color: #555; margin-bottom: 0.25in; text-transform: uppercase; letter-spacing: 2px; }
.grid { width: 7in; height: 7in; }
.grid text { font-size: 24px; font-weight: 700; font-family: 'Liberation Sans', Arial, sans-serif; }
.words { display: flex; justify-content: space-between; width: 6.4in; margin-top: 0.3in; }
.words ul { list-style: none; margin: 0; padding: 0; width: 33%; }
.words li { font-size: 19pt; font-weight: 700; line-height: 1.6; text-transform: uppercase; }
.title-page { justify-content: center; text-align: center; }
.title-page .big { font-size: 64pt; font-weight: 900; line-height: 1; }
.title-page .sub { font-size: 26pt; margin-top: 0.2in; }
.title-page .note { font-size: 13pt; margin-top: 0.6in; color: #666; }
.instr { text-align: left; width: 6.5in; font-size: 17pt; line-height: 1.5; }
.instr h1 { text-align: left; margin-bottom: 0.3in; }
"""


def main(src, dst):
    book = json.load(open(src, encoding="utf-8"))
    size = book.get("size", 15)
    rng = random.Random(book.get("seed", 1))
    puzzles = book["puzzles"]
    pages = []

    pages.append(f'<section class="page title-page"><div class="big">{html.escape(book["title"])}</div>'
                 f'<div class="sub">{html.escape(book.get("subtitle", ""))}</div>'
                 f'<div class="note">{len(puzzles)} Large Print Puzzles &middot; Solutions Included</div></section>')

    pages.append('<section class="page"><div class="instr"><h1>How to Play</h1>'
                 '<p>Each puzzle has a grid of letters and a list of words below it.</p>'
                 '<p>Find every word from the list hidden in the grid. Words can run '
                 '<b>across</b>, <b>up and down</b>, or <b>diagonally</b>, and they can be spelled '
                 '<b>forwards or backwards</b>.</p>'
                 '<p>When you find a word, circle it in the grid and cross it off the list.</p>'
                 '<p>Stuck? The solutions start on page ' + str(3 + len(puzzles)) + '.</p>'
                 '<p><b>Have fun!</b></p></div><div class="num">2</div></section>')

    solved = []
    for i, p in enumerate(puzzles, 1):
        if len(p["words"]) != 9:
            raise ValueError(f"Puzzle {i} tiene {len(p['words'])} palabras, no 9")
        grid, placed = build(p["words"], size, rng)
        solved.append((p, grid, placed))
        pn = 2 + i
        pages.append(f'<section class="page">{header("Puzzle", i, p)}{grid_svg(grid)}{words_block(p["words"])}<div class="num">{pn}</div></section>')

    for i, (p, grid, placed) in enumerate(solved, 1):
        pn = 2 + len(puzzles) + i
        pages.append(f'<section class="page">{header("Solution", i, p)}{grid_svg(grid, placed)}{words_block(p["words"])}<div class="num">{pn}</div></section>')

    with open(dst, "w", encoding="utf-8") as f:
        f.write(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>'
                f'<body>{"".join(pages)}</body></html>')
    print(f"{len(pages)} páginas -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

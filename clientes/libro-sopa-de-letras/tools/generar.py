#!/usr/bin/env python3
"""Generador de libros de sopa de letras (serie de Pedro).

Entrada: un JSON con el libro:
  {
    "title": "Word Search", "subtitle": "Aisle Hunt!", "volume": "Vol. 1",
    "tagline": "55 Large Print Supermarket Puzzles for Adults and Seniors",
    "trim": [6, 9],            # pulgadas (ancho, alto)
    "size": 13, "seed": 1,     # grilla size×size
    "directions": "forward",   # solo izq->der / arriba->abajo (sin palabras al revés) | "all"
    "series_note": "texto al pie de la página de instrucciones" (opcional),
    "puzzles": [{"theme": "Dairy Case" (opcional), "words": ["MILK", ...9]}, ...]
  }
Salida: un HTML con 1 página de título, 1 de instrucciones, N puzzles y N soluciones,
que se imprime a PDF con Chrome:  agent-browser open file://<html> && agent-browser pdf <pdf>

Márgenes KDP (sin sangrado): interior >= 0.375" hasta 150 págs., resto >= 0.25".
Aquí: interior 0.5", exterior 0.35", espejados por página par/impar.

Uso: generar.py libro.json salida.html
"""
import html
import json
import random
import sys

# (fila, columna). Las 4 primeras se leen hacia adelante; las otras 4 son al revés.
DIRS = [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]
FORWARD = DIRS[:4]
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GUTTER, OUTSIDE, TOP, BOTTOM = 0.5, 0.35, 0.4, 0.6


def clean(word):
    return "".join(c for c in word.upper() if c.isalpha())


def build(words, size, rng, dirs=DIRS, tries=2000):
    """Coloca las palabras (largas primero); devuelve grilla y posiciones."""
    for _ in range(200):
        grid = [[None] * size for _ in range(size)]
        placed = {}
        ok = True
        for w in sorted(words, key=lambda x: -len(clean(x))):
            letters = clean(w)
            if len(letters) > size:
                raise ValueError(f"'{w}' no cabe en una grilla de {size}")
            for _ in range(tries):
                dr, dc = rng.choice(dirs)
                r, c = rng.randrange(size), rng.randrange(size)
                er, ec = r + dr * (len(letters) - 1), c + dc * (len(letters) - 1)
                if not (0 <= er < size and 0 <= ec < size):
                    continue
                cells = [(r + dr * i, c + dc * i) for i in range(len(letters))]
                # no esconder una palabra dentro de otra ya puesta (APPLE dentro de PINEAPPLE)
                if any(set(cells) <= set(o) for o in placed.values()):
                    continue
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
            if all(len(occurrences(grid, w, placed)) == 1 for w in words):
                return grid, placed
    raise RuntimeError(f"No pude colocar: {words}")


def occurrences(grid, word, placed):
    """Posiciones donde se lee la palabra, sin contar las que caen dentro de OTRA palabra
    de la lista (inevitable si una contiene a la otra)."""
    letters = clean(word)
    others = [set(c) for w, c in placed.items() if w != word]
    n = len(grid)
    found = set()
    for r in range(n):
        for c in range(n):
            for dr, dc in DIRS:
                cells = [(r + dr * k, c + dc * k) for k in range(len(letters))]
                if all(0 <= y < n and 0 <= x < n for y, x in cells) and all(
                        grid[y][x] == letters[k] for k, (y, x) in enumerate(cells)):
                    if not any(set(cells) <= o for o in others):
                        found.add(frozenset(cells))  # un palíndromo no cuenta doble
    return found


def grid_svg(grid, placed=None):
    n = len(grid)
    cell = 40
    s = n * cell
    out = [f'<svg class="grid" viewBox="0 0 {s} {s}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect x="1.5" y="1.5" width="{s-3}" height="{s-3}" rx="10" fill="none" stroke="#222" stroke-width="3"/>']
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


def css(w, h):
    live = w - GUTTER - OUTSIDE
    k = w / 8.5  # escala tipográfica respecto del diseño original 8.5x11
    return f"""
@page {{ size: {w}in {h}in; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: 'Liberation Sans', Arial, sans-serif; color: #111; }}
.page {{ width: {w}in; height: {h}in; padding: {TOP}in {OUTSIDE}in {BOTTOM}in {GUTTER}in; position: relative;
        page-break-after: always; display: flex; flex-direction: column; align-items: center; overflow: hidden; }}
.page.even {{ padding-left: {OUTSIDE}in; padding-right: {GUTTER}in; }}
.num {{ position: absolute; bottom: 0.3in; left: {GUTTER}in; right: {OUTSIDE}in; text-align: center; font-size: 10pt; }}
.even .num {{ left: {OUTSIDE}in; right: {GUTTER}in; }}
h1 {{ font-size: {max(18, 30 * k):.0f}pt; margin: 0 0 0.08in; text-align: center; }}
.tag {{ font-size: 9pt; color: #555; margin-bottom: 0.04in; text-transform: uppercase; letter-spacing: 2px; }}
.grid {{ width: {live:.2f}in; height: {live:.2f}in; }}
.grid text {{ font-size: 26px; font-weight: 700; font-family: 'Liberation Sans', Arial, sans-serif; }}
.words {{ display: flex; justify-content: space-between; width: {live - 0.1:.2f}in; margin-top: 0.18in; }}
.words ul {{ list-style: none; margin: 0; padding: 0; width: 33.3%; }}
.words li {{ font-size: {max(12, 19 * k):.0f}pt; font-weight: 700; line-height: 1.45; text-transform: uppercase; white-space: nowrap; }}
.title-page {{ justify-content: center; text-align: center; }}
.title-page .big {{ font-size: {64 * k:.0f}pt; font-weight: 900; line-height: 1; }}
.title-page .sub {{ font-size: {30 * k:.0f}pt; margin-top: 0.15in; font-weight: 700; }}
.title-page .vol {{ font-size: {20 * k:.0f}pt; margin-top: 0.15in; letter-spacing: 3px; }}
.title-page .note {{ font-size: {16 * k:.0f}pt; margin-top: 0.4in; color: #555; max-width: {live - 0.4:.2f}in; }}
.instr {{ text-align: left; width: 100%; font-size: {max(12, 17 * k):.0f}pt; line-height: 1.45; }}
.instr h1 {{ text-align: left; margin-bottom: 0.2in; }}
.series {{ margin-top: auto; margin-bottom: 0.2in; width: 100%; border-top: 1.5px solid #999; padding-top: 0.15in;
          font-size: {max(11, 15 * k):.0f}pt; line-height: 1.45; text-align: center; }}
"""


def main(src, dst):
    book = json.load(open(src, encoding="utf-8"))
    w, h = book.get("trim", [8.5, 11])
    size = book.get("size", 15)
    rng = random.Random(book.get("seed", 1))
    forward = book.get("directions", "all") == "forward"
    dirs = FORWARD if forward else DIRS
    puzzles = book["puzzles"]
    pages = []

    def page(body, cls=""):
        n = len(pages) + 1
        parity = "even" if n % 2 == 0 else "odd"
        num = f'<div class="num">{n}</div>' if n > 1 else ""
        pages.append(f'<section class="page {parity} {cls}">{body}{num}</section>')

    page(f'<div class="big">{html.escape(book["title"])}</div>'
         f'<div class="sub">{html.escape(book.get("subtitle", ""))}</div>'
         f'<div class="vol">{html.escape(book.get("volume", ""))}</div>'
         f'<div class="note">{html.escape(book.get("tagline", ""))}</div>', "title-page")

    how = ('<p>Find every word from the list hidden in the grid. Words always read '
           '<b>left to right</b> or <b>top to bottom</b>: across, down, or diagonally. '
           '<b>No words are spelled backwards.</b></p>' if forward else
           '<p>Find every word from the list hidden in the grid. Words can run '
           '<b>across</b>, <b>up and down</b>, or <b>diagonally</b>, and they can be spelled '
           '<b>forwards or backwards</b>.</p>')
    note = f'<div class="series">{book["series_note"]}</div>' if book.get("series_note") else ""
    page('<div class="instr"><h1>How to Play</h1>'
         '<p>Each puzzle has a grid of letters and a list of words below it.</p>' + how +
         '<p>When you find a word, circle it in the grid and cross it off the list.</p>'
         f'<p>Stuck? The solutions start on page {3 + len(puzzles)}.</p>'
         '<p><b>Have fun!</b></p></div>' + note)

    solved = []
    for i, p in enumerate(puzzles, 1):
        if len(p["words"]) != 9:
            raise ValueError(f"Puzzle {i} tiene {len(p['words'])} palabras, no 9")
        grid, placed = build(p["words"], size, rng, dirs)
        solved.append((p, grid, placed))
        page(f'{header("Puzzle", i, p)}{grid_svg(grid)}{words_block(p["words"])}')

    for i, (p, grid, placed) in enumerate(solved, 1):
        page(f'{header("Solution", i, p)}{grid_svg(grid, placed)}{words_block(p["words"])}')

    with open(dst, "w", encoding="utf-8") as f:
        f.write(f'<!doctype html><html><head><meta charset="utf-8"><style>{css(w, h)}</style></head>'
                f'<body>{"".join(pages)}</body></html>')
    print(f"{len(pages)} páginas {w}x{h} -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

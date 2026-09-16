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
    "puzzles": [{"phrase": "Grab a Cart!" | "theme": "Dairy Case" (opcional), "words": ["MILK", ...9]}, ...]
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
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# (fila, columna). Las 4 primeras se leen hacia adelante; las otras 4 son al revés.
DIRS = [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]
FORWARD = DIRS[:4]
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GUTTER, OUTSIDE, TOP, BOTTOM = 0.5, 0.35, 0.4, 0.6
WORD_PT = 14  # 16 pt no cabe en 3 columnas con palabras como CHICKEN THIGH (probado)


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
            base = [row[:] for row in grid]
            for _ in range(100):  # re-sortear solo el relleno, manteniendo las palabras
                grid = [row[:] for row in base]
                for y in range(size):
                    for x in range(size):
                        if grid[y][x] is None:
                            grid[y][x] = rng.choice(ALPHA)
                # cada palabra UNA sola vez (si no, la solución es ambigua) y ninguna palabra
                # inapropiada formada por el relleno, en ninguna dirección
                if (all(len(occurrences(grid, w, placed)) == 1 for w in words)
                        and not bad_words(grid, placed)):
                    return grid, placed
    raise RuntimeError(f"No pude colocar: {words}")


# Palabras que no deben quedar escondidas por azar en el relleno (en ninguna dirección).
# Si una aparece DENTRO de una palabra de la lista (RAPE en GRAPE, CUM en CUCUMBER) se tolera.
BAD = ("ASS SEX TIT TITS FUCK FUK FUC SHIT CRAP DAMN PISS DICK COCK CUNT FAG NAZI KKK SLUT WHORE HOE "
       "BITCH PORN NIGGER NIGGA NIG RAPE BOOB JIZZ CUM ANAL ANUS PENIS SCREW HELL DUMB IDIOT KILL DIE DEAD "
       "GAY HAG PIG FAT UGLY STUPID HATE "
       "JEW JEWS KIKE SPIC CHINK GOOK WOP RETARD TRANNY ARSE TWAT WANK PUSSY BASTARD").split()

# Ocho direcciones: la promesa "sin palabras al revés" vale para la LISTA, no para el
# relleno. Una grosería escondida se ve igual leída de derecha a izquierda o de abajo
# hacia arriba, así que aquí se buscan en todas las direcciones.
BAD_DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def bad_words(grid, placed):
    n = len(grid)
    inside = [set(c) for c in placed.values()]
    for w in BAD:
        for r in range(n):
            for c in range(n):
                if grid[r][c] != w[0]:
                    continue
                for dr, dc in BAD_DIRS:
                    cells = [(r + dr * k, c + dc * k) for k in range(len(w))]
                    if all(0 <= y < n and 0 <= x < n for y, x in cells) and all(
                            grid[y][x] == w[k] for k, (y, x) in enumerate(cells)):
                        if not any(set(cells) <= o for o in inside):
                            return w
    return None


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
        import math
        for cells in placed.values():
            (y1, x1), (y2, x2) = cells[0], cells[-1]
            cx, cy = (x1 + x2 + 1) * cell / 2, (y1 + y2 + 1) * cell / 2
            length = math.hypot(x2 - x1, y2 - y1) * cell + cell * 0.8
            ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
            out.append(f'<rect x="{cx-length/2:.1f}" y="{cy-15}" width="{length:.1f}" height="30" rx="15" '
                       f'fill="none" stroke="#000" stroke-width="2.6" transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})"/>')
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
    """Con frase: 'PUZZLE N' grande + frase. Con temática: rótulo chico + tema. Si no: solo 'Puzzle N'."""
    if p.get("phrase"):
        return f'<h1 class="num-title">{kind} {i}</h1><div class="phrase">{html.escape(p["phrase"])}</div>'
    if p.get("theme"):
        return f'<div class="tag">{kind} {i}</div><h1>{html.escape(p["theme"])}</h1>'
    return f'<div class="tag">&nbsp;</div><h1>{kind} {i}</h1>'



ICON = {  # íconos de línea propios, 24x24
    "list": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8.5 8h7M8.5 12h7M8.5 16h5"/>',
    "lens": '<circle cx="10" cy="10" r="6"/><path d="M14.5 14.5L20 20"/>',
    "pencil": '<path d="M4 20l1.2-4.4L16 4.8a2 2 0 0 1 2.8 0l.4.4a2 2 0 0 1 0 2.8L8.4 18.8z"/><path d="M14 6.8l3.2 3.2"/>',
    "cart": '<path d="M3 4h2.5l2.2 10.5h10.3l2-7.5H7"/><circle cx="9.5" cy="19" r="1.6"/><circle cx="16.5" cy="19" r="1.6"/>',
    "check": '<circle cx="12" cy="12" r="9.5"/><path d="M7.5 12.5l3 3 6-6.5"/>',
}


def icon(name, size="0.3in"):
    return (f'<svg class="ico" style="width:{size};height:{size}" viewBox="0 0 24 24" fill="none" stroke="#111" '
            f'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg>')


def arrows_icon():
    return ('<svg class="ico" style="width:0.3in;height:0.3in" viewBox="0 0 24 24" fill="none" stroke="#111" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M2 5h9M8 2l3 3-3 3"/><path d="M5 11v10M2 18l3 3 3-3"/><path d="M11 11l9 9M20 14v6h-6"/></svg>')


def example_grid():
    """Mini sopa de ejemplo con palabras marcadas en cápsula negra y letras blancas."""
    rows = ["MILKQRT", "EAPJXEZ", "GWOTCBO", "GTBPEHS", "SYVLRAN", "KDBUANC", "OLFSWIZ"]
    marks = [(0, 0, 0, 3), (1, 0, 4, 0), (2, 3, 4, 5)]  # MILK →, EGGS ↓, TEA ↘
    cell = 30
    n = len(rows)
    inside = {}
    out = [f'<svg class="example" viewBox="-60 -50 {n*cell+120} {n*cell+70}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect x="-6" y="-6" width="{n*cell+12}" height="{n*cell+12}" rx="8" fill="#fff" stroke="#111" stroke-width="2.5"/>']
    for (r1, c1, r2, c2) in marks:
        dr, dc = (r2 > r1) - (r2 < r1), (c2 > c1) - (c2 < c1)
        k = max(abs(r2 - r1), abs(c2 - c1))
        for t in range(k + 1):
            inside[(r1 + dr * t, c1 + dc * t)] = True
        x1, y1, x2, y2 = c1 * cell + cell / 2, r1 * cell + cell / 2, c2 * cell + cell / 2, r2 * cell + cell / 2
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#111" stroke-width="25" stroke-linecap="round"/>')
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            fill = "#fff" if (r, c) in inside else "#111"
            out.append(f'<text x="{c*cell+cell/2}" y="{r*cell+cell/2+7}" text-anchor="middle" font-size="19" '
                       f'font-weight="700" font-family="Liberation Sans, Arial" fill="{fill}">{ch}</text>')
    a = 'stroke="#111" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    out.append(f'<path d="M0,-28 H{4*cell-6} M{4*cell-16},-38 l10,10 -10,10" {a}/>')            # →
    out.append(f'<path d="M-28,{cell} V{5*cell-6} M-38,{5*cell-16} l10,10 10,-10" {a}/>')         # ↓
    out.append(f'<path d="M{n*cell+14},{3*cell} l40,40 M{n*cell+54},{3*cell+22} v18 h-18" {a}/>')  # ↘
    out.append('</svg>')
    return "".join(out)


def instructions_icons(forward, sol_page):
    rows = [
        (icon("list"), "Read the word list under the grid."),
        (icon("lens"), "Hunt for one word at a time."),
        (arrows_icon(), "Words go across, down or diagonally. <b>Never backwards.</b>" if forward
         else "Words go in any direction, even backwards."),
        (icon("pencil"), "Circle each word and cross it off the list."),
        (icon("cart"), "Take your time and enjoy every aisle!"),
    ]
    items = "".join(f'<div class="step">{ic}<span>{tx}</span></div>' for ic, tx in rows)
    return (f'<div class="howbox">How to Play</div>{items}'
            f'<div class="exwrap">{example_grid()}</div>'
            f'<div class="solnote">{icon("check", "0.42in")}<span><b>Stuck? Solutions start on page {sol_page}.</b></span></div>')


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
.words {{ display: flex; justify-content: space-between; gap: 0.1in; width: {live:.2f}in; margin-top: 0.16in; }}
.words ul {{ list-style: none; margin: 0; padding: 0; }}
.words li {{ font-size: {WORD_PT}pt; font-weight: 700; line-height: 1.45; text-transform: uppercase; white-space: nowrap; }}
.title-page {{ justify-content: center; text-align: center; }}
.num-title {{ text-transform: uppercase; letter-spacing: 1px; margin: 0; }}
.phrase {{ font-size: {max(12, 17 * k):.0f}pt; font-style: normal; color: #333; margin: 0.02in 0 0.1in; }}
.cover1 {{ width: 100%; max-height: 100%; }}
.title-page .big {{ font-size: {64 * k:.0f}pt; font-weight: 900; line-height: 1; }}
.title-page .sub {{ font-size: {30 * k:.0f}pt; margin-top: 0.15in; font-weight: 700; }}
.title-page .vol {{ font-size: {20 * k:.0f}pt; margin-top: 0.15in; letter-spacing: 3px; }}
.title-page .note {{ font-size: {16 * k:.0f}pt; margin-top: 0.4in; color: #555; max-width: {live - 0.4:.2f}in; }}
.instr {{ text-align: left; width: 100%; font-size: 14pt; line-height: 1.45; }}
.instr h1 {{ text-align: left; margin-bottom: 0.2in; }}
.belongs {{ width: 100%; font-size: {max(12, 17 * k):.0f}pt; font-weight: 700; display: flex; align-items: flex-end;
           gap: 0.1in; margin: 0.05in 0 0.28in; }}
.belongs span {{ flex: 1; border-bottom: 1.5px solid #111; height: 1.2em; }}
.howbox {{ border: 2px solid #111; border-radius: 12px; padding: 0.03in 0.3in; font-size: 20pt; font-weight: 700; margin: 0 0 0.16in; }}
.step {{ width: 100%; display: flex; align-items: center; gap: 0.14in; font-size: 14pt; line-height: 1.25; margin: 0.07in 0; }}
.step .ico {{ flex: none; }}
.exwrap {{ width: 100%; display: flex; justify-content: center; margin: 0.12in 0 0.06in; }}
.example {{ width: 2.75in; }}
.solnote {{ width: 100%; display: flex; align-items: center; gap: 0.14in; font-size: 14pt; margin-top: 0.06in; }}
.copyright {{ width: 100%; font-size: 9pt; color: #444; text-align: center; line-height: 1.35; margin-bottom: 0.05in; }}
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

    if book.get("cover"):
        # página 1 = la portada sobre papel blanco
        import portada
        page(portada.front_svg_white(book), "title-page")
    else:
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
    if book.get("author"):
        note += (f'<div class="copyright">Copyright &copy; {book.get("year", "")} {html.escape(book["author"])}. '
                 'All rights reserved. No part of this book may be reproduced in any form without written '
                 'permission from the authors.</div>')
    belongs = ('<div class="belongs">This book belongs to<span></span></div>'
               if book.get("belongs_to", True) else "")
    if book.get("instructions_style") == "icons":
        page(belongs + instructions_icons(forward, 3 + len(puzzles)) + note)
    else:
        page(belongs + '<div class="instr"><h1>How to Play</h1>'
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
        fonts = ""
        if book.get("cover"):
            import portada
            fonts = portada.font_css()
        f.write(f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(book.get("title", ""))} - '
                f'{html.escape(book.get("subtitle", ""))} (interior)</title><style>{fonts}{css(w, h)}</style></head>'
                f'<body>{"".join(pages)}</body></html>')
    print(f"{len(pages)} páginas {w}x{h} -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

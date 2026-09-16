#!/usr/bin/env python3
"""Cinco portadas clásicas para el libro híbrido (frente 8.5x11 con sangrado).

Cada una imita un código visual tradicional del rubro, dibujado desde cero:
  6  magazine  – cabecera roja de revista de pasatiempos, blanco y negro, muy directa
  7  library   – azul marino y dorado, marco fino, aire de libro de biblioteca
  8  newsprint – crema tipo papel de diario, cuadrícula de crucigrama y acento rojo
  9  header    – barra de color arriba, tipografía sans y piezas ordenadas (Brain Games)
  10 quilt     – orla tipo colcha, simétrica y cálida, muy tradicional para mayores

Uso: portadas_clasicas.py libro.json carpeta_salida
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from portada_cozy import BLEED, U, esc, font_css  # noqa: E402
from portadas_opciones import maze_mini, mini_grid, sudoku_mini  # noqa: E402

SANS = "Liberation Sans, Arial, sans-serif"
SERIF = "Playfair Display, serif"


def stars(cx, y, n, size, color):
    out = []
    for k in range(n):
        x = cx - (n - 1) * size * 1.6 / 2 + k * size * 1.6
        out.append(f'<path transform="translate({x},{y}) scale({size/18:.2f})" fill="{color}" '
                   'd="M0,-18 L5,-6 18,-6 8,2 12,15 0,7 -12,15 -8,2 -18,-6 -5,-6 z"/>')
    return "".join(out)


# ------------------------------------------------------------------ 6. revista de pasatiempos
def front_magazine(x0, y0, w, h, cv, c):
    cx = x0 + w / 2
    ink, red = "#111111", "#C62828"
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#FFFFFF"/>',
           f'<rect x="{x0}" y="{y0}" width="{w}" height="230" fill="{red}"/>',
           f'<text x="{cx}" y="{y0+120}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="92" '
           f'textLength="{w-140}" lengthAdjust="spacingAndGlyphs" fill="#FFFFFF">WORD SEARCH</text>',
           f'<text x="{cx}" y="{y0+186}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="46" '
           f'letter-spacing="3" fill="#FFFFFF">SUDOKU · MAZES</text>',
           f'<rect x="{x0}" y="{y0+230}" width="{w}" height="14" fill="{ink}"/>']
    out.append(f'<text x="{cx}" y="{y0+330}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="112" fill="{ink}">70 PUZZLES</text>')
    out.append(f'<text x="{cx}" y="{y0+396}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="52" fill="{red}">LARGE PRINT</text>')
    cw = dict(c, ink=ink, highlight="#E0E0E0")
    out.append(mini_grid(x0 + 84, y0 + 470, 6, 4, cv["cup"], cw, cell=46, font=33, family=SANS))
    out.append(maze_mini(x0 + 100, y0 + 716, cw, cell=28, n=7))
    out.append(sudoku_mini(x0 + w - 390, y0 + 529, cw, cell=36))
    out.append(f'<rect x="{x0+60}" y="{y0+h-190}" width="{w-120}" height="64" rx="8" fill="{ink}"/>')
    out.append(f'<text x="{cx}" y="{y0+h-146}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="34" '
               f'fill="#FFFFFF">40 WORD SEARCH · 20 SUDOKU · 10 MAZES</text>')
    out.append(f'<text x="{cx}" y="{y0+h-86}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="36" fill="{ink}">FOR ADULTS &amp; SENIORS</text>')
    out.append(f'<text x="{cx}" y="{y0+h-46}" text-anchor="middle" font-family="{SANS}" font-size="26" fill="{ink}">{esc(cv["author"])} · Solutions Included</text>')
    return "".join(out)


# ------------------------------------------------------------------ 7. biblioteca
def front_library(x0, y0, w, h, cv, c):
    cx = x0 + w / 2
    navy, gold, cream = "#14213D", "#C9A227", "#F6F1E4"
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{navy}"/>',
           f'<rect x="{x0+44}" y="{y0+44}" width="{w-88}" height="{h-88}" rx="6" fill="none" stroke="{gold}" stroke-width="6"/>',
           f'<rect x="{x0+62}" y="{y0+62}" width="{w-124}" height="{h-124}" rx="4" fill="none" stroke="{gold}" stroke-width="2"/>',
           stars(cx, y0 + 160, 3, 20, gold),
           f'<text x="{cx}" y="{y0+300}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="104" '
           f'textLength="{w-230}" lengthAdjust="spacingAndGlyphs" fill="{cream}">PUZZLES</text>',
           f'<text x="{cx}" y="{y0+360}" text-anchor="middle" font-family="{SERIF}" font-size="34" letter-spacing="6" fill="{gold}">WORD SEARCH · SUDOKU · MAZES</text>',
           f'<line x1="{cx-230}" y1="{y0+392}" x2="{cx+230}" y2="{y0+392}" stroke="{gold}" stroke-width="3"/>']
    cw = dict(c, ink=navy, highlight="#E7DCC0")
    out.append(f'<rect x="{cx-320}" y="{y0+430}" width="640" height="330" rx="10" fill="{cream}"/>')
    out.append(mini_grid(cx - 268, y0 + 470, 6, 4, cv["cup"], cw, cell=44, font=31))
    out.append(sudoku_mini(cx + 40, y0 + 456, cw, cell=31))
    out.append(f'<text x="{cx}" y="{y0+828}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="74" fill="{gold}">70</text>')
    out.append(f'<text x="{cx}" y="{y0+872}" text-anchor="middle" font-family="{SERIF}" font-size="30" letter-spacing="4" fill="{cream}">PUZZLES IN LARGE PRINT</text>')
    out.append(stars(cx, y0 + 910, 3, 16, gold))
    out.append(f'<text x="{cx}" y="{y0+h-70}" text-anchor="middle" font-family="{SERIF}" font-size="30" letter-spacing="5" fill="{cream}">{esc(cv["author"].upper())}</text>')
    return "".join(out)


# ------------------------------------------------------------------ 8. papel de diario
def front_newsprint(x0, y0, w, h, cv, c):
    cx = x0 + w / 2
    ink, red, paper = "#1A1A1A", "#B3261E", "#F2EDE1"
    rng = random.Random(12)
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{paper}"/>']
    # cuadrícula de crucigrama de fondo
    cell = 58
    for r in range(int(h // cell) + 1):
        for k in range(int(w // cell) + 1):
            if rng.random() < 0.22:
                out.append(f'<rect x="{x0+k*cell}" y="{y0+r*cell}" width="{cell}" height="{cell}" fill="{ink}" opacity=".07"/>')
    for i in range(int(w // cell) + 1):
        out.append(f'<line x1="{x0+i*cell}" y1="{y0}" x2="{x0+i*cell}" y2="{y0+h}" stroke="{ink}" stroke-width="1.5" opacity=".12"/>')
    for i in range(int(h // cell) + 1):
        out.append(f'<line x1="{x0}" y1="{y0+i*cell}" x2="{x0+w}" y2="{y0+i*cell}" stroke="{ink}" stroke-width="1.5" opacity=".12"/>')
    out.append(f'<rect x="{x0+56}" y="{y0+96}" width="{w-112}" height="330" fill="{paper}" stroke="{ink}" stroke-width="5"/>')
    out.append(f'<text x="{cx}" y="{y0+180}" text-anchor="middle" font-family="{SERIF}" font-size="30" letter-spacing="8" fill="{red}">THE DAILY</text>')
    out.append(f'<text x="{cx}" y="{y0+290}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="106" '
               f'textLength="{w-210}" lengthAdjust="spacingAndGlyphs" fill="{ink}">PUZZLE BOOK</text>')
    out.append(f'<line x1="{x0+90}" y1="{y0+320}" x2="{x0+w-90}" y2="{y0+320}" stroke="{ink}" stroke-width="3"/>')
    out.append(f'<text x="{cx}" y="{y0+386}" text-anchor="middle" font-family="{SERIF}" font-size="38" letter-spacing="3" fill="{ink}">WORD SEARCH · SUDOKU · MAZES</text>')
    cw = dict(c, ink=ink, highlight="#E2D7BE")
    out.append(mini_grid(x0 + 86, y0 + 500, 6, 4, cv["cup"], cw, cell=46, font=32))
    out.append(maze_mini(x0 + 100, y0 + 740, cw, cell=28, n=7))
    out.append(sudoku_mini(x0 + w - 386, y0 + 565, cw, cell=34))
    out.append(f'<rect x="{x0+56}" y="{y0+h-172}" width="{w-112}" height="118" fill="{red}"/>')
    out.append(f'<text x="{cx}" y="{y0+h-118}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="44" fill="#FFFFFF">70 PUZZLES · LARGE PRINT</text>')
    out.append(f'<text x="{cx}" y="{y0+h-76}" text-anchor="middle" font-family="{SERIF}" font-size="26" fill="#FFFFFF">For Adults &amp; Seniors · Solutions Included</text>')
    return "".join(out)


# ------------------------------------------------------------------ 9. barra de color
def front_header(x0, y0, w, h, cv, c):
    cx = x0 + w / 2
    ink, teal, cream = "#1F2933", "#1E7A6F", "#FFFFFF"
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{cream}"/>',
           f'<rect x="{x0}" y="{y0}" width="{w}" height="300" fill="{teal}"/>',
           f'<text x="{cx}" y="{y0+150}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="80" '
           f'textLength="{w-200}" lengthAdjust="spacingAndGlyphs" fill="#FFFFFF">PUZZLE TIME</text>',
           f'<text x="{cx}" y="{y0+220}" text-anchor="middle" font-family="{SANS}" font-size="40" letter-spacing="4" fill="#FFFFFF">WORD SEARCH · SUDOKU · MAZES</text>',
           f'<rect x="{x0}" y="{y0+300}" width="{w}" height="10" fill="{ink}"/>']
    cw = dict(c, ink=ink, highlight="#CFE3DF")
    out.append(f'<text x="{cx}" y="{y0+390}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="54" fill="{ink}">70 PUZZLES IN LARGE PRINT</text>')
    out.append(mini_grid(x0 + 90, y0 + 440, 6, 4, cv["cup"], cw, cell=46, font=32, family=SANS))
    out.append(maze_mini(x0 + 104, y0 + 690, cw, cell=28, n=7))
    out.append(sudoku_mini(x0 + w - 380, y0 + 470, cw, cell=34))
    out.append(f'<circle cx="{x0+w-160}" cy="{y0+878}" r="76" fill="{teal}"/>')
    out.append(f'<text x="{x0+w-160}" y="{y0+872}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="42" fill="#FFFFFF">EASY</text>')
    out.append(f'<text x="{x0+w-160}" y="{y0+908}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="24" fill="#FFFFFF">LEVEL</text>')
    out.append(f'<rect x="{x0}" y="{y0+h-150}" width="{w}" height="150" fill="{ink}"/>')
    out.append(f'<text x="{cx}" y="{y0+h-90}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="40" fill="#FFFFFF">FOR ADULTS &amp; SENIORS</text>')
    out.append(f'<text x="{cx}" y="{y0+h-46}" text-anchor="middle" font-family="{SANS}" font-size="26" fill="#FFFFFF">{esc(cv["author"])} · Solutions Included</text>')
    return "".join(out)


# ------------------------------------------------------------------ 10. orla tipo colcha
def front_quilt(x0, y0, w, h, cv, c):
    cx = x0 + w / 2
    ink, cream, rose, sage = "#2B2B2B", "#FBF4E6", "#B4614F", "#7F9A78"
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{cream}"/>']
    # orla de rombos
    step = 72
    nx = max(2, int((w - 120) // step))
    sx = (w - 120) / nx
    for k in range(nx + 1):  # filas superior e inferior, incluidas las esquinas
        x = x0 + 60 + k * sx
        for (yy, col) in ((y0 + 60, rose), (y0 + h - 60, sage)):
            out.append(f'<path d="M{x:.1f},{yy-26} l26,26 -26,26 -26,-26 z" fill="{col}" opacity=".9"/>')
    ny = max(2, int((h - 120) // step))
    sy = (h - 120) / ny
    for k in range(1, ny):  # columnas laterales, sin repetir las esquinas
        y = y0 + 60 + k * sy
        for (xx, col) in ((x0 + 60, sage), (x0 + w - 60, rose)):
            out.append(f'<path d="M{xx},{y-26:.1f} l26,26 -26,26 -26,-26 z" fill="{col}" opacity=".9"/>')
    out.append(f'<rect x="{x0+110}" y="{y0+110}" width="{w-220}" height="{h-220}" rx="10" fill="#FFFFFF" stroke="{ink}" stroke-width="5"/>')
    out.append(f'<text x="{cx}" y="{y0+236}" text-anchor="middle" font-family="{SERIF}" font-size="30" letter-spacing="6" fill="{rose}">{esc(cv["author"].upper())}</text>')
    out.append(f'<text x="{cx}" y="{y0+348}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="92" '
               f'textLength="{w-330}" lengthAdjust="spacingAndGlyphs" fill="{ink}">PUZZLES</text>')
    out.append(f'<text x="{cx}" y="{y0+404}" text-anchor="middle" font-family="{SERIF}" font-size="32" letter-spacing="3" fill="{ink}">WORD SEARCH · SUDOKU · MAZES</text>')
    out.append(f'<line x1="{cx-200}" y1="{y0+436}" x2="{cx+200}" y2="{y0+436}" stroke="{rose}" stroke-width="4"/>')
    cw = dict(c, ink=ink, highlight="#EADFC6")
    out.append(mini_grid(cx - 138, y0 + 480, 6, 4, cv["cup"], cw, cell=46, font=32))
    out.append(f'<text x="{cx}" y="{y0+790}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="86" fill="{rose}">70 PUZZLES</text>')
    out.append(f'<text x="{cx}" y="{y0+848}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="44" letter-spacing="4" fill="{ink}">LARGE PRINT</text>')
    out.append(f'<text x="{cx}" y="{y0+898}" text-anchor="middle" font-family="{SERIF}" font-size="26" fill="{ink}">{esc(cv["band_line"])}</text>')
    return "".join(out)


STYLES = {"6-magazine": front_magazine, "7-library": front_library, "8-newsprint": front_newsprint,
          "9-header": front_header, "10-quilt": front_quilt}


def main(src, outdir):
    book = json.load(open(src, encoding="utf-8"))
    cv, c = book["cover"], book["cover"]["colors"]
    tw, th = book["trim"]
    W, H = (tw + 2 * BLEED) * U, (th + 2 * BLEED) * U
    os.makedirs(outdir, exist_ok=True)
    for name, fn in STYLES.items():
        svg = fn(0, 0, W, H, cv, c)
        doc = (f'<!doctype html><html><head><meta charset="utf-8"><title>{esc(cv["title"])} {name}</title><style>'
               f'{font_css()}@page {{ size: {W/U:.4f}in {H/U:.4f}in; margin: 0; }}'
               f'html,body {{ margin:0; padding:0; }} svg {{ display:block; width:{W/U:.4f}in; height:{H/U:.4f}in; }}'
               f'</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}">{svg}</svg></body></html>')
        path = os.path.join(outdir, f"opcion_{name}.html")
        open(path, "w", encoding="utf-8").write(doc)
        print(path)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

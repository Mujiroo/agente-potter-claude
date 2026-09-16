#!/usr/bin/env python3
"""Cinco portadas distintas para el libro híbrido (frente 8.5x11 con sangrado).

Cada estilo imita un patrón que hoy funciona en Amazon, con dibujo propio:
  1 cozy      – crema, taza con sopa de letras, ramitas (TG Edition / Cozy Autumn)
  2 bignumber – números gigantes y colores fuertes (Big Book of Word Search)
  3 window    – ventana con lluvia, té y plantas; marco ilustrado (Cozy / Brain Games Calm)
  4 clean     – crema casi blanco, orla botánica fina y tipografía sobria (Brain Games Relax & Solve)
  5 modern    – geométrico de alto contraste, mostaza y tinta (propuesta propia)

Uso: portadas_opciones.py libro.json carpeta_salida
"""
import html
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from portada_cozy import BLEED, U, badge, book_and_blanket, esc, front as cozy_front, leaves, letter_texture, mug  # noqa: E402


def frame(x0, y0, w, h, color, inset=38, width=5, op=".55"):
    return (f'<rect x="{x0+inset}" y="{y0+inset}" width="{w-2*inset}" height="{h-2*inset}" rx="18" '
            f'fill="none" stroke="{color}" stroke-width="{width}" opacity="{op}"/>')


def mini_grid(x, y, cols, rows, words, c, cell=42, font=30, family="Playfair Display, serif"):
    """Grilla de letras suelta, con algunas palabras marcadas."""
    out = [f'<rect x="{x-14}" y="{y-14}" width="{cols*cell+28}" height="{rows*cell+28}" rx="12" fill="#fff" '
           f'stroke="{c["ink"]}" stroke-width="7"/>']
    for (r1, c1, r2, c2) in words["found"]:
        out.append(f'<line x1="{x+c1*cell+cell/2}" y1="{y+r1*cell+cell/2}" x2="{x+c2*cell+cell/2}" '
                   f'y2="{y+r2*cell+cell/2}" stroke="{c["highlight"]}" stroke-width="32" stroke-linecap="round"/>')
    for r, row in enumerate(words["grid"]):
        for k, ch in enumerate(row):
            out.append(f'<text x="{x+k*cell+cell/2}" y="{y+r*cell+cell/2+font*0.35:.0f}" text-anchor="middle" '
                       f'font-family="{family}" font-weight="700" font-size="{font}" fill="{c["ink"]}">{ch}</text>')
    return "".join(out)


def sudoku_mini(x, y, c, cell=34, n=9):
    rng = random.Random(4)
    out = [f'<rect x="{x}" y="{y}" width="{n*cell}" height="{n*cell}" fill="#fff" stroke="{c["ink"]}" stroke-width="7"/>']
    for i in range(1, n):
        wd = 6 if i % 3 == 0 else 2
        out.append(f'<line x1="{x+i*cell}" y1="{y}" x2="{x+i*cell}" y2="{y+n*cell}" stroke="{c["ink"]}" stroke-width="{wd}"/>')
        out.append(f'<line x1="{x}" y1="{y+i*cell}" x2="{x+n*cell}" y2="{y+i*cell}" stroke="{c["ink"]}" stroke-width="{wd}"/>')
    for r in range(n):
        for k in range(n):
            if rng.random() < 0.42:
                out.append(f'<text x="{x+k*cell+cell/2}" y="{y+r*cell+cell/2+9}" text-anchor="middle" '
                           f'font-family="Playfair Display, serif" font-weight="700" font-size="24" '
                           f'fill="{c["ink"]}">{rng.randint(1,9)}</text>')
    return "".join(out)


def maze_mini(x, y, c, cell=30, n=7, seed=9):
    """Laberinto chico y decorativo (no hay que resolverlo)."""
    rng = random.Random(seed)
    out = [f'<rect x="{x}" y="{y}" width="{n*cell}" height="{n*cell}" fill="#fff" stroke="{c["ink"]}" stroke-width="7"/>']
    for r in range(n):
        for k in range(n):
            if rng.random() < 0.5:
                out.append(f'<line x1="{x+k*cell}" y1="{y+r*cell}" x2="{x+(k+1)*cell}" y2="{y+r*cell}" '
                           f'stroke="{c["ink"]}" stroke-width="6" stroke-linecap="round"/>')
            if rng.random() < 0.5:
                out.append(f'<line x1="{x+k*cell}" y1="{y+r*cell}" x2="{x+k*cell}" y2="{y+(r+1)*cell}" '
                           f'stroke="{c["ink"]}" stroke-width="6" stroke-linecap="round"/>')
    return "".join(out)


# ------------------------------------------------------------------ 2. números grandes
def front_bignumber(x0, y0, w, h, cv, c):
    cx = x0 + w / 2
    ink, blue, sun = "#10243F", "#1B6CA8", "#F6B93B"
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{blue}"/>',
           letter_texture(x0, y0, w, h, "#FFFFFF", 0.12, cell=52, size=30),
           f'<rect x="{x0+30}" y="{y0+30}" width="{w-60}" height="{h-60}" rx="14" fill="none" stroke="#fff" stroke-width="6" opacity=".8"/>']
    out.append(f'<text x="{cx}" y="{y0+150}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="60" textLength="{w-200}" lengthAdjust="spacingAndGlyphs" fill="#fff">PUZZLE BOOK</text>')
    out.append(f'<text x="{cx}" y="{y0+300}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="190" fill="{sun}">70</text>')
    out.append(f'<text x="{cx}" y="{y0+364}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="52" letter-spacing="4" fill="#fff">PUZZLES IN LARGE PRINT</text>')
    out.append(f'<rect x="{x0+70}" y="{y0+404}" width="{w-140}" height="74" rx="14" fill="{sun}"/>')
    out.append(f'<text x="{cx}" y="{y0+456}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="38" textLength="{w-190}" lengthAdjust="spacingAndGlyphs" fill="{ink}">40 WORD SEARCH · 20 SUDOKU · 10 MAZES</text>')
    cw = dict(c, ink=ink)
    out.append(mini_grid(x0 + 86, y0 + 548, 6, 4, cv["cup"], cw, cell=44, font=31))
    out.append(sudoku_mini(x0 + w - 386, y0 + 534, cw, cell=34))
    out.append(maze_mini(x0 + 110, y0 + 800, cw, cell=32, n=7))
    out.append(f'<g transform="rotate(4 {x0+w-260} {y0+880})">{maze_mini(x0 + w - 360, y0 + 810, cw, cell=30, n=6)}</g>')
    out.append(f'<rect x="{x0+30}" y="{y0+h-146}" width="{w-60}" height="108" rx="14" fill="#fff"/>')
    out.append(f'<text x="{cx}" y="{y0+h-96}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="42" fill="{ink}">FOR ADULTS &amp; SENIORS</text>')
    out.append(f'<text x="{cx}" y="{y0+h-58}" text-anchor="middle" font-family="Playfair Display, serif" font-size="26" '
               f'fill="{ink}">{esc(cv["author"])} · Solutions Included</text>')
    return "".join(out)


# ------------------------------------------------------------------ 3. ventana con lluvia
def front_window(x0, y0, w, h, cv, c):
    cx = x0 + w / 2
    ink = c["ink"]
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#EFE7DA"/>',
           letter_texture(x0, y0, w, h, ink, 0.07, cell=48)]
    # ventana
    wx, wy, ww, wh = cx - 300, y0 + 330, 600, 470
    out.append(f'<rect x="{wx-22}" y="{wy-22}" width="{ww+44}" height="{wh+44}" rx="26" fill="#C98A5B" stroke="{ink}" stroke-width="9"/>')
    out.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="#BBD5DD" stroke="{ink}" stroke-width="7"/>')
    out.append(f'<line x1="{cx}" y1="{wy}" x2="{cx}" y2="{wy+wh}" stroke="{ink}" stroke-width="9"/>')
    out.append(f'<line x1="{wx}" y1="{wy+wh/2}" x2="{wx+ww}" y2="{wy+wh/2}" stroke="{ink}" stroke-width="9"/>')
    rng = random.Random(6)
    for _ in range(60):  # gotas de lluvia
        rx, ry = wx + rng.uniform(14, ww - 14), wy + rng.uniform(14, wh - 14)
        out.append(f'<line x1="{rx:.0f}" y1="{ry:.0f}" x2="{rx-8:.0f}" y2="{ry+26:.0f}" stroke="#7FA6B5" stroke-width="5" stroke-linecap="round"/>')
    # colinas al fondo
    out.append(f'<path d="M{wx+6},{wy+wh-60} q90,-90 190,-10 q80,-70 170,0 q70,-50 130,10 l0,50 l-490,0 z" fill="#9BBFA0" opacity=".9"/>')
    # alféizar con taza y planta
    out.append(f'<rect x="{wx-54}" y="{wy+wh+22}" width="{ww+108}" height="30" rx="12" fill="#C98A5B" stroke="{ink}" stroke-width="8"/>')
    out.append(mug(cx - 150, wy + wh - 40, c, cv["cup"], 0.52))
    out.append(leaves(cx + 210, wy + wh + 20, c, 1.1, 8))
    # títulos
    out.append(f'<text x="{cx}" y="{y0+150}" text-anchor="middle" font-family="Caveat, cursive" font-size="104" fill="{c["terracotta"]}">{esc(cv["script"])}</text>')
    out.append(f'<text x="{cx}" y="{y0+238}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="72" textLength="{w-200}" lengthAdjust="spacingAndGlyphs" fill="{ink}">{esc(cv["title"])}</text>')
    out.append(f'<text x="{cx}" y="{y0+284}" text-anchor="middle" font-family="Playfair Display, serif" font-size="26" '
               f'letter-spacing="4" fill="{ink}">{esc(cv["subtitle"].upper())}</text>')
    out.append(badge(x0 + 146, y0 + h - 236, 74, cv["badge1"], cv["badge2"], c))
    out.append(f'<rect x="{x0+50}" y="{y0+h-140}" width="{w-100}" height="102" rx="16" fill="{c["sage"]}" stroke="{ink}" stroke-width="6"/>')
    out.append(f'<text x="{cx}" y="{y0+h-92}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="38" letter-spacing="3" fill="{ink}">LARGE PRINT</text>')
    out.append(f'<text x="{cx}" y="{y0+h-58}" text-anchor="middle" font-family="Playfair Display, serif" font-size="22" fill="{ink}">{esc(cv["band_line"])}</text>')
    return "".join(out)


# ------------------------------------------------------------------ 4. sobrio con orla
def front_clean(x0, y0, w, h, cv, c):
    cx = x0 + w / 2
    ink = "#243425"
    cream = "#FBF7EF"
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{cream}"/>',
           frame(x0, y0, w, h, ink, inset=46, width=4, op=".8"),
           frame(x0, y0, w, h, ink, inset=62, width=2, op=".5")]
    cw = dict(c, ink=ink, sage="#C7D6BD", sage2="#DCE7D3")
    for k in range(6):  # orla botánica arriba y abajo
        out.append(leaves(x0 + 150 + k * (w - 300) / 5, y0 + 250, cw, 0.5, -20 + k * 8))
        out.append(leaves(x0 + 150 + k * (w - 300) / 5, y0 + h - 78, cw, 0.5, 200 - k * 8))
    out.append(f'<text x="{cx}" y="{y0+150}" text-anchor="middle" font-family="Playfair Display, serif" font-size="30" '
               f'letter-spacing="8" fill="{ink}">{esc(cv["author"].upper())}</text>')
    out.append(f'<text x="{cx}" y="{y0+400}" text-anchor="middle" font-family="Caveat, cursive" font-size="126" fill="{ink}">{esc(cv["script"])}</text>')
    out.append(f'<text x="{cx}" y="{y0+486}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="82" letter-spacing="6" fill="{ink}">{esc(cv["title"])}</text>')
    out.append(f'<line x1="{cx-210}" y1="{y0+520}" x2="{cx+210}" y2="{y0+520}" stroke="{ink}" stroke-width="3"/>')
    out.append(f'<text x="{cx}" y="{y0+566}" text-anchor="middle" font-family="Playfair Display, serif" font-size="30" '
               f'letter-spacing="3" fill="{ink}">{esc(cv["subtitle"].upper())}</text>')
    out.append(mini_grid(cx - 138, y0 + 620, 6, 4, cv["cup"], cw, cell=46, font=32))
    out.append(f'<text x="{cx}" y="{y0+h-206}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="46" letter-spacing="4" fill="{ink}">LARGE PRINT</text>')
    out.append(f'<text x="{cx}" y="{y0+h-162}" text-anchor="middle" font-family="Playfair Display, serif" font-size="26" fill="{ink}">{esc(cv["band_line"])}</text>')
    return "".join(out)


# ------------------------------------------------------------------ 5. moderno geométrico
MODERN_DEFAULT = {"ink": "#1C2B2D", "accent": "#E5A020", "cream": "#F4EFE6", "main": "#2F6E6B", "highlight": "#F3DCA8"}


def front_modern(x0, y0, w, h, cv, c, pal=None):
    cx = x0 + w / 2
    pal = dict(MODERN_DEFAULT, **(pal or {}))
    ink, mustard, cream, teal = pal["ink"], pal["accent"], pal["cream"], pal["main"]
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{cream}"/>',
           f'<rect x="{x0}" y="{y0}" width="{w}" height="{h*0.44}" fill="{teal}"/>',
           f'<circle cx="{x0+w*0.16}" cy="{y0+h*0.44}" r="120" fill="{mustard}"/>',
           f'<circle cx="{x0+w*0.86}" cy="{y0+h*0.12}" r="86" fill="{mustard}" opacity=".85"/>']
    out.append(letter_texture(x0, y0, w, int(h * 0.44), "#FFFFFF", 0.1, cell=50, size=28))
    out.append(f'<text x="{cx}" y="{y0+130}" text-anchor="middle" font-family="Playfair Display, serif" font-size="26" '
               f'letter-spacing="7" fill="#FFFFFF">{esc(cv["author"].upper())}</text>')
    out.append(f'<text x="{cx}" y="{y0+256}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="96" textLength="{w-190}" lengthAdjust="spacingAndGlyphs" fill="#FFFFFF">{esc(cv["title"])}</text>')
    out.append(f'<text x="{cx}" y="{y0+330}" text-anchor="middle" font-family="Caveat, cursive" font-size="82" fill="{mustard}">{esc(cv["script"])}</text>')
    out.append(f'<text x="{cx}" y="{y0+398}" text-anchor="middle" font-family="Playfair Display, serif" font-size="30" '
               f'letter-spacing="4" fill="#FFFFFF">{esc(cv["subtitle"].upper())}</text>')
    cw = dict(c, ink=ink, highlight=pal["highlight"])
    out.append(f'<g transform="rotate(-6 {cx-150} {y0+600})">{mini_grid(cx - 330, y0 + 510, 6, 4, cv["cup"], cw, cell=46, font=32)}</g>')
    out.append(f'<g transform="rotate(5 {cx+180} {y0+640})">{sudoku_mini(cx + 40, y0 + 546, cw, cell=36)}</g>')
    # laberinto sobre la franja LARGE PRINT: abajo termina a ~y0+h-195, con aire antes de la franja (y0+h-150)
    out.append(f'<g transform="rotate(-3 {cx-150} {y0+h-300})">{maze_mini(cx - 248, y0 + h - 402, cw, cell=28, n=7)}</g>')
    out.append(f'<rect x="{x0+60}" y="{y0+h-150}" width="{w-120}" height="112" rx="56" fill="{ink}"/>')
    out.append(f'<text x="{cx}" y="{y0+h-98}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="42" letter-spacing="3" fill="{mustard}">LARGE PRINT</text>')
    out.append(f'<text x="{cx}" y="{y0+h-60}" text-anchor="middle" font-family="Playfair Display, serif" font-size="24" '
               f'fill="#FFFFFF">{esc(cv["band_line"])}</text>')
    return "".join(out)


STYLES = {"1-cozy": None, "2-bignumber": front_bignumber, "3-window": front_window,
          "4-clean": front_clean, "5-modern": front_modern}


def main(src, outdir):
    from portada_cozy import font_css
    book = json.load(open(src, encoding="utf-8"))
    cv, c = book["cover"], book["cover"]["colors"]
    tw, th = book["trim"]
    W, H = (tw + 2 * BLEED) * U, (th + 2 * BLEED) * U
    os.makedirs(outdir, exist_ok=True)
    for name, fn in STYLES.items():
        svg = cozy_front(0, 0, W, H, cv, c) if fn is None else fn(0, 0, W, H, cv, c)
        doc = (f'<!doctype html><html><head><meta charset="utf-8"><title>{esc(cv["title"])} {name}</title><style>'
               f'{font_css()}@page {{ size: {W/U:.4f}in {H/U:.4f}in; margin: 0; }}'
               f'html,body {{ margin:0; padding:0; }} svg {{ display:block; width:{W/U:.4f}in; height:{H/U:.4f}in; }}'
               f'</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}">{svg}</svg></body></html>')
        path = os.path.join(outdir, f"opcion_{name}.html")
        open(path, "w", encoding="utf-8").write(doc)
        print(path)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

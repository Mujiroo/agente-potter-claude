#!/usr/bin/env python3
"""Portada completa KDP (contratapa + lomo + frente) de Calm & Cozy, estilo moderno.

Paleta elegida por Pedro (16-sep): B · azul marino y coral.
El frente deja claro que son 3 juegos: cinta "3 KINDS OF PUZZLES IN ONE BOOK" y
tres tarjetas rotuladas (Word Search · Easy Sudoku · Mazes) con su cantidad.

Uso: portada_final.py libro.json salida.html [--front-only]
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from portada_cozy import BLEED, PAPER, U, esc, font_css, letter_texture  # noqa: E402

def texture(x0, y0, w, h, seed):
    """letter_texture recortada exactamente a su rectángulo (la original se pasa una fila)."""
    return (f'<svg x="{x0}" y="{y0}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" overflow="hidden">'
            f'{letter_texture(0, 0, w, h, "#FFFFFF", 0.1, cell=50, size=28, seed=seed)}</svg>')


PAL = {"main": "#1F3A5F", "accent": "#F08A5D", "ink": "#16263D", "cream": "#F4EFE6", "highlight": "#F9D3C0"}
SERIF = "Playfair Display, serif"


def card_grid(x, y, words, cell=34, font=25):
    rows = words["grid"]
    cols = len(rows[0])
    out = [f'<rect x="{x-14}" y="{y-14}" width="{cols*cell+28}" height="{len(rows)*cell+28}" rx="12" fill="#fff" '
           f'stroke="{PAL["ink"]}" stroke-width="6"/>']
    for r1, c1, r2, c2 in words["found"]:
        out.append(f'<line x1="{x+c1*cell+cell/2}" y1="{y+r1*cell+cell/2}" x2="{x+c2*cell+cell/2}" y2="{y+r2*cell+cell/2}" '
                   f'stroke="{PAL["highlight"]}" stroke-width="26" stroke-linecap="round"/>')
    for r, row in enumerate(rows):
        for k, ch in enumerate(row):
            out.append(f'<text x="{x+k*cell+cell/2}" y="{y+r*cell+cell/2+font*0.35:.1f}" text-anchor="middle" '
                       f'font-family="{SERIF}" font-weight="700" font-size="{font}" fill="{PAL["ink"]}">{ch}</text>')
    return "".join(out)


def card_sudoku(x, y, cell=25):
    rng = random.Random(4)
    ink = PAL["ink"]
    n = 9
    out = [f'<rect x="{x}" y="{y}" width="{n*cell}" height="{n*cell}" fill="#fff" stroke="{ink}" stroke-width="6"/>']
    for i in range(1, n):
        wd = 4.5 if i % 3 == 0 else 1.5
        out.append(f'<line x1="{x+i*cell}" y1="{y}" x2="{x+i*cell}" y2="{y+n*cell}" stroke="{ink}" stroke-width="{wd}"/>')
        out.append(f'<line x1="{x}" y1="{y+i*cell}" x2="{x+n*cell}" y2="{y+i*cell}" stroke="{ink}" stroke-width="{wd}"/>')
    import puzzles as PZ
    pz, _sol, _g = PZ.make_easy_sudoku(rng)  # un sudoku real: sin números repetidos en fila, columna ni caja
    for r in range(n):
        for k in range(n):
            if pz[r][k]:
                out.append(f'<text x="{x+k*cell+cell/2}" y="{y+r*cell+cell/2+6}" text-anchor="middle" '
                           f'font-family="{SERIF}" font-weight="700" font-size="17" fill="{ink}">{pz[r][k]}</text>')
    return "".join(out)


def card_maze(x, y, cell=32, n=7, seed=9):
    import puzzles as PZ
    mz = PZ.make_maze(random.Random(seed), n, n)
    ink = PAL["ink"]
    out = [f'<rect x="{x-10}" y="{y-10}" width="{n*cell+20}" height="{n*cell+20}" rx="10" fill="#fff"/>']
    pts = " ".join(f"{x+c*cell+cell/2},{y+r*cell+cell/2}" for r, c in mz["path"])
    out.append(f'<polyline points="{pts}" fill="none" stroke="{PAL["highlight"]}" stroke-width="14" '
               'stroke-linecap="round" stroke-linejoin="round"/>')
    seg = []
    for r in range(n):
        for c in range(n):
            wl = mz["walls"][r][c]
            X, Y = x + c * cell, y + r * cell
            if wl["N"] and not (r == 0 and c == 0):
                seg.append(f"M{X},{Y} h{cell}")
            if wl["W"] and not (r == 0 and c == 0):
                seg.append(f"M{X},{Y} v{cell}")
            if r == n - 1 and wl["S"] and not (c == n - 1):
                seg.append(f"M{X},{Y+cell} h{cell}")
            if c == n - 1 and wl["E"] and not (r == n - 1):
                seg.append(f"M{X+cell},{Y} v{cell}")
    out.append(f'<path d="{" ".join(seg)}" stroke="{ink}" stroke-width="6" stroke-linecap="round" fill="none"/>')
    return "".join(out)


def front(x0, y0, w, h, cv):
    """Frente con sangrado en los 4 lados; (x0, y0, w, h) incluye el sangrado."""
    cx = x0 + w / 2
    m, a, ink, cream = PAL["main"], PAL["accent"], PAL["ink"], PAL["cream"]
    top = 470
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{cream}"/>',
           f'<rect x="{x0}" y="{y0}" width="{w}" height="{top}" fill="{m}"/>',
           f'<circle cx="{x0+w*0.86}" cy="{y0+h*0.11}" r="80" fill="{a}" opacity=".85"/>',
           texture(x0, y0, w, top, 3),
           f'<text x="{cx}" y="{y0+118}" text-anchor="middle" font-family="{SERIF}" font-size="26" letter-spacing="7" '
           f'fill="#FFFFFF">{esc(cv["author"].upper())}</text>',
           f'<text x="{cx}" y="{y0+240}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="96" '
           f'textLength="{w-190}" lengthAdjust="spacingAndGlyphs" fill="#FFFFFF">{esc(cv["title"])}</text>',
           f'<text x="{cx}" y="{y0+318}" text-anchor="middle" font-family="Caveat, cursive" font-size="84" fill="{a}">'
           f'{esc(cv["script"])}</text>',
           # cinta: 3 juegos en un libro
           f'<rect x="{cx-330}" y="{y0+366}" width="660" height="64" rx="32" fill="{a}"/>',
           f'<text x="{cx}" y="{y0+409}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="29" '
           f'letter-spacing="2" fill="{ink}">3 KINDS OF PUZZLES IN ONE BOOK</text>']

    # tres tarjetas rotuladas
    centers = [cx - 266, cx, cx + 266]
    mid = y0 + 668
    grid_w, grid_h = 6 * 34, 4 * 34
    items = [
        (card_grid(centers[0] - grid_w / 2, mid - grid_h / 2, cv["cup"]), -4, "WORD SEARCH", f'{cv["counts"][0]} puzzles'),
        (card_sudoku(centers[1] - 112.5, mid - 112.5), 3, "EASY SUDOKU", f'{cv["counts"][1]} puzzles'),
        (card_maze(centers[2] - 112, mid - 112), -3, "MAZES", f'{cv["counts"][2]} puzzles'),
    ]
    for (svg, rot, label, count), x in zip(items, centers):
        out.append(f'<g transform="rotate({rot} {x} {mid})">{svg}</g>')
        out.append(f'<text x="{x}" y="{y0+842}" text-anchor="middle" font-family="{SERIF}" font-weight="700" '
                   f'font-size="27" letter-spacing="1.5" fill="{ink}">{label}</text>')
        out.append(f'<rect x="{x-44}" y="{y0+856}" width="88" height="5" rx="2.5" fill="{a}"/>')
        out.append(f'<text x="{x}" y="{y0+904}" text-anchor="middle" font-family="Caveat, cursive" font-size="40" '
                   f'fill="{m}">{count}</text>')

    out.append(f'<rect x="{x0+60}" y="{y0+h-150}" width="{w-120}" height="108" rx="54" fill="{ink}"/>')
    out.append(f'<text x="{cx}" y="{y0+h-99}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="42" '
               f'letter-spacing="3" fill="{a}">LARGE PRINT</text>')
    out.append(f'<text x="{cx}" y="{y0+h-62}" text-anchor="middle" font-family="{SERIF}" font-size="24" '
               f'fill="#FFFFFF">{esc(cv["band_line"])}</text>')
    return "".join(out)


def back(x0, y0, w, h, cv, trim_right):
    """Contratapa; (x0, w) incluye el sangrado izquierdo. trim_right = x del borde de corte derecho."""
    m, a, ink, cream = PAL["main"], PAL["accent"], PAL["ink"], PAL["cream"]
    left = x0 + BLEED * U + 60
    width = trim_right - left - 60
    cxb = left + width / 2
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{cream}"/>',
           f'<rect x="{x0}" y="{y0}" width="{w}" height="250" fill="{m}"/>',
           texture(x0, y0, w, 250, 11),
           f'<text x="{cxb}" y="{y0+150}" text-anchor="middle" font-family="Caveat, cursive" font-size="86" fill="{a}">'
           f'{esc(cv["back_headline"])}</text>',
           f'<rect x="{left}" y="{y0+300}" width="{width}" height="410" rx="22" fill="#fff" stroke="{ink}" stroke-width="5"/>',
           f'<foreignObject x="{left+34}" y="{y0+326}" width="{width-68}" height="364">'
           f'<div xmlns="http://www.w3.org/1999/xhtml" class="backtext">'
           + "".join(f"<p>{p}</p>" for p in cv["back_intro"])
           + "<ul>" + "".join(f"<li>{b}</li>" for b in cv["back_bullets"]) + "</ul>"
           + f'<p class="close">{cv["back_close"]}</p></div></foreignObject>',
           f'<text x="{left}" y="{y0+790}" font-family="{SERIF}" font-weight="700" font-size="28" fill="{ink}">'
           f'{esc(cv["back_note"])}</text>',
           f'<text x="{left}" y="{y0+1000}" font-family="Caveat, cursive" font-size="40" fill="{m}">{esc(cv["series_line"])}</text>',
           f'<text x="{left}" y="{y0+1042}" font-family="{SERIF}" font-size="22" letter-spacing="4" fill="{ink}">'
           f'{esc(cv["author"].upper())}</text>']
    return "".join(out)


def spine(x0, y0, sw, h, cv):
    cx, cy = x0 + sw / 2, y0 + h / 2
    size = max(9, min(16, sw - 2 * 6.25 - 6))
    return (f'<rect x="{x0}" y="{y0}" width="{sw}" height="{h}" fill="{PAL["main"]}"/>'
            f'<text x="{cx}" y="{cy}" transform="rotate(90 {cx} {cy})" text-anchor="middle" dominant-baseline="central" '
            f'font-family="{SERIF}" font-weight="700" font-size="{size:.1f}" letter-spacing="1" fill="#FFFFFF">'
            f'{esc(cv["spine"])}</text>')


def main(src, dst, front_only=False):
    book = json.load(open(src, encoding="utf-8"))
    cv = book["cover"]
    tw, th = book["trim"]
    b = BLEED * U
    sw = cv["page_count"] * PAPER[cv.get("paper", "white")] * U
    H = (th + 2 * BLEED) * U
    if front_only:
        W = (tw + 2 * BLEED) * U
        svg = front(0, 0, W, H, cv)
        meta = ""
    else:
        W = 2 * (tw + BLEED) * U + sw
        fx = b + tw * U + sw  # borde izquierdo del frente (sin sangrado)
        # orden: contratapa y frente (cada uno con su sangrado) y encima el lomo, que tapa lo que invadió
        svg = (back(0, 0, b + tw * U + b, H, cv, trim_right=b + tw * U)
               + front(fx - b, 0, tw * U + 2 * b, H, cv)
               + spine(b + tw * U, 0, sw, H, cv))
        meta = f' data-spine="{sw/U:.4f}"'
    doc = f'''<!doctype html><html><head><meta charset="utf-8"><title>{esc(cv["script"])} {esc(cv["title"])} (cover)</title><style>
{font_css()}
@page {{ size: {W/U:.4f}in {H/U:.4f}in; margin: 0; }}
html, body {{ margin: 0; padding: 0; }}
svg {{ display: block; width: {W/U:.4f}in; height: {H/U:.4f}in; }}
.backtext {{ font-family: 'Playfair Display', Georgia, serif; font-size: 21px; line-height: 1.45; color: {PAL['ink']}; }}
.backtext p {{ margin: 0 0 12px; }}
.backtext ul {{ margin: 8px 0 12px; padding: 0; list-style: none; }}
.backtext li {{ margin-bottom: 7px; padding-left: 28px; position: relative; }}
.backtext li::before {{ content: ""; position: absolute; left: 2px; top: 9px; width: 12px; height: 12px; border-radius: 50%; background: {PAL['accent']}; }}
.backtext .close {{ font-weight: 700; margin-top: 12px; }}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg"{meta} viewBox="0 0 {W:.2f} {H:.2f}">{svg}</svg>
</body></html>'''
    open(dst, "w", encoding="utf-8").write(doc)
    print(f"{W/U:.4f} x {H/U:.4f} in (lomo {sw/U:.4f} in) -> {dst}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0], args[1], "--front-only" in sys.argv)

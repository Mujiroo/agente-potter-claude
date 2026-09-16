#!/usr/bin/env python3
"""Portada estilo "cozy" para la serie Calm & Cozy Puzzles (contraportada + lomo + frente).

Estilo tomado de lo que hoy funciona en el subnicho de calma en Amazon: fondo crema,
ilustración cálida dibujada a mano (taza, manta, planta, libro), tipografía con serifas
más una palabra manuscrita, sellos discretos y paleta salvia/terracota.

Todo vectorial y propio. Fuentes: Playfair Display y Caveat (OFL).

Uso: portada_cozy.py libro.json salida.html [--front-only] [--white]
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BLEED = 0.125
PAPER = {"white": 0.002252, "cream": 0.0025}
U = 100


def esc(s):
    return html.escape(s, quote=True)


def letter_texture(x0, y0, w, h, color, opacity, cell=46, seed=3, size=26):
    """Textura suave de letras, como las portadas de la otra serie."""
    import random
    rng = random.Random(seed)
    out = [f'<g fill="{color}" opacity="{opacity}" font-family="Playfair Display, serif" font-weight="700" '
           f'font-size="{size}" text-anchor="middle">']
    for r in range(int(h // cell) + 1):
        for k in range(int(w // cell) + 1):
            out.append(f'<text x="{x0+k*cell+cell/2}" y="{y0+r*cell+cell/2+9}">'
                       f'{rng.choice("ABCDEFGHIJKLMNOPRSTUVWY")}</text>')
    out.append("</g>")
    return "".join(out)


def leaves(x, y, c, k=1.0, rot=0):
    """Ramita con hojas."""
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale({k})" stroke="{c["ink"]}" stroke-width="5" fill="none">'
            f'<path d="M0,0 C10,-40 14,-80 8,-120"/>'
            f'<path d="M6,-28 C-18,-34 -30,-52 -28,-70 C-8,-66 4,-48 6,-28 z" fill="{c["sage"]}"/>'
            f'<path d="M8,-58 C30,-64 44,-82 42,-100 C22,-96 10,-78 8,-58 z" fill="{c["sage2"]}"/>'
            f'<path d="M6,-88 C-14,-94 -26,-110 -24,-126 C-6,-122 4,-104 6,-88 z" fill="{c["sage"]}"/></g>')


def mug(cx, cy, c, words, k=1.0):
    """Taza humeante; en el frente lleva una mini sopa de letras."""
    rows = words["grid"]
    nr, nc = len(rows), len(rows[0])
    cell = 42
    gw, gh = nc * cell, nr * cell
    gx, gy = cx - gw / 2, cy - gh / 2 + 6
    ink = c["ink"]
    out = [f'<g transform="translate({cx},{cy}) scale({k}) translate({-cx},{-cy})">']
    # vapor
    for dx in (-52, 0, 52):
        out.append(f'<path d="M{cx+dx},{gy-64} c-14,-20 14,-30 0,-50 c-12,-16 8,-26 2,-38" stroke="{ink}" '
                   f'stroke-width="6" fill="none" stroke-linecap="round" opacity=".75"/>')
    # cuerpo
    bx0, by0, bw, bh = gx - 46, gy - 40, gw + 92, gh + 96
    out.append(f'<path d="M{bx0+bw},{by0+34} c56,0 78,26 78,58 c0,34 -26,58 -80,58" fill="none" stroke="{ink}" stroke-width="10"/>')
    out.append(f'<path d="M{bx0},{by0} h{bw} v{bh-40} c0,26 -22,40 -52,40 h{-(bw-104)} c-30,0 -52,-14 -52,-40 z" '
               f'fill="#fff" stroke="{ink}" stroke-width="10" stroke-linejoin="round"/>')
    out.append(f'<rect x="{bx0}" y="{by0}" width="{bw}" height="26" rx="12" fill="{c["terracotta"]}" stroke="{ink}" stroke-width="8"/>')
    for (r1, c1, r2, c2) in words["found"]:
        out.append(f'<line x1="{gx+c1*cell+cell/2}" y1="{gy+r1*cell+cell/2}" x2="{gx+c2*cell+cell/2}" '
                   f'y2="{gy+r2*cell+cell/2}" stroke="{c["highlight"]}" stroke-width="34" stroke-linecap="round"/>')
    for r, row in enumerate(rows):
        for j, ch in enumerate(row):
            out.append(f'<text x="{gx+j*cell+cell/2}" y="{gy+r*cell+cell/2+11}" text-anchor="middle" '
                       f'font-family="Playfair Display, serif" font-weight="700" font-size="30" fill="{ink}">{ch}</text>')
    # platillo
    out.append(f'<ellipse cx="{cx}" cy="{by0+bh+34}" rx="{bw/2+56}" ry="20" fill="{c["sage"]}" stroke="{ink}" stroke-width="9"/>')
    out.append("</g>")
    return "".join(out)


def book_and_blanket(x, y, c, k=1.0):
    """Libro abierto y manta doblada, apoyados a un costado."""
    ink = c["ink"]
    return (f'<g transform="translate({x},{y}) scale({k})">'
            f'<path d="M0,0 c-60,-22 -110,-16 -140,-4 l0,86 c30,-12 80,-18 140,4 z" fill="#fff" stroke="{ink}" stroke-width="8" stroke-linejoin="round"/>'
            f'<path d="M0,0 c60,-22 110,-16 140,-4 l0,86 c-30,-12 -80,-18 -140,4 z" fill="#fff" stroke="{ink}" stroke-width="8" stroke-linejoin="round"/>'
            f'<path d="M-104,16 h56 M-104,40 h56 M48,16 h56 M48,40 h56" stroke="{ink}" stroke-width="5" opacity=".5" stroke-linecap="round"/>'
            f'<g transform="translate(-36,104)">'
            f'<rect x="-120" y="0" width="300" height="44" rx="18" fill="{c["terracotta"]}" stroke="{ink}" stroke-width="8"/>'
            f'<rect x="-104" y="-34" width="270" height="44" rx="18" fill="{c["sage2"]}" stroke="{ink}" stroke-width="8"/>'
            f'<path d="M-70,22 h30 M10,22 h30 M90,22 h30" stroke="{ink}" stroke-width="5" opacity=".5" stroke-linecap="round"/>'
            f'</g></g>')


def badge(cx, cy, r, text1, text2, c):
    return (f'<g><circle cx="{cx}" cy="{cy}" r="{r}" fill="{c["terracotta"]}" stroke="{c["ink"]}" stroke-width="7"/>'
            f'<text x="{cx}" y="{cy-6}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
            f'font-size="{r*0.42:.0f}" fill="#fff">{esc(text1)}</text>'
            f'<text x="{cx}" y="{cy+r*0.42:.0f}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
            f'font-size="{r*0.3:.0f}" fill="#fff">{esc(text2)}</text></g>')


def front(x0, y0, w, h, cv, c, cx=None, white=False):
    cx = x0 + w / 2 if cx is None else cx
    ink = c["ink"]
    bg = "#FFFFFF" if white else c["bg"]
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{bg}"/>']
    if cv.get("texture", True):
        out.append(letter_texture(x0, y0, w, h, c["ink"], 0.05 if white else 0.09))
    # marco fino
    out.append(f'<rect x="{x0+38}" y="{y0+38}" width="{w-76}" height="{h-76}" rx="18" fill="none" '
               f'stroke="{ink}" stroke-width="5" opacity=".55"/>')
    if cv.get("author"):
        out.append(f'<text x="{cx}" y="{y0+92}" text-anchor="middle" font-family="Playfair Display, serif" '
                   f'font-size="24" letter-spacing="5" fill="{ink}">{esc(cv["author"].upper())}</text>')
    # título
    out.append(f'<text x="{cx}" y="{y0+196}" text-anchor="middle" font-family="Caveat, cursive" font-size="118" '
               f'fill="{c["terracotta"] if not white else "#444"}">{esc(cv["script"])}</text>')
    out.append(f'<text x="{cx}" y="{y0+286}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="76" textLength="{w-150}" lengthAdjust="spacingAndGlyphs" fill="{ink}">{esc(cv["title"])}</text>')
    out.append(f'<text x="{cx}" y="{y0+330}" text-anchor="middle" font-family="Playfair Display, serif" font-size="26" '
               f'letter-spacing="4" fill="{ink}">{esc(cv["subtitle"].upper())}</text>')
    out.append(f'<line x1="{cx-150}" y1="{y0+352}" x2="{cx+150}" y2="{y0+352}" stroke="{ink}" stroke-width="3" opacity=".6"/>')
    # escena
    out.append(leaves(x0 + 100, y0 + 560, c, 1.15, -14))
    out.append(leaves(x0 + w - 92, y0 + 590, c, 1.05, 16))
    out.append(mug(cx, y0 + 566, c, cv["cup"], 0.95))
    out.append(book_and_blanket(cx, y0 + 806, c, 0.86))
    out.append(badge(x0 + w - 128, y0 + 396, 74, cv["badge1"], cv["badge2"], c))
    # pie
    out.append(f'<rect x="{x0+38}" y="{y0+h-150}" width="{w-76}" height="112" rx="16" fill="{c["sage"]}" stroke="{ink}" stroke-width="6"/>')
    out.append(f'<text x="{cx}" y="{y0+h-98}" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" '
               f'font-size="40" letter-spacing="3" fill="{ink}">LARGE PRINT</text>')
    out.append(f'<text x="{cx}" y="{y0+h-62}" text-anchor="middle" font-family="Playfair Display, serif" font-size="23" '
               f'fill="{ink}">{esc(cv["band_line"])}</text>')
    return "".join(out)


def back(x0, y0, w, h, cv, c):
    ink = c["ink"]
    left = x0 + BLEED * U + 52
    width = w - BLEED * U - 104
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{c["bg"]}"/>',
           letter_texture(x0, y0, w, h, c["ink"], 0.09, seed=8) if cv.get("texture", True) else "",
           f'<rect x="{x0+BLEED*U+20}" y="{y0+38}" width="{w-BLEED*U-58}" height="{h-76}" rx="18" fill="none" stroke="{ink}" stroke-width="5" opacity=".55"/>',
           f'<text x="{left+width/2}" y="{y0+150}" text-anchor="middle" font-family="Caveat, cursive" font-size="74" '
           f'fill="{c["terracotta"]}">{esc(cv["back_headline"])}</text>',
           f'<rect x="{left}" y="{y0+186}" width="{width}" height="400" rx="20" fill="#fff" stroke="{ink}" stroke-width="5"/>',
           f'<foreignObject x="{left+28}" y="{y0+206}" width="{width-56}" height="370">'
           f'<div xmlns="http://www.w3.org/1999/xhtml" class="backtext">'
           + "".join(f"<p>{p}</p>" for p in cv["back_intro"])
           + "<ul>" + "".join(f"<li>{b}</li>" for b in cv["back_bullets"]) + "</ul>"
           + f'<p class="close">{cv["back_close"]}</p></div></foreignObject>',
           leaves(left + 40, y0 + 700, c, 0.85, -10),
           leaves(left + width - 40, y0 + 700, c, 0.85, 10),
           f'<text x="{left+width/2}" y="{y0+690}" text-anchor="middle" font-family="Playfair Display, serif" '
           f'font-weight="700" font-size="30" fill="{ink}">{esc(cv["back_note"])}</text>']
    return "".join(out)


def spine(x0, y0, sw, h, cv, c):
    cx, cy = x0 + sw / 2, y0 + h / 2
    size = max(9, min(16, sw - 2 * 6.25 - 2))
    return (f'<rect x="{x0}" y="{y0}" width="{sw}" height="{h}" fill="{c["bg"]}"/>'
            f'<text x="{cx}" y="{cy}" transform="rotate(90 {cx} {cy})" text-anchor="middle" dominant-baseline="central" '
            f'font-family="Playfair Display, serif" font-weight="700" font-size="{size:.1f}" fill="{c["ink"]}">{esc(cv["spine"])}</text>')


def front_svg_white(book):
    cv, c = book["cover"], dict(book["cover"]["colors"])
    c.update(bg="#FFFFFF", sage="#E6E6E6", sage2="#D6D6D6", terracotta="#8A8A8A", highlight="#D9D9D9", ink="#111111")
    tw, th = book["trim"]
    W, H = (tw + 2 * BLEED) * U, (th + 2 * BLEED) * U
    b = BLEED * U
    return (f'<svg class="cover1" xmlns="http://www.w3.org/2000/svg" viewBox="{b} {b} {tw*U} {th*U}">'
            f'{front(0, 0, W, H, cv, c, white=True)}</svg>')


def font_css():
    f = os.path.join(HERE, "fonts")
    return (f"@font-face {{ font-family: 'Playfair Display'; src: url('file://{f}/PlayfairDisplay-Bold.ttf'); font-weight: 700; }}"
            f"@font-face {{ font-family: 'Playfair Display'; src: url('file://{f}/PlayfairDisplay-Bold.ttf'); font-weight: 400; }}"
            f"@font-face {{ font-family: 'Caveat'; src: url('file://{f}/Caveat-Bold.ttf'); font-weight: 700; }}")


def main(src, dst, front_only=False, white=False):
    book = json.load(open(src, encoding="utf-8"))
    cv, c = book["cover"], book["cover"]["colors"]
    tw, th = book["trim"]
    sw = cv["page_count"] * PAPER[cv.get("paper", "white")] * U
    fw, fh = (tw + BLEED) * U, (th + 2 * BLEED) * U
    if front_only:
        W, H = fw + BLEED * U, fh
        svg = front(0, 0, W, H, cv, c, white=white)
    else:
        W, H = 2 * fw + sw, fh
        svg = (back(0, 0, fw, H, cv, c) + spine(fw, 0, sw, H, cv, c)
               + front(fw + sw, 0, fw, H, cv, c, cx=fw + sw + tw * U / 2))
    doc = f'''<!doctype html><html><head><meta charset="utf-8"><title>{esc(cv["title"])} (cover)</title><style>
{font_css()}
@page {{ size: {W/U:.4f}in {H/U:.4f}in; margin: 0; }}
html, body {{ margin: 0; padding: 0; }}
svg {{ display: block; width: {W/U:.4f}in; height: {H/U:.4f}in; }}
.backtext {{ font-family: 'Playfair Display', Georgia, serif; font-size: 19px; line-height: 1.45; color: {c['ink']}; }}
.backtext p {{ margin: 0 0 10px; }}
.backtext ul {{ margin: 8px 0 10px; padding: 0; list-style: none; }}
.backtext li {{ margin-bottom: 6px; padding-left: 26px; position: relative; }}
.backtext li::before {{ content: ""; position: absolute; left: 2px; top: 8px; width: 11px; height: 11px; border-radius: 50%; background: {c['terracotta']}; }}
.backtext .close {{ font-weight: 700; margin-top: 10px; }}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}">{svg}</svg>
</body></html>'''
    open(dst, "w", encoding="utf-8").write(doc)
    print(f"{W/U:.3f} x {H/U:.3f} in (lomo {sw/U:.4f} in) -> {dst}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0], args[1], "--front-only" in sys.argv, "--white" in sys.argv)

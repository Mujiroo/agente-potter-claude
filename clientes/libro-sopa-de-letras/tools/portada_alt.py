"""Estilos alternativos de portada (frente) para comparar contra el clásico de portada.py.

  bold : fondo saturado con textura de letras, título gigante en dos líneas, sello con el
         número de puzzles y barra roja LARGE PRINT abajo (patrón de los top sellers).
  grid : toda la portada es una sopa de letras con palabras del súper marcadas en color y
         bloques de título sólidos encima (estilo "Big Book of Word Search").
"""
import math
import random

from portada import cart, esc


def letter_texture(x0, y0, w, h, color, opacity, cell=42, seed=7, size=26):
    rng = random.Random(seed)
    out = [f'<g fill="{color}" opacity="{opacity}" font-family="Fredoka" font-weight="700" '
           f'font-size="{size}" text-anchor="middle">']
    for r in range(int(h // cell) + 1):
        for k in range(int(w // cell) + 1):
            out.append(f'<text x="{x0+k*cell+cell/2}" y="{y0+r*cell+cell/2+9}">'
                       f'{rng.choice("ABCDEFGHIJKLMNOPRSTUVWY")}</text>')
    out.append("</g>")
    return "".join(out)


def burst(bx, by, r_out, r_in, fill, stroke, n=16):
    pts = []
    for k in range(2 * n):
        rr = r_out if k % 2 == 0 else r_in
        a = math.pi * k / n
        pts.append(f"{bx+rr*math.cos(a):.1f},{by+rr*math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="6" stroke-linejoin="round"/>'


def scaled(svg, ox, oy, k):
    return f'<g transform="translate({ox},{oy}) scale({k}) translate({-ox},{-oy})">{svg}</g>'


def big_title(cx, y, text, size, width, fill, shadow, outline):
    t = (f'text-anchor="middle" font-family="Luckiest Guy" font-size="{size}" textLength="{width}" '
         f'lengthAdjust="spacingAndGlyphs"')
    return (f'<text x="{cx}" y="{y}" {t} fill="{shadow}" stroke="{shadow}" stroke-width="16" '
            f'stroke-linejoin="round" transform="translate(6,8)">{esc(text)}</text>'
            f'<text x="{cx}" y="{y}" {t} fill="{outline}" stroke="{outline}" stroke-width="16" '
            f'stroke-linejoin="round">{esc(text)}</text>'
            f'<text x="{cx}" y="{y}" {t} fill="{fill}">{esc(text)}</text>')


def price_tag(cx, cy, text, fill, ink, hole, text_color, size=58):
    return f'''
    <g transform="translate({cx},{cy}) rotate(-3)">
      <path d="M-205,-44 H175 L215,0 L175,44 H-205 a12,12 0 0 1 -12,-12 V-32 a12,12 0 0 1 12,-12 z"
            fill="{fill}" stroke="{ink}" stroke-width="6" stroke-linejoin="round"/>
      <circle cx="186" cy="0" r="9" fill="{hole}" stroke="{ink}" stroke-width="4"/>
      <text x="-15" y="21" text-anchor="middle" font-family="Luckiest Guy" font-size="{size}" fill="{text_color}">{esc(text)}</text>
    </g>'''


def front_bold(x0, y0, w, h, cv, c, cx=None, white=False):
    cx = x0 + w / 2 if cx is None else cx
    blue, navy, deep, word_fill, tex = "#1565C0", "#0B2E6B", "#0D47A1", "#FFFFFF", ("#FFFFFF", 0.11)
    if white:  # papel blanco, tinta negra
        blue, navy, deep, word_fill, tex = "#FFFFFF", "#111111", "#9E9E9E", "#FFFFFF", ("#000000", 0.07)
    out = ['<defs><radialGradient id="vign" cx="50%" cy="45%" r="75%">'
           '<stop offset="60%" stop-color="#000" stop-opacity="0"/>'
           f'<stop offset="100%" stop-color="#000" stop-opacity="{0 if white else .28}"/></radialGradient></defs>',
           f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{blue}"/>',
           letter_texture(x0, y0, w, h, *tex),
           f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#vign)"/>',
           big_title(cx, y0 + 180, "WORD", 150, 330, word_fill, deep, navy),
           big_title(cx, y0 + 322, "SEARCH", 150, w - 100, c["yellow"], deep, navy),
           scaled(cart(cx - 55, y0 + 455, cv["cart"], dict(c, ink=navy)), cx - 55, y0 + 455, 0.74),
           price_tag(cx, y0 + 398, cv["series_name"], "#FFFFFF", navy, "#FFFFFF" if white else blue, c["red"])]
    bx, by = x0 + w - 115, y0 + 585
    out.append(f'<g transform="rotate(10 {bx} {by})">{burst(bx, by, 82, 71, c["red"], "#fff")}'
               f'<text x="{bx}" y="{by-6}" text-anchor="middle" font-family="Luckiest Guy" font-size="60" fill="#fff">55</text>'
               f'<text x="{bx}" y="{by+30}" text-anchor="middle" font-family="Luckiest Guy" font-size="25" fill="#fff">PUZZLES</text></g>')
    out.append(f'<g transform="rotate(-6 {x0+105} {y0+58})"><rect x="{x0+50}" y="{y0+38}" width="110" height="40" rx="20" '
               f'fill="{c["yellow"]}" stroke="{navy}" stroke-width="4"/><text x="{x0+105}" y="{y0+67}" text-anchor="middle" '
               f'font-family="Luckiest Guy" font-size="24" fill="{navy}">{esc(cv["volume"])}</text></g>')
    out.append(f'''
    <rect x="{x0}" y="{y0+h-190}" width="{w}" height="190" fill="{c['red']}"/>
    <rect x="{x0}" y="{y0+h-190}" width="{w}" height="8" fill="{navy}"/>
    <text x="{cx}" y="{y0+h-112}" text-anchor="middle" font-family="Luckiest Guy" font-size="66" textLength="{w-130}" lengthAdjust="spacingAndGlyphs" fill="#fff">LARGE PRINT</text>
    <text x="{cx}" y="{y0+h-72}" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="25" fill="#fff">Supermarket Puzzles for Adults &amp; Seniors</text>
    <text x="{cx}" y="{y0+h-42}" text-anchor="middle" font-family="Fredoka" font-weight="600" font-size="19" fill="{c['yellow']}">Solutions Included</text>''')
    return "".join(out)


def front_grid(x0, y0, w, h, cv, c, cx=None, white=False):
    cx = x0 + w / 2 if cx is None else cx
    ink = "#14213D"
    rng = random.Random(3)
    cell = 44
    cols, rows = int(w // cell) + 1, int(h // cell) + 1
    grid = [[rng.choice("ABCDEFGHIJKLMNOPRSTUVWY") for _ in range(cols)] for _ in range(rows)]
    # palabras reales del súper, en zonas que quedan a la vista (fila, col, dirección)
    marks = [("BANANA", 1, 1, 0, 1), ("CHEESE", 9, 0, 1, 0), ("SALT", 9, 13, 1, 0),
             ("APPLE", 15, 1, 0, 1), ("BREAD", 15, 8, 0, 1), ("MILK", 16, 4, 0, 1), ("EGGS", 20, 5, 0, 1)]
    palette = [c["yellow"], "#7BD389", "#FF8A80", "#80D8FF"]
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#FFFFFF"/>']
    for i, (word, r, k, dr, dc) in enumerate(marks):
        if r + dr * (len(word) - 1) >= rows or k + dc * (len(word) - 1) >= cols:
            continue
        for j, ch in enumerate(word):
            grid[r + dr * j][k + dc * j] = ch
        x1, y1 = x0 + k * cell + cell / 2, y0 + r * cell + cell / 2
        x2, y2 = x1 + dc * (len(word) - 1) * cell, y1 + dr * (len(word) - 1) * cell
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{palette[i % 4]}" '
                   f'stroke-width="36" stroke-linecap="round"/>')
    out.append('<g fill="#23324D" font-family="Fredoka" font-weight="700" font-size="28" text-anchor="middle">')
    for r in range(rows):
        for k in range(cols):
            out.append(f'<text x="{x0+k*cell+cell/2}" y="{y0+r*cell+cell/2+10}">{grid[r][k]}</text>')
    out.append('</g>')
    out.append(f'''
    <rect x="{x0+40}" y="{y0+120}" width="{w-80}" height="255" rx="18" fill="{c['red']}" stroke="{ink}" stroke-width="7"/>
    <text x="{cx}" y="{y0+235}" text-anchor="middle" font-family="Luckiest Guy" font-size="112" textLength="{w-150}" lengthAdjust="spacingAndGlyphs" fill="#fff">WORD</text>
    <text x="{cx}" y="{y0+350}" text-anchor="middle" font-family="Luckiest Guy" font-size="112" textLength="{w-150}" lengthAdjust="spacingAndGlyphs" fill="#fff">SEARCH</text>
    {price_tag(cx, y0 + 440, cv['series_name'], c['yellow'], ink, '#fff', ink)}
    <rect x="{x0+40}" y="{y0+510}" width="{w-80}" height="150" rx="18" fill="#2E7D32" stroke="{ink}" stroke-width="7"/>
    <text x="{x0+170}" y="{y0+622}" text-anchor="middle" font-family="Luckiest Guy" font-size="118" fill="{c['yellow']}">55</text>
    <text x="{x0+395}" y="{y0+575}" text-anchor="middle" font-family="Luckiest Guy" font-size="44" fill="#fff">LARGE PRINT</text>
    <text x="{x0+395}" y="{y0+625}" text-anchor="middle" font-family="Luckiest Guy" font-size="44" fill="#fff">PUZZLES</text>
    <rect x="{x0+40}" y="{y0+h-160}" width="{w-80}" height="92" rx="18" fill="#1565C0" stroke="{ink}" stroke-width="7"/>
    <text x="{cx}" y="{y0+h-119}" text-anchor="middle" font-family="Luckiest Guy" font-size="30" textLength="{w-150}" lengthAdjust="spacingAndGlyphs" fill="#fff">SUPERMARKET PUZZLES</text>
    <text x="{cx}" y="{y0+h-85}" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="21" fill="{c['yellow']}">for Adults &amp; Seniors · Solutions Included</text>
    <g transform="rotate(6 {x0+w-100} {y0+62})"><rect x="{x0+w-155}" y="{y0+42}" width="110" height="42" rx="21" fill="{ink}"/>
      <text x="{x0+w-100}" y="{y0+72}" text-anchor="middle" font-family="Luckiest Guy" font-size="25" fill="#fff">{esc(cv['volume'])}</text></g>''')
    return "".join(out)


STYLES = {"bold": front_bold, "grid": front_grid}


def back_bold(x0, y0, w, h, cv, c):
    """Contraportada del estilo bold. Zona de código de barras (abajo a la derecha, junto al lomo) libre."""
    from portada import BLEED, U, sample
    blue, navy = "#1565C0", "#0B2E6B"
    left = x0 + BLEED * U + 45
    width = w - BLEED * U - 90
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{blue}"/>',
           letter_texture(x0, y0, w, h, "#FFFFFF", 0.11, seed=11),
           big_title(left + width / 2, y0 + 118, cv["back_headline"].upper(), 44, width - 10, c["yellow"], "#0D47A1", navy),
           f'<rect x="{left}" y="{y0+150}" width="{width}" height="405" rx="24" fill="#fff" stroke="{navy}" stroke-width="6"/>',
           f'<foreignObject x="{left+28}" y="{y0+170}" width="{width-56}" height="375">'
           f'<div xmlns="http://www.w3.org/1999/xhtml" class="backtext">'
           + "".join(f"<p>{p}</p>" for p in cv["back_intro"])
           + "<ul>" + "".join(f"<li>{b}</li>" for b in cv["back_bullets"]) + "</ul>"
           + f'<p class="close">{cv["back_close"]}</p></div></foreignObject>',
           f'<rect x="{x0}" y="{y0+h-190}" width="{w}" height="190" fill="{c["red"]}"/>',
           f'<rect x="{x0}" y="{y0+h-190}" width="{w}" height="8" fill="{navy}"/>',
           sample(left + 15, y0 + 590, cv, dict(c, ink=navy))]
    return "".join(out)


def spine_bold(x0, y0, sw, h, cv, c):
    navy = "#0B2E6B"
    cx, cy = x0 + sw / 2, y0 + h / 2
    size = max(8, min(15, sw - 2 * 6.25 - 2))
    return (f'<rect x="{x0}" y="{y0}" width="{sw}" height="{h}" fill="#1565C0"/>'
            f'<rect x="{x0}" y="{y0+h-190}" width="{sw}" height="190" fill="{c["red"]}"/>'
            f'<rect x="{x0}" y="{y0+h-190}" width="{sw}" height="8" fill="{navy}"/>'
            f'<text x="{cx}" y="{cy-40}" transform="rotate(90 {cx} {cy-40})" text-anchor="middle" dominant-baseline="central" '
            f'font-family="Luckiest Guy" font-size="{size:.1f}" fill="#fff" letter-spacing="1">{esc(cv["spine"])}</text>')


BACKS = {"bold": (back_bold, spine_bold)}

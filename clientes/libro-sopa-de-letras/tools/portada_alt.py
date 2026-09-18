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


def big_title(cx, y, text, size, width, fill, shadow, outline, thick=8):
    """Título con contorno y sombra SIN usar stroke: el texto con stroke sale como fuente Type3 en el
    PDF de Chrome (riesgo de rechazo en KDP). El contorno se arma con copias rellenas desplazadas."""
    t = (f'text-anchor="middle" font-family="Luckiest Guy" font-size="{size}" textLength="{width}" '
         f'lengthAdjust="spacingAndGlyphs"')
    ring = [(round(thick * math.cos(a), 2), round(thick * math.sin(a), 2))
            for a in [2 * math.pi * k / 24 for k in range(24)]]
    out = [f'<g fill="{shadow}">' + "".join(
        f'<text x="{cx + 6 + dx}" y="{y + 8 + dy}" {t}>{esc(text)}</text>' for dx, dy in ring) + "</g>"]
    out.append(f'<g fill="{outline}">' + "".join(
        f'<text x="{cx + dx}" y="{y + dy}" {t}>{esc(text)}</text>' for dx, dy in ring) + "</g>")
    out.append(f'<text x="{cx}" y="{y}" {t} fill="{fill}">{esc(text)}</text>')
    return "".join(out)


def price_tag(cx, cy, text, fill, ink, hole, text_color, size=58):
    # nombres largos (CHRISTMAS HUNT!) se ajustan al ancho de la etiqueta; los cortos quedan igual
    fit = ' textLength="350" lengthAdjust="spacingAndGlyphs"' if len(text) > 11 else ""
    return f'''
    <g transform="translate({cx},{cy}) rotate(-3)">
      <path d="M-205,-44 H175 L215,0 L175,44 H-205 a12,12 0 0 1 -12,-12 V-32 a12,12 0 0 1 12,-12 z"
            fill="{fill}" stroke="{ink}" stroke-width="6" stroke-linejoin="round"/>
      <circle cx="186" cy="0" r="9" fill="{hole}" stroke="{ink}" stroke-width="4"/>
      <text x="-15" y="21" text-anchor="middle" font-family="Luckiest Guy" font-size="{size}" fill="{text_color}"{fit}>{esc(text)}</text>
    </g>'''


def bold_palette(cv):
    """Colores del estilo bold: fondo, tinta oscura y sombra. Cada volumen puede cambiarlos."""
    p = cv.get("bold", {})
    return p.get("bg", "#1565C0"), p.get("ink", "#0B2E6B"), p.get("deep", "#0D47A1")


def illustration(cv, cx, top, c, ink):
    kind = cv.get("illustration", "cart")
    if kind == "retrotv":
        return scaled(retrotv(cx - 70, top + 20, cv["cart"], dict(c, ink=ink)), cx - 70, top + 20, 0.58)
    if kind == "giftbox":
        return scaled(giftbox(cx - 70, top + 28, cv["cart"], dict(c, ink=ink)), cx - 70, top + 28, 0.6)
    if kind == "billboard":
        return scaled(billboard(cx - 20, top - 10, cv["cart"], dict(c, ink=ink)), cx - 20, top - 10, 0.62)
    if kind == "suitcase":
        return scaled(suitcase(cx - 95, top + 40, cv["cart"], dict(c, ink=ink)), cx - 95, top + 40, 0.66)
    return scaled(cart(cx - 55, top, cv["cart"], dict(c, ink=ink)), cx - 55, top, 0.72)


def festive_back(x0, y0, w, h, seed=5):
    """Copos de nieve dispersos (detrás de los títulos)."""
    rng = random.Random(seed)
    out = []
    for _ in range(38):
        sx, sy = x0 + rng.uniform(20, w - 20), y0 + rng.uniform(20, h - 230)
        sc = rng.uniform(0.35, 0.8)
        op = rng.uniform(0.45, 0.9)
        out.append(f'<g transform="translate({sx:.0f},{sy:.0f}) scale({sc:.2f})" stroke="#fff" stroke-width="5" '
                   f'stroke-linecap="round" opacity="{op:.2f}"><path d="M0,-20 V20 M-17,-10 L17,10 M-17,10 L17,-10"/></g>')
    return "".join(out)


def snow_caps(cx, y, width, n, size):
    """Nieve acumulada sobre cada letra del título (aprox. por posición uniforme)."""
    top = y - size * 0.70
    step = width / n
    out = []
    for k in range(n):
        lx = cx - width / 2 + step * (k + 0.5)
        wd = step * 0.78
        out.append(f'<path d="M{lx-wd/2:.0f},{top+10:.0f} C{lx-wd/2:.0f},{top-14:.0f} {lx-wd/6:.0f},{top-20:.0f} {lx:.0f},{top-12:.0f} '
                   f'C{lx+wd/6:.0f},{top-22:.0f} {lx+wd/2:.0f},{top-12:.0f} {lx+wd/2:.0f},{top+10:.0f} '
                   f'C{lx+wd/4:.0f},{top+2:.0f} {lx-wd/4:.0f},{top+18:.0f} {lx-wd/2:.0f},{top+10:.0f} z" fill="#fff"/>')
    return "".join(out)


def light_garland(x0, w, y, c, ink):
    """Guirnalda de luces navideñas de lado a lado."""
    out = [f'<path d="M{x0-10},{y} Q{x0+w/4},{y+34} {x0+w/2},{y+6} Q{x0+3*w/4},{y+34} {x0+w+10},{y}" '
           f'fill="none" stroke="{ink}" stroke-width="4"/>']
    cols = [c["red"], c["yellow"], "#4FC3F7", "#FFFFFF", "#FF8A65"]
    for k in range(14):
        t = (k + 0.5) / 14
        if t < 0.5:
            u = t * 2; bx = x0 + u * w / 2; by = y + 2 * (1 - u) * u * 34 + u * u * 6
        else:
            u = (t - 0.5) * 2; bx = x0 + w / 2 + u * w / 2; by = (1 - u) ** 2 * (y + 6) + 2 * (1 - u) * u * (y + 34) + u * u * y
        if 0.32 < t < 0.68:  # no tapar el nombre del autor, centrado arriba
            continue
        col = cols[k % len(cols)]
        out.append(f'<g transform="translate({bx:.0f},{by:.0f}) rotate({(-1)**k*12})"><rect x="-4" y="-2" width="8" height="8" fill="{ink}"/>'
                   f'<ellipse cx="0" cy="14" rx="8" ry="12" fill="{col}" stroke="{ink}" stroke-width="3"/></g>')
    return "".join(out)


def holly(x, y, c, ink, k=1.0):
    return (f'<g transform="translate({x},{y}) scale({k})">'
            f'<path d="M0,0 C-14,-16 -38,-14 -46,-4 C-36,-2 -36,8 -44,14 C-28,16 -12,10 0,0 z" fill="#2E7D32" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M0,0 C14,-16 38,-14 46,-4 C36,-2 36,8 44,14 C28,16 12,10 0,0 z" fill="#388E3C" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>'
            f'<circle cx="-6" cy="6" r="8" fill="{c["red"]}" stroke="{ink}" stroke-width="3"/>'
            f'<circle cx="8" cy="4" r="8" fill="{c["red"]}" stroke="{ink}" stroke-width="3"/>'
            f'<circle cx="1" cy="-7" r="8" fill="{c["red"]}" stroke="{ink}" stroke-width="3"/></g>')


def santa_hat(x, y, c, ink, rot=-18):
    return (f'<g transform="translate({x},{y}) rotate({rot})">'
            f'<path d="M-34,0 C-30,-40 10,-62 44,-40 C30,-34 22,-20 26,0 z" fill="{c["red"]}" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>'
            f'<rect x="-40" y="-6" width="72" height="16" rx="8" fill="#fff" stroke="{ink}" stroke-width="4"/>'
            f'<circle cx="46" cy="-40" r="10" fill="#fff" stroke="{ink}" stroke-width="4"/></g>')


def snow_ground(x0, y, w):
    return (f'<path d="M{x0},{y} C{x0+w*0.12},{y-26} {x0+w*0.25},{y-8} {x0+w*0.38},{y-22} C{x0+w*0.52},{y-38} {x0+w*0.66},{y-6} '
            f'{x0+w*0.8},{y-24} C{x0+w*0.9},{y-34} {x0+w*0.96},{y-14} {x0+w},{y-20} L{x0+w},{y+12} L{x0},{y+12} z" fill="#fff"/>')


def front_bold(x0, y0, w, h, cv, c, cx=None, white=False):
    cx = x0 + w / 2 if cx is None else cx
    blue, navy, deep = bold_palette(cv)
    word_fill, tex = "#FFFFFF", ("#FFFFFF", 0.11)
    if white:  # papel blanco, tinta negra
        blue, navy, deep, word_fill, tex = "#FFFFFF", "#111111", "#9E9E9E", "#FFFFFF", ("#000000", 0.07)
    out = ['<defs><radialGradient id="vign" cx="50%" cy="45%" r="75%">'
           '<stop offset="60%" stop-color="#000" stop-opacity="0"/>'
           f'<stop offset="100%" stop-color="#000" stop-opacity="{0 if white else .28}"/></radialGradient></defs>',
           f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{blue}"/>',
           letter_texture(x0, y0, w, h, *tex, seed=42),  # semilla verificada sin groserías EN+ES en 8 direcciones (18-sep)
           f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#vign)"/>']
    festive = cv.get("festive") and not white
    if festive:
        out.append(festive_back(x0, y0, w, h))
    out += [big_title(cx, y0 + 200, "WORD", 146, 322, word_fill, deep, navy),
            big_title(cx, y0 + 336, "SEARCH", 146, w - 110, c["yellow"], deep, navy)]
    if cv.get("festive"):
        out += [snow_caps(cx, y0 + 200, 322, 4, 146), snow_caps(cx, y0 + 336, w - 110, 6, 146)]
    out += [illustration(cv, cx, y0 + 470, c, navy)]
    if festive:
        out.append(snow_ground(x0, y0 + h - 196, w))
    out += [price_tag(cx, y0 + 410, cv["series_name"], "#FFFFFF", navy, "#FFFFFF" if white else blue, c["red"])]
    if festive:  # en la p1 B/N se omiten (tienen colores propios)
        out.append(holly(cx + 150, y0 + 366, c, navy, 0.8))
        out.append(light_garland(x0, w, y0 + 18, c, navy))
    if cv.get("author"):
        # autor arriba y centrado, separado del título
        out.append(f'<text x="{cx}" y="{y0+62}" text-anchor="middle" font-family="Fredoka" font-weight="700" '
                   f'font-size="21" letter-spacing="4" fill="{navy if white else "#FFFFFF"}">{esc(cv["author"].upper())}</text>')
    if cv.get("illustration") in ("suitcase", "billboard", "giftbox", "retrotv"):
        bx, by, k = x0 + w - 118, y0 + 648, 0.88
    else:
        bx, by, k = x0 + w - 128, y0 + 585, 1
    pre = f"translate({bx},{by}) scale({k}) translate({-bx},{-by}) " if k != 1 else ""
    out.append(f'<g transform="{pre}rotate(10 {bx} {by})">{burst(bx, by, 82, 71, c["red"], "#fff")}'
               f'<text x="{bx}" y="{by-6}" text-anchor="middle" font-family="Luckiest Guy" font-size="60" fill="#fff">{cv.get("count", "55")}</text>'
               f'<text x="{bx}" y="{by+30}" text-anchor="middle" font-family="Luckiest Guy" font-size="25" fill="#fff">PUZZLES</text></g>')
    vx, vy = x0 + 92, y0 + 360  # VOL. 1 como etiqueta pegada al extremo izquierdo del precio
    out.append(f'<g transform="rotate(-10 {vx} {vy})"><rect x="{vx-52}" y="{vy-20}" width="104" height="40" rx="20" '
               f'fill="{c["yellow"]}" stroke="{navy}" stroke-width="4"/><text x="{vx}" y="{vy+9}" text-anchor="middle" '
               f'font-family="Luckiest Guy" font-size="24" fill="{navy}">{esc(cv["volume"])}</text></g>')
    if cv.get("festive"):
        out.append(santa_hat(vx - 44, vy - 20, c, navy))
    out.append(f'''
    <rect x="{x0}" y="{y0+h-190}" width="{w}" height="190" fill="{c['red']}"/>
    <rect x="{x0}" y="{y0+h-190}" width="{w}" height="8" fill="{navy}"/>
    <text x="{cx}" y="{y0+h-112}" text-anchor="middle" font-family="Luckiest Guy" font-size="66" textLength="{w-130}" lengthAdjust="spacingAndGlyphs" fill="#fff">LARGE PRINT</text>
    <text x="{cx}" y="{y0+h-72}" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="25" fill="#fff">{esc(cv.get("band_line", "Supermarket Puzzles for Adults & Seniors"))}</text>
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


def suitcase(cx, top, words, c):
    """Maleta de viaje cuyo costado es una sopa de letras con ciudades marcadas; globo a la derecha,
    avión de papel con estela arriba."""
    rows = words["grid"]
    nr, nc = len(rows), len(rows[0])
    cell = 42
    gw, gh = nc * cell, nr * cell
    gx, gy = cx - gw / 2, top + 70
    ink = c["ink"]
    bx0, by0, bw, bh = gx - 34, gy - 44, gw + 68, gh + 88
    out = []
    # globo (esquemático, tierra abstracta) asomando a la derecha, detrás de la maleta
    gcx, gcy, gr = bx0 + bw + 70, gy + 30, 105
    land = c.get("land", "#7BD389")
    out.append(f'''
    <circle cx="{gcx}" cy="{gcy}" r="{gr}" fill="{c.get('sea', '#4FC3F7')}" stroke="{ink}" stroke-width="7"/>
    <path d="M{gcx-60},{gcy-55} c25,-30 60,-25 70,-5 c8,18 -20,30 -35,45 c-15,15 -40,5 -45,-15 c-4,-12 2,-18 10,-25 z" fill="{land}"/>
    <path d="M{gcx+10},{gcy+25} c25,-12 55,0 58,22 c3,22 -25,38 -48,30 c-20,-8 -28,-40 -10,-52 z" fill="{land}"/>
    <path d="M{gcx+35},{gcy-78} c18,-6 38,4 36,18 c-2,12 -22,14 -34,8 c-10,-6 -12,-22 -2,-26 z" fill="{land}"/>
    <ellipse cx="{gcx}" cy="{gcy}" rx="{gr*0.45}" ry="{gr}" fill="none" stroke="{ink}" stroke-width="3" opacity=".5"/>
    <line x1="{gcx-gr}" y1="{gcy}" x2="{gcx+gr}" y2="{gcy}" stroke="{ink}" stroke-width="3" opacity=".5"/>
    <path d="M{gcx-gr*0.87},{gcy-gr*0.5} Q{gcx},{gcy-gr*0.62} {gcx+gr*0.87},{gcy-gr*0.5}" fill="none" stroke="{ink}" stroke-width="3" opacity=".5"/>
    <path d="M{gcx-gr*0.87},{gcy+gr*0.5} Q{gcx},{gcy+gr*0.38} {gcx+gr*0.87},{gcy+gr*0.5}" fill="none" stroke="{ink}" stroke-width="3" opacity=".5"/>
    <g transform="translate({gcx+45},{gcy+5})">
      <path d="M0,0 c-20,-24 -22,-50 0,-62 c22,12 20,38 0,62 z" fill="{c['red']}" stroke="{ink}" stroke-width="5"/>
      <circle cx="0" cy="-40" r="8" fill="#fff"/>
    </g>
    <path d="M{bx0+30},{by0-40} C{bx0+120},{by0-110} {bx0+260},{by0-95} {gcx-40},{gcy-gr-5}" fill="none" stroke="#fff"
          stroke-width="6" stroke-dasharray="16 13" stroke-linecap="round"/>
    <g transform="translate({bx0+15},{by0-30}) rotate(-25)">
      <path d="M-46,10 L54,-26 L-6,36 L-14,16 z" fill="#fff" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>
      <path d="M-14,16 L54,-26 L-2,14" fill="{c.get('plane_fold', '#DDE7EE')}" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>
    </g>''')
    # asa
    out.append(f'<path d="M{cx-62},{by0+2} V{by0-34} a16,16 0 0 1 16,-16 H{cx+46} a16,16 0 0 1 16,16 V{by0+2}" '
               f'fill="none" stroke="{ink}" stroke-width="12" stroke-linejoin="round"/>')
    # cuerpo con franjas y correas
    out.append(f'<rect x="{bx0}" y="{by0}" width="{bw}" height="{bh}" rx="30" fill="#fff" stroke="{ink}" stroke-width="9"/>')
    out.append(f'<rect x="{bx0+5}" y="{by0+5}" width="{bw-10}" height="28" rx="14" fill="{c["yellow"]}"/>')
    out.append(f'<rect x="{bx0+5}" y="{by0+bh-33}" width="{bw-10}" height="28" rx="14" fill="{c["yellow"]}"/>')
    for sx in (bx0 + 70, bx0 + bw - 70):
        out.append(f'<rect x="{sx-9}" y="{by0+5}" width="18" height="28" fill="{ink}" opacity=".85"/>'
                   f'<rect x="{sx-9}" y="{by0+bh-33}" width="18" height="28" fill="{ink}" opacity=".85"/>')
    for (r1, c1, r2, c2) in words["found"]:
        out.append(f'<line x1="{gx+c1*cell+cell/2}" y1="{gy+r1*cell+cell/2}" x2="{gx+c2*cell+cell/2}" '
                   f'y2="{gy+r2*cell+cell/2}" stroke="{c["highlight"]}" stroke-width="34" stroke-linecap="round"/>')
    for r, row in enumerate(rows):
        for k, ch in enumerate(row):
            out.append(f'<text x="{gx+k*cell+cell/2}" y="{gy+r*cell+cell/2+11}" text-anchor="middle" '
                       f'font-family="Fredoka" font-weight="700" font-size="31" fill="{ink}">{ch}</text>')
    # ruedas y sombra
    out.append(f'<ellipse cx="{cx+60}" cy="{by0+bh+42}" rx="{bw/2+90}" ry="13" fill="#000" opacity=".14"/>')
    for wx in (bx0 + 55, bx0 + bw - 55):
        out.append(f'<rect x="{wx-6}" y="{by0+bh}" width="12" height="16" fill="{ink}"/>'
                   f'<circle cx="{wx}" cy="{by0+bh+24}" r="14" fill="{ink}"/><circle cx="{wx}" cy="{by0+bh+24}" r="5" fill="#fff"/>')
    # lupa
    lr, lc = words["lens"]
    lx, ly = gx + lc * cell + cell / 2, gy + lr * cell + cell / 2
    out.append(f'''
    <line x1="{lx+52}" y1="{ly+52}" x2="{lx+120}" y2="{ly+120}" stroke="{ink}" stroke-width="22" stroke-linecap="round"/>
    <circle cx="{lx}" cy="{ly}" r="66" fill="#fff" fill-opacity=".25" stroke="{ink}" stroke-width="11"/>
    <path d="M{lx-40},{ly-22} a48,48 0 0 1 30,-30" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round"/>''')
    return "".join(out)

def billboard(cx, top, words, c):
    """Cartel de carretera cuya cara es una sopa de letras con estados marcados; auto clásico delante."""
    rows = words["grid"]
    nr, nc = len(rows), len(rows[0])
    cell = 42
    gw, gh = nc * cell, nr * cell
    gx, gy = cx - gw / 2, top + 60
    ink = c["ink"]
    bx0, by0, bw, bh = gx - 30, gy - 30, gw + 60, gh + 60
    out = []
    # postes
    for px in (bx0 + 70, bx0 + bw - 70):
        out.append(f'<rect x="{px-10}" y="{by0+bh-10}" width="20" height="130" fill="{c.get("post", "#8D6E63")}" stroke="{ink}" stroke-width="6"/>')
    # carretera
    out.append(f'<path d="M{bx0-120},{by0+bh+150} L{bx0+bw+120},{by0+bh+150} L{bx0+bw+60},{by0+bh+105} L{bx0-60},{by0+bh+105} z" '
               f'fill="#4A4A4A" stroke="{ink}" stroke-width="6" stroke-linejoin="round"/>')
    for k in range(6):
        x = bx0 - 40 + k * (bw + 80) / 6
        out.append(f'<rect x="{x}" y="{by0+bh+124}" width="46" height="8" rx="4" fill="{c["yellow"]}"/>')
    # cartel
    out.append(f'<rect x="{bx0}" y="{by0}" width="{bw}" height="{bh}" rx="14" fill="#fff" stroke="{ink}" stroke-width="9"/>')
    usa = words.get("usa_flag")
    if usa:
        # cabecera del cartel como bandera: campo azul con estrellas + franjas rojas y blancas
        hx, hy, hw, hh = bx0 - 14, by0 - 44, bw + 28, 52
        blue = c.get("flag_blue", "#1E3A8A")
        out.append(f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="8" fill="#fff" stroke="{ink}" stroke-width="6"/>')
        for k in range(0, 7, 2):
            out.append(f'<rect x="{hx+3}" y="{hy+3+k*(hh-6)/7}" width="{hw-6}" height="{(hh-6)/7}" fill="{c["red"]}"/>')
        cw = hw * 0.3
        out.append(f'<rect x="{hx+3}" y="{hy+3}" width="{cw}" height="{(hh-6)*4/7}" fill="{blue}"/>')
        for r in range(2):
            for k in range(6):
                sx, sy = hx + 16 + k * (cw - 26) / 5, hy + 10 + r * 12
                out.append(f'<circle cx="{sx}" cy="{sy}" r="3" fill="#fff"/>')
        out.append(f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="8" fill="none" stroke="{ink}" stroke-width="6"/>')
        # bandera flameando en su asta, a la izquierda del cartel
        fx, fy = bx0 - 196, by0 - 10
        out.append(f'<rect x="{fx-6}" y="{fy-20}" width="12" height="{bh+150}" rx="6" fill="{c.get("post", "#8D6E63")}" stroke="{ink}" stroke-width="5"/>')
        out.append(f'<circle cx="{fx}" cy="{fy-26}" r="12" fill="{c["yellow"]}" stroke="{ink}" stroke-width="5"/>')
        fw, fh = 158, 100
        wave = lambda yy: f"M{fx+6},{yy} C{fx+60},{yy-18} {fx+120},{yy+18} {fx+6+fw},{yy}"
        out.append(f'<path d="M{fx+6},{fy} C{fx+60},{fy-18} {fx+120},{fy+18} {fx+6+fw},{fy} L{fx+6+fw},{fy+fh} '
                   f'C{fx+120},{fy+fh+18} {fx+60},{fy+fh-18} {fx+6},{fy+fh} z" fill="#fff" stroke="{ink}" stroke-width="6" stroke-linejoin="round"/>')
        for k in range(0, 13, 2):
            y1 = fy + k * fh / 13
            out.append(f'<path d="M{fx+6},{y1} C{fx+60},{y1-18} {fx+120},{y1+18} {fx+6+fw},{y1} L{fx+6+fw},{y1+fh/13} '
                       f'C{fx+120},{y1+fh/13+18} {fx+60},{y1+fh/13-18} {fx+6},{y1+fh/13} z" fill="{c["red"]}"/>')
        cy2 = fy + fh * 7 / 13
        out.append(f'<path d="M{fx+6},{fy} C{fx+34},{fy-10} {fx+58},{fy-5} {fx+72},{fy} L{fx+72},{cy2} C{fx+58},{cy2-5} {fx+34},{cy2-10} {fx+6},{cy2} z" fill="{blue}"/>')
        for r in range(3):
            for k in range(4):
                out.append(f'<circle cx="{fx+17+k*15}" cy="{fy+10+r*14}" r="3" fill="#fff"/>')
        out.append(f'<path d="M{fx+6},{fy} C{fx+60},{fy-18} {fx+120},{fy+18} {fx+6+fw},{fy} L{fx+6+fw},{fy+fh} '
                   f'C{fx+120},{fy+fh+18} {fx+60},{fy+fh-18} {fx+6},{fy+fh} z" fill="none" stroke="{ink}" stroke-width="6" stroke-linejoin="round"/>')
    else:
        out.append(f'<rect x="{bx0-14}" y="{by0-14}" width="{bw+28}" height="22" rx="8" fill="{c["red"]}" stroke="{ink}" stroke-width="6"/>')
        for k in range(5):  # estrellas sobre el cartel
            sx = bx0 + 40 + k * (bw - 80) / 4
            out.append(f'<path transform="translate({sx},{by0-3}) scale(.55)" d="M0,-18 L5,-6 18,-6 8,2 12,15 0,7 -12,15 -8,2 -18,-6 -5,-6 z" fill="#fff"/>')
    for (r1, c1, r2, c2) in words["found"]:
        out.append(f'<line x1="{gx+c1*cell+cell/2}" y1="{gy+r1*cell+cell/2}" x2="{gx+c2*cell+cell/2}" '
                   f'y2="{gy+r2*cell+cell/2}" stroke="{c["highlight"]}" stroke-width="34" stroke-linecap="round"/>')
    for r, row in enumerate(rows):
        for k, ch in enumerate(row):
            out.append(f'<text x="{gx+k*cell+cell/2}" y="{gy+r*cell+cell/2+11}" text-anchor="middle" '
                       f'font-family="Fredoka" font-weight="700" font-size="31" fill="{ink}">{ch}</text>')
    # auto clásico (convertible) delante, a la izquierda
    ax, ay = bx0 + 40, by0 + bh + 118
    body = c.get("car", c["red"])
    out.append(f'''
    <g transform="translate({ax},{ay})">
      <path d="M-10,0 C-10,-38 20,-44 60,-46 L110,-78 C120,-84 170,-84 185,-74 L220,-46 C265,-44 290,-36 292,0 z"
            fill="{body}" stroke="{ink}" stroke-width="7" stroke-linejoin="round"/>
      <path d="M118,-72 L175,-72 L200,-48 L100,-48 z" fill="{c.get('glass', '#B3E5FC')}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>
      <rect x="-14" y="-10" width="310" height="16" rx="8" fill="{c.get('chrome', '#ECEFF1')}" stroke="{ink}" stroke-width="5"/>
      <circle cx="55" cy="6" r="30" fill="{ink}"/><circle cx="55" cy="6" r="12" fill="{c.get('chrome', '#ECEFF1')}"/>
      <circle cx="230" cy="6" r="30" fill="{ink}"/><circle cx="230" cy="6" r="12" fill="{c.get('chrome', '#ECEFF1')}"/>
      <circle cx="-4" cy="-26" r="8" fill="{c['yellow']}" stroke="{ink}" stroke-width="4"/>
    </g>''')
    lr, lc = words["lens"]
    lx, ly = gx + lc * cell + cell / 2, gy + lr * cell + cell / 2
    out.append(f'''
    <line x1="{lx+52}" y1="{ly+52}" x2="{lx+120}" y2="{ly+120}" stroke="{ink}" stroke-width="22" stroke-linecap="round"/>
    <circle cx="{lx}" cy="{ly}" r="66" fill="#fff" fill-opacity=".25" stroke="{ink}" stroke-width="11"/>
    <path d="M{lx-40},{ly-22} a48,48 0 0 1 30,-30" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round"/>''')
    return "".join(out)


def giftbox(cx, top, words, c):
    """Regalo navideño: la cara frontal es una sopa de letras; tapa con cinta y moño, árbol y copos."""
    rows = words["grid"]
    nr, nc = len(rows), len(rows[0])
    cell = 42
    gw, gh = nc * cell, nr * cell
    gx, gy = cx - gw / 2, top + 120
    ink = c["ink"]
    bx0, by0, bw, bh = gx - 34, gy - 34, gw + 68, gh + 68
    red, gold = c["red"], c["yellow"]
    out = []
    # arbolito a la derecha, detrás
    tx, ty = bx0 + bw + 95, by0 - 40
    for k, (wd, yy) in enumerate([(120, 0), (160, 70), (200, 140)]):
        out.append(f'<path d="M{tx},{ty+yy-60} L{tx+wd/2},{ty+yy+40} L{tx-wd/2},{ty+yy+40} z" fill="{c.get("tree", "#43A047")}" '
                   f'stroke="{ink}" stroke-width="6" stroke-linejoin="round"/>')
    out.append(f'<rect x="{tx-16}" y="{ty+180}" width="32" height="36" fill="{c.get("post", "#8D6E63")}" stroke="{ink}" stroke-width="6"/>')
    out.append(f'<path transform="translate({tx},{ty-70}) scale(1.1)" d="M0,-18 L5,-6 18,-6 8,2 12,15 0,7 -12,15 -8,2 -18,-6 -5,-6 z" fill="{gold}" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>')
    for (ox, oy, col) in [(-30, 20, red), (25, 60, gold), (-45, 120, gold), (40, 140, red), (0, 95, "#fff")]:
        out.append(f'<circle cx="{tx+ox}" cy="{ty+oy}" r="10" fill="{col}" stroke="{ink}" stroke-width="4"/>')
    # caja
    out.append(f'<rect x="{bx0}" y="{by0}" width="{bw}" height="{bh}" rx="12" fill="#fff" stroke="{ink}" stroke-width="9"/>')
    # tapa
    lx0, ly0, lw, lh = bx0 - 22, by0 - 62, bw + 44, 62
    out.append(f'<rect x="{lx0}" y="{ly0}" width="{lw}" height="{lh}" rx="12" fill="{red}" stroke="{ink}" stroke-width="9"/>')
    out.append(f'<rect x="{cx-26}" y="{ly0}" width="52" height="{lh}" fill="{gold}" stroke="{ink}" stroke-width="6"/>')
    # moño
    out.append(f'''
    <path d="M{cx},{ly0+4} C{cx-40},{ly0-70} {cx-120},{ly0-40} {cx-70},{ly0+4} z" fill="{gold}" stroke="{ink}" stroke-width="7" stroke-linejoin="round"/>
    <path d="M{cx},{ly0+4} C{cx+40},{ly0-70} {cx+120},{ly0-40} {cx+70},{ly0+4} z" fill="{gold}" stroke="{ink}" stroke-width="7" stroke-linejoin="round"/>
    <circle cx="{cx}" cy="{ly0}" r="18" fill="{gold}" stroke="{ink}" stroke-width="7"/>''')
    # cinta vertical sólo en los bordes superior/inferior de la cara, para no tapar letras
    out.append(f'<rect x="{cx-26}" y="{by0+4}" width="52" height="26" fill="{gold}"/>'
               f'<rect x="{cx-26}" y="{by0+bh-30}" width="52" height="26" fill="{gold}"/>')
    for (r1, c1, r2, c2) in words["found"]:
        out.append(f'<line x1="{gx+c1*cell+cell/2}" y1="{gy+r1*cell+cell/2}" x2="{gx+c2*cell+cell/2}" '
                   f'y2="{gy+r2*cell+cell/2}" stroke="{c["highlight"]}" stroke-width="34" stroke-linecap="round"/>')
    for r, row in enumerate(rows):
        for k, ch in enumerate(row):
            out.append(f'<text x="{gx+k*cell+cell/2}" y="{gy+r*cell+cell/2+11}" text-anchor="middle" '
                       f'font-family="Fredoka" font-weight="700" font-size="31" fill="{ink}">{ch}</text>')
    out.append(f'<ellipse cx="{cx+60}" cy="{by0+bh+22}" rx="{bw/2+120}" ry="14" fill="#000" opacity=".14"/>')
    # copos de nieve
    for (sx, sy, sc) in [(bx0 - 70, by0 - 120, 1.2), (bx0 - 110, by0 + 90, 0.9), (bx0 + bw + 20, by0 + bh - 10, 0.8)]:
        out.append(f'<g transform="translate({sx},{sy}) scale({sc})" stroke="#fff" stroke-width="6" stroke-linecap="round">'
                   '<path d="M0,-24 V24 M-21,-12 L21,12 M-21,12 L21,-12"/></g>')
    lr, lc = words["lens"]
    lx, ly = gx + lc * cell + cell / 2, gy + lr * cell + cell / 2
    out.append(f'''
    <line x1="{lx+52}" y1="{ly+52}" x2="{lx+120}" y2="{ly+120}" stroke="{ink}" stroke-width="22" stroke-linecap="round"/>
    <circle cx="{lx}" cy="{ly}" r="66" fill="#fff" fill-opacity=".25" stroke="{ink}" stroke-width="11"/>
    <path d="M{lx-40},{ly-22} a48,48 0 0 1 30,-30" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round"/>''')
    return "".join(out)


def retrotv(cx, top, words, c):
    """Televisor antiguo de madera: la pantalla es una sopa de letras; antena de conejo y un disco de vinilo."""
    rows = words["grid"]
    nr, nc = len(rows), len(rows[0])
    cell = 42
    gw, gh = nc * cell, nr * cell
    gx, gy = cx - gw / 2 - 30, top + 110
    ink = c["ink"]
    wood = c.get("wood", "#A1662F")
    bx0, by0, bw, bh = gx - 60, gy - 55, gw + 190, gh + 110
    out = []
    # disco de vinilo detrás, a la derecha
    rx, ry = bx0 + bw + 40, by0 + 40
    out.append(f'<circle cx="{rx}" cy="{ry}" r="105" fill="{c.get("vinyl", "#222")}" stroke="{ink}" stroke-width="6"/>')
    for rr in (85, 68, 52):
        out.append(f'<circle cx="{rx}" cy="{ry}" r="{rr}" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="3"/>')
    out.append(f'<circle cx="{rx}" cy="{ry}" r="34" fill="{c["red"]}" stroke="{ink}" stroke-width="4"/><circle cx="{rx}" cy="{ry}" r="6" fill="#fff"/>')
    # antena
    out.append(f'<path d="M{cx-10},{by0} L{cx-90},{by0-120} M{cx+10},{by0} L{cx+100},{by0-110}" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>')
    out.append(f'<circle cx="{cx-90}" cy="{by0-120}" r="10" fill="{c["yellow"]}" stroke="{ink}" stroke-width="4"/>'
               f'<circle cx="{cx+100}" cy="{by0-110}" r="10" fill="{c["yellow"]}" stroke="{ink}" stroke-width="4"/>')
    out.append(f'<ellipse cx="{cx}" cy="{by0}" rx="46" ry="18" fill="{wood}" stroke="{ink}" stroke-width="6"/>')
    # gabinete y patas
    for lx in (bx0 + 50, bx0 + bw - 50):
        out.append(f'<path d="M{lx-8},{by0+bh-4} L{lx-18},{by0+bh+46} M{lx+8},{by0+bh-4} L{lx+18},{by0+bh+46}" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>')
    out.append(f'<rect x="{bx0}" y="{by0}" width="{bw}" height="{bh}" rx="26" fill="{wood}" stroke="{ink}" stroke-width="9"/>')
    # pantalla redondeada
    out.append(f'<rect x="{gx-24}" y="{gy-24}" width="{gw+48}" height="{gh+48}" rx="34" fill="#fff" stroke="{ink}" stroke-width="8"/>')
    # perillas y parlante a la derecha
    kx = gx + gw + 70
    for ky in (gy + 20, gy + 85):
        out.append(f'<circle cx="{kx}" cy="{ky}" r="22" fill="{c.get("knob", "#F5E6C8")}" stroke="{ink}" stroke-width="6"/>'
                   f'<line x1="{kx}" y1="{ky}" x2="{kx+12}" y2="{ky-12}" stroke="{ink}" stroke-width="5" stroke-linecap="round"/>')
    for k in range(4):
        out.append(f'<line x1="{kx-26}" y1="{gy+130+k*14}" x2="{kx+26}" y2="{gy+130+k*14}" stroke="{ink}" stroke-width="5" stroke-linecap="round"/>')
    for (r1, c1, r2, c2) in words["found"]:
        out.append(f'<line x1="{gx+c1*cell+cell/2}" y1="{gy+r1*cell+cell/2}" x2="{gx+c2*cell+cell/2}" '
                   f'y2="{gy+r2*cell+cell/2}" stroke="{c["highlight"]}" stroke-width="34" stroke-linecap="round"/>')
    for r, row in enumerate(rows):
        for k, ch in enumerate(row):
            out.append(f'<text x="{gx+k*cell+cell/2}" y="{gy+r*cell+cell/2+11}" text-anchor="middle" '
                       f'font-family="Fredoka" font-weight="700" font-size="31" fill="{ink}">{ch}</text>')
    out.append(f'<ellipse cx="{cx}" cy="{by0+bh+52}" rx="{bw/2+60}" ry="13" fill="#000" opacity=".14"/>')
    lr, lc = words["lens"]
    lx, ly = gx + lc * cell + cell / 2, gy + lr * cell + cell / 2
    out.append(f'''
    <line x1="{lx+52}" y1="{ly+52}" x2="{lx+120}" y2="{ly+120}" stroke="{ink}" stroke-width="22" stroke-linecap="round"/>
    <circle cx="{lx}" cy="{ly}" r="66" fill="#fff" fill-opacity=".25" stroke="{ink}" stroke-width="11"/>
    <path d="M{lx-40},{ly-22} a48,48 0 0 1 30,-30" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round"/>''')
    return "".join(out)


STYLES = {"bold": front_bold, "grid": front_grid}


def back_bold(x0, y0, w, h, cv, c):
    """Contraportada del estilo bold. Zona de código de barras (abajo a la derecha, junto al lomo) libre."""
    from portada import BLEED, U, sample
    blue, navy, deep = bold_palette(cv)
    left = x0 + BLEED * U + 45
    width = w - BLEED * U - 90
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{blue}"/>',
           letter_texture(x0, y0, w, h, "#FFFFFF", 0.11, seed=82),  # antes 11: formaba SLUT/COCK/JEW; 82 verificada limpia
           big_title(left + width / 2, y0 + 118, cv["back_headline"].upper(), 44, width - 10, c["yellow"], deep, navy),
           f'<rect x="{left}" y="{y0+150}" width="{width}" height="418" rx="24" fill="#fff" stroke="{navy}" stroke-width="6"/>',
           f'<foreignObject x="{left+28}" y="{y0+170}" width="{width-56}" height="390">'
           f'<div xmlns="http://www.w3.org/1999/xhtml" class="backtext">'
           + "".join(f"<p>{p}</p>" for p in cv["back_intro"])
           + "<ul>" + "".join(f"<li>{b}</li>" for b in cv["back_bullets"]) + "</ul>"
           + f'<p class="close">{cv["back_close"]}</p></div></foreignObject>',
           f'<rect x="{x0}" y="{y0+h-190}" width="{w}" height="190" fill="{c["red"]}"/>',
           f'<rect x="{x0}" y="{y0+h-190}" width="{w}" height="8" fill="{navy}"/>',
           sample(left + 15, y0 + 600, cv, dict(c, ink=navy))]
    return "".join(out)


def spine_bold(x0, y0, sw, h, cv, c):
    blue, navy, deep = bold_palette(cv)
    cx, cy = x0 + sw / 2, y0 + h / 2
    size = max(8, min(15, sw - 2 * 6.25 - 2))
    return (f'<rect x="{x0}" y="{y0}" width="{sw}" height="{h}" fill="{blue}"/>'
            f'<rect x="{x0}" y="{y0+h-190}" width="{sw}" height="190" fill="{c["red"]}"/>'
            f'<rect x="{x0}" y="{y0+h-190}" width="{sw}" height="8" fill="{navy}"/>'
            f'<text x="{cx}" y="{cy-40}" transform="rotate(90 {cx} {cy-40})" text-anchor="middle" dominant-baseline="central" '
            f'font-family="Luckiest Guy" font-size="{size:.1f}" fill="#fff" letter-spacing="1">{esc(cv["spine"])}</text>')


BACKS = {"bold": (back_bold, spine_bold)}

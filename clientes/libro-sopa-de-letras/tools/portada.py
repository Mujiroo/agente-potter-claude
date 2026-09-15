#!/usr/bin/env python3
"""Portada completa KDP (contraportada + lomo + portada) para la serie "___ HUNT!".

Plantilla de serie: la estructura (toldo de supermercado, título, etiqueta de precio con el
nombre del libro, sello LARGE PRINT, carro cuya canasta es una sopa de letras, franja inferior)
queda fija; cada libro cambia textos, palabras del carro y colores en el JSON "cover".

Todo es vectorial y hecho a mano (sin imágenes de IA ni de stock): fuentes Luckiest Guy
(Apache 2.0) y Fredoka (OFL), ambas de uso comercial libre.

Uso: portada.py libro.json salida.html [--front-only] [--white]
  --front-only : solo la portada 6x9 con sangrado (preview / página 1)
  --white      : fondo blanco (para la página 1 del interior)
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BLEED = 0.125
PAPER = {"white": 0.002252, "cream": 0.0025}  # pulgadas por página (KDP)
U = 100  # unidades SVG por pulgada


def esc(s):
    return html.escape(s, quote=True)


def awning(x0, width, y0, colors, n):
    """Toldo a rayas con borde festoneado."""
    w = width / n
    out = []
    for i in range(n):
        c = colors[i % 2]
        x = x0 + i * w
        out.append(f'<path d="M{x},{y0} h{w} v70 a{w/2},{w/2*0.55} 0 0 1 {-w},0 z" fill="{c}"/>')
    return "".join(out)


def cart(cx, top, words, c):
    """Carro de supermercado: la canasta es una grilla de letras con palabras marcadas."""
    rows = words["grid"]
    nr, nc = len(rows), len(rows[0])
    cell = 42
    gw, gh = nc * cell, nr * cell
    gx, gy = cx - gw / 2, top + 70
    out = []
    # mercadería asomando por arriba (dibujada antes que la canasta)
    out.append(f'''
    <g transform="translate({gx+40},{gy-10}) rotate(-18)">
      <rect x="0" y="-150" width="46" height="170" rx="23" fill="#E9B872" stroke="{c['ink']}" stroke-width="5"/>
      <path d="M8,-120 l30,-14 M8,-85 l30,-14 M8,-50 l30,-14" stroke="{c['ink']}" stroke-width="4" stroke-linecap="round"/>
    </g>
    <g transform="translate({gx+125},{gy-5})">
      <path d="M0,0 v-120 l25,-30 l25,30 v120 z" fill="#fff" stroke="{c['ink']}" stroke-width="5" stroke-linejoin="round"/>
      <rect x="0" y="-95" width="50" height="45" fill="{c['accent']}"/>
      <text x="25" y="-64" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="20" fill="#fff">MILK</text>
    </g>
    <g transform="translate({gx+gw-150},{gy-8}) rotate(20)">
      <path d="M0,0 C-10,-80 40,-140 110,-150 C70,-120 40,-70 45,0 z" fill="{c['yellow']}" stroke="{c['ink']}" stroke-width="5" stroke-linejoin="round"/>
    </g>
    <g transform="translate({gx+gw-55},{gy-75}) rotate(22)">
      <path d="M0,0 c-20,-20 -30,-35 -25,-55 M0,0 c0,-25 0,-40 5,-58 M0,0 c20,-18 32,-30 30,-50" stroke="#3FA34D" stroke-width="9" fill="none" stroke-linecap="round"/>
      <path d="M-24,0 L24,0 L0,130 z" fill="#F4843C" stroke="{c['ink']}" stroke-width="5" stroke-linejoin="round"/>
      <path d="M-12,30 h14 M-6,60 h12" stroke="{c['ink']}" stroke-width="4" stroke-linecap="round"/>
    </g>
    <g transform="translate({gx+gw/2+20},{gy-40})">
      <circle r="44" fill="{c['red']}" stroke="{c['ink']}" stroke-width="5"/>
      <path d="M0,-44 c0,-18 6,-26 14,-30" stroke="{c['ink']}" stroke-width="6" fill="none" stroke-linecap="round"/>
      <path d="M8,-60 c18,-14 38,-10 44,-2 c-16,12 -34,12 -44,2 z" fill="#3FA34D" stroke="{c['ink']}" stroke-width="4"/>
      <ellipse cx="-16" cy="-14" rx="9" ry="14" fill="#fff" opacity=".45"/>
    </g>''')
    # canasta (trapecio) con la grilla
    out.append(f'<path d="M{gx-40},{gy-18} H{gx+gw+40} L{gx+gw+10},{gy+gh+22} H{gx-10} z" '
               f'fill="#fff" stroke="{c["ink"]}" stroke-width="9" stroke-linejoin="round"/>')
    for (r1, c1, r2, c2) in words["found"]:
        out.append(f'<line x1="{gx+c1*cell+cell/2}" y1="{gy+r1*cell+cell/2}" x2="{gx+c2*cell+cell/2}" '
                   f'y2="{gy+r2*cell+cell/2}" stroke="{c["highlight"]}" stroke-width="34" stroke-linecap="round"/>')
    for r, row in enumerate(rows):
        for k, ch in enumerate(row):
            out.append(f'<text x="{gx+k*cell+cell/2}" y="{gy+r*cell+cell/2+11}" text-anchor="middle" '
                       f'font-family="Fredoka" font-weight="700" font-size="31" fill="{c["ink"]}">{ch}</text>')
    # manija, bastidor y ruedas
    out.append(f'''
    <path d="M{gx+gw+40},{gy-18} L{gx+gw+75},{gy-70} H{gx+gw+120}" stroke="{c['ink']}" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M{gx-10},{gy+gh+22} L{gx+10},{gy+gh+70} H{gx+gw-10}" stroke="{c['ink']}" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <ellipse cx="{cx}" cy="{gy+gh+118}" rx="{gw/2+40}" ry="14" fill="#000" opacity=".12"/>
    <circle cx="{gx+40}" cy="{gy+gh+95}" r="20" fill="{c['ink']}"/><circle cx="{gx+40}" cy="{gy+gh+95}" r="7" fill="#fff"/>
    <circle cx="{gx+gw-40}" cy="{gy+gh+95}" r="20" fill="{c['ink']}"/><circle cx="{gx+gw-40}" cy="{gy+gh+95}" r="7" fill="#fff"/>''')
    # lupa sobre una palabra encontrada
    lr, lc = words["lens"]
    lx, ly = gx + lc * cell + cell / 2, gy + lr * cell + cell / 2
    out.append(f'''
    <line x1="{lx+52}" y1="{ly+52}" x2="{lx+120}" y2="{ly+120}" stroke="{c['ink']}" stroke-width="22" stroke-linecap="round"/>
    <circle cx="{lx}" cy="{ly}" r="66" fill="#fff" fill-opacity=".25" stroke="{c['ink']}" stroke-width="11"/>
    <path d="M{lx-40},{ly-22} a48,48 0 0 1 30,-30" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round"/>''')
    return "".join(out)


def front(x0, y0, w, h, cv, c, white=False, cx=None):
    """Portada. x0,y0 = esquina del área con sangrado; cx = centro del área de corte."""
    cx = x0 + w / 2 if cx is None else cx
    bg = "#FFFFFF" if white else c["bg"]
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{bg}"/>']
    # baldosas del piso del supermercado
    if not white:
        out.append(floor(x0, y0, w, h, c))
    out.append(awning(x0, w, y0, [c["red"], "#FFFFFF"], 10))
    # título
    ty = y0 + 12.5 + 190
    out.append(f'<text x="{cx}" y="{ty}" text-anchor="middle" font-family="Luckiest Guy" font-size="96" '
               f'textLength="{w-110}" lengthAdjust="spacingAndGlyphs" fill="{c["ink"]}" stroke="{c["ink"]}" '
               f'stroke-width="18" stroke-linejoin="round" transform="translate(5,7)">{esc(cv["title"])}</text>')
    out.append(f'<text x="{cx}" y="{ty}" text-anchor="middle" font-family="Luckiest Guy" font-size="96" '
               f'textLength="{w-110}" lengthAdjust="spacingAndGlyphs" fill="#fff" stroke="#fff" stroke-width="18" '
               f'stroke-linejoin="round">{esc(cv["title"])}</text>')
    out.append(f'<text x="{cx}" y="{ty}" text-anchor="middle" font-family="Luckiest Guy" font-size="96" '
               f'textLength="{w-110}" lengthAdjust="spacingAndGlyphs" fill="{c["ink"]}">{esc(cv["title"])}</text>')
    # etiqueta de precio con el nombre del libro
    out.append(f'''
    <g transform="translate({cx-18},{ty+85}) rotate(-4)">
      <path d="M-215,-52 H185 L230,0 L185,52 H-215 a14,14 0 0 1 -14,-14 V-38 a14,14 0 0 1 14,-14 z" fill="{c['yellow']}" stroke="{c['ink']}" stroke-width="7" stroke-linejoin="round"/>
      <circle cx="195" cy="0" r="11" fill="{bg}" stroke="{c['ink']}" stroke-width="5"/>
      <text x="-12" y="24" text-anchor="middle" font-family="Luckiest Guy" font-size="66" fill="{c['red']}">{esc(cv['series_name'])}</text>
    </g>
    <g transform="translate({cx+175},{ty+150}) rotate(-4)">
      <rect x="-48" y="-20" width="96" height="40" rx="20" fill="{c['ink']}"/>
      <text x="0" y="10" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="25" fill="#fff">{esc(cv['volume'])}</text>
    </g>''')
    out.append(cart(cx - 45, ty + 205, cv["cart"], c))
    # sello LARGE PRINT
    bx, by = cx - 205, y0 + 385
    pts = []
    import math
    for k in range(32):
        rr = 70 if k % 2 == 0 else 61
        a = math.pi * k / 16
        pts.append(f"{bx+rr*math.cos(a):.1f},{by+rr*math.sin(a):.1f}")
    out.append(f'''
    <g transform="rotate(-12 {bx} {by})">
      <polygon points="{' '.join(pts)}" fill="{c['red']}" stroke="{c['ink']}" stroke-width="6" stroke-linejoin="round"/>
      <text x="{bx}" y="{by-6}" text-anchor="middle" font-family="Luckiest Guy" font-size="29" fill="#fff">LARGE</text>
      <text x="{bx}" y="{by+25}" text-anchor="middle" font-family="Luckiest Guy" font-size="29" fill="#fff">PRINT</text>
    </g>''')
    # franja inferior
    out.append(f'''
    <rect x="{x0+45}" y="{y0+h-125}" width="{w-90}" height="82" rx="41" fill="{c['ink']}"/>
    <text x="{cx}" y="{y0+h-86}" text-anchor="middle" font-family="Luckiest Guy" font-size="28" textLength="{w-170}" lengthAdjust="spacingAndGlyphs" fill="#fff">{esc(cv['band1'])}</text>
    <text x="{cx}" y="{y0+h-56}" text-anchor="middle" font-family="Fredoka" font-weight="600" font-size="21" fill="{c['yellow']}">{esc(cv['band2'])}</text>''')
    return "".join(out)


def floor(x0, y0, w, h, c, phase=0):
    tile = 50
    fy = y0 + h - 150
    out = []
    for i in range(int(w // tile) + 1):
        for j in range(4):
            if (i + j + phase) % 2 == 0:
                out.append(f'<rect x="{x0+i*tile}" y="{fy+j*tile}" width="{tile}" height="{tile}" fill="{c["tile"]}"/>')
    return "".join(out)


def sample(x, y, cv, c):
    """Miniatura de una página de puzzle (decorativa)."""
    rows = cv["sample"]["grid"]
    cell = 21
    n = len(rows)
    out = [f'<g transform="translate({x},{y}) rotate(-6)">',
           f'<rect x="-8" y="-8" width="{n*cell+46}" height="{n*cell+84}" rx="10" fill="#000" opacity=".12"/>',
           f'<rect x="-14" y="-14" width="{n*cell+46}" height="{n*cell+84}" rx="10" fill="#fff" stroke="{c["ink"]}" stroke-width="4"/>',
           f'<text x="{n*cell/2+9}" y="14" text-anchor="middle" font-family="Luckiest Guy" font-size="20" fill="{c["ink"]}">{esc(cv["sample"]["title"])}</text>']
    gx, gy = 9, 30
    out.append(f'<rect x="{gx-4}" y="{gy-4}" width="{n*cell+8}" height="{n*cell+8}" rx="6" fill="none" stroke="{c["ink"]}" stroke-width="2.5"/>')
    for (r1, c1, r2, c2) in cv["sample"]["found"]:
        out.append(f'<line x1="{gx+c1*cell+cell/2}" y1="{gy+r1*cell+cell/2}" x2="{gx+c2*cell+cell/2}" y2="{gy+r2*cell+cell/2}" '
                   f'stroke="{c["highlight"]}" stroke-width="17" stroke-linecap="round"/>')
    for r, row in enumerate(rows):
        for k, ch in enumerate(row):
            out.append(f'<text x="{gx+k*cell+cell/2}" y="{gy+r*cell+cell/2+7}" text-anchor="middle" font-family="Fredoka" '
                       f'font-weight="700" font-size="16" fill="{c["ink"]}">{ch}</text>')
    out.append(f'<text x="{n*cell/2+9}" y="{gy+n*cell+26}" text-anchor="middle" font-family="Fredoka" font-weight="600" '
               f'font-size="11" textLength="{n*cell+10}" lengthAdjust="spacingAndGlyphs" fill="{c["ink"]}">{esc(cv["sample"]["words"])}</text></g>')
    return "".join(out)


def back(x0, y0, w, h, cv, c):
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{c["bg"]}"/>', floor(x0, y0, w, h, c, 1),
           awning(x0, w, y0, ["#FFFFFF", c["red"]], 10)]
    left = x0 + BLEED * U + 45
    width = w - BLEED * U - 90
    y = y0 + 190
    out.append(f'<text x="{left+width/2}" y="{y}" text-anchor="middle" font-family="Luckiest Guy" font-size="40" '
               f'textLength="{width-20}" lengthAdjust="spacingAndGlyphs" fill="{c["red"]}">{esc(cv["back_headline"].upper())}</text>')
    y += 30
    out.append(f'<rect x="{left}" y="{y}" width="{width}" height="425" rx="26" fill="#fff" stroke="{c["ink"]}" stroke-width="5"/>')
    body = f'<foreignObject x="{left+30}" y="{y+22}" width="{width-60}" height="395"><div xmlns="http://www.w3.org/1999/xhtml" class="backtext">'
    body += "".join(f"<p>{p}</p>" for p in cv["back_intro"])
    body += "<ul>" + "".join(f"<li>{b}</li>" for b in cv["back_bullets"]) + "</ul>"
    body += f'<p class="close">{cv["back_close"]}</p></div></foreignObject>'
    out.append(body)
    # zona del código de barras (KDP la usa: abajo a la derecha, junto al lomo) — se deja vacía
    out.append(sample(left + 20, y + 458, cv, c))
    # zona del código de barras (KDP la pone abajo a la derecha, junto al lomo): se deja libre
    return "".join(out)


def spine(x0, y0, sw, h, cv, c):
    cx = x0 + sw / 2
    cy = y0 + h / 2
    size = max(8, min(15, sw - 2 * 6.25 - 2))
    return (f'<rect x="{x0}" y="{y0}" width="{sw}" height="{h}" fill="{c["bg"]}"/>'
            f'<text x="{cx}" y="{cy}" transform="rotate(90 {cx} {cy})" text-anchor="middle" dominant-baseline="central" '
            f'font-family="Luckiest Guy" font-size="{size:.1f}" fill="{c["ink"]}" letter-spacing="1">'
            f'{esc(cv["spine"])}</text>')


def front_svg_white(book):
    """Portada sobre fondo blanco, recortada al área de corte (página 1 del interior)."""
    cv, c = book["cover"], book["cover"]["colors"]
    tw, th = book["trim"]
    W, H = (tw + 2 * BLEED) * U, (th + 2 * BLEED) * U
    b = BLEED * U
    return (f'<svg class="cover1" xmlns="http://www.w3.org/2000/svg" viewBox="{b} {b} {tw*U} {th*U}">'
            f'{front(0, 0, W, H, cv, c, white=True)}</svg>')


def font_css():
    fonts = os.path.join(HERE, "fonts")
    return (f"@font-face {{ font-family: 'Luckiest Guy'; src: url('file://{fonts}/LuckiestGuy-Regular.ttf'); }}\n"
            f"@font-face {{ font-family: 'Fredoka'; src: url('file://{fonts}/Fredoka-VF.ttf'); font-weight: 300 700; }}\n")


def main(src, dst, front_only=False, white=False):
    book = json.load(open(src, encoding="utf-8"))
    cv, c = book["cover"], book["cover"]["colors"]
    tw, th = book["trim"]
    pages = cv["page_count"]
    sw = pages * PAPER[cv.get("paper", "white")] * U
    fw, fh = (tw + BLEED) * U, (th + 2 * BLEED) * U  # cada cara incluye sangrado exterior
    if front_only:
        W, H = fw + BLEED * U, fh  # sangrado a ambos lados para preview
        svg = front(0, 0, W, H, cv, c, white)
    else:
        W, H = 2 * fw + sw, fh
        svg = back(0, 0, fw, H, cv, c) + spine(fw, 0, sw, H, cv, c) + front(fw + sw, 0, fw, H, cv, c, cx=fw + sw + tw * U / 2)
    fonts = os.path.join(HERE, "fonts")
    doc = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: 'Luckiest Guy'; src: url('file://{fonts}/LuckiestGuy-Regular.ttf'); }}
@font-face {{ font-family: 'Fredoka'; src: url('file://{fonts}/Fredoka-VF.ttf'); font-weight: 300 700; }}
@page {{ size: {W/U:.4f}in {H/U:.4f}in; margin: 0; }}
html, body {{ margin: 0; padding: 0; }}
svg {{ display: block; width: {W/U:.4f}in; height: {H/U:.4f}in; }}
.backtext {{ font-family: 'Fredoka', sans-serif; font-size: 19px; line-height: 1.38; color: {c['ink']}; }}
.backtext p {{ margin: 0 0 10px; }}
.backtext ul {{ margin: 6px 0 12px; padding: 0; list-style: none; }}
.backtext li {{ margin-bottom: 5px; padding-left: 26px; position: relative; }}
.backtext li::before {{ content: ""; position: absolute; left: 2px; top: 7px; width: 12px; height: 12px; border-radius: 50%; background: {c['red']}; }}
.backtext .close {{ font-weight: 600; margin-top: 8px; }}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}">{svg}</svg>
</body></html>'''
    open(dst, "w", encoding="utf-8").write(doc)
    print(f"{W/U:.3f} x {H/U:.3f} in (lomo {sw/U:.4f} in) -> {dst}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0], args[1], "--front-only" in sys.argv, "--white" in sys.argv)

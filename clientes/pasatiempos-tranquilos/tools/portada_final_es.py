#!/usr/bin/env python3
"""Portada completa KDP (contratapa + lomo + frente) de «Pasatiempos Tranquilos».

Frente elegido por Pedro (17-sep, msg 845): diseño 1 «Rojo 3 en 1» de portadas_v2.py.
La contratapa sigue el mismo sistema: rojo con textura de letras, panel blanco, banda amarilla.
Deja libre el recuadro del código de barras (2 × 1,2" abajo a la derecha, lo pone KDP).

Uso: portada_final_es.py libro.json salida.html
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "calm-cozy", "tools"))

from portada_cozy import BLEED, PAPER, U, font_css, letter_texture  # noqa: E402
import portadas_v2 as V2  # noqa: E402

ROJO, OSC, AM, AZUL = "#C62828", "#7F1414", "#FFD54F", "#1E3A8A"
# Tipografía E elegida por Pedro (17-sep, msg 874): Archivo Black + Bree Serif + Caveat
FONTS = dict(next(k for n, _l, k in V2.TIPOS if n == "T5-archivo"))
SERIF, SANS, SCRIPT = FONTS["sub"], FONTS["bold"], FONTS["script"]
BARCODE = (2.0 * U, 1.2 * U)  # ancho, alto
BARCODE_MARGIN = 0.25 * U     # desde el corte inferior y desde el lomo


def esc(s):
    return html.escape(s, quote=True)


def texture(x0, y0, w, h, seed=28):
    return (f'<svg x="{x0}" y="{y0}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" overflow="hidden">'
            f'{letter_texture(0, 0, w, h, "#FFFFFF", 0.10, cell=50, size=28, seed=seed)}</svg>')


def front(x0, w, H):
    """El diseño 1 tal cual (mide W = 8,75" con sangrado); si w es mayor, se extiende el fondo por el borde exterior."""
    return (f'<rect x="{x0}" y="0" width="{w}" height="{H}" fill="{ROJO}"/>'
            f'<g transform="translate({x0} 0)">{V2.p1(fonts=FONTS)}</g>'
            f'<rect x="{x0 + V2.W - 1}" y="{H-215}" width="{w - V2.W + 1}" height="130" fill="{AM}"/>'
            if w > V2.W else f'<g transform="translate({x0} 0)">{V2.p1(fonts=FONTS)}</g>')


def back(x0, w, H, cv, trim_right):
    b = BLEED * U
    left = x0 + b + 55
    width = trim_right - left - 55
    cx = left + width / 2
    bx, by = trim_right - BARCODE_MARGIN - BARCODE[0], H - b - BARCODE_MARGIN - BARCODE[1]
    out = [f'<rect x="{x0}" y="0" width="{w}" height="{H}" fill="{ROJO}"/>', texture(x0, 0, w, H, seed=28),
           f'<text x="{cx}" y="{b+120}" text-anchor="middle" font-family="{SCRIPT}" font-size="70" fill="{AM}">{esc(cv["back_headline"])}</text>',
           f'<rect x="{left}" y="{b+160}" width="{width}" height="560" rx="24" fill="#FFFFFF"/>',
           f'<foreignObject x="{left+34}" y="{b+186}" width="{width-68}" height="512">'
           f'<div xmlns="http://www.w3.org/1999/xhtml" class="backtext">'
           + "".join(f"<p>{p}</p>" for p in cv["back_intro"])
           + "<ul>" + "".join(f"<li>{x}</li>" for x in cv["back_bullets"]) + "</ul>"
           + f'<p class="close">{cv["back_close"]}</p></div></foreignObject>',
           f'<rect x="{x0}" y="{b+760}" width="{w}" height="96" fill="{AM}"/>',
           f'<text x="{cx}" y="{b+826}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="54" letter-spacing="3" fill="{ROJO}">LETRA GRANDE</text>',
           f'<text x="{left}" y="{by+50}" font-family="{SCRIPT}" font-size="46" fill="{AM}">{esc(cv["series_line"])}</text>',
           f'<text x="{left}" y="{by+92}" font-family="{SERIF}" font-size="22" letter-spacing="5" fill="#FFFFFF">{esc(cv["author"].upper())}</text>',
           # recuadro reservado al código de barras (KDP lo imprime en blanco encima)
           f'<rect id="barcode" x="{bx}" y="{by}" width="{BARCODE[0]}" height="{BARCODE[1]}" fill="#FFFFFF" opacity="0"/>']
    return "".join(out)


def spine(x0, sw, H, cv):
    cx, cy = x0 + sw / 2, H / 2
    size = max(9, min(16, sw - 2 * 6.25 - 6))
    return (f'<rect x="{x0}" y="0" width="{sw}" height="{H}" fill="{OSC}"/>'
            f'<text x="{cx}" y="{cy}" transform="rotate(90 {cx} {cy})" text-anchor="middle" dominant-baseline="central" '
            f'font-family="{SANS}" font-weight="700" font-size="{size:.1f}" letter-spacing="1" fill="#FFFFFF">{esc(cv["spine"])}</text>')


def main(src, dst):
    book = json.load(open(src, encoding="utf-8"))
    cv = book["cover_full"]
    tw, th = book["trim"]
    b = BLEED * U
    sw = cv["page_count"] * PAPER[cv.get("paper", "white")] * U
    H = (th + 2 * BLEED) * U
    EXTRA = 3  # fondo extra por el borde exterior del frente; ajustar_mediabox recorta al ancho exacto
    W = 2 * (tw + BLEED) * U + sw + EXTRA
    fx = b + tw * U + sw
    svg = (back(0, b + tw * U + b, H, cv, trim_right=b + tw * U)
           + front(fx - b, tw * U + 2 * b + EXTRA, H)
           + spine(b + tw * U, sw, H, cv))
    doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Pasatiempos Tranquilos Vol. 1 (portada)</title><style>
{font_css()}{V2.fonts_css()}
@page {{ size: {W/U:.4f}in {H/U:.4f}in; margin: 0; }}
html, body {{ margin: 0; padding: 0; }}
svg {{ display: block; width: {W/U:.4f}in; height: {H/U:.4f}in; }}
.backtext {{ font-family: 'Bree Serif', Georgia, serif; font-size: 25px; line-height: 1.38; color: #1B1B1B; }}
.backtext p {{ margin: 0 0 12px; }}
.backtext ul {{ margin: 6px 0 10px; padding: 0; list-style: none; }}
.backtext li {{ margin-bottom: 6px; padding-left: 30px; position: relative; }}
.backtext li::before {{ content: ""; position: absolute; left: 3px; top: 10px; width: 13px; height: 13px; border-radius: 50%; background: {ROJO}; }}
.backtext b {{ color: {OSC}; }}
.backtext .close {{ font-weight: 700; margin-top: 10px; color: {OSC}; }}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" data-spine="{sw/U:.4f}" data-trim-w="{(W-EXTRA)/U:.4f}" viewBox="0 0 {W:.2f} {H:.2f}">{svg}</svg>
</body></html>'''
    open(dst, "w", encoding="utf-8").write(doc)
    print(f"{(W-EXTRA)/U:.4f} x {H/U:.4f} in (lomo {sw/U:.4f} in) -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

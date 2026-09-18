#!/usr/bin/env python3
"""Variantes sutiles del FONDO de la portada 1 «Rojo 3 en 1» (Pedro, 18-sep, msg 941:
«más rojos, distintos brillos, algo sutil pero que me diferencie»). Todo vectorial
(degradados SVG, sin filtros ni blur) para que el PDF de KDP siga sin rasterizar.

Uso: fondos_es.py carpeta_salida      → portada_<nombre>.html por variante + hoja.html
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portadas_v2 as V2  # noqa: E402
from portadas_opciones import W, H, page  # noqa: E402
import portada_final_es as PF  # noqa: E402

CX, TY = W / 2, 300  # centro horizontal y altura del título
ROJO, OSC = "#C62828", "#7F1414"


def radial(id_, cx, cy, r, stops):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    return f'<radialGradient id="{id_}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'


def linear(id_, stops, y1=0, y2=H):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    return f'<linearGradient id="{id_}" gradientUnits="userSpaceOnUse" x1="0" y1="{y1}" x2="0" y2="{y2}">{s}</linearGradient>'


def textura(fill, op=1.0):
    """Misma textura de letras verificada (seed 28), con relleno plano o degradado."""
    return V2.tex(fill, op)


def viñeta(k):
    """Centro más luminoso detrás del título, bordes más oscuros."""
    return (f'<defs>{radial(f"vg{k}", CX, TY + 60, 820, [(0, "#DC3B2E", 1), (0.55, ROJO, 1), (1, "#8C1616", 1)])}</defs>'
            f'<rect width="{W}" height="{H}" fill="url(#vg{k})"/>')


def f_actual():
    return f'<rect width="{W}" height="{H}" fill="{ROJO}"/>' + textura("#FFFFFF", 0.10)


def f_vineta():
    """A · Viñeta cálida: luz al centro, bordes carmesí. La misma textura blanca."""
    return viñeta("a") + textura("#FFFFFF", 0.09)


def f_profundo():
    """B · Rojo profundo: degradado vertical, más claro arriba, casi vino abajo; la textura se desvanece hacia abajo."""
    return (f'<defs>{linear("pb", [(0, "#D63A2F", 1), (0.45, ROJO, 1), (1, "#7A1212", 1)])}'
            f'{linear("pt", [(0, "#FFFFFF", 0.15), (0.6, "#FFFFFF", 0.07), (1, "#FFFFFF", 0.03)])}</defs>'
            f'<rect width="{W}" height="{H}" fill="url(#pb)"/>' + textura("url(#pt)"))


def f_rayos():
    """C · Rayos: viñeta + rayos de luz muy suaves que salen detrás del título (estilo afiche clásico)."""
    n, R = 32, 1600
    rays = []
    for i in range(0, n, 2):
        a1, a2 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        rays.append(f'M{CX},{TY} L{CX + R*math.cos(a1):.1f},{TY + R*math.sin(a1):.1f} '
                    f'L{CX + R*math.cos(a2):.1f},{TY + R*math.sin(a2):.1f} Z')
    return (viñeta("c") + f'<defs>{radial("rf", CX, TY, 900, [(0, "#FFFFFF", 0.10), (1, "#FFFFFF", 0.0)])}</defs>'
            f'<path d="{" ".join(rays)}" fill="url(#rf)"/>' + textura("#FFFFFF", 0.07))


def f_tono():
    """D · Tono sobre tono: viñeta + letras en rojo claro en vez de blanco. Más elegante, menos ruido."""
    return viñeta("d") + textura("#F0625A", 0.30)


def f_brillos():
    """E · Brillos: viñeta + halos de luz cálida (naranja y rosa) en esquinas y detrás del título."""
    halos = [("h1", CX, TY, 420, "#FFB74D", 0.22), ("h2", 60, 60, 380, "#FF8A65", 0.20),
             ("h3", W - 40, 700, 360, "#F06292", 0.16), ("h4", 120, H - 260, 340, "#FFB74D", 0.14)]
    defs = "".join(radial(i, x, y, r, [(0, c, a), (1, c, 0)]) for i, x, y, r, c, a in halos)
    return (viñeta("e") + f'<defs>{defs}</defs>'
            + "".join(f'<rect width="{W}" height="{H}" fill="url(#{i})"/>' for i, *_ in halos) + textura("#FFFFFF", 0.09))


FONDOS = [("0-actual", "Actual (plano)", f_actual), ("A-vineta", "A · Viñeta cálida", f_vineta),
          ("B-profundo", "B · Rojo profundo", f_profundo), ("C-rayos", "C · Rayos de luz", f_rayos),
          ("D-tono", "D · Tono sobre tono", f_tono), ("E-brillos", "E · Brillos cálidos", f_brillos)]

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, _l, fn in FONDOS:
        p = os.path.join(out, f"portada_{name}.html")
        open(p, "w", encoding="utf-8").write(
            page(V2.p1(fonts=PF.FONTS, fondo=fn()), name).replace("<style>", "<style>" + V2.fonts_css(), 1))
        print(p)

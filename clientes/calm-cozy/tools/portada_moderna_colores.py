#!/usr/bin/env python3
"""Portada 5 (moderna) en varias paletas, para que Pedro elija el color.

Uso: portada_moderna_colores.py libro.json carpeta_salida
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from portada_cozy import BLEED, U, esc, font_css  # noqa: E402
from portadas_opciones import front_modern  # noqa: E402

PALETAS = {
    "a-petroleo-mostaza": {},  # la original
    "b-marino-coral": {"main": "#1F3A5F", "accent": "#F08A5D", "ink": "#16263D", "highlight": "#F9D3C0"},
    "c-terracota-arena": {"main": "#B4553A", "accent": "#F2C14E", "ink": "#2E1F1A", "highlight": "#F6DDA0"},
    "d-salvia-rosa": {"main": "#5F7D5C", "accent": "#EFA9A0", "ink": "#23312A", "highlight": "#F6D4CF"},
    "e-ciruela-dorado": {"main": "#5A3458", "accent": "#E8B04B", "ink": "#2A1A2A", "highlight": "#F3DCA8"},
    "f-azul-amarillo": {"main": "#3E5C9A", "accent": "#F4D35E", "ink": "#1B2440", "highlight": "#FBEAA8"},
}


def main(src, outdir):
    book = json.load(open(src, encoding="utf-8"))
    cv, c = book["cover"], book["cover"]["colors"]
    tw, th = book["trim"]
    W, H = (tw + 2 * BLEED) * U, (th + 2 * BLEED) * U
    os.makedirs(outdir, exist_ok=True)
    for name, pal in PALETAS.items():
        svg = front_modern(0, 0, W, H, cv, c, pal)
        doc = (f'<!doctype html><html><head><meta charset="utf-8"><title>{esc(cv["title"])} {name}</title><style>'
               f'{font_css()}@page {{ size: {W/U:.4f}in {H/U:.4f}in; margin: 0; }}'
               f'html,body {{ margin:0; padding:0; }} svg {{ display:block; width:{W/U:.4f}in; height:{H/U:.4f}in; }}'
               f'</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}">{svg}</svg></body></html>')
        path = os.path.join(outdir, f"moderna_{name}.html")
        open(path, "w", encoding="utf-8").write(doc)
        print(path)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

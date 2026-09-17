#!/usr/bin/env python3
"""5 portadas nuevas para «Pasatiempos Tranquilos» Vol. 1, diseñadas desde los datos del estudio
(top 10 de «sopa de letras letra grande» en amazon.com, 16-sep-2026):

1 Rojo 3 en 1     ← el n.º 1 (BSR 3.459): rojo, grilla de fondo, título blanco, banda amarilla, número grande
2 Jardín alegre   ← el n.º 2 (BSR 6.194): flores multicolor, grilla verde clara, título blanco con contorno verde
3 Cocina cozy     ← el premium (US$ 13,99, BSR 18k) y «de la Abuela»: crema, acuarela, manuscrita
4 Tablero 70      ← BSR 10.897: azul, amarillo 3D con contorno rojo, número gigante
5 Lotería grande  ← la E que eligió Pedro, con lo aprendido: título más grande, sello 3 EN 1, banda LETRA GRANDE

Uso: portadas_v2.py carpeta_salida
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from portadas_opciones import (W, H, SERIF, SCRIPT, SANS, three_games, papel_picado, jarrito, pan_dulce,  # noqa: E402
                               flor_acuarela, pill, carta, mini_grid, mini_sudoku, mini_maze, page, letter_texture)

CX = W / 2
TEX = dict(cell=50, size=28, seed=28)  # textura verificada sin groserías (ver check_textura)
VOL = "Vol. 1 · Hogar y Sabores"


def tex(color, op):
    return f'<svg x="0" y="0" width="{W}" height="{H}" viewBox="0 0 {W} {H}" overflow="hidden">{letter_texture(0, 0, W, H, color, op, **TEX)}</svg>'


def big(text, y, size, fill, stroke=None, sw=0, family=SANS, tl=None, shadow=None, dx=7):
    tl = f'textLength="{tl}" lengthAdjust="spacingAndGlyphs"' if tl else ""
    out = []
    if shadow:
        out.append(f'<text x="{CX+dx}" y="{y+dx}" text-anchor="middle" font-family="{family}" font-weight="700" font-size="{size}" {tl} '
                   f'fill="{shadow}" stroke="{shadow}" stroke-width="{sw}" stroke-linejoin="round">{text}</text>')
    st = f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" paint-order="stroke"' if stroke else ""
    out.append(f'<text x="{CX}" y="{y}" text-anchor="middle" font-family="{family}" font-weight="700" font-size="{size}" {tl} '
               f'fill="{fill}" {st}>{text}</text>')
    return "".join(out)


def sello(cx, cy, r, fill, ring, l1, l2, c1, c2):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{ring}" stroke-width="6"/>'
            f'<text x="{cx}" y="{cy+8}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="{r*0.56:.0f}" fill="{c1}">{l1}</text>'
            f'<text x="{cx}" y="{cy+r*0.52:.0f}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="{r*0.22:.0f}" fill="{c2}">{l2}</text>')


def t(x, y, s, fill, text, family=SERIF, weight=700, ls=0, anchor="middle"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{family}" font-weight="{weight}" font-size="{s}" '
            f'letter-spacing="{ls}" fill="{fill}">{text}</text>')


# 1 ------------------------------------------------------------------ Rojo 3 en 1
def p1():
    rojo, osc, am, azul = "#C62828", "#7F1414", "#FFD54F", "#1E3A8A"
    return "".join([
        f'<rect width="{W}" height="{H}" fill="{rojo}"/>', tex("#FFFFFF", 0.10),
        t(CX, 72, 24, "#FFFFFF", "PETER &amp; CARDU", ls=6, weight=400),
        t(CX - 70, 158, 72, am, "Pasatiempos Tranquilos", SCRIPT, 400),
        sello(W - 108, 126, 62, am, "#FFFFFF", "3 EN 1", "JUEGOS", rojo, osc),
        big("SOPA DE LETRAS", 300, 124, "#FFFFFF", osc, 12, tl=W - 90),
        t(CX, 368, 58, "#FFFFFF", "SUDOKU · LABERINTOS", ls=3),
        pill(CX, 392, 600, 56, azul, "EN ESPAÑOL · PARA ADULTOS MAYORES", "#FFFFFF", 25),
        f'<rect x="36" y="478" width="{W-72}" height="330" rx="26" fill="#FFFFFF"/>',
        three_games(612, "#222222", am, "#222222"),
        t(CX, 872, 52, "#FFFFFF", VOL),
        f'<rect x="0" y="{H-215}" width="{W}" height="130" fill="{am}"/>',
        t(CX, H - 125, 82, rojo, "LETRA GRANDE", SANS, ls=4),
        t(CX, H - 34, 30, "#FFFFFF", "70 pasatiempos · con soluciones"),
    ])


# 2 ------------------------------------------------------------------ Jardín alegre
def p2():
    verde, fondo, rosa = "#1B5E20", "#E3F2E1", "#D81B60"
    flores = [(55, 55, 80, "#EC407A"), (150, 30, 50, "#FB8C00"), (W - 55, 55, 80, "#42A5F5"), (W - 150, 28, 48, "#FDD835"),
              (55, H - 55, 80, "#FDD835"), (160, H - 25, 50, "#42A5F5"), (W - 55, H - 55, 80, "#FB8C00"), (W - 160, H - 25, 50, "#EC407A")]
    hojas = "".join(f'<ellipse cx="{x}" cy="{y}" rx="40" ry="15" fill="#43A047" transform="rotate({a} {x} {y})"/>'
                    for x, y, a in [(110, 110, 40), (W - 110, 110, -40), (110, H - 110, -40), (W - 110, H - 110, 40)])
    return "".join([
        f'<rect width="{W}" height="{H}" fill="{fondo}"/>', tex("#2E7D32", 0.16), hojas,
        "".join(flor_acuarela(x, y, r, c, op=".95") for x, y, r, c in flores),
        t(CX, 158, 24, verde, "PETER &amp; CARDU", ls=6),
        big("SOPA DE LETRAS", 280, 120, "#FFFFFF", verde, 16, tl=W - 110),
        t(CX, 350, 56, verde, "SUDOKU · LABERINTOS", ls=3),
        pill(CX, 374, 600, 56, rosa, "EN ESPAÑOL · PARA ADULTOS MAYORES", "#FFFFFF", 25),
        t(CX, 498, 76, rosa, "Hogar y Sabores", SCRIPT, 400),
        f'<rect x="38" y="530" width="{W-76}" height="320" rx="26" fill="#FFFFFF" stroke="{verde}" stroke-width="4"/>',
        three_games(662, verde, "#F8BBD0", verde),
        pill(CX, 880, 520, 92, verde, "LETRA GRANDE", "#FFFFFF", 54, SANS, 3),
        t(CX, 1018, 30, verde, "Vol. 1 · 70 pasatiempos · con soluciones"),
    ])


# 3 ------------------------------------------------------------------ Cocina cozy
def p3():
    crema, cafe, terra, verde = "#FBF3E4", "#5A3A22", "#B5542C", "#2F6B4F"
    marco = (f'<rect x="22" y="22" width="{W-44}" height="{H-44}" rx="18" fill="none" stroke="{cafe}" stroke-width="3"/>'
             f'<rect x="34" y="34" width="{W-68}" height="{H-68}" rx="12" fill="none" stroke="{terra}" stroke-width="1.5" stroke-dasharray="8 7"/>')
    ramitas = "".join(flor_acuarela(x, y, r, c) for x, y, r, c in [(95, 100, 55, "#E58FA6"), (W - 95, 100, 55, "#F2B15B"),
                                                                    (72, 432, 30, "#F2B15B"), (W - 72, 432, 30, "#E58FA6")])
    return "".join([
        f'<rect width="{W}" height="{H}" fill="{crema}"/>', marco, ramitas,
        t(CX, 92, 22, cafe, "PETER &amp; CARDU", ls=6, weight=400),
        t(CX, 182, 80, verde, "Pasatiempos Tranquilos", SCRIPT, 400),
        big("SOPA DE LETRAS", 300, 112, cafe, family=SERIF, tl=W - 170),
        t(CX, 364, 50, terra, "SUDOKU · LABERINTOS", ls=4),
        pill(CX, 390, 580, 52, verde, "EN ESPAÑOL · PARA ADULTOS MAYORES", "#FFFFFF", 23),
        f'<rect x="40" y="488" width="{W-80}" height="318" rx="22" fill="#FFFFFF" stroke="{cafe}" stroke-width="3" stroke-dasharray="12 8"/>',
        three_games(615, cafe, "#F6D38A", cafe),
        jarrito(140, 935, 0.66), pan_dulce(W - 145, 955, 0.78),
        pill(CX, 872, 400, 84, terra, "LETRA GRANDE", "#FFFFFF", 44),
        t(CX, 1012, 36, cafe, VOL),
        t(CX, 1058, 24, terra, "70 pasatiempos · con soluciones"),
    ])


# 4 ------------------------------------------------------------------ Tablero 70
def p4():
    azul, osc, am, rojo = "#1565C0", "#0D2A5C", "#FFD600", "#D32F2F"
    s = 62
    tablero = "".join(f'<rect x="{c*s}" y="{r*s}" width="{s}" height="{s}" fill="#0F4FA0"/>'
                      for r in range(int(H // s) + 1) for c in range(int(W // s) + 1) if (r + c) % 2)
    return "".join([
        f'<rect width="{W}" height="{H}" fill="{azul}"/>', tablero,
        t(CX, 70, 22, "#FFFFFF", "PETER &amp; CARDU · PASATIEMPOS TRANQUILOS", ls=3),
        big("SOPA DE LETRAS", 215, 122, am, osc, 10, tl=W - 90, shadow=rojo, dx=8),
        t(CX, 292, 56, "#FFFFFF", "+ SUDOKU + LABERINTOS", SANS, ls=2),
        f'<text x="205" y="560" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="270" fill="{rojo}">70</text>',
        f'<text x="197" y="552" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="270" fill="{am}" stroke="{osc}" stroke-width="8" paint-order="stroke">70</text>',
        t(200, 618, 36, "#FFFFFF", "PASATIEMPOS", SANS, ls=2),
        pill(620, 360, 400, 64, rojo, "PARA ADULTOS", am, 32, SANS, 2),
        pill(620, 440, 400, 64, osc, "EN ESPAÑOL", "#FFFFFF", 32, SANS, 2),
        t(620, 576, 66, am, "Hogar y Sabores", SCRIPT, 400),
        t(620, 618, 26, "#FFFFFF", "Vol. 1 · con soluciones", SERIF),
        f'<rect x="36" y="660" width="{W-72}" height="330" rx="24" fill="#FFFFFF"/>',
        three_games(795, osc, am, osc),
        f'<rect x="0" y="{H-118}" width="{W}" height="118" fill="{rojo}"/>',
        t(CX, H - 38, 74, am, "LETRA GRANDE", SANS, ls=4),
    ])


# 5 ------------------------------------------------------------------ Lotería grande
def p5():
    rojo, verde, am, crema, ink = "#C8102E", "#00845A", "#F4B400", "#FFF6E3", "#1B1B1B"
    cw, ch = 250, 350
    xs = [CX - 1.5 * cw - 16, CX - cw / 2, CX + cw / 2 + 16]
    y0 = 568
    cards = [carta(xs[0], y0, cw, ch, "1", "LA SOPA", color=rojo, contenido=f'<g transform="translate({xs[0]+cw/2-93} {y0+122}) scale(0.78)">{mini_grid(14, 14, ink, "#FBE3A1")}</g>'),
             carta(xs[1], y0 + 14, cw, ch, "2", "EL SUDOKU", color=rojo, contenido=f'<g transform="translate({xs[1]+cw/2-88} {y0+92}) scale(0.78)">{mini_sudoku(0, 0, ink)}</g>'),
             carta(xs[2], y0, cw, ch, "3", "EL LABERINTO", color=rojo, contenido=f'<g transform="translate({xs[2]+cw/2-96} {y0+86}) scale(0.70)">{mini_maze(10, 10, ink, "#FBE3A1")}</g>')]
    return "".join([
        f'<rect width="{W}" height="{H}" fill="{crema}"/>', tex(rojo, 0.06),
        papel_picado(8, [rojo, verde, am, "#1C8C8C", "#D6336C"], h=92),
        t(CX, 166, 22, ink, "PETER &amp; CARDU", ls=6, weight=400),
        big("SOPA DE LETRAS", 282, 126, rojo, ink, 4, tl=W - 90, shadow=am, dx=7),
        t(CX, 350, 56, ink, "SUDOKU · LABERINTOS", ls=3),
        pill(CX - 40, 374, 560, 54, verde, "EN ESPAÑOL · PARA ADULTOS MAYORES", "#FFFFFF", 23),
        t(CX - 80, 500, 68, verde, "Pasatiempos Tranquilos", SCRIPT, 400),
        sello(W - 104, 488, 64, am, rojo, "3 EN 1", "JUEGOS", rojo, ink),
        "".join(cards),
        f'<rect x="0" y="{H-160}" width="{W}" height="160" fill="{rojo}"/>',
        t(CX, H - 84, 72, "#FFFFFF", "LETRA GRANDE", SANS, ls=4),
        t(CX, H - 36, 28, am, "Vol. 1 · Hogar y Sabores · 70 pasatiempos"),
    ])


DISENOS = [("1-rojo-3en1", "Rojo 3 en 1", p1), ("2-jardin-alegre", "Jardín alegre", p2), ("3-cocina-cozy", "Cocina cozy", p3),
           ("4-tablero-70", "Tablero 70", p4), ("5-loteria-grande", "Lotería grande", p5)]


def check_textura():
    """Reconstruye la textura (misma semilla) y busca groserías en 8 direcciones."""
    import random
    from verificar_temas import BAD_ES
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "libro-sopa-de-letras", "tools"))
    from generar import BAD
    rng = random.Random(TEX["seed"])
    rows, cols = int(H // TEX["cell"]) + 1, int(W // TEX["cell"]) + 1
    g = [[rng.choice("ABCDEFGHIJKLMNOPRSTUVWY") for _ in range(cols)] for _ in range(rows)]
    hits = []
    for w in set(BAD + BAD_ES):
        for r in range(rows):
            for c in range(cols):
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    if all(0 <= r + dr * k < rows and 0 <= c + dc * k < cols and g[r + dr * k][c + dc * k] == w[k] for k in range(len(w))):
                        hits.append(w)
    return sorted(set(hits))


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    print("groserías en la textura:", check_textura() or "ninguna")
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, _l, fn in DISENOS:
        p = os.path.join(out, f"portada_{name}.html")
        open(p, "w", encoding="utf-8").write(page(fn(), name))
        print(p)

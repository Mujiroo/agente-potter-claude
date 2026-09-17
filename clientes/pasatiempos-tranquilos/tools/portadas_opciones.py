#!/usr/bin/env python3
"""Tres opciones de portada (frente 8,5x11 con sangrado) para «Pasatiempos Tranquilos».

A cozy latino · B llamativa · C floral suave. Todas llevan lo que repiten los más vendidos
en español (estudio del 16-sep): SOPA DE LETRAS gigante, LETRA GRANDE, EN ESPAÑOL,
número llamativo y grilla visible; y nuestra diferencia: los 3 juegos a la vista.

Uso: portadas_opciones.py carpeta_salida
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.path.join(HERE, "..", "..", "calm-cozy", "tools")
sys.path.insert(0, CC)

from portada_cozy import BLEED, U, font_css, letter_texture  # noqa: E402
import puzzles as PZ  # noqa: E402

W, H = (8.5 + 2 * BLEED) * U, (11 + 2 * BLEED) * U
SERIF = "Playfair Display, serif"
SCRIPT = "Caveat, cursive"
SANS = "Liberation Sans, Arial, sans-serif"

GRID = {"rows": ["CAFEMI", "FLORES", "PANSOL", "TIAMOR"],
        "found": [(0, 0, 0, 3), (1, 0, 1, 5), (2, 0, 2, 2), (2, 3, 2, 5), (3, 2, 3, 5)]}


def mini_grid(x, y, ink, hi, cell=34, font=25, paper="#fff"):
    rows = GRID["rows"]
    out = [f'<rect x="{x-14}" y="{y-14}" width="{6*cell+28}" height="{4*cell+28}" rx="12" fill="{paper}" stroke="{ink}" stroke-width="6"/>']
    for r1, c1, r2, c2 in GRID["found"]:
        out.append(f'<line x1="{x+c1*cell+cell/2}" y1="{y+r1*cell+cell/2}" x2="{x+c2*cell+cell/2}" y2="{y+r2*cell+cell/2}" '
                   f'stroke="{hi}" stroke-width="26" stroke-linecap="round"/>')
    for r, row in enumerate(rows):
        for k, ch in enumerate(row):
            out.append(f'<text x="{x+k*cell+cell/2}" y="{y+r*cell+cell/2+font*0.35:.1f}" text-anchor="middle" '
                       f'font-family="{SANS}" font-weight="700" font-size="{font}" fill="{ink}">{ch}</text>')
    return "".join(out)


def mini_sudoku(x, y, ink, cell=25, paper="#fff"):
    pz, _s, _g = PZ.make_easy_sudoku(random.Random(4))
    out = [f'<rect x="{x}" y="{y}" width="{9*cell}" height="{9*cell}" fill="{paper}" stroke="{ink}" stroke-width="6"/>']
    for i in range(1, 9):
        wd = 4.5 if i % 3 == 0 else 1.5
        out.append(f'<line x1="{x+i*cell}" y1="{y}" x2="{x+i*cell}" y2="{y+9*cell}" stroke="{ink}" stroke-width="{wd}"/>')
        out.append(f'<line x1="{x}" y1="{y+i*cell}" x2="{x+9*cell}" y2="{y+i*cell}" stroke="{ink}" stroke-width="{wd}"/>')
    for r in range(9):
        for c in range(9):
            if pz[r][c]:
                out.append(f'<text x="{x+c*cell+cell/2}" y="{y+r*cell+cell/2+6}" text-anchor="middle" font-family="{SANS}" '
                           f'font-weight="700" font-size="17" fill="{ink}">{pz[r][c]}</text>')
    return "".join(out)


def mini_maze(x, y, ink, hi, cell=32, n=7, paper="#fff"):
    mz = PZ.make_maze(random.Random(9), n, n)
    out = [f'<rect x="{x-10}" y="{y-10}" width="{n*cell+20}" height="{n*cell+20}" rx="10" fill="{paper}"/>']
    pts = " ".join(f"{x+c*cell+cell/2},{y+r*cell+cell/2}" for r, c in mz["path"])
    out.append(f'<polyline points="{pts}" fill="none" stroke="{hi}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>')
    seg = []
    for r in range(n):
        for c in range(n):
            wl = mz["walls"][r][c]
            X, Y = x + c * cell, y + r * cell
            if wl["N"]:
                seg.append(f"M{X},{Y} h{cell}")
            if wl["W"] and not (r == 0 and c == 0):
                seg.append(f"M{X},{Y} v{cell}")
            if r == n - 1 and wl["S"]:
                seg.append(f"M{X},{Y+cell} h{cell}")
            if c == n - 1 and wl["E"] and not (r == n - 1):
                seg.append(f"M{X+cell},{Y} v{cell}")
    out.append(f'<path d="{" ".join(seg)}" stroke="{ink}" stroke-width="6" stroke-linecap="round" fill="none"/>')
    return "".join(out)


def three_games(cy, ink, hi, label_ink, paper="#fff", labels=("SOPA DE LETRAS", "SUDOKU", "LABERINTOS"), rot=True):
    cx = W / 2
    centers = [cx - 266, cx, cx + 266]
    items = [(mini_grid(centers[0] - 102, cy - 68, ink, hi, paper=paper), -4),
             (mini_sudoku(centers[1] - 112.5, cy - 112.5, ink, paper=paper), 3),
             (mini_maze(centers[2] - 112, cy - 112, ink, hi, paper=paper), -3)]
    out = []
    for (svg, r), x, lab in zip(items, centers, labels):
        out.append(f'<g transform="rotate({r if rot else 0} {x} {cy})">{svg}</g>')
        out.append(f'<text x="{x}" y="{cy+170}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="25" '
                   f'letter-spacing="1" fill="{label_ink}">{lab}</text>')
    return "".join(out)


def papel_picado(y, colors, n=9, h=120):
    """Banderines de papel picado con calados simples."""
    out = [f'<path d="M0,{y} Q{W/2},{y+26} {W},{y}" stroke="#6B4B3A" stroke-width="3" fill="none"/>']
    fw = W / n
    for i in range(n):
        x0 = i * fw + 6
        sag = 26 * (1 - ((i + 0.5) / n * 2 - 1) ** 2)
        top = y + sag
        c = colors[i % len(colors)]
        out.append(f'<path d="M{x0},{top} h{fw-12} v{h} l-{(fw-12)/4},-18 l-{(fw-12)/4},18 l-{(fw-12)/4},-18 l-{(fw-12)/4},18 z" fill="{c}"/>')
        cxp = x0 + (fw - 12) / 2
        out.append(f'<circle cx="{cxp}" cy="{top+45}" r="13" fill="#FBF3E4"/>')
        for k in range(6):
            a = k * math.pi / 3
            out.append(f'<circle cx="{cxp+26*math.cos(a):.1f}" cy="{top+45+26*math.sin(a):.1f}" r="5" fill="#FBF3E4"/>')
        out.append(f'<rect x="{cxp-22}" y="{top+84}" width="44" height="6" rx="3" fill="#FBF3E4"/>')
    return "".join(out)


def cempasuchil(cx, cy, r, c1="#F29F05", c2="#E36414"):
    out = []
    for ring, (rad, col) in enumerate([(r, c2), (r * 0.72, c1), (r * 0.45, c2)]):
        for k in range(14):
            a = k * 2 * math.pi / 14 + ring * 0.2
            out.append(f'<circle cx="{cx+rad*0.55*math.cos(a):.1f}" cy="{cy+rad*0.55*math.sin(a):.1f}" r="{rad*0.42:.1f}" fill="{col}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.22:.1f}" fill="#8A3B12"/>')
    return "".join(out)


def jarrito(cx, cy, s=1.0):
    """Jarrito de barro con café de olla y vapor."""
    body = "#B5542C"
    return (f'<g transform="translate({cx} {cy}) scale({s})">'
            f'<path d="M-70,-40 Q-80,40 -40,70 L40,70 Q80,40 70,-40 Z" fill="{body}"/>'
            f'<ellipse cx="0" cy="-40" rx="72" ry="16" fill="#7A3217"/>'
            f'<path d="M70,-20 Q115,-10 100,30 Q90,55 62,45" stroke="{body}" stroke-width="16" fill="none" stroke-linecap="round"/>'
            f'<path d="M-50,5 h100" stroke="#F2C14E" stroke-width="6" stroke-dasharray="14 10"/>'
            f'<path d="M-20,-70 q-14,-22 0,-44 q14,-22 0,-44" stroke="#C9B8A6" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<path d="M18,-66 q-14,-22 0,-44" stroke="#C9B8A6" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'</g>')


def pan_dulce(cx, cy, s=1.0):
    return (f'<g transform="translate({cx} {cy}) scale({s})">'
            f'<path d="M-80,20 Q-80,-60 0,-62 Q80,-60 80,20 Z" fill="#E9B872"/>'
            f'<path d="M-72,14 Q-70,-50 0,-52 Q70,-50 72,14 Z" fill="#F7E1C4"/>'
            + "".join(f'<path d="M{-55+i*22},10 Q{-40+i*18},-30 0,-48" stroke="#E0B98A" stroke-width="5" fill="none"/>' for i in range(6))
            + '<rect x="-84" y="16" width="168" height="16" rx="8" fill="#D39A55"/></g>')


def mariposa(cx, cy, s, c1, c2):
    return (f'<g transform="translate({cx} {cy}) scale({s})" opacity=".9">'
            f'<ellipse cx="-26" cy="-18" rx="30" ry="24" fill="{c1}"/><ellipse cx="26" cy="-18" rx="30" ry="24" fill="{c1}"/>'
            f'<ellipse cx="-20" cy="16" rx="20" ry="16" fill="{c2}"/><ellipse cx="20" cy="16" rx="20" ry="16" fill="{c2}"/>'
            f'<rect x="-4" y="-34" width="8" height="62" rx="4" fill="#4A3B47"/></g>')


def flor_acuarela(cx, cy, r, col, op=".55"):
    return "".join(f'<circle cx="{cx+r*0.6*math.cos(k*1.2566):.1f}" cy="{cy+r*0.6*math.sin(k*1.2566):.1f}" r="{r*0.55:.1f}" '
                   f'fill="{col}" opacity="{op}"/>' for k in range(5)) + f'<circle cx="{cx}" cy="{cy}" r="{r*0.28:.1f}" fill="#F6C453"/>'


def pill(cx, y, w, h, fill, text, color, size, family=SERIF, spacing=2):
    return (f'<rect x="{cx-w/2}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{fill}"/>'
            f'<text x="{cx}" y="{y+h/2+size*0.36:.1f}" text-anchor="middle" font-family="{family}" font-weight="700" '
            f'font-size="{size}" letter-spacing="{spacing}" fill="{color}">{text}</text>')


def seal(cx, cy, r, fill, l1, l2, color, s1=40, s2=19):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r-8}" fill="none" stroke="{color}" stroke-width="2.5" stroke-dasharray="5 5"/>'
            f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="{s1}" fill="{color}">{l1}</text>'
            f'<text x="{cx}" y="{cy+s2+16}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="{s2}" fill="{color}">{l2}</text>')


# ---------------------------------------------------------------- A · cozy latino
def cover_a():
    cream, brown, terra, green, rosa, mostaza, turq = "#FBF3E4", "#3B2418", "#B5542C", "#2F6B4F", "#D6336C", "#E2A400", "#1C8C8C"
    cx = W / 2
    o = [f'<rect width="{W}" height="{H}" fill="{cream}"/>',
         papel_picado(18, [rosa, turq, mostaza, green, terra]),
         f'<text x="{cx}" y="205" text-anchor="middle" font-family="{SERIF}" font-size="24" letter-spacing="6" fill="{brown}">PETER &amp; CARDU</text>',
         f'<text x="{cx}" y="318" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="100" textLength="{W-150}" '
         f'lengthAdjust="spacingAndGlyphs" fill="{brown}">SOPA DE LETRAS</text>',
         f'<text x="{cx}" y="384" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="50" letter-spacing="4" fill="{terra}">SUDOKU · LABERINTOS</text>',
         f'<text x="{cx}" y="456" text-anchor="middle" font-family="{SCRIPT}" font-size="78" fill="{green}">Pasatiempos Tranquilos</text>',
         pill(cx, 482, 520, 50, green, "EN ESPAÑOL · PARA ADULTOS MAYORES", "#FFFFFF", 22),
         three_games(700, brown, "#F6D38A", brown),
         jarrito(120, 1000, 0.62), pan_dulce(W - 130, 1010, 0.75),
         cempasuchil(60, 1085, 24), cempasuchil(W - 60, 1085, 22),
         pill(cx, 935, 420, 84, rosa, "LETRA GRANDE", "#FFFFFF", 44),
         f'<text x="{cx}" y="1062" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="28" fill="{brown}">70 pasatiempos · con soluciones</text>']
    return "".join(o)


# ---------------------------------------------------------------- B · llamativa
def cover_b():
    blue, yellow, red, white, ink = "#1B3A8C", "#FFD23F", "#E63946", "#FFFFFF", "#14213D"
    cx = W / 2
    tex = (f'<svg x="0" y="0" width="{W}" height="{H}" viewBox="0 0 {W} {H}" overflow="hidden">'
           f'{letter_texture(0, 0, W, H, "#FFFFFF", 0.08, cell=50, size=28, seed=28)}</svg>')
    title = "".join(f'<text x="{cx+dx}" y="{250+dy}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="112" '
                    f'textLength="{W-120}" lengthAdjust="spacingAndGlyphs" fill="{col}">SOPA DE LETRAS</text>'
                    for dx, dy, col in [(7, 7, red), (0, 0, yellow)])
    o = [f'<rect width="{W}" height="{H}" fill="{blue}"/>', tex,
         f'<text x="{cx}" y="110" text-anchor="middle" font-family="{SERIF}" font-size="24" letter-spacing="6" fill="{white}">PETER &amp; CARDU</text>',
         title,
         f'<text x="{cx}" y="330" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="56" letter-spacing="4" fill="{white}">SUDOKU · LABERINTOS</text>',
         pill(cx, 360, 600, 64, red, "EN ESPAÑOL · PARA ADULTOS", yellow, 30),
         f'<text x="{cx-85}" y="494" text-anchor="middle" font-family="{SCRIPT}" font-size="68" fill="{yellow}">Pasatiempos Tranquilos</text>',
         f'<rect x="40" y="540" width="{W-80}" height="420" rx="28" fill="#F4F1EA"/>',
         three_games(720, ink, "#FFD23F", ink, paper="#fff"),
         f'<rect x="0" y="{H-160}" width="{W}" height="160" fill="{red}"/>',
         f'<text x="{cx}" y="{H-90}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="56" letter-spacing="3" fill="{yellow}">LETRA GRANDE</text>',
         f'<text x="{cx}" y="{H-48}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="26" fill="{white}">con soluciones</text>',
         f'<circle cx="{W-128}" cy="470" r="74" fill="{yellow}" stroke="{red}" stroke-width="7"/>',
         f'<text x="{W-128}" y="484" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="62" fill="{red}">70</text>',
         f'<text x="{W-128}" y="512" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="14" fill="{ink}">PASATIEMPOS</text>']
    return "".join(o)


# ---------------------------------------------------------------- C · floral suave
def cover_c():
    bg, plum, rosa, lila, verde, dorado = "#FCEFF1", "#4A2545", "#E58FA6", "#B9A2D8", "#7FB285", "#C9963A"
    cx = W / 2
    flores = "".join([flor_acuarela(70, 90, 90, rosa), flor_acuarela(W - 45, 60, 70, lila), flor_acuarela(80, H - 120, 100, lila),
                      flor_acuarela(W - 80, H - 110, 95, rosa)])
    hojas = "".join(f'<ellipse cx="{x}" cy="{y}" rx="38" ry="14" fill="{verde}" opacity=".6" transform="rotate({a} {x} {y})"/>'
                    for x, y, a in [(60, 205, 30), (W - 70, 130, -30), (170, H - 60, -20), (W - 170, H - 50, 25)])
    o = [f'<rect width="{W}" height="{H}" fill="{bg}"/>', flores, hojas,
         mariposa(W - 105, 440, 0.7, lila, rosa), mariposa(110, 440, 0.6, rosa, lila),
         f'<text x="{cx}" y="110" text-anchor="middle" font-family="{SERIF}" font-size="24" letter-spacing="6" fill="{plum}">PETER &amp; CARDU</text>',
         f'<text x="{cx}" y="205" text-anchor="middle" font-family="{SCRIPT}" font-size="80" fill="{dorado}">Pasatiempos Tranquilos</text>',
         f'<text x="{cx}" y="318" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="104" textLength="{W-170}" '
         f'lengthAdjust="spacingAndGlyphs" fill="{plum}">SOPA DE LETRAS</text>',
         f'<text x="{cx}" y="384" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="50" letter-spacing="4" fill="{rosa}">SUDOKU · LABERINTOS</text>',
         pill(cx, 414, 520, 52, plum, "EN ESPAÑOL · PARA ADULTOS", "#FFFFFF", 24),
         three_games(655, plum, "#F7C9D4", plum),
         pill(cx, 880, 560, 90, rosa, "LETRA GRANDE", "#FFFFFF", 50),
         f'<text x="{cx}" y="1018" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="30" fill="{plum}">70 pasatiempos · con soluciones</text>']
    return "".join(o)


# ---------------------------------------------------------------- AB · mezcla elegida por Pedro (16-sep)
def cover_ab():
    cream, brown, terra, green, rosa, mostaza, turq = "#FBF3E4", "#3B2418", "#B5542C", "#2F6B4F", "#D6336C", "#E2A400", "#1C8C8C"
    cx = W / 2
    title = "".join(f'<text x="{cx+dx}" y="{300+dy}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="120" '
                    f'textLength="{W-110}" lengthAdjust="spacingAndGlyphs" fill="{col}">SOPA DE LETRAS</text>'
                    for dx, dy, col in [(6, 6, mostaza), (0, 0, terra)])
    o = [f'<rect width="{W}" height="{H}" fill="{cream}"/>',
         papel_picado(14, [rosa, turq, mostaza, green, terra], h=100),
         f'<text x="{cx}" y="172" text-anchor="middle" font-family="{SERIF}" font-size="24" letter-spacing="6" fill="{brown}">PETER &amp; CARDU</text>',
         title,
         f'<text x="{cx}" y="368" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="54" letter-spacing="4" fill="{brown}">SUDOKU · LABERINTOS</text>',
         pill(cx, 390, 560, 54, green, "EN ESPAÑOL · PARA ADULTOS MAYORES", "#FFFFFF", 23),
         f'<text x="{cx-78}" y="506" text-anchor="middle" font-family="{SCRIPT}" font-size="70" fill="{green}">Pasatiempos Tranquilos</text>',
         f'<rect x="40" y="552" width="{W-80}" height="340" rx="26" fill="#FFFFFF" stroke="{terra}" stroke-width="3"/>',
         three_games(698, brown, "#F6D38A", brown),
         f'<circle cx="{W-122}" cy="510" r="64" fill="{mostaza}" stroke="{rosa}" stroke-width="7"/>',
         f'<text x="{W-122}" y="522" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="54" fill="{brown}">70</text>',
         f'<text x="{W-122}" y="546" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="12" fill="{brown}">PASATIEMPOS</text>',
         f'<rect x="0" y="{H-150}" width="{W}" height="150" fill="{rosa}"/>',
         f'<text x="{cx}" y="{H-84}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="58" letter-spacing="3" fill="#FFFFFF">LETRA GRANDE</text>',
         f'<text x="{cx}" y="{H-42}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="26" fill="{mostaza}">con soluciones</text>',
         jarrito(92, 940, 0.36), pan_dulce(W - 96, 952, 0.45),
         cempasuchil(52, H - 75, 22), cempasuchil(W - 52, H - 75, 22)]
    return "".join(o)


# ---------------------------------------------------------------- D · Talavera
def azulejo(x, y, sz, azul="#1D4E9E", amarillo="#F2B705", fondo="#FFFDF7"):
    c = sz / 2
    o = [f'<rect x="{x}" y="{y}" width="{sz}" height="{sz}" fill="{fondo}" stroke="{azul}" stroke-width="{sz*0.05:.1f}"/>',
         f'<circle cx="{x+c}" cy="{y+c}" r="{sz*0.16:.1f}" fill="{amarillo}"/>']
    for k in range(8):
        a = k * math.pi / 4
        o.append(f'<ellipse cx="{x+c+sz*0.24*math.cos(a):.1f}" cy="{y+c+sz*0.24*math.sin(a):.1f}" rx="{sz*0.09:.1f}" ry="{sz*0.05:.1f}" '
                 f'fill="{azul}" transform="rotate({k*45} {x+c+sz*0.24*math.cos(a):.1f} {y+c+sz*0.24*math.sin(a):.1f})"/>')
    for dx, dy in [(0, 0), (sz, 0), (0, sz), (sz, sz)]:
        o.append(f'<circle cx="{x+dx}" cy="{y+dy}" r="{sz*0.14:.1f}" fill="{azul}"/>')
    o.append(f'<circle cx="{x+c}" cy="{y+c}" r="{sz*0.06:.1f}" fill="{azul}"/>')
    return "".join(o)


def cover_d():
    blanco, azul, amarillo, ink = "#FFFDF7", "#1D4E9E", "#F2B705", "#16284F"
    cx = W / 2
    sz = W / 7
    tiles = [azulejo(i * sz, 0, sz) for i in range(7)] + [azulejo(i * sz, H - sz, sz) for i in range(7)]
    o = [f'<rect width="{W}" height="{H}" fill="{blanco}"/>', "".join(tiles),
         f'<text x="{cx}" y="{sz+62}" text-anchor="middle" font-family="{SERIF}" font-size="24" letter-spacing="6" fill="{ink}">PETER &amp; CARDU</text>',
         "".join(f'<text x="{cx+dx}" y="{sz+180+dy}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="112" '
                 f'textLength="{W-120}" lengthAdjust="spacingAndGlyphs" fill="{col}">SOPA DE LETRAS</text>' for dx, dy, col in [(5, 5, amarillo), (0, 0, azul)]),
         f'<text x="{cx}" y="{sz+246}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="50" letter-spacing="4" fill="{ink}">SUDOKU · LABERINTOS</text>',
         f'<text x="{cx}" y="{sz+318}" text-anchor="middle" font-family="{SCRIPT}" font-size="66" fill="{azul}">Pasatiempos Tranquilos</text>',
         pill(cx, sz + 340, 560, 52, azul, "EN ESPAÑOL · PARA ADULTOS MAYORES", "#FFFFFF", 22),
         three_games(sz + 548, ink, "#FBE3A1", ink),
         pill(cx - 70, H - sz - 112, 420, 72, amarillo, "LETRA GRANDE", ink, 38),
         f'<circle cx="{cx+235}" cy="{H-sz-76}" r="54" fill="{azul}"/>',
         f'<text x="{cx+235}" y="{H-sz-70}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="44" fill="#FFFFFF">70</text>',
         f'<text x="{cx+235}" y="{H-sz-47}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="11" fill="#FFFFFF">PASATIEMPOS</text>']
    return "".join(o)


# ---------------------------------------------------------------- E · Lotería
def carta(x, y, w, h, num, nombre, contenido, borde="#1B1B1B", fondo="#FFFDF4", color="#C8102E"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fondo}" stroke="{borde}" stroke-width="7"/>'
            f'<rect x="{x+14}" y="{y+14}" width="{w-28}" height="{h-28}" rx="6" fill="none" stroke="{borde}" stroke-width="2.5"/>'
            f'<text x="{x+28}" y="{y+52}" font-family="{SERIF}" font-weight="700" font-size="30" fill="{color}">{num}</text>'
            f'{contenido}'
            f'<text x="{x+w/2}" y="{y+h-30}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="26" letter-spacing="1" fill="{borde}">{nombre}</text>')


def cover_e():
    rojo, verde, amarillo, crema, ink = "#C8102E", "#00845A", "#F4B400", "#FFF6E3", "#1B1B1B"
    cx = W / 2
    stripes = "".join(f'<rect x="{i*W/12}" y="0" width="{W/12+1}" height="{H}" fill="{c}" opacity=".10"/>' for i, c in
                      zip(range(12), [rojo, amarillo, verde] * 4))
    cw, ch = 250, 340
    xs = [cx - 1.5 * cw - 16, cx - cw / 2, cx + cw / 2 + 16]
    y0 = 560
    cards = [carta(xs[0], y0, cw, ch, "1", "LA SOPA", f'<g transform="translate({xs[0]+cw/2-93} {y0+118}) scale(0.78)">{mini_grid(14, 14, ink, "#FBE3A1")}</g>'),
             carta(xs[1], y0 + 18, cw, ch, "2", "EL SUDOKU", f'<g transform="translate({xs[1]+cw/2-88} {y0+90}) scale(0.78)">{mini_sudoku(0, 0, ink)}</g>'),
             carta(xs[2], y0, cw, ch, "3", "EL LABERINTO", f'<g transform="translate({xs[2]+cw/2-96} {y0+84}) scale(0.70)">{mini_maze(10, 10, ink, "#FBE3A1")}</g>')]
    o = [f'<rect width="{W}" height="{H}" fill="{crema}"/>', stripes,
         f'<text x="{cx}" y="100" text-anchor="middle" font-family="{SERIF}" font-size="24" letter-spacing="6" fill="{ink}">PETER &amp; CARDU</text>',
         f'<text x="{cx}" y="175" text-anchor="middle" font-family="{SCRIPT}" font-size="70" fill="{verde}">Pasatiempos Tranquilos</text>',
         "".join(f'<text x="{cx+dx}" y="{300+dy}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="118" '
                 f'textLength="{W-110}" lengthAdjust="spacingAndGlyphs" fill="{col}">SOPA DE LETRAS</text>' for dx, dy, col in [(6, 6, amarillo), (0, 0, rojo)]),
         f'<text x="{cx}" y="370" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="54" letter-spacing="4" fill="{ink}">SUDOKU · LABERINTOS</text>',
         pill(cx, 400, 560, 54, verde, "EN ESPAÑOL · PARA ADULTOS MAYORES", "#FFFFFF", 23),
         f'<text x="{cx}" y="520" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="34" fill="{ink}">¡Lotería de pasatiempos!</text>',
         "".join(cards),
         f'<rect x="0" y="{H-150}" width="{W}" height="150" fill="{rojo}"/>',
         f'<text x="{cx}" y="{H-86}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="56" letter-spacing="3" fill="#FFFFFF">LETRA GRANDE</text>',
         f'<text x="{cx}" y="{H-44}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="26" fill="{amarillo}">70 pasatiempos · con soluciones</text>']
    return "".join(o)


# ---------------------------------------------------------------- F · Atardecer con bugambilias
def bugambilia(cx, cy, r, col="#C2185B", col2="#E91E63"):
    rng = random.Random(int(cx * 7 + cy))
    o = []
    for _ in range(18):
        a, d = rng.random() * 2 * math.pi, rng.random() * r
        x, y, rr = cx + d * math.cos(a), cy + d * math.sin(a), r * (0.18 + rng.random() * 0.12)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="{col if rng.random()<0.5 else col2}" opacity=".9"/>')
    for _ in range(6):
        a, d = rng.random() * 2 * math.pi, r * (0.8 + rng.random() * 0.4)
        x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        o.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r*0.22:.1f}" ry="{r*0.1:.1f}" fill="#3E7B3E" transform="rotate({rng.random()*180:.0f} {x:.1f} {y:.1f})"/>')
    return "".join(o)


def cover_f():
    ink, blanco, rosa = "#2B1B17", "#FFFFFF", "#C2185B"
    cx = W / 2
    o = ['<defs><linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#F9A03F"/><stop offset=".55" stop-color="#F7C59F"/><stop offset="1" stop-color="#FDEBD3"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#cielo)"/>',
         f'<circle cx="{cx}" cy="470" r="150" fill="#FFE08A" opacity=".85"/>',
         f'<path d="M0,500 Q200,420 420,480 Q640,540 {W},450 L{W},{H} L0,{H} Z" fill="#8DB580" opacity=".55"/>',
         f'<path d="M0,560 Q260,500 520,550 Q720,590 {W},540 L{W},{H} L0,{H} Z" fill="#6E9E63" opacity=".45"/>',
         bugambilia(20, 30, 80), bugambilia(W - 20, 30, 80), bugambilia(30, H - 40, 85), bugambilia(W - 30, H - 40, 85),
         f'<text x="{cx}" y="110" text-anchor="middle" font-family="{SERIF}" font-size="24" letter-spacing="6" fill="{ink}">PETER &amp; CARDU</text>',
         "".join(f'<text x="{cx+dx}" y="{250+dy}" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="116" '
                 f'textLength="{W-140}" lengthAdjust="spacingAndGlyphs" fill="{col}">SOPA DE LETRAS</text>' for dx, dy, col in [(5, 5, "#FFFFFF"), (0, 0, ink)]),
         f'<text x="{cx}" y="318" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="52" letter-spacing="4" fill="{rosa}">SUDOKU · LABERINTOS</text>',
         f'<text x="{cx}" y="392" text-anchor="middle" font-family="{SCRIPT}" font-size="70" fill="{ink}">Pasatiempos Tranquilos</text>',
         pill(cx, 414, 520, 50, ink, "EN ESPAÑOL · PARA ADULTOS", "#FFFFFF", 22),
         f'<rect x="40" y="520" width="{W-80}" height="370" rx="26" fill="#FFFFFF" opacity=".92"/>',
         three_games(680, ink, "#F9C6D8", ink),
         pill(cx, 930, 480, 84, rosa, "LETRA GRANDE", blanco, 44),
         f'<text x="{cx}" y="1060" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="28" fill="{ink}">70 pasatiempos · con soluciones</text>']
    return "".join(o)


# ---------------------------------------------------------------- F2 · Atardecer dorado (estilo premium tipo Fiverr: noche + líneas doradas)
def bugambilia_linea(cx, cy, r, oro, rot=0):
    o = [f'<g transform="rotate({rot} {cx} {cy})" fill="none" stroke="{oro}" stroke-width="2.6" stroke-linecap="round">']
    for k in range(3):
        a = k * 2 * math.pi / 3
        x, y = cx + r * 0.45 * math.cos(a), cy + r * 0.45 * math.sin(a)
        o.append(f'<path d="M{cx:.1f},{cy:.1f} Q{x+r*0.5*math.cos(a+1.2):.1f},{y+r*0.5*math.sin(a+1.2):.1f} {x+r*0.55*math.cos(a):.1f},{y+r*0.55*math.sin(a):.1f} '
                 f'Q{x+r*0.5*math.cos(a-1.2):.1f},{y+r*0.5*math.sin(a-1.2):.1f} {cx:.1f},{cy:.1f}"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.08:.1f}" fill="{oro}"/>')
    o.append(f'<path d="M{cx},{cy} q{-r*0.9},{r*0.4} {-r*1.4},{r*1.2}"/>')
    o.append(f'<path d="M{cx-r*0.9:.1f},{cy+r*0.7:.1f} q{-r*0.3},{-r*0.35} {-r*0.05},{-r*0.55} q{r*0.15},{r*0.3} {r*0.05},{r*0.55}"/>')
    o.append('</g>')
    return "".join(o)


def cover_f2():
    oro, crema, noche = "url(#oro)", "#F3E9D2", "#101A33"
    oro_plano = "#D9B25A"
    cx = W / 2
    defs = ('<defs><linearGradient id="noche" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0E1730"/>'
            '<stop offset=".6" stop-color="#1A1F3F"/><stop offset="1" stop-color="#2A1C3D"/></linearGradient>'
            '<linearGradient id="oro" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBE7A8"/>'
            '<stop offset=".5" stop-color="#D9A93F"/><stop offset="1" stop-color="#F4D27E"/></linearGradient>'
            '<radialGradient id="brillo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#F2C45A" stop-opacity=".35"/>'
            '<stop offset="1" stop-color="#F2C45A" stop-opacity="0"/></radialGradient></defs>')
    rng = random.Random(5)
    puntos = "".join(f'<circle cx="{rng.random()*W:.0f}" cy="{rng.random()*H*0.5:.0f}" r="{rng.choice([1.2,1.6,2.2])}" fill="{oro_plano}" opacity="{rng.choice([.25,.4,.6])}"/>'
                     for _ in range(90))
    rayos = "".join(f'<line x1="{cx+132*math.cos(a):.1f}" y1="{600+132*math.sin(a):.1f}" x2="{cx+150*math.cos(a):.1f}" y2="{600+150*math.sin(a):.1f}" '
                    f'stroke="{oro_plano}" stroke-width="2.5" stroke-linecap="round" opacity=".7"/>'
                    for a in [math.pi + k * math.pi / 12 for k in range(1, 12)])
    o = [defs, f'<rect width="{W}" height="{H}" fill="url(#noche)"/>', puntos,
         f'<circle cx="{cx}" cy="600" r="300" fill="url(#brillo)"/>',
         f'<circle cx="{cx}" cy="600" r="115" fill="none" stroke="{oro_plano}" stroke-width="3" opacity=".8"/>', rayos,
         f'<path d="M0,560 Q200,470 430,535 Q650,595 {W},500" fill="none" stroke="{oro_plano}" stroke-width="3" opacity=".8"/>',
         f'<path d="M0,600 Q260,540 520,585 Q720,620 {W},575" fill="none" stroke="{oro_plano}" stroke-width="2" opacity=".5"/>',
         bugambilia_linea(70, 60, 42, oro_plano, -20), bugambilia_linea(W - 70, 60, 42, oro_plano, 200),
         bugambilia_linea(80, H - 100, 44, oro_plano, 30), bugambilia_linea(W - 80, H - 100, 44, oro_plano, 160),
         f'<text x="{cx}" y="92" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="26" letter-spacing="7" fill="{oro}">PETER &amp; CARDU</text>',
         f'<line x1="{cx-150}" y1="112" x2="{cx+150}" y2="112" stroke="{oro_plano}" stroke-width="1.5"/>',
         f'<text x="{cx}" y="238" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="120" textLength="{W-150}" '
         f'lengthAdjust="spacingAndGlyphs" fill="{oro}">SOPA DE LETRAS</text>',
         f'<text x="{cx}" y="306" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="52" letter-spacing="5" fill="{crema}">SUDOKU · LABERINTOS</text>',
         f'<text x="{cx}" y="378" text-anchor="middle" font-family="{SCRIPT}" font-size="72" fill="{oro}">Pasatiempos Tranquilos</text>',
         f'<rect x="{cx-280}" y="398" width="560" height="50" rx="25" fill="none" stroke="{oro_plano}" stroke-width="2.5"/>',
         f'<text x="{cx}" y="431" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="22" letter-spacing="2" fill="{crema}">EN ESPAÑOL · PARA ADULTOS MAYORES</text>',
         f'<rect x="44" y="612" width="{W-88}" height="330" rx="24" fill="#0E1730" opacity=".82" stroke="{oro_plano}" stroke-width="2"/>',
         three_games(760, oro_plano, "#5B4A24", crema, paper="#141E3A"),
         f'<rect x="{cx-230}" y="962" width="460" height="78" rx="39" fill="{oro}"/>',
         f'<text x="{cx}" y="1015" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="42" letter-spacing="2" fill="{noche}">LETRA GRANDE</text>',
         f'<text x="{cx}" y="1080" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="26" letter-spacing="1" fill="{crema}">70 pasatiempos · con soluciones</text>']
    return "".join(o)


def page(svg, title):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{title}</title><style>{font_css()}'
            f'@page {{ size: {W/U:.4f}in {H/U:.4f}in; margin: 0; }} html,body{{margin:0;padding:0}} '
            f'svg{{display:block;width:{W/U:.4f}in;height:{H/U:.4f}in}}</style></head><body>'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}">{svg}</svg></body></html>')


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, fn in [("A-cozy-latino", cover_a), ("B-llamativa", cover_b), ("C-floral-suave", cover_c), ("AB-mezcla", cover_ab), ("D-talavera", cover_d), ("E-loteria", cover_e), ("F-atardecer", cover_f), ("F2-atardecer-dorado", cover_f2)]:
        p = os.path.join(out, f"portada_{name}.html")
        open(p, "w", encoding="utf-8").write(page(fn(), name))
        print(p)

"""Versión en español (Pasatiempos Tranquilos) de la página 2 de Calm & Cozy: "This book belongs to", How to Play con íconos
y un mini ejemplo por tipo de puzzle (sopa, sudoku, laberinto), aviso de soluciones y copyright.

Sigue la línea de la p2 con íconos de Big Print Word Hunt (generar.instructions_icons).
"""
import html
import random
import re

import puzzles as PZ
from generar import ICON, icon

ICON.update({
    "grid9": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18M15 3v18M3 9h18M3 15h18"/>',
    "norep": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7.5 8.5l9 7M16.5 8.5l-9 7"/>',
    "start": '<path d="M3 12h13M12 7l5 5-5 5"/><path d="M21 4v16"/>',
    "path": '<path d="M4 20V13h7V6h9"/><circle cx="4" cy="20" r="1.4"/><path d="M17 3l3 3-3 3"/>',
    "cup": '<path d="M4 9h12v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M16 11h1.5a2.5 2.5 0 0 1 0 5H16"/>'
           '<path d="M8 3.5c0 1.5 1.5 1.5 1.5 3M12 3.5c0 1.5 1.5 1.5 1.5 3"/>',
})

CSS = """
.p2 {{ width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; }}
.p2 .belongs {{ width: 100%; font-size: 16pt; font-weight: 700; display: flex; align-items: flex-end; gap: 0.1in;
               margin: 0.02in 0 0.22in; }}
.p2 .belongs span {{ flex: 1; border-bottom: 1.5px solid #111; height: 1.2em; }}
.p2 .howbox {{ border: 2px solid #111; border-radius: 12px; padding: 0.03in 0.36in; font-size: 22pt; font-weight: 700;
              margin: 0 0 0.16in; }}
.p2 .card {{ width: 100%; display: flex; align-items: center; gap: 0.3in; border: 1.5px solid #111; border-radius: 14px;
            padding: 0.2in 0.24in; margin-bottom: 0.18in; }}
.p2 .ex {{ flex: none; width: 2.05in; display: flex; flex-direction: column; align-items: center; }}
.p2 .ex .cap {{ font-size: 11.5pt; font-style: italic; margin-top: 0.06in; }}
.p2 .ex svg {{ width: 100%; height: auto; max-height: 1.8in; }}
.p2 .txt {{ flex: 1; }}
.p2 .txt h2 {{ font-size: 17pt; margin: 0 0 0.06in; }}
.p2 .step {{ display: flex; align-items: center; gap: 0.12in; font-size: 13.5pt; line-height: 1.25; margin: 0.06in 0; }}
.p2 .step .ico {{ flex: none; }}
.p2 .solnote {{ width: 100%; display: flex; align-items: center; justify-content: center; gap: 0.14in;
               font-size: 15pt; margin-top: 0.04in; }}
.p2 .copyright {{ position: static; margin-top: auto; margin-bottom: 0.12in; width: 100%; border-top: 1.5px solid #999; padding-top: 0.1in;
                 font-size: 9pt; color: #444; text-align: center; line-height: 1.35; }}
"""


def _word_example():
    rows = ["SOLRUB", "MCUDWH", "IJARED", "EYVFGR", "LPNOEU", "BWIDTU"]
    marks = [(0, 0, 0, 2), (1, 0, 4, 0), (1, 1, 4, 4)]  # SOL →, MIEL ↓, CAFE ↘
    cell, n = 30, len(rows)
    inside = set()
    out = [f'<svg viewBox="-8 -8 {n*cell+16} {n*cell+16}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect x="-6" y="-6" width="{n*cell+12}" height="{n*cell+12}" rx="8" fill="#fff" stroke="#111" stroke-width="2.5"/>']
    for r1, c1, r2, c2 in marks:
        dr, dc = (r2 > r1) - (r2 < r1), (c2 > c1) - (c2 < c1)
        for t in range(max(abs(r2 - r1), abs(c2 - c1)) + 1):
            inside.add((r1 + dr * t, c1 + dc * t))
        out.append(f'<line x1="{c1*cell+cell/2}" y1="{r1*cell+cell/2}" x2="{c2*cell+cell/2}" y2="{r2*cell+cell/2}" '
                   'stroke="#111" stroke-width="25" stroke-linecap="round"/>')
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            fill = "#fff" if (r, c) in inside else "#111"
            out.append(f'<text x="{c*cell+cell/2}" y="{r*cell+cell/2+7}" text-anchor="middle" font-size="19" '
                       f'font-weight="700" font-family="Liberation Sans, Arial" fill="{fill}">{ch}</text>')
    out.append("</svg>")
    return "".join(out)


def _sudoku_example():
    box = [[5, 3, 2], [6, 0, 1], [9, 8, 4]]  # falta el 7
    cell = 56
    s = 3 * cell
    out = [f'<svg viewBox="-6 -6 {s+12} {s+12}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect x="0" y="0" width="{s}" height="{s}" fill="#fff"/>']
    for i in range(4):
        w = 6 if i in (0, 3) else 2.5
        out.append(f'<line x1="{i*cell}" y1="0" x2="{i*cell}" y2="{s}" stroke="#111" stroke-width="{w}" stroke-linecap="square"/>')
        out.append(f'<line x1="0" y1="{i*cell}" x2="{s}" y2="{i*cell}" stroke="#111" stroke-width="{w}" stroke-linecap="square"/>')
    for r in range(3):
        for c in range(3):
            x, y = c * cell + cell / 2, r * cell + cell / 2 + 12
            if box[r][c]:
                out.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="34" font-weight="700" '
                           f'font-family="Liberation Sans, Arial" fill="#111">{box[r][c]}</text>')
            else:
                out.append(f'<circle cx="{x}" cy="{r*cell+cell/2}" r="21" fill="#111"/>'
                           f'<text x="{x}" y="{y}" text-anchor="middle" font-size="34" font-weight="700" '
                           f'font-family="Liberation Sans, Arial" fill="#fff">7</text>')
    out.append("</svg>")
    return "".join(out)


def _maze_example():
    mz = PZ.make_maze(random.Random(4), 6, 6)
    cell, lw = 30, 5
    svg = PZ.maze_svg(mz, solve=True, cell=cell, lw=lw)
    W, H = 6 * cell, 6 * cell
    # las flechas de entrada y salida quedan fuera del viewBox original: se amplía
    return re.sub(r'class="maze" viewBox="[^"]*"', f'viewBox="{-cell} {-lw} {W + 2*cell} {H + 2*lw}"', svg, count=1)


CSS3 = """
.p3 {{ width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; }}
.p3 .howbox {{ border: 2px solid #111; border-radius: 12px; padding: 0.03in 0.36in; font-size: 22pt; font-weight: 700; margin: 0.1in 0 0.12in; }}
.p3 .lead {{ font-size: 13.5pt; text-align: center; margin: 0 0 0.2in; color: #333; }}
.p3 .tipcard {{ width: 100%; border: 1.5px solid #111; border-radius: 14px; padding: 0.16in 0.3in 0.1in; margin-bottom: 0.2in; }}
.p3 .tipcard h2 {{ display: flex; align-items: center; gap: 0.12in; font-size: 17pt; margin: 0 0 0.08in; }}
.p3 .tipcard ul {{ margin: 0; padding-left: 0.28in; }}
.p3 .tipcard li {{ font-size: 14pt; line-height: 1.3; margin-bottom: 0.08in; }}
.p3 .closing {{ margin-top: auto; margin-bottom: 0.2in; display: flex; align-items: center; gap: 0.14in; font-size: 15pt; font-weight: 700; text-align: center; }}
"""


CSS4 = """
.thanks {{ width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }}
.thanks .t-script {{ font-family: 'Caveat', cursive; font-size: 64pt; line-height: 1; margin-bottom: 0.3in; }}
.thanks p {{ font-size: 16pt; line-height: 1.55; max-width: 5.8in; margin: 0 0 0.22in; color: #222; }}
.thanks .sign {{ font-family: 'Playfair Display', serif; font-size: 14pt; letter-spacing: 5px; margin-top: 0.3in; }}
"""


def css():
    return CSS.format() + CSS3.format() + CSS4.format()


def thanks_page(book):
    title = html.escape(book.get("series", book["title"]))
    return ('<div class="thanks">'
            f'{icon("cup", "0.8in")}<div class="t-script">¡Gracias!</div>'
            f'<p>Gracias por regalarte un rato de calma con <i>{title}</i>. '
            'Esperamos que estas páginas te hayan dado momentos tranquilos y felices.</p>'
            '<p>Si te gustó este libro, te agradeceríamos mucho que dejaras una breve reseña con tu opinión sincera. '
            'Ayuda a que otras personas lo encuentren y nos anima a preparar el próximo volumen.</p>'
            f'<div class="sign">{html.escape(book.get("author", "").upper())}</div></div>')


TIPS = [
    ("lens", "Sopa de Letras", [
        "Busca la <b>primera letra</b> de la palabra y revisa las letras de alrededor.",
        "Fíjate en las letras dobles, como la <b>LL</b> de OLLA o la <b>RR</b> de ARROZ.",
        "Recorre fila por fila, con el dedo o un marcador como guía.",
    ]),
    ("grid9", "Sudoku Fácil", [
        "Empieza por la fila, columna o cuadro que tenga <b>más números</b>.",
        "Elige un número, por ejemplo el <b>1</b>, y busca en qué cuadros todavía falta.",
        "¿Tienes dudas? Anota números pequeños en la esquina de la casilla.",
    ]),
    ("path", "Laberintos", [
        "Traza el camino <b>suavemente</b> con lápiz para poder borrar.",
        "¿Te atascaste? Empieza desde la <b>flecha de salida</b> y ve hacia atrás.",
        "Un callejón sin salida es parte del juego: vuelve al último cruce.",
    ]),
]


def page3():
    cards = "".join(
        f'<div class="tipcard"><h2>{icon(ic, "0.34in")}{t}</h2><ul>'
        + "".join(f"<li>{x}</li>" for x in tips) + "</ul></div>"
        for ic, t, tips in TIPS)
    return ('<div class="p3"><div class="howbox">Consejos Útiles</div>'
            '<div class="lead">Algunas ideas para empezar con calma.</div>'
            f'{cards}<div class="closing">{icon("cup", "0.4in")}<span>Sin apuro y sin presiones. Un pasatiempo a la vez.</span></div></div>')


def page2(book, sol_start):
    def steps(rows):
        return "".join(f'<div class="step">{icon(ic, "0.27in")}<span>{tx}</span></div>' for ic, tx in rows)

    cards = [
        (_word_example(), "Sopa de Letras", [
            ("list", "Busca cada palabra de la lista."),
            ("lens", "Se leen de izquierda a derecha, hacia abajo o en diagonal."),
            ("check", "Van <b>sin tildes</b>, y las de dos palabras van <b>juntas</b> (ARROZ CON LECHE = ARROZCONLECHE)."),
            ("pencil", "Enciérrala en la grilla y táchala de la lista."),
        ]),
        (_sudoku_example(), "Sudoku Fácil", [
            ("grid9", "Cada <b>fila</b>, <b>columna</b> y <b>cuadro de 3&times;3</b> lleva los números del <b>1 al 9</b>."),
            ("norep", "Ningún número se repite en la misma fila, columna o cuadro."),
            ("check", "Cada sudoku tiene una sola solución."),
        ]),
        (_maze_example(), "Laberintos", [
            ("start", "Entra por la flecha de la izquierda."),
            ("path", "Encuentra el único camino hasta la flecha de la derecha."),
            ("pencil", "Usa lápiz para poder intentarlo de nuevo."),
        ]),
    ]
    captions = {"Sudoku Fácil": "A este cuadro le falta el 7."}
    body = "".join(f'<div class="card"><div class="ex">{ex}'
                   + (f'<div class="cap">{captions[t]}</div>' if t in captions else "")
                   + f'</div><div class="txt"><h2>{t}</h2>{steps(st)}</div></div>'
                   for ex, t, st in cards)
    copyright = ""
    if book.get("author"):
        copyright = (f'<div class="copyright">Copyright &copy; {book.get("year", "")} {html.escape(book["author"])}. '
                     'Todos los derechos reservados. Ninguna parte de este libro puede reproducirse de ninguna forma '
                     'sin permiso escrito de los autores.</div>')
    return ('<div class="p2"><div class="belongs">Este libro pertenece a<span></span></div>'
            f'<div class="howbox">Cómo Jugar</div>{body}'
            f'<div class="solnote">{icon("cup", "0.4in")}<span><b>Tómate tu tiempo. ¿Te atascaste? Las soluciones empiezan en la página '
            f'{sol_start}.</b></span></div>{copyright}</div>')

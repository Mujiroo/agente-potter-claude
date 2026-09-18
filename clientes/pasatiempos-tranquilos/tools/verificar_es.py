#!/usr/bin/env python3
"""Auditoría del interior híbrido: lee el HTML ya generado y comprueba, sin
confiar en el generador, que todo lo que promete el libro se cumple.

  verificar_mixto.py libro.json salida.html
"""
import html
import json
import re
import sys

DIRS = [(0, 1), (1, 0), (1, 1), (-1, 1)]
ALL8 = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/../../libro-sopa-de-letras/tools")
from generar import BAD  # noqa: E402
sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/..")
from verificar_temas import BAD_ES, BAD_RELLENO  # noqa: E402
from tildes_es import con_tildes, sin_tildes  # noqa: E402
BAD = list(dict.fromkeys(BAD + BAD_ES + BAD_RELLENO))


def solvable_by_singles(g):
    g = [r[:] for r in g]

    def cands(r, c):
        used = set(g[r]) | {g[i][c] for i in range(9)} | {g[i][j] for i in range(r // 3 * 3, r // 3 * 3 + 3)
                                                        for j in range(c // 3 * 3, c // 3 * 3 + 3)}
        return set(range(1, 10)) - used
    units = ([[(r, c) for c in range(9)] for r in range(9)] + [[(r, c) for r in range(9)] for c in range(9)]
             + [[(r, c) for r in range(a, a + 3) for c in range(b, b + 3)] for a in (0, 3, 6) for b in (0, 3, 6)])
    while True:
        prog = False
        for r in range(9):
            for c in range(9):
                if not g[r][c]:
                    cs = cands(r, c)
                    if len(cs) == 1:
                        g[r][c] = cs.pop()
                        prog = True
        for u in units:
            for d in range(1, 10):
                spots = [(r, c) for r, c in u if not g[r][c] and d in cands(r, c)]
                if len(spots) == 1:
                    g[spots[0][0]][spots[0][1]] = d
                    prog = True
        if not prog:
            return all(all(r) for r in g)


def parse_pages(doc):
    return re.findall(r'<section class="page [^"]*">(.*?)</section>', doc, re.S)


def grid_of(page):
    """Reconstruye la grilla a partir de los <text> del SVG (orden de dibujo)."""
    letters = re.findall(r'<text [^>]*>([A-ZÑ])</text>', page)
    n = int(round(len(letters) ** 0.5))
    if n * n != len(letters):
        return None
    return [letters[r * n:(r + 1) * n] for r in range(n)]


def find_all(grid, word, dirs):
    n = len(grid)
    hits = []
    for r in range(n):
        for c in range(n):
            for dr, dc in dirs:
                rr, cc = r, c
                ok = True
                cells = []
                for ch in word:
                    if not (0 <= rr < n and 0 <= cc < n) or grid[rr][cc] != ch:
                        ok = False
                        break
                    cells.append((rr, cc))
                    rr += dr
                    cc += dc
                if ok:
                    hits.append(tuple(cells))
    return hits


def main(src, dst):
    book = json.load(open(src, encoding="utf-8"))
    doc = open(dst, encoding="utf-8").read()
    pages = parse_pages(doc)
    errs, warn = [], []
    n_w = len(book["word_puzzles"])
    n_s, n_m = book.get("sudokus", 0), book.get("mazes", 0)

    # --- numeración y paridad
    for i, p in enumerate(pages, 1):
        num = re.search(r'<div class="num">(\d+)</div>', p)
        if i == 1:
            if num:
                errs.append("la página 1 no debería llevar número")
        elif not num or int(num.group(1)) != i:
            errs.append(f"página {i}: número equivocado ({num.group(1) if num else 'falta'})")
    if len(pages) % 2:
        errs.append(f"el total de páginas es impar ({len(pages)}): KDP exige par")

    # --- índice de páginas por tipo
    kinds = []
    for i, p in enumerate(pages, 1):
        t = re.search(r'<div class="tag">([^<]+)</div>', p)
        kinds.append((i, t.group(1) if t else None))
    ws = [(i, t) for i, t in kinds if t and t.startswith("Sopa de letras")]
    su = [(i, t) for i, t in kinds if t and t.startswith("Sudoku")]
    mz = [(i, t) for i, t in kinds if t and t.startswith("Laberinto")]
    if len(ws) != 2 * n_w:
        errs.append(f"hay {len(ws)} páginas de sopa y deberían ser {2*n_w} (puzzle + solución)")
    if len(su) != n_s:
        errs.append(f"hay {len(su)} páginas de sudoku y deberían ser {n_s}")
    if len(mz) != n_m:
        errs.append(f"hay {len(mz)} páginas de laberinto y deberían ser {n_m}")

    # --- la referencia a las soluciones de la página 2
    sol_pg = next((i for i, p in enumerate(pages, 1) if 'class="tp-script">Soluciones<' in p), None)
    ref = re.search(r'soluciones empiezan en la página (\d+)', pages[1], re.I)
    if not ref:
        errs.append("la página 2 no dice dónde empiezan las soluciones")
    elif sol_pg is None or int(ref.group(1)) != sol_pg:
        errs.append(f"la página 2 manda a la página {ref.group(1)} y las soluciones están en la {sol_pg}")

    # --- cada sopa: enunciado y solución
    half = len(ws) // 2
    for k in range(half):
        pi, _ = ws[k]
        si, _ = ws[half + k]
        pz = book["word_puzzles"][k]
        gp, gs = grid_of(pages[pi - 1]), grid_of(pages[si - 1])
        tag = f'sopa {k+1} "{pz["theme"]}" (págs. {pi}/{si})'
        if gp is None or gs is None:
            errs.append(f"{tag}: no pude leer la grilla")
            continue
        if gp != gs:
            errs.append(f"{tag}: la grilla del enunciado y la de la solución no coinciden")
        # el título y la lista de palabras
        for idx in (pi, si):
            if f'<h1>{html.escape(pz["theme"])}</h1>' not in pages[idx - 1]:
                errs.append(f"{tag}: falta el título en la página {idx}")
            listed = [html.unescape(x).strip() for x in re.findall(r'<li>([^<]+)</li>', pages[idx - 1])]
            if [sin_tildes(x) for x in listed] != pz["words"]:
                errs.append(f"{tag}: la lista de la página {idx} no calza con el JSON")
            # la lista va con su ortografía correcta (tildes), la grilla sin ellas
            if listed != [con_tildes(w) for w in pz["words"]]:
                errs.append(f"{tag}: la lista de la página {idx} no lleva las tildes de tildes_es.py")
        # cada palabra, una sola vez y nunca al revés
        for w in pz["words"]:
            plain = w.replace(" ", "")
            fwd = find_all(gp, plain, DIRS)
            # descarto las que están contenidas dentro de otra palabra de la lista
            others = [o.replace(" ", "") for o in pz["words"] if o != w]
            fwd = [h for h in fwd if not any(
                set(h) <= set(c) for o in others for c in find_all(gp, o, DIRS))]
            if len(fwd) != 1:
                errs.append(f"{tag}: {w} aparece {len(fwd)} veces hacia adelante")
            back = [h for h in find_all(gp, plain, ALL8) if h not in find_all(gp, plain, DIRS)]
            if back:
                errs.append(f"{tag}: {w} también se puede leer al revés")
        # groserías en el relleno, en las ocho direcciones. Se toleran las que caen
        # enteras dentro de una palabra de la lista (ASS dentro de GLASSES).
        inside = [set(c) for w in pz["words"] for c in find_all(gp, w.replace(" ", ""), DIRS)]
        for b in BAD:
            for hit in find_all(gp, b, ALL8):
                if not any(set(hit) <= o for o in inside):
                    errs.append(f"{tag}: aparece {b} en el relleno")
        # las cápsulas de la solución
        caps = len(re.findall(r'<rect [^>]*rx="15"', pages[si - 1]))
        if caps != 9:
            errs.append(f"{tag}: la solución marca {caps} palabras y deberían ser 9")

    # --- sudokus: una sola solución y coherencia enunciado/solución
    sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/../../calm-cozy/tools")
    import puzzles as PZ
    sud_sol = [p for i, p in enumerate(pages, 1) if '<h1>Sudoku</h1>' in p]
    n_sol = sum(len(re.findall(r'<div>Sudoku \d+</div>', p)) for p in sud_sol)
    if n_sol != n_s:
        errs.append(f"hay {n_sol} soluciones de sudoku y deberían ser {n_s}")
    for i, t in su:
        cells = re.findall(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*>(\d)</text>', pages[i - 1])
        if not 30 <= len(cells) <= 45:
            warn.append(f"{t} (pág. {i}): {len(cells)} pistas, fuera del rango fácil 30-45")
        g = [[0] * 9 for _ in range(9)]
        for x, y, v in cells:
            g[int(float(y) // 60)][int(float(x) // 60)] = int(v)
        if PZ.count_solutions([r[:] for r in g], limit=2) != 1:
            errs.append(f"{t} (pág. {i}): no tiene solución única")
        elif not solvable_by_singles(g):
            warn.append(f"{t} (pág. {i}): necesita técnicas más allá de singles (no es 'easy')")

    # --- laberintos: que tengan camino
    for i, t in mz:
        if '<h1>Encuentra el camino</h1>' not in pages[i - 1]:
            errs.append(f"{t} (pág. {i}): falta el título")
    for i, p in enumerate(pages, 1):  # flechas de entrada/salida dentro del dibujo
        for vb, cell in re.findall(r'<svg class="maze" viewBox="(-?[\d.]+) [^"]*"[^>]*>.*?M(-[\d.]+),', p, re.S):
            if float(vb) > float(cell):
                errs.append(f"pág. {i}: la flecha de entrada del laberinto queda fuera del dibujo")
    mz_sol = [p for p in pages if '<h1>Laberintos</h1>' in p]
    n_msol = sum(len(re.findall(r'<div>Laberinto \d+</div>', p)) for p in mz_sol)
    if n_msol != n_m:
        errs.append(f"hay {n_msol} soluciones de laberinto y deberían ser {n_m}")

    print(f"{len(pages)} páginas · {half} sopas · {len(su)} sudokus · {len(mz)} laberintos")
    print(f"errores: {len(errs)} · avisos: {len(warn)}")
    for e in errs:
        print("  ✗", e)
    for w in warn:
        print("  ·", w)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))

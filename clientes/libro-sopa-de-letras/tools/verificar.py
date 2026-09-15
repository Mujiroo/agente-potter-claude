#!/usr/bin/env python3
"""Auditoría del interior YA GENERADO (lee el HTML final, no regenera nada).

Revisa, para cada puzzle y su solución:
  - numeración de páginas correlativa y márgenes espejados (par/impar)
  - "PUZZLE N" / "SOLUTION N", frase y lista de palabras idénticas al JSON y entre sí
  - la grilla del puzzle es idéntica a la de su solución
  - 9 contornos en la solución, cada uno sobre la palabra correcta
  - cada palabra aparece exactamente 1 vez hacia adelante y nunca al revés
    (salvo palíndromos o apariciones dentro de otra palabra de la lista)
  - ninguna palabra inapropiada formada por el relleno (lista BAD de generar.py)
  - la página de instrucciones apunta a la página real donde empiezan las soluciones

Uso: verificar.py libro.json interior.html
"""
import html
import json
import math
import re
import sys
from itertools import product

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generar import BAD, DIRS, FORWARD, clean  # noqa: E402


def grid_of(body):
    svg = re.search(r'<svg class="grid"(.*?)</svg>', body, re.S).group(1)
    letters = re.findall(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*>([A-Z])</text>', svg)
    n = int(round(len(letters) ** 0.5))
    g = [[None] * n for _ in range(n)]
    for x, y, ch in letters:
        g[int(float(y) // 40)][int(float(x) // 40)] = ch
    return g


def find(g, word, dirs):
    n = len(g)
    L = clean(word)
    out = []
    for r, c, (dr, dc) in product(range(n), range(n), dirs):
        cells = [(r + dr * k, c + dc * k) for k in range(len(L))]
        if all(0 <= y < n and 0 <= x < n for y, x in cells) and all(
                g[y][x] == L[k] for k, (y, x) in enumerate(cells)):
            out.append(cells)
    return out


def capsules(body):
    """Centro, largo y ángulo de cada contorno de la solución."""
    caps = []
    for m in re.finditer(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" height="30" rx="15"[^>]*'
                         r'transform="rotate\(([-\d.]+) ([-\d.]+) ([-\d.]+)\)"', body):
        x, y, w, ang, cx, cy = map(float, m.groups())
        caps.append((cx, cy, w, ang))
    return caps


def main(src, htm):
    book = json.load(open(src, encoding="utf-8"))
    H = open(htm, encoding="utf-8").read()
    pages = re.findall(r'<section class="page ([^"]*)">(.*?)</section>', H, re.S)
    N = len(book["puzzles"])
    errors, notes = [], []
    nums = [int(m.group(1)) if (m := re.search(r'<div class="num">(\d+)</div>', b)) else None for _, b in pages]
    if nums[1:] != list(range(2, len(pages) + 1)):
        errors.append("numeración de páginas no correlativa")
    for i, (cls, _) in enumerate(pages, 1):
        if (i % 2 == 0) != ("even" in cls):
            errors.append(f"p{i}: margen espejado incorrecto")
    sol_start = 3 + N
    if f"Solutions start on page {sol_start}" not in pages[1][1] and f"start on page {sol_start}" not in pages[1][1]:
        errors.append("p2 no apunta a la página correcta de soluciones")
    if f"SOLUTION 1".lower() not in pages[sol_start - 1][1].lower():
        errors.append(f"la solución 1 no está en la página {sol_start}")

    for i, p in enumerate(book["puzzles"]):
        pp, sp = pages[2 + i][1], pages[2 + N + i][1]
        k = i + 1
        if f"puzzle {k}<" not in pp.lower() or f"solution {k}<" not in sp.lower():
            errors.append(f"#{k}: título/numeración")
        if p.get("phrase"):
            ph = html.escape(p["phrase"])
            if ph not in pp or ph not in sp:
                errors.append(f"#{k}: frase no coincide")
        wl_p = [html.unescape(w) for w in re.findall(r"<li>(.*?)</li>", pp)]
        wl_s = [html.unescape(w) for w in re.findall(r"<li>(.*?)</li>", sp)]
        if wl_p != p["words"] or wl_s != p["words"]:
            errors.append(f"#{k}: lista de palabras distinta")
        gp, gs = grid_of(pp), grid_of(sp)
        if gp != gs:
            errors.append(f"#{k}: grilla del puzzle ≠ grilla de la solución")
        caps = capsules(sp)
        if len(caps) != 9:
            errors.append(f"#{k}: {len(caps)} contornos en la solución")
        placed = {}
        for w in p["words"]:
            fwd = find(gp, w, FORWARD)
            # una palabra contenida en otra de la lista (MEXICO en MEXICO CITY) siempre aparece dentro de
            # ella: esa aparición no cuenta, pero debe existir exactamente UNA aparición propia
            longer = [set(c) for o in p["words"] if o != w and clean(w) in clean(o) for c in find(gp, o, FORWARD)]
            own = [c for c in fwd if not any(set(c) <= L for L in longer)]
            if longer:
                notes.append(f"#{k}: '{w}' también se lee dentro de otra palabra de la lista (esperado)")
                fwd = own
            if len(fwd) != 1:
                errors.append(f"#{k}: '{w}' aparece {len(fwd)} veces hacia adelante")
                continue
            placed[w] = fwd[0]
            back = [c for c in find(gp, w, DIRS) if c not in fwd and set(c) != set(fwd[0])]
            others = [set(c) for o in p["words"] if o != w for c in find(gp, o, FORWARD)]
            if [c for c in back if not any(set(c) <= o for o in others)]:
                errors.append(f"#{k}: '{w}' también se lee al revés")
            # el contorno debe estar sobre la palabra
            (y1, x1), (y2, x2) = fwd[0][0], fwd[0][-1]
            cx, cy = (x1 + x2 + 1) * 20, (y1 + y2 + 1) * 20
            ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
            if not any(abs(a - cx) < 1 and abs(b - cy) < 1 and abs(an - ang) < 0.2 for a, b, _, an in caps):
                errors.append(f"#{k}: contorno de '{w}' no calza")
        inside = [set(c) for c in placed.values()]
        n = len(gp)
        for bw in BAD:
            for cells in find(gp, bw, DIRS):
                if not any(set(cells) <= o for o in inside):
                    errors.append(f"#{k}: palabra inapropiada '{bw}' en el relleno")
                else:
                    notes.append(f"#{k}: '{bw}' dentro de una palabra de la lista (ok)")

    words = [w for p in book["puzzles"] for w in p["words"]]
    dup = sorted({w for w in words if words.count(w) > 1})
    if dup:
        errors.append(f"palabras repetidas entre puzzles: {dup}")
    print(f"páginas: {len(pages)} | puzzles: {N} | palabras: {len(words)} (únicas {len(set(words))})")
    print("ERRORES:", "ninguno" if not errors else "")
    for e in errors:
        print("  -", e)
    for nte in sorted(set(notes)):
        print("  nota:", nte)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))

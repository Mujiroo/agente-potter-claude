#!/usr/bin/env python3
"""Generadores de sudoku y laberintos para los libros híbridos "Calm & Cozy".

Todo se verifica al generar:
  - el sudoku tiene UNA sola solución y la cantidad de pistas del nivel pedido
  - el laberinto es perfecto (un único camino entre entrada y salida, sin ciclos)
    y se guarda su solución
"""
import random


# ---------------------------------------------------------------- sudoku
def _candidates(grid, r, c):
    used = set(grid[r]) | {grid[i][c] for i in range(9)}
    br, bc = 3 * (r // 3), 3 * (c // 3)
    used |= {grid[br + i][bc + j] for i in range(3) for j in range(3)}
    return [n for n in range(1, 10) if n not in used]


def _fill(grid, rng):
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                nums = _candidates(grid, r, c)
                rng.shuffle(nums)
                for n in nums:
                    grid[r][c] = n
                    if _fill(grid, rng):
                        return True
                    grid[r][c] = 0
                return False
    return True


def count_solutions(grid, limit=2):
    """Cuenta soluciones hasta `limit` (para comprobar unicidad)."""
    best = None
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                cand = _candidates(grid, r, c)
                if not cand:
                    return 0
                if best is None or len(cand) < len(best[2]):
                    best = (r, c, cand)
    if best is None:
        return 1
    r, c, cand = best
    total = 0
    for n in cand:
        grid[r][c] = n
        total += count_solutions(grid, limit - total)
        grid[r][c] = 0
        if total >= limit:
            break
    return total


def make_sudoku(rng, givens=38):
    """Devuelve (puzzle, solución). `givens` fija el nivel: 38-40 = fácil."""
    solution = [[0] * 9 for _ in range(9)]
    _fill(solution, rng)
    puzzle = [row[:] for row in solution]
    cells = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(cells)
    removed = 0
    target = 81 - givens
    for r, c in cells:
        if removed >= target:
            break
        r2, c2 = 8 - r, 8 - c  # se quita en pares simétricos, como los libros impresos
        saved = [(r, c, puzzle[r][c])]
        puzzle[r][c] = 0
        if (r2, c2) != (r, c) and puzzle[r2][c2]:
            saved.append((r2, c2, puzzle[r2][c2]))
            puzzle[r2][c2] = 0
        if count_solutions([row[:] for row in puzzle]) != 1:
            for rr, cc, v in saved:
                puzzle[rr][cc] = v
        else:
            removed += len(saved)
    # segunda pasada, celda a celda, para acercarse a la cantidad de pistas pedida
    for r, c in cells:
        if 81 - removed <= givens:
            break
        if puzzle[r][c]:
            v = puzzle[r][c]
            puzzle[r][c] = 0
            if count_solutions([row[:] for row in puzzle]) != 1:
                puzzle[r][c] = v
            else:
                removed += 1
    assert count_solutions([row[:] for row in puzzle]) == 1
    return puzzle, solution


def make_easy_sudoku(rng, max_givens=40, tries=8):
    """Sudoku fácil: reintenta hasta lograr un tablero con pocas pistas y solución única."""
    best = None
    for _ in range(tries):
        puzzle, solution = make_sudoku(rng, givens=max_givens - 4)
        n = sum(1 for row in puzzle for v in row if v)
        if best is None or n < best[0]:
            best = (n, puzzle, solution)
        if n <= max_givens:
            break
    return best[1], best[2], best[0]


def sudoku_svg(puzzle, solution=None, cell=60):
    """Grilla 9x9; si se pasa `solution`, los números añadidos salen en gris."""
    s = 9 * cell
    out = [f'<svg class="sudoku" viewBox="-6 -6 {s+12} {s+12}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect x="0" y="0" width="{s}" height="{s}" fill="#fff"/>']
    for i in range(10):
        w = 7 if i % 3 == 0 else 2.5
        out.append(f'<line x1="{i*cell}" y1="0" x2="{i*cell}" y2="{s}" stroke="#111" stroke-width="{w}" stroke-linecap="square"/>')
        out.append(f'<line x1="0" y1="{i*cell}" x2="{s}" y2="{i*cell}" stroke="#111" stroke-width="{w}" stroke-linecap="square"/>')
    for r in range(9):
        for c in range(9):
            v = puzzle[r][c] or (solution[r][c] if solution else 0)
            if not v:
                continue
            color = "#111" if puzzle[r][c] else "#8A8A8A"
            out.append(f'<text x="{c*cell+cell/2}" y="{r*cell+cell/2}" text-anchor="middle" dominant-baseline="central" '
                       f'font-family="Liberation Sans, Arial" font-weight="700" font-size="{cell*0.62:.0f}" fill="{color}">{v}</text>')
    out.append("</svg>")
    return "".join(out)


# ---------------------------------------------------------------- laberinto
def make_maze(rng, w=17, h=17):
    """Laberinto perfecto (recursive backtracker). Devuelve muros, entrada, salida y solución."""
    walls = [[{"N": True, "S": True, "E": True, "W": True} for _ in range(w)] for _ in range(h)]
    seen = [[False] * w for _ in range(h)]
    stack = [(0, 0)]
    seen[0][0] = True
    opp = {"N": "S", "S": "N", "E": "W", "W": "E"}
    dirs = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
    while stack:
        r, c = stack[-1]
        nxt = [(d, r + dr, c + dc) for d, (dr, dc) in dirs.items()
               if 0 <= r + dr < h and 0 <= c + dc < w and not seen[r + dr][c + dc]]
        if not nxt:
            stack.pop()
            continue
        d, nr, nc = rng.choice(nxt)
        walls[r][c][d] = False
        walls[nr][nc][opp[d]] = False
        seen[nr][nc] = True
        stack.append((nr, nc))
    start, end = (0, 0), (h - 1, w - 1)
    # camino único entre entrada y salida
    prev = {start: None}
    queue = [start]
    while queue:
        cur = queue.pop(0)
        if cur == end:
            break
        r, c = cur
        for d, (dr, dc) in dirs.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and not walls[r][c][d] and (nr, nc) not in prev:
                prev[(nr, nc)] = cur
                queue.append((nr, nc))
    assert end in prev, "laberinto sin salida"
    path = []
    cur = end
    while cur:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return {"walls": walls, "w": w, "h": h, "start": start, "end": end, "path": path}


def maze_svg(maze, solve=False, cell=40, lw=9):
    w, h = maze["w"], maze["h"]
    W, H = w * cell, h * cell
    out = [f'<svg class="maze" viewBox="{-cell-lw} {-lw} {W+2*cell+2*lw} {H+2*lw}" xmlns="http://www.w3.org/2000/svg">']
    if solve:
        pts = " ".join(f"{c*cell+cell/2},{r*cell+cell/2}" for r, c in maze["path"])
        out.append(f'<polyline points="{pts}" fill="none" stroke="#BDBDBD" stroke-width="{cell*0.42:.0f}" '
                   f'stroke-linecap="round" stroke-linejoin="round"/>')
    seg = []
    for r in range(h):
        for c in range(w):
            x, y = c * cell, r * cell
            wl = maze["walls"][r][c]
            if wl["N"]:  # la entrada es sólo por la izquierda (donde apunta la flecha)
                seg.append(f"M{x},{y} h{cell}")
            if wl["W"] and not (r == 0 and c == 0):
                seg.append(f"M{x},{y} v{cell}")
            if r == h - 1 and wl["S"]:  # la salida es sólo por la derecha
                seg.append(f"M{x},{y+cell} h{cell}")
            if c == w - 1 and wl["E"] and not (r == h - 1 and c == w - 1):
                seg.append(f"M{x+cell},{y} v{cell}")
    out.append(f'<path d="{" ".join(seg)}" stroke="#111" stroke-width="{lw}" stroke-linecap="round" fill="none"/>')
    # flechas de entrada y salida
    out.append(f'<path d="M{-cell*0.95},{cell/2} h{cell*0.75} m{-cell*0.3:.1f},{-cell*0.25:.1f} l{cell*0.3:.1f},{cell*0.25:.1f} {-cell*0.3:.1f},{cell*0.25:.1f}" stroke="#111" stroke-width="{lw*0.8}" '
               f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<path d="M{W+cell*0.2},{H-cell/2} h{cell*0.75} m{-cell*0.3:.1f},{-cell*0.25:.1f} l{cell*0.3:.1f},{cell*0.25:.1f} {-cell*0.3:.1f},{cell*0.25:.1f}" stroke="#111" stroke-width="{lw*0.8}" '
               f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append("</svg>")
    return "".join(out)

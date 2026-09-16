# Audita los PDF FINALES (no el HTML): extraer antes con pdf_texto.mjs (node + pdfjs-dist@4) a <carpeta>/<nombre>.json
# Uso: python3 auditar_pdf.py <carpeta_con_json>
import json, re, sys, glob, os
sys.path.insert(0, "/home/agent/workspace/clientes/libro-sopa-de-letras/tools")
from generar import BAD
D8 = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
FWD = [(0,1),(1,0),(1,1),(-1,1)]
S = sys.argv[1]
for jf in sorted(glob.glob(S + "/*interior*.json")):
    d = json.load(open(jf)); pages = d["pages"]; errs = []; notes = []
    name = os.path.basename(jf)[:-5]
    if len(pages) != 112: errs.append(f"{len(pages)} págs")
    if any((p["w"], p["h"]) != (432, 648) for p in pages): errs.append("tamaño distinto de 6x9")
    # numeración
    for i, p in enumerate(pages[1:], 2):
        nums = [t for t in p["items"] if t[0] == str(i) and t[2] < 40]
        if not nums: errs.append(f"p{i}: sin número de página")
    ref = None
    for t in pages[1]["items"]:
        m = re.search(r"Solutions start on page (\d+)", t[0])
        if m: ref = int(m.group(1))
    grids = {}
    for i, p in enumerate(pages, 1):
        hdr = next((t[0] for t in p["items"] if re.fullmatch(r"(PUZZLE|SOLUTION) \d+", t[0])), None)
        if not hdr: continue
        letters = [t for t in p["items"] if re.fullmatch(r"[A-Z]", t[0]) and t[2] > 190]
        n = int(round(len(letters) ** 0.5))
        if n * n != len(letters):
            errs.append(f"p{i} {hdr}: {len(letters)} letras"); continue
        rows = sorted(letters, key=lambda t: -t[2])
        g = []
        for r in range(n):
            row = sorted(rows[r*n:(r+1)*n], key=lambda t: t[1])
            if max(t[2] for t in row) - min(t[2] for t in row) > 3:
                errs.append(f"p{i} {hdr}: fila {r} desalineada"); break
            g.append([t[0] for t in row])
        if len(g) != n: continue
        words = [t[0] for t in p["items"] if t[2] < 200 and t[2] > 40 and len(t[0]) > 1]
        grids[hdr] = (i, g, words)
    npz = sum(1 for k in grids if k.startswith("PUZZLE"))
    nsol = sum(1 for k in grids if k.startswith("SOLUTION"))
    if npz != 55 or nsol != 55: errs.append(f"{npz} puzzles / {nsol} soluciones")
    first_sol = min((v[0] for k, v in grids.items() if k.startswith("SOLUTION")), default=None)
    if ref != first_sol: errs.append(f"p2 dice soluciones en {ref}, están en {first_sol}")
    bad_hits = 0
    for k in range(1, 56):
        if f"PUZZLE {k}" not in grids or f"SOLUTION {k}" not in grids: errs.append(f"falta puzzle/solución {k}"); continue
        pi, g, words = grids[f"PUZZLE {k}"]; si, gs, ws = grids[f"SOLUTION {k}"]
        if g != gs: errs.append(f"puzzle {k}: grilla distinta a su solución")
        if words != ws: errs.append(f"puzzle {k}: lista distinta a su solución")
        if len(words) != 9: errs.append(f"puzzle {k}: {len(words)} palabras")
        n = len(g)
        def count(w, dirs):
            c = 0
            for r in range(n):
                for q in range(n):
                    for dr, dc in dirs:
                        if all(0 <= r+dr*j < n and 0 <= q+dc*j < n and g[r+dr*j][q+dc*j] == w[j] for j in range(len(w))): c += 1
            return c
        clean = [re.sub(r"[^A-Z]", "", w.upper()) for w in words]
        for w in clean:
            f = count(w, FWD)
            if f < 1: errs.append(f"puzzle {k}: {w} no está")
            elif f > 1 and not any(w != o and w in o for o in clean): errs.append(f"puzzle {k}: {w} aparece {f} veces")
            back = count(w[::-1], FWD) if w != w[::-1] else 0
            if back and not any(w[::-1] in o for o in clean): notes.append(f"puzzle {k}: {w} también al revés")
        for b in BAD:
            if count(b, D8):
                if any(b in o or b[::-1] in o for o in clean): continue
                bad_hits += 1; errs.append(f"puzzle {k}: relleno forma '{b}'")
    print(f"{name}: págs {len(pages)} · puzzles {npz} · soluciones {nsol} · p2→{ref} · errores {len(errs)} · avisos {len(notes)}")
    for e in errs[:15]: print("   ✗", e)
    for e in notes[:8]: print("   ·", e)

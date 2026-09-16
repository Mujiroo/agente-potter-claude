#!/usr/bin/env python3
"""Chrome redondea el tamaño de página a píxeles CSS enteros (1/96"), así que una portada
KDP puede quedar unas milésimas más ancha de lo que exige el cálculo del lomo.
Esto fija el ancho exacto del MediaBox sin tocar el contenido (el sobrante cae en el sangrado).
Sólo reescribe si el número nuevo ocupa los mismos bytes (no rompe la tabla xref).

Uso: ajustar_mediabox.py archivo.pdf ancho_pulgadas alto_pulgadas
"""
import re
import sys

path, w_in, h_in = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
data = open(path, "rb").read()
m = re.search(rb"/MediaBox \[0 0 ([\d.]+) ([\d.]+)\]", data)
old = m.group(0)
w_old, h_old = m.group(1), m.group(2)
w_new = f"{w_in*72:.{max(0, len(w_old.split(b'.')[1]) if b'.' in w_old else 0)}f}".encode()
h_new = f"{h_in*72:.{max(0, len(h_old.split(b'.')[1]) if b'.' in h_old else 0)}f}".encode()
new = b"/MediaBox [0 0 " + w_new + b" " + h_new + b"]"
if len(new) != len(old):
    sys.exit(f"no cabe sin rehacer la xref: {old!r} -> {new!r}")
open(path, "wb").write(data.replace(old, new, 1))
print(f"{old.decode()} -> {new.decode()}")

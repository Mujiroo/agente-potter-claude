#!/usr/bin/env python3
"""Chrome redondea el tamaño de página a píxeles CSS enteros (1/96"), así que una portada
KDP puede quedar unas milésimas más ancha o más angosta de lo que exige el cálculo del lomo.
Esto fija el MediaBox exacto sin tocar el contenido (la diferencia cae en el sangrado exterior)
y, si el número cambia de largo, rehace la tabla xref clásica y el startxref.

Uso: ajustar_mediabox.py archivo.pdf ancho_pulgadas alto_pulgadas
"""
import re
import sys


def fmt(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s.encode()


def main(path, w_in, h_in):
    data = open(path, "rb").read()
    boxes = re.findall(rb"/MediaBox \[0 0 [\d.]+ [\d.]+\]", data)
    if len(boxes) != 1:
        sys.exit(f"esperaba 1 MediaBox y hay {len(boxes)}")
    old = boxes[0]
    new = b"/MediaBox [0 0 " + fmt(w_in * 72) + b" " + fmt(h_in * 72) + b"]"
    if old == new:
        print("ya estaba exacto:", old.decode())
        return
    data = data.replace(old, new, 1)
    if len(old) != len(new):
        # rehacer xref: offsets de cada "N 0 obj"
        m = re.search(rb"\nxref\n0 (\d+)\n", data)
        if not m or b"/Type /XRef" in data:
            sys.exit("el PDF no usa xref clásica; no se modifica")
        n = int(m.group(1))
        offsets = {int(o.group(1)): o.start() for o in re.finditer(rb"(?m)^(\d+) 0 obj", data)}
        xref_start = m.start() + 1
        table = [b"xref\n", f"0 {n}\n".encode(), b"0000000000 65535 f \n"]
        for i in range(1, n):
            if i not in offsets:
                sys.exit(f"falta el objeto {i}")
            table.append(f"{offsets[i]:010d} 00000 n \n".encode())
        end_table = data.index(b"trailer", xref_start)
        data = data[:xref_start] + b"".join(table) + data[end_table:]
        data = re.sub(rb"startxref\n\d+", b"startxref\n" + str(xref_start).encode(), data)
    open(path, "wb").write(data)
    print(f"{old.decode()} -> {new.decode()}")


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))

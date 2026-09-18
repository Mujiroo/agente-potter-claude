#!/usr/bin/env python3
"""PDF de revisión: frente de la portada + interior completo + contratapa, en orden de lectura (8,5×11, sin sangrado).
Sólo para revisar; a KDP se suben por separado el interior y la portada completa.

Uso: revision_es.py libro.json interior.html salida.html
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import portada_final_es as PF  # noqa: E402

book = json.load(open(sys.argv[1], encoding="utf-8"))
PF.set_volumen(book)
doc = open(sys.argv[2], encoding="utf-8").read()
b = PF.BLEED * PF.U
tw, th = book["trim"]
vb = f'{b} {b} {tw*PF.U} {th*PF.U}'
H = (th + 2 * PF.BLEED) * PF.U
front = PF.front(0, PF.V2.W, H)
back = PF.back(0, PF.V2.W, H, book["cover_full"], trim_right=b + tw * PF.U)
page = ('<section class="cover-page" style="width:{w}in;height:{h}in;page-break-after:always;overflow:hidden">'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" style="display:block;width:{w}in;height:{h}in">{svg}</svg></section>')
css = PF.font_css() + PF.V2.fonts_css() + re.search(r"\.backtext \{\{.*?\n</style>", open(PF.__file__).read(), re.S).group(0)[:-9]
css = css.replace("{{", "{").replace("}}", "}").replace("{OSC}", PF.OSC).replace("{ROJO}", PF.ROJO)
doc = doc.replace("<style>", f"<style>{css}", 1)
doc = doc.replace("<body>", "<body>" + page.format(w=tw, h=th, vb=vb, svg=front), 1)
doc = doc.replace("</body>", page.format(w=tw, h=th, vb=vb, svg=back) + "</body>", 1)
open(sys.argv[3], "w", encoding="utf-8").write(doc)
print("->", sys.argv[3])

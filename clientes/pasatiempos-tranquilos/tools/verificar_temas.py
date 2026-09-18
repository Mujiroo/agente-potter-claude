#!/usr/bin/env python3
"""Verifica las listas de temas_serie.py: cantidad, largo, caracteres, repetidas, contenidas y groserías."""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from temas_serie import VOLS  # noqa: E402

MAX = 13
# Groserías y dobles sentidos regionales en español (Latinoamérica + España), sin tildes.
BAD_ES = ("PUTA PUTO CULO COÑO VERGA PENE PICHULA PIJA POLLA CONCHA CHUCHA CHOCHO CHOCHA CAJETA PAPAYA PENDEJ PINCHE "
          "CABRON JODER JODID MIERDA CAGAR CAGAD MAMAR MAMADA COGER COJON HUEVON HUEVO MARICA MARICON JOTO PUÑETA "
          "CARAJO CHINGA ORTO POTO CACHAR TETA TETAS ZORRA PERRA GUARRA MAMON CULIAO CULEAR BOLUDO PELOTUDO SORETE "
          "CHIMBA GONORREA MALPARID CAPULLO GILIPOLL NALGA PEDO MEAR ESTUPID IDIOTA IMBECIL NAZI").split()
# Sólo para el RELLENO de la grilla (no para las listas): palabras que el azar puede formar y que
# son vulgares en alguna región (PICO en Chile, CHOTA en Perú/Argentina, TOTA y BICHO en Puerto Rico) o de mal gusto. CACA vive
# dentro de CACAO, por eso no va en BAD_ES (marcaría la palabra de la lista). Revisión del 18-sep-2026.
BAD_RELLENO = ("PICO CHOTA CACA PAJA PICHA MOCO CAGON CUCA PITO TOTA PINGA BICHO OJETE CULERO SEXO").split()


def main():
    ok = True
    seen = {}
    for vol, areas in VOLS.items():
        temas = [t for a in areas.values() for t in a]
        if len(temas) != 40:
            print(f"ERROR {vol}: {len(temas)} temas"); ok = False
        for tema, words in temas:
            if len(words) != 9:
                print(f"ERROR {tema}: {len(words)} palabras"); ok = False
            for w in words:
                letters = w.replace(" ", "")
                if len(letters) > MAX:
                    print(f"LARGO {tema}: {w} ({len(letters)})"); ok = False
                if not re.fullmatch(r"[A-ZÑ ]+", w):
                    print(f"CARACTER {tema}: {w}"); ok = False
                if w in seen:
                    print(f"REPETIDA {w}: {seen[w]} / {tema}"); ok = False
                seen[w] = tema
                for b in BAD_ES:
                    if b in letters:
                        print(f"GROSERIA? {tema}: {w} contiene {b}"); ok = False
            ls = [w.replace(" ", "") for w in words]
            for a in ls:
                for b in ls:
                    if a != b and a in b:
                        print(f"CONTENIDA {tema}: {a} en {b}"); ok = False
    print(f"{len(seen)} palabras únicas ·", "OK" if ok else "CON ERRORES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

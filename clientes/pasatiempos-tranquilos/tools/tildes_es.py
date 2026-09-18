"""Ortografía de la LISTA de palabras (Pedro, 18-sep-2026, msg 1080: opción A).

La grilla va sin tildes (una «Á» sería una pista), pero la lista bajo la grilla se escribe
bien: en español las mayúsculas llevan tilde (RAE). «Cómo jugar» avisa que en la grilla van
sin tildes. temas_serie.py guarda las palabras SIN tildes (así se arma la grilla); aquí está
la forma correcta de cada una que la lleva. Revisada palabra por palabra.
"""
import unicodedata

ACENTOS = {w.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U").replace("Ü", "U"): w for w in """
ACORDEÓN AJÍ ALCALDÍA ALEGRÍA ALGODÓN ALMIDÓN ANDÉN ANÉCDOTAS ÁNGEL ANÍS ARÁBICA ARCOÍRIS ARMONÍA AZADÓN AZAFRÁN
BAHÍA BALCÓN BANDONEÓN BASTÓN BEBÉ BENDICIÓN BENJAMÍN BIBERÓN BÚHO BUZÓN CAFÉ CÁLIZ CALLEJÓN CÁMARA CAMARÓN CAMISÓN
CANAPÉS CANCIÓN CAPÍTULO CARBÓN CELEBRACIÓN CEMPASÚCHIL CHACHACHÁ CHICHARRÓN CIGÜEÑA COLIBRÍ COMPÁS COMPAÑÍA
CÓMPLICES CÓNDOR CONSOMÉ CONSTELACIÓN COREOGRAFÍA CORAZÓN CORBATÍN CORTESÍA CRÁTER CUCHARÓN DANZÓN DEDICACIÓN
DIVERSIÓN DOMINÓ DRAGÓN EDREDÓN ENERGÍA ESTACIÓN ÉXITO FÁBULA FOGÓN FOTÓGRAFO FRÍO GALÁN GRADUACIÓN GORRIÓN
GUANÁBANA GUAYACÁN GUÍA GÜIRA GUITARRÓN HÉROE ILUSIÓN JABÓN JARDINERÍA JAZMÍN JONRÓN LÁMPARA LECHÓN LIMÓN LOTERÍA
LUCIÉRNAGA MALETÍN MANGÚ MARACUYÁ MÁSCARAS MAZAPÁN MELODÍA MELÓN MICRÓFONO MÚSICA ORACIÓN ORÉGANO ORQUÍDEA PABELLÓN
PATACÓN PASIÓN PELÍCULA PEPIÁN PERDÓN PIZARRÓN PLÁTANO POLVORÓN PRÓCERES PROCESIÓN PROPÓSITOS PRIMOGÉNITO RAÍCES
RELAJACIÓN RESURRECCIÓN ROCÍO ROMÁNTICO ROPÓN SÁBANAS SÁBILA SALÓN SANDÍA SARTÉN SAXOFÓN SAZÓN SILLÓN SOFÁ TAZÓN
TÍAS TÍOS TÍTULO TOBOGÁN TÓMBOLA TUCÁN UNGÜENTO UNIÓN VAGÓN VIGORÓN VIOLÍN VOLCÁN ZAGUÁN YOYÓ
""".split()}
ACENTOS.update({k.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U"): k for k in [
    "BAJO ELÉCTRICO", "BUEN ÁRBOL", "CAFÉ CON LECHE", "CINTA MÉTRICA", "DELFÍN ROSADO", "HABÍA UNA VEZ",
    "MANÍ TOSTADO", "PÁJARO EN MANO", "TÉ VERDE", "VÍA LÁCTEA"]})


def sin_tildes(w):
    """Quita tildes y diéresis pero conserva la Ñ."""
    out = []
    for c in w:
        if c in "Ññ":
            out.append(c)
        else:
            out.append("".join(x for x in unicodedata.normalize("NFD", c) if unicodedata.category(x) != "Mn"))
    return "".join(out)


def con_tildes(w):
    return ACENTOS.get(w, w)


assert all(sin_tildes(v) == k for k, v in ACENTOS.items()), "clave y forma con tilde no calzan"

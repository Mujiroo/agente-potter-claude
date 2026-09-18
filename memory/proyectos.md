# Proyectos de Pedro

- **Libros de sopa de letras (Amazon KDP)**, con Adri. Serie **Big Print Word Hunt**, autor "Peter & Cardu".
  - Vol. 1 *Word Search: Aisle Hunt!* (supermercado): edición cerrada el 2026-09-15.
    - Estado y decisiones: `clientes/libro-sopa-de-letras/estado.md`.
    - Archivos finales: `clientes/libro-sopa-de-letras/entregables/vol1/` (interior v11 + portada v7).
    - Herramientas reutilizables para la serie: `clientes/libro-sopa-de-letras/tools/` (`generar.py`, `portada.py`, `portada_alt.py`, `verificar.py`).
  - Pendiente del Vol. 1: parte KDP (descripción, palabras clave, categorías, precio).
  - Vol. 2 *World Hunt!* (países, capitales y ciudades), Vol. 3 *USA Hunt!* (50 estados), Vol. 4 *Memory Lane Hunt!* (nostalgia 50–80), Vol. 5 *Christmas Hunt!*: armados, verificados y **aprobados por Pedro el 2026-09-15**. Archivos en `entregables/volN/`.
  - Vol. 5 Christmas debe estar publicado antes de fines de octubre (temporada).
  - Idea en evaluación: planner navideño tipo calendario de adviento ("Christmas Countdown Planner & Puzzle Book").
  - Reglas aprendidas para la serie:
    - buscar el nombre en Amazon antes de fijarlo
    - medir que la lista quepa en 3 columnas a 14 pt
    - sin marcas ni personajes registrados
    - filtro de palabras ofensivas
    - p1 en grises
    - sin fuentes Type 3

- **Pendiente al editar cualquier libro en inglés** (Pedro, 18-sep-2026, msg 1047: «los regeneramos al momento de editarlos»):
  - Regenerar con el filtro ampliado en español (`pasatiempos-tranquilos/tools/verificar_temas.py`: BAD_ES + BAD_RELLENO) sumado al BAD en inglés.
  - Hallazgos del barrido del 18-sep: Calm & Cozy (PAJA, WEON, MOCO) · Aisle Hunt 1 (TETA, ORTO, CACA, PAPO) · World Hunt 2 (TETA, PEDO, TOTA) · USA Hunt 3 (PENE, PAJA, WEON, MEAR, TOTO) · Memory Lane 4 (TETA, TOTA, PAPO, MOCO, TONTO, BOBO) · Christmas Hunt 5 (PENE, ORTO, TOTO).
  - 18-sep: preparadas ediciones 2 de Calm & Cozy, Vol. 4 y Vol. 5 (entregables/*edicion2). Falta que Pedro las suba. Vol. 1 Aisle (¿publicado?), Vol. 2 World y Vol. 3 USA: regenerar antes de subir (cierre `closing` propio, filtro ES, semillas de textura nuevas). Pendiente de decidir: listas a 14 pt en 6×9.
  - Detalle en `clientes/libro-sopa-de-letras/estado.md`. Ver [[checklist-revision]].

Ver [[pedro]], [[preferencias]].

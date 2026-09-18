---
name: checklist-revision
description: Lista de revisión exhaustiva para libros de pasatiempos KDP (lo que Pedro espera cuando pide «revisar»)
metadata:
  type: feedback
---

Pedro pide que toda revisión sea exhaustiva (msg 1033, 18-sep-2026). Ver [[preferencias]].

**Why:** una revisión solo técnica dejó pasar groserías regionales en el relleno de las grillas.

**How to apply:** recorrer todos los bloques y decir cuáles se revisaron.

## Texto y redacción
- Trato uniforme (tú o usted) en todas las páginas, contratapa y ficha.
- Repeticiones de palabras en un mismo párrafo o página (p. ej. «gracias… agradeceríamos», «tranquilos»).
- Mayúsculas según la RAE: en títulos, solo la primera palabra y los nombres propios. Las festividades y colecciones sí llevan mayúscula.
- Frases que se entienden a la primera, para adultos mayores; nada de «Nunca al revés» sin explicar.
- Que el interior avise que las palabras van sin tildes y que las compuestas van juntas.
- Números citados: la página de soluciones y los conteos (40/20/10 = 70) coinciden con el libro.

## Listas de palabras
- Casi repetidas dentro del libro (TARJETA/TARJETAS, VELA/VELAS) y repetidas en la serie.
- Palíndromos (ORO): rompen la regla de no leerse al revés.
- Regionalismos y dobles sentidos en toda Latinoamérica.
- Anglicismos en títulos de temas.

## Grillas (relleno al azar)
- Groserías en inglés y en español, con jerga regional: Chile (PICO), Perú y Argentina (CHOTA), Puerto Rico (TOTA, BICHO), Venezuela y Colombia (CUCA), además de CACA, CAGON, PITO, etc. Se revisan en las 8 direcciones.
- Filtro en `verificar_temas.BAD_ES` (listas) y `BAD_RELLENO` (solo relleno).
- Barrido extra con una lista más amplia antes de dar por buena la revisión.

## Puzzles
- Correr el verificador: solución única, soluciones bien marcadas, nada leído al revés.
- Sudokus y laberintos distintos entre volúmenes.
- Mirar a ojo al menos un puzzle con palabras largas y su solución.

## Diseño e interior
- Márgenes sobre el mínimo de KDP, medidos con agent-browser.
- Nada fuera de página, nada cortado.
- Fuentes incrustadas, 0 Type3 y 0 imágenes rasterizadas.
- MediaBox exacto.

## Portada
- Medidas y lomo según las páginas y el tipo de papel.
- Zona segura.
- Texto del lomo a ≥ 0,0625" de cada borde.
- Espacio del código de barras libre.
- Coherencia frente/contratapa/interior.

## KDP
- Ficha completa: título igual al de la portada, serie, palabras clave, categorías, papel, declaración de IA y precio.
- Captura del previsualizador antes de publicar.

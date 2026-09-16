# Calm & Cozy Puzzles (libro híbrido) — estado

## Qué es
Idea de Pedro (2026-09-15): libro mixto **40 sopas + 20 sudokus fáciles + 10 laberintos**, subnicho de calma/anti-estrés, estética acogedora. **Serie nueva**, en **inglés**, autor Peter & Cardu.

## Decisiones
- Idioma inglés; serie nueva; yo amplío los 10 bloques de Pedro a 40 temas (msg 312).
- Tamaño **8,5×11"** (los sudokus y laberintos piden más espacio).
- "Bold & Easy" se usa como **estilo**, no como palabra clave (la dominan los libros para colorear).

## Estilo de portada (investigado el 2026-09-15)
Los libros del subnicho que están hoy en el top 100 (Calming Mindfulness #12, Cozy Autumn #18, Brain Games Calm #26, Spooky Halloween #65, Peaceful Wildlife #94) comparten: fondo crema, ilustración cálida, tipografía con serifas o manuscrita, trozo de sopa de letras, sello LARGE PRINT y paleta apagada. Se venden a **US$ 12,98–13,99**, contra 5,99–9,99 de los de estilo "gritón".

## Herramientas
- `tools/puzzles.py`: sudoku (solución única verificada, 37–40 pistas) y laberintos perfectos con solución.
- `tools/generar_mixto.py`: arma el interior (secuencia 4 sopas → 1 sudoku; cada 4 sudokus → 1 laberinto; soluciones al final, sudokus y laberintos de a dos por página). Reutiliza `build`, `grid_svg` y `words_block` del generador de sopas.
- `tools/portada_cozy.py`: portada estilo cozy (taza con sopa de letras, libro y manta, ramitas, sello, franja LARGE PRINT). Fuentes Playfair Display y Caveat (OFL) en `tools/fonts`.

## Estado
- **Muestra enviada** (msgs 324–326): 12 páginas (2 sopas, 2 sudokus, 1 laberinto + soluciones) y la portada frontal. Sin desbordes, sin Type3, 8,5×11.
- Pendiente: OK de Pedro para armar el libro completo (40 temas, ~120 págs., portada con lomo y contraportada).
- 00:20 (16-sep) Pedro: revisará mañana las opciones A/B de portada y la muestra del interior.
- 00:21 Pedro pide **5 opciones de portada distintas** (algunas fuera del estilo cozy), parecidas a las que más éxito tienen en Amazon, para revisar **mañana 16-sep a las 8:00**.
- 01:15 (16-sep) Enviadas **5 portadas** (msgs 333+): 1 cozy, 2 números, 3 ventana, 4 sobria, 5 moderna. Generador: `tools/portadas_opciones.py`; PNG en `entregables/portadas/`.
  - Recomendé la 5 (moderna) y, como alternativa segura, la 3 (ventana).
- 00:28 Pedro pide **5 portadas más, más clásicas**, y que revise si se me pasa algo. Retoma a las 8:00.
- 00:40 Enviadas las **5 clásicas** (msgs 344–352): 6 revista, 7 biblioteca, 8 diario, 9 barra de color, 10 colcha. Generador: `tools/portadas_clasicas.py`; PNG y `hoja_clasicas.png` (comparativa + las 10 en miniatura) en `entregables/portadas/`.
  - Corregidos solapes en 6, 8 y 9 (el laberinto pisaba la banda inferior y el sudoku) y las esquinas dobles de la orla de la 10.
  - Recomendé la **9** como apuesta clásica segura y la **6** si se quiere la palabra clave en el título; mi favorita sigue siendo la 5 (moderna).
- Tres cosas que levanté en la revisión y **Pedro debe decidir**:
  1. Las opciones 6–9 **no llevan el nombre de serie "Calm & Cozy"**. Definir si el nombre va en portada o la serie la hace el estilo.
  2. Las portadas que sólo dicen "PUZZLES" (7 y 10) pierden la palabra que se busca en Amazon. El **título en KDP** debería ser explícito ("Large Print Word Search, Sudoku & Mazes for Adults") aunque la portada diga algo más corto.
  3. La **10 no muestra sudoku ni laberinto**; si le gusta, hay que agregárselos.
- 00:41 Pedro: "hablamos a partir de las 8:00 am", se fue a dormir. No escribirle hasta esa hora.

## Pendientes generales (al 16-sep 00:45)
1. Elegir portada (1–10) y armar la completa: frente + lomo + contratapa.
2. Pedro debe revisar el interior de muestra (12 págs.).
3. Vol. 1–5: falta el listado KDP (descripción, 7 keywords, categorías, precio). Partir por el Vol. 5 Christmas por temporada. Declaración de IA: texto sí, imágenes no. Máx. 3 títulos nuevos por 24 h.
4. Ofrecimiento abierto: borrar definitivamente los 8 correos que quedaron en Eliminados de Hotmail.
5. Sin luz verde todavía: Christmas Countdown Planner y prueba del libro para colorear.

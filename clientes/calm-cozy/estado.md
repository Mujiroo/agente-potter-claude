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

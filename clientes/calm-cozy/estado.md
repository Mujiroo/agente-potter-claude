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

## 2026-09-16 01:15 · Libro completo generado (a la espera del OK de portada)
- `libro1_calm_cozy.json`: los **40 temas**, ampliando los 10 bloques de Pedro (Mañanas Acogedoras → Cozy Mornings, etc.) con 30 más en la misma línea. 9 palabras cada uno, ninguna repetida ni contenida en otra dentro del mismo puzzle.
- Interior generado y auditado con `tools/verificar_mixto.py` (nuevo): **128 páginas**, 40 sopas + 20 sudokus + 10 laberintos, **0 errores, 0 avisos**, sin desbordes, 0 Type3.
- PDF en `entregables/CalmCozy_Vol1_interior_8.5x11.pdf`. Lomo con 128 págs. en papel blanco: **0,288"**.
- Falta sólo que Pedro elija la portada para armar frente + lomo + contratapa.

## 2026-09-16 · Mañana
- 08:19–08:48 Pedro escribió y no le respondí: estuve caído hasta las ~09:04. Me lo reclamó.
- msg 358: **nunca ingresar con claves a ningún sitio sin preguntarle** (anotado en memory/preferencias.md).
- msg 359: le gusta la **portada 5 (moderna)**; pide verla **en otros colores**.
- msg 363: le gusta el interior; pide **mejorar la p2** como en los otros libros, mostrársela y después seguir con el resto.
- 09:10 Enviada la **p2 nueva** (msgs 367–368): `tools/pagina2.py` (`instructions_style: "icons"` en el JSON). Tiene «belongs to», How to Play, 3 tarjetas con mini ejemplo e íconos (sopa, sudoku y laberinto), aviso de soluciones en la pág. 73 y copyright.
  - Auditoría: 128 págs., 0 errores, sin salirse de márgenes, 0 Type3. El PDF vigente quedó en `entregables/`.
  - Esperando su OK.
- 09:12 Enviada la **portada 5 en 6 paletas** (hoja `entregables/portadas/hoja_moderna.png`, generador `tools/portada_moderna_colores.py`; `front_modern` ahora acepta `pal`). A es la original (PNG idéntico byte a byte).
  - Paletas: A petróleo/mostaza, B marino/coral, C terracota/amarillo, D salvia/rosa, E ciruela/dorado, F azul/amarillo.
  - Recomendé la B; como alternativa, la C.
  - Defecto detectado: el laberinto mini queda tapado por la franja LARGE PRINT (también en la original). Se corrige en la elegida.
  - Esperando que elija.

## 2026-09-16 10:30 · Vol. 1 FINAL (esperando aprobación)
- Pedro (msg 440): aprueba el interior; portada = la que recomendé (moderna **B, marino y coral**) «por el momento». msg 443: que quede claro que son **3 tipos de juegos**. msg 442: revisar varias veces.
- `tools/portada_final.py`: portada completa (contratapa + lomo + frente). Tiene la cinta «3 KINDS OF PUZZLES IN ONE BOOK» y 3 tarjetas rotuladas con cantidades.
  - La textura de letras queda recortada a su bloque.
  - El sudoku decorativo es real (`make_easy_sudoku`); antes tenía números repetidos.
  - El laberinto ya no queda tapado por la franja. Además lo corregí en `portadas_opciones.front_modern`.
- `tools/ajustar_mediabox.py`: Chrome redondea la página a px CSS; la portada salía 17,5433" y quedó en 17,5383" exactos.
- Verificado:
  - Portada: zona segura (0,125" desde el corte, lomo con 0,0625" por lado), código de barras libre (2×1,2" abajo a la derecha), sin choques, 0 groserías en texturas y mini sopa, 0 Type3, miniaturas legibles.
  - Interior: PDF de 128 págs. a 612×792. Las 40 sopas coinciden con su solución, cada palabra 1 vez, 0 al revés, 0 groserías. p2→73 correcto. Todo en grises.
- Archivos: `entregables/vol1_final/` (cover PDF, interior PDF, previews). Enviados msgs 447–451.
- 10:35 Pedro (msg 456): el Calm & Cozy **se queda en 8,5×11**, como le recomendé (msg 455). A 8,5×11 y US$ 12,99 le quedan ~US$ 4,62 por libro; en 6×9 a 9,99, ~US$ 3,30. Posible versión 6×9 aparte más adelante.
- Sigue pendiente su OK explícito a los PDF finales (msgs 449–451).

## 2026-09-16 11:00 · Revisión experta (msg 458) → v2
Pedro pidió revisar todo como editor y experto en juegos. La v1 quedó en `entregables/vol1_v1/` y en `libro1_calm_cozy_v1.json`. La v2 está en `entregables/vol1_v2/` y en `libro1_calm_cozy.json`.
- **Bugs**:
  - Flechas de los laberintos fuera del viewBox (no se veían), y la entrada tenía 2 aberturas. Corregido en `puzzles.maze_svg`; `verificar_mixto` ahora lo detecta (la v1 da 20 errores).
- **Editorial**:
  - 34 palabras repetidas entre sopas → 0.
  - 4 temas casi duplicados → Picnic Day, Sewing Box, Library Visit, Pot of Soup.
  - POLAROID (marca) → SNAPSHOT; GREY → GRAY; FISH NETS → FISHING NETS.
  - En total, 89 palabras distintas a la v1.
- **Maqueta**:
  - Portadilla nueva con fuentes y los 3 mini ejemplos.
  - Sudoku (7") y laberinto centrados.
  - Laberintos ordenados por largo del camino.
  - Divisor «Solutions».
  - Soluciones: 6 sudokus y 4 laberintos por página → **120 págs.** (impresión US$ 3,04 en vez de 3,18).
- **Portada**: page_count 120, lomo 0,2702", 17,5202 × 11,25". EXTRA = 3 unidades de fondo por el borde exterior para que `ajustar_mediabox` recorte sin dejar franja blanca.
  - Nota: en las 5 portadas 6×9 el ajuste agregó 0,0022" sin contenido en el sangrado exterior, que se corta al imprimir.
- **Verificado**:
  - Sudokus con solución única y resolubles sólo con singles (verificador nuevo).
  - Sopas en el PDF: 1 vez cada palabra, 0 al revés, 0 groserías, puzzle = solución.
  - 0 desbordes en las 120 págs. (control en el navegador), grises, 0 Type3, zona segura y código de barras libre.
- **Pendiente de Pedro**:
  - Aprobar la v2 (msgs 464–470).
  - Decidir A/B/C sobre la densidad de las sopas (9 palabras en 15×15, 76 % relleno). Recomendé C: 13×13.

## 2026-09-16 11:10 · Instrucciones
- msg 474–482: Pedro aprobó el texto más claro del sudoku en la p2 («Every row, column and 3×3 box must have the numbers 1 to 9», «No number repeats in a row, column or box», pie «This box is missing a 7»). Ya está en `tools/pagina2.py`; **faltan los PDF regenerados**.
- msg 478: pidió ver cómo explican las reglas los libros del rubro. Las editoriales grandes (Brain Games de PIL, Ultimate Brain Health de Callisto) traen instrucciones y consejos por tipo de juego, con un «warm-up».
  - Propuesta enviada (msg 487): p3 «Helpful Tips» (`pagina2.page3`, activa con `"tips_page": true`; hoy no está activa en el JSON) + página final «Thank you» con invitación a reseña (sin incentivos) para dejar 122 págs. La p3 NO la aplico sin su OK.
- msg 483–484: ¿listo para publicar? Respondí que todavía no. Faltan:
  - decisiones: tips sí/no y densidad A/B/C (recomendé C, 13×13)
  - PDF finales + revisión final sobre esos PDF
  - ficha KDP
  - Recomendé una copia de prueba impresa.

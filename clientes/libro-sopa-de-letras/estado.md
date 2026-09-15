# Libro de sopa de letras (Pedro y Adri)

## Estado — 2026-09-15
- Proyecto para publicar un libro de sopa de letras; Pedro pedirá trabajo en Canva.
- Preguntó si puedo usar **Book Bolt** (bookbolt.io, herramienta para libros tipo KDP).
  - Composio no tiene toolkit de Book Bolt (verificado).
  - agent-browser: bookbolt.io devuelve bloqueo de **Cloudflare** ("Attention Required").
  - Usarlo requeriría login de Pedro (credenciales solo vía /env, nunca por chat).
- Le ofrecí alternativa: generar las sopas de letras (grilla, palabras, soluciones) en PDF + portada/interiores en Canva.
- Pendiente: que diga para qué usan Book Bolt (puzzles, portada o keywords de Amazon).

## Portada — 2026-09-15 08:40
- Pedido: portada en Canva, tema **supermercado**, estilo **fun pero profesional**, que se diferencie pero se entienda que es sopa de letras. Libro en **inglés**.
- Generé con Canva AI (canva_mcp, tipo poster) 4 candidatas; título de trabajo **"AISLE HUNT! Supermarket Word Search"**, banda "100+ Fun Puzzles from Aisle 1 to Checkout", "Large Print".
- Guardadas en el Canva de Pedro:
  - DAHVQyjvkOw — Opción 1 (recomendada, la más completa) — https://www.canva.com/d/N_yXGP-JUBv-wUi
  - DAHVQz-shcM — Opción 2 (llamativa; texto sobrante "BRIGHT & YELLOW", sin subtítulo) — https://www.canva.com/d/RP9LtjOYjl1t2QF
  - DAHVQw41Dcw — descartada (grilla ilegible, cinta vacía)
  - DAHVQ1RlCfI — no se pudo exportar/revisar
- Problema en todas: la IA dibuja letras ilegibles en lupa/carro → reemplazar por grilla real antes de imprimir.
- Preview de canva.ai bloqueado por Cloudflare en agent-browser; se revisó exportando PNG por API.
- Pendiente de Pedro: opción elegida, título final, cantidad de puzzles, plataforma (¿KDP?), tamaño y n.º de páginas (para lomo y contraportada).

## Interior — 2026-09-15 09:08
- Pedro pregunta si puedo hacer el libro con **55 puzzles** a partir de una lista, en Canva.
- Respondí: sí. Genero los puzzles y las soluciones en un PDF de interior (KDP). Pedro lo sube a Canva (se abre editable).
  - No importar directo: CANVA_MCP_IMPORT_DESIGN_FROM_URL exige un enlace público. No publicar sin que Pedro lo pida sabiendo que queda expuesto.
- Pendiente de Pedro: lista (por tema/puzzle o general), tamaño (¿8,5×11"?), letra grande 15×15 o normal 20×20, soluciones al final.
- 09:18 Pedro aprueba: le mando el PDF y él lo sube a Canva.
- Defaults propuestos (msg 25) si no dice otra cosa: 8,5×11", grilla 15×15 letra grande, 1 puzzle por página con título del tema, soluciones al final.
- Esperando: **la lista** de palabras.

## Especificación del interior — 2026-09-15 09:41 (Pedro, msg 26)
- Pedro envía listado de **55 puzzles**, cada uno con **9 palabras**.
- **Letra grande**. Bajo la grilla: **3 columnas × 3 palabras**, en el orden de la lista (no revolver).
- **112 páginas** + portada y contraportada:
  - p1: igual a la portada, sobre fondo blanco (página de título)
  - p2: instrucciones (en inglés)
  - p3–57: los 55 puzzles
  - p58–112: las 55 soluciones (al final)
- Libro en **inglés**.
- **Serie**: Pedro hará más libros → la portada debe ser una **plantilla genérica** que se reutilice cambiando la temática de cada libro.
- Esperando: el listado.

## Libro 1 (supermercado) — interior entregado 2026-09-15 ~10:00
- Listado de Pedro: Excel `Supermercado`, col. A, 55 bloques de 9 palabras separados por fila vacía (sin nombres de tema). Datos en `libro1_supermercado.json`.
  - Antes mandó otro archivo (msg 29) y dijo que era "para otro libro": ignorado.
- Generador reutilizable para la serie: `tools/generar.py libro.json salida.html`, y luego `agent-browser open file://…html` + `agent-browser pdf …`.
  - 8,5×11", márgenes 0,75", grilla 15×15, 8 direcciones, seed fija (2026), 3 columnas de palabras en el orden de la lista.
  - Verifica que cada palabra aparezca exactamente 1 vez (con la primera seed hubo 2 dobles: HAM y APPLE; se corrigió).
  - Sin pip en el contenedor: el PDF se hace con Chrome vía agent-browser, sin librerías.
- PDF enviado por Telegram (msg 35): 112 páginas, 6,4 MB. Pedro lo sube a Canva.
- Pendiente de Pedro:
  - portada elegida y título final (p1 hoy es solo texto "AISLE HUNT!")
  - ¿8 direcciones o solo hacia adelante?
  - ¿nombres de tema por puzzle?
  - portada completa para KDP (lomo y contraportada)

## Investigación comercial y KDP — 2026-09-15 ~10:15 (msgs 39–41)
Pedro pidió (msg 37): portada comercialmente atractiva, cumplir con KDP y derechos de autor, sugerencia de título y subtítulo, texto de contraportada, destacar la letra grande y otras mejoras.

- Mercado:
  - Competencia de supermercado: títulos genéricos, 6×9", 50–55 puzzles.
  - Los top de large print destacan letra grande y "adults and seniors" (asinsight, jul. 2026).
- Propuesta:
  - **AISLE HUNT!**, subtítulo *Supermarket Word Search: 55 Large Print Puzzles for Adults and Seniors*.
  - Busqué "Aisle Hunt" y no hay libro con ese nombre.
  - Alternativas sin verificar: Cart Full of Words / Shop & Seek.
- Serie: logo "___ HUNT!" + sello LARGE PRINT + marco de grilla fijos; cambia tema, ilustración y color.
- Contraportada: texto en inglés enviado (msg 40), sin promesas de salud.
- Legal / KDP:
  - **POPSICLE** es marca registrada de Unilever → cambiar a ICE POP (pendiente de su OK).
  - Declarar en KDP las imágenes hechas con IA (ilustración de Canva AI).
  - No usar bestseller, free ni marcas en el título; el texto de la portada debe coincidir con los metadatos.
  - Canva sirve si el diseño es propio.
- Specs de portada: lomo 112 × 0.002252 = 0,252" (texto permitido desde 79 págs.); archivo completo 17,502 × 11,25" con sangrado de 0,125"; 300 DPI; un solo PDF.
- Mejoras sugeridas: nombre de sección por puzzle, "Vol. 1", página final con la serie.
- Esperando: OK de Pedro al título → rehacer la portada y corregir POPSICLE en el PDF.

## Cambios de Pedro — 2026-09-15 09:53–09:58 (msgs 42, 43, 47, 48, 52, 53)
- **Tamaño 6×9"**. Yo había entendido mal "no cambies el tamaño": el tamaño que quiere es 6×9.
- **Título**: *Word Search: Aisle Hunt! 55 Large Print Supermarket Puzzles for Adults and Seniors* (confirmado, msg 52).
- Palabras **solo hacia adelante**: → ↓ ↘ ↗, ninguna al revés.
- Contraportada aprobada; POPSICLE → ICE POP.
- Mejoras aprobadas: nombres de sección (55, desde Citrus & Orchard hasta Checkout Lane), Vol. 1, nota de serie.
- Nota de serie: **opción B**, al pie de las instrucciones, para mantener **112 págs.**

## Interior v2 — enviado 10:0x (msg 54)
- 6×9", grilla 13×13, márgenes espejados (0,5" hacia el lomo, 0,35" hacia afuera). 112 págs.
- PDF: `agent-browser pdf` IGNORA @page (sale carta). Usar Chrome directo:
  `~/.agent-browser/browsers/chrome-*/chrome --headless --no-sandbox --no-pdf-header-footer --print-to-pdf=<pdf> file://<html>`
- El generador evita esconder una palabra dentro de otra; en el puzzle 55 APPLE está contenida en PINEAPPLE. Le propuse cambiar APPLE → PLUM (pendiente).
- Siguiente: portada completa 6×9 (lomo 0,252", archivo 12,502×9,25").

## Portada v1 propia (vectorial) — enviada 10:10 (msgs 68–70)
- `tools/portada.py libro.json out.html [--front-only] [--white]`, con los datos en `libro.json` → "cover".
  - Toldo, título, etiqueta "AISLE HUNT!", sello LARGE PRINT, carro con canasta sopa de letras, piso, franja inferior.
  - Contraportada: titular, tarjeta con texto, muestra "DAIRY CASE" y zona de código de barras libre (abajo a la derecha).
- Sin IA ni stock. Fuentes en `tools/fonts`: Luckiest Guy (Apache 2.0) y Fredoka (OFL).
- PDF: Chrome headless `--print-to-pdf`. Medidas 900×666 pt = 12,502×9,25"; lomo 0,2522". Fredoka queda incrustada como Type3 (vectorial).
- p1 del interior = frente sobre blanco (`portada.front_svg_white`). Avisé que en interior B/N se imprime en grises.
- Sugerí borrar de Canva las 4 portadas IA (DAHVQyjvkOw, DAHVQw41Dcw, DAHVQz-shcM, DAHVQ1RlCfI).
- MELON se queda (Pedro, msg 64).
- Pedro (msg 66): no le calzan los nombres de sección → quiere el número del puzzle identificado. Le di opciones (msg 67):
  - A) PUZZLE 1
  - B) PUZZLE 1 · AISLE 1 (recomendada)
  - C) PUZZLE N + frase rotativa
  Esperando la elección; cambia también la viñeta "Themed aisles…" de la contraportada.
- 10:17 Pedro preguntó si la p1 se ve bien en grises. La simulé (filtro grayscale):
  - En color se pierde contraste: rojo sobre amarillo queda gris sobre gris.
  - Hice una paleta B/N para la p1 (`interior_ink: "bw"`, que es el valor por defecto en `front_svg_white`). Enviada (msgs 72–74).
  - La portada exterior sigue en color.
- Sigue pendiente: títulos A/B/C.

## Versión con títulos C — enviada 10:25 (msgs 78–81)
- Pedro eligió **C** (msg 75): cada puzzle lleva "PUZZLE N" y debajo una frase de compras. Las 55 frases son únicas y están en el JSON (`phrase`).
  - Las soluciones muestran "SOLUTION N" con la misma frase.
- Viñeta de la contraportada: "A fun shopping moment on every page, from Grab a Cart! to See You Next Time!".
  - Muestra de la contraportada: "PUZZLE 7".
  - Texto de la contraportada a 18px para que no se desborde.
- Entregados: **interior v4** (112 págs., 6×9) y **portada v2** (12,502×9,25"). Verificado: 495 palabras únicas, solo hacia adelante, 0 ambigüedades, sin desbordes.
- Declaración de IA en KDP: primero dije "no declarar" y lo corregí.
  - **Texto = sí**: contraportada, instrucciones y frases los redacté yo.
  - **Imágenes = no**: la portada es vectorial hecha con código.
  - Los puzzles son algorítmicos y las palabras son de Pedro.
- Nota técnica: no usar `pkill -f` con un patrón que calce con la propia línea de comando (mata la shell).
- Esperando: conformidad de Pedro / siguientes ajustes.

## Recomendaciones de mejora — enviadas 11:10 (msgs 85–86)
Pedro pidió (msg 83) más recomendaciones, mirando libros muy vendidos.

- Ya cumple: 1 puzzle por página, grilla de ~18 pt, B/N, soluciones al final.
- Propuse para el interior:
  - lista de palabras de 13 pt → 16–18 pt (lo que quepa en 3 columnas)
  - frase sin cursiva
  - "This book belongs to ___" en p2
  - línea de copyright en p2 (falta nombre de autor/sello)
  - soluciones con contorno en vez de relleno
- Ideas para Vol. 2: mensaje secreto con las letras sobrantes; más palabras (los top traen 15–20).
- Precio: impresión US$ 2,344 (1,00 + 0,012 × 112). En Amazon.com la regalía es 50% bajo US$ 9,99 y 60% desde 9,99.
  - US$ 7,99 → 1,65 · US$ 8,99 → 2,15 · US$ 9,99 → 3,65 (recomendado)
- Envié 7 palabras clave, estrategia de serie (Vol. 2–3 pronto, un tema por libro) y el ángulo de regalo solo en la descripción.
- Fuentes: KDP G201834340, KDP community (regalías), kdpeasy (blog no oficial).
- Esperando: si aplico las mejoras + nombre de autor/sello.

## Interior v5 — enviado 11:25 (msgs 90–92)
- Pedro aprobó (msg 87): lista a 16 pt "siempre y cuando quepa en 3 columnas", frase sin cursiva, "This book belongs to", soluciones con contorno.
  - Las recomendaciones de venta quedan para antes de publicar (msg 88).
- 16 pt **no cabe** (10 puzzles se desbordan hasta 0,7"); 15 → 8; 14,5 → 4; **14 pt → 0**. Quedó en `WORD_PT = 14`, con gap 0,1".
  - Ofrecí como alternativa 16 pt partiendo las palabras largas (no recomendado).
- Soluciones: cápsula `rect` rx=15 con contorno negro de 2,6 unidades, rotada según la dirección.
- Pendiente: nombre de autor/sello → línea de copyright en p2. Recomendaciones de venta antes de publicar.
- 11:17 Pedro confirma lista en 14 pt (msg 93). Interior v5 = versión vigente.

## Alternativas comerciales de portada — enviadas 11:45 (msgs 100–103)
- Pedro (msg 96) pidió revisar la competencia y alternativas "lo más comercial posible".
- Revisé con agent-browser el top 30 de Amazon Best Sellers (Word Search Games) y la búsqueda "large print word search grocery food".
  - El título domina más del 50% de la portada.
  - Textura o bordes de letras de sopa.
  - Números grandes en sellos (5000 WORDS, 224 PUZZLES).
  - LARGE PRINT en franja roja abajo; colores saturados.
  - En comida predominan ilustraciones realistas o de IA.
- Nuevo `tools/portada_alt.py` con estilos `bold` (A) y `grid` (B); `portada.py --front-only --style=bold|grid`.
  - Hice una hoja comparativa con miniaturas de Amazon.
- Recomendé **A · Bold**: azul con textura de letras, WORD SEARCH gigante, sello 55 PUZZLES, franja LARGE PRINT, carro al 74%.
- Esperando elección → luego contraportada y lomo del estilo elegido (hoy `back`/`spine` son del estilo clásico).

## Portada A (bold) elegida — portada v3 + interior v6 enviados ~12:00 (msgs 107–113)
- Pedro eligió **A** (msg 104). `cover.style = "bold"` en el JSON.
  - `portada_alt.back_bold`, `spine_bold` y `front_bold(white=True)` para la p1 en B/N.
  - La franja roja es continua de contraportada a frente.
- Pedro preguntó si "LARGE PRINT" se justifica (msg 106):
  - grilla ~18,5 pt (cumple APH ≥18)
  - lista 14 pt (mínimo NAVH)
  - instrucciones subidas de 12 → 14 pt
  - No usar "EXTRA LARGE" ni "JUMBO".
- Verificado:
  - portada 900×666 pt
  - ningún texto fuera de la zona segura (25 u = 0,125" dentro del corte) ni cruzando el lomo
  - zona de código de barras libre
  - interior 112 págs. sin desbordes
- Detalle menor: en la p1 B/N la zanahoria conserva su color fijo (se imprime en gris).
- Pendiente:
  - nombre de autor/sello (línea de copyright)
  - revisión comercial antes de publicar (precio, palabras clave, descripción)

## Autor y dificultad — 11:35–12:10 (msgs 114–121)
- **Autor: "Peter & Cardu"** (msg 114).
  - JSON: `author`, `year` 2026, `cover.author`.
  - Aparece en el frente (arriba a la derecha), en el lomo y en la línea de copyright de la p2.
  - Enviados **portada v4** e **interior v7**. En KDP el autor debe decir exactamente "Peter & Cardu".
- Dificultad (msg 116):
  - Medí 13×13, 9 palabras, sin revés; 45% →, 32% ↓, 23% diagonales; 7,3 letras en promedio; las palabras cubren el 39% de la grilla.
  - Resultado **FÁCIL** (convención de mercado, no estándar oficial). Sugerí usar "easy" en la descripción y las palabras clave.
  - Pregunté si agrega un sello "EASY" en la portada (pendiente).
- Ofrecí preparar la descripción de Amazon (pendiente de respuesta).

## Ajuste de autor en portada — portada v5 + interior v8 (msgs 122–128)
- Pedro (msg 122): el autor quedaba muy cerca del título.
  - Ahora "PETER & CARDU" va arriba y centrado (letter-spacing 4); título y etiqueta bajan ~12–20 u; VOL. 1 como etiqueta pegada al extremo izquierdo de "AISLE HUNT!"; carro a y=470, escala 0,72.
  - Zonas seguras OK. Envié antes/después.
- Pedro (msg 123) pidió el texto completo de la contraportada: enviado (msg 128).
- Detecté que la muestra "PUZZLE 7" no es el puzzle 7 real → propuse cambiarla a "SAMPLE" en la próxima versión, junto con sus comentarios del texto.
- 11:41 Pedro **aprueba la portada** con el autor arriba (msg 130).
  - Portada v6: muestra "SAMPLE".
  - **Vigentes: portada v6 + interior v8**, copiados en `entregables/libro1/` (fuera de git, no se commitean) + `cover_final.png`.
- Siguiente: revisión comercial antes de publicar (precio, palabras clave, categorías, descripción).

## Página 2 con íconos (propuesta) — 11:55 (msgs 141–146)
- Pedro quiere "mejorar la página de las soluciones" y mandó una foto de referencia (incoming/file_1.jpg).
  - La foto era en realidad una **página de instrucciones** de otro libro: recuadro de título, pasos con íconos, mini grilla con cápsulas negras y flechas, "Solutions start on page X".
- Hice una p2 propia (`instructions_style: "icons"` en el JSON; `instructions_icons()` en generar.py):
  - 5 pasos con íconos SVG propios (lista, lupa, flechas, lápiz, carro)
  - mini ejemplo 7×7 con MILK →, EGGS ↓, TEA ↘ en cápsula negra con letras blancas
  - check "Stuck? Solutions start on page 58."
  - se mantienen belongs to, nota de serie y copyright
  - sin desbordes
- Le pregunté si también quiere cambiar las soluciones a cápsula negra con letras blancas (pendiente).
- Interior regenerado localmente (v9 candidato, aún no enviado como PDF).
- 12:11 Pedro aprueba la p2 con íconos; las soluciones se quedan con contorno (msg 148).
  - **Vigentes: interior v9 + portada v6**, ambos en `entregables/libro1/`.
- Pendiente: revisión comercial (precio, palabras clave, categorías, descripción); sello "EASY" sin respuesta.

## Revisión editorial completa — 12:22–12:50 (msgs 153–160)
Pedro pidió revisar todo como editor profesional.

### Corregido (técnico)
1. **Palabras ofensivas en el relleno**: 34/55 grillas las tenían (SEX, ASS, KKK, FAG, CUM, FUK…).
   - Nuevo filtro `BAD` + `bad_words()` en generar.py: re-sortea el relleno hasta 100 veces, manteniendo las palabras.
   - Se toleran las que caen dentro de palabras de la lista (RAPE en GRAPE, CUM en CUCUMBER, ASS en GLASS/CROISSANT, NIG en GINGER al revés).
2. **Type3 en PDF**: el texto SVG con `stroke` sale como Type3 en Chrome.
   - `big_title` ahora arma el contorno con 24 copias rellenas desplazadas.
   - Fredoka variable reemplazada por estáticas 400/500/600/700 (fonts.gstatic, OFL).
   - Resultado: 0 Type3 en portada e interior.
3. **p1 con color** (zanahoria, hojas, pan): claves `bread/carrot/leaf` en la paleta B/N → 100% gris (verificado: 0 colores no grises en el HTML).
4. `<title>` en los HTML/PDF.

### Nueva herramienta
- `tools/verificar.py libro.json interior.html`: audita el HTML final.
  - numeración y paridad
  - título, frase y lista iguales en puzzle y solución
  - grilla del puzzle = grilla de la solución
  - 9 contornos en su posición
  - 1 aparición hacia adelante y 0 al revés
  - palabras ofensivas
  - página de soluciones en p2
- Resultado actual: **0 errores**.
- Ortografía: comparé contra la lista dwyl/english-words. Solo marcó términos válidos (NAAN, UDON, SRIRACHA, etc.).

### Propuesto, esperando OK de Pedro
- a) Contraportada: "on every page" → "with every puzzle"
- b) #3 "Clean-Up on Aisle 3!" → "Cleanup on Aisle 3!"
- c) #47 "Around the World Aisle!" → "International Aisle!"
- d) Nota de serie: "large-print"
- Palabras:
  - FABRIC SHEETS → DRYER SHEETS (#45)
  - MILK POWDER → POWDERED MILK (#32)
  - COLLARD → COLLARDS (#6)
  - MATCH → MATCHES (#24)
  - CANDLES (#50) → FLASHLIGHT
- Decisión: nombre de serie en KDP (p. ej. "Word Search Hunt!") y ajustar la nota de p2.
- Los PDFs con las correcciones técnicas están generados en el scratchpad; se envían como interior v10 + portada v7 después del OK.

## Correcciones editoriales aplicadas — interior v10 + portada v7 (msgs 161–168)
- Pedro aprobó todo menos el tema Vol. 1 (msg 161). Aplicado:
  - contraportada: "with every puzzle"
  - #3 "Cleanup on Aisle 3!"; #47 "International Aisle!"
  - nota de serie: "large-print"
  - DRYER SHEETS (#45), POWDERED MILK (#32), COLLARDS (#6), MATCHES (#24), FLASHLIGHT (#50, reemplaza CANDLES)
- Ajustes derivados:
  - recuadro de contraportada 418 u de alto, foreignObject 390, muestra en y+600 (el texto quedaba a 5 px del borde)
  - sello 55 PUZZLES en `x0+w-128` (una punta salía de la zona segura)
- `verificar.py`: 0 errores. PDFs: 0 Type3. Copiados en `entregables/libro1/`.
- **Vigentes: interior v10 + portada v7.**

## Serie / Vol. 2 (msgs 163–168)
- Pedro: habrá más libros; el siguiente con **países, capitales y ciudades importantes**.
- Propuse:
  - **A (recomendada)**: una sola serie en KDP (p. ej. "Word Search Hunt!"), cada libro con nombre propio (Vol. 1 Aisle Hunt!, Vol. 2 p. ej. World Hunt!). En este libro solo cambia la nota de p2.
  - **B**: una serie por tema.
- Esperando su idea.
- 12:53 Pedro valora que todo quede dentro de márgenes y medidas (guardado en memory/preferencias.md).
- 12:53 Pedro preguntó si "Aisle Hunt!"/"World Hunt!" son nombres comerciales que venden (msg 170). Respondí (msg 171):
  - No venden solos: son marca, no búsqueda.
  - Lo que atrae ventas es "Word Search" + un subtítulo con lo que la gente busca (large print, tema, adults and seniors) + la portada en miniatura.
  - El nombre creativo es gancho opcional.
  - Recomendé subtítulo descriptivo por libro y nombre de serie descriptivo (p. ej. "Large Print Word Search by Theme").
  - Aclaré que Amazon no publica cómo pondera el título frente a las palabras clave (es práctica habitual) y que "World Hunt" no está verificado.
- Pregunté si mantiene "Aisle Hunt!" en el Vol. 1 o pasa a un enfoque solo descriptivo (pendiente).
- 12:56 Pedro preguntó si el libro está bien para publicar y ser comercial (msg 172). Respondí (msg 173):
  - Publicable: sí.
  - Fortalezas: portada, título con palabras clave, nicho, interior cuidado.
  - Débiles: 55 puzzles frente a 100–224 de la competencia; 9 palabras; sin reseñas al inicio.
  - Falta: nombre de serie, descripción, 7 palabras clave y categorías, precio, marcar IA en texto.
- **Error mío corregido** (msg 174): había sugerido reseñas de amigos o familiares. Amazon lo **prohíbe** (Community Guidelines). Alternativas: reseñas espontáneas, Amazon Ads, programas oficiales.
- 12:58 Pedro: ¿"supermarket" o "grocery"? (msg 176). Medí en Amazon.com:
  - Autocompletado: "supermarket word search" sí aparece; "grocery word…" no sugiere sopas de letras.
  - Resultados: grocery word search 443; supermarket word search 194; food word search large print 4.000+.
  - Recomendé **mantener Supermarket** y poner grocery/food en las 7 palabras clave.
- Nota técnica: nunca dejar `cat >> archivo` sin entrada en un comando (se cuelga esperando stdin).
- 13:03 Pedro pidió un resumen de lo que falta definir de la edición (lo de KDP después). Enviado (msg 181):
  1) nombre de serie / VOL. 1
  2) mantener "Aisle Hunt!" o ir solo descriptivo
  3) sello EASY (opcional)
  4) papel blanco (actual) o crema (cambia el lomo)
  5) prueba impresa recomendada
- 13:06 Pedro decide (msg 185): **sin sello EASY**, **papel blanco**, **sin prueba impresa**.
- Nombre de serie (msg 182) y punto 2 (msg 183). Busqué en Amazon libros cuyo título contenga cada nombre:
  - Libres (0 títulos): Big Print Word Hunt, Large Print Word Search by Theme, Word Search Hunt.
  - Ya usados: Big Letter Word Search (2), Easy Large Print Word Search (1).
- Recomendé serie **"Big Print Word Hunt"** + **mantener "Aisle Hunt!"**.
  - KDP: serie Big Print Word Hunt, vol. 1; título Word Search; subtítulo Aisle Hunt! 55 Large Print Supermarket Puzzles for Adults and Seniors.
  - p2: "Aisle Hunt! is Vol. 1 of the Big Print Word Hunt series…". Portada sin cambios. Esperando OK.
- 13:10 Pedro aprueba (msg 187): serie **Big Print Word Hunt** vol. 1 y mantener "Aisle Hunt!".
  - JSON: `series`. Nota p2: "Aisle Hunt! is Vol. 1 of the Big Print Word Hunt series." (la versión larga desbordaba la p2 y cortaba "large-/print"). Mini ejemplo a 2,75".
  - verificar.py: 0 errores; 0 desbordes; 0 Type3.
- **EDICIÓN CERRADA. Vigentes: interior v11 + portada v7** (en `entregables/libro1/`).
- Siguiente: parte KDP (descripción, 7 palabras clave, categorías, precio; marcar IA en texto = sí, imágenes = no).
- 13:21 Pedro: "guarda eso". Archivos finales versionados en `clientes/libro-sopa-de-letras/entregables/vol1/` (interior v11, portada v7, cover_final.png). Resumen del proyecto en `memory/proyectos.md`.

# VOL. 2 — Países, capitales y ciudades importantes
- 13:23 Pedro pide armar el Vol. 2 (msg 193): libro + portada, lo más profesional posible, revisando errores de todo tipo. Enviará la lista.
- Asumo las specs del Vol. 1 salvo indicación: 6×9, blanco, 13×13, 55×9, 112 págs., p1 B/N, p2 con íconos, contornos, solo hacia adelante, frases, autor Peter & Cardu, serie Big Print Word Hunt Vol. 2, portada estilo A con otro color e ilustración de viaje.
- Revisiones clave para geografía:
  - capitales y nombres actuales (Astana, Eswatini, Türkiye…)
  - diacríticos y signos (grilla solo A–Z)
  - nombres de más de 13 letras
  - temas sensibles (territorios en disputa, capitales múltiples)
- Esperando la lista.
- 13:24 Lista del Vol. 2 recibida (incoming/file_2.xlsx → `vol2/lista_original.json`): 55 bloques × 9 = país + capital + 7 ciudades. Sin repetidas, máx. 13 letras, solo A–Z y espacios. Pedro: "usa lo mismo" (specs del Vol. 1).
- Revisión y preguntas enviadas (msg 200):
  1) título por puzzle: país (recomendado) o frase de viaje
  2) faltan USA, UK y Australia (el mercado es EE. UU.); 22/55 de Latinoamérica
  3) sensibles: Ucrania DONETSK y MARIUPOL (ocupadas) → POLTAVA y CHERNIVTSI; Corea del Norte (aviso)
  4) nombres:
     - DANANG → DA NANG; HATYAI → HAT YAI; HO CHI MINH → SAIGON
     - con puntuación en la lista: ST. PETERSBURG, PORT-AU-PRINCE, CAP-HAITIEN, PETION-VILLE
     - mantener BANGALORE y TURKEY
  - aviso: MEXICO en MEXICO CITY y PANAMA en PANAMA CITY → dejarlo
- 13:31 Pedro decide (msg 204):
  1) **B**: frases de viaje por puzzle
  2) **cambiar países** para atraer lectores de EE. UU.
  3) OK Ucrania (POLTAVA, CHERNIVTSI) y **cambiar Corea del Norte**
  4) OK correcciones de nombres; dejar BANGALORE y TURKEY; dejar MEXICO y PANAMA (dentro de su capital)
- Portada Vol. 2 en progreso: estilo bold teal (#00897B), ilustración `suitcase` (maleta con sopa de letras, globo, avión, pin), nombre de trabajo "WORLD HUNT!" (0 títulos en Amazon).
  - Plantilla generalizada (`bold_palette`, `illustration`, `count`, `band_line`); el Vol. 1 se regenera idéntico byte a byte (md5 verificado).

## Vol. 2 v1 entregado — 13:45 (msgs 207–212)
- Datos: `vol2/libro2_mundo.json` (cada puzzle: `phrase`, `country`, `words`). Seed 2027.
- Países:
  - Entran: United States, United Kingdom, Ireland, Portugal, Greece, Philippines, Australia, New Zealand.
  - Salen: North Korea (pedido), Haiti, Libya, Myanmar (conflictos), Nicaragua, Honduras, Zambia, Cameroon.
- Orden (pedido msg 207): 1 United States, 2 United Kingdom, 3 France, luego Américas → Europa → África → Asia → Oceanía.
- Correcciones: DA NANG, HAT YAI, SAIGON, POLTAVA, CHERNIVTSI, ST. PETERSBURG, WASHINGTON, D.C.
- 55 frases de viaje únicas (Pack Your Bags! → Welcome Home!).
- Palabras contenidas en otra (aceptado por criterio de Pedro): MEXICO/MEXICO CITY, PANAMA/PANAMA CITY, TUNIS/TUNISIA. `verificar.py` ahora las trata como esperadas.
- Portada:
  - teal #00897B, ilustración maleta con grilla (PARIS, TOKYO, CAIRO, LIMA marcadas), globo, pin y avión
  - sello 55 a la derecha escalado 0,88
  - contraportada: "Pack your bags and start searching!", muestra TOKYO/OSAKA/KYOTO/NAGOYA/KOBE
  - band_line "World Geography Puzzles for Adults & Seniors"
- p1 B/N: agregué `sea`/`land`/`plane_fold` grises.
- Verificado: 0 errores, 0 desbordes, 0 Type3, zona segura OK, código de barras libre, contraportada 340/374. El Vol. 1 sigue idéntico (md5).
- Archivos: `entregables/vol2/` (interior v1, portada v1, cover_preview.png).
- Esperando revisión de Pedro. Pendiente además: confirmar nombre "World Hunt!".

# Vol. 3–5 — investigación de temas (13:51–14:20, msgs 216–219)
- Pedro pide que YO proponga los temas de los Vol. 3, 4 y 5: complementarios, comerciales, con buena rotación.
- Top 100 Amazon Word Search Games (15-sep-2026):
  - misterio/asesinato 15; Biblia/fe 9; calma/mindfulness/inspiración 7
  - estacionales 8 (otoño 5, Halloween 2, Navidad 1, subiendo); español 4
  - nostalgia #10; naturaleza 3 (jardín #67, fauna #94, perros #99); USA #85 (Brain Games)
  - licencias: Friends, Gilmore Girls, Family Feud, Wheel of Fortune, Dolly Parton, D&D
- Autocompletado: "for seniors" y "large print" aparecen en Christmas, nostalgic, gardening, bible, inspirational, winter, cat.
- Resultados (búsqueda amplia): christmas 10k+, bible 10k+, inspirational 9k+, nostalgic 5k+, usa 5k+, garden 3k+, dog 3k+, bird 2k+.
- Recomendación enviada:
  - **Vol. 3 Christmas** (publicar antes de fines de octubre; sin personajes registrados)
  - **Vol. 4 Nostalgia** (solo genéricos)
  - **Vol. 5 USA Road Trip** (sigue al Vol. 2)
  - Alternativas: Biblia, jardín y aves, perros y gatos.
  - Extras: serie en español; pack de 5 volúmenes.
- Esperando OK.
- 14:02 Pedro decide (msgs 221–223): **Vol. 3 USA, Vol. 4 Nostalgia, Vol. 5 Christmas**. "Do it!"
  - Yo armo las listas de palabras.
  - Christmas debe estar publicado a fines de octubre (KDP permite publicar fuera de orden).
  - Otros libros navideños sugeridos (respuesta a su pregunta): sudoku letra grande, libro de actividades mixto, crucigramas. Colorear no recomendado.

## Otras ideas navideñas (msgs 227–231)
- Pedro (227): libro para colorear con imágenes de Canva que yo mejore. Respondí:
  - Posible, pero hay que declarar las imágenes IA en KDP y no son protegibles por derechos de autor.
  - Stock de Canva no vale tal cual.
  - Yo limpio a B/N a 300 DPI, maqueto, reverso en blanco y hago la portada. No redibujo.
  - Propuse prueba con 5 imágenes.
- Pedro (228, 230): planner de Navidad tipo calendario de adviento (actividades diarias, lista de regalos, checklist).
  - Demanda: autocompletado "christmas planner 2026", "advent puzzle books for adults 2026", "advent calendar puzzles for adults"; hay un "The Seniors' Advent Calendar: 24 Days of Relaxing Puzzles".
  - Propuse "Christmas Countdown Planner & Puzzle Book": 25 días (mini sopa + actividad/recuerdo + check) + regalos, tarjetas, menú, decoración, presupuesto, checklist semanal; letra grande. Fecha: fines de octubre.
- Prioridad sugerida: Vol. 5 Christmas, Planner, Vol. 3 USA, Vol. 4 Nostalgia (esperando OK).
- Vol. 3 USA: interior y portada generados en el scratchpad y auditados (0 errores). Falta enviar.

## Vol. 3 USA v1 entregado — ~14:30 (msgs 232–235)
- `vol3/libro3_usa.json`, seed 2028:
  - Puzzles 1–50: estado + capital + 7 ciudades o lugares, orden NE → S → MW → SW → W → AK/HI.
  - Puzzles 51–55: National Parks ×2, Landmarks, Road Trip, Symbols. Cada puzzle tiene `theme_label`.
- 55 frases de viaje en auto, sin repetir las de Vol. 1 y 2.
- Evitados:
  - duplicados homónimos entre estados (Springfield, Portland, Jackson, Columbus, Charleston, Newark, Dover, Salem, Augusta, Albany, Rochester, Manhattan, Bellevue, Lexington, Norfolk, Alexandria…)
  - marcas: Space Needle, Empire State, Hollywood Sign, Disney
- Contenidas aceptadas: INDIANA/INDIANAPOLIS, OKLAHOMA/OKLAHOMA CITY.
- Portada: navy #1D2F6F, ilustración `billboard` (cartel con MAINE/TEXAS/IOWA/OHIO marcadas, estrellas, auto teal, carretera), escala 0,62. "USA Hunt!" sin títulos en Amazon.
- Paleta B/N ampliada: car/glass/post/chrome.
- Verificado: 0 errores, 0 desbordes, 0 Type3, 0 colores no grises, zona segura OK. Vol. 1 y 2 intactos (cmp).
- Archivos: `entregables/vol3/`.
- Siguiente: Vol. 5 Christmas. Esperando prioridad con el planner.
- 14:17 Pedro (msgs 237–238): la portada Vol. 3 no deja claro que es EE. UU.
  - Agregué `cart.usa_flag`: bandera flameando en asta a la izquierda y cabecera del cartel con barras y estrellas. Paleta B/N con flag_blue.
  - Enviados antes/después, **portada v2 + interior v2**. Verificado: zona segura, 0 errores, grises; Vol. 1 y 2 intactos.
- Vol. 5 Christmas: lista borrador lista (`vol5/lista_borrador.json`, 55 temas × 9, sin duplicados, sin palabras contenidas, sin personajes registrados).

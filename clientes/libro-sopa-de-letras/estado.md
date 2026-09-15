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

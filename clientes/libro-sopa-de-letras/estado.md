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

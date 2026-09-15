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

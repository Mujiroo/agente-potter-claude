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

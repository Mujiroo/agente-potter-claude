# Tamarama SpA — mangueras de PVC (proveedores chinos)

## Contexto
- Tamarama SpA (Curicó) importa mangueras de PVC de **succión** (amarilla, espiral rígida) y **jardín** (verde). Pedro es trader: presenta precios a sus clientes.
- Proveedor anterior: **Dongying Wanhe Rubber & Plastic**. Pedidos en 2021; último precio en la proforma DYWH20210607CH01 (7-jun-2021): US$ 21.016 FOB por un 40HQ, pago 30/70.
- 14-sep-2026: Pedro pidió cotización a **Weifang Xiandai Plastics & Rubbers** (contacto vía Alibaba). Motivo: el proveedor actual tiene **problemas de calidad** («se ven bien, pero duran poco en terreno», según sus clientes). Pidió ficha técnica completa: WP/BP, vacío, radio de curvatura, temperatura, UV, certificaciones y MOQ.
- 16-sep-2026: Xiandai mandó la cotización XDQ260916 (FOB por rollo; sin accesorios ni embalaje; precio por contenedor completo) y un informe SGS RoHS (TAOEC26010757001_1).

## Análisis enviado a Pedro (16-sep, msgs 556–558)
- Por metro:
  - Succión: Xiandai −14 % a +34 % (en 1-1/2" y 2" casi igual). Paredes más gruesas; US$ 1,95/kg vs 2,15.
  - Jardín: Xiandai +51 % a +95 % (US$ 2,26/kg vs 1,51).
- Mismo pedido que 2021: US$ 26.239 (+25 %). **93 m³ vs 71 m³**: no cabe en un 40HQ.
- Faltantes de Xiandai: presiones, vacío, radio, temperatura, UV, ficha técnica.
- El informe SGS es de otra manguera (reforzada con fibra roja/blanca/negra), sólo RoHS, «referencia interna».
- Recomendación:
  - Pedir ficha técnica, muestras (succión 1" y jardín 3/4") y material (PVC virgen, % de carga, DOTP vs DOP, UV).
  - Pedir plan de carga, precio con embalaje y Form F (arancel 0 % con TLC; sin él, 6 %).
  - Negociar jardín; succión con Xiandai se ve mejor apuesta.
- Ofrecí redactar el correo a Xiandai (sin enviar). Esperando respuesta.

## Archivos
- incoming/file_15.pdf (cotización Xiandai), incoming/file_14.pdf (SGS), incoming/file_16.pdf (PI Dongying 24-may-2021).
- 13:08 Pedro pidió «el resumen de todo en un Excel» (msg 559). Se generó el 16-sep 14:05 con su autorización: `Mangueras_Xiandai_vs_Dongying.xlsx` (`excel_build.js`).
- 18-sep 21:20 Pedro retoma mangueras (msg 1202). Enviado resumen + borrador de correo a Xiandai en inglés (msgs 1203–1204), 7 puntos: ficha técnica, material, SGS de otro producto, muestras, plan de carga con embalaje, Form F, negociar jardín. NO enviado; esperando revisión de Pedro.
- 18-sep 21:24 Pedro pide qué proveedor es mejor (msgs 1205–1206). Análisis con datos públicos (msg 1207):
  - Xiandai: 2002, especialista PVC, 100–120 líneas, 36.000–60.000 t/año (cifras inconsistentes entre fuentes), ISO 9001/14001/18001, SGS FDA/SVHC declarados. Fuentes: wfpvc.suppliergo.com/about.html, made-in-china, búsqueda.
  - Wanhe: 2007, foco caucho, 14.000 m², exporta a +20 países incl. Chile, ISO 9001:2008 (versión vencida desde 2018). Fuente: whrubberhose.com/aboutus.html.
  - Veredicto: Xiandai mejor para PVC; falta validar con muestras + ensayo del producto exacto y métricas Alibaba (bloqueadas para mí; ofrecí prompt para Claude en Chrome).
- 18-sep 21:37 Pedro pide correo para el contacto de Xiandai (msg 1208). Borrador enviado (msg 1209): 8 puntos (se agregó copia del ISO 9001 vigente y tono de interés en succión). NO enviado por mí.
- 18-sep 21:39 ¿Especificaciones comparables? (msg 1214): parcialmente. Comparables: DI/DE, largo, peso → pared y kg/m (succión Xiandai más gruesa en 1"–2" y 4"; jardín 3/4" y 1" misma manguera). No comparables: presiones (sólo Wanhe), construcción, largo de rollo, fecha (Wanhe 2021, PI 24-may DYWH20210524CH02), material. Enviado msg 1215.
- 18-sep 21:40 Prompt para buscar specs de mangueras de jardín 1/2, 3/4 y 1" en Mercado Libre Chile: clientes/tamarama/prompt_mangueras_meli.txt (msgs 1217–1218).
- 18-sep 22:00 Pedro manda el Excel de Claude en Chrome (Mercado Libre, 3 por medida): guardado `meli_mangueras_jardin_2026-09-18.xlsx`. Retail CLP/m con IVA: 1/2" 308–540; 3/4" 628–681; 1" 1.084–1.320. FOB CLP/m (dólar 959, Infobae cierre 18-sep): Xiandai 337/500/782; Wanhe 2021 173/331/537. Conclusión enviada (msg 1236): jardín Xiandai no es viable (FOB ≈ precio final sin IVA), debería bajar ~40–50 %; succión sigue siendo la oportunidad. Mercado más liviano (Hardpro 1/2" 0,084 kg/m vs Xiandai 0,156).
- 18-sep 22:05 Datos de dicas.cl (Shopify /collections/mangueras-de-jardin/products.json, leído por mí): jardín con malla 3 capas PVC + malla poliéster, espesor 2 mm, WP 7 bar, rotura 18 bar (todas las medidas). CLP/m con IVA y 20 % dcto: 1/2" 339, 3/4" 739, 1" 1.119. Peso despacho kg/m: 0,10 / 0,20 / 0,27 (más livianas que Xiandai y Wanhe). Enviado a Pedro (msg 1242).

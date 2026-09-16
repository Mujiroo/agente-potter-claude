const ExcelJS = require("exceljs");
const out = process.argv[2];
const wb = new ExcelJS.Workbook();
wb.creator = "Denver";
const NAVY = "FF1F3A5F", LIGHT = "FFE8EEF6", GREEN = "FFE3F2E1", RED = "FFFBE3E1", YEL = "FFFFF4D6";
const border = { top: { style: "thin", color: { argb: "FFBFBFBF" } }, bottom: { style: "thin", color: { argb: "FFBFBFBF" } },
  left: { style: "thin", color: { argb: "FFBFBFBF" } }, right: { style: "thin", color: { argb: "FFBFBFBF" } } };
function header(row) {
  row.eachCell(c => { c.font = { bold: true, color: { argb: "FFFFFFFF" } }; c.fill = { type: "pattern", pattern: "solid", fgColor: { argb: NAVY } };
    c.alignment = { vertical: "middle", horizontal: "center", wrapText: true }; c.border = border; });
  row.height = 34;
}
function title(ws, text, sub) {
  ws.addRow([text]).font = { bold: true, size: 16, color: { argb: NAVY } };
  if (sub) ws.addRow([sub]).font = { italic: true, color: { argb: "FF666666" } };
  ws.addRow([]);
}

// ---------------- 1. Resumen
const r = wb.addWorksheet("Resumen");
r.columns = [{ width: 30 }, { width: 95 }];
title(r, "Mangueras PVC · Xiandai (2026) vs Dongying Wanhe (2021)", "Tamarama SpA · análisis del 16-sep-2026 · precios FOB China en US$");
const resumen = [
  ["Proveedor nuevo", "Weifang Xiandai Plastics & Rubbers (Lina Liu) · cotización XDQ260916 del 16-sep-2026"],
  ["Proveedor anterior", "Dongying Wanhe Rubber & Plastic (Ben Hu) · último precio: proforma DYWH20210607CH01 del 7-jun-2021"],
  ["Motivo del cambio", "El proveedor anterior tiene problemas de durabilidad en terreno (reclamo de clientes)"],
  ["", ""],
  ["SUCCIÓN (amarilla)", "Precio por metro parecido: de −14% (3\") a +34% (1-1/4\"). Xiandai tiene paredes más gruesas y es 9% más barato por kilo (US$ 1,95 vs 2,15/kg)."],
  ["JARDÍN (verde)", "Xiandai es 51% a 95% más caro por metro (US$ 2,26 vs 1,51/kg). Hay que negociar o buscar otro fabricante."],
  ["Pedido tipo 2021", "Mismos metros: Dongying US$ 21.016 vs Xiandai US$ 26.239 (+25%). Volumen: 71 m³ vs 93 m³ (no cabe en un 40HQ)."],
  ["", ""],
  ["⚠ Falta en la cotización", "Presión de trabajo y de rotura, vacío, radio de curvatura, temperatura, protección UV, ficha técnica (lo pediste el 14-sep)."],
  ["⚠ Informe SGS", "Es de otra manguera (reforzada con fibra roja/blanca/negra). Solo RoHS (no mide durabilidad). Dice «solo referencia interna»."],
  ["", ""],
  ["RECOMENDACIÓN", "1) Pedir ficha técnica completa y muestras (succión 1\" y jardín 3/4\") para probar en terreno."],
  ["", "2) Pedir material por escrito: PVC virgen, % de carga (carbonato), plastificante (DOTP mejor que DOP), aditivo UV."],
  ["", "3) Pedir plan de carga del 40HQ y precio con embalaje (su precio no incluye cajas ni pallets)."],
  ["", "4) Exigir Certificado de Origen Form F (arancel 0% con TLC Chile-China; sin él, 6%)."],
  ["", "5) Negociar precio de jardín. Succión: Xiandai es la mejor apuesta, sujeta a muestras."],
  ["", "6) No cerrar sin ficha técnica, prueba de muestras y Form F."],
];
resumen.forEach(x => {
  const row = r.addRow(x);
  row.getCell(1).font = { bold: true }; row.getCell(2).alignment = { wrapText: true, vertical: "top" };
  if (x[0].startsWith("⚠")) row.eachCell(c => c.fill = { type: "pattern", pattern: "solid", fgColor: { argb: YEL } });
  if (x[0] === "RECOMENDACIÓN") row.getCell(1).font = { bold: true, color: { argb: NAVY } };
});

// ---------------- 2. Comparación por medida (con fórmulas)
const c = wb.addWorksheet("Comparación");
title(c, "Comparación por medida", "Datos de las cotizaciones; columnas en gris se calculan con fórmulas");
const H = ["Tipo", "Medida", "DW largo rollo (m)", "DW kg/rollo", "DW m³/rollo", "DW US$/rollo", "DW DI mm", "DW DE mm", "DW pared mm", "DW P. trabajo bar", "DW P. rotura bar",
  "XD largo rollo (m)", "XD kg/rollo", "XD m³/rollo", "XD US$/rollo", "XD DI mm", "XD DE mm", "XD MOQ (m)",
  "DW US$/m", "XD US$/m", "Dif. US$/m", "DW kg/m", "XD kg/m", "DW US$/kg", "XD US$/kg", "XD pared mm"];
header(c.addRow(H));
const data = [
  ["Succión", "1\"", 50, 16.5, 0.072, 35.5, 25, 30, 2.5, 8, 24, 30, 12.78, 0.10, 24.98, 25, 32, 1000],
  ["Succión", "1-1/4\"", 50, 21, 0.185, 45, 32, 38, 3, 8, 24, 30, 18.45, 0.15, 36.06, 32, 40, 1000],
  ["Succión", "1-1/2\"", 50, 31.5, 0.195, 67.5, 38, 45, 3.5, 8, 24, 30, 21.52, 0.20, 42.07, 38, 46, 1000],
  ["Succión", "2\"", 50, 47.5, 0.220, 102, 50, 58, 4, 7, 21, 30, 32.00, 0.30, 62.55, 51, 60, 1000],
  ["Succión", "3\"", 25, 45.5, 0.432, 98, 75, 85, 5, 5, 15, 30, 51.89, 0.46, 101.43, 76, 86, 600],
  ["Succión", "4\"", 25, 78.75, 1.6, 169, 100, 112, 6, 5, 15, 30, 97.75, 1.04, 191.09, 102, 116, 600],
  ["Jardín", "1/2\"", 100, 12, 0.038, 18, 12, 16, 2, 8, 15, 50, 7.80, 0.058, 17.59, 12, 17, 3000],
  ["Jardín", "3/4\"", 100, 22.8, 0.05, 34.5, 19, 24, 2.5, 5, 15, 50, 11.56, 0.068, 26.08, 19, 24, 2000],
  ["Jardín", "1\"", 50, 17.8, 0.072, 27, 25, 31, 3, 4, 12, 50, 18.07, 0.096, 40.75, 25, 31, 2000],
];
data.forEach(d => {
  const row = c.addRow(d);
  const n = row.number;
  const [,, L, kg, , pr, , , , , , L2, kg2, , pr2, di2, de2] = d;
  row.getCell(19).value = { formula: `F${n}/C${n}`, result: pr / L };
  row.getCell(20).value = { formula: `O${n}/L${n}`, result: pr2 / L2 };
  row.getCell(21).value = { formula: `T${n}/S${n}-1`, result: (pr2 / L2) / (pr / L) - 1 };
  row.getCell(22).value = { formula: `D${n}/C${n}`, result: kg / L };
  row.getCell(23).value = { formula: `M${n}/L${n}`, result: kg2 / L2 };
  row.getCell(24).value = { formula: `F${n}/D${n}`, result: pr / kg };
  row.getCell(25).value = { formula: `O${n}/M${n}`, result: pr2 / kg2 };
  row.getCell(26).value = { formula: `(Q${n}-P${n})/2`, result: (de2 - di2) / 2 };
  row.eachCell(cell => { cell.border = border; cell.alignment = { horizontal: "center" }; });
  [19, 20, 24, 25].forEach(i => row.getCell(i).numFmt = '"US$ "0.00');
  [22, 23].forEach(i => row.getCell(i).numFmt = "0.000");
  row.getCell(21).numFmt = "+0%;-0%";
  [6, 15].forEach(i => row.getCell(i).numFmt = '"US$ "0.00');
  for (let i = 19; i <= 26; i++) row.getCell(i).fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FFF2F2F2" } };
});
c.addConditionalFormatting({ ref: `U5:U13`, rules: [
  { type: "cellIs", operator: "greaterThan", formulae: ["0.15"], style: { fill: { type: "pattern", pattern: "solid", bgColor: { argb: RED } } } },
  { type: "cellIs", operator: "lessThan", formulae: ["0"], style: { fill: { type: "pattern", pattern: "solid", bgColor: { argb: GREEN } } } }] });
c.columns.forEach((col, i) => col.width = i < 2 ? 10 : 11);
c.views = [{ state: "frozen", xSplit: 2, ySplit: 4 }];
c.addRow([]);
c.addRow(["DW = Dongying Wanhe (7-jun-2021) · XD = Xiandai (16-sep-2026) · Xiandai no informó presiones (pendiente)."]).font = { italic: true };

// ---------------- 3. Pedido tipo
const p = wb.addWorksheet("Pedido tipo");
title(p, "Mismo pedido de 2021 con los precios de cada proveedor", "Metros de la proforma de junio-2021 (1 contenedor 40HQ)");
header(p.addRow(["Tipo", "Medida", "Metros", "DW US$", "XD US$", "Diferencia US$", "DW m³", "XD m³"]));
const metros = [300, 200, 600, 1500, 1000, 425, 8000, 20000, 3000];
const acc = [0, 0, 0, 0, 0, 0];
data.forEach((d, i) => {
  const src = 5 + i; // fila en Comparación
  const row = p.addRow([d[0], d[1], metros[i]]);
  const n = row.number;
  const m = metros[i], vo = m * d[5] / d[2], vn = m * d[14] / d[11], co = m * d[4] / d[2], cn = m * d[13] / d[11];
  acc[0] += m; acc[1] += vo; acc[2] += vn; acc[4] += co; acc[5] += cn;
  row.getCell(4).value = { formula: `C${n}*'Comparación'!S${src}`, result: vo };
  row.getCell(5).value = { formula: `C${n}*'Comparación'!T${src}`, result: vn };
  row.getCell(6).value = { formula: `E${n}-D${n}`, result: vn - vo };
  row.getCell(7).value = { formula: `C${n}*'Comparación'!E${src}/'Comparación'!C${src}`, result: co };
  row.getCell(8).value = { formula: `C${n}*'Comparación'!N${src}/'Comparación'!L${src}`, result: cn };
  row.eachCell(cell => cell.border = border);
  [4, 5, 6].forEach(k => row.getCell(k).numFmt = '"US$ "#,##0');
  [7, 8].forEach(k => row.getCell(k).numFmt = "0.0");
});
const tot = p.addRow(["TOTAL", "", { formula: "SUM(C5:C13)", result: acc[0] }, { formula: "SUM(D5:D13)", result: acc[1] }, { formula: "SUM(E5:E13)", result: acc[2] }, { formula: "E14-D14", result: acc[2] - acc[1] }, { formula: "SUM(G5:G13)", result: acc[4] }, { formula: "SUM(H5:H13)", result: acc[5] }]);
tot.eachCell(cell => { cell.font = { bold: true }; cell.fill = { type: "pattern", pattern: "solid", fgColor: { argb: LIGHT } }; cell.border = border; });
[4, 5, 6].forEach(k => tot.getCell(k).numFmt = '"US$ "#,##0'); [7, 8].forEach(k => tot.getCell(k).numFmt = "0.0");
p.addRow([]);
p.addRow(["Un contenedor 40HQ tiene unos 76 m³ interiores (~68 m³ útiles). Con Xiandai el mismo pedido no cabe: ajustar el mix o pedir su plan de carga."]).font = { italic: true };
p.columns = [{ width: 10 }, { width: 10 }, { width: 10 }, { width: 14 }, { width: 14 }, { width: 16 }, { width: 10 }, { width: 10 }];

// ---------------- 4. Pendientes con Xiandai
const q = wb.addWorksheet("Pedir a Xiandai");
title(q, "Lo que falta pedirle a Lina (Xiandai)", "Pedido por Pedro el 14-sep y no entregado, más lo recomendado");
header(q.addRow(["#", "Qué pedir", "Por qué", "Estado"]));
[
  ["Presión de trabajo y de rotura (bar/psi) por medida", "Comparar con Dongying (8/24 bar en succión)", "Pendiente"],
  ["Vacío máximo y radio mínimo de curvatura (succión)", "Uso en bombas y riego", "Pendiente"],
  ["Rango de temperatura y protección UV", "Clave para la vida útil al sol (el problema actual)", "Pendiente"],
  ["Ficha técnica / data sheet de cada manguera", "Respaldo por escrito", "Pendiente"],
  ["Material: PVC virgen, % de carga, tipo de plastificante (DOTP/DOP), aditivo UV", "Es lo que define la durabilidad", "Pendiente"],
  ["Muestras: succión 1\" y jardín 3/4\"", "Probar en terreno antes de comprar", "Pendiente"],
  ["Informe de ensayo del producto cotizado (no de otra manguera) y respaldo de REACH", "El SGS enviado es de otro producto", "Pendiente"],
  ["Plan de carga 40HQ y precio con embalaje (cajas/pallet)", "El precio es solo manguera; hoy el pedido no cabe", "Pendiente"],
  ["Certificado de Origen Form F", "Arancel 0% con TLC Chile-China (sin él, 6%)", "Pendiente"],
  ["Condiciones de pago y plazo de entrega; Trade Assurance de Alibaba", "Protección del pago", "Pendiente"],
  ["Mejor precio en jardín (1/2\", 3/4\", 1\")", "Está 51–95% sobre 2021", "Pendiente"],
].forEach((x, i) => { const row = q.addRow([i + 1, ...x]); row.eachCell(cell => { cell.border = border; cell.alignment = { wrapText: true, vertical: "top" }; });
  row.getCell(4).fill = { type: "pattern", pattern: "solid", fgColor: { argb: YEL } }; });
q.columns = [{ width: 5 }, { width: 60 }, { width: 50 }, { width: 12 }];

// ---------------- 5. Costos de importación
const k = wb.addWorksheet("Costos importación");
title(k, "Qué sumar al precio FOB", "Referencias generales; confirmar con el agente de aduana");
header(k.addRow(["Concepto", "Referencia", "Fuente"]));
[
  ["Precio FOB China", "Cotización del proveedor", "Cotizaciones"],
  ["Flete marítimo y seguro", "Pedir cotización al forwarder (40HQ Qingdao → San Antonio/Valparaíso)", "Pendiente"],
  ["Arancel aduanero", "0% con TLC Chile-China y Certificado de Origen Form F; 6% sin certificado", "aduana.cl · hencargochile.com"],
  ["IVA importación", "19% sobre CIF + arancel", "Norma general Chile"],
  ["Agente de aduana y gastos de puerto", "Según cotización del agente", "Pendiente"],
  ["Transporte a Curicó", "Según cotización", "Pendiente"],
].forEach(x => { const row = k.addRow(x); row.eachCell(cell => { cell.border = border; cell.alignment = { wrapText: true, vertical: "top" }; }); });
k.columns = [{ width: 32 }, { width: 70 }, { width: 30 }];
k.addRow([]);
k.addRow(["Fuentes:"]).font = { bold: true };
["https://www.aduana.cl/tratado-de-libre-comercio-chile-china/aduana/2007-02-28/100917.html",
 "https://hencargochile.com/tratados-de-libre-comercio-en-chile-como-usar-el-certificado-de-origen-en-tu-despacho-aduanero-para-pagar-0-de-arancel/",
 "https://wfpvc.en.alibaba.com/", "https://wfpvc.goldsupplier.com/about.html"].forEach(u => k.addRow([{ text: u, hyperlink: u }]).getCell(1).font = { color: { argb: "FF1F5FBF" }, underline: true });

wb.xlsx.writeFile(out).then(() => console.log("ok", out));

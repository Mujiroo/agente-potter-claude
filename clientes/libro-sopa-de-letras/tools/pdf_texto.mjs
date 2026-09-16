import { getDocument } from "pdfjs-dist/legacy/build/pdf.mjs";
import fs from "fs";
const [src, dst] = process.argv.slice(2);
const doc = await getDocument({ data: new Uint8Array(fs.readFileSync(src)), verbosity: 0 }).promise;
const out = { pages: [] };
for (let i = 1; i <= doc.numPages; i++) {
  const p = await doc.getPage(i);
  const vp = p.getViewport({ scale: 1 });
  const tc = await p.getTextContent();
  const fonts = new Set();
  const ops = await p.getOperatorList();
  out.pages.push({ w: vp.width, h: vp.height,
    items: tc.items.filter(t => t.str.trim()).map(t => [t.str, +t.transform[4].toFixed(1), +t.transform[5].toFixed(1), +Math.hypot(t.transform[0], t.transform[1]).toFixed(1)]) });
}
fs.writeFileSync(dst, JSON.stringify(out));
console.log(src.split("/").pop(), doc.numPages);

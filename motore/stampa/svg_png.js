// Conversione SVG → PNG con Chromium (Playwright), per le immagini delle appendici.
// Uso: node svg_png.js <svg> <png> [scala]. Le misure vengono da width/height (o viewBox) dell'SVG;
// scala predefinita 2 (una mappa larga 1240 px diventa 2480 px, circa 300 dpi su una pagina di 5,5").
const fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const [svg, png, s] = process.argv.slice(2);
  const testo = fs.readFileSync(svg, 'utf8');
  const radice = (testo.match(/<svg\b[^>]*>/) || [''])[0];
  const attr = (n) => { const m = radice.match(new RegExp('\\s' + n + '="([\\d.]+)')); return m ? parseFloat(m[1]) : null; };
  let w = attr('width'), h = attr('height');
  if (!w || !h) {
    const vb = (radice.match(/viewBox="([^"]+)"/) || [null, ''])[1].trim().split(/[\s,]+/).map(Number);
    if (vb.length === 4) { w = vb[2]; h = vb[3]; }
  }
  if (!w || !h) throw new Error('SVG senza width/height né viewBox: ' + svg);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: Math.ceil(w), height: Math.ceil(h) },
                                       deviceScaleFactor: parseFloat(s || '2') });
  await page.goto('file://' + svg, { waitUntil: 'networkidle' });
  await page.screenshot({ path: png, clip: { x: 0, y: 0, width: Math.ceil(w), height: Math.ceil(h) } });
  await browser.close();
})().catch((e) => { console.error(e.message || e); process.exit(1); });

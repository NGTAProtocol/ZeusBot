// Render di un file HTML in PDF con Chromium (Playwright). Uso: node print.js <html> <pdf>
// Il formato della pagina e i margini vengono dal CSS (@page): preferCSSPageSize.
const { chromium } = require('playwright');
(async () => {
  const [html, pdf] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: pdf, preferCSSPageSize: true, printBackground: true });
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });

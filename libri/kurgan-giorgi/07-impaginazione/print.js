// Uso: node print.js <file.html> <out.pdf> [footerTemplate]
const { chromium } = require(process.env.NODE_PATH_PW);
(async () => {
  const [html, out, footer] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: out, format: 'A5', preferCSSPageSize: true, printBackground: true,
    displayHeaderFooter: !!footer,
    headerTemplate: '<div></div>',
    footerTemplate: footer || '<div></div>',
  });
  await browser.close();
})();

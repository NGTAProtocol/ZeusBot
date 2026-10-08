// Ciclo di qualità: screenshot 375/768/1280, Lighthouse mobile+desktop, controlli automatici, fallback.
// Uso: node scripts/qa.mjs <id-output> [<id-output>...] [--runs 3] [--no-lh]
//   <id-output> = cartella in output/ (es. fornace-lume-cinematic)
import http from 'node:http';
import { createReadStream, existsSync, statSync } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import { join, extname, resolve, dirname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import zlib from 'node:zlib';
import { chromium } from 'playwright';
import { GL_ARGS } from './lib/browser.mjs';
import { runLighthouse } from './lib/lighthouse.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff', '.json': 'application/json', '.txt': 'text/plain', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.mp4': 'video/mp4' };

export const THRESHOLDS = {
  base: { mobile: 90, desktop: 90 },
  cinematic: { mobile: 75, desktop: 85 },
  baseline: { mobile: 0, desktop: 0 },
  a11y: 95,
  seo: 95
};

// server statico con gzip e cache lunga sugli asset (come Cloudflare Pages / Vercel / GitHub Pages)
export function serve(dir) {
  const root = resolve(dir);
  const server = http.createServer((req, res) => {
    let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    let file = resolve(join(root, p));
    if (!file.startsWith(root + sep) && file !== root) { res.writeHead(403).end(); return; }
    if (existsSync(file) && statSync(file).isDirectory()) file = join(file, 'index.html');
    if (!existsSync(file)) { res.writeHead(404).end('not found'); return; }
    const type = MIME[extname(file)] || 'application/octet-stream';
    const headers = { 'Content-Type': type, 'Cache-Control': file.includes('_assets') ? 'public, max-age=31536000, immutable' : 'no-cache' };
    const gz = /text|javascript|json|svg/.test(type) && /gzip/.test(req.headers['accept-encoding'] || '');
    if (gz) {
      res.writeHead(200, { ...headers, 'Content-Encoding': 'gzip', Vary: 'Accept-Encoding' });
      createReadStream(file).pipe(zlib.createGzip({ level: 9 })).pipe(res);
    } else {
      res.writeHead(200, headers);
      createReadStream(file).pipe(res);
    }
  });
  return new Promise((r) => server.listen(0, '127.0.0.1', () => r({ server, url: `http://127.0.0.1:${server.address().port}/` })));
}

const VIEWPORTS = [
  { w: 375, h: 812, mobile: true },
  { w: 768, h: 1024, mobile: true },
  { w: 1280, h: 800, mobile: false }
];

async function browse(url, id, level) {
  const browser = await chromium.launch({ args: GL_ARGS });
  const shotsDir = join(ROOT, 'reports', 'shots', id);
  await mkdir(shotsDir, { recursive: true });
  const out = { viewports: {}, checks: {} };
  try {
    for (const vp of VIEWPORTS) {
      const ctx = await browser.newContext({ viewport: { width: vp.w, height: vp.h }, isMobile: vp.mobile, hasTouch: vp.mobile, deviceScaleFactor: 1 });
      const page = await ctx.newPage();
      const errors = [];
      const hosts = new Set();
      page.on('pageerror', (e) => errors.push(e.message));
      page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
      page.on('request', (r) => hosts.add(new URL(r.url()).host));
      await page.goto(url, { waitUntil: 'networkidle' });
      // interazione simulata: nel CINEMATICO il 3D parte al primo gesto dell'utente
      if (vp.mobile) await page.evaluate(() => { dispatchEvent(new Event('touchstart')); dispatchEvent(new Event('scroll')); });
      else { await page.mouse.move(640, 400); await page.mouse.move(820, 300, { steps: 5 }); }
      await page.waitForTimeout(level === 'cinematic' ? 3500 : 1200);
      await page.screenshot({ path: join(shotsDir, `${vp.w}-hero.png`) });
      const state = await page.evaluate(() => ({
        overflowX: document.documentElement.scrollWidth > innerWidth + 1,
        h1: document.querySelectorAll('h1').length,
        canvasLive: !!document.querySelector('.hero__art.is-live'),
        fallback: document.documentElement.dataset.fallback || null,
        fonts: [...new Set([...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family.replace(/["']/g, '')))],
        smallTargets: [...document.querySelectorAll('a, button')].filter((el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && s.visibility !== 'hidden' && (r.height < 24 || r.width < 24) && !el.closest('.sr-only, .skip, .footer, p'); }).length
      }));
      // scorri tutta la pagina (fa comparire i contenuti), conta ciò che resta nascosto, poi screenshot a pagina intera
      await page.evaluate(async () => {
        for (let y = 0; y < document.body.scrollHeight; y += innerHeight * 0.6) { scrollTo(0, y); await new Promise((r) => setTimeout(r, 140)); }
        scrollTo(0, document.body.scrollHeight);
        await new Promise((r) => setTimeout(r, 2200)); // lascia finire le ultime comparse
      });
      const hidden = await page.evaluate(() =>
        [...document.querySelectorAll('[data-reveal]')].filter((el) => parseFloat(getComputedStyle(el).opacity) < 0.5).length +
        [...document.querySelectorAll('.mask-line > span')].filter((el) => Math.abs(new DOMMatrix(getComputedStyle(el).transform).m42) > 2).length);
      await page.evaluate(async () => { scrollTo(0, 0); await new Promise((r) => setTimeout(r, 600)); });
      await page.screenshot({ path: join(shotsDir, `${vp.w}-full.png`), fullPage: true });
      out.viewports[vp.w] = { ...state, errors, hiddenAfterScroll: hidden, externalHosts: [...hosts].filter((h) => !h.startsWith('127.0.0.1')) };
      await ctx.close();
    }
    // fallback: movimento ridotto
    {
      const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, reducedMotion: 'reduce' });
      const page = await ctx.newPage();
      await page.goto(url, { waitUntil: 'networkidle' });
      await page.waitForTimeout(1500);
      out.checks.reducedMotion = await page.evaluate(() => ({
        fallback: document.documentElement.dataset.fallback || null,
        canvas: !!document.querySelector('.hero__art canvas'),
        hiddenContent: [...document.querySelectorAll('[data-reveal]')].filter((el) => parseFloat(getComputedStyle(el).opacity) < 0.5).length
      }));
      await ctx.close();
    }
    // fallback: WebGL assente
    if (level === 'cinematic') {
      const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
      await ctx.addInitScript(() => { const orig = HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext = function (t, ...a) { return /webgl/.test(t) ? null : orig.call(this, t, ...a); }; });
      const page = await ctx.newPage();
      await page.goto(url, { waitUntil: 'networkidle' });
      await page.waitForTimeout(2500);
      out.checks.noWebGL = await page.evaluate(() => ({ fallback: document.documentElement.dataset.fallback || null, posterVisible: !!document.querySelector('.hero__poster svg'), canvas: !!document.querySelector('.hero__art canvas') }));
      await page.screenshot({ path: join(shotsDir, 'nowebgl-hero.png') });
      await ctx.close();
      // Save-Data
      const ctx2 = await browser.newContext({ viewport: { width: 375, height: 812 }, isMobile: true, hasTouch: true });
      await ctx2.addInitScript(() => Object.defineProperty(navigator, 'connection', { value: { saveData: true, effectiveType: '4g' } }));
      const p2 = await ctx2.newPage();
      await p2.goto(url, { waitUntil: 'networkidle' });
      await p2.waitForTimeout(1500);
      out.checks.saveData = await p2.evaluate(() => ({ fallback: document.documentElement.dataset.fallback || null, canvas: !!document.querySelector('.hero__art canvas') }));
      await ctx2.close();
    }
  } finally {
    await browser.close();
  }
  return out;
}

const median = (xs) => { const s = [...xs].sort((a, b) => a - b); return s[Math.floor(s.length / 2)]; };

export async function qa(id, { runs = 1, lh = true } = {}) {
  const dir = join(ROOT, 'output', id);
  if (!existsSync(dir)) throw new Error(`Manca output/${id}: esegui prima generate.mjs`);
  const level = id.endsWith('-cinematic') ? 'cinematic' : id.endsWith('-baseline') ? 'baseline' : 'base';
  const { server, url } = await serve(dir);
  const report = { id, level, url_tested: 'locale, server statico con gzip', at: new Date().toISOString() };
  try {
    report.browser = await browse(url, id, level);
    if (lh) {
      report.lighthouse = {};
      for (const ff of ['mobile', 'desktop']) {
        const all = [];
        for (let i = 0; i < runs; i++) all.push(await runLighthouse(url, { formFactor: ff }));
        const pick = all.find((r) => r.performance === median(all.map((x) => x.performance)));
        report.lighthouse[ff] = { ...pick, runs: all.map((r) => r.performance) };
      }
      if (level === 'cinematic') {
        // costo del 3D avviato subito (senza attendere un gesto): riportato per trasparenza
        report.lighthouseForce3d = {
          mobile: await runLighthouse(url + '?force3d', { formFactor: 'mobile' }),
          desktop: await runLighthouse(url + '?force3d', { formFactor: 'desktop' })
        };
      }
      const t = THRESHOLDS[level];
      const L = report.lighthouse;
      report.thresholds = {
        performanceMobile: { need: t.mobile, got: L.mobile.performance, ok: L.mobile.performance >= t.mobile },
        performanceDesktop: { need: t.desktop, got: L.desktop.performance, ok: L.desktop.performance >= t.desktop },
        accessibility: { need: THRESHOLDS.a11y, got: Math.min(L.mobile.accessibility, L.desktop.accessibility), ok: Math.min(L.mobile.accessibility, L.desktop.accessibility) >= THRESHOLDS.a11y },
        seo: { need: THRESHOLDS.seo, got: Math.min(L.mobile.seo, L.desktop.seo), ok: Math.min(L.mobile.seo, L.desktop.seo) >= THRESHOLDS.seo }
      };
      report.pass = level === 'baseline' ? null : Object.values(report.thresholds).every((x) => x.ok);
    }
  } finally {
    server.close();
  }
  await mkdir(join(ROOT, 'reports', 'qa'), { recursive: true });
  await writeFile(join(ROOT, 'reports', 'qa', `${id}.json`), JSON.stringify(report, null, 2) + '\n');
  return report;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const argv = process.argv.slice(2);
  const runs = argv.includes('--runs') ? Number(argv[argv.indexOf('--runs') + 1]) : 1;
  const lh = !argv.includes('--no-lh');
  const ids = argv.filter((a, i) => !a.startsWith('--') && argv[i - 1] !== '--runs');
  for (const id of ids) {
    const r = await qa(id, { runs, lh });
    const L = r.lighthouse;
    const v = r.browser.viewports;
    console.log(`${id}: ${L ? `LH mob P${L.mobile.performance} A${L.mobile.accessibility} S${L.mobile.seo} (LCP ${L.mobile.lcpMs}ms TBT ${L.mobile.tbtMs}ms) | desk P${L.desktop.performance} A${L.desktop.accessibility} S${L.desktop.seo}` : ''} | overflow375=${v[375].overflowX} errori=${Object.values(v).flatMap((x) => x.errors).length} esterni=${[...new Set(Object.values(v).flatMap((x) => x.externalHosts))].join(',') || 'nessuno'} canvas1280=${v[1280].canvasLive} | nascosti=${Object.values(v).map((x) => x.hiddenAfterScroll).join('/')} | ${!L ? 'Lighthouse non eseguito' : r.pass === null ? 'baseline' : r.pass ? 'SOGLIE OK' : 'SOGLIE NON RAGGIUNTE'}${r.lighthouseForce3d ? ` | force3d: mob P${r.lighthouseForce3d.mobile.performance} desk P${r.lighthouseForce3d.desktop.performance}` : ''}`);
  }
}

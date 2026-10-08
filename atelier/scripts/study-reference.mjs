// Studio di un sito di riferimento: registra SOLO informazioni pubbliche
// (librerie caricate, struttura, scroll, peso, resa a 3 larghezze, Lighthouse).
// Non salva codice, testi o immagini del sito: solo screenshot di analisi locali (non versionati).
// Uso: node scripts/study-reference.mjs <url> [<url>...]
import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import { GL_ARGS } from './lib/browser.mjs';
import { runLighthouse } from './lib/lighthouse.mjs';

const LIBS = {
  GSAP: { url: /gsap|greensock|TweenMax/i, global: 'gsap' },
  ScrollTrigger: { url: /ScrollTrigger/i, global: 'ScrollTrigger' },
  Lenis: { url: /lenis/i, global: 'Lenis', htmlClass: 'lenis' },
  'Locomotive Scroll': { url: /locomotive/i, global: 'LocomotiveScroll' },
  'Three.js': { url: /three(\.module)?(\.min)?\.js|\/three@/i, global: 'THREE', meta: '__THREE__' },
  Howler: { url: /howler/i, global: 'Howler' },
  React: { global: '__REACT_DEVTOOLS_GLOBAL_HOOK__', selector: '[data-reactroot],#__next,#root' },
  'Next.js': { global: '__NEXT_DATA__', selector: '#__next', url: /\/_next\// },
  Nuxt: { global: '__NUXT__', url: /\/_nuxt\// },
  Astro: { selector: 'astro-island', url: /\/_astro\// },
  SvelteKit: { url: /\/_app\/immutable\// },
  Webflow: { url: /webflow/i, selector: 'html[data-wf-site]' },
  Framer: { url: /framerusercontent|framer\.com/i }
};

const slug = (u) => new URL(u).hostname.replace(/[^a-z0-9]+/gi, '-');

async function study(url) {
  const out = { url, studied_at: new Date().toISOString(), reachable: false };
  const browser = await chromium.launch({ args: GL_ARGS });
  try {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await ctx.newPage();
    const requests = [];
    page.on('response', async (res) => {
      const len = Number(res.headers()['content-length'] || 0);
      requests.push({ url: res.url(), type: res.request().resourceType(), status: res.status(), bytes: len });
    });
    const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
    out.status = resp?.status();
    out.reachable = !!resp && resp.status() < 400;
    if (!out.reachable) return out;
    await page.waitForTimeout(1500);
    const scrollProbe = await page.evaluate(async () => {
      const before = window.scrollY;
      window.scrollTo(0, document.body.scrollHeight / 3);
      await new Promise((r) => setTimeout(r, 600));
      const sticky = [...document.querySelectorAll('body *')].filter((el) => ['sticky', 'fixed'].includes(getComputedStyle(el).position)).length;
      return { moved: window.scrollY !== before, docHeight: document.body.scrollHeight, stickyOrFixed: sticky, htmlClass: document.documentElement.className.slice(0, 200) };
    });
    const structure = await page.evaluate(() => ({
      sections: document.querySelectorAll('section').length,
      landmarks: ['header', 'nav', 'main', 'footer'].filter((t) => document.querySelector(t)),
      headings: { h1: document.querySelectorAll('h1').length, h2: document.querySelectorAll('h2').length, h3: document.querySelectorAll('h3').length },
      canvases: document.querySelectorAll('canvas').length,
      videos: document.querySelectorAll('video').length,
      fontsFamilies: [...new Set([...document.querySelectorAll('h1,h2,p,a,button')].slice(0, 200).map((el) => getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g, '').trim()))].slice(0, 6)
    }));
    const globals = await page.evaluate((libs) => {
      const found = {};
      for (const [name, d] of Object.entries(libs)) {
        found[name] = !!(
          (d.global && window[d.global]) ||
          (d.meta && window[d.meta]) ||
          (d.selector && document.querySelector(d.selector)) ||
          (d.htmlClass && document.documentElement.classList.contains(d.htmlClass))
        );
      }
      return found;
    }, Object.fromEntries(Object.entries(LIBS).map(([k, v]) => [k, { global: v.global, meta: v.meta, selector: v.selector, htmlClass: v.htmlClass }])));
    const scriptUrls = requests.filter((r) => r.type === 'script').map((r) => r.url);
    out.libraries = Object.fromEntries(
      Object.entries(LIBS).map(([name, d]) => [name, globals[name] || (d.url ? scriptUrls.some((u) => d.url.test(u)) : false)])
    );
    out.structure = structure;
    out.scroll = scrollProbe;
    out.network = {
      requests: requests.length,
      scripts: scriptUrls.length,
      transferBytesDeclared: requests.reduce((a, r) => a + r.bytes, 0),
      thirdPartyHosts: [...new Set(requests.map((r) => new URL(r.url).hostname).filter((h) => h !== new URL(url).hostname))].slice(0, 15)
    };
    const shotsDir = `reports/reference-shots/${slug(url)}`;
    await mkdir(shotsDir, { recursive: true });
    for (const w of [375, 768, 1280]) {
      await page.setViewportSize({ width: w, height: w === 375 ? 812 : w === 768 ? 1024 : 800 });
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(500);
      await page.screenshot({ path: `${shotsDir}/${w}.png` });
    }
    await ctx.close();
  } catch (err) {
    out.error = err.message.split('\n')[0];
  } finally {
    await browser.close();
  }
  if (out.reachable) {
    try {
      out.lighthouse = { mobile: await runLighthouse(url, { formFactor: 'mobile' }), desktop: await runLighthouse(url, { formFactor: 'desktop' }) };
    } catch (err) {
      out.lighthouseError = err.message.split('\n')[0];
    }
  }
  return out;
}

const urls = process.argv.slice(2);
if (!urls.length) {
  console.error('Uso: node scripts/study-reference.mjs <url> [...]');
  process.exit(2);
}
await mkdir('references/data', { recursive: true });
for (const url of urls) {
  const r = await study(url);
  await writeFile(`references/data/${slug(url)}.json`, JSON.stringify(r, null, 2) + '\n');
  console.log(slug(url), r.reachable ? 'OK' : `NON RAGGIUNGIBILE (${r.error || r.status})`, r.lighthouse ? `LH mob ${r.lighthouse.mobile.performance} desk ${r.lighthouse.desktop.performance}` : '');
}

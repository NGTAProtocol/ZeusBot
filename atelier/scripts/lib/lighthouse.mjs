// Esegue Lighthouse (mobile o desktop) su un URL e restituisce i punteggi principali.
import lighthouse from 'lighthouse';
import * as chromeLauncher from 'chrome-launcher';
import desktopConfig from 'lighthouse/core/config/desktop-config.js';
import { chromePath, GL_ARGS } from './browser.mjs';

export async function runLighthouse(url, { formFactor = 'mobile' } = {}) {
  const chrome = await chromeLauncher.launch({
    chromePath: chromePath(),
    chromeFlags: ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage', ...GL_ARGS]
  });
  try {
    const config = formFactor === 'desktop' ? desktopConfig : undefined;
    const result = await lighthouse(
      url,
      { port: chrome.port, output: 'json', logLevel: 'error', onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'] },
      config
    );
    const lhr = result.lhr;
    const score = (k) => Math.round((lhr.categories[k]?.score ?? 0) * 100);
    const num = (id) => lhr.audits[id]?.numericValue ?? null;
    const failing = (cat) =>
      lhr.categories[cat].auditRefs
        .filter((r) => r.weight > 0 && lhr.audits[r.id].score !== null && lhr.audits[r.id].score < 1)
        .map((r) => r.id);
    return {
      formFactor,
      performance: score('performance'),
      accessibility: score('accessibility'),
      bestPractices: score('best-practices'),
      seo: score('seo'),
      lcpMs: Math.round(num('largest-contentful-paint')),
      tbtMs: Math.round(num('total-blocking-time')),
      cls: Number((num('cumulative-layout-shift') ?? 0).toFixed(3)),
      fcpMs: Math.round(num('first-contentful-paint')),
      totalBytes: Math.round(num('total-byte-weight')),
      failingA11y: failing('accessibility'),
      failingSeo: failing('seo'),
      runtimeError: lhr.runtimeError?.code || null
    };
  } finally {
    await chrome.kill();
  }
}

// Aggrega misure reali (reports/qa/*.json, build-times, slop, distanza visiva) e la rubrica (reports/rubric.json)
// in reports/QUALITY.md e reports/metrics.json. Le tabelle di PROVA-DI-VALORE.md citano questi numeri.
import { readFileSync, readdirSync, writeFileSync, existsSync, statSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
import { slopReport } from './lib/slop.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const qaDir = join(ROOT, 'reports', 'qa');
const qa = Object.fromEntries(readdirSync(qaDir).filter((f) => f.endsWith('.json')).map((f) => [f.replace('.json', ''), JSON.parse(readFileSync(join(qaDir, f), 'utf8'))]));
const rubric = existsSync(join(ROOT, 'reports', 'rubric.json')) ? JSON.parse(readFileSync(join(ROOT, 'reports', 'rubric.json'), 'utf8')) : null;
const builds = JSON.parse(readFileSync(join(ROOT, 'reports', 'build-times.json'), 'utf8'));
const SLUGS = ['fornace-lume', 'quota-2100', 'nodo-sicuro'];
const CONFIGS = ['baseline', 'a', 'b', 'c'];
const LEVELS = ['base', 'cinematic'];
const kb = (b) => (b / 1024).toFixed(0);
const avg = (xs) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : NaN);
const f1 = (x) => (Number.isFinite(x) ? x.toFixed(1) : '—');

// --- distanza visiva tra gli hero (1280) dei 3 siti della stessa configurazione: misura "effetto template" ---
async function heroVectors() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const vec = {};
  for (const id of Object.keys(qa)) {
    const png = join(ROOT, 'reports', 'shots', id, '1280-hero.png');
    if (!existsSync(png)) continue;
    const b64 = readFileSync(png).toString('base64');
    vec[id] = await page.evaluate(async (src) => {
      const img = new Image();
      img.src = src;
      await img.decode();
      const c = document.createElement('canvas');
      c.width = 64; c.height = 40;
      const x = c.getContext('2d');
      x.drawImage(img, 0, 0, 64, 40);
      return [...x.getImageData(0, 0, 64, 40).data].filter((_, i) => i % 4 !== 3);
    }, `data:image/png;base64,${b64}`);
  }
  await browser.close();
  return vec;
}
const dist = (a, b) => avg(a.map((v, i) => Math.abs(v - b[i]))) / 255 * 100;

const vectors = await heroVectors();
const metrics = { perConfig: {}, sites: {} };
for (const s of SLUGS) for (const c of CONFIGS) for (const l of LEVELS) {
  const id = `${s}-${c}-${l}`;
  const r = qa[id];
  const out = join(ROOT, 'output', id);
  const authored = c === 'baseline'
    ? [join(ROOT, 'baseline', `${s}-${l}.astro`)]
    : [join(ROOT, 'bibbia', `${s}-${c}.json`), join(ROOT, 'content', `${s}-${c}.json`)];
  const bytes = authored.filter(existsSync).reduce((a, p) => a + statSync(p).size, 0);
  metrics.sites[id] = {
    slug: s, config: c, level: l,
    perfMobile: r?.lighthouse?.mobile.performance, perfDesktop: r?.lighthouse?.desktop.performance,
    a11y: r?.lighthouse ? Math.min(r.lighthouse.mobile.accessibility, r.lighthouse.desktop.accessibility) : undefined,
    seo: r?.lighthouse ? Math.min(r.lighthouse.mobile.seo, r.lighthouse.desktop.seo) : undefined,
    lcpMobile: r?.lighthouse?.mobile.lcpMs, tbtMobile: r?.lighthouse?.mobile.tbtMs, bytes: r?.lighthouse?.mobile.totalBytes,
    pass: r?.pass, slop: existsSync(out) ? slopReport(out) : null,
    buildMs: builds.find((b) => b.id === id)?.ms,
    authoredBytes: bytes, estTokens: Math.round(bytes / 4)
  };
}
for (const c of CONFIGS) for (const l of LEVELS) {
  const rows = SLUGS.map((s) => metrics.sites[`${s}-${c}-${l}`]);
  const ids = SLUGS.map((s) => `${s}-${c}-${l}`).filter((id) => vectors[id]);
  const pairs = [];
  for (let i = 0; i < ids.length; i++) for (let j = i + 1; j < ids.length; j++) pairs.push(dist(vectors[ids[i]], vectors[ids[j]]));
  metrics.perConfig[`${c}-${l}`] = {
    perfMobile: avg(rows.map((r) => r.perfMobile).filter(Number.isFinite)),
    perfDesktop: avg(rows.map((r) => r.perfDesktop).filter(Number.isFinite)),
    a11y: avg(rows.map((r) => r.a11y).filter(Number.isFinite)),
    seo: avg(rows.map((r) => r.seo).filter(Number.isFinite)),
    passed: rows.filter((r) => r.pass).length,
    slop: rows.reduce((a, r) => a + (r.slop?.totale || 0), 0),
    distinct: avg(pairs),
    buildS: avg(rows.map((r) => r.buildMs).filter(Number.isFinite)) / 1000,
    estTokens: avg(rows.map((r) => r.estTokens))
  };
}
if (rubric) {
  for (const it of rubric.iterations) for (const row of it.rows) row.avg = avg(row.scores);
  const last = rubric.iterations.at(-1);
  for (const c of CONFIGS) for (const l of LEVELS) {
    const rows = last.rows.filter((r) => r.config === c && r.level === l);
    metrics.perConfig[`${c}-${l}`].rubric = avg(rows.map((r) => r.avg));
    metrics.perConfig[`${c}-${l}`].rubricByCrit = rubric.criteria.map((_, k) => avg(rows.map((r) => r.scores[k])));
  }
}
writeFileSync(join(ROOT, 'reports', 'metrics.json'), JSON.stringify(metrics, null, 2) + '\n');

let md = `# Report di qualità (generato da scripts/report.mjs)\n\n`;
md += `**Come si misura:**\n- Lighthouse 13.5.0 su Chromium headless (WebGL software SwiftShader), una run per profilo, con un server statico locale gzip.\n- Mobile = profilo Lighthouse predefinito (Moto G, 4G lento simulato, CPU 4x); desktop = preset desktop.\n- Soglie: BASE ≥ 90 mobile e desktop; CINEMATICO ≥ 75 mobile e ≥ 85 desktop; accessibilità e SEO ≥ 95.\n- Le baseline sono misurate con le stesse soglie, ma solo per confronto.\n\n`;
md += `## Lighthouse per sito\n\n| Sito | Config | Livello | Perf mob | Perf desk | A11y | SEO | LCP mob | TBT mob | Peso | Soglie |\n|---|---|---|---|---|---|---|---|---|---|---|\n`;
for (const s of SLUGS) for (const c of CONFIGS) for (const l of LEVELS) {
  const m = metrics.sites[`${s}-${c}-${l}`];
  if (m.perfMobile === undefined) { md += `| ${s} | ${c} | ${l} | non misurato | | | | | | | |\n`; continue; }
  md += `| ${s} | ${c.toUpperCase()} | ${l.toUpperCase()} | ${m.perfMobile} | ${m.perfDesktop} | ${m.a11y} | ${m.seo} | ${(m.lcpMobile / 1000).toFixed(2)} s | ${m.tbtMobile} ms | ${kb(m.bytes)} KB | ${m.pass ? '✅' : '❌'} |\n`;
}
const f3d = Object.entries(qa).filter(([, r]) => r.lighthouseForce3d);
if (f3d.length) {
  md += `\n### Costo del 3D avviato subito (\`?force3d\`)\n\nIl 3D parte al primo gesto e gira in un Web Worker. Lighthouse non interagisce e non conta il lavoro del worker. Qui il 3D è forzato al caricamento.\n\n| Sito | Perf mob | TBT mob | Perf desk |\n|---|---|---|---|\n`;
  for (const [id, r] of f3d) md += `| ${id} | ${r.lighthouseForce3d.mobile.performance} | ${r.lighthouseForce3d.mobile.tbtMs} ms | ${r.lighthouseForce3d.desktop.performance} |\n`;
}
md += `\n## Controlli automatici (Playwright)\n\n| Sito | Overflow 375 | Errori console | Host esterni | Nascosti dopo scroll | 3D attivo 1280 | Reduced-motion | No-WebGL | Save-Data |\n|---|---|---|---|---|---|---|---|---|\n`;
for (const s of SLUGS) for (const c of CONFIGS) for (const l of LEVELS) {
  const r = qa[`${s}-${c}-${l}`];
  if (!r) continue;
  const vp = r.browser.viewports;
  const k = r.browser.checks;
  md += `| ${s}-${c}-${l} | ${vp[375].overflowX ? '❌' : '✅'} | ${Object.values(vp).flatMap((x) => x.errors).length} | ${[...new Set(Object.values(vp).flatMap((x) => x.externalHosts))].join(', ') || 'nessuno'} | ${[375, 768, 1280].map((w) => vp[w].hiddenAfterScroll).join('/')} | ${vp[1280].canvasLive ? 'sì' : 'no'} | ${k.reducedMotion ? `nascosti ${k.reducedMotion.hiddenContent}, canvas ${k.reducedMotion.canvas ? 'sì' : 'no'}` : '—'} | ${k.noWebGL ? `firma/poster ${k.noWebGL.posterVisible ? 'sì' : 'no'}` : '—'} | ${k.saveData ? `canvas ${k.saveData.canvas ? 'sì' : 'no'}` : '—'} |\n`;
}
md += `\n## Rilevatore di slop sull'HTML compilato (\`scripts/lib/slop.mjs\`)\n\nConta i segnali della lista nera (§10) e i link finti (§9).\n\n**Limite:** il lint di Atelier fa rispettare proprio queste regole. Lo zero delle configurazioni A/B/C è quindi atteso, non una prova indipendente di qualità.\n\n| Sito | Config | Livello | Totale | Dettaglio (≠0) |\n|---|---|---|---|---|\n`;
for (const s of SLUGS) for (const c of CONFIGS) for (const l of LEVELS) {
  const sl = metrics.sites[`${s}-${c}-${l}`].slop;
  if (!sl) continue;
  md += `| ${s} | ${c} | ${l} | ${sl.totale} | ${Object.entries(sl).filter(([k, v]) => v && k !== 'totale').map(([k, v]) => `${k} ${v}`).join(', ') || '—'} |\n`;
}
md += `\n## Confronto per configurazione (medie sui 3 siti)\n\n- **Distanza visiva:** differenza media dei pixel (0-100) tra gli hero a 1280 px dei 3 siti della stessa configurazione, ridotti a 64×40. Più è alta, più i siti sono diversi tra loro (meno "effetto template").\n- **Token (stima):** byte scritti a mano per sito (Bibbia + contenuti, oppure il file della baseline) diviso 4. Stima i soli token di output; non sono token misurati dall'API.\n\n| Config | Livello | Perf mob | Perf desk | A11y | SEO | Soglie superate | Slop | Distanza visiva | Build | Token stimati/sito |${rubric ? ' Rubrica |' : ''}\n|---|---|---|---|---|---|---|---|---|---|---|${rubric ? '---|' : ''}\n`;
for (const c of CONFIGS) for (const l of LEVELS) {
  const p = metrics.perConfig[`${c}-${l}`];
  md += `| ${c.toUpperCase()} | ${l.toUpperCase()} | ${f1(p.perfMobile)} | ${f1(p.perfDesktop)} | ${f1(p.a11y)} | ${f1(p.seo)} | ${p.passed}/3 | ${p.slop} | ${f1(p.distinct)} | ${p.buildS.toFixed(1)} s | ~${Math.round(p.estTokens)} |${rubric ? ` **${f1(p.rubric)}** |` : ''}\n`;
}
if (rubric) {
  md += `\n## Rubrica 1-10 (AUTOVALUTAZIONE)\n\n${rubric.disclaimer}\n\nCriteri: ${rubric.criteria.join(', ')}.\n\n`;
  for (const it of rubric.iterations) {
    md += `### ${it.name}\n\n| Sito | Config | Livello | ${rubric.criteria.join(' | ')} | Media |\n|---|---|---|${rubric.criteria.map(() => '---').join('|')}|---|\n`;
    for (const row of it.rows) md += `| ${row.site} | ${row.config.toUpperCase()} | ${row.level} | ${row.scores.join(' | ')} | **${row.avg.toFixed(1)}** |\n`;
    if (it.notes) md += `\n${it.notes}\n`;
    md += '\n';
  }
  md += `### Media per criterio (ultima iterazione)\n\n| Config | Livello | ${rubric.criteria.join(' | ')} |\n|---|---|${rubric.criteria.map(() => '---').join('|')}|\n`;
  for (const c of CONFIGS) for (const l of LEVELS) md += `| ${c.toUpperCase()} | ${l} | ${metrics.perConfig[`${c}-${l}`].rubricByCrit.map(f1).join(' | ')} |\n`;
}
const notes = join(ROOT, 'reports', 'quality-notes.md');
if (existsSync(notes)) md += '\n' + readFileSync(notes, 'utf8');
writeFileSync(join(ROOT, 'reports', 'QUALITY.md'), md);
console.log('scritto reports/QUALITY.md e reports/metrics.json');

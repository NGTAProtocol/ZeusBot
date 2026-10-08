// Aggrega reports/qa/*.json (misure reali) e reports/rubric.json (autovalutazione) in reports/QUALITY.md
import { readFileSync, readdirSync, writeFileSync, existsSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const qaDir = join(ROOT, 'reports', 'qa');
const qa = Object.fromEntries(readdirSync(qaDir).filter((f) => f.endsWith('.json')).map((f) => [f.replace('.json', ''), JSON.parse(readFileSync(join(qaDir, f), 'utf8'))]));
const rubric = existsSync(join(ROOT, 'reports', 'rubric.json')) ? JSON.parse(readFileSync(join(ROOT, 'reports', 'rubric.json'), 'utf8')) : null;
const slugs = [...new Set(Object.keys(qa).map((k) => k.replace(/-(base|cinematic|baseline)$/, '')))].sort();
const kb = (b) => (b / 1024).toFixed(0);

let md = `# Report di qualità (generato da scripts/report.mjs)\n\n`;
md += `Misure: Lighthouse ${'13.5.0'} su Chromium headless (rendering WebGL software SwiftShader), server statico locale con gzip, mediana di più run (indicate). `;
md += `Mobile = profilo Lighthouse predefinito (Moto G, rete 4G lenta simulata, CPU 4x); desktop = preset desktop.\n\n`;
md += `## Lighthouse\n\n| Sito | Variante | Perf mobile | Perf desktop | Accessibilità | SEO | LCP mobile | TBT mobile | Peso | Soglie |\n|---|---|---|---|---|---|---|---|---|---|\n`;
for (const s of slugs) {
  for (const v of ['baseline', 'base', 'cinematic']) {
    const r = qa[`${s}-${v}`];
    if (!r?.lighthouse) continue;
    const L = r.lighthouse;
    const pass = r.pass === null ? '—' : r.pass ? '✅' : '❌';
    md += `| ${s} | ${v.toUpperCase()} | ${L.mobile.performance} (${L.mobile.runs.join('/')}) | ${L.desktop.performance} (${L.desktop.runs.join('/')}) | ${Math.min(L.mobile.accessibility, L.desktop.accessibility)} | ${Math.min(L.mobile.seo, L.desktop.seo)} | ${(L.mobile.lcpMs / 1000).toFixed(2)} s | ${L.mobile.tbtMs} ms | ${kb(L.mobile.totalBytes)} KB | ${pass} |\n`;
  }
}
md += `\n### Costo del 3D avviato subito (\`?force3d\`), solo CINEMATICO\n\nNel CINEMATICO il 3D parte al primo gesto dell'utente; Lighthouse non interagisce, quindi la tabella sopra misura la pagina **prima** del 3D. Qui il 3D è forzato al caricamento.\n\n**Attenzione:** il 3D gira in un Web Worker (OffscreenCanvas). Lighthouse non conta né il peso del worker (~133 KB gzip, Three.js incluso) né il suo lavoro CPU, che non blocca il thread principale. Questi numeri misurano quindi solo l'impatto sul thread principale, non il costo totale sul dispositivo. Verificato con Playwright: con \`?force3d\` il 3D è attivo dopo circa 3,2 s.\n\n| Sito | Perf mobile | TBT mobile | Perf desktop | TBT desktop | Peso desktop (senza il worker) |\n|---|---|---|---|---|---|\n`;
for (const s of slugs) {
  const f = qa[`${s}-cinematic`]?.lighthouseForce3d;
  if (f) md += `| ${s} | ${f.mobile.performance} | ${f.mobile.tbtMs} ms | ${f.desktop.performance} | ${f.desktop.tbtMs} ms | ${kb(f.desktop.totalBytes)} KB |\n`;
}
md += `\n## Controlli automatici (Playwright)\n\n| Sito | Variante | Overflow a 375 | Errori console | Host esterni | Contenuti nascosti dopo lo scroll (375/768/1280) | 3D attivo a 1280 | Fallback reduced-motion | Fallback no-WebGL | Fallback Save-Data |\n|---|---|---|---|---|---|---|---|---|---|\n`;
for (const s of slugs) {
  for (const v of ['baseline', 'base', 'cinematic']) {
    const r = qa[`${s}-${v}`];
    if (!r) continue;
    const vp = r.browser.viewports;
    const c = r.browser.checks;
    md += `| ${s} | ${v.toUpperCase()} | ${vp[375].overflowX ? '❌' : '✅ no'} | ${Object.values(vp).flatMap((x) => x.errors).length} | ${[...new Set(Object.values(vp).flatMap((x) => x.externalHosts))].join(', ') || 'nessuno'} | ${[375, 768, 1280].map((w) => vp[w].hiddenAfterScroll).join('/')} | ${v === 'cinematic' ? (vp[1280].canvasLive ? '✅' : '❌') : '—'} | ${c.reducedMotion ? `${c.reducedMotion.fallback || 'n/d'}, nascosti ${c.reducedMotion.hiddenContent}, canvas ${c.reducedMotion.canvas ? 'sì' : 'no'}` : '—'} | ${c.noWebGL ? `poster ${c.noWebGL.posterVisible ? 'sì' : 'no'}, canvas ${c.noWebGL.canvas ? 'sì' : 'no'}` : '—'} | ${c.saveData ? `${c.saveData.fallback}, canvas ${c.saveData.canvas ? 'sì' : 'no'}` : '—'} |\n`;
  }
}
if (rubric) {
  md += `\n## Rubrica 1-10 (AUTOVALUTAZIONE)\n\n${rubric.disclaimer}\n\n`;
  const crit = rubric.criteria;
  for (const it of rubric.iterations) {
    md += `### ${it.name}\n\n| Sito | Variante | ${crit.join(' | ')} | Media |\n|---|---|${crit.map(() => '---').join('|')}|---|\n`;
    for (const row of it.rows) {
      const avg = row.scores.reduce((a, b) => a + b, 0) / row.scores.length;
      md += `| ${row.site} | ${row.variant} | ${row.scores.join(' | ')} | **${avg.toFixed(1)}** |\n`;
    }
    if (it.notes) md += `\n${it.notes}\n`;
    md += '\n';
  }
}
const notes = join(ROOT, 'reports', 'quality-notes.md');
if (existsSync(notes)) md += '\n' + readFileSync(notes, 'utf8');
writeFileSync(join(ROOT, 'reports', 'QUALITY.md'), md);
console.log('scritto reports/QUALITY.md');

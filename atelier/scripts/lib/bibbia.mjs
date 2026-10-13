// Fase Bibbia: validazione del file bibbia/<slug>-<config>.json e generazione dei design token (:root).
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { contrast } from './directions.mjs';

export const CONFIGS = {
  a: { label: 'A', skills: ['frontend-design'] },
  b: { label: 'B', skills: ['frontend-design', 'impeccable'] },
  c: { label: 'C', skills: ['frontend-design', 'taste-skill', 'emil-design-eng', 'emil-animate'] }
};
export const SIGNATURES_CSS = ['layers', 'drip', 'contours', 'lattice', 'turn'];
export const SIGNATURES_3D = ['blob', 'terrain', 'points', 'ribbons', 'rings'];
export const LAYOUTS = ['editorial', 'panels', 'index', 'manifesto', 'catalogue', 'monolith', 'blueprint'];

const hex = /^#[0-9a-f]{6}$/i;

function checkPalette(p, where, problems) {
  for (const k of ['bg', 'surface', 'ink', 'muted', 'accent', 'accent2']) if (!hex.test(p?.[k] || '')) problems.push(`${where}.${k}: colore esadecimale mancante`);
  if (problems.length) return;
  for (const k of ['ink', 'muted']) for (const b of ['bg', 'surface']) {
    const c = contrast(p[k], p[b]);
    if (c < 4.5) problems.push(`${where}: ${k} su ${b} = ${c.toFixed(2)} (< 4,5 AA)`);
  }
  for (const b of ['bg', 'surface']) {
    const c = contrast(p.accent, p[b]);
    if (c < 3) problems.push(`${where}: accent su ${b} = ${c.toFixed(2)} (< 3 per testo grande/componenti)`);
  }
  // bottone primario: testo bg su fondo ink
  if (contrast(p.bg, p.ink) < 4.5) problems.push(`${where}: bottone primario (bg su ink) < 4,5`);
}

export function validateBibbia(b, root) {
  const problems = [];
  const words = (s) => String(s || '').trim().split(/\s+/).filter(Boolean).length;
  if (!b.concept || words(b.concept) < 8 || words(b.concept) > 40) problems.push('concept: una frase di 8-40 parole');
  if (/[.!?].+[.!?]/.test(String(b.concept || '').trim().replace(/[.!?]$/, ''))) problems.push('concept: deve essere UNA frase');
  if (!Array.isArray(b.personality?.adjectives) || b.personality.adjectives.length !== 3) problems.push('personality.adjectives: esattamente 3');
  if (!b.personality?.not) problems.push('personality.not: cosa NON è');
  const s = b.signature || {};
  if (!['css', '3d'].includes(s.kind)) problems.push('signature.kind: css | 3d');
  if (s.kind === 'css' && !SIGNATURES_CSS.includes(s.id)) problems.push(`signature.id CSS: ${SIGNATURES_CSS.join(', ')}`);
  if (s.kind === '3d' && !SIGNATURES_3D.includes(s.id)) problems.push(`signature.id 3D: ${SIGNATURES_3D.join(', ')}`);
  if (s.kind === '3d' && !s.why_3d) problems.push('signature.why_3d: perché il 3D È la firma (Bibbia §14.3)');
  if (s.kind === 'css' && !SIGNATURES_CSS.includes(s.fallback_id || s.id)) problems.push('signature.fallback_id non valido');
  if (s.kind === '3d' && !SIGNATURES_CSS.includes(s.fallback_id)) problems.push('signature.fallback_id: firma CSS da usare nel BASE e come fallback');
  if (!s.description || words(s.description) < 8) problems.push('signature.description: cosa vede, cosa fa, perché dimostra il concept');
  const t = b.tokens || {};
  checkPalette(t.palette, 'tokens.palette', problems);
  if (t.dark) checkPalette(t.dark, 'tokens.dark', problems);
  if (!t.palette_source || Object.keys(t.palette_source).length < 3) problems.push('tokens.palette_source: da dove viene ogni colore (almeno 3)');
  if (!['contenuta', 'impegnata', 'piena', 'immersa'].includes(t.color_strategy)) problems.push('tokens.color_strategy: contenuta | impegnata | piena | immersa');
  const fams = new Set();
  for (const role of ['display', 'body']) {
    const f = t.fonts?.[role];
    if (!f?.pkg || !f.family) { problems.push(`tokens.fonts.${role}: pkg e family`); continue; }
    fams.add(f.family);
    if (root) {
      const pj = join(root, 'node_modules', f.pkg, 'package.json');
      if (!existsSync(pj)) problems.push(`font ${f.pkg} non installato`);
      else {
        const lic = JSON.parse(readFileSync(pj, 'utf8')).license;
        if (!/OFL|Apache/i.test(lic || '')) problems.push(`font ${f.pkg}: licenza ${lic} non open`);
        const files = f.variable ? [`${f.axis || 'wght'}.css`] : (f.weights || []).map((w) => `latin-${w}.css`);
        for (const file of files) if (!existsSync(join(root, 'node_modules', f.pkg, file))) problems.push(`font ${f.pkg}: manca ${file}`);
      }
    }
  }
  if (fams.size > 2) problems.push('massimo 2 famiglie di font');
  if (!LAYOUTS.includes(b.layout)) problems.push(`layout: ${LAYOUTS.join(', ')}`);
  if (!Array.isArray(b.unknowns)) problems.push('unknowns: elenco (anche vuoto) dei dati mancanti');
  if (!Array.isArray(b.skills_used)) problems.push('skills_used: elenco delle skill applicate');
  return problems;
}

const EASE = { out: 'cubic-bezier(.23,1,.32,1)', inout: 'cubic-bezier(.77,0,.175,1)', drawer: 'cubic-bezier(.32,.72,0,1)', linear: 'linear' };
export const GSAP_EASE = { out: 'expo.out', inout: 'power3.inOut', drawer: 'power3.out', linear: 'none' };

/** CSS dei token per :root (+ modo scuro se definito) */
export function tokensCss(b) {
  const t = b.tokens;
  const imports = [];
  for (const role of ['display', 'body']) {
    const f = t.fonts[role];
    if (f.variable) imports.push(`@import "${f.pkg}/${f.axis || 'wght'}.css";`);
    else for (const w of f.weights) imports.push(`@import "${f.pkg}/latin-${w}.css";`);
  }
  const ty = t.type || {};
  const sp = t.space || {};
  const mo = t.motion || {};
  const p = t.palette;
  const darkBg = contrast(p.bg, '#000000') < contrast(p.bg, '#ffffff');
  const colors = (q) => `--c-bg: ${q.bg}; --c-surface: ${q.surface}; --c-ink: ${q.ink}; --c-muted: ${q.muted}; --c-accent: ${q.accent}; --c-accent2: ${q.accent2};`;
  let css = `${[...new Set(imports)].join('\n')}
:root {
  ${colors(p)}
  --f-display: "${t.fonts.display.family}", ${t.fonts.display.fallback || 'system-ui, sans-serif'};
  --f-body: "${t.fonts.body.family}", ${t.fonts.body.fallback || 'system-ui, sans-serif'};
  --scale: ${ty.scale || 1.25}; --body-size: ${ty.body_size || '1.0625rem'}; --body-leading: ${ty.body_leading || 1.6};
  --display-weight: ${ty.display_weight || 700}; --display-tracking: ${ty.display_tracking || '-0.02em'}; --display-leading: ${ty.display_leading || 1};
  --display-stretch: ${ty.display_stretch || '100%'}; --char-width: ${ty.char_width || 0.56}; --display-max: ${ty.display_max || '6rem'};
  --space-unit: 4px;
  --section: ${sp.section || 'clamp(96px, 12vw, 160px)'}; --gutter: ${sp.gutter || 'clamp(16px, 4vw, 48px)'}; --measure: ${sp.measure || '62ch'};
  --radius: ${t.radius ?? '0px'};
  --dur-micro: ${mo.micro_ms || 200}ms; --dur: ${(mo.sequence_ms || 900) / 1000}; --distance: ${mo.distance ?? 24}px;
  --ease-css: ${EASE[mo.ease] || EASE.out}; --ease-move: ${EASE.inout};
  --scheme: ${darkBg ? 'dark' : 'light'};
}
`;
  if (t.dark) {
    css += `@media (prefers-color-scheme: dark) { :root { ${colors(t.dark)} --scheme: dark; } }\n`;
  }
  return css;
}

export function loadBibbia(root, slug, config) {
  const p = join(root, 'bibbia', `${slug}-${config}.json`);
  if (!existsSync(p)) throw new Error(`Manca bibbia/${slug}-${config}.json: la fase Bibbia (concept, personalità, firma) va fatta prima del codice.`);
  const b = JSON.parse(readFileSync(p, 'utf8'));
  const problems = validateBibbia(b, root);
  if (problems.length) throw new Error(`Bibbia ${slug}-${config} non valida:\n- ${problems.join('\n- ')}`);
  return b;
}

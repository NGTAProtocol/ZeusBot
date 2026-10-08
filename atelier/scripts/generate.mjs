// Pipeline Atelier: brief JSON → direzione artistica → contenuti → sito Astro statico.
// Uso:
//   node scripts/generate.mjs <brief.json> --level base|cinematic
//   node scripts/generate.mjs <brief.json> --baseline     (sito "baseline" scritto a mano, stesso stack)
// I contenuti (struttura + copy) stanno in content/<slug>.json e vengono scritti dall'agente
// seguendo .claude/skills/atelier/SKILL.md; questo script li valida e li impagina.
import { readFile, writeFile, mkdir, rm, cp, readdir, unlink } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { pickDirection, getDirection, contrast } from './lib/directions.mjs';
import { lintContent } from './lib/lint.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ENGINE = join(ROOT, 'engine');
const GEN = join(ENGINE, 'src', 'generated');

function parseArgs(argv) {
  const args = { brief: null, level: 'base', baseline: false, out: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--level') args.level = argv[++i];
    else if (a === '--baseline') args.baseline = true;
    else if (a === '--out') args.out = argv[++i];
    else if (!args.brief) args.brief = a;
  }
  return args;
}

export function validateBrief(b) {
  const required = ['slug', 'business', 'sector', 'audience', 'goal', 'tone', 'language', 'pages', 'level'];
  const missing = required.filter((k) => b[k] === undefined || b[k] === '');
  if (missing.length) throw new Error(`Brief incompleto: mancano ${missing.join(', ')}`);
  if (!/^[a-z0-9-]+$/.test(b.slug)) throw new Error('slug: solo minuscole, cifre e trattini');
  if (!['base', 'cinematic', 'video-scroll'].includes(b.level)) throw new Error('level: base | cinematic | video-scroll');
  if (!Array.isArray(b.pages) || !b.pages.includes('home')) throw new Error('pages deve includere "home"');
  return b;
}

function themeCss(d) {
  const imports = [];
  for (const role of ['display', 'body']) {
    const f = d.fonts[role];
    if (f.variable) imports.push(`@import "${f.pkg}/wdth.css";`);
    else for (const w of f.weights) imports.push(`@import "${f.pkg}/${w}.css";`);
  }
  const p = d.palette;
  const dark = contrast(p.bg, '#000000') < contrast(p.bg, '#ffffff');
  const easeCss = { 'expo.out': 'cubic-bezier(.16,1,.3,1)', 'power3.inOut': 'cubic-bezier(.65,0,.35,1)', 'power2.out': 'cubic-bezier(.33,1,.68,1)', 'sine.inOut': 'cubic-bezier(.37,0,.63,1)', 'power4.out': 'cubic-bezier(.25,1,.5,1)', 'power2.inOut': 'cubic-bezier(.45,0,.55,1)', 'power1.inOut': 'cubic-bezier(.45,.05,.55,.95)', none: 'linear' };
  return `${[...new Set(imports)].join('\n')}
:root {
  --c-bg: ${p.bg}; --c-surface: ${p.surface}; --c-ink: ${p.ink}; --c-muted: ${p.muted}; --c-accent: ${p.accent}; --c-accent2: ${p.accent2};
  --f-display: "${d.fonts.display.family}", ${d.fonts.display.fallback};
  --f-body: "${d.fonts.body.family}", ${d.fonts.body.fallback};
  --scale: ${d.type.scale}; --body-size: ${d.type.bodySize}; --body-leading: ${d.type.bodyLeading};
  --display-tracking: ${d.type.displayTracking}; --display-leading: ${d.type.displayLeading};
  --display-weight: ${d.type.displayWeight || d.fonts.display.weights.filter(Number.isFinite).at(-1) || 400};
  --display-stretch: ${d.type.displayStretch || '100%'};
  --char-width: ${d.type.charWidth || 0.56};
  --section: ${d.space.section}; --gutter: ${d.space.gutter}; --measure: ${d.space.measure};
  --radius: ${d.radius};
  --dur: ${d.motion.duration}; --distance: ${d.motion.distance}px; --ease-css: ${easeCss[d.motion.ease] || 'ease'};
  --scheme: ${dark ? 'dark' : 'light'};
  --grain: ${dark ? 0.09 : 0.06};
}
`;
}

const BASELINE_STUB = `---\n---\n`;

// Astro emette tutti gli script del layout anche quando una pagina non li usa (es. i chunk del CINEMATICO
// nel BASE). Qui si eliminano i .js non raggiungibili dall'HTML, seguendo import statici, dinamici e worker.
export async function pruneUnreferencedJs(outDir) {
  const assets = join(outDir, '_assets');
  if (!existsSync(assets)) return [];
  const files = (await readdir(assets)).filter((f) => f.endsWith('.js'));
  const htmlFiles = [];
  const walk = async (d) => {
    for (const e of await readdir(d, { withFileTypes: true })) {
      const p = join(d, e.name);
      if (e.isDirectory()) await walk(p);
      else if (e.name.endsWith('.html')) htmlFiles.push(p);
    }
  };
  await walk(outDir);
  const refsIn = (text) => files.filter((f) => text.includes(f));
  const seen = new Set();
  const queue = [];
  for (const h of htmlFiles) refsIn(await readFile(h, 'utf8')).forEach((f) => queue.push(f));
  while (queue.length) {
    const f = queue.pop();
    if (seen.has(f)) continue;
    seen.add(f);
    refsIn(await readFile(join(assets, f), 'utf8')).forEach((g) => queue.push(g));
  }
  const removed = files.filter((f) => !seen.has(f));
  for (const f of removed) await unlink(join(assets, f));
  return removed;
}

export async function generate({ brief: briefPath, level, baseline, out }) {
  const brief = validateBrief(JSON.parse(await readFile(resolve(briefPath), 'utf8')));
  const slug = brief.slug;
  if (level === 'video-scroll') throw new Error('VIDEO-SCROLL richiede asset forniti dal cliente in assets/<slug>/scroll/: non generiamo media a pagamento.');
  const direction = brief.direction ? getDirection(brief.direction) : pickDirection(brief);
  const t0 = Date.now();
  await mkdir(GEN, { recursive: true });

  let content = null;
  let mode = 'atelier';
  if (baseline) {
    mode = 'baseline';
    const src = join(ROOT, 'baseline', `${slug}.astro`);
    if (!existsSync(src)) throw new Error(`Manca baseline/${slug}.astro`);
    await cp(src, join(GEN, 'Baseline.astro'));
    content = { meta: { lang: brief.language }, pages: {} };
  } else {
    const cpath = join(ROOT, 'content', `${slug}.json`);
    if (!existsSync(cpath)) {
      throw new Error(`Manca content/${slug}.json: scrivilo seguendo .claude/skills/atelier/SKILL.md (sezione "Struttura e copy").`);
    }
    content = JSON.parse(await readFile(cpath, 'utf8'));
    const problems = lintContent(content, brief);
    if (problems.length) throw new Error('Contenuti non validi:\n- ' + problems.join('\n- '));
    await writeFile(join(GEN, 'Baseline.astro'), BASELINE_STUB);
  }

  const site = { mode, level: baseline ? 'baseline' : level, brief: { slug, language: brief.language }, direction, content };
  await writeFile(join(GEN, 'site.json'), JSON.stringify(site, null, 2));
  await writeFile(join(GEN, 'theme.css'), baseline ? '' : themeCss(direction));
  await mkdir(join(ENGINE, 'public'), { recursive: true });
  const p = direction.palette;
  await writeFile(join(ENGINE, 'public', 'favicon.svg'), `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="${baseline ? '#334155' : p.ink}"/><circle cx="16" cy="16" r="7" fill="${baseline ? '#e2e8f0' : p.accent}"/></svg>`);
  await writeFile(join(ENGINE, 'public', 'robots.txt'), 'User-agent: *\nAllow: /\n');

  const outDir = resolve(out || join(ROOT, 'output', baseline ? `${slug}-baseline` : `${slug}-${level}`));
  await rm(outDir, { recursive: true, force: true });
  const res = spawnSync(process.execPath, [join(ROOT, 'node_modules', 'astro', 'bin', 'astro.mjs'), 'build', '--silent'], {
    cwd: ENGINE,
    env: { ...process.env, ATELIER_SRC: baseline ? './baseline-src' : './src', ATELIER_OUT: outDir, ATELIER_SITE: (content.meta && content.meta.url) || 'https://example.com', ASTRO_TELEMETRY_DISABLED: '1' },
    encoding: 'utf8'
  });
  if (res.status !== 0) throw new Error(`Build Astro fallita:\n${res.stdout}\n${res.stderr}`);
  const pruned = await pruneUnreferencedJs(outDir);
  const ms = Date.now() - t0;
  return { slug, level: site.level, direction: direction.id, outDir, ms, pruned };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const args = parseArgs(process.argv.slice(2));
  if (!args.brief) {
    console.error('Uso: node scripts/generate.mjs <brief.json> [--level base|cinematic] [--baseline] [--out dir]');
    process.exit(2);
  }
  try {
    const r = await generate(args);
    console.log(`✓ ${r.slug} [${r.level}] direzione=${r.direction} → ${r.outDir} (${(r.ms / 1000).toFixed(1)} s)`);
  } catch (err) {
    console.error('✗', err.message);
    process.exit(1);
  }
}

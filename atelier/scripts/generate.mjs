// Pipeline Atelier: brief JSON → fase Bibbia (concept, personalità, firma) → struttura e copy → sito Astro statico.
// Uso:
//   node scripts/generate.mjs <brief.json> --config a|b|c --level base|cinematic
//   node scripts/generate.mjs <brief.json> --config baseline --level base|cinematic   (sito scritto senza skill né Bibbia)
// La fase Bibbia sta in bibbia/<slug>-<config>.json, struttura e copy in content/<slug>-<config>.json:
// li scrive l'agente seguendo .claude/skills/atelier/SKILL.md e le skill della configurazione; questo script
// li valida (Bibbia, contrasto, font, lint dei contenuti e dei link) e li impagina.
import { readFile, writeFile, mkdir, rm, cp, readdir, unlink } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { lintContent } from './lib/lint.mjs';
import { CONFIGS, loadBibbia, tokensCss, GSAP_EASE } from './lib/bibbia.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ENGINE = join(ROOT, 'engine');
const GEN = join(ENGINE, 'src', 'generated');
export const LEVELS = ['base', 'cinematic'];
export const ALL_CONFIGS = ['baseline', ...Object.keys(CONFIGS)];

function parseArgs(argv) {
  const args = { brief: null, level: 'base', config: 'a', out: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--level') args.level = argv[++i];
    else if (a === '--config') args.config = argv[++i];
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

// dati strutturati (SEO, Bibbia §17) ricavati dai contatti veri del brief
function schemaFor(content, brief) {
  const f = content.footer;
  const s = { '@context': 'https://schema.org', '@type': 'LocalBusiness', name: content.brand.name, description: content.meta.description, url: content.meta.url };
  if (f.email) s.email = f.email;
  if (f.phone) s.telephone = f.phone;
  if (f.address) s.address = f.address;
  return s;
}

export async function generate({ brief: briefPath, level, config = 'a', out }) {
  const brief = validateBrief(JSON.parse(await readFile(resolve(briefPath), 'utf8')));
  const slug = brief.slug;
  if (level === 'video-scroll') throw new Error('VIDEO-SCROLL richiede asset forniti dal cliente in assets/<slug>/scroll/: non generiamo media a pagamento.');
  if (!LEVELS.includes(level)) throw new Error(`level: ${LEVELS.join(' | ')}`);
  if (!ALL_CONFIGS.includes(config)) throw new Error(`config: ${ALL_CONFIGS.join(' | ')}`);
  const t0 = Date.now();
  await mkdir(GEN, { recursive: true });
  const id = `${slug}-${config}-${level}`;
  let site;
  let favicon;
  if (config === 'baseline') {
    const src = join(ROOT, 'baseline', `${slug}-${level}.astro`);
    if (!existsSync(src)) throw new Error(`Manca baseline/${slug}-${level}.astro`);
    await cp(src, join(GEN, 'Baseline.astro'));
    site = { mode: 'baseline', config, level, brief: { slug, language: brief.language } };
    await writeFile(join(GEN, 'theme.css'), '');
    favicon = ['#334155', '#e2e8f0'];
  } else {
    const bibbia = loadBibbia(ROOT, slug, config);
    const cpath = join(ROOT, 'content', `${slug}-${config}.json`);
    if (!existsSync(cpath)) throw new Error(`Manca content/${slug}-${config}.json: scrivilo seguendo .claude/skills/atelier/SKILL.md (Struttura e copy).`);
    const content = JSON.parse(await readFile(cpath, 'utf8'));
    const problems = lintContent(content, brief, { config, bibbia });
    if (problems.length) throw new Error(`Contenuti ${slug}-${config} non validi:\n- ` + problems.join('\n- '));
    content.schema = schemaFor(content, brief);
    const m = bibbia.tokens.motion || {};
    const client = {
      sig: { kind: bibbia.signature.kind, id: bibbia.signature.id, fallback_id: bibbia.signature.fallback_id, params: bibbia.signature.params || {} },
      palette: bibbia.tokens.palette,
      motion: { dur: Math.min(1.2, (m.sequence_ms || 900) / 1000), ease: GSAP_EASE[m.ease] || GSAP_EASE.out, distance: m.distance ?? 24, stagger: 0.08 }
    };
    site = { mode: 'atelier', config, level, brief: { slug, language: brief.language }, bibbia, content, client };
    await writeFile(join(GEN, 'Baseline.astro'), BASELINE_STUB);
    await writeFile(join(GEN, 'theme.css'), tokensCss(bibbia));
    favicon = [bibbia.tokens.palette.ink, bibbia.tokens.palette.accent];
  }
  await writeFile(join(GEN, 'site.json'), JSON.stringify(site, null, 2));
  // foto e media forniti dal cliente: assets/<slug>/ → /media/ (si svuota a ogni build: nessun file di un altro sito)
  const media = join(ENGINE, 'public', 'media');
  await rm(media, { recursive: true, force: true });
  const assets = join(ROOT, 'assets', slug);
  if (existsSync(assets)) await cp(assets, media, { recursive: true });
  for (const [name, m] of Object.entries(site.content?.media || {}))
    for (const w of m.widths) for (const ext of ['webp', 'jpg'])
      if (!existsSync(join(assets, `${name}-${w}.${ext}`))) throw new Error(`Manca assets/${slug}/${name}-${w}.${ext}`);
  await mkdir(join(ENGINE, 'public'), { recursive: true });
  await writeFile(join(ENGINE, 'public', 'favicon.svg'), `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="${favicon[0]}"/><circle cx="16" cy="16" r="7" fill="${favicon[1]}"/></svg>`);
  await writeFile(join(ENGINE, 'public', 'robots.txt'), 'User-agent: *\nAllow: /\n');

  const outDir = resolve(out || join(ROOT, 'output', id));
  await rm(outDir, { recursive: true, force: true });
  const res = spawnSync(process.execPath, [join(ROOT, 'node_modules', 'astro', 'bin', 'astro.mjs'), 'build', '--silent'], {
    cwd: ENGINE,
    env: { ...process.env, ATELIER_SRC: config === 'baseline' ? './baseline-src' : './src', ATELIER_OUT: outDir, ATELIER_SITE: site.content?.meta?.url || 'https://example.com', ATELIER_3D: site.bibbia?.signature.kind === '3d' && level === 'cinematic' ? '1' : '0', ASTRO_TELEMETRY_DISABLED: '1' },
    encoding: 'utf8'
  });
  if (res.status !== 0) throw new Error(`Build Astro fallita:\n${res.stdout}\n${res.stderr}`);
  const pruned = await pruneUnreferencedJs(outDir);
  const ms = Date.now() - t0;
  return { id, slug, config, level, signature: site.bibbia ? `${site.bibbia.signature.kind}:${site.bibbia.signature.id}` : null, outDir, ms, pruned };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const args = parseArgs(process.argv.slice(2));
  if (!args.brief) {
    console.error('Uso: node scripts/generate.mjs <brief.json> --config a|b|c|baseline --level base|cinematic [--out dir]');
    process.exit(2);
  }
  try {
    const r = await generate(args);
    console.log(`✓ ${r.id} firma=${r.signature || '—'} → ${r.outDir} (${(r.ms / 1000).toFixed(1)} s)`);
  } catch (err) {
    console.error('✗', err.message);
    process.exit(1);
  }
}

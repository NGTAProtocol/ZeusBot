import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { join, resolve, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { DIRECTIONS, contrast } from '../scripts/lib/directions.mjs';
import { lintContent } from '../scripts/lib/lint.mjs';
import { validateBrief } from '../scripts/generate.mjs';
import { validateBibbia, CONFIGS } from '../scripts/lib/bibbia.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = (p) => readFileSync(join(ROOT, p), 'utf8');
function walk(dir, exts, out = []) {
  for (const e of readdirSync(join(ROOT, dir), { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) { if (!['node_modules', 'generated', 'dist'].includes(e.name)) walk(p, exts, out); }
    else if (exts.includes(extname(e.name))) out.push(p);
  }
  return out;
}

test('struttura del progetto', () => {
  for (const p of ['README.md', 'CREDITS.md', 'skills.lock', 'audit-skill.md', 'package.json', '.claude/skills/atelier/SKILL.md',
    'scripts/generate.mjs', 'scripts/qa.mjs', 'scripts/build-all.mjs', 'scripts/study-reference.mjs', 'scripts/lib/directions.mjs', 'scripts/lib/lint.mjs',
    'engine/astro.config.mjs', 'engine/src/pages/index.astro', 'engine/src/scripts/cinematic.js', 'engine/src/scripts/scene.js',
    'references/README.md', 'references/patterns.md', 'references/stack-stats.md', 'references/archetipi.md',
    'bibbia/BIBBIA.md', 'scripts/lib/bibbia.mjs', 'engine/src/lib/signature.js'])
    assert.ok(existsSync(join(ROOT, p)), `manca ${p}`);
  const skill = read('.claude/skills/atelier/SKILL.md');
  assert.match(skill, /^---\nname: atelier\ndescription: /);
});

test('8 direzioni originali, contrasto AA, max 2 famiglie di font OFL', () => {
  assert.equal(DIRECTIONS.length, 8);
  assert.equal(new Set(DIRECTIONS.map((d) => d.id)).size, 8);
  const pkg = JSON.parse(read('package.json'));
  for (const d of DIRECTIONS) {
    const p = d.palette;
    for (const k of ['ink', 'muted', 'accent']) for (const bg of ['bg', 'surface'])
      assert.ok(contrast(p[k], p[bg]) >= 4.5, `${d.id}: ${k} su ${bg} = ${contrast(p[k], p[bg]).toFixed(2)}`);
    assert.ok(contrast(p.accent2, p.bg) >= 3, `${d.id}: accent2 decorativo < 3:1`);
    const fams = new Set([d.fonts.display.family, d.fonts.body.family]);
    assert.ok(fams.size <= 2);
    for (const f of [d.fonts.display, d.fonts.body]) {
      assert.ok(pkg.dependencies[f.pkg], `${d.id}: font ${f.pkg} non è una dipendenza`);
      const lic = JSON.parse(readFileSync(join(ROOT, 'node_modules', f.pkg, 'package.json'), 'utf8')).license;
      assert.equal(lic, 'OFL-1.1', `${f.pkg}: licenza ${lic}`);
    }
    for (const k of ['motion', 'layout', 'hero3d', 'tone', 'space']) assert.ok(d[k], `${d.id}: manca ${k}`);
  }
});

test('nessuna CDN e nessun path assoluto nei sorgenti', () => {
  const files = [...walk('engine', ['.astro', '.js', '.mjs', '.css', '.ts']), ...walk('scripts', ['.mjs', '.js']), ...walk('content', ['.json']), ...walk('baseline', ['.astro'])];
  assert.ok(files.length > 10);
  for (const f of files) {
    const s = read(f);
    assert.doesNotMatch(s, /https?:\/\/(cdn\.|unpkg\.com|cdn\.jsdelivr|fonts\.googleapis|fonts\.gstatic|cdnjs)/i, `CDN in ${f}`);
    assert.doesNotMatch(s, /(["'`])\/(home|tmp|Users|root)\//, `path assoluto in ${f}`);
  }
});

test('CREDITS presente e copre dipendenze e font', () => {
  const credits = read('CREDITS.md');
  const pkg = JSON.parse(read('package.json'));
  for (const dep of ['three', 'lenis', 'gsap']) assert.ok(credits.includes(dep), `CREDITS non cita ${dep}`);
  const fonts = DIRECTIONS.flatMap((d) => [d.fonts.display, d.fonts.body]);
  for (const f of readdirSync(join(ROOT, 'bibbia')).filter((x) => x.endsWith('.json'))) {
    const b = JSON.parse(read(`bibbia/${f}`));
    fonts.push(b.tokens.fonts.display, b.tokens.fonts.body);
  }
  for (const f of fonts) {
    const name = f.family.replace(' Variable', '');
    assert.ok(credits.includes(name), `CREDITS non cita il font ${name}`);
  }
  assert.ok(Object.keys(pkg.dependencies).length > 0);
});

test('skills.lock coerente con .claude/skills', () => {
  const lock = JSON.parse(read('skills.lock'));
  const installed = new Set(lock.skills.filter((s) => ['installed', 'installed-partial'].includes(s.status)).flatMap((s) => s.installed_as));
  const onDisk = readdirSync(join(ROOT, '.claude/skills')).filter((n) => n !== 'atelier' && statSync(join(ROOT, '.claude/skills', n)).isDirectory());
  assert.deepEqual([...onDisk].sort(), [...installed].sort());
  for (const s of lock.skills) {
    assert.match(s.commit, /^[0-9a-f]{40}$/, `${s.name}: commit non valido`);
    assert.ok(s.license, `${s.name}: licenza mancante`);
    if (s.status === 'rejected') assert.equal(s.installed_as.length, 0);
    for (const dir of s.installed_as) {
      assert.ok(existsSync(join(ROOT, '.claude/skills', dir, 'SKILL.md')), `${dir}: manca SKILL.md`);
      assert.ok(readdirSync(join(ROOT, '.claude/skills', dir)).some((f) => /^LICENSE/i.test(f)), `${dir}: manca il file di licenza`);
    }
  }
  const audit = read('audit-skill.md');
  for (const s of lock.skills) assert.ok(audit.includes(s.name), `audit-skill.md non cita ${s.name}`);
});

test('fase Bibbia e contenuti validi per ogni brief e configurazione', () => {
  const briefs = readdirSync(join(ROOT, 'briefs')).filter((f) => f.endsWith('.json'));
  const all = briefs.map((f) => validateBrief(JSON.parse(read(`briefs/${f}`))));
  assert.equal(all.filter((b) => !b.client).length, 3, '3 attività fittizie per la prova di valore');
  for (const b of all) {
    for (const config of b.configs || Object.keys(CONFIGS)) {
      const bib = JSON.parse(read(`bibbia/${b.slug}-${config}.json`));
      assert.deepEqual(validateBibbia(bib, ROOT), [], `${b.slug}-${config}: Bibbia non valida`);
      for (const sk of CONFIGS[config].skills) assert.ok(bib.skills_used.includes(sk), `${b.slug}-${config}: skill ${sk} non dichiarata`);
      const c = JSON.parse(read(`content/${b.slug}-${config}.json`));
      assert.deepEqual(lintContent(c, b, { config }), [], `${b.slug}-${config}: problemi di contenuto`);
    }
    if (!b.client) for (const level of ['base', 'cinematic']) assert.ok(existsSync(join(ROOT, 'baseline', `${b.slug}-${level}.astro`)), `manca la baseline ${b.slug}-${level}`);
  }
});

test('la Bibbia contiene tutti i capitoli e la checklist Q1-Q6', () => {
  const md = read('bibbia/BIBBIA.md');
  for (const h of ['CONCEPT', 'PERSONALITY', 'SIGNATURE', 'Budget di performance', 'Mobile', 'Copy e conversione', 'SEO', 'Licenze degli asset', 'Consegna', '14.3'])
    assert.ok(md.includes(h), `BIBBIA.md: manca ${h}`);
  for (let i = 1; i <= 6; i++) assert.match(md, new RegExp(`\\*\\*Q${i}\\*\\*`));
});

test('il lint blocca i link finti e le regole della configurazione C', () => {
  const b = { language: 'it', pages: ['home'], facts: ['email vera@esempio.it'] };
  const c = JSON.parse(read('content/fornace-lume-c.json'));
  c.pages.home.sections[0].body.push('x');
  c.nav.push({ label: 'Blog', href: 'blog' }, { label: 'Team', href: '#team' });
  c.footer.email = 'finta@altro.it';
  c.pages.home.hero.title_lines = ['uno', 'due', 'tre'];
  const p = lintContent(c, { ...b, pages: ['home', 'contatti'] }, { config: 'c' }).join('\n');
  for (const re of [/pagina "blog" non esiste/, /#team non esiste/, /non è nei fatti del brief/, /oltre 2 righe/]) assert.match(p, re);
});

test('il lint blocca i cliché', () => {
  const b = { language: 'it', pages: ['home'] };
  const c = { meta: { title: 'x', description: 'x'.repeat(80), lang: 'it' }, brand: { name: 'Acme' }, cta: { label: 'Scopri di più', href: '#' }, footer: { email: 'a@b.c', closing: 'Lorem ipsum dolor sit amet' }, pages: { home: { hero: { title_lines: ['Soluzioni innovative a 360 gradi'], lead: 'la', lead_short: 'la' }, sections: [{ type: 'cards' }] } } };
  const p = lintContent(c, b).join('\n');
  for (const re of [/lorem ipsum/i, /scopri di più/i, /soluzioni innovative/i, /cards/, /meno di 3 volte/]) assert.match(p, re);
});

test('VIDEO-SCROLL non parte senza asset del cliente', async () => {
  const { generate } = await import('../scripts/generate.mjs');
  const brief = join(ROOT, 'briefs', readdirSync(join(ROOT, 'briefs'))[0]);
  await assert.rejects(generate({ brief, level: 'video-scroll' }), /asset forniti dal cliente/);
});

// Build reale di tutti gli esempi (BASE, CINEMATICO, BASELINE) e controllo dell'output statico.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, resolve, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { generate } from '../scripts/generate.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, 'output', '_test');
const files = (dir) => readdirSync(dir, { recursive: true }).map((f) => join(dir, f)).filter((f) => extname(f));

for (const f of readdirSync(join(ROOT, 'briefs')).filter((x) => x.endsWith('.json'))) {
  const slug = f.replace('.json', '');
  for (const config of ['baseline', 'a', 'b', 'c']) for (const level of ['base', 'cinematic']) {
    test(`build ${slug}-${config}-${level}`, { timeout: 120000 }, async () => {
      const out = join(OUT, `${slug}-${config}-${level}`);
      const r = await generate({ brief: join(ROOT, 'briefs', f), level, config, out });
      assert.ok(existsSync(join(out, 'index.html')));
      const html = readFileSync(join(out, 'index.html'), 'utf8');
      assert.match(html, /<html lang="it"/);
      assert.equal((html.match(/<h1[\s>]/g) || []).length, 1, 'un solo h1');
      for (const file of files(out).filter((x) => /\.(html|js|css)$/.test(x))) {
        const s = readFileSync(file, 'utf8');
        assert.doesNotMatch(s, /<script[^>]+src="https?:|<link[^>]+href="https?:\/\/(?!(fornacelume|quota2100|nodosicuro)\.example)/, `risorsa esterna in ${file}`);
        assert.doesNotMatch(s, /cdn\.jsdelivr|unpkg\.com|fonts\.googleapis|cdnjs/, `CDN in ${file}`);
      }
      if (config === 'baseline') return;
      const js = files(out).filter((x) => x.endsWith('.js')).map((x) => x.split('/').pop()).join(' ');
      if (level === 'base') assert.doesNotMatch(js, /gsap|lenis|scene|hero-worker/i, 'il BASE non deve includere GSAP/Lenis/Three');
      // Bibbia §14.3: Three.js solo se la firma è 3D
      if (level === 'cinematic' && r.signature.startsWith('3d')) assert.match(js, /hero-worker/, 'firma 3D: serve il worker 3D');
      if (level === 'cinematic' && r.signature.startsWith('css')) assert.doesNotMatch(js, /hero-worker|scene/, 'firma CSS: niente Three.js');
      assert.match(html, /application\/ld\+json/, 'dati strutturati LocalBusiness');
    });
  }
}

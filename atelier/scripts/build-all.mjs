// Compila tutti gli esempi: per ogni brief → BASE, CINEMATICO e (se esiste) BASELINE.
import { readdir, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { generate } from './generate.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const briefs = (await readdir(join(ROOT, 'briefs'))).filter((f) => f.endsWith('.json')).sort();
const results = [];
for (const f of briefs) {
  const slug = f.replace(/\.json$/, '');
  const jobs = [{ level: 'base' }, { level: 'cinematic' }];
  if (existsSync(join(ROOT, 'baseline', `${slug}.astro`))) jobs.push({ baseline: true });
  for (const j of jobs) {
    const r = await generate({ brief: join(ROOT, 'briefs', f), level: j.level || 'base', baseline: !!j.baseline });
    console.log(`✓ ${r.slug} [${r.level}] ${r.direction} ${(r.ms / 1000).toFixed(1)} s`);
    results.push({ slug: r.slug, level: r.level, direction: r.direction, ms: r.ms });
  }
}
await mkdir(join(ROOT, 'reports'), { recursive: true });
await writeFile(join(ROOT, 'reports', 'build-times.json'), JSON.stringify(results, null, 2) + '\n');

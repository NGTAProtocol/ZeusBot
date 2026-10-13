// Compila tutti gli esempi: per ogni brief, 4 configurazioni (baseline, A, B, C) × 2 livelli (BASE, CINEMATICO) = 8 siti.
import { readdir, writeFile, mkdir, readFile } from 'node:fs/promises';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { generate, ALL_CONFIGS, LEVELS } from './generate.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const briefs = (await readdir(join(ROOT, 'briefs'))).filter((f) => f.endsWith('.json')).sort();
const results = [];
for (const f of briefs) {
  // un brief di un cliente reale può limitare le configurazioni (es. "configs": ["a"])
  const brief = JSON.parse(await readFile(join(ROOT, 'briefs', f), 'utf8'));
  for (const config of brief.configs || ALL_CONFIGS) {
    for (const level of LEVELS) {
      const r = await generate({ brief: join(ROOT, 'briefs', f), level, config });
      console.log(`✓ ${r.id} ${r.signature || ''} ${(r.ms / 1000).toFixed(1)} s`);
      results.push({ id: r.id, slug: r.slug, config, level, signature: r.signature, ms: r.ms });
    }
  }
}
await mkdir(join(ROOT, 'reports'), { recursive: true });
await writeFile(join(ROOT, 'reports', 'build-times.json'), JSON.stringify(results, null, 2) + '\n');

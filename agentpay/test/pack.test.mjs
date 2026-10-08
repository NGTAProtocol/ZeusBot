import { test } from 'node:test';
import assert from 'node:assert/strict';
import { randomBytes } from 'node:crypto';
import { encryptPack, decryptPack, newScanId, isScanId, buildTeaser, getPackKey } from '../lib/pack.js';
import { withEnv } from './helpers.mjs';

const key = randomBytes(32);
const fix_pack = { lang: 'it', jsonld: '{\n  "a": 1,\n  "b": 2,\n  "c": 3\n}', llms_txt: '# Sito\n\n> descrizione\n\n## Pagine', snippets: [{ title: 'S1', language: 'html', code: 'riga1\nriga2\nriga3\nriga4', instructions: 'x' }] };

test('scan_id: 16 caratteri [a-zA-Z0-9_-]', () => {
  const ids = new Set(Array.from({ length: 200 }, newScanId));
  assert.equal(ids.size, 200);
  for (const id of ids) assert.ok(isScanId(id), id);
});

test('cifratura e decifratura del blob (AES-256-GCM)', () => {
  const scan_id = newScanId();
  const locked = encryptPack({ fix_pack, scan_id, url: 'https://x.it/' }, key);
  assert.match(locked, /^v1\.[A-Za-z0-9_-]+$/);
  assert.ok(!locked.includes('Sito'));
  const out = decryptPack(locked, key);
  assert.equal(out.scan_id, scan_id);
  assert.deepEqual(out.fix_pack, fix_pack);
  // due cifrature dello stesso contenuto sono diverse (IV casuale)
  assert.notEqual(locked, encryptPack({ fix_pack, scan_id, url: 'https://x.it/' }, key));
});

test('blob manomesso, chiave errata o scaduto → errore', () => {
  const locked = encryptPack({ fix_pack, scan_id: newScanId(), url: 'u' }, key);
  const raw = Buffer.from(locked.slice(3), 'base64url');
  raw[raw.length - 1] ^= 1;
  assert.throws(() => decryptPack('v1.' + raw.toString('base64url'), key), { status: 400 });
  assert.throws(() => decryptPack(locked, randomBytes(32)), { status: 400 });
  assert.throws(() => decryptPack('garbage', key), { status: 400 });
  assert.throws(() => decryptPack(locked, key, { now: Date.now() + 8 * 24 * 3600 * 1000 }), { status: 410 });
});

test('PACK_SECRET: 32 byte base64 obbligatori se richiesti', withEnv({ PACK_SECRET: undefined }, async () => {
  assert.throws(() => getPackKey({ required: true }), /PACK_SECRET/);
  assert.equal(getPackKey().length, 32); // chiave temporanea in demo
  process.env.PACK_SECRET = Buffer.alloc(16).toString('base64');
  assert.throws(() => getPackKey(), /32 byte/);
  process.env.PACK_SECRET = key.toString('base64');
  assert.deepEqual(getPackKey({ required: true }), key);
}));

test('teaser: solo titoli e prime 3 righe', () => {
  const t = buildTeaser(fix_pack);
  assert.deepEqual(t.files.map((f) => f.title), ['JSON-LD (schema.org)', 'llms.txt', 'S1']);
  assert.equal(t.files[0].preview, '{\n  "a": 1,\n  "b": 2,');
  assert.equal(t.files[2].preview, 'riga1\nriga2\nriga3');
  assert.ok(!JSON.stringify(t).includes('riga4'));
});

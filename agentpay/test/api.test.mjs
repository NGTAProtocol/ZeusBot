import { test } from 'node:test';
import assert from 'node:assert/strict';
import { randomBytes } from 'node:crypto';
import { createScanHandler } from '../api/scan.js';
import unlockHandler from '../api/unlock.js';
import configHandler from '../api/config.js';
import { crawl } from '../lib/crawler.js';
import { encryptPack, newScanId } from '../lib/pack.js';
import { call, fakeShopFetcher, withEnv } from './helpers.mjs';

const SECRET = randomBytes(32).toString('base64');
const STRIPE_ENV = {
  PACK_SECRET: SECRET,
  STRIPE_SECRET_KEY: 'rk_test_dummy',
  STRIPE_PAYMENT_LINK_URL: 'https://buy.stripe.com/test_abc',
  SUPPORT_EMAIL: 'aiuto@example.com',
  ANTHROPIC_API_KEY: undefined
};
const DEMO_ENV = { PACK_SECRET: SECRET, STRIPE_SECRET_KEY: undefined, STRIPE_PAYMENT_LINK_URL: undefined, ANTHROPIC_API_KEY: undefined };
const SESSION = 'cs_test_a1B2c3D4e5F6g7H8';
const realFetch = globalThis.fetch;
const scanHandler = createScanHandler({ crawl: (url) => crawl(url, { fetcher: fakeShopFetcher() }), rateLimit: 1000 });

function mockStripe(session, status = 200) {
  const calls = [];
  globalThis.fetch = async (url, opts) => {
    calls.push({ url, auth: opts.headers.Authorization });
    return new Response(JSON.stringify(session), { status, headers: { 'content-type': 'application/json' } });
  };
  return calls;
}

let ip = 0;
const nextIp = () => `198.51.100.${++ip}`;

test('/api/scan non restituisce il fix_pack completo', withEnv(STRIPE_ENV, async () => {
  const r = await call(scanHandler, { body: { url: 'shop.example.com' }, ip: nextIp() });
  assert.equal(r.status, 200);
  assert.equal(r.body.fix_pack, undefined);
  assert.deepEqual(Object.keys(r.body).sort(), ['issues', 'locked', 'mode', 'scan_id', 'scanned_at', 'score', 'teaser', 'url']);
  assert.match(r.body.scan_id, /^[A-Za-z0-9_-]{16}$/);
  assert.match(r.body.locked, /^v1\./);
  assert.ok(r.body.teaser.files.length >= 3);
  for (const f of r.body.teaser.files) assert.ok(f.preview.split('\n').length <= 3);
  // nessun contenuto oltre la 3ª riga in chiaro
  assert.ok(!JSON.stringify(r.body).includes('Organization'));
}));

test('/api/scan in modalità Stripe senza PACK_SECRET → 500 di configurazione', withEnv({ ...STRIPE_ENV, PACK_SECRET: undefined }, async () => {
  const r = await call(scanHandler, { body: { url: 'shop.example.com' }, ip: nextIp() });
  assert.equal(r.status, 500);
  assert.match(r.body.error, /PACK_SECRET/);
}));

test('/api/unlock: pagato e client_reference_id corretto → 200 con fix_pack', withEnv(STRIPE_ENV, async () => {
  const scan = await call(scanHandler, { body: { url: 'shop.example.com' }, ip: nextIp() });
  const calls = mockStripe({ id: SESSION, payment_status: 'paid', client_reference_id: scan.body.scan_id });
  try {
    const r = await call(unlockHandler, { body: { locked: scan.body.locked, session_id: SESSION }, ip: nextIp() });
    assert.equal(r.status, 200);
    assert.ok(r.body.fix_pack.jsonld && r.body.fix_pack.llms_txt);
    assert.equal(calls[0].url, `https://api.stripe.com/v1/checkout/sessions/${SESSION}`);
    assert.equal(calls[0].auth, 'Bearer rk_test_dummy');
  } finally { globalThis.fetch = realFetch; }
}));

test('/api/unlock: non pagato → 402', withEnv(STRIPE_ENV, async () => {
  const scan_id = newScanId();
  const locked = encryptPack({ fix_pack: { jsonld: '{}', llms_txt: 'x', snippets: [] }, scan_id, url: 'u' }, Buffer.from(SECRET, 'base64'));
  mockStripe({ id: SESSION, payment_status: 'unpaid', client_reference_id: scan_id });
  try {
    const r = await call(unlockHandler, { body: { locked, session_id: SESSION }, ip: nextIp() });
    assert.equal(r.status, 402);
    assert.equal(r.body.fix_pack, undefined);
  } finally { globalThis.fetch = realFetch; }
}));

test('/api/unlock: client_reference_id diverso → 402', withEnv(STRIPE_ENV, async () => {
  const locked = encryptPack({ fix_pack: { jsonld: '{}', llms_txt: 'x', snippets: [] }, scan_id: newScanId(), url: 'u' }, Buffer.from(SECRET, 'base64'));
  mockStripe({ id: SESSION, payment_status: 'paid', client_reference_id: newScanId() });
  try {
    const r = await call(unlockHandler, { body: { locked, session_id: SESSION }, ip: nextIp() });
    assert.equal(r.status, 402);
    assert.equal(r.body.fix_pack, undefined);
  } finally { globalThis.fetch = realFetch; }
}));

test('/api/unlock: sessione inesistente → 402; Stripe giù → 502; session_id malformato → 400', withEnv(STRIPE_ENV, async () => {
  const locked = encryptPack({ fix_pack: { jsonld: '{}', llms_txt: 'x', snippets: [] }, scan_id: newScanId(), url: 'u' }, Buffer.from(SECRET, 'base64'));
  const err = console.error;
  console.error = () => {};
  try {
    mockStripe({ error: {} }, 404);
    assert.equal((await call(unlockHandler, { body: { locked, session_id: SESSION }, ip: nextIp() })).status, 402);
    mockStripe({ error: {} }, 500);
    assert.equal((await call(unlockHandler, { body: { locked, session_id: SESSION }, ip: nextIp() })).status, 502);
    const calls = mockStripe({});
    assert.equal((await call(unlockHandler, { body: { locked, session_id: '../../customers' }, ip: nextIp() })).status, 400);
    assert.equal(calls.length, 0);
  } finally {
    globalThis.fetch = realFetch;
    console.error = err;
  }
}));

test('/api/unlock: blob manomesso → 400 senza chiamare Stripe', withEnv(STRIPE_ENV, async () => {
  const calls = mockStripe({ payment_status: 'paid' });
  try {
    const r = await call(unlockHandler, { body: { locked: 'v1.AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', session_id: SESSION }, ip: nextIp() });
    assert.equal(r.status, 400);
    assert.equal(calls.length, 0);
  } finally { globalThis.fetch = realFetch; }
}));

test('modalità DEMO: unlock simulato senza Stripe, rifiutato in modalità Stripe', async () => {
  let locked;
  await withEnv(DEMO_ENV, async () => {
    const scan = await call(scanHandler, { body: { url: 'shop.example.com' }, ip: nextIp() });
    locked = scan.body.locked;
    const r = await call(unlockHandler, { body: { locked, demo: true }, ip: nextIp() });
    assert.equal(r.status, 200);
    assert.equal(r.body.payments, 'demo');
    assert.ok(r.body.fix_pack.jsonld);
    assert.equal((await call(unlockHandler, { body: { locked }, ip: nextIp() })).status, 400);
  })();
  await withEnv(STRIPE_ENV, async () => {
    const calls = mockStripe({ payment_status: 'unpaid' });
    try {
      const r = await call(unlockHandler, { body: { locked, demo: true, session_id: SESSION }, ip: nextIp() });
      assert.equal(r.status, 402); // "demo: true" non bypassa Stripe
      assert.equal(calls.length, 1);
    } finally { globalThis.fetch = realFetch; }
  })();
});

test('/api/config non espone segreti', withEnv(STRIPE_ENV, async () => {
  const r = await call(configHandler, { method: 'GET', ip: nextIp() });
  assert.equal(r.status, 200);
  assert.deepEqual(r.body, { payments: 'stripe', payment_link_url: 'https://buy.stripe.com/test_abc', support_email: 'aiuto@example.com', price_eur: 9 });
  const text = JSON.stringify(r.body);
  assert.ok(!text.includes('rk_test') && !text.includes(SECRET));
}));

test('/api/config in demo se manca la chiave Stripe', withEnv(DEMO_ENV, async () => {
  const r = await call(configHandler, { method: 'GET', ip: nextIp() });
  assert.equal(r.body.payments, 'demo');
  assert.equal(r.body.payment_link_url, null);
}));

test('/api/scan: input non validi', withEnv(DEMO_ENV, async () => {
  assert.equal((await call(scanHandler, { body: { url: '' }, ip: nextIp() })).status, 400);
  assert.equal((await call(scanHandler, { body: 'garbage', ip: nextIp() })).status, 400);
  assert.equal((await call(scanHandler, { method: 'GET', ip: nextIp() })).status, 405);
  assert.equal((await call(scanHandler, { body: 'x'.repeat(20000), ip: nextIp() })).status, 413);
}));

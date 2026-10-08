import { test } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import zlib from 'node:zlib';
import { safeFetch, crawl, parseRobots } from '../lib/crawler.js';
import { resolvePublicUrl, isPrivateIp } from '../lib/ssrf.js';
import { fakeShopFetcher } from './helpers.mjs';

// Server locale: "shop.test" viene risolto (solo nel test) su 127.0.0.1 per verificare il pinning.
function startServer(handler) {
  return new Promise((resolve) => {
    const srv = http.createServer(handler).listen(0, '127.0.0.1', () => resolve(srv));
  });
}
const pinTo = (port) => async (url) => {
  if (url.hostname === 'shop.test') return { url, address: '127.0.0.1', family: 4 };
  return resolvePublicUrl(url); // ogni altro hop passa dal controllo reale
};

test('IP privati riconosciuti', () => {
  for (const ip of ['127.0.0.1', '10.1.2.3', '172.16.0.1', '192.168.1.1', '169.254.169.254', '100.64.0.1', '::1', 'fd00::1', 'fe80::1', '::ffff:127.0.0.1', '::ffff:7f00:1'])
    assert.equal(isPrivateIp(ip), true, ip);
  for (const ip of ['8.8.8.8', '104.16.0.1', '2606:4700::1']) assert.equal(isPrivateIp(ip), false, ip);
});

test('resolvePublicUrl rifiuta host locali e schemi non http', async () => {
  for (const u of ['http://localhost/', 'http://127.0.0.1/', 'http://[::1]/', 'http://printer.local/', 'http://db.internal/', 'ftp://example.com/', 'http://0x7f000001/'])
    await assert.rejects(resolvePublicUrl(u), u);
});

test('DNS pinning: connessione all\'IP validato con Host originale', async () => {
  let seenHost;
  const srv = await startServer((req, res) => { seenHost = req.headers.host; res.setHeader('content-type', 'text/html'); res.end('<html>ok</html>'); });
  const port = srv.address().port;
  try {
    const r = await safeFetch(`http://shop.test:${port}/`, { resolve: pinTo(port) });
    assert.equal(r.status, 200);
    assert.equal(r.body, '<html>ok</html>');
    assert.equal(seenHost, `shop.test:${port}`);
  } finally { srv.close(); }
});

test('redirect verso IP privato bloccato', async () => {
  const srv = await startServer((req, res) => { res.statusCode = 302; res.setHeader('location', 'http://127.0.0.1/admin'); res.end(); });
  try {
    await assert.rejects(safeFetch(`http://shop.test:${srv.address().port}/`, { resolve: pinTo() }), /privat/);
  } finally { srv.close(); }
});

test('massimo 3 redirect', async () => {
  let n = 0;
  const srv = await startServer((req, res) => { res.statusCode = 301; res.setHeader('location', `/r${n++}`); res.end(); });
  try {
    await assert.rejects(safeFetch(`http://shop.test:${srv.address().port}/`, { resolve: pinTo() }), /Troppi redirect/);
    assert.equal(n, 4);
  } finally { srv.close(); }
});

test('gzip decompresso e corpo troncato a 1.5 MB', async () => {
  const big = 'a'.repeat(3 * 1024 * 1024);
  const srv = await startServer((req, res) => {
    if (req.url === '/gz') { res.setHeader('content-encoding', 'gzip'); res.end(zlib.gzipSync('<p>compresso</p>')); return; }
    res.end(big);
  });
  const port = srv.address().port;
  try {
    assert.equal((await safeFetch(`http://shop.test:${port}/gz`, { resolve: pinTo() })).body, '<p>compresso</p>');
    assert.equal((await safeFetch(`http://shop.test:${port}/big`, { resolve: pinTo() })).body.length, 1.5 * 1024 * 1024);
  } finally { srv.close(); }
});

test('crawl estrae JSON-LD, prezzi, form, robots, sitemap, llms.txt HTML = assente', async () => {
  const data = await crawl('shop.example.com', { fetcher: fakeShopFetcher() });
  assert.deepEqual(data.robots.blockedAiBots, ['GPTBot', 'CCBot']);
  assert.equal(data.sitemap.found, true);
  assert.equal(data.llms.found, false);
  assert.equal(data.page.jsonld.count, 2);
  assert.equal(data.page.jsonld.invalidCount, 1);
  assert.deepEqual(data.page.prices.visible, ['€ 129,90']);
  assert.equal(data.page.prices.hasMachineReadable, false);
  assert.deepEqual(data.page.forms, [{ inputs: 3, unlabeled: 1 }]);
  assert.equal(data.page.lang, 'en-US');
  assert.ok(!data.page.text.includes('menu'));
});

test('robots: blocco totale via * e override specifico', () => {
  assert.equal(parseRobots('User-agent: *\nDisallow: /', 'https://a.b').blockedAiBots.length, 7);
  assert.equal(parseRobots('User-agent: *\nDisallow: /\nUser-agent: ClaudeBot\nAllow: /', 'https://a.b').blockedAiBots.includes('ClaudeBot'), false);
});

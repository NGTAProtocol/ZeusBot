import { test } from 'node:test';
import assert from 'node:assert/strict';
import { crawl } from '../lib/crawler.js';
import { heuristicScan, buildTemplateFixPack, analyze, validateLlmResult, dedupeFixPack, fixPackLang } from '../lib/analyzer.js';
import { fakeShopFetcher, withEnv } from './helpers.mjs';

const data = await crawl('shop.example.com', { fetcher: fakeShopFetcher() });
const realFetch = globalThis.fetch;

test('punteggio euristico deterministico', () => {
  const h = heuristicScan(data);
  // 25 + 15 + 0 (llms) + 0 (bot bloccati) + 10 + 0 (prezzi) + 7.5 (manca canonical) + 3.33 (form)
  assert.equal(h.score, 61);
  assert.equal(h.issues[0].severity, 'critical');
});

test('lingua del Fix Pack: da <html lang>, default italiano', () => {
  assert.equal(fixPackLang({ lang: 'en-US' }), 'en');
  assert.equal(fixPackLang({ lang: 'de' }), 'de');
  assert.equal(fixPackLang({ lang: null }), 'it');
  const fp = buildTemplateFixPack(data);
  assert.equal(fp.lang, 'en');
  assert.match(fp.llms_txt, /## Main pages/);
  const fpIt = buildTemplateFixPack({ ...data, page: { ...data.page, lang: null } });
  assert.equal(fpIt.lang, 'it');
  assert.match(fpIt.llms_txt, /## Pagine principali/);
});

test('template: nessun dato inventato', () => {
  const fp = buildTemplateFixPack(data);
  const graph = JSON.parse(fp.jsonld)['@graph'];
  const product = graph.find((x) => x['@type'] === 'Product');
  const org = graph.find((x) => x['@type'] === 'Organization');
  // il prezzo visibile NON viene copiato nel JSON-LD (non è legato con certezza a un prodotto)
  assert.equal(product.offers.price, 'DA_COMPILARE');
  assert.equal(product.offers.availability, 'DA_COMPILARE');
  assert.equal(product.sku, 'DA_COMPILARE');
  assert.equal(product.brand.name, 'DA_COMPILARE');
  assert.equal(org.email, 'DA_COMPILARE');
  assert.equal(org.telephone, 'DA_COMPILARE');
  assert.ok(!fp.jsonld.includes('InStock'));
});

test('template: snippet senza duplicati dei file', () => {
  const fp = buildTemplateFixPack(data);
  const titles = fp.snippets.map((s) => s.title);
  assert.equal(new Set(titles).size, titles.length);
  const squash = (t) => t.replace(/\s+/g, '');
  for (const s of fp.snippets) {
    assert.ok(!squash(s.code).includes(squash(fp.jsonld)), `${s.title} ripete il JSON-LD`);
    assert.ok(!squash(s.code).includes(squash(fp.llms_txt)), `${s.title} ripete llms.txt`);
  }
  assert.ok(fp.snippets.some((s) => s.instructions.includes('https://search.google.com/test/rich-results')));
  assert.ok(fp.snippets.some((s) => s.title === 'Come servire /llms.txt'));
});

test('dedupeFixPack rimuove snippet che ripetono file o altri snippet', () => {
  const jsonld = JSON.stringify({ '@context': 'https://schema.org', '@type': 'Organization', name: 'Rossi Shoes Company' }, null, 2);
  const llms_txt = '# Rossi\n\n> Scarpe artigianali fatte a mano in Italia dal 1950\n';
  const fp = dedupeFixPack({
    jsonld,
    llms_txt,
    snippets: [
      { title: 'JSON-LD', code: `<script type="application/ld+json">\n${jsonld}\n</script>` },
      { title: 'JSON-LD compatto', code: JSON.stringify(JSON.parse(jsonld)) },
      { title: 'llms', code: llms_txt },
      { title: 'Dove incollare', code: '<head><!-- incolla qui --></head>' },
      { title: 'Dove incollare', code: '<head><!-- altro --></head>' },
      { title: 'Copia', code: '<head><!-- incolla qui --></head>' }
    ]
  });
  assert.deepEqual(fp.snippets.map((s) => s.title), ['Dove incollare']);
});

test('analyze senza chiave → euristica', withEnv({ ANTHROPIC_API_KEY: undefined }, async () => {
  assert.equal((await analyze(data)).mode, 'heuristic');
}));

test('analyze con LLM simulato: clamp, filtro severity, fences, lingua nel prompt, dedupe', withEnv({ ANTHROPIC_API_KEY: 'test', ANTHROPIC_MODEL: undefined }, async () => {
  let sent;
  const jsonld = '{"@context":"https://schema.org","@type":"Organization","name":"Rossi"}';
  globalThis.fetch = async (u, opts) => {
    assert.equal(u, 'https://api.anthropic.com/v1/messages');
    assert.equal(opts.headers['x-api-key'], 'test');
    assert.equal(opts.headers['anthropic-version'], '2023-06-01');
    sent = JSON.parse(opts.body);
    const payload = { score: 140, issues: [{ severity: 'critical', title: 'X', detail: 'y' }, { severity: 'bogus', title: 'Z' }], fix_pack: { jsonld, llms_txt: '# Rossi', snippets: [{ title: 'dup', language: 'html', code: `<script type="application/ld+json">${jsonld}</script>`, instructions: 'i' }, { title: 'ok', language: 'html', code: '<p>', instructions: 'i' }] } };
    return new Response(JSON.stringify({ stop_reason: 'end_turn', content: [{ type: 'thinking', thinking: '' }, { type: 'text', text: '```json\n' + JSON.stringify(payload) + '\n```' }] }));
  };
  try {
    const r = await analyze(data);
    assert.equal(r.mode, 'llm');
    assert.equal(r.score, 100);
    assert.equal(r.issues.length, 1);
    assert.deepEqual(r.fix_pack.snippets.map((s) => s.title), ['ok']);
    assert.equal(r.fix_pack.lang, 'en');
    assert.equal(sent.model, 'claude-sonnet-5-5');
    assert.match(sent.system, /NON fidato/);
    assert.match(sent.system, /lingua "en"/);
  } finally {
    globalThis.fetch = realFetch;
  }
}));

test('LLM in errore o JSON non valido → euristica', withEnv({ ANTHROPIC_API_KEY: 'test' }, async () => {
  const warn = console.warn;
  console.warn = () => {};
  try {
    globalThis.fetch = async () => new Response('{"error":{}}', { status: 500 });
    assert.equal((await analyze(data)).mode, 'heuristic');
    globalThis.fetch = async () => new Response(JSON.stringify({ stop_reason: 'end_turn', content: [{ type: 'text', text: 'non json' }] }));
    assert.equal((await analyze(data)).mode, 'heuristic');
    globalThis.fetch = async () => new Response(JSON.stringify({ stop_reason: 'refusal', content: [] }));
    assert.equal((await analyze(data)).mode, 'heuristic');
  } finally {
    globalThis.fetch = realFetch;
    console.warn = warn;
  }
  assert.throws(() => validateLlmResult({ score: 5, issues: [], fix_pack: { jsonld: 'not json', llms_txt: 'x' } }));
}));

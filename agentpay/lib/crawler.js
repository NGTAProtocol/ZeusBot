import * as cheerio from 'cheerio';
import { assertPublicUrl, UrlError } from './ssrf.js';

const USER_AGENT = 'AgentPayBot/0.1 (+https://github.com/agentpay)';
const TIMEOUT_MS = 8000;
const MAX_REDIRECTS = 3;
const MAX_BYTES = 1.5 * 1024 * 1024;
const AI_BOTS = ['GPTBot', 'ClaudeBot', 'anthropic-ai', 'Google-Extended', 'PerplexityBot', 'CCBot', 'OAI-SearchBot'];

export class CrawlError extends Error {
  constructor(message, status = 422) {
    super(message);
    this.name = 'CrawlError';
    this.status = status;
  }
}

export function normalizeUrl(input) {
  if (typeof input !== 'string') throw new UrlError('URL mancante.');
  let value = input.trim();
  if (!value) throw new UrlError('URL mancante.');
  if (value.length > 2048) throw new UrlError('URL troppo lungo.');
  if (!/^[a-z][a-z0-9+.-]*:\/\//i.test(value)) value = `https://${value.replace(/^\/+/, '')}`;
  let url;
  try {
    url = new URL(value);
  } catch {
    throw new UrlError('URL non valido.');
  }
  url.hash = '';
  return url.toString();
}

async function readCapped(response) {
  if (!response.body) return '';
  const reader = response.body.getReader();
  const chunks = [];
  let total = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const remaining = MAX_BYTES - total;
    if (value.byteLength >= remaining) {
      chunks.push(value.subarray(0, remaining));
      total += remaining;
      await reader.cancel().catch(() => {});
      break;
    }
    chunks.push(value);
    total += value.byteLength;
  }
  return new TextDecoder('utf-8').decode(Buffer.concat(chunks));
}

/**
 * fetch con timeout, redirect manuali (max 3, ogni hop validato contro SSRF)
 * e corpo troncato a 1.5 MB.
 */
export async function safeFetch(url, { accept = '*/*' } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    let current = new URL(url);
    for (let hop = 0; hop <= MAX_REDIRECTS; hop++) {
      await assertPublicUrl(current);
      const res = await fetch(current, {
        method: 'GET',
        redirect: 'manual',
        signal: controller.signal,
        headers: { 'User-Agent': USER_AGENT, Accept: accept, 'Accept-Language': 'it,en;q=0.8' }
      });
      if (res.status >= 300 && res.status < 400 && res.headers.get('location')) {
        await res.body?.cancel().catch(() => {});
        if (hop === MAX_REDIRECTS) throw new CrawlError('Troppi redirect.');
        current = new URL(res.headers.get('location'), current);
        continue;
      }
      const body = await readCapped(res);
      return {
        url: current.toString(),
        status: res.status,
        ok: res.ok,
        contentType: (res.headers.get('content-type') || '').toLowerCase(),
        body
      };
    }
    throw new CrawlError('Troppi redirect.');
  } catch (err) {
    if (err instanceof UrlError || err instanceof CrawlError) throw err;
    if (err.name === 'AbortError') throw new CrawlError('Timeout: il sito non ha risposto entro 8 secondi.');
    throw new CrawlError('Impossibile raggiungere il sito.');
  } finally {
    clearTimeout(timer);
  }
}

/** Come safeFetch ma non lancia mai: restituisce null in caso di errore. */
async function optionalFetch(url, accept) {
  try {
    return await safeFetch(url, { accept });
  } catch {
    return null;
  }
}

function looksLikeHtml(res) {
  return res.contentType.includes('text/html') || /^\s*(<!doctype html|<html|<head|<body)/i.test(res.body);
}

// ---------- robots.txt ----------

export function parseRobots(text, baseUrl) {
  const sitemaps = [];
  const groups = [];
  let current = null;
  let lastWasAgent = false;
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.replace(/#.*/, '').trim();
    if (!line) continue;
    const idx = line.indexOf(':');
    if (idx === -1) continue;
    const key = line.slice(0, idx).trim().toLowerCase();
    const value = line.slice(idx + 1).trim();
    if (key === 'sitemap') {
      try {
        sitemaps.push(new URL(value, baseUrl).toString());
      } catch {}
      continue;
    }
    if (key === 'user-agent') {
      if (!lastWasAgent || !current) {
        current = { agents: [], disallowAll: false };
        groups.push(current);
      }
      current.agents.push(value.toLowerCase());
      lastWasAgent = true;
      continue;
    }
    lastWasAgent = false;
    if (current && key === 'disallow' && value === '/') current.disallowAll = true;
  }
  const blockedAll = groups.some((g) => g.agents.includes('*') && g.disallowAll);
  const blockedAiBots = AI_BOTS.filter((bot) => {
    const specific = groups.filter((g) => g.agents.includes(bot.toLowerCase()));
    if (specific.length) return specific.some((g) => g.disallowAll);
    return blockedAll;
  });
  return { sitemaps: [...new Set(sitemaps)].slice(0, 10), blockedAiBots, blockedAll };
}

// ---------- JSON-LD ----------

function collectTypes(node, types, depth = 0) {
  if (!node || typeof node !== 'object' || depth > 6) return;
  if (Array.isArray(node)) {
    node.forEach((n) => collectTypes(n, types, depth + 1));
    return;
  }
  const t = node['@type'];
  if (typeof t === 'string') types.add(t);
  else if (Array.isArray(t)) t.filter((x) => typeof x === 'string').forEach((x) => types.add(x));
  if (Array.isArray(node['@graph'])) collectTypes(node['@graph'], types, depth + 1);
  for (const [k, v] of Object.entries(node)) {
    if (k !== '@graph' && v && typeof v === 'object') collectTypes(v, types, depth + 1);
  }
}

function hasPriceKey(node, depth = 0) {
  if (!node || typeof node !== 'object' || depth > 8) return false;
  if (Array.isArray(node)) return node.some((n) => hasPriceKey(n, depth + 1));
  return Object.entries(node).some(
    ([k, v]) => ((k === 'price' || k === 'lowPrice') && v !== '' && v != null) || hasPriceKey(v, depth + 1)
  );
}

export function extractJsonLd($) {
  const blocks = [];
  $('script[type="application/ld+json" i]').each((_, el) => {
    const raw = $(el).text().trim();
    if (!raw) return;
    try {
      blocks.push({ valid: true, data: JSON.parse(raw) });
    } catch {
      // alcuni siti mettono virgole finali o commenti HTML: secondo tentativo "pulito"
      try {
        const cleaned = raw.replace(/^<!--|-->$/g, '').replace(/,\s*([}\]])/g, '$1');
        blocks.push({ valid: true, data: JSON.parse(cleaned) });
      } catch {
        blocks.push({ valid: false, error: 'INVALID_JSON', raw: raw.slice(0, 300) });
      }
    }
  });
  const types = new Set();
  let hasPrice = false;
  for (const b of blocks.filter((b) => b.valid)) {
    collectTypes(b.data, types);
    if (hasPriceKey(b.data)) hasPrice = true;
  }
  const samples = blocks.slice(0, 3).map((b) => {
    if (!b.valid) return { error: b.error, raw: b.raw };
    const text = JSON.stringify(b.data);
    return text.length > 1500 ? { truncated: true, json: text.slice(0, 1500) } : b.data;
  });
  return {
    count: blocks.length,
    validCount: blocks.filter((b) => b.valid).length,
    invalidCount: blocks.filter((b) => !b.valid).length,
    types: [...types].slice(0, 30),
    hasPrice,
    samples
  };
}

// ---------- HTML ----------

const PRICE_RE = /(?:€|EUR)\s?\d{1,3}(?:[.,\s]\d{3})*(?:[.,]\d{1,2})?|\d{1,3}(?:[.,\s]?\d{3})*(?:[.,]\d{1,2})?\s?(?:€|EUR)\b|\$\s?\d{1,3}(?:[,.]?\d{3})*(?:\.\d{1,2})?/g;

export function extractHtml(html, pageUrl) {
  const $ = cheerio.load(html);
  const meta = (sel) => ($(sel).attr('content') || '').trim() || null;
  const absolute = (href) => {
    if (!href) return null;
    try {
      return new URL(href, pageUrl).toString();
    } catch {
      return null;
    }
  };

  const jsonld = extractJsonLd($);

  const forms = [];
  $('form').each((_, form) => {
    const inputs = $(form).find('input, select, textarea').filter((_, el) => {
      const type = ($(el).attr('type') || '').toLowerCase();
      return !['hidden', 'submit', 'button', 'reset', 'image'].includes(type);
    });
    let unlabeled = 0;
    inputs.each((_, el) => {
      const $el = $(el);
      const id = $el.attr('id');
      const hasLabel =
        (id && $(form).find(`label[for="${id.replace(/"/g, '\\"')}"]`).length > 0) ||
        $el.closest('label').length > 0 ||
        $el.attr('aria-label') ||
        $el.attr('aria-labelledby') ||
        $el.attr('name');
      if (!hasLabel) unlabeled++;
    });
    forms.push({ inputs: inputs.length, unlabeled });
  });

  const machinePrices = {
    itemprop: $('[itemprop="price"]').length,
    ogProductPrice: $('meta[property="product:price:amount"]').length,
    jsonld: jsonld.hasPrice
  };

  // testo principale
  const root = $('main').length ? $('main').first().clone() : $('body').clone();
  root.find('script, style, noscript, nav, footer, svg, template, iframe').remove();
  const text = root.text().replace(/\s+/g, ' ').trim();
  const visiblePrices = [...new Set(text.match(PRICE_RE) || [])].map((p) => p.trim()).slice(0, 10);

  return {
    title: $('title').first().text().trim() || null,
    description: meta('meta[name="description" i]'),
    canonical: absolute($('link[rel="canonical" i]').attr('href')),
    lang: ($('html').attr('lang') || '').trim() || null,
    ogTitle: meta('meta[property="og:title"]'),
    ogImage: absolute(meta('meta[property="og:image"]')),
    ogSiteName: meta('meta[property="og:site_name"]'),
    h1: $('h1').first().text().replace(/\s+/g, ' ').trim() || null,
    h2: $('h2')
      .map((_, el) => $(el).text().replace(/\s+/g, ' ').trim())
      .get()
      .filter(Boolean)
      .slice(0, 8),
    jsonld,
    text: text.slice(0, 4000),
    prices: {
      visible: visiblePrices,
      visibleCount: visiblePrices.length,
      machineReadable: machinePrices,
      hasMachineReadable: machinePrices.itemprop > 0 || machinePrices.ogProductPrice > 0 || machinePrices.jsonld
    },
    forms
  };
}

function isValidSitemap(res) {
  return !!res && res.ok && /<(urlset|sitemapindex)[\s>]/i.test(res.body);
}

// ---------- crawl ----------

export async function crawl(inputUrl) {
  const url = normalizeUrl(inputUrl);
  await assertPublicUrl(url);
  const origin = new URL(url).origin;

  const [home, robotsRes, sitemapRes, llmsRes] = await Promise.all([
    safeFetch(url, { accept: 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.5' }),
    optionalFetch(`${origin}/robots.txt`, 'text/plain,*/*;q=0.5'),
    optionalFetch(`${origin}/sitemap.xml`, 'application/xml,text/xml,*/*;q=0.5'),
    optionalFetch(`${origin}/llms.txt`, 'text/plain,text/markdown,*/*;q=0.5')
  ]);

  if (!home.ok) throw new CrawlError(`Il sito ha risposto con stato HTTP ${home.status}.`);
  if (!looksLikeHtml(home)) throw new CrawlError('La pagina non restituisce HTML analizzabile.');

  const page = extractHtml(home.body, home.url);

  const robotsOk = !!robotsRes && robotsRes.ok && !looksLikeHtml(robotsRes);
  const robots = robotsOk
    ? { found: true, ...parseRobots(robotsRes.body, origin) }
    : { found: false, sitemaps: [], blockedAiBots: [], blockedAll: false };

  let sitemap = { found: isValidSitemap(sitemapRes), url: `${origin}/sitemap.xml` };
  if (!sitemap.found && robots.sitemaps.length) {
    const declared = await optionalFetch(robots.sitemaps[0], 'application/xml,text/xml,*/*;q=0.5');
    sitemap = { found: isValidSitemap(declared), url: robots.sitemaps[0] };
  }

  const llmsValid = !!llmsRes && llmsRes.ok && !looksLikeHtml(llmsRes) && llmsRes.body.trim().length > 0;
  const llms = {
    found: llmsValid,
    url: `${origin}/llms.txt`,
    excerpt: llmsValid ? llmsRes.body.slice(0, 1000) : null
  };

  return {
    url,
    finalUrl: home.url,
    origin,
    status: home.status,
    page,
    robots,
    sitemap,
    llms
  };
}

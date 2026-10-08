import { crawl, normalizeUrl } from '../lib/crawler.js';
import { analyze } from '../lib/analyzer.js';

export const config = { maxDuration: 60 };

const MAX_BODY = 10 * 1024;
const RATE_LIMIT = 5;
const RATE_WINDOW_MS = 60_000;
const hits = new Map(); // ip -> timestamps (in memoria, per istanza)

function send(res, status, payload, extraHeaders = {}) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  for (const [k, v] of Object.entries(extraHeaders)) res.setHeader(k, v);
  res.end(JSON.stringify(payload));
}

function clientIp(req) {
  const fwd = req.headers['x-forwarded-for'];
  if (typeof fwd === 'string' && fwd) return fwd.split(',')[0].trim();
  return req.headers['x-real-ip'] || req.socket?.remoteAddress || 'unknown';
}

function rateLimited(ip) {
  const now = Date.now();
  const recent = (hits.get(ip) || []).filter((t) => now - t < RATE_WINDOW_MS);
  if (recent.length >= RATE_LIMIT) {
    hits.set(ip, recent);
    return Math.ceil((RATE_WINDOW_MS - (now - recent[0])) / 1000);
  }
  recent.push(now);
  hits.set(ip, recent);
  if (hits.size > 5000) {
    for (const [k, v] of hits) if (!v.some((t) => now - t < RATE_WINDOW_MS)) hits.delete(k);
  }
  return 0;
}

class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function readBody(req) {
  if (req.body !== undefined && req.body !== null && req.body !== '') {
    if (typeof req.body === 'object' && !Buffer.isBuffer(req.body)) return req.body;
    const text = Buffer.isBuffer(req.body) ? req.body.toString('utf8') : String(req.body);
    if (text.length > MAX_BODY) throw new HttpError(413, 'Richiesta troppo grande.');
    return parseJson(text);
  }
  let size = 0;
  const chunks = [];
  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_BODY) throw new HttpError(413, 'Richiesta troppo grande (max 10 KB).');
    chunks.push(chunk);
  }
  return parseJson(Buffer.concat(chunks).toString('utf8'));
}

function parseJson(text) {
  try {
    return JSON.parse(text || '{}');
  } catch {
    throw new HttpError(400, 'Corpo della richiesta non è JSON valido.');
  }
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return send(res, 405, { error: 'Metodo non consentito: usa POST.' }, { Allow: 'POST' });
  }
  const retryAfter = rateLimited(clientIp(req));
  if (retryAfter) {
    return send(res, 429, { error: `Troppe richieste: riprova tra ${retryAfter} secondi.` }, { 'Retry-After': String(retryAfter) });
  }
  try {
    const body = await readBody(req);
    if (!body || typeof body.url !== 'string' || !body.url.trim()) {
      throw new HttpError(400, 'Inserisci un URL da analizzare.');
    }
    const url = normalizeUrl(body.url);
    const data = await crawl(url);
    const result = await analyze(data);
    return send(res, 200, {
      url: data.finalUrl,
      score: result.score,
      issues: result.issues,
      fix_pack: result.fix_pack,
      mode: result.mode,
      scanned_at: new Date().toISOString()
    });
  } catch (err) {
    const status = Number.isInteger(err.status) ? err.status : 500;
    if (status >= 500) console.error('[agentpay] errore interno:', err);
    const message = status >= 500 ? 'Errore interno durante l’analisi. Riprova più tardi.' : err.message;
    return send(res, status, { error: message });
  }
}

export class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.name = 'HttpError';
    this.status = status;
  }
}

export function send(res, status, payload, extraHeaders = {}) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  for (const [k, v] of Object.entries(extraHeaders)) res.setHeader(k, v);
  res.end(JSON.stringify(payload));
}

export function clientIp(req) {
  const fwd = req.headers['x-forwarded-for'];
  if (typeof fwd === 'string' && fwd) return fwd.split(',')[0].trim();
  return req.headers['x-real-ip'] || req.socket?.remoteAddress || 'unknown';
}

/** Rate limit in memoria (per istanza). Restituisce i secondi di attesa, 0 se consentito. */
export function createRateLimiter(limit, windowMs = 60_000) {
  const hits = new Map();
  return function check(key) {
    const now = Date.now();
    const recent = (hits.get(key) || []).filter((t) => now - t < windowMs);
    if (recent.length >= limit) {
      hits.set(key, recent);
      return Math.ceil((windowMs - (now - recent[0])) / 1000);
    }
    recent.push(now);
    hits.set(key, recent);
    if (hits.size > 5000) {
      for (const [k, v] of hits) if (!v.some((t) => now - t < windowMs)) hits.delete(k);
    }
    return 0;
  };
}

function parseJson(text) {
  try {
    return JSON.parse(text || '{}');
  } catch {
    throw new HttpError(400, 'Corpo della richiesta non è JSON valido.');
  }
}

/** Legge il corpo JSON: usa req.body se già parsato (Vercel), altrimenti lo stream (server locale). */
export async function readJsonBody(req, maxBytes) {
  const tooBig = () => new HttpError(413, `Richiesta troppo grande (max ${Math.round(maxBytes / 1024)} KB).`);
  if (req.body !== undefined && req.body !== null && req.body !== '') {
    if (typeof req.body === 'object' && !Buffer.isBuffer(req.body)) return req.body;
    const text = Buffer.isBuffer(req.body) ? req.body.toString('utf8') : String(req.body);
    if (Buffer.byteLength(text) > maxBytes) throw tooBig();
    return parseJson(text);
  }
  let size = 0;
  const chunks = [];
  for await (const chunk of req) {
    size += chunk.length;
    if (size > maxBytes) throw tooBig();
    chunks.push(chunk);
  }
  return parseJson(Buffer.concat(chunks).toString('utf8'));
}

export function errorResponse(res, err) {
  const status = Number.isInteger(err.status) ? err.status : 500;
  if (status >= 500) console.error('[agentpay] errore:', err);
  const message = status >= 500 && !err.expose ? 'Errore interno. Riprova più tardi.' : err.message;
  return send(res, status, { error: message });
}

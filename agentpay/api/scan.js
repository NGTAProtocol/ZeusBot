import { crawl as realCrawl, normalizeUrl } from '../lib/crawler.js';
import { analyze as realAnalyze } from '../lib/analyzer.js';
import { send, clientIp, createRateLimiter, readJsonBody, errorResponse, HttpError } from '../lib/http.js';
import { newScanId, encryptPack, getPackKey, buildTeaser } from '../lib/pack.js';
import { paymentConfig } from '../lib/stripe.js';

export const config = { maxDuration: 60 };

const MAX_BODY = 10 * 1024;

export function createScanHandler({ crawl = realCrawl, analyze = realAnalyze, rateLimit = 5 } = {}) {
  const limiter = createRateLimiter(rateLimit);
  return async function handler(req, res) {
    if (req.method !== 'POST') return send(res, 405, { error: 'Metodo non consentito: usa POST.' }, { Allow: 'POST' });
    const wait = limiter(clientIp(req));
    if (wait) return send(res, 429, { error: `Troppe richieste: riprova tra ${wait} secondi.` }, { 'Retry-After': String(wait) });
    try {
      const body = await readJsonBody(req, MAX_BODY);
      if (!body || typeof body.url !== 'string' || !body.url.trim()) throw new HttpError(400, 'Inserisci un URL da analizzare.');
      // la chiave serve prima del crawl: in modalità Stripe senza PACK_SECRET falliamo subito
      const key = getPackKey({ required: paymentConfig().mode === 'stripe' });
      const data = await crawl(normalizeUrl(body.url));
      const result = await analyze(data);
      const scan_id = newScanId();
      return send(res, 200, {
        url: data.finalUrl,
        score: result.score,
        issues: result.issues,
        mode: result.mode,
        scanned_at: new Date().toISOString(),
        scan_id,
        teaser: buildTeaser(result.fix_pack),
        locked: encryptPack({ fix_pack: result.fix_pack, scan_id, url: data.finalUrl }, key)
      });
    } catch (err) {
      return errorResponse(res, err);
    }
  };
}

export default createScanHandler();

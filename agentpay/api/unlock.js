import { send, clientIp, createRateLimiter, readJsonBody, errorResponse, HttpError } from '../lib/http.js';
import { decryptPack, getPackKey } from '../lib/pack.js';
import { paymentConfig, getCheckoutSession } from '../lib/stripe.js';

const MAX_BODY = 256 * 1024;
const limiter = createRateLimiter(20);

export default async function handler(req, res) {
  if (req.method !== 'POST') return send(res, 405, { error: 'Metodo non consentito: usa POST.' }, { Allow: 'POST' });
  const wait = limiter(clientIp(req));
  if (wait) return send(res, 429, { error: `Troppe richieste: riprova tra ${wait} secondi.` }, { 'Retry-After': String(wait) });
  try {
    const body = await readJsonBody(req, MAX_BODY);
    if (typeof body.locked !== 'string' || !body.locked) throw new HttpError(400, 'Dati della scansione mancanti: ripeti la scansione.');
    const cfg = paymentConfig();
    const pack = decryptPack(body.locked, getPackKey({ required: cfg.mode === 'stripe' }));

    if (cfg.mode === 'demo') {
      if (body.demo !== true) throw new HttpError(400, 'Modalità demo: usa il pagamento simulato.');
      return send(res, 200, { scan_id: pack.scan_id, url: pack.url, fix_pack: pack.fix_pack, payments: 'demo' });
    }

    const session = await getCheckoutSession(body.session_id);
    if (!session) return send(res, 402, { error: 'Pagamento non trovato per questo codice.' });
    if (session.payment_status !== 'paid') {
      return send(res, 402, { error: 'Il pagamento non risulta completato.' });
    }
    if (session.client_reference_id !== pack.scan_id) {
      return send(res, 402, { error: 'Questo pagamento non corrisponde alla scansione corrente.' });
    }
    return send(res, 200, { scan_id: pack.scan_id, url: pack.url, fix_pack: pack.fix_pack, payments: 'stripe' });
  } catch (err) {
    return errorResponse(res, err);
  }
}

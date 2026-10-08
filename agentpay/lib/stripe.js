import { HttpError } from './http.js';

const STRIPE_API = 'https://api.stripe.com/v1';

/** Modalità di pagamento: "stripe" solo se chiave segreta e Payment Link sono configurati. */
export function paymentConfig() {
  const secret = process.env.STRIPE_SECRET_KEY || '';
  const link = process.env.STRIPE_PAYMENT_LINK_URL || '';
  let linkOk = false;
  try {
    linkOk = new URL(link).protocol === 'https:';
  } catch {}
  const mode = secret && linkOk ? 'stripe' : 'demo';
  return {
    mode,
    paymentLinkUrl: mode === 'stripe' ? link : null,
    supportEmail: process.env.SUPPORT_EMAIL || null
  };
}

export function isCheckoutSessionId(value) {
  return typeof value === 'string' && /^cs_(test|live)_[A-Za-z0-9]{10,250}$/.test(value);
}

/** Legge la Checkout Session da Stripe (fetch, nessun SDK). Restituisce null se non esiste. */
export async function getCheckoutSession(sessionId) {
  if (!isCheckoutSessionId(sessionId)) throw new HttpError(400, 'Codice di pagamento (session_id) non valido.');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  let res;
  try {
    res = await fetch(`${STRIPE_API}/checkout/sessions/${encodeURIComponent(sessionId)}`, {
      headers: { Authorization: `Bearer ${process.env.STRIPE_SECRET_KEY}` },
      signal: controller.signal
    });
  } catch {
    throw Object.assign(new HttpError(502, 'Impossibile verificare il pagamento con Stripe: riprova tra poco.'), { expose: true });
  } finally {
    clearTimeout(timer);
  }
  if (res.status === 404) return null;
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    console.error('[agentpay] Stripe', res.status, text.slice(0, 300));
    throw Object.assign(new HttpError(502, 'Impossibile verificare il pagamento con Stripe: riprova tra poco.'), { expose: true });
  }
  return res.json();
}

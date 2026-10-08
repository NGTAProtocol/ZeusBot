import { send } from '../lib/http.js';
import { paymentConfig } from '../lib/stripe.js';

// Espone al frontend solo dati pubblici: mai chiavi segrete.
export default function handler(req, res) {
  if (req.method !== 'GET') return send(res, 405, { error: 'Metodo non consentito: usa GET.' }, { Allow: 'GET' });
  const cfg = paymentConfig();
  return send(res, 200, {
    payments: cfg.mode,
    payment_link_url: cfg.paymentLinkUrl,
    support_email: cfg.supportEmail,
    price_eur: 9
  });
}

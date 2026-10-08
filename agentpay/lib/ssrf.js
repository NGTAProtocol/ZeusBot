import { lookup } from 'node:dns/promises';
import { isIP } from 'node:net';

export class UrlError extends Error {
  constructor(message, status = 400) {
    super(message);
    this.name = 'UrlError';
    this.status = status;
  }
}

const BLOCKED_HOSTNAMES = new Set(['localhost', 'localhost.localdomain', 'ip6-localhost', 'ip6-loopback']);
const BLOCKED_SUFFIXES = ['.localhost', '.local', '.internal', '.lan', '.home.arpa'];

function ipv4ToInt(ip) {
  return ip.split('.').reduce((acc, part) => (acc << 8) + Number(part), 0) >>> 0;
}

function inCidr4(ip, base, bits) {
  const mask = bits === 0 ? 0 : (~0 << (32 - bits)) >>> 0;
  return (ipv4ToInt(ip) & mask) === (ipv4ToInt(base) & mask);
}

const PRIVATE_V4 = [
  ['0.0.0.0', 8], // "this network"
  ['10.0.0.0', 8],
  ['100.64.0.0', 10], // CGNAT 100.64-127.x
  ['127.0.0.0', 8],
  ['169.254.0.0', 16], // link-local / metadata cloud
  ['172.16.0.0', 12],
  ['192.0.0.0', 24],
  ['192.168.0.0', 16],
  ['198.18.0.0', 15],
  ['224.0.0.0', 4], // multicast
  ['240.0.0.0', 4] // riservati + broadcast
];

export function isPrivateIp(ip) {
  const family = isIP(ip);
  if (family === 4) return PRIVATE_V4.some(([base, bits]) => inCidr4(ip, base, bits));
  if (family === 6) {
    const lower = ip.toLowerCase();
    // IPv4-mapped (::ffff:a.b.c.d) e IPv4-compatible
    const mapped = lower.match(/^(?:::ffff:|::)(\d+\.\d+\.\d+\.\d+)$/);
    if (mapped) return isPrivateIp(mapped[1]);
    const hexMapped = lower.match(/^::ffff:([0-9a-f]{1,4}):([0-9a-f]{1,4})$/);
    if (hexMapped) {
      const hi = parseInt(hexMapped[1], 16);
      const lo = parseInt(hexMapped[2], 16);
      return isPrivateIp(`${hi >> 8}.${hi & 255}.${lo >> 8}.${lo & 255}`);
    }
    if (lower === '::' || lower === '::1') return true;
    if (/^f[cd]/.test(lower)) return true; // fc00::/7 unique local
    if (/^fe[89ab]/.test(lower)) return true; // fe80::/10 link-local
    if (/^ff/.test(lower)) return true; // multicast
    if (/^64:ff9b:/.test(lower)) return true; // NAT64: può puntare a IPv4 privati
    return false;
  }
  return true; // non è un IP valido: trattalo come non sicuro
}

/**
 * Verifica che l'URL punti a un host pubblico e risolve il DNS UNA sola volta.
 * Restituisce { url, address, family }: il chiamante deve connettersi a `address`
 * (DNS pinning, contro il DNS rebinding). Lancia UrlError altrimenti.
 */
export async function resolvePublicUrl(url) {
  let parsed;
  try {
    parsed = url instanceof URL ? new URL(url.href) : new URL(url);
  } catch {
    throw new UrlError('URL non valido.');
  }
  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    throw new UrlError('Sono ammessi solo URL http o https.');
  }
  if (parsed.username || parsed.password) {
    throw new UrlError('Gli URL con credenziali non sono ammessi.');
  }
  const host = parsed.hostname.toLowerCase().replace(/^\[|\]$/g, '').replace(/\.$/, '');
  if (!host) throw new UrlError('URL non valido: host mancante.');
  if (BLOCKED_HOSTNAMES.has(host) || BLOCKED_SUFFIXES.some((s) => host.endsWith(s))) {
    throw new UrlError('Indirizzi locali o interni non sono ammessi.');
  }
  const literal = isIP(host);
  if (literal) {
    if (isPrivateIp(host)) throw new UrlError('Indirizzi IP privati o locali non sono ammessi.');
    return { url: parsed, address: host, family: literal };
  }
  if (!host.includes('.')) throw new UrlError('Hostname non valido: serve un dominio pubblico.');

  let addresses;
  try {
    addresses = await lookup(host, { all: true, verbatim: true });
  } catch {
    throw new UrlError('Dominio non trovato (DNS).', 422);
  }
  if (!addresses.length) throw new UrlError('Dominio non trovato (DNS).', 422);
  if (addresses.some((a) => isPrivateIp(a.address))) {
    throw new UrlError('Il dominio risolve su un indirizzo privato o locale: non ammesso.');
  }
  const preferred = addresses.find((a) => a.family === 4) || addresses[0];
  return { url: parsed, address: preferred.address, family: preferred.family };
}

/** Compatibilità: valida l'URL e restituisce l'oggetto URL. */
export async function assertPublicUrl(url) {
  return (await resolvePublicUrl(url)).url;
}

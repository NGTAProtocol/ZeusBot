import { createCipheriv, createDecipheriv, randomBytes } from 'node:crypto';
import { deflateRawSync, inflateRawSync } from 'node:zlib';
import { HttpError } from './http.js';

const VERSION = 'v1';
const AAD = Buffer.from('agentpay:pack:v1');
const MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000; // il blob vale 7 giorni
const ID_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-';

let ephemeralKey = null;

/** 16 caratteri [a-zA-Z0-9_-] (64 simboli: nessun bias modulo). */
export function newScanId() {
  return Array.from(randomBytes(16), (b) => ID_ALPHABET[b & 63]).join('');
}

export function isScanId(value) {
  return typeof value === 'string' && /^[A-Za-z0-9_-]{16}$/.test(value);
}

/**
 * Chiave AES-256 da PACK_SECRET (32 byte in base64).
 * Senza PACK_SECRET: errore se `required`, altrimenti (solo demo) chiave casuale valida per questo processo.
 */
export function getPackKey({ required = false } = {}) {
  const raw = process.env.PACK_SECRET;
  if (raw) {
    const key = Buffer.from(raw, 'base64');
    if (key.length !== 32) {
      throw Object.assign(new HttpError(500, 'Configurazione non valida: PACK_SECRET deve essere di 32 byte in base64.'), { expose: true });
    }
    return key;
  }
  if (required) {
    throw Object.assign(new HttpError(500, 'Configurazione mancante: PACK_SECRET non impostata.'), { expose: true });
  }
  if (!ephemeralKey) {
    ephemeralKey = randomBytes(32);
    console.warn('[agentpay] PACK_SECRET assente: uso una chiave temporanea (solo modalità demo, si perde al riavvio).');
  }
  return ephemeralKey;
}

export function encryptPack({ fix_pack, scan_id, url }, key) {
  const iv = randomBytes(12);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  cipher.setAAD(AAD);
  const plain = deflateRawSync(Buffer.from(JSON.stringify({ scan_id, url, iat: Date.now(), fix_pack })));
  const ct = Buffer.concat([cipher.update(plain), cipher.final()]);
  return `${VERSION}.${Buffer.concat([iv, cipher.getAuthTag(), ct]).toString('base64url')}`;
}

export function decryptPack(locked, key, { now = Date.now() } = {}) {
  const invalid = () => new HttpError(400, 'Dati della scansione non validi o danneggiati: ripeti la scansione.');
  if (typeof locked !== 'string' || !locked.startsWith(`${VERSION}.`)) throw invalid();
  const buf = Buffer.from(locked.slice(VERSION.length + 1), 'base64url');
  if (buf.length < 12 + 16 + 1) throw invalid();
  let payload;
  try {
    const decipher = createDecipheriv('aes-256-gcm', key, buf.subarray(0, 12));
    decipher.setAAD(AAD);
    decipher.setAuthTag(buf.subarray(12, 28));
    const plain = Buffer.concat([decipher.update(buf.subarray(28)), decipher.final()]);
    payload = JSON.parse(inflateRawSync(plain, { maxOutputLength: 2 * 1024 * 1024 }).toString('utf8'));
  } catch {
    throw invalid();
  }
  if (!isScanId(payload.scan_id) || !payload.fix_pack) throw invalid();
  if (!(now - payload.iat < MAX_AGE_MS)) throw new HttpError(410, 'La scansione è scaduta (più di 7 giorni): ripeti l’analisi.');
  return payload;
}

/** Teaser pubblico: titolo di ogni file del Fix Pack e solo le prime 3 righe. */
export function buildTeaser(fixPack) {
  const entry = (title, filename, content) => {
    const lines = String(content || '').split('\n');
    return { title, filename, preview: lines.slice(0, 3).join('\n'), total_lines: lines.length };
  };
  const files = [];
  if (fixPack.jsonld) files.push(entry('JSON-LD (schema.org)', 'agentpay-jsonld.json', fixPack.jsonld));
  if (fixPack.llms_txt) files.push(entry('llms.txt', 'llms.txt', fixPack.llms_txt));
  (fixPack.snippets || []).forEach((s, i) => files.push(entry(s.title, `snippet-${i + 1}`, s.code)));
  return { lang: fixPack.lang || null, files };
}

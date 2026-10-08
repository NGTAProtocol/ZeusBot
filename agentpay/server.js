import http from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { extname, join, normalize, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import scanHandler from './api/scan.js';
import unlockHandler from './api/unlock.js';
import configHandler from './api/config.js';
import { paymentConfig } from './lib/stripe.js';

const API = { '/api/scan': scanHandler, '/api/unlock': unlockHandler, '/api/config': configHandler };

// Carica .env se presente (senza dipendenze esterne)
try {
  process.loadEnvFile?.(fileURLToPath(new URL('./.env', import.meta.url)));
} catch {}

const PORT = Number(process.env.PORT) || 3000;
const PUBLIC_DIR = fileURLToPath(new URL('./public', import.meta.url));
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
  '.txt': 'text/plain; charset=utf-8'
};

async function serveStatic(req, res) {
  const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  const rel = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
  const file = normalize(join(PUBLIC_DIR, rel));
  if (!file.startsWith(PUBLIC_DIR + sep)) {
    res.writeHead(403).end('Forbidden');
    return;
  }
  try {
    const info = await stat(file);
    if (!info.isFile()) throw new Error('not a file');
    const content = await readFile(file);
    res.writeHead(200, { 'Content-Type': MIME[extname(file)] || 'application/octet-stream' });
    res.end(content);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('Non trovato');
  }
}

const server = http.createServer(async (req, res) => {
  try {
    const { pathname } = new URL(req.url, 'http://localhost');
    if (API[pathname]) return await API[pathname](req, res);
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.writeHead(405).end();
      return;
    }
    await serveStatic(req, res);
  } catch (err) {
    console.error(err);
    if (!res.headersSent) res.writeHead(500).end('Errore interno');
  }
});

server.listen(PORT, () => {
  const mode = process.env.ANTHROPIC_API_KEY ? 'LLM' : 'euristica (nessuna ANTHROPIC_API_KEY)';
  const pay = paymentConfig().mode === 'stripe' ? 'Stripe' : 'DEMO (pagamento simulato)';
  console.log(`AgentPay in ascolto su http://localhost:${PORT} — analisi: ${mode} — pagamenti: ${pay}`);
});

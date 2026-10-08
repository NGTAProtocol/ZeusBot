# AgentPay (MVP)

AgentPay analizza un sito o e-commerce, calcola un **Agent Score** da 0 a 100, elenca i problemi che impediscono agli agenti AI (ChatGPT, Claude, Perplexity, assistenti di acquisto) di leggerlo e usarlo, e genera un **Fix Pack** pronto all'uso: JSON-LD schema.org, `llms.txt` e snippet con istruzioni.

L'MVP gira a costo zero: niente database, nessun framework, una sola dipendenza (`cheerio`), deploy gratuito su Vercel. L'analisi con Claude è opzionale: senza chiave API funziona in modalità euristica.

## Requisiti

- Node.js **>= 20** (consigliato 20.12+ o 22, per il caricamento automatico di `.env`)
- (Opzionale) una chiave API Anthropic

## Setup locale

```bash
cd agentpay
npm install
cp .env.example .env       # facoltativo: inserisci ANTHROPIC_API_KEY
npm run dev                # http://localhost:3000
```

### Variabili d'ambiente (`.env.example`)

| Variabile | Default | Descrizione |
|---|---|---|
| `ANTHROPIC_API_KEY` | vuota | Se presente, attiva l'analisi con Claude (`mode: "llm"`). Se manca o la chiamata fallisce, si usa l'euristica (`mode: "heuristic"`). |
| `ANTHROPIC_MODEL` | `claude-sonnet-5-5` | Modello usato per l'analisi LLM. |
| `PORT` | `3000` | Porta del server locale. |

Opzionale (non in `.env.example`): `ANTHROPIC_TIMEOUT_MS` (default 50000) per il timeout della chiamata a Claude.

## Comandi

| Comando | Cosa fa |
|---|---|
| `npm run dev` / `npm start` | Server locale (`server.js`, `node:http`): serve `public/` e instrada `POST /api/scan` |
| `npm test` | Test unitari senza rete (SSRF sui redirect, crawler, euristica, fix pack, percorso LLM simulato e fallback) |

## API

`POST /api/scan` con corpo JSON `{"url": "www.esempio.it"}` (max 10 KB).

Risposta 200:

```json
{
  "url": "https://www.esempio.it/",
  "score": 61,
  "issues": [{ "severity": "critical", "title": "...", "detail": "..." }],
  "fix_pack": { "jsonld": "...", "llms_txt": "...", "snippets": [{ "title": "...", "language": "html", "code": "...", "instructions": "..." }] },
  "mode": "heuristic",
  "scanned_at": "2026-10-08T04:00:00.000Z"
}
```

Errori (sempre JSON `{"error": "..."}`, in italiano): `400` input non valido o indirizzo privato/locale, `405` metodo non POST, `413` corpo troppo grande, `422` sito non raggiungibile / DNS / HTTP non 2xx / non HTML, `429` rate limit (5 richieste al minuto per IP), `500` errore interno.

## Come funziona

```
api/scan.js      handler (Vercel + server locale): validazione, rate limit, crawl → analyze
lib/ssrf.js      assertPublicUrl: solo http/https, blocca localhost/*.local/*.internal e IP privati dopo risoluzione DNS
lib/crawler.js   safeFetch (timeout 8 s, max 3 redirect validati a ogni hop, corpo max 1.5 MB) + estrazione con cheerio
lib/analyzer.js  heuristicScan (0-100), analyzeWithLLM (Claude via fetch), fix pack da template, analyze()
public/index.html  frontend (Tailwind CDN + JS vanilla, solo textContent/createElement)
server.js        server di sviluppo
```

Il crawler scarica in parallelo homepage, `/robots.txt`, `/sitemap.xml` e `/llms.txt` (le risorse opzionali non generano mai errori; un `llms.txt` che risponde HTML è considerato assente). Se `/sitemap.xml` manca, prova la prima sitemap dichiarata in `robots.txt`.

### Pesi dell'Agent Score euristico

| Controllo | Punti |
|---|---|
| Almeno un JSON-LD valido | 25 |
| JSON-LD di tipo Product/Offer o Organization | 15 |
| `llms.txt` valido | 15 |
| `robots.txt` senza `Disallow: /` per i bot AI (GPTBot, ClaudeBot, anthropic-ai, Google-Extended, PerplexityBot, CCBot, OAI-SearchBot) — 5 se robots.txt manca | 10 |
| Sitemap XML valida | 10 |
| Prezzi machine-readable quando ci sono prezzi visibili (pieno se non ci sono prezzi) | 10 |
| title + meta description + canonical + lang (2,5 ciascuno) | 10 |
| Campi dei form con label/aria-label/name (proporzionale; pieno se non ci sono form) | 5 |

### Modalità LLM

Con `ANTHROPIC_API_KEY` impostata, i dati raccolti e il risultato euristico vengono inviati a `https://api.anthropic.com/v1/messages` (fetch nativo, nessun SDK). Il system prompt:

- impone come output **solo JSON** con lo schema `{score, issues, fix_pack}`;
- vieta di inventare prezzi o dati: dove manca un'informazione va usato il segnaposto `DA_COMPILARE`;
- dichiara il testo del sito **contenuto non fidato** e ordina di ignorare ogni istruzione in esso contenuta (difesa da prompt injection).

La risposta viene ripulita da eventuali ```` ``` ````, validata (severity ammesse, JSON-LD parsabile, llms.txt non vuoto) e lo score è limitato a 0-100. Qualsiasi errore (HTTP, timeout, rifiuto del modello, JSON non valido) fa ripiegare sull'euristica con fix pack da template.

## Deploy su Vercel

1. Importa il repository su [vercel.com](https://vercel.com) (piano Hobby gratuito). Se `agentpay/` è una sottocartella, imposta **Root Directory = `agentpay`**.
2. Framework preset: **Other**. Nessun build command; output: la cartella `public/` viene servita come statica e `api/scan.js` diventa la funzione serverless `/api/scan`.
3. In *Settings → Environment Variables* aggiungi (facoltativo) `ANTHROPIC_API_KEY` e `ANTHROPIC_MODEL`.
4. Deploy. La funzione dichiara `maxDuration: 60` per lasciare tempo alla chiamata LLM.

Da CLI: `npx vercel` (anteprima) e `npx vercel --prod`.

## Test eseguiti

- Scansione reale di `nodejs.org` (score 60) e `www.anthropic.com` (score 45) in modalità euristica; un host che risponde 400 restituisce correttamente 422.
- Rifiutati con 400: `localhost`, `127.0.0.1`, `192.168.1.1`, `10.0.0.5`, `[::1]`, `[::ffff:127.0.0.1]`, `169.254.169.254`, `0x7f000001`, `2130706433`, `printer.local`, `ftp://…`, un dominio pubblico che risolve su 127.0.0.1 (`localtest.me`), un redirect verso 127.0.0.1.
- Input non valido, corpo vuoto, JSON rotto, corpo > 10 KB, GET, rate limit (6ª richiesta → 429).
- Frontend testato con Playwright: stato vuoto, errori, gauge, problemi, sblocco simulato, download.
- Modalità LLM verificata con risposta Anthropic **simulata** (nessuna chiave disponibile durante lo sviluppo): va provata con una chiave reale prima del lancio.

## Limiti noti

- **Il Fix Pack non è protetto lato server**: l'API restituisce sempre il fix pack completo e il frontend lo nasconde finché non si "paga". Chiunque può leggerlo dalla risposta di rete. Va bene per una demo, non per incassare.
- **Pagamento simulato**: il bottone apre solo una modale demo.
- **Rate limit in memoria**: per singola istanza serverless, si azzera a ogni cold start; in locale l'IP viene da `X-Forwarded-For`, che è falsificabile.
- **DNS rebinding**: l'IP viene verificato prima di ogni richiesta, ma `fetch` risolve di nuovo il DNS; un attaccante con TTL molto bassi potrebbe teoricamente alternare IP pubblico/privato. Mitigazione futura: connessione verso l'IP già validato (dispatcher `undici` con `lookup` personalizzato).
- Viene analizzata **solo la homepage**: niente crawling di schede prodotto o categorie, niente rendering JavaScript (i siti SPA che generano JSON-LD lato client risultano senza dati strutturati).
- Il rilevamento dei prezzi visibili usa espressioni regolari (€, EUR, $) e può dare falsi positivi/negativi.
- Il Tailwind Play CDN non è pensato per la produzione (va sostituito con un CSS compilato).
- In ambienti dietro proxy HTTP(S) avvia Node con `NODE_USE_ENV_PROXY=1` (Node 22.21+/24) perché `fetch` usi il proxy.

## Cosa manca per il pagamento reale

1. Creare un prodotto "Fix Pack – €9" su Stripe e un **Payment Link** (o Checkout Session) con `success_url` che riporti a `/?session_id={CHECKOUT_SESSION_ID}`.
2. Separare l'API: `/api/scan` restituisce solo score, issues e un'anteprima; un nuovo endpoint `/api/fixpack` restituisce il fix pack completo **solo** dopo aver verificato il pagamento (`stripe.checkout.sessions.retrieve` con `payment_status === "paid"`, oppure un webhook `checkout.session.completed`).
3. Salvare il risultato della scansione tra scansione e pagamento (es. Vercel KV/Upstash, gratuiti nei piani base) o rigenerarlo dopo il pagamento.
4. Variabili `STRIPE_SECRET_KEY` e `STRIPE_WEBHOOK_SECRET`, pagine termini/privacy, ricevute e gestione rimborsi.

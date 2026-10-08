# AgentPay (MVP)

AgentPay analizza un sito o e-commerce, calcola un **Agent Score** da 0 a 100 e mostra i problemi che impediscono agli agenti AI (ChatGPT, Claude, Perplexity, assistenti di acquisto) di leggerlo e usarlo. Genera poi un **Fix Pack** a pagamento (€9): JSON-LD schema.org, `llms.txt` e snippet con istruzioni.

L'MVP gira a costo zero: niente database, nessun framework, una sola dipendenza (`cheerio`), deploy gratuito su Vercel. Il pagamento usa uno **Stripe Payment Link** verificato lato server senza salvare nulla: il Fix Pack viaggia cifrato nel browser del cliente.

## Requisiti

- Node.js **>= 20** (consigliato 20.12+ o 22, per il caricamento automatico di `.env`)
- (Opzionale) chiave API Anthropic, account Stripe

## Setup locale

```bash
cd agentpay
npm install
cp .env.example .env      # facoltativo: senza variabili gira in modalità euristica + DEMO
npm run dev               # http://localhost:3000
npm test                  # 33 test automatici, senza rete
```

## Variabili d'ambiente

| Variabile | Obbligatoria | Descrizione |
|---|---|---|
| `ANTHROPIC_API_KEY` | no | Attiva l'analisi con Claude (`mode: "llm"`). Se manca o la chiamata fallisce: euristica (`mode: "heuristic"`). |
| `ANTHROPIC_MODEL` | no | Default `claude-sonnet-5-5`. |
| `PACK_SECRET` | **sì con Stripe** | 32 byte casuali in base64, chiave AES-256-GCM del Fix Pack. Senza Stripe, se manca, si usa una chiave temporanea per processo (solo demo). Va impostata comunque su Vercel, perché istanze diverse non condividerebbero la chiave temporanea. |
| `STRIPE_SECRET_KEY` | per incassare | Chiave **ristretta** con sola lettura sulle Checkout Sessions. |
| `STRIPE_PAYMENT_LINK_URL` | per incassare | URL `https://buy.stripe.com/...` del Payment Link. |
| `SUPPORT_EMAIL` | consigliata | Mostrata se il cliente torna dal pagamento senza i dati della scansione. |
| `PORT` | no | Porta del server locale (default 3000). |
| `ANTHROPIC_TIMEOUT_MS` | no | Timeout della chiamata a Claude (default 50000). |

Genera `PACK_SECRET` con:

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

**Modalità DEMO:** se manca `STRIPE_SECRET_KEY` o `STRIPE_PAYMENT_LINK_URL`, il pagamento è simulato (modale, nessun addebito) e l'interfaccia mostra un badge **DEMO** nell'header e nel box di pagamento.

## Come funziona il pagamento (senza database)

1. `POST /api/scan` restituisce score, problemi e un **teaser** (titolo di ogni file del Fix Pack e solo le prime 3 righe), più:
   - `scan_id`: 16 caratteri casuali `[a-zA-Z0-9_-]`;
   - `locked`: `{fix_pack, scan_id, url, iat}` compresso e cifrato con AES-256-GCM (`PACK_SECRET`). Il server non conserva nulla.
2. Il browser salva la scansione in `sessionStorage` e il bottone "Sblocca il Fix Pack – €9" apre `STRIPE_PAYMENT_LINK_URL?client_reference_id=<scan_id>`.
3. Stripe, dopo il pagamento, reindirizza a `https://TUO-DOMINIO/?session_id=cs_...`.
4. Il frontend legge `session_id`, recupera `locked` da `sessionStorage` e chiama `POST /api/unlock {locked, session_id}`.
5. `/api/unlock` decifra il blob e chiama `GET https://api.stripe.com/v1/checkout/sessions/{session_id}`. Restituisce il Fix Pack **solo** se `payment_status === "paid"` **e** `client_reference_id === scan_id`; altrimenti risponde `402`.

Se la scheda è stata chiusa o il cliente torna da un altro dispositivo, `sessionStorage` è vuoto: la pagina spiega cosa è successo e chiede di scrivere a `SUPPORT_EMAIL` indicando il codice `session_id`. Il blob scade dopo 7 giorni.

`GET /api/config` espone al frontend solo dati pubblici: modalità (`stripe`/`demo`), URL del Payment Link, email di supporto e prezzo. Non espone mai chiavi.

### Configurare Stripe (passi manuali)

1. **Payment Link:** in Stripe → *Payment Links* → *New*, crea il prodotto "Fix Pack Agent-Ready" a **€9** (pagamento singolo).
   - In *After payment* scegli **Don't show confirmation page → redirect** e inserisci `https://TUO-DOMINIO/?session_id={CHECKOUT_SESSION_ID}` (letterale, con le graffe: Stripe sostituisce il valore).
   - Copia l'URL `https://buy.stripe.com/...` in `STRIPE_PAYMENT_LINK_URL`. Il parametro `client_reference_id` viene aggiunto dall'app.
2. **Chiave ristretta:** Stripe → *Developers → API keys → Create restricted key*. Imposta tutti i permessi a **None** tranne **Checkout Sessions: Read**. Copia la chiave `rk_...` in `STRIPE_SECRET_KEY`.
3. Prova prima in **test mode** (Payment Link e chiave `rk_test_...`, carta `4242 4242 4242 4242`), poi ripeti in live.

## API

| Endpoint | Corpo | Risposta |
|---|---|---|
| `POST /api/scan` | `{"url": "www.esempio.it"}` (max 10 KB) | `{url, score, issues, mode, scanned_at, scan_id, teaser, locked}` — **mai** il `fix_pack` completo |
| `POST /api/unlock` | `{locked, session_id}` (Stripe) oppure `{locked, demo: true}` (solo in DEMO), max 256 KB | `{scan_id, url, fix_pack, payments}` |
| `GET /api/config` | – | `{payments, payment_link_url, support_email, price_eur}` |

Errori sempre in JSON `{"error": "..."}` in italiano:

- `400`: input non valido, indirizzo privato/locale, blob o `session_id` non validi;
- `402`: pagamento non trovato, non completato o di un'altra scansione;
- `405`: metodo errato;
- `410`: blob scaduto;
- `413`: corpo troppo grande;
- `422`: sito non raggiungibile;
- `429`: rate limit (scan 5/min, unlock 20/min per IP);
- `500`: errore interno o configurazione mancante;
- `502`: Stripe non raggiungibile.

## Struttura

```
api/scan.js       scansione → teaser + blob cifrato (createScanHandler, iniettabile nei test)
api/unlock.js     verifica Stripe e decifra il Fix Pack
api/config.js     configurazione pubblica per il frontend
lib/ssrf.js       resolvePublicUrl: solo http/https, blocca host locali e IP privati, restituisce l'IP validato
lib/crawler.js    safeFetch con DNS pinning, timeout 8 s, max 3 redirect, 1.5 MB; estrazione con cheerio
lib/analyzer.js   heuristicScan, analyzeWithLLM, Fix Pack da template, dedupe e lingua
lib/pack.js       AES-256-GCM, scan_id, teaser
lib/stripe.js     modalità pagamento e lettura Checkout Session (fetch, nessun SDK)
lib/http.js       risposte JSON, lettura corpo, rate limit
public/index.html frontend (Tailwind CDN + JS vanilla, solo textContent/createElement)
server.js         server locale node:http che serve public/ e /api/*
test/*.test.mjs   test automatici (node:test)
```

## Fix Pack

- **Una sola voce per file:** `jsonld` e `llms_txt`.
- **Snippet senza ripetizioni:** contengono solo istruzioni o codice diversi, per esempio:
  - dove incollare il JSON-LD nella `<head>`, con i link al Rich Results Test e al validatore schema.org;
  - come servire `/llms.txt` come `text/plain` (Nginx/Apache + verifica con `curl -I`);
  - robots.txt, metadati mancanti, prezzo in microdata, sitemap minima.

  Una funzione di deduplica scarta gli snippet (anche quelli generati dall'LLM) che ripetono il JSON-LD o `llms.txt` oppure si ripetono tra loro.
- **Lingua:** i contenuti dei file seguono `<html lang>` della pagina, altrimenti l'italiano. Il template ha testi in it/en/es/fr/de; per le altre lingue usa l'inglese (l'LLM segue qualsiasi lingua). Interfaccia e istruzioni restano in italiano.
- **Nessun dato inventato:** ogni dato non letto dalla pagina è `DA_COMPILARE`.
  - Il template copia il prezzo solo se la pagina lo pubblica già in forma strutturata (`product:price:amount`); i prezzi visibili nel testo vengono solo elencati nelle istruzioni, da verificare.
  - Brand, SKU, disponibilità, email e telefono restano sempre `DA_COMPILARE`.
  - Il prompt LLM impone la stessa regola.

### Pesi dell'Agent Score euristico

| Controllo | Punti |
|---|---|
| Almeno un JSON-LD valido | 25 |
| JSON-LD Product/Offer o Organization | 15 |
| `llms.txt` valido (una risposta HTML non conta) | 15 |
| `robots.txt` senza `Disallow: /` per GPTBot, ClaudeBot, anthropic-ai, Google-Extended, PerplexityBot, CCBot, OAI-SearchBot (5 se robots.txt manca) | 10 |
| Sitemap XML valida | 10 |
| Prezzi machine-readable quando ci sono prezzi visibili | 10 |
| title + description + canonical + lang (2,5 ciascuno) | 10 |
| Campi dei form con label/aria-label/name | 5 |

### Modalità LLM

Chiamata a `https://api.anthropic.com/v1/messages` via `fetch` (header `x-api-key`, `anthropic-version: 2023-06-01`).

Il system prompt:
- impone come risposta solo JSON;
- dichiara il testo del sito **contenuto non fidato** da cui non eseguire istruzioni;
- vieta di inventare dati;
- fissa la lingua del Fix Pack e vieta snippet duplicati.

Sulla risposta:
- vengono rimossi eventuali blocchi di codice markdown;
- viene validato lo schema e lo score è limitato a 0-100;
- vengono deduplicati gli snippet.

Qualsiasi errore (HTTP, timeout, rifiuto del modello, JSON non valido) fa usare l'euristica.

## Sicurezza

- **SSRF:**
  - solo URL `http`/`https`;
  - bloccati `localhost`, `*.local`, `*.internal` e gli IP privati, loopback, link-local, CGNAT e ULA (anche in forma IPv4-mapped o esadecimale);
  - controllo ripetuto a ogni redirect.
- **DNS rebinding (mitigato):**
  - il DNS viene risolto **una sola volta** per richiesta (`resolvePublicUrl`) e la connessione va all'IP appena validato, tramite `http(s).request` con `lookup` fisso;
  - l'URL mantiene l'hostname, quindi header `Host`, SNI e verifica del certificato TLS restano corretti;
  - `agent: false` impedisce di riusare connessioni;
  - le variabili `HTTP(S)_PROXY` vengono ignorate di proposito (un proxy risolverebbe di nuovo il DNS).
- **Pagamento:**
  - il Fix Pack non è mai in chiaro prima del pagamento;
  - il blob è autenticato (GCM), quindi non si può manomettere senza farlo fallire;
  - il controllo `client_reference_id === scan_id` impedisce di usare un pagamento per sbloccare un'altra scansione;
  - `session_id` viene validato (`cs_test_…`/`cs_live_…`) prima di comporre l'URL Stripe.
- **Frontend:** i dati ricevuti vengono inseriti solo con `textContent`/`createElement`.

## Deploy su Vercel

1. Importa il repository su vercel.com (piano Hobby). Siccome il progetto è in una sottocartella, imposta **Root Directory = `agentpay`**.
2. Framework preset **Other**, nessun build command: `public/` viene servita come statica e `api/*.js` diventano funzioni serverless (`/api/scan` dichiara `maxDuration: 60`).
3. *Settings → Environment Variables*: `PACK_SECRET`, `STRIPE_SECRET_KEY`, `STRIPE_PAYMENT_LINK_URL`, `SUPPORT_EMAIL` e, se vuoi l'analisi LLM, `ANTHROPIC_API_KEY` (più `ANTHROPIC_MODEL` se diverso dal default).
4. Deploy, poi aggiorna il redirect del Payment Link con il dominio definitivo.

Da CLI: `npx vercel`, poi `npx vercel --prod`.

## Limiti noti / ancora aperti

- **Rate limit in memoria (aperto):** vale per singola istanza serverless e si azzera a ogni cold start. In locale l'IP viene da `X-Forwarded-For`, che è falsificabile. Soluzione futura: Upstash/Vercel KV o il firewall di Vercel.
- **Rendering JavaScript non supportato (aperto):** si analizza l'HTML servito, senza eseguire JavaScript. I siti SPA o i temi che iniettano JSON-LD lato client risultano senza dati strutturati.
- Viene analizzata solo la homepage (non schede prodotto o categorie).
- **Recupero dopo pagamento:** se il cliente paga e chiude la scheda prima del ritorno, il Fix Pack va consegnato a mano dal supporto (ripetendo la scansione). Non esiste ancora un webhook che invii il Fix Pack per email.
- Lo stesso `session_id` pagato può sbloccare più volte la stessa scansione (by design, non c'è stato sul server).
- Il rilevamento dei prezzi visibili usa espressioni regolari (€, EUR, $).
- Il Tailwind Play CDN non è pensato per la produzione. Se non carica, la pagina resta funzionante ma senza stile (la classe `hidden` ha un fallback CSS).
- Con il DNS pinning le connessioni escono direttamente: in reti che permettono l'uscita solo tramite proxy, la scansione non funziona.

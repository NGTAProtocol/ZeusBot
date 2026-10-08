# Studio dei riferimenti — esito reale

## Cosa era richiesto
Analizzare con Playwright almeno 8 siti premiati di settori diversi, compreso il case study Awwwards di Kode Immersive, registrando librerie, struttura, scroll, resa a 375/768/1280, peso e Lighthouse.

## Cosa è successo
La rete di questo ambiente consente l'uscita solo verso un elenco di host (GitHub, npm, nodejs.org, anthropic.com…).
**Tutti i siti premiati tentati sono bloccati** dal proxy (`ERR_TUNNEL_CONNECTION_FAILED` / `403 host_not_allowed`).
Gli errori sono registrati, sito per sito, in `references/data/*.json` (generati da `npm run study`).

| Sito tentato | Settore | Esito |
|---|---|---|
| awwwards.com/case-study-kode-immersive.html | case study (agenzia immersive) | ❌ bloccato |
| lusion.co | studio 3D/WebGL | ❌ bloccato |
| activetheory.net | agenzia creativa | ❌ bloccato |
| igloo.inc | prodotto/3D | ❌ bloccato |
| bruno-simon.com | portfolio 3D | ❌ bloccato |
| locomotive.ca | agenzia (scroll) | ❌ bloccato |
| apple.com | prodotto/retail | ❌ bloccato |
| linear.app | SaaS | ❌ bloccato |
| www.anthropic.com | AI / corporate | ✅ raggiunto, **ma degradato**: font e risorse di host terzi bloccati (rende in Times/Arial, 7 richieste) |
| nodejs.org | open source / documentazione | ✅ raggiunto |

Non ho usato servizi di scraping a pagamento (es. Firecrawl, disponibile come connettore) per aggirare il blocco: richiederebbero crediti e il brief vieta di spenderli senza conferma.

## Conseguenze (dette chiaramente)
- **Nessuna scheda di sito premiato contiene misure reali.** Le schede dei siti bloccati riportano solo l'errore.
- Le **statistiche di stack** sono calcolate sul campione effettivamente misurato (2 siti, non premiati). Sono riportate così come sono e **non sono rappresentative** dei siti premiati: vedi `stack-stats.md`.
- La **libreria dei pattern** (`patterns.md`) è scritta con parole mie da conoscenza generale del settore, **non da misure di questa sessione**. Ogni pattern è marcato così.
- Le due schede raggiungibili servono soprattutto a **tarare lo strumento di studio** (lo script funziona e produce i dati).

## Come completare lo studio
Eseguire `npm run study -- <url> …` da una macchina con accesso libero al web, oppure autorizzare l'host nelle impostazioni di rete dell'ambiente. Lo script salva in `references/data/` solo informazioni pubbliche (librerie rilevate, numero di sezioni e titoli, comportamento di scroll, peso, Lighthouse) e screenshot di analisi in `reports/reference-shots/` (non versionati, mai riusati nei siti).

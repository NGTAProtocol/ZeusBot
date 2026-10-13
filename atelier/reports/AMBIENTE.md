# §0: verifica dell'ambiente (v2)

Comandi eseguiti in questa sessione; i risultati riportati sono quelli reali.

| Risorsa | Esito | Come è stato verificato |
|---|---|---|
| Node.js | ✅ v22.22.0 | `node -v` |
| Playwright + Chromium | ✅ Playwright 1.56.1, Chromium 1194 preinstallato in `/opt/pw-browsers` | `npx playwright --version`, screenshot generati dal QA |
| Lighthouse | ✅ 13.5.0 (dipendenza di sviluppo) | `require('lighthouse/package.json')`, report in `reports/qa/*.json` |
| WebGL headless | ✅ solo **software** (SwiftShader, flag in `scripts/lib/browser.mjs`) | il QA rileva il canvas 3D attivo (`canvas1280=true` su quota-2100-a-cinematic). Nessuna GPU reale |
| ffmpeg / ffprobe | ✅ 6.1.1 | `ffmpeg -version`. Non usato: nessun asset video fornito, quindi niente VIDEO-SCROLL |
| Rete verso npm | ✅ `registry.npmjs.org` → 200 | `curl` |
| Rete verso GitHub | ✅ per git (clone delle skill riuscito); `curl https://github.com` → 400 dal proxy | clone in cartelle temporanee durante l'audit |
| Siti premiati (awwwards.com e i riferimenti) | ❌ irraggiungibili (`curl` → nessuna risposta) | vedi `references/README.md` |
| gsap.com (testo della licenza GSAP) | ❌ irraggiungibile | la licenza resta **non verificata** (`CREDITS.md`) |

**Nota sui connettori:** in questa sessione è comparso un connettore Firecrawl (scraping web). Avrebbe potuto aggirare il blocco per lo studio dei riferimenti e per il testo della licenza GSAP. **Non è stato usato:** le sue chiamate di scraping sono a pagamento, e la richiesta vieta di spendere crediti senza conferma. Con una conferma esplicita si può rifare lo studio dei riferimenti con dati veri.

# Atelier

Atelier produce **siti web statici** (Astro + Tailwind, zero CDN, deploy gratuito) a partire da un **brief JSON**. Ha tre livelli:

- **BASE:** nessun WebGL.
- **CINEMATICO:** GSAP + ScrollTrigger + Lenis, hero Three.js procedurale in un Web Worker, grana.
- **VIDEO-SCROLL:** opzionale, solo con asset forniti dal cliente.

Il controllo qualità è automatico: screenshot a 375 / 768 / 1280, Lighthouse mobile e desktop, controlli dei fallback, lint dei cliché e una rubrica di critica.

> **Esito della prova di valore e limiti:** vedi [`reports/PROVA-DI-VALORE.md`](reports/PROVA-DI-VALORE.md) e [`reports/QUALITY.md`](reports/QUALITY.md). In sintesi: i numeri sono reali; la rubrica è un'autovalutazione; lo studio dei siti premiati **non è stato possibile** (rete bloccata).

## Requisiti
- Node.js ≥ 20 (testato con 22.22).
- Per il QA: Chromium di Playwright (`npx playwright install chromium` se manca; in questo ambiente era preinstallato) e Lighthouse (dipendenza di sviluppo).

## Comandi
```bash
npm install
npm run generate -- briefs/fornace-lume.json --level cinematic   # un sito → output/fornace-lume-cinematic/
npm run generate -- briefs/fornace-lume.json --level base
npm run generate -- briefs/fornace-lume.json --baseline           # baseline di confronto (baseline/<slug>.astro)
npm run build:all                                                 # tutti i brief × BASE, CINEMATICO, BASELINE
npm run qa -- fornace-lume-cinematic --runs 3                     # screenshot + Lighthouse + fallback → reports/
node scripts/report.mjs                                           # aggrega in reports/QUALITY.md
npm run study -- https://sito-di-riferimento.example              # studio di un riferimento (solo dati pubblici)
npm test                                                          # struttura, licenze, CDN, skills.lock, build di tutti gli esempi
```

## Come si crea un sito (flusso)
1. **Brief:** scrivi `briefs/<slug>.json` con questi campi:
   - obbligatori: `slug`, `business`, `sector`, `audience`, `goal`, `tone`, `language`, `pages`, `level`;
   - opzionali: `direction`, e `facts` (dati veri forniti dal cliente: il copy non deve inventarne).
2. **Direzione artistica:** viene scelta automaticamente tra le 8 di `scripts/lib/directions.mjs` in base a settore e tono, oppure impostata nel brief.
3. **Struttura e copy:** scrivi `content/<slug>.json` seguendo la skill **`.claude/skills/atelier/SKILL.md`**. In Claude Code basta chiedere "usa la skill atelier per il brief X". Il lint (`scripts/lib/lint.mjs`) blocca:
   - cliché e testo segnaposto;
   - lingua diversa da quella del cliente;
   - copy troppo generico;
   - sezioni a "tre card".
4. **Build:** `npm run generate`. L'output in `output/<slug>-<level>/` è HTML/CSS/JS statico.
5. **QA:** `npm run qa` e critica con la rubrica, al massimo 3 iterazioni sui punti peggiori.

## Deploy gratuito
La cartella `output/<slug>-<level>/` è un sito statico autonomo, senza CDN né chiamate esterne.
- **Cloudflare Pages:** `npx wrangler pages deploy output/<slug>-cinematic`, oppure collega il repo con build command `npm run generate -- briefs/<slug>.json --level cinematic` e output directory `output/<slug>-cinematic`.
- **Vercel:** stessa build command, output directory come sopra, framework "Other".
- **GitHub Pages:** pubblica la cartella di output (es. con l'action `upload-pages-artifact`).
  - Se il sito sta in una sottocartella, imposta `ATELIER_BASE=/nome-repo/` prima della build.
  - Gli URL interni usano `import.meta.env.BASE_URL`, ma i link dentro il copy (es. `"href": "contatti"`) devono essere relativi.
- Imposta `meta.url` in `content/<slug>.json` con il dominio reale (serve a canonical e Open Graph).

## Struttura
```
.claude/skills/atelier/SKILL.md   skill: principi, 8 direzioni, pattern, lista nera, copy, schema contenuti, rubrica
.claude/skills/*                  skill di terzi che hanno passato l'audit (vedi skills.lock, audit-skill.md)
briefs/ content/ baseline/        3 attività fittizie: brief, contenuti Atelier, baseline scritte direttamente
engine/                           motore Astro condiviso (componenti, CSS, script client, worker 3D)
engine/baseline-src/              ingresso separato per le baseline (nessuno stile Atelier)
scripts/generate.mjs              brief → direzione → contenuti → build
scripts/qa.mjs                    screenshot, Lighthouse, fallback, controlli
scripts/study-reference.mjs       studio di un sito di riferimento (dati pubblici)
scripts/lib/                      direzioni, lint, Lighthouse, browser
references/                       studio dei riferimenti (esito reale), libreria di pattern, statistiche di stack
reports/                          QA (json), screenshot, QUALITY.md, PROVA-DI-VALORE.md, rubric.json
tests/                            npm test
CREDITS.md                        licenze di font, librerie, asset (nessuna immagine o modello di terzi)
```

## Livelli e fallback
| Livello | Cosa include | Fallback |
|---|---|---|
| BASE | HTML/CSS, poster SVG procedurale, comparse con IntersectionObserver, menu mobile accessibile | contenuto sempre visibile senza JS e con reduced-motion |
| CINEMATICO | Lenis (solo con puntatore fine), GSAP/ScrollTrigger (comparse, scrub dei capitoli, transizione di tono, testo reattivo al cursore), hero Three.js con shader procedurali in **Web Worker + OffscreenCanvas**, grana, audio opzionale spento | WebGL assente → poster SVG; `deviceMemory` < 4 o `hardwareConcurrency` < 4 → poster; Save-Data o reduced-motion → si comporta come il BASE; GSAP non caricabile → contenuto visibile; nessun OffscreenCanvas → 3D nel thread principale |
| VIDEO-SCROLL | hero con video o frame legati allo scroll | **non implementato senza asset:** la pipeline rifiuta di partire. Servono media forniti dal cliente (o generati a pagamento solo previa conferma esplicita della spesa) |

**Scelta di progetto da conoscere:** nel CINEMATICO il 3D parte **alla prima interazione** (mouse, scroll, tocco o tastiera). Fino ad allora si vede il poster SVG con la stessa palette.
- Lighthouse non interagisce, quindi misura la pagina prima del 3D.
- Per trasparenza il QA misura anche il costo con il 3D forzato all'avvio (`?force3d`): vedi `reports/QUALITY.md`.

**Mobile curato, non solo ridimensionato:**
- lead dedicato più corto;
- arte nella fascia alta con dissolvenza prima del titolo;
- barra CTA fissa dopo l'hero;
- dati in fila scorrevole;
- menu a pagina intera con focus trap ed Esc;
- bersagli tattili ≥ 44 px;
- niente Lenis né cursore reattivo su touch.

## Licenze
- **Codice di Atelier:** scritto per questo progetto.
- **Font:** tutti OFL-1.1, serviti in locale.
- **Librerie:** three e lenis sono MIT.
- **GSAP:** "Standard No-Charge License", **testo non verificabile da questo ambiente**. Va letto prima di vendere il servizio: vedi `CREDITS.md`.
- **Skill di terzi:** vedi `skills.lock` e `audit-skill.md`.

## Limiti noti
- **Studio dei riferimenti non eseguito sui siti premiati:** la rete dell'ambiente li blocca tutti. La libreria dei pattern è scritta da conoscenza generale ed è dichiarata come tale (`references/`).
- **WebGL misurato solo in software (SwiftShader):** su GPU reali creazione del contesto e compilazione degli shader sono molto più rapide; l'aspetto visivo dovrebbe essere identico.
- **Nessun test su dispositivi reali** (iPhone, Android di fascia bassa) né su Safari o Firefox.
- **Rubrica autovalutata:** l'ha compilata lo stesso modello che ha generato i siti. Non sostituisce il giudizio di un designer o di utenti.
- **Copy:** lo scrive l'agente seguendo la skill (nessuna chiamata a un LLM dentro gli script). Senza un agente, la pipeline impagina contenuti già scritti.
- **Un solo template di pagina con 7 archetipi di layout:** la varietà fra siti viene da direzione, tipografia, motivo 3D e copy, non da layout radicalmente diversi.
- **VIDEO-SCROLL:** solo predisposto (rifiuto esplicito senza asset), non implementato end-to-end.

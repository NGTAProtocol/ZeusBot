# Atelier (v2)

Atelier produce **siti web statici** (Astro + Tailwind, zero CDN, deploy gratuito) a partire da un **brief JSON**.

Prima del codice c'è sempre la **fase Bibbia**: concept, personalità, firma (`bibbia/BIBBIA.md`). Poi vengono struttura e copy, poi la build, poi il controllo qualità automatico:
- screenshot a 375 / 768 / 1280;
- Lighthouse mobile e desktop;
- controlli dei fallback;
- lint di cliché e link finti;
- rubrica 1-10.

I livelli sono tre:
- **BASE:** nessun WebGL. La firma si muove con le animazioni CSS legate allo scroll.
- **CINEMATICO:** GSAP + ScrollTrigger + Lenis pilotano la firma, con la grana. Three.js **solo se la firma è 3D** (Bibbia §14.3).
- **VIDEO-SCROLL:** solo con asset forniti dal cliente.

> **Esito della prova di valore:** [`reports/PROVA-DI-VALORE.md`](reports/PROVA-DI-VALORE.md). **Misure:** [`reports/QUALITY.md`](reports/QUALITY.md). Lo studio dei siti premiati non è stato possibile per il blocco di rete (`references/README.md`); la rubrica è un'autovalutazione.

## Requisiti
- Node.js ≥ 20 (testato con 22).
- Per il QA: Chromium di Playwright e Lighthouse (dipendenze di sviluppo).

## Comandi
```bash
npm install
npm run generate -- briefs/fornace-lume.json --config b --level cinematic   # → output/fornace-lume-b-cinematic/
npm run generate -- briefs/fornace-lume.json --config baseline --level base  # baseline senza skill né Bibbia
npm run build:all                    # 3 brief × 4 configurazioni × 2 livelli = 24 siti
npm run qa -- fornace-lume-b-cinematic --runs 3
node scripts/report.mjs              # reports/QUALITY.md + reports/metrics.json
npm test                             # struttura, Bibbia, lint, licenze, CDN, skills.lock, build dei 24 siti
```

## Flusso per un nuovo cliente
1. **Brief** → `briefs/<slug>.json`. I `facts` sono gli unici dati che il sito può usare.
2. **Fase Bibbia** → `bibbia/<slug>-<config>.json`: concept in una frase, 3 aggettivi + cosa NON è, firma (`css` o `3d` con `why_3d`), palette con la provenienza di ogni colore, font OFL, token, layout, `unknowns`. Viene validata da `scripts/lib/bibbia.mjs` (contrasto AA, font installati e open, al massimo 2 famiglie…).
3. **Struttura e copy** → `content/<slug>-<config>.json`, seguendo `.claude/skills/atelier/SKILL.md` e un archetipo di `references/archetipi.md`. Il lint (`scripts/lib/lint.mjs`) blocca:
   - cliché;
   - link finti (ogni `href` deve portare a una sezione o a una pagina esistente, oppure a un'email o a un telefono del brief);
   - CTA con etichette diverse per la stessa azione;
   - le regole della configurazione C.
4. **Build:** `npm run generate`. L'output è statico e include i dati strutturati `LocalBusiness`, generati dai contatti veri.
5. **QA + rubrica:** al massimo 3 iterazioni sui punti peggiori. Non si dichiara successo se una soglia manca.

## Configurazioni (per la prova di valore)
| config | Skill | Note |
|---|---|---|
| `baseline` | nessuna, nessuna Bibbia | `baseline/<slug>-base.astro` e `-cinematic.astro`, scritte come le scriverebbe un generatore generico |
| `a` | frontend-design | + metodo Atelier/Bibbia |
| `b` | frontend-design + impeccable | strategia di colore, niente font "default", superfici del browser tematizzate |
| `c` | frontend-design + taste-skill + emil-design-eng/emil-animate | sans display, un accento, hero ≤ 2 righe, modo scuro, pressione sui bottoni |

## Deploy gratuito
`output/<slug>-<config>-<level>/` è un sito statico autonomo, senza CDN né chiamate esterne.
- **Cloudflare Pages:** `npx wrangler pages deploy output/<id>`.
- **Vercel:** framework "Other", output directory `output/<id>`.
- **GitHub Pages:** carica la cartella. Se il sito sta in una sottocartella, imposta `ATELIER_BASE=/repo/` prima della build.
- Imposta `meta.url` sul dominio reale (serve a canonical, Open Graph e JSON-LD).

## Struttura
```
bibbia/BIBBIA.md                 metodo obbligatorio (concept, personalità, firma, regole, checklist Q1-Q6)
bibbia/<slug>-<config>.json      fase Bibbia di ogni sito di esempio
.claude/skills/atelier/SKILL.md  skill operativa (riassume Bibbia, pattern, archetipi, direzioni, lista nera)
.claude/skills/*                 skill di terzi che hanno passato l'audit (skills.lock, audit-skill.md)
briefs/ content/ baseline/       3 attività fittizie
engine/                          motore Astro (componenti, firme SVG, script client, worker 3D)
engine/baseline-src/             ingresso separato per le baseline (nessuno stile Atelier)
scripts/                         generate, qa, report, build-all, study-reference; lib/ (bibbia, lint, slop, lighthouse…)
references/                      esito dello studio, pattern, archetipi, statistiche di stack
reports/                         QUALITY.md, PROVA-DI-VALORE.md, metrics.json, rubric.json, qa/*.json, shots/*.jpg
tests/                           npm test
CREDITS.md                       licenze di font, librerie, asset
```

## Fallback
| Livello | Fallback |
|---|---|
| BASE | contenuto sempre visibile senza JS; reduced-motion = firma ferma; senza `animation-timeline` la firma resta statica |
| CINEMATICO | GSAP non caricabile o reduced-motion o Save-Data → si comporta come il BASE. Con firma 3D: WebGL assente o dispositivo debole → firma CSS di ripiego |
| VIDEO-SCROLL | la pipeline rifiuta di partire senza asset |

Il 3D (dove c'è) parte al primo gesto, in un Worker, e **si ferma quando l'utente è fermo**: ~4 s dopo l'avvio e 2,5 s dopo ogni gesto. Nessun loop infinito.

## Licenze
- **Codice:** scritto per Atelier.
- **Font:** OFL-1.1, serviti in locale.
- **Librerie:** three e lenis sono MIT.
- **GSAP:** "Standard No-Charge License", **testo non verificabile da questo ambiente**; va letto prima di vendere il servizio (vedi `CREDITS.md`).

## Limiti noti
- **Studio dei riferimenti** (siti premiati) non eseguito: la rete li blocca.
- **WebGL** misurato solo in software (SwiftShader). Nessun test su dispositivi reali, Safari o Firefox.
- **Rubrica autovalutata** dallo stesso modello che ha scritto i siti.
- **Contaminazione del confronto:** anche baseline, A, B e C sono state scritte dallo stesso modello, nella stessa sessione.
- **Firme parametriche:** 4 firme CSS e 5 scene 3D procedurali, parametrizzate dalla Bibbia. Non sono disegnate da zero per ogni cliente; due siti possono condividere lo stesso tipo di firma.
- **Il copy lo scrive l'agente:** gli script non chiamano nessun LLM.
- **VIDEO-SCROLL:** non implementato end-to-end.

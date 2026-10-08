---
name: atelier
description: Produce siti web statici di livello alto (Astro + Tailwind, livelli BASE / CINEMATICO / VIDEO-SCROLL) a partire da un brief JSON, con direzione artistica, copy specifico nella lingua del cliente e controllo qualità automatico (screenshot, Lighthouse, rubrica). Usala quando bisogna creare o rifare un sito vetrina/landing per un'attività reale a partire da un brief.
---

# Atelier

Trasforma un brief in un sito statico, deployabile gratis, che non sembri un template.
La pipeline è in `scripts/`; questa skill dice **come pensare** prima di lanciarla.

## Flusso

1. **Brief** → `briefs/<slug>.json`. Campi obbligatori: `slug`, `business`, `sector`, `audience`, `goal`, `tone`, `language`, `pages` (deve includere `home`), `level` (`base` | `cinematic` | `video-scroll`). Opzionale: `direction` (id di una delle 8 direzioni).
2. **Direzione artistica** → `scripts/lib/directions.mjs` sceglie per affinità con settore e tono, oppure usa `direction`. Leggi la direzione scelta (palette, font, movimento, archetipo, tono) **prima** di scrivere il copy.
3. **Struttura e copy** → scrivi `content/<slug>.json` (schema sotto) seguendo le regole di questa skill.
4. **Build** → `node scripts/generate.mjs briefs/<slug>.json --level base|cinematic`.
5. **Qualità** → `node scripts/qa.mjs <slug>-<level>`: screenshot 375/768/1280, Lighthouse mobile e desktop, controlli automatici. Poi la **critica con rubrica** (sotto), con al massimo 3 iterazioni sui punti peggiori.
6. Non dichiarare successo se le soglie non sono raggiunte: riporta le cause e cosa servirebbe.

## Principi di design (non negoziabili)

- **Gerarchia tipografica:** un solo h1. Scala modulare della direzione (`type.scale`). Il titolo hero è il "momento firma" del livello BASE.
- **Ritmo:** padding di sezione dalla direzione (`space.section`). Si alternano sezioni dense (dati, offerta) e sezioni ariose (capitoli, citazione). Non mettere mai due sezioni dello stesso tipo una dopo l'altra.
- **Griglia:** contenitore `.wrap` (max 88rem) con gutter fluido. Righe di testo ≤ `measure` (circa 60-75 caratteri).
- **Contrasto AA:** tutte le palette sono verificate nei test (testo ≥ 4,5:1 su fondo e superficie). `accent2` è solo decorativo.
- **Vuoto:** spendi l'audacia in un solo punto. Il resto è calmo.
- **Al massimo 2 famiglie di font** (display + testo), entrambe con licenza OFL, servite in locale con @fontsource. Mai CDN.

## Le 8 direzioni

| id | Nome | Per | Layout | Motivo 3D | Movimento |
|---|---|---|---|---|---|
| argilla | Argilla notturna | artigianato, materia | editoriale asimmetrico | blob smaltato | maschera che sale, lenta |
| quota | Quota | montagna, outdoor | pannelli a tutta larghezza | terreno a curve di livello | curve che scorrono, numeri da altimetro |
| cifra | Cifra | tecnologia, B2B | indice laterale fisso | reticolo di punti | decifrazione, punti che si accendono |
| salmastro | Salmastro | ristorazione, mare | pannelli | nastri ondulati | deriva lenta |
| manifesto | Manifesto | moda, creativi | tipografia enorme | blob cromato | tagli netti |
| archivio | Archivio | legale, cultura | catalogo | fogli sovrapposti | voltare pagina |
| serra | Serra | benessere, botanica | monolite centrale | fillotassi | crescita, respiro |
| officina | Officina | industria, ingegneria | griglia tecnica | anelli | tracciatura lineare |

Dettagli completi (hex, font, spaziature, tono) in `scripts/lib/directions.mjs`.

## Pattern disponibili (da `references/patterns.md`)

- **Scroll narrativo** (sezione `chapter`): titolo fermo (sticky) e testo che si accende progressivamente nel CINEMATICO. Usalo per la storia dell'attività, non per elenchi.
- **Testo che reagisce al cursore:** il titolo hero nel CINEMATICO, solo con puntatore fine.
- **Menu che si trasforma:** barra estesa → capsula compatta dopo l'hero. Su mobile c'è un menu a pagina intera accessibile.
- **Grana + distorsione leggera:** overlay di grana (statico nel BASE, animato nel CINEMATICO) e grana nello shader 3D per fondere 3D e fondi piatti.
- **Transizione di tono:** una sezione con `"tone": "invert"` inverte i colori (nel CINEMATICO con transizione guidata dallo scroll).
- **Audio opzionale:** drone procedurale WebAudio, **spento di default**, interruttore `aria-pressed`, nascosto su mobile.
- **Contatori:** solo per dati veri e verificabili del brief, mai numeri inventati per riempire.

## Livelli

- **BASE:** nessun WebGL e nessuna libreria di animazione. Hero con poster SVG procedurale (stessa palette e motivo della direzione), comparse via IntersectionObserver. Obiettivo Lighthouse: performance ≥ 90; accessibilità e SEO ≥ 95.
- **CINEMATICO:** GSAP + ScrollTrigger + Lenis (solo con puntatore fine) + hero Three.js con geometrie e shader procedurali + grana. Tutto caricato **dopo** il primo rendering. Obiettivo Lighthouse: performance ≥ 75 mobile e ≥ 85 desktop; accessibilità e SEO ≥ 95.
  - Fallback: WebGL assente, dispositivo debole (`deviceMemory` < 4 o `hardwareConcurrency` < 4) → poster SVG; Save-Data o `prefers-reduced-motion` → si comporta come il BASE.
  - Il 3D gira in un Web Worker (OffscreenCanvas) e parte **alla prima interazione** (mouse, scroll, tocco, tastiera) su tutti i dispositivi. Fino ad allora resta il poster SVG. `?force3d` lo avvia subito, per misurarne il costo nel QA.
- **VIDEO-SCROLL (opzionale):** hero con video o sequenza di frame legata allo scroll. **Solo con asset forniti dal cliente**: la pipeline rifiuta di partire senza. Non generare media a pagamento senza conferma esplicita della spesa.

## Versione mobile curata (non solo ridimensionata)

- Lead dell'hero più corto e dedicato (`lead_short`, ≤ 120 caratteri).
- Hero più basso, con l'arte nella metà superiore.
- Barra CTA fissa in basso dopo l'hero.
- Dati in fila orizzontale scorrevole (scroll-snap).
- Menu a pagina intera con focus trap ed Esc.
- Bersagli tattili ≥ 44 px.

## Lista nera dei cliché (il lint li blocca dove possibile)

- Gradiente viola/indaco generico su fondo scuro o bianco.
- Tre card con icone uguali (le sezioni `cards`, `features`, `icons` non esistono; un'offerta con tre voci brevi viene segnalata).
- Hero senza personalità: "Benvenuti", stock anonime, slogan intercambiabili.
- Immagini stock anonime: Atelier usa solo grafica procedurale originale o asset del cliente con licenza registrata in `CREDITS.md`.
- Lorem ipsum o testo segnaposto.
- Frasi vuote: "soluzioni innovative", "a 360 gradi", "eccellenza", "leader del settore", "la nostra passione", "scopri di più", "clicca qui".
- Tic grafici da sito generato: eyebrow in MAIUSCOLO sopra ogni titolo, "A · B · C", "→" appesa ai bottoni, numerazione 01/02/03 su contenuti che non sono una sequenza. La numerazione è ammessa solo nella sezione `process`, che è una sequenza vera.
- Crema #F4F1EA + serif + terracotta; nero + verde acido; kit SaaS a card con ombra grigia uguale ovunque.

## Copy

- **Nella lingua del cliente** (`brief.language`); `meta.lang` deve coincidere.
- **Specifico dell'attività:** nomi di luoghi, materiali, tempi, prezzi o condizioni reali del brief. Se un dato non c'è nel brief, **non inventarlo**: scrivi in modo che non serva, oppure segnalo come "da confermare".
- Voce attiva; i bottoni dicono cosa succede ("Chiedi un preventivo", non "Invia").
- Ogni elemento di testo fa un solo lavoro. Niente etichette decorative.
- Il nome dell'attività compare almeno 3 volte (il lint lo verifica).
- `meta.description`: 70-165 caratteri. Titolo hero ≤ 70 caratteri, diviso in righe sensate (`title_lines`).

## Schema di `content/<slug>.json`

```jsonc
{
  "meta": { "title": "…", "description": "…", "lang": "it", "url": "https://dominio.it" },
  "brand": { "name": "…" },
  "nav": [{ "label": "…", "href": "#ancora" }],
  "cta": { "label": "…", "href": "contatti", "mobile_hint": "frase breve per la barra mobile" },
  "pages": {
    "home": {
      "hero": { "title_lines": ["…", "…"], "lead": "…", "lead_short": "…", "cta": { "label": "…", "href": "…" }, "secondary": { "label": "…", "href": "#…" }, "meta": ["…", "…"] },
      "sections": [
        { "type": "chapter", "id": "…", "index_label": "…", "title_lines": ["…"], "body": ["…"], "aside": "…", "tone": "invert" },
        { "type": "facts", "title": "…", "items": [{ "value": "12", "unit": "km", "label": "…" }] },
        { "type": "offer", "title": "…", "intro": "…", "items": [{ "name": "…", "detail": "…", "meta": "…" }] },
        { "type": "process", "title": "…", "steps": [{ "name": "…", "detail": "…" }] },
        { "type": "quote", "text": "…", "cite": "…" },
        { "type": "marquee", "words": ["…"] },
        { "type": "faq", "title": "…", "items": [{ "q": "…", "a": "…" }] },
        { "type": "contact", "title": "…", "body": ["…"], "lines": [{ "label": "…", "value": "…", "href": "…" }], "cta": { "label": "…", "href": "…" } }
      ]
    },
    "contatti": { "meta_title": "…", "meta_description": "…", "title_lines": ["…"], "intro": "…", "sections": [] }
  },
  "footer": { "closing": "…", "address": "…", "email": "…", "phone": "…", "hours": ["…"], "legal": "…" }
}
```

## Critica con rubrica (1-10)

Valuta su screenshot reali a 375 / 768 / 1280, non sul codice:

1. **Gerarchia:** si capisce in 3 secondi chi sei, cosa offri e cosa fare?
2. **Contrasto:** testo leggibile su ogni fondo, anche sopra il 3D e la grana.
3. **Spazio:** ritmo verticale, respiro, nessun affollamento.
4. **Coerenza:** palette, font e movimento appartengono alla stessa direzione.
5. **Originalità ("effetto template"):** si distingue da un sito generico dello stesso settore?
6. **Movimento:** ha uno scopo, non distrae, rispetta `reduced-motion`.
7. **Mobile:** è progettato per il telefono, non solo ridimensionato.

Ripeti per al massimo 3 iterazioni sui 2 punteggi peggiori. Registra i punteggi e le modifiche in `reports/`.
È una **autovalutazione**: dichiaralo sempre quando riporti i risultati.

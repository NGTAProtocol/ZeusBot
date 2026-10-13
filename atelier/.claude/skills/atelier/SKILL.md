---
name: atelier
description: Produce siti web statici di livello alto (Astro + Tailwind, livelli BASE / CINEMATICO / VIDEO-SCROLL) a partire da un brief JSON. Prima la fase Bibbia (concept, personalità, firma), poi struttura e copy nella lingua del cliente, poi build e controllo qualità automatico (screenshot, Lighthouse, rubrica Q1-Q6). Usala quando bisogna creare o rifare un sito vetrina o una landing per un'attività a partire da un brief.
---

# Atelier

Trasforma un brief in un sito statico, pubblicabile gratis, che non sembri un template.
Il metodo completo è in `bibbia/BIBBIA.md`: questa skill ne è il riassunto operativo. In caso di dubbio vince la Bibbia.

## Flusso

1. **Brief** → `briefs/<slug>.json`. Campi: `slug`, `business`, `sector`, `audience`, `goal`, `tone`, `language`, `pages` (con `home`), `level`, `facts` (gli unici dati che si possono usare).
2. **Fase Bibbia, prima del codice** → `bibbia/<slug>-<config>.json`, validato da `scripts/lib/bibbia.mjs`:
   - `concept`: la tensione narrativa in **una frase**: un conflitto dell'attività, non un tema visivo;
   - `personality`: **3 aggettivi** verificabili guardando la pagina, più `not` (cosa NON è);
   - `signature`: l'elemento memorabile e non trasferibile, con `kind` `css` (predefinito) o `3d`. Il 3D richiede `why_3d` e una firma CSS di ripiego (`fallback_id`);
   - `tokens`: palette nata dal concept, con `palette_source` (da dove viene ogni colore) e `color_strategy`; font OFL; scala; spazi su base 4 px; movimento;
   - `layout`, `features`, `unknowns` (i dati mancanti da chiedere al cliente), `skills_used`.
3. **Struttura e copy** → `content/<slug>-<config>.json` (schema sotto), seguendo un archetipo di `references/archetipi.md`.
4. **Build** → `node scripts/generate.mjs briefs/<slug>.json --config a|b|c --level base|cinematic`. La build si ferma se la Bibbia non è valida, se il contrasto non è AA, se un font non è open, se il lint trova cliché o **link finti**.
5. **Qualità** → `node scripts/qa.mjs <slug>-<config>-<level>`: screenshot a 375/768/1280, Lighthouse mobile e desktop, controlli e fallback. Poi la rubrica (sotto), con **al massimo 3 iterazioni** sui punti peggiori.
6. **Non dichiarare successo** se una soglia manca: riporta il numero, la causa e cosa servirebbe.

## Configurazioni (servono a confrontare le skill)

| config | Skill in uso oltre ad Atelier | Cosa cambia nel metodo |
|---|---|---|
| `a` | frontend-design | Direzione estetica netta, font con carattere, un elemento memorabile |
| `b` | + impeccable | Strategia di colore scelta prima dei colori; niente font "default da addestramento"; superfici del browser tematizzate; un solo momento di movimento d'autore |
| `c` | + taste-skill + emil-design-eng/emil-animate | Sans display, palette fuori dalla famiglia beige/ottone, un solo accento, hero ≤ 2 righe con sottotesto ≤ 20 parole e una CTA, modo chiaro e scuro; ease-out deciso, UI < 300 ms, pressione `scale(.97)` |
| `baseline` | nessuna | Sito scritto senza skill né Bibbia (`baseline/<slug>-<level>.astro`), per il confronto |

## Principi (dalla Bibbia, non negoziabili)

- **Il contenuto comanda la forma.** Un'idea per sezione; ogni testo si può tagliare del 30%.
- **Token in `:root`**, spaziatura su base 4 px, **al massimo 2 famiglie di font**, righe di 45-65 caratteri.
- **Palette e font nascono dal concept**, dal mondo materiale del cliente; nessuna palette fissa.
- **Movimento:**
  - solo ciò che ha un referente fisico o guida lo sguardo;
  - durate di 150-400 ms per le micro-interazioni e fino a ~4 s per le sequenze;
  - parte da un gesto dell'utente; nessun loop infinito;
  - **solo `transform` e `opacity`**; `prefers-reduced-motion` = contenuto fermo.
- **Contenuto in HTML** che funziona senza JS. **Accessibilità** AA, focus visibile, bersagli ≥ 44 px.
- **Mostra, non dichiarare:** ogni aggettivo di sé diventa un fatto, un tempo, un numero.
- **Contenuto vero:** solo `facts`; ciò che manca è UNKNOWN (va in `unknowns`), **mai inventato**. **Mai link finti.**
- **3D solo quando È la firma** (§14.3). Altrimenti vince il CSS: il CINEMATICO usa GSAP + Lenis per la firma e non carica Three.js.

## Firme disponibili nel motore

Le firme sono parametriche (`signature.params`), non scritte da zero per ogni cliente. È un limite, ed è dichiarato.

| id | tipo | Cosa fa | Adatta a |
|---|---|---|---|
| `drip` | css | Fascia di colore che cola in gocce di lunghezza diversa con lo scroll | materia, liquidi, smalti |
| `layers` | css | Strati sovrapposti che si separano con lo scroll | stratificazioni: smalto, neve, terreno, documenti |
| `contours` | css | Isoipse che salgono a velocità diverse | quota, territorio, progressione |
| `lattice` | css | Reticolo che da disordinato si allinea (scroll) e si calma sotto il puntatore | ordine, controllo, reti |
| `blob`, `terrain`, `points`, `ribbons`, `rings` | 3d | Scene Three.js procedurali in un Web Worker, che si fermano quando l'utente è fermo | solo se `why_3d` regge |

La sezione `signature` del contenuto ripresenta la firma a metà pagina, con la didascalia che spiega il concept.

## Pattern (da `references/patterns.md`)

- **Scroll narrativo** (`chapter`): titolo fermo, testo che si accende man mano che si legge.
- **Menu che si trasforma**: la barra diventa una capsula dopo l'hero (solo opacity/transform). Su mobile c'è un menu a pagina intera.
- **Nastro di parole** (`marquee`): si sposta solo con lo scroll.
- **Contatori**: solo dati veri; il valore finale è già nell'HTML.
- **Sezioni a colori invertiti** (`tone: "invert"`): statiche, senza transizione di colore.
- **Grana statica**: c'è sempre nel CINEMATICO, nel BASE solo con `features.grain`.

## Archetipi di pagina (da `references/archetipi.md`)

Struttura della landing: promessa → prova → spiegazione (dove vive il concept) → offerta → condizioni e **prezzi** → domande → invito finale.
- **A. Servizio su commissione:** artigiani, studi.
- **B. Esperienza prenotabile:** corsi, soggiorni.
- **C. B2B a rischio percepito:** sicurezza, legale.

Una sezione si toglie solo se il brief non ha contenuto vero per riempirla. Un prezzo sconosciuto si scrive "su preventivo".

## Le 8 direzioni: punti di partenza, non palette

Servono per il ritmo, il movimento e l'archetipo. **Palette e font si decidono nella fase Bibbia.**

| id | Ritmo e archetipo | Movimento tipico |
|---|---|---|
| argilla | editoriale asimmetrico | maschera che sale, lenta |
| quota | pannelli, dati tecnici | curve che salgono, numeri |
| cifra | indice laterale fisso | allineamento, ordine |
| salmastro | pannelli ariosi | deriva lenta |
| manifesto | tipografia enorme | tagli netti |
| archivio | catalogo | voltare pagina |
| serra | monolite centrale | crescita |
| officina | griglia tecnica (blueprint) | tracciatura lineare |

I layout del motore sono: `editorial`, `panels`, `index`, `manifesto`, `catalogue`, `monolith`, `blueprint`.

## Livelli

- **BASE:** nessun WebGL e nessuna libreria di animazione. La firma si muove con le animazioni CSS legate allo scroll (`animation-timeline`), dove il browser le supporta; altrimenti resta ferma. Budget: JS ≤ 10 KB gzip, performance ≥ 90.
- **CINEMATICO:** GSAP + ScrollTrigger + Lenis (solo con puntatore fine) pilotano la firma; grana statica. Three.js solo con firma 3D, caricato al primo gesto, in un Worker. Budget: performance ≥ 75 mobile e ≥ 85 desktop.
  - Ripieghi: WebGL assente o dispositivo debole → firma CSS; Save-Data o reduced-motion → BASE.
- **VIDEO-SCROLL:** solo con asset forniti dal cliente, oppure dopo una conferma esplicita della spesa. La pipeline rifiuta di partire senza.
- Per tutti i livelli: accessibilità e SEO ≥ 95.

## Mobile curato

- Lead più corto (`lead_short`; in config C il lead è già ≤ 20 parole).
- CTA nel primo schermo e barra CTA fissa dopo l'hero.
- Dati in fila orizzontale con scroll-snap.
- Menu a pagina intera con focus trap ed Esc.
- Niente scorrimento fluido simulato su touch.

## Lista nera (il lint blocca dove possibile)

- **Colore e superfici:** gradiente viola generico; testo in gradiente; beige/crema + ottone + serif come scelta di default.
- **Componenti:** tre card con icone uguali; emoji come icone; immagini stock anonime.
- **Testo:** lorem ipsum; hero senza personalità ("Benvenuti", "Soluzioni innovative"); frasi vuote ("a 360 gradi", "eccellenza", "la nostra passione", "scopri di più").
- **Tic tipografici:** eyebrow in maiuscolo sopra ogni titolo; "→" appesa ai bottoni; "A · B · C"; numerazione 01/02/03 su contenuti che non sono una sequenza.
- **CTA:** azioni duplicate con etichette diverse.
- **Movimento:** loop infiniti, cursori personalizzati, preloader.

## Copy

- **Nella lingua del cliente** (`brief.language`, `meta.lang` coincide).
- Specifico: luoghi, materiali, tempi, prezzi del brief; il nome dell'attività compare almeno 3 volte.
- I bottoni dicono l'azione reale. **Una sola azione principale, con un'etichetta sola ovunque.**
- `meta.description` di 70-165 caratteri; titolo hero ≤ 70 caratteri.

## Schema di `content/<slug>-<config>.json`

```jsonc
{
  "meta": { "title": "…", "description": "…", "lang": "it", "url": "https://dominio" },
  "brand": { "name": "…" },
  "nav": [{ "label": "…", "href": "#id-sezione" }],
  "cta": { "label": "…", "href": "contatti", "mobile_hint": "…" },
  "pages": {
    "home": {
      "hero": { "title_lines": ["…"], "lead": "…", "lead_short": "…", "cta": { "label": "(= cta.label)", "href": "…" }, "secondary": {}, "meta": ["…"] },
      "sections": [
        { "type": "chapter", "id": "…", "index_label": "…", "title_lines": ["…"], "body": ["…"], "aside": "…", "tone": "invert" },
        { "type": "signature", "id": "…", "title_lines": ["…"], "caption": "…" },
        { "type": "facts", "id": "…", "title": "…", "items": [{ "value": "3", "unit": "…", "label": "…" }] },
        { "type": "offer", "id": "…", "title": "…", "items": [{ "name": "…", "detail": "…", "meta": "…" }] },
        { "type": "process", "id": "…", "title": "…", "steps": [{ "name": "…", "detail": "…" }] },
        { "type": "prices", "id": "…", "title": "…", "items": [{ "item": "…", "value": "180 € | Su preventivo", "note": "…" }] },
        { "type": "faq", "id": "…", "title": "…", "items": [{ "q": "…", "a": "…" }] },
        { "type": "contact", "id": "…", "title": "…", "body": ["…"], "lines": [{ "label": "…", "value": "…", "href": "mailto:|tel: dal brief" }], "cta": {} }
      ]
    },
    "contatti": { "meta_title": "…", "meta_description": "…", "title_lines": ["…"], "intro": "…", "sections": [] }
  },
  "footer": { "closing": "…", "address": "…", "email": "…", "phone": "…", "hours": ["…"], "legal": "…" }
}
```

## Rubrica 1-10 (su screenshot reali a 375/768/1280)

- **Checklist Q1-Q6 della Bibbia:**
  - **Q1** concept in una frase;
  - **Q2** personalità distinta;
  - **Q3** firma memorabile e non trasferibile;
  - **Q4** contenuto vero;
  - **Q5** zero slop;
  - **Q6** cosa ricorderà il visitatore.
- **Altri criteri:** gerarchia, contrasto, spazio, movimento, mobile, effetto template (10 = per niente template).

Si itera al massimo 3 volte sui due punteggi peggiori. È un'**autovalutazione** del modello che ha scritto il sito: dichiaralo sempre.

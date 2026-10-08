# Prova di valore: Atelier contro baseline

**Domanda:** a parità di brief, Atelier produce un sito visibilmente migliore di un sito generato da un'AI "senza metodo"?

## Impostazione
- **3 attività fittizie in 3 settori:** Fornace Lume (ceramica artigianale, Faenza), Quota 2100 (scialpinismo e rifugio, Val Masino), Nodo (sicurezza informatica B2B, Treviso). I brief sono in `briefs/` e includono i dati "forniti dal cliente" (`facts`).
- **Per ogni attività, tre varianti:**
  - **BASELINE:** stesso brief e stesso stack (Astro + Tailwind), scritta direttamente in una sola passata, in buona fede, senza skill, senza ciclo di qualità e senza guardare gli screenshot. Font di sistema.
  - **ATELIER BASE:** skill + direzione artistica + lint + 2 iterazioni di QA, senza WebGL.
  - **ATELIER CINEMATICO:** come il BASE, più GSAP/ScrollTrigger, Lenis, hero Three.js procedurale nel Worker, grana e audio opzionale.
- **Strumenti di misura:** Lighthouse 13.5 (mediana di 3 run) e controlli Playwright; tabelle complete in `QUALITY.md`. Rubrica 1-10 su 7 criteri, sugli screenshot reali: `rubric.json` e `QUALITY.md`.

### Limiti dell'impostazione (da leggere prima dei numeri)
1. **Stesso autore, che conosceva l'esperimento.** Baseline e Atelier sono stati scritti dallo stesso modello. Ho cercato di non sabotare la baseline: è ordinata, accessibile, con copy corretto, il tipo di sito che un'AI produce davvero con una richiesta diretta. Ma un osservatore esterno potrebbe giudicarla diversamente.
2. **La rubrica è un'autovalutazione,** non un giudizio indipendente.
3. **I siti premiati non sono stati studiati** (rete bloccata): Atelier non è stato confrontato con siti di livello Awwwards, solo con la baseline.
4. **Un bug iniziale della pipeline** (il CSS di Atelier finiva anche nella baseline) rendeva la baseline rotta e quindi "peggiore". È stato trovato e corretto prima delle misure riportate qui. Lo segnalo perché un confronto non verificato visivamente sarebbe stato falsato a favore di Atelier.

## Risultati misurati (Lighthouse, mediana di 3 run, misura finale)

| Attività | Variante | Perf mobile | Perf desktop | Accessibilità | SEO | LCP mobile | Peso iniziale |
|---|---|---|---|---|---|---|---|
| Fornace Lume | Baseline | 100 | 100 | 100 | 100 | 0,75 s | 5 KB |
| | Atelier BASE | 100 | 100 | 100 | 100 | 1,36 s | 73 KB |
| | Atelier CINEMATICO | 99 | 100 | 100 | 100 | 1,82 s | 121 KB (+~133 KB del worker 3D al primo gesto) |
| Quota 2100 | Baseline | 100 | 100 | 100 (90 nel run precedente) | 100 | 0,76 s | 4 KB |
| | Atelier BASE | 98 | 100 | 100 | 100 | 1,88 s | 152 KB |
| | Atelier CINEMATICO | 97 | 99 | 100 | 100 | 2,26 s | 199 KB (+ worker) |
| Nodo | Baseline | 100 | 100 | 100 (90 nel run precedente) | 100 | 0,75 s | 4 KB |
| | Atelier BASE | 100 | 100 | 100 | 100 | 1,51 s | 76 KB |
| | Atelier CINEMATICO | 97 | 100 | 100 | 100 | 1,89 s | 123 KB (+ worker) |

**Lettura onesta dei numeri:**
- **Lighthouse non distingue i due approcci.** Tutti stanno fra 97 e 100. La baseline è un po' **più veloce** (LCP 0,75 s contro 1,4-2,3 s) perché usa i font di sistema e nessuna grafica.
- **Soglie richieste:**
  - BASE: performance ≥ 90 → superata (98-100);
  - CINEMATICO: ≥ 75 mobile e ≥ 85 desktop → superata (97-99 / 99-100);
  - accessibilità e SEO ≥ 95 → 100 per tutti i siti Atelier.
  - Attenzione: nel CINEMATICO il 3D parte al primo gesto. Con il 3D forzato all'avvio si ottiene mobile 96-99 e desktop 94-100, ma Lighthouse non conta il worker (vedi `QUALITY.md`).
- **Accessibilità:** le baseline di Quota e Nodo hanno fallito il contrasto (90) in un run e l'hanno superato (100) in un altro, senza modifiche. Atelier ha 100 stabile in entrambi i run, perché le palette sono verificate AA nei test.
- **Robustezza misurata, solo Atelier CINEMATICO:**
  - fallback no-WebGL → poster;
  - Save-Data e reduced-motion → nessun canvas e contenuto visibile;
  - 0 errori in console, 0 host esterni, nessun overflow a 375 px.

## Rubrica (autovalutazione, iterazione finale)

Media dei 7 criteri: gerarchia, contrasto, spazio, coerenza, originalità, movimento, mobile.

| Attività | Baseline | Atelier BASE | Atelier CINEMATICO |
|---|---|---|---|
| Fornace Lume | 6,1 | 7,3 | 7,7 |
| Quota 2100 | 6,1 | 7,3 | 7,4 |
| Nodo | 6,0 | 7,4 | 7,7 |

La differenza sta quasi tutta in **originalità** (baseline 2-3, Atelier 6-8), **movimento** (5 contro 6-8) e **mobile** (6 contro 6-8). Su gerarchia e contrasto la baseline è già buona (7-8).

**Cosa si vede negli screenshot** (`reports/shots/`):
- **Baseline:**
  - hero centrato con titolo generico ("Ceramiche artigianali fatte a mano", "Scopri la magia dello scialpinismo", "Proteggi la tua azienda dalle minacce informatiche");
  - tre card con emoji;
  - gradiente indaco-viola su Nodo;
  - riquadri colorati al posto delle immagini;
  - nessuna identità che distingua un settore dall'altro.
- **Atelier:**
  - ogni sito ha una direzione propria: Argilla notturna (smalti e cenere), Quota (curve di livello e altimetro), Cifra (reticolo di punti, tono calmo);
  - titoli scritti per l'attività ("Il piatto lo finisce il fuoco.", "Salire con le pelli, scendere sapendo dove metti gli sci.");
  - dati del brief usati in modo preciso;
  - hero 3D procedurale coerente con il settore;
  - versione mobile dedicata.

## Tempi e costi

| Voce | Atelier | Baseline |
|---|---|---|
| Scrittura dei contenuti di un sito | ~2 min (content JSON 7,6-9,4 KB, ~2,2-2,7k token di output) | ~0,5 min (file .astro 6,4-8,6 KB, ~1,8-2,5k token di output) |
| Input necessario per sito | SKILL.md + direzioni (~6k token) + brief | brief |
| Build (misurata) | 2,1-3,3 s per variante | 1,5-1,8 s |
| QA automatico (misurato) | ~2-3 min per variante con 3 run di Lighthouse | idem (se lo si esegue) |
| Revisione con rubrica | ~6 screenshot per iterazione × 2 iterazioni ≈ 15-20k token di input per sito (immagini) | nessuna |
| Costo marginale stimato per sito | **≈ 30-45k token** (soprattutto la lettura degli screenshot) | **≈ 3-5k token** |
| Costo una tantum (motore, skill, QA, test) | ~143k caratteri di codice e documentazione; sessione intera di sviluppo e prova ≈ **650k token** (dal contatore di sessione) | — |

Le stime in token derivano da dimensione dei file / 3,5 e dal contatore di contesto della sessione. Non c'è una fattura misurata.

## Giudizio: il salto è netto e visibile?

**Dipende.** In concreto:
- **Sì, è visibile, su identità e cura:** a colpo d'occhio i siti Atelier non sembrano template. Ogni settore ha una voce visiva propria, il copy è specifico, il 3D è originale e coerente, la versione mobile è progettata. La baseline è competente ma intercambiabile: gli stessi tre blocchi per tre settori diversi.
- **No, sui numeri tecnici:** Lighthouse è alla pari (anzi la baseline carica prima). Il guadagno misurabile è l'accessibilità stabile al 100 e i fallback verificati, non la velocità.
- **Non dimostrato, sul livello "premiato":**
  - non ho potuto confrontarmi con siti Awwwards;
  - il motore usa un solo template di pagina con 7 archetipi, quindi siti diversi condividono la stessa struttura di sezioni;
  - mancano fotografia e asset reali del brand, che nei siti premiati fanno metà del lavoro.

### Cosa servirebbe per un salto netto e dimostrato
1. **Giudizio esterno:** 3-5 designer o clienti che valutino alla cieca baseline e Atelier.
2. **Studio reale dei riferimenti** (rete libera) e una libreria di layout più varia: più template di pagina, non solo archetipi CSS.
3. **Asset reali del cliente** (foto, logo) o grafica procedurale più ricca per settore.
4. **Test su dispositivi reali con GPU,** e su Safari e Firefox.
5. **Licenza GSAP verificata,** oppure la sostituzione con un'alternativa MIT.

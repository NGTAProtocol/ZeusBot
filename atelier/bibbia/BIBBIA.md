# La Bibbia di Atelier

Metodo obbligatorio per ogni brief. Si applica **prima di scrivere codice**. Il risultato della fase Bibbia è un file `bibbia/<slug>-<config>.json`, validato da `scripts/lib/bibbia.mjs` e usato dalla pipeline.

---

## 1. Fase 0: concept, personalità, firma

### 1.1 CONCEPT
La **tensione narrativa in una frase**: un conflitto o un paradosso dell'attività, non un tema visivo.
- ✗ "Ceramica artigianale con toni caldi." È un tema, non una tensione.
- ✓ "Un piatto da ristorante dev'essere identico agli altri cento, e lo smalto si rifiuta di esserlo."

### 1.2 PERSONALITY
- **Tre aggettivi** che si possono verificare guardando la pagina.
- **Cosa NON è:** almeno un aggettivo contrario, plausibile per il settore, che rifiutiamo esplicitamente.

### 1.3 SIGNATURE
- È l'elemento memorabile. Nasce dal concept e **non si può trasferire** su un altro sito: se funzionerebbe identico per un concorrente, non è una firma.
- Va descritta in una frase: *cosa vede il visitatore, cosa fa, perché dimostra il concept*.
- Tipo: `css` (default) oppure `3d`. Vedi §14.3.

---

## 2. Il contenuto comanda la forma
- Si parte dai contenuti veri del brief (`facts`), non da un layout.
- **Un'idea per sezione.** Se una sezione ha bisogno di due titoli, sono due sezioni.
- **Meglio togliere che aggiungere.** Ogni elemento deve rispondere a: "se lo tolgo, cosa perde il visitatore?"
- **Ogni testo è tagliabile del 30%.** Si scrive, poi si taglia, prima di consegnare.

## 3. Design token
- Tutti i valori in variabili `:root`: colori, font, scala, spazi, raggi, durate, curve. Nessun valore magico nei componenti.
- **Scala tipografica** definita una volta (rapporto modulare).
- **Spaziatura su base 4 px:** 4, 8, 12, 16, 24, 32, 48, 64, 96, 128…
- **Al massimo 2 famiglie di font:** display + testo. Font open (OFL/Apache), serviti in locale.
- **Righe di testo di 45-65 caratteri.**

## 4. Palette e font nascono dal concept
- **Nessuna palette fissa.** Le 8 direzioni della skill sono punti di partenza per ritmo, movimento e archetipo, non palette obbligate.
- Ogni brief sceglie colori e font dal **mondo materiale e culturale del concept**: oggetti, luoghi e strumenti che il pubblico conosce. Per ogni colore si scrive da dove viene ("blu del rame ridotto", "rosso dei segnavia").
- **Strategia di colore** scelta prima dei colori: *Contenuta* (neutri tinti + un accento), *Impegnata* (un colore copre il 30-60% della superficie), *Piena* (3-4 ruoli), *Immersa* (la superficie È il colore).
- **Contrasto AA verificato** su testo e superfici (test automatico).

## 5. Movimento
- **Si muove solo ciò che ha un referente fisico** (versare, girare, salire, aprire) **o che guida lo sguardo** verso la prossima azione.
- **Durate:** micro-interazioni 150-400 ms; sequenze fino a ~4 s.
- **Parte da un'azione dell'utente** (scroll, puntatore, clic, tocco). Il replay è consentito.
- **Nessun loop infinito** e **nessun autoplay aggressivo**. Il 3D si ferma quando l'utente è fermo.
- **Si animano solo `transform` e `opacity`.** Colori, dimensioni e clip cambiano senza transizione.
- **`prefers-reduced-motion` rispettato:** niente spostamenti, il contenuto è già al suo posto.
- **Curve:** ease-out deciso per gli ingressi (`cubic-bezier(.23,1,.32,1)`), ease-in-out per gli spostamenti in scena, mai ease-in sulle interfacce.

## 6. Contenuto in HTML
- Tutto il contenuto è nell'HTML statico e **funziona senza JavaScript**. Il JS aggiunge, non sostituisce.
- Nessun contenuto nascosto in attesa di un'animazione che potrebbe non partire.

## 7. Accessibilità
- **Semantica:** un solo h1, titoli in ordine, landmark (`header`, `nav`, `main`, `footer`).
- **Interazione:** focus visibile e tematizzato, link di salto al contenuto, menu mobile con focus trap ed Esc.
- **Contrasto AA** (4,5:1 per il testo, 3:1 per il testo grande e i componenti).
- **`aria`** solo dove la semantica HTML non basta. Bersagli tattili ≥ 44 px.

## 8. Mostra, non dichiarare
- ✗ "Siamo attenti e gentili." ✓ "Rispondiamo con una proposta entro una settimana."
- Ogni aggettivo di sé va sostituito da un fatto, un tempo, un numero, una condizione.

## 9. Contenuto vero
- Si usano solo i `facts` del brief. Ciò che manca è **UNKNOWN**: va segnalato nel file Bibbia (`unknowns`) e **mai inventato** nel sito.
- **Mai link finti:** ogni `href` porta a una sezione esistente, a una pagina del sito, a `mailto:` o `tel:` veri del brief. Il lint li verifica.

## 10. Lista nera (slop)
Gradiente viola generico; tre card con icone uguali; hero senza personalità ("Benvenuti", "Soluzioni innovative"); immagini stock anonime; lorem ipsum; eyebrow in maiuscolo sopra ogni titolo; numerazione 01/02/03 su contenuti che non sono una sequenza; testo in gradiente; emoji come icone; "→" appesa ai bottoni; CTA duplicate con lo stesso intento ma etichette diverse; frasi vuote ("a 360 gradi", "eccellenza", "la nostra passione").

## 11. Budget di performance
| Livello | JS iniziale (gzip) | Peso iniziale | LCP mobile | Lighthouse |
|---|---|---|---|---|
| BASE | ≤ 10 KB | ≤ 250 KB | ≤ 2,5 s | performance ≥ 90 |
| CINEMATICO | ≤ 60 KB prima dell'interazione; 3D ≤ 150 KB gzip, caricato solo al primo gesto | ≤ 300 KB prima dell'interazione | ≤ 2,5 s | ≥ 75 mobile, ≥ 85 desktop |

Accessibilità e SEO ≥ 95 per tutti. Font: al massimo 4 file woff2 per pagina nel sottoinsieme latin. Nessuna risorsa da CDN.

## 12. Mobile
- **Progettata, non ridimensionata:**
  - lead dedicato più corto;
  - hero che lascia la CTA nel primo schermo;
  - barra CTA fissa dopo l'hero;
  - file orizzontali con scroll-snap per i dati;
  - menu a pagina intera.
- **Il movimento sul touch:** niente scorrimento fluido simulato e niente effetti al passaggio del puntatore; il 3D parte solo al primo gesto e a risoluzione ridotta.
- **Fallback obbligatori:** WebGL assente → firma CSS/SVG; dispositivo debole (`deviceMemory` < 4, `hardwareConcurrency` < 4) → niente 3D; Save-Data → niente 3D né animazioni di scroll; reduced-motion → contenuto statico.

## 13. Copy e conversione
- **La prima schermata risponde a tre domande:** cosa fate, per chi, qual è il passo successivo.
- **Una sola azione principale** per pagina, con **un'etichetta sola** ovunque (nav, hero, barra mobile, contatto) e il verbo dell'azione reale ("Chiedi un preventivo", "Iscriviti al corso base").
- **Struttura da archetipo** (vedi `references/archetipi.md`): promessa → prova → spiegazione → offerta → condizioni/prezzi → domande → invito finale. Si salta una sezione solo se il brief non ha contenuto vero per riempirla.
- **Prove sociali solo vere.** Senza testimonianze reali nel brief, la prova è un fatto verificabile (anni, numeri, condizioni), non una citazione inventata.
- **Obiezioni** affrontate nelle FAQ con risposte brevi e concrete.

## 14. 3D e WebGL
### 14.1 Quando
Solo nel livello CINEMATICO e solo quando serve la firma.
### 14.2 Come
Geometrie e shader procedurali scritti per il progetto. Rendering in Web Worker con OffscreenCanvas. Si ferma fuori schermo e quando l'utente è fermo. Poster SVG identico per palette.
### 14.3 Correzione
**Il 3D/WebGL si usa solo quando È la firma e serve il concept. Altrimenti vince il CSS.**
- Un oggetto 3D decorativo dietro al titolo non è una firma: è un fondale.
- Se la firma si regge con CSS/SVG (transform e opacity guidati dallo scroll o dal puntatore), il livello CINEMATICO usa GSAP e Lenis per quella firma e **non carica Three.js**.

## 15. Licenze degli asset
- Si usano solo:
  - grafica originale o procedurale;
  - font OFL/Apache da pacchetti npm, con la licenza verificata dal test;
  - librerie con licenza registrata in `CREDITS.md`.
- **Mai hotlinking.** Mai codice, testi, immagini, shader, modelli o layout copiati da siti di riferimento.
- Gli asset del cliente (foto, logo, video) entrano con la loro licenza scritta in `CREDITS.md`.

## 16. Consegna
1. Cartella `output/<slug>-<config>-<level>/` statica: si pubblica su Cloudflare Pages, Vercel o GitHub Pages senza build lato server.
2. `meta.url` impostato sul dominio reale (serve a canonical e Open Graph), `robots.txt` e favicon.
3. Report di qualità del sito (Lighthouse, screenshot, checklist Q1-Q6) e lista degli **UNKNOWN** da chiedere al cliente.
4. Nessuna dipendenza da servizi a pagamento. Il form di contatto è `mailto:` finché il cliente non sceglie un servizio.

## 17. SEO
- **Un `<title>` e una meta description per pagina**, scritti per la ricerca reale: attività + cosa fa + luogo (es. "servizi da tavola smaltati a mano per ristoranti, Faenza"). Description di 70-165 caratteri (il lint la misura).
- **Un solo `h1`** con la promessa; gli `h2` sono i temi delle sezioni, in ordine.
- **URL canonico** e Open Graph (`og:title`, `og:description`, `og:url`, `og:locale`) da `meta.url`; `robots.txt` pubblicato; lingua dichiarata in `<html lang>`.
- **Dati strutturati** `LocalBusiness` (JSON-LD) generati dai contatti veri del brief: nome, email, telefono, indirizzo. Mai valori inventati (§9).
- **Il testo è HTML statico** (§6): i motori leggono tutto senza eseguire JavaScript. I titoli spezzati in righe hanno una copia accessibile intera.
- **Prestazioni come fattore di ranking:** il budget del §11 vale anche qui (LCP ≤ 2,5 s su mobile).
- **Link interni veri** (§9): ancore alle sezioni, pagina contatti; nessun link verso pagine inesistenti.
- Obiettivo misurato: **SEO Lighthouse ≥ 95** su mobile e desktop.

---

## CHECKLIST FINALE (per ogni sito)
| | Domanda | Superata se |
|---|---|---|
| **Q1** | Il concept sta in una frase? | La frase è una tensione e si riconosce nella pagina |
| **Q2** | La personalità è distinta? | I tre aggettivi si vedono; il "NON è" è evitato |
| **Q3** | La firma è memorabile? | Non è trasferibile su un concorrente e dimostra il concept |
| **Q4** | Il contenuto è vero? | Solo `facts` del brief; gli UNKNOWN sono dichiarati; nessun link finto |
| **Q5** | Zero slop? | Il lint passa e nessun elemento della lista nera è visibile |
| **Q6** | Cosa ricorderà il visitatore? | Si può nominare un elemento preciso a una settimana di distanza |

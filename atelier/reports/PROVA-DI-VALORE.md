# Prova di valore (v2): Atelier contro un sito AI generico, e quali skill servono

**Domande:**
1. A parità di brief, Atelier produce un sito migliore di un sito AI generico?
2. Quale combinazione di skill rende di più?

## Impostazione
- **3 attività fittizie in 3 settori:**
  - Fornace Lume: ceramica artigianale, Faenza;
  - Quota 2100: scuola di scialpinismo e rifugio, Val Masino;
  - Nodo: sicurezza informatica B2B, Treviso.
- **Stesso brief** (`briefs/`, con i soli `facts` utilizzabili) **in 4 configurazioni × 2 livelli = 24 siti:**

| Config | Cosa la guida |
|---|---|
| **BASELINE** | Nessuna skill, nessuna Bibbia. Tailwind e font di sistema. Il CINEMATICO aggiunge GSAP, Lenis e un oggetto Three.js che ruota, come li scriverebbe un generatore generico |
| **A** | frontend-design + metodo Atelier (Bibbia, lint, firma) |
| **B** | A + impeccable |
| **C** | A + taste-skill + emil-design-eng/emil-animate |

- **Interpretazione dichiarata:** A, B e C usano tutte la pipeline e la Bibbia di Atelier. Cambiano solo le skill ausiliarie, e quindi le scelte della fase Bibbia (palette, font, firma, layout) e del copy.
- **Misure:**
  - Lighthouse 13.5, una run per profilo e per sito;
  - controlli Playwright (overflow, errori, host esterni, contenuti nascosti, fallback);
  - rilevatore di slop sull'HTML compilato;
  - distanza visiva tra i siti della stessa configurazione;
  - rubrica 1-10 su 12 criteri (Q1-Q6 + gerarchia, contrasto, spazio, movimento, mobile, effetto template).
- **Dati completi:** `QUALITY.md` e `metrics.json`.

### Limiti (leggere prima dei numeri)
1. **Stesso autore per tutto.** Baseline, A, B e C sono state scritte dallo stesso modello, nella stessa sessione, sapendo dell'esperimento. Le skill "attive" in una configurazione erano note anche mentre scrivevo le altre. La separazione tra le configurazioni è quindi **imperfetta**.
2. **La rubrica è un'autovalutazione,** non un giudizio di designer o utenti.
3. **Una run per sito:** le differenze di pochi punti Lighthouse sono rumore. La stessa baseline ha dato 80 e poi 67.
4. **Nessun confronto con siti premiati** (rete bloccata), nessun dispositivo reale, WebGL solo software.
5. **Il confronto della v1 non era valido.** Le baseline v1 uscivano senza CSS (Tailwind non scansionava la cartella generata) e la v1 non se n'era accorta. Ora è corretto e coperto da un test (vedi `quality-notes.md`).

## Risultati (medie sui 3 siti)

| Config | Livello | Perf mobile | Perf desktop | A11y | Soglie superate | Slop (HTML) | Distanza visiva tra siti | Rubrica (autoval.) |
|---|---|---|---|---|---|---|---|---|
| BASELINE | BASE | 100 | 100 | 93,3 | **1/3** | 40 | 54,6 | **3,9** |
| BASELINE | CINEMATICO | 68 | 86 | 94 | **0/3** | 40 | 52,3 | **3,9** |
| A | BASE | 98 | 100 | 100 | 3/3 | 0 | 13,6 | **7,5** |
| A | CINEMATICO | 98,7 | 99,7 | 100 | 3/3 | 0 | 19,7 | **7,6** |
| B | BASE | 100 | 100 | 100 | 3/3 | 0 | 49,8 | 7,3 |
| B | CINEMATICO | 98,7 | 100 | 100 | 3/3 | 0 | 50,1 | 7,4 |
| C | BASE | 100 | 100 | 100 | 3/3 | 0 | 10,6 | 6,7 |
| C | CINEMATICO | 97,3 | 100 | 100 | 3/3 | 0 | 10,5 | 6,8 |

**SEO:** 100 per tutti i 24 siti.

**Tempi e costi:**

| | BASELINE | A | B | C |
|---|---|---|---|---|
| Build per sito | 1,9-2,7 s | 1,9-3,2 s | 1,9-3,0 s | 1,9-2,6 s |
| Token di output scritti a mano per sito (stima: byte/4) | ~1.900 / 2.400 | ~3.100 | ~2.400 | ~2.100 |

- **Il costo vero in token non è misurato.** Il totale di questa sessione (lettura delle skill, iterazioni, QA) è di vari ordini di grandezza superiore ai token scritti, e non è attribuibile alle singole configurazioni.
- **Il tempo di scrittura per configurazione non è stato cronometrato.** Il QA completo dei 24 siti richiede circa 75 minuti di macchina.

### Cosa dicono i numeri
1. **Prestazioni, accessibilità, SEO:**
   - tutti i 18 siti Atelier superano le soglie (BASE ≥ 90; CINEMATICO ≥ 75 mobile e ≥ 85 desktop; a11y e SEO ≥ 95);
   - le baseline ne superano 1 su 6. Le BASE di Quota e Nodo hanno accessibilità 90 (contrasto dei testi su sfumature). Le CINEMATICO stanno a 66-71 su mobile, per il loop 3D infinito nel thread principale (TBT 1,2-2,2 s);
   - **attenzione:** sul BASE le baseline hanno LCP migliore (font di sistema, 0,75 s contro 1,0-1,4 s).
2. **Slop:**
   - baseline: 7-24 segnali per sito (emoji come icone, gradienti viola/indaco, testo sfumato, card in serie);
   - Atelier: 0;
   - **ma** il rilevatore controlla regole che il lint di Atelier già impone: è una verifica di conformità, non una prova indipendente.
3. **Effetto template, il dato scomodo:** per distanza visiva i siti A e C di tre clienti diversi **si somigliano tra loro** (10-20) più delle baseline (52-55). Le cause:
   - stesso motore e stesso schema di pagina;
   - fondi chiari;
   - in C, la stessa firma `layers` su due clienti.

   Solo B, con strategie di colore molto diverse per cliente, varia quanto la baseline (50).
4. **Rubrica:** il salto grande è tra baseline (3,9) e qualsiasi configurazione Atelier (6,7-7,6). Tra A, B e C le differenze sono piccole:
   - **A** vince di poco: firme più legate al concept (la colatura di Fornace, il rilievo 3D di Quota);
   - **B** è quasi alla pari: più personalità cromatica, ma la massa 3D di Fornace B è debole;
   - **C** è la più bassa. Applicare alla lettera regole generiche di gusto (sans ovunque, un accento, hero di 2 righe) ha prodotto siti puliti, ma **più intercambiabili**, ed è l'effetto opposto a quello cercato.

## Verdetto

| Domanda | Risposta |
|---|---|
| Atelier batte un sito AI generico? | **Sì** su tutto ciò che si misura: soglie Lighthouse 18/18 contro 1/6, zero slop, nessun loop infinito, link e contenuti verificati. **Sì** anche nella rubrica, che però è un'autovalutazione |
| Il salto è netto? | **Sì** tra baseline e Atelier. **No** tra A, B e C: differenze di 0,1-0,9 punti di rubrica, dentro l'incertezza di un giudizio fatto dallo stesso modello |
| Quale configurazione vince? | **A (frontend-design + Bibbia)** di poco, **B** quasi alla pari. **C non conviene** come predefinita |
| Cosa produce il valore? | La **Bibbia e la pipeline** (concept → firma, lint dei fatti e dei link, budget, QA), più delle skill aggiuntive |
| Abbastanza per vendere? | **Dipende.** Vedi sotto |

**Perché "Dipende":**
- **Basta** per vendere siti vetrina curati a piccole attività: veloci, accessibili, senza cliché, con contenuti veri e una firma riconoscibile. Il livello è superiore a un generatore generico.
- **Non basta** per vendere siti "di livello Awwwards":
  - le firme sono 4 parametriche più 5 scene 3D, non disegnate da zero per ogni cliente;
  - i siti di clienti diversi si somigliano;
  - non c'è fotografia reale;
  - non c'è nessun giudizio esterno né confronto con siti premiati;
  - la licenza GSAP non è verificata per un uso come servizio.
- **Cosa servirebbe:**
  - una revisione di un designer umano su un campione;
  - lo studio dei riferimenti con dati veri (possibile con il connettore Firecrawl, che però è a pagamento e quindi richiede la tua conferma);
  - nuove firme per ogni cliente;
  - foto del cliente;
  - test su telefoni reali.

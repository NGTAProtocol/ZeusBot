# Fase 8 — Correttore e rifinitura per la pubblicazione — «Il padre del mostro»

- **Punto di partenza:** `5ede115`. **Punto di ripristino:** `cf6d1bb`.

## 1. Strumento usato

- **LanguageTool:** non disponibile. Il pacchetto `language-tool-python` si installa, ma il programma vero e proprio deve essere scaricato da `languagetool.org` / `internet.languagetool.org`, e il proxy di rete del container rifiuta la connessione (HTTP 403, «connect_rejected»).
  - **Conseguenza: non è stato fatto nessun controllo grammaticale o di stile automatico.** LanguageTool resta da fare in un ambiente con accesso a quel sito (vedi «da decidere»).
- **Hunspell `it_IT`:** installato dai pacchetti di sistema (`hunspell`, `hunspell-it`). Controllo ortografico su tutto il testo di `04-manoscritto/`, in UTF-8.
- **Controlli propri, per espressione regolare:**
  - doppi spazi;
  - spazio prima di virgola, punto, punto e virgola, due punti, punto esclamativo, punto interrogativo e », oppure dopo «;
  - spazio mancante dopo la punteggiatura;
  - accenti sbagliati (perchè, poichè, sè, nè, pò, qual'è, E', ventitre…);
  - parole ripetute;
  - virgolette dritte e apostrofi curvi.

## 2. Esito

- **Hunspell:** 130 forme non riconosciute. **Nessuna è un refuso.** Classificazione completa qui sotto (prima occorrenza «cap.:riga»).
- **Refusi certi corretti nel testo:** solo le virgolette dritte (punto 2 della richiesta). Altro non serviva:
  - nessun accento sbagliato;
  - nessun doppio spazio;
  - nessuno spazio mancante;
  - nessuno spazio prima della punteggiatura, salvo i due casi voluti del cap. 41 («da decidere»).
- **«Mamma .» al prologo:** nel manoscritto non c'è (prologo, r. 17: `*Mamma*.`). Era un artefatto dell'estrazione del testo dal PDF. Non toccato.
- **«se se» al cap. 16, r. 213:** «come se se ne accorgesse» è corretto. Non toccato.
- **Apostrofi:** solo dritti in tutto il manoscritto, nessun apostrofo curvo misto.

### elisione (falso allarme del dizionario) (35)

dell (124, 0:31), all (123, 1:43), dall (80, 0:5), nell (39, 0:53), quell (36, 1:215), sull (31, 3:5), vent (28, 2:7), dov (18, 1:203), quest (16, 7:137), gliel (16, 2:95), All (15, 18:53), trent (13, 8:95), Nell (8, 1:75), Dall (8, 2:79), qualcos (7, 7:127), settant (6, 14:131), mezz (6, 13:137), quarant (5, 8:25), cinquant (5, 4:19), Dov (5, 14:191), sessant (3, 5:71), cos (3, 9:221), com (3, 11:51), Vent (3, 25:57), sott (2, 38:90), anch (2, 8:11), Quell (2, 8:85), ventiquattr (1, 43:63), novant (1, 15:187), Trent (1, 41:7), Sessant (1, 6:7), Quarant (1, 49:43), Mezz (1, 31:129), Gliel (1, 33:41), Dell (1, 52:9)

### abbreviazione o sigla (11)

AV (22, 0:23), AGIORGI (6, 1:171), SRV (5, 34:143), ADM (5, —), TVELA (3, 34:141), Sen (3, 34:21), sec (1, 40:45), cost (1, 39:70), USB (1, 4:153), Dott (1, 9:169), CIA (1, 12:61)

### prestito straniero (15)

System (22, 0:23), force (19, 37:83), report (4, 0:61), rating (3, 30:53), futures (3, 30:31), desk (3, 0:29), food (2, 10:19), audit (2, 4:109), spritz (1, 25:27), moka (1, 24:37), kilobyte (1, 34:5), gigabyte (1, 40:9), curricula (1, 1:159), Regulator (1, 51:69), Futures (1, 41:51)

### parola valida assente dal dizionario (20)

sedette (45, 1:45), portablocco (25, 5:27), sedeva (7, 9:55), serrani (4, 18:147), fiducianti (4, 31:15), sedettero (3, 7:53), possedeva (3, 7:181), magistrata (3, 20:135), anticorruzione (3, 34:89), varnio (2, 3:71), siede (2, 16:95), monospaziato (2, 0:63), Sedeva (2, 31:25), trecentoventimila (1, 4:67), sieda (1, 35:13), sedevano (1, 13:131), risedette (1, 31:131), maxischermo (1, 0:41), maxiprocessi (1, 3:37), Quattrocentodiciottomila (1, 34:11)

### nome proprio o luogo inventato (49)

Giorgi (295, 0:69), Kurgan (244, 2:33), Merania (110, 0:3), Albaterra (67, 0:3), Adorisio (64, 3:13), Partenia (63, 2:49), Salvarani (41, 8:5), Bertola (41, 8:27), Rastegar (37, 7:49), Clodio (36, 3:111), Biasi (32, 26:9), Serrana (30, 2:71), Marcena (27, 0:3), Carrese (26, 3:13), Valdhof (25, 9:5), Salmara (23, 21:9), Volkov (20, 10:25), Cicimarra (20, 34:21), Sannella (16, 9:65), Valcerna (15, 0:19), Tarassa (15, 5:27), Cadrasca (14, 8:83), Notarangelo (12, 5:7), Morenna (12, 0:19), Drenak (10, 2:95), Consob (10, 9:9), Castelvaro (10, 49:75), Vetra (9, 0:21), Oddone (9, 14:117), Pisapia (8, 40:35), Serrania (7, 3:49), Clodia (7, 15:179), Chen (7, 18:7), Parsàn (6, 13:41), Perennis (5, 4:9), Civitas (5, 4:9), Casal (5, 26:49), Portofosco (3, 38:21), Kaliria (2, 12:21), Aterno (2, 17:15), Zanella (1, 25:39), Wei (1, 18:7), Varnia (1, 3:77), Ursini (1, 25:39), Ronchedo (1, 38:11), Palumbo (1, 25:39), Padèra (1, 38:11), Hossein (1, 7:49), Dmitri (1, 10:25)
## 3. Tipografia e impaginazione

- **Virgolette dritte → « ».** Cinque coppie, cioè le 10 virgolette segnalate:
  - cap. 1, r. 159 («inutilmente elegante»);
  - cap. 4, r. 19 («dall'interno dei suoi numeri»);
  - cap. 5, r. 193 («per il ministero»);
  - cap. 9, rr. 107 e 139 («per il ministero»).
  - Nessuna virgoletta dritta residua, né nel manoscritto né nel PDF.
- **Impaginazione portata nel repository:** nuova cartella `07-impaginazione/`. Fino a ieri gli script stavano solo nella cartella temporanea della sessione. Contenuto:
  - `compile_md.py`: compone il testo completo;
  - `build_pdf.py`: impagina;
  - `print.js`: Chromium/Playwright;
  - `fonts.css` e `fonts/`: EB Garamond, licenza OFL;
  - `.gitignore` per la cartella di lavoro `_build/`.
- **Frontespizio:**
  - «Il padre del mostro», «F.R. Faraone», «Romanzo». Tolto «Romanzo — prima stesura rivista».
  - Pagina 2: copyright «© 2026 F.R. Faraone. Tutti i diritti riservati.» e la nota sulla finzione, nel testo richiesto. Nessun ISBN.
- **Numerazione:**
  - Frontespizio, copyright e indice (4 pagine) sono senza numero.
  - Il prologo è pagina 1; il libro arriva a pagina 490.
  - L'indice riporta questi numeri.
- **Numeri di pagina:** in EB Garamond 9 pt, al posto di DejaVu Serif. Sono stampati con PyMuPDF dopo l'impaginazione, perché l'intestazione di Chromium non carica il font del libro.
- **Font incorporati:** solo EB Garamond (regolare e corsivo), tutti come Type0 incorporati.
  - **Correzione tecnica trovata durante il lavoro:** il tondo del testo era incorporato come font **Type3**, sia nel PDF precedente sia nel primo PDF di questa fase. Il motivo è che il file EB Garamond scaricato da Google Fonts è un font «variabile», e Chromium lo converte in Type3.
  - Ho creato istanze fisse (pesi 400 e 600) con fontTools: `fonts/*-static.woff2`. Ora non c'è nessun Type3.
  - Nell'indice il corsivo dentro il grassetto («Parte prima — *La creatura*») produceva un grassetto-corsivo sintetico, anch'esso Type3: ora il corsivo è a peso normale.
- **Metadati PDF:** Title «Il padre del mostro», Author «F.R. Faraone», Subject «Romanzo».
- **Orfane e vedove:**
  - `orphans:2; widows:2` sui paragrafi (erano già impostati).
  - In più, l'ultimo paragrafo di ogni capitolo resta legato al precedente (`break-before: avoid-page`), così una riga finale non resta sola su una pagina nuova.
  - Testo e margini invariati.
  - Ultime pagine dei capitoli dopo la modifica: cap. 41 da 4 a 22 parole, cap. 44 da 14 a 19. Restano corte, ma con almeno due righe: cap. 1 (28 parole), cap. 11 (28), cap. 12 (35), cap. 39 (14, tre righe di dialogo). Per accorciarle ancora bisognerebbe toccare testo o margini, che è escluso.
- **Separatori di scena:** i 261 `---` del manoscritto diventano tutti `* * *` centrati, con la stessa spaziatura. Nel manoscritto non ci sono altri separatori (`***`, `___`).

## 4. Verifiche finali

- **PDF:** 494 pagine (4 iniziali senza numero + 490 numerate). Manoscritto: 111.470 parole (stessa formula delle fasi precedenti).
- **Indice:** 58 voci, tutte coincidono con il numero stampato sulla pagina d'inizio. Ogni pagina numerata porta il suo numero esatto.
- **Virgolette dritte residue:** 0. **«prima stesura»:** 0. **«Felice»:** 0.
- **Autore:** «F.R. Faraone» sul frontespizio, nel copyright e nei metadati.
- **Font:** solo EB Garamond, incorporati, nessun Type3.
- **Durate:** le occorrenze di «N anni» sono identiche a quelle di `5ede115`. Il manoscritto differisce da `5ede115` solo per le 5 righe delle virgolette.
- `il-padre-del-mostro-completo.pdf` e `il-padre-del-mostro-rivisto.pdf` sono identici.

---

## Nota di chiusura (1 ottobre 2026)

**Righe cambiate nel manoscritto** (solo virgolette):
- cap. 1, r. 159;
- cap. 4, r. 19;
- cap. 5, r. 193;
- cap. 9, rr. 107 e 139.

**Impaginazione:**
- nuova cartella `07-impaginazione/` (frontespizio, copyright, numerazione, font fissi, orfane e vedove, metadati);
- rigenerati `05-output/il-padre-del-mostro-completo.md`, `il-padre-del-mostro-completo.pdf` e `il-padre-del-mostro-rivisto.pdf`.

**Non toccato, e perché:**
- Trama, voce, durate e dialoghi, per la regola generale.
- Le scelte già approvate:
  - cap. 2, r. 29;
  - cap. 12, rr. 19, 25 e 71;
  - cap. 40, r. 59;
  - cap. 51, r. 89;
  - il «sei anni» di Nicola al cap. 43.
- I nomi propri e i luoghi inventati, compresi Varnia/varnio e Padèra.
- Le 130 forme non riconosciute da Hunspell: nessuna è un refuso (sezione 2).
- I margini e il corpo del testo, per tua istruzione.

**Da decidere:**
1. **Cap. 41, rr. 23 e 55: «*12 novembre ?*»**, con uno spazio prima del punto interrogativo. È l'appunto a mano di Dalia; alla r. 55 Dalia «cancellò il punto interrogativo», quindi lo spazio può essere voluto, per mostrare il segno staccato. Le alternative sono «*12 novembre?*» oppure lasciarlo.
2. **«Felice Faraone» come autore nei documenti di lavoro**, fuori da `04-manoscritto/` e dall'impaginazione, quindi non toccati per la regola di salvataggio:
   - `00-progetto/stato.md`, r. 4;
   - `02-bibbia/bibbia.md`, r. 4;
   - `01-mercato/mercato.md`, r. 3.
   - Dimmi se vanno aggiornati.
3. **Controllo grammaticale e di stile con LanguageTool:** non eseguito, perché il sito di download è bloccato dal proxy. Va fatto in un ambiente con rete libera, oppure abilitando `languagetool.org` nella policy di rete dell'ambiente.
4. **Ultime pagine corte rimaste** (capp. 1, 11, 12, 39, 44): si possono migliorare solo intervenendo su testo o margini.
5. **Pagina dispari per il prologo:** oggi il prologo è a pagina 1 del PDF, ma è la quinta pagina fisica, cioè una pagina pari. Per la stampa di solito il prologo apre su una pagina dispari, e servirebbe una pagina bianca in più dopo l'indice. Non aggiunta perché non richiesta.

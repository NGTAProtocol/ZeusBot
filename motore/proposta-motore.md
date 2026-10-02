# Motore editoriale — proposta

Stato: **proposta**, nessun file del motore è ancora stato creato oltre a questo.
Ramo: `claude/mister-provino-espansione`, cartella `motore/` alla radice di NGTAProtocol/ZeusBot.
Vincoli: `libri/` non si tocca; casa-editrice si legge soltanto, mai in scrittura.
Fonte delle direttive KDP: `riferimenti/11-direttive-kdp.md` di NGTAProtocol/casa-editrice, `origin/main` @ becd0e2.

---

## A. Direttive KDP nel motore

### A.1 Verifica sulle pagine ufficiali (kdp.amazon.com/help)

Tentativo del 2026-10-02 dal container della sessione: **bloccato dal proxy** (`CONNECT tunnel failed, response 403`) per tutte e tre le pagine provate (Metadata Guidelines, Paperback trim/bleed/margins, Keywords). Nessun valore è stato confrontato con la fonte ufficiale.

| Voce | Valore nel file | Valore sulla pagina ufficiale |
|---|---|---|
| Titolo + sottotitolo | < 200 caratteri | non consultabile (403) |
| Descrizione | max 4.000 caratteri | non consultabile (403) |
| Parole chiave | 7 caselle | non consultabile (403) |
| Margine interno per pagine | tabella in A.2 | non consultabile (403) |
| Margini esterni | 0,25" / 0,375" | non consultabile (403) |
| Pagine min/max | 24 / 828 bianca / 776 crema | non consultabile (403) |
| Tag HTML descrizione | lista in A.2 | non consultabile (403) |

Di conseguenza `ultima_verifica` resta **null** e lo script segnala la verifica come mai fatta.

### A.2 `motore/dati/kdp.yaml`

```yaml
# Direttive KDP in forma di dati.
# Fonte: casa-editrice riferimenti/11-direttive-kdp.md (main @ becd0e2)
# e KDP Help Center (kdp.amazon.com/help). Prima di pubblicare, riverificare.
ultima_verifica: null        # AAAA-MM-GG; null = mai verificata
validita_giorni: 30
url_verifica: https://kdp.amazon.com/help

metadati:
  titolo_piu_sottotitolo_max_caratteri: 200      # 11-direttive r. 11
  descrizione_max_caratteri: 4000                # r. 17
  parole_chiave_max: 7                           # r. 30
  parole_chiave_parole_consigliate: [2, 3]       # r. 31 (fuori range = avviso)
  categorie_max: 3                               # r. 37
  html_ammesso_descrizione:                      # r. 20
    stato: da_verificare_sulla_pagina_ufficiale
    tag: [b, strong, i, em, u, br, p, ul, ol, li, h4, h5, h6]
  # Confronto per PAROLA INTERA o FRASE COMPLETA, senza distinzione
  # di maiuscole: regex \b<voce>\b. «Amazzonia», «Amazonas», «freedom»,
  # «gratissimo» NON scattano.
  parole_vietate:            # titolo, sottotitolo, parole chiave, editore (rr. 7, 28, 32)
    - amazon
    - kindle
    - kindle unlimited
    - kdp
    - kdp select
    - bestseller
    - best seller
    - gratis
    - free
    - n/a
    - nessuno                # solo se è l'intero valore del campo
  formule_vietate_descrizione:   # r. 19, r. 21 (bloccanti)
    - "per i fan di"
  pattern_descrizione:
    bloccanti:               # r. 19
      url: '(?i)\bhttps?://|\bwww\.'
      email: '[\w.+-]+@[\w-]+\.[A-Za-z]{2,}'
    avvisi:
      telefono: '\+?\d[\d\s./-]{7,}\d'

cartaceo:
  formati_citati_pollici:    # r. 50: elenco non chiuso
    - [6, 9]
    - [5, 8]
    - [5.25, 8]
    - [5.5, 8.5]
  pagine_min: 24             # r. 51
  pagine_max: {bianca: 828, crema: 776}
  pagine_pari:               # avviso, non KO
    stato: da_verificare_sulla_pagina_ufficiale
  margine_esterno_min_pollici: {senza_bleed: 0.25, con_bleed: 0.375}   # r. 52
  bleed_pollici: 0.125           # r. 55
  margine_interno_per_pagine:    # r. 53
    - {da: 24,  a: 150, pollici: 0.375}
    - {da: 151, a: 300, pollici: 0.5}
    - {da: 301, a: 500, pollici: 0.625}
    - {da: 501, a: 700, pollici: 0.75}
    - {da: 701, a: 828, pollici: 0.875}
  margine_esterno_consigliato_narrativa: [0.6, 0.75]   # r. 54, solo consiglio
  font_incorporati: obbligatorio                        # r. 56

isbn:
  modalita_predefinita: kdp_gratuito
  editore_risultante: "Independently published"

dichiarazione_ai:            # rr. 62-64
  domande: [testo, immagini, traduzioni]
  testo_del_sistema: generato
```

### A.3 Esiti: cosa blocca e cosa avvisa

- **KO (bloccanti):** URL, email, «per i fan di», parole vietate (a parola intera), tag HTML non ammessi, superamento dei limiti di caratteri, più di 7 parole chiave, più di 3 categorie, margini o pagine fuori soglia, font non incorporati o Type3, nome autore diverso tra i file, conferme dell'autore mancanti.
- **AVVISO (non bloccanti):** numeri di telefono, parole chiave che ripetono parole del titolo, parole chiave fuori da 2-3 parole, formato pagina non tra quelli citati, numero di pagine dispari (da verificare), ISBN presente nel manoscritto, verifica delle direttive scaduta o mai fatta.
- La verifica scaduta (più di 30 giorni o `null`) produce un avviso in testa al report e il codice d'uscita 2: il pacchetto non risulta pronto finché qualcuno non riverifica kdp.amazon.com/help e aggiorna la data.

### A.4 `motore/script/conformita_kdp.py`

Uso:

```
python3 motore/script/conformita_kdp.py libri/<nome> [--pdf <percorso>] [--carta crema|bianca] [--bleed]
```

Legge `06-pubblicazione/scheda-amazon.md`, `manoscritto-finale.md`, `cartaceo.pdf` (o `--pdf`), `ebook.docx` se c'è, `06-pubblicazione/conferme-autore.yaml` e `motore/dati/kdp.yaml`. Scrive `libri/<nome>/06-pubblicazione/conformita-kdp.md`: in testa data, hash del PDF, stato della verifica; poi una riga **OK/KO** con la **prova** (il testo o il valore esatto controllato) e gli eventuali **avvisi** per ognuna delle sezioni 1-15. Un controllo lasciato all'autore e non confermato è **KO** con nota «da confermare dall'autore» (11-direttive r. 76). Codice d'uscita: 0 tutto OK; 1 almeno un KO; 2 verifica direttive scaduta.

| Sez. | Controlla da solo | Lascia all'autore (`conferme-autore.yaml`) |
|---|---|---|
| 1 Titolo | Parole vietate a parola intera, tag HTML, valore vuoto; identico in scheda, frontespizio e `Title` del PDF (`pdfinfo`) | identico in copertina (fronte o dorso) |
| 2 Sottotitolo | Titolo + sottotitolo ≤ 200 caratteri; parole vietate; più di 2 virgole = avviso | identico in copertina |
| 3 Serie | Se presente: numero in cifre, nome senza parole vietate; se assente: OK, prova «nessuna serie» | ordine dei libri |
| 4 Descrizione | ≤ 4.000 caratteri; KO: URL, email, «per i fan di», parole vietate, tag fuori lista; avviso: telefono | spoiler, recensioni camuffate |
| 5 Autore | Nome identico in `Author` del PDF, frontespizio, copyright, scheda | pseudonimo non ingannevole, collaboratori reali |
| 6 Editore | Parole vietate; con ISBN gratuito la nota «Independently published» | — |
| 7 Parole chiave | Massimo 7, parole vietate (KO); duplicati del titolo e frasi fuori 2-3 parole (avvisi) | pertinenza |
| 8 Categorie | Massimo 3 | coerenza categorie/parole chiave/descrizione/copertina; contenuti espliciti |
| 9 Copertina | — | bleed, dimensioni dal calcolatore KDP, nessuna imitazione, dati identici ai metadati, riquadro del codice a barre libero |
| 10 ISBN | Vedi A.5 | `isbn: kdp_gratuito` |
| 11 Cartaceo | Formato da `pdfinfo` (avviso se non citato); pagine min/max per carta; pagine pari (avviso); margini con `pdftotext -bbox` (interno a sinistra sulle dispari, a destra sulle pari; esterni); font con `pdffonts` (tutti `emb=yes`, nessun Type3) | scelta della carta |
| 12 eBook | Se c'è `ebook.docx`: stili Titolo 1/2, nessun campo numero di pagina, intestazione o piè di pagina | controllo con Kindle Previewer |
| 13 Dichiarazione AI | Promemoria fisso (A.6) | `dichiarazione_ai: fatta` |
| 14 Contenuti | — | copyright, marchi, contenuti per adulti segnalati |
| 15 Recensioni | Nell'invito alla recensione: niente «positiva», «5 stelle», compensi o copie in cambio | nessuno scambio di recensioni |

Metodo dei margini: per ogni pagina il riquadro minimo che contiene tutte le parole, numero di pagina compreso; pagina dispari = recto, interno a sinistra; pagina pari = verso, interno a destra. Il report riporta il minimo trovato e la pagina dove cade.

### A.5 ISBN (sezione 10)

- Si usa l'**ISBN gratuito di KDP**: KDP lo assegna alla creazione del titolo e mette il codice a barre nel riquadro bianco della quarta di copertina.
- Riga del report: **«ISBN gratuito KDP, nessuna azione»**, OK se `conferme-autore.yaml` contiene `isbn: kdp_gratuito`, altrimenti KO «da confermare dall'autore».
- Nessuno script crea ISBN o codici a barre.
- **Avviso** se un ISBN compare nel manoscritto: non deve esserci finché non è assegnato; dopo l'assegnazione deve coincidere con quello di KDP.
- **Promemoria copertina:** il riquadro del codice a barre resta libero, secondo il modello del calcolatore KDP.
- **Nota nel report:** con l'ISBN gratuito l'editore risulta «Independently published».

### A.6 Passo fisso «dichiarazione AI»

Riquadro stampato alla sezione 13 e in fondo a ogni report:

> **Promemoria per l'autore — dichiarazione AI su KDP.** Alla pubblicazione KDP pone tre domande: **testo**, **immagini**, **traduzioni**. Il testo prodotto con questo sistema va dichiarato **«generato dall'AI»**, anche se poi modificato a fondo. Lo stesso vale per copertine e traduzioni fatte con l'AI. La dichiarazione non è visibile ai lettori; ometterla può portare alla rimozione del libro e a sanzioni sull'account.

La sezione 13 resta KO finché `conferme-autore.yaml` non contiene `dichiarazione_ai: fatta`.

### A.7 Primo caso di prova: PDF DEFINITIVO di Kurgan/Giorgi

File: `libri/kurgan-giorgi/05-output/il-padre-del-mostro-DEFINITIVO.pdf` del ramo `claude/kurgan-giorgi-thriller-3f6mfq` (sha256 `fe460844b5515225f88a3840fcf2873564eb32761740652df227aed32dfa9a7d`). Sul ramo del motore quel PDF non c'è: il caso di prova lo passa con `--pdf` dal checkout dell'altro ramo. Misure fatte il 2026-10-02 con `pdfinfo`, `pdffonts`, `pdftotext -bbox`, senza modificare il file.

| Controllo | Misurato | Soglia | Esito atteso |
|---|---|---|---|
| Pagine | 494 (pari) | 24 – 776 crema / 828 bianca | OK |
| Margine interno | min 0,705" (17,9 mm) a pag. 64; mediana 0,708" | ≥ 0,625" (301-500 pagine) | OK |
| Margine esterno (lato) | min 0,704" (17,9 mm) a pag. 409 | ≥ 0,25" | OK |
| Margine alto | min 0,870" (22,1 mm) a pag. 429 | ≥ 0,25" | OK |
| Margine basso | min 0,435" (11,1 mm) a pag. 5 (numero di pagina); corpo 0,894" | ≥ 0,25" | OK |
| Font | solo EB Garamond Regular/Italic, tutti incorporati, nessun Type3 | tutti incorporati | OK |
| Autore | `Author` «F.R. Faraone»; frontespizio e copyright «F.R. Faraone» | identico | OK |
| Formato | 420 × 594,96 pt = 5,83 × 8,26" (A5) | formati citati r. 50 | AVVISO |

Sezioni 1-10 e 12-15: per Kurgan/Giorgi oggi non esistono `06-pubblicazione/`, `scheda-amazon.md` né `conferme-autore.yaml`, quindi il caso di prova copre solo la sezione 11 e il nome autore nel PDF.

---

## B. Il motore: proposta 1-7

### B.1 Inventario di ciò che esiste

**ZeusBot, `libri/kurgan-giorgi/07-impaginazione/`** (ramo `claude/kurgan-giorgi-thriller-3f6mfq`)

| File | Cosa fa | Decisione |
|---|---|---|
| `compile_md.py` (38 righe) | Compone il `completo.md`: occhietto, autore, copyright, indice, parti, capitoli, `---` → `* * *`, FINE | **riusare con modifiche**: titolo, autore, parti e copyright oggi sono scritti nel codice; vanno letti da `libro.yaml` |
| `build_pdf.py` (119 righe) | md → HTML → PDF con Chromium; numeri di pagina con PyMuPDF dal prologo; metadati | **riusare con modifiche**: formato (`@page size:A5`), margini e font da `libro.yaml`; margine interno scelto dalla tabella KDP |
| `print.js` (16 righe) | Render Playwright | **riusare** così com'è |
| `fonts.css`, `fonts/*-static.woff2` | EB Garamond statico (niente Type3) | **riusare** |
| `.gitignore` per `_build/` | | **riusare** |

**ZeusBot, `libri/kurgan-giorgi/06-diagnostica/`**

| File | Decisione |
|---|---|
| `fase2-…`, `fase3-…`, `fase4-…`, `fase5-…`, `fase8-…`, `fase9-…`, `fase10-…`, `proposta-coerenza-finale.md` | **non riusare** come codice: sono registri delle fasi di quel libro; restano dove sono |
| `controllo-ortografico.md` | **riusare il metodo** (Hunspell it_IT, `-i utf-8`) in uno script `ortografia.py` |
| `keyword-per-capitolo.md`, `pattern-metafora-tecnica.md`, `proposte-metafora-tecnica.md` | **riusare con modifiche**: il metodo diventa un controllo di `stile.py`, le liste diventano dati in `libro.yaml` |

**ZeusBot, `libri/_modelli/`** (README, capitolo, luogo, personaggio, piano, stato) e `libri/libro-attivo.md`: **riusare** come modelli; `libro-attivo.md` resta il puntatore al libro attivo (oggi: `kurgan-giorgi`).

**ZeusBot, `libri/mister-provino/`**: `03-architettura/manuale-di-stile.md` è la fonte delle regole del libro (frase media, minimi, formule contate, tetti, immagini vietate, metodo unico di conteggio). **Riusare come dati**: i valori passano in `libro.yaml`, il manuale resta il testo di riferimento.

**casa-editrice (`origin/main` @ becd0e2), sola lettura**

| File | Decisione |
|---|---|
| `SKILL.md` (fasi 1-10) | **riusare con modifiche**: la sequenza delle fasi diventa l'elenco dei comandi; le parti che contrastano con il manuale del libro cedono (vedi B.5) |
| `riferimenti/01-mercato`, `02-architettura`, `04-editing-sviluppo`, `06-lettori-beta`, `07-copyediting`, `09-edizione-inglese`, `10-lancio` | **riusare** come testo di procedura, letti dal motore, non copiati |
| `riferimenti/03-stesura` | **riusare con modifiche**: r. 12 «interrompi sul massimo della domanda» contrasta con il manuale di Mister Provino (chiusure su gesto o oggetto) |
| `riferimenti/05-critica-e-punteggio` | **riusare**: scheda a 10 voci, soglia media < 8 o voce < 7; la lista nera diventa dati di `stile.py` |
| `riferimenti/08-pubblicazione` | **riusare con modifiche**: ordine del manoscritto finale; gli interludi senza numero vanno aggiunti al sommario |
| `riferimenti/11-direttive-kdp` | **riusare come dati** in `kdp.yaml` |
| `riferimenti/12-lunghezze` | **riusare con modifiche**: `wc -w` sostituito dal metodo unico (B.5) |
| `modelli/` (lezioni, personaggio, registro-promesse, scheda-scena, stato, struttura-capitolo, style-sheet) | **riusare** come modelli |

### B.2 Albero di `motore/`

```
motore/
  proposta-motore.md        questo file (esiste)
  README.md                 come si usa il motore, comandi, regole fisse     da scrivere
  zb                        lanciatore: zb <comando> [libro]                 da scrivere
  dati/
    kdp.yaml                direttive KDP (A.2)                              da scrivere
    lista-nera.yaml         cliché e tic da 05-critica rr. 19-21             da scrivere
    libro.schema.yaml       schema di libro.yaml (B.3)                       da scrivere
  script/
    comune.py               lettura di libro.yaml, percorsi, ramo, salvataggio  da scrivere
    conta.py                metodo unico di conteggio, parole per pagina     da scrivere
    stile.py                frase media, formule contate, tetti, immagini vietate, lista nera  da scrivere
    ortografia.py           Hunspell it_IT                                   da scrivere (metodo esistente)
    compila.py              manoscritto completo da 04-manoscritto           esiste come compile_md.py (da generalizzare)
    impagina.py             PDF di stampa                                    esiste come build_pdf.py (da generalizzare)
    print.js                render Chromium                                  esiste (da copiare)
    verifica_pdf.py         pagine, margini, font, sommario/pagine           da scrivere (metodo provato in A.7)
    conformita_kdp.py       report KDP sezioni 1-15                          da scrivere
    pacchetto.py            06-pubblicazione: scheda, quarta, brief, checklist  da scrivere
  impaginazione/
    fonts.css               EB Garamond statico                              esiste (da copiare)
    fonts/                  woff2 statici                                    esiste (da copiare)
  prove/
    attesi.yaml             valori attesi dei casi di prova (sha256, conteggi)  da scrivere
```

Esistono già, da generalizzare o copiare: `compile_md.py`, `build_pdf.py`, `print.js`, `fonts.css`, `fonts/`. Tutto il resto va scritto.

### B.3 Schema di `libro.yaml`

Un file per libro in `libri/<nome>/libro.yaml` (si crea solo dopo approvazione, vedi B.6). Esempio con i valori di Mister Provino dal suo manuale di stile.

```yaml
titolo: "Mister Provino"
sottotitolo: null
autore: "F.R. Faraone"
lingua: it
genere: narrativa            # chiave della tabella minimi di 12-lunghezze r. 19-28

formato:
  pagina_pollici: [5.5, 8.5] # da scegliere con l'autore; Kurgan oggi: A5 (5,83 x 8,27)
  carta: crema
  bleed: false
  margini_mm: {alto: 22, basso: 22, esterno: 18, interno: auto}   # auto = tabella KDP
  font: {nome: "EB Garamond", corpo_pt: 11.5, interlinea: 1.5}
  numerazione: {da: prologo, pagine_iniziali: senza_numero, posizione: piede_centro}

parole:
  target_totale: 78000
  tolleranza_totale: 0.05
  capitolo: {minimo: 1300, media: 1700, massimo: null, tolleranza: 0.15}
  prologo: 500
  epilogo: 1000
  interludi: {numero: 9, minimo: 300, massimo: 600}
  parole_per_pagina_misurate: null   # calcolate da impagina.py sul PDF reale

stile:
  persona: prima
  tempo: {racconto: passato, interludi: presente}
  frase_media: [10, 13]
  dialogo_percento: [15, 35]
  similitudini_max_per_parole: 300
  gesti_di_conteggio_max_per_capitolo: 3
  chiusure: {sentenza_tematica_max: 8, consecutive: false, mai_su_domanda: true}
  formule_contate:           # manuale 3.5
    - {formula: "Non era X. Era Y.", massimo_libro: 5}
    - {formula: "come se", massimo_capitolo: 2}
    # ... le altre righe della tabella 3.5
  immagini_vietate:          # manuale 4.3
    - "lama (figurata)"
    - "cuore che martella / in gola"
    # ... elenco completo dal manuale
  lista_nera_casa_editrice: true    # 05-critica rr. 19-21, cede al manuale

struttura:
  separatore_scena: "•"      # Kurgan: "---" nel sorgente → "* * *" in stampa
  nomi_file: "{numero:02d}-{slug}.md"
  intestazione_capitolo: "Voce — luogo, data"   # Kurgan: "*Nome — Luogo, giorno mese*"
  prologo_epilogo_numerati: false
  interludi_numerati: false
  parti:
    - {titolo: "Parte prima — Il cane", capitoli: [1, 19]}
    - {titolo: "Parte seconda — La caccia", capitoli: [20, 30]}
    - {titolo: "Parte terza — Oltre l'orizzonte", capitoli: [31, 43]}

voce_narratore: "03-architettura/manuale-di-stile.md §2"   # rimando, non copia
manuale: "03-architettura/manuale-di-stile.md"
ramo: "claude/mister-provino-espansione"
copyright: "© {anno} {autore}. Tutti i diritti riservati."
```

### B.4 Comandi a una parola

Forma: `motore/zb <comando> [libro]`; senza libro usa `libri/libro-attivo.md`.

| Comando | Script | Report (in `libri/<nome>/06-diagnostica/` salvo diversa indicazione) |
|---|---|---|
| `stato` | `comune.py` | a schermo: libro, ramo, fase, ultimo commit, allineamento con origin |
| `conta` | `conta.py` | `conteggio.md`: parole per capitolo, scarto dal budget, totale |
| `stile` | `stile.py` | `stile.md`: frase media, dialogo %, formule contate, tetti, immagini vietate, lista nera |
| `ortografia` | `ortografia.py` | `controllo-ortografico.md` |
| `compila` | `compila.py` | `05-output/<titolo>-completo.md` |
| `impagina` | `impagina.py` | `05-output/<titolo>-completo.pdf`, `-rivisto.pdf`, `-DEFINITIVO.pdf` |
| `pdf` | `verifica_pdf.py` | `verifica-pdf.md`: pagine, margini, font, sommario contro pagine reali |
| `kdp` | `conformita_kdp.py` | `06-pubblicazione/conformita-kdp.md` |
| `pacchetto` | `pacchetto.py` | `06-pubblicazione/`: scheda-amazon, quarta, brief-copertina, checklist, promemoria AI |

Nessun comando fa commit o push da solo: il salvataggio segue B.5.

### B.5 Regole fisse

1. **Tono.** Il vecchio testo di un libro è un registro dei fatti: non si commenta né si giudica, nei report come in chat.
2. **Proponi → approvo → applica.** Ogni modifica al testo o ai dati di un libro si propone, voce per voce; si applica solo dopo l'OK. Mai nuovi oggetti o persone in una scena senza richiesta.
3. **Metodo unico di conteggio.** Token separati da spazi; esclusi le righe che cominciano con «#» e i token senza lettere né cifre (lineette di dialogo, separatori, segni isolati). Niente `wc -w`, che cambia con la lingua di sistema. Ogni report dichiara il metodo.
4. **Precedenza.** Manuale del libro > procedura (motore e casa-editrice) > skill dell'autore. In caso di contrasto vince il manuale del libro e il report lo segnala.
5. **Ramo.** Si lavora solo sul ramo assegnato dalla sessione o indicato in `libro.yaml`; il motore controlla il ramo prima di scrivere e si ferma se non coincide.
6. **Dichiarazione AI.** Promemoria fisso in ogni pacchetto e in ogni report KDP (A.6).
7. **Blocco di salvataggio.** Dopo ogni fase: file derivati rigenerati, report in `06-diagnostica/`, `git add`, commit, push, `git status -sb`, `git log`. Se il push fallisce o un file non si salva: fermarsi e riportare l'errore, mai dire «fatto» se non è su origin. Resoconto con hash, file, pagine, parole e «branch allineato a origin: sì/no».
8. **Direttive KDP.** Verifica più vecchia di 30 giorni = avviso e pacchetto non pronto.

### B.6 Migrazione dei due romanzi senza rompere nulla

1. **Nessun file di `libri/` si sposta, si rinomina o si cancella.** I due libri restano sui loro rami.
2. Il motore legge i libri; non scrive in `libri/` finché `libro.yaml` del libro non è approvato e aggiunto con un commit a parte.
3. **Kurgan/Giorgi** (ramo `claude/kurgan-giorgi-thriller-3f6mfq`): `07-impaginazione/` resta. Prova di non regressione: `compila` + `impagina` del motore in una cartella temporanea devono riprodurre `completo.md` identico e un PDF con lo stesso numero di pagine, gli stessi margini e lo stesso sommario del DEFINITIVO (sha256 `fe460844…`). Solo con la prova superata il libro passa al motore.
4. **Conteggio di Kurgan.** Il totale registrato (111.468, con la formula `grep -v … | wc -w`) resta nei report storici. Il motore calcola il totale con il metodo unico e lo riporta accanto, senza riscrivere i report vecchi.
5. **Mister Provino** (ramo `claude/mister-provino-espansione`): `04-manoscritto/` è vuoto; il motore parte con `conta` sul vecchio testo e deve dare **49.998 parole**, il valore del manuale. È il caso di prova di `conta.py`.
6. **Rami.** Il motore vive su `claude/mister-provino-espansione`. Su quel ramo Kurgan è in una versione precedente (senza `07-impaginazione/`); per Kurgan il motore si usa con `--pdf` e `--libro` da un checkout del ramo di Kurgan, finché i rami non vengono riuniti con una decisione esplicita.

### B.7 Ordine di costruzione e libro di prova

| Passo | Cosa | Caso di prova | Criterio |
|---|---|---|---|
| 1 | `dati/kdp.yaml`, `script/verifica_pdf.py`, `script/conformita_kdp.py` | PDF DEFINITIVO di Kurgan con `--pdf` | sezione 11 OK con i valori di A.7; avviso formato A5; avviso verifica mai fatta |
| 2 | `script/conta.py` | vecchio testo di Mister Provino | 49.998 parole esatte |
| 3 | `dati/libro.schema.yaml` + bozza di `libro.yaml` dei due libri (in chat, non in `libri/`) | entrambi | approvazione dell'autore |
| 4 | `script/compila.py`, `script/impagina.py`, `impaginazione/` | Kurgan | non regressione di B.6 punto 3 |
| 5 | `script/stile.py`, `dati/lista-nera.yaml` | Mister Provino, primi capitoli scritti | valori del registro dei contatori del manuale |
| 6 | `script/ortografia.py` | Kurgan | zero errori certi, come `controllo-ortografico.md` |
| 7 | `script/pacchetto.py`, `zb`, `README.md` | Kurgan | pacchetto completo; report KDP con le sole conferme dell'autore aperte |

Ogni passo: proposta → OK → codice → caso di prova → commit e push secondo B.5.

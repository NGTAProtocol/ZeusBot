# Motore editoriale — proposta

Stato: **proposta**, nessun file del motore è ancora stato creato oltre a questo.
Parti: A (direttive KDP), B (motore 1-7), C (funzionamento quasi automatico: macchina a stati, stesura, briefing, avvio obbligatorio, sessioni, migrazione, secondo lettore, distribuzione ai rami dei libri).
Ramo: `claude/mister-provino-espansione`, cartella `motore/` alla radice di NGTAProtocol/ZeusBot.
Vincoli: `libri/` non si tocca; casa-editrice si legge soltanto, mai in scrittura.
Fonte delle direttive KDP: `riferimenti/11-direttive-kdp.md` di NGTAProtocol/casa-editrice, `origin/main` @ becd0e2, da copiare in `motore/riferimenti/` (B.8): dopo la copia il motore non legge più casa-editrice.

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
- **AVVISO (non bloccanti):** numeri di telefono, parole chiave che ripetono parole del titolo, parole chiave fuori da 2-3 parole, formato pagina non tra quelli citati finché `formato_confermato_kdp` in `conferme-autore.yaml` è false (con true la riga è OK, A.9), numero di pagine dispari (da verificare), ISBN presente nel manoscritto, verifica delle direttive scaduta o mai fatta.
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
| 11 Cartaceo | Formato da `pdfinfo` (avviso se non citato); pagine min/max per carta; pagine pari (avviso); margini con `pdftotext -bbox` (interno a sinistra sulle dispari, a destra sulle pari; esterni); font con `pdffonts` (tutti `emb=yes`, nessun Type3) | scelta della carta; `formato_confermato_kdp` (A.9) |
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
| Formato | 420 × 594,96 pt = 5,83 × 8,26" (A5) | formati citati r. 50 | AVVISO finché `formato_confermato_kdp: false` (A.9) |

Sezioni 1-10 e 12-15: per Kurgan/Giorgi oggi non esistono `06-pubblicazione/`, `scheda-amazon.md` né `conferme-autore.yaml`, quindi il caso di prova copre solo la sezione 11 e il nome autore nel PDF.


### A.8 Verifica delle direttive: la data la scrive l'autore

**Comando:** `verifica KDP fatta [AAAA-MM-GG]` (senza data vale oggi). Lo esegue `motore/script/kdp_verifica.py`.

**File:** imposta `ultima_verifica` in **`motore/dati/kdp.yaml`**, e solo lì. Perché lì:
- le direttive sono di Amazon, non di un libro: una sola verifica vale per tutti i libri;
- `conformita_kdp.py` legge la data da quel file e la copia in testa a ogni report;
- tenerla in `stato.yaml` di ogni libro creerebbe date diverse per le stesse regole.

**Regole del comando:**
- rifiuta una data futura o scritta male;
- accetta una data più vecchia di 30 giorni, ma avvisa che è già scaduta;
- aggiunge una riga a `motore/dati/verifiche-kdp.md` (data, chi, valori confermati) e fa commit e push con il blocco di salvataggio;
- non tocca nessun altro valore: se l'autore ha trovato un valore diverso, lo dice con «correggi: …» e la modifica a `kdp.yaml` passa dal gate.

**Se il proxy blocca le pagine ufficiali,** lo script prova a scaricarle, e al primo 403 stampa questo promemoria, breve e leggibile da telefono:

```
Verifica KDP a mano (proxy bloccato)
Ultima verifica: mai

1 Titolo+sottotitolo: < 200 caratteri
2 Descrizione: max 4.000 caratteri
3 Parole chiave: 7 caselle
4 Margine interno: 24-150 p 0,375" | 151-300 0,5" | 301-500 0,625" | 501-700 0,75" | 701-828 0,875"
5 Margini esterni: 0,25" senza bleed | 0,375" con bleed
6 Pagine: min 24 | max 828 bianca, 776 crema
7 Tag HTML descrizione: b i u em strong br p ul ol li h4-h6

Link:
kdp.amazon.com/help/topic/G201097560  (metadati: 1, 2)
kdp.amazon.com/help/topic/G201298500  (parole chiave: 3)
kdp.amazon.com/help/topic/G201834180  (formato, margini, pagine: 4, 5, 6)
kdp.amazon.com/help  (cerca «description HTML»: 7)

Se tutto coincide: verifica KDP fatta AAAA-MM-GG
Se qualcosa cambia: correggi: <voce> <valore nuovo>
```

I tre codici di pagina sono quelli che conosco per quelle guide e non li ho potuti aprire: alla prima verifica vanno confermati, e se sono cambiati si correggono in `kdp.yaml` (`url_verifica`).

### A.9 `conferme-autore.yaml`

File per libro: `libri/<nome>/06-pubblicazione/conferme-autore.yaml`. Lo scrive solo l'autore, oppure il motore su sua risposta esplicita.

```yaml
isbn: kdp_gratuito              # sezione 10
formato_confermato_kdp: false   # sezione 11: true quando l'autore ha verificato
                                # che il formato del PDF (per Kurgan A5) è
                                # accettato da KDP. Con false: AVVISO, non KO.
carta: crema
dichiarazione_ai: da_fare       # sezione 13: "fatta" dopo la pubblicazione
copertina_verificata: false     # sezione 9
categorie_coerenti: false       # sezione 8
contenuti_verificati: false     # sezione 14
recensioni_regolari: false      # sezione 15
note: ""
```

Le voci a `false` delle sezioni 8, 9, 14 e 15 danno KO «da confermare dall'autore» (A.4). Fa eccezione `formato_confermato_kdp`, che dà solo AVVISO.

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

**casa-editrice (`origin/main` @ becd0e2)**: si legge una volta sola, per copiarla in `motore/riferimenti/` con gli adattamenti di B.8; dopo la copia il motore non la legge più e non ci scrive mai.

| File | Decisione |
|---|---|
| `SKILL.md` (fasi 1-10) | **non copiare**: la sequenza delle fasi è già riscritta in C.1 e finisce in `motore/PROCEDURA.md`; la sua r. 53 (`wc -w`) non vale |
| `riferimenti/01-mercato`, `04-editing-sviluppo`, `06-lettori-beta`, `07-copyediting`, `09-edizione-inglese`, `10-lancio` | **riusare**: copiati in `motore/riferimenti/` senza modifiche, salvo l'intestazione di fonte |
| `riferimenti/03-stesura` | **riusare con modifiche** (B.8, mod. 1): r. 12, chiusure su gesto o oggetto |
| `riferimenti/05-critica-e-punteggio` | **riusare con modifiche** (B.8, mod. 4): scheda a 10 voci, soglia media < 8 o voce < 7; lista nera unita alle immagini vietate del manuale del libro |
| `riferimenti/08-pubblicazione` | **riusare con modifiche** (B.8, mod. 5-6): interludi senza numero nel corpo e nel sommario |
| `riferimenti/11-direttive-kdp` | **riusare**: copiato senza modifiche; i valori passano anche in `kdp.yaml` |
| `riferimenti/02-architettura` | **riusare con modifiche** (B.8, mod. 7, nuova): r. 39, gancio di chiusura senza «domanda» come prima scelta |
| `riferimenti/12-lunghezze` | **riusare con modifiche** (B.8, mod. 2-3): `wc -w` sostituito dal metodo unico |
| `modelli/` (lezioni, personaggio, registro-promesse, scheda-scena, stato, struttura-capitolo, style-sheet) | **riusare**: copiati in `motore/riferimenti/modelli/` senza modifiche |

### B.2 Albero di `motore/`

```
motore/
  proposta-motore.md        questo file (esiste)
  PROCEDURA.md              fasi, gate, comandi, regole fisse (C.1-C.7)      da scrivere
  README.md                 come si usa il motore, comandi, regole fisse     da scrivere
  zb                        lanciatore: zb <comando> [libro]                 da scrivere
  riferimenti/               copia di casa-editrice main @ becd0e2 (B.8)       da copiare
    01-mercato.md … 12-lunghezze-e-struttura-capitoli.md   12 file, 5 adattati (B.8)
    modelli/                lezioni, personaggio, registro-promesse, scheda-scena,
                            stato, struttura-capitolo, style-sheet (7 file)
  modelli/
    briefing.md             briefing da compilare dal telefono (C.3)         da scrivere
    LEGGIMI.md              modello del LEGGIMI di libro (C.4)               da scrivere
    stato.yaml              modello della macchina a stati (C.1)             da scrivere
  dati/
    kdp.yaml                direttive KDP (A.2); ultima_verifica (A.8)       da scrivere
    verifiche-kdp.md        registro delle verifiche fatte dall'autore (A.8) da scrivere
    lista-nera.yaml         cliché e tic da 05-critica rr. 19-21             da scrivere
    libro.schema.yaml       schema di libro.yaml (B.3)                       da scrivere
    stato.schema.yaml       schema di stato.yaml (C.1)                       da scrivere
    hook.yaml               modalita dell'hook: avviso | blocco (C.4)        da scrivere
  script/
    avvio.py                lettura obbligatoria, marker di sessione (C.4)   da scrivere
    fase.py                 macchina a stati: gate, ok/avanti/correggi/stato (C.1)  da scrivere
    capitolo.py             controlli del capitolo in un colpo solo (C.2)    da scrivere
    riciclo.py              anti-riciclo a 7 parole (C.2)                    da scrivere
    date.py                 date e giorni della settimana dal calendario (C.2)  da scrivere
    revisione.py            «prepara per revisione»: blocchi da incollare (C.7)  da scrivere
    hook_sessione.py        hook SessionStart (C.4, solo proposta)           da scrivere
    hook_manoscritto.py     hook PreToolUse, modalità avviso/blocco (C.4)    da scrivere
    comune.py               lettura di libro.yaml, percorsi, ramo letto da git, salvataggio  da scrivere
    continuita.py           date, età, durate, cifre, nomi in due grafie (B.2.1)  da scrivere
    conta.py                metodo unico di conteggio, parole per pagina     da scrivere
    stile.py                frase media, formule contate, tetti, immagini vietate, lista nera  da scrivere
    ortografia.py           Hunspell it_IT                                   da scrivere (metodo esistente)
    compila.py              manoscritto completo da 04-manoscritto           esiste come compile_md.py (da generalizzare)
    impagina.py             PDF di stampa                                    esiste come build_pdf.py (da generalizzare)
    print.js                render Chromium                                  esiste (da copiare)
    verifica_pdf.py         pagine, margini, font, sommario/pagine           da scrivere (metodo provato in A.7)
    conformita_kdp.py       report KDP sezioni 1-15                          da scrivere
    kdp_verifica.py         «verifica KDP fatta [data]»; promemoria se 403 (A.8)  da scrivere
    pacchetto.py            06-pubblicazione: scheda, quarta, brief, checklist  da scrivere
  impaginazione/
    fonts.css               EB Garamond statico                              esiste (da copiare)
    fonts/                  woff2 statici                                    esiste (da copiare)
  prove/
    libro-prova/            libro finto di 3 capitoli con errori voluti (B.2.2)  da scrivere
    attesi.yaml             esiti attesi degli script e dei casi reali (sha256, conteggi)  da scrivere
```

File per libro letti dal motore (in `libri/<nome>/`, creati solo dopo approvazione): `libro.yaml` (B.3), `stato.yaml` (C.1), `LEGGIMI.md` (C.4), `cronologia.yaml` (B.2.1), `nomi_propri.txt` (B.3), `06-pubblicazione/conferme-autore.yaml` (A.9).

Esistono già, da generalizzare o copiare: `compile_md.py`, `build_pdf.py`, `print.js`, `fonts.css`, `fonts/` (da `libri/kurgan-giorgi/07-impaginazione/`) e i 19 file di `riferimenti/` (da casa-editrice). Tutto il resto va scritto.

`motore/modelli/` (modelli del motore: briefing, LEGGIMI, stato) e `motore/riferimenti/modelli/` (modelli di casa-editrice) sono due cartelle diverse.

#### B.2.1 Continuità: `continuita.py` e `cronologia.yaml`

**File per libro:** `libri/<nome>/cronologia.yaml`, compilato in fase 3 (C.1) dai documenti approvati (bibbia, scaletta). Contiene:

```yaml
nascite:
  - {chi: Beniamino, data: AAAA-MM-GG}        # dalla bibbia, sezione 3 (cronologia)
eventi:
  - {id: palo, data: 1976-07-17, capitolo: 10, descrizione: "il palo"}   # scaletta: cap. 10, sab 17 luglio
durate:                                       # ogni «N anni/mesi/giorni» atteso nel testo
  - {da: evento_x, a: evento_y, valore: "tre anni", tolleranza_mesi: 6}
cifre:                                        # zaino, debiti, prezzi (bibbia 5.7)
  - {id: zaino, valore: <dalla tabella della bibbia 5.7>, unita: lire, forme_ammesse: [<cifre>, <in lettere>]}
eta_per_capitolo:                             # calcolata da nascite + data d'intestazione
  calcolata: true
```

**Cosa controlla `continuita.py`** (tabelle nel report `06-diagnostica/continuita.md`):

| Controllo | Come |
|---|---|
| Giorni della settimana | ogni «sabato 17 luglio» nell'intestazione e nel testo, ricalcolato su `calendario.anni_ammessi`; KO se nessun anno ammesso dà quel giorno |
| Età | ogni «N anni» riferito a un personaggio nominato nella stessa frase, confrontato con nascita e data del capitolo; KO oltre ±1 anno |
| Durate | **tabella di tutte le occorrenze** di «N anni/mesi/settimane/giorni» con capitolo e riga, e il ricalcolo dalle date di intestazione e da `durate`; KO oltre la tolleranza |
| Cifre ripetute | ogni cifra in lettere o in numeri vicina a «lire», «milioni», «mila» confrontata con `cifre`; KO se diversa dalle forme ammesse |
| Nomi propri scritti in due modi | parole con maiuscola non in `nomi_propri.txt` a distanza di modifica 1-2 da una voce dell'elenco (es. «Nardo» / «Nardu») → avviso con le due grafie |
| Ordine delle date | le date d'intestazione non tornano indietro rispetto alla scaletta → avviso |

**Cosa NON può controllare**, e come lo segnala:
- che un oggetto o una persona sia già in scena, o sia uscito di scena;
- chi sa cosa in un certo momento (per esempio Nicola che non sa di Michele fino al 21 luglio);
- la posizione dei personaggi nello spazio e i tempi di spostamento («il Ciao e le distanze»);
- il tempo interno di una scena (giorno e notte, pasti, luce);
- età e durate dette in modo indiretto («quando aveva l'età di Franco»);
- le conseguenze fisiche (ferite, il segno del collare) da un capitolo all'altro.

Per questi punti il report finisce con una **checklist manuale**: una riga per capitolo con le voci della bibbia che il capitolo tocca (personaggi, oggetti, ferite, chi sa cosa) e la casella «verificato dall'autore». Al gate G5 la checklist si mostra con il capitolo; le caselle vuote restano avvisi aperti in `stato.yaml`, non KO.

#### B.2.2 Libro di prova: `motore/prove/`

```
motore/prove/
  libro-prova/
    libro.yaml              titolo «Prova», A5, minimo 300 parole, 2 interludi
    cronologia.yaml         2 nascite, 3 eventi, 1 durata, 1 cifra
    nomi_propri.txt
    03-architettura/scaletta.md, piano-parole.md
    04-manoscritto/
      00-prologo.md         corretto
      01-*.md               corretto: deve passare tutti i controlli
      02-*.md               errori voluti: «lama di luce», «come se» ×3, «Lucia» prima del limite,
                            giorno della settimana sbagliato, età sbagliata, «Nardo» per «Nardu»,
                            chiusura S consecutiva, intrusioni 4
      03-*.md               sotto il minimo di parole, frase media 22, ultima riga di una parola
  attesi.yaml               per ogni script: esito atteso, controllo, file, riga
```

`attesi.yaml` elenca ogni KO e ogni avviso atteso, e il numero di parole con il metodo unico. Uno script si usa sui due romanzi solo dopo che sul libro di prova dà esattamente gli esiti attesi: nessun KO in più, nessuno in meno. Poi si aggiungono i casi reali: 49.998 parole sul registro dei fatti di Mister Provino (B.7 passo 2) e i margini del PDF di Kurgan/Giorgi (A.7).

### B.3 Schema di `libro.yaml`

Un file per libro in `libri/<nome>/libro.yaml` (si crea solo dopo approvazione, vedi B.6). Esempio con i valori di Mister Provino, presi dal manuale di stile (`03-architettura/manuale-di-stile.md`, «manuale») e dalla scaletta.

**Il ramo non sta in `libro.yaml`.** Lo legge `comune.py` da git (`git branch --show-current`): ogni sessione ha il suo ramo. `avvio.py` controlla solo che il libro attivo di quel ramo (`libri/libro-attivo.md`) esista e abbia `libro.yaml` (C.4).

**Formato e margine interno.** Formato A5 (5,83 × 8,27"), come Kurgan/Giorgi, valido solo con `formato_confermato_kdp: true` in `conferme-autore.yaml` (A.9); finché è false il report dà AVVISO. Margine interno = **max(tabella KDP per numero di pagine, margine scelto)**. Stima per Mister Provino con la densità di Kurgan/Giorgi (111.468 parole su 494 pagine = 225,6 parole per pagina): 78.000 ÷ 225,6 ≈ **346 pagine** → fascia KDP **301-500 → 0,625" (15,9 mm)**. Il margine scelto (18 mm = 0,709") è più largo, quindi vale **18 mm**. Se il libro finisse sotto le 301 pagine la fascia scenderebbe a 0,5" e il margine resterebbe 18 mm; sopra le 500, 0,75" (19,1 mm) supererebbe i 18 mm e `impagina.py` userebbe 19,1 mm. Il numero vero di pagine lo misura `impagina.py`, che ricalcola il margine e rifà l'impaginazione se cambia fascia.

```yaml
titolo: "Mister Provino"
sottotitolo: null
autore: "F.R. Faraone"
lingua: it
genere: narrativa            # chiave della tabella di 12-lunghezze rr. 19-28

formato:
  pagina_pollici: [5.83, 8.27]   # A5; accettazione KDP in conferme-autore.yaml (A.9)
  carta: crema
  bleed: false
  margini_mm: {alto: 22, basso: 22, esterno: 18, interno_scelto: 18}
  margine_interno: max(tabella_kdp, interno_scelto)   # calcolato da impagina.py
  font: {nome: "EB Garamond", corpo_pt: 11.5, interlinea: 1.5}
  numerazione: {da: prologo, pagine_iniziali: senza_numero, posizione: piede_centro}

parole:
  metodo: unico              # manuale §1
  target_totale: 78000
  tolleranza_totale: 0.05
  capitolo:
    minimo: 1300
    media: 1700
    tolleranza_budget: 0.15  # ±15% sul budget DEL CAPITOLO in 03-architettura/piano-parole.md,
                             # non sulla media generica (12-lunghezze rr. 66-67)
    override_dichiarato:
      campo: minimo
      valore_tabella: 2000   # 12-lunghezze, narrativa
      valore_libro: 1300
      motivo: "Capitoli brevi del romanzo di formazione a doppia voce, media 1.700 (manuale §1, scaletta)."
      fonte: "12-lunghezze r. 30: scelta narrativa dichiarata"
  prologo: 500
  epilogo: 1000
  interludi: {minimo: 300, massimo: 600}
  parole_per_pagina_misurate: null   # calcolate da impagina.py sul PDF reale

stile:
  persona: prima
  tempo: {racconto: passato, interludi: presente}
  frase_media: [10, 13]
  frase_breve: {sotto_parole: 6, massimo_di_fila: 3}           # manuale 3.1
  paragrafi_una_frase_breve_max_capitolo: 3                    # manuale 3.1
  dialogo_percento: [15, 35]
  similitudini_max_per_parole: 300                             # manuale 4.1
  gesti_di_conteggio_max_per_capitolo: 3                       # manuale 3.6
  aperture: {data_in_prima_frase: vieta, risveglio_max_libro: 3}   # manuale 3.3
  chiusure:                                                    # manuale 3.4
    sigle: [G, I, O, B, F, S]   # gesto, immagine, oggetto, battuta, fatto, sentenza (scaletta r. 7)
    sentenza_max_libro: 8
    sentenza_consecutive: false
    escluso_dal_conto: [epilogo]
    frase_isolata_max_parole: 2   # vieta la chiusura su una riga di 1-2 parole
  intrusioni:                                                  # manuale 2.2
    per_capitolo: [1, 3]
    capitoli_a_zero: [10]
    ancore:                       # controllo incrociato: avviso, non KO
      - "allora non lo sapevo"
      - "quel giorno"
      - "anni dopo"
      - "l'ho saputo anni dopo"
      - "oggi"
      - "da vecchio"
      - "me lo raccontò"
      - "me l'hanno raccontato"
      - "non ricordo se"
  aforismi: {massimo: "1 ogni 2 capitoli", solo_dentro_intrusione: true}
  lista_nera_casa_editrice: true  # 05-critica rr. 19-21 (B.8 mod. 4), cede al manuale
  voci:                           # vedi sotto, «Voci con pattern»

struttura:
  separatore_scena: {sorgente: "•", stampa: "•"}   # manuale §1 nomina «•»; da confermare
  nomi_file: "{numero:02d}-{slug}.md"
  intestazione_capitolo: "Luogo — giorno e data"   # un solo narratore: niente «Voce»
  intestazione_interludio: "Titolo"                # in corsivo, senza data (manuale 2.3)
  dichiarazioni_capitolo: "<!-- zb: chiusura=G intrusioni=2 aforismi=0 -->"
  prologo_epilogo_numerati: false
  interludi_numerati: false
  parti:
    - {titolo: "Parte prima — Il cane", capitoli: [1, 19]}
    - {titolo: "Parte seconda — La caccia", capitoli: [20, 30]}
    - {titolo: "Parte terza — Oltre l'orizzonte", capitoli: [31, 43]}
  interludi:                                       # scaletta rr. 75-396
    - {numero: I,    dopo_capitolo: 3,  titolo: "I fiori",    parte: 1}
    - {numero: II,   dopo_capitolo: 10, titolo: "La pagina",  parte: 1}
    - {numero: III,  dopo_capitolo: 15, titolo: "La nave",    parte: 1}
    - {numero: IV,   dopo_capitolo: 19, titolo: "La lettera", parte: 1}
    - {numero: V,    dopo_capitolo: 25, titolo: "Il collo",   parte: 2}
    - {numero: VI,   dopo_capitolo: 30, titolo: "Il telefono", parte: 2}
    - {numero: VII,  dopo_capitolo: 35, titolo: "Ero io",     parte: 3}
    - {numero: VIII, dopo_capitolo: 38, titolo: "La firma",   parte: 3}
    - {numero: IX,   dopo_capitolo: 43, titolo: "Le pagine",  parte: 3}

nome_vietato_prima_di:                             # manuale 2.5
  - nome: "Lucia"
    pattern: '\bLucia\b'
    vietato_in: [prologo, "1-36", "interludi I-VI"]
    obbligatorio_in: ["37-43", "interludi VII-IX", epilogo]   # avviso se il capitolo nomina
                                                             # «il ritratto» o «lei» senza «Lucia»

calendario:
  anni_ammessi: [1976, 1977]   # 1976 come richiesto; 1977 proposto: la scaletta (r. 388) data il cap. 43 al 1977
  file: cronologia.yaml        # B.2.1

ortografia:
  parole_ammesse_file: nomi_propri.txt   # una voce per riga, letto da ortografia.py e continuita.py
  esempi: [Sabino, Gaetano, "don Tobia", "zi' Nardu", "La Scala", "Mister Provino", Beniamino, Checco, Michele, Cataldo, Saro, Ciro]

copyright:
  riga: "© {anno} {autore}. Tutti i diritti riservati."
  fantasia: >                  # 08-pubblicazione r. 7
    Quest'opera è frutto di fantasia. Nomi, personaggi e fatti sono invenzione
    dell'autore o usati in modo fittizio; ogni somiglianza con persone, vive o
    scomparse, o con fatti realmente accaduti è puramente casuale.
  nota_autore: >               # pagine finali, 08-pubblicazione r. 9
    Bari e il 1976 sono reali: le strade, i quartieri, le istituzioni nominate.
    Le persone, le famiglie e i clan del romanzo sono inventati, e nessuno di loro
    rimanda a persone o gruppi realmente esistiti. Date, luoghi e cifre sono stati
    adattati alle esigenze del racconto.

voce_narratore: "03-architettura/manuale-di-stile.md §2"   # rimando, non copia
manuale: "03-architettura/manuale-di-stile.md"
```

Per Kurgan/Giorgi gli stessi campi hanno: `separatore_scena: {sorgente: "---", stampa: "* * *"}`, `intestazione_capitolo: "Nome — Luogo, giorno mese"` (sette punti di vista), `calendario.anni_ammessi: [2025, 2026, 2027, 2028]`. Gli anni sono Y, Y+1, Y+2, Y+3 del suo calendario, che usa quattro anni e non tre: capp. 1-10 in Y, cap. 11 in Y+1, capp. 12-47 in Y+2, capp. 48-53 in Y+3. `00-progetto/semi.md` r. 118 dice che la griglia dei giorni della settimana è «coerente con 2025/2027, anno mai nominato».

#### Voci con pattern (`stile.voci`)

Ogni voce ha: `id`, `pattern` (regex Python, `(?i)` = senza maiuscole), `modalita` (`vieta`: ogni occorrenza è KO; `conta`: KO solo sopra il massimo; `avviso`: elenca le occorrenze con capitolo e riga per un controllo a vista), `massimo`, `ambito` (`libro` | `capitolo`), e quando serve `consentito_in_capitoli` / `vietato_in_capitoli` / `solo_dialogo`.

```yaml
voci:
  # Manuale 3.5 — formule contate
  - {id: non_era_era, pattern: '(?i)\bnon (era|fu)\b[^.!?]{1,60}[.!?]\s+(era|fu)\b', modalita: conta, massimo: 5, ambito: libro}
  - {id: non_ma_due_frasi, pattern: '(?i)\bnon\b[^.!?]{1,60}[.!?]\s+ma\b', modalita: avviso, ambito: libro, nota: "variante del 3.5; somma a non_era_era dopo controllo a vista"}
  - {id: era_peggio, pattern: '(?i)\bera peggio\b|\bqualcosa di peggio\b', modalita: conta, massimo: 2, ambito: libro}
  - {id: come_si_verbo, pattern: '(?i)\bcome si [a-zà-ù]+(a|e|ono|ava|eva)\b', modalita: conta, massimo: 1, ambito: capitolo}
  - {id: non_risposi_isolata, pattern: '(?im)^(—\s*)?(non risposi|non disse niente)\.\s*$', modalita: conta, massimo: 1, ambito: capitolo}
  - {id: una_specie_di, pattern: '(?i)\buna specie di\b', modalita: conta, massimo: 10, ambito: libro}
  - {id: qualcosa_di_agg, pattern: '(?i)\bqualcosa di (?!peggio\b)[a-zà-ù]+', modalita: conta, massimo: 1, ambito: capitolo}
  - {id: come_se, pattern: '(?i)\bcome se\b', modalita: conta, massimo: 2, ambito: capitolo}
  - id: fischiare
    pattern: '(?i)\bfischi\w*|\bfischia\w*|\bfischio\b'
    modalita: conta
    massimo: 6
    ambito: libro
    consentito_in_capitoli: [10, 23, 35, "interludio VII", 39, epilogo]
    vietato_in_capitoli: [9, 17, 19]
    nota: "senso morale; ogni occorrenza fuori dall'elenco è KO"
  # Manuale 4.3 — immagini vietate (forme fisse)
  - {id: lama_letterale, pattern: '(?i)\blam[ae]\b', modalita: conta, massimo: 3, ambito: libro, nota: "solo la lama vera di un coltello; ogni occorrenza elencata per il controllo a vista"}
  - {id: lama_figurata, pattern: '(?i)\blam[ae] d[i\x27]\s*(luce|sole|sorriso|acqua|oro|argento)|\blama (d.oro|azzurra|bianca)', modalita: vieta}
  - {id: cuore_uccello, pattern: '(?i)cuore come un uccello in gabbia', modalita: vieta}
  - {id: cuore_martella, pattern: '(?i)\bcuore\b[^.!?]{0,40}\b(martell\w*|all.impazzata|in gola)', modalita: vieta}
  - {id: silenzio_piombo, pattern: '(?i)silenzio si fece piombo|silenzio (denso|assordante|di pietra|pesante)|silenzio che pes\w+|silenzio pesava', modalita: vieta}
  - {id: reliquia, pattern: '(?i)\breliqui[ae]\b', modalita: vieta}
  - {id: campo_sacro, pattern: '(?i)\b(altar[ei]|sacr[oaie]|religios[oaie])\b', modalita: avviso, nota: "vietato solo sugli oggetti; in chiesa è ammesso"}
  - {id: paura_cosi, pattern: '(?i)faceva più paura così|era questo a fare paura', modalita: vieta}
  - {id: battito_ciglia, pattern: '(?i)in un battito di ciglia', modalita: vieta}
  - {id: statue_persone, pattern: '(?i)statu[ae] di sale|come (una )?statu[ae]', modalita: vieta}
  - {id: statue_altre, pattern: '(?i)\bstatu[ae]\b', modalita: avviso}
  - {id: animale_gabbia, pattern: '(?i)come un animale in gabbia|come un cane bastonato|come una bestia', modalita: vieta}
  - {id: sangue_gelo, pattern: '(?i)il sangue mi si gelò|un brivido lungo la schiena|gelo nelle vene', modalita: vieta}
  - {id: tempo_fermo, pattern: '(?i)in quel preciso istante|il mondo si fermò|il tempo si fermò', modalita: vieta}
  - {id: occhi_ghiaccio, pattern: '(?i)occhi di ghiaccio|sorriso che non arrivava agli occhi', modalita: vieta}
  - {id: spezzo_dentro, pattern: '(?i)qualcosa si spezzò dentro di me|qualcosa dentro di me cambiò', modalita: vieta}
  - {id: acqua_nera, pattern: '(?i)come acqua nera|sentinelle nere|cassa armonica', modalita: vieta}
  - {id: ingranaggio, pattern: '(?i)\bingranagg\w*', modalita: avviso, nota: "vietato per il sistema criminale; ammesso per un motore"}
  # Manuale 4.4 — campo del cane
  - {id: campo_cane, pattern: '(?i)\bcane da tartufo\b|\bcan[ei]\b|\bguinzagl\w*|\bcollar[ei]\b', modalita: conta, massimo: 8, ambito: libro, nota: "«cane da tartufo» conta una volta"}
  - {id: cane_similitudine, pattern: '(?i)\bcome (un|i) can[ei]\b', modalita: vieta}
  # Manuale 4.5 — emozioni spiegate
  - {id: emozione_innominabile, pattern: '(?i)provai qualcosa che non sapevo nominare', modalita: vieta}
  # Manuale 5.1-5.4 — lingua e dialetto
  - {id: accento_decorativo, pattern: '\b\w*[àèéìíòóù]\w+\b', modalita: avviso, nota: "es. «Siéditi», «Avvicìnati»; controllo a vista"}
  - id: napoletano
    pattern: '(?i)\bguagli(ò|o\x27|one)\b|\bpiccerì\b'
    modalita: vieta
    consentito_in_capitoli: [2]          # don Tobia e Ciro (scaletta r. 55, bibbia r. 138-139)
    consentito_con_personaggi: ["don Tobia", Ciro]
    solo_dialogo: true
    nota: "l'elenco dei capitoli si ricalcola dalla scaletta: ogni capitolo che nomina don Tobia o Ciro"
  - id: calabrese
    pattern: '(?i)\bcumpà\b|\bfigghiolu\b'
    modalita: vieta
    consentito_con_personaggi: ["zi' Nardu", Saro]
    solo_dialogo: true
  - {id: beniami, pattern: '\bBeniamì\b', modalita: conta, massimo: 3, ambito: libro}
  - {id: dialetto_nel_racconto, pattern: '(?i)\b(uè|uagnò|uagnone|citte|mo\x27)\b', modalita: avviso, nota: "KO se fuori dal discorso diretto (riga che non inizia con «—»)"}
  - {id: dichiarativo_avverbio, pattern: '(?i)\b(disse|chiese|rispose)\s+(piano|\w+mente)\b', modalita: conta, massimo: 1, ambito: capitolo}
  - {id: dialogo_lineetta, pattern: '(?m)^(-|–|«)\s?', modalita: vieta, nota: "il dialogo si apre con «— »"}
  # Manuale 6 — sensibilità
  - {id: ago, pattern: '(?i)\bl.ago\b|\bago\b', modalita: conta, massimo: 3, ambito: libro}
  - {id: bucarsi, pattern: '(?i)\bbucar(si|mi|ti)\b|\bsi buca(va|vano)?\b|\bmi bucai\b|\bsi bucò\b', modalita: conta, massimo: 3, ambito: libro}
  - {id: droga_strumenti, pattern: '(?i)\b(cucchiaino|cucchiaio|laccio|fiamma)\b', modalita: avviso, nota: "vietati solo in primo piano sulla droga"}
  - {id: droga_dosi, pattern: '(?i)\b\d+([.,]\d+)?\s?(g|gr|grammi|mg|milligrammi)\b', modalita: avviso}
  - {id: sostanze_taglio, pattern: '(?i)\b(mannite|lattosio|stricnina|caffeina|lidocaina)\b', modalita: vieta}
  - {id: cariche_pubbliche, pattern: '(?i)\bil (sindaco|questore)\b', modalita: avviso, nota: "vietati in una scena di collusione"}
  # Manuale 7 — anacronismi (aggiunta)
  - {id: anacronismi, pattern: '(?i)\b(walkman|cellular[ei]|computer|scherm[oi]|cordless|porto container)\b', modalita: vieta}
```

**Voci che una regex non può decidere, e come si trattano**

| Regola | Perché la regex non basta | Trattamento |
|---|---|---|
| «lama» figurata (manuale 4.3) | «lama» può essere vera o figurata; il senso dipende dalla frase | forme fisse (`lama di luce`, `lama d'oro`…) → **vieta**; ogni altra «lama» → conteggio (max 3) **e** elenco per controllo a vista nel report |
| «cuore» che martella, batte all'impazzata, sta in gola | infinite varianti («il cuore mi saliva») | forme fisse → **vieta**; ogni «cuore» entro 40 caratteri da un verbo di movimento → **avviso** |
| silenzio denso, di pietra, che pesa | aggettivi e verbi variabili | forme fisse → **vieta**; ogni «silenzio» con aggettivo → **avviso** |
| campo sacro applicato agli oggetti | «altare» in chiesa è ammesso | **avviso** con la frase |
| «statue» per persone immobili | una statua vera è ammessa | «come una statua», «statue di sale» → **vieta**; il resto → **avviso** |
| «ingranaggio» per il sistema criminale | l'ingranaggio di un motore è ammesso | **avviso** |
| «come una bestia» e simili per esseri umani | il soggetto non è leggibile da regex | le similitudini fisse → **vieta** |
| schema vietato (manuale 4.6), metafora spiegata | è una struttura di paragrafo | **avviso** se una frase con «come» o «era» è seguita da una frase che comincia con «Era/Voleva dire/Significava» o da una conclusione con «sempre/mai/tutti»; controllo a vista |
| aforismi prestati al ragazzo (manuale 2.1) | serve il senso | conteggio dichiarato nell'intestazione + **avviso** sulle frasi al presente gnomico fuori dalle intrusioni |
| gesti di conteggio (manuale 3.6) | «contare» non è una parola sola | **avviso** su numerali seguiti da unità (passi, gradini, secondi, lire, mazzette) e sui verbi «contai/contava»; il numero vero lo dichiara il registro dei contatori |
| similitudini (manuale 4.1) | «come» ha molti usi | **avviso** su «come un/una/il/la», «sembrava», «pareva»; tetto controllato sul conteggio dei candidati |
| dialetto «in bocca a un barese» (manuale 5.3) | chi parla non è nel testo | `solo_dialogo` + capitoli consentiti dai personaggi in scaletta; il resto **avviso** |
| trascrizioni fonetiche > 5 parole | serve l'orecchio | **avviso** su sequenze di parole non riconosciute da Hunspell e non in `nomi_propri.txt` |
| persone reali, clan, boss | non c'è un elenco chiuso | controllo **manuale** nella checklist del capitolo |

Le voci in `avviso` non bloccano: finiscono in una tabella «da guardare» del report di capitolo, con capitolo, riga e frase.

#### Dichiarazioni nel capitolo

Ogni file di capitolo ha, sotto l'intestazione, una riga nascosta (in stampa la toglie `compila.py`):

```
## 12
*Bari — sabato 17 luglio*
<!-- zb: chiusura=G intrusioni=2 aforismi=0 -->
```

`capitolo.py` verifica:
- **chiusura**: una sigla tra G, I, O, B, F, S (la scaletta usa anche F, «fatto»); confronto con la sigla prevista in scaletta → **avviso** se diversa; sentenze (S) al massimo 8 nel libro e mai in due capitoli consecutivi (epilogo escluso) → **KO**; ultima riga di 1-2 parole → **KO**; ultima frase con «?» quando la sigla non è B → **avviso**;
- **intrusioni**: da 1 a 3, il cap. 10 a zero (`capitoli_a_zero`) → **KO** fuori dai limiti; conteggio delle ancore fuori dal discorso diretto → **avviso** se diverso dal numero dichiarato;
- **aforismi**: totale cumulato ≤ metà dei capitoli scritti (arrotondata per eccesso) → **KO** oltre; aforismi > intrusioni nello stesso capitolo → **KO** (stanno solo dentro un'intrusione).

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
| `verifica KDP fatta [AAAA-MM-GG]` | `kdp_verifica.py` | `motore/dati/kdp.yaml` (`ultima_verifica`) e `motore/dati/verifiche-kdp.md` (A.8) |
| `pacchetto` | `pacchetto.py` | `06-pubblicazione/`: scheda-amazon, quarta, brief-copertina, checklist, promemoria AI |

Nessun comando fa commit o push da solo: il salvataggio segue B.5.

### B.5 Regole fisse

1. **Tono.** Il vecchio testo di un libro è un registro dei fatti: non si commenta né si giudica, nei report come in chat.
2. **Proponi → approvo → applica.** Ogni modifica al testo o ai dati di un libro si propone, voce per voce; si applica solo dopo l'OK. Mai nuovi oggetti o persone in una scena senza richiesta.
3. **Metodo unico di conteggio.** Token separati da spazi; esclusi le righe che cominciano con «#» e i token senza lettere né cifre (lineette di dialogo, separatori, segni isolati). Niente `wc -w`, che cambia con la lingua di sistema. Ogni report dichiara il metodo.
4. **Precedenza.** Manuale del libro > procedura (motore e casa-editrice) > skill dell'autore. In caso di contrasto vince il manuale del libro e il report lo segnala.
5. **Ramo.** Si lavora solo sul ramo assegnato dalla sessione; `comune.py` lo legge da git. Il motore controlla che il libro attivo di quel ramo esista e si ferma se il ramo non è quello della sessione.
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
| 2b | `prove/libro-prova/`, `prove/attesi.yaml` (B.2.2) | libro di prova | ogni script, prima dei casi reali, dà esattamente gli esiti attesi |
| 3a | `PROCEDURA.md`, `CLAUDE.md`, `modelli/` (briefing, LEGGIMI, stato), `script/avvio.py`, `script/fase.py` (C.1, C.3, C.4) | Mister Provino: migrazione di C.6, ripartenza a G2 | `avvio.py` stampa la riga «Letto: …» e si ferma nei casi di C.4 |
| 3b | `script/capitolo.py`, `riciclo.py`, `date.py`, `continuita.py`, `revisione.py` (C.2, C.7, B.2.1) | Mister Provino, pagina campione e primo lotto | report di capitolo completo; regola della correzione unica |
| 4 | `script/compila.py`, `script/impagina.py`, `impaginazione/` | Kurgan | non regressione di B.6 punto 3 |
| 5 | `script/stile.py`, `dati/lista-nera.yaml` | Mister Provino, primi capitoli scritti | valori del registro dei contatori del manuale |
| 6 | `script/ortografia.py` | Kurgan | zero errori certi, come `controllo-ortografico.md` |
| 7 | `script/pacchetto.py`, `zb`, `README.md` | Kurgan | pacchetto completo; report KDP con le sole conferme dell'autore aperte |

Ogni passo: proposta → OK → codice → caso di prova → commit e push secondo B.5.

### B.8 Copia dei riferimenti in `motore/riferimenti/`

**Cosa si copia.** Da NGTAProtocol/casa-editrice, `origin/main` @ becd0e2, con `git show` (sola lettura):
- i 12 file di `.claude/skills/casa-editrice/riferimenti/` (da `01-mercato.md` a `12-lunghezze-e-struttura-capitoli.md`) → `motore/riferimenti/`;
- i 7 file di `.claude/skills/casa-editrice/modelli/` → `motore/riferimenti/modelli/`.

**Intestazione** aggiunta in testa a ogni file copiato, come prima riga, seguita da una riga vuota:

```
> Fonte: NGTAProtocol/casa-editrice main @ becd0e2, copiato il AAAA-MM-GG. Adattamenti: vedi motore/proposta-motore.md B.8.
```

Per questo, nei file copiati, ogni riga originale scende di 2 posizioni. I numeri di riga qui sotto sono quelli dell'originale.

**Adattamenti, uno per uno**

**Mod. 1 — `03-stesura.md` r. 12** (chiusure)
- Prima: `9. **Chiusura di capitolo**: interrompi sul massimo della domanda, non sulla risposta.`
- Dopo: `9. **Chiusura di capitolo**: chiudi su un gesto, un oggetto, una battuta o un'immagine concreta, non su una domanda. I tetti delle chiusure (sentenze, domande) li fissa il manuale del libro.`

**Mod. 2 — `12-lunghezze-e-struttura-capitoli.md` r. 6** (conteggio)
- Prima: `- Si conta in **parole** (comando `wc -w` sul file del capitolo, esclusi titoli e note).`
- Dopo: `- Si conta in **parole** con il metodo unico del motore (`motore/script/conta.py`): token separati da spazi; escluse le righe che cominciano con «#» e i token senza lettere né cifre. Non si usa `wc -w`, che cambia con la lingua di sistema.`

**Mod. 3 — `12-lunghezze-e-struttura-capitoli.md` r. 66** (conteggio)
- Prima: `- Dopo ogni capitolo conta le parole e aggiorna "Parole reali" e "Scarto".`
- Dopo: `- Dopo ogni capitolo conta le parole con il metodo unico e aggiorna "Parole reali" e "Scarto".`

**Mod. 4 — `05-critica-e-punteggio.md`, dopo r. 22** (lista nera unita alle immagini vietate del libro; si aggiunge una riga, nessuna si toglie)
- Prima (r. 22): `Aggiungi in lezioni.md ogni nuova espressione che l'autore segnala.`
- Dopo (r. 22 invariata, più una riga nuova): `Alla lista nera si sommano le immagini e le formule vietate del manuale del libro (in `libro.yaml`: `stile.immagini_vietate`, `stile.formule_contate`). `stile.py` le controlla insieme. In caso di contrasto vale il manuale del libro: un'espressione che il manuale ammette con un tetto segue il tetto, non il divieto.`

**Mod. 5 — `08-pubblicazione.md` r. 8** (corpo)
- Prima: `**Corpo**: eventuali parti ("Parte prima — titolo") e capitoli con titoli e numerazione uniformi.`
- Dopo: `**Corpo**: eventuali parti ("Parte prima — titolo") e capitoli con titoli e numerazione uniformi. Prologo, epilogo e interludi non hanno numero di capitolo quando il manuale del libro lo prevede.`

**Mod. 6 — `08-pubblicazione.md` r. 12** (sommario)
- Prima: `- Generalo SEMPRE dai titoli reali dei file in 04-manoscritto, mai a memoria, includendo parti, prologo, epilogo e pagine finali principali.`
- Dopo: `- Generalo SEMPRE dai titoli reali dei file in 04-manoscritto, mai a memoria, includendo parti, prologo, interludi (con il loro titolo, senza numero), epilogo e pagine finali principali.`

**Mod. 7 — `02-architettura.md` r. 39** (nuova, non era tra quelle già individuate: stessa questione della mod. 1)
- Prima: `… un capitolo = 1-4 scene, chiuso da un gancio (domanda, rivelazione, pericolo, decisione).`
- Dopo: `… un capitolo = 1-4 scene, chiuso da un gancio (gesto, oggetto, rivelazione, pericolo, decisione; la domanda solo se il manuale del libro la ammette).`

**Non modificati.**
- `05-critica-e-punteggio.md` r. 5 («le prime righe creano una domanda?») riguarda l'apertura, non la chiusura.
- `04-editing-sviluppo.md` r. 11 riguarda le prime 10 pagine.
- `modelli/registro-promesse.md` r. 3 usa «domanda» come tipo di promessa.
- I file `01`, `04`, `06`, `07`, `09`, `10`, `11` e i 7 modelli si copiano identici, salvo l'intestazione.

**Verifica della copia.** Un caso di prova confronta ogni file copiato con l'originale (`git show`). La differenza ammessa è solo l'intestazione più le 7 modifiche sopra; qualsiasi altra differenza è un KO.

---

## C. Funzionamento quasi automatico

Obiettivo: l'autore scrive solo il briefing e risponde «ok», «avanti», «correggi: …», «stato» o «prepara per revisione». Tutto il resto si legge da file: lo stato del libro, le fasi, i controlli e i punti di approvazione. Nessun prompt da incollare a ogni passo.

### C.1 Macchina a stati

**File:** `libri/<nome>/stato.yaml`, scritto solo da `motore/script/fase.py`.

```yaml
libro: mister-provino
ramo_ultimo_salvataggio: claude/mister-provino-espansione   # solo informativo, scritto da fase.py
fase: 2                        # 0-8, oppure "chiuso"
passo: pagina-campione         # sottopasso della fase
gate_in_attesa: voce           # null se nessun gate è aperto
lotto: {dimensione: 3, capitoli: []}   # fase 5
ultimo_capitolo_approvato: null
parole: {scritte: 0, obiettivo: 78000, metodo: unico}
documenti_approvati:           # percorso → sha256 e commit dell'approvazione
  02-bibbia/bibbia.md: {sha256: "3302e642cd67…", commit: 7692265}
avvisi_aperti:
  - {id: A1, fonte: bibbia, testo: "20 marche [PROPOSTA]"}
revisione_in_corso: null       # {documento, blocco, blocchi_totali, sha256}
push_in_sospeso: false
aggiornato: 2026-10-02T00:00:00Z
```

**Tabella delle fasi**

| Fase | Legge | Produce | Controlli automatici | Gate |
|---|---|---|---|---|
| 0 Avvio | `00-progetto/briefing.md`, `motore/modelli/` | cartelle `00-06`, `libro.yaml`, `stato.yaml`, `LEGGIMI.md`, file dai modelli | briefing completo (C.3); nome autore; ramo | **G0** domande (massimo 5, solo se mancano dati essenziali) e conferma di `libro.yaml` |
| 1 Bibbia | briefing, `libro.yaml`; registro dei fatti se c'è | `02-bibbia/bibbia.md` (personaggi, luoghi, cronologia, motivi con tetti) | nomi unici, età coerenti con la cronologia, ogni fatto canonico del briefing presente, marche [PROPOSTA] contate | **G1** bibbia |
| 2 Voce | bibbia, briefing (tono, riferimenti, divieti) | `03-architettura/manuale-di-stile.md`; `05-revisioni/pagina-campione.md` in 3 voci (stessa scena, circa 400 parole ciascuna) | frase media, dialogo %, formule e immagini vietate sulle tre voci | **G2** scelta della voce; il manuale si completa con la voce scelta |
| 3 Continuità | bibbia, manuale | `02-bibbia/continuita.md`: cronologia giorno per giorno, date con giorno della settimana, età per anno, cifre (soldi, distanze, durate) | `date.py`: giorno della settimana dal calendario reale; età da data di nascita; somme e durate | **G3** decisioni di continuità |
| 4 Scaletta | bibbia, manuale, continuità | `03-architettura/scaletta.md`, `03-architettura/piano-parole.md` | somma budget = obiettivo ± 5%; nessun capitolo sotto il minimo; parti; interludi; date in ordine | **G4** scaletta e piano parole |
| 5 Stesura | `LEGGIMI.md`, manuale, scaletta (riga del capitolo), continuità, capitoli precedenti | `04-manoscritto/NN-*.md`, `06-diagnostica/capitoli/NN.md` | C.2 per ogni capitolo | **G5** a ogni lotto: primo lotto di 3 capitoli, poi lotti di N scelti dall'autore |
| 6 Assemblaggio | tutti i capitoli, `libro.yaml` | `05-output/*-completo.md`, `*-completo.pdf`, `*-rivisto.pdf`, `*-DEFINITIVO.pdf` | `verifica_pdf.py`: indice contro pagine, margini, font, pagine pari | **G6** PDF |
| 7 Controlli finali | manoscritto, continuità | `06-diagnostica/controlli-finali.md` | durate, ortografia (Hunspell), coerenza nomi e date, tetti sull'intero libro, anti-riciclo | **G7** esiti e proposte di correzione |
| 8 Pacchetto KDP | `libro.yaml`, PDF, `kdp.yaml` | `06-pubblicazione/`: scheda, quarta, brief copertina, `conformita-kdp.md`, promemoria AI | `conformita_kdp.py` (A.4) | **G8** pacchetto; resta aperto finché ci sono KO o conferme dell'autore mancanti |

**Cosa mostra ogni gate**

| Gate | Cosa mostro | Formato |
|---|---|---|
| G0 | domande mancanti (al massimo 5), poi `libro.yaml` | elenco numerato; poi il file intero in blocchi |
| G1 | bibbia intera e riepilogo dei controlli (nomi, età, fatti canonici, [PROPOSTA]) | blocchi di circa 120 righe, «Blocco N di M, righe X-Y»; riepilogo in fondo all'ultimo blocco |
| G2 | le tre voci della pagina campione affiancate, con le misure (frase media, dialogo %) | un blocco per voce, poi una tabella |
| G3 | tabella delle date, età e cifre con i dubbi in cima | blocchi di circa 120 righe |
| G4 | scaletta e piano parole | blocchi di circa 120 righe; totali in fondo |
| G5 | per ogni capitolo del lotto: testo intero e report dei controlli | blocchi di circa 120 righe per capitolo; tabella dei controlli dopo l'ultimo blocco |
| G6 | indice con le pagine, margini, font, numero di pagine, sha256 del PDF | tabella; il PDF si invia come file |
| G7 | esiti dei controlli e proposte di correzione voce per voce | tabella con file e riga |
| G8 | `conformita-kdp.md` e promemoria AI | blocchi; righe KO in cima |

**Significato delle risposte**

| Risposta | Effetto |
|---|---|
| `ok` | Approva il documento del gate aperto: registro sha256 e commit in `documenti_approvati`, chiudo il gate, commit e push, passo al passo successivo e mi fermo al gate seguente. `ok` vale solo se il documento è stato mostrato per intero; se ci sono blocchi non ancora mostrati chiedo prima di mostrarli. |
| `avanti` | Mostra il blocco successivo del documento in revisione. Non approva nulla. Dopo l'ultimo blocco scrivo: «Fine del documento. Scrivi ok o correggi: …». |
| `correggi: …` | Applico solo la correzione descritta, rieseguo i controlli, mostro le righe cambiate (prima e dopo) e resto allo stesso gate. Nessun'altra modifica. |
| `stato` | Mostra `stato.yaml` in forma leggibile: fase, gate, lotto, parole scritte/obiettivo, avvisi aperti, ultimo commit, allineamento con origin. Non scrive nulla. |
| `prepara per revisione` | Vedi C.7. Non scrive nulla. |
| `ok, lotti da N` | Al gate G5 approva il lotto e fissa la dimensione dei lotti successivi. |

Qualunque altra frase è una domanda: rispondo senza cambiare stato.

### C.2 Stesura di un capitolo

Procedura meccanica, uguale per ogni capitolo:

1. **Avvio:** `avvio.py` (C.4). Leggo `LEGGIMI.md`, la riga del capitolo nella scaletta, il budget nel piano parole, le voci di continuità che il capitolo tocca, il manuale e il capitolo precedente.
2. **Scrittura** del capitolo in `04-manoscritto/NN-slug.md`.
3. **Controlli** con `motore/script/capitolo.py NN`, che esegue in un colpo solo:
   - parole con il metodo unico, rispetto a budget e minimo;
   - frase media e dialogo %;
   - formule contate (per capitolo e cumulate sul libro);
   - immagini vietate e lista nera;
   - similitudini rispetto al tetto per parole;
   - gesti di conteggio rispetto al tetto per capitolo;
   - anti-riciclo a 7 parole (`riciclo.py`): ogni sequenza di 7 parole uguale al registro dei fatti o a un capitolo già scritto, con file e riga;
   - date e giorni della settimana (`date.py`) contro `continuita.md`;
   - nomi: ogni nome proprio deve esistere in bibbia;
   - tetti dei motivi e delle chiusure (sentenze, domande).
4. **Report** in `06-diagnostica/capitoli/NN.md`: tabella dei controlli con valore, soglia ed esito, più la posizione di ogni KO.
5. **Commit e push** (capitolo e report), poi `stato.yaml` aggiornato con le parole scritte.

**Regola della correzione unica.** Se un controllo numerico fallisce:
- faccio **una sola** correzione mirata sul punto indicato e rieseguo i controlli;
- se fallisce ancora mi **fermo** e scrivo quale controllo, quale valore, quale soglia, file e righe;
- non riscrivo in ciclo, non allento le soglie, non approvo da solo. Il capitolo resta al gate G5 come «da decidere».

### C.3 Briefing

**`motore/modelli/briefing.md`**, pensato per il telefono: una voce per riga, «Campo: valore»; le voci multiple con un trattino.

```markdown
# Briefing

Titolo di lavoro:
Autore: F.R. Faraone
Genere:
Lettore:
Lunghezza (parole):
Persona e tempo:

## Idea (massimo 5 righe)

## Tono e voce desiderati

## Personaggi chiave
- Nome — ruolo — età — una riga

## Fatti canonici
- 

## Cose da non cambiare
- 

## Divieti
- 

## Riferimenti
- 
```

**Verifica di completezza** (`avvio.py`, fase 0). Prima di passare alla fase 1 controlla:

| Voce | Obbligatoria | Controllo |
|---|---|---|
| Titolo di lavoro, Autore | sì | non vuoti |
| Genere | sì | nella tabella di 12-lunghezze, altrimenti avviso |
| Lunghezza | sì | numero tra 40.000 e 180.000 |
| Idea | sì | da 1 a 5 righe |
| Personaggi chiave | sì | almeno 1, con nome e ruolo |
| Lettore, tono e voce, persona e tempo | no | se mancano, la fase 2 propone le tre voci |
| Fatti canonici, cose da non cambiare, divieti, riferimenti | no | se ci sono, finiscono in bibbia e manuale come vincoli |

Se manca una voce obbligatoria: al massimo 5 domande, solo su quelle voci, al gate G0. Le altre voci mancanti non generano domande.

### C.4 Avvio obbligatorio

**`CLAUDE.md` alla radice di ZeusBot** (testo completo):

```markdown
# ZeusBot — regole di avvio

Prima di toccare qualunque file:
1. Leggi `motore/PROCEDURA.md`.
2. Leggi `libri/libro-attivo.md` e il `LEGGIMI.md` del libro attivo.
3. Esegui `python3 motore/script/avvio.py` e riporta la sua riga «Letto: …».
   Se avvio.py si ferma, fermati anche tu e riporta il motivo.

Precedenza: manuale del libro > procedura del motore > skill dell'autore.
In caso di contrasto vince il manuale del libro; segnalalo nel report.

Metodo: proponi → l'autore approva → applica. Mai approvare da solo.
Risposte dell'autore: ok, avanti, correggi: …, stato, prepara per revisione
(significato in `motore/PROCEDURA.md`, sezione gate).

Ramo: solo quello assegnato dalla sessione (letto da git, non da file).
Se il checkout è su un altro ramo, fermati.

Tono: il vecchio testo di un libro è un registro dei fatti,
non va commentato né giudicato.

Salvataggio a ogni passo: git add, commit, push, git status -sb, git log -1.
Se il push fallisce o un file non si salva: fermati e riporta l'errore.
Non dire «fatto» se non è su origin. Resoconto con hash, file,
parole/pagine e «branch allineato a origin: sì/no».

Nel testo pushato non vanno identificativi di modello.
```

**`LEGGIMI.md` di libro** (modello `motore/modelli/LEGGIMI.md`):

```markdown
# <Titolo> — LEGGIMI

Ramo: letto da git all'avvio (non scritto qui)
Fase: <n> — <nome>; gate in attesa: <gate>
Ultimo capitolo approvato: <NN>

Da leggere a ogni avvio (in quest'ordine):
1. libro.yaml
2. stato.yaml
3. <manuale>
4. <documenti della fase corrente>

Decisioni fisse (non si toccano senza richiesta esplicita):
- <elenco>

Non toccare: <file o cartelle>
Avvisi aperti: vedi stato.yaml
```

Il LEGGIMI lo aggiorna `fase.py` a ogni gate chiuso. L'elenco delle decisioni fisse si scrive solo con un «ok».

**Libro attivo con due romanzi.**
- Ogni ramo ha il suo `libri/libro-attivo.md`, con il nome del libro di quel ramo.
- Il ramo non è scritto in nessun file: `comune.py` lo legge da git.
- `avvio.py` controlla che il libro indicato in `libro-attivo.md` esista su quel ramo e abbia `libro.yaml`; se non c'è si ferma: «Sul ramo X il libro attivo Y non ha libro.yaml».
- Su `claude/mister-provino-espansione` oggi `libro-attivo.md` dice `kurgan-giorgi`: va cambiato in `mister-provino` (passo della migrazione, C.6).

**`motore/script/avvio.py`**

Cosa stampa:
1. libro, ramo, ultimo commit (hash breve e messaggio), allineamento con origin;
2. fase, passo, gate in attesa, ultimo capitolo approvato, parole scritte/obiettivo;
3. i file da leggere per la fase corrente, ciascuno con righe e sha256 (12 caratteri);
4. avvisi aperti;
5. in fase 8: età della verifica delle direttive KDP.

Quando si ferma (codice d'uscita diverso da zero):
- checkout su un ramo diverso da quello della sessione, o libro attivo senza `libro.yaml`;
- modifiche non salvate nel checkout, o ramo indietro rispetto a origin;
- `stato.yaml` mancante o non valido;
- sha256 di un documento approvato diverso da quello registrato (modificato fuori procedura);
- in fase 0: briefing incompleto (C.3);
- `push_in_sospeso: true` (C.5).

**Marker di sessione.** Quando `avvio.py` termina senza errori scrive `.zb/letto-<session_id>` con la data, il commit e gli sha256 dei file letti. `.zb/` va in `.gitignore`. Il `session_id` lo deposita in `.zb/sessione-corrente` l'hook SessionStart. Se non c'è un hook, `avvio.py` usa un identificativo locale e lo dichiara.

**Frase di conferma** prima di ogni scrittura (stampata da `avvio.py`, ripetuta da me):

```
Letto: libro.yaml (54 righe, sha256 …), stato.yaml (31 righe, sha256 …),
03-architettura/manuale-di-stile.md (269 righe, sha256 f460afa60d65), …;
ultimo commit a8a69e1 «…»; fase 2, gate voce.
```

**Hook PreToolUse sul manoscritto (solo proposta, non creato)**

Versione presente nel container: **Claude Code 2.1.287**. Gli hook `SessionStart` e `PreToolUse` sono funzioni documentate di Claude Code:
- ricevono su stdin un JSON con `session_id`, `tool_name` e `tool_input`;
- un `PreToolUse` che esce con codice 2 blocca lo strumento e il messaggio su stderr torna al modello;
- `$CLAUDE_PROJECT_DIR` indica la radice del repo.

In questa sessione non l'ho provato, perché non l'ho creato.

`.claude/settings.json` proposto:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command",
        "command": "python3 \"$CLAUDE_PROJECT_DIR\"/motore/script/hook_sessione.py" } ] }
    ],
    "PreToolUse": [
      { "matcher": "Write|Edit|MultiEdit|NotebookEdit|Bash",
        "hooks": [ { "type": "command",
          "command": "python3 \"$CLAUDE_PROJECT_DIR\"/motore/script/hook_manoscritto.py" } ] }
    ]
  }
}
```

- `hook_sessione.py` scrive il `session_id` in `.zb/sessione-corrente`. Con `source: compact` (contesto compattato) cancella il marker, così dopo una compattazione bisogna rileggere.
- `hook_manoscritto.py` ha due modalità, scelte in `motore/dati/hook.yaml` (`modalita: avviso | blocco`):
  - **avviso** (iniziale): se il percorso è sotto `libri/*/04-manoscritto/` e manca `.zb/letto-<session_id>`, stampa «ATTENZIONE: avvio.py non eseguito in questa sessione; scrittura nel manoscritto non verificata» ed esce con 0, quindi **non blocca**. Ogni avviso finisce anche in `.zb/avvisi-hook.log`;
  - **blocco**: stesso controllo, ma esce con codice 2 e il messaggio «Esegui motore/script/avvio.py prima di scrivere nel manoscritto».

**Passaggio da avviso a blocco.** Solo dopo una prova superata, in una cartella temporanea fuori dal repo (per esempio `/tmp/zb-prova-hook/libri/prova/04-manoscritto/prova.md`):
1. senza marker: Write, Edit e i comandi Bash dei casi della tabella qui sotto. Atteso: blocco dove previsto;
2. con marker: le stesse operazioni. Atteso: nessun blocco;
3. scritture fuori dal manoscritto: mai bloccate;
4. hook con un errore volontario: per i percorsi fuori dal manoscritto lascia passare.

L'esito si mostra in una tabella. Il passaggio a `modalita: blocco` è un commit a parte, dopo il tuo «ok».

**Rilevamento delle scritture via Bash: scenari di errore**

Il comando Bash arriva all'hook come testo. L'hook lo considera una scrittura nel manoscritto se contiene `04-manoscritto` insieme a un operatore di scrittura: `>`, `>>`, `tee`, `sed -i`, `perl -i`, `mv`, `cp`, `rm`, `truncate`, `git checkout --`, `git restore`, `python`.

| # | Scenario | Tipo di errore | Cosa fa il sistema |
|---|---|---|---|
| 1 | `grep -n x libri/mp/04-manoscritto/01.md > /tmp/out.txt` (lettura, con redirezione verso un altro file) | falso blocco | L'hook guarda dove punta la redirezione: se il bersaglio di `>` non è in `04-manoscritto` lascia passare. In modalità avviso non blocca comunque. |
| 2 | `python3 motore/script/capitolo.py 01` (legge il manoscritto, non lo nomina) | nessun errore | Lascia passare: il percorso non compare. |
| 3 | `python3 -c "open('libri/mp/04-manoscritto/01.md','w')…"` | rilevato | Blocca (o avvisa): compaiono `python` e il percorso. |
| 4 | Uno script che scrive nel manoscritto senza nominarlo nel comando (`python3 /tmp/s.py`) | falso permesso | Non rilevabile dall'hook. Lo copre `avvio.py` al passo successivo: lo sha256 di un capitolo approvato cambiato fuori procedura ferma il lavoro (C.4). |
| 5 | Percorso costruito con variabili (`D=libri/mp/04-manoscritto; echo x > $D/01.md`) | falso permesso | Non rilevabile con certezza. L'hook cerca anche `04-manoscritto` nelle assegnazioni di variabili dello stesso comando; il resto lo copre il controllo sha256 di `avvio.py`. |
| 6 | `cd libri/mp/04-manoscritto && sed -i … 01.md` | rilevato | Blocca: `04-manoscritto` e `sed -i` nello stesso comando. |
| 7 | `cd libri/mp/04-manoscritto` in un comando precedente, poi `sed -i … 01.md` | falso permesso | Non rilevabile, perché il comando non nomina la cartella. Lo copre il controllo sha256 di `avvio.py`. |
| 8 | `git commit` o `git push` con file del manoscritto in stage | falso blocco evitato | `git add/commit/push/status/log/diff` non sono operatori di scrittura: lascia passare. |
| 9 | `git checkout -- libri/mp/04-manoscritto/01.md` o `git restore …` | rilevato | Blocca (o avvisa): sovrascrive il capitolo. |
| 10 | `cp libri/mp/04-manoscritto/01.md /tmp/copia.md` (copia in uscita) | falso blocco | L'hook guarda l'ultimo argomento di `cp`/`mv`: se la destinazione è fuori dal manoscritto lascia passare. `mv` con sorgente nel manoscritto invece blocca, perché toglie il file. |
| 11 | `cat libri/mp/04-manoscritto/*.md \| wc -w` | nessun errore | Lascia passare: nessun operatore di scrittura. |
| 12 | Nome di un file che contiene `04-manoscritto` fuori da `libri/*/` (per esempio nella proposta) | falso blocco | L'hook richiede il percorso completo `libri/<nome>/04-manoscritto/`: lascia passare. |
| 13 | L'hook stesso va in errore (JSON illeggibile, Python mancante) | falso blocco o falso permesso | In modalità avviso lascia sempre passare e lo scrive nel log. In modalità blocco blocca solo se il testo contiene `libri/` e `04-manoscritto`, altrimenti lascia passare. |
| 14 | Contesto compattato: il marker viene cancellato (`source: compact`) | blocco voluto | Il messaggio chiede di rieseguire `avvio.py`; dopo la rilettura si procede. |

Rischi che restano:
- **Garanzia:** l'hook è una protezione in più, non una garanzia. La regola resta in `CLAUDE.md` e in `PROCEDURA.md`, e il controllo sha256 di `avvio.py` copre i casi 4, 5 e 7.
- **Portata:** `.claude/settings.json` nel repo vale per ogni sessione su quel ramo e su ogni ramo in cui venga unito (C.8).
- **Comandi eseguiti:** gli hook eseguono comandi con i permessi della sessione. Lo script deve solo leggere stdin, il marker e `hook.yaml`.
- **Marker:** `.zb/` va in `.gitignore`, altrimenti il marker finisce in un commit. Un marker di un'altra sessione non vale, perché il nome contiene il `session_id`.

### C.5 Sessioni

**Ripresa dopo un'interruzione**, solo da file:
1. `avvio.py` legge `stato.yaml`: fase, passo, gate, lotto, `revisione_in_corso`.
2. Se ci sono modifiche non salvate nel checkout (sessione caduta a metà), si ferma, mostra quali file e quante righe e chiede «tieni» o «scarta». Non scarta nulla da solo.
3. Se il ramo locale è avanti rispetto a origin, prova un solo push. Se riesce, prosegue; se fallisce, si ferma (punto seguente).
4. Se c'era una revisione in corso, riparte dal blocco indicato in `revisione_in_corso`, dopo aver verificato che lo sha256 del documento sia lo stesso.
5. Il riepilogo di ripresa è la frase «Letto: …» più fase e gate. Nessun riassunto a memoria della conversazione precedente.

**Se la sessione non può pushare:**
- mi fermo subito e riporto il messaggio d'errore esatto di `git push`;
- non scrivo il capitolo successivo e non apro un nuovo gate sopra lavoro non pushato;
- il commit resta locale. Il container della sessione è temporaneo: il lavoro non pushato si perde quando il container viene chiuso, e lo dico esplicitamente;
- non provo altri rami, non creo tag e non forzo il push;
- `stato.yaml` non può segnare il problema su origin. Lo segno nel resoconto in chat con l'hash del commit locale non pushato.

### C.6 Migrazione dei due romanzi

| | Kurgan/Giorgi | Mister Provino |
|---|---|---|
| Ramo | `claude/kurgan-giorgi-thriller-3f6mfq` | `claude/mister-provino-espansione` |
| Fase nel motore | `chiuso` dopo la fase 7 (PDF DEFINITIVO); fase 8 non avviata | fase 2, passo `pagina-campione`, gate G2 |
| File che servono subito | `stato.yaml`, `LEGGIMI.md`, `libro.yaml` (sul suo ramo) | `stato.yaml`, `LEGGIMI.md`, `libro.yaml`; `libri/libro-attivo.md` → `mister-provino` |
| Avvisi iniziali | formato A5 da verificare su KDP; «Felice Faraone» in `00-progetto/stato.md` r. 4, `02-bibbia/bibbia.md` r. 4, `01-mercato/mercato.md` r. 3; direttive KDP mai verificate | 20 marche [PROPOSTA] in bibbia, 4 nel manuale, 3 in scaletta; incongruenza n. 25 aperta per istruzione; manuale r. 75 «Da compilare dopo l'approvazione della pagina campione» |

**Kurgan/Giorgi.** Nessun file esistente cambia. I tre file nuovi si aggiungono con un commit sul suo ramo, dopo il tuo «ok». In `documenti_approvati` vanno gli sha256 attuali di manoscritto, bibbia, manuale e PDF DEFINITIVO (`fe460844…`), con il commit d31e84c.

**Mister Provino: ripartenza senza rifare il lavoro.**
- I documenti delle fasi 3b-3f del libro sono già su origin (commit 7692265). Nel motore li registro come approvati con il loro sha256:
  - briefing `a2c2e8ded919`
  - bibbia `3302e642cd67`
  - manuale `f460afa60d65`
  - scaletta `50a952d18b02`
  - incongruenze `9f0c81e3d9b9`
  - registro dei fatti `78afbc2ca68d`
- Corrispondenza con le fasi del motore:
  - bibbia → fase 1, fatta;
  - manuale → fase 2, fatta salvo la pagina campione;
  - incongruenze e bibbia §10 → fase 3, fatta salvo la n. 25;
  - scaletta → fase 4, fatta, con 3 [PROPOSTA].
- Il libro riparte da **fase 2, pagina campione in 3 voci (G2)**, l'unico passo mancante prima della stesura.
- Dopo G2 non rifaccio le fasi 3 e 4. Apro un solo gate di conferma che mostra l'elenco dei documenti con sha256 e le marche [PROPOSTA] ancora aperte, non il testo intero. Con «ok» si passa alla fase 5, primo lotto di 3 capitoli.
- Le marche [PROPOSTA] restano avvisi: si chiudono quando un capitolo le tocca, con un «ok» sulla singola voce.
- Prima della fase 5 manca il piano parole come file a sé (`03-architettura/piano-parole.md`). Si ricava dalla tabella della scaletta senza cambiare numeri e si mostra al gate di conferma.

### C.7 Secondo lettore

Gate in cui suggerisco una lettura fuori dalla sessione, prima dell'«ok»:

| Gate | Documento | Perché |
|---|---|---|
| G1 | bibbia | tutti i fatti successivi dipendono da qui |
| G2 | pagina campione e manuale | la voce non si cambia dopo la stesura |
| G4 | scaletta e piano parole | ordine e lunghezze dei capitoli |
| G5, primo lotto | primi tre capitoli | prova della voce su pagine vere |

Al gate scrivo: «Consigliata una lettura fuori sessione. Scrivi "prepara per revisione" per avere il documento in blocchi pronti da incollare.»

**«prepara per revisione»** (`revisione.py`, sola lettura):
- mostra il documento in blocchi di circa 120 righe, tagliati a fine paragrafo;
- ogni blocco si apre con «<Titolo> — <documento> — Blocco N di M, righe X-Y — sha256 <12 caratteri>»;
- testo puro, senza numeri di riga né commenti;
- a ogni «avanti» passa al blocco successivo;
- le tue note tornano come «correggi: righe X-Y, …», applicate secondo C.1;
- se il documento cambia durante la revisione, lo sha256 diverso lo segnala e la revisione riparte dal blocco 1.

### C.8 Come il motore arriva a tutti i libri

**Situazione verificata il 2026-10-02 con `git ls-remote --symref origin HEAD`:**
- in ZeusBot **non esiste un ramo `main`**;
- il ramo principale (HEAD di GitHub) è **`claude/claude-rc-4umw8n`**, ultimo commit 28560a6 del 2026-09-24. Contiene solo `.gitignore` e `ghimoney/`, niente `libri/`;
- `claude/mister-provino-espansione` è 289 commit avanti al principale e 0 indietro; `claude/kurgan-giorgi-thriller-3f6mfq` è 302 avanti e 0 indietro. Partono entrambi da 28560a6.

**Problema.** Una pull request di `claude/mister-provino-espansione` verso il principale porterebbe con sé anche tutta `libri/`: i due libri e la versione vecchia di Kurgan/Giorgi che sta su quel ramo.

**Proposta.**
1. Creo un ramo solo per il motore, per esempio `claude/motore`, partendo dal principale (28560a6), e ci copio **solo** `motore/` (più `CLAUDE.md` e `.claude/settings.json` quando esisteranno). Nessun file di `libri/`. Creare questo ramo richiede il tuo permesso esplicito, perché è un ramo diverso da quello assegnato.
2. Tu apri su GitHub la pull request `claude/motore` → `claude/claude-rc-4umw8n` e fai il merge.
3. Unisco il principale nei rami dei libri con `git merge` (commit di merge, nessuna riscrittura della storia): prima `claude/kurgan-giorgi-thriller-3f6mfq`, poi `claude/mister-provino-espansione`. Il principale non ha `libri/`, quindi il merge aggiunge solo `motore/` e non tocca i libri. Su `claude/mister-provino-espansione` `motore/` esiste già con la stessa storia di file, quindi il merge non dà conflitti, oppure dà conflitti solo sui file cambiati nel frattempo.
4. I libri futuri: il ramo del nuovo libro parte dal principale, quindi ha già il motore.
5. Gli aggiornamenti del motore si fanno su `claude/motore`, poi PR verso il principale, poi merge del principale nei rami dei libri.

**Se non puoi fare il merge sul principale** (ramo protetto, permessi, o preferisci non toccarlo):
- **Alternativa A:** unisco `claude/motore` direttamente in ciascun ramo di libro con `git merge`. Funziona senza il principale. Ogni aggiornamento del motore va unito in ogni ramo, uno per uno.
- **Alternativa B:** copio la cartella con `git checkout origin/claude/motore -- motore/` e un commit su ciascun ramo di libro. È più semplice, ma le copie si separano nel tempo: va annotato in `stato.yaml` il commit del motore usato (`motore_commit`), e `avvio.py` avvisa se è più vecchio di quello di `claude/motore`.
- In tutti i casi: niente force push, niente rebase dei rami dei libri, niente tag. Se un push fallisce mi fermo e riporto l'errore.
- Finché il motore non è su un ramo di libro, per quel libro si usa da un checkout separato del ramo del motore, con `--libro` e `--pdf` che puntano al checkout del libro (come per il caso di prova di A.7).


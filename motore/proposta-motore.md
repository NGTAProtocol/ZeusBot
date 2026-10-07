# Motore editoriale — proposta

Stato: **proposta approvata dall'autore** (2026-10-02). Nessun file del motore è ancora stato creato oltre a questo; la costruzione segue B.7.

**Principio.** Il motore è una fabbrica vuota e generica, per qualsiasi romanzo o manoscritto di qualsiasi genere. Contiene solo: procedura, script, modelli vuoti, profili di genere, dati KDP e un mini-libro inventato per le prove. **Non contiene nessun libro reale**, nemmeno come esempio o caso di prova. Il libro si indica a ogni comando con un percorso; tutto ciò che il motore produce per un libro va nella cartella di quel libro, e il motore non scrive in nessuna cartella di libro che non gli sia stata indicata.

Parti:
- **A.** Direttive KDP.
- **B.** Il motore: inventario, albero, profili, `libro.yaml`, ingresso, regole, ordine di costruzione, riferimenti, separazione.
- **C.** Funzionamento quasi automatico: macchina a stati, stesura, briefing, avvio, sessioni, secondo lettore, distribuzione.

Fonte delle direttive e dei riferimenti: NGTAProtocol/casa-editrice, `origin/main` @ becd0e2. Si legge una volta sola per copiare i file in `motore/riferimenti/` (B.8); dopo la copia il motore non la legge più e non ci scrive mai.

Nei comandi e nei percorsi, `<libro>` è la cartella del libro indicata dall'autore (B.4).

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
zb kdp <libro> [--pdf <percorso>] [--carta crema|bianca] [--bleed]
```

Legge da `libro.yaml` titolo, `sottotitolo`, `serie` ed `ebook` (B.3), poi `06-pubblicazione/scheda-amazon.md`, `manoscritto-finale.md`, `cartaceo.pdf` (o `--pdf`), `ebook.docx` se c'è, `06-pubblicazione/conferme-autore.yaml` e `motore/dati/kdp.yaml`. Scrive `<libro>/06-pubblicazione/conformita-kdp.md`: in testa data, hash del PDF, stato della verifica; poi una riga **OK/KO** con la **prova** (il testo o il valore esatto controllato) e gli eventuali **avvisi** per ognuna delle sezioni 1-15. Un controllo lasciato all'autore e non confermato è **KO** con nota «da confermare dall'autore» (11-direttive r. 76). Codice d'uscita: 0 tutto OK; 1 almeno un KO; 2 verifica direttive scaduta.

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

### A.7 Primo caso di prova: il PDF del mini-libro

Il primo caso di prova di `verifica_pdf.py` e `conformita_kdp.py` è il PDF del mini-libro inventato di `motore/prove/` (B.2.2), generato dallo stesso motore. Nessun PDF di libri reali.

| Controllo | Atteso (da `prove/attesi.yaml`) |
|---|---|
| Pagine | il numero fissato alla prima generazione approvata; pari |
| Margine interno | ≥ max(tabella KDP per numero di pagine, `margini_mm.interno_scelto`) |
| Margini esterni | ≥ i valori di `libro.yaml` e ≥ 0,25" |
| Font | tutti incorporati, nessun Type3 |
| Autore | `Author` del PDF = `autore` di `libro.yaml` = frontespizio |
| Formato | quello di `libro.yaml`; AVVISO se non tra i formati citati e `formato_confermato_kdp: false` |
| Parole | conteggio con il metodo unico uguale al valore in `attesi.yaml` |

Il numero di pagine e lo sha256 del PDF si fissano in `attesi.yaml` solo dopo la prima generazione, con l'«ok» dell'autore: da lì ogni cambiamento è una regressione da spiegare.

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

File per libro: `<libro>/06-pubblicazione/conferme-autore.yaml`. Lo scrive solo l'autore, oppure il motore su sua risposta esplicita.

```yaml
isbn: kdp_gratuito              # sezione 10
formato_confermato_kdp: false   # sezione 11: true quando l'autore ha verificato su KDP
                                # che il formato del PDF è accettato. Con false: AVVISO, non KO.
carta: crema
dichiarazione_ai: da_fare       # sezione 13: "fatta" dopo la pubblicazione
copertina_verificata: false     # sezione 9
categorie_coerenti: false       # sezione 8
contenuti_verificati: false     # sezione 14
recensioni_regolari: false      # sezione 15
note: ""
```

Le voci a `false` delle sezioni 8, 9, 14 e 15 danno KO «da confermare dall'autore» (A.4). `formato_confermato_kdp` dà solo AVVISO.

---

## B. Il motore

### B.1 Inventario: cosa si riusa

Solo tecniche e testi generici. Nessun file di un libro entra nel motore.

| Cosa | Da dove | Decisione |
|---|---|---|
| Composizione del manoscritto da capitoli Markdown, con parti, indice, pagina copyright e separatore di scena | tecnica già usata nel repository (script fuori da `motore/`) | **riusare con modifiche**: si riscrive generico in `compila.py`; titolo, autore, parti, copyright e separatore vengono da `libro.yaml` |
| Impaginazione md → HTML → PDF con Chromium (Playwright), numeri di pagina stampati con PyMuPDF, metadati Title/Author | tecnica già usata nel repository | **riusare con modifiche**: si riscrive generico in `impagina.py`; formato, margini, font e numerazione da `libro.yaml` |
| Font statici ricavati con fontTools da un font variabile, per evitare i font Type3 nel PDF | tecnica già usata | **riusare la tecnica**: i file di `motore/stampa/font/` si scaricano dalle fonti ufficiali con licenza OFL (B.2.3), mai da cartelle di libri |
| Misura dei margini con `pdftotext -bbox`, font con `pdffonts`, pagine con `pdfinfo` | metodo provato in questa sessione | **riusare** in `verifica_pdf.py` |
| Controllo ortografico con Hunspell it_IT (`-i utf-8`) | metodo già usato | **riusare** in `ortografia.py`, con le parole ammesse del libro |
| Metodo unico di conteggio (token separati da spazi; esclusi i titoli Markdown e i token senza lettere né cifre) | metodo già usato | **riusare** in `conta.py` come metodo predefinito |
| Riferimenti 01-12 e modelli di casa-editrice | casa-editrice main @ becd0e2 | **riusare**: copiati in `motore/riferimenti/` (B.8) |
| `SKILL.md` di casa-editrice | casa-editrice | **non copiare**: la sequenza delle fasi è riscritta in C.1 e finisce in `motore/PROCEDURA.md` |
| Report delle fasi di un libro, documenti di un libro, PDF di un libro | cartelle dei libri | **non riusare**: restano nei libri |

### B.2 Albero di `motore/`

```
motore/
  proposta-motore.md        questo file (esiste)
  PROCEDURA.md              fasi, gate, comandi, regole fisse (C.1-C.6)      da scrivere
  README.md                 come si usa il motore                            da scrivere
  zb                        lanciatore: zb <comando> <libro> [argomenti] (B.4)  da scrivere
  profili/                  default per genere (B.6)                          da scrivere
    thriller.yaml  giallo.yaml  romance.yaml  narrativa-letteraria.yaml
    fantasy.yaml  fantascienza.yaml  young-adult.yaml
  riferimenti/              copia di casa-editrice main @ becd0e2 (B.8)       da copiare
    01-mercato.md … 12-lunghezze-e-struttura-capitoli.md   12 file, 4 resi parametrici
    modelli/                lezioni, personaggio, registro-promesse, scheda-scena,
                            stato, struttura-capitolo, style-sheet (7 file, invariati)
  modelli/                  modelli vuoti per un libro nuovo
    briefing.md             briefing da compilare dal telefono (C.3)         da scrivere
    libro.yaml              libro.yaml vuoto con i commenti dello schema (B.3)  da scrivere
    LEGGIMI.md              LEGGIMI di libro (C.4)                            da scrivere
    stato.yaml              macchina a stati (C.1)                            da scrivere
    cronologia.yaml         cronologia vuota (B.2.1)                          da scrivere
    conferme-autore.yaml    conferme KDP (A.9)                                da scrivere
  dati/
    kdp.yaml                direttive KDP (A.2); ultima_verifica (A.8)       da scrivere
    verifiche-kdp.md        registro delle verifiche fatte dall'autore (A.8) da scrivere
    lista-nera.yaml         lista base: 05-critica rr. 19-21 (B.8)           da scrivere
    libro.schema.yaml       schema di libro.yaml (B.3)                       da scrivere
    profilo.schema.yaml     schema dei profili (B.6)                         da scrivere
    stato.schema.yaml       schema di stato.yaml (C.1)                       da scrivere
    lingue.yaml             lingue supportate: per ora solo it (B.3)         da scrivere
    hook.yaml               modalità dell'hook: avviso | blocco (C.4)        da scrivere
    nomi_vietati.txt        nomi che non devono comparire in motore/ (B.9); lo compila l'autore  da scrivere (vuoto)
  script/
    comune.py               percorso del libro, libro.yaml + profilo, ramo da git, scrittura recintata  da scrivere
    avvio.py                lettura obbligatoria, marker di sessione (C.4)   da scrivere
    nuovo.py                crea un libro dal briefing (B.4, fase 0)         da scrivere
    fase.py                 macchina a stati: gate, ok/avanti/correggi/stato (C.1)  da scrivere
    capitolo.py             controlli del capitolo in un colpo solo (C.2)    da scrivere
    conta.py                metodo di conteggio, parole per pagina           da scrivere
    stile.py                frase media, voci con pattern, tetti, lista nera  da scrivere
    riciclo.py              anti-riciclo a 7 parole (C.2)                    da scrivere
    continuita.py           date, età, durate, cifre, nomi in due grafie (B.2.1)  da scrivere
    ortografia.py           Hunspell it_IT + parole ammesse del libro        da scrivere
    compila.py              manoscritto completo da 04-manoscritto           da scrivere (tecnica esistente)
    impagina.py             PDF di stampa                                    da scrivere (tecnica esistente)
    verifica_pdf.py         pagine, margini, font, indice contro pagine      da scrivere (metodo provato)
    conformita_kdp.py       report KDP sezioni 1-15 (A.4)                    da scrivere
    kdp_verifica.py         «verifica KDP fatta [data]»; promemoria se 403 (A.8)  da scrivere
    pacchetto.py            06-pubblicazione: scheda, quarta, brief, checklist  da scrivere
    revisione.py            «prepara per revisione» (C.6)                    da scrivere
    valida_profili.py       i 7 profili contro profilo.schema.yaml (B.2.2)   da scrivere
    separazione.py          nessun libro dentro motore/ (B.9)                da scrivere
    recinto.py              nessuna scrittura fuori dal libro indicato (B.9) da scrivere
    hook_sessione.py        hook SessionStart (C.4)                          da scrivere
    hook_manoscritto.py     hook PreToolUse, modalità avviso/blocco (C.4)    da scrivere
  stampa/
    modello.css             foglio di stile parametrico (valori da libro.yaml)  da scrivere
    print.js                render Chromium                                  da scrivere (tecnica esistente)
    font/                   font OFL statici, licenze, FONTI.yaml (B.2.3)    da preparare dalle fonti ufficiali
  prove/
    mini-libro/             giallo inventato di 3 capitoli (B.2.2)           da scrivere
    mini-libro-romance/     romance inventato di 3 capitoli brevi (B.2.2)    da scrivere
    attesi.yaml             esiti attesi degli script sui due mini-libri     da scrivere
```

**File per libro** (nella cartella `<libro>`, creati da `zb nuovo` o con l'«ok» dell'autore): `libro.yaml` (B.3), `stato.yaml` (C.1), `LEGGIMI.md` (C.4), `cronologia.yaml` (B.2.1), `nomi_propri.txt` (B.3), `06-pubblicazione/conferme-autore.yaml` (A.9), e le cartelle `00-progetto` … `06-pubblicazione`.

`motore/modelli/` (modelli vuoti del motore) e `motore/riferimenti/modelli/` (modelli di casa-editrice) sono due cartelle diverse.

#### B.2.1 Continuità: `continuita.py` e `cronologia.yaml`

**File per libro:** `<libro>/cronologia.yaml`, compilato in fase 3 (C.1) dai documenti approvati del libro (bibbia, scaletta). Modello vuoto:

```yaml
nascite:        # - {chi: <personaggio>, data: AAAA-MM-GG}
eventi:         # - {id: <id>, data: AAAA-MM-GG, capitolo: <N>, descrizione: <breve>}
durate:         # - {da: <id evento>, a: <id evento>, valore: "<N anni>", tolleranza_mesi: 6}
cifre:          # - {id: <id>, valore: <numero>, unita: <euro|lire|...>, forme_ammesse: [<cifre>, <in lettere>]}
eta_per_capitolo: {calcolata: true}   # da nascite + data d'intestazione del capitolo
```

**Cosa controlla `continuita.py`** (report `<libro>/06-diagnostica/continuita.md`):

| Controllo | Come |
|---|---|
| Giorni della settimana | ogni «giorno N mese» con il giorno della settimana, nell'intestazione e nel testo, ricalcolato su `calendario.anni_ammessi`; KO se nessun anno ammesso lo dà |
| Età | ogni «N anni» riferito a un personaggio nominato nella stessa frase, confrontato con nascita e data del capitolo; KO oltre ±1 anno |
| Durate | **tabella di tutte le occorrenze** di «N anni/mesi/settimane/giorni» con capitolo e riga, e ricalcolo dalle date di intestazione e da `durate`; KO oltre la tolleranza |
| Cifre ripetute | ogni cifra vicina a un'unità di misura o di valuta confrontata con `cifre`; KO se diversa dalle forme ammesse |
| Nomi in due grafie | parole con maiuscola non in `nomi_propri.txt` a distanza di modifica 1-2 da una voce dell'elenco → avviso con le due grafie |
| Ordine delle date | le date d'intestazione non tornano indietro rispetto alla scaletta → avviso |

**Cosa NON può controllare:**
- che un oggetto o una persona sia già in scena, o ne sia uscito;
- chi sa cosa in un dato momento;
- posizioni, distanze e tempi di spostamento;
- il tempo interno di una scena (luce, pasti, giorno e notte);
- età e durate dette in modo indiretto;
- conseguenze fisiche (ferite, segni) da un capitolo all'altro.

Per questi punti il report finisce con una **checklist manuale**: una riga per capitolo con le voci della bibbia del libro che il capitolo tocca (personaggi, oggetti, ferite, chi sa cosa) e la casella «verificato dall'autore». Al gate G5 la checklist si mostra con il capitolo; le caselle vuote restano avvisi aperti in `stato.yaml`, non KO.

#### B.2.2 Prove: `motore/prove/`

**Genere del mini-libro: giallo.** Il profilo ha capitoli corti (minimo 800 parole, 12-lunghezze r. 22) e scene obbligatorie verificabili (scoperta, falsa pista, smascheramento: 01-mercato r. 25). Tutto è inventato: titolo «Prova di stampa», autore «Autore di Prova», luoghi e personaggi fittizi, nessun riferimento a libri reali.

```
motore/prove/
  mini-libro/
    libro.yaml              profilo giallo; A5 crema; target 3.000 parole; 1 interludio senza numero
    briefing.md, cronologia.yaml, nomi_propri.txt
    02-bibbia/bibbia.md     una pagina
    03-architettura/scaletta.md, piano-parole.md
    04-manoscritto/
      01-*.md               corretto: deve passare tutti i controlli
      02-*.md               errori voluti: una voce della lista nera, «come se» oltre il tetto,
                            un nome vietato prima del capitolo consentito, un giorno della settimana
                            sbagliato, un'età sbagliata, un nome in due grafie, chiusura dichiarata
                            diversa dalla scaletta
      03-*.md               sotto il minimo di parole, frase media fuori range, ultima riga di una parola
    05-output/              PDF generato dal motore (B.7 passo 3)
  attesi.yaml               per ogni script: esiti attesi (controllo, file, riga);
                            per il PDF: pagine, margini minimi, font incorporati, sha256;
                            per conta.py: parole per capitolo e totale
```

Uno script si usa su un libro vero solo dopo che sul mini-libro dà **esattamente** gli esiti di `attesi.yaml`: nessun KO in più, nessuno in meno. Le prove girano su una copia del mini-libro in una cartella temporanea, così `recinto.py` (B.9) può verificare che nessun file fuori dalla copia sia cambiato.

**Validazione dei profili: `script/valida_profili.py`.**
- Legge i 7 file di `motore/profili/` e li confronta con `dati/profilo.schema.yaml`.
- Controlla che ci siano tutti i campi obbligatori e che i tipi siano giusti.
- Controlla la coerenza interna:
  - minimo ≤ media ≤ massimo;
  - `parole_per_atto` con somma 1;
  - `chiusura_preferita` tra `gancio_domanda`, `gesto_oggetto` e `misto`;
  - intervalli con il primo valore minore del secondo.
- Ogni valore deve avere una fonte nel commento (`12 r. N`, `01-mercato r. N`…) oppure la marca `PROPOSTA`.
- Esce con 1, indicando file e campo, al primo errore. Gira nel passo 2 di B.7 e prima di ogni commit nel ramo del motore.

**Secondo mini-libro: `prove/mini-libro-romance/`.** Romance inventato: titolo «Prova d'inchiostro», autore «Autrice di Prova», luoghi e personaggi fittizi. Ha 3 capitoli brevi, circa 1.600 parole ciascuno, e serve a provare che i controlli cambiano davvero con il profilo.

| Cosa | Mini-libro giallo | Mini-libro romance | Atteso |
|---|---|---|---|
| Minimo di parole per capitolo | 800 (profilo giallo) | 1.500 (profilo romance) | un capitolo di 1.200 parole è OK nel giallo e KO nel romance; i due mini-libri contengono lo stesso capitolo-prova di 1.200 parole |
| Chiusura preferita | `gancio_domanda` | `misto` | la stessa chiusura su una domanda è conforme nel giallo; nel romance (`misto`, e `D_massimo_consecutivi: 2` nel `libro.yaml` del mini-libro romance) la terza chiusura su domanda di fila dà KO |
| Frase media | [9, 14] (thriller/giallo) | [12, 17] | un capitolo con frase media 10 è OK nel giallo e KO nel romance |
| Dialogo % | [25, 45] | [35, 55] | un capitolo con il 30% di dialogo è OK nel giallo e KO nel romance |
| Scene obbligatorie | scoperta, falsa pista, smascheramento | primo incontro, separazione, gesto finale | il report di struttura chiede le scene del profilo giusto |

Il confronto usa **lo stesso testo** dove serve (il capitolo-prova da 1.200 parole e una pagina con frase media 10 e dialogo al 30%), così l'unica cosa che cambia è il profilo. `attesi.yaml` ha una sezione per ciascun mini-libro. Nessun riferimento a libri reali.

#### B.2.3 Font: `motore/stampa/font/`

I font si preparano **solo dalle fonti ufficiali**, con licenza SIL Open Font License (OFL). Mai da una cartella di libro o da un'altra copia locale.

`motore/stampa/font/FONTI.yaml` registra ogni file:

```yaml
- nome: "EB Garamond"
  versione: "<da registrare al download>"
  licenza: "SIL Open Font License 1.1"
  fonte: "https://github.com/google/fonts/tree/main/ofl/ebgaramond"
  file_origine: "EBGaramond[wght].ttf, EBGaramond-Italic[wght].ttf"
  preparazione: "istanze statiche con fontTools (Regular 400, Italic 400, SemiBold 600), compressione woff2"
  file:
    - {nome: EBGaramond-Regular.woff2, sha256: "<…>"}
  licenza_file: OFL.txt
  scaricato_il: AAAA-MM-GG
```

- La versione e gli sha256 si scrivono al momento del download, letti dal file scaricato. Non si inventano.
- Se il download è bloccato (proxy), mi fermo e lo dico. Non prendo il font da un'altra cartella.
- Il file della licenza (`OFL.txt`) sta accanto ai font.
- Si possono aggiungere altri font OFL con una voce nuova in `FONTI.yaml`. `libro.yaml` sceglie il font per nome, e `impagina.py` si ferma se il nome non è in `FONTI.yaml`.

### B.3 Schema di `libro.yaml`

Un file per libro, in `<libro>/libro.yaml`. Lo crea `zb nuovo` dal briefing (fase 0) e lo approva l'autore al gate G0. **Il ramo non sta in `libro.yaml`**: lo legge `comune.py` da git, perché ogni sessione ha il suo.

**Come si combinano i valori.** `comune.py` carica il profilo di genere indicato in `profilo:` (B.6), poi applica i valori di `libro.yaml`. Un valore di `libro.yaml` che cambia un valore del profilo deve stare in `override`, con il motivo; altrimenti `avvio.py` si ferma con «valore del profilo cambiato senza override: <campo>».

**Campi**

| Campo | Obbligatorio | Contenuto |
|---|---|---|
| `titolo`, `autore` | sì | testo |
| `modalita` | sì | `nuovo` (si scrive da zero) \| `riscrittura` (si riscrive un testo precedente) |
| `sottotitolo` | no | testo; letto da `conformita_kdp.py` (sezione 2: titolo + sottotitolo ≤ 200 caratteri) |
| `serie` | no | `{nome, numero}`; letto da `conformita_kdp.py` (sezione 3: numero solo in cifre, nome senza parole vietate) |
| `ebook` | no | `true`/`false` (predefinito `false`); con `true` `conformita_kdp.py` esegue anche la sezione 12 su `ebook.docx` |
| `lingua` | sì | codice di lingua; per ora solo `it` (vedi sotto) |
| `profilo` | sì | nome di un file in `motore/profili/` |
| `override` | no | elenco di `{campo, valore, motivo}`; senza motivo è un errore |
| `parole.metodo` | no | `unico` (predefinito) |
| `parole.target_totale` | sì | numero |
| `parole.unita_senza_numero` | no | budget di prologo, epilogo, interludi |
| `formato.pagina_pollici` | sì | `[larghezza, altezza]` |
| `formato.carta`, `formato.bleed` | no | `crema`/`bianca`; `true`/`false` |
| `formato.margini_mm` | no | `alto`, `basso`, `esterno`, `interno_scelto` |
| `formato.font`, `formato.numerazione` | no | nome, corpo, interlinea; da dove e dove |
| `stile.*` | no | correzioni a frase media, dialogo, tetti, chiusure (sempre via `override` se cambiano il profilo) |
| `voci` | no | voci con pattern del libro, aggiunte alla lista nera (sotto) |
| `vincoli_capitolo` | no | parole o voci con `consentito_in_capitoli` / `vietato_in_capitoli` |
| `nome_vietato_prima_di` | no | nomi che non compaiono prima di un punto del libro |
| `dichiarazioni` | no | campi dichiarati nell'intestazione nascosta di ogni capitolo e loro vincoli |
| `fatti_incompatibili` | no | coppie di fatti che non possono stare tutti e due nel libro: `{id, a: {pattern, unita}, b: {pattern, unita}, nota}`; `unita` è facoltativo (senza, tutto il libro); se compaiono A e B, `continuita.py` dà un AVVISO con le due righe |
| `struttura.separatore_scena` | sì | `{sorgente, stampa}`: un valore ciascuno |
| `struttura.intestazione_capitolo` | sì | modello, per esempio `"Luogo — giorno e data"` o `"Nome — Luogo, giorno mese"` |
| `struttura.parti`, `struttura.interludi` | no | parti con capitoli; interludi con `dopo_capitolo`, `titolo`, `parte` |
| `calendario.anni_ammessi` | no | anni su cui si verificano i giorni della settimana |
| `ortografia.parole_ammesse_file` | no | predefinito `nomi_propri.txt` |
| `testo_precedente` | **sì in `riscrittura`**, assente in `nuovo` | percorso del testo precedente del libro: registro dei fatti, usato per l'anti-riciclo (C.2) e letto in fase 1; con `modalita: nuovo` il campo dà errore se presente, con `riscrittura` dà errore se manca o il file non esiste |
| `copyright` | sì | riga ©, dichiarazione di fantasia (08-pubblicazione r. 7), nota dell'autore facoltativa |
| `manuale` | no | percorso del manuale di stile del libro, se c'è |

**Lingua.** `lingua` è obbligatoria. Le lingue supportate stanno in `motore/dati/lingue.yaml`; per ora c'è solo `it`:

```yaml
it:
  ortografia: {hunspell: it_IT, opzioni: "-i utf-8"}
  mesi: [gennaio, febbraio, marzo, aprile, maggio, giugno, luglio, agosto, settembre, ottobre, novembre, dicembre]
  giorni: [lunedì, martedì, mercoledì, giovedì, venerdì, sabato, domenica]
  lineetta_dialogo: "—"
  virgolette: ["«", "»"]
```

`comune.py` lo controlla prima di qualsiasi altra cosa. Con un altro codice, o con il campo mancante, il motore si ferma senza scrivere nulla:

```
Lingua «<codice>» non supportata. Il motore oggi lavora solo in italiano (lingua: it):
ortografia Hunspell it_IT, giorni e mesi in italiano. Correggi libro.yaml oppure
chiedi di aggiungere la lingua in motore/dati/lingue.yaml.
```

**Margine interno.** Margine interno = **max(tabella KDP per il numero di pagine, `margini_mm.interno_scelto`)**. `impagina.py` stima le pagine con `parole.target_totale ÷ parole_per_pagina`. La densità parte dal valore del profilo; dopo la prima impaginazione si usa quella misurata sul PDF reale. Se il numero vero di pagine cambia fascia, `impagina.py` ricalcola il margine e rifà l'impaginazione.

**Voci con pattern** (in `motore/dati/lista-nera.yaml` per la lista base, in `voci` per il libro). Ogni voce ha questi campi:
- `id`;
- `pattern`: regex Python, `(?i)` per non distinguere le maiuscole;
- `modalita`:
  - `vieta`: ogni occorrenza è KO;
  - `conta`: KO solo sopra il massimo;
  - `avviso`: elenco delle occorrenze con capitolo e riga, per un controllo a vista;
- `massimo` e `ambito` (`libro` | `capitolo`);
- facoltativi: `consentito_in_capitoli`, `vietato_in_capitoli`, `solo_dialogo`, `nota`.

I capitoli si indicano come numeri, intervalli (`"5-12"`), o nomi di unità senza numero (`prologo`, `epilogo`, `"interludio II"`). Gli elenchi sono espliciti e non dipendono dalla posizione: un'unità senza numero vale solo se è nominata.

**Voci che una regex non decide da sola.** Per esempio un'immagine vietata solo in senso figurato, una parola ammessa in un luogo e non in un altro, una struttura di paragrafo, chi sta parlando.
- Le forme fisse hanno `modalita: vieta`.
- Il resto ha `modalita: avviso` e finisce in una tabella «da guardare» del report, con capitolo, riga e frase.
- Ciò che non si può cercare nel testo (persone reali, per esempio) va nella checklist manuale del capitolo.

**Dichiarazioni nel capitolo.** Ogni file di capitolo può avere, sotto l'intestazione, una riga nascosta (commento HTML) che `compila.py` toglie in stampa. **I campi non sono fissi: li decide ogni libro in `dichiarazioni` di `libro.yaml`**; il motore legge le coppie `campo=valore` e ignora il testo tra parentesi:

```
## 7
*Luogo — giorno e data*
<!-- zb: chiusura=G pov=Anna (campi decisi dal libro in «dichiarazioni» di libro.yaml) -->
```

I campi e i loro vincoli li definisce `dichiarazioni` in `libro.yaml`. `capitolo.py` li confronta:
- con la scaletta (per esempio la chiusura prevista);
- con i tetti (per esempio un tipo di chiusura al massimo N volte e mai in capitoli consecutivi);
- con il testo, quando c'è un controllo incrociato (per esempio le parole-àncora di un tipo di passaggio): dà avviso se il conteggio non coincide.

#### Esempio 1 — thriller inventato

Titolo, autrice, luoghi, personaggi e numeri sono inventati.

```yaml
titolo: "Le chiavi di Morlano"
sottotitolo: null
modalita: nuovo
serie: {nome: "Le indagini di Nora Silvi", numero: 1}
ebook: true
autore: "Ada Rensi"
lingua: it
profilo: thriller
override: []

parole:
  metodo: unico
  target_totale: 82000
  unita_senza_numero: {prologo: 900}

formato:
  pagina_pollici: [6, 9]
  carta: crema
  bleed: false
  margini_mm: {alto: 20, basso: 20, esterno: 16, interno_scelto: 16}
  font: {nome: "EB Garamond", corpo_pt: 11, interlinea: 1.45}
  numerazione: {da: prologo, pagine_iniziali: senza_numero, posizione: piede_centro}

voci:
  - {id: orologio, pattern: '(?i)\bcome un orologio\b', modalita: conta, massimo: 2, ambito: libro}

vincoli_capitolo:
  - {id: parola_chiave_selenite, pattern: '\bSelenite\b', consentito_in_capitoli: ["20-34"]}

nome_vietato_prima_di:
  - {nome: "Ivo Barca", pattern: '\bIvo Barca\b|\bBarca\b', vietato_in: [prologo, "1-21"]}
fatti_incompatibili:
  # esempio neutro: se il faro è spento dal capitolo 3, nessuna luce del faro dopo
  - {id: faro_spento, a: {pattern: '(?i)\bfaro\b.*\bspento\b', unita: ["1-3"]},
     b: {pattern: '(?i)\bluce del faro\b', unita: ["4-34"]}, nota: "il faro resta spento"}

dichiarazioni:
  chiusura: {sigle: [D, R, P, X], prevista_da: scaletta}   # domanda, rivelazione, pericolo, decisione
  pov: {valori: [Nora, Silvano], massimo_consecutivi: 3}

struttura:
  separatore_scena: {sorgente: "* * *", stampa: "* * *"}
  intestazione_capitolo: "Nome — Luogo, giorno mese"
  parti:
    - {titolo: "Parte prima — Il furto", capitoli: [1, 11]}
    - {titolo: "Parte seconda — La rete", capitoli: [12, 24]}
    - {titolo: "Parte terza — Le chiavi", capitoli: [25, 34]}
  interludi: []

calendario: {anni_ammessi: [2019]}
ortografia: {parole_ammesse_file: nomi_propri.txt}   # Morlano, Nora, Silvano, Selenite…

copyright:
  riga: "© {anno} {autore}. Tutti i diritti riservati."
  fantasia: "Quest'opera è frutto di fantasia. Nomi, personaggi, luoghi e fatti sono invenzione dell'autrice o usati in modo fittizio; ogni somiglianza con persone, vive o scomparse, o con fatti realmente accaduti è puramente casuale."
  nota_autore: null
```

#### Esempio 2 — romanzo d'amore inventato

Titolo, autore, luoghi, personaggi e numeri sono inventati.

```yaml
titolo: "Un'estate a Calvenna"
sottotitolo: "Romanzo"
modalita: nuovo
serie: null
ebook: false
autore: "Piero Lanzi"
lingua: it
profilo: romance
override:
  - campo: capitoli.minimo
    valore: 1200
    motivo: "Capitoli brevi alternati tra i due punti di vista; scelta dichiarata in scaletta (12-lunghezze r. 30)."

parole:
  metodo: unico
  target_totale: 70000
  unita_senza_numero: {interludi: 450, epilogo: 1200}

formato:
  pagina_pollici: [5.5, 8.5]
  carta: crema
  bleed: false
  margini_mm: {alto: 20, basso: 22, esterno: 16, interno_scelto: 17}
  font: {nome: "EB Garamond", corpo_pt: 11.5, interlinea: 1.5}
  numerazione: {da: capitolo_1, pagine_iniziali: senza_numero, posizione: piede_centro}

voci:
  - {id: farfalle, pattern: '(?i)farfalle nello stomaco', modalita: vieta}
  - {id: sorriso, pattern: '(?i)\bsorris[eoi]\b', modalita: conta, massimo: 4, ambito: capitolo}

vincoli_capitolo:
  - {id: anello, pattern: '(?i)\banello\b', vietato_in_capitoli: ["1-25"], nota: "l'anello compare dal cap. 26"}

nome_vietato_prima_di:
  - {nome: "Nives", pattern: '\bNives\b', vietato_in: ["1-9", "interludio I"], obbligatorio_in: ["10-30"]}

dichiarazioni:
  pov: {valori: [Teo, Giulia], alternanza: stretta}
  chiusura: {sigle: [G, O, B, D], prevista_da: scaletta, D_massimo_consecutivi: 2}   # gesto, oggetto, battuta, domanda

struttura:
  separatore_scena: {sorgente: "~", stampa: "❦"}
  intestazione_capitolo: "Nome"
  parti: []
  interludi:
    - {numero: I,   dopo_capitolo: 8,  titolo: "Lettera da Calvenna", parte: null}
    - {numero: II,  dopo_capitolo: 16, titolo: "Lettera dal porto",   parte: null}
    - {numero: III, dopo_capitolo: 24, titolo: "Ultima lettera",      parte: null}

calendario: {anni_ammessi: [2023]}
ortografia: {parole_ammesse_file: nomi_propri.txt}   # Calvenna, Teo, Giulia, Nives…

copyright:
  riga: "© {anno} {autore}. Tutti i diritti riservati."
  fantasia: "Quest'opera è frutto di fantasia. Nomi, personaggi, luoghi e fatti sono invenzione dell'autore o usati in modo fittizio; ogni somiglianza con persone, vive o scomparse, o con fatti realmente accaduti è puramente casuale."
  nota_autore: "Calvenna non esiste: è fatta di pezzi di molti paesi di mare."
```

### B.4 Ingresso: il libro come parametro

**Forma:** `zb <comando> <libro> [argomenti]`. `<libro>` è un percorso, assoluto o relativo alla cartella corrente. Non c'è un «libro attivo» implicito; per comodità, `ZB_LIBRO=<percorso>` vale come valore predefinito per la sessione, e ogni comando stampa comunque il percorso risolto prima di fare qualcosa.

**Come il motore trova il libro.**
1. Se `<libro>` è un file `libro.yaml`, il libro è la sua cartella.
2. Se è una cartella, il motore cerca `libro.yaml` lì e poi nelle cartelle superiori, fino alla radice del repository git che la contiene. Il primo che trova definisce `<libro>`.
3. Se non lo trova, si ferma: «Nessun libro.yaml sopra <percorso>. Per un libro nuovo: zb nuovo <briefing>».
4. Il briefing di un libro esistente è sempre `<libro>/00-progetto/briefing.md`.

**Come nasce un libro: `zb nuovo <percorso-briefing>`.**
- Se il briefing sta in `<x>/00-progetto/briefing.md`, il libro è `<x>`; altrimenti il libro è la cartella del briefing, e il briefing viene spostato in `00-progetto/` con l'«ok» dell'autore.
- Se in quella cartella c'è già un `libro.yaml`, si ferma: non sovrascrive un libro esistente.
- Crea le cartelle e i file dai modelli vuoti (B.2), compila `libro.yaml` dal briefing e dal profilo, apre il gate G0 (C.1).

**Comandi**

| Comando | Script | Scrive in |
|---|---|---|
| `zb nuovo <briefing>` | `nuovo.py` | la cartella del nuovo libro |
| `zb avvio <libro>` | `avvio.py` | `<libro>/.zb/` (marker) |
| `zb stato <libro>` | `fase.py` | niente (a schermo) |
| `zb capitolo <libro> N` | `capitolo.py` | `<libro>/06-diagnostica/capitoli/NN.md` |
| `zb conta <libro>` | `conta.py` | a schermo; con `--scrivi` `<libro>/06-diagnostica/conteggio.md` |
| `zb stile <libro> [N]` | `stile.py` | `<libro>/06-diagnostica/stile.md` |
| `zb continuita <libro>` | `continuita.py` | `<libro>/06-diagnostica/continuita.md` |
| `zb ortografia <libro>` | `ortografia.py` | `<libro>/06-diagnostica/controllo-ortografico.md` |
| `zb compila <libro>` | `compila.py` | `<libro>/05-output/<titolo>-completo.md` |
| `zb impagina <libro>` | `impagina.py` | `<libro>/05-output/*.pdf` |
| `zb pdf <libro>` | `verifica_pdf.py` | `<libro>/06-diagnostica/verifica-pdf.md` |
| `zb kdp <libro>` | `conformita_kdp.py` | `<libro>/06-pubblicazione/conformita-kdp.md` |
| `zb pacchetto <libro>` | `pacchetto.py` | `<libro>/06-pubblicazione/` |
| `zb revisione <libro> <documento>` | `revisione.py` | niente (a schermo) |
| `verifica KDP fatta [AAAA-MM-GG]` | `kdp_verifica.py` | `motore/dati/kdp.yaml`, `motore/dati/verifiche-kdp.md` (unica eccezione: non riguarda un libro) |
| `zb prove` | tutti, sui due mini-libri (giallo e romance) | copie temporanee dei mini-libri |
| `zb push` | `push.py` | niente nel repository: push del ramo corrente con attese crescenti, poi su un ramo alternativo `<ramo>-salvataggio-<data-ora>`, poi un `git bundle` nella cartella temporanea (percorso e sha256 a schermo) |

Ogni comando che opera su un libro scrive **solo** dentro `<libro>` (B.9). Nessun comando fa commit da solo, e il push lo fa solo `zb push`, quando lo si lancia: il salvataggio segue B.5.

**Motore e libri in repository diversi.**
- Il motore trova sé stesso dal percorso di `zb`, oppure da `--radice <cartella-del-motore>`, oppure da `ZB_RADICE`. Esempio: `python3 /percorso/repo-motore/motore/zb avvio /percorso/repo-libri/romanzi/le-chiavi`.
- I comandi git (stato, commit, push) si fanno nel repository del libro: `git -C <libro> …`. Il motore non fa mai commit nel proprio repository mentre lavora su un libro.
- `avvio.py` stampa entrambi: commit del motore usato e commit del libro. Il commit del motore va anche in `stato.yaml` (`motore_commit`).
- Nella sessione servono tutti e due i repository: il motore basta in lettura, quello del libro serve in scrittura.

**Se la sessione non può scrivere nel repository del libro.**
- `avvio.py` lo verifica prima di tutto, con una prova di scrittura in `<libro>/.zb/` e un `git -C <libro> push --dry-run`.
- Se una delle due fallisce, si ferma con il messaggio d'errore esatto e non scrive niente da nessuna parte: né nel motore, né in un'altra cartella, né in un altro ramo.
- Restano disponibili solo i comandi a schermo (`stato`, `revisione`, e `conta`, `stile`, `continuita` con `--schermo`), che non scrivono file.

### B.5 Regole fisse

1. **Tono.** Il testo precedente di un libro, se c'è, è un registro dei fatti: non si commenta né si giudica, nei report come in chat.
2. **Proponi → approvo → applica.** Ogni modifica al testo o ai dati di un libro si propone, voce per voce; si applica solo dopo l'«ok». Mai nuovi oggetti o persone in una scena senza richiesta.
3. **Metodo unico di conteggio** (predefinito): token separati da spazi; esclusi le righe che cominciano con «#» e i token senza lettere né cifre (lineette di dialogo, separatori, segni isolati). Niente `wc -w`, che cambia con la lingua di sistema. Ogni report dichiara il metodo.
4. **Precedenza.** Manuale e `libro.yaml` del libro > profilo di genere > procedura del motore e riferimenti > skill dell'autore. In caso di contrasto vince il livello più alto e il report lo segnala.
5. **Ramo.** Si lavora solo sul ramo assegnato dalla sessione; `comune.py` lo legge da git. Se il checkout del libro è su un altro ramo, il motore si ferma.
6. **Recinto.** Un comando su un libro scrive solo dentro `<libro>` (B.9). Il motore non contiene libri (B.9).
7. **Dichiarazione AI.** Promemoria fisso in ogni pacchetto e in ogni report KDP (A.6).
8. **Blocco di salvataggio.** Dopo ogni passo: file derivati rigenerati, report in `<libro>/06-diagnostica/`, `git add`, commit, push, `git status -sb`, `git log -1`. Se il push fallisce o un file non si salva: fermarsi e riportare l'errore; mai dire «fatto» se non è su origin. Resoconto con hash, file, pagine, parole e «branch allineato a origin: sì/no».
9. **Direttive KDP.** Verifica più vecchia di 30 giorni, o mai fatta = avviso e pacchetto non pronto.

### B.6 Profili di genere: `motore/profili/`

Un file per genere. Ogni profilo è un **default**: `libro.yaml` lo sceglie con `profilo:` e lo corregge con `override` motivato (B.3). Accanto a ogni valore c'è la fonte:
- `12 r. N`, `02 r. N`, `03 r. N`, `05 r. N` sono le righe dei file `riferimenti/12-lunghezze-e-struttura-capitoli.md`, `02-architettura.md`, `03-stesura.md` e `05-critica-e-punteggio.md` (casa-editrice main @ becd0e2);
- `01-mercato r. 25` è la riga di `riferimenti/01-mercato.md`;
- **PROPOSTA** è un valore senza una fonte nei riferimenti, approvato dall'autore il 2026-10-02. Fanno eccezione le similitudini dei cinque profili giallo, narrativa-letteraria, fantasy, fantascienza e young-adult, segnate «da confermare».

**Formato di un profilo** (`dati/profilo.schema.yaml`): `genere`, `lunghezza_totale`, `capitoli`, `scene`, `parole_per_atto`, `battiti`, `chiusura_preferita` (`gancio_domanda` | `gesto_oggetto` | `misto`), `frase_media`, `dialogo_percento`, `similitudini_max_per_parole`, `parole_filtro`, `lista_nera`, `parole_per_pagina`, `scene_obbligatorie`.

#### `profili/thriller.yaml`

```yaml
genere: thriller
lunghezza_totale:
  consigliata: [70000, 90000]                 # 12 r. 17 (thriller/giallo)
  formati:                                    # 12 rr. 13-16
    breve: [40000, 60000]
    standard: [70000, 90000]
    lungo: [90000, 120000]
    epico: [120000, 180000]
  parti_sopra: 100000                         # 12 r. 46: oltre 100.000 parole, dividere in parti
capitoli:
  minimo: 800                                 # 12 r. 22
  media: [1500, 2500]                         # 12 r. 22
  massimo: 3500                               # 12 r. 22
  coerenza: {min_su_media: 0.5, max_su_media: 1.7}   # 12 r. 30
  scene_per_capitolo: [1, 3]                  # 12 r. 34 («tipico nei thriller»: 1 scena), r. 35
  tolleranza_budget: 0.15                     # 12 r. 67, sul budget del capitolo in piano-parole.md
  tolleranza_totale: 0.05                     # 12 r. 67
scene:
  lunghezza: [800, 2500]                      # 12 r. 38
  sequel: [150, 600]                          # 12 r. 38
  budget_interno: {apertura: [0.10, 0.15], centro: [0.60, 0.70], chiusura: [0.15, 0.25]}   # 12 rr. 41-43
parole_per_atto: [0.25, 0.50, 0.25]           # 12 r. 56
battiti: {punto_centrale: [0.45, 0.55], tutto_perduto: [0.70, 0.80]}   # 02 r. 46
chiusura_preferita: gancio_domanda            # 03 r. 12; 02 r. 39 (domanda, rivelazione, pericolo, decisione)
frase_media: [9, 14]                          # PROPOSTA (03 r. 10 dà solo la regola: brevi nell'azione)
dialogo_percento: [25, 45]                    # PROPOSTA
similitudini_max_per_parole: 400              # PROPOSTA (una ogni 400 parole)
parole_filtro: {modalita: avviso, massimo_per_1000_parole: 8}   # elenco 05 r. 21 («ridurre»); il numero è PROPOSTA
lista_nera: dati/lista-nera.yaml              # 05 rr. 19-20, «eliminare sempre» → modalità vieta
parole_per_pagina: 250                        # 12 r. 7: 250-300 per pagina stampata; scelto il minimo (PROPOSTA)
scene_obbligatorie:
  - scoperta del crimine o della minaccia     # 01-mercato r. 25 (crime)
  - falsa pista                               # 01-mercato r. 25 (crime)
  - smascheramento                            # 01-mercato r. 25 (crime)
  - incidente scatenante che promette il climax   # 02 r. 19
  - posta in gioco che cresce da un atto all'altro # 02 r. 49
  - confronto finale tra protagonista e antagonista   # PROPOSTA
  - scadenza o corsa contro il tempo          # PROPOSTA
```

#### `profili/romance.yaml`

```yaml
genere: romance
lunghezza_totale:
  consigliata: [60000, 90000]                 # 12 r. 17
  formati:                                    # 12 rr. 13-16
    breve: [40000, 60000]
    standard: [70000, 90000]
    lungo: [90000, 120000]
    epico: [120000, 180000]
  parti_sopra: 100000                         # 12 r. 46
capitoli:
  minimo: 1500                                # 12 r. 23
  media: [2000, 3000]                         # 12 r. 23
  massimo: 4000                               # 12 r. 23
  coerenza: {min_su_media: 0.5, max_su_media: 1.7}   # 12 r. 30
  scene_per_capitolo: [2, 3]                  # 12 r. 35 (capitolo standard)
  tolleranza_budget: 0.15                     # 12 r. 67
  tolleranza_totale: 0.05                     # 12 r. 67
scene:
  lunghezza: [800, 2500]                      # 12 r. 38
  sequel: [150, 600]                          # 12 r. 38
  budget_interno: {apertura: [0.10, 0.15], centro: [0.60, 0.70], chiusura: [0.15, 0.25]}   # 12 rr. 41-43
parole_per_atto: [0.25, 0.50, 0.25]           # 12 r. 56
battiti: {punto_centrale: [0.45, 0.55], tutto_perduto: [0.70, 0.80]}   # 02 r. 46
chiusura_preferita: misto                     # PROPOSTA (il default di 03 r. 12 è la domanda)
frase_media: [12, 17]                         # PROPOSTA
dialogo_percento: [35, 55]                    # PROPOSTA
similitudini_max_per_parole: 300              # PROPOSTA
parole_filtro: {modalita: avviso, massimo_per_1000_parole: 8}   # elenco 05 r. 21; il numero è PROPOSTA
lista_nera: dati/lista-nera.yaml              # 05 rr. 19-20
parole_per_pagina: 250                        # 12 r. 7 (PROPOSTA il valore dentro il range)
scene_obbligatorie:
  - primo incontro                            # 01-mercato r. 25 (romance)
  - separazione                               # 01-mercato r. 25 (romance)
  - gesto finale                              # 01-mercato r. 25 (romance)
  - incidente scatenante che promette il climax   # 02 r. 19
  - punto di non ritorno della relazione      # PROPOSTA
  - finale felice o aperto alla speranza      # PROPOSTA
```

#### Gli altri profili

Stesso formato di thriller e romance. Tutti i valori marcati PROPOSTA sono stati approvati dall'autore.

#### `profili/giallo.yaml`

```yaml
genere: giallo
lunghezza_totale:
  consigliata: [70000, 90000]                  # 12 r. 17 (thriller/giallo)
  formati:                                    # 12 rr. 13-16
    breve: [40000, 60000]
    standard: [70000, 90000]
    lungo: [90000, 120000]
    epico: [120000, 180000]
  parti_sopra: 100000                         # 12 r. 46
capitoli:
  minimo: 800                                 # 12 r. 22
  media: [1500, 2500]                         # 12 r. 22
  massimo: 3500                               # 12 r. 22
  coerenza: {min_su_media: 0.5, max_su_media: 1.7}   # 12 r. 30
  scene_per_capitolo: [1, 3]                  # 12 rr. 34-35
  tolleranza_budget: 0.15                     # 12 r. 67
  tolleranza_totale: 0.05                     # 12 r. 67
scene:
  lunghezza: [800, 2500]                      # 12 r. 38
  sequel: [150, 600]                          # 12 r. 38
  budget_interno: {apertura: [0.10, 0.15], centro: [0.60, 0.70], chiusura: [0.15, 0.25]}   # 12 rr. 41-43
parole_per_atto: [0.25, 0.50, 0.25]           # 12 r. 56
battiti: {punto_centrale: [0.45, 0.55], tutto_perduto: [0.70, 0.80]}   # 02 r. 46
chiusura_preferita: gancio_domanda            # 03 r. 12; 02 r. 39
frase_media: [9, 14]                          # PROPOSTA approvata
dialogo_percento: [25, 45]                    # PROPOSTA approvata
similitudini_max_per_parole: 400              # PROPOSTA da confermare: valore non presente nelle tabelle approvate
parole_filtro: {modalita: avviso, massimo_per_1000_parole: 8}   # elenco 05 r. 21; il numero è PROPOSTA approvata
lista_nera: dati/lista-nera.yaml              # 05 rr. 19-20
parole_per_pagina: 250                        # 12 r. 7 (PROPOSTA approvata)
scene_obbligatorie:
  - scoperta del crimine                      # 01-mercato r. 25 (crime)
  - falsa pista                               # 01-mercato r. 25 (crime)
  - smascheramento                            # 01-mercato r. 25 (crime)
  - incidente scatenante che promette il climax   # 02 r. 19
  - indizi leali prima della soluzione        # PROPOSTA approvata
```

#### `profili/narrativa-letteraria.yaml`

```yaml
genere: narrativa-letteraria
lunghezza_totale:
  consigliata: [70000, 100000]                 # 12 r. 17
  formati:                                    # 12 rr. 13-16
    breve: [40000, 60000]
    standard: [70000, 90000]
    lungo: [90000, 120000]
    epico: [120000, 180000]
  parti_sopra: 100000                         # 12 r. 46
capitoli:
  minimo: 2500                                # 12 r. 25
  media: [3500, 5000]                         # 12 r. 25
  massimo: 7000                               # 12 r. 25
  coerenza: {min_su_media: 0.5, max_su_media: 1.7}   # 12 r. 30
  scene_per_capitolo: [2, 6]                  # 12 rr. 35-36
  tolleranza_budget: 0.15                     # 12 r. 67
  tolleranza_totale: 0.05                     # 12 r. 67
scene:
  lunghezza: [800, 2500]                      # 12 r. 38
  sequel: [150, 600]                          # 12 r. 38
  budget_interno: {apertura: [0.10, 0.15], centro: [0.60, 0.70], chiusura: [0.15, 0.25]}   # 12 rr. 41-43
parole_per_atto: [0.25, 0.50, 0.25]           # 12 r. 56
battiti: {punto_centrale: [0.45, 0.55], tutto_perduto: [0.70, 0.80]}   # 02 r. 46
chiusura_preferita: gesto_oggetto             # PROPOSTA approvata
frase_media: [14, 20]                         # PROPOSTA approvata
dialogo_percento: [15, 35]                    # PROPOSTA approvata
similitudini_max_per_parole: 250              # PROPOSTA da confermare: valore non presente nelle tabelle approvate
parole_filtro: {modalita: avviso, massimo_per_1000_parole: 8}   # elenco 05 r. 21; il numero è PROPOSTA approvata
lista_nera: dati/lista-nera.yaml              # 05 rr. 19-20
parole_per_pagina: 250                        # 12 r. 7 (PROPOSTA approvata)
scene_obbligatorie:
  - incidente scatenante che promette il climax   # 02 r. 19
  # nessuna scena fissa di genere: si decidono nel libro (PROPOSTA approvata)
```

#### `profili/fantasy.yaml`

```yaml
genere: fantasy
lunghezza_totale:
  consigliata: [90000, 130000]                 # 12 r. 17 («e oltre»)
  formati:                                    # 12 rr. 13-16
    breve: [40000, 60000]
    standard: [70000, 90000]
    lungo: [90000, 120000]
    epico: [120000, 180000]
  parti_sopra: 100000                         # 12 r. 46
  parti_obbligatorie: true                    # 12 r. 46-47 (romanzo lungo: 3-5 parti)
capitoli:
  minimo: 3000                                # 12 r. 27
  media: [4000, 6000]                         # 12 r. 27
  massimo: 8000                               # 12 r. 27
  coerenza: {min_su_media: 0.5, max_su_media: 1.7}   # 12 r. 30
  scene_per_capitolo: [3, 6]                  # 12 r. 36 (capitolo lungo)
  tolleranza_budget: 0.15                     # 12 r. 67
  tolleranza_totale: 0.05                     # 12 r. 67
scene:
  lunghezza: [800, 2500]                      # 12 r. 38
  sequel: [150, 600]                          # 12 r. 38
  budget_interno: {apertura: [0.10, 0.15], centro: [0.60, 0.70], chiusura: [0.15, 0.25]}   # 12 rr. 41-43
parole_per_atto: [0.25, 0.50, 0.25]           # 12 r. 56
battiti: {punto_centrale: [0.45, 0.55], tutto_perduto: [0.70, 0.80]}   # 02 r. 46
chiusura_preferita: misto                     # PROPOSTA approvata
frase_media: [13, 18]                         # PROPOSTA approvata
dialogo_percento: [25, 45]                    # PROPOSTA approvata
similitudini_max_per_parole: 300              # PROPOSTA da confermare: valore non presente nelle tabelle approvate
parole_filtro: {modalita: avviso, massimo_per_1000_parole: 8}   # elenco 05 r. 21; il numero è PROPOSTA approvata
lista_nera: dati/lista-nera.yaml              # 05 rr. 19-20
parole_per_pagina: 250                        # 12 r. 7 (PROPOSTA approvata)
scene_obbligatorie:
  - incidente scatenante che promette il climax   # 02 r. 19
  - regole del mondo mostrate prima di essere usate   # PROPOSTA approvata
  - prezzo della magia                        # PROPOSTA approvata
  - viaggio o soglia                          # PROPOSTA approvata
```

#### `profili/fantascienza.yaml`

```yaml
genere: fantascienza
lunghezza_totale:
  consigliata: [80000, 110000]                 # PROPOSTA approvata (12 r. 17 non lo indica)
  formati:                                    # 12 rr. 13-16
    breve: [40000, 60000]
    standard: [70000, 90000]
    lungo: [90000, 120000]
    epico: [120000, 180000]
  parti_sopra: 100000                         # 12 r. 46
capitoli:
  minimo: 2000                                # 12 r. 26
  media: [3000, 4000]                         # 12 r. 26
  massimo: 6000                               # 12 r. 26
  coerenza: {min_su_media: 0.5, max_su_media: 1.7}   # 12 r. 30
  scene_per_capitolo: [2, 3]                  # 12 r. 35
  tolleranza_budget: 0.15                     # 12 r. 67
  tolleranza_totale: 0.05                     # 12 r. 67
scene:
  lunghezza: [800, 2500]                      # 12 r. 38
  sequel: [150, 600]                          # 12 r. 38
  budget_interno: {apertura: [0.10, 0.15], centro: [0.60, 0.70], chiusura: [0.15, 0.25]}   # 12 rr. 41-43
parole_per_atto: [0.25, 0.50, 0.25]           # 12 r. 56
battiti: {punto_centrale: [0.45, 0.55], tutto_perduto: [0.70, 0.80]}   # 02 r. 46
chiusura_preferita: misto                     # PROPOSTA approvata
frase_media: [12, 17]                         # PROPOSTA approvata
dialogo_percento: [25, 45]                    # PROPOSTA approvata
similitudini_max_per_parole: 300              # PROPOSTA da confermare: valore non presente nelle tabelle approvate
parole_filtro: {modalita: avviso, massimo_per_1000_parole: 8}   # elenco 05 r. 21; il numero è PROPOSTA approvata
lista_nera: dati/lista-nera.yaml              # 05 rr. 19-20
parole_per_pagina: 250                        # 12 r. 7 (PROPOSTA approvata)
scene_obbligatorie:
  - incidente scatenante che promette il climax   # 02 r. 19
  - novum presentato presto                   # PROPOSTA approvata
  - conseguenza sociale del novum             # PROPOSTA approvata
```

#### `profili/young-adult.yaml`

```yaml
genere: young-adult
lunghezza_totale:
  consigliata: [60000, 85000]                  # 12 r. 17
  formati:                                    # 12 rr. 13-16
    breve: [40000, 60000]
    standard: [70000, 90000]
    lungo: [90000, 120000]
    epico: [120000, 180000]
  parti_sopra: 100000                         # 12 r. 46
capitoli:
  minimo: 1500                                # 12 r. 28
  media: [2500, 4000]                         # 12 r. 28
  massimo: 5000                               # 12 r. 28
  coerenza: {min_su_media: 0.5, max_su_media: 1.7}   # 12 r. 30
  scene_per_capitolo: [2, 3]                  # 12 r. 35
  tolleranza_budget: 0.15                     # 12 r. 67
  tolleranza_totale: 0.05                     # 12 r. 67
scene:
  lunghezza: [800, 2500]                      # 12 r. 38
  sequel: [150, 600]                          # 12 r. 38
  budget_interno: {apertura: [0.10, 0.15], centro: [0.60, 0.70], chiusura: [0.15, 0.25]}   # 12 rr. 41-43
parole_per_atto: [0.25, 0.50, 0.25]           # 12 r. 56
battiti: {punto_centrale: [0.45, 0.55], tutto_perduto: [0.70, 0.80]}   # 02 r. 46
chiusura_preferita: gancio_domanda            # 03 r. 12; 02 r. 39
frase_media: [10, 15]                         # PROPOSTA approvata
dialogo_percento: [30, 50]                    # PROPOSTA approvata
similitudini_max_per_parole: 300              # PROPOSTA da confermare: valore non presente nelle tabelle approvate
parole_filtro: {modalita: avviso, massimo_per_1000_parole: 8}   # elenco 05 r. 21; il numero è PROPOSTA approvata
lista_nera: dati/lista-nera.yaml              # 05 rr. 19-20
parole_per_pagina: 250                        # 12 r. 7 (PROPOSTA approvata)
scene_obbligatorie:
  - incidente scatenante che promette il climax   # 02 r. 19
  - scelta di identità del protagonista       # PROPOSTA approvata
  - prova tra pari                            # PROPOSTA approvata
```

### B.7 Ordine di costruzione

**Nessun libro reale tra i casi di prova.** Ogni passo si prova solo sui due mini-libri inventati di `motore/prove/` (giallo e romance, B.2.2), confrontando gli esiti con `prove/attesi.yaml`. Le prove girano su copie dei mini-libri in una cartella temporanea.

| Passo | File creati | Prova | Criterio di superamento |
|---|---|---|---|
| **1. Fondamenta** | `script/comune.py`, `script/conta.py`; `dati/libro.schema.yaml`, `dati/profilo.schema.yaml`, `dati/stato.schema.yaml`, `dati/lingue.yaml`; `profili/` (7 file); `script/valida_profili.py`; `prove/mini-libro/`, `prove/mini-libro-romance/`; `prove/attesi.yaml`; `dati/nomi_vietati.txt` (vuoto); `script/separazione.py`, `script/recinto.py` | `valida_profili.py` sui 7 profili; `libro.yaml` dei due mini-libri contro lo schema; un `libro.yaml` con `lingua: en` e uno con un override senza motivo; `conta.py` sui due mini-libri; `separazione.py` su `motore/`; `recinto.py` con una scrittura fuori dal libro messa apposta | profili e schemi validi; `lingua: en` e override senza motivo rifiutati; parole per capitolo e totale uguali ad `attesi.yaml`; `separazione.py` esce con 0; `recinto.py` rileva la scrittura messa apposta |
| **2. Controlli del testo** | `script/stile.py`, `dati/lista-nera.yaml`, `script/continuita.py`, `script/riciclo.py`, `script/capitolo.py` | i capitoli con errori voluti del mini-libro giallo; il capitolo-prova e la pagina-prova comuni ai due mini-libri | esattamente i KO e gli avvisi di `attesi.yaml`, nessuno in più e nessuno in meno; lo stesso testo dà OK nel giallo e KO nel romance dove previsto (minimo di parole, frase media, dialogo, chiusure) |
| **3. Stampa** | `script/compila.py`, `script/impagina.py`, `stampa/modello.css`, `stampa/print.js`, `stampa/font/` con `FONTI.yaml` e `OFL.txt`, `script/verifica_pdf.py` | `compila` + `impagina` + `pdf` sui due mini-libri | font scaricati dalle fonti ufficiali, con sha256 registrati; PDF con tutti i font incorporati e nessun Type3; margini ≥ max(tabella KDP, valori di `libro.yaml`); indice uguale alle pagine reali; numero di pagine e sha256 fissati in `attesi.yaml` con l'«ok» dell'autore |
| **4. Pubblicazione** | `dati/kdp.yaml`, `dati/verifiche-kdp.md`, `script/conformita_kdp.py`, `script/kdp_verifica.py`, `script/pacchetto.py`; `modelli/conferme-autore.yaml` | `kdp` e `pacchetto` sui due mini-libri (uno con `ebook: true` e `serie`); `verifica KDP fatta` con una data futura e con una data valida | sezioni 1-15 con gli esiti di `attesi.yaml`; avviso «verifica mai fatta»; promemoria dei sette valori se il proxy blocca; data futura rifiutata; `recinto.py` riconosce l'eccezione dichiarata |
| **5. Conduzione** | `script/avvio.py`, `script/nuovo.py`, `script/fase.py`, `script/revisione.py`, `script/hook_sessione.py`, `script/hook_manoscritto.py`, `dati/hook.yaml` (modalità avviso), `modelli/` (briefing, libro.yaml, LEGGIMI, stato, cronologia), `PROCEDURA.md`, `README.md`, `CLAUDE.md`, `zb` | `zb nuovo` su un briefing inventato in una cartella temporanea; `zb avvio` e i gate G0-G1 sul mini-libro giallo; hook in modalità avviso sui 14 scenari di C.4, su una copia del mini-libro | struttura creata; `avvio.py` stampa la riga «Letto: …» e si ferma in tutti i casi di C.4; `ok`, `avanti`, `correggi`, `stato` producono gli effetti di C.1; l'hook avvisa e non blocca; `separazione.py` e `recinto.py` ancora a 0 |

Ogni passo: codice → prova sui mini-libri → confronto con `attesi.yaml` → commit e push secondo B.5. Si passa al passo successivo solo con tutti i criteri superati e l'«ok» dell'autore.

### B.8 Riferimenti copiati in `motore/riferimenti/`

**Cosa si copia.** Da NGTAProtocol/casa-editrice, `origin/main` @ becd0e2, con `git show` (sola lettura):
- i 12 file di `.claude/skills/casa-editrice/riferimenti/` → `motore/riferimenti/`;
- i 7 file di `.claude/skills/casa-editrice/modelli/` → `motore/riferimenti/modelli/`.

**Intestazione** in testa a ogni file copiato, come prima riga, seguita da una riga vuota (le righe originali scendono di 2; i numeri qui sotto sono quelli dell'originale):

```
> Fonte: NGTAProtocol/casa-editrice main @ becd0e2, copiato il AAAA-MM-GG. Righe rese parametriche: vedi motore/proposta-motore.md B.8.
```

**Regola.** Nessun adattamento per un singolo libro. Solo i valori che cambiano da un libro all'altro diventano un rimando a un parametro: tipo di chiusura, lunghezze e tolleranze, lista nera, metodo di conteggio, unità senza numero. Il valore di casa-editrice resta scritto come predefinito.

| File | Esito |
|---|---|
| `01-mercato.md` | generico così com'è |
| `02-architettura.md` | **reso parametrico** (r. 39) |
| `03-stesura.md` | **reso parametrico** (rr. 12, 24) |
| `04-editing-sviluppo.md` | generico così com'è |
| `05-critica-e-punteggio.md` | **reso parametrico** (una riga aggiunta dopo la r. 21) |
| `06-lettori-beta.md` | generico così com'è |
| `07-copyediting.md` | generico così com'è |
| `08-pubblicazione.md` | generico così com'è |
| `09-edizione-inglese.md` | generico così com'è |
| `10-lancio.md` | generico così com'è |
| `11-direttive-kdp.md` | generico così com'è (i valori sono anche in `dati/kdp.yaml`) |
| `12-lunghezze-e-struttura-capitoli.md` | **reso parametrico** (rr. 6, 30, 66, 67; una riga aggiunta dopo la r. 28) |
| `modelli/` (7 file) | generici così come sono |

Rispetto alla versione precedente della proposta, `08-pubblicazione.md` torna invariato: la regola sugli interludi era nata per un libro. Le unità senza numero stanno in `struttura` di `libro.yaml` e `compila.py` le mette nel sommario da lì.

**Righe rese parametriche**

1. `02-architettura.md` r. 39
   - Prima: `… un capitolo = 1-4 scene, chiuso da un gancio (domanda, rivelazione, pericolo, decisione).`
   - Dopo: `… un capitolo = 1-4 scene, chiuso secondo `chiusura_preferita` del profilo o di libro.yaml (predefinito: un gancio — domanda, rivelazione, pericolo, decisione).`
2. `03-stesura.md` r. 12
   - Prima: `9. **Chiusura di capitolo**: interrompi sul massimo della domanda, non sulla risposta.`
   - Dopo: `9. **Chiusura di capitolo**: secondo `chiusura_preferita` del profilo o di libro.yaml (predefinito: interrompi sul massimo della domanda, non sulla risposta).`
3. `03-stesura.md` r. 24
   - Prima: `Rispetta il budget del capitolo e delle scene in 03-struttura/piano-parole.md (tolleranza ±15%, vedi …).`
   - Dopo: `Rispetta il budget del capitolo e delle scene in 03-struttura/piano-parole.md (tolleranza `capitoli.tolleranza_budget`, predefinita ±15%, vedi …).`
4. `05-critica-e-punteggio.md`, dopo r. 21 (riga aggiunta, nessuna tolta)
   - Prima: (nessuna riga)
   - Dopo: `La lista base è in motore/dati/lista-nera.yaml; il libro aggiunge voci in libro.yaml (`voci`) e può cambiare un tetto solo con un override motivato.`
5. `12-lunghezze-e-struttura-capitoli.md` r. 6
   - Prima: `- Si conta in **parole** (comando `wc -w` sul file del capitolo, esclusi titoli e note).`
   - Dopo: `- Si conta in **parole** con il metodo `parole.metodo` di libro.yaml (predefinito: metodo unico, motore/script/conta.py), esclusi titoli e note.`
6. `12-lunghezze-e-struttura-capitoli.md`, dopo r. 28 (riga aggiunta)
   - Prima: (nessuna riga)
   - Dopo: `I valori di questa tabella sono i default dei profili in motore/profili/; il libro li sceglie con `profilo:` e li corregge con `override`.`
7. `12-lunghezze-e-struttura-capitoli.md` r. 30
   - Prima: `… salvo scelta narrativa dichiarata nella griglia (es. capitolo-shock di una pagina).`
   - Dopo: `… salvo scelta narrativa dichiarata nella griglia o in un `override` di libro.yaml (es. capitolo-shock di una pagina).`
8. `12-lunghezze-e-struttura-capitoli.md` r. 66
   - Prima: `- Dopo ogni capitolo conta le parole e aggiorna "Parole reali" e "Scarto".`
   - Dopo: `- Dopo ogni capitolo conta le parole con conta.py e aggiorna "Parole reali" e "Scarto".`
9. `12-lunghezze-e-struttura-capitoli.md` r. 67
   - Prima: `- Tolleranza: ±15% per capitolo; ±5% sul totale del libro.`
   - Dopo: `- Tolleranza: `capitoli.tolleranza_budget` sul budget del capitolo in piano-parole.md (predefinita ±15%); `capitoli.tolleranza_totale` sul totale (predefinita ±5%).`

**Verifica della copia.** Un caso di prova confronta ogni file copiato con l'originale (`git show`). La differenza ammessa è solo l'intestazione più le 9 righe sopra; qualsiasi altra differenza è un KO.

### B.9 Separazione tra motore e libri

**`motore/script/separazione.py`** fallisce (codice d'uscita 1, con file e riga) se:
1. sotto `motore/` c'è un percorso che contiene un segmento `libri/`, o un file che è copia identica (stesso sha256) di un file che sta fuori da `motore/` in una cartella con `libro.yaml`;
2. in un file di `motore/` compare, come parola intera e senza distinguere le maiuscole, una voce di `motore/dati/nomi_vietati.txt`;
3. in `motore/` c'è un file `libro.yaml` fuori da `motore/prove/mini-libro/` e `motore/prove/mini-libro-romance/`.

**Eccezione per i font.** I file di `motore/stampa/font/` elencati in `FONTI.yaml`, con lo sha256 registrato, non sono segnalati dal punto 1: un font OFL ufficiale può essere identico a una copia dello stesso font usata da un libro. Un file in `stampa/font/` che **non** è in `FONTI.yaml`, o ha uno sha256 diverso, resta un KO.

`nomi_vietati.txt` lo compila l'autore quando serve, una voce per riga: titoli, personaggi, luoghi dei libri veri. Le righe che cominciano con `#` sono commenti. Il file stesso è escluso dal controllo. Il motore non aggiunge voci da solo.

**`motore/script/recinto.py`** fallisce se un comando scrive fuori dalla cartella del libro indicato. Ha due livelli:
- **in esecuzione:** ogni script scrive solo tramite `comune.scrivi(percorso, …)`. La funzione risolve il percorso reale, seguendo anche i collegamenti simbolici, e solleva un errore se non sta sotto `<libro>`. L'unica eccezione dichiarata è `verifica KDP fatta`, che scrive in `motore/dati/`;
- **in prova:** `recinto.py` copia il mini-libro in una cartella temporanea, fotografa il file system fuori dalla copia (percorsi, dimensioni, sha256 di `motore/` e del repository), esegue ogni comando e confronta. Qualsiasi file creato o cambiato fuori dalla copia è un KO, con il nome del comando. **Eccezione ammessa:** `verifica KDP fatta` scrive in `motore/dati/kdp.yaml` e `motore/dati/verifiche-kdp.md`; `recinto.py` la riconosce dal nome del comando e da questi due percorsi esatti, la riporta nel report come «eccezione dichiarata» e **non** la segnala come violazione. Qualsiasi altro file toccato da quel comando, o gli stessi file toccati da un altro comando, resta un KO.

Tutti e due girano nel passo 1 di B.7 e prima di ogni commit nel ramo del motore.

---

## C. Funzionamento quasi automatico

Obiettivo: l'autore scrive solo il briefing e risponde «ok», «avanti», «correggi: …», «stato» o «prepara per revisione». Tutto il resto si legge da file nella cartella del libro: lo stato, le fasi, i controlli e i punti di approvazione. Nessun prompt da incollare a ogni passo.

### C.1 Macchina a stati

**File:** `<libro>/stato.yaml`, scritto solo da `motore/script/fase.py`.

```yaml
libro: "<titolo>"
motore_commit: "<hash>"        # commit del motore usato (B.4)
ramo_ultimo_salvataggio: "<ramo>"   # solo informativo, scritto da fase.py
fase: 0                        # 0-8, oppure "chiuso"
passo: briefing                # sottopasso della fase
gate_in_attesa: G0             # null se nessun gate è aperto
lotto: {dimensione: 3, capitoli: []}   # fase 5
ultimo_capitolo_approvato: null
parole: {scritte: 0, obiettivo: <target_totale>, metodo: unico}
documenti_approvati: {}        # percorso → {sha256, commit} dell'approvazione
avvisi_aperti: []              # {id, fonte, testo}
revisione_in_corso: null       # {documento, blocco, blocchi_totali, sha256}
push_in_sospeso: false
aggiornato: AAAA-MM-GGThh:mm:ssZ
```

**Tabella delle fasi**

| Fase | Legge | Produce | Controlli automatici | Gate |
|---|---|---|---|---|
| 0 Avvio | `00-progetto/briefing.md`, `motore/modelli/` | cartelle `00-06`, `libro.yaml`, `stato.yaml`, `LEGGIMI.md`, file dai modelli | briefing completo (C.3); nome autore; ramo | **G0** domande (massimo 5, solo se mancano dati essenziali) e conferma di `libro.yaml` |
| 1 Bibbia | briefing, `libro.yaml`; `testo_precedente` se c'è | `02-bibbia/bibbia.md` (personaggi, luoghi, cronologia, motivi con tetti) | nomi unici, età coerenti con la cronologia, ogni fatto canonico del briefing presente, marche [PROPOSTA] contate | **G1** bibbia |
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
| `prepara per revisione` | Vedi C.6. Non scrive nulla. |
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
   - anti-riciclo a 7 parole (`riciclo.py`): ogni sequenza di 7 parole uguale al `testo_precedente` del libro (se dichiarato in `libro.yaml`) o a un capitolo già scritto, con file e riga;
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
Autore:
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

**`CLAUDE.md` alla radice del repository dei libri** (testo completo, generico):

```markdown
# Regole di avvio

Il libro su cui lavorare lo indica l'autore con un percorso. Se non l'ha
indicato, chiedilo prima di toccare qualunque file.

Prima di toccare qualunque file:
1. Leggi `motore/PROCEDURA.md` (o quella del motore indicato da ZB_RADICE).
2. Esegui `zb avvio <libro>` e riporta la sua riga «Letto: …».
   Se si ferma, fermati anche tu e riporta il motivo.
3. Leggi il `LEGGIMI.md` del libro.

Precedenza: manuale e libro.yaml del libro > profilo di genere >
procedura del motore > skill dell'autore. Segnala ogni contrasto nel report.

Metodo: proponi → l'autore approva → applica. Mai approvare da solo.
Risposte dell'autore: ok, avanti, correggi: …, stato, prepara per revisione
(significato in `motore/PROCEDURA.md`, sezione gate).

Ramo: solo quello assegnato dalla sessione (letto da git). Scrivi solo
dentro la cartella del libro indicato.

Tono: il testo precedente di un libro è un registro dei fatti,
non va commentato né giudicato.

Salvataggio a ogni passo: git add, commit, push, git status -sb, git log -1.
Se il push fallisce o un file non si salva: fermati e riporta l'errore.
Non dire «fatto» se non è su origin. Resoconto con hash, file,
parole/pagine e «branch allineato a origin: sì/no».
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

**Quale libro.**
- Nessun «libro attivo» scritto in un file: il libro si passa a ogni comando (B.4).
- `ZB_LIBRO` può fare da predefinito per la sessione; `avvio.py` stampa sempre il percorso risolto.
- Il ramo non è scritto in nessun file: `comune.py` lo legge da git.
- Più libri nello stesso repository o sullo stesso ramo non sono un problema: ogni comando opera solo nella cartella indicata.

**`motore/script/avvio.py`**

Cosa stampa:
1. percorso risolto del libro, ramo, ultimo commit del libro e commit del motore, allineamento con origin;
2. fase, passo, gate in attesa, ultimo capitolo approvato, parole scritte/obiettivo;
3. i file da leggere per la fase corrente, ciascuno con righe e sha256 (12 caratteri);
4. avvisi aperti;
5. in fase 8: età della verifica delle direttive KDP.

Quando si ferma (codice d'uscita diverso da zero):
- checkout su un ramo diverso da quello della sessione, o nessun `libro.yaml` nel percorso indicato;
- repository del libro non scrivibile (B.4);
- modifiche non salvate nel checkout, o ramo indietro rispetto a origin;
- `stato.yaml` mancante o non valido;
- sha256 di un documento approvato diverso da quello registrato (modificato fuori procedura);
- in fase 0: briefing incompleto (C.3);
- `push_in_sospeso: true` (C.5).

**Marker di sessione.** Quando `avvio.py` termina senza errori scrive `<libro>/.zb/letto-<session_id>` con la data, il commit e gli sha256 dei file letti. `.zb/` va in `.gitignore`. Il `session_id` lo deposita l'hook SessionStart in `$CLAUDE_PROJECT_DIR/.zb/sessione-corrente`: è l'unica scrittura fuori da una cartella di libro, ed è dell'hook, non di un comando. Se non c'è un hook, `avvio.py` usa un identificativo locale e lo dichiara.

**Frase di conferma** prima di ogni scrittura (stampata da `avvio.py`, ripetuta da me):

```
Letto: <libro>/libro.yaml (N righe, sha256 …), stato.yaml (N righe, sha256 …),
profilo thriller (N righe, sha256 …), <manuale> (N righe, sha256 …), …;
libro @ <commit> «…»; motore @ <commit>; fase N, gate GN.
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
  - **avviso** (iniziale): se il percorso è sotto `<x>/04-manoscritto/` di una cartella `<x>` che contiene `libro.yaml`, e manca `<x>/.zb/letto-<session_id>`, stampa «ATTENZIONE: avvio.py non eseguito in questa sessione; scrittura nel manoscritto non verificata» ed esce con 0, quindi **non blocca**. Ogni avviso finisce anche in `.zb/avvisi-hook.log`;
  - **blocco**: stesso controllo, ma esce con codice 2 e il messaggio «Esegui motore/script/avvio.py prima di scrivere nel manoscritto».

**Passaggio da avviso a blocco.** Solo dopo una prova superata, in una cartella temporanea fuori dal repo (una copia del mini-libro, per esempio `/tmp/zb-prova-hook/mini-libro/04-manoscritto/01-prova.md`):
1. senza marker: Write, Edit e i comandi Bash dei casi della tabella qui sotto. Atteso: blocco dove previsto;
2. con marker: le stesse operazioni. Atteso: nessun blocco;
3. scritture fuori dal manoscritto: mai bloccate;
4. hook con un errore volontario: per i percorsi fuori dal manoscritto lascia passare.

L'esito si mostra in una tabella. Il passaggio a `modalita: blocco` è un commit a parte, dopo il tuo «ok».

**Rilevamento delle scritture via Bash: scenari di errore**

Il comando Bash arriva all'hook come testo. L'hook lo considera una scrittura nel manoscritto se contiene `04-manoscritto` insieme a un operatore di scrittura: `>`, `>>`, `tee`, `sed -i`, `perl -i`, `mv`, `cp`, `rm`, `truncate`, `git checkout --`, `git restore`, `python`.

| # | Scenario | Tipo di errore | Cosa fa il sistema |
|---|---|---|---|
| 1 | `grep -n x romanzi/esempio/04-manoscritto/01.md > /tmp/out.txt` (lettura, con redirezione verso un altro file) | falso blocco | L'hook guarda dove punta la redirezione: se il bersaglio di `>` non è in `04-manoscritto` lascia passare. In modalità avviso non blocca comunque. |
| 2 | `python3 motore/script/capitolo.py 01` (legge il manoscritto, non lo nomina) | nessun errore | Lascia passare: il percorso non compare. |
| 3 | `python3 -c "open('romanzi/esempio/04-manoscritto/01.md','w')…"` | rilevato | Blocca (o avvisa): compaiono `python` e il percorso. |
| 4 | Uno script che scrive nel manoscritto senza nominarlo nel comando (`python3 /tmp/s.py`) | falso permesso | Non rilevabile dall'hook. Lo copre `avvio.py` al passo successivo: lo sha256 di un capitolo approvato cambiato fuori procedura ferma il lavoro (C.4). |
| 5 | Percorso costruito con variabili (`D=romanzi/esempio/04-manoscritto; echo x > $D/01.md`) | falso permesso | Non rilevabile con certezza. L'hook cerca anche `04-manoscritto` nelle assegnazioni di variabili dello stesso comando; il resto lo copre il controllo sha256 di `avvio.py`. |
| 6 | `cd romanzi/esempio/04-manoscritto && sed -i … 01.md` | rilevato | Blocca: `04-manoscritto` e `sed -i` nello stesso comando. |
| 7 | `cd romanzi/esempio/04-manoscritto` in un comando precedente, poi `sed -i … 01.md` | falso permesso | Non rilevabile, perché il comando non nomina la cartella. Lo copre il controllo sha256 di `avvio.py`. |
| 8 | `git commit` o `git push` con file del manoscritto in stage | falso blocco evitato | `git add/commit/push/status/log/diff` non sono operatori di scrittura: lascia passare. |
| 9 | `git checkout -- romanzi/esempio/04-manoscritto/01.md` o `git restore …` | rilevato | Blocca (o avvisa): sovrascrive il capitolo. |
| 10 | `cp romanzi/esempio/04-manoscritto/01.md /tmp/copia.md` (copia in uscita) | falso blocco | L'hook guarda l'ultimo argomento di `cp`/`mv`: se la destinazione è fuori dal manoscritto lascia passare. `mv` con sorgente nel manoscritto invece blocca, perché toglie il file. |
| 11 | `cat romanzi/esempio/04-manoscritto/*.md \| wc -w` | nessun errore | Lascia passare: nessun operatore di scrittura. |
| 12 | Un percorso che contiene `04-manoscritto` fuori da una cartella con `libro.yaml` (per esempio nella proposta) | falso blocco | L'hook richiede che sopra `04-manoscritto` ci sia un `libro.yaml`: lascia passare. |
| 13 | L'hook stesso va in errore (JSON illeggibile, Python mancante) | falso blocco o falso permesso | In modalità avviso lascia sempre passare e lo scrive nel log. In modalità blocco blocca solo se il testo contiene `04-manoscritto`, altrimenti lascia passare. |
| 14 | Contesto compattato: il marker viene cancellato (`source: compact`) | blocco voluto | Il messaggio chiede di rieseguire `avvio.py`; dopo la rilettura si procede. |

Rischi che restano:
- **Garanzia:** l'hook è una protezione in più, non una garanzia. La regola resta in `CLAUDE.md` e in `PROCEDURA.md`, e il controllo sha256 di `avvio.py` copre i casi 4, 5 e 7.
- **Portata:** `.claude/settings.json` nel repo vale per ogni sessione su quel ramo e su ogni ramo in cui venga unito (C.7).
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

### C.6 Secondo lettore

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

### C.7 Come il motore arriva ai libri

**Situazione verificata il 2026-10-02 con `git ls-remote --symref origin HEAD`.**
- Nel repository ZeusBot non esiste un ramo `main`.
- Il ramo principale (HEAD di GitHub) è **`claude/claude-rc-4umw8n`** (ultimo commit 28560a6). Contiene solo `.gitignore` e `ghimoney/`.

**Proposta.**
1. Un ramo solo per il motore, per esempio `claude/motore`, creato dal ramo principale. Contiene **solo** `motore/` (più `CLAUDE.md` e `.claude/settings.json` quando esisteranno). Nessuna cartella di libro. Creare questo ramo richiede il permesso esplicito dell'autore, perché è diverso dal ramo assegnato alla sessione.
2. L'autore apre su GitHub la pull request `claude/motore` → ramo principale e fa il merge. Prima della PR, `separazione.py` deve uscire con 0.
3. I rami dei libri ricevono il motore con `git merge` del ramo principale: un commit di merge, nessuna riscrittura della storia. Il ramo principale non contiene libri, quindi il merge aggiunge solo `motore/` e non tocca le cartelle dei libri.
4. Un libro nuovo nasce su un ramo creato dal ramo principale, e ha già il motore.
5. Gli aggiornamenti del motore si fanno su `claude/motore` → PR → merge nel principale → merge del principale nei rami dei libri.

**In alternativa, motore in un repository separato** (B.4): i libri non contengono `motore/`; la sessione clona il repository del motore in lettura e usa `--radice` o `ZB_RADICE`. Nessun merge nei rami dei libri; il commit del motore usato resta in `stato.yaml`.

**Se l'autore non può fare il merge nel ramo principale** (ramo protetto, permessi, scelta):
- **Alternativa A:** merge di `claude/motore` direttamente in ciascun ramo di libro. Ogni aggiornamento va unito ramo per ramo.
- **Alternativa B:** motore in un repository separato, come sopra.
- In tutti i casi: niente force push, niente rebase dei rami dei libri, niente tag. Se un push fallisce mi fermo e riporto l'errore.

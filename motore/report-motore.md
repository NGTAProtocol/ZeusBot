# Report del motore editoriale

Stato al 2026-10-15, ramo `motore`. Suite: **520/520 OK**, 0 saltate, 0 KO (con LanguageTool 6.8).
Il motore è una fabbrica generica di romanzi in italiano: procedura, script, modelli vuoti, profili
di genere, dati KDP, il livello editoriale (`editoriale/`) e mini-libri inventati per le prove. Non contiene
libri reali.

## 1. Struttura

| Percorso | Contenuto |
|---|---|
| `CLAUDE.md` | regole di avvio delle sessioni che lavorano su un libro |
| `.gitignore` | file Python generati, ambienti virtuali |
| `motore/zb` | punto d'ingresso unico: `python3 motore/zb <comando> …` |
| `motore/script/` | 33 moduli Python: controlli, fasi, ruoli, cartella unica, anti-IA, agenti, capsule, consumo, stampa, KDP, voci, prove |
| `motore/editoriale/` | livello editoriale dell'autore: percorso, ruoli (con riferimenti), agenti, struttura e modelli, anti-IA, correttore, risparmio di token, glossario |
| `motore/requirements.txt` | dipendenze Python |
| `motore/stampa/` | foglio di stile, render con Chromium, font EB Garamond |
| `motore/dati/` | schemi, dati KDP, lista nera, lingue, struttura standard di un libro |
| `motore/modelli/` | modelli vuoti per un libro nuovo |
| `motore/profili/` | 7 profili di genere con i valori predefiniti |
| `motore/prove/` | mini-libri inventati, mini-banca-voci inventata, `attesi.yaml`, esiti dei passi di sviluppo |
| `motore/README.md` | regole d'uso, comandi, ambiente |
| `motore/PROCEDURA.md` | come si lavora su un libro, passo per passo |
| `motore/proposta-motore.md` | progetto approvato del motore (riferimento delle sigle A.x, B.x, C.x) |
| `motore/report-motore.md` | questo report |
| `motore/passaggio-di-consegne.md` | riepilogo breve per ripartire in una nuova chat |

## 2. Moduli e script

| Modulo | A cosa serve |
|---|---|
| `zb` | smista i comandi verso gli script; `zb aiuto` li elenca |
| `comune.py` | funzioni comuni: lettura e validazione di `libro.yaml`, percorsi dentro il libro, dati KDP, date, sessione |
| `fase.py` | macchina a stati del libro (struttura, documenti, pagina campione, stesura, revisione del manoscritto, line, copy, bozze, chiusura), gate con controlli della struttura, `zb pronto/ok/avanti/correggi/riapprova/esito`; unico script che scrive `stato.yaml` |
| `ruoli.py` | un ruolo per sessione, separazione tra chi scrive e chi revisiona (`zb ruoli`) |
| `cartella_unica.py` | niente fuori da `libri/<slug>/`: file modificati, commit misti, nome del libro (`zb cartella`, `avvio`, `push`) |
| `anti_ia.py` | misure della sezione H del catalogo anti-IA, in audit, dentro `zb esito` |
| `installa_languagetool.py` | `zb ortografia installa|verifica`: LanguageTool fuori dal repository |
| `agenti.py`, `capsule.py`, `consumo.py` | subagenti (`zb agenti`), capsule di continuità (`zb capsula`), misura della sessione (`zb consumo`) | |
| `avvio.py` | controlli d'avvio e riga «Letto: …» (`zb avvio`); con la voce, anche briefing e scheda della voce |
| `voce.py` | voci narrative della banca-voci (`ZB_BANCA_VOCI`): `zb voce lista`, `mostra <slug> [N]`, `verifica <slug>`; divieti della voce per `stile.py` |
| `nuovo.py` | crea un libro dal briefing (`zb nuovo`) |
| `adotta.py` | bozze di `libro.yaml`, stato, cronologia e nomi per un libro già avviato (`zb adotta`) |
| `conta.py` | conteggio delle parole con il metodo unico; stampa a schermo, non scrive |
| `capitolo.py` | tutti i controlli di un capitolo in un colpo solo (dentro `zb esito`), più anti-IA e Gulpease informativo |
| `stile.py` | frase media, dialogo, lista nera e voci, divieti della voce narrativa (avviso), tetti, similitudini, vincoli, eccezioni motivate |
| `riciclo.py` | anti-riciclo a 7 parole tra unità, con i richiami ammessi |
| `continuita.py` | date, età, durate, tempi relativi, cifre, nomi scritti in due modi, fatti incompatibili |
| `ortografia.py` | Hunspell it_IT, LanguageTool se disponibile, checklist per la lettura umana |
| `revisione.py` | mostra un documento o un gate in blocchi di circa 120 righe; sola lettura |
| `compila.py` | manoscritto completo in `05-output/<titolo>-completo.md` |
| `impagina.py` | PDF di stampa: render con Chromium, sommario con le pagine reali, numeri di pagina, formato esatto, bleed, metadati |
| `verifica_pdf.py` | verifica del PDF (pagine, metadati, font, margini, sommario, parole per pagina) |
| `conformita_kdp.py` | conformità KDP in 15 sezioni, report in `06-pubblicazione/` |
| `kdp_verifica.py` | registra la verifica delle direttive KDP fatta dall'autore (`zb verifica KDP fatta`) |
| `pacchetto.py` | struttura di `06-pubblicazione/` per KDP |
| `push.py` | cartella unica e prove (sul motore) prima del push; push con 4 tentativi, poi ramo di salvataggio, poi git bundle (`zb push`) |
| `hook_sessione.py`, `hook_manoscritto.py`, `hook_recinto.py` | hook di Claude Code (SessionStart, PreToolUse): sessione, manoscritto (avviso), recinto e cartella unica anche su Bash (blocco) |
| `separazione.py` | controlla che `motore/` non contenga libri |
| `recinto.py` | controlla che i comandi scrivano solo dentro il libro indicato |
| `valida_profili.py` | valida i profili di genere contro lo schema |
| `prove.py` | suite di prove sui mini-libri inventati (`zb prove`) |
| `stampa/modello.css` | foglio di stile parametrico: formato, margini a specchio, font, corpo |
| `stampa/print.js` | render HTML → PDF con Chromium di Playwright (Node) |
| `stampa/font/` | EB Garamond Regular, Italic, SemiBold (.ttf statici), licenza OFL, `FONTI.yaml` con gli sha256 |

## 3. Dati, modelli, profili

| File | Contenuto | Chi lo usa |
|---|---|---|
| `dati/kdp.yaml` | direttive KDP come dati (metadati, parole vietate, cartaceo, ISBN, dichiarazione AI) | `comune.py`, `verifica_pdf.py`, `conformita_kdp.py`, `impagina.py`, `pacchetto.py`, `prove.py` |
| `dati/verifiche-kdp.md` | registro delle verifiche dell'autore sulle pagine ufficiali | `kdp_verifica.py` |
| `dati/libro.schema.yaml`, `stato.schema.yaml`, `profilo.schema.yaml` | schemi di `libro.yaml`, `stato.yaml` e dei profili | `comune.py`, `valida_profili.py` |
| `dati/lingue.yaml` | lingue supportate (solo `it`) | `comune.py`, `ortografia.py` |
| `dati/lista-nera.yaml` | espressioni da evitare (base); il libro aggiunge le sue voci | `stile.py` |
| `dati/parole-ammesse-it.txt` | forme italiane valide ignote a Hunspell; mai nomi propri | `ortografia.py` |
| `dati/nomi_vietati.txt` | nomi che non devono comparire in `motore/`; vuoto | `separazione.py` |
| `dati/struttura-libro.yaml` | cartelle standard di un libro, con scopo e momento di creazione | `nuovo.py`, `comune.py` |
| `dati/hook.yaml`, `hook-settings.esempio.json` | modalità degli hook e impostazioni d'esempio | hook, `zb hook` |
| `modelli/` | `briefing.md`, `libro.yaml`, `stato.yaml`, `cronologia.yaml`, `LEGGIMI.md`, `conferme-autore.yaml` | `nuovo.py`, `adotta.py`, `conformita_kdp.py` |
| `profili/` | fantascienza, fantasy, giallo, narrativa letteraria, romance, thriller, young adult: valori predefiniti di lunghezze, stile, scene | `nuovo.py`, `stile.py`, `capitolo.py` |

## 4. Vincoli KDP applicati

Fonte: `dati/kdp.yaml`, ricavato dalle direttive del repository casa-editrice (main @ becd0e2) e dal
KDP Help Center. `ultima_verifica: null`: l'autore non ha ancora riverificato le pagine ufficiali
(validità prevista 30 giorni).

- Pagine: minimo 24; massimo 828 (carta bianca) o 776 (crema). Numero dispari: AVVISO.
- Margine interno minimo per numero di pagine: 24-150 → 0,375″; 151-300 → 0,5″; 301-500 → 0,625″;
  501-700 → 0,75″; 701-828 → 0,875″. Sotto le 24 pagine vale la prima fascia.
- Margine esterno minimo (vale anche per alto e basso): 0,25″ senza bleed, 0,375″ con bleed.
- Bleed: 0,125″. Pagina con bleed = trim + 0,125″ in larghezza e + 0,25″ in altezza.
- Formati citati: 6 × 9, 5 × 8, 5,25 × 8, 5,5 × 8,5 (elenco non chiuso). Un formato diverso
  (per esempio A5, 5,83 × 8,27) va confermato in `libro.yaml` (`formato_confermato_kdp`).
- Font: tutti incorporati, nessun Type3.
- Metadati, parole vietate, descrizione, parole chiave, categorie, ISBN, dichiarazione AI:
  `conformita_kdp.py`, sezioni 1-15.

## 5. `verifica_pdf.py`: cosa misura e cosa no

Misura:
- pagine (`pdfinfo`) e numero pari;
- Title e Author uguali a `libro.yaml`;
- font (`pdffonts`): incorporati, nessun Type3;
- margini (`pdftotext -bbox`): interno (sinistra sulle dispari, destra sulle pari), esterno, alto,
  basso, contro i minimi KDP;
- sommario contro le pagine reali; parole per pagina.

Non misura:
- TrimBox e BleedBox: non vengono scritti (MediaBox e CropBox coincidono con il formato);
- trasparenze, immagini e loro risoluzione, colori: il motore non li gestisce;
- formato della pagina: lo controlla la prova strutturale di `prove.py` e la sezione 11 di
  `conformita_kdp.py`, non `verifica_pdf.py`;
- i margini sono misurati sul bordo del testo, non sui box del PDF.

## 6. Mini-libri e prove

Mini-libri inventati in `prove/`: giallo (`mini-libro`, A5, 16 pagine), romance (`mini-libro-romance`,
5,5 × 8,5, 23 pagine), adozione (`mini-libro-adozione`), più briefing e schede di pubblicazione
inventati. Autori inventati («Autore di Prova», «Autrice di Prova»).

| Sezione | Prove | Copre |
|---|---|---|
| passo 1 | 35 | conteggio parole, profili |
| passo 2 | 52 | stile, riciclo, capitolo |
| passo 3 | 45 | compila, impagina, verifica PDF: struttura, margini con tolleranza e minimi KDP, bleed |
| passo 4 | 38 | conformità KDP, sezioni 1-15 |
| passo 5 | 97 | fasi, gate, avvio, hook, CLAUDE.md |
| passo 5b | 18 | `zb adotta` |
| passo 6 | 6 | struttura (le prove di pulizia sono su archivio/motore-ritirati) |
| passo 7 | 11 | ortografia, LanguageTool |
| override | 8 | override motivati sulla lunghezza |
| scene | 12 | controllo delle scene |
| manuale | 7 | manuale generato |
| checklist | 3 | checklist di capitolo |
| continuita | 8 | durate ed età |
| correzioni | 20 | correzioni dopo la prova |
| adozione | 5 | libri esistenti |
| interludi e grafie | 10 | interludi in anticipo, impronte, grafie, battute del manuale |
| correggi e passo | 4 | correzioni e passo |
| unità consentite e interludi | 7 | unità consentite |
| fase e rinomine | 6 | fase di stesura, rinomine |
| esclusioni e budget | 6 | escludi_pattern, pattern «Non era X. Era Y.», budget degli interludi, chiusura |
| titoli, tempi, età, push | 23 | titoli, tempi relativi, età, fatti incompatibili, push |
| eccezioni e richiami | 3 | eccezioni motivate, richiami ammessi |
| voce | 25 | `zb voce` sulla mini-banca inventata (solo schede), regressioni della scheda, assenza di `ZB_BANCA_VOCI`, voce non pronta, libro senza voce invariato, «Letto» con la voce, divieti in AVVISO, modello del briefing |
| recinto libro | 3 |  |
| appendici | 6 |  |
| fase struttura | 18 | fase struttura e gate su due briefing inventati |
| cartella unica | 13 | cartella unica, recinto su Bash, push |
| ruoli | 9 | un ruolo per sessione, separazione tra chi scrive e chi revisiona |
| anti-IA | 7 | misure della sezione H, audit, blocco |
| correttore | 5 | lista di controllo dai criteri, installazione e verifica di LanguageTool |
| agenti e capsule | 10 | subagenti, modelli centrali, capsule, revisori con Edit, consumo, output compatto |
| **Totale** | **520** | più `separazione.py` e `recinto.py` (46 esecuzioni) |

Non coperto dalle prove: libri oltre le 24 pagine, quindi le fasce interne oltre la prima;
`zb pacchetto` su un libro completo; un PDF con immagini; i formati citati diversi da 5,5 × 8,5 e A5;
gli hook in modalità blocco; LanguageTool senza rete (le 2 prove si saltano).

## 7. Ambiente e suite

| Strumento | Uso | Installazione in un container nuovo |
|---|---|---|
| Python 3 | tutti gli script | presente |
| PyMuPDF 1.28.2, markdown | impagina, verifica | `pip install pymupdf markdown` |
| Hunspell it_IT | ortografia | `apt-get install hunspell hunspell-it` |
| Node, Playwright 1.56.1, Chromium (`/opt/pw-browsers`) | render del PDF | presenti |
| poppler (`pdfinfo`, `pdftotext`, `pdffonts`) | verifica del PDF | presenti |
| Java 21, Maven | LanguageTool | presenti |
| LanguageTool 6.8 | livello (b) dell'ortografia | jar da Maven Central fuori dal repository, `export ZB_LANGUAGETOOL=<cartella>/lib` (README, «LanguageTool») |
| EB Garamond | font di stampa | nel repository (`stampa/font/`) |

Suite: `ZB_LANGUAGETOOL=<cartella>/lib ZB_BANCA_VOCI=<banca-voci> python3 -B motore/zb prove`, dalla radice del
repository. Le prove della sezione «voce» impostano da sole la mini-banca inventata di `prove/banca-voci-prova/`.
Senza `ZB_LANGUAGETOOL`, 2 prove sono saltate con il motivo «LanguageTool assente» e le istruzioni.

## 8. Lettura da `libro.yaml`

- `titolo`, `autore`: Title e Author del PDF, riga del copyright. Le prove confrontano l'Author con
  `libro.yaml`: nessun nome è scritto nel codice.
- `formato`: trim (`pagina_pollici`), carta, `bleed`, margini in mm (`interno_scelto`, `esterno`,
  `alto`, `basso`), font e corpo, numerazione.
- `voci`: espressioni del libro con `modalita` (avviso, conta…), `ambito`, `consentito_in_capitoli`,
  `conta_per`, `escludi_pattern`. Poi `vincoli_capitolo` e `nome_vietato_prima_di`.
- `stile.eccezioni` (`unita`, `controllo`, `motivo`): un AVVISO diventa ECCEZIONE motivata; i KO restano KO.
- `stile.richiami_ammessi`: frasi ripetute di proposito, ignorate dall'anti-riciclo.
- `fatti_incompatibili` (`id`, `a`, `b`, `nota`): AVVISO con le due righe se compaiono entrambi.
- `struttura.interludi`, `gate`, `parole`, `override`, `copyright`, `ortografia`, `checklist_capitolo`.
- `voce` (facoltativo): `{slug, ambientazione}`, voce della banca-voci. Senza il blocco, nulla cambia.
- I documenti approvati si cambiano solo con `zb riapprova` (due commit).

## 9. Tolleranze e decisioni

- Niente sha256 dei PDF nelle prove: il render di Chromium cambia di qualche millesimo tra container.
  Al suo posto una prova strutturale (pagine, formato esatto, font, metadati, testo estratto).
- Margini: ±0,005″ dall'atteso (`TOLLERANZA_MARGINI`), mai sotto i minimi KDP. Non si allarga senza l'autore.
- Formato esatto delle pagine: `impagina.py` riporta ogni pagina al trim (più il bleed) senza
  scalare. Il contenuto resta fermo in alto a sinistra; con il bleed scende di 0,125″ e, sulle pagine
  pari, si sposta di 0,125″ a destra; i numeri di pagina seguono il trim.
- Solo il motore nel repository: nessun manoscritto né riferimento a libri reali. `ghimoney/` è
  archiviato nel ramo `archivio/ghimoney`.
- Storia git non riscritta, nessun push forzato.

## 10. Voci narrative (banca-voci)

La voce (come si racconta) sta in un repository separato, la banca-voci, che contiene solo schede di
voce e divieti; il contenuto del libro (cosa si racconta) lo decide l'autore nel briefing, libro per
libro. Né il motore né la banca contengono pagine di libri, manoscritti o nomi di romanzi, personaggi o
luoghi reali.

- `ZB_BANCA_VOCI`: percorso della banca, accanto a `ZB_LANGUAGETOOL` (README, «Banca-voci»); nessun
  percorso nel codice.
- Banca: `indice.yaml`, `voci/<slug>/scheda.md` (7 sezioni: nome e ruolo, principi, ritmo e sintassi,
  lessico, adattamento per genere, campione, istruzione di esecuzione con «ambientazione:»),
  `voci/<slug>/divieti.yaml`, `modelli/scheda-vuota.md`. Nessuna pagina d'esempio: l'unico testo
  d'esempio è il campione breve della sezione 6, con nomi inventati.
- `zb voce verifica`: voce nell'indice, scheda presente con 7 sezioni e «ambientazione:», `divieti.yaml`
  leggibile, stato «pronta». Errori sempre come FERMO o KO, mai traceback.
- `libro.yaml` → `voce: {slug, ambientazione}`; dal briefing con «Voce dalla banca:» e «Ambientazione:».
- `zb avvio`: «Letto» con briefing e scheda della voce; voce non verificata o banca assente = AVVISO.
- `stile.py`: i divieti della voce si sommano alle voci del libro in modalità avviso (`voce:<slug>:<id>`).
- `modelli/briefing.md`: Storia, Schede dei personaggi (vincoli «sempre» / «quasi sempre» / «mai»),
  Luoghi ed epoca, Regole del libro, Voce scelta e ambientazione; esempio inventato in un commento.
- Prove: mini-banca inventata in `prove/banca-voci-prova/` (una voce pronta, una da completare).
- Banca reale oggi (NGTAProtocol/https-github.com-banca-voci, ramo `main`, HEAD 375ee5f): 11 voci,
  11 pronte, solo scheda e divieti (da 60 a 90 divieti per voce). I nomi delle voci stanno
  nella banca, non nel motore.

## 11. Limiti noti e punti aperti (in ordine di importanza)

1. Dati KDP mai riverificati dall'autore (`ultima_verifica: null`): prima di pubblicare va fatta la
   verifica sulle pagine ufficiali e registrata con `zb verifica KDP fatta`.
2. Soglie anti-IA (campo `anti_ia` dei profili) tarate solo sui due mini-libri, uguali per ogni genere:
   da rivedere su testi veri. Sono avvisi, non blocchi.
3. Gli hook sono una protezione in più: su Bash il recinto non vede script che scrivono senza nominare il
   percorso, variabili di comandi precedenti, `$(…)`, `awk -i`, `find -delete`, `xargs`. Restano i controlli
   su git di `zb avvio` e `zb push` (cartella unica).
4. La separazione dei ruoli distingue le sessioni solo con l'hook SessionStart o `ZB_SESSIONE`; con la
   sessione «locale» dà un avviso. I log in `.zb/` sono locali al container.
5. Il consumo misura ciò che è letto attraverso gli strumenti (file, righe, parole), non i token.
   Misura di prova sul mini-libro (scrittore del capitolo 3): senza capsule 2444 parole lette in 4 file,
   con capsule 796 parole in 5 file.
6. TrimBox e BleedBox non scritti; trasparenze e immagini non controllate.
7. Ambiente non persistente: in un container nuovo vanno reinstallati i requisiti (`motore/requirements.txt`,
   Hunspell, LanguageTool con `zb ortografia installa`).
8. `dati/nomi_vietati.txt` è vuoto: `separazione.py` non trova da solo i nomi dei libri reali; la cartella
   unica controlla invece il titolo del libro attivo sul suo ramo.
9. Continuità: i tempi relativi si controllano solo se nessuna data nota coincide; le differenze
   d'età solo per i personaggi con data di nascita completa in `cronologia.yaml`.
10. Mini-libri sotto le 24 pagine: la sezione 11 della conformità KDP è KO per costruzione.
11. La storia git del ramo contiene ancora i documenti spostati sui rami d'archivio (niente riscrittura).

# Report del motore editoriale

Stato al 2026-10-21, ramo `integrazione-editoriale` (lavoro sul motore: integrazione, poi le correzioni di
`docs/PROPOSTE_MOTORE.md`). Base: ramo ccr
(`origin/ccr-d1e12273-izx78k`, d2b8814); aggiunte dal ramo `motore` (`origin/motore`, 971b6df). Scelte
dell'integrazione: `docs/DECISIONI_INTEGRAZIONE.md` (D1-D18). Esito della suite: sezione 13.
Il motore è una casa editrice generica di romanzi in italiano e in inglese: procedura, script, modelli vuoti, profili
di genere, dati KDP, il livello editoriale (`editoriale/`) e mini-libri inventati per le prove. Non contiene libri
reali.

## 1. Struttura

| Percorso | Contenuto |
|---|---|
| `CLAUDE.md` | regole di avvio delle sessioni che lavorano su un libro |
| `.gitignore` | file Python generati, ambienti virtuali |
| `motore/zb` | punto d'ingresso unico: `python3 motore/zb <comando> …` |
| `motore/script/` | 44 moduli Python: controlli, fasi e percorso editoriale, recinto e cartella unica, ruoli, agenti, capsule, consumo, anti-IA, traduzione, stampa, KDP, voci, prove |
| `motore/editoriale/` | livello editoriale: percorso, struttura (con modelli), diagnosi, 8 ruoli (con riferimenti), 12 agenti (10 in `agenti/`, traduttore e revisore di fedeltà in `lingue/agenti/`), anti-IA (catalogo, catalogo esteso, `formule.yaml`), criteri del correttore, risparmio-token, glossario; lingue it/en e traduzione; 4 comandi di Claude Code |
| `motore/requirements.txt` | dipendenze Python (PyYAML, pymupdf, Markdown) e note su quelle fuori da pip |
| `motore/stampa/` | foglio di stile, render con Chromium, font EB Garamond |
| `motore/dati/` | schemi, dati KDP, lista nera, lingue, struttura standard di un libro, hook, comandi, modelli dei ruoli, orchestrazione, output compatto, cartella unica, soglie anti-IA |
| `motore/modelli/` | modelli vuoti per un libro nuovo |
| `motore/profili/` | 7 profili di genere con i valori predefiniti (anche le soglie anti-IA) |
| `motore/prove/` | mini-libri inventati, mini-banca-voci inventata, `attesi.yaml`, esiti dei passi di sviluppo |
| `motore/README.md` | regole d'uso, comandi, ambiente |
| `motore/PROCEDURA.md` | come si lavora su un libro, passo per passo |
| `motore/proposta-motore.md` | progetto approvato del motore (riferimento delle sigle A.x, B.x, C.x) |
| `motore/report-motore.md` | questo report |
| `motore/passaggio-di-consegne.md` | riepilogo breve per ripartire in una nuova chat |
| `docs/` | documenti per l'autore, non letti nelle sessioni di lavoro (decisioni dell'integrazione, file da verificare, analisi dei repository, attribuzioni) |

## 2. Moduli e script

| Modulo | A cosa serve |
|---|---|
| `zb` | smista i comandi verso gli script; `zb aiuto` li elenca (fonte unica: `dati/comandi.yaml`) |
| `comune.py` | funzioni comuni: lettura e validazione di `libro.yaml`, percorsi dentro il libro, dati KDP, date, sessione (`ZB_SESSIONE` o hook) |
| `fase.py` | macchina a stati del libro, gate, pausa di lettura, `zb pronto/ok/avanti/correggi/riapprova/esito`; unico script che scrive `stato.yaml` |
| `percorso.py` | fasi del percorso editoriale (struttura → documenti → pagina_campione → stesura → struttura_manoscritto → line → copy → bozze → chiusura; traduzione: guida … fedeltà), rapporti con impronta, fasi dei ruoli, canone; gate «struttura» automatico |
| `struttura.py` | modelli e controlli dei nove file di `03-struttura/` (`zb struttura`), anche campi vuoti e promesse senza «Si chiude» |
| `avvio.py` | controlli d'avvio e riga «Letto: …» (`zb avvio`); un ruolo per sessione (`--ruolo`); con la voce, anche briefing e scheda della voce; senza libro, lavoro sul motore |
| `ruolo.py` | ruolo ammesso nella fase e prima riga del rapporto (`zb ruolo <libro> <ruolo> [N]`); ruoli delle sessioni e separazione tra chi scrive e chi revisiona (`zb ruolo <libro> stato`) |
| `cartella_unica.py` | niente fuori da `libri/<slug>/`: file modificati, commit misti, titolo del libro fuori dal libro (`zb cartella`; lo usano anche `avvio`, `push` e l'hook) |
| `voce.py` | voci narrative della banca-voci (`ZB_BANCA_VOCI`): `zb voce lista`, `mostra <slug> [N]`, `verifica <slug>`; divieti della voce per `stile.py` |
| `nuovo.py` | crea un libro dal briefing (`zb nuovo`); sul percorso editoriale `gate: [lettura]` e `pausa_lettura: 3`; bibbia, codex, cronologia e manuale nascono alla chiusura della struttura (`genera_documenti`) |
| `adotta.py` | bozze di `libro.yaml`, stato, cronologia e nomi per un libro già avviato (`zb adotta`) |
| `conta.py` | conteggio delle parole con il metodo unico; stampa a schermo, non scrive |
| `capitolo.py` | tutti i controlli di un capitolo in un colpo solo (`zb capitolo`, usato da `zb esito`), più le righe `anti-ia:<misura>` e l'indice Gulpease informativo |
| `stile.py` | frase media, dialogo, lista nera e voci, divieti della voce narrativa (avviso), tetti, similitudini, vincoli, eccezioni motivate |
| `riciclo.py` | anti-riciclo a 7 parole tra unità, con i richiami ammessi |
| `continuita.py` | date, età, durate, tempi relativi, cifre, nomi scritti in due modi, fatti incompatibili |
| `ortografia.py` | Hunspell (it_IT, en_US), LanguageTool se disponibile, lista di controllo dalle sezioni 1-6 dei criteri del correttore |
| `languagetool.py` | LanguageTool fuori dal repository: installazione e verifica (`zb languagetool` stato, installa, verifica) |
| `antiia.py` | audit anti-IA non distruttivo, estrazione del vocabolario, taratura (`zb antiia`); soglie da `dati/antiia.yaml`, profilo e `libro.yaml` |
| `codex.py` | schede `@char`/`@loc`, filtro per tag, personaggi morti (`zb codex`) |
| `prepara.py` | preparazione del capitolo per lo scrittore (`zb prepara`) |
| `capsula.py` | capsule di continuità e registro delle promesse (`zb capsula`); campo `capsule` di `libro.yaml` |
| `compatto.py` | stato compatto del libro (`zb compatto`) |
| `agenti.py` | installa subagenti e comandi sui rami dei libri, ne controlla il formato, dice chi chiamare ora (`zb agenti` stato, attiva, disattiva, prossimo) |
| `consumo.py` | misura per sessione (righe e parole lette, subagenti, durata) con l'hook PostToolUse; confronto con e senza capsule (`zb consumo`) |
| `traduci.py` | traduzione e controlli meccanici (`zb traduci`) |
| `revisione.py` | mostra un documento o un gate in blocchi di circa 120 righe; sola lettura |
| `compila.py` | manoscritto completo in `05-output/<titolo>-completo.md` |
| `impagina.py` | PDF di stampa: render con Chromium, sommario con le pagine reali, numeri di pagina, formato esatto, bleed, metadati |
| `verifica_pdf.py` | verifica del PDF (pagine, metadati, font, margini, sommario, parole per pagina) |
| `conformita_kdp.py` | conformità KDP in 15 sezioni, report in `06-pubblicazione/` |
| `kdp_verifica.py` | registra la verifica delle direttive KDP fatta dall'autore (`zb verifica KDP fatta`) |
| `pacchetto.py` | struttura di `06-pubblicazione/` per KDP |
| `pulizia.py` | elenca temporanei, cartelle vuote e copie; cancella solo con `--applica` |
| `push.py` | prima del push: cartella unica (libro) o impronta di una `zb prove` intera e tutta OK (motore); poi push con 4 tentativi, ramo di salvataggio, git bundle (`zb push`) |
| `precommit.py`, `salva.py` | controllo pre-commit di git sul recinto; `zb salva` (recinto, prove sul motore, commit, push) |
| `hook_sessione.py`, `hook_manoscritto.py`, `hook_recinto.py` | hook di Claude Code: SessionStart; manoscritto (modalità in `dati/hook.yaml`, oggi avviso); recinto e cartella unica anche su Bash (blocco) |
| `separazione.py` | controlla che `motore/`, `docs/` e `CLAUDE.md` non contengano libri né nomi vietati |
| `recinto.py` | controlla che i comandi scrivano solo dentro il libro indicato |
| `valida_profili.py` | valida i profili di genere contro lo schema |
| `prove.py`, `prove_editoriale.py` | suite di prove sui mini-libri inventati (`zb prove`; `--solo`, `--sezione`) |
| `stampa/modello.css` | foglio di stile parametrico: formato, margini a specchio, font, corpo |
| `stampa/print.js` | render HTML → PDF con Chromium di Playwright (Node) |
| `stampa/font/` | EB Garamond Regular, Italic, SemiBold (.ttf statici), licenza OFL, `FONTI.yaml` con gli sha256 |

## 3. Dati, modelli, profili

| File | Contenuto | Chi lo usa |
|---|---|---|
| `dati/kdp.yaml` | direttive KDP come dati (metadati, parole vietate, cartaceo, ISBN, dichiarazione AI) | `comune.py`, `verifica_pdf.py`, `conformita_kdp.py`, `impagina.py`, `pacchetto.py`, `prove.py` |
| `dati/verifiche-kdp.md` | registro delle verifiche dell'autore sulle pagine ufficiali | `kdp_verifica.py` |
| `dati/libro.schema.yaml`, `stato.schema.yaml`, `profilo.schema.yaml` | schemi di `libro.yaml`, `stato.yaml` e dei profili | `comune.py`, `valida_profili.py` |
| `dati/lingue.yaml` | lingue supportate: `it` ed `en` (Hunspell, LanguageTool, mesi, giorni, virgolette) | `comune.py`, `ortografia.py` |
| `dati/lista-nera.yaml` | espressioni da evitare (base); il libro aggiunge le sue voci | `stile.py` |
| `dati/parole-ammesse-it.txt` | forme italiane valide ignote a Hunspell; mai nomi propri | `ortografia.py` |
| `dati/nomi_vietati.txt` | nomi che non devono comparire in `motore/`; vuoto (solo commenti) | `separazione.py` |
| `dati/struttura-libro.yaml` | cartelle standard di un libro, con scopo e momento di creazione | `nuovo.py`, `comune.py` |
| `dati/hook.yaml`, `hook-settings.esempio.json` | modalità degli hook (`modalita: avviso`, `separazione_ruoli: blocco`) e impostazioni d'esempio (anche il PostToolUse del consumo) | hook, `ruolo.py`, `zb hook` |
| `dati/comandi.yaml` | comandi di `zb` con uso e gruppo | `zb aiuto` |
| `dati/modelli-ruoli.yaml` | modello per ruolo (forte, medio, leggero), `parallelo_massimo: 3` | `agenti.py` |
| `dati/orchestrazione.yaml` | regole di `zb agenti prossimo` (in sequenza, a gruppi, righe della risposta) | `agenti.py` |
| `dati/output.yaml` | output compatto di `zb` (`righe_max: 40`, comandi esenti) | `zb` |
| `dati/cartella-unica.yaml` | file ammessi fuori da `libri/<slug>/` sul ramo di un libro | `cartella_unica.py` |
| `dati/antiia.yaml` | soglie dell'audit anti-IA e vocabolario per lingua (italiano vuoto; `formule_sezione_b: false`) | `antiia.py` |
| `editoriale/anti-ia/formule.yaml` | formule del catalogo, contate come misura a sé | `antiia.py` |
| `modelli/` | `briefing.md`, `libro.yaml`, `stato.yaml`, `cronologia.yaml`, `LEGGIMI.md`, `conferme-autore.yaml` | `nuovo.py`, `adotta.py`, `conformita_kdp.py` |
| `profili/` | fantascienza, fantasy, giallo, narrativa letteraria, romance, thriller, young adult: valori predefiniti di lunghezze, stile, scene, blocco `anti_ia` | `nuovo.py`, `stile.py`, `capitolo.py`, `antiia.py` |

## 4. Vincoli KDP applicati

Fonte: `dati/kdp.yaml`, ricavato dalle direttive del repository casa-editrice (main @ becd0e2) e dal
KDP Help Center. `ultima_verifica: null`: i dati non sono ancora stati verificati dall'autore sulle pagine
ufficiali (validità prevista 30 giorni). Il motore non la scrive da solo.

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
5,5 × 8,5, 23 pagine), adozione (`mini-libro-adozione`), editoriale (`mini-libro-editoriale`, con traduzione in
inglese), più briefing e schede di pubblicazione inventati. Autori inventati («Autore di Prova», «Autrice di Prova»).

Prove per sezione nell'ultima suite intera (tabella `zb-prove-ultimo.md` nella cartella temporanea, 2026-10-21,
675 righe, 2026-10-21):

| Sezione | Prove | Sezione | Prove |
|---|---|---|---|
| passo 1 | 35 | eccezioni e richiami | 3 |
| passo 2 | 52 | voce | 30 |
| passo 3 | 45 | recinto libro | 3 |
| passo 4 | 38 | appendici | 6 |
| passo 5 | 96 | fase struttura | 18 |
| passo 5b | 18 | cartella unica | 13 |
| passo 6 | 12 | avvio motore | 4 |
| passo 7 | 11 | ruoli | 9 |
| override | 8 | agenti e capsule | 12 |
| scene | 12 | anti-IA | 9 |
| manuale | 7 | correttore | 5 |
| checklist | 3 | frasi_finali | 2 |
| continuita | 8 | frase_media_registro | 8 |
| correzioni | 20 | percorso editoriale | 73 |
| adozione | 5 | cartella unica e recinto | 13 |
| interludi e grafie | 10 | agenti e comandi | 11 |
| correggi e passo | 4 | consumo e capsule | 3 |
| unità consentite e interludi | 7 | traduzione in inglese | 17 |
| fase e rinomine | 6 | correttore e anti-IA | 10 |
| esclusioni e budget | 6 | **Totale** | **675** |
| titoli, tempi, età, push | 23 | | |

Da dove vengono (D12): ccr 560 prove (d2b8814), `motore` 520 (971b6df); le 65 prove che esistevano solo in
`motore` sono tutte presenti; in più 5 prove della pausa di lettura e 2 nate dalla divisione di prove esistenti.
Dopo il punto 9: 1 prova delle note della pausa allo scrittore (punto 8b, D16, in «percorso editoriale») e la sezione
`avvio motore` con 4 prove su `zb avvio` senza libro (punto 12, D15).

Non coperto dalle prove: libri oltre le 24 pagine, quindi le fasce interne oltre la prima;
`zb pacchetto` su un libro completo; un PDF con immagini; i formati citati diversi da 5,5 × 8,5 e A5.
Senza `ZB_LANGUAGETOOL` le prove di LanguageTool sono saltate con il motivo (4 in `prove.py`); senza Node, anche
quella dell'immagine SVG delle appendici.

## 7. Ambiente e suite

| Strumento | Uso | Installazione in un container nuovo |
|---|---|---|
| Python 3, PyYAML, PyMuPDF 1.28.2, Markdown | tutti gli script; impagina, verifica | `pip install -r motore/requirements.txt` |
| Hunspell it_IT ed en_US | ortografia | `apt-get install hunspell hunspell-it hunspell-en-us` |
| Node, Playwright 1.56.1, Chromium (`/opt/pw-browsers`) | render del PDF | presenti |
| poppler (`pdfinfo`, `pdftotext`, `pdffonts`) | verifica del PDF | presenti |
| Java 21, Maven | LanguageTool | presenti |
| LanguageTool 6.8 | livello (b) dell'ortografia | `python3 motore/zb languagetool installa [--cartella <dir>]`, fuori dal repository, poi `export ZB_LANGUAGETOOL=<cartella>/lib` (README, «LanguageTool») |
| EB Garamond | font di stampa | nel repository (`stampa/font/`) |

Suite: `ZB_LANGUAGETOOL=<cartella>/lib python3 -B motore/zb prove`, dalla radice del repository (a schermo solo le
righe non OK; tabella intera in `zb-prove-ultimo.md` nella cartella temporanea). Le prove della sezione «voce»
impostano da sole la mini-banca inventata di `prove/banca-voci-prova/`. Solo la suite intera e tutta OK scrive
l'impronta `<git-dir>/zb-prove-ok`, che `zb push` chiede sul lavoro del motore.

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
- `percorso` (`editoriale` o `breve`; senza il campo, percorso breve), `pausa_lettura` (solo 3, 4, 5),
  `capsule` (`obbligatorie` o `avviso`), `anti_ia` (soglie e `modalita: avviso|blocco`; vince sul profilo).
- `voce` (facoltativo): `{slug, ambientazione}`, voce della banca-voci. Senza il blocco, nulla cambia.
- I documenti approvati si cambiano solo con `zb riapprova` (due commit).

## 9. Tolleranze e decisioni

- Niente sha256 dei PDF nelle prove: il render di Chromium cambia di qualche millesimo tra container.
  Al suo posto una prova strutturale (pagine, formato esatto, font, metadati, testo estratto).
- Margini: ±0,005″ dall'atteso (`TOLLERANZA_MARGINI`), mai sotto i minimi KDP. Non si allarga senza l'autore.
- Formato esatto delle pagine: `impagina.py` riporta ogni pagina al trim (più il bleed) senza
  scalare. Il contenuto resta fermo in alto a sinistra; con il bleed scende di 0,125″ e, sulle pagine
  pari, si sposta di 0,125″ a destra; i numeri di pagina seguono il trim.
- Solo il motore nel repository: nessun manoscritto né riferimento a libri reali. Ciò che è stato tolto sta nei
  rami `archivio/…` su origin.
- Storia git non riscritta, nessun push forzato.
- Le scelte dell'integrazione, con il perché, sono in `docs/DECISIONI_INTEGRAZIONE.md` (D1-D18).

## 10. Voci narrative (banca-voci)

La voce (come si racconta) sta in un repository separato, la banca-voci, che contiene solo schede di
voce e divieti; il contenuto del libro (cosa si racconta) lo decide l'autore nel briefing, libro per
libro. Né il motore né la banca contengono pagine di libri, manoscritti o nomi di romanzi, personaggi o
luoghi reali.

- `ZB_BANCA_VOCI`: percorso della banca, letta in sola lettura, accanto a `ZB_LANGUAGETOOL` (README,
  «Banca-voci»); nessun percorso nel codice.
- Banca: `indice.yaml`, `voci/<slug>/scheda.md` (7 sezioni: nome e ruolo, principi, ritmo e sintassi,
  lessico, adattamento per genere, campione, istruzione di esecuzione con «ambientazione:»),
  `voci/<slug>/divieti.yaml`, `modelli/scheda-vuota.md`. Nessuna pagina d'esempio: l'unico testo
  d'esempio è il campione breve della sezione 6, con nomi inventati.
- `zb voce verifica`: voce nell'indice, scheda presente con 7 sezioni e «ambientazione:», `divieti.yaml`
  leggibile, stato «pronta». Errori sempre come FERMO o KO, mai traceback.
- `libro.yaml` → `voce: {slug, ambientazione}`; dal briefing con «Voce dalla banca:» e «Ambientazione:».
- `zb avvio`: «Letto» con briefing e scheda della voce; voce non verificata o banca assente = AVVISO.
- `stile.py`: i divieti della voce si sommano alle voci del libro in modalità avviso (`voce:<slug>:<id>`).
- `zb separazione`: con `ZB_BANCA_VOCI` controlla anche che gli slug della banca non compaiano nel motore.
- `modelli/briefing.md`: Storia, Schede dei personaggi (vincoli «sempre» / «quasi sempre» / «mai»),
  Luoghi ed epoca, Regole del libro, Voce scelta e ambientazione; esempio inventato in un commento.
- Prove: mini-banca inventata in `prove/banca-voci-prova/` (una voce pronta, una da completare).
- Banca reale al 2026-10-15 (NGTAProtocol/https-github.com-banca-voci, ramo `main`, HEAD 375ee5f): 11 voci,
  11 pronte, solo scheda e divieti. Dato del ramo ccr, non verificato nell'integrazione (la banca non è in questo
  container). I nomi delle voci stanno nella banca, non nel motore.

## 11. Limiti noti e punti aperti (in ordine di importanza)

1. Dati KDP non verificati dall'autore (`dati/kdp.yaml`, `ultima_verifica: null`): prima di pubblicare va fatta la
   verifica sulle pagine ufficiali e registrata con `zb verifica KDP fatta AAAA-MM-GG`. Il motore non la scrive.
2. Contrasto tra il pacchetto da 28 file e il modo automatico (D4): i 28 file descrivono fermate con l'«ok»
   dell'autore (`00-percorso.md`, `struttura/01-fase-struttura.md`, «solo dopo il mio ok» nei ruoli); il motore,
   per decisione dell'autore del 2026-10-20, scrive in automatico con la sola pausa di lettura. La scala di
   precedenza (`editoriale/LEGGIMI.md`) mette i ruoli sopra la procedura del motore: il contrasto è segnalato in
   `docs/DA_VERIFICARE_AUTORE.md`, non corretto nei 28 file. L'autore aggiorna il pacchetto se vuole. `CLAUDE.md`
   invece è allineato: riga di avvio con `--ruolo` e modo automatico accanto al «Metodo» (D17).
3. Soglie anti-IA (blocco `anti_ia` dei profili) uguali per ogni genere e tarate solo sui mini-libri: PROPOSTA da
   rivedere su testi veri. In modalità avviso sono segnalazioni, non blocchi. Il vocabolario italiano L1-L3 è vuoto
   finché non c'è un corpus (`zb antiia estrai`); la sezione B del catalogo non si conta
   (`formule_sezione_b: false`, decisione aperta dell'autore).
4. Gli hook sono una protezione in più: su Bash il recinto non vede script che scrivono senza nominare il percorso,
   variabili o `cd` di comandi precedenti, sostituzioni di comando, `awk -i inplace`, `ed`, `vim -c`,
   `find -delete`, `xargs rm`. Restano il controllo pre-commit e i controlli su git di `zb avvio` e `zb push`
   (cartella unica). L'hook del manoscritto è in modalità avviso (`dati/hook.yaml`).
5. La separazione dei ruoli distingue le sessioni solo con l'hook SessionStart o `ZB_SESSIONE`; con la sessione
   «locale» dà un avviso. I log in `<libro>/.zb/` sono esclusi da git (`.gitignore` del libro): restano nel
   container.
6. Il consumo misura ciò che è letto attraverso gli strumenti (file, righe, parole), non i token. Le prove
   controllano che con le capsule si leggano meno parole che senza; le cifre misurate sui mini-libri dei due rami
   (ccr: 1.127 parole con le capsule e 1.694 senza; `motore`: 796 con e 2444 senza) non sono state rifatte
   nell'integrazione.
7. TrimBox e BleedBox non scritti; trasparenze e immagini non controllate. KDP usa il MediaBox, ma
   un controllo preflight esterno potrebbe chiederli.
8. I PDF dei libri già impaginati prima del formato esatto (A5) vanno rigenerati, ma solo quando
   l'autore lo chiede.
9. Ambiente non persistente: in un container nuovo vanno reinstallati i requisiti (`motore/requirements.txt`,
   Hunspell, LanguageTool con `zb languagetool installa`).
10. `dati/nomi_vietati.txt` è vuoto: titoli, personaggi e luoghi dei libri veri li aggiunge l'autore.
    `separazione.py` ricava da solo, senza scriverli, i nomi dei rami di libro su origin e gli slug della
    banca-voci; la cartella unica controlla il titolo del libro attivo sul suo ramo.
11. Continuità: i tempi relativi si controllano solo se nessuna data nota coincide; le differenze
    d'età solo per i personaggi con data di nascita completa in `cronologia.yaml`.
12. Mini-libri sotto le 24 pagine: la sezione 11 della conformità KDP è KO per costruzione; le fasce
    del margine interno oltre la prima non sono provate.
13. La storia git contiene ancora i riferimenti tolti e i documenti spostati sui rami d'archivio (niente
    riscrittura).
14. I divieti della voce si applicano solo con `ZB_BANCA_VOCI` impostata: senza, `zb avvio` avvisa ma
    `zb stile` non li controlla.

## 12. Livello editoriale e modo automatico (integrazione del 2026-10-20)

- Percorso editoriale per i libri nuovi (`percorso: editoriale`); i libri senza il campo restano sul percorso breve.
  Nomi del pacchetto da 28 file ovunque: fase `struttura_manoscritto`, `rapporto-struttura.md` /
  `rapporto-manoscritto.md` (diagnosta), `piano-revisione-struttura.md` / `piano-revisione-manoscritto.md` (editor
  strutturale), `06-sottotrame-temi.md` (D6).
- Gate «struttura» automatico e sempre presente: se `zb pronto` trova tutto in regola registra i nove file e i
  rapporti, crea i documenti e passa a «documenti»; se no si ferma e scrive il motivo. Nessun documento prima della
  struttura (D6).
- Pausa di lettura: i libri nuovi del percorso editoriale nascono con `gate: [lettura]` e `pausa_lettura: 3`; dopo
  3 capitoli (3-5 in `libro.yaml`) e a fine stesura il motore stampa «PAUSA DI LETTURA» con i file da leggere e non
  accetta altri `zb esito`. `zb ok <libro>` registra i capitoli come letti e riparte; `zb correggi <libro> <note>`
  scrive le note in `06-diagnostica/note-lettura.md` e riparte (D11). Restano le fermate `controllo_fallito` e
  `canone`, che non sono approvazioni del lavoro.
- Ruoli: un ruolo per sessione (`zb avvio <libro> --ruolo R`, registro in `<libro>/.zb/ruoli.yaml`) e controllo per
  fase (`zb ruolo`); `separazione_ruoli: blocco` (D8).
- Cartella unica: libro attivo in `<git-dir>/zb-libro-attivo`, fuori dai file tracciati; commit misti e titolo
  fuori dal libro fermano (D7).
- Agenti: modelli da `dati/modelli-ruoli.yaml` (fonte unica), `zb agenti prossimo <libro>` con
  `dati/orchestrazione.yaml`; capsule a otto sezioni, 120-250 parole; consumo con l'hook PostToolUse; output
  compatto (D9).
- Anti-IA: misure di `antiia.py` più soglie per profilo e `libro.yaml`, `formule.yaml`, coerenza tipografica,
  ripetizioni ravvicinate, modalità `blocco` (D10). Un solo comando per LanguageTool: `zb languagetool` (D10).

## 13. Esito della suite

675 prove, 675 OK, 0 saltate (2026-10-21), con LanguageTool 6.8 da `ZB_LANGUAGETOOL`, senza
`ZB_BANCA_VOCI`. Storia: 637 al punto 12 (le 632 del punto 9, D12, più 1 di D16 e 4 della sezione `avvio motore`,
D15); 661 dopo le proposte P1-P3 e la frase media per registro (`docs/PROPOSTE_MOTORE.md`); 663 con le prove di
`aperture_battuta` (anti-IA) e `letture` (agenti) del 2026-10-21; 673 con le prove di
`aperture_senza_parole`, delle misure prima del revisore, del giro di revisione, del modello del diagnosta e delle sue
letture; 675 con il divieto della voce e gli avvisi che non fermano il diagnosta.

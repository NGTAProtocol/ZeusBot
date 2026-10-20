# Decisioni dell'integrazione (ramo `integrazione-editoriale`)

Lavoro in modo automatico (richiesta dell'autore del 2026-10-20): dove serviva una scelta l'ho presa io con le
regole del compito; qui la scelta e il perché, con il riferimento da cui viene. Partenza: `origin/ccr-d1e12273-izx78k`
(d2b8814); da `origin/motore` (971b6df) si riprende quello che manca. `motore` e `main` non si toccano.

## D1. Repository di salvataggio
- Il compito indica «NGTAProtocol/casa-editrice (conferma dal remote)». Il remote di questo checkout è
  `https://github.com/NGTAProtocol/ZeusBot` (`git remote -v`), e lì stanno i due rami di partenza.
- `NGTAProtocol/casa-editrice` esiste (privato) ma è un altro repository: 2 commit del 2026-09-26 (becd0e2 su `main`,
  275ac1e), con `libri/` nella radice, nessun commit in comune con ZeusBot (`git cat-file` dei due hash in ZeusBot:
  assenti).
- Scelta: il ramo `integrazione-editoriale` sta su `NGTAProtocol/ZeusBot`. Spingere qui una storia estranea in
  `casa-editrice` la mescolerebbe con un progetto diverso; `casa-editrice` non è stato toccato.

## D2. Ramo `main`
- In `NGTAProtocol/ZeusBot` non esiste un ramo `main` (`git ls-remote origin`: il ramo predefinito è
  `claude/claude-rc-4umw8n`). «origin/main invariato» vale quindi in senso stretto: non c'è e non è stato creato.

## D3. Punto 1: le due incoerenze del pacchetto da 28 file
- Il ramo di partenza contiene i 28 file di cc58ae6 più le integrazioni di cc12973 (unico commit successivo che li
  tocca: 24 file, +112 −20). Le tengo: il punto 7 chiede i criteri con la sezione 9, che viene da cc12973.
- (a) `editoriale/LEGGIMI.md`: a d2b8814 dice già «otto ruoli editoriali, uno per file (diagnosta compreso)» e cita
  `diagnosi/` e `agenti/` (cc12973).
- (b) `struttura/01-fase-struttura.md:30-33`: a d2b8814 dice già «Prima il diagnosta … `rapporto-struttura.md`; poi
  l'editor strutturale … scrive `06-diagnostica/piano-revisione-struttura.md`» (cc12973), coerente con `ruoli/04`.
- Nei file del motore non resta nessun «revisione-struttura», «sette ruoli» o «piano-revisione.md» (ricerca con
  grep su `motore/editoriale`, `script`, `dati`, `modelli`, `PROCEDURA.md`, `README.md`, `CLAUDE.md`).
- Scelta: nessuna modifica ai 28 file nel punto 1; questo file registra la verifica.

## D4. Contrasto tra il pacchetto e il modo automatico (segnalato, non corretto nei 28 file)
- I 28 file descrivono fermate con l'«ok» dell'autore: `00-percorso.md` (gate a ogni fase),
  `struttura/01-fase-struttura.md` («Gate `struttura`: L'autore risponde `ok`, `correggi` o `avanti`»), i ruoli
  («solo dopo il mio ok»).
- L'autore ha deciso (2026-10-20) la scrittura in automatico: nessuna approvazione intermedia, una sola pausa di
  lettura ogni 3 capitoli (3-5 in `libro.yaml`).
- La scala di precedenza (`editoriale/LEGGIMI.md`) mette «questa cartella (ruoli)» sopra la «procedura del motore»;
  la decisione dell'autore è successiva ed esplicita, e il punto 1 vieta altre modifiche ai 28 file. Il motore segue la
  decisione dell'autore; il contrasto è elencato in `docs/DA_VERIFICARE_AUTORE.md` perché l'autore aggiorni il
  pacchetto se vuole.

## D5. Punto 2: aggiunte da `motore`
- I 14 file sono copiati da 971b6df e adattati ai nomi del pacchetto (elenco e adattamenti in
  `docs/DA_VERIFICARE_AUTORE.md`). Nessuno dei 28 file è cambiato.
- Due glossari restano entrambi: `editoriale/glossario.md` (inglese → italiano, da `motore`) e
  `lingue/it/glossario-editoriale.md` (significato dei termini, da ccr); il primo rimanda al secondo.
- `lettore-cieco`: livello «medio» in `dati/modelli-ruoli.yaml`, come il valore `sonnet` che aveva in `motore`.
- `ruoli/riferimenti/critica-manoscritto.md`: nel pacchetto la diagnosi la fa il diagnosta e le proposte l'editor
  strutturale; il riferimento ora indica `rapporto-manoscritto.md` e `piano-revisione-manoscritto.md`, e la colonna
  «Proposta» del rapporto diventa «Classe di intervento» (`diagnosi/00-principi.md`: la diagnosi non scrive soluzioni).

## D6. Punto 3: macchina degli stati
- Nomi del pacchetto (ccr) ovunque: fase e gate `struttura_manoscritto`, `rapporto-struttura.md` /
  `rapporto-manoscritto.md` (diagnosta), `piano-revisione-struttura.md` / `piano-revisione-manoscritto.md` (editor
  strutturale), `06-sottotrame-temi.md`. Il nome di `motore` `revisione_manoscritto` non entra.
- Gate «struttura» automatico e sempre presente: `percorso.pronto` verifica (struttura.py più i rapporti con impronta e
  commit separato) e, se tutto regge, registra i nove file e i rapporti senza fermata e passa a «documenti»; se no si
  ferma e scrive il motivo. `fase.gate_attivi` toglie «struttura» anche se libro.yaml lo elenca (un libro di prima con
  i gate di un tempo non si ferma più lì).
- Modo automatico: i libri nuovi del percorso editoriale nascono con `gate: []` (`nuovo.GATE_EDITORIALI`). Il
  meccanismo dei gate resta per chi li chiede nel briefing («Gate: …») o nei libri già esistenti. Restano due
  fermate che non sono approvazioni del lavoro: `controllo_fallito` (stesso controllo fallito due volte: il motore
  blocca e scrive il motivo) e `canone` (cambiare i fatti bloccati è una richiesta dell'autore, non una pausa della
  scrittura).
- Percorso breve: resta solo come opzione (`Percorso: breve` nel briefing, `percorso: breve` in libro.yaml); un
  libro.yaml senza il campo `percorso` (libri nati prima) resta sul percorso breve, come in ccr, per non cambiare i
  libri già in lavorazione.
- «Nessun documento prima della struttura» (`editoriale/struttura/01-fase-struttura.md:3`): in ccr `zb nuovo` creava
  già bibbia, manuale, cronologia e codex. Ora sul percorso editoriale nascono alla chiusura della struttura
  (`nuovo.genera_documenti`, da `motore`, senza sovrascrivere nulla); scaletta e piano parole restano in
  `03-struttura/` (una sola fonte, `comune.rel_piano`).
- Modelli della struttura in italiano: vengono dai file di `editoriale/struttura/modelli/` (fonte unica, come la scheda
  di capitolo già faceva in ccr); l'inglese resta nei modelli interni di `struttura.py`.
- Controlli in più da `motore` in `struttura.verifica`: campi «- Campo:» vuoti in 01, 02, 03, 09; almeno una promessa
  o sottotrama e nessuna senza «Si chiude» in 06.
- Prove: la sezione `fase struttura` di `motore` (18 prove, giallo e romance) è portata in `prove.py` con gli attesi del
  modo automatico; il giallo, che in ccr usa il percorso breve, è portato sul percorso editoriale solo in questa prova.
  Nel percorso completo di `prove_editoriale.py` le prove dei gate (struttura, documenti, pagina campione,
  primi capitoli, revisioni) restano una per una con gli attesi senza fermata; la prova del codex alla nascita
  diventa «nessun documento prima della struttura» e il conteggio del codex si fa alla chiusura della struttura.

## D7. Punto 4: recinto, hook e cartella unica
- Base ccr (`hook_recinto.py`, `precommit.py`, `zb salva`, avviso di `zb avvio` sui file cambiati rispetto a
  `origin/motore`); da `motore` si aggiunge ciò che ccr non aveva:
  - libro attivo in `<git-dir>/zb-libro-attivo`, fuori dai file tracciati (il nome del libro non compare fuori dal
    libro); `libri/libro-attivo.md` dei rami creati prima si legge ancora;
  - `cartella_unica.py` (`zb cartella`), usato da `zb avvio`, `zb push` e dall'hook prima di `git commit` /
    `git push` da Bash: commit misti (libro e altro nello stesso commit) e titolo del libro fuori dal libro fermano;
    i merge del motore e i commit dichiarati in `dati/cartella-unica.yaml` sono ammessi;
  - `zb push` sul lavoro del motore vuole l'impronta di una `zb prove` intera e tutta OK (`<git-dir>/zb-prove-ok`,
    scritta da `prove.py`);
  - in `hook_manoscritto.py`: l'espressione di `sed -i`/`perl -i` non è un file; in modalità recinto
    `git checkout <ramo>` non è una scrittura (contano i percorsi dopo `--`). Il controllo di ccr su `python -c`
    resta.
- Adattamenti: `dati/cartella-unica.yaml` ammette fuori dal libro gli stessi file del pre-commit di ccr
  (`libri/libro-attivo.md`, `.claude/commands/` in più); il controllo del titolo non guarda le cartelle di altri libri
  (due libri sullo stesso ramo li segnala già `zb avvio` con un avviso, e le prove di ccr usano due libri con lo
  stesso briefing); per la stessa ragione un commit che tocca anche un altro libro non è «misto» (in `motore` era
  sempre un errore): contano i file fuori da `libri/`, e gli altri libri restano l'avviso di ccr in `zb avvio`.
- Il controllo del titolo guarda solo i file fuori da `libri/` diversi da `origin/motore` (scritti sul ramo del
  libro): il motore arriva da `origin/motore`, e le prove di ccr ne copiano uno intero con i mini-libri inventati.
- Prove: la sezione `cartella unica` di `motore` (13 prove) è portata in `prove.py`.

## D8. Punto 5: ruoli
- Due controlli, tutti e due tenuti:
  - per fase (ccr): `zb ruolo <libro> <ruolo> [N]` rifiuta un ruolo fuori dalla sua fase (`percorso.FASI_RUOLO`) e dà
    la prima riga del rapporto con l'impronta del testo rivisto; `zb pronto` rifiuta rapporti con un'altra impronta o
    salvati nello stesso commit del testo;
  - per sessione (`motore`): `zb avvio <libro> [--ruolo R]` registra un ruolo per sessione in `<libro>/.zb/ruoli.yaml`
    (senza `--ruolo`, quello della fase) e mette il file del ruolo nella riga «Letto»; l'hook del recinto e `zb esito`
    annotano chi scrive in `.zb/scritture.log`; al «pronto» delle fasi con rapporti e all'avvio di un ruolo di
    revisione, chi ha scritto il testo non può aver scritto la revisione. Modalità `separazione_ruoli: blocco` in
    `dati/hook.yaml` (scelta fatta in `motore`; l'autore può tornare ad `avviso`).
- Un solo nome di comando: `zb ruoli` (motore) e `zb ruolo` (ccr) hanno la stessa lunghezza (5 lettere); scelgo
  `ruolo`, che i 28 file del pacchetto già citano (`zb ruolo <libro> …` in `ruoli/04` e `diagnosi/03`). Il vecchio
  `zb ruoli <libro> stato` diventa `zb ruolo <libro> stato`; un solo modulo, `script/ruolo.py`.
- Nomi del pacchetto: il diagnosta è un ruolo di revisione (non scrive in `03-struttura/` né in `04-manoscritto/`);
  le revisioni controllate sono `rapporto-*.md` e `piano-revisione-*.md`. Ruolo della fase `struttura_manoscritto`:
  diagnosta (il primo dei due).
- `zb avvio` non controlla la fase del ruolo (come in `motore`): quel controllo resta in `zb ruolo` (come in ccr).
- I revisori non riscrivono per intero un capitolo esistente (Write rifiutato dall'hook, si corregge con Edit).
- Prove: la sezione `ruoli` di `motore` (9 prove) è portata; con il gate «struttura» automatico, dopo un «pronto»
  riuscito la fase è «documenti» (in `motore` si apriva il gate).

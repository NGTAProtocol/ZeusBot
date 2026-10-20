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

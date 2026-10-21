# Stato attuale del motore (fotografia del ramo integrato)

Data: 2026-10-20. Ramo `integrazione-editoriale` @ `951a42c` (dopo D17 e D18). Nessun libro, nessun
nome di libro o di autore reale.

La fotografia di prima (ccr, scritta prima del suo lavoro sul ramo motore @ `dce3774`) resta nella storia git:
ultimo commit che la contiene `6b59a9d` (`git show 6b59a9d:docs/STATO_ATTUALE.md`).

Come è fatta questa fotografia:
- elenco degli script: `ls motore/script/` (44 file `.py`) più `motore/zb`;
- «Cosa fa»: prima riga del docstring di ogni script;
- «Comandi zb»: campo `script` di `motore/dati/comandi.yaml` (`fase` = `fase.py`; `speciale` = gestito in `motore/zb`);
- «Importato da»: istruzioni `import` degli altri script (lettura con `ast`), senza `prove.py` e `prove_editoriale.py`;
- punti deboli: solo quelli che si leggono in `motore/report-motore.md`, `docs/DA_VERIFICARE_AUTORE.md`,
  `docs/DECISIONI_INTEGRAZIONE.md` o in un file del motore citato.

## 1. Punto d'ingresso

| File | Cosa fa | Comandi |
|---|---|---|
| `motore/zb` | comandi del motore editoriale: lancia lo script di `motore/script/` con `python3 -B`; output compatto (`dati/output.yaml`) | tutti; gestisce da sé `hook`, e smista `verifica` → `kdp_verifica.py`, `lavoro` → `hook_recinto.py`, i comandi di fase → `fase.py` |

## 2. I 44 script di `motore/script/`

| Script | Cosa fa (prima riga del docstring) | Comandi zb | Importato da |
|---|---|---|---|
| adotta.py | Adotta nel motore un libro già avviato (passo 5b). | `adotta` | — |
| agenti.py | Subagenti e comandi di Claude Code per i rami dei libri. | `agenti` | — |
| antiia.py | Audit anti-IA non distruttivo e vocabolario dai dati. | `antiia` | capitolo, fase, traduci |
| avvio.py | Avvio obbligatorio prima di lavorare su un libro. | `avvio` | — |
| capitolo.py | Controlli di un capitolo in un colpo solo. | `capitolo` (e `esito`, lanciato da fase.py) | — |
| capsula.py | Capsule di continuità: 07-capsule/NN.md dopo ogni capitolo accettato, e il registro delle promesse. | `capsula` | agenti, avvio, compatto, prepara |
| cartella_unica.py | Cartella unica: tutto ciò che riguarda un libro vive solo in libri/<slug>/ (ramo del libro). | `cartella` | avvio, hook_recinto, push |
| codex.py | Codex del libro: schede dei personaggi e dei luoghi in <libro>/02-bibbia/codex/, una per file. | `codex` | capsula, consumo, nuovo, percorso, prepara, traduci |
| compatto.py | Stato compatto del libro: <libro>/stato-compatto.md, 15-20 righe. | `compatto` | salva |
| compila.py | Compone il manoscritto completo di un libro. | `compila` | — |
| comune.py | Funzioni comuni del motore. | — (libreria) | tutti gli altri script tranne hook_manoscritto e precommit |
| conformita_kdp.py | Controllo di conformità KDP, sezioni 1-15. | `kdp` | — |
| consumo.py | Misura del consumo per sessione. Misura, non stima: righe e parole lette dai file. | `consumo`; hook PostToolUse (`Read\|Agent\|Task`) | — |
| conta.py | Conteggio delle parole con il metodo unico. | `conta` | capitolo, capsula, consumo, fase, traduci, verifica_pdf |
| continuita.py | Controlli di continuità. | `continuita` | capitolo |
| fase.py | Macchina a stati del libro. Unico script che scrive stato.yaml. | `stato pronto avanti ok correggi esito riapprova fase canone` | agenti, avvio, compatto, nuovo, percorso, struttura |
| hook_manoscritto.py | Hook PreToolUse di Claude Code sul manoscritto. | hook PreToolUse (`Write\|Edit\|MultiEdit\|NotebookEdit\|Bash`) | hook_recinto |
| hook_recinto.py | Hook PreToolUse di Claude Code: recinto sul libro attivo, in modalità BLOCCO. | `lavoro`; hook PreToolUse (stesso matcher) | agenti, avvio, consumo, nuovo, precommit, push, salva |
| hook_sessione.py | Hook SessionStart di Claude Code. Non blocca mai: esce sempre con 0. | hook SessionStart | — |
| impagina.py | Impaginazione del PDF di stampa. | `impagina` | compila |
| kdp_verifica.py | Verifica delle direttive KDP da parte dell'autore. | `verifica KDP …` | conformita_kdp |
| languagetool.py | LanguageTool per il livello (b) di «zb ortografia». | `languagetool` | — |
| nuovo.py | Crea un libro dal briefing. | `nuovo` | adotta, avvio, percorso |
| ortografia.py | Controllo ortografico del manoscritto (passo 7). Tre livelli. | `ortografia` | — |
| pacchetto.py | Pacchetto di pubblicazione: struttura di <libro>/06-pubblicazione/. | `pacchetto` | — |
| percorso.py | Percorso da casa editrice (libri con «percorso: editoriale» in libro.yaml). Lo usa fase.py. | — (via fase.py) | agenti, avvio, fase, revisione, ruolo |
| precommit.py | Controllo pre-commit di git: il recinto vale anche per ciò che il recinto degli hook non vede (Bash, script). | — (installato da `zb lavoro`) | avvio, hook_recinto, salva |
| prepara.py | Preparazione di un capitolo per lo scrittore. | `prepara` | consumo |
| prove.py | Prove ripetibili del motore. | `prove` | — |
| prove_editoriale.py | Prove del percorso da casa editrice (le lancia prove.py). | — (via `prove`) | prove |
| pulizia.py | Pulizia di un libro (passo 6). Di default solo ELENCO: non cancella nulla. | `pulizia` | — |
| push.py | Push del ramo corrente con ripiego. | `push` (e lanciato da salva.py) | — |
| recinto.py | Controlla che i comandi del motore scrivano solo dentro il libro indicato. | `recinto` | — |
| revisione.py | Mostra un documento o i documenti di un gate in blocchi. Sola lettura. | `revisione` | adotta, fase, percorso, voce |
| riciclo.py | Anti-riciclo a 7 parole. | `riciclo` | capitolo |
| ruolo.py | Ruoli del percorso editoriale: chi può lavorare in quale fase, la prima riga del suo rapporto, e la separazione … | `ruolo` | avvio, consumo, fase, hook_recinto, percorso |
| salva.py | Salvataggio con il recinto: controllo, commit, push. | `salva` | — |
| separazione.py | Controlla che il motore non contenga libri. | `separazione` | — |
| stile.py | Controlli di stile. | `stile` | capitolo, continuita, riciclo, verifica_pdf |
| struttura.py | Fase struttura del percorso editoriale: modelli dei nove file di 03-struttura/ e controlli meccanici. | `struttura` | codex, compatto, nuovo, percorso, prepara |
| traduci.py | Traduzione di un libro. Tutto in <libro>/08-traduzione-<lingua>/. | `traduci` (e lanciato da fase.py) | percorso |
| valida_profili.py | Valida i profili di genere di motore/profili/. | `profili` | — |
| verifica_pdf.py | Verifica del PDF di stampa. | `pdf` | conformita_kdp |
| voce.py | Voci narrative della banca-voci. Sola lettura. | `voce` | avvio, stile |

Note:
- I riferimenti «proposta …» dei docstring sono tolti dalla colonna; restano nei file.
- Gli hook li aggancia `motore/dati/hook-settings.esempio.json` (copiato in `.claude/settings.json` da `zb hook attiva`).
- `prove.py`, `prove_editoriale.py` e `recinto.py` lanciano o importano quasi tutti gli script: non sono nella colonna.
- Rispetto alla fotografia di prima (28 script a `dce3774`): 16 script in più (agenti, antiia, capsula, cartella_unica,
  codex, compatto, consumo, languagetool, percorso, precommit, prepara, prove_editoriale, ruolo, salva, struttura,
  traduci); nessuno tolto.
  `motore/report-motore.md` §1 dice «43 moduli Python»: oggi i file `.py` sono 44.

## 3. Punti deboli di prima: cosa si vede oggi nei file

| Punto debole di prima | Oggi |
|---|---|
| Il recinto non vede Bash | il matcher PreToolUse di `dati/hook-settings.esempio.json` comprende `Bash`; in più `precommit.py` |
| Hook spenti sul ramo motore | nel repository non c'è `.claude/`; `avvio_motore()` ferma se ci sono `.claude/agents`, `.claude/commands` o `.claude/settings.json` |
| «Lavoro sul motore» non verificabile | in `avvio.py` c'è `avvio_motore()` («zb avvio» senza libro: controlli e riga «Letto»); punto 12 dell'integrazione: funzione di ccr tenuta identica e coperta da 4 prove (sezione `avvio motore`, D15) |
| requirements mancante | c'è `motore/requirements.txt` (PyYAML, pymupdf, Markdown) |
| Prove non automatiche | `zb push` sul lavoro del motore vuole l'impronta di una `zb prove` intera e tutta OK (D7) |
| Modello libro.yaml senza appendici | `motore/modelli/libro.yaml` riga 41: `appendici: []` |
| Dati KDP con `ultima_verifica: null` | ancora così: `motore/dati/kdp.yaml` riga 5 |

## 4. Punti deboli noti oggi (con la prova)

| # | Punto debole | Dove si vede |
|---|---|---|
| 1 | Dati KDP mai riverificati dall'autore | `motore/dati/kdp.yaml` riga 5: `ultima_verifica: null`; `report-motore.md` §11.1 |
| 2 | Contrasto tra il pacchetto da 28 file (fermate con l'«ok» dell'autore) e il modo automatico | D4; `docs/DA_VERIFICARE_AUTORE.md`; i 28 file non sono stati corretti su questo punto (`CLAUDE.md` allineato, D17; subagenti e capsula corretti, D18) |
| 3 | Decisioni dell'autore ancora aperte | «avvenire/avvenire» (`correttore/criteri-correttore.md` §5); sezione B del catalogo anti-IA (`formule_sezione_b: false`, D10); licenza di APODICTIC (CC BY-NC-SA 4.0) |
| 4 | I ruoli del pacchetto non rimandano ai tre file di `ruoli/riferimenti/` | `docs/DA_VERIFICARE_AUTORE.md` |
| 5 | `separazione.py` non trova da solo i nomi dei libri reali | `motore/dati/nomi_vietati.txt` senza righe di nomi; `report-motore.md` §11.5 |
| 6 | `hook_manoscritto.py` in modalità avviso | `motore/dati/hook.yaml` riga 4: `modalita: avviso` (il recinto di `hook_recinto.py` è in blocco) |
| 7 | TrimBox e BleedBox non scritti; trasparenze e immagini non controllate | `report-motore.md` §5 e §11.2 |
| 8 | Ambiente non persistente: PyMuPDF, markdown, Hunspell, LanguageTool da reinstallare in un container nuovo | `report-motore.md` §11.4 |
| 9 | Continuità: tempi relativi solo se nessuna data nota coincide; differenze d'età solo con la data di nascita completa | `report-motore.md` §11.6 |
| 10 | Mini-libri sotto le 24 pagine: sezione 11 della conformità KDP KO per costruzione; fasce del margine interno oltre la prima non provate | `report-motore.md` §6 e §11.8 |
| 11 | I divieti della voce valgono solo con `ZB_BANCA_VOCI` impostata | `report-motore.md` §11.11 |
| 12 | Misura con e senza capsule fatta solo sul mini-libro editoriale (1.127 contro 1.694 parole lette) | `report-motore.md` §12 |
| 13 | Prova dell'output compatto solo con soglia 10: nessun comando supera oggi 40 righe in modo stabile | D9 |
| 14 | Divergenza lasciata visibile su kindle-book-agency (ccr: non trovato; motore: trovato a c1d75dc) | D13 |

## 5. Prove

Totale alla data di questa fotografia: 637 prove, 637 OK, 0 saltate (punto 12: 632 del punto 9, D12, più 1 di D16 e 4
di D15). Dopo: 661 (e264a01) e 663 (2026-10-21, d73e926), tutte OK, 0 saltate (`motore/report-motore.md` §13).
Questa fotografia non ha lanciato `zb prove`.

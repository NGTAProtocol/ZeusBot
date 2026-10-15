# Esportazione completa del progetto — parte 6 di 6

Testo integrale, parola per parola. Nessun riassunto, nessuna correzione. Esclusi `libri/` e i manoscritti.


---

## 7. Programmi, stampa e prove

### `motore/prove/esiti/passo-5.md`

```markdown
# Passo 5 — Conduzione: resoconto

Prove: `python3 motore/zb prove`, **259/259 OK**: 163 prove dei passi 1-4 e 96 nuove.
Tutto gira su copie temporanee, cioè repository git con un remoto locale. Il repository vero non viene toccato.

## a) File

| File | Righe |
|---|---|
| `script/nuovo.py` | 311 |
| `script/avvio.py` | 175 |
| `script/fase.py` | 377 |
| `script/revisione.py` | 128 |
| `script/hook_sessione.py` | 38 |
| `script/hook_manoscritto.py` | 182 |
| `dati/hook.yaml` (modalità avviso) | 4 |
| `dati/hook-settings.esempio.json` (non attivo) | 13 |
| `modelli/briefing.md` | 48 |
| `modelli/libro.yaml` | 35 |
| `modelli/LEGGIMI.md` | 19 |
| `modelli/stato.yaml` | 18 |
| `modelli/cronologia.yaml` | 6 |
| `PROCEDURA.md` | 185 |
| `README.md` (aggiornato) | 69 |
| `zb` | 131 |
| `CLAUDE.md` (radice del repository) | 27 |
| `prove/briefing/briefing-giallo.md` (inventato) | 48 |

File modificati:
- `script/comune.py` (+54): git, sha256, sessione, `.zb/`;
- `script/prove.py` (+426): sezione passo_5;
- `prove/attesi.yaml` (+107);
- `script/recinto.py` (+3): avvio, fase stato, revisione;
- `script/separazione.py`: ammesso il modello vuoto `modelli/libro.yaml`;
- `dati/libro.schema.yaml`: campo `gate`;
- `dati/stato.schema.yaml`: `ultimo_capitolo_scritto`, `tentativi`, `correzioni_aperte`.

## b) Prove del passo 5 (tutte OK)

| Script | Controllo | Atteso | Ottenuto | Esito |
|---|---|---|---|---|
| nuovo.py | briefing inventato: struttura creata (18 file) | elenco fisso | uguale | OK |
| nuovo.py | scritture fuori dalla cartella del libro (repository e motore) | nessuna | nessuna | OK |
| nuovo.py | libro.yaml valido; 30 capitoli; tetti, vietati, vincoli e gate dalle Direttive | come attesi | uguale | OK |
| nuovo.py | libro già esistente | rifiutato, intatto | rifiutato, intatto | OK |
| nuovo.py / avvio.py | briefing incompleto | codice 2, elenca Autore, Lunghezza, Idea, niente creato | uguale | OK |
| avvio.py | briefing svuotato dopo la creazione (fase documenti) | fermo, elenca Autore | uguale | OK |
| avvio.py | libro pulito: riga «Letto» | 10 file con righe, sha256 e commit; libro @ e motore @ | uguale | OK |
| avvio.py | marker di sessione (locale e da hook SessionStart); git status pulito | sì | sì | OK |
| avvio.py | sessione che non può pushare | fermo, niente scritto | fermo, niente scritto | OK |
| avvio.py | fuori da git; modifiche non salvate; ramo diverso; documento approvato cambiato | fermo | fermo | OK |
| fase.py | ok senza gate; ok prima di tutti i blocchi; ok con correzione non applicata; ok su documenti cambiati o non salvati | rifiutato | rifiutato | OK |
| fase.py | pronto → avanti × 6 → correggi → avanti riparte dal blocco 1 → ok | gate, blocchi, approvazione | uguale | OK |
| fase.py | stato | non scrive | non scrive | OK |
| fase.py | gate pagina_campione → fase stesura; LEGGIMI aggiornato | sì | sì | OK |
| fase.py | gate configurabili: senza «documenti», con «lotto», senza gate | come attesi | uguale | OK |
| fase.py | stesura mini-libro giallo: KO poi secondo KO → fermata; ok; dopo il cap. 3 gate primi_capitoli; «ok, lotti da 5»; chiusura | come attesi | uguale | OK |
| nuovo/avvio | nuovo e riscrittura: senza testo precedente rifiutato; libro.yaml, LEGGIMI e «Letto» diversi | come attesi | uguale | OK |
| CLAUDE.md | ≤30 righe; nessun nome di libro; 12 frasi obbligatorie | sì, nessuno, tutte | 27 righe, nessuno, tutte | OK |
| hook_manoscritto.py | avviso: Write, Edit e 14 scenari Bash | avvisa o passa, sempre codice 0 | uguale | OK |
| hook_manoscritto.py | con marker; dopo compattazione; log; modalità blocco su una copia del motore | come attesi | uguale | OK |
| zb | hook attiva (senza e con --ok), disattiva, rifiuto su file altrui; nessun settings.json nel repository | come attesi | uguale | OK |
| revisione.py / zb | blocchi tagliati a fine paragrafo, sola lettura; ortografia non ancora costruita | come attesi | uguale | OK |

Tabella completa, riga per riga: `python3 motore/zb prove`.

## c) Separazione e recinto

- `separazione.py`: OK, nessun libro dentro `motore/`.
- `recinto.py`: OK, 40 esecuzioni, nessuna scrittura fuori dal libro. Erano 34; ora include avvio, fase stato e revisione.
- `CLAUDE.md` controllato anche a mano contro i nomi delle cartelle in `libri/` (sola lettura): nessuno compare.

## d) Scelte non scritte nella proposta

1. **Fasi semplificate** secondo il processo del passo 5: documenti → pagina_campione → stesura → chiusura → chiuso. Sostituiscono le fasi 0-8 di C.1.
2. **Comandi interni** di Claude Code oltre alle risposte dell'autore:
   - `zb pronto` apre il gate, oppure passa oltre se il gate è disattivato;
   - `zb esito N` esegue capitolo.py e registra l'esito.
   `zb nuovo` non apre subito il gate «documenti»: lo apre `pronto`, a documenti completati.
3. **Gate `controllo_fallito`** sempre attivo, al secondo KO di fila sullo stesso capitolo. `ok` accetta il capitolo così com'è.
4. **«ok» rifiutato** se i documenti hanno modifiche non salvate in git. Il commit registrato è così sempre reale.
5. **Lotti senza gate «lotto»**: il lotto si chiude senza fermata e lo segnala a schermo.
6. **`.zb/` contiene un `.gitignore` con `*`**, sia nel libro sia alla radice della sessione. Così i marker non finiscono mai nei commit senza toccare il `.gitignore` del repository.
7. **Hook dopo una compattazione**: il marker non viene cancellato. L'hook registra l'ora in `.zb/compattato-<sessione>` e il marker più vecchio non vale più.
8. **Hook in avviso**: stampa `{"systemMessage": …}`.
9. **`zb hook attiva`** senza `--ok` mostra soltanto cosa scriverebbe; con `--ok` scrive. **`disattiva`** toglie solo un file identico al modello.
10. **Rilevamento Bash**: in PROCEDURA.md la tabella ha 18 scenari. Ai 14 della proposta ho aggiunto 5b, 15, 16 e 17 (falsi permessi e falsi avvisi) e 18.
11. Il vincolo «vietato prima del 2» ora dà `['1']` invece di `['1-1']`.
12. In `prove.py`, la nuova prova CLAUDE.md cerca i nomi dei mini-libri e del briefing inventato. Il controllo contro i libri veri l'ho fatto a mano, perché il motore non legge `libri/`.

## e) Prossimo passo

- **Manca `ortografia.py`** (Hunspell it_IT): non è in nessun passo di B.7, ma serve alla chiusura. `zb ortografia` oggi risponde «non esiste ancora», e `zb pronto` in chiusura lo richiede.
- **Dall'autore servono:**
  - l'«ok» al passo 5;
  - la decisione su `ortografia.py` (passo 6?);
  - quando vuole, `zb hook attiva --ok` (commit a parte), e più avanti il passaggio a `modalita: blocco`;
  - la scelta su come portare il motore ai rami dei libri (C.7).
```

### `motore/prove/esiti/passo-5b.md`

```markdown
# Passo 5b — zb adotta: resoconto

Prove: `zb prove` **277/277 OK** (18 nuove); separazione OK; recinto OK (42 esecuzioni).

## File
- `script/adotta.py` (nuovo): bozze di libro.yaml, stato.yaml, cronologia.yaml, nomi_propri.txt e
  06-diagnostica/adozione.md da documenti esistenti, con fonte file:riga e override con motivo.
- `prove/mini-libro-adozione/` (nuovo, inventato): bibbia, manuale, scaletta, un capitolo; nessun libro.yaml.
- Modificati: `zb` (comando adotta), `PROCEDURA.md` (sezione 3b con esempio neutro),
  `script/prove.py` e `prove/attesi.yaml` (sezione passo_5b), `script/recinto.py` (adotta).

## Prove (tutte OK)
Documenti parziali: 5 file scritti, nessuna scrittura fuori; 19 valori tutti con fonte;
non ricavati elencati (autore, formato, copyright, piano parole); override frase_media con la
riga del manuale; libro.yaml senza autore segnalato non valido; cronologia 2 nascite e 3 date;
fase documenti senza gate. Seconda esecuzione: nulla sovrascritto. Documenti completi: valido e
gate «documenti» aperto. 01-originale presente: riscrittura. Cartella vuota: fermo.

## Scelte
- Valori senza fonte possibile (formato, testo di fantasia del copyright) entrano col valore
  standard del motore e sono elencati come «da confermare».
- Se mancano documenti il gate non si apre; con tutti i documenti adotta apre direttamente il
  gate «documenti» (niente approvato: si approva con avanti/ok).
```

### `motore/prove/esiti/passo-6.md`

```markdown
# Passo 6 — struttura e pulizia: resoconto

Prove: `zb prove` **289/289 OK** (12 nuove); separazione OK; recinto OK (44 esecuzioni con `pulizia.py`).

## File
- Nuovi: `dati/struttura-libro.yaml` (cartelle con scopo, modalità, momento di creazione),
  `script/pulizia.py` (`zb pulizia <libro> [--applica]`).
- Modificati: `script/nuovo.py` (nessuna cartella vuota, nessun `.gitkeep`; `01-originale` solo in
  riscrittura e il testo precedente deve stare lì), `script/comune.py` (`controlla_struttura`),
  `modelli/briefing.md`, `PROCEDURA.md`, `zb`, `script/recinto.py`, `script/prove.py`, `prove/attesi.yaml`.
- Correzione approvata: `pulizia.py` costruisce il percorso da cancellare con `comune.dentro`, senza
  ricreare cartelle (prima la riga 131 ricreava la cartella appena tolta).

## Audit del repository (solo elenco, nulla cancellato)

### Radice del ramo di lavoro del motore

| Voce | Scopo | Ultimo commit | Dimensione | Candidato alla rimozione |
|---|---|---|---|---|
| `.gitignore` | regole git del repository | dd5dc60 2026-09-23 | 4 KB | no |
| `CLAUDE.md` | regole di avvio delle sessioni | 71fbc62 2026-10-06 | 4 KB | no |
| `ghimoney/` | progetto separato (analisi repository GitHub) | 28560a6 2026-09-24 | 756 KB | no dal motore: è di un altro progetto; da decidere se tenerlo nei rami dei libri |
| `libri/` | cartelle dei libri, fuori dal motore | 7692265 2026-10-01 | 7,1 MB | no (non si tocca) |
| `motore/` | motore editoriale | c3e3964 2026-10-06 | 2,3 MB (font compresi) | no |

### Rami remoti

| Ramo | Scopo | Ultimo commit | Contenuto | Candidato alla rimozione |
|---|---|---|---|---|
| `claude/claude-rc-4umw8n` | ramo principale (HEAD di GitHub) | 28560a6 2026-09-24 | `.gitignore`, `ghimoney/` | no: è il ramo principale |
| `claude/roadmemo-context-review-c9rf26` | sessione chiusa senza modifiche | 28560a6 2026-09-24 | identico al principale | sì: nessun commit proprio (decide l'autore) |
| `claude/ai-toolkit-reference-setup-b3kel4` | regola .gitignore per un riferimento locale | c047398 2026-09-29 | principale + 1 commit | possibile: un solo commit su .gitignore, da unire o scartare |
| `claude/manuscript-reader-voice-notes-s0vnee` | app lettore del manoscritto (Android) | 42fa935 2026-09-25 | storia diversa (nato da e7a94cb, prima del principale) | no: progetto a sé |
| ramo di un libro | libro | d31e84c 2026-10-01 | principale + `libri/` | no |
| ramo di lavoro del motore (questo ramo) | motore, insieme a un libro | c3e3964 2026-10-06 | principale + `libri/` + `motore/` + `CLAUDE.md` | no |

### Cartelle di lavoro nel container (fuori dal repository o non tracciate)

| Cartella | Scopo | Dimensione | Candidato alla rimozione |
|---|---|---|---|
| checkout principale | checkout del repository, ramo di un libro | 54 MB | no (cartella di sessione) |
| worktree del motore | worktree del ramo del motore | 11 MB | no finché si lavora al motore; poi sì (`git worktree remove`) |
| copia di `casa-editrice` | copia in sola lettura di un altro repository | 332 KB | sì a fine lavori |
| scratchpad della sessione | file temporanei, LanguageTool (240 MB) | 260 MB | sì a fine sessione |
| `/tmp/zb-prove-*` (4 cartelle) | resti di prove interrotte | 984 KB | sì |

Il container è temporaneo: tutte queste cartelle spariscono quando la sessione si chiude.

## Ramo di origine (`origin/claude/claude-rc-4umw8n`)
- Ultimo commit 28560a6 (2026-09-24), 15 commit, 81 file.
- Contiene solo `.gitignore` e `ghimoney/`: nessun libro, nessun motore.
- Tutti i rami dei libri e del motore partono da 28560a6. Fa eccezione il lettore del manoscritto,
  che ha una storia più vecchia (base comune e7a94cb).
```

### `motore/prove/esiti/passo-7.md`

```markdown
# Passo 7 — ortografia: resoconto

Prove: `zb prove` **298/298 OK, 2 saltate** (le due di LanguageTool, senza `ZB_LANGUAGETOOL`;
non contate nel totale). Con `ZB_LANGUAGETOOL` impostata su una copia temporanea di LanguageTool
le 11 prove del passo 7 danno 11/11 OK. Separazione OK; recinto OK (46 esecuzioni).
Nomi dei libri reali in `motore/`: 0.

## File
- Nuovi: `script/ortografia.py`, `dati/parole-ammesse-it.txt` (80 forme dei verbi sedere,
  possedere, soprassedere che il dizionario it_IT non conosce; nessun nome).
- Modificati: `README.md` (percorso in 8 righe, un comando per riga), `PROCEDURA.md` (ortografia e
  LanguageTool da Maven Central), `script/prove.py` (passo_7 e prove «saltate»), `prove/attesi.yaml`,
  `script/recinto.py`, `prove/esiti/passo-6.md` (nomi dei rami resi neutri).

## Livelli
- (a) Hunspell it_IT: sempre. Sul mini-libro giallo segnala solo «Brena», la seconda grafia messa
  apposta al passo 2; sul romance nulla; sui refusi inventati «errrore» e «registo», non «sedette»
  né le elisioni.
- (b) LanguageTool 6.8: solo con `ZB_LANGUAGETOOL`. Scaricato da Maven Central (Java 21 e Maven già
  presenti) in una cartella temporanea fuori dal repository, 240 MB; languagetool.org mai usato.
  Trova gli stessi refusi; non segnala «e» per «è» né «Lui sono andato».
- (c) Checklist manuale in fondo al report, con la nota sui limiti dei correttori automatici.
```

### `motore/prove/esiti/pdf-indipendente-dal-container.md`

```markdown
# Prove del PDF indipendenti dal container: esito

Data: 2026-10-13. Ramo motore, partendo da 3a01e42.

## Problema

Nel passo 3, 4 prove dipendevano dal container in cui era stato fatto il render con Chromium:
- gli sha256 dei due PDF di prova;
- i margini interno ed esterno del romance (0,665/0,667 e 0,624/0,625).

## Modifiche (`script/prove.py`, `prove/attesi.yaml`)

- **Sha256 del PDF → struttura del PDF** (`struttura_pdf`). Per ciascun mini-libro una prova controlla:
  - le pagine;
  - il formato di ogni pagina, uguale al trim di `libro.yaml` più il bleed se previsto (bleed: `dati/kdp.yaml`);
  - i font: tutti incorporati, nessun Type3;
  - Title e Author uguali a `libro.yaml`;
  - il testo estratto con PyMuPDF, con gli spazi normalizzati: numero di parole e sha256.
- **Margini → tolleranza più minimo KDP** (`controllo_margine`). Ogni margine deve stare entro ±0,005″
  dall'atteso (`TOLLERANZA_MARGINI`, con commento) e non sotto il minimo KDP (`minimi_kdp`).
  - I minimi si leggono da `dati/kdp.yaml` con `comune.kdp_margini` e `comune.kdp_interno_pollici`:
    interno secondo il numero di pagine; esterno, alto e basso secondo il bleed. La fonte (KDP Help
    Center) è indicata nell'intestazione di `dati/kdp.yaml`.
  - Il minimo KDP vale anche dentro la tolleranza.
- Il numero di prove resta 424. Le altre prove non sono state toccate.
- Trasparenze: il motore non le gestisce, quindi non sono state aggiunte prove.
- Autore nei metadati: si confronta con l'autore di libro.yaml; i mini-libri hanno autori inventati,
  perché il motore non contiene libri reali.

## Prove di regressione

Ogni alterazione è stata temporanea e poi ripristinata con `git checkout`.

| Alterazione | Esito |
|---|---|
| (a) romance, margine esterno 16 → 16,508 mm (+0,02″) | KO: «0.646: fuori tolleranza» |
| (b) romance, margine esterno 5 mm, atteso portato a 0,198 | KO: «0.198: sotto il minimo KDP 0.25» |
| (c1) romance, una parola aggiunta al capitolo 1 | KO della struttura: 4556 parole, sha256 del testo diverso |
| (c2) PDF del romance con un font Helvetica non incorporato | font_non_incorporati: 1, quindi KO della struttura |

## Difetto trovato: formato A5 non esatto

Il mini-libro dichiara 5,83 × 8,27″ (A5), ma il PDF misura 420 × 594,96 pt, cioè 5,833 × 8,263″.

- Chromium arrotonda il formato della pagina, anche se lo riceve da `page.pdf` invece che dal CSS
  (provato: 420 × 595,92 pt).
- I formati multipli di 1/96″ (5,5 × 8,5″, 6 × 9″) escono esatti: il romance passa.
- Qualunque libro in A5, compreso un libro di prova, avrebbe lo stesso scarto.
- La prova «mini-libro: struttura del PDF» resta KO. La correzione, cioè riportare le pagine al trim
  esatto con PyMuPDF in `impagina.py`, cambia il PDF dei libri e sposta i margini di qualche millesimo:
  la decide l'autore.

## Esito della suite

Con LanguageTool: vedi il resoconto del commit (423/424 OK, 0 saltate, 1 KO: il formato A5 del mini-libro).
```

### `motore/prove/esiti/recinto-libro.md`

```markdown
# Recinto sul libro: zb nuovo, hook di blocco, regola di avvio: esito

Data: 2026-10-13. Ramo motore, partendo da fd61225.

## Decisioni dell'autore

- Strada «c»: i libri restano nel repository, in `libri/<slug>/`, solo sui rami di libro; il ramo
  `motore` non contiene mai un libro.
- Hook di Claude Code in modalità blocco sulle scritture fuori dal libro attivo.

## Cosa cambia

- `nuovo.py`: `controlla_posizione` prima di creare qualsiasi cosa. Rifiutato (codice 2, messaggio con la
  regola) se la cartella è dentro `motore/`, è la radice del repository, il ramo è `motore`, oppure non è
  `libri/<slug>/`. Le prove della suite (`ZB_PROVE=1`, impostata da `prove.py`) sono esenti solo
  dall'ultimo controllo, perché usano cartelle temporanee. Dopo la nascita in `libri/<slug>/` imposta
  il libro attivo.
- `hook_recinto.py` (nuovo), aggiunto al modello `dati/hook-settings.esempio.json` (PreToolUse su Write,
  Edit, MultiEdit, NotebookEdit). Sul ramo `motore` nessun `.claude/settings.json`: sui rami di libro
  si attiva con `zb hook attiva --ok`, insieme all'hook del manoscritto (avviso). Libro attivo da `libri/libro-attivo.md`; consentito solo `libri/<slug>/`, tutto il resto
  bloccato (codice 2). Eccezioni: il briefing di un libro che non ha ancora `libro.yaml`; «lavoro sul
  motore» (`zb lavoro motore`: consentito il repository tranne `libri/`). `libro-attivo.md` assente o
  vuoto: avviso, non blocco.
- `zb lavoro stato | motore | libro <slug>` (in `zb`, che lancia `hook_recinto.py lavoro …`); stato in
  `<git-dir>/zb-lavoro`, non tracciato. `zb lavoro libro` si rifiuta sul ramo `motore`.
- `CLAUDE.md` (29 righe, nessun percorso di libro): regola madre, regola di avvio per ogni briefing
  nuovo («nella cartella del libro»), recinto, report di sessione (ogni 5 scambi o a «passaggio»; sezioni fisse).
- `passaggio-di-consegne.md` del motore riordinato nelle sezioni fisse.

## Conflitti con prove già verdi (prima esecuzione: 454/457)

La prima versione metteva `.claude/settings.json` nel motore e allungava CLAUDE.md con «libri/<slug>/»:
tre prove già verdi di «passo 5» fallivano (righe di CLAUDE.md ≤ 30, nessun `libri/` in CLAUDE.md,
`.claude/settings.json` assente dal repository del motore). Decisione dell'autore: nessuna prova
cambiata. Correzioni: settings.json tolto, hook nel modello, CLAUDE.md accorciato e senza `libri/`.
La prova dell'hook chiama `hook_recinto.py` direttamente e non leggeva `settings.json`: invariata.

## Prove (+3, sezione «recinto libro», libro inventato dal briefing di prova)

| Prova | Atteso |
|---|---|
| `zb nuovo` con la cartella in `motore/giallo` di un repository temporaneo | codice 2, messaggio «è dentro motore/», nella cartella resta solo il briefing |
| `zb nuovo` in `libri/giallo` di un repository temporaneo sul ramo `motore` | codice 2, messaggio sul ramo «motore», nella cartella resta solo il briefing |
| hook con libro attivo `giallo`: Write su `motore/nota.md` / su `libri/giallo/02-bibbia/nota.md` | `2` con «RECINTO» / `0` senza messaggio |

Nessuna prova esistente modificata: con `ZB_PROVE=1` le prove di `zb nuovo` già presenti (libri in
cartelle temporanee, ramo «prova») danno gli stessi esiti.

Verifica a mano, fuori dalla suite (repository temporaneo): avviso senza libro attivo; `zb nuovo
libri/giallo/briefing.md` crea il libro e imposta `libro-attivo.md`; bloccati `motore/`, un altro libro e
un file fuori dal repository; consentito il briefing di un libro non ancora nato; con `zb lavoro motore`
consentito `motore/` e bloccato `libri/`; `zb nuovo` fuori da `libri/` senza `ZB_PROVE` rifiutato.

## Suite

`ZB_LANGUAGETOOL=<scratchpad>/lt/lib ZB_BANCA_VOCI=/home/user/banca-voci python3 -B motore/zb prove`,
eseguita una volta: **457/457 OK**, 0 saltate. `separazione.py` OK, `recinto.py` OK (48 esecuzioni).

Esecuzioni precedenti non salvate: 454/457 (i tre conflitti sopra), poi 456/457 («frasi obbligatorie
mancanti» in CLAUDE.md: tolta per errore la parola «indicato» da «la cartella del libro indicato»;
ripristinata con l'ok dell'autore).
```

### `motore/prove/esiti/solo-il-motore.md`

```markdown
# Solo il motore nel repository: esito

Data: 2026-10-13. Ramo motore, partendo da f27082e.

## Passo B: riferimenti testuali ai libri reali

Nel ramo non c'erano manoscritti reali, ma restavano riferimenti nel testo. Sono stati sostituiti sul posto.

| File | Prima | Dopo |
|---|---|---|
| `prove/attesi.yaml` | commento con lotto e titolo di un libro | «Correzioni su interludi, impronte e grafie» |
| `prove/attesi.yaml` | chiavi `correzioni_lotto_…` e `correzioni_dopo_lotto_…` | `correzioni_interludi_e_grafie`, `correzioni_esclusioni_e_budget` |
| `prove/attesi.yaml` | frasi di prova riprese da un libro (escludi_pattern, pattern «Non era X. Era Y.») | frasi inventate con lo stesso numero di parole, la stessa punteggiatura e lo stesso schema («fischio del treno», «la villa di Ardena», «la scatola sotto il letto») |
| `script/stile.py` | esempio nel commento ripreso da un libro | «il fischio letterale del treno» |
| `script/prove.py` | funzioni e sezioni con i numeri dei lotti di un libro | `correzioni_interludi_e_grafie` («interludi e grafie»), `correzioni_esclusioni_e_budget` («esclusioni e budget») |
| `prove/esiti/pdf-indipendente-dal-container.md` | titolo e autore di un libro | «autore di libro.yaml», «qualunque libro in A5, compreso un libro di prova» |
| `prove/esiti/passo-6.md` | «libro 1», «libro 2», suffisso di un ramo di libro, percorsi con il nome del repository | formulazioni neutre |
| `prove/esiti/passo-5.md`, `proposta-motore.md` | nome del repository | «repository» |

Suite dopo la sostituzione: **424/424 OK**. Le prove sostituite danno lo stesso esito di prima.

Controllo finale sui nomi reali (titoli, autori, personaggi, luoghi, nome del repository e dei rami
dei libri, presi dai file dei libri disponibili in sessione; la lista non è salvata nel repository):
0 occorrenze di riferimenti. Restano 3 parole comuni della lingua, usate nel loro senso normale nei
testi dei mini-libri inventati: coincidono solo per caso con un nome proprio di un libro.

## Passo D: archivio e rimozione di `ghimoney/`

`ghimoney/` era un progetto separato (misura dell'impatto di repository open-source, 80 file), non il motore.

- Archivio: ramo `archivio/ghimoney` su origin, creato dal commit 572f40f, con `ghimoney/` per intero.
- Copia fuori dal repository, nello scratchpad della sessione: vive solo nel container. La copia che
  conta è il ramo su origin.
- Verifica prima della rimozione, con un manifesto sha256 per ciascuna delle tre fonti (origine su disco,
  copia, ramo su origin): 80 file in ognuna, manifesti identici riga per riga. Nessun file non tracciato
  dentro `ghimoney/`.
- Rimozione: `ghimoney/` tolto dal ramo del motore; da `.gitignore` tolta la riga `.ghimoney/`, che
  serviva solo a quel progetto.
- Per recuperarlo: `git checkout origin/archivio/ghimoney -- ghimoney`.
```

### `motore/prove/esiti/voce-solo-schede.md`

```markdown
# Banca-voci con sole schede: esito

Data: 2026-10-13. Ramo motore, partendo da 80d7f46.

## Regola

Il motore è generico e vale per qualsiasi libro. La banca-voci contiene solo schede di voce e divieti:
niente pagine di libri, manoscritti, nomi di romanzi, personaggi o luoghi reali, né nel motore né nella
banca. Il contenuto di ogni libro lo decide l'autore nel briefing.

## Correzioni al motore (commit di pulizia)

- `voce.py`: `zb voce verifica` non richiede più pagine d'esempio. Controlla: voce nell'indice, scheda
  presente con le 7 sezioni e il campo «ambientazione:», `divieti.yaml` leggibile, stato «pronta».
- `prove/banca-voci-prova/`: tolte le cartelle `esempi/` della mini-banca inventata.
- `README.md`, `report-motore.md`, `passaggio-di-consegne.md`: niente pagine d'esempio; il punto aperto
  sulle voci nuove è ora «le voci si aggiungono in banca-voci quando l'autore lo decide», senza nomi.

## Prove cambiate (perché cambia il requisito, non per farle passare)

| Prova | Prima | Dopo | Motivo |
|---|---|---|---|
| (a) verifica della voce pronta | «7 sezioni, 2 esempi, 3 divieti, pronta» | «7 sezioni, 3 divieti, pronta» | gli esempi non fanno più parte della verifica, quindi l'uscita non li conta |
| (c) scheda rotta | «un solo esempio» → KO | «scheda assente» → KO | il requisito «≥ 2 esempi» non esiste più: la prova che lo controllava non ha più oggetto; al suo posto si prova l'altro requisito di file, la scheda presente |

Tutte le altre prove della sezione «voce» sono invariate. Totale invariato: 25 nella sezione, 454 in tutto.

## Suite

`ZB_LANGUAGETOOL=<cartella>/lib ZB_BANCA_VOCI=<banca-voci> python3 -B motore/zb prove`:
**454/454 OK**, 0 saltate. `separazione.py` OK, `recinto.py` OK (48 esecuzioni).

## Regressione sulla banca reale

Tolta la sezione 5 dalla scheda di una delle due voci pronte: `zb voce verifica` → codice 1,
«sezione 5 «Adattamento per genere» mancante». Scheda ripristinata: codice 0, «7 sezioni, 90 divieti,
pronta». L'altra voce: «7 sezioni, 60 divieti, pronta». I campioni-modello delle due schede non
contengono espressioni dei rispettivi `divieti.yaml`.

## Controllo dei nomi reali

Grep su tutti i file tracciati del motore e su `CLAUDE.md`, con i titoli, gli autori e i nomi propri
letti in memoria dai rami dei libri su origin (la lista non è salvata nel repository): nessun nome di
libro, autore o personaggio reale. Le sole coincidenze sono parole comuni della lingua (usate nel loro
senso normale) e nomi inventati di un ramo di prova, già usati nei mini-libri inventati.
```

### `motore/prove/esiti/voce.md`

```markdown
# Voci narrative dalla banca-voci: esito

> Superato in parte da `voce-solo-schede.md`: le pagine d'esempio non sono più richieste né presenti.

Data: 2026-10-13. Ramo motore, partendo da b36a438.

## Correzioni al motore

| Commit | Cosa |
|---|---|
| fd404a8 | `voce.py` e `zb voce lista / mostra / verifica`; `ZB_BANCA_VOCI` (README, «Banca-voci»); blocco `voce: {slug, ambientazione}` in schema, modello e `zb nuovo`; «Letto» di `zb avvio` con briefing e scheda della voce, AVVISO se la voce non verifica; divieti della voce in `stile.py` (modalità avviso); regola in CLAUDE.md; `voce.py lista` tra i comandi di `recinto.py` |
| 783216e | `modelli/briefing.md`: Storia, Schede dei personaggi («sempre», «quasi sempre», «mai»), Luoghi ed epoca, Regole del libro, Voce scelta e ambientazione; esempio inventato dentro un commento |
| e619bcf | prove della sezione «voce» (+25) sulla mini-banca inventata `prove/banca-voci-prova/` |

I libri senza il blocco `voce` restano identici: stessa uscita di `zb avvio` con e senza
`ZB_BANCA_VOCI`, nessun divieto in più in `zb stile`.

## Prove (`script/prove.py`, sezione «voce»)

| Gruppo | Prove | Copre |
|---|---|---|
| (a) | 7 | lista, mostra (blocco, 7 sezioni), mostra di una voce non pronta (avviso), blocco inesistente, verifica OK, verifica della voce non pronta (KO), voce assente dall'indice (FERMO) |
| (b) | 2 | senza `ZB_BANCA_VOCI` (lista, mostra, verifica: FERMO con il nome della variabile), cartella senza `indice.yaml` |
| (c) | 5 | scheda rotta: `divieti.yaml` non leggibile, sezione 4 tolta, «ambientazione:» tolta, un solo esempio; scheda ripristinata: OK |
| (d) | 1 | libro senza voce: avvio identico con e senza la variabile, nessuna voce in «Letto» |
| (e) | 4 | briefing con la voce → blocco in `libro.yaml`; «Letto» con scheda e briefing (11 file, 0 avvisi); senza variabile: AVVISO; voce non pronta: AVVISO, non blocco |
| (g) | 3 | divieti della voce in `stile.py`: libro senza voce (niente), senza banca (niente), con voce e banca (3 AVVISO) |
| (f) | 3 | voce senza slug rifiutata dallo schema; `zb aiuto` elenca `zb voce`; modello del briefing (sezioni nuove, campi della voce, esempio fuori dai dati) |

Nessun traceback in nessun caso d'errore.

## Suite

`ZB_LANGUAGETOOL=<cartella>/lib ZB_BANCA_VOCI=<banca-voci> python3 -B motore/zb prove`:
**454/454 OK**, 0 saltate (429 di prima + 25). `separazione.py` OK, `recinto.py` OK (48 esecuzioni).

## Prova di regressione sulla banca reale

Sulla banca-voci reale (fuori dal repository), tolta una sezione dalla scheda della voce pronta:
`zb voce verifica` → codice 1, «sezione 3 «Ritmo e sintassi» mancante». Scheda ripristinata: codice 0,
«7 sezioni, 5 esempi, 60 divieti, pronta». Controllo finale: nessuna delle 5 pagine-modello contiene
espressioni di `divieti.yaml`; parole guida entro 1 ogni 120 parole; 290-316 parole per pagina.

## Separazione

Nel motore solo la mini-banca inventata (voci, frasi e nomi inventati). Le voci reali, le loro
pagine-modello e gli eventuali brani di manoscritti stanno solo nella banca-voci.
```

### `motore/prove/mini-libro-adozione/03-architettura/manuale-di-stile.md`

```markdown
# Manuale di stile — Il faro spento

Genere: narrativa-letteraria

## Voce

- Terza persona, passato.

## Lunghezze

- Obiettivo: 60000 parole.
- Capitolo: minimo 2500, media 3500-5000, massimo 7000 parole.

## Frase e dialogo

- Frase media: 8-12 parole.
- Dialogo: 15-35% delle parole del capitolo.

## Tetti e vietati

- Tetto: «come se» al massimo 2 per capitolo.
- Vietato: «il cuore in gola».

## Vincoli

- «Bice Orlandi» non compare nei capitoli 1-2.

## Struttura

- Intestazione del capitolo: «Luogo — giorno e data».
- Separatore di scena: «* * *».
```

### `motore/prove/mini-libro-adozione/03-architettura/scaletta.md`

```markdown
# Scaletta — Il faro spento

| Unità | Data | Contenuto | Chiusura |
|---|---|---|---|
| 1 | 1987-03-02 | Il faro si spegne durante la burrasca | G |
| 2 | 1987-03-03 | Anselmo risale la scala con la lanterna | O |
| 3 | 1987-03-05 | La postina porta una lettera senza mittente | B |
```

### `motore/prove/mini-libro-adozione/04-manoscritto/01-il-faro.md`

> Escluso su richiesta (manoscritto).

### `motore/prove/mini-libro-romance/00-progetto/briefing.md`

```markdown
# Briefing

Titolo di lavoro: Prova d'inchiostro
Autore: Autrice di Prova
Genere: romance
Lettore: lettrice di romanzi d'amore ambientati al mare
Lunghezza (parole): 4400
Persona e tempo: terza persona, passato

## Idea (massimo 5 righe)
Una restauratrice di libri arriva in una pensione chiusa in un paese di mare inventato.
Il nipote della proprietaria la ospita lo stesso.
Un atlante del padre di lei lega le due famiglie.

## Tono e voce desiderati
Caldo, frasi distese, molto dialogo.

## Personaggi chiave
- Lidia Fenzi — restauratrice di libri — 34 anni
- Tomas — falegname, nipote della proprietaria
- Signora Vitale — proprietaria della pensione

## Fatti canonici
- Il padre di Lidia, Alberto Fenzi, è morto l'inverno precedente.

## Cose da non cambiare
- Il nome del nonno di Tomas non compare nel capitolo 1.

## Divieti
- Nessun cliché della lista nera.

## Riferimenti
- Nessuno.
```

### `motore/prove/mini-libro-romance/03-architettura/piano-parole.md`

```markdown
# Piano parole — Prova d'inchiostro

| Parte | Cap. | Titolo | Funzione | Scene | Budget capitolo | Budget per scena | Parole reali | Scarto |
|---|---|---|---|---|---|---|---|---|
| — | 1 | La pensione | apertura | 3 | 1600 | 530 | | |
| — | 2 | La cantina | complicazione | 2 | 1600 | 800 | | |
| — | 3 | Capitolo-prova | prova | 1 | 1200 | 1200 | | |

Totale: 4400.
```

### `motore/prove/mini-libro-romance/03-architettura/scaletta.md`

```markdown
# Scaletta — Prova d'inchiostro

Chiusure: G = gesto, O = oggetto, B = battuta, D = domanda.

| Unità | Data | Contenuto | Chiusura |
|---|---|---|---|
| 1 | sabato 11 giugno 2022 | La pensione chiusa, l'atlante, la cena. | D |
| 2 | domenica 12 giugno 2022 | La cantina, la stecca d'osso, la telefonata della zia. | D |
| 3 | — | Capitolo-prova comune ai due mini-libri. | D |
```

### `motore/prove/mini-libro-romance/04-manoscritto/01-la-pensione.md`

> Escluso su richiesta (manoscritto).

### `motore/prove/mini-libro-romance/04-manoscritto/02-la-cantina.md`

> Escluso su richiesta (manoscritto).

### `motore/prove/mini-libro-romance/04-manoscritto/03-capitolo-prova.md`

> Escluso su richiesta (manoscritto).

### `motore/prove/mini-libro-romance/cronologia.yaml`

```yaml
# Cronologia del mini-libro romance (inventata).
nascite:
  - {chi: Lidia Fenzi, data: 1988-04-15}
eventi:
  - {id: spedizione_atlante, data: 2012-05-20, capitolo: 1, descrizione: "il timbro sulla scatola dell'atlante"}
  - {id: morte_padre, data: 2022-01-12, capitolo: 1, descrizione: "morte di Alberto Fenzi"}
  - {id: arrivo, data: 2022-06-11, capitolo: 1, descrizione: "Lidia arriva ad Ardena"}
durate:
  - {da: spedizione_atlante, a: arrivo, valore: "dieci anni", tolleranza_mesi: 6}
cifre:
  - {id: distanza_paese, valore: 40, unita: chilometri, forme_ammesse: ["quaranta"]}
eta_per_capitolo: {calcolata: true}
```

### `motore/prove/mini-libro-romance/libro.yaml`

```yaml
# Mini-libro di prova del motore (romance). Tutto inventato: nessun riferimento a libri reali.
# Il capitolo 3 ha lo stesso testo del capitolo 1 del mini-libro giallo (capitolo-prova, B.2.2).
titolo: "Prova d'inchiostro"
sottotitolo: "Romanzo"
autore: "Autrice di Prova"
lingua: it
modalita: nuovo
serie: {nome: "Prove del motore", numero: 1}
ebook: true
profilo: romance
override: []

parole:
  metodo: unico
  target_totale: 4400

formato:
  pagina_pollici: [5.5, 8.5]
  carta: crema
  bleed: false
  margini_mm: {alto: 20, basso: 22, esterno: 16, interno_scelto: 17}
  font: {nome: "EB Garamond", corpo_pt: 11.5, interlinea: 1.5}
  numerazione: {da: capitolo_1, pagine_iniziali: senza_numero, posizione: piede_centro}

voci:
  - {id: farfalle, pattern: '(?i)farfalle nello stomaco', modalita: vieta}

nome_vietato_prima_di:
  - {nome: "Vittorio Alessi", pattern: '\bVittorio Alessi\b', vietato_in: ["1"], obbligatorio_in: []}

dichiarazioni:
  pov: {valori: [Lidia, Irene]}
  chiusura: {sigle: [G, O, B, D], prevista_da: scaletta, D_massimo_consecutivi: 2}   # gesto, oggetto, battuta, domanda

struttura:
  separatore_scena: {sorgente: "~", stampa: "❦"}
  intestazione_capitolo: "Nome"
  parti: []
  interludi: []

calendario: {anni_ammessi: [2022]}
ortografia: {parole_ammesse_file: nomi_propri.txt}

copyright:
  riga: "© {anno} {autore}. Tutti i diritti riservati."
  anno: 2026
  fantasia: "Quest'opera è frutto di fantasia. Nomi, personaggi, luoghi e fatti sono invenzione dell'autrice o usati in modo fittizio; ogni somiglianza con persone, vive o scomparse, o con fatti realmente accaduti è puramente casuale."
  nota_autore: "Ardena e Sorvegna non esistono."
```

### `motore/prove/mini-libro-romance/nomi_propri.txt`

```text
Ardena
Lidia
Fenzi
Tomas
Vitale
Alberto
Vittorio
Alessi
Irene
Calvi
Ottavio
Brenna
Gemma
Rosselli
Sorvegna
```

### `motore/prove/mini-libro/00-progetto/briefing.md`

```markdown
# Briefing

Titolo di lavoro: Prova di stampa
Autore: Autore di Prova
Genere: giallo
Lettore: lettore di gialli brevi di paese
Lunghezza (parole): 3000
Persona e tempo: terza persona, passato

## Idea (massimo 5 righe)
In un paese inventato il farmacista viene trovato morto nel retro della farmacia.
La commissaria segue un registro con cifre in inchiostro azzurro.
La soluzione arriva dalla sorella del farmacista.

## Tono e voce desiderati
Sobrio, frasi brevi.

## Personaggi chiave
- Irene Calvi — commissaria — 35 anni — paziente, annota tutto
- Ottavio Brenna — farmacista, la vittima
- Gemma Rosselli — commessa della farmacia
- Lodovico Arsa — meccanico, porta i pacchi il giovedì
- Marta Brenna — sorella della vittima

## Fatti canonici
- La morte avviene lunedì 1 marzo, tra le 22 e le 23.

## Cose da non cambiare
- Il nome di Lodovico Arsa non compare prima del capitolo 3.

## Divieti
- Nessun dettaglio tecnico sui farmaci.

## Riferimenti
- Nessuno.
```

### `motore/prove/mini-libro/03-architettura/piano-parole.md`

```markdown
# Piano parole — Prova di stampa

| Parte | Cap. | Titolo | Funzione | Scene | Budget capitolo | Budget per scena | Parole reali | Scarto |
|---|---|---|---|---|---|---|---|---|
| — | 1 | La farmacia | apertura | 1 | 1200 | 1200 | | |
| — | 2 | L'officina | complicazione | 2 | 900 | 450 | | |
| — | interludio I | La vetrina | pausa | 1 | 150 | 150 | | |
| — | 3 | La stazione | rivelazione | 1 | 900 | 900 | | |

Totale: 3150.
```

### `motore/prove/mini-libro/03-architettura/scaletta.md`

```markdown
# Scaletta — Prova di stampa

Chiusure: D = domanda, R = rivelazione, P = pericolo, X = decisione.

| Unità | Data | Contenuto | Chiusura |
|---|---|---|---|
| 1 | martedì 2 marzo 2021 | La farmacia: il corpo, il registro, la scatola vuota. | D |
| 2 | giovedì 4 marzo 2021 | L'officina: il farmaco nel caffè, l'uomo del giovedì. | R |
| interludio I | — | La vetrina con i fiori. | — |
| 3 | martedì 9 marzo 2021 | La stazione: la sorella e la chiave del retro. | R |
```

### `motore/prove/mini-libro/04-manoscritto/01-la-farmacia.md`

> Escluso su richiesta (manoscritto).

### `motore/prove/mini-libro/04-manoscritto/02-l-officina.md`

> Escluso su richiesta (manoscritto).

### `motore/prove/mini-libro/04-manoscritto/03-la-stazione.md`

> Escluso su richiesta (manoscritto).

### `motore/prove/mini-libro/04-manoscritto/interludio-I.md`

> Escluso su richiesta (manoscritto).

### `motore/prove/mini-libro/cronologia.yaml`

```yaml
# Cronologia del mini-libro giallo (inventata).
nascite:
  - {chi: Irene Calvi, data: 1985-06-10}
  - {chi: Gemma Rosselli, data: 1999-09-02}
eventi:
  - {id: assunzione_gemma, data: 2017-09-01, capitolo: 1, descrizione: "Gemma comincia in farmacia"}
  - {id: litigio_natale, data: 2020-12-25, capitolo: 1, descrizione: "lite tra i fratelli Brenna"}
  - {id: visita_domenica, data: 2021-02-28, capitolo: 3, descrizione: "la sorella in farmacia di domenica"}
  - {id: morte, data: 2021-03-01, capitolo: 1, descrizione: "morte del farmacista, tra le 22 e le 23"}
durate:
  - {da: assunzione_gemma, a: morte, valore: "tre anni, quasi quattro", tolleranza_mesi: 6}
cifre:
  - {id: pagine_registro, valore: 32, unita: pagine, forme_ammesse: ["trentadue"]}
eta_per_capitolo: {calcolata: true}
```

### `motore/prove/mini-libro/libro.yaml`

```yaml
# Mini-libro di prova del motore (giallo). Tutto inventato: nessun riferimento a libri reali.
titolo: "Prova di stampa"
sottotitolo: null
autore: "Autore di Prova"
lingua: it
modalita: nuovo
serie: null
ebook: false
profilo: giallo
override: []

parole:
  metodo: unico
  target_totale: 3000
  unita_senza_numero: {interludi: 150}

formato:
  pagina_pollici: [5.83, 8.27]
  carta: crema
  bleed: false
  margini_mm: {alto: 20, basso: 20, esterno: 16, interno_scelto: 16}
  font: {nome: "EB Garamond", corpo_pt: 11.5, interlinea: 1.5}
  numerazione: {da: capitolo_1, pagine_iniziali: senza_numero, posizione: piede_centro}

voci:
  - {id: come_se, pattern: '(?i)\bcome se\b', modalita: conta, massimo: 2, ambito: capitolo}

vincoli_capitolo:
  - {id: chiave_retro, pattern: '(?i)\bretro\b', consentito_in_capitoli: ["1-3"]}

nome_vietato_prima_di:
  - {nome: "Lodovico Arsa", pattern: '\bLodovico\b|\bArsa\b', vietato_in: ["1-2", "interludio I"], obbligatorio_in: []}

dichiarazioni:
  chiusura: {sigle: [D, R, P, X], prevista_da: scaletta, riga_finale_min_parole: 3}   # domanda, rivelazione, pericolo, decisione

struttura:
  separatore_scena: {sorgente: "* * *", stampa: "* * *"}
  intestazione_capitolo: "Luogo — giorno e data"
  parti: []
  interludi:
    - {numero: I, dopo_capitolo: 2, titolo: "La vetrina", parte: null}

calendario: {anni_ammessi: [2021]}
ortografia: {parole_ammesse_file: nomi_propri.txt}

copyright:
  riga: "© {anno} {autore}. Tutti i diritti riservati."
  anno: 2026
  fantasia: "Quest'opera è frutto di fantasia. Nomi, personaggi, luoghi e fatti sono invenzione dell'autore o usati in modo fittizio; ogni somiglianza con persone, vive o scomparse, o con fatti realmente accaduti è puramente casuale."
  nota_autore: null
```

### `motore/prove/mini-libro/nomi_propri.txt`

```text
Sorvegna
Irene
Calvi
Ottavio
Brenna
Gemma
Rosselli
Lodovico
Arsa
Marta
```

### `motore/prove/pubblicazione/conferme-tutto-ok.yaml`

```yaml
# Conferme di prova: tutte date (percorso «tutto OK»). Inventate per le prove del motore.
isbn: kdp_gratuito
formato_confermato_kdp: true
carta: crema
dichiarazione_ai: fatta
copertina_verificata: true
categorie_coerenti: true
contenuti_verificati: true
recensioni_regolari: true
note: "prova"
```

### `motore/prove/pubblicazione/scheda-giallo.md`

```markdown
# Scheda Amazon — Prova di stampa

<!-- Testi inventati per le prove del motore. -->

Titolo: Prova di stampa
Sottotitolo:
Serie:
Autore: Autore di Prova
Editore:

## Descrizione

<b>In un paese di collina, una farmacia apre con mezz'ora di ritardo.</b>

Nel retro, il farmacista è morto sopra un registro aperto. Una tazza rovesciata, una scatola vuota, tre pagine scritte con un inchiostro più chiaro degli altri. La commissaria Irene Calvi ha un taccuino, una ragazza che non piange e un uomo che arriva il giovedì sera.

<i>Chi entrava nella farmacia quando la farmacia era chiusa?</i>

## Parole chiave

1. giallo di paese
2. commissaria di provincia
3. farmacia misteriosa
4. indagine in collina
5. registro segreto

## Categorie

1. Gialli di provincia
2. Polizieschi brevi
```

### `motore/prove/pubblicazione/scheda-romance.md`

```markdown
# Scheda Amazon — Prova d'inchiostro

<!-- Testi inventati per le prove del motore. -->

Titolo: Prova d'inchiostro
Sottotitolo: Romanzo
Serie: Prove del motore | 1
Autore: Autrice di Prova
Editore:

## Descrizione

<b>Una restauratrice di libri arriva al mare con un atlante che non è suo.</b>

La pensione è chiusa, la proprietaria è in ospedale e ad aprire la porta c'è un falegname con le mani sporche di vernice. Tra le pagine incollate dall'umidità c'è un biglietto che nessuno ha ancora letto, e in cantina una cassa di attrezzi che porta le stesse iniziali di una stecca d'osso.

<i>Che cosa lega due famiglie che non si sono mai incontrate?</i>

## Parole chiave

1. romanzo al mare
2. restauratrice di libri
3. pensione chiusa
4. segreti di famiglia

## Categorie

1. Narrativa sentimentale
2. Romanzi di formazione
3. Storie di mare
```


---

## Cose notate

Solo elencate, senza correggere nulla.

### Dove sta la Bibbia editor

1. Nel repository non c'è un file chiamato «Bibbia editor». Il salvataggio «Bibbia editor: appendici e indice» ha modificato solo `motore/PROCEDURA.md` (paragrafi «Appendici» e «Indice e sommario», sezione 7). Le regole per tutti i libri stanno in `motore/PROCEDURA.md`, con dettagli ripetuti in `motore/README.md` e `motore/proposta-motore.md`. La «bibbia» di ogni libro è invece il file `02-bibbia/bibbia.md` del libro; nel motore ce ne sono solo gli esempi inventati dei mini-libri di prova.
2. Su un altro ramo (quello della skill «atelier») esiste `atelier/bibbia/BIBBIA.md`: riguarda la grafica di siti web, non i libri. Non è copiato qui.
3. Una sezione specifica «anti-scrittura-da-IA» (frasi lunghe e corte, imperfezioni) non esiste come documento a sé. Le regole che le somigliano sono in `motore/dati/lista-nera.yaml`, nei campi `frase_media` e `dialogo_percento` dei profili e nei controlli di `motore/script/stile.py`.

### Conflitti

4. Ordine di precedenza diverso. `CLAUDE.md`: «manuale del libro (e libro.yaml) > procedura del motore > skill dell'autore». `PROCEDURA.md`: «manuale del libro e `libro.yaml` > profilo di genere > questa procedura > skill dell'autore». Solo la seconda nomina il profilo di genere.
5. Hook: «blocca» o «avvisa»? `CLAUDE.md` dice «l'hook blocca le scritture fuori dal libro attivo», e `hook_recinto.py` è «in modalità BLOCCO». `motore/README.md` dice invece «hook di Claude Code (oggi in modalità avviso, non attivi)», e `dati/hook.yaml` ha `modalita: avviso`, che però vale solo per `hook_manoscritto.py`.
6. La sezione 10 «Hook» di `PROCEDURA.md` descrive `hook_sessione.py` e `hook_manoscritto.py` ma non nomina `hook_recinto.py`, che invece è nella configurazione di esempio e in `CLAUDE.md`.
7. `dati/hook.yaml` parla della «prova dei 14 scenari»; la tabella di `PROCEDURA.md` sezione 10 ne elenca 19 (da 1 a 18, più il 5b).
8. Numero delle prove: `passaggio-di-consegne.md` dice «457/457 OK», `report-motore.md` (stato al 2026-10-13) dice «454/454 OK».
9. LanguageTool: `PROCEDURA.md` dice «circa 140 file, 240 MB», `README.md` dice «143 file, 240 MB». La differenza è minima, ma i due testi descrivono la stessa installazione in due posti.
10. Il report ogni 5 scambi è scritto in `CLAUDE.md` e in `passaggio-di-consegne.md`, ma non in `PROCEDURA.md`, che pure è indicata come il riferimento per lavorare su un libro.
11. Il README della banca-voci (privata) dice che le voci non vanno «mai nel repository del motore». La richiesta di esportazione le includeva: per questo la sezione 5 è stata consegnata a parte, non qui. Inoltre la tabella di quel README riporta per alcune voci meno generi di quelli scritti in `indice.yaml`.

### Riferimenti a file che non esistono

12. `dati/lista-nera.yaml` cita come fonte `riferimenti/05-critica-e-punteggio.md`; `dati/kdp.yaml` cita `riferimenti/11-direttive-kdp.md`. La cartella `riferimenti/` non è nel ramo `motore`.
13. `proposta-motore.md` cita molti file (`01-mercato.md`, `02-architettura.md`, … `10-lancio.md`) che non sono nel ramo `motore`.
14. La configurazione degli hook attiva su un ramo di libro richiama `motore/script/hook_manoscritto.py`, `hook_recinto.py` e `hook_sessione.py`: esistono tutti e tre nel ramo `motore`.

### Duplicati

15. La configurazione degli hook del ramo di libro (`.claude/settings.json`) è identica a `motore/dati/hook-settings.esempio.json`.
16. L'elenco dei comandi `zb` è sia in `motore/README.md` sia in `motore/zb aiuto`; `PROCEDURA.md` rimanda al README. La spiegazione della banca-voci compare quasi uguale nel README del motore e nel README della banca.
17. Ognuna delle 39 skill grafiche del ramo «atelier» porta con sé la propria copia della licenza.

### Parti che sembrano inutili o vuote

18. `motore/dati/nomi_vietati.txt` contiene solo commenti: nessun nome. Il controllo di `separazione.py` sui nomi vietati, oggi, non controlla niente.
19. `motore/dati/lingue.yaml` elenca solo l'italiano.
20. `motore/dati/verifiche-kdp.md` è un registro quasi vuoto (324 byte).
21. Le cartelle `voci/<slug>/materiali/` della banca-voci contengono solo un `LEGGIMI.md`.
22. Le skill del ramo «atelier» (grafica web, three.js, animazioni) non c'entrano con il motore dei libri.
23. `motore/prove/mini-libro-adozione/` non ha `libro.yaml`: è voluto, perché serve a provare `zb adotta`.

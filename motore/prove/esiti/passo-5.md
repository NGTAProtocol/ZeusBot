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
| `CLAUDE.md` (radice di ZeusBot) | 27 |
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

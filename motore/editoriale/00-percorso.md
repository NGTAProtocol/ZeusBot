# Percorso di un libro

Vale per i libri con `percorso: editoriale` in `libro.yaml` (lo scrive `zb nuovo`). I libri nati prima
(senza il campo) seguono il percorso breve: documenti, pagina campione, stesura, chiusura.

| # | Fase (`stato.yaml`) | Chi lavora (agente) | Gate |
|---|------|-----------|---------|
| 1 | Briefing | autore | - |
| 2 | Apertura della cartella unica `libri/<slug>/` | motore (`zb nuovo`) | - |
| 3 | `struttura` | architetto-struttura | - |
| 4 | revisione della struttura (dentro `struttura`) | diagnosta, poi editor-strutturale (piano di revisione) | `struttura` |
| 5 | `documenti` (bibbia, codex, cronologia, manuale) | direttore-editoriale | `documenti` |
| 6 | `pagina_campione` | scrittore-voce | `pagina_campione` |
| 7 | `stesura`, capitolo per capitolo | scrittore-voce, poi capsula | `primi_capitoli`, `lotto`, `controllo_fallito` |
| 8 | `revisione_manoscritto` | diagnosta, poi editor-strutturale | `revisione_manoscritto` (sul piano) |
| 9 | `line` | line-editor | `line` |
| 10 | `copy` | correttore-italiano | `copy` |
| 11 | `bozze` | correttore-bozze | `bozze` |
| 12 | `chiusura` meccanica | motore | - |

Chiusura meccanica, in ordine: continuita, ortografia, compila, impagina, pdf, pacchetto, kdp, pronto.
Traduzione (facoltativa, dopo la chiusura): `lingue/traduzione.md`.

## Regole di fermata
- Ogni gate si apre con `zb pronto`; risposte dell'autore: `avanti`, `ok`, `correggi: …`, `stato`.
- Non si passa alla fase successiva senza `ok`.
- Fasi 8-11 in due tempi: proposte (rapporti) → gate → applicazione delle sole proposte approvate →
  `zb pronto` (passa alla fase successiva senza un secondo gate).
- Se un ruolo trova un problema G1 (bloccante), si ferma e lo segnala; non lo risolve da solo.
- Il canone (fatti bloccati in `stato.yaml`) cambia solo con il gate `canone` (`zb canone`).

## Separazione dei ruoli
Un subagente = un ruolo, in contesto pulito. Chi scrive non rivede: i rapporti di revisione stanno in
un commit che non tocca il testo rivisto (lo controlla `zb pronto`), e durante la `stesura` non
esistono rapporti di line editing o copyediting (lo controlla `zb esito`).

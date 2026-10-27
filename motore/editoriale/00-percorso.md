# Percorso di un libro

Modo automatico (decisione dell'autore del 2026-10-20, confermata il 2026-10-27): il motore controlla e passa da una
fase all'altra da solo; le fermate sono la **pausa di lettura** (ogni `pausa_lettura` capitoli e a fine stesura), un
**FERMO** del motore (controllo fallito, secondo «non passa» della revisione) e il **canone**. Un gate di fase si
ferma solo se è elencato in `gate` di `libro.yaml` (lo decide il briefing).

| # | Fase | Chi lavora | Strumento |
|---|------|-----------|-----------|
| 1 | Briefing e pagine campione della voce | autore | `modelli/briefing.md`, `00-progetto/voce/` |
| 2 | Apertura della cartella unica `libri/<slug>/` | motore | `zb nuovo` |
| 3 | Struttura | architetto della struttura | nove file di `03-struttura/` |
| 4 | Revisione della struttura | diagnosta, poi editor strutturale (agenti diversi) | `zb pronto` la verifica |
| 5 | Documenti (bibbia, codex, cronologia, manuale, nota di direzione) e voce del libro | direttore editoriale, agente voce | `zb voce campioni`, `zb voce scheda` |
| 6 | Pagina campione | scrittore con voce | `zb pronto` |
| 7 | Stesura | scrittore → misure → diagnosta → correzione → esito → capsula | `/capitolo` |
| 8 | Revisione del manoscritto | diagnosta (critico, professore, panel), editor strutturale | `zb pronto` |
| 9 | Line editing | line editor (taglio avversario) | `/revisiona` |
| 10 | Copyediting | correttore di italiano | `/revisiona` |
| 11 | Grafica e bozze | grafico, correttore di bozze | `zb impagina`, `zb copertina` |
| 12 | Chiusura meccanica | motore | continuita, ortografia, compila, impagina, pdf, pacchetto, kdp, pronto |

## Regole
- Risposte dell'autore alla pausa di lettura: `zb ok <libro>` oppure `zb correggi <libro> <note>`.
- Un problema grave (continuità, struttura rotta, canone) ferma la catena e si segnala: non si risolve da soli.
- Chi scrive non rivede: scrittore e revisori sono agenti diversi (le scritture si registrano per agente).
- Fasi 8-10 in due tempi: rapporti (proposte) → applicazione delle proposte → `zb pronto`.
- Il canone (fatti bloccati) cambia solo con il gate `canone`.
- Vale per i libri con `percorso: editoriale` in `libro.yaml`; i libri nati prima seguono il percorso breve
  (documenti, pagina campione, stesura, chiusura).

# Percorso di un libro

| # | Fase | Chi lavora | Fermata |
|---|------|-----------|---------|
| 1 | Briefing | Autore | - |
| 2 | Apertura cartella unica `libri/<slug>/` | motore (`zb nuovo`) | - |
| 3 | Struttura | architetto della struttura | gate `struttura` |
| 4 | Revisione della struttura | editor strutturale (sessione separata) | nel gate `struttura` |
| 5 | Documenti (bibbia, cronologia, piano parole) | direttore editoriale | gate `documenti` |
| 6 | Pagina campione | scrittore con voce | gate `pagina_campione` |
| 7 | Stesura capitolo per capitolo | scrittore con voce | gate `primi_capitoli` |
| 8 | Revisione strutturale del manoscritto | editor strutturale | gate `struttura_manoscritto` |
| 9 | Line editing | line editor | gate `line` |
| 10 | Copyediting | correttore di italiano | gate `copy` |
| 11 | Bozze | correttore di bozze | gate `bozze` |
| 12 | Chiusura meccanica | motore | - |

Chiusura meccanica, in ordine: continuita, ortografia, compila, impagina, pdf, pacchetto, kdp, pronto.

## Regole di fermata
- La fermata si apre con `zb pronto`; risposte dell'autore: `avanti`, `ok`, `correggi`, `stato`.
- Non si passa alla fase successiva senza `ok`.
- Se un ruolo trova un problema grave (continuità, struttura rotta), si ferma e lo segnala; non lo risolve da solo.

## Separazione dei ruoli
Una sessione di Claude Code = un ruolo. Per cambiare ruolo: salvare, aprire sessione nuova, `zb avvio`, riga "Letto".

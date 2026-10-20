# Livello editoriale del motore

Questa cartella è il livello che trasforma il motore da linea di produzione in casa editrice.
Non contiene libri, né nomi di libri o autori reali, né contenuti di un libro (manoscritto, codex, schede e stato
stanno solo in `libri/<slug>/` del ramo del libro).

## Contenuto
- `00-percorso.md`: il percorso completo con le fermate (gate).
- `struttura/01-fase-struttura.md`: la prima fase dopo il briefing.
- `struttura/modelli/`: i documenti vuoti della fase struttura.
- `ruoli/`: otto ruoli editoriali, uno per file (diagnosta compreso).
- `diagnosi/`: principi, contratto del libro, passaggi di analisi, gravità e rapporto.
- `agenti/` e `lingue/agenti/`: dodici subagenti di Claude Code (10 + 2 per la traduzione; fonte unica; `zb agenti attiva` li installa sui rami dei libri).
- `risparmio-token.md`: subagenti, capsule e regole per pochi token.
- `anti-ia/catalogo-it.md`: schemi da IA in italiano e regole di ritmo.
- `correttore/criteri-correttore.md`: criteri del correttore di italiano.
- Estensioni: `lingue/` (profili it/en, traduzione, agenti di traduzione), `comandi/` (comandi di Claude Code).

## Regole
1. Una fonte di verità: queste regole sostituiscono ogni skill citata ma assente.
2. Chi scrive non revisiona mai il proprio testo nella stessa sessione.
3. Ogni ruolo lavora in contesto pulito: legge solo i file elencati nel suo "Input".
4. Ogni ruolo produce un report in `06-diagnostica/` del libro e non modifica il manoscritto, salvo il ruolo di correzione, solo dopo il mio ok.
5. Tutto vive nella cartella del libro (`libri/<slug>/`). Questa cartella resta nel motore in sola lettura.

## Precedenza (una sola scala)
1. manuale del libro e `libro.yaml`
2. briefing e scheda della voce (se contrastano vince il briefing, il contrasto si segnala)
3. profilo di genere
4. questa cartella (ruoli)
5. procedura del motore

# Livello editoriale del motore

Questa cartella è il livello che trasforma il motore da linea di produzione in casa editrice.
Va copiata in `motore/editoriale/` del ramo motore. Non contiene libri, né nomi di libri o autori reali.

## Contenuto
- `00-percorso.md`: il percorso completo con le fermate (gate).
- `struttura/01-fase-struttura.md`: la prima fase dopo il briefing.
- `struttura/modelli/`: i documenti vuoti della fase struttura.
- `ruoli/`: sette ruoli editoriali, uno per file.
- `anti-ia/catalogo-it.md`: schemi da IA in italiano e regole di ritmo.
- `correttore/criteri-correttore.md`: criteri del correttore di italiano.
- `ruoli/riferimenti/`: riferimenti letti solo quando servono (critica del manoscritto, lettori e panel, continuità e serie).
- `agenti/`: i ruoli come subagenti di Claude Code; `risparmio-token.md`: subagenti, capsule, misura.
- `anti-ia/catalogo-it-esteso.md`, `anti-ia/formule.yaml`: schemi J-P e formule misurate da `zb esito`.
- `glossario.md`: termini editoriali inglese-italiano usati in tutti i file.

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

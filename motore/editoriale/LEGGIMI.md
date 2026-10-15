# Livello editoriale del motore

Il livello che trasforma il motore da linea di produzione in casa editrice. Non contiene libri, né
nomi di libri o autori reali, né contenuti di un libro: manoscritto, codex, schede e stato stanno solo in
`libri/<slug>/` del ramo del libro. Si legge in sola lettura.

## Contenuto (28 file)
- `00-percorso.md`: il percorso con le fermate (gate).
- `struttura/01-fase-struttura.md` e `struttura/modelli/scaletta-capitolo.md`: la fase struttura.
- `diagnosi/` (4): principi, contratto del libro, dieci passaggi, gravità e rapporto.
- `ruoli/` (8): diagnosta, direttore editoriale, architetto della struttura, scrittore con voce,
  editor strutturale, line editor, correttore di italiano, correttore di bozze.
- `agenti/` (9): i subagenti di Claude Code, uno per ruolo più `capsula` (fonte unica; li installa
  `zb agenti attiva` sui rami dei libri).
- `anti-ia/catalogo-it.md`: schemi da IA in italiano, gravità, misure.
- `correttore/criteri-correttore.md`: criteri e passaggio operativo del correttore di italiano.
- `risparmio-token.md`: come si lavora con pochi token.
- Questo `LEGGIMI.md`.
Estensioni fuori dal conteggio: `lingue/` (profili di lingua it/en, traduzione, agenti di traduzione),
`comandi/` (comandi di Claude Code per i rami dei libri).

## Regole
1. Una fonte di verità: queste regole valgono per ogni libro; nessuna skill esterna è richiesta.
2. Chi scrive non revisiona mai il proprio testo nella stessa sessione né nello stesso commit.
3. Ogni ruolo lavora in contesto pulito: legge solo i file elencati nel suo «Input».
4. Ogni ruolo di revisione scrive un report in `06-diagnostica/` e non modifica il testo, salvo
   l'applicazione delle sole proposte approvate dall'autore al gate.

## Precedenza (una sola scala)
1. manuale del libro e `libro.yaml`
2. briefing e scheda della voce (se contrastano vince il briefing, il contrasto si segnala)
3. profilo di genere
4. questa cartella (ruoli, catalogo anti-IA, criteri del correttore)
5. procedura del motore
Ogni contrasto si segnala.

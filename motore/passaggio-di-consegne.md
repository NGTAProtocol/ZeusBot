# Passaggio di consegne: motore

Frase di apertura per la nuova chat: «Leggi motore/passaggio-di-consegne.md e docs/AVANZAMENTO_LAVORO.md e riprendi da lì».

## Stato

- Lavoro sul motore del 2026-10-15 (casa editrice), sul ramo della sessione `ccr-d1e12273-izx78k`, partito da
  `origin/motore` @ `dce3774`. L'unione nel ramo `motore` la decide l'autore. Avanzamento per sezione:
  `docs/AVANZAMENTO_LAVORO.md`.
- Suite: tutte OK con LanguageTool (560 prove al 2026-10-15), rilanciata da `zb salva` prima del push. Comando: `ZB_LANGUAGETOOL=<dir>/lib python3 -B motore/zb prove` dalla radice; tabella completa
  nel report indicato a fine output.
- Livello editoriale: 28 file ricreati esatti da `editoriale_tutto.md` più le integrazioni; estensioni `lingue/`
  (it, en, traduzione) e `comandi/` (4 comandi di Claude Code).
- Banca-voci: repository separato, fuori dal motore; i nomi delle voci stanno solo lì.

## Decisioni prese

- Percorso editoriale per i libri nuovi (`percorso: editoriale`); i libri vecchi restano sul percorso breve.
- Nomi della base editoriale adottati nel codice (`struttura_manoscritto`, `06-sottotrame-temi.md`,
  `rapporto-<ambito>.md`); piani di revisione separati per struttura e manoscritto.
- Modelli per ruolo in un solo file: `dati/modelli-ruoli.yaml` (sostituisce il `model:` dei file degli agenti).
- Recinto su tre livelli: hook (anche Bash), pre-commit di git, `zb avvio`/`zb salva`.
- Comandi da una sola fonte: `dati/comandi.yaml` (`zb aiuto`).
- Vocabolario anti-IA italiano vuoto fino ai dati; inglese con elenco esterno MIT, gravità massima P2.
- `docs/` senza esportazioni né copie della banca-voci (archivio verificato fuori dal repository).

## Regole da non violare

- Il ramo `motore` non contiene mai un libro, né nomi di libri, rami di libri o autori reali (anche in `docs/`).
- Agenti, comandi e hook spenti sul ramo `motore`; si accendono solo sui rami dei libri con l'«ok» dell'autore.
- Chi scrive non rivede: rapporti in commit separati dal testo, ruoli solo nella loro fase.
- Non toccare i rami dei libri vecchi.

## Fatto in questa sessione

- Stato attuale, avanzamento, prompt (docs/). Livello editoriale ricreato e integrato.
- Fasi e gate editoriali, struttura, codex, canone, capsule, stato compatto, prepara, ruolo, agenti, consumo.
- Recinto su Bash, pre-commit, salva, avvio del motore. Anti-IA, correttore it/en, LanguageTool, traduzione.
- Analisi di 25 repository, attribuzioni. Pulizia di docs/, CLAUDE.md, README, PROCEDURA, modello libro.yaml,
  requirements, separazione estesa. Prove: mini-libro editoriale con traduzione in inglese.

## Punti aperti

- `docs/DA_FORNIRE.md`: verifica KDP, corpus anti-IA italiano, licenze, confronto 8.4, unione nel ramo `motore`.

## Prossimo passo

- L'autore rivede e unisce il ramo nel `motore`; poi, su un ramo di libro, `zb agenti attiva --ok`.

## Ripartenza

- `python3 motore/zb lavoro motore`, `python3 motore/zb avvio` (riga «Letto»), poi `docs/AVANZAMENTO_LAVORO.md`.

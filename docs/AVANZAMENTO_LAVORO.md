# Avanzamento del lavoro sul motore

Prompt di riferimento: `docs/PROMPT_NUOVA_CHAT.md`. Ripartenza: apri una nuova chat e scrivi
«riprendi da docs/AVANZAMENTO_LAVORO.md»; si rilegge il prompt, questo file, si esegue
`python3 motore/zb avvio` e si continua dalla prima sezione non «fatto».

Ramo di lavoro: il ramo della sessione, partito da `origin/motore` @ `dce3774` (il push va sul ramo
assegnato alla sessione; l'unione nel ramo `motore` la decide l'autore).

| # | Sezione | Stato | Commit |
|---|---|---|---|
| 1 | Avvio e fotografia dei ruderi (`docs/STATO_ATTUALE.md`) | in corso | — |
| 2 | Livello editoriale (`motore/editoriale/`) | da fare | — |
| 3 | Percorso da casa editrice (fasi e gate) | da fare | — |
| 4 | Cartella unica del libro e controlli veri | da fare | — |
| 5 | Ruoli come subagenti, capsule, risparmio di token | da fare | — |
| 6 | Anti-IA | da fare | — |
| 7 | Correttore professionale italiano | da fare | — |
| 8 | Lingue e traduzione | da fare | — |
| 9 | Repository esterni (`docs/ANALISI_REPOSITORY.md`) | da fare | — |
| 10 | Pulizia | da fare | — |
| 11 | Prove | da fare | — |
| 12 | File derivati | da fare | — |
| 13 | Comandi mobile e flusso di scrittura | da fare | — |

## Note per sezione

### 1
- `zb avvio` senza libro sul ramo motore: si ferma («Uso: avvio.py <libro>»); nessuna riga «Letto».
- Suite di base (pymupdf, markdown, hunspell installati; LanguageTool no): 460/461 OK, 2 saltate,
  1 KO: «passo 5 | CLAUDE.md | frasi obbligatorie mancanti» (la prova cerca ancora «skill»,
  tolta dal commit dce3774 con la scala unica di precedenza).
- File di riferimento editoriale (editoriale_tutto.md, editoriale.zip): assenti in tutti i rami.

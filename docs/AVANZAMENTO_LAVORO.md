# Avanzamento del lavoro sul motore

Prompt di riferimento: `docs/PROMPT_NUOVA_CHAT.md`. Ripartenza: apri una nuova chat e scrivi
«riprendi da docs/AVANZAMENTO_LAVORO.md»; si rilegge il prompt, questo file, si esegue
`python3 motore/zb avvio` e si continua dalla prima sezione non «fatto».

Ramo di lavoro: il ramo della sessione, partito da `origin/motore` @ `dce3774` (il push va sul ramo
assegnato alla sessione; l'unione nel ramo `motore` la decide l'autore).

| # | Sezione | Stato | Commit |
|---|---|---|---|
| 1 | Avvio e fotografia dei ruderi (`docs/STATO_ATTUALE.md`) | fatto | 6b59a9d |
| 2 | Livello editoriale (`motore/editoriale/`) | fatto | cc58ae6, cc12973 |
| 3 | Percorso da casa editrice (fasi e gate) | fatto | cc57896 |
| 4 | Cartella unica del libro e controlli veri | fatto | 4872779 |
| 5 | Ruoli come subagenti, capsule, risparmio di token | fatto | add1f4f |
| 6 | Anti-IA | fatto | 6a383c6 |
| 7 | Correttore professionale italiano | fatto | 6a383c6 |
| 8 | Lingue e traduzione | fatto (8.4 parziale, DA_FORNIRE §6) | d73221b, d73221b |
| 9 | Repository esterni (`docs/ANALISI_REPOSITORY.md`) | fatto | 7f97ddb |
| 10 | Pulizia | fatto | 138ef20 |
| 11 | Prove | fatto | 6a383c6 (560/560) |
| 12 | File derivati | fatto | 9ee2466 |
| 13 | Comandi mobile e flusso di scrittura | fatto | add1f4f |

## Note per sezione

### 1
- `zb avvio` senza libro sul ramo motore: si ferma («Uso: avvio.py <libro>»); nessuna riga «Letto».
- Suite di base (pymupdf, markdown, hunspell installati; LanguageTool no): 460/461 OK, 2 saltate,
  1 KO: «passo 5 | CLAUDE.md | frasi obbligatorie mancanti» (la prova cerca ancora «skill»,
  tolta dal commit dce3774 con la scala unica di precedenza).
- File di riferimento editoriale (editoriale_tutto.md, editoriale.zip): assenti in tutti i rami.

### 2
- editoriale_tutto.md fornito in chat: 28 file ricreati esatti (28 marcatori = 28 file), commit cc58ae6.
- Le mie versioni scritte prima (commit 3cc8fac) sono archiviate fuori dal repository e restano nella storia git.
- Integrazioni (cc12973): nomi della base adottati nel codice; righe aggiunte dove mancavano (tag, polarità,
  sottotesto, prima riga dei rapporti, comandi zb negli agenti, note per il motore).

### 3-8 (stato al 2026-10-15)
- Codice: fasi editoriali, struttura, codex, canone, capsule, compatto, prepara, ruolo, agenti, consumo,
  recinto Bash e pre-commit, salva, anti-IA, traduci. Prove editoriali: 70/70 OK.
- Suite finale: 560/560 OK con LanguageTool (zb salva, commit della documentazione).

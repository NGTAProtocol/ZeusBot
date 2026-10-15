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
| 3 | Percorso da casa editrice (fasi e gate) | in corso | cc57896 |
| 4 | Cartella unica del libro e controlli veri | in corso | 4872779 |
| 5 | Ruoli come subagenti, capsule, risparmio di token | in corso | add1f4f |
| 6 | Anti-IA | in corso | 787ae5e |
| 7 | Correttore professionale italiano | da fare | — |
| 8 | Lingue e traduzione | in corso | 742dcf7 |
| 9 | Repository esterni (`docs/ANALISI_REPOSITORY.md`) | in corso | — |
| 10 | Pulizia | da fare | — |
| 11 | Prove | da fare | — |
| 12 | File derivati | da fare | — |
| 13 | Comandi mobile e flusso di scrittura | in corso | add1f4f |

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
- Da fare: fixture e prova della traduzione in inglese; LanguageTool (script e livello b); confronto 8.4.

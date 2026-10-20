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
| 6 | Anti-IA | fatto | 787ae5e, 6a383c6 |
| 7 | Correttore professionale italiano | fatto | 6a383c6 |
| 8 | Lingue e traduzione | fatto (8.4 parziale, DA_FORNIRE §6) | 742dcf7, d73221b |
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

## Integrazione editoriale (ramo `integrazione-editoriale`, 2026-10-20)

Base: ramo ccr (`origin/ccr-d1e12273-izx78k`, d2b8814); aggiunte da `origin/motore` (971b6df). Scelte e motivi in
`docs/DECISIONI_INTEGRAZIONE.md` (D1-D18); file da leggere dall'autore in `docs/DA_VERIFICARE_AUTORE.md`.
Fotografia del motore integrato: `docs/STATO_ATTUALE.md`.

| # | Punto | Stato | Commit | Prove |
|---|---|---|---|---|
| 0 | Verifica degli hash di partenza, ramo creato | fatto | — | 560 |
| 1 | Pacchetto (28 file) | fatto | 5ae0bda | 560 |
| 2 | Aggiunte da motore | fatto | 2787ade | 560 |
| 3 | Macchina degli stati | fatto | 1b1717c | 579 |
| 4 | Recinto, hook, cartella unica | fatto | 820a4e1 | 592 |
| 5 | Ruoli | fatto | 3070050 | 601 |
| 6 | Agenti, capsule, consumo | fatto | 0c74646 | 611 |
| 7 | Anti-IA e correttore | fatto | 12dd48a | 623 |
| 8 | Pausa di lettura | fatto | 3270e84 | 628 |
| 9 | Prove | fatto | 7770e6c | 632 |
| 10 | Attribuzioni e analisi dei repository | fatto | 078b9b3 | 632 |
| 8b | Note della pausa di lettura passate allo scrittore (D16) | fatto | 06cbb70 | 633 |
| 11 | Documentazione rigenerata | fatto | 286f793 | 633 |
| 12 | `avvio_motore()` con la riga «Letto:» | fatto | 2ed341e | 637 |
| D17 | `CLAUDE.md` allineato al flusso attuale | fatto | 05facce | 637 |
| D18 | Subagenti (12) e capsula (120-250 parole) nei file del pacchetto | fatto | 951a42c | 637 |
| — | Documenti derivati, PDF, INFRASTRUTTURA dopo D17-D18 | fatto (commit dopo 951a42c: `git log`) | — | 637 |

Dopo ogni passo: `zb salva`.

Ripartenza: apri una nuova chat e scrivi «riprendi da docs/AVANZAMENTO_LAVORO.md, sezione Integrazione
editoriale»; si legge `docs/DECISIONI_INTEGRAZIONE.md`, si controlla il ramo (`git branch --show-current`:
`integrazione-editoriale`) e si continua dal primo punto non «fatto».

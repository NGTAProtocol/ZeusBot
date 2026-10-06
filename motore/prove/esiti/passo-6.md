# Passo 6 — struttura e pulizia: resoconto

Prove: `zb prove` **289/289 OK** (12 nuove); separazione OK; recinto OK (44 esecuzioni con `pulizia.py`).

## File
- Nuovi: `dati/struttura-libro.yaml` (cartelle con scopo, modalità, momento di creazione),
  `script/pulizia.py` (`zb pulizia <libro> [--applica]`).
- Modificati: `script/nuovo.py` (nessuna cartella vuota, nessun `.gitkeep`; `01-originale` solo in
  riscrittura e il testo precedente deve stare lì), `script/comune.py` (`controlla_struttura`),
  `modelli/briefing.md`, `PROCEDURA.md`, `zb`, `script/recinto.py`, `script/prove.py`, `prove/attesi.yaml`.
- Correzione approvata: `pulizia.py` costruisce il percorso da cancellare con `comune.dentro`, senza
  ricreare cartelle (prima la riga 131 ricreava la cartella appena tolta).

## Audit di ZeusBot (solo elenco, nulla cancellato)

### Radice del ramo `claude/mister-provino-espansione`

| Voce | Scopo | Ultimo commit | Dimensione | Candidato alla rimozione |
|---|---|---|---|---|
| `.gitignore` | regole git del repository | dd5dc60 2026-09-23 | 4 KB | no |
| `CLAUDE.md` | regole di avvio delle sessioni | 71fbc62 2026-10-06 | 4 KB | no |
| `ghimoney/` | progetto separato (analisi repository GitHub) | 28560a6 2026-09-24 | 756 KB | no dal motore: è di un altro progetto; da decidere se tenerlo nei rami dei libri |
| `libri/` | libri reali, esempi da cui è nato il processo | 7692265 2026-10-01 | 7,1 MB | no (non si tocca) |
| `motore/` | motore editoriale | c3e3964 2026-10-06 | 2,3 MB (font compresi) | no |

### Rami remoti

| Ramo | Scopo | Ultimo commit | Contenuto | Candidato alla rimozione |
|---|---|---|---|---|
| `claude/claude-rc-4umw8n` | ramo principale (HEAD di GitHub) | 28560a6 2026-09-24 | `.gitignore`, `ghimoney/` | no: è il ramo principale |
| `claude/roadmemo-context-review-c9rf26` | sessione chiusa senza modifiche | 28560a6 2026-09-24 | identico al principale | sì: nessun commit proprio (decide l'autore) |
| `claude/ai-toolkit-reference-setup-b3kel4` | regola .gitignore per un riferimento locale | c047398 2026-09-29 | principale + 1 commit | possibile: un solo commit su .gitignore, da unire o scartare |
| `claude/manuscript-reader-voice-notes-s0vnee` | app lettore del manoscritto (Android) | 42fa935 2026-09-25 | storia diversa (nato da e7a94cb, prima del principale) | no: progetto a sé |
| `claude/kurgan-giorgi-thriller-3f6mfq` | primo libro reale | d31e84c 2026-10-01 | principale + `libri/` | no |
| `claude/mister-provino-espansione` | secondo libro reale + motore | c3e3964 2026-10-06 | principale + `libri/` + `motore/` + `CLAUDE.md` | no |

### Cartelle di lavoro nel container (fuori dal repository o non tracciate)

| Cartella | Scopo | Dimensione | Candidato alla rimozione |
|---|---|---|---|
| `/home/user/ZeusBot` | checkout principale, ramo del primo libro | 54 MB | no (cartella di sessione) |
| `/home/user/ZeusBot-mp` | worktree del ramo del motore | 11 MB | no finché si lavora al motore; poi sì (`git worktree remove`) |
| `/home/user/casa-editrice` | copia in sola lettura di un altro repository | 332 KB | sì a fine lavori |
| scratchpad della sessione | file temporanei, LanguageTool (240 MB) | 260 MB | sì a fine sessione |
| `/tmp/zb-prove-*` (4 cartelle) | resti di prove interrotte | 984 KB | sì |

Il container è temporaneo: tutte queste cartelle spariscono quando la sessione si chiude.

## Ramo di origine (`origin/claude/claude-rc-4umw8n`)
- Ultimo commit 28560a6 (2026-09-24), 15 commit, 81 file.
- Contiene solo `.gitignore` e `ghimoney/`: nessun libro, nessun motore.
- Tutti i rami dei libri e del motore partono da 28560a6. Fa eccezione il lettore del manoscritto,
  che ha una storia più vecchia (base comune e7a94cb).

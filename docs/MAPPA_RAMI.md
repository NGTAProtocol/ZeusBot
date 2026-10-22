# Mappa dei rami

Regole: un solo ramo di lavoro, `motore` (dal 2026-10-21, dopo l'unione di `integrazione-editoriale`); nessun ramo
si cancella; `integrazione-editoriale` resta com'è (9c54726) e non si usa più per lavorare.

Unione del 2026-10-21: `git merge -s ours origin/motore` sopra `integrazione-editoriale` (ec8fe47: la storia di
`motore` entra come antenato, il contenuto resta quello di `integrazione-editoriale`), poi la correzione di
`script/separazione.py` (1092a89); push fast-forward di `motore` da 971b6df a 1092a89. Copia di sicurezza del motore
precedente: archivio (3) su 971b6df.

Aggiornata il 2026-10-21 con git (`git fetch origin`, `git for-each-ref refs/remotes/origin`, `git log -1`,
`git merge-base --is-ancestor <ramo> origin/motore`, `git ls-remote`).
«Fuso in motore» = la punta del ramo è già contenuta in `origin/motore` (1092a89). «A cosa serve» viene dal nome
del ramo, dalle cartelle in cima al ramo e dai messaggi di commit che lo nominano; dove non c'è altro, lo dice.
I rami dei libri, e i rami d'archivio che contengono un `libro.yaml`, hanno etichette generiche (il loro nome è
vietato fuori da `libri/`, lo controlla `script/separazione.py`): si riconoscono dall'hash.

## ZeusBot (NGTAProtocol/ZeusBot)

| Ramo | Hash | Ultima data | A cosa serve | Fuso in motore |
|---|---|---|---|---|
| `motore` | 1092a89 | 2026-10-21 | unico ramo di lavoro: motore editoriale (`motore/`, `docs/`, `CLAUDE.md`), contenuto di `integrazione-editoriale` più la correzione di `separazione.py`; nessun libro | — |
| `integrazione-editoriale` | 9c54726 | 2026-10-21 | ramo dell'integrazione (base ccr più le aggiunte di `motore`, `docs/DECISIONI_INTEGRAZIONE.md`); chiuso, non si lavora più qui | sì (unione «ours», ec8fe47) |
| `ccr-d1e12273-izx78k` | d2b8814 | 2026-10-15 | «ccr»: base del ramo di integrazione (D1-D3) | sì (tramite `integrazione-editoriale`) |
| `ccr-332e9c8e-2hw45z` | aaeab3a | 2026-10-20 | cartelle `ghimoney/` e `test-video/`; ultimo commit: prova di un render video | no |
| `ccr-e70de148-ie85hq` | 0975c73 | 2026-10-13 | cartelle `agentpay/`, `atelier/`, `ghimoney/`; non riguarda il motore | no |
| archivio (1) | bb71252 | 2026-10-15 | archivio delle esportazioni doppie di `docs/` tolte da `motore` (commit 138db51 di `motore`) | sì |
| archivio (2) | 05fc414 | 2026-10-15 | archivio di `motore/ritirati/`, tolto da `motore` dopo la copia (commit ff3b2e1 di `motore`) | sì |
| archivio (3) | 971b6df | 2026-10-15 | copia di sicurezza del ramo `motore` prima dell'unione del 2026-10-21 | sì |
| `archivio/ghimoney` | 572f40f | 2026-10-13 | archivio (dal nome); cartelle `ghimoney/` e `motore/` | sì |
| `claude/claude-rc-4umw8n` | 28560a6 | 2026-09-24 | cartella `ghimoney/`; stesso commit di `claude/roadmemo-context-review-c9rf26` | sì |
| `claude/roadmemo-context-review-c9rf26` | 28560a6 | 2026-09-24 | cartella `ghimoney/`; stesso commit del ramo sopra | sì |
| `claude/ai-toolkit-reference-setup-b3kel4` | c047398 | 2026-09-29 | cartella `ghimoney/`; non riguarda il motore | no |
| `claude/manuscript-reader-voice-notes-s0vnee` | 42fa935 | 2026-09-25 | lettore dei manoscritti (`lettore-manoscritto/`, `android-lettore/`); porta il tag `lettore-apk` | no |
| libro (1) | 43713a8 | 2026-10-21 | ramo di un libro (percorso editoriale, agenti e hook installati in `.claude/`); prova degli agenti | no |
| libro (2) | f66d092 | 2026-10-14 | ramo di un libro (`libri/`, `.claude/`, `motore/`) | no |
| libro (3) | d31e84c | 2026-10-01 | ramo di un libro (`libri/`, `ghimoney/`; senza `motore/`) | no |
| libro (4) | 2b7bb64 | 2026-10-06 | ramo di un libro (`libri/`, `motore/`, `ghimoney/`) | no |
| libro (5) | 9ab990f | 2026-10-13 | ramo di un libro (`libri/`, `motore/`, `ghimoney/`) | no |
| libro (6) | b226161 | 2026-10-06 | libro di prova di genere romance, chiuso fino al PDF (`libri/`, `motore/`) | no |

Rami che non ci sono più su origin: `claude/integrazione-editoriale-motore-suuf1q` (ramo assegnato a una sessione
di Claude Code, ultimo hash visto 28560a6) risultava cancellato al `git fetch --prune` del 2026-10-21; non è stato
cancellato da questa sessione.

Tag su origin: `lettore-apk` → 42fa935 (ramo del lettore dei manoscritti). Il tag `pre-integrazione-editoriale` su
971b6df non è su origin: il push dei tag dalla sessione del 2026-10-21 è stato rifiutato (HTTP 403).

## casa-editrice (NGTAProtocol/casa-editrice), letta in sola lettura il 2026-10-21

| Ramo | Hash | Ultima data | A cosa serve | Note |
|---|---|---|---|---|
| `main` | becd0e2 | 2026-09-26 | riferimenti della casa editrice (fonte dei profili di genere: «casa-editrice main @ becd0e2» in `motore/profili/`) | un commit avanti al ramo sotto |
| `claude/setup-casa-editrice-a3ueib` | 275ac1e | 2026-09-26 | primo impianto («Setup casa editrice»); ramo predefinito del repository | contenuto in `main` |

## banca-voci (NGTAProtocol/https-github.com-banca-voci)

Non letta: in questa sessione il repository non era disponibile (accesso negato). Rami, hash e voci non sono
riportati qui.

# Attribuzioni

Materiale del motore adattato da repository esterni. Regola (docs/ANALISI_REPOSITORY.md): con licenza
permissiva (MIT) si adatta con attribuzione qui; con Apache-2.0, licenza non dichiarata, CC-BY-SA o
GPL/LGPL si prende solo l'idea, riscritta da zero. Gli originali inglesi non entrano nel repository: qui
solo nome, licenza e link. Tutto è stato riscritto in italiano e adattato all'italiano (esempi inventati,
mai tradotti). Le singole righe «Fonti delle idee» in fondo ai file del motore rimandano a questa tabella.

## Adattati con attribuzione (MIT)

| Repository | Licenza (titolare) | Commit letto | Cosa abbiamo adattato | Dove nel motore |
|---|---|---|---|---|
| [blader/humanizer](https://github.com/blader/humanizer) | MIT (© 2025 Siqi Chen) | 225a6f3 | idee di schemi da IA: aperture ripetute, «non X ma Y», massime di chiusura, connettivi riempitivi, gerundio di commento | `editoriale/anti-ia/catalogo-it-esteso.md`, `formule.yaml` |
| [chi-feng/humanizer](https://github.com/chi-feng/humanizer) | MIT (© 2026 Chi Feng) | 3a30f97 | ipofora, falsa suspense, conto alla rovescia, triade forzata, salvaguardie, «correggere per sottrazione» | idem |
| [ghanemzadeh/claude-skills](https://github.com/ghanemzadeh/claude-skills) (line-and-copy-editor) | MIT (© 2026 Nasser Ghanemzadeh) | 3ee2101 | cucitura di registro, dettaglio portabile, punteggiatura monotona, residui di chat, densità dei trattini | idem |
| [danjdewhurst/story-skills](https://github.com/danjdewhurst/story-skills) | MIT (© 2026 Daniel Dewhurst) | 4b8019d | registro dei fatti, promesse/indizi/domande con stato, esenzioni motivate, passate di revisione | `script/nuovo.py` (bibbia), `editoriale/ruoli/riferimenti/` |
| [robskidmore/fiction-skills](https://github.com/robskidmore/fiction-skills) | MIT (© 2026 Robert A. Skidmore) | 321f179 | contratto della storia | `editoriale/struttura/modelli/01-premessa.md` |
| [mrigankad/Novel-OS](https://github.com/mrigankad/Novel-OS) | MIT (© 2026 Mriganka Dey) | 1bd4b57 | centro che cede, esenzioni motivate | `editoriale/ruoli/riferimenti/critica-manoscritto.md` |
| scriven-cli 2.0.0 (npm; package.json: github.com/aihxp/scriven) | MIT (© 2026 Scriven contributors) | — (pacchetto) | lettore beta, controllo della voce | `editoriale/ruoli/riferimenti/lettori-e-panel.md` |
| [felipelobomotta-blip/book-genesis-studio](https://github.com/felipelobomotta-blip/book-genesis-studio) | MIT (© 2026 Felipe Lobo) | 46a744f | lettori ciechi in sola lettura, panel di mercato, regola di accettazione | `lettori-e-panel.md`, `editoriale/agenti/lettore-cieco.md` |
| [ThomasHoussin/Claude-Book](https://github.com/ThomasHoussin/Claude-Book) | MIT (© 2025 Thomas Houssin) | 3fdebbb | bibbia permanente separata dallo stato, estrazione della bibbia da un testo | `editoriale/ruoli/riferimenti/continuita-e-serie.md` |
| [Harshil-Jani/kindle-book-agency](https://github.com/Harshil-Jani/kindle-book-agency) | MIT (© 2026 Harshil Jani) | c1d75dc | dipendenze dei lavori, parallelo solo tra lavori indipendenti, uscita rifatta una volta | `dati/orchestrazione.yaml`, `script/agenti.py` |
| [danielrosehill/Claude-Book-Writing-Plugin](https://github.com/danielrosehill/Claude-Book-Writing-Plugin) | MIT (© 2026 Daniel Rosehill) | f594e3f | compito mai più grande di un capitolo | `dati/orchestrazione.yaml` |
| [bmad-code-org/bmad-method](https://github.com/bmad-code-org/bmad-method) | MIT (© 2025 BMad Code, LLC; nome e logo marchi) | 8f0d50e | due passaggi (struttura poi prosa), correzione minima, modifica incerta come domanda | `critica-manoscritto.md` |
| [howells/fiction](https://github.com/howells/fiction) | MIT dichiarata nei metadati (file LICENSE assente) | 2e7d4e1 | critica dell'intero manoscritto in fasi | `critica-manoscritto.md` |

## Solo idee, riscritte da zero (licenza non permissiva o non dichiarata)

| Repository | Licenza | Commit letto | Idea |
|---|---|---|---|
| [epicsagas/Velith](https://github.com/epicsagas/Velith) | Apache-2.0 (© 2026 epicsagas) | f6aab7f | fasi dopo la stesura e gravità dei rilievi |
| [haowjy/creative-writing-skills](https://github.com/haowjy/creative-writing-skills) | Apache-2.0 | 254d4bb | passaggio olistico dell'editor |
| [forsonny/Claude-Code-Novel-Writer](https://github.com/forsonny/Claude-Code-Novel-Writer) | non dichiarata | 017cd8b | ruoli come agenti nominati, «mai pronto solo perché i controlli passano» |
| [knightdx91-alt/Book-pipeline](https://github.com/knightdx91-alt/Book-pipeline) | non dichiarata (`tools/apodictic` CC BY-NC-SA, escluso) | c4e781f | registro dei fatti, segnalare senza correggere, serie e canone |
| [jwynia/agent-skills](https://github.com/jwynia/agent-skills) | non dichiarata a livello di repository | e02ec7e | protocollo prima della modifica, spirale di revisione |
| [hypnosdesign/claude-skill-scrittura-italiana](https://github.com/hypnosdesign/claude-skill-scrittura-italiana) | CC-BY-SA-4.0 (Hypnos Design) | e397599 | tre livelli di intervento, «nel dubbio, il livello minimo» |
| [languagetool-org/languagetool](https://github.com/languagetool-org/languagetool) | LGPL 2.1 | c8d4098 | usato come strumento esterno (livello b di `zb ortografia`), scaricato fuori dal repository |
| [Mte90/Gulpease](https://github.com/Mte90/Gulpease), [ilmanzo/gedit-plugin-gulpease](https://github.com/ilmanzo/gedit-plugin-gulpease) | GPL-3, Apache-2.0 | 54bdc7e, d7626f7 | indice Gulpease (formula pubblica, riscritta in `script/capitolo.py`) |

Non accessibile: mwakidenis/Publish-Books (nulla preso).

# Attribuzioni

Unione delle due versioni: ramo `ccr-d1e12273-izx78k` (d2b8814, 13 voci) e ramo `motore` (971b6df, 13 voci adattate,
8 «solo idee», 1 non accessibile). Nessuna voce tolta: dove i due rami dicono cose diverse sullo stesso repository,
la riga riporta entrambe le letture. Le schede complete sono in `docs/ANALISI_REPOSITORY.md`.

## Provenienza del materiale non esterno

- I 28 file del pacchetto editoriale (commit cc58ae6: `editoriale/00-percorso.md`, `LEGGIMI.md`, `agenti/`, `ruoli/`,
  `diagnosi/`, `anti-ia/catalogo-it.md`, `correttore/criteri-correttore.md`, `struttura/`, `risparmio-token.md`) sono
  testo fornito in chat dall'autore: nessun repository esterno, nessuna licenza di terzi.
- APODICTIC (CC BY-NC-SA 4.0, dentro `knightdx91-alt/Book-pipeline`, `tools/apodictic/LICENSE` letto al commit
  c4e781f): solo idee, nessun testo.
- robskidmore/fiction-skills (MIT): adattato in `editoriale/struttura/modelli/01-premessa.md` (sezione «Contratto della
  storia»).

## Regola

- Nessun testo esterno è copiato nel repository: ogni voce è «adattato» (riscritto in italiano, esempi inventati) o
  «solo idea» (riscritta da zero) o «nulla preso». Gli originali non sono nel repository: qui solo nome, licenza e link.
- MIT: adattamento con attribuzione in questo file.
- Apache-2.0: i due rami differivano (ccr: adattamento con attribuzione; `motore`: solo idea). L'integrazione segue la
  regola più stretta, quella di `motore`: solo idee, nessun testo; per Apache-2.0 resta l'indicazione che i file del
  motore sono riscritture, non copie (decisione D13 in `docs/DECISIONI_INTEGRAZIONE.md`).
- Licenza non dichiarata, CC BY-SA, CC BY-NC-SA, GPL, LGPL, AGPL: solo idee, mai testo né codice.
- Colonna «Fonte della licenza»: «LICENSE letto» = file di licenza aperto da chi ha scritto la scheda; «solo
  README/metadati» = file di licenza assente o non aperto; «non verificato» = nessuno dei due rami dice di averlo aperto.
  In questa integrazione ho riletto un solo file di licenza: `tools/apodictic/LICENSE` di Book-pipeline.

## Adattati con attribuzione (MIT)

| Repository | Licenza dichiarata (titolare) | Fonte della licenza | Commit letto | Uso | Cosa | Dove nel motore |
|---|---|---|---|---|---|---|
| [nousresearch/autonovel](https://github.com/nousresearch/autonovel) | non dichiarata (nessun file LICENSE) | repository letto, file LICENSE assente | d165f26 | solo idea | voti tarati con il momento più debole, taglio avversario, regole che crescono dai difetti | `ruoli/00-diagnosta.md`, `ruoli/05-line-editor.md`, `script/percorso.py` (lezioni) |
| [ThomasHoussin/Claude-Book](https://github.com/ThomasHoussin/Claude-Book) | MIT (© 2025 Thomas Houssin) | LICENSE letto | 3fdebbb | solo idea | catena con subagenti di Claude Code, scrittore su Opus, revisori separati | `editoriale/comandi/capitolo.md`, `script/agenti.py` |
| [mrigankad/Novel-OS](https://github.com/mrigankad/Novel-OS) | MIT (© 2026 Mriganka Dey) | LICENSE letto | 1bd4b57 | solo idea | controlli deterministici prima del revisore LLM (già presenti) | — |
| [aihxp/scriven](https://github.com/aihxp/scriven) (pacchetto npm scriven-cli 2.0.0) | MIT (© 2026 Scriven contributors) | LICENSE letto (`package/LICENSE`, package.json) | — (pacchetto npm, senza storia git) | adattato | regole dei segni come pavimento sotto la guida di stile; insidie per tipo di opera; registro delle promesse; ritraduzione (ccr); lettore beta, controllo della voce (`motore`) | `anti-ia/catalogo-it.md`, `script/capsula.py`, `script/traduci.py`, `ruoli/riferimenti/lettori-e-panel.md` |
| [asadeisa/book-translator](https://github.com/asadeisa/book-translator) | MIT (© 2026 asad) | LICENSE letto (ccr) | non indicato | adattato | glossario per primo; voci per blocco; controlli meccanici; rubrica di fedeltà | `script/traduci.py`, `lingue/agenti/revisore-fedelta.md` |
| [chi-feng/humanizer](https://github.com/chi-feng/humanizer) | MIT (© 2026 Chi Feng) | LICENSE letto (entrambi) | 3a30f97 | adattato | correggere per sottrazione; non aggiungere dettagli; audit non distruttivo; ipofora, falsa suspense, conto alla rovescia, triade forzata, salvaguardie | `ruoli/05-line-editor.md`, `anti-ia/catalogo-it.md`, `anti-ia/catalogo-it-esteso.md`, `anti-ia/formule.yaml` |
| [blader/humanizer](https://github.com/blader/humanizer) | MIT (© 2025 Siqi Chen); l'elenco deriva da Wikipedia «Signs of AI writing», CC BY-SA | LICENSE letto (`motore`) | 225a6f3 | adattato (idee); nessun testo dell'elenco (ccr) | aperture ripetute, «non X ma Y», massime di chiusura, connettivi riempitivi, gerundio di commento; quando non intervenire | `anti-ia/catalogo-it-esteso.md`, `anti-ia/formule.yaml` |
| [ghanemzadeh/claude-skills](https://github.com/ghanemzadeh/claude-skills) (line-and-copy-editor) | MIT (© 2026 Nasser Ghanemzadeh) | LICENSE letto (entrambi) | 3ee2101 | adattato | regola della non invenzione nel line editing; cucitura di registro, dettaglio portabile, punteggiatura monotona, residui di chat, densità dei trattini | `ruoli/05-line-editor.md`, `anti-ia/catalogo-it-esteso.md`, `anti-ia/formule.yaml` |
| [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) (ai-writing-auditor) | MIT (© 2025 VoltAgent) | LICENSE letto (ccr) | non indicato | adattato | livelli del vocabolario, gravità P0/P1/P2, profili per tipo di testo; vocabolario inglese L1-L2 | `anti-ia/catalogo-it.md`, `dati/antiia.yaml` |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) | MIT (© 2026 Conor Bronsdon) | LICENSE letto (ccr) | non indicato | adattato | misura dei falsi positivi su prosa umana | `script/antiia.py` (taratura) |
| [danjdewhurst/story-skills](https://github.com/danjdewhurst/story-skills) | MIT (© 2026 Daniel Dewhurst) | LICENSE letto (entrambi) | 4b8019d | adattato | controlli di continuità deterministici (ccr); registro dei fatti, promesse/indizi/domande con stato, esenzioni motivate, passate di revisione (`motore`) | `script/codex.py`, `script/capsula.py`, `script/nuovo.py` (`genera_bibbia`), `ruoli/riferimenti/` |
| [ThomasHoussin/Claude-Book](https://github.com/ThomasHoussin/Claude-Book) | MIT (© 2025 Thomas Houssin) | LICENSE letto (entrambi) | 3fdebbb | adattato | orchestratore che non scrive; schede dei personaggi pertinenti al writer (ccr); bibbia permanente separata dallo stato, estrazione della bibbia da un testo (`motore`) | `script/prepara.py`, `comandi/scrivi-capitolo.md`, `ruoli/riferimenti/continuita-e-serie.md` |
| [felipelobomotta-blip/book-genesis-studio](https://github.com/felipelobomotta-blip/book-genesis-studio) | MIT (© 2026 Felipe Lobo) | LICENSE letto (entrambi) | 46a744f | adattato | lineette contate solo nella narrazione (ccr); lettori ciechi in sola lettura, panel di mercato, regola di accettazione (`motore`) | `script/antiia.py`, `ruoli/riferimenti/lettori-e-panel.md`, `agenti/lettore-cieco.md` |
| [fredchu/book-translator](https://github.com/fredchu/book-translator) | MIT (© 2026 Fred Chu) | LICENSE letto (ccr) | non indicato | adattato | parallelo solo con la tabella dei termini | `lingue/traduzione.md` |
| [deusyu/translate-book](https://github.com/deusyu/translate-book) | MIT (© 2025 Rainman) | LICENSE letto (ccr) | non indicato | adattato | un termine = una traduzione; voci presenti nel blocco | `script/traduci.py` |
| [robskidmore/fiction-skills](https://github.com/robskidmore/fiction-skills) | MIT (© 2026 Robert A. Skidmore) | LICENSE letto (`motore`) | 321f179 | adattato | contratto della storia | `struttura/modelli/01-premessa.md` |
| [mrigankad/Novel-OS](https://github.com/mrigankad/Novel-OS) | MIT (© 2026 Mriganka Dey) | LICENSE letto (`motore`) | 1bd4b57 | adattato | centro che cede, esenzioni motivate | `ruoli/riferimenti/critica-manoscritto.md` |
| [Harshil-Jani/kindle-book-agency](https://github.com/Harshil-Jani/kindle-book-agency) | MIT (© 2026 Harshil Jani) | LICENSE letto (`motore`) | c1d75dc | adattato | dipendenze dei lavori, parallelo solo tra lavori indipendenti, uscita rifatta una volta | `dati/orchestrazione.yaml`, `script/agenti.py` |
| [danielrosehill/Claude-Book-Writing-Plugin](https://github.com/danielrosehill/Claude-Book-Writing-Plugin) | MIT (© 2026 Daniel Rosehill) | LICENSE letto (`motore`) | f594e3f | adattato | compito mai più grande di un capitolo | `dati/orchestrazione.yaml` |
| [bmad-code-org/bmad-method](https://github.com/bmad-code-org/BMAD-METHOD) | MIT (© 2025 BMad Code, LLC; nome e logo sono marchi) | LICENSE letto (`motore`) | 8f0d50e | adattato | due passaggi (struttura poi prosa), correzione minima, modifica incerta come domanda | `ruoli/riferimenti/critica-manoscritto.md` |
| [howells/fiction](https://github.com/howells/fiction) | MIT dichiarata nei metadati (plugin.json, README); file LICENSE assente | solo README/metadati; non verificato | 2e7d4e1 | adattato (`motore`); per ccr «solo idee, nessuna presa» | critica dell'intero manoscritto in fasi | `ruoli/riferimenti/critica-manoscritto.md` |

## Solo idee, riscritte da zero (licenza non permissiva, Apache-2.0 o non dichiarata)

| Repository | Licenza dichiarata | Fonte della licenza | Commit letto | Uso | Idea | Dove nel motore |
|---|---|---|---|---|---|---|
| [haowjy/creative-writing-skills](https://github.com/haowjy/creative-writing-skills) | Apache-2.0 (titolare non compilato) | LICENSE letto (entrambi) | 254d4bb | solo idea (ccr: «adattato», senza testo) | difetti automatici del modello; protezione di ambiguità e ripetizioni volute; MATTR; passaggio olistico dell'editor | `anti-ia/catalogo-it.md`, `lingue/en/catalogo-anti-ia.md`, `ruoli/05-line-editor.md`, `script/antiia.py`, `ruoli/riferimenti/critica-manoscritto.md` |
| [epicsagas/Velith](https://github.com/epicsagas/Velith) | Apache-2.0 (© 2026 epicsagas) | LICENSE letto (`motore`; NOTICE non verificato) | f6aab7f | solo idea | ordine delle revisioni (conferma); fasi dopo la stesura e gravità dei rilievi | `ruoli/riferimenti/critica-manoscritto.md` |
| [forsonny/Claude-Code-Novel-Writer](https://github.com/forsonny/Claude-Code-Novel-Writer) | non dichiarata | nessun LICENSE né campo license | 017cd8b | solo idea | ruoli come agenti nominati, «mai pronto solo perché i controlli passano» | `agenti/`, `ruoli/riferimenti/critica-manoscritto.md` |
| [knightdx91-alt/Book-pipeline](https://github.com/knightdx91-alt/Book-pipeline) | non dichiarata (nessun LICENSE a livello di repository) | nessun LICENSE | c4e781f | solo idea | registro dei fatti, segnalare senza correggere, serie e canone; varietà strutturale; una sola fonte di verità per libro | `ruoli/riferimenti/continuita-e-serie.md`, `script/struttura.py` |
| APODICTIC (`tools/apodictic/` dentro Book-pipeline; anotherpanacea-eng) | CC BY-NC-SA 4.0 (© 2025-2026 Joshua A. Miller, PhD) | LICENSE letto (ccr; riletto in questa integrazione al commit c4e781f) | c4e781f | solo idee, nessun testo, nessun file aperto oltre la licenza | contratto dedotto dal testo, «diagnostica e non riscrive», gravità (idee generali indicate dall'autore) | `editoriale/diagnosi/` (testo dell'autore) |
| [jwynia/agent-skills](https://github.com/jwynia/agent-skills) | non dichiarata a livello di repository (solo una skill dichiara `license: MIT`) | nessun LICENSE di repository | e02ec7e | solo idea | protocollo prima della modifica, spirale di revisione | `ruoli/riferimenti/critica-manoscritto.md` |
| [hypnosdesign/claude-skill-scrittura-italiana](https://github.com/hypnosdesign/claude-skill-scrittura-italiana) | CC-BY-SA-4.0 (Hypnos Design, dal README) | LICENSE letto (`motore`) | e397599 | solo idea | tre livelli di intervento, «nel dubbio, il livello minimo» | `ruoli/riferimenti/critica-manoscritto.md` |
| [languagetool-org/languagetool](https://github.com/languagetool-org/languagetool) | LGPL 2.1 | COPYING.txt letto (`motore`) | c8d4098 | strumento esterno, non incluso | livello (b) di `zb ortografia`, scaricato fuori dal repository con `zb languagetool installa` | `script/languagetool.py` |
| [Mte90/Gulpease](https://github.com/Mte90/Gulpease), [ilmanzo/gedit-plugin-gulpease](https://github.com/ilmanzo/gedit-plugin-gulpease) | GPL-3, Apache-2.0 (titolari non dichiarati) | file di licenza secondo il metodo di `motore`; non verificato | 54bdc7e, d7626f7 | solo idea | indice Gulpease (formula pubblica, riscritta) | `script/capitolo.py` (`gulpease`) |

## Consultati senza nulla preso, o solo come conferma (dalle schede di ccr)

| Repository | Licenza dichiarata | Fonte della licenza | Uso |
|---|---|---|---|
| rhavekost/author-toolkit | MIT | solo README e elenco dei file nella scheda; non verificato | conferma, nessuna modifica |
| itotm/calibre-novel-translator | GPL-3.0 | solo README nella scheda; non verificato | solo idee, nessun codice |
| darkautism/ai-novel-translation | nessun file LICENSE | `Readme.md` | solo idea |
| ac1982/translate-book | MIT | solo README nella scheda; non verificato | conferma, nessuna modifica |
| DDChen666/translate-book | CC BY-NC-SA 4.0 | README e LICENSE letti | solo idee, nessun testo |
| KazKozDev/book-translator | AGPL-3.0 | solo README nella scheda; non verificato | solo idee, nessun codice |
| rohitg00/awesome-claude-code-toolkit | Apache-2.0 | non verificato (ricerca per nome dei file) | nulla preso |
| rshah515/claude-code-subagents | MIT | non verificato (letta un'intestazione) | nulla preso |

## Non accessibile o non trovato

- mwakidenis/Publish-Books: non accessibile (clone 403/non trovato al 2026-10-15). Nulla preso, nulla inventato.
- kindle-book-agency: per ccr «cercato, non trovato con questo nome»; `motore` ha letto `Harshil-Jani/kindle-book-agency`
  al commit c1d75dc (riga sopra). Le due letture restano entrambe; quale repository intendeva il brief non è verificato.

Il testo integrale delle licenze MIT e Apache-2.0 è pubblico; per Apache-2.0 vale l'obbligo di indicare che i file
del motore contengono modifiche rispetto alle idee originali: sono riscritture, non copie.

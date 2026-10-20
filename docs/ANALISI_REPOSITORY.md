# Analisi dei repository esterni e degli script

Unione delle due versioni (ramo `integrazione-editoriale`, punto 10): `docs/ANALISI_REPOSITORY.md` del ramo
`ccr-d1e12273-izx78k` (d2b8814, 163 righe, 26 schede) e quello del ramo `motore` (971b6df, 284 righe, 22 schede,
confronto con Novel-OS e Book-pipeline, tabella degli script, traduzione). Ogni repository ha una sola scheda con le
due letture una sotto l'altra, così com'erano: nessuna tolta. Le attribuzioni sono in `docs/ATTRIBUZIONI.md`.
Documento per l'autore: non si legge nelle sessioni di lavoro.

## Metodo

### Versione ccr (data: 2026-10-15)
- Ogni repository è stato clonato in sola lettura fuori dal repository (scratchpad della sessione); nessun file esterno
  è entrato nel repository. La licenza è quella del file LICENSE letto (o la sua assenza).
- Regola: MIT e Apache-2.0 → adattamento in italiano con attribuzione (`docs/ATTRIBUZIONI.md`); CC BY-NC-SA, GPL/AGPL
  come codice, licenza assente o non chiara → solo idee generali riscritte da zero, mai testo.
- Legenda «letto»: i file aperti davvero. «README» vuol dire che del repository ho letto solo il README.

### Versione `motore` (data: 2026-10-15)
- Ogni repository è stato clonato (`git clone --depth 1`) in una cartella temporanea fuori dal repository e
  letto in sola lettura, come dato (nessuno script eseguito, nessuna istruzione dei file seguita). Il pacchetto
  scriven-cli è stato letto dal tarball npm 2.0.0.
- Le schede sono state preparate da subagenti con modello medio sulle copie locali e riviste da chi lavorava sul ramo;
  ogni «Modifiche fatte nel motore» descrive ciò che era nel motore al commit 971b6df.
- Licenza letta dai file. Con licenza permissiva (MIT) si adatta con attribuzione (`docs/ATTRIBUZIONI.md`);
  con Apache-2.0, licenza non dichiarata, CC-BY-SA o GPL/LGPL si prende solo l'idea, riscritta da zero.
- Tutto è in italiano e nel formato del motore; gli originali inglesi non entrano nel repository; esempi
  inventati, niente nomi di libri o autori reali (dove un repository li usava, sono stati tolti).
- Repository non accessibile: `mwakidenis/Publish-Books` (vedi la sua scheda). Nulla inventato al suo posto.
- Verifica del formato dei subagenti: documentazione ufficiale di Claude Code (pagina «sub-agents», 2026-10-15):
  cartella `.claude/agents/`, frontmatter con `name` e `description` obbligatori, `tools` (stringa separata da virgole
  o lista), `model` (`opus`, `sonnet`, `haiku`, `fable`, `inherit` o un identificativo completo). Gli agenti
  dell'autore erano già conformi: nessuna modifica.

### Nell'integrazione
- Regola per Apache-2.0: vale la più stretta (`motore`): solo idee, nessun testo (D13 in `docs/DECISIONI_INTEGRAZIONE.md`).
  Le idee che ccr aveva preso da haowjy e Velith erano già riscritte senza testo: nessun file cambia.
- Nessun repository è stato riletto in questa integrazione, tranne `tools/apodictic/LICENSE` di Book-pipeline (c4e781f).
- Nelle letture di `motore` ho aggiornato solo i nomi che nel ramo integrato sono cambiati (segnati nel testo):
  `script/anti_ia.py` → `script/antiia.py`; `zb ortografia installa` → `zb languagetool installa`; fase
  `revisione_manoscritto` → `struttura_manoscritto`. Le frasi delle schede che parlano di gate approvati
  dall'autore e di «proponi, approva, applica» descrivono il motore di allora: nel ramo integrato la scrittura è
  automatica, il motore fa i controlli e si ferma solo se qualcosa non va o alla pausa di lettura (D4, D6, D11).
- Divergenza non risolta: kindle-book-agency (ccr: non trovato con quel nome; `motore`: letto
  `Harshil-Jani/kindle-book-agency` a c1d75dc). Le due letture restano entrambe nella scheda.

## Schede

### haowjy/creative-writing-skills — Apache-2.0
#### Lettura ccr (d2b8814)
- Letto: README; `skills/writing-principles/SKILL.md`; `skills/writing-principles/resources/failure-modes.md`;
  `skills/story-review/resources/prose-critique/antipatterns.md`; `.../prose-critique/analyze.py` (inizio e funzioni);
  `agents/editor.md`; `agents/continuity-checker.md`; `agents/reader-sim.md`; `skills/story-memory/resources/writing-issues.md`.
- Preso (adattato e riscritto in italiano): i dieci difetti automatici del modello (catalogo anti-IA, note per il
  motore; catalogo inglese, sezione F); «non cancellare ambiguità, omissioni, ripetizioni volute» (line editor);
  misura della varietà lessicale MATTR (`antiia.py`); l'avvertenza che gli elenchi di parole «da IA» non sono segnali
  affidabili, soprattutto per Claude (motivo dei livelli vuoti in italiano e della gravità massima P2 in inglese).
- Idee non prese: lettore simulato e simulazione di personaggi (costo in token alto; possibile estensione).
- Modifiche fatte: `editoriale/anti-ia/catalogo-it.md` (note), `editoriale/lingue/en/catalogo-anti-ia.md` (F, G),
  `editoriale/ruoli/05-line-editor.md` (principio), `script/antiia.py` (MATTR).
#### Lettura `motore` (971b6df)
- Link: https://github.com/haowjy/creative-writing-skills
- Licenza: Apache-2.0 (testo standard; campo copyright dell'appendice non compilato, titolare: non presente nella scheda)
- Commit letto: 254d4bb
- Cosa fa: pacchetto di agenti e skill per narrativa: un coordinatore che parla con l'autore e delega ad agenti compatti (writer, critic, reader-sim, outliner, continuity-checker, editor); skill per craft, revisione per livelli e memoria della storia.
- Qualità: metodo ben pensato (un compito per agente, critici e lettori simulati in sola lettura, contesto deciso con criteri espliciti, problemi ricorrenti registrati). Limiti: dipende dal runtime Meridian/Mars, due copie delle skill da sincronizzare, solo inglese, un solo editor per tutti i livelli.
- Cosa prendiamo: passaggio olistico dell'editor (ordine dei controlli); memoria della storia e regole di contesto per ruolo; registro dei problemi ricorrenti; un solo scrittore per scena; lettore simulato con persona e confine di conoscenza.
- Cosa scartiamo e perché: runtime Meridian e gestione dei modelli; brainstormer e character-sim (il nostro architetto lavora per approvazione dell'autore); coordinatore con write/edit e approvazione «never» (incompatibile con i gate); Knowledge Graph.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): passaggio olistico dell'editor (ordine dei controlli) in critica-manoscritto.md; memoria della storia = capsule 07-capsule/ e registro dei fatti. Apache-2.0: niente testo copiato.

### Scriven (aihxp/scriven, pacchetto npm `scriven-cli` 2.0.0) — MIT
#### Lettura ccr (d2b8814)
- Letto: `package/LICENSE`, `package.json`; `templates/WRITING-RULES.md`; `templates/pitfalls/novel.md`;
  `templates/RECORD.md`; `docs/translation.md` (prima parte); elenco di `agents/` e `templates/pitfalls/`.
- Preso: regole dei segni da IA come «pavimento, non soffitto» sotto la guida di stile (coerente con la scala di
  precedenza); pacchetti di insidie per tipo di opera (catalogo, sezione G nella versione inglese; insidie per genere);
  RECORD.md → registro delle promesse generato dalle capsule (`07-capsule/registro.md`, `capsula.py`); traduzione
  unità per unità in contesto pulito, glossario prima, ritraduzione per verificare la fedeltà (`traduci.py ritraduci`).
- Non preso: motori di traduzione esterni (DeepL, Google), profilo della voce su 15 dimensioni (la banca-voci del
  motore ha già la sua scheda in 7 sezioni).
#### Lettura `motore` (971b6df)
- Link: pacchetto npm scriven-cli 2.0.0 (package.json punta a github.com/aihxp/scriven; il brief indicava https://github.com/scriven/scriven)
- Licenza: MIT, «Copyright (c) 2026 Scriven contributors» (package.json e LICENSE)
- Commit letto: non presente (cartella estratta dal pacchetto npm 2.0.0, senza storia git)
- Cosa fa: installatore che porta in vari agenti di codice oltre 100 comandi `/scr:...`, sei agenti (stesura, continuità, voce, ricerca, piani, traduzione) e modelli di file (stile, personaggi, mondo, stato); copre anche testi sacri, accademici e tecnici.
- Qualità: prompt ben strutturati con formato di rapporto, ma nessun codice di analisi del testo e documentazione difficile da verificare. Incoerenze interne: soglie di voce 80/60 nel comando e 90/75/60 nell'agente; il «beta reader tra più IA» ha un solo agente; cartella test assente.
- Cosa prendiamo: scheda di voce in nove parti; lettore beta come rapporto esperienziale con sezioni fisse; revisione della sensibilità («probabilmente voluta» o «involontaria»); riesame delle note di craft; divieto di confondere i ruoli di line e copy.
- Cosa scartiamo e perché: installatore multi-runtime e comandi per altri generi (fuori perimetro); punteggio di voce 0-100 senza metodo (non riproducibile); soglie incoerenti; continuità affidata al solo modello.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): lettore beta e controllo della voce in ruoli/riferimenti/lettori-e-panel.md; divieto di confondere line e copy nei tre livelli di intervento.

### asadeisa/book-translator — MIT
#### Lettura ccr (d2b8814)
- Letto: README; `SKILL.md` (flusso completo); `references/review-rubric.md`; `scripts/book.py` (funzione `check_chunk`).
- Preso: glossario per primo con un senso per termine; nel compito del traduttore solo le voci del glossario presenti e
  le ultime righe del blocco precedente; controlli meccanici per blocco (numeri mancanti, frasi in più, rapporto di
  lunghezza, parole non tradotte, termini del glossario); rubrica del revisore di fedeltà in ordine di gravità
  (segmento sbagliato, omissione, significato, aggiunta, identificatori, termini, struttura); note del traduttore vietate.
- Modifiche: `script/traduci.py` (controlla, prepara), `editoriale/lingue/agenti/revisore-fedelta.md`.
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### APODICTIC (anotherpanacea-eng) — CC BY-NC-SA 4.0 (non commerciale)
#### Lettura ccr (d2b8814)
- Letto: solo il file LICENSE (raw). Nessun altro file aperto, come richiesto.
- Preso: nessun testo. Le idee generali già indicate dall'autore (contratto dedotto dal testo, «diagnostica e non
  riscrive», gravità) sono nei file `editoriale/diagnosi/` forniti dall'autore e scritti dalla pratica comune.
- Per usare di più serve una licenza commerciale dall'autore del repository: decisione dell'autore (`docs/DA_FORNIRE.md`).
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### knightdx91-alt/Book-pipeline — nessun file LICENSE
#### Lettura ccr (d2b8814)
- Letto: README; `CLAUDE.md` (sezione «Structural-variety rule» e regole sulla bibbia dei personaggi); elenco di
  `docs/` e `tools/` (contiene `tools/apodictic`: non aperto).
- Preso solo come idea, riscritta: una sola fonte di verità per libro; varietà strutturale (macrostruttura scelta e
  motivata, niente capitoli uguali sui quarti esatti) → `struttura.py` e fase struttura; «budget dei tic» per
  personaggio (proposta per il codex, non implementata).
#### Lettura `motore` (971b6df)
- Link: https://github.com/knightdx91-alt/Book-pipeline
- Licenza: non dichiarata: solo idee riscritte da zero (nessun LICENSE né campo; `tools/apodictic/` è CC BY-NC-SA 4.0, «Copyright (c) 2025-2026 Joshua A. Miller, PhD», da non importare)
- Commit letto: c4e781f (24 settembre 2026; un solo commit di storia)
- Cosa fa: pipeline condivisa (`.claude/agents/`, `tools/`) con una cartella per libro; dodici agenti che comunicano solo tramite file (STATE.yaml, ENTITY_STATE.yaml, bibbia dei personaggi), tre punti di approvazione umana, tre script meccanici per libro, supporto per serie e pubblicazione.
- Qualità: il più vicino al nostro motore e il più concreto (soglie, comandi, codici di uscita). Difetti: soglie incoerenti tra documento e script, controlli solo per l'inglese, valutazione da un modello della stessa famiglia dello scrittore, gate 8,5/10 su punteggi dichiarati dal modello.
- Cosa prendiamo: registro dei fatti con flusso informativo; Guardiano che segnala e non corregge, con citazione; tetto di 3 usi per frase-firma; auto-ripetizione per punto di vista; tetto parole sul totale del libro; gestione delle serie; sconto di 0,5 per giro contro l'auto-valutazione indulgente.
- Cosa scartiamo e perché: gate a 8,5/10 (non verificabile); orchestratore autonomo (contro «proponi, approva, applica»); commit diretto sul ramo principale a ogni capitolo; parti di mercato e pubblicazione estere; indice di vendibilità; il plugin APODICTIC (licenza non commerciale).
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): registro dei fatti, Guardiano che segnala e non corregge con citazione, tetto di usi per frase-firma, serie e canone in continuita-e-serie.md; controlli bloccanti già nostri (gate, controllo_fallito, cartella unica). Licenza non dichiarata: solo idee; tools/apodictic CC BY-NC-SA, escluso.

### epicsagas/Velith — Apache-2.0
#### Lettura ccr (d2b8814)
- Letto: README (inizio); `skills/loom/quality-bar.md` (rubrica a 5 assi e tassonomia strutturale); elenco degli
  `skills/` (book-edit: fasi fact check → valutazione → developmental → line → copy → proofread → readiness).
- Preso: conferma dell'ordine delle revisioni (coincide con il percorso); i segni strutturali indipendenti dalla lingua
  (paragrafi uguali, chiusura a effetto, triadi, scene simmetriche) già nel catalogo. Non preso: punteggi numerici
  1-10 (rischio di numeri inventati dal modello).
#### Lettura `motore` (971b6df)
- Link: https://github.com/epicsagas/Velith
- Licenza: Apache-2.0, «Copyright 2026 epicsagas» (testo integrale in LICENSE; NOTICE non verificato)
- Commit letto: f6aab7f (30 settembre 2026; plugin 0.7.2, un solo commit di storia)
- Cosa fa: plugin per agenti di codice che porta un libro da pagina bianca a EPUB/PDF in sei fasi con dodici agenti, 18 skill e un piccolo programma Node di misure deterministiche (`scan`, `metrics`, `snapshot`).
- Qualità: documentazione coerente, soglie numeriche scritte nelle istruzioni e nel codice; test in `tests/` non eseguiti. Limiti: liste lessicali per inglese e coreano, esempi brevi con report sbrigativi, progetto recente con un solo contributore.
- Cosa prendiamo: fasi di editing con rapporto scritto e istantanea prima di ogni riscrittura; «misurare, leggere, riscrivere, misurare»; rilettura a freddo con verdetto a soglie; gravità Minore/Maggiore/Critico; tassonomia dei difetti «da macchina».
- Cosa scartiamo e perché: pipeline in sei fasi e fasi visive (fuori perimetro); liste lessicali non italiane; dashboard e plugin per sette strumenti; gate affidato a lettori simulati e rifacimento «fino a passare» (contro «proponi, approva, applica»).
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): sequenza delle fasi dopo la stesura (struttura_manoscritto, line, copy, bozze; in `motore` la prima si chiamava revisione_manoscritto) con gate e report in fase.py; gravità Minore/Maggiore/Critico come bloccante/serio/minore in critica-manoscritto.md. Licenza Apache-2.0: niente testo copiato.

### danjdewhurst/story-skills — MIT
#### Lettura ccr (d2b8814)
- Letto: README (sezione «The continuity engine»); elenco di `skills/`.
- Preso (riscritto): controlli di continuità deterministici: personaggio morto che compare dopo (codex, «Stato: morto
  nel capitolo N», `codex.py verifica`), promessa pagata prima di essere aperta (`capsula.py`, registro).
#### Lettura `motore` (971b6df)
- Link: https://github.com/danjdewhurst/story-skills
- Licenza: MIT, «Copyright (c) 2026 Daniel Dewhurst» (file LICENSE; package.json e README confermano)
- Commit letto: 4b8019d
- Cosa fa: 24 skill più una CLI Node senza dipendenze per pianificare e tracciare narrativa in markdown; ogni entità (personaggio, capitolo, promessa, indizio, domanda) è un file con frontmatter YAML e la CLI controlla in modo deterministico la continuità.
- Qualità: molto ordinata e documentata (formato con schema JSON, circa 140 test, CI, versione 0.24.0, manutenzione attiva). Limiti: controlli di prosa e voce solo per l'inglese, flusso pensato per Node, troppi campi per il nostro motore.
- Cosa prendiamo: un file per entità (frontmatter = macchina, corpo = umano); registro a tre voci (promesse, indizi, domande) con stati ed esenzioni motivate; stato di continuità con «imparato in»; revisione a passate ordinate.
- Cosa scartiamo e perché: CLI Node, export e skill di pubblicazione (fuori perimetro); liste di parole inglesi e id solo ASCII (inutili in italiano); narrativa ramificata (non serve al romanzo lineare).
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): registro dei fatti (chi sa che cosa, da quale capitolo), promesse/indizi/domande con stato ed esenzioni motivate nella bibbia generata da zb (nuovo.genera_bibbia) e in ruoli/riferimenti/continuita-e-serie.md; ordine delle passate di revisione in ruoli/riferimenti/critica-manoscritto.md.

### ThomasHoussin/Claude-Book — MIT
#### Lettura ccr (d2b8814)
- Letto: README; `CLAUDE.md` (orchestratore); elenco di `.claude/agents/`; `.claude/skills/perplexity-improver/SKILL.md`.
- Preso: l'orchestratore non scrive e non giudica, inietta al writer solo le schede dei personaggi pertinenti
  (→ `zb prepara` con il codex filtrato), aggiorna lo stato dopo ogni capitolo (→ capsula e stato compatto).
  Non preso: misura della perplessità con un modello locale (lenta, dipendenze pesanti).
#### Lettura `motore` (971b6df)
- Link: https://github.com/ThomasHoussin/Claude-Book
- Licenza: MIT, «Copyright (c) 2025 Thomas HOUSSIN» (file LICENSE)
- Commit letto: 3fdebbb
- Cosa fa: framework multi-agente per romanzi con orchestratore e agenti separati (pianificatore, scrittore, revisori di stile, personaggi e continuità, aggiornatore di stato); separa la bibbia permanente dallo stato transitorio per capitolo; skill per estrarre e unire bibbie da un libro sorgente.
- Qualità: struttura pulita, separazione bibbia/stato ben pensata, estrazione con prove (citazioni con capitolo, conteggi con campione). Limiti: esempio su corpus coperto da diritti e in francese, revisore di continuità con Edit/Write/Bash (da non copiare), script ebook PowerShell inutile.
- Cosa prendiamo: divisione bibbia permanente / stato transitorio; formato dei quattro file di stato per capitolo; estrazione con prove; regole di unione e conflitti; ciclo di controllo di massimo tre iterazioni.
- Cosa scartiamo e perché: esempio di libro e personaggi (diritti altrui, lingua diversa); script ebook e rilevamento «perplexity»; story-ideator (genera trame, il nostro architetto parte da una scelta dell'autore); symlink `state/current` assente nel clone.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): bibbia permanente separata dallo stato del racconto ed estrazione della bibbia da un testo esistente (passi, prove, unione, conflitti all'autore, massimo tre giri) in continuita-e-serie.md, per zb adotta.

### robskidmore/fiction-skills — MIT
#### Lettura ccr (d2b8814)
- Letto: README; elenco di `skills/`.
- Preso come conferma: «Story Contract» concordato una volta (coincide con il contratto del libro), nessuna struttura
  presunta, niente scritto senza il sì dell'autore. Nessuna modifica.
#### Lettura `motore` (971b6df)
- Link: https://github.com/robskidmore/fiction-skills
- Licenza: MIT, «Copyright (c) 2026 Robert A. Skidmore» (file LICENSE; package.json)
- Commit letto: 321f179
- Cosa fa: 17 skill (v0.4.0) che sviluppano la narrativa «a colloquio»: interrogano l'autore una domanda alla volta su una cartella di storia con file fissi (contratto, mondo, personaggi, outline, domande aperte).
- Qualità: piccolo, coerente, con decisioni documentate (ADR), glossario e tag di provenienza; niente si scrive senza il sì dell'autore. Limiti: nessun test né CI, solo inglese, dipende da «touchstones» di opere reali, contratto senza schema formale.
- Cosa prendiamo: il «contratto della storia» come accordo unico che ogni suggerimento rispetta; la «spina» prima della trama; unità di outline a tre campi; tag di provenienza e una domanda alla volta; verifica delle lacune per catena causale.
- Cosa scartiamo e perché: catalogo di touchstone (opere reali, vietate negli esempi); strutture come scelta libera (la decide il motore); skill di mondo e relazioni; config utente in `~/.config` (contro il recinto del libro).
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): contratto della storia nella fase struttura (03-struttura/01-premessa.md, sezione "Contratto della storia").

### howells/fiction — licenza non chiara (MIT dichiarata in `.claude-plugin/plugin.json`, nessun file LICENSE)
#### Lettura ccr (d2b8814)
- Letto: README; elenco di `skills/references/`.
- Solo idee: nessuna presa. Caso segnalato all'autore (licenza da chiarire).
#### Lettura `motore` (971b6df)
- Link: https://github.com/howells/fiction
- Licenza: MIT dichiarata nei metadati (plugin.json, marketplace.json, README; autore «Daniel Howells»); file LICENSE e copyright formale: non presenti nella scheda, quindi «MIT dichiarata, testo assente»
- Commit letto: 2e7d4e1
- Cosa fa: plugin per Claude Code e Codex che guida la scrittura di un romanzo con comandi e 26 agenti (architetto, scrittore, editor, continuità, lettori paralleli); quasi solo prompt in markdown, nessun codice di analisi.
- Qualità: prompt coerenti con formato di report fisso e buona idea dei lettori paralleli che scrivono un digest su file. Limiti: un solo commit, nessun test, nessuna licenza in file, agenti «in stile» di autori reali; l'algoritmo dei «word echoes» non esiste, c'è solo la richiesta di segnalare parole ripetute vicine.
- Cosa prendiamo: critica dell'intero manoscritto in fasi (completezza, digest per capitolo, sintesi, salvataggio, proposte); lettore per capitolo in parallelo con coordinatore; modalità di lunghezza; memoria dell'editor; segnalazioni di leggibilità ad alta voce.
- Cosa scartiamo e perché: agenti con nomi di autori reali (vincolo del progetto); guide di stile angloamericane, copertine, naming (fuori perimetro); il controllo delle parole ripetute così com'è, troppo vago.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): critica dell'intero manoscritto in fasi (completezza, schede di sintesi dalle capsule, sintesi, proposte) in ruoli/riferimenti/critica-manoscritto.md; ripetizioni ravvicinate in zb esito (script/antiia.py): l'algoritmo nel repository non c'è, il nostro è una proposta nostra, tarata sui mini-libri.

### rhavekost/author-toolkit — MIT
#### Lettura ccr (d2b8814)
- Letto: README; elenco dei file (`story-structure`, `fiction-workshop`, `prose-mechanics`).
- Preso come conferma: stato del progetto letto a inizio sessione e aggiornato a fine (stato compatto). Nessuna modifica.
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### felipelobomotta-blip/book-genesis-studio — MIT
#### Lettura ccr (d2b8814)
- Letto: README (inizio); `skills/book-genesis/references/patterns/ai-tells-pt-br.md` (inizio).
- Preso (riscritto): lineetta del dialogo usata anche negli incisi della narrazione come segno da contare, solo nella
  narrazione (`antiia.py`, `lineette_narrazione`, per l'italiano con le lineette); le soglie sono valori di progetto,
  non norme (lo dichiara anche `dati/antiia.yaml`); molte «spie» compaiono anche nei bestseller umani.
#### Lettura `motore` (971b6df)
- Link: https://github.com/felipelobomotta-blip/book-genesis-studio
- Licenza: MIT, «Copyright (c) 2026 Felipe Lobo» (file LICENSE)
- Commit letto: 46a744f
- Cosa fa: flusso da idea a libro in fasi (intake, architettura, stesura, audit, revisione, punteggio, pacchetto editoriale); quattro lettori ciechi simulati, un revisore in sola lettura e un panel di mercato (agente, editor, libraio, lettore target).
- Qualità: documentazione concreta (ruoli con ciò che vedono e non vedono, verdetti fissi, aggregazione numerica, indipendenza graduata A/B/C). Limiti: un solo autore, nessun lettore umano ha validato, pesante e in beta, prompt in inglese e portoghese brasiliano.
- Cosa prendiamo: protocollo dei lettori ciechi e regole di aggregazione; revisione accettata solo se i lettori preferiscono la nuova versione; dichiarazione di indipendenza dei critici; 10 passaggi dell'audit; panel con etichette «mercato/gusto».
- Cosa scartiamo e perché: punteggio con soglia (il gate è approvato dall'autore); pacchetto di pubblicazione e test dei titoli; installer multi-agente; segnali di prosa da macchina in inglese/portoghese; modalità «vai fino in fondo» senza gate.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): lettori ciechi in sola lettura (agente lettore-cieco) e panel di mercato come passo opzionale dopo la revisione strutturale, in lettori-e-panel.md.

### mrigankad/Novel-OS — MIT
#### Lettura ccr (d2b8814)
- Letto: README (inizio); `agents/continuity_guardian/prompt.md` (inizio).
- Conferma: il controllo di continuità sulle conoscenze dei personaggi (capsule: «personaggi presenti e cosa sanno»).
  Nessuna modifica.
#### Lettura `motore` (971b6df)
- Link: https://github.com/mrigankad/Novel-OS
- Licenza: MIT, «Copyright (c) 2026 Mriganka Dey» (file LICENSE)
- Commit letto: 1bd4b57 (9 agosto 2026; un solo commit di storia; versione del pacchetto non verificata)
- Cosa fa: studio di scrittura con cinque agenti (Architetto, Scriba, Editor, Guardiano, Curatore di stile) intorno a un file di stato centrale; un motore di continuità locale gira prima del Guardiano LLM; interfaccia web ed esportazione DOCX, EPUB e HTML.
- Qualità: moduli Python leggibili con costanti in testa e un test per modulo (374 test dichiarati nel README, non verificati); i risultati dei controlli entrano nel prompt del Guardiano. Limiti: tokenizzazione e liste solo inglesi; l'unico blocco vero è `approve` rifiutato se il rapporto è FAIL.
- Cosa prendiamo: registro di fili e presagi con capitolo di inizio e obiettivo; «centro che cede» (tre capitoli senza movimento misurabile); rilievi con severità, chiave stabile ed esenzioni con motivo; anteprima delle conseguenze; risultati meccanici al revisore.
- Cosa scartiamo e perché: interfaccia web, database, 13 fornitori LLM; blocchi di stato rigidi emessi dall'LLM (fragili rispetto ai nostri documenti con sha256); divieto del trattino lungo (in italiano è punteggiatura legittima); punteggi su liste di parole inglesi; macchina a stati dei capitoli.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): confronto con stato.yaml e gate (vedi sotto); preso il "centro che cede" (critica-manoscritto.md) e le esenzioni motivate; i nostri controlli tra le fasi restano deterministici in fase.py.

### ghanemzadeh/claude-skills — MIT
#### Lettura ccr (d2b8814)
- Letto: README; intestazioni di `line-and-copy-editor/SKILL.md` e `references/ai-prose-patterns.md`.
- Preso: «regola della non invenzione» nel line e copy editing (nessun dettaglio nuovo) → ruolo line editor.
#### Lettura `motore` (971b6df)
- Link: https://github.com/ghanemzadeh/claude-skills (cartella `line-and-copy-editor`)
- Licenza: MIT, «Copyright (c) 2026 Nasser Ghanemzadeh» (file LICENSE; SKILL.md dichiara `license: MIT`)
- Commit letto: 3ee2101
- Cosa fa: skill di revisione combinata (line e copy editing) per saggistica passata da bozze IA; produce modifiche tracciate in .docx, un foglio di stile e una lettera editoriale; contiene un catalogo di 40 schemi di prosa IA in 7 gruppi.
- Qualità: alta sul metodo (regola della densità, falsi positivi, segni umani da preservare, voce dell'autore che prevale, intervento minimo). Limiti: pensata per saggistica inglese e per Word/OOXML, nessun contenuto in italiano, lessico inglese non trasferibile.
- Cosa prendiamo: «bad in aggregate» (soglie per densità, non divieti); elenco dei falsi positivi e dei segni umani; punteggiatura monotona, cuciture di registro, riassunto che ripete; sweep meccanico prima della lettura; voce-baseline.
- Cosa scartiamo e perché: parte docx/track changes/XML (fuori ambito); compressione del 10-15% e citazioni (saggistica); regola Chicago su virgolette e trattini; voci lessicali inglesi.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): schemi J-P di anti-ia/catalogo-it-esteso.md (cucitura di registro, dettaglio portabile, punteggiatura monotona), salvaguardie contro i falsi positivi.

### blader/humanizer — MIT (elenco basato su Wikipedia «Signs of AI writing», CC BY-SA)
#### Lettura ccr (d2b8814)
- Letto: README; intestazioni di `SKILL.md` e sezione «When not to act».
- Non preso testo: l'elenco deriva da una pagina CC BY-SA (condividi allo stesso modo). Idea presa: quando non
  intervenire (citazioni, nomi, dettagli insoliti che sono voce).
#### Lettura `motore` (971b6df)
- Link: https://github.com/blader/humanizer
- Licenza: MIT, «Copyright (c) 2025 Siqi Chen» (file LICENSE; SKILL.md dichiara `license: MIT`)
- Commit letto: 225a6f3
- Cosa fa: skill di riscrittura (v3.1.0) che toglie i segni di scrittura IA senza inventare fatti; 26 schemi in sei famiglie (messa in scena, ritmo a regola, gonfiatura, formattazione, residui di chat, lettore sbagliato); procedimento segnare, riscrivere, controllare.
- Qualità: buona e usabile (schemi ordinati per forza, esempi prima/dopo, «quando non intervenire»). Limiti: calibrata su inglese e prosa web, regola «niente trattini» discutibile (il campione la scavalca), poco su narrativa e dialogo.
- Cosa prendiamo: famiglia A (non X ma Y, chiusure a effetto, massime, rincorse, domande retoriche) da adattare all'italiano; triadi e aperture ripetute; participi e gerundi di coda; controllo «non inventare dettagli»; «fix by subtraction».
- Cosa scartiamo e perché: lista di parole IA inglesi; copula avoidance, composti con trattino, maiuscole nei titoli (fenomeni inglesi); divieto assoluto del trattino lungo; formattazione e residui di PR/commit.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): idee di schemi adattati all'italiano in catalogo-it-esteso.md e 38 formule in anti-ia/formule.yaml contate da zb esito; modalità audit.

### chi-feng/humanizer — MIT
#### Lettura ccr (d2b8814)
- Letto: README; `SKILL.md` (principi, modalità audit, «Fixing without adding new tells», processo).
- Preso (riscritto): correggere per sottrazione, rileggere ciò che la correzione introduce, non aggiungere dettagli,
  non omogeneizzare, frequenza «su due assi» (un tic che torna in ogni capitolo conta anche se è uno per capitolo);
  modalità audit non distruttiva. Modifiche: line editor, catalogo it/en.
#### Lettura `motore` (971b6df)
- Link: https://github.com/chi-feng/humanizer
- Licenza: MIT, «Copyright (c) 2026 Chi Feng» (file LICENSE)
- Commit letto: 3a30f97
- Cosa fa: skill portabile (v6.1.0) per trovare e correggere gli schemi di scrittura IA, con modalità riscrittura e `--audit` (diff non distruttivo); diagnostiche in sette aree e autoesame finale; dichiara di derivare da blader/humanizer e dalla guida Wikipedia sui segni di scrittura IA.
- Qualità: alta, la più matura sul piano concettuale (due assi di frequenza, «non omogeneizzare», correggere per sottrazione, audit con diff). Limiti: orientata a testi tecnici e web, solo inglese, poca narrativa.
- Cosa prendiamo: audit con «cosa non è cambiato» e sezione citata; grappolo e tic ricorrente; falsa suspense, epifania fabbricata, posta gonfiata, equilibrio di facciata; controllo dei dettagli aggiunti; indice dei dispositivi retorici (antitesi, ipofora, sentenza).
- Cosa scartiamo e perché: sezione «code-adjacent» (PR, commit); lessico inglese e composti con trattino; divieto di trattini lunghi senza campione; formattazione, emoji, grassetti.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): ipofora, falsa suspense, conto alla rovescia, triade forzata, salvaguardie; correggere per sottrazione.

### itotm/calibre-novel-translator — GPL-3.0
#### Lettura ccr (d2b8814)
- Letto: README (inizio). Solo idee: riassunto della storia fin lì, glossario dei nomi, nota su come scrive l'autore
  passati al modello capitolo per capitolo → coincide con capsule + glossario + guida. Nessun codice preso.
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### darkautism/ai-novel-translation — nessun file LICENSE
#### Lettura ccr (d2b8814)
- Letto: `Readme.md`. Solo idea (due passaggi: analisi e glossario, poi traduzione): coincide con il gate «guida».
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### fredchu/book-translator — MIT
#### Lettura ccr (d2b8814)
- Letto: README (inizio).
- Preso: osservazione misurata dall'autore del repository: in parallelo senza tabella dei termini i nomi divergono, peggio
  che in sequenza → il motore traduce in sequenza e ammette il parallelo solo con il glossario approvato.
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### deusyu/translate-book — MIT
#### Lettura ccr (d2b8814)
- Letto: README (inizio); `SKILL.md` (glossario, voci per blocco, sottoagenti in parallelo).
- Preso: glossario modificabile a mano e mai sovrascritto; una forma non può stare in due termini (→ «un termine = una
  traduzione» in `traduci.py`); stampa delle sole voci presenti nel blocco.
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### ac1982/translate-book — MIT
#### Lettura ccr (d2b8814)
- Letto: README (inizio). Conferma: l'agente stesso traduce, senza API esterne. Nessuna modifica.
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### DDChen666/translate-book — CC BY-NC-SA 4.0
#### Lettura ccr (d2b8814)
- Letto: README (inizio), LICENSE. Solo idee, nessun testo; caso segnalato (non commerciale).
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### KazKozDev/book-translator — AGPL-3.0
#### Lettura ccr (d2b8814)
- Letto: README (inizio). Solo idee (nomi coerenti, modifiche verificate). Nessun codice.
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### VoltAgent/awesome-claude-code-subagents — MIT (solo agenti di scrittura)
#### Lettura ccr (d2b8814)
- Letto: `categories/04-quality-security/ai-writing-auditor.md` (intero); `categories/08-business-product/content-quality-editor.md` (inizio).
- `content-editor` non esiste in questo repository: c'è in rshah515 (sotto).
- Preso: struttura a livelli del vocabolario (sostituire sempre / in gruppo / per densità), gravità P0/P1/P2, profili per
  tipo di testo → catalogo, `dati/antiia.yaml` (vocabolario inglese L1-L2, con l'avvertenza che non è verificato su Claude).
  Non preso: riscrittura automatica (il motore è in modalità audit).
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### rohitg00/awesome-claude-code-toolkit — Apache-2.0
#### Lettura ccr (d2b8814)
- Letto: ricerca per nome dei file di agenti e comandi di scrittura. Solo agenti per contenuti di marketing e codice:
  nulla per la narrativa. Nessuna modifica.
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### rshah515/claude-code-subagents — MIT
#### Lettura ccr (d2b8814)
- Letto: `marketing/content-production/content-editor.md` (intestazione). Agente per contenuti di marketing (SEO):
  non adatto alla narrativa. Nessuna modifica.
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### conorbronsdon/avoid-ai-writing
#### Lettura ccr (d2b8814)
(«Trovati da me» nella versione ccr)
- conorbronsdon/avoid-ai-writing — MIT. Letto: LICENSE, CHANGELOG (ricerca). Preso: misurare i falsi positivi su un corpus
  scritto da persone (→ `zb antiia taratura --umano <dir>`). Fonte dell'ai-writing-auditor.
#### Lettura `motore` (971b6df)
Nessuna scheda in questo ramo.

### Harshil-Jani/kindle-book-agency
#### Lettura ccr (d2b8814)
(«Trovati da me» nella versione ccr)
- kindle-book-agency: cercato (ricerca web), non trovato con questo nome: l'idea dell'orchestrazione per dipendenze è
  applicata dalla regola del prompt (capsula N prima del capitolo N+1, gate prima della fase successiva).
#### Lettura `motore` (971b6df)
- Link: https://github.com/Harshil-Jani/kindle-book-agency
- Licenza: MIT, «Copyright (c) 2026 Harshil Jani» (file LICENSE)
- Commit letto: c1d75dc
- Cosa fa: pipeline per libri Kindle con otto agenti (nicchia, ghostwriter, copertina, marketing, editor, correttore, impaginatore, compilatore .docx) e un espansore di capitoli; l'orchestratore Python raggruppa gli agenti in fasi secondo le dipendenze con `asyncio.gather`.
- Qualità: grafo delle dipendenze esplicito (`depends_on`, `parallel_group`), concorrenza limitata con semaforo, un solo tentativo di ripetizione. Limiti: non si ferma se un agente fallisce, fasi derivate dal gruppo e non calcolate, controllo di qualità ridotto al numero di parole (soglia 500), orientamento commerciale e saggistico.
- Cosa prendiamo: dichiarare per ogni ruolo da quali uscite dipende e lanciare in parallelo solo ruoli con le stesse dipendenze; concorrenza massima configurabile; validazione dell'uscita con un solo tentativo.
- Cosa scartiamo e perché: ricerca di nicchia, copertina, marketing, formattazione Kindle (fuori perimetro); scrittura dei capitoli in parallelo senza gate (rompe la continuità di voce); assenza di arresto in caso di errore; uso dell'API con chiave.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): dipendenze dei lavori e uscita rifatta una sola volta in dati/orchestrazione.yaml; zb agenti prossimo lancia in parallelo solo i lavori indipendenti, massimo 3.

### forsonny/Claude-Code-Novel-Writer
#### Lettura ccr (d2b8814)
Nessuna scheda in questo ramo.
#### Lettura `motore` (971b6df)
- Link: https://github.com/forsonny/Claude-Code-Novel-Writer
- Licenza: non dichiarata: solo idee riscritte da zero (nessun LICENSE, nessun campo license, nessun titolare indicato)
- Commit letto: 017cd8b
- Cosa fa: spazio di lavoro per scrivere un romanzo (v4.1.0) con un AGENTS.md canonico, sette ruoli in `.agents/roles/`, cinque flussi e adattatori sottili per Claude, Codex e Pi; script bash e hook per stato, backup e controllo del capitolo.
- Qualità: architettura pulita (una definizione per ruolo, ordine di verità dichiarato, onestà sui limiti delle metriche). Limiti: nessun test automatico né CI, stato JSON quasi vuoto, nessun ruolo di editing di prosa, permessi che non separano lettura da scrittura.
- Cosa prendiamo: un file di ruolo canonico per agente; ordine di verità («la prosa esistente è canone»); protocollo di delega con passaggio di consegne conciso; gravità dei rilievi di continuità; «mai pronto solo perché i controlli passano».
- Cosa scartiamo e perché: hook, backup e JSON di tracciamento (il motore ha già stato e salvataggio); compatibilità Codex e Pi (fuori perimetro); scrittura autonoma di capitoli interi, contraria a «proponi, approva, applica».
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): ruoli come agenti nominati con file canonico (editoriale/agenti/, attivati con zb agenti); gravità dei rilievi e regola "mai pronto solo perché i controlli passano" in critica-manoscritto.md. Licenza non dichiarata: solo idee.

### mwakidenis/Publish-Books
#### Lettura ccr (d2b8814)
Nessuna scheda in questo ramo.
#### Lettura `motore` (971b6df)
- Link: https://github.com/mwakidenis/Publish-Books
- Licenza: non verificabile (repository non accessibile: clone 403/non trovato; profilo utente senza repository pubblici al 2026-10-15)
- Commit letto: non presente (repository non accessibile)
- Cosa fa: non verificabile
- Qualità: non verificabile
- Cosa prendiamo: nulla (non verificabile)
- Cosa scartiamo e perché: nulla di valutabile, per non inventare dati su un repository non letto.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): nessuna: griglia a cinque assi e lettura a freddo non prese, per non inventare.

### danielrosehill/Claude-Book-Writing-Plugin
#### Lettura ccr (d2b8814)
Nessuna scheda in questo ramo.
#### Lettura `motore` (971b6df)
- Link: https://github.com/danielrosehill/Claude-Book-Writing-Plugin
- Licenza: MIT, «Copyright (c) 2026 Daniel Rosehill» (file LICENSE)
- Commit letto: f594e3f
- Cosa fa: plugin per libri di saggistica con squadre di subagenti (definizione, pianificazione, ricerca, scrittura in parallelo, revisione, grafica, pubblicazione); principio: nessun agente riceve un compito abbastanza grande da degradare, uno scrittore per capitolo e per scheda.
- Qualità: ragionamento esplicito e motivato, agenti corti con regole chiare su cosa leggere, controllo meccanico `book.py lint`. Limiti: pensato per saggistica con fonti, verifica dei fatti non coperta, dipende da script e da un template esterno.
- Cosa prendiamo: solo l'idea del compito mai troppo grande: una scheda per capitolo, uno scrittore per capitolo che usa riassunti dei vicini, revisori che non modificano.
- Cosa scartiamo e perché: ricerca fonti, grafica, KDP, linter e script; scrittori in parallelo (nel romanzo la voce deve restare unica); il divieto di leggere il capitolo precedente (per un romanzo serve la coda del capitolo prima).
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): solo la regola del compito mai più grande di un capitolo (orchestrazione.yaml); scrittura dei capitoli sempre in sequenza, mai in parallelo.

### bmad-code-org/bmad-method
#### Lettura ccr (d2b8814)
Nessuna scheda in questo ramo.
#### Lettura `motore` (971b6df)
- Link: https://github.com/bmad-code-org/BMAD-METHOD
- Licenza: MIT, «Copyright (c) 2025 BMad Code, LLC» (file LICENSE; nome e logo sono marchi, vedi TRADEMARK.md)
- Commit letto: 8f0d50e
- Cosa fa: metodo agile a agenti per progetti software; conta solo la revisione editoriale. La skill `bmad-editorial-review-prose` (e `-structure`) non esiste più: il CHANGELOG la dà come shim della lente `prose` (e `structure`) di `skills/bmad-review`.
- Qualità: metodo breve, preciso e disciplinato (contenuto intoccabile, formato unico dei rilievi, risparmio di parole con `word_metrics.py`). Limiti: pensato per documenti tecnici, la lente struttura premia la brevità (sbagliato per un romanzo), dipende da `customize.toml`.
- Cosa prendiamo: due passaggi separati (struttura poi prosa); correzione minima; tabella dei rilievi con motivazione; apertura con scopo e pubblico; modifica incerta formulata come domanda.
- Cosa scartiamo e perché: obiettivo di riduzione di lunghezza e modelli per documentazione; lenti avversaria, casi limite, lacune di verifica (per codice); impianto TOML; il marchio.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): la skill bmad-editorial-review-prose non esiste più (diventata lente "prose" di bmad-review): presi due passaggi (struttura poi prosa), correzione minima, modifica incerta come domanda, in critica-manoscritto.md.

### jwynia/agent-skills
#### Lettura ccr (d2b8814)
Nessuna scheda in questo ramo.
#### Lettura `motore` (971b6df)
- Link: https://github.com/jwynia/agent-skills
- Licenza: non dichiarata: solo idee riscritte da zero (nessun LICENSE a livello di repository; solo la skill non-fiction-revision dichiara `license: MIT`, autore `jwynia`, copyright holder non presente)
- Commit letto: e02ec7e
- Cosa fa: grande raccolta di skill per agenti per dominio; conta `skills/general/writing/revision/non-fiction-revision/SKILL.md` (370 righe), skill diagnostica che individua a quale livello sta il problema prima di cambiare qualcosa.
- Qualità: ben strutturata (sei stati diagnostici con sintomi, domande, interventi e avviso di cascata; protocollo prima della modifica; registro delle modifiche; antischemi). Limiti: per saggistica, senza script né verifica automatica, versione 1.0 senza prove d'uso.
- Cosa prendiamo: protocollo prima della modifica (livello, dipendenze, rischio di cascata, criteri di successo); registro della modifica; punto di ripristino stabile; antischemi (spirale di revisione, deriva della tesi).
- Cosa scartiamo e perché: stati su evidenze e fonti (NR3, NR5) e varianti per tipo di saggio, inutili ai romanzi; integrazioni con altre skill dello stesso repository.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): protocollo prima della modifica (livello, dipendenze, cascata, criterio di successo) e spirale di revisione in critica-manoscritto.md. Licenza a livello di repository non dichiarata: solo idee.

### hypnosdesign/claude-skill-scrittura-italiana
#### Lettura ccr (d2b8814)
Nessuna scheda in questo ramo.
#### Lettura `motore` (971b6df)
- Link: https://github.com/hypnosdesign/claude-skill-scrittura-italiana
- Licenza: CC-BY-SA-4.0 (LICENSE e front matter di SKILL.md); titolare «Hypnos Design» (da README, il testo di LICENSE non riporta un nome); share-alike: copiare testo contagia il motore
- Commit letto: e397599 (12 ottobre 2026)
- Cosa fa: skill editoriale per l'italiano (correzione, line edit, umanizzazione) in tre livelli (proofread, line edit, deep rewrite), con guardia di registro, contratto di conservazione e testo trattato come dato; riferimenti su punteggiatura, voce d'autore, narrativa.
- Qualità: alta e molto curata (changelog, audit, eval, test; 504 righe di SKILL.md e circa 3800 di riferimenti). Rischio: pesante da caricare per intero.
- Cosa prendiamo: tre livelli con «nel dubbio, il livello minimo»; precedenza tipografica; punteggiatura del dialogo (caporali o lineette, una convenzione per libro); licenza vs errore nel parlato; elenco dei tic da prosa generata in italiano.
- Cosa scartiamo e perché: copia testuale (CC-BY-SA); humanizer generico, saggistica e SEO; eval e script Node; la sezione narrativa sull'idea (da manuali di terzi, con esempi di opere reali).
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): tre livelli di intervento e "nel dubbio, il livello minimo", riscritti da zero (CC-BY-SA, niente testo).

### languagetool-org/languagetool
#### Lettura ccr (d2b8814)
Nessuna scheda in questo ramo.
#### Lettura `motore` (971b6df)
- Link: https://github.com/languagetool-org/languagetool
- Licenza: GNU LGPL 2.1 (COPYING.txt); titolari: it/grammar.xml «Copyright (C) 2006 Marcin Miłkowski», file Java del modulo italiano «Daniel Naber» (2012) e contributori; le risorse del modulo it possono avere licenze diverse
- Commit letto: c8d4098 (14 ottobre 2026)
- Cosa fa: correttore grammaticale e stilistico per più di 25 lingue; il modulo italiano ha `grammar.xml` (2199 righe, circa 11 sezioni di regole) più regole Java (ripetizione di parole, speller Morfologik, date).
- Qualità: ottima come software, maturità alta; le regole italiane sono utili ma di copertura media. Java e Maven non eseguiti da chi ha scritto la scheda.
- Cosa prendiamo: come idee, le categorie di errori comuni (a/ha, ai/hai, anno/hanno, apocopi, concordanza, congiuntivo, pleonasmi, regionalismi, forestierismi); regole di stile spente di default; soglia di 40 parole come avviso.
- Cosa scartiamo e perché: codice e XML (LGPL vincola la copia, richiedono Java e Maven); dizionario/speller; integrazione del server (fuori dal motore leggero).
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): LanguageTool 6.8 come livello (b) di zb ortografia, installato fuori dal repository (`zb languagetool installa`; in `motore` era `zb ortografia installa`); codice non incluso (LGPL).

### Mte90/Gulpease e ilmanzo/gedit-plugin-gulpease
#### Lettura ccr (d2b8814)
Nessuna scheda in questo ramo.
#### Lettura `motore` (971b6df)
- Link: https://github.com/Mte90/Gulpease
- Link: https://github.com/ilmanzo/gedit-plugin-gulpease
- Licenza: Mte90/Gulpease GNU GPL 3 (titolare non dichiarato); ilmanzo/gedit-plugin-gulpease Apache-2.0 (titolare non dichiarato)
- Commit letto: Mte90/Gulpease 54bdc7e (28 giugno 2018); gedit-plugin-gulpease d7626f7 (4 gennaio 2017)
- Cosa fa: due strumenti piccoli che calcolano l'indice di leggibilità Gulpease: estensione per browser (Mte90) e plugin per l'editor gedit (ilmanzo).
- Qualità: bassa/media, prototipi. Mte90: parole e frasi contate in modo approssimato, soglie con buco. ilmanzo: formula più vicina all'originale ma conteggio delle lettere e delle frasi impreciso, risultato troncato.
- Cosa prendiamo: solo il fatto che il calcolo è automatizzabile con tre conteggi e la forma normalizzata per 100 parole; formula riscritta da noi (89 + (300 × frasi − 10 × lettere) / parole) e gestione del testo vuoto.
- Cosa scartiamo e perché: tutto il codice (GPL-3 e Apache-2.0; imprecisioni nei conteggi); interfacce browser e GTK obsolete.
- Modifiche fatte nel motore (ramo `motore`, nomi aggiornati all'integrazione): indice Gulpease informativo nel report di capitolo (capitolo.py), formula riscritta; nessun codice preso (GPL-3 e Apache-2.0).
## Confronto con Novel-OS e Book-pipeline (da `motore`, colonna «Nel ramo integrato» aggiunta)

| Aspetto | Loro | Noi (`motore`, 971b6df) | Cosa abbiamo preso | Nel ramo integrato |
|---|---|---|---|---|
| File di stato | N-OS: un solo `story_state.json`; B-P: STATE.yaml e ENTITY_STATE.yaml | `libro.yaml` e `stato.yaml` (fase, gate, sha256) | nessuna sostituzione: confronto con stato.yaml e gate | uguale |
| Avanzamento | N-OS: stato per capitolo, `approve` rifiutato solo se il Guardiano scrive FAIL; B-P: orchestratore con 3 approvazioni umane | fasi del libro e gate che si apre con `zb pronto`; risposta ok/avanti/correggi | niente: il nostro gate resta dell'autore | scrittura automatica: struttura verificata dal motore (gate automatico), una sola fermata, la pausa di lettura ogni 3 capitoli (3-5 in `libro.yaml`) |
| Integrità e recinto | N-OS: nessuna prova di integrità né blocco di scrittura | documenti approvati con sha256; hook sulle scritture | niente (già nostri) | uguale, più cartella unica e separazione dei ruoli in blocco |
| Controllo meccanico del capitolo | B-P: tre script con tetti e codici di uscita; N-OS: `check` e `validate` (LLM) | `zb esito N`: lunghezze, dialogo %, liste nere, date ed età, anti-riciclo a 7 parole | controlli bloccanti già nostri (gate, controllo_fallito) | `zb esito N` con anti-IA (`script/antiia.py`) e Gulpease |
| Fili, promesse, presagi | N-OS: registro con obiettivo e scadenza; B-P: fili aperti nell'audit | nessun registro di avanzamento delle promesse narrative | promesse/indizi/domande con stato ed esenzioni motivate | uguale, più registro delle promesse dalle capsule (`07-capsule/registro.md`) e controllo delle promesse senza chiusura in `struttura.py` |
| Chi sa che cosa | B-P: ENTITY_STATE con fonte per valore e «appreso al capitolo N» | solo date ed età in `zb esito` | registro dei fatti (chi sa che cosa, da quale capitolo) | uguale |
| Rilievi e gravità | N-OS: critico/avviso/informazione con chiave stabile; B-P: Guardiano a tre gravità con citazione | nessun meccanismo di «voluto» registrato nello stato | Guardiano che segnala e non corregge, con citazione; esenzioni motivate | uguale |
| Ristagno | N-OS: «centro che cede», 3 capitoli senza movimento | non presente nella scheda | «centro che cede» in critica-manoscritto.md | uguale |
| Tic e motivi | B-P: tetto di 3 usi per frase-firma, frasi ritirate, auto-ripetizione per punto di vista | liste nere e anti-riciclo a 7 parole | tetto di usi per frase-firma | uguale |
| Valutazione | B-P: gate 8,5/10 su punteggi del modello, sconto 0,5 per giro | giudizio dell'autore | solo l'idea dell'indipendenza dei critici; punteggi scartati | controlli meccanici del motore più lettura dell'autore alla pausa; nessun punteggio |
| Serie e canone | B-P: bibbia di serie, carry_forward, lista di passaggio al libro N+1 | nessun blocco serie nella scheda | serie e canone in continuita-e-serie.md | uguale, più `zb canone` (ccr) |

## Script del motore

### Tabella del ramo `motore` (971b6df, punto 9 di quel lavoro), com'era

Regola dell'autore: restano i controlli meccanici (compila, impagina, pdf, pacchetto, kdp, continuita,
ortografia, esito, stato, avvio); le altre si semplificano o si eliminano, con motivo.

| Script o comando | Decisione | Motivo |
|---|---|---|
| `pulizia.py` (`zb pulizia`) | eliminato | non è un controllo: elenca e cancella file; temporanei e copie li gestiscono git e `.gitignore`, e un comando che cancella è un rischio in più. Prima spostato in `motore/ritirati/` con le sue 6 prove e gli attesi, verificato (6/6 OK dalla cartella nuova, blob identico), copiato sul ramo d'archivio di `motore` (nome del ramo omesso: lo vieta `separazione.py`) e solo dopo tolto |
| `zb conta`, `zb stile`, `zb riciclo`, `zb capitolo` | comandi tolti, moduli tenuti | sono le parti di `zb esito` (capitolo.py): un solo comando per i controlli del capitolo; i moduli restano perché `esito`, `fase` e `verifica_pdf` li usano |
| `revisione.py` (`zb revisione`) | tenuto | mostra i documenti a blocchi: è il meccanismo dei gate (`avanti`) e serve a rileggere un documento approvato fuori dal gate |
| `adotta.py` (`zb adotta`) | tenuto | servirà per i manoscritti già scritti (estrazione della bibbia, `ruoli/riferimenti/continuita-e-serie.md`) |
| `separazione.py`, `recinto.py`, `valida_profili.py` | tenuti | controlli meccanici del motore stesso, lanciati da `zb prove`; restano anche come comandi |
| `nuovo.py`, `fase.py`, `comune.py`, hook, `push.py`, `voce.py`, `kdp_verifica.py`, `prove.py` | tenuti | infrastruttura del percorso (nascita, gate, salvataggio, banca-voci, verifica KDP, prove) |
| nuovi: `ruoli.py`, `cartella_unica.py`, `anti_ia.py`, `installa_languagetool.py`, `agenti.py`, `capsule.py`, `consumo.py` | aggiunti | punti 5, 6, 7, 8, 15 del lavoro: ciascuno è un controllo meccanico o un'infrastruttura richiesta |

### Nel ramo integrato

Nel ramo integrato la base è ccr e le prove di ccr che usano quei comandi restano (D12): dove le due decisioni non
stanno insieme vale ccr, segnato sotto.

| Script o comando | Decisione in `motore` | Motivo in `motore` | Nel ramo integrato |
|---|---|---|---|
| `pulizia.py` (`zb pulizia`) | eliminato | non è un controllo: elenca e cancella file; temporanei e copie li gestiscono git e `.gitignore`; un comando che cancella è un rischio in più (prima spostato in `motore/ritirati/` con le sue 6 prove, copiato sul ramo d'archivio di `motore` (nome del ramo omesso: lo vieta `separazione.py`)) | tenuto, con le sue prove (ccr, `passo 6`: 12 prove) |
| `zb conta`, `zb stile`, `zb riciclo`, `zb capitolo` | comandi tolti, moduli tenuti | sono le parti di `zb esito` (capitolo.py) | comandi tenuti (ccr: le prove li usano); restano anche dentro `zb esito` |
| `revisione.py` (`zb revisione`) | tenuto | mostra i documenti a blocchi; serve a rileggere un documento approvato | tenuto; mostra anche i capitoli della pausa di lettura |
| `adotta.py` (`zb adotta`) | tenuto | servirà per i manoscritti già scritti | tenuto |
| `separazione.py`, `recinto.py`, `valida_profili.py` | tenuti | controlli meccanici del motore stesso, lanciati da `zb prove` | tenuti |
| `nuovo.py`, `fase.py`, `comune.py`, hook, `push.py`, `voce.py`, `kdp_verifica.py`, `prove.py` | tenuti | infrastruttura del percorso | tenuti, più `percorso.py`, `struttura.py`, `salva.py`, `precommit.py` di ccr |
| `ruoli.py` | aggiunto | separazione dei ruoli | unito in `ruolo.py` (comando `zb ruolo`, D8) |
| `cartella_unica.py` | aggiunto | un libro per commit, nessun file del libro fuori dalla sua cartella | tenuto, adattato (D7; comando `zb cartella`) |
| `anti_ia.py` | aggiunto | soglie per profilo, formule, ripetizioni ravvicinate in `zb esito` | unito in `antiia.py` (D10) |
| `installa_languagetool.py` | aggiunto | LanguageTool fuori dal repository | unito in `languagetool.py` (`zb languagetool installa`, D10) |
| `agenti.py` | aggiunto | subagenti e ordine dei lavori | unito con quello di ccr (D9) |
| `capsule.py` | aggiunto | capsule di continuità | unito in `capsula.py` di ccr (D9) |
| `consumo.py` | aggiunto | misura per sessione (hook PostToolUse) | unito con quello di ccr (D9) |

## Traduzione e adattamento (da `motore`)

- Glossario unico: `motore/editoriale/glossario.md` (nel ramo integrato rimanda anche a
  `editoriale/lingue/it/glossario-editoriale.md` del pacchetto).
- Traduzione e adattamento a lotti con modello medio (subagenti): schemi J-P del catalogo anti-IA, tre
  riferimenti dei ruoli; seconda lettura con modello medio dei file chiave nuovi (catalogo esteso,
  riferimenti, modelli della struttura, glossario): 4 errori e 10 calchi corretti. I file scritti
  dall'autore (ruoli, catalogo A-I, criteri del correttore) non sono traduzioni: non riscritti.
- Nel repository solo i file italiani; originali solo come link in `docs/ATTRIBUZIONI.md`.
- File lunghi spezzati: `catalogo-it.md` (A-I) e `catalogo-it-esteso.md` (J-P), `formule.yaml`;
  riferimenti dei ruoli sotto le 80 righe, letti solo quando servono.

## Casi da segnalare all'autore

Da ccr:
- APODICTIC e DDChen666/translate-book: non commerciali (CC BY-NC-SA 4.0). Per usare di più APODICTIC serve una licenza
  commerciale dall'autore del repository (`docs/DA_FORNIRE.md`).
- howells/fiction: licenza non chiara (manca il file LICENSE).
- Book-pipeline, darkautism/ai-novel-translation: nessuna licenza.
- itotm (GPL-3.0), KazKozDev (AGPL-3.0): solo idee, nessun codice.

Da `motore`:
- forsonny/Claude-Code-Novel-Writer, jwynia/agent-skills: licenza non dichiarata a livello di repository, solo idee.
- hypnosdesign/claude-skill-scrittura-italiana: CC-BY-SA-4.0, copiare testo contagerebbe il motore: solo idee.
- languagetool (LGPL 2.1): strumento esterno, mai nel repository.
- mwakidenis/Publish-Books: non accessibile.

Dall'integrazione:
- Apache-2.0 (haowjy, Velith, rohitg00, ilmanzo): i due rami avevano regole diverse; vale «solo idee» (D13).
- kindle-book-agency: le due letture divergono (sopra).

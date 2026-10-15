# Analisi dei repository esterni

Data: 2026-10-15. Ogni repository è stato clonato in sola lettura fuori dal repository (scratchpad della sessione);
nessun file esterno è entrato nel repository. La licenza è quella del file LICENSE letto (o la sua assenza).
Regola: MIT e Apache-2.0 → adattamento in italiano con attribuzione (`docs/ATTRIBUZIONI.md`); CC BY-NC-SA, GPL/AGPL
come codice, licenza assente o non chiara → solo idee generali riscritte da zero, mai testo.

Legenda «letto»: i file aperti davvero. «README» vuol dire che del repository ho letto solo il README.

## Schede

### haowjy/creative-writing-skills — Apache-2.0
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

### Scriven (aihxp/scriven, pacchetto npm `scriven-cli` 2.0.0) — MIT
- Letto: `package/LICENSE`, `package.json`; `templates/WRITING-RULES.md`; `templates/pitfalls/novel.md`;
  `templates/RECORD.md`; `docs/translation.md` (prima parte); elenco di `agents/` e `templates/pitfalls/`.
- Preso: regole dei segni da IA come «pavimento, non soffitto» sotto la guida di stile (coerente con la scala di
  precedenza); pacchetti di insidie per tipo di opera (catalogo, sezione G nella versione inglese; insidie per genere);
  RECORD.md → registro delle promesse generato dalle capsule (`07-capsule/registro.md`, `capsula.py`); traduzione
  unità per unità in contesto pulito, glossario prima, ritraduzione per verificare la fedeltà (`traduci.py ritraduci`).
- Non preso: motori di traduzione esterni (DeepL, Google), profilo della voce su 15 dimensioni (la banca-voci del
  motore ha già la sua scheda in 7 sezioni).

### asadeisa/book-translator — MIT
- Letto: README; `SKILL.md` (flusso completo); `references/review-rubric.md`; `scripts/book.py` (funzione `check_chunk`).
- Preso: glossario per primo con un senso per termine; nel compito del traduttore solo le voci del glossario presenti e
  le ultime righe del blocco precedente; controlli meccanici per blocco (numeri mancanti, frasi in più, rapporto di
  lunghezza, parole non tradotte, termini del glossario); rubrica del revisore di fedeltà in ordine di gravità
  (segmento sbagliato, omissione, significato, aggiunta, identificatori, termini, struttura); note del traduttore vietate.
- Modifiche: `script/traduci.py` (controlla, prepara), `editoriale/lingue/agenti/revisore-fedelta.md`.

### APODICTIC (anotherpanacea-eng) — CC BY-NC-SA 4.0 (non commerciale)
- Letto: solo il file LICENSE (raw). Nessun altro file aperto, come richiesto.
- Preso: nessun testo. Le idee generali già indicate dall'autore (contratto dedotto dal testo, «diagnostica e non
  riscrive», gravità) sono nei file `editoriale/diagnosi/` forniti dall'autore e scritti dalla pratica comune.
- Per usare di più serve una licenza commerciale dall'autore del repository: decisione dell'autore (`docs/DA_FORNIRE.md`).

### knightdx91-alt/Book-pipeline — nessun file LICENSE
- Letto: README; `CLAUDE.md` (sezione «Structural-variety rule» e regole sulla bibbia dei personaggi); elenco di
  `docs/` e `tools/` (contiene `tools/apodictic`: non aperto).
- Preso solo come idea, riscritta: una sola fonte di verità per libro; varietà strutturale (macrostruttura scelta e
  motivata, niente capitoli uguali sui quarti esatti) → `struttura.py` e fase struttura; «budget dei tic» per
  personaggio (proposta per il codex, non implementata).

### epicsagas/Velith — Apache-2.0
- Letto: README (inizio); `skills/loom/quality-bar.md` (rubrica a 5 assi e tassonomia strutturale); elenco degli
  `skills/` (book-edit: fasi fact check → valutazione → developmental → line → copy → proofread → readiness).
- Preso: conferma dell'ordine delle revisioni (coincide con il percorso); i segni strutturali indipendenti dalla lingua
  (paragrafi uguali, chiusura a effetto, triadi, scene simmetriche) già nel catalogo. Non preso: punteggi numerici
  1-10 (rischio di numeri inventati dal modello).

### danjdewhurst/story-skills — MIT
- Letto: README (sezione «The continuity engine»); elenco di `skills/`.
- Preso (riscritto): controlli di continuità deterministici: personaggio morto che compare dopo (codex, «Stato: morto
  nel capitolo N», `codex.py verifica`), promessa pagata prima di essere aperta (`capsula.py`, registro).

### ThomasHoussin/Claude-Book — MIT
- Letto: README; `CLAUDE.md` (orchestratore); elenco di `.claude/agents/`; `.claude/skills/perplexity-improver/SKILL.md`.
- Preso: l'orchestratore non scrive e non giudica, inietta al writer solo le schede dei personaggi pertinenti
  (→ `zb prepara` con il codex filtrato), aggiorna lo stato dopo ogni capitolo (→ capsula e stato compatto).
  Non preso: misura della perplessità con un modello locale (lenta, dipendenze pesanti).

### robskidmore/fiction-skills — MIT
- Letto: README; elenco di `skills/`.
- Preso come conferma: «Story Contract» concordato una volta (coincide con il contratto del libro), nessuna struttura
  presunta, niente scritto senza il sì dell'autore. Nessuna modifica.

### howells/fiction — licenza non chiara (MIT dichiarata in `.claude-plugin/plugin.json`, nessun file LICENSE)
- Letto: README; elenco di `skills/references/`.
- Solo idee: nessuna presa. Caso segnalato all'autore (licenza da chiarire).

### rhavekost/author-toolkit — MIT
- Letto: README; elenco dei file (`story-structure`, `fiction-workshop`, `prose-mechanics`).
- Preso come conferma: stato del progetto letto a inizio sessione e aggiornato a fine (stato compatto). Nessuna modifica.

### felipelobomotta-blip/book-genesis-studio — MIT
- Letto: README (inizio); `skills/book-genesis/references/patterns/ai-tells-pt-br.md` (inizio).
- Preso (riscritto): lineetta del dialogo usata anche negli incisi della narrazione come segno da contare, solo nella
  narrazione (`antiia.py`, `lineette_narrazione`, per l'italiano con le lineette); le soglie sono valori di progetto,
  non norme (lo dichiara anche `dati/antiia.yaml`); molte «spie» compaiono anche nei bestseller umani.

### mrigankad/Novel-OS — MIT
- Letto: README (inizio); `agents/continuity_guardian/prompt.md` (inizio).
- Conferma: il controllo di continuità sulle conoscenze dei personaggi (capsule: «personaggi presenti e cosa sanno»).
  Nessuna modifica.

### ghanemzadeh/claude-skills — MIT
- Letto: README; intestazioni di `line-and-copy-editor/SKILL.md` e `references/ai-prose-patterns.md`.
- Preso: «regola della non invenzione» nel line e copy editing (nessun dettaglio nuovo) → ruolo line editor.

### blader/humanizer — MIT (elenco basato su Wikipedia «Signs of AI writing», CC BY-SA)
- Letto: README; intestazioni di `SKILL.md` e sezione «When not to act».
- Non preso testo: l'elenco deriva da una pagina CC BY-SA (condividi allo stesso modo). Idea presa: quando non
  intervenire (citazioni, nomi, dettagli insoliti che sono voce).

### chi-feng/humanizer — MIT
- Letto: README; `SKILL.md` (principi, modalità audit, «Fixing without adding new tells», processo).
- Preso (riscritto): correggere per sottrazione, rileggere ciò che la correzione introduce, non aggiungere dettagli,
  non omogeneizzare, frequenza «su due assi» (un tic che torna in ogni capitolo conta anche se è uno per capitolo);
  modalità audit non distruttiva. Modifiche: line editor, catalogo it/en.

### itotm/calibre-novel-translator — GPL-3.0
- Letto: README (inizio). Solo idee: riassunto della storia fin lì, glossario dei nomi, nota su come scrive l'autore
  passati al modello capitolo per capitolo → coincide con capsule + glossario + guida. Nessun codice preso.

### darkautism/ai-novel-translation — nessun file LICENSE
- Letto: `Readme.md`. Solo idea (due passaggi: analisi e glossario, poi traduzione): coincide con il gate «guida».

### fredchu/book-translator — MIT
- Letto: README (inizio).
- Preso: osservazione misurata dall'autore del repository: in parallelo senza tabella dei termini i nomi divergono, peggio
  che in sequenza → il motore traduce in sequenza e ammette il parallelo solo con il glossario approvato.

### deusyu/translate-book — MIT
- Letto: README (inizio); `SKILL.md` (glossario, voci per blocco, sottoagenti in parallelo).
- Preso: glossario modificabile a mano e mai sovrascritto; una forma non può stare in due termini (→ «un termine = una
  traduzione» in `traduci.py`); stampa delle sole voci presenti nel blocco.

### ac1982/translate-book — MIT
- Letto: README (inizio). Conferma: l'agente stesso traduce, senza API esterne. Nessuna modifica.

### DDChen666/translate-book — CC BY-NC-SA 4.0
- Letto: README (inizio), LICENSE. Solo idee, nessun testo; caso segnalato (non commerciale).

### KazKozDev/book-translator — AGPL-3.0
- Letto: README (inizio). Solo idee (nomi coerenti, modifiche verificate). Nessun codice.

### VoltAgent/awesome-claude-code-subagents — MIT (solo agenti di scrittura)
- Letto: `categories/04-quality-security/ai-writing-auditor.md` (intero); `categories/08-business-product/content-quality-editor.md` (inizio).
- `content-editor` non esiste in questo repository: c'è in rshah515 (sotto).
- Preso: struttura a livelli del vocabolario (sostituire sempre / in gruppo / per densità), gravità P0/P1/P2, profili per
  tipo di testo → catalogo, `dati/antiia.yaml` (vocabolario inglese L1-L2, con l'avvertenza che non è verificato su Claude).
  Non preso: riscrittura automatica (il motore è in modalità audit).

### rohitg00/awesome-claude-code-toolkit — Apache-2.0
- Letto: ricerca per nome dei file di agenti e comandi di scrittura. Solo agenti per contenuti di marketing e codice:
  nulla per la narrativa. Nessuna modifica.

### rshah515/claude-code-subagents — MIT
- Letto: `marketing/content-production/content-editor.md` (intestazione). Agente per contenuti di marketing (SEO):
  non adatto alla narrativa. Nessuna modifica.

### Trovati da me
- conorbronsdon/avoid-ai-writing — MIT. Letto: LICENSE, CHANGELOG (ricerca). Preso: misurare i falsi positivi su un corpus
  scritto da persone (→ `zb antiia taratura --umano <dir>`). Fonte dell'ai-writing-auditor.
- kindle-book-agency: cercato (ricerca web), non trovato con questo nome: l'idea dell'orchestrazione per dipendenze è
  applicata dalla regola del prompt (capsula N prima del capitolo N+1, gate prima della fase successiva).

## Casi da segnalare all'autore
- APODICTIC e DDChen666/translate-book: non commerciali (CC BY-NC-SA 4.0).
- howells/fiction: licenza non chiara (manca il file LICENSE).
- Book-pipeline, darkautism/ai-novel-translation: nessuna licenza.
- itotm (GPL-3.0), KazKozDev (AGPL-3.0): solo idee, nessun codice.

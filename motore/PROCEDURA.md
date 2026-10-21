# Procedura del motore

Regole di lavoro per qualsiasi libro. Comandi: `python3 motore/zb <comando> <libro> …`
(qui sotto abbreviato in `zb`; l'elenco unico è `zb aiuto`). Percorso e ruoli: `editoriale/00-percorso.md`;
ruoli editoriali: `editoriale/ruoli/`. Il progetto iniziale è in `proposta-motore.md`.

## 1. Regole fisse

1. **Il libro è un percorso** indicato dall'autore (oppure `ZB_LIBRO`): `libri/<slug>/` sul ramo del libro
   (cartella unica, sezione 10). Il motore legge solo `motore/` e la cartella di quel libro, e scrive solo dentro
   quella cartella. `docs/` non si legge nelle sessioni di lavoro.
2. **Precedenza:** una sola scala, quella di `editoriale/LEGGIMI.md` (manuale del libro e
   `libro.yaml` > briefing e scheda della voce > profilo di genere > ruoli editoriali > questa
   procedura). Ogni contrasto si segnala.
3. **Proponi → approvo → applica.** Mai approvare da solo; mai nuovi oggetti o persone in una
   scena senza richiesta.
4. **Ramo:** solo quello assegnato dalla sessione, letto da git. Con `ZB_RAMO` impostato,
   `zb avvio` si ferma se il checkout è su un altro ramo.
5. **Tono:** il testo precedente di un libro è un registro dei fatti, non va commentato né giudicato.
6. **Metodo unico di conteggio** delle parole (vedi `README.md`).
7. **Prima di scrivere in `04-manoscritto/`** si riporta la riga «Letto: …» di `zb avvio`
   (file, righe, sha256, ultimo commit).
8. **Un ruolo per sessione** (`zb avvio <libro> --ruolo R`); chi scrive un testo non lo revisiona
   (`dati/hook.yaml`, `separazione_ruoli`).
9. **La sessione principale non scrive prosa**: chiama l'agente del passo (`zb agenti prossimo <libro>`) e
   legge solo la sua risposta breve (`editoriale/risparmio-token.md`).
10. **Modo automatico** (decisione dell'autore del 2026-10-20): sul percorso editoriale il motore fa i
   controlli e passa da una fase all'altra senza approvazioni intermedie; l'unica fermata prevista è la pausa di
   lettura (sezione 6). `editoriale/00-percorso.md` e i ruoli descrivono ancora le fermate con l'«ok»: il
   contrasto è segnalato in `docs/DA_VERIFICARE_AUTORE.md`.

## 1b. Percorso da casa editrice (libri con `percorso: editoriale`)

Il percorso e i ruoli sono in `editoriale/` (fonte di verità; questa procedura ne descrive la meccanica).
È il percorso predefinito di `zb nuovo`; «Percorso: breve» nel briefing (`percorso: breve` in `libro.yaml`) sceglie
il percorso breve (sezione 5). Un `libro.yaml` senza il campo `percorso` (libri nati prima) resta sul percorso breve.

| Fase in `stato.yaml` | Lavoro (agente) | Gate (solo se elencato in `libro.yaml`) | Controlli di `zb pronto` |
|---|---|---|---|
| `struttura` | architetto-struttura: i nove file di `03-struttura/`; poi diagnosta e editor-strutturale | `struttura`: sempre automatico, nessuna fermata | nove file senza `<!-- zb: modello -->`, nessun campo «- Campo:» vuoto in 01, 02, 03, 09, macrostruttura dichiarata e motivata, schede complete, budget non tutti uguali, almeno una promessa o sottotrama e nessuna senza «Si chiude» in 06; `rapporto-struttura.md` e `piano-revisione-struttura.md` sulla struttura attuale, in commit che non la toccano |
| `documenti` | direttore-editoriale: bibbia, codex, cronologia, manuale, nota di direzione | `documenti` | `zb codex verifica`; presenti libro.yaml, bibbia, cronologia, manuale e `06-diagnostica/nota-direzione.md` |
| `pagina_campione` | scrittore-voce | `pagina_campione` | pagina non vuota |
| `stesura` | scrittore-voce (un capitolo, in sequenza), revisione del diagnosta sul capitolo (`audit/NN.md`), poi capsula | `lettura` (pausa di lettura), `primi_capitoli`, `lotto`; `controllo_fallito` sempre | `zb esito`: capitolo, audit anti-IA, lunghezze quasi uguali, capsula N-1 presente, nessun rapporto di line o copy; con `revisione_capitolo: obbligatoria` anche `audit/NN.md` sul testo attuale con «passa» |
| `struttura_manoscritto` | diagnosta, editor-strutturale | `struttura_manoscritto` | rapporto e piano sul manoscritto attuale |
| `line` | line-editor per capitolo (fino a 3 in parallelo) | `line` | un rapporto per capitolo, intestato e separato |
| `copy` | correttore-italiano per capitolo | `copy` | come sopra |
| `bozze` | `zb compila` e `zb impagina`, poi correttore-bozze | `bozze` | PDF presente, rapporto |
| `chiusura` | motore | — | sezione 7 |

**Struttura automatica.** In fase «struttura» `zb pronto` verifica i nove file e i rapporti (`zb struttura
<libro> verifica` più impronta e commit separato dei rapporti). Se tutto regge registra i nove file e i rapporti
senza fermata, crea bibbia, codex, cronologia e manuale dal briefing (senza sovrascrivere nulla; scaletta e piano
parole restano in `03-struttura/`) e passa a «documenti»; se no si ferma e scrive il motivo. Il gate «struttura»
non ferma mai, anche se `libro.yaml` lo elenca.

**Gate attivi.** I libri nuovi del percorso editoriale nascono con `gate: [lettura]` e `pausa_lettura: 3`. Un
briefing può chiedere altri gate («Gate: …»); i libri già esistenti tengono i loro. Un gate non elencato non
ferma: i documenti si registrano con `senza_gate: true` e si passa oltre. Restano sempre due fermate che non sono
approvazioni del lavoro: `controllo_fallito` (sezione 6) e `canone` (sotto).

**Fasi di revisione in due tempi** (`sottofase`): «proposte» (i rapporti; `zb pronto` li controlla e, se il gate
della fase è in `libro.yaml`, lo apre; altrimenti li registra senza fermata) e «applicazione» (si applicano le
proposte con modifiche puntuali, con il gate solo quelle approvate; `zb esito N` rimisura; `zb pronto` passa alla
fase successiva e registra di nuovo i capitoli cambiati). Ogni rapporto comincia con la riga data da
`zb ruolo <libro> <ruolo> [N]`, che si rifiuta per un ruolo fuori dalla sua fase. Un revisore non riscrive per
intero un capitolo esistente (l'hook rifiuta il Write; si corregge con Edit).

**Capsule, codex, canone, stato compatto.** Dopo ogni capitolo accettato: `zb capsula <libro> N` e l'agente
capsula (`07-capsule/NN.md`, registro delle promesse `@prom:`). `zb prepara <libro> N` dà allo scrittore la
scheda, il codex filtrato per i tag `@char`/`@loc`, il canone e le capsule. Il canone sta in `stato.yaml`
(`fatti_bloccati`) e cambia solo con `zb canone <libro> proponi|togli …` e il gate `canone`. `zb compatto`
scrive `stato-compatto.md` (15-20 righe); `zb salva` lo rigenera.

**Agenti e comandi di Claude Code**: `zb agenti attiva --ok` (solo sui rami dei libri) installa i subagenti e
i comandi `/scrivi-capitolo`, `/revisiona`, `/diagnosi`, `/handover`. Modelli per ruolo: `dati/modelli-ruoli.yaml`
(unica fonte; un «model:» diverso nel file dell'agente è un avviso di `zb agenti stato`, che controlla anche il
formato degli agenti). `zb agenti prossimo <libro>` dice chi chiamare ora: scrittura in sequenza, un capitolo per
volta; line, copy e capsule a gruppi di al massimo `parallelo_massimo` (`dati/modelli-ruoli.yaml`); regole in
`dati/orchestrazione.yaml`.

**Ruoli e sessioni.** `zb avvio <libro> --ruolo R` registra il ruolo della sessione in `<libro>/.zb/ruoli.yaml`
(senza `--ruolo`, quello della fase) e mette il file del ruolo nella riga «Letto». L'hook del recinto e `zb esito`
annotano chi scrive in `<libro>/.zb/scritture.log`. Al «pronto» delle fasi con rapporti e all'avvio di un ruolo di
revisione, chi ha scritto il testo non può aver scritto la revisione (`separazione_ruoli: blocco` in
`dati/hook.yaml`). `zb ruolo <libro> stato` mostra modalità, ruoli delle sessioni e scritture.

**Consumo.** `zb consumo <libro> [sessione] [--sessione S] [--registra]` riassume, per una sessione, capitoli,
parole, file e righe letti e subagenti chiamati, dalle righe che l'hook PostToolUse (Read, Agent, Task) scrive in
`<libro>/.zb/letture.log`; con `--registra` aggiunge il riassunto a `<libro>/.zb/consumo.log`. Restano anche
`zb consumo <libro> registra|mostra|confronto <N>` (confronto con e senza capsule).

**Traduzione**: `zb traduci <libro> --a <lingua> inizia`, poi il libro di traduzione `08-traduzione-<lingua>/`
segue guida → stesura → line → copy → fedelta → chiusura (`editoriale/lingue/traduzione.md`).

**Lingua**: «Lingua: it|en» nel briefing; per l'inglese le stesse fasi e gli stessi ruoli, con i profili di
`editoriale/lingue/en/` (catalogo, criteri, glossario) e Hunspell/LanguageTool in inglese.

## 2. Due modalità

| Modalità | Quando | Differenze |
|---|---|---|
| `nuovo` | libro da zero | nessun testo precedente |
| `riscrittura` | si riscrive un testo esistente | `Testo precedente:` obbligatorio nel briefing (file in `01-originale/`, cartella che esiste solo in riscrittura); finisce in `libro.yaml`; `zb avvio` lo elenca tra i file letti; `riciclo.py` dà KO su ogni sequenza di 7 parole uguale |

## 3. Nascita del libro: `zb nuovo <briefing>`

1. L'autore compila `motore/modelli/briefing.md` (una voce per riga) e lo mette nella cartella
   del futuro libro.
2. `zb nuovo <percorso-briefing>`:
   - se il briefing è incompleto elenca cosa manca (al massimo 5 voci) e **non crea nulla**;
   - se c'è già un `libro.yaml` si ferma;
   - si ferma anche se la cartella è dentro `motore/`, è la radice del repository o il ramo è «motore»: il
     libro nasce solo in `libri/<slug>/`, e diventa il libro attivo;
   - altrimenti sposta il briefing in `00-progetto/briefing.md` e crea solo dentro la cartella
     `libro.yaml`, `stato.yaml`, `LEGGIMI.md`, `nomi_propri.txt`, `.gitignore`, più:
     - percorso editoriale (predefinito): i nove file di `03-struttura/` (modelli di
       `editoriale/struttura/modelli/`), fase «struttura». Nessun documento prima della struttura: bibbia, codex,
       cronologia e manuale nascono quando il motore chiude la struttura (sezione 1b);
     - percorso breve: `cronologia.yaml`, bibbia, manuale di stile, scaletta e piano parole, fase «documenti».
3. Le regole della sezione «Direttive» del briefing (genere, lunghezza, voce, tetti, vietati,
   vincoli, gate) vanno in `libro.yaml` e nel manuale **senza riscriverle a mano**.

**Valori fuori dal profilo di genere (override motivati).** La lunghezza, i capitoli («Capitoli:
minimo | media | massimo») e, se indicati, «Frase media: a-b» e «Dialogo: a-b» devono stare nei
valori del profilo. Un valore diverso è accettato solo con «Motivo override:» non vuoto nel
briefing; allora va in `libro.yaml` come override con il motivo, il manuale lo elenca (sezione
«Override»; con il gate «documenti» attivo la approva l'autore) e il numero di capitoli si calcola con i valori nuovi.
Senza motivo `zb nuovo` elenca i campi e si ferma. Con una lunghezza fuori dai formati del profilo
serve anche «Capitoli:». Sotto 1.000 parole il motore si ferma comunque.
Esempio neutro: `Lunghezza: 9000`, `Motivo override: racconto lungo`, `Capitoli: 800 | 1000-1300 | 1800`
→ 8 capitoli; l'obiettivo resta in `parole.target_totale` con il motivo in `parole.motivo_fuori_profilo` (il profilo non si tocca), override su `capitoli.minimo/media/massimo`.

**Scene.** `capitolo.py` conta le scene di ogni capitolo numerato dal separatore di `libro.yaml`
(`struttura.separatore_scena.sorgente`): numero fuori da `capitoli.scene_per_capitolo` = KO; scena
sotto il minimo di `scene.lunghezza` = KO, sopra il massimo = avviso; il sequel è informativo. Si
cambiano con «Scene: numero | lunghezza» nel briefing, con le stesse regole di «Capitoli:» (serve
«Motivo override:»); «Scene:» è obbligatoria quando le scene del profilo non stanno in un capitolo
medio. Esempio neutro: profilo con 2-3 scene da 800-2500 parole, `Capitoli: 800 | 1000-1300 | 1800`
→ serve `Scene: 1 | 400-1200` (override su `capitoli.scene_per_capitolo` e `scene.lunghezza`).

**Continuità: età e durate.** `continuita.py` prende come età attuale solo le forme dichiarative
(«Nome ha N anni», «Nome, di N anni», «trentenne»): KO se non torna con la data di nascita. «Nome aveva N
anni» nella principale (imperfetto narrativo) e le attribuzioni incerte danno un avviso; i ricordi
(«quando aveva N anni», «a N anni», «da N anni») sono ignorati. Le durate della cronologia si
confrontano in giorni con l'unità vera (giorni, settimane, mesi, anni); la tolleranza si scrive come
`tolleranza_giorni`, `tolleranza_mesi` o `tolleranza_anni`. Esempio neutro: «sei settimane» tra due date a
41 giorni con `tolleranza_giorni: 3` → nessun KO.

**Campi del profilo: controllati e informativi.** Lo schema `dati/profilo.schema.yaml` dichiara per
ogni campo il suo uso; `zb profili` li elenca.
- Controllati da uno script: `capitoli.minimo`, `capitoli.scene_per_capitolo`, `capitoli.tolleranza_budget`,
  `capitoli.tolleranza_totale`, `scene.lunghezza`, `frase_media`, `dialogo_percento`,
  `similitudini_max_per_parole`, `parole_filtro`.
- Usati da `zb nuovo` per generare i documenti: `genere`, `lunghezza_totale.formati`, `capitoli.media`,
  `capitoli.massimo`, `chiusura_preferita`, `scene_obbligatorie`.
- Informativi, non controllati (marcati così anche nei profili): `lunghezza_totale.consigliata`,
  `lunghezza_totale.parti_sopra`, `lunghezza_totale.parti_obbligatorie`, `capitoli.coerenza`,
  `scene.sequel`, `scene.budget_interno`, `parole_per_atto`, `battiti`, `lista_nera` (la lista nera
  usata è sempre `dati/lista-nera.yaml`), `parole_per_pagina`.

## 3b. Libro già avviato: `zb adotta <cartella>`

Per un libro che ha già alcuni documenti (briefing, manuale di stile, bibbia, scaletta, piano
parole, cronologia) ma non ancora `libro.yaml`.

- Genera in **bozza** `libro.yaml`, `stato.yaml`, `cronologia.yaml`, `nomi_propri.txt` e
  `06-diagnostica/adozione.md`. Ogni valore ha la sua fonte (file:riga) in `adozione.md`.
- Se il manuale diverge dal profilo di genere, il valore entra come `override` con il motivo.
- Non sovrascrive mai un file esistente; scrive solo nella cartella indicata.
- Elenca in `adozione.md` ciò che non ha potuto ricavare (da completare a mano).
- Se il titolo non si ricava dai documenti si ferma senza scrivere nulla e lo chiede:
  `zb adotta <cartella> --titolo "<titolo>"`.
- Media e massimo dei capitoli si leggono solo dalla riga «Capitolo:» del manuale: «frase media 10-13»
  o «al massimo 150 parole» scritti altrove non diventano valori dei capitoli.
- Si ferma alla fase «documenti»: apre il gate se ci sono tutti i documenti, altrimenti li elenca.

Righe riconosciute (formato dei documenti del motore): `Titolo di lavoro:`, `Autore:`,
`Genere:`, `Lunghezza:`, `Modalità:` nel briefing; nel manuale `# Manuale di stile — <titolo>`,
`Genere:`, `Obiettivo: N parole`, `Capitolo: minimo …, media a-b, massimo … parole`,
`Frase media: a-b`, `Dialogo: a-b%`, `una ogni N parole`, `Tetto: «…» al massimo N per capitolo|libro`,
`Vietato: «…»`, `«Nome» non compare nei capitoli 1-3`, `Separatore di scena: «…»`,
`Intestazione del capitolo: «…»`; nella bibbia `**Nome**` e `nato/nata il AAAA-MM-GG`; nella
scaletta le righe `| N | AAAA-MM-GG | contenuto |`; `01-originale/` presente = riscrittura.

Esempio neutro: una cartella con bibbia, manuale (con «Frase media: 8-12» e genere
narrativa-letteraria) e scaletta, senza briefing né piano parole. `zb adotta` ricava titolo,
profilo, obiettivo, tetti, vincoli, date e nomi; scrive un override `frase_media [8, 12]` con la
riga del manuale come motivo; segnala «autore» e il piano parole come mancanti; resta in fase
«documenti» senza gate aperto finché il piano parole non c'è.

## 4. Avvio: `zb avvio <libro>`

Obbligatorio all'inizio di ogni sessione e dopo ogni compattazione del contesto.

Si ferma (codice 2) **senza scrivere nulla da nessuna parte** se:
- nel percorso non c'è un libro (se c'è solo un briefing, elenca cosa manca);
- la cartella non è scrivibile, non è in un repository git, o `git push --dry-run` fallisce
  (riporta l'errore esatto);
- il ramo non è quello della sessione; ci sono modifiche non salvate; il ramo è avanti o
  indietro rispetto a origin;
- `stato.yaml` manca o non è valido, o `push_in_sospeso` è vero;
- in fase «documenti» il briefing è incompleto (non per un libro in riscrittura senza briefing nel
  formato del motore, cioè senza «Titolo di lavoro:»: un libro adottato parte dai suoi documenti);
- un documento approvato è cambiato fuori procedura (sha256 diverso da quello registrato).
  Se la modifica è autorizzata dall'autore: commit, poi `zb riapprova <libro> <documento> <motivo>`
  (nuovo sha256 e commit; in `stato.yaml` restano data, motivo e sha256 precedente);
- file modificati fuori da `libri/<slug>/` (anche da Bash), un altro libro attivo (un solo libro per sessione;
  per cambiare `zb lavoro libro <slug>` e nuovo avvio), o la cartella unica violata (sezione 10);
- la sessione ha già un altro ruolo, o chiede un ruolo di revisione dopo aver scritto il testo (con
  `separazione_ruoli: blocco`);
- percorso editoriale, fase «stesura»: mancano capsule dei capitoli scritti e `libro.yaml` ha
  `capsule: obbligatorie` (senza il campo, o con `avviso`, è un avviso).

Se tutto va bene stampa:
`Letto: <file> (N righe, sha256 …, commit …), …; libro @ <commit>; motore @ <commit>; fase, gate`,
poi passo, capitoli, parole, revisione in corso, correzioni e avvisi aperti, e scrive solo il
marker `<libro>/.zb/letto-<session_id>` e il ruolo in `<libro>/.zb/ruoli.yaml` (la cartella `.zb/` ignora sé
stessa in git). Sul percorso editoriale la riga «Letto» ha lo stato compatto e i file della fase (in stesura
`09-scelte-fisse.md` e il registro delle capsule, non il capitolo precedente) e il file del ruolo.

Avvisi: commit del ramo che cambiano file fuori dai libri rispetto a origin/motore; altri libri sullo stesso
ramo; percorso editoriale: report di sessione non aggiornato da più di 10 salvataggi.
`zb avvio` senza libro (solo con «lavoro sul motore»): controlli del ramo del motore (nessun `libri/`, nessun
`.claude/`, controllo pre-commit) e riga «Letto» con CLAUDE.md, PROCEDURA, passaggio di consegne e livello editoriale.

## 5. Fasi e gate

Questa tabella è il percorso breve; il percorso editoriale è nella sezione 1b. Il meccanismo dei gate (blocchi,
`ok`, `avanti`, `correggi`) è lo stesso per i gate chiesti nel briefing, per `canone` e per `controllo_fallito`.

| Fase | Lavoro | Gate (se attivo) | Documenti mostrati |
|---|---|---|---|
| documenti | completare bibbia, cronologia, scaletta, piano parole | `documenti` | libro.yaml, bibbia, cronologia, manuale, scaletta, piano parole |
| pagina_campione | scrivere `05-revisioni/pagina-campione.md` (creata vuota all'ingresso nella fase; `pronto` la rifiuta finché è vuota) | `pagina_campione` | pagina campione |
| stesura | capitoli, uno dopo l'altro | `primi_capitoli` dopo il capitolo 3; `lotto` a ogni lotto (se attivo); `controllo_fallito` sempre | capitoli e report |
| chiusura | continuità, ortografia, manoscritto completo, PDF, pacchetto, controllo KDP | — | — |
| chiuso | — | — | — |

**Gate attivi:** campo `gate` di `libro.yaml` (dal briefing, «Gate:»). Predefiniti del percorso breve (e di un
`libro.yaml` senza il campo): `documenti, pagina_campione, primi_capitoli`. Possibili: anche `lotto` e `lettura`.
Percorso editoriale: `lettura` (sezione 1b). Un gate non attivo non ferma: i documenti si registrano con
`senza_gate: true` e si passa oltre. `controllo_fallito` è sempre attivo.

**Risposte dell'autore**

| Risposta | Comando | Effetto |
|---|---|---|
| `ok` | `zb ok <libro>` | Approva il gate aperto: registra sha256 e commit dei documenti, chiude il gate, passa oltre. Rifiutato se i blocchi non sono stati mostrati tutti, se i documenti sono cambiati dall'ultima lettura, se hanno modifiche non salvate, o se una correzione registrata non è stata applicata. Alla pausa di lettura non servono blocchi: registra i capitoli come letti e la scrittura riparte. |
| `ok, lotti da N` | `zb ok <libro> lotti da N` | Come `ok`, e fissa la dimensione dei lotti successivi. |
| `avanti` | `zb avanti <libro>` | Blocco successivo (circa 120 righe, tagliato a fine paragrafo). Non approva nulla. Se i documenti cambiano, riparte dal blocco 1. |
| `correggi: …` | `zb correggi <libro> <istruzione>` | Registra la correzione; il gate resta aperto. Applico solo quella, rieseguo i controlli, mostro le righe cambiate (prima e dopo), salvo; poi `avanti` riparte dal blocco 1. Alla pausa di lettura invece le note vanno in `06-diagnostica/note-lettura.md` e in `stato.yaml` (`note_lettura`) e la scrittura riparte. |
| correzione fuori dal gate | `zb correggi <libro> <unità>: <motivo>` (con `--commit <hash>` per una correzione già salvata) | Registra data, file, motivo, sha256 precedente e corretto in `stato.yaml` (`correzioni_registrate`); non apre e non chiude gate. Segue i file rinominati (sha256 precedente sotto il nome vecchio). |
| ritorno alla stesura | `zb fase <libro> stesura --motivo "<testo>"` | Solo da «chiusura» e solo se nel piano parole mancano unità: registra data, fase precedente, motivo e unità mancanti (`cambi_fase`). La fase passa a «chiusura» da sola soltanto quando tutte le unità del piano (prologo, capitoli, interludi, epilogo) sono scritte e accettate. |
| `riapprova` | `zb riapprova <libro> <documento> <motivo>` | Modifica autorizzata a un documento già approvato (già salvata in un commit): registra il nuovo sha256 e commit, con data, motivo e sha256 precedente. Rifiutato se il documento non è approvato, non è cambiato o ha modifiche non salvate. |
| `stato` | `zb stato <libro>` | Fase, gate, lotto, capitoli, parole, revisione, correzioni, avvisi, ultimo commit, allineamento con origin. Non scrive nulla. |

Qualunque altra frase è una domanda: rispondo senza cambiare stato.

**Comandi di Claude Code** (non dell'autore): `zb pronto <libro>` quando il lavoro di una fase
è finito (apre il gate e mostra il blocco 1, oppure passa oltre); `zb esito <libro> N` dopo
aver scritto il capitolo N.

## 6. Stesura di un capitolo

Procedura uguale per ogni capitolo, senza fermate tranne i gate:

1. Rileggo `LEGGIMI.md`, il manuale di stile, le direttive del briefing, la riga del capitolo in
   scaletta e piano parole, le voci di cronologia che tocca e il capitolo precedente. Sul percorso editoriale
   scrive l'agente `scrittore-voce`, chiamato dalla sessione principale (mai due capitoli in parallelo);
   `zb prepara <libro> N` gli dà la scheda del capitolo, il codex filtrato, il canone, le capsule e, dopo una
   pausa di lettura con note, `06-diagnostica/note-lettura.md` (la scheda e le parole previste sostituiscono
   `05-scaletta.md` e `08-piano-parole.md` interi, che l'agente non rilegge); con una voce della banca indica anche le sezioni
   2, 3 e 6 della scheda della voce e i divieti, da leggere prima di scrivere. Gli esempi «versione debole →
   versione forte» si nominano solo se la sezione 6 li ha (righe «Debole: …» e «Forte: …»); se la scheda o
   `ZB_BANCA_VOCI` mancano, `zb prepara` si ferma con il motivo.
2. Riporto la riga «Letto: …» di `zb avvio` (se non l'ho già fatto in questa sessione).
3. Scrivo `04-manoscritto/NN-<slug>.md` con la riga nascosta `<!-- zb: chiusura=X -->`.
3b. Revisione del capitolo (percorso editoriale). Prima le misure del motore: la sessione principale lancia
   `zb ruolo <libro> diagnosta N` (in fase «stesura» solo con N), che esegue i controlli di `capitolo.py` e l'audit
   anti-IA senza scrivere il report. Con un KO, o un avviso di frase media, dei divieti della voce o delle ripetizioni
   ravvicinate, si ferma (codice 2): il diagnosta non si chiama e chi scrive fa una correzione mirata. Con le misure
   superate scrive `06-diagnostica/misure/NN.md` (prima riga con l'impronta del capitolo; misure, righe misurate con
   gli avvisi restanti, elenco «File da leggere» e canone) e `06-diagnostica/frasi-finali/NN.md`, e stampa la prima
   riga del rapporto. L'agente `diagnosta` installato non ha la shell (sola lettura): la sessione principale gli passa
   la riga e il file delle misure. Il diagnosta, in una sessione separata da chi ha scritto, legge solo i file
   elencati lì e scrive `06-diagnostica/audit/NN.md` con la checklist del capitolo singolo
   (`editoriale/ruoli/00-diagnosta.md`), la sezione `## Da correggere` (riga, frase, motivo) e l'ultima riga «passa» o
   «non passa». Un solo giro completo: dopo un «non passa» e la correzione, `zb ruolo` prepara il secondo giro con le
   sole frasi del primo (che resta in `audit/NN-giro1.md`); dopo il secondo «non passa» si ferma e decide l'autore
   (`--nuovo-giro`, dopo il suo «ok», riparte da un giro completo). Con `revisione_capitolo: obbligatoria` in
   `libro.yaml`, `zb esito` si ferma se il rapporto manca, è scritto su un'altra versione del capitolo (impronta della
   prima riga), chiude con «non passa» o mancano le misure del motore sul testo attuale; senza il campo la revisione
   resta consigliata e `zb esito` non la legge.
4. `zb esito <libro> N`: esegue `capitolo.py` (report in `06-diagnostica/capitoli/NN.md`, con le righe
   `anti-ia:<misura>` e l'indice Gulpease informativo; audit in `06-diagnostica/anti-ia/NN.md`) e
   aggiorna `stato.yaml` (ultimo capitolo scritto, parole, lotto). `zb stile <libro> [N]` scrive anche
   `06-diagnostica/frasi-finali/NN.md`: la frase finale di ogni paragrafo di narrazione e dell'ultima battuta di
   ogni scambio, con il numero di riga; non dà esiti, è l'elenco da cui chi rivede giudica le chiuse frase per frase.
   Frase media: con `frase_media_voce: true` nel profilo (thriller) e una voce in `libro.yaml`, l'intervallo del
   capitolo è quello del suo registro nella riga «frase media» della tabella della sezione 3 della scheda della
   voce; il registro si dichiara nella scheda del capitolo in scaletta («registro corto», «registro freddo»…; se
   ce ne sono più d'uno vale il primo, il dominante); senza registro dichiarato vale «base». Un override di
   `frase_media` in `libro.yaml` resta sopra. Il motore misura il capitolo intero: registri diversi per scena
   non si dichiarano e non si misurano separatamente. L'intervallo del registro è una scelta della voce, non
   ancora calibrata sui testi dell'autore: fuori intervallo il capitolo ha un AVVISO («intervallo non calibrato
   sull'autore»), non un KO; diventerà un blocco solo dopo la calibrazione. L'intervallo del profilo o
   dell'override resta un KO.
5. Percorso editoriale: `zb capsula <libro> N` prepara `07-capsule/NN.md`, l'agente `capsula` la compila (otto
   sezioni, 120-250 parole), `zb capsula <libro> N --verifica` la controlla e riscrive il registro.
6. Blocco di salvataggio (sezione 8).

**Anti-IA (audit).** `script/antiia.py` (anche `zb antiia <libro> [N]`) misura senza toccare il testo:
variazione delle frasi, aperture uguali, formule per mille parole, lineette nella narrazione, varietà lessicale,
chiusure uguali di fila (P0 oltre `chiusure_uguali_max`); in più, P2, le formule di
`editoriale/anti-ia/formule.yaml` (`formule_catalogo_per_mille`; la sezione B solo con
`formule_sezione_b: true`), i segni tipografici all'inglese e le ripetizioni ravvicinate (solo italiano). Soglie:
`dati/antiia.yaml`, poi la lingua, poi il blocco `anti_ia` del profilo di genere, poi `anti_ia` di `libro.yaml`.
Sono avvisi; con `anti_ia: {modalita: blocco}` ogni segnalazione è un KO in `capitolo.py`.

**Titoli interni al capitolo.** Il capitolo comincia con il suo titolo («# N — Titolo»), che `zb compila`
riscrive («N. Titolo») e porta nel sommario. Dentro il capitolo sono ammessi titoli di secondo livello
(«## …», per esempio una pagina di enigma): il motore li conserva nel manoscritto compilato, un livello sotto
il titolo del capitolo («### …»). Si scartano solo il titolo del capitolo e i commenti `<!-- zb: … -->`.

**Checklist di capitolo.** Il report di `capitolo.py` chiude con una checklist manuale per l'autore:
i tic fissi del motore, le voci di cronologia che il capitolo tocca e le voci proprie del libro scritte in
`libro.yaml` come `checklist_capitolo` (esempio neutro: `checklist_capitolo: ["Il diario non si apre prima del capitolo 5"]`).

**Correzione unica.** Se i controlli danno KO: **una sola** correzione mirata, poi di nuovo
`zb esito`. Al secondo KO di fila sullo stesso capitolo si apre il gate `controllo_fallito`: mi
fermo e scrivo quale controllo, valore, soglia, file e righe. L'autore decide: `ok` accetta il
capitolo così com'è, `correggi: …` indica la correzione.

**Correzione a un gate di capitoli.** Con il gate `primi_capitoli` o `lotto` aperto e una correzione
registrata (`correggi: …`), `zb esito <libro> N` su un capitolo del gate rifà i controlli e aggiorna le
parole in `stato.yaml`; il gate resta aperto e `avanti` riparte dal blocco 1.

**Totale del libro.** `zb conta` e `zb capitolo` confrontano il totale previsto (parole scritte più i
budget delle unità non ancora scritte) con `parole.target_totale`. Fuori da `capitoli.tolleranza_totale`
danno un AVVISO con il budget residuo proposto per le unità rimanenti (in proporzione ai loro budget).
È una proposta: il motore non accorcia né allunga un capitolo per far sparire l'avviso, e non tiene
i capitoli sotto una soglia; a libro finito, fuori tolleranza, decide l'autore.

**Pausa di lettura** (gate `lettura`, percorso editoriale). Dopo `pausa_lettura` capitoli accettati da
`zb esito` (`libro.yaml`: 3, 4 o 5, predefinito 3; un altro valore ferma ogni comando) e a fine stesura il motore
si ferma, stampa «PAUSA DI LETTURA» con l'elenco dei file da leggere e non accetta altri `zb esito`. L'autore
risponde `ok` (continua) oppure `correggi <note>` (le note valgono per il blocco successivo: `zb prepara` mette
`06-diagnostica/note-lettura.md` tra i file che lo scrittore legge; un capitolo già
scritto si corregge con `zb correggi <libro> <unità>: <motivo>`).

**Lotti** (percorso breve, o gate chiesti nel briefing). Dopo il capitolo 3 si apre `primi_capitoli`; con
l'«ok» l'autore sceglie i lotti (`ok, lotti da N`). Poi i capitoli si scrivono in lotti di N **senza fermate**
(salvo gate `lotto` attivo o controllo fallito due volte). Scritte e accettate tutte le unità del piano parole,
la fase passa a «chiusura» (percorso editoriale: a «struttura_manoscritto»).

## 7. Chiusura

In ordine: `zb continuita`, `zb ortografia`,
`zb compila`, `zb impagina`, `zb pdf`, `zb pacchetto`, `zb kdp`; poi `zb pronto <libro>`, che
controlla che ci siano tutti i report e chiude il libro. `zb pacchetto` va prima di `zb kdp`: il
controllo KDP legge la scheda del pacchetto (senza, dà KO anche sulle sezioni che la scheda copre).
Il formato della pagina si conferma in `libro.yaml` con `formato.formato_confermato_kdp` (facoltativo,
predefinito false): con false la sezione 11 del controllo KDP dà un AVVISO, con true è OK.

**Continuità: durate e cifre.** Le durate di `cronologia.yaml` si confrontano con le date degli eventi
anche quando nessun capitolo le nomina (unità «cronologia» nel report). Una cifra (`cifre`) con
`contesto: [parole]` si controlla solo nelle righe che contengono una di quelle parole (KO se il
numero è diverso); senza `contesto`, un numero diverso vicino all'unità è un AVVISO da verificare,
perché la frase può parlare d'altro («tre settimane di lavoro»).

**Limiti noti.**
- Similitudini (`stile.py`): si contano solo «come» seguito da un articolo o da «se», «sembrava» e
  «pareva»; «come l'» seguito da un verbo («a come l'aveva lasciata») non si conta. Forme come
  «come si fa con…», «come quando…» non si contano: sono spesso «in che modo» e il motore non le
  distingue. Effetto sul report: il numero di candidati e l'AVVISO «similitudini» possono stare
  sotto il vero; il controllo resta alla lettura dell'autore.

**Ortografia (`zb ortografia <libro>`), tre livelli.**
- (a) Hunspell it_IT, sempre. Parole ammesse: quelle del libro (`nomi_propri.txt`) e quelle generiche
  del motore (`dati/parole-ammesse-it.txt`: forme italiane valide che il dizionario non conosce, mai
  nomi di personaggi o luoghi). Le elisioni (l', dell', anch') non si controllano.
- (b) LanguageTool, solo se `ZB_LANGUAGETOOL` indica la cartella dei suoi `.jar`, mai nel repository e mai
  scaricati da languagetool.org. Installazione e verifica: `zb languagetool installa` (stampa la riga
  `export ZB_LANGUAGETOOL=…`), `zb languagetool verifica`, `zb languagetool stato` (README, «LanguageTool»).
  Se Maven Central risponde 403 o 429, non insistere: si resta con Hunspell e la lista di controllo.
- (c) Lista di controllo per la lettura umana, sempre, in fondo al report: per l'italiano le voci delle sezioni
  1-6 di `editoriale/correttore/criteri-correttore.md` (fonte unica). I correttori automatici non rilevano «e»
  per «è», gli accordi sbagliati, le parole vere usate al posto di altre.
- Il report (`06-diagnostica/controllo-ortografico.md`) dice quali livelli sono stati eseguiti.

**Appendici.** Materiali che stanno dopo l'ultima unità del libro (epilogo compreso): soluzioni di enigmi,
mappe, glossari, note. Stanno nella cartella `05-appendici/` del libro e si dichiarano in `libro.yaml`, in
ordine di lettura:

```yaml
appendici:
  - {titolo: "Le soluzioni", file: soluzioni.md}
  - {titolo: "La mappa", file: mappa.svg, didascalia: "Riga sotto l'immagine."}
```

- `titolo`: titolo della pagina e voce del sommario; `file`: nome in `05-appendici/`; `didascalia`: solo per
  le immagini, facoltativa.
- Formati: testo `.md` (il suo primo titolo si scarta, gli altri titoli restano un livello sotto); immagini
  `.svg`, `.png`, `.jpg`. Un `.svg` si converte in PNG con Chromium (`stampa/svg_png.js`, scala 2) in
  `05-output/appendici/`; `.png` e `.jpg` si copiano lì. Ogni appendice comincia su una pagina nuova.
- Un libro senza il campo si compila come prima. Un file di `05-appendici/` non dichiarato dà un AVVISO e non
  entra nel libro; un file dichiarato e assente ferma `zb compila`. Le appendici non vanno mai in
  `04-manoscritto/`, che accetta solo le unità (prologo, capitoli, interludi, epilogo).
- Un'appendice non anticipa nulla: le soluzioni stanno solo in appendice, mai nel testo prima della pagina
  dell'enigma, e una mappa in appendice non mostra la soluzione di un enigma (per esempio un punto da trovare).

**Indice e sommario.** Il sommario lo genera `zb compila`, sempre, e non si scrive a mano: contiene, in ordine,
le parti (se `struttura.parti` le dichiara), il prologo, i capitoli («N. Titolo»), gli interludi, l'epilogo e
le appendici dichiarate. `zb impagina` mette accanto a ogni voce la pagina reale e `zb pdf` controlla che
ogni voce corrisponda alla pagina su cui l'unità comincia. Per cambiare una voce si cambia la sua fonte
(intestazione del capitolo, `struttura` o `appendici` in `libro.yaml`), poi si rilancia `zb compila`.

## 8. Blocco di salvataggio

Dopo ogni passo che scrive: report in `<libro>/06-diagnostica/`, poi `zb salva <libro> "<messaggio>"`
(controllo su git di tutti i file modificati: rifiuta se uno sta fuori dal recinto; rigenera lo stato compatto;
sul motore lancia prima `zb prove`; poi commit e push con ripiego), `git status -sb`, `git log -1`. Se il push fallisce o un file non si salva: fermarsi e riportare
l'errore esatto; mai dire «fatto» se non è su origin; niente altri rami, tag o push forzati.
Resoconto: hash, file, parole o pagine, «branch allineato a origin: sì/no».
Nessun comando del motore fa commit o push da solo, tranne `zb salva` e `zb push` quando li si lancia.
`zb push`, prima del push: sul ramo di un libro controlla la cartella unica; sul lavoro del motore vuole
l'impronta di una `zb prove` intera e tutta OK sullo stato attuale di `motore/` (`<git-dir>/zb-prove-ok`; con
`--solo` o `--sezione` l'impronta non si scrive). Se il controllo fallisce non fa niente ed esce con 2.

## 9. Ripresa dopo un'interruzione

Solo da file: `zb avvio <libro>`. Se si ferma per modifiche non salvate, mostro quali file e
chiedo «tieni» o «scarta» (non scarto nulla da solo). Se c'era una revisione in corso, `avanti`
riprende dal blocco registrato (o dal blocco 1 se i documenti sono cambiati).

## 10. Recinto e hook

**Cartella unica.** Tutto ciò che riguarda un libro vive solo in `libri/<slug>/`, sul ramo del libro; il libro
attivo sta in `<git-dir>/zb-libro-attivo`, fuori dai file tracciati (`libri/libro-attivo.md` dei rami creati
prima si legge ancora). `zb cartella <libro> [--commit]`, e da soli `zb avvio`, `zb push` e l'hook del recinto
prima di `git commit`/`git push`, controllano su git: file modificati fuori dal libro, commit «misti» che
toccano il libro e file fuori da `libri/`, titolo o percorso del libro in file fuori da `libri/` scritti sul
ramo. Esclusi, in `dati/cartella-unica.yaml`: i file ammessi fuori (`CLAUDE.md`, `.gitignore`,
`libri/libro-attivo.md`, `.claude/settings.json`, `.claude/agents/`, `.claude/commands/`), i merge del motore e
i commit misti già fatti che l'autore dichiara con il motivo (`commit_dichiarati`: la storia non si riscrive).

**Recinto (blocco).** `script/hook_recinto.py` (PreToolUse su Write, Edit, MultiEdit, NotebookEdit e Bash):
con un libro attivo consente solo `libri/<slug>/`; con «lavoro sul motore»
(`zb lavoro motore`) consente il repository tranne `libri/`. Per Bash controlla i percorsi che il comando
probabilmente scrive (stessa euristica dell'hook del manoscritto: redirezioni, tee, sed -i, cp, mv, rm, touch,
mkdir…), solo dentro il repository. Limiti residui (falsi permessi): script che scrivono senza nominare il
percorso, variabili o `cd` di comandi precedenti, sostituzioni di comando, strumenti non elencati.
Li coprono:
- il **controllo pre-commit di git** (`script/precommit.py`, installato da `zb lavoro motore|libro`): rifiuta
  un commit con file fuori dal recinto, qualunque strumento li abbia scritti (eccezione dichiarata: merge del
  motore, MERGE_HEAD raggiungibile da origin/motore);
- **`zb avvio`**: si ferma con file modificati fuori dal libro e avvisa se i commit del ramo cambiano file
  fuori dai libri rispetto a origin/motore (pre-commit aggirato con `--no-verify`);
- **`zb salva`**: stesso controllo prima del commit.
Sul ramo `motore` hook, agenti e comandi restano spenti (nessun `.claude/`); `zb avvio` senza libro lo verifica.

**Hook del manoscritto e della sessione (avviso).**

- `script/hook_sessione.py` (SessionStart): scrive il `session_id` in
  `$CLAUDE_PROJECT_DIR/.zb/sessione-corrente`; dopo una compattazione registra l'ora, e i marker
  di avvio precedenti non valgono più.
- `script/hook_manoscritto.py` (PreToolUse): se una scrittura va in `<x>/04-manoscritto/` di un
  libro senza il marker di avvio della sessione, in modalità **avviso** stampa «ATTENZIONE: …»,
  lo annota in `<x>/.zb/avvisi-hook.log` e **lascia passare**; in modalità **blocco** ferma lo
  strumento (codice 2).
- `script/hook_recinto.py`, oltre al recinto: rifiuta il Write di un revisore su un capitolo già esistente e
  annota chi scrive in `<libro>/.zb/scritture.log` (separazione dei ruoli).
- `script/consumo.py` (PostToolUse su Read, Agent, Task): letture e subagenti in `<libro>/.zb/letture.log`,
  per `zb consumo`. Non blocca mai.
- Modalità in `dati/hook.yaml`: `modalita` dell'hook del manoscritto (oggi: `avviso`; il passaggio a `blocco` è
  un commit a parte, dopo l'«ok» dell'autore) e `separazione_ruoli` (oggi: `blocco`; l'autore può tornare ad
  `avviso` con un commit a parte).
- Configurazione di esempio, **non attiva**: `dati/hook-settings.esempio.json`.
  `zb hook attiva` mostra cosa scriverebbe; `zb hook attiva --ok` (solo dopo l'«ok»
  dell'autore) crea `.claude/settings.json` alla radice del repository; `zb hook disattiva` lo
  toglie, solo se è quello del motore; `zb hook stato` dice se è attivo.

**Rilevamento delle scritture via Bash: dove sbaglia.** Il comando arriva come testo; l'hook
considera scrittura nel manoscritto un comando che nomina `04-manoscritto` con `>`, `>>`, `tee`,
`sed -i`, `perl -i`, `mv`, `cp` (destinazione), `rm`, `truncate`, `touch`, `dd`,
`git checkout`/`git restore`, `python`.

| # | Scenario | Errore | Cosa succede |
|---|---|---|---|
| 1 | `grep … 04-manoscritto/01.md > /tmp/out.txt` | nessuno | la redirezione punta fuori: passa |
| 2 | `python3 motore/script/capitolo.py <libro> 1` (legge, non nomina la cartella) | nessuno | passa |
| 3 | `python3 -c "open('…/04-manoscritto/01.md','w')…"` | nessuno | rilevato |
| 4 | uno script che scrive nel manoscritto senza nominarlo (`python3 /tmp/s.py`) | **falso permesso** | non rilevabile; lo copre `zb avvio` (vedi sotto) |
| 5 | `D=…/04-manoscritto; echo x > $D/01.md` | nessuno | variabile dello stesso comando: rilevato |
| 5b | variabile assegnata in un comando precedente | **falso permesso** | non rilevabile; lo copre `zb avvio` |
| 6 | `cd …/04-manoscritto && sed -i … 01.md` | nessuno | rilevato |
| 7 | `cd …/04-manoscritto` in un comando precedente, poi `sed -i … 01.md` | **falso permesso** | non rilevabile; lo copre `zb avvio` |
| 8 | `git add/commit/push` con file del manoscritto | nessuno | non sono scritture: passa |
| 9 | `git checkout -- …/04-manoscritto/01.md`, `git restore …` | nessuno | rilevato |
| 10 | `cp …/04-manoscritto/01.md /tmp/copia.md` | nessuno | destinazione fuori: passa (`mv` invece è rilevato: toglie il file) |
| 11 | `cat …/04-manoscritto/*.md \| wc -w` | nessuno | passa |
| 12 | un percorso con `04-manoscritto` senza `libro.yaml` sopra | nessuno | passa |
| 13 | l'hook va in errore (JSON illeggibile) | possibile falso permesso | avviso: passa e lo dice; blocco: blocca solo se il testo contiene `04-manoscritto` |
| 14 | contesto compattato dopo l'avvio | voluto | avviso finché non si riesegue `zb avvio` |
| 15 | `python3 x.py …/04-manoscritto/01.md` che legge soltanto | **falso avviso** | `python` con un percorso del manoscritto conta come scrittura |
| 16 | `sed -i` o `cp` con percorso tra virgolette costruito (`"$(ls …)"`, `$(…)`) | **falso permesso** | la sostituzione di comando non si espande; lo copre `zb avvio` |
| 17 | strumenti non elencati (`awk -i inplace`, `ed`, `ex`, `vim -c`, `rsync` verso il manoscritto con opzioni dopo la destinazione, `find … -delete`, `xargs rm`) | **falso permesso** | non rilevati; lo copre `zb avvio` |
| 18 | `echo "04-manoscritto" > nota.txt` (la parola solo nel testo) | nessuno | il bersaglio è `nota.txt`: passa |

I controlli che non dipendono dall'hook sono di `zb avvio`, a ogni sessione: si ferma se nel
libro ci sono modifiche non salvate e se un documento approvato ha uno sha256 diverso da quello
registrato. Una scrittura non rilevata dall'hook ma già salvata in un commit, su un capitolo non
ancora approvato a un gate, non la rileva nessuno dei due: resta visibile solo nella storia git.

## 11. Comandi

`python3 motore/zb aiuto` elenca tutti i comandi, `zb aiuto <comando>` ne dà l'uso: unica fonte
`dati/comandi.yaml` (README e guide non ripetono l'elenco). Prima di ogni push sul lavoro del motore:
`zb prove` intera, tutta OK; `zb push` lo controlla.

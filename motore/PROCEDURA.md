# Procedura del motore

Regole di lavoro per qualsiasi libro. Comandi: `python3 motore/zb <comando> <libro> …`
(qui sotto abbreviato in `zb`; l'elenco unico è `zb aiuto`). Percorso, ruoli e gate: `editoriale/00-percorso.md`;
ruoli editoriali: `editoriale/ruoli/`. Il progetto iniziale è in `proposta-motore.md`.

## 1. Regole fisse

1. **Il libro è un percorso** indicato dall'autore (oppure `ZB_LIBRO`): sempre `libri/<slug>/` sul ramo del
   libro (cartella unica, sezione 10). Il motore legge solo `motore/` e la cartella di quel libro, e scrive
   solo dentro quella cartella. `docs/` non si legge nelle sessioni di lavoro, salvo richiesta.
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
8. **Un ruolo per sessione** (`zb avvio <libro> --ruolo R`); chi scrive non revisiona il proprio testo
   nella stessa sessione (`dati/hook.yaml`, `separazione_ruoli`).
9. **La sessione principale non scrive prosa**: chiama l'agente del passo (`zb agenti prossimo <libro>`) e
   legge solo la sua risposta breve (`editoriale/risparmio-token.md`).

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
   - altrimenti sposta il briefing in `00-progetto/briefing.md` e crea solo dentro la cartella:
     `libro.yaml`, `stato.yaml` (fase «struttura»), `LEGGIMI.md`, `nomi_propri.txt`, `.gitignore` e
     `03-struttura/` con i nove file della fase struttura (modelli di `editoriale/struttura/modelli/`;
     scaletta e piano parole già divisi per capitolo). Nessun documento e nessun capitolo prima del gate
     `struttura`: bibbia, cronologia, manuale di stile, scaletta operativa (date e chiusure) e piano parole
     nascono all'`ok` di quel gate (il piano parole è quello di `03-struttura/08-piano-parole.md`).
3. Le regole della sezione «Direttive» del briefing (genere, lunghezza, voce, tetti, vietati,
   vincoli, gate) vanno in `libro.yaml` e nel manuale **senza riscriverle a mano**.

**Valori fuori dal profilo di genere (override motivati).** La lunghezza, i capitoli («Capitoli:
minimo | media | massimo») e, se indicati, «Frase media: a-b» e «Dialogo: a-b» devono stare nei
valori del profilo. Un valore diverso è accettato solo con «Motivo override:» non vuoto nel
briefing; allora va in `libro.yaml` come override con il motivo, il manuale lo elenca (sezione
«Override», da approvare al gate «documenti») e il numero di capitoli si calcola con i valori nuovi.
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

**Fase struttura** (`editoriale/struttura/01-fase-struttura.md`). L'architetto compila i nove file;
l'editor strutturale, in un'altra sessione, scrive `06-diagnostica/revisione-struttura.md`. `zb pronto`
controlla prima del gate: nessun campo «- …:» vuoto, un blocco di scaletta per ogni capitolo del piano,
budget numerici, nessuna promessa senza pagamento (`06-sottotrame-temi.md`), una tensione da 1 a 10 per
capitolo (`07-tensione-ritmo.md`), revisione dell'editor presente e scritta da un'altra sessione. Il gate
`struttura` è sempre attivo. Dopo l'`ok`, cambiare `09-scelte-fisse.md` (o un altro file approvato) ferma
`zb avvio`: serve `zb riapprova`.

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
- un file modificato o un commit del libro sta fuori da `libri/<slug>/`, o il titolo compare fuori (sezione 10);
- la sessione ha già un altro ruolo, o chiede un ruolo di revisione dopo aver scritto il testo (con
  `separazione_ruoli: blocco`);
- dalla stesura in poi mancano capsule dei capitoli scritti (`capsule: obbligatorie` in `libro.yaml`, il
  predefinito dei libri nuovi; senza il campo è un avviso).

Se tutto va bene stampa:
`Letto: <file> (N righe, sha256 …, commit …), …; libro @ <commit>; motore @ <commit>; fase, gate`,
poi passo, capitoli, parole, revisione in corso, correzioni e avvisi aperti, e scrive solo il
marker `<libro>/.zb/letto-<session_id>` e il ruolo in `<libro>/.zb/ruoli.yaml` (la cartella `.zb/` ignora
sé stessa in git). In stesura legge le capsule dei capitoli scritti, non il capitolo precedente intero.

## 5. Fasi e gate

| Fase | Chi lavora | Gate | Documenti mostrati al gate |
|---|---|---|---|
| struttura | architetto; editor strutturale (altra sessione) | `struttura` (sempre attivo) | i nove file di `03-struttura/` e `06-diagnostica/revisione-struttura.md` |
| documenti | direttore editoriale | `documenti` | libro.yaml, bibbia, cronologia, manuale, scaletta, piano parole, `06-diagnostica/nota-direzione.md` |
| pagina_campione | scrittore con voce | `pagina_campione` | `05-revisioni/pagina-campione.md` (creata vuota; `pronto` la rifiuta vuota) |
| stesura | scrittore con voce, un capitolo per volta | `primi_capitoli` dopo il capitolo 3; `lotto` se attivo; `controllo_fallito` sempre | capitoli e report |
| revisione_manoscritto | editor strutturale (altra sessione) | `struttura_manoscritto` | `06-diagnostica/revisione-manoscritto.md` |
| line | line editor, per capitolo (max 3 in parallelo) | `line` | `06-diagnostica/line/NN.md` di ogni unità |
| copy | correttore di italiano, per capitolo | `copy` | `06-diagnostica/copy/NN.md` di ogni unità |
| bozze | correttore di bozze, su testo fermo (`compila`, `impagina`, `pdf`) | `bozze` | `06-diagnostica/bozze.md` |
| chiusura | motore | — | — |
| chiuso | — | — | — |

**Gate attivi:** campo `gate` di `libro.yaml` (dal briefing, «Gate:»). Predefiniti dei libri nuovi: tutti
(`struttura, documenti, pagina_campione, primi_capitoli, struttura_manoscritto, line, copy, bozze`); possibile
anche `lotto`. `struttura` e `controllo_fallito` sono sempre attivi. Un gate non attivo non ferma: i documenti
si registrano con `senza_gate: true` e si passa oltre; i report della fase devono comunque esserci.
Dopo l'`ok` ai gate `struttura_manoscritto`, `line` e `copy` si applicano gli interventi approvati, con
modifiche puntuali (Edit; l'hook rifiuta la riscrittura intera di un capitolo da parte di un revisore), poi
`zb esito <libro> N` sui capitoli toccati: `esito` vale in tutte le fasi dopo la stesura e non cambia fase.
Passo opzionale, solo con l'ok dell'autore, dopo la revisione strutturale: lettori ciechi e panel
(`editoriale/ruoli/riferimenti/lettori-e-panel.md`, agente `lettore-cieco`).

**Risposte dell'autore**

| Risposta | Comando | Effetto |
|---|---|---|
| `ok` | `zb ok <libro>` | Approva il gate aperto: registra sha256 e commit dei documenti, chiude il gate, passa oltre. Rifiutato se i blocchi non sono stati mostrati tutti, se i documenti sono cambiati dall'ultima lettura, se hanno modifiche non salvate, o se una correzione registrata non è stata applicata. |
| `ok, lotti da N` | `zb ok <libro> lotti da N` | Come `ok`, e fissa la dimensione dei lotti successivi. |
| `avanti` | `zb avanti <libro>` | Blocco successivo (circa 120 righe, tagliato a fine paragrafo). Non approva nulla. Se i documenti cambiano, riparte dal blocco 1. |
| `correggi: …` | `zb correggi <libro> <istruzione>` | Registra la correzione; il gate resta aperto. Applico solo quella, rieseguo i controlli, mostro le righe cambiate (prima e dopo), salvo; poi `avanti` riparte dal blocco 1. |
| correzione fuori dal gate | `zb correggi <libro> <unità>: <motivo>` (con `--commit <hash>` per una correzione già salvata) | Registra data, file, motivo, sha256 precedente e corretto in `stato.yaml` (`correzioni_registrate`); non apre e non chiude gate. Segue i file rinominati (sha256 precedente sotto il nome vecchio). |
| ritorno alla stesura | `zb fase <libro> stesura --motivo "<testo>"` | Solo da una fase dopo la stesura e solo se nel piano parole mancano unità: registra data, fase precedente, motivo e unità mancanti (`cambi_fase`). Si lascia la stesura da soli soltanto quando tutte le unità del piano (prologo, capitoli, interludi, epilogo) sono scritte e accettate. |
| `riapprova` | `zb riapprova <libro> <documento> <motivo>` | Modifica autorizzata a un documento già approvato (già salvata in un commit): registra il nuovo sha256 e commit, con data, motivo e sha256 precedente. Rifiutato se il documento non è approvato, non è cambiato o ha modifiche non salvate. |
| `stato` | `zb stato <libro>` | Fase, gate, lotto, capitoli, parole, revisione, correzioni, avvisi, ultimo commit, allineamento con origin. Non scrive nulla. |

Qualunque altra frase è una domanda: rispondo senza cambiare stato.

**Comandi di Claude Code** (non dell'autore): `zb pronto <libro>` quando il lavoro di una fase
è finito (apre il gate e mostra il blocco 1, oppure passa oltre); `zb esito <libro> N` dopo
aver scritto il capitolo N.

## 6. Stesura di un capitolo

Procedura uguale per ogni capitolo, senza fermate tranne i gate:

1. L'agente `scrittore-voce` (chiamato dalla sessione principale, mai due capitoli in parallelo) legge
   `LEGGIMI.md`, il manuale di stile, la scheda della voce, il blocco del capitolo in scaletta e piano
   parole, la cronologia, le capsule dei capitoli precedenti e solo l'ultima pagina del capitolo precedente.
2. Riporto la riga «Letto: …» di `zb avvio` (se non l'ho già fatto in questa sessione).
3. Scrivo `04-manoscritto/NN-<slug>.md` con la riga nascosta `<!-- zb: chiusura=X -->`.
4. `zb esito <libro> N`: esegue `capitolo.py` (report in `06-diagnostica/capitoli/NN.md`, con le misure
   anti-IA della sezione H del catalogo, audit in `06-diagnostica/anti-ia/NN.md`, e l'indice Gulpease
   informativo) e aggiorna `stato.yaml` (ultimo capitolo scritto, parole, lotto).
5. `zb capsula <libro> N`: crea `07-capsule/NN.md`; l'agente `capsula` la compila (sette campi, massimo 180
   parole); di nuovo `zb capsula` per controllarla.
6. Blocco di salvataggio (sezione 8).

**Anti-IA (audit).** Le misure (`script/anti_ia.py`, soglie `anti_ia` nel profilo di genere, tarate sui
mini-libri) sono avvisi: monotonia delle frasi, aperture uguali, formule per mille parole, chiusure uguali
di fila, ripetizioni ravvicinate, segni tipografici all'inglese. Il report elenca riga, schema e proposta;
non riscrive nulla. Con `anti_ia: {modalita: blocco}` in `libro.yaml` diventano KO.

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

**Totale del libro.** `zb esito` (e il modulo `conta.py`) confronta il totale previsto (parole scritte più i
budget delle unità non ancora scritte) con `parole.target_totale`. Fuori da `capitoli.tolleranza_totale`
danno un AVVISO con il budget residuo proposto per le unità rimanenti (in proporzione ai loro budget).
È una proposta: il motore non accorcia né allunga un capitolo per far sparire l'avviso, e non tiene
i capitoli sotto una soglia; a libro finito, fuori tolleranza, decide l'autore.

**Lotti.** Dopo il capitolo 3 si apre `primi_capitoli`; con l'«ok» l'autore sceglie i lotti
(`ok, lotti da N`). Poi i capitoli si scrivono in lotti di N **senza fermate** (salvo gate
`lotto` attivo o controllo fallito due volte). Scritte e accettate tutte le unità del piano parole, la
fase passa a «revisione_manoscritto».

## 7. Chiusura

Dopo il gate `bozze`, in ordine: `zb continuita`, `zb ortografia`,
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
- (b) LanguageTool, solo se `ZB_LANGUAGETOOL` indica la cartella dei suoi `.jar`, mai nel repository.
  Installazione e verifica: `zb ortografia installa` (stampa la riga `export ZB_LANGUAGETOOL=…`) e
  `zb ortografia verifica` (README, «LanguageTool»). Con 403 o 429 da Maven Central non si insiste.
- (c) Lista di controllo del correttore, sempre, in fondo al report: le voci delle sezioni 1-6 di
  `editoriale/correttore/criteri-correttore.md` (fonte unica). I correttori automatici non rilevano «e» per
  «è», gli accordi sbagliati, le parole vere usate al posto di altre: le controlla il correttore di italiano.
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

Dopo ogni passo che scrive: report in `<libro>/06-diagnostica/`, `git add`, commit, push,
`git status -sb`, `git log -1`. Se il push fallisce o un file non si salva: fermarsi e riportare
l'errore esatto; mai dire «fatto» se non è su origin; niente altri rami, tag o push forzati.
Resoconto: hash, file, parole o pagine, «branch allineato a origin: sì/no».
Nessun comando del motore fa commit da solo. `zb push` prima del push controlla la cartella unica; sul
lavoro del motore vuole anche `zb prove` passate sullo stato attuale (sezione 11).

## 9. Ripresa dopo un'interruzione

Solo da file: `zb avvio <libro>`. Se si ferma per modifiche non salvate, mostro quali file e
chiedo «tieni» o «scarta» (non scarto nulla da solo). Se c'era una revisione in corso, `avanti`
riprende dal blocco registrato (o dal blocco 1 se i documenti sono cambiati).

## 10. Cartella unica e recinto

Tutto ciò che riguarda un libro vive solo in `libri/<slug>/`, sul ramo del libro; il nome del libro non
compare fuori da lì (il libro attivo sta in `<git-dir>/zb-libro-attivo`, non in un file tracciato).
`zb cartella <libro>`, e da soli `zb avvio` e `zb push`, controllano su git: file modificati fuori dal libro,
commit «misti» che toccano il libro e altro, titolo o percorso del libro in file fuori dalla cartella.
Esclusi, dichiarati in `dati/cartella-unica.yaml`: la configurazione della radice del ramo (`CLAUDE.md`,
`.gitignore`, `.claude/settings.json`, `.claude/agents/`), i merge del motore e i commit misti già fatti che
l'autore dichiara con motivo (la storia non si riscrive). Il recinto dell'hook (`hook_recinto.py`, sezione
11) blocca prima le scritture fuori dal libro attivo, anche via Bash, e i `git commit`/`git push` che
violerebbero la cartella unica; sul lavoro del motore («lavoro sul motore» → `zb lavoro motore`) blocca invece
`libri/`.

## 11. Hook (protezione in più, non una garanzia)

- `script/hook_sessione.py` (SessionStart): scrive il `session_id` in
  `$CLAUDE_PROJECT_DIR/.zb/sessione-corrente`; dopo una compattazione registra l'ora, e i marker
  di avvio precedenti non valgono più.
- `script/hook_manoscritto.py` (PreToolUse): se una scrittura va in `<x>/04-manoscritto/` di un
  libro senza il marker di avvio della sessione, in modalità **avviso** stampa «ATTENZIONE: …»,
  lo annota in `<x>/.zb/avvisi-hook.log` e **lascia passare**; in modalità **blocco** ferma lo
  strumento (codice 2).
- `script/hook_recinto.py` (PreToolUse, anche su Bash): recinto sul libro attivo in blocco, cartella unica
  prima di `git commit` e `git push`, nessuna riscrittura intera di un capitolo da parte di un revisore;
  annota chi scrive in `<libro>/.zb/scritture.log` (separazione dei ruoli).
- `script/consumo.py` (PostToolUse su Read, Agent, Task): letture e subagenti per `zb consumo`.
- Modalità di `hook_manoscritto.py` in `dati/hook.yaml` (oggi: `avviso`); nello stesso file
  `separazione_ruoli` (oggi: `blocco`). Ogni cambio è un commit a parte, dopo l'«ok» dell'autore.
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

## 12. Comandi

Un solo elenco, nel codice: `python3 motore/zb aiuto`. Prima di ogni push sul lavoro del motore:
`zb prove` (tutte OK); `zb push` lo controlla.

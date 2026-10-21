# Proposte di motore (non applicate)

Modifiche al codice che servirebbero per applicare in automatico regole oggi solo scritte. Nessuna è
implementata: il codice del motore non è cambiato. Nate dalla riscrittura di prova di tre capitoli di un
libro di test con una voce della banca (ottobre 2026).

## P1. Limite per capitolo sui divieti della voce

**Problema.** La voce vuole al massimo una chiusa a sentenza per capitolo. `stile.py` sa già contare un
limite per unità (campo `massimo` delle voci del libro, modalità avviso), ma `voce.divieti()` costruisce
ogni divieto della voce solo con `id`, `espressione`, `pattern`, `modalita: avviso` e `nota`: il campo
`massimo` (e anche `escludi_pattern`) di `divieti.yaml` si perde, e ogni occorrenza è un avviso.

**Cosa servirebbe.**
- `motore/script/voce.py`, `divieti()`: portare nel dizionario anche `massimo` (intero ≥ 0) ed
  `escludi_pattern` (validato con `re.compile`, come `pattern`), se presenti.
- `motore/script/voce.py`, docstring e `verifica`: documentare i due campi facoltativi; FERMO se `massimo`
  non è un intero.
- `motore/script/stile.py`: nessuna modifica per `massimo` (il ramo «avviso con massimo» esiste già); per
  contare più pattern insieme (tutte le forme di chiusa contro un solo limite) servirebbe un campo di
  gruppo, per esempio `gruppo: chiuse`, sommato per unità: modifica in `controlla_unita`.
- Banca-voci: il README documenta i campi; la voce li usa.

**Prove da cambiare o aggiungere.** `motore/script/prove.py`, sezione della banca-voci (punto (g), «divieti
della voce: AVVISO in stile.py»): un divieto con `massimo: 1` e due occorrenze dà un solo AVVISO
«2 occorrenze (massimo 1)»; un divieto con `massimo` non intero dà FERMO in `zb voce verifica`; un
`escludi_pattern` toglie l'occorrenza. Valori attesi in `motore/prove/attesi.yaml`; banca di prova in
`motore/prove/banca-voci-prova/voci/voce-di-prova/divieti.yaml`.

**Limite che resta.** Anche con il limite, il motore conta solo le forme scritte nei pattern: la chiusa
definita per funzione la riconosce solo chi rivede.

## P2. Revisione del capitolo in fase «stesura»

**Problema.** Il ruolo del diagnosta prevede un rapporto sul capitolo singolo (`06-diagnostica/audit/NN.md`,
`editoriale/ruoli/00-diagnosta.md`), ma `percorso.FASI_RUOLO` dà al diagnosta solo «struttura» e
«struttura_manoscritto»: in «stesura» `zb ruolo <libro> diagnosta N` si rifiuta e il rapporto non ha la
prima riga con l'impronta. `zb esito` non sa nulla della revisione: un capitolo che «non passa» la checklist
viene accettato lo stesso se i controlli meccanici sono verdi.

**Cosa servirebbe.**
- `motore/script/percorso.py`, `FASI_RUOLO`: «stesura» tra le fasi del diagnosta, solo per il capitolo
  singolo (`zb ruolo <libro> diagnosta N`).
- `motore/script/ruolo.py`: in «stesura» con N, percorso del rapporto `06-diagnostica/audit/NN.md` e prima
  riga `<!-- zb: ruolo=diagnosta; su=<impronta del capitolo N> -->`; controllo di separazione: la sessione
  del diagnosta non deve aver scritto `04-manoscritto/` (già in `NON_SCRITTO`).
- `motore/script/fase.py`, `cmd_esito`: con un campo di `libro.yaml` (per esempio `revisione_capitolo:
  obbligatoria`) `zb esito N` vuole `06-diagnostica/audit/NN.md` con l'impronta del testo attuale e
  l'ultima riga «passa»; altrimenti KO con il motivo. Senza il campo, comportamento di oggi.
- `motore/dati/libro.schema.yaml`: il campo nuovo; `motore/PROCEDURA.md`, sezione 6: il passo di revisione
  tra la scrittura e `zb esito`.

**Prove da cambiare o aggiungere.** `motore/script/prove_editoriale.py`: oggi «line-editor in fase struttura:
rifiutato»; in più: diagnosta con N in «stesura» accettato, diagnosta senza N in «stesura» rifiutato,
`zb esito` con `revisione_capitolo: obbligatoria` e rapporto mancante, con impronta vecchia, con «non passa»
(tre KO) e con rapporto valido (OK). Mini-libro editoriale in `motore/prove/mini-libro-editoriale/`.

## P3. Frase media per registro

**Problema.** La frase media è una sola per tutto il libro (`frase_media` del profilo o override in
`libro.yaml`, controllata da `stile.py` come KO). Una voce con un registro corto per l'azione (5-10 parole)
e un manuale con 9-14 si contraddicono nei capitoli d'azione; il motore spinge a unire frasi corte per
rientrare nella media.

**Cosa servirebbe.**
- `motore/dati/libro.schema.yaml`: un campo facoltativo per capitolo, per esempio
  `frase_media_capitoli: {"1": [5, 10]}`, con motivo obbligatorio (come gli altri override).
- `motore/script/stile.py`, `controlla_unita`: se l'unità ha un valore in quel campo, usa quello al posto
  di `profilo['frase_media']`; il report lo dice.
- `motore/script/nuovo.py` o la scheda del capitolo: chi decide il registro del capitolo lo scrive lì; il
  manuale lo elenca nella sezione «Override».

**Prove da cambiare o aggiungere.** `motore/script/prove.py`, prove di `stile.py` e `capitolo.py`: capitolo con
override per capitolo dentro il suo intervallo e fuori da quello generale (OK), fuori da entrambi (KO);
campo senza motivo (FERMO in `zb nuovo`/validazione dello schema). Valori in `motore/prove/attesi.yaml`.

## Senza codice: checklist del capitolo per l'autore

`libro.yaml` accetta già `checklist_capitolo` (righe con casella nel report di `capitolo.py`, sezione
«Checklist manuale»). Le regole della revisione (chiuse, eco, etichette, soggetto, registro corto,
continuità) possono stare lì come promemoria per l'autore, senza cambiare il codice: è una modifica a
`libro.yaml`, documento approvato, quindi con `zb riapprova` e decisione dell'autore.

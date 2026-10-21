# Proposte di motore: cosa è stato realizzato

Nate dalla riscrittura di prova di tre capitoli di un libro di test con una voce della banca (ottobre 2026).
Le prime tre proposte e la frase media per registro sono ora nel codice del ramo `integrazione-editoriale`,
ognuna con le sue prove; sotto, per ciascuna, cosa fa e cosa resta fuori.

## P1. Limite per capitolo sui divieti della voce — realizzata (commit 1e11337)

- `script/voce.py`, `divieti()`: porta in `stile.py` il campo facoltativo `massimo` (intero ≥ 0; FERMO con il
  nome del divieto se non lo è). Senza `massimo` nulla cambia: un avviso a ogni occorrenza.
- `script/stile.py`: nessuna modifica; il ramo «avviso con massimo» già esistente dà un solo AVVISO
  «N occorrenze (massimo M)» quando il capitolo supera il limite.
- Prove: `prove.py`, sezione `voce`, punto (h): esiti con massimo 1, 2 e senza; `massimo: uno` → verifica KO.
- Limite di gruppo — realizzato dopo (21 ottobre): `massimo` conta per singolo pattern, quindi cinque forme di
  chiusa con `massimo: 1` lasciavano passare fino a cinque chiuse. Ora `gruppi: {nome: {massimo: N}}` e
  `gruppo: nome` sui divieti danno un solo massimo complessivo per capitolo (prove (i) della sezione `voce`).
  La voce della prova non usa ancora i gruppi: va aggiunto nel suo `divieti.yaml`, nella banca-voci.
- **Non realizzato:** `escludi_pattern` per i divieti della voce. Due forme che prendono la stessa frase la
  contano due volte nel gruppo.

## P2. Revisione del capitolo in fase «stesura» — realizzata (commit 5d19661)

- `percorso.FASI_RUOLO`: il diagnosta lavora anche in «stesura», solo con N (`zb ruolo <libro> diagnosta N` →
  `06-diagnostica/audit/NN.md`, prima riga con l'impronta del capitolo); senza N si rifiuta.
- `libro.yaml`: campo facoltativo `revisione_capitolo: obbligatoria | facoltativa`. Con «obbligatoria»
  `zb esito <libro> N` si ferma se il rapporto manca, non ha l'intestazione del diagnosta, è scritto su
  un'altra versione del capitolo o chiude con «non passa». Senza il campo, comportamento di prima.
- Prove: `prove_editoriale.py`, `revisione_in_stesura` (sette controlli).
- **Non realizzato:** il motore non legge il contenuto della checklist (solo l'ultima riga e l'impronta).

## P3. Frasi finali per chi rivede — realizzata (commit 03f12c6)

- `zb stile <libro> [N]` scrive `06-diagnostica/frasi-finali/NN.md`: la frase finale di ogni paragrafo di
  narrazione e dell'ultima battuta di ogni scambio, con riga e tipo («fine scena» se segue uno stacco).
- Il motore elenca e non giudica: la tabella «chiusa sì/no» la scrive il diagnosta (`00-diagnosta.md`).
- Prove: `prove.py`, sezione `frasi_finali` (due controlli).

## Frase media per registro — realizzata (commit 4d21449; AVVISO invece di KO dal commit 3990f86)

- Decisione dell'autore: nel thriller la voce prevale sul manuale per la frase media.
- `profili/thriller.yaml`: `frase_media_voce: true` (campo nuovo dello schema, uso controllo).
- `voce.registri()`: intervalli dalla riga «frase media» della tabella nella sezione 3 della scheda.
- `stile.intervallo_frase_media()`: registro del capitolo dalla scaletta («registro <nome>»; il primo dichiarato è
  il dominante); senza registro, «base»; un override di `frase_media` in `libro.yaml` resta sopra.
- Formulazione scelta: «il capitolo passa se la media complessiva è nell'intervallo del registro dominante
  dichiarato». **Non realizzato:** il controllo per scena («ogni registro nel proprio intervallo»), perché la
  scaletta dichiara il registro per capitolo e non per scena.
- Fuori intervallo del registro: AVVISO «intervallo non calibrato sull'autore» (l'intervallo è una scelta della
  voce da calibrare sui testi dell'autore prima di bloccare); l'intervallo del profilo resta KO.
- Prove: `prove.py`, sezione `frase_media_registro` (otto controlli).

## Ruoli

- Diagnosta, capitolo singolo: tabella frase per frase delle chiuse costruita su `frasi-finali/NN.md`; eco,
  etichette, soggetto (anche nome ripetuto dove è ovvio), battute giustificative, registro corto, continuità.
- Scrittore con voce: legge le sezioni 2, 3 e 6 della scheda della voce e i divieti; `zb prepara` lo scrive nella
  preparazione del capitolo e nomina gli esempi «debole → forte» solo se la scheda li ha; si ferma se la scheda
  manca (commit dd93098; prove in `prove_editoriale.py`).

## Senza codice: checklist del capitolo per l'autore

`libro.yaml` accetta già `checklist_capitolo` (righe con casella nel report di `capitolo.py`). Resta possibile
usarla come promemoria; è una modifica a un documento approvato (`zb riapprova`) e decisione dell'autore.

## P4. Diagnosta senza shell: rapporti senza impronta — NON realizzata (motivo sotto)

Problema (prova su una pagina, ottobre 2026): l'agente `diagnosta` installato ha `tools: Read, Write, Glob, Grep`
(`editoriale/agenti/diagnosta.md`), quindi non può lanciare `zb ruolo <libro> diagnosta N` né `zb stile <libro> N`.
Il rapporto resta senza la prima riga `<!-- zb: ruolo=diagnosta; su=<impronta> -->` e, con
`revisione_capitolo: obbligatoria`, `zb esito` lo rifiuta.

Perché non si aggiunge Bash al diagnosta (verificato il 2026-10-21):
- il campo `tools` dei subagenti accetta nomi di strumenti interi: un comando solo (`Bash(python3 motore/zb ruolo:*)`)
  non si può esprimere lì; in `disallowedTools` una voce con specificatore toglie l'intero strumento
  (documentazione ufficiale di Claude Code, pagina «Subagents»);
- un hook PreToolUse nel frontmatter dell'agente che ammetta solo quei comandi esiste, ma Claude Code lo salta se la
  cartella non è stata dichiarata attendibile («the subagent still runs, but Claude Code skips its frontmatter
  hooks»): il diagnosta resterebbe con Bash libero;
- il recinto (`script/hook_recinto.py`, PROCEDURA §10) su Bash blocca solo le scritture fuori dal libro attivo; il
  divieto per i revisori di riscrivere un capitolo vale solo per Write (`riscrittura_da_revisore`). Con Bash il
  diagnosta, che oggi è «in sola lettura» perché non ha Edit né Bash, potrebbe modificare `04-manoscritto/`
  (`sed -i`, script) senza che nulla lo fermi. Nota: `correttore-italiano` e `correttore-bozze` hanno già Bash, ma
  sono ruoli che correggono il testo; il diagnosta per ruolo non lo tocca (`00-diagnosta.md`, «Cosa NON fa»).

Soluzione alternativa proposta (non realizzata):
- la sessione principale, che ha la shell, lancia prima della chiamata `zb stile <libro> N` e
  `zb ruolo <libro> diagnosta N` e passa al diagnosta la riga d'intestazione nel compito; il diagnosta la copia come
  prima riga di `06-diagnostica/audit/NN.md`;
- in codice: `zb agenti prossimo <libro>` (agenti.py), quando il passo è la revisione di un capitolo, stampa questi
  due comandi prima della chiamata al diagnosta, e `editoriale/agenti/diagnosta.md` dice di usare la riga ricevuta
  (e di fermarsi se manca) invece di lanciare il comando.
- Prove necessarie: `zb agenti prossimo` su un libro di prova con `revisione_capitolo: obbligatoria` stampa i due
  comandi; `zb esito` accetta il rapporto con la riga copiata e lo rifiuta senza; `zb agenti stato` controlla che
  il diagnosta installato resti senza Bash ed Edit.

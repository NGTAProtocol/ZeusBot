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
- **Non realizzato:** `escludi_pattern` per i divieti della voce e un limite di gruppo (tutte le forme di chiusa
  contro un solo tetto). Il limite resta per singolo pattern.

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

## Frase media per registro — realizzata (commit 4d21449)

- Decisione dell'autore: nel thriller la voce prevale sul manuale per la frase media.
- `profili/thriller.yaml`: `frase_media_voce: true` (campo nuovo dello schema, uso controllo).
- `voce.registri()`: intervalli dalla riga «frase media» della tabella nella sezione 3 della scheda.
- `stile.intervallo_frase_media()`: registro del capitolo dalla scaletta («registro <nome>»; il primo dichiarato è
  il dominante); senza registro, «base»; un override di `frase_media` in `libro.yaml` resta sopra.
- Formulazione scelta: «il capitolo passa se la media complessiva è nell'intervallo del registro dominante
  dichiarato». **Non realizzato:** il controllo per scena («ogni registro nel proprio intervallo»), perché la
  scaletta dichiara il registro per capitolo e non per scena.
- Prove: `prove.py`, sezione `frase_media_registro` (sette controlli).

## Ruoli

- Diagnosta, capitolo singolo: tabella frase per frase delle chiuse costruita su `frasi-finali/NN.md`; eco,
  etichette, soggetto (anche nome ripetuto dove è ovvio), battute giustificative, registro corto, continuità.
- Scrittore con voce: legge le sezioni 2, 3 e 6 della scheda della voce (esempi «debole → forte») e i divieti;
  `zb prepara` lo scrive nella preparazione del capitolo (prova in `prove_editoriale.py`).

## Senza codice: checklist del capitolo per l'autore

`libro.yaml` accetta già `checklist_capitolo` (righe con casella nel report di `capitolo.py`). Resta possibile
usarla come promemoria; è una modifica a un documento approvato (`zb riapprova`) e decisione dell'autore.

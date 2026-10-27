# Difetti: da errore a test permanente

Ogni difetto trovato in un capitolo (da chi legge, dal revisore, dall'autore) diventa un test che non si può più
violare. Il motore lo controlla a ogni «zb esito» (cancello dei difetti) e nel controllo finale («zb finale»).

## Procedura (sempre in quest'ordine)

1. **Registra.** Una voce in `06-diagnostica/difetti/registro.yaml` del libro:
   `{id: D16, classe: <classe>, descrizione, gravita, rilevamento, data, scena: <N>, fixture_sbagliata: <cartella>,
   fixture_corretta: <cartella>}`. La classe è una di `motore/dati/difetti.yaml`; se nessuna va bene, se ne aggiunge
   una (motore: «lavoro sul motore»).
2. **Scrivi la fixture che fallisce.** La versione sbagliata del capitolo (o dei capitoli, se il difetto è tra
   capitoli) in una cartella di fixture del libro, con il commit prima della correzione.
3. **Correggi** il capitolo con una correzione mirata (chi scrive, non chi rivede).
4. **Il test passa.** La versione corretta in una seconda cartella di fixture; `zb difetti <libro> prova` deve dare
   «fallito» sulla sbagliata e «passato» sulla corretta.
5. **Commit**: fixture originali, correzione del capitolo, test e registro, in commit separati.

Il controllo ha un criterio generale (un tipo di errore), mai la frase esatta dell'esempio: cambiare una parola non
deve bastare a eluderlo. Un controllo con falsi allarmi si corregge nel criterio, non spegnendolo.

## Tre rilevamenti

- **Deterministico** (`motore/script/difetti.py`): date e giorni, ordine e tipo dei capitoli, aperture ripetute,
  frasi-firma, chiusure, lunghezza, cliché, copia tra capitoli, similitudini, tratti ricorrenti, etichette di ruolo.
- **Revisore** (diagnosta, sezione `## Registro dei difetti` del rapporto): conoscenza dei personaggi, inferenze
  presentate come fatti, motivazioni. È meno affidabile di uno script: i falsi negativi osservati si annotano nel
  registro e alzano l'attenzione del revisore (lezioni).
- **Fonte**: i fatti controllabili (sezione `## Fatti da verificare` del rapporto) vanno in
  `06-diagnostica/difetti/fatti.yaml`; il capitolo resta non approvato finché ognuno non è `verificato` (con la fonte)
  o riscritto in forma `generico`. Mai scrivere un fatto a memoria.

## Il cancello

Per ogni classe: **passato**, **fallito** o **non verificabile**. «Non verificabile» non vale mai come passato. Un
difetto bloccante fallito o non verificabile ferma «zb esito»; un avviso si scrive e non ferma. L'unica scorciatoia è
un'eccezione con il motivo scritto nel registro (`eccezioni: [{unita, classe, motivo}]`), visibile a chi legge.

## Comandi

- `zb difetti <libro> [N]`: il cancello su un capitolo o su tutti.
- `zb difetti <libro> prova`: ogni voce del registro sulle sue fixture.
- `zb difetti <libro> continuita`: registro di continuità (date, giorni trascorsi, conteggi, luoghi, conoscenze).
- `zb difetti <libro> fatto <id> verificato|generico|errato --fonte <url>`: esito della verifica di un fatto.

## Intestazione dei capitoli

Ogni capitolo ha sotto il titolo l'intestazione `Luogo — 21 ottobre` (data della storia) e, se non è un capitolo in
sequenza, il tipo nascosto `<!-- zb: tipo=prologo|flash-forward|flashback|epilogo|interludio -->`. Un capitolo con
data anteriore a uno precedente senza tipo dichiarato è un difetto bloccante.

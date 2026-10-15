# Risparmio di token

Regole per lavorare su un libro con pochi token. Le applicano la sessione principale, gli agenti e gli
script. Misura reale con `zb consumo` (nessuna percentuale dichiarata senza misura).

## Chi fa cosa
1. **Gli script fanno tutto il meccanico:** conteggi, controlli, capsule preparate, filtro del codex,
   stato compatto, salvataggio. Nessun ragionamento del modello su ciò che uno script calcola.
2. **La sessione principale orchestra e non scrive prosa:** chiama l'agente del passo con libro e
   capitolo e legge solo la sua risposta breve (al massimo 10 righe).
3. **Un subagente per capitolo e per ruolo, in contesto pulito.** La scrittura va in sequenza (il
   capitolo N+1 ha bisogno della capsula N). Line editing, copyediting e controlli per capitolo vanno
   in parallelo, al massimo 3 alla volta (`motore/dati/modelli-ruoli.yaml`, campo `parallelo_massimo`).
4. **Orchestrazione per dipendenze:** un passo parte quando i suoi input esistono (capsula precedente,
   gate approvato), non per orario.

## Cosa si legge
- Nelle sessioni nuove: la riga «Letto» di `zb avvio`, lo stato compatto (`stato-compatto.md`, 15-20
  righe) e la scheda del capitolo. Nient'altro all'inizio.
- Lo scrittore e i revisori leggono le capsule (`07-capsule/`), non i capitoli precedenti interi.
- Dal codex solo le schede con i tag della scena (`zb prepara`).
- `docs/` non si legge mai durante il lavoro su un libro.

## Cosa si scrive
- Output di ogni comando `zb` al massimo 40 righe, con il rimando al report per il resto. Eccezione
  dichiarata: i blocchi dei documenti mostrati all'autore a un gate (circa 120 righe), perché sono la
  lettura dell'autore.
- I report citano capitolo e riga e non incollano brani.
- I revisori fanno modifiche puntuali (Edit) e non riscrivono i file.

## Caching
- `CLAUDE.md` al massimo 30 righe, senza nomi di libri, e sempre uguale: è il prefisso stabile delle
  istruzioni. Le cose che cambiano (stato, capitolo) stanno nei file del libro, non in `CLAUDE.md`.
- I file degli agenti non cambiano durante un libro: il loro testo è un prefisso stabile.

## Modelli per ruolo
Un solo file di dati: `motore/dati/modelli-ruoli.yaml` (forte per architetto ed editor strutturale,
medio per scrittore, line, copy e bozze, leggero per la capsula). Se il modello leggero sbaglia nel
copyediting, si alza solo quel ruolo.

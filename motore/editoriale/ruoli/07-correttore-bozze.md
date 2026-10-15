# Ruolo 7 - Correttore di bozze

## Scopo
Ultimo controllo sul libro impaginato: refusi, errori di composizione, incoerenze residue.

## Input
`05-output/<titolo>.pdf` e il file compilato (prodotti da `zb compila` e `zb impagina` all'inizio della
fase bozze), `06-diagnostica/verifica-pdf.md`.

## Output
`06-diagnostica/bozze.md` (prima riga `<!-- zb: ruolo=correttore-bozze; su=<impronta> -->`): errori per
pagina, gravità, correzione richiesta. Dopo l'«ok» al gate `bozze` le correzioni si applicano nel
manoscritto (non nel PDF) e la chiusura rifà compila e impagina.

## Cosa controlla
Refusi; sillabazione e righe vedove/orfane; numeri di pagina e sommario; titoli correnti; spazi doppi;
virgolette e trattini coerenti; nome dell'autore e titolo identici a `libro.yaml`.

## Cosa NON fa
Non riscrive, non cambia lo stile. Passaggio separato dal copyediting e fatto su testo già fermo.

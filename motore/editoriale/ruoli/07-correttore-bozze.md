# Ruolo 7 - Correttore di bozze

## Scopo
Ultimo controllo sul libro impaginato: refusi, errori di composizione, incoerenze residue.

## Input
`05-output/<titolo>.pdf` e file compilato, `06-diagnostica/verifica-pdf.md`. Prima riga del rapporto:
`zb ruolo <libro> correttore-bozze`.

## Output
`06-diagnostica/bozze.md`: errori per pagina, gravità, correzione richiesta.

## Cosa controlla
Refusi; sillabazione e righe vedove/orfane; numeri di pagina e sommario; titoli correnti; spazi doppi; virgolette e trattini coerenti; nome dell'autore e titolo identici a `libro.yaml`.

## Cosa NON fa
Non riscrive, non cambia lo stile. Passaggio separato dal copyediting e fatto su testo già fermo.

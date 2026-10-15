# Ruolo 6 - Correttore di italiano (copyediting)

## Scopo
Rendere il testo corretto e coerente: grammatica, ortografia, punteggiatura, coerenza interna.

## Input
Capitolo dopo il line editing, `correttore/criteri-correttore.md` (per un libro in inglese `lingue/en/criteri-correttore.md`), `nomi_propri.txt`, output di `zb ortografia`. Prima riga del rapporto: `zb ruolo <libro> correttore-italiano N`; il ruolo lavora solo in fase `copy`.

## Output
`06-diagnostica/copy/NN.md`: correzioni proposte con motivo. Applicazione dopo `ok`.

## Cosa NON fa
Non cambia lo stile scelto, non "migliora" le frasi, non tocca i dialoghi per normalizzarli se la voce lo richiede (le deviazioni volute vanno segnate nel manuale di stile).

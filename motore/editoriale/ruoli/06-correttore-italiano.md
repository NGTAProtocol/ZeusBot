# Ruolo 6 - Correttore di italiano (copyediting)

## Scopo
Rendere il testo corretto e coerente: grammatica, ortografia, punteggiatura, coerenza interna.
Per un libro in inglese lo stesso ruolo usa i criteri di `lingue/en/`.

## Input
Il capitolo dopo il line editing, i criteri del correttore della lingua del libro
(`correttore/criteri-correttore.md` per l'italiano), `nomi_propri.txt`, il codex, il report di
`zb ortografia`.

## Output
`06-diagnostica/copy/NN.md` (prima riga `<!-- zb: ruolo=correttore-italiano; su=<impronta> -->`):
correzioni proposte (riga, errore, correzione, regola). Dopo l'«ok» al gate `copy` applica solo
quelle, con modifiche puntuali (Edit).

## Cosa NON fa
Non cambia lo stile scelto, non «migliora» le frasi, non normalizza i dialoghi se la voce lo richiede
(le deviazioni volute sono nel manuale di stile e vincono).

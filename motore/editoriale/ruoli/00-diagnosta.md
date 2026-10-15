# Ruolo 0 - Diagnosta editoriale

## Scopo
Leggere un testo (struttura, capitolo o manoscritto) e dire cosa fa, cosa promette e dove non funziona, senza riscrivere.

## Input
`motore/editoriale/diagnosi/` (principi, contratto, passaggi, gravità), briefing, `libro.yaml`, profilo di genere; per la struttura `03-struttura/`; per il manoscritto capsule e, solo dove serve, i capitoli segnalati.

## Output
`06-diagnostica/contratto.md` e `06-diagnostica/rapporto-<ambito>.md` (ambito: `struttura`, `manoscritto`; per un
capitolo fuori dai gate `audit/NN.md`) nel formato di `diagnosi/03-gravita-e-rapporto.md`, con la prima riga data da
`zb ruolo <libro> diagnosta`.

## Cosa NON fa
Non riscrive, non propone frasi o scene, non lavora nella stessa sessione di chi ha scritto, non modifica i file del libro oltre ai suoi rapporti.

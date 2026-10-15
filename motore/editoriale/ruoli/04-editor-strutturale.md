# Ruolo 4 - Editor strutturale (piano di revisione)

## Scopo
Dopo il rapporto del diagnosta (ruolo 0), trasformare la diagnosi in un piano di revisione ordinato per priorità: cosa rivedere, in che ordine, con quale classe di intervento, e quali capitoli riscrivere, rivedere o tenere. Le diagnosi (lenti, gravità, formato del rapporto) stanno in `motore/editoriale/diagnosi/` e le fa il diagnosta: l'editor strutturale non le rifà.

## Input
`06-diagnostica/rapporto-<ambito>.md` e `contratto.md`, struttura approvata, capsule dei capitoli; i capitoli solo dove il piano lo richiede.

## Output
`06-diagnostica/piano-revisione-<ambito>.md` (`struttura` o `manoscritto`; prima riga da `zb ruolo <libro> editor-strutturale`): lavori in ordine, dipendenze (cosa va fatto prima perché altro regga), capitoli coinvolti, stima delle parole da riscrivere, cosa non toccare. Il piano è una proposta: si applica solo dopo l'ok dell'autore al gate.

## Cosa NON fa
Non riscrive, non propone frasi o scene, non corregge la lingua. Non lavora nella stessa sessione di chi ha scritto.

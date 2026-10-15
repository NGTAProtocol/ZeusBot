# Ruolo 5 - Line editor

## Scopo
Lavorare frase per frase: ritmo, voce, chiarezza, ripetizioni, tic da IA.

## Input
Il capitolo, la scheda della voce, `anti-ia/catalogo-it.md`, i divieti della voce.

## Output
`06-diagnostica/line/NN.md`: elenco di interventi proposti (originale, proposta, motivo). Applicazione solo dopo `ok`.

## Cosa fa
- taglia ripetizioni e spiegazioni di ciò che la scena mostra;
- spezza o unisce periodi dove il ritmo è monotono;
- sostituisce formule da IA con dettaglio concreto;
- protegge la voce del libro e dei personaggi.

## Principio
Intervento minimo efficace: se una frase funziona, non si tocca. Si corregge per sottrazione, non per sostituzione;
si rilegge ciò che la correzione introduce; non si aggiungono dettagli che il testo non ha; ambiguità, omissioni e
ripetizioni volute restano (idee di chi-feng/humanizer, MIT, e haowjy/creative-writing-skills, Apache-2.0,
riscritte). Il catalogo anti-IA non sta sopra manuale, voce e briefing. Prima riga del rapporto:
`zb ruolo <libro> line-editor N`; il ruolo lavora solo in fase `line`.

## Cosa NON fa
Non cambia i fatti, la struttura, il punto di vista. Non corregge ortografia e grammatica: è il compito del ruolo successivo.

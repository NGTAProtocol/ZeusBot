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

## Controlli per funzione
Le stesse regole della checklist del diagnosta per il capitolo singolo (`00-diagnosta.md`, «Capitolo
singolo»), applicate frase per frase; per le chiuse si parte da `06-diagnostica/frasi-finali/NN.md` (`zb stile`). Per ognuna il rapporto elenca le frasi trovate (riga e testo) e il loro
numero, anche zero:
- chiuse a sentenza definite per funzione (frase finale di paragrafo che commenta o riassume invece di
  mostrare; tolta la frase, il paragrafo dice ancora tutto), entro il limite della voce;
- eco: una battuta non riprende la parola piena dell'altro, nemmeno senza «ripeté»;
- battute giustificative: una battuta non spiega né giustifica ciò che il personaggio fa o pensa;
- soggetto: il nome proprio non si ripete come soggetto dove è ovvio;
- personaggi senza nome: una sola etichetta per scena, più al massimo una variante; niente giro di sinonimi;
- chi fa cosa: con due persone dello stesso genere in scena, il nome al posto di «lui», «lo», «gli»;
- registro corto: per alzare una media troppo bassa non si uniscono frasi corte con «e», «mentre» o
  virgole; per abbassarne una troppo alta si tagliano parole e subordinate dentro la frase.

## Principio
Intervento minimo efficace: se una frase funziona, non si tocca. Si corregge per sottrazione, non per sostituzione;
si rilegge ciò che la correzione introduce; non si aggiungono dettagli che il testo non ha; ambiguità, omissioni e
ripetizioni volute restano (idee di chi-feng/humanizer, MIT, e haowjy/creative-writing-skills, Apache-2.0,
riscritte). Il catalogo anti-IA non sta sopra manuale, voce e briefing. Prima riga del rapporto:
`zb ruolo <libro> line-editor N`; il ruolo lavora solo in fase `line`.

## Cosa NON fa
Non cambia i fatti, la struttura, il punto di vista. Non corregge ortografia e grammatica: è il compito del ruolo successivo.

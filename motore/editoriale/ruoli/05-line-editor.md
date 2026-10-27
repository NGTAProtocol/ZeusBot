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

## Taglio avversario (metodo, 2026-10-27)
Il compito è «togli almeno il 10% delle parole del capitolo senza perdere nulla di ciò che serve» (idea di
nousresearch/autonovel, senza file di licenza: solo l'idea, riscritta): ciò che si può tagliare rivela ciò che è debole, e l'elenco dei tagli è il
piano del line editing. Rapporto (al massimo 600 parole):
1. Da 10 a 20 interventi, ognuno: citazione esatta (almeno 10 parole, per trovarla senza dubbi), classe, azione
   (TAGLIA o RISCRIVI; per RISCRIVI la proposta), motivo in una riga. Classi: **spiega** (il narratore spiega ciò che
   la scena ha già mostrato), **ridondante** (ripete una frase o una scena precedente), **superfluo** (non aggiunge
   nulla), **generico** (potrebbe stare in qualunque romanzo), **dice** (nomina un'emozione invece di mostrarla),
   **ritmo** (paragrafo che rompe il passo), **tic** (chiusa a sentenza, eco, battuta giustificativa, soggetto
   ambiguo, elenco di tre).
2. Parole tagliabili in tutto e percentuale.
3. Il passaggio migliore (da non toccare) e il peggiore, citati.
Si applica nell'ordine: prima **spiega** e **ridondante** (di solito più della metà dei tagli), poi il resto.

## Principio
Intervento minimo efficace: se una frase funziona, non si tocca. Si corregge per sottrazione, non per sostituzione;
si rilegge ciò che la correzione introduce; non si aggiungono dettagli che il testo non ha; ambiguità, omissioni e
ripetizioni volute restano (idee di chi-feng/humanizer, MIT, e haowjy/creative-writing-skills, Apache-2.0,
riscritte). Il catalogo anti-IA non sta sopra manuale, voce e briefing. Prima riga del rapporto:
`zb ruolo <libro> line-editor N`; il ruolo lavora solo in fase `line`.

## Cosa NON fa
Non cambia i fatti, la struttura, il punto di vista. Non corregge ortografia e grammatica: è il compito del ruolo successivo.

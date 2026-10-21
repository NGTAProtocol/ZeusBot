# Passaggio di consegne — prova-padre-del-mostro

## Stato
- Ramo `libro/prova-padre-del-mostro`, cartella `libri/prova-padre-del-mostro/`.
- Fase «stesura», gate in attesa «lettura»: PAUSA DI LETTURA dopo la riscrittura dei capitoli 1, 2, 3.
- Capitoli riscritti con la voce aggiornata (banca-voci @ 45927f0, 85 divieti) e accettati da `zb esito`:
  1 (2081 parole), 2 (1675), 3 (2540).
- Capsule 1 e 2 rifatte sui capitoli riscritti e verificate; capsula 3 non fatta (con il gate «lettura» aperto
  `zb agenti prossimo` chiede prima la risposta dell'autore).
- Voce: `sistema-nell-ombra`, ambientazione `altro`.

## Decisioni prese
- Alla pausa precedente l'autore ha risposto «correggi» con le note in `06-diagnostica/note-lettura.md`
  (riscrittura dei capitoli 1-3; Bertola ha avuto parte nel sacrificio di Kurgan; il libro è una suspense;
  capitolo 2 invariato come struttura; canoni e continuità del ragazzo).
- Riscrittura dei capitoli già accettati: `zb prepara N`, scrittore-voce (un subagente per capitolo),
  `zb correggi <libro> N: <motivo>` (correzione fuori dal gate, in `correzioni_registrate`), `zb esito N`,
  `zb riapprova` del capitolo (richiesto da `zb avvio`: i capitoli erano tra i documenti approvati alla pausa),
  capsula rifatta (vecchio file tolto, `zb capsula N`, agente capsula, `--verifica`).
- Codex: canoni confermati (telefoni nelle buste con il numero, Bertola il 31; linee guida in cinque punti;
  sala piccola e bicchieri con gli aloni) in `caserma-squadra.md` e `sede-fondo.md`; «da confermare
  dall'autore» le buste in portineria (`luigi-bertola.md`) e Giorgi che sa a chi Bertola riferisce
  (`alfredo-giorgi.md`). Le quattro schede sono riapprovate con `zb riapprova`.

## Regole da non violare
- Scrivere solo in `libri/prova-padre-del-mostro/`; la banca-voci si legge soltanto.
- Fatti canonici (`stato.yaml`, `fatti_bloccati`) non si cambiano senza il gate «canone».
- Un ruolo per sessione (`ZB_SESSIONE`); chi scrive non rivede.
- Alla pausa di lettura: solo «ok» o «correggi <note>» dell'autore.

## Fatto in questa sessione
- Banca-voci: 17 divieti nuovi (eco, sentenze, riassunti, soprannomi) e regole 2.12-2.14, sezione 3 e
  sezione 7 punti 10-15 nella scheda; `zb voce verifica`: «OK voce sistema-nell-ombra: 7 sezioni, 85 divieti,
  pronta».
- Capitolo 1: KO al primo `zb esito` (frase_media 5.7 fuori da 9-14), una correzione, poi OK (10.9).
- Capitolo 2: KO al primo `zb esito` (scena_minimo: scena 2 791 parole, minimo 800; cifra
  anni-fiducia-bertola-giorgi: «una anni», atteso 13, lettura sbagliata del controllo su «fiducia: una bella
  parola»), una correzione, poi OK.
- Capitolo 3: OK al primo `zb esito`.
- `zb stile`: nessun KO, 4 avvisi della voce (sentenza_lo_fa_chi cap. 1, sentenza_certe_cose_vanno cap. 2,
  soprannome_il_piu ×2 cap. 3).

## Punti aperti
- Capitolo 3: «il vecchio» sostituisce «il più anziano» come etichetta fissa (7 volte nella scena 3,
  4 nella scena 2) e «con la cartella» 3 volte nella scena 3: la regola 2.13 è scritta, nessun pattern la copre.
- Capitolo 3: lo scrittore segnala un dettaglio aggiunto (la macchina di Bertola vista da una finestra).
- Capsula 2 rifatta: non riporta più la promessa @prom:bertola-prossimo-sacrificato della capsula precedente.
- Ripetizioni ravvicinate sopra 12 per mille nei capitoli 1 (13.97) e 3 (12.23).
- Restano aperti: decisione A1 e problema B1 della diagnosi di struttura; contrasto frase media del manuale
  (9-14) e registro corto della voce (5-10); contrasto caporali di `09-scelte-fisse.md` e lineetta del motore;
  campi del briefing non compilati; capsula 3.
- Motore: dopo «correggi» alla pausa lo stato resta su «passo: pausa di lettura» senza gate finché un
  `zb esito` sposta il passo.

## Prossimo passo
L'autore legge `04-manoscritto/01-l-ultimo-appuntamento.md`, `02-la-nomina.md`, `03-la-convocazione.md` e
risponde «ok» oppure «correggi <note>».

## Ripartenza
```
export ZB_BANCA_VOCI=<cartella della banca-voci>
git checkout libro/prova-padre-del-mostro && git pull
python3 -B motore/zb lavoro libro prova-padre-del-mostro
python3 -B motore/zb avvio libri/prova-padre-del-mostro
python3 -B motore/zb stato libri/prova-padre-del-mostro
python3 -B motore/zb agenti prossimo libri/prova-padre-del-mostro
```
Frase di apertura: «Leggi libri/prova-padre-del-mostro/passaggio-di-consegne.md e riprendi dalla pausa di lettura».

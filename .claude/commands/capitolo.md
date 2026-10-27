---
description: "Catena automatica dei capitoli del libro attivo: scrittore, misure, revisione con voto, correzione mirata, esito, capsula, salvataggio, fino alla pausa di lettura. La sessione principale orchestra e non scrive prosa."
argument-hint: "[quanti capitoli al massimo; senza numero: fino alla pausa di lettura]"
disable-model-invocation: true
---

Libro: quello attivo (`python3 motore/zb lavoro stato`), cartella `libri/<slug>/`. Limite: $ARGUMENTS capitoli
accettati (senza numero: fino alla pausa di lettura). Tu orchestri: non scrivi prosa, non leggi capitoli né
rapporti, leggi solo le righe dei comandi e le risposte degli agenti (al massimo 5 righe).

1. Una volta: `python3 -B motore/zb avvio libri/<slug> --ruolo regia` e riporta la riga «Letto». Se si ferma,
   fermati e riporta il motivo.
2. Ripeti:
   a. `python3 -B motore/zb agenti prossimo libri/<slug>` e leggi la riga che comincia con AZIONE o FERMO.
   b. FERMO → riportala all'autore e fermati (pausa di lettura, secondo «non passa», gate aperto).
   c. AZIONE → eseguila esattamente: i comandi `zb` li lanci tu; gli agenti (`scrittore-voce`, `diagnosta`,
      `capsula`) li chiami con cartella del libro, capitolo e file indicati. Al `diagnosta` passi la riga «Prima
      riga» stampata da `zb ruolo`. Allo `scrittore-voce` in correzione passi il rapporto `audit/NN.md` o il KO.
   d. Se un comando si ferma con un KO: una sola correzione mirata dello `scrittore-voce`, poi di nuovo il passo;
      al secondo KO sullo stesso punto fermati e riporta.
   e. Dopo `zb esito` accettato e la capsula del capitolo: `python3 -B motore/zb compatto libri/<slug>`, poi
      `python3 -B motore/zb salva libri/<slug> "capitolo N"` (recinto, commit, push). Se il push fallisce, fermati.
3. Alla fine, in poche righe: capitoli accettati, media della revisione di ciascuno, lezioni nuove, hash dell'ultimo
   salvataggio e «branch allineato a origin: sì/no».
La revisione del manoscritto, il line editing e il copyediting sono fasi successive (`/revisiona`).

<!-- zb: installato da «zb agenti attiva»; fonte: motore/editoriale/ -->

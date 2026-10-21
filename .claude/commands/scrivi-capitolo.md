---
description: "Scrive il capitolo N del libro attivo orchestrando i subagenti (scrittore-voce, capsula); la sessione principale non scrive prosa. Si ferma dopo il salvataggio: la revisione è /revisiona."
argument-hint: "<N>"
disable-model-invocation: true
---

Capitolo da scrivere: $ARGUMENTS. Libro: quello attivo (`python3 motore/zb lavoro stato`), cartella `libri/<slug>/`.
Tu orchestri e non scrivi prosa. Non è una catena in una sola sessione: ogni passo di scrittura o sintesi
lo fa un subagente con il suo contesto pulito. Leggi solo le risposte brevi (al massimo 10 righe).

1. `python3 motore/zb avvio libri/<slug>` e riporta la riga «Letto». Se si ferma, fermati e riporta il motivo.
2. Preparazione: `python3 motore/zb prepara libri/<slug> $ARGUMENTS`. Il comando legge la scheda del capitolo in
   `03-struttura/05-scaletta.md`, filtra il codex per i tag @char e @loc della scena, raccoglie il canone (fatti
   bloccati) e le capsule precedenti, e si ferma se la scheda non ha funzione, conflitto, cambiamento,
   informazione data, gancio, polarità emotiva e sottotesto dei dialoghi. Se si ferma: fermati e segnalalo
   all'autore, senza completare la scheda da solo.
3. Chiama il subagente `scrittore-voce` con: cartella del libro, capitolo $ARGUMENTS, file
   `06-diagnostica/preparazione/NN.md`.
4. `python3 motore/zb esito libri/<slug> $ARGUMENTS`. Con un KO: una sola correzione mirata, sempre dal
   subagente `scrittore-voce`, poi di nuovo esito; al secondo KO si apre il gate e decide l'autore.
5. `python3 motore/zb capsula libri/<slug> $ARGUMENTS`, poi il subagente `capsula` (compila e verifica).
6. `python3 motore/zb compatto libri/<slug>` (stato compatto).
7. `python3 motore/zb salva libri/<slug> "capitolo $ARGUMENTS"`: controllo del recinto, commit e push.
   Riporta hash e «branch allineato a origin: sì/no».
Poi fermati. Niente line editing né copyediting qui: la revisione è un comando separato (`/revisiona`).

<!-- zb: installato da «zb agenti attiva»; fonte: motore/editoriale/ -->

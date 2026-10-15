---
description: "Audit isolato in sola lettura del capitolo N (o della struttura, o del manoscritto) del libro attivo: scrive solo il rapporto in 06-diagnostica/, non tocca il testo."
argument-hint: "<N | struttura | manoscritto>"
disable-model-invocation: true
---

Oggetto: $ARGUMENTS. Libro: quello attivo, cartella `libri/<slug>/`.

1. `python3 motore/zb avvio libri/<slug>` e riporta la riga «Letto».
2. Misure meccaniche, senza ragionamento: per un capitolo `python3 motore/zb antiia libri/<slug> $ARGUMENTS`
   e `python3 motore/zb capitolo libri/<slug> $ARGUMENTS` (scrivono solo report in `06-diagnostica/`).
3. Chiama il subagente `diagnosta` in sola lettura sul capitolo, sulla struttura o sul manoscritto, con le
   regole di `motore/editoriale/diagnosi/`. Per «struttura» e «manoscritto» il rapporto è quello del gate
   (`zb ruolo libri/<slug> diagnosta` gli dà la prima riga); per un capitolo scrive
   `06-diagnostica/audit/NN.md`, fuori dai gate.
4. Nessuna modifica al testo, alla struttura o allo stato: se il diagnosta trova un problema G1, lo riporti
   all'autore e ti fermi.
5. `python3 motore/zb salva libri/<slug> "diagnosi $ARGUMENTS"` (solo il rapporto).
Rispondi con il riepilogo del rapporto in al massimo 10 righe.

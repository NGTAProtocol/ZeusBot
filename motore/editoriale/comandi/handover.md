---
description: "Passaggio di consegne del libro attivo: aggiorna passaggio-di-consegne.md (sette sezioni) e lo stato compatto, salva con commit e push, poi chiede di aprire una nuova chat."
disable-model-invocation: true
---

Libro: quello attivo, cartella `libri/<slug>/`.

Avvertenza: un comando non può azzerare il contesto di questa chat. Questo comando prepara i file perché una
chat nuova riparta da lì; il contesto si azzera solo aprendo una nuova chat.

1. `python3 motore/zb stato libri/<slug>` e `python3 motore/zb compatto libri/<slug>`.
2. Aggiorna `libri/<slug>/passaggio-di-consegne.md` con le sette sezioni, brevi, senza brani del libro:
   Stato; Decisioni prese; Regole da non violare; Fatto in questa sessione; Punti aperti; Prossimo passo;
   Ripartenza (comandi e frase di apertura: «Leggi libri/<slug>/stato-compatto.md e
   libri/<slug>/passaggio-di-consegne.md, esegui zb avvio libri/<slug> e riprendi»).
3. `python3 motore/zb salva libri/<slug> "passaggio di consegne"` e riporta hash e
   «branch allineato a origin: sì/no».
4. Scrivi all'autore una sola riga: apri una nuova chat e incolla la frase di apertura.

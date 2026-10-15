---
description: "Revisione chirurgica del capitolo N nella fase di revisione del libro attivo: line-editor in fase line, correttore-italiano in fase copy, in subagenti separati; applica solo le proposte approvate dall'autore."
argument-hint: "<N>"
disable-model-invocation: true
---

Capitolo: $ARGUMENTS. Libro: quello attivo, cartella `libri/<slug>/`. Tu orchestri; non correggi tu il testo.

1. `python3 motore/zb avvio libri/<slug>` e riporta la riga «Letto».
2. `python3 motore/zb stato libri/<slug>`: la fase decide il ruolo (line editing e copyediting sono fasi diverse,
   in quest'ordine: prima tutta la fase `line`, poi tutta la fase `copy`; durante la stesura non si rivede).
   - fase `line`, proposte: subagente `line-editor` sul capitolo $ARGUMENTS (`zb ruolo libri/<slug> line-editor $ARGUMENTS`
     gli dà la prima riga del rapporto);
   - fase `copy`, proposte: subagente `correttore-italiano` sul capitolo $ARGUMENTS;
   - altra fase: fermati e dillo (il comando `zb ruolo` rifiuta il ruolo fuori fase).
3. Il subagente segnala solo i punti che non rispettano il catalogo anti-IA e i criteri del correttore, con
   riga e proposta, nel rapporto `06-diagnostica/<fase>/NN.md`. Catalogo e criteri sono filtri di qualità:
   non stanno sopra il manuale del libro, la voce e il briefing; una scelta documentata nel manuale vince.
4. Salva il rapporto da solo (`python3 motore/zb salva libri/<slug> "rapporto <fase> $ARGUMENTS"`): mai nello
   stesso commit di una modifica al capitolo.
5. L'autore approva le proposte al gate della fase (`zb pronto` quando tutti i capitoli hanno il rapporto,
   poi `avanti` e `ok`). Solo dopo l'«ok», in sottofase «applicazione», lo stesso tipo di subagente applica
   le sole proposte approvate con modifiche puntuali (Edit), senza riscrivere il capitolo se l'impianto regge;
   poi `python3 motore/zb esito libri/<slug> $ARGUMENTS` e `zb salva`.
Rispondi in poche righe: rapporto scritto, proposte, cosa aspetta l'autore.

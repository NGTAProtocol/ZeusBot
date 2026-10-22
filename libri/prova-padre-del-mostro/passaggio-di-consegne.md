# Passaggio di consegne — prova-padre-del-mostro

## Stato
- Ramo `libro/prova-padre-del-mostro`, cartella `libri/prova-padre-del-mostro/`.
- Fase «stesura», nessun gate aperto: la pausa di lettura è stata chiusa con «correggi 1: …» (17213c4).
- LAVORO FERMATO dall'autore (2026-10-21): nessuna riscrittura di capitoli finché non sono installati gli agenti
  veri. Il capitolo 1 è nella versione aa5b2b6 (riscritta dallo scrittore, NON accettata: niente `zb esito`);
  i capitoli 2 e 3 sono quelli accettati in a7e1c88.
- Revisione del capitolo 1 (giro 1, 6dfca7f, `06-diagnostica/audit/01.md`, prima riga di `zb ruolo … diagnosta 1`
  del motore di `integrazione-editoriale`): «non passa» (2 chiuse, 2 eco, 7 battute giustificative, 2 frasi di
  26 parole, 9 soggetti ambigui di cui 2 su un fatto, battute dello zucchero senza attribuzione). La correzione
  dello scrittore è stata fermata prima di toccare il file.
- `stato.yaml` dice ancora capitoli scritti e approvati fino a 3 (il capitolo 1 riscritto non è registrato).
- 2026-10-22: merge di `origin/motore` (d575b87) nel ramo, commit a74412e: `motore/` ora è il motore unificato
  (contenuto di `integrazione-editoriale` più la correzione di `separazione.py`), al posto della copia 2df84b3.
  36 file, solo `motore/`, `docs/`; nessun conflitto; nessun file del libro né di `.claude/` toccato.
  Verificato dopo il merge: i 12 agenti e i 4 comandi installati in `.claude/` sono identici a quelli che
  `zb agenti attiva` scriverebbe oggi (nessun riallineamento); `dati/modelli-ruoli.yaml` dice diagnosta `leggero`
  (haiku) come l'agente installato; `percorso.py` ha `misure_prima_della_revisione` e `giro_revisione`.

- 2026-10-21, seconda parte: installati in `.claude/` (ee4eab7) i 12 agenti, i 4 comandi e gli hook, con
  `zb agenti attiva --ok` e `zb hook attiva --ok` del motore di `integrazione-editoriale` (`--progetto`). Gli hook
  valgono dalla prossima sessione aperta su questo ramo; in quella dell'installazione non registravano.
- La pagina di prova con gli agenti NON è stata scritta: `zb avvio` si ferma («Documenti approvati cambiati
  fuori procedura … 04-manoscritto/01-l-ultimo-appuntamento.md»), perché il capitolo 1 è la riscrittura aa5b2b6
  non accettata. Serve la decisione dell'autore: `zb riapprova` di aa5b2b6 o ritorno al testo di a7e1c88.

- 2026-10-21, terza parte: capitolo 1 riportato al testo approvato a7e1c88 (7fb201a); `zb avvio` passa.
  Merge di `origin/integrazione-editoriale` nel ramo tentato e ANNULLATO (non pushato): suite 658/661 e
  `separazione.py` KO sul ramo del libro (`.claude/` presente, nomi del libro in `docs/`). Il ramo resta sul motore
  2df84b3; il motore nuovo si usa per percorso dalla cartella di `integrazione-editoriale`.
- Pagina di prova `prova-pagina/apertura.md` (scrittore-voce e diagnosta installati, due giri): giro 1 «non passa»
  (2 chiuse, 2 fatti contraddetti), giro 2 «non passa» (r.27 «Il ragazzo non dice altro.» contraddice il
  capitolo, rr. 47-63). Gli hook non registrano in questa sessione (`CLAUDE_PROJECT_DIR` vuota).

## Decisioni prese
- Nota di lettura del 2026-10-21 per il capitolo 1 (in `06-diagnostica/note-lettura.md`).
- Frase media nel thriller: vale il registro della voce (corto 5-10, freddo 15-25, base 12-18), solo con il motore
  di `integrazione-editoriale`; con quel motore i capitoli 2 (9,1) e 3 (9,6) risultano fuori intervallo.

## Regole da non violare
- Scrivere solo in `libri/prova-padre-del-mostro/`; la banca-voci si legge soltanto.
- Nessuna scrittura di capitoli fino a nuova istruzione dell'autore.
- Un ruolo per sessione; chi scrive non rivede.

## Fatto in questa sessione
- Pausa chiusa con le note (17213c4); `zb prepara 1` con il motore nuovo; riscrittura del capitolo 1 (aa5b2b6:
  1890 parole, frase media 6,0, dialogo 31,7%, nessun avviso di `zb stile`); revisione giro 1 (6dfca7f).

## Punti aperti
- Capitolo 1: decidere se tornare alla versione a7e1c88 o riprendere da aa5b2b6 con il rapporto del giro 1.
- Capsula 1 da correggere (dice che sparano due uomini; nel testo aa5b2b6 spara uno solo); capsula 3 non fatta.
- `motore/` di questo ramo riallineato a `origin/motore` (a74412e). Con il motore nuovo la frase media dei capitoli
  2 e 3 risulta fuori dall'intervallo del registro (avviso, non blocco): da rivedere quando riprende il lavoro.

## Prossimo passo
Nessuno finché l'autore non lo indica.

## Ripartenza
```
export ZB_BANCA_VOCI=<cartella della banca-voci>
git checkout libro/prova-padre-del-mostro && git pull
python3 -B motore/zb lavoro libro prova-padre-del-mostro
python3 -B motore/zb avvio libri/prova-padre-del-mostro
python3 -B motore/zb stato libri/prova-padre-del-mostro
```
Frase di apertura: «Leggi libri/prova-padre-del-mostro/passaggio-di-consegne.md: il lavoro sui capitoli è fermo».

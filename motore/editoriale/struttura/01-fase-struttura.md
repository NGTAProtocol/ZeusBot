# Fase STRUTTURA

Prima fase dopo il briefing. Nessun documento, nessuna pagina di prosa prima che la struttura sia approvata.

## Ruolo
Architetto della struttura (vedi `ruoli/02-architetto-struttura.md`).

## Input
`briefing.md`, `libro.yaml`, profilo di genere, scheda della voce (se c'è).

## Output in `03-struttura/` del libro
1. `01-premessa.md` - premessa e promessa al lettore, una pagina. Chi è il lettore, cosa gli promette il libro, perché lo finirà.
2. `02-logline-tema.md` - logline in una frase; tema centrale e controtema.
3. `03-personaggi-chiave.md` - protagonista, antagonista (o forza antagonista), posta in gioco, ferita o mancanza, desiderio e bisogno, arco di trasformazione.
4. `04-atti-svolte.md` - atti e punti di svolta, con i valori del profilo di genere (lunghezza, proporzioni).
5. `05-scaletta.md` - un blocco per capitolo (vedi `modelli/scaletta-capitolo.md`).
6. `06-sottotrame-temi.md` - dove ogni sottotrama e promessa si apre, si sviluppa, si chiude.
7. `07-tensione-ritmo.md` - curva di tensione capitolo per capitolo; dove si respira.
8. `08-piano-parole.md` - parole per capitolo e totale.
9. `09-scelte-fisse.md` - punto di vista, tempo verbale, voce: fissati prima della prosa.

## Controlli prima del gate
- ogni capitolo ha funzione, conflitto, cambiamento, informazione data, gancio;
- ogni promessa aperta ha un pagamento;
- nessun capitolo "di passaggio" senza cambiamento;
- punto di vista, tempo verbale e voce sono scritti in `09-scelte-fisse.md` e non si cambiano dopo senza gate;
- la fine è coerente con la promessa.

## Revisione
Prima il diagnosta (sessione separata) scrive `06-diagnostica/contratto.md` e `06-diagnostica/rapporto-struttura.md`;
poi l'editor strutturale (sessione separata) legge solo `03-struttura/`, il briefing e il rapporto e scrive
`06-diagnostica/piano-revisione-struttura.md`: punti forti, problemi in ordine di gravità, proposte. Non riscrive la
struttura. I rapporti stanno in commit che non toccano `03-struttura/` (lo controlla `zb pronto`).

## Gate `struttura`
L'autore risponde `ok`, `correggi` o `avanti`. Con `correggi`, l'architetto applica solo le correzioni richieste.

## Note per il motore
- `zb nuovo` crea i nove file con la riga `<!-- zb: modello -->`; l'architetto la toglie a file scritto (`zb pronto`
  rifiuta i file che la contengono ancora; `zb struttura <libro> verifica` dice cosa manca).
- `05-scaletta.md` comincia con la tabella `| Unità | Data | Contenuto | Chiusura |`; `08-piano-parole.md` ha le colonne
  `Cap.` e `Budget capitolo` (le leggono gli script).
- `04-atti-svolte.md` dichiara `Macrostruttura:` (una tra 3 atti, 4 atti, 5 atti, dittico, in medias res, mosaico,
  slow-burn, circolare) e `Motivo:`. Le svolte non stanno sui quarti esatti per regola; numero e lunghezza dei capitoli
  nascono dal contenuto (budget non tutti uguali); niente etichette automatiche «Atto 1/2/3». `zb esito` segnala
  capitoli di lunghezza quasi uguale.

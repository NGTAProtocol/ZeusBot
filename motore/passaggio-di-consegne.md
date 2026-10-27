# Passaggio di consegne: motore

Frase di apertura per la nuova chat: «Leggi motore/passaggio-di-consegne.md e riprendi da lì». La storia completa
delle sessioni precedenti è in git (`git log`, ramo `archivio/motore-prima-2026-10-27` per i documenti di allora).

## Stato (2026-10-27)
- Catena automatica dei capitoli: `/capitolo` (ruolo `regia`; `zb agenti prossimo` dà una sola AZIONE o FERMO);
  scrittore, diagnosta, direttore editoriale, line editor, lettore cieco, voce e grafico su Opus; correttori su
  Sonnet; capsule su Haiku (`dati/modelli-ruoli.yaml`).
- Revisione del capitolo con sette voti tarati, `Media` e `soglia_qualita` (7.5) controllata da `zb esito`; lezioni
  in `06-diagnostica/lezioni.md` allo scrittore; revisione del manoscritto con critico, professore e panel di quattro
  lettori; editor strutturale con classi di intervento; line editing con il taglio avversario.
- Voce del libro dalle pagine campione (`00-progetto/voce/`, anche ibrida): `zb voce campioni`, agente `voce`,
  `zb voce scheda`; anti-copia a 7 parole (`copia:campione_voce`).
- Grafica: stili dell'interno (`formato.stile`), agente `grafico` (quarta, brief), `zb copertina` (copertina intera
  KDP in PDF, misura esatta; dati in `dati/kdp.yaml`, sezione «copertina», da verificare).
- Soglie di stile informative (`soglie_stile`); bloccano fatti oggettivi e il voto sotto soglia.
- Tolti: traduzione (codice, agenti, prove), `zb adotta`, documenti superati di `docs/`, esiti storici delle prove.
- Suite: `ZB_LANGUAGETOOL=<cartella>/lib python3 -B motore/zb prove` (dalla radice); impronta per `zb push` sul
  motore solo con la suite intera tutta OK.

## Decisioni prese
- Modo automatico: fermate solo alla pausa di lettura, a un FERMO del motore e al canone (`editoriale/00-percorso.md`).
- Opus dove si scrive o si giudica; il consumo si contiene con letture minime e risposte di 5 righe.
- Voce: si imita il modo dei campioni, mai il testo.
- Dati KDP (anche la copertina): validi solo dopo la verifica dell'autore (`zb verifica KDP fatta AAAA-MM-GG`).

## Regole da non violare
- Il ramo `motore` non contiene mai un libro; nessun nome reale (titoli, personaggi, luoghi, nomi dei rami dei
  libri) in `motore/`, `docs/`, `CLAUDE.md` (`zb separazione`).
- Lavoro sul motore solo dopo «lavoro sul motore» dell'autore (`zb lavoro motore`); salvataggio con commit e push,
  mai push forzati né storia riscritta.
- Chi scrive non rivede (agenti diversi; scritture registrate per «sessione:agente»).

## Punti aperti
- Provare `/capitolo` su un libro vero e tarare `soglia_qualita` dopo 3 capitoli.
- Verifica dei dati KDP da parte dell'autore, compresa la sezione «copertina».
- Su origin resta un ramo d'archivio creato per errore il 27 ottobre da un ramo di libro (quello senza «prima» nel
  nome): da cancellare dal sito (l'ambiente cloud non permette di cancellare rami remoti). Finché c'è, il suo nome è
  vietato nel motore.

## Ripartenza
```
python3 -B motore/zb lavoro motore
python3 -B motore/zb avvio
ZB_LANGUAGETOOL=<cartella>/lib python3 -B motore/zb prove
```

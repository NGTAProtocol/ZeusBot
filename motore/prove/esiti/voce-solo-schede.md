# Banca-voci con sole schede: esito

Data: 2026-10-13. Ramo motore, partendo da 80d7f46.

## Regola

Il motore è generico e vale per qualsiasi libro. La banca-voci contiene solo schede di voce e divieti:
niente pagine di libri, manoscritti, nomi di romanzi, personaggi o luoghi reali, né nel motore né nella
banca. Il contenuto di ogni libro lo decide l'autore nel briefing.

## Correzioni al motore (commit di pulizia)

- `voce.py`: `zb voce verifica` non richiede più pagine d'esempio. Controlla: voce nell'indice, scheda
  presente con le 7 sezioni e il campo «ambientazione:», `divieti.yaml` leggibile, stato «pronta».
- `prove/banca-voci-prova/`: tolte le cartelle `esempi/` della mini-banca inventata.
- `README.md`, `report-motore.md`, `passaggio-di-consegne.md`: niente pagine d'esempio; il punto aperto
  sulle voci nuove è ora «le voci si aggiungono in banca-voci quando l'autore lo decide», senza nomi.

## Prove cambiate (perché cambia il requisito, non per farle passare)

| Prova | Prima | Dopo | Motivo |
|---|---|---|---|
| (a) verifica della voce pronta | «7 sezioni, 2 esempi, 3 divieti, pronta» | «7 sezioni, 3 divieti, pronta» | gli esempi non fanno più parte della verifica, quindi l'uscita non li conta |
| (c) scheda rotta | «un solo esempio» → KO | «scheda assente» → KO | il requisito «≥ 2 esempi» non esiste più: la prova che lo controllava non ha più oggetto; al suo posto si prova l'altro requisito di file, la scheda presente |

Tutte le altre prove della sezione «voce» sono invariate. Totale invariato: 25 nella sezione, 454 in tutto.

## Suite

`ZB_LANGUAGETOOL=<cartella>/lib ZB_BANCA_VOCI=<banca-voci> python3 -B motore/zb prove`:
**454/454 OK**, 0 saltate. `separazione.py` OK, `recinto.py` OK (48 esecuzioni).

## Regressione sulla banca reale

Tolta la sezione 5 dalla scheda di una delle due voci pronte: `zb voce verifica` → codice 1,
«sezione 5 «Adattamento per genere» mancante». Scheda ripristinata: codice 0, «7 sezioni, 90 divieti,
pronta». L'altra voce: «7 sezioni, 60 divieti, pronta». I campioni-modello delle due schede non
contengono espressioni dei rispettivi `divieti.yaml`.

## Controllo dei nomi reali

Grep su tutti i file tracciati del motore e su `CLAUDE.md`, con i titoli, gli autori e i nomi propri
letti in memoria dai rami dei libri su origin (la lista non è salvata nel repository): nessun nome di
libro, autore o personaggio reale. Le sole coincidenze sono parole comuni della lingua (usate nel loro
senso normale) e nomi inventati di un ramo di prova, già usati nei mini-libri inventati.

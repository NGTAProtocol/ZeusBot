# Voci narrative dalla banca-voci: esito

> Superato in parte da `voce-solo-schede.md`: le pagine d'esempio non sono più richieste né presenti.

Data: 2026-10-13. Ramo motore, partendo da b36a438.

## Correzioni al motore

| Commit | Cosa |
|---|---|
| fd404a8 | `voce.py` e `zb voce lista / mostra / verifica`; `ZB_BANCA_VOCI` (README, «Banca-voci»); blocco `voce: {slug, ambientazione}` in schema, modello e `zb nuovo`; «Letto» di `zb avvio` con briefing e scheda della voce, AVVISO se la voce non verifica; divieti della voce in `stile.py` (modalità avviso); regola in CLAUDE.md; `voce.py lista` tra i comandi di `recinto.py` |
| 783216e | `modelli/briefing.md`: Storia, Schede dei personaggi («sempre», «quasi sempre», «mai»), Luoghi ed epoca, Regole del libro, Voce scelta e ambientazione; esempio inventato dentro un commento |
| e619bcf | prove della sezione «voce» (+25) sulla mini-banca inventata `prove/banca-voci-prova/` |

I libri senza il blocco `voce` restano identici: stessa uscita di `zb avvio` con e senza
`ZB_BANCA_VOCI`, nessun divieto in più in `zb stile`.

## Prove (`script/prove.py`, sezione «voce»)

| Gruppo | Prove | Copre |
|---|---|---|
| (a) | 7 | lista, mostra (blocco, 7 sezioni), mostra di una voce non pronta (avviso), blocco inesistente, verifica OK, verifica della voce non pronta (KO), voce assente dall'indice (FERMO) |
| (b) | 2 | senza `ZB_BANCA_VOCI` (lista, mostra, verifica: FERMO con il nome della variabile), cartella senza `indice.yaml` |
| (c) | 5 | scheda rotta: `divieti.yaml` non leggibile, sezione 4 tolta, «ambientazione:» tolta, un solo esempio; scheda ripristinata: OK |
| (d) | 1 | libro senza voce: avvio identico con e senza la variabile, nessuna voce in «Letto» |
| (e) | 4 | briefing con la voce → blocco in `libro.yaml`; «Letto» con scheda e briefing (11 file, 0 avvisi); senza variabile: AVVISO; voce non pronta: AVVISO, non blocco |
| (g) | 3 | divieti della voce in `stile.py`: libro senza voce (niente), senza banca (niente), con voce e banca (3 AVVISO) |
| (f) | 3 | voce senza slug rifiutata dallo schema; `zb aiuto` elenca `zb voce`; modello del briefing (sezioni nuove, campi della voce, esempio fuori dai dati) |

Nessun traceback in nessun caso d'errore.

## Suite

`ZB_LANGUAGETOOL=<cartella>/lib ZB_BANCA_VOCI=<banca-voci> python3 -B motore/zb prove`:
**454/454 OK**, 0 saltate (429 di prima + 25). `separazione.py` OK, `recinto.py` OK (48 esecuzioni).

## Prova di regressione sulla banca reale

Sulla banca-voci reale (fuori dal repository), tolta una sezione dalla scheda della voce pronta:
`zb voce verifica` → codice 1, «sezione 3 «Ritmo e sintassi» mancante». Scheda ripristinata: codice 0,
«7 sezioni, 5 esempi, 60 divieti, pronta». Controllo finale: nessuna delle 5 pagine-modello contiene
espressioni di `divieti.yaml`; parole guida entro 1 ogni 120 parole; 290-316 parole per pagina.

## Separazione

Nel motore solo la mini-banca inventata (voci, frasi e nomi inventati). Le voci reali, le loro
pagine-modello e gli eventuali brani di manoscritti stanno solo nella banca-voci.

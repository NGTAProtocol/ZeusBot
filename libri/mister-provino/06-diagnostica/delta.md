# Ricontrollo — differenze dall'audit (ffed613)

Motore 8c3784a (unito in 79f81c2). Comandi: compila, continuita, stile. Parole: 77.192 (zb conta); .md completo 77.569 (prima 77.520), sha256 69e068b6b36f6c3ce113a73fdcf4275b648b0cadff70a91999ffe42e522a0098.

## Scomparsi
- 38:45 Michele a Genova per il visto contro 40:15 e 41:17 «mai oltre Foggia»: visto per posta.
- 11:69 «tre giorni prima» → quattro; 18:137 «dieci» → dodici; 27:41 «a ottobre» → dieci giorni prima.
- 20:23 «La quarta mattina, il sabato» (venerdì) → «Dopo la quarta notte, il sabato»: il nuovo controllo lo trovava, ora 0.
- 25:101 Saro «tre anni in più» → sei; 39:19 «la sera del vino» → «la sera che venne da Michele».
- 3:65 Checco in cucina → falegnameria; 36:31 e 37:21 tenda della cucina → coperta militare della branda.
- 14:43 «la prima notte» → «la mattina della nave ferma»; 36:83 «uagliò» → «uagnò» (voce guaglio_napoletano: 0 KO).
- 4 «che di cui»; 43 «Questo è olio»; 41 «Fino a ieri»; eco prologo:7 / interludio IX:7 variata (riciclo 0).
- Motore: titoli dei capitoli in compila (ora «1. Pane e Pomodoro», 0 avvisi); fase.py 412 (catena sha256).

## Nuovi
- Nessun KO. continuita: 0 KO, 0 avvisi (prima: 0 KO; con i controlli nuovi, sul testo dell'audit 1 avviso, 20:23).
- Controlli nuovi sul libro: tempi relativi 0, differenze d'età 0, fatti_incompatibili 0 (nessuno dichiarato in libro.yaml).
- 39: avviso di riciclo «carlo la sera che venne da michele» (eco del 35, formula indicata dall'autore).

## Invariati
- stile: 2 avvisi, frase media interludio V 9,9 e VI 7,7 (intervallo 10-13).
- Bibbia 5.7: la cifra a Genova (168) non è detta nel cap. 40. Epilogo −9,4% sul budget.
- Orari oltre il tetto in 13, 18, 26, 28 e tic: proposte in proposte/tetti.md e proposte/tic.md, non applicate.

## Limiti dei controlli nuovi
- Tempi relativi: avviso solo se nessuna data nota coincide; in periodi fitti di date un numero sbagliato può
  cadere su un altro giorno datato (sul testo dell'audit 11:69 e 18:137 non sarebbero stati trovati).
- Differenze d'età: solo tra personaggi con nascita in cronologia (Saro non c'è).

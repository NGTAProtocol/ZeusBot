# Banca-voci: ripristino dal bundle e cartelle «materiali»: esito

Data: 2026-10-13. Ramo motore, partendo da d4b4833.

## Ripristino

- Bundle caricato dall'autore: sha256 `9b9718fe…dada3b`, combacia. `git bundle verify`: storia completa.
- Clonato in `/home/user/banca-voci`, ramo `main`: due commit (eba0658, a22b018 = HEAD), due voci
  (`atkinson-2-0`, `ibrida-pasolini-camilleri`). Nessun file esistente modificato. Tolto il remote
  `origin` che puntava al file del bundle.
- `export ZB_BANCA_VOCI=/home/user/banca-voci` (scritto nella «Ripartenza» di `passaggio-di-consegne.md`).

## Cartelle «materiali» (nella banca, non nel motore)

Commit 896e7f4 nella banca: `voci/<slug>/materiali/LEGGIMI.md` per le due voci, un solo file per
cartella, che dice che lì l'autore mette, quando vuole, brani, interviste e scritti da cui ricavare la
voce, che nessuno li scrive al suo posto e che non vanno mai nel motore. `zb voce verifica` ignora la
cartella: entrambe le voci restano OK («7 sezioni, 60 divieti, pronta» e «7 sezioni, 90 divieti, pronta»).

Nuovo bundle (HEAD e `main` = 896e7f4), mandato all'autore come file:
sha256 `a5d3ad1d648d77cc3d8cdc7308a5d979a2d66b2a70df40cf5c42e77e7992bffe`.

## Motore

`zb voce` esiste già (fd404a8): la parte sul motore non è stata rifatta. Nessun file di codice o di
prova modificato.

## Suite

`ZB_LANGUAGETOOL=<scratchpad>/lt/lib ZB_BANCA_VOCI=/home/user/banca-voci python3 -B motore/zb prove`,
eseguita una volta: **454/454 OK**, 0 saltate. `separazione.py` OK, `recinto.py` OK (48 esecuzioni).

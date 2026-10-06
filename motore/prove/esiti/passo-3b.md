# Passo 3b — Rifiniture: esito

Data: 2026-10-02.

1. In passo-3.md ho corretto i numeri di righe: compila.py 102, impagina.py 176, verifica_pdf.py 199, modello.css 35, print.js 12.
2. In stampa/font/FONTI.yaml c'è ora il modo in cui sono state ricavate le istanze statiche: strumento e versione (fontTools 4.66.1, Python 3.11.15), comando, data (2026-10-02), elenco delle tre istanze e la nota sul nome PostScript.
3. La tabella KDP dei margini è stata spostata in dati/kdp.yaml (sezione `cartaceo`), che ora è l'unica fonte. comune.py non ha più valori propri e si ferma se il file o la sezione mancano.
4. zb prove: 127/127 OK; separazione.py e recinto.py OK.

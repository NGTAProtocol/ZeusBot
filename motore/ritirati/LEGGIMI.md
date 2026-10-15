# Script ritirati

Cartella di passaggio: qui si sposta uno script prima di eliminarlo, con le sue prove e i suoi attesi,
per verificare che il ritiro sia completo. Dopo la verifica la cartella si copia sul ramo
`archivio/motore-ritirati` e si toglie dal ramo `motore`. Motivi in `docs/ANALISI_REPOSITORY.md`.

- `pulizia.py`: `zb pulizia <libro> [--applica]`, elenco di temporanei, cartelle vuote e copie.
  Prove: `prove-pulizia.py` (da `passo_6` di prove.py); attesi: `attesi-pulizia.yaml`.

Verifica di completezza (2026-10-15): le 6 prove di `prove-pulizia.py`, eseguite con lo script di questa
cartella (PYTHONPATH=motore/script per comune.py) e gli attesi di `attesi-pulizia.yaml`: 6/6 OK.

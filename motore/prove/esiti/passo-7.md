# Passo 7 — ortografia: resoconto

Prove: `zb prove` **298/298 OK, 2 saltate** (le due di LanguageTool, senza `ZB_LANGUAGETOOL`;
non contate nel totale). Con `ZB_LANGUAGETOOL` impostata su una copia temporanea di LanguageTool
le 11 prove del passo 7 danno 11/11 OK. Separazione OK; recinto OK (46 esecuzioni).
Nomi dei libri reali in `motore/`: 0.

## File
- Nuovi: `script/ortografia.py`, `dati/parole-ammesse-it.txt` (80 forme dei verbi sedere,
  possedere, soprassedere che il dizionario it_IT non conosce; nessun nome).
- Modificati: `README.md` (percorso in 8 righe, un comando per riga), `PROCEDURA.md` (ortografia e
  LanguageTool da Maven Central), `script/prove.py` (passo_7 e prove «saltate»), `prove/attesi.yaml`,
  `script/recinto.py`, `prove/esiti/passo-6.md` (nomi dei rami resi neutri).

## Livelli
- (a) Hunspell it_IT: sempre. Sul mini-libro giallo segnala solo «Brena», la seconda grafia messa
  apposta al passo 2; sul romance nulla; sui refusi inventati «errrore» e «registo», non «sedette»
  né le elisioni.
- (b) LanguageTool 6.8: solo con `ZB_LANGUAGETOOL`. Scaricato da Maven Central (Java 21 e Maven già
  presenti) in una cartella temporanea fuori dal repository, 240 MB; languagetool.org mai usato.
  Trova gli stessi refusi; non segnala «e» per «è» né «Lui sono andato».
- (c) Checklist manuale in fondo al report, con la nota sui limiti dei correttori automatici.

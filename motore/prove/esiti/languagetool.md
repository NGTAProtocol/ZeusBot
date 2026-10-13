# LanguageTool attivo nelle prove: esito

Data: 2026-10-13. Ramo motore, partendo da d4b6fa6.

## Ambiente

| Strumento | Esito |
|---|---|
| Java | OpenJDK 21.0.12.1 (già presente) |
| Maven | già presente |
| LanguageTool | 6.8, `languagetool-commandline` + `language-it` da Maven Central, 143 file, 240 MB, nello scratchpad (fuori dal repository) |
| PyMuPDF, markdown | assenti nel container nuovo; installati con pip (PyMuPDF 1.28.2) |
| Hunspell it_IT | assente nel container nuovo; installato con apt (`hunspell`, `hunspell-it`) |

## Le 2 prove saltate

`passo_7` in `script/prove.py`: «LanguageTool sui refusi inventati» e «LanguageTool: livello eseguito
nel report». Vengono saltate quando `ZB_LANGUAGETOOL` non è impostata, perché `ortografia.py` trova
i `.jar` solo tramite quella variabile.

Con `ZB_LANGUAGETOOL` impostata passano tutte e due: segnalate `['Brena', 'errrore', 'registo']`,
livelli «sì / sì / sì». Non è servito correggere né il motore né le prove.

## Modifiche

- `script/prove.py`: il motivo dello skip ora è «LanguageTool assente (ZB_LANGUAGETOOL non impostata)».
  In fondo all'output c'è una riga per ogni motivo, con il numero di prove saltate e le istruzioni di installazione.
- `README.md`: nuova sezione «Ambiente», con la sottosezione «LanguageTool» (metodo d'installazione).

## Esito della suite

- Con LanguageTool: **420/424 OK, 0 saltate, 4 KO**.
- Senza: 418/422 OK, 2 saltate (LanguageTool assente), 4 KO.

I 4 KO sono tutti del passo 3 e compaiono anche senza LanguageTool. Non dipendono da queste modifiche:

| Controllo | Atteso | Ottenuto |
|---|---|---|
| mini-libro: sha256 del PDF | cecd5860… | 3346029c… |
| mini-libro-romance: sha256 del PDF | 9e54c302… | 992a9603… |
| mini-libro-romance: margine interno | 0.665 | 0.667 |
| mini-libro-romance: margine esterno | 0.624 | 0.625 |

Cosa è stato verificato:

- Chromium (Playwright 1.56.1, chromium-1194), PyMuPDF 1.28.2, i font e il .md compilato sono
  gli stessi registrati nel passo 3.
- La differenza nasce già nel PDF prodotto da Chromium, prima di PyMuPDF.
- Non cambia con le versioni 3.8.2-3.11 di `markdown`, né installando `fontTools` e `brotli`.
- Due generazioni consecutive danno ancora lo stesso sha256.

Gli attesi del passo 3 (sha256 e margini al millesimo di pollice) dipendono dal container in cui
Chromium ha fatto il render. Non sono stati modificati: la decisione spetta all'autore.

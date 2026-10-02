# Passo 2b — Rifiniture: esito

Data: 2026-10-02.

1. **solo_dialogo: implementato** in stile.py (non rifiutato dallo schema). Una voce con `solo_dialogo: true` è ammessa solo nelle righe di dialogo, cioè quelle che cominciano con la lineetta di lingue.yaml. Ogni riga di narrazione che la contiene è KO (`voce:<id>:fuori_dialogo`), e nel dialogo vale la modalità della voce. Prova: voce «registro» su una copia del giallo, con KO sulle 7 righe di narrazione del cap. 1 e nessun esito sulle 2 righe di dialogo.
2. **Checklist manuale nel report di capitolo.py**, con la casella «verificato dall'autore». Contiene i 4 tic che il motore non rileva (05-critica r. 20: meteo all'inizio, domande retoriche in serie, chiusure di paragrafo con morale, scena che finisce con una presa di consapevolezza) e le voci della bibbia toccate dal capitolo. Prova: 4 tic con casella nel report.
3. **Le tre modifiche al mini-libro giallo** sono spiegate in passo-2.md. In più c'è una prova del ramo `obbligatorio_in`, rimasto senza prova dopo la modifica.
4. **zb prove: 87/87 OK.** Le 83 prove di prima restano tutte OK; le 4 nuove sono solo_dialogo ×2, checklist e nome obbligatorio. separazione.py e recinto.py OK.

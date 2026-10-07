# Motore: da correggere (elenco, non ancora corretto)

Trovato durante la stesura di Mister Provino. Le correzioni si fanno sul ramo `motore`, a parte.

- **Piano parole approvato.** `03-architettura/piano-parole.md` è tra i documenti approvati al gate «documenti»: ogni aggiornamento delle parole reali cambia lo sha256 e richiede `zb riapprova` (un commit in più). Il piano dovrebbe restare il budget approvato; le colonne «Parole reali» e «Scarto» dovrebbero stare in un file di stato (per esempio `stato.yaml` o un file scritto da `zb esito`).
- **`motore/script/fase.py`, riga 407.** Lo stato si salva dopo le stampe: se l'uscita viene chiusa (per esempio con una pipe), `zb esito` stampa «controlli OK» ma non aggiorna `stato.yaml`.
- **`motore/script/continuita.py`, righe 272-281 (nomi in due grafie).** Confronta con i nomi propri anche le parole comuni maiuscole a inizio frase: avvisi falsi come «Torno»/«Torino», «Parlo»/«Paolo», «Piano»/«Pino».
- **`motore/script/riciclo.py`, riga 57.** Le battute canoniche del manuale devono essere escluse dall'anti-riciclo: oggi la dedica «Al mio amico Beniamino, con affetto», insieme alla parola vicina, forma 7 parole uguali al vecchio testo e dà KO.
- **`motore/script/fase.py`, riga 299.** `zb correggi` vale solo a un gate aperto: una correzione chiesta dall'autore fuori da un gate (per esempio al capitolo 10, a lotto finito) non si può registrare.

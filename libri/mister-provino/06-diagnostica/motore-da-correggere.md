# Motore: da correggere (elenco, non ancora corretto)

Trovato durante la stesura di Mister Provino. Le correzioni si fanno sul ramo `motore`, a parte.

- Il piano parole (`03-architettura/piano-parole.md`) è tra i documenti approvati al gate «documenti»: ogni aggiornamento delle parole reali cambia lo sha256 e richiede `zb riapprova` (un commit in più a ogni capitolo). Il piano dovrebbe restare il budget approvato.
- Le colonne «Parole reali» e «Scarto» dovrebbero stare in un file di stato (per esempio `stato.yaml` o un file di diagnostica scritto da `zb esito`), non nel piano parole approvato.

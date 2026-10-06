# Passo 5b — zb adotta: resoconto

Prove: `zb prove` **277/277 OK** (18 nuove); separazione OK; recinto OK (42 esecuzioni).

## File
- `script/adotta.py` (nuovo): bozze di libro.yaml, stato.yaml, cronologia.yaml, nomi_propri.txt e
  06-diagnostica/adozione.md da documenti esistenti, con fonte file:riga e override con motivo.
- `prove/mini-libro-adozione/` (nuovo, inventato): bibbia, manuale, scaletta, un capitolo; nessun libro.yaml.
- Modificati: `zb` (comando adotta), `PROCEDURA.md` (sezione 3b con esempio neutro),
  `script/prove.py` e `prove/attesi.yaml` (sezione passo_5b), `script/recinto.py` (adotta).

## Prove (tutte OK)
Documenti parziali: 5 file scritti, nessuna scrittura fuori; 19 valori tutti con fonte;
non ricavati elencati (autore, formato, copyright, piano parole); override frase_media con la
riga del manuale; libro.yaml senza autore segnalato non valido; cronologia 2 nascite e 3 date;
fase documenti senza gate. Seconda esecuzione: nulla sovrascritto. Documenti completi: valido e
gate «documenti» aperto. 01-originale presente: riscrittura. Cartella vuota: fermo.

## Scelte
- Valori senza fonte possibile (formato, testo di fantasia del copyright) entrano col valore
  standard del motore e sono elencati come «da confermare».
- Se mancano documenti il gate non si apre; con tutti i documenti adotta apre direttamente il
  gate «documenti» (niente approvato: si approva con avanti/ok).

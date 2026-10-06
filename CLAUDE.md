# Regole di avvio

Per qualsiasi lavoro su un libro leggi `motore/PROCEDURA.md` e il `LEGGIMI.md`
del libro indicato. Il libro lo indica l'autore con un percorso: se manca,
chiedilo prima di toccare qualunque file.

Prima di scrivere: esegui `python3 motore/zb avvio <libro>` e riporta la riga
«Letto: …». Se si ferma, fermati anche tu e riporta il motivo.

Il motore legge solo `motore/` e la cartella del libro indicato, e scrive solo
dentro quella cartella.

Precedenza: manuale del libro (e libro.yaml) > procedura del motore > skill
dell'autore. Segnala ogni contrasto.

Metodo: proponi → l'autore approva → applica. Mai approvare da solo.
Risposte dell'autore: ok, avanti, correggi: …, stato (vedi PROCEDURA.md).

Ramo: solo quello assegnato dalla sessione, letto da git.

Tono: il testo precedente di un libro è un registro dei fatti, non va
commentato né giudicato.

Blocco di salvataggio a ogni passo: git add, commit, push, git status -sb,
git log -1. Se il push fallisce o un file non si salva: fermati e riporta
l'errore. Non dire «fatto» se non è su origin. Resoconto con hash, file e
«branch allineato a origin: sì/no».

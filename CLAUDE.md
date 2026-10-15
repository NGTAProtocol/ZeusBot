# Regole di avvio

Regola madre: il motore resta sempre pulito; il ramo `motore` non contiene mai un libro.
Per ogni briefing nuovo: prima azione «zb nuovo», che crea la cartella del libro. Da quel
momento scrivi solo nella cartella del libro, sottocartelle comprese; mai in motore/, nella
banca-voci o altrove. Briefing, voce scelta e report di sessione stanno nella cartella del libro.
Recinto: l'hook blocca le scritture fuori dal libro attivo; solo se l'autore scrive «lavoro sul
motore»: `zb lavoro motore`. Percorsi: `motore/passaggio-di-consegne.md`.

Per qualsiasi lavoro su un libro leggi `motore/PROCEDURA.md` e il `LEGGIMI.md` del libro
indicato (un percorso: se manca, chiedilo prima di toccare qualunque file).
Prima di scrivere: `python3 motore/zb avvio <libro>` e riporta la riga «Letto: …»; se si
ferma, fermati e riporta il motivo. Prima di ogni capitolo: zb avvio, rileggi la scheda della
voce (se libro.yaml ha «voce»: zb voce mostra <slug>) e il briefing.
Il motore legge solo `motore/`, la cartella del libro indicato e la banca-voci (`ZB_BANCA_VOCI`, sola lettura).

Report di sessione ogni 5 scambi o a «passaggio»: nella cartella del libro
(passaggio-di-consegne.md), mai in motore/; `motore/passaggio-di-consegne.md` solo per il
lavoro sul motore. Sezioni: Stato; Decisioni prese; Regole da non violare; Fatto in questa
sessione; Punti aperti; Prossimo passo; Ripartenza (comandi e frase di apertura).

Precedenza: una sola scala, in `motore/editoriale/LEGGIMI.md`; segnala ogni contrasto.
Metodo: proponi → l'autore approva → applica; mai approvare da solo.
Risposte dell'autore: ok, avanti, correggi: …, stato (PROCEDURA.md). Ramo: quello della
sessione, letto da git. Tono: il testo precedente è un registro dei fatti, non si giudica.

Blocco di salvataggio a ogni passo: git add, commit, push, git status -sb, git log -1. Se il
push fallisce o un file non si salva: fermati e riporta l'errore. Non dire «fatto» se non è
su origin. Resoconto con hash, file e «branch allineato a origin: sì/no».

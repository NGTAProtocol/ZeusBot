# Regole di avvio

Regola madre: il motore resta sempre pulito; il ramo `motore` non contiene mai un libro.
Per ogni briefing nuovo: prima azione «zb nuovo», che apre una sola cartella del libro. Da quel momento
scrivi solo nella cartella del libro, sottocartelle comprese; mai in motore/, nella banca-voci o altrove.
Recinto: hook su Write/Edit/Bash, controllo pre-commit e `zb avvio` rifiutano i file fuori dal libro attivo;
solo se l'autore scrive «lavoro sul motore»: `zb lavoro motore`. Percorsi: `motore/passaggio-di-consegne.md`.

Per qualsiasi lavoro su un libro leggi `motore/PROCEDURA.md` e il `LEGGIMI.md` del libro indicato
(un percorso: se manca, chiedilo prima di toccare qualunque file). `docs/` non si legge durante il lavoro.
Prima di scrivere: `python3 motore/zb avvio <libro>` e riporta la riga «Letto: …»; se si ferma, fermati e
riporta il motivo. Nelle sessioni nuove leggi lo stato compatto del libro e la scheda del capitolo.
Il motore legge solo `motore/`, la cartella del libro indicato e la banca-voci (`ZB_BANCA_VOCI`, sola lettura).

Percorso da casa editrice: `motore/editoriale/00-percorso.md`. La sessione principale orchestra e non
scrive prosa: chiama l'agente del ruolo (un subagente per capitolo) e legge solo la sua risposta breve.
Chi scrive non rivede. Comandi: `zb aiuto` (fonte unica: motore/dati/comandi.yaml).

Report di sessione ogni 5 scambi o a «passaggio»: nella cartella del libro (passaggio-di-consegne.md),
mai in motore/. Sezioni: Stato; Decisioni prese; Regole da non violare; Fatto in questa sessione;
Punti aperti; Prossimo passo; Ripartenza (comandi e frase di apertura).

Precedenza: una sola scala, in `motore/editoriale/LEGGIMI.md`; segnala ogni contrasto.
Metodo: proponi → l'autore approva → applica; mai approvare da solo.
Risposte dell'autore: ok, avanti, correggi: …, stato. Ramo: quello della sessione, letto da git.

Salvataggio a ogni passo: `zb salva` (recinto, commit, push), poi git status -sb, git log -1. Se il push
fallisce: fermati e riporta l'errore. Non dire «fatto» se non è su origin. Resoconto con hash, file e
«branch allineato a origin: sì/no».

# Regole di avvio

Regola madre: il motore resta sempre pulito; il ramo `motore` non contiene mai un libro. Per ogni briefing nuovo: prima
azione «zb nuovo», che apre una sola cartella del libro. Da quel momento scrivi solo nella cartella del libro, sottocartelle
comprese; mai in motore/, nella banca-voci o altrove. Recinto: hook su Write/Edit/Bash, controllo pre-commit e `zb avvio`
rifiutano i file fuori dal libro attivo; solo se l'autore scrive «lavoro sul motore»: `zb lavoro motore`.

Per qualsiasi lavoro su un libro leggi `motore/PROCEDURA.md` e il `LEGGIMI.md` del libro indicato (un percorso: se manca,
chiedilo prima di toccare qualunque file). `docs/` non si legge durante il lavoro. Prima di scrivere:
`python3 motore/zb avvio <libro> [--ruolo R]` e riporta la riga «Letto: …»; se si ferma, fermati e riporta il motivo.
Un ruolo per sessione (senza `--ruolo`, quello della fase; `<libro>/.zb/ruoli.yaml`). Nelle sessioni nuove leggi lo stato
compatto del libro e la scheda del capitolo. Il motore legge solo `motore/`, la cartella del libro indicato e la
banca-voci (`ZB_BANCA_VOCI`, sola lettura). Lavoro sul motore: `motore/passaggio-di-consegne.md`.

Percorso da casa editrice: `motore/editoriale/00-percorso.md`. La sessione principale orchestra e non scrive prosa:
chiama l'agente indicato da `zb agenti prossimo <libro>` (un subagente per capitolo) e legge solo la sua risposta breve.
Chi scrive non rivede (`separazione_ruoli`, `motore/dati/hook.yaml`). Comandi: `zb aiuto` (fonte: `dati/comandi.yaml`).

Report di sessione ogni 5 scambi o a «passaggio»: nella cartella del libro (passaggio-di-consegne.md), mai in motore/.
Sezioni: Stato; Decisioni prese; Regole da non violare; Fatto in questa sessione; Punti aperti; Prossimo passo;
Ripartenza (comandi e frase di apertura).

Precedenza: una sola scala, in `motore/editoriale/LEGGIMI.md`; segnala ogni contrasto.
Metodo: proponi → l'autore approva → applica; mai approvare da solo. Modo automatico (PROCEDURA, regola 10): sul percorso
editoriale nessuna approvazione tra le fasi; ci si ferma solo alla pausa di lettura (`pausa_lettura`, 3-5 capitoli in
libro.yaml), a `controllo_fallito` e a `canone`. Risposte dell'autore: ok, avanti, correggi: …, stato (alla pausa: ok o
correggi <note>). Ramo: quello della sessione, letto da git.

Salvataggio a ogni passo: `zb salva` (recinto, commit, push), poi git status -sb, git log -1. Se il push fallisce:
fermati e riporta l'errore. Non dire «fatto» se non è su origin. Resoconto con hash, file e «branch allineato a origin: sì/no».

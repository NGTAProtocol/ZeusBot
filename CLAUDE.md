# Regole di avvio

Regola madre: il motore resta sempre pulito; il ramo `motore` non contiene mai un libro.
Briefing nuovo: prima azione «zb nuovo», che crea la cartella del libro. Tutto ciò che riguarda il libro
vive solo lì (briefing, voce, report di sessione); il suo nome non compare altrove. Il recinto (hook) blocca
le scritture fuori dal libro attivo; solo se l'autore scrive «lavoro sul motore»: `zb lavoro motore`.

Per lavorare su un libro leggi `motore/PROCEDURA.md` e il `LEGGIMI.md` del libro (un percorso: se manca,
chiedilo prima di toccare qualunque file). Prima di scrivere: `python3 motore/zb avvio <libro> [--ruolo R]`
e riporta la riga «Letto: …»; se si ferma, fermati e riporta il motivo. Un ruolo per sessione.
Il motore legge solo `motore/`, la cartella del libro e la banca-voci (`ZB_BANCA_VOCI`, sola lettura).
Non leggere `docs/` (esportazioni, guida, analisi) se l'autore non lo chiede.

Orchestrazione: la sessione principale non scrive prosa. `zb agenti prossimo <libro>` dice chi chiamare:
l'agente del passo con slug e capitolo; leggi solo la sua risposta breve. Capitoli sempre in sequenza;
line, copy e capsule in parallelo, al massimo come in `motore/dati/orchestrazione.yaml`.

Report di sessione ogni 5 scambi o a «passaggio»: `passaggio-di-consegne.md` nella cartella del libro;
`motore/passaggio-di-consegne.md` solo per il lavoro sul motore. Sezioni: Stato; Decisioni prese; Regole
da non violare; Fatto in questa sessione; Punti aperti; Prossimo passo; Ripartenza.

Precedenza: una sola scala, in `motore/editoriale/LEGGIMI.md`; segnala ogni contrasto.
Metodo: proponi → l'autore approva → applica; mai approvare da solo.
Risposte dell'autore: ok, avanti, correggi: …, stato (PROCEDURA.md). Ramo: quello della
sessione, letto da git. Tono: il testo precedente è un registro dei fatti, non si giudica.

Blocco di salvataggio a ogni passo: git add, commit, push (`zb push`), git status -sb, git log -1. Se il
push fallisce o un file non si salva: fermati e riporta l'errore. Non dire «fatto» se non è
su origin. Resoconto con hash, file e «branch allineato a origin: sì/no».

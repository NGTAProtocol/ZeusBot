# Regole di avvio

Regola madre: il motore resta sempre pulito; il ramo `motore` non contiene mai un libro. Briefing nuovo: prima «zb nuovo»
(una sola cartella del libro); poi si scrive solo lì. Recinto: hook, controllo pre-commit e `zb avvio` rifiutano i file
fuori dal libro attivo; solo se l'autore scrive «lavoro sul motore»: `zb lavoro motore` (consegne: `motore/passaggio-di-consegne.md`).

Lavoro su un libro (sessione principale; gli agenti no): il libro (se manca, chiedilo). Prima di scrivere `python3 -B motore/zb avvio <libro>
[--ruolo R]` e riporta la riga «Letto: …»; se si ferma, fermati e riporta il motivo. Il motore legge solo `motore/`,
la cartella del libro indicato e la banca-voci (`ZB_BANCA_VOCI`, sola lettura). Leggi lo stato compatto e il
`LEGGIMI.md` del libro; `motore/PROCEDURA.md` solo per un dubbio puntuale (cerca la sezione, non leggerla intera);
`docs/` mai durante il lavoro. Comandi: `zb aiuto`.

Stesura: `/capitolo` (ruolo `regia`): `zb agenti prossimo` dà una sola AZIONE o un FERMO; scrittore (Opus), misure del
motore, revisione con voti tarati e soglia di qualità, una correzione mirata, `zb esito`, capsula, `zb salva`. La
sessione principale non scrive prosa e legge solo le risposte brevi degli agenti. Chi scrive non rivede: agenti diversi.
Le soglie di stile informano; bloccano solo fatti oggettivi e il voto sotto soglia.

Modo automatico: nessuna approvazione tra le fasi; ci si ferma solo alla pausa di lettura (ok | correggi <note>), a
un FERMO del motore e al canone. Fuori dal percorso: proponi → l'autore approva → applica; mai approvare da solo.
Precedenza: una sola scala, in `motore/editoriale/LEGGIMI.md`; segnala ogni contrasto. Ramo: quello della sessione.

Salvataggio: `zb salva` a ogni capitolo (recinto, commit, push), poi git status -sb e git log -1; se il push fallisce,
fermati. Non dire «fatto» se non è su origin: hash e «branch allineato a origin: sì/no». A «passaggio» o a fine
sessione: `passaggio-di-consegne.md` nella cartella del libro indicato (Stato, Decisioni, Prossimo passo, Ripartenza).

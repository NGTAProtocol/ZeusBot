# Passaggio di consegne — prova-padre-del-mostro

## Stato
- Ramo `libro/prova-padre-del-mostro`, cartella `libri/prova-padre-del-mostro/`.
- Fase «stesura», gate in attesa «lettura»: PAUSA DI LETTURA dopo la seconda riscrittura dei capitoli 1, 2, 3.
- Capitoli accettati da `zb esito`: 1 (2069 parole), 2 (1787), 3 (2557); `zb stile`: nessun KO e nessun avviso.
- Voce: `sistema-nell-ombra` @ f6ee79d (83 divieti, regole per funzione in scheda 2.12-2.15, sezione 3, sezione 7
  punti 10-17). Ruoli del diagnosta e del line editor aggiornati su `integrazione-editoriale` @ 16a0e15 (questo ramo
  ha ancora la copia precedente dei ruoli in `motore/`: i revisori hanno letto il file da integrazione-editoriale).
- Capsule 1 e 2 rifatte e verificate; capsula 3 non fatta (gate «lettura» aperto).

## Decisioni prese
- Note dell'autore del 2026-10-21 in `06-diagnostica/note-lettura.md` (stessi fatti e scene; regole nuove della voce;
  Kurgan rimanda a casa il ragazzo, con il soggetto chiaro; canone dal codex).
- Ciclo per capitolo: `zb prepara`, scrittore-voce (sessione-scrittore), revisione del diagnosta (sessione-diagnosta,
  checklist «Capitolo singolo», rapporto `06-diagnostica/audit/NN.md`), correzione unica dello scrittore, nuova
  revisione; al «passa» `zb correggi <libro> N: <motivo> --commit <hash>` per ogni passaggio e `zb esito`; dopo ogni
  commit del capitolo `zb riapprova` (richiesto da `zb avvio`). Giri di revisione al massimo tre
  (`ruoli/riferimenti/critica-manoscritto.md`).
- In fase «stesura» `zb ruolo <libro> diagnosta N` si rifiuta: i rapporti di audit lo dicono nella prima riga (proposta
  P2 in `docs/PROPOSTE_MOTORE.md` su integrazione-editoriale).

## Regole da non violare
- Scrivere solo in `libri/prova-padre-del-mostro/`; la banca-voci si legge soltanto.
- Fatti canonici (`fatti_bloccati`) solo con il gate «canone».
- Un ruolo per sessione; chi scrive non rivede.
- Alla pausa di lettura: solo «ok» o «correggi <note>».

## Fatto in questa sessione
- Capitolo 1: tre giri di revisione (non passa: 6 chiuse, 2 eco, 9 catene, 1 soggetto; non passa: 1 catena; passa),
  poi `zb esito` OK (frase media 9.3, nessun avviso).
- Capitolo 2: due giri (non passa: ora contraddetta alla r. 87 e fatto nuovo alla r. 57; passa), `zb esito` OK con due
  avvisi anti-IA (ripetizioni 14.61/1000, formule 1.12/1000).
- Capitolo 3: due giri (non passa: 2 chiuse, 3 battute senza chi parla, uno scambio nuovo; passa), `zb esito` OK con
  un avviso (ripetizioni 12.94/1000); pausa di lettura riaperta.

## Punti aperti
- Frase media: il manuale vuole 9-14, la voce 5-10 nel registro corto; il capitolo 1 sta a 9.3 senza frasi unite, con
  le frasi-frammento tagliate (proposta P3 in `docs/PROPOSTE_MOTORE.md`).
- Casi segnalati dai revisori e non contati: frasi dubbie di chiusa (cap. 3 rr. 47 e 203), possibile eco cap. 3 r. 133,
  cap. 1 «resto»/«resta» rr. 189-191; nel cap. 3 non si dice che fine fa il cartoncino ritirato dal caporale.
- Battute minori della prima versione sparite nel capitolo 2 (elenco in `06-diagnostica/audit/02.md`).
- Restano aperti: A1 e B1 della diagnosi di struttura; contrasto caporali/lineetta; campi del briefing non compilati;
  capsula 3; punti «da confermare dall'autore» del codex.

## Prossimo passo
L'autore legge `04-manoscritto/01-l-ultimo-appuntamento.md`, `02-la-nomina.md`, `03-la-convocazione.md` e
risponde «ok» oppure «correggi <note>».

## Ripartenza
```
export ZB_BANCA_VOCI=<cartella della banca-voci>
git checkout libro/prova-padre-del-mostro && git pull
python3 -B motore/zb lavoro libro prova-padre-del-mostro
python3 -B motore/zb avvio libri/prova-padre-del-mostro
python3 -B motore/zb stato libri/prova-padre-del-mostro
python3 -B motore/zb agenti prossimo libri/prova-padre-del-mostro
```
Frase di apertura: «Leggi libri/prova-padre-del-mostro/passaggio-di-consegne.md e riprendi dalla pausa di lettura».

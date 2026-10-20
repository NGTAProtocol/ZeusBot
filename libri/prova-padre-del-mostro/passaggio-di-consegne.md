# Passaggio di consegne — prova-padre-del-mostro

## Stato
- Ramo `libro/prova-padre-del-mostro` (creato da `integrazione-editoriale` @ 2df84b3), cartella `libri/prova-padre-del-mostro/`.
- Fase «stesura», gate in attesa «lettura»: PAUSA DI LETTURA dopo i capitoli 1, 2, 3 (`pausa_lettura: 3`).
- Capitoli scritti e accettati da `zb esito`: 1 (2104 parole), 2 (1694), 3 (2614); totale 6412 su 70000 previste.
- Capsule: 1 e 2 fatte e verificate; capsula 3 non ancora fatta (il motore, con il gate «lettura» aperto, chiede prima la risposta dell'autore).
- Voce: `sistema-nell-ombra` (banca-voci @ 4655f99), ambientazione `altro`.

## Decisioni prese
- Lunghezza 70000 parole dal profilo `thriller` (valore minimo di `lunghezza_totale.consigliata`): il briefing non la indicava ed è obbligatoria per `zb nuovo`. Ne derivano 35 capitoli previsti.
- Genere del briefing «thriller geopolitico/noir d'azione» → profilo `thriller` (non esiste un profilo noir).
- Intestazione dei capitoli senza date di calendario (luogo generico e tempo relativo «giorno N»): epoca e date non indicate nel briefing.
- Dialoghi con la lineetta «—»: per l'italiano il motore misura come dialogo solo le righe che cominciano con la lineetta (`dati/lingue.yaml`).
- Piano di revisione della struttura NON applicato: nel modo automatico la struttura non ha gate; il piano è una proposta che si applica solo con l'ok dell'autore (ruolo 04).

## Regole da non violare
- Scrivere solo in `libri/prova-padre-del-mostro/`; la banca-voci si legge soltanto.
- Fatti canonici del briefing (`stato.yaml`, `fatti_bloccati`) non si cambiano senza il gate «canone».
- Un ruolo per sessione (`ZB_SESSIONE`); chi scrive non rivede.
- Alla pausa di lettura: solo «ok» o «correggi <note>» dell'autore.

## Fatto in questa sessione
- `zb nuovo` dal briefing; struttura (architetto-struttura), rapporto e contratto (diagnosta), piano di revisione (editor-strutturale), `zb pronto` (gate automatico).
- Documenti (direttore-editoriale): bibbia, 21 schede del codex, cronologia, nota di direzione; `zb pronto` senza gate.
- Pagina campione (scrittore-voce); `zb pronto` senza gate.
- Capitoli 1-3 (scrittore-voce, un subagente per capitolo, dopo `zb prepara`), `zb esito`, capsule 1-2 (agente capsula, sessione propria).
- Capitolo 1: KO al primo `zb esito` (frase_media 7.7 fuori da 9-14; dialogo 0.0% fuori da 25-45%), una correzione, poi OK.
- Capitolo 3: KO al primo `zb esito` (scena_minimo: scena 1 783 parole, minimo 800), una correzione, poi OK.
- `zb stile`: nessun KO e nessun avviso; nessun divieto della voce trovato (68 divieti caricati).

## Punti aperti
- Decisioni dell'autore indicate dal piano di revisione della struttura (`06-diagnostica/piano-revisione-struttura.md`): A1 (capitoli 30-35 proposti dall'architetto), A2 (Bertola ha avuto parte nel sacrificio di Kurgan?), A3 (enigma o suspense). Problema bloccante B1 del rapporto del diagnosta (cause della seconda svolta e del climax).
- Contrasti: frase media del manuale (9-14) e registro corto della voce (5-10); `03-struttura/09-scelte-fisse.md` prescrive le caporali, il motore misura la lineetta.
- Dettagli inventati dagli agenti (segnalati da loro): 22 uomini convocati e un «pensò» nella pagina campione; luogo e autista nel capitolo 1; usciere, impiegata, sala piccola nel capitolo 2; ritiro dei telefoni (31), linee guida in cinque punti, orario nel capitolo 3.
- Avvisi anti-IA P2 «ripetizioni ravvicinate» nei capitoli 1, 2, 3.
- Capsula 3 da fare dopo la risposta dell'autore (senza, `zb prepara 4` si ferma).
- Campi non compilati nel briefing: Lettore, età dei personaggi, Tono, Finale, schede (fissi, variabili, come parla, da solo, mai cambiare), Epoca, Regole del libro, Riferimenti, Cose da non cambiare, ruolo del colonnello De Stefano.

## Prossimo passo
L'autore legge `04-manoscritto/01-l-ultimo-appuntamento.md`, `02-la-nomina.md`, `03-la-convocazione.md` e risponde «ok» oppure «correggi <note>».

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

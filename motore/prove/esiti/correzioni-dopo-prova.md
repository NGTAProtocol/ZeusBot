# Correzioni dopo la prova romance: resoconto

Prove: `zb prove` **356/356 OK** (20 nuove nella sezione `correzioni_dopo_prova`, 4 attesi di passo 2
aggiornati per il nuovo avviso sul totale); saltate 2 (LanguageTool, `ZB_LANGUAGETOOL` non impostata);
separazione OK; recinto OK (46 esecuzioni).

| Voce | Esito | Correzione |
|---|---|---|
| a | risolto | `continuita.py`: le durate di `cronologia.yaml` si confrontano con le date degli eventi anche senza testo (unità «cronologia»). |
| b | limite noto | «come si…», «come quando…» non contati: sono spesso «in che modo». In `PROCEDURA.md` (sezione 7, «Limiti noti») con l'effetto sul report: candidati e avviso «similitudini» possono stare sotto il vero. |
| c | risolto | All'ingresso nella fase `pagina_campione`, `fase.py` crea `05-revisioni/pagina-campione.md` vuota (solo titolo e nota nascosta); `zb pronto` la rifiuta finché è vuota. |
| d | risolto | Il manuale generato spiega le sigle: G gesto, O oggetto, B battuta, D domanda, R rivelazione, P pericolo, X decisione, I immagine. |
| g | risolto | Nuovo comando `zb riapprova <libro> <documento> <motivo>`: nuovo sha256 e commit, con data, motivo, sha256 e commit precedenti in `stato.yaml`. `zb avvio` lo indica quando si ferma. |
| h | risolto | Cifre: campo facoltativo `contesto` in `cronologia.yaml`; con il contesto KO solo nelle righe che lo contengono, senza contesto un numero diverso è AVVISO. |
| i | risolto | `stile.py`: «come l'» seguito da un verbo («a come l'aveva lasciata») non è una similitudine. |
| j | risolto | Ordine di chiusura: `zb pacchetto` prima di `zb kdp` in `fase.py`, `PROCEDURA.md` e `README.md`. |
| k | risolto | `zb esito` a un gate `primi_capitoli` o `lotto` con una correzione registrata: rifà i controlli del capitolo del gate e aggiorna le parole; il gate resta aperto. |
| l | risolto | `zb conta` e `zb capitolo`: totale previsto (scritte + budget delle unità non scritte) fuori da `tolleranza_totale` dà AVVISO con il budget residuo proposto; nessun capitolo si accorcia o si allunga da solo. |

## File

- Modificati: `script/fase.py`, `script/avvio.py`, `script/nuovo.py`, `script/stile.py`,
  `script/continuita.py`, `script/conta.py`, `script/capitolo.py`, `script/prove.py`, `zb`,
  `prove/attesi.yaml`, `modelli/cronologia.yaml`, `dati/struttura-libro.yaml`, `PROCEDURA.md`, `README.md`.
- Nuovo: `prove/esiti/correzioni-dopo-prova.md`.

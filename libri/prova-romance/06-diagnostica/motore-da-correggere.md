# Motore: da correggere (elenco, non ancora corretto)

Trovato durante la prova romance. Le correzioni si fanno sul ramo `motore`, a parte.

| # | Problema | Dove | Esempio |
|---|---|---|---|
| a | Aperto. `continuita.py` controlla le durate della cronologia solo quando compaiono nel testo dei capitoli; non verifica da sola gli eventi tra loro. | `motore/script/continuita.py`, riga 157 (durate) | «sei settimane» tra il 4 marzo e il 14 aprile 2024 sono 41 giorni, non 42: nessun KO perché non ci sono capitoli. |
| b | Aperto. Il riconoscitore di similitudini di `stile.py` ne trova 0 anche quando ci sono: cerca solo «come» seguito subito da un articolo, «sembrava», «pareva». | `motore/script/stile.py`, riga 20 (`SIMILITUDINE`) | «come si fa con un cane…», «come si sente un dente…», «come quando da bambina…», «come si guarda una barca…»: 0 trovate. |
| c | Aperto. `nuovo.py` non crea `05-revisioni/`, ma il gate «pagina_campione» cerca la pagina proprio lì. | `motore/script/nuovo.py` (`crea`, riga 371); `motore/script/revisione.py`, riga 24 (`PAGINA_CAMPIONE`) | Il messaggio di fase dice dove scriverla, ma la cartella non esiste e la struttura standard la crea solo al primo file. |
| d | Aperto. Il manuale generato non spiega le sigle di chiusura G, O, B, D, R (ne scrive solo le lettere). | `motore/script/nuovo.py`, riga 310 | Romance «misto»: G gesto, O oggetto, B battuta, D domanda, R rivelazione. |
| e | Risolto in `57d1a84`. `continuita.py` trattava ogni durata diversa da «anni» come mesi («sei settimane» = 6 mesi). | `motore/script/continuita.py` (durate) | Capitolo 1: due KO su «sei settimane»; ora confronto in giorni con `tolleranza_giorni`. |
| f | Risolto in `57d1a84`. `continuita.py` prendeva come età attuale ogni «N anni» della frase, anche al passato, e la dava a tutti i nomi. | `motore/script/continuita.py` (età) | Capitolo 1: «da quando Nora aveva sei anni» dava KO a Nora e ad Adele; ora è ignorato. |
| g | Aperto. Nessun comando registra una modifica autorizzata a un documento già approvato: `zb avvio` si ferma per sha256 diverso. | `motore/script/fase.py` (documenti_approvati); `motore/script/avvio.py` | `cronologia.yaml`: tolleranza della durata «sei settimane» cambiata su richiesta dopo l'approvazione. |

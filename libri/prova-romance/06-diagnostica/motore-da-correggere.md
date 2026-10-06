# Motore: da correggere (elenco, non ancora corretto)

Trovato durante la prova romance. Le correzioni si fanno sul ramo `motore`, a parte.

| # | Problema | Dove | Esempio |
|---|---|---|---|
| a | `continuita.py` non controlla le durate tra gli eventi della cronologia: confronta solo le durate scritte nel testo dei capitoli. | `motore/script/continuita.py`, riga 157 (durate) | «sei settimane» tra il 4 marzo e il 14 aprile 2024 sono 41 giorni, non 42: nessun KO perché non ci sono capitoli. |
| b | Il riconoscitore di similitudini di `stile.py` ne trova 0 anche quando ci sono: cerca solo «come» seguito subito da un articolo, «sembrava», «pareva». | `motore/script/stile.py`, riga 20 (`SIMILITUDINE`) | «come si fa con un cane…», «come si sente un dente…», «come quando da bambina…», «come si guarda una barca…»: 0 trovate. |
| c | `nuovo.py` non crea `05-revisioni/`, ma il gate «pagina_campione» cerca la pagina proprio lì. | `motore/script/nuovo.py` (`crea`, riga 371); `motore/script/revisione.py`, riga 24 (`PAGINA_CAMPIONE`) | Il messaggio di fase dice dove scriverla, ma la cartella non esiste e la struttura standard la crea solo al primo file. |
| d | Il manuale generato non spiega le sigle di chiusura G, O, B, D, R (ne scrive solo le lettere). | `motore/script/nuovo.py`, riga 310 | Romance «misto»: G gesto, O oggetto, B battuta, D domanda, R rivelazione. |

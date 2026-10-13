# Solo il motore nel repository: esito

Data: 2026-10-13. Ramo motore, partendo da f27082e.

## Passo B: riferimenti testuali ai libri reali

Nel ramo non c'erano manoscritti reali, ma restavano riferimenti nel testo. Sono stati sostituiti sul posto.

| File | Prima | Dopo |
|---|---|---|
| `prove/attesi.yaml` | commento con lotto e titolo di un libro | «Correzioni su interludi, impronte e grafie» |
| `prove/attesi.yaml` | chiavi `correzioni_lotto_…` e `correzioni_dopo_lotto_…` | `correzioni_interludi_e_grafie`, `correzioni_esclusioni_e_budget` |
| `prove/attesi.yaml` | frasi di prova riprese da un libro (escludi_pattern, pattern «Non era X. Era Y.») | frasi inventate con lo stesso numero di parole, la stessa punteggiatura e lo stesso schema («fischio del treno», «la villa di Ardena», «la scatola sotto il letto») |
| `script/stile.py` | esempio nel commento ripreso da un libro | «il fischio letterale del treno» |
| `script/prove.py` | funzioni e sezioni con i numeri dei lotti di un libro | `correzioni_interludi_e_grafie` («interludi e grafie»), `correzioni_esclusioni_e_budget` («esclusioni e budget») |
| `prove/esiti/pdf-indipendente-dal-container.md` | titolo e autore di un libro | «autore di libro.yaml», «qualunque libro in A5, compreso un libro di prova» |
| `prove/esiti/passo-6.md` | «libro 1», «libro 2», suffisso di un ramo di libro, percorsi con il nome del repository | formulazioni neutre |
| `prove/esiti/passo-5.md`, `proposta-motore.md` | nome del repository | «repository» |

Suite dopo la sostituzione: **424/424 OK**. Le prove sostituite danno lo stesso esito di prima.

Controllo finale sui nomi reali (titoli, autori, personaggi, luoghi, nome del repository e dei rami
dei libri, presi dai file dei libri disponibili in sessione; la lista non è salvata nel repository):
0 occorrenze di riferimenti. Restano 3 parole comuni della lingua, usate nel loro senso normale nei
testi dei mini-libri inventati: coincidono solo per caso con un nome proprio di un libro.

## Passo D: archivio e rimozione di `ghimoney/`

`ghimoney/` era un progetto separato (misura dell'impatto di repository open-source, 80 file), non il motore.

- Archivio: ramo `archivio/ghimoney` su origin, creato dal commit 572f40f, con `ghimoney/` per intero.
- Copia fuori dal repository, nello scratchpad della sessione: vive solo nel container. La copia che
  conta è il ramo su origin.
- Verifica prima della rimozione, con un manifesto sha256 per ciascuna delle tre fonti (origine su disco,
  copia, ramo su origin): 80 file in ognuna, manifesti identici riga per riga. Nessun file non tracciato
  dentro `ghimoney/`.
- Rimozione: `ghimoney/` tolto dal ramo del motore; da `.gitignore` tolta la riga `.ghimoney/`, che
  serviva solo a quel progetto.
- Per recuperarlo: `git checkout origin/archivio/ghimoney -- ghimoney`.

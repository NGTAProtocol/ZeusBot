# Traduzione di un libro

Comando: `zb traduci <libro> --a <lingua> inizia`. Tutto sta in `libri/<slug>/08-traduzione-<lingua>/`, che è
un libro di traduzione (`modalita: traduzione` in `libro.yaml`): si lavora con gli stessi comandi di zb su
quella cartella. L'originale si legge in sola lettura (`..`).

## Fasi e gate
| Fase | Chi | Gate |
|---|---|---|
| `guida` | autore e traduttore: guida di traduzione e glossario, PRIMA del capitolo 1 | `guida` |
| `stesura` | agente `traduttore`, un capitolo alla volta, in sequenza; `zb esito` fa i controlli meccanici | — |
| `line` | `line-editor` nella lingua di arrivo (ruolo separato dal traduttore) | `line` |
| `copy` | `correttore-italiano` con i criteri della lingua di arrivo (`lingue/<lingua>/`) | `copy` |
| `fedelta` | agente `revisore-fedelta`, sessione nuova: revisione affiancata e ritraduzione a campione | `fedelta` |
| `chiusura` | motore: compila, impagina, pdf, pacchetto, kdp della lingua di arrivo | — |

## Guida e glossario (gate `guida`)
- Guida (`00-progetto/guida-traduzione.md`): voce, registro, resa di dialetto e riferimenti locali, varietà
  (per l'inglese britannico o americano), sistema del dialogo, titolo, traduttore da indicare.
- Glossario (`00-progetto/glossario.yaml`): un termine = una traduzione; nessuna traduzione usata per due
  termini; i nomi che non cambiano si ripetono uguali. Il motore lo prepara dal codex e da `nomi_propri.txt`.

## Ogni capitolo
1. `zb traduci <traduzione> --a <lingua> prepara N`: capitolo originale, guida, le sole voci del glossario
   presenti, capsule dell'originale fino a N-1, ultime righe del capitolo tradotto precedente.
2. Agente `traduttore` (contesto pulito): scrive `04-manoscritto/NN-<slug>.md` della traduzione.
3. `zb esito <traduzione> N`: stessi paragrafi e battute, stessi numeri e date, nomi dal glossario, parole
   della lingua di partenza rimaste, rapporto di lunghezza, nessuna nota aggiunta, chiusura conservata.

## Fedeltà
Niente aggiunte, niente note o didascalie inventate, errori dell'autore resi come scritti (si segnalano
all'autore, non si correggono). Il revisore di fedeltà lavora in una sessione nuova, con una scheda di
fedeltà per capitolo e la ritraduzione a campione (`06-diagnostica/ritraduzione/NN.md`, poi
`zb traduci … ritraduci N`).

## Sequenza o blocchi
In sequenza: ogni capitolo vede le ultime righe del precedente tradotto. Il parallelo (blocchi con ancora di
stile) è ammesso solo con il glossario approvato: senza, nomi e termini divergono (osservazione misurata in
fredchu/book-translator). Confronto delle due strade: `zb traduci … confronta <cartella A> <cartella B>`.

## Edizione commerciale
- Lettura finale di un madrelingua consigliata per ogni edizione in vendita.
- KDP (Content Guidelines, verificato il 2026-10-15 sulla pagina ufficiale): una traduzione creata con uno
  strumento di IA è contenuto «AI-generated» e va dichiarata alla pubblicazione, anche se poi rivista; il
  traduttore e l'autore originale vanno indicati tra i contributor. Ricontrollare la pagina prima di pubblicare.

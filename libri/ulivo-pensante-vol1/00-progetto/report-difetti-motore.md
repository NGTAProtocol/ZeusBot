# Report per l'autore: difetti generici del motore e altre segnalazioni

Regola: i difetti GENERICI del motore non si correggono durante il lavoro sul libro; si annotano qui.

## Difetti generici del motore (da valutare in una sessione «lavoro sul motore»)

1. **Manca un profilo «ragazzi 9-12».** I profili sono fantascienza, fantasy, giallo, narrativa-letteraria,
   romance, thriller, young-adult; tutti hanno formati da 40.000 parole in su e capitoli da 800-1.500 parole
   minimo. Usato il più vicino («giallo») con override motivati su lunghezza, capitoli e scene.
2. **Upstream del ramo di libro.** Creando il ramo con `git checkout -b <ramo> origin/motore`, git imposta
   come upstream `origin/motore`: un `git push` senza argomenti spingerebbe sul ramo motore. Tolto a mano
   (`git branch --unset-upstream`). La procedura potrebbe indicare `--no-track` o il push esplicito.
3. **Formato di stampa predefinito.** `zb nuovo` scrive sempre EB Garamond 11,5 pt: per un libro per
   ragazzi serve un carattere più grande e leggibile. Da decidere alla fase PDF (non toccato ora).
4. **Intestazione del capitolo predefinita** «Luogo — giorno e data»: pensata per romanzi adulti.
   Risolto senza toccare il motore: è un campo di testo del libro (`struttura.intestazione_capitolo` in
   libro.yaml), che nessuno script usa come regola; ora dice «solo titolo». Nei capitoli resta solo
   «# N — Titolo» (lo usa `compila.py`). Effetto: `continuita.py`, senza la riga di luogo e data, prende la
   data del capitolo dalla scaletta o dalla prima data nel testo. Nessuna modifica al motore.
5. **`zb correggi` al gate**: una correzione con più punti va registrata come una sola istruzione; il
   motore non tiene l'elenco dei singoli punti. Solo un'osservazione, nessun blocco.

## Segnalazioni sulla banca-voci (solo lettura, nulla modificato)

- Il prompt dice che `mistero-ed-epicita` è «da_completare» (mancano lessico/divieti, adattamento di genere,
  campione-modello e divieti.yaml, che scrive l'autore). Nella banca-voci (`main` @ 375ee5f) risulta invece
  **pronta**: `zb voce verifica` → «OK voce mistero-ed-epicita: 7 sezioni, 76 divieti, pronta».
  Sezioni 4, 5, 6 e `divieti.yaml` ci sono, ma la nota in testa alla scheda dice che sono «ricavate dalla
  voce stessa», non scritte dall'autore.
- Il motore accetta la voce. Uso per il libro: solo le sezioni 1, 2, 3 e 7 (testo dell'autore). Le sezioni
  4-6 non fanno da modello; `divieti.yaml` viene letto comunque da `stile.py` come AVVISI (non blocca).
  Da confermare con Felice.
- Contrasto voce/libro: la voce prevede fantasy, spade, meccanismi antichi e meraviglia; il libro è
  realistico, senza magia (decisione 4a). Vince il manuale del libro (precedenza).

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

## Aggiunte del 14/10/2026 (pagina campione)

6. **Dialogo misurato solo con la lineetta.** `stile.py` conta come dialogo solo le righe che iniziano con
   «—» (`dati/lingue.yaml`, `lineetta_dialogo`); le virgolette «» sono dichiarate in lingue.yaml ma non usate.
   Con i caporali ogni capitolo darebbe dialogo 0% = KO. Difetto generico, non corretto: **la misura del
   dialogo non riconosce le virgolette «»**. Il libro usa la lineetta (decisione dell'autore del 14/10/2026).
7. **Frase media del profilo giallo (9-14) e lettori 9-12.** La pagina campione (versione finale) sta a 9,1 (metodo del motore,
   `stile.metriche`): dentro, ma al limite. Se l'autore vuole frasi più corte serve un override motivato
   («Frase media: a-b» nel briefing → libro.yaml), da approvare. Nessuna modifica fatta.
8. **Nessun comando per controllare la pagina campione.** `zb stile`/`zb capitolo` lavorano sulle unità del
   manoscritto; per la pagina campione ho chiamato le stesse funzioni di `stile.py` (`controlla_unita`) da
   fuori. Esito in `06-diagnostica/pagina-campione.md`. Un comando dedicato sarebbe utile.

## Aggiunte del 14/10/2026 (stesura, capitoli 1-3)

9. **Controllo «cifre» troppo largo.** `continuita.py` (cifre con `contesto`) prende come numero anche
   l'articolo o il pronome «uno/una» entro tre parole da «quaderni»: «raccolse i quaderni uno alla volta»
   → KO «uno quaderni, atteso 7» (cap. 1, primo tentativo). Inoltre la trama vuole «sei quaderni» sul
   tavolo (ne manca uno): con `cifre: quaderni = 7` ogni «sei» vicino a «quaderni» è KO. Nel testo ho
   evitato la vicinanza; nessuna modifica a cronologia.yaml né al motore.
10. **Gate «primi_capitoli» fisso dopo il capitolo 3.** L'autore aveva chiesto 1-5 con fermata dopo il 5;
    il motore apre il gate dopo il 3 e rifiuta `zb esito 4` finché l'autore non risponde (ok / correggi).
    Non è un difetto: è la procedura. Segnalato perché il passaggio di consegne diceva «1-5».
11. **Avvio senza banca-voci.** Senza clone la riga «Letto: …» esce con un AVVISO e senza la scheda della
    voce; in ambiente cloud il clone richiede prima di aggiungere il repository alla sessione.

## Aggiunte del 14/10/2026 (correzioni al gate primi_capitoli, capitoli 4-5)

12. **Riciclo e pagine enigma.** Il controllo di riciclo segnala come AVVISO le ripetizioni volute: la tavola
    dell'enigma 1 (cap. 2) ripete apposta la descrizione dell'elicriso del cap. 1, perché l'enigma sia leale.
    Lasciate (3 avvisi, nessun KO). Utile poter escludere dal controllo la sezione «L'enigma della banda».
13. **Gate dopo una correzione.** Dopo `zb correggi` e `zb esito`, `zb ok` va solo se tutti i blocchi del gate
    sono stati rimostrati con `zb avanti` (9 blocchi per tre capitoli). Funziona, ma non è detto da nessuna
    parte nell'output di `zb esito`.

## Aggiunte del 14/10/2026 (correzioni C1-C7 ai capitoli 4-5)

14. **Falso positivo «si_sentiva» (divieti della voce).** Con la banca-voci a `375ee5f`, il divieto
    `si_sentiva` (emozione diretta) prende anche «si sentivano solo i grilli» (cap. 5): lì «solo» vuol dire
    «soltanto», non è un'emozione. AVVISO, nessun KO; testo lasciato com'è. Il pattern andrebbe limitato
    (per esempio escludendo «solo» seguito da articolo o nome). I divieti non sono dell'autore (punto 10 del
    passaggio di consegne).
15. **Pagina enigma a metà capitolo.** Il motore non conosce la pagina «L'enigma della banda»: la conta come
    prosa della scena in cui sta. Nel cap. 4 la pagina chiude la scena 1 (correzione C1): ammessa, ma le sue
    parole entrano nel conteggio della scena e del capitolo, e le righe in elenco abbassano la frase media.

## Aggiunte del 14/10/2026 (capitoli 6-10)

16. **Colonna «Scene» del piano parole solo informativa.** `capitolo.py` controlla il numero di scene sul
    profilo (1-2), non sulla colonna «Scene» di piano-parole.md: i cap. 8 e 9 hanno due scene (pagina enigma a
    metà) con il piano che dice 1, senza avvisi. Utile un AVVISO quando il numero di scene differisce dal piano.
17. **Ripetizioni volute segnalate come riciclo.** Cap. 10: «un rametto con le foglie strette e appuntite» (la
    firma di Rosa, uguale apposta al cap. 1-2) e «la stanza di pietra sotto i capperi» (la frase decifrata nel
    cap. 9). Lasciate: 2 AVVISI, nessun KO (vedi punto 12).
18. **`zb riapprova` con l'output in una pipe.** Con `| head -1` lo script chiude con BrokenPipeError dopo aver
    già scritto stato.yaml (registrazione riuscita, traccia d'errore a schermo). Innocuo, ma confonde.

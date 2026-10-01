# Controllo ortografico — «Il padre del mostro»

- **Stato controllato:** `87e4cba` (prologo e capitoli 1-53, `04-manoscritto/`).
- **Sola proposta:** il manoscritto e i PDF non sono stati modificati.
- **Data:** 1 ottobre 2026.

## Esito

**Nessuna svista certa trovata.** In tutte le categorie richieste il totale delle correzioni da proporre è zero.

| Tipo | Casi certi | Casi esaminati e scartati come corretti |
|---|---|---|
| Refusi (parole inesistenti) | 0 | 130 forme non riconosciute da Hunspell: elisioni, nomi inventati, prestiti, parole valide assenti dal dizionario (elenco in `fase8-correttore.md`) |
| Lettere doppie o mancanti (parola esistente ma sbagliata) | 0 | 621 parole usate una sola volta e diverse di una lettera da una parola frequente. Ne ho letto in contesto un campione di 55, scelto tra le più sospette (es. «costate», «stirò», «sordi», «torse», «cerato», «rimesse»): tutte corrette |
| Accenti (è/e, né/ne, perché, sì/si, dà/da, lì/li, là/la, c'è, po') | 0 | 4 casi di «e» da verificare (cap. 2 r. 131; cap. 18 r. 183; cap. 24 r. 27; cap. 31 r. 47): sono congiunzioni, corrette |
| Apostrofi ed elisioni (un'/un, qual è, po', d'accordo…) | 0 | 23 casi «un'ora», «un'auto», «un'abitudine»: corretti (femminili) |
| Parole staccate o attaccate per errore | 0 | Nessuna forma unita non riconosciuta. «chi sa» (cap. 47, r. 67) è il pronome relativo, non «chissà»: corretto |
| Doppie parole | 0 | 1 caso, cap. 16 r. 213, «come se se ne accorgesse»: corretto |
| Maiuscola dopo il punto | 0 | 3 casi con minuscola dopo il punto: sono iniziali puntate negli appunti scritti, «F. sa» (cap. 40 r. 95; cap. 47 rr. 74, 90): corretti. Nessun paragrafo comincia con la minuscola |
| Concordanze di genere e numero | 0 | 215 coppie segnalate da un'analisi automatica; le 43 più sospette lette in contesto. Tutti falsi allarmi: nomi invariabili («il file», «la nota spese»), aggettivi riferiti a un altro nome («una porta a vetri aperta», «giacca a vento scura», «una tazza di caffè vuota»), verbi con pronomi («la richiuse») |
| Nomi propri scritti in due modi | 0 | Vedi tabella sotto |
| Punteggiatura sbagliata in modo meccanico (doppi segni, « » o corsivi aperti e non chiusi) | 0 | Nessun caso |

## Nomi propri: coppie controllate

Nessun nome è scritto in due modi. Le coppie simili trovate sono nomi diversi, usati in modo coerente.

| Coppia | Occorrenze | Esito |
|---|---|---|
| Clodio / Clodia | Porto Clodio 36; Clodia Navi 7 | Due nomi diversi (porto e società di navigazione). Corretto |
| Serrana / Serrania | la Serrana 30; Serrania 7 | Due nomi diversi, come in `02-bibbia/nomi-inventati.md`: la Serrana è l'organizzazione (gli affiliati sono i *serrani*), la Serrania è la regione. Corretto |
| Martina / Marina | Martina 13; Marina 2 | «Marina» compare solo in «Aterno Marina» (cap. 17 r. 15; cap. 38 r. 11), nome di luogo. Corretto |
| Rocco / Rocca | Rocco 20; Rocca 16 | Personaggio / Rocca Sannella. Corretto |
| Porto / Porta | Porto Clodio; Porta Vetra 9 | Due luoghi. Corretto |
| De Biasi, De Stefano, AV System, Ardesia Custodia, Casal Fascio, Punta Saline, Rocca Sannella, Porta Vetra | sempre nella stessa grafia | Corretto |
| Via dei Cordai / via dei Cordai | 1 / 25 | La maiuscola compare solo a inizio frase, in un dialogo (cap. 20 r. 19, «Via dei Cordai 14…»). Corretto |
| Padèra, Varnia / varnio, Kaliria, Parsàn | sempre nella stessa grafia | Corretto |

**Da sapere, non è un errore di grafia:** la regione **Serrania** compare a volte senza articolo e a volte con l'articolo.
- **Senza articolo:** «a Serrania» (cap. 3 r. 49; cap. 5 r. 119), «una mappa di Serrania» (cap. 7 r. 71), «portate su da Serrania» (cap. 33 r. 53).
- **Con l'articolo:** «della Serrania» (cap. 3 r. 53; cap. 11 r. 17).

Per una regione l'italiano usa l'articolo («in Calabria», «della Calabria»); per una città no. Se Serrania è una regione, le forme senza articolo diventerebbero:
- cap. 3, r. 49: «Nessuno a Serrania» → «Nessuno in Serrania»;
- cap. 5, r. 119: «sequestrati a Serrania» → «sequestrati in Serrania»;
- cap. 7, r. 71: «una mappa di Serrania» → «una mappa della Serrania»;
- cap. 33, r. 53: «portate su da Serrania» → «portate su dalla Serrania».

È una scelta d'uso, non una svista certa: la lascio a te.

## Metodo

1. **Hunspell `it_IT`** su tutto il testo, in UTF-8: le parole inesistenti.
2. **Ricerche mirate:**
   - accenti (perché/perche, né/ne, è/e davanti a participi e aggettivi, sì/si nelle risposte, dà/da, lì/li, là/la, c'è, po', acuto/grave);
   - apostrofi (un'/un davanti a maschili e femminili, qual è, d'accordo);
   - doppie parole;
   - minuscole dopo il punto e a inizio paragrafo;
   - doppi segni di punteggiatura;
   - virgolette « » e corsivi aperti e non chiusi;
   - grafie alternative della stessa parola (obiettivo/obbiettivo, chissà/chi sa, caffè/caffé, ventitré/ventitre…).
3. **Concordanze:** analisi grammaticale automatica con spaCy (`it_core_news_md`). Segnala articoli e aggettivi che non concordano in genere o numero con il nome vicino. Tutti i casi sospetti sono stati letti in contesto.
4. **Errori di battitura che danno una parola esistente:** elenco delle parole usate una sola volta che differiscono di una lettera da una parola frequente nel libro («pala» per «palla»). Lette in contesto le più sospette.
5. **Nomi propri:** confronto di tutti i nomi con maiuscola per trovare grafie simili, più un controllo dei nomi composti.

**Limite:** questo controllo è fatto con strumenti automatici più la lettura in contesto dei casi segnalati. Non è una rilettura umana riga per riga di tutte le 111.468 parole: errori di senso che formano parole corrette e non sono vicini a parole frequenti (per esempio una parola giusta al posto di un'altra giusta) possono sfuggire. LanguageTool resta non disponibile in questo ambiente (vedi `fase8-correttore.md`).

## Totali per tipo

| Tipo | Totale |
|---|---|
| Refusi | 0 |
| Lettere doppie o mancanti | 0 |
| Accenti | 0 |
| Apostrofi ed elisioni | 0 |
| Parole staccate o attaccate | 0 |
| Doppie parole | 0 |
| Maiuscole dopo il punto | 0 |
| Concordanze evidenti | 0 |
| Nomi propri in due modi | 0 |
| **Totale proposte** | **0** |
| Da decidere (non errori) | 4 righe: uso dell'articolo con «Serrania» |

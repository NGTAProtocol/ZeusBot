# Continuità e serie

Riferimento per il direttore editoriale e l'editor strutturale. Tutto vive nella cartella del libro; nel motore non entra mai un libro.

## Bibbia e stato, due cose separate
- La bibbia è permanente: stile, struttura, personaggi, mondo. Non cambia durante la stesura se non per decisione scritta dell'autore.
- Lo stato del racconto cambia a ogni capitolo: dove sono i personaggi, che cosa portano, che cosa sanno, quale giorno è.
- Lo stato si archivia dopo ogni capitolo approvato; la bibbia no. Così si può sempre risalire a «com'era a quel punto».

## Registro dei fatti
- Un fatto, una riga: identificativo stabile, testo, capitolo-fonte, data di storia.
- Chi sa che cosa, e da quale capitolo: per ogni conoscenza si annota il capitolo in cui il personaggio la apprende e il modo (detto, visto, origliato, dedotto).
- Nessuno agisce su ciò che non sa. Un sapere senza trasmissione è una lacuna da segnalare.
- Si aggiorna la voce esistente, non se ne crea una seconda.
- Se il capitolo contraddice il registro, il conflitto si conserva come «non risolto» finché non decide l'autore.

## Promesse, indizi, domande
- Tre famiglie: promesse (oggetto, giuramento, scadenza), indizi (anche falsi: il pagamento è lo smascheramento), domande del lettore.
- Stati: aperta, sviluppata, pagata (per le domande anche lasciata cadere, solo per scelta scritta).
- Ogni record riporta capitolo di semina, ultimo capitolo in cui è toccato, capitolo atteso di pagamento.
- Un solo record per ogni setup: se lo stesso filo riappare, si aggiorna lo stesso record.
- Errori: pagata senza capitolo di pagamento; pagamento prima della semina; domanda risolta prima di essere posta.
- Avvisi: promessa ferma da tre o più capitoli senza sviluppo; domanda aperta da dodici capitoli o più.
- Esempio: «la lettera sigillata», seminata al cap. 4, toccata al cap. 9, attesa al cap. 18: stato sviluppata.

## Esenzioni motivate
- Sogno, flashback, finale aperto per un seguito: l'autore dichiara la scelta con il motivo, una volta.
- Si registra in un elenco (che cosa, dove, motivo, data) e da quel momento nessun controllo lo ripete.
- Senza motivo scritto, l'esenzione non vale.

## La prosa approvata è canone
- Dopo l'ok dell'autore, il testo vince sul registro: è il registro ad adeguarsi, non il capitolo.
- Se il testo contraddice un fatto già approvato altrove, è un rilievo di continuità; lo risolve l'autore, non il critico.
- Il critico segnala con fonte e capitolo, non indovina le intenzioni e non propone correzioni al canone.

## Motivi ricorrenti
- Ogni frase-firma ha un tetto di usi nel libro intero (di base 3), dichiarato in `libro.yaml` come voce con ambito libro.
- Per alzare il tetto si dichiara la coppia (frase, N) con il motivo; ogni uso oltre il tetto è un rilievo.

## Serie e canone
- La bibbia di serie sta sopra i libri e prevale sul singolo volume per il canone condiviso. Sezioni: libri e ordine, arco di serie e promesse da pagare, regole del mondo con i loro costi, luoghi e tempi, personaggi che ritornano, nomi e grafie canoniche, decisioni datate, questioni aperte per l'autore (che nessuno inventa).
- La bibbia si aggiorna nello stesso salvataggio del libro che cambia il canone.
- Ogni volume dichiara in `libro.yaml` il blocco serie: nome, posizione, bibbia, volume precedente, file da portare.
- Passaggio al volume successivo, dalla cartella del libro precedente:
  - schede dei personaggi, con nuovo controllo dei tic sul cast;
  - registro dei fatti dallo stato finale del precedente, perché «chi sa che cosa» attraversi il confine;
  - voce portata avanti, con nota se cambia;
  - motivi di serie nel nuovo elenco;
  - riga del volume nella tabella della serie.
- Una «passata tra volumi» si fa solo su richiesta: cronologia, flusso di informazioni, fili senza pagamento.

## Estrarre la bibbia da un testo già scritto
Serve per i manoscritti esistenti (`zb adotta`); il testo è dell'autore, la bibbia è sua.
1. Lettura completa: lunghezza e struttura generale.
2. Voce: punto di vista, tempi, circa 50 frasi campione, lessico, verbi dichiarativi, rapporto dialogo/prosa.
3. Personaggi, con tratti, relazioni, battute tipiche.
4. Struttura: atti, svolte, schemi ricorrenti.
5. Luoghi e tempi.
6. Compilazione dei file della bibbia e del registro dei fatti.
- Prove: ogni dato porta la citazione con capitolo e riga; ogni misura dice la dimensione del campione. «È testardo» non vale; vale «rifiuta il soprannome al cap. 2 e insiste a guidare al cap. 5».
- Più analisi (per esempio capitoli letti da subagenti diversi) si uniscono così: si tiene ciò che compare ovunque; i tratti permanenti solo se dimostrati in tutte le apparizioni; il mostrato batte il raccontato; tra due versioni di un fatto prevale il capitolo successivo.
- I conflitti non si risolvono da soli: «le fonti divergono: il cap. 3 dice X, il cap. 12 dice Y». Decide l'autore.
- Al massimo tre giri di estrazione e correzione; poi si porta ciò che resta all'autore.
- Nulla di inventato: se manca una prova, la voce resta vuota.

Fonti delle idee: danjdewhurst/story-skills, knightdx91-alt/Book-pipeline, mrigankad/Novel-OS, forsonny/Claude-Code-Novel-Writer, ThomasHoussin/Claude-Book

# Diagnostica: parole chiave per capitolo

*Controllo automatico, solo analisi. Nessun file del manoscritto, della bibbia, della scaletta o di `semi.md` è stato modificato.*

## Metodo

- **Strumento:** YAKE! 0.7.1 (`pip install yake`), lingua `it`, n-grammi fino a 2, deduplicazione 0,7, prime 10 parole chiave per file.
- **Stopword:** lista italiana di YAKE!, più una lista aggiuntiva di verbi narrativi e parole funzionali ricorrenti («disse», «guardò», «sapeva», «perché», «c'era», «avrebbe», numerali da uno a dieci e simili). Senza di essa le prime posizioni erano occupate da verbi di dialogo e non dicevano niente sul contenuto.
- **Testo analizzato:** i 54 file di `04-manoscritto/`, esclusi titoli, separatori di scena e riga di intestazione (personaggio, luogo, data).
- **KeyBERT:** non installato. Richiede PyTorch e sentence-transformers (diverse centinaia di MB, più il download di un modello); PyTorch non è presente nell'ambiente. Come da istruzioni, si procede solo con YAKE!.
- **Confronto con la scaletta:** per ogni capitolo, sovrapposizione tra i termini delle parole chiave e il testo della voce corrispondente in `03-architettura/scaletta.md`, poi lettura manuale dei casi deboli.
- **Nomi estranei:** ogni parola chiave con iniziale maiuscola è stata cercata in bibbia (incluso `nomi-inventati.md` e schede), scaletta e `semi.md`.
- **Ripetizioni:** somiglianza (indice di Jaccard) tra le parole chiave di capitoli dello stesso punto di vista distanti almeno 10 capitoli, esclusi i nomi dei punti di vista.

Le parole chiave statistiche premiano la frequenza e la posizione, non il senso: nomi propri e oggetti di scena ripetuti tendono a salire. Una sovrapposizione bassa con la scaletta non è di per sé un difetto.

## Parole chiave per capitolo

### Prologo — corale

*Albaterra, Marcena, Merania — 12 novembre*

**Parole chiave:** scese dall'auto · Tommaso · sala · piano · Marcena · Andrea Gatti · scese · dall'auto · portone · mercato

**Termini in comune con la scaletta:** marcena, tommaso

### Capitolo 1 — Tommaso

*Tommaso — Merania, 13 novembre*

**Parole chiave:** Tommaso · Andrea · ACCESSO NEGATO · mail · Tommaso Vela · sala · ACCESSO · tecnico · NEGATO · Merlo

**Termini in comune con la scaletta:** accesso

### Capitolo 2 — Giorgi

*Giorgi — Merania, 12 novembre*

**Parole chiave:** Giorgi · Kurgan · uomini · sistema · Elena · voce · Alfredo Giorgi · telefono · attuatore · sera

**Termini in comune con la scaletta:** giorgi, kurgan, sera, sistema, uomini

### Capitolo 3 — Kurgan

*Kurgan — Partenia, 14 novembre*

**Parole chiave:** Kurgan · uomini · Adorisio · mani · scala · Onorato · Serrana · occhi · Tanino · Carrese

**Termini in comune con la scaletta:** kurgan, tanino, uomini

### Capitolo 4 — Tommaso

*Tommaso — Merania, 4 dicembre*

**Parole chiave:** Tommaso · novembre · riga · Fondazione · nota standard · Fondazione Civitas · piano · Martina · Ricci · Tommaso Vela

**Termini in comune con la scaletta:** fondazione

### Capitolo 5 — Flora

*Flora — Albaterra, 25 novembre*

**Parole chiave:** Flora · Calabrese · Cataldo · fascicolo · notte · Corte · maggio · undici · Flora Notarangelo · tavolo

**Termini in comune con la scaletta:** calabrese, cataldo

### Capitolo 6 — Dalia

*Dalia — Merania, 9 dicembre*

**Parole chiave:** Dalia · Alfredo · Vito · stanza · mano · chiesto · paura · letto · porta · un'ora

**Termini in comune con la scaletta:** stanza

### Capitolo 7 — Kurgan

*Kurgan — Porto Clodio, 20 dicembre*

**Parole chiave:** Kurgan · Rastegar · Punta Saline · busta · piano · Saline · Adorisio · Punta · scale · libro

**Termini in comune con la scaletta:** adorisio, rastegar

### Capitolo 8 — Giorgi

*Giorgi — Vaticano, 6 gennaio*

**Parole chiave:** Giorgi · Salvarani · Kurgan · tazza · terza tazza · cardinale · Partenia · Giorgi avesse · cardinale Salvarani · tavolo

**Termini in comune con la scaletta:** giorgi, kurgan, partenia, salvarani

### Capitolo 9 — Flora

*Flora — Albaterra, 22 gennaio*

**Parole chiave:** Flora · Calabrese · Carlo · Valdhof · dati · porta · telefono · soggetti · settimane · trentuno

**Termini in comune con la scaletta:** calabrese

### Capitolo 10 — Kurgan

*Kurgan — statale costiera, 7 febbraio*

**Parole chiave:** Volkov · Kurgan · Punta Saline · uomini · Partenia · navi · socio · carte · furgone · Undici

**Termini in comune con la scaletta:** kurgan, partenia, punta, saline, volkov

### Capitolo 11 — Dalia

*Dalia — Partenia, 17 maggio*

**Parole chiave:** Vito · Dalia · stanza · Partenia · mano · testa · telefono · mani · Alfredo · silenzio

**Termini in comune con la scaletta:** partenia

### Capitolo 12 — Giorgi

*Giorgi — Merania, Albaterra, 11 maggio dell'anno seguente*

**Parole chiave:** Giorgi · Kurgan · Laura · telefono · stanza · numero vero · Punta Saline · stava · numero · Elena

**Termini in comune con la scaletta:** giorgi, kurgan, laura

### Capitolo 13 — Kurgan

*Kurgan — Punta Saline, 18 maggio dell'anno seguente*

**Parole chiave:** Kurgan · Porto · uomini · Porto Clodio · bambina · Adorisio · macchina · L'autista · telefono · foglio

**Termini in comune con la scaletta:** uomini

### Capitolo 14 — Elena

*Elena — Merania, 19 maggio*

**Parole chiave:** Elena · Alfredo · Laura · Sergio · macchina · telefono · Fabrizio · maresciallo · scuola · mano

**Termini in comune con la scaletta:** scuola, telefono

### Capitolo 15 — Flora

*Flora — Albaterra, 27 maggio*

**Parole chiave:** Flora · Merania · Calabrese · nome · Oddone · procuratore · foglio · bambina · Cataldo · Maresciallo Oddone

**Termini in comune con la scaletta:** flora, maresciallo, merania, nome, oddone

### Capitolo 16 — Dalia

*Dalia — Merania, 28 maggio*

**Parole chiave:** Dalia · Alfredo · Vito · stanza · finestra · domenica · occhi · letto · mano · martedì

**Termini in comune con la scaletta:** stanza

### Capitolo 17 — Giorgi

*Giorgi — Merania, 31 maggio*

**Parole chiave:** Kurgan · Giorgi · bambina · generale · tavolo · schermo · foglio · sottosegretario · uomini · l'americano

**Termini in comune con la scaletta:** bambina, giorgi, kurgan, tavolo

### Capitolo 18 — Kurgan

*Kurgan — Partenia, 16 giugno*

**Parole chiave:** Kurgan · Serrana · Rastegar · Onorato · Carrese · Chen · navi · uomini · cinese · banchina

**Termini in comune con la scaletta:** banchina, carrese, chen, onorato, rastegar, serrana

### Capitolo 19 — Elena

*Elena — Merania, 20 giugno*

**Parole chiave:** Elena · Alfredo · Laura · telefono · martedì · parola · nome · madre · cucina · maggio

**Termini in comune con la scaletta:** elena, telefono

### Capitolo 20 — Flora

*Flora — Rocca Sannella, 26 giugno*

**Parole chiave:** Flora · Porto Clodio · Carlo · Valdhof · porto · Clodio · madre · Albaterra · studio · trentuno

**Termini in comune con la scaletta:** carlo, clodio, flora, porto, valdhof

### Capitolo 21 — Giorgi

*Giorgi — Merania, 28 giugno*

**Parole chiave:** Giorgi · Bertola · Kurgan · supervisore · variabile · piano · generale · regolatore · aprisse bocca · tavolo

**Termini in comune con la scaletta:** bertola, giorgi, kurgan, variabile

### Capitolo 22 — Elena

*Elena — Merania, 29 giugno*

**Parole chiave:** Elena · Alfredo · telefono · vestito · porta · macchina · tasca · Ferri · Passi · letto

**Termini in comune con la scaletta:** elena, telefono, vestito

### Capitolo 23 — Dalia

*Dalia — Merania, 29 giugno*

**Parole chiave:** Dalia · punto interrogativo · Alfredo · Vito · chiesto · frase · Stasera · settimana · sera · telefono

**Termini in comune con la scaletta:** dalia

### Capitolo 24 — Kurgan

*Kurgan — Riva Salmara, 29 giugno, 12.51*

**Parole chiave:** Kurgan · contabile · porta · cucina · Riva Salmara · Carrese · Rocco · conto · strada · Porto Clodio

**Termini in comune con la scaletta:** contabile, kurgan, riva, salmara

### Capitolo 25 — Dalia

*Dalia — Merania, 29 giugno, sera*

**Parole chiave:** Riva Salmara · Dalia · voce · telefono · vestito blu · all'anta dell'armadio · Pietro · Salmara · Riva · Dalia rientrò

**Termini in comune con la scaletta:** nessuno

### Capitolo 26 — Giorgi

*Giorgi — Albaterra, 2 luglio*

**Parole chiave:** Giorgi · Adorisio · Biasi · uomini · Bertola · nome · accanto · macchina · foglio · stava

**Termini in comune con la scaletta:** adorisio, bertola, biasi, giorgi, nome

### Capitolo 27 — Flora

*Flora — Albaterra, 5 luglio*

**Parole chiave:** Flora · Calabrese · foglio · Riva Salmara · Cataldo · Kurgan · Busta · Porto Clodio · martedì · quarto

**Termini in comune con la scaletta:** calabrese, cataldo, clodio, foglio, porto, riva, salmara

### Capitolo 28 — Elena

*Elena — Merania, 25 luglio*

**Parole chiave:** Elena · Alfredo · chiavi · porta · cassetto · Laura · chiavetta · cordino · fondo · faceva

**Termini in comune con la scaletta:** cassetto, chiavetta, chiavi, elena, laura

### Capitolo 29 — Giorgi

*Giorgi — Punta Saline, 10 agosto*

**Parole chiave:** Giorgi · Laura · Elena · Tanino · fari spenti · motore acceso · portiera · luglio · fosse · Adorisio

**Termini in comune con la scaletta:** adorisio, laura, tanino

### Capitolo 30 — Dalia

*Dalia — Merania, 18 agosto*

**Parole chiave:** Dalia · ottobre · mercato · Trenta righe · Trenta · Consob · Giovedì · novembre · agosto · notizia

**Termini in comune con la scaletta:** agosto, righe, trenta

### Capitolo 31 — Flora

*Flora — Albaterra, 23 agosto*

**Parole chiave:** Flora · settimo foglio · Calabrese · foglio · banchiere · undici · Carlo · settimo · Partenia · Lanterna

**Termini in comune con la scaletta:** calabrese, flora, partenia

### Capitolo 32 — Elena

*Elena — Merania, 27 agosto*

**Parole chiave:** Elena · Laura · Alfredo · riga · sera · porta · numero · data · fosse · Elena aspettò

**Termini in comune con la scaletta:** elena, laura

### Capitolo 33 — Giorgi

*Giorgi — Merania, notte tra il 29 e il 30 agosto*

**Parole chiave:** Giorgi · Biasi · Bertola · Casal Fascio · Adorisio · telefono · generale · orario ferroviario · sistema · Laura

**Termini in comune con la scaletta:** adorisio, bertola, biasi, casal, fascio, giorgi, sistema

### Capitolo 34 — Tommaso

*Tommaso — Merania, 16 settembre*

**Parole chiave:** Tommaso · fattura · nome · file · pesava quattrocento · quattrocento kilobyte · undici · Sestante · senatore · Undici fatture

**Termini in comune con la scaletta:** fattura, fatture, file, sestante

### Capitolo 35 — Carlo

*Carlo — Albaterra, 27 settembre*

**Parole chiave:** capo reparto · Carlo · capo · Rocca Sannella · reparto · Flora · foglio · Albaterra · Carlo conosceva · Rocca

**Termini in comune con la scaletta:** albaterra, flora, rocca, sannella

### Capitolo 36 — Flora

*Flora — Albaterra, 5 ottobre*

**Parole chiave:** Flora · Cataldo · colonna · numero · Calabrese · nome · richiesta · Undici · senatore · Cordai

**Termini in comune con la scaletta:** cordai, flora, nome

### Capitolo 37 — Giorgi

*Giorgi — Vaticano, 20 ottobre*

**Parole chiave:** Giorgi · Salvarani · senatore · Cicimarra · Parlamento · Conosceva · tazza · cravatta blu · Alfonso Cicimarra · paura

**Termini in comune con la scaletta:** cicimarra, giorgi, salvarani

### Capitolo 38 — Tommaso

*Tommaso — Merania, 15 novembre*

**Parole chiave:** Tommaso · Venerdì · riga · Marcena · intermediario · Trentuno · novembre · mattina · codice · commissione

**Termini in comune con la scaletta:** commissione, novembre, trentuno, venerdì

### Capitolo 39 — Flora

*Flora — Albaterra, 23 novembre*

**Parole chiave:** Flora · procuratore · Cataldo · Task force · decreto · trenta · Calabrese · giudice · lunedì · legge

**Termini in comune con la scaletta:** decreto, force, giudice, legge, lunedì, task, trenta

### Capitolo 40 — Elena

*Elena — Merania, 30 novembre*

**Parole chiave:** Elena · Alfredo · chiavetta · banca · riga · nome · porta · lista · portatile · Fabrizio

**Termini in comune con la scaletta:** banca, chiavetta, elena, fabrizio, nome, porta, portatile

### Capitolo 41 — Dalia

*Dalia — Merania, 15 dicembre*

**Parole chiave:** Vito · Dalia · NOVEMBRE · profumo caro · punto interrogativo · Trentuno · agosto · punto · redazione · telefono

**Termini in comune con la scaletta:** dalia, novembre, redazione, telefono

### Capitolo 42 — Giorgi

*Giorgi — Albaterra, 15 dicembre*

**Parole chiave:** Giorgi · voti favorevoli · metri dall'aula · quattrocento metri · undici rispetto · sera · sistema · momento · registrò · Salvarani

**Termini in comune con la scaletta:** favorevoli, giorgi, salvarani, sera, sistema

### Capitolo 43 — Dalia

*Dalia — Merania, 16 dicembre*

**Parole chiave:** Dalia · telefono · direttore · telefono squillò · pagina · voce · numeri · Pietro · minuto · nome

**Termini in comune con la scaletta:** direttore, pietro, telefono

### Capitolo 44 — Flora

*Flora — Albaterra, 22 dicembre*

**Parole chiave:** Flora · Cataldo · Calabrese · Carlo · Porto Clodio · notte · carte · citofono suonò · Rocca Sannella · terzo

**Termini in comune con la scaletta:** calabrese, carlo, carte, cataldo, clodio, flora, notte, porto

### Capitolo 45 — Carlo

*Carlo — Albaterra, 23 dicembre*

**Parole chiave:** Carlo · capo reparto · Rocca Sannella · macchina · bagagliaio · capo · reparto · cortile · Cataldo. · Natale

**Termini in comune con la scaletta:** capo, carlo, cataldo, cortile, macchina, natale, reparto, rocca, sannella

### Capitolo 46 — Dalia

*Dalia — Merania, 28 dicembre*

**Parole chiave:** Dalia · firma · dichiarazione · giornale · direttore · madre · busta · pezzo · firma dell'articolo · fondo

**Termini in comune con la scaletta:** busta, dichiarazione, giornale, madre

### Capitolo 47 — Elena

*Elena — Merania, 29 dicembre*

**Parole chiave:** Elena · Alfredo · nome · cucina · Laura · file · penna blu · Fabrizio · busta · scritto

**Termini in comune con la scaletta:** busta, elena, fabrizio, file, scritto

### Capitolo 48 — Tommaso

*Tommaso — Merania, Albaterra, 18 gennaio*

**Parole chiave:** Tommaso · arrivata lunedì · Cataldo · riga · Flora · piano · accanto · minuti · Albaterra · treno

**Termini in comune con la scaletta:** albaterra, cataldo, flora, piano, treno

### Capitolo 49 — Giorgi

*Giorgi — Vaticano, 21 gennaio*

**Parole chiave:** Giorgi · Salvarani · cardinale · ragazzo · vassoio · giudice · stanza · mani · tazza · sigla

**Termini in comune con la scaletta:** giudice, salvarani

### Capitolo 50 — Flora

*Flora — Albaterra, 29 gennaio*

**Parole chiave:** Flora · nome · riga · numero · giudice · foglio · notaio · maresciallo · Accanto · Cataldo

**Termini in comune con la scaletta:** foglio, numero, riga

### Capitolo 51 — Giorgi

*Giorgi — Castelvaro, lago di Varo, 30 gennaio*

**Parole chiave:** Giorgi · barca · barcaiolo · taglio vecchio · riva · pontile · mano · l'altra barca · comando · sistema

**Termini in comune con la scaletta:** barca, giorgi, mano, sistema

### Capitolo 52 — Flora

*Flora — Castelvaro, 31 gennaio*

**Parole chiave:** Flora · Giorgi Alfredo · maresciallo · macchina · circolo · domenica · Riga · Alfredo · Giorgi · nome

**Termini in comune con la scaletta:** flora, giorgi

### Capitolo 53 — Elena

*Elena — Merania, 15 febbraio*

**Parole chiave:** Elena · mani · mano · Laura · accanto · l'avvocato · frase · Duomo · chiavetta · porta

**Termini in comune con la scaletta:** accanto, avvocato, chiavetta, laura

## Somiglianze tra capitoli dello stesso punto di vista (distanza ≥ 10)

| Indice | Capitoli | Punto di vista | Termini comuni |
|---|---|---|---|
| 0,42 | 6 e 16 | Dalia | alfredo, letto, mano, stanza, vito |
| 0,33 | 35 e 45 | Carlo | capo, reparto, rocca, sannella |
| 0,29 | 19 e 47 | Elena | alfredo, cucina, laura, nome |
| 0,29 | 15 e 50 | Flora | cataldo, foglio, maresciallo, nome |
| 0,29 | 3 e 18 | Kurgan | carrese, onorato, serrana, uomini |
| 0,25 | 23 e 41 | Dalia | interrogativo, punto, telefono, vito |
| 0,24 | 27 e 44 | Flora | calabrese, cataldo, clodio, porto |
| 0,23 | 8 e 49 | Giorgi | cardinale, salvarani, tazza |
| 0,2 | 36 e 50 | Flora | cataldo, nome, numero |
| 0,2 | 28 e 53 | Elena | chiavetta, laura, porta |

## Sintesi: capitoli da verificare

Su 54 file, **3 segnalazioni** (una per ciascun criterio). Gli altri 51 capitoli hanno parole chiave riconoscibilmente legate al conflitto previsto dalla scaletta, nessun nome fuori registro e nessuna ripetizione sospetta.

| Capitolo | Criterio | Motivo | Cosa guardare |
|---|---|---|---|
| **1** (Tommaso) | Nome estraneo | «Merlo» (Sandro Merlo, il responsabile che piange davanti alla vetrata) è tra le parole chiave ma non compare in bibbia, `nomi-inventati.md`, schede, scaletta o `semi.md`. È l'unico nome delle parole chiave fuori registro. | Se Sandro Merlo va aggiunto al registro dei nomi o se il personaggio deve restare senza nome. |
| **25** (Dalia) | Nessun collegamento con la scaletta | È l'unico capitolo con sovrapposizione zero. Le parole chiave (Riva Salmara, voce, telefono, vestito blu, anta dell'armadio, Pietro) puntano sulla notizia e sugli oggetti di scena; non emergono Vito, il sollievo né il «da solo, come sempre» che la scaletta mette al centro. | Se il ritorno del dettaglio «da solo, come sempre» pesa abbastanza rispetto alla scena del vestito e dell'armadio. |
| **6 e 16** (Dalia) | Ripetizione tra capitoli lontani | Indice 0,42, il più alto del libro: alfredo, letto, mano, stanza, vito. Stessa stanza 512, stessa coppia, dieci capitoli di distanza. La scaletta prevede entrambi nella 512, quindi l'ambientazione è voluta; la somiglianza dei termini è però superiore a qualunque altra coppia. | Se il capitolo 16 ripete i gesti del 6 (letto, mani, domande su Vito) oltre a quanto serve per far sentire che «Giorgi è diverso». |

**Somiglianze viste e non segnalate:**
- **35 e 45 (De Stefano), indice 0,33:** capo reparto e Rocca Sannella in entrambi. È continuità prevista (il diniego del comando e la bugia sul fico), fissata in scaletta e nelle note del 45 in `semi.md`.
- **Le altre coppie** (0,29 o meno) condividono solo nomi di personaggi fissi o parole generiche (cucina, nome, porta).

**Casi deboli verificati a mano e non segnalati:** i capitoli 9, 13, 23 e 53 hanno poca sovrapposizione lessicale con la scaletta, ma le parole chiave sono chiaramente pertinenti: Valdhof e Carlo per la pista dei soldi (9), Porto Clodio, bambina e autista per il piano del rapimento (13), «Stasera» e il punto interrogativo per l'incontro annullato (23), chiavetta, avvocato e Duomo per la vedovanza e la cassetta (53).

## Esito della verifica sul testo (dopo la sintesi)

### Capitolo 1: Sandro Merlo
Aggiunto a `02-bibbia/nomi-inventati.md`, nuova sezione «Persone minori», con una riga coerente con la sua unica apparizione (capo del desk, cinquantadue anni, diciassette in sala, le tre regole del 13 novembre). `comprimari.md` non ha una sezione per il capitolo 1, quindi non è stato toccato. Il testo del capitolo è invariato.

### Capitolo 25: falso allarme
Il dettaglio c'è ed è il perno della scena. La testimone al telegiornale dice: «C'era un signore grande, altissimo, seduto dentro da solo. Aspettava qualcuno.» Subito dopo, su una riga isolata: «*Da solo.*» E poi il ricordo della frase detta da Dalia nella 512: «*Con lui va da solo. Sempre. È la condizione. In mezzo alla gente. All'ora di pranzo.*», seguito da «Un'esplosione non prendeva nessuno.» È il motivo per cui il lettore capisce che Kurgan è andato a un appuntamento fatale e che l'informazione veniva da lei. YAKE! non lo ha colto perché «da» e «solo» sono entrambe stopword italiane: l'espressione è invisibile all'estrazione.

### Capitoli 6 e 16: falso allarme per la ripetizione, ma un difetto reale nel 16
La somiglianza delle parole chiave (stanza, letto, mano) viene dall'ambientazione prevista nella 512. Il capitolo 16 è costruito come rovesciamento del 6, con segni espliciti:
- **Capitolo 6:** «Quella sera il sorriso aveva qualcosa in più. Un'ombra agli angoli.»; «Sapeva tutto di lei. Era questo, all'inizio, che le aveva fatto paura.»; «Eccola, pensò Dalia. La frase con dentro due frasi.»; «Messe in fila, adesso, le sembravano un'altra cosa. Le sembravano una scheda.»; «Anche Vito, quando mentiva, aveva il battito calmo.»; «Si chiese, davanti allo specchio, se anche quel centimetro fosse stato calcolato.» Il sospetto nasce, ma dentro l'intimità di sempre.
- **Capitolo 16:** il messaggio del venerdì «non aveva il punto interrogativo»; «In sei anni non l'aveva mai ringraziata di essere venuta. […] Non si ringraziava un patto.»; «Per la prima volta in sei anni, nella 512, non si toccarono.»; «Mi chiedi di Vito come si chiede di un uomo che si deve trovare.»; «Non era una promessa. Era una descrizione.»; «Mi rispondi come a una riunione.»; «Ho paura»; «Non più la donna del martedì. Un pezzo.»; «Non fecero l'amore.»; «Non disse *martedì*.»; «Una faccia nuda».

**Difetto reale trovato rileggendo il 16:** la chiusura rivista in fase 2 («Dalia guardò il bicchiere sul tavolino. Il ghiaccio si era sciolto del tutto.») si appoggia a un oggetto che nel capitolo 16 non esiste. Nel 16 non c'è nessun bicchiere e nessun ghiaccio: il bicchiere d'acqua era nel capitolo 6. Da correggere con un oggetto già in scena (per esempio la manica della giacca, il velluto della poltrona, il telefono girato a faccia in giù). Non applicato in questa fase.

## Chiusura della revisione

### Verifica sul capitolo 16 (giacca)
La giacca in scena è di Alfredo, non di Kurgan. È sulla sedia (righe 33 e 213), ma alla riga 225 Alfredo «Si rimise la giacca.» prima di uscire. La chiusura proposta con la giacca («La giacca era di nuovo sulla sedia…») avrebbe contraddetto il testo e non è stata applicata.

### Modifiche applicate
- **Capitolo 16, chiusura.** Prima: «Lo disse piano, e troppo a lungo. Dalia guardò il bicchiere sul tavolino. Il ghiaccio si era sciolto del tutto.» Dopo: «Lo disse piano, e troppo a lungo. Dalia sentiva ancora sotto il pollice il filo tirato del velluto.» Il velluto della poltrona è in scena (il filo tirato con il pollice) e il capitolo 25 lo riprende.
- **Capitolo 5, chiusura della prima scena.** Prima: «…con la borsa sulle ginocchia, e aspettò che la chiamassero.» Dopo: «…con le mani in grembo, e aspettò che la chiamassero.» Flora arriva con due scatoloni tra le braccia e nessuna borsa è mai nominata.

### Controllo degli oggetti nelle chiusure riviste
Verificate le 9 chiusure sostituite e la chiusura del capitolo 35. Unico oggetto assente: bicchiere e ghiaccio del capitolo 16, ora corretti. Punto debole corretto: la borsa del capitolo 5. Oggetti introdotti dalla chiusura stessa senza contraddizione: cameriere (18), cappuccio della penna (26), taccuino del maresciallo (52).

### Decisione sul capitolo 52
Il taccuino del maresciallo resta com'è: nessuna contraddizione, solo un oggetto nominato per la prima volta nella chiusura.

### PDF
`05-output/il-padre-del-mostro-completo.pdf` rigenerato (A5, EB Garamond): 494 pagine, indice verificato. Manoscritto: 111.547 parole (prologo e 53 capitoli).

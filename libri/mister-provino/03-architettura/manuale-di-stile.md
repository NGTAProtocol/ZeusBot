# Mister Provino — Manuale di stile

Versione 1 (Fase 3). Vale per ogni riga del romanzo nuovo. Tra i valori, quelli marcati [PROPOSTA] vanno confermati.

---

## 0. Regola zero: niente riciclo

- Il vecchio testo è un registro dei fatti. **Nessuna frase si copia, si adatta o si «migliora».** Ogni scena si scrive partendo dalla scaletta e dalla bibbia, non dalla pagina vecchia.
- Se durante la stesura affiora una frase del vecchio testo, o la sua struttura (lo stesso attacco, la stessa battuta finale, la stessa similitudine), va riscritta da capo.
- **Controllo automatico [PROPOSTA]:** prima della consegna di ogni capitolo, uno script in `06-diagnostica/` cerca sequenze di **7 o più parole consecutive** in comune con il vecchio testo. Ogni riscontro si riscrive, tranne le battute canoniche elencate qui sotto.
- **Battute canoniche** ammesse perché sono fatti del romanzo, non stile. Si possono dire con parole identiche:
  - «Non lo sprecare» (il Capo);
  - «Al mio amico Beniamino, con affetto» (la dedica sulla maglia);
  - «è matematica, non cattiveria» (Nicola);
  - «Tu il giuramento l'hai mantenuto, fratello mio. Io il mio no.» (Checco);
  - «Tutto si aggiusta, solo la morte è una fine vera» (O Anjo, forma libera);
  - «Finalmente» (Michele);
  - «Le mie mani avevano aiutato» (il vecchio, cap. 10; una volta sola, con l'eco del cap. 36);
  - «Si chiamava Lucia.» (Michele, cap. 37);
  - «La scelta c'è sempre, anche all'ultimo.» (Michele, cap. 12; ultima volta nell'epilogo);
  - «Una vita non detta si perde due volte» (di Michele, nel prologo e nell'interludio IX);
  - «E se anche fosse?» (Nicola, cap. 19);
  - «Uno si abitua.» (Saro, cap. 25; eco nel cap. 26);
  - «Beniamino… non ti lascio» (Nicola, cap. 24);
  - «Ti porto via da qua» (Checco, cap. 18);
  - «Allora non vado.» (Beniamino, cap. 34);
  - «Il cugino di Nicola. Una guardia.» (il magro, cap. 36);
  - «Stai zitto.» (la madre, cap. 17);
  - «A che ora parte questo transatlantico?» (Michele, cap. 37);
  - «PER FRANCO. PER LA VESPA, E PER TUTTO IL RESTO.» (la busta gialla, cap. 39).

---

## 1. Che libro è

**Romanzo di formazione letterario, retrospettivo, a doppia voce.** Il crimine è il paesaggio, non il genere. Il lettore deve uscire dal libro con la sensazione di aver vissuto un'estate a Bari Vecchia, non di aver letto un thriller.

Riferimenti di registro, da tenere a mente e da non imitare:
- **Starnone, *Via Gemito*:** l'adulto che ricostruisce, dubita, corregge la propria memoria e la mette sotto accusa.
- **Fenoglio, *La malora*:** la sobrietà; il dolore detto senza commento; il dialetto che affiora nella sintassi più che nelle parole.
- **De Silva, *Certi bambini*:** un ragazzo dentro il crimine, raccontato senza compiacimento e senza pietismo.

**Obiettivi numerici:**
- **78.000 parole** complessive;
- prima persona;
- racconto al passato, con gli interludi al presente;
- **frase media 10-13 parole** per capitolo (il vecchio testo stava a 9,7);
- dialogo tra il 15% e il 35% per capitolo;
- nessun capitolo sotto le 1.300 parole; la media è di circa 1.700 (vedi scaletta).

**Metodo unico di conteggio delle parole.** Vale per il target, per la scaletta, per il registro dei contatori e per ogni confronto con il vecchio testo:
- si contano i token separati da spazi (spazio, a capo, tabulazione);
- **si escludono le righe di titolo Markdown** (che cominciano con «#»);
- **si escludono i token senza nessuna lettera e nessuna cifra**: la lineetta «—» isolata dei dialoghi, i «•» dei separatori di scena, ogni altro segno da solo.

Con questo metodo il vecchio testo vale **49.998 parole**. Il target di **78.000** si misura nello stesso modo. Non si usano altri conteggi: `wc -w` dà 49.945 o 51.664 a seconda della lingua di sistema; contare tutti i token esclusi i titoli dà 51.543.

---

## 2. Le due voci

### 2.1 Il ragazzo (la scena)
- Il racconto è al **passato remoto**, con l'imperfetto per gli sfondi e le abitudini.
- **Il ragazzo capisce solo quello che può capire a tredici anni.** Percepisce con i sensi, con i conti, con le mani. Vede il gesto e non sempre il motivo.
- Il lessico è quello dell'uomo che scrive (un italiano pulito, non ricercato), ma **l'intelligenza della scena è del ragazzo**: niente sintesi morali dentro la scena.
- **Divieto assoluto:** prestare al ragazzo aforismi dell'adulto. Una frase come «la compassione verso un padre è già una forma di lutto» non può stare nella testa di un tredicenne sotto il neon. Se è vera e serve, la dice il vecchio, fuori dalla scena e con lo scarto segnato.

### 2.2 Il vecchio dentro il racconto (le intrusioni)
- Ogni intrusione **segna lo scarto temporale** con un'àncora esplicita: «allora non lo sapevo», «quel giorno», «l'ho saputo anni dopo», «oggi», «da vecchio», «me lo raccontò Carlo».
- **Tipi ammessi:**
  1. **correzione:** allora credevo X, non era così;
  2. **prolessi:** lo avrei rivisto una volta sola;
  3. **fonte:** questo non l'ho visto, me l'hanno raccontato;
  4. **dubbio di memoria:** non ricordo se fosse martedì;
  5. **giudizio su di sé**, raro e mai assolutorio.
- **Quantità:** da 1 a 3 intrusioni per capitolo, di 1-3 frasi l'una, con alcuni capitoli a zero (il cap. 10 resta puro: nessuna intrusione). Un'intrusione più lunga (un paragrafo) al massimo una volta ogni 3 capitoli.
- **Aforismi del vecchio:** al massimo uno ogni due capitoli (circa 20 nel libro), e solo dentro un'intrusione marcata.
- **Il vecchio non anticipa i colpi di scena del capitolo in corso.** Può anticipare esiti lontani (Checco che non uscirà più) per dare peso alle scene vicine.

### 2.3 Gli interludi (il presente)
- **Presente indicativo.** Da 300 a 600 parole. Un solo **piccolo evento del presente** (i fiori, la nave, una lettera, una telefonata, la mano ferma sulla pagina) che si specchia con la scena accanto, senza spiegarla.
- **Niente riassunti di trama e niente date.** Nessun oggetto che dati il presente (niente cellulari, computer, schermi): il telefono è «il telefono».
- **Personaggi del presente:** la moglie (mai nominata [PROPOSTA]), la figlia al telefono, il figlio che viene di rado, il mare, la nave. Nessun personaggio del 1976 compare vivo nel presente.
- **Formato:** gli interludi non hanno numero di capitolo. Portano un titolo breve, 1-2 parole, in corsivo (per esempio *I fiori*, *La nave*), e stanno tra due capitoli.

### 2.4 Voce d'autore
Da compilare dopo l'approvazione della pagina campione.

### 2.5 Il nome di Lucia
Il nome «Lucia» **non compare prima del cap. 37**: né nel racconto, né nel prologo, né negli interludi I-VI. Fino ad allora il narratore scrive «lei» o «il ritratto». Dal cap. 37 in poi (interludi VII-IX ed epilogo compresi) il nome si usa sempre (bibbia §5.8).

---

## 3. Ritmo e costruzione

### 3.1 Frase e paragrafo
- La frase media sta tra 10 e 13 parole, con **periodi lunghi (25-45 parole) alternati a frasi brevi**. Il periodo lungo porta sensazioni e movimento; la frase breve porta il fatto.
- Mai più di **3 frasi sotto le 6 parole di fila**.
- Al massimo **3 paragrafi di una sola frase breve** per capitolo (il vecchio testo ne aveva 219 in tutto).
- Niente elenchi di tre aggettivi. Niente coppie di aggettivi in chiusura di frase («luminosa, infinita»).

### 3.2 Scena e riassunto
- **Ogni capitolo ha almeno una scena in tempo reale di 800 o più parole**: un luogo, un tempo continuo, corpi che si muovono.
- Il riassunto è ammesso **solo come ponte**, al massimo 150 parole per ponte, e mai per un evento canonico. L'estate, i sette giorni di Checco, la traversata e l'arrivo vanno vissuti, non riassunti.
- **Gli oggetti fanno il lavoro delle emozioni:** il golf, la teca, il vasetto dei fiori, l'accendino, le sgagliozze, la borraccia, il cavalletto del Ciao.

### 3.3 Aperture
- **Nessun capitolo si apre con una data** come prima frase. La data del 13 luglio 1976 compare nel cap. 1, ma non in apertura.
- **Al massimo 3 capitoli su 43 si aprono con un risveglio** (il vecchio testo lo faceva di continuo).
- **Aperture preferite:** un luogo in movimento, un oggetto, una battuta di dialogo, un'azione già cominciata.

### 3.4 Chiusure
- **Sentenza tematica** (una frase che enuncia il senso): **al massimo 8 capitoli su 43**, mai due di fila. L'epilogo è escluso dal conto.
- **Tutti gli altri capitoli chiudono su:** un gesto, un oggetto, una battuta di dialogo, un'immagine concreta o un fatto semplice.
- **Nessun capitolo chiude con una frase di una o due parole** isolata a capo («Uno di loro.», «Io.»).

### 3.5 Formule contate (registro in fondo)

| Formula | Massimo nel libro |
|---|---|
| «Non era X. Era Y.» / «Non fu X. Fu Y.» e varianti con «non... ma» in due frasi | **5** |
| «Era peggio.» / «qualcosa di peggio» | 2 |
| «come si + verbo» (come si guarda, come si dice) | 1 per capitolo |
| «Non risposi.» / «Non disse niente.» come battuta isolata | 1 per capitolo |
| «una specie di» | 10 |
| «qualcosa di» + aggettivo (qualcosa di freddo, di antico) | 1 per capitolo |
| «come se» | 2 per capitolo |
| «fischiare» / il fischio in senso morale | **6** apparizioni esplicite: cap. 10, cap. 23, cap. 35, interludio VII, cap. 39, epilogo. I capp. 9, 17 e 19 funzionano senza il verbo |

### 3.6 Il tic del contare
Contare è un tratto di Beniamino (passi, ore, soldi, secondi, gradini, mazzette), ma ripetuto diventa un tic dell'autore. Tetto: **al massimo 3 gesti di conteggio per capitolo**, inclusi quelli del narratore adulto. Un elenco di conteggi nella stessa frase vale come un gesto solo. Il conteggio dei gesti va annotato nel registro dei contatori (sezione 9).

---

## 4. Immagini e similitudini

### 4.1 Tetto
Al massimo **una similitudine per pagina**, circa una ogni 300 parole.

### 4.2 Campi ammessi
Le similitudini sono **concrete** e vengono dal mondo del ragazzo e da quello di Michele:
- il mare e la pesca: reti, ricci, polpi, cassette, ghiaccio, nafta, gozzi;
- la cucina: brodetto, pane, olio, sale, pentola, fornello, soffritto;
- l'officina e il motore: Ciao, catena, candela, cavalletto, olio del motore;
- il mercato, la chiesa di quartiere, il pallone, la staccia, il cortile dei panni;
- la pittura (solo attraverso Michele): olio, trementina, tela, spatola, blu cobalto.

### 4.3 Immagini vietate
Divieto assoluto:
- «lama», in ogni senso figurato (di luce, di sole, di sorriso, d'acqua); ammessa solo la lama vera di un coltello, e al massimo 3 volte nel libro;
- «il cuore come un uccello in gabbia» e ogni «cuore» che martella, batte all'impazzata o sta in gola;
- «il silenzio si fece piombo», e ogni silenzio denso, assordante, di pietra, che pesa;
- «reliquia», «come una reliquia», e il campo sacro applicato agli oggetti (altare, sacro, religioso);
- «faceva più paura così», e ogni «era questo a fare paura»;
- «in un battito di ciglia»;
- «statue» e «statue di sale», per persone immobili;
- «come un animale in gabbia», «come un cane bastonato», «come una bestia», per esseri umani (il campo del «cane» è riservato al nome e al collare; vedi 4.4);
- «il sangue mi si gelò», «un brivido lungo la schiena», «gelo nelle vene»;
- «in quel preciso istante», «il mondo si fermò», «il tempo si fermò»;
- «occhi di ghiaccio», «un sorriso che non arrivava agli occhi»;
- «qualcosa si spezzò dentro di me», «qualcosa dentro di me cambiò»;
- «come acqua nera», «sentinelle nere», «cassa armonica»;
- «ingranaggio», per descrivere il sistema criminale.

### 4.4 Il campo del cane
«Cane», «guinzaglio», «collare», «cane da tartufo» sono **il nucleo del titolo della Parte prima** e del collare dell'Aspromonte. Si usano **al massimo 8 volte in tutto il libro**, e mai come similitudine generica.

### 4.5 Emozioni
**Non si spiega l'emozione dopo averla mostrata.** Vietate le formule «Non era coraggio, non era rabbia. Era resa.» e «Provai qualcosa che non sapevo nominare». Se la scena ha mostrato, basta. Se deve dire, lo dice il vecchio con lo scarto segnato (2.2).

### 4.6 Lo schema vietato
È vietata la catena **azione → osservazione → metafora → spiegazione della metafora → conclusione filosofica**. Il paragrafo si ferma prima: all'azione e a ciò che si vede, al massimo con un'immagine. Il lettore deve arrivare da solo al senso. Una metafora non si spiega mai nella frase successiva; una conclusione generale non chiude mai un paragrafo di scena.

---

## 5. Lingua e dialetto

### 5.1 Principio
Il dialetto **affiora**: sta in poche parole, in qualche costruzione, nella sintassi del parlato. Non si trascrivono foneticamente frasi intere. Niente accenti grafici decorativi: vietate forme come «Siéditi», «Avvicìnati», «Giùramelo».

### 5.2 Lessico ammesso (da verificare con un parlante barese prima della stesura [PROPOSTA])

**Baresi:**

| Voce | Significato |
|---|---|
| «uè» | richiamo |
| «uagnò» | vocativo, ragazzo |
| «uagnone» | ragazzo |
| «mo'» | adesso |
| «citte!» | zitto |
| «u'», «'u» | articolo nei soprannomi: «Pasquale 'u pesce spada» |
| «sgagliozze» | polenta fritta |
| «chianche» | lastre di pietra delle strade e dei pavimenti |
| «basso» | abitazione a livello della strada |
| «crudo», «ricci», «cozze tarantine», «orecchiette», «brodetto» | cibo |
| «Madonna!» | esclamazione |

- Costruzioni di parlato regionale in bocca ai personaggi, con misura: «tenere» per «avere» («tengo fame»), il tu ai vecchi, il voi alla madre di un amico.

**Napoletani** (solo don Tobia e Ciro): «guagliò», «piccerì», «guaglione».

**Calabresi** (solo zi' Nardu, Saro, gli uomini della montagna): «cumpà», «figghiolu», il «mi» del verbo al posto dell'infinito, con misura.

### 5.3 Vietato
- «guaglio'», «guagliò» e «guaglione» in bocca a un barese;
- le trascrizioni fonetiche di più di cinque parole di seguito;
- il dialetto nel racconto del narratore, fuori dal discorso diretto: il vecchio scrive in italiano;
- «Beniamì» più di 3 volte nel libro (è della madre);
- l'inglese oltre «Mister».

### 5.4 Dialogo
- Il dialogo si apre con la **lineetta lunga** («—»), con uno spazio dopo.
- Il verbo dichiarativo standard è «disse»; gli altri si usano solo quando dicono qualcosa di più.
- **Niente avverbi di modo sui dichiarativi** («disse piano» al massimo 1 volta per capitolo).
- **I personaggi parlano diversi:**
  - Nicola: cortese, frasi complete, ironia;
  - Checco: corto, dialettale;
  - Michele: lento, immagini di mestiere;
  - la madre: imperativi;
  - Franco: allegro, a mitraglia;
  - Cataldo: domande secche.

---

## 6. Sensibilità

- **Persone reali:** nessuna persona reale, nessun clan e nessun boss reale. Le istituzioni reali sono ammesse per nome: Carabinieri, Guardia di Finanza, Polizia, Questura, carcere di Trani, Policlinico, Gazzetta del Mezzogiorno. Nessuna carica pubblica identificabile in una scena di collusione: né «il sindaco» né «il questore» (bibbia, decisione 10.12).
- **Droga:** nessun dettaglio procedurale. Vietati:
  - i nomi di sostanze da taglio;
  - le dosi;
  - la preparazione;
  - gli strumenti in primo piano (cucchiaio, fiamma, laccio).
- **Parole ammesse sulla droga:** «la roba»; «l'ago», al massimo 3 volte nel libro; «bucarsi», al massimo 3.
- **Effetti e astinenza:** si raccontano come esperienza del corpo (freddo, sbadigli, nausea, gambe, sonno che non viene), mai come istruzioni.
- **Il prova-merce:** il gesto di Beniamino si racconta con quello che sente e con il giudizio che dà, mai con il come.
- **Minore:** Beniamino ha tredici anni. **Nessun contenuto sessuale.** Alla villa le donne sono presenze del potere, descritte senza sguardo sessualizzato.
- **Violenza:**
  - fuori campo o sonora, come per Franco;
  - quando è in campo (lo schiaffo, il collare, il fuoco), resta breve e porta a una conseguenza;
  - niente dettagli anatomici insistiti, niente compiacimento;
  - il dopo (i corpi, le facce, gli oggetti) conta più del durante.

---

## 7. Verosimiglianza 1976

- **Oggetti e cose del tempo:** il Ciao, l'Alfa GT Junior, i motocarri, i gettoni telefonici, le cabine, la Peroni, la Gazzetta del Mezzogiorno, le lire (banconote da 100.000 e da 10.000), il Totocalcio, i transistor, i mangiadischi, i giradischi nei bar.
- **Niente anacronismi:** niente walkman, niente telefoni senza filo, niente «porto container». Prima di usare un oggetto si controlla che esistesse nel 1976.
- **Prezzi di riferimento, indicativi, da verificare:** Vespa circa 500.000 lire; stipendio operaio circa 200-250.000 lire al mese; biglietto nave di terza classe per il Sud America circa 500-600.000 lire a persona.
- **Le cifre dello zaino** seguono la tabella della bibbia (5.7).
- **Le date** seguono la cronologia della bibbia (sezione 3). I giorni della settimana sono verificati.

---

## 8. Checklist per ogni capitolo, prima della consegna

1. Il capitolo rispetta la scaletta: eventi, data, filone, lunghezza (±15%)?
2. Il controllo anti-riciclo (7 parole) è pulito?
3. Frase media tra 10 e 13? Dialogo tra 15 e 35%?
4. C'è almeno una scena in tempo reale di 800 o più parole?
5. Intrusioni del vecchio: da 1 a 3 (zero nel cap. 10), ognuna con la sua àncora temporale? Aforismi del vecchio entro uno ogni due capitoli? Nessun aforisma prestato al ragazzo?
6. Le formule contate (3.5) e le immagini vietate (4.3) sono sotto soglia? Il registro qui sotto è aggiornato?
7. Similitudini: al massimo 1 per pagina, concrete, nei campi ammessi?
8. La chiusura è di un tipo ammesso? Il conto delle sentenze è sotto 8?
9. Il dialetto è corretto per il parlante (barese, napoletano, calabrese)?
10. Continuità: nomi, età, oggetti, luoghi e cifre coincidono con la bibbia?
11. Sensibilità: niente procedura, niente persone reali, violenza con misura?
12. I motivi usati sono sotto il tetto della bibbia (sezione 7) e il conto è aggiornato?
13. Gesti di conteggio: al massimo 3 (3.6)?
14. Nessun paragrafo segue lo schema vietato del 4.6 (metafora spiegata, conclusione filosofica)?
15. Parole contate con il metodo unico (sezione 1)?
16. Il nome «Lucia» è assente se il capitolo viene prima del cap. 37 (prologo e interludi I-VI compresi)? Presente, dal cap. 37 in poi, al posto di «lei»? (2.5)

---

## 9. Registro dei contatori (da aggiornare capitolo per capitolo)

| Cap. | Parole (metodo unico) | Frase media | Dialogo % | «Non era X. Era Y.» (cumulato, su 5) | Chiusura sentenziosa (cumulato, su 8) | Intrusioni | Gesti di conteggio (su 3) | Note sui motivi |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | 0 | 0 | — | — | — |

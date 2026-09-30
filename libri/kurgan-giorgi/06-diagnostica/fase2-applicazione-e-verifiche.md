# Fase 2 — applicazione parziale e verifiche — «Il padre del mostro»

- **Punto di ripristino:** commit `cf6d1bb`. Stato di partenza di questa fase: `3899e64`.
- **Riferimento:** i numeri di riga sono quelli del manoscritto dopo il commit delle modifiche del blocco A (le sostituzioni sono tutte dentro una riga: la numerazione non cambia).

## A. Applicato

Ogni sostituzione è stata fatta con un controllo automatico: il testo «prima» doveva comparire una sola volta nel capitolo, alla riga indicata (±1).

- **Cap. 51, r. 21** (apertura)
  - Prima: «Nella fisica sperimentale c'è una regola che i fisici imparano presto e rispettano male:»
  - Dopo: «L'uomo con il loden verde e il berretto di lana era rimasto sul pontile a guardare la barca, e Giorgi conosceva la regola che la fisica sperimentale impone a chiunque guardi:»
  - Verificato: r. 9 (loden verde, berretto di lana), r. 11 («Io vi raggiungo con l'altra barca»), r. 25 (la barca si stacca dal pontile)
  - Parole: +17
- **Cap. 5, r. 161** (numeri)
  - Prima: «Sei mesi tra la prima riga e la seconda.»
  - Dopo: «Quattro mesi e mezzo tra la prima riga e la seconda.»
  - Verificato: rr. 153–155 (maggio, notte dei droni; giovedì 2 ottobre, Valcerna); cap. 11 (17 maggio)
  - Parole: +2
- **Cap. 35, r. 163** (chiusura)
  - Prima: «Non c'era nessuno. Non gli servì a niente saperlo.»
  - Dopo: «Non c'era nessuno. Attraversò.»
  - Verificato: r. 161 («prima di attraversare la strada guardò a destra, poi a sinistra»)
  - Parole: -5
- **Cap. 7, r. 177** (tic Kurgan)
  - Prima: «Guardò la folla. Fece il conto un'altra volta, da capo.»
  - Dopo: «Guardò la folla. Riascoltò la voce di Rastegar, da capo.»
  - Verificato: rr. 153–169 (Rastegar parla al tavolino e se ne va dalle scale di servizio, r. 171)
  - Parole: +0
- **Cap. 13, r. 55** (tic Kurgan)
  - Prima: «Fece il conto come l'aveva fatto sul muretto, nella valle.»
  - Dopo: «Guardò fuori, verso il buio delle saline, come aveva guardato la valle dal muretto.»
  - Verificato: r. 41 (finestra «sul buio delle saline»); cap. 3 (il muretto nel Drenak)
  - Parole: +4
- **Cap. 18, r. 129** (tic Kurgan)
  - Prima: «Kurgan fece il conto, lì, in piedi, come l'aveva fatto sul muretto nella valle.»
  - Dopo: «Kurgan restò in piedi, con la schiena alla porta scorrevole, e li guardò in faccia.»
  - Verificato: r. 105 («Kurgan in piedi, con la schiena alla porta scorrevole»); il richiamo al muretto resta al cap. 13
  - Parole: +1
- **Cap. 24, r. 31** (tic Kurgan)
  - Prima: «Kurgan fece il conto e il conto gli diede una spiegazione sola.»
  - Dopo: «Kurgan rilesse a memoria le due parole del secondo biglietto, *questa settimana*, e ci trovò una spiegazione sola.»
  - Verificato: r. 27 (il secondo biglietto: «due parole soltanto: *questa settimana*»)
  - Parole: +6
- **Cap. 9, r. 189** (tic Flora)
  - Prima: «Rimise in fila. Non riusciva a smettere.»
  - Dopo: «Il freddo dalla nuca le era sceso lungo la schiena, e non se ne andava.»
  - Verificato: r. 185 («Flora sentì il freddo partire dalla nuca»)
  - Parole: +8
- **Cap. 27, r. 9** (tic Flora)
  - Prima: «Prima mise in fila le cose. Lo faceva sempre.»
  - Dopo: «Prima guardò la calligrafia storta del biglietto giallo.»
  - Verificato: r. 5 (il biglietto giallo «con la sua calligrafia storta»)
  - Parole: -1
- **Cap. 31, r. 143** (tic Flora)
  - Prima: «Fece il conto, come lo faceva sempre.»
  - Dopo: «Sentì il foglio piegato contro il fianco.»
  - Verificato: r. 139 (il settimo foglio nella borsa, piegato in quattro, «lo sentiva contro il fianco»)
  - Parole: +0
- **Cap. 50, r. 45** (tic Flora)
  - Prima: «Il notaio restò in silenzio per un tempo che Flora contò. Nove secondi. Poi tirò fuori»
  - Dopo: «Il notaio restò in silenzio, e Flora gli vide la mano andare alla tasca del maglione e fermarsi lì. Poi tirò fuori»
  - Verificato: stessa riga («tirò fuori un mazzo dalla tasca del maglione»)
  - Parole: +6
- **Cap. 11, r. 63** (tic Dalia)
  - Prima: «Dalia ne contò undici. Poi vide che in fondo, contro il muro, c'erano altre casse ancora chiuse, e smise di contare.»
  - Dopo: «Undici, sui tavoli. Dalia sentì il freddo della stanza sulle braccia, e vide che in fondo, contro il muro, c'erano altre casse ancora chiuse.»
  - Verificato: r. 59 («Faceva freddo»); il numero resta perché r. 151 lo richiama («Undici aerei»)
  - Parole: +3
- **Cap. 16, r. 215** (tic Dalia)
  - Prima: «Dalia contò i secondi. Sette. Non capiva. Sapeva soltanto che in quei sette secondi Alfredo»
  - Dopo: «Dalia guardò la mano ferma sulla stoffa. Non capiva. Sapeva soltanto che, chino in quel modo, Alfredo»
  - Verificato: r. 213 («restò chino un momento di più, con la mano sulla stoffa»); risolve il conflitto con cap. 6, r. 177 («Non i secondi, non era il suo modo»); nessun richiamo ai «sette secondi»
  - Parole: +2
- **Cap. 19, r. 79** (tic Elena)
  - Prima: «Lei si lasciò baciare. Contò i secondi: meno di uno.»
  - Dopo: «Lei si lasciò baciare. Sentì il freddo dei capelli bagnati contro la fronte.»
  - Verificato: stessa riga («scese in cucina con i capelli bagnati. Baciò Elena sulla tempia»)
  - Parole: +3
- **Cap. 22, r. 51** (tic Elena)
  - Prima: «Elena aspettò. Contò i secondi, come aveva contato i respiri di lui la domenica di giugno in cui aveva letto l'altro telefono. Venti. Quaranta. La doccia scorreva. Al cinquantaduesimo secondo lo schermo»
  - Dopo: «Elena aspettò. Sentì il parquet sotto i piedi nudi. La doccia scorreva. Poi lo schermo»
  - Verificato: r. 49 («fece due passi a piedi nudi sul parquet»), r. 47 (la doccia)
  - Parole: -17
- **Cap. 28, r. 90** (tic Elena)
  - Prima: «Elena aspettò il rumore. Lo contò tre volte.»
  - Dopo: «Elena aspettò il rumore. Lo sentì arrivare, piccolo, in fondo alla gola di lui.»
  - Verificato: stessa riga («faceva un piccolo rumore in fondo alla gola»); il conteggio dei respiri resta alle rr. 88 e 92
  - Parole: +6
- **Cap. 40, r. 83** (tic Elena)
  - Prima: «Elena contò fino a tre prima di rispondere. Era il suo numero.»
  - Dopo: «Elena sentì la parola *papà* restare tra loro, prima di rispondere.»
  - Verificato: r. 79 («Il cordino nero. Era di papà.»); la formula «contò fino a tre» resta solo al cap. 32
  - Parole: -1
- **Cap. 47, r. 133** (tic Elena)
  - Prima: «che Elena contò come si contava una cosa comparsa in un inventario dove prima non c'era»
  - Dopo: «che Elena vide come si vedeva una cosa comparsa in un inventario dove prima non c'era»
  - Verificato: stessa riga (la ruga tra le sopracciglia)
  - Parole: +0
- **Cap. 35, r. 127** (tic Carlo)
  - Prima: «Contò, dentro di sé, fino a tre, perché sapeva»
  - Dopo: «Sentì il proprio respiro, lento, e lo lasciò durare, perché sapeva»
  - Verificato: stessa riga (lo sguardo fermo sul capo reparto)
  - Parole: +2

**Saldo del blocco A: +36 parole** (manoscritto: 111.428 → 111.464).

Differenze rispetto alla proposta di fase 1, per rispettare «sostituire il conteggio con un'altra percezione, senza cancellare la riga»:
- Nessuna frase è stata eliminata: le quattro frasi che in fase 1 erano «da eliminare» (cap. 7 r. 177, cap. 9 r. 189, cap. 19 r. 79, cap. 28 r. 90) sono state sostituite con una percezione.
- Cap. 11, r. 63: il numero «undici» resta, perché la r. 151 dello stesso capitolo lo richiama («Undici aerei»). Cambia solo l'atto: non è più Dalia a contare.
- Cap. 13, r. 55 e cap. 18, r. 129: il richiamo al muretto del Drenak resta una volta sola (cap. 13), come proposto in fase 1.
## B. Non applicato, per decisione dell'autore

- Cap. 2, r. 29, «cambiare stato»: resta. I quattro «cambiato stato» (2:29, 2:157, 21:123, 21:131) sono una catena voluta.
- Fusione del ragazzo della Serrana (cap. 18) con il ragazzo della pergola (cap. 16): non fatta.
- Chiusure dei capp. 2, 8, 17, 21, 38: invariate.

## C. Proposte in attesa di conferma (nessuna applicata)

### C1. Cap. 34, chiusura

Il «codice sbiadito» è già in scena alla **r. 149**: «Guardò il palmo della mano sinistra. Il codice di sedici caratteri si era sbiadito, ma si leggeva ancora.» L'ascensore è alla r. 151.

**Prima (rr. 149–155):**

> Guardò il palmo della mano sinistra. Il codice di sedici caratteri si era sbiadito, ma si leggeva ancora.
>
> Spense il computer. Si alzò. Contò i passi fino all'ascensore, come ogni sera.
>
> Trentuno.
>
> Non gli erano mai sembrati così tanti.

**Dopo:**

> Guardò il palmo della mano sinistra. Il codice di sedici caratteri si era sbiadito, ma si leggeva ancora.
>
> Spense il computer. Si alzò. Contò i passi fino all'ascensore, come ogni sera.
>
> Trentuno.
>
> Chiuse la mano sinistra sul codice sbiadito e aspettò l'ascensore.

- Il «Trentuno» resta: è il motivo dei passi di Tommaso (capp. 4, 34, 48).
- Parole: +3.

### C2. Cap. 15, r. 57: i trentuno conti e i quarantasei soggetti

**Prima (riga intera):**

> Sulla lavagna c'era ancora la colonna del gennaio precedente: quarantasei soggetti, una banca di Valdhof, il 29 settembre, il 12 novembre. Sotto, in blu, le cose nuove di sedici mesi. Poche. I dati della Consob erano arrivati in autunno e i conti delle 12.07 si erano persi, uno per uno, dentro altrettante fiduciarie di Valdhof. La seconda rogatoria era tornata con metà delle pagine annerite.

**Dopo:**

> Sulla lavagna c'era ancora la colonna del gennaio precedente: quarantasei soggetti, una banca di Valdhof, il 29 settembre, il 12 novembre. Sotto, in blu, le cose nuove di sedici mesi. Poche. I dati della Consob erano arrivati in autunno, e dei quarantasei ne avevano staccati trentuno, quelli delle 12.07: si erano persi, uno per uno, dentro altrettante fiduciarie di Valdhof. La seconda rogatoria era tornata con metà delle pagine annerite.

- Verificato:
  - cap. 9, r. 11: i quarantasei chiudono tra le 11.51 e le 12.30, una finestra che contiene le 12.07.
  - cap. 20, r. 41: trentuno fiduciarie a Valdhof.
  - Nessun passaggio del libro dice che i trentuno sono esterni ai quarantasei.
- Parole: +8.
- Rispetto alla fase 1 («i trentuno conti delle 12.07, trentuno dei quarantasei») cambia la sintassi: la ripetizione di «trentuno» a due parole di distanza suonava come un errore.

### C3. Voci: tutti gli interventi, prima e dopo

La richiesta dice «sette», ma la fase 1 ne proponeva **dieci**: due per ciascuno dei cinque blocchi (Tommaso cap. 1, Kurgan cap. 3, Flora cap. 5, Kurgan cap. 7, Giorgi cap. 2). Li riporto tutti. Due sono corretti rispetto alla fase 1: Giorgi cap. 2 r. 9, per non reintrodurre il tic del contare, e Flora cap. 5 r. 191, dove gli scatoloni non sono in scena.

1. **Tommaso, cap. 1, r. 197**
   - Prima: «Cancellato non voleva dire sparito. Lo sapeva anche un bambino.»
   - Dopo: «Cancellato non voleva dire sparito. Voleva dire spostato in un'altra colonna.»
   - Verificato: nessun oggetto nuovo; è una voce da contabile.
   - Parole: +1.
2. **Tommaso, cap. 1, r. 205**
   - Prima: «Non si fidò di niente per il resto del pomeriggio.»
   - Dopo: «Per il resto del pomeriggio non si fidò di niente che non potesse contare.»
   - Verificato: nessun oggetto nuovo. Il tic di Tommaso non è stato ridotto (resta, per scelta).
   - Parole: +4.
3. **Kurgan, cap. 3, r. 11** (solo la prima frase della riga)
   - Prima: «Gli uomini si erano disposti come si disponevano sempre, senza che nessuno glielo avesse mai insegnato.»
   - Dopo: «Gli uomini si erano disposti come si disponevano le squadre nel Drenak, senza che nessuno glielo avesse mai insegnato.»
   - Verificato: cap. 3, r. 71 (il Drenak, più avanti nello stesso capitolo).
   - Parole: +3.
4. **Kurgan, cap. 3, r. 17**
   - Prima: «Kurgan si sedette a capotavola. Non disse niente per un po'. Lasciò che il silenzio facesse il suo lavoro, che era quello di far capire a ciascuno che stava per succedere qualcosa che non si sarebbe potuto disfare.»
   - Dopo: «Kurgan si sedette a capotavola. Non disse niente per un po'. Lasciò che il silenzio facesse il suo lavoro. Il generatore, nell'angolo, ronzava per tutti.»
   - Verificato: cap. 3, r. 9 («un generatore che ronzava in un angolo»).
   - Parole: −13.
5. **Flora, cap. 5, r. 47**
   - Prima: «Non era una domanda. Flora lo prese come tale lo stesso.»
   - Dopo: «Non era una domanda. Flora la mise agli atti come tale lo stesso.»
   - Verificato: nessun oggetto nuovo; è una voce da magistrato.
   - Parole: +2.
6. **Flora, cap. 5, r. 191** (corretta rispetto alla fase 1)
   - Prima: «Il treno era mezzo vuoto. Fuori era già buio. Nel vetro vedeva la sua faccia sovrapposta ai campi neri, e sotto la faccia la stanchezza, che ormai non se ne andava più nemmeno con il sonno.»
   - Dopo: «Il treno era mezzo vuoto. Fuori era già buio. Nel vetro vedeva la sua faccia sovrapposta ai campi neri, e la guardò come avrebbe guardato un testimone: sotto la faccia, la stanchezza, che ormai non se ne andava più nemmeno con il sonno.»
   - Verificato: rr. 189–191 (in treno, al ritorno; il vetro). Nessun oggetto nuovo; è una voce da magistrato.
   - Perché è corretta: la versione di fase 1 citava gli scatoloni, ma questi restano nell'ufficio del pool (rr. 39, 149) e non sono sul treno. Era anche un elenco, cioè il «mettere in fila» appena ridotto.
   - Parole: +7.
7. **Kurgan, cap. 7, r. 13**
   - Prima: «Era quello il punto. Chiunque avesse scelto quel posto conosceva il mestiere.»
   - Dopo: «Chi aveva scelto quel posto voleva la stessa cosa che voleva lui: essere guardato per un secondo, e poi via.»
   - Verificato: cap. 7, r. 11 («Per un secondo, e poi via»).
   - Parole: +8.
8. **Kurgan, cap. 7, r. 207**
   - Prima: «Adorisio annuì, chiuse il libro, accese il motore. Non chiese altro. Era una delle cose per cui Kurgan lo teneva vicino da quindici anni: sapeva quando smettere di chiedere.»
   - Dopo: «Adorisio annuì, chiuse il libro, accese il motore. Non chiese altro. Adorisio sapeva quando smettere di chiedere. Per questo era ancora lì.»
   - Verificato: stessa riga. Toglie anche una delle due occorrenze di «quindici anni» di Adorisio negli anni Y (vedi C4).
   - Parole: −7.
9. **Giorgi, cap. 2, r. 9** (corretta rispetto alla fase 1)
   - Prima: «Aspettò, dunque. Era il suo talento principale, anche se nessuno, nemmeno quelli che lo pagavano, lo avrebbe descritto così.»
   - Dopo: «Aspettò, dunque. Aspettare era la parte del lavoro che nessuno, nemmeno quelli che lo pagavano, gli aveva mai visto fare.»
   - Verificato: nessun oggetto nuovo.
   - Motivo della correzione: la versione di fase 1 («ne misurò l'intervallo per avere un numero da tenere») aggiungeva un conteggio e anticipava i fari rossi della r. 11, che li introduce da capo.
   - Parole: 0.
10. **Giorgi, cap. 2, r. 75** (solo l'ultima frase)
    - Prima: «Non vi trovò nulla da correggere.»
    - Dopo: «Registrò che non c'era nulla da correggere.»
    - Verificato: stessa riga (il riflesso nel vetro). La r. 11 dello stesso capitolo usa già «registrava questa conformità»: è il verbo di Giorgi.
    - Parole: +1.

Saldo delle voci: +6 parole.

### C4. Età e durate

**Calendario usato.**
- Capitoli 1–10: anno Y (novembre Y – febbraio Y+1).
- Capitolo 11: maggio Y+1.
- Capitoli 12–47: anno Y+2.
- Capitoli 48–53: gennaio–febbraio Y+3.

**Le due direzioni.**
- **Direzione A:** si correggono i capitoli 1–11, cioè si portano indietro.
- **Direzione B:** si correggono i capitoli 12 e seguenti, cioè si portano avanti.

«Invariate» indica le occorrenze che restano come sono in quella direzione.

#### C4a–b. Occorrenze e conteggio

**1. Matrimonio Giorgi–Elena: «diciassette anni»**
- Anni Y: cap. 2, r. 21 («diciassette anni prima, l'aveva scelta»). 1 occorrenza.
- Anni Y+2 e Y+3:
  - cap. 17, r. 159
  - cap. 22, r. 39
  - cap. 28, rr. 67 e 146
  - cap. 32, r. 100
  - cap. 40, rr. 43 e 59
  - cap. 46, r. 127
  - cap. 47, rr. 5, 141 e 145
  - cap. 53, r. 92
  - Totale: 13 occorrenze.
- Escluse: cap. 41, r. 79 («a diciassette anni» è un'età, non una durata).
- **A:** cap. 2, r. 21, «diciassette» → «quindici». Invariate le 13 dei capitoli 17–53. **1 punto.**
- **B:** le 13 occorrenze diventano «diciannove». **13 punti.**
- Controllo incrociato: il cap. 47, r. 141 («Diciassette anni. Quindici di ville…») e Fabrizio a quindici anni (capp. 19, 40) sono coerenti con A.

**2. Giorgi–Dalia: «sei anni»** (relazione iniziata con il primo messaggio di ottobre; la macchina di Vito sotto la redazione, a marzo, viene prima)
- Anno Y, cap. 6: rr. 7, 23, 33, 75, 105, 113, 135, 141, 165. 9 occorrenze.
- Anno Y+1: cap. 11, r. 139. 1 occorrenza.
- Anni Y+2 e Y+3:
  - cap. 12, r. 99
  - cap. 13, r. 65
  - cap. 16, rr. 7, 39 e 55
  - cap. 19, r. 39 (tre occorrenze nella stessa riga) e r. 63
  - cap. 23, rr. 5, 73, 103, 125 e 131
  - cap. 30, r. 79
  - cap. 41, rr. 69, 77 e 91
  - cap. 47, r. 105
  - Totale: 17 righe.
- Escluse:
  - cap. 3, r. 145 («ventisei»)
  - cap. 15, r. 109 e cap. 26, r. 69 (età)
  - cap. 27, r. 72 (Tarassa, altro fatto)
  - cap. 31, r. 63 (l'ammiraglio)
  - cap. 43, r. 91 (Nicola)
- **A:** in cap. 6, otto occorrenze «sei anni» → «quattro anni». Poi:
  - cap. 6, r. 105: «Sei anni prima, una sera di marzo» → «Quasi cinque anni prima, una sera di marzo». Correzione rispetto alla fase 1, che diceva «quasi quattro»: marzo Y−4, visto da novembre Y, è a 4 anni e 8 mesi.
  - cap. 11, r. 139: «da sei anni» → «da quasi cinque anni».
  - Invariate le 17 righe dei capitoli 12–47 e le schede (Dalia rr. 49–54, Vito rr. 47 e 63, Elena r. 60), che contano dal presente di Y+2.
  - **10 punti.**
- **B:** le 17 righe diventano «otto anni». In più, cap. 6, r. 105 diventa «Quasi sette anni prima» (marzo, prima di ottobre). Da aggiornare anche 6 righe di schede. **18 punti** nel manoscritto.

**3. Carlo e Flora: «due anni» / «tre anni»** (da quanto si conoscono e cenano)
- Anni Y e Y+1: cap. 5, r. 193 («conosceva da due anni»); cap. 9, r. 55 («la prima sera, due anni prima») e r. 65 («Due anni di cene»). 3 occorrenze. La r. 65 del cap. 9 mancava nella fase 1.
- Anno Y+2, «tre anni»:
  - cap. 20, rr. 87, 127, 135 e 149
  - cap. 31, r. 133
  - cap. 39, r. 116
  - Totale: 6 occorrenze.
- Anno Y+2, «due anni»:
  - cap. 31, r. 141
  - cap. 35, rr. 69 e 71
  - cap. 44, rr. 9 e 96
  - Totale: 5 occorrenze.
- **Anche dentro l'anno Y+2 le due cifre si contraddicono:** il cap. 31 dice «la quarta volta in tre anni» (r. 133) e, otto righe dopo, «Due anni di cene» (r. 141).
- Non riguardano la conoscenza, e restano in tutte e due le direzioni:
  - cap. 35, rr. 41, 59 e 79: l'incarico di Carlo e l'ascolto delle linee del pool, «da due anni», cioè dalla nascita del pool (giorno 0). **Correzione rispetto alla fase 1**, che proponeva di cambiare le rr. 41 e 59: sono giuste così.
  - cap. 20, r. 157 («i primi tre anni»): modo di dire della madre.
  - cap. 20, r. 165 e cap. 35, rr. 21, 31, 39 e 141: la domanda di comando di tre anni prima, un fatto datato e non una durata della conoscenza.
- **A** (si conoscono da Y−1):
  - cap. 5, r. 193, e cap. 9, rr. 55 e 65: «due anni» → «un anno».
  - cap. 31, r. 141, cap. 35, rr. 69 e 71, cap. 44, rr. 9 e 96: «due anni» → «tre anni».
  - Invariate le 6 occorrenze con «tre anni».
  - **8 punti.**
- **B** (si conoscono da Y−2, cap. 5 invariato): tutte le 11 occorrenze dell'anno Y+2 diventano «quattro anni». **11 punti.**

**4. Adorisio con Kurgan: «quindici anni»**
- Anno Y: cap. 3, r. 53; cap. 7, r. 207.
- Anno Y+2: cap. 13, r. 89; cap. 17, r. 121; scheda dei comprimari, r. 27 («con Kurgan da quindici anni», riferita al cap. 13).
- **A:** «quindici» → «tredici» nel cap. 3, r. 53, e nel cap. 7, r. 207. **2 punti**, oppure **1** se si applica la voce C3.8, che toglie la cifra dal cap. 7.
- **B:** «quindici» → «diciassette» nei capp. 13 e 17. **2 punti**, più la scheda.

**5. Tanino**
- Anno Y: cap. 3, r. 145 («ventisei anni»).
- Anno Y+2: cap. 13, r. 175 e cap. 29, r. 7 («ventisette»); scheda di Kurgan, r. 73 (27 anni).
- **A:** «ventisei» → «venticinque». **1 punto.**
- **B:** «ventisette» → «ventotto» nei capp. 13 e 29. **2 punti**, più la scheda.

**6. Kurgan–Giorgi: «dieci anni»** (NUOVO: nella fase 1 l'avevo segnato come coerente, ed era un errore)
- Anni Y e Y+1:
  - cap. 2, rr. 7, 33, 49, 121 e 133 (due volte)
  - cap. 3, rr. 195 e 197 (l'orologio)
  - cap. 8, rr. 35 e 55
  - cap. 11, r. 41 (l'orologio)
  - Totale: 11 occorrenze in 10 righe.
- Anno Y+2:
  - cap. 12, rr. 19 e 71
  - cap. 13, rr. 47 e 65
  - cap. 17, r. 161
  - cap. 18, r. 7 (l'orologio)
  - cap. 21, r. 77
  - Totale: 7 righe.
- Escluse, perché sono un altro fatto:
  - cap. 17, r. 7 (la sala sicura)
  - cap. 18, r. 31
  - capp. 36, 37, 38, 41, 42 e 48 (conservazione legale, battute)
- Legato: cap. 8, r. 39 (Kurgan «aveva trentotto anni» al primo incontro).
- **A** (primo incontro in Y−8): le 11 occorrenze degli anni Y diventano «otto anni» e il cap. 8, r. 35 diventa «Otto anni prima». Il **cap. 8, r. 39 resta «trentotto»**: nato nel 1979 (vent'anni nell'inverno del novantanove), ha 38 anni in Y−8. Le schede restano coerenti (Kurgan 48 anni in Y+2 = 38 + 10; Giorgi r. 56). **11 punti.** Tocca cinque volte il cap. 2, dove «dieci anni» fa da ritornello.
- **B** (primo incontro in Y−10): le 7 righe degli anni Y+2 diventano «dodici anni». Il cap. 8, r. 39 diventa «trentasette». Da aggiornare le schede (Giorgi rr. 55 e 56; il «38» della r. 56). **8 punti** nel manoscritto. Il cap. 2 resta intatto.
- Nota: la correzione «trentotto → trentasette» della fase 1 vale **solo** in direzione B.

**Conteggio finale**

| Durata | A (capp. 1–11 indietro) | B (capp. 12+ avanti) | Più leggera |
|---|---|---|---|
| Matrimonio Giorgi–Elena | 1 | 13 | A |
| Giorgi–Dalia | 10 | 18 | A |
| Carlo–Flora | 8 | 11 | A |
| Adorisio | 2 (1 con C3.8) | 2 | A (le schede restano) |
| Tanino | 1 | 2 | A |
| Kurgan–Giorgi | 11 | 8 | **B** |
| **Totale** | **33** | **54** | |

- **Proposta:** A per tutte le durate tranne Kurgan–Giorgi, dove B è più leggera e lascia intatto il ritornello del cap. 2. Totale: **30 punti** (29 con C3.8).
- La coerenza è la stessa: ogni durata è indipendente dalle altre. L'unico legame incrociato, l'età di Kurgan al cap. 8, r. 39, è già dentro il conto di B.

#### C4c. Cap. 46, r. 53: «Il 2005.»

**Prima:**

> Avrebbe potuto dirglielo. Una macchina sotto la redazione, un uomo altissimo seduto dietro, una busta, l'affitto di sua madre. Avrebbe dovuto dirgli anche il resto, allora. Il 2005. Le stanze. I vent'anni. Il corpo come una cosa che rendeva. Non c'era una versione della risposta vera che non cominciasse da lì. E una volta cominciata da lì, non sarebbe più stata la storia di una fonte falsa. Sarebbe stata la sua.

**Dopo:**

> Avrebbe potuto dirglielo. Una macchina sotto la redazione, un uomo altissimo seduto dietro, una busta, l'affitto di sua madre. Avrebbe dovuto dirgli anche il resto, allora. I quindici anni. Le stanze. I vent'anni. Il corpo come una cosa che rendeva. Non c'era una versione della risposta vera che non cominciasse da lì. E una volta cominciata da lì, non sarebbe più stata la storia di una fonte falsa. Sarebbe stata la sua.

**Dove compare l'anno.**
- **Nel manoscritto:** «2005» compare **solo** qui. Nessun altro anno a quattro cifre è scritto nel libro. Il cap. 9, r. 9, «duemila pagine», non è un anno.
- **Unico altro anno nominato:** cap. 3, r. 71, «nell'inverno del novantanove» (Kurgan nel Drenak).
- **Nei materiali di lavoro, non stampati:**
  - `00-progetto/stato.md`, r. 21 («sfruttata dal 2005»)
  - `02-bibbia/trama.md`, r. 44
  - scheda di Dalia, r. 13 («Dal 2005 circa»)
  - scheda di Vito Kurgan, r. 15 («dal 2005 circa (lui 27 anni…)»)
  - Sono note di bibbia: non vanno cambiate.

**Tiene con le età?**
- Sì. Dalia ha 35 anni nell'anno Y (cap. 6, r. 161). Il 2005 cade quando ne ha quindici solo se Y = 2025. Il cap. 16, r. 141 conferma: «Aveva imparato a sostenere gli sguardi a quindici anni, in una stanza con le persiane chiuse».
- Quindi la riga non è sbagliata, ma **data il romanzo**: dice al lettore che il giorno 0 è nel 2025.
- «I quindici anni» dice la stessa cosa senza l'anno e crea il parallelo con «I vent'anni» della stessa riga.

**Limite.**
- Anche togliendo il 2005, il romanzo resta databile per chi fa i conti: «novantanove» (cap. 3) + Kurgan che aveva vent'anni allora + i suoi 48 anni nella scheda (non nel testo).
- Nel testo stampato, però, l'età di Kurgan nel presente non compare. Senza il 2005 la datazione diventa molto più difficile.
- Parole: +1.

#### C4d.

Il messaggio si interrompe a «d) Este…». Il punto d) non è stato eseguito: aspetto il testo completo.

## Stato

- Manoscritto modificato solo per il blocco A.
- Blocchi B e C: nessuna modifica. Il blocco C aspetta la conferma, voce per voce.

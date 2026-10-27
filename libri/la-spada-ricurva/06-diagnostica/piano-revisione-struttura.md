<!-- zb: ruolo=editor-strutturale; su=f6f9d7ee126f -->
# Piano di revisione della struttura — La Spada Ricurva

Fonte: `06-diagnostica/rapporto-struttura.md` e `contratto.md`, più tre decisioni dell'autore già registrate nel
briefing (`00-progetto/briefing.md`, righe 18-19, 40 e 45) ma non ancora nella struttura. È una **proposta**: si
applica in `03-struttura/` solo dopo l'ok dell'autore al gate. Fase struttura: non ci sono capitoli scritti, quindi le
stime riguardano le parole delle schede e dei file di struttura da riscrivere, non la prosa.

## Ordine dei lavori e dipendenze

```
A1 presente ───────────────┐
A2 copie borboniche ──► S3 (gancio 31) ──► 39 ──► S7 (44)
        │                                     ▲
        └──► P7 / cap. 4, 17                  │
A3 Claudia rebus / Lorenzo apre ──► S6 (Claudia) ──► S4 (rete/audio, chiavi di Lorenzo)
S1 + S2 (centro e perizia) ──► cap. 1, 22, 25
minori, alla fine
```
Prima le tre decisioni dell'autore (A1-A3): tutto il resto le cita. A2 precede S3, il 39 e il 44 perché sposta
l'oggetto (il registro) su cui poggiano. A3 precede S6 e S4 perché cambia chi ha in mano il rebus e la porta.

---

## Priorità assolute (decisioni dell'autore)

### A1. Tutto il libro al presente — classe: continuità
- **Fonte da correggere:** `09-scelte-fisse.md`, voce «Tempo verbale». Oggi dice: passato (remoto e imperfetto), a
  cose avvenute, presente solo per le riflessioni «da dopo». Va scritto: presente per tutta la narrazione, coerente
  con il briefing (riga 19) e con `00-progetto/voce/indicazioni.md` (riga 4, che già dice presente).
- **Conseguenze da fissare nella stessa voce:** con il presente non c'è più una Elana che racconta da dopo. Vanno tolte
  le riflessioni del tipo «ancora oggi». Il cap. 1 resta un'anticipazione, ma la regge l'intestazione «Luogo — giorno e
  data» (G51), non una voce che ricorda. Lo stesso vale per il 44, che diventa un salto in avanti datato, non uno
  «sguardo retrospettivo».
- **Punti che citano la fonte:** `03-personaggi-chiave.md` r. 7 («a cose avvenute»); `04-atti-svolte.md` r. 4
  («Elana racconta a cose avvenute»); `05-scaletta.md` cap. 1 r. 53 («io narrante a cose avvenute») e cap. 44 r. 655
  («sguardo retrospettivo»); titolo del cap. 44 «Come si ricucì» (passato remoto) in scaletta e in `08-piano-parole.md`;
  `07-tensione-ritmo.md` r. 48 («distanza retrospettiva voluta»).
- **Fuori dal mio recinto, da segnalare:** `06-diagnostica/contratto.md` r. 9 dice «passato, a cose avvenute»; va
  allineato dal diagnosta.
- **Cosa resta:** apertura in medias res, ritorno all'alba nel 45, calendario. Cambia come arriva il salto temporale,
  non dove sta.
- **Stima:** circa 250 parole di struttura.

### A2. Le copie borboniche e i testi in copia unica — scioglie B1 e B2 — classe: continuità + spostare un'informazione
Decisione (briefing r. 45): i Borbone possedevano circa un terzo dei volumi in copie tratte dagli originali; alcuni
dei testi più importanti esistono in copia unica solo nella cripta.
- **Fonte da correggere:** `04-atti-svolte.md`, «Tensione canonica da sciogliere». L'ipotesi del «Breviario» (un
  compendio unico) lascia il posto al canone: un terzo del Fondo è stato copiato prima della sigillatura e quelle copie
  sono passate ai Borbone. La cripta conserva gli originali e i testi in copia unica. Va aggiornata anche la catena
  della ridipintura (1860-61) e del divieto di restauro, che oggi poggia sul Breviario.
- **B1, il registro (cap. 29; ricade su 31, 39, 44, P20):** il registro con il Borbone, le famiglie dell'Accademia e i
  Valli va **spostato fuori dall'archivio sigillato**. Deve stare in un luogo accessibile dopo la sigillatura e legato
  alle copie borboniche (fondo delle copie, carte della loggia dell'Ottocento, archivi dell'Accademia: la scelta spetta
  all'autore). Il 29 cambia luogo e quindi i tag (`@loc:archivio`). Restano la funzione (rivelazione e silenzio di
  Elana), la presenza della sola Claudia, la battuta «niente di utile» e la catena 15→29→32→39. Con il luogo cambia la
  domanda del 31: chi altro ha accesso a quel luogo (vedi S3).
- **B2, il 1861 (cap. 17, P7; preparato nel 4):** nel 17 la conoscenza del 1861 e della guerra occulta **non può
  venire dal corpus della cripta**. Deve venire dalle copie borboniche (annotazioni di corte, glosse aggiunte dopo la
  copiatura) o da una fonte esterna già in scena (Dell'Aquila nel 16 e nel 31). Il 17 tiene dalla cripta solo Venezia,
  i guru, i traduttori e il viaggio a Napoli, e confronta gli originali con quello che le copie lasciano fuori: i testi
  in copia unica. Si tolgono «la sigillatura e il Breviario [ipotesi]» (r. 280) e «chiude P7: il 1861» (r. 282). P7
  passa alla nuova fonte. In `06-sottotrame-temi.md`, r. 12, va aggiornata la riga di chiusura di P7.
- **Ricadute da verificare:** il cap. 16 (Dell'Aquila «cita i Borbone»), ora può pagare in modo naturale con le copie.
  Nel cap. 35 la «perdita degli originali» pesa di più, perché i testi in copia unica esistono ormai solo nella copia
  digitale: va scritto in scaletta. Poi i cap. 39 (la pagina dei Valli) e 44 (P20, il registro mai consegnato), e la
  riga del registro in `03-personaggi-chiave.md` (r. 50).
- **Dipendenza bloccante residua (domanda per l'autore):** la decisione non dice **chi sigillò** l'archivio nel
  Trecento, mentre la loggia nasce nel Settecento dalla fusione con la massoneria napoletana (rapporto, B2). Serve una
  riga di canone: per esempio predecessori di cui la loggia eredita il segreto. Serve anche il **luogo del registro**.
  Senza queste due risposte il 17 e il 29 non si chiudono.
- **Stima:** 600-800 parole di struttura (tensione canonica, schede 4, 16, 17, 29, 31, 35, 39, 44, tabella promesse).

### A3. Claudia decifra il rebus, Lorenzo apre l'archivio — scioglie S5 («tre studenti» contro cinque) — classe: continuità + approfondisci
Decisione (briefing r. 40). Nella lettura più economica i tre studenti sono Claudia, Lorenzo e Mina. Elana è
dottoranda e Pietro viene dalla Federico II.
- **Fonte da correggere:** `01-premessa.md` (r. 4-6) e `02-logline-tema.md` (r. 4). Oggi la logline dice che è la
  dottoranda a decifrare il rebus, e questo contraddice il canone. Il soggetto della scoperta diventa il gruppo, con il
  rebus a Claudia e la porta a Lorenzo. Elana resta protagonista per lo sguardo (il dettaglio sotto la vernice, cap.
  2) e per la scelta del 12. In `03-personaggi-chiave.md`, r. 74, la domanda aperta su «i tre» va chiusa.
- **Cap. 3:** il gruppo si forma con i tre studenti, non con quattro pari. Va dichiarato chi sono «i tre» e dove sta
  Elana rispetto a loro.
- **Cap. 7:** oggi la chiave è «filologica (Elana) e iconografica (Claudia)», e le due si contendono il merito. La
  soluzione va a **Claudia**. Elana dà gli strumenti filologici, ma il passaggio decisivo è di Claudia. Il conflitto di
  merito resta, rovesciato.
- **Cap. 9-10:** **Lorenzo apre** la porta. Oggi nel 9 «vuole tornare indietro»: va deciso nella scheda perché è proprio
  lui ad aprire (la casata, il prezzo, la sua ironia). Va tenuto il sottotesto «se ci scoprono io ho più da perdere».
  Nel 10 restano invariati i ruoli (Elana cataloga, Mina tocca, Lorenzo stima, Claudia vuole richiudere).
- **Cap. 12:** ritocco minimo. Chi ha aperto la porta e chi ha letto la chiave pesa nella trattativa sul piano.
- **Effetti collaterali utili (da usare, non da aggiungere):** la porta aperta da Lorenzo dà un motivo strutturale alle
  sue chiavi nel 39-40 (vedi S4). Il rebus di Claudia è il primo atto in cui una sua scelta cambia la trama (vedi S6),
  ma non basta per il cappio.
- **Stima:** 400-500 parole di struttura (premessa, logline, personaggi, schede 3, 7, 9, 10, 12).

---

## Lavori dal rapporto (dopo A1-A3)

### 4. S1 + S2. Il centro è già speso; la perizia contro la collusione — cap. 1, 22, 25 — classe: drammatizza (preparare una svolta)
- **Cap. 1:** decidere che cosa tace. Il lettore sa della morte e della perizia, ma il cap. 1 non deve dire chi l'ha
  mandata né perché il dato vero c'è.
- **Cap. 22:** togliere l'anticipazione del 25, cioè il fermacarte a due lame sulla scrivania del PM in chiusura. La
  chiusura del 22 va cambiata, non la sua funzione.
- **Cap. 25:** gli serve un'informazione nuova. Il rapporto indica quella già pronta: chi ha fatto arrivare la perizia
  e perché il referto riporta l'ora vera (perito dissidente, errore o segnale: sceglie l'autore). Così si sciolgono
  insieme S1 e S2. La decisione «pubblicare tutto» resta.
- `06-sottotrame-temi.md`: P17 si chiude al 25 solo se il cap. 1 non l'ha già chiusa.
- **Stima:** 250 parole. **Non toccare:** la collocazione del 25 al 55%.

### 5. S3. Il gancio del 31 — cap. 31, 39 o 44 — classe: continuità (pagare la domanda)
Dipende da A2: con il registro in un luogo accessibile, la risposta a «chi l'ha detto a lui?» può venire da chi ha
accesso a quel luogo, o da Claudia, o restare dentro l'ambiguità di Dell'Aquila. In quest'ultimo caso va dichiarata
nel 44 come domanda lasciata aperta di proposito, come nel 42. In scaletta va segnato dove si paga.
**Stima:** 100 parole.

### 6. S6. Claudia non guida — una scena tra 26 e 36 (il rapporto indica 26 o 33) — classe: approfondisci
Dopo A3 Claudia ha la chiave del rebus (atto I), ma nel cappio continua a subire. Serve una sua scelta con
conseguenze **in una scena esistente** (26 o 33), senza aggiungerne. La scelta deve ricadere su un capitolo successivo
(per esempio la «chiave di Claudia» pagata nel 39). Restano invariati il soccorso del 40 e l'uscita del 43.
**Stima:** 150 parole.

### 7. S4. Il modello in rete e sull'impianto audio — cap. 36, 38, 42 — classe: drammatizza (preparare una causa)
Serve una causa dichiarata che superi le «regole ferree, niente rete» di Pietro (13). Il rapporto indica le chiavi di
Lorenzo (39-40), che dopo A3 hanno anche una radice nell'apertura dell'archivio, oppure una necessità tecnica detta
prima del 36. Pietro resta razionale. Il «copiato altrove» del 42 resta aperto, ma deve poggiare su questa causa.
**Stima:** 200 parole.

### 8. S7. Il 44 chiude per riassunto — cap. 30/34, 44 — classe: taglia o comprimi + spostare un'informazione
Dipende da A1 (il 44 non è più retrospettivo), da A2 (P20) e da S3. P12 («che cosa dicono i testi») va anticipata al
30 o al 34, dove è già drammatizzata. Il 44 tiene solo il ricucirsi del sistema e la cartolina, e resta breve (circa
1.800 parole o meno), con le chiusure in scene datate e non in elenco. Il nuovo titolo del capitolo non deve essere al
passato remoto.
**Stima:** 200 parole.

### 9. Minori — classe: continuità
- P10 e P13: unificarle in `06-sottotrame-temi.md` (una sola promessa).
- Dono ai musei (scarto 3): una riga nel 35 o nel 36 che registri la caduta del canale dei musei. È canone, quindi la
  formula va concordata con l'autore.
- Cap. 20: chiarire come Elana legge l'ora sul telefono sequestrato.
- Cap. 27: fissare tra il 13 e il 18 il vincolo che lascia metà del Fondo non digitalizzata.
- Cap. 43-44: «perché nessuno la porta via?» va segnata come ambiguità voluta oppure pagata.
- Cap. 44-45: mostrare che il bisogno di riscatto di Elana resta e che cambia solo l'oggetto («mai cambiare»).
**Stima:** 200 parole.

---

## Stima complessiva
Circa 2.300-2.700 parole di struttura da riscrivere. Nessun capitolo da aggiungere. Il piano parole (45 capitoli,
circa 90.000 parole, centro al 55%) resta invariato, salvo un possibile accorciamento del 44.

## Cosa non toccare
Apertura in medias res e ritorno all'alba (con A1 cambia solo il tempo verbale); calendario G1-G72; collocazione delle
svolte (12, 25, 35, 41-42) e piano parole; i cap. 19-20; la catena silenzio-tradimento 15→29→32→39 (con A2 cambia il
luogo del 29, non la catena); il protocollo 34→41; la scelta di cancellare gli schemi nel 42; la cartolina con le lame
dritte nel 44; l'ironia drammatica del cap. 1 sulle scene con l'assistente (6, 11, 19).

## Domande bloccanti per l'autore (prima di applicare A2)
1. Chi sigillò l'archivio nel Trecento, se la loggia nasce nel Settecento?
2. Dove sta il registro (luogo accessibile dopo la sigillatura)?
3. Da quale fonte Elana ricava il 1861 nel 17 (copie borboniche annotate, Dell'Aquila, altro)?

## Dopo
Dopo ogni lavoro applicato, il diagnosta rimisura i file toccati. Se due giri non portano miglioramento, ci si ferma.

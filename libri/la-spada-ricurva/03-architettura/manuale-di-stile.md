# Manuale di stile — La Spada Ricurva

Generato da nuovo.py dal briefing (sezione «Direttive») e dal profilo «thriller». Le regole numeriche stanno in libro.yaml e le controlla capitolo.py: qui sono scritte per esteso.

## 1. Voce

La voce è definita in `02-bibbia/voce.md` («Gotico-Analitica»): questo manuale la recepisce e non la riscrive. In
caso di dubbio vale `voce.md`, sezioni 2 (principi), 3 (ritmo e sintassi), 4 (lessico) e 7 (istruzione di
esecuzione). Le regole che non si discutono:

- **Persona:** prima persona di Elena Magnisi, unico punto di vista per tutti i 45 capitoli; «io» per sé, «noi» solo
  per il gruppo. Ciò che Elena non vede arriva solo da documenti, racconti altrui o ricostruzione dichiarata.
- **Tempo:** sempre il presente (decisione dell'autore). Nessuna Elena «di dopo»: niente «ancora oggi», niente «allora
  non sapevo». Passato prossimo e imperfetto solo per ricordi brevi e antefatti. I salti di tempo (cap. 1 a G51,
  cap. 44 gennaio-marzo, cap. 45 di nuovo a G72) li regge l'intestazione, non la voce.
- **Dialoghi:** tra caporali «», battute brevi e poche per scena; attribuzione con un gesto o niente, raramente
  «dice». Pensieri senza virgolette. Le parole del modello di Pietro e i documenti citati (perizie, registro,
  traduzioni, comunicati) vanno anch'essi tra caporali, senza grafie speciali.
- **Tre registri:** gotico (frase media 20-26) per aperture, atmosfera e sommario; analitico (10-14) per scena e
  indagine; lama (3-8) per svolte e chiuse. Mai tre frasi lunghe di fila.
- **Attacco e chiusa:** il capitolo si apre con una sentenza concreta e chiude su un oggetto o un fatto non spiegato,
  in una frase secca e isolata.
- **Metodo:** osservo, confronto, concludo; in forma esplicita al massimo una volta per capitolo.
- **Punteggiatura:** niente punto e virgola, esclamativi, puntini di sospensione.
- **Lessico:** restauro, debito, legge; niente cliché napoletani, niente aggettivi vaghi, niente psicologia
  dichiarata. Anglismi solo nel lessico tecnico di Pietro (file, codice, server, modello).
- **Nomi provvisori:** «l'assistente», «il Professore», «la perita», «il PM», «il Direttore», «il Vicedirettore» restano
  senza nome finché l'autore non li dà; Pietro senza cognome. Nessuna età scritta finché l'autore non la conferma.
- Voce d'autore: si fissa con l'«ok» alla pagina campione.

## 2. Lunghezze

- Obiettivo: 90000 parole, circa 45 capitoli.
- Capitolo: minimo 800, media 1500-2500, massimo 3500 parole.
- Scene: 1-3 per capitolo, ciascuna 800-2500 parole (controllate da capitolo.py; separatore «* * *»).
- Tolleranza: ±15% sul budget del capitolo in piano-parole.md; ±5% sul totale.

## 3. Frase e dialogo

- Frase media: 9-14 parole (valore del profilo thriller). La voce del libro attende 15-19 parole di media, con almeno
  un quinto di frasi ≤ 8 e un quinto ≥ 25 (`voce.md`, sez. 3). Contrasto segnalato nella nota di direzione: finché
  l'autore non approva un override, la soglia del profilo informa e non blocca; in stesura prevale la voce.
- Dialogo: 25-45% delle parole del capitolo.
- Similitudini: al massimo una ogni 400 parole.

## 4. Chiusure

- Chiusura preferita: gancio_domanda. Sigle: D domanda, R rivelazione, P pericolo, X decisione.
- Ogni capitolo dichiara la chiusura nella riga nascosta `<!-- zb: chiusura=… -->`; la sigla prevista sta nella scaletta.

## 5. Tetti e vietati

- Lista nera di base (05-critica rr. 19-21): 19 voci, sempre attive.

## 6. Vincoli

- Nessun vincolo.

## 7. Struttura

- Intestazione del capitolo: «Luogo — giorno e data». Giorno e mese, mai l'anno né il giorno della settimana finché
  l'autore non fissa l'anno; il calendario interno (G1 = 21 ottobre … G72 = 31 dicembre) sta in `cronologia.yaml`.
- Separatore di scena: «* * *».
- Nomi dei file: NN-<slug>.md in 04-manoscritto/.

## 8. Scene obbligatorie del genere

- scoperta del crimine o della minaccia
- falsa pista
- smascheramento
- incidente scatenante che promette il climax
- posta in gioco che cresce da un atto all'altro
- confronto finale tra protagonista e antagonista
- scadenza o corsa contro il tempo

## 9. Override rispetto al profilo (da approvare al gate «documenti», se libro.yaml lo elenca)

- Nessuno.

## 10. Fatti canonici e cose da non cambiare

- L'archivio sotto l'Accademia è rimasto sigillato per oltre settecento anni; vi si accede decifrando un rebus visivo nei dettagli di dipinti barocchi dell'Accademia.
- Claudia decifra il rebus; Lorenzo apre l'archivio (decisione dell'autore).
- Il Fondo Proibito: circa 500 manoscritti di magia pratica, mentalismo e teosofia; tra questi testi vedici dall'India portati a Venezia da due guru e tradotti clandestinamente in latino denso, cifrato ed eretico da alchimisti e dotti.
- I ragazzi non denunciano la scoperta: usano un'IA offline addestrata da Pietro per tradurre e indicizzare i testi, per renderli open-source e donarli ai musei internazionali.
- La Spada Ricurva: loggia plurisecolare nata dalla fusione tra massoneria napoletana, traffici veneziani con l'Oriente e correnti vediche e filosofiche; simbolo: due scimitarre incrociate e piegate.
- L'ultimo re Borbone delle Due Sicilie era della setta, che usava i testi per il controllo politico; la caduta del regno fu anche una guerra occulta tra logge rivali.
- I Borbone possedevano circa un terzo dei volumi, in copie tratte dagli originali; alcuni testi, tra i più importanti, esistono in copia unica solo nella cripta ritrovata (decisione dell'autore: risolve il contrasto con i settecento anni di sigillo).
- La Spada Ricurva esiste già nel Trecento ed è lei a sigillare l'archivio; la massoneria del Settecento è solo una delle sue maschere (decisione dell'autore).
- Il registro della loggia, con i nomi dei Borbone e dei Valli, è nelle mani di Carlo Dell'Aquila; è dal registro che i ragazzi scoprono la guerra occulta del 1861 (decisioni dell'autore).
- La busta del cap. 1 contiene solo la bozza della perizia; la perizia ufficiale la porta a Elena la perita dissidente, all'alba, nel cap. 25 (decisione dell'autore).
- Dopo il sigillo del Trecento la porta non fu mai più aperta: la chiave dipinta nel Seicento tramanda solo la via; la loggia non la forza perché la volta può crollare (decisione dell'autore).
- Il dono ai musei internazionali salta con il ritiro di Dell'Aquila (cap. 35): il Fondo vive solo open-source in rete (decisione dell'autore).
- La pagina dei Valli nel registro riguarda un antenato di Lorenzo: la famiglia è legata alla setta da generazioni, il debito è un'eredità (decisione dell'autore).
- Oggi il Direttore, il Vicedirettore e i vertici dell'Accademia sono della setta.
- La setta detiene i debiti e i titoli finanziari della famiglia di Lorenzo.
- L'assistente viene assassinato dalla setta; dieci giorni dopo arriva la perizia medico-legale: l'ora del decesso è precedente al timestamp di un messaggio minatorio arrivato sul telefono della vittima. Prova che Procura e medicina legale sono colluse.
- Assedio: in una notte di pioggia la setta isola i ragazzi nell'Accademia; Lorenzo passa i dati; l'IA di Pietro si comporta in modo anomalo e manipola i presenti.
- Elena completa l'upload globale: i manoscritti restano open-source sui server internazionali.
- La setta non viene distrutta in superficie; il sistema si ricuce.
- Lorenzo tradisce per debito e alla fine sparisce.
- Il finale: Elena sola all'alba; la conoscenza è libera, ma la voce di quell'intelligenza, umana e artificiale, le resta nella mente.

# Guida breve per l'autore

Il motore è una casa editrice automatica: tu dai l'idea e la voce, gli agenti scrivono, rivedono e impaginano; tu
leggi alle pause e decidi.

## 1. Cominciare un libro
1. Copia `motore/modelli/briefing.md` in `libri/<nome>/briefing.md` e compilalo (storia, personaggi, regole, genere).
2. Nella sessione: «zb nuovo» sul briefing. Nasce la cartella del libro.
3. **La voce**: metti una pagina di prosa che ti piace (tua o di riferimento, almeno 250 parole) in
   `libri/<nome>/00-progetto/voce/campione-1.md`. Per una voce **ibrida** aggiungi una seconda pagina in
   `campione-2.md` e, se vuoi, scrivi in `indicazioni.md` che cosa prendere da ciascuna (es. «ritmo e dialoghi dal
   campione 1, lessico e immagini dal campione 2»). Il motore imita il modo di scrivere, mai le frasi.

## 2. Che cosa succede da solo
- Struttura (architetto) → controllo (diagnosta ed editor strutturale) → documenti e scheda della voce.
- Stesura con **/capitolo**: per ogni capitolo scrive lo scrittore (Opus), il motore misura, il revisore dà sette
  voti tarati (6 = mestiere, 8 = un editor lo terrebbe); sotto 7,5 c'è una correzione mirata, poi si accetta. Ogni
  difetto trovato diventa una «lezione» per i capitoli successivi.
- Ogni 3 capitoli: **pausa di lettura**. Tu leggi e rispondi «ok» oppure «correggi» con le tue note.
- Dopo la stesura: revisione del manoscritto (critico, professore, panel di quattro lettori), line editing (taglio
  del superfluo), copyediting, bozze.
- Grafica: stile dell'interno (essenziale, classico, moderno), quarta di copertina e brief della copertina
  dall'agente grafico, copertina del cartaceo in PDF con le misure KDP («zb copertina», sempre dopo l'impaginazione:
  la costola dipende dalle pagine vere).
- **Copertina fatta da altri**: dai al grafico `06-pubblicazione/copertina/modello-kdp.pdf` (misure esatte). Poi metti
  la sua immagine in `00-progetto/copertina/prima.jpg` (solo la prima, con titolo e autore già scritti: costola e
  quarta le compone il motore) oppure `intera.jpg` (quarta + costola + prima). Serve alta risoluzione (300 DPI alla
  misura di stampa; il motore dice quanti pixel): uno screenshot di solito non basta per la stampa.

## 3. Le tue risposte
- Alla pausa di lettura: «ok» oppure «correggi: …».
- Quando il motore scrive FERMO: leggi il motivo e decidi.
- Per cambiare il motore stesso: scrivi «lavoro sul motore».

## 3b. Quando trovi un errore
- Dimmelo come lo hai visto: diventa una voce del registro dei difetti del libro e un test che il motore non lascia
  più passare (`zb difetti`). I fatti reali (medicina, tecnica, citazioni) restano bloccati finché non sono verificati
  su una fonte o resi generici.

## 4. Prima di pubblicare
- «zb finale»: rifà tutti i controlli (ortografia, grammatica, tipografia, continuità, PDF, KDP, copertina). Il libro
  si chiude solo con 0 errori; un falso allarme si accetta per iscritto, con il motivo.
- Controlla i dati KDP (formati, margini, copertina) sulle pagine ufficiali e registra la verifica:
  «zb verifica KDP fatta AAAA-MM-GG».
- Confronta le misure della copertina con il calcolatore di KDP.

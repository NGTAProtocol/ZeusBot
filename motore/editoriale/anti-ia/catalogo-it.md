# Catalogo anti-IA per l'italiano

Scritto da zero per questo motore. Uso: lo scrittore lo applica mentre scrive; il line editor lo usa per diagnosticare; `zb esito` può controllarne gli elementi misurabili.

## A. Ritmo
1. Frasi tutte di lunghezza simile (tre o più di seguito entro 20% di differenza).
2. Elenchi di tre elementi ripetuti a ogni paragrafo ("A, B e C").
3. Struttura "non solo X, ma anche Y" usata più di una volta per capitolo.
4. Paragrafi tutti della stessa lunghezza.
5. Chiusura di paragrafo con frase a effetto che riassume ("E in quel momento capì tutto").
Cosa fare: alternare per emozione, non per regola. Frase breve dopo un colpo; periodo lungo dove il pensiero scorre.

## B. Formule vuote tipiche
- "Un misto di", "un turbinio di", "una sensazione indescrivibile", "il cuore che batteva forte".
- "Non sapeva ancora che", "il destino stava per", "nulla sarebbe stato più come prima".
- "Un silenzio carico di significato", "l'aria era densa di tensione".
- "In quel momento", "all'improvviso", usati come cerniera ovunque.
- Avverbi in -mente a catena; aggettivi in coppia ("fredda e distante").
Cosa fare: sostituire con un fatto percepibile (cosa fa la mano, cosa sente l'orecchio, cosa manca nella stanza).

## C. Spiegare ciò che si è già mostrato
- Dopo un gesto, la frase che ne dichiara il significato.
- Dialogo seguito da "disse con tono triste/arrabbiato".
- Pensiero che ripete il dialogo appena avvenuto.
Cosa fare: tagliare la spiegazione; se il lettore non capisce, cambiare il gesto, non aggiungere la glossa.

## D. Dialogo
- Personaggi che parlano tutti con lo stesso registro.
- Battute che dicono esattamente ciò che provano.
- Tutti rispondono alla domanda posta (nella vita no).
- Saluti e convenevoli inutili.
Cosa fare: sottotesto, interruzioni, risposte laterali, silenzi, lessico diverso per personaggio.

## E. Aperture e chiusure
- Capitoli che iniziano con meteo, sveglia o descrizione del luogo generica.
- Capitoli che chiudono sempre con una riflessione o con una domanda retorica.
- Gancio sempre dello stesso tipo.
Cosa fare: variare; entrare in scena a cose iniziate; chiudere sull'azione, sull'immagine o sulla battuta.

## F. Vocabolario
- Parole "eleganti" ripetute in tutto il libro (a ogni capitolo la stessa decina).
- Tono letterario uniforme anche dove il personaggio non lo sarebbe.
- Termini astratti al posto di cose.
Cosa fare: un lessico per voce e per personaggio; il nome della cosa, non la categoria.

## G. Imperfezioni naturali credibili (dosate)
Ammesse, con misura: frase sbilenca perché così pensa il personaggio; ripetizione voluta; periodo spezzato; omissione del soggetto; parola dialettale o gergale coerente con la voce; dettaglio lasciato senza spiegazione.
Vietate: errori di ortografia o grammatica veri.
Tetto: un'imperfezione voluta ogni 800-1000 parole circa, mai più di tre per pagina.

## H. Misure per `zb esito` (da implementare)
- deviazione standard della lunghezza delle frasi sotto soglia (monotonia);
- percentuale di frasi con la stessa apertura (stessa parola iniziale) sopra soglia;
- numero di occorrenze delle formule della sezione B per mille parole;
- stesso tipo di chiusura nei capitoli consecutivi.
Le soglie vanno tarate sui mini-libri di prova e scritte nel profilo di genere.

## I. Modalità audit
Il controllo non riscrive: produce un elenco (posizione, schema, proposta) in `06-diagnostica/`. Le correzioni si applicano dopo `ok`.

## Note per il motore (integrazioni)
- **Gravità della prosa**: P0 rompe la lettura o la voce (terzo capitolo di fila con la stessa chiusura; dialogo che
  dichiara il sottotesto); P1 schema evidente e ripetuto; P2 da guardare.
- **Profili**: «narrativa» (prosa fuori dal dialogo: sezioni A, C, E) e «dialogo» (sezione D; le misure di ritmo non
  si applicano al parlato).
- **Vocabolario per livelli** (L1 da sostituire sempre, L2 da segnalare in gruppo, L3 da segnalare per densità): per
  l'italiano i livelli restano vuoti in `motore/dati/antiia.yaml` finché non sono estratti dai dati
  (`zb antiia estrai`, corpus da fornire). Le formule della sezione B sono esempi per lo scrittore e il line editor,
  non una lista che il motore misura.
- **Difetti automatici del modello** (da haowjy/creative-writing-skills, Apache-2.0, riscritti): allargare la scena
  oltre il compito; appiattire la voce in un registro competente; spiegoni; nominare le emozioni; risolvere la
  tensione troppo presto; personaggi tutti ugualmente eloquenti; commento emotivo dopo il momento; chiudere
  un'ambiguità voluta; lingua troppo intensa; ignorare lo stile del progetto.
- **Come si corregge** (da chi-feng/humanizer, MIT, riscritto): per sottrazione, non per sostituzione; rileggere ciò
  che la correzione introduce; non aggiungere dettagli che il testo non ha; non omogeneizzare la voce; un tic conta
  anche se compare una sola volta per capitolo, se torna in ogni capitolo.
- **Lineette nella narrazione**: dove la lineetta apre la battuta, usarla anche per gli incisi della narrazione
  confonde la pagina (idea di book-genesis-studio, MIT); misura `lineette_narrazione`.
- **Misure implementate** (sezione H): `motore/script/antiia.py`, lanciato da `zb esito` (variazione delle frasi,
  aperture uguali, formule per mille, lineette nella narrazione, varietà lessicale, chiusure uguali); soglie in
  `motore/dati/antiia.yaml`, tarate sui mini-libri; report in `06-diagnostica/anti-ia/NN.md`.


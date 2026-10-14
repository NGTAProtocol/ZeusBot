# Manuale di stile — Il quaderno nell'ulivo (La Banda della Gravina, 1)

Generato da nuovo.py dal briefing (sezione «Direttive») e dal profilo «giallo». Le regole numeriche stanno in libro.yaml e le controlla capitolo.py: qui sono scritte per esteso.

## 1. Voce

- Voce: da fissare con la pagina campione.
- Voce dalla banca-voci: mistero-ed-epicita, ambientazione altro; scheda e briefing da rileggere prima di ogni capitolo (zb avvio, zb voce mostra).
- Realistico, con un solo elemento strano: l'ulivo e la rete di radici, spiegati senza magia.
- Ritmo serrato, capitoli brevi, descrizioni corte, poche similitudini; comico ma mai stupido.
- Voce della banca-voci: Mistero ed Epicità (mistero-ed-epicita), adattata al tono realistico.
- Voce d'autore: da completare dopo l'«ok» alla pagina campione.

## 2. Lunghezze

- Obiettivo: 32500 parole, circa 25 capitoli.
- Capitolo: minimo 1000, media 1200-1400, massimo 1600 parole.
- Scene: 1-2 per capitolo, ciascuna 500-1400 parole (controllate da capitolo.py; separatore «* * *»).
- Tolleranza: ±15% sul budget del capitolo in piano-parole.md; ±5% sul totale.

## 3. Frase e dialogo

- Frase media: 9-14 parole.
- Dialogo: 25-45% delle parole del capitolo.
- Similitudini: al massimo una ogni 400 parole.

## 4. Chiusure

- Chiusura preferita: gancio_domanda. Sigle: D domanda, R rivelazione, P pericolo, X decisione.
- Ogni capitolo dichiara la chiusura nella riga nascosta `<!-- zb: chiusura=… -->`; la sigla prevista sta nella scaletta.

## 5. Tetti e vietati

- Vietato: «ologramma».
- Vietato: «cristallo luminoso».
- Vietato: «onde neurali».
- Lista nera di base (05-critica rr. 19-21): 19 voci, sempre attive.

## 6. Vincoli

- «Sviluppo Territoriale Sostenibile» non compare nei capitoli 1-24.

## 7. Struttura

- Intestazione del capitolo: «# N — Titolo» e basta: niente riga di luogo e data (libro per ragazzi; decisione dell'autore del 14/10).
- Separatore di scena: «* * *».
- Nomi dei file: NN-<slug>.md in 04-manoscritto/.

## 8. Scene obbligatorie del genere

- scoperta del crimine
- falsa pista
- smascheramento
- incidente scatenante che promette il climax
- indizi leali prima della soluzione

## 9. Override rispetto al profilo (da approvare al gate «documenti»)

- parole.target_totale: 32500 — motivo: libro per ragazzi 9-12 anni (30.000-35.000 parole, 25 capitoli da 1.200-1.400): manca un profilo ragazzi, si usa il più vicino (giallo) — Lunghezza: 32500 fuori dai formati del profilo (40000-180000)
- capitoli.minimo: 1000 — motivo: libro per ragazzi 9-12 anni (30.000-35.000 parole, 25 capitoli da 1.200-1.400): manca un profilo ragazzi, si usa il più vicino (giallo) — Capitoli (minimo): 1000 invece di 800 del profilo
- capitoli.media: [1200, 1400] — motivo: libro per ragazzi 9-12 anni (30.000-35.000 parole, 25 capitoli da 1.200-1.400): manca un profilo ragazzi, si usa il più vicino (giallo) — Capitoli (media): [1200, 1400] invece di [1500, 2500] del profilo
- capitoli.massimo: 1600 — motivo: libro per ragazzi 9-12 anni (30.000-35.000 parole, 25 capitoli da 1.200-1.400): manca un profilo ragazzi, si usa il più vicino (giallo) — Capitoli (massimo): 1600 invece di 3500 del profilo
- capitoli.scene_per_capitolo: [1, 2] — motivo: libro per ragazzi 9-12 anni (30.000-35.000 parole, 25 capitoli da 1.200-1.400): manca un profilo ragazzi, si usa il più vicino (giallo) — Scene (numero): [1, 2] invece di [1, 3] del profilo
- scene.lunghezza: [500, 1400] — motivo: libro per ragazzi 9-12 anni (30.000-35.000 parole, 25 capitoli da 1.200-1.400): manca un profilo ragazzi, si usa il più vicino (giallo) — Scene (lunghezza): [500, 1400] invece di [800, 2500] del profilo

## 10. Fatti canonici e cose da non cambiare

- Ginosa e le gravine (Puglia) sono il luogo del volume 1; la gravina è un personaggio: decide passaggi, enigmi, scoperte e pericoli.
- Il mistero è umano e si risolve con i quaderni cifrati di Rosa, osservazione e deduzione.
- Il mistero compare entro il capitolo 2; la Terravox è presente fin dal capitolo 1.
- L'archeologia arriva come rivelazione finale, non come gancio d'apertura.
- Il finale apre il volume 2 con la Sviluppo Territoriale Sostenibile S.r.l., legata a un ex dirigente della Terravox.
- Ogni ragazzo della banda ha un talento, un difetto e una funzione precisa nella soluzione.
- Nessun cristallo luminoso, nessun potere, nessuna magia: l'ulivo e la rete di radici hanno una spiegazione.
- Droni e sensori del nonno sono un aiuto, non uno spettacolo.
- Nessuna lezione di storia: la storia emerge dall'azione.
- Da evitare, perché troppo vicino a un libro del 2025: masseria con scheletro, dolmen, leggenda di sangue, reperto preistorico come gancio.
- Pagina enigma in circa 12 capitoli, non in tutti; soluzioni in fondo al libro; mai un codice in ogni capitolo.

## 11. La voce del libro (approvata al gate «documenti» il 14/10/2026)

Base: «Mistero ed Epicità» (mistero-ed-epicita), sezioni 1, 2, 3 e 7 della scheda (testo dell'autore).
Le sezioni 4-6 e `divieti.yaml` della banca-voci non sono state scritte dall'autore: non fanno da modello
(vedi `00-progetto/report-difetti-motore.md`). Dove la voce contrasta con il libro vince il libro.

Cosa si prende dalla voce:
- Ritmo serrato; ogni capitolo avanza con un indizio che si incastra nel precedente; gancio a fine capitolo.
- Lavoro di squadra: ogni ragazzo parla e agisce con la voce del suo talento.
- Dialoghi rapidi, fatti di intuizioni e di aiuto reciproco nel pericolo.
- Ogni enigma si risolve con ingegno e cooperazione, mai per coincidenza.
- Nessuno spiegone: il luogo si svela mentre i ragazzi agiscono.
- Personaggi non infallibili.
- Senso di scoperta e di meraviglia.

Cosa si adatta al libro (precedenza del manuale):
- Niente fantasy, niente spade, niente meccanismi magici: la meraviglia viene da cose vere (la gravina, un
  ulivo di mille anni, un muro antico, un cifrario risolto, un falco grillaio).
- Lessico concreto del luogo invece di quello epico: tufo, calcare, gravina, ciglio, muretto a secco,
  cappero, lentisco, timo, carrubo, cisterna, chiesa rupestre, Ape, quaderno, sensore, drone, scheda.
- «Evocativo» vuol dire preciso, non solenne: una parola giusta invece di tre aggettivi.
- Descrizioni corte: al massimo due o tre frasi, poi un gesto o una battuta; almeno due sensi (caldo,
  odore, rumore) quando si entra in un luogo nuovo.

## 12. Punto di vista e tempo

- Terza persona, vicina a Pino (approvata): il lettore sa quello che sa Pino, non di più.
- Passato remoto e imperfetto.
- Nessun narratore che commenta o fa la morale.

## 13. Lettore 9-12

- Frasi brevi e chiare; una sola subordinata per frase quando serve.
- Parole difficili solo se il contesto le spiega (oppure le spiega un personaggio in una battuta).
- Paura sì, crudeltà no; nessun personaggio muore in scena; adulti cattivi mai violenti in modo esplicito.
- Umorismo dalle situazioni e dai caratteri (Checco, l'Ape, Ciuffo), mai a spese di chi è debole.
- Dialetto: spento (ambientazione «altro»); al massimo una o due parole di dialetto per capitolo, solo in
  bocca a Checco o agli anziani, capibili dal contesto (approvato).

## 14. Enigmi e pagine enigma

- Pagina enigma in 12 capitoli: 2, 4, 6, 8, 9, 11, 13, 15, 17, 19, 21, 23 (scaletta). Negli altri no.
- La pagina enigma sta alla fine del capitolo, dopo il gancio, con un titolo fisso («L'enigma della banda»)
  e una domanda sola. Eccezione approvata dall'autore il 14/10/2026 (correzione C1): nel cap. 4 la pagina
  chiude la scena 1, prima della partenza per la terrazza; la scena 2 riparte dal dito di Lucia che si ferma.
  Stesso schema nei cap. 8 e 9 (decisione D1 dell'autore del 14/10/2026) e nei cap. 13 e 15 (decisione E1).
- La soluzione non è mai spiegata nel testo prima della pagina enigma (nessun percorso casella per casella,
  nessun calcolo mostrato).
- Equità: tutto quello che serve è già comparso nel testo prima della pagina enigma. Il lettore deve poter
  dire «era lì!».
- Il capitolo successivo mostra la soluzione trovata dai ragazzi; la soluzione spiegata sta in fondo al libro.
- Tipi diversi, mai due uguali di fila: cifrario, mappa, scheda indizio, grafico, testimonianze, ombra.
- Mappe e schede indizio: disegni semplici, leggibili su carta e su Kindle (da impaginare a parte).

## 15. Divieti del libro

- Vietato: magia, poteri, oggetti che si illuminano da soli, visioni.
- Vietato: soluzioni per coincidenza o per fortuna; un adulto che risolve al posto dei ragazzi.
- Vietato: lezioni di storia o di scienza; la storia emerge dall'azione.
- Vietato: masseria con scheletro, dolmen, leggenda di sangue, reperto preistorico come gancio.
- Vietato: frasi, descrizioni, metafore o ordine dei capitoli del vecchio testo.
- Tetto: similitudini, al massimo una ogni 400 parole (profilo); meglio meno.

## 16. Rete di radici: cosa è certo e cosa no

- Certo, nel libro: i sensori di Michele misurano acqua e vibrazioni nelle radici. Le scosse degli scavi e il
  calo dell'acqua si vedono nei grafici. L'Ulivo Pensante reagisce per primo perché ha le radici più profonde.
- Ipotesi, solo di Michele: che gli ulivi «si parlino» attraverso i funghi del suolo. Lo dice sempre come
  ipotesi («Secondo me…», «Non lo sa nessuno, ma…»), mai il narratore, mai come fatto.

## 17. Archeologia: prudenza

- Il muro è «antico, di grosse pietre squadrate». Nessuno dice di più finché non arriva il funzionario.
- Il funzionario parla con prudenza: «probabilmente di età greca, da verificare».
- Vietato: Sparta, date precise, popoli o fondazioni nominati, ogni affermazione storica non verificata.

## 18. Enigmi

- Testo, indizi da seminare, soluzioni e controlli di equità: `03-architettura/enigmi.md`. Gli indizi elencati
  lì vanno messi nei capitoli indicati, prima della pagina enigma.

## 19. Dialoghi

- Sempre con la lineetta «—» a inizio riga (decisione dell'autore del 14/10/2026), mai con le virgolette «».
  È anche la forma che il motore misura: con le virgolette il dialogo risulterebbe 0% (vedi
  `00-progetto/report-difetti-motore.md`).
- Inciso: «— Battuta, — disse Checco. — Seguito.»

## 20. Mezzogiorno, mappa, tic (correzioni dell'autore del 14/10/2026)

- «Mezzogiorno» nel libro è il mezzogiorno del sole: il sole è più alto, l'ombra è la più corta e punta a
  nord. D'estate, con l'ora legale, cade verso l'una dell'orologio (cap. 3; vale per l'enigma 7 e il cap. 13).
- Mappa canonica: `03-architettura/mappa-di-lucia.md`. Ogni posizione nei capitoli e nelle pagine enigma la
  segue; un cambiamento di posizione si fa prima lì.
- Tic da tenere bassi: il verbo «contare» al massimo 3 volte per capitolo, nei punti chiave; «poi» e
  «senza dire niente» con parsimonia.
- Pagine enigma leggibili anche su Kindle: elenchi brevi, niente tabelle larghe.

# Nota di direzione — La Spada Ricurva

Ruolo: direttore editoriale. Fonti: briefing (prevale), `03-struttura/` chiusa, `02-bibbia/voce.md`. Questa nota non
cambia la struttura; le proposte si applicano solo con l'ok dell'autore.

## Posizionamento
Thriller dark academia italiano, circa 90.000 parole in 45 capitoli, prima persona al presente. Sta accanto a Tartt
(«Dio di illusioni»), Bardugo («La nona casa») e Michaelides («Le vergini»), ma con due cose che quei libri non
hanno: Napoli sotterranea come materia (tufo, archivi, laboratori di restauro, non cartolina) e una domanda di oggi,
cioè chi possiede il sapere quando una macchina può tradurlo e diffonderlo in una notte. Scaffale: narrativa
straniera/italiana di qualità con taglio thriller, non fantasy: il soprannaturale resta ambiguo fino all'ultima riga.

## Lettore ideale
Una lettrice o un lettore tra i 25 e i 45 anni, laureato in una materia umanistica o rimasto attaccato all'università
da fuori; ha letto «Dio di illusioni» due volte e «La nona casa» in una settimana; conosce il nome di Caravaggio e
non quello di un pigmento, e gli piace impararlo da chi lo maneggia. Legge la sera, a capitoli interi, e smette solo
quando una chiusa gli lascia un oggetto da ricordare. Diffida degli eroi e si fida dei dettagli; ha avuto almeno una
volta la sensazione che un'istituzione gli sorridesse per farlo stare zitto. Napoli la conosce di passaggio o per
sentito dire, e vuole vederla da sotto.

## Promessa (verificabile capitolo per capitolo)
1. **Un indizio concreto e una minaccia per capitolo**: un pigmento, un orario, una parola tradotta male, una
   perizia; e qualcuno che osserva. Verifica: la chiusa di ogni capitolo nomina un oggetto o un fatto non spiegato
   (sigle D/R/P/X della scaletta).
2. **Il sapere è vero e costa**: ogni scoperta si paga (carriera 6, borsa 18, mentore 20, giustizia 25, originali 35,
   gruppo 43). Verifica: la «posta» di ogni capitolo sale o almeno non scende.
3. **Nessuno è puro, Elana compresa**: ogni personaggio ha un movente sporco; Elana tace e usa il protocollo.
   Verifica: in ogni capitolo con il gruppo, almeno un gesto mosso da ambizione, paura o debito.
4. **La voce non cede**: prima persona di Elana, presente, caporali, tre registri. Verifica: misure del motore e
   `voce.md`.
5. **Finale amaro e non pulito**: l'upload riesce, la setta resta, Elana è sola con una voce in testa (canone).

## Cosa rende il libro riconoscibile
- La protagonista guarda il mondo come una restauratrice guarda una tela: luce radente, vernice, ritocco. Il metodo
  «osservo, confronto, concludo» è la sua firma.
- Due scimitarre incrociate e piegate che tornano su tela, pietra, specchio, e una sola volta dritte.
- Un'IA che parla con la cadenza di un morto: thriller tecnologico e gotico nello stesso oggetto.
- Documenti che mentono con precisione: la perizia rettificata, il comunicato del Direttore.

## Rischi
1. **Lentezza della voce gotica nell'apertura** (cap. 1-12, 28%): la densità sensoriale chiesta può soffocare il
   ritmo. Rimedio: registro analitico nelle scene, gotico solo nei sommari; ogni capitolo chiude su un oggetto.
2. **Spiegazioni tecniche dell'IA** (13, 14, 23, 30): rischio di lezione. Rimedio: solo «in parole di Pietro», e
   sempre con un dettaglio che non torna.
3. **Ambiguità del soprannaturale**: se la «forza viva» o la voce vengono spiegate, il finale si sgonfia; se restano
   troppo vaghe, il lettore si sente imbrogliato. Rimedio: spiegazione razionale sempre presente, mai sufficiente.
4. **Elana antipatica**: superiorità e silenzi possono allontanare. Rimedio: il prezzo del riscatto è visibile (8, 26)
   e la voce registra anche le sue colpe.
5. **Napoli da cartolina**: vietata dal lessico della voce; da controllare in revisione.
6. **Personaggi ancora senza tratti fissi**: aspetto, modo di parlare e abitudini quasi tutti [DA CONFERMARE] (sotto).
   Finché mancano, gli scrittori rischiano di inventare tratti diversi da capitolo a capitolo: ogni tratto inventato in
   stesura va riportato nella capsula e poi nel codex.

## Contrasti e decisioni da prendere (proposte)
1. **G41 è il 30 novembre, non dicembre.** Con G1 = fine ottobre e l'assedio il 30 dicembre (= G71), G1 cade il 21
   ottobre e G41 il 30 novembre; la scaletta scrive «G41 · dicembre» e le scelte fisse «inizio dicembre». Proposta:
   intestazione del cap. 20 con «30 novembre» (nessun effetto sulla struttura: la perizia resta a dieci giorni, G51 =
   10 dicembre). In alternativa l'autore sposta l'ancora.
2. **G12 = 1 novembre (Ognissanti).** Il cap. 6 ha un seminario in aula in un giorno festivo. Proposta: in stesura un
   seminario straordinario «a porte chiuse» (rafforza l'arena) oppure il 2 novembre come data d'intestazione.
3. **G66-G67 = Natale e Santo Stefano.** L'aggressione a Claudia a Natale funziona (è sola, la città è ferma). Il cap.
   34 in Procura il 26 dicembre è poco plausibile: proposta, il PM è «di turno» e il corridoio vuoto spiega perché
   cede. Da decidere prima del 34.
4. **Frase media.** Il profilo thriller indica 9-14 parole; `voce.md` attende 15-19. Proposta: override della frase
   media a 15-19 in `libro.yaml` (serve l'ok dell'autore); fino ad allora la soglia informa e non blocca.
5. **Anno della storia.** Non fissato: la cronologia usa il 2025 solo per calcolare le distanze. Va scelto prima di
   scrivere un giorno della settimana.
6. **Codex: vecchie schede con id sbagliati.** I file `elana-magnisi.md`, `claudia-rinaldi.md`, `lorenzo-valli.md`,
   `marco-mina-minervini.md`, `carlo-dell-aquila.md`, `il-professore-di-arte-moderna.md`, `l-assistente.md` non
   corrispondono ai tag della scaletta e sono sostituiti dalle nuove schede (`elana.md`, `claudia.md`, …): vanno
   rimossi (git rm) per non avere due schede per persona.
7. **Piano residuo (`piano-revisione-struttura.md`).** Applicati nei documenti, senza toccare `03-struttura/` (che è
   chiusa e ha un'impronta): n. 2 e n. 3 come chiarimenti in `02-bibbia/bibbia.md` («La regola della porta») e nelle
   schede `ipogei.md` e `cripta.md`; n. 4 nella scheda `perita.md` (bozza e perizia ufficiale marcate [canone]). Il n.
   1 resta da fare in stesura nel cap. 25. Se l'autore vuole le mezze righe anche nelle schede 28 e 29 della scaletta,
   serve riaprire la struttura.
8. **Briefing r. 42 e r. 43** (dono ai musei; loggia «nata» dalla massoneria) sono superati dalle decisioni dell'autore
   (r. 46 e r. 50): la bibbia lo annota accanto ai due fatti.

## Proposte su titolo, copertina, prezzo
Nessuna decisione presa. Titolo: «La Spada Ricurva» regge (nome della loggia, simbolo visivo forte); alternativa da
valutare: «Il Fondo Proibito». Copertina: le due lame piegate in un dettaglio di tela sotto luce radente, toni bruni e
freddi, nessun volto. Prezzo e formato: da decidere con l'autore.

## Domande per l'autore ([DA CONFERMARE] del briefing: non sono canone)
1. **Età** di Elana (28), Claudia (21), Lorenzo (26), Mina (25), Pietro (27), Dell'Aquila (60), Professore (60);
   età dell'assistente da definire. Servono per `cronologia.yaml` (nascite).
2. **Aspetto («Fissi» e «Variabili»)** di tutti i personaggi; per Dell'Aquila c'è solo «elegante», per il Professore
   solo «formale».
3. **Modo di parlare («Come parla»)** di Claudia, Lorenzo, Mina, Pietro e dell'assistente (Elana, Dell'Aquila e
   Professore ce l'hanno).
4. **«Da solo»** (che cosa fa ciascuno quando nessuno lo guarda) di tutti i personaggi.
5. **Nomi**: l'assistente, il Professore, la perita, il PM, il Direttore, il Vicedirettore; cognome di Pietro.
6. **Elana**: provenienza (città, famiglia, classe), che serve al riscatto sociale; dottoranda dell'Accademia o di
   un'altra sede con un posto in laboratorio all'Accademia.
7. **Epoca**: autunno-inverno con pioggia [DA CONFERMARE]; anno esatto.
8. **Pseudonimo dell'autore** (indicato «da definire» in struttura; il briefing riporta V. M. Barone).

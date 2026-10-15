PROMPT PER NUOVA CHAT DI CLAUDE CODE - ESEGUI TUTTO QUI

Questa è una chat nuova: non hai memoria di conversazioni precedenti. Tutto ciò che ti serve è in questo prompt e nel repository. Sei l'unico responsabile del lavoro: portalo avanti da solo in questa chat, fino alla fine, senza rimandarmi ad altre chat e senza chiedermi di consultare altri. Esamina tu stesso il repository, i file e i repository esterni indicati.

FILE DI RIFERIMENTO: cerca nel repository (motore/, docs/, radice) editoriale_tutto.md oppure editoriale.zip. Se non li trovi, scrivimelo in una riga e prosegui con le parti che non ne dipendono (vedi 2.1).

RIPARTENZA E AVANZAMENTO (obbligatorio):
- All'inizio controlla se esiste docs/AVANZAMENTO_LAVORO.md. Se esiste, leggilo e riprendi dalla prima sezione non completata. Se non esiste, crealo con le sezioni 1-13 del lavoro e lo stato di ognuna (da fare / in corso / fatto, con hash del commit).
- Aggiorna quel file dopo ogni commit.
- Se il contesto sta per finire o devi fermarti per qualsiasi motivo: aggiorna il file, fai commit e push, e scrivimi una sola riga: "ripartenza: apri una nuova chat e scrivi: riprendi da docs/AVANZAMENTO_LAVORO.md".
- Quando rispondo "riprendi", rileggi questo prompt (se è nel repository come docs/PROMPT_NUOVA_CHAT.md) e il file di avanzamento, esegui zb avvio e continua.

DA QUI IN POI È IL LAVORO COMPLETO.

LAVORO SUL MOTORE - PROMPT MASTER (sostituisce tutti i prompt precedenti)

Repository ZeusBot, ramo motore. Obiettivo: trasformare il motore da linea di produzione in una casa editrice di alto livello, per qualsiasi libro, in italiano e in inglese, con pochi token e subagenti. Questo è un lavoro sul motore (zb lavoro motore). I libri esistenti NON fanno parte di questo lavoro.

=== 0. REGOLE INDEROGABILI ===
0.1 Il motore resta pulito: nessun libro, nessun nome di libro o di autore reale, in motore/, docs/ o nei commit del ramo motore.
0.2 Non inventare: ogni formato, licenza, dato o comportamento da verificare va controllato su fonte ufficiale o sul file reale. Se non riesci a verificarlo, dillo e non farlo a metà.
0.3 Trasparenza: per ogni repository o strumento valutato scrivi "letto: README / file X / non letto". Valuta leggendo i file veri (prompt, codice, licenza), non solo le descrizioni.
0.4 Licenze: prima di prendere qualsiasi cosa leggi la LICENSE del repository. MIT e Apache-2.0: puoi adattare con attribuzione in docs/ATTRIBUZIONI.md. CC BY-NC-SA, licenza assente o non chiara: SOLO idee generali riscritte da zero, mai testo, e segnala il caso a me. Tutto va tradotto e adattato in italiano; gli originali non entrano nel repository.
0.5 Metodo: lavora in autonomia fino alla fine. Fermati e chiedimi SOLO per: licenza non chiara o non compatibile, cancellazioni (prima sposta in una cartella nuova e verifica che sia completo), errori di push, conflitti tra regole.
0.6 Precedenza delle regole (una sola scala): 1 manuale del libro e libro.yaml; 2 briefing e scheda della voce (se contrastano vince il briefing, il contrasto si segnala); 3 profilo di genere; 4 motore/editoriale/; 5 procedura del motore. Ogni contrasto si segnala.
0.7 Non toccare i rami dei libri vecchi (hanno un CLAUDE.md proprio per mia scelta). Non scrivere nomi di rami di libri sul ramo motore.
0.8 Comunicazione: risposte brevi, senza preamboli né giudizi. Report di sessione ogni 5 scambi o su "passaggio".

=== 1. AVVIO E FOTOGRAFIA DEI "RUDERI" ===
1.1 Esegui zb avvio e riporta la riga "Letto".
1.2 Prima di modificare qualsiasi cosa, scrivi docs/STATO_ATTUALE.md: elenco delle 28 script con cosa fanno e quali comandi zb le usano; punti deboli noti (recinto che non vede Bash; hook spenti sul ramo motore; "lavoro sul motore" non verificabile; report ogni 5 scambi non controllato; due scale di precedenza; skill nominate ma assenti; voci copiate e nomi reali nei docs del ramo motore; README sbagliato sugli hook; PROCEDURA.md senza recinto; comandi elencati tre volte; esportazioni doppie in docs/; arcaismi e LEGGIMI duplicati; requirements mancante; prove non automatiche; modello libro.yaml senza appendici; dati KDP con ultima_verifica null).
1.3 Per ogni script decidi: tieni / semplifica / accorpa / elimina, con motivo. Tieni le verifiche meccaniche affidabili (avvio, stato, esito, continuita, ortografia, compila, impagina, pdf, pacchetto, kdp). Prima di eliminare, sposta in una cartella nuova e verifica.

=== 2. LIVELLO EDITORIALE (motore/editoriale/) ===
2.1 Cerca l'allegato editoriale.zip oppure editoriale_tutto.md (file unico con righe "=== FILE: percorso ===" e "=== FINE FILE ==="). Ricrea/decomprimi i file sotto motore/editoriale/ con contenuto esatto; verifica che il numero dei file coincida. Se non trovi nessuno dei due, scrivi in docs/DA_FORNIRE.md cosa manca e prosegui con ciò che non ne dipende, senza inventare quei file.
2.2 Se hai già creato qualcosa di tuo sugli stessi temi, non cancellarlo: confrontalo, tieni la versione di editoriale/ come base, integra solo ciò che manca e dimmi in una riga cosa hai cambiato.
2.3 Contenuto atteso (28 file): percorso con gate, fase struttura, diagnosi (principi, contratto del libro, dieci passaggi, gravità e rapporto), otto ruoli (diagnosta, direttore editoriale, architetto della struttura, scrittore con voce, editor strutturale, line editor, correttore di italiano, correttore di bozze), nove agenti in agenti/, catalogo anti-IA, criteri del correttore, risparmio-token. Verifica che i file ricreati siano 28 e riporta il numero.

=== 3. PERCORSO DA CASA EDITRICE ===
Ordine con gate approvati da me: 1 briefing; 2 apertura cartella unica del libro; 3 STRUTTURA; 4 revisione della struttura (diagnosta, poi editor strutturale con piano di revisione); 5 documenti; 6 pagina campione; 7 stesura capitolo per capitolo; 8 revisione strutturale del manoscritto (diagnosta, poi editor strutturale con piano di revisione, gate sul piano); 9 line editing; 10 copyediting; 11 bozze; 12 chiusura meccanica (continuita, ortografia, compila, impagina, pdf, pacchetto, kdp, pronto).
3.1 Cablalo in zb e in motore/script/fase.py: ogni gate si apre con zb pronto e si chiude con ok / avanti / correggi.
3.2 FASE STRUTTURA (prima dopo il briefing, prima di ogni documento): zb nuovo crea 03-struttura/ con i nove file previsti (premessa e promessa, logline e tema, personaggi chiave, atti e svolte, scaletta per capitolo, sottotrame e promesse, tensione e ritmo, piano parole, scelte fisse di punto di vista/tempo/voce). Revisione strutturale in sessione separata. Nessun documento o capitolo prima del gate "struttura".
3.3 VARIETÀ STRUTTURALE (idea da Book-pipeline, riscritta da te): l'architetto sceglie e motiva una macrostruttura (3 atti, 4 atti, 5 atti, dittico, in medias res, mosaico, slow-burn, circolare), con svolte non fisse sui quarti esatti e capitoli di numero e lunghezza che nascono dal contenuto. Niente etichette automatiche "Atto 1/2/3". zb esito segnala capitoli di lunghezza quasi uguale.
3.4 La scrittura NON include revisione: chi scrive un capitolo non lo rivede nella stessa sessione (nessun line editing dentro la fase di stesura).

=== 4. CARTELLA UNICA DEL LIBRO ===
4.1 Dopo il briefing la prima azione è aprire UNA sola cartella libri/<slug>/ (zb nuovo). Tutto ciò che riguarda quel libro vive solo lì (briefing, struttura, bibbia, manoscritto, capsule, appendici, output, report, pacchetto KDP, passaggio di consegne, traduzioni, log). Il libro non scrive né legge altri libri; il motore e la banca-voci si leggono in sola lettura. Il nome del libro non compare mai fuori da libri/<slug>/. Un solo libro attivo per sessione; per cambiare: zb lavoro libro <slug> e nuovo zb avvio.
4.2 Controlli veri, perché il recinto non vede Bash: (a) a ogni salvataggio e in zb avvio, controllo su git dei file modificati: se anche uno è fuori da libri/<slug>/ (esclusi i merge del motore dichiarati) il salvataggio è rifiutato; (b) estendi il recinto a Bash (redirect, tee, sed -i, cp, mv, rm) dichiarando i limiti residui; (c) prova con due mini-libri inventati: lavorare sul primo non tocca il secondo né il motore.

=== 5. RUOLI COME SUBAGENTI E RISPARMIO DI TOKEN ===
5.1 Fonte unica: motore/editoriale/agenti/*.md (formato dei subagenti di Claude Code: file Markdown con frontmatter, cartella .claude/agents/). Verifica il formato corrente sulla documentazione ufficiale (name e description obbligatori; tools e model facoltativi; alias dei modelli) e adegua i file.
5.2 zb agenti attiva|stato|disattiva (solo sui rami dei libri, con ok dell'autore) copia gli agenti in .claude/agents/. Sul ramo motore restano spenti, con prova.
5.3 Capsule di continuità: dopo ogni capitolo approvato zb capsula <libro> N scrive 07-capsule/NN.md (circa 180 parole: eventi, personaggi presenti e cosa sanno, informazioni date, promesse aperte/chiuse, cosa cambia, stato emotivo, ultima immagine). Scrittore e revisori leggono le capsule, non i capitoli precedenti interi. zb avvio e zb esito verificano che esistano.
5.4 Orchestrazione: la sessione principale non scrive prosa, chiama l'agente del passo con slug e capitolo e legge solo la risposta breve (massimo 10 righe). Scrittura in sequenza; line editing, copyediting e controlli per capitolo in parallelo, massimo 3 alla volta, configurabile. Un subagente per capitolo, contesto pulito. Orchestrazione per dipendenze (idea da kindle-book-agency).
5.5 Risparmio: gli script fanno tutto il meccanico; output di zb massimo 40 righe con rimando al report; i report citano capitolo e riga e non incollano brani; modifiche puntuali (Edit/str_replace) nei revisori; docs/ mai letto durante il lavoro; CLAUDE.md massimo 30 righe e senza nomi di libri; prefisso delle istruzioni stabile per il caching.
5.6 Modelli per ruolo in un solo file di dati: forte per architetto ed editor strutturale, medio per scrittore, line, copy e bozze, leggero per capsula. Se il modello leggero sbaglia nel copyediting italiano, alza solo quel ruolo.
5.7 Misura: zb consumo registra per sessione capitoli, parole, file e righe letti, subagenti, durata. Prova su un mini-libro con e senza capsule. Non dichiarare percentuali non misurate.

=== 6. ANTI-IA ===
6.1 Struttura (da ai-writing-auditor, licenza da verificare): livelli di vocabolario (da sostituire sempre / da segnalare in gruppo / da segnalare per densità), gravità P0/P1/P2, profili per tipo di testo con profilo "narrativa" e "dialogo".
6.2 Il vocabolario ITALIANO non va inventato: estrailo dai dati (parole e formule più frequenti nei testi scritti da Claude, confrontate con prosa italiana umana) e fino ad allora il catalogo italiano contiene solo schemi strutturali (ritmo, spiegare ciò che è già mostrato, chiusure uguali, dialogo troppo esplicito), senza liste di parole.
6.3 Idee da integrare riscritte: file di regole dei segni da IA e pacchetti di insidie per tipo di opera (Scriven, MIT); disciplina contro i difetti automatici senza cancellare ambiguità, omissioni e ripetizioni volute (haowjy, Apache-2.0).
6.4 Imperfezioni naturali credibili, dosate, mai errori di lingua veri. Modalità audit non distruttiva in zb esito, con misure (deviazione della lunghezza delle frasi, aperture uguali, formule per mille parole, chiusure uguali in capitoli consecutivi), soglie tarate sui mini-libri.

=== 7. CORRETTORE PROFESSIONALE ITALIANO ===
Documento di criteri e passaggio operativo (accenti ed e/è, accordi, tempi, punteggiatura del dialogo, ripetizioni, parole vere sbagliate, coerenza di maiuscole e nomi). Indica cosa fanno Hunspell e LanguageTool e cosa resta alla lettura mirata. Rendi stabile l'installazione di LanguageTool (script e documentazione di ZB_LANGUAGETOOL) e verifica che il livello b di zb ortografia giri davvero.

=== 8. LINGUE E TRADUZIONE ===
8.1 Profili di lingua: motore/editoriale/lingue/it/ e /en/, ciascuno con catalogo anti-IA, criteri del correttore e glossario editoriale. libro.yaml ottiene lingua_originale e lingue_target. Il motore deve poter scrivere un libro direttamente in inglese con gli stessi ruoli e gate.
8.2 zb traduci <libro> --a <lingua>, tutto in libri/<slug>/08-traduzione-<lingua>/. Gate: guida di traduzione (voce, registro, resa di dialetto e riferimenti locali, britannico/americano) e glossario deciso PRIMA del capitolo 1 (un termine = una traduzione). Traduzione capitolo per capitolo in sequenza con guida, voci del glossario presenti, capsule precedenti e ultime righe del capitolo tradotto precedente. Fedeltà: niente aggiunte, niente note o didascalie inventate, errori dell'autore resi come scritti. Controlli meccanici per capitolo: stesso numero di paragrafi e battute, numeri e date, nomi dal glossario, parole italiane residue, rapporto di lunghezza. Poi line editing e copyediting nella lingua di arrivo (ruoli separati), revisione affiancata con scheda di fedeltà da un revisore in sessione nuova, ritraduzione a campione (idea da Scriven) per verificare la fedeltà, pacchetto KDP della lingua di arrivo.
8.3 Nel resoconto: consiglia lettura finale di un madrelingua per edizioni commerciali; verifica sulla fonte ufficiale cosa chiede KDP sulla dichiarazione di contenuti tradotti con IA e riportalo senza darlo per scontato.
8.4 Confronta traduzione sequenziale e a blocchi con ancora di stile su un mini-libro e riporta quale tiene meglio la voce.

=== 9. REPOSITORY ESTERNI (studio vero, scheda per ciascuno in docs/ANALISI_REPOSITORY.md) ===
Già letti da me (README): 
- haowjy/creative-writing-skills (Apache-2.0): agenti coordinatore, scrittore, critico, editor olistico, lettore simulato, controllo di continuità, creatore di stile; knowledge base con stili, personaggi, mondo, cronologia, canone, problemi tracciati. Base migliore da adattare: apri e leggi i file di skills/ e agents/.
- Scriven (MIT): profilo della voce su 15+ dimensioni, unità atomiche in contesto pulito, RECORD.md (cosa il libro ha stabilito: fili aperti, promesse, payoff), traduzione con glossario e ritraduzione.
- asadeisa/book-translator (MIT): glossario per primo, controlli per blocco, revisore nuovo.
- APODICTIC (anotherpanacea-eng): CC BY-NC-SA 4.0, NON commerciale. Non inglobare, non copiare. Prendi solo le idee generali riscritte da zero (contratto del libro dedotto dal testo, regola "diagnostica e non riscrive", gravità Must/Should/Could-Fix) e scrivi nella scheda che serve una licenza commerciale dall'autore se si vuole di più.
- Book-pipeline (knightdx91-alt): nessuna licenza vista, ricetta personale; solo idee (una sola fonte di verità, varietà strutturale). Contiene APODICTIC: non riusare quella parte.
Da studiare davvero (non ancora aperti): epicsagas/Velith, danjdewhurst/story-skills, ThomasHoussin/Claude-Book, robskidmore/fiction-skills, howells/fiction, rhavekost/author-toolkit, felipelobomotta-blip/book-genesis-studio, mrigankad/Novel-OS, ghanemzadeh/claude-skills, blader/humanizer, chi-feng/humanizer, itotm/calibre-novel-translator, darkautism/ai-novel-translation, fredchu/book-translator, deusyu/translate-book, ac1982/translate-book, DDChen666/translate-book, KazKozDev/book-translator, VoltAgent/awesome-claude-code-subagents (solo gli agenti di scrittura: ai-writing-auditor, content-quality-editor, content-editor), rohitg00/awesome-claude-code-toolkit, rshah515/claude-code-subagents. Gli agenti per codice, infrastruttura e dati non vanno nel motore. Cerca tu altri repository e valutali con la stessa scheda.
Integra davvero: aggiorna ruoli, fasi, controlli e prove con ciò che decidi di prendere e scrivi per ogni repository quali modifiche hai fatto.

=== 10. PULIZIA ===
Risolvi tutti i punti della sezione 1.2: una sola fonte per i comandi; esportazioni doppie in docs/ (sposta fuori dal ramo, verifica, poi rimuovi); voci e nomi reali nei docs del ramo motore (sposta fuori dal ramo o in repository separato, verifica, poi rimuovi); requirements; prove da lanciare sempre prima del push; modello libro.yaml con appendici; README e PROCEDURA.md corretti su hook e recinto; dati KDP: segnala ultima_verifica null come passo manuale per me, non inventare la verifica.

=== 11. PROVE ===
Aggiorna zb prove: cartella unica e file fuori dal libro, fase struttura e gate, ruoli e separazione scrittore/revisore, capsule, agenti spenti sul ramo motore, anti-IA, correttore, traduzione con i controlli meccanici. Un mini-libro inventato con autore inventato che attraversi struttura, scrittura, revisione e traduzione in inglese. Le prove devono passare.

=== 12. FILE DERIVATI ===
Aggiorna: motore/README.md, motore/PROCEDURA.md, motore/passaggio-di-consegne.md, motore/report-motore.md, docs/INFRASTRUTTURA_COMPLETA.md, docs/GUIDA_AL_SISTEMA (.md e .pdf rigenerata). Per ciascuno dichiara aggiornato sì/no.

=== 13. COMANDI MOBILE E FLUSSO DI SCRITTURA (richiesti dall'autore) ===
Implementa come comandi di Claude Code (file in .claude/commands/ del ramo del libro; verifica il formato corrente sulla documentazione ufficiale), attivi solo sui rami dei libri, ciascuno un involucro sottile sui comandi zb:
13.1 /scrivi-capitolo N. Non è una catena unica in una sola sessione. La sessione principale orchestra e non scrive prosa: (a) zb avvio e riga "Letto"; (b) PREPARAZIONE: legge la scheda del capitolo in 03-struttura/05-scaletta.md, carica dal codex SOLO le schede dei personaggi e dei luoghi marcati con i tag @char e @loc presenti nella scena, carica il Canon (fatti bloccati) e le capsule dei capitoli precedenti; controlla che la scheda abbia funzione, conflitto, cambiamento, informazione data, gancio, polarità emotiva (da cosa a cosa cambia la carica della scena) e sottotesto dei dialoghi principali, altrimenti si ferma e lo segnala; (c) chiama il subagente scrittore-voce; (d) zb esito; (e) chiama il subagente capsula; (f) aggiorna lo stato compatto; (g) commit e push con zb. Poi si ferma: la revisione è un comando separato.
13.2 /revisiona N. Chiama in sessioni/subagenti separati, nell'ordine: line-editor, correttore-italiano. Editing chirurgico: gli agenti segnalano i punti che non rispettano catalogo anti-IA e criteri del correttore e intervengono solo su quelli, con modifiche puntuali, dopo il mio ok; non riscrivono il capitolo se l'impianto regge. Il catalogo anti-IA e i criteri del correttore sono filtri di qualità, NON stanno sopra manuale del libro, voce e briefing (vedi 0.6): le scelte di stile documentate nel manuale della voce vincono.
13.3 /diagnosi N. Audit isolato in sola lettura: scrive solo il report in 06-diagnostica/, non tocca il testo.
13.4 /handover. Aggiorna passaggio-di-consegne.md (sette sezioni) e lo stato compatto, fa commit e push e mi dice di aprire una nuova chat. Un comando non può azzerare il contesto: dichiaralo nel testo del comando e non promettere un reset.
13.5 Codex del libro: schede dei personaggi e dei luoghi in libri/<slug>/02-bibbia/codex/ con tag @char e @loc; uno script le filtra per i tag della scena (zero token di ragionamento). Canon: sezione "fatti bloccati" nello stato del libro, modificabile solo con un gate. Stato compatto: 15-20 righe con ultimo capitolo salvato, stato dei personaggi, fatti bloccati, obiettivo del prossimo capitolo. Nelle nuove sessioni si legge solo lo stato compatto e la scheda del capitolo, oltre alla riga "Letto".
13.6 Diagnosi: i file originali sono già scritti in motore/editoriale/diagnosi/ (principi, contratto del libro, dieci passaggi di analisi, gravità e rapporto), con ruolo ruoli/00-diagnosta.md e agente agenti/diagnosta.md. Usali come base e collegali ai gate (struttura prima della stesura, revisione del manoscritto). NON copiare né adattare testo di APODICTIC (licenza non commerciale) e non aprirlo per scrivere questi file; se servono altri passaggi, scrivili da zero a partire dalla pratica editoriale comune e segnalamelo.
13.7 Nessun contenuto di libro dentro motore/editoriale/: il manoscritto, il codex, le schede e lo stato stanno SOLO in libri/<slug>/ del ramo del libro, mai nel motore. Scrivi in italiano, e in inglese per i libri in lingua inglese (sezione 8).
13.8 Aggiungi le prove per i comandi 13.1-13.4 su un mini-libro inventato.

=== BLOCCO DI SALVATAGGIO (dopo ogni tema e alla fine) ===
- Dove salvare: ramo motore del repository ZeusBot, mai sui rami dei libri.
- Commit piccoli e separati per tema (stato attuale, collocazione editoriale, percorso e struttura, cartella unica e controlli, agenti e capsule, anti-IA, correttore, traduzione, script, pulizia, prove, documentazione), con elenco dei file toccati.
- Push su origin dopo ogni commit; se fallisce, fermati e riporta l'errore.
- Resoconto finale: hash di ogni commit; file creati, modificati, spostati, rimossi; file derivati aggiornati sì/no; per ogni repository "letto: ..." e licenza; cosa resta a me (docs/DA_FORNIRE.md, verifica dati KDP, decisione su licenza APODICTIC); "branch allineato a origin: sì/no".
- Mai scrivere "fatto" se il lavoro non è su GitHub.

# Passaggio di sessione — Il quaderno nell'ulivo (La Banda della Gravina, 1)

Prompt da incollare in una nuova sessione di Claude Code.

---

LIBRO «Il quaderno nell'ulivo» (La Banda della Gravina, 1) — ripresa dopo il capitolo 20

CONTESTO
- Repository NGTAProtocol/ZeusBot, ramo libro/ulivo-pensante-vol1, cartella libri/ulivo-pensante-vol1/.
  Push solo su quel ramo, sempre esplicito: git push origin libro/ulivo-pensante-vol1. Nessun push forzato.
- motore/ e banca-voci (NGTAProtocol/https-github.com-banca-voci): sola lettura, nessuna modifica.
- Romanzo per ragazzi 9-12 anni, Ginosa e le gravine. Autore F.R. Faraone. 25 capitoli, circa 32.500 parole
  (1.200-1.400 a capitolo), 12 enigmi con pagina «L'enigma della banda» (cap. 2, 4, 6, 8, 9, 11, 13, 15, 17, 19,
  21, 23). Voce mistero-ed-epicita (sezioni 1, 2, 3, 7 della scheda), terza persona vicina a Pino, dialetto
  spento, dialoghi con la lineetta «—», titoli «# N — Titolo», riga <!-- zb: chiusura=X --> (sigla da scaletta).
- Il vecchio «L'Ulivo Pensante» (materiale/…docx) è solo registro dei fatti: nessuna frase o scena ripresa.

STATO (dopo il lotto B; ultimo commit: vedi git log -1, base del lotto 0c9dea7)
- Fase stesura, passo capitolo 21, nessun gate aperto (gate «lotto» non attivo). Capitoli scritti 1-20;
  approvati dal motore 1-3; 4-15 letti e corretti dall'autore; 16-20 da leggere.
- Parole (metodo unico del motore): 1 = 1.366 · 2 = 1.365 · 3 = 1.388 · 4 = 1.320 · 5 = 1.300 · 6 = 1.377 ·
  7 = 1.349 · 8 = 1.225 · 9 = 1.196 · 10 = 1.335 · 11 = 1.160 · 12 = 1.236 · 13 = 1.152 · 14 = 1.187 ·
  15 = 1.216 · 16 = 1.237 · 17 = 1.255 · 18 = 1.169 · 19 = 1.295 · 20 = 1.212. Totale 25.340 / 32.500.
- zb stato atteso: «Fase: stesura; passo: capitolo 21; gate in attesa: nessuno … Capitoli: scritti fino a 20,
  approvati fino a 3, previsti 25 … Parole: 25340/32500 … allineato a origin: sì».

DECISIONI PRESE (non rimetterle in discussione)
- Grafia del luogo reale: «Rocca Vetere» (due parole, maiuscole). Il cambio di grafia della revisione E6 era errato
  ed è stato annullato ovunque, tranne che nel registro dei fatti del vecchio testo (righe P16, L21, C6, già corrette).
- Guardiano della Terravox: è chi ha tolto la corda nel cap. 10 (che non si riscrive). Operaio della Terravox,
  di notte guardiano, di giorno vicedirettore dell'ufficio postale del paese; ha bisogno di soldi perché la figlia
  è gravemente malata (solo accenni discreti, nessun dettaglio clinico). Il gesto del cap. 10 nasce dal disagio,
  non dalla crudeltà. Nome: non deciso. Comparso una volta come presenza neutra nel cap. 19 (allo sportello,
  camicia azzurra; Checco: «Come sta la piccola?» — «Meglio, oggi»). Rivelazione: non prima del cap. 21;
  capitolo da fissare con l'autore (proposta: cap. 22, la notte delle ruspe).
- Scavi notturni: continuano sulle notti pari (4, 6, 8, 10, 12, 14, 16…), sempre tra le 2:10 e le 2:50; sabato
  18 notte le ruspe (cronologia.yaml).
- Seme della madre di Checco: nel cap. 14 ha chiesto tre volte il codice dell'allarme; nel cap. 17 in bottega il
  cartellino «Radio — mamma di Checco — pronta»; nel cap. 18 Gianni non dice come ha saputo il codice («C'è di
  mezzo una persona che non sa niente»). Il come resta aperto: non risolverlo senza decisione dell'autore.
- Enigma 10: «ULIVO» è un acrostico (prime lettere delle righe), come MICHELE nel cap. 15. Fatto nel cap. 19.
- Gianni: smascherato nei cap. 17-18 (scheda col sette tagliato, occhiali da saldatore = i due cerchi del disegno
  di Stellina); non è un cattivo da fumetto; testimonierà nel cap. 24 (scaletta).
- Pagine enigma: in fondo al capitolo, dopo il gancio (manuale § 14). Pagina a fine scena 1 quando la soluzione
  si vede nel capitolo stesso: cap. 4, 8, 9, 13, 15, 17, 19. Per i cap. 21 e 23 applicare la stessa regola.
- Nota dell'autore (libro.yaml): «Ginosa, Rocca Vetere e la Piazza dell'Orologio sono luoghi reali; i fatti che
  il romanzo vi ambienta sono invenzione. I nomi di contrada la Croce, il Pozzo Vecchio e la Capperaia sono di
  fantasia.»
- Altre decisioni attive: mappa canonica 03-architettura/mappa-di-lucia.md (D4 recinto e muro, E4 Ulivo
  Pensante, F5 curva dell'Ape, C3 chiesa rupestre); «mezzogiorno» = mezzogiorno del sole; il nonno vieta le
  uscite notturne (cap. 9) e «si fa tutto insieme» (cap. 13); il nonno dà strumenti, mai soluzioni.

DA VERIFICARE (00-progetto/registro-verifiche.md)
- (a) Piazza dell'Orologio, luogo reale: fontana, portici, bar e tre porte intorno alla torre sono invenzione;
  l'enigma 7 dipende dall'orientamento nord/est/sud.
- (b) Rocca Vetere: grafia e dettagli DA CONTROLLARE su carta a cura dell'autore (zona del muro di Rosa, «nome
  vecchio», casella D4, carta delle contrade). Compare dal cap. 21: finché non confermati, nel testo nulla di reale.
- (c) Botanica, esito del 14/10/2026 (fonti web generiche, non scientifiche; calendario del libro invariato):
  cappero maggio-ottobre (6-7-8 dentro); asfodelo marzo-metà aprile (5 un po' largo, ritocco facoltativo a 3-4);
  elicriso maggio-agosto (5-6-7 dentro); rosmarino coste ottobre-febbraio, entroterra marzo-luglio (1-4 e 10-12
  vale vicino al mare); pero selvatico fine marzo-aprile (3-4 regge); iris marzo-aprile plausibile, NON verificato.
- Ufficio postale (cap. 19): nessun dettaglio reale descritto; non aggiungerne.

AVVIO (in quest'ordine)
1. git fetch origin libro/ulivo-pensante-vol1 && git checkout libro/ulivo-pensante-vol1
2. git rev-parse --abbrev-ref @{u} deve dare origin/libro/ulivo-pensante-vol1
   (altrimenti git branch --set-upstream-to=origin/libro/ulivo-pensante-vol1).
3. Banca-voci in sola lettura: aggiungere NGTAProtocol/https-github.com-banca-voci alla sessione, clonarla in
   /home/user/https-github.com-banca-voci, export ZB_BANCA_VOCI=/home/user/https-github.com-banca-voci
4. python3 motore/zb avvio libri/ulivo-pensante-vol1 → riportare la riga «Letto: …»;
   python3 motore/zb stato libri/ulivo-pensante-vol1. zb avvio si ferma se ci sono modifiche non salvate,
   commit non spinti o documenti approvati cambiati senza zb riapprova.
5. Leggere: passaggio-di-sessione.md (questo), 03-architettura/scaletta.md (cap. 21-25), manuale-di-stile.md,
   02-bibbia/bibbia.md, piano-parole.md, enigmi.md (enigmi 11 e 12), mappa-di-lucia.md, cronologia.yaml,
   00-progetto/registro-verifiche.md, 02-bibbia/registro-fatti.md («Fatti del libro nuovo», N1-N20 e D1),
   scheda voce (python3 motore/zb voce mostra mistero-ed-epicita), capitoli 19 e 20 per il raccordo.

VINCOLI DI SCRITTURA E CONTROLLI PER CAPITOLO
- Mistero chiaro; ogni enigma risolvibile con indizi già in pagina; l'indizio decisivo non compare mai dopo la
  risposta; la soluzione non è mai spiegata prima della pagina «L'enigma della banda».
- Il nonno dà strumenti e metodo, mai soluzioni. Checco comico ma non stupido; le sue chiacchiere contengono sempre
  un'informazione vera. Paura sì, crudeltà no. Il guardiano: disagio, non cattiveria.
- Similitudini rare, mai a grappolo. Tic: «contare» ≤ 3, «tutto insieme» ≤ 1; tenere bassi «piano», «poi»,
  «a lungo», «Nessuno disse niente», «sussurrò».
- Finestra delle scosse 2:10-2:50, notti pari; date della scaletta (cap. 21-22 sabato 18, 23 domenica 19, 24
  lunedì 20, 25 sabato 25). Calendario delle fioriture di Rosa (colonne 1-6) intoccabile.
- Luoghi reali (Ginosa, Piazza dell'Orologio, Rocca Vetere): nessun dettaglio reale inventato. Croce, Pozzo
  Vecchio, Capperaia sono di fantasia. Archeologia: il muro è «antico, di grosse pietre squadrate»; solo il
  funzionario (cap. 23) dice «probabilmente di età greca, da verificare». Niente Sparta, niente date.
- «Sviluppo Territoriale Sostenibile» vietato prima del cap. 25.
- Attenzione al controllo «cifre» del motore: «sei» vicino a «quaderni» dà KO (i quaderni sono sette).
- Misure del motore: 1.000-1.600 parole (piano 1.300 ±15%), frase media 9-14, dialogo 25-45%, scene 1-2 da almeno
  500 parole, separatore «* * *». Misurare prima di lanciare zb esito: il primo KO vale come tentativo.

FLUSSO DEL MOTORE E SALVATAGGIO
- Per ogni capitolo: zb avvio, zb voce mostra mistero-ed-epicita, scrivere 04-manoscritto/NN-<slug>.md,
  python3 motore/zb esito libri/ulivo-pensante-vol1 N. Su un KO: una sola correzione mirata, poi di nuovo zb
  esito; al secondo KO ci si ferma (gate controllo_fallito).
- Correzioni a capitoli già scritti: modificare, commit, zb correggi libri/ulivo-pensante-vol1 "N: motivo"
  --commit <hash>. Documenti approvati (bibbia, scaletta, manuale, piano-parole, cronologia.yaml, libro.yaml):
  dopo il commit, zb riapprova libri/ulivo-pensante-vol1 <documento> "<motivo>". Entrambi scrivono stato.yaml:
  serve un secondo commit. zb esito riscrive LEGGIMI.md (ripristinarlo con git checkout se serve).
- Derivati: stato.yaml, piano-parole.md, enigmi.md, scaletta.md (riga «Stato»), bibbia.md, registro-fatti.md
  (N…), registro-verifiche.md, cronologia.yaml, mappa-di-lucia.md, passaggio-di-sessione.md.
- Salvataggio: git add, git status, commit, git push origin libro/ulivo-pensante-vol1, verifica con git status
  e git log. Resoconto: file, ramo, hash di ogni commit, esito del motore, parole per capitolo e totale su 32.500.

PRIMA AZIONE NELLA NUOVA SESSIONE
Dopo l'avvio e le letture, scrivere i capitoli 21-25 secondo la scaletta, uno alla volta (21 «Il lucido»,
enigma 11; 22 «La notte delle ruspe»; 23 «La lettera di Rosa», enigma 12; 24 «Il consiglio»; 25 «Il biglietto»),
senza toccare i capitoli già scritti, con zb esito, derivati e salvataggio dopo ciascuno. Prima di scrivere il
cap. 21, chiedere all'autore il capitolo di rivelazione del guardiano e la conferma dei dettagli di Rocca Vetere.

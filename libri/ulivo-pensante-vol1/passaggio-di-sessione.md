# Passaggio di sessione — Il quaderno nell'ulivo (La Banda della Gravina, 1)

Prompt da incollare in una nuova sessione di Claude Code.

---

LIBRO «Il quaderno nell'ulivo» (La Banda della Gravina, 1) — ripresa dopo il capitolo 16

CONTESTO
- Repository NGTAProtocol/ZeusBot, ramo libro/ulivo-pensante-vol1, cartella libri/ulivo-pensante-vol1/.
  Push solo su quel ramo, sempre esplicito: git push origin libro/ulivo-pensante-vol1. Nessun push forzato.
- motore/ e banca-voci (NGTAProtocol/https-github.com-banca-voci): sola lettura, nessuna modifica.
- Romanzo per ragazzi 9-12 anni, Ginosa e le gravine. Autore F.R. Faraone. 25 capitoli, circa 32.500 parole
  (1.200-1.400 a capitolo), 12 enigmi con pagina «L'enigma della banda» (cap. 2, 4, 6, 8, 9, 11, 13, 15, 17, 19,
  21, 23). Voce mistero-ed-epicita (sezioni 1, 2, 3, 7 della scheda), terza persona vicina a Pino, dialetto
  spento, dialoghi con la lineetta «—», titoli «# N — Titolo», riga <!-- zb: chiusura=X --> (sigla da scaletta).
- Il vecchio «L'Ulivo Pensante» (materiale/…docx) è solo registro dei fatti: nessuna frase o scena ripresa.

STATO (al commit COMMIT_CAP16, base 9c2da15)
- Fase stesura, passo capitolo 17, nessun gate aperto (gate «lotto» non attivo). Capitoli scritti 1-16;
  approvati dal motore 1-3; 4-16 letti e corretti dall'autore fino al 15, il 16 è da leggere.
- Parole (metodo unico del motore): 1 = 1.366 · 2 = 1.365 · 3 = 1.388 · 4 = 1.320 · 5 = 1.300 · 6 = 1.377 ·
  7 = 1.349 · 8 = 1.225 · 9 = 1.196 · 10 = 1.335 · 11 = 1.160 · 12 = 1.236 · 13 = 1.152 · 14 = 1.187 ·
  15 = 1.216 · 16 = 1.238. Totale 20.410 / 32.500.
- zb stato atteso: «Fase: stesura; passo: capitolo 17; gate in attesa: nessuno … Capitoli: scritti fino a 16,
  approvati fino a 3, previsti 25 … Parole: 20410/32500 … allineato a origin: sì».

DECISIONI PRESE (non rimetterle in discussione)
- Enigma 10 (cap. 19): «ULIVO» è un acrostico, prime lettere delle righe della poesia di Rosa (enigmi.md), come
  MICHELE nel biglietto del cap. 15; il metodo è già dato in pagina nel cap. 15. Non anticipare ULIVO.
- Guardiano della Terravox: è chi ha tolto la corda nel cap. 10 (che non si riscrive). Identità e capitolo della
  rivelazione: DA FISSARE con l'autore. Non si rivela nel cap. 16 (e non c'è). Non inventarne il nome.
- Falsa pista: nel cap. 16 Pino accusa Checco (il codice dell'allarme lo sa lui); il sospetto su Gianni cresce
  (Lucia: entrava nel laboratorio, ripara i droni; Checco: chi ha preso solo le schede sapeva del video) ma resta
  una pista da verificare. Nel cap. 17 Pino e Stellina vanno nella bottega di Gianni (scaletta).
- Occhiali da saldatore di Gianni: mai da Gianni prima del cap. 17; nel cap. 17 compaiono (i «due cerchi neri»
  del disegno di Stellina, cap. 3). Nessuna anticipazione oltre la scaletta.
- Pagine enigma: in fondo al capitolo, dopo il gancio (manuale § 14). Eccezione, pagina a fine scena 1, quando
  la scaletta mostra la soluzione nel capitolo: cap. 4, 8, 9, 13, 15 (scaletta, «Pagine enigma a metà
  capitolo»; manuale § 14). Per ogni nuovo capitolo con enigma: se la soluzione si vede nel capitolo stesso,
  pagina a fine scena 1 e soluzione nella scena 2; altrimenti pagina in fondo. Proporlo all'autore se in dubbio.
- Nota dell'autore (libro.yaml): «Ginosa, Roccavedere e la Piazza dell'Orologio sono luoghi reali; i fatti che il
  romanzo vi ambienta sono invenzione. I nomi di contrada la Croce, il Pozzo Vecchio e la Capperaia sono di
  fantasia.»
- Altre decisioni attive: mappa canonica 03-architettura/mappa-di-lucia.md; «mezzogiorno» = mezzogiorno del sole
  (verso l'una, ora legale); il nonno vieta le uscite notturne (cap. 9, registro-fatti N1); il nonno dà
  strumenti e metodo, mai soluzioni, e dopo il cap. 13 «si fa tutto insieme».

DA VERIFICARE (00-progetto/registro-verifiche.md)
- (a) Piazza dell'Orologio, luogo reale: fontana, portici, bar e tre porte intorno alla torre sono invenzione;
  l'enigma 7 dipende dall'orientamento nord/est/sud.
- (b) Roccavedere: grafia e dettagli DA CONTROLLARE su carta (posizione, «nome vecchio», carta delle contrade).
  Compare solo dal cap. 21: nessun fatto reale va affermato.
- (c) Mesi di fioritura (cappero, elicriso, asfodelo, pero selvatico, rosmarino, iris): fonte botanica.

AVVIO (in quest'ordine)
1. git fetch origin libro/ulivo-pensante-vol1 && git checkout libro/ulivo-pensante-vol1
2. git rev-parse --abbrev-ref @{u} deve dare origin/libro/ulivo-pensante-vol1
   (altrimenti git branch --set-upstream-to=origin/libro/ulivo-pensante-vol1).
3. Banca-voci in sola lettura: aggiungere NGTAProtocol/https-github.com-banca-voci alla sessione, clonarla in
   /home/user/https-github.com-banca-voci, export ZB_BANCA_VOCI=/home/user/https-github.com-banca-voci
4. python3 motore/zb avvio libri/ulivo-pensante-vol1 → riportare la riga «Letto: …»;
   python3 motore/zb stato libri/ulivo-pensante-vol1.
5. Leggere: passaggio-di-sessione.md (questo), 03-architettura/scaletta.md (cap. 17-25), 03-architettura/
   manuale-di-stile.md, 02-bibbia/bibbia.md, 03-architettura/piano-parole.md, 03-architettura/enigmi.md,
   03-architettura/mappa-di-lucia.md, cronologia.yaml, 00-progetto/registro-verifiche.md, 02-bibbia/
   registro-fatti.md (sezione «Fatti del libro nuovo»), scheda voce (python3 motore/zb voce mostra
   mistero-ed-epicita), capitoli 15 e 16 per il raccordo.

VINCOLI DI SCRITTURA E CONTROLLI PER CAPITOLO
- Mistero chiaro; ogni enigma risolvibile con indizi già in pagina; l'indizio decisivo non compare mai dopo la
  risposta; la soluzione non è mai spiegata prima della pagina «L'enigma della banda».
- Il nonno dà strumenti e metodo, mai soluzioni. Checco comico per carattere e situazione, mai stupido; le sue
  chiacchiere contengono sempre un'informazione vera. Paura sì, crudeltà no.
- Similitudini: al massimo una ogni due pagine, mai a grappolo. Tic: «contare» ≤ 3, «tutto insieme» ≤ 1; tenere
  bassi «piano», «poi», «a lungo», «Nessuno disse niente», «sussurrò».
- Finestra delle scosse: 2:10-2:50, notti alterne (4, 6, 8, 10, 12 luglio). Rispettare cronologia e date della
  scaletta (cap. 17: giovedì 16 luglio).
- Luoghi reali (Ginosa, Piazza dell'Orologio, Roccavedere): nessun dettaglio reale inventato; coerenza con le
  scene già scritte (piazza: cap. 3, 7, 13). Croce, Pozzo Vecchio, Capperaia sono di fantasia.
- Misure del motore: 1.000-1.600 parole (piano 1.300 ±15%), frase media 9-14, dialogo 25-45%, scene 1-2 da almeno
  500 parole, separatore «* * *».
- Se la scaletta non fissa qualcosa di essenziale: soluzione più sobria ed elenco «SCELTE DA CONFERMARE».

FLUSSO DEL MOTORE E SALVATAGGIO
- Per ogni capitolo: zb avvio, zb voce mostra mistero-ed-epicita, scrivere 04-manoscritto/NN-<slug>.md,
  python3 motore/zb esito libri/ulivo-pensante-vol1 N (report in 06-diagnostica/capitoli/NN.md). Su un KO: una
  sola correzione mirata, poi di nuovo zb esito; al secondo KO ci si ferma.
- Correzioni a capitoli già scritti: modificare, commit, poi zb correggi libri/ulivo-pensante-vol1
  "N: motivo" --commit <hash>. Documenti approvati (bibbia, scaletta, manuale, piano-parole, libro.yaml): dopo
  il commit, zb riapprova libri/ulivo-pensante-vol1 <documento> "<motivo>". Entrambi scrivono stato.yaml, quindi
  serve un secondo commit.
- zb esito riscrive LEGGIMI.md e le misure del piano parole (senza riapprovazione).
- Derivati da tenere allineati: stato.yaml, piano-parole.md, enigmi.md, scaletta.md, bibbia.md, registro-fatti.md
  («Fatti del libro nuovo», righe N…), registro-verifiche.md, mappa-di-lucia.md, passaggio-di-sessione.md.
- Salvataggio: git add, git status, commit con messaggio chiaro, git push origin libro/ulivo-pensante-vol1,
  verifica allineamento (git status, git log). Resoconto: file, ramo, hash di ogni commit, esito del motore,
  parole per capitolo e totale su 32.500.

PRIMA AZIONE NELLA NUOVA SESSIONE
Dopo l'avvio e le letture, scrivere il capitolo 17 («La bottega», enigma 9: oggetto fuori posto) secondo la
scaletta, senza toccare i capitoli già scritti, poi zb esito 17, derivati e salvataggio. Fermarsi per la lettura
dell'autore se non indicato diversamente.

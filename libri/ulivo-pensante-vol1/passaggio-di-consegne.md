# Passaggio di consegne — Il quaderno nell'ulivo (La Banda della Gravina, 1)

Frase di apertura per la nuova chat: «Leggi libri/ulivo-pensante-vol1/passaggio-di-consegne.md e riprendi da lì».

## Stato
- Repository `NGTAProtocol/ZeusBot`, ramo `libro/ulivo-pensante-vol1` (nato dal ramo `motore`; upstream
  corretto: `origin/libro/ulivo-pensante-vol1`).
- Fase «stesura», passo «capitolo 6», nessun gate aperto. Lotto (motore): dimensione 3, capitoli [4, 5].
- Gate «primi_capitoli» approvato dall'autore il 14/10/2026 dopo le correzioni A1-A6 (capitoli 1-3).
- Capitoli 4 e 5 scritti, controlli OK, **in attesa della lettura dell'autore** (non ancora approvati).
- Stato tecnico in `stato.yaml` (il motore usa stato.yaml, non stato.md).

| Cap. | Titolo | Parole | Frase media | Dialogo | Esito | Stato |
|---|---|---|---|---|---|---|
| 1 | L'Ape e il cartello | 1.366 | 10,1 | 30,2% | OK | approvato |
| 2 | Le piastrelle della nonna (enigma 1) | 1.365 | 10,9 | 32,4% | OK, 3 avvisi di riciclo voluti | approvato |
| 3 | La prova della gravina | 1.388 | 10,0 | 28,7% | OK | approvato |
| 4 | Il Gufo (enigma 2) | 1.339 | 10,1 | 25,8% | OK | da leggere |
| 5 | L'albero che pensa | 1.290 | 10,1 | 42,3% | OK | da leggere |

Totale: 6.748 / 32.500 parole (metodo unico del motore).

## Obiettivo del libro
Romanzo per ragazzi 9-12, avventura investigativa con enigmi, primo volume della serie «La Banda della
Gravina». Ginosa e le gravine; mistero umano risolto con i quaderni cifrati di nonna Rosa; un solo elemento
strano (l'Ulivo Pensante), spiegato senza magia; finale che apre il volume 2.

## Decisioni prese
- Titolo «Il quaderno nell'ulivo»; serie «La Banda della Gravina», numero 1.
- Voce `mistero-ed-epicita`, solo sezioni 1, 2, 3 e 7 della scheda; banca-voci in sola lettura.
- 25 capitoli da 1.200-1.400 parole (32.500 in tutto); profilo «giallo» con override motivati.
- 12 enigmi (cap. 2, 4, 6, 8, 9, 11, 13, 15, 17, 19, 21, 23), 12 tipi diversi: `03-architettura/enigmi.md`.
- Terza persona vicina a Pino; dialetto spento; dialoghi con la lineetta «—».
- Banda: Pino 11, Lucia 12, Stellina 10, Tonio 12; Checco 15 con l'Ape; il cane Ciuffo.
- Michele ex ingegnere, padre di Antonio. Intestazione dei capitoli: solo «# N — Titolo».
- Funghi del suolo: solo ipotesi di Michele. Muro «antico, di grosse pietre squadrate»; il funzionario dice
  «probabilmente di età greca, da verificare». Niente Sparta, niente date.
- 14/10 (approvate dall'autore): allarme col codice montato da Checco (cap. 2); i «due cerchi neri appesi a
  una cinghia» del disegno di Stellina sono gli occhiali da saldatore di Gianni — mai a casa o in bottega di
  Gianni prima del cap. 12, poi dove serve (cap. 17).
- 14/10 (correzioni A1-A6): mappa canonica `03-architettura/mappa-di-lucia.md` (A-F × 1-6, nord in alto);
  «mezzogiorno» = mezzogiorno del sole, d'estate verso l'una (ora legale); il cap. 2 finisce senza la parola
  (il nonno conta e si ferma), SETTE all'inizio del cap. 3; pagina enigma 1 con la tavola delle 14 piastrelle;
  tic: «contare» al massimo 3 volte per capitolo, «poi» e «senza dire niente» con parsimonia.

## Indizi già seminati (per i capitoli successivi)
- Cap. 1: le 14 piastrelle (elicriso descritto), Gianni in piazza lunedì mattina, toppa a V vista solo da
  Pino, due furgoni bianchi Terravox, tre ruote dell'Ape, la curva dove si pianta (F5).
- Cap. 2: allarme col codice (Checco lo conosce → cap. 16); «Rosa portava i quaderni al bar, in piazza, dal
  fornaio»: mezzo paese sapeva dei quaderni.
- Cap. 3: SETTE; sole a est / ovest; ombra a nord a mezzogiorno del sole; Capperaia (C2) e terrazza di Franco
  (A2); carrubo, grotta; paura di Tonio delle grotte; disegno di Stellina («domenica, ore 23», due cerchi neri).
- Cap. 4: tastierino dell'allarme; foglio di Rosa col percorso (in chiaro); mappa di Lucia ricopiata dalla carta
  delle contrade del forno (proposta); Franco con binocolo grosso che gli pende fino alla pancia (nel disegno i
  cerchi sono sul petto: Stellina se ne accorge e tace) e lampada rossa sulla terrazza (→ enigma 6, Carmela).
- Cap. 5: sette tagliato in verde (scatoletta 17), Stellina lo disegna; grafico (ore in basso, scosse in alto),
  scosse tra le 2 e le 3, «non tutte le notti» (→ enigma 4); «l'albero che pensa» (→ enigma 10); tronco cavo,
  Rosa ci si sedeva a scrivere (→ cap. 20); Franco andava in gravina con Rosa (→ cap. 11).

## Stato dei documenti
| Documento | Stato |
|---|---|
| `02-bibbia/bibbia.md` | approvato (riapprovato il 14/10 dopo le correzioni al gate primi_capitoli) |
| `03-architettura/manuale-di-stile.md` | approvato (riapprovato il 14/10, sezione 20 nuova) |
| `03-architettura/scaletta.md` | approvato (riapprovato il 14/10: righe dei cap. 2 e 3) |
| `03-architettura/enigmi.md` | approvato dall'autore; aggiornato il 14/10 (enigmi 1, 2, 7, 11) |
| `03-architettura/mappa-di-lucia.md` | nuovo il 14/10 (correzione A3), da confermare con la lettura |
| `05-revisioni/pagina-campione.md` | approvato (gate pagina_campione) |
| `03-architettura/piano-parole.md`, `cronologia.yaml`, `libro.yaml` | approvati; piano parole aggiornato dal motore con le misure |
| `02-bibbia/registro-fatti.md` | da confermare con Felice, riga per riga |

## Regole da non violare
- Push solo su `libro/ulivo-pensante-vol1`, sempre esplicito: `git push origin libro/ulivo-pensante-vol1`.
- Nessun push su `motore`, `mister-provino` o altri rami; nessuna modifica a `motore/` né alla banca-voci.
- Nessun push forzato. Conteggio parole solo col motore. Vecchio testo: solo registro dei fatti.
- Proponi → l'autore approva → applica; mai approvare da solo. Report di passaggio ogni 5 scambi.
- Una sola correzione mirata per KO, poi di nuovo `zb esito`; al secondo KO ci si ferma (gate controllo_fallito).

## Fatto in questa sessione (14/10/2026)
- Capitoli 1-3 scritti; gate «primi_capitoli» aperto dal motore dopo il 3.
- Correzioni A1-A6 dell'autore registrate con `zb correggi` e applicate; `zb esito` 1-3 OK; bibbia, manuale e
  scaletta riapprovati (`zb riapprova`); blocchi del gate mostrati (`zb avanti`); «ok» dell'autore (`zb ok`).
- Mappa canonica creata; enigmi 2, 7 e 11 verificati sulla mappa (dettagli in mappa-di-lucia.md).
- Capitoli 4 e 5 scritti, controlli OK.

## Punti aperti / da confermare con l'autore
1. Lettura dei capitoli 4 e 5.
2. Enigma 2: il cap. 4 mostra la banda che va alla terrazza di Franco prima della pagina enigma (la scaletta
   lo vuole); il dito di Lucia si ferma senza nominare la casella, ma all'arrivo la soluzione si capisce. Va
   bene così, o si sposta l'arrivo al cap. 5?
3. Mappa: posizioni proposte (casa delle sorelle D5, torre F3, curva dell'Ape F5, recinto D4, Ulivo E4);
   la carta delle contrade appesa nel forno di Sergio è una proposta.
4. Cap. 5: il permesso della Terravox «dalle sette alle diciannove», letto in bacheca in comune (proposta).
5. Autore in libro.yaml: «DA CONFERMARE» (nel vecchio file: Luca Ventura). Prima della fase PDF.
6. Registro dei fatti: ogni riga (P16 e C6 compresi).
7. Mesi di fioritura del calendario di Rosa (enigmi 5 e 8): da verificare con una fonte botanica.
8. Nomi di contrada inventati dell'enigma 2: Croce, Pozzo Vecchio, Capperaia.
9. Dettagli ancora «proposta» in bibbia: età degli adulti, Rosa morta tre anni prima, Gianni (50, barba
   grigia), Franco (70), Sergio padre di Tonio, Nicola, Carmela, chiesa rupestre, falco grillaio.
10. Voce: in banca-voci risulta «pronta», ma sezioni 4-6 e divieti.yaml non sono dell'autore.

## Difetti generici del motore (sessione separata «lavoro sul motore»; dettagli in report-difetti-motore.md)
1-8. Vedi report (profilo ragazzi mancante, upstream sul motore, formato di stampa, intestazione, correggi
     a più punti, dialogo solo con la lineetta, frase media al limite, nessun comando per la pagina campione).
9. Il controllo «cifre» prende «uno/una» per numeri vicino a «quaderni»; la trama vuole sei sul tavolo.
10. Gate «primi_capitoli» fisso dopo il capitolo 3.
11. Senza banca-voci `zb avvio` dà un avviso; in cloud il repository va aggiunto alla sessione prima del clone.
12. Il controllo di riciclo segnala anche le ripetizioni volute delle pagine enigma (avvisi, non KO).
13. Dopo una correzione al gate, `zb ok` richiede di rivedere tutti i blocchi con `zb avanti` (9 blocchi).

## Prossimo passo
Aspettare la lettura dell'autore dei capitoli 4 e 5 («ok» o «correggi: …»). Poi capitoli 6-10, a lotti
(il motore ha lotti da 3; l'autore può dire «lotti da N»), uno alla volta con `zb esito`, seminando gli indizi
di enigmi.md: cap. 6 enigma 3 (impronte; la banda crede a un furgone Terravox; l'Ape si rompe), cap. 7 il
Dottore in piazza, cap. 8 enigma 4 (grafico, notti alterne), cap. 9 enigma 5 (CAPPERI), cap. 10 discesa alla
chiesa rupestre (C3). Gli occhiali da saldatore non compaiono da Gianni prima del cap. 12.

Procedura per ogni capitolo: `zb avvio` (riportare la riga «Letto: …»), `zb voce mostra mistero-ed-epicita`,
rileggere briefing, manuale (sezione 20 compresa), scaletta, enigmi.md, mappa-di-lucia.md; scrivere
`04-manoscritto/NN-<slug>.md` con `# N — Titolo` e `<!-- zb: chiusura=X -->`; `zb esito <libro> N`; salvataggio.
Misure da tenere: frase media sopra 10, dialogo 28-40%, una scena se il piano dice 1 (al massimo due, ognuna
di almeno 500 parole); niente «sei» vicino a «quaderni».

## Ripartenza (sessione nuova)
1. `git fetch origin libro/ulivo-pensante-vol1 && git checkout libro/ulivo-pensante-vol1`
2. `git rev-parse --abbrev-ref @{u}` deve dare `origin/libro/ulivo-pensante-vol1` (mai il ramo motore;
   altrimenti `git branch --set-upstream-to=origin/libro/ulivo-pensante-vol1`).
3. Banca-voci in sola lettura: aggiungere `NGTAProtocol/https-github.com-banca-voci` alla sessione, clonarlo in
   `/home/user/https-github.com-banca-voci` e `export ZB_BANCA_VOCI=/home/user/https-github.com-banca-voci`.
4. `python3 motore/zb avvio libri/ulivo-pensante-vol1` (riportare «Letto: …»); `python3 motore/zb stato libri/ulivo-pensante-vol1`.
5. Leggere questo file e riprendere dal «Prossimo passo».
6. Salvataggio a ogni passo: git add, git status, commit, `git push origin libro/ulivo-pensante-vol1`,
   verifica dell'allineamento con origin, resoconto con file, ramo, hash, esito.

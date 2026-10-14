# Passaggio di consegne — Il quaderno nell'ulivo (La Banda della Gravina, 1)

> Aggiornato al cap. 16: lo stato corrente e il prompt di ripartenza sono in `passaggio-di-sessione.md`.

Frase di apertura per la nuova chat: «Leggi libri/ulivo-pensante-vol1/passaggio-di-consegne.md e riprendi da lì».

## Stato
- Repository `NGTAProtocol/ZeusBot`, ramo `libro/ulivo-pensante-vol1` (upstream `origin/libro/ulivo-pensante-vol1`).
- Fase «stesura», passo «capitolo 16», nessun gate aperto (il gate «lotto» non è attivo in libro.yaml).
- Capitoli 1-3 approvati; 4-15 scritti, controlli OK, **in attesa della lettura dell'autore**.
- Autore in libro.yaml: F.R. Faraone (D8). Stato tecnico in `stato.yaml`.

| Cap. | Titolo | Parole | Frase media | Dialogo | Esito | Stato |
|---|---|---|---|---|---|---|
| 1 | L'Ape e il cartello | 1.366 | 10,1 | 30,2% | OK | approvato |
| 2 | Le piastrelle della nonna (enigma 1) | 1.365 | 10,9 | 32,4% | OK, 3 avvisi voluti | approvato |
| 3 | La prova della gravina | 1.388 | 10,0 | 28,7% | OK | approvato |
| 4 | Il Gufo (enigma 2) | 1.320 | 10,0 | 26,8% | OK | da leggere |
| 5 | L'albero che pensa | 1.300 | 9,8 | 43,1% | OK, 1 avviso (falso positivo) | da leggere |
| 6 | Terra rossa (enigma 3) | 1.387 | 10,0 | 35,7% | OK | da leggere (D2, D6, E2) |
| 7 | Il Dottore in piazza | 1.339 | 11,2 | 39,0% | OK | da leggere (D3) |
| 8 | Il grafico della notte (enigma 4) | 1.223 | 10,8 | 31,4% | OK | da leggere (D1, E3) |
| 9 | Il calendario delle fioriture (enigma 5) | 1.182 | 11,5 | 33,4% | OK | da leggere (D1, D4) |
| 10 | Sotto i capperi | 1.328 | 10,1 | 29,2% | OK, 2 avvisi voluti | da leggere (D5) |
| 11 | Tre versioni (enigma 6) | 1.176 | 10,8 | 34,0% | OK | da leggere |
| 12 | Guardia al recinto | 1.236 | 10,2 | 32,1% | OK | da leggere |
| 13 | L'ombra della torre (enigma 7) | 1.153 | 10,4 | 34,0% | OK, 1 avviso voluto | da leggere |
| 14 | Il telefono | 1.187 | 10,2 | 36,2% | OK | da leggere |
| 15 | Il lucchetto di Rosa (enigma 8) | 1.217 | 10,4 | 29,7% | OK, 2 avvisi voluti | da leggere |

Totale: 19.167 / 32.500 parole (metodo unico del motore).

## Decisioni prese
- Titolo, serie, voce `mistero-ed-epicita` (sezioni 1-2-3-7), 25 capitoli, 12 enigmi (`enigmi.md`), terza persona
  vicina a Pino, dialetto spento, lineetta, «# N — Titolo». Mappa canonica; «mezzogiorno» del sole.
- Occhiali da saldatore di Gianni: mai da Gianni prima del cap. 12, poi cap. 17. Nei cap. 12-15 non compaiono.
- Pagine enigma a fine scena 1: cap. 4 (C1), cap. 8 e 9 (D1), cap. 13 e 15 (E1).
- E1-E8 del 14/10 (sessione senza stesura): cap. 6 tagliato a 1.387 parole su descrizioni e similitudini (indizi
  D2 intatti); cap. 8 «L'asfodelo invece, come da noi in campagna» (tolto «in primavera»); cap. 11 con due
  scene nel piano parole; vincolo del cap. 13 in scaletta (il nonno aiuta, non risolve); Rocca Vetere luogo
  reale, grafia uniformata in bibbia e scaletta, nota dell'autore che distingue luoghi reali e contrade di
  fantasia.
- D1-D9 del 14/10 applicate (dettagli nei commit 5e08933 e 0e414c3): regola delle ruote piantata nel cap. 6;
  sentiero lungo dei pastori; Checco grida in piazza dei quaderni nel laboratorio (spiegazione innocua per il
  Dottore); «oggi stesso» nel cap. 9; corda legata a un picchetto del recinto e tolta da un guardiano Terravox
  che pattuglia il ciglio (non è Gianni; si rivela più avanti); Carmela, chiesa rupestre, cancelletto
  approvati; autore F.R. Faraone; nota dell'autore sui nomi di contrada di fantasia.
- Regole dell'autore: soluzione mai spiegata prima della pagina; indizio decisivo mai dopo; il nonno dà metodo,
  mai soluzioni; Checco comico ma non stupido; paura sì, crudeltà no; similitudini rare; «contare» ≤ 3,
  «tutto insieme» ≤ 1; «piano» e «poi» sorvegliati.

## Indizi seminati nei capitoli 11-15 (per i successivi)
- Cap. 11: Franco alleato («dalla terrazza, non dal sentiero»); l'assiolo e la lampada rossa; Rosa andava da
  Franco a guardare i falchi; Rosa temeva i tombaroli, non le aziende. Tre testimonianze esatte; Pino ride alla
  battuta di Checco. Tonio ha mentito al padre sulla corda.
- Cap. 12: promessa di Pino e Tonio di dire tutto al nonno «dopo stanotte»; Stellina di vedetta (tre segnali di
  torcia); buca del cane sotto la rete; trivella, tre uomini col casco, il Dottore alle 2:04; una sagoma bassa
  coi fari spenti dietro il camion, che Pino non guarda; la vigilanza con la torcia non passa la rete.
- Cap. 13: Pino racconta tutto al nonno («da adesso si fa tutto insieme»); il nonno non va a chiedere il
  telefono; cantina della famiglia di Rosa (porta a nord), chiavi del nonno; cassetta di latta firmata, vuota da
  anni (polvere e ragnatela intatte).
- Cap. 14: Nicola (tuta Terravox) riporta il telefono senza parlare; Checco lo conosce; il nonno: «dentro ci
  lavorano anche persone come lui»; 19 foto, tre copie; il codice dell'allarme «sempre quello», Checco non l'ha
  dato a nessuno (seme del cap. 16); foto 15: furgone bianco con la toppa a V dietro il camion → Gianni; Pino
  collega anche la bugia sulla febbre (enigma 6); Checco difende Gianni («è come uno zio») e se ne va in Ape
  verso il paese (seme della falsa pista del cap. 16); Lucia chiede se era lui quello del disegno: «Non lo so».
- Cap. 15: baule verde di Rosa, 5241; biglietto MICHELE (seme dell'enigma 10); foto di Rosa davanti al muro di
  pietre squadrate, scattata da Michele; dietro solo la firma di rosmarino. Pino ripensa ai tombaroli, in
  silenzio.

## Stato dei documenti
| Documento | Stato |
|---|---|
| `02-bibbia/bibbia.md` | riapprovata il 14/10 (D1-D9; poi cantina, baule, biglietto come «proposta») |
| `03-architettura/scaletta.md` | riapprovata il 14/10 (D1, D4, D5, D6; nota sulle pagine dei cap. 13 e 15, proposta) |
| `03-architettura/manuale-di-stile.md` | riapprovato il 14/10 (eccezioni 4, 8, 9; 13 e 15 proposta) |
| `libro.yaml` | riapprovato il 14/10 (autore, nota dell'autore) |
| `03-architettura/piano-parole.md` | misure aggiornate dal motore |
| `03-architettura/enigmi.md`, `mappa-di-lucia.md` | aggiornati |
| `00-progetto/report-difetti-motore.md` | punti 19-20 nuovi |
| `02-bibbia/registro-fatti.md` | da confermare con l'autore, riga per riga |

## Regole da non violare
- Push solo su `libro/ulivo-pensante-vol1`, sempre esplicito. Nessuna modifica a `motore/` né alla banca-voci.
- Nessun push forzato. Conteggio parole solo col motore. Vecchio testo: solo registro dei fatti.
- Proponi → l'autore approva → applica; mai approvare da solo. Una sola correzione mirata per KO.
- Se una scelta non è coperta dalle istruzioni: fermarsi e riportarla.

## Fatto in questa sessione (14/10/2026)
- D1-D9 applicate ai cap. 6-10, `zb esito` 6-10 OK, `zb correggi` 6, 7, 10, `zb riapprova` di bibbia, scaletta,
  manuale, libro.yaml.
- Capitoli 11-15 scritti uno alla volta (zb avvio, zb voce mostra, zb esito, commit e push per ognuno).

## Correzioni S1-S14 (14/10/2026, dopo la lettura dei cap. 6-15)
- Applicate le sostituzioni S1-S14 nei cap. 6, 7, 8, 9, 10, 11, 13, 15; nessun'altra modifica al testo.
- Parole dopo le correzioni: 6 = 1.377, 7 = 1.349, 8 = 1.225, 9 = 1.196, 10 = 1.335, 11 = 1.160, 13 = 1.152,
  15 = 1.216. Totale 1-15: 19.172 / 32.500.
- Nuovo `00-progetto/registro-verifiche.md` (Piazza dell'Orologio, Rocca Vetere, mesi di fioritura).
- Registro dei fatti: nuova sezione «Fatti del libro nuovo», riga N1 (cap. 9, divieto di uscite notturne).

## Punti aperti / da confermare con l'autore
1. Lettura dei capitoli 6-15.
2. Punti botanici: vedi `00-progetto/registro-verifiche.md`, punto (c) (elenco unico).
3. Rocca Vetere (E6): nel libro non compare ancora in nessun capitolo scritto (1-15). Dettagli attribuiti al luogo,
   tutti da confermare: bibbia, «zona del muro scoperto da Rosa» (invenzione narrativa), «nome vecchio della
   zona», presente sulla carta delle contrade, collocato nella casella D4 dentro il recinto Terravox (scaletta,
   cap. 21). Non verificati: posizione reale rispetto alla gravina e al paese, aspetto, storia, abitanti. Il
   registro dei fatti (P16, L21, C6) riporta il vecchio testo con la grafia «Rocca Vetere»: lasciato com'è,
   perché registra il vecchio testo (C6 parla di coloni spartani: già escluso dalla bibbia).
4. Guardiano della Terravox (D5): la scaletta non fissa il capitolo della rivelazione. Opzioni (non prima del
   cap. 16): (a) cap. 18, quando Gianni confessa e racconta come lavora la Terravox di notte, il guardiano è
   l'uomo che fa i giri sul ciglio e ha tolto la corda «come roba del cantiere»; (b) cap. 22, la notte delle
   ruspe: il guardiano è sul ciglio, riconosce i ragazzi del fondo e, a disagio come Nicola, non li ferma.
5. Registro dei fatti, dettagli «proposta» in bibbia, sezioni 4-6 della voce: ancora aperti.

## Prossimo passo
Aspettare la lettura dell'autore dei capitoli 6-15 («ok» o «correggi: …»). Poi capitoli 16-20: cap. 16 il codice
(falsa pista su Checco, la banda si spacca), cap. 17 la bottega (enigma 9; occhiali da saldatore di Gianni qui),
cap. 18 il perché di Gianni, cap. 19 l'Ape torna (enigma 10, ULIVO), cap. 20 dentro l'ulivo. Il guardiano D5: scelta dell'autore
tra le opzioni del punto 4.

## Ripartenza (sessione nuova)
1. `git fetch origin libro/ulivo-pensante-vol1 && git checkout libro/ulivo-pensante-vol1`
2. `git rev-parse --abbrev-ref @{u}` deve dare `origin/libro/ulivo-pensante-vol1`.
3. Banca-voci in sola lettura: aggiungere `NGTAProtocol/https-github.com-banca-voci` alla sessione, clonarlo in
   `/home/user/https-github.com-banca-voci` e `export ZB_BANCA_VOCI=/home/user/https-github.com-banca-voci`.
4. `python3 motore/zb avvio libri/ulivo-pensante-vol1` (riportare «Letto: …»); `python3 motore/zb stato libri/ulivo-pensante-vol1`.
5. Leggere questo file e riprendere dal «Prossimo passo».
6. Salvataggio a ogni passo: git add, git status, commit, `git push origin libro/ulivo-pensante-vol1`, verifica
   dell'allineamento con origin, resoconto con file, ramo, hash, esito.

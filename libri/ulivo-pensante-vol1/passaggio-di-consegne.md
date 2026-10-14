# Passaggio di consegne — Il quaderno nell'ulivo (La Banda della Gravina, 1)

Frase di apertura per la nuova chat: «Leggi libri/ulivo-pensante-vol1/passaggio-di-consegne.md e riprendi da lì».

## Stato
- Repository `NGTAProtocol/ZeusBot`, ramo `libro/ulivo-pensante-vol1` (nato dal ramo `motore`).
- Fase «stesura»: documenti e pagina campione approvati dall'autore il 14/10/2026. Nessun capitolo scritto.
- Parole: 0/32.500. Stato tecnico in `stato.yaml` (il motore usa stato.yaml, non stato.md).

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

## Stato dei documenti
| Documento | Stato |
|---|---|
| `02-bibbia/bibbia.md` | approvato (riapprovato dopo le correzioni) |
| `03-architettura/manuale-di-stile.md` | approvato (riapprovato dopo le correzioni) |
| `03-architettura/scaletta.md` | approvato (riapprovato dopo le correzioni) |
| `03-architettura/enigmi.md` | approvato dall'autore (non registrato dal motore: non è un documento del gate) |
| `05-revisioni/pagina-campione.md` | approvato (gate pagina_campione) |
| `03-architettura/piano-parole.md`, `cronologia.yaml`, `libro.yaml` | approvati (gate documenti) |
| `02-bibbia/registro-fatti.md` | da confermare con Felice, riga per riga |

## Da confermare con Felice
1. Autore in libro.yaml: «DA CONFERMARE» (nel vecchio file: Luca Ventura). Prima della fase PDF.
2. Registro dei fatti: ogni riga (P16 e C6 compresi).
3. Mesi di fioritura del calendario di Rosa (enigmi 5 e 8): da verificare con una fonte botanica.
4. Nomi di contrada inventati dell'enigma 2: Croce, Pozzo Vecchio, Capperaia.
5. Dettagli ancora «proposta» in bibbia: età degli adulti, Rosa morta tre anni prima, sette quaderni, Gianni
   (50, barba grigia), Franco (70), Sergio padre di Tonio, Nicola, Carmela, chiesa rupestre, falco grillaio.
6. Voce: in banca-voci risulta «pronta», ma sezioni 4-6 e divieti.yaml non sono dell'autore.

## Difetti generici del motore (sessione separata «lavoro sul motore»; da report-difetti-motore.md)
1. Manca un profilo «ragazzi 9-12»: usato «giallo» con override.
2. Ramo creato con `git checkout -b … origin/motore`: upstream su `motore`, un `git push` nudo finirebbe lì.
3. Formato di stampa predefinito (EB Garamond 11,5): non adatto ai ragazzi; da decidere alla fase PDF.
4. Intestazione del capitolo predefinita con luogo e data: risolta nel libro, nessuna modifica al motore.
5. `zb correggi` registra una correzione con più punti come una sola istruzione.
6. La misura del dialogo non riconosce le virgolette «»: conta solo le righe con la lineetta.
7. Frase media del profilo giallo (9-14) al limite per i 9-12 anni; override possibile solo con l'autore.
8. Nessun comando per i controlli della pagina campione (usate le funzioni di stile.py da fuori).

## Regole da non violare
- Push solo su `libro/ulivo-pensante-vol1`, sempre esplicito: `git push origin libro/ulivo-pensante-vol1`.
- Nessun push su `motore`, `mister-provino` o altri rami; nessuna modifica a `motore/` né alla banca-voci.
- Nessun push forzato. Conteggio parole solo col motore. Vecchio testo: solo registro dei fatti.
- Proponi → l'autore approva → applica. Report di passaggio ogni 5 scambi.

## Fatto in questa sessione
- Libro creato con `zb nuovo`; materiale, ricerca di mercato, registro dei fatti.
- Bibbia, manuale, scaletta, piano parole, cronologia, enigmi; gate documenti approvato con correzioni.
- Pagina campione scritta, corretta e approvata (383 parole, frase media 9,1, dialogo 25,8%, nessun KO).

## Prossimo passo
Scrivere i capitoli 1-5, uno alla volta, con i controlli del motore; fermarsi dopo il 5 per la lettura
dell'autore. Per ogni capitolo: `zb avvio` (riportare la riga «Letto: …»), `zb voce mostra
mistero-ed-epicita`, rileggere briefing, manuale, scaletta, enigmi.md (indizi da seminare); scrivere
`04-manoscritto/NN-<slug>.md` con `# N — Titolo` e `<!-- zb: chiusura=X -->`; `zb esito <libro> N`; salvataggio.
Il cap. 1 parte dalla pagina campione approvata.

## Ripartenza (sessione nuova)
1. Repository `NGTAProtocol/ZeusBot`, ramo `libro/ulivo-pensante-vol1`:
   `git fetch origin libro/ulivo-pensante-vol1 && git checkout libro/ulivo-pensante-vol1`
2. Controllare che l'upstream NON sia il ramo motore: `git rev-parse --abbrev-ref @{u}` deve dare
   `origin/libro/ulivo-pensante-vol1` (altrimenti `git branch --unset-upstream`).
3. Banca-voci in sola lettura: clonare `NGTAProtocol/https-github.com-banca-voci` in
   `/home/user/https-github.com-banca-voci` e `export ZB_BANCA_VOCI=/home/user/https-github.com-banca-voci`.
4. `python3 motore/zb avvio libri/ulivo-pensante-vol1` (riportare «Letto: …»); `python3 motore/zb stato libri/ulivo-pensante-vol1`.
5. Push sempre esplicito: `git push origin libro/ulivo-pensante-vol1`.

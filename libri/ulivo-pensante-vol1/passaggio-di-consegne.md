# Passaggio di consegne — La Banda della Gravina, vol. 1

Frase di apertura per la nuova chat: «Leggi libri/ulivo-pensante-vol1/passaggio-di-consegne.md e riprendi da lì».

## Stato
- Repository NGTAProtocol/ZeusBot, ramo `libro/ulivo-pensante-vol1` (creato da `motore`), allineato a origin.
- Fase «documenti». Passi 1-3 del prompt di avvio fatti; si aspetta l'autore su: documenti, titolo, pagina di prova.
- Parole del manoscritto: 0/32.500 (nessun capitolo scritto).
- Banca-voci: `/home/user/https-github.com-banca-voci` (sola lettura), `ZB_BANCA_VOCI` impostata in `~/.bashrc`.

## Decisioni prese
- Libro in ZeusBot, ramo di libro dal ramo `motore` (scelta dell'autore, opzione 1). Niente casa-editrice.
- Profilo «giallo» con override motivati (manca un profilo ragazzi 9-12).
- Voce `mistero-ed-epicita`, ambientazione «altro»; usate solo le sezioni 1-3 e 7.
- Hook del motore attivi sul ramo (`.claude/settings.json`, commit b55ef4f).

## Regole da non violare
- Nessun push su `motore`, `mister-provino` o altri rami; nessun push su banca-voci; nessun push forzato.
- Niente contenuto del libro in `motore/`; banca-voci in sola lettura.
- Nessun capitolo prima dell'«ok» dell'autore.
- Conteggio parole solo col metodo del motore.
- Vecchio testo: solo registro dei fatti; non si giudica e non si riusa.

## Fatto in questa sessione
- Passo 1: `zb nuovo`, materiale (docx), ricerca di mercato, registro dei fatti (commit ba3e0ee).
- Passo 2: bibbia, manuale di stile, scaletta (25 capitoli, 12 enigmi), piano parole, cronologia (commit f85c4db).
- Passo 3: tre titoli e pagina di prova (`00-progetto/titoli-e-pagina-di-prova.md`).
- Report per l'autore: `00-progetto/report-difetti-motore.md`.

## Punti aperti (per Felice)
1. Autore in libro.yaml: «DA CONFERMARE» (nel vecchio file: Luca Ventura). Da fissare prima del PDF.
2. Titolo: scegliere tra le tre proposte.
3. Voce: in banca-voci risulta «pronta», con sezioni 4-6 e divieti.yaml non scritti dall'autore.
4. Banda: quattro ragazzi più Checco (Mimmo tolto); mascotte Ciuffo; età proposte.
5. Anno 2026 e date della scaletta; rivelazione archeologica (dettagli di Rocca Vetere).
6. Registro dei fatti: ogni riga da confermare.

## Prossimo passo
L'autore risponde. Con «ok» ai documenti: `zb ok`, poi fase «pagina_campione».

## Ripartenza
`export ZB_BANCA_VOCI=/home/user/https-github.com-banca-voci`
`python3 motore/zb avvio libri/ulivo-pensante-vol1`
`python3 motore/zb stato libri/ulivo-pensante-vol1`

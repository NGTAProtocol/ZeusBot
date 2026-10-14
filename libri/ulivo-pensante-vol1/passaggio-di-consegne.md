# Passaggio di consegne — Il quaderno nell'ulivo (La Banda della Gravina, 1)

Frase di apertura per la nuova chat: «Leggi libri/ulivo-pensante-vol1/passaggio-di-consegne.md e riprendi da lì».

## Stato
- Repository NGTAProtocol/ZeusBot, ramo `libro/ulivo-pensante-vol1` (creato da `motore`), allineato a origin.
- Fase «pagina_campione», gate aperto: si aspetta l'«ok» dell'autore su `05-revisioni/pagina-campione.md`.
- Gate «documenti» approvato il 14/10/2026 con 7 correzioni (commit 422702a, ok 4392136).
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
- Correzioni dell'autore, `03-architettura/enigmi.md` (12 enigmi), gate documenti approvato.
- Pagina campione `05-revisioni/pagina-campione.md` (337 parole, frase media 9,1, dialogo 27,6%); gate aperto.
- Report per l'autore: `00-progetto/report-difetti-motore.md`.

## Punti aperti (per Felice)
1. Autore in libro.yaml: «DA CONFERMARE» (nel vecchio file: Luca Ventura). Da fissare prima del PDF.
2. Dialoghi: lineetta «—» (misurata dal motore) o caporali «» (il motore darebbe dialogo 0% = KO)?
3. Voce: in banca-voci risulta «pronta», con sezioni 4-6 e divieti.yaml non scritti dall'autore; si usano 1-3 e 7.
4. Mesi di fioritura del calendario di Rosa (enigmi 5 e 8) da verificare con una fonte botanica.
5. Registro dei fatti: ogni riga da confermare (P16 e C6 compresi).
6. Nomi di contrada inventati per l'enigma 2 (Croce, Pozzo Vecchio, Capperaia): da confermare.

## Prossimo passo
Con «ok» alla pagina campione: `zb avanti` (blocco 1), `zb ok`; poi capitoli 1-5 uno alla volta
(`zb avvio`, `zb voce mostra mistero-ed-epicita`, scrittura, `zb esito N`, salvataggio), stop dopo il 5.

## Ripartenza
`export ZB_BANCA_VOCI=/home/user/https-github.com-banca-voci`
`python3 motore/zb avvio libri/ulivo-pensante-vol1`
`python3 motore/zb stato libri/ulivo-pensante-vol1`

# Passaggio di consegne: motore

Frase di apertura per la nuova chat: «Leggi motore/passaggio-di-consegne.md e riprendi da lì».

## Stato

- Ramo `motore` (unico ramo di lavoro), allineato a origin. Ultimo commit: quello di questo file (`git log -1`).
- Suite: **429/429 OK**, 0 saltate, 0 KO, con LanguageTool. Comando:
  `ZB_LANGUAGETOOL=<cartella>/lib python3 -B motore/zb prove`, dalla radice del repository.
- Ramo `archivio/ghimoney` su origin (572f40f): contiene `ghimoney/`, tolto dal motore.
- Dettagli completi: `motore/report-motore.md`.

## Fatto in questa sessione (commit sul ramo motore)

| Commit | Cosa |
|---|---|
| 3a01e42 | LanguageTool attivo; skip esplicito «LanguageTool assente»; README «Ambiente» |
| 48d0a22 | prove PDF senza sha256: prova strutturale, margini ±0,005 e minimi KDP |
| f27082e | formato esatto delle pagine (Chromium arrotondava l'A5) |
| 57f262e | via i riferimenti testuali ai libri reali (frasi di prova inventate, sezioni rinominate) |
| 572f40f | prova del bleed (+5 prove) e numeri di pagina sul trim |
| ea464c7 | `ghimoney/` rimosso, dopo la verifica dell'archivio (80 file, sha256 identici) |
| ultimo | report-motore.md e questo file |

## Ambiente (container nuovo)

`pip install pymupdf markdown` · `apt-get install hunspell hunspell-it` · LanguageTool 6.8 da Maven
Central fuori dal repository e `ZB_LANGUAGETOOL` (README, «LanguageTool»). Java, Maven, Node,
Playwright, Chromium e poppler sono già presenti.

## Regole da non violare

- Nel repository del motore solo il motore: codice, configurazione, dati KDP, mini-libri inventati
  con autori inventati. Nessun manoscritto reale.
- Nessun nome reale (autori, titoli, personaggi, luoghi, frasi, nomi di ramo dei libri) in codice,
  prove, commenti, esiti e report. L'Author si confronta sempre con `libro.yaml`.
- Non toccare i libri reali né il loro `libro.yaml`. Niente impagina, pdf, kdp o pacchetto sui libri
  reali senza richiesta esplicita dell'autore.
- Nessun push forzato, nessuna riscrittura della storia.
- Tolleranza sui margini ±0,005″: non si allarga senza l'autore. Sotto i minimi KDP la prova fallisce sempre.
- KDP è il criterio: minimi da `dati/kdp.yaml`, mai scritti a mano.
- Se un test cambia esito dopo una modifica ai dati di prova, si corregge il dato, non il test.
- Salvataggio: un commit per blocco, `python3 -B motore/zb push`, `git status -sb`, `git log -1`.
  Se il push fallisce, fermarsi e riportare l'errore. Resoconto con hash, file e «branch allineato a
  origin: sì/no». Righe finali dei commit: Co-Authored-By e Claude-Session della sessione corrente.

## Decisioni aperte (dell'autore)

1. Verifica dei dati KDP sulle pagine ufficiali (`ultima_verifica: null`).
2. Scrivere TrimBox e BleedBox nel PDF? Controllare trasparenze e immagini?
3. `dati/nomi_vietati.txt` vuoto: come far controllare i nomi reali a `separazione.py` senza scriverli
   nel repository (per esempio una lista esterna letta da una variabile d'ambiente).
4. Rigenerare i PDF dei libri A5 già impaginati: solo su richiesta.
5. Script d'avvio della sessione per installare le dipendenze in un container nuovo.

## Prossimi passi possibili

- Prove sulle fasce del margine interno oltre la prima (un mini-libro sintetico oltre le 150 pagine).
- Hook in modalità blocco, dopo l'«ok» dell'autore e la prova dei 14 scenari.
- Unire il motore ai rami dei libri, se l'autore lo chiede (merge, mai rebase).

# Passaggio di consegne: motore

Frase di apertura per la nuova chat: «Leggi motore/passaggio-di-consegne.md e riprendi da lì».

## Stato

- Ramo `motore` (unico ramo di lavoro), allineato a origin. Ultimo commit: quello di questo file (`git log -1`).
- Suite: **454/454 OK**, 0 saltate, 0 KO, con LanguageTool e `ZB_BANCA_VOCI`. Comando:
  `ZB_LANGUAGETOOL=<cartella>/lib ZB_BANCA_VOCI=<banca-voci> python3 -B motore/zb prove`, dalla radice del repository.
- Banca-voci (repository separato, fuori dal motore): oggi in `/home/user/banca-voci` (commit eba0658, ramo
  `main`), senza remote (creazione rifiutata: 404 sull'organizzazione, 403 sull'account); copia in git bundle
  nello scratchpad della sessione, `banca-voci-bundle/banca-voci.bundle`. Il container è effimero: il bundle va
  salvato altrove, oppure serve un repository privato creato dall'autore (poi `git remote add` e push).
- Ramo `archivio/ghimoney` su origin (572f40f): contiene `ghimoney/`, tolto dal motore.
- Dettagli completi: `motore/report-motore.md`.

## Fatto nell'ultima sessione (commit sul ramo motore)

| Commit | Cosa |
|---|---|
| fd404a8 | `voce.py`, `zb voce`, `ZB_BANCA_VOCI`, blocco `voce` in libro.yaml, «Letto» con la voce, divieti in `stile.py`, CLAUDE.md |
| 783216e | `modelli/briefing.md`: storia, schede dei personaggi, luoghi, regole, voce |
| e619bcf | prove della sezione «voce» (+25), mini-banca inventata |
| ultimo | report, questo file, `prove/esiti/voce.md` |

Banca-voci: README, `indice.yaml`, `modelli/scheda-vuota.md`, una sola voce pronta (scheda in 7 sezioni
con il prompt originale integrale, `divieti.yaml` con 60 voci, 5 pagine-modello originali).

## Sessione precedente (commit sul ramo motore)

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
Playwright, Chromium e poppler sono già presenti. Per le voci: `export ZB_BANCA_VOCI=<banca-voci>` (README,
«Banca-voci»); la banca va ripristinata dal suo remote o dal bundle (`git clone <bundle> banca-voci`).

## Regole da non violare

- Nel repository del motore solo il motore: codice, configurazione, dati KDP, mini-libri inventati
  con autori inventati. Nessun manoscritto reale.
- Nessun nome reale (autori, titoli, personaggi, luoghi, frasi, nomi di ramo dei libri) in codice,
  prove, commenti, esiti e report. L'Author si confronta sempre con `libro.yaml`.
- Voci reali, pagine-modello e brani veri dei manoscritti solo nella banca-voci, mai nel motore.
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
6. Repository privato per la banca-voci (da creare a mano: la sessione non ha il permesso).
7. Nell'esempio del briefing, il biondo: capelli o capo d'abbigliamento? (segnato «DA CONFERMARE»).

## Prossimi passi possibili

- Banca-voci: aggiungere le altre quattro voci previste (elenco nel README della banca) con i capitoli veri,
  solo nella banca (copiare `modelli/scheda-vuota.md`, stato `da_completare` finché non verifica).
- Prove sulle fasce del margine interno oltre la prima (un mini-libro sintetico oltre le 150 pagine).
- Hook in modalità blocco, dopo l'«ok» dell'autore e la prova dei 14 scenari.
- Unire il motore ai rami dei libri, se l'autore lo chiede (merge, mai rebase).

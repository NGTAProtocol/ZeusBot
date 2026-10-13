# Passaggio di consegne: motore

Frase di apertura per la nuova chat: «Leggi motore/passaggio-di-consegne.md e riprendi da lì».

## Stato

- Ramo `motore` (unico ramo di lavoro), allineato a origin. Ultimo commit: quello di questo file (`git log -1`).
- Suite: **454/454 OK**, 0 saltate, 0 KO, con LanguageTool e `ZB_BANCA_VOCI`. Comando:
  `ZB_LANGUAGETOOL=<cartella>/lib ZB_BANCA_VOCI=<banca-voci> python3 -B motore/zb prove`, dalla radice del repository.
- Banca-voci (repository separato, fuori dal motore, solo schede di voce e divieti): oggi in
  `/home/user/banca-voci` (ramo `main`, HEAD 896e7f4 «aggiunte cartelle materiali…», sopra a22b018),
  senza remote (creazione rifiutata: 404 sull'organizzazione, 403 sull'account). Unica copia fuori dal
  container: il bundle `banca-voci.bundle` (sha256 `a5d3ad1d…7e7992bffe`) mandato all'autore come file.
  Il container è effimero: serve quel bundle oppure un repository privato creato dall'autore (poi
  `git remote add` e push).
- Ramo `archivio/ghimoney` su origin (572f40f): contiene `ghimoney/`, tolto dal motore.
- Dettagli completi: `motore/report-motore.md`.

## Fatto nell'ultima sessione: ripristino della banca-voci

| Dove | Commit | Cosa |
|---|---|---|
| banca-voci | 896e7f4 | `voci/<slug>/materiali/LEGGIMI.md` per le due voci (sopra a22b018) |
| motore | ultimo | questo file (ripartenza con `ZB_BANCA_VOCI`), `prove/esiti/banca-voci-ripristino.md` |

Banca ripristinata dal bundle dell'autore (sha256 controllato); nuovo bundle mandato all'autore.
`zb voce` esisteva già: nessuna modifica al codice. Suite 454/454 OK.

## Sessione precedente: solo schede (commit sul ramo motore)

| Commit | Cosa |
|---|---|
| 78b9963 | `zb voce verifica` non richiede più pagine d'esempio; mini-banca di prova senza esempi; prova «un solo esempio» sostituita da «scheda assente» |
| c49842a | report, questo file, `prove/esiti/voce-solo-schede.md` |
| 8f268c7 | hash in questo file |
| d4b4833 | sezione «Ripartenza» |

Banca-voci: rimosse le pagine d'esempio; due voci pronte, ciascuna con `scheda.md` e `divieti.yaml`.
Il contenuto dei libri lo decide l'autore nel briefing.

## Sessione precedente: voci narrative (commit sul ramo motore)

| Commit | Cosa |
|---|---|
| fd404a8 | `voce.py`, `zb voce`, `ZB_BANCA_VOCI`, blocco `voce` in libro.yaml, «Letto» con la voce, divieti in `stile.py`, CLAUDE.md |
| 783216e | `modelli/briefing.md`: storia, schede dei personaggi, luoghi, regole, voce |
| e619bcf | prove della sezione «voce» (+25), mini-banca inventata |
| 80d7f46 | report, questo file, `prove/esiti/voce.md` |

## Sessioni precedenti (commit sul ramo motore)

| Commit | Cosa |
|---|---|
| 3a01e42 | LanguageTool attivo; skip esplicito «LanguageTool assente»; README «Ambiente» |
| 48d0a22 | prove PDF senza sha256: prova strutturale, margini ±0,005 e minimi KDP |
| f27082e | formato esatto delle pagine (Chromium arrotondava l'A5) |
| 57f262e | via i riferimenti testuali ai libri reali (frasi di prova inventate, sezioni rinominate) |
| 572f40f | prova del bleed (+5 prove) e numeri di pagina sul trim |
| ea464c7 | `ghimoney/` rimosso, dopo la verifica dell'archivio (80 file, sha256 identici) |
| b36a438 | report-motore.md e questo file |

## Ripartenza in una chat nuova (passi concreti)

1. **Ramo.** La sessione può partire su un ramo diverso (per esempio `ccr-…`). Se l'autore indica il ramo
   `motore`: `git fetch origin motore && git checkout -b motore origin/motore` (o `git checkout motore`).
   Controllo: `git log -1` deve dare l'ultimo commit di questo file.
2. **Dipendenze** (circa 2 minuti, LanguageTool in background):
   `pip install pymupdf markdown` · `apt-get install -y hunspell hunspell-it` · nello scratchpad un
   `pom.xml` con `org.languagetool:languagetool-commandline` e `org.languagetool:language-it` 6.8, poi
   `mvn -q -B dependency:copy-dependencies -DoutputDirectory=lib` (143 file) ed
   `export ZB_LANGUAGETOOL=<scratchpad>/lt/lib`.
3. **Banca-voci.** In un container nuovo `/home/user/banca-voci` non c'è più. Chiedere all'autore il bundle
   (ultimo mandato: HEAD 896e7f4, sha256 `a5d3ad1d…7e7992bffe`) o l'URL del repository privato, poi:
   ```
   git clone <bundle o URL> /home/user/banca-voci
   export ZB_BANCA_VOCI=/home/user/banca-voci
   ```
   Controllo: `zb voce lista` (2 voci pronte), `zb voce verifica <slug>` per ciascuna (`script/voce.py`).
   Senza la banca la suite passa lo stesso: le prove «voce» usano la mini-banca di `prove/banca-voci-prova/`.
4. **Suite** (circa 10 minuti: lanciarla in background):
   `ZB_LANGUAGETOOL=… ZB_BANCA_VOCI=… python3 -B motore/zb prove` → atteso 454/454 OK.
   Per provare una sola sezione: importare `script/prove.py` e chiamare la funzione con
   `comune.leggi_yaml('prove/attesi.yaml')[<chiave>]`, poi cancellare `prove.TMP`.
5. **Remote della banca.** `create_repository` (GitHub) è rifiutato: 404 sull'organizzazione, 403
   sull'account. Non riprovare senza un cambiamento dei permessi: serve un repository creato dall'autore.

### Come funzionano le voci (in breve)

- `zb voce lista | mostra <slug> [N] | verifica <slug>` (`script/voce.py`); verifica = voce
  nell'indice, scheda con 7 sezioni «## N. Titolo» e campo «ambientazione:» nella 7, `divieti.yaml`
  leggibile, stato `pronta`. Nessuna pagina d'esempio richiesta.
- `libro.yaml` → `voce: {slug, ambientazione}` (facoltativo); `zb nuovo` lo scrive dai campi del briefing
  «Voce dalla banca:» e «Ambientazione:».
- `zb avvio`: con la voce, «Letto» include `00-progetto/briefing.md` e «scheda della voce <slug>»;
  banca assente o voce non verificata = AVVISO, mai fermo.
- `stile.py`: `voce.divieti_del_libro` aggiunge i divieti come voci in modalità avviso
  (`voce:<slug>:<id>`), solo se `ZB_BANCA_VOCI` è impostata.
- Il parser del briefing (`nuovo.leggi_briefing`) tratta ogni riga «Campo: valore» senza trattino come
  direttiva globale: nelle sezioni descrittive del briefing si scrive sempre «- Campo: …».

### Controllo dei nomi reali

`nomi_vietati.txt` è vuoto per regola. Il controllo si fa in memoria: leggere titoli, autori e
`nomi_propri.txt` dai rami dei libri su origin (`git ls-remote origin`, `git show <ramo>:<file>`),
cercarli in `git ls-files motore CLAUDE.md`, non salvare la lista. Ultimo esito: zero nomi reali; le
coincidenze sono parole comuni e nomi inventati del ramo di prova da cui viene il mini-libro romance.

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
- La banca-voci contiene solo schede di voce e divieti: niente pagine di libri, manoscritti, nomi di
  romanzi, personaggi o luoghi reali, né lì né nel motore. Il contenuto dei libri sta nel briefing.
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

- Le voci si aggiungono in banca-voci quando l'autore lo decide (copiare `modelli/scheda-vuota.md`,
  stato `da_completare` finché non verifica).
- Prove sulle fasce del margine interno oltre la prima (un mini-libro sintetico oltre le 150 pagine).
- Hook in modalità blocco, dopo l'«ok» dell'autore e la prova dei 14 scenari.
- Unire il motore ai rami dei libri, se l'autore lo chiede (merge, mai rebase).

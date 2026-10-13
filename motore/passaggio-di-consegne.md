# Passaggio di consegne: motore

Frase di apertura per la nuova chat: «Leggi motore/passaggio-di-consegne.md e riprendi da lì».

## Stato

- Ramo `motore` (unico ramo di lavoro sul motore), allineato a origin. Ultimo commit: quello di questo file (`git log -1`).
- Suite: **457/457 OK**, 0 saltate, 0 KO, con LanguageTool e `ZB_BANCA_VOCI`. Comando:
  `ZB_LANGUAGETOOL=<cartella>/lib ZB_BANCA_VOCI=<banca-voci> python3 -B motore/zb prove`, dalla radice del repository.
- Recinto sul libro attivo: hook `motore/script/hook_recinto.py` in **blocco**, nel modello
  `dati/hook-settings.esempio.json` insieme all'hook del manoscritto (avviso). Sul ramo `motore` non c'è
  `.claude/settings.json` (lo vuole la prova): sui rami di libro si attiva con `zb hook attiva --ok`.
- `zb voce` (fd404a8), nessuna modifica in questa sessione:

  | Elemento | Esito |
  |---|---|
  | `zb voce lista` | esiste |
  | `zb voce mostra <slug> [N]` | esiste |
  | `zb voce verifica <slug>` | esiste |
  | `ZB_BANCA_VOCI` | esiste |
  | blocco `voce` in libro.yaml | esiste |
  | divieti della voce in `stile.py` | esiste |
  | sezioni del briefing | esiste (nell'esempio resta il «biondo» DA CONFERMARE, punto aperto 7) |
- Banca-voci (repository separato, fuori dal motore, solo schede di voce e divieti): remote privato
  `https://github.com/NGTAProtocol/https-github.com-banca-voci`, ramo `main`, HEAD `08ce720`
  «aggiunte 7 voci editoriali», allineato a origin. 9 voci: `atkinson-2-0` e `ibrida-pasolini-camilleri`
  (pronte); `avventura-e-cuore`, `mistero-ed-epicita`, `grande-voce-crossover` (ragazzi, narrativa) e
  `saggistica-cinematografica`, `saggistica-psicologica-esistenziale`, `saggistica-idee-visione`,
  `saggistica-corale-sociale` (saggistica e biografia), tutte `da_completare`. Copia di sicurezza: bundle
  `banca-voci.bundle` (sha256 `5a172d7c…1774802`) mandato all'autore.
- Ramo `archivio/ghimoney` su origin (572f40f): contiene `ghimoney/`, tolto dal motore.
- Dettagli completi: `motore/report-motore.md`.

## Decisioni prese

- I libri restano nel repository, in `libri/<slug>/`, solo sui rami di libro; il ramo `motore` non
  contiene mai un libro (strada «c»).
- Hook di Claude Code in blocco sulle scritture fuori dal libro attivo (sì dell'autore): sta nel modello
  `dati/hook-settings.esempio.json` e si attiva sui rami di libro con `zb hook attiva --ok`, insieme
  all'hook del manoscritto (avviso). Nessun `.claude/settings.json` sul ramo `motore`.
- Nessuna prova già verde si cambia: CLAUDE.md resta entro 30 righe e senza percorsi di libri («nella
  cartella del libro»); il percorso preciso `libri/<slug>/` sta qui e in `prove/esiti/recinto-libro.md`.
- `zb nuovo` rifiuta un libro dentro `motore/`, nella radice del repository o sul ramo `motore`, e fuori
  da `libri/<slug>/` (eccezione: le prove della suite, `ZB_PROVE=1`, che restano rifiutate negli altri tre casi).
- Libro attivo in `libri/libro-attivo.md` (prima riga: lo slug), impostato da `zb nuovo` o
  `zb lavoro libro <slug>`; stato del lavoro («libro» | «motore») in `<git-dir>/zb-lavoro`, non tracciato.

## Regole da non violare

- Regola madre: il motore resta sempre pulito. I libri stanno in `libri/<slug>/` solo sui rami di
  libro; il ramo `motore` non contiene mai un libro. Sul libro si scrive solo nella sua cartella.
- Report di sessione ogni 5 scambi di lavoro o a «passaggio»: sul libro in
  `libri/<slug>/passaggio-di-consegne.md`, mai in motore/; questo file solo per il lavoro sul motore.
  Sezioni fisse: Stato; Decisioni prese; Regole da non violare; Fatto in questa sessione; Punti aperti;
  Prossimo passo; Ripartenza.
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

## Fatto in questa sessione: recinto sul libro

| Commit | Cosa |
|---|---|
| ultimo | `nuovo.py` (posizione del libro), `hook_recinto.py` nel modello `dati/hook-settings.esempio.json`, `zb lavoro`, CLAUDE.md (regola di avvio e report, 29 righe), 3 prove, questo file, `prove/esiti/recinto-libro.md` |

Come funziona l'hook (PreToolUse su Write, Edit, MultiEdit, NotebookEdit):
- lavoro su un libro: consentito solo `libri/<slug-attivo>/`; tutto il resto (motore/ compreso, fuori dal
  repository compreso) bloccato con «RECINTO: …», codice 2. Nascita: consentito anche
  `libri/<slug>/briefing.md` se quel libro non ha ancora `libro.yaml`.
- `libro-attivo.md` assente o vuoto: avviso, non blocco (succede sul ramo `motore`, che non ha `libri/`).
- «lavoro sul motore» → `zb lavoro motore`: consentito il repository tranne `libri/`. `zb lavoro stato` mostra lo stato.

### Stessa sessione: banca-voci (nessun commit nel motore)

| Commit (banca) | Cosa |
|---|---|
| 08ce720 | 7 voci editoriali: testo dell'autore invariato nelle sezioni 1, 2, 3 e 7 della scheda; sezioni 4-6 e `divieti.yaml` (vuoto) da completare dall'autore; `ambientazione: altro`; indice.yaml e README a 9 voci |

Remote: push normale di `main` su `NGTAProtocol/https-github.com-banca-voci` (repository vuoto prima).
La rinomina in `banca-voci` è sospesa: l'autore non riesce ad accedere a GitHub (email di verifica non
ricevuta); `NGTAProtocol/banca-voci` oggi non esiste per la sessione.

### Sessione precedente: ripristino della banca-voci

| Dove | Commit | Cosa |
|---|---|---|
| banca-voci | 896e7f4 | `voci/<slug>/materiali/LEGGIMI.md` per le due voci (sopra a22b018) |
| motore | fd61225 | questo file (ripartenza con `ZB_BANCA_VOCI`), `prove/esiti/banca-voci-ripristino.md` |

### Sessioni precedenti: solo schede (commit sul ramo motore)

| Commit | Cosa |
|---|---|
| 78b9963 | `zb voce verifica` non richiede più pagine d'esempio; mini-banca di prova senza esempi; prova «un solo esempio» sostituita da «scheda assente» |
| c49842a | report, questo file, `prove/esiti/voce-solo-schede.md` |
| 8f268c7 | hash in questo file |
| d4b4833 | sezione «Ripartenza» |

Banca-voci: rimosse le pagine d'esempio; due voci pronte, ciascuna con `scheda.md` e `divieti.yaml`.
Il contenuto dei libri lo decide l'autore nel briefing.

### Voci narrative (commit sul ramo motore)

| Commit | Cosa |
|---|---|
| fd404a8 | `voce.py`, `zb voce`, `ZB_BANCA_VOCI`, blocco `voce` in libro.yaml, «Letto» con la voce, divieti in `stile.py`, CLAUDE.md |
| 783216e | `modelli/briefing.md`: storia, schede dei personaggi, luoghi, regole, voce |
| e619bcf | prove della sezione «voce» (+25), mini-banca inventata |
| 80d7f46 | report, questo file, `prove/esiti/voce.md` |

### Prima ancora (commit sul ramo motore)

| Commit | Cosa |
|---|---|
| 3a01e42 | LanguageTool attivo; skip esplicito «LanguageTool assente»; README «Ambiente» |
| 48d0a22 | prove PDF senza sha256: prova strutturale, margini ±0,005 e minimi KDP |
| f27082e | formato esatto delle pagine (Chromium arrotondava l'A5) |
| 57f262e | via i riferimenti testuali ai libri reali (frasi di prova inventate, sezioni rinominate) |
| 572f40f | prova del bleed (+5 prove) e numeri di pagina sul trim |
| ea464c7 | `ghimoney/` rimosso, dopo la verifica dell'archivio (80 file, sha256 identici) |
| b36a438 | report-motore.md e questo file |

## Punti aperti

1. Verifica dei dati KDP sulle pagine ufficiali (`ultima_verifica: null`).
2. Scrivere TrimBox e BleedBox nel PDF? Controllare trasparenze e immagini?
3. `dati/nomi_vietati.txt` vuoto: come far controllare i nomi reali a `separazione.py` senza scriverli
   nel repository (per esempio una lista esterna letta da una variabile d'ambiente).
4. Rigenerare i PDF dei libri A5 già impaginati: solo su richiesta.
5. Script d'avvio della sessione per installare le dipendenze in un container nuovo.
6. Banca-voci: repository privato fatto (`NGTAProtocol/https-github.com-banca-voci`); rinomina in
   `banca-voci` sospesa (accesso a GitHub dell'autore). Le 7 voci nuove restano `da_completare`: servono
   lessico guida, adattamento per genere, campione-modello e divieti (dall'autore, o scritti da Claude
   con il suo ok).
7. Nell'esempio del briefing, il biondo: capelli o capo d'abbigliamento? (segnato «DA CONFERMARE»).
8. L'hook copre Write, Edit, MultiEdit e NotebookEdit, non Bash: una scrittura via shell non è bloccata
   (resta il recinto dei comandi del motore, `comune.scrivi`).
9. «zb lavoro motore» lo lancia Claude quando l'autore scrive «lavoro sul motore»: l'hook non può
   verificare chi l'ha chiesto.
10. Dove nasce un libro: chiuso (strada «c», vedi «Decisioni prese»).

## Prossimo passo

- Banca-voci: completare le 7 voci nuove (sezioni 4-6 e `divieti.yaml`), poi `stato: pronta` e
  `zb voce verifica`; rinomina del repository quando l'autore rientra su GitHub.
- Sul primo ramo di libro: unire il motore (merge, mai rebase), `zb hook attiva --ok` (dopo l'«ok»
  dell'autore, commit a parte sul ramo del libro), poi `zb lavoro libro <slug>` e `zb avvio libri/<slug>`;
  per un briefing nuovo `zb nuovo libri/<slug>/briefing.md`.
- Le voci si aggiungono in banca-voci quando l'autore lo decide (copiare `modelli/scheda-vuota.md`,
  stato `da_completare` finché non verifica).
- Prove sulle fasce del margine interno oltre la prima (un mini-libro sintetico oltre le 150 pagine).
- Hook del manoscritto in modalità blocco, dopo l'«ok» dell'autore e la prova dei 14 scenari.
- Unire il motore ai rami dei libri, se l'autore lo chiede (merge, mai rebase).

## Ripartenza

1. **Ramo.** La sessione può partire su un ramo diverso (per esempio `ccr-…`). Se l'autore indica il ramo
   `motore`: `git fetch origin motore && git checkout -b motore origin/motore` (o `git checkout motore`).
   Controllo: `git log -1` deve dare l'ultimo commit di questo file.
2. **Dipendenze** (circa 2 minuti, LanguageTool in background):
   `pip install pymupdf markdown` · `apt-get install -y hunspell hunspell-it` · nello scratchpad un
   `pom.xml` con `org.languagetool:languagetool-commandline` e `org.languagetool:language-it` 6.8, poi
   `mvn -q -B dependency:copy-dependencies -DoutputDirectory=lib` (143 file) ed
   `export ZB_LANGUAGETOOL=<scratchpad>/lt/lib`.
3. **Banca-voci.** In un container nuovo `/home/user/banca-voci` non c'è più. Collegare alla sessione
   `NGTAProtocol/https-github.com-banca-voci` (push), poi:
   ```
   git clone https://github.com/NGTAProtocol/https-github.com-banca-voci /home/user/banca-voci
   export ZB_BANCA_VOCI=/home/user/banca-voci
   ```
   Se il repository non è raggiungibile: bundle dell'autore (HEAD 08ce720, sha256 `5a172d7c…1774802`).
   Controllo: `zb voce lista` (9 voci, 2 pronte), `zb voce verifica` OK sulle 2 pronte (`script/voce.py`).
   Senza la banca la suite passa lo stesso: le prove «voce» usano la mini-banca di `prove/banca-voci-prova/`.
4. **Suite** (circa 10 minuti: lanciarla in background):
   `ZB_LANGUAGETOOL=… ZB_BANCA_VOCI=… python3 -B motore/zb prove` → atteso 457/457 OK.
   Per provare una sola sezione: importare `script/prove.py` e chiamare la funzione con
   `comune.leggi_yaml('prove/attesi.yaml')[<chiave>]`, poi cancellare `prove.TMP`.
5. **Remote della banca.** `NGTAProtocol/https-github.com-banca-voci`. Se l'autore lo rinomina in
   `banca-voci`: collegare `NGTAProtocol/banca-voci`, `git remote set-url origin
   https://github.com/NGTAProtocol/banca-voci.git`, fetch di verifica. `create_repository` resta rifiutato.
6. **Recinto.** `zb lavoro stato`. Sul ramo `motore` l'hook non è attivo (nessun `.claude/settings.json`);
   dopo «lavoro sul motore» dell'autore: `zb lavoro motore`. Su un libro: ramo del libro,
   `zb hook attiva --ok` se manca `.claude/settings.json`, poi
   `zb lavoro libro <slug>` e `zb avvio libri/<slug>`; il report va in `libri/<slug>/passaggio-di-consegne.md`.
7. **Frase di apertura**: «Leggi motore/passaggio-di-consegne.md e riprendi da lì» (sul motore) oppure
   «Leggi libri/<slug>/passaggio-di-consegne.md e riprendi da lì» (su un libro).

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

### Ambiente (container nuovo)

`pip install pymupdf markdown` · `apt-get install hunspell hunspell-it` · LanguageTool 6.8 da Maven
Central fuori dal repository e `ZB_LANGUAGETOOL` (README, «LanguageTool»). Java, Maven, Node,
Playwright, Chromium e poppler sono già presenti. Per le voci: `export ZB_BANCA_VOCI=<banca-voci>` (README,
«Banca-voci»); la banca va ripristinata dal suo remote o dal bundle (`git clone <bundle> banca-voci`).

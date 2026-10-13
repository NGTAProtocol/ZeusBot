# Motore editoriale

Fabbrica generica per romanzi di qualsiasi genere: procedura, script, modelli vuoti,
profili di genere e dati KDP. Non contiene libri reali. Il progetto completo è in
`proposta-motore.md` (approvata). Come si lavora su un libro: `PROCEDURA.md`.
Questo file raccoglie le regole d'uso e i comandi.

## Regole d'uso

- **Lancia sempre gli script con `python3 -B`.** L'opzione `-B` impedisce a Python di
  scrivere `__pycache__` dentro `motore/script/`: sarebbe una scrittura fuori dal libro,
  e `recinto.py` la segnalerebbe.
- Il libro si indica con un percorso: `python3 -B motore/script/<script>.py <libro>`.
  Il motore cerca `libro.yaml` nel percorso e nelle cartelle superiori.
- Ogni comando che opera su un libro scrive solo dentro la cartella del libro.

## Nomi dei file del manoscritto (`<libro>/04-manoscritto/`)

| File | Unità |
|---|---|
| `prologo.md` | prologo |
| `NN-<slug>.md` | capitolo NN (per esempio `07-la-stazione.md`) |
| `interludio-<N>.md` | interludio N (per esempio `interludio-II.md`), collocato con `struttura.interludi[].dopo_capitolo` di `libro.yaml` |
| `epilogo.md` | epilogo |

Un file con un nome diverso ferma il motore.

## Dal briefing al PDF

1. L'autore compila `modelli/briefing.md` nella cartella del libro; `zb nuovo <briefing>` crea il libro.
   Per un libro già avviato con documenti propri: `zb adotta <cartella>`.
2. A ogni sessione: `zb avvio <libro>` e la riga «Letto: …».
3. Fase documenti: bibbia, cronologia, scaletta e piano parole; `zb pronto`, poi `avanti` e `ok`.
4. Fase pagina campione: `05-revisioni/pagina-campione.md`; `zb pronto`, poi `ok`.
5. Stesura: un capitolo alla volta, `zb esito <libro> N`; fermata dopo il capitolo 3, poi lotti di N.
6. Due controlli falliti di fila sullo stesso capitolo: fermata e decisione dell'autore.
7. Chiusura: `continuita`, `ortografia`, `compila`, `impagina`, `pdf`, `pacchetto`, `kdp`; `zb pronto`.
8. A ogni passo: commit, push, `git status -sb`, `git log -1` (blocco di salvataggio, `PROCEDURA.md`).

## Comandi

Si lanciano con `python3 motore/zb <comando> …`; il libro è sempre un percorso (oppure `ZB_LIBRO`).

- `zb nuovo <briefing>`: crea il libro dal briefing; se è incompleto elenca cosa manca e non crea nulla.
- `zb avvio <libro>`: controlli di avvio e riga «Letto: …»; si ferma se qualcosa non va.
- `zb stato <libro>`: fase, gate, capitoli, parole, allineamento con origin; non scrive.
- `zb pronto <libro>`: fine del lavoro di una fase; apre il gate o passa oltre.
- `zb esito <libro> N`: controlli del capitolo N e registrazione dell'esito.
- `zb ok <libro> [lotti da N]`: approva il gate aperto, dopo aver mostrato tutti i blocchi.
- `zb avanti <libro>`: blocco successivo dei documenti del gate.
- `zb correggi <libro> <istruzione>`: registra una correzione; il gate resta aperto.
- `zb riapprova <libro> <documento> <motivo>`: registra una modifica autorizzata a un documento già approvato.
- `zb adotta <cartella>`: bozze di libro.yaml, stato, cronologia e nomi da documenti esistenti, con le fonti.
- `zb conta <libro>`: parole con il metodo unico, per capitolo e totale.
- `zb stile <libro> [N]`: frase media, dialogo, lista nera, tetti, similitudini, vincoli.
- `zb continuita <libro>`: date, età, durate, cifre, nomi scritti in due modi.
- `zb capitolo <libro> N`: tutti i controlli di un capitolo, con report.
- `zb ortografia <libro>`: Hunspell, LanguageTool se disponibile, checklist per la lettura umana.
- `zb compila <libro>`: manoscritto completo in `05-output/`.
- `zb impagina <libro>`: PDF di stampa in `05-output/`.
- `zb pdf <libro>`: verifica del PDF (pagine, font, margini, indice).
- `zb kdp <libro>`: conformità KDP, sezioni 1-15.
- `zb pacchetto <libro>`: struttura di `06-pubblicazione/` per KDP.
- `zb revisione <libro> <documento|gate> [N]`: un documento in blocchi di circa 120 righe; non scrive.
- `zb pulizia <libro> [--applica]`: elenco di temporanei, cartelle vuote e copie; cancella solo con `--applica`.
- `zb hook stato|attiva [--ok]|disattiva`: hook di Claude Code (oggi in modalità avviso, non attivi).
- `zb prove`: tutte le prove sui mini-libri inventati, più separazione e recinto.

Altri comandi: `zb verifica KDP fatta [AAAA-MM-GG]` (anche `stato`, `controlla`), `zb riciclo <libro>`,
`zb separazione`, `zb recinto`, `zb profili`, `zb aiuto`.

## Ambiente

Un container nuovo non conserva quello che è stato installato nelle sessioni precedenti. Prima di
`zb prove` o di `zb ortografia` servono:

- Python: `pip install pymupdf markdown` (PyMuPDF 1.28.2 negli attesi del passo 3);
- Hunspell con il dizionario italiano: `apt-get install hunspell hunspell-it`;
- Node con Playwright e Chromium (già presenti nel container: `/opt/pw-browsers`), `pdfinfo` e `pdftotext`.

### PDF nelle prove (passo 3)

Il render di Chromium cambia di qualche millesimo di pollice da un container all'altro, anche con le
stesse versioni. Per questo le prove non fissano lo sha256 del PDF, ma controllano:

- la struttura: pagine, formato di ogni pagina uguale al trim di `libro.yaml` (più il bleed, se previsto),
  font tutti incorporati e nessun Type3 (requisito KDP), Title e Author uguali a `libro.yaml`, testo
  estratto con PyMuPDF uguale all'atteso;
- i margini, con due condizioni:
  - entro ±0,005″ dall'atteso (`TOLLERANZA_MARGINI` in `script/prove.py`; non si allarga senza l'autore);
  - mai sotto i minimi KDP di `dati/kdp.yaml`: interno secondo il numero di pagine; esterno, alto e
    basso secondo il bleed.

  Un margine sotto il minimo KDP fa fallire la prova anche se è dentro la tolleranza.

### LanguageTool

Il motore non usa un server né un pacchetto Python. Lancia la riga di comando di LanguageTool
(`org.languagetool.commandline.Main`) con `java -cp <cartella>/*`, e la cartella dei `.jar` la legge
da `ZB_LANGUAGETOOL`. Senza questa variabile, `zb ortografia` salta il livello (b) e `zb prove`
salta 2 prove, con il motivo «LanguageTool assente».

Installazione (Java 21 e Maven già presenti nel container):

1. In una cartella temporanea fuori dal repository (per esempio lo scratchpad della sessione), un
   `pom.xml` con le dipendenze `org.languagetool:languagetool-commandline` e `org.languagetool:language-it`,
   versione 6.8.
2. `mvn -q -B dependency:copy-dependencies -DoutputDirectory=lib`: scarica da Maven Central 143 file, 240 MB.
3. `export ZB_LANGUAGETOOL=<cartella temporanea>/lib`.

Non va nel repository e non si scarica da languagetool.org. Se Maven Central risponde 403 o 429,
le 2 prove restano saltate. Dettagli in `PROCEDURA.md`, sezione «Ortografia».

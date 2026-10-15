# Motore editoriale

Fabbrica generica per romanzi di qualsiasi genere: procedura, script, modelli vuoti, profili di genere,
dati KDP e il livello editoriale (`editoriale/`: percorso, ruoli, agenti, anti-IA, correttore). Non
contiene libri reali. Come si lavora su un libro: `PROCEDURA.md`. Percorso e ruoli: `editoriale/00-percorso.md`
e `editoriale/LEGGIMI.md` (che ha anche l'unica scala di precedenza). Questo file raccoglie le regole d'uso,
l'ambiente e gli hook. Documenti per l'autore in `docs/` (non letti nelle sessioni di lavoro).

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

Il percorso completo, con chi lavora e le fermate, è `editoriale/00-percorso.md`. In breve:
`zb nuovo` (cartella unica `libri/<slug>/`, fase struttura) → struttura e revisione della struttura
(gate `struttura`) → documenti → pagina campione → stesura capitolo per capitolo con `zb esito` e
`zb capsula` → revisione strutturale del manoscritto → line → copy → bozze → chiusura meccanica
(`continuita`, `ortografia`, `compila`, `impagina`, `pdf`, `pacchetto`, `kdp`, `pronto`). Ogni gate si apre
con `zb pronto` e si chiude con `ok` (o `avanti`, `correggi`). A ogni passo il blocco di salvataggio.

## Comandi

L'elenco dei comandi è uno solo, nel codice: `python3 motore/zb aiuto`. Il libro è sempre un percorso
(oppure `ZB_LIBRO`). Ogni comando stampa al massimo 40 righe (`dati/output.yaml`) e rimanda al file con
l'output intero; le righe con KO o FERMO restano a schermo.

## Hook di Claude Code

Si attivano solo sul ramo di un libro, con l'ok dell'autore: `zb hook attiva --ok` copia
`dati/hook-settings.esempio.json` in `.claude/settings.json`. Sul ramo `motore` restano spenti (lo
controlla `zb prove`). Sono una protezione in più, non una garanzia: i controlli che contano sono quelli di
`zb avvio` e `zb push`, che guardano git.

| Hook | Script | Cosa fa | Modalità |
|---|---|---|---|
| SessionStart | `hook_sessione.py` | registra il session_id; dopo una compattazione chiede un nuovo `zb avvio` | mai blocca |
| PreToolUse Write, Edit, MultiEdit, NotebookEdit, Bash | `hook_manoscritto.py` | scrittura nel manoscritto senza `zb avvio` della sessione | `dati/hook.yaml`, `modalita` (oggi avviso) |
| PreToolUse Write, Edit, MultiEdit, NotebookEdit, Bash | `hook_recinto.py` | recinto sul libro attivo (anche redirezioni, tee, sed -i, cp, mv, rm), cartella unica prima di git commit e git push, nessuna riscrittura intera di un capitolo da parte di un revisore, annota chi scrive (separazione dei ruoli) | blocco |
| PostToolUse Read, Agent, Task | `consumo.py` | file e righe letti, subagenti chiamati, per `zb consumo` | mai blocca |

Separazione dei ruoli: `dati/hook.yaml`, `separazione_ruoli` (oggi `blocco`). Limiti del rilevamento su
Bash: docstring di `hook_recinto.py` e `PROCEDURA.md`, «Hook». Subagenti: `zb agenti attiva --ok`, come gli hook.

## Ambiente

### Solo il motore nel repository

Nel ramo del motore stanno solo codice, configurazione, dati KDP e i mini-libri inventati di `prove/`
(con autori inventati). Nessun manoscritto reale e nessun riferimento a libri reali: niente titoli,
autori, personaggi, luoghi, frasi o nomi di ramo dei libri, nemmeno nei commenti, nelle prove e negli
esiti. Le frasi di prova si inventano.

Un container nuovo non conserva quello che è stato installato nelle sessioni precedenti. Prima di
`zb prove` o di `zb ortografia` servono:

- Python: `pip install -r motore/requirements.txt` (PyYAML, PyMuPDF 1.28.2 degli attesi del passo 3, markdown);
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

### Formato esatto delle pagine

Chromium arrotonda il formato della pagina: i formati che non sono multipli di 1/96″ escono
sbagliati di qualche decimo di millimetro (A5, 5,83 × 8,27″, diventa 5,833 × 8,263″).
`impagina.py` (`formato_esatto`) riporta ogni pagina al trim di `libro.yaml`, più il bleed di
`dati/kdp.yaml` se previsto, senza scalare il contenuto. MediaBox e CropBox coincidono e partono
da 0, 0. Il contenuto resta fermo rispetto all'angolo in alto a sinistra; con il bleed scende di un
bleed e, sulle pagine pari, si sposta di un bleed a destra. I numeri di pagina stanno al centro del
piede del trim, quindi seguono lo stesso spostamento.

Prova del bleed (passo 3, `bleed_pdf`): copia inventata del romance con `bleed: true`, confrontata con
la stessa copia senza bleed. Controlla il formato (trim + bleed di `dati/kdp.yaml`), lo spostamento di
ogni parola (0,125″ in basso su tutte le pagine, 0,125″ a destra solo sulle pari) e il margine esterno:
0,75″ ±0,005, mai sotto il minimo KDP con bleed (0,375″).

### LanguageTool

Il motore non usa un server né un pacchetto Python. Lancia la riga di comando di LanguageTool
(`org.languagetool.commandline.Main`) con `java -cp <cartella>/*`, e la cartella dei `.jar` la legge
da `ZB_LANGUAGETOOL`. Senza questa variabile, `zb ortografia` salta il livello (b) e `zb prove`
salta 2 prove, con il motivo «LanguageTool assente».

Installazione stabile, un comando (Java e Maven già presenti nel container):

```
python3 motore/zb ortografia installa            # scarica in ~/.cache/zb-languagetool, mai nel repository
export ZB_LANGUAGETOOL=~/.cache/zb-languagetool/lib   # la riga esatta la stampa il comando
python3 motore/zb ortografia verifica            # OK solo se la frase di prova «Qual'è il problema?» è segnalata
```

- Versioni: 6.8, poi 6.7 (su Maven Central `languagetool-commandline` 6.4-6.6 non esiste); `--versione X` per
  sceglierne un'altra, `--cartella <dir>` per un'altra cartella fuori dal repository.
- Prima prova la cache locale di Maven (`~/.m2`, senza rete), poi Maven Central. Scarica in `lib.nuova` e
  sostituisce `lib` solo dopo la verifica: una cartella che funziona non si perde.
- Già pronta e verificata: non riscarica niente, quindi si può lanciare a ogni sessione nuova.
- `ZB_LANGUAGETOOL` va impostata nell'ambiente della sessione (per le sessioni nel cloud: variabili
  d'ambiente dell'ambiente o script di avvio). Senza, `zb ortografia` salta il livello (b) e lo dice nel report.
- Se Maven Central risponde 403 o 429 il comando si ferma: non insistere, si resta con Hunspell e la lista di
  controllo del correttore (livelli a e c) e si riprova più tardi.
- Circa 143 file, 240 MB. Non si scarica mai da languagetool.org.

### Banca-voci

Le voci narrative (come si racconta) stanno in un repository separato, la banca-voci, mai dentro il
motore. La banca contiene solo schede di voce e divieti: niente pagine di libri né manoscritti. Il
contenuto di ogni libro lo decide l'autore nel briefing. Il motore legge la banca in
sola lettura dalla cartella indicata da `ZB_BANCA_VOCI`, come fa con `ZB_LANGUAGETOOL`; nessun percorso
è scritto nel codice.

```
export ZB_BANCA_VOCI=<cartella della banca-voci>
python3 motore/zb voce lista
python3 motore/zb voce mostra <slug> [N]     # scheda in blocchi di circa 120 righe
python3 motore/zb voce verifica <slug>       # indice, scheda con 7 sezioni e «ambientazione:», divieti.yaml, pronta
```

Struttura della banca: `indice.yaml` (`voci:` con `slug`, `nome`, `genere`, `stato: pronta | da_completare`),
`voci/<slug>/scheda.md` con le sezioni «## 1. Nome e ruolo», «## 2. Principi», «## 3. Ritmo e sintassi»,
«## 4. Lessico…», «## 5. Adattamento per genere», «## 6. Campione…», «## 7. Istruzione di esecuzione»
(con il campo «ambientazione:») e `voci/<slug>/divieti.yaml`
(`divieti:` con `id` ed `espressione` o `pattern`): le espressioni vietate della voce.

Un libro sceglie la voce in `libro.yaml` con il blocco facoltativo `voce: {slug, ambientazione}` (dal
briefing: «Voce dalla banca:» e «Ambientazione:»). Con il blocco, `zb avvio` aggiunge alla riga «Letto»
il briefing e la scheda della voce; se `ZB_BANCA_VOCI` manca o la voce non verifica stampa un AVVISO e
non si ferma. `zb esito` aggiunge i divieti della voce alle voci del libro, in modalità
avviso (controllo `voce:<slug>:<id>`); senza `ZB_BANCA_VOCI` i divieti non si applicano. Senza il blocco nulla cambia. Senza `ZB_BANCA_VOCI`, `zb voce` si ferma con un messaggio
chiaro. Le prove usano una mini-banca inventata in `prove/banca-voci-prova/`.

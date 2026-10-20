# Motore editoriale

Fabbrica generica per romanzi di qualsiasi genere: procedura, script, modelli vuoti, profili di genere,
dati KDP e il livello editoriale (`editoriale/`: percorso, ruoli, agenti, anti-IA, correttore). Non contiene
libri reali. Il progetto iniziale è in `proposta-motore.md` (approvata). Come si lavora su un libro: `PROCEDURA.md`.
Percorso e ruoli: `editoriale/00-percorso.md` e `editoriale/LEGGIMI.md` (che ha anche l'unica scala di precedenza).
Questo file raccoglie le regole d'uso, l'ambiente e gli hook. Copia integrale di tutta l'infrastruttura
(motore, regole, voci, hook), con mappa e guida alla modifica: `docs/INFRASTRUTTURA_COMPLETA.md`.
Guida di lettura per l'autore (organigramma, percorso di un libro, regole), in PDF per telefono: `docs/GUIDA_AL_SISTEMA.pdf` (sorgente `docs/GUIDA_AL_SISTEMA.md`).
I documenti di `docs/` non si leggono nelle sessioni di lavoro.

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

## Dal briefing al PDF (percorso da casa editrice)

I libri nuovi seguono il percorso editoriale (`percorso: editoriale` in `libro.yaml`) in **modo automatico**: il
motore fa i controlli e passa da una fase all'altra senza approvazioni intermedie; l'unica fermata è la **pausa di
lettura** ogni 3 capitoli (`pausa_lettura`: 3, 4 o 5 in `libro.yaml`). `editoriale/00-percorso.md` e i ruoli
descrivono ancora le fermate con l'«ok» dell'autore: il contrasto è segnalato in `docs/DA_VERIFICARE_AUTORE.md`.

1. L'autore compila `modelli/briefing.md` in `libri/<slug>/briefing.md`; `zb nuovo` apre la cartella unica del libro
   (per un libro già avviato: `zb adotta <cartella>`). «Percorso: breve» nel briefing sceglie il percorso breve.
2. A ogni sessione: `zb avvio <libro> [--ruolo R]` e la riga «Letto: …»; un ruolo per sessione; nelle sessioni
   nuove lo stato compatto.
3. Struttura (nove file di `03-struttura/`), poi rapporto del diagnosta e piano dell'editor strutturale in sessioni
   e commit separati; `zb pronto` verifica la struttura (gate `struttura` automatico) e, se regge, crea bibbia,
   codex, cronologia e manuale e passa ai documenti; se no si ferma e scrive il motivo.
4. Documenti (bibbia, codex, cronologia, manuale, nota di direzione); pagina campione; stesura capitolo per capitolo
   con `zb esito` e capsule; pausa di lettura ogni `pausa_lettura` capitoli e a fine stesura.
5. Revisione strutturale del manoscritto, line editing, copyediting, bozze: rapporti → `zb pronto` → applicazione
   → `zb pronto`. Un gate dell'autore solo se il briefing lo chiede («Gate: …»).
6. Chiusura: `continuita`, `ortografia`, `compila`, `impagina`, `pdf`, `pacchetto`, `kdp`; `zb pronto`.
7. Traduzione facoltativa: `zb traduci <libro> --a en inizia`.
8. A ogni passo: `zb salva` (recinto, commit, push), `git status -sb`, `git log -1`.
Dettagli: `PROCEDURA.md`; ruoli e regole editoriali: `editoriale/`.

## Comandi

Unica fonte: `dati/comandi.yaml`. `python3 motore/zb aiuto` li elenca per gruppo, `zb aiuto <comando>` dà l'uso.
Il libro è sempre un percorso (oppure `ZB_LIBRO`). Ogni comando stampa al massimo 40 righe (`dati/output.yaml`,
`righe_max`) e mette l'output intero in `<libro>/.zb/ultimo-output.txt` (o nella cartella temporanea); le righe con
KO, FERMO o ERRORE restano sempre a schermo. I comandi che mostrano testo da leggere per intero (`esenti` nello
stesso file) non si tagliano; con `ZB_OUTPUT_COMPLETO=1` niente taglio.

## Hook di Claude Code

Si attivano solo sul ramo di un libro, con l'ok dell'autore: `zb hook attiva --ok` copia
`dati/hook-settings.esempio.json` in `.claude/settings.json`. Sul ramo `motore` restano spenti. Sono una
protezione in più, non una garanzia: i controlli che contano sono quelli che guardano git (controllo pre-commit,
`zb avvio`, `zb salva`, `zb push`; `PROCEDURA.md`, sezione 10).

| Hook | Script | Cosa fa | Modalità |
|---|---|---|---|
| SessionStart | `hook_sessione.py` | registra il session_id; dopo una compattazione chiede un nuovo `zb avvio` | mai blocca |
| PreToolUse Write, Edit, MultiEdit, NotebookEdit, Bash | `hook_manoscritto.py` | scrittura nel manoscritto senza `zb avvio` della sessione | `dati/hook.yaml`, `modalita` (oggi avviso) |
| PreToolUse Write, Edit, MultiEdit, NotebookEdit, Bash | `hook_recinto.py` | recinto sul libro attivo (anche redirezioni, tee, sed -i, cp, mv, rm), cartella unica prima di `git commit` e `git push`, nessuna riscrittura intera di un capitolo da parte di un revisore, annota chi scrive (separazione dei ruoli) | blocco |
| PostToolUse Read, Agent, Task | `consumo.py` | file e righe letti, subagenti chiamati, per `zb consumo` | mai blocca |

Separazione dei ruoli: `dati/hook.yaml`, `separazione_ruoli` (oggi `blocco`). Controllo pre-commit di git:
`script/precommit.py`, installato da `zb lavoro`. Subagenti e comandi di Claude Code: `zb agenti attiva --ok`, solo
sui rami dei libri, come gli hook.

## Ambiente

### Solo il motore nel repository

Nel ramo del motore stanno solo codice, configurazione, dati KDP e i mini-libri inventati di `prove/`
(con autori inventati). Nessun manoscritto reale e nessun riferimento a libri reali: niente titoli,
autori, personaggi, luoghi, frasi o nomi di ramo dei libri, nemmeno nei commenti, nelle prove e negli
esiti. Le frasi di prova si inventano.

Un container nuovo non conserva quello che è stato installato nelle sessioni precedenti. Prima di
`zb prove` o di `zb ortografia` servono:

- Python: `pip install -r motore/requirements.txt` (PyYAML, PyMuPDF 1.28.2, Markdown);
- Hunspell con i dizionari italiano e inglese: `apt-get install hunspell hunspell-it hunspell-en-us`;
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

Il motore lancia la riga di comando di LanguageTool (`org.languagetool.commandline.Main`) con
`java -cp <cartella>/*`; la cartella dei `.jar` la legge da `ZB_LANGUAGETOOL`. Senza, `zb ortografia` salta il
livello (b) e lo dice nel report, e `zb prove` salta le prove di LanguageTool con il motivo «LanguageTool assente».

Un solo comando, `zb languagetool` (Java e Maven presenti):

```
python3 motore/zb languagetool installa [--cartella <dir>] [--versione X]   # mai dentro il repository
export ZB_LANGUAGETOOL=<dir>/lib      # la riga esatta la stampa il comando
python3 motore/zb languagetool verifica   # OK solo se la frase di prova «Qual'è il problema?» è segnalata (regola GR_…)
python3 motore/zb languagetool stato      # variabile, numero di .jar, se il livello (b) gira davvero
```

- Cartella predefinita: `$ZB_LANGUAGETOOL/..` se impostata, altrimenti `~/.cache/zb-languagetool`. Il `pom.xml`
  ha `languagetool-commandline`, `language-it` e `language-en` della stessa versione: 6.8, poi 6.7.
- Prima prova la cache locale di Maven (`~/.m2`, senza rete), poi Maven Central (mai languagetool.org). Scarica in
  `lib.nuova` e sostituisce `lib` solo dopo la verifica: una cartella che funziona non si perde.
- Già pronta e verificata: non riscarica niente, quindi si può lanciare a ogni sessione nuova.
- Se Maven Central risponde 403 o 429 il comando si ferma: non insistere, si resta con Hunspell e la lista di
  controllo del correttore (livelli a e c).
- Verificato il 2026-10-15 e di nuovo il 2026-10-20 (versione 6.8): 143 `.jar`; «e» al posto di «è» NON è segnalato (resta alla lettura mirata del
  correttore).

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
non si ferma. `zb stile` e `zb capitolo` aggiungono i divieti della voce alle voci del libro, in modalità
avviso (controllo `voce:<slug>:<id>`); senza `ZB_BANCA_VOCI` i divieti non si applicano. Senza il blocco nulla cambia. Senza `ZB_BANCA_VOCI`, `zb voce` si ferma con un messaggio
chiaro. Le prove usano una mini-banca inventata in `prove/banca-voci-prova/`.

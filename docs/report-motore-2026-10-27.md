# Report sul motore e proposta per una casa editrice di qualità

Data: 2026-10-27. Ramo: `claude/audit-4-tools-claude-code-ho78x3` (ramo di libro con il motore unificato `d575b87`).
Base del giudizio: lettura di `motore/README.md`, `motore/report-motore.md`, `motore/passaggio-di-consegne.md`,
`dati/modelli-ruoli.yaml`, agenti installati in `.claude/`, libro di prova `libri/prova-padre-del-mostro/`
(stato, passaggio di consegne, note di lettura, rapporti); suite di prove **eseguita davvero** oggi; comandi
`zb stato`, `zb agenti stato`, `zb agenti prossimo`, `zb capitolo` provati sul libro di prova.
Nota: «sfornatore di HTTP» l'ho inteso come «macchina che sforna manoscritti»; se intendevi altro, dimmelo.

## 1. In una riga

Il motore è un **sistema di controllo molto solido** (stato, recinto, prove, PDF e KDP), ma **produce poco testo
e di qualità non ancora accettata**: in tre settimane il libro di prova ha 3 capitoli su 35 (6.413 parole su
70.000, 9%), il capitolo 1 riscritto «non passa» la revisione, e il lavoro è fermo dal 2026-10-21.
Il collo di bottiglia non è il controllo: è **la scrittura**.

## 2. Cosa funziona (verificato oggi)

| Parte | Esito | Prova |
|---|---|---|
| Suite di prove | **669/677 OK**, 0 saltate, con LanguageTool 6.8 | `zb prove`, tabella in `/tmp/zb-prove-ultimo.md` |
| Macchina a stati del libro (fasi, gate, pausa di lettura) | funziona | `zb stato` legge fase, capitoli, parole, 41 documenti approvati con impronta |
| Recinto e separazione (niente scritture fuori dal libro, niente libri nel motore) | OK | `recinto.py`: 48 esecuzioni pulite; `separazione.py` OK |
| Controlli di capitolo (parole, frase media, dialogo, lista nera, anti-IA, Gulpease, checklist) | funziona | `zb capitolo` sul capitolo 2: 0 KO, 2 avvisi |
| Ortografia (Hunspell + LanguageTool 6.8) | funziona | `zb languagetool installa`: frase di prova segnalata |
| Impaginazione PDF (Chromium, formato esatto, bleed, font incorporati) e conformità KDP (15 sezioni) | funziona | prove dei passi 3-4 (font incorporati 0 mancanti, nessun Type3) |
| Capsule di continuità (meno lettura per lo scrittore) | funziona | misura della suite: 4.086 parole lette con capsule contro 5.560 senza (-27%) |
| 12 agenti + 4 comandi installati in `.claude/` | installati, formato OK | `zb agenti stato`: 16/16 |

**Gli 8 KO della suite**
- 3 (`agenti e capsule`, `agenti e comandi`, `passo 5`): le prove si aspettano il ramo `motore` senza `.claude/`;
  questo è un ramo di libro con gli agenti installati. **Non sono difetti.**
- 2 (`passo 3`, struttura del PDF): pagine, formato, font e metadati sono giusti; cambia solo il conteggio del
  testo estratto (2.769 parole invece di 2.737). Il container ha Playwright 1.63.0, le prove sono tarate su 1.56.1.
  **Effetto dell'ambiente**, ma rivela una prova fragile (impronta del testo estratto).
- 3 (`passo 6`, `pulizia.py`): con `--applica` cancella anche il marcatore della sessione corrente
  (`.zb/letto-sessione-prova`). **Da verificare**: o la prova dipende dall'id di sessione, o `pulizia` può
  cancellare il file della sessione in corso.

**Difetti trovati usando i comandi**
- `zb agenti prossimo` stampa «scrittore-voce … pausa di lettura» al posto del numero del capitolo
  (`script/agenti.py` righe 128 e 133 usano il testo di `passo`).
- `zb stato`: passo «pausa di lettura» con gate «nessuno», anche se la pausa è stata chiusa (17213c4).
- Libro di prova: capsula del capitolo 3 mancante, capsula 1 con un fatto sbagliato (passaggio di consegne).
- `zb capitolo` riscrive i rapporti anche quando rilancia solo un controllo (diff di una riga): sporca il ramo.

## 3. Dove si perde la qualità (la diagnosi)

1. **Il modello più debole scrive, il più economico giudica.** In `dati/modelli-ruoli.yaml`: architetto e editor
   strutturale = opus (forte); **scrittore-voce = sonnet (medio)**; **diagnosta = haiku (leggero)**. Per un
   romanzo di alta qualità la stesura e il giudizio letterario sono proprio i due passi che meritano il modello migliore.
2. **Troppi vincoli numerici sulla prosa.** Lo scrittore deve rispettare insieme: frase media per registro,
   percentuale di dialogo, soglie anti-IA (aperture uguali, ripetizioni ravvicinate, formule per mille), lista nera,
   divieti della voce con massimi per gruppo, chiuse a sentenza contate frase per frase (il rapporto del
   capitolo 1 analizza 68 frasi una per una). Il risultato misurabile è prosa che «passa» i numeri ma esce rigida;
   i rapporti continuano a trovare gli stessi tic (chiuse, eco, battute giustificative, soggetti ambigui) giro dopo giro.
3. **Ciclo di correzione senza uscita.** Note di lettura ripetute tre volte (20 e 21 ottobre) con le stesse
   istruzioni; la riscrittura del capitolo 1 è stata respinta e il lavoro fermato. Manca un criterio di «abbastanza
   buono» qualitativo: oggi l'uscita dipende da soglie meccaniche.
4. **Il processo pesa più del testo.** Motore: 44 script, ~14.500 righe di Python (di cui ~4.200 di prove);
   documentazione: ~2.800 righe in `motore/` più ~29.500 in `docs/` (la sola `INFRASTRUTTURA_COMPLETA.md` copia
   l'intero motore). Contro 6.413 parole di romanzo. Ogni sessione spende contesto in avvio, ruoli, recinto,
   consegne, report ogni 5 scambi.
5. **Contrasti aperti mai chiusi**: le 28 schede del pacchetto editoriale dicono «fermati per l'ok», il motore va in
   automatico (segnalato in `docs/DA_VERIFICARE_AUTORE.md` dal 2026-10-20). Dati KDP mai verificati
   (`ultima_verifica: null`).

## 4. Cosa eliminare (o spegnere)

| Cosa | Perché | Come |
|---|---|---|
| Soglie numeriche di stile come **blocco** (frase media, dialogo %, anti-IA per mille, gruppi di divieti) | spingono verso prosa rigida e cicli infiniti | lasciarle come **informazione** nel rapporto, mai come KO; KO solo per fatti oggettivi (continuità, canone, nomi, parole vietate KDP) |
| Analisi frase per frase delle chiuse (68 righe di tabella) | costosa, non migliora il testo | sostituire con 3-5 passaggi citati dal revisore letterario |
| `docs/INFRASTRUTTURA_COMPLETA.md`, `report-motore.md`, parti ripetute di README/PROCEDURA/passaggio di consegne | quattro documenti dicono le stesse cose e vanno tenuti allineati a mano | un solo `README` del motore + `PROCEDURA.md`; il resto in archivio |
| Report di sessione ogni 5 scambi, riga «Letto: …», registro dei ruoli per sessione | burocrazia che consuma contesto | stato compatto aggiornato dal comando a ogni capitolo, basta |
| Percorso «breve», `adotta`, traduzione, lettore cieco (se non servono ora) | rami di codice e prove da mantenere | spegnere, tenere in archivio |
| Hook del manoscritto in «avviso», separazione ruoli per sessione | protezione fragile (lo dice il README stesso) | tenere solo il recinto su git (pre-commit) |
| **Ponytail** sui progetti di libri | inietta «scrivi il minimo» anche negli agenti di prosa | `PONYTAIL_DEFAULT_MODE=off` nei libri, o disinstallarlo |
| Prove con impronta del testo estratto dal PDF | si rompono a ogni aggiornamento di Chromium | confrontare pagine, formato, font, metadati e numero di parole con tolleranza |

## 5. Cosa aggiungere

**A. Modelli giusti nei posti giusti** (una riga ciascuno in `dati/modelli-ruoli.yaml`)
- scrittore-voce: **forte** (opus, o il modello più capace disponibile); revisione letteraria: **forte**;
  diagnosta meccanico, capsula, correttore: leggero/medio (sono controlli, non giudizi).

**B. Una catena per capitolo, corta e con un'uscita certa**
1. **Piano delle scene** (agente forte): obiettivo, conflitto, svolta, sottotesto, ultima immagine di ogni scena,
   dalla scaletta + capsule. Breve, approvabile in un colpo d'occhio.
2. **Stesura** (scrittore forte): con la scheda della voce e **3-5 pagine di prosa approvata dall'autore come
   esempio** (il motore oggi dà soprattutto divieti; gli esempi positivi sono la leva più forte sulla qualità).
3. **Due versioni delle scene chiave** (apertura, svolta, chiusa) e un giudice che sceglie: costa poco, alza molto.
4. **Revisione letteraria** (agente forte, sessione separata): legge come un editor, con una griglia qualitativa
   (tensione, sottotesto, specificità dei dettagli, credibilità dei dialoghi, ritmo, voce, promesse mantenute),
   voto 1-10 per voce e massimo 5 interventi mirati con citazione.
5. **Una sola riscrittura mirata**, poi controlli meccanici finali (continuità, canone, ortografia, parole vietate).
6. Se il voto medio è sotto la soglia scelta dall'autore (es. 8/10): si ferma e chiede all'autore, non riprova all'infinito.

**C. Un solo comando che fa girare tutto**
- Oggi: `zb agenti prossimo` dice chi chiamare, la sessione principale fa da orchestratore a mano.
- Proposta, in due tempi:
  1. subito: un comando di Claude Code `/capitolo N` (in `.claude/commands/`) che esegue in automatico la catena B
     con i subagenti già installati e si ferma solo alla pausa di lettura o a un controllo fallito;
  2. dopo: un **programma con agenti specifici** scritto con Claude Agent SDK (Python), che fa girare la stessa
     catena senza sessione aperta, capitolo dopo capitolo, salvando su git e mandando una notifica alla pausa di
     lettura. È la vera «macchina che sforna manoscritti», ma va fatta dopo aver verificato la qualità della catena
     su 3 capitoli.

**D. Misura della qualità che conta**
- Al posto delle soglie per mille: il **voto del revisore letterario** per capitolo e il tuo giudizio alla pausa
  di lettura, registrati in un file; si confronta il voto prima e dopo ogni cambio del motore.
- **Lettore cieco** attivo alla fine di ogni atto (non opzionale): legge senza documenti e dice dove si annoia o
  non capisce.

**E. Da chiudere una volta per tutte**
- Decidere il contrasto «ok dell'autore» contro «modo automatico» e allineare le 28 schede.
- Verificare i dati KDP (`zb verifica KDP fatta AAAA-MM-GG`) prima del primo libro vero.
- Correggere i 4 difetti della sezione 2.

## 6. Ordine consigliato

1. Cambiare i modelli (scrittore e revisore forti) e rendere informative le soglie di stile. Minimo sforzo, effetto immediato.
2. Raccogliere 3-5 pagine di prosa che ti piace (tua o di riferimento, nella voce scelta) come esempi positivi.
3. Rifare il capitolo 1 del libro di prova con la catena B e confrontarlo con la versione di oggi.
4. Se la qualità regge su 3 capitoli: comando `/capitolo N`, poi il programma con Agent SDK.
5. Solo allora la pulizia grossa (documenti doppi, rami spenti).

## 7. Cosa NON è stato verificato

- Non ho fatto girare gli agenti di scrittura (nessuna prosa prodotta oggi): il giudizio sulla qualità viene dai
  rapporti esistenti nel libro di prova, non da una prova nuova.
- La banca-voci (`ZB_BANCA_VOCI`) non è in questo container: le prove della voce usano la mini-banca inventata.
- I comandi di modifica del motore descritti sopra sono **proposte**: nulla è stato cambiato nel motore.
  Per applicarle serve «lavoro sul motore» e il tuo ok punto per punto.

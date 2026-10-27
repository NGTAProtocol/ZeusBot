# Miglioramenti del motore (2026-10-27)

Lavoro sul motore autorizzato dall'autore («lavoro sul motore», scelte: Opus dove si scrive o si giudica, parti non
usate archiviate, soglie di stile solo informative). Obiettivo: manoscritti di qualità alta, più velocità, meno token.

## Fonti studiate su GitHub (codice letto, solo idee riscritte)

| Progetto | Licenza | Cosa abbiamo preso |
|---|---|---|
| nousresearch/autonovel (d165f26) | nessun file LICENSE: solo idee, nessun testo | voti tarati (6 = mestiere, 8 = un editor lo terrebbe, 9+ solo con un confronto pubblicato), momento più debole citato per ogni voce, «in stesura si avanza, la qualità sale in revisione», taglio avversario («togli il 10%», tagli classificati = piano di revisione), regole che crescono dai difetti dei primi capitoli |
| ThomasHoussin/Claude-Book (3fdebbb) | MIT (© 2025 Thomas Houssin), LICENSE letto | catena con subagenti di Claude Code, scrittore su Opus, revisori separati, massimo 3 giri |
| mrigankad/Novel-OS (1bd4b57) | MIT (© 2026 Mriganka Dey), LICENSE letto | controlli deterministici gratuiti prima del revisore LLM (già nel motore: misure di `zb ruolo`) |
| articoli DOC, Re3, Agents' Room, Plan Before You Write | — | pianificare prima di scrivere migliora coerenza e interesse (lo scrittore fissa il piano delle scene prima della stesura) |

## Qualità

- Scrittore, diagnosta, direttore editoriale, line editor e lettore cieco su **Opus**; correttori su Sonnet; capsule su
  Haiku (`dati/modelli-ruoli.yaml`).
- Revisione del capitolo: sette voti tarati con il momento più debole citato, `Media`, continuità, al massimo 5
  interventi, una **Lezione**. `zb esito` accetta solo con media ≥ `soglia_qualita` (predefinito 7.5).
- **Lezioni che crescono**: accettato un capitolo, la lezione va in `06-diagnostica/lezioni.md` (ultime 12, senza
  doppioni) e lo scrittore la legge prima di ogni capitolo successivo.
- Lo scrittore riceve funzione e gancio del capitolo successivo, per chiudere bene il capitolo.
- Line editing con il **taglio avversario** (10-20 interventi classificati: spiega, ridondante, superfluo, generico,
  dice, ritmo, tic).
- Soglie di stile **informative** (`soglie_stile`, predefinito `informative`): frase media, dialogo, scene, anti-IA e
  divieti della voce non bloccano più; bloccano i fatti oggettivi e il voto sotto soglia.

## Velocità

- **`/capitolo`**: la sessione principale (ruolo `regia`) ripete `zb agenti prossimo`, che guarda lo stato reale e dà
  una sola riga `AZIONE` o `FERMO`. Gira da solo fino alla pausa di lettura.
- Un giro di revisione completo più un giro mirato; poi decide l'autore (niente cicli infiniti).
- Rapporti brevi (≤ 400 parole), risposte degli agenti ≤ 5 righe.

## Token

- `CLAUDE.md` non impone più di leggere `PROCEDURA.md` (circa 6.300 parole) a ogni sessione né il report ogni 5
  scambi.
- Ruolo `regia`: «Letto» solo con `libro.yaml`, `stato.yaml`, stato compatto.
- Lo scrittore legge le ultime 3 capsule + registro delle promesse, non tutte le capsule del libro.
- Il diagnosta non legge più la tabella delle frasi finali.
- Agenti della traduzione installati solo con `--traduzione`.

## Difetti corretti

- `ZB_SESSIONE` ignorata quando c'era il file dell'hook (`pulizia --applica` cancellava il marcatore corrente).
- Passo rimasto «pausa di lettura» dopo la chiusura della pausa (a metà libro).
- `zb agenti prossimo` stampava «pausa di lettura» al posto del numero del capitolo.
- Separazione dei ruoli per sessione: con subagenti nella stessa sessione avrebbe bloccato la revisione del
  manoscritto; ora le scritture dei subagenti si registrano come «sessione:agente».
- Prova del PDF fragile (sha256 del testo estratto) e prove «solo motore» che fallivano sui rami di libro.

## Archiviato (ramo `archivio/motore-prima-2026-10-27`)

`zb adotta` con le sue prove e il mini-libro d'adozione; `docs/INFRASTRUTTURA_COMPLETA.md` e il suo generatore;
`motore/proposta-motore.md`; `motore/report-motore.md`.

## Seconda parte (stesso giorno): voce, agenti, grafica, pulizia

- **Voce dalle pagine campione**, anche ibrida: `00-progetto/voce/campione-N.md` → `zb voce campioni` (misure senza
  modelli) → agente `voce` (Opus) → `02-bibbia/voce.md` → `zb voce scheda`. Lo scrittore legge scheda e campioni; il
  diagnosta vota la voce su quella scheda; 7 parole uguali a un campione sono un KO.
- **Agenti più capaci**: ruolo dello scrittore riscritto come manuale di mestiere (motore della scena, mostrare una
  volta, dettaglio scelto, dialogo come azione, scena più che sommario, ritmo, tensione, sorpresa); diagnosta del
  manoscritto con critico, professore e panel di quattro lettori con le priorità di consenso; editor strutturale con
  classi di intervento (taglia, espandi, drammatizza, approfondisci, continuità).
- **Grafica**: stili dell'interno `classico` e `moderno` (capolettera, maiuscoletto, fleuron ❧ di EB Garamond);
  `zb copertina` (copertina intera in PDF con quarta, costola e prima, misura esatta, font incorporati); agente
  `grafico` (quarta di copertina e brief con tre concept e prompt per l'illustrazione).
- **Pulizia**: traduzione tolta per intero; documenti superati di `docs/` (analisi, avanzamento, decisioni
  dell'integrazione, proposte, guida vecchia) tolti, al loro posto `docs/GUIDA.md`; esiti storici delle prove tolti;
  il contrasto «ok dell'autore / modo automatico» chiuso allineando i testi del pacchetto editoriale.
- Corretta una prova che passava per caso (scriveva un file vuoto invece di «non passa»).

## Terza parte: libro pronto per la stampa, copertina KDP

- **Tipografia** (`zb tipografia <libro> [N]`): errori che un libro pubblicato non può avere, trovati senza modelli
  (accenti, «qual è», «po’», parola ripetuta, spazi, virgolette dritte, caporali spaiati, lineette, punti, due sistemi
  di dialogo). Lo scrittore lo esegue prima di consegnare il capitolo, il correttore lo porta a zero.
- **Impaginazione**: apostrofi e puntini tipografici (’ …) in stampa.
- **Controllo finale** (`zb finale <libro>`): compilato e PDF aggiornati (impronta), ortografia e LanguageTool eseguiti
  e a zero, tipografia, continuità, riciclo, PDF, KDP e copertina a 0 KO; falsi allarmi solo per iscritto con il motivo
  (`06-diagnostica/correzioni-accettate.yaml`). `zb pronto` in chiusura lo rifà e chiude solo a 0 KO.
- **Copertina**: pagine solo dal PDF definitivo (con impronta: se l'interno cambia la copertina va rifatta); copertina
  fatta da altri in `00-progetto/copertina/` (`prima` o `intera`), controlli di risoluzione e proporzioni; modello KDP
  per il grafico (PDF e PNG a 300 DPI), anteprima con le guide, scheda di caricamento KDP; `--pagine` solo anteprima.

## Quarta parte: giro della struttura senza intoppi

- `zb agenti prossimo` guida da solo il giro della struttura e del manoscritto: controllo del motore → diagnosta →
  editor strutturale → revisione con il piano → nuova diagnosi; al secondo «non passa» decide l'autore.
- Gli agenti senza terminale (diagnosta, editor strutturale, line editor) ricevono la prima riga del rapporto già
  calcolata dal motore; se manca si fermano e la chiedono, non la inventano.

## Da fare con l'autore

- Provare `/capitolo` sul libro di prova (capitolo 1) e confrontare con la versione di oggi.
- Tarare `soglia_qualita` dopo 3 capitoli (7.5 è il punto di partenza).
- Verifica dei dati KDP (`zb verifica KDP fatta AAAA-MM-GG`).

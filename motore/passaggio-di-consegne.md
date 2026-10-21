# Passaggio di consegne: motore

Frase di apertura per la nuova chat: «Leggi motore/passaggio-di-consegne.md e docs/DECISIONI_INTEGRAZIONE.md e
riprendi da lì».

## Stato

- Lavoro sul motore del 2026-10-20: integrazione nel ramo `integrazione-editoriale` (repository
  `NGTAProtocol/ZeusBot`, D1). Base: ramo ccr (`origin/ccr-d1e12273-izx78k`, d2b8814); aggiunte dal ramo `motore`
  (`origin/motore`, 971b6df). I rami `motore` e `main` non sono toccati (`main` in questo repository non esiste, D2).
  Ultimo commit: `git log -1` (prima del commit dei documenti derivati: 951a42c, allineato a origin).
- Punti dell'integrazione: 1-12 e 8b fatti e su origin; dopo: `CLAUDE.md` allineato (D17, 05facce), subagenti e
  capsula nei file del pacchetto (D18, 951a42c); documenti derivati nel commit che porta questo file.
- Suite: **637/637 OK** (dal punto 12; invariata con D17 e D18), 0 saltate, con LanguageTool 6.8 (`ZB_LANGUAGETOOL`), senza `ZB_BANCA_VOCI` (D12). Comando,
  dalla radice: `ZB_LANGUAGETOOL=<cartella>/lib python3 -B motore/zb prove` (a schermo solo le righe non OK;
  tabella intera in `zb-prove-ultimo.md` nella cartella temporanea).
- Lavoro del 2026-10-21 (problema di stile della prova): P1 campo `massimo` dei divieti della voce (1e11337); P2
  diagnosta in fase «stesura» sul capitolo singolo e `revisione_capitolo: obbligatoria` in `zb esito` (5d19661);
  P3 frasi finali in `zb stile` (03f12c6); frase media per registro della voce con `frase_media_voce` nel thriller
  (4d21449); ruoli e `zb prepara` con la voce (6371041). Suite dopo l'ultimo commit di codice: 655/655 OK, 0
  saltate. Dettaglio, realizzato e non realizzato: `docs/PROPOSTE_MOTORE.md`.
- Correzioni del 2026-10-21 (seconda parte): `zb prepara` nomina gli esempi «debole → forte» solo se la scheda li
  ha e si ferma se la scheda manca (dd93098); frase media del registro della voce: AVVISO «intervallo non
  calibrato sull'autore» (3990f86); gruppi di forme nei divieti della voce con un massimo complessivo (c79df0a).
  Suite: 661/661 OK, 0 saltate.
- Modo automatico (decisione dell'autore del 2026-10-20): gate «struttura» verificato dal motore senza fermata;
  nessuna approvazione intermedia; una sola fermata, la PAUSA DI LETTURA ogni 3 capitoli (`pausa_lettura` 3-5 in
  `libro.yaml`) e a fine stesura. Restano le fermate `controllo_fallito` e `canone`.
- Livello editoriale in `motore/editoriale/`: pacchetto da 28 file non toccato, più le 14 aggiunte da `motore`
  adattate ai nomi del pacchetto (`docs/DA_VERIFICARE_AUTORE.md`).
- Banca-voci: repository separato, letto in sola lettura da `ZB_BANCA_VOCI`; i nomi delle voci stanno solo lì.
- Documenti per l'autore: `docs/DECISIONI_INTEGRAZIONE.md` (D1-D18), `docs/DA_VERIFICARE_AUTORE.md`,
  `docs/ATTRIBUZIONI.md`, `docs/ANALISI_REPOSITORY.md`. Stato del motore per esteso: `motore/report-motore.md`.

## Decisioni prese

- Nomi del pacchetto da 28 file ovunque (`struttura_manoscritto`, `rapporto-struttura.md` /
  `rapporto-manoscritto.md`, `piano-revisione-struttura.md` / `piano-revisione-manoscritto.md`,
  `06-sottotrame-temi.md`); il nome `revisione_manoscritto` di `motore` non entra (D6).
- Libri nuovi del percorso editoriale: `gate: [lettura]`, `pausa_lettura: 3`; nessun documento prima della
  struttura (bibbia, codex, cronologia e manuale nascono alla sua chiusura). Libri senza il campo `percorso`: percorso
  breve, come prima (D6, D11).
- Pausa di lettura: `zb ok <libro>` = capitoli letti, si riparte; `zb correggi <libro> <note>` = note in
  `06-diagnostica/note-lettura.md`, si riparte (D11).
- Contrasto tra i 28 file (fermate con l'«ok») e il modo automatico: segnalato, non corretto nei 28 file (D4).
  `CLAUDE.md` descrive `--ruolo` e il modo automatico (D17). Nei 28 file, su autorizzazione dell'autore, solo:
  dodici subagenti in `editoriale/LEGGIMI.md`; capsula 120-250 parole in `agenti/capsula.md` e `risparmio-token.md` (D18).
- Recinto di ccr più, da `motore`: libro attivo in `<git-dir>/zb-libro-attivo`, cartella unica (`zb cartella`),
  impronta di una `zb prove` intera e tutta OK per `zb push` sul motore (D7).
- Ruoli: un solo comando, `zb ruolo` (controllo per fase di ccr e un ruolo per sessione di `motore`);
  `separazione_ruoli: blocco` (D8).
- Agenti: modelli solo da `dati/modelli-ruoli.yaml`; `zb agenti prossimo` con `dati/orchestrazione.yaml`; capsule
  di ccr (120-250 parole) con il campo `capsule` di `motore`; `zb consumo` con l'hook PostToolUse; output compatto
  (D9).
- Anti-IA: `antiia.py` di ccr con soglie per profilo e `libro.yaml`, `formule.yaml`, modalità `blocco`; sezione B
  non contata (`formule_sezione_b: false`). Un solo comando LanguageTool: `zb languagetool` (D10).
- Prove: tutte quelle dei due rami (632) più 1 del punto 8b e 4 del punto 12 (637); `prove.py` con `--solo` e `--sezione` (D12).
- Licenze Apache-2.0: solo idee, nessun testo (D13).

## Regole da non violare

- Regola madre: il motore resta sempre pulito; il ramo `motore` non contiene mai un libro.
- Nessun nome reale (autori, titoli, personaggi, luoghi, frasi, nomi dei rami dei libri) in codice, prove,
  commenti, esiti, report e documenti, anche in `docs/`. Controllo: `zb separazione`.
- Non toccare i rami dei libri, né `motore` e `main`: l'unione nel ramo `motore` la decide l'autore.
- I 28 file del pacchetto non si cambiano senza l'autore (eccezione autorizzata: D18).
- `dati/kdp.yaml`: `ultima_verifica` resta `null` finché l'autore non registra la sua verifica
  (`zb verifica KDP fatta AAAA-MM-GG`); il motore non la scrive.
- Agenti, comandi e hook spenti sul ramo del motore (`zb avvio` senza libro si ferma se ci sono); si accendono solo
  sui rami dei libri con l'«ok» dell'autore.
- Chi scrive non rivede: rapporti in commit separati dal testo, ruoli solo nella loro fase.
- Lavoro sul motore solo dopo «lavoro sul motore» dell'autore (`zb lavoro motore`).
- Salvataggio con `zb salva`; non dire «fatto» se non è su origin. Nessun push forzato, nessuna riscrittura della
  storia.
- Report di sessione ogni 5 scambi o a «passaggio», con le sezioni fisse.

## Fatto in questa sessione (2026-10-20)

Commit su `integrazione-editoriale` (tra parentesi le prove della suite a quel commit):
- 5ae0bda (560) punto 1: pacchetto da 28 file verificato, nessuna modifica (D3);
- 2787ade (560) punto 2: aggiunte da `motore` adattate ai nomi del pacchetto (D5);
- 1b1717c (579) punto 3: macchina degli stati, struttura automatica, nessun documento prima (D6);
- 820a4e1 (592) punto 4: recinto, hook e cartella unica (D7);
- 3070050 (601) punto 5: ruoli, controllo per fase e un ruolo per sessione (D8);
- 0c74646 (611) punto 6: agenti, capsule, consumo, output compatto (D9);
- 12dd48a (623) punto 7: anti-IA e correttore (D10);
- 3270e84 (628) punto 8: pausa di lettura (D11);
- 7770e6c (632) punto 9: prove dei due rami unite (D12);
- 078b9b3 (632) punto 10: attribuzioni e analisi dei repository (D13);
- 06cbb70 (633) punto 8b: le note della pausa di lettura arrivano allo scrittore con `zb prepara` (D16).
Punto 11 (D14), nel commit che porta questo file: `docs/INFRASTRUTTURA_COMPLETA.md` dal generatore, guida (md e pdf),
README, PROCEDURA, STATO_ATTUALE, AVANZAMENTO_LAVORO, questo file e `motore/report-motore.md`; nomi
`formule_catalogo_per_mille` corretti; `[--ruolo R]` nell'uso di `zb avvio`: commit 286f793 (633).
- 2ed341e (637) punto 12: `avvio_motore()` di ccr tenuta identica; sezione di prove `avvio motore` (D15);
- 05facce (637) `CLAUDE.md` allineato al flusso attuale (D17);
- 951a42c (637) subagenti (12) e capsula (120-250 parole) nei file del pacchetto (D18).
Nel commit che porta questo file: guida (md e pdf), STATO_ATTUALE, AVANZAMENTO_LAVORO, report, questo file,
`docs/INFRASTRUTTURA_COMPLETA.md` rigenerata.

## Punti aperti

1. Punti 11 e 12 fatti (286f793, 2ed341e); D17 e D18 fatti (05facce, 951a42c).
2. Dopo ogni passo `zb salva`: recinto, prove, commit e push; resoconto con hash, file e «branch allineato a origin».
3. Per l'autore (`docs/DA_VERIFICARE_AUTORE.md`): contrasto pacchetto/modo automatico (D4); sezione B del catalogo
   anti-IA; coppia «avvenire/avvenire» nei criteri del correttore; licenza di APODICTIC; verifica dei dati KDP
   (`ultima_verifica: null`, non verificati dall'autore); unione nel ramo `motore`.
4. Soglie anti-IA uguali per ogni genere, tarate sui mini-libri; vocabolario italiano vuoto finché non c'è un corpus
   (`docs/DA_FORNIRE.md`).
5. Divergenza lasciata visibile in `docs/ANALISI_REPOSITORY.md`: kindle-book-agency (D13).

## Prossimo passo

`zb salva` e controllo con `git status -sb` e `git log -1`. Dopo, l'autore legge
`docs/DA_VERIFICARE_AUTORE.md` e decide se unire il ramo nel `motore`.

## Ripartenza

```
pip install -r motore/requirements.txt
apt-get install -y hunspell hunspell-it hunspell-en-us poppler-utils
python3 motore/zb languagetool installa        # poi l'export di ZB_LANGUAGETOOL che stampa
python3 motore/zb lavoro motore                # solo se l'autore ha scritto «lavoro sul motore»
python3 -B motore/zb avvio                     # riga «Letto»
ZB_LANGUAGETOOL=<cartella>/lib python3 -B motore/zb prove
```
Frase di apertura: «Leggi motore/passaggio-di-consegne.md e docs/DECISIONI_INTEGRAZIONE.md e riprendi da lì».

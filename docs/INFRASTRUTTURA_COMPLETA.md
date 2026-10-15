# Infrastruttura del sistema casa editrice

Mappa di tutto ciò che sta sul ramo del motore, generata dai file stessi il 2026-10-15 (prima riga del docstring per
gli script, primo titolo per i documenti). Non è più una copia integrale: il testo di ogni file sta nel file. Le voci
della banca-voci non sono copiate qui (stanno nel loro repository). Esportazioni precedenti: storia git (commit 7f97ddb
e precedenti).

## 1. Come funziona, in breve

1. Briefing → `zb nuovo` apre `libri/<slug>/` (cartella unica) sul ramo del libro.
2. Percorso da casa editrice (`motore/editoriale/00-percorso.md`): struttura → documenti → pagina campione → stesura →
   revisione strutturale del manoscritto → line → copy → bozze → chiusura meccanica; ogni gate si apre con `zb pronto`
   e si chiude con `ok`, `avanti`, `correggi`.
3. Ruoli come subagenti (`motore/editoriale/agenti/`), uno per capitolo, contesto pulito; la sessione principale
   orchestra. Capsule, codex filtrato, canone e stato compatto riducono ciò che si legge.
4. Recinto: hook su Write/Edit/Bash, controllo pre-commit, `zb avvio`, `zb salva`.
5. Traduzione: `zb traduci` → `libri/<slug>/08-traduzione-<lingua>/`.
6. Comandi: `python3 motore/zb aiuto` (fonte unica `motore/dati/comandi.yaml`).

## 2. File del ramo del motore

| File | A cosa serve |
|---|---|
| `CLAUDE.md` | Regole di avvio |
| `docs/ANALISI_REPOSITORY.md` | Analisi dei repository esterni |
| `docs/ATTRIBUZIONI.md` | Attribuzioni |
| `docs/AVANZAMENTO_LAVORO.md` | Avanzamento del lavoro sul motore |
| `docs/DA_FORNIRE.md` | Da fornire (autore) |
| `docs/GUIDA_AL_SISTEMA.md` |  |
| `docs/GUIDA_AL_SISTEMA.pdf` | file binario |
| `docs/INFRASTRUTTURA_COMPLETA.md` | Infrastruttura completa del sistema casa editrice |
| `docs/PROMPT_NUOVA_CHAT.md` | PROMPT PER NUOVA CHAT DI CLAUDE CODE - ESEGUI TUTTO QUI |
| `docs/STATO_ATTUALE.md` | Stato attuale del motore (fotografia prima del lavoro) |
| `motore/PROCEDURA.md` | Procedura del motore |
| `motore/README.md` | Motore editoriale |
| `motore/passaggio-di-consegne.md` | Passaggio di consegne: motore |
| `motore/proposta-motore.md` | Motore editoriale — proposta |
| `motore/report-motore.md` | Report del motore editoriale |
| `motore/requirements.txt` | Dipendenze Python del motore (pip install -r motore/requirements.txt). Versioni con cui girano le prove (2026-10-15). |
| `motore/zb` | zb — comandi del motore editoriale (proposta B.4). Uso: python3 motore/zb <comando> [argomenti] |
| `motore/dati/antiia.yaml` | Soglie dell'audit anti-IA (script/antiia.py) e vocabolario per lingua. |
| `motore/dati/comandi.yaml` | Unica fonte dei comandi di zb: la leggono «zb aiuto» e «zb aiuto <comando>». |
| `motore/dati/hook-settings.esempio.json` | { |
| `motore/dati/hook.yaml` | Modalità di motore/script/hook_manoscritto.py (proposta C.4). |
| `motore/dati/kdp.yaml` | Direttive KDP in forma di dati (proposta A.2). |
| `motore/dati/libro.schema.yaml` | Schema di libro.yaml (proposta B.3). Formato degli schemi: vedi profilo.schema.yaml. |
| `motore/dati/lingue.yaml` | Lingue supportate dal motore: italiano e inglese. Profili editoriali in motore/editoriale/lingue/<codice>/ |
| `motore/dati/lista-nera.yaml` | Lista nera di base (proposta B.8, mod. 4): da riferimenti/05-critica-e-punteggio.md |
| `motore/dati/modelli-ruoli.yaml` | Modelli per ruolo: unica fonte (la legge «zb agenti attiva», che scrive «model:» negli agenti installati). |
| `motore/dati/nomi_vietati.txt` | Nomi che non devono comparire in motore/ (proposta B.9). |
| `motore/dati/parole-ammesse-it.txt` | Forme italiane valide che il dizionario Hunspell it_IT non riconosce (passo 7). |
| `motore/dati/profilo.schema.yaml` | Schema dei profili di genere (proposta B.6). Formato degli schemi del motore: |
| `motore/dati/stato.schema.yaml` | Schema di stato.yaml (proposta C.1). Formato degli schemi: vedi profilo.schema.yaml. |
| `motore/dati/struttura-libro.yaml` | Struttura standard di un libro (passo 6). La legge nuovo.py; la usano pulizia.py e PROCEDURA.md. |
| `motore/dati/verifiche-kdp.md` | Verifiche delle direttive KDP |
| `motore/editoriale/00-percorso.md` | Percorso di un libro |
| `motore/editoriale/LEGGIMI.md` | Livello editoriale del motore |
| `motore/editoriale/risparmio-token.md` | Risparmio di token e subagenti |
| `motore/editoriale/agenti/architetto-struttura.md` | --- |
| `motore/editoriale/agenti/capsula.md` | --- |
| `motore/editoriale/agenti/correttore-bozze.md` | --- |
| `motore/editoriale/agenti/correttore-italiano.md` | --- |
| `motore/editoriale/agenti/diagnosta.md` | --- |
| `motore/editoriale/agenti/direttore-editoriale.md` | --- |
| `motore/editoriale/agenti/editor-strutturale.md` | --- |
| `motore/editoriale/agenti/line-editor.md` | --- |
| `motore/editoriale/agenti/scrittore-voce.md` | --- |
| `motore/editoriale/anti-ia/catalogo-it.md` | Catalogo anti-IA per l'italiano |
| `motore/editoriale/comandi/diagnosi.md` | --- |
| `motore/editoriale/comandi/handover.md` | --- |
| `motore/editoriale/comandi/revisiona.md` | --- |
| `motore/editoriale/comandi/scrivi-capitolo.md` | --- |
| `motore/editoriale/correttore/criteri-correttore.md` | Criteri del correttore di italiano |
| `motore/editoriale/diagnosi/00-principi.md` | Diagnosi editoriale: principi |
| `motore/editoriale/diagnosi/01-contratto-del-libro.md` | Il contratto del libro |
| `motore/editoriale/diagnosi/02-passaggi-di-analisi.md` | Passaggi di analisi |
| `motore/editoriale/diagnosi/03-gravita-e-rapporto.md` | Gravità e rapporto editoriale |
| `motore/editoriale/lingue/traduzione.md` | Traduzione di un libro |
| `motore/editoriale/lingue/agenti/revisore-fedelta.md` | --- |
| `motore/editoriale/lingue/agenti/traduttore.md` | --- |
| `motore/editoriale/lingue/en/catalogo-anti-ia.md` | Anti-AI catalogue for English |
| `motore/editoriale/lingue/en/criteri-correttore.md` | Copyeditor criteria (English) |
| `motore/editoriale/lingue/en/glossario-editoriale.md` | Editorial glossary (English) |
| `motore/editoriale/lingue/en/lingua.yaml` | Language profile: English. Roles read these three files when the book's language (libro.yaml, «lingua») is en. |
| `motore/editoriale/lingue/it/glossario-editoriale.md` | Glossario editoriale (italiano) |
| `motore/editoriale/lingue/it/lingua.yaml` | Profilo di lingua: italiano. I ruoli leggono questi tre file secondo la lingua del libro (libro.yaml, «lingua»). |
| `motore/editoriale/ruoli/00-diagnosta.md` | Ruolo 0 - Diagnosta editoriale |
| `motore/editoriale/ruoli/01-direttore-editoriale.md` | Ruolo 1 - Direttore editoriale |
| `motore/editoriale/ruoli/02-architetto-struttura.md` | Ruolo 2 - Architetto della struttura |
| `motore/editoriale/ruoli/03-scrittore-voce.md` | Ruolo 3 - Scrittore con voce |
| `motore/editoriale/ruoli/04-editor-strutturale.md` | Ruolo 4 - Editor strutturale (piano di revisione) |
| `motore/editoriale/ruoli/05-line-editor.md` | Ruolo 5 - Line editor |
| `motore/editoriale/ruoli/06-correttore-italiano.md` | Ruolo 6 - Correttore di italiano (copyediting) |
| `motore/editoriale/ruoli/07-correttore-bozze.md` | Ruolo 7 - Correttore di bozze |
| `motore/editoriale/struttura/01-fase-struttura.md` | Fase STRUTTURA |
| `motore/editoriale/struttura/modelli/scaletta-capitolo.md` | Capitolo N - <titolo di lavoro |
| `motore/modelli/LEGGIMI.md` | {titolo} — LEGGIMI |
| `motore/modelli/briefing.md` | Briefing |
| `motore/modelli/conferme-autore.yaml` | Conferme dell'autore per la conformità KDP (proposta A.9). |
| `motore/modelli/cronologia.yaml` | Cronologia del libro (proposta B.2.1). Si compila nella fase dei documenti. |
| `motore/modelli/libro.yaml` | libro.yaml — schema in motore/dati/libro.schema.yaml (proposta B.3). |
| `motore/modelli/stato.yaml` | Stato del libro (proposta C.1). Lo scrive solo motore/script/fase.py. |
| `motore/profili/fantascienza.yaml` | Profilo di genere «fantascienza» — default per libro.yaml (proposta B.6). |
| `motore/profili/fantasy.yaml` | Profilo di genere «fantasy» — default per libro.yaml (proposta B.6). |
| `motore/profili/giallo.yaml` | Profilo di genere «giallo» — default per libro.yaml (proposta B.6). |
| `motore/profili/narrativa-letteraria.yaml` | Profilo di genere «narrativa-letteraria» — default per libro.yaml (proposta B.6). |
| `motore/profili/romance.yaml` | Profilo di genere «romance» — default per libro.yaml (proposta B.6). |
| `motore/profili/thriller.yaml` | Profilo di genere «thriller» — default per libro.yaml (proposta B.6). |
| `motore/profili/young-adult.yaml` | Profilo di genere «young-adult» — default per libro.yaml (proposta B.6). |
| `motore/prove/attesi.yaml` | Esiti attesi delle prove del motore sui due mini-libri inventati (proposta B.2.2, B.7). |
| `motore/prove/appendici/LEGGIMI.md` | Appendici di prova |
| `motore/prove/appendici/nota-in-piu.md` | Nota in più |
| `motore/prove/appendici/piantina-prova.svg` | <?xml version="1.0" encoding="UTF-8"?> |
| `motore/prove/appendici/soluzioni-prova.md` | Le soluzioni di prova |
| `motore/prove/banca-voci-prova/LEGGIMI.md` | Banca-voci di prova |
| `motore/prove/banca-voci-prova/indice.yaml` | Indice della banca-voci di prova (inventata) |
| `motore/prove/banca-voci-prova/voci/voce-di-prova/divieti.yaml` | Divieti della voce di prova (inventati): stile.py li aggiunge alle voci del libro, modalità avviso. |
| `motore/prove/banca-voci-prova/voci/voce-di-prova/scheda.md` | Voce di prova |
| `motore/prove/banca-voci-prova/voci/voce-incompleta/scheda.md` | Voce incompleta |
| `motore/prove/briefing/briefing-giallo.md` | Briefing |
| `motore/prove/esiti/banca-voci-ripristino.md` | Banca-voci: ripristino dal bundle e cartelle «materiali»: esito |
| `motore/prove/esiti/bleed.md` | Prova del bleed: esito |
| `motore/prove/esiti/correzioni-dopo-prova.md` | Correzioni dopo la prova romance: resoconto |
| `motore/prove/esiti/formato-esatto.md` | Formato esatto delle pagine: esito |
| `motore/prove/esiti/languagetool.md` | LanguageTool attivo nelle prove: esito |
| `motore/prove/esiti/passo-1.md` | Passo 1 — Fondamenta: esito |
| `motore/prove/esiti/passo-2.md` | Passi 1b e 2 — Prove ripetibili e controlli del testo: esito |
| `motore/prove/esiti/passo-2b.md` | Passo 2b — Rifiniture: esito |
| `motore/prove/esiti/passo-3.md` | Passo 3 — Stampa: esito |
| `motore/prove/esiti/passo-3b.md` | Passo 3b — Rifiniture: esito |
| `motore/prove/esiti/passo-4.md` | Passo 4 — Pubblicazione: esito |
| `motore/prove/esiti/passo-5.md` | Passo 5 — Conduzione: resoconto |
| `motore/prove/esiti/passo-5b.md` | Passo 5b — zb adotta: resoconto |
| `motore/prove/esiti/passo-6.md` | Passo 6 — struttura e pulizia: resoconto |
| `motore/prove/esiti/passo-7.md` | Passo 7 — ortografia: resoconto |
| `motore/prove/esiti/pdf-indipendente-dal-container.md` | Prove del PDF indipendenti dal container: esito |
| `motore/prove/esiti/recinto-libro.md` | Recinto sul libro: zb nuovo, hook di blocco, regola di avvio: esito |
| `motore/prove/esiti/solo-il-motore.md` | Solo il motore nel repository: esito |
| `motore/prove/esiti/voce-solo-schede.md` | Banca-voci con sole schede: esito |
| `motore/prove/esiti/voce.md` | Voci narrative dalla banca-voci: esito |
| `motore/prove/mini-libro/cronologia.yaml` | Cronologia del mini-libro giallo (inventata). |
| `motore/prove/mini-libro/libro.yaml` | Mini-libro di prova del motore (giallo). Tutto inventato: nessun riferimento a libri reali. |
| `motore/prove/mini-libro/nomi_propri.txt` | Sorvegna |
| `motore/prove/mini-libro/00-progetto/briefing.md` | Briefing |
| `motore/prove/mini-libro/02-bibbia/bibbia.md` | Bibbia — Prova di stampa |
| `motore/prove/mini-libro/03-architettura/piano-parole.md` | Piano parole — Prova di stampa |
| `motore/prove/mini-libro/03-architettura/scaletta.md` | Scaletta — Prova di stampa |
| `motore/prove/mini-libro/04-manoscritto/01-la-farmacia.md` | 1 |
| `motore/prove/mini-libro/04-manoscritto/02-l-officina.md` | 2 |
| `motore/prove/mini-libro/04-manoscritto/03-la-stazione.md` | 3 |
| `motore/prove/mini-libro/04-manoscritto/interludio-I.md` | *La vetrina* |
| `motore/prove/mini-libro-adozione/02-bibbia/bibbia.md` | Bibbia — Il faro spento |
| `motore/prove/mini-libro-adozione/03-architettura/manuale-di-stile.md` | Manuale di stile — Il faro spento |
| `motore/prove/mini-libro-adozione/03-architettura/scaletta.md` | Scaletta — Il faro spento |
| `motore/prove/mini-libro-adozione/04-manoscritto/01-il-faro.md` | 1. Il faro |
| `motore/prove/mini-libro-editoriale/LEGGIMI.md` | Mini-libro editoriale (prove) |
| `motore/prove/mini-libro-editoriale/briefing.md` | Briefing |
| `motore/prove/mini-libro-editoriale/capitoli/01-il-molo.md` | 1 |
| `motore/prove/mini-libro-editoriale/capitoli/02-il-registro.md` | 2 |
| `motore/prove/mini-libro-editoriale/capitoli/03-la-lanterna.md` | 3 |
| `motore/prove/mini-libro-editoriale/capsule/01.md` | Capsula 1 — La lanterna del molo |
| `motore/prove/mini-libro-editoriale/capsule/02.md` | Capsula 2 — La lanterna del molo |
| `motore/prove/mini-libro-editoriale/capsule/03.md` | Capsula 3 — La lanterna del molo |
| `motore/prove/mini-libro-editoriale/codex/molo.md` | Il molo |
| `motore/prove/mini-libro-editoriale/codex/ufficio-porto.md` | L'ufficio del porto |
| `motore/prove/mini-libro-editoriale/rapporti/bozze.md` | zb: ruolo=correttore-bozze; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/rapporti/piano-revisione-manoscritto.md` | zb: ruolo=editor-strutturale; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/rapporti/piano-revisione-struttura.md` | zb: ruolo=editor-strutturale; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/rapporti/rapporto-manoscritto.md` | zb: ruolo=diagnosta; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/rapporti/rapporto-struttura.md` | zb: ruolo=diagnosta; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/rapporti/copy/01.md` | zb: ruolo=correttore-italiano; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/rapporti/copy/02.md` | zb: ruolo=correttore-italiano; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/rapporti/copy/03.md` | zb: ruolo=correttore-italiano; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/rapporti/line/01.md` | zb: ruolo=line-editor; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/rapporti/line/02.md` | zb: ruolo=line-editor; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/rapporti/line/03.md` | zb: ruolo=line-editor; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/struttura/01-premessa.md` | Premessa e promessa al lettore — La lanterna del molo |
| `motore/prove/mini-libro-editoriale/struttura/02-logline-tema.md` | Logline e tema — La lanterna del molo |
| `motore/prove/mini-libro-editoriale/struttura/03-personaggi-chiave.md` | Personaggi chiave — La lanterna del molo |
| `motore/prove/mini-libro-editoriale/struttura/04-atti-svolte.md` | Macrostruttura e svolte — La lanterna del molo |
| `motore/prove/mini-libro-editoriale/struttura/05-scaletta.md` | Scaletta per capitolo — La lanterna del molo |
| `motore/prove/mini-libro-editoriale/struttura/06-sottotrame-temi.md` | Sottotrame e promesse — La lanterna del molo |
| `motore/prove/mini-libro-editoriale/struttura/07-tensione-ritmo.md` | Tensione e ritmo — La lanterna del molo |
| `motore/prove/mini-libro-editoriale/struttura/08-piano-parole.md` | Piano parole — La lanterna del molo |
| `motore/prove/mini-libro-editoriale/struttura/09-scelte-fisse.md` | Scelte fisse: punto di vista, tempo, voce — La lanterna del molo |
| `motore/prove/mini-libro-editoriale/traduzione-en/glossario.yaml` | Glossario della traduzione: un termine = una traduzione. |
| `motore/prove/mini-libro-editoriale/traduzione-en/guida-traduzione.md` | Guida di traduzione — La lanterna del molo (it → en) |
| `motore/prove/mini-libro-editoriale/traduzione-en/capitoli/01-il-molo.md` | 1 |
| `motore/prove/mini-libro-editoriale/traduzione-en/capitoli/02-il-registro.md` | 2 |
| `motore/prove/mini-libro-editoriale/traduzione-en/capitoli/03-la-lanterna.md` | 3 |
| `motore/prove/mini-libro-editoriale/traduzione-en/rapporti/fedelta.md` | zb: ruolo=revisore-fedelta; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/traduzione-en/rapporti/copy/01.md` | zb: ruolo=correttore-italiano; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/traduzione-en/rapporti/copy/02.md` | zb: ruolo=correttore-italiano; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/traduzione-en/rapporti/copy/03.md` | zb: ruolo=correttore-italiano; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/traduzione-en/rapporti/line/01.md` | zb: ruolo=line-editor; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/traduzione-en/rapporti/line/02.md` | zb: ruolo=line-editor; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/traduzione-en/rapporti/line/03.md` | zb: ruolo=line-editor; su=IMPRONTA |
| `motore/prove/mini-libro-editoriale/traduzione-en/ritraduzione/01.md` | 1 |
| `motore/prove/mini-libro-romance/cronologia.yaml` | Cronologia del mini-libro romance (inventata). |
| `motore/prove/mini-libro-romance/libro.yaml` | Mini-libro di prova del motore (romance). Tutto inventato: nessun riferimento a libri reali. |
| `motore/prove/mini-libro-romance/nomi_propri.txt` | Ardena |
| `motore/prove/mini-libro-romance/00-progetto/briefing.md` | Briefing |
| `motore/prove/mini-libro-romance/02-bibbia/bibbia.md` | Bibbia — Prova d'inchiostro |
| `motore/prove/mini-libro-romance/03-architettura/piano-parole.md` | Piano parole — Prova d'inchiostro |
| `motore/prove/mini-libro-romance/03-architettura/scaletta.md` | Scaletta — Prova d'inchiostro |
| `motore/prove/mini-libro-romance/04-manoscritto/01-la-pensione.md` | 1 |
| `motore/prove/mini-libro-romance/04-manoscritto/02-la-cantina.md` | 2 |
| `motore/prove/mini-libro-romance/04-manoscritto/03-capitolo-prova.md` | 3 |
| `motore/prove/pubblicazione/conferme-tutto-ok.yaml` | Conferme di prova: tutte date (percorso «tutto OK»). Inventate per le prove del motore. |
| `motore/prove/pubblicazione/scheda-giallo.md` | Scheda Amazon — Prova di stampa |
| `motore/prove/pubblicazione/scheda-romance.md` | Scheda Amazon — Prova d'inchiostro |
| `motore/script/adotta.py` | Adotta nel motore un libro già avviato (passo 5b). |
| `motore/script/agenti.py` | Subagenti e comandi di Claude Code per i rami dei libri (comando «zb agenti»). |
| `motore/script/antiia.py` | Audit anti-IA non distruttivo e vocabolario dai dati (comando «zb antiia»). |
| `motore/script/avvio.py` | Avvio obbligatorio prima di lavorare su un libro (proposta B.4, C.4, C.5). |
| `motore/script/capitolo.py` | Controlli di un capitolo in un colpo solo (proposta C.2). |
| `motore/script/capsula.py` | Capsule di continuità: 07-capsule/NN.md dopo ogni capitolo accettato, e il registro delle promesse. |
| `motore/script/codex.py` | Codex del libro: schede dei personaggi e dei luoghi in <libro>/02-bibbia/codex/, una per file. |
| `motore/script/compatto.py` | Stato compatto del libro: <libro>/stato-compatto.md, 15-20 righe (comando «zb compatto <libro>»). |
| `motore/script/compila.py` | Compone il manoscritto completo di un libro (proposta B.2, B.4). |
| `motore/script/comune.py` | Funzioni comuni del motore (proposta B.3, B.4, B.9). |
| `motore/script/conformita_kdp.py` | Controllo di conformità KDP, sezioni 1-15 (proposta A.3-A.6, A.9). |
| `motore/script/consumo.py` | Misura del consumo per sessione (comando «zb consumo»). Misura, non stima: righe e parole lette dai file. |
| `motore/script/conta.py` | Conteggio delle parole con il metodo unico (proposta B.5 regola 3). |
| `motore/script/continuita.py` | Controlli di continuità (proposta B.2.1). |
| `motore/script/fase.py` | Macchina a stati del libro (proposta C.1, adattata al processo del passo 5). Unico script che scrive stato.yaml. |
| `motore/script/hook_manoscritto.py` | Hook PreToolUse di Claude Code sul manoscritto (proposta C.4). |
| `motore/script/hook_recinto.py` | Hook PreToolUse di Claude Code: recinto sul libro attivo, in modalità BLOCCO. |
| `motore/script/hook_sessione.py` | Hook SessionStart di Claude Code (proposta C.4). Non blocca mai: esce sempre con 0. |
| `motore/script/impagina.py` | Impaginazione del PDF di stampa (proposta B.2, B.3). |
| `motore/script/kdp_verifica.py` | Verifica delle direttive KDP da parte dell'autore (proposta A.8). |
| `motore/script/languagetool.py` | Installazione stabile di LanguageTool per il livello (b) di «zb ortografia» (comando «zb languagetool»). |
| `motore/script/nuovo.py` | Crea un libro dal briefing (proposta B.4, C.1 fase «documenti», C.3). |
| `motore/script/ortografia.py` | Controllo ortografico del manoscritto (passo 7). Tre livelli. |
| `motore/script/pacchetto.py` | Pacchetto di pubblicazione: struttura di <libro>/06-pubblicazione/ (proposta A.5, A.6, A.9, B.4). |
| `motore/script/percorso.py` | Percorso da casa editrice (libri con «percorso: editoriale» in libro.yaml). Lo usa fase.py. |
| `motore/script/precommit.py` | Controllo pre-commit di git: il recinto vale anche per ciò che il recinto degli hook non vede (Bash, script). |
| `motore/script/prepara.py` | Preparazione di un capitolo per lo scrittore (comando «zb prepara <libro> <N>»). |
| `motore/script/prove.py` | Prove ripetibili del motore (comando «zb prove»). |
| `motore/script/prove_editoriale.py` | Prove del percorso da casa editrice (le lancia prove.py; da sola: python3 -B prove_editoriale.py). |
| `motore/script/pulizia.py` | Pulizia di un libro (passo 6). Di default solo ELENCO: non cancella nulla. |
| `motore/script/push.py` | Push del ramo corrente con ripiego (comando «zb push»). |
| `motore/script/recinto.py` | Controlla che i comandi del motore scrivano solo dentro il libro indicato (proposta B.9). |
| `motore/script/revisione.py` | Mostra un documento o i documenti di un gate in blocchi (proposta C.1, C.6). Sola lettura. |
| `motore/script/riciclo.py` | Anti-riciclo a 7 parole (proposta C.2). |
| `motore/script/ruolo.py` | Ruoli del percorso editoriale: chi può lavorare in quale fase, e la prima riga del suo rapporto. |
| `motore/script/salva.py` | Salvataggio con il recinto (comando «zb salva [<libro>] <messaggio>»): controllo, commit, push. |
| `motore/script/separazione.py` | Controlla che il motore non contenga libri (proposta B.9). |
| `motore/script/stile.py` | Controlli di stile (proposta B.3, B.6, C.2). |
| `motore/script/struttura.py` | Fase struttura del percorso editoriale: modelli dei nove file di 03-struttura/ e controlli meccanici. |
| `motore/script/traduci.py` | Traduzione di un libro (comando «zb traduci <libro> --a <lingua> …»). Tutto in <libro>/08-traduzione-<lingua>/. |
| `motore/script/valida_profili.py` | Valida i profili di genere di motore/profili/ (proposta B.2.2, B.6). |
| `motore/script/verifica_pdf.py` | Verifica del PDF di stampa (proposta A.4 sezione 11, A.7, B.2). |
| `motore/script/voce.py` | Voci narrative della banca-voci (comando «zb voce»). Sola lettura. |
| `motore/stampa/modello.css` | /* Foglio di stile parametrico del motore (proposta B.2). |
| `motore/stampa/print.js` | Render di un file HTML in PDF con Chromium (Playwright). Uso: node print.js <html> <pdf |
| `motore/stampa/svg_png.js` | Conversione SVG → PNG con Chromium (Playwright), per le immagini delle appendici. |
| `motore/stampa/font/EBGaramond-Italic.ttf` | file binario |
| `motore/stampa/font/EBGaramond-Regular.ttf` | file binario |
| `motore/stampa/font/EBGaramond-SemiBold.ttf` | file binario |
| `motore/stampa/font/FONTI.yaml` | Fonti dei font di stampa (proposta B.2.3). Solo fonti ufficiali con licenza OFL. |
| `motore/stampa/font/OFL.txt` | Copyright 2017 The EB Garamond Project Authors (https://github.com/octaviopardo/EBGaramond12) |

## 3. Dove cambiare cosa

| Voglio cambiare… | File |
|---|---|
| il percorso, i ruoli, i criteri | `motore/editoriale/` |
| i comandi | `motore/dati/comandi.yaml` e lo script indicato |
| i modelli per ruolo | `motore/dati/modelli-ruoli.yaml` |
| le soglie anti-IA | `motore/dati/antiia.yaml` |
| le lingue | `motore/dati/lingue.yaml`, `motore/editoriale/lingue/` |
| i valori di genere | `motore/profili/` |
| le regole KDP | `motore/dati/kdp.yaml` (verifica dell'autore: `zb verifica KDP fatta`) |

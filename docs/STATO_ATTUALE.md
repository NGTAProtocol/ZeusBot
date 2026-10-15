# Stato attuale del motore (fotografia prima del lavoro)

Data: 2026-10-15. Ramo motore @ `dce3774`. Fotografia scritta prima di qualsiasi modifica
(sezione 1 del lavoro sul motore). Nessun libro, nessun nome di libro o di autore reale.

## 1. Avvio

`zb avvio` senza libro sul ramo motore si ferma: «Uso: avvio.py <libro> (oppure ZB_LIBRO=<libro>)».
Non esiste un avvio per il lavoro sul motore: la riga «Letto» non si può ottenere. È il punto debole
«lavoro sul motore non verificabile» (sezione 3, punto 3).

## 2. Le 28 script di `motore/script/`

| Script | Cosa fa | Comandi zb | Decisione | Motivo |
|---|---|---|---|---|
| adotta.py | bozze di libro.yaml, stato, cronologia, nomi da documenti esistenti, con le fonti | `adotta` | tieni | serve per i libri avviati fuori dal motore; meccanico |
| avvio.py | controlli di avvio e riga «Letto» | `avvio` | tieni, estendi | verifica meccanica affidabile; manca l'avvio del motore, il controllo git dei file fuori dal libro, le capsule |
| capitolo.py | tutti i controlli di un capitolo, report | `capitolo`, `esito` (via fase.py) | tieni | meccanico |
| compila.py | manoscritto completo, sommario, appendici | `compila` | tieni | meccanico |
| comune.py | funzioni comuni (yaml, schema, git, unità, scrittura nel libro) | — (libreria) | tieni | base di tutte |
| conformita_kdp.py | conformità KDP, sezioni 1-15 | `kdp` | tieni | meccanico |
| conta.py | parole con il metodo unico | `conta` | tieni | meccanico |
| continuita.py | date, età, durate, cifre, grafie | `continuita` | tieni | meccanico |
| fase.py | macchina a stati: fasi e gate, unico script che scrive stato.yaml | `stato ok avanti correggi riapprova pronto esito fase` | tieni, estendi | va cablato il percorso da casa editrice (struttura, revisioni, line, copy, bozze) |
| hook_manoscritto.py | hook PreToolUse: avviso sulle scritture nel manoscritto senza `zb avvio` | `hook` (configurazione) | tieni | il riconoscimento delle scritture Bash si riusa nel recinto |
| hook_recinto.py | hook PreToolUse: blocco delle scritture fuori dal libro attivo; `zb lavoro` | `lavoro`, `hook` | tieni, estendi | vede solo Write/Edit: va esteso a Bash |
| hook_sessione.py | hook SessionStart: session_id e compattazione | `hook` | tieni | piccolo e affidabile |
| impagina.py | PDF di stampa con Chromium | `impagina` | tieni | meccanico |
| kdp_verifica.py | registra la verifica KDP fatta dall'autore | `verifica KDP …` | tieni | unico punto che scrive `ultima_verifica` |
| nuovo.py | crea il libro dal briefing | `nuovo` | tieni, estendi | deve creare `03-struttura/` e aprire la fase struttura |
| ortografia.py | Hunspell, LanguageTool, checklist | `ortografia` | tieni, estendi | manca l'inglese; livello b da rendere stabile |
| prove.py | suite sui mini-libri | `prove` | tieni, semplifica | stampa oltre 450 righe: va portato a ≤ 40 righe con report a parte |
| pulizia.py | elenco di temporanei e copie | `pulizia` | tieni | non cancella senza `--applica` |
| push.py | push con ripiego | `push` | tieni | meccanico |
| recinto.py | i comandi scrivono solo nel libro (copia, fotografia, confronto) | `recinto`, `prove` | tieni | prova vera del recinto degli script |
| revisione.py | documenti di un gate in blocchi | `revisione`, `avanti` (via fase.py) | tieni | sola lettura |
| riciclo.py | anti-riciclo a 7 parole (riscrittura) | `riciclo` | tieni | meccanico |
| separazione.py | il motore non contiene libri né nomi vietati | `separazione`, `prove` | tieni, estendi | controlla solo `motore/`: non vede `docs/` e `CLAUDE.md` |
| stile.py | frase media, dialogo, lista nera, tetti, similitudini | `stile`, `capitolo` | tieni, estendi | qui va l'audit anti-IA non distruttivo |
| valida_profili.py | valida i profili di genere | `profili` | tieni | meccanico |
| verifica_pdf.py | verifica del PDF | `pdf` | tieni | meccanico |
| voce.py | banca-voci in sola lettura | `voce` | tieni | meccanico |

Nessuna script da eliminare o accorpare: ognuna è usata da un comando o da un'altra script, e le
verifiche meccaniche (avvio, stato, esito, continuita, ortografia, compila, impagina, pdf, pacchetto,
kdp) sono quelle da tenere. Il punto «accorpa» riguarda la logica, non i file: il riconoscimento delle
scritture Bash di `hook_manoscritto.py` si riusa in `hook_recinto.py` invece di essere scritto due volte.

## 3. Punti deboli noti (con la prova)

| # | Punto debole | Dove si vede |
|---|---|---|
| 1 | Il recinto non vede Bash | `hook_recinto.py`: legge solo `file_path`/`notebook_path`; la configurazione lo aggancia a `Write\|Edit\|MultiEdit\|NotebookEdit` |
| 2 | Hook spenti sul ramo motore | nessun `.claude/settings.json`: voluto, ma nessuna prova lo dichiara come stato verificato del ramo |
| 3 | «Lavoro sul motore» non verificabile | `zb lavoro motore` scrive solo `<git-dir>/zb-lavoro`; `zb avvio` senza libro si ferma; nessun controllo su ciò che il commit tocca |
| 4 | Report ogni 5 scambi non controllato | solo una regola in `CLAUDE.md` riga 17; nessuno script lo verifica |
| 5 | Due scale di precedenza | `proposta-motore.md` righe 707 e 1262 (senza briefing e voce, con le «skill dell'autore»); la scala unica è in `editoriale/LEGGIMI.md` |
| 6 | Skill nominate ma assenti | `editoriale/ruoli/02-architetto-struttura.md` riga 28 (`rotte-narrative`); `proposta-motore.md` righe 1027-1028 (`.claude/skills/…`) |
| 7 | Voci copiate e nomi reali nei docs del ramo motore | `docs/INFRASTRUTTURA_COMPLETA.md` copia la banca-voci (68 righe con nomi reali negli slug); `docs/ESPORTAZIONE_COMPLETA_1.md` e `_5.md`; `motore/passaggio-di-consegne.md` riga 27; `motore/prove/esiti/banca-voci-ripristino.md` |
| 8 | README sbagliato sugli hook | `motore/README.md` riga 68: «oggi in modalità avviso, non attivi»; il recinto è in blocco |
| 9 | PROCEDURA.md senza recinto | sezione 10 descrive solo `hook_sessione` e `hook_manoscritto` |
| 10 | Comandi elencati tre volte | `motore/zb` (AIUTO), `motore/README.md` («Comandi»), `docs/INFRASTRUTTURA_COMPLETA.md` e `docs/GUIDA_AL_SISTEMA.md` |
| 11 | Esportazioni doppie in docs/ | `docs/ESPORTAZIONE_COMPLETA_1…6.md` (30.152 righe) ripetono il contenuto del repository, come `INFRASTRUTTURA_COMPLETA.md` |
| 12 | Arcaismi e LEGGIMI duplicati | rimandi a «proposta B.4», «passo 5b» nei docstring; due LEGGIMI con ruoli diversi (`modelli/LEGGIMI.md` modello del libro, `editoriale/LEGGIMI.md` livello editoriale) e `editoriale/LEGGIMI.md` dice «va copiata in motore/editoriale/» (istruzione d'installazione rimasta) |
| 13 | requirements mancante | nessun `requirements.txt`; PyMuPDF e markdown si installano a mano (README, «Ambiente») |
| 14 | Prove non automatiche | nessun controllo le lancia prima del push; `zb push` non le esegue |
| 15 | Modello libro.yaml senza appendici | `motore/modelli/libro.yaml` non ha il campo `appendici` (documentato in PROCEDURA.md §7) |
| 16 | Dati KDP con `ultima_verifica: null` | `motore/dati/kdp.yaml` riga 5: mai verificati dall'autore |
| 17 | Percorso senza struttura né revisioni | `fase.py`: fasi documenti → pagina_campione → stesura → chiusura; nessuna fase struttura, revisione strutturale, line, copy, bozze |
| 18 | Livello editoriale incompleto | `motore/editoriale/` ha 14 file; mancano diagnosi, ruolo diagnosta, agenti, risparmio-token (il file di riferimento editoriale_tutto.md / editoriale.zip non è nel repository) |
| 19 | Una sola lingua | `lingua: it` fisso in `nuovo.py`; nessun profilo inglese, nessuna traduzione |
| 20 | Output lungo | `zb prove` stampa una tabella di oltre 450 righe |

## 4. Prove prima del lavoro

Ambiente del container nuovo: installati `pymupdf`, `markdown`, `hunspell`, `hunspell-it`; LanguageTool
non impostato. L'esito della suite di base è in `docs/AVANZAMENTO_LAVORO.md`, sezione 1.

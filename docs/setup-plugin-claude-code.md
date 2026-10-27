# Setup di 4 strumenti per Claude Code: audit di sicurezza

Data: 2026-10-27. Ambiente: sessione Claude Code in un container cloud temporaneo (non il computer dell'autore).
Esito in breve: **audit fatto su tutti e 4.** Graphify installato dopo «installa Graphify» (sezione dedicata). Prima, dopo l'ok dell'autore («installa quello che devi installare»):
**installati Ponytail 5.3.2 e Agent Skills 0.6.13** (scope utente del container, vedi «Aggiornamento:
installazione»); Graphify (DUBBIO) e OmniRoute (NON INSTALLARE) **non installati**, in attesa di conferma esplicita.

## Aggiornamento: installazione (2026-10-27)

Comandi eseguiti nel container (CLI `claude` 2.1.311, equivalenti ai comandi `/plugin`):
```
claude plugin marketplace add 'DietrichGebert/ponytail#v5.3.2' --scope user
claude plugin install ponytail@ponytail --scope user
claude plugin marketplace add 'addyosmani/agent-skills#0.6.13' --scope user
claude plugin install agent-skills@addy-agent-skills --scope user
```
Verifica (`claude plugin list`): `ponytail@ponytail` 5.3.2 abilitato; `agent-skills@addy-agent-skills` 0.6.13
abilitato; in cache i comandi build, code-simplify, constraints, plan, review, ship, spec, test, webperf.
File modificati fuori dal repository: `/root/.claude/settings.json` (`enabledPlugins`, `extraKnownMarketplaces`),
`/root/.claude/plugins/` (cache). Opzioni utente di Ponytail (webhook ecc.) lasciate vuote: nessun dato esce.

**Limite**: è il `~/.claude` del container cloud, che sparisce a fine sessione; non è il tuo computer né le
prossime sessioni. Per averli ovunque: digita i comandi `/plugin` delle sezioni 1 e 2 nel tuo Claude Code, oppure
dichiararli nello scope «project» (`.claude/settings.json` del repo): è una modifica al motore, quindi solo dopo
«lavoro sul motore», e per Ponytail con il limite sui subagenti descritto sotto.

## Aggiornamento: Graphify installato (2026-10-27, dopo «installa Graphify»)

Comandi eseguiti (da una cartella dello scratchpad, **non** dal repository):
```
cp -p ~/.claude/settings.json <scratchpad>/backup-claude/settings.json.bak-20261027   # ~/.claude/CLAUDE.md non esisteva
uv tool install graphifyy==0.9.96
graphify install
```
- Versione: `graphify 0.9.96`; i 233 file installati in `~/.local/share/uv/tools/graphifyy/` sono identici al
  wheel esaminato (sha256 `bbef4c79…`).
- Scritto da `graphify install`, esattamente come previsto dall'audit: `~/.claude/skills/graphify/SKILL.md`,
  `~/.claude/skills/graphify/references/` (8 file), `~/.claude/skills/graphify/.graphify_version` (`0.9.96`) e
  `~/.claude/CLAUDE.md` creato con la sola sezione `# graphify` (3 righe). `~/.claude/settings.json` **invariato**
  (confrontato col backup); nessun hook installato.
- **Non** eseguito `graphify claude install`: in ZeusBot modificherebbe `CLAUDE.md` e `.claude/settings.json` del motore.
- Prova su una cartella di prova (`<scratchpad>/prova-graphify`, 3 file Python): `graphify update .` → «9 nodes,
  14 edges, 2 communities», creati `graphify-out/graph.json`, `graph.html`, `GRAPH_REPORT.md`; `graphify query`
  e `graphify path "main" "query"` (main → UserService → .get_user → query, 3 passi) rispondono correttamente.
  Nessuna chiave API usata, nessun invio esterno (solo estrazione AST locale).
- La skill `graphify` risulta caricata nella sessione. Il comando `/graphify` completo non l'ho lanciato da qui:
  scrive `graphify-out/` nella cartella corrente, che in questa sessione è il repository ZeusBot (fuori dal
  recinto). Va provato aprendo Claude Code in una cartella di prova.
- Limite: anche questa installazione sta nel container cloud e sparisce a fine sessione.

## Rete: sbloccare GitHub (sito e API)

Il proxy di questo ambiente rifiuta `api.github.com` e `github.com` via HTTPS (HTTP 403); `git clone` invece passa.
Non posso cambiarlo da dentro la sessione: lo cambi tu nelle impostazioni dell'ambiente cloud (menu dell'ambiente
nella barra del titolo della sessione → Edit → Network access): scegli un livello più ampio, oppure aggiungi
`api.github.com` e `github.com` (ed eventualmente `raw.githubusercontent.com`) agli «Allowed domains», lasciando
spuntato «Allow package managers». Istruzioni: https://code.claude.com/docs/en/cloud-environments#network-access.
Vale dalle sessioni nuove. Le operazioni GitHub del repository (PR, issue) passano comunque dagli strumenti GitHub
integrati della sessione, limitati a `ngtaprotocol/zeusbot`.

| Strumento | Verdetto | Versione bloccata |
|---|---|---|
| Ponytail | **OK** (con una riserva d'uso per ZeusBot) | tag `v5.3.2` = commit `16352ac229eb08a9598dcae48fe9f2b342567d86` |
| Agent Skills (Addy Osmani) | **OK** (via plugin; `npx skills` con riserva) | tag `0.6.13` = commit `aeac41d4d005999432bb7312f7ff06383a91d59d` |
| Graphify | **DUBBIO** (codice pulito, ma comportamenti da approvare) | PyPI `graphifyy==0.9.96` = tag `v0.9.96` = commit `dac063456bc1f5d92354ec3936fd9dd1513a83f3` |
| OmniRoute | **NON INSTALLARE** (per l'uso con l'abbonamento Claude) | npm `omniroute@3.8.52` (repo: ramo `release/v3.8.53`, HEAD `1ac00b05e2d507d416a3e9c4c278ab625ce1dbf2`) |

## Metodo e limiti

- Codice ottenuto con `git clone` (solo lettura, nessun hook git eseguito, niente `npm install`/`pip install`).
  Pacchetti npm/PyPI scaricati come archivi con `curl` ed estratti senza eseguirli.
- **Non verificabile con i miei strumenti**: pagine web e API di GitHub erano bloccate dal proxy (HTTP 403).
  Quindi **non ho visto** data di creazione «ufficiale» del repository, stelle, numero di fork, badge di verifica
  dell'owner, né il redirect HTTP di un repository trasferito. Al loro posto ho usato la storia git: data del
  primo commit, numero di commit, data dell'ultimo commit, licenza nel file `LICENSE`.
- Il controllo «typosquatting» si basa su: owner richiesto = owner clonato; campi `repository`/`homepage` nei
  manifest; per i pacchetti, confronto file per file con il repository (fatto per graphifyy).

---

## 1) Ponytail — OK

**Identità**
- Repository: `DietrichGebert/ponytail` (owner richiesto, non un fork). Primo commit 2026-06-12 (DietrichGebert),
  363 commit, ultimo commit 2026-10-18. Licenza MIT (`LICENSE`, «Copyright (c) 2026 DietrichGebert»).
- `.claude-plugin/marketplace.json`: marketplace `ponytail`, plugin `ponytail`, `source: "./"` (il plugin è il
  repository stesso, nessun download da altrove). `package.json`: `@dietrichgebert/ponytail` 5.3.2, `repository`
  = `github.com/DietrichGebert/ponytail`. Nessuno script `preinstall`/`postinstall`/`install`.

**Versione**: tag `v5.3.2` (`16352ac`). HEAD (`09c434a`) ha 8 commit in più: ho letto il diff di hook e skill
(`hooks/claude-codex-hooks.json` timeout 5→15 s; `ponytail-activate.js` e `ponytail-map.js` timeout/buffer;
`hooks/band/register.tsx` 41 righe). Nessuna modifica rilevante per la sicurezza.

**File letti per intero**: `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`, `package.json`,
`hooks/claude-codex-hooks.json`, `hooks/claude-band.json`, `hooks/ponytail-activate.js`, `hooks/ponytail-config.js`,
`hooks/ponytail-runtime.js`, `hooks/ponytail-mode-tracker.js`, `hooks/ponytail-subagent.js`, `hooks/ponytail-map.js`,
`hooks/ponytail-statusline.sh`, `skills/ponytail/SKILL.md`.
**Letti in parte**: `hooks/band/register.tsx` (righe 85-200 e tutti i punti con `process.run`, `fs`, `http`, `env`),
`hooks/band/metrics.ts` (righe 290-317, webhook), `hooks/ponytail-band-import.js` (righe 190-274).
**Solo scansione con grep** (rete, exec, eval, base64, credenziali, istruzioni tipo «ignora/bypass»): le altre 5
`skills/*/SKILL.md`, `hooks/ponytail-instructions.js`, `hooks/band/board.ts`, `scripts/*.js`.
**Non letti**: `benchmarks/`, `tests/`, `docs/`, `i18n/`, `examples/`, file per altri editor (Cursor, Codex, Gemini…).

**Cosa fa all'avvio (hook registrati dal plugin)**
- `SessionStart` → `ponytail-activate.js`: scrive `~/.claude/.ponytail-active` e
  `~/.claude/ponytail-modes/<sha256 del progetto>`; inietta le regole «lazy senior dev» e una mappa del codice
  (`git ls-files` + regex, max 2000 caratteri); **legge** `~/.claude/settings.json` solo per il campo
  `statusLine`; copia `ponytail-statusline.sh` in `~/.claude/`. Se manca la statusline, chiede all'agente di
  **proporre** all'utente di aggiungerla a `settings.json` (riga 149-153): proposta, non modifica automatica.
- `SubagentStart` → `ponytail-subagent.js`: inietta le stesse regole in **ogni** subagente (salvo
  `PONYTAIL_SUBAGENT_MATCHER`).
- `UserPromptSubmit` → `ponytail-mode-tracker.js`: legge il prompt solo per riconoscere `/ponytail …`;
  `/ponytail default X` scrive `~/.config/ponytail/config.json`.
- Modulo «band» (`hooks/band/register.tsx`): dopo ogni turno scrive una riga CSV (costo, token, turni) in
  `~/.config/ponytail/band/<progetto>.csv` e `board.html`; legge il transcript con `grep` per il nome del modello.

**Rete**: unica chiamata esterna è il **webhook opzionale** (`plugin.json` → `userConfig.webhookUrl`, vuoto di
default; `metrics.ts:305-317` accetta solo https, o http su localhost). Con il campo vuoto nulla esce dal computer.
**Credenziali**: nessuna lettura di `~/.ssh`, `~/.aws`, `.env`, token o cookie. Il `webhookToken` è dichiarato
`sensitive` (portachiavi di sistema).
**Offuscamento / codice remoto**: nessuno (`eval`, `base64`, download+esecuzione assenti; `vm.runInNewContext`
in `ponytail-subagent.js` serve solo a limitare il tempo di una regex).
**Istruzioni all'agente**: nessuna richiesta di ignorare regole o disattivare conferme.

**Riserva per ZeusBot**: l'hook `SubagentStart` metterebbe le regole «scrivi il minimo codice» anche negli agenti
che scrivono prosa (`scrittore-voce`, `line-editor`, …). Per questo progetto conviene installarlo **solo a livello
utente con `PONYTAIL_SUBAGENT_MATCHER`** impostato (es. `general|explore`) oppure disattivarlo nei progetti di libri
(`PONYTAIL_DEFAULT_MODE=off`, documentato in `hooks/ponytail-config.js`).

**Comandi da digitare tu** (in Claude Code, sul tuo computer; `#ref` è la sintassi documentata per bloccare un tag,
code.claude.com/docs/en/plugins/install):
```
/plugin marketplace add DietrichGebert/ponytail#v5.3.2
/plugin install ponytail@ponytail
```

---

## 2) Agent Skills (Addy Osmani) — OK

**Identità**
- Repository: `addyosmani/agent-skills`. Primo commit 2026-02-15 (Addy Osmani), 702 commit, ultimo 2026-10-13
  («bump plugin manifests to 0.6.13»). Licenza MIT («Copyright (c) 2025 Addy Osmani»).
- `.claude-plugin/marketplace.json`: marketplace `addy-agent-skills`, plugin `agent-skills` 0.6.13,
  `source: {source: github, repo: addyosmani/agent-skills}`.

**Versione**: tag `0.6.13` = HEAD `aeac41d`. **Attenzione**: la voce del plugin nel marketplace non ha `ref`/`sha`,
quindi anche se blocchi il marketplace al tag, il plugin viene preso dal ramo predefinito. Oggi coincide con
`0.6.13`; per un blocco reale serve verificare dopo l'installazione che la versione sia 0.6.13.

**Comandi esistenti** (verificati nei file, non a memoria): in `.claude/commands/` ci sono `spec.md`, `plan.md`,
`build.md`, `test.md`, `review.md`, `code-simplify.md`, `ship.md` (più `constraints.md`, `webperf.md`).
Tutti e 7 i comandi richiesti esistono. Da plugin compaiono col prefisso `agent-skills:` se c'è un conflitto di nomi.

**File letti per intero**: `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`, `plugin.json`, i 7
comandi sopra, `hooks/session-start.sh`, `hooks/sdd-cache-pre.sh`, `hooks/sdd-cache-post.sh`,
`skills/idea-refine/scripts/idea-refine.sh`; `skills/browser-testing-with-devtools/SKILL.md` righe 25-45.
**Letto in parte**: `hooks/simplify-ignore.sh` (intestazione). README: righe con i comandi di installazione.
**Solo scansione con grep**: tutte le 25 `skills/*/SKILL.md` (8070 righe con comandi e agenti), `agents/*.md`,
`references/*.md` — cercati curl/wget/pipe a shell, eval, base64, «ignore instructions», bypass, `settings.json`,
`~/.claude`, `.ssh`, `.aws`, force-push, `rm -rf`, e tutti gli URL. **Non** ho letto riga per riga ogni SKILL.md.
**Non letti**: `evals/`, `docs/`, `scripts/` di validazione.

**Esito**
- **Nessun hook attivato dal plugin**: non esiste `hooks/hooks.json` e `plugin.json` non dichiara hook;
  `session-start.sh` lo dice esplicitamente (righe 5-8). Gli script in `hooks/` sono opzionali, da collegare a mano.
  (Se collegati: `sdd-cache-*` fanno richieste HEAD verso gli URL già usati da WebFetch e salvano in
  `.claude/sdd-cache/`; nulla verso domini propri.)
- Nessuna rete, nessuna lettura di credenziali, nessun offuscamento nei file di installazione.
- Skill e comandi: nessuna istruzione a ignorare regole o saltare conferme; al contrario chiedono conferma
  (`/build auto` si ferma per azioni irreversibili, segreti, deploy). Unico punto da sapere:
  `browser-testing-with-devtools` suggerisce di aggiungere un server MCP con `npx -y chrome-devtools-mcp@latest`
  (non bloccato a una versione): lo fai tu, se vuoi.
- Per ZeusBot: `/plan` di questo plugin scrive `tasks/plan.md`, `/spec` scrive `SPEC.md` nella radice: fuori dal
  recinto del libro. Usarli solo in sessioni «lavoro sul motore» o in altri progetti.

**`npx skills add addyosmani/agent-skills --list`: non eseguito.** Esegue un'altra CLI, il pacchetto npm `skills`
(1.7.4, repo `vercel-labs/skills`, pubblicata il 2026-10-19: meno di due settimane fa), che non è tra i 4 strumenti
da verificare. Dall'archivio scaricato (`package/dist/cli.mjs` righe 2798-2846): invia **telemetria** a
`https://www.skills.sh/tele/t` e una richiesta di «audit» a `https://www.skills.sh/tele/audit`, disattivabili con
`DISABLE_TELEMETRY=1` o `DO_NOT_TRACK=1`. Il resto della CLI (~9000 righe) non l'ho letto. Cosa installerebbe
(dai file del repo): le 25 skill di `skills/` (api-and-interface-design, browser-testing-with-devtools,
ci-cd-and-automation, code-review-and-quality, code-simplification, constraint-driven-development,
context-engineering, debugging-and-error-recovery, deprecation-and-migration, documentation-and-adrs,
doubt-driven-development, frontend-ui-engineering, git-workflow-and-versioning, idea-refine,
incremental-implementation, interview-me, observability-and-instrumentation, performance-optimization,
planning-and-task-breakdown, security-and-hardening, shipping-and-launch, source-driven-development,
spec-driven-development, test-driven-development, using-agent-skills). Strada consigliata: il plugin.

**Comandi da digitare tu**:
```
/plugin marketplace add addyosmani/agent-skills#0.6.13
/plugin install agent-skills@addy-agent-skills
```
Poi controlla con `/plugin` che la versione installata sia 0.6.13.

---

## 3) Graphify — DUBBIO

**Repository canonico**: `Graphify-Labs/graphify`. Prove: `README.md` riga 190 («The official source repository is
Graphify-Labs/graphify»); `pyproject.toml` `[project.urls] Repository = https://github.com/Graphify-Labs/graphify`.
`safishamsi/graphify` clonato dà **la stessa identica storia** (stesso HEAD `dac0634`, 2584 commit, primo commit
2026-04-03 di «Safi»): è coerente con un repository trasferito da `safishamsi` all'organizzazione (il redirect HTTP
non l'ho potuto vedere, API bloccate). Licenza: Apache-2.0 (`LICENSE`) più `LICENSE-MIT`.

**PyPI `graphifyy`** (due «y»): ultima versione 0.9.96 (2026-10-26), 264 release, prima release 2026-04-04;
`project_urls` → Graphify-Labs/graphify. Wheel `graphifyy-0.9.96-py3-none-any.whl`, sha256
`bbef4c79b5905f45e384a7ca49417cd6c131d4774f280037159dd6cf4c425e29`: **tutti i 233 file del pacchetto `graphify/`
sono identici byte per byte** al tag `v0.9.96` del repository. È il pacchetto legittimo. Il nome PyPI `graphify`
(una «y») non l'ho potuto interrogare (risposta senza dati). Nota: nel repo esiste un tag `v1.0.0` vecchio
(2026-04-05, commit `0a31c08`), non è una release più nuova.
Requisito: Python ≥ 3.10 (`requires-python`). Dipendenze: networkx, numpy, rapidfuzz, pyyaml, tree-sitter e
grammatiche (tutte librerie note); nessuno script di installazione (build `setuptools`, si installa da wheel).

**File letti**: `pyproject.toml` (righe 1-80), `graphify/install.py` (funzioni `install`, `_copy_skill_file`,
`_write_version_stamp`, `_skill_registration`, `_claude_pretooluse_hooks`, `_strip_graphify_hooks`,
`claude_install`, `_install_claude_hook`, `_read_settings_for_merge`, `_write_settings_with_backup`,
`_refuse_to_modify`, configurazione `claude`), `graphify/always_on/claude-md.md`, `graphify/cli.py`
`_run_hook_guard` (righe 1143-1230), `graphify/llm.py` righe 87-262 (provider), `graphify/querylog.py` righe 1-40,
`graphify/skill.md` righe 53-100 e 165-172. **Solo grep** su tutto `graphify/*.py`: URL, `urllib`/`socket`/`requests`,
`eval`/`exec`/`b64decode`/`shell=True`/`os.system`, `.ssh`/`.aws`/cookie, telemetria. **Non letti**: il resto di
`cli.py` (5463 righe), `llm.py`, `extract*`, `serve.py`, `security.py` (solo intestazione), `skills/claude/references/*`.

**Cosa scrive `graphify install`** (piattaforma claude, globale; codice in `install.py` 948-1025, 329-408):
1. `~/.claude/skills/graphify/SKILL.md` (copia di `graphify/skill.md`, 793 righe) + cartella
   `~/.claude/skills/graphify/references/` (8 file: add-watch, exports, extraction-spec, github-and-merge, hooks,
   query, transcribe, update) + `~/.claude/skills/graphify/.graphify_version`. Se esiste uno SKILL.md diverso, ne
   salva una copia `.bak`.
2. In `~/.claude/CLAUDE.md` aggiunge (o aggiorna) questa sezione, esatta (`install.py` 577-585):
   ```
   # graphify
   - **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
   When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.
   ```
   **Non** tocca `settings.json`.

**Gli hook PreToolUse li scrive un altro comando**: `graphify claude install` (`claude_install`, righe 2183-2232),
nel **progetto corrente**: aggiunge la sezione `graphify/always_on/claude-md.md` al `CLAUDE.md` del progetto e in
`.claude/settings.json` due hook (backup automatico in `settings.json.graphify-bak`):
```json
{"matcher": "Bash|Grep", "hooks": [{"type": "command", "command": "<percorso>/graphify hook-guard search", "timeout": 10}]},
{"matcher": "Read|Glob", "hooks": [{"type": "command", "command": "<percorso>/graphify hook-guard read", "timeout": 10}]}
```
L'hook (`cli.py` 1143-1230) non blocca: se esiste `graphify-out/graph.json` suggerisce di usare `graphify query`
(blocca la prima lettura solo in modalità `--strict`, opzionale). **In ZeusBot non va eseguito**: modificherebbe
`CLAUDE.md` e `.claude/settings.json` del motore, che già contiene gli hook del recinto.

**Rete e credenziali**
- Nessuna telemetria (`querylog.py`: registro delle query locale e spento di default). Nessuna lettura di
  `~/.ssh`/`~/.aws`: anzi `detect.py` (righe 116-143) esclude queste cartelle e i file `.netrc`, `.npmrc`, ecc.
- Estrazione semantica (documenti, PDF, immagini): se `GEMINI_API_KEY` o `GOOGLE_API_KEY` sono impostate, la skill
  usa **Gemini** e quindi invia il contenuto a Google (`skill.md` riga 170); altrimenti la fa l'agente stesso.
  Il codice sorgente è estratto in locale (AST), senza rete. Il CLI supporta anche altri provider (Anthropic,
  OpenAI, DeepSeek, Moonshot, Azure, Ollama, `claude-cli`) solo se scelti esplicitamente.

**Perché DUBBIO**
- `skill.md` righe 85-94 (Step 1): se `graphify` non è importabile, la skill fa eseguire all'agente
  `uv tool install --upgrade graphifyy` oppure `pip install graphifyy … --break-system-packages`, **senza versione
  e senza chiedere**: annulla il blocco di versione e può modificare il Python di sistema.
- Invio automatico a Gemini se nel tuo ambiente esiste già una chiave Google.
- Modifica permanente di `~/.claude/CLAUDE.md` (globale, vale per tutti i progetti).
Nessuno di questi è codice malevolo; sono azioni che devi approvare tu.

**Comandi proposti (da eseguire sul tuo computer, dopo il tuo ok)**
```
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.bak-$(date +%Y%m%d) 2>/dev/null
cp ~/.claude/settings.json ~/.claude/settings.json.bak-$(date +%Y%m%d) 2>/dev/null
uv tool install graphifyy==0.9.96      # oppure: pip install graphifyy==0.9.96
graphify install
```
Prova su una cartella di prova (fuori da ZeusBot): `mkdir /tmp/prova-graphify && cd /tmp/prova-graphify`, mettici
qualche file `.py`, apri Claude Code lì e digita `/graphify .` → deve creare `graphify-out/graph.json` e
`graphify-out/GRAPH_REPORT.md`. **Non eseguito qui** (vedi sotto).

---

## 4) OmniRoute — NON INSTALLARE (non toccato `~/.claude/settings.json`)

**Identità**
- Repository: `diegosouzapw/OmniRoute`. Primo commit 2026-02-18, 11 747 commit, ultimo 2026-10-27. Licenza MIT.
  Pacchetto npm `omniroute`: creato 2026-02-14, 291 versioni, ultima `3.8.52` (2026-10-19), maintainer
  `diegosouza.pw`; tarball 114 MB, integrità `sha512-R+GUs3vDWpX36n+oOwjRSJN/7dGoXC3ehSV7mSz41nZM4mFhUo2+YepYzXMk5Hf6sIwCKRpGBaPMDVR8xbvwew==`.
- **Segnale di provenienza da chiarire**: nel codice sorgente attuale `package.json` indica
  `repository: github.com/cheaper-inference/OmniRoute` (un'altra organizzazione), e il programma scarica le
  novità da `raw.githubusercontent.com/cheaper-inference/OmniRoute/main/news.json`
  (`src/shared/utils/releaseNotes.ts` riga 4); il pacchetto npm 3.8.52 invece indica ancora `diegosouzapw/OmniRoute`.
  Probabile trasferimento del progetto, ma non l'ho potuto verificare.

**Cosa esegue all'installazione**: `postinstall` = `node scripts/build/postinstall.mjs` (412 righe, letto fino a
riga ~200): copia/ricompila moduli nativi (`npm rebuild better-sqlite3`; su Android modifica
`~/.cache/node-gyp/.../common.gypi`). Non ho visto download di codice remoto nella parte letta, ma l'installazione
**esegue codice** e porta 101 dipendenze più 8 opzionali (fra cui `keytar`, `onnxruntime-node`, `wreq-js`: client
TLS usato per «provider OAuth e web-cookie»).

**Cosa modificherebbe in Claude Code** (`src/app/api/cli-tools/claude-settings/route.ts` righe 100-170,
`src/shared/services/claudeCliConfig.ts`): dalla dashboard scrive in `~/.claude/settings.json` →
`env.ANTHROPIC_BASE_URL` (l'indirizzo di OmniRoute) e `env.ANTHROPIC_AUTH_TOKEN` con **la chiave completa in
chiaro** (letta dal database), più eventualmente `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY`, i modelli
predefiniti e `API_TIMEOUT_MS`. Fa un backup prima. Da quel momento **tutto il traffico di Claude Code** (prompt,
codice, file letti) passa da OmniRoute.

**Credenziali e abbonamento Claude**
- `src/lib/oauth/constants/oauth.ts` righe 40-54: login OAuth su `claude.ai/oauth/authorize` con il client ID
  pubblico di Claude Code e gli scope `org:create_api_key`, `user:profile`, `user:inference`,
  `user:sessions:claude_code`, `user:mcp_servers`. In pratica OmniRoute si presenta come Claude Code per ottenere
  token del tuo abbonamento.
- I token stanno in un database SQLite locale; la cifratura è **spenta di default** (`.env.example` righe 93-96:
  «Leave empty to disable DB encryption», `STORAGE_ENCRYPTION_KEY=` vuoto).
- «Cloud sync» (`src/lib/cloudSync.ts`): spento finché non imposti `CLOUD_URL`/`NEXT_PUBLIC_CLOUD_URL`; se attivo
  invia la configurazione a quel server; dalla 3.8.6 non riceve token dal cloud salvo `OMNIROUTE_CLOUD_SYNC_SECRETS=true`.
- Server contattati (trovati nel codice): quelli dei provider configurati, `claude.ai`/`api.anthropic.com`/
  `platform.claude.com` per l'OAuth, `raw.githubusercontent.com/cheaper-inference/...` per le novità, il cloud
  opzionale. Elenco **non completo**: il progetto ha 26 738 file e non l'ho letto tutto.

**Rischi di collegare l'abbonamento Claude tramite un proxy di terzi**
1. Il proxy vede e può registrare tutto ciò che mandi a Claude (codice, testi del libro, segreti nei file).
2. I token OAuth danno accesso al tuo account (compreso creare chiavi API, scope `org:create_api_key`) e sono salvati
   senza cifratura di default.
3. Usare l'abbonamento Pro/Max fuori dai client ufficiali tramite un client che si spaccia per Claude Code può
   violare i termini d'uso di Anthropic, con rischio di blocco dell'account (valuta tu i termini attuali).
4. Progetto molto grande e che cambia ogni giorno (ultimo commit oggi), con un cambio di owner non chiarito:
   un aggiornamento futuro può cambiare comportamento senza che te ne accorga.

**Cosa richiederebbe**: `npm install -g omniroute@3.8.52` (esegue il postinstall), avvio del server con la
dashboard web locale, inserimento di chiavi API o login OAuth dei provider, poi il collegamento di Claude Code
dalla dashboard (che riscrive `~/.claude/settings.json` come sopra). **Non fatto.**

---

## Perché non ho installato nulla

1. **I comandi `/plugin` non li posso digitare**: sono comandi interattivi di Claude Code. Inoltre questa sessione
   gira in un container cloud temporaneo: un'installazione qui finirebbe in un `~/.claude` che sparisce a fine
   sessione e **non sul tuo computer**. Per questo ti lascio i comandi da digitare.
2. Graphify è DUBBIO e OmniRoute NON INSTALLARE: servono la tua conferma esplicita (regola della richiesta).
3. Il test di `/graphify` su una cartella di prova richiede l'installazione: non eseguito.

## Comandi eseguiti (tutti in sola lettura, nello scratchpad della sessione)

- `git clone --no-checkout --filter=blob:none https://github.com/<owner>/<repo>` per i 5 repository
  (DietrichGebert/ponytail, addyosmani/agent-skills, safishamsi/graphify, Graphify-Labs/graphify,
  diegosouzapw/OmniRoute), poi `git checkout`, `git log`, `git rev-list --count`, `git tag`, `git diff`.
- `curl` verso `registry.npmjs.org` (metadati `skills`, `omniroute`) e `pypi.org` (metadati `graphifyy`);
  download dei tarball `skills-1.7.4.tgz`, `omniroute-3.8.52.tgz` e del wheel `graphifyy-0.9.96`, estratti
  senza eseguirli; confronto `cmp` wheel ↔ repository.
- `grep`, `sed`, `cat`, `wc` per leggere i file.
- Consultata la documentazione ufficiale di Claude Code (sintassi `#ref` per `/plugin marketplace add`).
- Nessun `npm install`, `pip install`, `npx`, `graphify`, nessuno script del progetto eseguito.

## File modificati

- Solo questo file: `docs/setup-plugin-claude-code.md` (nuovo). Nessuna modifica a `~/.claude/settings.json`,
  `~/.claude/CLAUDE.md`, `.claude/settings.json` o `CLAUDE.md` del progetto; nessun indice da aggiornare in `docs/`.

## Cosa non è stato possibile verificare

- Metadati GitHub (data di creazione del repository, stelle, fork, owner verificato, redirect del trasferimento
  di graphify e OmniRoute): API e sito bloccati dal proxy.
- Lettura completa: delle 25 skill di Agent Skills (solo scansione), della CLI `skills`, di gran parte di
  Graphify (`cli.py`, `llm.py`, estrattori) e di quasi tutto OmniRoute (26 738 file).
- Funzionamento reale dei plugin e di `/graphify` (nessuna installazione).

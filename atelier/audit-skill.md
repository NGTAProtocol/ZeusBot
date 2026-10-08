# Audit delle skill di terzi

Data: 2026-10-08. Metodo per ogni candidata:

1. `git clone --depth 1` in una cartella temporanea fuori dal progetto, **senza installare nulla** (nessun `npm install`, `pip install` o script di installazione eseguito).
2. Lettura completa di tutti i file eseguibili della skill (`.sh`, `.py`, `.mjs`, `.js`, `.yaml`) e dei `SKILL.md` brevi.
3. Per i pacchetti grandi (24 `SKILL.md` Impertio, ~290 KB; 3 `SKILL.md` freshtechbro, ~2.400 righe) non c'è stata una lettura riga per riga: frontmatter, struttura e comandi shell citati sono stati letti integralmente; il resto del testo è stato controllato con ricerche mirate (sotto). **Non è una lettura completa**: lo segnalo esplicitamente.
4. Ricerca automatica su tutti i file della skill:
   - chiamate di rete (`curl`, `wget`, `fetch(`, `requests`, `urllib`, `socket`, `http.request`);
   - esecuzione di processi (`subprocess`, `child_process`, `spawn`, `exec`, `eval`, `os.system`);
   - credenziali (`api key`, `secret`, `token`, `password`, `.ssh`, `.aws`, `process.env`, `os.environ`);
   - comandi distruttivi (`rm -rf`, `rmtree`, `unlink`, `sudo`, `chmod`, `git push`, `--force`);
   - istruzioni sospette (`ignore previous`, `do not tell`, `without asking`, `secretly`, `exfiltrate`, `bypass`…);
   - domini esterni citati.
5. Licenza: deve consentire l'uso commerciale ed essere verificabile (file di licenza con titolare).

Gli SHA dei commit e le licenze sono registrati in `skills.lock`.

## Esiti

| Skill | Repo @ commit | Licenza | Esito |
|---|---|---|---|
| frontend-design | anthropics/skills @ `683bc88` | Apache-2.0 (LICENSE.txt) | ✅ installata |
| webapp-testing | anthropics/skills @ `683bc88` | Apache-2.0 (LICENSE.txt) | ✅ installata (con note) |
| web-design-guidelines | vercel-labs/agent-skills @ `063bee9` | MIT dichiarata solo nel README | ❌ respinta |
| ai-ui-ux-motion-engine | OpaceDigitalAgency/skills @ `7ac89f9` | MIT (LICENSE) | ✅ installata (con note) |
| Three.js-Claude-Skill-Package (24 skill) | Impertio-Studio @ `6c190f0` | MIT (LICENSE) | ✅ installata (appiattita) |
| threejs-skills (10 skill) | CloudAI-X @ `b1c6230` | "MIT" solo come frase nel README | ❌ respinta |
| gsap-scrolltrigger | freshtechbro/claudedesignskills @ `1da73fe` | MIT (LICENSE) | ✅ installata (con note) |
| react-three-fiber | freshtechbro/claudedesignskills @ `1da73fe` | MIT (LICENSE) | ✅ installata (non usata dalla pipeline) |
| threejs-webgl | freshtechbro/claudedesignskills @ `1da73fe` | MIT (LICENSE) | ✅ installata (con note) |

### frontend-design — ✅
- Solo `SKILL.md` + `LICENSE.txt`, letti integralmente.
- Niente codice, rete o credenziali.
- Contenuto: linee guida di direzione artistica e una lista dei "tratti tipici del design generato da AI". Sono coerenti con la lista nera di Atelier, che la richiama.

### webapp-testing — ✅ con note
- Letti integralmente `SKILL.md`, `scripts/with_server.py` e i 3 esempi.
- `with_server.py` avvia i comandi passati dall'utente con `shell=True` e controlla le porte su `localhost`. È il comportamento dichiarato: nessuna rete esterna, nessuna credenziale.
- Nota: il `SKILL.md` invita a **non leggere** il sorgente degli script e a usarli "a scatola chiusa". Per prudenza non seguiamo questa indicazione: il sorgente è stato letto (93 righe, innocuo).
- Gli esempi scrivono in `/mnt/user-data/outputs/` e `/tmp`: percorsi d'esempio, non usati da Atelier.
- Richiede Playwright per Python (non installato qui). Atelier usa Playwright per Node.

### web-design-guidelines (vercel-labs) — ❌ respinta
- Il `SKILL.md` (1,2 KB) chiede all'agente di **scaricare a ogni uso** le regole da `raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md` e di seguirle, compreso il formato di output.
- Sono istruzioni remote, mutabili e non bloccate a un commit: chi controlla quel branch può cambiare il comportamento dell'agente in qualsiasi momento. È un rischio di supply-chain e di prompt-injection.
- Inoltre la licenza è dichiarata solo nel README (nessun file LICENSE nel repo) e la licenza del documento remoto non è verificata.
- Per accettarla servirebbe bloccare `command.md` a uno SHA preciso, verificarne la licenza e copiarlo localmente.

### ai-ui-ux-motion-engine (Opace) — ✅ con note
- Letti integralmente:
  - `SKILL.md`;
  - i 2 script shell (`extract-reference-frames.sh`, `prepare-scroll-media.sh`: solo `ffmpeg`/`ffprobe` locali, `mkdir -p`);
  - `audit-motion-safety.mjs` e `render-cinematic-prompt.mjs` (solo lettura di file locali);
  - `agents/openai.yaml`;
  - `references/tool-connections.md`.
- `validate-scroll-media.mjs` usa `spawnSync('ffprobe' / 'ffmpeg')` in locale.
- `validate-package.mjs` legge file del repository originale (installer, plugin.json). Fuori dal repo fallirebbe in modo innocuo: **non va eseguito** nell'installazione di Atelier.
- Niente rete, niente comandi distruttivi.
- Cita un provider video a pagamento (Higgsfield, MCP ospitato). La skill stessa impone di non configurare servizi né spendere crediti senza autorizzazione dell'utente, ed è coerente con il divieto del brief. **Atelier non lo usa**: il livello VIDEO-SCROLL accetta solo asset forniti dal cliente.

### Three.js-Claude-Skill-Package (Impertio) — ✅
- 24 skill di sola documentazione (`.md`), nessuno script.
- Le occorrenze di "credentials" sono documentazione delle API Three.js (`setWithCredentials`); quelle di "bypass" sono descrizioni di anti-pattern. Nessuna istruzione sospetta.
- I comandi citati (`npx gltf-transform …`, `npm install -g gltfpack`, `npm install three …`) sono esempi d'uso, non eseguiti automaticamente. Nota: `npm install -g` è un'installazione globale, da non eseguire senza conferma.
- Installate appiattite (`.claude/skills/threejs-core-renderer`, …) perché Claude Code carica le skill a un solo livello di profondità. Ogni cartella contiene una copia della LICENSE MIT.
- Non installati i file di progetto della radice del repo (`CLAUDE.md`, `START-PROMPT.md`, `agents/`), che contengono istruzioni per il loro processo di sviluppo e non servono.

### threejs-skills (CloudAI-X) — ❌ respinta
- Contenuto tecnicamente innocuo: 10 `SKILL.md`, nessuno script, nessuna rete.
- Respinta per la licenza: nel repo non c'è un file LICENSE né un titolare del copyright, solo la frase "MIT License - Feel free to use, modify, and distribute" nel README. La MIT richiede di riprodurre la nota di copyright, che qui non esiste: per uso commerciale non è verificabile.
- È anche ridondante rispetto al pacchetto Impertio.
- Per accettarla: l'autore dovrebbe aggiungere un file LICENSE con titolare.

### gsap-scrolltrigger, react-three-fiber, threejs-webgl (freshtechbro) — ✅ con note
- Script Python letti per le parti eseguibili (`generate_animation.py`, `timeline_builder.py`, `component_generator.py`, `scene_setup.py`, `setup_scene.py`). Sono generatori di codice che usano solo `argparse`/`pathlib`/`json` e scrivono nel file indicato con `--output`: nessuna rete, nessun processo esterno.
- Nota: gli starter (`assets/starter_*`) caricano GSAP e Three.js da `cdn.jsdelivr.net`. Atelier vieta le CDN: **gli starter non vanno usati così come sono**.
- Nota licenza GSAP: le skill descrivono GSAP ma non ne trattano la licenza. Atelier la verifica separatamente (vedi `CREDITS.md`).
- `react-three-fiber` è installata perché ha passato l'audit, ma la pipeline Atelier usa Three.js "vanilla" in Astro e non React.

## Cosa NON è stato fatto

- Nessuna skill è stata eseguita in modo produttivo durante l'audit (solo lettura).
- Non sono stati collegati servizi esterni né spesi crediti.

# TASKS

Stati: `DONE` · `PARTIAL` · `BLOCKED` · `TODO`

> **V0.1 — COMPLETO per gli obiettivi dichiarati (2026-09-23).** Approvato da D-11 (Opzione 1): v0.1 è considerato completo anche senza Impact Score finale sui repository reali, perché le evidenze disponibili non superano le soglie di D-02. Non è un bug: è una limitazione metodologica deliberata e documentata. V0.1 produce e verifica: punteggi per dimensione osservabile, Coverage, Confidence, Risk, stato `INSUFFICIENT_EVIDENCE` con motivi, report JSON/Markdown tracciabili e riproducibili. Nessun punteggio parziale è mai pubblicato come Impact Score.

## Impact Engine v0.1

| ID | Description | Status | Dependencies | Acceptance Criteria |
|---|---|---|---|---|
| T-01 | Architecture audit | DONE | — | `docs/ARCHITECTURE_AUDIT.md`, 25 sezioni |
| T-02 | Decisioni D-01…D-04 | DONE | T-01 | Approvate e registrate in DECISIONS.md |
| T-03 | Project + Evidence models | DONE | T-02 | Modelli Pydantic immutabili; stati Regola 3 |
| T-04 | Methodology / config versionata | DONE | T-03 | `scoring.yaml` validato; `config_hash` |
| T-05 | GitHub ingestion | DONE | T-04 | Paginazione con limite; rate limit; validazione del target |
| T-06 | Cache / snapshot | DONE | T-05 | SQLite con hash e controllo di integrità |
| T-07 | Normalization | DONE | T-04 | Log saturante/decrescente, frazione, booleano |
| T-08 | Impact Engine | DONE | T-07 | Regola D-02 completa e testata |
| T-09 | Confidence + Coverage | DONE | T-08 | Indipendenti dall'Impact (testato) |
| T-10 | Risk / anti-gaming v0.1 | DONE | T-08 | 5 segnali, con evidenze; nessun effetto sull'Impact |
| T-11 | Report JSON + Markdown | DONE | T-08…T-10 | Deterministici; `report_hash` |
| T-12 | CLI | DONE | T-11 | `ghimoney analyze owner/repo` |
| T-13 | Test | DONE | T-03…T-12 | Unit, integration, golden, determinism, regression, red-team: 64 test |
| T-14 | Analisi di repository reali (§48) | **BLOCKED** | T-12 | ≥ 10 repository di categorie diverse. Bloccato: in questo ambiente la GitHub API è limitata ai repository collegati alla sessione. Eseguito solo su `NGTAProtocol/ZeusBot`. Vedi `docs/VALIDATION.md` |
| T-15 | Red-team iniziale | DONE | T-13 | `tests/test_redteam.py`, THREAT_MODEL.md |
| T-16 | Risolvere il conflitto D-11 | DONE | approvazione | **Opzione 1 approvata e confermata 2026-09-23.** V0.1 è completo senza Impact Score finale su repository reali; limitazione metodologica dichiarata, non un fallimento. Vincoli in DECISIONS.md: niente deps.dev non verificata (D-03), niente punteggi parziali spacciati per Impact Score (test `test_no_partial_score_is_ever_reported_as_impact`) |
| T-17 | Conferma dei parametri D-02 ("dimensioni principali") | DONE | approvazione | **Confermato 2026-09-23 (due volte)**: Adoption e Dependency, peso iniziale 25% ciascuna, max 1 mancante; entrambe mancanti → `INSUFFICIENT_EVIDENCE`. Aggiunto il campo esplicito `impact.renormalization_reason` (motivo del ricalcolo, punto 6d della conferma) — estensione del formato di report, non della metodologia |
| T-18 | Verificare deps.dev — analisi documentale (disponibilità, affidabilità, qualità dei dati, copertura, provenance, stabilità API, riproducibilità, rate limits) | **DONE / COMPLETED** | — | `docs/DEPS_DEV_EVALUATION.md` pubblicato (15 sezioni). Conclusione: APPROVED WITH CONDITIONS. Nessuna riga di codice toccata |
| T-19A | Verifica empirica di deps.dev (analisi soltanto, nessuna integrazione) | **DONE / COMPLETED** | T-18 | `docs/DEPS_DEV_EMPIRICAL_VERIFICATION.md` pubblicato. 16 richieste HTTP reali tramite Firecrawl (EMPIRICAL VERIFICATION VIA THIRD-PARTY NETWORK INFRASTRUCTURE, `*.deps.dev` bloccato da questa sessione). Confermato empiricamente: Go privo del dependency graph risolto (HTTP 404), riproducibilità byte-identica su richiesta ripetuta. Conclusione: VERIFIED FOR NEXT DECISION. Nessuna riga di codice toccata |
| **T-19** | **Implementazione Dependency Evidence** (modulo deps.dev, ingestion, evidence, provenance) | **DONE / COMPLETED** | T-18 (DONE), T-19A (DONE), D-03 v2 (APPROVATA CON CONDIZIONI) | `depsdev_ingestion.py` + `depsdev_evidence.py` + CLI `dependency-evidence`. Rispettate le 7 condizioni di D-03 v2: Go = `NOT_AVAILABLE` sul grafo risolto, mai zero (test dedicato); provenance preservata (`UNVERIFIED_METADATA` non letto/riscritto); riproducibilità tramite snapshot (nessuna chiamata live nel calcolo dell'evidenza); errori classificati esplicitamente (404 mai → 0, distinto da absence/transport/rate-limit); nessun rate limit inventato (nessun retry, nessuna soglia numerica assunta). 34 nuovi test (98 totali), tutti con fixture reali di T-19A o mock, nessuna dipendenza dalla rete. **Non wired in `engine.analyze()`: `config/scoring.yaml` invariato, nessun Impact Score prodotto** |
| T-19B | Audit semantico: la Dependency Evidence di T-19 (dependencies uscenti) è compatibile con la dimensione "Dependency" (dependents)? | **DONE / COMPLETED** | T-19 | **Incoerenza confermata e risolta con D-12**: "Dependency" nell'Impact Engine misura i dependents, non le dependencies uscenti. T-19 resta valido come Dependency Evidence strutturale separata, non collegata alla dimensione. Nessun codice toccato |
| T-20A | Verifica di una fonte di dependents (deps.dev `GetDependents`) | **DONE / COMPLETED** | T-19B, D-12 | `docs/DEPENDENTS_SOURCE_VERIFICATION.md`: VERIFIED FOR T-20. Solo v3alpha (non v3 stabile); npm/PyPI/Maven/Cargo verificati con dati reali; Go strutturalmente assente (404 su due package reali). Nessun codice toccato |
| **T-20** | **Full Impact Score** (dependents integrati nello scoring per la dimensione Dependency) | **DONE / COMPLETED** | T-20A (DONE), D-12 (DEFINITIVA) | `depsdev_dependents_ingestion.py` + `depsdev_dependents_evidence.py` (fonte separata da T-19, mai la alimenta). Nuova metrica `dependents_total_count` in `config/scoring.yaml` (dimensione `dependency`, peso 1.0, log_saturating, anchor=1000 dichiarata ipotesi) — pesi di dimensione, D-02 e soglie invariati. `methodology_version` → `GHIM-IMPACT-0.2` (§44). `engine.analyze()` accetta `extra_evidence` opzionale (additivo, retrocompatibile); CLI `analyze --dependents ecosystem:name@version` (esplicito, nessuna correlazione automatica progetto↔package). Go: `NOT_AVAILABLE`, mai zero (verificato). 404 ambiguo mai zero. Fonte marcata esplicitamente sperimentale (v3alpha) in `method`. 30 nuovi test (128 totali) |
| **T-21** | **Test, regressione e red-team su GHIM-IMPACT-0.2** | **DONE / COMPLETED** | T-20 | `docs/T21_TEST_REPORT.md`. 133/133 test passano (128 preesistenti + 5 nuovi, solo le lacune reali: scoping del metric alla sola dimensione dependency, chiave `dependencies` di T-19 mai letta come dependents, sensibilità dell'ancora 1000). **Finding non corretto** (per istruzione esplicita): l'ancora 1000 satura per ogni valore reale ≥ ~1000 dependents, perdendo discriminazione tra progetti molto popolari (requests/guava/lodash tutti a 100.0). Nessun bug reale trovato: nessuna riga di codice sorgente modificata |
| T-22 | Validazione su repository reali diversificati | **BLOCKED** | T-21 | ≥ 10 repository di categorie diverse (§48). **Bloccato, verificato empiricamente 2026-09-24**: il proxy di rete della sessione limita `api.github.com` ai soli repository collegati (3, tutti `NGTAProtocol`), indipendentemente dal `GITHUB_TOKEN` usato (verificato con `curl` e token falso). Nessun dato simulato prodotto per compensare. Vedi `docs/T22_REAL_WORLD_VALIDATION.md` |
| T-22-collector | Collector GitHub esterno (owner/repo + GITHUB_TOKEN → snapshot `ghimoney-snapshot/1`) | **DONE / COMPLETED** | T-21 | `tools/collect_github_snapshot.py`: wrapper sottile su `GitHubIngestor`/`Snapshot.dump()` già verificati, nessuna logica HTTP/paginazione/errori propria, nessuna modifica a Impact Engine/metodologia/formato snapshot. 5 nuovi test offline (`tests/test_collect_github_snapshot.py`, 138 totali), snapshot prodotto verificato accettato da `ghimoney analyze --snapshot-file`. T-22 stesso (10 repository) resta BLOCKED: questo task fornisce solo lo strumento di raccolta, funzionante e verificato offline |

## Criteri di accettazione §73

| | Criterio | Stato |
|---|---|---|
| A | Analizza un repository GitHub reale | ✅ (`NGTAProtocol/ZeusBot`) |
| B | Evidenze con provenance | ✅ |
| C | Produce Impact Score | ✅ **implementato e testato.** Con Adoption ancora senza fonte, un repository GitHub-only resta `INSUFFICIENT_EVIDENCE` (D-11); un Full Impact Score numerico è ora possibile quando Dependency (dependents, T-20) è disponibile assieme ad almeno un'altra dimensione, fino a superare la soglia di coverage (D-02) |
| D | Confidence | ✅ |
| E | Evidence Coverage | ✅ |
| F | Risk | ✅ |
| G | Missing data | ✅ |
| H | Deterministico | ✅ |
| I | Metodologia versionata | ✅ |
| J | JSON | ✅ |
| K | Markdown | ✅ |
| L | Test automatici | ✅ |
| M | Verificato su repository reali | ⚠️ uno solo (T-14 bloccato dall'ambiente di sviluppo) |
| N | Documentato | ✅ |
| O | Red-team iniziale | ✅ |

## Sequenza operativa approvata verso l'Impact Score completo (D-11, confermata 2026-09-23; D-03 formalizzata 2026-09-23)

```
V0.1 (COMPLETO)
  → validazione reale (T-14, bloccato dall'ambiente)
  → verifica deps.dev — analisi documentale (T-18, DONE)
  → verifica empirica deps.dev (T-19A, DONE)
  → D-03 formalizzata: deps.dev approvato con condizioni (DONE, 2026-09-23)
  → implementazione Dependency evidence (T-19, DONE, strutturale/dependencies uscenti)
  → audit semantico Dependency Evidence vs dimensione Dependency (T-19B, DONE)
  → D-12: Dependency = dependents, non dependencies uscenti (DEFINITIVA)
  → verifica di una fonte di dependents (T-20A, DONE — VERIFIED FOR T-20)
  → Full Impact Score (T-20, DONE — dependents wired, GHIM-IMPACT-0.2)
  → nuova batteria di test (T-21)
  → regression test (T-21)
  → red-team (T-21)
  → validazione su repository reali diversificati (T-22)
```

Nessun passo successivo inizia prima che il precedente sia chiuso. Le regole di D-02/D-03 non vengono modificate per ottenere artificialmente un Impact Score.

**Stato al 2026-09-23 dopo la formalizzazione di D-03:**
- T-18 = COMPLETED
- T-19A = COMPLETED
- T-19 = **DONE** (implementazione Dependency Evidence via deps.dev, standalone, non wired nello scoring).
- T-19B = **DONE** (audit semantico: incoerenza confermata e risolta con D-12 — "Dependency" = dependents, T-19 non la alimenta).
- T-20A = **DONE** (deps.dev `GetDependents` verificato, VERIFIED FOR T-20).
- T-20 = **DONE** (dependents wired nella dimensione "dependency"; `methodology_version` = `GHIM-IMPACT-0.2`; pesi di dimensione, D-02 e soglie invariati; T-19 resta separato). Prossimo passo: T-21 (nuova batteria di test + regression + red-team sulla metodologia aggiornata) — non avviato.

## Dopo v0.1 (roadmap §66, non iniziati)
Dependency Graph → AI Auditor → Human Review → Community Signal → Challenge → Funding Simulator → Milestone Monitoring → Project Credential → Smart Contracts → Testnet → Security Audit → Economic Validation → Mainnet → GHIM Token.

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
| T-18 | Verificare deps.dev (disponibilità, affidabilità, qualità dei dati, copertura, provenance, stabilità API, riproducibilità, rate limits) | TODO | T-14 | Prerequisito per qualsiasi aggiornamento di D-03. **Non iniziare l'integrazione prima di questa verifica** — vincolo esplicito confermato 2026-09-23 |
| T-19 | Implementazione Dependency evidence | TODO | T-18 | Solo dopo un esito positivo di T-18 e un aggiornamento formale di D-03 |
| T-20 | Impact Score completo | TODO | T-19 | Solo quando Adoption o Dependency hanno una fonte verificata e la Coverage può superare il 60% |
| T-21 | Nuova batteria di test + regression test + red-team | TODO | T-20 | Sulla metodologia aggiornata (nuova `methodology_version`) |
| T-22 | Validazione su repository reali diversificati | TODO | T-21 | ≥ 10 repository di categorie diverse (§48) |

## Criteri di accettazione §73

| | Criterio | Stato |
|---|---|---|
| A | Analizza un repository GitHub reale | ✅ (`NGTAProtocol/ZeusBot`) |
| B | Evidenze con provenance | ✅ |
| C | Produce Impact Score | ✅ **implementato, testato, e accettato come completo per v0.1** (D-11, Opzione 1): produce `INSUFFICIENT_EVIDENCE` con i motivi quando le soglie non sono superate — non raggiungibile su repository reali con sola GitHub, per costruzione (D-03). Il vero Impact Score numerico si chiude con T-20 |
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

## Sequenza operativa approvata verso l'Impact Score completo (D-11, confermata 2026-09-23)

```
V0.1 (qui, COMPLETO)
  → validazione reale (T-14)
  → verifica deps.dev (T-18)
  → eventuale aggiornamento D-03
  → implementazione Dependency evidence (T-19)
  → Impact Score completo (T-20)
  → nuova batteria di test (T-21)
  → regression test (T-21)
  → red-team (T-21)
  → validazione su repository reali diversificati (T-22)
```

Nessun passo successivo inizia prima che il precedente sia chiuso. Le regole di D-02/D-03 non vengono modificate per ottenere artificialmente un Impact Score.

## Dopo v0.1 (roadmap §66, non iniziati)
Dependency Graph → AI Auditor → Human Review → Community Signal → Challenge → Funding Simulator → Milestone Monitoring → Project Credential → Smart Contracts → Testnet → Security Audit → Economic Validation → Mainnet → GHIM Token.

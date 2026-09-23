# TASKS

Stati: `DONE` · `PARTIAL` · `BLOCKED` · `TODO`

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
| T-13 | Test | DONE | T-03…T-12 | Unit, integration, golden, determinism, regression, red-team: 62 test |
| T-14 | Analisi di repository reali (§48) | **BLOCKED** | T-12 | ≥ 10 repository di categorie diverse. Bloccato: in questo ambiente la GitHub API è limitata ai repository collegati alla sessione. Eseguito solo su `NGTAProtocol/ZeusBot`. Vedi `docs/VALIDATION.md` |
| T-15 | Red-team iniziale | DONE | T-13 | `tests/test_redteam.py`, THREAT_MODEL.md |
| T-16 | Risolvere il conflitto D-11 | DONE | approvazione | **Opzione 1 approvata 2026-09-23.** v0.1 resta senza Impact Score finale su repository reali; limitazione metodologica dichiarata, non un fallimento. Vincoli registrati in DECISIONS.md: niente deps.dev non verificata, niente punteggi parziali spacciati per Impact Score (test `test_no_partial_score_is_ever_reported_as_impact`) |
| T-17 | Conferma dei parametri D-02 ("dimensioni principali") | DONE | approvazione | **Confermato 2026-09-23**: Adoption e Dependency, max 1 mancante. Nessuna modifica al codice necessaria |
| T-18 | Verificare deps.dev (copertura, affidabilità, termini d'uso, stabilità API) | TODO | T-14 | Prerequisito per qualsiasi aggiornamento di D-03. Non iniziare l'integrazione prima di questa verifica |

## Criteri di accettazione §73

| | Criterio | Stato |
|---|---|---|
| A | Analizza un repository GitHub reale | ✅ (`NGTAProtocol/ZeusBot`) |
| B | Evidenze con provenance | ✅ |
| C | Produce Impact Score | ⚠️ implementato e testato; non raggiungibile su repository reali con sola GitHub. **Accettato come limitazione metodologica dichiarata (D-11, Opzione 1)**, da chiudere dopo T-18 e l'aggiornamento di D-03 |
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

## Sequenza approvata verso l'Impact Score completo (D-11)

```
V0.1 (qui) → validazione reale (T-14) → verifica deps.dev (T-18)
  → D-03 aggiornata → Impact Score completo → nuova batteria di test
```

Nessun passo successivo inizia prima che il precedente sia chiuso.

## Dopo v0.1 (roadmap §66, non iniziati)
Dependency Graph → AI Auditor → Human Review → Community Signal → Challenge → Funding Simulator → Milestone Monitoring → Project Credential → Smart Contracts → Testnet → Security Audit → Economic Validation → Mainnet → GHIM Token.

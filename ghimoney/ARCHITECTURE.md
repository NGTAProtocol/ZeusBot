# ARCHITECTURE — Impact Engine v0.1

Modular monolith (Directive §40). Nessuna blockchain, nessun token, nessun Treasury in questa fase (§72).

## Componenti

| Modulo | Responsabilità | Dipende da |
|---|---|---|
| `methodology.py` | Carica e valida `config/scoring.yaml`, calcola `config_hash` | `canonical` |
| `ingestion.py` | Legge la GitHub REST API (httpx) e produce uno `Snapshot` | `methodology`, `snapshot` |
| `snapshot.py` | Snapshot immutabili con hash; store SQLite (= cache); storia dei nomi | `canonical` |
| `evidence.py` | Snapshot → Evidence Record con provenance; identità del progetto | `normalization`, `models` |
| `normalization.py` | Scale 0–100 logaritmiche (D-01) | `methodology` |
| `scoring.py` | Punteggi di dimensione, Coverage, Impact (D-02), Confidence | `models` |
| `risk.py` | Segnali di anomalia con evidenze | `models` |
| `engine.py` | Pipeline completa → report (dict) con `report_hash` | tutti i precedenti |
| `report.py` | Rendering JSON (canonico) e Markdown | `canonical` |
| `cli.py` | `ghimoney analyze`, `ghimoney export-snapshot` | tutti |
| `canonical.py` | JSON canonico, arrotondamento, hash | — |

## Flusso

```
ghimoney analyze owner/repo
   │
   ├─ snapshot in cache più recente di --max-age-hours?  ── sì ─┐
   │                                                            │
   └─ no ─► GitHubIngestor.fetch() ─► SnapshotStore.save() ─────┤
                                                                ▼
                         engine.analyze(snapshot, methodology)   (nessun accesso di rete)
                                                                │
                              reports/<owner>__<repo>/<snapshot_id>/report.{json,md}
```

## Confini

- **Rete ↔ scoring:** solo `ingestion.py` accede alla rete. Tutto il resto è una funzione pura dello snapshot e della configurazione. È il confine che garantisce il determinismo.
- **Repository analizzato = input non fidato (§21):** nessun clone e nessuna esecuzione. I campi testuali sono solo dati.
- **Impact ↔ Coverage/Confidence/Risk:** calcolati da funzioni separate. Risk e Confidence non hanno accesso in scrittura all'Impact (verificato dai test).
- **Impact Engine ↔ Treasury (Regola 12):** il Treasury non esiste in v0.1. L'Impact Engine non produce importi.

## Dati

- **Snapshot** (`.ghimoney/snapshots.db`, escluso da git): risposte grezze dell'API, incluse le email degli autori dei commit, che sono dati pubblici ma personali. Non entrano mai nei report (§36, testato).
- **Report:** solo conteggi, punteggi, hash e provenance.
- **Fixture di test:** esclusivamente sintetiche e marcate `synthetic: true`.

## On-chain / off-chain

Non applicabile in v0.1. Il formato del report (`snapshot_hash`, `config_hash`, `report_hash`) è pensato per diventare in futuro il commitment on-chain (§35) senza cambiare il motore.

## Governance

In v0.1 la metodologia è scritta dal fondatore e non è vincolante (DECISIONS D-10). Ogni modifica passa da una nuova `methodology_version`, controllata dal test golden.

# GHIMONEY — Impact Engine v0.1

Motore di misurazione **verificabile e riproducibile** dell'impatto dei progetti open-source. Prima fase del protocollo GHIMONEY: *prove the score before you move the money*.

v0.1 **non** include token, blockchain, smart contract, Treasury o funding (Directive v6.0 §72). I risultati delle metodologie 0.x non sono mai usati per finanziamenti.

## Uso

```bash
cd ghimoney
pip install -e ".[test]"
export GITHUB_TOKEN=...            # opzionale, consigliato per i rate limit

ghimoney analyze owner/repository  # → reports/<owner>__<repo>/<snapshot_id>/report.{json,md}
```

Opzioni utili:

| Opzione | Effetto |
|---|---|
| `--offline` | Nessuna chiamata di rete: usa l'ultimo snapshot in cache |
| `--snapshot <id>` | Ri-analizza uno snapshot salvato |
| `--snapshot-file f.json` | Analizza uno snapshot esportato |
| `--max-age-hours N` | Riusa la cache se più recente di N ore (default 24) |
| `--config path.yaml` | Metodologia alternativa |

`ghimoney export-snapshot <id> file.json` esporta uno snapshot per farlo verificare a terzi: chiunque può ricalcolare lo stesso report.

## Cosa produce ogni analisi

- **Impact Score**, oppure `INSUFFICIENT_EVIDENCE` con i motivi;
- **Evidence Coverage**, **Confidence** e **Risk** come metriche separate: non modificano l'Impact;
- punteggi per dimensione, pesi originali ed effettivi, dimensioni mancanti;
- ogni evidenza con stato del dato, valore grezzo e normalizzato, metodo, confidence e provenance (endpoint e hash della risposta);
- `methodology_version`, `config_hash`, `snapshot_hash` e `report_hash` per la riproducibilità.

## Test

```bash
python -m pytest
```

Unit, integration, golden, determinismo (anche tra processi), regressione e red-team.

## Documenti

| File | Contenuto |
|---|---|
| [DECISIONS.md](DECISIONS.md) | Decisioni approvate (D-01…D-11); nessuna in attesa |
| [METHODOLOGY.md](METHODOLOGY.md) | Formule, pesi, normalizzazione, limiti |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Componenti, confini, flussi |
| [THREAT_MODEL.md](THREAT_MODEL.md) | Minacce e stato delle mitigazioni |
| [ECONOMICS.md](ECONOMICS.md) | Domande economiche aperte (nessuna decisione presa) |
| [TASKS.md](TASKS.md) | Stato dei task e dei criteri di accettazione |
| [docs/ARCHITECTURE_AUDIT.md](docs/ARCHITECTURE_AUDIT.md) | Audit architetturale della Directive v6.0 |
| [docs/VALIDATION.md](docs/VALIDATION.md) | Validazione su repository reali |

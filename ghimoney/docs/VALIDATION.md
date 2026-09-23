# VALIDATION — GHIM-IMPACT-0.1

## Repository reali analizzati

| Repository | Snapshot | Impact | Coverage | Risk | Report |
|---|---|---|---|---|---|
| `NGTAProtocol/ZeusBot` | `9b966eb2d631ad45` (2026-09-23) | INSUFFICIENT_EVIDENCE | 50% | LOW | [`reports/NGTAProtocol__ZeusBot/9b966eb2d631ad45/`](../reports/NGTAProtocol__ZeusBot/9b966eb2d631ad45/report.md) |

Verifiche eseguite su dati reali:
- ingestion completa da GitHub API: tutti gli endpoint hanno risposto;
- missing data: nessuna GitHub Release e nessun workflow → `UNKNOWN`, non zero;
- determinismo: la ri-analisi offline dello stesso snapshot produce un `report.json` identico byte per byte.

## Perché un solo repository

L'ambiente cloud in cui è stato sviluppato v0.1 permette chiamate alla GitHub API **solo per i repository collegati alla sessione**. Per gli altri (es. `psf/requests`) il proxy risponde 403. Il criterio §48 (≥ 10 repository reali di categorie diverse) **non è ancora soddisfatto** (TASKS T-14).

## Come completare la validazione

Su una macchina con accesso diretto a `api.github.com`:

```bash
cd ghimoney
pip install -e .
export GITHUB_TOKEN=...   # consigliato: il limite senza token è 60 richieste/ora
for repo in <lista di repository di categorie diverse>; do
  ghimoney analyze "$repo"
done
```

Categorie da coprire (§48): piccole librerie, librerie molto usate, framework, tool, infrastruttura, progetti nuovi, progetti maturi, progetti con pochi contributor, grandi community. L'obiettivo è **trovare dove il modello sbaglia**, non confermarlo.

## Scoperte finora

1. **D-11 (approvata, Opzione 1):** con D-02 + D-03, nessun repository reale può ottenere un Impact Score finale. Limitazione metodologica dichiarata, non un fallimento tecnico. Si chiude solo dopo T-18 (verifica di deps.dev) e un aggiornamento di D-03.
2. **Bug trovato dal test golden e corretto prima del commit:** i file della community profile restituiti come oggetto vuoto venivano contati come assenti.

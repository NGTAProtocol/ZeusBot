# METHODOLOGY — GHIM-IMPACT-0.1

> Tutti i pesi, le ancore e le soglie sono **ipotesi iniziali**, non valori validati. Fonte di verità: `config/scoring.yaml`. Il suo hash (`config_hash`) compare in ogni report.

## 1. Pipeline

```
GitHub REST API ──► Snapshot (SQLite, hash) ──► Evidence Records ──► Normalizzazione
                                                                        │
          ┌─────────────────────┬────────────────────┬──────────────────┤
          ▼                     ▼                    ▼                  ▼
   Dimension scores         Coverage             Confidence            Risk
          │                     │                    ▲                  │
          └────► Impact (D-02) ◄┘                    └── fattore ───────┘
```

Coverage, Confidence e Risk sono calcolati da funzioni separate e **non modificano l'Impact Score** (D-04).

## 2. Stati dei dati (Regola 3)

| Stato | Significato | Esempio v0.1 |
|---|---|---|
| `VERIFIED` | Valore osservato | 120 commit nell'ultimo anno |
| `UNKNOWN` | L'assenza osservata non prova un valore zero | nessuna GitHub Release; nessun workflow Actions |
| `NOT_AVAILABLE` | La fonte non ha fornito il dato | HTTP 403 o dimensione senza fonte approvata |
| `NOT_APPLICABLE` | La metrica non ha senso per il progetto | "giorni dall'ultimo commit" su repository vuoto |
| `INSUFFICIENT_EVIDENCE` | Dati insufficienti per un risultato | dimensione con copertura interna < 50% |

Nessuno di questi stati diventa zero.

## 3. Dimensioni e metriche

| Dimensione | Peso | Metrica | Peso interno | Normalizzazione | Ancora |
|---|---|---|---|---|---|
| Adoption | 25% | — | — | `NOT_AVAILABLE` in v0.1 (D-03) | — |
| Dependency | 25% | — | — | `NOT_AVAILABLE` in v0.1 (D-03) | — |
| Maintenance | 15% | `commits_last_365d` | 0.4 | log saturante | 500 |
| | | `days_since_last_commit` | 0.4 | log decrescente | 365 |
| | | `releases_last_365d` | 0.2 | log saturante | 12 |
| Quality | 15% | `community_profile_files` (README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, template issue e PR) | 0.5 | frazione | — |
| | | `ci_workflows_present` | 0.5 | booleano | — |
| Security | 10% | `security_policy_present` | 1.0 | booleano | — |
| Community | 10% | `distinct_authors_last_365d` | 0.5 | log saturante | 50 |
| | | `total_contributors` | 0.5 | log saturante | 200 |

**Segnali registrati ma mai usati nel punteggio (Regola 2):** stars, forks, watchers, età del repository, advisory pubblicate, quota del primo autore, massima concentrazione di commit in 7 giorni. Il Risk Engine li usa.

## 4. Normalizzazione (D-01)

- log saturante: `100 · min(1, ln(1+x) / ln(1+ancora))`
- log decrescente: `100 · max(0, 1 − ln(1+x) / ln(1+ancora))`
- frazione: `100 · x`; booleano: `100` o `0`

Oltre l'ancora non c'è guadagno.

## 5. Aggregazione (D-02)

1. **Dimensione:** media pesata delle metriche `VERIFIED`, con pesi interni ricalcolati. Se la copertura interna è < 50%, la dimensione è `INSUFFICIENT_EVIDENCE`.
2. **Coverage** = Σ pesi delle dimensioni osservabili ÷ Σ pesi delle dimensioni applicabili.
3. **Impact** = `INSUFFICIENT_EVIDENCE` se:
   - Coverage < 60%, oppure
   - meno di 2 dimensioni osservabili, oppure
   - più di 1 dimensione principale (Adoption, Dependency) mancante.

   Altrimenti: Σ (peso effettivo × punteggio), con peso effettivo = peso ÷ Σ pesi osservabili. Il report riporta `original_weights`, `effective_weights`, `weights_renormalized` e `missing_dimensions`.

## 6. Confidence (D-04)

Confidence per tipo di evidenza:

| Tipo | Confidence |
|---|---|
| conteggio diretto | 0.90 |
| limite inferiore (paginazione troncata) | 0.60 |
| presenza verificata | 0.80 |
| assenza verificata | 0.60 |
| derivato | 0.80 |

- Confidence di dimensione = media pesata delle evidenze usate.
- Confidence base = media pesata delle dimensioni osservabili.
- Confidence corretta = base × fattore di rischio (LOW 1.0, MEDIUM 0.9, HIGH 0.7, CRITICAL 0.5).

Entrambi i valori sono riportati.

## 7. Risk (D-04)

| Segnale | Livello | Condizione (ipotesi) |
|---|---|---|
| `popularity_vs_contributors` | MEDIUM | stars ≥ 500 e contributor ≤ 2 |
| `young_and_popular` | MEDIUM | età ≤ 90 giorni e stars ≥ 1000 |
| `commit_burst` | MEDIUM | ≥ 50 commit/anno e > 50% concentrati in 7 giorni |
| `author_concentration` | LOW | ≥ 20 commit/anno e primo autore ≥ 90% (sostenibilità, non manipolazione) |
| `repository_is_fork` | MEDIUM | il repository è un fork |

Livello complessivo = massimo tra i segnali (LOW se nessuno). I controlli non valutabili per mancanza di dati sono elencati in `checks_not_evaluated`. **Un segnale non è mai una prova di frode** (Regole 10, 11).

## 8. Versioning e determinismo

- Ogni report dichiara `methodology_version`, `config_version`, `config_hash`, `snapshot_id`, `snapshot_hash`, `as_of`, `source_versions` e `report_hash`.
- Stesso snapshot + stessa configurazione → report identico byte per byte (testato anche tra processi con hash seed diversi).
- Qualsiasi modifica alla configurazione cambia `config_hash`. Il test golden fallisce se la configurazione cambia senza una nuova `methodology_version`.

## 9. Limiti noti di GHIM-IMPACT-0.1

1. **Nessun Impact Score finale per repository reali**: Coverage massima 50% (vedi DECISIONS D-11).
2. **Solo GitHub**: progetti su GitLab, Codeberg o altre forge sono esclusi per costruzione (bias di piattaforma, §63).
3. **Quality** misura l'igiene del progetto (file di community, CI), non la qualità del codice.
4. **Security** misura solo la presenza di una security policy, non la sicurezza del software.
5. **Bias di dimensione**: più commit e più contributor portano un punteggio più alto, fino all'ancora. Un piccolo progetto maturo e stabile può risultare penalizzato su Maintenance (§11).
6. **Bias contro i progetti mantenuti da una sola persona** su Community.
7. **Ancore scelte a priori**, non calibrate su un corpus reale.
8. **Limiti di paginazione**: repository molto attivi producono valori marcati come limite inferiore.
9. **Validazione reale limitata**: vedi `docs/VALIDATION.md`.

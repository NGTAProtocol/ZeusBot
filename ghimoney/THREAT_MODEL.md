# THREAT MODEL

Stato: v0.1 (solo Impact Engine). Da aggiornare a ogni fase (Directive §57).

Legenda stato: ✅ mitigato e testato · 🟡 parzialmente mitigato · ⛔ non mitigato in v0.1 · ➖ fuori scope v0.1

| # | Minaccia | Stato | Mitigazione attuale | Test |
|---|---|---|---|---|
| 1 | Fake stars | ✅ | Le stars non entrano nel punteggio (Regola 2); segnali di rischio `popularity_vs_contributors` e `young_and_popular` | `test_fake_stars_do_not_change_any_score`, `test_star_inflation_raises_risk` |
| 2 | Fake downloads | ➖ | I download non sono misurati in v0.1 | — |
| 3 | Bot contributors / Sybil accounts | 🟡 | Saturazione all'ancora (50 autori): autori extra non danno guadagno | `test_bot_author_multiplication_saturates` |
| 4 | Attività artificiale (commit burst) | 🟡 | Segnale `commit_burst`; nessun effetto sul punteggio (solo sulla confidence) | `test_commit_burst_is_flagged` |
| 5 | Commit artificiali distribuiti nel tempo | ⛔ | Non rilevabili con i segnali v0.1; saturano all'ancora 500 | — |
| 6 | Repository cloning / fork spacciato per originale | 🟡 | Segnale `repository_is_fork`; un clone non-fork non viene rilevato | `test_fork_is_flagged` |
| 7 | Repository takeover / rename per ereditare reputazione | 🟡 | `project_id` ancorato all'ID numerico GitHub; storia dei nomi | `test_identity_is_anchored_to_numeric_repo_id`, `test_name_history_tracks_renames` |
| 8 | Nascondere dati sfavorevoli | ✅ | Dati nascosti → Coverage più bassa → `INSUFFICIENT_EVIDENCE` | `test_hiding_data_cannot_produce_a_score` |
| 9 | Esecuzione di codice malevolo del repository | ✅ | Nessun clone e nessuna esecuzione (§21) | per costruzione |
| 10 | Manipolazione dello snapshot locale | ✅ | Hash di integrità verificato alla lettura | `test_store_roundtrip_and_tamper_detection` |
| 11 | Path/URL injection tramite il nome del repository | ✅ | Validazione `owner/repo` | `test_invalid_targets_are_rejected` |
| 12 | Esposizione del token GitHub | ✅ | Solo variabile d'ambiente; mai scritto su disco o nei report | revisione |
| 13 | Dati personali nei report | ✅ | Email mai nei report; solo conteggi | `test_personal_data_does_not_reach_report` |
| 14 | Modifica silenziosa della metodologia | ✅ | `config_hash` nel report; il test golden richiede una nuova versione | `test_golden_report`, `test_config_hash_changes_with_any_parameter` |
| 15 | Dependency manipulation / circular dependencies | ➖ | Dependency non misurata in v0.1 | — |
| 16 | AI manipulation / prompt injection | ➖ | Nessuna AI in v0.1 | — |
| 17 | Reviewer collusion, vote manipulation, challenge manipulation | ➖ | Fasi 4–6 | — |
| 18 | Governance attack, whale voting, token concentration | ➖ | Nessun token in v0.1 | — |
| 19 | Treasury attack, smart contract vulnerabilities | ➖ | Nessun Treasury né contratto in v0.1 | — |
| 20 | Oracle/data manipulation della fonte (API compromessa o errata) | ⛔ | Unica fonte, nessun confronto tra fonti (§9) | — |
| 21 | Abuso di privilegi del fondatore | 🟡 | Metodologia 0.x dichiarata non vincolante e mai usata per fondi (D-10); hash pubblici | — |
| 22 | Maintainer impersonation | ⛔ | Nessuna attestazione di ownership in v0.1 | — |

## Priorità per v0.2
1. #20: seconda fonte indipendente per incrociare i dati (deps.dev, dopo verifica).
2. #5: segnali temporali più robusti (serie storiche tra snapshot successivi).
3. #6: rilevare cloni non-fork (hash della storia dei commit, se ottenibile senza eseguire codice).

# T-21 — Test, Regressione e Red-Team su GHIM-IMPACT-0.2

**Data:** 2026-09-23
**Scopo:** validare l'Impact Engine dopo T-20 (dependents nella dimensione "dependency"). Nessuna modifica a metodologia, pesi, ancore o D-02: nessun bug reale è stato trovato, quindi il codice sorgente non è stato toccato. È stato aggiunto un solo file di test.

## 1. Risultato

**133/133 test passano** (128 preesistenti + 5 nuovi in `tests/test_t21_redteam.py`). Nessuna regressione.

## 2. Cosa era già coperto (non riscritto)

La maggior parte della checklist richiesta era già verificata da suite precedenti:

| Voce della checklist | Già coperta da |
|---|---|
| Fake stars/forks non alterano l'Impact | `test_redteam.py::test_fake_stars_do_not_change_any_score`, `test_t20_full_impact_score.py::test_stars_and_forks_still_cannot_alter_score_with_dependents_wired` |
| Dati mancanti non diventano zero | `test_units.py` (Regola 3), `test_scoring.py::test_dependency_missing_is_not_scored_as_zero` |
| Adoption + Dependency mancanti → `INSUFFICIENT_EVIDENCE` | `test_scoring.py::test_both_core_dimensions_missing_blocks_score` |
| Coverage < 60% → nessun Impact Score | `test_scoring.py::test_coverage_below_threshold_gives_no_score`, `test_t20_full_impact_score.py::test_coverage_insufficient_even_with_dependency_verified` |
| Renormalizzazione coerente e tracciata | `test_scoring.py::test_renormalization_is_declared`, `test_report_always_shows_weights_and_recalculation_reason` |
| Determinismo (stesso snapshot/config) | `test_determinism.py` (anche cross-processo), `test_depsdev_dependents_ingestion.py::test_fetch_is_reproducible` |
| Go "dependents" mai zero | `test_depsdev_dependents_evidence.py::test_go_dependents_is_not_available_never_zero` |
| 404 su ecosistemi supportati mai zero | `test_depsdev_dependents_evidence.py::test_404_on_supported_ecosystem_is_ambiguous_never_zero` |

## 3. Cosa ho aggiunto (solo il necessario)

Tre lacune reali, non coperte da nessun test esistente:

1. **`dependents_total_count` influenza solo la dimensione "dependency".** Nuovo test che confronta due analisi identiche differenti solo per il valore dei dependents: tutte le altre dimensioni, Confidence, e Risk restano bit-per-bit identiche.
2. **La chiave `"dependencies"` di T-19 non deve mai essere letta come dependents.** Verificato sia staticamente (grep del codice: `depsdev_dependents_evidence.py` legge solo `snap.get("dependents")`, mai `"dependencies"`) sia dinamicamente, con due test: uno snapshot che ha solo la chiave T-19 (`NOT_AVAILABLE`, mai il valore 31/37 di T-19), e uno snapshot con **entrambe** le chiavi presenti insieme (adversariale), dove il valore letto è quello di `"dependents"` (22.623), non quello di `"dependencies"`.
3. **Sensibilità dell'ancora `1000`.** Curva calcolata su valori rappresentativi (0, 1, 68, 500, 1000, 3041, 9397, 22623, 100000): monotona e limitata a [0, 100], nessun valore patologico (NaN, negativo, fuori scala).

## 4. Finding — non corretto, solo documentato

**L'ancora `1000` per `dependents_total_count` satura molto presto rispetto ai valori reali osservati in T-20A.**

| Dependents (reali, T-20A) | Punteggio normalizzato |
|---|---|
| 0 | 0.00 |
| 1 | 10.03 |
| 68 (serde) | 61.29 |
| 500 | 89.98 |
| 1.000 | 100.00 |
| 3.041 (requests) | 100.00 |
| 9.397 (guava) | 100.00 |
| 22.623 (lodash) | 100.00 |

Tre progetti reali con dependents molto diversi tra loro (3.041, 9.397, 22.623 — quasi un ordine di grandezza di differenza) **ottengono lo stesso punteggio identico, 100.0**, perdendo ogni discriminazione una volta superata la soglia. Il curve stesso, essendo logaritmico, comprime la discriminazione quasi tutta sotto le poche centinaia di dependents.

**Non ho corretto questo comportamento**, come richiesto esplicitamente ("Non cambiare metodologia, pesi o anchor solo perché un test evidenzia una caratteristica discutibile"). L'ancora resta `1000`, dichiarata ipotesi in `config/scoring.yaml` fin da T-20. Segnalo qui che, se e quando emergerà un corpus reale più ampio (§48), questo è il primo candidato per una revisione dell'ancora — probabilmente verso un valore più alto, o verso un confronto in percentile piuttosto che un'ancora assoluta (opzione già discussa in D-01 come alternativa futura).

## 5. Limiti residui

- La validazione su repository reali diversificati (T-14/T-22) resta bloccata dall'ambiente di sviluppo, indipendentemente da T-21.
- Il red-team qui è ancora unitario/sintetico più fixture reali di T-19A/T-20A; nessun red-team è stato eseguito contro l'API deps.dev dal vivo in questo task (non necessario: T-21 verifica il motore, non la fonte, già verificata in T-18/T-19A/T-20A).
- Nessuna nuova metrica, peso, soglia o normalizzazione è stata introdotta.

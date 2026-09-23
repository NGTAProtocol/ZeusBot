# DECISIONS

Registro delle decisioni (Directive v6.0 §54). Le decisioni critiche sono approvate esplicitamente dal fondatore; le altre sono scelte "più semplici possibili" prese durante l'implementazione e restano contestabili.

---

## D-00 — La Directive v6.0 sostituisce la Specification v3.0 dove sono in conflitto
- **Decision:** in caso di conflitto (roadmap, posizione del token) prevale la v6.0.
- **Context:** la v3.0 prevede il token in Fase 8, la v6.0 in Phase 15; la v3.0 Fase 1 è "formalizzazione", la v6.0 Phase 1 è "Impact Engine".
- **Alternatives:** chiedere una riconciliazione esplicita.
- **Reason:** la v6.0 è successiva e più restrittiva.
- **Consequences:** nessuna per v0.1.
- **Date / Version:** 2026-09-23 / GHIM-IMPACT-0.1
- **Status:** adottata, non critica.

## D-01 — Normalizzazione logaritmica con ancore dichiarate ✅ APPROVATA
- **Decision:** ogni metrica è normalizzata 0–100 con `ln(1+x)/ln(1+anchor)` (saturante o decrescente). Le ancore sono in `config/scoring.yaml` e dichiarate come ipotesi.
- **Context:** la formula §10 non definiva la normalizzazione (audit CF-1).
- **Alternatives:** percentile su corpus di riferimento; soglie lineari.
- **Reason:** deterministica per singolo progetto, indipendente dagli altri progetti, smorza i valori estremi.
- **Consequences:** le ancore sono arbitrarie finché non esiste un corpus reale (§48). Oltre l'ancora non c'è guadagno: questo limita anche la manipolazione (vedi test red-team).
- **Date / Version:** 2026-09-23 / GHIM-IMPACT-0.1

## D-02 — Aggregazione con dati mancanti ✅ CONFERMATA (2026-09-23, seconda conferma)
- **Decision (regole confermate testualmente):**
  1. Coverage < 60% → `INSUFFICIENT_EVIDENCE`.
  2. Devono essere osservabili almeno 2 dimensioni (`min_observable_dimensions: 2`).
  3. Al massimo una delle due dimensioni principali (Adoption, Dependency) può essere mancante (`max_missing_core_dimensions: 1`).
  4. Se **entrambe** Adoption e Dependency sono mancanti → `INSUFFICIENT_EVIDENCE`.
  5. Quando il ricalcolo è consentito, i pesi si ricalcolano **esclusivamente** sulle dimensioni disponibili.
  6. Il report deve mostrare **sempre**: (a) pesi originali, (b) pesi ricalcolati, (c) dimensioni mancanti, (d) motivo del ricalcolo.
- **Context:** Regola 3 vs somma pesata fissa (audit CF-2).
- **Dimensioni principali (confermato):** Adoption e Dependency, entrambe con peso iniziale del 25%.
- **Consequences:** vedi **D-11** (risolto: Opzione 1 approvata).
- **Implementazione del punto 6d (motivo del ricalcolo):** nuovo campo `impact.renormalization_reason` (stringa, popolato solo quando `weights_renormalized` è vero), reso in Markdown come sezione "Reason for recalculation". Non è un cambio di metodologia (nessun peso, ancora o soglia modificata): resta `GHIM-IMPACT-0.1`, è un'estensione del formato di report per trasparenza. Testato in `test_report_always_shows_weights_and_recalculation_reason`.
- **Date / Version:** 2026-09-23 / GHIM-IMPACT-0.1 (report format esteso, stessa metodologia)

## D-03 — V0.1 solo GitHub ✅ APPROVATA, NON MODIFICARE ANCORA (confermato 2026-09-23)
- **Decision:** unica fonte la GitHub REST API. Adoption e Dependency sono `NOT_AVAILABLE`, mai zero.
- **Consequences:** Coverage massima raggiungibile in v0.1 = 50% (vedi D-11).
- **Vincolo esplicito (ribadito 2026-09-23):** NON aggiungere deps.dev, né alcuna seconda fonte, finché non è verificata sotto il profilo di:
  disponibilità · affidabilità · qualità dei dati · copertura · provenance · stabilità dell'API · riproducibilità · limiti e rate limits.
- **Date / Version:** 2026-09-23 / GHIM-IMPACT-0.1

## D-04 — Confidence, Coverage, Risk come metriche indipendenti ✅ APPROVATA CON CONDIZIONE
- **Decision:** tre funzioni separate (`compute_coverage`, `compute_confidence`, `assess_risk`), ciascuna testata e versionata con la metodologia. Nessuna modifica l'Impact Score.
  - **Coverage** = Σ pesi delle dimensioni osservabili ÷ Σ pesi delle dimensioni applicabili.
  - **Confidence** = media pesata della confidence delle evidenze usate. Il Risk produce un fattore riportato separatamente (`base`, `risk_adjustment_factor`, `adjusted`).
  - **Risk** = massimo livello tra i segnali, ciascuno con evidenze e valori osservati. Un segnale è un'anomalia, non una frode.
- **Verifica della condizione:** `test_risk_never_changes_impact_or_dimension_scores`, `test_confidence_is_independent_of_impact`.
- **Date / Version:** 2026-09-23 / GHIM-IMPACT-0.1

## D-09 — Posizione del codice ✅ APPROVATA
- **Decision:** il progetto vive nella cartella `ghimoney/` alla radice del repository `ZeusBot`.
- **Date:** 2026-09-23

## D-10 — Scelte implementative non critiche
- **Snapshot = cache.** Ogni analisi legge solo da uno snapshot SQLite con hash (contenuto delle risposte + `as_of`). Lo scoring non chiama mai la rete. Motivo: §43 e §45 con un solo meccanismo.
- **`project_id` = `ghp-` + sha256(`github-repo-id:<id numerico>`)[:16].** Deterministico, stabile dopo rename e transfer. I collegamenti tra progetti (fork, successor) non sono automatici. La storia dei nomi è registrata in `name_observations`.
- **Metriche per dimensione** (vedi METHODOLOGY.md). Le assenze non dimostrabili (nessuna GitHub Release, nessun workflow Actions) sono `UNKNOWN`, non zero. L'assenza di `SECURITY.md` nei tre percorsi standard è invece un fatto verificato (`absence_check`, confidence 60%).
- **Nessun codice del repository analizzato viene clonato o eseguito** (§21).
- **Token GitHub** solo da `GITHUB_TOKEN` (variabile d'ambiente).
- **Moduli piatti invece di sotto-package** (§41 consente di adattare): ogni modulo è piccolo e le sotto-cartelle vuote non aggiungerebbero nulla.
- **CLI con `argparse`** della libreria standard: nessuna dipendenza aggiuntiva (§40).
- **Metodologie 0.x scritte dal fondatore.** Le metodologie `0.x` sono scritte dal fondatore (con l'assistente), non sono vincolanti e **nessun risultato 0.x sarà mai usato per un finanziamento**. La prima metodologia usata per fondi reali (1.0) richiede review esterna e un processo di governance (Regole 13 e 14, audit §18).
- **Date:** 2026-09-23

## D-11 — D-02 + D-03 impediscono qualsiasi Impact Score in v0.1 ✅ APPROVATA OPZIONE 1 (confermata, definizione di "completo" chiarita)
- **Context:** con sola GitHub (D-03), Adoption (25%) e Dependency (25%) sono sempre mancanti. La Coverage massima è quindi 50% < 60%, e mancano entrambe le dimensioni principali. **Ogni repository reale ottiene `INSUFFICIENT_EVIDENCE`.**
- **Decision: OPZIONE 1 APPROVATA.** V0.1 può essere considerato **completo** anche senza Impact Score finale sui repository reali, quando le evidenze disponibili non superano le soglie metodologiche definite (D-02). Non è un bug: è una limitazione metodologica deliberata e documentata. **Le regole non devono essere modificate per ottenere artificialmente un Impact Score.**
- **V0.1 deve produrre comunque, ed è verificato che produca:**
  1. punteggi delle singole dimensioni osservabili (`report["dimensions"]`);
  2. Coverage (`report["coverage"]`);
  3. Confidence (`report["confidence"]`);
  4. Risk (`report["risk"]`);
  5. stato `INSUFFICIENT_EVIDENCE` quando applicabile, con i motivi (`impact.reasons`);
  6. report JSON e Markdown completamente tracciabili e riproducibili (hash di config, snapshot e report; determinismo testato anche tra processi).
- **Vincolo assoluto:** NON pubblicare un "punteggio parziale" come Impact Score. Nessun "Partial Impact", "GitHub-observable score" o simile può mai apparire nel campo `impact.score` o essere presentato come Impact Score. Testato in `test_no_partial_score_is_ever_reported_as_impact`.
- **Obiettivo prioritario dichiarato:** meglio nessun punteggio che un punteggio apparentemente preciso basato su evidenze insufficienti.
- **Sequenza operativa approvata:**
  ```
  V0.1 → validazione reale → verifica deps.dev → eventuale aggiornamento D-03
       → implementazione Dependency evidence → Impact Score completo
       → nuova batteria di test → regression test → red-team
       → validazione su repository reali diversificati
  ```
  Nessun passo inizia prima che il precedente sia chiuso (vedi TASKS.md).
- **Date / Version:** 2026-09-23 / GHIM-IMPACT-0.1

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

## D-02 — Aggregazione con dati mancanti ✅ APPROVATA CON MODIFICHE, PARAMETRI CONFERMATI
- **Decision:**
  - Coverage < 60% → `INSUFFICIENT_EVIDENCE`, nessun Impact Score finale.
  - Coverage ≥ 60% → pesi ricalcolati solo tra le dimensioni misurabili; il report mostra dimensioni mancanti, pesi originali e pesi effettivi.
  - Nessun ricalcolo se resta osservabile una sola dimensione (`min_observable_dimensions: 2`).
  - Nessun ricalcolo se manca una parte eccessiva delle dimensioni principali (`max_missing_core_dimensions: 1`).
- **Context:** Regola 3 vs somma pesata fissa (audit CF-2).
- **Consequences:** vedi **D-11** (risolto: Opzione 1 approvata).
- **Parametri: CONFERMATI il 2026-09-23.** "Dimensioni principali" = Adoption e Dependency (le due al 25%), con al massimo 1 mancante (`core: true` in `config/scoring.yaml`, `max_missing_core_dimensions: 1`). Nessuna modifica al codice necessaria (T-17 chiuso).
- **Date / Version:** 2026-09-23 / GHIM-IMPACT-0.1

## D-03 — V0.1 solo GitHub ✅ APPROVATA
- **Decision:** unica fonte la GitHub REST API. Adoption e Dependency sono `NOT_AVAILABLE`, mai zero. deps.dev entra solo dopo una verifica di qualità e affidabilità.
- **Consequences:** Coverage massima raggiungibile in v0.1 = 50% (vedi D-11).
- **Vincolo esplicito (confermato 2026-09-23):** NON aggiungere deps.dev, né alcuna seconda fonte, finché non è stata verificata (copertura, affidabilità, termini d'uso, stabilità dell'API). L'aggiunta di una fonte non verificata a "IMPACT_ENGINE_V0.1" non è consentita.
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

## D-11 — D-02 + D-03 impediscono qualsiasi Impact Score in v0.1 ✅ APPROVATA OPZIONE 1
- **Context:** con sola GitHub (D-03), Adoption (25%) e Dependency (25%) sono sempre mancanti. La Coverage massima è quindi 50% < 60%, e mancano entrambe le dimensioni principali. **Ogni repository reale ottiene `INSUFFICIENT_EVIDENCE`.** Il criterio di accettazione §73-C ("Produce Impact Score") non è soddisfacibile senza cambiare una delle due decisioni.
- **Alternatives considerate:**
  1. accettare v0.1 senza Impact Score finale, in attesa di una seconda fonte verificata;
  2. anticipare deps.dev (dopo verifica) per coprire Dependency;
  3. pubblicare un "Partial Impact (GitHub-observable)" etichettato come non comparabile.
- **Decision: OPZIONE 1 APPROVATA.** v0.1 resta senza Impact Score finale su repository reali. Questa è una limitazione metodologica dichiarata, non un fallimento tecnico: Impact, Confidence, Coverage e Risk restano corretti e testati; manca solo la seconda fonte per le dimensioni principali.
- **Vincoli espliciti che ne derivano:**
  - **NON aggiungere deps.dev** (o altra fonte) finché non è stata verificata — vedi D-03.
  - **NON pubblicare punteggi parziali come Impact Score.** Nessun "Partial Impact", "GitHub-observable score" o simile deve mai apparire nel campo `impact.score` o essere presentato come Impact Score. I punteggi per dimensione (Maintenance, Quality, Security, Community) restano visibili nel report solo come tali, mai aggregati in sostituzione dell'Impact.
- **Sequenza approvata:** V0.1 → validazione reale → verifica deps.dev → D-03 aggiornata → Impact Score completo → nuova batteria di test.
- **Date / Version:** 2026-09-23 / GHIM-IMPACT-0.1

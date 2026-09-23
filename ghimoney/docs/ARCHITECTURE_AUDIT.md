# GHIMONEY ARCHITECTURE AUDIT

- **Documento auditato:** GHIMONEY Master Build Directive v6.0 (con riferimento alla Blockchain Protocol & Native Token Specification v3.0)
- **Data:** 2026-09-23
- **Stato:** audit iniziale, nessun codice scritto
- **Ambito:** §76 STEP 1–5. Lo STEP 6 (approvazione delle decisioni critiche) è in attesa.

Convenzioni: ogni problema riporta SEVERITY / PROBLEM / WHY IT MATTERS / RECOMMENDED SOLUTION / BLOCKS IMPLEMENTATION.
Le affermazioni su sistemi esterni che non ho verificato in questa sessione sono marcate **[DA VERIFICARE]** (§1, regola "non inventare").

---

## 0. AUDIT DEL REPOSITORY ESISTENTE (STEP 1)

Il repository `NGTAProtocol/ZeusBot` è vuoto: nessun file, nessun commit, nessun branch sul remote.
Non esistono codice, dati, configurazioni o decisioni precedenti da riconciliare.

| Punto | Esito |
|---|---|
| Codice esistente | Nessuno |
| Conflitti con codice esistente | Nessuno |
| Nome del repository | `ZeusBot`, mentre il progetto si chiama `ghimoney` (vedi D-09) |

---

## 1. ARCHITECTURE VERDICT

**Verdetto: SOLIDA NEI PRINCIPI, INCOMPLETA NELLA METODOLOGIA.**

La v6.0 è corretta su tre punti. Separa denaro e punteggio (Regole 1, 12, 13). Costruisce le componenti nell'ordine giusto: misura, poi finanziamento, poi token (§51, §66). Tratta l'incertezza come un output di prima classe: missing ≠ zero, Confidence e Coverage separate, "INSUFFICIENT EVIDENCE".

Il problema principale non è l'architettura ma la **metodologia dell'Impact Score**, che è indefinita proprio dove v0.1 deve essere implementata:

1. non è definito come i dati grezzi diventano sotto-punteggi 0–100 (normalizzazione);
2. non è definito come l'aggregazione pesata tratta un sotto-punteggio mancante (Regola 3 vs formula §10);
3. il 50% del peso (Adoption + Dependency) dipende da dati che la sola GitHub API non fornisce in modo affidabile;
4. Confidence, Coverage e Risk sono richiesti come output ma non hanno una definizione operativa.

Sono decisioni metodologiche con effetti economici futuri, quindi per §1 non posso sceglierle da solo. Vanno approvate prima dello STEP 7.

---

## 2. CRITICAL FLAWS

### CF-1. Normalizzazione non definita
- **SEVERITY:** CRITICAL
- **PROBLEM:** la formula §10 somma sotto-punteggi (Adoption, Dependency…) senza specificare come i dati grezzi (stelle, download, commit, advisory) diventano valori confrontabili. Le opzioni hanno proprietà molto diverse:
  - **(a) soglie assolute / scala logaritmica con tetti dichiarati:** deterministica per singolo progetto e indipendente dagli altri. I tetti però sono arbitrari.
  - **(b) percentile rispetto a un corpus di riferimento:** relativa, e dipende da quale corpus è stato scelto (bias di selezione). Per essere deterministica il corpus va versionato come parte della metodologia.
  - **(c) ibrido:** (a) in v0.1, (b) quando esisterà un corpus reale (§48).
- **WHY IT MATTERS:** la normalizzazione decide chi vince. Una scala lineare sulle stelle schiaccia i piccoli progetti (§11, "piccola libreria"); un percentile rende il punteggio di un progetto dipendente dagli altri.
- **RECOMMENDED SOLUTION:** (c). Per v0.1 una scala logaritmica con ancore dichiarate in `config/scoring.yaml`, marcata esplicitamente come ipotesi. Percentile solo quando esiste un corpus versionato.
- **BLOCKS IMPLEMENTATION:** YES (decisione D-01)

### CF-2. Aggregazione con dati mancanti
- **SEVERITY:** CRITICAL
- **PROBLEM:** la Regola 3 vieta di trasformare dati mancanti in zero. Ma la formula §10 è una somma pesata fissa e non dice cosa fare se, per esempio, Dependency è `NOT_AVAILABLE`. Le opzioni:
  - **(a) rinormalizzare i pesi** sui componenti disponibili: il punteggio resta calcolabile, ma un progetto poco osservabile può ottenere un Impact alto su poche metriche. È un vettore di gaming: si nascondono i dati sfavorevoli.
  - **(b) valore neutro imputato** (es. 50): introduce un numero inventato. Viola lo spirito della Regola 3.
  - **(c) soglia di Coverage:** se la Coverage pesata è sotto la soglia, `Impact = INSUFFICIENT_EVIDENCE` (§64). Sopra la soglia si applica (a), e la Coverage viene sempre riportata accanto al punteggio.
- **WHY IT MATTERS:** è il punto di contatto diretto tra la Regola 3, la §64 e la resistenza al gaming.
- **RECOMMENDED SOLUTION:** (c).
- **BLOCKS IMPLEMENTATION:** YES (decisione D-02, inclusa la soglia)

### CF-3. Adoption e Dependency non misurabili con la sola GitHub API
- **SEVERITY:** CRITICAL
- **PROBLEM:** lo scope v0.1 (§72) dice "GitHub API", ma Adoption (25%) e Dependency (25%) richiedono download dai package registry e conteggi dei dependents. Per quanto mi risulta:
  - la GitHub REST API non espone il conteggio "Used by" / dependents mostrato nell'interfaccia web **[DA VERIFICARE]**;
  - l'endpoint del dependency graph (SBOM) restituisce le dipendenze *del* repository, non chi dipende *da* esso **[DA VERIFICARE]**;
  - le Traffic API (views/clones) richiedono permessi di push sul repository, quindi non sono utilizzabili per repository di terzi;
  - l'unico dato di adozione nativo di GitHub resta stars/forks/watchers. Usarlo come Adoption contraddice di fatto la Regola 2.
- **WHY IT MATTERS:** con la sola GitHub API il 50% della formula sarebbe `NOT_AVAILABLE` per quasi ogni progetto, oppure verrebbe riempito da proxy di popolarità, cioè esattamente ciò che la Regola 2 vieta.
- **RECOMMENDED SOLUTION:** tre alternative da scegliere:
  - **(a)** v0.1 solo GitHub, con Adoption/Dependency dichiarati `NOT_AVAILABLE`. Onesto, ma l'Impact v0.1 misurerebbe quasi solo Maintenance/Quality/Community.
  - **(b)** aggiungere in v0.1 una fonte multi-ecosistema per i dependents (candidato: deps.dev di Google/Open Source Insights **[DA VERIFICARE: copertura, API, termini d'uso]**).
  - **(c)** aggiungere 1–2 registry specifici (es. PyPI + npm) **[DA VERIFICARE: endpoint ufficiali per le statistiche di download]**. Crea un bias di ecosistema (§11, §63).

  Raccomando (a) + (b): prima si implementa (a) in modo pulito, poi si aggiunge (b) come seconda fonte dopo averla verificata.
- **BLOCKS IMPLEMENTATION:** YES (decisione D-03)

### CF-4. Confidence, Coverage e Risk senza definizione operativa
- **SEVERITY:** HIGH
- **PROBLEM:** §17–19 descrivono cosa esprimono, non come si calcolano.
- **WHY IT MATTERS:** senza definizione, questi tre numeri diventano "falsa precisione" (§64).
- **RECOMMENDED SOLUTION:** proposta per v0.1, da approvare:
  - **Coverage** = somma dei pesi dei componenti con stato `VERIFIED` o calcolabile ÷ somma dei pesi dei componenti applicabili (`NOT_APPLICABLE` escluso dal denominatore).
  - **Confidence** = media pesata della confidence dei singoli Evidence Record. La confidence di ogni fonte è dichiarata in config per tipo di fonte, e ridotta se c'è un'anomalia Risk sulla stessa metrica. Esplicitamente euristica in v0.1.
  - **Risk** = livello massimo tra i segnali rilevati. Ogni segnale ha una regola dichiarata e le sue evidenze. Nessun segnale implica frode (Regola 11).
- **BLOCKS IMPLEMENTATION:** YES (decisione D-04, approvazione della proposta)

### CF-5. Determinismo con API "live"
- **SEVERITY:** HIGH
- **PROBLEM:** §45 richiede lo stesso risultato a parità di snapshot, ma un'API live cambia ogni minuto. Anche metriche come "giorni dall'ultimo commit" dipendono dall'istante di esecuzione.
- **WHY IT MATTERS:** senza uno snapshot esplicito il test "run A == run B" non ha senso.
- **RECOMMENDED SOLUTION:** ogni analisi produce uno **snapshot**, cioè le risposte grezze salvate in SQLite con hash del contenuto e un `as_of` fisso. Lo scoring legge solo dallo snapshot, mai dalla rete. Il report contiene `snapshot_hash` e `as_of`. La cache (§43) e lo snapshot coincidono.
- **BLOCKS IMPLEMENTATION:** NO (soluzione più semplice, documentabile in DECISIONS.md)

---

## 3. PROJECT IDENTITY ANALYSIS

- **SEVERITY:** MEDIUM
- **PROBLEM:** §5 richiede un `project_id` stabile. Non specifica come generarlo né chi è autorizzato a collegare o scollegare repository (fork, successor, merge).
- **WHY IT MATTERS:** collegare un repository a un progetto ne trasferisce la storia di Impact. È un vettore di attacco ("fake project identity", §49).
- **RECOMMENDED SOLUTION:**
  - v0.1: registry locale in SQLite. Il `project_id` viene assegnato una volta e poi resta stabile. Ogni repository è ancorato al suo **ID numerico GitHub**, che per quanto mi risulta resta invariato dopo rename e transfer **[DA VERIFICARE nei test reali]**, oltre che a `owner/name`.
  - I collegamenti tra progetti (fork, successor, merge) **non** sono automatici in v0.1. Sono solo manuali, versionati e con motivazione.
  - La governance dell'identità (chi approva un collegamento) va rinviata alla fase Human Review/Challenge.
- **BLOCKS IMPLEMENTATION:** NO

## 4. PROJECT CREDENTIAL ANALYSIS

- **SEVERITY:** LOW (per v0.1)
- **PROBLEM:** §6 è ben impostato: identità + reputazione + storico, non un token speculativo. Resta aperta la forma: registry, attestation, credenziale non trasferibile o ERC-721.
- **WHY IT MATTERS:** un credential trasferibile, come un ERC-721 standard, renderebbe la reputazione un asset vendibile. Questo contraddice la §67 ("NFT speculativi") e permetterebbe di comprare la storia di Impact di un progetto.
- **RECOMMENDED SOLUTION:** il credential è, in prima istanza, una **vista derivata**: lo storico dei report finalizzati indicizzato per `project_id`. In v0.1 è semplicemente l'insieme dei report JSON. La forma on-chain va decisa in Phase 9, con un requisito minimo di **non trasferibilità**.
- **BLOCKS IMPLEMENTATION:** NO

## 5. EVIDENCE MODEL ANALYSIS

- **SEVERITY:** MEDIUM
- **PROBLEM:** il record §8 è solido. Mancano però alcuni campi necessari per la verificabilità (§2):
  - `retrieved_at`, distinto dal `timestamp` del dato;
  - `source_endpoint` / `source_version`;
  - `raw_hash`, cioè l'hash della risposta grezza;
  - `as_of`, l'istante logico dell'analisi.

  Inoltre il campo `status` sovrappone due assi diversi: stato del dato (UNKNOWN, NOT_AVAILABLE…, Regola 3) e stato di verifica (VERIFIED).
- **WHY IT MATTERS:** senza hash e endpoint un osservatore terzo non può ricostruire da dove viene un numero.
- **RECOMMENDED SOLUTION:** aggiungere i campi e separare `availability` (le 5 categorie della Regola 3) da `verification` (UNVERIFIED / VERIFIED).
- **BLOCKS IMPLEMENTATION:** NO (lo definisco nei modelli e lo documento)

## 6. IMPACT ENGINE ANALYSIS

- **SEVERITY:** CRITICAL (vedi CF-1, CF-2, CF-3)
- **Ulteriori problemi:**
  - **HIGH:** i sei componenti non hanno una lista di metriche. "Quality" e "Security" possono voler dire molte cose. v0.1 richiede un elenco esplicito metrica → componente, approvato.
  - **MEDIUM:** Maintenance e Community misurate su GitHub sono **manipolabili** (commit artificiali, bot contributor). Il Risk Engine deve osservare le stesse metriche su cui si basa lo scoring.
  - **MEDIUM:** un punteggio 0–100 assoluto suggerisce una precisione che la v0.1 non ha. Raccomando di riportarlo sempre con Confidence, Coverage e la dicitura "methodology GHIM-IMPACT-0.1, pesi ipotetici".
- **BLOCKS IMPLEMENTATION:** YES, per la lista metriche (inclusa nella decisione D-04)

## 7. BIAS ANALYSIS

- **SEVERITY:** HIGH
- **PROBLEM:** con le sole fonti GitHub:
  - **popularity bias:** stars/forks;
  - **size bias:** più commit, più contributor;
  - **age bias:** accumulo storico;
  - **language/ecosystem bias:** GitHub non è l'unica forge. GitLab, Codeberg e altre sono escluse per costruzione.
- **WHY IT MATTERS:** §63 (neutralità) non è dimostrabile con una sola forge.
- **RECOMMENDED SOLUTION:**
  - v0.1: metriche **normalizzate per età e dimensione** dove possibile (tassi, non totali);
  - i bias noti vanno dichiarati in `METHODOLOGY.md` alla voce "limiti";
  - il golden set per §48 va costruito con categorie bilanciate (piccole librerie vs framework).
- **BLOCKS IMPLEMENTATION:** NO

## 8. DEPENDENCY GRAPH ANALYSIS

- **SEVERITY:** HIGH
- **PROBLEM:** oltre a CF-3, un grafo transitivo richiede dati a livello di ecosistema, non di singolo repository. Il conteggio grezzo dei dependents è facilmente gonfiabile ("dependency inflation", §49): basta pubblicare molti pacchetti vuoti che dipendono dal target.
- **WHY IT MATTERS:** Dependency pesa il 25%.
- **RECOMMENDED SOLUTION:** in v0.1 solo il conteggio diretto (se la fonte è approvata) con un `dependency_risk` sui dependents di bassa qualità. Il grafo transitivo, con i dependents pesati per la propria qualità (tipo PageRank), va in Phase 2 come da §66.
- **BLOCKS IMPLEMENTATION:** NO

## 9. CONFIDENCE / COVERAGE / RISK ANALYSIS

Vedi CF-4. In aggiunta:
- **SEVERITY:** MEDIUM
- **PROBLEM:** "anomalous star growth" richiede i timestamp delle singole stelle. È costoso: centinaia di richieste paginate per repository grandi, e l'API potrebbe limitare la paginazione **[DA VERIFICARE]**.
- **RECOMMENDED SOLUTION:** in v0.1 solo segnali economici (rapporti tra metriche, es. stars/contributor, forks/stars, attività recente vs storica). La serie temporale delle stelle diventa opzionale, con un flag.
- **BLOCKS IMPLEMENTATION:** NO

## 10. AI AUDITOR ANALYSIS

- **SEVERITY:** MEDIUM (fuori scope v0.1)
- **PROBLEM:** gli output di un LLM non sono deterministici e contrastano con §45. Un repository analizzato può inoltre contenere prompt injection ("AI manipulation", §37).
- **RECOMMENDED SOLUTION:**
  - gli audit AI sono **evidenze registrate**: l'output salvato con hash viene letto, non ricalcolato;
  - il contenuto del repository è sempre dato, mai istruzione;
  - gli output AI non entrano mai nella formula dell'Impact, solo in findings e Risk (coerente con la Regola 5).
- **BLOCKS IMPLEMENTATION:** NO

## 11. HUMAN REVIEW ANALYSIS

- **SEVERITY:** HIGH (design, fuori scope v0.1)
- **PROBLEM:** §22 chiede di incentivare "l'accuratezza del giudizio". Per l'impatto però non esiste una ground truth. Misurare l'accuratezza come accordo con la maggioranza punisce il dissenso, e la v3.0 §14 lo vieta esplicitamente.
- **WHY IT MATTERS:** è la stessa trappola dei sistemi di peer-prediction: produce conformismo.
- **RECOMMENDED SOLUTION:** penalizzare solo:
  - violazioni verificabili (conflitto di interessi non dichiarato, fatti falsi dimostrabili);
  - esiti di challenge.

  Mai la semplice distanza dalla media. Da progettare in Phase 4.
- **BLOCKS IMPLEMENTATION:** NO

## 12. COMMUNITY VOTING ANALYSIS

- **SEVERITY:** HIGH
- **PROBLEM:** **dipendenza circolare nella roadmap.** §23 prevede un costo di voto in GHIM, ma il token arriva al passo 28 (§51) e in Phase 15 (§66), mentre il Community Signal è al passo 17 / Phase 5.
- **WHY IT MATTERS:** o il voto aspetta il token, oppure serve un meccanismo anti-spam diverso.
- **RECOMMENDED SOLUTION:** decisione da prendere prima di Phase 5, non ora. Alternative: identità verificata (account GitHub con storico minimo), rate limit, oppure deposito in stablecoin su testnet.
- **BLOCKS IMPLEMENTATION:** NO (decisione D-05, rinviabile)

## 13. ANTI-SYBIL ANALYSIS

- **SEVERITY:** MEDIUM
- **PROBLEM:** il principio "ANOMALY prima di FRAUD" (§24) è corretto. Manca però un'identità di base: senza di essa l'anti-Sybil può solo rilevare pattern, non prevenirli.
- **RECOMMENDED SOLUTION:** v0.1 produce solo flag di anomalia sui contributor (account nuovi, attività sincronizzata) come segnali Risk. Identità e Sybil-resistance vanno in Phase 4–5.
- **BLOCKS IMPLEMENTATION:** NO

## 14. CHALLENGE SYSTEM ANALYSIS

- **SEVERITY:** MEDIUM
- **PROBLEM:**
  - la pipeline §25 è corretta, ma chi giudica una challenge? Se sono gli stessi reviewer del risultato contestato, c'è conflitto;
  - il deposito in GHIM ha la stessa circolarità del §12;
  - un deposito alto esclude chi ha poche risorse, uno basso permette lo spam.
- **RECOMMENDED SOLUTION:** challenge giudicate da un panel distinto da chi ha prodotto il risultato. Il deposito va progettato in Phase 6 con le simulazioni. In v0.1 il report deve già esporre **tutto** ciò che è contestabile (dati, fonte, metodo), come prerequisito tecnico.
- **BLOCKS IMPLEMENTATION:** NO

## 15. FUNDING MODEL ANALYSIS

- **SEVERITY:** HIGH
- **PROBLEM:**
  1. **Tensione concettuale:** il Retroactive PGF finanzia valore *già dimostrato*, mentre l'Emerging Impact Fund (§12) finanzia *potenziale* con milestone (§13). Quest'ultimo è un grant prospettico, non retroattivo. È legittimo, ma è un meccanismo diverso, con rischi e regole diverse.
  2. L'Emerging Fund è più facile da manipolare: in un pool di progetti piccoli, poche stelle o pochi download falsi pesano molto di più.
  3. La funzione Impact → allocazione non è assegnata a nessun componente. La Regola 12 separa Impact Engine e Treasury, ma serve un **Funding Engine** con regole proprie (approvate dalla governance) che traduca Impact/Confidence/Risk in importi.
- **RECOMMENDED SOLUTION:**
  - dichiarare esplicitamente che l'Emerging Fund è un meccanismo prospettico;
  - soglie di Confidence più alte e Risk più restrittivo per l'Emerging Fund;
  - Funding Engine come terzo componente separato: Impact Engine → **Funding Engine** → Treasury.
- **BLOCKS IMPLEMENTATION:** NO

## 16. MILESTONE / MONITORING ANALYSIS

- **SEVERITY:** MEDIUM
- **PROBLEM:** chi definisce le milestone? Se le propone il progetto stesso, sceglierà milestone facili. Le milestone di "Adoption" (download, utenti) sono le metriche più manipolabili.
- **RECOMMENDED SOLUTION:** le milestone sono proposte dal progetto e approvate in review. Le milestone di adoption richiedono Confidence minima e superamento dei controlli Risk. Da progettare in Phase 8.
- **BLOCKS IMPLEMENTATION:** NO

## 17. TREASURY ANALYSIS

- **SEVERITY:** MEDIUM
- **PROBLEM:**
  - la separazione dei poteri (§27) è corretta;
  - manca l'origine dei fondi in stablecoin: la v3.0 §7 elenca donazioni, sponsor e grant, ma nessuna è confermata;
  - nessun meccanismo protocollare garantisce che il Treasury abbia fondi.
- **RECOMMENDED SOLUTION:** il Treasury simulator (Phase 7) va costruito con scenari di funding pari a zero o scarso, e le regole devono gestire "nessun fondo disponibile" senza alterare l'Impact.
- **BLOCKS IMPLEMENTATION:** NO

## 18. FOUNDER / CONFLICT-OF-INTEREST ANALYSIS

- **SEVERITY:** HIGH
- **PROBLEM:** **contraddizione transitoria inevitabile.** §28 dice che il fondatore non deve modificare unilateralmente la metodologia. Ma in v0.x il fondatore (e questo assistente, sotto la sua direzione) *scrive* la metodologia. Non esiste ancora nessun altro organo.
- **WHY IT MATTERS:** se non viene dichiarato, è un privilegio nascosto (§28, "privilegi nascosti").
- **RECOMMENDED SOLUTION:** dichiarazione esplicita in `DECISIONS.md`:
  - le metodologie `0.x` sono founder-authored, non vincolanti e non collegate a fondi reali;
  - nessun risultato `0.x` sarà usato per un funding;
  - la prima metodologia usata per fondi reali (`1.0`) richiede review esterna e un processo di governance.
- **BLOCKS IMPLEMENTATION:** NO (documentazione)

## 19. TOKENOMICS ANALYSIS

- **SEVERITY:** HIGH (fuori scope v0.1)
- **PROBLEM:**
  1. il 35% della supply per il RetroPGF implica che i progetti ricevano GHIM, in tensione con §32 e v3.0 §5 (pagamento preferibilmente in asset stabili). Se i progetti ricevono GHIM, la pressione di vendita ricade su di loro;
  2. i 5% Team + 5% Partner + 2% Liquidity sono dichiarati preliminari, correttamente;
  3. **legale/regolatorio:** un token con allocazione al fondatore, fee di voto e distribuzione pubblica in UE rientra potenzialmente nel perimetro MiCA. Non sono in grado di dare un parere legale.
- **RECOMMENDED SOLUTION:**
  - `ECONOMICS.md` deve separare "riserva GHIM per incentivi all'ecosistema" dal "funding in asset stabili";
  - una consulenza legale è un prerequisito esplicito di Phase 13–15, da aggiungere ai criteri Mainnet (v3.0 §43).
- **BLOCKS IMPLEMENTATION:** NO

## 20. GOVERNANCE ANALYSIS

- **SEVERITY:** MEDIUM
- **PROBLEM:** la Regola 7 esclude "1 GHIM = 1 voto" senza proporre un'alternativa. Qualsiasi alternativa (quadratic, reputation-based, per camere) richiede identità resistente ai Sybil, che non esiste ancora.
- **RECOMMENDED SOLUTION:**
  - progressive decentralization (§60) come percorso dichiarato;
  - fino ad allora multisig con firmatari indipendenti e dichiarati;
  - la scelta del modello di voto va rinviata a quando esisterà un'identità.
- **BLOCKS IMPLEMENTATION:** NO

## 21. SMART CONTRACT ANALYSIS

- **SEVERITY:** LOW (fuori scope v0.1)
- **PROBLEM:** 8 contratti candidati (§38). Alcuni sono accorpabili: Epoch Manager e Impact Registry sono entrambi registri di commitment per epoch.
- **RECOMMENDED SOLUTION:** set minimo stimato per la prima testnet:
  - `EpochRegistry`: commitment della metodologia e delle evidence/impact root per epoch;
  - `Distribution`: claim tramite Merkle proof;
  - `Treasury` come multisig + timelock standard, non codice custom.

  Staking, Challenge, Governance e Token vanno aggiunti solo quando la rispettiva fase è validata.
- **BLOCKS IMPLEMENTATION:** NO

## 22. SECURITY THREATS

Minacce rilevanti **già per v0.1** (le altre vanno in `THREAT_MODEL.md`):

| # | Minaccia | Severity | Mitigazione v0.1 |
|---|---|---|---|
| T1 | Codice del repository eseguito dal tool | CRITICAL | v0.1 **non clona e non esegue** codice; usa solo metadati via API (§21) |
| T2 | Token GitHub esposto nel repo o nei report | HIGH | Token solo da variabile d'ambiente; i report non includono header |
| T3 | Contenuto del repository usato come istruzione (README, issue) | MEDIUM | v0.1 non usa AI; i campi testuali sono trattati come dati |
| T4 | Metriche gonfiate (stars, commit, bot) | HIGH | Segnali Risk v0.1 + Confidence ridotta |
| T5 | Snapshot manomesso localmente | MEDIUM | Hash dello snapshot nel report |
| T6 | Rename/transfer per ereditare la reputazione | MEDIUM | Ancoraggio all'ID numerico + collegamenti solo manuali |

## 23. COMPLEXITY RISKS

- **SEVERITY:** MEDIUM
- **PROBLEM:** l'architettura target ha ~19 componenti (§4). Il rischio non è in v0.1, che è ben delimitata, ma nella pressione a costruire in parallelo.
- **RECOMMENDED SOLUTION:**
  - rispettare §51 alla lettera;
  - v0.1 è un modular monolith con dipendenze minime (§40);
  - nessun componente di Phase ≥ 2 entra nel codice finché la Phase 1 non ha superato i criteri §73.
- **Omissione rilevata:** la **Contributor Attribution** (v3.0 §31) compare nella v6.0 solo come campo del credential e nella privacy (§36). Non ha un componente né un passo della roadmap. Da collocare esplicitamente, e da trattare con attenzione GDPR perché riguarda persone.

## 24. REQUIRED CHANGES

### Decisioni che richiedono approvazione (STEP 6)

| ID | Decisione | Blocca v0.1 | Raccomandazione |
|---|---|---|---|
| **D-01** | Metodo di normalizzazione | **SÌ** | Scala log con ancore dichiarate in config (ipotesi), percentile in futuro |
| **D-02** | Missing data nell'aggregazione | **SÌ** | Soglia di Coverage → `INSUFFICIENT_EVIDENCE`, sopra soglia pesi rinormalizzati; soglia proposta 60% |
| **D-03** | Fonti dati v0.1 oltre GitHub | **SÌ** | v0.1 solo GitHub (Adoption/Dependency `NOT_AVAILABLE` dichiarati), poi deps.dev dopo verifica |
| **D-04** | Definizioni Confidence/Coverage/Risk + lista metriche per componente | **SÌ** | Proposta in CF-4, dettagliata in `METHODOLOGY.md` prima del codice |
| D-05 | Anti-spam del Community Voting prima del token | No (Phase 5) | Rinviare |
| D-06 | Forma on-chain del Project Credential | No (Phase 9) | Non trasferibile; forma da decidere |
| D-07 | Regole di accuratezza dei reviewer | No (Phase 4) | Nessuna penalità per dissenso |
| D-08 | Consulenza legale sul token (MiCA) | No (Phase 13+) | Prerequisito Mainnet |
| D-09 | Posizione del package nel repo `ZeusBot` | No | `ghimoney` alla radice del repo `ZeusBot` |

### Decisioni non critiche che adotterò e documenterò in DECISIONS.md

- Snapshot = cache SQLite con hash; scoring solo offline dallo snapshot (CF-5).
- `project_id` assegnato dal registry locale; ancoraggio all'ID numerico GitHub.
- Evidence Record esteso (§5 di questo audit).
- Token GitHub da `GITHUB_TOKEN` (variabile d'ambiente), mai su disco.
- Dichiarazione "metodologie 0.x founder-authored, non vincolanti".
- Nessuna esecuzione o clonazione di codice analizzato in v0.1.

### Correzioni al documento v6.0 proposte

1. §13: sostituire "TOKEN / FUND RELEASE" con "FUND RELEASE", per coerenza con §32.
2. §4: aggiungere **FUNDING ENGINE** come confine esplicito tra Impact e Treasury (è già nella lista, ma senza definizione).
3. §4 / §51: collocare la **CONTRIBUTOR ATTRIBUTION**.
4. §12: dichiarare l'Emerging Fund come meccanismo prospettico.
5. Dichiarare che la v6.0 sostituisce la v3.0 dove sono in conflitto (roadmap, posizione del token).

## 25. V0.1 IMPLEMENTATION PLAN

Da avviare solo dopo l'approvazione di D-01…D-04.

| Passo | Contenuto | Criteri §73 coperti |
|---|---|---|
| 1 | `DECISIONS.md`, `ARCHITECTURE.md`, `METHODOLOGY.md` (GHIM-IMPACT-0.1), `THREAT_MODEL.md`, `ECONOMICS.md` (stub), `TASKS.md` | N |
| 2 | Modelli Pydantic: Project, RepositoryLink, EvidenceRecord, ComponentScore, ImpactResult | B, G |
| 3 | `config/scoring.yaml` con metodologia, pesi, ancore, soglie e versione | I |
| 4 | Ingestion GitHub (httpx) → snapshot SQLite con hash | A, B, H |
| 5 | Normalizzazione (D-01) | C |
| 6 | Impact + Coverage + Confidence (D-02, D-04) | C, D, E, G |
| 7 | Risk v0.1 con segnali economici | F |
| 8 | Report JSON + Markdown | J, K |
| 9 | CLI `ghimoney analyze owner/repo` | A |
| 10 | Test unit, golden, determinismo (run A == run B), missing data | H, L |
| 11 | Analisi di ~10 repository reali di categorie diverse (§48) | M |
| 12 | Red-team iniziale: fixture sintetiche con stars gonfiate, bot contributor, repository vuoti | O |
| 13 | Commit e push per ogni passo verificato (§52) | — |

**Dipendenze v0.1:** Python 3.11+, httpx, pydantic, pyyaml, pytest. Nessun'altra dipendenza senza una nuova voce in DECISIONS.md.

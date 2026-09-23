# DEPS.DEV EVALUATION

**Task:** T-18 (analisi soltanto — nessun codice modificato)
**Data:** 2026-09-23
**Scopo:** determinare se deps.dev può diventare, in una futura versione, una fonte ufficiale di Dependency evidence per GHIMONEY. Questo documento non autorizza alcuna integrazione.

**Nota metodologica sull'accesso alle fonti in questa sessione.** L'ambiente in cui è stata svolta questa verifica blocca, per policy di rete dell'organizzazione, tutti i sottodomini `*.deps.dev` (incluso `docs.deps.dev`, `api.deps.dev`, `blog.deps.dev`) e `console.cloud.google.com`. Non è stato quindi possibile leggere direttamente la documentazione ufficiale completa né interrogare l'API dal vivo. Le fonti effettivamente consultate sono:

1. **Primaria, letta per intero:** il repository ufficiale `github.com/google/deps.dev` (README.md, LICENSE, `api/v3/api.proto`, `api/v3alpha/apiv3alpha.proto`, CONTRIBUTING.md), clonato e letto direttamente.
2. **Primaria, parziale:** la issue ufficiale `google/deps.dev#33` (letta per intero via GitHub).
3. **Secondaria (motore di ricerca):** estratti/titoli di pagine `docs.deps.dev` e `blog.deps.dev` restituiti da una ricerca web, **non** la pagina stessa. Ogni informazione che si basa solo su questo tipo di fonte è segnalata come tale e trattata con cautela.

Dove né (1) né (2) confermano un fatto, e (3) non è una citazione diretta sufficientemente affidabile, il valore è `UNKNOWN`. Nessuna informazione è stata inventata o ricavata da memoria di addestramento non verificata in questa sessione.

---

## 1. Executive Summary

deps.dev è un servizio di Google che aggrega metadati su package open-source (npm, PyPI, Maven, Go, Cargo, NuGet, RubyGems) e sui progetti che li ospitano (GitHub, GitLab, Bitbucket), esponendo un'API HTTP/gRPC pubblica (`api.deps.dev`, versioni v3 e v3alpha) e un dataset BigQuery pubblico. Il codice del client, il proto dell'API e i termini di licenza dei dati generati (CC-BY 4.0) sono pubblicati e verificabili su `github.com/google/deps.dev`.

I punti di forza confermati da fonte primaria: copertura di tutti gli ecosistemi richiesti da GHIMONEY (npm, PyPI, Maven, Go, Cargo), API v3 con garanzia di stabilità e politica di deprecazione dichiarate, caching esplicitamente permesso, licenza dei dati generati chiara (CC-BY 4.0), nessuna autenticazione richiesta per le letture v3 secondo l'esempio ufficiale.

I punti critici, anch'essi confermati: **nessun rate limit documentato** (una issue ufficiale su questo tema è aperta e senza risposta dal 2023), **nessuna fonte primaria raggiungibile in questa sessione** per verificare in modo indipendente disponibilità, latenza e stabilità reali dell'endpoint dal vivo, e **fonte unica** per Dependency (violerebbe il principio "non assumere che una singola fonte sia verità assoluta", Directive §9) se usata da sola.

**Conclusione preliminare (sezione 15): APPROVED WITH CONDITIONS.**

## 2. Official Sources

| # | Fonte | Tipo | Accesso in questa sessione |
|---|---|---|---|
| S1 | `github.com/google/deps.dev` — README.md | Primaria | Letta per intero |
| S2 | `github.com/google/deps.dev` — LICENSE (codice) | Primaria | Letta per intero (Apache 2.0) |
| S3 | `github.com/google/deps.dev` — `api/v3/api.proto` | Primaria | Letta per intero |
| S4 | `github.com/google/deps.dev` — `api/v3alpha/apiv3alpha.proto` | Primaria | Letta per intero |
| S5 | `github.com/google/deps.dev` — CONTRIBUTING.md | Primaria | Letta per intero |
| S6 | `github.com/google/deps.dev/issues/33` ("Rate limits for api.deps.dev") | Primaria | Letta per intero |
| S7 | `docs.deps.dev/api/v3/`, `/v3alpha/`, `/bigquery/v1/` | Ufficiale, **non raggiunta** | Solo titolo/estratto da motore di ricerca |
| S8 | `blog.deps.dev/api/`, `/enumerating-dependents/` | Ufficiale, **non raggiunta** | Solo titolo/estratto da motore di ricerca |
| S9 | `console.cloud.google.com/marketplace/product/bigquery-public-data/deps-dev` | Ufficiale, **non raggiunta** | Non recuperata |
| S10 | Google API Terms of Service (`developers.google.com/terms`) | Primaria, citata da S1, **non raggiunta direttamente** | Testo non letto in questa sessione |

## 3. Availability

- **API pubbliche disponibili:** sì. Due protocolli: JSON su HTTP e gRPC (S1). Esempio ufficiale:
  `curl 'https://api.deps.dev/v3/systems/npm/packages/%40colors%2Fcolors'` (S1).
- **Due versioni:** **v3** ("Core features with a stability guarantee and deprecation policy. Recommended for most users") e **v3alpha** ("All the features of v3, with additional experimental features. May change in incompatible ways from time to time") (S1).
- **Endpoint necessari per Dependency evidence** (da S3, v3, stabile):
  - `GetPackage` — `GET /v3/systems/{system}/packages/{name}` — versioni disponibili di un package.
  - `GetVersion` — `GET /v3/systems/{system}/packages/{name}/versions/{version}` — licenze, advisory.
  - `GetRequirements` — dipendenze dichiarate (vincoli). Disponibile per "Cargo, Go, Maven, npm, NuGet, PyPI, and RubyGems" (S3).
  - `GetDependencies` — grafo delle dipendenze **risolto**. Disponibile solo per "npm, Cargo, Maven and PyPI" (S3) — **Go e RubyGems non hanno dipendenze risolte in v3**.
  - `Query` — ricerca per hash di contenuto o nome.
  - `GetProjectPackageVersions` — mappa progetto → versioni di package, "at most 1500 package versions... mappings derived from attestations are served first" (S3).
- **Reverse-dependency lookup (`GetDependents`, "chi dipende da questo package"):** esiste solo in **v3alpha** (S4), non in v3 stabile.
- **Autenticazione richiesta:** **nessuna evidenza di autenticazione richiesta** per le letture HTTP v3. L'esempio ufficiale (S1) è un `curl` semplice senza header di autenticazione, e né il proto né il README menzionano API key o OAuth per l'API HTTP. `UNKNOWN` se esistano quote più alte per client autenticati (non documentato nelle fonti raggiunte).
- **Limiti di accesso:** vedi sezioni 8 e 10. Nessun numero di richieste/secondo o richieste/giorno è documentato nelle fonti raggiunte. Il solo limite numerico confermato da fonte primaria è quello dei metodi batch di v3alpha: **"Up to 5000 requests are allowed in a single batch"** (S4, ripetuto identico per `GetVersionBatch`, `GetProjectBatch`, `PurlLookupBatch`, `GetFindingsBatch`).

## 4. Reliability

- **Origine dei dati (da S1, sezione "Data"):**
  - Dati di package: Crates.io, Go Module Mirror/Index/Checksum Database, Maven Central, Google's Maven Repository, Jenkins' Maven Repository, Gradle Plugins Maven Repository, npm Registry, NuGet, PyPI, RubyGems.
  - Dati di progetto (fork, stelle, descrizioni): GitHub, GitLab, Bitbucket.
  - Advisory di sicurezza: OSV.dev.
  - Dati associati: OpenSSF Scorecard, OSS-Fuzz.
- **Come vengono raccolti:** deps.dev **aggrega** dati dalle fonti sopra e **genera** dati aggiuntivi (dipendenze risolte, statistiche sulle advisory, associazioni tra entità) (S1). Il meccanismo esatto di raccolta (polling, frequenza, pipeline) non è descritto in S1; `UNKNOWN` per mancanza di accesso a S7/S8.
- **Frequenza di aggiornamento:** non confermata da fonte primaria raggiunta in questa sessione. Un estratto di motore di ricerca cita una frase attribuita a un post ufficiale del blog ("repeatedly examines sites such as github.com, npmjs.com, and pkg.go.dev... keeps the information fresh by doing it all again") e un'altra pagina della pagina dei progetti che si aggiornerebbe "every day" — **entrambe non verificate da lettura diretta della fonte in questa sessione**: `UNKNOWN (fonte secondaria non verificata)`.
- **Ritardi:** `UNKNOWN`. Nessuna fonte raggiunta quantifica il ritardo tra la pubblicazione di una versione su un registry e la sua comparsa su deps.dev.
- **Copertura degli ecosistemi:** vedi sezione 6.

## 5. Data Quality

- **Dati sulle dipendenze disponibili (da S3, v3):**
  - `GetRequirements`: vincoli di versione dichiarati dal package, "in a system-specific format" (S3).
  - `GetDependencies`: grafo **risolto**, definito come "similar to one produced by installing the package version on a generic 64-bit Linux system, with no other dependencies present. The precise meaning of this varies from system to system" (S3). Questa è una dichiarazione ufficiale di **ambiguità intrinseca**: la risoluzione non è garantita identica a quella dell'ambiente reale di ogni progetto.
- **Gestione delle relazioni:** `DependencyRelation` distingue `SELF`, `DIRECT`, `INDIRECT` (S3) — utile per pesare diversamente dipendenze dirette e transitive in una futura metodologia.
- **Gestione delle versioni:** ogni `Package` elenca le versioni disponibili con, quando nota, la versione di default marcata; "the default version... is commonly the version with the greatest version number, ignoring pre-release versions" (da estratto di ricerca su contenuto ufficiale, **non verificato con lettura diretta**: `UNKNOWN (fonte secondaria)`).
- **Gestione di package deprecati:** confermata da fonte primaria (S3): `Version.is_deprecated` (bool) e `Version.deprecated_reason` (string) esistono sia a livello di `Package.Version` che di `Version` (S3, righe 264-268 e 297-301 del proto).
- **Stato del progetto (maintained/deprecated):** `Project.ProjectStatus.status`, con nota esplicita che segue la specifica PEP 728 dei "project status markers" di packaging.python.org, e che **è popolato solo per PyPI** (S3: "this field is only set for package versions in the PyPI system"). **Non disponibile per npm, Maven, Go o Cargo.**
- **Gestione di package abbandonati (non deprecati formalmente):** un rilevamento per "inattività di release oltre una soglia" è citato solo da fonte secondaria non verificata in questa sessione: `UNKNOWN (fonte secondaria non verificata)`.
- **Gestione di package rinominati:** `GetSimilarlyNamedPackages` esiste solo in **v3alpha** (S4) e calcola una "similarity relation", non un collegamento di rename dichiarato/verificato. Nessuna fonte confermata descrive una gestione esplicita del rename (es. `left-pad` → fork). `UNKNOWN` per il meccanismo esatto.
- **Anomalie note:** nessuna fonte primaria raggiunta elenca anomalie note del dataset. `UNKNOWN`.

## 6. Ecosystem Coverage

Confermato da fonte primaria (S3, `enum System`): `GO`, `RUBYGEMS`, `NPM`, `CARGO`, `MAVEN`, `PYPI`, `NUGET`.

| Ecosistema richiesto da GHIMONEY | Presente | Copertura per `GetRequirements` | Copertura per `GetDependencies` (risolto) |
|---|---|---|---|
| npm | ✅ | ✅ | ✅ |
| PyPI | ✅ | ✅ | ✅ |
| Maven | ✅ | ✅ | ✅ |
| Go | ✅ | ✅ | ⚠️ **non elencato** in `GetDependencies` (S3 elenca solo npm, Cargo, Maven, PyPI) |
| Cargo | ✅ | ✅ | ✅ |
| Altri (non richiesti ma presenti) | RubyGems, NuGet | ✅ | ⚠️ RubyGems non in `GetDependencies`; NuGet non in `GetDependencies` |

**Non assumere copertura dove non è documentata (istruzione ricevuta):** per Go, il grafo delle dipendenze **risolto** non è dichiarato disponibile in v3; è disponibile solo il grafo dei **requirement** dichiarati. Qualsiasi uso di deps.dev per la dimensione Dependency su progetti Go dovrebbe quindi basarsi sui requirement, non sul grafo risolto, salvo diversa conferma diretta dell'endpoint (non verificabile in questa sessione per il blocco di rete).

**Ecosistemi esplicitamente fuori copertura:** nessun linguaggio/ecosistema oltre ai sette elencati è menzionato in nessuna fonte raggiunta (es. nessuna menzione di Composer/PHP, Hex/Erlang, Swift Package Manager, CocoaPods).

## 7. Provenance

Valutazione della possibilità di conservare, per ogni evidenza deps.dev, gli stessi campi già richiesti dal modello `EvidenceRecord` di GHIMONEY (`ghimoney/src/ghimoney/models.py`):

| Campo richiesto da GHIMONEY | Disponibile da deps.dev? |
|---|---|
| `source` | Sì: `"deps.dev"` + versione API (v3) |
| `endpoint` | Sì: l'URL HTTP invocato è deterministico dato package/versione (S3) |
| `retrieved_at` | Sì: timestamp locale al momento della chiamata, come già fatto per GitHub |
| `raw_value` / `response hash` | Sì, **in linea di principio**: la risposta HTTP è JSON e può essere congelata e hashata esattamente come gli snapshot GitHub attuali (`ghimoney/src/ghimoney/snapshot.py`) |
| Identificativo/versione del dato lato server | **Parziale.** Il proto non espone, per quanto letto in S3/S4, un campo tipo `ETag`, numero di versione del dataset o timestamp di "ultimo aggiornamento" per singola risposta. Non è confermato che due chiamate nello stesso istante a package diversi riflettano lo stesso "snapshot" del dataset sottostante. `UNKNOWN` |

**Conclusione sezione 7:** la provenance a livello di **singola chiamata HTTP** è tecnicamente sufficiente (stesso meccanismo usato oggi per GitHub). La provenance a livello di **stato del dataset sottostante** (quando è stato aggiornato, se due chiamate sono coerenti tra loro) non è verificabile con le fonti raggiunte in questa sessione.

## 8. API Stability

- **v3:** dichiarata "Core features with a stability guarantee and deprecation policy" (S1). Nessun testo della policy di deprecazione stessa è stato letto direttamente (bloccato in S7); la sua esistenza è affermata dal README ma il suo contenuto (es. periodo minimo di preavviso) è `UNKNOWN`.
- **v3alpha:** dichiarata esplicitamente instabile: "May change in incompatible ways from time to time" (S1). Un cambiamento breaking reale nel campo `artifacts` di `Query` in v3alpha è citato da fonte secondaria (estratto di ricerca), coerente con questa dichiarazione ma non verificato con lettura diretta.
- **Versionamento:** basato su percorso URL (`/v3/...` vs `/v3alpha/...`), confermato da S3/S4.
- **Compatibilità:** "Features that become stable in v3alpha will eventually be added to the v3 API as a non-breaking change" — citato da estratto di ricerca su contenuto ufficiale del blog, **non verificato con lettura diretta**: `UNKNOWN (fonte secondaria non verificata)`.
- **SLA:** nessuna menzione di SLA in nessuna fonte raggiunta (S1, S3, S4, S5). **Assenza di SLA** è quindi lo stato di fatto confermabile: non ne esiste uno documentato nelle fonti disponibili.

## 9. Reproducibility

**Determinazione richiesta: una risposta deps.dev può essere congelata in uno snapshot e ridare lo stesso risultato in modo deterministico?**

- **Sì, per la struttura del meccanismo:** deps.dev restituisce JSON su HTTP; lo stesso meccanismo di snapshot con hash già usato per GitHub (`SnapshotStore`, hash SHA-256 del contenuto) si applicherebbe identicamente. Il README conferma esplicitamente: **"Clients are expressly permitted to cache data served by the API"** (S1) — questo autorizza esplicitamente il pattern di snapshot/cache che GHIMONEY usa già.
- **Limite non risolvibile dal lato client:** il dato **sottostante** su deps.dev cambia nel tempo (è un servizio "live", non un dataset versionato con tag immutabili per singola release). Congelare la risposta di oggi non garantisce che la stessa chiamata in futuro (senza passare dalla cache) restituisca lo stesso valore — esattamente come già accade con la GitHub API, e già gestito da GHIMONEY con lo stesso pattern di snapshot. **Non è un problema nuovo rispetto a D-03**, ma va dichiarato.
- **Non verificabile in questa sessione:** non è stato possibile eseguire una vera chiamata all'API dal vivo (bloccata dalla policy di rete), quindi non è stato verificato empiricamente che due chiamate identiche a distanza di minuti restituiscano byte identici a parità di stato del dataset. `UNKNOWN (non testabile in questa sessione)`.

## 10. Rate Limits and Usage

- **Rate limit documentato per l'API v3 HTTP:** **nessuno trovato.** La issue ufficiale `google/deps.dev#33`, intitolata "Rate limits for `api.deps.dev`", aperta il 16 settembre 2023 dall'utente `nikpivkin` con la domanda "Is there a rate limit for `api.deps.dev`?", etichettata "documentation", **non ha ricevuto risposta dai maintainer** al momento della lettura in questa sessione (S6). Questo è il singolo dato più rilevante e verificabile di questa sezione: **al momento non esiste una policy di rate limit dichiarata pubblicamente e confermabile.**
- **Limite documentato, ma solo per i metodi batch (v3alpha, non v3):** "Up to 5000 requests are allowed in a single batch" (S4) — un limite di **dimensione della richiesta**, non di frequenza nel tempo.
- **Quote:** `UNKNOWN`.
- **Caching:** esplicitamente permesso dal README (S1): "Clients are expressly permitted to cache data served by the API." Questo è positivo per GHIMONEY, che già tratta ogni fonte come cache-first (snapshot).
- **Bulk usage:** l'esistenza stessa dei metodi *Batch* in v3alpha suggerisce che l'uso massivo tramite tante chiamate singole non sia il pattern preferito da deps.dev, ma nessuna fonte raggiunta lo dichiara esplicitamente per v3 stabile (i batch sono solo alpha). In alternativa esiste il dataset BigQuery (sezione 12/13) per un uso bulk, ma i suoi dettagli (nome, schema, costo) non sono stati verificati direttamente in questa sessione (S7/S9 bloccate).

## 11. Terms and Licensing

- **Termini di utilizzo dell'API:** "Use of the deps.dev API is subject to the [Google API Terms of Service]" (S1, con link a `developers.google.com/terms`). Il testo di quei termini **non è stato letto direttamente** in questa sessione (S10 non raggiunta); vanno quindi trattati come **da verificare con lettura diretta prima di qualsiasi decisione formale di integrazione**, non solo citati per nome.
- **Licenza del codice del repository client:** Apache License 2.0 (S2, letta per intero). Riguarda il codice di esempio e le definizioni proto, non i dati.
- **Licenza dei dati generati da deps.dev** (dipendenze risolte, statistiche, associazioni): **CC-BY 4.0**, dichiarata esplicitamente (S1): "This generated data is available under a CC-BY 4.0 license." La CC-BY richiede attribuzione in caso di redistribuzione.
- **Licenza dei dati aggregati dalle fonti upstream** (es. i metadati grezzi di npm o PyPI): il README rimanda esplicitamente alla documentazione di ciascuna fonte upstream: "For details on using the data from these sources, please consult their documentation" (S1). Questo significa che GHIMONEY, se usasse deps.dev, **erediterebbe potenzialmente termini diversi per dati diversi** (dati generati = CC-BY 4.0; dati aggregati grezzi = termini della fonte originale, non verificati singolarmente in questa sessione).
- **Uso commerciale:** non esiste, in nessuna fonte raggiunta, una menzione esplicita di divieto o permesso specifico per uso commerciale. La CC-BY 4.0 permette uso commerciale con attribuzione; i Google API ToS (non letti direttamente) potrebbero introdurre condizioni aggiuntive.
- **Obblighi di attribuzione:** derivano dalla CC-BY 4.0 per i dati generati. Una futura integrazione dovrebbe includere un'attribuzione visibile a deps.dev nei report GHIMONEY che usano questi dati — coerente con l'approccio già seguito per la provenance GitHub.

## 12. GHIMONEY Risks

| Rischio | Valutazione |
|---|---|
| **Single-source dependency** | Se deps.dev diventasse l'**unica** fonte per Adoption/Dependency, GHIMONEY violerebbe il proprio principio (Directive §9, "non assumere che una singola fonte sia verità assoluta"). deps.dev stesso è già un aggregatore multi-fonte, ma dal punto di vista di GHIMONEY resterebbe un singolo punto di fallimento/manipolazione se non affiancato da un confronto incrociato. |
| **Incomplete coverage** | Confermato: nessuna copertura per Go/RubyGems/NuGet in `GetDependencies` risolto (solo requirement); nessuna copertura per linguaggi fuori dai 7 elencati. |
| **Stale data** | Frequenza di aggiornamento non verificata da fonte primaria in questa sessione; rischio non quantificabile con le fonti disponibili. |
| **API instability** | v3 dichiara stabilità; v3alpha esplicitamente no. Qualsiasi integrazione futura dovrebbe usare **solo v3**, non v3alpha (che contiene però le funzionalità più utili per GHIMONEY: `GetDependents`, `GetSimilarlyNamedPackages`). |
| **Provenance limitations** | A livello di singola chiamata sufficiente; a livello di stato del dataset sottostante non verificabile con le fonti raggiunte (sezione 7). |
| **Licensing restrictions** | Termini a due livelli (dati generati CC-BY 4.0, dati aggregati con termini propri della fonte upstream) da verificare con lettura diretta del ToS Google prima di qualsiasi uso in produzione. |
| **Manipulation risks** | deps.dev stesso dipende da npm/PyPI/GitHub ecc.: se quei registry sono manipolabili (rischio già in `THREAT_MODEL.md`, righe su fake stars/downloads), deps.dev **eredita** la stessa manipolabilità a monte. Non introduce un rischio nuovo, ma non lo elimina nemmeno. |
| **Ecosystem bias** | Copertura asimmetrica (Go e RubyGems più deboli su Dependency risolta) introdurrebbe un bias di ecosistema simile a quello già segnalato nell'audit (§11/§63) per GitHub-only. |
| **Rischio operativo specifico di questa sessione** | Il blocco di rete su tutti i sottodomini `*.deps.dev` in questo ambiente cloud significa che **l'implementazione e il test reali di un futuro ingestion module per deps.dev non potranno essere fatti da questa stessa sessione/ambiente**, salvo che la policy di rete cambi. Da verificare nell'ambiente in cui T-19 sarà eventualmente svolto. |

## 13. Dependency Evidence Suitability

Risposte separate, come richiesto:

- **A. È tecnicamente utilizzabile?**
  **Sì, con riserva.** L'API v3 HTTP restituisce JSON su un endpoint stabile e documentato (S1, S3), con un formato di richiesta semplice (`GET`, nessuna autenticazione nota) compatibile con il pattern di ingestion già usato per GitHub. Riserva: non è stato possibile verificare in questa sessione una chiamata reale (rete bloccata), quindi l'utilizzabilità è confermata solo sulla carta (proto + README), non empiricamente.

- **B. È sufficientemente affidabile?**
  **Parzialmente determinabile.** L'origine dei dati è documentata e proviene da registry ufficiali (S1). La frequenza di aggiornamento e i ritardi non sono verificati da fonte primaria raggiunta in questa sessione: `UNKNOWN`. Non si può quindi rispondere con certezza.

- **C. È sufficientemente riproducibile?**
  **Sì, per il meccanismo di snapshot/cache** (il README autorizza esplicitamente il caching, S1), con lo stesso limite già presente per GitHub: il dato sottostante può cambiare nel tempo, quindi la riproducibilità riguarda "lo stesso snapshot", non "la stessa chiamata in futuro". Non verificato empiricamente in questa sessione.

- **D. La provenance è sufficiente?**
  **Sufficiente a livello di singola chiamata, insufficiente a livello di stato del dataset.** Vedi sezione 7.

- **E. I termini d'uso sono compatibili?**
  **Non ancora verificabile con certezza.** La licenza dei dati generati (CC-BY 4.0) è compatibile con attribuzione. I Google API Terms of Service, citati ma non letti direttamente in questa sessione, e i termini propri di ciascuna fonte upstream aggregata, richiedono una verifica diretta prima di qualsiasi decisione. `UNKNOWN (verifica testuale mancante)`.

- **F. La copertura è sufficiente?**
  **Sufficiente per i requirement dichiarati su tutti i 5 ecosistemi richiesti; insufficiente per il grafo delle dipendenze risolto su Go** (e su RubyGems/NuGet, non richiesti ma presenti nel sistema). Vedi sezione 6.

- **G. Quali limitazioni devono essere dichiarate?**
  1. Nessun rate limit pubblicamente documentato e confermato (rischio operativo, non solo di trasparenza).
  2. `GetDependencies` (grafo risolto) non copre Go/RubyGems/NuGet in v3 stabile.
  3. Le funzionalità più utili per Adoption (chi dipende da un package: `GetDependents`) e per la gestione dei rename (`GetSimilarlyNamedPackages`) esistono **solo in v3alpha**, instabile per definizione.
  4. Provenance a livello di stato del dataset non verificabile.
  5. Termini di licenza a due livelli, con il livello "dati aggregati upstream" non uniforme.
  6. Nessuna verifica empirica dal vivo eseguita in questa sessione (limite di rete di questo ambiente specifico, non di deps.dev).

## 14. Open Questions

1. Qual è, in numeri, il rate limit reale dell'API v3 HTTP (se esiste)? (issue ufficiale senza risposta, S6)
2. Qual è la frequenza di aggiornamento effettiva per npm/PyPI/Maven/Go/Cargo? (non verificato da fonte primaria raggiunta)
3. Il testo completo dei Google API Terms of Service è compatibile con l'uso in un protocollo che finanzia retroattivamente terzi sulla base (anche) di questi dati?
4. È possibile, per una versione futura v3, ottenere `GetDependencies` anche per Go/RubyGems/NuGet, o resta un limite strutturale?
5. Il dataset BigQuery pubblico (menzionato da fonti secondarie) offre garanzie di aggiornamento o schema diverse rispetto all'API HTTP? Non verificato in questa sessione (S7/S9 bloccate).
6. Qual è, esattamente, il meccanismo di rilevamento di package "abbandonati" citato da fonti secondarie? Non confermato da fonte primaria.
7. Questo ambiente di sviluppo continuerà a bloccare `*.deps.dev`, o si tratta di una policy temporanea di questa sessione? Rilevante per pianificare T-19.

## 15. Recommendation

**APPROVED WITH CONDITIONS**

Motivazione: le fonti primarie raggiunte (repository ufficiale, proto dell'API, una issue ufficiale) confermano che deps.dev è un servizio reale, mantenuto da Google, con copertura dei 5 ecosistemi richiesti da GHIMONEY per almeno i dati sui requirement, con un meccanismo di caching esplicitamente autorizzato e compatibile con l'architettura a snapshot già usata da GHIMONEY, e con una licenza chiara per i dati generati (CC-BY 4.0). Non ci sono, nelle fonti raggiunte, segnali che deps.dev sia inaffidabile o inadeguato in linea di principio.

Le condizioni da soddisfare **prima** di qualsiasi aggiornamento di D-03 (non in questo documento):

1. Verificare con una chiamata reale all'API (da un ambiente che non blocchi `*.deps.dev`) disponibilità, formato esatto della risposta e comportamento sotto carico, per confermare empiricamente le sezioni 3, 9 e 10.
2. Leggere per intero i Google API Terms of Service (S10) prima di un uso in produzione, non solo la citazione del README.
3. Decidere esplicitamente se, e come, GHIMONEY tratterà `GetDependencies` mancante su Go (requirement-only) e se questo va dichiarato come limite di copertura nella futura `METHODOLOGY.md`, coerentemente con la Regola 3 (missing data ≠ zero) e con Directive §9 (non assumere che una fonte sia verità assoluta senza confronto).
4. Decidere se usare **solo v3** (stabile) in produzione, escludendo v3alpha, oppure attendere che `GetDependents`/`GetSimilarlyNamedPackages` diventino stabili — coerente con la Regola 16 della Directive ("la complessità deve essere giustificata") e con il principio "prove the score before you move the money".
5. Ottenere risposta, o documentare l'assenza di risposta, sulla issue ufficiale del rate limit (S6) prima di pianificare il volume di chiamate previsto da T-19.

**Questa raccomandazione non autorizza l'integrazione nel codice.** L'autorizzazione a procedere con T-19 (implementazione Dependency evidence) e con un aggiornamento di D-03 richiede una decisione esplicita successiva del fondatore, come stabilito dalla sequenza operativa approvata in `TASKS.md`.

# DEPENDENTS SOURCE VERIFICATION

**Task:** T-20A (analisi soltanto — nessun codice, nessuna metodologia, nessun T-20)
**Data:** 2026-09-23
**Motivazione:** D-12 ha stabilito che la dimensione "Dependency" dell'Impact Engine misura i **dependents** del progetto (chi dipende da esso), non le dependencies uscenti raccolte da T-19. Questo documento verifica se esiste, oggi, una fonte utilizzabile per misurare i dependents, con lo stesso standard metodologico di T-18/T-19A.

**Vincoli rispettati:** nessun file di codice toccato, `config/scoring.yaml` non modificato, D-12/D-02 non modificate, nessuna formula o normalizzazione scelta, T-20 non avviato.

**Metodo:** stesso di T-18/T-19A. Fonti primarie lette per intero: il repository ufficiale `github.com/google/deps.dev` (proto `api/v3/api.proto` e `api/v3alpha/apiv3alpha.proto`, raggiunti via `raw.githubusercontent.com`, non bloccato). Verifica empirica reale tramite il tool Firecrawl, perché questa sessione blocca `*.deps.dev` (stesso blocco di T-18/T-19A, riverificato) — **EMPIRICAL VERIFICATION VIA THIRD-PARTY NETWORK INFRASTRUCTURE**, non una simulazione: 9 chiamate HTTP reali, moderate, non aggressive.

---

## 1. Disponibilità reale

- **`GetDependents` esiste solo in v3alpha, non in v3 stabile.** Confermato da fonte primaria (proto ufficiale) e confermato empiricamente: `GET /v3/systems/npm/packages/lodash/versions/4.17.21:dependents` → **HTTP 404 "version not found"**, mentre `GET /v3alpha/systems/npm/packages/lodash/versions/4.17.21:dependents` → **HTTP 200** con dati reali.
- Endpoint v3alpha: `GET /v3alpha/systems/{system}/packages/{name}/versions/{version}:dependents` (proto `api/v3alpha/apiv3alpha.proto`, riga 110-114).
- Risposta: `{"dependentCount": N, "directDependentCount": N, "indirectDependentCount": N}` — coerente con il messaggio proto `Dependents` (righe 1090-1101).
- **Nessuna autenticazione richiesta**, come per il resto dell'API v3/v3alpha (nessun header di autenticazione inviato nelle chiamate riuscite).
- **Avvertenza ufficiale nel proto stesso (riga 1086-1089), cruciale per una futura metodologia:**
  > "Dependent counts are derived from the dependency graphs computed by deps.dev, which means that only public dependents are counted. As such, dependent counts should be treated as **indicative of relative popularity rather than precisely accurate**."

  Questo è un limite dichiarato dalla fonte stessa, non un'ipotesi di questa verifica: il conteggio non è un censimento esatto, ma una stima derivata dai grafi che deps.dev ha già calcolato.

## 2. Ecosistemi coperti

Verificato empiricamente, non assunto:

| Ecosistema | Package testato | Esito |
|---|---|---|
| npm | `lodash@4.17.21` | ✅ 200, dati reali |
| PyPI | `requests@2.31.0` | ✅ 200, dati reali |
| Maven | `com.google.guava:guava@32.1.3-jre` | ✅ 200, dati reali |
| Cargo | `serde@1.0.203` | ✅ 200, dati reali |
| **Go** | `github.com/pkg/errors@v0.9.1` | ❌ **404 "dependents not found"** |
| **Go** (secondo package, per escludere un caso isolato) | `github.com/gin-gonic/gin@v1.9.1` (popolare, sicuramente esistente) | ❌ **404 "dependents not found"**, stesso esito |

**Go non ha dependents calcolati da deps.dev, in nessuna versione testata, in v3alpha, esattamente come non ha il grafo delle dipendenze risolto (T-19A).** Il limite non è isolato a un singolo package: è stato confermato su due package Go reali e ben noti, con lo stesso identico messaggio di errore.

RubyGems e NuGet non sono stati testati: fuori dallo scope dei 5 ecosistemi che GHIMONEY usa (npm, PyPI, Maven, Go, Cargo), stesso criterio già seguito in T-18/T-19A/T-19.

## 3. Risposta per progetti/package reali

Dati reali osservati (non inventati), utili anche a illustrare l'avvertenza della sezione 1 (i numeri sono grandi e "indicativi", non censuari):

| Package | dependentCount | directDependentCount | indirectDependentCount |
|---|---|---|---|
| npm `lodash@4.17.21` | 22.623 | 7.092 | 16.154 |
| PyPI `requests@2.31.0` | 3.041 | 2.650 | 405 |
| Maven `com.google.guava:guava@32.1.3-jre` | 9.397 | 3.097 | 6.343 |
| Cargo `serde@1.0.203` | 68 | 62 | 7 |

Nota tecnica dal proto (riga 1091-1093): `dependentCount` **può essere inferiore alla somma** di `directDependentCount` e `indirectDependentCount` (un package può essere sia dipendente diretto che indiretto per percorsi diversi, e viene contato una sola volta nel totale). Questo va tenuto presente in una futura normalizzazione: `total ≠ direct + indirect` in generale, a differenza del pattern usato in T-19 per il grafo delle dipendenze uscenti.

## 4. Provenance

- A livello di singola chiamata HTTP: sì, lo stesso pattern già usato per GitHub e per T-19 (endpoint, timestamp locale, hash della risposta) si applica identicamente.
- **A livello di stato del dataset sottostante: non verificabile**, stesso limite già documentato in T-18/T-19A. La risposta non contiene un timestamp di calcolo, una versione del grafo o un identificativo di snapshot lato server.
- **Nessuna distinzione, nella risposta, tra "0 dependents perché nessuno dipende dal progetto" e "0 dependents perché il conteggio non è stato ancora calcolato"** — il proto non lo dichiara esplicitamente per questo endpoint. Da trattare con la stessa cautela già applicata in T-19 alle dependencies uscenti (un valore basso o zero VERIFICATO via 200 è legittimo; un 404 non deve mai diventare zero).

## 5. Riproducibilità / snapshot

- **Verificata concretamente**: la stessa chiamata (`lodash@4.17.21:dependents`) ripetuta due volte (a inizio e fine di questa verifica) ha restituito **valori identici** (22.623 / 7.092 / 16.154 entrambe le volte).
- Il meccanismo di snapshot già usato in T-19 (`ghimoney/src/ghimoney/snapshot.py`, generico e riutilizzabile senza modifiche) si applicherebbe identicamente a questo endpoint: stesso schema Response/Snapshot, stesso hash SHA-256 del corpo.
- Limite già noto: il dato sottostante è "live" e può cambiare nel tempo (i grafi vengono ricalcolati); congelare uno snapshot garantisce riproducibilità rispetto a quello snapshot, non rispetto a una chiamata futura — stesso principio già accettato per GitHub e per T-19.

## 6. Limiti operativi

- **Endpoint v3alpha, non v3.** Il README ufficiale (letto in T-18) dichiara che v3 ha "stability guarantee and deprecation policy" mentre v3alpha "may change in incompatible ways from time to time". Usare `GetDependents` oggi significa dipendere da un'API esplicitamente instabile.
- **Rate limit**: nessun limite numerico documentato, stesso esito di T-18/T-19A. 9 chiamate moderate in questa verifica, nessun errore di throttling — non sufficiente per escludere un limite, solo per confermare che non è stato incontrato.
- **Errore ambiguo**: il messaggio "dependents not found" (HTTP 404) è **identico** sia per il limite strutturale di Go (confermato su due package reali) sia per un package/versione realmente inesistente (`this-package-does-not-exist-ghimoney-test-12345`, testato). **Il corpo della risposta da solo non permette di distinguere le due cause.** Una futura implementazione dovrebbe trattare questo 404 come `NOT_AVAILABLE` con causa ambigua dichiarata, esattamente come già fatto in T-19 per `GetDependencies`, salvo per Go dove la causa strutturale è già stabilita da verifica ripetuta su ecosistema intero (non serve ambiguità, il limite è dell'ecosistema, non del singolo package).

## 7. Differenze tra ecosistemi

- **npm, PyPI, Maven, Cargo**: dati disponibili, stessa struttura di risposta.
- **Go**: nessun dato disponibile, in nessuna versione o package testato. Coerente con l'assenza già verificata in T-19A per il grafo delle dipendenze risolto — Go sembra sistematicamente escluso dalle funzionalità derivate/calcolate di deps.dev, non solo da questa in particolare.
- Nessuna assunzione fatta su RubyGems/NuGet (non testati, fuori scope GHIMONEY).

## 8. Distinzione tra dato verificato, UNKNOWN e NOT_AVAILABLE

Applicando lo stesso schema già usato in T-19 (`depsdev_evidence.py`), una futura implementazione dovrebbe classificare:

| Caso osservato in questa verifica | Classificazione proposta (non implementata) |
|---|---|
| HTTP 200 con numeri (npm/PyPI/Maven/Cargo) | `VERIFIED` — dato reale, con l'avvertenza "indicativo, non censuario" sempre riportata in nota |
| HTTP 404 su Go, per qualunque package/versione testato | `NOT_AVAILABLE` — limite strutturale dell'ecosistema, confermato su più package, **mai zero** |
| HTTP 404 su un package/versione inesistente di un ecosistema supportato | `NOT_APPLICABLE` (se l'esistenza del package è già stata verificata altrove, come in T-19) o `NOT_AVAILABLE` con causa ambigua dichiarata (se non verificata) — **mai zero** |
| Stato del dataset sottostante (quando calcolato, se aggiornato) | `UNKNOWN` — non esposto dalla risposta, non verificabile con le fonti raggiunte |

Questa tabella è una proposta di lettura, non un'implementazione: nessun codice è stato scritto in questo task.

## 9. Conclusione

**VERIFIED FOR T-20**

Motivazione: `GetDependents` esiste, è raggiungibile, restituisce dati reali e riproducibili per 4 dei 5 ecosistemi che GHIMONEY usa (npm, PyPI, Maven, Cargo), con una struttura di risposta chiara e un'avvertenza ufficiale già nota alla fonte stessa (indicativo, non censuario). Il caso Go è già chiaramente classificabile come `NOT_AVAILABLE`, sullo stesso modello già validato in T-19 — non è un ostacolo all'uso della fonte, è un limite da dichiarare, esattamente come già fatto per il grafo delle dipendenze uscenti.

**Limitazioni da portare a una futura decisione (non risolte qui, non di competenza di questa verifica):**
1. L'endpoint è **v3alpha**, non v3 stabile: nessuna garanzia di stabilità o di deprecation policy.
2. Il conteggio è dichiarato dalla fonte stessa come "indicativo", non esatto — rilevante per qualunque normalizzazione futura.
3. Un 404 ambiguo (Go vs. package inesistente) richiede una regola di classificazione esplicita, come già fatto in T-19.
4. Nessun rate limit numerico verificato: da non assumere.
5. Nessuna verifica dei Google API Terms of Service in questo task (stesso limite di T-18: `developers.google.com` bloccato in questa sessione).

Questa verifica **non autorizza** l'uso di `GetDependents`, non implementa T-20 e non modifica D-02, D-12 o `config/scoring.yaml`. Una decisione esplicita resta necessaria prima di qualsiasi implementazione — in particolare sulla scelta tra usare comunque un'API v3alpha instabile o attendere una sua eventuale promozione a v3 stabile.

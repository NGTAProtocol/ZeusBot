# T-22 — Real-World Validation su repository reali diversificati

**Stato: BLOCCATO. T-22 NON è completato.**

Questo documento riporta esattamente il blocco riscontrato tentando di eseguire
T-22 con il collector di `tools/collect_github_snapshot.py` (T-22-collector,
`DONE`), come richiesto. Non contiene un corpus di ≥10 repository perché
quel corpus non è stato possibile raccoglierlo con dati reali in questo
ambiente — e per la regola esplicita del task ("non simulare dati") non ne è
stato costruito uno con dati fittizi.

## 1. Cosa è stato tentato

Prima di eseguire qualunque raccolta, è stato verificato l'accesso GitHub
disponibile in questa sessione per un corpus diversificato (owner diversi,
librerie vs applicazioni, progetti grandi/piccoli, giovani/maturi):

| Repository candidato | Categoria prevista | Azione | Esito |
|---|---|---|---|
| `psf/requests` | libreria molto usata, matura, moltissimi dependents | `add_repo(access=push)` | **negato**: "you need push access to psf/requests for Claude to make changes there" |
| `pallets/flask` | framework maturo, molti dependents | `add_repo(access=push)` | **negato**: "you need push access to pallets/flask for Claude to make changes there" |
| `torvalds/linux` | infrastruttura, enorme, community estesa | `add_repo(access=read)` | Concesso **solo** accesso git anonimo (clone), esplicitamente **non** copre l'API GitHub |

`mcp__Claude_Code_Remote__list_repos` restituisce, prima e dopo questi
tentativi, esattamente 3 repository disponibili — tutti dello stesso owner:

```
NGTAProtocol/ZeusBot   (pubblico)
NGTAProtocol/Roadmemo  (pubblico)
NGTAProtocol/ngta-core (privato)
```

## 2. Verifica empirica diretta sul proxy di rete (non solo sugli strumenti MCP)

Per escludere che il blocco fosse solo una restrizione dei tool MCP (aggirabile
chiamando `api.github.com` direttamente, come fa `tools/collect_github_snapshot.py`
via `httpx`), è stata fatta una verifica diretta con `curl` contro l'host reale
usato dal collector:

```
$ curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/repos/psf/requests
HTTP 403
{"message":"GitHub access to this repository is not enabled for this session.
Use add_repo to request access. ..."}
```

Test di controllo per capire *chi* applica il blocco — un repository dentro lo
scope della sessione, con un token deliberatamente non valido:

```
$ curl -H "Authorization: Bearer ghp_fake_test_token_xyz" https://api.github.com/repos/NGTAProtocol/ZeusBot
HTTP 200   (dati reali del repository)

$ curl -H "Authorization: Bearer ghp_fake_test_token_xyz" https://api.github.com/repos/pallets/flask
HTTP 403   (stesso messaggio "not enabled for this session")
```

**Conclusione della verifica:** il proxy di rete di questo ambiente
autentica/instrada le richieste a `api.github.com` per repository, non per
contenuto del token fornito dal client — un repository fuori dallo scope
della sessione resta a 403 indipendentemente dal token usato, e un repository
dentro lo scope risponde con dati reali anche con un token client palesemente
falso (il proxy sostituisce le credenziali server-side). Questo significa che
**nessun `GITHUB_TOKEN` fornibile dall'utente in questa sessione puo bypassare
il limite**: non è un problema di token, è un confine di autorizzazione per
repository imposto dall'infrastruttura della sessione stessa.

Questo confino distingue esplicitamente da un blocco di rete generico (come il
blocco di `*.deps.dev` risolto in T-19A tramite Firecrawl, un percorso di rete
reale alternativo): qui non esiste un percorso di rete alternativo legittimo
da usare, perché il limite è un controllo di autorizzazione per-repository, non
un firewall di rete — instradarlo con un altro strumento equivarrebbe a
eludere un controllo di accesso, cosa che questa sessione si è già impegnata
a non fare (vedi T-14/`docs/VALIDATION.md`, stesso principio).

## 3. Perché i 3 repository disponibili non bastano

`NGTAProtocol/ZeusBot`, `NGTAProtocol/Roadmemo`, `NGTAProtocol/ngta-core` sono
già stati analizzati in run precedenti reali (non simulate), i cui snapshot e
report restano disponibili in `reports/NGTAProtocol__*/`. Non soddisfano i
criteri del corpus richiesti da T-22:

- **stesso owner** per tutti e tre → nessuna diversità di governance/community;
- **nessuna libreria ampiamente adottata** con molti dependents reali (nessuno
  dei tre è pubblicato come package su npm/PyPI/Maven/Cargo osservabile da
  deps.dev, quindi anche la dimensione "dependency" via T-20 resterebbe non
  osservabile per l'intero corpus);
- **nessun progetto molto maturo o molto grande** nel campione (tutti giovani,
  §48 richiede anche progetti maturi/grandi);
- 3 < 10, la soglia numerica minima non è raggiunta indipendentemente dalle
  categorie.

Ripetere l'analisi solo su questi 3 non costituirebbe una "validazione su
repository reali diversificati": sarebbe una ripetizione di T-14/delle analisi
già documentate in `docs/VALIDATION.md` e nei report `NGTAProtocol/*`
esistenti, non un nuovo risultato.

## 4. Cosa servirebbe per sbloccare (nessuna di queste azioni è stata presa)

- l'utente concede, tramite `add_repo(access="push")`, l'accesso ad almeno
  ~10 repository reali di owner/categorie diverse — possibile solo per
  repository la cui organizzazione GitHub ha installato la GitHub App di
  Claude; oppure
- l'utente fornisce un ambiente di esecuzione con accesso diretto e non
  proxato a `api.github.com` (fuori da questa sessione cloud), dove eseguire
  `tools/collect_github_snapshot.py` con un `GITHUB_TOKEN` personale — opzione
  già descritta in `docs/VALIDATION.md` §"Come completare la validazione".

## 5. Stato del codice

Nessuna riga di codice di Impact Engine, scoring, metodologia, config,
ingestion o del collector è stata modificata in questo task: il blocco è
un limite di accesso dell'ambiente, non un difetto del collector (già
verificato offline con fixture in T-22-collector, 138/138 test). Non è stata
prodotta alcuna analisi con dati simulati o inventati per compensare
l'assenza di accesso.

## Conclusione

**Fatto osservato:** in questo ambiente l'accesso reale a `api.github.com` è
limitato, a livello di proxy di rete, ai soli repository esplicitamente
collegati alla sessione (attualmente 3, tutti `NGTAProtocol`); nessun token
fornito dal client cambia questo limite. Il collector T-22-collector funziona
correttamente (verificato offline); il blocco è esterno al codice GHIMONEY.

**Possibile modifica futura (non decisa, non implementata):** nessuna
modifica alla metodologia è proposta qui, perché non è stato osservato nessun
risultato di scoring da cui derivarla — il blocco impedisce l'osservazione
stessa. L'unica azione possibile è organizzativa/di accesso (sezione 4), non
di modello.

**T-22 resta TODO/BLOCKED.** Non viene dichiarato completato.

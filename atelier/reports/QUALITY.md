# Report di qualità (generato da scripts/report.mjs)

**Come si misura:**
- Lighthouse 13.5.0 su Chromium headless (WebGL software SwiftShader), una run per profilo, con un server statico locale gzip.
- Mobile = profilo Lighthouse predefinito (Moto G, 4G lento simulato, CPU 4x); desktop = preset desktop.
- Soglie: BASE ≥ 90 mobile e desktop; CINEMATICO ≥ 75 mobile e ≥ 85 desktop; accessibilità e SEO ≥ 95.
- Le baseline sono misurate con le stesse soglie, ma solo per confronto.

## Lighthouse per sito

| Sito | Config | Livello | Perf mob | Perf desk | A11y | SEO | LCP mob | TBT mob | Peso | Soglie |
|---|---|---|---|---|---|---|---|---|---|---|
| fornace-lume | BASELINE | BASE | 100 | 100 | 100 | 100 | 0.75 s | 26 ms | 7 KB | ✅ |
| fornace-lume | BASELINE | CINEMATIC | 71 | 72 | 100 | 100 | 2.48 s | 1164 ms | 182 KB | ❌ |
| fornace-lume | A | BASE | 100 | 100 | 100 | 100 | 1.35 s | 0 ms | 66 KB | ✅ |
| fornace-lume | A | CINEMATIC | 99 | 100 | 100 | 100 | 1.61 s | 71 ms | 113 KB | ✅ |
| fornace-lume | B | BASE | 100 | 100 | 100 | 100 | 1.21 s | 0 ms | 57 KB | ✅ |
| fornace-lume | B | CINEMATIC | 99 | 100 | 100 | 100 | 1.62 s | 72 ms | 104 KB | ✅ |
| fornace-lume | C | BASE | 100 | 100 | 100 | 100 | 1.06 s | 0 ms | 39 KB | ✅ |
| fornace-lume | C | CINEMATIC | 99 | 100 | 100 | 100 | 1.76 s | 70 ms | 86 KB | ✅ |
| quota-2100 | BASELINE | BASE | 100 | 100 | 90 | 100 | 0.76 s | 0 ms | 6 KB | ❌ |
| quota-2100 | BASELINE | CINEMATIC | 67 | 100 | 91 | 100 | 2.76 s | 2020 ms | 182 KB | ❌ |
| quota-2100 | A | BASE | 94 | 100 | 100 | 100 | 1.35 s | 0 ms | 91 KB | ✅ |
| quota-2100 | A | CINEMATIC | 98 | 99 | 100 | 100 | 1.88 s | 109 ms | 138 KB | ✅ |
| quota-2100 | B | BASE | 100 | 100 | 100 | 100 | 1.36 s | 0 ms | 78 KB | ✅ |
| quota-2100 | B | CINEMATIC | 98 | 100 | 100 | 100 | 1.85 s | 127 ms | 125 KB | ✅ |
| quota-2100 | C | BASE | 100 | 100 | 100 | 100 | 1.05 s | 0 ms | 43 KB | ✅ |
| quota-2100 | C | CINEMATIC | 99 | 100 | 100 | 100 | 1.65 s | 73 ms | 90 KB | ✅ |
| nodo-sicuro | BASELINE | BASE | 100 | 100 | 90 | 100 | 0.76 s | 2 ms | 6 KB | ❌ |
| nodo-sicuro | BASELINE | CINEMATIC | 66 | 86 | 91 | 100 | 2.85 s | 2179 ms | 182 KB | ❌ |
| nodo-sicuro | A | BASE | 100 | 100 | 100 | 100 | 1.36 s | 0 ms | 73 KB | ✅ |
| nodo-sicuro | A | CINEMATIC | 99 | 100 | 100 | 100 | 1.76 s | 44 ms | 120 KB | ✅ |
| nodo-sicuro | B | BASE | 100 | 100 | 100 | 100 | 1.21 s | 0 ms | 66 KB | ✅ |
| nodo-sicuro | B | CINEMATIC | 99 | 100 | 100 | 100 | 1.63 s | 68 ms | 113 KB | ✅ |
| nodo-sicuro | C | BASE | 100 | 100 | 100 | 100 | 1.20 s | 54 ms | 46 KB | ✅ |
| nodo-sicuro | C | CINEMATIC | 94 | 100 | 100 | 100 | 1.89 s | 265 ms | 93 KB | ✅ |

### Costo del 3D avviato subito (`?force3d`)

Il 3D parte al primo gesto e gira in un Web Worker. Lighthouse non interagisce e non conta il lavoro del worker. Qui il 3D è forzato al caricamento.

| Sito | Perf mob | TBT mob | Perf desk |
|---|---|---|---|
| fornace-lume-b-cinematic | 99 | 109 ms | 100 |
| fornace-lume-baseline-cinematic | 73 | 1058 ms | 73 |
| nodo-sicuro-baseline-cinematic | 65 | 2445 ms | 72 |
| quota-2100-a-cinematic | 93 | 51 ms | 99 |
| quota-2100-baseline-cinematic | 80 | 673 ms | 88 |

## Controlli automatici (Playwright)

| Sito | Overflow 375 | Errori console | Host esterni | Nascosti dopo scroll | 3D attivo 1280 | Reduced-motion | No-WebGL | Save-Data |
|---|---|---|---|---|---|---|---|---|
| fornace-lume-baseline-base | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | — | — |
| fornace-lume-baseline-cinematic | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | firma/poster no | canvas no |
| fornace-lume-a-base | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | — | — |
| fornace-lume-a-cinematic | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | firma/poster sì | canvas no |
| fornace-lume-b-base | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | — | — |
| fornace-lume-b-cinematic | ✅ | 0 | nessuno | 0/0/0 | sì | nascosti 0, canvas no | firma/poster sì | canvas no |
| fornace-lume-c-base | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | — | — |
| fornace-lume-c-cinematic | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | firma/poster sì | canvas no |
| quota-2100-baseline-base | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | — | — |
| quota-2100-baseline-cinematic | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | firma/poster no | canvas no |
| quota-2100-a-base | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | — | — |
| quota-2100-a-cinematic | ✅ | 0 | nessuno | 0/0/0 | sì | nascosti 0, canvas no | firma/poster sì | canvas no |
| quota-2100-b-base | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | — | — |
| quota-2100-b-cinematic | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | firma/poster sì | canvas no |
| quota-2100-c-base | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | — | — |
| quota-2100-c-cinematic | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | firma/poster sì | canvas no |
| nodo-sicuro-baseline-base | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | — | — |
| nodo-sicuro-baseline-cinematic | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | firma/poster no | canvas no |
| nodo-sicuro-a-base | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | — | — |
| nodo-sicuro-a-cinematic | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | firma/poster sì | canvas no |
| nodo-sicuro-b-base | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | — | — |
| nodo-sicuro-b-cinematic | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | firma/poster sì | canvas no |
| nodo-sicuro-c-base | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | — | — |
| nodo-sicuro-c-cinematic | ✅ | 0 | nessuno | 0/0/0 | no | nascosti 0, canvas no | firma/poster sì | canvas no |

## Rilevatore di slop sull'HTML compilato (`scripts/lib/slop.mjs`)

Conta i segnali della lista nera (§10) e i link finti (§9).

**Limite:** il lint di Atelier fa rispettare proprio queste regole. Lo zero delle configurazioni A/B/C è quindi atteso, non una prova indipendente di qualità.

| Sito | Config | Livello | Totale | Dettaglio (≠0) |
|---|---|---|---|---|
| fornace-lume | baseline | base | 9 | emoji 6, card-con-ombra-ripetute 3 |
| fornace-lume | baseline | cinematic | 9 | emoji 6, card-con-ombra-ripetute 3 |
| fornace-lume | a | base | 0 | — |
| fornace-lume | a | cinematic | 0 | — |
| fornace-lume | b | base | 0 | — |
| fornace-lume | b | cinematic | 0 | — |
| fornace-lume | c | base | 0 | — |
| fornace-lume | c | cinematic | 0 | — |
| quota-2100 | baseline | base | 7 | emoji 4, card-con-ombra-ripetute 3 |
| quota-2100 | baseline | cinematic | 7 | emoji 4, card-con-ombra-ripetute 3 |
| quota-2100 | a | base | 0 | — |
| quota-2100 | a | cinematic | 0 | — |
| quota-2100 | b | base | 0 | — |
| quota-2100 | b | cinematic | 0 | — |
| quota-2100 | c | base | 0 | — |
| quota-2100 | c | cinematic | 0 | — |
| nodo-sicuro | baseline | base | 24 | testo-gradiente 5, gradiente-viola-indaco 14, emoji 4, frasi-vuote 1 |
| nodo-sicuro | baseline | cinematic | 24 | testo-gradiente 5, gradiente-viola-indaco 14, emoji 4, frasi-vuote 1 |
| nodo-sicuro | a | base | 0 | — |
| nodo-sicuro | a | cinematic | 0 | — |
| nodo-sicuro | b | base | 0 | — |
| nodo-sicuro | b | cinematic | 0 | — |
| nodo-sicuro | c | base | 0 | — |
| nodo-sicuro | c | cinematic | 0 | — |

## Confronto per configurazione (medie sui 3 siti)

- **Distanza visiva:** differenza media dei pixel (0-100) tra gli hero a 1280 px dei 3 siti della stessa configurazione, ridotti a 64×40. Più è alta, più i siti sono diversi tra loro (meno "effetto template").
- **Token (stima):** byte scritti a mano per sito (Bibbia + contenuti, oppure il file della baseline) diviso 4. Stima i soli token di output; non sono token misurati dall'API.

| Config | Livello | Perf mob | Perf desk | A11y | SEO | Soglie superate | Slop | Distanza visiva | Build | Token stimati/sito | Rubrica |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BASELINE | BASE | 100.0 | 100.0 | 93.3 | 100.0 | 1/3 | 40 | 54.6 | 1.9 s | ~1868 | **3.9** |
| BASELINE | CINEMATIC | 68.0 | 86.0 | 94.0 | 100.0 | 0/3 | 40 | 52.3 | 2.7 s | ~2391 | **3.9** |
| A | BASE | 98.0 | 100.0 | 100.0 | 100.0 | 3/3 | 0 | 13.6 | 1.9 s | ~3088 | **7.5** |
| A | CINEMATIC | 98.7 | 99.7 | 100.0 | 100.0 | 3/3 | 0 | 19.7 | 3.2 s | ~3088 | **7.6** |
| B | BASE | 100.0 | 100.0 | 100.0 | 100.0 | 3/3 | 0 | 49.8 | 1.9 s | ~2394 | **7.3** |
| B | CINEMATIC | 98.7 | 100.0 | 100.0 | 100.0 | 3/3 | 0 | 50.1 | 3.0 s | ~2394 | **7.4** |
| C | BASE | 100.0 | 100.0 | 100.0 | 100.0 | 3/3 | 0 | 10.6 | 1.9 s | ~2061 | **6.7** |
| C | CINEMATIC | 97.3 | 100.0 | 100.0 | 100.0 | 3/3 | 0 | 10.5 | 2.6 s | ~2061 | **6.8** |

## Rubrica 1-10 (AUTOVALUTAZIONE)

**Autovalutazione.** Punteggi assegnati dallo stesso modello che ha scritto tutti i siti (baseline, A, B, C), guardando screenshot reali a 375/768/1280 e pagine intere. Non è un giudizio di designer o utenti; serve a rendere esplicito il criterio, non a dimostrare qualcosa da solo.

Criteri: Q1 concept, Q2 personalità, Q3 firma, Q4 contenuto vero, Q5 zero slop, Q6 memorabile, gerarchia, contrasto, spazio, movimento, mobile, effetto template (10 = nessuno).

### Iterazione 1 (prima build v2)

| Sito | Config | Livello | Q1 concept | Q2 personalità | Q3 firma | Q4 contenuto vero | Q5 zero slop | Q6 memorabile | gerarchia | contrasto | spazio | movimento | mobile | effetto template (10 = nessuno) | Media |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fornace-lume | BASELINE | base | 2 | 3 | 1 | 5 | 3 | 2 | 6 | 7 | 6 | 5 | 6 | 2 | **4.0** |
| fornace-lume | BASELINE | cinematic | 2 | 3 | 2 | 5 | 3 | 2 | 6 | 7 | 6 | 3 | 6 | 2 | **3.9** |
| quota-2100 | BASELINE | base | 2 | 3 | 1 | 6 | 4 | 2 | 6 | 6 | 6 | 5 | 6 | 2 | **4.1** |
| quota-2100 | BASELINE | cinematic | 2 | 3 | 2 | 6 | 4 | 2 | 6 | 6 | 6 | 3 | 6 | 2 | **4.0** |
| nodo-sicuro | BASELINE | base | 2 | 2 | 1 | 6 | 2 | 2 | 6 | 6 | 6 | 5 | 6 | 1 | **3.8** |
| nodo-sicuro | BASELINE | cinematic | 2 | 2 | 2 | 6 | 2 | 2 | 6 | 6 | 6 | 3 | 6 | 1 | **3.7** |
| fornace-lume | A | base | 8 | 7 | 8 | 8 | 9 | 8 | 8 | 8 | 7 | 7 | 7 | 8 | **7.8** |
| fornace-lume | A | cinematic | 8 | 7 | 8 | 8 | 9 | 8 | 8 | 8 | 7 | 8 | 7 | 8 | **7.8** |
| quota-2100 | A | base | 8 | 8 | 7 | 8 | 9 | 7 | 8 | 8 | 7 | 7 | 7 | 7 | **7.6** |
| quota-2100 | A | cinematic | 8 | 8 | 8 | 8 | 9 | 8 | 8 | 8 | 7 | 8 | 7 | 7 | **7.8** |
| nodo-sicuro | A | base | 7 | 7 | 4 | 8 | 9 | 6 | 7 | 8 | 7 | 7 | 7 | 6 | **6.9** |
| nodo-sicuro | A | cinematic | 7 | 7 | 4 | 8 | 9 | 6 | 7 | 8 | 7 | 4 | 7 | 6 | **6.7** |
| fornace-lume | B | base | 7 | 7 | 5 | 8 | 9 | 6 | 8 | 8 | 7 | 7 | 7 | 7 | **7.2** |
| fornace-lume | B | cinematic | 7 | 7 | 6 | 8 | 9 | 6 | 8 | 8 | 7 | 7 | 7 | 7 | **7.3** |
| quota-2100 | B | base | 7 | 7 | 7 | 8 | 9 | 7 | 8 | 8 | 7 | 7 | 7 | 7 | **7.4** |
| quota-2100 | B | cinematic | 7 | 7 | 7 | 8 | 9 | 7 | 8 | 8 | 7 | 8 | 7 | 7 | **7.5** |
| nodo-sicuro | B | base | 7 | 7 | 4 | 8 | 9 | 6 | 8 | 8 | 7 | 7 | 7 | 6 | **7.0** |
| nodo-sicuro | B | cinematic | 7 | 7 | 4 | 8 | 9 | 6 | 8 | 8 | 7 | 8 | 7 | 6 | **7.1** |
| fornace-lume | C | base | 6 | 5 | 4 | 8 | 9 | 4 | 8 | 8 | 7 | 7 | 8 | 5 | **6.6** |
| fornace-lume | C | cinematic | 6 | 5 | 4 | 8 | 9 | 4 | 8 | 8 | 7 | 8 | 8 | 5 | **6.7** |
| quota-2100 | C | base | 6 | 5 | 5 | 8 | 9 | 4 | 8 | 8 | 7 | 7 | 8 | 5 | **6.7** |
| quota-2100 | C | cinematic | 6 | 5 | 5 | 8 | 9 | 4 | 8 | 8 | 7 | 8 | 8 | 5 | **6.8** |
| nodo-sicuro | C | base | 6 | 5 | 3 | 8 | 9 | 5 | 8 | 8 | 7 | 7 | 8 | 4 | **6.5** |
| nodo-sicuro | C | cinematic | 6 | 5 | 3 | 8 | 9 | 5 | 8 | 8 | 7 | 4 | 8 | 4 | **6.3** |

Punti peggiori trovati:
- **Nodo:** il reticolo era quasi invisibile, e nel CINEMATICO A e C costava 1,2-1,8 s di TBT, sotto soglia.
- **Baseline:** uscivano senza stile per un difetto della pipeline (Tailwind non scansionava `engine/src/generated`). Non sono state valutate in questo stato: il difetto è stato corretto e le baseline rimisurate.

### Iterazione 2 (finale)

| Sito | Config | Livello | Q1 concept | Q2 personalità | Q3 firma | Q4 contenuto vero | Q5 zero slop | Q6 memorabile | gerarchia | contrasto | spazio | movimento | mobile | effetto template (10 = nessuno) | Media |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fornace-lume | BASELINE | base | 2 | 3 | 1 | 5 | 3 | 2 | 6 | 7 | 6 | 5 | 6 | 2 | **4.0** |
| fornace-lume | BASELINE | cinematic | 2 | 3 | 2 | 5 | 3 | 2 | 6 | 7 | 6 | 3 | 6 | 2 | **3.9** |
| quota-2100 | BASELINE | base | 2 | 3 | 1 | 6 | 4 | 2 | 6 | 6 | 6 | 5 | 6 | 2 | **4.1** |
| quota-2100 | BASELINE | cinematic | 2 | 3 | 2 | 6 | 4 | 2 | 6 | 6 | 6 | 3 | 6 | 2 | **4.0** |
| nodo-sicuro | BASELINE | base | 2 | 2 | 1 | 6 | 2 | 2 | 6 | 6 | 6 | 5 | 6 | 1 | **3.8** |
| nodo-sicuro | BASELINE | cinematic | 2 | 2 | 2 | 6 | 2 | 2 | 6 | 6 | 6 | 3 | 6 | 1 | **3.7** |
| fornace-lume | A | base | 8 | 7 | 8 | 8 | 9 | 8 | 8 | 8 | 7 | 7 | 7 | 8 | **7.8** |
| fornace-lume | A | cinematic | 8 | 7 | 8 | 8 | 9 | 8 | 8 | 8 | 7 | 8 | 7 | 8 | **7.8** |
| quota-2100 | A | base | 8 | 8 | 7 | 8 | 9 | 7 | 8 | 8 | 7 | 7 | 7 | 7 | **7.6** |
| quota-2100 | A | cinematic | 8 | 8 | 8 | 8 | 9 | 8 | 8 | 8 | 7 | 8 | 7 | 7 | **7.8** |
| nodo-sicuro | A | base | 7 | 7 | 6 | 8 | 9 | 6 | 7 | 8 | 7 | 7 | 7 | 7 | **7.2** |
| nodo-sicuro | A | cinematic | 7 | 7 | 6 | 8 | 9 | 6 | 7 | 8 | 7 | 8 | 7 | 7 | **7.3** |
| fornace-lume | B | base | 7 | 7 | 5 | 8 | 9 | 6 | 8 | 8 | 7 | 7 | 7 | 7 | **7.2** |
| fornace-lume | B | cinematic | 7 | 7 | 6 | 8 | 9 | 6 | 8 | 8 | 7 | 7 | 7 | 7 | **7.3** |
| quota-2100 | B | base | 7 | 7 | 7 | 8 | 9 | 7 | 8 | 8 | 7 | 7 | 7 | 7 | **7.4** |
| quota-2100 | B | cinematic | 7 | 7 | 7 | 8 | 9 | 7 | 8 | 8 | 7 | 8 | 7 | 7 | **7.5** |
| nodo-sicuro | B | base | 7 | 7 | 6 | 8 | 9 | 6 | 8 | 8 | 7 | 7 | 7 | 7 | **7.3** |
| nodo-sicuro | B | cinematic | 7 | 7 | 6 | 8 | 9 | 6 | 8 | 8 | 7 | 8 | 7 | 7 | **7.3** |
| fornace-lume | C | base | 6 | 5 | 4 | 8 | 9 | 4 | 8 | 8 | 7 | 7 | 8 | 5 | **6.6** |
| fornace-lume | C | cinematic | 6 | 5 | 4 | 8 | 9 | 4 | 8 | 8 | 7 | 8 | 8 | 5 | **6.7** |
| quota-2100 | C | base | 6 | 5 | 5 | 8 | 9 | 4 | 8 | 8 | 7 | 7 | 8 | 5 | **6.7** |
| quota-2100 | C | cinematic | 6 | 5 | 5 | 8 | 9 | 4 | 8 | 8 | 7 | 8 | 8 | 5 | **6.8** |
| nodo-sicuro | C | base | 6 | 5 | 5 | 8 | 9 | 5 | 8 | 8 | 7 | 7 | 8 | 5 | **6.8** |
| nodo-sicuro | C | cinematic | 6 | 5 | 5 | 8 | 9 | 5 | 8 | 8 | 7 | 8 | 8 | 5 | **6.8** |

Correzioni applicate:
- **Reticolo:** più spesso e con meno segmenti, senza misure per segmento. Effetto misurato su Nodo C CINEMATICO: mobile da 68 a 94, TBT da 1.803 a 265 ms.
- **Baseline:** con lo stile Tailwind corretto.

**Non corretti (limite dichiarato):**
- la firma `layers` della configurazione C sembra un paesaggio montano generico ed è uguale su Fornace e Quota;
- la massa 3D di Fornace B ricorda più un frutto che lo smalto;
- con lo scrub, i paragrafi dei capitoli scendono a opacità 0,35 quando si risale la pagina.

La terza iterazione non è stata fatta: correggere la firma C vuol dire disegnarne una nuova, non regolare un parametro.

### Media per criterio (ultima iterazione)

| Config | Livello | Q1 concept | Q2 personalità | Q3 firma | Q4 contenuto vero | Q5 zero slop | Q6 memorabile | gerarchia | contrasto | spazio | movimento | mobile | effetto template (10 = nessuno) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BASELINE | base | 2.0 | 2.7 | 1.0 | 5.7 | 3.0 | 2.0 | 6.0 | 6.3 | 6.0 | 5.0 | 6.0 | 1.7 |
| BASELINE | cinematic | 2.0 | 2.7 | 2.0 | 5.7 | 3.0 | 2.0 | 6.0 | 6.3 | 6.0 | 3.0 | 6.0 | 1.7 |
| A | base | 7.7 | 7.3 | 7.0 | 8.0 | 9.0 | 7.0 | 7.7 | 8.0 | 7.0 | 7.0 | 7.0 | 7.3 |
| A | cinematic | 7.7 | 7.3 | 7.3 | 8.0 | 9.0 | 7.3 | 7.7 | 8.0 | 7.0 | 8.0 | 7.0 | 7.3 |
| B | base | 7.0 | 7.0 | 6.0 | 8.0 | 9.0 | 6.3 | 8.0 | 8.0 | 7.0 | 7.0 | 7.0 | 7.0 |
| B | cinematic | 7.0 | 7.0 | 6.3 | 8.0 | 9.0 | 6.3 | 8.0 | 8.0 | 7.0 | 7.7 | 7.0 | 7.0 |
| C | base | 6.0 | 5.0 | 4.7 | 8.0 | 9.0 | 4.3 | 8.0 | 8.0 | 7.0 | 7.0 | 8.0 | 5.0 |
| C | cinematic | 6.0 | 5.0 | 4.7 | 8.0 | 9.0 | 4.3 | 8.0 | 8.0 | 7.0 | 8.0 | 8.0 | 5.0 |

## Note sulle misure (v2)

- **Run singola per profilo.** Lighthouse è stato eseguito una volta per profilo e per sito, perché 24 siti × 2 profili richiedono già circa 75 minuti. Le stesse pagine ripetute oscillano parecchio. Esempio: quota-2100 baseline CINEMATICO ha dato mobile 80 nell'iterazione 1 e 67 nell'iterazione 2, senza modifiche al codice (la ricompilazione ha cambiato solo la presenza del CSS). Differenze di pochi punti tra configurazioni **non** sono significative.
- **Iterazioni:**
  - iterazione 1: tutti i 24 siti (`reports/qa-v2-iter1/`, log `qa-iter1.log`);
  - iterazione 2: Nodo (reticolo corretto) e le 6 baseline (stile corretto), con log `qa-iter2.log`;
  - `reports/qa/` contiene l'ultima misura di ogni sito.
- **Difetto trovato nella baseline e corretto:** Tailwind 4 non scansiona le cartelle in `.gitignore` e `engine/src/generated/` lo è. Per questo **in v1 tutte le baseline uscivano senza stile** (testo nero su bianco, vedi `reports/shots` della v1). Il confronto della v1 era quindi falsato a favore di Atelier. Ora `baseline.css` dichiara `@source "../generated"` e un test verifica che le classi della baseline abbiano CSS.
- **Reticolo (Nodo):**
  - prima versione: centinaia di `gsap.set` e misure per segmento. TBT mobile 1.241 ms (A) e 1.803 ms (C), sotto soglia;
  - riscritto con le coordinate già nell'SVG e scrittura solo dei segmenti che cambiano: TBT 44 ms (A), 265 ms (C), mobile 99 e 94.
- **3D solo dove è la firma:**
  - Three.js entra nel bundle solo in fornace-lume-b e quota-2100-a CINEMATICO (verificato da `npm test`);
  - con il 3D forzato all'avvio (`?force3d`, Web Worker) misurano mobile 99 e 93;
  - le baseline CINEMATICO, con un 3D in loop infinito nel thread principale, misurano 65-88.
- **LCP:** le baseline usano i font di sistema e hanno LCP più basso (0,75 s contro 1,0-1,9 s), ma il CINEMATICO delle baseline perde punti sul TBT.
- **WebGL software:** tutto il 3D è renderizzato con SwiftShader (CPU). Nessuna GPU reale, nessun dispositivo reale.
- **Rilevatore di slop circolare:** controlla le regole che il lint di Atelier già impone. Non vede, nelle baseline, il modulo senza backend e il riquadro segnaposto di Fornace (li ha notati la rubrica).
- **Distanza visiva, misura grezza:** differenza dei pixel a 64×40, dominata dal colore di fondo. Dice comunque una cosa vera: i siti A e C di clienti diversi si somigliano tra loro (fondi chiari, stesso motore e stesso schema di pagina) più di quanto si somiglino le baseline tra loro.

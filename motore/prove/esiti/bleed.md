# Prova del bleed: esito

Data: 2026-10-13. Ramo motore, partendo da 57f262e.

## Correzione al motore

`impagina.py`: con il bleed, i numeri di pagina venivano centrati sulla pagina allargata (trim + bleed)
invece che sul trim, quindi non seguivano lo spostamento del contenuto. Ora stanno al centro del piede
del trim. Senza bleed i calcoli sono gli stessi di prima.

## Prova (`script/prove.py`, `bleed_pdf`, sezione «passo 3»)

Una copia inventata del romance con `formato.bleed: true`, confrontata con la stessa copia senza
bleed. 5 prove nuove:

| Prova | Atteso |
|---|---|
| formato = trim + bleed di `dati/kdp.yaml` | 5,625 × 8,75″ su tutte le pagine |
| pagine dispari: spostamento di ogni parola (dx, dy) | (0, 0,125″) |
| pagine pari: spostamento di ogni parola (dx, dy) | (0,125″, 0,125″) |
| soglia KDP del margine esterno con bleed | 0,375″ (`dati/kdp.yaml`) |
| margine esterno | 0,75″ ±0,005, mai sotto 0,375″ |

## Prova di regressione

Con `formato_esatto` modificato temporaneamente per ignorare il bleed, falliscono 4 prove su 5:
formato (5,5 × 8,5″), spostamenti delle pagine dispari e pari, margine esterno («0.625: fuori
tolleranza»). Resta OK solo la soglia KDP, che è un dato letto da `dati/kdp.yaml`. Poi il file è
stato ripristinato.

## Suite

**429/429 OK** (424 + 5), 0 saltate, 0 KO, con LanguageTool.

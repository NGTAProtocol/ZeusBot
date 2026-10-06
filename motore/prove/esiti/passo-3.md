# Passo 3 — Stampa: esito

Data: 2026-10-02. Proposta di riferimento: `motore/proposta-motore.md` (approvata), B.7 passo 3.

## Strumenti nel container

| Strumento | Esito |
|---|---|
| Chromium (Playwright) | /opt/pw-browsers/chromium-1194 |
| Playwright per Node | 1.56.1 (globale, /opt/node22/lib/node_modules); Node 22.22.2 |
| Playwright per Python | assente (non serve: il render usa Node) |
| PyMuPDF | 1.28.2 |
| pdftotext, pdffonts, pdfinfo | presenti (/usr/bin) |
| Hunspell | presente, dizionario it_IT |
| fontTools, brotli, markdown (Python) | presenti |

## Font

- EB Garamond, «Version 1.003», SIL Open Font License 1.1, scaricato il 2026-10-02 da https://raw.githubusercontent.com/google/fonts/main/ofl/ebgaramond/ (github.com risponde 403 dal proxy; raw.githubusercontent.com risponde 200).
- Istanze statiche Regular 400, Italic 400 e SemiBold 600, ricavate con fontTools dai file variabili. Sha256 delle origini e dei file in `stampa/font/FONTI.yaml`; licenza in `stampa/font/OFL.txt`.

## File

| File | Righe |
|---|---|
| script/compila.py | 102 |
| script/impagina.py | 176 |
| script/verifica_pdf.py | 199 |
| stampa/modello.css | 35 |
| stampa/print.js | 12 |
| stampa/font/ | FONTI.yaml, OFL.txt, 3 file .ttf |
| script/comune.py | + percorso_in_libro, nome_file, margini KDP |
| dati/libro.schema.yaml | + copyright.anno |
| prove/mini-libro*/libro.yaml | + copyright.anno: 2026 |
| script/prove.py, script/recinto.py, prove/attesi.yaml | + passo 3 |

## Esito

**zb prove: 127/127 OK** (87 dei passi 1-2b + 40 del passo 3). separazione.py OK; recinto.py OK su 26 esecuzioni.

| Mini-libro | Pagine | Margine interno min / soglia KDP | Esterno min | Font | Sommario | Parole per pagina |
|---|---|---|---|---|---|---|
| giallo | 16 (4 + 12) | 0,625" / 0,375" | 0,625" | incorporati, nessun Type3 | coincide | 184,9 |
| romance | 23 (4 + 19) | 0,665" / 0,375" | 0,624" | incorporati, nessun Type3 | coincide | 205,8 |

- Lo sha256 di ciascun PDF è fissato in attesi.yaml: due generazioni consecutive danno lo stesso valore.
- Parole per pagina misurate: 184,9 (giallo) e 205,8 (romance), contro 250 dei profili. I profili non sono stati modificati.
- Romance: 23 pagine, numero dispari, quindi AVVISO (atteso).

## Scelte non scritte nella proposta

1. Il render usa Playwright per Node, perché nel container non c'è Playwright per Python.
2. Font in .ttf statici, non woff2: PyMuPDF, che stampa i numeri di pagina, non legge il woff2.
3. Le pagine iniziali (frontespizio, copyright, sommario) si stampano senza numero e si completano a un numero pari con una pagina bianca, così il capitolo 1 comincia su una pagina dispari.
4. I numeri di pagina partono da 1 sulla prima unità del corpo e li stampa PyMuPDF al centro del piede: in Chromium il piè di pagina via CSS non funziona.
5. Margini a specchio con `@page :right / :left`: interno a sinistra sulle pagine dispari. Le misure sul romance (17 mm interno, 16 mm esterno) confermano che Chromium li applica.
6. Tabella KDP dei margini: dal passo 3b sta solo in dati/kdp.yaml, letta da comune.py. Sotto le 24 pagine vale la prima fascia (0,375").
7. I PDF sono resi deterministici: metadati senza date, nessun nuovo ID, font ridotti ai sottoinsiemi.
8. Nome del PDF: `<libro>/05-output/<titolo>.pdf`, con il titolo in minuscolo e i trattini.
9. Nuovo campo facoltativo `copyright.anno` in libro.yaml (fissato a 2026 nei mini-libri), per avere lo stesso .md anche a cavallo di un cambio d'anno.
10. L'istanza SemiBold conserva il nome interno «Regular»: pdffonts la elenca come EBGaramond-Regular. Non ha effetti sul PDF.

## Non fatto in questo passo

- Il minimo KDP di 24 pagine non si controlla qui: è un controllo di conformità (passo 4, sezione 11). I mini-libri ne hanno 16 e 23.

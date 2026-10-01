# Fase 9 — PDF definitivo — «Il padre del mostro»

- **Punto di partenza:** `199f39c`, verificato. **Punto di ripristino:** `cf6d1bb`.
- **Commit del manoscritto:** `423a8f1`.

## A. Unica modifica al testo

**Cap. 41, rr. 23 e 55:** «*12 novembre ?*» → «*12 novembre?*».

Ho letto le due frasi intere prima di cambiare:
- **r. 23:** «…Il foglio con la data e il punto interrogativo. *12 novembre?*»
- **r. 55:** «…e prese il foglio di agosto, e sotto *12 novembre?* cancellò il punto interrogativo. Accanto scrisse: *12.07.04. AGIORGI. 31.*»

La scena funziona ancora: Dalia cancella il segno «?» scritto sul foglio, e non conta se sul foglio fosse attaccato o staccato dalla data.

**Diff rispetto a `199f39c`:** solo `04-manoscritto/41-capitolo-41.md`, 2 righe.

```
-…Il foglio con la data e il punto interrogativo. *12 novembre ?*
+…Il foglio con la data e il punto interrogativo. *12 novembre?*
-…e prese il foglio di agosto, e sotto *12 novembre ?* cancellò il punto interrogativo. Accanto scrisse: *12.07.04. AGIORGI. 31.*
+…e prese il foglio di agosto, e sotto *12 novembre?* cancellò il punto interrogativo. Accanto scrisse: *12.07.04. AGIORGI. 31.*
```

## B. PDF definitivo

- Rigenerati con lo stesso impianto della fase 8 (`07-impaginazione/`, invariata):
  - `il-padre-del-mostro-completo.md`;
  - `il-padre-del-mostro-completo.pdf`;
  - `il-padre-del-mostro-rivisto.pdf`.
- **Nuova copia finale:** `05-output/il-padre-del-mostro-DEFINITIVO.pdf`, identica byte per byte al rivisto e al completo (verificato con `cmp`).
- Nessuna pagina bianca aggiunta e nessuna modifica all'impaginazione.

## C. Verifica

| Voce | Esito |
|---|---|
| Pagine totali | **494** (A5, 420 × 595 pt) |
| Pagine numerate | **490** (dal prologo = 1); 4 pagine iniziali senza numero: frontespizio, copyright, indice ×2 |
| Parole del manoscritto | **111.468** (stessa formula delle fasi precedenti; erano 111.470: i due «?» staccati contavano come parole) |
| Dimensione del file | **1.446.759 byte** |
| sha256 del DEFINITIVO | `150b76f71cba340bc9d87dc731d7ff9e466fee93a33a4ae1fa6a09703d1b8991` |
| Metadati | Title «Il padre del mostro», Author «F.R. Faraone» (pdfinfo) |
| Indice | 58 voci, tutte coincidono con la pagina del capitolo; ogni pagina porta il numero giusto |
| Virgolette dritte | 0 nel manoscritto, 0 nel PDF |
| «prima stesura» | 0 |
| «Felice» | 0 (manoscritto e PDF) |
| Spazi prima di ? ! , ; : . nel manoscritto | **0**. Nessuna eccezione da elencare: nemmeno dentro le « » c'è uno spazio voluto |
| Prologo | **pagina fisica 5, dispari, quindi a destra in stampa**. Non cambiato |
| Durate «N anni» | 386 occorrenze, identiche a `5ede115` |

**Correzione al report della fase 8.** Lì avevo scritto che il prologo cadeva su una pagina pari. Era sbagliato: è la pagina fisica 5, dispari, quindi a destra. La pagina bianca che proponevo non serve.

**Font** (`pdffonts`):

```
name                                 type              encoding         emb sub uni
AAAAAA+EBGaramond-Regular            CID TrueType      Identity-H       yes yes yes
BAAAAA+EBGaramond-Italic             CID TrueType      Identity-H       yes yes yes
CAAAAA+EBGaramond-Regular            CID TrueType      Identity-H       yes yes yes
AAAAAA+EBGaramond-Regular            CID TrueType      Identity-H       yes yes yes
BAAAAA+EBGaramond-Italic             CID TrueType      Identity-H       yes yes yes
EB Garamond Regular                  CID TrueType      Identity-H       yes no  yes
```

- Tutti i font sono **incorporati** (emb = yes) e sono solo EB Garamond.
- **Nessun font Type3.**
- L'ultima riga è il font dei numeri di pagina, incorporato intero (sub = no).

---

## Nota di chiusura (1 ottobre 2026)

**Righe cambiate:** cap. 41, rr. 23 e 55 (lo spazio prima del «?»).

**File rigenerati:**
- `05-output/il-padre-del-mostro-completo.md`;
- `05-output/il-padre-del-mostro-completo.pdf`;
- `05-output/il-padre-del-mostro-rivisto.pdf`;
- `05-output/il-padre-del-mostro-DEFINITIVO.pdf` (nuovo).

**Non toccato, e perché:**
- Durate, trama, voce e dialoghi, e tutte le scelte già approvate:
  - cap. 2, r. 29;
  - cap. 12, rr. 19, 25 e 71;
  - cap. 40, r. 59;
  - cap. 51, r. 89;
  - il «sei anni» di Nicola al cap. 43.
- `07-impaginazione/` (nessuna modifica): l'impaginazione resta quella della fase 8.
- «Felice Faraone» nei documenti di lavoro (`00-progetto/stato.md`, `02-bibbia/bibbia.md`, `01-mercato/mercato.md`): sono fuori dai file modificabili, e la questione resta aperta dalla fase 8.
- Il controllo con LanguageTool: non disponibile, perché il proxy blocca `languagetool.org` (vedi fase 8).

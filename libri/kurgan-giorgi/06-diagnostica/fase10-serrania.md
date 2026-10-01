# Fase 10 — Serrania — «Il padre del mostro»

- **Stato di partenza:** `561ef35`, verificato. **Commit del manoscritto:** `94f7d1b`.
- **Riferimento:** in `02-bibbia/nomi-inventati.md` la **Serrania** è la regione (aggettivo *serrano*) e la **Serrana** è l'organizzazione (affiliati: *serrani*).

## 1. Tabella

### «Serrania» (7 occorrenze, prima della correzione)

| Cap. | Riga | Forma scritta | Contesto | Trattata come |
|---|---|---|---|---|
| 3 | 49 | **a** Serrania (senza articolo) | «Nessuno a Serrania aveva capito da dove», dopo la strage dei capi «in undici posti diversi» | regione |
| 3 | 53 | **della** Serrania | «Adorisio era della Serrania anche lui» (provenienza) | regione |
| 5 | 119 | **a** Serrania (senza articolo) | «i frammenti di uno, sequestrati a Serrania la mattina dopo» (i droni dello stesso raid) | regione |
| 7 | 71 | **di** Serrania (senza articolo) | «Undici puntini luminosi sparsi su una mappa di Serrania» | regione |
| 10 | 39 | **di** Serrania (senza articolo) | «una mappa di Serrania. Undici puntini verdi, sparsi tra le montagne e la costa» | regione |
| 11 | 17 | **della** Serrania | «un uomo giovane e magro della Serrania» (provenienza) | regione |
| 33 | 53 | **da** Serrania (senza articolo) | «armi da guerra portate su da Serrania in una cisterna» | regione |

**Nessuna occorrenza tratta la Serrania come città o Stato:** non c'è niente da lasciare in sospeso.
- Rispetto alle quattro correzioni proposte nel controllo ortografico c'è **un quinto caso**, il cap. 10 r. 39 («una mappa di Serrania»). È nella stessa situazione del cap. 7 r. 71 e l'ho corretto per la stessa regola.

### «Serrana» (30 occorrenze): l'organizzazione, non toccata

Tutte nella forma «la Serrana / della Serrana» e tutte riferite all'organizzazione:
- **cap. 2:** rr. 71, 99;
- **cap. 3:** rr. 11, 47, 49, 99, 159;
- **cap. 5:** r. 71 (due volte);
- **cap. 7:** r. 135;
- **cap. 10:** rr. 51, 87, 99, 177;
- **cap. 13:** rr. 53, 77;
- **cap. 16:** r. 135;
- **cap. 18:** rr. 103, 105, 115, 117, 123, 129 (due volte), 145, 147, 163, 167;
- **cap. 24:** rr. 15, 39.

Gli usi sono «i capi della Serrana», «i sei della Serrana», «il ragazzo della Serrana», «il più anziano della Serrana».

## 2. Modifiche (prima → dopo)

| Cap. | Riga | Prima | Dopo |
|---|---|---|---|
| 3 | 49 | «Nessuno **a Serrania** aveva capito da dove.» | «Nessuno **in Serrania** aveva capito da dove.» |
| 5 | 119 | «Io ho i frammenti di uno, sequestrati **a Serrania** la mattina dopo.» | «Io ho i frammenti di uno, sequestrati **in Serrania** la mattina dopo.» |
| 7 | 71 | «Undici puntini luminosi sparsi su una mappa **di Serrania**.» | «Undici puntini luminosi sparsi su una mappa **della Serrania**.» |
| 10 | 39 | «Sullo schermo c'era una mappa **di Serrania**.» | «Sullo schermo c'era una mappa **della Serrania**.» |
| 33 | 53 | «…armi da guerra portate su **da Serrania** in una cisterna d'acqua per l'irrigazione.» | «…armi da guerra portate su **dalla Serrania** in una cisterna d'acqua per l'irrigazione.» |

Dopo la correzione tutte e 7 le occorrenze hanno l'articolo: in Serrania (2), della Serrania (4), dalla Serrania (1). Parole: invariate.

## 3. Derivati e verifiche

- Rigenerati con l'impianto della fase 9. `07-impaginazione/` è invariata rispetto a `87e4cba`:
  - `il-padre-del-mostro-completo.md`;
  - `il-padre-del-mostro-completo.pdf`;
  - `il-padre-del-mostro-rivisto.pdf`;
  - `il-padre-del-mostro-DEFINITIVO.pdf`.
- I tre PDF sono identici byte per byte (`cmp`).

| Voce | Esito |
|---|---|
| Pagine | **494** (4 iniziali senza numero + 490 numerate) |
| Parole del manoscritto | **111.468** (invariate) |
| Dimensione | 1.446.720 byte |
| sha256 DEFINITIVO | `fe460844b5515225f88a3840fcf2873564eb32761740652df227aed32dfa9a7d` |
| pdffonts | solo EB Garamond (regolare e corsivo), CID TrueType, tutti **incorporati**; **nessun Type3** |
| Metadati | Title «Il padre del mostro», Author «F.R. Faraone» |
| Indice | 58 voci, tutte coincidenti con le pagine; ogni pagina porta il numero giusto |
| «N anni» | 386 occorrenze, identiche a `5ede115` |
| Prologo | pagina fisica 5, **dispari** |
| Testo del PDF | le 7 «Serrania» compaiono tutte con l'articolo |

---

## Nota di chiusura (1 ottobre 2026)

**Righe cambiate** (commit `94f7d1b`):
- cap. 3, r. 49;
- cap. 5, r. 119;
- cap. 7, r. 71;
- cap. 10, r. 39;
- cap. 33, r. 53.

**Non toccato, e perché:**
- «Serrania» al cap. 3 r. 53 e al cap. 11 r. 17: hanno già l'articolo.
- Le 30 occorrenze di «Serrana»: sono l'organizzazione, per tua istruzione.
- `07-impaginazione/`: per tua istruzione.
- Durate, trama, voce, dialoghi e scelte già approvate.

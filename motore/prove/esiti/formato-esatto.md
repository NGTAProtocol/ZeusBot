# Formato esatto delle pagine: esito

Data: 2026-10-13. Ramo motore, partendo da 48d0a22.

## Difetto

Chromium arrotonda il formato della pagina. Il mini-libro A5 (5,83 × 8,27″) usciva a 420 × 594,96 pt
(5,833 × 8,263″) invece di 419,76 × 595,44 pt. I formati multipli di 1/96″ (5,5 × 8,5″) erano già esatti.

## Correzione (`script/impagina.py`, `formato_esatto`)

- Dopo l'unione di pagine iniziali e corpo, e prima dei numeri di pagina, ogni pagina va al formato
  esatto: trim di `libro.yaml`, più `cartaceo.bleed_pollici` di `dati/kdp.yaml` se `bleed: true`
  (larghezza + 1 bleed, altezza + 2 bleed).
- Il contenuto non si scala. Una traslazione (`q … cm … Q`) attorno al contenuto lo tiene fermo
  rispetto all'angolo in alto a sinistra.
- MediaBox e CropBox coincidono e partono da 0, 0. TrimBox e BleedBox non si scrivono: il motore non
  li gestiva.
- Con il bleed il contenuto scende di un bleed e, sulle pagine pari (esterno a sinistra), si sposta di
  un bleed a destra. Provato su una copia del romance con `bleed: true`: 405 × 630 pt, spostamenti di
  9 pt. Nessuna prova della suite copre il bleed.

## Verifiche (PDF prima e dopo la correzione)

| | A5 (mini-libro) | 5,5 × 8,5″ (romance) |
|---|---|---|
| Formato | 419,76 × 595,44 pt su tutte le pagine | 396 × 612 pt |
| Scarto su MediaBox e CropBox | 0,00001 pt (precisione con cui il numero è scritto nel PDF) | 0 |
| Spostamento delle parole rispetto all'alto a sinistra | massimo 0,0001 pt | 0 |
| Testo, font incorporati, metadati | invariati | invariati |

I numeri di pagina restano ancorati al piede, come prima.

## Suite

**424/424 OK, 0 saltate, 0 KO** (con LanguageTool). I margini alto e basso del mini-libro restano
0,798 e 0,356: nessun atteso modificato.

## Prove di regressione (ripetute, ogni alterazione ripristinata)

| Alterazione | Esito |
|---|---|
| (a) romance, margine esterno +0,02″ | KO: «0.646: fuori tolleranza» |
| (b) romance, margine esterno 5 mm, atteso 0,198 | KO: «0.198: sotto il minimo KDP 0.25» |
| (c1) romance, una parola aggiunta | KO della struttura (testo diverso) |
| (c2) PDF del romance con un font non incorporato | font_non_incorporati: 1, quindi KO della struttura |

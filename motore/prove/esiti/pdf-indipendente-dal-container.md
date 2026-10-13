# Prove del PDF indipendenti dal container: esito

Data: 2026-10-13. Ramo motore, partendo da 3a01e42.

## Problema

Nel passo 3, 4 prove dipendevano dal container in cui era stato fatto il render con Chromium:
- gli sha256 dei due PDF di prova;
- i margini interno ed esterno del romance (0,665/0,667 e 0,624/0,625).

## Modifiche (`script/prove.py`, `prove/attesi.yaml`)

- **Sha256 del PDF → struttura del PDF** (`struttura_pdf`). Per ciascun mini-libro una prova controlla:
  - le pagine;
  - il formato di ogni pagina, uguale al trim di `libro.yaml` più il bleed se previsto (bleed: `dati/kdp.yaml`);
  - i font: tutti incorporati, nessun Type3;
  - Title e Author uguali a `libro.yaml`;
  - il testo estratto con PyMuPDF, con gli spazi normalizzati: numero di parole e sha256.
- **Margini → tolleranza più minimo KDP** (`controllo_margine`). Ogni margine deve stare entro ±0,005″
  dall'atteso (`TOLLERANZA_MARGINI`, con commento) e non sotto il minimo KDP (`minimi_kdp`).
  - I minimi si leggono da `dati/kdp.yaml` con `comune.kdp_margini` e `comune.kdp_interno_pollici`:
    interno secondo il numero di pagine; esterno, alto e basso secondo il bleed. La fonte (KDP Help
    Center) è indicata nell'intestazione di `dati/kdp.yaml`.
  - Il minimo KDP vale anche dentro la tolleranza.
- Il numero di prove resta 424. Le altre prove non sono state toccate.
- Trasparenze: il motore non le gestisce, quindi non sono state aggiunte prove.
- Autore nei metadati: si confronta con l'autore di libro.yaml; i mini-libri hanno autori inventati,
  perché il motore non contiene libri reali.

## Prove di regressione

Ogni alterazione è stata temporanea e poi ripristinata con `git checkout`.

| Alterazione | Esito |
|---|---|
| (a) romance, margine esterno 16 → 16,508 mm (+0,02″) | KO: «0.646: fuori tolleranza» |
| (b) romance, margine esterno 5 mm, atteso portato a 0,198 | KO: «0.198: sotto il minimo KDP 0.25» |
| (c1) romance, una parola aggiunta al capitolo 1 | KO della struttura: 4556 parole, sha256 del testo diverso |
| (c2) PDF del romance con un font Helvetica non incorporato | font_non_incorporati: 1, quindi KO della struttura |

## Difetto trovato: formato A5 non esatto

Il mini-libro dichiara 5,83 × 8,27″ (A5), ma il PDF misura 420 × 594,96 pt, cioè 5,833 × 8,263″.

- Chromium arrotonda il formato della pagina, anche se lo riceve da `page.pdf` invece che dal CSS
  (provato: 420 × 595,92 pt).
- I formati multipli di 1/96″ (5,5 × 8,5″, 6 × 9″) escono esatti: il romance passa.
- Qualunque libro in A5, compreso un libro di prova, avrebbe lo stesso scarto.
- La prova «mini-libro: struttura del PDF» resta KO. La correzione, cioè riportare le pagine al trim
  esatto con PyMuPDF in `impagina.py`, cambia il PDF dei libri e sposta i margini di qualche millesimo:
  la decide l'autore.

## Esito della suite

Con LanguageTool: vedi il resoconto del commit (423/424 OK, 0 saltate, 1 KO: il formato A5 del mini-libro).

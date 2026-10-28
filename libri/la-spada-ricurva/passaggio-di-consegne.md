# Passaggio di consegne — La Spada Ricurva

## Stato (2026-10-28)
- Fase stesura; capitoli 1-6 scritti, rivisti, verificati e accettati; capsule 1-6 sul testo attuale.
- Fermo alla pausa di lettura sui capitoli 4-6: risposta dell'autore con «zb ok» oppure «zb correggi <note>».
- Parole: circa 11.300 su 90.000.

## Decisioni dell'autore
- Ora della morte (cap. 1): forbice larga della perizia (20:00-01:00) e ultimo battito all'orologio al polso alle
  22:46; messaggio alle 23:47: lo scarto di un'ora è l'ipotesi più forte, non una certezza.
- Gradini della scala del chiostro (cap. 1): generici, senza numero né materiale.
- Chiusure: cap. 1 R, cap. 2 P, cap. 3 X (finale riscritto come decisione; scaletta allineata).
- Fatti: verificati su fonte o resi generici in `06-diagnostica/difetti/fatti.yaml` (fonti nel registro).

## Prossimo passo
- Dopo la risposta alla pausa: capitolo 7 con `zb agenti prossimo libri/la-spada-ricurva`.

## Ripartenza
```
python3 -B motore/zb lavoro libro la-spada-ricurva
python3 -B motore/zb avvio libri/la-spada-ricurva --ruolo regia
python3 -B motore/zb agenti prossimo libri/la-spada-ricurva
```

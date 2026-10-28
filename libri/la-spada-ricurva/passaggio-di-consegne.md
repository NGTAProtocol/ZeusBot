# Passaggio di consegne — La Spada Ricurva

## Stato (2026-10-28)
- Fase stesura; capitoli 1-15 scritti, rivisti, verificati e accettati; capsule 1-15.
- PDF di lettura dei capitoli 1-12 mandato all'autore; pausa sui capitoli 7-12 chiusa con «Continua».
- Fermo alla pausa di lettura sui capitoli 13-15: risposta dell'autore «ok» oppure «correggi <note>».
- Fatti fino a F106. Anno convenzionale 2025 non confermato: niente giorni della settimana nel testo.

## Decisioni dell'autore
- Ora della morte (cap. 1): forbice larga della perizia (20:00-01:00) e ultimo battito all'orologio al polso alle
  22:46; messaggio alle 23:47: lo scarto di un'ora è l'ipotesi più forte, non una certezza.
- Gradini della scala del chiostro (cap. 1): generici, senza numero né materiale.
- Narratrice: Elena (non «Elana»).
- Chiusure: cap. 1 R, cap. 2 P, cap. 3 X (finale riscritto come decisione; scaletta allineata).
- Fatti: verificati su fonte o resi generici in `06-diagnostica/difetti/fatti.yaml` (fonti nel registro).

## Prossimo passo
- Dopo la risposta alla pausa: capitolo 16 con `zb agenti prossimo libri/la-spada-ricurva`.
- Motore, da sistemare: promesse citate solo per id nella scheda; lunghezza minima dei capitoli non controllata;
  fatti doppi riformulati senza citazione; giri di controllo costosi per ritocchi di una riga.

## Ripartenza
```
python3 -B motore/zb lavoro libro la-spada-ricurva
python3 -B motore/zb avvio libri/la-spada-ricurva --ruolo regia
python3 -B motore/zb agenti prossimo libri/la-spada-ricurva
```

# Audit — ortografia

Hunspell it_IT su tutte le parole del manoscritto, escluse nomi_propri.txt e parole-ammesse-it.txt. Parole non riconosciute: 77.

## Casi certi

- 4:41 «un ciuffo di qualcosa di giallo che di cui non sapevo il nome»: «che di cui» → «di cui» (errore grammaticale; Hunspell non lo vede).
- Parole ripetute per errore: nessuna («stretti stretti», 24:107, è voluto).

## Dubbi (da decidere)

- «rispegnevano» (1×) — suggerimenti: rispendevano, spegnevano, rispiegavano. Forma di «rispegnere», corretta ma rara (31:15).
- «Tienitele» (1×) — suggerimenti: Tientele, Tienicele, Tienimele. Corretta (tieni + ti + le).
- «giallina» (1×) — suggerimenti: gallina, giallino, ingiallir. Corretta (diminutivo).
- «riappoggiai» (1×) — suggerimenti: appoggiai, appoggiacapo, appoggiar. Corretta (ri- + appoggiare).
- «guantata» (1×) — suggerimenti: guantaia, guastata, agguantata. Corretta (participio di «guantare»).

## Falsi positivi (non errori)

- Elisioni spezzate dal tokenizzatore (all', dell', quell', cinquant'…): 446 occorrenze.
- Dialetto e vocativi voluti: Capu, Citte, Gaetà, Michè, Mmh, Nicò, Obrigado, Pai, Tonì, Totò, Uagliò, Uagnò, Uè, Vitù, Zi, cangiau, cca, cchiù, chiddu, cu, mercatu, muntagna, obrigado, pai, restu, sapimu, uagliò, veru, vostru, zi. Da valutare: «uagliò» in 36:83 (vicino barese: «uagnò»).
- Nomi di luogo e di persona: Garelli, Japigia, Madonnella, Modugno, Peppe (da aggiungere a nomi_propri.txt).

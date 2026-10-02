# Passi 1b e 2 — Prove ripetibili e controlli del testo: esito

Data: 2026-10-02. Proposta di riferimento: `motore/proposta-motore.md` (approvata), B.7 passo 2.

## Passo 1b (commit separato)

- `script/prove.py` («zb prove»): esegue tutte le prove dei passi presenti in `prove/attesi.yaml` su copie temporanee dei mini-libri, stampa la tabella e rilancia `separazione.py` e `recinto.py`; codice 0 solo se tutto è OK.
- `README.md`: regola «python3 -B», nomi dei file del manoscritto, comandi.
- Esito prima del passo 2: 35/35 OK.

## Passo 2: file

| File | Stato |
|---|---|
| dati/lista-nera.yaml | nuovo: 19 voci (05-critica rr. 19-20) + parole filtro (r. 21) |
| script/stile.py | nuovo |
| script/continuita.py | nuovo |
| script/riciclo.py | nuovo |
| script/capitolo.py | nuovo |
| script/comune.py | aggiunte funzioni di testo (righe di prosa, parole, dichiarazioni, elenchi di capitoli, tabelle) |
| script/prove.py | aggiunta la sezione passo_2 |
| script/recinto.py | aggiunti i comandi del passo 2 |
| prove/attesi.yaml | aggiunta la sezione passo_2 |
| prove/mini-libro/ | libro.yaml (riga_finale_min_parole: 3; obbligatorio_in vuoto), cronologia (assunzione a settembre 2017), bibbia e briefing allineati |

## Esito

**Prove: 83/83 OK** (35 del passo 1 + 48 del passo 2). separazione.py OK; recinto.py OK su 20 esecuzioni.

Errori voluti di B.2.2, tutti trovati:

| Mini-libro | Unità | Controllo | Esito |
|---|---|---|---|
| giallo | 2 | lista nera «un brivido le percorse la schiena» | KO |
| giallo | 2 | «come se» 6 volte (massimo 2) | KO |
| giallo | 2 | «Lodovico Arsa» prima del cap. 3 (4 righe) | KO |
| giallo | 2 | «venerdì 4 marzo»: nel 2021 è giovedì | KO |
| giallo | 2 | Irene Calvi «quarantadue anni», ne ha 35 | KO |
| giallo | 2 | «Brena» e «Brenna» | AVVISO |
| giallo | 2 | chiusura dichiarata X, prevista R | AVVISO |
| giallo | 3 | 457 parole, minimo 800 | KO |
| giallo | 3 | frase media 45,3, dialogo 0% | KO |
| giallo | 3 | ultima riga di una parola | KO |
| romance | 3 (capitolo-prova) | minimo 1.500, frase media 9,8, dialogo 29,5%, tre chiusure su domanda di fila | KO |
| giallo | 1 (capitolo-prova) | stesso testo | nessun KO |

## Scelte non scritte nella proposta

1. Frase media e dialogo % si controllano solo sui capitoli numerati, non su prologo, epilogo e interludi.
2. Le misure di stile escludono la riga d'intestazione in corsivo e i separatori; il conteggio delle parole del capitolo resta quello di conta.py.
3. Una frase finisce con «.», «!», «?» o «…» seguiti da uno spazio; il dialogo è una riga che comincia con la lineetta di lingue.yaml.
4. Anti-riciclo: le ripetizioni rispetto al testo precedente sono KO; quelle tra capitoli dello stesso libro sono AVVISO.
5. Chiusura dichiarata diversa dalla scaletta: AVVISO. Ultima riga troppo corta: KO solo se il libro dichiara `riga_finale_min_parole`.
6. Similitudini e tic dei gesti: solo AVVISO (il conteggio dei candidati non distingue le similitudini vere).
7. Nomi in due grafie: avviso per parole con la maiuscola di almeno 5 lettere, stessa iniziale e distanza di modifica 1 da un nome dell'elenco.
8. Età: controllata quando nella stessa frase ci sono un personaggio con data di nascita e «N anni».
9. Data di un'unità: dall'intestazione, altrimenti dalla colonna «Data» della scaletta.
10. «solo_dialogo» delle voci non è ancora applicato.

## Non fatto in questo passo

- Tic «meteo all'inizio del capitolo» e «domande retoriche in serie» (05 r. 20): non rilevabili con affidabilità; restano al controllo a vista.

## Le tre modifiche al mini-libro giallo (chiarimento del passo 2b)

| Modifica | Errore di prova che toglieva | Controllo che continua a esercitare |
|---|---|---|
| Assunzione di Gemma da giugno a settembre 2017 (cronologia.yaml e bibbia) | Con giugno, «tre anni, quasi quattro» (36 mesi dichiarati) contro 45 mesi calcolati superava la tolleranza di 6 mesi: dava un KO di durata nel cap. 1, che per B.2.2 deve passare tutti i controlli. | Il controllo `durata` gira ancora sul cap. 1: trova la frase, ricalcola dalle date (42 mesi) e la accetta al limite della tolleranza. La prova «cap. 1: 0 esiti» lo verifica. |
| `obbligatorio_in: ["3"]` diventa `[]` per «Lodovico Arsa» | Il cap. 3 non nomina Lodovico Arsa: dava un KO «nome_obbligatorio» non previsto tra gli errori voluti. | Il divieto prima del cap. 3 resta esercitato (4 KO nel cap. 2). Il ramo «obbligatorio» si prova dal passo 2b su una copia con `obbligatorio_in: ["3"]`: KO atteso nel cap. 3. |
| Briefing: «il nome del colpevole» diventa «il nome di Lodovico Arsa» | Nessun errore di prova: era un'incoerenza del testo, perché nella storia il colpevole è la sorella. | Nessun controllo cambia: la regola resta quella di `nome_vietato_prima_di` in libro.yaml. |

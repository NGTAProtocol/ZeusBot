# Passo 1 — Fondamenta: esito

Data: 2026-10-02. Proposta di riferimento: `motore/proposta-motore.md` (approvata, commit 6821b44), B.7 passo 1.

## File creati

| File | Righe |
|---|---|
| script/comune.py | 312 |
| script/conta.py | 102 |
| script/valida_profili.py | 76 |
| script/separazione.py | 119 |
| script/recinto.py | 98 |
| dati/libro.schema.yaml | 130 |
| dati/profilo.schema.yaml | 73 |
| dati/stato.schema.yaml | 28 |
| dati/lingue.yaml | 7 |
| dati/nomi_vietati.txt | 3 (solo commenti) |
| profili/ (7 file) | 35-40 ciascuno |
| prove/mini-libro/ (giallo, 10 file) | capitoli: 109, 75, 7; interludio 3 |
| prove/mini-libro-romance/ (10 file) | capitoli: 123, 131, 109 |
| prove/attesi.yaml | 58 |

## Prove (35, tutte sui due mini-libri inventati)

| Script | Controllo | Atteso | Ottenuto | Esito |
|---|---|---|---|---|
| valida_profili.py | 7 profili | OK ×7 | OK ×7 | OK |
| valida_profili.py | profilo con valore senza fonte | KO | KO | OK |
| valida_profili.py | profilo con media oltre il massimo | KO | KO | OK |
| valida_profili.py | esecuzione su profili/ | 0 | 0 | OK |
| comune.py | libro.yaml giallo e romance contro lo schema | OK ×2 | OK ×2 | OK |
| comune.py | lingua: en / lingua mancante | rifiuto | rifiuto | OK |
| comune.py | override senza motivo | rifiuto | rifiuto | OK |
| comune.py | valore del profilo cambiato senza override | rifiuto | rifiuto | OK |
| comune.py | riscrittura senza testo_precedente | rifiuto | rifiuto | OK |
| stato.schema.yaml | esempio C.1 / senza fase | OK / KO | OK / KO | OK |
| conta.py | ordine delle unità (giallo, romance) | da attesi | uguale | OK |
| conta.py | parole per unità (7 unità) | da attesi | uguale | OK |
| conta.py | totale nel report: giallo 2578, romance 4313 | da attesi | uguale | OK |
| comune.py | scrivi fuori dal libro (assoluto e con ../) | rifiutata | rifiutata | OK |
| separazione.py | nome vietato in una copia di motore/ | 1 | 1 | OK |
| separazione.py | libro.yaml fuori dai mini-libri | 1 | 1 | OK |
| recinto.py | scrittura messa apposta in motore/ | 1 | 1 | OK |

I conteggi attesi sono calcolati con una pipeline di shell indipendente da conta.py (in testa ad attesi.yaml).

## Separazione e recinto su motore/

- separazione.py: OK, codice 0.
- recinto.py: OK, 8 esecuzioni (4 comandi × 2 mini-libri), nessuna scrittura fuori dal libro, codice 0.

## Scelte non scritte nella proposta

1. Schemi in un formato YAML proprio, con validatore in comune.py: nel container non c'è jsonschema.
2. conta.py esclude anche le righe di commento HTML (la riga nascosta `<!-- zb: … -->`), trattate come «note» (12-lunghezze r. 6). La riga d'intestazione in corsivo si conta.
3. Nomi dei file in 04-manoscritto: `prologo.md`, `NN-<slug>.md`, `interludio-<NUMERO>.md`, `epilogo.md`.
4. piano-parole.md si legge dalle colonne «Cap.» e «Budget capitolo» (formato di 12-lunghezze r. 62).
5. In valida_profili.py la fonte può stare sulla riga del valore o su una riga madre (per esempio `formati:` copre `breve`, `standard`…).
6. Gli script impostano `dont_write_bytecode`: senza, Python creerebbe `__pycache__` in motore/script, che recinto.py segnalerebbe come scrittura fuori dal libro.
7. recinto.py fotografa il repository che contiene motore/ (esclusa .git); ha l'opzione `--extra` per provare una scrittura messa apposta.
8. Ogni profilo ha due righe di commento in testa; il resto è copiato dalla proposta.
9. Il mini-libro giallo totalizza 2578 parole su 3000 (−14%), per effetto voluto del cap. 3 corto; conta.py lo segnala come fuori dal ±5%, senza KO (i KO di lunghezza sono del passo 2).
10. Il mini-libro romance ha `serie` ed `ebook: true`, per le prove del passo 4.
11. Lo script che esegue le prove non è tra i file del passo 1: le prove sono state eseguite da uno script fuori dal repository.

## Non fatto in questo passo

- Parole per pagina in conta.py: serve il PDF (passo 3).
- Controllo dell'esistenza di dati/lista-nera.yaml citata dai profili: il file è del passo 2.

# Passo 4 — Pubblicazione: esito

Data: 2026-10-02. Proposta di riferimento: `motore/proposta-motore.md` (approvata), A.2-A.9 e B.7 passo 4.

## File

| File | Righe |
|---|---|
| dati/kdp.yaml | 82 (completato come A.2; la sezione margini era del passo 3b) |
| dati/verifiche-kdp.md | 8 (registro vuoto) |
| modelli/conferme-autore.yaml | 12 |
| script/conformita_kdp.py | 343 |
| script/kdp_verifica.py | 129 |
| script/pacchetto.py | 110 |
| prove/pubblicazione/ | scheda-giallo.md 30, scheda-romance.md 30, conferme-tutto-ok.yaml 10 (testi inventati) |
| script/comune.py | + oggi() (data fissabile con --oggi o ZB_OGGI) |
| script/recinto.py | + pacchetto, conformita_kdp, kdp_verifica controlla/stato; etichetta dell'eccezione |
| script/prove.py, prove/attesi.yaml, README.md | + passo 4 |

## Esito

**zb prove: 163/163 OK** (127 dei passi 1-3b + 36 del passo 4). separazione.py OK; recinto.py OK su 34 esecuzioni.

Alla prima esecuzione 3 prove su 163 erano KO. Ciascuna ha avuto una sola correzione mirata:
1. `avviso_formato: no` in attesi.yaml veniva letto da YAML come «falso»: scritto tra virgolette.
2. La prova di ultima_verifica confrontava la riga con il commento finale compreso: ora confronta solo il valore.
3. L'eccezione di recinto.py compare 3 volte, non 4: alla seconda esecuzione, con la stessa data, dati/kdp.yaml resta identico e cambia solo il registro. Corretto il valore atteso.

| Prova | Atteso | Ottenuto |
|---|---|---|
| giallo, conferme non date | KO nelle sezioni 8, 9, 11, 13, 14, 15; codice 1 | uguale |
| romance, conferme non date | KO nelle sezioni 8, 9, 11, 12, 13, 14, 15; codice 1 | uguale |
| sezione 11 per costruzione | «16 pagine (minimo 24)» / «23 pagine (minimo 24)» | uguale |
| tutto OK (PDF sintetico di 32 pagine, conferme date, verifica del 2026-10-01) | nessun KO, codice 0 | uguale |
| formato_confermato_kdp false / true | sezione 11 OK con avviso / OK senza avviso | uguale |
| «Amazzonia» / «Kindle» nelle parole chiave | sezione 7 OK / KO | uguale |
| descrizione di 4.001 caratteri; URL nella descrizione | sezione 4 KO | uguale |
| 8 parole chiave | sezione 7 KO | uguale |
| autore della scheda diverso dal PDF | sezione 5 KO | uguale |
| ultima_verifica nulla / scaduta | codice 2 | uguale |
| kdp_verifica: data futura, data scritta male | rifiutate (codice 1) | uguale |
| kdp_verifica: data valida | ultima_verifica scritta, 1 riga nel registro | uguale |
| kdp_verifica: data già scaduta | accettata con avviso | uguale |
| promemoria con il proxy bloccato | 7 righe numerate | uguale |
| recinto.py con «verifica KDP fatta» | eccezione dichiarata, codice 0 | uguale |
| pacchetto.py | 6 file; alla seconda esecuzione nessuno; scheda non toccata | uguale |

## Scelte non scritte nella proposta

1. Codici d'uscita di conformita_kdp.py: se c'è un KO vale 1, anche con la verifica scaduta; il codice 2 vale solo senza KO.
2. «n/a» e «nessuno» stanno in `valori_vuoti_vietati` (KO solo se sono l'intero valore), separati da `parole_vietate`.
3. La scheda Amazon ha un formato fisso, letto da conformita_kdp.py: righe «Campo: valore», poi le sezioni «## Descrizione», «## Parole chiave» e «## Categorie» con elenchi numerati.
4. Sezione 12: con `ebook: true` manca ebook.docx, perché il motore non lo produce, quindi KO; con il file presente si controllano gli stili Titolo 1/2 e l'assenza di numeri di pagina, intestazioni e piè di pagina; Kindle Previewer è sempre un avviso.
5. Sezione 15: KO anche per formule non neutre nel manoscritto («recensione positiva», «5 stelle», «in cambio di»); il pattern sta in kdp.yaml.
6. Sezione 7: parole del titolo o del sottotitolo ripetute nelle parole chiave → avviso (solo parole di più di 3 lettere).
7. kdp_verifica.py ha tre comandi: `fatta`, `controlla`, `stato`. `controlla` stampa il promemoria anche quando le pagine sono raggiungibili, perché il confronto dei valori resta a mano.
8. Data di oggi fissabile con `--oggi` o `ZB_OGGI`, così le prove non dipendono dal giorno in cui girano.
9. Il PDF sintetico del percorso «tutto OK» ripete le pagine del PDF del giallo fino a 32 (almeno 30, numero pari), copiando i metadati, senza aggiungere testo.
10. I codici delle pagine ufficiali KDP in kdp.yaml restano «da confermare alla prima verifica» (proposta A.8).

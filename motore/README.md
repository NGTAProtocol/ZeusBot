# Motore editoriale

Fabbrica generica per romanzi di qualsiasi genere: procedura, script, modelli vuoti,
profili di genere e dati KDP. Non contiene libri reali. Il progetto completo è in
`proposta-motore.md` (approvata); questo file raccoglie le regole d'uso già in vigore.
È una prima versione: si completa al passo 5 di B.7, insieme a `PROCEDURA.md`.

## Regole d'uso

- **Lancia sempre gli script con `python3 -B`.** L'opzione `-B` impedisce a Python di
  scrivere `__pycache__` dentro `motore/script/`: sarebbe una scrittura fuori dal libro,
  e `recinto.py` la segnalerebbe.
- Il libro si indica con un percorso: `python3 -B motore/script/<script>.py <libro>`.
  Il motore cerca `libro.yaml` nel percorso e nelle cartelle superiori.
- Ogni comando che opera su un libro scrive solo dentro la cartella del libro.

## Nomi dei file del manoscritto (`<libro>/04-manoscritto/`)

| File | Unità |
|---|---|
| `prologo.md` | prologo |
| `NN-<slug>.md` | capitolo NN (per esempio `07-la-stazione.md`) |
| `interludio-<N>.md` | interludio N (per esempio `interludio-II.md`), collocato con `struttura.interludi[].dopo_capitolo` di `libro.yaml` |
| `epilogo.md` | epilogo |

Un file con un nome diverso ferma il motore.

## Comandi disponibili

| Comando | Cosa fa |
|---|---|
| `python3 -B motore/script/prove.py` | «zb prove»: tutte le prove sui due mini-libri inventati, confronto con `prove/attesi.yaml`, poi `separazione.py` e `recinto.py`; codice 0 solo se tutto è OK |
| `python3 -B motore/script/conta.py <libro> [--schermo]` | conteggio delle parole con il metodo unico |
| `python3 -B motore/script/valida_profili.py` | valida i profili di genere |
| `python3 -B motore/script/capitolo.py <libro> <N>` | tutti i controlli di un capitolo (parole, stile, continuità, riciclo, dichiarazioni); `N` può essere anche `prologo`, `epilogo`, `interludio II` |
| `python3 -B motore/script/stile.py <libro> [N]` | frase media, dialogo %, lista nera e voci del libro, parole filtro, similitudini, vincoli, nomi vietati |
| `python3 -B motore/script/continuita.py <libro>` | giorni della settimana, età, durate, cifre, nomi in due grafie; checklist manuale |
| `python3 -B motore/script/riciclo.py <libro>` | sequenze di 7 parole ripetute (testo precedente: KO; capitoli precedenti: avviso) |
| `python3 -B motore/script/separazione.py` | controlla che `motore/` non contenga libri |
| `python3 -B motore/script/recinto.py` | controlla che i comandi scrivano solo nel libro indicato |

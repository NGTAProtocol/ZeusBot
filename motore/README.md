# Motore editoriale

Fabbrica generica per romanzi di qualsiasi genere: procedura, script, modelli vuoti,
profili di genere e dati KDP. Non contiene libri reali. Il progetto completo è in
`proposta-motore.md` (approvata). Come si lavora su un libro: `PROCEDURA.md`.
Questo file raccoglie le regole d'uso e i comandi.

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

## Comandi `zb`

Si lanciano con `python3 motore/zb <comando> …` (il libro è sempre un percorso, oppure `ZB_LIBRO`).

| Comando | Script | Cosa fa |
|---|---|---|
| `zb nuovo <briefing>` | `nuovo.py` | crea il libro dal briefing (modello in `modelli/briefing.md`); briefing incompleto: elenca cosa manca e non crea nulla |
| `zb avvio <libro>` | `avvio.py` | avvio obbligatorio: controlli, riga «Letto: …», marker `<libro>/.zb/letto-<sessione>` |
| `zb stato <libro>` | `fase.py` | stato del libro (non scrive) |
| `zb ok <libro> [lotti da N]` · `zb avanti <libro>` · `zb correggi <libro> <istruzione>` | `fase.py` | risposte dell'autore al gate aperto |
| `zb pronto <libro>` · `zb esito <libro> N` | `fase.py` | fine del lavoro di una fase; esito dei controlli del capitolo N |
| `zb revisione <libro> <documento\|gate> [N]` | `revisione.py` | blocco N di un documento, circa 120 righe (non scrive) |
| `zb capitolo` · `conta` · `stile` · `continuita` · `riciclo` · `compila` · `impagina` · `pdf` · `kdp` · `pacchetto` `<libro>` | vedi sotto | controlli, stampa, pubblicazione |
| `zb verifica KDP fatta [AAAA-MM-GG]` · `stato` · `controlla` | `kdp_verifica.py` | verifica delle direttive KDP |
| `zb hook stato` · `attiva [--ok]` · `disattiva` | `zb` | hook di Claude Code: `attiva` senza `--ok` mostra soltanto; con `--ok` crea `.claude/settings.json` |
| `zb prove` · `separazione` · `recinto` · `profili` | | prove del motore |

`zb ortografia` è previsto ma lo script non c'è ancora.

## Script

| Comando | Cosa fa |
|---|---|
| `python3 -B motore/script/prove.py` | «zb prove»: tutte le prove sui due mini-libri inventati, confronto con `prove/attesi.yaml`, poi `separazione.py` e `recinto.py`; codice 0 solo se tutto è OK |
| `python3 -B motore/script/conta.py <libro> [--schermo]` | conteggio delle parole con il metodo unico |
| `python3 -B motore/script/valida_profili.py` | valida i profili di genere |
| `python3 -B motore/script/capitolo.py <libro> <N>` | tutti i controlli di un capitolo (parole, stile, continuità, riciclo, dichiarazioni); `N` può essere anche `prologo`, `epilogo`, `interludio II` |
| `python3 -B motore/script/stile.py <libro> [N]` | frase media, dialogo %, lista nera e voci del libro, parole filtro, similitudini, vincoli, nomi vietati |
| `python3 -B motore/script/continuita.py <libro>` | giorni della settimana, età, durate, cifre, nomi in due grafie; checklist manuale |
| `python3 -B motore/script/riciclo.py <libro>` | sequenze di 7 parole ripetute (testo precedente: KO; capitoli precedenti: avviso) |
| `python3 -B motore/script/compila.py <libro>` | manoscritto completo in `<libro>/05-output/<titolo>-completo.md` |
| `python3 -B motore/script/impagina.py <libro>` | PDF di stampa in `<libro>/05-output/<titolo>.pdf` (Chromium via Node e Playwright, PyMuPDF; font di `stampa/font/`) |
| `python3 -B motore/script/verifica_pdf.py <libro> [--pdf <file>]` | pagine, metadati, font, margini contro la tabella KDP, sommario contro le pagine, parole per pagina |
| `python3 -B motore/script/pacchetto.py <libro>` | struttura di `06-pubblicazione/` con i modelli compilati da `libro.yaml` (nessun testo commerciale; non sovrascrive) |
| `python3 -B motore/script/conformita_kdp.py <libro> [--pdf <file>]` | conformità KDP sezioni 1-15; codice 0 tutto OK, 1 almeno un KO, 2 verifica delle direttive mai fatta o scaduta |
| `python3 -B motore/script/kdp_verifica.py fatta [AAAA-MM-GG]` | «verifica KDP fatta»: l'autore registra la data in `dati/kdp.yaml` e `dati/verifiche-kdp.md` |
| `python3 -B motore/script/kdp_verifica.py controlla` | prova a raggiungere le pagine ufficiali; se bloccate, promemoria dei sette valori |
| `python3 -B motore/script/kdp_verifica.py stato` | stato della verifica delle direttive (codice 2 se mai fatta o scaduta) |
| `python3 -B motore/script/separazione.py` | controlla che `motore/` non contenga libri |
| `python3 -B motore/script/recinto.py` | controlla che i comandi scrivano solo nel libro indicato |
| `python3 -B motore/script/hook_sessione.py` | hook SessionStart (stdin JSON): session_id in `.zb/sessione-corrente` |
| `python3 -B motore/script/hook_manoscritto.py` | hook PreToolUse (stdin JSON): avviso o blocco sulle scritture nel manoscritto senza avvio |

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

## Dal briefing al PDF

1. L'autore compila `modelli/briefing.md` nella cartella del libro; `zb nuovo <briefing>` crea il libro.
   Per un libro già avviato con documenti propri: `zb adotta <cartella>`.
2. A ogni sessione: `zb avvio <libro>` e la riga «Letto: …».
3. Fase documenti: bibbia, cronologia, scaletta e piano parole; `zb pronto`, poi `avanti` e `ok`.
4. Fase pagina campione: `05-revisioni/pagina-campione.md`; `zb pronto`, poi `ok`.
5. Stesura: un capitolo alla volta, `zb esito <libro> N`; fermata dopo il capitolo 3, poi lotti di N.
6. Due controlli falliti di fila sullo stesso capitolo: fermata e decisione dell'autore.
7. Chiusura: `continuita`, `ortografia`, `compila`, `impagina`, `pdf`, `pacchetto`, `kdp`; `zb pronto`.
8. A ogni passo: commit, push, `git status -sb`, `git log -1` (blocco di salvataggio, `PROCEDURA.md`).

## Comandi

Si lanciano con `python3 motore/zb <comando> …`; il libro è sempre un percorso (oppure `ZB_LIBRO`).

- `zb nuovo <briefing>`: crea il libro dal briefing; se è incompleto elenca cosa manca e non crea nulla.
- `zb avvio <libro>`: controlli di avvio e riga «Letto: …»; si ferma se qualcosa non va.
- `zb stato <libro>`: fase, gate, capitoli, parole, allineamento con origin; non scrive.
- `zb pronto <libro>`: fine del lavoro di una fase; apre il gate o passa oltre.
- `zb esito <libro> N`: controlli del capitolo N e registrazione dell'esito.
- `zb ok <libro> [lotti da N]`: approva il gate aperto, dopo aver mostrato tutti i blocchi.
- `zb avanti <libro>`: blocco successivo dei documenti del gate.
- `zb correggi <libro> <istruzione>`: registra una correzione; il gate resta aperto.
- `zb riapprova <libro> <documento> <motivo>`: registra una modifica autorizzata a un documento già approvato.
- `zb adotta <cartella>`: bozze di libro.yaml, stato, cronologia e nomi da documenti esistenti, con le fonti.
- `zb conta <libro>`: parole con il metodo unico, per capitolo e totale.
- `zb stile <libro> [N]`: frase media, dialogo, lista nera, tetti, similitudini, vincoli.
- `zb continuita <libro>`: date, età, durate, cifre, nomi scritti in due modi.
- `zb capitolo <libro> N`: tutti i controlli di un capitolo, con report.
- `zb ortografia <libro>`: Hunspell, LanguageTool se disponibile, checklist per la lettura umana.
- `zb compila <libro>`: manoscritto completo in `05-output/`.
- `zb impagina <libro>`: PDF di stampa in `05-output/`.
- `zb pdf <libro>`: verifica del PDF (pagine, font, margini, indice).
- `zb kdp <libro>`: conformità KDP, sezioni 1-15.
- `zb pacchetto <libro>`: struttura di `06-pubblicazione/` per KDP.
- `zb revisione <libro> <documento|gate> [N]`: un documento in blocchi di circa 120 righe; non scrive.
- `zb pulizia <libro> [--applica]`: elenco di temporanei, cartelle vuote e copie; cancella solo con `--applica`.
- `zb hook stato|attiva [--ok]|disattiva`: hook di Claude Code (oggi in modalità avviso, non attivi).
- `zb prove`: tutte le prove sui mini-libri inventati, più separazione e recinto.

Altri comandi: `zb verifica KDP fatta [AAAA-MM-GG]` (anche `stato`, `controlla`), `zb riciclo <libro>`,
`zb separazione`, `zb recinto`, `zb profili`, `zb aiuto`.

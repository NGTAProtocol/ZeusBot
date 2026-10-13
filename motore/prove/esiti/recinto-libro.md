# Recinto sul libro: zb nuovo, hook di blocco, regola di avvio: esito

Data: 2026-10-13. Ramo motore, partendo da fd61225.

## Decisioni dell'autore

- Strada «c»: i libri restano nel repository, in `libri/<slug>/`, solo sui rami di libro; il ramo
  `motore` non contiene mai un libro.
- Hook di Claude Code in modalità blocco sulle scritture fuori dal libro attivo.

## Cosa cambia

- `nuovo.py`: `controlla_posizione` prima di creare qualsiasi cosa. Rifiutato (codice 2, messaggio con la
  regola) se la cartella è dentro `motore/`, è la radice del repository, il ramo è `motore`, oppure non è
  `libri/<slug>/`. Le prove della suite (`ZB_PROVE=1`, impostata da `prove.py`) sono esenti solo
  dall'ultimo controllo, perché usano cartelle temporanee. Dopo la nascita in `libri/<slug>/` imposta
  il libro attivo.
- `hook_recinto.py` (nuovo), aggiunto al modello `dati/hook-settings.esempio.json` (PreToolUse su Write,
  Edit, MultiEdit, NotebookEdit). Sul ramo `motore` nessun `.claude/settings.json`: sui rami di libro
  si attiva con `zb hook attiva --ok`, insieme all'hook del manoscritto (avviso). Libro attivo da `libri/libro-attivo.md`; consentito solo `libri/<slug>/`, tutto il resto
  bloccato (codice 2). Eccezioni: il briefing di un libro che non ha ancora `libro.yaml`; «lavoro sul
  motore» (`zb lavoro motore`: consentito il repository tranne `libri/`). `libro-attivo.md` assente o
  vuoto: avviso, non blocco.
- `zb lavoro stato | motore | libro <slug>` (in `zb`, che lancia `hook_recinto.py lavoro …`); stato in
  `<git-dir>/zb-lavoro`, non tracciato. `zb lavoro libro` si rifiuta sul ramo `motore`.
- `CLAUDE.md` (29 righe, nessun percorso di libro): regola madre, regola di avvio per ogni briefing
  nuovo («nella cartella del libro»), recinto, report di sessione (ogni 5 scambi o a «passaggio»; sezioni fisse).
- `passaggio-di-consegne.md` del motore riordinato nelle sezioni fisse.

## Conflitti con prove già verdi (prima esecuzione: 454/457)

La prima versione metteva `.claude/settings.json` nel motore e allungava CLAUDE.md con «libri/<slug>/»:
tre prove già verdi di «passo 5» fallivano (righe di CLAUDE.md ≤ 30, nessun `libri/` in CLAUDE.md,
`.claude/settings.json` assente dal repository del motore). Decisione dell'autore: nessuna prova
cambiata. Correzioni: settings.json tolto, hook nel modello, CLAUDE.md accorciato e senza `libri/`.
La prova dell'hook chiama `hook_recinto.py` direttamente e non leggeva `settings.json`: invariata.

## Prove (+3, sezione «recinto libro», libro inventato dal briefing di prova)

| Prova | Atteso |
|---|---|
| `zb nuovo` con la cartella in `motore/giallo` di un repository temporaneo | codice 2, messaggio «è dentro motore/», nella cartella resta solo il briefing |
| `zb nuovo` in `libri/giallo` di un repository temporaneo sul ramo `motore` | codice 2, messaggio sul ramo «motore», nella cartella resta solo il briefing |
| hook con libro attivo `giallo`: Write su `motore/nota.md` / su `libri/giallo/02-bibbia/nota.md` | `2` con «RECINTO» / `0` senza messaggio |

Nessuna prova esistente modificata: con `ZB_PROVE=1` le prove di `zb nuovo` già presenti (libri in
cartelle temporanee, ramo «prova») danno gli stessi esiti.

Verifica a mano, fuori dalla suite (repository temporaneo): avviso senza libro attivo; `zb nuovo
libri/giallo/briefing.md` crea il libro e imposta `libro-attivo.md`; bloccati `motore/`, un altro libro e
un file fuori dal repository; consentito il briefing di un libro non ancora nato; con `zb lavoro motore`
consentito `motore/` e bloccato `libri/`; `zb nuovo` fuori da `libri/` senza `ZB_PROVE` rifiutato.

## Suite

`ZB_LANGUAGETOOL=<scratchpad>/lt/lib ZB_BANCA_VOCI=/home/user/banca-voci python3 -B motore/zb prove`,
eseguita una volta: **457/457 OK**, 0 saltate. `separazione.py` OK, `recinto.py` OK (48 esecuzioni).

Esecuzioni precedenti non salvate: 454/457 (i tre conflitti sopra), poi 456/457 («frasi obbligatorie
mancanti» in CLAUDE.md: tolta per errore la parola «indicato» da «la cartella del libro indicato»;
ripristinata con l'ok dell'autore).

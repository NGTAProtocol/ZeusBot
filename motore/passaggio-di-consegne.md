# Passaggio di consegne: motore

Frase di apertura per la nuova chat: «Leggi motore/passaggio-di-consegne.md e riprendi da lì».

## Stato

- Ramo `motore` (unico ramo di lavoro sul motore), allineato a origin. Ultimo commit: quello di questo file
  (`git log -1`).
- Suite: **520/520 OK**, 0 saltate, con LanguageTool 6.8 (`ZB_LANGUAGETOOL`). Comando, dalla radice:
  `ZB_LANGUAGETOOL=<cartella>/lib python3 -B motore/zb prove` (a schermo solo le righe non OK; tabella intera
  in `/tmp/zb-prove-ultima.md`). Con `ZB_BANCA_VOCI` si aggiungono le prove sulla banca vera.
- Livello editoriale in `motore/editoriale/` (pacchetto dell'autore, 22 file, più riferimenti, glossario,
  modelli della struttura, agente `lettore-cieco`, `anti-ia/catalogo-it-esteso.md` e `formule.yaml`).
- Percorso cablato in `zb` e `fase.py`: struttura (gate sempre attivo) → documenti → pagina_campione →
  stesura → revisione_manoscritto → line → copy → bozze → chiusura.
- Cartella unica, recinto anche su Bash, separazione dei ruoli (blocco), anti-IA in audit in `zb esito`,
  LanguageTool installabile con `zb ortografia installa`, subagenti (`zb agenti`), capsule (`zb capsula`),
  output compatto, `zb consumo`.
- Rami d'archivio su origin: `archivio/motore-ritirati` (pulizia.py con prove e attesi),
  `archivio/motore-docs` (esportazioni precedenti di `docs/`, con la banca-voci integrale),
  `archivio/ghimoney`.
- Banca-voci: repository separato e privato, letto in sola lettura da `ZB_BANCA_VOCI`; gli slug delle voci
  stanno nel suo `indice.yaml`, non qui (alcuni contengono nomi reali).
- Analisi dei repository esterni: `docs/ANALISI_REPOSITORY.md`; attribuzioni: `docs/ATTRIBUZIONI.md`;
  cosa deve leggere l'autore: `docs/DA_VERIFICARE_AUTORE.md`.

## Decisioni prese

- Una sola scala di precedenza: `motore/editoriale/LEGGIMI.md`.
- Nessun documento o capitolo prima del gate `struttura`; i documenti nascono all'`ok` (nuovo.genera_documenti).
- Tutto il libro in `libri/<slug>/`; libro attivo in `<git-dir>/zb-libro-attivo` (non tracciato); eccezioni
  della cartella unica in `dati/cartella-unica.yaml`.
- Un ruolo per sessione, registrato da `zb avvio` in `<libro>/.zb/ruoli.yaml`; `separazione_ruoli: blocco`.
- Anti-IA: misure della sezione H in audit (avviso), soglie nel profilo di genere tarate sui mini-libri.
- Script: eliminato `pulizia.py`; tolti i comandi `conta`, `stile`, `riciclo`, `capitolo` (moduli di `esito`).
- Modelli degli agenti centralizzati in `dati/modelli-agenti.yaml` (vince il file di dati).
- `zb push` sul lavoro del motore vuole `zb prove` intera e tutta OK sullo stato attuale.

## Regole da non violare

- Regola madre: il motore resta sempre pulito; il ramo `motore` non contiene mai un libro.
- Nessun nome reale (autori, titoli, personaggi, luoghi, frasi, nomi di ramo dei libri) in codice, prove,
  commenti, esiti, report e documenti del ramo `motore`.
- Non toccare i rami dei libri (ognuno ha il suo `CLAUDE.md` per scelta dell'autore).
- Report di sessione ogni 5 scambi o a «passaggio»; sezioni fisse.
- Nessun push forzato sul ramo `motore`, nessuna riscrittura della storia.

## Fatto in questa sessione (2026-10-15)

Commit su `motore`: e258631 (editoriale), dce3774 (precedenza), ed77fd9 (risparmio-token e agenti),
170fc37 (percorso e struttura), a2d6b93 (cartella unica), 4363276 (ruoli), a728845 (anti-IA), 8960870
(correttore), 89d6d4e (agenti, capsule, consumo, output), 05fc414 e ff3b2e1 (script ritirati),
3d22ec0 (repository esterni), bb71252 (pulizia, README, PROCEDURA), più i commit dei documenti derivati.

## Punti aperti

1. Verifica KDP mai fatta (`dati/kdp.yaml`, `ultima_verifica: null`): passo manuale dell'autore.
2. Soglie anti-IA da rivedere su testi veri, genere per genere (oggi uguali per tutti).
3. Ramo «Maven Central» di `zb ortografia installa` provato prima del 429 di oggi; dopo, solo la cache locale.
4. `mwakidenis/Publish-Books` non accessibile: griglia a cinque assi e lettura a freddo non prese.
5. File da leggere e scelte da confermare: `docs/DA_VERIFICARE_AUTORE.md`.

## Prossimo passo

Primo libro sul nuovo percorso: briefing, `zb nuovo`, `zb hook attiva --ok` e `zb agenti attiva --ok` sul
ramo del libro (con l'ok dell'autore), poi la fase struttura.

## Ripartenza

```
pip install -r motore/requirements.txt
apt-get install -y hunspell hunspell-it poppler-utils
python3 motore/zb ortografia installa          # poi l'export che stampa
python3 motore/zb lavoro motore                # solo se l'autore ha scritto «lavoro sul motore»
python3 -B motore/zb prove
```

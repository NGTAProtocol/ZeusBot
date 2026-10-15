# Da verificare dall'autore

File e scelte che deve leggere l'autore prima di considerarli suoi. Lavoro del 2026-10-15 sul ramo `motore`.

## Passi manuali
1. **Verifica KDP mai fatta**: `motore/dati/kdp.yaml` ha `ultima_verifica: null`. Controllare a mano i sette
   valori sulle pagine ufficiali KDP (promemoria con `zb verifica KDP controlla`), poi
   `python3 motore/zb verifica KDP fatta AAAA-MM-GG`. Finché resta null, `zb kdp` lo segnala.
2. **LanguageTool nelle sessioni nuove**: `zb ortografia installa`, poi l'export che stampa (o la variabile
   `ZB_LANGUAGETOOL` nell'ambiente del cloud). Il ramo «scarico da Maven Central» è stato provato il
   2026-10-15 prima che Maven rispondesse 429; dopo le modifiche è stato provato solo il ramo «cache locale».

## File da leggere (tradotti o adattati, o nuovi)
- `motore/editoriale/anti-ia/catalogo-it-esteso.md` (sezioni J-P, adattate da repository inglesi) e
  `motore/editoriale/anti-ia/formule.yaml` (37 espressioni regolari contate da `zb esito`).
- `motore/editoriale/ruoli/riferimenti/critica-manoscritto.md`, `lettori-e-panel.md`, `continuita-e-serie.md`.
- `motore/editoriale/glossario.md`.
- `motore/editoriale/struttura/modelli/`: gli otto modelli nuovi (01-04, 06, 07, 09; il 05 e l'08 li genera
  `zb nuovo`), in particolare la sezione «Contratto della storia» di `01-premessa.md`.
- `motore/editoriale/agenti/lettore-cieco.md` (nuovo, passo opzionale) e `motore/dati/modelli-agenti.yaml`.

## Modifiche ai tuoi file (dove e perché)
- `ruoli/03-scrittore-voce.md`, «Input»: «capitolo precedente» → «le capsule dei capitoli precedenti e solo
  l'ultima pagina del capitolo precedente», come nel tuo agente `scrittore-voce.md` e nel punto 15c.
- `ruoli/01, 04, 05, 06`: aggiunta in fondo una sezione «Riferimenti (letti solo quando servono)».
- `agenti/editor-strutturale.md`: una frase che rimanda a `critica-manoscritto.md`.
- `anti-ia/catalogo-it.md`: solo un rimando in fondo (sezioni A-I invariate).
- `LEGGIMI.md` dell'editoriale: elenco del contenuto aggiornato con i file nuovi.

## Da decidere
- `correttore/criteri-correttore.md`, sezione 5: la coppia «avvenire/avvenire» è ripetuta (probabile
  refuso: forse «eminente/imminente» o altra coppia). Lasciata com'è, come nel tuo pacchetto.
- `struttura/modelli/scaletta-capitolo.md`: «Promesse aperte / chiuse»; il glossario usa «pagate». Lasciato.
- Soglie anti-IA (campo `anti_ia` dei sette profili): PROPOSTA tarata solo sui due mini-libri di prova,
  uguale per tutti i generi; modalità avviso. Da rivedere su testi veri, genere per genere.
- Ripetizioni ravvicinate (finestra 60 parole piene, 3 occorrenze, massimo 12 gruppi ogni mille parole):
  algoritmo nostro, il repository indicato non lo conteneva.
- `dati/hook.yaml`: `separazione_ruoli: blocco` (scelta mia); `avviso` se preferisci.
- `capsule: obbligatorie` per i libri nuovi; i libri già esistenti senza il campo hanno solo un avviso.
- Modelli degli agenti: lasciati i tuoi valori (forte per architetto ed editor strutturale, medio per gli
  altri, leggero per la capsula). La prova di copyediting italiano con il modello leggero non è stata
  fatta: il copyediting usa già il modello medio, il leggero fa solo le capsule.
- `mwakidenis/Publish-Books` non è accessibile: griglia a cinque assi e lettura a freddo non prese.

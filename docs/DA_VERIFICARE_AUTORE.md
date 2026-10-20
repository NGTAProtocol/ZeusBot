# Da verificare dall'autore

File e scelte che l'autore deve leggere prima di considerarli suoi. Integrazione del 2026-10-20 sul ramo
`integrazione-editoriale` (base: pacchetto da 28 file; aggiunte da `motore`). Le scelte prese in automatico, con il
perché, stanno in `docs/DECISIONI_INTEGRAZIONE.md`.

## Aggiunte da `motore`, adattate ai nomi del pacchetto da 28 file (punto 2)
| File | Adattamento |
|---|---|
| `motore/editoriale/glossario.md` | glossario inglese-italiano; rimando a `lingue/it/glossario-editoriale.md` (significato dei termini) |
| `motore/editoriale/anti-ia/catalogo-it-esteso.md` | sezioni J-P; lo script è `script/antiia.py` (misura `formule_catalogo_per_mille`) |
| `motore/editoriale/anti-ia/formule.yaml` | 37 espressioni; lette da `script/antiia.py`; soglia `formule_catalogo_per_mille_max` (3,0; le 11 della sezione B contano solo con `formule_sezione_b: true`) |
| `motore/editoriale/agenti/lettore-cieco.md` | invariato; livello del modello in `dati/modelli-ruoli.yaml` (medio) |
| `motore/editoriale/ruoli/riferimenti/critica-manoscritto.md` | riferimento del diagnosta e dell'editor strutturale; rapporto in `06-diagnostica/rapporto-manoscritto.md`, proposte nel `piano-revisione-manoscritto.md`; colonna «Classe di intervento» al posto di «Proposta» (il diagnosta non propone) |
| `motore/editoriale/ruoli/riferimenti/lettori-e-panel.md` | invariato |
| `motore/editoriale/ruoli/riferimenti/continuita-e-serie.md` | invariato |
| `motore/editoriale/struttura/modelli/01-premessa.md` | invariato (sezione «Contratto della storia», idea di robskidmore/fiction-skills, MIT) |
| `motore/editoriale/struttura/modelli/02-logline-tema.md` | invariato |
| `motore/editoriale/struttura/modelli/03-personaggi-chiave.md` | invariato |
| `motore/editoriale/struttura/modelli/04-atti-svolte.md` | titolo «Macrostruttura e svolte»; righe `Macrostruttura:` e `Motivo:` e tabella delle svolte (le controlla `zb pronto`); niente «Atto I/II/III» fissi |
| `motore/editoriale/struttura/modelli/06-sottotrame-temi.md` | colonne del pacchetto: «Sottotrama o promessa · Si apre · Si sviluppa · Si chiude» |
| `motore/editoriale/struttura/modelli/07-tensione-ritmo.md` | colonne unite: «Cap. · Tensione (1-10) · Azione o reazione · Respiro voluto? (dove e perché)» |
| `motore/editoriale/struttura/modelli/09-scelte-fisse.md` | nota: dopo la fase struttura non si cambiano (`zb avvio` si ferma) |

- I ruoli del pacchetto (28 file, non toccati) non rimandano ai tre file di `ruoli/riferimenti/`: li richiamano
  l'agente `lettore-cieco` e questo elenco. Se vuoi il rimando nei ruoli, va aggiunto ai tuoi file.

## Contrasto tra il pacchetto e il modo automatico (segnalato, non corretto)
- I 28 file descrivono fermate con l'«ok» dell'autore (`00-percorso.md`, `struttura/01-fase-struttura.md`,
  «solo dopo il mio ok» nei ruoli). Dal 2026-10-20 il motore scrive in automatico, con una sola pausa di lettura
  (decisione D4). Se vuoi, aggiorna il pacchetto.
- `CLAUDE.md`: risolto (D17). Ora descrive `--ruolo` (un ruolo per sessione) e il modo automatico con la pausa di
  lettura; il «Metodo» resta, come la regola 3 di PROCEDURA.

## Incoerenze nei 28 file del pacchetto: risolte (D18, con la tua autorizzazione)
- `editoriale/LEGGIMI.md` riga 13: ora «dodici subagenti» in `agenti/` (10) e `lingue/agenti/` (2), come
  `zb agenti stato`.
- Lunghezza della capsula: `agenti/capsula.md` e `risparmio-token.md` ora dicono 120-250 parole (circa 180), come
  `script/capsula.py`; allineati anche i due glossari di `lingue/` e `dati/struttura-libro.yaml`.

## Decisioni tue ancora aperte (non toccate)
- Coppia «avvenire/avvenire» in `correttore/criteri-correttore.md`, sezione 5.
- Sezione B del catalogo anti-IA.
- Licenza di APODICTIC (CC BY-NC-SA 4.0): nessun testo copiato.
- Verifica dei dati KDP: `motore/dati/kdp.yaml`, `ultima_verifica: null`; la registri tu con
  `python3 motore/zb verifica KDP fatta AAAA-MM-GG`.

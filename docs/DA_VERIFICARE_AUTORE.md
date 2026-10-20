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
- `CLAUDE.md` (non toccato: è il tuo foglio delle regole): dice ancora «Metodo: proponi → l'autore approva → applica» e
  la riga di avvio non ha `--ruolo` (un ruolo per sessione, D8). Il motore segue il modo automatico; se vuoi, aggiorna
  `CLAUDE.md` (massimo 30 righe, lo controlla una prova).

## Incoerenze nei 28 file del pacchetto (segnalate, non corrette)
- `editoriale/LEGGIMI.md` riga 13: «nove subagenti»; in `editoriale/agenti/` i file sono 10 (con `lettore-cieco`,
  aggiunto da `motore`), più 2 in `lingue/agenti/`; `zb agenti stato` ne conta 12.
- Lunghezza della capsula: `agenti/capsula.md` dice «massimo 180 parole», `risparmio-token.md` «circa 150-180»; il
  motore (`script/capsula.py`) accetta 120-250 (D9). Il glossario aggiunto da `motore` ora dice 120-250.

## Decisioni tue ancora aperte (non toccate)
- Coppia «avvenire/avvenire» in `correttore/criteri-correttore.md`, sezione 5.
- Sezione B del catalogo anti-IA.
- Licenza di APODICTIC (CC BY-NC-SA 4.0): nessun testo copiato.
- Verifica dei dati KDP: `motore/dati/kdp.yaml`, `ultima_verifica: null`; la registri tu con
  `python3 motore/zb verifica KDP fatta AAAA-MM-GG`.

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

## Profilo thriller: valori segnati PROPOSTA o senza fonte (2026-10-21, elencati, non cambiati)
Righe di `motore/profili/thriller.yaml`. Fonte dichiarata in testa al file: righe dei riferimenti di
casa-editrice `main` @ becd0e2; i valori qui sotto non hanno una riga di quei riferimenti.

| Riga | Campo | Valore | Perché è proposta (dal commento del file) |
|---|---|---|---|
| 27 | `frase_media` | [9, 14] | il riferimento (03 r. 10) dà solo la regola «brevi nell'azione», non un intervallo |
| 28 | `frase_media_voce` | true | decisione dell'autore del 2026-10-21, ma segnata ancora PROPOSTA (vedi sotto) |
| 29 | `dialogo_percento` | [25, 45] | nessuna fonte |
| 30 | `similitudini_max_per_parole` | 400 | nessuna fonte |
| 31 | `parole_filtro.massimo_per_1000_parole` | 8 | l'elenco viene da 05 r. 21; il numero no |
| 33 | `anti_ia.modalita` | avviso | uguale per tutti i generi |
| 34 | `anti_ia.variazione_frasi_min` | 0.25 | come `dati/antiia.yaml`, tarato sui mini-libri |
| 35 | `anti_ia.aperture_uguali_max` | 20 | come `dati/antiia.yaml` |
| 36 | `anti_ia.formule_per_mille_max` | 1.0 | come `dati/antiia.yaml` |
| 37 | `anti_ia.formule_catalogo_per_mille_max` | 3.0 | mini-libri 0,0-0,6 |
| 38 | `anti_ia.ripetizioni_per_mille_max` | 12.0 | mini-libri 2,2-9,7 |
| 39 | `anti_ia.chiusure_uguali_max` | 2 | nessuna fonte |
| 41 | `parole_per_pagina` | 250 | il riferimento (12 r. 7) dà 250-300; scelto il minimo |
| 48 | `scene_obbligatorie` | «confronto finale tra protagonista e antagonista» | nessuna fonte |
| 49 | `scene_obbligatorie` | «scadenza o corsa contro il tempo» | nessuna fonte |

## Scelte con due valori, da decidere (2026-10-21)
- Significato di «PROPOSTA» nei profili. `motore/profili/thriller.yaml` riga 2: «PROPOSTA = valore approvato
  dall'autore»; riga 28: «PROPOSTA (decisione dell'autore, 2026-10-21)»; `docs/GUIDA_AL_SISTEMA.md` («Le soglie
  anti-IA dei profili sono una PROPOSTA»), dove vuol dire «valore da confermare». Due letture: valore proposto e già
  approvato, oppure valore ancora da approvare.
- Gruppi di divieti nella voce della prova. `docs/PROPOSTE_MOTORE.md` (P1): «La voce della prova non usa ancora i
  gruppi»; resoconto dell'autore: la voce nuova ha il gruppo «chiuse». La banca-voci non era disponibile in questa
  sessione: non verificato, frase non cambiata.
- Frase media e dialogo del thriller contro quelli della voce. Profilo: `frase_media` [9, 14], `dialogo_percento`
  [25, 45]; con `frase_media_voce: true` per la frase media vale la voce, per il dialogo resta il profilo
  (`script/stile.py`, KO fuori da [25, 45]). I valori della scheda della voce non sono stati letti (banca-voci non
  disponibile): il confronto è da fare.

## Revisione del capitolo: scelte da confermare (2026-10-21, quarta parte)
- Quali avvisi fermano la chiamata al diagnosta (`script/percorso.py`, `bloccanti_prima_della_revisione`): **decisione
  presa dall'autore il 2026-10-21**: solo i KO e gli avvisi dei divieti della voce. Motivo: le soglie delle ripetizioni
  (`ripetizioni_per_mille_max` 12,0) e l'intervallo della frase media del registro sono ancora PROPOSTA o «non calibrato
  sull'autore». Frase media e ripetizioni ravvicinate restano avvisi: con gli altri avvisi (lista nera di base, budget
  di parole, scene, altre misure anti-IA) compaiono tra le righe misurate di `06-diagnostica/misure/NN.md` e passano al
  diagnosta, senza fermare.
- Modello del diagnosta: haiku (`leggero` in `dati/modelli-ruoli.yaml`) è **da provare su una pagina: se la revisione
  risulta debole, tornare al modello medio** (sonnet, una riga del file). Un livello vale per agente, non per lavoro:
  vale anche per la diagnosi della struttura e del manoscritto (`rapporto-*.md`), che prima era su opus.

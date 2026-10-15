# Gravità e formato del rapporto

Scritto da zero per questo motore.

## Tre gravità
| Gravità | Significato | Effetto sul gate |
|---|---|---|
| **G1 bloccante** | rompe il contratto o la logica del libro (finale che non risponde, svolta senza causa, punto di vista violato) | il piano di revisione deve risolverla prima di procedere |
| **G2 seria** | indebolisce il libro in modo visibile (sottotrama orfana, tratto piatto lungo, personaggio senza scopo) | il piano la affronta o motiva perché no |
| **G3 minore** | migliorabile, non necessaria (ordine di due scene, una ripetizione di funzione) | l'autore decide |

Le gravità anti-IA P0/P1/P2 (catalogo anti-IA) sono un'altra scala, solo per la prosa.

## Formato del rapporto (`06-diagnostica/diagnosi-<struttura|manoscritto>.md`)
Prima riga, obbligatoria (la controlla `zb pronto`):
`<!-- zb: ruolo=diagnosta; su=<impronta> -->` dove `<impronta>` è quella stampata da `zb ruolo <libro> diagnosta`.

Sezioni, in quest'ordine:
1. `## Contratto` (sette righe)
2. `## Sintesi`
3. `## Analisi` (i dieci passaggi, poche righe ciascuno)
4. `## Problemi` (tabella: n., gravità, dove, problema, perché)
5. `## Cosa non toccare` (ciò che funziona e va protetto)

Regole: ogni problema ha il rimando; nessun brano incollato oltre le cinque parole; nessuna proposta di
riscrittura (le proposte le fa l'editor strutturale nel piano di revisione).

## Piano di revisione (editor strutturale)
`06-diagnostica/revisione-<struttura|manoscritto>.md`, prima riga
`<!-- zb: ruolo=editor-strutturale; su=<impronta> -->`, con la sezione obbligatoria
`## Piano di revisione`: una riga per intervento (n., problema del rapporto, intervento, file o
capitolo, chi lo applica). Al gate l'autore approva o corregge il piano; dopo l'«ok» il piano si applica.

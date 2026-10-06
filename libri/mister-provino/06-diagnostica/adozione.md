# Adozione — (titolo non ricavato)

Bozze generate da `zb adotta`. Niente è approvato: si approva al gate «documenti».

Documenti letti: 00-progetto/briefing.md, 03-architettura/manuale-di-stile.md, 02-bibbia/bibbia.md, 03-architettura/scaletta.md, 03-architettura/piano-parole.md, cronologia.yaml.
File scritti: stato.yaml.
File già presenti, non toccati: libro.yaml, cronologia.yaml, nomi_propri.txt.
libro.yaml valido: sì.

## Valori e fonti

| Campo | Valore | Fonte (file:riga) |
|---|---|---|
| parole.target_totale | 78000 | 03-architettura/piano-parole.md:62 |
| modalita | riscrittura | 01-originale/ (cartella presente) |
| stile.similitudini_max_per_parole | 300 | 03-architettura/manuale-di-stile.md:126 |
| stile.capitoli.media | [10, 13] | 03-architettura/manuale-di-stile.md:35 |
| stile.capitoli.massimo | 150 | 03-architettura/manuale-di-stile.md:92 |

## Override rispetto al profilo

- nessuno

## Non ricavato (da completare a mano)

- titolo
- autore
- profilo
- struttura.separatore_scena
- struttura.intestazione_capitolo
- dichiarazioni.chiusura (serve il profilo)
- formato (predefinito 5.5 x 8.5: da confermare)
- copyright.fantasia (testo standard: da confermare)
- calendario.anni_ammessi (nessuna data in scaletta)

## Prossimo passo

Gate «documenti» aperto: avanti, ok o correggi.

## Completato a mano (dopo «zb adotta»)

I documenti di questo libro non sono nel formato che `zb adotta` riconosce (titoli «# Mister Provino — …», valori scritti in prosa). Le bozze `libro.yaml`, `cronologia.yaml` e `nomi_propri.txt` sono state completate a mano: in `libro.yaml` e `cronologia.yaml` ogni valore ha la fonte (file:riga) nel commento della sua riga.

Due righe della tabella qui sopra vengono da riconoscimenti sbagliati e **non** sono entrate in `libro.yaml`:
- «stile.capitoli.media [10, 13]» (manuale:35) è la frase media, non la media dei capitoli: in `libro.yaml` è `frase_media: [10, 13]`;
- «stile.capitoli.massimo 150» (manuale:92) è il massimo di un ponte di riassunto: in `libro.yaml` il massimo dei capitoli è 3.000 (scaletta:349).

`03-architettura/piano-parole.md` è ricavato 1:1 dalla scaletta (tabella delle parole), senza valori nuovi.

### Ancora da completare
- autore (nessun documento lo nomina; in `libro.yaml` c'è «DA COMPLETARE»);
- sottotitolo, serie;
- struttura.intestazione_capitolo (predefinito del motore; il manuale dice solo che nessun capitolo si apre con una data, M:96);
- formato e copyright (predefiniti del motore, da confermare);
- capitoli.tolleranza_totale (il manuale non la dice: resta quella del profilo, ±5%);
- cifre della cronologia (lo zaino cambia scena per scena: controllo a mano, bibbia §5.7);
- nascite con la data completa solo per Beniamino e Checco (gli altri hanno solo l'anno).

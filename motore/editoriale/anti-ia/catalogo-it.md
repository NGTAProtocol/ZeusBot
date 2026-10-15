# Catalogo anti-IA per l'italiano

Scritto da zero per questo motore. Lo scrittore lo applica mentre scrive; il line editor lo usa per
diagnosticare; `zb esito` ne misura gli elementi misurabili (`motore/script/antiia.py`, modalità audit:
non riscrive nulla). È un filtro di qualità: **non sta sopra** il manuale del libro, la voce e il
briefing (scala in `../LEGGIMI.md`). Una scelta documentata nel manuale vince sul catalogo.

## 0. Vocabolario: livelli (vuoti finché non ci sono i dati)
Il vocabolario italiano non si inventa. I tre livelli restano vuoti finché non viene estratto dai dati
con `zb antiia estrai` (parole e formule più frequenti in testi scritti da un modello, confrontate con
prosa italiana scritta da persone; corpus da fornire, vedi `docs/DA_FORNIRE.md`).
| Livello | Trattamento | Voci |
|---|---|---|
| L1 da sostituire sempre | ogni occorrenza è P1 | nessuna (in attesa dei dati) |
| L2 da segnalare in gruppo | P2 se due o più compaiono nello stesso paragrafo | nessuna |
| L3 da segnalare per densità | P2 sopra la soglia per mille parole | nessuna |
I dati estratti vanno in `motore/dati/antiia-it.yaml` (campo `vocabolario`), con fonte e data.
Restano attive, separate da questo catalogo, la lista nera di base (`motore/dati/lista-nera.yaml`) e
le voci del libro.

## Gravità
| Gravità | Significato |
|---|---|
| P0 | rompe la lettura o la voce (capitolo che chiude come il precedente per la terza volta, dialogo che spiega il sottotesto); si corregge |
| P1 | schema evidente e ripetuto; si corregge salvo scelta documentata |
| P2 | da guardare; si corregge solo se il passo migliora |

## Profili per tipo di testo
| Profilo | Si applica a | Schemi pesati di più |
|---|---|---|
| narrativa | prosa narrativa fuori dal dialogo | A, C, E |
| dialogo | righe di discorso diretto | D (le misure di ritmo A non si applicano: il parlato è irregolare) |

## A. Ritmo (misurato)
1. Frasi di lunghezza simile: deviazione della lunghezza delle frasi bassa rispetto alla media
   (misura `variazione_frasi`).
2. Paragrafi tutti della stessa lunghezza.
3. Aperture uguali: frasi o paragrafi vicini che cominciano con la stessa parola (misura `aperture_uguali`).
4. Elenco ternario a ogni paragrafo come cadenza fissa.
5. Struttura correttiva ripetuta (negazione di un termine seguita dal termine «vero») più di una volta
   per capitolo.
Cosa fare: alternare per emozione, non per regola.

## B. Astrazione al posto del fatto
Schema: un'emozione o un'atmosfera nominata in astratto dove la scena potrebbe mostrare un fatto
percepibile (cosa fa la mano, cosa sente l'orecchio, cosa manca nella stanza). Si riconosce dal
sostantivo astratto seguito da una specificazione vaga. Cosa fare: sostituire con un fatto.

## C. Spiegare ciò che si è già mostrato
- Dopo un gesto, la frase che ne dichiara il significato.
- Battuta seguita da un verbo dichiarativo con avverbio o complemento di modo che ripete il tono.
- Pensiero che ripete il dialogo appena avvenuto.
- Chiusura di paragrafo che riassume ciò che il paragrafo ha mostrato.
Cosa fare: tagliare la spiegazione; se il lettore non capisce, cambiare il gesto, non aggiungere la glossa.

## D. Dialogo troppo esplicito
- Personaggi che parlano tutti con lo stesso registro.
- Battute che dicono esattamente ciò che provano.
- Tutti rispondono alla domanda posta; nessuna interruzione, nessuna risposta laterale.
- Convenevoli che non servono alla scena.
Cosa fare: sottotesto (dalla scheda del capitolo), interruzioni, silenzi, lessico diverso per personaggio.

## E. Aperture e chiusure
- Capitoli che iniziano con meteo, risveglio o descrizione generica del luogo.
- Capitoli consecutivi che chiudono nello stesso modo (stessa sigla di chiusura, stessa forma della
  frase finale; misura `chiusure_uguali`).
- Gancio sempre dello stesso tipo.
Cosa fare: entrare in scena a cose iniziate; variare la chiusura (azione, immagine, battuta).

## F. Uniformità del registro
Tono letterario uniforme anche dove il personaggio non lo sarebbe; termini astratti al posto delle
cose; la stessa decina di parole «eleganti» in ogni capitolo (si misura solo con i dati, livello L3).

## G. Insidie per tipo di opera
| Opera | Insidia tipica |
|---|---|
| giallo, thriller | indizi spiegati appena posati; detective che riassume il caso a ogni capitolo |
| romance | emozioni dichiarate invece che mostrate nei gesti; dialoghi di chiarimento che chiudono il conflitto troppo presto |
| fantasy, fantascienza | spiegazione del mondo in blocchi; nomi inventati tutti con lo stesso suono |
| narrativa letteraria | chiusure epifaniche a ogni capitolo; metafore in serie |
| young adult | voce adulta che spiega i sentimenti del ragazzo |

## H. Cosa non si tocca
Ambiguità volute, omissioni, ripetizioni volute, frasi sbilenche della voce: se sono nel manuale o nella
scheda della voce restano. Il catalogo non cancella la voce per uniformarla.

## I. Imperfezioni naturali credibili (dosate)
Ammesse, con misura: frase sbilenca perché così pensa il personaggio; ripetizione voluta; periodo
spezzato; omissione del soggetto; parola dialettale o gergale coerente con la voce; dettaglio lasciato
senza spiegazione. Vietate: errori di ortografia o grammatica veri. Tetto: circa una ogni 800-1000
parole, mai più di tre per pagina.

## L. Misure di `zb esito` (modalità audit)
| Misura | Cosa conta | Soglia (dati/antiia.yaml) |
|---|---|---|
| `variazione_frasi` | deviazione standard / media della lunghezza delle frasi di prosa | sotto la soglia: P1 |
| `aperture_uguali` | percentuale di frasi consecutive con la stessa prima parola | sopra la soglia: P2 |
| `formule_per_mille` | occorrenze delle voci L1-L3 e della lista nera per mille parole | sopra la soglia: P2 |
| `chiusure_uguali` | capitoli consecutivi con la stessa sigla di chiusura e frase finale della stessa forma | tre di fila: P0, due: P2 |
Le soglie sono tarate sui mini-libri di prova; il report va in `06-diagnostica/anti-ia/NN.md`.

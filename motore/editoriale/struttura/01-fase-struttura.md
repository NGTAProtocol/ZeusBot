# Fase STRUTTURA

Prima fase dopo il briefing e l'apertura della cartella del libro. Nessun documento, nessuna pagina di
prosa prima che il gate `struttura` sia approvato (`fase.py` lo impedisce).

## Ruolo
Architetto della struttura (`ruoli/02-architetto-struttura.md`).

## Input
`00-progetto/briefing.md`, `libro.yaml`, profilo di genere, scheda della voce (se c'è).

## Output in `03-struttura/` del libro
`zb nuovo` crea i nove file con la riga `<!-- zb: modello -->`; l'architetto la toglie quando il file è
scritto (`zb pronto` rifiuta i file che la contengono ancora).
1. `01-premessa.md` - premessa e promessa al lettore, una pagina: chi è il lettore, cosa gli promette il
   libro, perché lo finirà.
2. `02-logline-tema.md` - logline in una frase; tema centrale e controtema.
3. `03-personaggi-chiave.md` - protagonista, antagonista (o forza antagonista), posta in gioco, ferita
   o mancanza, desiderio e bisogno, arco di trasformazione.
4. `04-atti-svolte.md` - macrostruttura scelta e motivata (vedi sotto), svolte e dove cadono.
5. `05-scaletta.md` - in testa la tabella `| Unità | Data | Contenuto | Chiusura |` (la leggono gli
   script), poi un blocco per capitolo (`modelli/scaletta-capitolo.md`).
6. `06-sottotrame-promesse.md` - dove ogni sottotrama e promessa si apre, si sviluppa, si chiude.
7. `07-tensione-ritmo.md` - curva di tensione capitolo per capitolo; dove si respira.
8. `08-piano-parole.md` - tabella con le colonne `Cap.` e `Budget capitolo` (la leggono gli script):
   budget diversi secondo la funzione, non divisi in parti uguali.
9. `09-scelte-fisse.md` - punto di vista, tempo verbale, voce: fissati prima della prosa.

## Macrostrutture ammesse (varietà strutturale)
L'architetto ne sceglie una e scrive in `04-atti-svolte.md` perché questa storia la chiede.
| Macrostruttura | Quando serve |
|---|---|
| 3 atti | conflitto unico che cresce fino a una resa dei conti |
| 4 atti | storia con un rovesciamento al centro che cambia il senso della prima metà |
| 5 atti | ascesa e caduta, tragedia, più svolte di pari peso |
| dittico | due metà speculari (prima/dopo, due punti di vista, due tempi) |
| in medias res | si apre nel pieno dell'azione e il passato si recupera dopo |
| mosaico | più fili o voci che si compongono solo alla fine |
| slow-burn | tensione che cresce per accumulo lento, svolta tardi |
| circolare | il finale torna all'immagine o al luogo d'inizio, cambiato |
Regole: le svolte non stanno sui quarti esatti per regola; numero e lunghezza dei capitoli nascono dal
contenuto; niente etichette automatiche «Atto 1/2/3». `zb esito` segnala capitoli di lunghezza quasi
uguale (misura in `capitolo.py`, controllo `lunghezze_uguali`).

## Controlli prima del gate (li fa `zb pronto`, il resto il diagnosta)
- nove file presenti e senza `<!-- zb: modello -->`;
- ogni scheda di capitolo ha funzione, conflitto, cambiamento, informazione data, gancio, polarità
  emotiva, sottotesto (`zb prepara` lo ricontrolla prima di ogni capitolo);
- `06-diagnostica/diagnosi-struttura.md` (diagnosta) e `06-diagnostica/revisione-struttura.md`
  (editor strutturale, con `## Piano di revisione`) presenti, scritti sulla struttura attuale e salvati
  in un commit che non tocca `03-struttura/` (separazione tra chi scrive e chi rivede).

## Gate `struttura`
L'autore legge struttura, diagnosi e piano: `avanti`, `ok` o `correggi: …`. Con `correggi`,
l'architetto applica solo le correzioni richieste. Dopo l'«ok» la struttura è approvata (sha256 e commit
in `stato.yaml`) e si passa ai documenti.

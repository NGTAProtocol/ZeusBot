# Ruolo 0 - Diagnosta editoriale

## Scopo
Leggere un testo (struttura, capitolo o manoscritto) e dire cosa fa, cosa promette e dove non funziona, senza riscrivere.

## Input
`motore/editoriale/diagnosi/` (principi, contratto, passaggi, gravità), briefing, `libro.yaml`, profilo di genere; per la struttura `03-struttura/`; per il manoscritto capsule e, solo dove serve, i capitoli segnalati.

## Output
`06-diagnostica/contratto.md` e `06-diagnostica/rapporto-<ambito>.md` (ambito: `struttura`, `manoscritto`; per un
capitolo fuori dai gate `audit/NN.md`) nel formato di `diagnosi/03-gravita-e-rapporto.md`, con la prima riga data da
`zb ruolo <libro> diagnosta`.

## Capitolo singolo (`06-diagnostica/audit/NN.md`)
Revisione di un capitolo appena scritto, prima che sia accettato, in sessione separata da chi lo ha scritto. Prima
riga: `zb ruolo <libro> diagnosta N` (in fase «stesura» solo con N), che prima misura il capitolo: con un KO, o un
avviso di frase media, divieti della voce o ripetizioni ravvicinate, si ferma e la revisione non comincia; con le misure
superate scrive `06-diagnostica/misure/NN.md` (righe misurate: non si rifanno) e `06-diagnostica/frasi-finali/NN.md`.
Input: il capitolo, `06-diagnostica/misure/NN.md`, `06-diagnostica/frasi-finali/NN.md`, la scheda della voce (sezioni 2, 3 e 6: regole, misure ed
esempi «debole → forte»), i file di `06-diagnostica/preparazione/NN.md` (codex filtrato, canone, capsule) e la
capsula del capitolo precedente. Checklist, in quest'ordine; per ogni punto si elencano le frasi trovate (riga e
testo) e il loro numero, anche quando è zero:
1. **Chiuse a sentenza, per funzione — tabella frase per frase.** Una riga per ogni frase di
   `frasi-finali/NN.md`: `| Riga | Frase | Chiusa? (sì/no) | Perché |`. «Sì» quando la frase commenta o
   riassume la scena invece di mostrarla (massima, giudizio, bilancio, approvazione): tolta la frase, il paragrafo
   dice ancora tutto. Un riassunto del narratore conta come chiusa. Conta la funzione, non le parole. Sotto la
   tabella: numero dei «sì» e, se superano il limite, quali togliere.
2. **Eco:** battuta che riprende una parola piena (nome, verbo, aggettivo, avverbio) dalla battuta precedente
   dell'altro personaggio, anche senza «ripeté»; non contano i nomi propri usati per chiamare qualcuno.
3. **Etichette dei personaggi senza nome:** per ogni scena e ogni persona, le etichette usate e quante volte.
4. **Soggetto:** (a) frasi in cui, con due persone dello stesso genere in scena, «lui», «lo», «gli» o un verbo
   senza soggetto possono riferirsi a tutte e due, anche nei fatti riferiti in un dialogo; (b) nome proprio
   ripetuto come soggetto dove il soggetto è ovvio (stessa persona della frase prima, nessun'altra persona dello
   stesso genere in mezzo, nessuna battuta di dialogo in mezzo): righe e numero.
5. **Battute giustificative:** battuta che spiega o giustifica ciò che il personaggio dice, fa o pensa (motivo
   dichiarato, «mi sembra chiaro», «se posso», «non si preoccupi», conferma di ciò che l'altro ha appena detto)
   invece di lasciarlo nel sottotesto. Conta la funzione: la versione forte è la battuta secca della sezione 6
   della voce.
6. **Registro corto** (scene d'azione): frasi oltre la misura massima della voce; frasi corte unite con «e»,
   «mentre» o virgole per alzare la media.
7. **Continuità:** i fatti che il capitolo riprende, confrontati con il codex e con la capsula del capitolo
   precedente (fatto, fonte, esito).

Esito, nell'ultima riga: «passa» o «non passa». Non passa con: più chiuse a sentenza del limite della voce
(una per capitolo se la voce non ne dà un altro), con l'elenco di quelle da togliere; un'eco; una battuta
giustificativa; più di due etichette per la stessa persona nella stessa scena; un soggetto ambiguo che può
cambiare un fatto; una frase del registro corto oltre la misura o unita per alzare la media; un fatto
contraddetto. Le soglie scritte nella scheda della voce prevalgono su queste (scala di precedenza). Si elencano le
frasi, non si riscrivono: la correzione la fa chi scrive, con una sola correzione mirata, poi una nuova revisione.
Con `revisione_capitolo: obbligatoria` in `libro.yaml`, `zb esito` legge l'ultima riga e l'impronta della prima.

## Cosa NON fa
Non riscrive, non propone frasi o scene, non lavora nella stessa sessione di chi ha scritto, non modifica i file del libro oltre ai suoi rapporti.

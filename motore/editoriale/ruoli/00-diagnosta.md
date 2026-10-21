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
Revisione di un capitolo appena scritto, prima che sia accettato, in sessione separata da chi lo ha scritto.
Input: il capitolo, la scheda della voce, i file di `06-diagnostica/preparazione/NN.md` (codex filtrato,
canone, capsule) e la capsula del capitolo precedente. Checklist, in quest'ordine; per ogni punto si
elencano le frasi trovate (riga e testo) e il loro numero, anche quando è zero:
1. **Chiuse a sentenza, per funzione:** frase finale di un paragrafo, o battuta che chiude uno scambio, che
   commenta o riassume la scena invece di mostrarla (massima, giudizio, bilancio, approvazione). Prova: tolta
   la frase, il paragrafo dice ancora tutto. Un riassunto del narratore conta come chiusa. Conta la funzione,
   non le parole.
2. **Eco:** battuta che riprende una parola piena (nome, verbo, aggettivo, avverbio) dalla battuta precedente
   dell'altro personaggio, anche senza «ripeté»; non contano i nomi propri usati per chiamare qualcuno.
3. **Personaggi senza nome:** per ogni scena e ogni persona, le etichette usate e quante volte.
4. **Chi fa cosa:** frasi in cui, con due persone dello stesso genere in scena, «lui», «lo», «gli» o un
   verbo senza soggetto possono riferirsi a tutte e due; anche nei fatti riferiti in un dialogo.
5. **Registro corto** (scene d'azione): frasi oltre la misura massima della voce; frasi corte unite con «e»,
   «mentre» o virgole per alzare la media.
6. **Continuità:** i fatti che il capitolo riprende, confrontati con il codex e con la capsula del capitolo
   precedente (fatto, fonte, esito).

Esito, nell'ultima riga: «passa» o «non passa». Non passa con: più chiuse a sentenza del limite della voce
(una per capitolo se la voce non ne dà un altro), con l'elenco di quelle da togliere; un'eco; più di due
etichette per la stessa persona nella stessa scena; un soggetto ambiguo che può cambiare un fatto; una frase
del registro corto oltre la misura o unita per alzare la media; un fatto contraddetto. Le soglie scritte
nella scheda della voce prevalgono su queste (scala di precedenza). Si elencano le frasi, non si riscrivono:
la correzione la fa chi scrive, con una sola correzione mirata, poi una nuova revisione.
In fase «stesura» `zb ruolo <libro> diagnosta` non dà la prima riga (il ruolo lavora in «struttura» e
«struttura_manoscritto»): il rapporto lo dice nella prima riga e indica la versione rivista del capitolo
(sha256 del file); proposta di motore in `docs/PROPOSTE_MOTORE.md`.

## Cosa NON fa
Non riscrive, non propone frasi o scene, non lavora nella stessa sessione di chi ha scritto, non modifica i file del libro oltre ai suoi rapporti.

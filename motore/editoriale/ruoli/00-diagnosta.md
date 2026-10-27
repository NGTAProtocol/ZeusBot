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
Revisione letteraria di un capitolo appena scritto, prima che sia accettato, in sessione separata da chi lo ha
scritto. Prima riga: `zb ruolo <libro> diagnosta N`, che prima misura il capitolo: con un KO oggettivo (continuità,
canone, nomi, parole vietate, lunghezza minima) si ferma e la revisione non comincia; le soglie di stile (frase media,
dialogo, anti-IA, divieti della voce) sono informative e stanno tra le righe misurate di `06-diagnostica/misure/NN.md`.
Input: solo i file della sezione «File da leggere» di `misure/NN.md` (capitolo, misure, scheda della voce sezioni 2, 3
e 6, codex filtrato, capsula precedente; il canone è nello stesso file). Leggi il capitolo **una volta, come un editor**.

Scala tarata (non regalare voti): 6 = mestiere, una bozza competente ma generica (è il voto tipico di una prima
stesura); 7 = fa qualcosa che una bozza generica non farebbe; 8 = un editor la terrebbe con note minori; 9-10 = regge
il confronto con un capitolo pubblicato di un grande autore del genere (nominane uno, o non dare 9). Per ogni voce
citi il momento più debole: se non lo trovi, non hai letto con attenzione.

Rapporto breve (al massimo 400 parole), in quest'ordine:
1. `## Voti`: tabella `| Voce | Voto 1-10 | Momento più debole (r.N «citazione breve») |` con sette voci: tensione e
   ritmo; sottotesto e dialoghi; voce (fedeltà alla scheda); specificità e immagini; personaggi (motivazioni,
   coerenza); funzione (fa ciò che chiede la scheda del capitolo); pulizia (spiegare ciò che la scena ha già mostrato,
   chiuse a sentenza, eco, battute giustificative, soggetti ambigui, ripetizioni, elenchi di tre).
2. Riga `Media: X.X` (media delle sette voci, un decimale).
3. `## Continuità`: fatti che il capitolo riprende confrontati con codex, capsula e canone; ogni fatto contraddetto è
   bloccante. Se nessuno: `- nessun fatto contraddetto`.
4. `## Da correggere`: **al massimo 5 voci**, quelle che alzano di più il voto, `- r.N «frase»: motivo → cosa
   ottenere` (l'effetto, non la frase riscritta); oppure `- nessuna`.
5. `## Lezione`: una sola riga, `- …`: il difetto di questo capitolo che lo scrittore non deve ripetere nei prossimi,
   detto come regola (es. «non spiegare dopo una battuta ciò che la battuta ha già detto»); `- nessuna` se non c'è.
   `zb esito` la aggiunge a `06-diagnostica/lezioni.md`, che lo scrittore legge prima di ogni capitolo.
6. `## Registro dei difetti` (le classi del revisore di `motore/dati/difetti.yaml`; il cancello di `zb esito` le
   legge, e una riga assente vale «non verificabile», che ferma il capitolo):
   `- conoscenza_personaggio: OK` oppure `KO r.N «…»: chi sa o vede che cosa, e perché non poteva` (controlla per
   ogni personaggio presente che cosa sa e da dove: capsule precedenti, porte chiuse, chi c'era);
   `- inferenza_come_fatto: OK` oppure `KO r.N «…»: è una deduzione di chi narra, il documento non lo dice`;
   `- motivazione: OK` oppure `KO r.N «…»: la scelta non è motivata dai fatti noti` (avviso, non blocca).
7. `## Fatti da verificare`: ogni fatto controllabile che il capitolo afferma (medicina legale, chimica, tecnica,
   storia, citazioni e attribuzioni, date reali), una riga `- r.N «…»: tipo`; oppure `- nessuno`. `zb esito` li
   registra in `06-diagnostica/difetti/fatti.yaml` e il capitolo resta non approvato finché ognuno non è verificato
   su fonte o riscritto in forma generica (`zb difetti <libro> fatto <id> verificato --fonte …`).
8. Ultima riga: `passa` se la media è almeno la soglia di qualità (`soglia_qualita` in `libro.yaml`, predefinito 7.5)
   e nessun fatto è contraddetto; altrimenti `non passa`. `zb esito` ricontrolla media e soglia.

Le soglie scritte nella scheda della voce restano criteri di giudizio per la voce «pulizia», non conteggi da
riportare. Si elencano gli interventi, non si riscrive: la correzione la fa chi scrive, con una correzione mirata.
Un solo giro completo: il secondo (dopo la correzione) rivede solo le voci della sezione «Giro 2» di `misure/NN.md`,
ognuna «risolta» o «non risolta», poi una nuova riga `Media:` e l'ultima riga; il primo rapporto resta in
`audit/NN-giro1.md`. Dopo un secondo «non passa» decide l'autore.

## Manoscritto intero (`06-diagnostica/rapporto-manoscritto.md`)
Dopo la stesura, due letture in un solo rapporto, con le capsule come mappa e i capitoli aperti solo dove serve:
1. **Da critico** (come una recensione di giornale, 200-300 parole): che libro è, che cosa riesce, dove cede.
2. **Da professore di narrativa**: difetti concreti con capitolo e riga, ognuno con l'intervento che lo risolve
   (non la frase riscritta). Non sei obbligato a trovare difetti, ma nemmeno a essere indulgente.
3. **Panel di quattro lettori simulati** (editor, lettore forte del genere, scrittore, primo lettore), ognuno con le
   stesse domande: dove il libro perde slancio; se il finale è meritato; quale capitolo taglierebbe; quale scena
   manca; quale personaggio è più sottile; la scena migliore e la peggiore; se lo consiglierebbe.
   Le risposte su cui concordano almeno tre lettori su quattro sono le **priorità** della revisione e aprono la
   sezione «Priorità» del rapporto; l'editor strutturale parte da lì.

## Cosa NON fa
Non riscrive, non propone frasi o scene, non lavora nella stessa sessione di chi ha scritto, non modifica i file del libro oltre ai suoi rapporti.

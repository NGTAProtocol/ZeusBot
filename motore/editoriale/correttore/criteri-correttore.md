# Criteri del correttore di italiano

## 1. Accenti e apostrofi
- e/è: "e" congiunzione, "è" verbo; controllare "e'"/"è" scritti male.
- "perché", "poiché", "affinché" con accento acuto; "né" negazione; "sé" pronome, "se" congiunzione; "dà" verbo, "da" preposizione; "là/lì" avverbi, "la/li" articolo/pronome.
- "un po'" con apostrofo; "qual è" senza apostrofo; "po'", "pò" errato.
- "d'accordo", "dall'altro", elisioni coerenti; apostrofo davanti a vocale con articolo giusto (un'amica / un amico).

## 2. Accordi
- genere e numero tra soggetto, verbo, participio, aggettivo;
- participio con ausiliare avere e pronome atono ("l'ho vista");
- accordo con soggetti multipli e con nomi collettivi;
- concordanza in dialoghi con voci regionali: segnare nel manuale di stile le deviazioni volute.

## 3. Tempi e modi
- consecutio temporum: congiuntivo dopo "credo che", "sembra che", periodo ipotetico (se avessi saputo, sarei venuto);
- passato remoto e prossimo coerenti con la voce scelta;
- trapassato per ciò che precede il racconto;
- non cambiare tempo verbale narrativo senza ragione.

## 4. Punteggiatura e dialogo
- scegliere un solo sistema di dialogo nel libro (caporali «», virgolette alte, lineette) e usarlo ovunque;
- punto prima e dopo le battute secondo il sistema scelto;
- virgola mai tra soggetto e verbo; due punti e punto e virgola usati con scopo;
- puntini di sospensione sempre tre, spazi coerenti;
- trattini: lineetta (–) per incisi, trattino (-) per composti.

## 5. Parole vere al posto di altre
- affetto/effetto, accettare/eccepire, prescindere/presumere, avvenire/avvenire;
- "piuttosto che" non vale "oppure";
- "qual è", "tal quale", "quant'è";
- anglicismi inutili e calchi: segnalare, non correggere se la voce lo richiede.

## 6. Coerenza interna
- nomi propri scritti sempre allo stesso modo (`nomi_propri.txt`);
- maiuscole e minuscole (titoli, istituzioni, mesi e giorni minuscoli);
- numeri in lettere o cifre secondo un solo criterio;
- date, età, durate coerenti con `cronologia.yaml`.

## 7. Cosa può fare il motore e cosa no
- Hunspell: errori di ortografia di base e refusi (con dizionario italiano); non vede e/è, accordi, parole vere sbagliate.
- LanguageTool: grammatica e punteggiatura più fini, se installato e se `ZB_LANGUAGETOOL` è impostata.
- Lettura mirata (lista di controllo a ogni capitolo): accordi, tempi, parole vere, coerenza di stile.

## 8. Regola d'oro
Il copyediting non cambia lo stile: corregge errori. Ciò che è scelta stilistica documentata nel manuale della voce resta.

## 9. Passaggio operativo (per capitolo)
1. `zb ortografia <libro>`: si leggono solo le righe del capitolo nel report (livello a Hunspell, livello b
   LanguageTool se `ZB_LANGUAGETOOL` è impostata, checklist).
2. Lettura mirata in un passaggio per sezione (1-6), cercando la categoria: accenti ed e/è; accordi; tempi;
   punteggiatura del dialogo; ripetizioni a breve distanza; parole vere sbagliate; maiuscole e nomi (codex).
3. `06-diagnostica/copy/NN.md` (prima riga da `zb ruolo <libro> correttore-italiano N`): riga, errore, correzione,
   sezione dei criteri.
4. Dopo l'«ok» al gate `copy`: modifiche puntuali (Edit), poi `zb esito <libro> N`.

| Strumento | Trova | Non trova |
|---|---|---|
| Hunspell it_IT | parole inesistenti, refusi | e/è, accordi, parole vere sbagliate, punteggiatura |
| LanguageTool (it) | molte regole di grammatica e punteggiatura, alcune confusioni | contesto lungo, scelte della voce |
| `zb continuita` | date, età, durate, cifre, nomi in due grafie | il senso |
| lettura mirata | e/è, accordi complessi, tempi, parole vere, ripetizioni | — |


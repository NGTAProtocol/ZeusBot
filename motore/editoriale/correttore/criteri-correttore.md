# Criteri del correttore di italiano

Documento di criteri e passaggio operativo del ruolo `correttore-italiano`. Il copyediting corregge
errori, non cambia lo stile: ciò che è scelta documentata nel manuale della voce resta.

## 1. Accenti e apostrofi
- e/è: «e» congiunzione, «è» verbo; «E'» al posto di «È» è errore.
- perché, poiché, affinché, né, sé (pronome; «se stesso» o «sé stesso» con un solo criterio nel libro),
  dà/da, là/lì e la/li, sì/si.
- «un po'» con apostrofo; «qual è» senza apostrofo; «pò» errato.
- elisioni coerenti; un'amica / un amico.

## 2. Accordi
Genere e numero tra soggetto, verbo, participio, aggettivo; participio con «avere» e pronome atono
(«l'ho vista»); soggetti multipli e collettivi; deviazioni regionali volute segnate nel manuale.

## 3. Tempi e modi
Consecutio temporum; congiuntivo dopo verbi d'opinione; periodo ipotetico; passato remoto e prossimo
coerenti con `09-scelte-fisse.md`; trapassato per l'antefatto; nessun cambio di tempo narrativo senza
ragione.

## 4. Punteggiatura e dialogo
Un solo sistema di dialogo nel libro (caporali, virgolette alte o lineette) e coerente ovunque; punto e
virgola dentro o fuori secondo il sistema; mai virgola tra soggetto e verbo; puntini sempre tre;
lineetta per incisi, trattino per composti.

## 5. Ripetizioni
Stessa parola piena a breve distanza (stessa frase o frase successiva) se non voluta; stesso verbo
dichiarativo in battute vicine. Si segnala, non si sostituisce con un sinonimo ricercato.

## 6. Parole vere al posto di altre
Coppie confuse (affetto/effetto, eminente/imminente, prescindere/presumere); «piuttosto che» per
«oppure»; calchi e anglicismi inutili (segnalare, non correggere se la voce li vuole).

## 7. Maiuscole e nomi
Nomi propri sempre nella stessa grafia (`nomi_propri.txt`, codex); mesi e giorni minuscoli; titoli e
istituzioni con un solo criterio; numeri in lettere o in cifre con un solo criterio; date, età e durate
coerenti con `cronologia.yaml` (le controlla anche `zb continuita`).

## 8. Cosa fa il motore e cosa resta alla lettura
| Strumento | Fa | Non fa |
|---|---|---|
| Hunspell it_IT (`zb ortografia`, livello a) | parole inesistenti, refusi | e/è, accordi, parole vere sbagliate, punteggiatura |
| LanguageTool (`zb ortografia`, livello b, `ZB_LANGUAGETOOL`) | molte regole di grammatica e punteggiatura, alcuni accordi, alcune confusioni | il contesto lungo, lo stile, le scelte della voce |
| `zb continuita` | date, età, durate, cifre, nomi in due grafie | il senso |
| Lettura mirata (questo ruolo) | e/è, accordi complessi, tempi, parole vere sbagliate, ripetizioni, coerenza | — |

## 9. Passaggio operativo (per capitolo)
1. `zb ortografia <libro>` e leggere il report: solo le righe del capitolo.
2. Lettura mirata nell'ordine delle sezioni 1-7, senza leggere per piacere: un passaggio per sezione,
   cercando la categoria, non rileggendo tutto ogni volta.
3. `06-diagnostica/copy/NN.md`: tabella riga, errore, correzione, sezione dei criteri.
4. Dopo l'«ok» al gate `copy`: modifiche puntuali (Edit), poi `zb esito <libro> N` per rimisurare.

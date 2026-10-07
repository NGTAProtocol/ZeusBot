# Difetti del motore: stato

Fonti: 06-diagnostica/motore-da-correggere.md (5 voci) e i resoconti dei passi (lotti 11-20, 21-30, 31-37, 38-43, chiusura). Hash sul ramo `motore`.

| # | Voce | Stato | Dettaglio |
|---|---|---|---|
| 1 | Piano parole approvato: le parole reali cambiano lo sha256 e chiedono `riapprova` | risolto (37269eb, 22b00b7) | «Parole reali» e «Scarto» sono colonne di misura escluse dall'impronta |
| 2 | fase.py: stato salvato dopo le stampe (uscita chiusa = stato perso) | risolto (37269eb) | i messaggi si stampano dopo `salva_stato` |
| 3 | continuita.py: nomi in due grafie con parole maiuscole a inizio frase | risolto (37269eb) | prova «Calvo a inizio frase ignorato» |
| 4 | riciclo.py: battute canoniche non escluse dall'anti-riciclo | risolto (37269eb) | prova «battute del manuale / KO rimasti» |
| 5 | fase.py: `correggi` solo a gate aperto | risolto (b30c897) | correzione registrata fuori dal gate |
| 6 | Passo che scende dopo un esito su un capitolo già scritto | risolto (b30c897) | |
| 7 | Contatori del libro («fischiare», «non era…») senza eccezioni per unità | risolto (2e49c98, 921359c) | `consentito_in_capitoli`, `conta_per: unita`, `escludi_pattern` |
| 8 | Frase media non controllata negli interludi | risolto (2e49c98) | avviso con l'intervallo dei capitoli |
| 9 | Percentuali del piano parole con il punto | risolto (2e49c98) | |
| 10 | Fase «chiusura» con unità del piano mancanti | risolto (a5e3fda) | `zb fase stesura --motivo` |
| 11 | `correggi` non segue i file rinominati | risolto (a5e3fda) | la voce del cap. 37 registrata prima resta con «—» (non retroattivo) |
| 12 | Pattern «Non era X. Era Y.» solo era/fu | risolto (libro.yaml 77e5eb6; prova 921359c) | forma generica, esclusa la frase del cap. 21 |
| 13 | Budget degli interludi | non era un difetto (prova 921359c) | il controllo c'era già; nel resoconto precedente l'avevo segnalato per errore |
| 14 | `esito`/`correggi` in fase «chiusura» | risolto (921359c) | ricontrolla senza cambiare fase |
| 15 | Commit del cap. 23 con dentro il cap. 25 | non del motore | era lo script di salvataggio; corretto allora |
| 16 | Unità accettate prima di `unita_accettate` riconosciute dal report «Esito: 0 KO» | limite noto | fase.py 129-130; effetto: un report cancellato a mano farebbe risultare l'unità mancante (blocco recuperabile con `zb esito`) |
| 17 | Più correzioni della stessa unità prima di un commit: tutte con lo stesso sha256 precedente (HEAD) | aperto | fase.py 412; effetto: registro impreciso (le 4 correzioni dell'epilogo hanno tutte e4120337… come precedente), nessun blocco; correzione: usare come precedente lo `sha256_corretto` dell'ultima voce registrata per lo stesso file, se più recente di HEAD |
| 18 | `compila` scrive «Capitolo N» senza il titolo del capitolo | aperto | compila.py 21-22; effetto: falso OK (i titoli, compreso «Il transatlantico», spariscono dal .md completo e dal sommario); correzione: leggere il titolo dalla riga «# N — Titolo» e scrivere «Capitolo N — Titolo» (o solo il titolo, secondo libro.yaml) |
| 19 | `zb conta` scrive 06-diagnostica/conteggio.md anche quando serve solo il totale | limite noto | file derivato non richiesto (cancellato a mano) |

# Risparmio di token e subagenti

Obiettivo: stesso livello editoriale con molti meno token, e il contesto principale sempre pulito.
Non si promettono percentuali: il risparmio si misura (vedi "Misura").

## 1. Cosa costa meno
1. **Gli script fanno tutto ciò che è meccanico** (conteggi, continuità, ortografia, compilazione, PDF, KDP): zero token di ragionamento. Niente LLM per ciò che uno script sa fare.
2. **Capsule di continuità** (`07-capsule/NN.md`, circa 150-180 parole per capitolo): chi scrive o revisiona legge le capsule dei capitoli precedenti, non i capitoli interi. È il risparmio più grande su libri lunghi.
3. **Un ruolo = un subagente con contesto proprio**: legge solo i suoi file, lavora, restituisce al chiamante al massimo 10 righe. Il contesto principale non si riempie di testo dei capitoli.
4. **Modelli per compito**: modello forte solo dove serve giudizio (struttura, editing strutturale); modello medio per scrittura e revisione di frase; modello leggero per capsule e lavori di riassunto. Scelta scritta in un solo file di dati, `motore/dati/modelli-ruoli.yaml`, che `zb agenti attiva` riporta nel campo `model` di ciascun agente; tarata con la prova (vedi "Misura").
5. **Modifiche puntuali**: i revisori applicano correzioni con modifiche mirate (str_replace/Edit), non riscrivono il capitolo intero.
6. **Report brevi a formato fisso**: citano capitolo e riga, non incollano brani lunghi.
7. **File non letti all'avvio**: `docs/` (esportazioni, archivio, guida) non si legge mai nelle sessioni di lavoro, solo su richiesta. `CLAUDE.md` resta sotto le 30 righe.
8. **Output compatto di zb**: i comandi stampano al massimo N righe (default 40) e rimandano al report su file.
9. **Riga "Letto" e capsule evitano riletture**; dopo una compattazione si rilegge solo ciò che serve.
10. **Prefisso stabile**: CLAUDE.md e istruzioni dei ruoli non cambiano a ogni sessione, così il caching dei prompt funziona.

## 2. Subagenti: cosa va in parallelo e cosa no
- **In sequenza (mai in parallelo)**: scrittura dei capitoli, perché ogni capitolo dipende dal precedente (continuità, voce, informazioni date).
- **In parallelo (max 3 alla volta, per non saturare i limiti)**: line editing, copyediting e controlli per capitolo su capitoli diversi, perché ogni capitolo si rivede da solo. Se i limiti d'uso o gli errori 429 compaiono, scendere a 2 o 1.
- **Un capitolo, un subagente**: contesto pulito per capitolo; separazione tra chi scrive e chi revisiona garantita dalla struttura (agenti diversi, sessioni diverse).
- **Capsula subito dopo ogni capitolo approvato**: subagente leggero.
- I subagenti non fanno commit né push: li fa il chiamante con `zb` dopo ogni lotto.
- I subagenti consumano token anch'essi: il risparmio viene da contesti piccoli, script e modelli giusti, non dal parallelismo in sé. Il parallelismo serve al tempo, non ai token.

## 3. Dove stanno i subagenti
- Fonte unica: `motore/editoriale/agenti/*.md` (formato subagenti di Claude Code: frontmatter con name, description, tools, model).
- Attivazione: `zb agenti attiva` (solo sui rami dei libri, con ok dell'autore) copia gli agenti in `.claude/agents/` del ramo, come per gli hook. Sul ramo motore restano spenti.
- Prima di attivarli, Claude Code verifica il formato corrente nella documentazione ufficiale dei subagenti e adegua i file se serve.

## 4. Orchestrazione per un libro
Chiamante (sessione principale) = direttore d'orchestra, non scrive prosa:
1. `zb avvio`, poi chiama l'agente del passo corrente con slug e numero di capitolo.
2. Legge solo la risposta breve e il report su file se serve.
3. Dopo ogni lotto: `zb esito`, capsule, commit e push con `zb`, report di sessione.
4. Alle fermate chiede l'ok all'autore (avanti, ok, correggi).

## 5. Misura
`zb prove` o uno script `zb consumo` registra per sessione: capitoli, parole scritte, righe lette, numero di subagenti, durata. Prima prova: stesso mini-libro con e senza capsule; si confronta il contesto letto. Le scelte del campo `model` si tarano su quella prova: se un modello leggero sbaglia sul copyediting italiano, si alza solo quel ruolo.

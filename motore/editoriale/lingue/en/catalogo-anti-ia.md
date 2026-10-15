# Anti-AI catalogue for English

Written for this engine. The writer applies it while drafting; the line editor uses it to diagnose; `zb esito`
measures what can be measured (`motore/script/antiia.py`, audit mode: the text is never rewritten). It is a
quality filter: it does **not** outrank the book's style manual, the voice card or the brief. A documented
choice in the manual wins.

## 0. Vocabulary tiers
| Tier | Treatment | Source |
|---|---|---|
| L1 always replace | at most P2 | `motore/dati/antiia.yaml` (`en`), from ai-writing-auditor (MIT) |
| L2 flag in clusters | at most P2 | same |
| L3 flag by density | at most P2 | empty |
Word lists are style preferences, not detection signals: they shift with model versions and were not measured
on this engine's output. They never block. Replace them with `zb antiia estrai` data when a corpus exists.

## Severity
P0 breaks the reading or the voice (third chapter in a row with the same ending; dialogue that states the
subtext). P1 obvious and repeated pattern. P2 look at it; change only if the passage improves.

## Profiles
narrative (prose outside dialogue): sections A, C, E weigh most. dialogue: section D; rhythm measures do not apply.

## A. Rhythm (measured)
Sentences of similar length (`variazione_frasi`); paragraphs all the same size; consecutive sentences opening
with the same word (`aperture_uguali`); a three-item list as the cadence of every paragraph; the corrective
"not X, but Y" construction more than once a chapter.

## B. Abstraction instead of fact
An emotion or mood named in the abstract where the scene could show a perceptible fact. Replace with the fact.

## C. Explaining what was shown
The line after a gesture that states its meaning; a dialogue tag with an adverb that repeats the tone;
interior thought that repeats the dialogue; a paragraph that closes by summarising itself.

## D. Over-explicit dialogue
Everyone in the same register; lines that say exactly what the speaker feels; every question answered;
pleasantries that do no work. Use the chapter card's subtext, interruptions, sideways answers.

## E. Openings and endings
Weather or waking-up openings; consecutive chapters ending the same way (`chiusure_uguali`); the same hook type.

## F. Default-model failures (adapted from haowjy/creative-writing-skills, Apache-2.0)
Over-elaborating the scope of a scene; flattening the voice into one competent register; info-dumping;
labelling emotions; resolving tension too early; every character equally articulate; emotional commentary
after the moment; collapsing deliberate ambiguity; over-intensified language; ignoring the project's style.

## G. What not to touch
Deliberate ambiguity, omissions, repetition, odd sentences that belong to the voice, real lists, terms of art.
Fix by subtraction, not substitution; re-read what a fix introduced; never add details the source does not
support (adapted from chi-feng/humanizer, MIT).

## H. Natural imperfections (dosed)
A lopsided sentence because the character thinks that way; deliberate repetition; a broken-off sentence; a
detail left unexplained. Never real spelling or grammar errors. About one per 800-1,000 words.

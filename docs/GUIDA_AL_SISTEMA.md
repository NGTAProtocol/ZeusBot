<!--
Sorgente di docs/GUIDA_AL_SISTEMA.pdf. Per rigenerare il PDF (pandoc e Chromium di Playwright, già nel container):

  node docs/GUIDA_AL_SISTEMA.md.js   ← non esiste: il programma sta qui sotto, fra le righe «INIZIO» e «FINE».

Copiare il programma in un file fuori dal repository (per esempio /tmp/guida.js) e lanciarlo dalla radice:
  node /tmp/guida.js docs/GUIDA_AL_SISTEMA.md docs/GUIDA_AL_SISTEMA.pdf

INIZIO
const { execFileSync } = require('child_process');
const fs = require('fs'); const path = require('path'); const os = require('os');
const { chromium } = require('playwright');
(async () => {
  const [src, out] = process.argv.slice(2);
  const corpo = execFileSync('pandoc', [src, '-f', 'markdown-smart', '-t', 'html5', '--wrap=none']).toString();
  const html = '<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Guida al sistema</title></head><body>' + corpo + '</body></html>';
  const tmp = path.join(os.tmpdir(), 'guida.html'); fs.writeFileSync(tmp, html);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + tmp, { waitUntil: 'networkidle' });
  await p.pdf({ path: out, preferCSSPageSize: true, printBackground: true, outline: true, tagged: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;text-align:center;font:12pt DejaVu Sans,sans-serif;color:#555"><span class="pageNumber"></span></div>' });
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
FINE

I numeri di pagina dell'indice sono scritti a mano qui sotto: se il testo cambia, vanno ricontrollati sul PDF.
-->

<style>
@page { size: 110mm 200mm; margin: 12mm 9mm 16mm 9mm; }
html { font-size: 12.5pt; }
body { font-family: "DejaVu Sans", "Liberation Sans", sans-serif; line-height: 1.45; color: #1a1a1a; margin: 0; }
h1 { font-size: 19pt; line-height: 1.2; margin: 0 0 6mm 0; color: #123d6a; break-before: page; }
h1.copertina { break-before: avoid; font-size: 24pt; margin-top: 30mm; }
h2 { font-size: 15pt; line-height: 1.25; margin: 6mm 0 2mm 0; color: #123d6a; break-after: avoid; }
h3 { font-size: 13pt; margin: 4mm 0 1.5mm 0; break-after: avoid; }
p, li { font-size: 12.5pt; orphans: 2; widows: 2; }
ul, ol { padding-left: 5mm; margin: 1.5mm 0; }
li { margin: 0.8mm 0; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 11.5pt; background: #eef2f6; padding: 0 0.6mm; border-radius: 1mm; overflow-wrap: anywhere; }
a { color: #123d6a; text-decoration: none; }
table { width: 100%; border-collapse: collapse; margin: 2mm 0 3mm 0; table-layout: fixed; }
th, td { font-size: 12pt; border: 0.3mm solid #b8c4d0; padding: 1.2mm 1.4mm; vertical-align: top; overflow-wrap: anywhere; hyphens: auto; text-align: left; }
th { background: #e3eaf2; }
tr { break-inside: avoid; }
.fonte { color: #555; }
.nota { border-left: 1.2mm solid #c98a1a; background: #fbf4e6; padding: 1.5mm 2.5mm; margin: 2.5mm 0; }
.nota p { margin: 1mm 0; }
.indice ol { list-style: none; padding-left: 0; }
.indice li { display: flex; font-size: 12.5pt; margin: 1.6mm 0; }
.indice li a { flex: 1; }
.indice li span { padding-left: 2mm; }
svg { width: 100%; height: auto; }
.copertina-sotto { font-size: 13pt; color: #444; }
</style>

<h1 class="copertina">Guida al sistema</h1>

<p class="copertina-sotto">Come è fatta la casa editrice del repository ZeusBot: chi fa cosa, il percorso di un libro, le regole.</p>

<p class="copertina-sotto">Per Felice, autore. Ottobre 2026.</p>

<p class="copertina-sotto">Fotografia del ramo <code>motore</code> al commit <code>f7decc4</code>.</p>

<div class="nota">

**Come leggere.** Tra parentesi, in grigio, c'è il file da cui viene ogni affermazione. Quando una cosa non c'è nel repository, la guida lo scrive: «non esiste».

</div>

# Indice {#indice}

<div class="indice">
<ol>
<li><a href="#parole">0. Le parole da sapere</a></li>
<li><a href="#cap1">1. A cosa serve il sistema</a></li>
<li><a href="#cap2">2. Organigramma: chi fa cosa</a></li>
<li><a href="#cap3">3. Il percorso di un libro</a></li>
<li><a href="#cap4">4. Le regole</a></li>
<li><a href="#cap5">5. I rami</a></li>
<li><a href="#cap6">6. Cosa c'è adesso</a></li>
<li><a href="#cap7">7. Appendici e indice</a></li>
<li><a href="#cap8">8. Cosa resta da fare all'autore</a></li>
<li><a href="#cap9">9. Dove trovare le cose</a></li>
</ol>
</div>

# 0. Le parole da sapere {#parole}

Poche parole tecniche tornano spesso. Eccole, una volta per tutte.

- **Repository**: l'archivio del progetto su GitHub, con tutta la storia delle modifiche. Qui si chiama ZeusBot.
- **Ramo**: una versione parallela del repository. Ogni ramo ha i suoi file. Il ramo `motore` contiene la macchina; ogni libro vive su un ramo suo.
- **Commit**: un salvataggio con nome e data. Ha un codice breve, per esempio `f7decc4`.
- **Push**: l'invio dei salvataggi su GitHub (su «origin», la copia in rete). Finché non c'è il push, il lavoro esiste solo nel computer di lavoro.
- **Merge**: l'unione di un ramo dentro un altro.
- **Script**: un piccolo programma che fa un lavoro preciso (contare parole, fare il PDF…).
- **Hook**: un guardiano automatico. Claude Code lo chiama prima di certe azioni; l'hook può lasciar passare, avvisare o bloccare.
- **Claude Code**: l'assistente che lavora nel repository, legge le regole e lancia i comandi.
- **YAML**: un formato di testo per i dati, fatto di righe «nome: valore». I file finiscono in `.yaml`.
- **Gate**: una fermata obbligata. Il lavoro si ferma finché l'autore non approva.
- **sha256**: l'«impronta digitale» di un file. Se cambia anche una virgola, l'impronta cambia.
- **KDP**: Kindle Direct Publishing, il servizio di Amazon per pubblicare.
- **Metadati del PDF**: dati nascosti nel file, come Title (titolo) e Author (autore).
- **Slug**: il nome breve di un libro usato nei percorsi, senza spazi né accenti.

# 1. A cosa serve il sistema {#cap1}

Il sistema è una fabbrica di libri. Serve per romanzi di qualsiasi genere (<span class="fonte">motore/README.md</span>).

Il cuore è il **motore**: procedura, script, modelli vuoti, profili di genere e dati KDP. Il motore non contiene libri veri (<span class="fonte">motore/README.md</span>).

Il percorso è sempre lo stesso. L'autore scrive un briefing. Il motore crea la cartella del libro. Claude Code scrive i documenti e poi i capitoli, uno alla volta. A ogni tappa importante l'autore approva. Alla fine il motore controlla il testo, compone il libro, fa il PDF di stampa e prepara il pacchetto per KDP (<span class="fonte">motore/README.md, «Dal briefing al PDF»</span>).

Tre idee reggono tutto (<span class="fonte">CLAUDE.md</span>):

1. **Il motore resta pulito.** Il ramo `motore` non contiene mai un libro.
2. **Si scrive solo nella cartella del libro.** Mai nel motore, mai altrove.
3. **Proponi, l'autore approva, poi applica.** Claude Code non approva mai da solo.

# 2. Organigramma: chi fa cosa {#cap2}

## Lo schema

<svg viewBox="0 0 320 470" xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans, sans-serif" role="img" aria-label="Organigramma del sistema">
<defs><marker id="fr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#444"/></marker></defs>
<rect x="60" y="4" width="200" height="46" rx="8" fill="#fbe9c8" stroke="#c98a1a" stroke-width="1.5"/>
<text x="160" y="24" text-anchor="middle" font-size="15" font-weight="bold">Felice (autore)</text>
<text x="160" y="42" text-anchor="middle" font-size="12">decide e approva: ok, avanti, correggi</text>
<line x1="160" y1="50" x2="160" y2="72" stroke="#444" stroke-width="1.5" marker-end="url(#fr)"/>
<rect x="60" y="74" width="200" height="46" rx="8" fill="#dbe7f3" stroke="#123d6a" stroke-width="1.5"/>
<text x="160" y="94" text-anchor="middle" font-size="15" font-weight="bold">Claude Code</text>
<text x="160" y="112" text-anchor="middle" font-size="12">propone, scrive, lancia zb</text>
<rect x="4" y="142" width="150" height="62" rx="8" fill="#eef2f6" stroke="#123d6a"/>
<text x="79" y="162" text-anchor="middle" font-size="13" font-weight="bold">Regole</text>
<text x="79" y="180" text-anchor="middle" font-size="11.5">CLAUDE.md</text>
<text x="79" y="196" text-anchor="middle" font-size="11.5">PROCEDURA.md</text>
<rect x="166" y="142" width="150" height="62" rx="8" fill="#f6e3e3" stroke="#a33" />
<text x="241" y="162" text-anchor="middle" font-size="13" font-weight="bold">Hook (guardiani)</text>
<text x="241" y="180" text-anchor="middle" font-size="11.5">recinto: blocca</text>
<text x="241" y="196" text-anchor="middle" font-size="11.5">manoscritto: avvisa</text>
<line x1="120" y1="120" x2="95" y2="140" stroke="#444" stroke-width="1.2" marker-end="url(#fr)"/>
<text x="62" y="134" font-size="10.5" fill="#444">legge</text>
<line x1="210" y1="140" x2="190" y2="122" stroke="#a33" stroke-width="1.2" marker-end="url(#fr)"/>
<text x="214" y="134" font-size="10.5" fill="#a33">sorvegliano</text>
<line x1="160" y1="120" x2="160" y2="226" stroke="#444" stroke-width="1.5" marker-end="url(#fr)"/>
<text x="166" y="220" font-size="10.5" fill="#444">lancia</text>
<rect x="40" y="228" width="240" height="56" rx="8" fill="#dbe7f3" stroke="#123d6a" stroke-width="1.5"/>
<text x="160" y="250" text-anchor="middle" font-size="15" font-weight="bold">Motore: zb + script</text>
<text x="160" y="270" text-anchor="middle" font-size="12">motore/zb, motore/script/ (ramo motore)</text>
<line x1="110" y1="284" x2="85" y2="308" stroke="#444" stroke-width="1.2" marker-end="url(#fr)"/>
<line x1="210" y1="284" x2="235" y2="308" stroke="#444" stroke-width="1.2" marker-end="url(#fr)"/>
<text x="40" y="300" font-size="10.5" fill="#444">legge</text>
<text x="240" y="300" font-size="10.5" fill="#444">legge</text>
<rect x="4" y="310" width="150" height="62" rx="8" fill="#eef2f6" stroke="#123d6a"/>
<text x="79" y="330" text-anchor="middle" font-size="13" font-weight="bold">Dati</text>
<text x="79" y="347" text-anchor="middle" font-size="11.5">7 profili, 6 modelli</text>
<text x="79" y="363" text-anchor="middle" font-size="11.5">dati KDP, lista nera</text>
<rect x="166" y="310" width="150" height="62" rx="8" fill="#eef2f6" stroke="#123d6a" stroke-dasharray="4 3"/>
<text x="241" y="330" text-anchor="middle" font-size="13" font-weight="bold">Banca-voci</text>
<text x="241" y="347" text-anchor="middle" font-size="11.5">repository a parte</text>
<text x="241" y="363" text-anchor="middle" font-size="11.5">sola lettura</text>
<line x1="160" y1="284" x2="160" y2="394" stroke="#2a7a3a" stroke-width="1.8" marker-end="url(#fr)"/>
<text x="166" y="388" font-size="10.5" fill="#2a7a3a">scrive solo qui</text>
<rect x="40" y="396" width="240" height="66" rx="8" fill="#e2f1e4" stroke="#2a7a3a" stroke-width="1.5"/>
<text x="160" y="418" text-anchor="middle" font-size="15" font-weight="bold">Il libro</text>
<text x="160" y="437" text-anchor="middle" font-size="12">libri/&lt;slug&gt;/</text>
<text x="160" y="453" text-anchor="middle" font-size="12">sul ramo del libro</text>
</svg>

<p class="fonte">Schema ricavato da CLAUDE.md, motore/README.md e docs/INFRASTRUTTURA_COMPLETA.md §3 e §8.4.</p>

## Chi fa cosa, in breve

| Chi | Che cosa fa | Dove sta |
|---|---|---|
| Felice | Scrive il briefing, risponde ok / avanti / correggi, decide | — |
| Claude Code | Legge le regole, propone, scrive nel libro, lancia `zb` | — |
| Motore | Crea, controlla, compone, impagina | `motore/` |
| Regole | Dicono come si lavora | `CLAUDE.md`, `motore/PROCEDURA.md` |
| Hook | Sorvegliano le scritture | `motore/script/hook_*.py` |
| Libro | Il lavoro vero | `libri/<slug>/` |

<p class="fonte">(CLAUDE.md; motore/README.md; docs/INFRASTRUTTURA_COMPLETA.md §8.4)</p>

## Il motore: `zb` e gli script

`zb` è il comando unico. Si scrive `python3 motore/zb <comando> <libro>`. Il libro si indica sempre con il percorso della sua cartella (<span class="fonte">motore/zb; motore/README.md, «Comandi»</span>).

Ogni comando di `zb` lancia uno script della cartella `motore/script/`. Gli script sono 28 file (<span class="fonte">motore/zb, tabella SCRIPT; cartella motore/script/</span>).

I comandi principali (<span class="fonte">motore/README.md, «Comandi»</span>):

- `zb nuovo`: crea il libro dal briefing.
- `zb avvio`: controlli di inizio sessione e riga «Letto: …».
- `zb stato`: mostra a che punto è il libro. Non scrive nulla.
- `zb pronto`: chiude il lavoro di una fase e apre la fermata.
- `zb ok`, `zb avanti`, `zb correggi`: le risposte dell'autore.
- `zb esito`: controlla un capitolo appena scritto.
- `zb continuita`, `zb ortografia`, `zb compila`, `zb impagina`, `zb pdf`, `zb pacchetto`, `zb kdp`: la chiusura.
- `zb prove`: le prove del motore sui mini-libri inventati.

Nessun comando del motore fa commit o push da solo (<span class="fonte">motore/PROCEDURA.md §8</span>).

## La «Bibbia editor»

Nel repository «Bibbia editor» è il nome dato all'insieme delle regole editoriali valide per ogni libro. Il commit `668afc2` si chiama proprio «Bibbia editor: appendici e indice» e modifica `motore/PROCEDURA.md` (<span class="fonte">docs/INFRASTRUTTURA_COMPLETA.md §4</span>).

Le regole stanno in due file (<span class="fonte">docs/INFRASTRUTTURA_COMPLETA.md §4</span>):

- `CLAUDE.md`: le regole di avvio. Claude Code le legge a ogni sessione.
- `motore/PROCEDURA.md`: la procedura completa, in 11 sezioni.

Le aiutano alcuni file di dati, per esempio la lista nera di base (`motore/dati/lista-nera.yaml`) e le parole italiane ammesse (`motore/dati/parole-ammesse-it.txt`) (<span class="fonte">docs/INFRASTRUTTURA_COMPLETA.md §4</span>).

<div class="nota">

Attenzione: la `bibbia.md` di ogni libro (personaggi, luoghi, fatti) è un'altra cosa. Sta nella cartella del libro, in `02-bibbia/` (<span class="fonte">docs/INFRASTRUTTURA_COMPLETA.md §4</span>).

</div>

## Profili di genere

Un profilo dà i valori predefiniti di un genere: lunghezza, capitoli, scene, frase media, dialogo (<span class="fonte">motore/PROCEDURA.md §3</span>).

Sono 7, nella cartella `motore/profili/`: fantascienza, fantasy, giallo, narrativa letteraria, romance, thriller, young adult (<span class="fonte">cartella motore/profili/</span>).

Un valore del briefing fuori dal profilo è accettato solo con un «Motivo override:» scritto nel briefing. Senza motivo, `zb nuovo` si ferma (<span class="fonte">motore/PROCEDURA.md §3</span>).

## Voci narranti

Una voce dice **come** si racconta. Il **cosa** lo decide l'autore nel briefing (<span class="fonte">motore/README.md, «Banca-voci»</span>).

Le voci stanno in un repository separato, la banca-voci, mai dentro il motore. Il motore le legge in sola lettura dalla cartella indicata da `ZB_BANCA_VOCI` (<span class="fonte">motore/README.md, «Banca-voci»</span>).

Oggi le voci sono 11, tutte pronte. L'elenco è in `indice.yaml` della banca-voci e in `motore/passaggio-di-consegne.md`, «Stato» (<span class="fonte">motore/passaggio-di-consegne.md</span>). Questa guida non le nomina.

Ogni voce ha una scheda in 7 sezioni e un elenco di espressioni vietate, `divieti.yaml` (<span class="fonte">motore/README.md, «Banca-voci»</span>).

Un libro sceglie la voce nel briefing («Voce dalla banca:», «Ambientazione:»); `zb nuovo` la scrive in `libro.yaml` (<span class="fonte">motore/README.md, «Banca-voci»</span>).

Se il briefing contrasta con la voce, vince il briefing, e il contrasto si segnala (<span class="fonte">motore/modelli/briefing.md; README della banca-voci, copiato in docs/INFRASTRUTTURA_COMPLETA.md §6</span>).

## Modelli

I modelli sono i file vuoti da cui nasce un libro. Stanno in `motore/modelli/` e sono 6 (<span class="fonte">cartella motore/modelli/</span>):

| File | A cosa serve |
|---|---|
| `briefing.md` | Il modulo che compila l'autore |
| `libro.yaml` | Le regole del libro |
| `stato.yaml` | A che punto è il libro |
| `cronologia.yaml` | Date ed eventi |
| `LEGGIMI.md` | Cosa leggere a ogni avvio |
| `conferme-autore.yaml` | Le conferme per KDP |

<p class="fonte">(motore/modelli/; docs/INFRASTRUTTURA_COMPLETA.md §3.3)</p>

## Hook

Gli hook sono tre. Stanno nel modello `motore/dati/hook-settings.esempio.json` (<span class="fonte">motore/dati/hook-settings.esempio.json</span>):

| Hook | Quando | Cosa fa |
|---|---|---|
| recinto | prima di ogni scrittura di file | **Blocca** le scritture fuori dal libro attivo |
| manoscritto | prima di scrivere in `04-manoscritto/` | Oggi **avvisa** se manca `zb avvio` |
| sessione | all'inizio della sessione | Annota la sessione |

<p class="fonte">(motore/script/hook_recinto.py; motore/script/hook_manoscritto.py; motore/dati/hook.yaml; motore/PROCEDURA.md §10)</p>

Gli hook si accendono solo sui rami dei libri, con `zb hook attiva --ok`. Sul ramo `motore` sono spenti per scelta (<span class="fonte">motore/passaggio-di-consegne.md, «Stato»</span>). Dettagli nel capitolo 4.

## CLAUDE.md

È il foglio delle regole di avvio. Sta nella radice del repository e Claude Code lo legge a ogni sessione (<span class="fonte">docs/INFRASTRUTTURA_COMPLETA.md §4 e §9</span>).

Ha al massimo 30 righe e nessun nome di libro: lo controlla una prova del motore (<span class="fonte">docs/INFRASTRUTTURA_COMPLETA.md §9; motore/script/prove.py</span>). Cosa dice: capitolo 4.

## Rami dei libri

Ogni libro vive su un ramo suo, nella cartella `libri/<slug>/`. Quel ramo porta anche una copia del motore (<span class="fonte">docs/INFRASTRUTTURA_COMPLETA.md §8.3</span>). Dettagli nel capitolo 5.

# 3. Il percorso di un libro {#cap3}

Il libro attraversa dodici tappe; dove c'è un gate il lavoro si ferma finché l'autore non scrive «ok» (<span class="fonte">motore/editoriale/00-percorso.md</span>).

| # | Tappa | Chi lavora | Fermata |
|---|---|---|---|
| 1 | Briefing | autore | — |
| 2 | Cartella unica `libri/<slug>/` | `zb nuovo` | — |
| 3 | Struttura: nove file | architetto della struttura | — |
| 4 | Revisione della struttura | diagnosta, poi editor strutturale | `struttura` |
| 5 | Documenti: bibbia, codex, cronologia | direttore editoriale | `documenti` |
| 6 | Pagina campione | scrittore con voce | `pagina_campione` |
| 7 | Stesura, un capitolo alla volta | scrittore, poi capsula | `primi_capitoli` |
| 8 | Revisione strutturale del manoscritto | diagnosta, poi editor strutturale | `struttura_manoscritto` |
| 9 | Line editing | line editor | `line` |
| 10 | Copyediting | correttore di italiano | `copy` |
| 11 | Bozze | correttore di bozze | `bozze` |
| 12 | Chiusura meccanica | motore | — |

## Le risposte dell'autore
`avanti` mostra il blocco successivo; `ok` approva; `correggi: …` chiede una correzione; `stato` mostra dove si è. Nelle tappe 8-11 l'«ok» approva le proposte: solo dopo si applicano, con modifiche puntuali.

## Prima di ogni sessione: `zb avvio`
Stampa la riga «Letto» e si ferma se qualcosa non va: modifiche non salvate, file fuori dal libro, un altro libro attivo, documenti approvati cambiati. In una sessione nuova si legge lo stato compatto del libro (15-20 righe) e la scheda del capitolo.

## La stesura
`/scrivi-capitolo N` prepara il capitolo (scheda, schede dei personaggi e dei luoghi in scena, fatti bloccati, capsule), chiama lo scrittore, controlla il capitolo, scrive la capsula e salva. Poi si ferma: la revisione è un altro comando (`/revisiona`), in un'altra fase.

## La chiusura
`zb continuita`, `zb ortografia`, `zb compila`, `zb impagina`, `zb pdf`, `zb pacchetto`, `zb kdp`, poi `zb pronto`.

## La traduzione
`zb traduci <libro> --a en inizia`: guida e glossario si approvano prima del capitolo 1; ogni capitolo tradotto ha i suoi controlli (paragrafi, battute, numeri, nomi, parole rimaste in italiano, lunghezza, nessuna nota aggiunta); poi line, copy e revisione di fedeltà. KDP chiede di dichiarare una traduzione fatta con l'IA (pagina ufficiale, verificata il 2026-10-15). Per un'edizione in vendita è consigliata la lettura finale di un madrelingua.

## Dopo ogni passo: il salvataggio
`zb salva`: controlla che nessun file stia fuori dal libro, salva e invia su GitHub.

# 4. Le regole {#cap4}

## Cosa dice CLAUDE.md
Una cartella per libro; prima `zb avvio`; la sessione principale non scrive prosa; chi scrive non rivede; report di sessione ogni 5 scambi o a «passaggio»; una sola scala di precedenza; salvataggio con `zb salva` (<span class="fonte">CLAUDE.md</span>).

## Il recinto
Blocca le scritture fuori dal libro attivo: con l'hook (anche sui comandi Bash), con il controllo che git fa prima di ogni salvataggio, con `zb avvio` e `zb salva`. Ciò che l'hook non vede (uno script che scrive senza nominare il file) lo ferma il controllo di git. Sul ramo del motore hook, agenti e comandi restano spenti.

## L'ordine di precedenza
1. manuale del libro e `libro.yaml`; 2. briefing e scheda della voce (se contrastano vince il briefing, e si segnala); 3. profilo di genere; 4. `motore/editoriale/`; 5. procedura del motore. Il catalogo anti-IA e i criteri del correttore sono filtri: non stanno sopra il manuale (<span class="fonte">motore/editoriale/LEGGIMI.md</span>).

# 5. I rami {#cap5}

## Il ramo `motore`
Solo il motore: codice, regole, mini-libri inventati. Nessun libro, nessun nome di libro o di autore reale (lo controlla `zb separazione`, anche in `docs/` e in `CLAUDE.md`).

## I rami dei libri
Un libro per ramo, in `libri/<slug>/`. I libri vecchi hanno il loro CLAUDE.md per scelta dell'autore e non si toccano.

# 6. Cosa c'è adesso {#cap6}

- **Subagenti e comandi** (`/scrivi-capitolo`, `/revisiona`, `/diagnosi`, `/handover`): si accendono sul ramo del libro con `zb agenti attiva --ok`.
- **Anti-IA**: controllo che misura e non riscrive (`zb esito`, `zb antiia`). Per l'italiano nessuna lista di parole finché non si estrae dai dati.
- **Correttore di italiano**: criteri, passaggio per capitolo, Hunspell e LanguageTool (`zb languagetool installa`).
- **Inglese**: un libro si può scrivere direttamente in inglese con gli stessi ruoli e gate.

# 7. Appendici e indice {#cap7}

Le appendici (soluzioni, mappe, glossari) stanno in `05-appendici/` e si dichiarano in `libro.yaml`; il sommario lo genera `zb compila` (<span class="fonte">motore/PROCEDURA.md, sezione 7</span>).

# 8. Cosa resta da fare all'autore {#cap8}

- Verificare i dati KDP e registrare la verifica (`zb verifica KDP fatta AAAA-MM-GG`).
- Fornire, se si vuole, un corpus per il vocabolario anti-IA italiano.
- Decidere sulla licenza non commerciale di un repository esterno (APODICTIC).
- Elenco aggiornato: `docs/DA_FORNIRE.md`.

# 9. Dove trovare le cose {#cap9}

Ramo «motore» vuol dire anche: nella copia del motore di ogni ramo di libro aggiornato.

| Cosa cerchi | File | Ramo |
|-------|----------|-----|
| Regole di avvio | `CLAUDE.md` | motore (ogni ramo di libro ha il suo) |
| Procedura completa | `motore/PROCEDURA.md` | motore |
| Elenco dei comandi | `motore/README.md`, «Comandi»; `python3 motore/zb aiuto` | motore |
| Stato del lavoro sul motore | `motore/passaggio-di-consegne.md` | motore |
| Limiti noti del motore | `motore/report-motore.md` §11 | motore |
| Progetto originale | `motore/proposta-motore.md` | motore |
| Profili di genere | `motore/profili/` | motore |
| Modelli vuoti | `motore/modelli/` | motore |
| Modulo del briefing | `motore/modelli/briefing.md` | motore |
| Dati KDP | `motore/dati/kdp.yaml` | motore |
| Lista nera | `motore/dati/lista-nera.yaml` | motore |
| Parole italiane ammesse | `motore/dati/parole-ammesse-it.txt` | motore |
| Cartelle di un libro | `motore/dati/struttura-libro.yaml` | motore |
| Campi di `libro.yaml` | `motore/dati/libro.schema.yaml` | motore |
| Hook | `motore/script/hook_*.py`, `motore/dati/hook-settings.esempio.json` | motore |
| Modalità dell'hook del manoscritto | `motore/dati/hook.yaml` | motore |
| Hook accesi | `.claude/settings.json` | ramo del libro |
| Impaginazione e font | `motore/stampa/` | motore |
| Prove e mini-libri inventati | `motore/script/prove.py`, `motore/prove/` | motore |
| Libro attivo | `libri/libro-attivo.md` | ramo del libro |
| Un libro | `libri/<slug>/` | ramo del libro |
| Briefing del libro | `libri/<slug>/00-progetto/briefing.md` | ramo del libro |
| Bibbia del libro | `libri/<slug>/02-bibbia/bibbia.md` | ramo del libro |
| Capitoli | `libri/<slug>/04-manoscritto/` | ramo del libro |
| Appendici | `libri/<slug>/05-appendici/` | ramo del libro |
| PDF e libro compilato | `libri/<slug>/05-output/` | ramo del libro |
| Report dei controlli | `libri/<slug>/06-diagnostica/` | ramo del libro |
| Pacchetto KDP | `libri/<slug>/06-pubblicazione/` | ramo del libro |
| Report di sessione del libro | `libri/<slug>/passaggio-di-consegne.md` | ramo del libro |
| Voci narranti | `indice.yaml`, `voci/<slug>/` | banca-voci, ramo `main` (repository a parte) |
| Archivio completo | `docs/INFRASTRUTTURA_COMPLETA.md` | motore |
| Questa guida | `docs/GUIDA_AL_SISTEMA.pdf` e `.md` | motore |

<p class="fonte">(docs/INFRASTRUTTURA_COMPLETA.md §8.4 e §9; motore/dati/struttura-libro.yaml; motore/README.md)</p>

Fine della guida.

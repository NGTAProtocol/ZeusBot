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

<p class="copertina-sotto">Fotografia del ramo <code>integrazione-editoriale</code> al commit <code>06cbb70</code>.</p>

<div class="nota">

**Come leggere.** Tra parentesi, in grigio, c'è il file da cui viene ogni affermazione. Quando una cosa non c'è nel repository, la guida lo scrive: «non esiste».

</div>

<div class="nota">

**Questa edizione** descrive il ramo `integrazione-editoriale` (commit `06cbb70`): la base del ramo di sessione ccr con le aggiunte del ramo `motore`. Le scelte dell'unione sono in `docs/DECISIONI_INTEGRAZIONE.md` (D1-D16) (<span class="fonte">docs/DECISIONI_INTEGRAZIONE.md, introduzione</span>).

</div>

# Indice {#indice}

<div class="indice">
<ol>
<li><a href="#parole">0. Le parole da sapere</a><span>4</span></li>
<li><a href="#cap1">1. A cosa serve il sistema</a><span>8</span></li>
<li><a href="#cap2">2. Organigramma: chi fa cosa</a><span>10</span></li>
<li><a href="#cap3">3. Il percorso di un libro</a><span>28</span></li>
<li><a href="#cap4">4. Le regole</a><span>49</span></li>
<li><a href="#cap5">5. I rami</a><span>58</span></li>
<li><a href="#cap6">6. Cosa c'è e cosa non esiste</a><span>61</span></li>
<li><a href="#cap7">7. Appendici e indice</a><span>65</span></li>
<li><a href="#cap8">8. Punti deboli e decisioni aperte</a><span>67</span></li>
<li><a href="#cap9">9. Dove trovare le cose</a><span>72</span></li>
</ol>
</div>

# 0. Le parole da sapere {#parole}

Poche parole tecniche tornano spesso. Eccole, una volta per tutte.

- **Repository**: l'archivio del progetto su GitHub, con tutta la storia delle modifiche. Qui si chiama ZeusBot.
- **Ramo**: una versione parallela del repository. Ogni ramo ha i suoi file. Il ramo `motore` contiene la macchina; ogni libro vive su un ramo suo.
- **Commit**: un salvataggio con nome e data. Ha un codice breve, per esempio `078b9b3`.
- **Push**: l'invio dei salvataggi su GitHub (su «origin», la copia in rete). Finché non c'è il push, il lavoro esiste solo nel computer di lavoro.
- **Merge**: l'unione di un ramo dentro un altro.
- **Script**: un piccolo programma che fa un lavoro preciso (contare parole, fare il PDF…).
- **Hook**: un guardiano automatico. Claude Code lo chiama prima o dopo certe azioni; l'hook può lasciar passare, avvisare o bloccare.
- **Claude Code**: l'assistente che lavora nel repository, legge le regole e lancia i comandi.
- **YAML**: un formato di testo per i dati, fatto di righe «nome: valore». I file finiscono in `.yaml`.
- **Gate** (fermata): il lavoro si ferma finché l'autore non risponde. Nei libri nuovi resta una sola fermata dell'autore, la pausa di lettura.
- **Modo automatico**: la scrittura va avanti da sola, senza approvazioni intermedie; i controlli li fa il motore. È una decisione dell'autore del 20 ottobre 2026.
- **Pausa di lettura**: ogni 3 capitoli (da 3 a 5, si sceglie in `libro.yaml`) il motore si ferma e ti dà l'elenco dei capitoli da leggere.
- **Struttura**: la prima fase dopo il briefing. Prima della prosa si fissano premessa, personaggi, svolte, scaletta, ritmo e scelte fisse (punto di vista, tempo, voce).
- **Cartella unica**: tutto ciò che riguarda un libro vive in `libri/<slug>/`, e il nome del libro non compare altrove.
- **Ruolo**: un mestiere editoriale (diagnosta, direttore, architetto, scrittore, editor, correttori). Una sessione di Claude Code svolge un ruolo solo.
- **Subagente** (o agente): un ruolo che Claude Code chiama come aiutante, con un contesto suo e pulito. Risponde con al massimo 10 righe.
- **Capsula**: il riassunto di continuità di un capitolo, in `07-capsule/NN.md`. Chi scrive legge le capsule, non i capitoli interi.
- **Audit anti-IA**: il controllo che segnala i segni di scrittura da IA. Il motore segnala; non riscrive.
- **sha256** (impronta): l'«impronta digitale» di un file. Se cambia anche una virgola, l'impronta cambia.
- **KDP**: Kindle Direct Publishing, il servizio di Amazon per pubblicare.
- **Metadati del PDF**: dati nascosti nel file, come Title (titolo) e Author (autore).
- **Slug**: il nome breve di un libro usato nei percorsi, senza spazi né accenti.

<p class="fonte">(motore/editoriale/glossario.md; docs/DECISIONI_INTEGRAZIONE.md, D4 e D11; motore/script/fase.py)</p>

# 1. A cosa serve il sistema {#cap1}

Il sistema è una casa editrice per romanzi di qualsiasi genere (<span class="fonte">motore/README.md; motore/editoriale/LEGGIMI.md</span>).

Il cuore è il **motore**: procedura, script, modelli vuoti, profili di genere, dati KDP e il livello editoriale (percorso, ruoli, agenti, anti-IA, correttore). Il motore non contiene libri veri (<span class="fonte">motore/README.md; motore/editoriale/LEGGIMI.md</span>).

Il percorso è sempre lo stesso. L'autore scrive un briefing. Il motore crea la cartella del libro. Prima la struttura, poi i documenti, poi i capitoli, uno alla volta. Seguono le revisioni, la chiusura meccanica, il PDF di stampa e il pacchetto per KDP (<span class="fonte">motore/editoriale/00-percorso.md</span>).

**Cosa cambia con il modo automatico.** Nei libri nuovi il motore scrive senza chiedere approvazioni a ogni tappa. Si ferma per te solo alla **pausa di lettura**, ogni 3 capitoli (<span class="fonte">docs/DECISIONI_INTEGRAZIONE.md, D4, D6, D11</span>).

Tre idee reggono tutto (<span class="fonte">CLAUDE.md</span>):

1. **Il motore resta pulito.** Il ramo `motore` non contiene mai un libro.
2. **Si scrive solo nella cartella del libro.** Mai nel motore, mai altrove.
3. **Proponi, l'autore approva, poi applica.** Claude Code non approva mai da solo.

<div class="nota">

La terza regola e il modo automatico vanno letti insieme: nei libri nuovi l'unica approvazione durante la scrittura è la tua risposta alla pausa di lettura. I file del livello editoriale e `CLAUDE.md` descrivono ancora le fermate di un tempo: il contrasto è segnalato in `docs/DA_VERIFICARE_AUTORE.md` (<span class="fonte">docs/DECISIONI_INTEGRAZIONE.md, D4 e D14</span>).

</div>

# 2. Organigramma: chi fa cosa {#cap2}

## Lo schema

<svg viewBox="0 0 320 470" xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans, sans-serif" role="img" aria-label="Organigramma del sistema">
<defs><marker id="fr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#444"/></marker></defs>
<rect x="60" y="4" width="200" height="46" rx="8" fill="#fbe9c8" stroke="#c98a1a" stroke-width="1.5"/>
<text x="160" y="24" text-anchor="middle" font-size="15" font-weight="bold">Felice (autore)</text>
<text x="160" y="42" text-anchor="middle" font-size="12">briefing; alla pausa: ok o correggi</text>
<line x1="160" y1="50" x2="160" y2="72" stroke="#444" stroke-width="1.5" marker-end="url(#fr)"/>
<rect x="60" y="74" width="200" height="46" rx="8" fill="#dbe7f3" stroke="#123d6a" stroke-width="1.5"/>
<text x="160" y="94" text-anchor="middle" font-size="15" font-weight="bold">Claude Code</text>
<text x="160" y="112" text-anchor="middle" font-size="12">orchestra, chiama gli agenti, lancia zb</text>
<rect x="4" y="142" width="150" height="62" rx="8" fill="#eef2f6" stroke="#123d6a"/>
<text x="79" y="162" text-anchor="middle" font-size="13" font-weight="bold">Regole</text>
<text x="79" y="180" text-anchor="middle" font-size="11.5">CLAUDE.md, PROCEDURA.md</text>
<text x="79" y="196" text-anchor="middle" font-size="11.5">editoriale/ (8 ruoli)</text>
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
<text x="160" y="270" text-anchor="middle" font-size="12">motore/zb, motore/script/</text>
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

<p class="fonte">Schema ricavato da CLAUDE.md, motore/editoriale/LEGGIMI.md, motore/dati/hook.yaml e motore/dati/hook-settings.esempio.json.</p>

## Chi fa cosa, in breve

| Chi | Che cosa fa | Dove sta |
|---|---|---|
| Felice | Scrive il briefing; alla pausa di lettura risponde ok o correggi; decide | — |
| Sessione principale (Claude Code) | Orchestra: chiama l'agente del passo, legge la sua risposta breve, lancia `zb`. **Non scrive prosa** | — |
| Ruoli e agenti | Fanno il lavoro editoriale | `motore/editoriale/` |
| Motore | Crea, controlla, compone, impagina | `motore/` |
| Regole | Dicono come si lavora | `CLAUDE.md`, `motore/PROCEDURA.md`, `motore/editoriale/` |
| Hook | Sorvegliano le scritture | `motore/script/hook_*.py`, `consumo.py` |
| Libro | Il lavoro vero | `libri/<slug>/` |

<p class="fonte">(CLAUDE.md; motore/editoriale/LEGGIMI.md; motore/editoriale/risparmio-token.md)</p>

## Gli otto ruoli editoriali

Ogni ruolo ha un file in `motore/editoriale/ruoli/`. Legge solo i file del suo «Input» e scrive un report in `06-diagnostica/` del libro. Non modifica il manoscritto, salvo chi scrive e chi corregge (<span class="fonte">motore/editoriale/LEGGIMI.md, «Regole»</span>).

| # | Ruolo | Lavoro | Fase |
|---|---|---|---|
| 0 | Diagnosta | dice cosa fa il testo e dove non funziona, senza riscrivere: `rapporto-struttura.md`, `rapporto-manoscritto.md` | `struttura`, `struttura_manoscritto` |
| 1 | Direttore editoriale | bibbia, schede del codex, cronologia, nota di direzione | `documenti` |
| 2 | Architetto della struttura | i nove file di `03-struttura/` | `struttura` |
| 3 | Scrittore con voce | pagina campione e capitoli | `pagina_campione`, `stesura` |
| 4 | Editor strutturale | trasforma la diagnosi in un piano di revisione: `piano-revisione-struttura.md`, `piano-revisione-manoscritto.md` | `struttura`, `struttura_manoscritto` |
| 5 | Line editor | frase per frase: ritmo, voce, ripetizioni, tic da IA | `line` |
| 6 | Correttore di italiano | grammatica, ortografia, punteggiatura, coerenza | `copy` |
| 7 | Correttore di bozze | ultimo controllo sul libro impaginato | `bozze` |

<p class="fonte">(motore/editoriale/ruoli/00-07; motore/script/percorso.py, FASI_RUOLO)</p>

`zb ruolo <libro> <ruolo> [N]` rifiuta un ruolo fuori dalla sua fase e dà la prima riga del rapporto, con l'impronta del testo rivisto (<span class="fonte">motore/script/ruolo.py</span>).

## Gli agenti

Gli agenti sono 12. In `motore/editoriale/agenti/` ce ne sono 10: uno per ruolo, più il **lettore cieco** (passo facoltativo) e la **capsula**. In `motore/editoriale/lingue/agenti/` ci sono i 2 della traduzione: traduttore e revisore di fedeltà (<span class="fonte">cartelle motore/editoriale/agenti/ e lingue/agenti/; zb agenti stato</span>).

- **Modelli.** Forte (opus): architetto, editor strutturale, diagnosta. Medio (sonnet): direttore, scrittore, line editor, correttore di italiano, correttore di bozze, lettore cieco, traduttore, revisore di fedeltà. Leggero (haiku): capsula. Fonte unica: `motore/dati/modelli-ruoli.yaml` (<span class="fonte">motore/dati/modelli-ruoli.yaml</span>).
- **In sequenza:** scrittore e traduttore, un capitolo per volta. **In parallelo:** line editor, correttore di italiano e capsula, al massimo 3 alla volta; con i limiti d'uso si scende a 2, poi a 1 (<span class="fonte">motore/dati/orchestrazione.yaml; motore/dati/modelli-ruoli.yaml</span>).
- **Chi chiamare ora:** `zb agenti prossimo <libro>`. Non scrive nulla (<span class="fonte">motore/script/agenti.py</span>).
- **Risposta breve:** ogni agente risponde con al massimo 10 righe e non fa commit né push (<span class="fonte">motore/dati/orchestrazione.yaml; motore/editoriale/agenti/</span>).
- **Il lettore cieco** legge un campione da lettore, in sola lettura, solo dopo il tuo ok (<span class="fonte">motore/editoriale/agenti/lettore-cieco.md; motore/dati/orchestrazione.yaml</span>).
- **Comandi di Claude Code:** `/scrivi-capitolo`, `/revisiona`, `/diagnosi`, `/handover` (<span class="fonte">motore/editoriale/comandi/</span>).
- **Accensione:** `zb agenti attiva --ok` copia agenti e comandi in `.claude/agents/` e `.claude/commands/`: 16 file, solo sui rami dei libri (<span class="fonte">motore/script/agenti.py; zb agenti stato</span>).

## Le capsule

Dopo ogni capitolo accettato: `zb capsula <libro> N` prepara `07-capsule/NN.md`, l'agente capsula la scrive, `zb capsula <libro> N --verifica` la controlla. Otto sezioni, da 120 a 250 parole (circa 180). Le promesse si scrivono con `@prom:<id>`; il registro segnala una promessa chiusa prima di essere aperta (<span class="fonte">motore/script/capsula.py</span>).

`zb esito` si ferma se manca la capsula del capitolo precedente. Con `capsule: obbligatorie` in `libro.yaml` si ferma anche `zb avvio`; senza il campo dà un avviso (<span class="fonte">motore/PROCEDURA.md §1b; motore/script/capsula.py; docs/DECISIONI_INTEGRAZIONE.md, D9</span>).

## Il motore: `zb` e gli script

`zb` è il comando unico. Si scrive `python3 motore/zb <comando> <libro>`. Il libro si indica sempre con il percorso della sua cartella. L'elenco dei comandi è uno solo, `motore/dati/comandi.yaml`: lo stampa `python3 motore/zb aiuto`, e `zb aiuto <comando>` dà l'uso (<span class="fonte">motore/PROCEDURA.md §11; motore/dati/comandi.yaml</span>).

Gli script sono 44 file in `motore/script/`. I comandi sono 47, in quattro gruppi (<span class="fonte">cartella motore/script/; motore/dati/comandi.yaml</span>):

- **Libro e fasi:** nuovo, adotta, avvio, stato, pronto, avanti, ok, correggi, esito, riapprova, fase, canone, revisione.
- **Percorso editoriale e agenti:** struttura, codex, prepara, capsula, compatto, ruolo, agenti, consumo, antiia, traduci.
- **Controlli e chiusura:** capitolo, conta, stile, continuita, riciclo, ortografia, languagetool, compila, impagina, pdf, pacchetto, kdp, verifica.
- **Recinto, salvataggio, motore:** lavoro, salva, push, cartella, hook, pulizia, voce, prove, separazione, recinto, profili.

Ogni comando stampa al massimo 40 righe e mette il resto in un file; le righe con KO, FERMO o ERRORE restano sempre a schermo (<span class="fonte">motore/dati/output.yaml</span>).

Nessun comando del motore fa commit o push da solo, tranne `zb salva` e `zb push` quando li si lancia (<span class="fonte">motore/PROCEDURA.md §8</span>).

## La «Bibbia editor»

«Bibbia editor» era il nome dato all'insieme delle regole editoriali: il commit `668afc2` si chiama «Bibbia editor: appendici e indice» (<span class="fonte">storia git</span>). Oggi quelle regole stanno in due posti:

- `motore/editoriale/`: percorso, ruoli, diagnosi, agenti, struttura, anti-IA, correttore, glossari;
- `motore/PROCEDURA.md`: la procedura completa.

Le aiutano alcuni file di dati, per esempio la lista nera di base (`motore/dati/lista-nera.yaml`) e le parole italiane ammesse (`motore/dati/parole-ammesse-it.txt`) (<span class="fonte">motore/editoriale/LEGGIMI.md; motore/PROCEDURA.md §7</span>).

<div class="nota">

Attenzione: la `bibbia.md` di ogni libro (personaggi, luoghi, fatti) è un'altra cosa. Sta nella cartella del libro, in `02-bibbia/` (<span class="fonte">motore/dati/struttura-libro.yaml</span>).

</div>

## Profili di genere

Un profilo dà i valori predefiniti di un genere: lunghezza, capitoli, scene, frase media, dialogo e soglie anti-IA (<span class="fonte">motore/PROCEDURA.md §3; motore/profili/</span>).

Sono 7, nella cartella `motore/profili/`: fantascienza, fantasy, giallo, narrativa letteraria, romance, thriller, young adult. Le soglie anti-IA dei profili sono una PROPOSTA, oggi uguale per tutti i generi (<span class="fonte">motore/profili/giallo.yaml, blocco anti_ia</span>).

Un valore del briefing fuori dal profilo è accettato solo con un «Motivo override:» scritto nel briefing. Senza motivo, `zb nuovo` si ferma (<span class="fonte">motore/PROCEDURA.md §3</span>).

## Voci narranti

Una voce dice **come** si racconta. Il **cosa** lo decide l'autore nel briefing (<span class="fonte">motore/README.md, «Banca-voci»</span>).

Le voci stanno in un repository separato, la banca-voci, mai dentro il motore. Il motore le legge in sola lettura dalla cartella indicata da `ZB_BANCA_VOCI`. I nomi delle voci stanno solo lì: questa guida non li scrive (<span class="fonte">motore/passaggio-di-consegne.md, «Stato»</span>).

Ogni voce ha una scheda in 7 sezioni e un elenco di espressioni vietate, `divieti.yaml`. `zb voce lista`, `zb voce mostra <slug>` e `zb voce verifica <slug>` le leggono (<span class="fonte">motore/README.md, «Banca-voci»</span>).

Un libro sceglie la voce nel briefing («Voce dalla banca:», «Ambientazione:»); `zb nuovo` la scrive in `libro.yaml`. Se il briefing contrasta con la voce, vince il briefing, e il contrasto si segnala (<span class="fonte">motore/README.md, «Banca-voci»; motore/editoriale/LEGGIMI.md</span>).

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

I modelli dei documenti della struttura stanno a parte, in `motore/editoriale/struttura/modelli/` (<span class="fonte">cartella motore/editoriale/struttura/modelli/; docs/DECISIONI_INTEGRAZIONE.md, D6</span>).

## Hook

Gli hook sono quattro, nel modello `motore/dati/hook-settings.esempio.json`. Gli effetti, uno per uno, sono nel capitolo 4.

| Hook | Quando | Cosa fa |
|---|---|---|
| sessione | all'inizio della sessione | Annota la sessione; non blocca mai |
| manoscritto | prima di scrivere in `04-manoscritto/` | Oggi **avvisa** se manca `zb avvio` |
| recinto | prima di ogni scrittura, anche via Bash, e prima di `git commit` e `git push` | **Blocca** |
| consumo | dopo le letture e le chiamate agli agenti | Annota, non blocca mai |

<p class="fonte">(motore/dati/hook-settings.esempio.json; motore/dati/hook.yaml; motore/script/hook_*.py; motore/script/consumo.py)</p>

Si accendono solo sui rami dei libri, con `zb hook attiva --ok`. Sul ramo `motore` sono spenti per scelta (<span class="fonte">motore/PROCEDURA.md §10</span>).

## CLAUDE.md

È il foglio delle regole di avvio. Sta nella radice del repository e Claude Code lo legge a ogni sessione. Ha al massimo 30 righe e nessun nome di libro: lo controlla una prova del motore (<span class="fonte">motore/script/prove.py, sezione CLAUDE.md</span>). Cosa dice: capitolo 4.

## Rami dei libri

Ogni libro vive su un ramo suo, nella cartella `libri/<slug>/`. Dettagli nel capitolo 5.

# 3. Il percorso di un libro {#cap3}

Dall'idea a KDP il percorso ha dodici passi. La tabella dice dove si ferma un libro **nuovo** del percorso editoriale, nel modo automatico (<span class="fonte">motore/editoriale/00-percorso.md; motore/script/nuovo.py; motore/script/percorso.py</span>).

| # | Passo | Chi lavora | Fermata dell'autore |
|---|---|---|---|
| 1 | Briefing | autore | — |
| 2 | Cartella unica `libri/<slug>/` | `zb nuovo` | — |
| 3 | Struttura: nove file | architetto della struttura | — |
| 4 | Revisione della struttura | diagnosta, poi editor strutturale | — (la controlla il motore) |
| 5 | Documenti: bibbia, codex, cronologia, manuale | direttore editoriale | — |
| 6 | Pagina campione | scrittore con voce | — |
| 7 | Stesura, un capitolo alla volta | scrittore, poi capsula | **pausa di lettura** ogni 3 capitoli e a fine stesura |
| 8 | Revisione strutturale del manoscritto | diagnosta, poi editor strutturale | — |
| 9 | Line editing | line editor | — |
| 10 | Copyediting | correttore di italiano | — |
| 11 | Bozze | correttore di bozze | — |
| 12 | Chiusura meccanica | motore | — |

Dopo il passo 8 c'è un **passo facoltativo**: il lettore cieco, solo con il tuo ok (<span class="fonte">motore/dati/orchestrazione.yaml</span>).

## Il modo automatico

- I libri nuovi del percorso editoriale nascono con `gate: [lettura]` e `pausa_lettura: 3` in `libro.yaml` (<span class="fonte">motore/script/nuovo.py</span>).
- La struttura la verifica il motore, sempre, senza la tua fermata: anche se `libro.yaml` elenca il gate `struttura` (<span class="fonte">motore/script/fase.py, gate_attivi; motore/script/percorso.py</span>).
- Nelle fasi di revisione (passi 8-11) un gate non elencato non ferma: le proposte si registrano e si passa all'applicazione (<span class="fonte">motore/script/percorso.py, pronto</span>).
- Restano due fermate che non sono approvazioni del lavoro: `controllo_fallito` (stesso controllo fallito due volte sullo stesso capitolo) e `canone` (cambiare i fatti bloccati è una tua richiesta) (<span class="fonte">docs/DECISIONI_INTEGRAZIONE.md, D6</span>).
- Un briefing può ancora chiedere dei gate, con la riga «Gate:». I libri nati prima e quelli del percorso breve non cambiano (<span class="fonte">motore/script/nuovo.py; docs/DECISIONI_INTEGRAZIONE.md, D6 e D11</span>).

## La pausa di lettura: cosa rispondi

Dopo `pausa_lettura` capitoli accettati da `zb esito`, e a fine stesura, il motore si ferma. Stampa «PAUSA DI LETTURA» con l'elenco dei file da leggere. Finché non rispondi, `zb esito` rifiuta altri capitoli (<span class="fonte">motore/script/fase.py, apri_pausa e cmd_esito</span>).

Leggi i capitoli nei file. Poi rispondi in uno di due modi (<span class="fonte">motore/script/fase.py, chiudi_pausa, cmd_ok, cmd_correggi</span>):

- **ok**: Claude Code lancia `zb ok <libro>`. I capitoli sono registrati come letti, con impronta e commit, e la scrittura riparte.
- **correggi** con le tue note: Claude Code lancia `zb correggi <libro> <note>`. Le note vanno in `06-diagnostica/note-lettura.md` e in `stato.yaml` (`note_lettura`), poi la scrittura riparte. Le note valgono per i capitoli successivi: `zb prepara` le mette tra i file che lo scrittore legge.

Altre cose da sapere:

- Non servono blocchi da mostrare in chat: l'«ok» non chiede di aver visto i blocchi, perché leggi i file. Se li vuoi comunque, `zb avanti` li mostra (<span class="fonte">docs/DECISIONI_INTEGRAZIONE.md, D11</span>).
- Un capitolo già scritto si corregge a parte, con `zb correggi <libro> <unità>: <motivo>` (<span class="fonte">docs/DECISIONI_INTEGRAZIONE.md, D11; motore/PROCEDURA.md §5</span>).
- Valori ammessi per `pausa_lettura`: 3, 4 o 5. Con un altro valore ogni comando si ferma e lo dice (<span class="fonte">motore/dati/libro.schema.yaml</span>).

## Prima di ogni sessione: `zb avvio`

A ogni sessione, e dopo ogni compattazione della memoria di Claude Code, si lancia `zb avvio <libro> [--ruolo R]`. Si ferma senza scrivere nulla se qualcosa non va: modifiche non salvate, ramo sbagliato, ramo non allineato a GitHub, un documento approvato cambiato di nascosto, file cambiati fuori dal libro, un altro libro attivo, un secondo ruolo nella stessa sessione (<span class="fonte">motore/script/avvio.py; motore/PROCEDURA.md §4</span>).

Se tutto va bene stampa la riga «Letto: …», con i file letti, le righe e le impronte; il file del ruolo entra nella riga. Claude Code la riporta prima di scrivere. Nelle sessioni nuove si legge lo stato compatto del libro (15-20 righe) e la scheda del capitolo (<span class="fonte">motore/script/avvio.py; CLAUDE.md</span>).

**Un ruolo per sessione.** Senza `--ruolo` vale quello della fase. Per cambiare ruolo: salvare, aprire una sessione nuova, `zb avvio` (<span class="fonte">motore/script/ruolo.py; motore/editoriale/00-percorso.md</span>).

## Passi 1-2. La nascita

1. Sul ramo del libro, mai sul ramo `motore`, l'autore compila il modello `motore/modelli/briefing.md`.
2. Claude Code lancia `zb nuovo <briefing>`.
3. Se il briefing è incompleto, `zb nuovo` elenca al massimo 5 cose mancanti e **non crea nulla**.
4. Se è completo, crea la cartella `libri/<slug>/` con `libro.yaml`, `stato.yaml`, `LEGGIMI.md`, `nomi_propri.txt`, e in `03-struttura/` i nove modelli della struttura. Bibbia, codex, cronologia e manuale nascono dopo, quando il motore chiude la struttura.

Per un libro che ha già dei documenti c'è `zb adotta`: prepara delle bozze con la fonte di ogni valore (<span class="fonte">motore/script/nuovo.py; motore/PROCEDURA.md §3 e §3b</span>).

## Passi 3-4. Struttura e sua verifica

L'architetto scrive nove file in `03-struttura/`: premessa, logline e tema, personaggi chiave, atti e svolte, scaletta, sottotrame e temi, tensione e ritmo, piano parole, scelte fisse (<span class="fonte">motore/editoriale/struttura/01-fase-struttura.md</span>).

Poi, in sessioni separate: il diagnosta scrive `06-diagnostica/rapporto-struttura.md`; l'editor strutturale scrive `06-diagnostica/piano-revisione-struttura.md`. I rapporti stanno in commit che non toccano `03-struttura/` (<span class="fonte">motore/editoriale/struttura/01-fase-struttura.md; motore/editoriale/00-percorso.md</span>).

`zb pronto` verifica tutto: i nove file senza la riga di modello, macrostruttura dichiarata e motivata, schede complete, rapporti con l'impronta della struttura attuale. Se regge, registra i file, crea i documenti e passa a «documenti», senza fermata. Se no, si ferma e scrive il motivo (<span class="fonte">motore/script/percorso.py, pronto; motore/PROCEDURA.md §1b</span>).

## Passi 5-6. Documenti e pagina campione

| Fase | Lavoro | Controllo di `zb pronto` |
|---|---|---|
| documenti | bibbia, schede del codex, cronologia, manuale; `06-diagnostica/nota-direzione.md` | `zb codex verifica`; senza la nota di direzione si ferma |
| pagina campione | `05-revisioni/pagina-campione.md` | pagina non vuota |

<p class="fonte">(motore/PROCEDURA.md §1b; motore/script/percorso.py, documenti_gate; docs/DECISIONI_INTEGRAZIONE.md, D12)</p>

## Passo 7. La stesura

Per ogni capitolo, la sessione principale chiama l'agente scrittore, mai due capitoli in parallelo (<span class="fonte">motore/editoriale/agenti/scrittore-voce.md; motore/PROCEDURA.md §1b e §6</span>):

1. `zb prepara <libro> N`: scheda, schede del codex della scena, canone, capsule e, dopo una pausa di lettura con note, le tue note;
2. lo scrittore scrive `04-manoscritto/NN-<slug>.md`;
3. `zb esito <libro> N`: parole, stile, continuità, audit anti-IA, lunghezze quasi uguali, capsula precedente;
4. `zb capsula <libro> N`, l'agente capsula, poi `--verifica`;
5. salvataggio con `zb salva`.

Il comando `/scrivi-capitolo N` fa questo giro e si ferma dopo il salvataggio (<span class="fonte">motore/editoriale/comandi/scrivi-capitolo.md</span>).

Se un controllo fallisce: **una sola** correzione mirata, poi di nuovo `zb esito`. Al secondo fallimento di fila sullo stesso capitolo si apre `controllo_fallito`: decidi tu, con `ok` (accetti il capitolo così) o `correggi: …` (<span class="fonte">motore/PROCEDURA.md §6</span>).

Ogni `pausa_lettura` capitoli c'è la pausa di lettura. Scritte tutte le unità del piano, la fase passa a «struttura_manoscritto» (<span class="fonte">motore/script/fase.py, dopo_capitolo; motore/script/percorso.py, dopo_stesura</span>).

## Passi 8-11. Le revisioni

Ogni fase di revisione ha due tempi: prima i **rapporti** (proposte), poi l'**applicazione** con modifiche puntuali e `zb esito N` sui capitoli toccati; `zb pronto` passa alla fase dopo. Ogni rapporto comincia con la riga data da `zb ruolo` e sta in un commit che non tocca il testo rivisto (<span class="fonte">motore/PROCEDURA.md §1b; motore/script/percorso.py</span>).

| Fase | Chi | Report |
|---|---|---|
| struttura_manoscritto | diagnosta, poi editor strutturale | `rapporto-manoscritto.md`, `piano-revisione-manoscritto.md` |
| line | line editor, per capitolo (fino a 3 in parallelo) | `06-diagnostica/line/NN.md` |
| copy | correttore di italiano, per capitolo | `06-diagnostica/copy/NN.md` |
| bozze | `zb compila`, `zb impagina`, poi correttore di bozze | `06-diagnostica/bozze.md` |

<p class="fonte">(motore/PROCEDURA.md §1b; motore/editoriale/ruoli/04-07; motore/editoriale/agenti/)</p>

Un revisore non può riscrivere per intero un capitolo che esiste: l'hook rifiuta la riscrittura, si corregge con modifiche puntuali (<span class="fonte">motore/script/hook_recinto.py</span>). Il comando `/revisiona N` chiama line editor o correttore secondo la fase (<span class="fonte">motore/editoriale/comandi/revisiona.md</span>).

## Passo 12. La chiusura meccanica

L'ordine è fisso: continuita, ortografia, compila, impagina, pdf, pacchetto, kdp, pronto. `pacchetto` va prima di `kdp`: il controllo KDP legge la scheda del pacchetto (<span class="fonte">motore/PROCEDURA.md §7</span>).

### Chiusura 1: `zb continuita`

- **Cosa fa.** Controlla giorni della settimana, età dei personaggi, durate, cifre, nomi scritti in due modi, ordine delle date.
- **Cosa serve prima.** I capitoli e il file `cronologia.yaml` del libro.
- **Cosa produce.** `06-diagnostica/continuita.md`, con la lista di controllo per capitolo.

<p class="fonte">(motore/script/continuita.py)</p>

### Chiusura 2: `zb ortografia`

- **Cosa fa.** Tre livelli: (a) Hunspell, sempre; (b) LanguageTool, solo se `ZB_LANGUAGETOOL` indica i suoi file; (c) una lista di controllo per la lettura umana, sempre, presa dalle sezioni 1-6 dei criteri del correttore.
- **Cosa serve prima.** Hunspell con il dizionario italiano; le parole ammesse del libro (`nomi_propri.txt`).
- **Cosa produce.** `06-diagnostica/controllo-ortografico.md`. Dice quali livelli sono stati eseguiti.

<p class="fonte">(motore/script/ortografia.py)</p>

### Chiusura 3: `zb compila`

- **Cosa fa.** Mette insieme il libro: frontespizio, copyright, sommario, parti, capitoli in ordine, appendici. Il sommario lo genera sempre il motore.
- **Cosa serve prima.** `libro.yaml` e i capitoli; le appendici dichiarate.
- **Cosa produce.** `05-output/<titolo>-completo.md`.

<p class="fonte">(motore/script/compila.py)</p>

### Chiusura 4: `zb impagina`

- **Cosa fa.** Il PDF di stampa con Chromium: margini dalla tabella KDP, pagine iniziali senza numero, sommario con le pagine vere, formato esatto della pagina, metadati Title e Author.
- **Cosa serve prima.** Il file compilato; Chromium e PyMuPDF.
- **Cosa produce.** `05-output/<titolo>.pdf`.

<p class="fonte">(motore/script/impagina.py)</p>

### Chiusura 5: `zb pdf`

- **Cosa fa.** Verifica il PDF: pagine, Title e Author uguali a `libro.yaml`, font incorporati, margini contro i minimi KDP, voci del sommario sulla pagina giusta.
- **Cosa serve prima.** Il PDF; gli strumenti `pdfinfo`, `pdffonts`, `pdftotext`.
- **Cosa produce.** `06-diagnostica/verifica-pdf.md`.

<p class="fonte">(motore/script/verifica_pdf.py)</p>

### Chiusura 6: `zb pacchetto`

- **Cosa fa.** Prepara la cartella per KDP con modelli compilati dai dati di `libro.yaml`. **Non** scrive testi commerciali (descrizione, quarta, parole chiave, categorie). Non sovrascrive mai un file che c'è già.
- **Cosa produce.** In `06-pubblicazione/`: `scheda-amazon.md`, `quarta.md`, `brief-copertina.md`, `conferme-autore.yaml`, `promemoria-ai.md`, `checklist.md`.

<p class="fonte">(motore/script/pacchetto.py)</p>

### Chiusura 7: `zb kdp`

- **Cosa fa.** Controlla la conformità a KDP in 15 sezioni. Ciò che deve confermare l'autore, finché non è confermato, risulta KO.
- **Cosa serve prima.** `libro.yaml`, la scheda del pacchetto, il compilato, il PDF, `conferme-autore.yaml`, i dati KDP del motore.
- **Cosa produce.** `06-pubblicazione/conformita-kdp.md`, una riga OK/KO per sezione.

<p class="fonte">(motore/script/conformita_kdp.py)</p>

### Chiusura 8: `zb pronto`

- **Cosa fa.** Controlla che ci siano tutti i risultati dei passi 1-7. Se sì, il libro passa a «chiuso»; se no, elenca cosa manca e con quale comando farlo.

<p class="fonte">(motore/script/fase.py, elenco CHIUSURA; motore/PROCEDURA.md §7)</p>

<div class="nota">

**Prima di pubblicare.** I dati KDP del motore non sono mai stati riverificati dall'autore (`ultima_verifica: null`). La verifica si registra con `zb verifica KDP fatta AAAA-MM-GG` (<span class="fonte">motore/dati/kdp.yaml; motore/report-motore.md §11</span>).

</div>

## Libri con le fermate di un tempo

I libri del percorso breve, quelli nati prima e quelli che chiedono dei gate nel briefing si fermano ancora ai loro gate. Il gate si apre con `zb pronto` e mostra i documenti a blocchi di circa 120 righe. Le risposte (<span class="fonte">motore/PROCEDURA.md §5</span>):

- **avanti**: il blocco dopo. Non approva nulla.
- **ok**: approva. Vale solo se hai visto tutti i blocchi.
- **ok, lotti da N**: approva e fissa quanti capitoli scrivere di fila.
- **correggi: …**: registra una correzione; la fermata resta aperta.
- **stato**: mostra lo stato, senza cambiare nulla.

Qualunque altra frase è una domanda: non cambia lo stato (<span class="fonte">motore/PROCEDURA.md §5</span>).

## La traduzione

`zb traduci <libro> --a en inizia` crea il libro di traduzione in `08-traduzione-<lingua>/`: guida → stesura → line → copy → fedeltà → chiusura. Qui le fermate restano: guida e glossario si approvano al gate «guida» prima del capitolo 1, e ci sono i gate `line`, `copy`, `fedelta` (<span class="fonte">motore/PROCEDURA.md §1b; motore/script/traduci.py</span>). KDP chiede di dichiarare una traduzione fatta con l'IA; per un'edizione in vendita è consigliata la lettura finale di un madrelingua (<span class="fonte">motore/editoriale/lingue/traduzione.md</span>).

## Dopo ogni passo: il salvataggio

`zb salva <libro> "<messaggio>"`: controlla che nessun file stia fuori dal recinto, rigenera lo stato compatto, fa commit e push con ripiego; poi `git status -sb` e `git log -1`. Se il push fallisce, ci si ferma e si riporta l'errore. Mai dire «fatto» se il lavoro non è su GitHub (<span class="fonte">motore/script/salva.py; motore/PROCEDURA.md §8; CLAUDE.md</span>).

# 4. Le regole {#cap4}

## Cosa dice CLAUDE.md

In parole semplici (<span class="fonte">CLAUDE.md</span>):

1. **Regola madre.** Il motore resta pulito; il ramo `motore` non contiene mai un libro.
2. **Briefing nuovo:** prima azione `zb nuovo`, che apre una sola cartella del libro. Da lì si scrive solo in quella cartella.
3. **Recinto.** Hook, controllo prima del commit e `zb avvio` rifiutano i file fuori dal libro attivo. Solo se scrivi «lavoro sul motore», Claude Code lancia `zb lavoro motore`.
4. **Letture.** Per un libro: `motore/PROCEDURA.md` e il `LEGGIMI.md` del libro; se manca il percorso, Claude Code lo chiede. `docs/` non si legge durante il lavoro.
5. **Avvio.** Prima di scrivere: `zb avvio <libro>` e la riga «Letto». Se si ferma, Claude Code si ferma e dice perché.
6. **Cosa legge il motore:** solo `motore/`, la cartella del libro e la banca-voci (sola lettura).
7. **Orchestrazione.** La sessione principale non scrive prosa: chiama l'agente del ruolo, un subagente per capitolo. Chi scrive non rivede.
8. **Report di sessione** ogni 5 scambi o quando scrivi «passaggio», nella cartella del libro, con sette sezioni fisse.
9. **Precedenza:** una sola scala, in `motore/editoriale/LEGGIMI.md`; ogni contrasto si segnala.
10. **Metodo:** proponi, l'autore approva, applica. Mai approvare da solo.
11. **Risposte dell'autore:** ok, avanti, correggi, stato. **Ramo:** quello della sessione, letto da git.
12. **Salvataggio** a ogni passo con `zb salva`, poi `git status -sb` e `git log -1`. Resoconto con codice, file e «branch allineato a origin: sì/no».

## Gli hook, uno per uno

### Il recinto: blocca

- **Cosa guarda.** Ogni scrittura di file (Write, Edit, MultiEdit, NotebookEdit) e i comandi di shell (Bash): redirezioni, `tee`, `sed -i`, `perl -i`, `cp`, `mv`, `rm`, `touch`, `mkdir` e altri.
- **Regola.** Si può scrivere solo in `libri/<slug-attivo>/`. Il resto è rifiutato.
- **Prima di `git commit` e `git push`** controlla la cartella unica: un commit che tocca il libro e altro è bloccato.
- **Revisori.** Un revisore non può riscrivere per intero un capitolo esistente: solo modifiche puntuali.
- **Chi scrive.** Annota chi scrive in `.zb/scritture.log` del libro, per la separazione dei ruoli.
- **Libro attivo.** Sta nella cartella interna di git (`zb-libro-attivo`), non in un file salvato; i rami creati prima usano ancora `libri/libro-attivo.md`.
- **Lavoro sul motore.** Con `zb lavoro motore` si può scrivere nel repository, ma non in `libri/`.

<p class="fonte">(motore/script/hook_recinto.py; motore/PROCEDURA.md §10)</p>

**Limiti dichiarati.** Su Bash il recinto non vede tutto: script che scrivono senza nominare il percorso, variabili o `cd` di comandi precedenti, `$(…)`, strumenti non elencati (`awk -i inplace`, `find -delete`, `xargs rm`). Li coprono il controllo di git prima di ogni commit, `zb avvio` e `zb salva` (<span class="fonte">motore/PROCEDURA.md §10</span>).

### Il manoscritto: avvisa

Se si scrive in `04-manoscritto/` senza `zb avvio` in quella sessione, stampa «ATTENZIONE: …», lo annota in `.zb/avvisi-hook.log` e lascia passare. La modalità sta in `motore/dati/hook.yaml`: oggi `avviso`. Il passaggio a `blocco` è un commit a parte, dopo il tuo ok (<span class="fonte">motore/script/hook_manoscritto.py; motore/dati/hook.yaml</span>).

### La separazione dei ruoli: blocca

Chi ha scritto un testo non lo revisiona nella stessa sessione. In `motore/dati/hook.yaml` la scelta è `separazione_ruoli: blocco`: il motore **si ferma** al `zb pronto` delle fasi con rapporti e all'avvio di un ruolo di revisione. Puoi tornare ad `avviso` con un commit a parte. Una sessione che ha già un ruolo non ne prende un altro (<span class="fonte">motore/dati/hook.yaml; motore/script/ruolo.py</span>).

### La sessione e il consumo

L'hook di sessione scrive il codice della sessione; dopo una compattazione, i vecchi «avvio fatto» non valgono più (<span class="fonte">motore/script/hook_sessione.py</span>). L'hook di consumo annota in `.zb/letture.log` i file letti e gli agenti chiamati; `zb consumo <libro>` ne fa il riassunto per sessione. Misura righe e parole lette, non i token (<span class="fonte">motore/script/consumo.py</span>).

### Come si accendono

`zb hook attiva` mostra cosa scriverebbe; `zb hook attiva --ok`, solo dopo il tuo ok, crea `.claude/settings.json`. `zb hook stato` dice se sono accesi; `zb hook disattiva` li spegne (<span class="fonte">motore/PROCEDURA.md §10</span>).

## La cartella unica

Tutto ciò che riguarda un libro vive in `libri/<slug>/`. `zb cartella <libro>` controlla su git, e lo fanno da soli anche `zb avvio`, `zb push` e l'hook prima di commit e push (<span class="fonte">motore/script/cartella_unica.py</span>):

- file modificati fuori dal libro;
- commit «misti», che toccano il libro e altro;
- titolo del libro in file fuori dalla sua cartella.

Le eccezioni sono in `motore/dati/cartella-unica.yaml`: `CLAUDE.md`, `.gitignore`, `libri/libro-attivo.md`, `.claude/settings.json`, `.claude/agents/`, `.claude/commands/`, e i merge del motore. I commit misti già fatti li dichiari tu, con il motivo: la storia non si riscrive (<span class="fonte">motore/dati/cartella-unica.yaml</span>).

## `zb push` e le prove sul motore

`zb push` fa il push del ramo corrente; se fallisce riprova, poi tenta un ramo alternativo, poi un `git bundle`. Sul ramo di un libro controlla prima la cartella unica. Sul **lavoro del motore** vuole una `zb prove` intera e tutta OK sullo stato attuale: le prove lasciano un'impronta, e senza quell'impronta il push non parte (<span class="fonte">motore/script/push.py; motore/script/prove.py</span>).

Al punto 9 dell'integrazione le prove erano 632, tutte OK; al punto 8b, 633; al punto 12, 637 (<span class="fonte">docs/DECISIONI_INTEGRAZIONE.md, D12, D15 e D16</span>).

## Altre protezioni, senza hook

| Chi | Cosa fa |
|---|---|
| Codice del motore | Ogni comando scrive solo nella cartella del libro |
| `zb nuovo` | Rifiuta un libro sul ramo `motore`, dentro `motore/` o nella radice |
| Controllo di git prima del commit | Rifiuta file fuori dal recinto, chiunque li abbia scritti |
| `zb recinto` | Prova che i comandi non scrivano fuori dal libro |
| `zb separazione` | Prova che il motore, `docs/` e `CLAUDE.md` non contengano libri né nomi vietati |

<p class="fonte">(motore/script/nuovo.py; motore/script/precommit.py; motore/script/recinto.py; motore/script/separazione.py)</p>

## La precedenza

Quando due regole si contraddicono, vince quella più in alto. Una sola scala (<span class="fonte">motore/editoriale/LEGGIMI.md</span>):

1. manuale del libro e `libro.yaml`;
2. briefing e scheda della voce (se contrastano vince il briefing, e si segnala);
3. profilo di genere;
4. `motore/editoriale/` (ruoli);
5. procedura del motore.

Il catalogo anti-IA e i criteri del correttore sono filtri: non stanno sopra il manuale. **Ogni contrasto si segnala** (<span class="fonte">motore/editoriale/LEGGIMI.md; CLAUDE.md</span>).

# 5. I rami {#cap5}

## Il ramo `motore`

- Solo il motore: codice, regole, mini-libri inventati, e `docs/` con i documenti di lettura.
- Mai un libro, mai un nome di libro, di ramo di libro o di autore reale, anche in `docs/` e in `CLAUDE.md` (lo controlla `zb separazione`).
- Qui hook, agenti e comandi sono spenti; `zb avvio` senza libro lo verifica.
- Qui `zb nuovo` e `zb lavoro libro` si rifiutano.

<p class="fonte">(motore/passaggio-di-consegne.md, «Regole da non violare»; motore/PROCEDURA.md §4 e §10; motore/script/hook_recinto.py)</p>

## I rami dei libri

- Un libro per ramo, nella cartella `libri/<slug>/`.
- Ogni ramo porta una copia di `motore/`. Il motore aggiornato arriva con un merge: è l'unica eccezione che il controllo prima del commit ammette (<span class="fonte">motore/script/precommit.py</span>).
- Con hook e agenti accesi ci sono anche `.claude/settings.json`, `.claude/agents/`, `.claude/commands/`.
- I libri vecchi hanno il loro `CLAUDE.md` per tua scelta e non si toccano (<span class="fonte">motore/passaggio-di-consegne.md, «Regole da non violare»; motore/dati/cartella-unica.yaml</span>).

## I rami d'archivio

Esistono rami d'archivio. Per esempio, il ramo `motore` ha copiato `pulizia.py` su un ramo d'archivio prima di toglierlo; in questo ramo integrato `zb pulizia` c'è ancora, con le sue prove. I nomi dei rami d'archivio non si scrivono qui: lo vieta `separazione.py` (<span class="fonte">docs/ANALISI_REPOSITORY.md, tabella degli script; docs/DECISIONI_INTEGRAZIONE.md, D12 e D13</span>).

## Il ramo dell'integrazione

`integrazione-editoriale` sta su `NGTAProtocol/ZeusBot`. Parte dal ramo di sessione `ccr-d1e12273-izx78k` (`d2b8814`) e riprende dal ramo `motore` (`971b6df`) ciò che mancava. I rami `motore` e `main` non sono stati toccati; in questo repository un ramo `main` non esiste (<span class="fonte">docs/DECISIONI_INTEGRAZIONE.md, introduzione, D1 e D2</span>).

# 6. Cosa c'è e cosa non esiste {#cap6}

## Cosa c'è

- **Subagenti e comandi** di Claude Code: 12 agenti e 4 comandi, accesi sui rami dei libri con `zb agenti attiva --ok` (capitolo 2).
- **Anti-IA.** `zb esito` e `zb antiia` misurano e non riscrivono: variazione delle frasi, aperture uguali, formule per mille parole, lineette nella narrazione, varietà lessicale, chiusure uguali; in più le formule di `motore/editoriale/anti-ia/formule.yaml`, la coerenza tipografica e le ripetizioni ravvicinate. Gravità P0, P1, P2. Le soglie stanno in `motore/dati/antiia.yaml`, poi nel profilo di genere, poi in `libro.yaml`. Con `anti_ia: {modalita: blocco}` ogni segnalazione diventa un KO (<span class="fonte">motore/script/antiia.py; motore/dati/antiia.yaml</span>).
- **Correttore di italiano**: il ruolo 6 e i criteri in `motore/editoriale/correttore/criteri-correttore.md`, insieme a `zb ortografia` (<span class="fonte">motore/editoriale/ruoli/06-correttore-italiano.md</span>).
- **LanguageTool**: un solo comando, `zb languagetool installa | verifica | stato`. Si installa fuori dal repository, da Maven Central, mai da languagetool.org (<span class="fonte">motore/script/languagetool.py</span>).
- **Inglese**: «Lingua: en» nel briefing; stesse fasi e stessi ruoli, con i profili di `motore/editoriale/lingue/en/` (<span class="fonte">motore/PROCEDURA.md §1b</span>).
- **Comandi di controllo singoli**: `zb conta`, `zb stile`, `zb riciclo`, `zb capitolo`, `zb pulizia` restano, oltre a `zb esito` (<span class="fonte">motore/dati/comandi.yaml; docs/DECISIONI_INTEGRAZIONE.md, D12</span>).

## Cosa non esiste

- **Skill di Claude Code** (`.claude/skills/`): non si usano. Agenti e comandi vanno in `.claude/agents/` e `.claude/commands/`; il livello editoriale sostituisce ogni skill citata ma assente (<span class="fonte">motore/script/agenti.py; motore/editoriale/LEGGIMI.md, «Regole», punto 1</span>).
- **Vocabolario anti-IA italiano**: i livelli L1-L3 sono vuoti finché non si estraggono dai dati con `zb antiia estrai` (<span class="fonte">motore/dati/antiia.yaml</span>).
- **Nomi vietati**: `motore/dati/nomi_vietati.txt` non ha voci. Titoli, personaggi e luoghi dei libri veri li aggiungi tu; da solo `zb separazione` ricava, senza scriverli, i nomi dei rami di libro su origin e gli slug della banca-voci (<span class="fonte">motore/dati/nomi_vietati.txt; motore/report-motore.md §11, punto 10</span>).
- **Un controllo automatico a ogni modifica** sul repository: non c'è. Le prove si lanciano con `zb prove`; sul lavoro del motore le lancia `zb salva` prima del commit (<span class="fonte">nessuna cartella .github/; motore/script/salva.py</span>).
- **Un ambiente che resti** da una sessione all'altra: in un container nuovo si reinstallano i requisiti (<span class="fonte">motore/report-motore.md §11, punto 9</span>).

# 7. Appendici e indice {#cap7}

<div class="nota">

Il motore **include** le appendici dal commit `71a36cc` («Motore: appendici dichiarate in libro.yaml e sommario completo», 14 ottobre 2026). Le regole sono in `motore/PROCEDURA.md` §7 (<span class="fonte">storia git; motore/script/compila.py</span>).

</div>

**Appendici.** Sono i materiali dopo l'ultima unità del libro, epilogo compreso: soluzioni di enigmi, mappe, glossari, note (<span class="fonte">motore/PROCEDURA.md §7</span>).

- Stanno nella cartella `05-appendici/` del libro (<span class="fonte">motore/dati/struttura-libro.yaml</span>).
- Si dichiarano in `libro.yaml`, campo `appendici`, nell'ordine di lettura: titolo, file, didascalia per le immagini.
- Formati: testo `.md`; immagini `.svg`, `.png`, `.jpg`. Un `.svg` diventa PNG con Chromium.
- Ogni appendice comincia su una pagina nuova.
- Un file dichiarato e assente ferma `zb compila`. Un file presente ma non dichiarato dà solo un avviso e resta fuori.
- Le appendici non vanno mai in `04-manoscritto/`.
- Un'appendice non anticipa nulla: le soluzioni stanno solo in appendice.
- Un libro senza il campo `appendici` si compila come prima.

<p class="fonte">(motore/PROCEDURA.md §7; motore/script/compila.py)</p>

**Indice (sommario).** Lo genera `zb compila`, sempre. Non si scrive a mano.

- Contiene, in ordine: parti, prologo, capitoli («N. Titolo»), interludi, epilogo, appendici.
- `zb impagina` aggiunge la pagina vera di ogni voce; `zb pdf` controlla che sia giusta.
- Per cambiare una voce si cambia la sua fonte (titolo del capitolo, `libro.yaml`), poi si rilancia `zb compila`.

<p class="fonte">(motore/PROCEDURA.md §7)</p>

# 8. Punti deboli e decisioni aperte {#cap8}

Sono i limiti noti di `motore/report-motore.md` §11, le scelte in attesa di `docs/DA_VERIFICARE_AUTORE.md` e di `docs/DA_FORNIRE.md`. L'ordine, dal più serio al più lieve, è una valutazione di questa guida.

## Importanti: prima di pubblicare o fidarsi

1. **Dati KDP mai verificati da te.** In `motore/dati/kdp.yaml` c'è `ultima_verifica: null`. Vanno controllati sulle pagine ufficiali e registrati con `zb verifica KDP fatta AAAA-MM-GG`.
2. **Soglie anti-IA provvisorie.** Sono tarate sui mini-libri di prova, non su prosa umana, e nei profili sono una PROPOSTA uguale per tutti i generi (<span class="fonte">motore/dati/antiia.yaml; motore/profili/</span>).
3. **Gli hook non vedono tutto** su Bash (capitolo 4). Restano il controllo di git, `zb avvio`, `zb salva` e `zb push`.
4. **La separazione dei ruoli distingue le sessioni solo con l'hook di sessione** (o con `ZB_SESSIONE`). Con la sessione «locale» dà solo un avviso (<span class="fonte">motore/script/ruolo.py</span>).
5. **Il lavoro si perde se non è su origin.** L'ambiente non è persistente: in un container nuovo vanno reinstallati PyMuPDF, markdown, Hunspell e LanguageTool.

## Medi: misure e controlli incompleti

6. **Il consumo misura le letture, non i token.** Le prove controllano che con le capsule si leggano meno parole; le cifre misurate sui mini-libri dei due rami (1.127 parole con le capsule e 1.694 senza; 796 con e 2.444 senza) non sono state rifatte nell'integrazione (<span class="fonte">motore/report-motore.md §11, punto 6</span>).
7. **La continuità ha limiti.** I tempi relativi si controllano solo se nessuna data nota coincide; le differenze d'età solo per i personaggi con data di nascita completa.
8. **PDF: TrimBox e BleedBox non sono scritti;** trasparenze e immagini non sono controllate.
9. **I mini-libri sotto le 24 pagine** hanno la sezione 11 della conformità KDP in KO per costruzione.

## Scelte tue ancora aperte

10. **Il pacchetto editoriale e `CLAUDE.md` descrivono ancora le fermate con l'ok** (`00-percorso.md`, la fase struttura, «solo dopo il mio ok» nei ruoli; in `CLAUDE.md` «proponi → l'autore approva → applica» e la riga di avvio senza `--ruolo`), mentre il motore scrive in automatico. Se vuoi, aggiorna quei file (<span class="fonte">docs/DA_VERIFICARE_AUTORE.md</span>).
11. **Sezione B del catalogo anti-IA.** Le sue formule stanno in `formule.yaml` ma non si contano finché `formule_sezione_b: false` (<span class="fonte">motore/dati/antiia.yaml; docs/DA_VERIFICARE_AUTORE.md</span>).
12. **Coppia «avvenire/avvenire»** nei criteri del correttore, sezione 5: forse un refuso, non toccata.
13. **Licenza di APODICTIC** (CC BY-NC-SA 4.0): nessun testo copiato.
14. **Corpus per il vocabolario anti-IA italiano**: servono prosa scritta da un modello e prosa umana dello stesso genere (<span class="fonte">docs/DA_FORNIRE.md</span>).
15. **Separazione dei ruoli in blocco** e **capsule** con avviso (o `obbligatorie` in `libro.yaml`): sono scelte fatte per te; puoi cambiarle (<span class="fonte">motore/dati/hook.yaml; motore/script/capsula.py</span>).
16. **File aggiunti dal ramo `motore`**, adattati ai nomi del pacchetto: vanno letti prima di considerarli tuoi (<span class="fonte">docs/DA_VERIFICARE_AUTORE.md</span>).

## Lievi

17. **La storia git contiene ancora i riferimenti tolti** e i documenti spostati sui rami d'archivio: non si riscrive (<span class="fonte">motore/report-motore.md §11, punto 13</span>).

<p class="fonte">(motore/report-motore.md §11; docs/DA_VERIFICARE_AUTORE.md; docs/DA_FORNIRE.md)</p>

# 9. Dove trovare le cose {#cap9}

Ramo «motore» vuol dire anche: nella copia del motore di ogni ramo di libro aggiornato.

| Cosa cerchi | File | Ramo |
|-------|----------|-----|
| Regole di avvio | `CLAUDE.md` | motore (ogni ramo di libro ha il suo) |
| Procedura completa | `motore/PROCEDURA.md` | motore |
| Percorso e fermate | `motore/editoriale/00-percorso.md` | motore |
| Precedenza e regole editoriali | `motore/editoriale/LEGGIMI.md` | motore |
| Gli otto ruoli | `motore/editoriale/ruoli/` | motore |
| Diagnosi: principi e rapporto | `motore/editoriale/diagnosi/` | motore |
| Gli agenti | `motore/editoriale/agenti/`, `lingue/agenti/` | motore |
| Comandi di Claude Code | `motore/editoriale/comandi/` | motore |
| Modelli degli agenti | `motore/dati/modelli-ruoli.yaml` | motore |
| Orchestrazione e parallelo | `motore/dati/orchestrazione.yaml` | motore |
| Fase struttura e suoi modelli | `motore/editoriale/struttura/` | motore |
| Anti-IA | `motore/editoriale/anti-ia/`, `motore/dati/antiia.yaml` | motore |
| Criteri del correttore | `motore/editoriale/correttore/criteri-correttore.md` | motore |
| Glossari | `motore/editoriale/glossario.md`, `lingue/it/glossario-editoriale.md` | motore |
| Risparmio di token | `motore/editoriale/risparmio-token.md` | motore |
| Elenco dei comandi | `python3 motore/zb aiuto`; `motore/dati/comandi.yaml` | motore |
| Stato del lavoro sul motore | `motore/passaggio-di-consegne.md` | motore |
| Limiti noti del motore | `motore/report-motore.md` §11 | motore |
| Scelte dell'integrazione | `docs/DECISIONI_INTEGRAZIONE.md` | integrazione |
| Da verificare e da fornire | `docs/DA_VERIFICARE_AUTORE.md`, `docs/DA_FORNIRE.md` | motore |
| Analisi dei repository esterni | `docs/ANALISI_REPOSITORY.md`, `docs/ATTRIBUZIONI.md` | motore |
| Progetto originale | `motore/proposta-motore.md` | motore |
| Profili di genere | `motore/profili/` | motore |
| Modelli vuoti | `motore/modelli/` | motore |
| Dati KDP | `motore/dati/kdp.yaml` | motore |
| Lista nera, parole ammesse | `motore/dati/lista-nera.yaml`, `parole-ammesse-it.txt` | motore |
| Cartelle di un libro | `motore/dati/struttura-libro.yaml` | motore |
| Campi di `libro.yaml` (anche `pausa_lettura`) | `motore/dati/libro.schema.yaml` | motore |
| Hook: script e modalità | `motore/script/hook_*.py`, `motore/dati/hook.yaml` | motore |
| Cartella unica: eccezioni | `motore/dati/cartella-unica.yaml` | motore |
| Output compatto | `motore/dati/output.yaml` | motore |
| Hook e agenti accesi | `.claude/settings.json`, `.claude/agents/`, `.claude/commands/` | ramo del libro |
| Impaginazione e font | `motore/stampa/` | motore |
| Prove e mini-libri inventati | `motore/script/prove.py`, `prove_editoriale.py`, `motore/prove/` | motore |
| Un libro | `libri/<slug>/` | ramo del libro |
| Briefing del libro | `libri/<slug>/00-progetto/briefing.md` | ramo del libro |
| Bibbia e codex | `libri/<slug>/02-bibbia/` | ramo del libro |
| Struttura del libro | `libri/<slug>/03-struttura/` | ramo del libro |
| Capitoli | `libri/<slug>/04-manoscritto/` | ramo del libro |
| Appendici | `libri/<slug>/05-appendici/` | ramo del libro |
| PDF e libro compilato | `libri/<slug>/05-output/` | ramo del libro |
| Report dei controlli e dei ruoli | `libri/<slug>/06-diagnostica/` | ramo del libro |
| Le tue note di lettura | `libri/<slug>/06-diagnostica/note-lettura.md` | ramo del libro |
| Pacchetto KDP | `libri/<slug>/06-pubblicazione/` | ramo del libro |
| Capsule | `libri/<slug>/07-capsule/` | ramo del libro |
| Report di sessione del libro | `libri/<slug>/passaggio-di-consegne.md` | ramo del libro |
| Voci narranti | `indice.yaml`, `voci/<slug>/` | banca-voci (repository a parte) |
| Questa guida | `docs/GUIDA_AL_SISTEMA.pdf` e `.md` | motore |

<p class="fonte">(motore/editoriale/LEGGIMI.md; motore/dati/struttura-libro.yaml; motore/PROCEDURA.md)</p>

Fine della guida.

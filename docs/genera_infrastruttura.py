"""Rigenera docs/INFRASTRUTTURA_COMPLETA.md dal ramo del motore (copia integrale di tutti i file, con verifica).

Uso, dalla radice del repository: python3 -B docs/genera_infrastruttura.py
- Include ogni file tracciato del ramo, tranne docs/ (documenti per l'autore) e i binari (descritti con
  dimensione e sha256). La banca-voci non si copia: sta nel suo repository e contiene nomi reali.
- Ogni file è in un blocco con il suo sha256; alla fine riestrae ogni blocco dal documento e lo confronta
  con il file: l'esito è scritto nella sezione «Verifica di completezza».
"""
import datetime
import hashlib
import os
import re
import subprocess

RAD = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True).stdout.strip()
DEST = os.path.join(RAD, 'docs', 'INFRASTRUTTURA_COMPLETA.md')
LINGUAGGI = {'.py': 'python', '.md': 'markdown', '.yaml': 'yaml', '.json': 'json', '.css': 'css', '.js': 'javascript',
             '.svg': 'xml', '.txt': 'text', '': 'text'}

FLUSSO = '''## 3. Come funziona il flusso

### 3.1 La regola madre
Il ramo del motore contiene solo il motore: codice, dati, modelli vuoti, il livello editoriale e i mini-libri
inventati delle prove. Ogni libro vive solo in `libri/<slug>/` sul suo ramo (cartella unica); il suo nome
non compare altrove. La scala di precedenza è una sola: `motore/editoriale/LEGGIMI.md`.

### 3.2 Recinto e cartella unica
`hook_recinto.py` (PreToolUse, anche su Bash) blocca le scritture fuori dal libro attivo, i `git commit` e
`git push` che violerebbero la cartella unica e la riscrittura intera di un capitolo da parte di un
revisore. Il controllo pre-commit (`precommit.py`), `zb avvio`, `zb salva` e `zb push` controllano comunque su git
file modificati, commit misti e titolo del libro (`cartella_unica.py`, eccezioni in `dati/cartella-unica.yaml`).

### 3.3 Dal briefing alla struttura
`zb nuovo` crea `libri/<slug>/` con `libro.yaml`, `stato.yaml` (fase «struttura»), `LEGGIMI.md` e i nove file di
`03-struttura/` (percorso editoriale). L'architetto li compila; il diagnosta scrive il rapporto e l'editor
strutturale il piano di revisione, in sessioni separate. `zb pronto` fa i controlli meccanici (`struttura.py`, rapporti
con impronta e commit separato): se reggono, il gate `struttura` si chiude da solo (gate automatico) e nascono bibbia,
cronologia, manuale e codex; se no il motore si ferma e scrive il motivo.

### 3.4 Le letture (avvio) e i ruoli
`zb avvio <libro> [--ruolo R]` controlla git, stato, documenti approvati, cartella unica e capsule, registra
il ruolo della sessione (uno solo) e stampa la riga «Letto». Chi ha scritto non revisiona
(`separazione_ruoli: blocco` in `dati/hook.yaml`); `zb ruolo` rifiuta un ruolo fuori dalla sua fase.

### 3.5 Fasi, scrittura automatica e pausa di lettura
struttura → documenti → pagina_campione → stesura → struttura_manoscritto → line → copy → bozze → chiusura
(libro di traduzione: guida → stesura → line → copy → fedelta → chiusura). Sul percorso editoriale nessuna fase aspetta l'approvazione dell'autore: il motore fa i controlli e si
ferma solo se qualcosa non va (`controllo_fallito`) o alla PAUSA DI LETTURA (gate `lettura`): dopo `pausa_lettura`
capitoli (3-5 in `libro.yaml`, predefinito 3) elenca i file da leggere; l'autore risponde `ok` o `correggi <note>`.
In stesura `zb esito` fa i controlli del capitolo (lunghezze, stile, continuità, anti-riciclo, anti-IA con le soglie
del profilo, Gulpease informativo) e `zb capsula` la capsula di continuità. La sessione principale non scrive prosa:
chiama gli agenti (`zb agenti prossimo`), capitoli in sequenza, line, copy e capsule fino a 3 in parallelo.
Il percorso breve resta come opzione di `libro.yaml` (`percorso: breve`).

### 3.6 Chiusura meccanica
`continuita`, `ortografia` (Hunspell, LanguageTool fuori dal repository con `zb languagetool`, lista del correttore),
`compila`, `impagina`, `pdf`, `pacchetto`, `kdp`, poi `pronto`.

### 3.7 Salvataggio e prove
A ogni passo: `zb salva` (recinto, commit, push), `git status -sb`, `git log -1`. Sul lavoro del motore `zb push` vuole
l'impronta di `zb prove` intera e tutta OK sullo stato attuale. Report di passaggio ogni 5 scambi, nella cartella
del libro (`motore/passaggio-di-consegne.md` solo per il lavoro sul motore).
'''


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def binario(p):
    try:
        open(p, encoding='utf-8').read()
        return False
    except UnicodeDecodeError:
        return True


def descrizione(rel):
    p = os.path.join(RAD, rel)
    if binario(p):
        return 'file binario'
    t = open(p, encoding='utf-8').read()
    if rel.endswith('.py') or rel.endswith('/zb'):
        m = re.search(r'"""(.+?)(?:\n|""")', t)
        return m.group(1).strip() if m else 'script'
    if rel.endswith('.md'):
        m = re.search(r'(?m)^#\s+(.+)$', t)
        return m.group(1).strip() if m else 'documento'
    if rel.endswith(('.yaml', '.txt')):
        m = re.search(r'(?m)^#\s*(.+)$', t)
        return m.group(1).strip() if m else 'dati'
    return os.path.splitext(rel)[1].lstrip('.') or 'file'


def albero(files):
    righe, visti = [], set()
    for rel in files:
        parti = rel.split('/')
        for i in range(len(parti) - 1):
            d = '/'.join(parti[:i + 1])
            if d not in visti:
                visti.add(d)
                righe.append('    ' * i + parti[i] + '/')
        righe.append('    ' * (len(parti) - 1) + parti[-1])
    return righe


def ancora(rel):
    return 'file-' + re.sub(r'[^a-z0-9]+', '-', rel.lower()).strip('-')


def main():
    files = [f for f in subprocess.run(['git', '-C', RAD, 'ls-files'], capture_output=True, text=True).stdout.split()
             if not f.startswith('docs/')]
    ramo = subprocess.run(['git', '-C', RAD, 'branch', '--show-current'], capture_output=True, text=True).stdout.strip()
    commit = subprocess.run(['git', '-C', RAD, 'log', '-1', '--format=%H «%s»'], capture_output=True, text=True).stdout.strip()
    testo = [f'# Infrastruttura completa del sistema casa editrice', '',
             f'- **Data:** {datetime.date.today().isoformat()}',
             f'- **Ramo:** `{ramo}`; **commit di partenza:** `{commit}`: tutti i file sono copiati da questo stato.',
             f'- **File inclusi:** {len(files)} file tracciati (esclusa `docs/`); i binari sono descritti con '
             'dimensione e sha256.',
             '- **Esclusi per regola:** `libri/` e ogni manoscritto (mai sul ramo `motore`); la banca-voci (repository '
             'separato, contiene nomi reali: non si copia qui); le esportazioni precedenti, nella storia git e sul ramo '
             'd\'archivio dei documenti.',
             '- **Rigenerazione:** `python3 -B docs/genera_infrastruttura.py`. Verifica in fondo.', '',
             '## 1. Indice', '', '1. Indice', '2. Mappa dell\'infrastruttura', '3. Come funziona il flusso',
             '4. File integrali', '5. Verifica di completezza', '',
             '## 2. Mappa dell\'infrastruttura', '', '### 2.1 Albero', '', '```text'] + albero(files) + \
            ['```', '', '### 2.2 Un file per riga', '']
    testo += [f'- [`{rel}`](#{ancora(rel)}): {descrizione(rel)}' for rel in files]
    testo += ['', FLUSSO, '## 4. File integrali', '']
    for rel in files:
        p = os.path.join(RAD, rel)
        testo += [f'<a id="{ancora(rel)}"></a>', f'#### FILE: {rel}', '']
        if binario(p):
            testo += [f'File binario, {os.path.getsize(p)} byte, sha256 `{sha(p)}`: non copiato come testo.', '']
            continue
        corpo = open(p, encoding='utf-8').read()
        ling = LINGUAGGI.get(os.path.splitext(rel)[1], 'text')
        testo += [f'{len(corpo.splitlines())} righe, sha256 `{sha(p)}`.', '', '`````' + ling, corpo.rstrip('\n'),
                  '`````', '']
    doc = '\n'.join(testo) + '\n'
    # verifica: ogni blocco riestratto deve coincidere con il file (a meno dell'a capo finale)
    ok, ko = 0, []
    for rel in files:
        p = os.path.join(RAD, rel)
        if binario(p):
            ok += 1
            continue
        m = re.search(r'#### FILE: ' + re.escape(rel) + r'\n\n[^\n]*\n\n`````\w*\n(.*?)\n`````\n', doc, re.S)
        if m and m.group(1) == open(p, encoding='utf-8').read().rstrip('\n'):
            ok += 1
        else:
            ko.append(rel)
    doc += (f'## 5. Verifica di completezza\n\n{ok} file su {len(files)} riestratti da questo documento e uguali '
            f'all\'originale' + (f'; diversi: {", ".join(ko)}' if ko else '') + '.\n')
    open(DEST, 'w', encoding='utf-8').write(doc)
    print(f'{DEST}: {len(files)} file, verifica {ok}/{len(files)}')
    return 0 if not ko else 1


if __name__ == '__main__':
    raise SystemExit(main())

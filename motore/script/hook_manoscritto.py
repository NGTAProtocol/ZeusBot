"""Hook PreToolUse di Claude Code sul manoscritto (proposta C.4).

Legge da stdin il JSON dell'hook ({session_id, tool_name, tool_input, cwd}). Se lo strumento
scrive sotto <x>/04-manoscritto/ di una cartella <x> che contiene libro.yaml, e manca il marker
<x>/.zb/letto-<session_id> (o è più vecchio dell'ultima compattazione del contesto):
- modalità «avviso» (motore/dati/hook.yaml): stampa {"systemMessage": "ATTENZIONE: …"}, annota
  in <x>/.zb/avvisi-hook.log ed esce con 0, quindi NON blocca;
- modalità «blocco»: messaggio su stderr, codice 2 (lo strumento non viene eseguito).
Write, Edit, MultiEdit, NotebookEdit: percorso del file. Bash: euristica sul testo del comando
(scenari e limiti in motore/PROCEDURA.md, «Hook»). Se l'hook stesso va in errore: in avviso lascia
passare; in blocco blocca solo se il testo contiene «04-manoscritto».
Si attiva solo con «zb hook attiva». Legge solo stdin, hook.yaml e i marker.
"""
import json
import os
import re
import shlex
import sys
import time

sys.dont_write_bytecode = True
MOTORE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARTELLA = '04-manoscritto'
SEPARATORI = {';', '&&', '||', '|', '&', '\n', '(', ')'}
REDIREZIONI = {'>', '>>', '>|', '&>', '&>>'}


def modalita():
    try:
        for riga in open(os.path.join(MOTORE, 'dati', 'hook.yaml'), encoding='utf-8'):
            m = re.match(r'^modalita:\s*(\w+)', riga)
            if m:
                return m.group(1)
    except OSError:
        pass
    return 'avviso'


def libro_di(percorso):
    """Cartella del libro se il percorso sta sotto <x>/04-manoscritto/ e <x>/libro.yaml esiste."""
    parti = os.path.normpath(percorso).split(os.sep)
    if CARTELLA not in parti:
        return None
    i = len(parti) - 1 - parti[::-1].index(CARTELLA)
    x = os.sep.join(parti[:i]) or os.sep
    return x if os.path.isfile(os.path.join(x, 'libro.yaml')) else None


def risolvi(p, base):
    p = os.path.expanduser(p)
    return os.path.normpath(p if os.path.isabs(p) else os.path.join(base, p))


def espandi(t, variabili):
    return re.sub(r'\$\{?(\w+)\}?', lambda m: variabili.get(m.group(1), m.group(0)), t)


def bersagli_bash(comando, cwd):
    """Percorsi che il comando Bash probabilmente scrive (solo se nomina 04-manoscritto)."""
    if CARTELLA not in comando:
        return []
    try:
        lex = shlex.shlex(comando, posix=True, punctuation_chars=';&|()<>')
        lex.whitespace_split = True
        lex.commenters = ''
        token = list(lex)
    except ValueError:            # virgolette sbilanciate: ogni percorso col manoscritto
        return [risolvi(p, cwd) for p in re.findall(r'[^\s\'"`;|&<>]*' + CARTELLA + r'[^\s\'"`;|&<>]*', comando)]
    segmenti, cur = [], []
    for t in token:
        if t in SEPARATORI:
            segmenti.append(cur)
            cur = []
        else:
            cur.append(t)
    segmenti.append(cur)
    variabili, base, out = {}, cwd, []
    for seg in segmenti:
        seg = [espandi(t, variabili) for t in seg]
        args, i = [], 0
        while i < len(seg):
            t = seg[i]
            if t in REDIREZIONI and i + 1 < len(seg):
                out.append(risolvi(seg[i + 1], base))
                i += 2
                continue
            if t in ('<', '<<', '<<<') and i + 1 < len(seg):
                i += 2
                continue
            args.append(t)
            i += 1
        while args and re.match(r'^\w+=', args[0]):
            k, v = args.pop(0).split('=', 1)
            variabili[k] = v
        if not args:
            continue
        prog = os.path.basename(args[0])
        file_args = [a for a in args[1:] if not a.startswith('-')]
        if prog == 'cd' and file_args:
            base = risolvi(file_args[0], base)
        elif prog == 'tee' or prog in ('rm', 'truncate', 'mv', 'dd', 'touch'):
            out += [risolvi(a.split('=', 1)[-1], base) for a in file_args]
        elif prog in ('sed', 'perl') and any(re.match(r'^-\w*i', a) for a in args[1:]):
            out += [risolvi(a, base) for a in file_args]
        elif prog in ('cp', 'install', 'rsync') and file_args:
            out.append(risolvi(file_args[-1], base))
        elif prog == 'git' and len(args) > 1 and args[1] in ('checkout', 'restore'):
            out += [risolvi(a, base) for a in args[2:] if not a.startswith('-')]
        elif prog.startswith('python'):
            if '-c' in args and args.index('-c') + 1 < len(args):
                codice = args[args.index('-c') + 1]
                out += [risolvi(p, base) for p in re.findall(r'[^\s\'"`,()]*' + CARTELLA + r'[^\s\'"`,()]*', codice)]
            else:
                out += [risolvi(a, base) for a in file_args if CARTELLA in a]
    return out


def bersagli(dati):
    nome = dati.get('tool_name') or ''
    inp = dati.get('tool_input') or {}
    cwd = dati.get('cwd') or os.getcwd()
    if nome in ('Write', 'Edit', 'MultiEdit'):
        return [risolvi(inp.get('file_path') or '', cwd)]
    if nome == 'NotebookEdit':
        return [risolvi(inp.get('notebook_path') or '', cwd)]
    if nome == 'Bash':
        return bersagli_bash(inp.get('command') or '', cwd)
    return []


def marker_valido(libro, sid, cwd):
    m = os.path.join(libro, '.zb', f'letto-{sid}')
    if not os.path.isfile(m):
        return False
    progetto = os.environ.get('CLAUDE_PROJECT_DIR') or cwd
    c = os.path.join(progetto, '.zb', f'compattato-{sid}')
    return not os.path.isfile(c) or os.path.getmtime(m) >= os.path.getmtime(c)


def annota(libro, testo):
    try:
        d = os.path.join(libro, '.zb')
        os.makedirs(d, exist_ok=True)
        if not os.path.isfile(os.path.join(d, '.gitignore')):
            open(os.path.join(d, '.gitignore'), 'w', encoding='utf-8').write('*\n')
        with open(os.path.join(d, 'avvisi-hook.log'), 'a', encoding='utf-8') as f:
            f.write(f'{time.strftime("%Y-%m-%dT%H:%M:%S")} {testo}\n')
    except OSError:
        pass


def main():
    grezzo = sys.stdin.read()
    mod = modalita()
    try:
        dati = json.loads(grezzo)
        sid = str(dati.get('session_id') or 'locale')
        cwd = dati.get('cwd') or os.getcwd()
        libri = sorted({lb for p in bersagli(dati) if (lb := libro_di(p))})
        senza = [lb for lb in libri if not marker_valido(lb, sid, cwd)]
        if not senza:
            return 0
        if mod == 'blocco':
            print(f'Esegui motore/script/avvio.py prima di scrivere nel manoscritto: zb avvio {senza[0]}',
                  file=sys.stderr)
            return 2
        msg = (f'ATTENZIONE: avvio.py non eseguito in questa sessione (o contesto compattato dopo l\'avvio); '
               f'scrittura nel manoscritto di {", ".join(senza)} non verificata. Esegui: zb avvio {senza[0]}')
        for lb in senza:
            annota(lb, f'{dati.get("tool_name")}: {msg}')
        print(json.dumps({'systemMessage': msg}, ensure_ascii=False))
        return 0
    except Exception as e:
        if mod == 'blocco' and CARTELLA in grezzo:
            print(f'hook_manoscritto: errore ({e}); blocco per prudenza.', file=sys.stderr)
            return 2
        print(json.dumps({'systemMessage': f'hook_manoscritto: errore ({e}); lasciato passare.'}, ensure_ascii=False))
        return 0


if __name__ == '__main__':
    sys.exit(main())

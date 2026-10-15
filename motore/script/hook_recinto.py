"""Hook PreToolUse di Claude Code: recinto sul libro attivo, in modalità BLOCCO.

Uso come hook (da .claude/settings.json): legge da stdin il JSON dell'hook
({tool_name, tool_input, cwd}) e controlla il file che Write, Edit, MultiEdit o NotebookEdit
vogliono scrivere.
- Lavoro su un libro (predefinito): consente solo <repo>/libri/<slug-attivo>/, con slug letto da
  <repo>/libri/libro-attivo.md (prima riga non vuota; vale anche «libri/<slug>»). Tutto il resto,
  motore/ compreso, è rifiutato: messaggio su stderr, codice 2 (lo strumento non viene eseguito).
  Nascita di un libro: è consentito anche <repo>/libri/<slug>/briefing.md (o 00-progetto/briefing.md)
  se <repo>/libri/<slug>/libro.yaml non esiste ancora; poi «zb nuovo» lo rende il libro attivo.
- Lavoro sul motore («lavoro sul motore» dell'autore → «zb lavoro motore»): consente il repository
  tranne libri/; rifiuta libri/ e ciò che sta fuori dal repository.
- libro-attivo.md assente o vuoto (lavoro su un libro): avviso, non blocco.
Lo stato del lavoro sta in <git-dir>/zb-lavoro («libro» o «motore»), fuori dai file tracciati.

Bash: i percorsi che il comando probabilmente scrive (redirezioni >, >>, tee, sed -i, perl -i, cp e rsync
verso, mv, rm, touch, truncate, dd, mkdir, ln, git checkout/restore, python -c con un percorso) si controllano
con la stessa regola, solo se stanno dentro il repository (/tmp, /dev/null e lo scratchpad restano liberi).
Limiti residui (falsi permessi, li coprono il controllo pre-commit e «zb avvio»): script che scrivono senza
nominare il percorso, variabili o «cd» di comandi precedenti, sostituzioni di comando, strumenti non elencati
(awk -i inplace, ed, vim -c, find -delete, xargs rm).

Uso come comando: hook_recinto.py lavoro stato | lavoro motore | lavoro libro <slug>
(«zb lavoro …»). «lavoro libro <slug>» scrive libri/libro-attivo.md: si rifiuta sul ramo «motore».
Ogni «zb lavoro motore|libro» installa anche il controllo pre-commit di git (precommit.py), che rifiuta un
commit con file fuori dal recinto qualunque strumento li abbia scritti.
"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
ATTIVO = os.path.join('libri', 'libro-attivo.md')
BRIEFING = ('briefing.md', os.path.join('00-progetto', 'briefing.md'))


def _git(cartella, *a):
    try:
        r = subprocess.run(['git', '-C', cartella, *a], capture_output=True, text=True)
    except FileNotFoundError:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def radice(cartella):
    while cartella and not os.path.isdir(cartella):
        cartella = os.path.dirname(cartella)
    r = _git(cartella or '/', 'rev-parse', '--show-toplevel')
    return os.path.realpath(r) if r else None


def dentro(cartella, percorso):
    return percorso == cartella or percorso.startswith(cartella + os.sep)


def file_stato(rad):
    g = _git(rad, 'rev-parse', '--absolute-git-dir')
    return os.path.join(g, 'zb-lavoro') if g else None


def lavoro(rad):
    f = file_stato(rad)
    try:
        return 'motore' if open(f, encoding='utf-8').read().strip() == 'motore' else 'libro'
    except (OSError, TypeError):
        return 'libro'


def imposta_lavoro(rad, valore):
    f = file_stato(rad)
    if f:
        with open(f, 'w', encoding='utf-8') as h:
            h.write(valore + '\n')


def slug_attivo(rad):
    try:
        for riga in open(os.path.join(rad, ATTIVO), encoding='utf-8'):
            riga = riga.strip().strip('`').rstrip('/')
            if riga and not riga.startswith('#'):
                return os.path.basename(riga)
    except OSError:
        pass
    return None


def imposta_libro_attivo(rad, slug):
    """Libro attivo = libri/<slug>/ e lavoro = libro. Operazione di servizio di zb (nuovo, lavoro)."""
    p = os.path.join(rad, ATTIVO)
    if slug_attivo(rad) != slug:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as h:
            h.write(slug + '\n')
    imposta_lavoro(rad, 'libro')


def decidi(percorso, rad):
    """(«consenti» | «avviso» | «blocca», messaggio) per una scrittura su `percorso`."""
    libri = os.path.join(rad, 'libri')
    if lavoro(rad) == 'motore':
        if dentro(rad, percorso) and not dentro(libri, percorso):
            return 'consenti', ''
        return 'blocca', (f'RECINTO: scrittura rifiutata su {percorso}. Lavoro sul motore: si scrive solo nel '
                          'repository fuori da libri/. Per tornare a un libro: zb lavoro libro <slug>.')
    slug = slug_attivo(rad)
    if not slug:
        return 'avviso', (f'RECINTO: nessun libro attivo ({ATTIVO} manca o è vuoto). Per un briefing nuovo: '
                          'zb nuovo libri/<slug>/briefing.md; per un libro esistente: zb lavoro libro <slug>, '
                          'poi zb avvio libri/<slug>.')
    cartella = os.path.join(libri, slug)
    if dentro(cartella, percorso):
        return 'consenti', ''
    rel = os.path.relpath(percorso, libri) if dentro(libri, percorso) else ''
    parti = rel.split(os.sep, 1)
    if len(parti) == 2 and parti[1] in BRIEFING and not os.path.exists(os.path.join(libri, parti[0], 'libro.yaml')):
        return 'consenti', ''
    return 'blocca', (f'RECINTO: scrittura rifiutata su {percorso}. Libro attivo: libri/{slug}/; si scrive solo '
                      'lì dentro, sottocartelle comprese (mai in motore/, nella banca-voci o altrove). '
                      'Se l\'autore ha scritto «lavoro sul motore»: zb lavoro motore.')


def hook():
    try:
        dati = json.load(sys.stdin)
    except ValueError:
        return 0
    ti = dati.get('tool_input') or {}
    cwd = dati.get('cwd') or os.getcwd()
    base = os.environ.get('CLAUDE_PROJECT_DIR') or cwd
    rad = radice(base)
    if not rad:
        return 0
    if dati.get('tool_name') == 'Bash':
        import hook_manoscritto
        bersagli = [os.path.realpath(p) for p in hook_manoscritto.bersagli_bash(ti.get('command') or '', cwd, solo=None)]
        for p in bersagli:
            if dentro(rad, p) and not dentro(os.path.join(rad, '.git'), p):
                esito, msg = decidi(p, rad)
                if esito == 'blocca':
                    print(msg + ' (comando Bash)', file=sys.stderr)
                    return 2
        return 0
    percorso = ti.get('file_path') or ti.get('notebook_path')
    if not percorso:
        return 0
    percorso = os.path.realpath(os.path.join(cwd, percorso))
    esito, msg = decidi(percorso, rad)
    if esito == 'blocca':
        print(msg, file=sys.stderr)
        return 2
    if esito == 'avviso':
        print(json.dumps({'systemMessage': msg}, ensure_ascii=False))
    return 0


def comando(args):
    rad = radice(os.path.dirname(os.path.abspath(__file__)))
    if not rad:
        print('FERMO: non sono in un repository git.', file=sys.stderr)
        return 2
    azione = args[1] if len(args) > 1 else 'stato'
    import precommit
    if azione == 'stato':
        print(f'Lavoro: {lavoro(rad)}; libro attivo: {slug_attivo(rad) or "nessuno"}; '
              f'controllo pre-commit: {precommit.stato(rad)}')
        return 0
    if azione == 'motore':
        imposta_lavoro(rad, 'motore')
        print('Lavoro sul motore: consentito il repository tranne libri/. Per tornare: zb lavoro libro <slug>.')
        print(precommit.installa(rad))
        return 0
    if azione == 'libro' and len(args) > 2:
        slug = os.path.basename(args[2].rstrip('/'))
        if _git(rad, 'branch', '--show-current') == 'motore':
            print('FERMO: il ramo «motore» non contiene mai un libro; passa a un ramo di libro.', file=sys.stderr)
            return 2
        imposta_libro_attivo(rad, slug)
        print(f'Libro attivo: libri/{slug}/; si scrive solo lì dentro. Poi: zb avvio libri/{slug}.')
        print(precommit.installa(rad))
        return 0
    print('Uso: zb lavoro stato | zb lavoro motore | zb lavoro libro <slug>', file=sys.stderr)
    return 2


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'lavoro':
        sys.exit(comando(sys.argv[1:]))
    sys.exit(hook())

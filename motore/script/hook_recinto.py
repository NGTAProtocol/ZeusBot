"""Hook PreToolUse di Claude Code: recinto sul libro attivo, in modalità BLOCCO.

Uso come hook (da .claude/settings.json): legge da stdin il JSON dell'hook
({session_id, tool_name, tool_input, cwd}) e controlla i file che Write, Edit, MultiEdit,
NotebookEdit o Bash vogliono scrivere.
- Lavoro su un libro (predefinito): consente solo <repo>/libri/<slug-attivo>/, con slug letto da
  <git-dir>/zb-libro-attivo (fuori dai file tracciati: il nome del libro non compare fuori da
  libri/<slug>/); per i rami creati prima, anche da <repo>/libri/libro-attivo.md, in sola lettura.
  Tutto il resto, motore/ compreso, è rifiutato: messaggio su stderr, codice 2.
- Bash: bersagli di redirezioni (>, >>), tee, sed -i, perl -i, cp (destinazione), mv e rm (anche la
  sorgente, che sparisce), truncate, touch, dd, git checkout/restore dopo «--» (euristica di
  hook_manoscritto.py, modalità recinto). Prima di «git commit» e «git push» controlla la cartella unica (cartella_unica.py):
  file in stage o commit misti fuori da libri/<slug>/ → blocco. Limiti dichiarati (non rilevati):
  script e «python -c» che scrivono (un programma lanciato non è un bersaglio), variabili o «cd» di un
  comando precedente, sostituzioni $(…), awk -i, ed, vim, find -delete, xargs, git checkout <ramo>;
  li coprono zb avvio e zb push, che controllano su git i file modificati. I bersagli fuori dal
  repository (/tmp, /dev/null) non contano: la cartella unica riguarda il ramo.
- Revisori (agent_type o ruolo della sessione: editor strutturale, line editor, correttori): un Write su un
  capitolo già esistente di 04-manoscritto/ è rifiutato; si corregge con Edit, a modifiche puntuali.
- Scritture dentro il libro (Write, Edit) in 03-struttura/, 04-manoscritto/, 06-diagnostica/, 07-capsule/:
  annotate in <libro>/.zb/scritture.log con la sessione (separazione dei ruoli, ruoli.py).
  Nascita di un libro: è consentito anche <repo>/libri/<slug>/briefing.md (o 00-progetto/briefing.md)
  se <repo>/libri/<slug>/libro.yaml non esiste ancora; poi «zb nuovo» lo rende il libro attivo.
- Lavoro sul motore («lavoro sul motore» dell'autore → «zb lavoro motore»): consente il repository
  tranne libri/; rifiuta libri/ e ciò che sta fuori dal repository.
- libro-attivo.md assente o vuoto (lavoro su un libro): avviso, non blocco.
Lo stato del lavoro sta in <git-dir>/zb-lavoro («libro» o «motore»), fuori dai file tracciati.

Uso come comando: hook_recinto.py lavoro stato | lavoro motore | lavoro libro <slug>
(«zb lavoro …»). «lavoro libro <slug>» scrive libri/libro-attivo.md: si rifiuta sul ramo «motore».
"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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


def file_attivo(rad):
    g = _git(rad, 'rev-parse', '--absolute-git-dir')
    return os.path.join(g, 'zb-libro-attivo') if g else None


def slug_attivo(rad):
    for p in (file_attivo(rad), os.path.join(rad, ATTIVO)):      # il secondo: rami creati prima
        try:
            for riga in open(p, encoding='utf-8'):
                riga = riga.strip().strip('`').rstrip('/')
                if riga and not riga.startswith('#'):
                    return os.path.basename(riga)
        except (OSError, TypeError):
            pass
    return None


def imposta_libro_attivo(rad, slug):
    """Libro attivo = libri/<slug>/ e lavoro = libro, in <git-dir>/zb-libro-attivo (mai in un file tracciato).
    Operazione di servizio di zb (nuovo, lavoro)."""
    p = file_attivo(rad)
    if p:
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


def bersagli_bash(comando, cwd):
    """Percorsi che il comando probabilmente scrive o cancella (euristica di hook_manoscritto.py, su ogni percorso)."""
    import hook_manoscritto
    return hook_manoscritto.bersagli_bash(comando, cwd, recinto=True)


def git_commit_o_push(comando):
    """«commit» o «push» se il comando Bash contiene git commit / git push (anche dopo && o ;)."""
    import re
    m = re.findall(r'(?:^|[;&|(]\s*|\s)git\s+(?:-C\s+\S+\s+)?(commit|push)\b', comando)
    return set(m)


def controlla_git(comando, rad):
    """Cartella unica prima di git commit / git push sul ramo di un libro: (blocca?, messaggio)."""
    azioni = git_commit_o_push(comando)
    if not azioni:
        return False, ''
    if lavoro(rad) == 'motore':
        import cartella_unica
        fuori = [f for f in cartella_unica.file_modificati(rad, solo_stage='commit' in azioni and ' -a' not in comando)
                 if f.startswith('libri/')]
        if fuori:
            return True, ('RECINTO: lavoro sul motore, ma ci sono file di libri/ da salvare: ' + ', '.join(fuori[:5]))
        return False, ''
    slug = slug_attivo(rad)
    if not slug or not os.path.isdir(os.path.join(rad, 'libri', slug)):
        return False, ''
    import cartella_unica
    titolo = None
    try:
        import comune
        titolo = comune.leggi_yaml(os.path.join(rad, 'libri', slug, 'libro.yaml')).get('titolo')
    except Exception:
        pass
    solo_stage = 'commit' in azioni and ' -a' not in comando and 'push' not in azioni
    err = cartella_unica.controlla(rad, slug, titolo, solo_stage=solo_stage)
    if err:
        return True, (f'CARTELLA UNICA: {" e ".join(sorted(azioni))} rifiutato, tutto il libro vive in libri/{slug}/:\n- '
                      + '\n- '.join(err[:10]))
    return False, ''


def annota_scrittura(percorso, rad, dati):
    """Scrittura dentro un libro: <libro>/.zb/scritture.log (separazione dei ruoli)."""
    try:
        libri = os.path.join(rad, 'libri')
        if not dentro(libri, percorso):
            return
        slug = os.path.relpath(percorso, libri).split(os.sep, 1)[0]
        cartella = os.path.join(libri, slug)
        if not os.path.isfile(os.path.join(cartella, 'libro.yaml')):
            return
        import ruoli
        ruoli.registra_scrittura(cartella, str(dati.get('session_id') or 'locale'), os.path.relpath(percorso, cartella))
    except Exception:       # l'annotazione non deve mai fermare lo strumento
        pass


REVISORI = {'editor-strutturale', 'line-editor', 'correttore-italiano', 'correttore-bozze'}


def riscrittura_da_revisore(percorso, rad, dati):
    """Messaggio se un revisore riscrive per intero (Write) un capitolo esistente; None altrimenti.
    I revisori correggono con modifiche puntuali (Edit), mai riscrivendo il capitolo (risparmio-token.md, 5)."""
    if dati.get('tool_name') != 'Write' or not os.path.isfile(percorso):
        return None
    libri = os.path.join(rad, 'libri')
    if not dentro(libri, percorso):
        return None
    parti = os.path.relpath(percorso, libri).split(os.sep)
    if len(parti) < 3 or parti[1] != '04-manoscritto':
        return None
    chi = dati.get('agent_type')
    if chi not in REVISORI:
        try:
            import ruoli
            chi = (ruoli.leggi_ruoli(os.path.join(libri, parti[0])).get(str(dati.get('session_id'))) or {}).get('ruolo')
        except Exception:
            chi = None
    if chi in REVISORI:
        return (f'RECINTO: {chi} non riscrive per intero {os.path.relpath(percorso, rad)}: correzioni puntuali con Edit, '
                'solo dopo l\'«ok» dell\'autore.')
    return None


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
        comando = ti.get('command') or ''
        blocca, msg = controlla_git(comando, rad)
        if blocca:
            print(msg, file=sys.stderr)
            return 2
        # solo i bersagli dentro il repository: /tmp, /dev/null e simili non toccano il ramo
        percorsi = [p for p in (os.path.realpath(x) for x in bersagli_bash(comando, cwd)) if dentro(rad, p)]
    else:
        percorso = ti.get('file_path') or ti.get('notebook_path')
        if not percorso:
            return 0
        percorsi = [os.path.realpath(os.path.join(cwd, percorso))]
    avvisi = []
    for percorso in percorsi:
        esito, msg = decidi(percorso, rad)
        if esito == 'blocca':
            print(msg, file=sys.stderr)
            return 2
        if esito == 'avviso':
            avvisi.append(msg)
    if dati.get('tool_name') != 'Bash':
        for percorso in percorsi:
            msg = riscrittura_da_revisore(percorso, rad, dati)
            if msg:
                print(msg, file=sys.stderr)
                return 2
        for percorso in percorsi:
            annota_scrittura(percorso, rad, dati)
    if avvisi:
        print(json.dumps({'systemMessage': avvisi[0]}, ensure_ascii=False))
    return 0


def comando(args):
    rad = radice(os.path.dirname(os.path.abspath(__file__)))
    if not rad:
        print('FERMO: non sono in un repository git.', file=sys.stderr)
        return 2
    azione = args[1] if len(args) > 1 else 'stato'
    if azione == 'stato':
        print(f'Lavoro: {lavoro(rad)}; libro attivo: {slug_attivo(rad) or "nessuno"}')
        return 0
    if azione == 'motore':
        imposta_lavoro(rad, 'motore')
        print('Lavoro sul motore: consentito il repository tranne libri/. Per tornare: zb lavoro libro <slug>.')
        return 0
    if azione == 'libro' and len(args) > 2:
        slug = os.path.basename(args[2].rstrip('/'))
        if _git(rad, 'branch', '--show-current') == 'motore':
            print('FERMO: il ramo «motore» non contiene mai un libro; passa a un ramo di libro.', file=sys.stderr)
            return 2
        imposta_libro_attivo(rad, slug)
        print(f'Libro attivo: libri/{slug}/; si scrive solo lì dentro.')
        return 0
    print('Uso: zb lavoro stato | zb lavoro motore | zb lavoro libro <slug>', file=sys.stderr)
    return 2


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'lavoro':
        sys.exit(comando(sys.argv[1:]))
    sys.exit(hook())

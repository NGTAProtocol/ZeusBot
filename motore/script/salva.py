"""Salvataggio con il recinto (comando «zb salva [<libro>] <messaggio>»): controllo, commit, push.

Uso: python3 -B salva.py [<libro>] <messaggio> [--senza-prove]
1. Controllo su git di tutti i file modificati o nuovi del repository (anche quelli scritti da Bash o da uno
   script): se uno sta fuori dal recinto del lavoro attuale (libri/<slug>/ per un libro, tutto tranne libri/
   per il motore; precommit.py) il salvataggio è rifiutato e il file è elencato.
2. Libro del percorso editoriale: rigenera lo stato compatto (stato-compatto.md).
3. Lavoro sul motore: lancia «zb prove» prima del commit; se non sono tutte OK si ferma. «--senza-prove»
   vale solo se tutti i file cambiati stanno in docs/.
4. git add (solo i file ammessi), commit, push con ripiego (push.py); poi «git status -sb» e «git log -1».
"""
import os
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import hook_recinto  # noqa: E402
import precommit  # noqa: E402


def git(rad, *a):
    return subprocess.run(['git', '-C', rad, *a], capture_output=True, text=True)


def main(argv):
    args = comune.argomenti(argv)
    rad = hook_recinto.radice(os.getcwd())
    if not rad:
        raise comune.ErroreMotore('Non sono in un repository git.')
    modo = hook_recinto.lavoro(rad)
    libro = None
    if args and os.path.isfile(os.path.join(args[0], 'libro.yaml')):
        libro, args = os.path.realpath(args[0]), args[1:]
    msg = ' '.join(args).strip()
    if not msg:
        raise comune.ErroreMotore('Uso: salva [<libro>] <messaggio>')
    cambiati = precommit.modificati(rad)
    if not cambiati:
        print('Niente da salvare.')
        return 0
    fuori = precommit.fuori(rad, cambiati)
    if fuori:
        raise comune.ErroreMotore('Salvataggio rifiutato: file fuori dal recinto (' + modo + '):\n- '
                                  + '\n- '.join(fuori[:20]) + '\nNon li salvo e non li cancello: decidi tu.')
    if modo == 'libro':
        slug = hook_recinto.slug_attivo(rad)
        libro = libro or (os.path.join(rad, 'libri', slug) if slug else None)
        if libro and os.path.isfile(os.path.join(libro, 'libro.yaml')):
            cartella, lb, _ = comune.carica_libro(libro)
            if comune.editoriale(lb) and os.path.isfile(os.path.join(cartella, 'stato.yaml')):
                import compatto
                compatto.genera(cartella, lb)
                cambiati = precommit.modificati(rad)
    else:
        if '--senza-prove' in argv and all(c.startswith('docs/') for c in cambiati):
            print('Prove saltate: cambiano solo file di docs/.')
        else:
            p = subprocess.run([sys.executable, '-B', os.path.join(comune.radice_motore(), 'zb'), 'prove'],
                               capture_output=True, text=True)
            fine = [r for r in p.stdout.splitlines() if r.startswith(('Prove:', 'ESITO', 'KO '))]
            print('\n'.join(fine[-8:]))
            if p.returncode != 0:
                raise comune.ErroreMotore('Prove con KO: niente commit né push. Correggi e rilancia zb salva.')
    # una cancellazione già nell'indice (git rm) non ha più il file né la voce: git add la rifiuterebbe
    indice = set(git(rad, 'ls-files', '-z', '--', *cambiati).stdout.split('\0'))
    da_aggiungere = [c for c in cambiati if c in indice or os.path.lexists(os.path.join(rad, c))]
    r = git(rad, 'add', '-A', '--', *da_aggiungere) if da_aggiungere else subprocess.CompletedProcess([], 0, '', '')
    if r.returncode:
        raise comune.ErroreMotore(f'git add non riuscito: {r.stderr.strip()}')
    r = git(rad, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', msg)
    if r.returncode:
        raise comune.ErroreMotore(f'Commit non riuscito: {(r.stderr or r.stdout).strip()}')
    p = subprocess.run([sys.executable, '-B', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'push.py')],
                       cwd=rad, capture_output=True, text=True)
    print((p.stdout.strip().splitlines() or [''])[-1])
    print(git(rad, 'status', '-sb').stdout.splitlines()[0])
    print(git(rad, 'log', '-1', '--format=%h %s').stdout.strip())
    if p.returncode:
        raise comune.ErroreMotore('Push non riuscito: il lavoro è nel commit locale, non su origin. ' + p.stderr.strip()[-300:])
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

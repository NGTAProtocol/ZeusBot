"""Cartella unica: tutto ciò che riguarda un libro vive solo in libri/<slug>/ (ramo del libro).

Uso: cartella_unica.py <libro> [--commit]      (zb cartella <libro>; lo usano anche zb avvio, zb push e l'hook)
Controlla su git, dalla radice del repository:
1. modifiche non salvate (git status): ogni file fuori da libri/<slug>/ è un errore;
   con --commit valgono solo i file in stage (git diff --cached), come prima di un commit;
2. commit del ramo che toccano libri/<slug>/ (da merge-base con origin/motore, merge esclusi):
   se lo stesso commit tocca file fuori da libri/ è un commit misto, errore (i file di un altro libro,
   libri/<altro>/, li segnala zb avvio con un avviso, come in ccr: un ramo può contenere più libri);
3. il titolo del libro e il percorso libri/<slug> non compaiono in nessun file tracciato fuori da libri/ scritto sul
   ramo (diverso da origin/motore: il contenuto del motore arriva da lì; le cartelle di altri libri sullo stesso ramo
   le segnala già zb avvio con un avviso). Integrazione: da motore, 971b6df.
Esclusi (dichiarati in dati/cartella-unica.yaml): i file di configurazione della radice del ramo
(CLAUDE.md, .gitignore, .claude/settings.json, .claude/agents/), i merge del motore (commit di merge:
il contenuto del motore arriva da origin/motore, mai scritto a mano sul ramo del libro) e i commit misti
già fatti che l'autore dichiara, con motivo, in commit_dichiarati (la storia non si riscrive).
Codice 0 se tutto è in regola, 2 con l'elenco degli errori. Non scrive nulla.
"""
import os
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402


def regole():
    return comune.leggi_yaml(os.path.join(comune.radice_motore(), 'dati', 'cartella-unica.yaml'))


def ammesso(rel, reg):
    return any(rel == a or (a.endswith('/') and rel.startswith(a)) for a in reg['ammessi_fuori'])


def _git(rad, *a):
    r = subprocess.run(['git', '-C', rad, *a], capture_output=True, text=True)
    return r.returncode, r.stdout


def file_modificati(rad, solo_stage=False):
    if solo_stage:
        return [x for x in _git(rad, 'diff', '--cached', '--name-only')[1].splitlines() if x]
    out = []
    for r in _git(rad, 'status', '--porcelain', '-uall')[1].splitlines():
        p = r[3:]
        if ' -> ' in p:
            p = p.split(' -> ', 1)[1]
        out.append(p.strip('"'))
    return out


def commit_del_libro(rad, slug, base):
    """[(commit, oggetto, [file])] dei commit (non merge) da merge-base con base che toccano libri/<slug>/."""
    c, mb = _git(rad, 'merge-base', 'HEAD', base)
    intervallo = f'{mb.strip()}..HEAD' if c == 0 and mb.strip() else 'HEAD'
    c, out = _git(rad, 'log', intervallo, '--no-merges', '--format=@%h %s', '--name-only', '--', f'libri/{slug}/')
    hash_ = [r[1:].split(' ', 1) for r in out.splitlines() if r.startswith('@')]
    res = []
    for h, *s in hash_:
        files = [x for x in _git(rad, 'show', '--format=', '--name-only', h)[1].splitlines() if x]
        res.append((h, s[0] if s else '', files))
    return res


def controlla(rad, slug, titolo=None, solo_stage=False, base='origin/motore'):
    """Elenco degli errori (vuoto se in regola)."""
    reg = regole()
    libro = f'libri/{slug}/'
    err = []
    for rel in file_modificati(rad, solo_stage):
        if not rel.startswith(libro) and not ammesso(rel, reg):
            err.append(f'file fuori dal libro: {rel}')
    if _git(rad, 'rev-parse', '--verify', '-q', base)[0] == 0:
        for h, sog, files in commit_del_libro(rad, slug, base):
            fuori = [f for f in files if not f.startswith('libri/') and not ammesso(f, reg)]
            if fuori and not any(h.startswith(str(d.get('commit', '-'))[:7]) for d in reg.get('commit_dichiarati') or []):
                err.append(f'commit {h} «{sog}» misto: tocca il libro e anche ' + ', '.join(fuori[:5]))
    diversi = None              # file scritti sul ramo: diversi da origin/motore (None: nessun origin/motore)
    if _git(rad, 'rev-parse', '--verify', '-q', base)[0] == 0:
        diversi = set(_git(rad, 'diff', '--name-only', base)[1].splitlines())
    for nome in [x for x in (titolo, f'libri/{slug}') if x]:
        c, out = _git(rad, 'grep', '-l', '-i', '-F', nome, '--', '.', ':(exclude)libri/')
        for f in out.splitlines():
            if diversi is None or f in diversi:
                err.append(f'«{nome}» compare fuori dal libro: {f}')
    return err


def per_libro(cartella):
    """(radice, slug) se il libro sta in <radice>/libri/<slug>/; altrimenti (radice, None)."""
    cartella = os.path.realpath(cartella)
    rad = comune.radice_git(cartella)
    if rad != '/' and os.path.dirname(cartella) == os.path.join(rad, 'libri'):
        return rad, os.path.basename(cartella)
    return rad, None


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: cartella_unica.py <libro> [--commit]')
    cartella, libro, _ = comune.carica_libro(args[0])
    rad, slug = per_libro(cartella)
    if not slug:
        raise comune.ErroreMotore(f'{cartella} non è libri/<slug>/ di un repository git: la cartella unica vale solo lì.')
    err = controlla(rad, slug, libro.get('titolo'), solo_stage='--commit' in argv)
    if err:
        raise comune.ErroreMotore(f'CARTELLA UNICA: {len(err)} problemi (tutto il libro vive solo in libri/{slug}/):\n- '
                                  + '\n- '.join(err[:30]))
    print(f'OK cartella unica: niente fuori da libri/{slug}/.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

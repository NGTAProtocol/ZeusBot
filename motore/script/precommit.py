"""Controllo pre-commit di git: il recinto vale anche per ciò che il recinto degli hook non vede (Bash, script).

Come hook di git (.git/hooks/pre-commit, installato da «zb lavoro motore|libro»): legge i file in stage e
rifiuta il commit (codice 1) se
- lavoro su un libro: un file sta fuori da libri/<slug-attivo>/ (ammessi anche libri/libro-attivo.md e i file
  che installano «zb agenti» e «zb hook»: .claude/agents/, .claude/commands/, .claude/settings.json);
- lavoro sul motore: un file sta in libri/.
Eccezione dichiarata: un merge del motore in corso (MERGE_HEAD raggiungibile da origin/motore) può portare
file del motore (motore/, docs/, CLAUDE.md, .gitignore) sul ramo del libro.
Lo stesso controllo lo usano «zb salva» (prima del commit) e «zb avvio» (sulle modifiche non salvate).
Uso come comando: precommit.py [--radice-repo <cartella>] (controlla lo stage e stampa l'esito).
"""
import os
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_recinto  # noqa: E402

FIRMA = '# zb: controllo pre-commit del motore'
EXTRA_LIBRO = ('libri/libro-attivo.md', '.claude/agents/', '.claude/commands/', '.claude/settings.json')
DAL_MOTORE = ('motore/', 'docs/', 'CLAUDE.md', '.gitignore')


def _git(rad, *a):
    r = subprocess.run(['git', '-C', rad, *a], capture_output=True, text=True)
    return r.returncode, r.stdout


def merge_del_motore(rad):
    c, out = _git(rad, 'rev-parse', '-q', '--verify', 'MERGE_HEAD')
    if c != 0:
        return False
    return subprocess.run(['git', '-C', rad, 'merge-base', '--is-ancestor', 'MERGE_HEAD', 'origin/motore'],
                          capture_output=True).returncode == 0


def fuori(rad, percorsi, merge=None):
    """Percorsi (relativi alla radice del repository) fuori dal recinto del lavoro attuale."""
    modo = hook_recinto.lavoro(rad)
    if modo == 'motore':
        return [p for p in percorsi if p == 'libri' or p.startswith('libri/')]
    slug = hook_recinto.slug_attivo(rad)
    if not slug:
        return [p for p in percorsi if not p.startswith('libri/')] if percorsi else []
    merge = merge_del_motore(rad) if merge is None else merge
    out = []
    for p in percorsi:
        if p.startswith(f'libri/{slug}/') or any(p == e or (e.endswith('/') and p.startswith(e)) for e in EXTRA_LIBRO):
            continue
        if merge and any(p == d or (d.endswith('/') and p.startswith(d)) for d in DAL_MOTORE):
            continue
        out.append(p)
    return out


def in_stage(rad):
    return [x for x in _git(rad, 'diff', '--cached', '--name-only', '-z')[1].split('\0') if x]


def modificati(rad):
    """File modificati, aggiunti o non tracciati (non ignorati) in tutto il repository."""
    out = []
    for r in _git(rad, 'status', '--porcelain', '-z', '-uall')[1].split('\0'):
        if len(r) > 3:
            out.append(r[3:])
    return out


def stato(rad):
    p = percorso_hook(rad)
    if not p:
        return 'non disponibile (non è un repository git)'
    if not os.path.isfile(p):
        return 'non installato'
    return 'installato' if FIRMA in open(p, encoding='utf-8').read() else 'presente ma non del motore'


def percorso_hook(rad):
    c, out = _git(rad, 'rev-parse', '--git-path', 'hooks/pre-commit')
    return os.path.join(rad, out.strip()) if c == 0 and not os.path.isabs(out.strip()) else (out.strip() or None)


def installa(rad):
    p = percorso_hook(rad)
    if not p:
        return 'Controllo pre-commit: non installato (non è un repository git).'
    if os.path.isfile(p) and FIRMA not in open(p, encoding='utf-8').read():
        return f'Controllo pre-commit: {p} esiste già e non è del motore; non lo tocco.'
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(f'#!/bin/sh\n{FIRMA}\nexec python3 -B "$(git rev-parse --show-toplevel)/motore/script/precommit.py"\n')
    os.chmod(p, 0o755)
    return f'Controllo pre-commit installato ({os.path.relpath(p, rad)}): rifiuta i commit fuori dal recinto.'


def main(argv):
    rad = hook_recinto.radice(os.getcwd())
    if '--radice-repo' in argv:
        rad = os.path.realpath(argv[argv.index('--radice-repo') + 1])
    if not rad:
        return 0
    f = fuori(rad, in_stage(rad))
    if f:
        modo = hook_recinto.lavoro(rad)
        dove = 'libri/' if modo == 'motore' else f'fuori da libri/{hook_recinto.slug_attivo(rad) or "<slug>"}/'
        print(f'RECINTO (pre-commit): commit rifiutato, file {dove} in stage:\n- ' + '\n- '.join(f[:20])
              + '\nToglili dallo stage (git restore --staged <file>) oppure cambia lavoro con «zb lavoro».',
              file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

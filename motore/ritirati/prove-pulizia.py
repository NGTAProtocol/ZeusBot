"""Prove di pulizia.py, tolte da prove.py (sezione passo_6) quando lo script è stato ritirato.

Si eseguivano dentro passo_6(A) di prove.py, con A = attesi.yaml[«passo_6»]; per ripristinarle si
rimettono in coda a passo_6 e si ripristina la voce «pulizia» di attesi (attesi-pulizia.yaml).
"""
import os
import re
import shutil
import subprocess
import sys


def prove_pulizia(A, E, copia_libro, esito, recinto, S, sez):
    # pulizia
    a = A['pulizia']
    L = copia_libro('mini-libro')
    for d in ('__pycache__', '_build', '.zb', '05-output/vuota', '05-revisioni'):
        os.makedirs(os.path.join(L, d), exist_ok=True)
    for rel, dati in (('__pycache__/a.pyc', b'x'), ('_build/b.html', b'y'), ('.zb/letto-vecchia', b'm'),
                      ('.zb/letto-sessione-prova', b'm'), ('05-output/libro.pdf', b'PDFDATA'),
                      ('05-output/libro-copia.pdf', b'PDFDATA'), ('05-output/libro-bozza.pdf', b'BOZZA')):
        open(os.path.join(L, rel), 'wb').write(dati)
    shutil.copyfile(os.path.join(L, '04-manoscritto', '01-la-farmacia.md'), os.path.join(L, '05-revisioni', '01-copia.md'))
    shutil.copyfile(os.path.join(L, '04-manoscritto', '02-l-officina.md'), os.path.join(L, '04-manoscritto', '02-l-officina.md.tmp'))
    env = dict(E, ZB_SESSIONE='sessione-prova')
    prima = recinto.foto(L)
    vuote_prima = sorted(r for r, ds, fs in os.walk(L) if not ds and not fs)
    p = subprocess.run([sys.executable, '-B', os.path.join(S, 'pulizia.py'), L], env=env, capture_output=True, text=True)
    elenco = [r[2:].split(' — ')[0] for r in p.stdout.splitlines() if r.startswith('- ')]
    esito('pulizia.py', 'elenco (dry-run)', a['elenco'], elenco, sez)
    esito('pulizia.py', 'dry-run: niente cancellato', a['dry_run'],
          f'{p.returncode} / {recinto.differenze(prima, recinto.foto(L))} / '
          f'{sorted(r for r, ds, fs in os.walk(L) if not ds and not fs) == vuote_prima}', sez)
    esito('pulizia.py', 'peso dichiarato', 'sì', 'sì' if re.search(r'elementi, [\d.]+ (B|KB|MB)', p.stdout) else 'no', sez)
    man = {r: v for r, v in prima.items() if r.startswith('04-manoscritto/')}
    p = subprocess.run([sys.executable, '-B', os.path.join(S, 'pulizia.py'), L, '--applica'], env=env, capture_output=True, text=True)
    dopo = recinto.foto(L)
    esito('pulizia.py', '--applica: tolti esattamente gli elementi elencati', a['applica'],
          sorted(r for r in prima if r not in dopo) + sorted(e for e in elenco if e.endswith('/') and not os.path.exists(os.path.join(L, e))), sez)
    esito('pulizia.py', '--applica: manoscritto, libro.yaml e marker corrente intatti', a['protetti'],
          f'{all(dopo.get(r) == v for r, v in man.items())} / {"libro.yaml" in dopo} / {".zb/letto-sessione-prova" in dopo}', sez)
    p = subprocess.run([sys.executable, '-B', os.path.join(S, 'pulizia.py'), L], env=env, capture_output=True, text=True)
    esito('pulizia.py', 'dopo --applica: niente da pulire', a['dopo'], p.stdout.count('\n- '), sez)


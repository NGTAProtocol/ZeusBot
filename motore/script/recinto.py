"""Controlla che i comandi del motore scrivano solo dentro il libro indicato (proposta B.9).

Uso: recinto.py [--radice <cartella motore>] [--extra "<comando con {libro}>"]
Per ogni mini-libro di prova: copia il mini-libro in una cartella temporanea,
fotografa il repository (percorsi, dimensioni, sha256, esclusa .git), esegue ogni
comando del motore sulla copia e confronta. Ogni file creato, cambiato o tolto
fuori dalla copia è un KO, con il nome del comando.
Eccezione dichiarata: «verifica KDP fatta» (kdp_verifica.py) può scrivere solo
dati/kdp.yaml e dati/verifiche-kdp.md; è riportata come eccezione, non come violazione.
"""
import hashlib
import os
import shlex
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

MINI_LIBRI = ('mini-libro', 'mini-libro-romance')
ECCEZIONE = ('kdp_verifica.py', ('dati/kdp.yaml', 'dati/verifiche-kdp.md'))


def comandi(motore):
    """Comandi del motore presenti in script/, con {libro} al posto della copia."""
    s = os.path.join(motore, 'script')
    elenco = [
        ('conta.py', 'conta.py {libro}'),
        ('conta.py --schermo', 'conta.py {libro} --schermo'),
        ('valida_profili.py', 'valida_profili.py'),
        ('separazione.py', 'separazione.py'),
        ('stile.py', 'stile.py {libro}'),
        ('continuita.py', 'continuita.py {libro}'),
        ('riciclo.py', 'riciclo.py {libro}'),
        ('capitolo.py 1', 'capitolo.py {libro} 1'),
        ('capitolo.py 2', 'capitolo.py {libro} 2'),
        ('capitolo.py 3', 'capitolo.py {libro} 3'),
        ('compila.py', 'compila.py {libro}'),
        ('impagina.py', 'impagina.py {libro}'),
        ('verifica_pdf.py', 'verifica_pdf.py {libro}'),
        ('pacchetto.py', 'pacchetto.py {libro}'),
        ('conformita_kdp.py', 'conformita_kdp.py {libro}'),
        ('kdp_verifica.py controlla', 'kdp_verifica.py controlla --simula-blocco'),
        ('kdp_verifica.py stato', 'kdp_verifica.py stato'),
    ]
    return [(n, f'{sys.executable} {os.path.join(s, c.split()[0])} ' + ' '.join(c.split()[1:]))
            for n, c in elenco if os.path.isfile(os.path.join(s, c.split()[0]))]


def foto(base):
    out = {}
    for radice, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != '.git']
        for f in files:
            p = os.path.join(radice, f)
            try:
                with open(p, 'rb') as fh:
                    out[os.path.relpath(p, base)] = (os.path.getsize(p), hashlib.sha256(fh.read()).hexdigest())
            except OSError:
                pass
    return out


def differenze(prima, dopo):
    return sorted(set(k for k in set(prima) | set(dopo) if prima.get(k) != dopo.get(k)))


def main(argv):
    motore = comune.radice_motore()
    base = comune.radice_git(motore)
    if base == '/':
        base = os.path.dirname(motore)
    extra = None
    if '--extra' in argv:
        extra = argv[argv.index('--extra') + 1]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    violazioni, eccezioni, eseguiti = [], [], 0
    for nome in MINI_LIBRI:
        sorgente = os.path.join(motore, 'prove', nome)
        with tempfile.TemporaryDirectory(prefix='zb-recinto-') as tmp:
            copia = os.path.join(tmp, nome)
            shutil.copytree(sorgente, copia)
            lista = comandi(motore) + ([('kdp_verifica.py (extra)' if 'kdp_verifica.py' in extra else 'extra', extra)] if extra else [])
            for etichetta, cmd in lista:
                prima = foto(base)
                subprocess.run(shlex.split(cmd.replace('{libro}', copia)), env=env,
                               capture_output=True, text=True, cwd=tmp)
                eseguiti += 1
                diff = differenze(prima, foto(base))
                for d in diff:
                    rel_motore = os.path.relpath(os.path.join(base, d), motore).replace(os.sep, '/')
                    if etichetta.startswith(ECCEZIONE[0]) and rel_motore in ECCEZIONE[1]:
                        eccezioni.append(f'{etichetta} su {nome}: {d} (eccezione dichiarata)')
                    else:
                        violazioni.append(f'{etichetta} su {nome}: scrittura fuori dal libro: {d}')
    for e in eccezioni:
        print(f'ECCEZIONE {e}')
    if violazioni:
        print(f'KO recinto ({eseguiti} esecuzioni)')
        for v in violazioni:
            print(f'  - {v}')
        return 1
    print(f'OK recinto: {eseguiti} esecuzioni, nessuna scrittura fuori dal libro')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

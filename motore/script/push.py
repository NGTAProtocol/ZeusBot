"""Push del ramo corrente con ripiego (comando «zb push»).

Uso: push.py [--cartella <dir>] [--remoto origin] [--tentativi 4] [--attesa 2] [--bundle-dir <dir>]
1. git push -u <remoto> <ramo>, fino a --tentativi volte, con attesa crescente (2, 4, 8, 16 s);
2. se non riesce: push dello stesso commit su un ramo alternativo <ramo>-salvataggio-<data-ora>;
3. se non riesce neppure quello: git bundle del ramo in --bundle-dir (predefinito: la cartella temporanea
   di sistema, fuori dal repository), con percorso e sha256;
4. messaggio finale chiaro: dove sta il commit e se il ramo è allineato a <remoto>.
Codice d'uscita: 0 ramo allineato; 3 salvato solo sul ramo alternativo; 4 salvato solo nel bundle;
5 niente salvato. Non fa commit e non cambia ramo.
"""
import datetime
import hashlib
import os
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True


def opzione(argv, nome, predefinito):
    return argv[argv.index(nome) + 1] if nome in argv and argv.index(nome) + 1 < len(argv) else predefinito


def git(cartella, *args):
    p = subprocess.run(['git', '-C', cartella, *args], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def ultima_riga(testo):
    righe = [r for r in testo.splitlines() if r.strip()]
    return righe[-1] if righe else '(nessun messaggio)'


def main(argv):
    cartella = opzione(argv, '--cartella', os.getcwd())
    remoto = opzione(argv, '--remoto', 'origin')
    tentativi = int(opzione(argv, '--tentativi', '4'))
    attesa = float(opzione(argv, '--attesa', '2'))
    c, ramo = git(cartella, 'rev-parse', '--abbrev-ref', 'HEAD')
    if c or ramo == 'HEAD':
        print(f'FERMO: nessun ramo corrente in {cartella} ({ramo}).', file=sys.stderr)
        return 5
    _, commit = git(cartella, 'rev-parse', 'HEAD')
    errore = ''
    for i in range(1, tentativi + 1):
        c, out = git(cartella, 'push', '-u', remoto, ramo)
        if c == 0:
            _, sul_remoto = git(cartella, 'ls-remote', remoto, f'refs/heads/{ramo}')
            allineato = sul_remoto.split()[:1] == [commit]
            print(f'Push riuscito al tentativo {i}: {ramo} {commit[:7]} su {remoto}.')
            print(f'Ramo allineato a {remoto}: {"sì" if allineato else "no"}.')
            return 0 if allineato else 5
        errore = ultima_riga(out)
        print(f'Tentativo {i}/{tentativi} non riuscito: {errore}')
        if i < tentativi:
            secondi = attesa * 2 ** (i - 1)
            print(f'  attendo {secondi:g} s')
            time.sleep(secondi)
    alt = f'{ramo}-salvataggio-{datetime.datetime.now():%Y%m%d-%H%M%S}'
    c, out = git(cartella, 'push', remoto, f'HEAD:refs/heads/{alt}')
    if c == 0:
        print(f'PUSH NON RIUSCITO su {ramo} (ultimo errore: {errore}).')
        print(f'Il commit {commit[:7]} è salvato su {remoto}/{alt}. Ramo {ramo} allineato a {remoto}: no.')
        print(f'Quando {remoto} risponde: zb push (poi si può cancellare {alt}).')
        return 3
    errore_alt = ultima_riga(out)
    cartella_bundle = opzione(argv, '--bundle-dir', tempfile.gettempdir())
    os.makedirs(cartella_bundle, exist_ok=True)
    nome = os.path.basename(git(cartella, 'rev-parse', '--show-toplevel')[1]) or 'repo'
    percorso = os.path.join(cartella_bundle, f'{nome}-{ramo.replace("/", "_")}-{commit[:7]}.bundle')
    c, out = git(cartella, 'bundle', 'create', percorso, ramo)
    if c == 0 and os.path.isfile(percorso):
        sha = hashlib.sha256(open(percorso, 'rb').read()).hexdigest()
        print(f'PUSH NON RIUSCITO su {ramo} (ultimo errore: {errore}) né su {alt} ({errore_alt}).')
        print(f'Il commit {commit[:7]} è salvato nel bundle {percorso}')
        print(f'sha256 {sha}')
        print(f'Ramo {ramo} allineato a {remoto}: no. Il bundle sta nel container: si perde se la sessione finisce.')
        print(f'Per recuperarlo: git fetch {percorso} {ramo}:{ramo}')
        return 4
    print(f'PUSH NON RIUSCITO su {ramo} ({errore}), né su {alt} ({errore_alt}); bundle non creato '
          f'({ultima_riga(out)}).')
    print(f'Il commit {commit[:7]} esiste solo in {cartella}. Ramo {ramo} allineato a {remoto}: no.')
    return 5


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

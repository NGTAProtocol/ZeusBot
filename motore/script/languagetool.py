"""Installazione stabile di LanguageTool per il livello (b) di «zb ortografia» (comando «zb languagetool»).

Uso: python3 -B languagetool.py stato
     python3 -B languagetool.py installa [--cartella <dir>] [--versione 6.8]
- installa: in una cartella FUORI dal repository (predefinita: <cartella temporanea di sistema>/zb-languagetool)
  scrive un pom.xml con languagetool-commandline, language-it e language-en della stessa versione e lancia
  «mvn -q -B dependency:copy-dependencies -DoutputDirectory=lib» (serve Java e Maven; si scarica da Maven
  Central, mai da languagetool.org). Poi prova la riga di comando su una frase italiana con un errore noto e
  stampa la riga da usare: export ZB_LANGUAGETOOL=<dir>/lib
- stato: dice se ZB_LANGUAGETOOL è impostata, quanti .jar ci sono e se il livello (b) gira davvero (stessa prova).
Se Maven Central risponde 403 o 429 non insiste: il livello (b) resta saltato e «zb ortografia» lo dice.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

POM = """<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>
<groupId>zb</groupId><artifactId>languagetool</artifactId><version>1</version>
<dependencies>
<dependency><groupId>org.languagetool</groupId><artifactId>languagetool-commandline</artifactId><version>{v}</version></dependency>
<dependency><groupId>org.languagetool</groupId><artifactId>language-it</artifactId><version>{v}</version></dependency>
<dependency><groupId>org.languagetool</groupId><artifactId>language-en</artifactId><version>{v}</version></dependency>
</dependencies></project>
"""
FRASE = 'Questa e una prova con un errrore.'


def prova(lib):
    """(ok, dettaglio): LanguageTool trova almeno un errore nella frase di prova italiana."""
    if not shutil.which('java'):
        return False, 'java non installato'
    if not glob.glob(os.path.join(lib, '*.jar')):
        return False, f'nessun .jar in {lib}'
    with tempfile.TemporaryDirectory(prefix='zb-lt-prova-') as d:
        f = os.path.join(d, 'prova.txt')
        open(f, 'w', encoding='utf-8').write(FRASE)
        r = subprocess.run(['java', '-cp', os.path.join(lib, '*'), 'org.languagetool.commandline.Main', '-l', 'it',
                            '--json', f], capture_output=True, text=True, timeout=600)
    try:
        m = json.loads(r.stdout[r.stdout.index('{'):]).get('matches', [])
    except ValueError:
        return False, (r.stderr or r.stdout).strip()[:200]
    return bool(m), f'{len(m)} segnalazioni sulla frase di prova ({", ".join(x["rule"]["id"] for x in m[:3])})'


def main(argv):
    args = comune.argomenti(argv)
    azione = args[0] if args else 'stato'
    if azione == 'stato':
        lib = os.environ.get('ZB_LANGUAGETOOL')
        if not lib:
            print('ZB_LANGUAGETOOL non impostata: livello (b) di zb ortografia saltato. Installazione: zb languagetool installa')
            return 1
        ok, det = prova(lib)
        print(f'ZB_LANGUAGETOOL={lib}: {len(glob.glob(os.path.join(lib, "*.jar")))} .jar; livello (b) '
              + ('funzionante' if ok else 'NON funzionante') + f' — {det}')
        return 0 if ok else 1
    if azione == 'installa':
        dest = argv[argv.index('--cartella') + 1] if '--cartella' in argv else os.path.join(tempfile.gettempdir(), 'zb-languagetool')
        dest = os.path.realpath(dest)
        if comune.dentro(comune.radice_git(comune.radice_motore()), dest):
            raise comune.ErroreMotore('LanguageTool non va nel repository: scegli una cartella fuori (--cartella).')
        v = argv[argv.index('--versione') + 1] if '--versione' in argv else '6.8'
        if not shutil.which('mvn'):
            raise comune.ErroreMotore('Maven (mvn) non installato.')
        os.makedirs(dest, exist_ok=True)
        open(os.path.join(dest, 'pom.xml'), 'w', encoding='utf-8').write(POM.format(v=v))
        lib = os.path.join(dest, 'lib')
        if not glob.glob(os.path.join(lib, 'languagetool-core-*.jar')):
            r = subprocess.run(['mvn', '-q', '-B', 'dependency:copy-dependencies', '-DoutputDirectory=lib'], cwd=dest,
                               capture_output=True, text=True, timeout=1800)
            if r.returncode:
                raise comune.ErroreMotore('Download da Maven Central non riuscito (403/429 o rete): '
                                          + (r.stdout + r.stderr).strip()[-300:])
        ok, det = prova(lib)
        print(f'LanguageTool {v} in {lib} ({len(glob.glob(os.path.join(lib, "*.jar")))} .jar): '
              + ('funzionante' if ok else 'NON funzionante') + f' — {det}')
        print(f'export ZB_LANGUAGETOOL={lib}')
        return 0 if ok else 1
    raise comune.ErroreMotore('Uso: languagetool.py stato | installa [--cartella <dir>] [--versione 6.8]')


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

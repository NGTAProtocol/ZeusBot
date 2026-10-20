"""LanguageTool per il livello (b) di «zb ortografia» (comando unico «zb languagetool»).

Uso: python3 -B languagetool.py stato
     python3 -B languagetool.py installa [--cartella <dir>] [--versione 6.8]
     python3 -B languagetool.py verifica
- installa (da motore, 971b6df, con le lingue di ccr): in <dir> (predefinita: $ZB_LANGUAGETOOL/.. se impostata,
  altrimenti ~/.cache/zb-languagetool; mai dentro il repository) scrive pom.xml con languagetool-commandline,
  language-it e language-en della stessa versione e copia i .jar con Maven: prima dalla cache locale (~/.m2,
  senza rete), poi da Maven Central (mai da languagetool.org). Scarica in <dir>/lib.nuova e sostituisce
  <dir>/lib solo dopo la verifica: una cartella che funziona non si perde mai. Se la versione non c'è prova quelle
  di ripiego (VERSIONI). Se <dir>/lib è già pronta e verificata non fa niente (si rilancia in ogni sessione
  nuova). Alla fine stampa la riga export ZB_LANGUAGETOOL=<dir>/lib da mettere nell'ambiente.
- verifica: con ZB_LANGUAGETOOL impostata, controlla java, i .jar e la frase di prova «Qual'è il problema?»:
  codice 0 solo se LanguageTool la segnala con una regola grammaticale italiana (GR_…).
- stato (ccr): dice se ZB_LANGUAGETOOL è impostata, quanti .jar ci sono e se il livello (b) gira davvero.
Serve rete verso Maven Central, Java 17 o più e Maven. Se Maven Central risponde 403 o 429 si ferma con il
messaggio e non insiste: si resta con Hunspell e la lista di controllo (livelli a e c di zb ortografia).
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

# languagetool-commandline su Maven Central: 6.8 e 6.7 tra le recenti (6.4-6.6 non pubblicate; verificato il 2026-10-15)
VERSIONI = ['6.8', '6.7']
POM = """<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>
<groupId>zb</groupId><artifactId>languagetool</artifactId><version>1</version>
<dependencies>
<dependency><groupId>org.languagetool</groupId><artifactId>languagetool-commandline</artifactId><version>{v}</version></dependency>
<dependency><groupId>org.languagetool</groupId><artifactId>language-it</artifactId><version>{v}</version></dependency>
<dependency><groupId>org.languagetool</groupId><artifactId>language-en</artifactId><version>{v}</version></dependency>
</dependencies></project>
"""
FRASE_PROVA = "Qual'è il problema?"       # regola grammaticale italiana GR_04_001: prova che le regole it sono caricate


def verifica(lib):
    """(ok, messaggio) per la cartella dei .jar: la frase di prova va segnalata con una regola GR_…."""
    if not lib or not os.path.isdir(lib):
        return False, f'cartella dei .jar assente: {lib or "(ZB_LANGUAGETOOL non impostata)"}'
    if not glob.glob(os.path.join(lib, '*.jar')):
        return False, f'nessun .jar in {lib}'
    if not shutil.which('java'):
        return False, 'java non installato'
    with tempfile.TemporaryDirectory(prefix='zb-lt-verifica-') as tmp:
        f = os.path.join(tmp, 'prova.txt')
        open(f, 'w', encoding='utf-8').write(FRASE_PROVA + '\n')
        r = subprocess.run(['java', '-cp', os.path.join(lib, '*'), 'org.languagetool.commandline.Main', '-l', 'it',
                            '--json', f], capture_output=True, text=True, timeout=600)
    try:
        dati = json.loads(r.stdout[r.stdout.index('{'):])
    except ValueError:
        return False, f'LanguageTool non parte: {(r.stderr or r.stdout).strip()[:300]}'
    regole = [m['rule']['id'] for m in dati.get('matches', [])]
    ver = (dati.get('software') or {}).get('version', '?')
    if not any(x.startswith('GR_') for x in regole):
        return False, f'LanguageTool {ver} non segnala la frase di prova «{FRASE_PROVA}» (regole: {regole or "nessuna"})'
    return True, f'LanguageTool {ver}: frase di prova segnalata ({", ".join(regole)}), livello (b) pronto'


def installa(cartella, versioni):
    rad = comune.radice_git(comune.radice_motore())
    if rad != '/' and comune.dentro(rad, os.path.realpath(cartella)):
        raise comune.ErroreMotore(f'{cartella} è dentro il repository: LanguageTool non va mai nel repository.')
    lib = os.path.join(cartella, 'lib')
    ok, msg = verifica(lib)
    if ok:
        return lib, f'già pronto ({msg})'
    if not shutil.which('mvn'):
        raise comune.ErroreMotore('Maven (mvn) non installato: serve per scaricare LanguageTool da Maven Central.')
    os.makedirs(cartella, exist_ok=True)
    nuova = os.path.join(cartella, 'lib.nuova')
    ultimo = ''
    for v in versioni:
        open(os.path.join(cartella, 'pom.xml'), 'w', encoding='utf-8').write(POM.format(v=v))
        for modo in (['-o'], ['-U']):              # prima la cache locale, poi la rete
            shutil.rmtree(nuova, ignore_errors=True)
            r = subprocess.run(['mvn', '-q', '-B', *modo, 'dependency:copy-dependencies', f'-DoutputDirectory={nuova}'],
                               cwd=cartella, capture_output=True, text=True, timeout=1800)
            testo = r.stdout + r.stderr
            if r.returncode == 0:
                ok, msg = verifica(nuova)
                if ok:
                    shutil.rmtree(lib, ignore_errors=True)
                    os.replace(nuova, lib)
                    n = len(glob.glob(os.path.join(lib, '*.jar')))
                    return lib, f'versione {v} ({"cache locale" if modo == ["-o"] else "Maven Central"}, {n} .jar); {msg}'
                ultimo = msg
            elif modo == ['-U'] and ('status code: 403' in testo or 'status code: 429' in testo or ' 429 ' in testo):
                shutil.rmtree(nuova, ignore_errors=True)
                raise comune.ErroreMotore('Maven Central risponde 403 o 429: non insistere, riprova più tardi. Intanto si '
                                          'resta con Hunspell e la lista di controllo (livelli a e c di zb ortografia).')
            else:
                ultimo = next((x for x in testo.splitlines() if 'Could not' in x), testo.strip()[-300:])
    shutil.rmtree(nuova, ignore_errors=True)
    raise comune.ErroreMotore(f'LanguageTool non installato (versioni provate: {", ".join(versioni)}): {ultimo}')


def main(argv):
    args = comune.argomenti(argv)
    azione = args[0] if args else 'stato'
    if azione == 'stato':
        lib = os.environ.get('ZB_LANGUAGETOOL')
        if not lib:
            print('ZB_LANGUAGETOOL non impostata: livello (b) di zb ortografia saltato. Installazione: zb languagetool installa')
            return 1
        ok, det = verifica(lib)
        print(f'ZB_LANGUAGETOOL={lib}: {len(glob.glob(os.path.join(lib, "*.jar")))} .jar; livello (b) '
              + ('funzionante' if ok else 'NON funzionante') + f' — {det}')
        return 0 if ok else 1
    if azione == 'verifica':
        ok, msg = verifica(os.environ.get('ZB_LANGUAGETOOL'))
        print(('OK ' if ok else 'KO ') + msg)
        return 0 if ok else 1
    if azione != 'installa':
        raise comune.ErroreMotore('Uso: languagetool.py stato | installa [--cartella <dir>] [--versione X] | verifica')
    if '--cartella' in argv:
        cartella = os.path.realpath(argv[argv.index('--cartella') + 1])
    elif os.environ.get('ZB_LANGUAGETOOL'):
        cartella = os.path.dirname(os.path.realpath(os.environ['ZB_LANGUAGETOOL']))
    else:
        cartella = os.path.join(os.path.expanduser('~'), '.cache', 'zb-languagetool')
    versioni = ([argv[argv.index('--versione') + 1]] if '--versione' in argv else []) + VERSIONI
    lib, msg = installa(cartella, list(dict.fromkeys(versioni)))
    print(f'LanguageTool: {msg}')
    print(f'export ZB_LANGUAGETOOL={lib}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

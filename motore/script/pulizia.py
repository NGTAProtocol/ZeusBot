"""Pulizia di un libro (passo 6). Di default solo ELENCO: non cancella nulla.

Uso: python3 -B pulizia.py <libro> [--applica]
Candidati, con il peso:
- file temporanei: __pycache__/, _build/, *.pyc, *.tmp, *~;
- marker di sessioni vecchie in .zb/ (letto-*, compattato-* di sessioni diverse da quella corrente);
- PDF intermedi (nome con bozza, prova, tmp, temp, intermedio, vecchio, old);
- cartelle vuote;
- copie identiche byte per byte (sha256): per ogni gruppo ne tiene una e propone di togliere le altre.
Mai toccati: 04-manoscritto/, 01-originale/, .git/, libro.yaml, stato.yaml, i documenti approvati
in stato.yaml. Nessun comando git: la cronologia resta com'è.
--applica (solo dopo l'«ok» dell'autore) cancella esattamente gli elementi elencati.
"""
import hashlib
import os
import re
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

PROTETTE = ('04-manoscritto', '01-originale', '.git')
PROTETTI = ('libro.yaml', 'stato.yaml')
TEMP_DIR = ('__pycache__', '_build')
TEMP_FILE = re.compile(r'(\.pyc|\.tmp|~)$')
PDF_INTERMEDIO = re.compile(r'(bozza|prova|tmp|temp|intermedio|vecchio|old)', re.I)


def peso(p):
    if os.path.isfile(p):
        return os.path.getsize(p)
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(p) for f in fs)


def leggibile(n):
    for u in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or u == 'GB':
            return f'{n:.0f} {u}' if u == 'B' else f'{n:.1f} {u}'
        n /= 1024


def candidati(cartella):
    """[(percorso relativo, motivo, byte)], ordinati; nessun elemento protetto."""
    protetti = set(PROTETTI)
    ps = os.path.join(cartella, 'stato.yaml')
    if os.path.isfile(ps):
        protetti |= set((comune.leggi_yaml(ps) or {}).get('documenti_approvati') or {})
    sid, _ = comune.sessione_corrente()

    def protetto(rel):
        parti = rel.replace(os.sep, '/').split('/')
        return parti[0] in PROTETTE or rel.replace(os.sep, '/') in protetti

    out, visti = [], {}
    for radice, dirs, files in os.walk(cartella, topdown=True):
        rel_r = os.path.relpath(radice, cartella)
        rel_r = '' if rel_r == '.' else rel_r
        for d in list(dirs):
            rel = os.path.join(rel_r, d)
            if protetto(rel):
                dirs.remove(d)
            elif d in TEMP_DIR:
                out.append((rel + '/', 'temporaneo', peso(os.path.join(radice, d))))
                dirs.remove(d)
        for f in files:
            rel = os.path.join(rel_r, f)
            p = os.path.join(radice, f)
            if protetto(rel):
                continue
            if rel_r == '.zb' and re.match(r'^(letto|compattato)-', f) and not f.endswith(f'-{sid}'):
                out.append((rel, 'marker di una sessione vecchia', peso(p)))
            elif TEMP_FILE.search(f):
                out.append((rel, 'temporaneo', peso(p)))
            elif f.lower().endswith('.pdf') and PDF_INTERMEDIO.search(f):
                out.append((rel, 'PDF intermedio', peso(p)))
            elif os.path.getsize(p) > 0 and rel_r != '.zb':
                with open(p, 'rb') as fh:
                    visti.setdefault(hashlib.sha256(fh.read()).hexdigest(), []).append(rel)
    gia = {c[0] for c in out}
    # copie identiche: si tiene la prima in ordine (percorso più corto, poi alfabetico), anche se protetta
    for radice, _, files in os.walk(cartella):
        rel_r = os.path.relpath(radice, cartella)
        if rel_r.split(os.sep)[0] in ('04-manoscritto', '01-originale') and files:
            for f in files:
                p = os.path.join(radice, f)
                if os.path.getsize(p) > 0:
                    with open(p, 'rb') as fh:
                        h = hashlib.sha256(fh.read()).hexdigest()
                    if h in visti:
                        visti[h].append(os.path.join(rel_r, f))
    for h, gruppo in visti.items():
        if len(gruppo) < 2:
            continue
        gruppo.sort(key=lambda r: (not protetto(r), len(r), r))
        tieni = gruppo[0]
        for r in gruppo[1:]:
            if not protetto(r) and r not in gia:
                out.append((r, f'copia identica di {tieni} (sha256 {h[:12]})', peso(os.path.join(cartella, r))))
    # cartelle vuote, anche quelle che resterebbero vuote dopo aver tolto i candidati
    via = {c[0].rstrip('/') for c in out}
    for radice, dirs, files in os.walk(cartella, topdown=False):
        rel = os.path.relpath(radice, cartella)
        if rel == '.' or protetto(rel) or rel in via or any(rel.startswith(v + os.sep) for v in via):
            continue
        resto = [x for x in os.listdir(radice) if os.path.join(rel, x) not in via]
        if not resto:
            out.append((rel + '/', 'cartella vuota' if not os.listdir(radice) else 'cartella vuota dopo la pulizia', 0))
            via.add(rel)
    return sorted(out)


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: pulizia.py <libro> [--applica]')
    cartella = comune.trova_libro(args[0])
    c = candidati(cartella)
    applica = '--applica' in argv
    print(f'Libro: {cartella}')
    print(f'{"CANCELLO" if applica else "ELENCO (nessuna cancellazione)"}: {len(c)} elementi, '
          f'{leggibile(sum(x[2] for x in c))}')
    for rel, motivo, b in c:
        print(f'- {rel} — {motivo} — {leggibile(b)}')
    if not applica:
        if c:
            print('Per cancellare, dopo l\'«ok» dell\'autore: zb pulizia <libro> --applica')
        return 0
    for rel, _, _ in c:
        p = os.path.join(cartella, rel.rstrip('/'))
        if not comune.dentro(cartella, p) or os.path.realpath(p) == os.path.realpath(cartella):
            raise comune.ErroreMotore(f'Percorso fuori dal libro, non cancellato: {rel}')
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
    print('Cancellati. Salva con un commit (i file tracciati risultano tolti in git status).')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

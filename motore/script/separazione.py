"""Controlla che il motore non contenga libri (proposta B.9).

Uso: separazione.py [--radice <cartella motore>]
Fallisce (codice 1, con file e riga) se:
1. sotto motore/ c'è un percorso con un segmento «libri», o un file identico
   (stesso sha256) a un file di una cartella di libro (con libro.yaml) fuori da motore/;
2. in un file di motore/ compare, come parola intera e senza distinguere le
   maiuscole, una voce di dati/nomi_vietati.txt (il file stesso è escluso);
3. in motore/ c'è un libro.yaml fuori da prove/mini-libro/, prove/mini-libro-romance/ e dal modello vuoto modelli/libro.yaml.
Eccezione: i font di stampa/font/ elencati in FONTI.yaml con lo sha256 registrato.
"""
import hashlib
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

AMMESSI_LIBRO_YAML = ('prove/mini-libro/libro.yaml', 'prove/mini-libro-romance/libro.yaml',
                      'modelli/libro.yaml')  # modello vuoto, usato solo come esempio commentato


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for blocco in iter(lambda: f.read(1 << 16), b''):
            h.update(blocco)
    return h.hexdigest()


def file_sotto(cartella, escludi=()):
    for radice, dirs, files in os.walk(cartella):
        dirs[:] = [d for d in dirs if d != '.git' and os.path.join(radice, d) not in escludi]
        for f in files:
            yield os.path.join(radice, f)


def font_ammessi(motore):
    p = os.path.join(motore, 'stampa', 'font', 'FONTI.yaml')
    if not os.path.isfile(p):
        return set()
    ok = set()
    for voce in comune.leggi_yaml(p) or []:
        for f in voce.get('file') or []:
            ok.add((os.path.join(motore, 'stampa', 'font', f['nome']), f.get('sha256')))
    return ok


def controlla(motore):
    errori = []
    motore = os.path.realpath(motore)
    file_motore = list(file_sotto(motore))
    rel = {p: os.path.relpath(p, motore) for p in file_motore}
    # 1a. segmento «libri»
    for p, r in rel.items():
        if 'libri' in r.split(os.sep):
            errori.append(f'{r}: percorso con un segmento «libri»')
    # 1b. copie di file di libri esterni
    base = comune.radice_git(motore)
    if base == '/':
        base = os.path.dirname(motore)
    cartelle_libro = set()
    for p in file_sotto(base, escludi=(motore,)):
        if os.path.basename(p) == 'libro.yaml':
            cartelle_libro.add(os.path.dirname(p))
    hash_libri = {}
    for c in cartelle_libro:
        for p in file_sotto(c):
            if os.path.getsize(p) > 0:
                hash_libri.setdefault(sha256(p), p)
    fonts = font_ammessi(motore)
    for p, r in rel.items():
        if os.path.getsize(p) == 0:
            continue
        h = sha256(p)
        if h in hash_libri and (p, h) not in fonts:
            errori.append(f'{r}: copia identica di {os.path.relpath(hash_libri[h], base)}')
    # 2. nomi vietati
    nv = os.path.join(motore, 'dati', 'nomi_vietati.txt')
    voci = []
    if os.path.isfile(nv):
        for riga in open(nv, encoding='utf-8'):
            riga = riga.strip()
            if riga and not riga.startswith('#'):
                voci.append(riga)
    if voci:
        regex = re.compile(r'(?i)(?<!\w)(' + '|'.join(re.escape(v) for v in voci) + r')(?!\w)')
        for p, r in rel.items():
            if os.path.realpath(p) == os.path.realpath(nv):
                continue
            try:
                righe = open(p, encoding='utf-8').read().splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for n, riga in enumerate(righe, 1):
                m = regex.search(riga)
                if m:
                    errori.append(f'{r}:{n}: nome vietato «{m.group(1)}»')
    # 3. libro.yaml fuori posto
    for p, r in rel.items():
        if os.path.basename(p) == 'libro.yaml' and r.replace(os.sep, '/') not in AMMESSI_LIBRO_YAML:
            errori.append(f'{r}: libro.yaml fuori dai mini-libri di prova')
    return errori


def main(argv):
    errori = controlla(comune.radice_motore())
    if errori:
        print('KO separazione')
        for e in errori:
            print(f'  - {e}')
        return 1
    print('OK separazione: nessun libro dentro motore/')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

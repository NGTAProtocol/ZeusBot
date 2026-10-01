"""Compone 05-output/il-padre-del-mostro-completo.md dai capitoli di 04-manoscritto/."""
import re, glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
AUTORE = 'F.R. Faraone'
COPYRIGHT = ('© 2026 F.R. Faraone. Tutti i diritti riservati.',
             "Quest'opera è frutto di fantasia. Nomi, personaggi, luoghi e fatti sono invenzione "
             "dell'autore o usati in modo fittizio; ogni somiglianza con persone, vive o scomparse, "
             "o con fatti realmente accaduti è puramente casuale.")
files = sorted(glob.glob('04-manoscritto/*.md'))
num = lambda f: int(re.match(r'04-manoscritto/(\d+)', f).group(1))
partnames = {1: 'Parte prima — La creatura', 13: 'Parte seconda — La figlia',
             25: 'Parte terza — Calma apparente', 38: 'Parte quarta — Il padre del mostro'}
ends = {1: 12, 13: 24, 25: 37, 38: 53}
toc = ['## Indice', '', '- Prologo']
for start, pn in partnames.items():
    toc.append(f'- **{pn}**')
    for n in range(start, ends[start] + 1):
        toc.append(f'  - Capitolo {n}')
body = []
for f in files:
    n = num(f)
    lines = open(f).read().rstrip('\n').split('\n')
    out = [l for l in lines if not re.match(r'^# (Prologo|Parte )', l) and not re.match(r'^## \d+\s*$', l)]
    while out and out[0].strip() == '':
        out.pop(0)
    txt = '\n'.join(out).replace('\n---\n', '\n\n<p align="center">* * *</p>\n\n')
    if n == 0:
        body.append('# Prologo\n\n' + txt)
    else:
        if n in partnames:
            body.append(f'<div style="page-break-before: always"></div>\n\n# {partnames[n]}')
        body.append(f'## Capitolo {n}\n\n' + txt)
doc = (f'# Il padre del mostro\n\n### {AUTORE}\n\n*Romanzo*\n\n---\n\n'
       f'<div class="copyright">\n\n{COPYRIGHT[0]}\n\n{COPYRIGHT[1]}\n\n</div>\n\n---\n\n'
       + '\n'.join(toc) + '\n\n---\n\n' + '\n\n---\n\n'.join(body) + '\n\n<p align="center">FINE</p>\n')
open('05-output/il-padre-del-mostro-completo.md', 'w').write(doc)
print('capitoli', doc.count('## Capitolo'))

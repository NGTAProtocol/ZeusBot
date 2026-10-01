"""Impagina 05-output/il-padre-del-mostro-completo.md in PDF A5 (EB Garamond).

Pagine iniziali (frontespizio, copyright, indice) senza numero; la numerazione
parte da 1 al prologo. Scrive 05-output/il-padre-del-mostro-completo.pdf e
05-output/il-padre-del-mostro-rivisto.pdf (identici).
"""
import re, os, shutil, subprocess, markdown, pymupdf
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(HERE, '_build')
os.makedirs(BUILD, exist_ok=True)
AUTORE = 'F.R. Faraone'
TITOLO = 'Il padre del mostro'
src = open(os.path.join(ROOT, '05-output/il-padre-del-mostro-completo.md')).read()
src = src.replace('<div style="page-break-before: always"></div>\n\n', '')
src = src.replace('<p align="center">* * *</p>', '<p class="scene">* * *</p>')
src = src.replace('<p align="center">FINE</p>', '<p class="fine">FINE</p>')
html = markdown.markdown(src)
html = re.sub(r'<hr\s*/?>', '', html)
body = html[html.index('<h1>Prologo</h1>'):]
body = re.sub(r'<h1>(Parte [^<]+)</h1>',
              lambda m: '<h1 class="part">' + m.group(1).replace(' — ', '<br><span class="parttitle">') + '</span></h1>', body)
body = body.replace('<h1>Prologo</h1>', '<h2 class="chapter">Prologo</h2>', 1)
body = re.sub(r'<h2>(Capitolo \d+)</h2>', r'<h2 class="chapter">\1</h2>', body)
body = re.sub(r'(<h2 class="chapter">[^<]+</h2>\s*)<p><em>(.*?)</em></p>', r'\1<p class="dateline"><em>\2</em></p>', body)
# l'ultimo paragrafo di ogni capitolo resta con il precedente (niente righe sole in una pagina nuova)
body = re.sub(r'<p>((?:(?!<p>).)*?)</p>(\s*(?:<h2 class="chapter">|<h1 class="part">|<p class="fine">))',
              r'<p class="last">\1</p>\2', body, flags=re.S)
m = re.search(r'<div class="copyright">\s*(.*?)\s*</div>', src, re.S)
copy_pars = [p.strip() for p in m.group(1).split('\n\n') if p.strip()]
fonts_css = open(os.path.join(HERE, 'fonts.css')).read().replace("url('fonts/", "url('" + HERE + "/fonts/")
css = fonts_css + """
@page{size:A5;margin:22mm 18mm 22mm 18mm;}
html{font-family:'EB Garamond',Garamond,'Liberation Serif',serif;font-size:11.5pt;line-height:1.5;color:#111;}
body{margin:0;}
p{margin:0;text-indent:1.2em;text-align:justify;hyphens:auto;orphans:2;widows:2;}
h1,h2{font-weight:400;text-align:center;}
.booktitle{font-size:26pt;margin-top:55mm;letter-spacing:.04em;}
.author{text-align:center;text-indent:0;font-size:14pt;margin-top:8mm;}
.genre{text-align:center;text-indent:0;font-style:italic;font-size:12pt;margin-top:4mm;}
.copyright{page-break-before:always;padding-top:120mm;font-size:9pt;line-height:1.4;}
.copyright p{text-indent:0;text-align:left;hyphens:manual;margin-bottom:3mm;}
.toc-title{page-break-before:always;font-size:16pt;margin-top:10mm;margin-bottom:6mm;}
.toc .tr{display:flex;align-items:baseline;line-height:1.45;font-size:10.5pt;break-inside:avoid;}
.toc .tr .dots{flex:1;border-bottom:1px dotted #999;margin:0 .35em;transform:translateY(-.25em);}
.toc .part{margin-top:.8em;font-weight:600;}
.toc .part em{font-weight:400;}
.toc .cols{columns:2;column-gap:8mm;}
h1.part{page-break-before:always;font-size:13pt;letter-spacing:.12em;text-transform:uppercase;margin-top:60mm;}
h1.part .parttitle{display:block;text-transform:none;letter-spacing:0;font-size:20pt;font-style:italic;margin-top:5mm;}
h2.chapter{page-break-before:always;font-size:16pt;margin-top:22mm;margin-bottom:3mm;}
body > h2.chapter:first-child{page-break-before:auto;}
p.dateline{text-align:center;text-indent:0;margin-bottom:10mm;font-size:10.5pt;}
h2.chapter + p.dateline + p, p.scene + p{text-indent:0;}
p.scene{text-align:center;text-indent:0;margin:.9em 0;letter-spacing:.3em;}
p.last{break-before:avoid-page;page-break-before:avoid;}
p.fine{text-align:center;text-indent:0;margin-top:20mm;letter-spacing:.2em;}
"""
parts = [('Parte prima', 'La creatura', 1, 12), ('Parte seconda', 'La figlia', 13, 24),
         ('Parte terza', 'Calma apparente', 25, 37), ('Parte quarta', 'Il padre del mostro', 38, 53)]

def page(name, inner):
    path = os.path.join(BUILD, name + '.html')
    open(path, 'w').write(f'<!doctype html><html lang="it"><head><meta charset="utf-8"><title>{TITOLO}</title>'
                          f'<style>{css}</style></head><body>{inner}</body></html>')
    return path

def pdf(html_path, out, footer):
    subprocess.run(['node', os.path.join(HERE, 'print.js'), html_path, out, ''],
                   check=True, env={**os.environ, 'NODE_PATH_PW': subprocess.run('npm root -g', shell=True, capture_output=True, text=True).stdout.strip() + '/playwright'})
    return pymupdf.open(out)

# 1) corpo del libro: numerazione da 1 al prologo
dbody = pdf(page('corpo', body), os.path.join(BUILD, 'corpo.pdf'), False)
found = {}
for k, p in enumerate(dbody):
    L = [x.strip() for x in p.get_text().strip().split('\n')]
    if len(L) < 2:
        continue
    if re.fullmatch(r'Capitolo \d+|Prologo', L[0]) and not re.fullmatch(r'\d+', L[1]):
        found.setdefault(L[0], k + 1)
    if re.match(r'(?i)parte (prima|seconda|terza|quarta)$', L[0]):
        found.setdefault('Parte ' + L[0].split()[1].lower(), k + 1)

# 2) pagine iniziali senza numero
g = lambda key: str(found[key])
rows = [f'<div class="tr top"><span>Prologo</span><span class="dots"></span><span>{g("Prologo")}</span></div>']
for a, b, s, e in parts:
    rows.append(f'<div class="tr part"><span>{a} — <em>{b}</em></span><span class="dots"></span><span>{g(a)}</span></div><div class="cols">')
    for n in range(s, e + 1):
        rows.append(f'<div class="tr"><span>Capitolo {n}</span><span class="dots"></span><span>{g("Capitolo %d" % n)}</span></div>')
    rows.append('</div>')
front_html = (f'<section class="titlepage"><h1 class="booktitle">{TITOLO}</h1><p class="author">{AUTORE}</p>'
              f'<p class="genre">Romanzo</p></section>'
              '<section class="copyright">' + ''.join(f'<p>{c}</p>' for c in copy_pars) + '</section>'
              '<section class="toc"><h2 class="toc-title">Indice</h2>' + ''.join(rows) + '</section>')
dfront = pdf(page('iniziali', front_html), os.path.join(BUILD, 'iniziali.pdf'), False)

# 3) numeri di pagina nel font del testo (EB Garamond), da 1 al prologo
from fontTools.ttLib import TTFont
ttf = os.path.join(BUILD, 'ebg-regular.ttf')
_f = TTFont(os.path.join(HERE, 'fonts/ebg-normal-400-latin-static.woff2')); _f.flavor = None; _f.save(ttf)
for k, p in enumerate(dbody):
    n = str(k + 1)
    fnt = pymupdf.Font(fontfile=ttf)
    w = fnt.text_length(n, fontsize=9)
    p.insert_font(fontname='EBG', fontfile=ttf)
    p.insert_text(((p.rect.width - w) / 2, p.rect.height - 12 * 72 / 25.4), n, fontname='EBG', fontsize=9, color=(0.2, 0.2, 0.2))

# 4) unione e metadati
book = pymupdf.open()
book.insert_pdf(dfront)
book.insert_pdf(dbody)
book.set_metadata({'title': TITOLO, 'author': AUTORE, 'subject': 'Romanzo', 'creator': 'Il padre del mostro — impaginazione',
                   'producer': 'Chromium / PyMuPDF', 'keywords': ''})
out = os.path.join(ROOT, '05-output/il-padre-del-mostro-completo.pdf')
book.save(out, garbage=4, deflate=True)
shutil.copyfile(out, os.path.join(ROOT, '05-output/il-padre-del-mostro-rivisto.pdf'))
print('pagine totali', book.page_count, '| iniziali', dfront.page_count, '| corpo', dbody.page_count, '| voci indice', len(found))

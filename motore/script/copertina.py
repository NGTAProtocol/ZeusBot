"""Copertina intera del cartaceo (comando «zb copertina <libro> [--pagine N]», 2026-10-27).

Calcola le misure KDP della copertina intera (abbondanza + quarta + costola + prima + abbondanza) dal numero di
pagine del PDF di stampa (05-output/<titolo>.pdf) o da --pagine, e genera 06-pubblicazione/copertina/copertina.pdf,
una copertina tipografica della misura esatta: titolo, sottotitolo e autore sulla prima (sopra l'immagine
00-progetto/copertina.jpg|png se c'è), testo sulla costola solo oltre la soglia di pagine, quarta da
06-pubblicazione/quarta.md (le righe di testo, senza commenti) con il riquadro del codice a barre lasciato libero.
Scrive anche misure.md. I valori vengono da dati/kdp.yaml, sezione «copertina» (da verificare dall'autore come
tutti i dati KDP). Per una copertina illustrata: brief in 06-pubblicazione/brief-copertina.md (agente grafico).
"""
import html
import os
import re
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

CARTELLA = os.path.join('06-pubblicazione', 'copertina')
FONDO = '#1d1c1a'
FONDO_RGB = (0x1d / 255, 0x1c / 255, 0x1a / 255)
IMMAGINI = [os.path.join('00-progetto', f'copertina.{e}') for e in ('jpg', 'jpeg', 'png')]


def pagine_pdf(cartella, libro):
    pdf = os.path.join(cartella, '05-output', f'{comune.nome_file(libro["titolo"])}.pdf')
    if not os.path.isfile(pdf):
        return None
    import pymupdf
    with pymupdf.open(pdf) as d:
        return d.page_count


def misure(libro, pagine):
    """Misure in pollici della copertina intera."""
    k = comune.kdp()['copertina']
    larg, alt = libro['formato']['pagina_pollici']
    carta = libro['formato'].get('carta') or 'crema'
    costola = round(pagine * k['spessore_pagina_pollici'][carta], 4)
    b = k['bleed_pollici']
    return {'pagine': pagine, 'carta': carta, 'trim': [larg, alt], 'costola': costola, 'bleed': b,
            'larghezza': round(2 * b + 2 * larg + costola, 4), 'altezza': round(2 * b + alt, 4),
            'testo_costola': pagine >= k['testo_costola_pagine_min'], 'sicurezza': k['margine_sicurezza_pollici'],
            'margine_costola': k['margine_costola_pollici'], 'codice_a_barre': k['codice_a_barre_pollici']}


def testo_quarta(cartella):
    p = os.path.join(cartella, '06-pubblicazione', 'quarta.md')
    if not os.path.isfile(p):
        return []
    t = re.sub(r'<!--.*?-->', '', open(p, encoding='utf-8').read(), flags=re.S)
    return [r.strip() for r in t.splitlines() if r.strip() and not r.lstrip().startswith('#')]


def html_copertina(libro, m, immagine, quarta):
    font_dir = 'file://' + os.path.join(comune.radice_motore(), 'stampa', 'font')
    e = html.escape
    b, (w, h), c, s = m['bleed'], m['trim'], m['costola'], m['sicurezza']
    bx, by = m['codice_a_barre']
    fondo = (f"background: url('file://{immagine}') center / cover no-repeat;" if immagine else f'background: {FONDO};')
    costola = ''
    if m['testo_costola']:
        costola = (f'<div class="costola"><span>{e(libro["titolo"])}</span><span class="aut">'
                   f'{e(libro["autore"])}</span></div>')
    sotto = f'<h2>{e(libro["sottotitolo"])}</h2>' if libro.get('sottotitolo') else ''
    paragrafi = ''.join(f'<p>{e(r)}</p>' for r in quarta)
    return f'''<!doctype html><html lang="{libro.get('lingua', 'it')}"><head><meta charset="utf-8"><style>
@font-face {{ font-family: 'Libro'; src: url('{font_dir}/EBGaramond-Regular.ttf'); }}
@font-face {{ font-family: 'Libro'; font-style: italic; src: url('{font_dir}/EBGaramond-Italic.ttf'); }}
@font-face {{ font-family: 'Libro'; font-weight: 600; src: url('{font_dir}/EBGaramond-SemiBold.ttf'); }}
@page {{ size: {m['larghezza']}in {m['altezza']}in; margin: 0; }}
html, body {{ margin: 0; font-family: 'Libro', serif; color: #f4efe6; }}
.tutto {{ position: relative; width: {m['larghezza']}in; height: {m['altezza']}in; background: {FONDO}; overflow: hidden; }}
.quarta {{ position: absolute; left: {b + s + .25}in; top: {b + s + .5}in; width: {w - 2 * s - .5}in; height: {h - 2 * s - 1}in; }}
.quarta p {{ font-size: 11pt; line-height: 1.45; margin: 0 0 .7em; text-align: justify; hyphens: auto; }}
.barre {{ position: absolute; left: {b + w - s - bx}in; top: {b + h - s - by}in; width: {bx}in; height: {by}in;
  background: #fff; }}
.costola {{ position: absolute; left: {b + w}in; top: {b}in; width: {c}in; height: {h}in; display: flex;
  align-items: center; justify-content: space-between; writing-mode: vertical-rl; padding: .4in 0;
  box-sizing: border-box; font-size: {max(7, min(14, c * 72 - 2 * m['margine_costola'] * 72 - 2)):.1f}pt; }}
.costola .aut {{ font-style: italic; }}
.prima {{ position: absolute; left: {b + w + c}in; top: 0; width: {w + b}in; height: {m['altezza']}in; {fondo} }}
.prima .testi {{ position: absolute; left: {s}in; right: {b + s}in; top: {b + s}in; bottom: {b + s}in; text-align: center; }}
.prima h1 {{ font-weight: 600; font-size: 30pt; line-height: 1.15; margin: .9in 0 0; letter-spacing: .02em; }}
.prima h2 {{ font-weight: 400; font-style: italic; font-size: 15pt; margin: .2in 0 0; }}
.prima .autore {{ position: absolute; bottom: .5in; left: 0; right: 0; font-size: 16pt; letter-spacing: .12em; }}
</style></head><body><div class="tutto">
<div class="quarta">{paragrafi}</div><div class="barre"></div>{costola}
<div class="prima"><div class="testi"><h1>{e(libro['titolo'])}</h1>{sotto}<div class="autore">{e(libro['autore'])}</div></div></div>
</div></body></html>'''


def formato_esatto(pdf, m):
    """Chromium arrotonda il formato a multipli di 1/96″: la pagina torna alla misura esatta, contenuto fermo in alto a
    sinistra, senza scalare (come impagina.formato_esatto). Lo scarto finisce nell'abbondanza."""
    import pymupdf
    W, H = m['larghezza'] * 72, m['altezza'] * 72
    with pymupdf.open(pdf) as doc:
        pg = doc[0]
        dy = H - pg.mediabox.y1
        if abs(dy) > 1e-6:
            prima, dopo = doc.get_new_xref(), doc.get_new_xref()
            for x, t in ((prima, f'q 1 0 0 1 0 {dy:.4f} cm\n'), (dopo, '\nQ\n')):
                doc.update_object(x, '<<>>')
                doc.update_stream(x, t.encode())
            cont = ' '.join(f'{x} 0 R' for x in pg.get_contents())
            doc.xref_set_key(pg.xref, 'Contents', f'[{prima} 0 R {cont} {dopo} 0 R]')
        pg.set_mediabox(pymupdf.Rect(0, 0, W, H))
        pg.set_cropbox(pg.mediabox)
        # lo scarto dell'arrotondamento resta bianco: lo copre il colore di fondo, sotto il contenuto
        pg.draw_rect(pg.rect, color=None, fill=FONDO_RGB, overlay=False)
        doc.saveIncr() if doc.can_save_incrementally() else doc.save(pdf + '.tmp')
    if os.path.isfile(pdf + '.tmp'):
        os.replace(pdf + '.tmp', pdf)


def copertina(cartella, libro, pagine):
    import impagina
    m = misure(libro, pagine)
    immagine = next((os.path.join(cartella, r) for r in IMMAGINI if os.path.isfile(os.path.join(cartella, r))), None)
    quarta = testo_quarta(cartella)
    os.makedirs(os.path.join(cartella, CARTELLA), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        h = os.path.join(tmp, 'copertina.html')
        open(h, 'w', encoding='utf-8').write(html_copertina(libro, m, immagine, quarta))
        import subprocess
        pdf = os.path.join(cartella, CARTELLA, 'copertina.pdf')
        r = subprocess.run(['node', os.path.join(comune.radice_motore(), 'stampa', 'print.js'), h, pdf],
                           env=dict(os.environ, NODE_PATH=impagina.node_path()), capture_output=True, text=True)
        if r.returncode != 0:
            raise comune.ErroreMotore('Render della copertina fallito: ' + (r.stderr.strip().splitlines() or ['?'])[-1])
        formato_esatto(pdf, m)
    righe = [f'# Copertina intera — {libro["titolo"]}', '',
             f'Valori di dati/kdp.yaml («copertina», stato: {comune.kdp()["copertina"]["stato"]}): da confrontare con il '
             'calcolatore delle copertine di KDP prima del caricamento.', '',
             '| Misura | Valore |', '|---|---|',
             f'| Pagine | {m["pagine"]} (carta {m["carta"]}) |',
             f'| Formato (trim) | {m["trim"][0]} × {m["trim"][1]} pollici |',
             f'| Costola | {m["costola"]} pollici ({round(m["costola"] * 25.4, 2)} mm) |',
             f'| Abbondanza | {m["bleed"]} pollici per lato |',
             f'| Copertina intera | {m["larghezza"]} × {m["altezza"]} pollici |',
             f'| Testo sulla costola | {"sì" if m["testo_costola"] else "no (troppe poche pagine)"} |',
             f'| Immagine della prima | {os.path.relpath(immagine, cartella) if immagine else "nessuna (fondo pieno)"} |',
             f'| Quarta | {len(quarta)} paragrafi da 06-pubblicazione/quarta.md |' if quarta else
             '| Quarta | vuota: scrivila in 06-pubblicazione/quarta.md (agente grafico) |',
             f'| Codice a barre | riquadro libero {m["codice_a_barre"][0]} × {m["codice_a_barre"][1]} pollici in basso a destra della quarta |']
    comune.scrivi(cartella, os.path.join(CARTELLA, 'misure.md'), '\n'.join(righe) + '\n')
    return m, pdf


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: zb copertina <libro> [--pagine N]')
    cartella, libro, _ = comune.carica_libro(args[0])
    pagine = int(argv[argv.index('--pagine') + 1]) if '--pagine' in argv else pagine_pdf(cartella, libro)
    if not pagine:
        raise comune.ErroreMotore('Numero di pagine sconosciuto: prima «zb impagina <libro>», oppure --pagine N.')
    m, pdf = copertina(cartella, libro, pagine)
    print(f'Copertina: {os.path.relpath(pdf, cartella)} ({m["larghezza"]} × {m["altezza"]} pollici, costola '
          f'{m["costola"]}″, testo sulla costola: {"sì" if m["testo_costola"] else "no"}); misure in '
          f'{CARTELLA}/misure.md.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

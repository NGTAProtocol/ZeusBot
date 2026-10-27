"""Copertina del cartaceo KDP (comando «zb copertina <libro> [--pagine N]», 2026-10-27).

Le pagine vengono SOLO dal PDF di stampa definitivo (05-output/<titolo>.pdf): la costola dipende da lì, e
l'impronta (sha256) del PDF finisce in copertina.yaml; se l'interno cambia, la copertina va rifatta (`coerente`,
usata da «zb finale»). Con --pagine N si fa solo un'anteprima (in copertina/anteprima/), mai da caricare.

Immagini dell'autore in 00-progetto/copertina/:
- intera.(jpg|png): copertina intera già fatta (quarta + costola + prima, con abbondanza): usata così com'è.
- prima.(jpg|png): solo la prima, già finita (titolo e autore compresi, nessun testo aggiunto): il motore compone
  costola e quarta con il colore del bordo dell'immagine, testo della quarta da 06-pubblicazione/quarta.md e
  riquadro libero per il codice a barre. Facoltativa quarta.(jpg|png) come fondo della quarta.
- nessuna immagine: copertina tipografica (titolo, sottotitolo, autore).
Controlli: risoluzione (≥ 300 DPI alla misura di stampa; sotto 150 KO) e proporzioni (intera: scarto > 1,5% KO).

Scrive in 06-pubblicazione/copertina/: copertina.pdf, anteprima-con-guide.png, modello-kdp.pdf e modello-kdp.png
(il modello con abbondanza, taglio, costola, zona sicura e codice a barre, da dare al grafico), misure.md con la
scheda di caricamento KDP, copertina.yaml. Valori da dati/kdp.yaml, sezione «copertina» (da verificare).
"""
import hashlib
import html
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

CARTELLA = os.path.join('06-pubblicazione', 'copertina')
IMMAGINI = os.path.join('00-progetto', 'copertina')
FONDO = (0x1d, 0x1c, 0x1a)
ESTENSIONI = ('jpg', 'jpeg', 'png')


def pdf_interno(cartella, libro):
    return os.path.join(cartella, '05-output', f'{comune.nome_file(libro["titolo"])}.pdf')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def pagine_pdf(cartella, libro):
    pdf = pdf_interno(cartella, libro)
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


def immagine(cartella, nome):
    for e in ESTENSIONI:
        p = os.path.join(cartella, IMMAGINI, f'{nome}.{e}')
        if os.path.isfile(p):
            return p
    if nome == 'prima':  # posto di prima del 27 ottobre
        return next((p for e in ESTENSIONI if os.path.isfile(p := os.path.join(cartella, '00-progetto', f'copertina.{e}'))), None)
    return None


def controlli_immagine(p, area, nome, rigida):
    """[(esito, testo)]: risoluzione alla misura di stampa e proporzioni (area in pollici)."""
    import pymupdf
    pix = pymupdf.Pixmap(p)
    w, h = pix.width, pix.height
    dpi = int(min(w / area[0], h / area[1]))
    serve = f'{round(area[0] * 300)} × {round(area[1] * 300)} px'
    out = []
    if dpi < 150:
        out.append(('KO', f'{nome}: {w} × {h} px = {dpi} DPI alla misura di stampa (minimo 300: servono {serve})'))
    elif dpi < 300:
        out.append(('AVVISO', f'{nome}: {dpi} DPI alla misura di stampa (consigliati 300: {serve})'))
    else:
        out.append(('OK', f'{nome}: {w} × {h} px, {dpi} DPI'))
    scarto = abs((w / h) / (area[0] / area[1]) - 1)
    if scarto > 0.015:
        msg = (f'{nome}: proporzioni {w}:{h} diverse dall\'area {area[0]:.4f} × {area[1]:.4f}″ ({scarto:.1%}): '
               + ('rifarla sul modello-kdp' if rigida else 'l\'immagine verrà adattata e un bordo può tagliarsi'))
        out.append(('KO' if rigida else 'AVVISO', msg))
    return out


def colore_bordo(p):
    """Colore medio della striscia sinistra della prima (continua sulla costola e sulla quarta)."""
    import pymupdf
    pix = pymupdf.Pixmap(p)
    if pix.alpha or pix.n != 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        if pix.alpha:
            pix = pymupdf.Pixmap(pix, 0)
    xs = range(0, max(1, pix.width // 50), max(1, pix.width // 500))
    ys = range(0, pix.height, max(1, pix.height // 200))
    px = [pix.pixel(x, y)[:3] for x in xs for y in ys]
    return tuple(round(sum(c[i] for c in px) / len(px)) for i in range(3))


def chiaro(rgb):
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2] > 150


def testo_quarta(cartella):
    p = os.path.join(cartella, '06-pubblicazione', 'quarta.md')
    if not os.path.isfile(p):
        return []
    t = re.sub(r'<!--.*?-->', '', open(p, encoding='utf-8').read(), flags=re.S)
    return [r.strip() for r in t.splitlines() if r.strip() and not r.lstrip().startswith('#')]


def html_copertina(libro, m, img, quarta):
    """img: {'intera'|'prima'|'quarta': percorso}. fondo/testo: colore del bordo della prima, se c'è."""
    font_dir = 'file://' + os.path.join(comune.radice_motore(), 'stampa', 'font')
    e = html.escape
    b, (w, h), c, s = m['bleed'], m['trim'], m['costola'], m['sicurezza']
    bx, by = m['codice_a_barre']
    fondo = m['fondo']
    testo = '#1d1c1a' if chiaro(fondo) else '#f4efe6'
    if img.get('intera'):
        corpo = f'<img class="intera" src="file://{img["intera"]}">'
    else:
        costola = ''
        if m['testo_costola']:
            costola = (f'<div class="costola"><span>{e(libro["titolo"])}</span><span class="aut">'
                       f'{e(libro["autore"])}</span></div>')
        if img.get('prima'):
            prima = f'<img class="prima" src="file://{img["prima"]}">'
        else:
            sotto = f'<h2>{e(libro["sottotitolo"])}</h2>' if libro.get('sottotitolo') else ''
            prima = (f'<div class="prima"><div class="testi"><h1>{e(libro["titolo"])}</h1>{sotto}'
                     f'<div class="autore">{e(libro["autore"])}</div></div></div>')
        fq = f'<img class="fondo-quarta" src="file://{img["quarta"]}">' if img.get('quarta') else ''
        paragrafi = ''.join(f'<p>{e(r)}</p>' for r in quarta)
        corpo = f'{fq}<div class="quarta">{paragrafi}</div><div class="barre"></div>{costola}{prima}'
    return f'''<!doctype html><html lang="{libro.get('lingua', 'it')}"><head><meta charset="utf-8"><style>
@font-face {{ font-family: 'Libro'; src: url('{font_dir}/EBGaramond-Regular.ttf'); }}
@font-face {{ font-family: 'Libro'; font-style: italic; src: url('{font_dir}/EBGaramond-Italic.ttf'); }}
@font-face {{ font-family: 'Libro'; font-weight: 600; src: url('{font_dir}/EBGaramond-SemiBold.ttf'); }}
@page {{ size: {m['larghezza']}in {m['altezza']}in; margin: 0; }}
html, body {{ margin: 0; font-family: 'Libro', serif; color: {testo}; }}
.tutto {{ position: relative; width: {m['larghezza']}in; height: {m['altezza']}in; background: rgb{fondo}; overflow: hidden; }}
img {{ position: absolute; display: block; }}
.intera {{ left: 0; top: 0; width: 100%; height: 100%; }}
.fondo-quarta {{ left: 0; top: 0; width: {w + b}in; height: {m['altezza']}in; object-fit: cover; }}
.quarta {{ position: absolute; left: {b + s + .25}in; top: {b + s + .5}in; width: {w - 2 * s - .5}in; height: {h - 2 * s - 1 - by}in; }}
.quarta p {{ font-size: 11pt; line-height: 1.45; margin: 0 0 .7em; text-align: justify; hyphens: auto; }}
.barre {{ position: absolute; left: {b + w - s - bx}in; top: {b + h - s - by}in; width: {bx}in; height: {by}in; background: #fff; }}
.costola {{ position: absolute; left: {b + w}in; top: {b}in; width: {c}in; height: {h}in; display: flex;
  align-items: center; justify-content: space-between; writing-mode: vertical-rl; padding: .4in 0;
  box-sizing: border-box; font-size: {max(7, min(14, c * 72 - 2 * m['margine_costola'] * 72 - 2)):.1f}pt; }}
.costola .aut {{ font-style: italic; }}
.prima {{ position: absolute; left: {b + w + c}in; top: 0; width: {w + b}in; height: {m['altezza']}in; object-fit: cover; }}
.prima .testi {{ position: absolute; left: {s}in; right: {b + s}in; top: {b + s}in; bottom: {b + s}in; text-align: center; }}
.prima h1 {{ font-weight: 600; font-size: 30pt; line-height: 1.15; margin: .9in 0 0; letter-spacing: .02em; }}
.prima h2 {{ font-weight: 400; font-style: italic; font-size: 15pt; margin: .2in 0 0; }}
.prima .autore {{ position: absolute; bottom: .5in; left: 0; right: 0; font-size: 16pt; letter-spacing: .12em; }}
</style></head><body><div class="tutto">{corpo}</div></body></html>'''


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
        pg.draw_rect(pg.rect, color=None, fill=tuple(v / 255 for v in m['fondo']), overlay=False)
        doc.saveIncr() if doc.can_save_incrementally() else doc.save(pdf + '.tmp')
    if os.path.isfile(pdf + '.tmp'):
        os.replace(pdf + '.tmp', pdf)


def guide(pg, m, etichette):
    """Disegna in punti le guide KDP sulla pagina: abbondanza, taglio, costola, zona sicura, codice a barre."""
    import pymupdf
    P = 72
    b, (w, h), c, s = m['bleed'] * P, [v * P for v in m['trim']], m['costola'] * P, m['sicurezza'] * P
    bx, by = [v * P for v in m['codice_a_barre']]
    W, H = m['larghezza'] * P, m['altezza'] * P
    rosa, nero, blu, verde = (.9, .3, .55), (0, 0, 0), (.1, .35, .85), (.1, .6, .2)
    if etichette:
        for r in (pymupdf.Rect(0, 0, W, b), pymupdf.Rect(0, H - b, W, H), pymupdf.Rect(0, 0, b, H), pymupdf.Rect(W - b, 0, W, H)):
            pg.draw_rect(r, color=None, fill=(1, .85, .9))
    pg.draw_rect(pymupdf.Rect(b, b, W - b, H - b), color=nero, width=.8)
    pg.draw_line((b + w, 0), (b + w, H), color=blu, width=.8)
    pg.draw_line((b + w + c, 0), (b + w + c, H), color=blu, width=.8)
    for x0 in (b, b + w + c):
        pg.draw_rect(pymupdf.Rect(x0 + s, b + s, x0 + w - s, b + h - s), color=verde, width=.6, dashes='[4 3] 0')
    pg.draw_rect(pymupdf.Rect(b + w - s - bx, b + h - s - by, b + w - s, b + h - s), color=rosa, width=.8,
                 fill=(1, 1, 1) if etichette else None)
    if not etichette:
        return
    px = lambda v: round(v / P * 300)  # noqa: E731
    righe = [(b + s + 4, b + s + 14, 'QUARTA DI COPERTINA'), (b + w + c + s + 4, b + s + 14, 'PRIMA DI COPERTINA'),
             (b + w - s - bx + 4, b + h - s - by + 14, 'CODICE A BARRE (KDP)'),
             (b + s + 4, H / 2 - 30, f'Copertina intera {m["larghezza"]} x {m["altezza"]} in = {px(W)} x {px(H)} px a 300 DPI'),
             (b + s + 4, H / 2 - 16, f'Pagine {m["pagine"]}, carta {m["carta"]}, costola {m["costola"]} in ({px(c)} px)'),
             (b + s + 4, H / 2 - 2, f'Prima: {m["trim"][0] + m["bleed"]} x {m["altezza"]} in con abbondanza = {px(w + b)} x {px(H)} px'),
             (b + s + 4, H / 2 + 12, 'Rosa: abbondanza (si taglia). Nero: taglio. Blu: costola. Verde: zona sicura per i testi.')]
    if m.get('anteprima'):
        righe.append((b + s + 4, H / 2 + 26, 'ANTEPRIMA: pagine provvisorie, rifare dal PDF definitivo'))
    for x, y, t in righe:
        pg.insert_text((x, y), t, fontsize=8, color=nero)


def modello(cartella, m, pdf_copertina, dove):
    """modello-kdp.pdf/.png (guide su bianco) e anteprima-con-guide.png (guide sulla copertina)."""
    import pymupdf
    out = os.path.join(cartella, dove)
    with pymupdf.open() as d:
        pg = d.new_page(width=m['larghezza'] * 72, height=m['altezza'] * 72)
        guide(pg, m, True)
        d.save(os.path.join(out, 'modello-kdp.pdf'))
        pg.get_pixmap(dpi=300).save(os.path.join(out, 'modello-kdp.png'))
    with pymupdf.open(pdf_copertina) as d:
        guide(d[0], m, False)
        d[0].get_pixmap(dpi=60).save(os.path.join(out, 'anteprima-con-guide.png'))


def copertina(cartella, libro, pagine, anteprima=False):
    import impagina
    m = misure(libro, pagine)
    m['anteprima'] = anteprima
    b, (w, h) = m['bleed'], m['trim']
    img = {n: immagine(cartella, n) for n in ('intera', 'prima', 'quarta')}
    esiti = []
    if img['intera']:
        img['prima'] = img['quarta'] = None
        esiti += controlli_immagine(img['intera'], (m['larghezza'], m['altezza']), 'intera', True)
    if img['prima']:
        esiti += controlli_immagine(img['prima'], (w + b, m['altezza']), 'prima', False)
    if img['quarta']:
        esiti += controlli_immagine(img['quarta'], (w + b, m['altezza']), 'quarta', False)
    m['fondo'] = colore_bordo(img['prima']) if img['prima'] else FONDO
    quarta = testo_quarta(cartella)
    if not img['intera'] and not quarta:
        esiti.append(('AVVISO', 'quarta vuota: scrivila in 06-pubblicazione/quarta.md (agente grafico)'))
    dove = os.path.join(CARTELLA, 'anteprima') if anteprima else CARTELLA  # l'anteprima non tocca la copertina vera
    os.makedirs(os.path.join(cartella, dove), exist_ok=True)
    pdf = os.path.join(cartella, dove, 'copertina.pdf')
    with tempfile.TemporaryDirectory() as tmp:
        hp = os.path.join(tmp, 'copertina.html')
        open(hp, 'w', encoding='utf-8').write(html_copertina(libro, m, img, quarta))
        r = subprocess.run(['node', os.path.join(comune.radice_motore(), 'stampa', 'print.js'), hp, pdf],
                           env=dict(os.environ, NODE_PATH=impagina.node_path()), capture_output=True, text=True)
        if r.returncode != 0:
            raise comune.ErroreMotore('Render della copertina fallito: ' + (r.stderr.strip().splitlines() or ['?'])[-1])
    formato_esatto(pdf, m)
    modello(cartella, m, pdf, dove)
    tipo = 'intera dell\'autore' if img['intera'] else 'prima dell\'autore' if img['prima'] else 'tipografica'
    rel = lambda p: os.path.relpath(p, cartella) if p else '—'  # noqa: E731
    stato = comune.kdp()['copertina']['stato']
    righe = [f'# Copertina — {libro["titolo"]}', '',
             ('**ANTEPRIMA con pagine provvisorie (--pagine): non caricarla. Rifalla dopo «zb impagina» con '
              '«zb copertina <libro>».**' if anteprima else
              f'Pagine dal PDF di stampa {rel(pdf_interno(cartella, libro))} (impronta in copertina.yaml).'), '',
             f'Valori di dati/kdp.yaml («copertina», stato: {stato}): da confrontare con il calcolatore delle copertine '
             'di KDP prima del caricamento.', '',
             '| Misura | Valore |', '|---|---|',
             f'| Pagine | {m["pagine"]} (carta {m["carta"]}) |',
             f'| Formato (trim) | {w} × {h} pollici |',
             f'| Costola | {m["costola"]} pollici ({round(m["costola"] * 25.4, 2)} mm) |',
             f'| Abbondanza | {b} pollici per lato |',
             f'| Copertina intera | {m["larghezza"]} × {m["altezza"]} pollici = {round(m["larghezza"] * 300)} × '
             f'{round(m["altezza"] * 300)} px a 300 DPI |',
             f'| Prima con abbondanza | {w + b} × {m["altezza"]} pollici = {round((w + b) * 300)} × '
             f'{round(m["altezza"] * 300)} px a 300 DPI |',
             f'| Testo sulla costola | {"sì" if m["testo_costola"] else "no (troppe poche pagine)"} |',
             f'| Copertina | {tipo} ({rel(img["intera"] or img["prima"])}) |',
             f'| Codice a barre | riquadro libero {m["codice_a_barre"][0]} × {m["codice_a_barre"][1]} pollici in basso a '
             'destra della quarta |', '',
             '## Controlli', ''] + [f'- {x}: {t}' for x, t in esiti] + ['- OK: misura esatta del PDF'] + [
             '', '## File', '',
             f'- `{os.path.basename(pdf)}`: la copertina da caricare (PDF, una pagina, font incorporati).',
             '- `anteprima-con-guide.png`: come viene, con taglio (nero), costola (blu) e zona sicura (verde).',
             '- `modello-kdp.pdf` / `modello-kdp.png`: il modello da dare al grafico (300 DPI).', '',
             '## Scheda di caricamento KDP (copertina del cartaceo)', '',
             f'1. Formato: {w} × {h} pollici; carta {m["carta"]}; con abbondanza nell\'interno: '
             f'{"sì" if libro["formato"].get("bleed") else "no"}.',
             '2. «Copertina del libro»: «Carica una copertina già pronta per la stampa» → '
             f'`{os.path.basename(pdf)}`.',
             '3. Controlla nell\'anteprima di KDP che titolo e autore restino nella zona sicura e che il codice a barre '
             'cada nel riquadro bianco.',
             f'4. Se KDP indica una costola diversa da {m["costola"]}″, fermati: il numero di pagine o i dati non '
             'coincidono (rifare «zb impagina» e «zb copertina»).']
    comune.scrivi(cartella, os.path.join(dove, 'misure.md'), '\n'.join(righe) + '\n')
    if not anteprima:
        dati = {'pagine': pagine, 'pdf_interno_sha256': sha(pdf_interno(cartella, libro)), 'costola_pollici': m['costola'],
                'copertina_sha256': sha(pdf), 'tipo': tipo, 'esiti': [f'{x}: {t}' for x, t in esiti if x != 'OK']}
        import yaml
        comune.scrivi(cartella, os.path.join(CARTELLA, 'copertina.yaml'), yaml.safe_dump(dati, allow_unicode=True, sort_keys=False))
    return m, pdf, esiti


def coerente(cartella, libro):
    """KO (lista di testi) se la copertina manca, è di un altro interno o ha controlli KO: per «zb finale»."""
    y = os.path.join(cartella, CARTELLA, 'copertina.yaml')
    pdf = os.path.join(cartella, CARTELLA, 'copertina.pdf')
    if not (os.path.isfile(y) and os.path.isfile(pdf)):
        return ['copertina: manca (zb copertina <libro> dopo zb impagina)']
    d = comune.leggi_yaml(y) or {}
    interno = pdf_interno(cartella, libro)
    out = []
    if not os.path.isfile(interno) or sha(interno) != d.get('pdf_interno_sha256'):
        out.append('copertina: fatta su un altro PDF dell\'interno (pagine o costola cambiate): rifare zb copertina')
    if sha(pdf) != d.get('copertina_sha256'):
        out.append('copertina: copertina.pdf modificato dopo zb copertina: rifarla')
    out += [f'copertina: {e[4:]}' for e in d.get('esiti') or [] if e.startswith('KO: ')]
    return out


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: zb copertina <libro> [--pagine N]')
    cartella, libro, _ = comune.carica_libro(args[0])
    anteprima = '--pagine' in argv
    pagine = int(argv[argv.index('--pagine') + 1]) if anteprima else pagine_pdf(cartella, libro)
    if not pagine:
        raise comune.ErroreMotore('Manca il PDF di stampa: prima «zb impagina <libro>» (le pagine della costola vengono '
                                  'da lì); per un\'anteprima provvisoria: --pagine N.')
    m, pdf, esiti = copertina(cartella, libro, pagine, anteprima)
    for x, t in esiti:
        if x != 'OK':
            print(f'{x} {t}')
    print(f'Copertina{" (ANTEPRIMA, non caricarla)" if anteprima else ""}: {os.path.relpath(pdf, cartella)} '
          f'({m["larghezza"]} × {m["altezza"]} pollici, {m["pagine"]} pagine, costola {m["costola"]}″, testo sulla '
          f'costola: {"sì" if m["testo_costola"] else "no"}); modello KDP e misure in {os.path.dirname(os.path.relpath(pdf, cartella))}/.')
    return 1 if any(x == 'KO' for x, _ in esiti) else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

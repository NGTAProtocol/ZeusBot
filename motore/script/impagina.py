"""Impaginazione del PDF di stampa (proposta B.2, B.3).

Uso: python3 -B impagina.py <libro>
Legge <libro>/05-output/<titolo>-completo.md (prima: compila.py) e scrive
<libro>/05-output/<titolo>.pdf:
- md → HTML con stampa/modello.css (formato, margini, font, corpo da libro.yaml);
- render con Chromium (stampa/print.js), separato per pagine iniziali e corpo;
- margine interno = max(tabella KDP per il numero di pagine, margini_mm.interno_scelto);
  se il numero di pagine cambia fascia, si rifà il render;
- pagine iniziali (frontespizio, copyright, sommario) senza numero e in numero pari,
  così il corpo comincia su una pagina dispari;
- sommario con le pagine reali; numeri di pagina stampati con PyMuPDF al piede;
- formato esatto: Chromium arrotonda la pagina (5,83 × 8,27" diventa 5,833 × 8,263"); ogni pagina
  è riportata con PyMuPDF al trim di libro.yaml (più il bleed di dati/kdp.yaml, se previsto), senza
  scalare il contenuto e tenendolo fermo rispetto all'angolo in alto a sinistra;
- metadati Title, Author, Subject; font sottoinsiemi, senza date di creazione.
I file di lavoro stanno in una cartella temporanea fuori dal repository.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

MM = 25.4


def node_path():
    try:
        r = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True, check=True)
        return r.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return '/opt/node22/lib/node_modules'


def sezioni(md):
    """[(tipo, testo)] dalle righe <!-- zb:sezione tipo -->."""
    parti = re.split(r'^<!-- zb:sezione (\w+) -->\s*$', md, flags=re.M)
    return [(parti[i], parti[i + 1].strip()) for i in range(1, len(parti), 2)]


def tipografia_di_stampa(testo):
    """Apostrofi tipografici (’) e puntini (…) nella stampa, senza toccare il manoscritto. Le righe di markup
    (commenti, tag, immagini e link) restano com'erano."""
    out = []
    for r in testo.splitlines():
        if r.lstrip().startswith('<') or '](' in r:
            out.append(r)
            continue
        out.append(re.sub(r'(?<!\.)\.\.\.(?!\.)', '…', r.replace("'", '’')))
    return '\n'.join(out)


def html_sezione(tipo, testo):
    import markdown
    corpo = markdown.markdown(tipografia_di_stampa(testo), extensions=['md_in_html'])
    if tipo in ('capitolo', 'prologo', 'epilogo', 'interludio'):
        corpo = marca_primo(corpo)
    return f'<section class="{tipo}">\n{corpo}\n</section>'


def marca_primo(corpo):
    """Classe «primo» sul primo paragrafo di testo dopo il titolo (non la riga del sottotitolo tutta in corsivo né
    il separatore di scena): lo usano gli stili con il capolettera (stampa/stili/)."""
    for m in re.finditer(r'<p(?: class="[^"]*")?>(.*?)</p>', corpo, re.S):
        dentro = m.group(1).strip()
        if 'class="scena"' in m.group(0) or re.fullmatch(r'<em>.*</em>', dentro, re.S) or not dentro:
            continue
        return corpo[:m.start()] + '<p class="primo">' + dentro + '</p>' + corpo[m.end():]
    return corpo


def css(libro, interno_mm):
    f = libro['formato']
    m = f.get('margini_mm') or {}
    font = f.get('font') or {}
    valori = {
        'font_dir': 'file://' + os.path.join(comune.radice_motore(), 'stampa', 'font'),
        'larghezza': f['pagina_pollici'][0], 'altezza': f['pagina_pollici'][1],
        'alto': m.get('alto', 20), 'basso': m.get('basso', 20),
        'esterno': m.get('esterno', 16), 'interno': round(interno_mm, 2),
        'corpo': font.get('corpo_pt', 11), 'interlinea': font.get('interlinea', 1.45),
    }
    t = open(os.path.join(comune.radice_motore(), 'stampa', 'modello.css'), encoding='utf-8').read()
    stile = f.get('stile') or 'essenziale'
    ps = os.path.join(comune.radice_motore(), 'stampa', 'stili', f'{stile}.css')
    if stile != 'essenziale' and os.path.isfile(ps):        # stili dell'interno (2026-10-27)
        t += '\n' + open(ps, encoding='utf-8').read()
    for k, v in valori.items():
        t = t.replace('{{' + k + '}}', str(v))
    return t


def render(html_corpo, stile, tmp, nome, base=None):
    """base: cartella da cui risolvere i percorsi relativi (immagini delle appendici in 05-output/)."""
    h = os.path.join(tmp, nome + '.html')
    p = os.path.join(tmp, nome + '.pdf')
    testa = f'<base href="file://{base.rstrip("/")}/">' if base else ''
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f'<!doctype html><html lang="it"><head><meta charset="utf-8">{testa}<style>{stile}</style>'
                f'</head><body>{html_corpo}</body></html>')
    env = dict(os.environ, NODE_PATH=node_path())
    r = subprocess.run(['node', os.path.join(comune.radice_motore(), 'stampa', 'print.js'), h, p],
                       env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise comune.ErroreMotore('Render Chromium fallito: ' + (r.stderr.strip().splitlines() or ['?'])[-1])
    return p


def piana(riga):
    """Riga senza apostrofi tipografici: nel PDF «L'arena» esce come «L’arena»."""
    return riga.strip().replace('\u2019', "'").replace('\u2018', "'")


def pagine_inizio(pdf, titoli):
    """{titolo: indice di pagina (0-based)} della prima pagina con una riga uguale al titolo."""
    import pymupdf as fitz
    out = {}
    with fitz.open(pdf) as d:
        for i, pg in enumerate(d):
            righe = [piana(r) for r in pg.get_text('text').splitlines()]
            for t in titoli:
                if t not in out and piana(t) in righe:
                    out[t] = i
    return out


def formato_esatto(doc, libro):
    """Porta ogni pagina al formato esatto in punti PDF: trim di libro.yaml, più il bleed se previsto.
    Il contenuto non si scala. Resta fermo rispetto all'angolo in alto a sinistra (con il bleed si sposta
    di un bleed in basso e, sulle pagine pari, a destra, così il trim sta dentro l'area di bleed).
    MediaBox e CropBox coincidono e partono da 0, 0; TrimBox e BleedBox non si scrivono."""
    import pymupdf as fitz
    larg, alt = libro['formato']['pagina_pollici']
    bleed = comune.kdp()['cartaceo']['bleed_pollici'] if libro['formato'].get('bleed') else 0
    W, H = (larg + bleed) * 72, (alt + 2 * bleed) * 72
    for i, pg in enumerate(doc):
        mb = pg.mediabox
        # spostamento in coordinate PDF (y verso l'alto): l'alto della pagina passa da mb.y1 a H - bleed
        dx = (bleed * 72 if i % 2 else 0) - mb.x0
        dy = (H - bleed * 72) - mb.y1
        if abs(dx) > 1e-6 or abs(dy) > 1e-6:
            prima, dopo = doc.get_new_xref(), doc.get_new_xref()
            for x, s in ((prima, f'q 1 0 0 1 {dx:.4f} {dy:.4f} cm\n'), (dopo, '\nQ\n')):
                doc.update_object(x, '<<>>')
                doc.update_stream(x, s.encode())
            cont = ' '.join(f'{x} 0 R' for x in pg.get_contents())
            doc.xref_set_key(pg.xref, 'Contents', f'[{prima} 0 R {cont} {dopo} 0 R]')
        pg.set_mediabox(fitz.Rect(0, 0, W, H))
        pg.set_cropbox(fitz.Rect(0, 0, W, H))


def impagina(cartella, libro):
    import pymupdf as fitz
    md_rel = f'05-output/{comune.nome_file(libro["titolo"])}-completo.md'
    md_path = os.path.join(cartella, md_rel)
    if not os.path.isfile(md_path):
        raise comune.ErroreMotore(f'Manca {md_rel}: esegui prima compila.py')
    sez = sezioni(open(md_path, encoding='utf-8').read())
    iniziali = [(t, s) for t, s in sez if t in ('frontespizio', 'copyright', 'sommario')]
    corpo = [(t, s) for t, s in sez if t not in ('frontespizio', 'copyright', 'sommario')]
    sommario = next(s for t, s in iniziali if t == 'sommario')
    voci = [re.sub(r'^-\s+', '', r).strip() for r in sommario.splitlines() if r.startswith('- ')]
    titoli = [v.strip('*') for v in voci]
    m = libro['formato'].get('margini_mm') or {}
    scelto = m.get('interno_scelto', m.get('esterno', 16))
    tmp = tempfile.mkdtemp(prefix='zb-impagina-')
    try:
        html_corpo = '\n'.join(html_sezione(t, s) for t, s in corpo)
        interno = scelto
        for _ in range(3):
            pdf_corpo = render(html_corpo, css(libro, interno), tmp, 'corpo', os.path.dirname(md_path))
            with fitz.open(pdf_corpo) as d:
                n_corpo = d.page_count
            stima = n_corpo + 4
            richiesto = max(comune.kdp_interno_pollici(stima) * MM, scelto)
            if abs(richiesto - interno) < 0.01:
                break
            interno = richiesto
        inizio = pagine_inizio(pdf_corpo, titoli)
        mancanti = [t for t in titoli if t not in inizio]
        if mancanti:
            raise comune.ErroreMotore(f'Titoli del sommario non trovati nel PDF: {", ".join(mancanti)}')
        righe_somm = []
        for v, t in zip(voci, titoli):
            classe = 'voce parte' if v.startswith('**') else 'voce'
            righe_somm.append(f'<div class="{classe}"><span>{t}</span><span class="punti"></span>'
                              f'<span>{inizio[t] + 1}</span></div>')
        html_iniz = '\n'.join(html_sezione(t, s) for t, s in iniziali if t != 'sommario')
        html_iniz += '\n<section class="sommario"><h2>Sommario</h2>\n' + '\n'.join(righe_somm) + '\n</section>'
        pdf_iniz = render(html_iniz, css(libro, interno), tmp, 'iniziali')
        doc = fitz.open(pdf_iniz)
        if doc.page_count % 2:
            w, h = doc[0].rect.width, doc[0].rect.height
            doc.new_page(width=w, height=h)
        n_iniz = doc.page_count
        with fitz.open(pdf_corpo) as dc:
            doc.insert_pdf(dc)
        formato_esatto(doc, libro)
        font = os.path.join(comune.radice_motore(), 'stampa', 'font', 'EBGaramond-Regular.ttf')
        basso_pt = m.get('basso', 20) / MM * 72
        # numeri al centro del piede del trim: con il bleed il trim è spostato come il contenuto
        b = comune.kdp()['cartaceo']['bleed_pollici'] * 72 if libro['formato'].get('bleed') else 0
        for i in range(n_iniz, doc.page_count):
            pg = doc[i]
            num = str(i - n_iniz + 1)
            f = fitz.Font(fontfile=font)
            larg = f.text_length(num, fontsize=9)
            x0 = b if i % 2 else 0
            pg.insert_font(fontname='ZBNum', fontfile=font)
            pg.insert_text((x0 + (pg.rect.width - b - larg) / 2, b + (pg.rect.height - 2 * b) - basso_pt / 2), num,
                           fontname='ZBNum', fontsize=9, color=(0.2, 0.2, 0.2))
        doc.set_metadata({'title': libro['titolo'], 'author': libro['autore'],
                          'subject': libro.get('sottotitolo') or '', 'creator': 'motore', 'producer': 'motore',
                          'creationDate': '', 'modDate': '', 'keywords': ''})
        doc.subset_fonts()
        uscita = comune.percorso_in_libro(cartella, f'05-output/{comune.nome_file(libro["titolo"])}.pdf')
        doc.save(uscita, garbage=4, deflate=True, no_new_id=True)
        doc.close()
        # impronta del compilato usato: «zb finale» controlla che il PDF venga da questo testo
        comune.scrivi(cartella, '05-output/impronta-pdf.yaml', 'completo_md_sha256: ' + hashlib.sha256(
            open(md_path, encoding='utf-8').read().encode('utf-8')).hexdigest() + '\n')
        return uscita, n_iniz, interno
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: impagina.py <libro>')
    cartella, libro, _ = comune.carica_libro(args[0])
    uscita, n_iniz, interno = impagina(cartella, libro)
    print(f'scritto {uscita} (pagine iniziali: {n_iniz}, margine interno: {interno:.1f} mm)')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

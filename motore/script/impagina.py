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
- metadati Title, Author, Subject; font sottoinsiemi, senza date di creazione.
I file di lavoro stanno in una cartella temporanea fuori dal repository.
"""
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


def html_sezione(tipo, testo):
    import markdown
    corpo = markdown.markdown(testo, extensions=['md_in_html'])
    return f'<section class="{tipo}">\n{corpo}\n</section>'


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
    for k, v in valori.items():
        t = t.replace('{{' + k + '}}', str(v))
    return t


def render(html_corpo, stile, tmp, nome):
    h = os.path.join(tmp, nome + '.html')
    p = os.path.join(tmp, nome + '.pdf')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f'<!doctype html><html lang="it"><head><meta charset="utf-8"><style>{stile}</style>'
                f'</head><body>{html_corpo}</body></html>')
    env = dict(os.environ, NODE_PATH=node_path())
    r = subprocess.run(['node', os.path.join(comune.radice_motore(), 'stampa', 'print.js'), h, p],
                       env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise comune.ErroreMotore('Render Chromium fallito: ' + (r.stderr.strip().splitlines() or ['?'])[-1])
    return p


def pagine_inizio(pdf, titoli):
    """{titolo: indice di pagina (0-based)} della prima pagina con una riga uguale al titolo."""
    import pymupdf as fitz
    out = {}
    with fitz.open(pdf) as d:
        for i, pg in enumerate(d):
            righe = [r.strip() for r in pg.get_text('text').splitlines()]
            for t in titoli:
                if t not in out and t in righe:
                    out[t] = i
    return out


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
            pdf_corpo = render(html_corpo, css(libro, interno), tmp, 'corpo')
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
        font = os.path.join(comune.radice_motore(), 'stampa', 'font', 'EBGaramond-Regular.ttf')
        basso_pt = m.get('basso', 20) / MM * 72
        for i in range(n_iniz, doc.page_count):
            pg = doc[i]
            num = str(i - n_iniz + 1)
            f = fitz.Font(fontfile=font)
            larg = f.text_length(num, fontsize=9)
            pg.insert_font(fontname='ZBNum', fontfile=font)
            pg.insert_text(((pg.rect.width - larg) / 2, pg.rect.height - basso_pt / 2), num,
                           fontname='ZBNum', fontsize=9, color=(0.2, 0.2, 0.2))
        doc.set_metadata({'title': libro['titolo'], 'author': libro['autore'],
                          'subject': libro.get('sottotitolo') or '', 'creator': 'motore', 'producer': 'motore',
                          'creationDate': '', 'modDate': '', 'keywords': ''})
        doc.subset_fonts()
        uscita = comune.percorso_in_libro(cartella, f'05-output/{comune.nome_file(libro["titolo"])}.pdf')
        doc.save(uscita, garbage=4, deflate=True, no_new_id=True)
        doc.close()
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

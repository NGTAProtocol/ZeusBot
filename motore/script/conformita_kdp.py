"""Controllo di conformità KDP, sezioni 1-15 (proposta A.3-A.6, A.9).

Uso: python3 -B conformita_kdp.py <libro> [--pdf <file>] [--carta crema|bianca] [--bleed] [--oggi AAAA-MM-GG]
Legge libro.yaml (titolo, sottotitolo, serie, ebook, autore), 06-pubblicazione/scheda-amazon.md,
05-output/<titolo>-completo.md, il PDF (predefinito 05-output/<titolo>.pdf),
06-pubblicazione/ebook.docx (se ebook: true), 06-pubblicazione/conferme-autore.yaml e dati/kdp.yaml.
Scrive 06-pubblicazione/conformita-kdp.md: una riga OK/KO per sezione con la prova e gli avvisi.
Un controllo lasciato all'autore e non confermato è KO «da confermare dall'autore».
Codici d'uscita: 0 tutto OK; 1 almeno un KO; 2 nessun KO ma verifica delle direttive mai fatta o scaduta.
"""
import hashlib
import os
import re
import sys
import zipfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import kdp_verifica  # noqa: E402
import verifica_pdf  # noqa: E402

NOMI = {1: 'Titolo', 2: 'Sottotitolo', 3: 'Serie', 4: 'Descrizione', 5: 'Autore', 6: 'Editore',
        7: 'Parole chiave', 8: 'Pubblico e categorie', 9: 'Copertina', 10: 'ISBN', 11: 'Cartaceo',
        12: 'eBook', 13: 'Dichiarazione AI', 14: 'Contenuti', 15: 'Recensioni e promozione'}


class Sezione:
    def __init__(self, n):
        self.n, self.ko, self.avvisi, self.prove = n, [], [], []

    def KO(self, t):
        self.ko.append(t)

    def avviso(self, t):
        self.avvisi.append(t)

    def prova(self, t):
        self.prove.append(t)

    @property
    def esito(self):
        return 'KO' if self.ko else 'OK'


def leggi_scheda(p):
    """{'campi': {...}, 'descrizione': str, 'parole chiave': [...], 'categorie': [...]} o None."""
    if not os.path.isfile(p):
        return None
    testo = re.sub(r'<!--.*?-->', '', open(p, encoding='utf-8').read(), flags=re.S)
    parti = re.split(r'^## (.+)$', testo, flags=re.M)
    campi = {}
    for r in parti[0].splitlines():
        m = re.match(r'^([A-Za-zÀ-ÿ ]+):\s*(.*)$', r)
        if m:
            campi[m.group(1).strip().lower()] = m.group(2).strip()
    sez = {parti[i].strip().lower(): parti[i + 1] for i in range(1, len(parti), 2)}
    elenco = lambda s: [m.group(1).strip() for m in re.finditer(r'(?m)^\d+\.[ \t]*(\S.*)$', s or '')]
    return {'campi': campi, 'descrizione': (sez.get('descrizione') or '').strip(),
            'parole chiave': elenco(sez.get('parole chiave')), 'categorie': elenco(sez.get('categorie'))}


def vietate(testo, k):
    voci = k['metadati']['parole_vietate']
    rx = re.compile(r'(?i)(?<!\w)(' + '|'.join(re.escape(v) for v in sorted(voci, key=len, reverse=True)) + r')(?!\w)')
    return [m.group(1) for m in rx.finditer(testo or '')]


def vuoto_vietato(valore, k):
    return (valore or '').strip().lower() in [v.lower() for v in k['metadati']['valori_vuoti_vietati']]


def tag_html(testo):
    return re.findall(r'</?\s*([a-zA-Z][a-zA-Z0-9]*)', testo or '')


def controlla(cartella, libro, argv):
    k = comune.kdp()
    m = k['metadati']
    base = comune.nome_file(libro['titolo'])
    pub = os.path.join(cartella, '06-pubblicazione')
    scheda = leggi_scheda(os.path.join(pub, 'scheda-amazon.md'))
    pc = os.path.join(pub, 'conferme-autore.yaml')
    conferme = (comune.leggi_yaml(pc) or {}) if os.path.isfile(pc) else {}
    md_p = os.path.join(cartella, '05-output', f'{base}-completo.md')
    md = open(md_p, encoding='utf-8').read() if os.path.isfile(md_p) else None
    pdf = os.path.join(cartella, '05-output', f'{base}.pdf')
    if '--pdf' in argv:
        pdf = os.path.realpath(argv[argv.index('--pdf') + 1])
    info = verifica_pdf.pdfinfo(pdf) if os.path.isfile(pdf) else None
    S = {n: Sezione(n) for n in NOMI}
    campi = (scheda or {}).get('campi', {})
    if scheda is None:
        for n in (1, 2, 3, 4, 5, 6, 7, 8):
            S[n].KO('manca 06-pubblicazione/scheda-amazon.md')

    # 1 Titolo
    t = libro['titolo']
    S[1].prova(f'«{t}»')
    if vietate(t, k) or vuoto_vietato(t, k):
        S[1].KO(f'parole vietate o valore vuoto: {vietate(t, k) or t}')
    if tag_html(t):
        S[1].KO('tag HTML nel titolo')
    if scheda is not None and campi.get('titolo') != t:
        S[1].KO(f'scheda: «{campi.get("titolo")}», libro.yaml: «{t}»')
    if info is None:
        S[1].KO('PDF assente')
    elif info.get('Title') != t:
        S[1].KO(f'PDF Title «{info.get("Title")}» diverso')
    if md is None:
        S[1].KO('manoscritto compilato assente (compila.py)')
    elif not re.search(r'(?m)^# ' + re.escape(t) + r'\s*$', md):
        S[1].KO('frontespizio con un titolo diverso')

    # 2 Sottotitolo
    st = libro.get('sottotitolo') or ''
    S[2].prova(f'«{st}»' if st else 'nessun sottotitolo')
    lung = len(t) + len(st)
    if lung >= m['titolo_piu_sottotitolo_max_caratteri']:
        S[2].KO(f'titolo + sottotitolo: {lung} caratteri (limite {m["titolo_piu_sottotitolo_max_caratteri"]})')
    if st and (vietate(st, k) or vuoto_vietato(st, k)):
        S[2].KO(f'parole vietate: {vietate(st, k) or st}')
    if st.count(',') > 2:
        S[2].avviso('più di 2 virgole: sembra un elenco di parole chiave')
    if scheda is not None and (campi.get('sottotitolo') or '') != st:
        S[2].KO(f'scheda: «{campi.get("sottotitolo")}», libro.yaml: «{st}»')

    # 3 Serie
    serie = libro.get('serie')
    if serie:
        S[3].prova(f'«{serie["nome"]}» n. {serie["numero"]}')
        if vietate(serie['nome'], k):
            S[3].KO(f'parole vietate nel nome della serie: {vietate(serie["nome"], k)}')
        if scheda is not None:
            atteso = f'{serie["nome"]} | {serie["numero"]}'
            if campi.get('serie') != atteso:
                S[3].KO(f'scheda: «{campi.get("serie")}», atteso «{atteso}»')
            elif not str(campi['serie'].split('|')[-1]).strip().isdigit():
                S[3].KO('numero della serie non in cifre')
    else:
        S[3].prova('nessuna serie')

    # 4 Descrizione
    if scheda is not None:
        d = scheda['descrizione']
        S[4].prova(f'{len(d)} caratteri')
        if not d:
            S[4].KO('descrizione vuota (la scrive Claude Code nella fase di pubblicazione)')
        if len(d) > m['descrizione_max_caratteri']:
            S[4].KO(f'{len(d)} caratteri (massimo {m["descrizione_max_caratteri"]})')
        for nome, rx in m['pattern_descrizione']['bloccanti'].items():
            if re.search(rx, d):
                S[4].KO(f'{nome} nella descrizione: «{re.search(rx, d).group(0)}»')
        for f in m['formule_vietate_descrizione']:
            if re.search(r'(?i)(?<!\w)' + re.escape(f) + r'(?!\w)', d):
                S[4].KO(f'formula vietata: «{f}»')
        if vietate(d, k):
            S[4].KO(f'parole vietate: {", ".join(vietate(d, k))}')
        ammessi = m['html_ammesso_descrizione']['tag']
        fuori = sorted({x.lower() for x in tag_html(d)} - set(ammessi))
        if fuori:
            S[4].KO(f'tag HTML non ammessi: {", ".join(fuori)}')
        for nome, rx in m['pattern_descrizione']['avvisi'].items():
            if re.search(rx, d):
                S[4].avviso(f'{nome}: «{re.search(rx, d).group(0)}»')

    # 5 Autore
    a = libro['autore']
    S[5].prova(f'«{a}»')
    if scheda is not None and campi.get('autore') != a:
        S[5].KO(f'scheda: «{campi.get("autore")}», libro.yaml: «{a}»')
    if info is not None and info.get('Author') != a:
        S[5].KO(f'PDF Author: «{info.get("Author")}», libro.yaml: «{a}»')
    if md is not None:
        if not re.search(r'(?m)^### ' + re.escape(a) + r'\s*$', md):
            S[5].KO('frontespizio con un autore diverso')
        if not re.search(r'©[^\n]*' + re.escape(a), md):
            S[5].KO('pagina di copyright senza il nome dell\'autore')

    # 6 Editore
    ed = campi.get('editore', '')
    if scheda is not None:
        S[6].prova(f'«{ed}»' if ed else 'campo vuoto')
        if ed and vietate(ed, k):
            S[6].KO(f'parole vietate: {vietate(ed, k)}')
        if ed and re.search(r'(?i)\b(https?://|www\.|\.com\b|\.it\b)', ed):
            S[6].KO('sito o dominio nel campo editore')
    if conferme.get('isbn') == 'kdp_gratuito':
        S[6].avviso(f'con l\'ISBN gratuito l\'editore risulta «{k["isbn"]["editore_risultante"]}»')

    # 7 Parole chiave
    if scheda is not None:
        pk = scheda['parole chiave']
        S[7].prova(f'{len(pk)} parole chiave')
        if len(pk) > m['parole_chiave_max']:
            S[7].KO(f'{len(pk)} parole chiave (massimo {m["parole_chiave_max"]})')
        parole_titolo = {w.lower() for w in re.findall(r'\w+', t + ' ' + st) if len(w) > 3}
        a_, b_ = m['parole_chiave_parole_consigliate']
        for x in pk:
            if vietate(x, k) or tag_html(x):
                S[7].KO(f'«{x}»: parole vietate {vietate(x, k)}')
            n = len(x.split())
            if not a_ <= n <= b_:
                S[7].avviso(f'«{x}»: {n} parole (consigliate {a_}-{b_})')
            dup = parole_titolo & {w.lower() for w in re.findall(r'\w+', x)}
            if dup:
                S[7].avviso(f'«{x}» ripete parole del titolo: {", ".join(sorted(dup))}')

    # 8 Categorie
    if scheda is not None:
        cat = scheda['categorie']
        S[8].prova(f'{len(cat)} categorie')
        if len(cat) > m['categorie_max']:
            S[8].KO(f'{len(cat)} categorie (massimo {m["categorie_max"]})')
    if conferme.get('categorie_coerenti') is not True:
        S[8].KO('coerenza di categorie, parole chiave, descrizione e copertina: da confermare dall\'autore')

    # 9 Copertina
    S[9].prova('bleed, dimensioni dal calcolatore KDP, riquadro del codice a barre libero, dati identici ai metadati')
    if conferme.get('copertina_verificata') is not True:
        S[9].KO('copertina: da confermare dall\'autore')

    # 10 ISBN
    if conferme.get('isbn') == 'kdp_gratuito':
        S[10].prova('ISBN gratuito KDP, nessuna azione')
    else:
        S[10].KO('ISBN: da confermare dall\'autore (isbn: kdp_gratuito)')
    if md is not None and re.search(k['isbn']['pattern'], md):
        S[10].avviso('un ISBN compare nel manoscritto: non deve esserci finché KDP non lo assegna')
    S[10].avviso('copertina: lasciare libero il riquadro del codice a barre (modello del calcolatore KDP)')

    # 11 Cartaceo
    c = k['cartaceo']
    carta = conferme.get('carta') or libro['formato'].get('carta') or 'crema'
    if '--carta' in argv:
        carta = argv[argv.index('--carta') + 1]
    bleed = '--bleed' in argv or bool(libro['formato'].get('bleed'))
    if info is None:
        S[11].KO(f'PDF assente: {pdf}')
    else:
        pagine = int(info['Pages'])
        w, h = (float(x) for x in re.findall(r'[\d.]+', info['Page size'])[:2])
        wi, hi = round(w / 72, 2), round(h / 72, 2)
        S[11].prova(f'{pagine} pagine, {wi} × {hi}", carta {carta}')
        if pagine < c['pagine_min']:
            S[11].KO(f'{pagine} pagine (minimo {c["pagine_min"]})')
        if pagine > c['pagine_max'][carta]:
            S[11].KO(f'{pagine} pagine (massimo {c["pagine_max"][carta]} con carta {carta})')
        if pagine % 2:
            S[11].avviso(f'{pagine} pagine: numero dispari (da verificare sulla pagina ufficiale)')
        citato = any(abs(wi - a_) < 0.03 and abs(hi - b_) < 0.03 for a_, b_ in c['formati_citati_pollici'])
        if 'formato_confermato_kdp' in libro['formato']:
            # libro.yaml (formato.formato_confermato_kdp): false = AVVISO, true = OK, citato o no
            if libro['formato']['formato_confermato_kdp'] is True:
                S[11].prova(f'formato {wi} × {hi}" confermato dall\'autore su KDP (libro.yaml)')
            else:
                S[11].avviso(f'formato {wi} × {hi}" da confermare su KDP: formato_confermato_kdp è false in libro.yaml')
        elif not citato:
            if conferme.get('formato_confermato_kdp') is True:
                S[11].prova('formato non tra quelli citati, confermato dall\'autore su KDP')
            else:
                S[11].avviso(f'formato {wi} × {hi}" non tra quelli citati: formato_confermato_kdp è false')
        min_int = comune.kdp_interno_pollici(pagine)
        min_est = c['margine_esterno_min_pollici']['con_bleed' if bleed else 'senza_bleed']
        mg = verifica_pdf.margini(pdf)
        interno = min((sx if i % 2 else dx, i) for i, sx, dx, _, _ in mg)
        altri = min(min(dx if i % 2 else sx, a_, b_) for i, sx, dx, a_, b_ in mg)
        S[11].prova(f'margine interno minimo {interno[0]:.3f}" (KDP {min_int}"), esterni minimi {altri:.3f}" (KDP {min_est}")')
        if interno[0] < min_int:
            S[11].KO(f'margine interno {interno[0]:.3f}" a pag. {interno[1]} (minimo {min_int}")')
        if altri < min_est:
            S[11].KO(f'margine esterno {altri:.3f}" (minimo {min_est}")')
        fonts = verifica_pdf.pdffonts(pdf)
        if any(f['tipo'] == 'Type 3' for f in fonts):
            S[11].KO('font Type3 nel PDF')
        if any(not f['incorporato'] for f in fonts):
            S[11].KO('font non incorporati nel PDF')

    # 12 eBook
    if not libro.get('ebook'):
        S[12].prova('eBook non previsto (ebook: false)')
    else:
        docx = os.path.join(pub, 'ebook.docx')
        if not os.path.isfile(docx):
            S[12].KO('ebook: true ma manca 06-pubblicazione/ebook.docx')
        else:
            with zipfile.ZipFile(docx) as z:
                doc = z.read('word/document.xml').decode('utf-8', 'ignore')
                nomi = z.namelist()
            if not re.search(r'w:pStyle w:val="(Heading1|Titolo1|Heading2|Titolo2)"', doc):
                S[12].KO('nessun titolo con stile Titolo 1/2 (serve per il sommario attivo)')
            if re.search(r'PAGE', doc) or any(n.startswith('word/footer') or n.startswith('word/header') for n in nomi):
                S[12].KO('numeri di pagina, intestazioni o piè di pagina fissi nell\'eBook')
            S[12].prova('ebook.docx presente')
        S[12].avviso('controllo con Kindle Previewer: a cura dell\'autore')

    # 13 Dichiarazione AI
    S[13].prova('promemoria: testo, immagini, traduzioni; testo del sistema «generato dall\'AI»')
    if conferme.get('dichiarazione_ai') != 'fatta':
        S[13].KO('dichiarazione AI: da confermare dall\'autore (dichiarazione_ai: fatta)')

    # 14 Contenuti
    S[14].prova('copyright, marchi, contenuti per adulti segnalati')
    if conferme.get('contenuti_verificati') is not True:
        S[14].KO('contenuti: da confermare dall\'autore')

    # 15 Recensioni
    if md is not None:
        trovati = re.findall(k['metadati']['recensioni_vietate'], md)
        if trovati:
            S[15].KO(f'invito alla recensione non neutro: {", ".join(trovati)}')
    S[15].prova('invito alla recensione neutro nel manoscritto')
    if conferme.get('recensioni_regolari') is not True:
        S[15].KO('nessuno scambio di recensioni: da confermare dall\'autore')
    return S, pdf


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore(__doc__.strip().splitlines()[2])
    cartella, libro, _ = comune.carica_libro(args[0])
    oggi = comune.oggi(argv)
    S, pdf = controlla(cartella, libro, argv)
    scaduta, msg = kdp_verifica.stato_verifica(oggi)
    sha = hashlib.sha256(open(pdf, 'rb').read()).hexdigest() if os.path.isfile(pdf) else '—'
    k = comune.kdp()
    righe = ['# Conformità KDP', '', f'Libro: {libro["titolo"]} — data: {oggi} — PDF: {os.path.basename(pdf)} (sha256 {sha[:16]}…)', '',
             ('**AVVISO:** ' if scaduta else '') + msg, '',
             '| Sez. | Voce | Esito | Prova | Avvisi |', '|---|---|---|---|---|']
    for n, s in S.items():
        prova = '; '.join(s.prove + s.ko).replace('|', '/')
        righe.append(f'| {n} | {NOMI[n]} | {s.esito} | {prova} | {"; ".join(s.avvisi).replace("|", "/") or "—"} |')
    ko = [n for n, s in S.items() if s.esito == 'KO']
    righe += ['', f'**Esito:** {"KO nelle sezioni " + ", ".join(map(str, ko)) if ko else "nessun KO"}.', '',
              '> ' + k['dichiarazione_ai']['promemoria'].replace('\n', ' '), '']
    print('scritto', comune.scrivi(cartella, '06-pubblicazione/conformita-kdp.md', '\n'.join(righe)))
    print(msg)
    print('KO:', ', '.join(f'{n} {NOMI[n]}' for n in ko) if ko else 'nessuno')
    if ko:
        return 1
    return 2 if scaduta else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

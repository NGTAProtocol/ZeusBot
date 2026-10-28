"""Compone il manoscritto completo di un libro (proposta B.2, B.4).

Uso: python3 -B compila.py <libro>
Scrive <libro>/05-output/<titolo>-completo.md: frontespizio, pagina di copyright
(riga ©, dichiarazione di fantasia, nota dell'autore), sommario, parti e unità
nell'ordine di lettura. Toglie le righe nascoste <!-- zb: … -->, sostituisce il
separatore di scena del sorgente con quello di stampa e intitola le unità
(«N. Titolo» dall'intestazione sorgente «# N — Titolo» o «# Titolo», «Prologo», «Epilogo», titolo
dell'interludio; un capitolo senza titolo resta «Capitolo N», con un avviso). Le sezioni sono
delimitate da commenti <!-- zb:sezione … --> che impagina.py usa per le pagine.
Titoli interni: nell'unità si scarta solo il primo titolo (l'intestazione «# N — Titolo», che il motore
riscrive); gli altri titoli («## L'enigma…») restano, abbassati di un livello sotto il titolo dell'unità.
Appendici: i file di 05-appendici/ dichiarati in libro.yaml (campo «appendici», in ordine) vengono dopo
l'ultima unità, epilogo compreso, ognuna su pagina nuova e nel sommario. Testo .md; immagini .svg (convertite
in PNG con Chromium, stampa/svg_png.js), .png, .jpg: vanno in 05-output/appendici/ con titolo e didascalia.
Un file di 05-appendici/ non dichiarato dà un avviso, non blocca.
Il risultato è deterministico: stesso libro, stesso file.
"""
import datetime
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402


def titolo_capitolo(testo):
    """Titolo dall'intestazione sorgente «# N — Titolo» o «# Titolo»; None se è solo «# N» o «# Capitolo N»."""
    for r in testo.splitlines():
        if r.strip().startswith('#'):
            m = re.match(r'^#+\s*(?:\d+\s*[—–-]\s*)?(\S.*?)\s*$', r.strip())
            if not m or re.fullmatch(r'(?i)(capitolo\s+)?\d+', m.group(1)):
                return None
            return m.group(1)
    return None


def titolo_unita(nome, libro, testo=None, avvisi=None):
    """«N. Titolo» per un capitolo con il titolo nell'intestazione; senza titolo «Capitolo N» e un avviso."""
    if nome.isdigit():
        t = titolo_capitolo(testo or '')
        if t:
            return f'{nome}. {t}'
        if avvisi is not None:
            avvisi.append(f'AVVISO: capitolo {nome} senza titolo nell\'intestazione («# {nome} — Titolo»): resta «Capitolo {nome}».')
        return f'Capitolo {nome}'
    if nome.startswith('interludio '):
        num = nome.split(' ', 1)[1]
        for i in (libro.get('struttura') or {}).get('interludi') or []:
            if str(i['numero']) == num:
                return i['titolo']
        return f'Interludio {num}'
    return nome.capitalize()


def corpo_unita(testo, sep_sorgente, sep_stampa):
    """Corpo dell'unità: senza commenti e senza il primo titolo (l'intestazione, riscritta da compila);
    i titoli successivi restano, abbassati di un livello («## X» diventa «### X»)."""
    righe, in_commento, titolo_visto = [], False, False
    for r in testo.splitlines():
        s = r.strip()
        if in_commento:
            in_commento = '-->' not in s
            continue
        if s.startswith('<!--'):
            in_commento = '-->' not in s
            continue
        if re.match(r'^#{1,6}\s', s) or re.match(r'^#{1,6}$', s):
            if not titolo_visto:
                titolo_visto = True
                continue
            livello = len(s) - len(s.lstrip('#'))
            righe.append('#' * min(livello + 1, 6) + s[livello:])
            continue
        if s and s == sep_sorgente.strip():
            righe.append(f'<p class="scena">{sep_stampa}</p>')
            continue
        righe.append(r.rstrip())
    while righe and not righe[0].strip():
        righe.pop(0)
    while righe and not righe[-1].strip():
        righe.pop()
    return '\n'.join(righe)


IMMAGINI = ('.svg', '.png', '.jpg', '.jpeg')


def immagine_appendice(cartella, sorgente, avvisi):
    """Percorso relativo a 05-output dell'immagine pronta per la stampa (PNG o JPG), o None se non riesce."""
    nome = os.path.basename(sorgente)
    base, est = os.path.splitext(nome)
    dest_dir = comune.percorso_in_libro(cartella, '05-output/appendici')
    os.makedirs(dest_dir, exist_ok=True)
    if est.lower() != '.svg':
        shutil.copyfile(sorgente, os.path.join(dest_dir, nome))
        return f'appendici/{nome}'
    png = os.path.join(dest_dir, base + '.png')
    try:
        import impagina
        env = dict(os.environ, NODE_PATH=impagina.node_path())
        r = subprocess.run(['node', os.path.join(comune.radice_motore(), 'stampa', 'svg_png.js'), sorgente, png],
                           env=env, capture_output=True, text=True)
        ok = r.returncode == 0 and os.path.isfile(png)
        motivo = (r.stderr.strip().splitlines() or ['?'])[-1]
    except FileNotFoundError:
        ok, motivo = False, 'node non trovato'
    if not ok:
        if avvisi is not None:
            avvisi.append(f'AVVISO: appendice {nome}: conversione SVG → PNG non riuscita ({motivo}); '
                          f'l\'immagine manca nel manoscritto compilato.')
        return None
    return f'appendici/{base}.png'


def appendici(cartella, libro, avvisi=None):
    """[(titolo, testo markdown)] delle appendici dichiarate in libro.yaml, nell'ordine dichiarato.
    Un file dichiarato e mancante ferma il motore; un file di 05-appendici/ non dichiarato dà un avviso."""
    dichiarate = libro.get('appendici') or []
    cart = os.path.join(cartella, '05-appendici')
    presenti = sorted(f for f in os.listdir(cart) if not f.startswith('.')) if os.path.isdir(cart) else []
    nomi = [a['file'] for a in dichiarate]
    for f in presenti:
        if f not in nomi and avvisi is not None:
            avvisi.append(f'AVVISO: 05-appendici/{f} non è dichiarato in libro.yaml (appendici): non entra nel libro.')
    out = []
    for a in dichiarate:
        sorgente = os.path.join(cart, a['file'])
        if not os.path.isfile(sorgente):
            raise comune.ErroreMotore(f'Appendice dichiarata in libro.yaml ma assente: 05-appendici/{a["file"]}')
        est = os.path.splitext(a['file'])[1].lower()
        if est == '.md':
            corpo = corpo_unita(open(sorgente, encoding='utf-8').read(), '\0', '')
        elif est in IMMAGINI:
            src = immagine_appendice(cartella, sorgente, avvisi)
            didascalia = (a.get('didascalia') or '').strip()
            if src:
                corpo = (f'<figure class="immagine"><img src="{src}" alt="{a["titolo"]}">'
                         + (f'<figcaption>{didascalia}</figcaption>' if didascalia else '') + '</figure>')
            else:
                corpo = f'<p class="immagine-mancante">[immagine non convertita: {a["file"]}]</p>'
        else:
            raise comune.ErroreMotore(f'Appendice 05-appendici/{a["file"]}: formato non previsto '
                                      f'(ammessi .md, {", ".join(IMMAGINI)})')
        out.append((a['titolo'], corpo))
    return out


def compila(cartella, libro, avvisi=None):
    st = libro.get('struttura') or {}
    sep = st['separatore_scena']
    cop = libro['copyright']
    anno = cop.get('anno') or datetime.date.today().year
    unita = comune.unita(cartella, libro)
    testi = {nome: open(p, encoding='utf-8').read() for nome, p in unita}
    titoli = {nome: titolo_unita(nome, libro, testi[nome], avvisi) for nome, _ in unita}
    parti = {p['capitoli'][0]: p['titolo'] for p in st.get('parti') or []}
    pezzi = ['<!-- zb:sezione frontespizio -->', '', f'# {libro["titolo"]}', '']
    if libro.get('sottotitolo'):
        pezzi += [f'## {libro["sottotitolo"]}', '']
    pezzi += [f'### {libro["autore"]}', '', '<!-- zb:sezione copyright -->', '',
              cop['riga'].replace('{anno}', str(anno)).replace('{autore}', libro['autore']), '',
              cop['fantasia'].strip(), '']
    if cop.get('nota_autore'):
        pezzi += [cop['nota_autore'].strip(), '']
    app = appendici(cartella, libro, avvisi)
    pezzi += ['<!-- zb:sezione sommario -->', '', '## Sommario', '']
    for nome, _ in unita:
        if nome.isdigit() and int(nome) in parti:
            pezzi.append(f'- **{parti[int(nome)]}**')
        pezzi.append(f'- {titoli[nome]}')
    for titolo, _ in app:
        pezzi.append(f'- {titolo}')
    pezzi.append('')
    for nome, p in unita:
        if nome.isdigit() and int(nome) in parti:
            pezzi += ['<!-- zb:sezione parte -->', '', f'# {parti[int(nome)]}', '']
        tipo = 'capitolo' if nome.isdigit() else nome.split()[0]
        pezzi += [f'<!-- zb:sezione {tipo} -->', '', f'## {titoli[nome]}', '',
                  corpo_unita(testi[nome], sep['sorgente'], sep['stampa']), '']
    for titolo, corpo in app:
        pezzi += ['<!-- zb:sezione appendice -->', '', f'## {titolo}', '', corpo, '']
    return '\n'.join(pezzi).rstrip() + '\n'


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: compila.py <libro>')
    cartella, libro, _ = comune.carica_libro(args[0])
    avvisi = []
    testo = compila(cartella, libro, avvisi)
    for a in avvisi:
        print(a)
    rel = f'05-output/{comune.nome_file(libro["titolo"])}-completo.md'
    print('scritto', comune.scrivi(cartella, rel, testo))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

"""Compone il manoscritto completo di un libro (proposta B.2, B.4).

Uso: python3 -B compila.py <libro>
Scrive <libro>/05-output/<titolo>-completo.md: frontespizio, pagina di copyright
(riga ©, dichiarazione di fantasia, nota dell'autore), sommario, parti e unità
nell'ordine di lettura. Toglie le righe nascoste <!-- zb: … -->, sostituisce il
separatore di scena del sorgente con quello di stampa e intitola le unità
(«N. Titolo» dall'intestazione sorgente «# N — Titolo», «Prologo», «Epilogo», titolo
dell'interludio; un capitolo senza titolo resta «Capitolo N», con un avviso). Le sezioni sono
delimitate da commenti <!-- zb:sezione … --> che impagina.py usa per le pagine.
Il risultato è deterministico: stesso libro, stesso file.
"""
import datetime
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402


def titolo_capitolo(testo):
    """Titolo dall'intestazione sorgente «# N — Titolo» (anche «## N - Titolo»); None se manca."""
    for r in testo.splitlines():
        if r.strip().startswith('#'):
            m = re.match(r'^#+\s*\d+\s*[—–-]\s*(\S.*?)\s*$', r.strip())
            return m.group(1) if m else None
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
    righe, in_commento = [], False
    for r in testo.splitlines():
        s = r.strip()
        if in_commento:
            in_commento = '-->' not in s
            continue
        if s.startswith('<!--'):
            in_commento = '-->' not in s
            continue
        if s.startswith('#'):
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
    pezzi += ['<!-- zb:sezione sommario -->', '', '## Sommario', '']
    for nome, _ in unita:
        if nome.isdigit() and int(nome) in parti:
            pezzi.append(f'- **{parti[int(nome)]}**')
        pezzi.append(f'- {titoli[nome]}')
    pezzi.append('')
    for nome, p in unita:
        if nome.isdigit() and int(nome) in parti:
            pezzi += ['<!-- zb:sezione parte -->', '', f'# {parti[int(nome)]}', '']
        tipo = 'capitolo' if nome.isdigit() else nome.split()[0]
        pezzi += [f'<!-- zb:sezione {tipo} -->', '', f'## {titoli[nome]}', '',
                  corpo_unita(testi[nome], sep['sorgente'], sep['stampa']), '']
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

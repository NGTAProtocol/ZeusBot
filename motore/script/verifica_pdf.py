"""Verifica del PDF di stampa (proposta A.4 sezione 11, A.7, B.2).

Uso: python3 -B verifica_pdf.py <libro> [--pdf <percorso>] [--schermo]
Controlla il PDF (predefinito: <libro>/05-output/<titolo>.pdf):
- pagine (pdfinfo) e numero pari (AVVISO se dispari);
- metadati Title e Author uguali a titolo e autore di libro.yaml (KO);
- font (pdffonts): tutti incorporati e nessun Type3 (KO);
- margini (pdftotext -bbox): margine interno minimo (a sinistra sulle pagine dispari,
  a destra sulle pari) contro la tabella KDP per il numero di pagine; margini esterni,
  alto e basso contro il minimo KDP senza bleed (o con bleed) (KO);
- sommario: ogni voce ha il numero di pagina su cui comincia davvero l'unità (KO);
- parole per pagina: parole del manoscritto compilato (metodo unico) diviso pagine numerate.
Report: <libro>/06-diagnostica/verifica-pdf.md. Codice 1 se c'è almeno un KO.
"""
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import conta  # noqa: E402
from stile import risultato, tabella  # noqa: E402

PT = 72.0


def pdfinfo(pdf):
    r = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True, check=True)
    info = {}
    for riga in r.stdout.splitlines():
        if ':' in riga:
            k, v = riga.split(':', 1)
            info[k.strip()] = v.strip()
    return info


def pdffonts(pdf):
    r = subprocess.run(['pdffonts', pdf], capture_output=True, text=True, check=True)
    righe = r.stdout.splitlines()
    if len(righe) < 2:
        return []
    # colonne a larghezza fissa: la riga di trattini dà le posizioni
    pos, i = [], 0
    for blocco in righe[1].split(' '):
        pos.append((i, i + len(blocco)))
        i += len(blocco) + 1
    out = []
    for riga in righe[2:]:
        campi = [riga[a:b].strip() for a, b in pos]
        if len(campi) < 4 or not campi[0]:
            continue
        out.append({'nome': campi[0], 'tipo': campi[1], 'incorporato': campi[3] == 'yes'})
    return out


def margini(pdf):
    """[(pagina 1-based, sx, dx, alto, basso)] in pollici, solo pagine con testo."""
    with tempfile.TemporaryDirectory(prefix='zb-bbox-') as tmp:
        out_html = os.path.join(tmp, 'bbox.html')
        subprocess.run(['pdftotext', '-bbox', pdf, out_html], check=True, stderr=subprocess.DEVNULL)
        html = open(out_html, encoding='utf-8').read()
    out = []
    for i, (w, h, corpo) in enumerate(re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', html, re.S), 1):
        box = [tuple(map(float, m)) for m in
               re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)"', corpo)]
        if not box:
            continue
        w, h = float(w), float(h)
        out.append((i, min(b[0] for b in box) / PT, (w - max(b[2] for b in box)) / PT,
                    min(b[1] for b in box) / PT, (h - max(b[3] for b in box)) / PT))
    return out


def numero_al_piede(pagina):
    """Numero stampato al piede della pagina (l'ultima parola numerica più in basso)."""
    parole = [w for w in pagina.get_text('words') if w[4].isdigit()]
    if not parole:
        return None
    return int(max(parole, key=lambda w: w[3])[4])


def sommario(pdf, titoli):
    """{titolo: (numero nel sommario, numero al piede della pagina d'inizio)}."""
    import pymupdf as fitz
    out = {}
    with fitz.open(pdf) as d:
        pag_somm = next((p for p in d if 'Sommario' in [r.strip() for r in p.get_text('text').splitlines()]), None)
        if pag_somm is None:
            return out
        parole = pag_somm.get_text('words')
        for t in titoli:
            primo = t.split()[0]
            cand = [w for w in parole if w[4] == primo]
            nel_somm = None
            for c in cand:
                riga = sorted([w for w in parole if abs(w[3] - c[3]) < 2], key=lambda w: w[0])
                testo = ' '.join(w[4] for w in riga)
                if testo.startswith(t) and riga[-1][4].isdigit():
                    nel_somm = int(riga[-1][4])
                    break
            reale = None
            for i, p in enumerate(d):
                if p.number == pag_somm.number:
                    continue
                if t in [r.strip() for r in p.get_text('text').splitlines()]:
                    reale = numero_al_piede(p)
                    break
            out[t] = (nel_somm, reale)
    return out


def verifica(cartella, libro, pdf):
    import pymupdf as fitz
    ris, misure = [], {}
    info = pdfinfo(pdf)
    pagine = int(info['Pages'])
    misure['pagine'] = pagine
    if pagine % 2:
        ris.append(risultato('PDF', 'pagine_pari', 'AVVISO', None, f'{pagine} pagine (numero dispari)'))
    for campo, atteso in (('Title', libro['titolo']), ('Author', libro['autore'])):
        misure[campo] = info.get(campo)
        if info.get(campo) != atteso:
            ris.append(risultato('PDF', f'metadato_{campo}', 'KO', None, f'«{info.get(campo)}», atteso «{atteso}»'))
    fonts = pdffonts(pdf)
    misure['font'] = sorted({f['nome'].split('+')[-1] for f in fonts})
    misure['font_type3'] = sum(1 for f in fonts if f['tipo'] == 'Type 3')
    misure['font_non_incorporati'] = sum(1 for f in fonts if not f['incorporato'])
    if misure['font_type3']:
        ris.append(risultato('PDF', 'font_type3', 'KO', None, f'{misure["font_type3"]} font Type3'))
    if misure['font_non_incorporati']:
        ris.append(risultato('PDF', 'font_incorporati', 'KO', None, f'{misure["font_non_incorporati"]} font non incorporati'))
    _, esterni = comune.kdp_margini()
    bleed = bool(libro['formato'].get('bleed'))
    min_est = esterni['con_bleed' if bleed else 'senza_bleed']
    min_int = comune.kdp_interno_pollici(pagine)
    mg = margini(pdf)
    interni = [(sx if i % 2 else dx, i) for i, sx, dx, _, _ in mg]
    esterni_mis = [(dx if i % 2 else sx, i) for i, sx, dx, _, _ in mg]
    alti = [(a, i) for i, _, _, a, _ in mg]
    bassi = [(b, i) for i, _, _, _, b in mg]
    for nome, valori, soglia in (('interno', interni, min_int), ('esterno', esterni_mis, min_est),
                                 ('alto', alti, min_est), ('basso', bassi, min_est)):
        v, pag = min(valori)
        misure[f'margine_{nome}'] = round(v, 3)
        misure[f'margine_{nome}_pagina'] = pag
        misure[f'margine_{nome}_soglia'] = soglia
        if v < soglia:
            ris.append(risultato('PDF', f'margine_{nome}', 'KO', None,
                                 f'{v:.3f}" a pag. {pag}, minimo KDP {soglia}" ({pagine} pagine)'))
    md = os.path.join(cartella, '05-output', f'{comune.nome_file(libro["titolo"])}-completo.md')
    testo_md = open(md, encoding='utf-8').read() if os.path.isfile(md) else ''
    somm = re.search(r'## Sommario\n\n(.*?)\n\n', testo_md, re.S)
    titoli = [re.sub(r'^-\s+', '', r).strip().strip('*') for r in somm.group(1).splitlines()] if somm else []
    confronto = sommario(pdf, titoli)
    misure['sommario'] = {t: v[0] for t, v in confronto.items()}
    for t, (nel, reale) in confronto.items():
        if nel is None or reale is None or nel != reale:
            ris.append(risultato('PDF', 'sommario', 'KO', None, f'«{t}»: sommario {nel}, pagina reale {reale}'))
    with fitz.open(pdf) as d:
        numerate = sum(1 for p in d if numero_al_piede(p) is not None and p.get_text('text').strip())
    corpo = testo_md.split('<!-- zb:sezione sommario -->')[-1]
    corpo = re.sub(r'^## Sommario\n\n.*?\n\n', '', corpo, flags=re.S)
    parole = conta.conta_testo(corpo)
    misure['pagine_numerate'] = numerate
    misure['parole_per_pagina'] = round(parole / numerate, 1) if numerate else None
    return misure, ris


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: verifica_pdf.py <libro> [--pdf <percorso>] [--schermo]')
    cartella, libro, _ = comune.carica_libro(args[0])
    pdf = os.path.join(cartella, '05-output', f'{comune.nome_file(libro["titolo"])}.pdf')
    if '--pdf' in argv:
        pdf = os.path.realpath(argv[argv.index('--pdf') + 1])
    if not os.path.isfile(pdf):
        raise comune.ErroreMotore(f'PDF inesistente: {pdf}. Esegui prima impagina.py')
    misure, ris = verifica(cartella, libro, pdf)
    righe = ['# Verifica del PDF', '', f'Libro: {libro["titolo"]} — file: {os.path.basename(pdf)}.', '',
             '| Misura | Valore |', '|---|---|']
    righe += [f'| {k} | {v} |' for k, v in misure.items()]
    righe += ['', '## Esiti', ''] + (tabella(ris) if ris else ['Nessun KO e nessun avviso.']) + ['']
    testo = '\n'.join(righe)
    if '--schermo' in argv:
        print(testo)
    else:
        print('scritto', comune.scrivi(cartella, '06-diagnostica/verifica-pdf.md', testo))
    return 1 if any(r['esito'] == 'KO' for r in ris) else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

# Esportazione completa del progetto — parte 5 di 6

Testo integrale, parola per parola. Nessun riassunto, nessuna correzione. Esclusi `libri/` e i manoscritti.


---

## 7. Programmi, stampa e prove

### `motore/script/prove.py`

```python
"""Prove ripetibili del motore (comando «zb prove»).

Uso: python3 -B prove.py [--radice <cartella motore>]
Copia i due mini-libri inventati di prove/ in cartelle temporanee, esegue le prove
di ogni passo presente in prove/attesi.yaml (passo_1, passo_2, …), confronta gli
esiti e stampa la tabella script | controllo | atteso | ottenuto | OK/KO.
Alla fine rilancia separazione.py e recinto.py su motore/.
Codice d'uscita 0 solo se tutto è OK.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

M = comune.radice_motore()
S = os.path.join(M, 'script')
os.environ['ZB_PROVE'] = '1'   # nuovo.py: libri di prova fuori da libri/<slug>/ (mai in motore/ né sul ramo motore)
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
TMP = tempfile.mkdtemp(prefix='zb-prove-')
righe = []


def esito(script, controllo, atteso, ottenuto, sezione):
    ok = str(atteso) == str(ottenuto)
    righe.append((sezione, script, controllo, str(atteso), str(ottenuto), 'OK' if ok else 'KO'))


def saltata(script, controllo, motivo, sezione):
    righe.append((sezione, script, controllo, '—', motivo, 'SALTATA'))


def esegui(*args):
    return subprocess.run([sys.executable, '-B', *args], env=ENV, capture_output=True, text=True)


def copia_libro(nome):
    d = tempfile.mkdtemp(dir=TMP)
    return shutil.copytree(os.path.join(M, 'prove', nome), os.path.join(d, nome))


def copia_motore():
    d = tempfile.mkdtemp(dir=TMP)
    return shutil.copytree(M, os.path.join(d, 'motore'))


# ---------------------------------------------------------------- passo 1

def passo_1(A):
    import conta
    import valida_profili
    sez = 'passo 1'
    for nome, att in A['profili'].items():
        e = valida_profili.valida_profilo(os.path.join(M, 'profili', f'{nome}.yaml'))
        esito('valida_profili.py', f'profilo {nome}', att, 'OK' if not e else 'KO', sez)
    t = open(os.path.join(M, 'profili', 'giallo.yaml'), encoding='utf-8').read()
    d = tempfile.mkdtemp(dir=TMP)
    p = os.path.join(d, 'giallo.yaml')
    open(p, 'w', encoding='utf-8').write(re.sub(r'(parole_per_pagina: 250)\s+#.*', r'\1', t))
    esito('valida_profili.py', 'profilo con valore senza fonte', A['profilo_senza_fonte'],
          'OK' if not valida_profili.valida_profilo(p) else 'KO', sez)
    open(p, 'w', encoding='utf-8').write(t.replace('massimo: 3500', 'massimo: 2000'))
    esito('valida_profili.py', 'profilo con media oltre il massimo', A['profilo_media_fuori'],
          'OK' if not valida_profili.valida_profilo(p) else 'KO', sez)
    esito('valida_profili.py', "esecuzione su profili/ (codice d'uscita)", 0,
          esegui(os.path.join(S, 'valida_profili.py')).returncode, sez)

    for nome, att in A['libro_schema'].items():
        try:
            comune.carica_libro(os.path.join(M, 'prove', nome))
            o = 'OK'
        except comune.ErroreMotore:
            o = 'KO'
        esito('comune.py', f'libro.yaml {nome} contro lo schema', att, o, sez)

    casi = {
        'lingua_en': lambda y: y.replace('lingua: it', 'lingua: en'),
        'lingua_mancante': lambda y: y.replace('lingua: it\n', ''),
        'override_senza_motivo': lambda y: y.replace(
            'override: []', 'override:\n  - {campo: capitoli.minimo, valore: 700, motivo: ""}'),
        'profilo_cambiato_senza_override': lambda y: y.replace(
            'override: []', 'override: []\nstile:\n  frase_media: [8, 12]'),
        'riscrittura_senza_testo_precedente': lambda y: y.replace('modalita: nuovo', 'modalita: riscrittura'),
    }
    for k, f in casi.items():
        c = copia_libro('mini-libro')
        y = open(os.path.join(c, 'libro.yaml'), encoding='utf-8').read()
        open(os.path.join(c, 'libro.yaml'), 'w', encoding='utf-8').write(f(y))
        try:
            comune.carica_libro(c)
            msg = 'accettato'
        except comune.ErroreMotore as e:
            msg = str(e)
        att = A['rifiuti'][k]
        esito('comune.py', f'rifiuto: {k}', att, att if att in msg else msg.splitlines()[0][:80], sez)

    stato = {'libro': 'Prova di stampa', 'motore_commit': 'abc1234', 'ramo_ultimo_salvataggio': 'prova',
             'fase': 0, 'passo': 'briefing', 'gate_in_attesa': 'G0',
             'lotto': {'dimensione': 3, 'capitoli': []}, 'ultimo_capitolo_approvato': None,
             'parole': {'scritte': 0, 'obiettivo': 3000, 'metodo': 'unico'},
             'documenti_approvati': {}, 'avvisi_aperti': [], 'revisione_in_corso': None,
             'push_in_sospeso': False, 'aggiornato': '2026-10-02T00:00:00Z'}
    sc = comune.carica_schema('stato')
    esito('stato.schema.yaml', "stato.yaml d'esempio (C.1)", A['stato_schema']['modello_valido'],
          'OK' if not comune.valida(stato, sc, 'stato') else 'KO', sez)
    s2 = dict(stato)
    del s2['fase']
    esito('stato.schema.yaml', 'stato.yaml senza fase', A['stato_schema']['fase_mancante'],
          'OK' if not comune.valida(s2, sc, 'stato') else 'KO', sez)

    for nome, att in A['conta'].items():
        c = copia_libro(nome)
        cart, libro, _ = comune.carica_libro(c)
        un = comune.unita(cart, libro)
        esito('conta.py', f'{nome}: ordine delle unità', att['ordine'], [n for n, _ in un], sez)
        for n, p in un:
            esito('conta.py', f'{nome}: parole unità {n}', att['unita'][n],
                  conta.conta_testo(open(p, encoding='utf-8').read()), sez)
        esegui(os.path.join(S, 'conta.py'), c, '--scrivi')
        rep = os.path.join(c, '06-diagnostica', 'conteggio.md')
        m = re.search(r'\*\*Totale:\*\* (\d+)', open(rep, encoding='utf-8').read()) if os.path.isfile(rep) else None
        esito('conta.py', f'{nome}: totale nel report', att['totale'], m.group(1) if m else 'nessun report', sez)

    c = copia_libro('mini-libro')
    for etichetta, dest in (('scrivi fuori dal libro', os.path.join(os.path.dirname(c), 'fuori.txt')),
                            ('scrivi con ../ fuori dal libro', '../fuori2.txt')):
        try:
            comune.scrivi(c, dest, 'x')
            o = 'accettata'
        except comune.ErroreMotore:
            o = 'rifiutata'
        esito('comune.py', etichetta, A['recinto']['scrivi_fuori_dal_libro'], o, sez)

    def sep(modifica):
        c = copia_motore()
        modifica(c)
        return esegui(os.path.join(c, 'script', 'separazione.py'), '--radice', c).returncode

    def nome_vietato(c):
        open(os.path.join(c, 'dati', 'nomi_vietati.txt'), 'a', encoding='utf-8').write('Zarvenco\n')
        open(os.path.join(c, 'prove', 'mini-libro', '02-bibbia', 'bibbia.md'), 'a', encoding='utf-8').write('\nZarvenco\n')

    def yaml_fuori(c):
        shutil.copy(os.path.join(c, 'prove', 'mini-libro', 'libro.yaml'), os.path.join(c, 'dati', 'libro.yaml'))

    esito('separazione.py', 'nome vietato presente in una copia di motore/',
          A['separazione']['nome_vietato_in_copia'], sep(nome_vietato), sez)
    esito('separazione.py', 'libro.yaml fuori dai mini-libri',
          A['separazione']['libro_yaml_fuori_posto'], sep(yaml_fuori), sez)

    c = copia_motore()
    viol = os.path.join(c, 'prove', 'esiti', '_violazione_di_prova.tmp')
    cmd = f"{sys.executable} -c \"open('{viol}','w').write('x')\""
    p = esegui(os.path.join(c, 'script', 'recinto.py'), '--radice', c, '--extra', cmd)
    esito('recinto.py', 'scrittura messa apposta in motore/', A['recinto']['scrittura_messa_apposta'],
          p.returncode, sez)


# ---------------------------------------------------------------- passo 2

def passo_2(A):
    import capitolo
    import riciclo
    sez = 'passo 2'
    for nome, unita in A['capitoli'].items():
        c = copia_libro(nome)
        cart, libro, prof = comune.carica_libro(c)
        for u, att in unita.items():
            met, ris = capitolo.controlla(cart, libro, prof, u)
            esito('capitolo.py', f'{nome} {u}: parole', att['parole'], met['parole'], sez)
            esito('capitolo.py', f'{nome} {u}: frase media', att['frase_media'], met['frase_media'], sez)
            esito('capitolo.py', f'{nome} {u}: dialogo %', att['dialogo'], met['dialogo_percento'], sez)
            ottenuti = sorted(f'{r["controllo"]}|{r["esito"]}|{r["riga"] or ""}' for r in ris)
            esito('capitolo.py', f'{nome} {u}: esiti ({len(att["esiti"])} attesi)', sorted(att['esiti']), ottenuti, sez)

    c = copia_libro('mini-libro')
    p = esegui(os.path.join(S, 'capitolo.py'), c, '3')
    rep = os.path.join(c, '06-diagnostica', 'capitoli', '03.md')
    trovato = os.path.isfile(rep) and '| 3 | parole_minimo | KO |' in open(rep, encoding='utf-8').read()
    esito('capitolo.py', "giallo cap. 3 sotto il minimo: codice d'uscita", A['capitolo_sotto_minimo']['codice'], p.returncode, sez)
    esito('capitolo.py', 'giallo cap. 3 sotto il minimo: KO nel report', A['capitolo_sotto_minimo']['controllo'],
          A['capitolo_sotto_minimo']['controllo'] if trovato else 'assente', sez)

    ko = lambda lst: sum(1 for e in lst if '|KO|' in e)
    esito('capitolo.py', 'capitolo-prova nel giallo: KO', A['capitolo_prova']['giallo_ko'],
          ko(A['capitoli']['mini-libro']['1']['esiti']), sez)
    esito('capitolo.py', 'capitolo-prova nel romance: KO', A['capitolo_prova']['romance_ko'],
          ko(A['capitoli']['mini-libro-romance']['3']['esiti']), sez)

    c = copia_libro('mini-libro')
    cap1 = open(os.path.join(c, '04-manoscritto', '01-la-farmacia.md'), encoding='utf-8').read()
    primo = [b for b in cap1.split('\n\n') if b.strip() and not b.lstrip().startswith(('#', '*', '<!--'))][0]
    open(os.path.join(c, '00-progetto', 'testo-precedente.md'), 'w', encoding='utf-8').write(primo + '\n')
    y = open(os.path.join(c, 'libro.yaml'), encoding='utf-8').read()
    y = y.replace('modalita: nuovo', 'modalita: riscrittura\ntesto_precedente: 00-progetto/testo-precedente.md')
    open(os.path.join(c, 'libro.yaml'), 'w', encoding='utf-8').write(y)
    cart, libro, _ = comune.carica_libro(c)
    r = riciclo.controlla_libro(cart, libro)
    esito('riciclo.py', 'testo precedente: segmenti KO nel cap. 1', A['riciclo']['testo_precedente'],
          sum(1 for x in r if x['controllo'] == 'riciclo:testo_precedente' and x['unita'] == '1'), sez)
    c = copia_libro('mini-libro')
    frase = 'Gemma Rosselli aspettava sul marciapiede con le chiavi in mano e il bavero alzato.'
    with open(os.path.join(c, '04-manoscritto', '03-la-stazione.md'), 'a', encoding='utf-8') as f:
        f.write('\n' + frase + '\n')
    cart, libro, _ = comune.carica_libro(c)
    r = riciclo.controlla_libro(cart, libro)
    esito('riciclo.py', 'unità precedenti: segmenti AVVISO nel cap. 3', A['riciclo']['unita_precedenti'],
          sum(1 for x in r if x['controllo'] == 'riciclo:unita_precedenti' and x['unita'] == '3'), sez)

    ln = comune.leggi_yaml(os.path.join(M, 'dati', 'lista-nera.yaml'))
    esito('lista-nera.yaml', 'numero di voci', A['lista_nera']['voci'], len(ln['voci']), sez)
    try:
        for v in ln['voci']:
            re.compile(v['pattern'])
        o = 'OK'
    except re.error as e:
        o = f'KO: {e}'
    esito('lista-nera.yaml', 'regex valide', A['lista_nera']['regex_valide'], o, sez)

    import stile
    c = copia_libro('mini-libro')
    y = open(os.path.join(c, 'libro.yaml'), encoding='utf-8').read()
    y = y.replace("voci:\n", "voci:\n  - {id: registro_prova, pattern: '(?i)\\bregistro\\b', modalita: conta, massimo: 10, solo_dialogo: true}\n", 1)
    open(os.path.join(c, 'libro.yaml'), 'w', encoding='utf-8').write(y)
    cart, libro, prof = comune.carica_libro(c)
    ris = stile.controlla_libro(cart, libro, prof)['1'][1]
    ko = sorted(r['riga'] for r in ris if r['controllo'] == 'voce:registro_prova:fuori_dialogo')
    altri = [r['riga'] for r in ris if r['controllo'].startswith('voce:registro_prova') and r['riga'] in A['solo_dialogo']['righe_dialogo_ammesse']]
    esito('stile.py', 'solo_dialogo: righe KO fuori dal dialogo (cap. 1)', A['solo_dialogo']['righe_ko_cap_1'], ko, sez)
    esito('stile.py', 'solo_dialogo: righe di dialogo segnalate', [], altri, sez)

    c = copia_libro('mini-libro')
    y = open(os.path.join(c, 'libro.yaml'), encoding='utf-8').read()
    open(os.path.join(c, 'libro.yaml'), 'w', encoding='utf-8').write(y.replace('obbligatorio_in: []}', 'obbligatorio_in: ["3"]}'))
    cart, libro, prof = comune.carica_libro(c)
    ris = stile.controlla_libro(cart, libro, prof)['3'][1]
    trovati = [f'{r["controllo"]}|{r["esito"]}|{r["riga"] or ""}' for r in ris if r['controllo'].startswith('nome_obbligatorio')]
    esito('stile.py', 'nome obbligatorio assente nel cap. 3', [A['nome_obbligatorio']['esito_cap_3']], trovati, sez)

    c = copia_libro('mini-libro')
    esegui(os.path.join(S, 'capitolo.py'), c, '1')
    rep = open(os.path.join(c, '06-diagnostica', 'capitoli', '01.md'), encoding='utf-8').read()
    n_tic = len(re.findall(r'^\| Tic: .* \| \[ \] \|$', rep, re.M)) if '## Checklist manuale' in rep else 0
    esito('capitolo.py', 'checklist manuale nel report: tic con casella', A['checklist_capitolo']['tic'], n_tic, sez)

    report = {'stile.py': 'stile.md', 'continuita.py': 'continuita.md', 'riciclo.py': 'riciclo.md'}
    for chiave, att in A['comandi'].items():
        script, libro_nome = chiave.split()
        c = copia_libro(libro_nome)
        p = esegui(os.path.join(S, script), c)
        esito(script, f"{libro_nome}: codice d'uscita", att, p.returncode, sez)
        esito(script, f'{libro_nome}: report scritto', 'sì',
              'sì' if os.path.isfile(os.path.join(c, '06-diagnostica', report[script])) else 'no', sez)


# ---------------------------------------------------------------- passo 3

# Tolleranza sul confronto dei margini con l'atteso (pollici, in più o in meno). Il render di Chromium
# sposta di qualche millesimo il bordo del testo da un container all'altro, a parità di versioni
# (Playwright 1.56.1, PyMuPDF 1.28.2, font di stampa/font): differenze osservate sul romance
# 0,665/0,667 (interno) e 0,624/0,625 (esterno). La tolleranza vale solo contro l'atteso: sotto il
# minimo KDP il controllo fallisce comunque. Non allargarla senza l'autore.
TOLLERANZA_MARGINI = 0.005


def minimi_kdp(libro, pagine):
    """{margine: minimo KDP in pollici}, da dati/kdp.yaml (fonte: KDP Help Center, vedi l'intestazione
    del file). Interno: fascia per numero di pagine; esterno, alto e basso: minimo esterno, con o senza bleed."""
    _, esterni = comune.kdp_margini()
    est = esterni['con_bleed' if libro['formato'].get('bleed') else 'senza_bleed']
    return {'interno': comune.kdp_interno_pollici(pagine), 'esterno': est, 'alto': est, 'basso': est}


def controllo_margine(atteso, misurato, minimo):
    """(atteso, ottenuto) per esito(): uguali se il margine è entro la tolleranza e non sotto il minimo KDP."""
    regola = f'{atteso} ±{TOLLERANZA_MARGINI}, minimo KDP {minimo}'
    difetti = []
    if abs(misurato - atteso) > TOLLERANZA_MARGINI + 1e-9:
        difetti.append(f'{misurato}: fuori tolleranza')
    if misurato < minimo:
        difetti.append(f'{misurato}: sotto il minimo KDP {minimo}')
    return regola, regola if not difetti else '; '.join(difetti)


def struttura_pdf(pdf, libro):
    """Struttura del PDF confrontabile tra container (al posto dello sha256 del file)."""
    import pymupdf
    import verifica_pdf
    k = comune.kdp()['cartaceo']
    larg, alt = libro['formato']['pagina_pollici']
    if libro['formato'].get('bleed'):
        larg, alt = larg + k['bleed_pollici'], alt + 2 * k['bleed_pollici']
    fonts = verifica_pdf.pdffonts(pdf)
    with pymupdf.open(pdf) as d:
        formati = sorted({(round(p.rect.width / 72, 3), round(p.rect.height / 72, 3)) for p in d})
        testo = ' '.join(' '.join(p.get_text('text').split()) for p in d)
        meta = {'Title': d.metadata.get('title'), 'Author': d.metadata.get('author')}
        pagine = d.page_count
    return {'pagine': pagine,
            'formato_pollici': formati if formati != [(round(larg, 3), round(alt, 3))] else 'uguale al trim KDP',
            'font_non_incorporati': sum(1 for f in fonts if not f['incorporato']),
            'font_type3': sum(1 for f in fonts if f['tipo'] == 'Type 3'),
            'metadati_come_libro_yaml': meta == {'Title': libro['titolo'], 'Author': libro['autore']},
            'testo_parole': len(testo.split()),
            'testo_sha256': hashlib.sha256(testo.encode('utf-8')).hexdigest()}


def passo_3(A):
    import hashlib
    import verifica_pdf
    sez = 'passo 3'
    sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
    for nome in ('mini-libro', 'mini-libro-romance'):
        att = A[nome]
        c = copia_libro(nome)
        r = esegui(os.path.join(S, 'compila.py'), c)
        esito('compila.py', f"{nome}: codice d'uscita", 0, r.returncode, sez)
        cart, libro, _ = comune.carica_libro(c)
        base = comune.nome_file(libro['titolo'])
        md = os.path.join(cart, '05-output', f'{base}-completo.md')
        esito('compila.py', f'{nome}: sha256 del .md compilato', att['md_sha256'],
              sha(md) if os.path.isfile(md) else 'assente', sez)
        r = esegui(os.path.join(S, 'impagina.py'), c)
        esito('impagina.py', f"{nome}: codice d'uscita", 0, r.returncode, sez)
        pdf = os.path.join(cart, '05-output', f'{base}.pdf')
        primo = sha(pdf) if os.path.isfile(pdf) else 'assente'
        esegui(os.path.join(S, 'impagina.py'), c)
        secondo = sha(pdf) if os.path.isfile(pdf) else 'assente'
        esito('impagina.py', f'{nome}: due generazioni, stesso sha256', 'sì', 'sì' if primo == secondo else 'no', sez)
        esito('impagina.py', f'{nome}: struttura del PDF (pagine, formato, font, metadati, testo)',
              {'pagine': att['struttura']['pagine'], 'formato_pollici': 'uguale al trim KDP', 'font_non_incorporati': 0,
               'font_type3': 0, 'metadati_come_libro_yaml': True, 'testo_parole': att['struttura']['testo_parole'],
               'testo_sha256': att['struttura']['testo_sha256']},
              struttura_pdf(pdf, libro) if os.path.isfile(pdf) else 'assente', sez)
        misure, ris = verifica_pdf.verifica(cart, libro, pdf)
        esito('verifica_pdf.py', f'{nome}: pagine', att['pagine'], misure['pagine'], sez)
        esito('verifica_pdf.py', f'{nome}: metadati Title e Author', att['metadati'],
              {'Title': misure['Title'], 'Author': misure['Author']}, sez)
        esito('verifica_pdf.py', f'{nome}: font Type3', 0, misure['font_type3'], sez)
        esito('verifica_pdf.py', f'{nome}: font non incorporati', 0, misure['font_non_incorporati'], sez)
        minimi = minimi_kdp(libro, misure['pagine'])
        for k, v in att['margini'].items():
            esito('verifica_pdf.py', f'{nome}: margine {k}', *controllo_margine(v, misure[f'margine_{k}'], minimi[k]), sez)
        for k, v in att['soglie_kdp'].items():
            esito('verifica_pdf.py', f'{nome}: soglia KDP margine {k}', v, misure[f'margine_{k}_soglia'], sez)
        esito('verifica_pdf.py', f'{nome}: sommario contro pagine reali', att['sommario'], misure['sommario'], sez)
        esito('verifica_pdf.py', f'{nome}: parole per pagina', att['parole_per_pagina'], misure['parole_per_pagina'], sez)
        esito('verifica_pdf.py', f'{nome}: esiti', sorted(att['esiti']),
              sorted(f'{x["controllo"]}|{x["esito"]}' for x in ris), sez)
        r = esegui(os.path.join(S, 'verifica_pdf.py'), c)
        esito('verifica_pdf.py', f"{nome}: codice d'uscita", att['codice'], r.returncode, sez)
        esito('verifica_pdf.py', f'{nome}: report scritto', 'sì',
              'sì' if os.path.isfile(os.path.join(cart, '06-diagnostica', 'verifica-pdf.md')) else 'no', sez)
    bleed_pdf(A['bleed'], sez)


def pdf_di(c):
    """compila e impagina una copia di mini-libro; (cartella, libro, pdf)."""
    esegui(os.path.join(S, 'compila.py'), c)
    esegui(os.path.join(S, 'impagina.py'), c)
    cart, libro, _ = comune.carica_libro(c)
    return cart, libro, os.path.join(cart, '05-output', f'{comune.nome_file(libro["titolo"])}.pdf')


def spostamenti(pdf_senza, pdf_con):
    """{'dispari': {(dx, dy)}, 'pari': {(dx, dy)}} in pollici, arrotondati al millesimo: spostamento di ogni
    parola dal PDF senza bleed a quello con bleed (coordinate dall'alto a sinistra), per pagina dispari e pari."""
    import pymupdf
    out = {'dispari': set(), 'pari': set()}
    with pymupdf.open(pdf_senza) as a, pymupdf.open(pdf_con) as b:
        for i, (pa, pb) in enumerate(zip(a, b)):
            for wa, wb in zip(pa.get_text('words'), pb.get_text('words')):
                out['pari' if i % 2 else 'dispari'].add((round((wb[0] - wa[0]) / 72, 3), round((wb[1] - wa[1]) / 72, 3)))
    return {k: sorted(v) for k, v in out.items()}


def bleed_pdf(att, sez):
    """Bleed su una copia inventata del romance con formato.bleed: true, contro la stessa copia senza bleed.
    Formato = trim + bleed di dati/kdp.yaml; contenuto spostato di un bleed in basso su tutte le pagine e di
    un bleed a destra solo sulle pagine pari; margine esterno mai sotto il minimo KDP con bleed."""
    import verifica_pdf
    nome = 'mini-libro-romance con bleed'
    _, _, pdf_senza = pdf_di(copia_libro('mini-libro-romance'))
    c = copia_libro('mini-libro-romance')
    py = os.path.join(c, 'libro.yaml')
    testo = open(py, encoding='utf-8').read()
    open(py, 'w', encoding='utf-8').write(testo.replace('  bleed: false', '  bleed: true'))
    cart, libro, pdf = pdf_di(c)
    b = comune.kdp()['cartaceo']['bleed_pollici']
    s = struttura_pdf(pdf, libro) if os.path.isfile(pdf) else {}
    esito('impagina.py', f'{nome}: formato = trim + bleed di dati/kdp.yaml', 'uguale al trim KDP', s.get('formato_pollici'), sez)
    sp = spostamenti(pdf_senza, pdf) if os.path.isfile(pdf) else {}
    esito('impagina.py', f'{nome}: pagine dispari, contenuto spostato (dx, dy)', [(0.0, b)], sp.get('dispari'), sez)
    esito('impagina.py', f'{nome}: pagine pari, contenuto spostato (dx, dy)', [(b, b)], sp.get('pari'), sez)
    misure, _ = verifica_pdf.verifica(cart, libro, pdf)
    esito('verifica_pdf.py', f'{nome}: soglia KDP margine esterno con bleed', att['soglia_esterno'],
          misure['margine_esterno_soglia'], sez)
    esito('verifica_pdf.py', f'{nome}: margine esterno',
          *controllo_margine(att['margine_esterno'], misure['margine_esterno'], minimi_kdp(libro, misure['pagine'])['esterno']), sez)


# ---------------------------------------------------------------- passo 4

def passo_4(A):
    import pymupdf
    import conformita_kdp
    sez = 'passo 4'
    oggi = ['--oggi', '2026-10-02']

    def prepara(nome, scheda):
        c = copia_libro(nome)
        for s in ('compila.py', 'impagina.py', 'pacchetto.py'):
            esegui(os.path.join(S, s), c)
        shutil.copyfile(os.path.join(M, 'prove', 'pubblicazione', scheda),
                        os.path.join(c, '06-pubblicazione', 'scheda-amazon.md'))
        return c

    def sezioni(c, argv=()):
        cart, libro, _ = comune.carica_libro(c)
        S_, _ = conformita_kdp.controlla(cart, libro, list(argv))
        return S_

    for nome, scheda in (('mini-libro', 'scheda-giallo.md'), ('mini-libro-romance', 'scheda-romance.md')):
        att = A['mini-libri'][nome]
        c = prepara(nome, scheda)
        r = esegui(os.path.join(S, 'conformita_kdp.py'), c, *oggi)
        esito('conformita_kdp.py', f"{nome}: codice d'uscita", att['codice'], r.returncode, sez)
        S_ = sezioni(c)
        esito('conformita_kdp.py', f'{nome}: sezioni KO', att['ko'], [n for n, s in S_.items() if s.ko], sez)
        esito('conformita_kdp.py', f'{nome}: sezioni con avvisi', att['avvisi'], [n for n, s in S_.items() if s.avvisi], sez)
        esito('conformita_kdp.py', f'{nome}: sezione 11 pagine sotto il minimo', att['sezione_11_pagine'],
              next((x for x in S_[11].ko if 'minimo' in x), 'assente'), sez)
        esito('conformita_kdp.py', f'{nome}: report scritto', 'sì',
              'sì' if os.path.isfile(os.path.join(c, '06-pubblicazione', 'conformita-kdp.md')) else 'no', sez)

    # percorso «tutto OK»: PDF sintetico di almeno 30 pagine, senza testo aggiunto
    att = A['tutto_ok']
    c = prepara('mini-libro', 'scheda-giallo.md')
    shutil.copyfile(os.path.join(M, 'prove', 'pubblicazione', 'conferme-tutto-ok.yaml'),
                    os.path.join(c, '06-pubblicazione', 'conferme-autore.yaml'))
    cart, libro, _ = comune.carica_libro(c)
    orig = os.path.join(cart, '05-output', f'{comune.nome_file(libro["titolo"])}.pdf')
    sint = os.path.join(tempfile.mkdtemp(dir=TMP), 'sintetico.pdf')
    with pymupdf.open(orig) as src:
        d = pymupdf.open()
        while d.page_count < 30:
            d.insert_pdf(src)
        d.set_metadata(src.metadata)
        d.save(sint)
        d.close()
    with pymupdf.open(sint) as d:
        esito('pymupdf', 'PDF sintetico: pagine', att['pagine_pdf_sintetico'], d.page_count, sez)
    mc = copia_motore()
    esegui(os.path.join(mc, 'script', 'kdp_verifica.py'), 'fatta', '2026-10-01', '--radice', mc, *oggi)
    r = esegui(os.path.join(mc, 'script', 'conformita_kdp.py'), c, '--radice', mc, '--pdf', sint, *oggi)
    esito('conformita_kdp.py', "tutto OK: codice d'uscita", att['codice'], r.returncode, sez)
    S_ = sezioni(c, ['--pdf', sint])
    esito('conformita_kdp.py', 'tutto OK: sezioni KO', att['ko'], [n for n, s in S_.items() if s.ko], sez)
    esito('conformita_kdp.py', 'tutto OK: sezioni con avvisi', att['avvisi'], [n for n, s in S_.items() if s.avvisi], sez)
    r = esegui(os.path.join(S, 'conformita_kdp.py'), c, '--pdf', sint, *oggi)
    esito('conformita_kdp.py', "verifica KDP nulla: codice d'uscita", A['verifica']['nulla'], r.returncode, sez)
    mc2 = copia_motore()
    esegui(os.path.join(mc2, 'script', 'kdp_verifica.py'), 'fatta', '2026-08-01', '--radice', mc2, *oggi)
    r = esegui(os.path.join(mc2, 'script', 'conformita_kdp.py'), c, '--radice', mc2, '--pdf', sint, *oggi)
    esito('conformita_kdp.py', "verifica KDP scaduta: codice d'uscita", A['verifica']['scaduta'], r.returncode, sez)

    pc = os.path.join(c, '06-pubblicazione', 'conferme-autore.yaml')
    base_conf = open(pc, encoding='utf-8').read()
    for chiave, valore in (('falso', 'false'), ('vero', 'true')):
        open(pc, 'w', encoding='utf-8').write(base_conf.replace('formato_confermato_kdp: true', f'formato_confermato_kdp: {valore}'))
        S_ = sezioni(c, ['--pdf', sint])
        av = any('formato' in x for x in S_[11].avvisi)
        esito('conformita_kdp.py', f'formato_confermato_kdp {valore}: sezione 11',
              A['formato_confermato'][chiave], {'esito_11': S_[11].esito, 'avviso_formato': 'sì' if av else 'no'}, sez)
    open(pc, 'w', encoding='utf-8').write(base_conf)
    pl = os.path.join(c, 'libro.yaml')
    base_libro = open(pl, encoding='utf-8').read()
    for chiave, valore in (('falso', 'false'), ('vero', 'true')):
        open(pl, 'w', encoding='utf-8').write(base_libro.replace('\nformato:\n', f'\nformato:\n  formato_confermato_kdp: {valore}\n', 1))
        S_ = sezioni(c, ['--pdf', sint])
        av = any('formato' in x for x in S_[11].avvisi)
        esito('conformita_kdp.py', f'libro.yaml formato.formato_confermato_kdp {valore}: sezione 11',
              A['formato_confermato_libro'][chiave], {'esito_11': S_[11].esito, 'avviso_formato': 'sì' if av else 'no'}, sez)
    open(pl, 'w', encoding='utf-8').write(base_libro)

    ps = os.path.join(c, '06-pubblicazione', 'scheda-amazon.md')
    base_scheda = open(ps, encoding='utf-8').read()
    modifiche = {
        'parola_amazzonia': lambda s: s.replace('5. registro segreto', '5. viaggio in Amazzonia'),
        'parola_kindle': lambda s: s.replace('5. registro segreto', '5. romanzo Kindle'),
        'descrizione_4001': lambda s: s.replace('## Parole chiave', 'x' * 4001 + '\n\n## Parole chiave'),
        'url_nella_descrizione': lambda s: s.replace('## Parole chiave', 'Leggi su www.esempio-prova.it\n\n## Parole chiave'),
        'otto_parole_chiave': lambda s: s.replace('5. registro segreto', '5. registro segreto\n6. sei parole\n7. sette parole\n8. otto parole'),
        'autore_diverso': lambda s: s.replace('Autore: Autore di Prova', 'Autore: Altro Autore'),
    }
    for chiave, f in modifiche.items():
        open(ps, 'w', encoding='utf-8').write(f(base_scheda))
        att = A['scheda_modificata'][chiave]
        S_ = sezioni(c, ['--pdf', sint])
        esito('conformita_kdp.py', f'{chiave}: sezione {att["sezione"]}', att['esito'], S_[att['sezione']].esito, sez)
    open(ps, 'w', encoding='utf-8').write(base_scheda)

    # kdp_verifica.py
    kv = A['kdp_verifica']
    mc = copia_motore()
    kvs = os.path.join(mc, 'script', 'kdp_verifica.py')
    esito('kdp_verifica.py', 'data futura rifiutata', kv['data_futura'],
          esegui(kvs, 'fatta', '2026-12-31', '--radice', mc, *oggi).returncode, sez)
    esito('kdp_verifica.py', 'data scritta male rifiutata', kv['data_malformata'],
          esegui(kvs, 'fatta', '1-10-2026', '--radice', mc, *oggi).returncode, sez)
    esito('kdp_verifica.py', 'data valida accettata', kv['data_valida'],
          esegui(kvs, 'fatta', '2026-10-01', '--radice', mc, *oggi).returncode, sez)
    riga = next((r.split('#')[0].strip() for r in open(os.path.join(mc, 'dati', 'kdp.yaml'), encoding='utf-8') if r.startswith('ultima_verifica:')), '')
    esito('kdp_verifica.py', 'ultima_verifica scritta in dati/kdp.yaml', kv['riga_kdp_yaml'], riga, sez)
    reg = [r for r in open(os.path.join(mc, 'dati', 'verifiche-kdp.md'), encoding='utf-8') if r.startswith('| 2026')]
    esito('kdp_verifica.py', 'righe nel registro delle verifiche', kv['righe_registro'], len(reg), sez)
    r = esegui(kvs, 'fatta', '2026-07-01', '--radice', mc, *oggi)
    esito('kdp_verifica.py', 'data già scaduta: accettata con avviso', kv['data_vecchia_avviso'],
          'sì' if r.returncode == 0 and 'AVVISO' in r.stdout else 'no', sez)
    r = esegui(os.path.join(S, 'kdp_verifica.py'), 'controlla', '--simula-blocco')
    esito('kdp_verifica.py', 'promemoria dei sette valori (proxy bloccato)', kv['promemoria_righe_numerate'],
          len(re.findall(r'(?m)^[1-7] ', r.stdout)), sez)

    # recinto: eccezione dichiarata di «verifica KDP fatta»
    mc = copia_motore()
    cmd = f'{sys.executable} -B {os.path.join(mc, "script", "kdp_verifica.py")} fatta 2026-10-01 --radice {mc} --oggi 2026-10-02'
    r = esegui(os.path.join(mc, 'script', 'recinto.py'), '--radice', mc, '--extra', cmd)
    esito('recinto.py', "eccezione «verifica KDP fatta»: codice d'uscita", A['recinto_eccezione']['codice'], r.returncode, sez)
    esito('recinto.py', 'eccezione «verifica KDP fatta»: eccezioni riportate', A['recinto_eccezione']['eccezioni'],
          r.stdout.count('ECCEZIONE'), sez)

    # pacchetto
    c = copia_libro('mini-libro')
    r = esegui(os.path.join(S, 'pacchetto.py'), c)
    esito('pacchetto.py', 'file creati', A['pacchetto']['creati'], r.stdout.count('creato:'), sez)
    ps = os.path.join(c, '06-pubblicazione', 'scheda-amazon.md')
    open(ps, 'a', encoding='utf-8').write('\nriga dell\'autore\n')
    r = esegui(os.path.join(S, 'pacchetto.py'), c)
    esito('pacchetto.py', 'seconda esecuzione: file creati', A['pacchetto']['seconda_esecuzione_creati'], r.stdout.count('creato:'), sez)
    esito('pacchetto.py', 'scheda già presente non toccata', A['pacchetto']['scheda_non_toccata'],
          'sì' if open(ps, encoding='utf-8').read().endswith("riga dell'autore\n") else 'no', sez)


# ---------------------------------------------------------------- passo 5

def passo_5(A):
    import json
    import time
    import fase
    import recinto
    sez = 'passo 5'
    E = {k: v for k, v in ENV.items() if k not in ('CLAUDE_PROJECT_DIR', 'ZB_LIBRO', 'ZB_RAMO', 'ZB_SESSIONE')}
    E.update(GIT_AUTHOR_NAME='Prova', GIT_AUTHOR_EMAIL='prova@esempio.invalid',
             GIT_COMMITTER_NAME='Prova', GIT_COMMITTER_EMAIL='prova@esempio.invalid')
    py = [sys.executable, '-B']

    def zb(cwd, *a, env=None, motore=M):
        return subprocess.run(py + [os.path.join(motore, 'zb'), *a], cwd=cwd, env=env or E, capture_output=True, text=True)

    def git(cwd, *a):
        return subprocess.run(['git', *a], cwd=cwd, env=E, capture_output=True, text=True)

    def repo():
        d = tempfile.mkdtemp(dir=TMP)
        git(d, 'init', '-q', '--bare', 'remoto.git')
        r = os.path.join(d, 'repo')
        os.makedirs(r)
        git(r, 'init', '-q')
        git(r, 'checkout', '-q', '-b', 'prova')
        git(r, 'remote', 'add', 'origin', os.path.join(d, 'remoto.git'))
        return r

    def salva(r, msg='prova'):
        git(r, 'add', '-A')
        git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', msg)
        return git(r, 'push', '-q', '-u', 'origin', 'prova').returncode

    def stato(L):
        return comune.leggi_yaml(os.path.join(L, 'stato.yaml'))

    def gate(L):
        s = stato(L)
        return f'{s["fase"]} / {s["gate_in_attesa"] or "nessuno"}'

    def mancanti(testo):
        return [r[2:].split(':')[0] for r in testo.splitlines() if r.startswith('- ')]

    def diff(base, prima, escludi=None):
        return [d for d in recinto.differenze(prima, recinto.foto(base)) if not (escludi and d.startswith(escludi))]

    briefing = open(os.path.join(M, 'prove', 'briefing', 'briefing-giallo.md'), encoding='utf-8').read()

    def libro_nuovo(testo=briefing, nome='giallo', prima_di=None):
        r = repo()
        L = os.path.join(r, nome)
        os.makedirs(L)
        if prima_di:
            prima_di(L)
        open(os.path.join(L, 'briefing.md'), 'w', encoding='utf-8').write(testo)
        p = zb(r, 'nuovo', f'{nome}/briefing.md')
        salva(r, 'nuovo libro')
        return r, L, p

    # --- nuovo da un briefing inventato
    a = A['nuovo']
    r = repo()
    L = os.path.join(r, 'giallo')
    os.makedirs(L)
    open(os.path.join(L, 'briefing.md'), 'w', encoding='utf-8').write(briefing)
    foto_r, foto_m = recinto.foto(r), recinto.foto(M)
    p = zb(r, 'nuovo', 'giallo/briefing.md')
    esito('nuovo.py', "briefing inventato: codice d'uscita", a['codice'], p.returncode, sez)
    creati = sorted(os.path.relpath(os.path.join(d, f), L) for d, _, fs in os.walk(L) for f in fs)
    esito('nuovo.py', 'file creati nella cartella del libro', a['file'], creati, sez)
    esito('nuovo.py', 'scritture fuori dalla cartella del libro (repo e motore)', a['fuori'],
          diff(r, foto_r, 'giallo/') + recinto.differenze(foto_m, recinto.foto(M)), sez)
    _, libro, _ = comune.carica_libro(L)
    esito('nuovo.py', 'libro.yaml valido (schema, lingua, profilo)', a['libro_valido'], 'sì', sez)
    esito('nuovo.py', 'stato iniziale (fase / gate)', a['stato'], gate(L), sez)
    esito('nuovo.py', 'capitoli previsti dal piano parole', a['capitoli'], fase.capitoli_previsti(L), sez)
    esito('nuovo.py', 'voci da Tetti e Vietati', a['voci'], [v['id'] for v in libro['voci']], sez)
    esito('nuovo.py', 'vincolo «vietato prima del 2»', a['vincolo'], libro['nome_vietato_prima_di'][0]['vietato_in'], sez)
    esito('nuovo.py', 'gate da Direttive', a['gate'], libro['gate'], sez)
    open(os.path.join(L, 'briefing.md'), 'w', encoding='utf-8').write(briefing)
    sha = comune.sha256_file(os.path.join(L, 'libro.yaml'))
    p = zb(r, 'nuovo', 'giallo/briefing.md')
    esito('nuovo.py', 'libro già esistente: rifiutato, libro.yaml intatto', a['esistente'],
          f'{p.returncode} / {"intatto" if comune.sha256_file(os.path.join(L, "libro.yaml")) == sha else "cambiato"}', sez)

    # --- briefing incompleto
    a = A['briefing_incompleto']
    inc = re.sub(r'(## Idea[^\n]*\n)(?:[^#\n][^\n]*\n)+', r'\1', briefing.replace('Autore: Autore di Prova\n', '')
                 .replace('Lunghezza: 60000', 'Lunghezza: 9000'))
    d = tempfile.mkdtemp(dir=TMP)
    os.makedirs(os.path.join(d, 'incompleto'))
    open(os.path.join(d, 'incompleto', 'briefing.md'), 'w', encoding='utf-8').write(inc)
    prima = recinto.foto(d)
    p = zb(d, 'nuovo', 'incompleto/briefing.md')
    esito('nuovo.py', "briefing incompleto: codice d'uscita", a['codice'], p.returncode, sez)
    esito('nuovo.py', 'briefing incompleto: voci mancanti elencate', a['mancano'], mancanti(p.stderr), sez)
    esito('nuovo.py', 'briefing incompleto: niente creato', a['creato'], diff(d, prima), sez)
    p = zb(d, 'avvio', 'incompleto')
    esito('avvio.py', "solo briefing incompleto: codice d'uscita", a['codice'], p.returncode, sez)
    esito('avvio.py', 'solo briefing incompleto: voci mancanti elencate', a['mancano'], mancanti(p.stderr), sez)
    esito('avvio.py', 'solo briefing incompleto: niente scritto', a['creato'], diff(d, prima), sez)
    r2, L2, _ = libro_nuovo()
    pb = os.path.join(L2, '00-progetto', 'briefing.md')
    testo_b = open(pb, encoding='utf-8').read()
    open(pb, 'w', encoding='utf-8').write(testo_b.replace('Autore: Autore di Prova\n', ''))
    salva(r2, 'briefing svuotato')
    p = zb(r2, 'avvio', 'giallo')
    esito('avvio.py', 'fase documenti, briefing reso incompleto: fermo', a['avvio_libro'],
          f'{p.returncode} / {mancanti(p.stderr)}', sez)

    # --- avvio
    a = A['avvio']
    r, L, _ = libro_nuovo()
    p = zb(r, 'avvio', 'giallo')
    esito('avvio.py', "libro pulito e pushato: codice d'uscita", a['codice'], p.returncode, sez)
    esito('avvio.py', 'riga «Letto»: file con righe, sha256 e ultimo commit', a['file_letti'],
          len(re.findall(r'\(\d+ righe, sha256 [0-9a-f]{12}, commit [0-9a-f]{7,}\)', p.stdout))
          if 'Letto: ' in p.stdout else 0, sez)
    esito('avvio.py', 'riga «Letto»: commit del libro e del motore', 'sì',
          'sì' if re.search(r'libro @ [0-9a-f]{7,} .*; motore @ [0-9a-f]{7,}', p.stdout) else 'no', sez)
    esito('avvio.py', 'marker di sessione (senza hook: «locale»)', 'sì',
          'sì' if os.path.isfile(os.path.join(L, '.zb', 'letto-locale')) else 'no', sez)
    esito('avvio.py', 'git status dopo l\'avvio', a['git_status'], git(r, 'status', '--porcelain').stdout.strip() or 'pulito', sez)
    subprocess.run(py + [os.path.join(S, 'hook_sessione.py')], input=json.dumps({'session_id': 'sessione-prova', 'source': 'startup'}),
                   env=dict(E, CLAUDE_PROJECT_DIR=r), capture_output=True, text=True)
    p = zb(r, 'avvio', 'giallo', env=dict(E, CLAUDE_PROJECT_DIR=r))
    esito('avvio.py', 'marker con il session_id dell\'hook SessionStart', 'sì',
          'sì' if p.returncode == 0 and os.path.isfile(os.path.join(L, '.zb', 'letto-sessione-prova')) else 'no', sez)
    # fermate
    r, L, _ = libro_nuovo()
    git(r, 'remote', 'set-url', 'origin', os.path.join(TMP, 'remoto-inesistente.git'))
    prima = recinto.foto(os.path.dirname(r))
    p = zb(r, 'avvio', 'giallo')
    esito('avvio.py', 'sessione che non può pushare: fermo', a['non_scrivibile'],
          f'{p.returncode} / {"push --dry-run" in p.stderr}', sez)
    esito('avvio.py', 'sessione che non può pushare: niente scritto', [], diff(os.path.dirname(r), prima), sez)
    d = tempfile.mkdtemp(dir=TMP)
    Lc = shutil.copytree(L, os.path.join(d, 'giallo'), ignore=shutil.ignore_patterns('.zb'))
    prima = recinto.foto(d)
    p = zb(d, 'avvio', Lc)
    esito('avvio.py', 'libro fuori da git: fermo, niente scritto', a['fuori_git'],
          f'{p.returncode} / {diff(d, prima)}', sez)
    r, L, _ = libro_nuovo()
    open(os.path.join(L, '02-bibbia', 'bibbia.md'), 'a', encoding='utf-8').write('- riga non salvata\n')
    p = zb(r, 'avvio', 'giallo')
    esito('avvio.py', 'modifiche non salvate: fermo', a['non_salvate'], f'{p.returncode} / {"non salvate" in p.stderr}', sez)
    git(r, 'checkout', '--', '.')
    p = zb(r, 'avvio', 'giallo', env=dict(E, ZB_RAMO='altro-ramo'))
    esito('avvio.py', 'ramo diverso da quello della sessione: fermo', a['ramo'], f'{p.returncode} / {"altro-ramo" in p.stderr}', sez)

    # --- fase.py: gate documenti
    a = A['gate_documenti']
    r, L, _ = libro_nuovo()
    esito('fase.py', 'ok senza gate aperto', a['ok_senza_gate'], zb(r, 'ok', 'giallo').returncode, sez)
    p = zb(r, 'pronto', 'giallo')
    rc = stato(L)['revisione_in_corso']
    esito('fase.py', 'pronto: gate aperto e blocco mostrato', a['pronto'],
          f'{gate(L)} / blocco {rc["blocco"]} di {rc["blocchi_totali"]}', sez)
    p = zb(r, 'ok', 'giallo')
    esito('fase.py', 'ok prima di aver mostrato tutto', a['ok_presto'], f'{p.returncode} / {"Mancano i blocchi" in p.stderr}', sez)
    for _ in range(5):
        p = zb(r, 'avanti', 'giallo')
    esito('fase.py', 'avanti fino all\'ultimo blocco', a['ultimo_blocco'],
          f'{"Blocco 6 di 6" in p.stdout} / {"Fine dei documenti" in p.stdout}', sez)
    p = zb(r, 'correggi', 'giallo', ': aggiungi', 'un', 'luogo')
    esito('fase.py', 'correggi: registrata, gate invariato', a['correggi'],
          f'{p.returncode} / {len(stato(L)["correzioni_aperte"])} / {gate(L)}', sez)
    p = zb(r, 'ok', 'giallo')
    esito('fase.py', 'ok con correzione non applicata', a['ok_correzione_pendente'],
          f'{p.returncode} / {"non ancora applicata" in p.stderr}', sez)
    open(os.path.join(L, '02-bibbia', 'bibbia.md'), 'a', encoding='utf-8').write('- Il forno di via Lunga\n')
    p = zb(r, 'ok', 'giallo')
    esito('fase.py', 'ok dopo la correzione senza rileggere', a['ok_documenti_cambiati'],
          f'{p.returncode} / {"mostrati per intero" in p.stderr}', sez)
    p = zb(r, 'avanti', 'giallo')
    esito('fase.py', 'avanti dopo la correzione: si riparte dal blocco 1', a['riparte'],
          f'{"riparte dal blocco 1" in p.stdout} / {stato(L)["revisione_in_corso"]["blocco"]}', sez)
    for _ in range(5):
        zb(r, 'avanti', 'giallo')
    p = zb(r, 'ok', 'giallo')
    esito('fase.py', 'ok con documenti non salvati', a['ok_non_salvati'], f'{p.returncode} / {"non salvate" in p.stderr}', sez)
    salva(r, 'correzione')
    sha_st = comune.sha256_file(os.path.join(L, 'stato.yaml'))
    p = zb(r, 'stato', 'giallo')
    esito('fase.py', 'stato: a schermo, stato.yaml intatto', a['stato'],
          f'{p.returncode} / {comune.sha256_file(os.path.join(L, "stato.yaml")) == sha_st}', sez)
    p = zb(r, 'ok', 'giallo')
    s = stato(L)
    esito('fase.py', 'ok: approvato, fase successiva', a['ok'],
          f'{p.returncode} / {gate(L)} / {len(s["documenti_approvati"])} / {len(s["correzioni_aperte"])}', sez)
    esito('fase.py', 'LEGGIMI aggiornato', a['leggimi'],
          next(x for x in open(os.path.join(L, 'LEGGIMI.md'), encoding='utf-8').read().splitlines() if x.startswith('Fase:')), sez)
    salva(r, 'ok documenti')
    esito('avvio.py', 'dopo l\'ok: avvio', a['avvio_dopo_ok'], zb(r, 'avvio', 'giallo').returncode, sez)
    pb = os.path.join(L, '02-bibbia', 'bibbia.md')
    orig = open(pb, encoding='utf-8').read()
    open(pb, 'a', encoding='utf-8').write('- fuori procedura\n')
    salva(r, 'modifica fuori procedura')
    p = zb(r, 'avvio', 'giallo')
    esito('avvio.py', 'documento approvato cambiato: fermo', a['approvato_cambiato'],
          f'{p.returncode} / {"02-bibbia/bibbia.md" in p.stderr}', sez)
    open(pb, 'w', encoding='utf-8').write(orig)
    salva(r, 'ripristino')
    os.makedirs(os.path.join(L, '05-revisioni'), exist_ok=True)
    open(os.path.join(L, '05-revisioni', 'pagina-campione.md'), 'w', encoding='utf-8').write('# Pagina campione\n\nTesto di prova.\n')
    salva(r, 'pagina campione')
    zb(r, 'pronto', 'giallo')
    esito('fase.py', 'pagina campione: gate', a['gate_pagina'], gate(L), sez)
    p = zb(r, 'ok', 'giallo')
    esito('fase.py', 'pagina campione: ok', a['ok_pagina'], f'{p.returncode} / {gate(L)} / {stato(L)["passo"]}', sez)

    # --- gate configurabili
    a = A['gate_configurabili']
    r, L, _ = libro_nuovo(briefing.replace('Gate: documenti, pagina_campione, primi_capitoli', 'Gate: primi_capitoli'))
    p = zb(r, 'pronto', 'giallo')
    s = stato(L)
    esito('fase.py', 'gate «documenti» disattivato: pronto passa oltre', a['senza_gate_documenti'],
          f'{p.returncode} / {gate(L)} / {sum(1 for v in s["documenti_approvati"].values() if v.get("senza_gate"))}', sez)

    def mini(gate_libro=None, dimensione=3):
        r = repo()
        Lm = shutil.copytree(os.path.join(M, 'prove', 'mini-libro'), os.path.join(r, 'mini'))
        if gate_libro is not None:
            open(os.path.join(Lm, 'libro.yaml'), 'a', encoding='utf-8').write(f'gate: {gate_libro}\n')
        s = comune.leggi_yaml(os.path.join(M, 'modelli', 'stato.yaml'))
        s.update(libro='Prova di stampa', fase='stesura', passo='capitolo 1', aggiornato='prova')
        s['lotto']['dimensione'] = dimensione
        open(os.path.join(Lm, 'stato.yaml'), 'w', encoding='utf-8').write(yaml.safe_dump(s, sort_keys=False, allow_unicode=True))
        salva(r, 'mini')
        return r, Lm

    r, Lm = mini('[lotto]', 1)
    zb(r, 'esito', 'mini', '1')
    esito('fase.py', 'gate «lotto» attivo, lotti da 1: fermata dopo il capitolo 1', a['lotto_attivo'], gate(Lm), sez)
    r, Lm = mini('[]', 1)
    p = zb(r, 'esito', 'mini', '1')
    esito('fase.py', 'nessun gate, lotti da 1: nessuna fermata', a['lotto_senza_gate'],
          f'{gate(Lm)} / {"nessuna fermata" in p.stdout}', sez)

    # --- stesura sul mini-libro giallo (capitolo 1 OK, 2 e 3 KO per costruzione)
    a = A['stesura']
    r, Lm = mini()
    p = zb(r, 'esito', 'mini', '1')
    esito('fase.py', 'esito 1 (OK)', a['esito_1'], f'{p.returncode} / {stato(Lm)["ultimo_capitolo_scritto"]} / {gate(Lm)}', sez)
    p = zb(r, 'esito', 'mini', '2')
    esito('fase.py', 'esito 2, primo KO: correzione unica, nessuna fermata', a['esito_2_primo'],
          f'{p.returncode} / {stato(Lm)["tentativi"]} / {gate(Lm)}', sez)
    p = zb(r, 'esito', 'mini', '2')
    esito('fase.py', 'esito 2, secondo KO: fermata', a['esito_2_secondo'], f'{p.returncode} / {gate(Lm)}', sez)
    p = zb(r, 'esito', 'mini', '3')
    esito('fase.py', 'esito 3 con gate aperto: rifiutato', a['esito_3_gate_aperto'], p.returncode, sez)
    salva(r, 'report 2')
    zb(r, 'avanti', 'mini')
    p = zb(r, 'ok', 'mini')
    s = stato(Lm)
    esito('fase.py', 'ok al controllo fallito: capitolo accettato', a['ok_controllo'],
          f'{p.returncode} / {gate(Lm)} / {s["passo"]} / {s["tentativi"]}', sez)
    zb(r, 'esito', 'mini', '3')
    zb(r, 'esito', 'mini', '3')
    salva(r, 'report 3')
    zb(r, 'avanti', 'mini')
    zb(r, 'ok', 'mini')
    esito('fase.py', 'dopo il capitolo 3: gate «primi_capitoli»', a['primi_capitoli'], gate(Lm), sez)
    salva(r, 'primi capitoli')
    for _ in range(30):
        if 'Fine dei documenti' in zb(r, 'avanti', 'mini').stdout:
            break
    p = zb(r, 'ok', 'mini', 'lotti', 'da', '5')
    s = stato(Lm)
    fase_dopo_ok = s['fase']       # manca ancora l'esito dell'interludio I: la fase resta «stesura»
    zb(r, 'esito', 'mini', 'interludio', 'I')
    s = stato(Lm)
    esito('fase.py', 'ok, lotti da 5: lotti, ultimo approvato, fase; fase dopo l\'interludio I', a['ok_lotti'],
          f'{p.returncode} / {s["lotto"]["dimensione"]} / {s["ultimo_capitolo_approvato"]} / {fase_dopo_ok} / {s["fase"]}', sez)
    p = zb(r, 'pronto', 'mini')
    esito('fase.py', 'chiusura senza report: fermo con elenco', a['chiusura_incompleta'],
          f'{p.returncode} / {len(mancanti(p.stderr))}', sez)

    # --- nuovo e riscrittura
    a = A['modalita']
    ris = briefing.replace('Modalità: nuovo', 'Modalità: riscrittura')
    d = tempfile.mkdtemp(dir=TMP)
    os.makedirs(os.path.join(d, 'ris'))
    open(os.path.join(d, 'ris', 'briefing.md'), 'w', encoding='utf-8').write(ris)
    p = zb(d, 'nuovo', 'ris/briefing.md')
    esito('nuovo.py', 'riscrittura senza testo precedente: rifiutato', a['senza_testo'], f'{p.returncode} / {mancanti(p.stderr)}', sez)

    def testo_prec(Lx):
        os.makedirs(os.path.join(Lx, '01-originale'))
        open(os.path.join(Lx, '01-originale', 'testo-precedente.md'), 'w', encoding='utf-8').write('# Vecchio testo\n\nUna riga.\n')

    rr, Lr, p = libro_nuovo(ris.replace('Testo precedente:\n', 'Testo precedente: 01-originale/testo-precedente.md\n'),
                            'ris', testo_prec)
    _, lr, _ = comune.carica_libro(Lr)
    rn, Ln, _ = libro_nuovo()
    _, ln, _ = comune.carica_libro(Ln)
    esito('nuovo.py', 'libro.yaml: modalità e testo precedente (riscrittura | nuovo)', a['libro_yaml'],
          f'{lr["modalita"]} {lr.get("testo_precedente", "assente")} | {ln["modalita"]} {ln.get("testo_precedente", "assente")}', sez)
    pr, pn = zb(rr, 'avvio', 'ris'), zb(rn, 'avvio', 'giallo')
    esito('avvio.py', 'testo precedente tra i file letti (riscrittura | nuovo)', a['avvio_letti'],
          f'{"testo-precedente.md (" in pr.stdout} | {"testo-precedente.md (" in pn.stdout}', sez)
    esito('nuovo.py', 'LEGGIMI: modalità (riscrittura | nuovo)', a['leggimi'],
          ' | '.join(next(x for x in open(os.path.join(Lx, 'LEGGIMI.md'), encoding='utf-8').read().splitlines()
                          if x.startswith('Modalità')) for Lx in (Lr, Ln)), sez)

    # --- CLAUDE.md
    a = A['claude_md']
    testo = open(os.path.join(os.path.dirname(M), 'CLAUDE.md'), encoding='utf-8').read()
    esito('CLAUDE.md', 'righe (massimo 30)', a['righe_max_30'], 'sì' if len(testo.splitlines()) <= 30 else 'no', sez)
    nomi = ['libri/']
    nomi += [x.strip() for x in open(os.path.join(M, 'dati', 'nomi_vietati.txt'), encoding='utf-8') if x.strip() and not x.startswith('#')]
    for nome in ('mini-libro', 'mini-libro-romance'):
        lb = comune.leggi_yaml(os.path.join(M, 'prove', nome, 'libro.yaml'))
        nomi += [lb['titolo'], lb['autore']]
        nomi += [x.strip() for x in open(os.path.join(M, 'prove', nome, 'nomi_propri.txt'), encoding='utf-8') if x.strip() and not x.startswith('#')]
    nomi += ['La chiave del forno', 'Nadia Ferro', 'Ugo Pelle']
    esito('CLAUDE.md', 'nomi di libri trovati', a['nomi'], [n for n in nomi if n.lower() in testo.lower()], sez)
    esito('CLAUDE.md', 'frasi obbligatorie mancanti', a['frasi'], [f for f in a['frasi_obbligatorie'] if f not in testo], sez)

    # --- hook in modalità avviso (scenari di PROCEDURA.md, sezione 10)
    a = A['hook']
    hr = repo()
    Lh = shutil.copytree(os.path.join(M, 'prove', 'mini-libro'), os.path.join(hr, 'libri-prova', 'mini'))
    os.makedirs(os.path.join(hr, 'documenti', '04-manoscritto'))
    F = 'libri-prova/mini/04-manoscritto/01-la-farmacia.md'
    cart_m = os.path.join(Lh, '04-manoscritto')

    def hook(dati, env=E, motore=M, cwd=hr):
        raw = dati if isinstance(dati, str) else json.dumps(dict({'session_id': 'sessione-prova', 'cwd': cwd}, **dati))
        return subprocess.run(py + [os.path.join(motore, 'script', 'hook_manoscritto.py')], input=raw, cwd=cwd,
                              env=env, capture_output=True, text=True)

    def tipo(p):
        return f'{"avviso" if "ATTENZIONE" in p.stdout else "niente"} / {p.returncode}'

    B = lambda c: {'tool_name': 'Bash', 'tool_input': {'command': c}}
    casi = {
        'Write': {'tool_name': 'Write', 'tool_input': {'file_path': F, 'content': 'x'}},
        'Edit': {'tool_name': 'Edit', 'tool_input': {'file_path': os.path.join(hr, F)}},
        'Write fuori dal manoscritto': {'tool_name': 'Write', 'tool_input': {'file_path': 'libri-prova/mini/02-bibbia/bibbia.md'}},
        '1': B(f'grep -n x {F} > {os.path.join(TMP, "out.txt")}'),
        '2': B('python3 motore/script/capitolo.py libri-prova/mini 1'),
        '3': B(f"python3 -c \"open('{F}','w').write('x')\""),
        '4': B(f'python3 {os.path.join(TMP, "s.py")}'),
        '5': B('D=libri-prova/mini/04-manoscritto; echo x > $D/01-la-farmacia.md'),
        '6': B("cd libri-prova/mini/04-manoscritto && sed -i 's/a/b/' 01-la-farmacia.md"),
        '8': B(f'git add {F} && git commit -m x && git push'),
        '9': B(f'git checkout -- {F}'),
        '10': B(f'cp {F} {os.path.join(TMP, "copia.md")}'),
        '11': B('cat libri-prova/mini/04-manoscritto/*.md | wc -w'),
        '12': B('echo x > documenti/04-manoscritto/nota.md'),
    }
    for k, dati in casi.items():
        esito('hook_manoscritto.py', f'avviso, senza marker: {k}', a['scenari'][k], tipo(hook(dati)), sez)
    esito('hook_manoscritto.py', 'avviso, senza marker: 7 (cd in un comando precedente)', a['scenari']['7'],
          tipo(hook(B("sed -i 's/a/b/' 01-la-farmacia.md"), cwd=cart_m)), sez)
    esito('hook_manoscritto.py', 'avviso: 13 (JSON illeggibile)', a['scenari']['13'], tipo(hook('{non è json 04-manoscritto')), sez)
    esito('hook_manoscritto.py', 'avviso annotato in .zb/avvisi-hook.log', 'sì',
          'sì' if os.path.isfile(os.path.join(Lh, '.zb', 'avvisi-hook.log')) else 'no', sez)
    marker = os.path.join(Lh, '.zb', 'letto-sessione-prova')
    open(marker, 'w', encoding='utf-8').write('prova\n')
    esito('hook_manoscritto.py', 'con marker: Write', a['con_marker'], tipo(hook(casi['Write'])), sez)
    esito('hook_manoscritto.py', 'con marker: Bash 6', a['con_marker'], tipo(hook(casi['6'])), sez)
    t0 = time.time() - 60
    os.utime(marker, (t0, t0))
    p = subprocess.run(py + [os.path.join(S, 'hook_sessione.py')], input=json.dumps({'session_id': 'sessione-prova', 'source': 'compact'}),
                       env=dict(E, CLAUDE_PROJECT_DIR=hr), capture_output=True, text=True)
    esito('hook_sessione.py', 'compattazione: messaggio e codice', a['compact_sessione'],
          f'{"riesegui" in p.stdout} / {p.returncode}', sez)
    esito('hook_manoscritto.py', 'avviso: 14 (marker più vecchio della compattazione)', a['scenari']['14'],
          tipo(hook(casi['Write'], env=dict(E, CLAUDE_PROJECT_DIR=hr))), sez)
    esito('hook_sessione.py', 'session_id in .zb/sessione-corrente, .zb ignorata da git', a['sessione_corrente'],
          f'{open(os.path.join(hr, ".zb", "sessione-corrente"), encoding="utf-8").read().strip()} / '
          f'{git(hr, "status", "--porcelain", "--", ".zb").stdout.strip() or "ignorata"}', sez)
    mc = copia_motore()
    open(os.path.join(mc, 'dati', 'hook.yaml'), 'w', encoding='utf-8').write('modalita: blocco\n')
    altra = lambda dati: dict(dati, session_id='altra-sessione')
    esito('hook_manoscritto.py', 'modalità blocco (copia del motore): Write senza marker', a['blocco']['write'],
          hook(altra(casi['Write']), motore=mc).returncode, sez)
    esito('hook_manoscritto.py', 'modalità blocco: Write fuori dal manoscritto', a['blocco']['fuori'],
          hook(altra(casi['Write fuori dal manoscritto']), motore=mc).returncode, sez)
    esito('hook_manoscritto.py', 'modalità blocco: JSON illeggibile (con e senza 04-manoscritto)', a['blocco']['errore'],
          f'{hook("{x 04-manoscritto", motore=mc).returncode} / {hook("{x", motore=mc).returncode}', sez)

    # --- zb hook attiva / disattiva (su una copia del motore in un repository temporaneo)
    a = A['zb_hook']
    rh = repo()
    mz = shutil.copytree(M, os.path.join(rh, 'motore'))
    dest = os.path.join(rh, '.claude', 'settings.json')
    p = zb(rh, 'hook', 'attiva', motore=mz)
    esito('zb', 'hook attiva senza --ok: mostra soltanto', a['attiva_senza_ok'],
          f'{p.returncode} / {"presente" if os.path.exists(dest) else "assente"}', sez)
    p = zb(rh, 'hook', 'attiva', '--ok', motore=mz)
    esito('zb', 'hook attiva --ok: settings.json uguale al modello', a['attiva_ok'],
          f'{p.returncode} / {open(dest, encoding="utf-8").read() == open(os.path.join(mz, "dati", "hook-settings.esempio.json"), encoding="utf-8").read()}', sez)
    p = zb(rh, 'hook', 'disattiva', motore=mz)
    esito('zb', 'hook disattiva: settings.json tolto', a['disattiva'],
          f'{p.returncode} / {"presente" if os.path.exists(dest) else "assente"}', sez)
    os.makedirs(os.path.dirname(dest))
    open(dest, 'w', encoding='utf-8').write('{}\n')
    esito('zb', 'hook disattiva su un settings.json non del motore: rifiutato', a['disattiva_altrui'],
          f'{zb(rh, "hook", "disattiva", motore=mz).returncode} / {"presente" if os.path.exists(dest) else "assente"}', sez)
    esito('zb', '.claude/settings.json nel repository del motore', a['settings_nel_repo'],
          'presente' if os.path.exists(os.path.join(os.path.dirname(M), '.claude', 'settings.json')) else 'assente', sez)

    # --- revisione.py e zb
    a = A['revisione']
    Lv = copia_libro('mini-libro')
    paragrafi = ''.join(''.join(f'Paragrafo {i}, riga {j}.\n' for j in range(1, 9)) + '\n' for i in range(1, 31))
    os.makedirs(os.path.join(Lv, '05-revisioni'))
    open(os.path.join(Lv, '05-revisioni', 'lungo.md'), 'w', encoding='utf-8').write(paragrafi)
    prima = recinto.foto(Lv)
    blocchi = []
    for n in (1, 2, 3):
        p = zb(Lv, 'revisione', Lv, '05-revisioni/lungo.md', str(n))
        m = re.match(r'^.+ — 05-revisioni/lungo\.md — Blocco (\d) di (\d), righe (\d+-\d+) — sha256 [0-9a-f]{12}$', p.stdout.splitlines()[0])
        blocchi.append(m.group(3) if m else p.stdout.splitlines()[0])
    esito('revisione.py', 'blocchi tagliati a fine paragrafo (270 righe)', a['blocchi'], blocchi, sez)
    esito('revisione.py', 'sola lettura', [], diff(Lv, prima), sez)
    p = zb(Lv, 'ortografia', Lv)
    esito('zb', 'ortografia ora costruito (codice, «non esiste ancora»)', a['ortografia'], f'{p.returncode} / {"non esiste ancora" in p.stderr}', sez)
    esito('zb', 'conta <libro> --schermo', a['conta'], zb(Lv, 'conta', Lv, '--schermo').returncode, sez)


# ---------------------------------------------------------------- passo 5b

def passo_5b(A):
    import recinto
    sez = 'passo 5b'
    fx = os.path.join(M, 'prove', 'mini-libro-adozione')
    sha_fx = recinto.foto(fx)
    d = tempfile.mkdtemp(dir=TMP)
    L = shutil.copytree(fx, os.path.join(d, 'adozione'))
    prima_d, prima_m = recinto.foto(d), recinto.foto(M)
    p = esegui(os.path.join(S, 'adotta.py'), L)
    esito('adotta.py', "documenti parziali: codice d'uscita", A['codice'], p.returncode, sez)
    esito('adotta.py', 'file scritti', A['scritti'], [r[9:] for r in p.stdout.splitlines() if r.startswith('scritto: ')], sez)
    fuori = [x for x in recinto.differenze(prima_d, recinto.foto(d)) if not x.startswith('adozione/')]
    esito('adotta.py', 'scritture fuori dalla cartella (e nel motore)', [], fuori + recinto.differenze(prima_m, recinto.foto(M)), sez)
    esito('adotta.py', 'mini-libro di prova originale intatto', [], recinto.differenze(sha_fx, recinto.foto(fx)), sez)
    rep = open(os.path.join(L, '06-diagnostica', 'adozione.md'), encoding='utf-8').read()
    tab = [r for r in rep.splitlines() if r.startswith('| ') and not r.startswith('| Campo')]
    esito('adotta.py', 'valori con fonte file:riga (o cartella)', 'tutti',
          'tutti' if tab and all(re.search(r'\| ([^|]*:\d+|[^|]*\(cartella presente\)|predefinito[^|]*) \|$', r) for r in tab) else
          [r for r in tab if not re.search(r':\d+ \|$', r)], sez)
    esito('adotta.py', 'valori ricavati', A['ricavati'], len(tab), sez)
    esito('adotta.py', 'non ricavati elencati', A['non_ricavati'],
          [r[len('non ricavato: '):] for r in p.stdout.splitlines() if r.startswith('non ricavato: ')], sez)
    lb = yaml.safe_load(open(os.path.join(L, 'libro.yaml'), encoding='utf-8'))
    esito('adotta.py', 'override con motivo (campo e fonte)', A['override'],
          [f'{o["campo"]} {o["valore"]} {o["motivo"].split(" dice ")[0]}' for o in lb['override']], sez)
    esito('adotta.py', 'libro.yaml: titolo, profilo, parole, voci, vincoli', A['libro'],
          f'{lb["titolo"]} / {lb["profilo"]} / {lb["parole"]["target_totale"]} / {[v["id"] for v in lb["voci"]]} / '
          f'{[(n["nome"], n["vietato_in"]) for n in lb["nome_vietato_prima_di"]]}', sez)
    esito('adotta.py', 'libro.yaml senza autore: non valido (segnalato)', A['valido'],
          'no' if 'libro.yaml valido: no' in p.stdout else 'sì', sez)
    cr = yaml.safe_load(open(os.path.join(L, 'cronologia.yaml'), encoding='utf-8'))
    esito('adotta.py', 'cronologia: nascite / eventi', A['cronologia'], f'{len(cr["nascite"])} / {len(cr["eventi"])}', sez)
    esito('adotta.py', 'nomi_propri.txt', A['nomi'], open(os.path.join(L, 'nomi_propri.txt'), encoding='utf-8').read().split(), sez)
    st = yaml.safe_load(open(os.path.join(L, 'stato.yaml'), encoding='utf-8'))
    esito('adotta.py', 'stato: fase / gate / ultimo capitolo scritto', A['stato_parziale'],
          f'{st["fase"]} / {st["gate_in_attesa"] or "nessuno"} / {st["ultimo_capitolo_scritto"]}', sez)
    foto1 = recinto.foto(L)
    p = esegui(os.path.join(S, 'adotta.py'), L)
    esito('adotta.py', 'seconda esecuzione: niente sovrascritto', A['seconda'],
          f'{p.returncode} / {p.stdout.count("già presente, non toccato")} / {recinto.differenze(foto1, recinto.foto(L))}', sez)
    # documenti completi: briefing con autore e piano parole
    L2 = shutil.copytree(fx, os.path.join(tempfile.mkdtemp(dir=TMP), 'adozione'))
    os.makedirs(os.path.join(L2, '00-progetto'))
    open(os.path.join(L2, '00-progetto', 'briefing.md'), 'w', encoding='utf-8').write(
        '# Briefing\n\nTitolo di lavoro: Il faro spento\nAutore: Autrice Inventata\nGenere: narrativa-letteraria\nLunghezza: 60000\n')
    open(os.path.join(L2, '03-architettura', 'piano-parole.md'), 'w', encoding='utf-8').write(
        ''.join(f'| — | {i} | x | | | 20000 | | | |\n' for i in (1, 2, 3)) + '\nTotale: 60000.\n')
    p = esegui(os.path.join(S, 'adotta.py'), L2)
    st = yaml.safe_load(open(os.path.join(L2, 'stato.yaml'), encoding='utf-8'))
    esito('adotta.py', 'documenti completi: valido, gate «documenti» aperto', A['completo'],
          f'{"libro.yaml valido: sì" in p.stdout} / {st["gate_in_attesa"]}', sez)
    esito('adotta.py', 'autore: fonte nel briefing', A['fonte_autore'],
          next((r.split('|')[3].strip() for r in open(os.path.join(L2, '06-diagnostica', 'adozione.md'), encoding='utf-8')
                if r.startswith('| autore |')), 'assente'), sez)
    # riscrittura: 01-originale presente
    L3 = shutil.copytree(fx, os.path.join(tempfile.mkdtemp(dir=TMP), 'adozione'))
    os.makedirs(os.path.join(L3, '01-originale'))
    open(os.path.join(L3, '01-originale', 'vecchio-testo.md'), 'w', encoding='utf-8').write('# Testo precedente\n\nUna riga.\n')
    esegui(os.path.join(S, 'adotta.py'), L3)
    lb = yaml.safe_load(open(os.path.join(L3, 'libro.yaml'), encoding='utf-8'))
    esito('adotta.py', 'con 01-originale: modalità e testo precedente', A['riscrittura'],
          f'{lb["modalita"]} {lb.get("testo_precedente")}', sez)
    vuota = tempfile.mkdtemp(dir=TMP)
    p = esegui(os.path.join(S, 'adotta.py'), vuota)
    esito('adotta.py', 'cartella senza documenti: fermo, niente scritto', A['vuota'], f'{p.returncode} / {os.listdir(vuota)}', sez)


# ---------------------------------------------------------------- passo 6

def passo_6(A):
    import recinto
    sez = 'passo 6'
    E = {k: v for k, v in ENV.items() if k not in ('CLAUDE_PROJECT_DIR', 'ZB_SESSIONE')}
    briefing = open(os.path.join(M, 'prove', 'briefing', 'briefing-giallo.md'), encoding='utf-8').read()

    def nuovo_in(testo, prepara=None):
        d = tempfile.mkdtemp(dir=TMP)
        L = os.path.join(d, 'libro')
        os.makedirs(L)
        if prepara:
            prepara(L)
        open(os.path.join(L, 'briefing.md'), 'w', encoding='utf-8').write(testo)
        return L, subprocess.run([sys.executable, '-B', os.path.join(S, 'nuovo.py'), os.path.join(L, 'briefing.md')],
                                 env=E, capture_output=True, text=True)

    def cartelle(L):
        return sorted(x for x in os.listdir(L) if os.path.isdir(os.path.join(L, x)))

    a = A['struttura']
    s = comune.struttura()
    esito('struttura-libro.yaml', 'cartelle descritte (scopo, modalità, creazione)', a['cartelle'],
          [k for k, v in s['cartelle'].items() if {'scopo', 'modalita', 'creazione'} <= set(v)], sez)
    L, p = nuovo_in(briefing)
    esito('nuovo.py', 'modalità nuovo: cartelle create', a['nuovo'], cartelle(L), sez)
    esito('nuovo.py', 'nessuna cartella vuota, nessun .gitkeep, nessuna cartella fuori struttura', [],
          comune.controlla_struttura(L, 'nuovo'), sez)

    def originale(Lx):
        os.makedirs(os.path.join(Lx, '01-originale'))
        open(os.path.join(Lx, '01-originale', 'testo.md'), 'w', encoding='utf-8').write('# Testo\n\nUna riga.\n')
    ris = briefing.replace('Modalità: nuovo', 'Modalità: riscrittura')
    L, p = nuovo_in(ris.replace('Testo precedente:\n', 'Testo precedente: 01-originale/testo.md\n'), originale)
    esito('nuovo.py', 'modalità riscrittura: cartelle create', a['riscrittura'], f'{p.returncode} / {cartelle(L)}', sez)
    L, p = nuovo_in(briefing, originale)
    esito('nuovo.py', 'modalità nuovo con 01-originale: rifiutato', a['nuovo_con_originale'],
          f'{p.returncode} / {"solo in riscrittura" in p.stderr} / {"libro.yaml" in os.listdir(L)}', sez)

    def altrove(Lx):
        os.makedirs(os.path.join(Lx, '00-progetto'))
        open(os.path.join(Lx, '00-progetto', 'testo.md'), 'w', encoding='utf-8').write('x\n')
    L, p = nuovo_in(ris.replace('Testo precedente:\n', 'Testo precedente: 00-progetto/testo.md\n'), altrove)
    esito('nuovo.py', 'testo precedente fuori da 01-originale: rifiutato', a['testo_altrove'],
          f'{p.returncode} / {"01-originale" in p.stderr}', sez)

    # pulizia
    a = A['pulizia']
    L = copia_libro('mini-libro')
    for d in ('__pycache__', '_build', '.zb', '05-output/vuota', '05-revisioni'):
        os.makedirs(os.path.join(L, d), exist_ok=True)
    for rel, dati in (('__pycache__/a.pyc', b'x'), ('_build/b.html', b'y'), ('.zb/letto-vecchia', b'm'),
                      ('.zb/letto-sessione-prova', b'm'), ('05-output/libro.pdf', b'PDFDATA'),
                      ('05-output/libro-copia.pdf', b'PDFDATA'), ('05-output/libro-bozza.pdf', b'BOZZA')):
        open(os.path.join(L, rel), 'wb').write(dati)
    shutil.copyfile(os.path.join(L, '04-manoscritto', '01-la-farmacia.md'), os.path.join(L, '05-revisioni', '01-copia.md'))
    shutil.copyfile(os.path.join(L, '04-manoscritto', '02-l-officina.md'), os.path.join(L, '04-manoscritto', '02-l-officina.md.tmp'))
    env = dict(E, ZB_SESSIONE='sessione-prova')
    prima = recinto.foto(L)
    vuote_prima = sorted(r for r, ds, fs in os.walk(L) if not ds and not fs)
    p = subprocess.run([sys.executable, '-B', os.path.join(S, 'pulizia.py'), L], env=env, capture_output=True, text=True)
    elenco = [r[2:].split(' — ')[0] for r in p.stdout.splitlines() if r.startswith('- ')]
    esito('pulizia.py', 'elenco (dry-run)', a['elenco'], elenco, sez)
    esito('pulizia.py', 'dry-run: niente cancellato', a['dry_run'],
          f'{p.returncode} / {recinto.differenze(prima, recinto.foto(L))} / '
          f'{sorted(r for r, ds, fs in os.walk(L) if not ds and not fs) == vuote_prima}', sez)
    esito('pulizia.py', 'peso dichiarato', 'sì', 'sì' if re.search(r'elementi, [\d.]+ (B|KB|MB)', p.stdout) else 'no', sez)
    man = {r: v for r, v in prima.items() if r.startswith('04-manoscritto/')}
    p = subprocess.run([sys.executable, '-B', os.path.join(S, 'pulizia.py'), L, '--applica'], env=env, capture_output=True, text=True)
    dopo = recinto.foto(L)
    esito('pulizia.py', '--applica: tolti esattamente gli elementi elencati', a['applica'],
          sorted(r for r in prima if r not in dopo) + sorted(e for e in elenco if e.endswith('/') and not os.path.exists(os.path.join(L, e))), sez)
    esito('pulizia.py', '--applica: manoscritto, libro.yaml e marker corrente intatti', a['protetti'],
          f'{all(dopo.get(r) == v for r, v in man.items())} / {"libro.yaml" in dopo} / {".zb/letto-sessione-prova" in dopo}', sez)
    p = subprocess.run([sys.executable, '-B', os.path.join(S, 'pulizia.py'), L], env=env, capture_output=True, text=True)
    esito('pulizia.py', 'dopo --applica: niente da pulire', a['dopo'], p.stdout.count('\n- '), sez)


# ---------------------------------------------------------------- passo 7

def passo_7(A):
    sez = 'passo 7'
    E = {k: v for k, v in ENV.items() if k != 'ZB_LANGUAGETOOL'}

    def orto(L, env=E):
        return subprocess.run([sys.executable, '-B', os.path.join(S, 'ortografia.py'), L, '--schermo'],
                              env=env, capture_output=True, text=True)

    def tabella_a(out):
        sez_a = out.split('## (a)')[1].split('## ')[0] if '## (a)' in out else ''
        return [r.split('|')[1].strip() for r in sez_a.splitlines() if r.startswith('| ') and not r.startswith('| Parola')]

    gen = [r.strip() for r in open(os.path.join(M, 'dati', 'parole-ammesse-it.txt'), encoding='utf-8')
           if r.strip() and not r.startswith('#')]
    nomi = []
    for nome in ('mini-libro', 'mini-libro-romance', 'mini-libro-adozione'):
        p = os.path.join(M, 'prove', nome, 'nomi_propri.txt')
        if os.path.isfile(p):
            nomi += [x.strip() for x in open(p, encoding='utf-8') if x.strip()]
    esito('parole-ammesse-it.txt', 'nessun nome di personaggio o luogo (mini-libri)', [], [x for x in gen if x in nomi], sez)
    for nome, att in A['base'].items():
        p = orto(copia_libro(nome))
        esito('ortografia.py', f'{nome}: parole non riconosciute', att, tabella_a(p.stdout), sez)
    L = copia_libro('mini-libro')
    with open(os.path.join(L, '04-manoscritto', '01-la-farmacia.md'), 'a', encoding='utf-8') as f:
        f.write('\n' + A['refusi']['riga'] + '\n')
    p = orto(L)
    esito('ortografia.py', 'refusi inventati: parole segnalate', A['refusi']['segnalate'], tabella_a(p.stdout), sez)
    esito('ortografia.py', "refusi inventati: codice d'uscita", A['refusi']['codice'], p.returncode, sez)
    esito('ortografia.py', 'livelli nel report (Hunspell / LanguageTool / checklist)', A['livelli_senza_lt'],
          ' / '.join(re.findall(r'^\| \([abc]\) [^|]+\| (sì|no) \|', p.stdout, re.M)), sez)
    esito('ortografia.py', 'checklist con la nota su «e»/«è» e accordi', 'sì',
          'sì' if '«e» al posto di «è»' in p.stdout and 'accordi' in p.stdout else 'no', sez)
    open(os.path.join(L, 'nomi_propri.txt'), 'w', encoding='utf-8').write('')
    esito('ortografia.py', 'senza parole ammesse del libro: compaiono i nomi propri', 'sì',
          'sì' if len(tabella_a(orto(L).stdout)) > len(A['refusi']['segnalate']) else 'no', sez)
    r = subprocess.run([sys.executable, '-B', os.path.join(S, 'ortografia.py'), L], env=E, capture_output=True, text=True)
    esito('ortografia.py', 'report scritto in 06-diagnostica', 'sì',
          'sì' if os.path.isfile(os.path.join(L, '06-diagnostica', 'controllo-ortografico.md')) else 'no', sez)
    lt = os.environ.get('ZB_LANGUAGETOOL')
    if not lt:
        motivo = 'LanguageTool assente (ZB_LANGUAGETOOL non impostata)'
        saltata('ortografia.py', 'LanguageTool sui refusi inventati', motivo, sez)
        saltata('ortografia.py', 'LanguageTool: livello eseguito nel report', motivo, sez)
        return
    L = copia_libro('mini-libro')
    with open(os.path.join(L, '04-manoscritto', '01-la-farmacia.md'), 'a', encoding='utf-8') as f:
        f.write('\n' + A['refusi']['riga'] + '\n')
    p = orto(L, dict(E, ZB_LANGUAGETOOL=lt))
    sez_b = p.stdout.split('## (b)')[1].split('## ')[0] if '## (b)' in p.stdout else ''
    esito('ortografia.py', 'LanguageTool sui refusi inventati', A['languagetool']['segnalate'],
          sorted({r.split('|')[3].strip() for r in sez_b.splitlines() if r.startswith('| 04-')}), sez)
    esito('ortografia.py', 'LanguageTool: livello eseguito nel report', A['languagetool']['livelli'],
          ' / '.join(re.findall(r'^\| \([abc]\) [^|]+\| (sì|no) \|', p.stdout, re.M)), sez)


# ---------------------------------------------------------------- override motivati sulla lunghezza

def override_lunghezza(A):
    sez = 'override'
    E = {k: v for k, v in ENV.items() if k != 'CLAUDE_PROJECT_DIR'}
    base = open(os.path.join(M, 'prove', 'briefing', 'briefing-giallo.md'), encoding='utf-8').read()

    def prova(sostituzione):
        d = tempfile.mkdtemp(dir=TMP)
        L = os.path.join(d, 'libro')
        os.makedirs(L)
        open(os.path.join(L, 'briefing.md'), 'w', encoding='utf-8').write(base.replace('Lunghezza: 60000', sostituzione))
        p = subprocess.run([sys.executable, '-B', os.path.join(S, 'nuovo.py'), os.path.join(L, 'briefing.md')],
                           env=E, capture_output=True, text=True)
        return L, p

    def campi(p):
        return [r[2:].split(':')[0] for r in p.stderr.splitlines() if r.startswith('- ')]

    for chiave, testo in A['casi'].items():
        att = A['attesi'][chiave]
        L, p = prova(testo)
        if p.returncode != 0:
            esito('nuovo.py', f'{chiave}: rifiutato, campi elencati', att,
                  f'{p.returncode} / {campi(p)} / {"libro.yaml" in os.listdir(L)}', sez)
            continue
        lb = yaml.safe_load(open(os.path.join(L, 'libro.yaml'), encoding='utf-8'))
        esito('nuovo.py', f'{chiave}: accettato', att['codice'], p.returncode, sez)
        esito('nuovo.py', f'{chiave}: override in libro.yaml (campo, valore, motivo presente)', att['override'],
              [f'{o["campo"]} {o["valore"]} {bool(o["motivo"])}' for o in lb['override']], sez)
        esito('nuovo.py', f'{chiave}: capitoli ricalcolati', att['capitoli'],
              len(re.findall(r'(?m)^\| — \| \d+ \|', open(os.path.join(L, '03-architettura', 'piano-parole.md'), encoding='utf-8').read())), sez)
        esito('nuovo.py', f'{chiave}: override elencati nel manuale', att['manuale'],
              open(os.path.join(L, '03-architettura', 'manuale-di-stile.md'), encoding='utf-8').read().count('— motivo:'), sez)


# ---------------------------------------------------------------- controllo delle scene e campi informativi

def scene(A):
    import valida_profili
    sez = 'scene'

    def cap(L, n):
        p = esegui(os.path.join(S, 'capitolo.py'), L, n, '--schermo')
        righe = [r for r in p.stdout.splitlines() if re.match(r'^\| \S+ \| (scene_numero|scena_minimo|scena_massimo) \|', r)]
        return p.returncode, [f'{r.split("|")[2].strip()}|{r.split("|")[3].strip()}' for r in righe]

    def con_override(nome, override):
        L = copia_libro(nome)
        pl = os.path.join(L, 'libro.yaml')
        t = open(pl, encoding='utf-8').read()
        open(pl, 'w', encoding='utf-8').write(t.replace('override: []', 'override: ' + json.dumps(override, ensure_ascii=False)))
        return L

    import json
    for chiave, (nome, n, override) in {
            'romance_1_senza_override': ('mini-libro-romance', '1', None),
            'romance_1_con_override': ('mini-libro-romance', '1', [{'campo': 'capitoli.scene_per_capitolo', 'valore': [1, 3],
                                                                     'motivo': 'prova: capitoli brevi'}]),
            'giallo_3_sotto_minimo': ('mini-libro', '3', None),
            'giallo_1_sopra_massimo': ('mini-libro', '1', [{'campo': 'scene.lunghezza', 'valore': [300, 1000],
                                                             'motivo': 'prova: scene brevi'}])}.items():
        L = con_override(nome, override) if override else copia_libro(nome)
        codice, righe = cap(L, n)
        esito('capitolo.py', f'scene: {chiave}', A[chiave], f'{codice} / {righe}', sez)
    L = con_override('mini-libro-romance', [{'campo': 'capitoli.scene_per_capitolo', 'valore': [1, 3], 'motivo': ''}])
    p = esegui(os.path.join(S, 'capitolo.py'), L, '1', '--schermo')
    esito('capitolo.py', 'scene: override senza motivo rifiutato', A['override_senza_motivo'],
          f'{p.returncode} / {"senza motivo" in p.stderr}', sez)

    # briefing: «Scene:»
    E = {k: v for k, v in ENV.items() if k != 'CLAUDE_PROJECT_DIR'}
    base = open(os.path.join(M, 'prove', 'briefing', 'briefing-giallo.md'), encoding='utf-8').read().replace(
        'Genere: giallo', 'Genere: romance')
    for chiave, testo in A['briefing']['casi'].items():
        d = tempfile.mkdtemp(dir=TMP)
        Lb = os.path.join(d, 'libro')
        os.makedirs(Lb)
        open(os.path.join(Lb, 'briefing.md'), 'w', encoding='utf-8').write(base.replace('Lunghezza: 60000', testo))
        p = subprocess.run([sys.executable, '-B', os.path.join(S, 'nuovo.py'), os.path.join(Lb, 'briefing.md')],
                           env=E, capture_output=True, text=True)
        if p.returncode:
            ott = f'{p.returncode} / {[r[2:].split(":")[0] for r in p.stderr.splitlines() if r.startswith("- ")]}'
        else:
            lb = yaml.safe_load(open(os.path.join(Lb, 'libro.yaml'), encoding='utf-8'))
            ott = f'0 / {[(o["campo"], o["valore"]) for o in lb["override"] if o["campo"].startswith(("scene", "capitoli.scene"))]}'
        esito('nuovo.py', f'briefing «Scene:»: {chiave}', A['briefing']['attesi'][chiave], ott, sez)

    # campi informativi
    u = valida_profili.usi()
    esito('valida_profili.py', 'campi informativi (dallo schema)', A['informativi'], sorted(k for k, v in u.items() if v == 'informativo'), sez)
    esito('valida_profili.py', 'campi controllati (dallo schema)', A['controllati'], sorted(k for k, v in u.items() if v == 'controllo'), sez)
    p = esegui(os.path.join(S, 'valida_profili.py'))
    esito('valida_profili.py', 'elenco per uso a schermo', 'sì',
          'sì' if all(x in p.stdout for x in ('Campi controllati:', 'Informativi, non controllati:', 'Usati da nuovo.py')) else 'no', sez)
    foglie = [k.split('.')[-1] for k, v in u.items() if v == 'informativo']
    manca = []
    for pr in sorted(glob_profili()):
        for r in open(pr, encoding='utf-8'):
            m = re.match(r'^\s*([a-z_]+):', r)
            if m and m.group(1) in foglie and 'informativo, non controllato' not in r:
                manca.append(f'{os.path.basename(pr)}:{m.group(1)}')
    esito('profili/*.yaml', 'campi informativi marcati nei sette profili', [], manca, sez)


def glob_profili():
    import glob
    return glob.glob(os.path.join(M, 'profili', '*.yaml'))


# ---------------------------------------------------------------- manuale generato leggibile

def manuale_leggibile(A):
    import nuovo
    sez = 'manuale'
    E = {k: v for k, v in ENV.items() if k != 'CLAUDE_PROJECT_DIR'}
    base = open(os.path.join(M, 'prove', 'briefing', 'briefing-giallo.md'), encoding='utf-8').read()
    manuali, libri = [], []
    for testo in (base, base.replace('Lunghezza: 60000', 'Lunghezza: 9000\nMotivo override: prova\nCapitoli: 800 | 1000-1300 | 1800'),
                  base.replace('Ugo Pelle | vietato prima del 2', 'Ugo Pelle | vietato prima del 4')):
        d = tempfile.mkdtemp(dir=TMP)
        L = os.path.join(d, 'libro')
        os.makedirs(L)
        open(os.path.join(L, 'briefing.md'), 'w', encoding='utf-8').write(testo)
        subprocess.run([sys.executable, '-B', os.path.join(S, 'nuovo.py'), os.path.join(L, 'briefing.md')], env=E, capture_output=True)
        manuali.append(open(os.path.join(L, '03-architettura', 'manuale-di-stile.md'), encoding='utf-8').read())
        libri.append(yaml.safe_load(open(os.path.join(L, 'libro.yaml'), encoding='utf-8')))
    tutto = '\n'.join(manuali)
    esito('nuovo.py', 'manuale: identificativi con trattino basso tra «»', A['identificativi'],
          sorted(set(re.findall(r'«([^»]*_[^»]*)»', tutto))), sez)
    esito('nuovo.py', 'manuale: «nei capitolo» o «nei capitoli N.» (un solo capitolo)', A['grammatica_errata'],
          re.findall(r'nei capitolo\b|nei capitoli \d+\.', tutto), sez)
    esito('nuovo.py', 'manuale: vincolo su un solo capitolo', A['vincolo'],
          next((r for r in manuali[0].splitlines() if 'non compare' in r), ''), sez)
    esito('nuovo.py', 'manuale: vincolo su un intervallo', 'nei capitoli 1-3',
          'nei capitoli 1-3' if 'non compare nei capitoli 1-3.' in manuali[2] else 'no', sez)
    esito('nuovo.py', 'manuale: tetti e vietati con le espressioni', A['tetti'],
          [r for r in manuali[0].splitlines() if r.startswith(('- Tetto:', '- Vietato:'))], sez)
    esito('nuovo.py', 'dove_capitoli', A['dove_capitoli'],
          [nuovo.dove_capitoli(x) for x in (['1'], ['1-3'], ['1', '4', '6-8'], [])], sez)
    esito('nuovo.py', 'lunghezza fuori profilo: parole.motivo_fuori_profilo (fuori profilo / dentro)', A['motivo_fuori_profilo'],
          f'{"sì" if libri[1]["parole"].get("motivo_fuori_profilo") else "no"} / '
          f'{"sì" if libri[0]["parole"].get("motivo_fuori_profilo") else "no"}', sez)


# ---------------------------------------------------------------- checklist di capitolo dal libro

def checklist_capitolo(A):
    sez = 'checklist'
    L = copia_libro('mini-libro')
    p = esegui(os.path.join(S, 'capitolo.py'), L, '1', '--schermo')
    base = [r for r in p.stdout.splitlines() if r.endswith('| [ ] |')]
    pl = os.path.join(L, 'libro.yaml')
    with open(pl, 'a', encoding='utf-8') as f:
        f.write('checklist_capitolo: ' + json.dumps(A['voci'], ensure_ascii=False) + '\n')
    p = esegui(os.path.join(S, 'capitolo.py'), L, '1', '--schermo')
    righe = [r for r in p.stdout.splitlines() if r.endswith('| [ ] |')]
    esito('capitolo.py', 'voci del libro in fondo alla checklist', A['righe'], righe[len(base):], sez)
    esito('capitolo.py', 'checklist fissa invariata', 'sì', 'sì' if righe[:len(base)] == base else 'no', sez)
    t = open(pl, encoding='utf-8').read().replace('checklist_capitolo: ', 'checklist_capitolo: 5 #')
    open(pl, 'w', encoding='utf-8').write(t)
    p = esegui(os.path.join(S, 'capitolo.py'), L, '1', '--schermo')
    esito('capitolo.py', 'checklist_capitolo non valida: rifiutata', A['non_valida'], p.returncode, sez)


# ---------------------------------------------------------------- età e durate in continuita.py

def continuita_eta_durate(A):
    import continuita
    sez = 'continuita'

    def esiti(L, controllo):
        _, libro, _ = comune.carica_libro(L)
        ris = continuita.controlla_libro(L, libro)[0]
        return [f'{r["controllo"]}|{r["esito"]}' for r in ris if r['unita'] == '1' and r['controllo'] == controllo]

    for chiave, frase in A['frasi'].items():
        L = copia_libro('mini-libro')
        cap = os.path.join(L, '04-manoscritto', '01-la-farmacia.md')
        base = esiti(L, 'eta')
        open(cap, 'a', encoding='utf-8').write('\n' + frase + '\n')
        esito('continuita.py', f'età: {chiave}', A['attesi'][chiave], esiti(L, 'eta')[len(base):], sez)
    for chiave, du in A['durate'].items():
        L = copia_libro('mini-libro')
        pc = os.path.join(L, 'cronologia.yaml')
        cron = yaml.safe_load(open(pc, encoding='utf-8'))
        import datetime
        cron['eventi'] += [{'id': 'a', 'data': datetime.date(2021, 1, 1), 'capitolo': 1, 'descrizione': 'prova'},
                           {'id': 'b', 'data': datetime.date(2021, 2, 11), 'capitolo': 1, 'descrizione': 'prova'},
                           {'id': 'c', 'data': datetime.date(2021, 3, 12), 'capitolo': 1, 'descrizione': 'prova'}]
        voce = {k: v for k, v in du.items() if k != 'atteso'}
        cron['durate'] = [voce]
        open(pc, 'w', encoding='utf-8').write(yaml.safe_dump(cron, allow_unicode=True))
        open(os.path.join(L, '04-manoscritto', '01-la-farmacia.md'), 'a', encoding='utf-8').write(
            f'\nIn tutto erano passate {du["valore"]} da quel giorno.\n')
        esito('continuita.py', f'durata: {chiave}', du['atteso'], esiti(L, 'durata'), sez)


# ---------------------------------------------------------------- correzioni dopo la prova romance

def correzioni_dopo_prova(A):
    import datetime
    import conta
    import continuita
    import fase
    import nuovo
    import stile
    sez = 'correzioni'
    E = {k: v for k, v in ENV.items() if k not in ('CLAUDE_PROJECT_DIR', 'ZB_LIBRO', 'ZB_RAMO', 'ZB_SESSIONE')}
    E.update(GIT_AUTHOR_NAME='Prova', GIT_AUTHOR_EMAIL='prova@esempio.invalid',
             GIT_COMMITTER_NAME='Prova', GIT_COMMITTER_EMAIL='prova@esempio.invalid')

    def zb(cwd, *a):
        return subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), *a], cwd=cwd, env=E, capture_output=True, text=True)

    def git(cwd, *a):
        return subprocess.run(['git', *a], cwd=cwd, env=E, capture_output=True, text=True)

    def salva(r):
        git(r, 'add', '-A')
        git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'prova')
        git(r, 'push', '-q', '-u', 'origin', 'prova')

    def repo():
        d = tempfile.mkdtemp(dir=TMP)
        git(d, 'init', '-q', '--bare', 'remoto.git')
        r = os.path.join(d, 'repo')
        os.makedirs(r)
        git(r, 'init', '-q')
        git(r, 'checkout', '-q', '-b', 'prova')
        git(r, 'remote', 'add', 'origin', os.path.join(d, 'remoto.git'))
        return r

    def stato(L):
        return comune.leggi_yaml(os.path.join(L, 'stato.yaml'))

    def tutto_e_ok(r, nome):
        for _ in range(40):
            if 'Fine dei documenti' in zb(r, 'avanti', nome).stdout:
                break
        return zb(r, 'ok', nome)

    # (c) pagina campione: 05-revisioni/ creata all'ingresso nella fase; pronto rifiuta la pagina vuota
    briefing = open(os.path.join(M, 'prove', 'briefing', 'briefing-giallo.md'), encoding='utf-8').read()
    r = repo()
    L = os.path.join(r, 'giallo')
    os.makedirs(L)
    open(os.path.join(L, 'briefing.md'), 'w', encoding='utf-8').write(briefing)
    zb(r, 'nuovo', 'giallo/briefing.md')
    salva(r)
    zb(r, 'pronto', 'giallo')
    salva(r)
    tutto_e_ok(r, 'giallo')
    pc = os.path.join(L, '05-revisioni', 'pagina-campione.md')
    esito('fase.py', '(c) pagina campione creata, struttura conforme', A['c_creata'],
          f'{os.path.isfile(pc)} / {comune.controlla_struttura(L, "nuovo")}', sez)
    salva(r)
    p = zb(r, 'pronto', 'giallo')
    esito('fase.py', '(c) pronto con la pagina vuota: rifiutato', A['c_vuota'],
          f'{p.returncode} / {stato(L)["gate_in_attesa"] or "nessuno"}', sez)
    open(pc, 'a', encoding='utf-8').write('\nTesto di prova della pagina.\n')
    salva(r)
    zb(r, 'pronto', 'giallo')
    esito('fase.py', '(c) pronto con la pagina scritta: gate', A['c_scritta'], stato(L)['gate_in_attesa'], sez)

    # (g) riapprova: modifica autorizzata a un documento già approvato
    doc = '02-bibbia/bibbia.md'
    salva(r)
    open(os.path.join(L, doc), 'a', encoding='utf-8').write('- modifica autorizzata\n')
    salva(r)
    p1 = zb(r, 'avvio', 'giallo')
    p2 = zb(r, 'riapprova', 'giallo', doc)
    p3 = zb(r, 'riapprova', 'giallo', '03-architettura/manuale-di-stile.md', 'nessun', 'cambiamento')
    p4 = zb(r, 'riapprova', 'giallo', doc, 'tolleranza', 'cambiata', 'su', 'richiesta')
    salva(r)
    p5 = zb(r, 'avvio', 'giallo')
    v = stato(L)['documenti_approvati'][doc]
    esito('fase.py', '(g) avvio fermo / senza motivo / invariato / riapprova / avvio', A['g_codici'],
          [p.returncode for p in (p1, p2, p3, p4, p5)], sez)
    esito('fase.py', '(g) registro della riapprovazione', A['g_registro'],
          f'{[x["motivo"] for x in v.get("riapprovazioni") or []]} / '
          f'{v["sha256"] == comune.sha256_file(os.path.join(L, doc))}', sez)

    # (d) manuale: sigle di chiusura spiegate
    righe = []
    for genere in ('giallo', 'romance'):
        d = tempfile.mkdtemp(dir=TMP)
        Lb = os.path.join(d, 'libro')
        os.makedirs(Lb)
        open(os.path.join(Lb, 'briefing.md'), 'w', encoding='utf-8').write(briefing.replace('Genere: giallo', f'Genere: {genere}'))
        subprocess.run([sys.executable, '-B', os.path.join(S, 'nuovo.py'), os.path.join(Lb, 'briefing.md')], env=E, capture_output=True)
        righe += [x for x in open(os.path.join(Lb, '03-architettura', 'manuale-di-stile.md'), encoding='utf-8').read().splitlines()
                  if x.startswith('- Chiusura preferita:')]
    esito('nuovo.py', '(d) manuale: riga delle sigle (giallo, romance)', A['d_righe'], righe, sez)
    esito('nuovo.py', '(d) sigle senza significato nei tre tipi di chiusura', [],
          [s for v in nuovo.SIGLE.values() for s in v if s not in nuovo.SIGNIFICATO_SIGLE], sez)

    # (i) e (b) similitudini
    esito('stile.py', '(i) candidati per frase', A['i_attesi'],
          [len(stile.occorrenze([(1, f)], stile.SIMILITUDINE.pattern)) for f in A['i_frasi']], sez)
    esito('stile.py', '(b) limite noto: «come si…», «come quando…» non contati', A['b_attesi'],
          [len(stile.occorrenze([(1, f)], stile.SIMILITUDINE.pattern)) for f in A['b_frasi']], sez)

    # (h) cifre con e senza contesto; (a) durate della cronologia senza testo
    def cifre(contesto, frase):
        Lm = copia_libro('mini-libro')
        pc_ = os.path.join(Lm, 'cronologia.yaml')
        cron = yaml.safe_load(open(pc_, encoding='utf-8'))
        if contesto:
            cron['cifre'][0]['contesto'] = contesto
        open(pc_, 'w', encoding='utf-8').write(yaml.safe_dump(cron, allow_unicode=True))
        open(os.path.join(Lm, '04-manoscritto', '01-la-farmacia.md'), 'a', encoding='utf-8').write('\n' + frase + '\n')
        _, libro, _ = comune.carica_libro(Lm)
        return [f'{x["controllo"]}|{x["esito"]}' for x in continuita.controlla_libro(Lm, libro)[0]
                if x['controllo'].startswith('cifra')]
    for chiave, (contesto, frase) in A['h_casi'].items():
        esito('continuita.py', f'(h) cifre: {chiave}', A['h_attesi'][chiave], cifre(contesto, frase), sez)
    for chiave, giorni in A['a_casi'].items():
        Lm = copia_libro('mini-libro')
        pc_ = os.path.join(Lm, 'cronologia.yaml')
        cron = yaml.safe_load(open(pc_, encoding='utf-8'))
        cron['eventi'] += [{'id': 'a', 'data': datetime.date(2021, 1, 1), 'capitolo': 1, 'descrizione': 'prova'},
                           {'id': 'b', 'data': datetime.date(2021, 1, 1) + datetime.timedelta(days=giorni), 'capitolo': 1,
                            'descrizione': 'prova'}]
        cron['durate'] = [{'da': 'a', 'a': 'b', 'valore': 'sei settimane', 'tolleranza_giorni': 3}]
        open(pc_, 'w', encoding='utf-8').write(yaml.safe_dump(cron, allow_unicode=True))
        _, libro, _ = comune.carica_libro(Lm)
        esito('continuita.py', f'(a) durata solo in cronologia: {chiave}', A['a_attesi'][chiave],
              [f'{x["unita"]}|{x["controllo"]}|{x["esito"]}' for x in continuita.controlla_libro(Lm, libro)[0]
               if x['controllo'] == 'durata'], sez)

    # (j) ordine di chiusura
    proc = open(os.path.join(M, 'PROCEDURA.md'), encoding='utf-8').read()
    esito('fase.py', '(j) ordine di chiusura (fase.py)', A['j_ordine'], [c for _, c in fase.CHIUSURA], sez)
    esito('PROCEDURA.md', '(j) zb pacchetto prima di zb kdp (sezione 7)', 'sì',
          'sì' if '`zb pdf`, `zb pacchetto`, `zb kdp`; poi `zb pronto' in proc else 'no', sez)

    # (k) esito a un gate di capitoli dopo una correzione registrata
    r = repo()
    Lm = shutil.copytree(os.path.join(M, 'prove', 'mini-libro'), os.path.join(r, 'mini'))
    s = comune.leggi_yaml(os.path.join(M, 'modelli', 'stato.yaml'))
    s.update(libro='Prova di stampa', fase='stesura', passo='capitolo 4', aggiornato='prova', gate_in_attesa='primi_capitoli',
             ultimo_capitolo_scritto=3)
    s['lotto']['capitoli'] = [1, 2, 'interludio I', 3]
    open(os.path.join(Lm, 'stato.yaml'), 'w', encoding='utf-8').write(yaml.safe_dump(s, sort_keys=False, allow_unicode=True))
    for u in ('1', '2', 'interludio I', '3'):
        esegui(os.path.join(S, 'capitolo.py'), Lm, *u.split())       # report dei capitoli del gate
    salva(r)
    p1 = zb(r, 'esito', 'mini', '1')
    zb(r, 'correggi', 'mini', 'capitolo 1: una frase più corta')
    p2 = zb(r, 'esito', 'mini', '1')
    s = stato(Lm)
    esito('fase.py', '(k) esito al gate: senza correzione / con correzione / gate / parole', A['k_esito'],
          f'{p1.returncode} / {p2.returncode} / {s["gate_in_attesa"]} / {s["parole"]["scritte"]}', sez)

    # (l) totale previsto fuori tolleranza: avviso e budget residuo proposto
    Lm = copia_libro('mini-libro')
    caps = {n: p for n, p in comune.unita(Lm, comune.carica_libro(Lm)[1])}
    os.remove(caps['3'])
    pl = os.path.join(Lm, 'libro.yaml')
    tl = re.sub(r'target_totale: \d+', 'target_totale: 4000', open(pl, encoding='utf-8').read())
    open(pl, 'w', encoding='utf-8').write(tl)
    prima = {n: comune.sha256_file(p) for n, p in caps.items() if n != '3'}
    _, libro, prof = comune.carica_libro(Lm)
    esito('conta.py', '(l) totale previsto e avviso (capitolo 3 non scritto, obiettivo 4000)', A['l_avviso'],
          conta.totale_previsto(Lm, libro, prof)[3], sez)
    p = esegui(os.path.join(S, 'conta.py'), Lm, '--schermo')
    q = esegui(os.path.join(S, 'capitolo.py'), Lm, '1', '--schermo')
    esito('conta.py / capitolo.py', '(l) avviso a schermo (conta | capitolo 1)', A['l_schermo'],
          f'{"AVVISO: totale previsto" in p.stdout} | {"| parole_totale | AVVISO |" in q.stdout}', sez)
    esito('conta.py / capitolo.py', '(l) capitoli invariati', 'sì',
          'sì' if prima == {n: comune.sha256_file(caps[n]) for n in prima} else 'no', sez)


# ---------------------------------------------------------------- adozione di libri esistenti

def adozione_libri_esistenti(A):
    sez = 'adozione'
    E = {k: v for k, v in ENV.items() if k not in ('CLAUDE_PROJECT_DIR', 'ZB_LIBRO', 'ZB_RAMO', 'ZB_SESSIONE')}
    E.update(GIT_AUTHOR_NAME='Prova', GIT_AUTHOR_EMAIL='prova@esempio.invalid',
             GIT_COMMITTER_NAME='Prova', GIT_COMMITTER_EMAIL='prova@esempio.invalid')

    def zb(cwd, *a):
        return subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), *a], cwd=cwd, env=E, capture_output=True, text=True)

    def git(cwd, *a):
        return subprocess.run(['git', *a], cwd=cwd, env=E, capture_output=True, text=True)

    def libro_adottabile(briefing, manuale=A['manuale']):
        d = tempfile.mkdtemp(dir=TMP)
        git(d, 'init', '-q', '--bare', 'remoto.git')
        r = os.path.join(d, 'repo')
        os.makedirs(r)
        git(r, 'init', '-q')
        git(r, 'checkout', '-q', '-b', 'prova')
        git(r, 'remote', 'add', 'origin', os.path.join(d, 'remoto.git'))
        L = os.path.join(r, 'torre')
        for rel, testo in {'00-progetto/briefing.md': briefing, '01-originale/vecchio-testo.md': A['vecchio'],
                           '02-bibbia/bibbia.md': A['bibbia'], '03-architettura/manuale-di-stile.md': manuale,
                           '03-architettura/scaletta.md': A['scaletta'],
                           '03-architettura/piano-parole.md': A['piano']}.items():
            os.makedirs(os.path.dirname(os.path.join(L, rel)), exist_ok=True)
            open(os.path.join(L, rel), 'w', encoding='utf-8').write(testo)
        return r, L

    def salva(r):
        git(r, 'add', '-A')
        git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'prova')
        git(r, 'push', '-q', '-u', 'origin', 'prova')

    # (c) valori di frase non copiati tra i capitoli; (a) avvio senza briefing nel formato del motore
    r, L = libro_adottabile(A['briefing_libero'])
    p = zb(r, 'adotta', 'torre')
    lb = yaml.safe_load(open(os.path.join(L, 'libro.yaml'), encoding='utf-8'))
    rep = open(os.path.join(L, '06-diagnostica', 'adozione.md'), encoding='utf-8').read()
    fonti_capitoli = re.findall(r'stile\.capitoli\.\w+', rep)
    esito('adotta.py', '(c) override e fonti dei capitoli', A['capitoli'],
          f'{[o["campo"] for o in lb["override"]]} / {fonti_capitoli}', sez)
    open(os.path.join(L, '.gitignore'), 'w', encoding='utf-8').write('.zb/\n')
    salva(r)
    p = zb(r, 'avvio', 'torre')
    esito('avvio.py', '(a) riscrittura senza briefing del motore: avvio non si ferma', A['avvio_libero'],
          f'{p.returncode} / {"Letto: " in p.stdout}', sez)
    r, L = libro_adottabile(A['briefing_motore_incompleto'])
    zb(r, 'adotta', 'torre')
    open(os.path.join(L, '.gitignore'), 'w', encoding='utf-8').write('.zb/\n')
    salva(r)
    p = zb(r, 'avvio', 'torre')
    esito('avvio.py', '(a) briefing nel formato del motore, incompleto: avvio fermo', A['avvio_motore'],
          f'{p.returncode} / {"Briefing incompleto" in p.stderr}', sez)
    # (b) titolo non trovato: rifiuto senza scrivere; con --titolo va avanti
    r, L = libro_adottabile(A['briefing_libero'], A['manuale_senza_titolo'])
    for rel in ('02-bibbia/bibbia.md', '03-architettura/scaletta.md'):
        pr = os.path.join(L, rel)
        resto = open(pr, encoding='utf-8').read().split('\n', 1)[1]
        open(pr, 'w', encoding='utf-8').write(resto)
    prima = sorted(os.listdir(L))
    p = zb(r, 'adotta', 'torre')
    esito('adotta.py', '(b) titolo non trovato: rifiutato, niente scritto, titolo chiesto', A['senza_titolo'],
          f'{p.returncode} / {sorted(os.listdir(L)) == prima} / {"--titolo" in p.stderr}', sez)
    p = zb(r, 'adotta', 'torre', '--titolo', 'La torre di sale')
    st = yaml.safe_load(open(os.path.join(L, 'stato.yaml'), encoding='utf-8'))
    esito('adotta.py', '(b) con --titolo: libro.yaml e stato.yaml', A['con_titolo'],
          f'{p.returncode} / {yaml.safe_load(open(os.path.join(L, "libro.yaml"), encoding="utf-8"))["titolo"]} / {st["libro"]}', sez)


# ---------------------------------------------------------------- correzioni su interludi, impronte e grafie

def correzioni_interludi_e_grafie(A):
    import continuita
    import fase
    import riciclo
    sez = 'interludi e grafie'
    E = {k: v for k, v in ENV.items() if k not in ('CLAUDE_PROJECT_DIR', 'ZB_LIBRO', 'ZB_RAMO', 'ZB_SESSIONE')}
    E.update(GIT_AUTHOR_NAME='Prova', GIT_AUTHOR_EMAIL='prova@esempio.invalid',
             GIT_COMMITTER_NAME='Prova', GIT_COMMITTER_EMAIL='prova@esempio.invalid')

    def git(cwd, *a):
        return subprocess.run(['git', *a], cwd=cwd, env=E, capture_output=True, text=True)

    def repo_stesura():
        d = tempfile.mkdtemp(dir=TMP)
        git(d, 'init', '-q', '--bare', 'remoto.git')
        r = os.path.join(d, 'repo')
        os.makedirs(r)
        git(r, 'init', '-q')
        git(r, 'checkout', '-q', '-b', 'prova')
        git(r, 'remote', 'add', 'origin', os.path.join(d, 'remoto.git'))
        Lm = shutil.copytree(os.path.join(M, 'prove', 'mini-libro'), os.path.join(r, 'mini'))
        s = comune.leggi_yaml(os.path.join(M, 'modelli', 'stato.yaml'))
        s.update(libro='Prova di stampa', fase='stesura', passo='capitolo 1', aggiornato='prova', gate_in_attesa=None)
        open(os.path.join(Lm, 'stato.yaml'), 'w', encoding='utf-8').write(yaml.safe_dump(s, sort_keys=False, allow_unicode=True))
        git(r, 'add', '-A')
        git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'prova')
        git(r, 'push', '-q', '-u', 'origin', 'prova')
        return r, Lm

    # (a) interludio la cui posizione è oltre l'ultimo capitolo scritto: AVVISO, nessun FERMO
    Lm = copia_libro('mini-libro')
    pl = os.path.join(Lm, 'libro.yaml')
    t = open(pl, encoding='utf-8').read().replace(
        '    - {numero: I, dopo_capitolo: 2, titolo: "La vetrina", parte: null}',
        '    - {numero: I, dopo_capitolo: 2, titolo: "La vetrina", parte: null}\n'
        '    - {numero: II, dopo_capitolo: 9, titolo: "La porta", parte: null}')
    open(pl, 'w', encoding='utf-8').write(t)
    open(os.path.join(Lm, '04-manoscritto', 'interludio-II.md'), 'w', encoding='utf-8').write(
        '## *La porta*\n\nLa porta del magazzino resta socchiusa tutta la notte, e il vento la muove piano.\n')
    _, libro, _ = comune.carica_libro(Lm)
    esito('comune.py', '(a) ordine con un interludio in anticipo', A['a_ordine'],
          [n for n, _ in comune.unita(Lm, libro)], sez)
    esito('comune.py', '(a) interludi in anticipo', A['a_anticipo'],
          [f'{n} dopo {d}' for n, d in comune.interludi_in_anticipo(Lm, libro)], sez)
    p = esegui(os.path.join(S, 'capitolo.py'), Lm, 'interludio', 'II', '--schermo')
    q = esegui(os.path.join(S, 'conta.py'), Lm, '--schermo')
    esito('capitolo.py / conta.py', '(a) nessun FERMO; AVVISO «in anticipo»', A['a_comandi'],
          f'{p.returncode in (0, 1)} / {"| posizione | AVVISO |" in p.stdout and "in anticipo" in p.stdout} / '
          f'{q.returncode} / {"FERMO" in p.stderr + q.stderr}', sez)
    open(os.path.join(Lm, '04-manoscritto', 'interludio-III.md'), 'w', encoding='utf-8').write('## *Fuori*\n\nUna riga.\n')
    p = esegui(os.path.join(S, 'conta.py'), Lm, '--schermo')
    esito('conta.py', '(a) interludio assente da struttura.interludi: resta FERMO', A['a_sconosciuto'],
          f'{p.returncode} / {"senza posizione" in p.stderr}', sez)

    # (b) piano parole: misure fuori dall'impronta; zb esito le aggiorna senza riapprova
    r, Lm = repo_stesura()
    pp = os.path.join(Lm, '03-architettura', 'piano-parole.md')
    registrata = comune.impronta_documento(pp)
    testo = open(pp, encoding='utf-8').read()
    misure = testo.replace('| 1200 | 1200 | | |', '| 1200 | 1200 | 999 | -16,8% |')
    open(pp, 'w', encoding='utf-8').write(misure)
    invariata = comune.impronta_documento(pp) == registrata
    open(pp, 'w', encoding='utf-8').write(testo.replace('| 1200 | 1200 | | |', '| 1300 | 1200 | | |'))
    cambiata = comune.impronta_documento(pp) != registrata
    open(pp, 'w', encoding='utf-8').write(testo)
    esito('comune.py', '(b) impronta: misure ignorate / budget contato', A['b_impronta'], f'{invariata} / {cambiata}', sez)
    p = subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), 'esito', 'mini', '1'], cwd=r, env=E,
                       capture_output=True, text=True)
    riga = [x for x in open(pp, encoding='utf-8').read().splitlines() if x.startswith('| — | 1 |')]
    esito('fase.py', '(b) esito aggiorna «Parole reali» e «Scarto»; impronta invariata', A['b_esito'],
          f'{p.returncode} / {riga} / {comune.documento_invariato(pp, registrata)}', sez)

    # (b) sha256 grezzo registrato prima delle impronte: valido anche dopo che esito aggiorna le misure;
    # il «Totale previsto» si aggiorna senza perdere il punto finale
    r, Lm = repo_stesura()
    pp = os.path.join(Lm, '03-architettura', 'piano-parole.md')
    open(pp, 'a', encoding='utf-8').write('\nTotale previsto (prova): 3.150.\n')
    git(r, 'add', '-A')
    git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'piano')
    git(r, 'push', '-q')
    grezzo, commit = comune.sha256_file(pp), git(r, 'log', '-1', '--format=%h').stdout.strip()
    subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), 'esito', 'mini', '1'], cwd=r, env=E, capture_output=True)
    ultima = open(pp, encoding='utf-8').read().strip().splitlines()[-1]
    esito('comune.py / fase.py', '(b) registrazione grezza ancora valida / riga del totale', A['b_grezzo'],
          f'{comune.documento_invariato(pp, grezzo, commit)} / {ultima}', sez)

    # (c) stato.yaml salvato prima di stampare: un'uscita chiusa non perde lo stato
    r, Lm = repo_stesura()
    pr = subprocess.Popen([sys.executable, '-B', os.path.join(M, 'zb'), 'esito', 'mini', '1'], cwd=r, env=E,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pr.stdout.close()
    pr.wait()
    s = comune.leggi_yaml(os.path.join(Lm, 'stato.yaml'))
    esito('fase.py', '(c) esito con l\'uscita chiusa: stato salvato', A['c_stato'],
          f'{s["ultimo_capitolo_scritto"]} / {s["passo"]}', sez)

    # (d) nomi in due grafie: le parole a inizio frase non si confrontano
    Lm = copia_libro('mini-libro')
    open(os.path.join(Lm, '04-manoscritto', '01-la-farmacia.md'), 'a', encoding='utf-8').write(
        '\nCalvo e stanco, il farmacista chiuse la porta. — Calvo, lui? Venne poi il dottor Calvo.\n')
    _, libro, _ = comune.carica_libro(Lm)
    esito('continuita.py', '(d) «Calvo» a inizio frase ignorato, a metà frase segnalato', A['d_grafie'],
          [x['dettaglio'] for x in continuita.controlla_libro(Lm, libro)[0]
           if x['controllo'] == 'nome_due_grafie' and x['unita'] == '1'], sez)

    # (e) battute canoniche escluse dall'anti-riciclo
    Lm = copia_libro('mini-libro')
    vecchio = ('Il vecchio disse che la notte porta sempre consiglio a chi resta sveglio. '
               'Poi aggiunse piano che la pioggia lava le strade ma non le colpe.')
    os.makedirs(os.path.join(Lm, '01-originale'), exist_ok=True)
    open(os.path.join(Lm, '01-originale', 'vecchio.md'), 'w', encoding='utf-8').write(vecchio + '\n')
    open(os.path.join(Lm, '03-architettura', 'manuale-di-stile.md'), 'w', encoding='utf-8').write(
        '# Manuale\n\n- Niente riciclo, tranne le battute canoniche qui sotto.\n'
        '- **Battute canoniche**, con le parole identiche:\n'
        '  - «la notte porta sempre consiglio a chi resta sveglio» (il vecchio);\n\n## 1. Altro\n')
    t = open(os.path.join(Lm, 'libro.yaml'), encoding='utf-8').read()
    t = re.sub(r'(?m)^modalita: .*$', 'modalita: riscrittura\ntesto_precedente: 01-originale/vecchio.md', t)
    open(os.path.join(Lm, 'libro.yaml'), 'w', encoding='utf-8').write(t)
    open(os.path.join(Lm, '04-manoscritto', '01-la-farmacia.md'), 'a', encoding='utf-8').write(
        '\nLa notte porta sempre consiglio a chi resta sveglio, disse Irene. '
        'Sapeva che la pioggia lava le strade ma non le colpe.\n')
    _, libro, _ = comune.carica_libro(Lm)
    esito('riciclo.py', '(e) battute del manuale / KO rimasti', A['e_riciclo'],
          f'{len(riciclo.battute_canoniche(Lm))} / '
          f'{[x["dettaglio"] for x in riciclo.controlla_libro(Lm, libro) if x["controllo"] == "riciclo:testo_precedente"]}',
          sez)

# ---------------------------------------------------------------- correzioni fuori dal gate e passo

def correzioni_e_passo(A):
    sez = 'correggi e passo'
    E = {k: v for k, v in ENV.items() if k not in ('CLAUDE_PROJECT_DIR', 'ZB_LIBRO', 'ZB_RAMO', 'ZB_SESSIONE')}
    E.update(GIT_AUTHOR_NAME='Prova', GIT_AUTHOR_EMAIL='prova@esempio.invalid',
             GIT_COMMITTER_NAME='Prova', GIT_COMMITTER_EMAIL='prova@esempio.invalid')

    def git(cwd, *a):
        return subprocess.run(['git', *a], cwd=cwd, env=E, capture_output=True, text=True)

    def zb(cwd, *a):
        return subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), *a], cwd=cwd, env=E, capture_output=True, text=True)

    def salva(r):
        git(r, 'add', '-A')
        git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'prova')
        git(r, 'push', '-q', '-u', 'origin', 'prova')

    d = tempfile.mkdtemp(dir=TMP)
    git(d, 'init', '-q', '--bare', 'remoto.git')
    r = os.path.join(d, 'repo')
    os.makedirs(r)
    git(r, 'init', '-q')
    git(r, 'checkout', '-q', '-b', 'prova')
    git(r, 'remote', 'add', 'origin', os.path.join(d, 'remoto.git'))
    Lm = shutil.copytree(os.path.join(M, 'prove', 'mini-libro'), os.path.join(r, 'mini'))
    s = comune.leggi_yaml(os.path.join(M, 'modelli', 'stato.yaml'))
    s.update(libro='Prova di stampa', fase='stesura', passo='capitolo 1', aggiornato='prova', gate_in_attesa=None)
    open(os.path.join(Lm, 'stato.yaml'), 'w', encoding='utf-8').write(yaml.safe_dump(s, sort_keys=False, allow_unicode=True))
    salva(r)
    cap = os.path.join(Lm, '04-manoscritto', '01-la-farmacia.md')

    def stato():
        return comune.leggi_yaml(os.path.join(Lm, 'stato.yaml'))

    # (a) fuori dal gate, con il file modificato e non salvato
    salvato = comune.sha256_file(cap)
    open(cap, 'a', encoding='utf-8').write('\nUna riga corretta.\n')
    p1 = zb(r, 'correggi', 'mini', 'capitolo 1: una riga in più')
    v = (stato().get('correzioni_registrate') or [{}])[-1]
    esito('fase.py', '(a) correggi senza gate: registrata, gate invariato', A['a_libera'],
          f'{p1.returncode} / {v.get("file")} / {v.get("motivo")} / {v.get("sha256_precedente") == salvato} / '
          f'{v.get("sha256_corretto") == comune.sha256_file(cap)} / {stato()["gate_in_attesa"]}', sez)
    # (a) correzione già salvata, con --commit
    salva(r)
    h = git(r, 'log', '-1', '--format=%h').stdout.strip()
    p2 = zb(r, 'correggi', 'mini', '1: registrata dopo il salvataggio', '--commit', h)
    v = stato()['correzioni_registrate'][-1]
    esito('fase.py', '(a) correggi --commit: sha256 prima e dopo il commit', A['a_commit'],
          f'{p2.returncode} / {v["sha256_precedente"] == salvato} / {v["sha256_corretto"] == comune.sha256_file(cap)} / '
          f'{v["commit"] == h}', sez)
    p3 = zb(r, 'correggi', 'mini', 'capitolo 9: inesistente')
    p4 = zb(r, 'correggi', 'mini', 'senza due punti')
    esito('fase.py', '(a) unità inesistente / uso sbagliato: rifiutati', A['a_rifiuti'],
          f'{p3.returncode} / {p4.returncode} / {len(stato()["correzioni_registrate"])}', sez)

    # (b) esito su un capitolo già scritto: misure aggiornate, passo invariato
    st = stato()
    st.update(ultimo_capitolo_scritto=2, passo='capitolo 3')      # capitoli 1-2 già scritti
    open(os.path.join(Lm, 'stato.yaml'), 'w', encoding='utf-8').write(yaml.safe_dump(st, sort_keys=False, allow_unicode=True))
    salva(r)
    p5 = zb(r, 'esito', 'mini', '1')
    esito('fase.py', '(b) esito di nuovo sul capitolo 1 (scritti fino a 2): codice / passo / scritti', A['b_passo'],
          f'{p5.returncode} / {stato()["passo"]} / {stato()["ultimo_capitolo_scritto"]}', sez)

def unita_consentite_e_interludi(A):
    import fase
    import stile
    sez = 'unità consentite e interludi'

    def avvisi(voce, testi, interludio=None):
        Lm = copia_libro('mini-libro')
        py = os.path.join(Lm, 'libro.yaml')
        lb = yaml.safe_load(open(py, encoding='utf-8'))
        lb['voci'] = (lb.get('voci') or []) + ([voce] if voce else [])
        open(py, 'w', encoding='utf-8').write(yaml.safe_dump(lb, allow_unicode=True, sort_keys=False))
        md = os.path.join(Lm, '04-manoscritto')
        for f, t in zip(sorted(x for x in os.listdir(md) if x[0].isdigit()), testi):
            open(os.path.join(md, f), 'a', encoding='utf-8').write('\n' + t + '\n')
        if interludio is not None:
            open(os.path.join(md, 'interludio-I.md'), 'w', encoding='utf-8').write('## *La vetrina*\n\n' + interludio + '\n')
        cartella, libro, profilo = comune.carica_libro(Lm)
        esiti = stile.controlla_libro(cartella, libro, profilo)
        return [f'{r["unita"]}|{r["controllo"]}|{r["esito"]}' for u in esiti for r in esiti[u][1]
                if r['controllo'] == f'voce:{(voce or {}).get("id")}'
                or (r['controllo'] == 'frase_media' and u.startswith('interludio'))]

    # (a) voce ad ambito «libro»: unità consentite escluse; tetto per unità o per occorrenza
    for chiave, voce in A['a_voci'].items():
        esito('stile.py', f'(a) {chiave}', A['a_attesi'][chiave], avvisi(voce, A['a_testi']), sez)
    # (b) frase media negli interludi: avviso con l'intervallo dei capitoli
    for chiave, testo in A['b_testi'].items():
        esito('stile.py', f'(b) interludio: {chiave}', A['b_attesi'][chiave], avvisi(None, [], testo), sez)
    # (c) piano parole: ogni scarto con la virgola, anche le righe scritte prima
    Lm = copia_libro('mini-libro')
    pp = os.path.join(Lm, '03-architettura', 'piano-parole.md')
    t = open(pp, encoding='utf-8').read().replace('| 150 | 150 | | |', '| 150 | 150 | 167 | +11.5% |')
    open(pp, 'w', encoding='utf-8').write(t)
    cartella, libro, _ = comune.carica_libro(Lm)
    fase.aggiorna_piano(cartella, libro, '1')
    esito('fase.py', '(c) scarti nel piano parole', A['c_scarti'],
          [x.split('|')[-2].strip() for x in open(pp, encoding='utf-8').read().splitlines()
           if x.startswith('| — |') and x.split('|')[-2].strip()], sez)


def fase_stesura_e_rinomine(A):
    sez = 'fase e rinomine'
    E = {k: v for k, v in ENV.items() if k not in ('CLAUDE_PROJECT_DIR', 'ZB_LIBRO', 'ZB_RAMO', 'ZB_SESSIONE')}
    E.update(GIT_AUTHOR_NAME='Prova', GIT_AUTHOR_EMAIL='prova@esempio.invalid',
             GIT_COMMITTER_NAME='Prova', GIT_COMMITTER_EMAIL='prova@esempio.invalid')

    def git(cwd, *a):
        return subprocess.run(['git', *a], cwd=cwd, env=E, capture_output=True, text=True)

    def zb(cwd, *a):
        return subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), *a], cwd=cwd, env=E, capture_output=True, text=True)

    def salva(r):
        git(r, 'add', '-A')
        git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'prova')
        git(r, 'push', '-q', '-u', 'origin', 'prova')
        return git(r, 'log', '-1', '--format=%h').stdout.strip()

    def libro(**campi):
        d = tempfile.mkdtemp(dir=TMP)
        git(d, 'init', '-q', '--bare', 'remoto.git')
        r = os.path.join(d, 'repo')
        os.makedirs(r)
        git(r, 'init', '-q')
        git(r, 'checkout', '-q', '-b', 'prova')
        git(r, 'remote', 'add', 'origin', os.path.join(d, 'remoto.git'))
        Lm = shutil.copytree(os.path.join(M, 'prove', 'mini-libro'), os.path.join(r, 'mini'))
        pp = os.path.join(Lm, '03-architettura', 'piano-parole.md')
        t = open(pp, encoding='utf-8').read().replace('| — | 3 | La stazione | rivelazione | 1 | 900 | 900 | | |',
                                                      '| — | 3 | La stazione | rivelazione | 1 | 900 | 900 | | |\n' + A['riga_epilogo'])
        open(pp, 'w', encoding='utf-8').write(t)
        st = comune.leggi_yaml(os.path.join(M, 'modelli', 'stato.yaml'))
        st.update(libro='Prova di stampa', fase='stesura', passo='capitolo 4', aggiornato='prova', gate_in_attesa=None,
                  ultimo_capitolo_scritto=3, ultimo_capitolo_approvato=3)
        st.update(campi)
        open(os.path.join(Lm, 'stato.yaml'), 'w', encoding='utf-8').write(yaml.safe_dump(st, sort_keys=False, allow_unicode=True))
        salva(r)
        return r, Lm

    def stato(Lm):
        return comune.leggi_yaml(os.path.join(Lm, 'stato.yaml'))

    # (a) capitoli tutti scritti: la fase resta «stesura» finché mancano interludio ed epilogo
    r, Lm = libro()
    p1 = zb(r, 'esito', 'mini', 'interludio', 'I')
    s1 = stato(Lm)
    p2 = zb(r, 'esito', 'mini', 'epilogo')        # file non scritto: rifiutato, la fase non cambia
    open(os.path.join(Lm, '04-manoscritto', 'epilogo.md'), 'w', encoding='utf-8').write(A['testo_epilogo'])
    salva(r)
    p3 = zb(r, 'esito', 'mini', 'epilogo')
    s3 = stato(Lm)
    esito('fase.py', '(a) interludio, epilogo assente, epilogo scritto: codice / fase / passo', A['a_fasi'],
          f'{p1.returncode} / {s1["fase"]} / {s1["passo"]} / {p2.returncode} / {p3.returncode} / {s3["fase"]}', sez)
    p4 = zb(r, 'esito', 'mini', '9')
    esito('fase.py', '(a) unità fuori dal piano: rifiutata', A['a_fuori_piano'], p4.returncode, sez)

    # (b) zb fase stesura: solo da «chiusura», solo se mancano unità, con motivo registrato
    r, Lm = libro(fase='chiusura', passo='controlli finali')
    q1 = zb(r, 'fase', 'mini', 'stesura')
    q2 = zb(r, 'fase', 'mini', 'stesura', '--motivo', 'manca l\'epilogo')
    s = stato(Lm)
    v = (s.get('cambi_fase') or [{}])[-1]
    q3 = zb(r, 'fase', 'mini', 'stesura', '--motivo', 'di nuovo')
    esito('fase.py', '(b) senza motivo / con motivo / già in stesura', A['b_codici'],
          f'{q1.returncode} / {q2.returncode} / {q3.returncode}', sez)
    esito('fase.py', '(b) registro: da / a / motivo / mancanti / fase / passo', A['b_registro'],
          f'{v.get("da")} / {v.get("a")} / {v.get("motivo")} / {v.get("mancanti")} / {s["fase"]} / {s["passo"]}', sez)
    open(os.path.join(Lm, '04-manoscritto', 'epilogo.md'), 'w', encoding='utf-8').write(A['testo_epilogo'])
    st = stato(Lm)
    st.update(fase='chiusura', unita_accettate=['interludio I', 'epilogo'])
    open(os.path.join(Lm, 'stato.yaml'), 'w', encoding='utf-8').write(yaml.safe_dump(st, sort_keys=False, allow_unicode=True))
    salva(r)
    q4 = zb(r, 'fase', 'mini', 'stesura', '--motivo', 'niente da scrivere')
    esito('fase.py', '(b) nessuna unità mancante: rifiutato, resta chiusura', A['b_completo'],
          f'{q4.returncode} / {stato(Lm)["fase"]}', sez)

    # (c) correggi segue i file rinominati
    r, Lm = libro()
    md = os.path.join(Lm, '04-manoscritto')
    originale = comune.sha256_file(os.path.join(md, '01-la-farmacia.md'))
    git(r, 'mv', 'mini/04-manoscritto/01-la-farmacia.md', 'mini/04-manoscritto/01-la-bottega.md')
    open(os.path.join(md, '01-la-bottega.md'), 'a', encoding='utf-8').write('\nUna riga nuova.\n')
    git(r, 'add', '-A')
    c1 = zb(r, 'correggi', 'mini', 'capitolo 1: titolo nuovo')
    v1 = (stato(Lm).get('correzioni_registrate') or [{}])[-1]
    h = salva(r)
    c2 = zb(r, 'correggi', 'mini', 'capitolo 1: titolo nuovo, dal commit', '--commit', h)
    v2 = (stato(Lm).get('correzioni_registrate') or [{}])[-1]
    salva(r)
    c3 = zb(r, 'correggi', 'mini', 'capitolo 1: titolo nuovo, dopo il salvataggio')
    v3 = (stato(Lm).get('correzioni_registrate') or [{}])[-1]
    esito('fase.py', '(c) rinomina: non salvata / --commit / salvata: codice e sha256 precedente = originale',
          A['c_rinomina'],
          ' / '.join(f'{c.returncode} {v.get("sha256_precedente") == originale}' for c, v in ((c1, v1), (c2, v2), (c3, v3))),
          sez)


def correzioni_esclusioni_e_budget(A):
    import capitolo
    import stile
    sez = 'esclusioni e budget'

    def mini_con(voci=None, testi=(), interludio=None):
        Lm = copia_libro('mini-libro')
        py = os.path.join(Lm, 'libro.yaml')
        lb = yaml.safe_load(open(py, encoding='utf-8'))
        lb['voci'] = (lb.get('voci') or []) + (voci or [])
        open(py, 'w', encoding='utf-8').write(yaml.safe_dump(lb, allow_unicode=True, sort_keys=False))
        md = os.path.join(Lm, '04-manoscritto')
        for f, t in zip(sorted(x for x in os.listdir(md) if x[0].isdigit()), testi):
            open(os.path.join(md, f), 'a', encoding='utf-8').write('\n' + t + '\n')
        if interludio is not None:
            open(os.path.join(md, 'interludio-I.md'), 'w', encoding='utf-8').write('## *La vetrina*\n\n' + interludio + '\n')
        return comune.carica_libro(Lm)

    # (a) escludi_pattern, sia per ambito «libro» sia per ambito «capitolo»
    for chiave, voce in A['a_voci'].items():
        cartella, libro, profilo = mini_con([voce], A['a_testi'])
        esiti = stile.controlla_libro(cartella, libro, profilo)
        esito('stile.py', f'(a) escludi_pattern: {chiave}', A['a_attesi'][chiave],
              [f'{u}|{r["esito"]}' for u in esiti for r in esiti[u][1] if r['controllo'] == f'voce:{voce["id"]}'], sez)
    # (b) pattern generico «Non era/è X. Era/È Y.»: quante frasi prende
    esito('stile.py', '(b) pattern generico: frasi prese', A['b_attesi'],
          [len(stile.occorrenze([(1, f)], A['b_pattern'])) for f in A['b_frasi']], sez)
    # (c) budget degli interludi: avviso fuori tolleranza
    for chiave, testo in A['c_testi'].items():
        cartella, libro, profilo = mini_con(interludio=testo)
        _, out = capitolo.controlla(cartella, libro, profilo, 'interludio I')
        esito('capitolo.py', f'(c) budget interludio: {chiave}', A['c_attesi'][chiave],
              [r['esito'] for r in out if r['controllo'] == 'parole_budget'], sez)
    # (d) in «chiusura» correggi ed esito funzionano sulle unità scritte e non cambiano la fase
    E = {k: v for k, v in ENV.items() if k not in ('CLAUDE_PROJECT_DIR', 'ZB_LIBRO', 'ZB_RAMO', 'ZB_SESSIONE')}
    E.update(GIT_AUTHOR_NAME='Prova', GIT_AUTHOR_EMAIL='prova@esempio.invalid',
             GIT_COMMITTER_NAME='Prova', GIT_COMMITTER_EMAIL='prova@esempio.invalid')

    def git(cwd, *a):
        return subprocess.run(['git', *a], cwd=cwd, env=E, capture_output=True, text=True)

    def zb(cwd, *a):
        return subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), *a], cwd=cwd, env=E, capture_output=True, text=True)

    d = tempfile.mkdtemp(dir=TMP)
    git(d, 'init', '-q', '--bare', 'remoto.git')
    r = os.path.join(d, 'repo')
    os.makedirs(r)
    git(r, 'init', '-q')
    git(r, 'checkout', '-q', '-b', 'prova')
    git(r, 'remote', 'add', 'origin', os.path.join(d, 'remoto.git'))
    Lm = shutil.copytree(os.path.join(M, 'prove', 'mini-libro'), os.path.join(r, 'mini'))
    st = comune.leggi_yaml(os.path.join(M, 'modelli', 'stato.yaml'))
    st.update(libro='Prova di stampa', fase='chiusura', passo='controlli finali', aggiornato='prova', gate_in_attesa=None,
              ultimo_capitolo_scritto=3, ultimo_capitolo_approvato=3, unita_accettate=['interludio I'])
    open(os.path.join(Lm, 'stato.yaml'), 'w', encoding='utf-8').write(yaml.safe_dump(st, sort_keys=False, allow_unicode=True))
    git(r, 'add', '-A')
    git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'prova')
    open(os.path.join(Lm, '04-manoscritto', '01-la-farmacia.md'), 'a', encoding='utf-8').write('\nUna riga corretta.\n')
    p1 = zb(r, 'correggi', 'mini', 'capitolo 1: una riga in più')
    p2 = zb(r, 'esito', 'mini', '1')
    p3 = zb(r, 'esito', 'mini', 'interludio', 'I')
    s2 = comune.leggi_yaml(os.path.join(Lm, 'stato.yaml'))
    esito('fase.py', '(d) chiusura: correggi / esito 1 / esito interludio: codici, fase, passo, correzioni', A['d_chiusura'],
          f'{p1.returncode} / {p2.returncode in (0, 1)} / {p3.returncode in (0, 1)} / {s2["fase"]} / {s2["passo"]} / '
          f'{len(s2.get("correzioni_registrate") or [])}', sez)


# ---------------------------------------------------------------- titoli, tempi relativi, età, fatti, push

def titoli_tempi_eta_push(A):
    import compila
    import continuita
    sez = 'titoli, tempi, età, push'

    def mini(testi=None, intestazioni=None, cronologia=None, libro_extra=None):
        Lm = copia_libro('mini-libro')
        md = os.path.join(Lm, '04-manoscritto')
        caps = sorted(x for x in os.listdir(md) if x[0].isdigit())
        for f, t in zip(caps, testi or []):
            if t:
                open(os.path.join(md, f), 'a', encoding='utf-8').write('\n' + t + '\n')
        for f, t in zip(caps, intestazioni or []):
            if t:
                righe = open(os.path.join(md, f), encoding='utf-8').read().split('\n')
                righe[1] = t
                open(os.path.join(md, f), 'w', encoding='utf-8').write('\n'.join(righe))
        if cronologia:
            pc = os.path.join(Lm, 'cronologia.yaml')
            cron = yaml.safe_load(open(pc, encoding='utf-8'))
            cron.update(cronologia)
            open(pc, 'w', encoding='utf-8').write(yaml.safe_dump(cron, allow_unicode=True))
        if libro_extra:
            py = os.path.join(Lm, 'libro.yaml')
            lb = yaml.safe_load(open(py, encoding='utf-8'))
            lb.update(libro_extra)
            open(py, 'w', encoding='utf-8').write(yaml.safe_dump(lb, allow_unicode=True, sort_keys=False))
        return Lm

    def avvisi(Lm, controllo):
        _, libro, _ = comune.carica_libro(Lm)
        return [f'{r["unita"]}|{r["esito"]}' for r in continuita.controlla_libro(Lm, libro)[0]
                if r['controllo'].startswith(controllo)]

    # (a) compila: titolo dall'intestazione sorgente nel testo e nel sommario; senza titolo, avviso
    Lm = copia_libro('mini-libro')
    p1 = os.path.join(Lm, '04-manoscritto', '01-la-farmacia.md')
    t = open(p1, encoding='utf-8').read()
    open(p1, 'w', encoding='utf-8').write(t.replace('## 1\n', A['a_intestazione'] + '\n', 1))
    _, libro, _ = comune.carica_libro(Lm)
    av = []
    out = compila.compila(Lm, libro, av)
    esito('compila.py', '(a) capitolo con titolo: sommario | intestazione', A['a_con_titolo'],
          f'{("- " + A["a_atteso"]) in out.splitlines()} | {("## " + A["a_atteso"]) in out.splitlines()}', sez)
    esito('compila.py', '(a) capitoli senza titolo: avvisi', A['a_senza_titolo'],
          [a.split(' senza titolo')[0] for a in av], sez)
    # (b) tempi relativi: testo inventato aggiunto al capitolo 2 (venerdì 4 marzo 2021)
    for chiave, prova in A['b_prove'].items():
        Lm = mini(testi=prova.get('testi'), intestazioni=prova.get('intestazioni'))
        esito('continuita.py', f'(b) tempi relativi: {chiave}', prova['atteso'], avvisi(Lm, 'tempo_relativo'), sez)
    # (c) differenze d'età tra personaggi con data di nascita (Irene 1985-06-10, Gemma 1999-09-02: 14 anni)
    for chiave, frase in A['c_frasi'].items():
        Lm = mini(testi=[frase])
        esito('continuita.py', f'(c) differenza d\'età: {chiave}', A['c_attesi'][chiave], avvisi(Lm, 'differenza_eta'), sez)
    # (d) fatti_incompatibili: avviso con le due righe se compaiono tutti e due
    for chiave, prova in A['d_prove'].items():
        Lm = mini(testi=prova['testi'], libro_extra={'fatti_incompatibili': A['d_fatti']})
        _, libro, _ = comune.carica_libro(Lm)
        ris = [r for r in continuita.controlla_libro(Lm, libro)[0] if r['controllo'].startswith('fatti_incompatibili')]
        esito('continuita.py', f'(d) fatti incompatibili: {chiave}', prova['atteso'],
              [f'{r["unita"]}|{r["esito"]}|{"riga" in r["dettaglio"] and "«" in r["dettaglio"]}' for r in ris], sez)
    # (e) due correzioni prima dello stesso commit: la seconda registra lo sha256 della prima
    E = {k: v for k, v in ENV.items() if k not in ('CLAUDE_PROJECT_DIR', 'ZB_LIBRO', 'ZB_RAMO', 'ZB_SESSIONE')}
    E.update(GIT_AUTHOR_NAME='Prova', GIT_AUTHOR_EMAIL='prova@esempio.invalid',
             GIT_COMMITTER_NAME='Prova', GIT_COMMITTER_EMAIL='prova@esempio.invalid')

    def git(cwd, *a):
        return subprocess.run(['git', *a], cwd=cwd, env=E, capture_output=True, text=True)

    def zb(cwd, *a):
        return subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), *a], cwd=cwd, env=E, capture_output=True, text=True)

    d = tempfile.mkdtemp(dir=TMP)
    r = os.path.join(d, 'repo')
    os.makedirs(r)
    git(r, 'init', '-q')
    git(r, 'checkout', '-q', '-b', 'prova')
    Lm = shutil.copytree(os.path.join(M, 'prove', 'mini-libro'), os.path.join(r, 'mini'))
    st = comune.leggi_yaml(os.path.join(M, 'modelli', 'stato.yaml'))
    st.update(libro='Prova di stampa', fase='chiusura', passo='controlli finali', aggiornato='prova', gate_in_attesa=None,
              ultimo_capitolo_scritto=3, ultimo_capitolo_approvato=3, unita_accettate=['interludio I'])
    open(os.path.join(Lm, 'stato.yaml'), 'w', encoding='utf-8').write(yaml.safe_dump(st, sort_keys=False, allow_unicode=True))
    git(r, 'add', '-A')
    git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'prova')
    pc = os.path.join(Lm, '04-manoscritto', '01-la-farmacia.md')
    sha = [comune.sha256_file(pc)]
    for riga in ('Prima riga corretta.', 'Seconda riga corretta.'):
        open(pc, 'a', encoding='utf-8').write('\n' + riga + '\n')
        sha.append(comune.sha256_file(pc))
        zb(r, 'correggi', 'mini', f'capitolo 1: {riga}')
    reg = comune.leggi_yaml(os.path.join(Lm, 'stato.yaml')).get('correzioni_registrate') or []
    catena = [(v['sha256_precedente'], v['sha256_corretto']) for v in reg]
    esito('fase.py', '(e) due correzioni prima del commit: precedente della seconda = corretto della prima',
          A['e_catena'], f'{len(reg)} / {catena == [(sha[0], sha[1]), (sha[1], sha[2])]}', sez)
    # (f) zb conta non scrive file; zb push: riuscito, ramo alternativo, bundle
    Lm = copia_libro('mini-libro')
    prima = sorted(os.path.relpath(os.path.join(a, f), Lm) for a, _, fs in os.walk(Lm) for f in fs)
    p = esegui(os.path.join(M, 'zb'), 'conta', Lm)
    dopo = sorted(os.path.relpath(os.path.join(a, f), Lm) for a, _, fs in os.walk(Lm) for f in fs)
    esito('conta.py', '(f) zb conta: codice | file nuovi | totale a schermo', A['f_conta'],
          f'{p.returncode} | {len(set(dopo) - set(prima))} | {"**Totale:**" in p.stdout}', sez)
    risultati = []
    for caso in ('ok', 'alternativo', 'bundle'):
        d = tempfile.mkdtemp(dir=TMP)
        git(d, 'init', '-q', '--bare', 'remoto.git')
        if caso == 'alternativo':        # il remoto rifiuta il ramo «prova» e accetta gli altri
            hk = os.path.join(d, 'remoto.git', 'hooks', 'pre-receive')
            open(hk, 'w').write('#!/bin/sh\nwhile read a b ref; do [ "$ref" = refs/heads/prova ] && exit 1; done\nexit 0\n')
            os.chmod(hk, 0o755)
        r = os.path.join(d, 'repo')
        os.makedirs(r)
        git(r, 'init', '-q')
        git(r, 'checkout', '-q', '-b', 'prova')
        git(r, 'remote', 'add', 'origin', os.path.join(d, 'remoto.git') if caso != 'bundle' else os.path.join(d, 'manca.git'))
        open(os.path.join(r, 'a.txt'), 'w').write('prova\n')
        git(r, 'add', '-A')
        git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'prova')
        bd = os.path.join(d, 'bundle')
        p = subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), 'push', '--tentativi', '3', '--attesa', '0',
                            '--bundle-dir', bd], cwd=r, env=E, capture_output=True, text=True)
        tent = p.stdout.count('non riuscito:')
        extra = ''
        if caso == 'alternativo':
            extra = ' ' + str('-salvataggio-' in git(os.path.join(d, 'remoto.git'), 'branch').stdout)
        if caso == 'bundle':
            b = [f for f in os.listdir(bd)] if os.path.isdir(bd) else []
            ok_sha = bool(b) and hashlib.sha256(open(os.path.join(bd, b[0]), 'rb').read()).hexdigest() in p.stdout
            extra = f' {len(b)} {ok_sha} {os.path.join(bd, b[0]) in p.stdout if b else False}'
        risultati.append(f'{caso}: {p.returncode} {tent}{extra}')
    esito('push.py', '(f) zb push: codice, tentativi falliti, ramo alternativo / bundle (file, sha256, percorso)',
          A['f_push'], ' / '.join(risultati), sez)


# ---------------------------------------------------------------- eccezioni motivate e richiami ammessi

def eccezioni_e_richiami(A):
    import capitolo
    import riciclo
    sez = 'eccezioni e richiami'
    for chiave, prova in A['prove'].items():
        Lm = copia_libro('mini-libro')
        md = os.path.join(Lm, '04-manoscritto')
        for f in ('01-la-farmacia.md', '03-la-stazione.md'):
            open(os.path.join(md, f), 'a', encoding='utf-8').write('\n' + A['frase'] + '\n')
        py = os.path.join(Lm, 'libro.yaml')
        lb = yaml.safe_load(open(py, encoding='utf-8'))
        if prova.get('stile'):
            lb['stile'] = prova['stile']
        open(py, 'w', encoding='utf-8').write(yaml.safe_dump(lb, allow_unicode=True, sort_keys=False))
        cartella, libro, profilo = comune.carica_libro(Lm)
        ric = [r['esito'] for r in riciclo.controlla_libro(cartella, libro) if r['controllo'] == 'riciclo:unita_precedenti']
        _, out = capitolo.controlla(cartella, libro, profilo, '3')
        ko = [r['esito'] for r in out if r['controllo'] == 'parole_minimo']
        esito('riciclo.py / capitolo.py', f'{chiave}: riciclo | parole_minimo del cap. 3', prova['atteso'], f'{ric} | {ko}', sez)


# ---------------------------------------------------------------- voce (banca-voci)

def voce(A):
    import nuovo
    sez = 'voce'
    banca = os.path.join(M, 'prove', 'banca-voci-prova')
    E = {k: v for k, v in ENV.items() if k not in ('CLAUDE_PROJECT_DIR', 'ZB_LIBRO', 'ZB_RAMO', 'ZB_SESSIONE', 'ZB_BANCA_VOCI')}
    E.update(GIT_AUTHOR_NAME='Prova', GIT_AUTHOR_EMAIL='prova@esempio.invalid',
             GIT_COMMITTER_NAME='Prova', GIT_COMMITTER_EMAIL='prova@esempio.invalid')

    def zb(cwd, *a, b=banca):
        env = dict(E, ZB_BANCA_VOCI=b) if b else E
        return subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), *a], cwd=cwd, env=env, capture_output=True, text=True)

    def tb(p):
        return 'Traceback' in p.stdout + p.stderr

    def git(cwd, *a):
        return subprocess.run(['git', *a], cwd=cwd, env=E, capture_output=True, text=True)

    def repo():
        d = tempfile.mkdtemp(dir=TMP)
        git(d, 'init', '-q', '--bare', 'remoto.git')
        r = os.path.join(d, 'repo')
        os.makedirs(r)
        git(r, 'init', '-q')
        git(r, 'checkout', '-q', '-b', 'prova')
        git(r, 'remote', 'add', 'origin', os.path.join(d, 'remoto.git'))
        return r

    def salva(r, msg='prova'):
        git(r, 'add', '-A')
        git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', msg)
        return git(r, 'push', '-q', '-u', 'origin', 'prova').returncode

    def letto(p):
        r = next((x for x in p.stdout.splitlines() if x.startswith('Letto: ')), '')
        return r

    # (a) zb voce lista | mostra | verifica sulla mini-banca inventata
    p = zb(M, 'voce', 'lista')
    voci = [f'{c[1].strip()}|{c[4].strip()}' for c in (x.split('|') for x in p.stdout.splitlines())
            if len(c) > 4 and c[1].strip().startswith('voce-')]
    esito('voce.py', '(a) lista: codice / voci|stato', A['lista'], f'{p.returncode} / {voci}', sez)
    p = zb(M, 'voce', 'mostra', 'voce-di-prova')
    esito('voce.py', '(a) mostra: codice / intestazione del blocco / 7 sezioni', A['mostra'],
          f'{p.returncode} / {"Blocco 1 di 1, righe 1-" in p.stdout} / {all(f"## {i}. " in p.stdout for i in range(1, 8))}', sez)
    p = zb(M, 'voce', 'mostra', 'voce-incompleta')
    esito('voce.py', '(a) mostra di una voce non pronta: codice / avviso', A['mostra_non_pronta'],
          f'{p.returncode} / {"AVVISO: voce non pronta" in p.stdout}', sez)
    p = zb(M, 'voce', 'mostra', 'voce-di-prova', '5')
    esito('voce.py', '(a) mostra di un blocco inesistente: codice / traceback', A['blocco_inesistente'], f'{p.returncode} / {tb(p)}', sez)
    p = zb(M, 'voce', 'verifica', 'voce-di-prova')
    esito('voce.py', '(a) verifica della voce pronta', A['verifica_pronta'], f'{p.returncode} / {p.stdout.strip()}', sez)
    p = zb(M, 'voce', 'verifica', 'voce-incompleta')
    esito('voce.py', '(a) verifica della voce non pronta: codice / motivo / traceback', A['verifica_non_pronta'],
          f'{p.returncode} / {"voce non pronta" in p.stdout} / {tb(p)}', sez)
    p = zb(M, 'voce', 'verifica', 'voce-inesistente')
    esito('voce.py', '(a) verifica di una voce assente dall\'indice: codice / traceback', A['voce_assente'], f'{p.returncode} / {tb(p)}', sez)
    # (b) senza ZB_BANCA_VOCI, o con una cartella che non è una banca
    out = []
    for a in (('lista',), ('mostra', 'voce-di-prova'), ('verifica', 'voce-di-prova')):
        p = zb(M, 'voce', *a, b=None)
        out.append(f'{p.returncode} {"ZB_BANCA_VOCI" in p.stderr} {tb(p)}')
    esito('voce.py', '(b) senza ZB_BANCA_VOCI: lista / mostra / verifica (codice, variabile nel messaggio, traceback)',
          A['senza_variabile'], ' / '.join(out), sez)
    vuota = tempfile.mkdtemp(dir=TMP)
    p = zb(M, 'voce', 'lista', b=vuota)
    esito('voce.py', '(b) ZB_BANCA_VOCI senza indice.yaml: codice / messaggio / traceback', A['senza_indice'],
          f'{p.returncode} / {"indice.yaml" in p.stderr} / {tb(p)}', sez)
    # (c) regressione: una scheda rotta fa fallire la verifica; ripristinata, torna OK
    d = tempfile.mkdtemp(dir=TMP)
    bc = shutil.copytree(banca, os.path.join(d, 'banca'))
    ps = os.path.join(bc, 'voci', 'voce-di-prova', 'scheda.md')
    orig = open(ps, encoding='utf-8').read()
    pd = os.path.join(bc, 'voci', 'voce-di-prova', 'divieti.yaml')
    orig_d = open(pd, encoding='utf-8').read()
    rotture = {
        'divieti.yaml non leggibile': lambda: open(pd, 'w', encoding='utf-8').write('divieti: [\n'),
        'senza la sezione 4': lambda: open(ps, 'w', encoding='utf-8').write(re.sub(r'(?s)## 4\..*?(?=## 5\.)', '', orig)),
        'senza ambientazione': lambda: open(ps, 'w', encoding='utf-8').write(orig.replace('ambientazione: altro\n', '')),
        'scheda assente': lambda: os.remove(ps),
    }
    for nome, rompi in rotture.items():
        rompi()
        p = zb(M, 'voce', 'verifica', 'voce-di-prova', b=bc)
        esito('voce.py', f'(c) scheda rotta, {nome}: codice / problemi', A['rotture'][nome],
              f'{p.returncode} / {[x.strip()[2:] for x in p.stdout.splitlines() if x.startswith("  - ")]}', sez)
        open(ps, 'w', encoding='utf-8').write(orig)
        open(pd, 'w', encoding='utf-8').write(orig_d)
    p = zb(M, 'voce', 'verifica', 'voce-di-prova', b=bc)
    esito('voce.py', '(c) scheda ripristinata: codice', A['ripristinata'], p.returncode, sez)
    # (d) libro senza blocco voce: avvio identico con e senza ZB_BANCA_VOCI, nessuna voce letta
    briefing = open(os.path.join(M, 'prove', 'briefing', 'briefing-giallo.md'), encoding='utf-8').read()

    def libro(testo):
        r = repo()
        L = os.path.join(r, 'giallo')
        os.makedirs(L)
        open(os.path.join(L, 'briefing.md'), 'w', encoding='utf-8').write(testo)
        zb(r, 'nuovo', 'giallo/briefing.md')
        salva(r, 'nuovo libro')
        return r, L

    r, L = libro(briefing)
    p1, p2 = zb(r, 'avvio', 'giallo', b=None), zb(r, 'avvio', 'giallo')
    senza = lambda p: [x for x in p.stdout.splitlines() if not x.startswith('Sessione:')]
    esito('avvio.py', '(d) libro senza voce: codici / uscita con e senza ZB_BANCA_VOCI / voce in «Letto» / blocco in libro.yaml',
          A['libro_senza_voce'], f'{p1.returncode} {p2.returncode} / {"identica" if senza(p1) == senza(p2) else "diversa"} / '
          f'{"voce " in letto(p2)} / {"voce" in comune.leggi_yaml(os.path.join(L, "libro.yaml"))}', sez)
    # (e) libro con voce dal briefing: blocco in libro.yaml, «Letto» con scheda e briefing
    r, L = libro(briefing.rstrip('\n') + '\n' + A['briefing_voce'])
    _, lb, _ = comune.carica_libro(L)
    esito('nuovo.py', '(e) briefing con la voce: blocco voce in libro.yaml', A['blocco_voce'], lb.get('voce'), sez)
    p = zb(r, 'avvio', 'giallo')
    esito('avvio.py', '(e) libro con voce: codice / scheda in «Letto» / briefing in «Letto» / file letti / avvisi',
          A['libro_con_voce'], f'{p.returncode} / {"scheda della voce voce-di-prova (" in letto(p)} / '
          f'{"00-progetto/briefing.md (" in letto(p)} / {letto(p).count(" righe, sha256 ")} / '
          f'{sum(1 for x in p.stdout.splitlines() if x.startswith("AVVISO"))}', sez)
    p = zb(r, 'avvio', 'giallo', b=None)
    esito('avvio.py', '(e) libro con voce senza ZB_BANCA_VOCI: codice / avviso / scheda in «Letto»', A['con_voce_senza_variabile'],
          f'{p.returncode} / {any(x.startswith("AVVISO") and "ZB_BANCA_VOCI" in x for x in p.stdout.splitlines())} / '
          f'{"scheda della voce" in letto(p)}', sez)
    py = os.path.join(L, 'libro.yaml')
    t = open(py, encoding='utf-8').read()
    open(py, 'w', encoding='utf-8').write(t.replace('slug: voce-di-prova', 'slug: voce-incompleta'))
    salva(r, 'voce non pronta')
    p = zb(r, 'avvio', 'giallo')
    esito('avvio.py', '(e) libro con voce non pronta: codice / avviso (non blocco)', A['con_voce_non_pronta'],
          f'{p.returncode} / {any(x.startswith("AVVISO") and "voce non pronta" in x for x in p.stdout.splitlines())}', sez)
    # (g) divieti della voce: AVVISO in stile.py, sommati alle voci del libro; senza voce o senza banca, niente
    import stile
    Lm = copia_libro('mini-libro')
    open(os.path.join(Lm, '04-manoscritto', '01-la-farmacia.md'), 'a', encoding='utf-8').write('\n' + A['frase_divieti'] + '\n')

    def divieti_trovati(con_voce, b):
        if con_voce:
            py = os.path.join(Lm, 'libro.yaml')
            lb = yaml.safe_load(open(py, encoding='utf-8'))
            lb['voce'] = {'slug': 'voce-di-prova', 'ambientazione': 'altro'}
            open(py, 'w', encoding='utf-8').write(yaml.safe_dump(lb, allow_unicode=True, sort_keys=False))
        prima = os.environ.pop('ZB_BANCA_VOCI', None)
        if b:
            os.environ['ZB_BANCA_VOCI'] = b
        try:
            cartella, libro, profilo = comune.carica_libro(Lm)
            ris = stile.controlla_libro(cartella, libro, profilo)['1'][1]
        finally:
            os.environ.pop('ZB_BANCA_VOCI', None)
            if prima is not None:
                os.environ['ZB_BANCA_VOCI'] = prima
        return sorted(f'{r["controllo"]}|{r["esito"]}' for r in ris if r['controllo'].startswith('voce:voce-di-prova:'))

    esito('stile.py', '(g) divieti della voce: libro senza voce', A['divieti_senza_voce'], divieti_trovati(False, banca), sez)
    esito('stile.py', '(g) divieti della voce: libro con voce, senza ZB_BANCA_VOCI', A['divieti_senza_banca'],
          divieti_trovati(True, None), sez)
    esito('stile.py', '(g) divieti della voce: libro con voce e banca', A['divieti_con_voce'], divieti_trovati(True, banca), sez)
    # (f) schema: voce senza slug rifiutata; zb aiuto; modello del briefing
    Lm = copia_libro('mini-libro')
    open(os.path.join(Lm, 'libro.yaml'), 'a', encoding='utf-8').write('voce: {ambientazione: altro}\n')
    try:
        comune.carica_libro(Lm)
        msg = 'accettato'
    except comune.ErroreMotore as e:
        msg = 'libro.yaml.voce.slug: campo obbligatorio mancante' in str(e)
    esito('comune.py', '(f) libro.yaml con voce senza slug: rifiutato con il campo', A['schema_senza_slug'], msg, sez)
    esito('zb', '(f) zb aiuto elenca zb voce', A['aiuto'], 'zb voce lista' in zb(M, 'aiuto').stdout, sez)
    pm = os.path.join(M, 'modelli', 'briefing.md')
    b = nuovo.leggi_briefing(pm)
    titoli = [x[3:].strip().lower() for x in open(pm, encoding='utf-8').read().splitlines() if x.startswith('## ')]
    esito('nuovo.py', '(f) modello del briefing: sezioni nuove / campi della voce / esempio fuori dai dati',
          A['modello_briefing'], f'{[t for t in A["sezioni_briefing"] if t not in titoli]} / '
          f'{"voce dalla banca" in b["campi"] and "ambientazione" in b["campi"]} / {b["personaggi"]}', sez)


def recinto_libro(A):
    """Libro inventato: zb nuovo rifiutato dentro motore/ e sul ramo motore; hook di blocco."""
    import json
    sez = 'recinto libro'
    E = {k: v for k, v in ENV.items() if k not in ('CLAUDE_PROJECT_DIR', 'ZB_LIBRO', 'ZB_RAMO', 'ZB_SESSIONE')}
    briefing = open(os.path.join(M, 'prove', 'briefing', 'briefing-giallo.md'), encoding='utf-8').read()

    def repo(ramo):
        r = os.path.join(tempfile.mkdtemp(dir=TMP), 'repo')
        os.makedirs(r)
        subprocess.run(['git', 'init', '-q', r], capture_output=True)
        subprocess.run(['git', '-C', r, 'checkout', '-q', '-b', ramo], capture_output=True)
        return r

    def nuovo_in(r, rel):
        L = os.path.join(r, rel)
        os.makedirs(L)
        open(os.path.join(L, 'briefing.md'), 'w', encoding='utf-8').write(briefing)
        p = subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), 'nuovo', os.path.join(L, 'briefing.md')],
                           cwd=r, env=E, capture_output=True, text=True)
        return f'{p.returncode} / {A["messaggio_" + rel.split("/")[0]] in p.stderr} / {os.listdir(L)}'

    esito('nuovo.py', 'libro inventato dentro motore/: rifiutato, niente creato', A['dentro_motore'],
          nuovo_in(repo('libro-prova'), 'motore/giallo'), sez)
    esito('nuovo.py', 'libro inventato in libri/<slug>/ sul ramo motore: rifiutato, niente creato', A['ramo_motore'],
          nuovo_in(repo('motore'), 'libri/giallo'), sez)
    r = repo('libro-prova')
    os.makedirs(os.path.join(r, 'libri', 'giallo'))
    open(os.path.join(r, 'libri', 'libro-attivo.md'), 'w', encoding='utf-8').write('giallo\n')

    def hook(rel):
        dati = json.dumps({'tool_name': 'Write', 'cwd': r, 'tool_input': {'file_path': os.path.join(r, rel)}})
        p = subprocess.run([sys.executable, '-B', os.path.join(S, 'hook_recinto.py')], input=dati,
                           env=dict(E, CLAUDE_PROJECT_DIR=r), capture_output=True, text=True)
        return f'{p.returncode} {"RECINTO" in p.stderr}'

    esito('hook_recinto.py', 'Write fuori dal libro attivo (motore/) / dentro libri/<slug>/', A['hook'],
          f'{hook("motore/nota.md")} / {hook("libri/giallo/02-bibbia/nota.md")}', sez)


# ---------------------------------------------------------------- tabella

# ---------------------------------------------------------------- appendici e titoli interni

def appendici(A):
    """compila su una copia di mini-libro con le appendici di prove/appendici/ e un titolo interno «##»."""
    import compila
    sez = 'appendici'
    Lm = copia_libro('mini-libro')
    dir_a = os.path.join(Lm, '05-appendici')
    os.makedirs(dir_a)
    for f in ('soluzioni-prova.md', 'nota-in-piu.md', 'piantina-prova.svg'):
        shutil.copyfile(os.path.join(M, 'prove', 'appendici', f), os.path.join(dir_a, f))
    p2 = os.path.join(Lm, '04-manoscritto', '02-l-officina.md')
    open(p2, 'a', encoding='utf-8').write('\n' + A['titolo_interno'] + '\n\nQuale chiave apre la vetrina?\n')
    py = os.path.join(Lm, 'libro.yaml')
    lb = yaml.safe_load(open(py, encoding='utf-8'))
    lb['appendici'] = A['dichiarate']
    open(py, 'w', encoding='utf-8').write(yaml.safe_dump(lb, allow_unicode=True, sort_keys=False))
    _, libro, _ = comune.carica_libro(Lm)
    av = []
    out = compila.compila(Lm, libro, av).splitlines()
    i = out.index('## Sommario')
    sommario = []
    for r in out[i + 2:]:
        if not r.startswith('- '):
            break
        sommario.append(r[2:])
    esito('compila.py', 'sommario: ultime voci', A['sommario_coda'], sommario[-len(A['sommario_coda']):], sez)
    esito('compila.py', 'titolo interno conservato, un livello sotto', A['titolo_compilato'],
          [r for r in out if 'indovinello' in r], sez)
    sezioni_app = [k for k, r in enumerate(out) if r == '<!-- zb:sezione appendice -->']
    esito('compila.py', 'appendici dopo l\'ultima unità, nell\'ordine dichiarato', A['titoli_appendici'],
          [out[k + 2] for k in sezioni_app], sez)
    esito('compila.py', 'avviso per il file non dichiarato', A['avviso_non_dichiarato'],
          [a for a in av if 'non è dichiarato' in a], sez)
    png = os.path.join(Lm, '05-output', 'appendici', 'piantina-prova.png')
    if shutil.which('node'):
        esito('compila.py', 'SVG convertito in PNG, con didascalia', A['immagine'],
              f'{os.path.isfile(png)} / {any("<figcaption>" in r and "piantina-prova.png" in r for r in out)}', sez)
    else:
        saltata('compila.py', 'SVG convertito in PNG, con didascalia', 'node assente', sez)
    lb['appendici'] = lb['appendici'] + [{'titolo': 'Mancante', 'file': 'non-esiste.md'}]
    open(py, 'w', encoding='utf-8').write(yaml.safe_dump(lb, allow_unicode=True, sort_keys=False))
    _, libro, _ = comune.carica_libro(Lm)
    try:
        compila.compila(Lm, libro, [])
        ottenuto = 'nessun errore'
    except comune.ErroreMotore as e:
        ottenuto = str(e)
    esito('compila.py', 'appendice dichiarata e assente: FERMO', A['fermo_assente'], ottenuto, sez)


SEZIONI = {'passo_1': passo_1, 'passo_2': passo_2, 'passo_3': passo_3, 'passo_4': passo_4, 'passo_5': passo_5, 'passo_5b': passo_5b, 'passo_6': passo_6, 'passo_7': passo_7, 'override_lunghezza': override_lunghezza, 'scene': scene, 'manuale_leggibile': manuale_leggibile, 'checklist_capitolo': checklist_capitolo, 'continuita_eta_durate': continuita_eta_durate, 'correzioni_dopo_prova': correzioni_dopo_prova, 'adozione_libri_esistenti': adozione_libri_esistenti, 'correzioni_interludi_e_grafie': correzioni_interludi_e_grafie, 'correzioni_e_passo': correzioni_e_passo, 'unita_consentite_e_interludi': unita_consentite_e_interludi, 'fase_stesura_e_rinomine': fase_stesura_e_rinomine, 'correzioni_esclusioni_e_budget': correzioni_esclusioni_e_budget, 'titoli_tempi_eta_push': titoli_tempi_eta_push, 'eccezioni_e_richiami': eccezioni_e_richiami, 'voce': voce, 'recinto_libro': recinto_libro, 'appendici': appendici}


def main(argv):
    A = comune.leggi_yaml(os.path.join(M, 'prove', 'attesi.yaml'))
    try:
        for chiave, funz in SEZIONI.items():
            if chiave in A:
                funz(A[chiave])
        finali = []
        for nome in ('separazione.py', 'recinto.py'):
            p = esegui(os.path.join(S, nome), '--radice', M)
            finali.append((nome, p.returncode, (p.stdout.strip().splitlines() or [''])[-1]))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print('| Sezione | Script | Controllo | Atteso | Ottenuto | Esito |')
    print('|---|---|---|---|---|---|')
    for r in righe:
        print('| ' + ' | '.join(r) + ' |')
    ok = sum(1 for r in righe if r[5] == 'OK')
    contate = [r for r in righe if r[5] != 'SALTATA']
    print(f'\nProve: {ok}/{len(contate)} OK; saltate: {len(righe) - len(contate)} (non contate nel totale)')
    for motivo in sorted({r[4] for r in righe if r[5] == 'SALTATA'}):
        n = sum(1 for r in righe if r[5] == 'SALTATA' and r[4] == motivo)
        print(f'saltate: {n}, {motivo}')
        if motivo.startswith('LanguageTool assente'):
            print('  per eseguirle: installare LanguageTool come in motore/README.md, sezione «LanguageTool»,'
                  ' e impostare ZB_LANGUAGETOOL')
    for nome, codice, riga in finali:
        print(f'{nome} su motore/: {"OK" if codice == 0 else "KO"} — {riga}')
    tutto_ok = ok == len(contate) and all(c == 0 for _, c, _ in finali)
    print('ESITO: ' + ('tutto OK' if tutto_ok else 'CI SONO KO'))
    return 0 if tutto_ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
```

### `motore/script/pulizia.py`

```python
"""Pulizia di un libro (passo 6). Di default solo ELENCO: non cancella nulla.

Uso: python3 -B pulizia.py <libro> [--applica]
Candidati, con il peso:
- file temporanei: __pycache__/, _build/, *.pyc, *.tmp, *~;
- marker di sessioni vecchie in .zb/ (letto-*, compattato-* di sessioni diverse da quella corrente);
- PDF intermedi (nome con bozza, prova, tmp, temp, intermedio, vecchio, old);
- cartelle vuote;
- copie identiche byte per byte (sha256): per ogni gruppo ne tiene una e propone di togliere le altre.
Mai toccati: 04-manoscritto/, 01-originale/, .git/, libro.yaml, stato.yaml, i documenti approvati
in stato.yaml. Nessun comando git: la cronologia resta com'è.
--applica (solo dopo l'«ok» dell'autore) cancella esattamente gli elementi elencati.
"""
import hashlib
import os
import re
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

PROTETTE = ('04-manoscritto', '01-originale', '.git')
PROTETTI = ('libro.yaml', 'stato.yaml')
TEMP_DIR = ('__pycache__', '_build')
TEMP_FILE = re.compile(r'(\.pyc|\.tmp|~)$')
PDF_INTERMEDIO = re.compile(r'(bozza|prova|tmp|temp|intermedio|vecchio|old)', re.I)


def peso(p):
    if os.path.isfile(p):
        return os.path.getsize(p)
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(p) for f in fs)


def leggibile(n):
    for u in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or u == 'GB':
            return f'{n:.0f} {u}' if u == 'B' else f'{n:.1f} {u}'
        n /= 1024


def candidati(cartella):
    """[(percorso relativo, motivo, byte)], ordinati; nessun elemento protetto."""
    protetti = set(PROTETTI)
    ps = os.path.join(cartella, 'stato.yaml')
    if os.path.isfile(ps):
        protetti |= set((comune.leggi_yaml(ps) or {}).get('documenti_approvati') or {})
    sid, _ = comune.sessione_corrente()

    def protetto(rel):
        parti = rel.replace(os.sep, '/').split('/')
        return parti[0] in PROTETTE or rel.replace(os.sep, '/') in protetti

    out, visti = [], {}
    for radice, dirs, files in os.walk(cartella, topdown=True):
        rel_r = os.path.relpath(radice, cartella)
        rel_r = '' if rel_r == '.' else rel_r
        for d in list(dirs):
            rel = os.path.join(rel_r, d)
            if protetto(rel):
                dirs.remove(d)
            elif d in TEMP_DIR:
                out.append((rel + '/', 'temporaneo', peso(os.path.join(radice, d))))
                dirs.remove(d)
        for f in files:
            rel = os.path.join(rel_r, f)
            p = os.path.join(radice, f)
            if protetto(rel):
                continue
            if rel_r == '.zb' and re.match(r'^(letto|compattato)-', f) and not f.endswith(f'-{sid}'):
                out.append((rel, 'marker di una sessione vecchia', peso(p)))
            elif TEMP_FILE.search(f):
                out.append((rel, 'temporaneo', peso(p)))
            elif f.lower().endswith('.pdf') and PDF_INTERMEDIO.search(f):
                out.append((rel, 'PDF intermedio', peso(p)))
            elif os.path.getsize(p) > 0 and rel_r != '.zb':
                with open(p, 'rb') as fh:
                    visti.setdefault(hashlib.sha256(fh.read()).hexdigest(), []).append(rel)
    gia = {c[0] for c in out}
    # copie identiche: si tiene la prima in ordine (percorso più corto, poi alfabetico), anche se protetta
    for radice, _, files in os.walk(cartella):
        rel_r = os.path.relpath(radice, cartella)
        if rel_r.split(os.sep)[0] in ('04-manoscritto', '01-originale') and files:
            for f in files:
                p = os.path.join(radice, f)
                if os.path.getsize(p) > 0:
                    with open(p, 'rb') as fh:
                        h = hashlib.sha256(fh.read()).hexdigest()
                    if h in visti:
                        visti[h].append(os.path.join(rel_r, f))
    for h, gruppo in visti.items():
        if len(gruppo) < 2:
            continue
        gruppo.sort(key=lambda r: (not protetto(r), len(r), r))
        tieni = gruppo[0]
        for r in gruppo[1:]:
            if not protetto(r) and r not in gia:
                out.append((r, f'copia identica di {tieni} (sha256 {h[:12]})', peso(os.path.join(cartella, r))))
    # cartelle vuote, anche quelle che resterebbero vuote dopo aver tolto i candidati
    via = {c[0].rstrip('/') for c in out}
    for radice, dirs, files in os.walk(cartella, topdown=False):
        rel = os.path.relpath(radice, cartella)
        if rel == '.' or protetto(rel) or rel in via or any(rel.startswith(v + os.sep) for v in via):
            continue
        resto = [x for x in os.listdir(radice) if os.path.join(rel, x) not in via]
        if not resto:
            out.append((rel + '/', 'cartella vuota' if not os.listdir(radice) else 'cartella vuota dopo la pulizia', 0))
            via.add(rel)
    return sorted(out)


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: pulizia.py <libro> [--applica]')
    cartella = comune.trova_libro(args[0])
    c = candidati(cartella)
    applica = '--applica' in argv
    print(f'Libro: {cartella}')
    print(f'{"CANCELLO" if applica else "ELENCO (nessuna cancellazione)"}: {len(c)} elementi, '
          f'{leggibile(sum(x[2] for x in c))}')
    for rel, motivo, b in c:
        print(f'- {rel} — {motivo} — {leggibile(b)}')
    if not applica:
        if c:
            print('Per cancellare, dopo l\'«ok» dell\'autore: zb pulizia <libro> --applica')
        return 0
    for rel, _, _ in c:
        p = os.path.join(cartella, rel.rstrip('/'))
        if not comune.dentro(cartella, p) or os.path.realpath(p) == os.path.realpath(cartella):
            raise comune.ErroreMotore(f'Percorso fuori dal libro, non cancellato: {rel}')
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
    print('Cancellati. Salva con un commit (i file tracciati risultano tolti in git status).')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/push.py`

```python
"""Push del ramo corrente con ripiego (comando «zb push»).

Uso: push.py [--cartella <dir>] [--remoto origin] [--tentativi 4] [--attesa 2] [--bundle-dir <dir>]
1. git push -u <remoto> <ramo>, fino a --tentativi volte, con attesa crescente (2, 4, 8, 16 s);
2. se non riesce: push dello stesso commit su un ramo alternativo <ramo>-salvataggio-<data-ora>;
3. se non riesce neppure quello: git bundle del ramo in --bundle-dir (predefinito: la cartella temporanea
   di sistema, fuori dal repository), con percorso e sha256;
4. messaggio finale chiaro: dove sta il commit e se il ramo è allineato a <remoto>.
Codice d'uscita: 0 ramo allineato; 3 salvato solo sul ramo alternativo; 4 salvato solo nel bundle;
5 niente salvato. Non fa commit e non cambia ramo.
"""
import datetime
import hashlib
import os
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True


def opzione(argv, nome, predefinito):
    return argv[argv.index(nome) + 1] if nome in argv and argv.index(nome) + 1 < len(argv) else predefinito


def git(cartella, *args):
    p = subprocess.run(['git', '-C', cartella, *args], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def ultima_riga(testo):
    righe = [r for r in testo.splitlines() if r.strip()]
    return righe[-1] if righe else '(nessun messaggio)'


def main(argv):
    cartella = opzione(argv, '--cartella', os.getcwd())
    remoto = opzione(argv, '--remoto', 'origin')
    tentativi = int(opzione(argv, '--tentativi', '4'))
    attesa = float(opzione(argv, '--attesa', '2'))
    c, ramo = git(cartella, 'rev-parse', '--abbrev-ref', 'HEAD')
    if c or ramo == 'HEAD':
        print(f'FERMO: nessun ramo corrente in {cartella} ({ramo}).', file=sys.stderr)
        return 5
    _, commit = git(cartella, 'rev-parse', 'HEAD')
    errore = ''
    for i in range(1, tentativi + 1):
        c, out = git(cartella, 'push', '-u', remoto, ramo)
        if c == 0:
            _, sul_remoto = git(cartella, 'ls-remote', remoto, f'refs/heads/{ramo}')
            allineato = sul_remoto.split()[:1] == [commit]
            print(f'Push riuscito al tentativo {i}: {ramo} {commit[:7]} su {remoto}.')
            print(f'Ramo allineato a {remoto}: {"sì" if allineato else "no"}.')
            return 0 if allineato else 5
        errore = ultima_riga(out)
        print(f'Tentativo {i}/{tentativi} non riuscito: {errore}')
        if i < tentativi:
            secondi = attesa * 2 ** (i - 1)
            print(f'  attendo {secondi:g} s')
            time.sleep(secondi)
    alt = f'{ramo}-salvataggio-{datetime.datetime.now():%Y%m%d-%H%M%S}'
    c, out = git(cartella, 'push', remoto, f'HEAD:refs/heads/{alt}')
    if c == 0:
        print(f'PUSH NON RIUSCITO su {ramo} (ultimo errore: {errore}).')
        print(f'Il commit {commit[:7]} è salvato su {remoto}/{alt}. Ramo {ramo} allineato a {remoto}: no.')
        print(f'Quando {remoto} risponde: zb push (poi si può cancellare {alt}).')
        return 3
    errore_alt = ultima_riga(out)
    cartella_bundle = opzione(argv, '--bundle-dir', tempfile.gettempdir())
    os.makedirs(cartella_bundle, exist_ok=True)
    nome = os.path.basename(git(cartella, 'rev-parse', '--show-toplevel')[1]) or 'repo'
    percorso = os.path.join(cartella_bundle, f'{nome}-{ramo.replace("/", "_")}-{commit[:7]}.bundle')
    c, out = git(cartella, 'bundle', 'create', percorso, ramo)
    if c == 0 and os.path.isfile(percorso):
        sha = hashlib.sha256(open(percorso, 'rb').read()).hexdigest()
        print(f'PUSH NON RIUSCITO su {ramo} (ultimo errore: {errore}) né su {alt} ({errore_alt}).')
        print(f'Il commit {commit[:7]} è salvato nel bundle {percorso}')
        print(f'sha256 {sha}')
        print(f'Ramo {ramo} allineato a {remoto}: no. Il bundle sta nel container: si perde se la sessione finisce.')
        print(f'Per recuperarlo: git fetch {percorso} {ramo}:{ramo}')
        return 4
    print(f'PUSH NON RIUSCITO su {ramo} ({errore}), né su {alt} ({errore_alt}); bundle non creato '
          f'({ultima_riga(out)}).')
    print(f'Il commit {commit[:7]} esiste solo in {cartella}. Ramo {ramo} allineato a {remoto}: no.')
    return 5


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
```

### `motore/script/recinto.py`

```python
"""Controlla che i comandi del motore scrivano solo dentro il libro indicato (proposta B.9).

Uso: recinto.py [--radice <cartella motore>] [--extra "<comando con {libro}>"]
Per ogni mini-libro di prova: copia il mini-libro in una cartella temporanea,
fotografa il repository (percorsi, dimensioni, sha256, esclusa .git), esegue ogni
comando del motore sulla copia e confronta. Ogni file creato, cambiato o tolto
fuori dalla copia è un KO, con il nome del comando.
Eccezione dichiarata: «verifica KDP fatta» (kdp_verifica.py) può scrivere solo
dati/kdp.yaml e dati/verifiche-kdp.md; è riportata come eccezione, non come violazione.
"""
import hashlib
import os
import shlex
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

MINI_LIBRI = ('mini-libro', 'mini-libro-romance')
ECCEZIONE = ('kdp_verifica.py', ('dati/kdp.yaml', 'dati/verifiche-kdp.md'))


def comandi(motore):
    """Comandi del motore presenti in script/, con {libro} al posto della copia."""
    s = os.path.join(motore, 'script')
    elenco = [
        ('conta.py', 'conta.py {libro}'),
        ('conta.py --schermo', 'conta.py {libro} --schermo'),
        ('valida_profili.py', 'valida_profili.py'),
        ('separazione.py', 'separazione.py'),
        ('stile.py', 'stile.py {libro}'),
        ('continuita.py', 'continuita.py {libro}'),
        ('riciclo.py', 'riciclo.py {libro}'),
        ('capitolo.py 1', 'capitolo.py {libro} 1'),
        ('capitolo.py 2', 'capitolo.py {libro} 2'),
        ('capitolo.py 3', 'capitolo.py {libro} 3'),
        ('compila.py', 'compila.py {libro}'),
        ('impagina.py', 'impagina.py {libro}'),
        ('verifica_pdf.py', 'verifica_pdf.py {libro}'),
        ('pacchetto.py', 'pacchetto.py {libro}'),
        ('conformita_kdp.py', 'conformita_kdp.py {libro}'),
        ('kdp_verifica.py controlla', 'kdp_verifica.py controlla --simula-blocco'),
        ('kdp_verifica.py stato', 'kdp_verifica.py stato'),
        ('avvio.py', 'avvio.py {libro}'),
        ('adotta.py', 'adotta.py {libro}'),
        ('pulizia.py', 'pulizia.py {libro}'),
        ('ortografia.py', 'ortografia.py {libro}'),
        ('fase.py stato', 'fase.py {libro} stato'),
        ('revisione.py', 'revisione.py {libro} 02-bibbia/bibbia.md'),
        ('voce.py lista', 'voce.py lista'),
    ]
    return [(n, f'{sys.executable} {os.path.join(s, c.split()[0])} ' + ' '.join(c.split()[1:]))
            for n, c in elenco if os.path.isfile(os.path.join(s, c.split()[0]))]


def foto(base):
    out = {}
    for radice, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != '.git']
        for f in files:
            p = os.path.join(radice, f)
            try:
                with open(p, 'rb') as fh:
                    out[os.path.relpath(p, base)] = (os.path.getsize(p), hashlib.sha256(fh.read()).hexdigest())
            except OSError:
                pass
    return out


def differenze(prima, dopo):
    return sorted(set(k for k in set(prima) | set(dopo) if prima.get(k) != dopo.get(k)))


def main(argv):
    motore = comune.radice_motore()
    base = comune.radice_git(motore)
    if base == '/':
        base = os.path.dirname(motore)
    extra = None
    if '--extra' in argv:
        extra = argv[argv.index('--extra') + 1]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    violazioni, eccezioni, eseguiti = [], [], 0
    for nome in MINI_LIBRI:
        sorgente = os.path.join(motore, 'prove', nome)
        with tempfile.TemporaryDirectory(prefix='zb-recinto-') as tmp:
            copia = os.path.join(tmp, nome)
            shutil.copytree(sorgente, copia)
            lista = comandi(motore) + ([('kdp_verifica.py (extra)' if 'kdp_verifica.py' in extra else 'extra', extra)] if extra else [])
            for etichetta, cmd in lista:
                prima = foto(base)
                subprocess.run(shlex.split(cmd.replace('{libro}', copia)), env=env,
                               capture_output=True, text=True, cwd=tmp)
                eseguiti += 1
                diff = differenze(prima, foto(base))
                for d in diff:
                    rel_motore = os.path.relpath(os.path.join(base, d), motore).replace(os.sep, '/')
                    if etichetta.startswith(ECCEZIONE[0]) and rel_motore in ECCEZIONE[1]:
                        eccezioni.append(f'{etichetta} su {nome}: {d} (eccezione dichiarata)')
                    else:
                        violazioni.append(f'{etichetta} su {nome}: scrittura fuori dal libro: {d}')
    for e in eccezioni:
        print(f'ECCEZIONE {e}')
    if violazioni:
        print(f'KO recinto ({eseguiti} esecuzioni)')
        for v in violazioni:
            print(f'  - {v}')
        return 1
    print(f'OK recinto: {eseguiti} esecuzioni, nessuna scrittura fuori dal libro')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
```

### `motore/script/revisione.py`

```python
"""Mostra un documento o i documenti di un gate in blocchi (proposta C.1, C.6). Sola lettura.

Uso: python3 -B revisione.py <libro> <documento|gate> [N]
- <documento>: percorso relativo al libro (per esempio 02-bibbia/bibbia.md).
- <gate>: documenti | pagina_campione | primi_capitoli | lotto | controllo_fallito:
  tutti i documenti del gate, uno dopo l'altro.
- N: numero del blocco (predefinito 1).
Blocchi di circa 120 righe, tagliati a fine paragrafo. Ogni blocco si apre con
«<Titolo> — <documento> — Blocco N di M, righe X-Y — sha256 <12 caratteri>».
Testo puro, senza numeri di riga. Non scrive nulla: lo stato della revisione lo tiene fase.py.
"""
import hashlib
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

MISURA = 120
MARGINE = 40
DOCUMENTI = ['libro.yaml', '02-bibbia/bibbia.md', 'cronologia.yaml', '03-architettura/manuale-di-stile.md',
             '03-architettura/scaletta.md', '03-architettura/piano-parole.md']
PAGINA_CAMPIONE = '05-revisioni/pagina-campione.md'


def nome_report(nome):
    return f'{int(nome):02d}' if nome.isdigit() else nome.replace(' ', '-')


def unita_con_report(cartella, libro, nomi):
    """File delle unità indicate, ciascuna seguita dal suo report di capitolo.py."""
    trovate = dict(comune.unita(cartella, libro))
    out = []
    for n in nomi:
        n = str(n)
        if n not in trovate:
            raise comune.ErroreMotore(f'Unità «{n}» assente in 04-manoscritto')
        out.append(os.path.relpath(trovate[n], cartella))
        out.append(f'06-diagnostica/capitoli/{nome_report(n)}.md')
    return out


def documenti_del_gate(cartella, libro, stato, gate):
    if gate == 'documenti':
        return list(DOCUMENTI)
    if gate == 'pagina_campione':
        return [PAGINA_CAMPIONE]
    if gate == 'primi_capitoli':
        return unita_con_report(cartella, libro, ['1', '2', '3'])
    if gate == 'lotto':
        return unita_con_report(cartella, libro, (stato.get('lotto') or {}).get('capitoli') or [])
    if gate == 'controllo_fallito':
        return unita_con_report(cartella, libro, [str(stato.get('passo') or '').replace('capitolo ', '')])
    raise comune.ErroreMotore(f'Gate sconosciuto: {gate}')


def taglia(testo):
    """[(X, Y, testo)] con righe 1-based; ogni taglio cade dopo una riga vuota, se c'è entro MARGINE."""
    righe = testo.splitlines()
    out, inizio = [], 0
    while inizio < len(righe):
        fine = min(inizio + MISURA, len(righe))
        j = fine
        while j < len(righe) and j < inizio + MISURA + MARGINE and righe[j - 1].strip():
            j += 1
        if j < len(righe) and righe[j - 1].strip():
            j = fine                      # nessun fine paragrafo vicino: taglio a MISURA
        out.append((inizio + 1, j, '\n'.join(righe[inizio:j])))
        inizio = j
    return out or [(1, 0, '')]


def blocchi(cartella, documenti):
    """[(documento, X, Y, sha12, testo)] per tutti i documenti, in ordine."""
    out = []
    for rel in documenti:
        p = os.path.join(cartella, rel)
        if not os.path.isfile(p):
            raise comune.ErroreMotore(f'Documento mancante: {rel}')
        testo = open(p, encoding='utf-8').read()
        sha = comune.sha256_file(p)[:12]
        out += [(rel, x, y, sha, t) for x, y, t in taglia(testo)]
    return out


def impronta(cartella, documenti):
    """sha256 dell'insieme dei documenti (cambia se ne cambia uno)."""
    h = hashlib.sha256()
    for rel in documenti:
        h.update(rel.encode() + b'\0' + comune.sha256_file(os.path.join(cartella, rel)).encode())
    return h.hexdigest()[:12]


def mostra(titolo, b, n):
    rel, x, y, sha, testo = b[n - 1]
    return f'{titolo} — {rel} — Blocco {n} di {len(b)}, righe {x}-{y} — sha256 {sha}\n\n{testo}\n'


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2:
        raise comune.ErroreMotore('Uso: revisione.py <libro> <documento|gate> [N]')
    cartella, libro, _ = comune.carica_libro(args[0])
    cosa = args[1]
    n = int(args[2]) if len(args) > 2 and args[2].isdigit() else 1
    if os.path.isfile(os.path.join(cartella, cosa)):
        if not comune.dentro(cartella, os.path.join(cartella, cosa)):
            raise comune.ErroreMotore(f'Documento fuori dal libro: {cosa}')
        documenti = [cosa]
    else:
        stato = comune.leggi_yaml(os.path.join(cartella, 'stato.yaml')) if os.path.isfile(
            os.path.join(cartella, 'stato.yaml')) else {}
        documenti = documenti_del_gate(cartella, libro, stato, cosa)
    b = blocchi(cartella, documenti)
    if not 1 <= n <= len(b):
        raise comune.ErroreMotore(f'Blocco {n} inesistente: i blocchi sono {len(b)}')
    print(mostra(libro['titolo'], b, n))
    if n == len(b):
        print('Fine del documento. Scrivi ok o correggi: …')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/riciclo.py`

```python
"""Anti-riciclo a 7 parole (proposta C.2).

Uso: python3 -B riciclo.py <libro> [--schermo]
Per ogni unità cerca le sequenze di 7 parole uguali:
- al testo precedente del libro (testo_precedente, solo con modalita: riscrittura) → KO;
- alle unità precedenti dello stesso libro → AVVISO (una ripetizione può essere voluta).
Le parole si confrontano in minuscolo, senza la punteggiatura ai bordi. Le finestre
consecutive che combaciano formano un solo segmento, riportato con la riga d'inizio.
Le battute canoniche del manuale (03-architettura/manuale-di-stile.md, voce «Battute canoniche»:
le frasi tra «» delle righe che la seguono, più rientrate) sono escluse: le loro parole, nel testo
nuovo e in quello precedente, non combaciano con niente. I richiami di libro.yaml (stile.richiami_ammessi)
sono esclusi allo stesso modo, ma solo nel confronto tra unità dello stesso libro.
Report: <libro>/06-diagnostica/riciclo.md.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
from stile import risultato, tabella  # noqa: E402

N = 7
BORDI = '.,;:!?«»"()[]—–-…\''


def gettoni(testo):
    """[(parola_normalizzata, riga)] della prosa."""
    out = []
    for n, r in comune.righe_prosa(testo):
        for t in comune.parole(r):
            w = t.strip(BORDI).lower()
            if w:
                out.append((w, n))
    return out


MANUALE = os.path.join('03-architettura', 'manuale-di-stile.md')


def battute_canoniche(cartella):
    """Frasi tra «» della voce «Battute canoniche» del manuale, come liste di parole normalizzate."""
    import re
    p = os.path.join(cartella, MANUALE)
    if not os.path.isfile(p):
        return []
    righe = open(p, encoding='utf-8').read().splitlines()
    out, rientro, trovate = [], None, 0
    for r in righe:
        if rientro is not None and r.strip():
            if len(r) - len(r.lstrip()) <= rientro or r.lstrip().startswith('#'):
                if trovate:
                    break
                rientro = None       # la voce citata senza elenco sotto: si cerca la successiva
        if rientro is None:
            if re.search(r'(?i)battute canoniche', r) and not r.lstrip().startswith('#'):
                rientro = len(r) - len(r.lstrip())
            continue
        if not r.strip():
            continue
        trovate += 1
        for frase in re.findall(r'«([^»]+)»', r):
            parole = [w for w in (t.strip(BORDI).lower() for t in comune.parole(frase)) if w]
            if parole:
                out.append(parole)
    return out


def maschera(tok, canoniche):
    """Sostituisce le parole delle battute canoniche con segnaposto unici (non combaciano mai)."""
    parole = [w for w, _ in tok]
    via = set()
    for c in canoniche:
        k = len(c)
        for i in range(len(parole) - k + 1):
            if parole[i:i + k] == c:
                via.update(range(i, i + k))
    return [((None, id(tok), i), r) if i in via else (w, r) for i, (w, r) in enumerate(tok)]


def ngrammi(tok):
    return {tuple(w for w, _ in tok[i:i + N]) for i in range(len(tok) - N + 1)}


def segmenti(tok, insieme):
    """Segmenti di finestre consecutive presenti in `insieme`: [(riga, testo)]."""
    out, i = [], 0
    while i <= len(tok) - N:
        if tuple(w for w, _ in tok[i:i + N]) in insieme:
            j = i
            while j + 1 <= len(tok) - N and tuple(w for w, _ in tok[j + 1:j + 1 + N]) in insieme:
                j += 1
            out.append((tok[i][1], ' '.join(w if isinstance(w, str) else '…' for w, _ in tok[i:j + N])))
            i = j + N
        else:
            i += 1
    return out


def controlla_libro(cartella, libro):
    risultati = []
    canoniche = battute_canoniche(cartella)
    precedente = set()
    if libro.get('modalita') == 'riscrittura' and libro.get('testo_precedente'):
        precedente = ngrammi(maschera(gettoni(open(os.path.join(cartella, libro['testo_precedente']),
                                                   encoding='utf-8').read()), canoniche))
    richiami = [[w for w in (t.strip(BORDI).lower() for t in comune.parole(f)) if w]
                for f in (libro.get('stile') or {}).get('richiami_ammessi') or []]
    gia_scritti = set()
    for nome, p in comune.unita(cartella, libro):
        gt = gettoni(open(p, encoding='utf-8').read())
        tok = maschera(gt, canoniche)
        for riga, testo in segmenti(tok, precedente):
            risultati.append(risultato(nome, 'riciclo:testo_precedente', 'KO', riga, testo))
        # i richiami ammessi valgono solo tra unità dello stesso libro, non contro il testo precedente
        tok_int = maschera(gt, canoniche + richiami)
        for riga, testo in segmenti(tok_int, gia_scritti):
            risultati.append(risultato(nome, 'riciclo:unita_precedenti', 'AVVISO', riga, testo))
        gia_scritti |= ngrammi(tok_int)
    return comune.applica_eccezioni(risultati, libro)


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: riciclo.py <libro> [--schermo]')
    cartella, libro, _ = comune.carica_libro(args[0])
    risultati = controlla_libro(cartella, libro)
    righe = ['# Anti-riciclo a 7 parole', '', f'Libro: {libro["titolo"]}.', '']
    righe += tabella(risultati) if risultati else ['Nessuna sequenza di 7 parole ripetuta.']
    testo = '\n'.join(righe + [''])
    if '--schermo' in argv:
        print(testo)
    else:
        print('scritto', comune.scrivi(cartella, '06-diagnostica/riciclo.md', testo))
    return 1 if any(r['esito'] == 'KO' for r in risultati) else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/separazione.py`

```python
"""Controlla che il motore non contenga libri (proposta B.9).

Uso: separazione.py [--radice <cartella motore>]
Fallisce (codice 1, con file e riga) se:
1. sotto motore/ c'è un percorso con un segmento «libri», o un file identico
   (stesso sha256) a un file di una cartella di libro (con libro.yaml) fuori da motore/;
2. in un file di motore/ compare, come parola intera e senza distinguere le
   maiuscole, una voce di dati/nomi_vietati.txt (il file stesso è escluso);
3. in motore/ c'è un libro.yaml fuori da prove/mini-libro/, prove/mini-libro-romance/ e dal modello vuoto modelli/libro.yaml.
Eccezione: i font di stampa/font/ elencati in FONTI.yaml con lo sha256 registrato.
"""
import hashlib
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

AMMESSI_LIBRO_YAML = ('prove/mini-libro/libro.yaml', 'prove/mini-libro-romance/libro.yaml',
                      'modelli/libro.yaml')  # modello vuoto, usato solo come esempio commentato


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for blocco in iter(lambda: f.read(1 << 16), b''):
            h.update(blocco)
    return h.hexdigest()


def file_sotto(cartella, escludi=()):
    for radice, dirs, files in os.walk(cartella):
        dirs[:] = [d for d in dirs if d != '.git' and os.path.join(radice, d) not in escludi]
        for f in files:
            yield os.path.join(radice, f)


def font_ammessi(motore):
    p = os.path.join(motore, 'stampa', 'font', 'FONTI.yaml')
    if not os.path.isfile(p):
        return set()
    ok = set()
    for voce in comune.leggi_yaml(p) or []:
        for f in voce.get('file') or []:
            ok.add((os.path.join(motore, 'stampa', 'font', f['nome']), f.get('sha256')))
    return ok


def controlla(motore):
    errori = []
    motore = os.path.realpath(motore)
    file_motore = list(file_sotto(motore))
    rel = {p: os.path.relpath(p, motore) for p in file_motore}
    # 1a. segmento «libri»
    for p, r in rel.items():
        if 'libri' in r.split(os.sep):
            errori.append(f'{r}: percorso con un segmento «libri»')
    # 1b. copie di file di libri esterni
    base = comune.radice_git(motore)
    if base == '/':
        base = os.path.dirname(motore)
    cartelle_libro = set()
    for p in file_sotto(base, escludi=(motore,)):
        if os.path.basename(p) == 'libro.yaml':
            cartelle_libro.add(os.path.dirname(p))
    hash_libri = {}
    for c in cartelle_libro:
        for p in file_sotto(c):
            if os.path.getsize(p) > 0:
                hash_libri.setdefault(sha256(p), p)
    fonts = font_ammessi(motore)
    for p, r in rel.items():
        if os.path.getsize(p) == 0:
            continue
        h = sha256(p)
        if h in hash_libri and (p, h) not in fonts:
            errori.append(f'{r}: copia identica di {os.path.relpath(hash_libri[h], base)}')
    # 2. nomi vietati
    nv = os.path.join(motore, 'dati', 'nomi_vietati.txt')
    voci = []
    if os.path.isfile(nv):
        for riga in open(nv, encoding='utf-8'):
            riga = riga.strip()
            if riga and not riga.startswith('#'):
                voci.append(riga)
    if voci:
        regex = re.compile(r'(?i)(?<!\w)(' + '|'.join(re.escape(v) for v in voci) + r')(?!\w)')
        for p, r in rel.items():
            if os.path.realpath(p) == os.path.realpath(nv):
                continue
            try:
                righe = open(p, encoding='utf-8').read().splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for n, riga in enumerate(righe, 1):
                m = regex.search(riga)
                if m:
                    errori.append(f'{r}:{n}: nome vietato «{m.group(1)}»')
    # 3. libro.yaml fuori posto
    for p, r in rel.items():
        if os.path.basename(p) == 'libro.yaml' and r.replace(os.sep, '/') not in AMMESSI_LIBRO_YAML:
            errori.append(f'{r}: libro.yaml fuori dai mini-libri di prova')
    return errori


def main(argv):
    errori = controlla(comune.radice_motore())
    if errori:
        print('KO separazione')
        for e in errori:
            print(f'  - {e}')
        return 1
    print('OK separazione: nessun libro dentro motore/')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
```

### `motore/script/stile.py`

```python
"""Controlli di stile (proposta B.3, B.6, C.2).

Voci con solo_dialogo: true: ammesse solo nelle righe di dialogo (che cominciano con la
lineetta di lingue.yaml); ogni riga fuori dal dialogo che le contiene è KO.

Uso: python3 -B stile.py <libro> [N] [--schermo]
Per ogni unità (o solo la N): frase media e dialogo % (capitoli numerati; negli interludi
solo la frase media, come avviso),
voci con pattern (lista nera di base + voci del libro + divieti della voce, se libro.yaml ha «voce»), parole filtro, candidati
similitudine, vincoli per capitolo, nomi vietati prima di un punto del libro.
Voci ad ambito «libro»: contatore cumulato; non contano le unità in consentito_in_capitoli;
con conta_per: unita il tetto è sul numero di unità in cui la voce compare.
Ogni voce può avere escludi_pattern: le occorrenze che cadono dentro una sua corrispondenza non contano.
Esiti: KO (blocca) o AVVISO (da guardare). Report: <libro>/06-diagnostica/stile.md.
"""
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import voce  # noqa: E402

# «come l'» seguito da un verbo («a come l'aveva lasciata») vuol dire «in che modo»: non è una similitudine
SIMILITUDINE = re.compile(r"(?i)\bcome (un|una|uno|il|la|lo|i|gli|le|se)\b"
                          r"|\bcome l'(?!(?:ho|hai|ha|abbiamo|avete|hanno|avev\w*|avess\w*|avrebb\w*|avrà|avrei|"
                          r"abbia\w*|ebbe|ebbero|era|erano|è)\b)|\bsembrava\b|\bpareva\b")


def risultato(unita, controllo, esito, riga=None, dettaglio=''):
    return {'unita': unita, 'controllo': controllo, 'esito': esito, 'riga': riga, 'dettaglio': dettaglio}


def voci_del_libro(libro):
    """Lista nera di base + voci del libro + divieti della voce narrativa (banca-voci, modalità avviso)."""
    base = comune.leggi_yaml(os.path.join(comune.radice_motore(), 'dati', 'lista-nera.yaml'))
    return ((base.get('voci') or []) + (libro.get('voci') or []) + voce.divieti_del_libro(libro),
            base.get('parole_filtro') or [])


def metriche(testo, lingua):
    prosa = comune.righe_prosa(testo)
    tot = sum(len(comune.parole(r)) for _, r in prosa)
    dial = sum(len(comune.parole(r)) for _, r in prosa if r.lstrip().startswith(lingua['lineetta_dialogo']))
    unito = ' '.join(r.strip() for _, r in prosa)
    frasi = [f for f in re.split(r'(?<=[.!?…])\s+', unito) if comune.parole(f)]
    return {
        'parole': tot,
        'frasi': len(frasi),
        'frase_media': round(tot / len(frasi), 1) if frasi else 0.0,
        'dialogo_percento': round(100 * dial / tot, 1) if tot else 0.0,
    }


def occorrenze(prosa, pattern):
    rx = re.compile(pattern)
    return [(n, m.group(0)) for n, r in prosa for m in rx.finditer(r)]


def occorrenze_voce(prosa, v):
    """Occorrenze del pattern della voce, tolte quelle che cadono dentro un «escludi_pattern»
    (per esempio il fischio letterale del treno in una voce che conta il fischio morale)."""
    occ = []
    rx = re.compile(v['pattern'])
    ex = re.compile(v['escludi_pattern']) if v.get('escludi_pattern') else None
    for n, r in prosa:
        esclusi = [m.span() for m in ex.finditer(r)] if ex else []
        for m in rx.finditer(r):
            if not any(a <= m.start() < b for a, b in esclusi):
                occ.append((n, m.group(0)))
    return occ


def controlla_unita(nome, testo, profilo, libro, voci, filtro, lingua):
    out = []
    prosa = comune.righe_prosa(testo)
    met = metriche(testo, lingua)
    capitolo = nome.isdigit()
    if capitolo:
        a, b = profilo['frase_media']
        if not a <= met['frase_media'] <= b:
            out.append(risultato(nome, 'frase_media', 'KO', None, f'{met["frase_media"]} fuori da {a}-{b}'))
        a, b = profilo['dialogo_percento']
        if not a <= met['dialogo_percento'] <= b:
            out.append(risultato(nome, 'dialogo', 'KO', None, f'{met["dialogo_percento"]}% fuori da {a}-{b}%'))
        pf = profilo['parole_filtro']
        rx = r'(?i)(?<!\w)(' + '|'.join(re.escape(p) for p in filtro) + r')(?!\w)'
        n_filtro = len(occorrenze(prosa, rx))
        densita = 1000 * n_filtro / met['parole'] if met['parole'] else 0
        met['parole_filtro_per_1000'] = round(densita, 1)
        if densita > pf['massimo_per_1000_parole']:
            esito = 'KO' if pf['modalita'] in ('vieta', 'conta') else 'AVVISO'
            out.append(risultato(nome, 'parole_filtro', esito, None,
                                 f'{densita:.1f} ogni 1000 parole (massimo {pf["massimo_per_1000_parole"]})'))
        n_sim = len(occorrenze(prosa, SIMILITUDINE.pattern))
        met['candidati_similitudine'] = n_sim
        tetto = met['parole'] / profilo['similitudini_max_per_parole']
        if n_sim > tetto:
            out.append(risultato(nome, 'similitudini', 'AVVISO', None,
                                 f'{n_sim} candidati, tetto {tetto:.1f} (una ogni {profilo["similitudini_max_per_parole"]} parole)'))
    if nome.lower().startswith('interludio'):
        # negli interludi solo un avviso sulla frase media, con l'intervallo dei capitoli
        a, b = profilo['frase_media']
        if not a <= met['frase_media'] <= b:
            out.append(risultato(nome, 'frase_media', 'AVVISO', None, f'{met["frase_media"]} fuori da {a}-{b}'))
    for v in voci:
        if v.get('ambito') == 'libro':
            continue
        if v.get('consentito_in_capitoli') is not None and comune.in_elenco(nome, v['consentito_in_capitoli']):
            continue
        occ = occorrenze_voce(prosa, v)
        if not occ:
            continue
        if v.get('vietato_in_capitoli') and not comune.in_elenco(nome, v['vietato_in_capitoli']):
            continue
        if v.get('solo_dialogo'):
            # Ammessa solo nel discorso diretto: fuori dal dialogo è KO (una riga per riga di testo);
            # nel dialogo vale la modalità della voce.
            dialogo = {n for n, r in prosa if r.lstrip().startswith(lingua['lineetta_dialogo'])}
            fuori = sorted({n for n, _ in occ if n not in dialogo})
            out += [risultato(nome, f'voce:{v["id"]}:fuori_dialogo', 'KO', n, 'fuori dal discorso diretto')
                    for n in fuori]
            occ = [(n, t) for n, t in occ if n in dialogo]
            if not occ:
                continue
        mod = v['modalita']
        if mod == 'vieta':
            out += [risultato(nome, f'voce:{v["id"]}', 'KO', n, t) for n, t in occ]
        elif mod == 'conta':
            if len(occ) > v.get('massimo', 0):
                out.append(risultato(nome, f'voce:{v["id"]}', 'KO', occ[v.get('massimo', 0)][0],
                                     f'{len(occ)} occorrenze (massimo {v.get("massimo", 0)})'))
        else:
            if 'massimo' in v:
                if len(occ) > v['massimo']:
                    out.append(risultato(nome, f'voce:{v["id"]}', 'AVVISO', occ[v['massimo']][0],
                                         f'{len(occ)} occorrenze (massimo {v["massimo"]})'))
            else:
                out += [risultato(nome, f'voce:{v["id"]}', 'AVVISO', n, t) for n, t in occ]
    for vc in libro.get('vincoli_capitolo') or []:
        occ = occorrenze(prosa, vc['pattern'])
        if not occ:
            continue
        fuori = ((vc.get('consentito_in_capitoli') is not None and not comune.in_elenco(nome, vc['consentito_in_capitoli']))
                 or comune.in_elenco(nome, vc.get('vietato_in_capitoli')))
        if fuori:
            out += [risultato(nome, f'vincolo:{vc["id"]}', 'KO', n, t) for n, t in occ]
    for nv in libro.get('nome_vietato_prima_di') or []:
        occ = occorrenze(prosa, nv['pattern'])
        if comune.in_elenco(nome, nv.get('vietato_in')):
            per_riga = {}
            for n, t in occ:
                per_riga.setdefault(n, []).append(t)
            out += [risultato(nome, f'nome_vietato:{nv["nome"]}', 'KO', n, ', '.join(ts))
                    for n, ts in sorted(per_riga.items())]
        elif comune.in_elenco(nome, nv.get('obbligatorio_in')) and not occ:
            out.append(risultato(nome, f'nome_obbligatorio:{nv["nome"]}', 'KO', None, 'nome assente'))
    return met, out


def controlla_libro(cartella, libro, profilo):
    """{unità: (metriche, risultati)} con le voci ad ambito «libro» cumulate in ordine di lettura."""
    lingua = comune.lingue()[libro['lingua']]
    voci, filtro = voci_del_libro(libro)
    esiti = {}
    contatori = {}
    for nome, p in comune.unita(cartella, libro):
        testo = open(p, encoding='utf-8').read()
        met, out = controlla_unita(nome, testo, profilo, libro, voci, filtro, lingua)
        prosa = comune.righe_prosa(testo)
        for v in voci:
            if v.get('ambito') != 'libro':
                continue
            # nelle unità consentite la voce non si conta e non dà avviso
            if v.get('consentito_in_capitoli') is not None and comune.in_elenco(nome, v['consentito_in_capitoli']):
                continue
            occ = occorrenze_voce(prosa, v)
            if v.get('conta_per') == 'unita':
                occ = occ[:1]      # il tetto conta le unità in cui la voce compare, non le occorrenze
            for n, t in occ:
                contatori[v['id']] = contatori.get(v['id'], 0) + 1
                if contatori[v['id']] == v.get('massimo', 0) + 1:
                    esito = 'KO' if v['modalita'] in ('vieta', 'conta') else 'AVVISO'
                    out.append(risultato(nome, f'voce:{v["id"]}', esito, n,
                                         f'superato il massimo di {v.get("massimo", 0)} nel libro'))
        esiti[nome] = (met, comune.applica_eccezioni(out, libro))
    return esiti


def tabella(risultati):
    righe = ['| Unità | Controllo | Esito | Riga | Dettaglio |', '|---|---|---|---|---|']
    for r in risultati:
        righe.append(f'| {r["unita"]} | {r["controllo"]} | {r["esito"]} | {r["riga"] or "—"} | {r["dettaglio"]} |')
    return righe


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: stile.py <libro> [N] [--schermo]')
    cartella, libro, profilo = comune.carica_libro(args[0])
    esiti = controlla_libro(cartella, libro, profilo)
    scelta = [args[1]] if len(args) > 1 else list(esiti)
    righe = ['# Controlli di stile', '', f'Libro: {libro["titolo"]} — profilo: {libro["profilo"]}.', '',
             '| Unità | Parole | Frase media | Dialogo % |', '|---|---|---|---|']
    tutti = []
    for u in scelta:
        if u not in esiti:
            raise comune.ErroreMotore(f'Unità «{u}» inesistente')
        met, out = esiti[u]
        righe.append(f'| {u} | {met["parole"]} | {met["frase_media"]} | {met["dialogo_percento"]} |')
        tutti += out
    righe += ['', '## Esiti', ''] + (tabella(tutti) if tutti else ['Nessun KO e nessun avviso.']) + ['']
    testo = '\n'.join(righe)
    if '--schermo' in argv:
        print(testo)
    else:
        print('scritto', comune.scrivi(cartella, '06-diagnostica/stile.md', testo))
    return 1 if any(r['esito'] == 'KO' for r in tutti) else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/valida_profili.py`

```python
"""Valida i profili di genere di motore/profili/ (proposta B.2.2, B.6).

Uso: valida_profili.py [file.yaml ...]   (senza argomenti: tutti i profili)
Controlla: schema dati/profilo.schema.yaml; minimo <= media <= massimo;
somma di parole_per_atto = 1; min_su_media < max_su_media; chiusura tra i
valori ammessi; ogni valore con una fonte nel commento (es. «12 r. 22»,
«01-mercato r. 25») o la marca PROPOSTA, sulla riga o su una riga madre.
Esce con 1 al primo profilo non valido, indicando file e campo.
Alla fine elenca i campi per uso (dallo schema, chiave «uso»): controllati da uno script,
usati da nuovo.py per generare i documenti, informativi (non controllati da nessuno script).
"""
import glob
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

FONTE = re.compile(r'(\b\d{2}(-[a-z-]+)?\s+rr?\.\s*\d+|PROPOSTA)')


def controlla_fonti(testo, nome):
    """Ogni riga con un valore deve avere una fonte sulla riga o su una riga madre."""
    errori = []
    pila = []                                   # (rientro, ha_fonte)
    for n, riga in enumerate(testo.splitlines(), 1):
        if not riga.strip() or riga.lstrip().startswith('#'):
            continue
        rientro = len(riga) - len(riga.lstrip())
        corpo, _, commento = riga.partition('#')
        ha = bool(FONTE.search(commento))
        while pila and pila[-1][0] >= rientro:
            pila.pop()
        coperta = ha or any(h for _, h in pila)
        chiave_sola = re.match(r'^\s*[\w-]+:\s*$', corpo) is not None
        if not chiave_sola and not coperta and corpo.strip() != 'genere: ' + nome:
            errori.append(f'riga {n}: valore senza fonte né PROPOSTA: {riga.strip()}')
        pila.append((rientro, ha))
    return errori


def valida_profilo(percorso):
    nome = os.path.basename(percorso)[:-5]
    testo = open(percorso, encoding='utf-8').read()
    dati = comune.leggi_yaml(percorso)
    errori = comune.valida(dati, comune.carica_schema('profilo'), nome)
    if errori:
        return errori
    c = dati['capitoli']
    if not (c['minimo'] <= c['media'][0] and c['media'][1] <= c['massimo']):
        errori.append(f'{nome}.capitoli: serve minimo <= media <= massimo')
    if abs(sum(dati['parole_per_atto']) - 1) > 1e-9:
        errori.append(f'{nome}.parole_per_atto: la somma deve essere 1')
    if not c['coerenza']['min_su_media'] < c['coerenza']['max_su_media']:
        errori.append(f'{nome}.capitoli.coerenza: min_su_media deve essere minore di max_su_media')
    if dati['genere'] != nome:
        errori.append(f'{nome}.genere: deve coincidere con il nome del file')
    errori += [f'{nome}: {e}' for e in controlla_fonti(testo, nome)]
    return errori


def usi(schema=None, prefisso=''):
    """{campo: uso} dai campi dello schema dei profili che dichiarano «uso»."""
    schema = schema or comune.carica_schema('profilo')
    out = {}
    for k, s in (schema.get('campi') or {}).items():
        if 'uso' in s:
            out[prefisso + k] = s['uso']
        elif s.get('tipo') == 'mappa':
            out.update(usi(s, prefisso + k + '.'))
    return out


def main(argv):
    file = comune.argomenti(argv) or sorted(glob.glob(os.path.join(comune.radice_motore(), 'profili', '*.yaml')))
    for p in file:
        errori = valida_profilo(p)
        if errori:
            print(f'KO {os.path.basename(p)}')
            for e in errori:
                print(f'  - {e}')
            return 1
        print(f'OK {os.path.basename(p)}')
    u = usi()
    for uso, titolo in (('controllo', 'Campi controllati'), ('generazione', 'Usati da nuovo.py per i documenti'),
                        ('informativo', 'Informativi, non controllati')):
        print(f'{titolo}: {", ".join(k for k, v in u.items() if v == uso)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
```

### `motore/script/verifica_pdf.py`

```python
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
```

### `motore/script/voce.py`

```python
"""Voci narrative della banca-voci (comando «zb voce»). Sola lettura.

Uso: python3 -B voce.py lista
     python3 -B voce.py mostra <slug> [N]
     python3 -B voce.py verifica <slug>
La banca-voci è un repository separato, fuori dal motore: il percorso si legge solo da
ZB_BANCA_VOCI, mai scritto nel codice. Struttura attesa:
  indice.yaml                 voci: [{slug, nome, genere, stato: pronta | da_completare}]
  voci/<slug>/scheda.md       7 sezioni «## N. Titolo», nell'ordine di SEZIONI
  voci/<slug>/divieti.yaml    divieti: [{id, espressione | pattern, tipo, nota}]: espressioni vietate
                              della voce; stile.py le aggiunge alle voci del libro (modalità avviso)
- lista: le voci dell'indice, con genere e stato.
- mostra: la scheda in blocchi di circa 120 righe (come revisione.py); N predefinito 1.
- verifica: la voce è nell'indice, ha la scheda con le 7 sezioni e il campo «ambientazione:»
  nella sezione 7, divieti.yaml leggibile, stato «pronta». Codice 1 con l'elenco dei problemi.
  Le pagine d'esempio non sono richieste: la banca contiene solo schede.
Senza ZB_BANCA_VOCI, con una cartella senza indice.yaml o con una voce assente: FERMO (codice 2).
"""
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import revisione  # noqa: E402

SEZIONI = ['Nome e ruolo', 'Principi', 'Ritmo e sintassi', 'Lessico', 'Adattamento per genere',
           'Campione', 'Istruzione di esecuzione']
STATI = ('pronta', 'da_completare')


def banca():
    """Cartella della banca-voci da ZB_BANCA_VOCI; FERMO se manca o non è una banca."""
    p = os.environ.get('ZB_BANCA_VOCI', '').strip()
    if not p:
        raise comune.ErroreMotore('ZB_BANCA_VOCI non impostata: indica la cartella della banca-voci, per esempio\n'
                                  '  export ZB_BANCA_VOCI=<cartella della banca-voci>\n(motore/README.md, «Banca-voci»)')
    p = os.path.realpath(os.path.expanduser(p))
    if not os.path.isfile(os.path.join(p, 'indice.yaml')):
        raise comune.ErroreMotore(f'ZB_BANCA_VOCI={p}: nessun indice.yaml, non è una banca-voci.')
    return p


def indice(b):
    dati = comune.leggi_yaml(os.path.join(b, 'indice.yaml')) or {}
    voci = dati.get('voci') if isinstance(dati, dict) else None
    if not isinstance(voci, list) or not all(isinstance(v, dict) and v.get('slug') for v in voci):
        raise comune.ErroreMotore(f'{b}/indice.yaml: serve «voci:», una lista di voci con slug, nome, genere, stato.')
    return voci


def voce_in_indice(b, slug):
    for v in indice(b):
        if v['slug'] == slug:
            return v
    raise comune.ErroreMotore(f'Voce «{slug}» assente da {b}/indice.yaml. Elenco: zb voce lista')


def scheda(b, slug):
    return os.path.join(b, 'voci', slug, 'scheda.md')


def divieti(b, slug):
    """Voci di stile (modalità avviso) da voci/<slug>/divieti.yaml; FERMO se il file manca o non è valido."""
    p = os.path.join(b, 'voci', slug, 'divieti.yaml')
    if not os.path.isfile(p):
        raise comune.ErroreMotore(f'divieti.yaml assente: voci/{slug}/divieti.yaml')
    try:
        dati = comune.leggi_yaml(p) or {}
    except Exception as e:  # yaml non valido: messaggio, mai traceback
        raise comune.ErroreMotore(f'voci/{slug}/divieti.yaml non leggibile: {e}'.splitlines()[0])
    elenco = dati.get('divieti') if isinstance(dati, dict) else None
    if not isinstance(elenco, list) or not elenco:
        raise comune.ErroreMotore(f'voci/{slug}/divieti.yaml: serve «divieti:», una lista non vuota')
    out = []
    for i, d in enumerate(elenco):
        if not isinstance(d, dict) or not d.get('id') or not (d.get('espressione') or d.get('pattern')):
            raise comune.ErroreMotore(f'voci/{slug}/divieti.yaml: voce {i + 1} senza id o senza espressione/pattern')
        pattern = d.get('pattern') or r'(?i)(?<!\w)' + re.escape(str(d['espressione'])) + r'(?!\w)'
        try:
            re.compile(pattern)
        except re.error as e:
            raise comune.ErroreMotore(f'voci/{slug}/divieti.yaml: pattern non valido in «{d["id"]}»: {e}')
        out.append({'id': f'{slug}:{d["id"]}', 'espressione': d.get('espressione'), 'pattern': pattern,
                    'modalita': 'avviso', 'nota': d.get('nota') or f'divieto della voce {slug}'})
    return out


def divieti_del_libro(libro):
    """Divieti della voce scelta in libro.yaml; [] senza voce, senza ZB_BANCA_VOCI o con la voce non leggibile
    (lo segnala zb avvio con un AVVISO)."""
    v = libro.get('voce') or {}
    if not v.get('slug'):
        return []
    try:
        return divieti(banca(), v['slug'])
    except comune.ErroreMotore:
        return []


def sezioni(testo):
    """{numero: (titolo, corpo)} dei titoli «## N. Titolo»."""
    out, cur = {}, None
    for riga in testo.splitlines():
        m = re.match(r'^##\s+(\d+)\.?\s+(.*)$', riga)
        if m:
            cur = int(m.group(1))
            out[cur] = (m.group(2).strip(), [])
        elif cur is not None:
            out[cur][1].append(riga)
    return {n: (t, '\n'.join(c)) for n, (t, c) in out.items()}


def problemi(b, slug):
    """Elenco dei problemi della voce (vuoto se verifica). La voce deve essere nell'indice."""
    v = voce_in_indice(b, slug)
    out = []
    p = scheda(b, slug)
    if not os.path.isfile(p):
        out.append(f'scheda assente: voci/{slug}/scheda.md')
    else:
        sez = sezioni(open(p, encoding='utf-8').read())
        for i, nome in enumerate(SEZIONI, 1):
            if i not in sez:
                out.append(f'sezione {i} «{nome}» mancante')
            elif not sez[i][0].lower().startswith(nome.lower()):
                out.append(f'sezione {i}: titolo «{sez[i][0]}», atteso «{nome}…»')
        if 7 in sez and not re.search(r'(?im)^\W*ambientazione\s*:', sez[7][1]):
            out.append('sezione 7: manca il campo «ambientazione:»')
    try:
        divieti(b, slug)
    except comune.ErroreMotore as e:
        out.append(str(e))
    stato = v.get('stato')
    if stato not in STATI:
        out.append(f'stato «{stato}» non ammesso ({" | ".join(STATI)})')
    elif stato != 'pronta':
        out.append(f'voce non pronta (stato: {stato}): non si usa per scrivere finché non è completata')
    return out


def lista(b):
    voci = indice(b)
    print(f'Banca-voci: {b}')
    print('| Slug | Nome | Genere | Stato |')
    print('|---|---|---|---|')
    for v in voci:
        g = v.get('genere') or []
        print(f'| {v["slug"]} | {v.get("nome", "")} | {", ".join(g) if isinstance(g, list) else g} | {v.get("stato", "")} |')
    print(f'Voci: {len(voci)}, pronte: {sum(1 for v in voci if v.get("stato") == "pronta")}')
    return 0


def mostra(b, slug, n):
    v = voce_in_indice(b, slug)
    p = scheda(b, slug)
    if not os.path.isfile(p):
        raise comune.ErroreMotore(f'Scheda assente: {p}')
    pezzi = revisione.taglia(open(p, encoding='utf-8').read())
    if not 1 <= n <= len(pezzi):
        raise comune.ErroreMotore(f'Blocco {n} inesistente: i blocchi sono {len(pezzi)}')
    x, y, testo = pezzi[n - 1]
    if v.get('stato') != 'pronta':
        print(f'AVVISO: voce non pronta (stato: {v.get("stato")}).')
    print(f'Voce {slug} — voci/{slug}/scheda.md — Blocco {n} di {len(pezzi)}, righe {x}-{y} — '
          f'sha256 {comune.sha256_file(p)[:12]}\n\n{testo}\n')
    if n == len(pezzi):
        print('Fine della scheda.')
    return 0


def verifica(b, slug):
    out = problemi(b, slug)
    if out:
        print(f'KO voce {slug}')
        for x in out:
            print(f'  - {x}')
        return 1
    print(f'OK voce {slug}: 7 sezioni, {len(divieti(b, slug))} divieti, pronta')
    return 0


def main(argv):
    args = comune.argomenti(argv)
    uso = 'Uso: zb voce lista | zb voce mostra <slug> [N] | zb voce verifica <slug>'
    if not args or args[0] not in ('lista', 'mostra', 'verifica'):
        raise comune.ErroreMotore(uso)
    if args[0] != 'lista' and len(args) < 2:
        raise comune.ErroreMotore(uso)
    b = banca()
    if args[0] == 'lista':
        return lista(b)
    if args[0] == 'mostra':
        return mostra(b, args[1], int(args[2]) if len(args) > 2 and args[2].isdigit() else 1)
    return verifica(b, args[1])


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/stampa/font/EBGaramond-Italic.ttf`

> file binario (463492 byte): non copiabile come testo

### `motore/stampa/font/EBGaramond-Regular.ttf`

> file binario (518872 byte): non copiabile come testo

### `motore/stampa/font/EBGaramond-SemiBold.ttf`

> file binario (521860 byte): non copiabile come testo

### `motore/stampa/font/FONTI.yaml`

```yaml
# Fonti dei font di stampa (proposta B.2.3). Solo fonti ufficiali con licenza OFL.
# Mai copiare font da cartelle di libri. separazione.py ammette solo i file elencati qui,
# con lo sha256 registrato.
- nome: "EB Garamond"
  versione: "Version 1.003"            # letta dalla tabella «name» (nameID 5) dei file scaricati
  licenza: "SIL Open Font License 1.1"
  fonte: "https://raw.githubusercontent.com/google/fonts/main/ofl/ebgaramond/"
  pagina: "https://github.com/google/fonts/tree/main/ofl/ebgaramond"
  file_origine:
    - {nome: "EBGaramond[wght].ttf", sha256: "ef9512f92f6d579e5dc75af59a5a4b1b8b47d2eda89e00b954d44520e5369027"}
    - {nome: "EBGaramond-Italic[wght].ttf", sha256: "bba2c4499c93c9612b90b9825d32b07da52fce2fe57562a1eb6b833553f93c4e"}
  preparazione:                        # istanze statiche dal font variabile (evitano i font Type3 nel PDF)
    strumento: "fontTools 4.66.1 (fontTools.varLib.instancer), Python 3.11.15"
    data: 2026-10-02
    comando: |
      from fontTools.ttLib import TTFont
      from fontTools.varLib import instancer
      st = instancer.instantiateVariableFont(TTFont(ORIGINE), {"wght": PESO}, updateFontNames=False)
      for r in st["name"].names:            # nameID 2 e 17 = stile
          if r.nameID in (2, 17): st["name"].setName(STILE, r.nameID, r.platformID, r.platEncID, r.langID)
      st.save(DESTINAZIONE)
    istanze:
      - {origine: "EBGaramond[wght].ttf", peso: 400, stile: Regular, destinazione: EBGaramond-Regular.ttf}
      - {origine: "EBGaramond-Italic[wght].ttf", peso: 400, stile: Italic, destinazione: EBGaramond-Italic.ttf}
      - {origine: "EBGaramond[wght].ttf", peso: 600, stile: SemiBold, destinazione: EBGaramond-SemiBold.ttf}
    nota: "il nome PostScript (nameID 6) resta quello dell'origine: pdffonts elenca l'istanza SemiBold come EBGaramond-Regular"
  file:
    - {nome: EBGaramond-Regular.ttf, sha256: "44b42cc31b8d10ea172be333113173dec49f53ce720d2ea9ece66411f979cfec"}
    - {nome: EBGaramond-Italic.ttf, sha256: "c762787cbf8a4c7b2bfc9ff467e1cc39506198edcf8a1eae81d5b11a34025886"}
    - {nome: EBGaramond-SemiBold.ttf, sha256: "37c4fb678423e5967cd2081618404e95a38e9d5ad807d5ff9d3ca74613452115"}
    - {nome: OFL.txt, sha256: "0985066662eb755ed3683ae5482a81a9195b49ce3f7e165cc2388b3dbece7dd7"}
  licenza_file: OFL.txt
  scaricato_il: 2026-10-02
```

### `motore/stampa/font/OFL.txt`

```text
Copyright 2017 The EB Garamond Project Authors (https://github.com/octaviopardo/EBGaramond12)

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is copied below, and is also available with a FAQ at:
https://openfontlicense.org


-----------------------------------------------------------
SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007
-----------------------------------------------------------

PREAMBLE
The goals of the Open Font License (OFL) are to stimulate worldwide
development of collaborative font projects, to support the font creation
efforts of academic and linguistic communities, and to provide a free and
open framework in which fonts may be shared and improved in partnership
with others.

The OFL allows the licensed fonts to be used, studied, modified and
redistributed freely as long as they are not sold by themselves. The
fonts, including any derivative works, can be bundled, embedded, 
redistributed and/or sold with any software provided that any reserved
names are not used by derivative works. The fonts and derivatives,
however, cannot be released under any other type of license. The
requirement for fonts to remain under this license does not apply
to any document created using the fonts or their derivatives.

DEFINITIONS
"Font Software" refers to the set of files released by the Copyright
Holder(s) under this license and clearly marked as such. This may
include source files, build scripts and documentation.

"Reserved Font Name" refers to any names specified as such after the
copyright statement(s).

"Original Version" refers to the collection of Font Software components as
distributed by the Copyright Holder(s).

"Modified Version" refers to any derivative made by adding to, deleting,
or substituting -- in part or in whole -- any of the components of the
Original Version, by changing formats or by porting the Font Software to a
new environment.

"Author" refers to any designer, engineer, programmer, technical
writer or other person who contributed to the Font Software.

PERMISSION & CONDITIONS
Permission is hereby granted, free of charge, to any person obtaining
a copy of the Font Software, to use, study, copy, merge, embed, modify,
redistribute, and sell modified and unmodified copies of the Font
Software, subject to the following conditions:

1) Neither the Font Software nor any of its individual components,
in Original or Modified Versions, may be sold by itself.

2) Original or Modified Versions of the Font Software may be bundled,
redistributed and/or sold with any software, provided that each copy
contains the above copyright notice and this license. These can be
included either as stand-alone text files, human-readable headers or
in the appropriate machine-readable metadata fields within text or
binary files as long as those fields can be easily viewed by the user.

3) No Modified Version of the Font Software may use the Reserved Font
Name(s) unless explicit written permission is granted by the corresponding
Copyright Holder. This restriction only applies to the primary font name as
presented to the users.

4) The name(s) of the Copyright Holder(s) or the Author(s) of the Font
Software shall not be used to promote, endorse or advertise any
Modified Version, except to acknowledge the contribution(s) of the
Copyright Holder(s) and the Author(s) or with their explicit written
permission.

5) The Font Software, modified or unmodified, in part or in whole,
must be distributed entirely under this license, and must not be
distributed under any other license. The requirement for fonts to
remain under this license does not apply to any document created
using the Font Software.

TERMINATION
This license becomes null and void if any of the above conditions are
not met.

DISCLAIMER
THE FONT SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
OF COPYRIGHT, PATENT, TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL THE
COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
INCLUDING ANY GENERAL, SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL
DAMAGES, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF THE USE OR INABILITY TO USE THE FONT SOFTWARE OR FROM
OTHER DEALINGS IN THE FONT SOFTWARE.
```

### `motore/stampa/modello.css`

```css
/* Foglio di stile parametrico del motore (proposta B.2).
   impagina.py sostituisce i segnaposto {{…}} con i valori di libro.yaml e del calcolo
   del margine interno (max tra tabella KDP e margine scelto). Pagine dispari = destra (recto):
   margine interno a sinistra; pagine pari = sinistra (verso): margine interno a destra. */
@font-face { font-family: 'Libro'; font-style: normal; font-weight: 400; src: url('{{font_dir}}/EBGaramond-Regular.ttf'); }
@font-face { font-family: 'Libro'; font-style: italic; font-weight: 400; src: url('{{font_dir}}/EBGaramond-Italic.ttf'); }
@font-face { font-family: 'Libro'; font-style: normal; font-weight: 600; src: url('{{font_dir}}/EBGaramond-SemiBold.ttf'); }

@page { size: {{larghezza}}in {{altezza}}in; margin-top: {{alto}}mm; margin-bottom: {{basso}}mm; }
@page :right { margin-left: {{interno}}mm; margin-right: {{esterno}}mm; }
@page :left { margin-left: {{esterno}}mm; margin-right: {{interno}}mm; }

html { font-family: 'Libro', serif; font-size: {{corpo}}pt; line-height: {{interlinea}}; color: #111; }
body { margin: 0; }
p { margin: 0; text-indent: 1.2em; text-align: justify; hyphens: auto; orphans: 2; widows: 2; }
h1, h2, h3 { font-weight: 600; text-align: center; text-indent: 0; }
em, i { font-weight: 400; }

section { break-before: page; }
section:first-child { break-before: auto; }

.frontespizio h1 { font-size: 24pt; margin-top: 45mm; letter-spacing: .03em; }
.frontespizio h2 { font-size: 14pt; font-weight: 400; font-style: italic; margin-top: 4mm; }
.frontespizio h3 { font-size: 13pt; font-weight: 400; margin-top: 10mm; }
.copyright { padding-top: 95mm; font-size: 8.5pt; line-height: 1.4; }
.copyright p { text-indent: 0; text-align: left; hyphens: manual; margin-bottom: 3mm; }
.sommario h2 { font-size: 14pt; margin: 8mm 0 6mm; }
.sommario .voce { display: flex; align-items: baseline; font-size: 10.5pt; line-height: 1.5; }
.sommario .voce .punti { flex: 1; border-bottom: 1px dotted #999; margin: 0 .35em; transform: translateY(-.25em); }
.sommario .parte { margin-top: .8em; font-weight: 600; }
.parte h1 { font-size: 18pt; margin-top: 60mm; }
.capitolo h2, .prologo h2, .epilogo h2, .interludio h2 { font-size: 15pt; margin-top: 18mm; margin-bottom: 4mm; }
.interludio h2 { font-weight: 400; font-style: italic; }
.appendice h2 { font-size: 15pt; margin-top: 18mm; margin-bottom: 6mm; }
.capitolo h3, .prologo h3, .epilogo h3, .interludio h3, .appendice h3 { font-size: 12pt; margin: 7mm 0 3mm; }
.appendice p { text-indent: 0; margin-bottom: .6em; }
figure.immagine { margin: 4mm 0 0; text-align: center; break-inside: avoid; }
figure.immagine img { max-width: 100%; max-height: 150mm; }
figure.immagine figcaption { font-size: 9.5pt; font-style: italic; margin-top: 3mm; }
.capitolo h2 + p, .prologo h2 + p, .epilogo h2 + p { text-align: center; text-indent: 0; margin-bottom: 8mm; font-size: 10pt; }
p.scena { text-align: center; text-indent: 0; margin: .9em 0; letter-spacing: .3em; }
```

### `motore/stampa/print.js`

```javascript
// Render di un file HTML in PDF con Chromium (Playwright). Uso: node print.js <html> <pdf>
// Il formato della pagina e i margini vengono dal CSS (@page): preferCSSPageSize.
const { chromium } = require('playwright');
(async () => {
  const [html, pdf] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: pdf, preferCSSPageSize: true, printBackground: true });
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
```

### `motore/stampa/svg_png.js`

```javascript
// Conversione SVG → PNG con Chromium (Playwright), per le immagini delle appendici.
// Uso: node svg_png.js <svg> <png> [scala]. Le misure vengono da width/height (o viewBox) dell'SVG;
// scala predefinita 2 (una mappa larga 1240 px diventa 2480 px, circa 300 dpi su una pagina di 5,5").
const fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const [svg, png, s] = process.argv.slice(2);
  const testo = fs.readFileSync(svg, 'utf8');
  const radice = (testo.match(/<svg\b[^>]*>/) || [''])[0];
  const attr = (n) => { const m = radice.match(new RegExp('\\s' + n + '="([\\d.]+)')); return m ? parseFloat(m[1]) : null; };
  let w = attr('width'), h = attr('height');
  if (!w || !h) {
    const vb = (radice.match(/viewBox="([^"]+)"/) || [null, ''])[1].trim().split(/[\s,]+/).map(Number);
    if (vb.length === 4) { w = vb[2]; h = vb[3]; }
  }
  if (!w || !h) throw new Error('SVG senza width/height né viewBox: ' + svg);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: Math.ceil(w), height: Math.ceil(h) },
                                       deviceScaleFactor: parseFloat(s || '2') });
  await page.goto('file://' + svg, { waitUntil: 'networkidle' });
  await page.screenshot({ path: png, clip: { x: 0, y: 0, width: Math.ceil(w), height: Math.ceil(h) } });
  await browser.close();
})().catch((e) => { console.error(e.message || e); process.exit(1); });
```

### `motore/prove/attesi.yaml`

```yaml
# Esiti attesi delle prove del motore sui due mini-libri inventati (proposta B.2.2, B.7).
# Ogni passo aggiunge la sua sezione. Le prove girano su copie temporanee dei mini-libri.
#
# Errori voluti già presenti nei mini-libri, da verificare nei passi successivi:
#   mini-libro (giallo), cap. 2: «un brivido le percorse la schiena» (lista nera);
#     «come se» 6 volte (tetto 2 per capitolo); «Lodovico Arsa» prima del cap. 3;
#     intestazione «venerdì 4 marzo» (nel 2021 il 4 marzo è giovedì); «quarantadue anni»
#     per Irene Calvi (nel 2021 ne ha 35); «Brena» accanto a «Brenna»; chiusura dichiarata
#     X, prevista R in scaletta.
#   mini-libro (giallo), cap. 3: 457 parole (minimo 800); frase media oltre 14;
#     ultima riga di una parola.
#   capitolo-prova (giallo cap. 1 = romance cap. 3): circa 1.180 parole, frase media
#     circa 10, dialogo circa 30%: OK nel giallo, KO nel romance (minimo 1.500,
#     frase media 12-17, dialogo 35-55%); chiusure su domanda: tre di fila nel romance.

passo_1:
  profili:                       # valida_profili.py: tutti OK
    giallo: OK
    thriller: OK
    romance: OK
    narrativa-letteraria: OK
    fantasy: OK
    fantascienza: OK
    young-adult: OK
  profilo_senza_fonte: KO        # copia di un profilo con una riga senza fonte né PROPOSTA
  profilo_media_fuori: KO        # copia con media fuori da minimo/massimo
  libro_schema:                  # comune.carica_libro
    mini-libro: OK
    mini-libro-romance: OK
  rifiuti:                       # comune.carica_libro su copie modificate
    lingua_en: "Lingua «en» non supportata"
    lingua_mancante: "Lingua «None» non supportata"
    override_senza_motivo: "override senza motivo"
    profilo_cambiato_senza_override: "valore del profilo cambiato senza override"
    riscrittura_senza_testo_precedente: "obbligatorio con modalita: riscrittura"
  stato_schema:
    modello_valido: OK           # stato.yaml d'esempio della proposta C.1
    fase_mancante: KO
  # Conteggi calcolati con una pipeline di shell indipendente da conta.py:
  #   grep -v -E '^[[:space:]]*(#|<!--)' FILE | tr -s '[:space:]' '\n' | grep -c '[[:alnum:]]'
  #   (LC_ALL=C.UTF-8)
  conta:
    mini-libro:
      unita: {"1": 1186, "2": 832, "interludio I": 103, "3": 457}
      ordine: ["1", "2", "interludio I", "3"]
      totale: 2578
    mini-libro-romance:
      unita: {"1": 1581, "2": 1549, "3": 1183}
      ordine: ["1", "2", "3"]
      totale: 4313
  separazione:
    motore: 0                    # codice d'uscita su motore/
    nome_vietato_in_copia: 1     # copia di motore/ con una voce in nomi_vietati.txt presente in un file
    libro_yaml_fuori_posto: 1    # copia di motore/ con un libro.yaml fuori dai mini-libri
  recinto:
    comandi_del_motore: 0        # nessuna scrittura fuori dalla copia del mini-libro
    scrittura_messa_apposta: 1   # un comando di prova che scrive in motore/ viene rilevato
    scrivi_fuori_dal_libro: rifiutata   # comune.scrivi verso un percorso fuori dal libro

passo_2:
  # Esiti di capitolo.py su ogni unità (controllo|esito|riga), verificati sugli errori voluti di B.2.2.
  capitoli:
    mini-libro:
      "1":
        parole: 1186
        frase_media: 9.8
        dialogo: 29.5
        esiti:
          - "parole_totale|AVVISO|"     # totale previsto 2578 su 3000 (-14,1%), fuori da ±5% (correzione «totale»)
      "2":
        parole: 832
        frase_media: 9.7
        dialogo: 26.1
        esiti:
          - "dichiarazione:chiusura|AVVISO|"
          - "eta|AVVISO|27"            # «Irene Calvi aveva quarantadue anni»: imperfetto narrativo, attribuzione incerta → avviso (correzione continuita.py)
          - "giorno_settimana|KO|2"
          - "nome_due_grafie|AVVISO|5"
          - "nome_vietato:Lodovico Arsa|KO|25"
          - "nome_vietato:Lodovico Arsa|KO|43"
          - "nome_vietato:Lodovico Arsa|KO|55"
          - "nome_vietato:Lodovico Arsa|KO|65"
          - "parole_totale|AVVISO|"     # totale previsto 2578 su 3000 (-14,1%), fuori da ±5% (correzione «totale»)
          - "scena_minimo|KO|2"        # controllo delle scene (correzione «scene»): 340 parole, minimo 800
          - "scena_minimo|KO|37"       # 492 parole, minimo 800
          - "similitudini|AVVISO|"
          - "voce:brivido_schiena|KO|5"
          - "voce:come_se|KO|19"
      "interludio I":
        parole: 103
        frase_media: 12.9
        dialogo: 0.0
        esiti:
          - "parole_budget|AVVISO|"
          - "parole_totale|AVVISO|"     # totale previsto 2578 su 3000 (-14,1%), fuori da ±5% (correzione «totale»)
      "3":
        parole: 457
        frase_media: 45.3
        dialogo: 0.0
        esiti:
          - "dialogo|KO|"
          - "dichiarazione:chiusura|KO|7"
          - "frase_media|KO|"
          - "parole_budget|AVVISO|"
          - "parole_minimo|KO|"
          - "parole_totale|AVVISO|"     # totale previsto 2578 su 3000 (-14,1%), fuori da ±5% (correzione «totale»)
          - "scena_minimo|KO|2"        # 457 parole, minimo 800
    mini-libro-romance:
      "1":
        parole: 1581
        frase_media: 13.4
        dialogo: 39.1
        esiti:
          - "scene_numero|KO|"         # 1 scena, il profilo romance ne vuole 2-3
          - "tempo_relativo|AVVISO|15" # «tre settimane fa» dall'11 giugno: nessuna data al 21 maggio
      "2":
        parole: 1549
        frase_media: 13.2
        dialogo: 40.3
        esiti:
          - "scena_minimo|KO|83"       # seconda scena di 664 parole, minimo 800
      "3":
        parole: 1183
        frase_media: 9.8
        dialogo: 29.5
        esiti:
          - "dialogo|KO|"
          - "dichiarazione:chiusura|KO|"
          - "frase_media|KO|"
          - "parole_minimo|KO|"
          - "scene_numero|KO|"         # 1 scena, il profilo romance ne vuole 2-3
  capitolo_sotto_minimo:          # capitolo.py sul cap. 3 del giallo (457 parole, minimo 800)
    codice: 1
    controllo: "parole_minimo|KO"
  capitolo_prova:                 # stesso testo: cap. 1 del giallo e cap. 3 del romance
    giallo_ko: 0
    romance_ko: 5                 # 4 di stile e lunghezza + 1 scena sola (il romance ne vuole 2-3)
  riciclo:
    testo_precedente: 1           # segmenti KO nel cap. 1, con il suo primo paragrafo come testo precedente
    unita_precedenti: 1           # segmenti AVVISO nel cap. 3, dopo avervi copiato una frase del cap. 1
  lista_nera:
    voci: 19
    regex_valide: OK
  comandi:                        # codici d'uscita sulle copie; ogni comando scrive il suo report
    stile.py mini-libro: 1
    stile.py mini-libro-romance: 1
    continuita.py mini-libro: 1
    continuita.py mini-libro-romance: 0
    riciclo.py mini-libro: 0
    riciclo.py mini-libro-romance: 0
  solo_dialogo:                   # voce di prova {id: registro_prova, pattern: '(?i)\bregistro\b', modalita: conta,
                                  # massimo: 10, solo_dialogo: true} aggiunta a una copia del giallo
    righe_ko_cap_1: [17, 19, 39, 53, 69, 71, 103]   # righe di narrazione con «registro»
    righe_dialogo_ammesse: [79, 99]                 # righe di dialogo: nessun esito
  checklist_capitolo:             # sezione «Checklist manuale» nel report di capitolo.py
    tic: 4
  nome_obbligatorio:              # copia del giallo con obbligatorio_in: ["3"] per «Lodovico Arsa»
    esito_cap_3: "nome_obbligatorio:Lodovico Arsa|KO|"

passo_3:
  # PDF dei due mini-libri generati dal motore (compila.py + impagina.py), verificati con verifica_pdf.py.
  # Nessuno sha256 del PDF: cambia da un container all'altro a parità di versioni (Chromium di
  # Playwright 1.56.1, PyMuPDF 1.28.2, font di stampa/font/FONTI.yaml). Al suo posto la struttura:
  # pagine, formato uguale al trim KDP di libro.yaml, font tutti incorporati e nessun Type3, Title e
  # Author uguali a libro.yaml, testo estratto con PyMuPDF (spazi normalizzati: numero di parole e sha256).
  # Margini: atteso ±0,005" (TOLLERANZA_MARGINI in prove.py) e mai sotto il minimo KDP di dati/kdp.yaml.
  mini-libro:
    md_sha256: "2324fc633819fa46b08b111465e3a9ab5267327a131bf744593852d46a0a9daf"
    struttura: {pagine: 16, testo_parole: 2737, testo_sha256: "2d1a2829cd8c6cae6a3cc08bcacec22abf1706b8ce5d4af2acb7520fdc17fad2"}
    pagine: 16                    # 4 iniziali senza numero + 12 numerate
    metadati: {Title: "Prova di stampa", Author: "Autore di Prova"}
    margini:                      # minimi misurati (pollici), ±0,005; interno a sinistra sulle dispari, a destra sulle pari
      interno: 0.625
      esterno: 0.625
      alto: 0.798
      basso: 0.356
    soglie_kdp:                   # 16 pagine → prima fascia (24-150 pagine): 0,375"; esterni senza bleed 0,25"
      interno: 0.375
      esterno: 0.25
    sommario: {"Capitolo 1": 1, "Capitolo 2": 6, "La vetrina": 10, "Capitolo 3": 11}
    parole_per_pagina: 184.9
    esiti: []
    codice: 0
  mini-libro-romance:
    md_sha256: "f853e720bf4d8850b1e1f4caa79226724f7d1fc0b2b4d9cd112a17ac95dd2df4"
    struttura: {pagine: 23, testo_parole: 4555, testo_sha256: "f621d19fefde21f911750d40d85fe84cfc9b37f6051053c87baf279eb92d44bd"}
    pagine: 23                    # 4 iniziali + 19 numerate
    metadati: {Title: "Prova d'inchiostro", Author: "Autrice di Prova"}
    margini:                      # interno scelto 17 mm, esterno 16 mm: margini a specchio
      interno: 0.665
      esterno: 0.624
      alto: 0.798
      basso: 0.396
    soglie_kdp:
      interno: 0.375
      esterno: 0.25
    sommario: {"Capitolo 1": 1, "Capitolo 2": 8, "Capitolo 3": 15}
    parole_per_pagina: 205.8
    esiti: ["pagine_pari|AVVISO"]   # 23 pagine: numero dispari (avviso, da verificare su KDP)
    codice: 0
  bleed:                          # copia inventata del romance con formato.bleed: true (prove.py, bleed_pdf)
    soglia_esterno: 0.375         # minimo KDP del margine esterno con bleed (dati/kdp.yaml)
    margine_esterno: 0.75         # 0,625 senza bleed + 0,125 di bleed; ±0,005

passo_4:
  # conformita_kdp.py sui due mini-libri dopo compila, impagina e pacchetto, con la scheda inventata
  # di prove/pubblicazione/ e le conferme del modello (nessuna conferma data).
  # Sezione 11: i PDF hanno meno di 24 pagine, quindi KO per costruzione.
  mini-libri:
    mini-libro:
      codice: 1
      ko: [8, 9, 11, 13, 14, 15]
      avvisi: [6, 10, 11]          # editore «Independently published»; codice a barre; formato A5 non citato
      sezione_11_pagine: "16 pagine (minimo 24)"
    mini-libro-romance:
      codice: 1
      ko: [8, 9, 11, 12, 13, 14, 15]   # 12: ebook: true senza ebook.docx
      avvisi: [6, 7, 10, 11, 12]       # 7: «romanzo» ripete il sottotitolo; 11: pagine dispari; 12: Kindle Previewer
      sezione_11_pagine: "23 pagine (minimo 24)"
  tutto_ok:                       # giallo, PDF sintetico (pagine del PDF di prova ripetute, nessun testo aggiunto),
                                  # conferme di prove/pubblicazione/conferme-tutto-ok.yaml, verifica KDP del 2026-10-01
    pagine_pdf_sintetico: 32
    codice: 0
    ko: []
    avvisi: [6, 10]
  formato_confermato:             # sul percorso «tutto OK»: formato A5 non citato
    falso: {esito_11: OK, avviso_formato: "sì"}
    vero: {esito_11: OK, avviso_formato: "no"}
  formato_confermato_libro:       # campo in libro.yaml (formato.formato_confermato_kdp), con conferme-autore.yaml a true
    falso: {esito_11: OK, avviso_formato: "sì"}
    vero: {esito_11: OK, avviso_formato: "no"}
  scheda_modificata:              # copie della scheda del giallo con un solo errore ciascuna → sezione: esito
    parola_amazzonia: {sezione: 7, esito: OK}
    parola_kindle: {sezione: 7, esito: KO}
    descrizione_4001: {sezione: 4, esito: KO}
    url_nella_descrizione: {sezione: 4, esito: KO}
    otto_parole_chiave: {sezione: 7, esito: KO}
    autore_diverso: {sezione: 5, esito: KO}
  verifica:
    nulla: 2                      # codice d'uscita sul percorso «tutto OK» con ultima_verifica: null
    scaduta: 2                    # verifica del 2026-08-01, oggi 2026-10-02
  kdp_verifica:
    data_futura: 1
    data_malformata: 1
    data_valida: 0
    riga_kdp_yaml: "ultima_verifica: 2026-10-01"
    righe_registro: 1
    data_vecchia_avviso: sì
    promemoria_righe_numerate: 7
  recinto_eccezione:              # recinto.py su una copia di motore/ con «kdp_verifica.py fatta» come comando extra
    codice: 0
    eccezioni: 3                  # 1° mini-libro: dati/kdp.yaml e dati/verifiche-kdp.md; 2° mini-libro: solo
                                  # verifiche-kdp.md (stessa data: kdp.yaml resta identico)
  pacchetto:
    creati: 6
    seconda_esecuzione_creati: 0
    scheda_non_toccata: sì

passo_5:
  # Conduzione: nuovo, avvio, fase (gate), revisione, hook, zb, CLAUDE.md. Su copie temporanee
  # (repository git con un remoto locale), mai sul repository del motore.
  nuovo:
    codice: 0
    file: ['.gitignore', '00-progetto/briefing.md', '02-bibbia/bibbia.md', '03-architettura/manuale-di-stile.md',
           '03-architettura/piano-parole.md', '03-architettura/scaletta.md', 'LEGGIMI.md', 'cronologia.yaml',
           'libro.yaml', 'nomi_propri.txt', 'stato.yaml']
    fuori: []
    libro_valido: "sì"
    stato: "documenti / nessuno"
    capitoli: 30
    voci: ['come_se', 'all_improvviso', 'un_brivido_le_percorse_la_schiena']
    vincolo: ['1']
    gate: ['documenti', 'pagina_campione', 'primi_capitoli']
    esistente: "2 / intatto"
  briefing_incompleto:
    codice: 2
    mancano: ['Autore', 'Capitoli', 'Lunghezza', 'Idea']   # 9000 parole senza motivo: servono anche Capitoli e Motivo override
    creato: []
    avvio_libro: "2 / ['Autore']"
  avvio:
    codice: 0
    file_letti: 10
    git_status: pulito
    non_scrivibile: "2 / True"
    fuori_git: "2 / []"
    non_salvate: "2 / True"
    ramo: "2 / True"
  gate_documenti:
    ok_senza_gate: 2
    pronto: "documenti / documenti / blocco 1 di 6"
    ok_presto: "2 / True"
    ultimo_blocco: "True / True"
    correggi: "0 / 1 / documenti / documenti"
    ok_correzione_pendente: "2 / True"
    ok_documenti_cambiati: "2 / True"
    riparte: "True / 1"
    ok_non_salvati: "2 / True"
    stato: "0 / True"
    ok: "0 / pagina_campione / nessuno / 6 / 0"
    leggimi: "Fase: pagina_campione; gate in attesa: nessuno"
    avvio_dopo_ok: 0
    approvato_cambiato: "2 / True"
    gate_pagina: "pagina_campione / pagina_campione"
    ok_pagina: "0 / stesura / nessuno / capitolo 1"
  gate_configurabili:
    senza_gate_documenti: "0 / pagina_campione / nessuno / 6"
    lotto_attivo: "stesura / lotto"
    lotto_senza_gate: "stesura / nessuno / True"
  stesura:
    esito_1: "0 / 1 / stesura / nessuno"
    esito_2_primo: "1 / {'2': 1} / stesura / nessuno"
    esito_2_secondo: "1 / stesura / controllo_fallito"
    esito_3_gate_aperto: 2
    ok_controllo: "0 / stesura / nessuno / capitolo 3 / {}"
    primi_capitoli: "stesura / primi_capitoli"
    ok_lotti: "0 / 5 / 3 / stesura / chiusura"   # chiusura solo dopo l'esito dell'interludio I
    chiusura_incompleta: "2 / 7"
  modalita:
    senza_testo: "2 / ['Testo precedente']"
    libro_yaml: "riscrittura 01-originale/testo-precedente.md | nuovo assente"
    avvio_letti: "True | False"
    leggimi: "Modalità: riscrittura | Modalità: nuovo"
  claude_md:
    righe_max_30: "sì"
    nomi: []
    frasi: []
    frasi_obbligatorie: ['motore/PROCEDURA.md', 'LEGGIMI.md', 'zb avvio', 'Letto', 'manuale del libro',
                         'procedura del motore', 'skill', "proponi → l'autore approva → applica", 'Ramo',
                         'cartella del libro indicato', 'git status -sb', 'Non dire «fatto»']
  hook:
    scenari:
      Write: "avviso / 0"
      Edit: "avviso / 0"
      Write fuori dal manoscritto: "niente / 0"
      "1": "niente / 0"
      "2": "niente / 0"
      "3": "avviso / 0"
      "4": "niente / 0"
      "5": "avviso / 0"
      "6": "avviso / 0"
      "7": "niente / 0"
      "8": "niente / 0"
      "9": "avviso / 0"
      "10": "niente / 0"
      "11": "niente / 0"
      "12": "niente / 0"
      "13": "niente / 0"
      "14": "avviso / 0"
    con_marker: "niente / 0"
    compact_sessione: "True / 0"
    sessione_corrente: "sessione-prova / ignorata"
    blocco: {write: 2, fuori: 0, errore: "2 / 0"}
  zb_hook:
    attiva_senza_ok: "0 / assente"
    attiva_ok: "0 / True"
    disattiva: "0 / assente"
    disattiva_altrui: "2 / presente"
    settings_nel_repo: assente
  revisione:
    blocchi: ['1-126', '127-252', '253-270']
    ortografia: "1 / False"
    conta: 0

passo_5b:
  # zb adotta sul mini-libro inventato prove/mini-libro-adozione (bibbia, manuale, scaletta, un capitolo).
  codice: 0
  scritti: ['libro.yaml', 'cronologia.yaml', 'nomi_propri.txt', 'stato.yaml', '06-diagnostica/adozione.md']
  ricavati: 19
  non_ricavati: ['autore', 'formato (predefinito 5.5 x 8.5: da confermare)', 'copyright.fantasia (testo standard: da confermare)',
                 'documento mancante: 03-architettura/piano-parole.md']
  override: ['frase_media [8, 12] 03-architettura/manuale-di-stile.md:16']
  libro: "Il faro spento / narrativa-letteraria / 60000 / ['come_se', 'il_cuore_in_gola'] / [('Bice Orlandi', ['1-2'])]"
  valido: "no"
  cronologia: "2 / 3"
  nomi: ['Anselmo', 'Bice', 'Capo', 'Lanza', 'Orlandi', 'Porto', 'Riva', 'Sferra']
  stato_parziale: "documenti / nessuno / 1"
  seconda: "0 / 5 / []"
  completo: "True / documenti"
  fonte_autore: "00-progetto/briefing.md:4"
  riscrittura: "riscrittura 01-originale/vecchio-testo.md"
  vuota: "2 / []"

passo_6:
  struttura:
    cartelle: ['00-progetto', '01-originale', '02-bibbia', '03-architettura', '04-manoscritto', '05-revisioni', '05-appendici',
               '05-output', '06-diagnostica', '06-pubblicazione', '.zb']
    nuovo: ['00-progetto', '02-bibbia', '03-architettura']
    riscrittura: "0 / ['00-progetto', '01-originale', '02-bibbia', '03-architettura']"
    nuovo_con_originale: "2 / True / False"
    testo_altrove: "2 / True"
  pulizia:
    # 04-manoscritto/02-l-officina.md.tmp è messo apposta: il manoscritto non si tocca mai, quindi non compare.
    # 05-revisioni/ resta vuota dopo aver tolto la copia: è proposta anche lei.
    elenco: ['.zb/letto-vecchia', '05-output/libro-bozza.pdf', '05-output/libro-copia.pdf', '05-output/vuota/',
             '05-revisioni/', '05-revisioni/01-copia.md', '__pycache__/', '_build/']
    dry_run: "0 / [] / True"
    applica: ['.zb/letto-vecchia', '05-output/libro-bozza.pdf', '05-output/libro-copia.pdf', '05-revisioni/01-copia.md',
              '__pycache__/a.pyc', '_build/b.html', '05-output/vuota/', '05-revisioni/', '__pycache__/', '_build/']
    protetti: "True / True / True"
    dopo: 0

passo_7:
  # Hunspell it_IT; «Brena» è la seconda grafia messa apposta nel mini-libro giallo (passo 2).
  base:
    mini-libro: ['Brena']
    mini-libro-romance: []
  refusi:
    riga: "Irene trovò un errrore nel registo della farmacia e sedette accanto al banco. Anch'io sedevo nell'auto, dov'era l'officina."
    segnalate: ['Brena', 'errrore', 'registo']
    codice: 1
  livelli_senza_lt: "sì / no / sì"
  languagetool:
    segnalate: ['Brena', 'errrore', 'registo']
    livelli: "sì / sì / sì"

override_lunghezza:
  # Briefing inventato (giallo) con la lunghezza cambiata. Profilo giallo: formati 40.000-180.000;
  # capitoli minimo 800 (uguale al briefing: nessun override), media 1500-2500, massimo 3500.
  casi:
    senza_motivo: "Lunghezza: 9000"
    motivo_senza_capitoli: "Lunghezza: 9000\nMotivo override: libro di prova"
    sotto_minimo_assoluto: "Lunghezza: 900\nMotivo override: libro di prova\nCapitoli: 100 | 200-300 | 400"
    capitoli_senza_motivo: "Lunghezza: 60000\nCapitoli: 800 | 1000-1300 | 1800"
    motivo_e_capitoli: "Lunghezza: 9000\nMotivo override: libro di prova\nCapitoli: 800 | 1000-1300 | 1800"
  attesi:
    senza_motivo: "2 / ['Capitoli', 'Lunghezza'] / False"
    motivo_senza_capitoli: "2 / ['Capitoli'] / False"
    sotto_minimo_assoluto: "2 / ['Lunghezza', 'Scene'] / False"   # capitoli da 200-300 parole: una scena da 800 non ci sta
    capitoli_senza_motivo: "2 / ['Capitoli (media)', 'Capitoli (massimo)'] / False"
    motivo_e_capitoli:
      codice: 0
      # la lunghezza fuori profilo non è più un override su consigliata: va in parole.motivo_fuori_profilo
      override: ['capitoli.media [1000, 1300] True', 'capitoli.massimo 1800 True']
      capitoli: 8
      manuale: 3

scene:
  # Mini-libri: giallo scene 1-3 da 800-2500; romance 2-3 da 800-2500 (profili).
  romance_1_senza_override: "1 / ['scene_numero|KO']"
  romance_1_con_override: "0 / []"
  giallo_3_sotto_minimo: "1 / ['scena_minimo|KO']"
  giallo_1_sopra_massimo: "0 / ['scena_massimo|AVVISO']"
  override_senza_motivo: "2 / True"
  briefing:
    # Briefing inventato con «Genere: romance»; «Lunghezza: 60000» sostituita dal testo del caso.
    casi:
      capitoli_corti_senza_scene: "Lunghezza: 9000\nMotivo override: prova\nCapitoli: 800 | 1000-1300 | 1800"
      scene_senza_motivo: "Lunghezza: 60000\nScene: 1 | 400-1200"
      scene_con_motivo: "Lunghezza: 9000\nMotivo override: prova\nCapitoli: 800 | 1000-1300 | 1800\nScene: 1 | 400-1200"
    attesi:
      capitoli_corti_senza_scene: "2 / ['Scene']"
      scene_senza_motivo: "2 / ['Scene (numero)', 'Scene (lunghezza)']"
      scene_con_motivo: "0 / [('capitoli.scene_per_capitolo', [1, 1]), ('scene.lunghezza', [400, 1200])]"
  informativi: ['battiti', 'capitoli.coerenza', 'lista_nera', 'lunghezza_totale.consigliata', 'lunghezza_totale.parti_obbligatorie',
                'lunghezza_totale.parti_sopra', 'parole_per_atto', 'parole_per_pagina', 'scene.budget_interno', 'scene.sequel']
  controllati: ['capitoli.minimo', 'capitoli.scene_per_capitolo', 'capitoli.tolleranza_budget', 'capitoli.tolleranza_totale',
                'dialogo_percento', 'frase_media', 'parole_filtro', 'scene.lunghezza', 'similitudini_max_per_parole']

manuale_leggibile:
  # Manuale generato dal briefing inventato (giallo) e dalla sua variante con lunghezza fuori profilo.
  identificativi: []
  grammatica_errata: []
  vincolo: "- «Ugo Pelle» non compare nel capitolo 1."
  tetti: ['- Tetto: «come se» al massimo 2 per capitolo.', "- Tetto: «all'improvviso» al massimo 3 per libro.",
          '- Vietato: «un brivido le percorse la schiena».']
  dove_capitoli: ['nel capitolo 1', 'nei capitoli 1-3', 'nei capitoli 1, 4 e 6-8', 'in nessun capitolo']
  motivo_fuori_profilo: "sì / no"

checklist_capitolo:
  # Voce inventata aggiunta al libro.yaml di una copia del mini-libro giallo.
  voci: ['Il registro non si apre prima del capitolo 3']
  righe: ['| Il registro non si apre prima del capitolo 3 | [ ] |']
  non_valida: 2

continuita_eta_durate:
  # Testi inventati aggiunti al capitolo 1 di una copia del mini-libro giallo (cronologia: Irene Calvi
  # nata il 1985-06-10, Gemma Rosselli il 1999-09-02; capitolo 1 datato marzo 2021).
  frasi:
    passato_due_nomi: "Gemma ricordava che Irene, da quando aveva sei anni, voleva fare la farmacista."
    eta_sbagliata: "Gemma ha 34 anni e nessuna voglia di parlarne."
    senza_nome_prima: "— Ha trent'anni, — disse Gemma."
  attesi:
    passato_due_nomi: []
    eta_sbagliata: ['eta|KO']
    senza_nome_prima: ['eta|AVVISO']
  durate:
    # eventi aggiunti: a = 2021-01-01, b = 2021-02-11 (41 giorni), c = 2021-03-12 (70 giorni)
    sei_settimane_41_giorni: {da: a, a: b, valore: "sei settimane", tolleranza_giorni: 3, atteso: []}
    sei_settimane_70_giorni: {da: a, a: c, valore: "sei settimane", tolleranza_giorni: 3, atteso: ['durata|KO']}
    due_mesi_70_giorni: {da: a, a: c, valore: "due mesi", tolleranza_mesi: 1, atteso: []}
    cinque_mesi_70_giorni: {da: a, a: c, valore: "cinque mesi", tolleranza_mesi: 1, atteso: ['durata|KO']}
    un_anno_41_giorni: {da: a, a: b, valore: "un anno", tolleranza_anni: 0, atteso: ['durata|KO']}

correzioni_dopo_prova:
  # Correzioni dopo la prova romance (voci a-l). Copie temporanee del mini-libro giallo e del briefing inventato.
  c_creata: "True / []"
  c_vuota: "2 / nessuno"
  c_scritta: pagina_campione
  g_codici: [2, 2, 2, 0, 0]          # avvio fermo; riapprova senza motivo; documento invariato; riapprova; avvio OK
  g_registro: "['tolleranza cambiata su richiesta'] / True"
  d_righe:
    - "- Chiusura preferita: gancio_domanda. Sigle: D domanda, R rivelazione, P pericolo, X decisione."
    - "- Chiusura preferita: misto. Sigle: G gesto, O oggetto, B battuta, D domanda, R rivelazione."
  i_frasi:
    - "La stanza era uguale a come l'aveva lasciata."
    - "Rimise il vaso a come l'aveva messa la madre."
    - "La strada brillava come l'acqua del porto."
    - "Il silenzio tagliava come una lama."
  i_attesi: [0, 0, 1, 1]
  b_frasi:
    - "Lo teneva fermo come si fa con un cane."
    - "Rideva come quando da bambina correva in cortile."
  b_attesi: [0, 0]
  h_casi:
    senza_contesto: [null, "Le pagine erano tre, disse il tipografo."]
    contesto_assente: [["registro"], "Le pagine erano tre, disse il tipografo."]
    contesto_presente: [["registro"], "Nel registro le pagine erano tre."]
  h_attesi:
    senza_contesto: ['cifra:pagine_registro|AVVISO']
    contesto_assente: []
    contesto_presente: ['cifra:pagine_registro|KO']
  a_casi: {giorni_41: 41, giorni_70: 70}
  a_attesi:
    giorni_41: []
    giorni_70: ['cronologia|durata|KO']
  j_ordine: ['zb continuita', 'zb ortografia', 'zb compila', 'zb impagina', 'zb pdf', 'zb pacchetto', 'zb kdp']
  k_esito: "2 / 0 / primi_capitoli / 2578"
  # scritte 1186 + 832 + 103 = 2121; capitolo 3 (budget 900) non scritto; previsto 3021 su 4000
  l_avviso: "totale previsto 3021 parole su 4000 (-24.5%, tolleranza ±5%); scritte 2121. Budget residuo proposto: 1879 parole per 1 unità (3: 1879); è una proposta, nessun capitolo si accorcia o si allunga per evitare l'avviso"
  l_schermo: "True | True"

adozione_libri_esistenti:
  # Libro inventato «La torre di sale», in riscrittura, adottato con i suoi documenti (copie temporanee).
  briefing_libero: "# Note dell'autrice\n\nIdea libera, scritta prima del motore: una torre, il sale, due sorelle.\n"
  briefing_motore_incompleto: "# Briefing\n\nTitolo di lavoro: La torre di sale\n"
  vecchio: "# Vecchio testo\n\nUna riga del testo precedente.\n"
  manuale: "# Manuale di stile — La torre di sale\n\nAutore: Autrice Inventata\nGenere: narrativa-letteraria\nObiettivo: 60000 parole\n\n- frase media 10-13 parole per capitolo;\n- un ponte di riassunto al massimo 150 parole.\n"
  manuale_senza_titolo: "# Note di stile\n\nAutore: Autrice Inventata\nGenere: narrativa-letteraria\nObiettivo: 60000 parole\n"
  bibbia: "# Bibbia — La torre di sale\n\n**Ada Neri**, nata il 1990-01-02.\n"
  scaletta: "# Scaletta — La torre di sale\n\n| 1 | 2020-05-04 | la torre |\n"
  piano: "# Piano parole\n\n| Parte | Cap. | Titolo | Budget capitolo |\n|---|---|---|---|\n| — | 1 | La torre | 20000 |\n| — | 2 | Il sale | 20000 |\n| — | 3 | Le sorelle | 20000 |\n\nTotale: 60000.\n"
  capitoli: "[] / []"                       # «frase media 10-13» e «al massimo 150 parole» non diventano capitoli
  avvio_libero: "0 / True"
  avvio_motore: "2 / True"
  senza_titolo: "2 / True / True"
  con_titolo: "0 / La torre di sale / La torre di sale"

# Correzioni su interludi, impronte e grafie: (a) interludio in anticipo come AVVISO, mai FERMO;
# (b) misure del piano parole fuori dall'impronta, aggiornate da zb esito; (c) stato.yaml salvato prima
# di stampare; (d) parole a inizio frase escluse dal confronto con i nomi; (e) battute canoniche escluse
# dall'anti-riciclo.
correzioni_interludi_e_grafie:
  a_ordine: ['1', '2', 'interludio I', '3', 'interludio II']
  a_anticipo: ['interludio II dopo 9']
  a_comandi: "True / True / 0 / False"   # capitolo.py eseguito / AVVISO «in anticipo» / conta.py / nessun FERMO
  a_sconosciuto: "2 / True"
  b_impronta: "True / True"
  b_esito: "0 / ['| — | 1 | La farmacia | apertura | 1 | 1200 | 1200 | 1186 | -1,2% |'] / True"   # libro in italiano: virgola
  b_grezzo: "True / Totale previsto (prova): 2.578."   # sha256 grezzo + commit registrati prima delle impronte
  c_stato: "1 / capitolo 2"
  d_grafie: ['«Calvo» e «Calvi»']      # «Calvo» a inizio frase e dopo la lineetta: ignorato; a metà frase: segnalato
  e_riciclo: "1 / ['che la pioggia lava le strade ma non le colpe']"   # la battuta canonica non è più un KO

# zb correggi fuori dal gate (registra data, file, motivo, sha256 precedente) e passo che non scende.
correzioni_e_passo:
  a_libera: "0 / 04-manoscritto/01-la-farmacia.md / una riga in più / True / True / None"
  a_commit: "0 / True / True / True"
  a_rifiuti: "2 / 2 / 2"          # unità inesistente e istruzione senza «:» rifiutate; registrate restano 2
  b_passo: "0 / capitolo 3 / 2"   # prima della correzione il passo tornava a «capitolo 2»

# Voci ad ambito «libro» con consentito_in_capitoli e conta_per; frase media negli interludi; virgola nel piano parole.
unita_consentite_e_interludi:
  a_testi: ["Fischiò due volte, poi fischiò ancora.", "Un fischio lungo.", "Si sentì un fischio."]
  a_voci:
    per occorrenza: {id: fischio_prova, pattern: '(?i)\bfisch\w*', modalita: avviso, massimo: 1, ambito: libro}
    per unità: {id: fischio_prova, pattern: '(?i)\bfisch\w*', modalita: avviso, massimo: 1, ambito: libro, conta_per: unita}
    per unità con consentita la 2: {id: fischio_prova, pattern: '(?i)\bfisch\w*', modalita: avviso, massimo: 1, ambito: libro, conta_per: unita, consentito_in_capitoli: ["2"]}
    per unità con consentite 1-3: {id: fischio_prova, pattern: '(?i)\bfisch\w*', modalita: avviso, massimo: 1, ambito: libro, conta_per: unita, consentito_in_capitoli: ["1-3"]}
  a_attesi:
    per occorrenza: ['1|voce:fischio_prova|AVVISO']     # la seconda occorrenza, nella stessa unità
    per unità: ['2|voce:fischio_prova|AVVISO']          # seconda unità con la voce
    per unità con consentita la 2: ['3|voce:fischio_prova|AVVISO']
    per unità con consentite 1-3: []
  b_testi:
    frasi corte: "Piove. Esco. Torno. Chiudo la porta. Mi siedo."
    frasi giuste: "La sera la piazza resta vuota fino alla chiesa grande. Il fornaio abbassa la saracinesca per ultimo, senza fretta. Nella vetrina la croce verde è spenta da tre giorni."
  b_attesi:
    frasi corte: ['interludio I|frase_media|AVVISO']
    frasi giuste: []
  c_scarti: ['-1,2%', '+11,5%']

# La fase resta «stesura» finché mancano unità del piano; zb fase stesura; correggi segue le rinomine.
fase_stesura_e_rinomine:
  riga_epilogo: "| — | epilogo | Epilogo | chiusura | 1 | 300 | 300 | | |"
  testo_epilogo: "## *Epilogo*\n\nLa sera la piazza resta vuota fino alla chiesa grande. Il fornaio abbassa la saracinesca per ultimo, senza fretta. Nella vetrina la croce verde è spenta da tre giorni.\n"
  a_fasi: "0 / stesura / epilogo / 2 / 0 / chiusura"   # prima: chiusura subito dopo l'ultimo capitolo
  a_fuori_piano: 2
  b_codici: "2 / 0 / 2"
  b_registro: "chiusura / stesura / manca l'epilogo / ['interludio I', 'epilogo'] / stesura / interludio I"
  b_completo: "2 / chiusura"
  c_rinomina: "0 True / 0 True / 0 True"              # prima: sha256 precedente «—» (None)

# escludi_pattern; pattern generico «Non era/è X. Era/È Y.»; budget degli interludi; esito e correggi in chiusura.
correzioni_esclusioni_e_budget:
  a_testi: ["Si sentì il fischio del treno, lungo.", "Fischiò forte, una volta.", "Il fischio del treno di nuovo."]
  a_voci:
    ambito libro: {id: fischio_x, pattern: '(?i)\bfisch\w*', escludi_pattern: '(?i)\bfischio del treno\b', modalita: avviso, massimo: 0, ambito: libro, conta_per: unita}
    ambito capitolo: {id: fischio_x, pattern: '(?i)\bfisch\w*', escludi_pattern: '(?i)\bfischio del treno\b', modalita: conta, massimo: 0, ambito: capitolo}
  a_attesi:
    ambito libro: ['2|AVVISO']        # il fischio del treno (unità 1 e 3) non conta
    ambito capitolo: ['2|KO']
  b_pattern: '(?:\b[Nn]on (?:era|fu|è|sono|c''era|ci fu) [^.!?]{1,80}[.!?]\s+(?:Era|Fu|È|Sono|C''era|Ci fu)\b)'
  b_frasi:
    - "Non era la villa di Ardena. Era un'altra casa."
    - "Non è educazione. È la scatola sotto il letto."
    - "Non c'era rabbia. C'era la stanchezza."
    - "Non fu un caso. Fu una scelta."
    - "Non sono parole. Sono pietre."
    - "La sera non era fredda, e io tornai a casa."
    - "Era tardi. Non era il caso di parlare."
  b_attesi: [1, 1, 1, 1, 1, 0, 0]
  c_testi:
    corto: "La sera la piazza resta vuota fino alla chiesa grande. Il fornaio abbassa la saracinesca per ultimo."
    nel budget: "La sera la piazza resta vuota fino alla chiesa grande. Il fornaio abbassa la saracinesca per ultimo, senza fretta, e per qualche minuto l'odore del pane resta sospeso tra i portici. Poi resta solo la fontana, che parla da sola nel buio. Nella vetrina della farmacia la croce verde è spenta da tre giorni. Qualcuno ha lasciato sul gradino un mazzo di fiori bianchi, legato con uno spago da cucina. La pioggia li ha piegati, ma nessuno li ha portati via. Una donna passa con il cane, si ferma, guarda i fiori e la vetrina buia. Poi tira il guinzaglio e se ne va verso la chiesa, senza voltarsi, con il passo di chi ha fretta di rientrare prima che ricominci a piovere sulla piazza. Dietro di lei la fontana continua a parlare da sola, e nessuno la ascolta più fino al mattino."
  c_attesi:
    corto: ['AVVISO']
    nel budget: []
  d_chiusura: "0 / True / True / chiusura / controlli finali / 1"   # prima: esito rifiutato in chiusura

# Titoli dei capitoli in compila; tempi relativi, differenze d'età e fatti incompatibili in continuita;
# catena degli sha256 di più correzioni prima dello stesso commit; zb conta senza file; zb push.
# Testi inventati aggiunti a copie del mini-libro giallo (cap. 1 martedì 2 marzo 2021, cap. 2 giovedì
# 4 marzo, cap. 3 martedì 9 marzo; eventi 2020-12-25, 2021-02-28, 2021-03-01).
titoli_tempi_eta_push:
  a_intestazione: "## 1 — La farmacia"
  a_atteso: "1. La farmacia"
  a_con_titolo: "True | True"                          # prima: «Capitolo 1»
  a_senza_titolo: ["AVVISO: capitolo 2", "AVVISO: capitolo 3"]
  b_prove:
    due giorni prima (cap. 1): {testi: [null, "Irene ci pensava da due giorni prima, dal martedì."], atteso: []}
    sei giorni prima (nessuna data): {testi: [null, "Gemma l'aveva visto sei giorni prima, al forno."], atteso: ['2|AVVISO']}
    cinque giorni dopo (cap. 3): {testi: [null, "Cinque giorni dopo la sorella sarebbe tornata."], atteso: []}
    una settimana dopo (nessuna data): {testi: [null, "Una settimana dopo nessuno ne parlava più."], atteso: ['2|AVVISO']}
    due mesi fa (Natale, tolleranza 15 giorni): {testi: [null, "La lite era di due mesi fa."], atteso: []}
    tre mesi fa (nessuna data): {testi: [null, "La chiave era nuova di tre mesi fa."], atteso: ['2|AVVISO']}
    terza notte di sabato (giusto): {intestazioni: [null, "*Sorvegna — giovedì 4 – sabato 6 marzo*"], testi: [null, "La terza notte, il sabato, Irene non dormì."], atteso: []}
    seconda notte di sabato (giorno sbagliato): {intestazioni: [null, "*Sorvegna — giovedì 4 – sabato 6 marzo*"], testi: [null, "La seconda notte, il sabato, Irene non dormì."], atteso: ['2|AVVISO']}
    quinta mattina (oltre l'intestazione): {intestazioni: [null, "*Sorvegna — giovedì 4 – sabato 6 marzo*"], testi: [null, "La quinta mattina Irene tornò in farmacia."], atteso: ['2|AVVISO']}
  c_frasi:                                             # Irene ha 14 anni più di Gemma
    in più giusto: "Irene, con quattordici anni in più di Gemma, guidava piano."
    in più sbagliato: "Irene, con dieci anni in più di Gemma, guidava piano."
    in meno giusto: "Gemma, con quattordici anni in meno di Irene, guardava la strada."
    più grande di N anni: "Irene era più grande di quattordici anni rispetto a Gemma."
    N anni più giovane sbagliato: "Gemma era dodici anni più giovane di Irene."
    un solo nome: "Irene, con dieci anni in più, guidava piano."
  c_attesi:
    in più giusto: []
    in più sbagliato: ['1|AVVISO']
    in meno giusto: []
    più grande di N anni: []
    N anni più giovane sbagliato: ['1|AVVISO']
    un solo nome: []
  d_fatti:
    - {id: chiave_persa, a: {pattern: '(?i)\bchiave\b.*\bpersa\b', unita: ["1"]}, b: {pattern: '(?i)\bapr\w* con la chiave\b', unita: ["2-3"]}, nota: "la chiave persa non apre più niente"}
  d_prove:
    tutti e due: {testi: ["La chiave d'ottone era persa da giorni.", null, "Irene aprì con la chiave il retro."], atteso: ['3|AVVISO|True']}
    solo A: {testi: ["La chiave d'ottone era persa da giorni."], atteso: []}
    B fuori dalle sue unità: {testi: ["La chiave era persa. Irene aprì con la chiave il cassetto."], atteso: []}
  e_catena: "2 / True"                                 # prima: la seconda registrava lo sha256 di HEAD
  f_conta: "0 | 0 | True"                              # prima: scriveva 06-diagnostica/conteggio.md
  f_push: "ok: 0 0 / alternativo: 3 3 True / bundle: 4 3 1 True True"

# stile.eccezioni (AVVISO -> ECCEZIONE, KO invariato) e stile.richiami_ammessi (riciclo tra unità).
# La stessa frase inventata va in coda ai capitoli 1 e 3 del mini-libro giallo (cap. 3 sotto il minimo: KO).
eccezioni_e_richiami:
  frase: "Irene guardò la fontana della piazza sotto la pioggia di marzo."
  prove:
    senza niente: {atteso: "['AVVISO'] | ['KO']"}
    richiamo ammesso: {stile: {richiami_ammessi: ["la fontana della piazza sotto la pioggia di marzo"]}, atteso: "[] | ['KO']"}
    eccezione: {stile: {eccezioni: [{unita: "3", controllo: riciclo, motivo: "eco voluta"}, {unita: "3", controllo: parole_minimo, motivo: "prova: un KO non si scusa"}]}, atteso: "['ECCEZIONE'] | ['KO']"}

# Voci narrative (zb voce) sulla mini-banca inventata prove/banca-voci-prova/, blocco «voce» di libro.yaml,
# riga «Letto» di zb avvio, modello del briefing. Nessuna voce reale nel motore.
voce:
  lista: "0 / ['voce-di-prova|pronta', 'voce-incompleta|da_completare']"
  mostra: "0 / True / True"
  mostra_non_pronta: "0 / True"
  blocco_inesistente: "2 / False"
  verifica_pronta: "0 / OK voce voce-di-prova: 7 sezioni, 3 divieti, pronta"
  verifica_non_pronta: "1 / True / False"
  voce_assente: "2 / False"
  senza_variabile: "2 True False / 2 True False / 2 True False"
  senza_indice: "2 / True / False"
  rotture:
    divieti.yaml non leggibile: "1 / ['voci/voce-di-prova/divieti.yaml non leggibile: while parsing a flow node']"
    senza la sezione 4: "1 / ['sezione 4 «Lessico» mancante']"
    senza ambientazione: "1 / ['sezione 7: manca il campo «ambientazione:»']"
    scheda assente: "1 / ['scheda assente: voci/voce-di-prova/scheda.md']"   # al posto di «un solo esempio»: gli esempi non sono più richiesti
  ripristinata: 0
  libro_senza_voce: "0 0 / identica / False / False"
  briefing_voce: "Voce dalla banca: voce-di-prova\nAmbientazione: Borgo di Prova\n"
  blocco_voce: "{'slug': 'voce-di-prova', 'ambientazione': 'Borgo di Prova'}"
  libro_con_voce: "0 / True / True / 11 / 0"
  con_voce_senza_variabile: "0 / True / False"
  con_voce_non_pronta: "0 / True"
  schema_senza_slug: "True"
  aiuto: "True"
  sezioni_briefing: [storia, schede dei personaggi, luoghi ed epoca, regole del libro, voce scelta e ambientazione]
  modello_briefing: "[] / True / []"
  frase_divieti: "Dunque dunque, nella vecchia bottega Irene era oltremodo stanca."
  divieti_senza_voce: "[]"
  divieti_senza_banca: "[]"
  divieti_con_voce: "['voce:voce-di-prova:dunque_dunque|AVVISO', 'voce:voce-di-prova:oltremodo|AVVISO', 'voce:voce-di-prova:vecchia_bottega|AVVISO']"

recinto_libro:
  messaggio_motore: "è dentro motore/, che resta sempre pulito"
  messaggio_libri: "il ramo corrente è «motore», che non contiene mai un libro"
  dentro_motore: "2 / True / ['briefing.md']"
  ramo_motore: "2 / True / ['briefing.md']"
  hook: "2 True / 0 False"

appendici:
  # compila su mini-libro con le appendici di prove/appendici/ e un titolo interno «##» nel capitolo 2
  titolo_interno: "## L'indovinello della farmacia"
  dichiarate:
    - {titolo: "Le soluzioni di prova", file: soluzioni-prova.md}
    - {titolo: "La piantina di prova", file: piantina-prova.svg, didascalia: "La farmacia e l'officina."}
  sommario_coda: ['Capitolo 3', 'Le soluzioni di prova', 'La piantina di prova']
  titolo_compilato: ["### L'indovinello della farmacia"]
  titoli_appendici: ['## Le soluzioni di prova', '## La piantina di prova']
  avviso_non_dichiarato: ["AVVISO: 05-appendici/nota-in-piu.md non è dichiarato in libro.yaml (appendici): non entra nel libro."]
  immagine: "True / True"
  fermo_assente: "Appendice dichiarata in libro.yaml ma assente: 05-appendici/non-esiste.md"
```

### `motore/prove/banca-voci-prova/LEGGIMI.md`

```markdown
# Banca-voci di prova

Mini-banca inventata per le prove di `zb voce` e di `zb avvio` (sezione «voce» di `script/prove.py`).
Le voci, le frasi e i nomi sono inventati. La banca vera sta fuori dal motore (`ZB_BANCA_VOCI`).
```

### `motore/prove/banca-voci-prova/indice.yaml`

```yaml
# Indice della banca-voci di prova (inventata)
voci:
  - slug: voce-di-prova
    nome: Voce di prova
    genere: [giallo, narrativa_letteraria]
    stato: pronta
  - slug: voce-incompleta
    nome: Voce incompleta
    genere: [thriller]
    stato: da_completare
```

### `motore/prove/banca-voci-prova/voci/voce-di-prova/divieti.yaml`

```yaml
# Divieti della voce di prova (inventati): stile.py li aggiunge alle voci del libro, modalità avviso.
voce: voce-di-prova
divieti:
  - {id: dunque_dunque, espressione: "dunque dunque", tipo: tic, nota: "ripetizione da evitare"}
  - {id: vecchia_bottega, espressione: "vecchia bottega", tipo: cliché}
  - {id: oltremodo, espressione: "oltremodo", tipo: arcaismo}
```

### `motore/prove/banca-voci-prova/voci/voce-di-prova/scheda.md`

```markdown
# Voce di prova

## 1. Nome e ruolo

Voce di prova: narratore esterno, vicino a un solo personaggio per scena. Serve alle prove del motore.

## 2. Principi

- Ogni scena parte da un oggetto concreto.
- Il narratore non spiega i sentimenti: li mostra con un gesto.

## 3. Ritmo e sintassi

- Un periodo lungo, poi una frase breve che chiude.
- Dialoghi corti, senza verbi di dire elaborati.

## 4. Lessico guida e parole vietate

- Guida: parole della bottega, degli attrezzi, del tempo atmosferico.
- Vietate: «improvvisamente», «in qualche modo».

## 5. Adattamento per genere

- Giallo: più indizi materiali, meno paesaggio.
- Narrativa letteraria: più silenzi, meno trama.

## 6. Campione-modello breve

Il barattolo delle viti stava sul bancone da tre giorni, e nessuno lo aveva toccato perché nessuno
voleva ammettere di averlo lasciato lì. Ottavio lo spostò di un palmo. Poi lo rimise dov'era.

## 7. Istruzione di esecuzione

ambientazione: altro
Scrivi in terza persona, passato remoto. Un oggetto per scena, una frase secca in chiusura.
```

### `motore/prove/banca-voci-prova/voci/voce-incompleta/scheda.md`

```markdown
# Voce incompleta

## 1. Nome e ruolo

Voce incompleta: segnaposto per le prove.

## 2. Principi

DA COMPLETARE

## 3. Ritmo e sintassi

DA COMPLETARE

## 4. Lessico guida e parole vietate

DA COMPLETARE

## 5. Adattamento per genere

DA COMPLETARE

## 6. Campione-modello breve

DA COMPLETARE

## 7. Istruzione di esecuzione

ambientazione: altro
```

### `motore/prove/briefing/briefing-giallo.md`

```markdown
# Briefing

<!-- Briefing inventato per le prove del motore. -->

Titolo di lavoro: La chiave del forno
Autore: Autore di Prova
Lettore: lettore di gialli di provincia

## Idea (massimo 5 righe)
Un fornaio di un paese inventato sparisce la notte prima della festa patronale.
La sua chiave del forno viene trovata nella fontana.
Una vigilessa al primo incarico segue le tracce di farina.

## Tono e voce desiderati
Asciutto, con ironia di paese.

## Personaggi chiave
- Nadia Ferro — vigilessa — 29 anni — testarda, appunta tutto a matita
- Ugo Pelle — fornaio scomparso — 61 anni — debiti con il mulino

## Fatti canonici
- Il fornaio sparisce la notte del 14 agosto.

## Cose da non cambiare
- La chiave del forno è l'unico indizio del primo capitolo.

## Riferimenti
- Nessuno.

## Direttive

Genere: giallo
Modalità: nuovo
Testo precedente:
Lunghezza: 60000
Voce: terza persona, passato
Intestazione capitolo: Luogo — giorno e data
Separatore di scena: * * *
Formato: 5.5 x 8.5
Anni ammessi: 2019
Gate: documenti, pagina_campione, primi_capitoli
Tetti:
- come se | 2 | capitolo
- all'improvviso | 3 | libro
Vietati:
- un brivido le percorse la schiena
Vincoli:
- Ugo Pelle | vietato prima del 2
```

### `motore/prove/esiti/banca-voci-ripristino.md`

```markdown
# Banca-voci: ripristino dal bundle e cartelle «materiali»: esito

Data: 2026-10-13. Ramo motore, partendo da d4b4833.

## Ripristino

- Bundle caricato dall'autore: sha256 `9b9718fe…dada3b`, combacia. `git bundle verify`: storia completa.
- Clonato in `/home/user/banca-voci`, ramo `main`: due commit (eba0658, a22b018 = HEAD), due voci
  (`atkinson-2-0`, `ibrida-pasolini-camilleri`). Nessun file esistente modificato. Tolto il remote
  `origin` che puntava al file del bundle.
- `export ZB_BANCA_VOCI=/home/user/banca-voci` (scritto nella «Ripartenza» di `passaggio-di-consegne.md`).

## Cartelle «materiali» (nella banca, non nel motore)

Commit 896e7f4 nella banca: `voci/<slug>/materiali/LEGGIMI.md` per le due voci, un solo file per
cartella, che dice che lì l'autore mette, quando vuole, brani, interviste e scritti da cui ricavare la
voce, che nessuno li scrive al suo posto e che non vanno mai nel motore. `zb voce verifica` ignora la
cartella: entrambe le voci restano OK («7 sezioni, 60 divieti, pronta» e «7 sezioni, 90 divieti, pronta»).

Nuovo bundle (HEAD e `main` = 896e7f4), mandato all'autore come file:
sha256 `a5d3ad1d648d77cc3d8cdc7308a5d979a2d66b2a70df40cf5c42e77e7992bffe`.

## Motore

`zb voce` esiste già (fd404a8): la parte sul motore non è stata rifatta. Nessun file di codice o di
prova modificato.

## Suite

`ZB_LANGUAGETOOL=<scratchpad>/lt/lib ZB_BANCA_VOCI=/home/user/banca-voci python3 -B motore/zb prove`,
eseguita una volta: **454/454 OK**, 0 saltate. `separazione.py` OK, `recinto.py` OK (48 esecuzioni).
```

### `motore/prove/esiti/bleed.md`

```markdown
# Prova del bleed: esito

Data: 2026-10-13. Ramo motore, partendo da 57f262e.

## Correzione al motore

`impagina.py`: con il bleed, i numeri di pagina venivano centrati sulla pagina allargata (trim + bleed)
invece che sul trim, quindi non seguivano lo spostamento del contenuto. Ora stanno al centro del piede
del trim. Senza bleed i calcoli sono gli stessi di prima.

## Prova (`script/prove.py`, `bleed_pdf`, sezione «passo 3»)

Una copia inventata del romance con `formato.bleed: true`, confrontata con la stessa copia senza
bleed. 5 prove nuove:

| Prova | Atteso |
|---|---|
| formato = trim + bleed di `dati/kdp.yaml` | 5,625 × 8,75″ su tutte le pagine |
| pagine dispari: spostamento di ogni parola (dx, dy) | (0, 0,125″) |
| pagine pari: spostamento di ogni parola (dx, dy) | (0,125″, 0,125″) |
| soglia KDP del margine esterno con bleed | 0,375″ (`dati/kdp.yaml`) |
| margine esterno | 0,75″ ±0,005, mai sotto 0,375″ |

## Prova di regressione

Con `formato_esatto` modificato temporaneamente per ignorare il bleed, falliscono 4 prove su 5:
formato (5,5 × 8,5″), spostamenti delle pagine dispari e pari, margine esterno («0.625: fuori
tolleranza»). Resta OK solo la soglia KDP, che è un dato letto da `dati/kdp.yaml`. Poi il file è
stato ripristinato.

## Suite

**429/429 OK** (424 + 5), 0 saltate, 0 KO, con LanguageTool.
```

### `motore/prove/esiti/correzioni-dopo-prova.md`

```markdown
# Correzioni dopo la prova romance: resoconto

Prove: `zb prove` **356/356 OK** (20 nuove nella sezione `correzioni_dopo_prova`, 4 attesi di passo 2
aggiornati per il nuovo avviso sul totale); saltate 2 (LanguageTool, `ZB_LANGUAGETOOL` non impostata);
separazione OK; recinto OK (46 esecuzioni).

| Voce | Esito | Correzione |
|---|---|---|
| a | risolto | `continuita.py`: le durate di `cronologia.yaml` si confrontano con le date degli eventi anche senza testo (unità «cronologia»). |
| b | limite noto | «come si…», «come quando…» non contati: sono spesso «in che modo». In `PROCEDURA.md` (sezione 7, «Limiti noti») con l'effetto sul report: candidati e avviso «similitudini» possono stare sotto il vero. |
| c | risolto | All'ingresso nella fase `pagina_campione`, `fase.py` crea `05-revisioni/pagina-campione.md` vuota (solo titolo e nota nascosta); `zb pronto` la rifiuta finché è vuota. |
| d | risolto | Il manuale generato spiega le sigle: G gesto, O oggetto, B battuta, D domanda, R rivelazione, P pericolo, X decisione, I immagine. |
| g | risolto | Nuovo comando `zb riapprova <libro> <documento> <motivo>`: nuovo sha256 e commit, con data, motivo, sha256 e commit precedenti in `stato.yaml`. `zb avvio` lo indica quando si ferma. |
| h | risolto | Cifre: campo facoltativo `contesto` in `cronologia.yaml`; con il contesto KO solo nelle righe che lo contengono, senza contesto un numero diverso è AVVISO. |
| i | risolto | `stile.py`: «come l'» seguito da un verbo («a come l'aveva lasciata») non è una similitudine. |
| j | risolto | Ordine di chiusura: `zb pacchetto` prima di `zb kdp` in `fase.py`, `PROCEDURA.md` e `README.md`. |
| k | risolto | `zb esito` a un gate `primi_capitoli` o `lotto` con una correzione registrata: rifà i controlli del capitolo del gate e aggiorna le parole; il gate resta aperto. |
| l | risolto | `zb conta` e `zb capitolo`: totale previsto (scritte + budget delle unità non scritte) fuori da `tolleranza_totale` dà AVVISO con il budget residuo proposto; nessun capitolo si accorcia o si allunga da solo. |

## File

- Modificati: `script/fase.py`, `script/avvio.py`, `script/nuovo.py`, `script/stile.py`,
  `script/continuita.py`, `script/conta.py`, `script/capitolo.py`, `script/prove.py`, `zb`,
  `prove/attesi.yaml`, `modelli/cronologia.yaml`, `dati/struttura-libro.yaml`, `PROCEDURA.md`, `README.md`.
- Nuovo: `prove/esiti/correzioni-dopo-prova.md`.
```

### `motore/prove/esiti/formato-esatto.md`

```markdown
# Formato esatto delle pagine: esito

Data: 2026-10-13. Ramo motore, partendo da 48d0a22.

## Difetto

Chromium arrotonda il formato della pagina. Il mini-libro A5 (5,83 × 8,27″) usciva a 420 × 594,96 pt
(5,833 × 8,263″) invece di 419,76 × 595,44 pt. I formati multipli di 1/96″ (5,5 × 8,5″) erano già esatti.

## Correzione (`script/impagina.py`, `formato_esatto`)

- Dopo l'unione di pagine iniziali e corpo, e prima dei numeri di pagina, ogni pagina va al formato
  esatto: trim di `libro.yaml`, più `cartaceo.bleed_pollici` di `dati/kdp.yaml` se `bleed: true`
  (larghezza + 1 bleed, altezza + 2 bleed).
- Il contenuto non si scala. Una traslazione (`q … cm … Q`) attorno al contenuto lo tiene fermo
  rispetto all'angolo in alto a sinistra.
- MediaBox e CropBox coincidono e partono da 0, 0. TrimBox e BleedBox non si scrivono: il motore non
  li gestiva.
- Con il bleed il contenuto scende di un bleed e, sulle pagine pari (esterno a sinistra), si sposta di
  un bleed a destra. Provato su una copia del romance con `bleed: true`: 405 × 630 pt, spostamenti di
  9 pt. Nessuna prova della suite copre il bleed.

## Verifiche (PDF prima e dopo la correzione)

| | A5 (mini-libro) | 5,5 × 8,5″ (romance) |
|---|---|---|
| Formato | 419,76 × 595,44 pt su tutte le pagine | 396 × 612 pt |
| Scarto su MediaBox e CropBox | 0,00001 pt (precisione con cui il numero è scritto nel PDF) | 0 |
| Spostamento delle parole rispetto all'alto a sinistra | massimo 0,0001 pt | 0 |
| Testo, font incorporati, metadati | invariati | invariati |

I numeri di pagina restano ancorati al piede, come prima.

## Suite

**424/424 OK, 0 saltate, 0 KO** (con LanguageTool). I margini alto e basso del mini-libro restano
0,798 e 0,356: nessun atteso modificato.

## Prove di regressione (ripetute, ogni alterazione ripristinata)

| Alterazione | Esito |
|---|---|
| (a) romance, margine esterno +0,02″ | KO: «0.646: fuori tolleranza» |
| (b) romance, margine esterno 5 mm, atteso 0,198 | KO: «0.198: sotto il minimo KDP 0.25» |
| (c1) romance, una parola aggiunta | KO della struttura (testo diverso) |
| (c2) PDF del romance con un font non incorporato | font_non_incorporati: 1, quindi KO della struttura |
```

### `motore/prove/esiti/languagetool.md`

```markdown
# LanguageTool attivo nelle prove: esito

Data: 2026-10-13. Ramo motore, partendo da d4b6fa6.

## Ambiente

| Strumento | Esito |
|---|---|
| Java | OpenJDK 21.0.12.1 (già presente) |
| Maven | già presente |
| LanguageTool | 6.8, `languagetool-commandline` + `language-it` da Maven Central, 143 file, 240 MB, nello scratchpad (fuori dal repository) |
| PyMuPDF, markdown | assenti nel container nuovo; installati con pip (PyMuPDF 1.28.2) |
| Hunspell it_IT | assente nel container nuovo; installato con apt (`hunspell`, `hunspell-it`) |

## Le 2 prove saltate

`passo_7` in `script/prove.py`: «LanguageTool sui refusi inventati» e «LanguageTool: livello eseguito
nel report». Vengono saltate quando `ZB_LANGUAGETOOL` non è impostata, perché `ortografia.py` trova
i `.jar` solo tramite quella variabile.

Con `ZB_LANGUAGETOOL` impostata passano tutte e due: segnalate `['Brena', 'errrore', 'registo']`,
livelli «sì / sì / sì». Non è servito correggere né il motore né le prove.

## Modifiche

- `script/prove.py`: il motivo dello skip ora è «LanguageTool assente (ZB_LANGUAGETOOL non impostata)».
  In fondo all'output c'è una riga per ogni motivo, con il numero di prove saltate e le istruzioni di installazione.
- `README.md`: nuova sezione «Ambiente», con la sottosezione «LanguageTool» (metodo d'installazione).

## Esito della suite

- Con LanguageTool: **420/424 OK, 0 saltate, 4 KO**.
- Senza: 418/422 OK, 2 saltate (LanguageTool assente), 4 KO.

I 4 KO sono tutti del passo 3 e compaiono anche senza LanguageTool. Non dipendono da queste modifiche:

| Controllo | Atteso | Ottenuto |
|---|---|---|
| mini-libro: sha256 del PDF | cecd5860… | 3346029c… |
| mini-libro-romance: sha256 del PDF | 9e54c302… | 992a9603… |
| mini-libro-romance: margine interno | 0.665 | 0.667 |
| mini-libro-romance: margine esterno | 0.624 | 0.625 |

Cosa è stato verificato:

- Chromium (Playwright 1.56.1, chromium-1194), PyMuPDF 1.28.2, i font e il .md compilato sono
  gli stessi registrati nel passo 3.
- La differenza nasce già nel PDF prodotto da Chromium, prima di PyMuPDF.
- Non cambia con le versioni 3.8.2-3.11 di `markdown`, né installando `fontTools` e `brotli`.
- Due generazioni consecutive danno ancora lo stesso sha256.

Gli attesi del passo 3 (sha256 e margini al millesimo di pollice) dipendono dal container in cui
Chromium ha fatto il render. Non sono stati modificati: la decisione spetta all'autore.
```

### `motore/prove/esiti/passo-1.md`

```markdown
# Passo 1 — Fondamenta: esito

Data: 2026-10-02. Proposta di riferimento: `motore/proposta-motore.md` (approvata, commit 6821b44), B.7 passo 1.

## File creati

| File | Righe |
|---|---|
| script/comune.py | 312 |
| script/conta.py | 102 |
| script/valida_profili.py | 76 |
| script/separazione.py | 119 |
| script/recinto.py | 98 |
| dati/libro.schema.yaml | 130 |
| dati/profilo.schema.yaml | 73 |
| dati/stato.schema.yaml | 28 |
| dati/lingue.yaml | 7 |
| dati/nomi_vietati.txt | 3 (solo commenti) |
| profili/ (7 file) | 35-40 ciascuno |
| prove/mini-libro/ (giallo, 10 file) | capitoli: 109, 75, 7; interludio 3 |
| prove/mini-libro-romance/ (10 file) | capitoli: 123, 131, 109 |
| prove/attesi.yaml | 58 |

## Prove (35, tutte sui due mini-libri inventati)

| Script | Controllo | Atteso | Ottenuto | Esito |
|---|---|---|---|---|
| valida_profili.py | 7 profili | OK ×7 | OK ×7 | OK |
| valida_profili.py | profilo con valore senza fonte | KO | KO | OK |
| valida_profili.py | profilo con media oltre il massimo | KO | KO | OK |
| valida_profili.py | esecuzione su profili/ | 0 | 0 | OK |
| comune.py | libro.yaml giallo e romance contro lo schema | OK ×2 | OK ×2 | OK |
| comune.py | lingua: en / lingua mancante | rifiuto | rifiuto | OK |
| comune.py | override senza motivo | rifiuto | rifiuto | OK |
| comune.py | valore del profilo cambiato senza override | rifiuto | rifiuto | OK |
| comune.py | riscrittura senza testo_precedente | rifiuto | rifiuto | OK |
| stato.schema.yaml | esempio C.1 / senza fase | OK / KO | OK / KO | OK |
| conta.py | ordine delle unità (giallo, romance) | da attesi | uguale | OK |
| conta.py | parole per unità (7 unità) | da attesi | uguale | OK |
| conta.py | totale nel report: giallo 2578, romance 4313 | da attesi | uguale | OK |
| comune.py | scrivi fuori dal libro (assoluto e con ../) | rifiutata | rifiutata | OK |
| separazione.py | nome vietato in una copia di motore/ | 1 | 1 | OK |
| separazione.py | libro.yaml fuori dai mini-libri | 1 | 1 | OK |
| recinto.py | scrittura messa apposta in motore/ | 1 | 1 | OK |

I conteggi attesi sono calcolati con una pipeline di shell indipendente da conta.py (in testa ad attesi.yaml).

## Separazione e recinto su motore/

- separazione.py: OK, codice 0.
- recinto.py: OK, 8 esecuzioni (4 comandi × 2 mini-libri), nessuna scrittura fuori dal libro, codice 0.

## Scelte non scritte nella proposta

1. Schemi in un formato YAML proprio, con validatore in comune.py: nel container non c'è jsonschema.
2. conta.py esclude anche le righe di commento HTML (la riga nascosta `<!-- zb: … -->`), trattate come «note» (12-lunghezze r. 6). La riga d'intestazione in corsivo si conta.
3. Nomi dei file in 04-manoscritto: `prologo.md`, `NN-<slug>.md`, `interludio-<NUMERO>.md`, `epilogo.md`.
4. piano-parole.md si legge dalle colonne «Cap.» e «Budget capitolo» (formato di 12-lunghezze r. 62).
5. In valida_profili.py la fonte può stare sulla riga del valore o su una riga madre (per esempio `formati:` copre `breve`, `standard`…).
6. Gli script impostano `dont_write_bytecode`: senza, Python creerebbe `__pycache__` in motore/script, che recinto.py segnalerebbe come scrittura fuori dal libro.
7. recinto.py fotografa il repository che contiene motore/ (esclusa .git); ha l'opzione `--extra` per provare una scrittura messa apposta.
8. Ogni profilo ha due righe di commento in testa; il resto è copiato dalla proposta.
9. Il mini-libro giallo totalizza 2578 parole su 3000 (−14%), per effetto voluto del cap. 3 corto; conta.py lo segnala come fuori dal ±5%, senza KO (i KO di lunghezza sono del passo 2).
10. Il mini-libro romance ha `serie` ed `ebook: true`, per le prove del passo 4.
11. Lo script che esegue le prove non è tra i file del passo 1: le prove sono state eseguite da uno script fuori dal repository.

## Non fatto in questo passo

- Parole per pagina in conta.py: serve il PDF (passo 3).
- Controllo dell'esistenza di dati/lista-nera.yaml citata dai profili: il file è del passo 2.
```

### `motore/prove/esiti/passo-2.md`

```markdown
# Passi 1b e 2 — Prove ripetibili e controlli del testo: esito

Data: 2026-10-02. Proposta di riferimento: `motore/proposta-motore.md` (approvata), B.7 passo 2.

## Passo 1b (commit separato)

- `script/prove.py` («zb prove»): esegue tutte le prove dei passi presenti in `prove/attesi.yaml` su copie temporanee dei mini-libri, stampa la tabella e rilancia `separazione.py` e `recinto.py`; codice 0 solo se tutto è OK.
- `README.md`: regola «python3 -B», nomi dei file del manoscritto, comandi.
- Esito prima del passo 2: 35/35 OK.

## Passo 2: file

| File | Stato |
|---|---|
| dati/lista-nera.yaml | nuovo: 19 voci (05-critica rr. 19-20) + parole filtro (r. 21) |
| script/stile.py | nuovo |
| script/continuita.py | nuovo |
| script/riciclo.py | nuovo |
| script/capitolo.py | nuovo |
| script/comune.py | aggiunte funzioni di testo (righe di prosa, parole, dichiarazioni, elenchi di capitoli, tabelle) |
| script/prove.py | aggiunta la sezione passo_2 |
| script/recinto.py | aggiunti i comandi del passo 2 |
| prove/attesi.yaml | aggiunta la sezione passo_2 |
| prove/mini-libro/ | libro.yaml (riga_finale_min_parole: 3; obbligatorio_in vuoto), cronologia (assunzione a settembre 2017), bibbia e briefing allineati |

## Esito

**Prove: 83/83 OK** (35 del passo 1 + 48 del passo 2). separazione.py OK; recinto.py OK su 20 esecuzioni.

Errori voluti di B.2.2, tutti trovati:

| Mini-libro | Unità | Controllo | Esito |
|---|---|---|---|
| giallo | 2 | lista nera «un brivido le percorse la schiena» | KO |
| giallo | 2 | «come se» 6 volte (massimo 2) | KO |
| giallo | 2 | «Lodovico Arsa» prima del cap. 3 (4 righe) | KO |
| giallo | 2 | «venerdì 4 marzo»: nel 2021 è giovedì | KO |
| giallo | 2 | Irene Calvi «quarantadue anni», ne ha 35 | KO |
| giallo | 2 | «Brena» e «Brenna» | AVVISO |
| giallo | 2 | chiusura dichiarata X, prevista R | AVVISO |
| giallo | 3 | 457 parole, minimo 800 | KO |
| giallo | 3 | frase media 45,3, dialogo 0% | KO |
| giallo | 3 | ultima riga di una parola | KO |
| romance | 3 (capitolo-prova) | minimo 1.500, frase media 9,8, dialogo 29,5%, tre chiusure su domanda di fila | KO |
| giallo | 1 (capitolo-prova) | stesso testo | nessun KO |

## Scelte non scritte nella proposta

1. Frase media e dialogo % si controllano solo sui capitoli numerati, non su prologo, epilogo e interludi.
2. Le misure di stile escludono la riga d'intestazione in corsivo e i separatori; il conteggio delle parole del capitolo resta quello di conta.py.
3. Una frase finisce con «.», «!», «?» o «…» seguiti da uno spazio; il dialogo è una riga che comincia con la lineetta di lingue.yaml.
4. Anti-riciclo: le ripetizioni rispetto al testo precedente sono KO; quelle tra capitoli dello stesso libro sono AVVISO.
5. Chiusura dichiarata diversa dalla scaletta: AVVISO. Ultima riga troppo corta: KO solo se il libro dichiara `riga_finale_min_parole`.
6. Similitudini e tic dei gesti: solo AVVISO (il conteggio dei candidati non distingue le similitudini vere).
7. Nomi in due grafie: avviso per parole con la maiuscola di almeno 5 lettere, stessa iniziale e distanza di modifica 1 da un nome dell'elenco.
8. Età: controllata quando nella stessa frase ci sono un personaggio con data di nascita e «N anni».
9. Data di un'unità: dall'intestazione, altrimenti dalla colonna «Data» della scaletta.
10. «solo_dialogo» delle voci non è ancora applicato.

## Non fatto in questo passo

- Tic «meteo all'inizio del capitolo» e «domande retoriche in serie» (05 r. 20): non rilevabili con affidabilità; restano al controllo a vista.

## Le tre modifiche al mini-libro giallo (chiarimento del passo 2b)

| Modifica | Errore di prova che toglieva | Controllo che continua a esercitare |
|---|---|---|
| Assunzione di Gemma da giugno a settembre 2017 (cronologia.yaml e bibbia) | Con giugno, «tre anni, quasi quattro» (36 mesi dichiarati) contro 45 mesi calcolati superava la tolleranza di 6 mesi: dava un KO di durata nel cap. 1, che per B.2.2 deve passare tutti i controlli. | Il controllo `durata` gira ancora sul cap. 1: trova la frase, ricalcola dalle date (42 mesi) e la accetta al limite della tolleranza. La prova «cap. 1: 0 esiti» lo verifica. |
| `obbligatorio_in: ["3"]` diventa `[]` per «Lodovico Arsa» | Il cap. 3 non nomina Lodovico Arsa: dava un KO «nome_obbligatorio» non previsto tra gli errori voluti. | Il divieto prima del cap. 3 resta esercitato (4 KO nel cap. 2). Il ramo «obbligatorio» si prova dal passo 2b su una copia con `obbligatorio_in: ["3"]`: KO atteso nel cap. 3. |
| Briefing: «il nome del colpevole» diventa «il nome di Lodovico Arsa» | Nessun errore di prova: era un'incoerenza del testo, perché nella storia il colpevole è la sorella. | Nessun controllo cambia: la regola resta quella di `nome_vietato_prima_di` in libro.yaml. |
```

### `motore/prove/esiti/passo-2b.md`

```markdown
# Passo 2b — Rifiniture: esito

Data: 2026-10-02.

1. **solo_dialogo: implementato** in stile.py (non rifiutato dallo schema). Una voce con `solo_dialogo: true` è ammessa solo nelle righe di dialogo, cioè quelle che cominciano con la lineetta di lingue.yaml. Ogni riga di narrazione che la contiene è KO (`voce:<id>:fuori_dialogo`), e nel dialogo vale la modalità della voce. Prova: voce «registro» su una copia del giallo, con KO sulle 7 righe di narrazione del cap. 1 e nessun esito sulle 2 righe di dialogo.
2. **Checklist manuale nel report di capitolo.py**, con la casella «verificato dall'autore». Contiene i 4 tic che il motore non rileva (05-critica r. 20: meteo all'inizio, domande retoriche in serie, chiusure di paragrafo con morale, scena che finisce con una presa di consapevolezza) e le voci della bibbia toccate dal capitolo. Prova: 4 tic con casella nel report.
3. **Le tre modifiche al mini-libro giallo** sono spiegate in passo-2.md. In più c'è una prova del ramo `obbligatorio_in`, rimasto senza prova dopo la modifica.
4. **zb prove: 87/87 OK.** Le 83 prove di prima restano tutte OK; le 4 nuove sono solo_dialogo ×2, checklist e nome obbligatorio. separazione.py e recinto.py OK.
```

### `motore/prove/esiti/passo-3.md`

```markdown
# Passo 3 — Stampa: esito

Data: 2026-10-02. Proposta di riferimento: `motore/proposta-motore.md` (approvata), B.7 passo 3.

## Strumenti nel container

| Strumento | Esito |
|---|---|
| Chromium (Playwright) | /opt/pw-browsers/chromium-1194 |
| Playwright per Node | 1.56.1 (globale, /opt/node22/lib/node_modules); Node 22.22.2 |
| Playwright per Python | assente (non serve: il render usa Node) |
| PyMuPDF | 1.28.2 |
| pdftotext, pdffonts, pdfinfo | presenti (/usr/bin) |
| Hunspell | presente, dizionario it_IT |
| fontTools, brotli, markdown (Python) | presenti |

## Font

- EB Garamond, «Version 1.003», SIL Open Font License 1.1, scaricato il 2026-10-02 da https://raw.githubusercontent.com/google/fonts/main/ofl/ebgaramond/ (github.com risponde 403 dal proxy; raw.githubusercontent.com risponde 200).
- Istanze statiche Regular 400, Italic 400 e SemiBold 600, ricavate con fontTools dai file variabili. Sha256 delle origini e dei file in `stampa/font/FONTI.yaml`; licenza in `stampa/font/OFL.txt`.

## File

| File | Righe |
|---|---|
| script/compila.py | 102 |
| script/impagina.py | 176 |
| script/verifica_pdf.py | 199 |
| stampa/modello.css | 35 |
| stampa/print.js | 12 |
| stampa/font/ | FONTI.yaml, OFL.txt, 3 file .ttf |
| script/comune.py | + percorso_in_libro, nome_file, margini KDP |
| dati/libro.schema.yaml | + copyright.anno |
| prove/mini-libro*/libro.yaml | + copyright.anno: 2026 |
| script/prove.py, script/recinto.py, prove/attesi.yaml | + passo 3 |

## Esito

**zb prove: 127/127 OK** (87 dei passi 1-2b + 40 del passo 3). separazione.py OK; recinto.py OK su 26 esecuzioni.

| Mini-libro | Pagine | Margine interno min / soglia KDP | Esterno min | Font | Sommario | Parole per pagina |
|---|---|---|---|---|---|---|
| giallo | 16 (4 + 12) | 0,625" / 0,375" | 0,625" | incorporati, nessun Type3 | coincide | 184,9 |
| romance | 23 (4 + 19) | 0,665" / 0,375" | 0,624" | incorporati, nessun Type3 | coincide | 205,8 |

- Lo sha256 di ciascun PDF è fissato in attesi.yaml: due generazioni consecutive danno lo stesso valore.
- Parole per pagina misurate: 184,9 (giallo) e 205,8 (romance), contro 250 dei profili. I profili non sono stati modificati.
- Romance: 23 pagine, numero dispari, quindi AVVISO (atteso).

## Scelte non scritte nella proposta

1. Il render usa Playwright per Node, perché nel container non c'è Playwright per Python.
2. Font in .ttf statici, non woff2: PyMuPDF, che stampa i numeri di pagina, non legge il woff2.
3. Le pagine iniziali (frontespizio, copyright, sommario) si stampano senza numero e si completano a un numero pari con una pagina bianca, così il capitolo 1 comincia su una pagina dispari.
4. I numeri di pagina partono da 1 sulla prima unità del corpo e li stampa PyMuPDF al centro del piede: in Chromium il piè di pagina via CSS non funziona.
5. Margini a specchio con `@page :right / :left`: interno a sinistra sulle pagine dispari. Le misure sul romance (17 mm interno, 16 mm esterno) confermano che Chromium li applica.
6. Tabella KDP dei margini: dal passo 3b sta solo in dati/kdp.yaml, letta da comune.py. Sotto le 24 pagine vale la prima fascia (0,375").
7. I PDF sono resi deterministici: metadati senza date, nessun nuovo ID, font ridotti ai sottoinsiemi.
8. Nome del PDF: `<libro>/05-output/<titolo>.pdf`, con il titolo in minuscolo e i trattini.
9. Nuovo campo facoltativo `copyright.anno` in libro.yaml (fissato a 2026 nei mini-libri), per avere lo stesso .md anche a cavallo di un cambio d'anno.
10. L'istanza SemiBold conserva il nome interno «Regular»: pdffonts la elenca come EBGaramond-Regular. Non ha effetti sul PDF.

## Non fatto in questo passo

- Il minimo KDP di 24 pagine non si controlla qui: è un controllo di conformità (passo 4, sezione 11). I mini-libri ne hanno 16 e 23.
```

### `motore/prove/esiti/passo-3b.md`

```markdown
# Passo 3b — Rifiniture: esito

Data: 2026-10-02.

1. In passo-3.md ho corretto i numeri di righe: compila.py 102, impagina.py 176, verifica_pdf.py 199, modello.css 35, print.js 12.
2. In stampa/font/FONTI.yaml c'è ora il modo in cui sono state ricavate le istanze statiche: strumento e versione (fontTools 4.66.1, Python 3.11.15), comando, data (2026-10-02), elenco delle tre istanze e la nota sul nome PostScript.
3. La tabella KDP dei margini è stata spostata in dati/kdp.yaml (sezione `cartaceo`), che ora è l'unica fonte. comune.py non ha più valori propri e si ferma se il file o la sezione mancano.
4. zb prove: 127/127 OK; separazione.py e recinto.py OK.
```

### `motore/prove/esiti/passo-4.md`

```markdown
# Passo 4 — Pubblicazione: esito

Data: 2026-10-02. Proposta di riferimento: `motore/proposta-motore.md` (approvata), A.2-A.9 e B.7 passo 4.

## File

| File | Righe |
|---|---|
| dati/kdp.yaml | 82 (completato come A.2; la sezione margini era del passo 3b) |
| dati/verifiche-kdp.md | 8 (registro vuoto) |
| modelli/conferme-autore.yaml | 12 |
| script/conformita_kdp.py | 343 |
| script/kdp_verifica.py | 129 |
| script/pacchetto.py | 110 |
| prove/pubblicazione/ | scheda-giallo.md 30, scheda-romance.md 30, conferme-tutto-ok.yaml 10 (testi inventati) |
| script/comune.py | + oggi() (data fissabile con --oggi o ZB_OGGI) |
| script/recinto.py | + pacchetto, conformita_kdp, kdp_verifica controlla/stato; etichetta dell'eccezione |
| script/prove.py, prove/attesi.yaml, README.md | + passo 4 |

## Esito

**zb prove: 163/163 OK** (127 dei passi 1-3b + 36 del passo 4). separazione.py OK; recinto.py OK su 34 esecuzioni.

Alla prima esecuzione 3 prove su 163 erano KO. Ciascuna ha avuto una sola correzione mirata:
1. `avviso_formato: no` in attesi.yaml veniva letto da YAML come «falso»: scritto tra virgolette.
2. La prova di ultima_verifica confrontava la riga con il commento finale compreso: ora confronta solo il valore.
3. L'eccezione di recinto.py compare 3 volte, non 4: alla seconda esecuzione, con la stessa data, dati/kdp.yaml resta identico e cambia solo il registro. Corretto il valore atteso.

| Prova | Atteso | Ottenuto |
|---|---|---|
| giallo, conferme non date | KO nelle sezioni 8, 9, 11, 13, 14, 15; codice 1 | uguale |
| romance, conferme non date | KO nelle sezioni 8, 9, 11, 12, 13, 14, 15; codice 1 | uguale |
| sezione 11 per costruzione | «16 pagine (minimo 24)» / «23 pagine (minimo 24)» | uguale |
| tutto OK (PDF sintetico di 32 pagine, conferme date, verifica del 2026-10-01) | nessun KO, codice 0 | uguale |
| formato_confermato_kdp false / true | sezione 11 OK con avviso / OK senza avviso | uguale |
| «Amazzonia» / «Kindle» nelle parole chiave | sezione 7 OK / KO | uguale |
| descrizione di 4.001 caratteri; URL nella descrizione | sezione 4 KO | uguale |
| 8 parole chiave | sezione 7 KO | uguale |
| autore della scheda diverso dal PDF | sezione 5 KO | uguale |
| ultima_verifica nulla / scaduta | codice 2 | uguale |
| kdp_verifica: data futura, data scritta male | rifiutate (codice 1) | uguale |
| kdp_verifica: data valida | ultima_verifica scritta, 1 riga nel registro | uguale |
| kdp_verifica: data già scaduta | accettata con avviso | uguale |
| promemoria con il proxy bloccato | 7 righe numerate | uguale |
| recinto.py con «verifica KDP fatta» | eccezione dichiarata, codice 0 | uguale |
| pacchetto.py | 6 file; alla seconda esecuzione nessuno; scheda non toccata | uguale |

## Scelte non scritte nella proposta

1. Codici d'uscita di conformita_kdp.py: se c'è un KO vale 1, anche con la verifica scaduta; il codice 2 vale solo senza KO.
2. «n/a» e «nessuno» stanno in `valori_vuoti_vietati` (KO solo se sono l'intero valore), separati da `parole_vietate`.
3. La scheda Amazon ha un formato fisso, letto da conformita_kdp.py: righe «Campo: valore», poi le sezioni «## Descrizione», «## Parole chiave» e «## Categorie» con elenchi numerati.
4. Sezione 12: con `ebook: true` manca ebook.docx, perché il motore non lo produce, quindi KO; con il file presente si controllano gli stili Titolo 1/2 e l'assenza di numeri di pagina, intestazioni e piè di pagina; Kindle Previewer è sempre un avviso.
5. Sezione 15: KO anche per formule non neutre nel manoscritto («recensione positiva», «5 stelle», «in cambio di»); il pattern sta in kdp.yaml.
6. Sezione 7: parole del titolo o del sottotitolo ripetute nelle parole chiave → avviso (solo parole di più di 3 lettere).
7. kdp_verifica.py ha tre comandi: `fatta`, `controlla`, `stato`. `controlla` stampa il promemoria anche quando le pagine sono raggiungibili, perché il confronto dei valori resta a mano.
8. Data di oggi fissabile con `--oggi` o `ZB_OGGI`, così le prove non dipendono dal giorno in cui girano.
9. Il PDF sintetico del percorso «tutto OK» ripete le pagine del PDF del giallo fino a 32 (almeno 30, numero pari), copiando i metadati, senza aggiungere testo.
10. I codici delle pagine ufficiali KDP in kdp.yaml restano «da confermare alla prima verifica» (proposta A.8).
```


Continua in [parte 6](ESPORTAZIONE_COMPLETA_6.md).

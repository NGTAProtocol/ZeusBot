"""Prove ripetibili del motore (comando «zb prove»).

Uso: python3 -B prove.py [--radice <cartella motore>] [--solo <sezione>] [--sezione <sezione>]… [--tutto]
Copia i mini-libri inventati di prove/ in cartelle temporanee, esegue le prove
di ogni passo presente in prove/attesi.yaml (passo_1, passo_2, …), confronta gli
esiti e stampa la tabella script | controllo | atteso | ottenuto | OK/KO.
Integrazione (ramo integrazione-editoriale): tutte le prove dei due rami, quelle di ccr (sezioni di questo file e
prove_editoriale.py) e quelle di motore (971b6df: fase struttura, cartella unica, ruoli, agenti e capsule, anti-IA,
correttore), adattate ai nomi del pacchetto e al modo automatico (docs/DECISIONI_INTEGRAZIONE.md), più la pausa di
lettura. Con --solo o --sezione (anche più volte) solo quelle sezioni di questo file: per lavorare; prima di un
commit sempre la suite intera (l'impronta per zb push si scrive solo con la suite intera tutta OK).
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
        'lingua_en': lambda y: y.replace('lingua: it', 'lingua: fr'),
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

    # nomi vietati dai rami di origin: un ramo con solo motore/ non è un ramo di libro; uno con libri/<slug>/libro.yaml sì
    import separazione
    r = tempfile.mkdtemp(dir=TMP)
    G = dict(ENV, GIT_AUTHOR_NAME='prova', GIT_AUTHOR_EMAIL='prova@esempio.invalid',
             GIT_COMMITTER_NAME='prova', GIT_COMMITTER_EMAIL='prova@esempio.invalid')

    def g(*a):
        return subprocess.run(['git', *a], cwd=os.path.join(r, 'lavoro'), env=G, capture_output=True, text=True)
    subprocess.run(['git', 'init', '-q', '--bare', os.path.join(r, 'origine.git')], env=G, capture_output=True)
    os.makedirs(os.path.join(r, 'lavoro'))
    g('init', '-q', '-b', 'lavoro')
    shutil.copytree(os.path.join(M, 'prove', 'mini-libro'), os.path.join(r, 'lavoro', 'motore', 'prove', 'mini-libro'))
    g('add', '-A')
    g('commit', '-q', '-m', 'motore')
    g('remote', 'add', 'origin', os.path.join(r, 'origine.git'))
    g('push', '-q', 'origin', 'lavoro:solo-motore-di-prova')
    libro = os.path.join(r, 'lavoro', 'libri', 'storia-inventata', 'libro.yaml')
    os.makedirs(os.path.dirname(libro))
    open(libro, 'w', encoding='utf-8').write('titolo: Storia inventata\n')
    g('add', '-A')
    g('commit', '-q', '-m', 'libro')
    g('push', '-q', 'origin', 'lavoro:libro/storia-inventata-di-prova')
    g('fetch', '-q', 'origin')
    nomi = separazione.nomi_dinamici(os.path.join(r, 'lavoro', 'motore'))
    esito('separazione.py', 'ramo di origin con solo motore/: nome vietato',
          A['separazione']['ramo_solo_motore_vietato'], 'sì' if 'solo-motore-di-prova' in nomi else 'no', sez)
    esito('separazione.py', 'ramo di origin con libri/<slug>/libro.yaml: nome vietato',
          A['separazione']['ramo_di_libro_vietato'], 'sì' if 'storia-inventata-di-prova' in nomi else 'no', sez)

    c = copia_motore()
    viol = os.path.join(c, 'prove', '_violazione_di_prova.tmp')
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


def struttura_pdf(pdf, libro, parole_attese=None):
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
            # testo estratto: numero di parole entro ±2% dell'atteso. Prima si confrontava anche lo sha256 del testo,
            # che cambia a ogni versione di Chromium/Playwright (sillabazione e spazi) anche con PDF corretti.
            'testo_parole': ('entro ±2% dell\'atteso' if parole_attese and abs(len(testo.split()) - parole_attese)
                             <= 0.02 * parole_attese else len(testo.split()))}


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
               'font_type3': 0, 'metadati_come_libro_yaml': True, 'testo_parole': 'entro ±2% dell\'atteso'},
              struttura_pdf(pdf, libro, att['struttura']['testo_parole']) if os.path.isfile(pdf) else 'assente', sez)
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
    if comune.repository_con_libro(os.path.dirname(M)):
        saltata('zb', '.claude/settings.json nel repository del motore', 'ramo di un libro: hook installati di proposito', sez)
    else:
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
    # soglie di stile informative (predefinito dal 2026-10-27): senza «soglie_stile: bloccanti» lo stesso capitolo dà avvisi
    L = copia_libro('mini-libro-romance')
    pl = os.path.join(L, 'libro.yaml')
    t = ''.join(r for r in open(pl, encoding='utf-8') if not r.startswith('soglie_stile:'))
    open(pl, 'w', encoding='utf-8').write(t)
    codice, righe = cap(L, '1')
    esito('capitolo.py', 'scene: romance 1 con le soglie di stile informative (predefinito): avviso, codice 0',
          "0 / ['scene_numero|AVVISO']", f'{codice} / {righe}', sez)
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

    def divieti_dettagli(L, b, profilo_extra=None):
        py = os.path.join(L, 'libro.yaml')
        lb = yaml.safe_load(open(py, encoding='utf-8'))
        lb['voce'] = {'slug': 'voce-di-prova', 'ambientazione': 'altro'}
        open(py, 'w', encoding='utf-8').write(yaml.safe_dump(lb, allow_unicode=True, sort_keys=False))
        prima = os.environ.pop('ZB_BANCA_VOCI', None)
        os.environ['ZB_BANCA_VOCI'] = b
        try:
            cartella, libro, profilo = comune.carica_libro(L)
            profilo.update(profilo_extra or {})
            return stile.controlla_libro(cartella, libro, profilo)['1'][1]
        finally:
            os.environ.pop('ZB_BANCA_VOCI', None)
            if prima is not None:
                os.environ['ZB_BANCA_VOCI'] = prima

    esito('stile.py', '(g) divieti della voce: libro senza voce', A['divieti_senza_voce'], divieti_trovati(False, banca), sez)
    esito('stile.py', '(g) divieti della voce: libro con voce, senza ZB_BANCA_VOCI', A['divieti_senza_banca'],
          divieti_trovati(True, None), sez)
    esito('stile.py', '(g) divieti della voce: libro con voce e banca', A['divieti_con_voce'], divieti_trovati(True, banca), sez)
    # (h) campo «massimo» dei divieti della voce (voce.py lo porta a stile.py): avviso solo oltre il massimo
    d = tempfile.mkdtemp(dir=TMP)
    bm = shutil.copytree(banca, os.path.join(d, 'banca'))
    pdm = os.path.join(bm, 'voci', 'voce-di-prova', 'divieti.yaml')
    base_d = open(pdm, encoding='utf-8').read()
    open(pdm, 'w', encoding='utf-8').write(base_d.rstrip('\n') + '\n' + ''.join(f'  {x}\n' for x in A['massimo_divieti'].splitlines()))
    Lm = copia_libro('mini-libro')
    open(os.path.join(Lm, '04-manoscritto', '01-la-farmacia.md'), 'a', encoding='utf-8').write('\n' + A['frase_massimo'] + '\n')
    trovati = []
    for r in divieti_dettagli(Lm, bm):
        if r['controllo'].split(':')[-1] in ('stanca_uno', 'stanca_due', 'stanca_ogni'):
            trovati.append(f'{r["controllo"].split(":")[-1]}|{r["esito"]}|{r["dettaglio"]}')
    esito('stile.py', '(h) massimo dei divieti: 2 occorrenze con massimo 1 (un avviso), con massimo 2 (nessuno), senza '
          'massimo (un avviso per occorrenza, come prima)', A['massimo_esiti'], sorted(trovati), sez)
    open(pdm, 'w', encoding='utf-8').write(base_d.rstrip('\n') + '\n  ' + A['massimo_non_valido'] + '\n')
    p = zb(M, 'voce', 'verifica', 'voce-di-prova', b=bm)
    esito('voce.py', '(h) massimo non intero: verifica KO con il motivo', A['massimo_verifica'],
          f'{p.returncode} / {"«massimo» non valido" in p.stdout} / {tb(p)}', sez)
    # (i) gruppi di forme: un solo massimo complessivo su più divieti (per esempio tutte le chiuse a sentenza)
    forme = ''.join(f'  {x}\n' for x in A['gruppo_divieti'].splitlines())
    Lg = copia_libro('mini-libro')
    open(os.path.join(Lg, '04-manoscritto', '01-la-farmacia.md'), 'a', encoding='utf-8').write('\n' + A['frase_gruppo'] + '\n')

    def gruppo_esiti(con_gruppi):
        open(pdm, 'w', encoding='utf-8').write(base_d.rstrip('\n') + '\n' + (forme if con_gruppi else forme.replace(', gruppo: chiuse', ''))
                                               + ('gruppi:\n  chiuse: {massimo: 1}\n' if con_gruppi else ''))
        return sorted(f'{r["controllo"].split(":", 1)[1]}|{r["esito"]}|{r["dettaglio"].split(":")[0]}'
                      for r in divieti_dettagli(Lg, bm) if 'forma_' in r['controllo'] or ':chiuse:' in r['controllo'])
    esito('stile.py', '(i) gruppo di forme: due forme con massimo 1 ciascuna, una occorrenza per forma: un avviso '
          'per il gruppo (massimo 1 in tutto)', A['gruppo_esiti'], gruppo_esiti(True), sez)
    esito('stile.py', '(i) senza gruppi (come prima): nessun avviso, ogni forma resta nel suo massimo', '[]',
          str(gruppo_esiti(False)), sez)
    open(pdm, 'w', encoding='utf-8').write(base_d.rstrip('\n') + '\n' + forme)
    p = zb(M, 'voce', 'verifica', 'voce-di-prova', b=bm)
    esito('voce.py', '(i) divieto in un gruppo non definito: verifica KO con il motivo', '1 / True / False',
          f'{p.returncode} / {"che non è definito in «gruppi»" in p.stdout} / {tb(p)}', sez)
    open(pdm, 'w', encoding='utf-8').write(base_d)
    # (f) schema: voce senza slug rifiutata; zb aiuto; modello del briefing
    Lm = copia_libro('mini-libro')
    open(os.path.join(Lm, 'libro.yaml'), 'a', encoding='utf-8').write('voce: {ambientazione: altro}\n')
    try:
        comune.carica_libro(Lm)
        msg = 'accettato'
    except comune.ErroreMotore as e:
        msg = 'libro.yaml.voce.slug: campo obbligatorio mancante' in str(e)
    esito('comune.py', '(f) libro.yaml con voce senza slug: rifiutato con il campo', A['schema_senza_slug'], msg, sez)
    esito('zb', '(f) zb aiuto elenca zb voce', A['aiuto'], 'zb voce campioni' in zb(M, 'aiuto', 'voce').stdout, sez)
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


# ---------------------------------------------------------------- sezioni portate da motore (971b6df)

class Banco:
    """repo git temporaneo con remoto, comandi zb e salvataggio (da motore, 971b6df)."""

    def __init__(self, sessione=None):
        self.E = {k: v for k, v in ENV.items() if k not in ('CLAUDE_PROJECT_DIR', 'ZB_LIBRO', 'ZB_RAMO', 'ZB_SESSIONE')}
        self.E.update(GIT_AUTHOR_NAME='Prova', GIT_AUTHOR_EMAIL='prova@esempio.invalid',
                      GIT_COMMITTER_NAME='Prova', GIT_COMMITTER_EMAIL='prova@esempio.invalid')
        if sessione:
            self.E['ZB_SESSIONE'] = sessione
        d = tempfile.mkdtemp(dir=TMP)
        self.git(d, 'init', '-q', '--bare', 'remoto.git')
        self.r = os.path.join(d, 'repo')
        os.makedirs(self.r)
        self.git(self.r, 'init', '-q')
        self.git(self.r, 'checkout', '-q', '-b', 'prova')
        self.git(self.r, 'remote', 'add', 'origin', os.path.join(d, 'remoto.git'))

    def git(self, cwd, *a):
        return subprocess.run(['git', *a], cwd=cwd, env=self.E, capture_output=True, text=True)

    def zb(self, *a, sessione=None, env=None):
        e = dict(env or self.E)
        if sessione:
            e['ZB_SESSIONE'] = sessione
        return subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), *a], cwd=self.r, env=e,
                              capture_output=True, text=True)

    def salva(self, msg='prova'):
        self.git(self.r, 'add', '-A')
        self.git(self.r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', msg)
        return self.git(self.r, 'push', '-q', '-u', 'origin', 'prova').returncode

    def stato(self, nome):
        return comune.leggi_yaml(os.path.join(self.r, nome, 'stato.yaml'))

    def nuovo(self, briefing, nome, editoriale=True):
        L = os.path.join(self.r, nome)
        os.makedirs(L)
        t = open(os.path.join(M, 'prove', 'briefing', briefing), encoding='utf-8').read()
        if editoriale:
            t = t.replace('Percorso: breve\n', 'Percorso: editoriale\n')
        open(os.path.join(L, 'briefing.md'), 'w', encoding='utf-8').write(t)
        p = self.zb('nuovo', f'{nome}/briefing.md')
        self.salva('nuovo')
        return L, p

    def fino_alla_fine(self, nome, p, **kw):
        for _ in range(80):
            if 'Fine dei documenti' in p.stdout or p.returncode:
                break
            p = self.zb('avanti', nome, **kw)
        return p

    def rapporto(self, nome, ruolo, rel, testo='DIAGNOSI: struttura di prova coerente.\n', n=None):
        """Rapporto con la prima riga data da «zb ruolo» (impronta del testo rivisto), in un commit a parte."""
        p = self.zb('ruolo', nome, ruolo, *([str(n)] if n else []))
        riga = next((x.split('Prima riga: ', 1)[1] for x in p.stdout.splitlines() if x.startswith('Prima riga: ')), '')
        dest = os.path.join(self.r, nome, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, 'w', encoding='utf-8').write(f'{riga}\n# {ruolo}\n\n{testo}')
        return self.salva(ruolo)


def compila_struttura_ed(L):
    """Riempie 03-struttura/ con testo di prova che passa i controlli di struttura.py (modelli tolti, campi pieni,
    macrostruttura, schede dei capitoli, una promessa chiusa, budget diversi). Adattata da motore (971b6df)."""
    import fase
    d = os.path.join(L, comune.STRUTTURA)
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        t = open(p, encoding='utf-8').read().replace(comune.MODELLO + '\n', '')
        t = re.sub(r'(?m)^(\s*- [^:\n]+:)\s*$', r'\1 valore di prova', t)
        t = re.sub(r'(?m)^(\s*- [^:\n]+:)\s*<[^>\n]*>\s*$', r'\1 valore di prova', t)
        t = t.replace('@char:<id> @loc:<id>', '@char:prova')
        if f == '04-atti-svolte.md':
            t = re.sub(r'(?m)^Macrostruttura:.*$', 'Macrostruttura: 3 atti', t)
            t = re.sub(r'(?m)^Motivo:.*$', 'Motivo: storia di prova con una sola svolta forte', t)
        if f == '06-sottotrame-temi.md':
            t = t.replace('|  |  |  |  |', '| La promessa di prova | 1 | 1 | 2 |')
        if f == '08-piano-parole.md':
            k = [0]

            def diverso(m):
                k[0] += 1
                return f'| {m.group(1)} |  |  |  | {int(m.group(2)) + 37 * k[0]} |'
            t = re.sub(r'\| (\d+) \|  \|  \|  \| (\d+) \|', diverso, t)
        open(p, 'w', encoding='utf-8').write(t)
    caps = [u for u in fase.unita_del_piano(L) if u.isdigit()]
    p = os.path.join(d, '07-tensione-ritmo.md')
    t = open(p, encoding='utf-8').read()
    open(p, 'w', encoding='utf-8').write(t.replace('|  |  |  |  |', '\n'.join(
        f'| {u} | {3 + int(u) % 5} | azione | prova |' for u in caps)))


def fase_struttura(A):
    """Fase struttura con il gate automatico (modo automatico del 2026-10-20), da motore (971b6df): giallo portato
    sul percorso editoriale, romance con tutti i gate di un tempo in libro.yaml (anche lì la struttura non si ferma)."""
    sez = 'fase struttura'
    import fase
    for briefing, nome in (('briefing-giallo.md', 'giallo'), ('briefing-romance.md', 'romance')):
        a = A[nome]
        b = Banco()
        L, p = b.nuovo(briefing, nome)
        presenti = sorted(d for d in os.listdir(L) if os.path.isdir(os.path.join(L, d)))
        scaletta = open(os.path.join(L, '03-struttura', '05-scaletta.md'), encoding='utf-8').read()
        esito('nuovo.py', f'{nome}: cartelle dopo zb nuovo / fase / blocchi di scaletta = capitoli del piano', a['nascita'],
              f'{presenti} / {b.stato(nome)["fase"]} / '
              f'{len(re.findall(r"(?m)^## Capitolo \d+", scaletta)) == fase.capitoli_previsti(L)}', sez)
        p = b.zb('pronto', nome)
        esito('fase.py', f'{nome}: pronto con la struttura ancora modello: fermo, file e rapporti elencati, nessun gate',
              a['vuota'], f'{p.returncode} / {"ancora modello" in p.stderr} / {"rapporto-struttura.md" in p.stderr} / '
                          f'{b.stato(nome)["gate_in_attesa"]}', sez)
        q = [b.zb('ok', nome).returncode, b.zb('avanti', nome).returncode, b.zb('esito', nome, '1').returncode]
        esito('fase.py', f'{nome}: ok / avanti / esito durante la fase struttura: rifiutati', a['prima_del_gate'], q, sez)
        compila_struttura_ed(L)
        st = os.path.join(L, '03-struttura', '06-sottotrame-temi.md')
        open(st, 'a', encoding='utf-8').write('| Promessa senza pagamento | 2 | 3 |  |\n')
        sf = os.path.join(L, '03-struttura', '09-scelte-fisse.md')
        t9 = open(sf, encoding='utf-8').read()
        open(sf, 'w', encoding='utf-8').write(re.sub(r'(?m)^(- Tempo verbale[^:\n]*:).*$', r'\1', t9))
        b.salva('struttura incompleta')
        p = b.zb('pronto', nome)
        esito('fase.py', f'{nome}: senza rapporto del diagnosta, un campo vuoto e una promessa senza chiusura: fermo',
              a['incompleta'], f'{p.returncode} / {"rapporto-struttura.md" in p.stderr} / {"senza chiusura" in p.stderr} / '
                               f'{"campo vuoto" in p.stderr}', sez)
        t = open(st, encoding='utf-8').read().replace('| Promessa senza pagamento | 2 | 3 |  |\n', '')
        open(st, 'w', encoding='utf-8').write(t)
        open(sf, 'w', encoding='utf-8').write(t9)
        b.salva('struttura completa')
        b.rapporto(nome, 'diagnosta', '06-diagnostica/rapporto-struttura.md')
        b.rapporto(nome, 'editor-strutturale', '06-diagnostica/piano-revisione-struttura.md', 'Piano: nessun lavoro.\n')
        p = b.zb('pronto', nome)
        s = b.stato(nome)
        esito('fase.py', f'{nome}: pronto: struttura verificata dal motore, nessuna fermata dell\'autore', a['gate'],
              f'{p.returncode} / {s["gate_in_attesa"]} / {s["fase"]} / {"nessuna fermata" in p.stdout}', sez)
        p = b.zb('ok', nome)
        esito('fase.py', f'{nome}: ok dopo la struttura automatica: rifiutato (nessun gate aperto)', a['ok_presto'],
              p.returncode, sez)
        creati = [x for x in ('02-bibbia/bibbia.md', 'cronologia.yaml', '03-architettura/manuale-di-stile.md')
                  if os.path.isfile(os.path.join(L, x))]
        esito('fase.py', f'{nome}: fase documenti, documenti creati solo ora, struttura registrata', a['ok'],
              f'{s["fase"]} / {len(creati)} / '
              f'{sum(1 for k in s["documenti_approvati"] if k.startswith("03-struttura/"))}', sez)
        esito('comune.py', f'{nome}: piano parole: una sola fonte (03-struttura/08-piano-parole.md)', 'sì',
              'sì' if comune.rel_piano(L) == os.path.join('03-struttura', '08-piano-parole.md')
              and not os.path.exists(os.path.join(L, '03-architettura', 'piano-parole.md')) else 'no', sez)
        b.salva('dopo struttura')
        open(sf, 'a', encoding='utf-8').write('- Cambio di punto di vista fuori procedura\n')
        b.salva('scelte fisse cambiate')
        p = b.zb('avvio', nome)
        esito('avvio.py', f'{nome}: scelte fisse cambiate dopo la struttura: avvio fermo', a['scelte_cambiate'],
              f'{p.returncode} / {"09-scelte-fisse.md" in p.stderr}', sez)


def cartella_unica_prove(A):
    """Cartella unica su git (avvio, push, hook su Bash e git commit), da motore (971b6df)."""
    import hook_recinto
    sez = 'cartella unica'
    b = Banco()
    r = b.r
    os.makedirs(os.path.join(r, 'motore'))
    open(os.path.join(r, 'motore', 'x.txt'), 'w', encoding='utf-8').write('motore di prova\n')
    b.salva('motore')
    b.git(r, 'push', '-q', 'origin', 'HEAD:motore')
    b.git(r, 'fetch', '-q', 'origin')
    os.makedirs(os.path.join(r, 'libri'))
    L, p = b.nuovo('briefing-giallo.md', 'libri/giallo')
    hook_recinto.imposta_libro_attivo(r, 'giallo')
    titolo = comune.leggi_yaml(os.path.join(L, 'libro.yaml'))['titolo']
    esito('hook_recinto.py', 'libro attivo fuori dai file tracciati (git-dir) / git status pulito', A['attivo'],
          f'{hook_recinto.slug_attivo(r)} / {b.git(r, "status", "--porcelain").stdout.strip() or "pulito"}', sez)
    esito('avvio.py', 'libro in libri/<slug>/, niente fuori: avvio', 0, b.zb('avvio', 'libri/giallo').returncode, sez)
    open(os.path.join(r, 'motore', 'x.txt'), 'a', encoding='utf-8').write('modifica\n')
    p = b.zb('avvio', 'libri/giallo')
    esito('avvio.py', 'file modificato fuori dal libro: fermo', A['modificato'],
          f'{p.returncode} / {"motore/x.txt" in p.stderr}', sez)
    b.git(r, 'checkout', '--', 'motore/x.txt')
    # commit misto: libro e motore nello stesso commit
    open(os.path.join(L, 'nomi_propri.txt'), 'a', encoding='utf-8').write('Ottavio\n')
    open(os.path.join(r, 'motore', 'x.txt'), 'a', encoding='utf-8').write('misto\n')
    b.salva('commit misto')
    misto = b.git(r, 'log', '-1', '--format=%h').stdout.strip()
    p = b.zb('avvio', 'libri/giallo')
    esito('avvio.py', 'commit misto (libro + motore): fermo', A['misto'], f'{p.returncode} / {"misto" in p.stderr}', sez)
    p = b.zb('push')
    esito('push.py', 'commit misto: push non eseguito', A['push'], f'{p.returncode} / {"cartella unica" in p.stderr}', sez)
    reg = os.path.join(M, 'dati', 'cartella-unica.yaml')
    orig = open(reg, encoding='utf-8').read()
    try:
        open(reg, 'w', encoding='utf-8').write(orig.replace('commit_dichiarati: []',
                                                            f'commit_dichiarati: [{{commit: {misto}, motivo: prova}}]'))
        p = b.zb('avvio', 'libri/giallo')
        esito('avvio.py', 'commit misto dichiarato in cartella-unica.yaml: avvio', 0, p.returncode, sez)
    finally:
        open(reg, 'w', encoding='utf-8').write(orig)
    b.git(r, 'reset', '-q', '--hard', 'HEAD~1')
    b.git(r, 'push', '-q', '-f', 'origin', 'prova')
    # merge del motore: ammesso
    b.git(r, 'checkout', '-q', '-b', 'm', 'origin/motore')
    open(os.path.join(r, 'motore', 'y.txt'), 'w', encoding='utf-8').write('nuovo nel motore\n')
    b.git(r, 'add', '-A')
    b.git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'motore nuovo')
    b.git(r, 'push', '-q', 'origin', 'HEAD:motore')
    b.git(r, 'checkout', '-q', 'prova')
    b.git(r, 'fetch', '-q', 'origin')
    b.git(r, '-c', 'commit.gpgsign=false', 'merge', '-q', '--no-edit', 'origin/motore')
    b.git(r, 'push', '-q', 'origin', 'prova')
    esito('avvio.py', 'merge del motore nel ramo del libro: avvio', 0, b.zb('avvio', 'libri/giallo').returncode, sez)
    # nome del libro fuori dalla cartella
    open(os.path.join(r, 'motore', 'nota.md'), 'w', encoding='utf-8').write(f'Appunto su {titolo}\n')
    b.salva('nome fuori')
    p = b.zb('avvio', 'libri/giallo')
    esito('avvio.py', 'titolo del libro in un file fuori dal libro: fermo', A['nome'],
          f'{p.returncode} / {"motore/nota.md" in p.stderr}', sez)
    os.remove(os.path.join(r, 'motore', 'nota.md'))
    b.salva('via il nome')
    # hook su Bash e git commit
    E = dict(b.E, CLAUDE_PROJECT_DIR=r)

    def hook(comando):
        dati = {'session_id': 's1', 'tool_name': 'Bash', 'tool_input': {'command': comando}, 'cwd': r}
        return subprocess.run([sys.executable, '-B', os.path.join(S, 'hook_recinto.py')], input=json.dumps(dati),
                              env=E, capture_output=True, text=True).returncode
    casi = ['echo x > motore/a.txt', 'echo x > libri/giallo/a.md', 'sed -i s/a/b/ libri/giallo/libro.yaml',
            'cp libri/giallo/libro.yaml motore/copia.yaml', 'rm CLAUDE.md', 'python3 motore/zb avvio libri/giallo 2>/dev/null',
            'grep -r x libri > /tmp/fuori.txt', 'git checkout prova']
    esito('hook_recinto.py', 'Bash: ' + ' | '.join(casi), A['bash'], [hook(c) for c in casi], sez)
    open(os.path.join(r, 'motore', 'x.txt'), 'a', encoding='utf-8').write('in stage\n')
    b.git(r, 'add', 'motore/x.txt')
    esito('hook_recinto.py', 'git commit con un file del motore in stage: bloccato', 2, hook('git commit -m prova'), sez)
    b.git(r, 'reset', '-q', 'motore/x.txt')
    b.git(r, 'checkout', '--', 'motore/x.txt')
    esito('hook_recinto.py', 'git commit con il solo libro: consentito', 0, hook('git add libri/giallo && git commit -m ok'), sez)
    hook_recinto.imposta_lavoro(r, 'motore')
    open(os.path.join(L, 'nomi_propri.txt'), 'a', encoding='utf-8').write('Prova\n')
    b.git(r, 'add', '-A')
    esito('hook_recinto.py', 'lavoro sul motore, file di libri/ in stage: commit bloccato', 2, hook('git commit -m x'), sez)
    b.git(r, 'reset', '-q')
    b.git(r, 'checkout', '--', '.')
    p = b.zb('push')
    esito('push.py', 'lavoro sul motore senza zb prove sullo stato attuale: push non eseguito', A['push_senza_prove'],
          f'{p.returncode} / {"zb prove" in p.stderr}', sez)


def avvio_motore_letto(A):
    """«zb avvio» senza libro (avvio_motore di ccr, tenuta nell'integrazione, punto 12): fermo senza «lavoro sul
    motore»; con «zb lavoro motore» riga «Letto» con CLAUDE.md, PROCEDURA, passaggio di consegne e LEGGIMI
    editoriale (righe, sha256, commit) e allineamento a origin; fermo se il ramo del motore contiene libri/."""
    sez = 'avvio motore'
    b = Banco()
    r = b.r
    shutil.copytree(M, os.path.join(r, 'motore'), ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy(os.path.join(os.path.dirname(M), 'CLAUDE.md'), os.path.join(r, 'CLAUDE.md'))
    b.salva('motore')
    zb = os.path.join(r, 'motore', 'zb')

    def avvio():
        return subprocess.run([sys.executable, '-B', zb, 'avvio'], cwd=r, env=b.E, capture_output=True, text=True)
    p = avvio()
    esito('avvio.py', 'zb avvio senza libro e senza «lavoro sul motore»: fermo', A['senza_lavoro'],
          f'{p.returncode} / {"lavoro sul motore non dichiarato" in p.stderr + p.stdout}', sez)
    subprocess.run([sys.executable, '-B', zb, 'lavoro', 'motore'], cwd=r, env=b.E, capture_output=True, text=True)
    p = avvio()
    letto = next((x for x in p.stdout.splitlines() if x.startswith('Letto: ')), '')
    file_letti = re.findall(r'([\w./-]+) \((\d+) righe, sha256 ([0-9a-f]{12}), commit [0-9a-f]+\)', letto)
    giusti = bool(file_letti) and all(comune.sha256_file(os.path.join(r, f))[:12] == h and
                 len(open(os.path.join(r, f), encoding='utf-8').read().splitlines()) == int(n) for f, n, h in file_letti)
    esito('avvio.py', 'lavoro sul motore: riga «Letto» con i quattro file (righe e sha256 giusti), allineato a origin',
          A['letto'], f'{p.returncode} / {", ".join(f for f, _, _ in file_letti)} / {giusti} / '
          f'{"allineato a origin: sì" in p.stdout}', sez)
    esito('avvio.py', 'zb avvio sul motore non scrive nulla', 'pulito',
          b.git(r, 'status', '--porcelain').stdout.strip() or 'pulito', sez)
    os.makedirs(os.path.join(r, 'libri'))
    p = avvio()
    esito('avvio.py', 'ramo del motore con una cartella libri/: fermo', A['con_libri'],
          f'{p.returncode} / {"cartella libri/" in p.stdout}', sez)


def ruoli_prove(A):
    """Un ruolo per sessione e separazione tra chi scrive e chi revisiona (da motore, 971b6df), con i nomi del
    pacchetto (rapporto-struttura.md del diagnosta) e il comando unico «zb ruolo»."""
    import hook_recinto
    sez = 'ruoli'
    b = Banco()
    r = b.r
    os.makedirs(os.path.join(r, 'libri'))
    L, _ = b.nuovo('briefing-romance.md', 'libri/romance')
    hook_recinto.imposta_libro_attivo(r, 'romance')
    nome = 'libri/romance'

    def scrive(sessione, rel):
        """Write di Claude Code (hook del recinto, che annota la sessione)."""
        dati = {'session_id': sessione, 'tool_name': 'Write', 'cwd': r,
                'tool_input': {'file_path': os.path.join(L, rel), 'content': 'x'}}
        return subprocess.run([sys.executable, '-B', os.path.join(S, 'hook_recinto.py')], input=json.dumps(dati),
                              env=dict(b.E, CLAUDE_PROJECT_DIR=r), capture_output=True, text=True).returncode

    p = b.zb('avvio', nome, sessione='s1')
    ruoli_reg = comune.leggi_yaml(os.path.join(L, '.zb', 'ruoli.yaml'))
    esito('avvio.py', 'avvio senza --ruolo: ruolo dalla fase, registrato in .zb/ruoli.yaml, file del ruolo letto', A['dalla_fase'],
          f'{p.returncode} / {ruoli_reg["s1"]["ruolo"]} / {"ruolo architetto-struttura" in p.stdout}', sez)
    p = b.zb('avvio', nome, '--ruolo', 'editor-strutturale', sessione='s1')
    esito('avvio.py', 'stessa sessione, secondo ruolo: fermo (un ruolo per sessione)', A['secondo_ruolo'],
          f'{p.returncode} / {"un ruolo per sessione" in p.stderr}', sez)
    p = b.zb('avvio', nome, '--ruolo', 'redattore', sessione='s9')
    esito('avvio.py', 'ruolo sconosciuto: fermo', 2, p.returncode, sez)
    compila_struttura_ed(L)
    b.salva('struttura')
    b.rapporto(nome, 'diagnosta', '06-diagnostica/rapporto-struttura.md')
    b.rapporto(nome, 'editor-strutturale', '06-diagnostica/piano-revisione-struttura.md', 'Piano: nessun lavoro.\n')
    scrive('s1', '03-struttura/01-premessa.md')
    scrive('s1', '06-diagnostica/rapporto-struttura.md')
    p = b.zb('pronto', nome)
    esito('fase.py', 'rapporto della struttura scritto dalla sessione dell\'architetto (blocco): fermo, nessun gate',
          A['stessa_sessione'], f'{p.returncode} / {"SEPARAZIONE DEI RUOLI" in p.stderr} / {b.stato(nome)["gate_in_attesa"]}', sez)
    hy = os.path.join(M, 'dati', 'hook.yaml')
    orig = open(hy, encoding='utf-8').read()
    try:
        open(hy, 'w', encoding='utf-8').write(orig.replace('separazione_ruoli: blocco', 'separazione_ruoli: avviso'))
        p = b.zb('pronto', nome)
        esito('fase.py', 'stessa situazione con separazione_ruoli: avviso: avviso e struttura verificata', A['avviso'],
              f'{p.returncode} / {"AVVISO separazione dei ruoli" in p.stdout} / {b.stato(nome)["fase"]}', sez)
    finally:
        open(hy, 'w', encoding='utf-8').write(orig)
    b.salva('documenti nati')
    # ripartenza pulita: il rapporto lo scrive un'altra sessione
    open(os.path.join(L, '.zb', 'scritture.log'), 'w', encoding='utf-8').write('')
    st = comune.leggi_yaml(os.path.join(L, 'stato.yaml'))
    st.update(fase='struttura', gate_in_attesa=None, revisione_in_corso=None, documenti_approvati={})
    open(os.path.join(L, 'stato.yaml'), 'w', encoding='utf-8').write(yaml.safe_dump(st, sort_keys=False, allow_unicode=True))
    scrive('s1', '03-struttura/01-premessa.md')
    scrive('s2', '06-diagnostica/rapporto-struttura.md')
    b.salva('rapporto da un\'altra sessione')
    p = b.zb('pronto', nome)
    esito('fase.py', 'rapporto scritto da un\'altra sessione: struttura verificata', A['altra_sessione'],
          f'{p.returncode} / {b.stato(nome)["fase"]}', sez)
    b.salva('struttura verificata')
    scrive('s4', '04-manoscritto/01-prova.md')
    p = b.zb('avvio', nome, '--ruolo', 'line-editor', sessione='s4')
    esito('avvio.py', 'sessione che ha scritto un capitolo chiede il ruolo di line editor: fermo', A['scrittore_revisore'],
          f'{p.returncode} / {"SEPARAZIONE DEI RUOLI" in p.stderr}', sez)
    p = b.zb('avvio', nome, '--ruolo', 'line-editor', sessione='s5')
    esito('avvio.py', 'altra sessione, ruolo di line editor: avvio', 0, p.returncode, sez)
    p = b.zb('ruolo', nome, 'stato')
    esito('ruolo.py', 'zb ruolo <libro> stato: modalità e sessioni', A['stato'],
          f'{p.returncode} / {"Modalità della separazione (dati/hook.yaml): blocco" in p.stdout} / {"s5: line-editor" in p.stdout}', sez)


# capsule di prova per il mini-libro (storia di motore, 971b6df), nelle otto sezioni di capsula.py e
# nella misura di ccr (120-250 parole nelle sezioni)
CAPSULE_PROVA = {
    1: ['Irene apre la farmacia di turno all\'alba e trova il registro dei veleni con una pagina strappata; '
        'controlla gli scaffali, conta le boccette e scopre che manca un flacone di laudano.',
        'Irene e il farmacista anziano: sanno della pagina strappata, non sanno chi l\'ha tolta; il farmacista '
        'ricorda un cliente forestiero della sera prima ma non ne dice il nome.',
        'Il registro manca della pagina del 3 marzo; la chiave dell\'armadio dei veleni l\'hanno in due; la '
        'pagina è stata tagliata con una lama, non strappata con le mani.',
        '@prom:pagina (chi ha tolto la pagina e perché proprio quella data).',
        'nessuna.',
        'Da errore di registro a furto: Irene decide di non avvisare subito i carabinieri e di cercare da sola.',
        'Irene diffidente e curiosa; il farmacista stanco, quasi offeso dalle domande.',
        'La pagina mancante guardata controluce: si vedono ancora le righe premute dalla penna.'],
    2: ['Irene porta l\'auto in officina e vede sul banco la stessa carta del registro, piegata in quattro sotto '
        'una chiave inglese; il meccanico la copre con uno straccio quando lei si avvicina.',
        'Irene e il meccanico: il meccanico tace sulla carta e dice di non conoscere il farmacista; Irene sa che '
        'mente perché li ha visti insieme al bar la domenica.',
        'La carta del registro è finita in officina; il meccanico ha una ricevuta della farmacia dello stesso giorno.',
        '@prom:officina (perché il meccanico ha la carta).',
        '@prom:pagina (la pagina è in officina, non distrutta).',
        'Irene passa dal sospetto sul farmacista al sospetto sul meccanico, e capisce che i due si coprono.',
        'Irene tesa e decisa; il meccanico nervoso, troppo gentile.',
        'Le mani sporche di grasso del meccanico sul foglio bianco del registro.'],
}


def agenti_capsule_consumo(A):
    """Agenti (formato e modello centrale), capsule, revisori, consumo e output compatto: da motore (971b6df),
    sulla base ccr (agenti.py con dati/modelli-ruoli.yaml, capsula.py a otto sezioni, consumo.py unico)."""
    import agenti
    import capsula
    import consumo
    import hook_recinto
    sez = 'agenti e capsule'
    err = agenti.controlla_formato(M)
    esito('agenti.py', 'formato degli agenti (name, description, model) e modelli = dati/modelli-ruoli.yaml',
          [], err, sez)
    tracciati = subprocess.run(['git', '-C', os.path.dirname(M), 'ls-files', '.claude'], capture_output=True, text=True).stdout.split()
    if comune.repository_con_libro(os.path.dirname(M)):
        saltata('agenti.py', 'ramo del motore: nessun agente attivo (.claude/ non tracciato)',
                'ramo di un libro: agenti installati di proposito', sez)
    else:
        esito('agenti.py', 'ramo del motore: nessun agente attivo (.claude/ non tracciato)', [], tracciati, sez)
    # attiva solo sul ramo di un libro e con --ok
    b = Banco()
    os.makedirs(os.path.join(b.r, 'libri'))
    b.nuovo('briefing-giallo.md', 'libri/giallo')
    ag = os.path.join(S, 'agenti.py')
    b.git(b.r, 'branch', '-m', 'motore')
    p1 = esegui(ag, 'attiva', '--ok', '--progetto', b.r)
    b.git(b.r, 'branch', '-m', 'libro-prova')
    p2 = esegui(ag, 'attiva', '--progetto', b.r)
    dest = os.path.join(b.r, '.claude', 'agents')
    senza_ok = os.path.isdir(dest)
    p3 = esegui(ag, 'attiva', '--ok', '--progetto', b.r)
    attivi = sorted(os.listdir(dest)) if os.path.isdir(dest) else []
    cap = open(os.path.join(dest, 'capsula.md'), encoding='utf-8').read() if attivi else ''
    p4 = esegui(ag, 'disattiva', '--progetto', b.r)
    esito('agenti.py', 'attiva: ramo motore fermo / senza --ok niente / con --ok tutti gli agenti / modello capsula / disattiva',
          A['attiva'], f'{p1.returncode} / {p2.returncode} {senza_ok} / {p3.returncode} {len(attivi)} / '
          f'{"model: haiku" in cap} / {p4.returncode} {os.path.isdir(dest)}', sez)
    # agenti come li installa il motore: diagnosta in sola lettura (niente Bash né Edit: P4 di docs/PROPOSTE_MOTORE.md);
    # letture ridotte: diagnosi/ non per il capitolo singolo; lo scrittore non rilegge scaletta e piano parole interi
    gen = {os.path.basename(x): t for x, t in agenti.piano(b.r, M)}
    strumenti = re.search(r'(?m)^tools:(.*)$', gen['diagnosta.md']).group(1)
    sv = gen['scrittore-voce.md']
    esito('agenti.py', 'agenti installati: diagnosta senza Bash né Edit / diagnosi/ non per il capitolo singolo / '
          'scrittore-voce senza 05-scaletta.md e 08-piano-parole.md interi (preparazione al loro posto)', A['letture'],
          f'{"Bash" not in strumenti and "Edit" not in strumenti} / {"per la struttura e il manoscritto anche motore/editoriale/diagnosi/" in gen["diagnosta.md"]} / '
          f'{"Mai la scaletta intera, il piano parole" in sv and "scaletta del capitolo, piano parole" not in sv}', sez)
    modello = lambda t: (re.search(r'(?m)^model:\s*(\S+)', t) or [None, None])[1]
    esito('agenti.py', 'modello dichiarato negli agenti installati: diagnosta (forte: dà il voto) / scrittore-voce (forte)',
          A['modello_diagnosta'], f'{modello(gen["diagnosta.md"])} / {modello(sv)}', sez)
    # modello centrale: si alza solo il ruolo indicato nel file di dati
    mc = copia_motore()
    pm = os.path.join(mc, 'dati', 'modelli-ruoli.yaml')
    testo_m = open(pm, encoding='utf-8').read()
    open(pm, 'w', encoding='utf-8').write(testo_m.replace('  capsula: leggero', '  capsula: medio'))
    p5 = esegui(os.path.join(mc, 'script', 'agenti.py'), 'attiva', '--ok', '--progetto', b.r)
    cap = open(os.path.join(dest, 'capsula.md'), encoding='utf-8').read()
    lin = open(os.path.join(dest, 'line-editor.md'), encoding='utf-8').read()
    p6 = esegui(os.path.join(mc, 'script', 'agenti.py'), 'stato', '--progetto', b.r)
    esito('agenti.py', 'modello alzato solo per la capsula nel file di dati: copiato / altri invariati / stato segnala il file',
          A['modello_centrale'], f'{p5.returncode} {"model: sonnet" in cap} / {"model: opus" in lin} / '
          f'{p6.returncode} {"diverso da dati/modelli-ruoli.yaml" in p6.stdout}', sez)
    esegui(os.path.join(mc, 'script', 'agenti.py'), 'disattiva', '--progetto', b.r)
    # capsule (capsula.py di ccr: modello, sezioni, 120-250 parole)
    L = copia_libro('mini-libro')
    st = comune.leggi_yaml(os.path.join(M, 'modelli', 'stato.yaml'))
    st.update(libro='mini-libro', fase='stesura', ultimo_capitolo_scritto=3, gate_in_attesa=None)
    open(os.path.join(L, 'stato.yaml'), 'w', encoding='utf-8').write(yaml.safe_dump(st, sort_keys=False, allow_unicode=True))
    _, libro, _ = comune.carica_libro(L)
    cp = os.path.join(S, 'capsula.py')
    q1 = esegui(cp, L, '1')
    q2 = esegui(cp, L, '1', '--verifica')

    def scrivi_capsula(n, extra=''):
        righe = [f'# Capsula {n} — prova', ''] + [f'- {s}: {v}' for s, v in zip(capsula.SEZIONI['it'], CAPSULE_PROVA[n])]
        open(os.path.join(L, capsula.rel(n)), 'w', encoding='utf-8').write('\n'.join(righe) + '\n' + extra)
    scrivi_capsula(1)
    q3 = esegui(cp, L, '1', '--verifica')
    scrivi_capsula(2, 'parola ' * 200 + '\n')
    q4 = esegui(cp, L, '2', '--verifica')
    esito('capsula.py', 'zb capsula: prepara il modello / ancora modello KO / compilata OK / oltre 250 parole KO',
          A['capsula'], f'{q1.returncode} {os.path.isfile(os.path.join(L, "07-capsule", "01.md"))} / {q2.returncode} / '
          f'{q3.returncode} / {q4.returncode} {"parole" in q4.stdout}', sez)
    stato_f = {'ultimo_capitolo_scritto': 3}
    try:
        capsula.controlla(L, dict(libro, capsule='obbligatorie'), stato_f)
        ob = 'passa'
    except comune.ErroreMotore as e:
        ob = 'fermo' if 'capitoli 2' in str(e) and '3' in str(e) else str(e)
    av = capsula.controlla(L, libro, stato_f) or ''
    esito('capsula.py', 'capsule mancanti o incomplete (2, 3): obbligatorie ferma / senza il campo avviso', A['controllo'],
          f'{ob} / {av.startswith("AVVISO")}', sez)
    # revisori: correzioni puntuali con Edit, mai Write su un capitolo esistente
    r = b.r
    hook_recinto.imposta_libro_attivo(r, 'giallo')
    cap1 = os.path.join(r, 'libri', 'giallo', '04-manoscritto', '01-prova.md')
    os.makedirs(os.path.dirname(cap1), exist_ok=True)
    open(cap1, 'w', encoding='utf-8').write('# 1 — Prova\n\nTesto.\n')

    def h(strumento, agente=None):
        dati = {'session_id': 's7', 'tool_name': strumento, 'cwd': r, 'tool_input': {'file_path': cap1}}
        if agente:
            dati['agent_type'] = agente
        return subprocess.run([sys.executable, '-B', os.path.join(S, 'hook_recinto.py')], input=json.dumps(dati),
                              env=dict(b.E, CLAUDE_PROJECT_DIR=r), capture_output=True, text=True).returncode
    esito('hook_recinto.py', 'capitolo esistente: Write del line editor / Edit del line editor / Write dello scrittore',
          A['revisori'], [h('Write', 'line-editor'), h('Edit', 'line-editor'), h('Write', 'scrittore-voce')], sez)
    # consumo: lo scrittore del capitolo 3 con e senza capsule (letture simulate secondo l'Input del ruolo)
    Lr = os.path.join(r, 'libri', 'giallo')
    os.makedirs(os.path.join(Lr, '07-capsule'), exist_ok=True)
    for f in sorted(os.listdir(os.path.join(L, '04-manoscritto'))):
        shutil.copy(os.path.join(L, '04-manoscritto', f), os.path.join(Lr, '04-manoscritto', f))
    for n in (1, 2):
        shutil.copy(os.path.join(L, capsula.rel(1)), os.path.join(Lr, capsula.rel(n)))
    comuni_letti = ['LEGGIMI.md', 'libro.yaml', '03-architettura/manuale-di-stile.md', '03-struttura/05-scaletta.md',
                    '03-struttura/08-piano-parole.md', 'cronologia.yaml']
    comuni_letti = [x for x in comuni_letti if os.path.isfile(os.path.join(Lr, x))]
    precedenti = [os.path.join('04-manoscritto', f) for f in ('01-la-farmacia.md', '02-l-officina.md')]

    def legge(sid, rel, limite=None):
        ti = {'file_path': os.path.join(Lr, rel)}
        if limite:
            ti['offset'] = max(1, sum(1 for _ in open(os.path.join(Lr, rel), encoding='utf-8')) - limite + 1)
            ti['limit'] = limite
        consumo.annota({'session_id': sid, 'tool_name': 'Read', 'tool_input': ti, 'cwd': r},
                       ora='2026-10-15T10:00:00Z')
    for rel in comuni_letti + precedenti:
        legge('senza-capsule', rel)
    for rel in comuni_letti + [capsula.rel(1), capsula.rel(2)]:
        legge('con-capsule', rel)
    legge('con-capsule', precedenti[-1], limite=25)          # solo l'ultima pagina del capitolo precedente
    consumo.annota({'session_id': 'con-capsule', 'tool_name': 'Agent', 'tool_input': {'subagent_type': 'scrittore-voce'},
                    'cwd': r}, ora='2026-10-15T10:05:00Z')
    _, lb, _ = comune.carica_libro(Lr)
    senza, con = consumo.riassunto(Lr, lb, 'senza-capsule'), consumo.riassunto(Lr, lb, 'con-capsule')
    misura = (f'senza capsule {senza["righe_lette"]} righe, {senza["parole_lette"]} parole in {senza["file_letti"]} file; '
              f'con capsule {con["righe_lette"]} righe, {con["parole_lette"]} parole in {con["file_letti"]} file; '
              f'subagenti {con["subagenti"]}, durata {con["durata"]}')
    print('MISURA CAPSULE (mini-libro, scrittore del capitolo 3): ' + misura)
    esito('consumo.py', 'scrittore del capitolo 3: con le capsule si leggono meno righe dei capitoli precedenti', 'sì',
          'sì' if con['parole_lette'] < senza['parole_lette'] else f'no ({misura})', sez)
    p = subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), 'consumo', Lr, '--sessione', 'con-capsule', '--registra'],
                       env=b.E, capture_output=True, text=True)
    esito('consumo.py', 'zb consumo <libro> --sessione S --registra: riga in .zb/consumo.log', A['consumo'],
          f'{p.returncode} / {os.path.isfile(os.path.join(Lr, ".zb", "consumo.log"))} / {"subagenti 1" in p.stdout}', sez)
    # output compatto: al massimo righe_max righe, KO a schermo, output intero nel .zb del libro
    # (soglia abbassata a 10 righe in una copia del motore: «zb conta» stampa 17 righe sul mini-libro, così la prova
    # non dipende da quante righe stampa oggi un comando)
    Lk = copia_libro('mini-libro')
    mk = copia_motore()
    po = os.path.join(mk, 'dati', 'output.yaml')
    testo_o = open(po, encoding='utf-8').read()
    open(po, 'w', encoding='utf-8').write(testo_o.replace('righe_max: 40', 'righe_max: 10'))
    p = subprocess.run([sys.executable, '-B', os.path.join(mk, 'zb'), 'conta', Lk], env=ENV, capture_output=True, text=True)
    pieno = os.path.join(Lk, '.zb', 'ultimo-output.txt')
    import importlib.machinery
    zbm = importlib.machinery.SourceFileLoader('zb_comando', os.path.join(M, 'zb')).load_module()
    finto = '\n'.join([f'riga {i}' for i in range(1, 100)] + ['| 3 | frase_media | KO | — | prova |'] +
                      [f'coda {i}' for i in range(1, 30)]) + '\n'
    corto = zbm.compatta(finto, 40, os.path.join(TMP, 'finto-output.txt'))
    esito('zb', 'output compatto: righe a schermo / riga KO tenuta / output intero salvato con più righe', A['compatto'],
          f'{len(p.stdout.splitlines()) <= 11 and len(corto.splitlines()) <= 41} / {"| KO |" in corto} / '
          f'{os.path.isfile(pieno) and len(open(pieno, encoding="utf-8").read().splitlines()) > 11}', sez)


# ---------------------------------------------------------------- anti-IA e correttore (da motore, 971b6df)

TESTO_IA = """# 3 — La stazione

<!-- zb: chiusura=G -->

Lei arrivò alla stazione in quel momento. Lei guardò il binario vuoto senza parlare. Lei sentì un turbinio di emozioni dentro.
Lei pensò alla lettera della sorella. Lei non sapeva ancora che tutto sarebbe cambiato. Lei strinse la valigia con forza.
All'improvviso il treno entrò in stazione. Lei salì sulla carrozza in fondo. Lei trovò un posto accanto al finestrino.
Lei osservò la città che spariva piano. Lei provò un misto di paura e speranza. Lei chiuse gli occhi per un attimo.
In quel momento il controllore entrò nella carrozza. Lei mostrò il biglietto con un sorriso. Lei ripose il biglietto nella borsa.
Non era solo un viaggio, era una fuga verso casa. Lei sapeva che nulla sarebbe stato più come prima. Lei guardò ancora fuori.
All'improvviso la luce cambiò sulle colline. Lei sentì il cuore che batteva forte nel petto. Lei respirò piano per calmarsi.
Lei pensò di nuovo alla sorella lontana. Lei ricordò la casa vicino al fiume. Lei sorrise senza un motivo preciso.
Sul biglietto c'era scritto "torno presto" con la sua calligrafia.
"""


def anti_ia_prove(A):
    """Audit anti-IA (antiia.py di ccr con le misure, le soglie per profilo e formule.yaml di motore)."""
    import antiia
    sez = 'anti-IA'
    nuove = ('formule_catalogo', 'coerenza', 'ripetizioni_ravvicinate')
    for nome in ('mini-libro', 'mini-libro-romance'):
        L = copia_libro(nome)
        _, libro, profilo = comune.carica_libro(L)
        segnalati = [f'{u}:{k}' for u, (m, v) in antiia.audit(L, libro, profilo=profilo, scrivi=False).items()
                     for k, g, d in v if k in nuove]
        esito('antiia.py', f'{nome}: taratura, nessuna segnalazione delle misure di motore sui capitoli di prova', [],
              segnalati, sez)
    L = copia_libro('mini-libro')
    _, libro, profilo = comune.carica_libro(L)
    p3 = dict(comune.unita(L, libro))['3']
    open(p3, 'w', encoding='utf-8').write(TESTO_IA)
    sha = comune.sha256_file(p3)
    m, v = antiia.audit(L, libro, '3', profilo=profilo, scrivi=False)['3']
    esito('antiia.py', 'capitolo inventato «da IA»: misure accese', A['ia_controlli'], sorted({k for k, _, _ in v}), sez)
    m_b, _ = antiia.audit(L, dict(libro, anti_ia={'formule_sezione_b': True}), '3', profilo=profilo, scrivi=False)['3']
    esito('antiia.py', 'capitolo «da IA»: aperture uguali sopra la soglia / formule del catalogo: la sezione B conta solo '
          'con formule_sezione_b', A['ia_misure'],
          f'{m["aperture_uguali"] > 20} / {m["formule_catalogo_per_mille"] < m_b["formule_catalogo_per_mille"]}', sez)
    p = esegui(os.path.join(S, 'capitolo.py'), L, '3')
    rep = os.path.join(L, '06-diagnostica', 'anti-ia', '03.md')
    righe_audit = [r for r in open(rep, encoding='utf-8').read().splitlines() if r.startswith('| ') and 'formula' in r]
    esito('capitolo.py', 'audit non distruttivo: report anti-ia scritto, capitolo intatto, avvisi non bloccanti', A['audit'],
          f'{os.path.isfile(rep)} / {len(righe_audit) >= 5} / {comune.sha256_file(p3) == sha} / '
          f'{"anti-ia:formule_catalogo | AVVISO" in open(os.path.join(L, "06-diagnostica", "capitoli", "03.md"), encoding="utf-8").read()}', sez)
    ly = os.path.join(L, 'libro.yaml')
    open(ly, 'a', encoding='utf-8').write('anti_ia: {modalita: blocco}\n')
    p2 = esegui(os.path.join(S, 'capitolo.py'), L, '3')
    esito('capitolo.py', 'anti_ia.modalita: blocco in libro.yaml: KO e codice 1', A['blocco'],
          f'{p2.returncode} / {"anti-ia:aperture_uguali | KO" in open(os.path.join(L, "06-diagnostica", "capitoli", "03.md"), encoding="utf-8").read()}', sez)
    # aperture uguali: una battuta di dialogo tra due frasi con lo stesso soggetto interrompe la serie
    con_battuta = 'Il ragazzo spegne il motore.\n\n— Lascialo acceso.\n\nIl ragazzo gira di nuovo la chiave.\n'
    stessa_riga = 'Il ragazzo spegne il motore. — Lascialo acceso. Il ragazzo gira di nuovo la chiave.\n'
    consecutive = 'Il ragazzo spegne il motore. Il ragazzo gira di nuovo la chiave.\n'
    esito('antiia.py', 'aperture uguali: battuta in mezzo (riga a parte / stessa riga) non conta; due frasi consecutive '
          'con lo stesso soggetto contano (coppie uguali; % della misura)', A['aperture_battuta'],
          f'{antiia.aperture_uguali(con_battuta, "it")[0]} / {antiia.aperture_uguali(stessa_riga, "it")[0]} / '
          f'{antiia.aperture_uguali(consecutive, "it")[0]} / {antiia.misure(con_battuta, "it", [])["aperture_uguali"]} / '
          f'{antiia.misure(consecutive, "it", [])["aperture_uguali"]}', sez)
    # segmenti senza parole («* * *», «...», «1984.») tra frasi di narrazione: nessun errore; con frasi() che li
    # lasciasse passare (simulato), la frase senza parole si salta
    senza_parole = 'Il ragazzo esce.\n\n* * *\n\nIl ragazzo torna. ... 1984. Lei resta.\n'
    originale = antiia.frasi
    try:
        antiia.frasi = lambda t: re.split(r'(?<=[.!?…])\s+', ' '.join(t.split()))
        simulato = antiia.aperture_uguali(senza_parole, 'it')
    except IndexError as e:
        simulato = f'IndexError {e}'
    finally:
        antiia.frasi = originale
    esito('antiia.py', 'aperture uguali: segmenti senza parole tra frasi di narrazione (reale / frasi() senza filtro)',
          A['aperture_senza_parole'], f'{antiia.aperture_uguali(senza_parole, "it")} / {simulato}', sez)
    R = copia_libro('mini-libro-romance')
    _, lr, pr = comune.carica_libro(R)
    gr = lambda lb: next((g for k, g, _ in antiia.audit(R, lb, '2', profilo=pr, scrivi=False)['2'][1]
                          if k == 'chiusure_uguali'), '—')
    esito('antiia.py', 'chiusure uguali di fila: soglia del profilo (P2 al secondo) / soglia 1 in libro.yaml (P0)',
          A['chiusure'], f'{gr(lr)} / {gr(dict(lr, anti_ia={"chiusure_uguali_max": 1}))}', sez)


def correttore(A):
    """Lista di controllo dai criteri e LanguageTool (languagetool.py: installatore di motore, comando unico)."""
    import ortografia
    sez = 'correttore'
    crit = os.path.join(M, 'editoriale', 'correttore', 'criteri-correttore.md')
    puntati = sum(1 for r in open(crit, encoding='utf-8').read().split('## 7.')[0].splitlines() if r.startswith('- '))
    voci = ortografia.checklist()
    esito('ortografia.py', 'lista di controllo = punti delle sezioni 1-6 di criteri-correttore.md', 'sì',
          'sì' if len(voci) == puntati and voci[0].startswith('Accenti e apostrofi:') else f'no ({len(voci)}/{puntati})', sez)
    L = copia_libro('mini-libro')
    p = esegui(os.path.join(S, 'ortografia.py'), L, '--schermo')
    esito('ortografia.py', 'report: sezione (c) con le voci dei criteri', A['report'],
          f'{"criteri-correttore.md" in p.stdout} / {sum(1 for v in voci if v.replace("|", "/") in p.stdout)}', sez)
    d = os.path.join(M, 'prova-languagetool-vietata')
    p = esegui(os.path.join(S, 'languagetool.py'), 'installa', '--cartella', d)
    esito('languagetool.py', 'installazione dentro il repository: rifiutata, niente creato', A['dentro_repo'],
          f'{p.returncode} / {os.path.exists(d)}', sez)
    lt = os.environ.get('ZB_LANGUAGETOOL')
    if not lt:
        saltata('languagetool.py', 'verifica: frase di prova segnalata', 'LanguageTool assente (ZB_LANGUAGETOOL non impostata)', sez)
        saltata('languagetool.py', 'installazione già pronta', 'LanguageTool assente (ZB_LANGUAGETOOL non impostata)', sez)
        return
    p = esegui(os.path.join(S, 'languagetool.py'), 'verifica')
    esito('languagetool.py', 'verifica: frase di prova segnalata con una regola grammaticale italiana', A['verifica'],
          f'{p.returncode} / {"GR_04_001" in p.stdout}', sez)
    p = esegui(os.path.join(S, 'languagetool.py'), 'installa', '--cartella', os.path.dirname(os.path.realpath(lt)))
    esito('languagetool.py', 'installazione già pronta: niente riscaricato', A['gia_pronto'],
          f'{p.returncode} / {"già pronto" in p.stdout} / {"export ZB_LANGUAGETOOL=" in p.stdout}', sez)


FRASI_FINALI_TESTO = """# 1 — Prova

Prima frase. Seconda frase che chiude.

— Vieni? — chiede lei.

— Davvero? — dice lui.

Lui resta alla finestra.

* * *

— Ultima battuta.
"""


def frasi_finali_prove(A):
    """P3: elenco delle frasi finali (stile.frasi_finali) e report 06-diagnostica/frasi-finali/NN.md di zb stile."""
    sez = 'frasi_finali'
    import stile
    ff = stile.frasi_finali(FRASI_FINALI_TESTO, comune.lingue()['it'])
    esito('stile.py', 'frasi finali: narrazione, ultima battuta di uno scambio, fine scena, attacco della battuta',
          A['elenco'], [f'{v["riga"]}|{v["tipo"]}|{v["frase"]}' for v in ff], sez)
    c = copia_libro('mini-libro')
    esegui(os.path.join(S, 'stile.py'), c)
    d = os.path.join(c, '06-diagnostica', 'frasi-finali')
    cartella, libro, _ = comune.carica_libro(c)
    testo = open(os.path.join(c, '04-manoscritto', '01-la-farmacia.md'), encoding='utf-8').read()
    n = len(stile.frasi_finali(testo, comune.lingue()[libro['lingua']]))
    rep = open(os.path.join(d, '01.md'), encoding='utf-8').read() if os.path.isfile(os.path.join(d, '01.md')) else ''
    righe = [r for r in rep.splitlines() if re.match(r'^\| \d+ \|', r)]
    esito('stile.py', 'zb stile: un report per capitolo numerato (non per l\'interludio), una riga per frase',
          A['report'], f'{sorted(os.listdir(d)) if os.path.isdir(d) else []} / {n > 0 and len(righe) == n} / '
          f'{"| Riga | Tipo | Frase finale |" in rep}', sez)


TABELLA_REGISTRI = """
| Elemento | Base (autore A) | Registro freddo (autore B) | Registro corto (autore C) |
|---|---|---|---|
| frase media | 12-18 parole | 15-25 parole | 5-10 parole |
| frase più lunga | 35 parole | 45 parole | 20 parole |
"""


def frase_media_registro(A):
    """Frase media per registro: con «frase_media_voce: true» nel profilo l'intervallo del capitolo viene dal registro
    dichiarato nella scaletta e dalla tabella della sezione 3 della scheda della voce (voce.registri,
    stile.intervallo_frase_media); override del libro e profili senza il campo tengono l'intervallo del profilo."""
    sez = 'frase_media_registro'
    import stile
    import voce as voce_mod
    d = tempfile.mkdtemp(dir=TMP)
    b = shutil.copytree(os.path.join(M, 'prove', 'banca-voci-prova'), os.path.join(d, 'banca'))
    sc = os.path.join(b, 'voci', 'voce-di-prova', 'scheda.md')
    t = open(sc, encoding='utf-8').read()
    open(sc, 'w', encoding='utf-8').write(t.replace('## 3. Ritmo e sintassi\n', '## 3. Ritmo e sintassi\n' + TABELLA_REGISTRI, 1))
    reg = voce_mod.registri(b, 'voce-di-prova')
    esito('voce.py', 'registri della voce dalla riga «frase media» della sezione 3', A['registri'],
          str(sorted(reg.items())), sez)
    esito('voce.py', 'voce senza tabella nella sezione 3: nessun registro', '{}',
          str(voce_mod.registri(os.path.join(M, 'prove', 'banca-voci-prova'), 'voce-di-prova')), sez)
    prof = {'frase_media': [9, 14], 'frase_media_voce': True}
    casi = [
        (prof, {}, {'pov': 'Anna; registro corto, presente'}),
        (prof, {}, {'pov': 'Anna; registro freddo e poi registro corto'}),
        (prof, {}, {'pov': 'Anna; giorno 2'}),
        (prof, {'override': [{'campo': 'frase_media', 'valore': [8, 12], 'motivo': 'prova'}]}, {'pov': 'registro corto'}),
        ({'frase_media': [9, 14]}, {}, {'pov': 'registro corto'}),
        (prof, {}, {'pov': 'registro lirico'}),
    ]
    ott = []
    for pr, lb, scheda in casi:
        x, y, nota = stile.intervallo_frase_media(pr, lb, reg, scheda)
        ott.append(f'{x}-{y}' + (f' {nota}' if nota else ''))
    esito('stile.py', 'intervallo della frase media: corto, primo registro dichiarato, senza registro (base), '
          'override del libro, profilo senza campo, registro sconosciuto', A['intervalli'], ott, sez)
    ott = [stile.intervallo_frase_media(prof, {}, {}, {'pov': 'registro corto'})[:2]]
    esito('stile.py', 'voce senza registri: intervallo del profilo', '[(9, 14)]', str(ott), sez)
    # integrazione: mini-libro con voce, scaletta con i registri dei capitoli 1 e 2, profilo con il campo acceso
    c = copia_libro('mini-libro')
    py = os.path.join(c, 'libro.yaml')
    lb = yaml.safe_load(open(py, encoding='utf-8'))
    lb['voce'] = {'slug': 'voce-di-prova', 'ambientazione': 'altro'}
    open(py, 'w', encoding='utf-8').write(yaml.safe_dump(lb, allow_unicode=True, sort_keys=False))
    os.makedirs(os.path.join(c, comune.STRUTTURA), exist_ok=True)
    open(os.path.join(c, comune.STRUTTURA, '05-scaletta.md'), 'w', encoding='utf-8').write(
        '# Scaletta\n\n## Capitolo 1 - Primo\n- Punto di vista, luogo e tempo: Anna; registro corto, presente\n\n'
        '## Capitolo 2 - Secondo\n- Punto di vista, luogo e tempo: Anna; registro freddo\n')
    prima = os.environ.pop('ZB_BANCA_VOCI', None)
    os.environ['ZB_BANCA_VOCI'] = b
    try:
        cartella, libro, profilo = comune.carica_libro(c)
        senza = stile.controlla_libro(cartella, libro, dict(profilo))
        profilo['frase_media_voce'] = True
        con = stile.controlla_libro(cartella, libro, profilo)
    finally:
        os.environ.pop('ZB_BANCA_VOCI', None)
        if prima is not None:
            os.environ['ZB_BANCA_VOCI'] = prima

    def fm(es):
        return [f'{n}: {m.get("frase_media_intervallo")} ' +
                next((r['esito'] for r in o if r['controllo'] == 'frase_media'), 'OK') for n, (m, o) in es.items() if n.isdigit()]
    esito('stile.py', 'mini-libro con voce e scaletta, profilo senza il campo: intervallo del profilo', A['senza_campo'],
          fm(senza), sez)
    esito('stile.py', 'mini-libro con voce e scaletta, frase_media_voce: true: intervallo del registro di ogni capitolo, '
          'fuori intervallo AVVISO (non KO)', A['con_campo'], fm(con), sez)
    det = [r['dettaglio'] for r in con['2'][1] if r['controllo'] == 'frase_media']
    esito('stile.py', 'avviso della frase media del registro: «intervallo non calibrato sull\'autore»', 'True',
          str(bool(det) and det[0].endswith("intervallo non calibrato sull'autore")), sez)
    th = comune.carica_profilo('thriller')
    esito('profili/thriller.yaml', 'thriller: la voce prevale sulla frase media', 'True', str(th.get('frase_media_voce')), sez)


def grafica(A):
    """Stili dell'interno (formato.stile) e copertina intera (copertina.py), 2026-10-27."""
    import impagina
    import pymupdf
    import verifica_pdf
    sez = 'grafica'
    esito('impagina.py', 'capolettera: classe «primo» sul primo paragrafo di testo, non sul sottotitolo in corsivo', True,
          impagina.marca_primo('<h2>1</h2>\n<p><em>Lidia</em></p>\n<p>Lidia arrivò.</p>\n<p>Poi.</p>')
          == '<h2>1</h2>\n<p><em>Lidia</em></p>\n<p class="primo">Lidia arrivò.</p>\n<p>Poi.</p>', sez)
    if not shutil.which('node'):
        saltata('impagina.py', 'stile classico e copertina', 'Node assente', sez)
        return
    c = copia_libro('mini-libro-romance')
    py = os.path.join(c, 'libro.yaml')
    t = open(py, encoding='utf-8').read().replace('  bleed: false', '  bleed: false\n  stile: classico')
    open(py, 'w', encoding='utf-8').write(t)
    cart, libro, pdf = pdf_di(c)
    fonts = verifica_pdf.pdffonts(pdf) if os.path.isfile(pdf) else []
    with pymupdf.open(pdf) as d:
        testo = ' '.join(p.get_text() for p in d)
    esito('impagina.py', 'stile classico: PDF, font tutti incorporati e nessun Type3, fleuron tra le scene', 'True / 0 / 0 / True',
          f'{os.path.isfile(pdf)} / {sum(1 for f in fonts if not f["incorporato"])} / '
          f'{sum(1 for f in fonts if f["tipo"] == "Type 3")} / {chr(0x2767) in testo}', sez)
    cop = os.path.join(cart, '06-pubblicazione', 'copertina', 'copertina.pdf')
    r1 = esegui(os.path.join(S, 'copertina.py'), c, '--pagine', '240')
    with pymupdf.open(cop) as d:
        w1, h1 = round(d[0].rect.width / 72, 4), round(d[0].rect.height / 72, 4)
    f1 = verifica_pdf.pdffonts(cop)
    r2 = esegui(os.path.join(S, 'copertina.py'), c, '--pagine', '60')
    with pymupdf.open(cop) as d:
        w2 = round(d[0].rect.width / 72, 4)
    esito('copertina.py', 'copertina intera: 240 pagine crema 5,5×8,5 = 11,85×8,75″ con testo sulla costola; 60 pagine = '
          '11,4″ senza; font incorporati', '0 11.85 8.75 True / 0 11.4 False / 0',
          f'{r1.returncode} {w1} {h1} {"costola: sì" in r1.stdout} / {r2.returncode} {w2} {"costola: sì" in r2.stdout} / '
          f'{sum(1 for f in f1 if not f["incorporato"])}', sez)
    r3 = esegui(os.path.join(S, 'copertina.py'), c)
    esito('copertina.py', 'senza --pagine: legge il PDF di stampa', 0, r3.returncode, sez)


SEZIONI = {'passo_1': passo_1, 'passo_2': passo_2, 'passo_3': passo_3, 'passo_4': passo_4, 'passo_5': passo_5, 'passo_6': passo_6, 'passo_7': passo_7, 'override_lunghezza': override_lunghezza, 'scene': scene, 'manuale_leggibile': manuale_leggibile, 'checklist_capitolo': checklist_capitolo, 'continuita_eta_durate': continuita_eta_durate, 'correzioni_dopo_prova': correzioni_dopo_prova, 'correzioni_interludi_e_grafie': correzioni_interludi_e_grafie, 'correzioni_e_passo': correzioni_e_passo, 'unita_consentite_e_interludi': unita_consentite_e_interludi, 'fase_stesura_e_rinomine': fase_stesura_e_rinomine, 'correzioni_esclusioni_e_budget': correzioni_esclusioni_e_budget, 'titoli_tempi_eta_push': titoli_tempi_eta_push, 'eccezioni_e_richiami': eccezioni_e_richiami, 'voce': voce, 'recinto_libro': recinto_libro, 'appendici': appendici, 'fase_struttura': fase_struttura, 'cartella_unica': cartella_unica_prove, 'avvio_motore_letto': avvio_motore_letto, 'ruoli': ruoli_prove, 'agenti_capsule': agenti_capsule_consumo, 'anti_ia': anti_ia_prove, 'correttore': correttore, 'frasi_finali': frasi_finali_prove, 'frase_media_registro': frase_media_registro, 'grafica': grafica}


def main(argv):
    A = comune.leggi_yaml(os.path.join(M, 'prove', 'attesi.yaml'))
    scelte = [argv[i + 1] for i, a in enumerate(argv) if a in ('--solo', '--sezione') and i + 1 < len(argv)]
    solo = scelte or None
    try:
        for chiave, funz in SEZIONI.items():
            if chiave in A and (not solo or chiave in solo):
                funz(A[chiave])
        import prove_editoriale
        prove_editoriale.TMP = tempfile.mkdtemp(dir=TMP)
        for f in prove_editoriale.SEZIONI:
            if not solo or f.__name__ in solo or 'editoriale' in solo:
                prove_editoriale.esegui_sezione(f)
        righe.extend(prove_editoriale.righe)
        finali = []
        for nome in ('separazione.py', 'recinto.py'):
            p = esegui(os.path.join(S, nome), '--radice', M)
            finali.append((nome, p.returncode, (p.stdout.strip().splitlines() or [''])[-1]))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    tabella = ['| Sezione | Script | Controllo | Atteso | Ottenuto | Esito |', '|---|---|---|---|---|---|']
    tabella += ['| ' + ' | '.join(r) + ' |' for r in righe]
    report = os.path.join(tempfile.gettempdir(), 'zb-prove-ultimo.md')
    with open(report, 'w', encoding='utf-8') as f:
        f.write('# Prove del motore\n\n' + '\n'.join(tabella) + '\n')
    ok = sum(1 for r in righe if r[5] == 'OK')
    contate = [r for r in righe if r[5] != 'SALTATA']
    ko = [r for r in righe if r[5] == 'KO']
    if '--tutto' in argv:
        print('\n'.join(tabella))
    for r in ko[:20]:
        print(f'KO [{r[0]}] {r[1]}: {r[2]} — atteso {r[3][:80]}, ottenuto {r[4][:80]}')
    if len(ko) > 20:
        print(f'… altri {len(ko) - 20} KO nel report')
    print(f'Prove: {ok}/{len(contate)} OK; saltate: {len(righe) - len(contate)} (non contate nel totale). '
          f'Tabella completa: {report}')
    for motivo in sorted({r[4] for r in righe if r[5] == 'SALTATA'}):
        n = sum(1 for r in righe if r[5] == 'SALTATA' and r[4] == motivo)
        print(f'saltate: {n}, {motivo}')
        if motivo.startswith('LanguageTool assente'):
            print('  per eseguirle: python3 motore/zb languagetool installa, poi ZB_LANGUAGETOOL come indicato')
    for nome, codice, riga in finali:
        print(f'{nome} su motore/: {"OK" if codice == 0 else "KO"} — {riga}')
    tutto_ok = ok == len(contate) and all(c == 0 for _, c, _ in finali)
    print('ESITO: ' + ('tutto OK' if tutto_ok else 'CI SONO KO'))
    f = comune.file_prove_ok()
    if f and not solo:          # impronta per zb push sul lavoro del motore (da motore): solo suite intera e tutta OK
        if tutto_ok:
            open(f, 'w', encoding='utf-8').write((comune.impronta_motore() or '') + '\n')
            print('Impronta del motore registrata per zb push.')
        elif os.path.isfile(f):
            os.remove(f)
    return 0 if tutto_ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

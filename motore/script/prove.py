"""Prove ripetibili del motore (comando «zb prove»).

Uso: python3 -B prove.py [--radice <cartella motore>]
Copia i due mini-libri inventati di prove/ in cartelle temporanee, esegue le prove
di ogni passo presente in prove/attesi.yaml (passo_1, passo_2, …), confronta gli
esiti e stampa la tabella script | controllo | atteso | ottenuto | OK/KO.
Alla fine rilancia separazione.py e recinto.py su motore/.
Codice d'uscita 0 solo se tutto è OK.
"""
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
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
TMP = tempfile.mkdtemp(prefix='zb-prove-')
righe = []


def esito(script, controllo, atteso, ottenuto, sezione):
    ok = str(atteso) == str(ottenuto)
    righe.append((sezione, script, controllo, str(atteso), str(ottenuto), 'OK' if ok else 'KO'))


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
        esegui(os.path.join(S, 'conta.py'), c)
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
        esito('impagina.py', f'{nome}: sha256 del PDF', att['pdf_sha256'], primo, sez)
        misure, ris = verifica_pdf.verifica(cart, libro, pdf)
        esito('verifica_pdf.py', f'{nome}: pagine', att['pagine'], misure['pagine'], sez)
        esito('verifica_pdf.py', f'{nome}: metadati Title e Author', att['metadati'],
              {'Title': misure['Title'], 'Author': misure['Author']}, sez)
        esito('verifica_pdf.py', f'{nome}: font Type3', 0, misure['font_type3'], sez)
        esito('verifica_pdf.py', f'{nome}: font non incorporati', 0, misure['font_non_incorporati'], sez)
        for k, v in att['margini'].items():
            esito('verifica_pdf.py', f'{nome}: margine {k}', v, misure[f'margine_{k}'], sez)
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
    esito('fase.py', 'ok, lotti da 5: lotti, ultimo approvato, fase', a['ok_lotti'],
          f'{p.returncode} / {s["lotto"]["dimensione"]} / {s["ultimo_capitolo_approvato"]} / {s["fase"]}', sez)
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
    esito('zb', 'comando previsto ma non costruito (ortografia)', a['ortografia'], f'{p.returncode} / {"non esiste ancora" in p.stderr}', sez)
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


# ---------------------------------------------------------------- tabella

SEZIONI = {'passo_1': passo_1, 'passo_2': passo_2, 'passo_3': passo_3, 'passo_4': passo_4, 'passo_5': passo_5, 'passo_5b': passo_5b, 'passo_6': passo_6}


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
    print(f'\nProve: {ok}/{len(righe)} OK')
    for nome, codice, riga in finali:
        print(f'{nome} su motore/: {"OK" if codice == 0 else "KO"} — {riga}')
    tutto_ok = ok == len(righe) and all(c == 0 for _, c, _ in finali)
    print('ESITO: ' + ('tutto OK' if tutto_ok else 'CI SONO KO'))
    return 0 if tutto_ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

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


# ---------------------------------------------------------------- tabella

SEZIONI = {'passo_1': passo_1, 'passo_2': passo_2}


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

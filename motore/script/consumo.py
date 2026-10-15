"""Misura del consumo di una sessione (editoriale/risparmio-token.md, «Misura»).

Hook PostToolUse (dati/hook-settings.esempio.json, matcher «Read|Agent|Task»): legge da stdin il JSON
dell'hook e aggiunge una riga a <libro>/.zb/letture.log, con il libro attivo (hook_recinto):
  <ora ISO>\t<sessione>\tRead\t<file relativo al repository>\t<righe lette>:<parole lette>
  <ora ISO>\t<sessione>\tAgent\t<tipo di subagente>\t0:0
Non blocca mai (codice 0).

Comando: zb consumo <libro> [--sessione S] [--registra]
Per la sessione S (predefinita: quella corrente) riassume: capitoli scritti (scritture.log, 04-manoscritto/),
parole di quei capitoli, file e righe letti, subagenti chiamati per tipo, durata (prima e ultima riga).
Con --registra aggiunge il riassunto a <libro>/.zb/consumo.log. Misura ciò che è stato letto attraverso gli
strumenti, non i token: nessuna percentuale che non sia misurata.
"""
import datetime
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _letto(ti):
    """«righe:parole» del tratto letto (offset e limit dello strumento Read; predefinito 2000 righe)."""
    p = ti.get('file_path') or ''
    try:
        righe = open(p, encoding='utf-8', errors='replace').read().splitlines()
    except OSError:
        return '0:0'
    inizio = int(ti.get('offset') or 1)
    lim = int(ti.get('limit') or 2000)
    tratto = righe[inizio - 1:inizio - 1 + lim]
    return f'{len(tratto)}:{sum(len(r.split()) for r in tratto)}'


def annota(dati, ora=None):
    import hook_recinto
    cwd = dati.get('cwd') or os.getcwd()
    rad = hook_recinto.radice(os.environ.get('CLAUDE_PROJECT_DIR') or cwd)
    if not rad:
        return
    slug = hook_recinto.slug_attivo(rad)
    cartella = os.path.join(rad, 'libri', slug or '')
    if not slug or not os.path.isfile(os.path.join(cartella, 'libro.yaml')):
        return
    nome = dati.get('tool_name')
    ti = dati.get('tool_input') or {}
    if nome == 'Read':
        p = os.path.realpath(os.path.join(cwd, ti.get('file_path') or ''))
        ti = dict(ti, file_path=p)
        cosa, n = os.path.relpath(p, rad), _letto(ti)
    elif nome in ('Agent', 'Task'):
        nome, cosa, n = 'Agent', ti.get('subagent_type') or 'general-purpose', '0:0'
    else:
        return
    d = os.path.join(cartella, '.zb')
    os.makedirs(d, exist_ok=True)
    if not os.path.isfile(os.path.join(d, '.gitignore')):
        open(os.path.join(d, '.gitignore'), 'w', encoding='utf-8').write('*\n')
    ora = ora or datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(os.path.join(d, 'letture.log'), 'a', encoding='utf-8') as f:
        f.write(f'{ora}\t{dati.get("session_id") or "locale"}\t{nome}\t{cosa}\t{n}\n')


def hook():
    try:
        annota(json.loads(sys.stdin.read() or '{}'))
    except Exception as e:      # la misura non deve mai fermare la sessione
        print(f'consumo: errore ignorato ({e})', file=sys.stderr)
    return 0


def riassunto(cartella, libro, sid):
    import comune
    import conta
    import ruoli
    righe = []
    p = os.path.join(cartella, '.zb', 'letture.log')
    if os.path.isfile(p):
        righe = [r.rstrip('\n').split('\t') for r in open(p, encoding='utf-8') if r.count('\t') == 4]
    mie = [r for r in righe if r[1] == sid]
    letture = [r for r in mie if r[2] == 'Read']
    agenti = {}
    for r in mie:
        if r[2] == 'Agent':
            agenti[r[3]] = agenti.get(r[3], 0) + 1
    capitoli = sorted({rel for s, rel in ruoli.scritture(cartella) if s == sid and rel.startswith('04-manoscritto/')})
    parole = 0
    for rel in capitoli:
        if os.path.isfile(os.path.join(cartella, rel)):
            parole += conta.conta_testo(open(os.path.join(cartella, rel), encoding='utf-8').read())
    ore = [r[0] for r in mie]
    durata = '—'
    if len(ore) > 1:
        a, b = (datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ') for x in (min(ore), max(ore)))
        durata = f'{int((b - a).total_seconds() // 60)} min'
    return {'sessione': sid, 'capitoli': len(capitoli), 'parole': parole, 'file_letti': len({r[3] for r in letture}),
            'letture': len(letture), 'righe_lette': sum(int(r[4].split(':')[0]) for r in letture),
            'parole_lette': sum(int((r[4].split(':') + ['0'])[1]) for r in letture),
            'subagenti': sum(agenti.values()), 'per_tipo': agenti, 'durata': durata}


def main(argv):
    import comune
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: zb consumo <libro> [--sessione S] [--registra]')
    cartella, libro, _ = comune.carica_libro(args[0])
    sid = argv[argv.index('--sessione') + 1] if '--sessione' in argv else comune.sessione_corrente()[0]
    r = riassunto(cartella, libro, sid)
    tipi = ', '.join(f'{k} {v}' for k, v in sorted(r['per_tipo'].items())) or 'nessuno'
    riga = (f'sessione {r["sessione"]}: capitoli {r["capitoli"]}, parole {r["parole"]}, file letti {r["file_letti"]} '
            f'({r["letture"]} letture, {r["righe_lette"]} righe, {r["parole_lette"]} parole), subagenti {r["subagenti"]} ({tipi}), durata {r["durata"]}')
    print(riga)
    if '--registra' in argv:
        d = comune.prepara_zb(cartella)
        ora = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        with open(os.path.join(d, 'consumo.log'), 'a', encoding='utf-8') as f:
            f.write(f'{ora} {riga}\n')
        print('registrato in .zb/consumo.log')
    return 0


if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.exit(hook())
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:
        import comune
        if isinstance(e, comune.ErroreMotore):
            comune.esci_con_errore(e)
        raise

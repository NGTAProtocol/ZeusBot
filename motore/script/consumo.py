"""Misura del consumo per sessione (comando «zb consumo»). Misura, non stima: righe e parole lette dai file.

Uso: python3 -B consumo.py <libro> registra [--capitoli 1,2] [--subagenti N] [--file a.md,b.md]
     python3 -B consumo.py <libro> mostra
     python3 -B consumo.py <libro> confronto <N>
- registra: aggiunge una voce a <libro>/06-diagnostica/consumo.yaml per la sessione corrente: capitoli
  lavorati, parole di quei capitoli, file e righe letti (i file della riga «Letto» dell'ultimo zb avvio, i
  file di preparazione dei capitoli e quelli indicati con --file), subagenti chiamati, durata dal primo
  zb avvio della sessione.
- confronto N: per scrivere il capitolo N, righe e parole da leggere con le capsule (zb prepara) e senza
  (gli stessi file più i capitoli precedenti interi al posto delle capsule, e tutto il codex). Il modello
  non conta i token: righe e parole sono la misura disponibile; il rapporto si dichiara solo se misurato così.
Da motore (971b6df):
- hook PostToolUse (dati/hook-settings.esempio.json, matcher «Read|Agent|Task»; consumo.py senza argomenti): legge
  da stdin il JSON dell'hook e aggiunge una riga a <libro>/.zb/letture.log, con il libro attivo:
    <ora ISO>\t<sessione>\tRead\t<file relativo al repository>\t<righe lette>:<parole lette>
    <ora ISO>\t<sessione>\tAgent\t<tipo di subagente>\t0:0
  Non blocca mai (codice 0).
- python3 -B consumo.py <libro> [sessione] [--sessione S] [--registra]: per la sessione S (predefinita: quella
  corrente) riassume dalle letture registrate dall'hook: capitoli scritti (.zb/scritture.log), parole, file e righe
  letti, subagenti per tipo, durata. Con --registra aggiunge il riassunto a <libro>/.zb/consumo.log.
"""
import datetime
import os
import re
import sys
import time

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import conta  # noqa: E402

REL = '06-diagnostica/consumo.yaml'


def misura(cartella, rels):
    righe = parole = 0
    for r in rels:
        p = r if os.path.isabs(r) else os.path.join(cartella, r)
        if os.path.isfile(p):
            t = open(p, encoding='utf-8').read()
            righe += len(t.splitlines())
            parole += conta.conta_testo(t)
    return righe, parole


def opzione(argv, nome):
    return argv[argv.index(nome) + 1] if nome in argv and argv.index(nome) + 1 < len(argv) else None


def letti_dal_marker(cartella, sid):
    m = os.path.join(cartella, '.zb', f'letto-{sid}')
    if not os.path.isfile(m):
        return [], None
    rels = []
    for r in open(m, encoding='utf-8').read().splitlines():
        k = r.split(':', 1)[0]
        if k not in ('data', 'libro_commit', 'motore_commit') and not k.startswith(('profilo ', 'voce ')):
            rels.append(k)
    return rels, os.path.getmtime(m)


def registra(cartella, libro, argv):
    sid, _ = comune.sessione_corrente()
    rels, inizio = letti_dal_marker(cartella, sid)
    capitoli = [c for c in (opzione(argv, '--capitoli') or '').split(',') if c.strip()]
    for c in capitoli:
        p = f'06-diagnostica/preparazione/{int(c):02d}.md'
        if os.path.isfile(os.path.join(cartella, p)):
            rels.append(p)
            testo = open(os.path.join(cartella, p), encoding='utf-8').read()
            rels += re.findall(r'(?m)^- ([\w./\-]+\.md)$', testo)
    rels += [x for x in (opzione(argv, '--file') or '').split(',') if x.strip()]
    rels = list(dict.fromkeys(rels))
    righe, parole_lette = misura(cartella, rels)
    unita = dict(comune.unita(cartella, libro))
    scritte = sum(conta.conta_testo(open(unita[c], encoding='utf-8').read()) for c in capitoli if c in unita)
    voce = {'data': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'sessione': sid,
            'capitoli': capitoli, 'parole_capitoli': scritte, 'file_letti': len(rels), 'righe_lette': righe,
            'parole_lette': parole_lette, 'subagenti': int(opzione(argv, '--subagenti') or 0),
            'durata_minuti': round((time.time() - inizio) / 60, 1) if inizio else None}
    p = os.path.join(cartella, REL)
    dati = (comune.leggi_yaml(p) or {}) if os.path.isfile(p) else {}
    dati.setdefault('sessioni', []).append(voce)
    comune.scrivi(cartella, REL, yaml.safe_dump(dati, sort_keys=False, allow_unicode=True))
    print(f'Consumo registrato: {len(rels)} file, {righe} righe, {parole_lette} parole lette; capitoli '
          f'{",".join(capitoli) or "—"} ({scritte} parole); subagenti {voce["subagenti"]}; durata '
          f'{voce["durata_minuti"] if voce["durata_minuti"] is not None else "—"} min. ({REL})')


def confronto(cartella, libro, n):
    import codex
    import prepara
    rel, _, _, _ = prepara.prepara(cartella, libro, n)
    testo = open(os.path.join(cartella, rel), encoding='utf-8').read()
    con = [rel] + re.findall(r'(?m)^- ([\w./\-]+\.md)$', testo)
    unita = dict(comune.unita(cartella, libro))
    senza = [x for x in con if not x.startswith('07-capsule/') and '/codex/' not in x]
    senza += [os.path.relpath(unita[str(i)], cartella) for i in range(1, n) if str(i) in unita]
    senza += [v['file'] for v in codex.schede(cartella).values()] + ['02-bibbia/bibbia.md']
    return misura(cartella, con), misura(cartella, list(dict.fromkeys(senza)))


# ---------------------------------------------------------------- hook PostToolUse e riassunto (da motore)

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
    d = comune.prepara_zb(cartella)
    ora = ora or datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(os.path.join(d, 'letture.log'), 'a', encoding='utf-8') as f:
        f.write(f'{ora}\t{dati.get("session_id") or "locale"}\t{nome}\t{cosa}\t{n}\n')


def hook():
    import json
    try:
        annota(json.loads(sys.stdin.read() or '{}'))
    except Exception as e:      # la misura non deve mai fermare la sessione
        print(f'consumo: errore ignorato ({e})', file=sys.stderr)
    return 0


def riassunto(cartella, libro, sid):
    import ruolo
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
    capitoli = sorted({rel for s, rel in ruolo.scritture(cartella) if s == sid and rel.startswith('04-manoscritto/')})
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


def sessione(cartella, libro, argv):
    sid = argv[argv.index('--sessione') + 1] if '--sessione' in argv else comune.sessione_corrente()[0]
    r = riassunto(cartella, libro, sid)
    tipi = ', '.join(f'{k} {v}' for k, v in sorted(r['per_tipo'].items())) or 'nessuno'
    riga = (f'sessione {r["sessione"]}: capitoli {r["capitoli"]}, parole {r["parole"]}, file letti {r["file_letti"]} '
            f'({r["letture"]} letture, {r["righe_lette"]} righe, {r["parole_lette"]} parole), subagenti {r["subagenti"]} '
            f'({tipi}), durata {r["durata"]}')
    print(riga)
    if '--registra' in argv:
        d = comune.prepara_zb(cartella)
        ora = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        with open(os.path.join(d, 'consumo.log'), 'a', encoding='utf-8') as f:
            f.write(f'{ora} {riga}\n')
        print('registrato in .zb/consumo.log')


def main(argv):
    pulito = [a for i, a in enumerate(argv) if a != '--sessione' and (i == 0 or argv[i - 1] != '--sessione')]
    args = comune.argomenti(pulito)
    if not args:
        raise comune.ErroreMotore('Uso: consumo.py <libro> [sessione] [--sessione S] [--registra] | '
                                  'registra|mostra|confronto <N>')
    cartella, libro, _ = comune.carica_libro(args[0])
    if len(args) == 1 or args[1] == 'sessione':
        sessione(cartella, libro, argv)
    elif args[1] == 'registra':
        registra(cartella, libro, argv)
    elif args[1] == 'mostra':
        p = os.path.join(cartella, REL)
        sess = ((comune.leggi_yaml(p) or {}).get('sessioni') or []) if os.path.isfile(p) else []
        for s in sess[-30:]:
            print(f'{s["data"]} capitoli {",".join(s["capitoli"]) or "—"}: {s["righe_lette"]} righe lette, '
                  f'{s["subagenti"]} subagenti, {s["durata_minuti"]} min')
        print(f'Sessioni: {len(sess)}; righe lette in tutto: {sum(s["righe_lette"] for s in sess)}.')
    elif args[1] == 'confronto' and len(args) > 2:
        (rc, pc), (rs, ps) = confronto(cartella, libro, int(args[2]))
        print(f'Capitolo {args[2]}: con le capsule {rc} righe / {pc} parole da leggere; senza {rs} righe / {ps} parole.')
    else:
        raise comune.ErroreMotore('Uso: consumo.py <libro> [sessione] [--sessione S] [--registra] | '
                                  'registra|mostra|confronto <N>')
    return 0


if __name__ == '__main__':
    if len(sys.argv) == 1:          # hook PostToolUse
        sys.exit(hook())
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

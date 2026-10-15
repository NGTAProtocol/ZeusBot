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


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2:
        raise comune.ErroreMotore('Uso: consumo.py <libro> registra|mostra|confronto <N>')
    cartella, libro, _ = comune.carica_libro(args[0])
    if args[1] == 'registra':
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
        raise comune.ErroreMotore('Uso: consumo.py <libro> registra|mostra|confronto <N>')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

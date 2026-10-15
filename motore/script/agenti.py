"""Subagenti del livello editoriale (editoriale/agenti/, editoriale/risparmio-token.md).

Uso: zb agenti stato | zb agenti attiva [--ok] | zb agenti disattiva | zb agenti prossimo <libro>
- stato: formato dei file degli agenti (frontmatter name, description, tools, model; formato dei subagenti di
  Claude Code), coerenza del campo model con dati/modelli-agenti.yaml (fonte unica), agenti attivi o no.
- attiva: solo sul ramo di un libro (mai sul ramo «motore») e solo dopo l'«ok» dell'autore (--ok): copia gli
  agenti in <repo>/.claude/agents/ con il modello di dati/modelli-agenti.yaml. Senza --ok mostra cosa farebbe.
- disattiva: toglie da .claude/agents/ solo i file uguali a quelli che attiva scriverebbe.
- prossimo <libro>: le chiamate del passo corrente per la sessione principale, che non scrive prosa:
  scrittura in sequenza (un capitolo per volta); line, copy e capsule a gruppi di al massimo
  parallelo_max (dati/orchestrazione.yaml). Non scrive nulla.
"""
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

CAMPI = ('name', 'description', 'tools', 'model')
MODELLI_AMMESSI = {'opus', 'sonnet', 'haiku', 'fable', 'inherit'}


def cartella_agenti():
    return os.path.join(comune.radice_motore(), 'editoriale', 'agenti')


def modelli():
    return comune.leggi_yaml(os.path.join(comune.radice_motore(), 'dati', 'modelli-agenti.yaml'))['modelli']


def orchestrazione():
    return comune.leggi_yaml(os.path.join(comune.radice_motore(), 'dati', 'orchestrazione.yaml'))


def frontmatter(testo):
    m = re.match(r'^---\n(.*?)\n---\n', testo, re.S)
    if not m:
        return None
    return {k.strip(): v.strip() for k, v in (r.split(':', 1) for r in m.group(1).splitlines() if ':' in r)}


def controlla_formato():
    """[(file, problema)] dei file degli agenti; [] se tutto è in regola."""
    err, mod = [], modelli()
    for f in sorted(os.listdir(cartella_agenti())):
        if not f.endswith('.md'):
            continue
        fm = frontmatter(open(os.path.join(cartella_agenti(), f), encoding='utf-8').read())
        if fm is None:
            err.append((f, 'manca il frontmatter ---'))
            continue
        for c in CAMPI:
            if not fm.get(c):
                err.append((f, f'campo «{c}» mancante'))
        if fm.get('name') and fm['name'] != f[:-3]:
            err.append((f, f'name «{fm["name"]}» diverso dal nome del file'))
        if ':' in fm.get('name', ''):
            err.append((f, 'name con «:» (riservato ai plugin)'))
        m = fm.get('model', '')
        if m and m not in MODELLI_AMMESSI and not m.startswith('claude-'):
            err.append((f, f'model «{m}» non ammesso'))
        if fm.get('name') in mod and m != mod[fm['name']]:
            err.append((f, f'model «{m}» diverso da dati/modelli-agenti.yaml ({mod[fm["name"]]})'))
        if fm.get('name') and fm['name'] not in mod:
            err.append((f, 'agente assente da dati/modelli-agenti.yaml'))
    return err


def generati():
    """{nome file: testo} come li scrive «attiva»: model da dati/modelli-agenti.yaml."""
    out, mod = {}, modelli()
    for f in sorted(os.listdir(cartella_agenti())):
        if f.endswith('.md'):
            t = open(os.path.join(cartella_agenti(), f), encoding='utf-8').read()
            nome = f[:-3]
            if nome in mod:
                t = re.sub(r'(?m)^model:.*$', f'model: {mod[nome]}', t, count=1)
            out[f] = t
    return out


def radice_progetto(argv):
    if '--progetto' in argv:
        return os.path.realpath(argv[argv.index('--progetto') + 1])
    r = subprocess.run(['git', '-C', comune.radice_motore(), 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    return r.stdout.strip() or os.path.dirname(comune.radice_motore())


def stato(argv):
    dest = os.path.join(radice_progetto(argv), '.claude', 'agents')
    err = controlla_formato()
    print(f'Agenti in editoriale/agenti/: {len(generati())}; formato: ' + ('OK' if not err else f'{len(err)} problemi'))
    for f, e in err:
        print(f'  - {f}: {e}')
    attivi = [f for f, t in generati().items() if os.path.isfile(os.path.join(dest, f))
              and open(os.path.join(dest, f), encoding='utf-8').read() == t]
    print(f'{dest}: ' + (f'{len(attivi)} agenti del motore attivi' if attivi else 'nessun agente del motore attivo'))
    for nome, m in modelli().items():
        print(f'  {nome}: {m}')
    return 1 if err else 0


def attiva(argv):
    rad = radice_progetto(argv)
    ramo = comune.ramo(rad)
    if ramo == 'motore':
        raise comune.ErroreMotore('Sul ramo «motore» gli agenti restano spenti: si attivano solo sul ramo di un libro.')
    libri = os.path.join(rad, 'libri')
    if not os.path.isdir(libri) or not any(os.path.isfile(os.path.join(libri, d, 'libro.yaml')) for d in os.listdir(libri)):
        raise comune.ErroreMotore('Nessun libro in libri/<slug>/: gli agenti si attivano solo sul ramo di un libro.')
    tutti = controlla_formato()
    err = [(f, e) for f, e in tutti if 'diverso da dati/modelli-agenti.yaml' not in e]
    if err:
        raise comune.ErroreMotore('Agenti non validi:\n- ' + '\n- '.join(f'{f}: {e}' for f, e in err))
    for f, e in tutti:
        if (f, e) not in err:      # vale il file di dati, fonte unica dei modelli
            print(f'AVVISO {f}: {e}; uso il valore di dati/modelli-agenti.yaml.')
    dest = os.path.join(rad, '.claude', 'agents')
    diversi = [f for f, t in generati().items() if os.path.isfile(os.path.join(dest, f))
               and open(os.path.join(dest, f), encoding='utf-8').read() != t]
    if diversi:
        raise comune.ErroreMotore(f'In {dest} ci sono file con lo stesso nome e contenuto diverso: {", ".join(diversi)}; '
                                  'non li sovrascrivo.')
    if '--ok' not in argv:
        print(f'Copierei in {dest} {len(generati())} agenti ({", ".join(f[:-3] for f in generati())}), con i modelli '
              'di dati/modelli-agenti.yaml. Valgono per ogni sessione su questo ramo.\n'
              'Per confermare, dopo l\'«ok» dell\'autore: zb agenti attiva --ok')
        return 0
    os.makedirs(dest, exist_ok=True)
    for f, t in generati().items():
        with open(os.path.join(dest, f), 'w', encoding='utf-8') as h:
            h.write(t)
    print(f'Attivati {len(generati())} agenti in {dest}. Valgono dalla prossima sessione. Salvali con un commit a parte.')
    return 0


def disattiva(argv):
    dest = os.path.join(radice_progetto(argv), '.claude', 'agents')
    tolti = []
    for f, t in generati().items():
        p = os.path.join(dest, f)
        if os.path.isfile(p) and open(p, encoding='utf-8').read() == t:
            os.remove(p)
            tolti.append(f)
    try:
        os.rmdir(dest)
    except OSError:
        pass
    print(f'Tolti {len(tolti)} agenti da {dest}.' + (' Salva la rimozione con un commit.' if tolti else ''))
    return 0


def a_gruppi(elenco, n):
    return [elenco[i:i + n] for i in range(0, len(elenco), n)]


def prossimo(argv):
    import capsule
    import fase
    import revisione
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: zb agenti prossimo <libro>')
    cartella, libro, _ = comune.carica_libro(args[0])
    st = fase.carica_stato(cartella)
    o = orchestrazione()
    n = int(o['parallelo_max'])
    agente = o['agente_di_fase'].get(st['fase'])
    rel = os.path.relpath(cartella, comune.radice_git(cartella))
    righe = [f'Fase {st["fase"]}; gate {st["gate_in_attesa"] or "nessuno"}. La sessione principale non scrive prosa: '
             f'chiama l\'agente, legge solo la risposta (massimo {o["righe_risposta"]} righe).']
    if st['gate_in_attesa']:
        righe.append('Gate aperto: prima la risposta dell\'autore (avanti, ok, correggi).')
    elif st['fase'] == 'stesura':
        mancano = capsule.mancanti(cartella, libro, st)
        if mancano:
            righe.append(f'Prima le capsule (agente capsula, in parallelo a gruppi di {n}):')
            righe += [f'  gruppo: ' + ', '.join(f'capsula {rel} capitolo {c}' for c in g) for g in a_gruppi(mancano, n)]
        righe.append(f'Poi, in sequenza (mai in parallelo): scrittore-voce {rel} {st["passo"]}; dopo: zb esito, zb capsula.')
    elif st['fase'] in ('line', 'copy'):
        cart = revisione.PER_CAPITOLO[st['fase']]
        da_fare = [u for u, _ in comune.unita(cartella, libro)
                   if not os.path.isfile(os.path.join(cartella, cart, f'{revisione.nome_report(u)}.md'))]
        righe.append(f'{agente}, in parallelo a gruppi di al massimo {n} (con limiti o errori 429: '
                     f'{" poi ".join(map(str, o["riduzione"]))}):')
        righe += ['  gruppo: ' + ', '.join(f'{agente} {rel} {u}' for u in g) for g in a_gruppi(da_fare, n)] or ['  niente da fare']
    elif agente:
        righe.append(f'{agente} {rel} (un solo agente; report in 06-diagnostica/).')
    else:
        righe.append(fase.prossimo(st))
    righe.append('I subagenti non fanno commit né push: dopo ogni gruppo zb esito/zb capsula, salvataggio e zb push.')
    print('\n'.join(righe))
    return 0


def main(argv):
    azione = argv[0] if argv else 'stato'
    resto = argv[1:]
    if azione == 'stato':
        return stato(resto)
    if azione == 'attiva':
        return attiva(resto)
    if azione == 'disattiva':
        return disattiva(resto)
    if azione == 'prossimo':
        return prossimo(resto)
    raise comune.ErroreMotore('Uso: zb agenti stato | attiva [--ok] | disattiva | prossimo <libro>')


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

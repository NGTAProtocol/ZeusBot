"""Subagenti e comandi di Claude Code per i rami dei libri (comando «zb agenti»).

Uso: python3 -B agenti.py stato | attiva [--ok] | disattiva [--progetto <radice>] | prossimo <libro>
Fonte unica: motore/editoriale/agenti/*.md (più motore/editoriale/lingue/agenti/*.md, traduzione) e
motore/editoriale/comandi/*.md. «attiva» li copia in <radice>/.claude/agents/ e <radice>/.claude/commands/,
scrivendo negli agenti il campo «model:» preso da motore/dati/modelli-ruoli.yaml (unica fonte dei modelli).
- Solo sui rami dei libri: rifiutato sul ramo «motore» e con il lavoro sul motore in corso
  (sul ramo del motore agenti e comandi restano spenti; la prova lo controlla).
- Senza --ok mostra cosa scriverebbe: l'«ok» lo dà l'autore.
- Non sovrascrive file che non ha scritto lui; «disattiva» toglie solo i propri (riga di firma).
Formato verificato sulla documentazione ufficiale (2026-10-15): agenti con frontmatter name e description
obbligatori, tools e model facoltativi; comandi in .claude/commands/<nome>.md (formato ancora supportato; le
skill in .claude/skills/ sono il formato raccomandato per i comandi nuovi), argomenti con $ARGUMENTS.
Da motore (971b6df):
- stato controlla anche il formato degli agenti (name uguale al nome del file, description, model ammesso) e
  segnala un «model:» del file diverso da dati/modelli-ruoli.yaml (vale il file di dati) o un agente assente da lì;
- prossimo <libro>: le chiamate del passo corrente per la sessione principale, che non scrive prosa: scrittura in
  sequenza (un capitolo per volta); line, copy e capsule a gruppi di al massimo parallelo_massimo
  (dati/modelli-ruoli.yaml); regole in dati/orchestrazione.yaml. Non scrive nulla.
"""
import os
import re
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import hook_recinto  # noqa: E402

FIRMA = '<!-- zb: installato da «zb agenti attiva»; fonte: motore/editoriale/ -->'
MODELLI_AMMESSI = {'opus', 'sonnet', 'haiku', 'fable', 'inherit'}


def sorgenti(motore):
    e = os.path.join(motore, 'editoriale')
    out = []
    for sub, dest in (('agenti', 'agents'), (os.path.join('lingue', 'agenti'), 'agents'), ('comandi', 'commands')):
        d = os.path.join(e, sub)
        if os.path.isdir(d):
            out += [(os.path.join(d, f), dest, f) for f in sorted(os.listdir(d)) if f.endswith('.md')]
    return out


def modelli(motore):
    d = comune.leggi_yaml(os.path.join(motore, 'dati', 'modelli-ruoli.yaml'))
    return {r: d['livelli'][liv] for r, liv in d['ruoli'].items()}, d.get('parallelo_massimo', 3)


def generato(src, dest, mod):
    t = open(src, encoding='utf-8').read()
    if dest == 'agents':
        m = re.match(r'^---\n(.*?)\n---\n', t, re.S)
        if not m:
            raise comune.ErroreMotore(f'{src}: frontmatter mancante')
        fm = yaml.safe_load(m.group(1))
        for k in ('name', 'description'):
            if not fm.get(k):
                raise comune.ErroreMotore(f'{src}: campo obbligatorio «{k}» mancante nel frontmatter')
        nome = fm['name']
        if nome in mod:     # unica fonte dei modelli: dati/modelli-ruoli.yaml (sostituisce un «model:» del file)
            corpo = re.sub(r'(?m)^model:.*\n?', '', m.group(1)).rstrip('\n')
            t = t.replace(m.group(0), f'---\n{corpo}\nmodel: {mod[nome]}\n---\n', 1)
    return t.rstrip('\n') + '\n\n' + FIRMA + '\n'


def controlla_formato(motore):
    """[(file, problema, grave)] degli agenti (editoriale/agenti/, lingue/agenti/); grave=False: vale il file di dati."""
    mod, _ = modelli(motore)
    out = []
    for src, dest, f in sorgenti(motore):
        if dest != 'agents':
            continue
        m = re.match(r'^---\n(.*?)\n---\n', open(src, encoding='utf-8').read(), re.S)
        if not m:
            out.append((f, 'manca il frontmatter ---', True))
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        for c in ('name', 'description'):
            if not fm.get(c):
                out.append((f, f'campo «{c}» mancante', True))
        if fm.get('name') and fm['name'] != f[:-3]:
            out.append((f, f'name «{fm["name"]}» diverso dal nome del file', True))
        md = str(fm.get('model') or '')
        if md and md not in MODELLI_AMMESSI and not md.startswith('claude-'):
            out.append((f, f'model «{md}» non ammesso', True))
        if fm.get('name') and fm['name'] not in mod:
            out.append((f, 'agente assente da dati/modelli-ruoli.yaml', True))
        elif md and fm.get('name') in mod and md != mod[fm['name']]:
            out.append((f, f'model «{md}» diverso da dati/modelli-ruoli.yaml ({mod[fm["name"]]})', False))
    return out


def orchestrazione(motore):
    return comune.leggi_yaml(os.path.join(motore, 'dati', 'orchestrazione.yaml'))


def a_gruppi(elenco, n):
    return [elenco[i:i + n] for i in range(0, len(elenco), n)]


def prossimo(motore, argv):
    """Chi chiamare adesso (da motore, con i nomi del pacchetto). Non scrive nulla."""
    import capsula
    import fase
    import percorso
    args = comune.argomenti(argv)
    if len(args) < 2:
        raise comune.ErroreMotore('Uso: zb agenti prossimo <libro>')
    cartella, libro, _ = comune.carica_libro(args[1])
    st = fase.carica_stato(cartella)
    o = orchestrazione(motore)
    _, n = modelli(motore)
    agente = o['agente_di_fase'].get(st['fase'])
    rel = os.path.relpath(cartella, comune.radice_git(cartella))
    righe = [f'Fase {st["fase"]}; gate {st["gate_in_attesa"] or "nessuno"}. La sessione principale non scrive prosa: '
             f'chiama l\'agente, legge solo la risposta (massimo {o["righe_risposta"]} righe).']
    if st['gate_in_attesa']:
        righe.append(f'Gate «{st["gate_in_attesa"]}» aperto: prima la risposta dell\'autore.')
    elif st['fase'] == 'stesura':
        mancano = capsula.mancanti(cartella, libro, st)
        if mancano:
            righe.append(f'Prima le capsule (agente capsula, in parallelo a gruppi di {n}):')
            righe += ['  gruppo: ' + ', '.join(f'capsula {rel} capitolo {c}' for c in g) for g in a_gruppi(mancano, n)]
        if libro.get('revisione_capitolo') == 'obbligatoria':
            righe.append(f'Poi, in sequenza (mai in parallelo): zb prepara, scrittore-voce {rel} {st["passo"]}; poi '
                         f'zb ruolo {rel} diagnosta N (misure del motore prima del revisore: se si ferma, non chiamare '
                         'il diagnosta, prima la correzione di chi scrive); con le misure superate, diagnosta con la '
                         'prima riga e 06-diagnostica/misure/NN.md; dopo: zb esito, zb capsula.')
        else:
            righe.append(f'Poi, in sequenza (mai in parallelo): zb prepara, scrittore-voce {rel} {st["passo"]}; dopo: '
                         'zb esito, zb capsula.')
    elif st['fase'] in ('line', 'copy') and (st.get('sottofase') or 'proposte') == 'proposte':
        da_fare = [str(u) for u, r in percorso.capitoli(cartella, libro)
                   if not os.path.isfile(os.path.join(cartella, '06-diagnostica', st['fase'], f'{percorso.nn(u)}.md'))]
        righe.append(f'{agente}, in parallelo a gruppi di al massimo {n} (con limiti o errori 429: '
                     f'{" poi ".join(map(str, o["riduzione"]))}):')
        righe += ['  gruppo: ' + ', '.join(f'{agente} {rel} {u}' for u in g) for g in a_gruppi(da_fare, n)] or ['  niente da fare']
    elif agente:
        righe.append(f'{agente} {rel} (un solo agente; rapporti in 06-diagnostica/).')
    else:
        righe.append(fase.prossimo(st))
    righe.append('I subagenti non fanno commit né push: dopo ogni gruppo zb esito/zb capsula, poi zb salva.')
    print('\n'.join(righe))
    return 0


def piano(rad, motore):
    mod, _ = modelli(motore)
    return [(os.path.join(rad, '.claude', dest, f), generato(src, dest, mod)) for src, dest, f in sorgenti(motore)]


def nostro(p):
    return os.path.isfile(p) and FIRMA in open(p, encoding='utf-8').read()


def main(argv):
    motore = comune.radice_motore()
    rad = os.path.realpath(argv[argv.index('--progetto') + 1]) if '--progetto' in argv else comune.radice_git(motore)
    pulito = [a for i, a in enumerate(argv) if a != '--progetto' and (i == 0 or argv[i - 1] != '--progetto')]
    args = comune.argomenti(pulito)
    azione = args[0] if args else 'stato'
    voci = piano(rad, motore)
    installati = [p for p, _ in voci if nostro(p)]
    if azione == 'stato':
        mod, par = modelli(motore)
        err = controlla_formato(motore)
        print(f'Agenti e comandi installati: {len(installati)} di {len(voci)} in {os.path.join(rad, ".claude")}; '
              f'parallelo massimo {par}.')
        print('Formato degli agenti: ' + ('OK' if not err else f'{len(err)} problemi'))
        for f, e, _ in err:
            print(f'  - {f}: {e}')
        for nome, m in mod.items():
            print(f'  {nome}: {m}')
        return 1 if any(g for _, _, g in err) else 0
    if azione == 'prossimo':
        return prossimo(motore, args)
    ramo = subprocess.run(['git', '-C', rad, 'branch', '--show-current'], capture_output=True, text=True).stdout.strip()
    if azione == 'attiva':
        if ramo == 'motore' or hook_recinto.lavoro(rad) == 'motore':
            raise comune.ErroreMotore('Agenti e comandi si attivano solo sui rami dei libri: sul ramo del motore '
                                      '(o con il lavoro sul motore in corso) restano spenti.')
        gravi = [f'{f}: {e}' for f, e, g in controlla_formato(motore) if g]
        if gravi:
            raise comune.ErroreMotore('Agenti non validi:\n- ' + '\n- '.join(gravi))
        for f, e, g in controlla_formato(motore):
            if not g:       # vale il file di dati, fonte unica dei modelli
                print(f'AVVISO {f}: {e}; uso il valore di dati/modelli-ruoli.yaml.')
        estranei = [p for p, _ in voci if os.path.exists(p) and not nostro(p)]
        if estranei:
            raise comune.ErroreMotore('File già presenti e non del motore (non li sovrascrivo):\n- ' + '\n- '.join(estranei))
        if '--ok' not in argv:
            print(f'Creerei {len(voci)} file in {os.path.join(rad, ".claude")} (agents/ e commands/), con i modelli di '
                  'motore/dati/modelli-ruoli.yaml. Valgono per ogni sessione su questo ramo.\n'
                  'Dopo l\'«ok» dell\'autore: zb agenti attiva --ok')
            return 0
        for p, testo in voci:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w', encoding='utf-8') as f:
                f.write(testo)
        print(f'Installati {len(voci)} file in .claude/agents/ e .claude/commands/. Salvali con un commit (zb salva).')
        return 0
    if azione == 'disattiva':
        for p in installati:
            os.remove(p)
        for d in ('agents', 'commands'):
            try:
                os.rmdir(os.path.join(rad, '.claude', d))
            except OSError:
                pass
        print(f'Tolti {len(installati)} file del motore da .claude/. Salva la rimozione con un commit.')
        return 0
    raise comune.ErroreMotore('Uso: agenti stato | attiva [--ok] | disattiva | prossimo <libro>')


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

"""Codex del libro: schede dei personaggi e dei luoghi in <libro>/02-bibbia/codex/, una per file.

Uso: python3 -B codex.py <libro> verifica            (comando «zb codex <libro> verifica»; non scrive)
     python3 -B codex.py <libro> filtra @char:a @loc:b  (elenca i file delle schede con quei tag)
     python3 -B codex.py <libro> filtra --capitolo N   (i tag della scheda del capitolo N in 05-scaletta.md)
Ogni scheda ha una riga con il suo tag: «@char:<id>» (personaggio) oppure «@loc:<id>» (luogo); <id> in
minuscole, cifre e trattini, uguale al nome del file senza «.md». Campi facoltativi riconosciuti:
«- Alias: a, b» (altre grafie ammesse) e «- Stato: morto nel capitolo N» (dopo N il personaggio può essere
solo ricordato: un tag @char in una scheda di capitolo successiva è KO, idea dei controlli di continuità
deterministici di danjdewhurst/story-skills, MIT, riscritta).
Il filtro non usa il modello: legge i tag e restituisce i file (zero token di ragionamento).
"""
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

CARTELLA = os.path.join('02-bibbia', 'codex')
TAG = re.compile(r'@(char|loc):([a-z0-9][a-z0-9\-]*)')


def id_da_nome(nome):
    return comune.nome_file(nome)


def dal_briefing(b):
    """{percorso relativo: testo} delle schede dei personaggi di «Personaggi chiave» (e «Schede dei personaggi»)."""
    out = {}
    for p in b['personaggi']:
        parti = [x.strip() for x in p.split('—')]
        nome = parti[0]
        i = id_da_nome(nome)
        righe = [f'# {nome}', '', f'@char:{i}', '', f'- In breve: {" — ".join(parti[1:])}', '- Alias:']
        righe += [f'- {r}' for r in b.get('schede', {}).get(nome, [])]
        righe += ['- Stato:', '']
        out[os.path.join(CARTELLA, f'{i}.md')] = '\n'.join(righe)
    return out


def schede(cartella):
    """{('char'|'loc', id): {'file': rel, 'nome': titolo, 'alias': [...], 'morto': N|None, 'errori': [...]}}"""
    d = os.path.join(cartella, CARTELLA)
    out = {}
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if not f.endswith('.md'):
            continue
        rel = os.path.join(CARTELLA, f)
        t = open(os.path.join(d, f), encoding='utf-8').read()
        tag = TAG.findall(t)
        errori = []
        if len(set(tag)) != 1:
            errori.append(f'{rel}: serve esattamente un tag @char:<id> o @loc:<id> (trovati {len(set(tag))})')
        tipo, i = tag[0] if tag else ('?', f[:-3])
        if tag and i != f[:-3]:
            errori.append(f'{rel}: il tag @{tipo}:{i} non corrisponde al nome del file')
        titolo = re.search(r'(?m)^#\s+(.+)$', t)
        alias = re.search(r'(?mi)^-\s*Alias:\s*(.*)$', t)
        morto = re.search(r'(?mi)^-\s*Stato:.*?(?:morto|morta|dead|died)\D*(\d+)', t)
        chiave = (tipo, i)
        if chiave in out:
            errori.append(f'{rel}: tag duplicato @{tipo}:{i}')
        out[chiave] = {'file': rel, 'nome': titolo.group(1).strip() if titolo else i,
                       'alias': [a.strip() for a in (alias.group(1) if alias else '').split(',') if a.strip()],
                       'morto': int(morto.group(1)) if morto else None, 'errori': errori}
    return out


def filtra(cartella, tags):
    """File delle schede con i tag indicati, nell'ordine dato; tag sconosciuti in un elenco a parte."""
    s = schede(cartella)
    trovati, ignoti = [], []
    for t in tags:
        if t in s:
            trovati.append(s[t]['file'])
        else:
            ignoti.append(f'@{t[0]}:{t[1]}')
    return trovati, ignoti


def verifica(cartella):
    import struttura
    s = schede(cartella)
    out = [e for v in s.values() for e in v['errori']]
    for n, sk in sorted(struttura.schede(cartella).items(), key=lambda x: int(x[0])):
        for t in struttura.tag_di(sk):
            if t not in s:
                out.append(f'05-scaletta.md, capitolo {n}: @{t[0]}:{t[1]} non ha una scheda nel codex')
            elif t[0] == 'char' and s[t]['morto'] is not None and int(n) > s[t]['morto']:
                out.append(f'05-scaletta.md, capitolo {n}: @char:{t[1]} è morto nel capitolo {s[t]["morto"]}; '
                           'dopo può essere solo ricordato (togli il tag)')
    return out


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2 or args[1] not in ('verifica', 'filtra'):
        raise comune.ErroreMotore('Uso: codex.py <libro> verifica | filtra @char:<id> … | filtra --capitolo N')
    cartella, libro, _ = comune.carica_libro(args[0])
    if args[1] == 'verifica':
        p = verifica(cartella)
        for x in p[:38]:
            print(f'KO {x}')
        print(f'Codex: {len(schede(cartella))} schede; ' + ('OK' if not p else f'{len(p)} problemi'))
        return 1 if p else 0
    if '--capitolo' in argv:
        import struttura
        n = argv[argv.index('--capitolo') + 1]
        tags = struttura.tag_di(struttura.schede(cartella).get(str(int(n)), {}))
    else:
        tags = TAG.findall(' '.join(args[2:]))
    trovati, ignoti = filtra(cartella, tags)
    for f in trovati:
        print(f)
    for x in ignoti:
        print(f'AVVISO {x}: nessuna scheda nel codex')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

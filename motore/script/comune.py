"""Funzioni comuni del motore (proposta B.3, B.4, B.9).

Trova il libro da un percorso, carica libro.yaml e il profilo di genere,
valida con gli schemi di motore/dati/, legge il ramo da git e scrive solo
dentro la cartella del libro (scrittura recintata).
"""
import copy
import os
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True


class ErroreMotore(Exception):
    """Errore che ferma il motore con un messaggio per l'autore."""


def radice_motore():
    """Cartella motore/: --radice, poi ZB_RADICE, poi la posizione di questo file."""
    for i, a in enumerate(sys.argv):
        if a == '--radice' and i + 1 < len(sys.argv):
            return os.path.realpath(sys.argv[i + 1])
        if a.startswith('--radice='):
            return os.path.realpath(a.split('=', 1)[1])
    if os.environ.get('ZB_RADICE'):
        return os.path.realpath(os.environ['ZB_RADICE'])
    return os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))


def leggi_yaml(percorso):
    with open(percorso, encoding='utf-8') as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------- schemi

def valida(dati, schema, dove='libro.yaml'):
    """Restituisce l'elenco degli errori di `dati` rispetto a `schema`."""
    errori = []
    _valida(dati, schema, dove, errori)
    return errori


def _numero(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _valida(x, s, dove, errori):
    if x is None:
        if not s.get('nullo') and s.get('tipo') != 'qualsiasi':
            errori.append(f'{dove}: valore mancante (null)')
        return
    tipo = s.get('tipo', 'qualsiasi')
    if tipo == 'qualsiasi':
        return
    if tipo == 'mappa':
        if not isinstance(x, dict):
            errori.append(f'{dove}: atteso una mappa')
            return
        campi = s.get('campi', {})
        for nome, sc in campi.items():
            if sc.get('obbligatorio') and nome not in x:
                errori.append(f'{dove}.{nome}: campo obbligatorio mancante')
        for nome, val in x.items():
            if nome in campi:
                _valida(val, campi[nome], f'{dove}.{nome}', errori)
            elif not s.get('altri_campi'):
                errori.append(f'{dove}.{nome}: campo non previsto dallo schema')
    elif tipo == 'lista':
        if not isinstance(x, list):
            errori.append(f'{dove}: attesa una lista')
            return
        if 'elementi' in s:
            for i, v in enumerate(x):
                _valida(v, s['elementi'], f'{dove}[{i}]', errori)
    elif tipo == 'testo':
        if not isinstance(x, str) or not x.strip():
            errori.append(f'{dove}: atteso un testo non vuoto')
    elif tipo == 'intero':
        if not isinstance(x, int) or isinstance(x, bool):
            errori.append(f'{dove}: atteso un numero intero')
    elif tipo == 'numero':
        if not _numero(x):
            errori.append(f'{dove}: atteso un numero')
    elif tipo == 'booleano':
        if not isinstance(x, bool):
            errori.append(f'{dove}: atteso true o false')
    elif tipo == 'intervallo':
        if not (isinstance(x, list) and len(x) == 2 and all(_numero(v) for v in x)):
            errori.append(f'{dove}: atteso un intervallo [a, b]')
        elif x[0] > x[1]:
            errori.append(f'{dove}: intervallo con il primo valore maggiore del secondo')
    elif tipo == 'scelta':
        if x not in s.get('valori', []):
            errori.append(f'{dove}: valore «{x}» non ammesso (ammessi: {", ".join(map(str, s["valori"]))})')
    else:
        errori.append(f'{dove}: tipo di schema sconosciuto «{tipo}»')


def carica_schema(nome):
    return leggi_yaml(os.path.join(radice_motore(), 'dati', f'{nome}.schema.yaml'))


# ---------------------------------------------------------------- libro

def trova_libro(percorso):
    """Cartella del libro: libro.yaml indicato, o cercato verso l'alto fino alla radice git."""
    p = os.path.realpath(percorso)
    if os.path.isfile(p):
        if os.path.basename(p) == 'libro.yaml':
            return os.path.dirname(p)
        p = os.path.dirname(p)
    if not os.path.isdir(p):
        raise ErroreMotore(f'Percorso inesistente: {percorso}')
    limite = radice_git(p)
    while True:
        if os.path.isfile(os.path.join(p, 'libro.yaml')):
            return p
        if p == limite or os.path.dirname(p) == p:
            break
        p = os.path.dirname(p)
    raise ErroreMotore(f'Nessun libro.yaml sopra {percorso}. Per un libro nuovo: zb nuovo <briefing>')


def radice_git(cartella):
    try:
        r = subprocess.run(['git', '-C', cartella, 'rev-parse', '--show-toplevel'],
                           capture_output=True, text=True, check=True)
        return os.path.realpath(r.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return '/'


def ramo(cartella):
    """Ramo corrente, letto da git (mai da un file)."""
    r = subprocess.run(['git', '-C', cartella, 'branch', '--show-current'],
                       capture_output=True, text=True)
    return r.stdout.strip() or None


def lingue():
    return leggi_yaml(os.path.join(radice_motore(), 'dati', 'lingue.yaml'))


def controlla_lingua(dati):
    codice = dati.get('lingua') if isinstance(dati, dict) else None
    if codice not in lingue():
        raise ErroreMotore(
            f'Lingua «{codice}» non supportata. Il motore oggi lavora solo in italiano (lingua: it):\n'
            'ortografia Hunspell it_IT, giorni e mesi in italiano. Correggi libro.yaml oppure\n'
            'chiedi di aggiungere la lingua in motore/dati/lingue.yaml.')


def _prendi(d, campo):
    for k in campo.split('.'):
        if not isinstance(d, dict) or k not in d:
            raise KeyError(campo)
        d = d[k]
    return d


def _metti(d, campo, valore):
    chiavi = campo.split('.')
    for k in chiavi[:-1]:
        d = d.setdefault(k, {})
    d[chiavi[-1]] = valore


def carica_profilo(nome):
    p = os.path.join(radice_motore(), 'profili', f'{nome}.yaml')
    if not os.path.isfile(p):
        raise ErroreMotore(f'Profilo «{nome}» inesistente in motore/profili/')
    return leggi_yaml(p)


def _foglie(d, prefisso=''):
    for k, v in d.items():
        campo = f'{prefisso}{k}'
        if isinstance(v, dict):
            yield from _foglie(v, campo + '.')
        else:
            yield campo, v


def carica_libro(percorso):
    """Restituisce (cartella, libro, profilo_effettivo). Si ferma con ErroreMotore."""
    cartella = trova_libro(percorso)
    dati = leggi_yaml(os.path.join(cartella, 'libro.yaml'))
    controlla_lingua(dati)                      # prima di qualsiasi altra cosa (B.3)
    errori = valida(dati, carica_schema('libro'))
    modalita = dati.get('modalita')
    if modalita == 'riscrittura':
        tp = dati.get('testo_precedente')
        if not tp:
            errori.append('libro.yaml.testo_precedente: obbligatorio con modalita: riscrittura')
        elif not os.path.isfile(os.path.join(cartella, tp)):
            errori.append(f'libro.yaml.testo_precedente: file inesistente «{tp}»')
    elif modalita == 'nuovo' and 'testo_precedente' in dati:
        errori.append('libro.yaml.testo_precedente: non ammesso con modalita: nuovo')
    for i, o in enumerate(dati.get('override') or []):
        if isinstance(o, dict) and not str(o.get('motivo') or '').strip():
            errori.append(f'libro.yaml.override[{i}]: override senza motivo ({o.get("campo")})')
    if errori:
        raise ErroreMotore('libro.yaml non valido:\n- ' + '\n- '.join(errori))
    profilo = carica_profilo(dati['profilo'])
    effettivo = copy.deepcopy(profilo)
    con_override = set()
    for o in dati.get('override') or []:
        try:
            _prendi(profilo, o['campo'])
        except KeyError:
            raise ErroreMotore(f'override su un campo che il profilo non ha: {o["campo"]}')
        _metti(effettivo, o['campo'], o['valore'])
        con_override.add(o['campo'])
    for campo, valore in _foglie(dati.get('stile') or {}):
        try:
            orig = _prendi(profilo, campo)
        except KeyError:
            continue
        if orig != valore and campo not in con_override:
            raise ErroreMotore(f'valore del profilo cambiato senza override: {campo}')
    return cartella, dati, effettivo


# ---------------------------------------------------------------- scrittura recintata

def dentro(cartella, percorso):
    c = os.path.realpath(cartella)
    p = os.path.realpath(percorso)
    return p == c or p.startswith(c + os.sep)


def scrivi(cartella_libro, percorso, testo):
    """Scrive `testo` solo se `percorso` sta sotto la cartella del libro (B.9)."""
    if not os.path.isabs(percorso):
        percorso = os.path.join(cartella_libro, percorso)
    if not dentro(cartella_libro, percorso):
        raise ErroreMotore(f'Scrittura rifiutata fuori dal libro: {percorso}')
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    if not dentro(cartella_libro, os.path.dirname(percorso)):
        raise ErroreMotore(f'Scrittura rifiutata fuori dal libro: {percorso}')
    with open(percorso, 'w', encoding='utf-8') as f:
        f.write(testo)
    return percorso


def argomenti(argv):
    """Argomenti posizionali, senza le opzioni (--x) e senza il valore di --radice."""
    out, salta = [], False
    for a in argv:
        if salta:
            salta = False
            continue
        if a == '--radice':
            salta = True
            continue
        if a.startswith('--'):
            continue
        out.append(a)
    return out


def percorso_in_libro(cartella_libro, percorso):
    """Percorso assoluto controllato: solleva ErroreMotore se è fuori dal libro (per file binari)."""
    if not os.path.isabs(percorso):
        percorso = os.path.join(cartella_libro, percorso)
    if not dentro(cartella_libro, percorso):
        raise ErroreMotore(f'Scrittura rifiutata fuori dal libro: {percorso}')
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    if not dentro(cartella_libro, os.path.dirname(percorso)):
        raise ErroreMotore(f'Scrittura rifiutata fuori dal libro: {percorso}')
    return percorso


def nome_file(titolo):
    """Nome di file dal titolo: minuscole, lettere e cifre, trattini."""
    import re
    import unicodedata
    s = unicodedata.normalize('NFKD', titolo).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-') or 'libro'


def esci_con_errore(e):
    print(f'FERMO: {e}', file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------- unità del manoscritto

def unita(cartella, libro):
    """Unità di 04-manoscritto in ordine di lettura: [(nome, percorso)].

    Nomi dei file: prologo.md, NN-<slug>.md (capitolo N), interludio-<NUMERO>.md, epilogo.md.
    Gli interludi si collocano con struttura.interludi[].dopo_capitolo.
    """
    import re
    dir_m = os.path.join(cartella, '04-manoscritto')
    if not os.path.isdir(dir_m):
        return []
    capitoli, interludi, altri = {}, {}, {}
    for f in sorted(os.listdir(dir_m)):
        if not f.endswith('.md'):
            continue
        p = os.path.join(dir_m, f)
        m = re.match(r'^(\d+)-', f)
        if m:
            capitoli[int(m.group(1))] = p
        elif f.startswith('interludio-'):
            interludi[f[len('interludio-'):-3]] = p
        elif f in ('prologo.md', 'epilogo.md'):
            altri[f[:-3]] = p
        else:
            raise ErroreMotore(f'File con nome non riconosciuto in 04-manoscritto: {f}')
    dopo = {}
    for i in (libro.get('struttura') or {}).get('interludi') or []:
        dopo.setdefault(i['dopo_capitolo'], []).append(str(i['numero']))
    ordine = []
    if 'prologo' in altri:
        ordine.append(('prologo', altri['prologo']))
    for n in sorted(capitoli):
        ordine.append((str(n), capitoli[n]))
        for num in dopo.get(n, []):
            if num in interludi:
                ordine.append((f'interludio {num}', interludi.pop(num)))
    for num, p in interludi.items():
        raise ErroreMotore(f'Interludio {num} senza posizione in struttura.interludi di libro.yaml')
    if 'epilogo' in altri:
        ordine.append(('epilogo', altri['epilogo']))
    return ordine


# ---------------------------------------------------------------- testo

def righe_prosa(testo):
    """Righe di prosa con il loro numero (1-based): escluse le righe «#», i commenti HTML,
    le righe senza lettere né cifre (separatori di scena) e la riga d'intestazione in corsivo
    che segue un titolo «#»."""
    import re
    out, in_commento, dopo_titolo = [], False, False
    for n, riga in enumerate(testo.splitlines(), 1):
        s = riga.strip()
        if in_commento:
            if '-->' in s:
                in_commento = False
            continue
        if s.startswith('<!--'):
            in_commento = '-->' not in s
            continue
        if s.startswith('#'):
            dopo_titolo = True
            continue
        if not s:
            continue
        if dopo_titolo and re.match(r'^\*[^*].*\*$', s):
            dopo_titolo = False
            continue
        dopo_titolo = False
        if not any(c.isalnum() for c in s):
            continue
        out.append((n, riga))
    return out


def parole(s):
    return [t for t in s.split() if any(c.isalnum() for c in t)]


def dichiarazioni_unita(testo):
    """Coppie campo=valore della riga nascosta <!-- zb: … -->."""
    import re
    m = re.search(r'<!--\s*zb:(.*?)-->', testo, re.S)
    if not m:
        return {}
    return dict(re.findall(r'(\w+)=([^\s()]+)', m.group(1)))


def in_elenco(unita, elenco):
    """True se l'unità («3», «interludio II», «prologo») è nell'elenco (numeri, «a-b», nomi)."""
    import re
    for voce in elenco or []:
        v = str(voce).strip().lower()
        if v == unita.lower():
            return True
        m = re.match(r'^(\d+)\s*-\s*(\d+)$', v)
        if m and unita.isdigit() and int(m.group(1)) <= int(unita) <= int(m.group(2)):
            return True
    return False


def tabella_md(percorso):
    """Righe di una tabella Markdown come dizionari {intestazione: cella}."""
    if not os.path.isfile(percorso):
        return []
    righe = [r for r in open(percorso, encoding='utf-8').read().splitlines() if r.strip().startswith('|')]
    if not righe:
        return []
    intest = [c.strip() for c in righe[0].strip().strip('|').split('|')]
    out = []
    for r in righe[1:]:
        celle = [c.strip() for c in r.strip().strip('|').split('|')]
        if all(set(c) <= set('-: ') for c in celle):
            continue
        out.append(dict(zip(intest, celle)))
    return out


# ---------------------------------------------------------------- margini KDP

def kdp():
    """Direttive KDP da dati/kdp.yaml: unica fonte dei valori KDP del motore."""
    p = os.path.join(radice_motore(), 'dati', 'kdp.yaml')
    if not os.path.isfile(p):
        raise ErroreMotore('Manca motore/dati/kdp.yaml (direttive KDP)')
    return leggi_yaml(p) or {}


def kdp_margini():
    """(tabella del margine interno [(da, a, pollici)], margini esterni minimi) da dati/kdp.yaml."""
    c = kdp().get('cartaceo') or {}
    try:
        tabella = [(f['da'], f['a'], f['pollici']) for f in c['margine_interno_per_pagine']]
        return tabella, c['margine_esterno_min_pollici']
    except (KeyError, TypeError):
        raise ErroreMotore('dati/kdp.yaml: mancano cartaceo.margine_interno_per_pagine o margine_esterno_min_pollici')


def kdp_interno_pollici(pagine):
    """Margine interno minimo KDP per il numero di pagine (sotto le 24 vale la prima fascia)."""
    tabella, _ = kdp_margini()
    for da, a, poll in tabella:
        if pagine <= a:
            return poll
    return tabella[-1][2]

# Esportazione completa del progetto — parte 4 di 6

Testo integrale, parola per parola. Nessun riassunto, nessuna correzione. Esclusi `libri/` e i manoscritti.


---

## 7. Programmi, stampa e prove

### `motore/script/comune.py`

```python
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
        if a in ('--radice', '--oggi', '--pdf', '--titolo'):
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
    sconosciuti = [num for num in interludi if not any(num in v for v in dopo.values())]
    if sconosciuti:
        raise ErroreMotore(f'Interludio {sconosciuti[0]} senza posizione in struttura.interludi di libro.yaml')
    # posizione: dopo il capitolo indicato; se quel capitolo non è scritto, dopo l'ultimo capitolo scritto
    # che lo precede; se è oltre l'ultimo capitolo scritto, in coda («in anticipo», vedi interludi_in_anticipo)
    ultimo = max(capitoli) if capitoli else 0
    posti = {}
    for d, nums in dopo.items():
        for num in nums:
            if num not in interludi:
                continue
            prima = [c for c in capitoli if c <= d]
            if d > ultimo:
                chiave = None
            else:
                chiave = d if d in capitoli else (max(prima) if prima else 'inizio')
            posti.setdefault(chiave, []).append((d, num))
    ordine = []
    if 'prologo' in altri:
        ordine.append(('prologo', altri['prologo']))
    for _, num in sorted(posti.get('inizio', [])):
        ordine.append((f'interludio {num}', interludi[num]))
    for n in sorted(capitoli):
        ordine.append((str(n), capitoli[n]))
        for _, num in sorted(posti.get(n, [])):
            ordine.append((f'interludio {num}', interludi[num]))
    for _, num in sorted(posti.get(None, [])):
        ordine.append((f'interludio {num}', interludi[num]))
    if 'epilogo' in altri:
        ordine.append(('epilogo', altri['epilogo']))
    return ordine


def interludi_in_anticipo(cartella, libro):
    """Interludi scritti la cui posizione (dopo_capitolo) è oltre l'ultimo capitolo scritto: [(nome, dopo)].

    Non è un errore: le unità restano in coda all'ordine di lettura e i comandi segnalano un AVVISO."""
    scritti = [int(n) for n, _ in unita(cartella, libro) if n.isdigit()]
    ultimo = max(scritti) if scritti else 0
    nomi = {n for n, _ in unita(cartella, libro)}
    return [(f'interludio {i["numero"]}', i['dopo_capitolo'])
            for i in (libro.get('struttura') or {}).get('interludi') or []
            if f'interludio {i["numero"]}' in nomi and i['dopo_capitolo'] > ultimo]


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


def applica_eccezioni(risultati, libro):
    """Gli AVVISO con un'eccezione motivata in libro.yaml (stile.eccezioni: {unita, controllo, motivo})
    diventano esito ECCEZIONE, con il motivo nel dettaglio. I KO restano KO."""
    ecc = (libro.get('stile') or {}).get('eccezioni') or []
    for r in risultati:
        if r['esito'] != 'AVVISO':
            continue
        for e in ecc:
            c = str(e.get('controllo') or '')
            if str(e.get('unita', '')).lower() == str(r['unita']).lower() and (
                    r['controllo'] == c or r['controllo'].split(':')[0] == c):
                r['esito'] = 'ECCEZIONE'
                r['dettaglio'] = f'{r["dettaglio"]} — eccezione: {e.get("motivo", "")}'.strip(' —')
                break
    return risultati


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


def oggi(argv=None):
    """Data di oggi: --oggi AAAA-MM-GG, poi ZB_OGGI, poi la data di sistema (le prove la fissano)."""
    import datetime
    argv = argv if argv is not None else sys.argv
    valore = None
    for i, a in enumerate(argv):
        if a == '--oggi' and i + 1 < len(argv):
            valore = argv[i + 1]
        elif a.startswith('--oggi='):
            valore = a.split('=', 1)[1]
    valore = valore or os.environ.get('ZB_OGGI')
    return datetime.date.fromisoformat(valore) if valore else datetime.date.today()


# ---------------------------------------------------------------- sessione e git (passo 5)

def git(cartella, *args, timeout=60):
    """Esegue git -C <cartella> …; restituisce (codice, stdout, stderr)."""
    try:
        r = subprocess.run(['git', '-C', cartella, *args], capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, '', f'git {" ".join(args)}: nessuna risposta in {timeout} s'
    except FileNotFoundError:
        return 127, '', 'git non installato'


def ultimo_commit(cartella, rel='.'):
    """Hash breve dell'ultimo commit che tocca `rel` (stringa vuota se mai salvato)."""
    return git(cartella, 'log', '-1', '--format=%h', '--', rel)[1]


def sha256_file(percorso):
    import hashlib
    with open(percorso, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


COLONNE_MISURATE = ('Parole reali', 'Scarto')


def testo_piano_senza_misure(testo):
    """piano-parole.md senza le colonne che misurano il manoscritto («Parole reali», «Scarto») e senza la
    frase «Totale previsto …: N.»: sono valori che zb esito aggiorna, non decisioni dell'autore."""
    import re
    out, idx = [], []
    for r in testo.splitlines():
        if r.strip().startswith('|'):
            celle = r.strip().strip('|').split('|')
            if not idx and any(c.strip() in COLONNE_MISURATE for c in celle):
                idx = [i for i, c in enumerate(celle) if c.strip() in COLONNE_MISURATE]
            elif idx:
                celle = [('' if i in idx else c) for i, c in enumerate(celle)]
            out.append('|'.join(c.strip() for c in celle))
        else:
            out.append(re.sub(r'Totale previsto[^:]*:\s*(\d{1,3}(?:\.\d{3})+|\d+)', 'Totale previsto', r))
    return '\n'.join(out)


def impronta_documento(percorso):
    """sha256 con cui un documento approvato si registra e si confronta. Per piano-parole.md le misure del
    manoscritto restano fuori dall'impronta (zb esito le aggiorna senza riapprovazione)."""
    import hashlib
    if os.path.basename(percorso) == 'piano-parole.md':
        return hashlib.sha256(testo_piano_senza_misure(open(percorso, encoding='utf-8').read()).encode()).hexdigest()
    return sha256_file(percorso)


def documento_invariato(percorso, registrato, commit=None):
    """True se il documento corrisponde a quanto registrato all'approvazione.

    Vale l'impronta attuale; per gli stati registrati prima delle impronte (sha256 grezzo) si confronta
    l'impronta della versione salvata nel commit registrato, se quel commit ha proprio lo sha256 grezzo."""
    import hashlib
    if not os.path.isfile(percorso):
        return False
    if registrato in (impronta_documento(percorso), sha256_file(percorso)):
        return True
    if not commit or os.path.basename(percorso) != 'piano-parole.md':
        return False
    cartella = os.path.dirname(percorso)
    rel = os.path.basename(percorso)
    try:
        prima = subprocess.run(['git', '-C', cartella, 'show', f'{commit}:./{rel}'], capture_output=True, timeout=60).stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    if hashlib.sha256(prima).hexdigest() != registrato:
        return False
    adesso = testo_piano_senza_misure(open(percorso, encoding='utf-8').read())
    return testo_piano_senza_misure(prima.decode('utf-8')) == adesso


def cartella_progetto():
    """Radice della sessione: $CLAUDE_PROJECT_DIR, altrimenti la radice git della cartella corrente."""
    return os.environ.get('CLAUDE_PROJECT_DIR') or radice_git(os.getcwd())


def sessione_corrente():
    """(session_id, fonte). Lo deposita hook_sessione.py; senza hook, identificativo locale."""
    p = os.path.join(cartella_progetto(), '.zb', 'sessione-corrente')
    try:
        sid = open(p, encoding='utf-8').read().strip()
        if sid:
            return sid, 'hook SessionStart'
    except OSError:
        pass
    if os.environ.get('ZB_SESSIONE'):
        return os.environ['ZB_SESSIONE'], 'variabile ZB_SESSIONE'
    return 'locale', 'identificativo locale (nessun hook SessionStart)'


def prepara_zb(cartella):
    """Crea <cartella>/.zb/ con un .gitignore che ignora tutto (marker mai nei commit)."""
    d = os.path.join(cartella, '.zb')
    os.makedirs(d, exist_ok=True)
    gi = os.path.join(d, '.gitignore')
    if not os.path.isfile(gi):
        with open(gi, 'w', encoding='utf-8') as f:
            f.write('*\n')
    return d


# ---------------------------------------------------------------- struttura standard (passo 6)

def struttura():
    return leggi_yaml(os.path.join(radice_motore(), 'dati', 'struttura-libro.yaml'))


def controlla_struttura(cartella, modalita):
    """Cartelle fuori struttura o non previste per la modalità, cartelle vuote, .gitkeep."""
    s = struttura()['cartelle']
    errori = []
    for d in sorted(os.listdir(cartella)):
        p = os.path.join(cartella, d)
        if not os.path.isdir(p) or d == '.git':
            continue
        if d not in s:
            errori.append(f'{d}/: cartella non prevista')
        elif modalita not in s[d]['modalita']:
            errori.append(f'{d}/: prevista solo in {", ".join(s[d]["modalita"])}')
    for radice, dirs, files in os.walk(cartella):
        dirs[:] = [x for x in dirs if x != '.git']
        rel = os.path.relpath(radice, cartella)
        if '.gitkeep' in files:
            errori.append(f'{os.path.join(rel, ".gitkeep")}: .gitkeep non ammesso')
        if rel != '.' and not dirs and not files:
            errori.append(f'{rel}/: cartella vuota')
    return errori
```

### `motore/script/conformita_kdp.py`

```python
"""Controllo di conformità KDP, sezioni 1-15 (proposta A.3-A.6, A.9).

Uso: python3 -B conformita_kdp.py <libro> [--pdf <file>] [--carta crema|bianca] [--bleed] [--oggi AAAA-MM-GG]
Legge libro.yaml (titolo, sottotitolo, serie, ebook, autore), 06-pubblicazione/scheda-amazon.md,
05-output/<titolo>-completo.md, il PDF (predefinito 05-output/<titolo>.pdf),
06-pubblicazione/ebook.docx (se ebook: true), 06-pubblicazione/conferme-autore.yaml e dati/kdp.yaml.
Scrive 06-pubblicazione/conformita-kdp.md: una riga OK/KO per sezione con la prova e gli avvisi.
Un controllo lasciato all'autore e non confermato è KO «da confermare dall'autore».
Codici d'uscita: 0 tutto OK; 1 almeno un KO; 2 nessun KO ma verifica delle direttive mai fatta o scaduta.
"""
import hashlib
import os
import re
import sys
import zipfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import kdp_verifica  # noqa: E402
import verifica_pdf  # noqa: E402

NOMI = {1: 'Titolo', 2: 'Sottotitolo', 3: 'Serie', 4: 'Descrizione', 5: 'Autore', 6: 'Editore',
        7: 'Parole chiave', 8: 'Pubblico e categorie', 9: 'Copertina', 10: 'ISBN', 11: 'Cartaceo',
        12: 'eBook', 13: 'Dichiarazione AI', 14: 'Contenuti', 15: 'Recensioni e promozione'}


class Sezione:
    def __init__(self, n):
        self.n, self.ko, self.avvisi, self.prove = n, [], [], []

    def KO(self, t):
        self.ko.append(t)

    def avviso(self, t):
        self.avvisi.append(t)

    def prova(self, t):
        self.prove.append(t)

    @property
    def esito(self):
        return 'KO' if self.ko else 'OK'


def leggi_scheda(p):
    """{'campi': {...}, 'descrizione': str, 'parole chiave': [...], 'categorie': [...]} o None."""
    if not os.path.isfile(p):
        return None
    testo = re.sub(r'<!--.*?-->', '', open(p, encoding='utf-8').read(), flags=re.S)
    parti = re.split(r'^## (.+)$', testo, flags=re.M)
    campi = {}
    for r in parti[0].splitlines():
        m = re.match(r'^([A-Za-zÀ-ÿ ]+):\s*(.*)$', r)
        if m:
            campi[m.group(1).strip().lower()] = m.group(2).strip()
    sez = {parti[i].strip().lower(): parti[i + 1] for i in range(1, len(parti), 2)}
    elenco = lambda s: [m.group(1).strip() for m in re.finditer(r'(?m)^\d+\.[ \t]*(\S.*)$', s or '')]
    return {'campi': campi, 'descrizione': (sez.get('descrizione') or '').strip(),
            'parole chiave': elenco(sez.get('parole chiave')), 'categorie': elenco(sez.get('categorie'))}


def vietate(testo, k):
    voci = k['metadati']['parole_vietate']
    rx = re.compile(r'(?i)(?<!\w)(' + '|'.join(re.escape(v) for v in sorted(voci, key=len, reverse=True)) + r')(?!\w)')
    return [m.group(1) for m in rx.finditer(testo or '')]


def vuoto_vietato(valore, k):
    return (valore or '').strip().lower() in [v.lower() for v in k['metadati']['valori_vuoti_vietati']]


def tag_html(testo):
    return re.findall(r'</?\s*([a-zA-Z][a-zA-Z0-9]*)', testo or '')


def controlla(cartella, libro, argv):
    k = comune.kdp()
    m = k['metadati']
    base = comune.nome_file(libro['titolo'])
    pub = os.path.join(cartella, '06-pubblicazione')
    scheda = leggi_scheda(os.path.join(pub, 'scheda-amazon.md'))
    pc = os.path.join(pub, 'conferme-autore.yaml')
    conferme = (comune.leggi_yaml(pc) or {}) if os.path.isfile(pc) else {}
    md_p = os.path.join(cartella, '05-output', f'{base}-completo.md')
    md = open(md_p, encoding='utf-8').read() if os.path.isfile(md_p) else None
    pdf = os.path.join(cartella, '05-output', f'{base}.pdf')
    if '--pdf' in argv:
        pdf = os.path.realpath(argv[argv.index('--pdf') + 1])
    info = verifica_pdf.pdfinfo(pdf) if os.path.isfile(pdf) else None
    S = {n: Sezione(n) for n in NOMI}
    campi = (scheda or {}).get('campi', {})
    if scheda is None:
        for n in (1, 2, 3, 4, 5, 6, 7, 8):
            S[n].KO('manca 06-pubblicazione/scheda-amazon.md')

    # 1 Titolo
    t = libro['titolo']
    S[1].prova(f'«{t}»')
    if vietate(t, k) or vuoto_vietato(t, k):
        S[1].KO(f'parole vietate o valore vuoto: {vietate(t, k) or t}')
    if tag_html(t):
        S[1].KO('tag HTML nel titolo')
    if scheda is not None and campi.get('titolo') != t:
        S[1].KO(f'scheda: «{campi.get("titolo")}», libro.yaml: «{t}»')
    if info is None:
        S[1].KO('PDF assente')
    elif info.get('Title') != t:
        S[1].KO(f'PDF Title «{info.get("Title")}» diverso')
    if md is None:
        S[1].KO('manoscritto compilato assente (compila.py)')
    elif not re.search(r'(?m)^# ' + re.escape(t) + r'\s*$', md):
        S[1].KO('frontespizio con un titolo diverso')

    # 2 Sottotitolo
    st = libro.get('sottotitolo') or ''
    S[2].prova(f'«{st}»' if st else 'nessun sottotitolo')
    lung = len(t) + len(st)
    if lung >= m['titolo_piu_sottotitolo_max_caratteri']:
        S[2].KO(f'titolo + sottotitolo: {lung} caratteri (limite {m["titolo_piu_sottotitolo_max_caratteri"]})')
    if st and (vietate(st, k) or vuoto_vietato(st, k)):
        S[2].KO(f'parole vietate: {vietate(st, k) or st}')
    if st.count(',') > 2:
        S[2].avviso('più di 2 virgole: sembra un elenco di parole chiave')
    if scheda is not None and (campi.get('sottotitolo') or '') != st:
        S[2].KO(f'scheda: «{campi.get("sottotitolo")}», libro.yaml: «{st}»')

    # 3 Serie
    serie = libro.get('serie')
    if serie:
        S[3].prova(f'«{serie["nome"]}» n. {serie["numero"]}')
        if vietate(serie['nome'], k):
            S[3].KO(f'parole vietate nel nome della serie: {vietate(serie["nome"], k)}')
        if scheda is not None:
            atteso = f'{serie["nome"]} | {serie["numero"]}'
            if campi.get('serie') != atteso:
                S[3].KO(f'scheda: «{campi.get("serie")}», atteso «{atteso}»')
            elif not str(campi['serie'].split('|')[-1]).strip().isdigit():
                S[3].KO('numero della serie non in cifre')
    else:
        S[3].prova('nessuna serie')

    # 4 Descrizione
    if scheda is not None:
        d = scheda['descrizione']
        S[4].prova(f'{len(d)} caratteri')
        if not d:
            S[4].KO('descrizione vuota (la scrive Claude Code nella fase di pubblicazione)')
        if len(d) > m['descrizione_max_caratteri']:
            S[4].KO(f'{len(d)} caratteri (massimo {m["descrizione_max_caratteri"]})')
        for nome, rx in m['pattern_descrizione']['bloccanti'].items():
            if re.search(rx, d):
                S[4].KO(f'{nome} nella descrizione: «{re.search(rx, d).group(0)}»')
        for f in m['formule_vietate_descrizione']:
            if re.search(r'(?i)(?<!\w)' + re.escape(f) + r'(?!\w)', d):
                S[4].KO(f'formula vietata: «{f}»')
        if vietate(d, k):
            S[4].KO(f'parole vietate: {", ".join(vietate(d, k))}')
        ammessi = m['html_ammesso_descrizione']['tag']
        fuori = sorted({x.lower() for x in tag_html(d)} - set(ammessi))
        if fuori:
            S[4].KO(f'tag HTML non ammessi: {", ".join(fuori)}')
        for nome, rx in m['pattern_descrizione']['avvisi'].items():
            if re.search(rx, d):
                S[4].avviso(f'{nome}: «{re.search(rx, d).group(0)}»')

    # 5 Autore
    a = libro['autore']
    S[5].prova(f'«{a}»')
    if scheda is not None and campi.get('autore') != a:
        S[5].KO(f'scheda: «{campi.get("autore")}», libro.yaml: «{a}»')
    if info is not None and info.get('Author') != a:
        S[5].KO(f'PDF Author: «{info.get("Author")}», libro.yaml: «{a}»')
    if md is not None:
        if not re.search(r'(?m)^### ' + re.escape(a) + r'\s*$', md):
            S[5].KO('frontespizio con un autore diverso')
        if not re.search(r'©[^\n]*' + re.escape(a), md):
            S[5].KO('pagina di copyright senza il nome dell\'autore')

    # 6 Editore
    ed = campi.get('editore', '')
    if scheda is not None:
        S[6].prova(f'«{ed}»' if ed else 'campo vuoto')
        if ed and vietate(ed, k):
            S[6].KO(f'parole vietate: {vietate(ed, k)}')
        if ed and re.search(r'(?i)\b(https?://|www\.|\.com\b|\.it\b)', ed):
            S[6].KO('sito o dominio nel campo editore')
    if conferme.get('isbn') == 'kdp_gratuito':
        S[6].avviso(f'con l\'ISBN gratuito l\'editore risulta «{k["isbn"]["editore_risultante"]}»')

    # 7 Parole chiave
    if scheda is not None:
        pk = scheda['parole chiave']
        S[7].prova(f'{len(pk)} parole chiave')
        if len(pk) > m['parole_chiave_max']:
            S[7].KO(f'{len(pk)} parole chiave (massimo {m["parole_chiave_max"]})')
        parole_titolo = {w.lower() for w in re.findall(r'\w+', t + ' ' + st) if len(w) > 3}
        a_, b_ = m['parole_chiave_parole_consigliate']
        for x in pk:
            if vietate(x, k) or tag_html(x):
                S[7].KO(f'«{x}»: parole vietate {vietate(x, k)}')
            n = len(x.split())
            if not a_ <= n <= b_:
                S[7].avviso(f'«{x}»: {n} parole (consigliate {a_}-{b_})')
            dup = parole_titolo & {w.lower() for w in re.findall(r'\w+', x)}
            if dup:
                S[7].avviso(f'«{x}» ripete parole del titolo: {", ".join(sorted(dup))}')

    # 8 Categorie
    if scheda is not None:
        cat = scheda['categorie']
        S[8].prova(f'{len(cat)} categorie')
        if len(cat) > m['categorie_max']:
            S[8].KO(f'{len(cat)} categorie (massimo {m["categorie_max"]})')
    if conferme.get('categorie_coerenti') is not True:
        S[8].KO('coerenza di categorie, parole chiave, descrizione e copertina: da confermare dall\'autore')

    # 9 Copertina
    S[9].prova('bleed, dimensioni dal calcolatore KDP, riquadro del codice a barre libero, dati identici ai metadati')
    if conferme.get('copertina_verificata') is not True:
        S[9].KO('copertina: da confermare dall\'autore')

    # 10 ISBN
    if conferme.get('isbn') == 'kdp_gratuito':
        S[10].prova('ISBN gratuito KDP, nessuna azione')
    else:
        S[10].KO('ISBN: da confermare dall\'autore (isbn: kdp_gratuito)')
    if md is not None and re.search(k['isbn']['pattern'], md):
        S[10].avviso('un ISBN compare nel manoscritto: non deve esserci finché KDP non lo assegna')
    S[10].avviso('copertina: lasciare libero il riquadro del codice a barre (modello del calcolatore KDP)')

    # 11 Cartaceo
    c = k['cartaceo']
    carta = conferme.get('carta') or libro['formato'].get('carta') or 'crema'
    if '--carta' in argv:
        carta = argv[argv.index('--carta') + 1]
    bleed = '--bleed' in argv or bool(libro['formato'].get('bleed'))
    if info is None:
        S[11].KO(f'PDF assente: {pdf}')
    else:
        pagine = int(info['Pages'])
        w, h = (float(x) for x in re.findall(r'[\d.]+', info['Page size'])[:2])
        wi, hi = round(w / 72, 2), round(h / 72, 2)
        S[11].prova(f'{pagine} pagine, {wi} × {hi}", carta {carta}')
        if pagine < c['pagine_min']:
            S[11].KO(f'{pagine} pagine (minimo {c["pagine_min"]})')
        if pagine > c['pagine_max'][carta]:
            S[11].KO(f'{pagine} pagine (massimo {c["pagine_max"][carta]} con carta {carta})')
        if pagine % 2:
            S[11].avviso(f'{pagine} pagine: numero dispari (da verificare sulla pagina ufficiale)')
        citato = any(abs(wi - a_) < 0.03 and abs(hi - b_) < 0.03 for a_, b_ in c['formati_citati_pollici'])
        if 'formato_confermato_kdp' in libro['formato']:
            # libro.yaml (formato.formato_confermato_kdp): false = AVVISO, true = OK, citato o no
            if libro['formato']['formato_confermato_kdp'] is True:
                S[11].prova(f'formato {wi} × {hi}" confermato dall\'autore su KDP (libro.yaml)')
            else:
                S[11].avviso(f'formato {wi} × {hi}" da confermare su KDP: formato_confermato_kdp è false in libro.yaml')
        elif not citato:
            if conferme.get('formato_confermato_kdp') is True:
                S[11].prova('formato non tra quelli citati, confermato dall\'autore su KDP')
            else:
                S[11].avviso(f'formato {wi} × {hi}" non tra quelli citati: formato_confermato_kdp è false')
        min_int = comune.kdp_interno_pollici(pagine)
        min_est = c['margine_esterno_min_pollici']['con_bleed' if bleed else 'senza_bleed']
        mg = verifica_pdf.margini(pdf)
        interno = min((sx if i % 2 else dx, i) for i, sx, dx, _, _ in mg)
        altri = min(min(dx if i % 2 else sx, a_, b_) for i, sx, dx, a_, b_ in mg)
        S[11].prova(f'margine interno minimo {interno[0]:.3f}" (KDP {min_int}"), esterni minimi {altri:.3f}" (KDP {min_est}")')
        if interno[0] < min_int:
            S[11].KO(f'margine interno {interno[0]:.3f}" a pag. {interno[1]} (minimo {min_int}")')
        if altri < min_est:
            S[11].KO(f'margine esterno {altri:.3f}" (minimo {min_est}")')
        fonts = verifica_pdf.pdffonts(pdf)
        if any(f['tipo'] == 'Type 3' for f in fonts):
            S[11].KO('font Type3 nel PDF')
        if any(not f['incorporato'] for f in fonts):
            S[11].KO('font non incorporati nel PDF')

    # 12 eBook
    if not libro.get('ebook'):
        S[12].prova('eBook non previsto (ebook: false)')
    else:
        docx = os.path.join(pub, 'ebook.docx')
        if not os.path.isfile(docx):
            S[12].KO('ebook: true ma manca 06-pubblicazione/ebook.docx')
        else:
            with zipfile.ZipFile(docx) as z:
                doc = z.read('word/document.xml').decode('utf-8', 'ignore')
                nomi = z.namelist()
            if not re.search(r'w:pStyle w:val="(Heading1|Titolo1|Heading2|Titolo2)"', doc):
                S[12].KO('nessun titolo con stile Titolo 1/2 (serve per il sommario attivo)')
            if re.search(r'PAGE', doc) or any(n.startswith('word/footer') or n.startswith('word/header') for n in nomi):
                S[12].KO('numeri di pagina, intestazioni o piè di pagina fissi nell\'eBook')
            S[12].prova('ebook.docx presente')
        S[12].avviso('controllo con Kindle Previewer: a cura dell\'autore')

    # 13 Dichiarazione AI
    S[13].prova('promemoria: testo, immagini, traduzioni; testo del sistema «generato dall\'AI»')
    if conferme.get('dichiarazione_ai') != 'fatta':
        S[13].KO('dichiarazione AI: da confermare dall\'autore (dichiarazione_ai: fatta)')

    # 14 Contenuti
    S[14].prova('copyright, marchi, contenuti per adulti segnalati')
    if conferme.get('contenuti_verificati') is not True:
        S[14].KO('contenuti: da confermare dall\'autore')

    # 15 Recensioni
    if md is not None:
        trovati = re.findall(k['metadati']['recensioni_vietate'], md)
        if trovati:
            S[15].KO(f'invito alla recensione non neutro: {", ".join(trovati)}')
    S[15].prova('invito alla recensione neutro nel manoscritto')
    if conferme.get('recensioni_regolari') is not True:
        S[15].KO('nessuno scambio di recensioni: da confermare dall\'autore')
    return S, pdf


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore(__doc__.strip().splitlines()[2])
    cartella, libro, _ = comune.carica_libro(args[0])
    oggi = comune.oggi(argv)
    S, pdf = controlla(cartella, libro, argv)
    scaduta, msg = kdp_verifica.stato_verifica(oggi)
    sha = hashlib.sha256(open(pdf, 'rb').read()).hexdigest() if os.path.isfile(pdf) else '—'
    k = comune.kdp()
    righe = ['# Conformità KDP', '', f'Libro: {libro["titolo"]} — data: {oggi} — PDF: {os.path.basename(pdf)} (sha256 {sha[:16]}…)', '',
             ('**AVVISO:** ' if scaduta else '') + msg, '',
             '| Sez. | Voce | Esito | Prova | Avvisi |', '|---|---|---|---|---|']
    for n, s in S.items():
        prova = '; '.join(s.prove + s.ko).replace('|', '/')
        righe.append(f'| {n} | {NOMI[n]} | {s.esito} | {prova} | {"; ".join(s.avvisi).replace("|", "/") or "—"} |')
    ko = [n for n, s in S.items() if s.esito == 'KO']
    righe += ['', f'**Esito:** {"KO nelle sezioni " + ", ".join(map(str, ko)) if ko else "nessun KO"}.', '',
              '> ' + k['dichiarazione_ai']['promemoria'].replace('\n', ' '), '']
    print('scritto', comune.scrivi(cartella, '06-pubblicazione/conformita-kdp.md', '\n'.join(righe)))
    print(msg)
    print('KO:', ', '.join(f'{n} {NOMI[n]}' for n in ko) if ko else 'nessuno')
    if ko:
        return 1
    return 2 if scaduta else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/conta.py`

```python
"""Conteggio delle parole con il metodo unico (proposta B.5 regola 3).

Uso: conta.py <libro> [--scrivi]
Metodo unico: token separati da spazi; escluse le righe che cominciano con «#»
(titoli Markdown), le righe di commento HTML (<!-- … -->, note nascoste del
motore) e i token senza lettere né cifre (lineette, separatori, segni isolati).
Totale: parole scritte più i budget delle unità di piano-parole.md non ancora scritte, rispetto a
parole.target_totale. Fuori da capitoli.tolleranza_totale: AVVISO con il budget residuo proposto per le
unità rimanenti (proposta: il motore non accorcia né allunga nessun capitolo da solo).
Stampa a schermo e non scrive file; con --scrivi salva il report in <libro>/06-diagnostica/conteggio.md
(«--schermo», delle versioni precedenti, è accettato e non cambia niente).
"""
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

METODO = ('metodo unico: token separati da spazi; escluse le righe che cominciano con «#», '
          'le righe di commento HTML e i token senza lettere né cifre')


def conta_testo(testo):
    n = 0
    in_commento = False
    for riga in testo.splitlines():
        s = riga.strip()
        if in_commento:
            if '-->' in s:
                in_commento = False
            continue
        if s.startswith('<!--'):
            if '-->' not in s:
                in_commento = True
            continue
        if s.startswith('#'):
            continue
        n += sum(1 for tok in riga.split() if any(c.isalnum() for c in tok))
    return n


def budget(cartella):
    """Budget per unità da 03-architettura/piano-parole.md (colonne «Cap.» e «Budget capitolo»)."""
    p = os.path.join(cartella, '03-architettura', 'piano-parole.md')
    if not os.path.isfile(p):
        return {}
    righe = [r for r in open(p, encoding='utf-8').read().splitlines() if r.strip().startswith('|')]
    if not righe:
        return {}
    intest = [c.strip() for c in righe[0].strip().strip('|').split('|')]
    try:
        ic, ib = intest.index('Cap.'), intest.index('Budget capitolo')
    except ValueError:
        raise comune.ErroreMotore('piano-parole.md: servono le colonne «Cap.» e «Budget capitolo»')
    out = {}
    for r in righe[1:]:
        celle = [c.strip() for c in r.strip().strip('|').split('|')]
        if len(celle) <= max(ic, ib) or set(celle[ic]) <= set('-: '):
            continue
        cifre = re.sub(r'[^\d]', '', celle[ib])
        if cifre:
            out[celle[ic].lower()] = int(cifre)
    return out


def totale_previsto(cartella, libro, profilo):
    """Totale previsto (scritte + budget delle unità non scritte) e, se esce dalla tolleranza, l'avviso.

    Restituisce (scritte, previsto, scarto, avviso o None)."""
    b = budget(cartella)
    scritte_per_unita = {n.lower(): conta_testo(open(p, encoding='utf-8').read()) for n, p in comune.unita(cartella, libro)}
    scritte = sum(scritte_per_unita.values())
    rimaste = {k: v for k, v in b.items() if k not in scritte_per_unita}
    previsto = scritte + sum(rimaste.values())
    obiettivo = libro['parole']['target_totale']
    tt = profilo['capitoli']['tolleranza_totale']
    sc = (previsto - obiettivo) / obiettivo
    if abs(sc) <= tt:
        return scritte, previsto, sc, None
    avviso = (f'totale previsto {previsto} parole su {obiettivo} ({sc:+.1%}, tolleranza ±{tt:.0%}); '
              f'scritte {scritte}')
    if rimaste:
        residuo = obiettivo - scritte
        fattore = residuo / sum(rimaste.values()) if sum(rimaste.values()) else 0
        proposta = ', '.join(f'{k}: {round(v * fattore)}' for k, v in rimaste.items())
        avviso += (f'. Budget residuo proposto: {residuo} parole per {len(rimaste)} unità ({proposta}); '
                   'è una proposta, nessun capitolo si accorcia o si allunga per evitare l\'avviso')
    else:
        avviso += '. Nessuna unità rimasta: decide l\'autore (motivo in libro.yaml o revisione dei capitoli)'
    return scritte, previsto, sc, avviso


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: conta.py <libro> [--scrivi]')
    cartella, libro, profilo = comune.carica_libro(args[0])
    toll = profilo['capitoli']['tolleranza_budget']
    b = budget(cartella)
    righe = ['# Conteggio delle parole', '',
             f'Libro: {libro["titolo"]} — metodo: {METODO}.', '',
             '| Unità | Parole | Budget | Scarto | Entro ±{:.0f}% |'.format(toll * 100),
             '|---|---|---|---|---|']
    totale = 0
    for nome, p in comune.unita(cartella, libro):
        n = conta_testo(open(p, encoding='utf-8').read())
        totale += n
        bud = b.get(nome.lower())
        if bud:
            sc = (n - bud) / bud
            righe.append(f'| {nome} | {n} | {bud} | {sc:+.1%} | {"sì" if abs(sc) <= toll else "no"} |')
        else:
            righe.append(f'| {nome} | {n} | — | — | — |')
    obiettivo = libro['parole']['target_totale']
    sct = (totale - obiettivo) / obiettivo
    tt = profilo['capitoli']['tolleranza_totale']
    _, previsto, scp, avviso = totale_previsto(cartella, libro, profilo)
    righe += ['', f'**Totale:** {totale} parole su {obiettivo} ({sct:+.1%}; '
              f'entro ±{tt:.0%}: {"sì" if abs(sct) <= tt else "no"}).',
              f'**Totale previsto** (scritte + budget delle unità non scritte): {previsto} ({scp:+.1%}).', '']
    if avviso:
        righe += [f'**AVVISO:** {avviso}.', '']
        print(f'AVVISO: {avviso}.')
    testo = '\n'.join(righe)
    if '--scrivi' in argv:
        print('scritto', comune.scrivi(cartella, '06-diagnostica/conteggio.md', testo))
    else:
        print(testo)
    return totale


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/continuita.py`

```python
"""Controlli di continuità (proposta B.2.1).

Uso: python3 -B continuita.py <libro> [--schermo]
Legge <libro>/cronologia.yaml e controlla nel testo: giorni della settimana
(su calendario.anni_ammessi), età dei personaggi con data di nascita, durate
dichiarate in cronologia (nel testo e tra le date degli eventi, unità «cronologia»), cifre
(KO solo nelle righe con una parola di «contesto»; senza contesto AVVISO), nomi propri scritti
in due modi, ordine delle date. Avvisi: tempi relativi («quattro giorni prima», «due settimane
dopo», «la terza notte») confrontati con le date delle intestazioni, del testo e della cronologia;
differenze d'età dichiarate tra personaggi con data di nascita; fatti_incompatibili di libro.yaml.
Report: <libro>/06-diagnostica/continuita.md, con la tabella di tutte le durate
trovate e la checklist manuale per capitolo.
"""
import datetime
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
from stile import risultato  # noqa: E402

UNITA_NUM = {'zero': 0, 'un': 1, 'uno': 1, 'una': 1, 'due': 2, 'tre': 3, 'tré': 3, 'quattro': 4, 'cinque': 5,
             'sei': 6, 'sette': 7, 'otto': 8, 'nove': 9}
DIECI = {'dieci': 10, 'undici': 11, 'dodici': 12, 'tredici': 13, 'quattordici': 14, 'quindici': 15,
         'sedici': 16, 'diciassette': 17, 'diciotto': 18, 'diciannove': 19}
DECINE = [('novant', 90), ('ottant', 80), ('settant', 70), ('sessant', 60), ('cinquant', 50),
          ('quarant', 40), ('trent', 30), ('vent', 20)]
DURATA = re.compile(r"(?i)\b([\w']+)\s+(anni|anno|mesi|mese|settimane|settimana|giorni|giorno)\b")



INIZIO_FRASE = '.!?…:;«"“—–-('

def numero(tok):
    t = tok.lower().strip(".,;:!?«»\"()'")
    if t.isdigit():
        return int(t)
    if t in UNITA_NUM:
        return UNITA_NUM[t]
    if t in DIECI:
        return DIECI[t]
    for pref, val in DECINE:
        if t.startswith(pref):
            resto = t[len(pref):]
            if resto in ('', 'a', 'i'):
                return val
            resto = resto.lstrip('aei') if resto[:1] in 'aei' and resto[1:] in UNITA_NUM else resto
            if resto in UNITA_NUM or resto in ('uno', 'otto'):
                return val + UNITA_NUM.get(resto, 0)
    return None


def leva(a, b):
    """Distanza di modifica (Levenshtein)."""
    prec = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prec[j] + 1, cur[j - 1] + 1, prec[j - 1] + (ca != cb)))
        prec = cur
    return prec[-1]


def righe_con_date(testo):
    """Righe utili per le date: tutte tranne titoli «#» e commenti HTML."""
    out = []
    for n, r in enumerate(testo.splitlines(), 1):
        s = r.strip()
        if s and not s.startswith('#') and not s.startswith('<!--'):
            out.append((n, r))
    return out


class Calendario:
    def __init__(self, libro):
        lingua = comune.lingue()[libro['lingua']]
        self.mesi = {m: i + 1 for i, m in enumerate(lingua['mesi'])}
        self.giorni = lingua['giorni']
        self.anni = (libro.get('calendario') or {}).get('anni_ammessi') or []
        self.rx = re.compile(r'(?i)\b(' + '|'.join(self.giorni) + r')\s+(\d{1,2})\s+('
                             + '|'.join(self.mesi) + r')(?:\s+(\d{4}))?')

    def trova(self, riga):
        return list(self.rx.finditer(riga))

    def risolvi(self, m):
        """(data, errore): la data con l'anno ammesso che dà quel giorno della settimana."""
        giorno, g, mese, anno = m.group(1).lower(), int(m.group(2)), self.mesi[m.group(3).lower()], m.group(4)
        anni = [int(anno)] if anno else self.anni
        for a in anni:
            try:
                d = datetime.date(a, mese, g)
            except ValueError:
                continue
            if self.giorni[d.weekday()] == giorno:
                return d, None
        if not anni:
            return None, None
        try:
            d = datetime.date(anni[0], mese, g)
            vero = self.giorni[d.weekday()]
        except ValueError:
            return None, f'data inesistente: {m.group(0)}'
        return d, f'«{m.group(0)}»: nel {anni[0]} il {g} {m.group(3)} è {vero}'


def eta(nascita, data):
    return data.year - nascita.year - ((data.month, data.day) < (nascita.month, nascita.day))


GIORNI_UNITA = {'giorn': 1, 'settiman': 7, 'mes': 30.44, 'ann': 365.25}


def giorni_dichiarati(valore):
    """«sei settimane» -> 42; «tre anni, quasi quattro» -> 1096 (prima cifra e prima unità)."""
    parti = valore.replace(',', ' ').split()
    if len(parti) < 2 or numero(parti[0]) is None:
        return None
    for pref, g in GIORNI_UNITA.items():
        if parti[1].lower().startswith(pref):
            return numero(parti[0]) * g
    return None


def tolleranza_giorni(du):
    """Tolleranza di una durata della cronologia: tolleranza_giorni, oppure _mesi o _anni come prima."""
    return (du.get('tolleranza_giorni') or 0) + (du.get('tolleranza_mesi') or 0) * 30.44 \
        + (du.get('tolleranza_anni') or 0) * 365.25


def _numero_enne(parola):
    """«trentaquattrenne» -> 34, «ventenne» -> 20, «diciottenne» -> 18."""
    base = parola.lower()[:-4]
    for fine in ('', 'o', 'e', 'i', 'a'):
        k = numero(base + fine)
        if k is not None:
            return k
    return None


def eta_nella_frase(frase, nascite):
    """[(chi, anni, forma, certo)] con le sole forme dichiarative dell'età attuale.

    KO (certo): «Nome ha N anni», «Nome, di N anni», «Nome … ha N anni» (soggetto = nome più vicino prima).
    AVVISO (incerto): «Nome aveva N anni» nella proposizione principale (imperfetto narrativo), «N-enne»
    con più nomi, «ha N anni» senza un nome prima.
    Ignorate: «quando/da quando/fin da quando … aveva N anni», «a N anni», «da N anni», «per N anni»."""
    pos = []
    for chi in nascite:
        for m in re.finditer(r'\b(' + re.escape(chi) + '|' + re.escape(chi.split()[0]) + r')\b', frase):
            pos.append((m.start(), m.end(), chi))
    if not pos:
        return []
    pos.sort()

    def prima(i):
        cand = [p for p in pos if p[1] <= i]
        return cand[-1] if cand else None

    out = []
    for m in re.finditer(r"(?i)\b(ha|compie|compirà)\s+(\w+)(?:\s+|['’])anni\b", frase):
        k = numero(m.group(2))
        if k is None:
            continue
        p = prima(m.start())
        if p:
            out.append((p[2], k, m.group(0), True))
        else:
            out.append((pos[0][2], k, m.group(0), False))
    for m in re.finditer(r"(?i)\b(aveva|avevi|avevo)\s+(\w+)(?:\s+|['’])anni\b", frase):
        k = numero(m.group(2))
        if k is None:
            continue
        prec = frase[:m.start()]
        if re.search(r"(?i)\b(quando|da quando|fin da quando|ricord\w*|allora)\b[^,;:]*$", prec):
            continue                                  # ricordo: età di allora, non attuale
        p = prima(m.start())
        if p and frase[p[1]:m.start()].strip(' ,') == '' or (p and len(frase[p[1]:m.start()].split()) <= 2):
            out.append((p[2], k, m.group(0), False))  # «Nome aveva N anni»: imperfetto narrativo, nel dubbio avviso
    for m in re.finditer(r"(?i)\b([\w']+)\s*,?\s+di\s+(\w+)(?:\s+|['’])anni\b", frase):
        k = numero(m.group(2))
        p = prima(m.start(2))
        if k is not None and p and len(frase[p[1]:m.start(2)].split()) <= 2:
            out.append((p[2], k, m.group(0).split(None, 1)[1] if m.group(1) not in [x[2] for x in pos] else m.group(0), True))
    for m in re.finditer(r"(?i)\b(\w+enne)\b", frase):
        k = _numero_enne(m.group(1))
        if k is None:
            continue
        vicini = sorted(pos, key=lambda p: min(abs(p[0] - m.end()), abs(p[1] - m.start())))
        certo = len({p[2] for p in pos}) == 1
        out.append((vicini[0][2], k, m.group(1), certo))
    return out


ORDINALI = {'prim': 1, 'second': 2, 'terz': 3, 'quart': 4, 'quint': 5, 'sest': 6, 'settim': 7, 'ottav': 8,
            'non': 9, 'decim': 10}
RELATIVO = re.compile(r"(?i)\b([\w']+)\s+(giorni|giorno|settimane|settimana|mesi|mese)\s+(prima|dopo|fa)\b")
ORDINALE = re.compile(r"(?i)\b(dopo\s+)?(?:la|il)\s+(prim|second|terz|quart|quint|sest|settim|ottav|non|decim)[oa]\s+"
                      r"(mattina|notte|giorno|sera)\b")
DIFF_ETA = [
    (re.compile(r"(?i)\bcon\s+(\w+)\s+anni\s+in\s+(più|meno)\b"), 1, lambda m: m.group(2).lower() == 'più'),
    (re.compile(r"(?i)\b(?:più|meno)?\s*(grande|vecchi\w*|piccol\w*|giovane|giovani)\s+di\s+(\w+)\s+anni\b"), 2,
     lambda m: m.group(1).lower()[:3] in ('gra', 'vec')),
    (re.compile(r"(?i)\b(\w+)\s+anni\s+più\s+(grande|vecchi\w*|piccol\w*|giovane|giovani)\b"), 1,
     lambda m: m.group(2).lower()[:3] in ('gra', 'vec')),
]


def intervallo_intestazione(testo, cal):
    """(inizio, fine) dalla riga in corsivo sotto il titolo («— martedì 14 – lunedì 20 settembre 1976»)."""
    for r in testo.splitlines()[:6]:
        s = r.strip()
        if not (s.startswith('*') and s.endswith('*') and len(s) > 2):
            continue
        rx = re.compile(r'(?i)(?:\b(' + '|'.join(cal.giorni) + r')\s+)?\b(\d{1,2})(?:\s+(' + '|'.join(cal.mesi)
                        + r'))?(?:\s+(\d{4}))?\b')
        parti = [m for m in rx.finditer(s) if m.group(1) or m.group(3)]
        if not parti:
            return None
        mese = anno = None
        date = []
        for m in reversed(parti):                    # mese e anno mancanti si prendono dalla data dopo
            mese = cal.mesi[m.group(3).lower()] if m.group(3) else mese
            anno = int(m.group(4)) if m.group(4) else anno
            if mese is None:
                return None
            anni = [anno] if anno else cal.anni
            scelta = None
            for a in anni:
                try:
                    d = datetime.date(a, mese, int(m.group(2)))
                except ValueError:
                    continue
                if scelta is None or (m.group(1) and cal.giorni[d.weekday()] == m.group(1).lower()):
                    scelta = d
            if scelta is None:
                return None
            date.insert(0, scelta)
        return date[0], date[-1]
    return None


def piu_mesi(d, n):
    m = d.month - 1 + n
    a, m = d.year + m // 12, m % 12 + 1
    for g in (d.day, 30, 29, 28):
        try:
            return datetime.date(a, m, g)
        except ValueError:
            continue


def tempi_relativi(nome, prosa, inter, note, cal):
    """Avvisi per «N giorni/settimane/mesi prima/dopo/fa» e «la N-esima mattina/notte/giorno/sera».

    note: {data: unità} con le date delle intestazioni (ogni giorno dell'intervallo), del testo e della
    cronologia. Giorni e settimane: tolleranza 0; mesi: ±15 giorni. Un «dopo» vale in tutte e due le
    direzioni (l'unità viene N giorni dopo un fatto, o un fatto viene N giorni dopo l'unità)."""
    out = []
    ini, fin = inter
    for n, r in prosa:
        for m in RELATIVO.finditer(r):
            k = numero(m.group(1))
            if not k:
                continue
            u, verso = m.group(2).lower(), m.group(3).lower()
            if u.startswith('mes'):
                passo, tol = (lambda d, s: piu_mesi(d, s * k)), 15
            else:
                g = k * (7 if u.startswith('settiman') else 1)
                passo, tol = (lambda d, s, g=g: d + datetime.timedelta(days=s * g)), 0
            segni = [-1] if verso in ('prima', 'fa') else [-1, 1]
            finestre = [(passo(ini, s) - datetime.timedelta(days=tol), passo(fin, s) + datetime.timedelta(days=tol))
                        for s in segni]
            finestre = [(min(a, b), max(a, b)) for a, b in finestre]
            if any(a <= d <= b for d in note for a, b in finestre):
                continue
            calcolata = passo(ini, segni[0]) if ini == fin else f'{passo(ini, segni[0])} … {passo(fin, segni[0])}'
            vicina = min(note, key=lambda d: min(abs((d - a).days) for a, _ in finestre)) if note else None
            out.append(risultato(nome, 'tempo_relativo', 'AVVISO', n,
                                 f'«{m.group(0)}» (unità datata {ini if ini == fin else f"{ini} – {fin}"}): '
                                 f'data calcolata {calcolata}' + (' (o dopo l\'unità)' if len(segni) > 1 else '')
                                 + '; nessuna data delle intestazioni, del testo o della cronologia coincide'
                                 + (f' (la più vicina: {vicina}, {note[vicina]})' if vicina else '')))
        if r.lstrip().startswith(('—', '–', '-')):
            continue                                       # nel dialogo l'ordinale può parlare d'altro
        for m in ORDINALE.finditer(r):
            k = ORDINALI[m.group(2).lower()] + (1 if m.group(1) else 0)
            calcolata = ini + datetime.timedelta(days=k - 1)
            prima = r[:m.start()].rstrip()
            inizio = not prima or prima[-1] in '.!?…'
            if prima.endswith(':'):
                continue                                   # elenco di ricordi («gli raccontai: il settimo giorno, …»)
            problemi = []
            if calcolata > fin and (ini < fin or inizio):
                problemi.append(f'oltre l\'intestazione ({fin})')
            dopo = r[m.end():m.end() + 25]
            g = re.match(r'(?i)\s*,?\s*(?:il|di|la)\s+(' + '|'.join(cal.giorni) + r')\b', dopo)
            if g and cal.giorni[calcolata.weekday()] != g.group(1).lower():
                problemi.append(f'il {calcolata} è {cal.giorni[calcolata.weekday()]}, non {g.group(1).lower()}')
            if problemi:
                out.append(risultato(nome, 'tempo_relativo', 'AVVISO', n,
                                     f'«{m.group(0)}» contando dal {ini}: data calcolata {calcolata}; '
                                     + '; '.join(problemi)))
    return out


def differenze_eta(nome, prosa, nascite):
    """Avvisi per «con N anni in più/meno», «più grande/piccolo di N anni», «N anni più grande» tra due
    personaggi con data di nascita nella stessa frase (il primo è il nome più vicino prima della forma)."""
    out = []
    for n, r in prosa:
        for frase in re.split(r'(?<=[.!?…])\s+', r):
            pos = []
            for chi in nascite:
                for m in re.finditer(r'\b(' + re.escape(chi) + '|' + re.escape(chi.split()[0]) + r')\b', frase):
                    pos.append((m.start(), chi))
            if len({c for _, c in pos}) < 2:
                continue
            for rx, gruppo, maggiore in DIFF_ETA:
                for m in rx.finditer(frase):
                    k = numero(m.group(gruppo))
                    if k is None:
                        continue
                    prima = [p for p in pos if p[0] < m.start()]
                    a = (prima or pos)[-1][1]
                    altri = sorted((p for p in pos if p[1] != a), key=lambda p: abs(p[0] - m.start()))
                    b = altri[0][1]
                    vecchio, giovane = (a, b) if maggiore(m) else (b, a)
                    vera = eta(nascite[vecchio], nascite[giovane]) if nascite[vecchio] <= nascite[giovane] else \
                        -eta(nascite[giovane], nascite[vecchio])
                    if vera != k:
                        out.append(risultato(nome, 'differenza_eta', 'AVVISO', n,
                                             f'«{m.group(0).strip()}» ({a} rispetto a {b}): dalle nascite '
                                             f'{vecchio} ha {vera} anni più di {giovane} '
                                             f'({nascite[vecchio]}, {nascite[giovane]})'))
    return out


def fatti_incompatibili(cartella, libro):
    """Avvisi per le coppie di libro.yaml «fatti_incompatibili»: pattern A (nelle sue unità) e pattern B
    (nelle sue) compaiono tutti e due. L'avviso riporta le due righe."""
    out = []
    voci = libro.get('fatti_incompatibili') or []
    if not voci:
        return out
    unita = [(nome, comune.righe_prosa(open(p, encoding='utf-8').read())) for nome, p in comune.unita(cartella, libro)]
    for f in voci:
        trovate = []
        for lato in ('a', 'b'):
            v = f[lato]
            rx = re.compile(v['pattern'])
            trovate.append(next(((nome, n, r.strip()) for nome, prosa in unita
                                 if v.get('unita') is None or comune.in_elenco(nome, v['unita'])
                                 for n, r in prosa if rx.search(r)), None))
        if all(trovate):
            (ua, na, ra), (ub, nb, rb) = trovate
            corta = (lambda t: t if len(t) <= 160 else t[:157] + '…')
            out.append(risultato(ub, f'fatti_incompatibili:{f["id"]}', 'AVVISO', nb,
                                 f'A, unità {ua} riga {na}: «{corta(ra)}» — B, unità {ub} riga {nb}: «{corta(rb)}»'
                                 + (f' ({f["nota"]})' if f.get('nota') else '')))
    return out


def controlla_libro(cartella, libro):
    cron = comune.leggi_yaml(os.path.join(cartella, 'cronologia.yaml')) if os.path.isfile(
        os.path.join(cartella, 'cronologia.yaml')) else {}
    cron = cron or {}
    cal = Calendario(libro)
    nascite = {n['chi']: n['data'] for n in cron.get('nascite') or []}
    eventi = {e['id']: e['data'] for e in cron.get('eventi') or []}
    pn = os.path.join(cartella, (libro.get('ortografia') or {}).get('parole_ammesse_file') or 'nomi_propri.txt')
    nomi = [r.strip() for r in open(pn, encoding='utf-8')] if os.path.isfile(pn) else []
    nomi = [n for n in nomi if n and not n.startswith('#')]
    scaletta = {r.get('Unità', '').lower(): r for r in
                comune.tabella_md(os.path.join(cartella, '03-architettura', 'scaletta.md'))}
    risultati, durate_trovate, date_unita = [], [], []
    intervalli, note = {}, {}
    for e in cron.get('eventi') or []:
        note.setdefault(e['data'], f'cronologia: {e["id"]}')
    for nome, p in comune.unita(cartella, libro):
        testo = open(p, encoding='utf-8').read()
        inter = intervallo_intestazione(testo, cal)
        if inter:
            intervalli[nome] = inter
            d = inter[0]
            while d <= inter[1]:
                note.setdefault(d, f'unità {nome}')
                d += datetime.timedelta(days=1)
        for _, r in righe_con_date(testo):
            for m in cal.trova(r):
                d = cal.risolvi(m)[0]
                if d:
                    note.setdefault(d, f'unità {nome}')
    for nome, p in comune.unita(cartella, libro):
        testo = open(p, encoding='utf-8').read()
        righe = righe_con_date(testo)
        prosa = comune.righe_prosa(testo)
        data_unita = None
        # giorni della settimana
        for n, r in righe:
            for m in cal.trova(r):
                d, err = cal.risolvi(m)
                if err:
                    risultati.append(risultato(nome, 'giorno_settimana', 'KO', n, err))
                if d and data_unita is None:
                    data_unita = d
        if data_unita is None and nome in scaletta:
            m = cal.rx.search(scaletta[nome].get('Data', ''))
            if m:
                data_unita = cal.risolvi(m)[0]
        date_unita.append((nome, data_unita))
        # tempi relativi, dall'intervallo dell'intestazione (o dalla prima data dell'unità)
        inter = intervalli.get(nome) or ((data_unita, data_unita) if data_unita else None)
        if inter:
            risultati += tempi_relativi(nome, prosa, inter, note, cal)
        risultati += differenze_eta(nome, prosa, nascite)
        # età (solo forme dichiarative; vedi eta_nella_frase)
        unito = ' '.join(r.strip() for _, r in prosa)
        if data_unita:
            for frase in re.split(r'(?<=[.!?…])\s+', unito):
                for chi, k, forma, certo in eta_nella_frase(frase, nascite):
                    vera = eta(nascite[chi], data_unita)
                    if abs(k - vera) > 1:
                        riga = next((n for n, r in prosa if forma in r), None)
                        risultati.append(risultato(nome, 'eta', 'KO' if certo else 'AVVISO', riga,
                                                   f'{chi}: «{forma}», ma al {data_unita} ne ha {vera}'
                                                   + ('' if certo else ' (attribuzione o tempo incerti: da verificare)')))
        # durate (tabella) e durate della cronologia
        for n, r in prosa:
            for m in DURATA.finditer(r):
                if numero(m.group(1)) is not None:
                    durate_trovate.append((nome, n, m.group(0)))
        for du in cron.get('durate') or []:
            for n, r in prosa:
                if du['valore'].lower() in r.lower():
                    dichiarati = giorni_dichiarati(du['valore'])
                    if dichiarati is None:
                        continue
                    calcolati = (eventi[du['a']] - eventi[du['da']]).days
                    if abs(calcolati - dichiarati) > tolleranza_giorni(du):
                        risultati.append(risultato(nome, 'durata', 'KO', n,
                                                   f'«{du["valore"]}»: dalle date risultano {calcolati} giorni '
                                                   f'({calcolati / 365.25:.1f} anni); tolleranza {tolleranza_giorni(du):.0f} giorni'))
        # cifre: con «contesto» si controllano solo le righe che contengono una di quelle parole (KO);
        # senza, un numero diverso vicino all'unità è solo un AVVISO (può parlare d'altro)
        for ci in cron.get('cifre') or []:
            contesto = [c.lower() for c in ci.get('contesto') or []]
            for n, r in prosa:
                if contesto and not any(c in r.lower() for c in contesto):
                    continue
                toks = r.split()
                for i, t in enumerate(toks):
                    if t.lower().strip('.,;:!?') != ci['unita'].lower():
                        continue
                    vicini = toks[i + 1:i + 4] + list(reversed(toks[max(0, i - 2):i]))
                    for v in vicini:
                        k = numero(v)
                        if k is not None:
                            if k != ci['valore']:
                                risultati.append(risultato(
                                    nome, f'cifra:{ci["id"]}', 'KO' if contesto else 'AVVISO', n,
                                    f'«{v} {ci["unita"]}», atteso {ci["valore"]}'
                                    + ('' if contesto else ' (senza «contesto» in cronologia.yaml: verifica '
                                       'che la frase parli di questa cifra)')))
                            break
        # nomi in due grafie
        visti = set()
        for n, r in prosa:
            for mt in re.finditer(r"\b[A-ZÀ-Ý][a-zà-ÿ]+\b", r):
                t = mt.group(0)
                if t in nomi or t in visti:
                    continue
                # a inizio frase la maiuscola è della frase, non del nome: le parole comuni non si confrontano
                prima = r[:mt.start()].rstrip()
                if not prima or prima[-1] in INIZIO_FRASE:
                    continue
                for nm in nomi:
                    if len(t) >= 5 and t[0] == nm[0] and leva(t, nm) == 1:
                        visti.add(t)
                        risultati.append(risultato(nome, 'nome_due_grafie', 'AVVISO', n, f'«{t}» e «{nm}»'))
                        break
    # durate della cronologia confrontate con le date degli eventi, anche se il testo non le nomina
    for du in cron.get('durate') or []:
        dichiarati = giorni_dichiarati(du['valore'])
        if dichiarati is None or du['da'] not in eventi or du['a'] not in eventi:
            continue
        calcolati = (eventi[du['a']] - eventi[du['da']]).days
        if abs(calcolati - dichiarati) > tolleranza_giorni(du):
            risultati.append(risultato('cronologia', 'durata', 'KO', None,
                                       f'«{du["valore"]}» da {du["da"]} a {du["a"]}: dalle date risultano {calcolati} '
                                       f'giorni; tolleranza {tolleranza_giorni(du):.0f} giorni'))
    risultati += fatti_incompatibili(cartella, libro)
    # ordine delle date
    prec = None
    for nome, d in date_unita:
        if d and prec and d < prec[1]:
            risultati.append(risultato(nome, 'ordine_date', 'AVVISO', None, f'{d} prima di {prec[1]} ({prec[0]})'))
        if d:
            prec = (nome, d)
    return comune.applica_eccezioni(risultati, libro), durate_trovate, date_unita


def voci_toccate(cartella, libro, nome_unita):
    """Voci in grassetto della bibbia che compaiono nell'unità."""
    pb = os.path.join(cartella, '02-bibbia', 'bibbia.md')
    voci = re.findall(r'\*\*([^*]+)\*\*', open(pb, encoding='utf-8').read()) if os.path.isfile(pb) else []
    voci = [v for v in voci if v.lower() != 'oggetti']
    testo = open(dict(comune.unita(cartella, libro))[nome_unita], encoding='utf-8').read()
    toccate = []
    for v in voci:
        parti = v.split()
        chiave = parti[-1] if parti[0].lower() in ('signora', 'signor', 'don', 'dottor', 'zia', 'zio') else parti[0]
        if v in testo or re.search(r'\b' + re.escape(chiave) + r'\b', testo):
            toccate.append(v)
    return toccate


def checklist(cartella, libro):
    righe = ['| Unità | Voci della bibbia toccate | Verificato dall\'autore |', '|---|---|---|']
    for nome, _ in comune.unita(cartella, libro):
        righe.append(f'| {nome} | {", ".join(voci_toccate(cartella, libro, nome)) or "—"} | [ ] |')
    return righe


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: continuita.py <libro> [--schermo]')
    cartella, libro, _ = comune.carica_libro(args[0])
    risultati, durate, date_unita = controlla_libro(cartella, libro)
    from stile import tabella
    righe = ['# Continuità', '', f'Libro: {libro["titolo"]}.', '', '## Esiti', '']
    righe += tabella(risultati) if risultati else ['Nessun KO e nessun avviso.']
    righe += ['', '## Date delle unità', '', '| Unità | Data |', '|---|---|']
    righe += [f'| {n} | {d or "—"} |' for n, d in date_unita]
    righe += ['', '## Tutte le durate trovate nel testo', '', '| Unità | Riga | Testo |', '|---|---|---|']
    righe += [f'| {u} | {n} | {t} |' for u, n, t in durate] or ['| — | — | — |']
    righe += ['', '## Checklist manuale', '',
              'Da verificare a mano: oggetti e persone in scena, chi sa cosa, distanze e tempi di '
              'spostamento, tempo interno della scena, età e durate dette in modo indiretto, ferite '
              'e segni da un capitolo all\'altro.', ''] + checklist(cartella, libro) + ['']
    testo = '\n'.join(righe)
    if '--schermo' in argv:
        print(testo)
    else:
        print('scritto', comune.scrivi(cartella, '06-diagnostica/continuita.md', testo))
    return 1 if any(r['esito'] == 'KO' for r in risultati) else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/fase.py`

```python
"""Macchina a stati del libro (proposta C.1, adattata al processo del passo 5). Unico script che scrive stato.yaml.

Uso: python3 -B fase.py <libro> <comando> [argomenti]

Comandi dell'autore:
  stato                    mostra lo stato; non scrive nulla
  avanti                   mostra il blocco successivo dei documenti del gate aperto
  ok [lotti da N]          approva il gate aperto (solo dopo aver mostrato tutti i blocchi)
  correggi <istruzione>    registra una correzione; il gate resta aperto
  riapprova <documento> <motivo>   registra una modifica autorizzata a un documento già approvato
  fase stesura --motivo <testo>    da «chiusura» torna a «stesura» se nel piano mancano unità (registra data,
                           motivo e fase precedente)
                           (nuovo sha256 e commit, con data, motivo e sha256 precedente)
Comandi di Claude Code:
  pronto                   il lavoro della fase è finito: apre il gate (se previsto in libro.yaml) o passa oltre
  esito <N>                esegue capitolo.py sull'unità N e registra l'esito (OK, KO, secondo KO = fermata);
                           a un gate «primi_capitoli» o «lotto» con una correzione registrata, rifà i controlli
                           di un capitolo del gate e aggiorna le parole; il gate resta aperto

Fasi: documenti → pagina_campione → stesura → chiusura → chiuso. Si passa a «chiusura» solo quando tutte le
unità del piano parole (prologo, capitoli, interludi, epilogo) sono scritte e accettate.
Gate (libro.yaml, campo «gate»; predefiniti documenti, pagina_campione, primi_capitoli):
documenti, pagina_campione, primi_capitoli, lotto; più controllo_fallito, sempre attivo
(stesso controllo fallito due volte di fila sullo stesso capitolo).
Scrive solo <libro>/stato.yaml e <libro>/LEGGIMI.md (e il report di capitolo.py). Nessun commit:
il salvataggio lo fa Claude Code secondo il blocco di salvataggio.
"""
import contextlib
import datetime
import io
import os
import re
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import conta  # noqa: E402
import revisione  # noqa: E402

FASI = ['documenti', 'pagina_campione', 'stesura', 'chiusura', 'chiuso']
GATE_PREDEFINITI = ['documenti', 'pagina_campione', 'primi_capitoli']
CHIUSURA = [('06-diagnostica/continuita.md', 'zb continuita'),
            ('06-diagnostica/controllo-ortografico.md', 'zb ortografia'),
            ('05-output/{nome}-completo.md', 'zb compila'),
            ('05-output/{nome}.pdf', 'zb impagina'),
            ('06-diagnostica/verifica-pdf.md', 'zb pdf'),
            ('06-pubblicazione/checklist.md', 'zb pacchetto'),
            ('06-pubblicazione/conformita-kdp.md', 'zb kdp')]
PAGINA_DA_SCRIVERE = ('# Pagina campione\n\n<!-- Da scrivere secondo 03-architettura/manuale-di-stile.md; '
                      'poi «zb pronto <libro>». -->\n')
SALVA = 'Salva: git add, commit, push, git status -sb, git log -1.'


# ---------------------------------------------------------------- stato

def carica_stato(cartella):
    p = os.path.join(cartella, 'stato.yaml')
    if not os.path.isfile(p):
        raise comune.ErroreMotore(f'stato.yaml mancante in {cartella}')
    stato = comune.leggi_yaml(p)
    errori = comune.valida(stato, comune.carica_schema('stato'), 'stato.yaml')
    if not errori and stato['fase'] not in FASI:
        errori.append(f'stato.yaml.fase: «{stato["fase"]}» non è una fase ({", ".join(FASI)})')
    if errori:
        raise comune.ErroreMotore('stato.yaml non valido:\n- ' + '\n- '.join(errori))
    stato.setdefault('tentativi', {})
    stato.setdefault('correzioni_aperte', [])
    stato.setdefault('ultimo_capitolo_scritto', None)
    return stato


def salva_stato(cartella, stato):
    stato['aggiornato'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    comune.scrivi(cartella, 'stato.yaml', yaml.safe_dump(stato, sort_keys=False, allow_unicode=True, width=120))
    p = os.path.join(cartella, 'LEGGIMI.md')
    if os.path.isfile(p):
        t = open(p, encoding='utf-8').read()
        t = re.sub(r'(?m)^Fase: .*$', f'Fase: {stato["fase"]}; gate in attesa: {stato["gate_in_attesa"] or "nessuno"}', t)
        t = re.sub(r'(?m)^Ultimo capitolo approvato: .*$',
                   f'Ultimo capitolo approvato: {stato["ultimo_capitolo_approvato"] or "—"}', t)
        comune.scrivi(cartella, 'LEGGIMI.md', t)


def gate_attivi(libro):
    return libro['gate'] if libro.get('gate') is not None else GATE_PREDEFINITI


def capitoli_previsti(cartella):
    p = os.path.join(cartella, '03-architettura', 'piano-parole.md')
    if not os.path.isfile(p):
        return 0
    return len(set(re.findall(r'(?m)^\|[^|\n]*\|\s*(\d+)\s*\|', open(p, encoding='utf-8').read())))


def unita_del_piano(cartella):
    """Unità di piano-parole.md (colonna «Cap.») in ordine: «prologo», «1», «interludio I», «epilogo»…"""
    p = os.path.join(cartella, '03-architettura', 'piano-parole.md')
    if not os.path.isfile(p):
        return []
    intest, out = None, []
    for r in open(p, encoding='utf-8').read().splitlines():
        if not r.strip().startswith('|'):
            continue
        celle = [c.strip() for c in r.strip().strip('|').split('|')]
        if intest is None:
            if 'Cap.' in celle:
                intest = celle
            continue
        if len(celle) != len(intest) or all(set(c) <= set('-: ') for c in celle):
            continue
        u = celle[intest.index('Cap.')]
        u = str(int(u)) if u.isdigit() else u
        if u and u not in out:
            out.append(u)
    return out


def accettata(cartella, stato, u):
    """True se l'unità del piano è scritta e ha superato «esito»."""
    if u.isdigit():
        return int(u) <= (stato['ultimo_capitolo_scritto'] or 0)
    if u.lower() in [str(x).lower() for x in stato.get('unita_accettate') or []]:
        return True
    # unità accettate prima del registro «unita_accettate»: il report di capitolo.py dice 0 KO
    rep = os.path.join(cartella, '06-diagnostica', 'capitoli', revisione.nome_report(u) + '.md')
    return os.path.isfile(rep) and re.search(r'(?m)^Esito: 0 KO', open(rep, encoding='utf-8').read()) is not None


def unita_mancanti(cartella, libro, stato):
    """Unità del piano non ancora scritte o non accettate, in ordine di piano."""
    scritte = {n.lower() for n, _ in comune.unita(cartella, libro)}
    return [u for u in unita_del_piano(cartella) if u.lower() not in scritte or not accettata(cartella, stato, u)]


def passo_di(u):
    return f'capitolo {u}' if u.isdigit() else u


def parole_scritte(cartella, libro):
    return sum(conta.conta_testo(open(p, encoding='utf-8').read()) for _, p in comune.unita(cartella, libro))


def prossimo(stato):
    g, f = stato['gate_in_attesa'], stato['fase']
    if g:
        return f'Gate «{g}» aperto: avanti, ok, correggi: … oppure stato.'
    return {'documenti': 'Completa bibbia, cronologia, scaletta e piano parole; poi «zb pronto <libro>».',
            'pagina_campione': 'Scrivi 05-revisioni/pagina-campione.md secondo il manuale; poi «zb pronto <libro>».',
            'stesura': f'Prossimo: {stato["passo"]}. Rileggi manuale e direttive, scrivi, poi «zb esito <libro> N».',
            'chiusura': 'Esegui ' + ', '.join(c for _, c in CHIUSURA) + '; poi «zb pronto <libro>».',
            'chiuso': 'Libro chiuso.'}[f]


# ---------------------------------------------------------------- revisione e approvazione

def apri_gate(cartella, libro, stato, gate, passo=None):
    stato['gate_in_attesa'] = gate
    stato['revisione_in_corso'] = None
    if passo:
        stato['passo'] = passo
    print(f'Gate «{gate}» aperto. Mostro i documenti in blocchi.')
    avanti(cartella, libro, stato)


def avanti(cartella, libro, stato):
    gate = stato['gate_in_attesa']
    if not gate:
        raise comune.ErroreMotore('Nessun gate aperto: «avanti» non ha niente da mostrare. ' + prossimo(stato))
    docs = revisione.documenti_del_gate(cartella, libro, stato, gate)
    b = revisione.blocchi(cartella, docs)
    imp = revisione.impronta(cartella, docs)
    rc = stato.get('revisione_in_corso')
    if rc and rc.get('gate') == gate and rc.get('sha256') == imp:
        n = rc['blocco'] + 1
        if n > len(b):
            print('Fine dei documenti. Scrivi ok o correggi: …')
            return
    else:
        if rc and rc.get('gate') == gate:
            print('Documenti cambiati dall\'ultima lettura: la revisione riparte dal blocco 1.')
        n = 1
    print(revisione.mostra(libro['titolo'], b, n))
    stato['revisione_in_corso'] = {'gate': gate, 'blocco': n, 'blocchi_totali': len(b), 'sha256': imp}
    if n == len(b):
        print('Fine dei documenti. Scrivi ok o correggi: …')


def registra(cartella, stato, documenti, senza_gate=False):
    """Registra sha256 e commit dei documenti approvati; rifiuta documenti non salvati."""
    codice, out, err = comune.git(cartella, 'status', '--porcelain', '--', *documenti)
    if codice != 0:
        raise comune.ErroreMotore(f'git status non riuscito: {err}')
    if out:
        raise comune.ErroreMotore('Documenti con modifiche non salvate:\n' + out +
                                  '\nSalva prima (git add, commit, push), poi ripeti.')
    for rel in documenti:
        commit = comune.ultimo_commit(cartella, rel)
        if not commit:
            raise comune.ErroreMotore(f'{rel} non è mai stato salvato in un commit')
        voce = {'sha256': comune.impronta_documento(os.path.join(cartella, rel)), 'commit': commit}
        if senza_gate:
            voce['senza_gate'] = True
        stato['documenti_approvati'][rel] = voce


def chiudi_fase(cartella, libro, stato):
    """Dopo l'approvazione dei documenti o della pagina campione: fase successiva."""
    if stato['fase'] == 'documenti':
        stato.update(fase='pagina_campione', passo='da completare', gate_in_attesa=None)
        if not os.path.isfile(os.path.join(cartella, revisione.PAGINA_CAMPIONE)):
            comune.scrivi(cartella, revisione.PAGINA_CAMPIONE, PAGINA_DA_SCRIVERE)
            print(f'Creato {revisione.PAGINA_CAMPIONE}, da scrivere secondo il manuale.')
    elif stato['fase'] == 'pagina_campione':
        stato.update(fase='stesura', passo='capitolo 1', gate_in_attesa=None)
    stato['revisione_in_corso'] = None


def dopo_capitolo(cartella, libro, stato):
    """Gate e fasi dopo un capitolo accettato."""
    gate = gate_attivi(libro)
    totale = capitoli_previsti(cartella)
    scritto = stato['ultimo_capitolo_scritto'] or 0
    numerici = [int(c) for c in stato['lotto']['capitoli'] if str(c).isdigit()]
    if 'primi_capitoli' in gate and stato['ultimo_capitolo_approvato'] is None and scritto >= min(3, totale or 3):
        apri_gate(cartella, libro, stato, 'primi_capitoli')
        return
    if numerici and (len(numerici) >= stato['lotto']['dimensione'] or (totale and scritto >= totale)):
        if 'lotto' in gate:
            apri_gate(cartella, libro, stato, 'lotto')
            return
        print(f'Lotto completato ({", ".join(map(str, stato["lotto"]["capitoli"]))}): nessuna fermata '
              '(gate «lotto» non attivo in libro.yaml).')
        stato['lotto']['capitoli'] = []
    if totale and scritto >= totale:
        mancanti = unita_mancanti(cartella, libro, stato)
        if mancanti:
            # la fase resta «stesura» finché manca un'unità del piano (prologo, interludi, epilogo)
            stato['passo'] = passo_di(mancanti[0])
            print(f'Capitoli scritti; mancano ancora: {", ".join(mancanti)}. La fase resta «stesura».')
            return
        stato.update(fase='chiusura', passo='controlli finali', gate_in_attesa=None)
        print(f'Tutte le unità del piano sono scritte e accettate: fase «chiusura».')


# ---------------------------------------------------------------- comandi

def cmd_stato(cartella, libro, stato):
    rc = stato.get('revisione_in_corso')
    codice, sub, _ = comune.git(cartella, 'log', '-1', '--format=%h «%s»')
    c2, conti, _ = comune.git(cartella, 'rev-list', '--left-right', '--count', 'HEAD...@{u}')
    if c2 == 0 and conti.split() == ['0', '0']:
        allineato = 'sì'
    elif c2 == 0:
        a, d = conti.split()
        allineato = f'no (avanti {a}, indietro {d})'
    else:
        allineato = 'nessun ramo remoto collegato'
    righe = [f'Libro: {libro["titolo"]} ({cartella}); modalità {libro.get("modalita", "nuovo")}',
             f'Fase: {stato["fase"]}; passo: {stato["passo"] or "—"}; gate in attesa: {stato["gate_in_attesa"] or "nessuno"}',
             f'Gate attivi (libro.yaml): {", ".join(gate_attivi(libro))}',
             f'Lotto: dimensione {stato["lotto"]["dimensione"]}, capitoli {stato["lotto"]["capitoli"] or "—"}',
             f'Capitoli: scritti fino a {stato["ultimo_capitolo_scritto"] or "—"}, approvati fino a '
             f'{stato["ultimo_capitolo_approvato"] or "—"}, previsti {capitoli_previsti(cartella) or "—"}',
             f'Parole: {stato["parole"]["scritte"]}/{stato["parole"]["obiettivo"]} (metodo unico)',
             'Revisione: ' + (f'blocco {rc["blocco"]} di {rc["blocchi_totali"]} (gate {rc["gate"]})' if rc else 'nessuna'),
             f'Correzioni aperte: {len(stato["correzioni_aperte"])}; '
             f'correzioni registrate fuori dal gate: {len(stato.get("correzioni_registrate") or [])}']
    righe += [f'  - [{c["gate"]}] {c["testo"]}' for c in stato['correzioni_aperte']]
    righe += [f'Controlli falliti di fila: {stato["tentativi"] or "nessuno"}',
              f'Avvisi aperti: {len(stato["avvisi_aperti"])}',
              f'Documenti approvati: {len(stato["documenti_approvati"])}',
              f'Ramo: {comune.ramo(cartella) or "—"}; ultimo commit: {sub if codice == 0 else "—"}; '
              f'allineato a origin: {allineato}',
              prossimo(stato)]
    print('\n'.join(righe))


def cmd_pronto(cartella, libro, stato):
    if stato['gate_in_attesa']:
        raise comune.ErroreMotore(f'Gate «{stato["gate_in_attesa"]}» già aperto: avanti, ok o correggi.')
    fase = stato['fase']
    if fase in ('documenti', 'pagina_campione'):
        docs = revisione.documenti_del_gate(cartella, libro, stato, fase)
        manca = [d for d in docs if not os.path.isfile(os.path.join(cartella, d))]
        if manca:
            raise comune.ErroreMotore('Documenti mancanti: ' + ', '.join(manca))
        pc = os.path.join(cartella, revisione.PAGINA_CAMPIONE)
        if fase == 'pagina_campione' and not conta.conta_testo(open(pc, encoding='utf-8').read()):
            raise comune.ErroreMotore(f'{revisione.PAGINA_CAMPIONE} è ancora vuota: scrivila, poi «zb pronto <libro>».')
        if fase in gate_attivi(libro):
            apri_gate(cartella, libro, stato, fase, passo='in revisione')
        else:
            registra(cartella, stato, docs, senza_gate=True)
            chiudi_fase(cartella, libro, stato)
            print(f'Gate «{fase}» non previsto in libro.yaml: documenti registrati senza fermata; fase «{stato["fase"]}».')
    elif fase == 'chiusura':
        nome = comune.nome_file(libro['titolo'])
        manca = [f'{p.format(nome=nome)} ({c})' for p, c in CHIUSURA
                 if not os.path.isfile(os.path.join(cartella, p.format(nome=nome)))]
        if manca:
            raise comune.ErroreMotore('Chiusura incompleta. Mancano:\n- ' + '\n- '.join(manca))
        stato.update(fase='chiuso', passo=None)
        print('Chiusura completa: libro chiuso.')
    else:
        raise comune.ErroreMotore(f'«pronto» non vale in fase «{fase}». ' + prossimo(stato))


def cmd_ok(cartella, libro, stato, resto):
    gate = stato['gate_in_attesa']
    if not gate:
        raise comune.ErroreMotore('Nessun gate aperto: niente da approvare. ' + prossimo(stato))
    docs = revisione.documenti_del_gate(cartella, libro, stato, gate)
    imp = revisione.impronta(cartella, docs)
    rc = stato.get('revisione_in_corso')
    if not rc or rc.get('gate') != gate or rc.get('sha256') != imp:
        raise comune.ErroreMotore('«ok» vale solo per documenti mostrati per intero: i documenti del gate '
                                  'non sono stati mostrati o sono cambiati. Scrivi avanti.')
    if rc['blocco'] < rc['blocchi_totali']:
        raise comune.ErroreMotore(f'Mancano i blocchi {rc["blocco"] + 1}-{rc["blocchi_totali"]} di '
                                  f'{rc["blocchi_totali"]}: prima li mostro. Scrivi avanti.')
    pendenti = [c for c in stato['correzioni_aperte'] if c['gate'] == gate and c['sha256'] == imp]
    if pendenti:
        raise comune.ErroreMotore('Correzione registrata ma non ancora applicata (documenti invariati): '
                                  + '; '.join(c['testo'] for c in pendenti))
    m = re.search(r'lott\w*\s+da\s+(\d+)', ' '.join(resto))
    registra(cartella, stato, docs)
    stato['correzioni_aperte'] = [c for c in stato['correzioni_aperte'] if c['gate'] != gate]
    if m:
        stato['lotto']['dimensione'] = int(m.group(1))
        print(f'Lotti successivi: {m.group(1)} capitoli.')
    stato['revisione_in_corso'] = None
    stato['gate_in_attesa'] = None
    print(f'Gate «{gate}» approvato: {len(docs)} documenti registrati con sha256 e commit.')
    if gate in ('documenti', 'pagina_campione'):
        chiudi_fase(cartella, libro, stato)
    elif gate in ('primi_capitoli', 'lotto'):
        numerici = [int(c) for c in stato['lotto']['capitoli'] if str(c).isdigit()]
        stato['ultimo_capitolo_approvato'] = max(numerici + [stato['ultimo_capitolo_approvato'] or 0])
        stato['lotto']['capitoli'] = []
        dopo_capitolo(cartella, libro, stato)
    elif gate == 'controllo_fallito':
        n = str(stato['passo']).replace('capitolo ', '')
        stato['tentativi'].pop(n, None)
        print(f'Capitolo {n} accettato così com\'è, per decisione dell\'autore.')
        accetta_capitolo(cartella, libro, stato, n)


def file_unita(cartella, libro, rif):
    """Percorso relativo al libro per «capitolo N», «N», «interludio X», «prologo», «epilogo» o un file del libro."""
    r = rif.strip()
    r = r[len('capitolo '):] if r.lower().startswith('capitolo ') else r
    unita = dict(comune.unita(cartella, libro))
    if r in unita:
        return os.path.relpath(unita[r], cartella)
    p = os.path.normpath(os.path.join(cartella, r))
    if p.startswith(os.path.abspath(cartella) + os.sep) and os.path.isfile(p):
        return os.path.relpath(p, cartella)
    raise comune.ErroreMotore(f'«{rif}»: né un\'unità di 04-manoscritto né un file del libro')


def sha_versione(cartella, commit, rel):
    """sha256 del file `rel` (relativo al libro) nella versione del commit; None se lì non esiste."""
    import hashlib
    r = subprocess.run(['git', '-C', cartella, 'show', f'{commit}:./{rel}'], capture_output=True)
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None


def nome_precedente(cartella, comando_git, rel):
    """Nome vecchio di `rel` in un elenco «git diff --name-status -M» (righe R<n> vecchio nuovo); None se non rinominato."""
    for riga in comune.git(cartella, *comando_git)[1].splitlines():
        c = riga.split('\t')
        if len(c) == 3 and c[0].startswith('R') and c[2] == rel:
            return c[1]
    return None


def registra_correzione(cartella, libro, stato, resto):
    """Correzione fuori dal gate: «<unità o file>: <motivo> [--commit <hash>]». Registra data, file, motivo,
    sha256 precedente e attuale; non apre e non chiude nessun gate.

    sha256 precedente: con --commit, la versione prima di quel commit; altrimenti la versione salvata
    (HEAD) se il file ha modifiche non salvate, o la versione prima dell'ultimo commit che lo tocca;
    se per quel file ci sono già correzioni registrate a partire da quella versione (più correzioni prima
    dello stesso commit), vale l'ultima versione corretta registrata."""
    commit = None
    if '--commit' in resto:
        i = resto.index('--commit')
        if i + 1 >= len(resto):
            raise comune.ErroreMotore('--commit vuole un hash')
        commit = resto[i + 1]
        resto = resto[:i] + resto[i + 2:]
    testo = ' '.join(resto).strip()
    if ':' not in testo:
        raise comune.ErroreMotore('Uso: correggi <unità o file>: <motivo> [--commit <hash>]')
    rif, motivo = (x.strip() for x in testo.split(':', 1))
    if not motivo:
        raise comune.ErroreMotore('Manca il motivo della correzione')
    rel = file_unita(cartella, libro, rif)
    attuale = comune.sha256_file(os.path.join(cartella, rel))
    if commit:
        prima, dopo = sha_versione(cartella, f'{commit}^', rel), sha_versione(cartella, commit, rel)
        if dopo is None:
            raise comune.ErroreMotore(f'Il commit {commit} non contiene {rel}')
        if prima is None:       # file rinominato in quel commit: la versione precedente sta sotto il nome vecchio
            vecchio = nome_precedente(cartella, ['diff', '-M', '--name-status', '--relative', f'{commit}^', commit], rel)
            prima = sha_versione(cartella, f'{commit}^', vecchio) if vecchio else None
    else:
        modificato = comune.git(cartella, 'status', '--porcelain', '--', rel)[1]
        if modificato:
            prima = sha_versione(cartella, 'HEAD', rel)
            if prima is None:   # rinomina non ancora salvata (git mv)
                vecchio = nome_precedente(cartella, ['diff', '--cached', '-M', '--name-status', '--relative', 'HEAD'], rel)
                prima = sha_versione(cartella, 'HEAD', vecchio) if vecchio else None
        else:
            # --follow: la storia continua sotto il nome vecchio, se il file è stato rinominato
            out = comune.git(cartella, 'log', '--follow', '-M', '-2', '--format=@%h', '--name-only', '--relative',
                             '--', rel)[1]
            voci, cur = [], None
            for riga in out.splitlines():
                if riga.startswith('@'):
                    cur = [riga[1:], None]
                    voci.append(cur)
                elif riga.strip() and cur and cur[1] is None:
                    cur[1] = riga.strip()
            prima = sha_versione(cartella, voci[1][0], voci[1][1] or rel) if len(voci) > 1 else None
        dopo = attuale
        # più correzioni prima dello stesso commit: la versione precedente è l'ultima già registrata,
        # seguendo la catena precedente -> corretto delle registrazioni dello stesso file
        for v in stato.get('correzioni_registrate') or []:
            if v.get('file') == rel and v.get('sha256_precedente') == prima and v.get('sha256_corretto') != dopo:
                prima = v['sha256_corretto']
    if prima == dopo:
        raise comune.ErroreMotore(f'{rel}: nessuna differenza tra la versione precedente e quella corretta')
    voce = {'data': datetime.date.today().isoformat(), 'file': rel, 'motivo': motivo,
            'sha256_precedente': prima, 'sha256_corretto': dopo}
    if commit:
        voce['commit'] = commit
    stato.setdefault('correzioni_registrate', []).append(voce)
    print(f'Correzione registrata: {rel}; motivo: {motivo}; sha256 precedente {(prima or "—")[:12]}, '
          f'corretto {dopo[:12]}. Gate invariato ({stato["gate_in_attesa"] or "nessuno"}).')


def cmd_correggi(cartella, libro, stato, resto):
    gate = stato['gate_in_attesa']
    if not gate or '--commit' in resto:     # fuori dal gate, o correzione già salvata: solo registro
        registra_correzione(cartella, libro, stato, resto)
        return
    testo = ' '.join(resto).strip().lstrip(':').strip()
    if not testo:
        raise comune.ErroreMotore('Uso: correggi <istruzione>')
    docs = revisione.documenti_del_gate(cartella, libro, stato, gate)
    stato['correzioni_aperte'].append({'gate': gate, 'testo': testo, 'sha256': revisione.impronta(cartella, docs),
                                       'data': datetime.date.today().isoformat()})
    print(f'Correzione registrata al gate «{gate}»: {testo}\n'
          'Applico solo questa, rieseguo i controlli e mostro le righe cambiate (prima e dopo). '
          'Il gate resta aperto; dopo la correzione «avanti» riparte dal blocco 1.')


def cmd_fase(cartella, libro, stato, resto):
    """«fase stesura --motivo <testo>»: da «chiusura» torna a «stesura» se nel piano mancano unità."""
    if '--motivo' not in resto or resto[0:1] != ['stesura']:
        raise comune.ErroreMotore('Uso: fase <libro> stesura --motivo "<testo>"')
    motivo = ' '.join(resto[resto.index('--motivo') + 1:]).strip()
    if not motivo:
        raise comune.ErroreMotore('Manca il motivo («--motivo "<testo>"»)')
    if stato['fase'] != 'chiusura':
        raise comune.ErroreMotore(f'Il libro è in fase «{stato["fase"]}»: si torna a «stesura» solo da «chiusura».')
    mancanti = unita_mancanti(cartella, libro, stato)
    if not mancanti:
        raise comune.ErroreMotore('Tutte le unità del piano sono scritte e accettate: la fase resta «chiusura».')
    stato.setdefault('cambi_fase', []).append({'data': datetime.date.today().isoformat(), 'da': stato['fase'],
                                               'a': 'stesura', 'motivo': motivo, 'mancanti': mancanti})
    stato.update(fase='stesura', passo=passo_di(mancanti[0]), gate_in_attesa=None)
    print(f'Fase «chiusura» → «stesura»; motivo: {motivo}. Mancano: {", ".join(mancanti)}.')


def cmd_riapprova(cartella, stato, resto):
    if len(resto) < 2:
        raise comune.ErroreMotore('Uso: riapprova <documento> <motivo>')
    rel, motivo = resto[0], ' '.join(resto[1:]).strip()
    prima = stato['documenti_approvati'].get(rel)
    if not prima:
        raise comune.ErroreMotore(f'«{rel}» non è tra i documenti approvati: ' + ', '.join(stato['documenti_approvati']))
    if comune.documento_invariato(os.path.join(cartella, rel), prima['sha256'], prima.get('commit')):
        raise comune.ErroreMotore(f'{rel} non è cambiato dall\'approvazione: niente da registrare.')
    registra(cartella, stato, [rel])
    voce = stato['documenti_approvati'][rel]
    voce.update({k: v for k, v in prima.items() if k not in ('sha256', 'commit', 'riapprovazioni')})
    voce['riapprovazioni'] = (prima.get('riapprovazioni') or []) + [
        {'data': datetime.date.today().isoformat(), 'motivo': motivo, 'sha256_precedente': prima['sha256'],
         'commit_precedente': prima['commit']}]
    print(f'Modifica autorizzata registrata: {rel} (commit {voce["commit"]}); motivo: {motivo}.')


def accetta_capitolo(cartella, libro, stato, n):
    if n.isdigit():
        prima = stato['ultimo_capitolo_scritto'] or 0
        stato['ultimo_capitolo_scritto'] = max(int(n), prima)
        if int(n) >= prima:      # un capitolo già scritto, ricontrollato, non riporta indietro il passo
            stato['passo'] = f'capitolo {stato["ultimo_capitolo_scritto"] + 1}'
    else:
        acc = stato.setdefault('unita_accettate', [])
        if n.lower() not in [str(x).lower() for x in acc]:
            acc.append(n)
        if str(stato.get('passo') or '').lower() == n.lower():
            mancanti = [u for u in unita_mancanti(cartella, libro, stato) if u.lower() != n.lower()]
            prossimo_cap = f'capitolo {(stato["ultimo_capitolo_scritto"] or 0) + 1}'
            stato['passo'] = passo_di(mancanti[0]) if mancanti else prossimo_cap
    if n not in [str(c) for c in stato['lotto']['capitoli']]:
        stato['lotto']['capitoli'].append(int(n) if n.isdigit() else n)
    stato['parole']['scritte'] = parole_scritte(cartella, libro)
    if stato['gate_in_attesa'] == 'controllo_fallito':
        stato['gate_in_attesa'] = None
        stato['revisione_in_corso'] = None
    dopo_capitolo(cartella, libro, stato)


def aggiorna_piano(cartella, libro, n):
    """Scrive in piano-parole.md le misure dell'unità n («Parole reali», «Scarto») e il «Totale previsto».

    Sono colonne di misura, escluse dall'impronta del documento approvato: nessuna riapprovazione."""
    rel = '03-architettura/piano-parole.md'
    p = os.path.join(cartella, rel)
    u = dict(comune.unita(cartella, libro)).get(n)
    if not os.path.isfile(p) or not u:
        return None
    parole = conta.conta_testo(open(u, encoding='utf-8').read())
    righe = open(p, encoding='utf-8').read().split('\n')
    intest, cambiata = None, None
    for i, r in enumerate(righe):
        if not r.strip().startswith('|'):
            continue
        celle = [c.strip() for c in r.strip().strip('|').split('|')]
        if intest is None:
            intest = celle
            if not all(k in intest for k in ('Cap.', 'Budget capitolo', 'Parole reali', 'Scarto')):
                return None
            continue
        ic = intest.index('Cap.')
        if len(celle) != len(intest) or celle[ic].lower() != n.lower():
            continue
        grezzo = celle[intest.index('Budget capitolo')]
        cifre = re.sub(r'[^\d]', '', grezzo)
        italiano = '.' in grezzo
        virgola = italiano or libro.get('lingua') == 'it'
        celle[intest.index('Parole reali')] = f'{parole:,}'.replace(',', '.' if italiano else '')
        if cifre:
            sc = (parole - int(cifre)) / int(cifre) * 100
            celle[intest.index('Scarto')] = f'{sc:+.1f}%'.replace('.', ',' if virgola else '.')
        righe[i] = '| ' + ' | '.join(celle) + ' |'
        cambiata = righe[i]
    if cambiata is None:
        return None
    if libro.get('lingua') == 'it':
        # tutte le percentuali di scarto con la virgola (anche quelle scritte prima)
        isc = intest.index('Scarto')
        for i, r in enumerate(righe):
            celle = [c.strip() for c in r.strip().strip('|').split('|')]
            if r.strip().startswith('|') and len(celle) == len(intest) and re.fullmatch(r'[+-]\d+\.\d%', celle[isc]):
                celle[isc] = celle[isc].replace('.', ',')
                righe[i] = '| ' + ' | '.join(celle) + ' |'
    testo = '\n'.join(righe)
    m = re.search(r'Totale previsto[^:]*:\s*(\d{1,3}(?:\.\d{3})+|\d+)', testo)
    if m:
        previsto = conta.totale_previsto(cartella, libro, comune.carica_libro(cartella)[2])[1]
        testo = testo[:m.start(1)] + (f'{previsto:,}'.replace(',', '.') if '.' in m.group(1) else str(previsto)) + testo[m.end(1):]
    comune.scrivi(cartella, rel, testo)
    return cambiata


def esito_in_chiusura(cartella, libro, stato, n, argv):
    """In «chiusura», esito su un'unità già scritta (dopo una correzione): rifà i controlli, aggiorna piano e
    parole, non tocca fase, passo, tentativi e gate."""
    extra = ['--radice', argv[argv.index('--radice') + 1]] if '--radice' in argv else []
    r = subprocess.run([sys.executable, '-B', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capitolo.py'),
                        cartella, *n.split(), *extra], capture_output=True, text=True)
    if r.returncode not in (0, 1):
        raise comune.ErroreMotore(f'capitolo.py {n} non eseguito: {r.stderr.strip() or r.stdout.strip()}')
    riga_piano = aggiorna_piano(cartella, libro, n)
    if riga_piano:
        print(f'Piano parole aggiornato (misure, senza riapprovazione): {riga_piano}')
    stato['parole']['scritte'] = parole_scritte(cartella, libro)
    rep = f'06-diagnostica/capitoli/{revisione.nome_report(n)}.md'
    print(f'Unità {n} ricontrollata in fase «chiusura»: controlli {"OK" if r.returncode == 0 else "KO"} '
          f'(report: {rep}); la fase non cambia.')
    return r.returncode


def cmd_esito(cartella, libro, stato, resto, argv):
    if not resto:
        raise comune.ErroreMotore('Uso: esito <N>')
    n = ' '.join(resto)
    n = str(int(n)) if n.isdigit() else n
    gate = stato['gate_in_attesa']
    if stato['fase'] == 'chiusura' and n.lower() in {u.lower() for u, _ in comune.unita(cartella, libro)}:
        return esito_in_chiusura(cartella, libro, stato, n, argv)
    if stato['fase'] != 'stesura':
        mancanti = unita_mancanti(cartella, libro, stato) if stato['fase'] == 'chiusura' else []
        extra = (f' Mancano unità del piano ({", ".join(mancanti)}): «zb fase <libro> stesura --motivo "…"».'
                 if mancanti else '')
        raise comune.ErroreMotore(f'«esito» vale solo in fase «stesura» (ora: {stato["fase"]}).{extra}')
    piano = unita_del_piano(cartella)
    if piano and n.lower() not in [u.lower() for u in piano]:
        raise comune.ErroreMotore(f'«{n}» non è un\'unità del piano parole: {", ".join(piano)}')
    correzione = (gate in ('primi_capitoli', 'lotto') and n in [str(c) for c in stato['lotto']['capitoli']]
                  and any(c['gate'] == gate for c in stato['correzioni_aperte']))
    if gate and not correzione and not (gate == 'controllo_fallito' and str(stato['passo']) == f'capitolo {n}'):
        raise comune.ErroreMotore(f'Gate «{gate}» aperto: prima ok o correggi.')
    extra = ['--radice', argv[argv.index('--radice') + 1]] if '--radice' in argv else []
    r = subprocess.run([sys.executable, '-B', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capitolo.py'),
                        cartella, *n.split(), *extra], capture_output=True, text=True)
    if r.returncode not in (0, 1):
        raise comune.ErroreMotore(f'capitolo.py {n} non eseguito: {r.stderr.strip() or r.stdout.strip()}')
    riga_piano = aggiorna_piano(cartella, libro, n)
    if riga_piano:
        print(f'Piano parole aggiornato (misure, senza riapprovazione): {riga_piano}')
    if correzione:
        stato['parole']['scritte'] = parole_scritte(cartella, libro)
        print(f'Capitolo {n} corretto al gate «{gate}»: controlli {"OK" if r.returncode == 0 else "KO"}; '
              f'parole del libro aggiornate ({stato["parole"]["scritte"]}). Il gate resta aperto: '
              '«avanti» riparte dal blocco 1.')
        return r.returncode
    if r.returncode == 0:
        stato['tentativi'].pop(n, None)
        print(f'Capitolo {n}: controlli OK.')
        accetta_capitolo(cartella, libro, stato, n)
        return 0
    stato['tentativi'][n] = stato['tentativi'].get(n, 0) + 1
    rep = f'06-diagnostica/capitoli/{revisione.nome_report(n)}.md'
    if stato['tentativi'][n] >= 2:
        print(f'FERMO: capitolo {n}, controlli falliti per la seconda volta di fila. Report: {rep}.\n'
              'Scrivo quale controllo, valore, soglia, file e righe; decide l\'autore (ok = accetta, correggi: …).')
        apri_gate(cartella, libro, stato, 'controllo_fallito', passo=f'capitolo {n}')
    else:
        print(f'Capitolo {n}: controlli KO (primo tentativo). Report: {rep}.\n'
              'Una sola correzione mirata sul punto indicato, poi «zb esito <libro> N» di nuovo.')
    return 1


def main(argv):
    args = [a for i, a in enumerate(argv) if a != '--radice' and (i == 0 or argv[i - 1] != '--radice')]
    if len(args) < 2:
        raise comune.ErroreMotore('Uso: fase.py <libro> stato|avanti|ok|correggi|riapprova|pronto|esito|fase [argomenti]')
    cartella, libro, _ = comune.carica_libro(args[0])
    comando, resto = args[1], args[2:]
    stato = carica_stato(cartella)
    if comando == 'stato':
        cmd_stato(cartella, libro, stato)
        return 0
    codice = 0
    # i messaggi del comando si raccolgono e si stampano solo dopo aver salvato stato.yaml: un'uscita
    # interrotta (pipe chiusa, terminale chiuso) non deve perdere lo stato
    uscita = io.StringIO()
    try:
        with contextlib.redirect_stdout(uscita):
            if comando == 'avanti':
                avanti(cartella, libro, stato)
            elif comando == 'ok':
                cmd_ok(cartella, libro, stato, resto)
            elif comando == 'correggi':
                cmd_correggi(cartella, libro, stato, resto)
            elif comando == 'pronto':
                cmd_pronto(cartella, libro, stato)
            elif comando == 'riapprova':
                cmd_riapprova(cartella, stato, resto)
            elif comando == 'esito':
                codice = cmd_esito(cartella, libro, stato, resto, argv)
            elif comando == 'fase':
                cmd_fase(cartella, libro, stato, resto)
            else:
                raise comune.ErroreMotore(f'Comando sconosciuto: {comando}. Comandi: stato, avanti, ok, correggi, '
                                          'riapprova, pronto, esito, fase.')
    except comune.ErroreMotore:
        sys.stdout.write(uscita.getvalue())
        raise
    salva_stato(cartella, stato)
    sys.stdout.write(uscita.getvalue())
    print(f'Fase: {stato["fase"]}; gate in attesa: {stato["gate_in_attesa"] or "nessuno"}. {prossimo(stato)}')
    print(SALVA)
    return codice


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/impagina.py`

```python
"""Impaginazione del PDF di stampa (proposta B.2, B.3).

Uso: python3 -B impagina.py <libro>
Legge <libro>/05-output/<titolo>-completo.md (prima: compila.py) e scrive
<libro>/05-output/<titolo>.pdf:
- md → HTML con stampa/modello.css (formato, margini, font, corpo da libro.yaml);
- render con Chromium (stampa/print.js), separato per pagine iniziali e corpo;
- margine interno = max(tabella KDP per il numero di pagine, margini_mm.interno_scelto);
  se il numero di pagine cambia fascia, si rifà il render;
- pagine iniziali (frontespizio, copyright, sommario) senza numero e in numero pari,
  così il corpo comincia su una pagina dispari;
- sommario con le pagine reali; numeri di pagina stampati con PyMuPDF al piede;
- formato esatto: Chromium arrotonda la pagina (5,83 × 8,27" diventa 5,833 × 8,263"); ogni pagina
  è riportata con PyMuPDF al trim di libro.yaml (più il bleed di dati/kdp.yaml, se previsto), senza
  scalare il contenuto e tenendolo fermo rispetto all'angolo in alto a sinistra;
- metadati Title, Author, Subject; font sottoinsiemi, senza date di creazione.
I file di lavoro stanno in una cartella temporanea fuori dal repository.
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

MM = 25.4


def node_path():
    try:
        r = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True, check=True)
        return r.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return '/opt/node22/lib/node_modules'


def sezioni(md):
    """[(tipo, testo)] dalle righe <!-- zb:sezione tipo -->."""
    parti = re.split(r'^<!-- zb:sezione (\w+) -->\s*$', md, flags=re.M)
    return [(parti[i], parti[i + 1].strip()) for i in range(1, len(parti), 2)]


def html_sezione(tipo, testo):
    import markdown
    corpo = markdown.markdown(testo, extensions=['md_in_html'])
    return f'<section class="{tipo}">\n{corpo}\n</section>'


def css(libro, interno_mm):
    f = libro['formato']
    m = f.get('margini_mm') or {}
    font = f.get('font') or {}
    valori = {
        'font_dir': 'file://' + os.path.join(comune.radice_motore(), 'stampa', 'font'),
        'larghezza': f['pagina_pollici'][0], 'altezza': f['pagina_pollici'][1],
        'alto': m.get('alto', 20), 'basso': m.get('basso', 20),
        'esterno': m.get('esterno', 16), 'interno': round(interno_mm, 2),
        'corpo': font.get('corpo_pt', 11), 'interlinea': font.get('interlinea', 1.45),
    }
    t = open(os.path.join(comune.radice_motore(), 'stampa', 'modello.css'), encoding='utf-8').read()
    for k, v in valori.items():
        t = t.replace('{{' + k + '}}', str(v))
    return t


def render(html_corpo, stile, tmp, nome, base=None):
    """base: cartella da cui risolvere i percorsi relativi (immagini delle appendici in 05-output/)."""
    h = os.path.join(tmp, nome + '.html')
    p = os.path.join(tmp, nome + '.pdf')
    testa = f'<base href="file://{base.rstrip("/")}/">' if base else ''
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f'<!doctype html><html lang="it"><head><meta charset="utf-8">{testa}<style>{stile}</style>'
                f'</head><body>{html_corpo}</body></html>')
    env = dict(os.environ, NODE_PATH=node_path())
    r = subprocess.run(['node', os.path.join(comune.radice_motore(), 'stampa', 'print.js'), h, p],
                       env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise comune.ErroreMotore('Render Chromium fallito: ' + (r.stderr.strip().splitlines() or ['?'])[-1])
    return p


def pagine_inizio(pdf, titoli):
    """{titolo: indice di pagina (0-based)} della prima pagina con una riga uguale al titolo."""
    import pymupdf as fitz
    out = {}
    with fitz.open(pdf) as d:
        for i, pg in enumerate(d):
            righe = [r.strip() for r in pg.get_text('text').splitlines()]
            for t in titoli:
                if t not in out and t in righe:
                    out[t] = i
    return out


def formato_esatto(doc, libro):
    """Porta ogni pagina al formato esatto in punti PDF: trim di libro.yaml, più il bleed se previsto.
    Il contenuto non si scala. Resta fermo rispetto all'angolo in alto a sinistra (con il bleed si sposta
    di un bleed in basso e, sulle pagine pari, a destra, così il trim sta dentro l'area di bleed).
    MediaBox e CropBox coincidono e partono da 0, 0; TrimBox e BleedBox non si scrivono."""
    import pymupdf as fitz
    larg, alt = libro['formato']['pagina_pollici']
    bleed = comune.kdp()['cartaceo']['bleed_pollici'] if libro['formato'].get('bleed') else 0
    W, H = (larg + bleed) * 72, (alt + 2 * bleed) * 72
    for i, pg in enumerate(doc):
        mb = pg.mediabox
        # spostamento in coordinate PDF (y verso l'alto): l'alto della pagina passa da mb.y1 a H - bleed
        dx = (bleed * 72 if i % 2 else 0) - mb.x0
        dy = (H - bleed * 72) - mb.y1
        if abs(dx) > 1e-6 or abs(dy) > 1e-6:
            prima, dopo = doc.get_new_xref(), doc.get_new_xref()
            for x, s in ((prima, f'q 1 0 0 1 {dx:.4f} {dy:.4f} cm\n'), (dopo, '\nQ\n')):
                doc.update_object(x, '<<>>')
                doc.update_stream(x, s.encode())
            cont = ' '.join(f'{x} 0 R' for x in pg.get_contents())
            doc.xref_set_key(pg.xref, 'Contents', f'[{prima} 0 R {cont} {dopo} 0 R]')
        pg.set_mediabox(fitz.Rect(0, 0, W, H))
        pg.set_cropbox(fitz.Rect(0, 0, W, H))


def impagina(cartella, libro):
    import pymupdf as fitz
    md_rel = f'05-output/{comune.nome_file(libro["titolo"])}-completo.md'
    md_path = os.path.join(cartella, md_rel)
    if not os.path.isfile(md_path):
        raise comune.ErroreMotore(f'Manca {md_rel}: esegui prima compila.py')
    sez = sezioni(open(md_path, encoding='utf-8').read())
    iniziali = [(t, s) for t, s in sez if t in ('frontespizio', 'copyright', 'sommario')]
    corpo = [(t, s) for t, s in sez if t not in ('frontespizio', 'copyright', 'sommario')]
    sommario = next(s for t, s in iniziali if t == 'sommario')
    voci = [re.sub(r'^-\s+', '', r).strip() for r in sommario.splitlines() if r.startswith('- ')]
    titoli = [v.strip('*') for v in voci]
    m = libro['formato'].get('margini_mm') or {}
    scelto = m.get('interno_scelto', m.get('esterno', 16))
    tmp = tempfile.mkdtemp(prefix='zb-impagina-')
    try:
        html_corpo = '\n'.join(html_sezione(t, s) for t, s in corpo)
        interno = scelto
        for _ in range(3):
            pdf_corpo = render(html_corpo, css(libro, interno), tmp, 'corpo', os.path.dirname(md_path))
            with fitz.open(pdf_corpo) as d:
                n_corpo = d.page_count
            stima = n_corpo + 4
            richiesto = max(comune.kdp_interno_pollici(stima) * MM, scelto)
            if abs(richiesto - interno) < 0.01:
                break
            interno = richiesto
        inizio = pagine_inizio(pdf_corpo, titoli)
        mancanti = [t for t in titoli if t not in inizio]
        if mancanti:
            raise comune.ErroreMotore(f'Titoli del sommario non trovati nel PDF: {", ".join(mancanti)}')
        righe_somm = []
        for v, t in zip(voci, titoli):
            classe = 'voce parte' if v.startswith('**') else 'voce'
            righe_somm.append(f'<div class="{classe}"><span>{t}</span><span class="punti"></span>'
                              f'<span>{inizio[t] + 1}</span></div>')
        html_iniz = '\n'.join(html_sezione(t, s) for t, s in iniziali if t != 'sommario')
        html_iniz += '\n<section class="sommario"><h2>Sommario</h2>\n' + '\n'.join(righe_somm) + '\n</section>'
        pdf_iniz = render(html_iniz, css(libro, interno), tmp, 'iniziali')
        doc = fitz.open(pdf_iniz)
        if doc.page_count % 2:
            w, h = doc[0].rect.width, doc[0].rect.height
            doc.new_page(width=w, height=h)
        n_iniz = doc.page_count
        with fitz.open(pdf_corpo) as dc:
            doc.insert_pdf(dc)
        formato_esatto(doc, libro)
        font = os.path.join(comune.radice_motore(), 'stampa', 'font', 'EBGaramond-Regular.ttf')
        basso_pt = m.get('basso', 20) / MM * 72
        # numeri al centro del piede del trim: con il bleed il trim è spostato come il contenuto
        b = comune.kdp()['cartaceo']['bleed_pollici'] * 72 if libro['formato'].get('bleed') else 0
        for i in range(n_iniz, doc.page_count):
            pg = doc[i]
            num = str(i - n_iniz + 1)
            f = fitz.Font(fontfile=font)
            larg = f.text_length(num, fontsize=9)
            x0 = b if i % 2 else 0
            pg.insert_font(fontname='ZBNum', fontfile=font)
            pg.insert_text((x0 + (pg.rect.width - b - larg) / 2, b + (pg.rect.height - 2 * b) - basso_pt / 2), num,
                           fontname='ZBNum', fontsize=9, color=(0.2, 0.2, 0.2))
        doc.set_metadata({'title': libro['titolo'], 'author': libro['autore'],
                          'subject': libro.get('sottotitolo') or '', 'creator': 'motore', 'producer': 'motore',
                          'creationDate': '', 'modDate': '', 'keywords': ''})
        doc.subset_fonts()
        uscita = comune.percorso_in_libro(cartella, f'05-output/{comune.nome_file(libro["titolo"])}.pdf')
        doc.save(uscita, garbage=4, deflate=True, no_new_id=True)
        doc.close()
        return uscita, n_iniz, interno
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: impagina.py <libro>')
    cartella, libro, _ = comune.carica_libro(args[0])
    uscita, n_iniz, interno = impagina(cartella, libro)
    print(f'scritto {uscita} (pagine iniziali: {n_iniz}, margine interno: {interno:.1f} mm)')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/kdp_verifica.py`

```python
"""Verifica delle direttive KDP da parte dell'autore (proposta A.8).

Uso:
  python3 -B kdp_verifica.py fatta [AAAA-MM-GG] [--oggi AAAA-MM-GG]
      L'autore dichiara di aver verificato le pagine ufficiali: scrive ultima_verifica in
      dati/kdp.yaml e aggiunge una riga a dati/verifiche-kdp.md. Senza data vale oggi.
      Rifiuta una data futura o scritta male; accetta una data già scaduta con un avviso.
  python3 -B kdp_verifica.py controlla [--simula-blocco]
      Prova a raggiungere le pagine ufficiali; se il proxy le blocca (o con --simula-blocco)
      stampa il promemoria dei sette valori da controllare a mano.
  python3 -B kdp_verifica.py stato [--oggi AAAA-MM-GG]
      Stampa lo stato della verifica; codice 2 se mai fatta o più vecchia di validita_giorni.
È l'unico comando del motore che scrive in motore/dati/ (eccezione dichiarata, B.9).
"""
import datetime
import os
import re
import sys
import urllib.error
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402


def stato_verifica(oggi):
    """(scaduta: bool, messaggio)."""
    k = comune.kdp()
    uv = k.get('ultima_verifica')
    validita = k.get('validita_giorni', 30)
    if not uv:
        return True, 'Direttive KDP mai verificate. Riverifica kdp.amazon.com/help prima di pubblicare.'
    if isinstance(uv, str):
        uv = datetime.date.fromisoformat(uv)
    giorni = (oggi - uv).days
    if giorni > validita:
        return True, (f'Direttive KDP verificate l\'ultima volta il {uv} ({giorni} giorni fa). '
                      'Riverifica kdp.amazon.com/help prima di pubblicare e aggiorna ultima_verifica.')
    return False, f'Direttive KDP verificate il {uv} ({giorni} giorni fa, validità {validita} giorni).'


def promemoria():
    k = comune.kdp()
    m, c = k['metadati'], k['cartaceo']
    fasce = ' | '.join(f'{f["da"]}-{f["a"]} p {str(f["pollici"]).replace(".", ",")}"' for f in c['margine_interno_per_pagine'])
    est = c['margine_esterno_min_pollici']
    uv = k.get('ultima_verifica') or 'mai'
    righe = ['Verifica KDP a mano (pagine ufficiali non raggiungibili)', f'Ultima verifica: {uv}', '',
             f'1 Titolo+sottotitolo: < {m["titolo_piu_sottotitolo_max_caratteri"]} caratteri',
             f'2 Descrizione: max {m["descrizione_max_caratteri"]:,} caratteri'.replace(',', '.'),
             f'3 Parole chiave: {m["parole_chiave_max"]} caselle',
             f'4 Margine interno: {fasce}',
             f'5 Margini esterni: {str(est["senza_bleed"]).replace(".", ",")}" senza bleed | '
             f'{str(est["con_bleed"]).replace(".", ",")}" con bleed',
             f'6 Pagine: min {c["pagine_min"]} | max {c["pagine_max"]["bianca"]} bianca, {c["pagine_max"]["crema"]} crema',
             '7 Tag HTML descrizione: ' + ' '.join(m['html_ammesso_descrizione']['tag']), '', 'Link:']
    for p in k.get('pagine_ufficiali') or []:
        righe.append(f'{p["url"].replace("https://", "")}  ({p["tema"]}: {", ".join(map(str, p["valori"]))})')
    righe += ['', 'Se tutto coincide: verifica KDP fatta AAAA-MM-GG',
              'Se qualcosa cambia: correggi: <voce> <valore nuovo>']
    return '\n'.join(righe)


def raggiungibili():
    for p in comune.kdp().get('pagine_ufficiali') or []:
        try:
            with urllib.request.urlopen(p['url'], timeout=20) as r:
                if r.status != 200:
                    return False
        except (urllib.error.URLError, OSError, ValueError):
            return False
    return True


def fatta(argv):
    oggi = comune.oggi(argv)
    pos = [a for a in comune.argomenti(argv) if a != 'fatta']
    try:
        data = datetime.date.fromisoformat(pos[0]) if pos else oggi
    except ValueError:
        print(f'FERMO: data scritta male «{pos[0]}» (serve AAAA-MM-GG)', file=sys.stderr)
        return 1
    if data > oggi:
        print(f'FERMO: data futura rifiutata ({data}, oggi è {oggi})', file=sys.stderr)
        return 1
    dati = os.path.join(comune.radice_motore(), 'dati')
    pk = os.path.join(dati, 'kdp.yaml')
    testo = open(pk, encoding='utf-8').read()
    nuovo, n = re.subn(r'(?m)^ultima_verifica:[^\n#]*', f'ultima_verifica: {data}        ', testo, count=1)
    if n != 1:
        print('FERMO: riga ultima_verifica non trovata in dati/kdp.yaml', file=sys.stderr)
        return 1
    with open(pk, 'w', encoding='utf-8') as f:
        f.write(nuovo)
    with open(os.path.join(dati, 'verifiche-kdp.md'), 'a', encoding='utf-8') as f:
        f.write(f'| {data} | {oggi} | autore | 1-7 (tutti) |\n')
    validita = comune.kdp().get('validita_giorni', 30)
    print(f'ultima_verifica: {data} (registrata in dati/kdp.yaml e dati/verifiche-kdp.md)')
    if (oggi - data).days > validita:
        print(f'AVVISO: la verifica del {data} è già più vecchia di {validita} giorni: il pacchetto resta non pronto.')
    return 0


def main(argv):
    pos = comune.argomenti(argv)
    comando = pos[0] if pos else 'controlla'
    if comando == 'fatta':
        return fatta(argv)
    if comando == 'stato':
        scaduta, msg = stato_verifica(comune.oggi(argv))
        print(msg)
        return 2 if scaduta else 0
    if comando == 'controlla':
        if '--simula-blocco' in argv or not raggiungibili():
            print(promemoria())
        else:
            print('Pagine ufficiali raggiungibili: confronta a mano i valori qui sotto.\n')
            print(promemoria())
        return 0
    print(__doc__)
    return 1


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/nuovo.py`

```python
"""Crea un libro dal briefing (proposta B.4, C.1 fase «documenti», C.3).

Uso: python3 -B nuovo.py <percorso-briefing>
- Il libro è <x> se il briefing sta in <x>/00-progetto/briefing.md; altrimenti è la cartella
  del briefing, e il briefing viene spostato in 00-progetto/briefing.md.
- Si ferma se c'è già un libro.yaml, o se il briefing è incompleto (elenca cosa manca, al massimo
  5 domande): in quel caso non crea nulla.
- Dal briefing (sezione «Direttive») e dal profilo di genere genera: libro.yaml, stato.yaml,
  LEGGIMI.md, cronologia.yaml, nomi_propri.txt, 02-bibbia/bibbia.md,
  03-architettura/manuale-di-stile.md, scaletta.md, piano-parole.md, e le cartelle standard.
  Le regole (tetti, vietati, vincoli, lunghezze, chiusure) vanno in libro.yaml e nel manuale
  senza riscriverle a mano; i contenuti narrativi li scrive Claude Code al gate «documenti».
Il libro nasce solo in <repo>/libri/<slug>/ su un ramo di libro: rifiutato (prima di creare
qualsiasi cosa) se la cartella è dentro motore/, è la radice del repository, o il ramo è «motore».
Unica eccezione: le prove della suite (ZB_PROVE=1) usano cartelle temporanee fuori da libri/, ma
restano rifiutate dentro motore/, nella radice e sul ramo «motore».
Legge solo motore/ e la cartella del libro; dopo la nascita in libri/<slug>/ imposta il libro
attivo (libri/libro-attivo.md, operazione di servizio per hook_recinto.py).
"""
import datetime
import os
import re
import sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import hook_recinto  # noqa: E402

GATE_PREDEFINITI = ['documenti', 'pagina_campione', 'primi_capitoli']
SIGLE = {'gancio_domanda': ['D', 'R', 'P', 'X'], 'gesto_oggetto': ['G', 'O', 'B', 'I'],
         'misto': ['G', 'O', 'B', 'D', 'R']}
SIGNIFICATO_SIGLE = {'G': 'gesto', 'O': 'oggetto', 'B': 'battuta', 'D': 'domanda', 'R': 'rivelazione',
                     'P': 'pericolo', 'X': 'decisione', 'I': 'immagine'}


def sigle_spiegate(sigle):
    """[G, O, B] -> «G gesto, O oggetto, B battuta»."""
    return ', '.join(f'{s} {SIGNIFICATO_SIGLE.get(s, "?")}' for s in sigle)


SEGNAPOSTO = 'Nome — ruolo — età — una riga'


# ---------------------------------------------------------------- briefing

def leggi_briefing(percorso):
    testo = re.sub(r'<!--.*?-->', '', open(percorso, encoding='utf-8').read(), flags=re.S)
    campi, sezioni, liste = {}, {}, {}
    sezione, lista = None, None
    for riga in testo.splitlines():
        s = riga.strip()
        if s.startswith('## '):
            sezione = s[3:].split('(')[0].strip().lower()
            sezioni[sezione] = []
            lista = None
            continue
        m = re.match(r'^([A-Za-zÀ-ÿ\' ]+):\s*(.*)$', s)
        if m and not s.startswith('-'):
            chiave = m.group(1).strip().lower()
            campi[chiave] = m.group(2).strip()
            lista = chiave if not m.group(2).strip() else None
            if lista:
                liste[lista] = []
            continue
        if s.startswith('-') and lista:
            v = s.lstrip('-').strip()
            if v:
                liste[lista].append(v)
            continue
        if sezione is not None and s and not s.startswith('#'):
            sezioni[sezione].append(s)
    personaggi = [p.lstrip('-').strip() for p in sezioni.get('personaggi chiave', [])
                  if p.startswith('-') and p.lstrip('-').strip() and p.lstrip('-').strip() != SEGNAPOSTO]
    elenco = lambda nome: [x.lstrip('-').strip() for x in sezioni.get(nome, []) if x.lstrip('-').strip()]
    return {'campi': campi, 'liste': liste, 'idea': sezioni.get('idea', []),
            'tono': sezioni.get('tono e voce desiderati', []), 'personaggi': personaggi,
            'fatti': elenco('fatti canonici'), 'non_cambiare': elenco('cose da non cambiare'),
            'riferimenti': elenco('riferimenti')}


def mancanze(b, cartella_libro):
    """Voci obbligatorie mancanti o non valide (C.3), come domande per l'autore."""
    c = b['campi']
    out = []
    if not c.get('titolo di lavoro'):
        out.append('Titolo di lavoro: manca')
    if not c.get('autore'):
        out.append('Autore: manca')
    g = c.get('genere', '')
    if not g:
        out.append('Genere: manca (un profilo di motore/profili/)')
    elif not os.path.isfile(os.path.join(comune.radice_motore(), 'profili', f'{g}.yaml')):
        out.append(f'Genere: profilo «{g}» inesistente in motore/profili/')
    lung = re.sub(r'[^\d]', '', c.get('lunghezza', ''))
    if not lung:
        out.append('Lunghezza: manca (numero di parole)')
    elif g and os.path.isfile(os.path.join(comune.radice_motore(), 'profili', f'{g}.yaml')):
        out += override_dal_briefing(c, comune.carica_profilo(g))[1]
    if not 1 <= len(b['idea']) <= 5:
        out.append(f'Idea: servono da 1 a 5 righe (ora {len(b["idea"])})')
    if not any('—' in p for p in b['personaggi']):
        out.append('Personaggi chiave: almeno uno, nella forma «Nome — ruolo — …»')
    mod = c.get('modalità', 'nuovo') or 'nuovo'
    if mod not in ('nuovo', 'riscrittura'):
        out.append(f'Modalità: «{mod}» non ammessa (nuovo | riscrittura)')
    if mod == 'riscrittura':
        tp = c.get('testo precedente', '')
        if not tp:
            out.append('Testo precedente: obbligatorio con Modalità: riscrittura')
        elif not tp.replace(os.sep, '/').startswith('01-originale/'):
            out.append(f'Testo precedente: «{tp}» deve stare in 01-originale/ (struttura standard)')
        elif not os.path.isfile(os.path.join(cartella_libro, tp)) or not comune.dentro(cartella_libro, os.path.join(cartella_libro, tp)):
            out.append(f'Testo precedente: «{tp}» non trovato dentro la cartella del libro')
    elif os.path.isdir(os.path.join(cartella_libro, '01-originale')):
        out.append('Modalità: 01-originale/ esiste solo in riscrittura (scrivi «Modalità: riscrittura» o togli la cartella)')
    return out[:5] if len(out) > 5 else out


def cartella_dal_briefing(percorso):
    p = os.path.realpath(percorso)
    d = os.path.dirname(p)
    if os.path.basename(d) == '00-progetto' and os.path.basename(p) == 'briefing.md':
        return os.path.dirname(d)
    return d


def controlla_posizione(cartella):
    """Radice del repository se la cartella è <repo>/libri/<slug>/ su un ramo di libro (None nelle prove)."""
    c = os.path.realpath(cartella)
    rad = hook_recinto.radice(c)
    regola = 'Il libro nasce solo in libri/<slug>/ su un ramo di libro.'
    if comune.dentro(comune.radice_motore(), c) or (rad and comune.dentro(os.path.join(rad, 'motore'), c)):
        raise comune.ErroreMotore(f'Libro rifiutato: {c} è dentro motore/, che resta sempre pulito. {regola}')
    if rad and c == rad:
        raise comune.ErroreMotore(f'Libro rifiutato: {c} è la radice del repository. {regola}')
    if rad and comune.ramo(rad) == 'motore':
        raise comune.ErroreMotore('Libro rifiutato: il ramo corrente è «motore», che non contiene mai un libro. '
                                  f'Passa a un ramo di libro. {regola}')
    if os.environ.get('ZB_PROVE') == '1':
        return None
    if not rad or os.path.dirname(c) != os.path.join(rad, 'libri'):
        raise comune.ErroreMotore(f'Libro rifiutato: {c} non è libri/<slug>/ del repository. {regola}')
    return rad


# ---------------------------------------------------------------- generazione

def slug(s):
    return comune.nome_file(s).replace('-', '_')


MINIMO_ASSOLUTO = 1000
DESCRIZIONE = {'lunghezza_totale.consigliata': 'Lunghezza', 'capitoli.minimo': 'Capitoli (minimo)',
               'capitoli.media': 'Capitoli (media)', 'capitoli.massimo': 'Capitoli (massimo)',
               'frase_media': 'Frase media', 'dialogo_percento': 'Dialogo',
               'capitoli.scene_per_capitolo': 'Scene (numero)', 'scene.lunghezza': 'Scene (lunghezza)'}


def _intervallo(s):
    m = re.match(r'^\s*(\d+)\s*-\s*(\d+)\s*%?\s*$', s or '')
    return [int(m.group(1)), int(m.group(2))] if m else None


def override_dal_briefing(c, profilo):
    """Valori del briefing fuori dal profilo -> (override, errori).

    Regola: un valore diverso dal profilo vale solo con «Motivo override:» non vuoto.
    Lunghezza fuori dai formati del profilo: serve anche «Capitoli: minimo | media | massimo».
    Sotto MINIMO_ASSOLUTO parole il motore si ferma comunque."""
    valori, err = [], []
    motivo = (c.get('motivo override') or '').strip()
    lung = int(re.sub(r'[^\d]', '', c.get('lunghezza', '')) or 0)
    formati = list(profilo['lunghezza_totale']['formati'].values())
    lo, hi = min(f[0] for f in formati), max(f[1] for f in formati)
    if lung and lung < MINIMO_ASSOLUTO:
        err.append(f'Lunghezza: {lung} sotto il minimo assoluto di {MINIMO_ASSOLUTO:,} parole'.replace(',', '.'))
    elif lung and not lo <= lung <= hi:
        valori.append(('lunghezza_totale.consigliata', [lung, lung], f'{lung} fuori dai formati del profilo ({lo}-{hi})'))
        if not (c.get('capitoli') or '').strip():
            err.append('Capitoli: obbligatorio con una lunghezza fuori profilo '
                       '(«minimo | media | massimo», per esempio 800 | 1000-1300 | 1800)')
    cap = (c.get('capitoli') or '').strip()
    if cap:
        parti = [x.strip() for x in cap.split('|')]
        media = _intervallo(parti[1]) if len(parti) == 3 else None
        if not media or not parti[0].isdigit() or not parti[2].isdigit():
            err.append('Capitoli: forma «minimo | media | massimo», per esempio 800 | 1000-1300 | 1800')
        else:
            mn, mx = int(parti[0]), int(parti[2])
            if not mn <= media[0] <= media[1] <= mx:
                err.append(f'Capitoli: serve minimo ≤ media ≤ massimo (ora {cap})')
            pc = profilo['capitoli']
            for campo, v, att in (('capitoli.minimo', mn, pc['minimo']), ('capitoli.media', media, pc['media']),
                                  ('capitoli.massimo', mx, pc['massimo'])):
                if v != att:
                    valori.append((campo, v, f'{v} invece di {att} del profilo'))
    sc = (c.get('scene') or '').strip()
    if sc:
        parti = [x.strip() for x in sc.split('|')]
        numero = ([int(parti[0])] * 2 if parti[0].isdigit() else _intervallo(parti[0])) if len(parti) == 2 else None
        lung = _intervallo(parti[1]) if len(parti) == 2 else None
        if not numero or not lung:
            err.append('Scene: forma «numero | lunghezza», per esempio 1 | 400-1200 oppure 2-3 | 800-2500')
        else:
            for campo, v, att in (('capitoli.scene_per_capitolo', numero, profilo['capitoli']['scene_per_capitolo']),
                                  ('scene.lunghezza', lung, profilo['scene']['lunghezza'])):
                if v != att:
                    valori.append((campo, v, f'{v} invece di {att} del profilo'))
    # coerenza: le scene previste devono stare in un capitolo medio
    nuovi = {cm: v for cm, v, _ in valori}
    media = nuovi.get('capitoli.media', profilo['capitoli']['media'])
    n_sc = nuovi.get('capitoli.scene_per_capitolo', profilo['capitoli']['scene_per_capitolo'])
    l_sc = nuovi.get('scene.lunghezza', profilo['scene']['lunghezza'])
    if not sc and n_sc[0] * l_sc[0] > media[1]:
        err.append(f'Scene: obbligatorio: {n_sc[0]} scene da almeno {l_sc[0]} parole non stanno in un capitolo '
                   f'medio di {media[1]} («numero | lunghezza», per esempio 1 | 400-1200)')
    for campo, chiave in (('frase_media', 'frase media'), ('dialogo_percento', 'dialogo')):
        if (c.get(chiave) or '').strip():
            v = _intervallo(c[chiave])
            if not v:
                err.append(f'{DESCRIZIONE[campo]}: forma «a-b»')
            elif v != profilo[campo]:
                valori.append((campo, v, f'{v} invece di {profilo[campo]} del profilo'))
    if valori and not motivo:
        err += [f'{DESCRIZIONE[campo]}: {nota}; serve «Motivo override:» nel briefing' for campo, _, nota in valori]
    ov = [{'campo': campo, 'valore': v, 'motivo': f'{motivo} — {DESCRIZIONE[campo]}: {nota}'} for campo, v, nota in valori]
    return ov, err


def profilo_effettivo(profilo, override):
    import copy
    eff = copy.deepcopy(profilo)
    for o in override:
        comune._metti(eff, o['campo'], o['valore'])
    return eff


def parole_dal_briefing(c, profilo):
    """Obiettivo in parole.target_totale; se è fuori dai formati del profilo, il motivo va in
    parole.motivo_fuori_profilo (il profilo non si tocca: lunghezza_totale.consigliata resta com'è)."""
    out = {'metodo': 'unico', 'target_totale': int(re.sub(r'[^\d]', '', c['lunghezza']))}
    for o in override_dal_briefing(c, profilo)[0]:
        if o['campo'] == 'lunghezza_totale.consigliata':
            out['motivo_fuori_profilo'] = o['motivo']
    return out


def genera_libro_yaml(b, profilo):
    c, L = b['campi'], b['liste']
    voci = []
    for t in L.get('tetti', []):
        parti = [x.strip() for x in t.split('|')]
        if len(parti) >= 2 and parti[1].isdigit():
            voci.append({'id': slug(parti[0]), 'espressione': parti[0], 'pattern': r'(?i)(?<!\w)' + re.escape(parti[0]) + r'(?!\w)',
                         'modalita': 'conta', 'massimo': int(parti[1]),
                         'ambito': parti[2] if len(parti) > 2 and parti[2] in ('libro', 'capitolo') else 'capitolo'})
    for v in L.get('vietati', []):
        voci.append({'id': slug(v)[:40], 'espressione': v, 'pattern': r'(?i)(?<!\w)' + re.escape(v) + r'(?!\w)', 'modalita': 'vieta'})
    nomi = []
    for v in L.get('vincoli', []):
        m = re.match(r'^(.+?)\s*\|\s*vietato prima del\s+(\d+)', v)
        if m:
            nome, n = m.group(1).strip(), int(m.group(2))
            nomi.append({'nome': nome, 'pattern': r'\b' + re.escape(nome) + r'\b',
                         'vietato_in': ([f'1-{n - 1}'] if n > 2 else ['1']) if n > 1 else [], 'obbligatorio_in': []})
    fm = re.findall(r'[\d.]+', c.get('formato', '') or '5.5 x 8.5')
    gate = [g.strip() for g in (c.get('gate') or '').split(',') if g.strip()] or GATE_PREDEFINITI
    anni = [int(a) for a in re.findall(r'\d{4}', c.get('anni ammessi', ''))]
    libro = {
        'titolo': c['titolo di lavoro'], 'sottotitolo': None, 'autore': c['autore'], 'lingua': 'it',
        'modalita': c.get('modalità') or 'nuovo',
    }
    if libro['modalita'] == 'riscrittura':
        libro['testo_precedente'] = c['testo precedente']
    libro.update({
        'serie': None, 'ebook': False, 'profilo': c['genere'], 'override': [o for o in override_dal_briefing(c, profilo)[0]
                                              if o['campo'] != 'lunghezza_totale.consigliata'], 'gate': gate,
        'parole': parole_dal_briefing(c, profilo),
        'formato': {'pagina_pollici': [float(fm[0]), float(fm[1])] if len(fm) >= 2 else [5.5, 8.5],
                    'carta': 'crema', 'bleed': False,
                    'margini_mm': {'alto': 20, 'basso': 20, 'esterno': 16, 'interno_scelto': 16},
                    'font': {'nome': 'EB Garamond', 'corpo_pt': 11.5, 'interlinea': 1.5},
                    'numerazione': {'da': 'capitolo_1', 'pagine_iniziali': 'senza_numero', 'posizione': 'piede_centro'}},
        'voci': voci, 'vincoli_capitolo': [], 'nome_vietato_prima_di': nomi,
        'dichiarazioni': {'chiusura': {'sigle': SIGLE[profilo['chiusura_preferita']], 'prevista_da': 'scaletta'}},
        'struttura': {'separatore_scena': {'sorgente': c.get('separatore di scena') or '* * *',
                                           'stampa': c.get('separatore di scena') or '* * *'},
                      'intestazione_capitolo': c.get('intestazione capitolo') or 'Luogo — giorno e data',
                      'parti': [], 'interludi': []},
        'calendario': {'anni_ammessi': anni},
        'ortografia': {'parole_ammesse_file': 'nomi_propri.txt'},
        'copyright': {'riga': '© {anno} {autore}. Tutti i diritti riservati.',
                      'anno': datetime.date.today().year,
                      'fantasia': "Quest'opera è frutto di fantasia. Nomi, personaggi, luoghi e fatti sono invenzione "
                                  "dell'autore o usati in modo fittizio; ogni somiglianza con persone, vive o scomparse, "
                                  "o con fatti realmente accaduti è puramente casuale.",
                      'nota_autore': None},
    })
    if c.get('voce dalla banca'):       # facoltativo: senza, libro.yaml resta quello di sempre
        libro['voce'] = {'slug': c['voce dalla banca'], 'ambientazione': c.get('ambientazione') or 'altro'}
    return libro


def numero_capitoli(libro, profilo):
    media = sum(profilo['capitoli']['media']) / 2
    return max(1, round(libro['parole']['target_totale'] / media))


def dove_capitoli(elenco):
    """«nel capitolo 1», «nei capitoli 1-3», «nei capitoli 1, 4 e 6-8»."""
    elenco = [str(x) for x in elenco or []]
    if not elenco:
        return 'in nessun capitolo'
    if len(elenco) == 1 and '-' not in elenco[0]:
        return f'nel capitolo {elenco[0]}'
    testo = elenco[0] if len(elenco) == 1 else ', '.join(elenco[:-1]) + ' e ' + elenco[-1]
    return f'nei capitoli {testo}'


def genera_manuale(b, libro, profilo, n_cap):
    cap = profilo['capitoli']
    base = comune.leggi_yaml(os.path.join(comune.radice_motore(), 'dati', 'lista-nera.yaml'))
    righe = [f'# Manuale di stile — {libro["titolo"]}', '',
             f'Generato da nuovo.py dal briefing (sezione «Direttive») e dal profilo «{libro["profilo"]}». '
             'Le regole numeriche stanno in libro.yaml e le controlla capitolo.py: qui sono scritte per esteso.', '',
             '## 1. Voce', '',
             f'- Voce: {b["campi"].get("voce") or "da fissare con la pagina campione"}.']
    if libro.get('voce'):
        righe.append(f'- Voce dalla banca-voci: {libro["voce"]["slug"]}, ambientazione {libro["voce"]["ambientazione"]}; '
                     'scheda e briefing da rileggere prima di ogni capitolo (zb avvio, zb voce mostra).')
    righe += [f'- {t}' for t in b['tono']]
    righe += ['- Voce d\'autore: da completare dopo l\'«ok» alla pagina campione.', '',
              '## 2. Lunghezze', '',
              f'- Obiettivo: {libro["parole"]["target_totale"]} parole, circa {n_cap} capitoli.',
              f'- Capitolo: minimo {cap["minimo"]}, media {cap["media"][0]}-{cap["media"][1]}, massimo {cap["massimo"]} parole.',
              f'- Scene: {"-".join(map(str, sorted(set(cap["scene_per_capitolo"]))))} per capitolo, ciascuna '
              f'{profilo["scene"]["lunghezza"][0]}-{profilo["scene"]["lunghezza"][1]} parole (controllate da capitolo.py; '
              f'separatore «{libro["struttura"]["separatore_scena"]["sorgente"]}»).',
              f'- Tolleranza: ±{cap["tolleranza_budget"]:.0%} sul budget del capitolo in piano-parole.md; '
              f'±{cap["tolleranza_totale"]:.0%} sul totale.', '',
              '## 3. Frase e dialogo', '',
              f'- Frase media: {profilo["frase_media"][0]}-{profilo["frase_media"][1]} parole.',
              f'- Dialogo: {profilo["dialogo_percento"][0]}-{profilo["dialogo_percento"][1]}% delle parole del capitolo.',
              f'- Similitudini: al massimo una ogni {profilo["similitudini_max_per_parole"]} parole.', '',
              '## 4. Chiusure', '',
              f'- Chiusura preferita: {profilo["chiusura_preferita"]}. Sigle: {sigle_spiegate(libro["dichiarazioni"]["chiusura"]["sigle"])}.',
              '- Ogni capitolo dichiara la chiusura nella riga nascosta `<!-- zb: chiusura=… -->`; '
              'la sigla prevista sta nella scaletta.', '',
              '## 5. Tetti e vietati', '']
    for v in libro['voci']:
        if v['modalita'] == 'conta':
            righe.append(f'- Tetto: «{v.get("espressione", v["id"])}» al massimo {v["massimo"]} per {v["ambito"]}.')
        else:
            righe.append(f'- Vietato: «{v.get("espressione", v["id"])}».')
    righe += [f'- Lista nera di base (05-critica rr. 19-21): {len(base["voci"])} voci, sempre attive.', '',
              '## 6. Vincoli', '']
    righe += [f'- «{n["nome"]}» non compare {dove_capitoli(n["vietato_in"])}.'
              for n in libro['nome_vietato_prima_di']] or ['- Nessun vincolo.']
    righe += ['', '## 7. Struttura', '',
              f'- Intestazione del capitolo: «{libro["struttura"]["intestazione_capitolo"]}».',
              f'- Separatore di scena: «{libro["struttura"]["separatore_scena"]["sorgente"]}».',
              '- Nomi dei file: NN-<slug>.md in 04-manoscritto/.', '',
              '## 8. Scene obbligatorie del genere', '']
    righe += [f'- {s}' for s in profilo['scene_obbligatorie']]
    righe += ['', '## 9. Override rispetto al profilo (da approvare al gate «documenti»)', '']
    fuori = libro['parole'].get('motivo_fuori_profilo')
    ov_righe = ([f'- parole.target_totale: {libro["parole"]["target_totale"]} — motivo: {fuori}'] if fuori else [])
    ov_righe += [f'- {o["campo"]}: {o["valore"]} — motivo: {o["motivo"]}' for o in libro['override']]
    righe += ov_righe or ['- Nessuno.']
    righe += ['', '## 10. Fatti canonici e cose da non cambiare', '']
    righe += [f'- {f}' for f in b['fatti'] + b['non_cambiare']] or ['- Nessuno.']
    return '\n'.join(righe) + '\n'


def genera_bibbia(b, libro):
    righe = [f'# Bibbia — {libro["titolo"]}', '', '<!-- Da completare al gate «documenti»: luoghi, cronologia, '
             'motivi. I personaggi e i fatti vengono dal briefing. -->', '', '## Personaggi', '']
    for p in b['personaggi']:
        parti = [x.strip() for x in p.split('—')]
        righe.append(f'- **{parti[0]}**: ' + ' — '.join(parti[1:]))
    righe += ['', '## Luoghi', '', '-', '', '## Fatti canonici', '']
    righe += [f'- {f}' for f in b['fatti']] or ['-']
    righe += ['', '## Cose da non cambiare', '']
    righe += [f'- {f}' for f in b['non_cambiare']] or ['-']
    return '\n'.join(righe) + '\n'


def genera_scaletta(libro, n_cap, sigla):
    righe = [f'# Scaletta — {libro["titolo"]}', '',
             '<!-- Da completare al gate «documenti»: data, contenuto e chiusura prevista di ogni capitolo. -->', '',
             '| Unità | Data | Contenuto | Chiusura |', '|---|---|---|---|']
    righe += [f'| {i} |  |  | {sigla} |' for i in range(1, n_cap + 1)]
    return '\n'.join(righe) + '\n'


def genera_piano(libro, n_cap):
    tot = libro['parole']['target_totale']
    budget = round(tot / n_cap)
    righe = [f'# Piano parole — {libro["titolo"]}', '',
             '| Parte | Cap. | Titolo | Funzione | Scene | Budget capitolo | Budget per scena | Parole reali | Scarto |',
             '|---|---|---|---|---|---|---|---|---|']
    righe += [f'| — | {i} |  |  |  | {budget} |  |  |  |' for i in range(1, n_cap + 1)]
    righe += ['', f'Totale: {budget * n_cap}.']
    return '\n'.join(righe) + '\n'


def crea(percorso_briefing):
    cartella = cartella_dal_briefing(percorso_briefing)
    rad = controlla_posizione(cartella)
    if os.path.exists(os.path.join(cartella, 'libro.yaml')):
        raise comune.ErroreMotore(f'C\'è già un libro in {cartella}: nuovo.py non sovrascrive un libro esistente')
    b = leggi_briefing(percorso_briefing)
    manca = mancanze(b, cartella)
    if manca:
        raise comune.ErroreMotore('Briefing incompleto. Mancano:\n- ' + '\n- '.join(manca))
    profilo = comune.carica_profilo(b['campi']['genere'])
    libro = genera_libro_yaml(b, profilo)
    profilo = profilo_effettivo(profilo, libro['override'])
    n_cap = numero_capitoli(libro, profilo)
    dest = os.path.join(cartella, '00-progetto', 'briefing.md')
    if os.path.realpath(percorso_briefing) != os.path.realpath(dest):
        os.replace(percorso_briefing, comune.percorso_in_libro(cartella, '00-progetto/briefing.md'))
    comune.scrivi(cartella, 'libro.yaml', yaml.safe_dump(libro, sort_keys=False, allow_unicode=True, width=120))
    comune.scrivi(cartella, '.gitignore', '.zb/\n')
    m = os.path.join(comune.radice_motore(), 'modelli')
    stato = comune.leggi_yaml(os.path.join(m, 'stato.yaml'))
    stato.update({'libro': libro['titolo'], 'fase': 'documenti', 'passo': 'da completare', 'gate_in_attesa': None,
                  'parole': {'scritte': 0, 'obiettivo': libro['parole']['target_totale'], 'metodo': 'unico'},
                  'aggiornato': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})
    comune.scrivi(cartella, 'stato.yaml', yaml.safe_dump(stato, sort_keys=False, allow_unicode=True))
    comune.scrivi(cartella, 'cronologia.yaml', open(os.path.join(m, 'cronologia.yaml'), encoding='utf-8').read())
    nomi = sorted({w for p in b['personaggi'] for w in p.split('—')[0].split() if w[:1].isupper()})
    comune.scrivi(cartella, 'nomi_propri.txt', '\n'.join(nomi) + '\n')
    comune.scrivi(cartella, '02-bibbia/bibbia.md', genera_bibbia(b, libro))
    comune.scrivi(cartella, '03-architettura/manuale-di-stile.md', genera_manuale(b, libro, profilo, n_cap))
    comune.scrivi(cartella, '03-architettura/scaletta.md',
                  genera_scaletta(libro, n_cap, libro['dichiarazioni']['chiusura']['sigle'][0]))
    comune.scrivi(cartella, '03-architettura/piano-parole.md', genera_piano(libro, n_cap))
    decisioni = '\n'.join(f'- {f}' for f in b['fatti'] + b['non_cambiare']) or '- nessuna'
    leggimi = open(os.path.join(m, 'LEGGIMI.md'), encoding='utf-8').read().format(
        titolo=libro['titolo'], percorso=cartella, modalita=libro['modalita'], fase='documenti',
        gate='nessuno', ultimo='—', decisioni=decisioni)
    comune.scrivi(cartella, 'LEGGIMI.md', leggimi)
    comune.carica_libro(cartella)          # libro.yaml generato valido (schema, override con motivo)
    errori = comune.controlla_struttura(cartella, libro['modalita'])
    if errori:
        raise comune.ErroreMotore('Struttura del libro non conforme a dati/struttura-libro.yaml:\n- ' + '\n- '.join(errori))
    if rad:
        hook_recinto.imposta_libro_attivo(rad, os.path.basename(cartella))
    return cartella, n_cap


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: nuovo.py <percorso-briefing>')
    cartella, n_cap = crea(args[0])
    print(f'libro creato in {cartella} ({n_cap} capitoli previsti); fase «documenti».')
    print('Prossimo passo: completare bibbia, cronologia, scaletta e piano parole; poi «zb pronto <libro>»,'
          ' che apre il gate «documenti».')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/ortografia.py`

```python
"""Controllo ortografico del manoscritto (passo 7). Tre livelli.

Uso: python3 -B ortografia.py <libro> [--schermo]
(a) Hunspell it_IT, sempre: parole non riconosciute, escluse le parole ammesse del libro
    (libro.yaml ortografia.parole_ammesse_file, di solito nomi_propri.txt) e quelle generiche del
    motore (dati/parole-ammesse-it.txt). Le elisioni (l', dell', anch'…) non si controllano.
(b) LanguageTool, solo se ZB_LANGUAGETOOL indica la cartella dei suoi .jar (scaricati fuori dal
    repository; come, in PROCEDURA.md). Mai scaricato da questo script.
(c) Checklist manuale per la lettura umana, sempre, in fondo al report.
Report: <libro>/06-diagnostica/controllo-ortografico.md (con --schermo solo a schermo).
Il report dice quali livelli sono stati eseguiti. Codice 1 se (a) o (b) trovano qualcosa;
2 se Hunspell o il dizionario it_IT mancano.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

PAROLA = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:['’][A-Za-zÀ-ÖØ-öø-ÿ]+)*['’]?")
ENV = dict(os.environ, LC_ALL='C.UTF-8')
CHECKLIST = [
    '«e» congiunzione al posto di «è» verbo (e viceversa)',
    'accordi di genere e numero (soggetto e verbo, nome e aggettivo)',
    'apostrofi: «qual è», «un amico» / «un\'amica», «po\'»',
    'accenti: «perché», «poiché», «né», «sé», «lì», «là», «dà»',
    'parole vere al posto sbagliato (per esempio «anno» per «hanno», «a» per «ha»)',
    'concordanza dei tempi verbali nella stessa scena',
    'virgolette e lineette dei dialoghi coerenti in tutto il libro',
    'maiuscole dopo i due punti e nei titoli dei capitoli',
]


def ammesse(cartella, libro):
    out = set()
    nome = ((libro.get('ortografia') or {}).get('parole_ammesse_file')) or 'nomi_propri.txt'
    for p in (os.path.join(cartella, nome), os.path.join(comune.radice_motore(), 'dati', 'parole-ammesse-it.txt')):
        if os.path.isfile(p):
            out |= {r.strip() for r in open(p, encoding='utf-8') if r.strip() and not r.startswith('#')}
    return out


def parole_della_riga(riga):
    """Parole da controllare: senza la parte elisa prima dell'apostrofo, senza cifre."""
    for t in PAROLA.findall(riga):
        parti = re.split(r"['’]", t)
        for i, x in enumerate(parti):
            if x and i == len(parti) - 1:
                yield x


def hunspell(parole):
    if not shutil.which('hunspell'):
        return None, 'hunspell non installato'
    r = subprocess.run(['hunspell', '-D'], capture_output=True, text=True, env=ENV, input='')
    if 'it_IT' not in r.stdout + r.stderr:
        return None, 'dizionario it_IT non trovato'
    r = subprocess.run(['hunspell', '-l', '-i', 'UTF-8', '-d', 'it_IT'], input='\n'.join(sorted(parole)),
                       capture_output=True, text=True, env=ENV)
    return set(r.stdout.split()), None


def languagetool(testi):
    """[(unita, riga, regola, messaggio, testo)] oppure (None, motivo)."""
    d = os.environ.get('ZB_LANGUAGETOOL')
    if not d:
        return None, 'variabile ZB_LANGUAGETOOL non impostata'
    if not glob.glob(os.path.join(d, '*.jar')):
        return None, f'nessun .jar in {d}'
    if not shutil.which('java'):
        return None, 'java non installato'
    out = []
    with tempfile.TemporaryDirectory(prefix='zb-lt-') as tmp:
        for nome, testo, prosa in testi:
            f = os.path.join(tmp, 'unita.txt')
            open(f, 'w', encoding='utf-8').write(testo)
            r = subprocess.run(['java', '-cp', os.path.join(d, '*'), 'org.languagetool.commandline.Main',
                                '-l', 'it', '--json', f], capture_output=True, text=True, env=ENV, timeout=600)
            try:
                dati = json.loads(r.stdout[r.stdout.index('{'):])
            except ValueError:
                return None, f'LanguageTool non eseguito: {(r.stderr or r.stdout).strip()[:200]}'
            for m in dati.get('matches', []):
                riga = testo[:m['offset']].count('\n') + 1
                if riga in prosa:
                    frammento = testo[m['offset']:m['offset'] + m['length']]
                    out.append((nome, riga, m['rule']['id'], m['message'], frammento))
    return out, None


def controlla(cartella, libro):
    am = ammesse(cartella, libro)
    am_min = {x.lower() for x in am}
    posizioni, testi = {}, []
    for nome, p in comune.unita(cartella, libro):
        testo = open(p, encoding='utf-8').read()
        prosa = {}
        for n, riga in comune.righe_prosa(testo):
            prosa[n] = riga
            for w in parole_della_riga(riga):
                posizioni.setdefault(w, []).append(f'{os.path.relpath(p, cartella)}:{n}')
        testi.append((os.path.relpath(p, cartella), testo, prosa))
    sconosciute, errore_h = hunspell(set(posizioni))
    trovate = {}
    if sconosciute is not None:
        trovate = {w: posizioni[w] for w in sorted(sconosciute)
                   if w in posizioni and w not in am and w.lower() not in am_min}
    lt, motivo_lt = languagetool(testi)
    if lt is not None:
        lt = [x for x in lt if not (x[2].startswith('MORFOLOGIK') and (x[4] in am or x[4].lower() in am_min))]
    return trovate, errore_h, lt, motivo_lt


def report(libro, trovate, errore_h, lt, motivo_lt):
    r = [f'# Controllo ortografico — {libro["titolo"]}', '', '## Livelli eseguiti', '',
         '| Livello | Eseguito | Note |', '|---|---|---|',
         f'| (a) Hunspell it_IT | {"no" if errore_h else "sì"} | {errore_h or "parole ammesse: libro + dati/parole-ammesse-it.txt"} |',
         f'| (b) LanguageTool | {"no" if lt is None else "sì"} | {motivo_lt or "regole italiane, solo righe di prosa"} |',
         '| (c) Checklist manuale | sì | in fondo al report, per la lettura umana |', '']
    if not errore_h:
        r += ['## (a) Parole non riconosciute da Hunspell', '',
              f'{len(trovate)} parole. Ogni voce va verificata: un refuso, oppure una parola da aggiungere '
              'alle parole ammesse del libro.', '']
        if trovate:
            r += ['| Parola | Occorrenze | Posizioni (file:riga) |', '|---|---|---|']
            r += [f'| {w} | {len(p)} | {", ".join(p[:10])}{" …" if len(p) > 10 else ""} |' for w, p in trovate.items()]
        r.append('')
    if lt is not None:
        r += ['## (b) Segnalazioni di LanguageTool', '', f'{len(lt)} segnalazioni.', '']
        if lt:
            r += ['| File:riga | Regola | Testo | Messaggio |', '|---|---|---|---|']
            r += [f'| {f}:{n} | {reg} | {t} | {msg} |' for f, n, reg, msg, t in lt]
        r.append('')
    r += ['## (c) Checklist per la lettura umana', '',
          'I correttori automatici non rilevano errori come «e» al posto di «è», gli accordi sbagliati '
          'o una parola vera usata al posto di un\'altra. Questi controlli li fa chi legge.', '',
          '| Controllo | Fatto |', '|---|---|']
    r += [f'| {c} | [ ] |' for c in CHECKLIST]
    return '\n'.join(r) + '\n'


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: ortografia.py <libro> [--schermo]')
    cartella, libro, _ = comune.carica_libro(args[0])
    trovate, errore_h, lt, motivo_lt = controlla(cartella, libro)
    testo = report(libro, trovate, errore_h, lt, motivo_lt)
    if '--schermo' in argv:
        print(testo)
    else:
        print('scritto', comune.scrivi(cartella, '06-diagnostica/controllo-ortografico.md', testo))
    print(f'Hunspell: {"non eseguito (" + errore_h + ")" if errore_h else f"{len(trovate)} parole da verificare"}; '
          f'LanguageTool: {"saltato (" + motivo_lt + ")" if lt is None else f"{len(lt)} segnalazioni"}')
    if errore_h:
        return 2
    return 1 if trovate or lt else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/pacchetto.py`

```python
"""Pacchetto di pubblicazione: struttura di <libro>/06-pubblicazione/ (proposta A.5, A.6, A.9, B.4).

Uso: python3 -B pacchetto.py <libro>
Crea, se mancano, i modelli compilati con i dati di libro.yaml: scheda-amazon.md,
quarta.md, brief-copertina.md, conferme-autore.yaml, promemoria-ai.md, checklist.md.
NON scrive testi commerciali: descrizione, quarta di copertina, parole chiave e categorie
li scrive Claude Code nella fase di pubblicazione del libro, e poi passano da
conformita_kdp.py. Un file già presente non viene mai sovrascritto.
"""
import os
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

NOTA = ('<!-- Compilato dal motore con i dati di libro.yaml. Le parti vuote le scrive Claude Code '
        'nella fase di pubblicazione; poi passano da conformita_kdp.py. -->')


def modelli(libro, cartella):
    t, a = libro['titolo'], libro['autore']
    st = libro.get('sottotitolo') or ''
    serie = libro.get('serie') or {}
    k = comune.kdp()
    pagine = '—'
    pdf = os.path.join(cartella, '05-output', f'{comune.nome_file(t)}.pdf')
    if os.path.isfile(pdf):
        import pymupdf
        with pymupdf.open(pdf) as d:
            pagine = str(d.page_count)
    f = libro['formato']
    anno = libro['copyright'].get('anno', '{anno}')
    out = {}
    out['scheda-amazon.md'] = '\n'.join([
        f'# Scheda Amazon — {t}', '', NOTA, '',
        f'Titolo: {t}', f'Sottotitolo: {st}',
        f'Serie: {serie.get("nome", "")} | {serie.get("numero", "")}' if serie else 'Serie:',
        f'Autore: {a}', 'Editore:', '',
        '## Descrizione', '',
        f'<!-- Massimo {k["metadati"]["descrizione_max_caratteri"]} caratteri. Tag HTML ammessi: '
        f'{" ".join(k["metadati"]["html_ammesso_descrizione"]["tag"])}. Niente link, prezzi, recensioni, '
        'parole chiave, paragoni («per i fan di…»), spoiler. -->', '',
        '## Parole chiave', '',
        f'<!-- Al massimo {k["metadati"]["parole_chiave_max"]}, frasi di 2-3 parole. -->', ''] +
        [f'{i}.' for i in range(1, k['metadati']['parole_chiave_max'] + 1)] +
        ['', '## Categorie', '', f'<!-- Al massimo {k["metadati"]["categorie_max"]}. -->', ''] +
        [f'{i}.' for i in range(1, k['metadati']['categorie_max'] + 1)] + [''])
    out['quarta.md'] = '\n'.join([
        f'# Quarta di copertina — {t}', '', NOTA, '',
        '<!-- 120-180 parole: frase gancio, premessa, posta in gioco, domanda finale (08-pubblicazione r. 23). '
        'Citazioni solo da recensioni reali e autorizzate. -->', '',
        '## Testo', '', '', '## Biografia dell\'autore (2 righe)', '', ''])
    out['brief-copertina.md'] = '\n'.join([
        f'# Brief per la copertina — {t}', '', NOTA, '',
        '| Dato | Valore |', '|---|---|',
        f'| Titolo | {t} |', f'| Sottotitolo | {st or "—"} |', f'| Autore | {a} |',
        f'| Serie | {serie.get("nome", "—")} {serie.get("numero", "")} |',
        f'| Formato | {f["pagina_pollici"][0]} × {f["pagina_pollici"][1]} pollici |',
        f'| Carta | {f.get("carta", "—")} |', f'| Pagine del PDF | {pagine} |', '',
        '- Dimensioni del file: SEMPRE dal calcolatore o dal modello ufficiale KDP (dipendono da formato, pagine e carta).',
        f'- Bleed obbligatorio per il cartaceo ({k["cartaceo"]["bleed_pollici"]}").',
        '- Lasciare libero il riquadro del codice a barre sulla quarta, secondo il modello KDP: '
        'con l\'ISBN gratuito KDP il codice lo mette KDP.',
        '- Titolo, sottotitolo, autore e serie identici ai metadati; nessuna imitazione di copertine esistenti.', '',
        '## Concept (3 alternative)', '', '1.', '2.', '3.', ''])
    out['promemoria-ai.md'] = '\n'.join([f'# Dichiarazione AI — {t}', '', k['dichiarazione_ai']['promemoria'], ''])
    out['checklist.md'] = '\n'.join([
        f'# Checklist prima dell\'upload — {t}', '', '(08-pubblicazione rr. 40-49)', '',
        '- [ ] Tutte le passate di revisione completate',
        '- [ ] Nessun avviso di continuità aperto',
        '- [ ] Registro promesse: tutte ripagate',
        '- [ ] Sommario generato e verificato (verifica_pdf.py)',
        '- [ ] Pagine iniziali e finali complete',
        f'- [ ] Nome autore identico su copertina, frontespizio e scheda: «{a}»',
        '- [ ] Totale parole nel range previsto dal piano (conta.py)',
        '- [ ] Dichiarazione AI preparata (promemoria-ai.md)',
        '- [ ] Controllo di conformità KDP senza KO (conformita_kdp.py)',
        f'- [ ] © {anno} {a}: pagina di copyright presente', ''])
    return out


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: pacchetto.py <libro>')
    cartella, libro, _ = comune.carica_libro(args[0])
    for nome, testo in modelli(libro, cartella).items():
        rel = f'06-pubblicazione/{nome}'
        if os.path.exists(os.path.join(cartella, rel)):
            print(f'già presente, non toccato: {rel}')
            continue
        comune.scrivi(cartella, rel, testo)
        print(f'creato: {rel}')
    rel = '06-pubblicazione/conferme-autore.yaml'
    if os.path.exists(os.path.join(cartella, rel)):
        print(f'già presente, non toccato: {rel}')
    else:
        shutil.copyfile(os.path.join(comune.radice_motore(), 'modelli', 'conferme-autore.yaml'),
                        comune.percorso_in_libro(cartella, rel))
        print(f'creato: {rel}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```


Continua in [parte 5](ESPORTAZIONE_COMPLETA_5.md).

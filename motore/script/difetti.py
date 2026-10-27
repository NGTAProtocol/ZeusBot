"""Sistema «difetto → test» (comando «zb difetti», 2026-10-27). Procedura: motore/editoriale/difetti.md.

Ogni difetto trovato in un capitolo diventa un test permanente: si registra (06-diagnostica/difetti/registro.yaml
del libro, con la classe di motore/dati/difetti.yaml e le fixture sbagliata e corretta), si scrive il controllo con
un criterio generale, e il cancello di «zb esito» rifiuta il capitolo finché un difetto bloccante non è superato.
Tre esiti per classe: passato, fallito, non verificabile; «non verificabile» non vale mai come passato. Scorciatoia
solo con un motivo scritto (registro, voce «eccezioni»).

Tre rilevamenti: deterministico (questo script), revisore (sezione «## Registro dei difetti» del rapporto
audit/NN.md del diagnosta: meno affidabile), fonte (fatti controllabili in 06-diagnostica/difetti/fatti.yaml,
bloccanti finché non sono verificati o riscritti in forma generica).

Uso:
  zb difetti <libro> [N]                      cancello su un capitolo (o su tutti): passato / fallito / non verificabile
  zb difetti <libro> prova                    ogni difetto del registro: il test fallisce sulla fixture sbagliata
                                              e passa sulla corretta
  zb difetti <libro> continuita               registro di continuità (06-diagnostica/difetti/continuita.md)
  zb difetti <libro> fatto <id> verificato|generico|errato [--fonte <url>] [--nota <testo>]
"""
import datetime
import glob
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

CARTELLA = os.path.join('06-diagnostica', 'difetti')
REGISTRO = os.path.join(CARTELLA, 'registro.yaml')
FATTI = os.path.join(CARTELLA, 'fatti.yaml')
CONTINUITA = os.path.join(CARTELLA, 'continuita.md')
TIPI = ('capitolo', 'prologo', 'epilogo', 'interludio', 'flash-forward', 'flashback')
IN_SEQUENZA = ('capitolo', 'interludio')
SEZIONE_REVISORE = '## Registro dei difetti'
REVISORE = ('conoscenza_personaggio', 'inferenza_come_fatto', 'motivazione')


# ---------------------------------------------------------------- dati e contesto

def dati():
    return comune.leggi_yaml(os.path.join(comune.radice_motore(), 'dati', 'difetti.yaml'))


def parametri(libro):
    p = {k: v['valore'] for k, v in dati()['parametri'].items()}
    p.update(((libro or {}).get('difetti') or {}).get('parametri') or {})
    return p


def leggi(cartella, rel, vuoto):
    p = os.path.join(cartella, rel)
    return (comune.leggi_yaml(p) or vuoto) if os.path.isfile(p) else vuoto


def anno_di(cartella):
    """Anno della storia dalla cronologia (le intestazioni di solito non lo scrivono)."""
    for e in (leggi(cartella, 'cronologia.yaml', {}) or {}).get('eventi') or []:
        m = re.match(r'(\d{4})-', str(e.get('data') or ''))
        if m:
            return int(m.group(1))
    return 2001


def dichiarazioni(testo):
    """Tutte le righe nascoste <!-- zb: campo=valore --> del capitolo, unite."""
    out = {}
    for blocco in re.findall(r'<!--\s*zb:(.*?)-->', testo, re.S):
        out.update(re.findall(r'(\w+)=([^\s()]+)', blocco))
    return out


def numero(tok):
    import continuita
    return continuita.numero(tok)


def mesi():
    return [m.lower() for m in comune.lingue()['it']['mesi']]


INTEST = re.compile(r'^(?P<luogo>[^—\n]{2,80}?)\s+—\s+(?:\w+\s+)?(?P<g>\d{1,2})\s+(?P<m>[a-zà-ù]+)(?:\s+(?P<a>\d{4}))?$')
DOPO = re.compile(r"(?i)^(?:la mattina|il giorno|la sera|la notte|il pomeriggio) dopo\b|^l'indomani\b")
SEPARATORE = re.compile(r'^\s*(\*\s*){3}\s*$')


def scene(testo, anno):
    """[(riga d'inizio, data o None, luogo o None)]: intestazione «Luogo — 21 ottobre» in testa a ogni scena; una
    scena senza intestazione eredita la data, +1 giorno se comincia con «La mattina dopo», «L'indomani»…"""
    out, cur, nuova = [], None, True
    for n, r in enumerate(testo.splitlines(), 1):
        if SEPARATORE.match(r):
            nuova = True
            continue
        s = r.strip().strip('*').strip()
        if not s or s.startswith(('#', '<!--')) or not nuova:
            continue
        nuova = False
        m = INTEST.match(s)
        if m and m.group('m').lower() in mesi():
            try:
                cur = datetime.date(int(m.group('a') or anno), mesi().index(m.group('m').lower()) + 1, int(m.group('g')))
            except ValueError:
                cur = None
            out.append((n, cur, m.group('luogo').strip()))
            continue
        k = re.match(r'(?i)^(\w+) giorni dopo\b', s)
        if cur and k and numero(k.group(1)):
            cur = cur + datetime.timedelta(days=numero(k.group(1)))
        elif cur and DOPO.match(s):
            cur = cur + datetime.timedelta(days=1)
        out.append((n, cur, None))
    return out


def data_riga(sc, n):
    d = None
    for inizio, data, _ in sc:
        if inizio <= n:
            d = data
    return d


def prosa(testo):
    """[(n, riga)] di prosa: niente titoli, commenti, separatori, intestazioni di scena."""
    out = []
    for n, r in comune.righe_prosa(testo):
        if INTEST.match(r.strip().strip('*').strip()):
            continue
        out.append((n, r))
    return out


def paragrafi(testo):
    """[(riga del primo rigo, testo del paragrafo)] di prosa."""
    out, cur, inizio = [], [], None
    righe = dict(prosa(testo))
    for n, r in enumerate(testo.splitlines(), 1):
        if n in righe and r.strip():
            inizio = inizio or n
            cur.append(r.strip())
        elif cur:
            out.append((inizio, ' '.join(cur)))
            cur, inizio = [], None
    if cur:
        out.append((inizio, ' '.join(cur)))
    return out


def dialogo(r):
    return r.lstrip().startswith(('«', '—', '"', '“'))


def ko(classe, unita, riga, dettaglio):
    return {'classe': classe, 'unita': str(unita), 'riga': riga, 'dettaglio': dettaglio}


# ---------------------------------------------------------------- controlli deterministici (ctx: cartella, libro, p)

REL = re.compile(r"(?i)\b(?:(da|fino a)\s+)?(\w+)\s+giorn[oi](?:\s+(fa|prima))?\b")


def c_giorni_relativi(unita, ctx):
    anno, p, voci = ctx['anno'], ctx['p'], []
    for i, (nome, testo) in enumerate(unita):
        sc = scene(testo, anno)
        for n, r in prosa(testo):
            for m in REL.finditer(r):
                k = numero(m.group(2))
                d = data_riga(sc, n)
                if not k or not d or not (m.group(1) == 'da' or m.group(3)):
                    continue                     # «tre giorni» senza «da», «fa» o «prima» non è un riferimento
                voci.append((i, nome, n, m.group(0).strip(), d, d - datetime.timedelta(days=k)))
    out = []
    for a in voci:
        for b in voci:
            if b[0] < a[0] or (b[0] == a[0] and b[2] < a[2]):
                scarto = abs((a[5] - b[5]).days)
                if a[0] - b[0] < p['finestra_capitoli'] and scarto in p['giorni_scarto_sospetto']:
                    out.append(ko('giorni_relativi', a[1], a[2],
                                  f'«{a[3]}» il {a[4]:%d/%m} dà il {a[5]:%d/%m}; «{b[3]}» (unità {b[1]}, r.{b[2]}, il '
                                  f'{b[4]:%d/%m}) dà il {b[5]:%d/%m}: scarto di {scarto} giorno/i per lo stesso fatto?'))
    return out


def c_ordine_tipo(unita, ctx):
    out, massimo = [], None
    for nome, testo in unita:
        tipo = dichiarazioni(testo).get('tipo', 'capitolo')
        sc = scene(testo, ctx['anno'])
        d = sc[0][1] if sc else None
        if tipo not in TIPI:
            out.append(ko('ordine_tipo', nome, None, f'tipo «{tipo}» sconosciuto ({", ".join(TIPI)})'))
        if not d:
            out.append(ko('ordine_tipo', nome, sc[0][0] if sc else None,
                          'intestazione senza data («Luogo — 21 ottobre» sotto il titolo)'))
            continue
        if tipo not in IN_SEQUENZA:
            continue
        if massimo and d < massimo[1]:
            out.append(ko('ordine_tipo', nome, sc[0][0],
                          f'data {d:%d/%m} anteriore all\'unità {massimo[0]} ({massimo[1]:%d/%m}): dichiara il tipo '
                          'dell\'unità fuori sequenza (<!-- zb: tipo=flash-forward|flashback|prologo -->)'))
        if not massimo or d > massimo[1]:
            massimo = (nome, d)
    return out


ODORI = re.compile(r"(?i)\b(?:sa|sanno|odora|odorano|puzza|profuma)\s+di\b[^.]*?(?:,|\be)\s*(?:e\s+)?"
                   r"(?:di|del|della|dello|dei|delle|degli)\b")


def c_apertura_ripetuta(unita, ctx):
    out, prima = [], None
    for nome, testo in unita:
        apertura = ' '.join(t for _, t in paragrafi(testo)[:2])
        m = ODORI.search(apertura)
        if m and prima:
            riga = paragrafi(testo)[0][0]
            out.append(ko('apertura_ripetuta', nome, riga,
                          f'«{m.group(0)[:40]}…» in apertura come nell\'unità {prima}: elenco di odori in capitoli '
                          'consecutivi'))
        prima = nome if m else None
    return out


def frasi_brevi(testo, massimo):
    out = []
    for n, r in prosa(testo):
        if dialogo(r):
            continue
        for f in re.split(r'(?<=[.!?:…])\s+', r):
            parole = re.findall(r"[\wà-ù']+", f.lower())
            if 1 <= len(parole) <= massimo:
                out.append((n, ' '.join(parole)))
    return out


def c_frase_firma(unita, ctx):
    p, out = ctx['p'], []
    viste = []
    for i, (nome, testo) in enumerate(unita):
        brevi = frasi_brevi(testo, p['frase_firma_parole_max'])
        recenti = {f: nm for nm, insieme in viste[-(p['finestra_capitoli'] - 1):] for f in insieme} \
            if p['finestra_capitoli'] > 1 else {}
        segnalate = set()
        for n, f in brevi:
            if f in recenti and f not in segnalate:
                segnalate.add(f)
                out.append(ko('frase_firma', nome, n, f'«{f}» identica nell\'unità {recenti[f]}'))
        viste.append((nome, {f for _, f in brevi}))
    firma = ((ctx['libro'] or {}).get('difetti') or {}).get('parole_firma') or []
    for termine in firma:
        rx = re.compile(r'(?i)\b' + termine)
        conti = [[n for n, r in prosa(t) if rx.search(r)] for _, t in unita]
        for i, (nome, _) in enumerate(unita):
            finestra = conti[max(0, i - p['finestra_capitoli'] + 1):i + 1]
            if conti[i] and sum(len(c) for c in finestra) > p['parole_firma_max_finestra']:
                out.append(ko('frase_firma', nome, conti[i][0],
                              f'parola-firma «{termine}»: {sum(len(c) for c in finestra)} volte in '
                              f'{len(finestra)} capitoli (massimo {p["parole_firma_max_finestra"]})'))
    return out


def c_chiusure_uguali(unita, ctx):
    out, serie, prima = [], 0, None
    for nome, testo in unita:
        s = dichiarazioni(testo).get('chiusura')
        serie = serie + 1 if s and s == prima else (1 if s else 0)
        prima = s
        if serie > ctx['p']['chiusure_max_consecutive']:
            out.append(ko('chiusure_uguali', nome, None, f'{serie} capitoli di fila con chiusura {s} (massimo '
                                                        f'{ctx["p"]["chiusure_max_consecutive"]})'))
    return out


def budget(cartella):
    out = {}
    for r in comune.tabella_md(os.path.join(cartella, comune.rel_piano(cartella))) if os.path.isfile(
            os.path.join(cartella, comune.rel_piano(cartella))) else []:
        b = re.sub(r'[^\d]', '', r.get('Budget capitolo', ''))
        if (r.get('Cap.') or '').strip().isdigit() and b:
            out[r['Cap.'].strip()] = int(b)
    return out


def c_lunghezza(unita, ctx):
    import conta
    out, bud = [], budget(ctx['cartella'])
    tol = (comune.carica_profilo(ctx['libro'].get('genere')) or {}).get('capitoli', {}).get('tolleranza_budget', 0.15) \
        if ctx['libro'].get('genere') else 0.15
    massimo = ((ctx['libro'].get('capitoli') or {}) if isinstance(ctx['libro'].get('capitoli'), dict) else {}).get('massimo')
    for nome, testo in unita:
        parole = conta.conta_testo(testo)
        b = bud.get(str(nome))
        if b and parole > b * (1 + tol):
            out.append(ko('lunghezza', nome, None, f'{parole} parole: budget {b} più il {tol:.0%}'))
        if massimo and parole > massimo:
            out.append(ko('lunghezza', nome, None, f'{parole} parole: massimo del libro {massimo}'))
    return out


def pattern_cliche(cartella, libro):
    base = comune.leggi_yaml(os.path.join(comune.radice_motore(), 'dati', 'lista-nera.yaml')) or {}
    voci = [(v['id'], v['pattern']) for v in base.get('voci') or [] if v.get('modalita') == 'vieta']
    voci += [(v.get('id', 'libro'), v['pattern']) for v in (libro.get('voci') or []) if isinstance(v, dict)
             and v.get('pattern') and v.get('modalita', 'vieta') == 'vieta']
    voci += [(f, r'(?i)\b' + re.escape(f) + r'\b') for f in ((libro.get('difetti') or {}).get('cliche') or [])]
    return [(i, re.compile(p)) for i, p in voci]


def c_cliche(unita, ctx):
    out = []
    pats = pattern_cliche(ctx['cartella'], ctx['libro'])
    for nome, testo in unita:
        for n, r in prosa(testo):
            for i, rx in pats:
                m = rx.search(r)
                if m:
                    out.append(ko('cliche', nome, n, f'«{m.group(0)}» ({i})'))
    return out


def c_copia_capitoli(unita, ctx):
    import riciclo
    out, gia = [], set()
    canoniche = riciclo.battute_canoniche(ctx['cartella'])
    for nome, testo in unita:
        tok = riciclo.maschera(riciclo.gettoni(testo), canoniche)
        for riga, t in riciclo.segmenti(tok, gia):
            out.append(ko('copia_capitoli', nome, riga, f'«{t}» uguale a un capitolo precedente'))
        gia |= riciclo.ngrammi(tok)
    return out


def c_similitudini(unita, ctx):
    import conta
    import stile
    p, out = ctx['p'], []
    for nome, testo in unita:
        tot = 0
        for n, par in paragrafi(testo):
            trovate = [m.group(0) for m in stile.SIMILITUDINE.finditer(par)]
            tot += len(trovate)
            if len(trovate) > p['similitudini_max_paragrafo']:
                out.append(ko('similitudini', nome, n, f'{len(trovate)} similitudini nel paragrafo ('
                                                        + ', '.join(f'«{t}»' for t in trovate) + ')'))
        tetto = max(1, conta.conta_testo(testo) / p['similitudini_parole_per_una'])
        if tot > tetto:
            out.append(ko('similitudini', nome, None, f'{tot} similitudini nel capitolo, tetto {tetto:.1f} '
                                                     f'(una ogni {p["similitudini_parole_per_una"]} parole)'))
    return out


CONTA = re.compile(r"(?i)(?<!\bil )(?<!\bun )(?<!\bdel )(?<!\bal )(?<!\bnel )(?<!\bsul )\b(?:li |le |lo |la |ne )?"
                   r"cont(?:o|ato|ati|ate|are|ando)\b")


def c_tratto_ricorrente(unita, ctx):
    out, serie = [], 0
    for nome, testo in unita:
        righe = [n for n, r in prosa(testo) if CONTA.search(r)]
        serie = serie + 1 if righe else 0
        if serie >= ctx['p']['tratto_capitoli_consecutivi']:
            out.append(ko('tratto_ricorrente', nome, righe[0], f'la narratrice conta (r. {", ".join(map(str, righe))}): '
                                                               f'{serie} capitoli di fila'))
    return out


def personaggi(cartella):
    """{id: (nomi, testo della scheda)} dal codex (@char:)."""
    out = {}
    for f in glob.glob(os.path.join(cartella, '02-bibbia', 'codex', '*.md')):
        t = open(f, encoding='utf-8').read()
        m = re.search(r'@char:([\w\-]+)', t)
        if not m:
            continue
        nomi = [re.sub(r'^#\s*', '', t.splitlines()[0]).strip()]
        a = re.search(r'(?im)^-\s*Alias:\s*(.+)$', t)
        if a:
            nomi += [x.strip() for x in a.group(1).split(',')]
        parti = {w for n in nomi for w in re.findall(r"[A-ZÀ-Ý][\wà-ù']{3,}", n)
                 if w.lower() not in ('il', 'la', 'professore', 'direttore', 'vicedirettore', 'assistente')}
        out[m.group(1)] = (parti, t.lower())
    return out


def c_etichetta_ruolo(unita, ctx):
    out, pg = [], personaggi(ctx['cartella'])
    for nome, testo in unita:
        for n, r in prosa(testo):
            for f in re.split(r'(?<=[.!?…])\s+', r):
                chi = [k for k, (nomi, _) in pg.items() if any(re.search(r'\b' + re.escape(x) + r'\b', f) for x in nomi)]
                if len(chi) != 1:
                    continue
                nomi = '|'.join(re.escape(x) for x in pg[chi[0]][0])
                for e in ctx['p']['etichette_ruolo']:
                    # l'etichetta deve riferirsi al personaggio: apposizione o predicato vicino al nome
                    m = re.search(r"(?i)\b(?:" + nomi + r")\b,?\s+(?:è\s+|era\s+)?(?:(?:un|una|uno|la|il|lo|l')\s*)?(" + e
                                  + r"\w*)|\b(" + e + r"\w*)\s+(?:[A-ZÀ-Ý][\wà-ù']+\s+)?(?:" + nomi + r")\b", f)
                    if m and e not in pg[chi[0]][1]:
                        out.append(ko('etichetta_ruolo', nome, n, f'«{m.group(0).strip()}»: {chi[0]} nel codex '
                                                                  'non ha questo ruolo'))  # noqa: E127
    return out


DETERMINISTICI = {'giorni_relativi': c_giorni_relativi, 'ordine_tipo': c_ordine_tipo,
                  'apertura_ripetuta': c_apertura_ripetuta, 'frase_firma': c_frase_firma,
                  'chiusure_uguali': c_chiusure_uguali, 'lunghezza': c_lunghezza, 'cliche': c_cliche,
                  'copia_capitoli': c_copia_capitoli, 'similitudini': c_similitudini,
                  'tratto_ricorrente': c_tratto_ricorrente, 'etichetta_ruolo': c_etichetta_ruolo}


# ---------------------------------------------------------------- revisore e fonte

def sezione_revisore(cartella, n):
    """{classe: (esito, dettaglio)} dalla sezione «## Registro dei difetti» di audit/NN.md (None se assente).
    Righe: «- conoscenza_personaggio: OK» oppure «- inferenza_come_fatto: KO r.35 «…»: motivo»."""
    import percorso
    p = os.path.join(cartella, percorso.rel_audit(n))
    if not os.path.isfile(p):
        return None
    t = open(p, encoding='utf-8').read()
    if SEZIONE_REVISORE not in t:
        return None
    blocco = t.split(SEZIONE_REVISORE, 1)[1].split('\n## ', 1)[0]
    out = {}
    for m in re.finditer(r'(?m)^-\s*(\w+):\s*(OK|KO)\b\s*(.*)$', blocco):
        out[m.group(1)] = (m.group(2), m.group(3).strip())
    return out


def fatti(cartella):
    return leggi(cartella, FATTI, {'fatti': []}).get('fatti') or []


def esiti_unita(cartella, libro, n, unita=None):
    """[(classe, gravità, esito, [dettagli])] del capitolo N: passato | fallito | non verificabile | accettato."""
    classi = dati()['classi']
    unita = unita if unita is not None else carica(cartella, libro)
    fino = [u for u in unita if not str(u[0]).isdigit() or not str(n).isdigit() or int(u[0]) <= int(n)]
    ctx = {'cartella': cartella, 'libro': libro, 'p': parametri(libro), 'anno': anno_di(cartella)}
    eccezioni = {(str(e.get('unita')), e.get('classe')): e.get('motivo')
                 for e in leggi(cartella, REGISTRO, {}).get('eccezioni') or [] if e.get('motivo')}
    out = []
    for classe, d in classi.items():
        if d['rilevamento'] == 'deterministico':
            trovati = [f'r.{k["riga"]}: {k["dettaglio"]}' if k['riga'] else k['dettaglio']
                       for k in DETERMINISTICI[classe](fino, ctx) if k['unita'] == str(n)]
            esito = 'fallito' if trovati else 'passato'
        elif d['rilevamento'] == 'revisore':
            sez = sezione_revisore(cartella, n)
            voce = (sez or {}).get(classe)
            if voce is None:
                esito, trovati = 'non verificabile', ['manca nel rapporto del diagnosta (sezione «Registro dei difetti»)']
            else:
                esito, trovati = ('fallito', [voce[1]]) if voce[0] == 'KO' else ('passato', [])
        else:
            aperti = [f'{f["id"]}: {f.get("affermazione", "")} ({f.get("stato")})' for f in fatti(cartella)
                      if str(f.get('unita')) == str(n) and f.get('stato') not in ('verificato', 'generico')]
            esito, trovati = ('non verificabile', aperti) if aperti else ('passato', [])
        if esito != 'passato' and (str(n), classe) in eccezioni:
            esito, trovati = 'accettato', [f'motivo: {eccezioni[(str(n), classe)]}'] + trovati
        out.append((classe, d['gravita'], esito, trovati))
    return out


def blocchi(esiti):
    return [e for e in esiti if e[1] == 'bloccante' and e[2] in ('fallito', 'non verificabile')]


def cancello(cartella, libro, n):
    """Per «zb esito»: ErroreMotore se un difetto bloccante è fallito o non verificabile."""
    b = blocchi(esiti_unita(cartella, libro, n))
    if b:
        raise comune.ErroreMotore(f'Cancello dei difetti, capitolo {n}: non approvato.\n' + '\n'.join(
            f'- {c} ({e}): ' + '; '.join(d[:3]) for c, _, e, d in b)
            + '\nCorreggi, oppure registra un\'eccezione con il motivo in ' + REGISTRO + ' (procedura: '
            'motore/editoriale/difetti.md).')


# ---------------------------------------------------------------- unità, fixture, prova

def carica(cartella, libro):
    return [(nome, open(p, encoding='utf-8').read()) for nome, p in comune.unita(cartella, libro)]


def da_cartella(cartella_fix):
    """Unità da una cartella di fixture: file .md, nome = numero iniziale del file (o il nome del file)."""
    out = []
    for f in sorted(glob.glob(os.path.join(cartella_fix, '*.md'))):
        b = os.path.basename(f)
        m = re.match(r'(\d+)', b)
        out.append((str(int(m.group(1))) if m else b[:-3], open(f, encoding='utf-8').read()))
    return out


def prova_voce(cartella, libro, voce):
    """(esito sulla fixture sbagliata, esito sulla corretta) per una voce del registro: 'fallito'/'passato'."""
    classe = voce['classe']
    d = dati()['classi'][classe]
    if d['rilevamento'] != 'deterministico':
        return 'non deterministico', 'non deterministico'
    ctx = {'cartella': cartella, 'libro': libro, 'p': parametri(libro), 'anno': anno_di(cartella)}
    res = []
    for chiave in ('fixture_sbagliata', 'fixture_corretta'):
        rel = voce.get(chiave)
        if not rel or not os.path.isdir(os.path.join(cartella, rel)):
            res.append('fixture mancante')
            continue
        unita = da_cartella(os.path.join(cartella, rel))
        trovati = [k for k in DETERMINISTICI[classe](unita, ctx)
                   if not voce.get('scena') or k['unita'] == str(voce['scena'])]
        res.append('fallito' if trovati else 'passato')
    return tuple(res)


def cmd_prova(cartella, libro):
    voci = leggi(cartella, REGISTRO, {}).get('difetti') or []
    if not voci:
        raise comune.ErroreMotore(f'Registro vuoto: {REGISTRO}')
    righe, male = ['| ID | Classe | Rilevamento | Sbagliata | Corretta | Esito |', '|---|---|---|---|---|---|'], 0
    for v in voci:
        s, c = prova_voce(cartella, libro, v)
        # atteso: un difetto confermato fallisce sulla sbagliata e passa sulla corretta; uno non confermato passa su
        # tutte e due; il registro può dichiarare altro (un avviso che resta), sempre con la nota
        att = v.get('atteso') or ({'sbagliata': 'passato', 'corretta': 'passato'} if v.get('stato') == 'non confermato'
                                  else {'sbagliata': 'fallito', 'corretta': 'passato'})
        ok = (s, c) == (att['sbagliata'], att['corretta'])
        nd = s == 'non deterministico'
        if nd:
            s = c = v.get('valutazione') or 'non deterministico'
        male += 0 if ok or nd else 1
        righe.append(f'| {v["id"]} | {v["classe"]} | {dati()["classi"][v["classe"]]["rilevamento"]} | {s} | {c} | '
                     f'{"OK" if ok else ("—" if nd else "KO")} |')
    print('\n'.join(righe))
    print(f'Prova del cancello: {sum(1 for r in righe[2:] if r.endswith("| OK |"))} OK, {male} KO, '
          f'{sum(1 for r in righe[2:] if r.endswith("| — |"))} non deterministici.')
    return 1 if male else 0


# ---------------------------------------------------------------- registro di continuità

def cmd_continuita(cartella, libro):
    import capsula
    anno = anno_di(cartella)
    r = [f'# Registro di continuità — {libro["titolo"]}', '',
         'Generato da «zb difetti <libro> continuita» (e a ogni «zb esito»): non si scrive a mano. Le conoscenze dei '
         'personaggi vengono dalle capsule («Personaggi presenti e cosa sanno»).', '']
    for nome, testo in carica(cartella, libro):
        dic = dichiarazioni(testo)
        r += [f'## Unità {nome} — tipo {dic.get("tipo", "capitolo")}, chiusura {dic.get("chiusura", "—")}', '']
        for inizio, d, luogo in scene(testo, anno):
            r.append(f'- scena da r.{inizio}: {d:%d/%m/%Y} ' if d else f'- scena da r.{inizio}: data ignota ')
            r[-1] += f'— {luogo or "(luogo della scena precedente)"}'
        sc = scene(testo, anno)
        for n, riga in prosa(testo):
            for m in REL.finditer(riga):
                k, d = numero(m.group(2)), data_riga(sc, n)
                if k and d and (m.group(1) == 'da' or m.group(3)):
                    r.append(f'- r.{n} «{m.group(0).strip()}» → {d - datetime.timedelta(days=k):%d/%m}')
            for m in re.finditer(r"(?i)\b(\w+)\s+(mandate|tamponi|gradini|chiavi|biette|bulloni|cornici)\b", riga):
                if numero(m.group(1)):
                    r.append(f'- r.{n} conteggio: {numero(m.group(1))} {m.group(2)}')
        p = os.path.join(cartella, capsula.rel(int(nome))) if str(nome).isdigit() else ''
        if p and os.path.isfile(p):
            sez = capsula.sezioni_di(open(p, encoding='utf-8').read(), capsula.lingua(libro))
            r.append(f'- conoscenze: {sez.get("Personaggi presenti e cosa sanno", "—")}')
        r.append('')
    comune.scrivi(cartella, CONTINUITA, '\n'.join(r))
    print(f'Registro di continuità: {CONTINUITA}.')
    return 0


# ---------------------------------------------------------------- fatti da verificare

def registra_fatti(cartella, n):
    """Fatti della sezione «## Fatti da verificare» di audit/NN.md (righe «- r.N «…»: tipo») nel registro dei fatti,
    stato «da_verificare» (solo i nuovi)."""
    import percorso
    import yaml
    p = os.path.join(cartella, percorso.rel_audit(n))
    if not os.path.isfile(p):
        return 0
    t = open(p, encoding='utf-8').read()
    if '## Fatti da verificare' not in t:
        return 0
    blocco = t.split('## Fatti da verificare', 1)[1].split('\n## ', 1)[0]
    dati_f = leggi(cartella, FATTI, {'fatti': []})
    voci = dati_f.setdefault('fatti', [])
    note = {(str(v.get('unita')), v.get('affermazione')) for v in voci}
    nuovi = 0
    for m in re.finditer(r'(?m)^-\s*(r\.\d+.*)$', blocco):
        aff = m.group(1).strip()
        if aff.lower().startswith('nessun') or (str(n), aff) in note:
            continue
        voci.append({'id': f'F{len(voci) + 1:03d}', 'unita': str(n), 'affermazione': aff, 'stato': 'da_verificare'})
        nuovi += 1
    if nuovi:
        comune.scrivi(cartella, FATTI, yaml.safe_dump(dati_f, allow_unicode=True, sort_keys=False))
    return nuovi


def cmd_fatto(cartella, args, argv):
    import yaml
    if len(args) < 2 or args[1] not in ('verificato', 'generico', 'errato', 'da_verificare'):
        raise comune.ErroreMotore('Uso: zb difetti <libro> fatto <id> verificato|generico|errato [--fonte <url>] '
                                  '[--nota <testo>]')
    d = leggi(cartella, FATTI, {'fatti': []})
    v = next((x for x in d.get('fatti') or [] if x.get('id') == args[0]), None)
    if not v:
        raise comune.ErroreMotore(f'Fatto {args[0]} assente in {FATTI}')
    fonte = argv[argv.index('--fonte') + 1] if '--fonte' in argv else None
    if args[1] == 'verificato' and not fonte:
        raise comune.ErroreMotore('Un fatto «verificato» vuole la fonte (--fonte <url o riferimento>).')
    v.update({'stato': args[1], 'data': datetime.date.today().isoformat()})
    if fonte:
        v['fonte'] = fonte
    if '--nota' in argv:
        v['nota'] = ' '.join(argv[argv.index('--nota') + 1:])
    comune.scrivi(cartella, FATTI, yaml.safe_dump(d, allow_unicode=True, sort_keys=False))
    print(f'Fatto {args[0]}: {args[1]}.')
    return 0


# ---------------------------------------------------------------- comando

def tabella(esiti):
    r = ['| Classe | Gravità | Esito | Dettagli |', '|---|---|---|---|']
    r += [f'| {c} | {g} | {e} | {"; ".join(d[:4]).replace("|", "/") or "—"} |' for c, g, e, d in esiti]
    return '\n'.join(r)


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore(__doc__.strip().split('Uso:', 1)[1])
    cartella, libro, _ = comune.carica_libro(args[0])
    resto = [a for a in args[1:] if not a.startswith('--')]
    if resto[:1] == ['prova']:
        return cmd_prova(cartella, libro)
    if resto[:1] == ['continuita']:
        return cmd_continuita(cartella, libro)
    if resto[:1] == ['fatto']:
        return cmd_fatto(cartella, resto[1:], argv)
    unita = carica(cartella, libro)
    scelte = [resto[0]] if resto else [n for n, _ in unita]
    codice = 0
    for n in scelte:
        es = esiti_unita(cartella, libro, n, unita)
        print(f'## Capitolo {n}\n\n{tabella(es)}\n')
        codice = 1 if blocchi(es) else codice
    print('Cancello: ' + ('KO (difetti bloccanti falliti o non verificabili).' if codice else 'passato.'))
    return codice


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

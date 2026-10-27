"""Controllo tipografico del manoscritto (comando «zb tipografia <libro> [N]», 2026-10-27).

Errori che un libro pubblicato non può avere e che il motore trova da solo, senza modelli: accenti sbagliati
(perchè, nè, sè, pò, qual'è, E'), parola ripetuta per errore («il il»), spazio prima della punteggiatura o mancante
dopo, virgolette dritte (italiano), caporali spaiati nel paragrafo, due sistemi di dialogo nello stesso libro,
trattino corto con spazi al posto della lineetta, quattro o più punti. Ogni riga trovata è un KO, salvo una
correzione accettata in 06-diagnostica/correzioni-accettate.yaml ({controllo, dove: "file:riga", motivo}).
Apostrofi e puntini li rende tipografici l'impaginazione (impagina.tipografia_di_stampa): qui non si contano.
Report: 06-diagnostica/tipografia.md.
"""
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

ACCETTATE = os.path.join('06-diagnostica', 'correzioni-accettate.yaml')
# raddoppiamenti voluti dell'italiano (non sono refusi)
RADDOPPI = {'no', 'sì', 'si', 'piano', 'pian', 'via', 'così', 'ciao', 'presto', 'bene', 'quasi', 'mai', 'forse',
            'adagio', 'zitto', 'zitta', 'zitti', 'basta', 'dai', 'su', 'ecco', 'pronto', 'avanti', 'fuori', 'giù',
            'piano', 'poco', 'ora', 'subito', 'tanto', 'ma', 'eh', 'ah', 'oh', 'mh', 'già', 'sempre', 'tic', 'toc',
            'bla', 'ehi', 'yes', 'very', 'so', 'oh', 'well', 'no', 'had', 'that'}
REGOLE_IT = [
    ('accento', re.compile(r"\b(perchè|poichè|affinchè|benchè|finchè|giacchè|purchè|sicchè|nè|sè|pò)\b", re.I),
     'accento sbagliato (perché, poiché, né, sé, po’…)'),
    ('accento', re.compile(r"\bqual[’']\s?è\b", re.I), '«qual è» si scrive senza apostrofo'),
    ('accento', re.compile(r"\bpo\b(?![’'])"), '«po’» vuole l’apostrofo'),
    ('accento', re.compile(r"(?:^|(?<=[.!?…»]\s)|(?<=—\s)|(?<=«))E[’']"), '«È» maiuscola accentata, non «E’»'),
    ('virgolette', re.compile(r'"'), 'virgolette dritte: in italiano «» (o “” se il manuale lo dice)'),
]
REGOLE = [
    ('spazio', re.compile(r'\s[,.;:!?](?!\.\.)'), 'spazio prima della punteggiatura'),
    ('spazio', re.compile(r'[,;:](?=[^\s\d»”’)\]—…\'"])'), 'manca lo spazio dopo la punteggiatura'),
    ('spazio', re.compile(r'(?<=[a-zà-ù]{2})[.!?](?=[A-ZÀ-Ý][a-zà-ù])'), 'manca lo spazio dopo la fine della frase'),
    ('lineetta', re.compile(r'\s-\s'), 'trattino corto con spazi: per un inciso la lineetta (– o —)'),
    ('punti', re.compile(r'\.{4,}|…\.|\.…'), 'più di tre punti di sospensione'),
]


def accettate(cartella):
    dati = comune.leggi_yaml(os.path.join(cartella, ACCETTATE)) if os.path.isfile(os.path.join(cartella, ACCETTATE)) else None
    voci = (dati or {}).get('accettate') or [] if isinstance(dati, dict) else (dati or [])
    return {(str(v.get('controllo')), str(v.get('dove'))) for v in voci if isinstance(v, dict) and v.get('motivo')}


def raddoppi(riga):
    out = []
    for m in re.finditer(r"\b(\w+)\s+\1\b", riga, re.I):
        w = m.group(1).lower()
        if w not in RADDOPPI and not w.isdigit():
            out.append(m.group(0))
    return out


def controlla_testo(rel, testo, lingua):
    """[(controllo, dove, dettaglio)] di un'unità."""
    regole = (REGOLE_IT if lingua == 'it' else []) + REGOLE
    out = []
    for n, r in comune.righe_prosa(testo):
        dove = f'{rel}:{n}'
        for nome, rx, msg in regole:
            for m in rx.finditer(r):
                frammento = r[max(0, m.start() - 15):m.end() + 15].strip()
                out.append((f'tipografia:{nome}', dove, f'{msg}: «{frammento}»'))
        for x in raddoppi(r):
            out.append(('tipografia:ripetizione', dove, f'parola ripetuta: «{x}»'))
        if lingua == 'it' and r.count('«') != r.count('»'):
            out.append(('tipografia:caporali', dove, f'caporali spaiati ({r.count("«")} « e {r.count("»")} »)'))
    return out


def sistemi_dialogo(unita):
    """Sistemi di apertura delle battute usati nel libro (righe che cominciano con —, «, “ o ")."""
    usati = {}
    for rel, testo in unita:
        for n, r in comune.righe_prosa(testo):
            s = r.lstrip()[:1]
            if s in ('—', '«', '“', '"'):
                usati.setdefault(s, f'{rel}:{n}')
    return usati


def controlla_libro(cartella, libro, solo=None):
    lingua = libro.get('lingua', 'it')
    unita = [(os.path.relpath(p, cartella), open(p, encoding='utf-8').read()) for u, p in comune.unita(cartella, libro)
             if solo is None or u == solo]
    out = []
    for rel, testo in unita:
        out += controlla_testo(rel, testo, lingua)
    usati = sistemi_dialogo(unita)
    if solo is None and len(usati) > 1:
        out.append(('tipografia:dialogo', ', '.join(usati.values()),
                    f'due o più sistemi di dialogo nello stesso libro ({", ".join(usati)}): uno solo'))
    acc = accettate(cartella)
    return [x for x in out if (x[0], x[1]) not in acc]


def report(libro, trovati):
    r = [f'# Controllo tipografico — {libro["titolo"]}', '',
         f'{len(trovati)} errori (KO). Una scelta voluta si dichiara in {ACCETTATE} con il motivo.', '']
    if trovati:
        r += ['| Controllo | Dove | Dettaglio |', '|---|---|---|']
        r += [f'| {c} | {d} | {t.replace("|", "/")} |' for c, d, t in trovati]
    return '\n'.join(r) + '\n'


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: zb tipografia <libro> [N]')
    cartella, libro, _ = comune.carica_libro(args[0])
    solo = ' '.join(args[1:]) or None
    trovati = controlla_libro(cartella, libro, solo)
    if solo is None:
        comune.scrivi(cartella, os.path.join('06-diagnostica', 'tipografia.md'), report(libro, trovati))
    for c, d, t in trovati[:25]:
        print(f'KO {c} {d}: {t}')
    if len(trovati) > 25:
        print(f'… altri {len(trovati) - 25} nel report 06-diagnostica/tipografia.md')
    print(f'Tipografia: {len(trovati)} errori.')
    return 1 if trovati else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

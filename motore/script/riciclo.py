"""Anti-riciclo a 7 parole (proposta C.2).

Uso: python3 -B riciclo.py <libro> [--schermo]
Per ogni unità cerca le sequenze di 7 parole uguali:
- al testo precedente del libro (testo_precedente, solo con modalita: riscrittura) → KO;
- alle unità precedenti dello stesso libro → AVVISO (una ripetizione può essere voluta).
Le parole si confrontano in minuscolo, senza la punteggiatura ai bordi. Le finestre
consecutive che combaciano formano un solo segmento, riportato con la riga d'inizio.
Le battute canoniche del manuale (03-architettura/manuale-di-stile.md, voce «Battute canoniche»:
le frasi tra «» delle righe che la seguono, più rientrate) sono escluse: le loro parole, nel testo
nuovo e in quello precedente, non combaciano con niente.
Report: <libro>/06-diagnostica/riciclo.md.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
from stile import risultato, tabella  # noqa: E402

N = 7
BORDI = '.,;:!?«»"()[]—–-…\''


def gettoni(testo):
    """[(parola_normalizzata, riga)] della prosa."""
    out = []
    for n, r in comune.righe_prosa(testo):
        for t in comune.parole(r):
            w = t.strip(BORDI).lower()
            if w:
                out.append((w, n))
    return out


MANUALE = os.path.join('03-architettura', 'manuale-di-stile.md')


def battute_canoniche(cartella):
    """Frasi tra «» della voce «Battute canoniche» del manuale, come liste di parole normalizzate."""
    import re
    p = os.path.join(cartella, MANUALE)
    if not os.path.isfile(p):
        return []
    righe = open(p, encoding='utf-8').read().splitlines()
    out, rientro, trovate = [], None, 0
    for r in righe:
        if rientro is not None and r.strip():
            if len(r) - len(r.lstrip()) <= rientro or r.lstrip().startswith('#'):
                if trovate:
                    break
                rientro = None       # la voce citata senza elenco sotto: si cerca la successiva
        if rientro is None:
            if re.search(r'(?i)battute canoniche', r) and not r.lstrip().startswith('#'):
                rientro = len(r) - len(r.lstrip())
            continue
        if not r.strip():
            continue
        trovate += 1
        for frase in re.findall(r'«([^»]+)»', r):
            parole = [w for w in (t.strip(BORDI).lower() for t in comune.parole(frase)) if w]
            if parole:
                out.append(parole)
    return out


def maschera(tok, canoniche):
    """Sostituisce le parole delle battute canoniche con segnaposto unici (non combaciano mai)."""
    parole = [w for w, _ in tok]
    via = set()
    for c in canoniche:
        k = len(c)
        for i in range(len(parole) - k + 1):
            if parole[i:i + k] == c:
                via.update(range(i, i + k))
    return [((None, id(tok), i), r) if i in via else (w, r) for i, (w, r) in enumerate(tok)]


def ngrammi(tok):
    return {tuple(w for w, _ in tok[i:i + N]) for i in range(len(tok) - N + 1)}


def segmenti(tok, insieme):
    """Segmenti di finestre consecutive presenti in `insieme`: [(riga, testo)]."""
    out, i = [], 0
    while i <= len(tok) - N:
        if tuple(w for w, _ in tok[i:i + N]) in insieme:
            j = i
            while j + 1 <= len(tok) - N and tuple(w for w, _ in tok[j + 1:j + 1 + N]) in insieme:
                j += 1
            out.append((tok[i][1], ' '.join(w if isinstance(w, str) else '…' for w, _ in tok[i:j + N])))
            i = j + N
        else:
            i += 1
    return out


def controlla_libro(cartella, libro):
    risultati = []
    canoniche = battute_canoniche(cartella)
    precedente = set()
    if libro.get('modalita') == 'riscrittura' and libro.get('testo_precedente'):
        precedente = ngrammi(maschera(gettoni(open(os.path.join(cartella, libro['testo_precedente']),
                                                   encoding='utf-8').read()), canoniche))
    gia_scritti = set()
    for nome, p in comune.unita(cartella, libro):
        tok = maschera(gettoni(open(p, encoding='utf-8').read()), canoniche)
        for riga, testo in segmenti(tok, precedente):
            risultati.append(risultato(nome, 'riciclo:testo_precedente', 'KO', riga, testo))
        for riga, testo in segmenti(tok, gia_scritti):
            risultati.append(risultato(nome, 'riciclo:unita_precedenti', 'AVVISO', riga, testo))
        gia_scritti |= ngrammi(tok)
    return risultati


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: riciclo.py <libro> [--schermo]')
    cartella, libro, _ = comune.carica_libro(args[0])
    risultati = controlla_libro(cartella, libro)
    righe = ['# Anti-riciclo a 7 parole', '', f'Libro: {libro["titolo"]}.', '']
    righe += tabella(risultati) if risultati else ['Nessuna sequenza di 7 parole ripetuta.']
    testo = '\n'.join(righe + [''])
    if '--schermo' in argv:
        print(testo)
    else:
        print('scritto', comune.scrivi(cartella, '06-diagnostica/riciclo.md', testo))
    return 1 if any(r['esito'] == 'KO' for r in risultati) else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

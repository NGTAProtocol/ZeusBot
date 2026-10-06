"""Anti-riciclo a 7 parole (proposta C.2).

Uso: python3 -B riciclo.py <libro> [--schermo]
Per ogni unità cerca le sequenze di 7 parole uguali:
- al testo precedente del libro (testo_precedente, solo con modalita: riscrittura) → KO;
- alle unità precedenti dello stesso libro → AVVISO (una ripetizione può essere voluta).
Le parole si confrontano in minuscolo, senza la punteggiatura ai bordi. Le finestre
consecutive che combaciano formano un solo segmento, riportato con la riga d'inizio.
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
            out.append((tok[i][1], ' '.join(w for w, _ in tok[i:j + N])))
            i = j + N
        else:
            i += 1
    return out


def controlla_libro(cartella, libro):
    risultati = []
    precedente = set()
    if libro.get('modalita') == 'riscrittura' and libro.get('testo_precedente'):
        precedente = ngrammi(gettoni(open(os.path.join(cartella, libro['testo_precedente']), encoding='utf-8').read()))
    gia_scritti = set()
    for nome, p in comune.unita(cartella, libro):
        tok = gettoni(open(p, encoding='utf-8').read())
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

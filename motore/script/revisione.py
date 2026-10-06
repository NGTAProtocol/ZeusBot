"""Mostra un documento o i documenti di un gate in blocchi (proposta C.1, C.6). Sola lettura.

Uso: python3 -B revisione.py <libro> <documento|gate> [N]
- <documento>: percorso relativo al libro (per esempio 02-bibbia/bibbia.md).
- <gate>: documenti | pagina_campione | primi_capitoli | lotto | controllo_fallito:
  tutti i documenti del gate, uno dopo l'altro.
- N: numero del blocco (predefinito 1).
Blocchi di circa 120 righe, tagliati a fine paragrafo. Ogni blocco si apre con
«<Titolo> — <documento> — Blocco N di M, righe X-Y — sha256 <12 caratteri>».
Testo puro, senza numeri di riga. Non scrive nulla: lo stato della revisione lo tiene fase.py.
"""
import hashlib
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

MISURA = 120
MARGINE = 40
DOCUMENTI = ['libro.yaml', '02-bibbia/bibbia.md', 'cronologia.yaml', '03-architettura/manuale-di-stile.md',
             '03-architettura/scaletta.md', '03-architettura/piano-parole.md']
PAGINA_CAMPIONE = '05-revisioni/pagina-campione.md'


def nome_report(nome):
    return f'{int(nome):02d}' if nome.isdigit() else nome.replace(' ', '-')


def unita_con_report(cartella, libro, nomi):
    """File delle unità indicate, ciascuna seguita dal suo report di capitolo.py."""
    trovate = dict(comune.unita(cartella, libro))
    out = []
    for n in nomi:
        n = str(n)
        if n not in trovate:
            raise comune.ErroreMotore(f'Unità «{n}» assente in 04-manoscritto')
        out.append(os.path.relpath(trovate[n], cartella))
        out.append(f'06-diagnostica/capitoli/{nome_report(n)}.md')
    return out


def documenti_del_gate(cartella, libro, stato, gate):
    if gate == 'documenti':
        return list(DOCUMENTI)
    if gate == 'pagina_campione':
        return [PAGINA_CAMPIONE]
    if gate == 'primi_capitoli':
        return unita_con_report(cartella, libro, ['1', '2', '3'])
    if gate == 'lotto':
        return unita_con_report(cartella, libro, (stato.get('lotto') or {}).get('capitoli') or [])
    if gate == 'controllo_fallito':
        return unita_con_report(cartella, libro, [str(stato.get('passo') or '').replace('capitolo ', '')])
    raise comune.ErroreMotore(f'Gate sconosciuto: {gate}')


def taglia(testo):
    """[(X, Y, testo)] con righe 1-based; ogni taglio cade dopo una riga vuota, se c'è entro MARGINE."""
    righe = testo.splitlines()
    out, inizio = [], 0
    while inizio < len(righe):
        fine = min(inizio + MISURA, len(righe))
        j = fine
        while j < len(righe) and j < inizio + MISURA + MARGINE and righe[j - 1].strip():
            j += 1
        if j < len(righe) and righe[j - 1].strip():
            j = fine                      # nessun fine paragrafo vicino: taglio a MISURA
        out.append((inizio + 1, j, '\n'.join(righe[inizio:j])))
        inizio = j
    return out or [(1, 0, '')]


def blocchi(cartella, documenti):
    """[(documento, X, Y, sha12, testo)] per tutti i documenti, in ordine."""
    out = []
    for rel in documenti:
        p = os.path.join(cartella, rel)
        if not os.path.isfile(p):
            raise comune.ErroreMotore(f'Documento mancante: {rel}')
        testo = open(p, encoding='utf-8').read()
        sha = comune.sha256_file(p)[:12]
        out += [(rel, x, y, sha, t) for x, y, t in taglia(testo)]
    return out


def impronta(cartella, documenti):
    """sha256 dell'insieme dei documenti (cambia se ne cambia uno)."""
    h = hashlib.sha256()
    for rel in documenti:
        h.update(rel.encode() + b'\0' + comune.sha256_file(os.path.join(cartella, rel)).encode())
    return h.hexdigest()[:12]


def mostra(titolo, b, n):
    rel, x, y, sha, testo = b[n - 1]
    return f'{titolo} — {rel} — Blocco {n} di {len(b)}, righe {x}-{y} — sha256 {sha}\n\n{testo}\n'


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2:
        raise comune.ErroreMotore('Uso: revisione.py <libro> <documento|gate> [N]')
    cartella, libro, _ = comune.carica_libro(args[0])
    cosa = args[1]
    n = int(args[2]) if len(args) > 2 and args[2].isdigit() else 1
    if os.path.isfile(os.path.join(cartella, cosa)):
        if not comune.dentro(cartella, os.path.join(cartella, cosa)):
            raise comune.ErroreMotore(f'Documento fuori dal libro: {cosa}')
        documenti = [cosa]
    else:
        stato = comune.leggi_yaml(os.path.join(cartella, 'stato.yaml')) if os.path.isfile(
            os.path.join(cartella, 'stato.yaml')) else {}
        documenti = documenti_del_gate(cartella, libro, stato, cosa)
    b = blocchi(cartella, documenti)
    if not 1 <= n <= len(b):
        raise comune.ErroreMotore(f'Blocco {n} inesistente: i blocchi sono {len(b)}')
    print(mostra(libro['titolo'], b, n))
    if n == len(b):
        print('Fine del documento. Scrivi ok o correggi: …')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

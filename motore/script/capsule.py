"""Capsule di continuità (editoriale/risparmio-token.md, punto 2; agente editoriale/agenti/capsula.md).

Uso: zb capsula <libro> <N>
Dopo ogni capitolo accettato: se 07-capsule/NN.md manca, lo crea con i sette campi fissi vuoti e stampa
la chiamata per l'agente «capsula» (che li riempie, massimo 180 parole); se c'è, lo controlla: campi
compilati e al massimo PAROLE_MAX parole. Lo scrittore e i revisori leggono le capsule, non i capitoli
precedenti interi.
Controlli negli altri comandi (campo «capsule» di libro.yaml: obbligatorie | avviso; senza il campo, avviso):
- zb avvio, nelle fasi dalla stesura in poi: capsule mancanti o incomplete per i capitoli già scritti;
- zb esito <N>: capsule dei capitoli prima di N.
Con «obbligatorie» il comando si ferma; con «avviso» stampa l'elenco e prosegue.
"""
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

CAMPI = ['Eventi', 'Personaggi presenti e cosa sanno', 'Informazioni date al lettore', 'Promesse aperte e chiuse',
         'Cosa cambia', 'Stato emotivo finale', 'Ultima immagine']
PAROLE_MAX = 180
FASI_CON_CAPSULE = ('stesura', 'revisione_manoscritto', 'line', 'copy', 'bozze', 'chiusura', 'chiuso')


def percorso(n):
    return f'07-capsule/{int(n):02d}.md'


def modello(n, titolo):
    return '\n'.join([f'# Capsula — capitolo {n}', '', f'<!-- {titolo}: da riempire con l\'agente capsula, massimo '
                      f'{PAROLE_MAX} parole, solo fatti. -->', ''] + [f'- {c}:' for c in CAMPI]) + '\n'


def problemi(cartella, n):
    """[] se la capsula del capitolo n è valida; altrimenti i problemi."""
    p = os.path.join(cartella, percorso(n))
    if not os.path.isfile(p):
        return ['manca']
    testo = re.sub(r'<!--.*?-->', '', open(p, encoding='utf-8').read(), flags=re.S)
    out = []
    for c in CAMPI:
        m = re.search(rf'(?m)^- {re.escape(c)}:[ \t]*(.*)$', testo)
        if not m or not m.group(1).strip():
            out.append(f'campo «{c}» vuoto')
    import conta
    corpo = '\n'.join(r for r in testo.splitlines() if not r.startswith('#'))
    parole = conta.conta_testo(corpo) - sum(len(c.split()) for c in CAMPI)
    if parole > PAROLE_MAX:
        out.append(f'{parole} parole (massimo {PAROLE_MAX})')
    return out


def mancanti(cartella, libro, stato, fino_a=None):
    """Capitoli numerati già scritti (fino a ultimo_capitolo_scritto, o fino_a escluso) senza capsula valida."""
    ultimo = (fino_a - 1) if fino_a else (stato.get('ultimo_capitolo_scritto') or 0)
    scritti = [int(u) for u, _ in comune.unita(cartella, libro) if u.isdigit() and int(u) <= ultimo]
    return [n for n in scritti if problemi(cartella, n)]


def regola(libro):
    return libro.get('capsule') or 'avviso'


def controlla(cartella, libro, stato, fino_a=None, contesto='avvio'):
    """Messaggio sulle capsule mancanti; ErroreMotore con capsule: obbligatorie. None se tutto c'è."""
    m = mancanti(cartella, libro, stato, fino_a)
    if not m:
        return None
    elenco = ', '.join(f'{n} ({"; ".join(problemi(cartella, n))})' for n in m)
    msg = (f'capsule di continuità mancanti o incomplete: capitoli {elenco}. Per ognuno: zb capsula <libro> N '
           '(agente capsula).')
    if regola(libro) == 'obbligatorie':
        raise comune.ErroreMotore(f'{contesto}: {msg}')
    return f'AVVISO: {msg}'


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2 or not args[1].isdigit():
        raise comune.ErroreMotore('Uso: zb capsula <libro> <N>')
    cartella, libro, _ = comune.carica_libro(args[0])
    n = int(args[1])
    if str(n) not in [u for u, _ in comune.unita(cartella, libro)]:
        raise comune.ErroreMotore(f'Capitolo {n} assente in 04-manoscritto: niente da riassumere.')
    rel = percorso(n)
    if not os.path.isfile(os.path.join(cartella, rel)):
        comune.scrivi(cartella, rel, modello(n, libro['titolo']))
        cap = os.path.relpath(dict(comune.unita(cartella, libro))[str(n)], cartella)
        print(f'Creato {rel} con i campi vuoti. Chiama l\'agente capsula: libro {cartella}, capitolo {n}, legge solo '
              f'{cap}, scrive {rel}. Poi di nuovo: zb capsula <libro> {n}.')
        return 1
    pr = problemi(cartella, n)
    if pr:
        print(f'KO capsula {n}: ' + '; '.join(pr))
        return 1
    print(f'OK capsula {n}: sette campi compilati, al massimo {PAROLE_MAX} parole.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

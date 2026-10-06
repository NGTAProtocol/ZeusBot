"""Valida i profili di genere di motore/profili/ (proposta B.2.2, B.6).

Uso: valida_profili.py [file.yaml ...]   (senza argomenti: tutti i profili)
Controlla: schema dati/profilo.schema.yaml; minimo <= media <= massimo;
somma di parole_per_atto = 1; min_su_media < max_su_media; chiusura tra i
valori ammessi; ogni valore con una fonte nel commento (es. «12 r. 22»,
«01-mercato r. 25») o la marca PROPOSTA, sulla riga o su una riga madre.
Esce con 1 al primo profilo non valido, indicando file e campo.
Alla fine elenca i campi per uso (dallo schema, chiave «uso»): controllati da uno script,
usati da nuovo.py per generare i documenti, informativi (non controllati da nessuno script).
"""
import glob
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

FONTE = re.compile(r'(\b\d{2}(-[a-z-]+)?\s+rr?\.\s*\d+|PROPOSTA)')


def controlla_fonti(testo, nome):
    """Ogni riga con un valore deve avere una fonte sulla riga o su una riga madre."""
    errori = []
    pila = []                                   # (rientro, ha_fonte)
    for n, riga in enumerate(testo.splitlines(), 1):
        if not riga.strip() or riga.lstrip().startswith('#'):
            continue
        rientro = len(riga) - len(riga.lstrip())
        corpo, _, commento = riga.partition('#')
        ha = bool(FONTE.search(commento))
        while pila and pila[-1][0] >= rientro:
            pila.pop()
        coperta = ha or any(h for _, h in pila)
        chiave_sola = re.match(r'^\s*[\w-]+:\s*$', corpo) is not None
        if not chiave_sola and not coperta and corpo.strip() != 'genere: ' + nome:
            errori.append(f'riga {n}: valore senza fonte né PROPOSTA: {riga.strip()}')
        pila.append((rientro, ha))
    return errori


def valida_profilo(percorso):
    nome = os.path.basename(percorso)[:-5]
    testo = open(percorso, encoding='utf-8').read()
    dati = comune.leggi_yaml(percorso)
    errori = comune.valida(dati, comune.carica_schema('profilo'), nome)
    if errori:
        return errori
    c = dati['capitoli']
    if not (c['minimo'] <= c['media'][0] and c['media'][1] <= c['massimo']):
        errori.append(f'{nome}.capitoli: serve minimo <= media <= massimo')
    if abs(sum(dati['parole_per_atto']) - 1) > 1e-9:
        errori.append(f'{nome}.parole_per_atto: la somma deve essere 1')
    if not c['coerenza']['min_su_media'] < c['coerenza']['max_su_media']:
        errori.append(f'{nome}.capitoli.coerenza: min_su_media deve essere minore di max_su_media')
    if dati['genere'] != nome:
        errori.append(f'{nome}.genere: deve coincidere con il nome del file')
    errori += [f'{nome}: {e}' for e in controlla_fonti(testo, nome)]
    return errori


def usi(schema=None, prefisso=''):
    """{campo: uso} dai campi dello schema dei profili che dichiarano «uso»."""
    schema = schema or comune.carica_schema('profilo')
    out = {}
    for k, s in (schema.get('campi') or {}).items():
        if 'uso' in s:
            out[prefisso + k] = s['uso']
        elif s.get('tipo') == 'mappa':
            out.update(usi(s, prefisso + k + '.'))
    return out


def main(argv):
    file = comune.argomenti(argv) or sorted(glob.glob(os.path.join(comune.radice_motore(), 'profili', '*.yaml')))
    for p in file:
        errori = valida_profilo(p)
        if errori:
            print(f'KO {os.path.basename(p)}')
            for e in errori:
                print(f'  - {e}')
            return 1
        print(f'OK {os.path.basename(p)}')
    u = usi()
    for uso, titolo in (('controllo', 'Campi controllati'), ('generazione', 'Usati da nuovo.py per i documenti'),
                        ('informativo', 'Informativi, non controllati')):
        print(f'{titolo}: {", ".join(k for k, v in u.items() if v == uso)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

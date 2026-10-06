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

"""Conteggio delle parole con il metodo unico (proposta B.5 regola 3).

Uso: conta.py <libro> [--schermo]
Metodo unico: token separati da spazi; escluse le righe che cominciano con «#»
(titoli Markdown), le righe di commento HTML (<!-- … -->, note nascoste del
motore) e i token senza lettere né cifre (lineette, separatori, segni isolati).
Totale: parole scritte più i budget delle unità di piano-parole.md non ancora scritte, rispetto a
parole.target_totale. Fuori da capitoli.tolleranza_totale: AVVISO con il budget residuo proposto per le
unità rimanenti (proposta: il motore non accorcia né allunga nessun capitolo da solo).
Scrive <libro>/06-diagnostica/conteggio.md, oppure stampa a schermo con --schermo.
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
        raise comune.ErroreMotore('Uso: conta.py <libro> [--schermo]')
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
    if '--schermo' in argv:
        print(testo)
    else:
        print('scritto', comune.scrivi(cartella, '06-diagnostica/conteggio.md', testo))
    return totale


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

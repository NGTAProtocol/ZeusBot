"""Voce del libro dalle pagine campione dell'autore (2026-10-27).

L'autore mette una o due pagine di prosa in <libro>/00-progetto/voce/campione-1.md (e campione-2.md per un ibrido),
più, se vuole, indicazioni.md (che cosa prendere da ciascun campione). Il motore misura lo stile senza modelli (zb voce
campioni); l'agente «voce» scrive la scheda 02-bibbia/voce.md con le sette sezioni della banca-voci; lo scrittore la
legge con i campioni prima di ogni capitolo. Si imita il modo, mai il testo: riciclo.py dà KO su 7 parole consecutive
uguali a un campione, e «zb voce scheda» controlla lo stesso sulla scheda.

Uso: zb voce campioni <libro> | zb voce scheda <libro>
"""
import os
import re
import statistics
import sys
from collections import Counter

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

CARTELLA = os.path.join('00-progetto', 'voce')
SCHEDA = os.path.join('02-bibbia', 'voce.md')
MISURE = os.path.join(CARTELLA, 'misure.md')
INDICAZIONI = os.path.join(CARTELLA, 'indicazioni.md')
MINIMO_PAROLE = 250          # sotto, le misure non dicono niente: il campione va allungato
PUNTEGGIATURA = [('virgole', ','), ('punti e virgola', ';'), ('due punti', ':'), ('puntini', '…'),
                 ('esclamativi', '!'), ('interrogativi', '?'), ('lineette nel testo', '—')]


def campioni(cartella):
    """Percorsi relativi dei campioni (campione-1.md, campione-2.md…), in ordine, che hanno del testo."""
    d = os.path.join(cartella, CARTELLA)
    if not os.path.isdir(d):
        return []
    out = []
    for f in sorted(os.listdir(d)):
        if re.match(r'^campione-\d+\.md$', f):
            t = open(os.path.join(d, f), encoding='utf-8').read()
            if comune.MODELLO not in t and conta_parole(t):
                out.append(os.path.join(CARTELLA, f))
    return out


def conta_parole(testo):
    return sum(len(comune.parole(r)) for _, r in comune.righe_prosa(testo))


def frasi(testo):
    unito = ' '.join(r.strip() for _, r in comune.righe_prosa(testo))
    return [f for f in re.split(r'(?<=[.!?…])\s+', unito) if comune.parole(f)]


def paragrafi(testo):
    out, prima = [], None
    for n, r in comune.righe_prosa(testo):
        if out and prima == n - 1:
            out[-1] += ' ' + r.strip()
        else:
            out.append(r.strip())
        prima = n
    return out


def misure(testo, lingua):
    """Misure di stile di un testo: ritmo, dialogo, paragrafi, punteggiatura, aperture, lessico."""
    import stile
    ling = comune.lingue()[lingua]
    met = stile.metriche(testo, ling)
    lun = [len(comune.parole(f)) for f in frasi(testo)] or [0]
    par = [len(comune.parole(p)) for p in paragrafi(testo) if not p.startswith(stile._dialogo(ling))] or [0]
    parole = [w.strip('.,;:!?«»"()—–-…\'').lower() for _, r in comune.righe_prosa(testo) for w in comune.parole(r)]
    parole = [w for w in parole if w]
    tot = len(parole) or 1
    grezzo = ' '.join(r for _, r in comune.righe_prosa(testo))
    aperture = Counter(comune.parole(f)[0].strip('«»"—–-').lower() for f in frasi(testo) if comune.parole(f))
    lessico = Counter(w for w in parole if len(w) >= 7)
    return {
        'parole': met['parole'],
        'frase_media': met['frase_media'],
        'frase_mediana': statistics.median(lun),
        'frase_p90': sorted(lun)[int(0.9 * (len(lun) - 1))],
        'frasi_corte': round(100 * sum(1 for x in lun if x <= 8) / len(lun)),
        'frasi_lunghe': round(100 * sum(1 for x in lun if x >= 25) / len(lun)),
        'dialogo': met['dialogo_percento'],
        'paragrafo_medio': round(sum(par) / len(par), 1),
        'punteggiatura': {nome: round(1000 * grezzo.count(seg) / tot, 1) for nome, seg in PUNTEGGIATURA},
        'aperture': [f'{w} ({n})' for w, n in aperture.most_common(6)],
        'lessico': [w for w, _ in lessico.most_common(12)],
    }


def tabella_misure(cartella, libro, rel_campioni):
    m = [misure(open(os.path.join(cartella, r), encoding='utf-8').read(), libro.get('lingua', 'it')) for r in rel_campioni]
    nomi = [os.path.basename(r)[:-3] for r in rel_campioni]
    intest = '| Misura | ' + ' | '.join(nomi) + (' | media |' if len(m) > 1 else ' |')
    righe = [intest, '|' + '---|' * (len(m) + 1 + (len(m) > 1))]

    def riga(etichetta, chiave, fmt=lambda x: str(x)):
        vals = [x[chiave] for x in m]
        media = [str(round(sum(vals) / len(vals), 1))] if len(m) > 1 else []
        righe.append(f'| {etichetta} | ' + ' | '.join(fmt(v) for v in vals) + (f' | {media[0]} |' if media else ' |'))
    riga('Parole', 'parole')
    riga('Frase media (parole)', 'frase_media')
    riga('Frase mediana', 'frase_mediana')
    riga('Frase lunga (90° percentile)', 'frase_p90')
    riga('Frasi corte, ≤ 8 parole (%)', 'frasi_corte')
    riga('Frasi lunghe, ≥ 25 parole (%)', 'frasi_lunghe')
    riga('Dialogo (% delle parole)', 'dialogo')
    riga('Paragrafo di narrazione medio (parole)', 'paragrafo_medio')
    for nome, _ in PUNTEGGIATURA:
        vals = [x['punteggiatura'][nome] for x in m]
        media = f' | {round(sum(vals) / len(vals), 1)} |' if len(m) > 1 else ' |'
        righe.append(f'| {nome.capitalize()} per 1000 parole | ' + ' | '.join(map(str, vals)) + media)
    righe += ['', '## Aperture di frase più frequenti', '']
    righe += [f'- {n}: {", ".join(x["aperture"]) or "—"}' for n, x in zip(nomi, m)]
    righe += ['', '## Lessico caratteristico (parole di 7 lettere o più, le più frequenti)', '']
    righe += [f'- {n}: {", ".join(x["lessico"]) or "—"}' for n, x in zip(nomi, m)]
    return m, righe


def cmd_campioni(cartella, libro):
    rel = campioni(cartella)
    if not rel:
        raise comune.ErroreMotore(f'Nessun campione in {CARTELLA}/: metti una pagina di prosa in {CARTELLA}/campione-1.md '
                                  '(e una seconda in campione-2.md per una voce ibrida).')
    corti = [r for r in rel if conta_parole(open(os.path.join(cartella, r), encoding='utf-8').read()) < MINIMO_PAROLE]
    if corti:
        raise comune.ErroreMotore(f'Campioni troppo corti (meno di {MINIMO_PAROLE} parole): {", ".join(corti)}. '
                                  'Serve almeno una pagina piena perché le misure dicano qualcosa.')
    m, tab = tabella_misure(cartella, libro, rel)
    ibrido = len(rel) > 1
    ind = os.path.isfile(os.path.join(cartella, INDICAZIONI))
    testa = [f'# Misure della voce dai campioni — {libro["titolo"]}', '',
             'Scritte da «zb voce campioni»: misure senza modelli, per l\'agente «voce» che scrive 02-bibbia/voce.md. '
             'Sono un ritratto del modo di scrivere, non soglie: nessuna diventa un blocco.', '',
             f'Campioni: {", ".join(rel)}.' + (' Voce ibrida: ' + (f'segui {INDICAZIONI}.' if ind else
                                                                    'nessuna indicazione, fondi i tratti più forti di '
                                                                    'ciascun campione e dichiara in sezione 2 da dove '
                                                                    'viene ogni tratto.') if ibrido else ''), '']
    comune.scrivi(cartella, MISURE, '\n'.join(testa + tab) + '\n')
    print(f'Misure della voce: {MISURE} ({len(rel)} campion{"i" if ibrido else "e"}; frase media '
          + ', '.join(str(x["frase_media"]) for x in m) + '; dialogo ' + ', '.join(f'{x["dialogo"]}%' for x in m) + ').')
    print(f'Prossimo: agente «voce» sul libro (scrive {SCHEDA}), poi «zb voce scheda <libro>».')
    return 0


def copie(cartella, testo, rel_campioni=None):
    """Segmenti di 7 o più parole consecutive del testo uguali a un campione: [(riga, testo)]."""
    import riciclo
    insieme = set()
    for r in rel_campioni if rel_campioni is not None else campioni(cartella):
        insieme |= riciclo.ngrammi(riciclo.gettoni(open(os.path.join(cartella, r), encoding='utf-8').read()))
    if not insieme:
        return []
    return riciclo.segmenti(riciclo.gettoni(testo), insieme)


def cmd_scheda(cartella, libro):
    import voce
    p = os.path.join(cartella, SCHEDA)
    if not os.path.isfile(p):
        raise comune.ErroreMotore(f'{SCHEDA} assente: prima «zb voce campioni <libro>», poi l\'agente «voce».')
    testo = open(p, encoding='utf-8').read()
    titoli = [t for t, _ in voce.sezioni(testo).values()]
    problemi = [f'manca la sezione «{s}»' for s in voce.SEZIONI if not any(s.lower() in t.lower() for t in titoli)]
    if comune.MODELLO in testo:
        problemi.append('ancora modello (riga «<!-- zb: modello -->»)')
    for riga, seg in copie(cartella, testo):
        problemi.append(f'riga {riga}: copiato da un campione «{seg[:80]}» (la scheda descrive, gli esempi si inventano)')
    if problemi:
        print('KO voce del libro:\n- ' + '\n- '.join(problemi[:20]))
        return 1
    print(f'OK voce del libro: {SCHEDA} con le sette sezioni, nessuna frase copiata dai campioni.')
    return 0


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2 or args[0] not in ('campioni', 'scheda'):
        raise comune.ErroreMotore('Uso: zb voce campioni <libro> | zb voce scheda <libro>')
    cartella, libro, _ = comune.carica_libro(args[1])
    return cmd_campioni(cartella, libro) if args[0] == 'campioni' else cmd_scheda(cartella, libro)


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

"""Audit anti-IA non distruttivo e vocabolario dai dati (comando «zb antiia»).

Uso: python3 -B antiia.py <libro> [N]                         misure di un capitolo (o di tutti); report
     python3 -B antiia.py estrai --ia <dir> --umano <dir> [--lingua it] [--uscita <file>]
     python3 -B antiia.py taratura --umano <dir> [--lingua it]
Audit: non tocca il testo. Scrive <libro>/06-diagnostica/anti-ia/NN.md con le misure e le gravità P0/P1/P2
del catalogo della lingua (motore/editoriale/anti-ia/catalogo-it.md; lingue/en/catalogo-anti-ia.md):
- variazione_frasi: deviazione standard / media della lunghezza delle frasi di narrazione (profilo «narrativa»;
  il dialogo è escluso: il parlato è irregolare per natura);
- aperture_uguali: percentuale di frasi di narrazione consecutive che cominciano con la stessa parola;
- formule_per_mille: voci della lista nera di base e del vocabolario L1-L3 (dati/antiia.yaml) per mille parole;
- lineette_narrazione: lineette fuori dal dialogo per mille parole di narrazione, nelle lingue in cui la
  lineetta apre la battuta (idea di book-genesis-studio, MIT, riscritta: il segno del dialogo usato anche
  per gli incisi della narrazione confonde la pagina);
- varieta_lessicale: MATTR su finestre di 100 parole (idea di haowjy/creative-writing-skills, Apache-2.0);
- chiusure_uguali: capitoli consecutivi con la stessa sigla di chiusura e la stessa punteggiatura finale.
Le soglie stanno in motore/dati/antiia.yaml, tarate sui mini-libri di prove/ (valori di progetto, non norme
misurate su prosa umana: «taratura» misura i falsi positivi su un corpus umano, idea di avoid-ai-writing, MIT).
Estrai: confronto delle frequenze (log-odds con prior, parole e bigrammi) tra testi scritti da un modello e
prosa umana; stampa i candidati, non scrive nel motore: l'autore decide cosa va nei livelli L1-L3.
"""
import math
import os
import re
import statistics
import sys
from collections import Counter

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

PAROLA = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?", re.U)


def soglie(lingua):
    d = comune.leggi_yaml(os.path.join(comune.radice_motore(), 'dati', 'antiia.yaml'))
    s = dict(d['soglie'])
    s.update((d.get('lingue') or {}).get(lingua, {}).get('soglie') or {})
    voc = (d.get('lingue') or {}).get(lingua, {}).get('vocabolario') or {}
    return s, voc


def dialogo_di(lingua):
    l = comune.lingue()[lingua]
    d = l['lineetta_dialogo']
    return tuple(d) if isinstance(d, list) else (d,)


def frasi(testo):
    unito = ' '.join(testo.split())
    return [f for f in re.split(r'(?<=[.!?…])\s+', unito) if PAROLA.search(f)]


def parti(testo, lingua):
    """(narrazione, dialogo): righe di prosa separate secondo il segno della battuta della lingua."""
    pre = dialogo_di(lingua)
    nar, dia = [], []
    for _, r in comune.righe_prosa(testo):
        (dia if r.lstrip().startswith(pre) else nar).append(r.strip())
    return '\n'.join(nar), '\n'.join(dia)


def mattr(parole, finestra=100):
    if len(parole) < finestra:
        return len(set(parole)) / len(parole) if parole else 0.0
    vals = [len(set(parole[i:i + finestra])) / finestra for i in range(0, len(parole) - finestra + 1)]
    return sum(vals) / len(vals)


def misure(testo, lingua, voci_regex):
    nar, _ = parti(testo, lingua)
    fr = frasi(nar)
    lung = [len(PAROLA.findall(f)) for f in fr]
    cv = statistics.pstdev(lung) / statistics.mean(lung) if len(lung) > 2 and statistics.mean(lung) else None
    prime = [PAROLA.findall(f)[0].lower() for f in fr if PAROLA.findall(f)]
    uguali = sum(1 for a, b in zip(prime, prime[1:]) if a == b)
    aperture = 100 * uguali / (len(prime) - 1) if len(prime) > 1 else 0.0
    tutte = [p.lower() for _, r in comune.righe_prosa(testo) for p in PAROLA.findall(r)]
    formule = sum(len(re.findall(rx, ' '.join(r for _, r in comune.righe_prosa(testo)))) for rx in voci_regex)
    pn = len(PAROLA.findall(nar))
    lineette = 0
    if '—' in dialogo_di(lingua):
        lineette = sum(r.count('—') + r.count(' – ') for r in nar.splitlines())
    return {'parole': len(tutte), 'frasi_narrazione': len(fr), 'variazione_frasi': round(cv, 3) if cv is not None else None,
            'aperture_uguali': round(aperture, 1), 'formule_per_mille': round(1000 * formule / len(tutte), 2) if tutte else 0,
            'lineette_narrazione': round(1000 * lineette / pn, 2) if pn else 0, 'varieta_lessicale': round(mattr(tutte), 3)}


def regex_voci(libro, voc):
    base = os.path.join(comune.radice_motore(), 'dati', 'lista-nera.yaml' if libro.get('lingua', 'it') == 'it'
                        else f'lista-nera-{libro["lingua"]}.yaml')
    rx = [v['pattern'] for v in ((comune.leggi_yaml(base) or {}).get('voci') or [])] if os.path.isfile(base) else []
    for livello in ('L1', 'L2', 'L3'):
        rx += [r'(?i)(?<!\w)' + re.escape(w) + r'(?!\w)' for w in voc.get(livello) or []]
    return rx


def valuta(m, s):
    """[(misura, gravità, dettaglio)] secondo le soglie."""
    out = []
    if m['variazione_frasi'] is not None and m['frasi_narrazione'] >= s['frasi_minime'] \
            and m['variazione_frasi'] < s['variazione_frasi_min']:
        out.append(('variazione_frasi', 'P1', f'{m["variazione_frasi"]} sotto {s["variazione_frasi_min"]}: frasi di lunghezza simile'))
    if m['aperture_uguali'] > s['aperture_uguali_max']:
        out.append(('aperture_uguali', 'P2', f'{m["aperture_uguali"]}% sopra {s["aperture_uguali_max"]}%'))
    if m['formule_per_mille'] > s['formule_per_mille_max']:
        out.append(('formule_per_mille', 'P2', f'{m["formule_per_mille"]} sopra {s["formule_per_mille_max"]}'))
    if m['lineette_narrazione'] > s['lineette_narrazione_max']:
        out.append(('lineette_narrazione', 'P2', f'{m["lineette_narrazione"]} per mille sopra {s["lineette_narrazione_max"]}'))
    if m['parole'] >= 200 and m['varieta_lessicale'] < s['varieta_lessicale_min']:
        out.append(('varieta_lessicale', 'P2', f'MATTR {m["varieta_lessicale"]} sotto {s["varieta_lessicale_min"]}'))
    return out


def chiusure(cartella, libro):
    """{capitolo: (gravità, dettaglio)} per le chiusure uguali in capitoli consecutivi."""
    numerati = sorted((int(u), p) for u, p in comune.unita(cartella, libro) if u.isdigit())
    firme = []
    for n, p in numerati:
        t = open(p, encoding='utf-8').read()
        sig = (comune.dichiarazioni_unita(t) or {}).get('chiusura')
        ult = [f for f in frasi(' '.join(r for _, r in comune.righe_prosa(t)))][-1:] or ['']
        firme.append((n, sig, ult[0].strip()[-1:]))
    out, serie = {}, 1
    for i in range(1, len(firme)):
        uguali = firme[i][1] and firme[i][1] == firme[i - 1][1] and firme[i][2] == firme[i - 1][2]
        serie = serie + 1 if uguali else 1
        if serie >= 3:
            out[firme[i][0]] = ('P0', f'terzo capitolo di fila con chiusura {firme[i][1]} e la stessa punteggiatura finale')
        elif serie == 2:
            out[firme[i][0]] = ('P2', f'stessa chiusura ({firme[i][1]}) e punteggiatura finale del capitolo precedente')
    return out


def audit(cartella, libro, scelta=None):
    s, voc = soglie(libro.get('lingua', 'it'))
    rx = regex_voci(libro, voc)
    ch = chiusure(cartella, libro)
    esiti = {}
    for u, p in comune.unita(cartella, libro):
        if scelta and u != scelta:
            continue
        m = misure(open(p, encoding='utf-8').read(), libro.get('lingua', 'it'), rx)
        v = valuta(m, s)
        if u.isdigit() and int(u) in ch:
            v.append(('chiusure_uguali', *ch[int(u)]))
        esiti[u] = (m, v)
        righe = [f'# Audit anti-IA, unità {u} — {libro["titolo"]}', '',
                 'Modalità audit: il testo non è stato toccato. Le gravità seguono il catalogo anti-IA della lingua; '
                 'una scelta documentata nel manuale del libro vince sul catalogo.', '',
                 '| Misura | Valore |', '|---|---|'] + [f'| {k} | {x} |' for k, x in m.items()]
        righe += ['', '## Segnalazioni', '']
        righe += [f'- {g} {k}: {d}' for k, g, d in v] or ['- nessuna']
        nome = f'{int(u):02d}' if u.isdigit() else u.replace(' ', '-')
        comune.scrivi(cartella, f'06-diagnostica/anti-ia/{nome}.md', '\n'.join(righe) + '\n')
    return esiti


def testi_di(cartella):
    out = []
    for dp, _, fs in os.walk(cartella):
        for f in sorted(fs):
            if f.endswith(('.md', '.txt')):
                out.append(open(os.path.join(dp, f), encoding='utf-8', errors='ignore').read())
    return out


def estrai(ia, umano, lingua, uscita):
    """Candidati per il vocabolario: log-odds informativo con prior di Dirichlet (Monroe e altri, 2008)."""
    def conteggi(testi):
        c = Counter()
        for t in testi:
            p = [x.lower() for x in PAROLA.findall(t)]
            c.update(p)
            c.update(f'{a} {b}' for a, b in zip(p, p[1:]))
        return c
    a, b = conteggi(testi_di(ia)), conteggi(testi_di(umano))
    prior = a + b
    na, nb, n0 = sum(a.values()), sum(b.values()), sum(prior.values())
    if not na or not nb:
        raise comune.ErroreMotore('Corpus vuoto: servono testi .md o .txt in entrambe le cartelle.')
    punti = []
    for w, k0 in prior.items():
        if k0 < 5:
            continue
        ya, yb, aw = a[w], b[w], k0 * 0.01 + 0.01
        d = math.log((ya + aw) / (na + n0 * 0.01 - ya - aw)) - math.log((yb + aw) / (nb + n0 * 0.01 - yb - aw))
        var = 1 / (ya + aw) + 1 / (yb + aw)
        punti.append((d / math.sqrt(var), w, ya, yb))
    punti.sort(reverse=True)
    righe = [f'# Candidati per il vocabolario anti-IA ({lingua})', '',
             f'Corpus modello: {na} occorrenze; corpus umano: {nb}. Punteggio z del log-odds (più alto = più tipico del modello).',
             'Proposte, non decisioni: l\'autore sceglie i livelli L1-L3 e li scrive in motore/dati/antiia.yaml con fonte e data.', '',
             '| z | Forma | Modello | Umano |', '|---|---|---|---|']
    righe += [f'| {z:.1f} | {w} | {x} | {y} |' for z, w, x, y in punti[:80]]
    with open(uscita, 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')
    return punti[:15], uscita


def main(argv):
    args = comune.argomenti(argv)
    def opz(n, pred=None):
        return argv[argv.index(n) + 1] if n in argv and argv.index(n) + 1 < len(argv) else pred
    if args[:1] == ['estrai']:
        import tempfile
        lingua = opz('--lingua', 'it')
        top, path = estrai(opz('--ia'), opz('--umano'), lingua,
                           opz('--uscita', os.path.join(tempfile.gettempdir(), f'zb-antiia-candidati-{lingua}.md')))
        print('Primi candidati: ' + ', '.join(w for _, w, _, _ in top))
        print(f'Elenco completo: {path} (fuori dal repository).')
        return 0
    if args[:1] == ['taratura']:
        lingua = opz('--lingua', 'it')
        s, voc = soglie(lingua)
        testi = testi_di(opz('--umano'))
        segnalati = Counter()
        for t in testi:
            for k, _, _ in valuta(misure(t, lingua, regex_voci({'lingua': lingua}, voc)), s):
                segnalati[k] += 1
        print(f'Taratura su {len(testi)} testi umani: falsi positivi per misura: '
              + (', '.join(f'{k} {v}/{len(testi)}' for k, v in segnalati.items()) or 'nessuno'))
        return 0
    if not args:
        raise comune.ErroreMotore('Uso: antiia.py <libro> [N] | estrai --ia <dir> --umano <dir> | taratura --umano <dir>')
    cartella, libro, _ = comune.carica_libro(args[0])
    esiti = audit(cartella, libro, args[1] if len(args) > 1 else None)
    conta = Counter(g for _, v in esiti.values() for _, g, _ in v)
    for u, (m, v) in list(esiti.items())[:30]:
        print(f'{u}: ' + ('; '.join(f'{g} {k}' for k, g, _ in v) or 'nessuna segnalazione'))
    print(f'Anti-IA (audit, testo intatto): P0 {conta["P0"]}, P1 {conta["P1"]}, P2 {conta["P2"]}; report in 06-diagnostica/anti-ia/.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

"""Audit anti-IA non distruttivo e vocabolario dai dati (comando «zb antiia»).

Uso: python3 -B antiia.py <libro> [N]                         misure di un capitolo (o di tutti); report
     python3 -B antiia.py estrai --ia <dir> --umano <dir> [--lingua it] [--uscita <file>]
     python3 -B antiia.py taratura --umano <dir> [--lingua it]
Audit: non tocca il testo. Scrive <libro>/06-diagnostica/anti-ia/NN.md con le misure e le gravità P0/P1/P2
del catalogo della lingua (motore/editoriale/anti-ia/catalogo-it.md; lingue/en/catalogo-anti-ia.md):
- variazione_frasi: deviazione standard / media della lunghezza delle frasi di narrazione (profilo «narrativa»;
  il dialogo è escluso: il parlato è irregolare per natura);
- aperture_uguali: percentuale di frasi di narrazione consecutive che cominciano con la stessa parola (una battuta
  di dialogo in mezzo interrompe la serie: tra le due frasi parla un altro);
- formule_per_mille: voci della lista nera di base e del vocabolario L1-L3 (dati/antiia.yaml) per mille parole;
- lineette_narrazione: lineette fuori dal dialogo per mille parole di narrazione, nelle lingue in cui la
  lineetta apre la battuta (idea di book-genesis-studio, MIT, riscritta: il segno del dialogo usato anche
  per gli incisi della narrazione confonde la pagina);
- varieta_lessicale: MATTR su finestre di 100 parole (idea di haowjy/creative-writing-skills, Apache-2.0);
- chiusure_uguali: capitoli consecutivi con la stessa sigla di chiusura e la stessa punteggiatura finale (P2 al
  secondo, P0 oltre chiusure_uguali_max).
Da motore (971b6df), misure P2 in più:
- formule_catalogo_per_mille: formule di editoriale/anti-ia/formule.yaml (tipo «formula», fuori dal dialogo) per
  mille parole; le voci della sezione B si contano solo con formule_sezione_b: true (decisione aperta dell'autore);
- coerenza: segni tipografici all'inglese (virgolette dritte, trattino al posto della virgola; tipo «coerenza»);
- ripetizioni_per_mille: gruppi di parole piene con la stessa radice almeno 3 volte in 60 parole (solo italiano).
Soglie: dati/antiia.yaml, poi la lingua, poi il blocco anti_ia del profilo di genere, poi anti_ia di libro.yaml.
Modalità (anti_ia.modalita): avviso (audit, predefinita) | blocco (capitolo.py: ogni segnalazione è un KO).
Il report elenca anche le posizioni (riga, schema, dove) per il line editor.
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


FORMULE = os.path.join('editoriale', 'anti-ia', 'formule.yaml')
PREDEFINITE = {'modalita': 'avviso', 'formule_catalogo_per_mille_max': 3.0, 'ripetizioni_per_mille_max': 12.0,
               'chiusure_uguali_max': 2, 'formule_sezione_b': False}
FINESTRA, SOGLIA_ECO = 60, 3
FUNZIONE = set('''il lo la i gli le un uno una di a da in con su per tra fra del dello della dei degli delle al allo alla
ai agli alle dal dallo dalla dai dagli dalle nel nello nella nei negli nelle sul sullo sulla sui sugli sulle col e ed o
oppure ma però anzi eppure perché poiché sebbene benché mentre quando come se che anche pure né neanche nemmeno non più
meno già ancora sempre mai poi dopo prima ora allora così quindi dunque comunque infatti cioè ecco molto poco troppo
tanto tutto tutta tutti tutte ogni qualche io tu lui lei noi voi loro egli ella essi esse me te sé mi ti ci vi si li ne
mio tuo suo nostro vostro mia tua sua miei tuoi suoi mie tue sue questo questa questi queste quello quella quelli quelle
cui chi quale quali dove essere sono era erano stato stata fu furono sarà avere aveva avevano ebbe hanno abbiamo stare
stava fare fece faceva andare andò andava potere poteva volere voleva dovere doveva disse dire detto niente nulla qui
lì là sopra sotto dentro fuori senza verso contro fosse fossi fossero stesso stessa'''.split())
SUFFISSI = sorted('''issimo issima issimi issime zioni zione mente eranno erebbe avamo evano ivano assero asse ando endo
ato ata ati ate uto uta uti ute ito ita iti ite are ere ire iamo ano ono ava eva iva ai ò i e o a'''.split(), key=len, reverse=True)


def soglie(lingua, profilo=None, libro=None):
    """(soglie, vocabolario): dati/antiia.yaml, la lingua, il profilo di genere (anti_ia), libro.yaml (anti_ia)."""
    d = comune.leggi_yaml(os.path.join(comune.radice_motore(), 'dati', 'antiia.yaml'))
    s = dict(PREDEFINITE)
    s.update(d['soglie'])
    s.update((d.get('lingue') or {}).get(lingua, {}).get('soglie') or {})
    s.update((profilo or {}).get('anti_ia') or {})
    s.update((libro or {}).get('anti_ia') or {})
    voc = (d.get('lingue') or {}).get(lingua, {}).get('vocabolario') or {}
    return s, voc


def formule(con_b=False):
    """[(id, sezione, tipo, regex)] di editoriale/anti-ia/formule.yaml (da motore)."""
    p = os.path.join(comune.radice_motore(), FORMULE)
    d = comune.leggi_yaml(p) if os.path.isfile(p) else {}
    return [(f['id'], f['sezione'], f['tipo'], re.compile(f['regex'], re.I | re.M)) for f in (d or {}).get('formule') or []
            if con_b or f['sezione'] != 'B']


def radice(p):
    import unicodedata
    p = unicodedata.normalize('NFC', p.lower())
    for x in SUFFISSI:
        if p.endswith(x) and len(p) - len(x) >= 4:
            return p[:-len(x)]
    return p


def echi(prosa):
    """[(radice, [righe])]: stessa radice almeno SOGLIA_ECO volte in FINESTRA parole piene (da motore)."""
    piene = []
    for n, r in prosa:
        for w in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", r.replace('’', "'")):
            wl = w.lower()
            if len(wl) >= 4 and wl not in FUNZIONE and not w[0].isupper():     # maiuscole: nomi propri (e attacchi)
                piene.append((radice(wl), n))
    gruppi, visti = [], set()
    for i in range(len(piene)):
        rad = piene[i][0]
        if (rad, i) in visti:
            continue
        fin = [j for j in range(i, min(i + FINESTRA, len(piene))) if piene[j][0] == rad]
        if len(fin) >= SOGLIA_ECO:
            for j in range(i, len(piene)):
                if piene[j][0] == rad:
                    visti.add((rad, j))
            gruppi.append((rad, sorted({piene[j][1] for j in fin})))
    unici, ultimo = [], {}
    for rad, righe in gruppi:
        if rad in ultimo and righe[0] <= ultimo[rad]:
            continue
        unici.append((rad, righe))
        ultimo[rad] = righe[-1]
    return unici


def misure_catalogo(testo, lingua, con_b=False):
    """(misure, posizioni) delle misure da motore: formule del catalogo, coerenza, ripetizioni ravvicinate."""
    prosa = comune.righe_prosa(testo)
    pre = dialogo_di(lingua) + ('«', '"', '“')
    trovate = []
    for fid, sez, tipo, rx in formule(con_b):
        for n, r in prosa:
            if tipo == 'formula' and r.lstrip().startswith(pre):
                continue
            for m in rx.finditer(r):
                trovate.append((n, f'formula {fid} ({sez})' if tipo == 'formula' else f'coerenza {fid} ({sez})',
                                m.group(0)[:60]))
    parole = sum(len(PAROLA.findall(r)) for _, r in prosa) or 1
    n_formule = sum(1 for x in trovate if x[1].startswith('formula'))
    gruppi = echi(prosa) if lingua == 'it' else []
    m = {'formule_catalogo_per_mille': round(1000 * n_formule / parole, 2),
         'coerenza': sum(1 for x in trovate if x[1].startswith('coerenza')),
         'ripetizioni_per_mille': round(1000 * len(gruppi) / parole, 2)}
    pos = trovate + [(righe[0], 'ripetizione', f'«{rad}…» alle righe {", ".join(map(str, righe))}') for rad, righe in gruppi]
    return m, sorted(pos, key=lambda x: x[0])


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


def aperture_uguali(testo, lingua):
    """(uguali, coppie): coppie di frasi di narrazione consecutive e quante cominciano con la stessa parola.
    Una battuta di dialogo in mezzo (riga di dialogo o frase che apre con il segno della battuta) interrompe la
    serie: «Il ragazzo spegne il motore. — Lascialo acceso. Il ragazzo gira la chiave.» non è una ripetizione,
    perché tra le due frasi parla un altro."""
    pre = dialogo_di(lingua) + ('«', '"', '“')
    blocchi, cur = [], []                     # righe di narrazione consecutive, interrotte dalle righe di dialogo
    for _, r in comune.righe_prosa(testo):
        if r.lstrip().startswith(dialogo_di(lingua)):
            blocchi.append(cur)
            cur = []
        else:
            cur.append(r.strip())
    blocchi.append(cur)
    serie = []
    for b in blocchi:
        cur = []
        for f in frasi('\n'.join(b)):
            if f.lstrip().startswith(pre):      # battuta dentro la riga di narrazione
                serie.append(cur)
                cur = []
            else:
                p = PAROLA.findall(f)               # frasi() oggi scarta le frasi senza parole: protezione in più
                if p:
                    cur.append(p[0].lower())
        serie.append(cur)
    uguali = sum(1 for s in serie for a, b in zip(s, s[1:]) if a == b)
    return uguali, sum(max(len(s) - 1, 0) for s in serie)


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
    uguali, coppie = aperture_uguali(testo, lingua)
    aperture = 100 * uguali / coppie if coppie else 0.0
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
    if m.get('formule_catalogo_per_mille', 0) > s['formule_catalogo_per_mille_max']:
        out.append(('formule_catalogo', 'P2', f'{m["formule_catalogo_per_mille"]} per mille sopra '
                                              f'{s["formule_catalogo_per_mille_max"]} (editoriale/anti-ia/formule.yaml)'))
    if m.get('coerenza'):
        out.append(('coerenza', 'P2', f'{m["coerenza"]} segni tipografici all\'inglese (virgolette o trattini)'))
    if m.get('ripetizioni_per_mille', 0) > s['ripetizioni_per_mille_max']:
        out.append(('ripetizioni_ravvicinate', 'P2', f'{m["ripetizioni_per_mille"]} gruppi per mille sopra '
                                                     f'{s["ripetizioni_per_mille_max"]}'))
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


def chiusure(cartella, libro, massimo=2):
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
        if serie > massimo:
            out[firme[i][0]] = ('P0', f'{serie} capitoli di fila con chiusura {firme[i][1]} e la stessa punteggiatura '
                                      f'finale (massimo {massimo})')
        elif serie == 2:
            out[firme[i][0]] = ('P2', f'stessa chiusura ({firme[i][1]}) e punteggiatura finale del capitolo precedente')
    return out


def audit(cartella, libro, scelta=None, profilo=None, scrivi=True):
    if profilo is None:
        try:
            profilo = comune.carica_libro(cartella)[2]
        except comune.ErroreMotore:
            profilo = {}
    lingua = libro.get('lingua', 'it')
    s, voc = soglie(lingua, profilo, libro)
    rx = regex_voci(libro, voc)
    ch = chiusure(cartella, libro, int(s['chiusure_uguali_max']))
    esiti = {}
    for u, p in comune.unita(cartella, libro):
        if scelta and u != scelta:
            continue
        testo = open(p, encoding='utf-8').read()
        m = misure(testo, lingua, rx)
        m_cat, posizioni = misure_catalogo(testo, lingua, bool(s.get('formule_sezione_b')))
        m.update(m_cat)
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
        righe += ['', f'## Elenco per il line editor (modalità {s["modalita"]})', '',
                  'Posizione, schema, dove. Si applica solo con modifiche puntuali; una ripetizione o una formula voluta '
                  'dalla voce resta.', '', '| Riga | Schema | Dove |', '|---|---|---|']
        righe += [f'| {n} | {sch} | {d.replace("|", "/")} |' for n, sch, d in posizioni] or ['| — | — | nessuno |']
        if scrivi:
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

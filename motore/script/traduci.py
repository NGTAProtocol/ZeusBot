"""Traduzione di un libro (comando «zb traduci <libro> --a <lingua> …»). Tutto in <libro>/08-traduzione-<lingua>/.

Uso: python3 -B traduci.py <libro> --a <lingua> inizia | stato | prepara N | controlla N | ritraduci N | confronta <A> <B>
- inizia: crea 08-traduzione-<lingua>/ come libro di traduzione (libro.yaml con «modalita: traduzione», stato.yaml,
  guida di traduzione e glossario da scrivere, piano e scaletta copiati dall'originale). Fase «guida».
- La guida (voce, registro, resa di dialetto e riferimenti locali, varietà britannica o americana) e il glossario
  (un termine = una traduzione) si approvano al gate «guida» PRIMA del capitolo 1 (fase.py, percorso.py).
- prepara N: 06-diagnostica/preparazione/NN.md della traduzione con il capitolo originale, la guida, le sole voci del
  glossario presenti nel capitolo, le capsule dell'originale fino a N-1 e le ultime righe del capitolo tradotto
  precedente (traduzione in sequenza; idee di asadeisa/book-translator e deusyu/translate-book, MIT, riscritte).
- controlla N (lo lancia «zb esito» nel libro di traduzione): stesso numero di paragrafi e di battute, stessi
  numeri e date, nomi del glossario resi come deciso, parole della lingua di partenza rimaste, rapporto di
  lunghezza, nessuna nota o didascalia aggiunta, chiusura e intestazione conservate. Report in
  06-diagnostica/capitoli/NN.md («Esito: N KO»).
- ritraduci N: confronta 06-diagnostica/ritraduzione/NN.md (ritraduzione del capitolo tradotto nella lingua di
  partenza, fatta da un revisore in sessione nuova; idea di Scriven, MIT) con l'originale: numeri, nomi,
  paragrafi, parole piene in comune. Misura indicativa di fedeltà, non un giudizio.
- confronta A B: misure di voce (lunghezza media e variazione delle frasi, dialogo, varietà lessicale) di due
  cartelle di capitoli tradotti, per scegliere tra traduzione in sequenza e a blocchi con ancora di stile.
Fedeltà: niente aggiunte, niente note o didascalie inventate, errori dell'autore resi come scritti.
"""
import os
import re
import shutil
import statistics
import sys
from collections import Counter

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import conta  # noqa: E402

PAROLA = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?", re.U)
# parole funzionali frequenti della lingua di partenza che non sono parole della lingua di arrivo
RESIDUE = {'it': {'che', 'della', 'delle', 'degli', 'nella', 'nelle', 'perché', 'anche', 'questo', 'questa',
                  'sono', 'aveva', 'però', 'quando', 'sempre', 'ancora', 'niente', 'tutto', 'dalla', 'alla',
                  'gli', 'una', 'il', 'con', 'per', 'più'},
           'en': {'the', 'and', 'with', 'which', 'would', 'could', 'should', 'there', 'their', 'what', 'this'}}
RAPPORTO = {('it', 'en'): (0.80, 1.20), ('en', 'it'): (0.90, 1.35)}
NOTE = re.compile(r'(?im)^\s*(\[?n\.\s*d\.\s*t\.?\]?|translator[’\']?s note|nota del traduttore|\[\^\d+\])')
GUIDA_MODELLO = """{modello}
# Guida di traduzione — {titolo} ({da} → {a})

Si approva al gate «guida» insieme al glossario, prima del capitolo 1.

- Voce (come suona il narratore nella lingua di arrivo):
- Registro (formale, colloquiale, misto; per personaggio se serve):
- Dialetto e parlate regionali (come si rendono, senza note):
- Riferimenti locali (cibi, istituzioni, toponimi: si tengono, si spiegano nel testo o si adattano):
- Varietà della lingua di arrivo (per l'inglese: americano o britannico):
- Sistema del dialogo nella lingua di arrivo:
- Titolo dell'edizione:
- Traduttore da indicare tra i contributor KDP:
- Dichiarazione KDP: una traduzione fatta con uno strumento di IA è «AI-generated» e va dichiarata
  (KDP, Content Guidelines, verificato il 2026-10-15).
"""


def opzione(argv, nome):
    return argv[argv.index(nome) + 1] if nome in argv and argv.index(nome) + 1 < len(argv) else None


def cartella_trad(cartella, lingua):
    return os.path.join(cartella, f'08-traduzione-{lingua}')


def originale_di(trad, libro_trad):
    return os.path.realpath(os.path.join(trad, libro_trad['traduzione']['da']))


# ---------------------------------------------------------------- inizia

def inizia(cartella, libro, lingua):
    if lingua not in comune.lingue() or lingua == libro['lingua']:
        raise comune.ErroreMotore(f'Lingua di arrivo «{lingua}» non ammessa (lingue: {", ".join(comune.lingue())}; '
                                  f'diversa da {libro["lingua"]}).')
    if lingua not in (libro.get('lingue_target') or []):
        print(f'AVVISO: «{lingua}» non è in lingue_target di libro.yaml.')
    T = cartella_trad(cartella, lingua)
    if os.path.exists(os.path.join(T, 'libro.yaml')):
        raise comune.ErroreMotore(f'La traduzione esiste già: {T}')
    lt = {k: v for k, v in libro.items() if k not in ('lingue_target', 'voce', 'testo_precedente')}
    lt.update({'lingua': lingua, 'lingua_originale': libro['lingua'], 'modalita': 'traduzione', 'percorso': 'editoriale',
               'gate': ['guida', 'line', 'copy', 'fedelta'],
               'traduzione': {'da': '..', 'lingua_originale': libro['lingua']},
               'voci': [], 'nome_vietato_prima_di': [], 'vincoli_capitolo': []})
    comune.scrivi(T, os.path.join(T, 'libro.yaml'), yaml.safe_dump(lt, sort_keys=False, allow_unicode=True, width=120))
    m = os.path.join(comune.radice_motore(), 'modelli')
    st = comune.leggi_yaml(os.path.join(m, 'stato.yaml'))
    st.update({'libro': libro['titolo'], 'fase': 'guida', 'passo': 'guida e glossario', 'sottofase': None,
               'parole': {'scritte': 0, 'obiettivo': 0, 'metodo': 'unico'},
               'fatti_bloccati': comune.leggi_yaml(os.path.join(cartella, 'stato.yaml')).get('fatti_bloccati') or [],
               'aggiornato': ''})
    comune.scrivi(T, os.path.join(T, 'stato.yaml'), yaml.safe_dump(st, sort_keys=False, allow_unicode=True))
    comune.scrivi(T, os.path.join(T, '00-progetto', 'guida-traduzione.md'), GUIDA_MODELLO.format(
        modello=comune.MODELLO, titolo=libro['titolo'], da=libro['lingua'], a=lingua))
    import codex
    termini = {v['nome']: None for v in codex.schede(cartella).values()}
    for r in open(os.path.join(cartella, 'nomi_propri.txt'), encoding='utf-8').read().split():
        termini.setdefault(r, None)
    comune.scrivi(T, os.path.join(T, '00-progetto', 'glossario.yaml'),
                  '# Glossario della traduzione: un termine = una traduzione. Per i nomi che non cambiano, la\n'
                  '# traduzione è il nome stesso. Si approva al gate «guida»; dopo cambia solo con «zb riapprova».\n'
                  + yaml.safe_dump({'termini': termini}, sort_keys=False, allow_unicode=True))
    for rel in (comune.rel_piano(cartella), comune.rel_scaletta(cartella)):
        dest = os.path.join(T, comune.STRUTTURA, os.path.basename(rel))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(os.path.join(cartella, rel), dest)
    for f in ('nomi_propri.txt', 'cronologia.yaml', '03-architettura/manuale-di-stile.md'):
        if os.path.isfile(os.path.join(cartella, f)):
            os.makedirs(os.path.dirname(os.path.join(T, f)) or T, exist_ok=True)
            shutil.copyfile(os.path.join(cartella, f), os.path.join(T, f))
    comune.scrivi(T, os.path.join(T, 'LEGGIMI.md'), f'# {libro["titolo"]} — traduzione {libro["lingua"]} → {lingua}\n\n'
                  f'Fase: guida; gate in attesa: nessuno\nUltimo capitolo approvato: —\n\n'
                  'Libro di traduzione: si lavora con i comandi di zb su questa cartella '
                  f'(zb avvio, zb pronto, zb esito …). Originale in «..» (sola lettura).\n')
    comune.scrivi(T, os.path.join(T, '.gitignore'), '.zb/\n')
    print(f'Traduzione avviata in {os.path.relpath(T, cartella)}/: scrivi la guida e il glossario, poi '
          f'«zb pronto {os.path.relpath(T)}», che apre il gate «guida».')


# ---------------------------------------------------------------- testo

def corpo(testo):
    """Righe di prosa (senza intestazione, titolo e commenti zb)."""
    return [r for _, r in comune.righe_prosa(testo)]


def paragrafi(testo):
    blocchi, cur = [], []
    for r in corpo(testo) + ['']:
        if r.strip():
            cur.append(r)
        elif cur:
            blocchi.append(' '.join(cur))
            cur = []
    return blocchi


def battute(testo, lingua):
    d = comune.lingue()[lingua]['lineetta_dialogo']
    pre = tuple(d) if isinstance(d, list) else (d,)
    return [p for p in paragrafi(testo) if p.lstrip().startswith(pre)]


def numeri(testo):
    return Counter(re.findall(r'\d+(?:[.,:]\d+)?', ' '.join(corpo(testo))))


def glossario(T):
    p = os.path.join(T, '00-progetto', 'glossario.yaml')
    return ((comune.leggi_yaml(p) or {}).get('termini') or {}) if os.path.isfile(p) else {}


def problemi_glossario(T):
    g = glossario(T)
    out = [f'«{k}»: traduzione mancante' for k, v in g.items() if not str(v or '').strip()]
    rese = Counter(str(v).strip().lower() for v in g.values() if v)
    out += [f'«{v}»: stessa traduzione per più termini' for v, n in rese.items() if n > 1]
    return out


def presente(term, testo):
    return re.search(r'(?<!\w)' + re.escape(term) + r'(?!\w)', testo, re.I) is not None


def capitoli_coppia(T, libro_trad, n):
    O = originale_di(T, libro_trad)
    _, lo, _ = comune.carica_libro(O)
    src = dict(comune.unita(O, lo)).get(str(n))
    dst = dict(comune.unita(T, libro_trad)).get(str(n))
    if not src:
        raise comune.ErroreMotore(f'Capitolo {n} assente nell\'originale')
    return O, lo, src, dst


def controlla(T, libro_trad, n):
    O, lo, src, dst = capitoli_coppia(T, libro_trad, n)
    if not dst:
        raise comune.ErroreMotore(f'Capitolo {n} tradotto assente in 04-manoscritto della traduzione')
    a, b = open(src, encoding='utf-8').read(), open(dst, encoding='utf-8').read()
    la, lb = lo['lingua'], libro_trad['lingua']
    ris = []

    def r(controllo, esito, dettaglio):
        ris.append((controllo, esito, dettaglio))
    pa, pb = len(paragrafi(a)), len(paragrafi(b))
    r('paragrafi', 'OK' if pa == pb else 'KO', f'{pa} → {pb}')
    ba, bb = len(battute(a, la)), len(battute(b, lb))
    r('battute', 'OK' if ba == bb else 'KO', f'{ba} → {bb}')
    na, nb = numeri(a), numeri(b)
    manca = sorted((na - nb).elements())
    agg = sorted((nb - na).elements())
    r('numeri e date', 'OK' if not manca and not agg else 'KO',
      'uguali' if not manca and not agg else f'mancano {manca}, in più {agg}')
    g = glossario(T)
    sbagliati = [f'{k}→{v}' for k, v in g.items() if v and presente(k, a) and not presente(str(v), b)]
    r('glossario', 'OK' if not sbagliati else 'KO', 'rese come deciso' if not sbagliati else ', '.join(sbagliati[:8]))
    res = sorted({w for w in (x.lower() for x in PAROLA.findall(' '.join(corpo(b)))) if w in RESIDUE.get(la, set())}
                 - {str(v).lower() for v in g.values() if v})
    r('parole residue', 'OK' if not res else 'KO', ', '.join(res[:10]) or 'nessuna')
    wa, wb = conta.conta_testo(a), conta.conta_testo(b)
    lo_, hi = RAPPORTO.get((la, lb), (0.8, 1.25))
    rap = wb / wa if wa else 0
    r('rapporto di lunghezza', 'OK' if lo_ <= rap <= hi else ('KO' if rap < lo_ - 0.1 or rap > hi + 0.15 else 'AVVISO'),
      f'{rap:.2f} ({wa} → {wb}; atteso {lo_}-{hi})')
    note = NOTE.findall(b)
    r('note aggiunte', 'OK' if not note else 'KO', 'nessuna' if not note else f'{len(note)} note del traduttore')
    da, db = comune.dichiarazioni_unita(a), comune.dichiarazioni_unita(b)
    r('chiusura conservata', 'OK' if da == db else 'KO', f'{da} → {db}')
    ia = [x for x in a.splitlines()[:4] if x.startswith('*')]
    ib = [x for x in b.splitlines()[:4] if x.startswith('*')]
    r('intestazione', 'OK' if len(ia) == len(ib) else 'KO', f'{len(ia)} → {len(ib)}')
    ko = sum(1 for x in ris if x[1] == 'KO')
    righe = [f'# Controlli di traduzione, capitolo {n} — {libro_trad["titolo"]} ({la} → {lb})', '',
             f'Esito: {ko} KO', '', '| Controllo | Esito | Dettaglio |', '|---|---|---|']
    righe += [f'| {c} | {e} | {d} |' for c, e, d in ris]
    comune.scrivi(T, os.path.join(T, '06-diagnostica', 'capitoli', f'{int(n):02d}.md'), '\n'.join(righe) + '\n')
    return ris, ko


def prepara(T, libro_trad, n):
    O, lo, src, _ = capitoli_coppia(T, libro_trad, n)
    a = open(src, encoding='utf-8').read()
    voci = {k: v for k, v in glossario(T).items() if presente(k, a)}
    caps = [os.path.relpath(os.path.join(O, '07-capsule', f'{i:02d}.md'), T) for i in range(1, n)
            if os.path.isfile(os.path.join(O, '07-capsule', f'{i:02d}.md'))]
    prec = dict(comune.unita(T, libro_trad)).get(str(n - 1))
    coda = [r for r in corpo(open(prec, encoding='utf-8').read()) if r.strip()][-4:] if prec else []
    out = [f'# Preparazione della traduzione, capitolo {n}', '',
           f'- Capitolo originale: {os.path.relpath(src, T)}', '- Guida: 00-progetto/guida-traduzione.md', '',
           '## Voci del glossario presenti nel capitolo (obbligatorie)', '']
    out += [f'- {k} → {v}' for k, v in voci.items()] or ['- nessuna']
    out += ['', '## Capsule dell\'originale', ''] + [f'- {c}' for c in caps] or ['- nessuna']
    if coda:
        out += ['', f'## Ultime righe del capitolo {n - 1} tradotto', ''] + coda
    out += ['', 'Fedeltà: niente aggiunte, niente note o didascalie, errori dell\'autore resi come scritti.']
    rel = os.path.join('06-diagnostica', 'preparazione', f'{n:02d}.md')
    comune.scrivi(T, os.path.join(T, rel), '\n'.join(out) + '\n')
    return rel, len(voci), len(caps)


def ritraduci(T, libro_trad, n):
    O, lo, src, _ = capitoli_coppia(T, libro_trad, n)
    p = os.path.join(T, '06-diagnostica', 'ritraduzione', f'{int(n):02d}.md')
    if not os.path.isfile(p):
        raise comune.ErroreMotore(f'Manca {os.path.relpath(p, T)}: la ritraduzione la fa un revisore in sessione nuova.')
    a, b = open(src, encoding='utf-8').read(), open(p, encoding='utf-8').read()
    piene = lambda t: {w.lower() for w in PAROLA.findall(' '.join(corpo(t))) if len(w) > 4}
    sa, sb = piene(a), piene(b)
    comuni = len(sa & sb) / len(sa | sb) if sa | sb else 0
    nomi = [k for k in glossario(T) if presente(k, a) and not presente(k, b)]
    out = {'paragrafi': f'{len(paragrafi(a))} / {len(paragrafi(b))}', 'numeri_uguali': numeri(a) == numeri(b),
           'nomi_persi': nomi, 'parole_piene_in_comune': round(comuni, 2)}
    righe = [f'# Ritraduzione a campione, capitolo {n}', '', 'Misura indicativa di fedeltà (non un giudizio): '
             'la ritraduzione si confronta con l\'originale.', '']
    righe += [f'- {k}: {v}' for k, v in out.items()]
    comune.scrivi(T, os.path.join(T, '06-diagnostica', 'ritraduzione', f'{int(n):02d}-confronto.md'), '\n'.join(righe) + '\n')
    return out


def voce(cartella_capitoli, lingua):
    import antiia
    testi = [open(os.path.join(cartella_capitoli, f), encoding='utf-8').read()
             for f in sorted(os.listdir(cartella_capitoli)) if f.endswith('.md')]
    ms = [antiia.misure(t, lingua, []) for t in testi]
    medie = []
    for t in testi:
        fr = antiia.frasi(' '.join(corpo(t)))
        medie.append(statistics.mean(len(PAROLA.findall(f)) for f in fr) if fr else 0)
    return {'frase_media_per_capitolo': [round(x, 1) for x in medie],
            'scarto_frase_media': round(statistics.pstdev(medie), 2) if len(medie) > 1 else 0,
            'variazione_frasi': [m['variazione_frasi'] for m in ms],
            'varieta_lessicale': [m['varieta_lessicale'] for m in ms]}


def main(argv):
    args = comune.argomenti(argv)
    lingua = opzione(argv, '--a')
    if not args or not lingua:
        raise comune.ErroreMotore('Uso: traduci.py <libro> --a <lingua> inizia|stato|prepara N|controlla N|ritraduci N|confronta A B')
    azione = [a for a in args[1:] if a != lingua]
    cmd = azione[0] if azione else 'stato'
    cartella, libro, _ = comune.carica_libro(args[0])
    if libro.get('modalita') == 'traduzione':          # indicata la cartella della traduzione
        T, lt = cartella, libro
    else:
        T = cartella_trad(cartella, lingua)
        lt = comune.leggi_yaml(os.path.join(T, 'libro.yaml')) if os.path.isfile(os.path.join(T, 'libro.yaml')) else None
    if cmd == 'inizia':
        inizia(cartella, libro, lingua)
        return 0
    if cmd == 'confronta' and len(azione) >= 3:
        for nome, d in (('A', azione[1]), ('B', azione[2])):
            print(f'{nome} ({d}): {voce(d, lingua)}')
        print('Tiene meglio la voce chi ha lo scarto della frase media più basso e la variazione più vicina all\'originale.')
        return 0
    if not lt:
        raise comune.ErroreMotore(f'Traduzione non avviata: zb traduci {args[0]} --a {lingua} inizia')
    if cmd == 'stato':
        st = comune.leggi_yaml(os.path.join(T, 'stato.yaml'))
        print(f'Traduzione {lt["lingua_originale"]} → {lt["lingua"]}: fase {st["fase"]}; gate {st["gate_in_attesa"] or "nessuno"}; '
              f'capitoli tradotti fino a {st["ultimo_capitolo_scritto"] or "—"}. Glossario: '
              + ('; '.join(problemi_glossario(T)[:5]) or 'completo'))
        return 0
    if cmd in ('prepara', 'controlla', 'ritraduci') and len(azione) > 1 and azione[1].isdigit():
        n = int(azione[1])
        if cmd == 'prepara':
            rel, nv, nc = prepara(T, lt, n)
            print(f'Preparazione: {rel} ({nv} voci del glossario, {nc} capsule). Prossimo: agente traduttore, poi zb esito.')
            return 0
        if cmd == 'controlla':
            ris, ko = controlla(T, lt, n)
            for c, e, d in ris:
                if e != 'OK':
                    print(f'{e} {c}: {d}')
            print(f'Capitolo {n} tradotto: {ko} KO (06-diagnostica/capitoli/{n:02d}.md).')
            return 1 if ko else 0
        out = ritraduci(T, lt, n)
        print(f'Ritraduzione {n}: ' + '; '.join(f'{k} {v}' for k, v in out.items()))
        return 0
    raise comune.ErroreMotore('Uso: traduci.py <libro> --a <lingua> inizia|stato|prepara N|controlla N|ritraduci N|confronta A B')


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

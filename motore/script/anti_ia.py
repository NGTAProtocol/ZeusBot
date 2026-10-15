"""Misure anti-IA di un capitolo (editoriale/anti-ia/catalogo-it.md, sezione H), in modalità audit.

Uso: python3 -B anti_ia.py <libro> <N> [--schermo]       (lo chiama capitolo.py, quindi zb esito)
Misure, con le soglie del profilo di genere (campo anti_ia, tarate sui mini-libri di prova):
1. monotonia: deviazione standard della lunghezza delle frasi (parole) sotto frase_dev_min;
2. aperture: quota di frasi che cominciano con la stessa parola sopra apertura_max (solo con almeno
   apertura_min_frasi frasi);
3. formule: occorrenze per mille parole delle formule di editoriale/anti-ia/formule.yaml (tipo «formula»,
   fuori dal dialogo) sopra formule_max_per_1000;
4. chiusure: stesso tipo di chiusura (riga <!-- zb: chiusura=… -->) in più di chiusura_max_consecutivi
   capitoli di fila;
5. ripetizioni ravvicinate (proposta nostra, schede in docs/ANALISI_REPOSITORY.md): stessa radice almeno
   3 volte in 60 parole piene; gruppi per mille parole sopra echi_max_per_1000.
Più le regole di coerenza (virgolette dritte o curve all'inglese, trattino al posto della virgola),
segnalate a parte. Modalità audit: non riscrive nulla; scrive l'elenco (riga, schema, proposta) in
<libro>/06-diagnostica/anti-ia/NN.md e restituisce gli esiti come AVVISO (KO solo con anti_ia.modalita:
blocco nel profilo o in libro.yaml override). Le correzioni si applicano dopo l'«ok» dell'autore.
"""
import os
import re
import statistics
import sys
import unicodedata

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

FORMULE = os.path.join('editoriale', 'anti-ia', 'formule.yaml')
PREDEFINITI = {'modalita': 'avviso', 'frase_dev_min': 4.0, 'apertura_max': 0.30, 'apertura_min_frasi': 20,
               'formule_max_per_1000': 3.0, 'chiusura_max_consecutivi': 3, 'echi_max_per_1000': 12.0}
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
PROPOSTE = {'monotonia': 'alternare per emozione: frase breve dopo un colpo, periodo lungo dove il pensiero scorre (A)',
            'aperture': 'variare l\'attacco: sottintendere il soggetto, aprire con l\'azione o l\'oggetto (A, J)',
            'formule': 'sostituire la formula con un fatto percepibile (B, K, L, M)',
            'chiusure': 'variare la chiusura: azione, immagine o battuta (E)',
            'echi': 'cambiare o togliere una delle ripetizioni, salvo ripetizione voluta (F)',
            'coerenza': 'uniformare al sistema di dialogo e alla punteggiatura scelti (N)'}


def soglie(profilo, libro=None):
    s = dict(PREDEFINITI)
    s.update(profilo.get('anti_ia') or {})
    s.update((libro or {}).get('anti_ia') or {})
    return s


def formule():
    d = comune.leggi_yaml(os.path.join(comune.radice_motore(), FORMULE))
    return [(f['id'], f['sezione'], f['tipo'], re.compile(f['regex'], re.I | re.M)) for f in d['formule']]


def frasi_con_riga(prosa, lineetta):
    """[(riga, frase, è_dialogo)] spezzando ogni riga di prosa ai segni di fine frase."""
    out = []
    for n, r in prosa:
        dialogo = r.lstrip().startswith((lineetta, '«', '"', '“'))
        for f in re.split(r'(?<=[.!?…])\s+', r.strip()):
            if comune.parole(f):
                out.append((n, f, dialogo))
    return out


def prima_parola(frase):
    m = re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", frase)
    return m.group(0).lower() if m else ''


def radice(p):
    p = unicodedata.normalize('NFC', p.lower())
    for s in SUFFISSI:
        if p.endswith(s) and len(p) - len(s) >= 4:
            return p[:-len(s)]
    return p


def echi(prosa):
    """[(radice, [righe])] dei gruppi con la stessa radice almeno SOGLIA_ECO volte in FINESTRA parole piene."""
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
    # un gruppo per radice e per zona: niente doppioni sovrapposti
    unici, ultimo = [], {}
    for rad, righe in gruppi:
        if rad in ultimo and righe[0] <= ultimo[rad]:
            continue
        unici.append((rad, righe))
        ultimo[rad] = righe[-1]
    return unici


def chiusure_consecutive(cartella, libro, nome):
    """Numero di capitoli di fila, fino a `nome`, con la stessa chiusura dichiarata."""
    capitoli = [(n, comune.dichiarazioni_unita(open(p, encoding='utf-8').read()).get('chiusura'))
                for n, p in comune.unita(cartella, libro) if n.isdigit()]
    nomi = [n for n, _ in capitoli]
    if nome not in nomi:
        return 0, None
    idx = nomi.index(nome)
    val = capitoli[idx][1]
    if not val:
        return 0, None
    k = 0
    for _, c in reversed(capitoli[:idx + 1]):
        if c != val:
            break
        k += 1
    return k, val


def misura(cartella, libro, profilo, nome):
    """(metriche, audit, esiti): audit = [(riga, schema, dettaglio, proposta)]."""
    import stile
    lingua = comune.lingue()[libro['lingua']]
    testo = open(dict(comune.unita(cartella, libro))[nome], encoding='utf-8').read()
    prosa = comune.righe_prosa(testo)
    s = soglie(profilo, libro)
    frasi = frasi_con_riga(prosa, lingua['lineetta_dialogo'])
    lunghezze = [len(comune.parole(f)) for _, f, _ in frasi]
    parole = sum(len(comune.parole(r)) for _, r in prosa) or 1
    narrate = [(n, f) for n, f, d in frasi if not d]
    met = {'frasi': len(frasi), 'frase_dev': round(statistics.pstdev(lunghezze), 1) if len(lunghezze) > 1 else 0.0}
    aperture = {}
    for n, f in narrate:
        aperture.setdefault(prima_parola(f), []).append(n)
    top = max(aperture.items(), key=lambda kv: len(kv[1]), default=('', []))
    met['apertura_parola'], met['apertura_quota'] = top[0], round(len(top[1]) / len(narrate), 2) if narrate else 0.0
    audit, esiti = [], []
    trovate = []
    for fid, sez, tipo, rx in formule():
        for n, r in prosa:
            if tipo == 'formula' and r.lstrip().startswith((lingua['lineetta_dialogo'], '«')):
                continue
            for m in rx.finditer(r):
                trovate.append((n, fid, sez, tipo, m.group(0)[:60]))
    n_formule = sum(1 for x in trovate if x[3] == 'formula')
    met['formule_per_1000'] = round(1000 * n_formule / parole, 1)
    gruppi = echi(prosa)
    met['echi_per_1000'] = round(1000 * len(gruppi) / parole, 1)
    k, chiusura = chiusure_consecutive(cartella, libro, nome)
    met['chiusure_di_fila'] = k
    esito = 'KO' if s['modalita'] == 'blocco' else 'AVVISO'
    if len(lunghezze) >= s['apertura_min_frasi'] and met['frase_dev'] < s['frase_dev_min']:
        esiti.append(stile.risultato(nome, 'anti-ia:monotonia', esito, None,
                                     f'deviazione standard delle frasi {met["frase_dev"]} parole (minimo {s["frase_dev_min"]})'))
        audit.append((None, 'monotonia', f'frasi di lunghezza troppo simile (dev. {met["frase_dev"]})', PROPOSTE['monotonia']))
    if len(narrate) >= s['apertura_min_frasi'] and met['apertura_quota'] > s['apertura_max']:
        esiti.append(stile.risultato(nome, 'anti-ia:aperture', esito, top[1][0],
                                     f'{met["apertura_quota"]:.0%} delle frasi narrate comincia con «{top[0]}» '
                                     f'(massimo {s["apertura_max"]:.0%})'))
        audit += [(n, 'aperture', f'frase che comincia con «{top[0]}»', PROPOSTE['aperture']) for n in top[1][:10]]
    if met['formule_per_1000'] > s['formule_max_per_1000']:
        esiti.append(stile.risultato(nome, 'anti-ia:formule', esito, None,
                                     f'{met["formule_per_1000"]} formule ogni mille parole (massimo {s["formule_max_per_1000"]})'))
    if k > s['chiusura_max_consecutivi']:
        esiti.append(stile.risultato(nome, 'anti-ia:chiusure', esito, None,
                                     f'{k} capitoli di fila con chiusura={chiusura} (massimo {s["chiusura_max_consecutivi"]})'))
        audit.append((None, 'chiusure', f'{k} capitoli di fila chiudono con {chiusura}', PROPOSTE['chiusure']))
    if met['echi_per_1000'] > s['echi_max_per_1000']:
        esiti.append(stile.risultato(nome, 'anti-ia:echi', esito, gruppi[0][1][0] if gruppi else None,
                                     f'{met["echi_per_1000"]} gruppi di ripetizioni ogni mille parole (massimo {s["echi_max_per_1000"]})'))
    coerenza = [x for x in trovate if x[3] == 'coerenza']
    if coerenza:
        esiti.append(stile.risultato(nome, 'anti-ia:coerenza', 'AVVISO', coerenza[0][0],
                                     f'{len(coerenza)} segni tipografici all\'inglese (virgolette o trattini)'))
    audit += [(n, f'formula {fid} ({sez})', f'«{t}»', PROPOSTE['formule' if tipo == 'formula' else 'coerenza'])
              for n, fid, sez, tipo, t in trovate]
    audit += [(righe[0], 'echi', f'«{rad}…» alle righe {", ".join(map(str, righe))}', PROPOSTE['echi']) for rad, righe in gruppi]
    audit.sort(key=lambda a: (a[0] is None, a[0] or 0))
    return met, audit, esiti


def report(libro, nome, met, audit, s):
    righe = [f'# Anti-IA — unità {nome} (audit, non riscrive)', '',
             f'Misure: {met["frasi"]} frasi, deviazione standard {met["frase_dev"]} (min {s["frase_dev_min"]}); '
             f'apertura più frequente «{met["apertura_parola"]}» {met["apertura_quota"]:.0%} (max {s["apertura_max"]:.0%}); '
             f'formule {met["formule_per_1000"]}/1000 (max {s["formule_max_per_1000"]}); '
             f'ripetizioni {met["echi_per_1000"]}/1000 (max {s["echi_max_per_1000"]}); '
             f'chiusure uguali di fila {met["chiusure_di_fila"]} (max {s["chiusura_max_consecutivi"]}).', '',
             'Elenco per il line editor: posizione, schema, proposta. Si applica solo dopo l\'«ok» dell\'autore,',
             'con modifiche puntuali; una ripetizione o una formula voluta dalla voce resta.', '',
             '| Riga | Schema | Dove | Proposta |', '|---|---|---|---|']
    righe += [f'| {r or "—"} | {sch} | {det.replace("|", "/")} | {pro} |' for r, sch, det, pro in audit] or ['| — | — | nessuno | — |']
    return '\n'.join(righe) + '\n'


def esegui(cartella, libro, profilo, nome, scrivi=True):
    met, audit, esiti = misura(cartella, libro, profilo, nome)
    testo = report(libro, nome, met, audit, soglie(profilo, libro))
    if scrivi:
        nomefile = f'{int(nome):02d}' if nome.isdigit() else nome.replace(' ', '-')
        comune.scrivi(cartella, f'06-diagnostica/anti-ia/{nomefile}.md', testo)
    return met, esiti, testo


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2:
        raise comune.ErroreMotore('Uso: anti_ia.py <libro> <N> [--schermo]')
    cartella, libro, profilo = comune.carica_libro(args[0])
    nome = ' '.join(args[1:])
    met, esiti, testo = esegui(cartella, libro, profilo, nome, scrivi='--schermo' not in argv)
    print(testo if '--schermo' in argv else f'Anti-IA {nome}: {len(esiti)} segnalazioni; report in 06-diagnostica/anti-ia/.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

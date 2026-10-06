"""Controlli di continuità (proposta B.2.1).

Uso: python3 -B continuita.py <libro> [--schermo]
Legge <libro>/cronologia.yaml e controlla nel testo: giorni della settimana
(su calendario.anni_ammessi), età dei personaggi con data di nascita, durate
dichiarate in cronologia (nel testo e tra le date degli eventi, unità «cronologia»), cifre
(KO solo nelle righe con una parola di «contesto»; senza contesto AVVISO), nomi propri scritti
in due modi, ordine delle date.
Report: <libro>/06-diagnostica/continuita.md, con la tabella di tutte le durate
trovate e la checklist manuale per capitolo.
"""
import datetime
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
from stile import risultato  # noqa: E402

UNITA_NUM = {'zero': 0, 'un': 1, 'uno': 1, 'una': 1, 'due': 2, 'tre': 3, 'tré': 3, 'quattro': 4, 'cinque': 5,
             'sei': 6, 'sette': 7, 'otto': 8, 'nove': 9}
DIECI = {'dieci': 10, 'undici': 11, 'dodici': 12, 'tredici': 13, 'quattordici': 14, 'quindici': 15,
         'sedici': 16, 'diciassette': 17, 'diciotto': 18, 'diciannove': 19}
DECINE = [('novant', 90), ('ottant', 80), ('settant', 70), ('sessant', 60), ('cinquant', 50),
          ('quarant', 40), ('trent', 30), ('vent', 20)]
DURATA = re.compile(r"(?i)\b([\w']+)\s+(anni|anno|mesi|mese|settimane|settimana|giorni|giorno)\b")


def numero(tok):
    t = tok.lower().strip(".,;:!?«»\"()'")
    if t.isdigit():
        return int(t)
    if t in UNITA_NUM:
        return UNITA_NUM[t]
    if t in DIECI:
        return DIECI[t]
    for pref, val in DECINE:
        if t.startswith(pref):
            resto = t[len(pref):]
            if resto in ('', 'a', 'i'):
                return val
            resto = resto.lstrip('aei') if resto[:1] in 'aei' and resto[1:] in UNITA_NUM else resto
            if resto in UNITA_NUM or resto in ('uno', 'otto'):
                return val + UNITA_NUM.get(resto, 0)
    return None


def leva(a, b):
    """Distanza di modifica (Levenshtein)."""
    prec = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prec[j] + 1, cur[j - 1] + 1, prec[j - 1] + (ca != cb)))
        prec = cur
    return prec[-1]


def righe_con_date(testo):
    """Righe utili per le date: tutte tranne titoli «#» e commenti HTML."""
    out = []
    for n, r in enumerate(testo.splitlines(), 1):
        s = r.strip()
        if s and not s.startswith('#') and not s.startswith('<!--'):
            out.append((n, r))
    return out


class Calendario:
    def __init__(self, libro):
        lingua = comune.lingue()[libro['lingua']]
        self.mesi = {m: i + 1 for i, m in enumerate(lingua['mesi'])}
        self.giorni = lingua['giorni']
        self.anni = (libro.get('calendario') or {}).get('anni_ammessi') or []
        self.rx = re.compile(r'(?i)\b(' + '|'.join(self.giorni) + r')\s+(\d{1,2})\s+('
                             + '|'.join(self.mesi) + r')(?:\s+(\d{4}))?')

    def trova(self, riga):
        return list(self.rx.finditer(riga))

    def risolvi(self, m):
        """(data, errore): la data con l'anno ammesso che dà quel giorno della settimana."""
        giorno, g, mese, anno = m.group(1).lower(), int(m.group(2)), self.mesi[m.group(3).lower()], m.group(4)
        anni = [int(anno)] if anno else self.anni
        for a in anni:
            try:
                d = datetime.date(a, mese, g)
            except ValueError:
                continue
            if self.giorni[d.weekday()] == giorno:
                return d, None
        if not anni:
            return None, None
        try:
            d = datetime.date(anni[0], mese, g)
            vero = self.giorni[d.weekday()]
        except ValueError:
            return None, f'data inesistente: {m.group(0)}'
        return d, f'«{m.group(0)}»: nel {anni[0]} il {g} {m.group(3)} è {vero}'


def eta(nascita, data):
    return data.year - nascita.year - ((data.month, data.day) < (nascita.month, nascita.day))


GIORNI_UNITA = {'giorn': 1, 'settiman': 7, 'mes': 30.44, 'ann': 365.25}


def giorni_dichiarati(valore):
    """«sei settimane» -> 42; «tre anni, quasi quattro» -> 1096 (prima cifra e prima unità)."""
    parti = valore.replace(',', ' ').split()
    if len(parti) < 2 or numero(parti[0]) is None:
        return None
    for pref, g in GIORNI_UNITA.items():
        if parti[1].lower().startswith(pref):
            return numero(parti[0]) * g
    return None


def tolleranza_giorni(du):
    """Tolleranza di una durata della cronologia: tolleranza_giorni, oppure _mesi o _anni come prima."""
    return (du.get('tolleranza_giorni') or 0) + (du.get('tolleranza_mesi') or 0) * 30.44 \
        + (du.get('tolleranza_anni') or 0) * 365.25


def _numero_enne(parola):
    """«trentaquattrenne» -> 34, «ventenne» -> 20, «diciottenne» -> 18."""
    base = parola.lower()[:-4]
    for fine in ('', 'o', 'e', 'i', 'a'):
        k = numero(base + fine)
        if k is not None:
            return k
    return None


def eta_nella_frase(frase, nascite):
    """[(chi, anni, forma, certo)] con le sole forme dichiarative dell'età attuale.

    KO (certo): «Nome ha N anni», «Nome, di N anni», «Nome … ha N anni» (soggetto = nome più vicino prima).
    AVVISO (incerto): «Nome aveva N anni» nella proposizione principale (imperfetto narrativo), «N-enne»
    con più nomi, «ha N anni» senza un nome prima.
    Ignorate: «quando/da quando/fin da quando … aveva N anni», «a N anni», «da N anni», «per N anni»."""
    pos = []
    for chi in nascite:
        for m in re.finditer(r'\b(' + re.escape(chi) + '|' + re.escape(chi.split()[0]) + r')\b', frase):
            pos.append((m.start(), m.end(), chi))
    if not pos:
        return []
    pos.sort()

    def prima(i):
        cand = [p for p in pos if p[1] <= i]
        return cand[-1] if cand else None

    out = []
    for m in re.finditer(r"(?i)\b(ha|compie|compirà)\s+(\w+)(?:\s+|['’])anni\b", frase):
        k = numero(m.group(2))
        if k is None:
            continue
        p = prima(m.start())
        if p:
            out.append((p[2], k, m.group(0), True))
        else:
            out.append((pos[0][2], k, m.group(0), False))
    for m in re.finditer(r"(?i)\b(aveva|avevi|avevo)\s+(\w+)(?:\s+|['’])anni\b", frase):
        k = numero(m.group(2))
        if k is None:
            continue
        prec = frase[:m.start()]
        if re.search(r"(?i)\b(quando|da quando|fin da quando|ricord\w*|allora)\b[^,;:]*$", prec):
            continue                                  # ricordo: età di allora, non attuale
        p = prima(m.start())
        if p and frase[p[1]:m.start()].strip(' ,') == '' or (p and len(frase[p[1]:m.start()].split()) <= 2):
            out.append((p[2], k, m.group(0), False))  # «Nome aveva N anni»: imperfetto narrativo, nel dubbio avviso
    for m in re.finditer(r"(?i)\b([\w']+)\s*,?\s+di\s+(\w+)(?:\s+|['’])anni\b", frase):
        k = numero(m.group(2))
        p = prima(m.start(2))
        if k is not None and p and len(frase[p[1]:m.start(2)].split()) <= 2:
            out.append((p[2], k, m.group(0).split(None, 1)[1] if m.group(1) not in [x[2] for x in pos] else m.group(0), True))
    for m in re.finditer(r"(?i)\b(\w+enne)\b", frase):
        k = _numero_enne(m.group(1))
        if k is None:
            continue
        vicini = sorted(pos, key=lambda p: min(abs(p[0] - m.end()), abs(p[1] - m.start())))
        certo = len({p[2] for p in pos}) == 1
        out.append((vicini[0][2], k, m.group(1), certo))
    return out


def controlla_libro(cartella, libro):
    cron = comune.leggi_yaml(os.path.join(cartella, 'cronologia.yaml')) if os.path.isfile(
        os.path.join(cartella, 'cronologia.yaml')) else {}
    cron = cron or {}
    cal = Calendario(libro)
    nascite = {n['chi']: n['data'] for n in cron.get('nascite') or []}
    eventi = {e['id']: e['data'] for e in cron.get('eventi') or []}
    pn = os.path.join(cartella, (libro.get('ortografia') or {}).get('parole_ammesse_file') or 'nomi_propri.txt')
    nomi = [r.strip() for r in open(pn, encoding='utf-8')] if os.path.isfile(pn) else []
    nomi = [n for n in nomi if n and not n.startswith('#')]
    scaletta = {r.get('Unità', '').lower(): r for r in
                comune.tabella_md(os.path.join(cartella, '03-architettura', 'scaletta.md'))}
    risultati, durate_trovate, date_unita = [], [], []
    for nome, p in comune.unita(cartella, libro):
        testo = open(p, encoding='utf-8').read()
        righe = righe_con_date(testo)
        prosa = comune.righe_prosa(testo)
        data_unita = None
        # giorni della settimana
        for n, r in righe:
            for m in cal.trova(r):
                d, err = cal.risolvi(m)
                if err:
                    risultati.append(risultato(nome, 'giorno_settimana', 'KO', n, err))
                if d and data_unita is None:
                    data_unita = d
        if data_unita is None and nome in scaletta:
            m = cal.rx.search(scaletta[nome].get('Data', ''))
            if m:
                data_unita = cal.risolvi(m)[0]
        date_unita.append((nome, data_unita))
        # età (solo forme dichiarative; vedi eta_nella_frase)
        unito = ' '.join(r.strip() for _, r in prosa)
        if data_unita:
            for frase in re.split(r'(?<=[.!?…])\s+', unito):
                for chi, k, forma, certo in eta_nella_frase(frase, nascite):
                    vera = eta(nascite[chi], data_unita)
                    if abs(k - vera) > 1:
                        riga = next((n for n, r in prosa if forma in r), None)
                        risultati.append(risultato(nome, 'eta', 'KO' if certo else 'AVVISO', riga,
                                                   f'{chi}: «{forma}», ma al {data_unita} ne ha {vera}'
                                                   + ('' if certo else ' (attribuzione o tempo incerti: da verificare)')))
        # durate (tabella) e durate della cronologia
        for n, r in prosa:
            for m in DURATA.finditer(r):
                if numero(m.group(1)) is not None:
                    durate_trovate.append((nome, n, m.group(0)))
        for du in cron.get('durate') or []:
            for n, r in prosa:
                if du['valore'].lower() in r.lower():
                    dichiarati = giorni_dichiarati(du['valore'])
                    if dichiarati is None:
                        continue
                    calcolati = (eventi[du['a']] - eventi[du['da']]).days
                    if abs(calcolati - dichiarati) > tolleranza_giorni(du):
                        risultati.append(risultato(nome, 'durata', 'KO', n,
                                                   f'«{du["valore"]}»: dalle date risultano {calcolati} giorni '
                                                   f'({calcolati / 365.25:.1f} anni); tolleranza {tolleranza_giorni(du):.0f} giorni'))
        # cifre: con «contesto» si controllano solo le righe che contengono una di quelle parole (KO);
        # senza, un numero diverso vicino all'unità è solo un AVVISO (può parlare d'altro)
        for ci in cron.get('cifre') or []:
            contesto = [c.lower() for c in ci.get('contesto') or []]
            for n, r in prosa:
                if contesto and not any(c in r.lower() for c in contesto):
                    continue
                toks = r.split()
                for i, t in enumerate(toks):
                    if t.lower().strip('.,;:!?') != ci['unita'].lower():
                        continue
                    vicini = toks[i + 1:i + 4] + list(reversed(toks[max(0, i - 2):i]))
                    for v in vicini:
                        k = numero(v)
                        if k is not None:
                            if k != ci['valore']:
                                risultati.append(risultato(
                                    nome, f'cifra:{ci["id"]}', 'KO' if contesto else 'AVVISO', n,
                                    f'«{v} {ci["unita"]}», atteso {ci["valore"]}'
                                    + ('' if contesto else ' (senza «contesto» in cronologia.yaml: verifica '
                                       'che la frase parli di questa cifra)')))
                            break
        # nomi in due grafie
        visti = set()
        for n, r in prosa:
            for t in re.findall(r"\b[A-ZÀ-Ý][a-zà-ÿ]+\b", r):
                if t in nomi or t in visti:
                    continue
                for nm in nomi:
                    if len(t) >= 5 and t[0] == nm[0] and leva(t, nm) == 1:
                        visti.add(t)
                        risultati.append(risultato(nome, 'nome_due_grafie', 'AVVISO', n, f'«{t}» e «{nm}»'))
                        break
    # durate della cronologia confrontate con le date degli eventi, anche se il testo non le nomina
    for du in cron.get('durate') or []:
        dichiarati = giorni_dichiarati(du['valore'])
        if dichiarati is None or du['da'] not in eventi or du['a'] not in eventi:
            continue
        calcolati = (eventi[du['a']] - eventi[du['da']]).days
        if abs(calcolati - dichiarati) > tolleranza_giorni(du):
            risultati.append(risultato('cronologia', 'durata', 'KO', None,
                                       f'«{du["valore"]}» da {du["da"]} a {du["a"]}: dalle date risultano {calcolati} '
                                       f'giorni; tolleranza {tolleranza_giorni(du):.0f} giorni'))
    # ordine delle date
    prec = None
    for nome, d in date_unita:
        if d and prec and d < prec[1]:
            risultati.append(risultato(nome, 'ordine_date', 'AVVISO', None, f'{d} prima di {prec[1]} ({prec[0]})'))
        if d:
            prec = (nome, d)
    return risultati, durate_trovate, date_unita


def voci_toccate(cartella, libro, nome_unita):
    """Voci in grassetto della bibbia che compaiono nell'unità."""
    pb = os.path.join(cartella, '02-bibbia', 'bibbia.md')
    voci = re.findall(r'\*\*([^*]+)\*\*', open(pb, encoding='utf-8').read()) if os.path.isfile(pb) else []
    voci = [v for v in voci if v.lower() != 'oggetti']
    testo = open(dict(comune.unita(cartella, libro))[nome_unita], encoding='utf-8').read()
    toccate = []
    for v in voci:
        parti = v.split()
        chiave = parti[-1] if parti[0].lower() in ('signora', 'signor', 'don', 'dottor', 'zia', 'zio') else parti[0]
        if v in testo or re.search(r'\b' + re.escape(chiave) + r'\b', testo):
            toccate.append(v)
    return toccate


def checklist(cartella, libro):
    righe = ['| Unità | Voci della bibbia toccate | Verificato dall\'autore |', '|---|---|---|']
    for nome, _ in comune.unita(cartella, libro):
        righe.append(f'| {nome} | {", ".join(voci_toccate(cartella, libro, nome)) or "—"} | [ ] |')
    return righe


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: continuita.py <libro> [--schermo]')
    cartella, libro, _ = comune.carica_libro(args[0])
    risultati, durate, date_unita = controlla_libro(cartella, libro)
    from stile import tabella
    righe = ['# Continuità', '', f'Libro: {libro["titolo"]}.', '', '## Esiti', '']
    righe += tabella(risultati) if risultati else ['Nessun KO e nessun avviso.']
    righe += ['', '## Date delle unità', '', '| Unità | Data |', '|---|---|']
    righe += [f'| {n} | {d or "—"} |' for n, d in date_unita]
    righe += ['', '## Tutte le durate trovate nel testo', '', '| Unità | Riga | Testo |', '|---|---|---|']
    righe += [f'| {u} | {n} | {t} |' for u, n, t in durate] or ['| — | — | — |']
    righe += ['', '## Checklist manuale', '',
              'Da verificare a mano: oggetti e persone in scena, chi sa cosa, distanze e tempi di '
              'spostamento, tempo interno della scena, età e durate dette in modo indiretto, ferite '
              'e segni da un capitolo all\'altro.', ''] + checklist(cartella, libro) + ['']
    testo = '\n'.join(righe)
    if '--schermo' in argv:
        print(testo)
    else:
        print('scritto', comune.scrivi(cartella, '06-diagnostica/continuita.md', testo))
    return 1 if any(r['esito'] == 'KO' for r in risultati) else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

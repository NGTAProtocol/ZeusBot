"""Adotta nel motore un libro già avviato (passo 5b).

Uso: python3 -B adotta.py <cartella-del-libro> [--titolo «titolo»]
Per un libro con alcuni documenti già scritti (briefing, manuale di stile, bibbia, scaletta,
piano parole, cronologia) genera in BOZZA libro.yaml, stato.yaml, cronologia.yaml e
nomi_propri.txt, ricavando i valori dai documenti e dal profilo di genere.
- Ogni valore ha la sua fonte (file e riga) in 06-diagnostica/adozione.md.
- Se un documento diverge dal profilo, il valore va in libro.yaml come override con motivo.
- Non sovrascrive mai un file esistente; scrive solo nella cartella indicata.
- In adozione.md elenca ciò che non ha potuto ricavare.
- Se il titolo non si ricava dai documenti si ferma senza scrivere nulla e lo chiede (--titolo).
- Si ferma alla fase «documenti»: apre il gate se tutti i documenti ci sono, altrimenti dice cosa manca.
Riconosce le righe nel formato dei documenti del motore (vedi PROCEDURA.md, «zb adotta»).
"""
import datetime
import os
import re
import sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import nuovo  # noqa: E402
import revisione  # noqa: E402

DOC = {'briefing': '00-progetto/briefing.md', 'manuale': '03-architettura/manuale-di-stile.md',
       'bibbia': '02-bibbia/bibbia.md', 'scaletta': '03-architettura/scaletta.md',
       'piano': '03-architettura/piano-parole.md', 'cronologia': 'cronologia.yaml'}
GENERATI = ['libro.yaml', 'stato.yaml', 'cronologia.yaml', 'nomi_propri.txt', '06-diagnostica/adozione.md']
DATA = r'(\d{4}-\d{2}-\d{2})'


class Raccolta:
    """Valori ricavati con la loro fonte, e voci non ricavate."""

    def __init__(self, cartella):
        self.cartella = cartella
        self.fonti, self.mancano = [], []
        self.righe = {}
        for k, rel in DOC.items():
            p = os.path.join(cartella, rel)
            self.righe[k] = open(p, encoding='utf-8').read().splitlines() if os.path.isfile(p) else None

    def cerca(self, doc, regex, flags=re.I):
        for n, r in enumerate(self.righe.get(doc) or [], 1):
            m = re.search(regex, r, flags)
            if m:
                return m, f'{DOC[doc]}:{n}'
        return None, None

    def primo(self, campo, prove):
        """prove: [(doc, regex, funzione)]; il primo che trova vince."""
        for doc, regex, f in prove:
            m, fonte = self.cerca(doc, regex)
            if m:
                v = f(m)
                self.fonti.append((campo, v, fonte))
                return v
        self.mancano.append(campo)
        return None

    def tutti(self, doc, regex):
        out = []
        for n, r in enumerate(self.righe.get(doc) or [], 1):
            for m in re.finditer(regex, r):
                out.append((m, f'{DOC[doc]}:{n}'))
        return out


def ricava(cartella, titolo_dato=None):
    R = Raccolta(cartella)
    presenti = [k for k in DOC if R.righe[k] is not None]
    if not presenti:
        raise comune.ErroreMotore(f'Nessun documento da adottare in {cartella} (cerco: {", ".join(DOC.values())})')
    g1 = lambda m: m.group(1).strip()
    titolo = R.primo('titolo', [('briefing', r'^Titolo di lavoro:\s*(\S.*)$', g1),
                                ('manuale', r'^#\s*Manuale di stile\s*—\s*(.+)$', g1),
                                ('bibbia', r'^#\s*Bibbia\s*—\s*(.+)$', g1),
                                ('scaletta', r'^#\s*Scaletta\s*—\s*(.+)$', g1)])
    if titolo is None and titolo_dato:
        R.mancano.remove('titolo')
        titolo = titolo_dato
        R.fonti.append(('titolo', titolo, 'indicato con --titolo'))
    autore = R.primo('autore', [('briefing', r'^Autore:\s*(\S.*)$', g1), ('manuale', r'^Autore:\s*(\S.*)$', g1)])
    genere = R.primo('profilo', [('briefing', r'^Genere:\s*([\w-]+)', g1), ('manuale', r'^Genere:\s*([\w-]+)', g1),
                                 ('manuale', r'profilo «([\w-]+)»', g1)])
    if genere and not os.path.isfile(os.path.join(comune.radice_motore(), 'profili', f'{genere}.yaml')):
        R.mancano.append(f'profilo («{genere}» non esiste in motore/profili/)')
        genere = None
    numero = lambda m: int(re.sub(r'\D', '', m.group(1)))
    target = R.primo('parole.target_totale', [('briefing', r'^Lunghezza[^:]*:\s*([\d.]+)', numero),
                                              ('manuale', r'Obiettivo:\s*([\d.]+)\s*parole', numero),
                                              ('piano', r'^Totale:\s*([\d.]+)', numero)])
    originale = os.path.join(cartella, '01-originale')
    precedenti = sorted(f for f in os.listdir(originale) if f.endswith('.md')) if os.path.isdir(originale) else []
    modalita = R.primo('modalita', [('briefing', r'^Modalità:\s*(nuovo|riscrittura)', g1)])
    if modalita is None and precedenti:
        R.mancano.remove('modalita')
        modalita = 'riscrittura'
        R.fonti.append(('modalita', modalita, '01-originale/ (cartella presente)'))
    elif modalita is None:
        R.mancano.remove('modalita')
        modalita = 'nuovo'
        R.fonti.append(('modalita', modalita, 'predefinito: nessun 01-originale'))

    profilo = comune.carica_profilo(genere) if genere else None
    override = []

    def confronta(campo, valore, fonte, attuale):
        if valore is None or profilo is None:
            return
        if valore != attuale:
            override.append({'campo': campo, 'valore': valore,
                             'motivo': f'{fonte} dice {valore}; il profilo «{genere}» dice {attuale}'})

    for campo, regex, conv in (
            ('frase_media', r'Frase media:\s*(\d+)\s*-\s*(\d+)', lambda m: [int(m.group(1)), int(m.group(2))]),
            ('dialogo_percento', r'Dialogo:\s*(\d+)\s*-\s*(\d+)\s*%', lambda m: [int(m.group(1)), int(m.group(2))]),
            ('similitudini_max_per_parole', r'una ogni\s+(\d+)\s+parole', lambda m: int(m.group(1))),
            ('capitoli.minimo', r'Capitolo:\s*minimo\s+(\d+)', lambda m: int(m.group(1))),
            # solo dalla riga «Capitolo:»: «frase media 10-13» o «al massimo 150 parole» altrove non sono capitoli
            ('capitoli.media', r'Capitolo:.*\bmedia\s+(\d+)\s*-\s*(\d+)', lambda m: [int(m.group(1)), int(m.group(2))]),
            ('capitoli.massimo', r'Capitolo:.*\bmassimo\s+(\d+)\s+parole', lambda m: int(m.group(1)))):
        m, fonte = R.cerca('manuale', regex)
        if m:
            v = conv(m)
            R.fonti.append((f'stile.{campo}', v, fonte))
            att = profilo
            for k in campo.split('.'):
                att = (att or {}).get(k) if isinstance(att, dict) else None
            confronta(campo, v, fonte, att)

    voci = []
    for m, fonte in R.tutti('manuale', r'Tetto:\s*«([^»]+)»\s*al massimo\s+(\d+)\s+per\s+(capitolo|libro)'):
        voci.append({'id': nuovo.slug(m.group(1)), 'pattern': r'(?i)(?<!\w)' + re.escape(m.group(1)) + r'(?!\w)',
                     'modalita': 'conta', 'massimo': int(m.group(2)), 'ambito': m.group(3)})
        R.fonti.append((f'voci.{voci[-1]["id"]}', f'tetto {m.group(2)} per {m.group(3)}', fonte))
    for m, fonte in R.tutti('manuale', r'Vietato:\s*«([^»]+)»'):
        voci.append({'id': nuovo.slug(m.group(1))[:40], 'pattern': r'(?i)(?<!\w)' + re.escape(m.group(1)) + r'(?!\w)',
                     'modalita': 'vieta'})
        R.fonti.append((f'voci.{voci[-1]["id"]}', 'vietato', fonte))
    nomi_vincolo = []
    for m, fonte in R.tutti('manuale', r'«([^»]+)»\s*non compare nei capitoli\s+([\d\-, ]+)'):
        elenco = [x.strip() for x in m.group(2).split(',') if x.strip()]
        nomi_vincolo.append({'nome': m.group(1), 'pattern': r'\b' + re.escape(m.group(1)) + r'\b',
                             'vietato_in': elenco, 'obbligatorio_in': []})
        R.fonti.append((f'nome_vietato_prima_di.{m.group(1)}', elenco, fonte))
    sep = R.primo('struttura.separatore_scena', [('manuale', r'Separatore di scena:\s*«([^»]+)»', g1),
                                                 ('briefing', r'^Separatore di scena:\s*(\S.*)$', g1)])
    intest = R.primo('struttura.intestazione_capitolo', [('manuale', r'Intestazione del capitolo:\s*«([^»]+)»', g1),
                                                         ('briefing', r'^Intestazione capitolo:\s*(\S.*)$', g1)])

    # cronologia e nomi
    trovate = R.tutti('bibbia', r'\*\*([^*]+)\*\*.*?\bnat[oa] il\s+' + DATA)
    nascite = [{'chi': m.group(1), 'data': m.group(2)} for m, _ in trovate]
    eventi = []
    for m, fonte in R.tutti('scaletta', r'^\|\s*(\d+)\s*\|\s*' + DATA + r'\s*\|\s*([^|]*)\|'):
        eventi.append({'id': f'capitolo_{m.group(1)}', 'data': m.group(2), 'capitolo': int(m.group(1)),
                       'descrizione': m.group(3).strip()})
    for m, fonte in trovate:
        R.fonti.append((f'cronologia.nascite.{m.group(1)}', m.group(2), fonte))
    for m, fonte in R.tutti('scaletta', r'^\|\s*(\d+)\s*\|\s*' + DATA):
        R.fonti.append((f'cronologia.eventi.capitolo_{m.group(1)}', m.group(2), fonte))
    nomi = sorted({w for m, _ in R.tutti('bibbia', r'\*\*([^*]+)\*\*') for w in m.group(1).split() if w[:1].isupper()})
    if not nomi:
        R.mancano.append('nomi_propri (nessun nome in grassetto nella bibbia)')
    anni = sorted({int(e['data'][:4]) for e in eventi})

    sigle = nuovo.SIGLE[profilo['chiusura_preferita']] if profilo else None
    if profilo is None:
        R.mancano.append('dichiarazioni.chiusura (serve il profilo)')
    libro = {'titolo': titolo, 'sottotitolo': None, 'autore': autore, 'lingua': 'it', 'modalita': modalita}
    if modalita == 'riscrittura':
        libro['testo_precedente'] = f'01-originale/{precedenti[0]}' if precedenti else None
        if not precedenti:
            R.mancano.append('testo_precedente (nessun .md in 01-originale/)')
    libro.update({
        'serie': None, 'ebook': False, 'profilo': genere, 'override': override, 'gate': nuovo.GATE_PREDEFINITI,
        'parole': {'metodo': 'unico', 'target_totale': target},
        'formato': {'pagina_pollici': [5.5, 8.5], 'carta': 'crema', 'bleed': False,
                    'margini_mm': {'alto': 20, 'basso': 20, 'esterno': 16, 'interno_scelto': 16},
                    'font': {'nome': 'EB Garamond', 'corpo_pt': 11.5, 'interlinea': 1.5},
                    'numerazione': {'da': 'capitolo_1', 'pagine_iniziali': 'senza_numero', 'posizione': 'piede_centro'}},
        'voci': voci, 'vincoli_capitolo': [], 'nome_vietato_prima_di': nomi_vincolo,
        'dichiarazioni': {'chiusura': {'sigle': sigle, 'prevista_da': 'scaletta'}},
        'struttura': {'separatore_scena': {'sorgente': sep or '* * *', 'stampa': sep or '* * *'},
                      'intestazione_capitolo': intest or 'Luogo — giorno e data', 'parti': [], 'interludi': []},
        'calendario': {'anni_ammessi': anni},
        'ortografia': {'parole_ammesse_file': 'nomi_propri.txt'},
        'copyright': {'riga': '© {anno} {autore}. Tutti i diritti riservati.', 'anno': datetime.date.today().year,
                      'fantasia': "Quest'opera è frutto di fantasia. Nomi, personaggi, luoghi e fatti sono invenzione "
                                  "dell'autore o usati in modo fittizio; ogni somiglianza con persone, vive o scomparse, "
                                  "o con fatti realmente accaduti è puramente casuale.",
                      'nota_autore': None},
    })
    R.mancano += ['formato (predefinito 5.5 x 8.5: da confermare)', 'copyright.fantasia (testo standard: da confermare)']
    if not anni:
        R.mancano.append('calendario.anni_ammessi (nessuna data in scaletta)')
    cron = {'nascite': nascite, 'eventi': eventi, 'durate': [], 'cifre': [], 'eta_per_capitolo': {'calcolata': True}}
    return R, libro, cron, nomi, presenti


def adotta(percorso, titolo=None):
    cartella = os.path.realpath(percorso)
    if not os.path.isdir(cartella):
        raise comune.ErroreMotore(f'Cartella inesistente: {percorso}')
    R, libro, cron, nomi, presenti = ricava(cartella, titolo)
    if not libro['titolo']:
        raise comune.ErroreMotore('Titolo non trovato nei documenti (briefing «Titolo di lavoro:», oppure '
                                  '«# Manuale di stile — <titolo>», «# Bibbia — <titolo>», «# Scaletta — <titolo>»). '
                                  'Non ho scritto nulla. Qual è il titolo? Indicalo così: '
                                  'zb adotta <cartella> --titolo "<titolo>"')
    scritti, esistenti = [], []

    def scrivi(rel, testo):
        if os.path.exists(os.path.join(cartella, rel)):
            esistenti.append(rel)
        else:
            comune.scrivi(cartella, rel, testo)
            scritti.append(rel)

    intest = '# BOZZA generata da «zb adotta»: ogni valore ha la fonte in 06-diagnostica/adozione.md.\n'
    scrivi('libro.yaml', intest + yaml.safe_dump(libro, sort_keys=False, allow_unicode=True, width=120))
    if True:
        scrivi('cronologia.yaml', '# BOZZA da «zb adotta» (date dalla scaletta, nascite dalla bibbia).\n'
               + yaml.safe_dump(cron, sort_keys=False, allow_unicode=True))
    scrivi('nomi_propri.txt', '\n'.join(nomi) + '\n' if nomi else '')
    stato = comune.leggi_yaml(os.path.join(comune.radice_motore(), 'modelli', 'stato.yaml'))
    docs = revisione.DOCUMENTI
    mancanti_doc = [d for d in docs if not os.path.isfile(os.path.join(cartella, d)) and d not in GENERATI]
    capitoli = [int(n) for n, _ in comune.unita(cartella, libro) if n.isdigit()] if os.path.isdir(
        os.path.join(cartella, '04-manoscritto')) else []
    stato.update({'libro': libro['titolo'], 'fase': 'documenti', 'motore_commit': None,
                  'passo': 'adozione: bozze da approvare' if not mancanti_doc else
                  'adozione: mancano ' + ', '.join(mancanti_doc),
                  'gate_in_attesa': 'documenti' if not mancanti_doc else None,
                  'ultimo_capitolo_scritto': max(capitoli) if capitoli else None,
                  'parole': {'scritte': 0, 'obiettivo': libro['parole']['target_totale'] or 0, 'metodo': 'unico'},
                  'aggiornato': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})
    scrivi('stato.yaml', yaml.safe_dump(stato, sort_keys=False, allow_unicode=True))
    valido = 'sì'
    if 'libro.yaml' in scritti:
        try:
            comune.carica_libro(cartella)
        except comune.ErroreMotore as e:
            valido = 'no — ' + str(e).replace('\n', ' ')
    righe = [f'# Adozione — {libro["titolo"] or "(titolo non ricavato)"}', '',
             'Bozze generate da `zb adotta`. Niente è approvato: si approva al gate «documenti».', '',
             f'Documenti letti: {", ".join(DOC[k] for k in presenti)}.',
             f'File scritti: {", ".join(scritti) or "nessuno"}.',
             f'File già presenti, non toccati: {", ".join(esistenti) or "nessuno"}.',
             f'libro.yaml valido: {valido}.', '', '## Valori e fonti', '',
             '| Campo | Valore | Fonte (file:riga) |', '|---|---|---|']
    righe += [f'| {c} | {v} | {f} |' for c, v, f in R.fonti]
    righe += ['', '## Override rispetto al profilo', '']
    righe += [f'- {o["campo"]}: {o["valore"]} — {o["motivo"]}' for o in libro['override']] or ['- nessuno']
    righe += ['', '## Non ricavato (da completare a mano)', '']
    righe += [f'- {m}' for m in R.mancano] or ['- niente']
    righe += [f'- documento mancante: {d}' for d in mancanti_doc]
    righe += ['', '## Prossimo passo', '',
              'Gate «documenti» aperto: avanti, ok o correggi.' if not mancanti_doc else
              'Completa i documenti mancanti, poi «zb pronto <libro>» apre il gate «documenti».']
    scrivi('06-diagnostica/adozione.md', '\n'.join(righe) + '\n')
    return scritti, esistenti, R.mancano + [f'documento mancante: {d}' for d in mancanti_doc], valido


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: adotta.py <cartella-del-libro> [--titolo «titolo»]')
    titolo = argv[argv.index('--titolo') + 1] if '--titolo' in argv and argv.index('--titolo') + 1 < len(argv) else None
    scritti, esistenti, mancano, valido = adotta(args[0], titolo)
    for s in scritti:
        print(f'scritto: {s}')
    for e in esistenti:
        print(f'già presente, non toccato: {e}')
    for m in mancano:
        print(f'non ricavato: {m}')
    print(f'libro.yaml valido: {valido}')
    print('Fermo alla fase «documenti». Dettagli e fonti: 06-diagnostica/adozione.md')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

"""Crea un libro dal briefing (proposta B.4, C.1 fase «documenti», C.3).

Uso: python3 -B nuovo.py <percorso-briefing>
- Il libro è <x> se il briefing sta in <x>/00-progetto/briefing.md; altrimenti è la cartella
  del briefing, e il briefing viene spostato in 00-progetto/briefing.md.
- Si ferma se c'è già un libro.yaml, o se il briefing è incompleto (elenca cosa manca, al massimo
  5 domande): in quel caso non crea nulla.
- Dal briefing (sezione «Direttive») e dal profilo di genere genera: libro.yaml, stato.yaml,
  LEGGIMI.md, cronologia.yaml, nomi_propri.txt, 02-bibbia/bibbia.md,
  03-architettura/manuale-di-stile.md, scaletta.md, piano-parole.md, e le cartelle standard.
  Le regole (tetti, vietati, vincoli, lunghezze, chiusure) vanno in libro.yaml e nel manuale
  senza riscriverle a mano; i contenuti narrativi li scrive Claude Code al gate «documenti».
Legge solo motore/ e la cartella del libro.
"""
import datetime
import os
import re
import sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

GATE_PREDEFINITI = ['documenti', 'pagina_campione', 'primi_capitoli']
SIGLE = {'gancio_domanda': ['D', 'R', 'P', 'X'], 'gesto_oggetto': ['G', 'O', 'B', 'I'],
         'misto': ['G', 'O', 'B', 'D', 'R']}
SIGNIFICATO_SIGLE = {'G': 'gesto', 'O': 'oggetto', 'B': 'battuta', 'D': 'domanda', 'R': 'rivelazione',
                     'P': 'pericolo', 'X': 'decisione', 'I': 'immagine'}


def sigle_spiegate(sigle):
    """[G, O, B] -> «G gesto, O oggetto, B battuta»."""
    return ', '.join(f'{s} {SIGNIFICATO_SIGLE.get(s, "?")}' for s in sigle)


SEGNAPOSTO = 'Nome — ruolo — età — una riga'


# ---------------------------------------------------------------- briefing

def leggi_briefing(percorso):
    testo = re.sub(r'<!--.*?-->', '', open(percorso, encoding='utf-8').read(), flags=re.S)
    campi, sezioni, liste = {}, {}, {}
    sezione, lista = None, None
    for riga in testo.splitlines():
        s = riga.strip()
        if s.startswith('## '):
            sezione = s[3:].split('(')[0].strip().lower()
            sezioni[sezione] = []
            lista = None
            continue
        m = re.match(r'^([A-Za-zÀ-ÿ\' ]+):\s*(.*)$', s)
        if m and not s.startswith('-'):
            chiave = m.group(1).strip().lower()
            campi[chiave] = m.group(2).strip()
            lista = chiave if not m.group(2).strip() else None
            if lista:
                liste[lista] = []
            continue
        if s.startswith('-') and lista:
            v = s.lstrip('-').strip()
            if v:
                liste[lista].append(v)
            continue
        if sezione is not None and s and not s.startswith('#'):
            sezioni[sezione].append(s)
    personaggi = [p.lstrip('-').strip() for p in sezioni.get('personaggi chiave', [])
                  if p.startswith('-') and p.lstrip('-').strip() and p.lstrip('-').strip() != SEGNAPOSTO]
    elenco = lambda nome: [x.lstrip('-').strip() for x in sezioni.get(nome, []) if x.lstrip('-').strip()]
    return {'campi': campi, 'liste': liste, 'idea': sezioni.get('idea', []),
            'tono': sezioni.get('tono e voce desiderati', []), 'personaggi': personaggi,
            'fatti': elenco('fatti canonici'), 'non_cambiare': elenco('cose da non cambiare'),
            'riferimenti': elenco('riferimenti')}


def mancanze(b, cartella_libro):
    """Voci obbligatorie mancanti o non valide (C.3), come domande per l'autore."""
    c = b['campi']
    out = []
    if not c.get('titolo di lavoro'):
        out.append('Titolo di lavoro: manca')
    if not c.get('autore'):
        out.append('Autore: manca')
    g = c.get('genere', '')
    if not g:
        out.append('Genere: manca (un profilo di motore/profili/)')
    elif not os.path.isfile(os.path.join(comune.radice_motore(), 'profili', f'{g}.yaml')):
        out.append(f'Genere: profilo «{g}» inesistente in motore/profili/')
    lung = re.sub(r'[^\d]', '', c.get('lunghezza', ''))
    if not lung:
        out.append('Lunghezza: manca (numero di parole)')
    elif g and os.path.isfile(os.path.join(comune.radice_motore(), 'profili', f'{g}.yaml')):
        out += override_dal_briefing(c, comune.carica_profilo(g))[1]
    if not 1 <= len(b['idea']) <= 5:
        out.append(f'Idea: servono da 1 a 5 righe (ora {len(b["idea"])})')
    if not any('—' in p for p in b['personaggi']):
        out.append('Personaggi chiave: almeno uno, nella forma «Nome — ruolo — …»')
    mod = c.get('modalità', 'nuovo') or 'nuovo'
    if mod not in ('nuovo', 'riscrittura'):
        out.append(f'Modalità: «{mod}» non ammessa (nuovo | riscrittura)')
    if mod == 'riscrittura':
        tp = c.get('testo precedente', '')
        if not tp:
            out.append('Testo precedente: obbligatorio con Modalità: riscrittura')
        elif not tp.replace(os.sep, '/').startswith('01-originale/'):
            out.append(f'Testo precedente: «{tp}» deve stare in 01-originale/ (struttura standard)')
        elif not os.path.isfile(os.path.join(cartella_libro, tp)) or not comune.dentro(cartella_libro, os.path.join(cartella_libro, tp)):
            out.append(f'Testo precedente: «{tp}» non trovato dentro la cartella del libro')
    elif os.path.isdir(os.path.join(cartella_libro, '01-originale')):
        out.append('Modalità: 01-originale/ esiste solo in riscrittura (scrivi «Modalità: riscrittura» o togli la cartella)')
    return out[:5] if len(out) > 5 else out


def cartella_dal_briefing(percorso):
    p = os.path.realpath(percorso)
    d = os.path.dirname(p)
    if os.path.basename(d) == '00-progetto' and os.path.basename(p) == 'briefing.md':
        return os.path.dirname(d)
    return d


# ---------------------------------------------------------------- generazione

def slug(s):
    return comune.nome_file(s).replace('-', '_')


MINIMO_ASSOLUTO = 1000
DESCRIZIONE = {'lunghezza_totale.consigliata': 'Lunghezza', 'capitoli.minimo': 'Capitoli (minimo)',
               'capitoli.media': 'Capitoli (media)', 'capitoli.massimo': 'Capitoli (massimo)',
               'frase_media': 'Frase media', 'dialogo_percento': 'Dialogo',
               'capitoli.scene_per_capitolo': 'Scene (numero)', 'scene.lunghezza': 'Scene (lunghezza)'}


def _intervallo(s):
    m = re.match(r'^\s*(\d+)\s*-\s*(\d+)\s*%?\s*$', s or '')
    return [int(m.group(1)), int(m.group(2))] if m else None


def override_dal_briefing(c, profilo):
    """Valori del briefing fuori dal profilo -> (override, errori).

    Regola: un valore diverso dal profilo vale solo con «Motivo override:» non vuoto.
    Lunghezza fuori dai formati del profilo: serve anche «Capitoli: minimo | media | massimo».
    Sotto MINIMO_ASSOLUTO parole il motore si ferma comunque."""
    valori, err = [], []
    motivo = (c.get('motivo override') or '').strip()
    lung = int(re.sub(r'[^\d]', '', c.get('lunghezza', '')) or 0)
    formati = list(profilo['lunghezza_totale']['formati'].values())
    lo, hi = min(f[0] for f in formati), max(f[1] for f in formati)
    if lung and lung < MINIMO_ASSOLUTO:
        err.append(f'Lunghezza: {lung} sotto il minimo assoluto di {MINIMO_ASSOLUTO:,} parole'.replace(',', '.'))
    elif lung and not lo <= lung <= hi:
        valori.append(('lunghezza_totale.consigliata', [lung, lung], f'{lung} fuori dai formati del profilo ({lo}-{hi})'))
        if not (c.get('capitoli') or '').strip():
            err.append('Capitoli: obbligatorio con una lunghezza fuori profilo '
                       '(«minimo | media | massimo», per esempio 800 | 1000-1300 | 1800)')
    cap = (c.get('capitoli') or '').strip()
    if cap:
        parti = [x.strip() for x in cap.split('|')]
        media = _intervallo(parti[1]) if len(parti) == 3 else None
        if not media or not parti[0].isdigit() or not parti[2].isdigit():
            err.append('Capitoli: forma «minimo | media | massimo», per esempio 800 | 1000-1300 | 1800')
        else:
            mn, mx = int(parti[0]), int(parti[2])
            if not mn <= media[0] <= media[1] <= mx:
                err.append(f'Capitoli: serve minimo ≤ media ≤ massimo (ora {cap})')
            pc = profilo['capitoli']
            for campo, v, att in (('capitoli.minimo', mn, pc['minimo']), ('capitoli.media', media, pc['media']),
                                  ('capitoli.massimo', mx, pc['massimo'])):
                if v != att:
                    valori.append((campo, v, f'{v} invece di {att} del profilo'))
    sc = (c.get('scene') or '').strip()
    if sc:
        parti = [x.strip() for x in sc.split('|')]
        numero = ([int(parti[0])] * 2 if parti[0].isdigit() else _intervallo(parti[0])) if len(parti) == 2 else None
        lung = _intervallo(parti[1]) if len(parti) == 2 else None
        if not numero or not lung:
            err.append('Scene: forma «numero | lunghezza», per esempio 1 | 400-1200 oppure 2-3 | 800-2500')
        else:
            for campo, v, att in (('capitoli.scene_per_capitolo', numero, profilo['capitoli']['scene_per_capitolo']),
                                  ('scene.lunghezza', lung, profilo['scene']['lunghezza'])):
                if v != att:
                    valori.append((campo, v, f'{v} invece di {att} del profilo'))
    # coerenza: le scene previste devono stare in un capitolo medio
    nuovi = {cm: v for cm, v, _ in valori}
    media = nuovi.get('capitoli.media', profilo['capitoli']['media'])
    n_sc = nuovi.get('capitoli.scene_per_capitolo', profilo['capitoli']['scene_per_capitolo'])
    l_sc = nuovi.get('scene.lunghezza', profilo['scene']['lunghezza'])
    if not sc and n_sc[0] * l_sc[0] > media[1]:
        err.append(f'Scene: obbligatorio: {n_sc[0]} scene da almeno {l_sc[0]} parole non stanno in un capitolo '
                   f'medio di {media[1]} («numero | lunghezza», per esempio 1 | 400-1200)')
    for campo, chiave in (('frase_media', 'frase media'), ('dialogo_percento', 'dialogo')):
        if (c.get(chiave) or '').strip():
            v = _intervallo(c[chiave])
            if not v:
                err.append(f'{DESCRIZIONE[campo]}: forma «a-b»')
            elif v != profilo[campo]:
                valori.append((campo, v, f'{v} invece di {profilo[campo]} del profilo'))
    if valori and not motivo:
        err += [f'{DESCRIZIONE[campo]}: {nota}; serve «Motivo override:» nel briefing' for campo, _, nota in valori]
    ov = [{'campo': campo, 'valore': v, 'motivo': f'{motivo} — {DESCRIZIONE[campo]}: {nota}'} for campo, v, nota in valori]
    return ov, err


def profilo_effettivo(profilo, override):
    import copy
    eff = copy.deepcopy(profilo)
    for o in override:
        comune._metti(eff, o['campo'], o['valore'])
    return eff


def parole_dal_briefing(c, profilo):
    """Obiettivo in parole.target_totale; se è fuori dai formati del profilo, il motivo va in
    parole.motivo_fuori_profilo (il profilo non si tocca: lunghezza_totale.consigliata resta com'è)."""
    out = {'metodo': 'unico', 'target_totale': int(re.sub(r'[^\d]', '', c['lunghezza']))}
    for o in override_dal_briefing(c, profilo)[0]:
        if o['campo'] == 'lunghezza_totale.consigliata':
            out['motivo_fuori_profilo'] = o['motivo']
    return out


def genera_libro_yaml(b, profilo):
    c, L = b['campi'], b['liste']
    voci = []
    for t in L.get('tetti', []):
        parti = [x.strip() for x in t.split('|')]
        if len(parti) >= 2 and parti[1].isdigit():
            voci.append({'id': slug(parti[0]), 'espressione': parti[0], 'pattern': r'(?i)(?<!\w)' + re.escape(parti[0]) + r'(?!\w)',
                         'modalita': 'conta', 'massimo': int(parti[1]),
                         'ambito': parti[2] if len(parti) > 2 and parti[2] in ('libro', 'capitolo') else 'capitolo'})
    for v in L.get('vietati', []):
        voci.append({'id': slug(v)[:40], 'espressione': v, 'pattern': r'(?i)(?<!\w)' + re.escape(v) + r'(?!\w)', 'modalita': 'vieta'})
    nomi = []
    for v in L.get('vincoli', []):
        m = re.match(r'^(.+?)\s*\|\s*vietato prima del\s+(\d+)', v)
        if m:
            nome, n = m.group(1).strip(), int(m.group(2))
            nomi.append({'nome': nome, 'pattern': r'\b' + re.escape(nome) + r'\b',
                         'vietato_in': ([f'1-{n - 1}'] if n > 2 else ['1']) if n > 1 else [], 'obbligatorio_in': []})
    fm = re.findall(r'[\d.]+', c.get('formato', '') or '5.5 x 8.5')
    gate = [g.strip() for g in (c.get('gate') or '').split(',') if g.strip()] or GATE_PREDEFINITI
    anni = [int(a) for a in re.findall(r'\d{4}', c.get('anni ammessi', ''))]
    libro = {
        'titolo': c['titolo di lavoro'], 'sottotitolo': None, 'autore': c['autore'], 'lingua': 'it',
        'modalita': c.get('modalità') or 'nuovo',
    }
    if libro['modalita'] == 'riscrittura':
        libro['testo_precedente'] = c['testo precedente']
    libro.update({
        'serie': None, 'ebook': False, 'profilo': c['genere'], 'override': [o for o in override_dal_briefing(c, profilo)[0]
                                              if o['campo'] != 'lunghezza_totale.consigliata'], 'gate': gate,
        'parole': parole_dal_briefing(c, profilo),
        'formato': {'pagina_pollici': [float(fm[0]), float(fm[1])] if len(fm) >= 2 else [5.5, 8.5],
                    'carta': 'crema', 'bleed': False,
                    'margini_mm': {'alto': 20, 'basso': 20, 'esterno': 16, 'interno_scelto': 16},
                    'font': {'nome': 'EB Garamond', 'corpo_pt': 11.5, 'interlinea': 1.5},
                    'numerazione': {'da': 'capitolo_1', 'pagine_iniziali': 'senza_numero', 'posizione': 'piede_centro'}},
        'voci': voci, 'vincoli_capitolo': [], 'nome_vietato_prima_di': nomi,
        'dichiarazioni': {'chiusura': {'sigle': SIGLE[profilo['chiusura_preferita']], 'prevista_da': 'scaletta'}},
        'struttura': {'separatore_scena': {'sorgente': c.get('separatore di scena') or '* * *',
                                           'stampa': c.get('separatore di scena') or '* * *'},
                      'intestazione_capitolo': c.get('intestazione capitolo') or 'Luogo — giorno e data',
                      'parti': [], 'interludi': []},
        'calendario': {'anni_ammessi': anni},
        'ortografia': {'parole_ammesse_file': 'nomi_propri.txt'},
        'copyright': {'riga': '© {anno} {autore}. Tutti i diritti riservati.',
                      'anno': datetime.date.today().year,
                      'fantasia': "Quest'opera è frutto di fantasia. Nomi, personaggi, luoghi e fatti sono invenzione "
                                  "dell'autore o usati in modo fittizio; ogni somiglianza con persone, vive o scomparse, "
                                  "o con fatti realmente accaduti è puramente casuale.",
                      'nota_autore': None},
    })
    return libro


def numero_capitoli(libro, profilo):
    media = sum(profilo['capitoli']['media']) / 2
    return max(1, round(libro['parole']['target_totale'] / media))


def dove_capitoli(elenco):
    """«nel capitolo 1», «nei capitoli 1-3», «nei capitoli 1, 4 e 6-8»."""
    elenco = [str(x) for x in elenco or []]
    if not elenco:
        return 'in nessun capitolo'
    if len(elenco) == 1 and '-' not in elenco[0]:
        return f'nel capitolo {elenco[0]}'
    testo = elenco[0] if len(elenco) == 1 else ', '.join(elenco[:-1]) + ' e ' + elenco[-1]
    return f'nei capitoli {testo}'


def genera_manuale(b, libro, profilo, n_cap):
    cap = profilo['capitoli']
    base = comune.leggi_yaml(os.path.join(comune.radice_motore(), 'dati', 'lista-nera.yaml'))
    righe = [f'# Manuale di stile — {libro["titolo"]}', '',
             f'Generato da nuovo.py dal briefing (sezione «Direttive») e dal profilo «{libro["profilo"]}». '
             'Le regole numeriche stanno in libro.yaml e le controlla capitolo.py: qui sono scritte per esteso.', '',
             '## 1. Voce', '',
             f'- Voce: {b["campi"].get("voce") or "da fissare con la pagina campione"}.']
    righe += [f'- {t}' for t in b['tono']]
    righe += ['- Voce d\'autore: da completare dopo l\'«ok» alla pagina campione.', '',
              '## 2. Lunghezze', '',
              f'- Obiettivo: {libro["parole"]["target_totale"]} parole, circa {n_cap} capitoli.',
              f'- Capitolo: minimo {cap["minimo"]}, media {cap["media"][0]}-{cap["media"][1]}, massimo {cap["massimo"]} parole.',
              f'- Scene: {"-".join(map(str, sorted(set(cap["scene_per_capitolo"]))))} per capitolo, ciascuna '
              f'{profilo["scene"]["lunghezza"][0]}-{profilo["scene"]["lunghezza"][1]} parole (controllate da capitolo.py; '
              f'separatore «{libro["struttura"]["separatore_scena"]["sorgente"]}»).',
              f'- Tolleranza: ±{cap["tolleranza_budget"]:.0%} sul budget del capitolo in piano-parole.md; '
              f'±{cap["tolleranza_totale"]:.0%} sul totale.', '',
              '## 3. Frase e dialogo', '',
              f'- Frase media: {profilo["frase_media"][0]}-{profilo["frase_media"][1]} parole.',
              f'- Dialogo: {profilo["dialogo_percento"][0]}-{profilo["dialogo_percento"][1]}% delle parole del capitolo.',
              f'- Similitudini: al massimo una ogni {profilo["similitudini_max_per_parole"]} parole.', '',
              '## 4. Chiusure', '',
              f'- Chiusura preferita: {profilo["chiusura_preferita"]}. Sigle: {sigle_spiegate(libro["dichiarazioni"]["chiusura"]["sigle"])}.',
              '- Ogni capitolo dichiara la chiusura nella riga nascosta `<!-- zb: chiusura=… -->`; '
              'la sigla prevista sta nella scaletta.', '',
              '## 5. Tetti e vietati', '']
    for v in libro['voci']:
        if v['modalita'] == 'conta':
            righe.append(f'- Tetto: «{v.get("espressione", v["id"])}» al massimo {v["massimo"]} per {v["ambito"]}.')
        else:
            righe.append(f'- Vietato: «{v.get("espressione", v["id"])}».')
    righe += [f'- Lista nera di base (05-critica rr. 19-21): {len(base["voci"])} voci, sempre attive.', '',
              '## 6. Vincoli', '']
    righe += [f'- «{n["nome"]}» non compare {dove_capitoli(n["vietato_in"])}.'
              for n in libro['nome_vietato_prima_di']] or ['- Nessun vincolo.']
    righe += ['', '## 7. Struttura', '',
              f'- Intestazione del capitolo: «{libro["struttura"]["intestazione_capitolo"]}».',
              f'- Separatore di scena: «{libro["struttura"]["separatore_scena"]["sorgente"]}».',
              '- Nomi dei file: NN-<slug>.md in 04-manoscritto/.', '',
              '## 8. Scene obbligatorie del genere', '']
    righe += [f'- {s}' for s in profilo['scene_obbligatorie']]
    righe += ['', '## 9. Override rispetto al profilo (da approvare al gate «documenti»)', '']
    fuori = libro['parole'].get('motivo_fuori_profilo')
    ov_righe = ([f'- parole.target_totale: {libro["parole"]["target_totale"]} — motivo: {fuori}'] if fuori else [])
    ov_righe += [f'- {o["campo"]}: {o["valore"]} — motivo: {o["motivo"]}' for o in libro['override']]
    righe += ov_righe or ['- Nessuno.']
    righe += ['', '## 10. Fatti canonici e cose da non cambiare', '']
    righe += [f'- {f}' for f in b['fatti'] + b['non_cambiare']] or ['- Nessuno.']
    return '\n'.join(righe) + '\n'


def genera_bibbia(b, libro):
    righe = [f'# Bibbia — {libro["titolo"]}', '', '<!-- Da completare al gate «documenti»: luoghi, cronologia, '
             'motivi. I personaggi e i fatti vengono dal briefing. -->', '', '## Personaggi', '']
    for p in b['personaggi']:
        parti = [x.strip() for x in p.split('—')]
        righe.append(f'- **{parti[0]}**: ' + ' — '.join(parti[1:]))
    righe += ['', '## Luoghi', '', '-', '', '## Fatti canonici', '']
    righe += [f'- {f}' for f in b['fatti']] or ['-']
    righe += ['', '## Cose da non cambiare', '']
    righe += [f'- {f}' for f in b['non_cambiare']] or ['-']
    return '\n'.join(righe) + '\n'


def genera_scaletta(libro, n_cap, sigla):
    righe = [f'# Scaletta — {libro["titolo"]}', '',
             '<!-- Da completare al gate «documenti»: data, contenuto e chiusura prevista di ogni capitolo. -->', '',
             '| Unità | Data | Contenuto | Chiusura |', '|---|---|---|---|']
    righe += [f'| {i} |  |  | {sigla} |' for i in range(1, n_cap + 1)]
    return '\n'.join(righe) + '\n'


def genera_piano(libro, n_cap):
    tot = libro['parole']['target_totale']
    budget = round(tot / n_cap)
    righe = [f'# Piano parole — {libro["titolo"]}', '',
             '| Parte | Cap. | Titolo | Funzione | Scene | Budget capitolo | Budget per scena | Parole reali | Scarto |',
             '|---|---|---|---|---|---|---|---|---|']
    righe += [f'| — | {i} |  |  |  | {budget} |  |  |  |' for i in range(1, n_cap + 1)]
    righe += ['', f'Totale: {budget * n_cap}.']
    return '\n'.join(righe) + '\n'


def crea(percorso_briefing):
    cartella = cartella_dal_briefing(percorso_briefing)
    if os.path.exists(os.path.join(cartella, 'libro.yaml')):
        raise comune.ErroreMotore(f'C\'è già un libro in {cartella}: nuovo.py non sovrascrive un libro esistente')
    b = leggi_briefing(percorso_briefing)
    manca = mancanze(b, cartella)
    if manca:
        raise comune.ErroreMotore('Briefing incompleto. Mancano:\n- ' + '\n- '.join(manca))
    profilo = comune.carica_profilo(b['campi']['genere'])
    libro = genera_libro_yaml(b, profilo)
    profilo = profilo_effettivo(profilo, libro['override'])
    n_cap = numero_capitoli(libro, profilo)
    dest = os.path.join(cartella, '00-progetto', 'briefing.md')
    if os.path.realpath(percorso_briefing) != os.path.realpath(dest):
        os.replace(percorso_briefing, comune.percorso_in_libro(cartella, '00-progetto/briefing.md'))
    comune.scrivi(cartella, 'libro.yaml', yaml.safe_dump(libro, sort_keys=False, allow_unicode=True, width=120))
    comune.scrivi(cartella, '.gitignore', '.zb/\n')
    m = os.path.join(comune.radice_motore(), 'modelli')
    stato = comune.leggi_yaml(os.path.join(m, 'stato.yaml'))
    stato.update({'libro': libro['titolo'], 'fase': 'documenti', 'passo': 'da completare', 'gate_in_attesa': None,
                  'parole': {'scritte': 0, 'obiettivo': libro['parole']['target_totale'], 'metodo': 'unico'},
                  'aggiornato': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})
    comune.scrivi(cartella, 'stato.yaml', yaml.safe_dump(stato, sort_keys=False, allow_unicode=True))
    comune.scrivi(cartella, 'cronologia.yaml', open(os.path.join(m, 'cronologia.yaml'), encoding='utf-8').read())
    nomi = sorted({w for p in b['personaggi'] for w in p.split('—')[0].split() if w[:1].isupper()})
    comune.scrivi(cartella, 'nomi_propri.txt', '\n'.join(nomi) + '\n')
    comune.scrivi(cartella, '02-bibbia/bibbia.md', genera_bibbia(b, libro))
    comune.scrivi(cartella, '03-architettura/manuale-di-stile.md', genera_manuale(b, libro, profilo, n_cap))
    comune.scrivi(cartella, '03-architettura/scaletta.md',
                  genera_scaletta(libro, n_cap, libro['dichiarazioni']['chiusura']['sigle'][0]))
    comune.scrivi(cartella, '03-architettura/piano-parole.md', genera_piano(libro, n_cap))
    decisioni = '\n'.join(f'- {f}' for f in b['fatti'] + b['non_cambiare']) or '- nessuna'
    leggimi = open(os.path.join(m, 'LEGGIMI.md'), encoding='utf-8').read().format(
        titolo=libro['titolo'], percorso=cartella, modalita=libro['modalita'], fase='documenti',
        gate='nessuno', ultimo='—', decisioni=decisioni)
    comune.scrivi(cartella, 'LEGGIMI.md', leggimi)
    comune.carica_libro(cartella)          # libro.yaml generato valido (schema, override con motivo)
    errori = comune.controlla_struttura(cartella, libro['modalita'])
    if errori:
        raise comune.ErroreMotore('Struttura del libro non conforme a dati/struttura-libro.yaml:\n- ' + '\n- '.join(errori))
    return cartella, n_cap


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: nuovo.py <percorso-briefing>')
    cartella, n_cap = crea(args[0])
    print(f'libro creato in {cartella} ({n_cap} capitoli previsti); fase «documenti».')
    print('Prossimo passo: completare bibbia, cronologia, scaletta e piano parole; poi «zb pronto <libro>»,'
          ' che apre il gate «documenti».')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

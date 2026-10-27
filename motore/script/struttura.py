"""Fase struttura del percorso editoriale: modelli dei nove file di 03-struttura/ e controlli meccanici.

Uso: python3 -B struttura.py <libro> verifica      (comando «zb struttura <libro> verifica»; non scrive nulla)
- nove file presenti in 03-struttura/ e senza la riga «<!-- zb: modello -->»;
- in 05-scaletta.md una scheda per ogni capitolo del piano parole, con tutti i campi pieni;
- in 04-atti-svolte.md una macrostruttura dichiarata tra quelle ammesse e il suo motivo;
- nessuna etichetta automatica «Atto 1/2/3» nei titoli della scaletta;
- budget del piano parole non tutti uguali (capitoli che nascono dal contenuto);
- nessun campo «- Campo:» vuoto in 01, 02, 03 e 09; in 06-sottotrame-temi.md almeno una promessa o sottotrama e
  nessuna senza «Si chiude» (controlli della fase struttura di motore, 971b6df, con i nomi del pacchetto).
I modelli in italiano vengono da motore/editoriale/struttura/modelli/ (fonte unica); li usa nuovo.py; i campi della scheda li controlla anche prepara.py prima di ogni capitolo.
"""
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

MACRO = ['3 atti', '4 atti', '5 atti', 'dittico', 'in medias res', 'mosaico', 'slow-burn', 'circolare']
MACRO_EN = {'3 acts': '3 atti', 'three acts': '3 atti', '4 acts': '4 atti', 'four acts': '4 atti',
            '5 acts': '5 atti', 'five acts': '5 atti', 'diptych': 'dittico', 'mosaic': 'mosaico',
            'circular': 'circolare'}

# campi obbligatori della scheda di capitolo: chiave, etichetta italiana, etichetta inglese
CAMPI_SCHEDA = [
    ('funzione', 'Funzione narrativa', 'Narrative function'),
    ('pov', 'Punto di vista, luogo e tempo', 'Point of view, place and time'),
    ('tag', 'Personaggi e luoghi (tag del codex)', 'Characters and places (codex tags)'),
    ('conflitto', 'Conflitto (chi vuole cosa, chi si oppone)', 'Conflict (who wants what, who opposes)'),
    ('cambiamento', 'Cosa cambia alla fine (situazione, conoscenza, relazione)', 'Change (situation, knowledge, relationship)'),
    ('informazione', 'Informazione data al lettore (e cosa viene taciuto)', 'Information given to the reader (and what is withheld)'),
    ('polarita', 'Polarità emotiva (da cosa a cosa cambia la carica della scena)', 'Emotional polarity (from what to what the charge shifts)'),
    ('sottotesto', 'Sottotesto dei dialoghi principali', 'Subtext of the main dialogues'),
    ('promesse', 'Promesse aperte / chiuse', 'Promises opened / closed'),
    ('emozione', 'Emozione dominante', 'Dominant emotion'),
    ('gancio', 'Gancio finale', 'Final hook'),
    ('parole', 'Parole previste', 'Planned words'),
]
OBBLIGATORI = ('funzione', 'conflitto', 'cambiamento', 'informazione', 'gancio', 'polarita', 'sottotesto')

TITOLI = {
    'it': {'01-premessa.md': 'Premessa e promessa al lettore', '02-logline-tema.md': 'Logline e tema',
           '03-personaggi-chiave.md': 'Personaggi chiave', '04-atti-svolte.md': 'Macrostruttura e svolte',
           '05-scaletta.md': 'Scaletta per capitolo', '06-sottotrame-temi.md': 'Sottotrame e promesse',
           '07-tensione-ritmo.md': 'Tensione e ritmo', '08-piano-parole.md': 'Piano parole',
           '09-scelte-fisse.md': 'Scelte fisse: punto di vista, tempo, voce'},
    'en': {'01-premessa.md': 'Premise and promise to the reader', '02-logline-tema.md': 'Logline and theme',
           '03-personaggi-chiave.md': 'Key characters', '04-atti-svolte.md': 'Macrostructure and turning points',
           '05-scaletta.md': 'Chapter outline', '06-sottotrame-temi.md': 'Subplots and promises',
           '07-tensione-ritmo.md': 'Tension and pacing', '08-piano-parole.md': 'Word plan',
           '09-scelte-fisse.md': 'Fixed choices: point of view, tense, voice'},
}
GUIDA = {
    'it': {'01-premessa.md': '- Lettore (in concreto):\n- Promessa del libro:\n- Perché lo finirà:\n',
           '02-logline-tema.md': '- Logline (una frase):\n- Tema:\n- Controtema:\n',
           '03-personaggi-chiave.md': '## Protagonista\n- Desiderio:\n- Bisogno:\n- Ferita o mancanza:\n- Arco (da… a…):\n\n'
                                      '## Antagonista o forza antagonista\n- Cosa vuole:\n\n## Posta in gioco\n-\n',
           '04-atti-svolte.md': f'Macrostruttura: <una tra: {", ".join(MACRO)}>\nMotivo:\n\n## Svolte\n'
                                '| Svolta | Capitolo | Cosa la rende necessaria |\n|---|---|---|\n',
           '06-sottotrame-temi.md': '| Sottotrama o promessa | Si apre | Si sviluppa | Si chiude |\n|---|---|---|---|\n',
           '07-tensione-ritmo.md': '| Cap. | Tensione (1-10) | Respiro voluto? |\n|---|---|---|\n',
           '09-scelte-fisse.md': '- Punto di vista:\n- Tempo verbale:\n- Voce:\n- Sistema del dialogo:\n'},
    'en': {'01-premessa.md': '- Reader (in concrete terms):\n- Promise of the book:\n- Why they will finish it:\n',
           '02-logline-tema.md': '- Logline (one sentence):\n- Theme:\n- Counter-theme:\n',
           '03-personaggi-chiave.md': '## Protagonist\n- Want:\n- Need:\n- Wound or lack:\n- Arc (from… to…):\n\n'
                                      '## Antagonist or opposing force\n- What it wants:\n\n## Stakes\n-\n',
           '04-atti-svolte.md': f'Macrostruttura: <one of: {", ".join(MACRO)}>\nMotivo:\n\n## Turning points\n'
                                '| Turning point | Chapter | What makes it necessary |\n|---|---|---|\n',
           '06-sottotrame-temi.md': '| Subplot or promise | Opens | Develops | Closes |\n|---|---|---|---|\n',
           '07-tensione-ritmo.md': '| Cap. | Tension (1-10) | Deliberate breather? |\n|---|---|---|\n',
           '09-scelte-fisse.md': '- Point of view:\n- Tense:\n- Voice:\n- Dialogue punctuation system:\n'},
}


def lingua_doc(libro):
    return 'en' if libro.get('lingua') == 'en' else 'it'


def scheda_vuota(n, lingua='it'):
    if lingua == 'it':          # fonte unica: il modello del livello editoriale
        m = os.path.join(comune.radice_motore(), 'editoriale', 'struttura', 'modelli', 'scaletta-capitolo.md')
        return open(m, encoding='utf-8').read().rstrip('\n').replace('Capitolo N ', f'Capitolo {n} ', 1)
    i = 2
    titolo = 'Capitolo' if lingua == 'it' else 'Chapter'
    righe = [f'## {titolo} {n} - <titolo di lavoro>']
    for c in CAMPI_SCHEDA:
        righe.append(f'- {c[i]}:' + (' @char:<id> @loc:<id>' if c[0] == 'tag' else ''))
    return '\n'.join(righe)


def guida_editoriale(f):
    """Corpo del modello del livello editoriale (editoriale/struttura/modelli/<f>) senza il titolo; None se manca."""
    m = os.path.join(comune.radice_motore(), 'editoriale', 'struttura', 'modelli', f)
    if not os.path.isfile(m):
        return None
    righe = open(m, encoding='utf-8').read().splitlines()
    if righe and righe[0].startswith('# '):
        righe = righe[1:]
    return '\n'.join(righe).strip('\n') + '\n'


def modelli(libro, n_cap, sigla, budget):
    """{nome file: testo} dei nove file di 03-struttura/, con la riga MODELLO."""
    l = lingua_doc(libro)
    out = {}
    for f in comune.FILE_STRUTTURA:
        testo = [comune.MODELLO, f'# {TITOLI[l][f]} — {libro["titolo"]}', '']
        if f == '05-scaletta.md':
            testo += ['| Unità | Data | Contenuto | Chiusura |', '|---|---|---|---|']
            testo += [f'| {i} |  |  | {sigla} |' for i in range(1, n_cap + 1)]
            testo += ['']
            testo += [scheda_vuota(i, l) + '\n' for i in range(1, n_cap + 1)]
        elif f == '08-piano-parole.md':
            testo += ['| Parte | Cap. | Titolo | Funzione | Scene | Budget capitolo | Budget per scena | Parole reali | Scarto |',
                      '|---|---|---|---|---|---|---|---|---|']
            testo += [f'| — | {i} |  |  |  | {budget} |  |  |  |' for i in range(1, n_cap + 1)]
            testo += ['', f'Totale: {budget * n_cap}.',
                      '<!-- I budget vanno resi diversi secondo la funzione di ogni capitolo. -->']
        else:
            testo.append((guida_editoriale(f) if l == 'it' else None) or GUIDA[l][f])
        out[f] = '\n'.join(testo).rstrip('\n') + '\n'
    return out


# ---------------------------------------------------------------- lettura della scaletta

# riconoscimento dei campi per parola iniziale: vale per il modello del livello editoriale
# (motore/editoriale/struttura/modelli/scaletta-capitolo.md) e per le etichette inglesi
PREFISSI = [('funzione', ('funzione', 'narrative function')), ('pov', ('punto di vista', 'point of view')),
            ('tag', ('personaggi e luoghi', 'characters and places')), ('conflitto', ('conflitto', 'conflict')),
            ('cambiamento', ('cambiamento', 'cosa cambia', 'change', 'what changes')),
            ('informazione', ('informazione', 'information')), ('polarita', ('polarità', 'polarita', 'emotional polarity')),
            ('sottotesto', ('sottotesto', 'subtext')), ('promesse', ('promesse', 'promises')),
            ('emozione', ('emozione', 'dominant emotion')), ('gancio', ('gancio', 'final hook', 'hook')),
            ('parole', ('parole', 'planned words', 'words'))]


def chiave_campo(etichetta):
    e = etichetta.strip().lower()
    for chiave, pref in PREFISSI:
        if e.startswith(pref):
            return chiave
    return None


def schede(cartella):
    """{numero capitolo (str): {chiave campo: valore}} dai blocchi «## Capitolo N» / «## Chapter N» di 05-scaletta.md."""
    p = os.path.join(cartella, comune.STRUTTURA, '05-scaletta.md')
    if not os.path.isfile(p):
        return {}
    out, cur = {}, None
    for r in open(p, encoding='utf-8').read().splitlines():
        m = re.match(r'^##\s+(?:Capitolo|Chapter)\s+(\d+)\b(.*)$', r.strip())
        if m:
            cur = str(int(m.group(1)))
            out[cur] = {'_titolo': m.group(2).strip(' -—')}
            continue
        if cur and r.strip().startswith('- ') and ':' in r:
            k, v = r.strip()[2:].split(':', 1)
            chiave = chiave_campo(k)
            if chiave:
                out[cur][chiave] = v.strip()
    return out


def campi_mancanti(scheda):
    out = []
    for k in OBBLIGATORI:
        v = (scheda.get(k) or '').strip()
        if not v or v.startswith('<') or v in ('-', '—'):
            out.append(k)
    return out


def tag_di(scheda):
    """[('char', id), ('loc', id)] dalla riga dei tag della scheda."""
    return [(t, i) for t, i in re.findall(r'@(char|loc):([\w\-]+)', scheda.get('tag') or '') if i != 'id']


def macrostruttura(cartella):
    p = os.path.join(cartella, comune.STRUTTURA, '04-atti-svolte.md')
    if not os.path.isfile(p):
        return None, None
    t = open(p, encoding='utf-8').read()
    m = re.search(r'(?mi)^Macrostruttura:\s*(.+)$', t)
    mot = re.search(r'(?mi)^Motivo:\s*(.+)$', t)
    nome = m.group(1).strip().lower() if m else None
    nome = MACRO_EN.get(nome, nome)
    return nome, (mot.group(1).strip() if mot else None)


def verifica(cartella):
    """Problemi meccanici della struttura (elenco vuoto = tutto a posto)."""
    out = []
    d = os.path.join(cartella, comune.STRUTTURA)
    for f in comune.FILE_STRUTTURA:
        p = os.path.join(d, f)
        if not os.path.isfile(p):
            out.append(f'{comune.STRUTTURA}/{f}: mancante')
        elif comune.MODELLO in open(p, encoding='utf-8').read():
            out.append(f'{comune.STRUTTURA}/{f}: ancora modello (togli la riga {comune.MODELLO} quando è scritto)')
    if out:
        return out
    nome, motivo = macrostruttura(cartella)
    if nome not in MACRO:
        out.append(f'04-atti-svolte.md: «Macrostruttura:» deve essere una tra {", ".join(MACRO)} (ora: {nome or "assente"})')
    if not motivo:
        out.append('04-atti-svolte.md: manca «Motivo:» della macrostruttura')
    import fase
    piano = [u for u in fase.unita_del_piano(cartella) if u.isdigit()]
    sk = schede(cartella)
    for n in piano:
        if n not in sk:
            out.append(f'05-scaletta.md: manca la scheda del capitolo {n}')
            continue
        manca = campi_mancanti(sk[n])
        if manca:
            out.append(f'05-scaletta.md, capitolo {n}: campi vuoti: {", ".join(manca)}')
        if re.search(r'(?i)\b(atto|act)\s+(\d|i{1,3}|iv|v)\b', sk[n].get('_titolo', '')):
            out.append(f'05-scaletta.md, capitolo {n}: etichetta automatica di atto nel titolo')
    out += campi_vuoti(cartella) + promesse_senza_chiusura(cartella)
    budget = []
    for r in comune.tabella_md(os.path.join(cartella, comune.rel_piano(cartella))):
        b = re.sub(r'[^\d]', '', r.get('Budget capitolo', ''))
        if (r.get('Cap.') or '').isdigit() and b:
            budget.append(int(b))
    if len(budget) >= 3 and len(set(budget)) == 1:
        out.append('08-piano-parole.md: tutti i capitoli hanno lo stesso budget; i budget nascono dalla funzione')
    return out


CON_CAMPI = ('01-premessa.md', '02-logline-tema.md', '03-personaggi-chiave.md', '09-scelte-fisse.md')


def campi_vuoti(cartella):
    """Righe «- Campo:» senza valore nei file a campi (fuori dai commenti HTML)."""
    out = []
    for f in CON_CAMPI:
        p = os.path.join(cartella, comune.STRUTTURA, f)
        if not os.path.isfile(p):
            continue
        t = re.sub(r'<!--.*?-->', '', open(p, encoding='utf-8').read(), flags=re.S)
        for r in t.splitlines():
            m = re.match(r'^\s*-\s+([^:\n]{2,}):\s*$', r)
            if m:
                out.append(f'{f}: campo vuoto «{m.group(1).strip()}»')
    return out


def promesse_senza_chiusura(cartella):
    """06-sottotrame-temi.md: almeno una promessa o sottotrama; ognuna con il capitolo in cui si chiude."""
    p = os.path.join(cartella, comune.STRUTTURA, '06-sottotrame-temi.md')
    if not os.path.isfile(p):
        return []
    def campo(r, prefissi):     # varianti dell'intestazione («Promessa», «Si chiude (pagamento)»…)
        return next((v.strip() for k, v in r.items() if k and k.strip().lower().startswith(prefissi) and v), '')
    righe = [r for r in comune.tabella_md(p) if campo(r, ('sottotrama', 'promessa', 'subplot', 'promise'))]
    if not righe:
        return ['06-sottotrame-temi.md: nessuna promessa o sottotrama']
    out = []
    for r in righe:
        nome = campo(r, ('sottotrama', 'promessa', 'subplot', 'promise'))
        chiude = campo(r, ('si chiude', 'si paga', 'closes'))
        if not chiude:
            out.append(f'06-sottotrame-temi.md: «{nome}» senza chiusura (pagamento)')
    return out


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2 or args[1] != 'verifica':
        raise comune.ErroreMotore('Uso: struttura.py <libro> verifica')
    cartella, libro, _ = comune.carica_libro(args[0])
    problemi = verifica(cartella)
    for p in problemi[:38]:
        print(f'KO {p}')
    if len(problemi) > 38:
        print(f'… altri {len(problemi) - 38}')
    print('Struttura: ' + ('OK' if not problemi else f'{len(problemi)} problemi'))
    return 1 if problemi else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

"""Controllo ortografico del manoscritto (passo 7). Tre livelli.

Uso: python3 -B ortografia.py <libro> [--schermo]
(a) Hunspell it_IT, sempre: parole non riconosciute, escluse le parole ammesse del libro
    (libro.yaml ortografia.parole_ammesse_file, di solito nomi_propri.txt) e quelle generiche del
    motore (dati/parole-ammesse-it.txt). Le elisioni (l', dell', anch'…) non si controllano.
(b) LanguageTool, solo se ZB_LANGUAGETOOL indica la cartella dei suoi .jar (scaricati fuori dal
    repository; come, in PROCEDURA.md). Mai scaricato da questo script.
(c) Checklist manuale per la lettura umana, sempre, in fondo al report.
Report: <libro>/06-diagnostica/controllo-ortografico.md (con --schermo solo a schermo).
Il report dice quali livelli sono stati eseguiti. Codice 1 se (a) o (b) trovano qualcosa;
2 se Hunspell o il dizionario it_IT mancano.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

PAROLA = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:['’][A-Za-zÀ-ÖØ-öø-ÿ]+)*['’]?")
ENV = dict(os.environ, LC_ALL='C.UTF-8')
CHECKLIST = [
    '«e» congiunzione al posto di «è» verbo (e viceversa)',
    'accordi di genere e numero (soggetto e verbo, nome e aggettivo)',
    'apostrofi: «qual è», «un amico» / «un\'amica», «po\'»',
    'accenti: «perché», «poiché», «né», «sé», «lì», «là», «dà»',
    'parole vere al posto sbagliato (per esempio «anno» per «hanno», «a» per «ha»)',
    'concordanza dei tempi verbali nella stessa scena',
    'virgolette e lineette dei dialoghi coerenti in tutto il libro',
    'maiuscole dopo i due punti e nei titoli dei capitoli',
]


def ammesse(cartella, libro):
    out = set()
    nome = ((libro.get('ortografia') or {}).get('parole_ammesse_file')) or 'nomi_propri.txt'
    for p in (os.path.join(cartella, nome), os.path.join(comune.radice_motore(), 'dati', 'parole-ammesse-it.txt')):
        if os.path.isfile(p):
            out |= {r.strip() for r in open(p, encoding='utf-8') if r.strip() and not r.startswith('#')}
    return out


def parole_della_riga(riga):
    """Parole da controllare: senza la parte elisa prima dell'apostrofo, senza cifre."""
    for t in PAROLA.findall(riga):
        parti = re.split(r"['’]", t)
        for i, x in enumerate(parti):
            if x and i == len(parti) - 1:
                yield x


def hunspell(parole):
    if not shutil.which('hunspell'):
        return None, 'hunspell non installato'
    r = subprocess.run(['hunspell', '-D'], capture_output=True, text=True, env=ENV, input='')
    if 'it_IT' not in r.stdout + r.stderr:
        return None, 'dizionario it_IT non trovato'
    r = subprocess.run(['hunspell', '-l', '-i', 'UTF-8', '-d', 'it_IT'], input='\n'.join(sorted(parole)),
                       capture_output=True, text=True, env=ENV)
    return set(r.stdout.split()), None


def languagetool(testi):
    """[(unita, riga, regola, messaggio, testo)] oppure (None, motivo)."""
    d = os.environ.get('ZB_LANGUAGETOOL')
    if not d:
        return None, 'variabile ZB_LANGUAGETOOL non impostata'
    if not glob.glob(os.path.join(d, '*.jar')):
        return None, f'nessun .jar in {d}'
    if not shutil.which('java'):
        return None, 'java non installato'
    out = []
    with tempfile.TemporaryDirectory(prefix='zb-lt-') as tmp:
        for nome, testo, prosa in testi:
            f = os.path.join(tmp, 'unita.txt')
            open(f, 'w', encoding='utf-8').write(testo)
            r = subprocess.run(['java', '-cp', os.path.join(d, '*'), 'org.languagetool.commandline.Main',
                                '-l', 'it', '--json', f], capture_output=True, text=True, env=ENV, timeout=600)
            try:
                dati = json.loads(r.stdout[r.stdout.index('{'):])
            except ValueError:
                return None, f'LanguageTool non eseguito: {(r.stderr or r.stdout).strip()[:200]}'
            for m in dati.get('matches', []):
                riga = testo[:m['offset']].count('\n') + 1
                if riga in prosa:
                    frammento = testo[m['offset']:m['offset'] + m['length']]
                    out.append((nome, riga, m['rule']['id'], m['message'], frammento))
    return out, None


def controlla(cartella, libro):
    am = ammesse(cartella, libro)
    am_min = {x.lower() for x in am}
    posizioni, testi = {}, []
    for nome, p in comune.unita(cartella, libro):
        testo = open(p, encoding='utf-8').read()
        prosa = {}
        for n, riga in comune.righe_prosa(testo):
            prosa[n] = riga
            for w in parole_della_riga(riga):
                posizioni.setdefault(w, []).append(f'{os.path.relpath(p, cartella)}:{n}')
        testi.append((os.path.relpath(p, cartella), testo, prosa))
    sconosciute, errore_h = hunspell(set(posizioni))
    trovate = {}
    if sconosciute is not None:
        trovate = {w: posizioni[w] for w in sorted(sconosciute)
                   if w in posizioni and w not in am and w.lower() not in am_min}
    lt, motivo_lt = languagetool(testi)
    if lt is not None:
        lt = [x for x in lt if not (x[2].startswith('MORFOLOGIK') and (x[4] in am or x[4].lower() in am_min))]
    return trovate, errore_h, lt, motivo_lt


def report(libro, trovate, errore_h, lt, motivo_lt):
    r = [f'# Controllo ortografico — {libro["titolo"]}', '', '## Livelli eseguiti', '',
         '| Livello | Eseguito | Note |', '|---|---|---|',
         f'| (a) Hunspell it_IT | {"no" if errore_h else "sì"} | {errore_h or "parole ammesse: libro + dati/parole-ammesse-it.txt"} |',
         f'| (b) LanguageTool | {"no" if lt is None else "sì"} | {motivo_lt or "regole italiane, solo righe di prosa"} |',
         '| (c) Checklist manuale | sì | in fondo al report, per la lettura umana |', '']
    if not errore_h:
        r += ['## (a) Parole non riconosciute da Hunspell', '',
              f'{len(trovate)} parole. Ogni voce va verificata: un refuso, oppure una parola da aggiungere '
              'alle parole ammesse del libro.', '']
        if trovate:
            r += ['| Parola | Occorrenze | Posizioni (file:riga) |', '|---|---|---|']
            r += [f'| {w} | {len(p)} | {", ".join(p[:10])}{" …" if len(p) > 10 else ""} |' for w, p in trovate.items()]
        r.append('')
    if lt is not None:
        r += ['## (b) Segnalazioni di LanguageTool', '', f'{len(lt)} segnalazioni.', '']
        if lt:
            r += ['| File:riga | Regola | Testo | Messaggio |', '|---|---|---|---|']
            r += [f'| {f}:{n} | {reg} | {t} | {msg} |' for f, n, reg, msg, t in lt]
        r.append('')
    r += ['## (c) Checklist per la lettura umana', '',
          'I correttori automatici non rilevano errori come «e» al posto di «è», gli accordi sbagliati '
          'o una parola vera usata al posto di un\'altra. Questi controlli li fa chi legge.', '',
          '| Controllo | Fatto |', '|---|---|']
    r += [f'| {c} | [ ] |' for c in CHECKLIST]
    return '\n'.join(r) + '\n'


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: ortografia.py <libro> [--schermo]')
    cartella, libro, _ = comune.carica_libro(args[0])
    trovate, errore_h, lt, motivo_lt = controlla(cartella, libro)
    testo = report(libro, trovate, errore_h, lt, motivo_lt)
    if '--schermo' in argv:
        print(testo)
    else:
        print('scritto', comune.scrivi(cartella, '06-diagnostica/controllo-ortografico.md', testo))
    print(f'Hunspell: {"non eseguito (" + errore_h + ")" if errore_h else f"{len(trovate)} parole da verificare"}; '
          f'LanguageTool: {"saltato (" + motivo_lt + ")" if lt is None else f"{len(lt)} segnalazioni"}')
    if errore_h:
        return 2
    return 1 if trovate or lt else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

"""Prove del percorso da casa editrice (le lancia prove.py; da sola: python3 -B prove_editoriale.py).

Mini-libro inventato prove/mini-libro-editoriale/ (autrice inventata) in un repository temporaneo con origin:
struttura e gate, ruoli e separazione scrittore/revisore, capsule, codex, canone, stato compatto, fasi di
revisione (manoscritto, line, copy, bozze), cartella unica e recinto (anche Bash e pre-commit), agenti spenti
sul ramo motore, comandi di Claude Code, anti-IA, correttore, traduzione in inglese con i controlli meccanici.
Gli attesi stanno accanto a ogni controllo.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

M = comune.radice_motore()
S = os.path.join(M, 'script')
F = os.path.join(M, 'prove', 'mini-libro-editoriale')
SLUG = 'lanterna'
TOGLI = ('CLAUDE_PROJECT_DIR', 'ZB_LIBRO', 'ZB_RAMO', 'ZB_SESSIONE')
E = {k: v for k, v in os.environ.items() if k not in TOGLI}
E.update(ZB_PROVE='1', PYTHONDONTWRITEBYTECODE='1', GIT_AUTHOR_NAME='Prova', GIT_AUTHOR_EMAIL='prova@esempio.invalid',
         GIT_COMMITTER_NAME='Prova', GIT_COMMITTER_EMAIL='prova@esempio.invalid')
righe = []
TMP = None


def esito(script, controllo, atteso, ottenuto, sezione):
    righe.append((sezione, script, controllo, str(atteso), str(ottenuto), 'OK' if str(atteso) == str(ottenuto) else 'KO'))


def saltata(script, controllo, motivo, sezione):
    righe.append((sezione, script, controllo, '—', motivo, 'SALTATA'))


def zb(cwd, *a, env=None):
    return subprocess.run([sys.executable, '-B', os.path.join(M, 'zb'), *a], cwd=cwd, env=env or E,
                          capture_output=True, text=True)


def git(cwd, *a):
    return subprocess.run(['git', *a], cwd=cwd, env=E, capture_output=True, text=True)


def repo(ramo='prova'):
    d = tempfile.mkdtemp(dir=TMP)
    git(d, 'init', '-q', '--bare', 'remoto.git')
    r = os.path.join(d, 'repo')
    os.makedirs(r)
    git(r, 'init', '-q')
    git(r, 'checkout', '-q', '-b', ramo)
    git(r, 'remote', 'add', 'origin', os.path.join(d, 'remoto.git'))
    open(os.path.join(r, 'LEGGIMI.md'), 'w').write('repository di prova\n')
    salva(r, 'inizio')
    return r


def salva(r, msg='prova', *percorsi):
    git(r, 'add', *(percorsi or ['-A']))
    p = git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', msg)
    git(r, 'push', '-q', '-u', 'origin', 'HEAD')
    return p


def copia(src, dest):
    os.makedirs(dest, exist_ok=True)
    for f in sorted(os.listdir(src)):
        if os.path.isfile(os.path.join(src, f)):
            shutil.copyfile(os.path.join(src, f), os.path.join(dest, f))


def stato(L):
    return comune.leggi_yaml(os.path.join(L, 'stato.yaml'))


def fino_alla_fine(L):
    """«avanti» finché i documenti del gate sono mostrati tutti (poi «ok» è ammesso)."""
    for _ in range(200):
        p = zb(L, 'avanti', '.')
        if 'Fine dei documenti' in p.stdout or p.returncode:
            return p
    return p


def intesta(L, sorgente, dest, ruolo, n=None):
    """Copia un rapporto di prova con la prima riga data da «zb ruolo»."""
    p = zb(L, 'ruolo', '.', ruolo, *([str(n)] if n else []))
    riga = next((x.split('Prima riga: ', 1)[1] for x in p.stdout.splitlines() if x.startswith('Prima riga: ')), None)
    if riga is None:
        return p
    testo = open(sorgente, encoding='utf-8').read().split('\n', 1)[1]
    os.makedirs(os.path.dirname(os.path.join(L, dest)), exist_ok=True)
    open(os.path.join(L, dest), 'w', encoding='utf-8').write(riga + '\n' + testo)
    return p


def nasce(r):
    L = os.path.join(r, 'libri', SLUG)
    os.makedirs(L)
    shutil.copyfile(os.path.join(F, 'briefing.md'), os.path.join(L, 'briefing.md'))
    p = zb(r, 'nuovo', f'libri/{SLUG}/briefing.md')
    return L, p


# ---------------------------------------------------------------- percorso completo

def percorso(sez='percorso editoriale'):
    r = repo()
    L, p = nasce(r)
    esito('nuovo.py', 'nascita: codice / fase / file di 03-struttura con il modello',
          '0 / struttura / 9', f'{p.returncode} / {stato(L)["fase"]} / '
          f'{sum(comune.MODELLO in open(os.path.join(L, "03-struttura", f)).read() for f in comune.FILE_STRUTTURA)}', sez)
    lb = comune.leggi_yaml(os.path.join(L, 'libro.yaml'))
    esito('nuovo.py', 'libro.yaml: percorso, lingua, lingue_target, gate (modo automatico: solo la pausa di lettura), '
          'pausa_lettura', "editoriale / it / ['en'] / ['lettura'] / 3",
          f'{lb.get("percorso")} / {lb["lingua_originale"]} / {lb["lingue_target"]} / {lb["gate"]} / '
          f'{lb.get("pausa_lettura")}', sez)
    esito('nuovo.py', 'nessun documento prima della struttura: bibbia / codex / cronologia / manuale',
          'False / False / False / False',
          ' / '.join(str(os.path.exists(os.path.join(L, x))) for x in
                     ('02-bibbia/bibbia.md', '02-bibbia/codex', 'cronologia.yaml', '03-architettura/manuale-di-stile.md')), sez)
    esito('nuovo.py', 'canone iniziale dai fatti canonici', 1, len(stato(L)['fatti_bloccati']), sez)
    salva(r, 'nascita')
    p = zb(L, 'pronto', '.')
    esito('fase.py', 'pronto con la struttura ancora modello: FERMO', '2 / True',
          f'{p.returncode} / {"ancora modello" in p.stderr}', sez)
    p = zb(L, 'esito', '.', '1')
    esito('fase.py', 'nessun capitolo prima del gate struttura', '2 / True', f'{p.returncode} / {"stesura" in p.stderr}', sez)
    p = zb(L, 'ruolo', '.', 'line-editor', '1')
    esito('ruolo.py', 'line-editor in fase struttura: rifiutato', '2 / True', f'{p.returncode} / {"non lavora" in p.stderr}', sez)
    copia(os.path.join(F, 'struttura'), os.path.join(L, '03-struttura'))
    copia(os.path.join(F, 'codex'), os.path.join(L, '02-bibbia', 'codex'))
    p = zb(L, 'struttura', '.', 'verifica')
    esito('struttura.py', 'struttura scritta: verifica', '0 / Struttura: OK', f'{p.returncode} / {p.stdout.strip().splitlines()[-1]}', sez)
    salva(r, 'architetto: struttura')
    p = zb(L, 'pronto', '.')
    esito('percorso.py', 'pronto senza diagnosi e piano: FERMO', '2 / True', f'{p.returncode} / {"rapporto-struttura.md: manca" in p.stderr}', sez)
    # separazione: diagnosi salvata nello stesso commit di una modifica alla struttura
    intesta(L, os.path.join(F, 'rapporti', 'rapporto-struttura.md'), '06-diagnostica/rapporto-struttura.md', 'diagnosta')
    intesta(L, os.path.join(F, 'rapporti', 'piano-revisione-struttura.md'), '06-diagnostica/piano-revisione-struttura.md',
            'editor-strutturale')
    open(os.path.join(L, '03-struttura', '07-tensione-ritmo.md'), 'a').write('\n')
    intesta(L, os.path.join(F, 'rapporti', 'rapporto-struttura.md'), '06-diagnostica/rapporto-struttura.md', 'diagnosta')
    intesta(L, os.path.join(F, 'rapporti', 'piano-revisione-struttura.md'), '06-diagnostica/piano-revisione-struttura.md',
            'editor-strutturale')
    salva(r, 'struttura e diagnosi insieme')
    p = zb(L, 'pronto', '.')
    esito('percorso.py', 'diagnosi nello stesso commit della struttura: FERMO (chi scrive non rivede)', '2 / True',
          f'{p.returncode} / {"stesso commit" in p.stderr}', sez)
    git(r, 'rm', '-q', f'libri/{SLUG}/06-diagnostica/rapporto-struttura.md', f'libri/{SLUG}/06-diagnostica/piano-revisione-struttura.md')
    salva(r, 'tolti i rapporti')
    intesta(L, os.path.join(F, 'rapporti', 'rapporto-struttura.md'), '06-diagnostica/rapporto-struttura.md', 'diagnosta')
    salva(r, 'diagnosta')
    intesta(L, os.path.join(F, 'rapporti', 'piano-revisione-struttura.md'), '06-diagnostica/piano-revisione-struttura.md',
            'editor-strutturale')
    salva(r, 'editor strutturale')
    p = zb(L, 'pronto', '.')
    esito('fase.py', 'pronto: struttura verificata dal motore, nessuna fermata dell\'autore: fase documenti',
          '0 / None / documenti', f'{p.returncode} / {stato(L)["gate_in_attesa"]} / {stato(L)["fase"]}', sez)
    p = zb(L, 'ok', '.')
    esito('fase.py', 'ok dopo la struttura automatica: rifiutato (nessun gate aperto)', 2, p.returncode, sez)
    esito('nuovo.py', 'documenti nati alla chiusura della struttura: bibbia / cronologia / manuale', 'True / True / True',
          ' / '.join(str(os.path.isfile(os.path.join(L, x))) for x in
                     ('02-bibbia/bibbia.md', 'cronologia.yaml', '03-architettura/manuale-di-stile.md')), sez)
    esito('nuovo.py', 'codex dal briefing (schede @char)', 3,
          sum('@char:' in open(os.path.join(L, '02-bibbia', 'codex', f), encoding='utf-8').read()
              for f in os.listdir(os.path.join(L, '02-bibbia', 'codex'))), sez)
    salva(r, 'struttura e documenti')
    # nota di direzione del direttore editoriale tra i documenti (editoriale/ruoli/01; prova di motore adattata)
    p = zb(L, 'pronto', '.')
    esito('fase.py', 'documenti con la nota di direzione: senza la nota pronto si ferma', '2 / True / documenti',
          f'{p.returncode} / {"06-diagnostica/nota-direzione.md" in p.stderr} / {stato(L)["fase"]}', sez)
    open(os.path.join(L, '06-diagnostica', 'nota-direzione.md'), 'w').write(
        '# Nota di direzione\n\nLettore: chi legge gialli di mare. Rischio: un finale troppo spiegato.\n')
    salva(r, 'direttore editoriale: nota di direzione')
    p = zb(L, 'pronto', '.')
    esito('fase.py', 'documenti (bibbia, codex, cronologia, manuale, nota di direzione): pronto senza fermata',
          '0 / pagina_campione / True', f'{p.returncode} / {stato(L)["fase"]} / '
          f'{"06-diagnostica/nota-direzione.md" in stato(L)["documenti_approvati"]}', sez)
    open(os.path.join(L, '05-revisioni', 'pagina-campione.md'), 'w').write(
        '# Pagina campione\n\nIl molo era grigio. Nives contò i colpi della catena fino a dieci.\n')
    salva(r, 'pagina campione')
    zb(L, 'pronto', '.')
    salva(r, 'pagina campione registrata')
    esito('fase.py', 'dopo la pagina campione: stesura', 'stesura', stato(L)['fase'], sez)
    # stesura con capsule
    p = zb(L, 'prepara', '.', '1')
    esito('prepara.py', 'prepara 1: scheda completa', 0, p.returncode, sez)
    prep = open(os.path.join(L, '06-diagnostica', 'preparazione', '01.md')).read()
    esito('prepara.py', 'prepara 1: codex filtrato per i tag della scena', '3 / False',
          f'{prep.count("02-bibbia/codex/")} / {"elda-corte" in prep}', sez)
    m = os.path.join(L, '04-manoscritto')
    os.makedirs(m)
    shutil.copyfile(os.path.join(F, 'capitoli', '01-il-molo.md'), os.path.join(m, '01-il-molo.md'))
    salva(r, 'scrittore: capitolo 1')
    revisione_in_stesura(r, L, m, sez)
    p = zb(L, 'esito', '.', '1')
    esito('fase.py', 'esito 1: controlli OK', 0, p.returncode, sez)
    rep1 = os.path.join(L, '06-diagnostica', 'capitoli', '01.md')
    esito('fase.py', 'conta.py resta dentro zb esito: parole del capitolo nel report (prova di motore adattata: il '
          'comando zb conta resta, come in ccr)', True,
          os.path.isfile(rep1) and 'Parole (metodo unico):' in open(rep1, encoding='utf-8').read(), sez)
    salva(r, 'esito 1')
    p = zb(L, 'prepara', '.', '2')
    esito('prepara.py', 'prepara 2 senza la capsula 1: FERMO', '2 / True', f'{p.returncode} / {"Capsula" in p.stderr}', sez)
    shutil.copyfile(os.path.join(F, 'capitoli', '02-il-registro.md'), os.path.join(m, '02-il-registro.md'))
    p = zb(L, 'esito', '.', '2')
    esito('fase.py', 'esito 2 senza la capsula 1: FERMO', '2 / True', f'{p.returncode} / {"capsula" in p.stderr}', sez)
    os.remove(os.path.join(m, '02-il-registro.md'))
    p = zb(L, 'capsula', '.', '1')
    esito('capsula.py', 'capsula 1: modello preparato con il codex nominato', '0 / True',
          f'{p.returncode} / {"@char:basilio-corte" in open(os.path.join(L, "07-capsule", "01.md")).read()}', sez)
    p = zb(L, 'capsula', '.', '1', '--verifica')
    esito('capsula.py', 'capsula 1 ancora modello: KO', 1, p.returncode, sez)
    for n in (1, 2, 3):
        if n > 1:
            nome = {2: '02-il-registro.md', 3: '03-la-lanterna.md'}[n]
            zb(L, 'prepara', '.', str(n))
            shutil.copyfile(os.path.join(F, 'capitoli', nome), os.path.join(m, nome))
            salva(r, f'scrittore: capitolo {n}')
            p = zb(L, 'esito', '.', str(n))
            if os.environ.get('ZB_DEBUG'):
                print('DEBUG esito', n, p.returncode, p.stdout[-600:], p.stderr[-600:])
            if n == 3:
                esito('fase.py', 'esito 3: avviso capitoli di lunghezza quasi uguale', True,
                      'lunghezze_uguali' in p.stdout, sez)
                esito('fase.py', 'esito 3: nessuna fermata (gate primi_capitoli non in libro.yaml)', 'True',
                      str('primi_capitoli' != stato(L)['gate_in_attesa']), sez)
                # pausa di lettura (modo automatico): dopo 3 capitoli si ferma ed elenca i file da leggere
                elenco = [f'- 04-manoscritto/{x}' for x in ('01-il-molo.md', '02-il-registro.md', '03-la-lanterna.md')]
                esito('fase.py', 'pausa di lettura dopo 3 capitoli: si ferma (gate «lettura») ed elenca i file da leggere',
                      'lettura / True / True', f'{stato(L)["gate_in_attesa"]} / {"PAUSA DI LETTURA" in p.stdout} / '
                      f'{all(x in p.stdout for x in elenco)}', sez)
                q = zb(L, 'esito', '.', '3')
                esito('fase.py', 'durante la pausa di lettura il motore non scrive: esito rifiutato', '2 / True',
                      f'{q.returncode} / {"lettura" in q.stderr}', sez)
                salva(r, 'esito 3')
                break
            zb(L, 'capsula', '.', str(n))
        shutil.copyfile(os.path.join(F, 'capsule', f'0{n}.md'), os.path.join(L, '07-capsule', f'0{n}.md'))
        p = zb(L, 'capsula', '.', str(n), '--verifica')
        if n == 1:
            esito('capsula.py', 'capsula 1 compilata: OK e registro', '0 / True',
                  f'{p.returncode} / {os.path.isfile(os.path.join(L, "07-capsule", "registro.md"))}', sez)
        salva(r, f'capsula {n}')
    p = zb(L, 'compatto', '.')
    n_righe = len(open(os.path.join(L, 'stato-compatto.md')).read().splitlines())
    if os.environ.get('ZB_DEBUG'):
        print('DEBUG compatto', p.stdout, p.stderr, open(os.path.join(L, 'stato-compatto.md')).read())
    esito('compatto.py', 'stato compatto: 15-20 righe', True, 15 <= n_righe <= 20, sez)
    salva(r, 'stesura')
    pausa_note(r, L, sez)
    p = zb(L, 'ok', '.')
    esito('fase.py', 'pausa di lettura: «ok» continua (capitoli registrati come letti)', '0 / None / 3',
          f'{p.returncode} / {stato(L)["gate_in_attesa"]} / {stato(L)["ultimo_capitolo_approvato"]}', sez)
    salva(r, 'pausa di lettura chiusa')
    esito('fase.py', 'stesura finita: struttura_manoscritto', 'struttura_manoscritto', stato(L)['fase'], sez)
    # capsula 3 e registro: promesse tutte chiuse
    zb(L, 'capsula', '.', '3')
    shutil.copyfile(os.path.join(F, 'capsule', '03.md'), os.path.join(L, '07-capsule', '03.md'))
    p = zb(L, 'capsula', '.', '3', '--verifica')
    esito('capsula.py', 'registro: nessuna promessa aperta dopo il capitolo 3', True, 'promesse aperte: nessuna' in p.stdout, sez)
    salva(r, 'capsula 3')
    # revisioni
    catena = [stato(L)['fase']]
    for fs, rap in (('struttura_manoscritto', [('rapporto-manoscritto.md', 'diagnosta', None),
                                              ('piano-revisione-manoscritto.md', 'editor-strutturale', None)]),
                    ('line', [(f'line/0{n}.md', 'line-editor', n) for n in (1, 2, 3)]),
                    ('copy', [(f'copy/0{n}.md', 'correttore-italiano', n) for n in (1, 2, 3)])):
        if fs == 'line':
            p = zb(L, 'pronto', '.')
            esito('percorso.py', 'line senza rapporti: fermo, un rapporto mancante per capitolo (prova di motore '
                  'adattata)', '2 / 3', f'{p.returncode} / {p.stderr.count("06-diagnostica/line/0")}', sez)
            # separazione: un rapporto di line editing nello stesso commit di una modifica al capitolo
            intesta(L, os.path.join(F, 'rapporti', 'line', '01.md'), '06-diagnostica/line/01.md', 'line-editor', 1)
            open(os.path.join(m, '01-il-molo.md'), 'a').write('\n')
            intesta(L, os.path.join(F, 'rapporti', 'line', '01.md'), '06-diagnostica/line/01.md', 'line-editor', 1)
            salva(r, 'capitolo e line insieme')
            for x, ru, n in rap[1:]:
                intesta(L, os.path.join(F, 'rapporti', x), f'06-diagnostica/{x}', ru, n)
                salva(r, ru)
            p = zb(L, 'pronto', '.')
            esito('percorso.py', 'line: rapporto nello stesso commit del capitolo: FERMO', '2 / True',
                  f'{p.returncode} / {"stesso commit" in p.stderr}', sez)
            git(r, 'rm', '-q', f'libri/{SLUG}/06-diagnostica/line/01.md')
            salva(r, 'tolto line 1')
            for x, ru, n in rap[1:]:
                intesta(L, os.path.join(F, 'rapporti', x), f'06-diagnostica/{x}', ru, n)
            salva(r, 'line 2-3 sul capitolo attuale')
            rap = rap[:1]
        for x, ru, n in rap:
            intesta(L, os.path.join(F, 'rapporti', x), f'06-diagnostica/{x}', ru, n)
            salva(r, ru)
        p = zb(L, 'pronto', '.')
        esito('fase.py', f'{fs}: pronto controlla i rapporti e li registra senza fermata', '0 / None',
              f'{p.returncode} / {stato(L)["gate_in_attesa"]}', sez)
        esito('fase.py', f'{fs}: proposte registrate → applicazione', 'applicazione', stato(L).get('sottofase'), sez)
        p = zb(L, 'esito', '.', '1')
        esito('fase.py', f'{fs}: esito rimisura un capitolo senza cambiare fase', f'True / {fs}',
              f'{"ricontrollata" in p.stdout} / {stato(L)["fase"]}', sez)
        salva(r, f'{fs} applicato')
        zb(L, 'pronto', '.')
        salva(r, f'fine {fs}')
        catena.append(stato(L)['fase'])
    esito('fase.py', 'dopo copy: fase bozze', 'bozze', stato(L)['fase'], sez)
    p = zb(L, 'pronto', '.')
    esito('percorso.py', 'bozze senza PDF: FERMO', '2 / True', f'{p.returncode} / {"PDF" in p.stderr}', sez)
    p = zb(L, 'canone', '.', 'proponi', 'Il pescatore non sa chi ha spento la lanterna.')
    salva(r, 'proposta di canone')
    zb(L, 'canone', '.', 'gate')
    fino_alla_fine(L)
    zb(L, 'ok', '.')
    esito('percorso.py', 'canone: un fatto in più solo dopo il gate', '2 / bozze', f'{len(stato(L)["fatti_bloccati"])} / {stato(L)["fase"]}', sez)
    salva(r, 'canone')
    p = zb(L, 'avvio', '.')
    if os.environ.get('ZB_DEBUG'):
        print('DEBUG avvio', p.stdout[-800:], p.stderr[-800:])
    esito('avvio.py', 'avvio dopo il canone (proposte non più tra i documenti approvati)', 0, p.returncode, sez)
    if shutil.which('node'):
        zb(L, 'compila', '.')
        zb(L, 'impagina', '.')
        salva(r, 'bozze impaginate')
        intesta(L, os.path.join(F, 'rapporti', 'bozze.md'), '06-diagnostica/bozze.md', 'correttore-bozze')
        salva(r, 'correttore bozze')
        p = zb(L, 'pronto', '.')
        salva(r, 'bozze registrate')
        zb(L, 'pronto', '.')
        esito('fase.py', 'bozze: proposte senza fermata, applicazione, poi chiusura', 'chiusura', stato(L)['fase'], sez)
        catena.append(stato(L)['fase'])
    else:
        saltata('fase.py', 'bozze: proposte senza fermata, applicazione, poi chiusura', 'node assente', sez)
    esito('fase.py', 'dopo la stesura: struttura_manoscritto → line → copy → bozze (→ chiusura con node; prova di '
          'motore con i nomi del pacchetto)', ' → '.join(['struttura_manoscritto', 'line', 'copy', 'bozze'] +
                                                        (['chiusura'] if shutil.which('node') else [])),
          ' → '.join(catena), sez)
    return r, L


def revisione_in_stesura(r, L, m, sez):
    """Diagnosta in fase «stesura» sul capitolo singolo e «revisione_capitolo: obbligatoria» in zb esito (P2).
    Alla fine libro.yaml e il capitolo tornano come prima; il rapporto resta in 06-diagnostica/audit/."""
    # misure del motore prima del revisore: un capitolo con un KO (frase vietata della lista nera) → non chiamare il diagnosta
    cap = os.path.join(m, '01-il-molo.md')
    testo_cap = open(cap, encoding='utf-8').read()
    open(cap, 'w', encoding='utf-8').write(testo_cap + '\nTrattenne il respiro senza accorgersene.\n')
    p = zb(L, 'ruolo', '.', 'diagnosta', '1')
    misure = os.path.join(L, '06-diagnostica', 'misure', '01.md')
    esito('ruolo.py', 'misure prima del revisore: capitolo con un KO, «non chiamare il diagnosta», nessuna prima riga, '
          'nessun file delle misure', '2 / True / False / False',
          f'{p.returncode} / {"Non chiamare il diagnosta" in p.stderr and "voce:respiro_senza_accorgersene KO" in p.stderr} / '
          f'{"Prima riga:" in p.stdout} / {os.path.isfile(misure)}', sez)
    open(cap, 'w', encoding='utf-8').write(testo_cap)
    p = zb(L, 'ruolo', '.', 'diagnosta', '1')
    esito('ruolo.py', 'diagnosta in fase stesura sul capitolo 1: ammesso, rapporto audit/01.md con la prima riga',
          '0 / True / True', f'{p.returncode} / {"Rapporto: 06-diagnostica/audit/01.md" in p.stdout} / '
          f'{"Prima riga: <!-- zb: ruolo=diagnosta; su=" in p.stdout}', sez)
    tm = open(misure, encoding='utf-8').read() if os.path.isfile(misure) else ''
    su = p.stdout.split('su=')[1][:12] if 'su=' in p.stdout else '?'
    esito('ruolo.py', 'misure superate: misure/01.md con la stessa impronta della prima riga, righe misurate e frasi '
          'finali scritte', 'True / True / True',
          f'{tm.startswith(f"<!-- zb: misure; su={su} -->")} / {"## Righe misurate" in tm and "| Frase media |" in tm} / '
          f'{os.path.isfile(os.path.join(L, "06-diagnostica", "frasi-finali", "01.md"))}', sez)
    # letture del diagnosta per il capitolo singolo: solo la sezione «File da leggere» delle misure, con il canone dentro
    sezione = tm.split('## File da leggere (solo questi)', 1)[1].split('\n## ', 1)[0] if '## File da leggere' in tm else ''
    da_leggere = [x[2:] for x in sezione.splitlines() if x.startswith('- ')]
    pr = open(os.path.join(L, '06-diagnostica', 'preparazione', '01.md'), encoding='utf-8').read()
    da_prep = [x[2:] for x in pr.split('## File da leggere', 1)[1].splitlines() if x.startswith('- ') and 'AVVISO' not in x]
    esito('percorso.py', 'letture del diagnosta (capitolo 1): capitolo, misure, frasi finali, codex filtrato; niente '
          'preparazione, manuale, scelte fisse; canone nel file (file elencati: misure / preparazione dello scrittore)',
          'True / 3 / False / True / 6 5', f'{"04-manoscritto/01-il-molo.md" in da_leggere and "06-diagnostica/frasi-finali/01.md" in da_leggere} / '
          f'{sum(x.startswith("02-bibbia/codex/") for x in da_leggere)} / '
          f'{any("manuale-di-stile" in x or "09-scelte-fisse" in x or "preparazione/" in x for x in da_leggere)} / '
          f'{"## Canone (fatti bloccati)" in tm} / {len(da_leggere)} {len(da_prep)}', sez)
    p = zb(L, 'ruolo', '.', 'diagnosta')
    esito('ruolo.py', 'diagnosta in fase stesura senza numero di capitolo: rifiutato', '2 / True',
          f'{p.returncode} / {"un capitolo alla volta" in p.stderr}', sez)
    py = os.path.join(L, 'libro.yaml')
    lb = open(py, encoding='utf-8').read()
    open(py, 'w', encoding='utf-8').write(lb.rstrip('\n') + '\nrevisione_capitolo: obbligatoria\n')
    p = zb(L, 'esito', '.', '1')
    esito('fase.py', 'revisione_capitolo obbligatoria, rapporto assente: esito fermo, capitolo non accettato',
          '2 / True / None', f'{p.returncode} / {"audit/01.md" in p.stderr and "mancante" in p.stderr} / '
          f'{stato(L)["ultimo_capitolo_scritto"]}', sez)
    sorgente = os.path.join(F, 'rapporti', 'audit-01.md')
    intesta(L, sorgente, '06-diagnostica/audit/01.md', 'diagnosta', 1)
    pa = os.path.join(L, '06-diagnostica', 'audit', '01.md')
    open(pa, 'w', encoding='utf-8').write(open(pa, encoding='utf-8').read().replace('\npassa\n', '\nnon passa\n'))
    p = zb(L, 'esito', '.', '1')
    esito('fase.py', 'revisione con «non passa»: esito fermo', '2 / True', f'{p.returncode} / {"«non passa»" in p.stderr}', sez)
    os.remove(pa)       # dopo un «non passa» sullo stesso testo zb ruolo si ferma (giro di revisione): si riparte da capo
    intesta(L, sorgente, '06-diagnostica/audit/01.md', 'diagnosta', 1)
    open(cap, 'a', encoding='utf-8').write('\n')
    p = zb(L, 'esito', '.', '1')
    esito('fase.py', 'revisione su un\'altra versione del capitolo: esito fermo', '2 / True',
          f'{p.returncode} / {"altra versione" in p.stderr}', sez)
    open(cap, 'w', encoding='utf-8').write(testo_cap)
    intesta(L, sorgente, '06-diagnostica/audit/01.md', 'diagnosta', 1)
    import percorso   # il caso valido si prova senza zb esito, che accetterebbe il capitolo prima delle prove successive
    try:
        cartella, libro, _ = comune.carica_libro(L)
        percorso.controlla_revisione_capitolo(cartella, libro, '1')
        ottenuto = 'nessun fermo'
    except comune.ErroreMotore as e:
        ottenuto = str(e)
    os.rename(misure, misure + '.via')
    try:
        percorso.controlla_revisione_capitolo(cartella, libro, '1')
        senza_misure = 'nessun fermo'
    except comune.ErroreMotore as e:
        senza_misure = 'fermo' if 'misure del motore assenti' in str(e) else str(e)
    os.rename(misure + '.via', misure)
    p = zb(L, 'agenti', 'prossimo', '.')
    open(py, 'w', encoding='utf-8').write(lb)
    esito('fase.py', 'revisione sulla versione attuale con «passa»: la revisione non ferma', 'nessun fermo', ottenuto, sez)
    esito('fase.py', 'revisione con «passa» ma senza le misure del motore: esito fermo', 'fermo', senza_misure, sez)
    esito('agenti.py', 'agenti prossimo con revisione_capitolo obbligatoria: zb ruolo diagnosta prima del revisore',
          '0 / True', f'{p.returncode} / {"diagnosta N (misure del motore prima del revisore" in p.stdout}', sez)
    # un solo giro completo: il secondo rivede solo le frasi di «## Da correggere» del primo
    g1 = os.path.join(L, '06-diagnostica', 'audit', '01-giro1.md')

    def rapporto(corpo):
        q = zb(L, 'ruolo', '.', 'diagnosta', '1')
        riga = next((x.split('Prima riga: ', 1)[1] for x in q.stdout.splitlines() if x.startswith('Prima riga: ')), '')
        open(pa, 'w', encoding='utf-8').write(riga + '\n# Revisione\n\n' + corpo)
        return q
    rapporto('## Da correggere\n\n- r.3 «Il molo era grigio.»: chiusa a sentenza\n\nnon passa\n')
    p1 = zb(L, 'ruolo', '.', 'diagnosta', '1')
    open(cap, 'a', encoding='utf-8').write('\nNives chiuse la porta del magazzino.\n')
    p2 = zb(L, 'ruolo', '.', 'diagnosta', '1')
    tm = open(misure, encoding='utf-8').read()
    esito('ruolo.py', 'giro di revisione: «non passa» sul testo non corretto fermo / dopo la correzione giro 2 con le sole '
          'frasi del primo, primo giro conservato', '2 True / 0 True True True',
          f'{p1.returncode} {"sul testo attuale" in p1.stderr} / {p2.returncode} {"Giro di revisione: 2" in p2.stdout} '
          f'{"## Giro 2: solo queste frasi" in tm and "- r.3 «Il molo era grigio.»: chiusa a sentenza" in tm} '
          f'{os.path.isfile(g1)}', sez)
    riga2 = next((x.split('Prima riga: ', 1)[1] for x in p2.stdout.splitlines() if x.startswith('Prima riga: ')), '')
    open(pa, 'w', encoding='utf-8').write(riga2 + '\n# Revisione 2\n\n## Da correggere\n\n- r.3: non risolta\n\nnon passa\n')
    open(cap, 'a', encoding='utf-8').write('\nNives spense la luce del magazzino.\n')
    p3 = zb(L, 'ruolo', '.', 'diagnosta', '1')
    p4 = zb(L, 'ruolo', '.', 'diagnosta', '1', '--nuovo-giro')
    esito('ruolo.py', 'secondo giro con «non passa»: fermo, decide l\'autore / --nuovo-giro: di nuovo un giro completo',
          '2 True / 0 True False', f'{p3.returncode} {"due giri di revisione fatti" in p3.stderr} / {p4.returncode} '
          f'{"Giro di revisione: 1 (completo)" in p4.stdout} {os.path.isfile(g1)}', sez)
    os.remove(pa)
    rapporto('## Esito\n\nnon passa\n')
    open(cap, 'a', encoding='utf-8').write('\nNives tornò sul molo.\n')
    p5 = zb(L, 'ruolo', '.', 'diagnosta', '1')
    esito('ruolo.py', '«non passa» senza la sezione «## Da correggere»: fermo', '2 / True',
          f'{p5.returncode} / {"senza la sezione «## Da correggere»" in p5.stderr}', sez)
    open(cap, 'w', encoding='utf-8').write(testo_cap)      # come prima: capitolo originale, rapporto «passa»
    os.remove(pa)
    intesta(L, sorgente, '06-diagnostica/audit/01.md', 'diagnosta', 1)


def pausa_note(r, L, sez):
    """Pausa di lettura con le note (su una copia del repository, alla stessa pausa) e valori di pausa_lettura."""
    d = tempfile.mkdtemp(dir=TMP)
    r2 = shutil.copytree(r, os.path.join(d, 'repo'), symlinks=True)
    L2 = os.path.join(r2, os.path.relpath(L, r))
    p = zb(L2, 'correggi', '.', 'il molo va descritto di notte, come nel capitolo 1')
    note = os.path.join(L2, '06-diagnostica', 'note-lettura.md')
    esito('fase.py', 'pausa di lettura con «correggi <note>»: note scritte, gate chiuso, la scrittura riparte',
          '0 / True / None / 1', f'{p.returncode} / {os.path.isfile(note) and "di notte" in open(note).read()} / '
          f'{stato(L2)["gate_in_attesa"]} / {len(stato(L2).get("note_lettura") or [])}', sez)
    pp = zb(L2, 'prepara', '.', '3')      # il mini-libro ha 3 capitoli: le note valgono per ogni preparazione dopo la pausa
    prep = os.path.join(L2, '06-diagnostica', 'preparazione', '03.md')
    esito('prepara.py', 'dopo la pausa con le note: zb prepara le mette tra i file da leggere dello scrittore', '0 / True',
          f'{pp.returncode} / {os.path.isfile(prep) and "- 06-diagnostica/note-lettura.md" in open(prep).read()}', sez)
    ly = os.path.join(L2, 'libro.yaml')
    orig = open(ly, encoding='utf-8').read()
    open(ly, 'w', encoding='utf-8').write(orig.rstrip('\n') + '\nvoce: {slug: voce-di-prova, ambientazione: altro}\n')
    banca = os.path.join(M, 'prove', 'banca-voci-prova')

    def prepara_con(b):
        p = zb(L2, 'prepara', '.', '3', env=dict(E, ZB_BANCA_VOCI=b))
        return p, (open(prep, encoding='utf-8').read() if os.path.isfile(prep) else '')
    if os.path.isfile(prep):
        os.remove(prep)
    pp, t = prepara_con(banca)       # voce di prova: sezione 6 con il solo campione, nessun esempio «debole → forte»
    esito('prepara.py', 'libro con voce senza esempi: sezioni 2, 3 e 6 e divieti, gli esempi «debole → forte» non nominati',
          '0 / True / True / False', f'{pp.returncode} / {"## Voce (banca-voci, sola lettura)" in t} / '
          f'{"sezione 6 (campione)" in t and "voci/voce-di-prova/divieti.yaml" in t} / {"debole" in t}', sez)
    d = tempfile.mkdtemp(dir=TMP)
    b2 = shutil.copytree(banca, os.path.join(d, 'banca'))
    sc = os.path.join(b2, 'voci', 'voce-di-prova', 'scheda.md')
    st = open(sc, encoding='utf-8').read()
    i = st.index('## 7.')
    open(sc, 'w', encoding='utf-8').write(st[:i] + '### 6.1 Esempi\n\n1. Debole: — Resto qui, perché da qui vedo la porta.\n'
                                          '   Forte: — Resto qui.\n2. Debole: Chiuse. Certe cose finiscono così.\n'
                                          '   Forte: Chiuse e girò la chiave.\n3. Il caso opposto, a metà riga. Debole: Lui annuì.\n'
                                          '   Forte: Il socio annuì.\n\n' + st[i:])
    pp, t = prepara_con(b2)
    esito('prepara.py', 'libro con voce con esempi: la sezione 6 nomina i 3 esempi «debole → forte» (uno a metà riga)',
          '0 / True', f'{pp.returncode} / {"3 esempi originali «versione debole → versione forte»" in t}', sez)
    os.remove(sc)
    pp, t = prepara_con(b2)
    esito('prepara.py', 'scheda della voce assente: zb prepara si ferma con il percorso', '2 / True',
          f'{pp.returncode} / {"Scheda della voce «voce-di-prova» assente" in pp.stderr}', sez)
    open(ly, 'w', encoding='utf-8').write(orig.replace('pausa_lettura: 3', 'pausa_lettura: 6'))
    p6 = zb(L2, 'stato', '.')
    open(ly, 'w', encoding='utf-8').write(orig.replace('pausa_lettura: 3', 'pausa_lettura: 5'))
    p5 = zb(L2, 'stato', '.')
    esito('fase.py', 'pausa_lettura 6 in libro.yaml: rifiutato (3-5) / 5: accettato', '2 / True / 0',
          f'{p6.returncode} / {"pausa_lettura" in p6.stderr and "3, 4, 5" in p6.stderr} / {p5.returncode}', sez)


def hook_bash(r, comando):
    dati = json.dumps({'tool_name': 'Bash', 'cwd': r, 'tool_input': {'command': comando}})
    p = subprocess.run([sys.executable, '-B', os.path.join(S, 'hook_recinto.py')], input=dati,
                       env=dict(E, CLAUDE_PROJECT_DIR=r), capture_output=True, text=True)
    return p.returncode


def cartella_unica(sez='cartella unica e recinto'):
    """Due mini-libri nello stesso repository (con una copia del motore): lavorare sul primo non tocca il
    secondo né il motore. Recinto su Bash, controllo pre-commit, avvio, salva."""
    r = repo()
    shutil.copytree(M, os.path.join(r, 'motore'), ignore=shutil.ignore_patterns('__pycache__'))
    salva(r, 'motore')
    git(r, 'branch', '-f', 'motore')
    git(r, 'push', '-q', 'origin', 'motore')
    git(r, 'fetch', '-q', 'origin')
    mz = os.path.join(r, 'motore', 'zb')
    zbr = lambda *a: subprocess.run([sys.executable, '-B', mz, *a], cwd=r, env=E, capture_output=True, text=True)
    for slug in ('primo', 'secondo'):
        L = os.path.join(r, 'libri', slug)
        os.makedirs(L)
        shutil.copyfile(os.path.join(F, 'briefing.md'), os.path.join(L, 'briefing.md'))
        p = zbr('nuovo', f'libri/{slug}/briefing.md')
    salva(r, 'due libri')
    p = zbr('lavoro', 'libro', 'primo')
    esito('hook_recinto.py', 'zb lavoro libro: installa il controllo pre-commit', True, 'pre-commit installato' in p.stdout, sez)
    prima = {f: open(os.path.join(dp, f), 'rb').read() for dp, _, fs in os.walk(os.path.join(r, 'libri', 'secondo'))
             for f in fs}
    p = zbr('avvio', 'libri/primo')
    esito('avvio.py', 'avvio sul primo libro', 0, p.returncode, sez)
    p = zbr('avvio', 'libri/secondo')
    esito('avvio.py', 'avvio sul secondo libro con il primo attivo: FERMO (un solo libro per sessione)', '2 / True',
          f'{p.returncode} / {"Un solo libro" in p.stderr}', sez)
    esito('hook_recinto.py', 'Bash: echo > libri/secondo/… / > motore/… / > libri/primo/… / > /tmp/…',
          '2 / 2 / 0 / 0', f'{hook_bash(r, "echo x > libri/secondo/nota.md")} / {hook_bash(r, "echo x >> motore/nota.md")} / '
          f'{hook_bash(r, "echo x > libri/primo/02-bibbia/nota.md")} / {hook_bash(r, "echo x > /tmp/zb-nota.txt")}', sez)
    esito('hook_recinto.py', 'Bash: sed -i, cp verso, mv, rm, tee fuori dal libro attivo', '2 / 2 / 2 / 2 / 2',
          f'{hook_bash(r, "sed -i s/a/b/ libri/secondo/libro.yaml")} / {hook_bash(r, "cp libri/primo/libro.yaml libri/secondo/x.yaml")} / '
          f'{hook_bash(r, "mv libri/secondo/stato.yaml /tmp/s.yaml")} / {hook_bash(r, "rm -f motore/zb")} / '
          f'{hook_bash(r, "date | tee motore/dati/x.txt")}', sez)
    # scrittura che il recinto non vede (script): la ferma il pre-commit e la vede zb avvio
    open(os.path.join(r, 'libri', 'secondo', 'scritto-da-script.md'), 'w').write('fuori\n')
    p = zbr('avvio', 'libri/primo')
    esito('avvio.py', 'file modificato fuori dal libro attivo: FERMO', '2 / True',
          f'{p.returncode} / {"scritto-da-script.md" in p.stderr}', sez)
    git(r, 'add', '-A')
    p = git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'tentativo')
    esito('precommit.py', 'commit con un file del secondo libro: rifiutato dal pre-commit', '1 / True',
          f'{p.returncode} / {"RECINTO (pre-commit)" in p.stderr}', sez)
    git(r, 'reset', '-q')
    p = zbr('salva', 'libri/primo', 'prova')
    esito('salva.py', 'zb salva con un file fuori dal recinto: rifiutato', '2 / True',
          f'{p.returncode} / {"fuori dal recinto" in p.stderr}', sez)
    os.remove(os.path.join(r, 'libri', 'secondo', 'scritto-da-script.md'))
    open(os.path.join(r, 'libri', 'primo', '00-progetto', 'nota.md'), 'w').write('nota del primo libro\n')
    p = zbr('salva', 'libri/primo', 'nota')
    esito('salva.py', 'zb salva dentro il libro: commit e push', '0 / True',
          f'{p.returncode} / {"libri/primo/00-progetto/nota.md" in git(r, "show", "--name-only", "--format=").stdout}', sez)
    dopo = {f: open(os.path.join(dp, f), 'rb').read() for dp, _, fs in os.walk(os.path.join(r, 'libri', 'secondo'))
            for f in fs}
    esito('recinto', 'il secondo libro è identico dopo il lavoro sul primo', True, prima == dopo, sez)
    c = git(r, 'diff', '--name-only', 'origin/motore', 'HEAD', '--', 'motore').stdout.strip()
    esito('recinto', 'il motore è identico dopo il lavoro sul primo', '', c, sez)
    # commit di un file fuori dal libro fatto aggirando il pre-commit: lo vede zb avvio (rispetto a origin/motore)
    open(os.path.join(r, 'motore', 'nota.md'), 'w').write('x\n')
    git(r, 'add', '-A')
    git(r, '-c', 'commit.gpgsign=false', 'commit', '-q', '--no-verify', '-m', 'aggirato')
    git(r, 'push', '-q')
    p = zbr('avvio', 'libri/primo')
    esito('avvio.py', 'commit fuori dal libro (pre-commit aggirato): AVVISO rispetto a origin/motore', True,
          'motore/nota.md' in p.stdout, sez)
    # lavoro sul motore: libri/ fuori dal recinto
    zbr('lavoro', 'motore')
    esito('hook_recinto.py', 'lavoro sul motore: Bash su libri/ bloccato, su motore/ consentito', '2 / 0',
          f'{hook_bash(r, "echo x > libri/primo/n.md")} / {hook_bash(r, "echo x > motore/n.md")}', sez)


def agenti_e_comandi(sez='agenti e comandi'):
    """Sul ramo «motore» gli agenti restano spenti; sul ramo di un libro si installano con l'ok."""
    r = repo('motore')
    p = zb(r, 'agenti', 'attiva', '--ok', '--progetto', r)
    esito('agenti.py', 'ramo motore: attiva rifiutato, nessun .claude/', '2 / False',
          f'{p.returncode} / {os.path.exists(os.path.join(r, ".claude"))}', sez)
    esito('agenti.py', 'repository del motore (questo): nessun .claude/agents né .claude/commands', 'False / False',
          f'{os.path.exists(os.path.join(comune.radice_git(M), ".claude", "agents"))} / '
          f'{os.path.exists(os.path.join(comune.radice_git(M), ".claude", "commands"))}', sez)
    r = repo('libro-prova')
    p = zb(r, 'agenti', 'attiva', '--progetto', r)
    esito('agenti.py', 'ramo del libro senza --ok: niente scritto', '0 / False',
          f'{p.returncode} / {os.path.exists(os.path.join(r, ".claude"))}', sez)
    p = zb(r, 'agenti', 'attiva', '--ok', '--progetto', r)
    ag = sorted(os.listdir(os.path.join(r, '.claude', 'agents')))
    co = sorted(os.listdir(os.path.join(r, '.claude', 'commands')))
    esito('agenti.py', 'installati: agenti / comandi (10 + 2 di traduzione)', '12 / [\'diagnosi.md\', \'handover.md\', \'revisiona.md\', \'scrivi-capitolo.md\']',
          f'{len(ag)} / {co}', sez)
    fm = []
    for f in ag:
        testo = open(os.path.join(r, '.claude', 'agents', f), encoding='utf-8').read()
        d = yaml.safe_load(testo.split('---')[1])
        fm.append(bool(d.get('name')) and bool(d.get('description')) and d.get('model') in ('opus', 'sonnet', 'haiku'))
    esito('agenti.py', 'frontmatter: name, description e model (da modelli-ruoli.yaml) in ogni agente', True, all(fm), sez)
    cap = yaml.safe_load(open(os.path.join(r, '.claude', 'agents', 'capsula.md')).read().split('---')[1])
    arch = yaml.safe_load(open(os.path.join(r, '.claude', 'agents', 'architetto-struttura.md')).read().split('---')[1])
    esito('agenti.py', 'modelli: capsula leggero, architetto forte', 'haiku / opus', f'{cap["model"]} / {arch["model"]}', sez)
    testi = {f: open(os.path.join(r, '.claude', 'commands', f), encoding='utf-8').read() for f in co}
    esito('comandi', '/scrivi-capitolo: avvio, prepara, scrittore-voce, esito, capsula, compatto, salva; poi si ferma',
          True, all(x in testi['scrivi-capitolo.md'] for x in ('zb avvio', 'zb prepara', 'scrittore-voce', 'zb esito',
                                                            'zb capsula', 'zb compatto', 'zb salva', '/revisiona')), sez)
    esito('comandi', '/revisiona: line-editor e correttore-italiano separati, solo dopo l\'ok, filtri sotto il manuale',
          True, all(x in testi['revisiona.md'] for x in ('line-editor', 'correttore-italiano', 'ok', 'manuale', 'Edit')), sez)
    esito('comandi', '/diagnosi: sola lettura, solo il rapporto', True,
          'Nessuna modifica al testo' in testi['diagnosi.md'] and 'diagnosta' in testi['diagnosi.md'], sez)
    esito('comandi', '/handover: sette sezioni, salva, dichiara che non azzera il contesto', True,
          'non può azzerare il contesto' in testi['handover.md'] and 'Ripartenza' in testi['handover.md']
          and 'zb salva' in testi['handover.md'], sez)
    p = zb(r, 'agenti', 'disattiva', '--progetto', r)
    esito('agenti.py', 'disattiva: tolti i file del motore', False, os.path.exists(os.path.join(r, '.claude', 'agents')), sez)


def consumo_capsule(sez='consumo e capsule'):
    """Misura reale sul mini-libro: righe e parole da leggere per il capitolo 3 con e senza capsule."""
    r = repo()
    L, _ = nasce(r)
    copia(os.path.join(F, 'struttura'), os.path.join(L, '03-struttura'))
    copia(os.path.join(F, 'codex'), os.path.join(L, '02-bibbia', 'codex'))
    m = os.path.join(L, '04-manoscritto')
    os.makedirs(m)
    for f in ('01-il-molo.md', '02-il-registro.md'):
        shutil.copyfile(os.path.join(F, 'capitoli', f), os.path.join(m, f))
    os.makedirs(os.path.join(L, '07-capsule'))
    for f in ('01.md', '02.md'):
        shutil.copyfile(os.path.join(F, 'capsule', f), os.path.join(L, '07-capsule', f))
    p = zb(L, 'consumo', '.', 'confronto', '3')
    numeri = [int(x) for x in re.findall(r'(\d+) (?:righe|parole)', p.stdout)]
    esito('consumo.py', 'confronto capitolo 3: misura eseguita (4 numeri)', 4, len(numeri), sez)
    if len(numeri) == 4:
        esito('consumo.py', 'con le capsule si leggono meno parole che senza', True, numeri[1] < numeri[3], sez)
        MISURE['consumo'] = p.stdout.strip()
    salva(r, 'libro')
    zb(L, 'avvio', '.', env=dict(E, ZB_SESSIONE='misura'))
    p = zb(L, 'consumo', '.', 'registra', '--capitoli', '1,2', '--subagenti', '2', env=dict(E, ZB_SESSIONE='misura'))
    d = comune.leggi_yaml(os.path.join(L, '06-diagnostica', 'consumo.yaml'))['sessioni'][-1]
    esito('consumo.py', 'registra: capitoli, parole, righe lette, subagenti, durata', "['1', '2'] / True / True / 2 / True",
          f'{d["capitoli"]} / {d["parole_capitoli"] > 0} / {d["righe_lette"] > 0} / {d["subagenti"]} / {d["durata_minuti"] is not None}', sez)


def traduzione(sez='traduzione in inglese'):
    """Mini-libro italiano tradotto in inglese: gate «guida» prima del capitolo 1, controlli meccanici per capitolo,
    line e copy nella lingua di arrivo, scheda di fedeltà e ritraduzione a campione, chiusura in inglese."""
    r = repo()
    L, _ = nasce(r)
    copia(os.path.join(F, 'struttura'), os.path.join(L, '03-struttura'))
    copia(os.path.join(F, 'codex'), os.path.join(L, '02-bibbia', 'codex'))
    copia(os.path.join(F, 'capitoli'), os.path.join(L, '04-manoscritto'))
    copia(os.path.join(F, 'capsule'), os.path.join(L, '07-capsule'))
    salva(r, 'libro italiano')
    TR = os.path.join(F, 'traduzione-en')
    p = zb(L, 'traduci', '.', '--a', 'en', 'inizia')
    T = os.path.join(L, '08-traduzione-en')
    lt = comune.leggi_yaml(os.path.join(T, 'libro.yaml'))
    esito('traduci.py', 'inizia: libro di traduzione in 08-traduzione-en/', '0 / traduzione / en / guida',
          f'{p.returncode} / {lt["modalita"]} / {lt["lingua"]} / {stato(T)["fase"]}', sez)
    salva(r, 'traduzione avviata')
    p = zb(T, 'pronto', '.')
    esito('percorso.py', 'gate guida: guida modello e glossario vuoto: FERMO', '2 / True / True',
          f'{p.returncode} / {"ancora modello" in p.stderr} / {"traduzione mancante" in p.stderr}', sez)
    p = zb(T, 'esito', '.', '1')
    esito('fase.py', 'nessun capitolo tradotto prima del gate guida', 2, p.returncode, sez)
    shutil.copyfile(os.path.join(TR, 'guida-traduzione.md'), os.path.join(T, '00-progetto', 'guida-traduzione.md'))
    shutil.copyfile(os.path.join(TR, 'glossario.yaml'), os.path.join(T, '00-progetto', 'glossario.yaml'))
    salva(r, 'guida e glossario')
    zb(T, 'pronto', '.')
    fino_alla_fine(T)
    p = zb(T, 'ok', '.')
    esito('percorso.py', 'gate guida approvato: stesura (capitolo 1)', 'stesura', stato(T)['fase'], sez)
    salva(r, 'gate guida')
    p = zb(T, 'traduci', '.', '--a', 'en', 'prepara', '1')
    prep = open(os.path.join(T, '06-diagnostica', 'preparazione', '01.md')).read()
    esito('traduci.py', 'prepara 1: voci del glossario presenti nel capitolo', True,
          'Basilio Corte → Basilio Corte' in prep and 'Il molo → the pier' in prep, sez)
    m = os.path.join(T, '04-manoscritto')
    os.makedirs(m, exist_ok=True)
    # capitolo 2 tradotto male: paragrafo tolto, numero cambiato, nota aggiunta, parola italiana rimasta
    giusto2 = open(os.path.join(TR, 'capitoli', '02-il-registro.md')).read()
    for n, f in ((1, '01-il-molo.md'), (2, '02-il-registro.md'), (3, '03-la-lanterna.md')):
        if n == 2:
            sbagliato = giusto2.replace('“And after eleven?”\n\n', '').replace('“Did he write this?” asked Nives.\n\n', '').replace('thirty-one boats', 'thirty-one boats (31)')
            sbagliato = sbagliato.replace('Elda closed the diesel register.', 'Elda closed the diesel register della barca.')
            sbagliato += '\n[N. d. T.] Vallorna is an invented village.\n'
            open(os.path.join(m, f), 'w').write(sbagliato)
            salva(r, 'traduttore: capitolo 2 (sbagliato)')
            p = zb(T, 'esito', '.', '2')
            rep = open(os.path.join(T, '06-diagnostica', 'capitoli', '02.md')).read()
            ko = sorted(re.findall(r'(?m)^\| ([^|]+?) \| KO \|', rep))
            esito('traduci.py', 'capitolo tradotto male: KO su battute, paragrafi, numeri, residue, note', 
                  "1 / ['battute', 'note aggiunte', 'numeri e date', 'paragrafi', 'parole residue']", f'{p.returncode} / {ko}', sez)
        zb(T, 'traduci', '.', '--a', 'en', 'prepara', str(n))
        shutil.copyfile(os.path.join(TR, 'capitoli', f), os.path.join(m, f))
        salva(r, f'traduttore: capitolo {n}')
        p = zb(T, 'esito', '.', str(n))
        esito('fase.py', f'esito {n} della traduzione: controlli meccanici OK', 0, p.returncode, sez)
        salva(r, f'esito {n}')
    esito('fase.py', 'traduzione finita: line nella lingua di arrivo', 'line', stato(T)['fase'], sez)
    for fs, rap in (('line', [(f'line/0{n}.md', 'line-editor', n) for n in (1, 2, 3)]),
                    ('copy', [(f'copy/0{n}.md', 'correttore-italiano', n) for n in (1, 2, 3)]),
                    ('fedelta', [('fedelta.md', 'revisore-fedelta', None)])):
        for x, ru, n in rap:
            intesta(T, os.path.join(TR, 'rapporti', x), f'06-diagnostica/{x}', ru, n)
            salva(r, ru)
        p = zb(T, 'pronto', '.')
        esito('fase.py', f'traduzione, {fs}: gate', f'0 / {fs}', f'{p.returncode} / {stato(T)["gate_in_attesa"]}', sez)
        fino_alla_fine(T)
        zb(T, 'ok', '.')
        if fs == 'fedelta':
            os.makedirs(os.path.join(T, '06-diagnostica', 'ritraduzione'), exist_ok=True)
            shutil.copyfile(os.path.join(TR, 'ritraduzione', '01.md'), os.path.join(T, '06-diagnostica', 'ritraduzione', '01.md'))
            p = zb(T, 'traduci', '.', '--a', 'en', 'ritraduci', '1')
            esito('traduci.py', 'ritraduzione a campione: numeri uguali, nessun nome perso', 'True / True',
                  f'{"numeri_uguali True" in p.stdout} / {"nomi_persi []" in p.stdout}', sez)
        salva(r, f'{fs} applicato')
        zb(T, 'pronto', '.')
        salva(r, f'fine {fs}')
    esito('fase.py', 'traduzione: dopo la fedeltà, chiusura', 'chiusura', stato(T)['fase'], sez)
    if shutil.which('node'):
        p1, p2 = zb(T, 'compila', '.'), zb(T, 'impagina', '.')
        esito('compila.py', 'edizione inglese: compila e impagina', '0 / 0', f'{p1.returncode} / {p2.returncode}', sez)
    else:
        saltata('compila.py', 'edizione inglese: compila e impagina', 'node assente', sez)
    p = zb(L, 'traduci', '.', '--a', 'en', 'confronta', os.path.join(F, 'capitoli'), os.path.join(TR, 'capitoli'))
    esito('traduci.py', 'confronta: misure di voce di due cartelle', 0, p.returncode, sez)
    MISURE['confronto_voce'] = p.stdout.strip()


def correttore(sez='correttore e anti-IA'):
    """zb ortografia (italiano e inglese, livelli a e b) e audit anti-IA su testi con errori e schemi voluti."""
    r = repo()
    L, _ = nasce(r)
    copia(os.path.join(F, 'struttura'), os.path.join(L, '03-struttura'))
    copia(os.path.join(F, 'capitoli'), os.path.join(L, '04-manoscritto'))
    c1 = os.path.join(L, '04-manoscritto', '01-il-molo.md')
    open(c1, 'a').write('\nQuesta e la prova di un errrore voluto.\n')
    p = zb(L, 'ortografia', '.')
    rep = open(os.path.join(L, '06-diagnostica', 'controllo-ortografico.md')).read()
    esito('ortografia.py', 'italiano, livello a: refuso trovato da Hunspell it_IT', 'True / True',
          f'{"| errrore |" in rep} / {"(a) Hunspell it_IT | sì" in rep}', sez)
    if os.environ.get('ZB_LANGUAGETOOL'):
        esito('ortografia.py', 'italiano, livello b: LanguageTool eseguito sul libro', True, '(b) LanguageTool | sì' in rep, sez)
    else:
        saltata('ortografia.py', 'italiano, livello b: LanguageTool eseguito sul libro', 'LanguageTool assente (ZB_LANGUAGETOOL non impostata)', sez)
    esito('ortografia.py', 'checklist per la lettura mirata (e/è, accordi, parole vere)', True, 'e/è' in rep or '«è»' in rep, sez)
    # audit anti-IA: capitolo con frasi uguali e aperture uguali; tre chiusure uguali di fila
    shutil.copyfile(os.path.join(F, 'capitoli', '01-il-molo.md'), c1)
    monotono = '## 2\n*Vallorna — mercoledì 5 ottobre*\n<!-- zb: chiusura=D -->\n\n' + ' '.join(
        ['Nives guardò il mare dal molo grigio.'] * 30) + ' Chi era stato?\n'
    open(os.path.join(L, '04-manoscritto', '02-il-registro.md'), 'w').write(monotono)
    for f, sig in (('03-la-lanterna.md', 'D'),):
        t = open(os.path.join(L, '04-manoscritto', f)).read().replace('chiusura=X', 'chiusura=' + sig)
        t = t.rstrip('\n').rstrip('.') + '?\n'
        open(os.path.join(L, '04-manoscritto', f), 'w').write(t)
    p = zb(L, 'antiia', '.')
    righe_out = {x.split(':')[0]: x for x in p.stdout.splitlines()}
    esito('antiia.py', 'capitolo monotono: P1 variazione_frasi e P2 aperture_uguali', 'True / True',
          f'{"P1 variazione_frasi" in righe_out.get("2", "")} / {"P2 aperture_uguali" in righe_out.get("2", "")}', sez)
    esito('antiia.py', 'tre capitoli di fila con la stessa chiusura: P0 al terzo', True,
          'P0 chiusure_uguali' in righe_out.get('3', ''), sez)
    esito('antiia.py', 'audit non distruttivo: il capitolo resta identico', monotono,
          open(os.path.join(L, '04-manoscritto', '02-il-registro.md')).read(), sez)
    p = zb(L, 'antiia', '.', '1')
    esito('antiia.py', 'capitolo del mini-libro: nessuna P0/P1 (soglie tarate)', True,
          'P0' not in p.stdout.splitlines()[0] and 'P1' not in p.stdout.splitlines()[0], sez)
    # inglese
    T = os.path.join(r, 'libri', 'inglese')
    os.makedirs(T)
    b = open(os.path.join(F, 'briefing.md')).read().replace('Lingua: it', 'Lingua: en').replace('Lingue target: en', 'Lingue target:')
    open(os.path.join(T, 'briefing.md'), 'w').write(b)
    p = zb(r, 'nuovo', 'libri/inglese/briefing.md')
    esito('nuovo.py', 'libro scritto direttamente in inglese: struttura con modelli in inglese', '0 / True',
          f'{p.returncode} / {"Chapter outline" in open(os.path.join(T, "03-struttura", "05-scaletta.md")).read()}', sez)
    copia(os.path.join(F, 'traduzione-en', 'capitoli'), os.path.join(T, '04-manoscritto'))
    c = os.path.join(T, '04-manoscritto', '01-il-molo.md')
    open(c, 'a').write('\nThis is a tset of the speling.\n')
    zb(T, 'ortografia', '.')
    rep = open(os.path.join(T, '06-diagnostica', 'controllo-ortografico.md')).read()
    esito('ortografia.py', 'inglese, livello a: refusi trovati con Hunspell en_US', 'True / True',
          f'{"| tset |" in rep and "| speling |" in rep} / {"(a) Hunspell en_US | sì" in rep}', sez)
    p = zb(T, 'capitolo', '.', '1')
    esito('capitolo.py', 'inglese: controlli del capitolo eseguiti (battute con le virgolette)', True,
          os.path.isfile(os.path.join(T, '06-diagnostica', 'capitoli', '01.md')), sez)


MISURE = {}
SEZIONI = [percorso, cartella_unica, agenti_e_comandi, consumo_capsule, traduzione, correttore]


def esegui_sezione(f):
    try:
        f()
    except Exception as e:      # una sezione che si rompe è un KO, non ferma le altre
        import traceback
        righe.append((f.__name__, 'prove_editoriale.py', 'sezione completata', 'sì',
                      f'eccezione: {type(e).__name__}: {e} @ {traceback.extract_tb(e.__traceback__)[-1].lineno}', 'KO'))


def main():
    global TMP
    TMP = tempfile.mkdtemp(prefix='zb-prove-ed-')
    try:
        for f in SEZIONI:
            esegui_sezione(f)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    return righe


if __name__ == '__main__':
    for r in main():
        if r[5] != 'OK' or '--tutto' in sys.argv:
            print(' | '.join(r))
    print(f'{sum(1 for r in righe if r[5] == "OK")}/{sum(1 for r in righe if r[5] != "SALTATA")} OK')
    for k, v in MISURE.items():
        print(f'MISURA {k}: {v}')

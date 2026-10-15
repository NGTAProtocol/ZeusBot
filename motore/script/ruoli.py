"""Ruoli editoriali e separazione tra chi scrive e chi revisiona (motore/editoriale/00-percorso.md).

Una sessione di Claude Code = un ruolo. Tutto sta in <libro>/.zb/ (ignorata da git):
- ruoli.yaml      sessione → {ruolo, data}: lo scrive «zb avvio <libro> [--ruolo R]»;
- scritture.log   «sessione<TAB>file» per ogni file del libro scritto in 03-struttura/, 04-manoscritto/,
                  06-diagnostica/, 07-capsule/: lo scrivono l'hook del recinto (Write, Edit) e «zb esito».
Regole:
- una sessione che ha già un ruolo non ne prende un altro (sempre FERMO);
- chi ha scritto un testo non lo revisiona nella stessa sessione: al gate (pronto) e all'avvio di un ruolo
  di revisione si confrontano le sessioni che hanno scritto il testo e quelle che hanno scritto la revisione.
  Modalità in dati/hook.yaml, «separazione_ruoli: avviso | blocco».
Con la sessione «locale» (nessun hook SessionStart né ZB_SESSIONE) le sessioni non si distinguono:
il controllo dà un avviso e non blocca.
Uso come comando: ruoli.py <libro> stato
"""
import datetime
import os
import re
import sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

RUOLI = {
    'direttore-editoriale': {'file': '01-direttore-editoriale.md', 'tipo': 'scrive'},
    'architetto-struttura': {'file': '02-architetto-struttura.md', 'tipo': 'scrive'},
    'scrittore-voce': {'file': '03-scrittore-voce.md', 'tipo': 'scrive'},
    'editor-strutturale': {'file': '04-editor-strutturale.md', 'tipo': 'revisiona'},
    'line-editor': {'file': '05-line-editor.md', 'tipo': 'revisiona'},
    'correttore-italiano': {'file': '06-correttore-italiano.md', 'tipo': 'revisiona'},
    'correttore-bozze': {'file': '07-correttore-bozze.md', 'tipo': 'revisiona'},
    'motore': {'file': None, 'tipo': 'meccanico'},     # chiusura meccanica, solo comandi zb
}
DA_FASE = {'struttura': 'architetto-struttura', 'documenti': 'direttore-editoriale',
           'pagina_campione': 'scrittore-voce', 'stesura': 'scrittore-voce',
           'revisione_manoscritto': 'editor-strutturale', 'line': 'line-editor', 'copy': 'correttore-italiano',
           'bozze': 'correttore-bozze', 'chiusura': 'motore', 'chiuso': 'motore'}
TRACCIATE = ('03-struttura/', '04-manoscritto/', '06-diagnostica/', '07-capsule/')
# testo scritto → revisione che non può nascere nella stessa sessione
REVISIONI = {'struttura': ('03-struttura/', '06-diagnostica/revisione-struttura.md'),
             'struttura_manoscritto': ('04-manoscritto/', '06-diagnostica/revisione-manoscritto.md'),
             'line': ('04-manoscritto/', '06-diagnostica/line/'),
             'copy': ('04-manoscritto/', '06-diagnostica/copy/'),
             'bozze': ('04-manoscritto/', '06-diagnostica/bozze.md')}
# ruolo di revisione → cosa non deve aver scritto la stessa sessione
NON_SCRITTO = {'editor-strutturale': ('03-struttura/', '04-manoscritto/'), 'line-editor': ('04-manoscritto/',),
               'correttore-italiano': ('04-manoscritto/',), 'correttore-bozze': ('04-manoscritto/',)}


def modalita():
    p = os.path.join(comune.radice_motore(), 'dati', 'hook.yaml')
    for riga in open(p, encoding='utf-8'):
        m = re.match(r'^separazione_ruoli:\s*(\w+)', riga)
        if m:
            return m.group(1)
    return 'avviso'


def _zb(cartella):
    return comune.prepara_zb(cartella)


def leggi_ruoli(cartella):
    p = os.path.join(cartella, '.zb', 'ruoli.yaml')
    return (comune.leggi_yaml(p) or {}) if os.path.isfile(p) else {}


def registra_ruolo(cartella, sid, ruolo):
    """Registra il ruolo della sessione; FERMO se la sessione ne ha già un altro."""
    if ruolo not in RUOLI:
        raise comune.ErroreMotore(f'Ruolo «{ruolo}» sconosciuto. Ruoli: {", ".join(RUOLI)}')
    tutti = leggi_ruoli(cartella)
    prima = (tutti.get(sid) or {}).get('ruolo')
    if prima and prima != ruolo and sid != 'locale':
        raise comune.ErroreMotore(f'Questa sessione ha già il ruolo «{prima}»: un ruolo per sessione. Per fare '
                                  f'«{ruolo}»: salva, apri una sessione nuova, zb avvio, riga «Letto».')
    tutti[sid] = {'ruolo': ruolo, 'data': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
    p = os.path.join(_zb(cartella), 'ruoli.yaml')
    with open(p, 'w', encoding='utf-8') as f:
        yaml.safe_dump(tutti, f, sort_keys=True, allow_unicode=True)
    return prima


def registra_scrittura(cartella, sid, rel):
    rel = rel.replace(os.sep, '/')
    if not rel.startswith(TRACCIATE):
        return
    with open(os.path.join(_zb(cartella), 'scritture.log'), 'a', encoding='utf-8') as f:
        f.write(f'{sid}\t{rel}\n')


def scritture(cartella):
    p = os.path.join(cartella, '.zb', 'scritture.log')
    out = []
    if os.path.isfile(p):
        for r in open(p, encoding='utf-8'):
            if '\t' in r:
                sid, rel = r.rstrip('\n').split('\t', 1)
                out.append((sid, rel))
    return out


def sessioni_che_hanno_scritto(cartella, prefisso):
    return {sid for sid, rel in scritture(cartella) if rel.startswith(prefisso)}


def _esito(msg):
    if modalita() == 'blocco':
        raise comune.ErroreMotore('SEPARAZIONE DEI RUOLI: ' + msg)
    print('AVVISO separazione dei ruoli: ' + msg)
    return msg


def controlla_separazione_gate(cartella, gate, docs=None):
    """Al «pronto» di un gate di revisione: la revisione non è scritta da chi ha scritto il testo."""
    if gate not in REVISIONI:
        return None
    testo, revisione = REVISIONI[gate]
    autori = sessioni_che_hanno_scritto(cartella, testo)
    revisori = sessioni_che_hanno_scritto(cartella, revisione)
    comuni = sorted((autori & revisori) - {'locale'})
    if comuni:
        return _esito(f'gate «{gate}»: la sessione {", ".join(comuni)} ha scritto sia {testo} sia {revisione}. '
                      'Chi scrive non revisiona il proprio testo nella stessa sessione.')
    if 'locale' in autori & revisori:
        print('AVVISO separazione dei ruoli: sessione non identificata («locale»): non posso distinguere chi ha '
              'scritto da chi ha revisionato (attiva gli hook o imposta ZB_SESSIONE).')
    return None


def controlla_avvio(cartella, sid, ruolo):
    """All'avvio di un ruolo di revisione: la stessa sessione non deve aver scritto il testo da revisionare."""
    if ruolo not in NON_SCRITTO or sid == 'locale':
        return None
    scritti = [p for p in NON_SCRITTO[ruolo] if sid in sessioni_che_hanno_scritto(cartella, p)]
    if scritti:
        return _esito(f'la sessione {sid} ha scritto in {", ".join(scritti)} e ora chiede il ruolo «{ruolo}». '
                      'Apri una sessione nuova per revisionare.')
    return None


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2 or args[1] != 'stato':
        raise comune.ErroreMotore('Uso: ruoli.py <libro> stato')
    cartella = comune.trova_libro(args[0])
    print(f'Modalità della separazione (dati/hook.yaml): {modalita()}')
    for sid, v in sorted(leggi_ruoli(cartella).items()):
        print(f'{sid}: {v.get("ruolo")} ({v.get("data")})')
    print(f'Scritture registrate: {len(scritture(cartella))}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

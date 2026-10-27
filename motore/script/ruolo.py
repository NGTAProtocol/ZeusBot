"""Ruoli del percorso editoriale: chi può lavorare in quale fase, la prima riga del suo rapporto, e la separazione
tra chi scrive e chi revisiona (un ruolo per sessione). Unico comando: «zb ruolo».

Uso: python3 -B ruolo.py <libro> <ruolo> [N]     (comando «zb ruolo»; non scrive nulla, tranne il diagnosta in
                                                   «stesura»: misure del capitolo prima della revisione, sotto)
     python3 -B ruolo.py <libro> stato             (modalità della separazione, ruoli delle sessioni, scritture)
Controllo per fase (ccr): si ferma (codice 2) se il ruolo non lavora nella fase attuale del libro: è il controllo
meccanico di «la scrittura non include revisione» (line-editor solo in fase «line», correttore-italiano solo in
«copy»…). Per i ruoli di revisione stampa il percorso del rapporto e la prima riga da copiare:
«<!-- zb: ruolo=<ruolo>; su=<impronta> -->», con l'impronta del testo rivisto (struttura, capitolo N o
manoscritto). «zb pronto» rifiuta un rapporto con un'impronta diversa da quella del testo attuale.
Diagnosta in fase «stesura» (capitolo N): prima le misure del motore (percorso.misure_prima_della_revisione: capitolo.py,
audit anti-IA, frasi finali); con un KO o un avviso dei divieti della voce si ferma (codice 2) e il diagnosta non
si chiama; altrimenti scrive 06-diagnostica/misure/NN.md e frasi-finali/NN.md. Frase media e ripetizioni ravvicinate
restano avvisi: compaiono tra le righe misurate e non fermano.
Un solo giro completo (percorso.giro_revisione): dopo un «non passa» e la correzione, il secondo giro rivede solo le
voci di «## Da correggere» del primo (copiato in audit/NN-giro1.md); dopo il secondo «non passa» si ferma, decide
l'autore («--nuovo-giro», dopo il suo ok, riparte da un giro completo).

Un ruolo per sessione (da motore, 971b6df). Tutto sta in <libro>/.zb/ (ignorata da git):
- ruoli.yaml      sessione → {ruolo, data}: lo scrive «zb avvio <libro> [--ruolo R]»;
- scritture.log   «sessione<TAB>file» per ogni file del libro scritto in 03-struttura/, 04-manoscritto/,
                  06-diagnostica/, 07-capsule/: lo scrivono l'hook del recinto (Write, Edit) e «zb esito».
Regole:
- una sessione che ha già un ruolo non ne prende un altro (sempre FERMO);
- chi ha scritto un testo non lo revisiona nella stessa sessione: al «pronto» delle fasi con rapporti e
  all'avvio di un ruolo di revisione si confrontano le sessioni che hanno scritto il testo e quelle che hanno
  scritto la revisione. Modalità in dati/hook.yaml, «separazione_ruoli: avviso | blocco».
Con la sessione «locale» (nessun hook SessionStart né ZB_SESSIONE) le sessioni non si distinguono:
il controllo dà un avviso e non blocca.
"""
import datetime
import os
import re
import sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import percorso  # noqa: E402

# ruolo → file in motore/editoriale/ e tipo (scrive, revisiona, meccanico)
RUOLI = {
    'diagnosta': {'file': 'ruoli/00-diagnosta.md', 'tipo': 'revisiona'},
    'direttore-editoriale': {'file': 'ruoli/01-direttore-editoriale.md', 'tipo': 'scrive'},
    'architetto-struttura': {'file': 'ruoli/02-architetto-struttura.md', 'tipo': 'scrive'},
    'scrittore-voce': {'file': 'ruoli/03-scrittore-voce.md', 'tipo': 'scrive'},
    'editor-strutturale': {'file': 'ruoli/04-editor-strutturale.md', 'tipo': 'revisiona'},
    'line-editor': {'file': 'ruoli/05-line-editor.md', 'tipo': 'revisiona'},
    'correttore-italiano': {'file': 'ruoli/06-correttore-italiano.md', 'tipo': 'revisiona'},
    'correttore-bozze': {'file': 'ruoli/07-correttore-bozze.md', 'tipo': 'revisiona'},
    'capsula': {'file': 'agenti/capsula.md', 'tipo': 'scrive'},
    'traduttore': {'file': 'lingue/agenti/traduttore.md', 'tipo': 'scrive'},
    'revisore-fedelta': {'file': 'lingue/agenti/revisore-fedelta.md', 'tipo': 'revisiona'},
    'motore': {'file': None, 'tipo': 'meccanico'},     # chiusura meccanica, solo comandi zb
    'regia': {'file': None, 'tipo': 'regia'},          # 2026-10-27: orchestra gli agenti (/capitolo), non scrive prosa
}
DA_FASE = {'struttura': 'architetto-struttura', 'documenti': 'direttore-editoriale',
           'pagina_campione': 'scrittore-voce', 'guida': 'traduttore', 'stesura': 'scrittore-voce',
           'struttura_manoscritto': 'diagnosta', 'line': 'line-editor', 'copy': 'correttore-italiano',
           'bozze': 'correttore-bozze', 'fedelta': 'revisore-fedelta', 'chiusura': 'motore', 'chiuso': 'motore'}
TRACCIATE = ('03-struttura/', '04-manoscritto/', '06-diagnostica/', '07-capsule/')
# fase con rapporti → (testo scritto, revisioni che non possono nascere nella stessa sessione)
REVISIONI = {'struttura': ('03-struttura/', ('06-diagnostica/rapporto-struttura.md',
                                              '06-diagnostica/piano-revisione-struttura.md')),
             'struttura_manoscritto': ('04-manoscritto/', ('06-diagnostica/rapporto-manoscritto.md',
                                                           '06-diagnostica/piano-revisione-manoscritto.md')),
             'line': ('04-manoscritto/', ('06-diagnostica/line/',)),
             'copy': ('04-manoscritto/', ('06-diagnostica/copy/',)),
             'bozze': ('04-manoscritto/', ('06-diagnostica/bozze.md',))}
# ruolo di revisione → cosa non deve aver scritto la stessa sessione
NON_SCRITTO = {'diagnosta': ('03-struttura/', '04-manoscritto/'), 'editor-strutturale': ('03-struttura/', '04-manoscritto/'),
               'line-editor': ('04-manoscritto/',), 'correttore-italiano': ('04-manoscritto/',),
               'correttore-bozze': ('04-manoscritto/',)}
REVISORI = {r for r, v in RUOLI.items() if v['tipo'] == 'revisiona'}


# ---------------------------------------------------------------- un ruolo per sessione (da motore)

def modalita():
    p = os.path.join(comune.radice_motore(), 'dati', 'hook.yaml')
    for riga in open(p, encoding='utf-8'):
        m = re.match(r'^separazione_ruoli:\s*(\w+)', riga)
        if m:
            return m.group(1)
    return 'avviso'


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
    with open(os.path.join(comune.prepara_zb(cartella), 'ruoli.yaml'), 'w', encoding='utf-8') as f:
        yaml.safe_dump(tutti, f, sort_keys=True, allow_unicode=True)
    return prima


def registra_scrittura(cartella, sid, rel):
    rel = rel.replace(os.sep, '/')
    if not rel.startswith(TRACCIATE):
        return
    with open(os.path.join(comune.prepara_zb(cartella), 'scritture.log'), 'a', encoding='utf-8') as f:
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


def sessioni_che_hanno_scritto(cartella, prefissi):
    prefissi = (prefissi,) if isinstance(prefissi, str) else tuple(prefissi)
    return {sid for sid, rel in scritture(cartella) if rel.startswith(prefissi)}


def _esito(msg):
    if modalita() == 'blocco':
        raise comune.ErroreMotore('SEPARAZIONE DEI RUOLI: ' + msg)
    print('AVVISO separazione dei ruoli: ' + msg)
    return msg


def controlla_separazione_gate(cartella, fase):
    """Al «pronto» di una fase con rapporti: la revisione non è scritta da chi ha scritto il testo."""
    if fase not in REVISIONI:
        return None
    testo, revisioni = REVISIONI[fase]
    autori = sessioni_che_hanno_scritto(cartella, testo)
    revisori = sessioni_che_hanno_scritto(cartella, revisioni)
    comuni = sorted((autori & revisori) - {'locale'})
    if comuni:
        return _esito(f'fase «{fase}»: la sessione {", ".join(comuni)} ha scritto sia {testo} sia '
                      f'{" / ".join(revisioni)}. Chi scrive non revisiona il proprio testo nella stessa sessione.')
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


def stato_ruoli(cartella):
    print(f'Modalità della separazione (dati/hook.yaml): {modalita()}')
    for sid, v in sorted(leggi_ruoli(cartella).items()):
        print(f'{sid}: {v.get("ruolo")} ({v.get("data")})')
    print(f'Scritture registrate: {len(scritture(cartella))}')
    return 0


# ---------------------------------------------------------------- comando

def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2:
        raise comune.ErroreMotore('Uso: ruolo.py <libro> <ruolo> [N] | <libro> stato. Ruoli: '
                                  + ', '.join(percorso.FASI_RUOLO))
    if args[1] == 'stato':
        return stato_ruoli(comune.trova_libro(args[0]))
    cartella, libro, profilo = comune.carica_libro(args[0])
    ruolo, n = args[1], (args[2] if len(args) > 2 else None)
    if not percorso.attivo(libro):
        raise comune.ErroreMotore('Il libro non segue il percorso editoriale (manca «percorso: editoriale» in libro.yaml).')
    if ruolo not in percorso.FASI_RUOLO:
        raise comune.ErroreMotore(f'Ruolo sconosciuto «{ruolo}». Ruoli: ' + ', '.join(percorso.FASI_RUOLO))
    stato = comune.leggi_yaml(os.path.join(cartella, 'stato.yaml'))
    fs = stato['fase']
    if fs not in percorso.FASI_RUOLO[ruolo]:
        raise comune.ErroreMotore(f'Il ruolo «{ruolo}» non lavora in fase «{fs}» (solo in: '
                                  f'{", ".join(percorso.FASI_RUOLO[ruolo])}). Chi scrive non rivede: ogni revisione '
                                  'ha la sua fase, dopo la stesura.')
    if stato.get('sottofase') == 'applicazione':
        print(f'Fase «{fs}», applicazione: il ruolo «{ruolo}» applica solo le proposte approvate (modifiche puntuali).')
        return 0
    attesi = [r for r in percorso.rapporti(cartella, libro, fs)
              if r[1] == ruolo] if fs in ('struttura', *percorso.REVISIONI) else []
    if fs == 'stesura' and ruolo == 'diagnosta':     # revisione del capitolo singolo (06-diagnostica/audit/NN.md)
        if not n:
            raise comune.ErroreMotore('Uso: ruolo <libro> diagnosta <N>: in fase «stesura» il diagnosta rivede un '
                                      'capitolo alla volta')
        attesi = [percorso.rapporto_capitolo(cartella, libro, n)]
        # prima le misure del motore: con un esito bloccante si ferma e il diagnosta non si chiama
        giro = percorso.giro_revisione(cartella, libro, n, nuovo='--nuovo-giro' in argv)
        misure = percorso.misure_prima_della_revisione(cartella, libro, profilo, n, giro)
        print(f'Giro di revisione: {giro[0]}' + (f' (solo le {len(giro[1])} frasi del primo giro, in {misure})'
                                                  if giro[0] == 2 else ' (completo)'))
        print(f'Misure del motore superate: {misure} (righe misurate) e 06-diagnostica/frasi-finali/{percorso.nn(n)}.md. '
              'La sessione principale le passa al diagnosta con la prima riga qui sotto.')
        print('Ultima riga del rapporto: «passa» oppure «non passa» (con revisione_capitolo: obbligatoria la legge '
              'zb esito).')
    if fs in ('line', 'copy'):
        if not n:
            raise comune.ErroreMotore(f'Uso: ruolo <libro> {ruolo} <N> (un capitolo alla volta)')
        attesi = [r for r in attesi if r[0].endswith(f'/{percorso.nn(n)}.md')]
        if not attesi:
            raise comune.ErroreMotore(f'Capitolo «{n}» assente in 04-manoscritto')
    if not attesi:
        print(f'Ruolo «{ruolo}» ammesso in fase «{fs}». Nessun rapporto da intestare.')
        return 0
    for rel, _, testi in attesi:
        print(f'Rapporto: {rel}')
        print(f'Prima riga: <!-- zb: ruolo={ruolo}; su={percorso.impronta(cartella, testi)} -->')
        print(f'Testo rivisto: {len(testi)} file ({", ".join(testi[:3])}{"…" if len(testi) > 3 else ""})')
    print('Salva il rapporto in un commit che non tocca il testo rivisto.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

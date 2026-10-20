"""Capsule di continuità: 07-capsule/NN.md dopo ogni capitolo accettato, e il registro delle promesse.

Uso: python3 -B capsula.py <libro> <N>              prepara 07-capsule/NN.md (modello con i dati meccanici)
     python3 -B capsula.py <libro> <N> --verifica   controlla la capsula compilata e riscrive 07-capsule/registro.md
Il modello contiene le sezioni (eventi; personaggi presenti e cosa sanno; informazioni date; promesse aperte;
promesse chiuse; cosa cambia; stato emotivo; ultima immagine) e i dati che lo script ricava da solo: parole,
schede del codex nominate nel testo, intestazione del capitolo. Le frasi le scrive l'agente «capsula»
(circa 180 parole), togliendo la riga «<!-- zb: modello -->».
Le promesse si scrivono con il tag «@prom:<id>». Il registro (idea del RECORD.md di Scriven, MIT, riscritta)
elenca le promesse aperte e chiuse capitolo per capitolo; una promessa chiusa prima di essere aperta è KO.
Scrittore e revisori leggono le capsule, non i capitoli precedenti interi (motore/editoriale/risparmio-token.md).
"""
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import conta  # noqa: E402

CARTELLA = '07-capsule'
SEZIONI = {
    'it': ['Eventi', 'Personaggi presenti e cosa sanno', 'Informazioni date al lettore', 'Promesse aperte',
           'Promesse chiuse', 'Cosa cambia', 'Stato emotivo', 'Ultima immagine'],
    'en': ['Events', 'Characters present and what they know', 'Information given to the reader', 'Promises opened',
           'Promises closed', 'What changes', 'Emotional state', 'Last image'],
}
MINIMO, MASSIMO = 120, 250
PROM = re.compile(r'@prom:([a-z0-9][a-z0-9\-]*)')


def rel(n):
    return f'{CARTELLA}/{int(n):02d}.md'


def lingua(libro):
    return 'en' if libro.get('lingua') == 'en' else 'it'


def nominati(cartella, testo):
    """Tag del codex il cui nome (o un alias, o la prima parola del nome di un personaggio) compare nel testo."""
    import codex
    out = []
    for (tipo, i), v in codex.schede(cartella).items():
        nomi = [v['nome']] + v['alias']
        if tipo == 'char' and v['nome'].split():
            nomi.append(v['nome'].split()[0])
        nomi = [re.sub(r'^(il|lo|la|l\'|the)\s*', '', x, flags=re.I) for x in nomi]
        if any(x and re.search(r'(?<!\w)' + re.escape(x) + r'(?!\w)', testo, re.I) for x in nomi):
            out.append(f'@{tipo}:{i}')
    return out


def prepara(cartella, libro, n):
    unita = dict(comune.unita(cartella, libro))
    if str(n) not in unita:
        raise comune.ErroreMotore(f'Capitolo {n} assente in 04-manoscritto')
    stato = comune.leggi_yaml(os.path.join(cartella, 'stato.yaml'))
    if int(n) > (stato.get('ultimo_capitolo_scritto') or 0):
        raise comune.ErroreMotore(f'Capitolo {n} non ancora accettato: prima «zb esito <libro> {n}».')
    p = os.path.join(cartella, rel(n))
    if os.path.isfile(p):
        print(f'{rel(n)} esiste già: non lo sovrascrivo. Verifica: zb capsula <libro> {n} --verifica')
        return 0
    testo = open(unita[str(n)], encoding='utf-8').read()
    intest = next((r.strip('* ') for r in testo.splitlines()[1:4] if r.startswith('*')), '—')
    l = lingua(libro)
    righe = [comune.MODELLO, f'# Capsula {n} — {libro["titolo"]}', '',
             f'Dati meccanici: {conta.conta_testo(testo)} parole; intestazione: {intest}; codex nominato: '
             + (' '.join(nominati(cartella, testo)) or 'nessuno') + '.', '']
    righe += [f'- {s}:' for s in SEZIONI[l]]
    comune.scrivi(cartella, rel(n), '\n'.join(righe) + '\n')
    print(f'Preparata {rel(n)}: l\'agente «capsula» compila le sezioni (circa 180 parole), poi '
          f'«zb capsula <libro> {n} --verifica».')
    return 0


def sezioni_di(testo, l):
    """{sezione: contenuto} della capsula."""
    out, cur = {}, None
    nomi = {s.lower(): s for s in SEZIONI[l]}
    for r in testo.splitlines():
        m = re.match(r'^-\s*([^:]+):\s*(.*)$', r.strip())
        if m and m.group(1).strip().lower() in nomi:
            cur = nomi[m.group(1).strip().lower()]
            out[cur] = m.group(2).strip()
        elif cur and r.strip() and not r.startswith('#'):
            out[cur] = (out[cur] + ' ' + r.strip()).strip()
    return out


def problemi_capsula(cartella, libro, n):
    p = os.path.join(cartella, rel(n))
    if not os.path.isfile(p):
        return [f'{rel(n)}: manca (zb capsula <libro> {n})']
    t = open(p, encoding='utf-8').read()
    out = []
    if comune.MODELLO in t:
        out.append(f'{rel(n)}: ancora modello (togli {comune.MODELLO} dopo averla compilata)')
    l = lingua(libro)
    sez = sezioni_di(t, l)
    vuote = [s for s in SEZIONI[l] if not sez.get(s)]
    if vuote:
        out.append(f'{rel(n)}: sezioni vuote: {", ".join(vuote)}')
    parole = sum(conta.conta_testo(v) for v in sez.values())
    if not MINIMO <= parole <= MASSIMO:
        out.append(f'{rel(n)}: {parole} parole nelle sezioni (atteso {MINIMO}-{MASSIMO}, circa 180)')
    return out


def mancanti(cartella, libro, stato, fino_a=None):
    """Capitoli numerati già scritti (fino a ultimo_capitolo_scritto, o fino_a escluso) senza capsula valida."""
    ultimo = (fino_a - 1) if fino_a else (stato.get('ultimo_capitolo_scritto') or 0)
    scritti = [int(u) for u, _ in comune.unita(cartella, libro) if u.isdigit() and int(u) <= ultimo]
    return [n for n in scritti if problemi_capsula(cartella, libro, n)]


def regola(libro):
    """Campo «capsule» di libro.yaml: obbligatorie (zb avvio si ferma) | avviso (predefinito). Da motore."""
    return libro.get('capsule') or 'avviso'


def controlla(cartella, libro, stato, fino_a=None, contesto='avvio'):
    """Messaggio sulle capsule mancanti o incomplete; ErroreMotore con «capsule: obbligatorie». None se tutto c'è."""
    m = mancanti(cartella, libro, stato, fino_a)
    if not m:
        return None
    msg = (f'capsule di continuità mancanti o incomplete: capitoli {", ".join(map(str, m))} '
           '(zb capsula <libro> N e l\'agente capsula; zb esito non va avanti senza)')
    if regola(libro) == 'obbligatorie':
        raise comune.ErroreMotore(f'{contesto}: {msg}')
    return f'AVVISO: {msg}'


def registro(cartella, libro):
    """Riscrive 07-capsule/registro.md; restituisce (aperte, errori)."""
    l = lingua(libro)
    numeri = sorted(int(f[:2]) for f in os.listdir(os.path.join(cartella, CARTELLA))
                    if re.fullmatch(r'\d{2}\.md', f)) if os.path.isdir(os.path.join(cartella, CARTELLA)) else []
    aperte, chiuse, errori = {}, {}, []
    for n in numeri:
        sez = sezioni_di(open(os.path.join(cartella, rel(n)), encoding='utf-8').read(), l)
        for i in PROM.findall(sez.get(SEZIONI[l][3], '')):
            aperte.setdefault(i, n)
        for i in PROM.findall(sez.get(SEZIONI[l][4], '')):
            if i not in aperte:
                errori.append(f'@prom:{i} chiusa nel capitolo {n} ma mai aperta prima')
            chiuse.setdefault(i, n)
    righe = [f'# Registro delle promesse — {libro["titolo"]}', '',
             'Generato da «zb capsula --verifica» dalle capsule: non si scrive a mano.', '',
             '| Promessa | Aperta nel cap. | Chiusa nel cap. | Stato |', '|---|---|---|---|']
    for i in sorted(set(aperte) | set(chiuse), key=lambda x: aperte.get(x, 999)):
        righe.append(f'| @prom:{i} | {aperte.get(i, "—")} | {chiuse.get(i, "—")} | '
                     f'{"chiusa" if i in chiuse else "aperta"} |')
    comune.scrivi(cartella, f'{CARTELLA}/registro.md', '\n'.join(righe) + '\n')
    return [i for i in aperte if i not in chiuse], errori


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2 or not args[1].isdigit():
        raise comune.ErroreMotore('Uso: capsula.py <libro> <N> [--verifica]')
    cartella, libro, _ = comune.carica_libro(args[0])
    n = int(args[1])
    if '--verifica' not in argv:
        return prepara(cartella, libro, n)
    p = problemi_capsula(cartella, libro, n)
    aperte, errori = registro(cartella, libro)
    for x in p + errori:
        print(f'KO {x}')
    print(f'Capsula {n}: ' + ('OK' if not p + errori else f'{len(p + errori)} problemi')
          + f'; promesse aperte: {", ".join("@prom:" + a for a in aperte) or "nessuna"} (07-capsule/registro.md).')
    return 1 if p + errori else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

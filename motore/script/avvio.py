"""Avvio obbligatorio prima di lavorare su un libro (proposta B.4, C.4, C.5).

Uso: python3 -B avvio.py <libro>        (oppure ZB_LIBRO=<libro>)
Si ferma (codice 2) e non scrive nulla da nessuna parte se:
- il percorso non contiene un libro (se c'è un briefing, elenca cosa manca);
- la cartella del libro non è scrivibile o «git push --dry-run» fallisce (errore esatto);
- il ramo non è quello della sessione (ZB_RAMO, se indicato);
- ci sono modifiche non salvate nel libro, o il ramo è avanti o indietro rispetto a origin;
- stato.yaml manca o non è valido, oppure push_in_sospeso è vero;
- in fase «documenti»: briefing incompleto;
- un documento approvato è cambiato fuori procedura (sha256 diverso).
Se tutto va bene stampa la riga «Letto: …» (file, righe, sha256, ultimo commit; libro e motore)
e scrive solo il marker <libro>/.zb/letto-<session_id>.
"""
import datetime
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import fase  # noqa: E402
import nuovo  # noqa: E402

DA_LEGGERE = {
    'documenti': ['00-progetto/briefing.md', '02-bibbia/bibbia.md', 'cronologia.yaml',
                  '03-architettura/scaletta.md', '03-architettura/piano-parole.md'],
    'pagina_campione': ['02-bibbia/bibbia.md', '05-revisioni/pagina-campione.md'],
    'stesura': ['03-architettura/scaletta.md', '03-architettura/piano-parole.md', 'cronologia.yaml',
                '02-bibbia/bibbia.md'],
    'chiusura': ['03-architettura/scaletta.md', 'cronologia.yaml'],
    'chiuso': [],
}


def ferma(msg):
    raise comune.ErroreMotore(msg)


def briefing_senza_libro(percorso):
    """Se il percorso non ha libro.yaml ma ha un briefing, elenca cosa manca."""
    p = os.path.realpath(percorso)
    candidati = [p] if os.path.isfile(p) else [os.path.join(p, 'briefing.md'), os.path.join(p, '00-progetto', 'briefing.md')]
    for c in candidati:
        if os.path.isfile(c) and c.endswith('.md'):
            manca = nuovo.mancanze(nuovo.leggi_briefing(c), nuovo.cartella_dal_briefing(c))
            if manca:
                ferma(f'Nessun libro.yaml: c\'è solo il briefing {c}, incompleto. Mancano:\n- ' + '\n- '.join(manca))
            ferma(f'Nessun libro.yaml: il briefing {c} è completo. Per creare il libro: zb nuovo {c}')
    return None


def riga_file(cartella, rel, etichetta=None):
    p = rel if os.path.isabs(rel) else os.path.join(cartella, rel)
    testo = open(p, encoding='utf-8').read()
    commit = comune.ultimo_commit(os.path.dirname(p), p) or 'mai salvato'
    return (f'{etichetta or rel} ({len(testo.splitlines())} righe, sha256 {comune.sha256_file(p)[:12]}, '
            f'commit {commit})'), comune.sha256_file(p)


def controlla(percorso):
    """Tutti i controlli, senza scrivere nulla. Restituisce i dati per il marker."""
    print(f'Percorso indicato: {percorso}')
    try:
        cartella = comune.trova_libro(percorso)
    except comune.ErroreMotore:
        briefing_senza_libro(percorso)
        raise
    print(f'Libro: {cartella}')
    cartella, libro, profilo = comune.carica_libro(cartella)

    # 1. scrivibilità, prima di qualunque scrittura (B.4)
    zb = os.path.join(cartella, '.zb')
    if not os.access(cartella, os.W_OK) or (os.path.exists(zb) and not os.access(zb, os.W_OK)):
        ferma(f'La sessione non può scrivere nella cartella del libro ({cartella}). Non scrivo nulla.')
    if comune.radice_git(cartella) == '/':
        ferma(f'{cartella} non è in un repository git: non posso salvare. Non scrivo nulla.')
    codice, out, err = comune.git(cartella, 'push', '--dry-run')
    if codice != 0:
        ferma(f'git push --dry-run non riuscito nel repository del libro:\n{err or out}\nNon scrivo nulla.')

    # 2. ramo e allineamento
    ramo = comune.ramo(cartella)
    atteso = os.environ.get('ZB_RAMO')
    if atteso and ramo != atteso:
        ferma(f'Checkout del libro sul ramo «{ramo}», ma la sessione lavora su «{atteso}».')
    codice, out, _ = comune.git(cartella, 'status', '--porcelain', '--', '.')
    if out:
        ferma('Modifiche non salvate nel libro (tieni o scarta? non scarto nulla da solo):\n' + out)
    codice, conti, err = comune.git(cartella, 'rev-list', '--left-right', '--count', 'HEAD...@{u}')
    if codice != 0:
        ferma(f'Nessun ramo remoto collegato a «{ramo}»: {err}')
    avanti, indietro = (int(x) for x in conti.split())
    if indietro:
        ferma(f'Il ramo «{ramo}» è indietro di {indietro} commit rispetto a origin: prima git pull.')
    if avanti:
        ferma(f'Il ramo «{ramo}» ha {avanti} commit non pushati: prima git push (C.5).')

    # 3. stato, briefing, documenti approvati
    stato = fase.carica_stato(cartella)
    if stato['push_in_sospeso']:
        ferma('stato.yaml: push_in_sospeso è vero. Prima il push.')
    if stato['fase'] == 'documenti':
        manca = nuovo.mancanze(nuovo.leggi_briefing(os.path.join(cartella, '00-progetto', 'briefing.md')), cartella)
        if manca:
            ferma('Briefing incompleto. Mancano:\n- ' + '\n- '.join(manca))
    cambiati = [rel for rel, v in stato['documenti_approvati'].items()
                if not os.path.isfile(os.path.join(cartella, rel))
                or comune.sha256_file(os.path.join(cartella, rel)) != v['sha256']]
    if cambiati:
        ferma('Documenti approvati cambiati fuori procedura (sha256 diverso da quello registrato):\n- '
              + '\n- '.join(cambiati) + '\nSe la modifica è autorizzata dall\'autore: salvala con un commit, poi '
              '«zb riapprova <libro> <documento> <motivo>».')

    # 4. file da leggere
    letti, sha = [], {}
    elenco = ['libro.yaml', 'stato.yaml', 'LEGGIMI.md', '03-architettura/manuale-di-stile.md']
    elenco += DA_LEGGERE[stato['fase']]
    if libro.get('modalita') == 'riscrittura':
        elenco.append(libro['testo_precedente'])
    if stato['fase'] == 'stesura' and stato['ultimo_capitolo_scritto']:
        u = dict(comune.unita(cartella, libro)).get(str(stato['ultimo_capitolo_scritto']))
        if u:
            elenco.append(os.path.relpath(u, cartella))
    for rel in dict.fromkeys(elenco):
        if os.path.isfile(os.path.join(cartella, rel)):
            r, s = riga_file(cartella, rel)
            letti.append(r)
            sha[rel] = s
    pp = os.path.join(comune.radice_motore(), 'profili', f'{libro["profilo"]}.yaml')
    r, s = riga_file(cartella, pp, f'profilo {libro["profilo"]}')
    letti.append(r)
    sha[f'profilo {libro["profilo"]}'] = s
    libro_commit = comune.git(cartella, 'log', '-1', '--format=%h «%s»')[1]
    motore_commit = comune.git(comune.radice_motore(), 'log', '-1', '--format=%h')[1] or 'fuori da git'
    return cartella, libro, stato, letti, sha, libro_commit, motore_commit, ramo


def main(argv):
    args = comune.argomenti(argv)
    percorso = args[0] if args else os.environ.get('ZB_LIBRO')
    if not percorso:
        raise comune.ErroreMotore('Uso: avvio.py <libro> (oppure ZB_LIBRO=<libro>)')
    cartella, libro, stato, letti, sha, libro_commit, motore_commit, ramo = controlla(percorso)
    print(f'Ramo: {ramo}; allineato a origin: sì')
    print('Letto: ' + ', '.join(letti) + ';')
    print(f'libro @ {libro_commit}; motore @ {motore_commit}; fase {stato["fase"]}, '
          f'gate {stato["gate_in_attesa"] or "nessuno"}.')
    rc = stato.get('revisione_in_corso')
    print(f'Passo: {stato["passo"] or "—"}; capitoli scritti fino a {stato["ultimo_capitolo_scritto"] or "—"}, '
          f'approvati fino a {stato["ultimo_capitolo_approvato"] or "—"}; '
          f'parole {stato["parole"]["scritte"]}/{stato["parole"]["obiettivo"]}.')
    if rc:
        print(f'Revisione in corso: gate {rc["gate"]}, blocco {rc["blocco"]} di {rc["blocchi_totali"]}.')
    for c in stato['correzioni_aperte']:
        print(f'Correzione aperta [{c["gate"]}]: {c["testo"]}')
    for a in stato['avvisi_aperti']:
        print(f'Avviso aperto: {a}')
    print(fase.prossimo(stato))
    # unica scrittura: il marker di sessione dentro il libro
    sid, fonte = comune.sessione_corrente()
    d = comune.prepara_zb(cartella)
    marker = os.path.join(d, f'letto-{sid}')
    corpo = [f'data: {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}',
             f'libro_commit: {libro_commit}', f'motore_commit: {motore_commit}']
    corpo += [f'{k}: {v}' for k, v in sha.items()]
    comune.scrivi(cartella, marker, '\n'.join(corpo) + '\n')
    print(f'Sessione: {sid} ({fonte}); marker {os.path.relpath(marker, cartella)}.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

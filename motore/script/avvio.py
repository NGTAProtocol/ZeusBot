"""Avvio obbligatorio prima di lavorare su un libro (proposta B.4, C.4, C.5).

Uso: python3 -B avvio.py <libro> [--ruolo <ruolo>]        (oppure ZB_LIBRO=<libro>)
Si ferma (codice 2) e non scrive nulla da nessuna parte se:
- il percorso non contiene un libro (se c'è un briefing, elenca cosa manca);
- la cartella del libro non è scrivibile o «git push --dry-run» fallisce (errore esatto);
- il ramo non è quello della sessione (ZB_RAMO, se indicato);
- ci sono modifiche non salvate nel libro, o il ramo è avanti o indietro rispetto a origin;
- stato.yaml manca o non è valido, oppure push_in_sospeso è vero;
- in fase «documenti»: briefing incompleto (non per un libro in riscrittura senza briefing nel formato
  del motore, cioè senza la riga «Titolo di lavoro:»: è un libro adottato con i suoi documenti);
- un documento approvato è cambiato fuori procedura (sha256 diverso).
- in fase «struttura» o «documenti»: briefing incompleto;
- la sessione ha già un altro ruolo (un ruolo per sessione), o un ruolo di revisione è chiesto da una
  sessione che ha scritto il testo da revisionare (con separazione_ruoli: blocco in dati/hook.yaml);
- un file della sessione o un commit del ramo è fuori da libri/<slug>/ (cartella_unica.py).
Ruolo: --ruolo <ruolo> (ruoli.py); senza, quello della fase. Registrato in <libro>/.zb/ruoli.yaml.
Se tutto va bene stampa la riga «Letto: …» (file, righe, sha256, ultimo commit; libro e motore)
e scrive solo in <libro>/.zb/ (marker letto-<session_id>, ruoli.yaml).
Con il blocco «voce» in libro.yaml la riga «Letto» include anche il briefing e la scheda della voce
(banca-voci da ZB_BANCA_VOCI); se la voce non verifica (voce.py) stampa un AVVISO, senza fermarsi.
"""
import datetime
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import fase  # noqa: E402
import nuovo  # noqa: E402
import ruoli  # noqa: E402
import voce  # noqa: E402

STRUTTURA = ['03-struttura/' + f for f in nuovo.FILE_STRUTTURA]
DA_LEGGERE = {
    'struttura': ['00-progetto/briefing.md'] + STRUTTURA,
    'revisione_manoscritto': ['03-struttura/05-scaletta.md', '03-struttura/06-sottotrame-temi.md', 'cronologia.yaml'],
    'line': ['02-bibbia/bibbia.md'],
    'copy': ['nomi_propri.txt', 'cronologia.yaml'],
    'bozze': [],
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

    # 2b. cartella unica: niente fuori da libri/<slug>/ (file modificati e commit del libro, nome del libro)
    import cartella_unica
    rad, slug = cartella_unica.per_libro(cartella)
    if slug:
        err = cartella_unica.controlla(rad, slug, libro.get('titolo'))
        if err:
            ferma(f'CARTELLA UNICA: tutto il libro vive solo in libri/{slug}/. Problemi:\n- ' + '\n- '.join(err[:30]))
    elif os.environ.get('ZB_PROVE') != '1':
        ferma(f'{cartella} non è libri/<slug>/ del repository: il libro vive solo lì (cartella unica).')

    # 3. stato, briefing, documenti approvati
    stato = fase.carica_stato(cartella)
    if stato['push_in_sospeso']:
        ferma('stato.yaml: push_in_sospeso è vero. Prima il push.')
    pb = os.path.join(cartella, '00-progetto', 'briefing.md')
    briefing_motore = os.path.isfile(pb) and re.search(r'(?m)^Titolo di lavoro:', open(pb, encoding='utf-8').read())
    if stato['fase'] in ('struttura', 'documenti') and (libro.get('modalita') != 'riscrittura' or briefing_motore):
        manca = nuovo.mancanze(nuovo.leggi_briefing(os.path.join(cartella, '00-progetto', 'briefing.md')), cartella)
        if manca:
            ferma('Briefing incompleto. Mancano:\n- ' + '\n- '.join(manca))
    cambiati = [rel for rel, v in stato['documenti_approvati'].items()
                if not comune.documento_invariato(os.path.join(cartella, rel), v['sha256'], v.get('commit'))]
    if cambiati:
        ferma('Documenti approvati cambiati fuori procedura (sha256 diverso da quello registrato):\n- '
              + '\n- '.join(cambiati) + '\nSe la modifica è autorizzata dall\'autore: salvala con un commit, poi '
              '«zb riapprova <libro> <documento> <motivo>».')

    # 4. file da leggere
    letti, sha = [], {}
    elenco = ['libro.yaml', 'stato.yaml', 'LEGGIMI.md', '03-architettura/manuale-di-stile.md']
    elenco += DA_LEGGERE[stato['fase']]
    if libro.get('voce'):
        elenco.append('00-progetto/briefing.md')
    if libro.get('modalita') == 'riscrittura':
        elenco.append(libro['testo_precedente'])
    import capsule
    if stato['fase'] in capsule.FASI_CON_CAPSULE:
        avviso_capsule = capsule.controlla(cartella, libro, stato)       # FERMO con capsule: obbligatorie
        if avviso_capsule:
            print(avviso_capsule)
    if stato['fase'] == 'stesura' and stato['ultimo_capitolo_scritto']:
        # si leggono le capsule dei capitoli già scritti, non i capitoli interi (risparmio-token.md);
        # il capitolo precedente intero solo se la sua capsula manca
        caps = [capsule.percorso(n) for n in range(1, stato['ultimo_capitolo_scritto'] + 1)
                if os.path.isfile(os.path.join(cartella, capsule.percorso(n)))]
        elenco += caps
        if capsule.percorso(stato['ultimo_capitolo_scritto']) not in caps:
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
    avvisi = []
    if libro.get('voce'):
        avvisi = scheda_voce(libro['voce'], letti, sha)
    libro_commit = comune.git(cartella, 'log', '-1', '--format=%h «%s»')[1]
    motore_commit = comune.git(comune.radice_motore(), 'log', '-1', '--format=%h')[1] or 'fuori da git'
    return cartella, libro, stato, letti, sha, libro_commit, motore_commit, ramo, avvisi


def scheda_voce(v, letti, sha):
    """Aggiunge la scheda della voce a «Letto»; restituisce gli avvisi (mai un fermo)."""
    slug = v['slug']
    try:
        b = voce.banca()
        problemi = voce.problemi(b, slug)
    except comune.ErroreMotore as e:
        return [f'voce «{slug}» non verificata: {e}'.replace('\n', ' ')]
    p = voce.scheda(b, slug)
    if os.path.isfile(p):
        r, s = riga_file(os.path.dirname(p), p, f'scheda della voce {slug}')
        letti.append(r)
        sha[f'voce {slug}'] = s
    return [f'voce «{slug}»: {x}' for x in problemi]


def main(argv):
    args = comune.argomenti(argv)
    percorso = args[0] if args else os.environ.get('ZB_LIBRO')
    if not percorso:
        raise comune.ErroreMotore('Uso: avvio.py <libro> (oppure ZB_LIBRO=<libro>)')
    cartella, libro, stato, letti, sha, libro_commit, motore_commit, ramo, avvisi_voce = controlla(percorso)
    sid, fonte = comune.sessione_corrente()
    ruolo = argv[argv.index('--ruolo') + 1] if '--ruolo' in argv and argv.index('--ruolo') + 1 < len(argv) \
        else ruoli.DA_FASE.get(stato['fase'], 'motore')
    if ruolo not in ruoli.RUOLI:
        raise comune.ErroreMotore(f'Ruolo «{ruolo}» sconosciuto. Ruoli: {", ".join(ruoli.RUOLI)}')
    precedente = (ruoli.leggi_ruoli(cartella).get(sid) or {}).get('ruolo')
    if precedente and precedente != ruolo and sid != 'locale':
        raise comune.ErroreMotore(f'Questa sessione ha già il ruolo «{precedente}»: un ruolo per sessione. Per fare '
                                  f'«{ruolo}»: salva, apri una sessione nuova, zb avvio, riga «Letto».')
    ruoli.controlla_avvio(cartella, sid, ruolo)
    f_ruolo = ruoli.RUOLI[ruolo]['file']
    if f_ruolo:
        p_ruolo = os.path.join(comune.radice_motore(), 'editoriale', 'ruoli', f_ruolo)
        r, s = riga_file(os.path.dirname(p_ruolo), p_ruolo, f'ruolo {ruolo}')
        letti.append(r)
        sha[f'ruolo {ruolo}'] = s
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
    if libro.get('voce'):
        print(f'Voce: {libro["voce"]["slug"]}, ambientazione {libro["voce"].get("ambientazione") or "altro"}. '
              'Prima di ogni capitolo: rileggi la scheda della voce e il briefing.')
    for a in avvisi_voce:
        print(f'AVVISO: {a}')
    for n_int, d in comune.interludi_in_anticipo(cartella, libro):
        print(f'AVVISO: {n_int} in anticipo (va dopo il capitolo {d}, non ancora scritto).')
    print(fase.prossimo(stato))
    # uniche scritture: ruolo della sessione e marker, dentro <libro>/.zb/
    ruoli.registra_ruolo(cartella, sid, ruolo)
    print(f'Ruolo della sessione: {ruolo}' + ('' if '--ruolo' in argv else ' (dalla fase; un altro: --ruolo <ruolo>)')
          + '. Un ruolo per sessione.')
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

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
- un documento approvato è cambiato fuori procedura (sha256 diverso);
- la sessione ha già un altro ruolo (un ruolo per sessione), o un ruolo di revisione è chiesto da una sessione che
  ha scritto il testo da revisionare (con «separazione_ruoli: blocco» in dati/hook.yaml; ruolo.py, da motore).
Ruolo: --ruolo <ruolo>; senza, quello della fase (ruolo.DA_FASE). Registrato in <libro>/.zb/ruoli.yaml; il file del
ruolo (motore/editoriale/) entra nella riga «Letto».
Se tutto va bene stampa la riga «Letto: …» (file, righe, sha256, ultimo commit; libro e motore)
e scrive solo il marker <libro>/.zb/letto-<session_id>.
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
import voce  # noqa: E402

DA_LEGGERE = {
    'documenti': ['00-progetto/briefing.md', '02-bibbia/bibbia.md', 'cronologia.yaml',
                  '03-architettura/scaletta.md', '03-architettura/piano-parole.md'],
    'pagina_campione': ['02-bibbia/bibbia.md', '05-revisioni/pagina-campione.md'],
    'stesura': ['03-architettura/scaletta.md', '03-architettura/piano-parole.md', 'cronologia.yaml',
                '02-bibbia/bibbia.md'],
    'chiusura': ['03-architettura/scaletta.md', 'cronologia.yaml'],
    'chiuso': [],
}
# percorso editoriale: nelle sessioni nuove si legge lo stato compatto e il necessario della fase
DA_LEGGERE_EDITORIALE = {
    'struttura': ['00-progetto/briefing.md'],
    'documenti': ['00-progetto/briefing.md', '03-struttura/01-premessa.md', '03-struttura/09-scelte-fisse.md'],
    'pagina_campione': ['03-struttura/09-scelte-fisse.md', '05-revisioni/pagina-campione.md'],
    'stesura': ['03-struttura/09-scelte-fisse.md', '07-capsule/registro.md'],
    'struttura_manoscritto': ['07-capsule/registro.md'], 'line': [], 'copy': [], 'bozze': [],
    'guida': ['00-progetto/guida-traduzione.md', '00-progetto/glossario.yaml'], 'fedelta': [],
    'chiusura': [], 'chiuso': [],
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


def recinto_git(cartella):
    """Cartella unica: nessun file modificato fuori da libri/<slug>/ (modifiche non salvate in tutto il repository,
    anche scritte da Bash o da uno script) e nessun file fuori dal libro cambiato dai commit del ramo rispetto a
    origin/motore (esclusi i file che il motore stesso installa). Solo per un libro in libri/<slug>/.
    Poi cartella_unica.controlla: commit misti (libro e altro nello stesso commit, merge del motore esclusi) e
    titolo del libro fuori da libri/ fermano l'avvio."""
    import hook_recinto
    import precommit
    rad = comune.radice_git(cartella)
    if os.path.dirname(cartella) != os.path.join(rad, 'libri'):
        return
    slug = os.path.basename(cartella)
    attivo = hook_recinto.slug_attivo(rad)
    if attivo and attivo != slug:
        ferma(f'Libro attivo: libri/{attivo}/, non libri/{slug}/. Un solo libro per sessione: per cambiare '
              f'«zb lavoro libro {slug}» e un nuovo zb avvio.')
    if hook_recinto.lavoro(rad) == 'motore':
        ferma('Lavoro sul motore in corso: per lavorare sul libro «zb lavoro libro ' + slug + '».')
    fuori = [p for p in precommit.modificati(rad)
             if not p.startswith(f'libri/{slug}/') and p not in precommit.EXTRA_LIBRO]
    if fuori:
        ferma('Modifiche fuori dalla cartella del libro (il libro non scrive altrove):\n- ' + '\n- '.join(fuori[:20]))
    import cartella_unica           # da motore: commit misti e titolo del libro fuori dal libro
    titolo = comune.leggi_yaml(os.path.join(cartella, 'libro.yaml')).get('titolo')
    err = cartella_unica.controlla(rad, slug, titolo)
    if err:
        ferma(f'CARTELLA UNICA: {len(err)} problemi (tutto il libro vive solo in libri/{slug}/):\n- '
              + '\n- '.join(err[:20]) + '\nUn commit misto già fatto si dichiara, con il motivo, in '
              'motore/dati/cartella-unica.yaml (commit_dichiarati): la storia non si riscrive.')
    if comune.git(rad, 'rev-parse', '-q', '--verify', 'origin/motore')[0] == 0:
        diff = comune.git(rad, 'diff', '--name-only', 'origin/motore...HEAD')[1].splitlines()
        altri = [p for p in diff if not p.startswith('libri/') and not any(
            p == e or (e.endswith('/') and p.startswith(e)) for e in precommit.EXTRA_LIBRO)]
        libri_altri = sorted({p.split('/')[1] for p in diff if p.startswith('libri/') and p.count('/') > 1
                              and p.split('/')[1] != slug})
        if altri:
            print('AVVISO: il ramo cambia file fuori dai libri rispetto a origin/motore: ' + ', '.join(altri[:8])
                  + ' (se non è un merge del motore dichiarato, va riportato all\'autore).')
        if libri_altri:
            print(f'AVVISO: il ramo contiene altri libri ({", ".join(libri_altri)}): questo libro non li legge.')


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
    recinto_git(cartella)
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
    pb = os.path.join(cartella, '00-progetto', 'briefing.md')
    briefing_motore = os.path.isfile(pb) and re.search(r'(?m)^Titolo di lavoro:', open(pb, encoding='utf-8').read())
    if stato['fase'] == 'documenti' and (libro.get('modalita') != 'riscrittura' or briefing_motore):
        manca = nuovo.mancanze(nuovo.leggi_briefing(os.path.join(cartella, '00-progetto', 'briefing.md')), cartella)
        if manca:
            ferma('Briefing incompleto. Mancano:\n- ' + '\n- '.join(manca))
    cambiati = [rel for rel, v in stato['documenti_approvati'].items()
                if not comune.documento_invariato(os.path.join(cartella, rel), v['sha256'], v.get('commit'))]
    import percorso
    in_revisione = []
    if percorso.attivo(libro) and stato['fase'] in percorso.REVISIONI:
        in_revisione = [rel for rel in cambiati if percorso.testo_in_revisione(rel)]
        cambiati = [rel for rel in cambiati if rel not in in_revisione]
    if in_revisione:
        print(f'AVVISO: {len(in_revisione)} capitoli cambiati nella fase «{stato["fase"]}» (li registra «zb pronto» '
              'a fine fase).')
    if cambiati:
        ferma('Documenti approvati cambiati fuori procedura (sha256 diverso da quello registrato):\n- '
              + '\n- '.join(cambiati) + '\nSe la modifica è autorizzata dall\'autore: salvala con un commit, poi '
              '«zb riapprova <libro> <documento> <motivo>».')

    # 4. file da leggere
    letti, sha = [], {}
    avvisi_capsule = []
    elenco = ['libro.yaml', 'stato.yaml', 'LEGGIMI.md', '03-architettura/manuale-di-stile.md']
    if comune.editoriale(libro):
        elenco += ['stato-compatto.md'] + DA_LEGGERE_EDITORIALE[stato['fase']]
    else:
        elenco += DA_LEGGERE[stato['fase']]
    if libro.get('voce'):
        elenco.append('00-progetto/briefing.md')
    if libro.get('modalita') == 'riscrittura':
        elenco.append(libro['testo_precedente'])
    if comune.editoriale(libro) and stato['fase'] == 'stesura':
        import capsula      # «capsule: obbligatorie» in libro.yaml: fermo; altrimenti avviso (da motore)
        try:
            msg = capsula.controlla(cartella, libro, stato)
        except comune.ErroreMotore as e:
            ferma(str(e))
        if msg:
            avvisi_capsule.append(msg[len('AVVISO: '):])
    if stato['fase'] == 'stesura' and stato['ultimo_capitolo_scritto'] and not comune.editoriale(libro):
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
    avvisi = list(avvisi_capsule)
    pc = os.path.join(cartella, 'passaggio-di-consegne.md')
    da_ultimo = comune.git(cartella, 'rev-list', '--count', f'{comune.ultimo_commit(cartella, pc) or "HEAD"}..HEAD', '--', '.')[1]
    if comune.editoriale(libro) and (not os.path.isfile(pc) or (da_ultimo.isdigit() and int(da_ultimo) > 10)):
        avvisi.append('report di sessione (passaggio-di-consegne.md) assente o non aggiornato da più di 10 salvataggi '
                      '(regola: ogni 5 scambi o a «passaggio»; /handover)')
    if libro.get('voce'):
        avvisi += scheda_voce(libro['voce'], letti, sha)
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


def avvio_motore():
    """«zb avvio» senza libro: lavoro sul motore. Controlli e riga «Letto»; non scrive nulla."""
    import hook_recinto
    import precommit
    rad = comune.radice_git(comune.radice_motore())
    if hook_recinto.lavoro(rad) != 'motore':
        ferma('Nessun libro indicato e lavoro sul motore non dichiarato. Per un libro: zb avvio libri/<slug>. '
              'Per il motore, solo se l\'autore ha scritto «lavoro sul motore»: zb lavoro motore.')
    ramo = comune.ramo(rad)
    codice, out, err = comune.git(rad, 'status', '--porcelain')
    problemi = []
    if os.path.isdir(os.path.join(rad, 'libri')):
        problemi.append('c\'è una cartella libri/: il ramo del motore non contiene libri')
    for rel in ('.claude/agents', '.claude/commands', '.claude/settings.json'):
        if os.path.exists(os.path.join(rad, rel)):
            problemi.append(f'{rel}: agenti, comandi e hook restano spenti sul ramo del motore')
    c2, conti, _ = comune.git(rad, 'rev-list', '--left-right', '--count', 'HEAD...@{u}')
    allineato = 'sì' if c2 == 0 and conti.split() == ['0', '0'] else (f'no ({conti})' if c2 == 0 else 'nessun remoto')
    letti = []
    for rel in ('CLAUDE.md', 'motore/PROCEDURA.md', 'motore/passaggio-di-consegne.md', 'motore/editoriale/LEGGIMI.md'):
        p = os.path.join(rad, rel)
        if os.path.isfile(p):
            letti.append(riga_file(rad, p, rel)[0])
    print(f'Lavoro sul motore. Ramo: {ramo}; allineato a origin: {allineato}; modifiche non salvate: '
          f'{len(out.splitlines()) if out else 0}; controllo pre-commit: {precommit.stato(rad)}.')
    print('Letto: ' + ', '.join(letti) + ';')
    print(f'motore @ {comune.git(rad, "log", "-1", "--format=%h «%s»")[1]}.')
    for x in problemi:
        print(f'FERMO: {x}')
    return 2 if problemi else 0


def main(argv):
    args = comune.argomenti(argv)
    percorso = args[0] if args else os.environ.get('ZB_LIBRO')
    if not percorso:
        return avvio_motore()
    cartella, libro, stato, letti, sha, libro_commit, motore_commit, ramo, avvisi_voce = controlla(percorso)
    # un ruolo per sessione (da motore): controlli prima di qualunque scrittura
    import ruolo as R
    sid, fonte = comune.sessione_corrente()
    ruolo = argv[argv.index('--ruolo') + 1] if '--ruolo' in argv and argv.index('--ruolo') + 1 < len(argv) \
        else R.DA_FASE.get(stato['fase'], 'motore')
    if ruolo not in R.RUOLI:
        ferma(f'Ruolo «{ruolo}» sconosciuto. Ruoli: {", ".join(R.RUOLI)}')
    precedente = (R.leggi_ruoli(cartella).get(sid) or {}).get('ruolo')
    if precedente and precedente != ruolo and sid != 'locale':
        ferma(f'Questa sessione ha già il ruolo «{precedente}»: un ruolo per sessione. Per fare «{ruolo}»: salva, '
              'apri una sessione nuova, zb avvio, riga «Letto».')
    R.controlla_avvio(cartella, sid, ruolo)
    if ruolo == 'regia':
        # chi orchestra legge solo lo stato: manuale, briefing, voce e struttura li leggono gli agenti (meno token)
        tieni = ('libro.yaml', 'stato.yaml', 'stato-compatto.md', 'passaggio-di-consegne.md')
        letti = [r for r in letti if r.split(' (')[0] in tieni]
        sha = {k: v for k, v in sha.items() if k in tieni}
    if R.RUOLI[ruolo]['file']:
        p_ruolo = os.path.join(comune.radice_motore(), 'editoriale', R.RUOLI[ruolo]['file'])
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
    R.registra_ruolo(cartella, sid, ruolo)
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

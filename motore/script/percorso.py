"""Percorso da casa editrice (libri con «percorso: editoriale» in libro.yaml). Lo usa fase.py.

Fasi: struttura → documenti → pagina_campione → stesura → struttura_manoscritto → line → copy → bozze →
chiusura → chiuso (motore/editoriale/00-percorso.md). I libri senza il campo restano sul percorso breve.

Fasi di revisione (struttura_manoscritto, line, copy, bozze) in due tempi, in stato.yaml «sottofase»:
- «proposte»: i ruoli scrivono i rapporti; «zb pronto» controlla che ci siano tutti, con la prima riga
  «<!-- zb: ruolo=<ruolo>; su=<impronta> -->» uguale all'impronta attuale del testo rivisto, e che ogni
  rapporto sia stato salvato in un commit che non tocca il testo rivisto (chi scrive non rivede); poi apre il
  gate della fase, che mostra i rapporti;
- «applicazione»: dopo l'«ok» si applicano solo le proposte approvate (modifiche puntuali); «zb esito N»
  rimisura un capitolo; «zb pronto» passa alla fase successiva senza un secondo gate.
Canone: «fatti_bloccati» in stato.yaml; cambia solo con «zb canone <libro> proponi|togli …» e il gate «canone».
Modo automatico (decisione dell'autore del 2026-10-20): la struttura la verifica il motore, sempre, senza fermata
dell'autore (gate «struttura» automatico anche se elencato in libro.yaml): se i controlli passano registra i nove
file, crea bibbia, codex, cronologia e manuale (nuovo.genera_documenti) e passa a «documenti»; se no si ferma e
scrive il motivo. Gli altri gate valgono solo se libro.yaml li elenca (i libri nuovi nascono con gate: [lettura], la pausa di lettura).
"""
import datetime
import os
import re

import comune

FASI = ['struttura', 'documenti', 'pagina_campione', 'guida', 'stesura', 'struttura_manoscritto', 'line', 'copy',
        'bozze', 'fedelta', 'chiusura', 'chiuso']
REVISIONI = ['struttura_manoscritto', 'line', 'copy', 'bozze', 'fedelta']
SUCCESSIVA = {'struttura_manoscritto': 'line', 'line': 'copy', 'copy': 'bozze', 'bozze': 'chiusura'}
# libro di traduzione (modalita: traduzione, 08-traduzione-<lingua>/): guida → stesura → line → copy → fedelta
SUCCESSIVA_TRADUZIONE = {'line': 'copy', 'copy': 'fedelta', 'fedelta': 'chiusura'}
GATE = ['struttura', 'documenti', 'pagina_campione', 'primi_capitoli', 'lotto', 'struttura_manoscritto',
        'line', 'copy', 'bozze', 'canone', 'guida', 'fedelta']
INTESTAZIONE = re.compile(r'^<!--\s*zb:\s*ruolo=([\w\-]+);\s*su=([0-9a-f]{12})\s*-->')
CANONE = '06-diagnostica/canone-proposte.md'
NOTA_DIREZIONE = '06-diagnostica/nota-direzione.md'
# ruolo -> fasi in cui può lavorare (zb ruolo lo controlla: la scrittura non include revisione)
# il diagnosta lavora anche in «stesura», solo sul capitolo singolo (06-diagnostica/audit/NN.md, rapporto_capitolo)
FASI_RUOLO = {'architetto-struttura': ['struttura'], 'diagnosta': ['struttura', 'stesura', 'struttura_manoscritto'],
              'editor-strutturale': ['struttura', 'struttura_manoscritto'], 'direttore-editoriale': ['documenti'],
              'scrittore-voce': ['pagina_campione', 'stesura', 'struttura_manoscritto'],
              'capsula': ['stesura', 'struttura_manoscritto'], 'line-editor': ['line'],
              'correttore-italiano': ['copy'], 'correttore-bozze': ['bozze'],
              'traduttore': ['stesura'], 'revisore-fedelta': ['fedelta']}


def traduzione(libro):
    return (libro or {}).get('modalita') == 'traduzione'


def successiva(libro, fs):
    return (SUCCESSIVA_TRADUZIONE if traduzione(libro) else SUCCESSIVA)[fs]


def attivo(libro):
    return comune.editoriale(libro)


# ---------------------------------------------------------------- testi rivisti e rapporti

def file_struttura():
    return [f'{comune.STRUTTURA}/{f}' for f in comune.FILE_STRUTTURA]


def capitoli(cartella, libro):
    return [(n, os.path.relpath(p, cartella)) for n, p in comune.unita(cartella, libro)]


def nn(n):
    return f'{int(n):02d}' if str(n).isdigit() else str(n).replace(' ', '-')


def rapporti(cartella, libro, fase):
    """[(rapporto, ruolo, [testi rivisti])] attesi in una fase."""
    if fase == 'struttura':
        s = file_struttura()
        return [('06-diagnostica/rapporto-struttura.md', 'diagnosta', s),
                ('06-diagnostica/piano-revisione-struttura.md', 'editor-strutturale', s)]
    tutti = [r for _, r in capitoli(cartella, libro)]
    if fase == 'struttura_manoscritto':
        return [('06-diagnostica/rapporto-manoscritto.md', 'diagnosta', tutti),
                ('06-diagnostica/piano-revisione-manoscritto.md', 'editor-strutturale', tutti)]
    if fase in ('line', 'copy'):
        ruolo = 'line-editor' if fase == 'line' else 'correttore-italiano'
        return [(f'06-diagnostica/{fase}/{nn(n)}.md', ruolo, [r]) for n, r in capitoli(cartella, libro)]
    if fase == 'bozze':
        return [('06-diagnostica/bozze.md', 'correttore-bozze', tutti)]
    if fase == 'fedelta':
        return [('06-diagnostica/fedelta.md', 'revisore-fedelta', tutti)]
    raise comune.ErroreMotore(f'Fase senza rapporti: {fase}')


def rapporto_capitolo(cartella, libro, n):
    """(rapporto, ruolo, [capitolo]) della revisione del capitolo singolo in fase «stesura» (diagnosta)."""
    trovati = dict(capitoli(cartella, libro))
    if str(n) not in trovati:
        raise comune.ErroreMotore(f'Capitolo «{n}» assente in 04-manoscritto')
    return (f'06-diagnostica/audit/{nn(n)}.md', 'diagnosta', [trovati[str(n)]])


def rel_audit(n):
    return f'06-diagnostica/audit/{nn(n)}.md'


def misure_rel(n):
    return f'06-diagnostica/misure/{nn(n)}.md'


def bloccanti_prima_della_revisione(risultati, libro):
    """Esiti che fermano la chiamata al diagnosta: ogni KO e gli avvisi dei divieti della voce (controlli
    «voce:<slug>:…»). Decisione dell'autore del 2026-10-21: frase media e ripetizioni ravvicinate restano avvisi (soglie
    ancora PROPOSTA): con gli altri avvisi passano al diagnosta come righe misurate e non fermano."""
    slug = (libro.get('voce') or {}).get('slug')
    if comune.soglie_informative(libro):      # 2026-10-27: i divieti della voce informano il revisore, non fermano
        return [r for r in risultati if r['esito'] == 'KO']
    return [r for r in risultati if r['esito'] == 'KO' or (
        r['esito'] == 'AVVISO' and slug and r['controllo'].startswith(f'voce:{slug}:'))]


def da_correggere(testo):
    """Voci «- …» della sezione «## Da correggere» di un rapporto del diagnosta («- nessuna» esclusa)."""
    out, dentro_sez = [], False
    for r in testo.splitlines():
        s = r.strip()
        if s.startswith('## '):
            dentro_sez = s[3:].strip().lower() == 'da correggere'
            continue
        if dentro_sez and s.startswith('- ') and s[2:].strip().lower().rstrip('.') != 'nessuna':
            out.append(s[2:].strip())
    return out


def giro_revisione(cartella, libro, n, nuovo=False):
    """(giro, voci) della revisione del capitolo N: un solo giro completo; dopo un «non passa» e la correzione di chi
    scrive, il secondo giro rivede solo le voci di «## Da correggere» del primo (copiato in audit/NN-giro1.md da
    misure_prima_della_revisione). Si ferma: capitolo non corretto dopo un «non passa»; primo rapporto senza
    «## Da correggere»; due giri già fatti (decide l'autore; --nuovo-giro, dopo il suo ok, riparte da un giro completo)."""
    rel, _, testi = rapporto_capitolo(cartella, libro, n)
    p = os.path.join(cartella, rel)
    g1 = os.path.join(cartella, f'06-diagnostica/audit/{nn(n)}-giro1.md')
    testo = open(p, encoding='utf-8').read() if os.path.isfile(p) else ''
    righe = [r.strip() for r in testo.splitlines()]
    if next((r for r in reversed(righe) if r), '').lower() != 'non passa':
        if os.path.isfile(g1):
            os.remove(g1)   # primo giro di un ciclo chiuso prima: si riparte da un giro completo (la storia resta in git)
        return 1, []
    m = INTESTAZIONE.match(righe[0] if righe else '')
    if m and m.group(2) == impronta(cartella, testi):
        raise comune.ErroreMotore(f'{rel}: «non passa» sul testo attuale del capitolo {n}. Prima la correzione mirata di '
                                  'chi scrive, poi la nuova revisione.')
    if os.path.isfile(g1):
        if not nuovo:
            raise comune.ErroreMotore(f'Capitolo {n}: due giri di revisione fatti, il secondo chiude con «non passa». '
                                      'Decide l\'autore; un nuovo giro completo solo dopo il suo ok: '
                                      f'«zb ruolo <libro> diagnosta {n} --nuovo-giro».')
        os.remove(g1)       # la storia resta in git
        return 1, []
    voci = da_correggere(testo)
    if not voci:
        raise comune.ErroreMotore(f'{rel}: «non passa» senza la sezione «## Da correggere» (una riga per frase: riga, '
                                  'frase, motivo). Il secondo giro rivede solo quelle frasi.')
    return 2, voci


def letture_diagnosta(cartella, libro, n, rel_cap):
    """Righe «File da leggere» e «Canone» del diagnosta per il capitolo singolo: solo ciò che serve alla checklist
    (capitolo, misure, frasi finali, voce sezioni 2, 3 e 6, codex filtrato per i tag della scheda, capsula del
    capitolo precedente; il canone è scritto qui). Non servono: la preparazione dello scrittore, il manuale di stile,
    le scelte fisse, le note della pausa di lettura, le capsule più vecchie."""
    import capsula
    import codex
    import struttura
    n = int(n)
    leggere = [rel_cap, misure_rel(n)]     # 2026-10-27: niente più tabella delle frasi finali (revisione con voti)
    sk = struttura.schede(cartella).get(str(n)) or {}
    leggere += codex.filtra(cartella, struttura.tag_di(sk))[0]
    if n > 1 and os.path.isfile(os.path.join(cartella, capsula.rel(n - 1))):
        leggere.append(capsula.rel(n - 1))
    out = ['## File da leggere (solo questi)', ''] + [f'- {r}' for r in leggere]
    slug = (libro.get('voce') or {}).get('slug')
    if slug:
        out.append(f'- scheda della voce «{slug}» (banca-voci, sola lettura): sezioni 2, 3 e 6')
    stato = comune.leggi_yaml(os.path.join(cartella, 'stato.yaml')) or {}
    out += ['', '## Canone (fatti bloccati)', ''] + ([f'- {x}' for x in stato.get('fatti_bloccati') or []] or ['- nessuno'])
    return out


def misure_prima_della_revisione(cartella, libro, profilo, n, giro=(1, [])):
    """Misure del motore sul capitolo N prima del diagnosta (capitolo.py senza scrivere il report, audit anti-IA,
    frasi finali di zb stile). Con un esito bloccante: ErroreMotore, niente diagnosta. Altrimenti scrive
    06-diagnostica/frasi-finali/NN.md e 06-diagnostica/misure/NN.md (prima riga con l'impronta del capitolo):
    le righe misurate che la sessione principale passa al diagnosta. Restituisce il percorso del file delle misure."""
    import capitolo
    import stile
    import revisione
    n = str(n)
    met, out = capitolo.controlla(cartella, libro, profilo, n)
    met_ia, ia = capitolo.anti_ia(cartella, libro, profilo, n, scrivi=False)
    tutti = out + comune.applica_eccezioni(ia, libro)
    blocca = bloccanti_prima_della_revisione(tutti, libro)
    if blocca:
        elenco = '; '.join(f'{r["controllo"]} {r["esito"]}' + (f' (riga {r["riga"]})' if r['riga'] else '')
                           + (f': {r["dettaglio"]}' if r['dettaglio'] else '') for r in blocca[:8])
        raise comune.ErroreMotore(f'Capitolo {n}: misure del motore non superate ({len(blocca)}): {elenco}. '
                                  'Non chiamare il diagnosta: prima una correzione mirata di chi scrive, poi di nuovo '
                                  f'«zb ruolo <libro> diagnosta {n}».')
    _, _, testi = rapporto_capitolo(cartella, libro, n)
    p = dict(comune.unita(cartella, libro))[n]
    ff = stile.frasi_finali(open(p, encoding='utf-8').read(), comune.lingue()[libro['lingua']])
    comune.scrivi(cartella, f'06-diagnostica/frasi-finali/{nn(n)}.md', stile.tabella_frasi_finali(n, ff))
    righe = [f'<!-- zb: misure; su={revisione.impronta(cartella, testi)} -->',
             f'# Misure del capitolo {n} per il diagnosta', '',
             'Scritte da «zb ruolo <libro> diagnosta N» prima della revisione: nessun KO oggettivo. Le righe sotto '
             'sono informazioni per il voto «pulizia», non conteggi da rifare.', '',
             '| Misura | Valore |', '|---|---|',
             f'| Parole | {met.get("parole")} |',
             f'| Frase media | {met.get("frase_media")} (intervallo {met.get("frase_media_intervallo", "—")}) |',
             f'| Dialogo | {met.get("dialogo_percento")}% |',
             f'| Ripetizioni ravvicinate | {met_ia.get("ripetizioni_per_mille")} per mille |',
             f'| Aperture uguali | {met_ia.get("aperture_uguali")}% |',
             f'| Frasi finali | {len(ff)}, in 06-diagnostica/frasi-finali/{nn(n)}.md |', '',
             '## Righe misurate (avvisi che restano, con la riga)', '']
    righe += stile.tabella(tutti) if tutti else ['Nessun avviso.']
    righe += [''] + letture_diagnosta(cartella, libro, n, rel_cap=testi[0])
    if giro[0] == 2:
        import shutil
        shutil.copyfile(os.path.join(cartella, rel_audit(n)), os.path.join(cartella, f'06-diagnostica/audit/{nn(n)}-giro1.md'))
        righe += ['', '## Giro 2: solo queste frasi', '',
                  f'Il primo giro è in 06-diagnostica/audit/{nn(n)}-giro1.md. Rivedi solo queste voci sul testo corretto: '
                  'per ognuna «risolta» o «non risolta» con il motivo; non rifare la revisione intera. Poi una nuova riga '
                  '«Media: X.X» e l\'ultima riga «passa» o «non passa».', '']
        righe += [f'- {v}' for v in giro[1]]
    else:
        righe += ['', '## Giro 1: revisione completa', '',
                  f'Rapporto del ruolo (al massimo 400 parole): «## Voti» (sette voci 1-10), «Media: X.X», «## Continuità», '
                  f'«## Da correggere» (al massimo 5 voci «- r.N «frase»: motivo → cosa ottenere», oppure «- nessuna»), '
                  f'«## Lezione» (una riga: il difetto da non ripetere), '
                  f'ultima riga «passa» (media almeno {soglia_qualita(libro)}, nessun fatto contraddetto) o «non passa».']
    rel = misure_rel(n)
    comune.scrivi(cartella, rel, '\n'.join(righe) + '\n')
    return rel


def controlla_revisione_capitolo(cartella, libro, n):
    """Con «revisione_capitolo: obbligatoria» in libro.yaml (fase «stesura»): il rapporto del diagnosta sul capitolo
    N deve esistere, essere scritto sulla versione attuale del capitolo e chiudere con la riga «passa».
    Si ferma con ErroreMotore e il motivo; senza il campo non fa nulla."""
    if libro.get('revisione_capitolo') != 'obbligatoria' or not str(n).isdigit():
        return
    rel, ruolo, testi = rapporto_capitolo(cartella, libro, n)
    p = os.path.join(cartella, rel)
    aiuto = (f'«zb ruolo <libro> diagnosta {n}» dà la prima riga; il diagnosta scrive il rapporto in una sessione '
             'separata da chi ha scritto il capitolo e chiude con la riga «passa» o «non passa».')
    if not os.path.isfile(p):
        raise comune.ErroreMotore(f'Revisione del capitolo {n} mancante: {rel} (libro.yaml: revisione_capitolo: '
                                  f'obbligatoria). {aiuto}')
    righe = [r.strip() for r in open(p, encoding='utf-8').read().splitlines()]
    m = INTESTAZIONE.match(righe[0] if righe else '')
    attuale = impronta(cartella, testi)
    if not m or m.group(1) != ruolo:
        raise comune.ErroreMotore(f'{rel}: prima riga senza l\'intestazione del diagnosta. {aiuto}')
    if m.group(2) != attuale:
        raise comune.ErroreMotore(f'{rel}: revisione scritta su un\'altra versione del capitolo {n} (impronta '
                                  f'{m.group(2)}, attuale {attuale}). Serve una nuova revisione del testo attuale.')
    ultima = next((r for r in reversed(righe) if r), '').lower()
    if ultima == 'non passa':
        raise comune.ErroreMotore(f'{rel}: il capitolo {n} «non passa» la revisione. Correzione unica di chi scrive, '
                                  'poi nuova revisione.')
    if ultima != 'passa':
        raise comune.ErroreMotore(f'{rel}: l\'ultima riga deve essere «passa» o «non passa» (trovato «{ultima[:40]}»).')
    media, soglia = media_revisione(righe), soglia_qualita(libro)
    if media is None:
        raise comune.ErroreMotore(f'{rel}: manca la riga «Media: X.X» (media dei sette voti della revisione). {aiuto}')
    if media < soglia:
        raise comune.ErroreMotore(f'{rel}: «passa» con media {media} sotto la soglia di qualità {soglia} '
                                  '(soglia_qualita in libro.yaml): il capitolo non passa. Correzione mirata, poi nuova revisione.')
    pm = os.path.join(cartella, misure_rel(n))     # le misure del motore vengono prima del diagnosta
    prima = open(pm, encoding='utf-8').readline().strip() if os.path.isfile(pm) else ''
    if prima != f'<!-- zb: misure; su={attuale} -->':
        raise comune.ErroreMotore(f'{misure_rel(n)}: misure del motore assenti o scritte su un\'altra versione del '
                                  f'capitolo {n}. Prima del diagnosta: «zb ruolo <libro> diagnosta {n}».')


LEZIONI = '06-diagnostica/lezioni.md'
LEZIONI_MAX = 12


def registra_lezione(cartella, libro, n):
    """Capitolo N accettato: la riga della sezione «## Lezione» del rapporto audit/NN.md (un difetto da non ripetere,
    detto come regola) va in 06-diagnostica/lezioni.md, che zb prepara passa allo scrittore dei capitoli successivi.
    Ultime LEZIONI_MAX, senza doppioni. Restituisce la lezione registrata o None."""
    if not str(n).isdigit():
        return None
    p = os.path.join(cartella, rel_audit(n))
    if not os.path.isfile(p):
        return None
    lezione, dentro_sez = None, False
    for r in open(p, encoding='utf-8').read().splitlines():
        t = r.strip()
        if t.startswith('## '):
            dentro_sez = t[3:].strip().lower().startswith('lezione')
            continue
        if dentro_sez and t.startswith('- ') and t[2:].strip().lower().rstrip('.') not in ('nessuna', 'nessuno'):
            lezione = t[2:].strip()
            break
    if not lezione:
        return None
    pl = os.path.join(cartella, LEZIONI)
    prima = [r[2:].split(' (cap. ')[0] for r in open(pl, encoding='utf-8').read().splitlines()
             if r.startswith('- ')] if os.path.isfile(pl) else []
    voci = [r for r in open(pl, encoding='utf-8').read().splitlines() if r.startswith('- ')] if os.path.isfile(pl) else []
    if lezione in prima:
        return None
    voci = (voci + [f'- {lezione} (cap. {n})'])[-LEZIONI_MAX:]
    comune.scrivi(cartella, LEZIONI, '# Lezioni dei capitoli già rivisti\n\nDifetti trovati dal revisore: non ripeterli. '
                  'Le aggiunge «zb esito» dalla sezione «## Lezione» dei rapporti.\n\n' + '\n'.join(voci) + '\n')
    return lezione


MEDIA = re.compile(r'^\**media\**\s*:\s*\**\s*(\d+(?:[.,]\d+)?)', re.IGNORECASE)


def media_revisione(righe):
    """Ultima riga «Media: X.X» del rapporto (al secondo giro vale la nuova media); None se manca."""
    for r in reversed(righe):
        m = MEDIA.match(r.strip())
        if m:
            return float(m.group(1).replace(',', '.'))
    return None


def soglia_qualita(libro):
    """Voto medio minimo per «passa» (libro.yaml soglia_qualita; predefinito 7.5 sulla scala tarata del ruolo, dove
    6 è il mestiere e 8 «un editor lo terrebbe»: in stesura si avanza, la qualità finale sale nelle revisioni)."""
    return float(libro.get('soglia_qualita') or 7.5)


def impronta(cartella, testi):
    import revisione
    return revisione.impronta(cartella, testi)


def intestazione(cartella, rel):
    p = os.path.join(cartella, rel)
    if not os.path.isfile(p):
        return None
    with open(p, encoding='utf-8') as f:
        m = INTESTAZIONE.match(f.readline().strip())
    return (m.group(1), m.group(2)) if m else None


def commit_di_nascita(cartella, rel):
    """Hash dell'ultimo commit che ha cambiato `rel` (None se non salvato): quel commit non deve toccare il testo
    rivisto, così anche un rapporto riscritto dopo resta separato dal testo."""
    out = comune.git(cartella, 'log', '-1', '--format=%H', '--', rel)[1].split()
    return out[0] if out else None


def file_del_commit(cartella, commit):
    """File toccati da un commit, relativi alla cartella del libro."""
    radice = comune.radice_git(cartella)
    out = comune.git(cartella, 'show', '--name-only', '--format=', commit)[1].splitlines()
    rel = os.path.relpath(cartella, radice)
    pref = '' if rel == '.' else rel + '/'
    return {x[len(pref):] for x in out if x.startswith(pref)}


def problemi_rapporto(cartella, rel, ruolo, testi):
    """Controlli di un rapporto: esiste, intestazione, impronta attuale, salvato a parte dal testo rivisto."""
    if not os.path.isfile(os.path.join(cartella, rel)):
        return [f'{rel}: manca (ruolo {ruolo}; prima riga da «zb ruolo <libro> {ruolo}»)']
    out = []
    i = intestazione(cartella, rel)
    if not i:
        out.append(f'{rel}: prima riga «<!-- zb: ruolo=…; su=… -->» mancante')
    elif i[0] != ruolo:
        out.append(f'{rel}: scritto dal ruolo «{i[0]}», atteso «{ruolo}»')
    elif i[1] != impronta(cartella, testi):
        out.append(f'{rel}: scritto su una versione diversa del testo (su={i[1]}, ora {impronta(cartella, testi)}): '
                   'rifallo sul testo attuale')
    c = commit_di_nascita(cartella, rel)
    if not c:
        out.append(f'{rel}: non ancora salvato in un commit')
    else:
        comuni = file_del_commit(cartella, c) & set(testi)
        if comuni:
            out.append(f'{rel}: salvato nello stesso commit del testo rivisto ({", ".join(sorted(comuni))}): '
                       'chi scrive non rivede; salva il testo e il rapporto in commit separati')
    return out


def problemi_fase(cartella, libro, fase):
    out = []
    for rel, ruolo, testi in rapporti(cartella, libro, fase):
        out += problemi_rapporto(cartella, rel, ruolo, testi)
    return out


def documenti_gate(cartella, libro, stato, gate):
    if gate == 'struttura':
        return file_struttura() + [r for r, _, _ in rapporti(cartella, libro, 'struttura')]
    if gate == 'documenti':
        import codex
        # più la nota di direzione del direttore editoriale (editoriale/ruoli/01-direttore-editoriale.md; da motore)
        d = ['libro.yaml', '02-bibbia/bibbia.md', 'cronologia.yaml', '03-architettura/manuale-di-stile.md', NOTA_DIREZIONE]
        return d + [v['file'] for v in codex.schede(cartella).values()]
    if gate in REVISIONI:
        return [r for r, _, _ in rapporti(cartella, libro, gate)]
    if gate == 'canone':
        return [CANONE]
    if gate == 'guida':
        return ['00-progetto/guida-traduzione.md', '00-progetto/glossario.yaml']
    raise comune.ErroreMotore(f'Gate sconosciuto: {gate}')


# ---------------------------------------------------------------- pronto e ok

def pronto(cartella, libro, stato, f):
    """«zb pronto» nelle fasi del percorso editoriale. True se ha gestito la fase."""
    import fase as F
    import struttura
    fs = stato['fase']
    if fs == 'guida':
        import traduci
        p = []
        g = os.path.join(cartella, '00-progetto', 'guida-traduzione.md')
        if not os.path.isfile(g) or comune.MODELLO in open(g, encoding='utf-8').read():
            p.append('00-progetto/guida-traduzione.md: ancora modello')
        p += traduci.problemi_glossario(cartella)
        if p:
            raise comune.ErroreMotore('Guida e glossario non pronti:\n- ' + '\n- '.join(p[:30]))
        if 'guida' in F.gate_attivi(libro):
            F.apri_gate(cartella, libro, stato, 'guida', passo='guida in revisione')
        else:
            F.registra(cartella, stato, documenti_gate(cartella, libro, stato, 'guida'), senza_gate=True)
            stato.update(fase='stesura', passo='capitolo 1', gate_in_attesa=None)
        return True
    if fs in ('struttura', *REVISIONI) and (fs == 'struttura' or (stato.get('sottofase') or 'proposte') == 'proposte'):
        import ruolo
        ruolo.controlla_separazione_gate(cartella, fs)      # un ruolo per sessione (da motore)
    if fs == 'struttura':
        p = struttura.verifica(cartella) + problemi_fase(cartella, libro, 'struttura')
        if p:
            raise comune.ErroreMotore('Struttura non pronta:\n- ' + '\n- '.join(p[:30]))
        # gate automatico: lo verifica il motore, mai l'autore (anche se «struttura» è in libro.yaml)
        F.registra(cartella, stato, documenti_gate(cartella, libro, stato, 'struttura'), senza_gate=True)
        chiudi_struttura(stato)
        import nuovo
        creati = nuovo.genera_documenti(cartella)
        print('Struttura verificata dal motore (gate automatico): nove file e rapporti registrati, nessuna fermata; '
              f'fase «documenti». Documenti creati: {", ".join(creati) if creati else "nessuno (già presenti)"}.')
        return True
    if fs == 'documenti':
        import codex
        p = codex.verifica(cartella)
        if p:
            raise comune.ErroreMotore('Codex non pronto:\n- ' + '\n- '.join(p[:30]))
        return False            # il resto lo fa fase.py come sempre
    if fs in REVISIONI:
        sotto = stato.get('sottofase') or 'proposte'
        if sotto == 'proposte':
            if fs == 'bozze':
                nome = comune.nome_file(libro['titolo'])
                if not os.path.isfile(os.path.join(cartella, '05-output', f'{nome}.pdf')):
                    raise comune.ErroreMotore('Bozze: prima «zb compila» e «zb impagina» (il PDF delle bozze manca).')
            p = problemi_fase(cartella, libro, fs)
            if p:
                raise comune.ErroreMotore(f'Fase «{fs}», proposte incomplete:\n- ' + '\n- '.join(p[:30]))
            if fs in F.gate_attivi(libro):
                F.apri_gate(cartella, libro, stato, fs, passo='proposte in revisione')
            else:
                F.registra(cartella, stato, documenti_gate(cartella, libro, stato, fs), senza_gate=True)
                stato['sottofase'] = 'applicazione'
                print(f'Gate «{fs}» non previsto: proposte registrate senza fermata; applicazione.')
            return True
        # applicazione finita
        cod, out, _ = comune.git(cartella, 'status', '--porcelain', '--', '.')
        if out:
            raise comune.ErroreMotore('Modifiche non salvate nel libro: salva prima di chiudere la fase.\n' + out)
        n = riregistra_testi(cartella, stato, fs)
        if n:
            print(f'Testi cambiati dalle proposte approvate e registrati di nuovo: {n}.')
        nuova = successiva(libro, fs)
        stato.update(fase=nuova, sottofase=None if nuova == 'chiusura' else 'proposte',
                     passo='controlli finali' if nuova == 'chiusura' else 'proposte', gate_in_attesa=None)
        print(f'Fase «{fs}» chiusa (proposte approvate e applicate): fase «{nuova}».')
        return True
    return False


def testo_in_revisione(rel):
    """Capitoli e loro report: cambiano per scelta nelle fasi di revisione (proposte approvate al gate)."""
    return rel.startswith('04-manoscritto/') or rel.startswith('06-diagnostica/capitoli/')


def riregistra_testi(cartella, stato, fs):
    """Registra di nuovo i capitoli approvati cambiati nell'applicazione delle proposte (autorizzati dal gate)."""
    import fase as F
    cambiati = [rel for rel, v in stato['documenti_approvati'].items() if testo_in_revisione(rel)
                and os.path.isfile(os.path.join(cartella, rel))
                and not comune.documento_invariato(os.path.join(cartella, rel), v['sha256'], v.get('commit'))]
    for rel in cambiati:
        prima = stato['documenti_approvati'][rel]
        F.registra(cartella, stato, [rel])
        stato['documenti_approvati'][rel]['riapprovazioni'] = (prima.get('riapprovazioni') or []) + [
            {'data': datetime.date.today().isoformat(), 'motivo': f'fase «{fs}»: proposte approvate al gate',
             'sha256_precedente': prima['sha256'], 'commit_precedente': prima.get('commit')}]
    return len(cambiati)


def chiudi_struttura(stato):
    stato.update(fase='documenti', passo='da completare', gate_in_attesa=None, sottofase=None)
    stato['revisione_in_corso'] = None


def dopo_ok(cartella, libro, stato, gate):
    """Effetti dell'«ok» sui gate del percorso editoriale. True se ha gestito il gate."""
    if gate == 'guida':
        stato.update(fase='stesura', passo='capitolo 1', gate_in_attesa=None)
        stato['revisione_in_corso'] = None
        print('Guida e glossario approvati: traduzione del capitolo 1 (agente traduttore, in sequenza).')
        return True
    if gate == 'struttura':
        chiudi_struttura(stato)
        print('Struttura approvata: fase «documenti» (direttore-editoriale: bibbia, codex, cronologia, manuale).')
        return True
    if gate in REVISIONI:
        stato['sottofase'] = 'applicazione'
        stato['passo'] = 'applicazione delle proposte approvate'
        print(f'Proposte della fase «{gate}» approvate: applicale con modifiche puntuali, «zb esito <libro> N» '
              'per rimisurare, poi «zb pronto <libro>».')
        return True
    if gate == 'canone':
        fb = stato.setdefault('fatti_bloccati', [])
        for p in stato.pop('canone_proposte', []):
            if p['azione'] == 'aggiungi' and p['testo'] not in fb:
                fb.append(p['testo'])
            elif p['azione'] == 'togli' and p['testo'] in fb:
                fb.remove(p['testo'])
        stato['documenti_approvati'].pop(CANONE, None)    # il file delle proposte si riscrive alla prossima
        stato.setdefault('canone_modifiche', []).append({'data': datetime.date.today().isoformat(),
                                                          'fatti': len(fb)})
        print(f'Canone aggiornato: {len(fb)} fatti bloccati.')
        return True
    return False


def dopo_stesura(stato, libro=None):
    """Tutte le unità scritte: nel percorso editoriale si passa alla revisione strutturale del manoscritto;
    in una traduzione al line editing nella lingua di arrivo."""
    if traduzione(libro):
        stato.update(fase='line', sottofase='proposte', passo='line editing nella lingua di arrivo', gate_in_attesa=None)
        print('Tutti i capitoli tradotti e controllati: fase «line» (line-editor nella lingua di arrivo).')
        return
    stato.update(fase='struttura_manoscritto', sottofase='proposte', passo='diagnosi e piano di revisione',
                 gate_in_attesa=None)
    print('Tutte le unità del piano sono scritte e accettate: fase «struttura_manoscritto» '
          '(diagnosta, poi editor-strutturale).')


def prossimo(stato):
    fs, sotto = stato['fase'], stato.get('sottofase') or 'proposte'
    if fs == 'guida':
        return 'Traduzione: guida e glossario (un termine = una traduzione); poi «zb pronto <traduzione>».'
    if fs == 'struttura':
        return ('Architetto: i nove file di 03-struttura/; poi diagnosta ed editor-strutturale (commit separati); '
                'poi «zb pronto <libro>» (il motore verifica la struttura, senza fermata).')
    if fs in REVISIONI:
        chi = {'struttura_manoscritto': 'diagnosta, poi editor-strutturale', 'line': 'line-editor per ogni capitolo',
               'copy': 'correttore-italiano per ogni capitolo', 'bozze': 'zb compila, zb impagina, poi correttore-bozze',
               'fedelta': 'revisore-fedelta (affiancata e ritraduzione a campione, sessione nuova)'}[fs]
        if sotto == 'proposte':
            return f'Fase «{fs}»: rapporti di {chi} (commit separati dal testo); poi «zb pronto <libro>».'
        return f'Fase «{fs}»: applica solo le proposte approvate, «zb esito <libro> N»; poi «zb pronto <libro>».'
    return None


# ---------------------------------------------------------------- canone

def canone(cartella, libro, stato, resto):
    """«canone proponi <fatto>» | «canone togli <fatto>» | «canone mostra»."""
    import fase as F
    azione = resto[0] if resto else 'mostra'
    if azione == 'mostra':
        fb = stato.get('fatti_bloccati') or []
        print(f'Fatti bloccati: {len(fb)}')
        for i, x in enumerate(fb, 1):
            print(f'{i}. {x}')
        for p in stato.get('canone_proposte') or []:
            print(f'proposta: {p["azione"]} «{p["testo"]}»')
        return
    testo = ' '.join(resto[1:]).strip()
    if azione not in ('proponi', 'togli') or not testo:
        raise comune.ErroreMotore('Uso: canone <libro> proponi <fatto> | togli <fatto> | mostra')
    if stato['gate_in_attesa'] and stato['gate_in_attesa'] != 'canone':
        raise comune.ErroreMotore(f'Gate «{stato["gate_in_attesa"]}» aperto: chiudilo prima di cambiare il canone.')
    if azione == 'togli' and testo not in (stato.get('fatti_bloccati') or []):
        raise comune.ErroreMotore(f'«{testo}» non è tra i fatti bloccati.')
    prop = stato.setdefault('canone_proposte', [])
    prop.append({'azione': 'aggiungi' if azione == 'proponi' else 'togli', 'testo': testo,
                 'data': datetime.date.today().isoformat()})
    righe = ['# Proposte di modifica del canone', '', 'Fatti bloccati attuali:', '']
    righe += [f'- {x}' for x in stato.get('fatti_bloccati') or []] or ['- nessuno']
    righe += ['', 'Proposte (si applicano solo con «ok»):', '']
    righe += [f'- {p["azione"]}: {p["testo"]}' for p in prop]
    comune.scrivi(cartella, CANONE, '\n'.join(righe) + '\n')
    print(f'Proposta registrata in {CANONE}. Salva il file (commit), poi «zb canone <libro> gate».')


def apri_gate_canone(cartella, libro, stato):
    import fase as F
    if not stato.get('canone_proposte'):
        raise comune.ErroreMotore('Nessuna proposta di canone da approvare.')
    if stato['gate_in_attesa']:
        raise comune.ErroreMotore(f'Gate «{stato["gate_in_attesa"]}» già aperto.')
    F.apri_gate(cartella, libro, stato, 'canone')

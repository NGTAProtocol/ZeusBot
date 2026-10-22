"""Voci narrative della banca-voci (comando «zb voce»). Sola lettura.

Uso: python3 -B voce.py lista
     python3 -B voce.py mostra <slug> [N]
     python3 -B voce.py verifica <slug>
La banca-voci è un repository separato, fuori dal motore: il percorso si legge solo da
ZB_BANCA_VOCI, mai scritto nel codice. Struttura attesa:
  indice.yaml                 voci: [{slug, nome, genere, stato: pronta | da_completare}]
  voci/<slug>/scheda.md       7 sezioni «## N. Titolo», nell'ordine di SEZIONI
  voci/<slug>/divieti.yaml    divieti: [{id, espressione | pattern, tipo, nota, massimo}]: espressioni vietate
                              della voce; stile.py le aggiunge alle voci del libro (modalità avviso). Con
                              «massimo: N» (intero ≥ 0, facoltativo) l'avviso scatta solo oltre N occorrenze
                              nell'unità; senza, ogni occorrenza è un avviso (come prima)
- lista: le voci dell'indice, con genere e stato.
- mostra: la scheda in blocchi di circa 120 righe (come revisione.py); N predefinito 1.
- verifica: la voce è nell'indice, ha la scheda con le 7 sezioni e il campo «ambientazione:»
  nella sezione 7, divieti.yaml leggibile, stato «pronta». Codice 1 con l'elenco dei problemi.
  Le pagine d'esempio non sono richieste: la banca contiene solo schede.
Senza ZB_BANCA_VOCI, con una cartella senza indice.yaml o con una voce assente: FERMO (codice 2).
"""
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import revisione  # noqa: E402

SEZIONI = ['Nome e ruolo', 'Principi', 'Ritmo e sintassi', 'Lessico', 'Adattamento per genere',
           'Campione', 'Istruzione di esecuzione']
STATI = ('pronta', 'da_completare')


def banca():
    """Cartella della banca-voci da ZB_BANCA_VOCI; FERMO se manca o non è una banca."""
    p = os.environ.get('ZB_BANCA_VOCI', '').strip()
    if not p:
        raise comune.ErroreMotore('ZB_BANCA_VOCI non impostata: indica la cartella della banca-voci, per esempio\n'
                                  '  export ZB_BANCA_VOCI=<cartella della banca-voci>\n(motore/README.md, «Banca-voci»)')
    p = os.path.realpath(os.path.expanduser(p))
    if not os.path.isfile(os.path.join(p, 'indice.yaml')):
        raise comune.ErroreMotore(f'ZB_BANCA_VOCI={p}: nessun indice.yaml, non è una banca-voci.')
    return p


def indice(b):
    dati = comune.leggi_yaml(os.path.join(b, 'indice.yaml')) or {}
    voci = dati.get('voci') if isinstance(dati, dict) else None
    if not isinstance(voci, list) or not all(isinstance(v, dict) and v.get('slug') for v in voci):
        raise comune.ErroreMotore(f'{b}/indice.yaml: serve «voci:», una lista di voci con slug, nome, genere, stato.')
    return voci


def voce_in_indice(b, slug):
    for v in indice(b):
        if v['slug'] == slug:
            return v
    raise comune.ErroreMotore(f'Voce «{slug}» assente da {b}/indice.yaml. Elenco: zb voce lista')


def scheda(b, slug):
    return os.path.join(b, 'voci', slug, 'scheda.md')


def divieti(b, slug):
    """Voci di stile (modalità avviso) da voci/<slug>/divieti.yaml; FERMO se il file manca o non è valido.
    Facoltativi: «massimo» per divieto; «gruppi: {nome: {massimo: N}}» e «gruppo: nome» sul divieto per un limite
    complessivo su più forme (per esempio tutte le chiuse a sentenza: una per capitolo in tutto)."""
    p = os.path.join(b, 'voci', slug, 'divieti.yaml')
    if not os.path.isfile(p):
        raise comune.ErroreMotore(f'divieti.yaml assente: voci/{slug}/divieti.yaml')
    try:
        dati = comune.leggi_yaml(p) or {}
    except Exception as e:  # yaml non valido: messaggio, mai traceback
        raise comune.ErroreMotore(f'voci/{slug}/divieti.yaml non leggibile: {e}'.splitlines()[0])
    elenco = dati.get('divieti') if isinstance(dati, dict) else None
    if not isinstance(elenco, list) or not elenco:
        raise comune.ErroreMotore(f'voci/{slug}/divieti.yaml: serve «divieti:», una lista non vuota')
    gruppi = dati.get('gruppi') or {}
    if not isinstance(gruppi, dict):
        raise comune.ErroreMotore(f'voci/{slug}/divieti.yaml: «gruppi» deve essere una mappa nome: {{massimo: N}}')
    for g, gv in gruppi.items():
        m = gv.get('massimo') if isinstance(gv, dict) else None
        if isinstance(m, bool) or not isinstance(m, int) or m < 0:
            raise comune.ErroreMotore(f'voci/{slug}/divieti.yaml: gruppo «{g}» senza «massimo» intero ≥ 0 ({m!r})')
    out = []
    for i, d in enumerate(elenco):
        if not isinstance(d, dict) or not d.get('id') or not (d.get('espressione') or d.get('pattern')):
            raise comune.ErroreMotore(f'voci/{slug}/divieti.yaml: voce {i + 1} senza id o senza espressione/pattern')
        pattern = d.get('pattern') or r'(?i)(?<!\w)' + re.escape(str(d['espressione'])) + r'(?!\w)'
        try:
            re.compile(pattern)
        except re.error as e:
            raise comune.ErroreMotore(f'voci/{slug}/divieti.yaml: pattern non valido in «{d["id"]}»: {e}')
        voce = {'id': f'{slug}:{d["id"]}', 'espressione': d.get('espressione'), 'pattern': pattern,
                'modalita': 'avviso', 'nota': d.get('nota') or f'divieto della voce {slug}'}
        if 'massimo' in d:
            m = d['massimo']
            if isinstance(m, bool) or not isinstance(m, int) or m < 0:
                raise comune.ErroreMotore(f'voci/{slug}/divieti.yaml: «massimo» non valido in «{d["id"]}» '
                                          f'({m!r}): serve un intero ≥ 0')
            voce['massimo'] = m      # stile.py: AVVISO solo oltre il massimo di occorrenze nell'unità
        if 'gruppo' in d:
            if d['gruppo'] not in gruppi:
                raise comune.ErroreMotore(f'voci/{slug}/divieti.yaml: «{d["id"]}» nel gruppo «{d["gruppo"]}», che non è '
                                          'definito in «gruppi»')
            # stile.py: tutte le forme del gruppo contano insieme contro un solo massimo per unità
            voce['gruppo'] = f'{slug}:{d["gruppo"]}'
            voce['massimo_gruppo'] = gruppi[d['gruppo']]['massimo']
        out.append(voce)
    return out


def divieti_del_libro(libro):
    """Divieti della voce scelta in libro.yaml; [] senza voce, senza ZB_BANCA_VOCI o con la voce non leggibile
    (lo segnala zb avvio con un AVVISO)."""
    v = libro.get('voce') or {}
    if not v.get('slug'):
        return []
    try:
        return divieti(banca(), v['slug'])
    except comune.ErroreMotore:
        return []


def esempi_debole_forte(b, slug):
    """Numero di esempi «versione debole → versione forte» nella sezione 6 della scheda: ogni «Debole:» (a inizio
    riga, numerato, o a metà riga dopo una frase di presentazione), contati solo se la sezione ha anche «Forte:»."""
    corpo = sezioni(open(scheda(b, slug), encoding='utf-8').read()).get(6, ('', ''))[1]
    deboli = len(re.findall(r'(?<!\w)Debole:', corpo))
    forti = len(re.findall(r'(?<!\w)Forte:', corpo))
    return deboli if forti else 0


def registri(b, slug):
    """{registro: [a, b]} dalla riga «frase media» della tabella nella sezione 3 della scheda («Ritmo e sintassi»):
    il nome del registro è l'intestazione della colonna senza la parentesi e senza la parola «registro»
    («Registro corto (Winslow)» → «corto»); l'intervallo è il primo «a-b» della cella. {} se la tabella manca."""
    p = scheda(b, slug)
    if not os.path.isfile(p):
        return {}
    corpo = sezioni(open(p, encoding='utf-8').read()).get(3, ('', ''))[1]
    tabella = [[c.strip() for c in r.strip().strip('|').split('|')] for r in corpo.splitlines()
               if r.strip().startswith('|') and not re.match(r'^\|[\s|:-]+\|?$', r.strip())]
    riga = next((r for r in tabella[1:] if r and r[0].lower().startswith('frase media')), None)
    if not tabella or not riga:
        return {}
    out = {}
    for testa, cella in zip(tabella[0][1:], riga[1:]):
        nome = re.sub(r'\(.*?\)', '', testa)
        nome = re.sub(r'(?i)\bregistro\b', '', nome).strip().lower()
        m = re.search(r'(\d+)\s*-\s*(\d+)', cella)
        if nome and m and int(m.group(1)) <= int(m.group(2)):
            out[nome] = [int(m.group(1)), int(m.group(2))]
    return out


def registri_del_libro(libro):
    """Registri della voce scelta in libro.yaml; {} senza voce, senza ZB_BANCA_VOCI o con la voce non leggibile."""
    v = libro.get('voce') or {}
    if not v.get('slug'):
        return {}
    try:
        return registri(banca(), v['slug'])
    except comune.ErroreMotore:
        return {}


def sezioni(testo):
    """{numero: (titolo, corpo)} dei titoli «## N. Titolo»."""
    out, cur = {}, None
    for riga in testo.splitlines():
        m = re.match(r'^##\s+(\d+)\.?\s+(.*)$', riga)
        if m:
            cur = int(m.group(1))
            out[cur] = (m.group(2).strip(), [])
        elif cur is not None:
            out[cur][1].append(riga)
    return {n: (t, '\n'.join(c)) for n, (t, c) in out.items()}


def problemi(b, slug):
    """Elenco dei problemi della voce (vuoto se verifica). La voce deve essere nell'indice."""
    v = voce_in_indice(b, slug)
    out = []
    p = scheda(b, slug)
    if not os.path.isfile(p):
        out.append(f'scheda assente: voci/{slug}/scheda.md')
    else:
        sez = sezioni(open(p, encoding='utf-8').read())
        for i, nome in enumerate(SEZIONI, 1):
            if i not in sez:
                out.append(f'sezione {i} «{nome}» mancante')
            elif not sez[i][0].lower().startswith(nome.lower()):
                out.append(f'sezione {i}: titolo «{sez[i][0]}», atteso «{nome}…»')
        if 7 in sez and not re.search(r'(?im)^\W*ambientazione\s*:', sez[7][1]):
            out.append('sezione 7: manca il campo «ambientazione:»')
    try:
        divieti(b, slug)
    except comune.ErroreMotore as e:
        out.append(str(e))
    stato = v.get('stato')
    if stato not in STATI:
        out.append(f'stato «{stato}» non ammesso ({" | ".join(STATI)})')
    elif stato != 'pronta':
        out.append(f'voce non pronta (stato: {stato}): non si usa per scrivere finché non è completata')
    return out


def lista(b):
    voci = indice(b)
    print(f'Banca-voci: {b}')
    print('| Slug | Nome | Genere | Stato |')
    print('|---|---|---|---|')
    for v in voci:
        g = v.get('genere') or []
        print(f'| {v["slug"]} | {v.get("nome", "")} | {", ".join(g) if isinstance(g, list) else g} | {v.get("stato", "")} |')
    print(f'Voci: {len(voci)}, pronte: {sum(1 for v in voci if v.get("stato") == "pronta")}')
    return 0


def mostra(b, slug, n):
    v = voce_in_indice(b, slug)
    p = scheda(b, slug)
    if not os.path.isfile(p):
        raise comune.ErroreMotore(f'Scheda assente: {p}')
    pezzi = revisione.taglia(open(p, encoding='utf-8').read())
    if not 1 <= n <= len(pezzi):
        raise comune.ErroreMotore(f'Blocco {n} inesistente: i blocchi sono {len(pezzi)}')
    x, y, testo = pezzi[n - 1]
    if v.get('stato') != 'pronta':
        print(f'AVVISO: voce non pronta (stato: {v.get("stato")}).')
    print(f'Voce {slug} — voci/{slug}/scheda.md — Blocco {n} di {len(pezzi)}, righe {x}-{y} — '
          f'sha256 {comune.sha256_file(p)[:12]}\n\n{testo}\n')
    if n == len(pezzi):
        print('Fine della scheda.')
    return 0


def verifica(b, slug):
    out = problemi(b, slug)
    if out:
        print(f'KO voce {slug}')
        for x in out:
            print(f'  - {x}')
        return 1
    print(f'OK voce {slug}: 7 sezioni, {len(divieti(b, slug))} divieti, pronta')
    return 0


def main(argv):
    args = comune.argomenti(argv)
    uso = 'Uso: zb voce lista | zb voce mostra <slug> [N] | zb voce verifica <slug>'
    if not args or args[0] not in ('lista', 'mostra', 'verifica'):
        raise comune.ErroreMotore(uso)
    if args[0] != 'lista' and len(args) < 2:
        raise comune.ErroreMotore(uso)
    b = banca()
    if args[0] == 'lista':
        return lista(b)
    if args[0] == 'mostra':
        return mostra(b, args[1], int(args[2]) if len(args) > 2 and args[2].isdigit() else 1)
    return verifica(b, args[1])


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

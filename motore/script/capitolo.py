"""Controlli di un capitolo in un colpo solo (proposta C.2).

Uso: python3 -B capitolo.py <libro> <N> [--schermo]
N è il numero del capitolo, oppure il nome di un'unità («prologo», «interludio II»).
Esegue: parole con il metodo unico rispetto a minimo del profilo (KO, solo capitoli)
e budget di piano-parole.md (AVVISO oltre la tolleranza); totale previsto del libro (AVVISO oltre
capitoli.tolleranza_totale, con il budget residuo proposto, vedi conta.py); controlli di stile.py;
continuità di continuita.py; anti-riciclo di riciclo.py; dichiarazioni della riga
nascosta <!-- zb: … --> secondo «dichiarazioni» di libro.yaml; scene (solo capitoli numerati), contate
dal separatore struttura.separatore_scena.sorgente: numero fuori da capitoli.scene_per_capitolo (KO),
scena sotto il minimo di scene.lunghezza (KO) o sopra il massimo (AVVISO). Il sequel è informativo.
Report: <libro>/06-diagnostica/capitoli/NN.md, con la checklist manuale (tic fissi, voci di cronologia
toccate e le voci del libro in checklist_capitolo di libro.yaml). Codice 1 se c'è almeno un KO.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import conta  # noqa: E402
import continuita  # noqa: E402
import riciclo  # noqa: E402
import stile  # noqa: E402
from stile import risultato, tabella  # noqa: E402


CHECKLIST_TIC = [
    'Tic: descrizione del meteo all\'inizio del capitolo (05-critica r. 20)',
    'Tic: domande retoriche interiori in serie (05-critica r. 20)',
    'Tic: chiusure di paragrafo con morale o riflessione (05-critica r. 20)',
    'Tic: scena che finisce con un momento di consapevolezza (05-critica r. 20)',
]


def dichiarazioni(cartella, libro, unita, nome):
    """Controlli delle dichiarazioni dell'unità `nome` (lista di (nome, percorso) in ordine)."""
    spec = libro.get('dichiarazioni') or {}
    if not spec or not nome.isdigit():
        return []
    out = []
    scaletta = {r.get('Unità', '').lower(): r for r in
                comune.tabella_md(os.path.join(cartella, '03-architettura', 'scaletta.md'))}
    capitoli = [(n, comune.dichiarazioni_unita(open(p, encoding='utf-8').read()), p)
                for n, p in unita if n.isdigit()]
    idx = [n for n, _, _ in capitoli].index(nome)
    dic, percorso = capitoli[idx][1], capitoli[idx][2]
    for campo, s in spec.items():
        val = dic.get(campo)
        if val is None:
            out.append(risultato(nome, f'dichiarazione:{campo}', 'KO', None, 'campo non dichiarato nella riga zb'))
            continue
        ammessi = s.get('sigle') or s.get('valori')
        if ammessi and val not in [str(a) for a in ammessi]:
            out.append(risultato(nome, f'dichiarazione:{campo}', 'KO', None, f'«{val}» non ammesso ({", ".join(map(str, ammessi))})'))
        if s.get('prevista_da') == 'scaletta':
            prevista = (scaletta.get(nome) or {}).get(campo.capitalize())
            if prevista and prevista != val:
                out.append(risultato(nome, f'dichiarazione:{campo}', 'AVVISO', None,
                                     f'dichiarata {val}, prevista in scaletta {prevista}'))
        for chiave, limite in s.items():
            if chiave.endswith('massimo_consecutivi'):
                sigla = chiave[:-len('_massimo_consecutivi')] if chiave != 'massimo_consecutivi' else None
                if sigla is not None and val != sigla:
                    continue
                k = 0
                for _, d, _ in reversed(capitoli[:idx + 1]):
                    if d.get(campo) == val:
                        k += 1
                    else:
                        break
                if k > limite:
                    out.append(risultato(nome, f'dichiarazione:{campo}', 'KO', None,
                                         f'{k} capitoli di fila con {campo}={val} (massimo {limite})'))
        if 'riga_finale_min_parole' in s:
            prosa = comune.righe_prosa(open(percorso, encoding='utf-8').read())
            if prosa:
                n, r = prosa[-1]
                if len(comune.parole(r)) < s['riga_finale_min_parole']:
                    out.append(risultato(nome, f'dichiarazione:{campo}', 'KO', n,
                                         f'ultima riga di {len(comune.parole(r))} parole: «{r.strip()}»'))
    return out


def scene(testo, libro):
    """[(riga di inizio, parole)] delle scene, separate da struttura.separatore_scena.sorgente."""
    sep = ((libro.get('struttura') or {}).get('separatore_scena') or {}).get('sorgente') or '* * *'
    out, inizio, righe = [], None, []
    for n, r in enumerate(testo.splitlines() + [sep], 1):
        if r.strip() == sep.strip():
            p = conta.conta_testo('\n'.join(righe))
            if p:
                out.append((inizio, p))
            inizio, righe = None, []
        else:
            if inizio is None and r.strip() and not r.strip().startswith(('#', '<!--')) and conta.conta_testo(r):
                inizio = n
            righe.append(r)
    return out


def controlla_scene(nome, testo, libro, profilo):
    sc = scene(testo, libro)
    lo, hi = profilo['capitoli']['scene_per_capitolo']
    mn, mx = profilo['scene']['lunghezza']
    out = []
    if not lo <= len(sc) <= hi:
        out.append(stile.risultato(nome, 'scene_numero', 'KO', None, f'{len(sc)} scene, ammesse {lo}-{hi}'))
    for i, (riga, p) in enumerate(sc, 1):
        if p < mn:
            out.append(stile.risultato(nome, 'scena_minimo', 'KO', riga, f'scena {i}: {p} parole, minimo {mn}'))
        elif p > mx:
            out.append(stile.risultato(nome, 'scena_massimo', 'AVVISO', riga, f'scena {i}: {p} parole, massimo {mx}'))
    return out


def controlla(cartella, libro, profilo, nome):
    unita = comune.unita(cartella, libro)
    nomi = [n for n, _ in unita]
    if nome not in nomi:
        raise comune.ErroreMotore(f'Unità «{nome}» inesistente in 04-manoscritto')
    percorso = dict(unita)[nome]
    testo = open(percorso, encoding='utf-8').read()
    out = []
    n_parole = conta.conta_testo(testo)
    if nome.isdigit() and n_parole < profilo['capitoli']['minimo']:
        out.append(risultato(nome, 'parole_minimo', 'KO', None,
                             f'{n_parole} parole, minimo {profilo["capitoli"]["minimo"]}'))
    bud = conta.budget(cartella).get(nome.lower())
    if bud:
        sc = (n_parole - bud) / bud
        if abs(sc) > profilo['capitoli']['tolleranza_budget']:
            out.append(risultato(nome, 'parole_budget', 'AVVISO', None,
                                 f'{n_parole} parole su {bud} ({sc:+.0%}, tolleranza ±{profilo["capitoli"]["tolleranza_budget"]:.0%})'))
    avviso = conta.totale_previsto(cartella, libro, profilo)[3]
    if avviso:
        out.append(risultato(nome, 'parole_totale', 'AVVISO', None, avviso))
    if nome.isdigit():
        out += controlla_scene(nome, testo, libro, profilo)
    for n_int, d in comune.interludi_in_anticipo(cartella, libro):
        if n_int == nome:
            out.append(risultato(nome, 'posizione', 'AVVISO', None,
                                 f'in anticipo: va dopo il capitolo {d}, non ancora scritto; per ora sta in coda'))
    met, ris_stile = stile.controlla_libro(cartella, libro, profilo)[nome]
    out += ris_stile
    out += [r for r in continuita.controlla_libro(cartella, libro)[0] if r['unita'] == nome]
    out += [r for r in riciclo.controlla_libro(cartella, libro) if r['unita'] == nome]
    out += dichiarazioni(cartella, libro, unita, nome)
    met['parole'] = n_parole
    return met, out


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2:
        raise comune.ErroreMotore('Uso: capitolo.py <libro> <N> [--schermo]')
    cartella, libro, profilo = comune.carica_libro(args[0])
    nome = ' '.join(args[1:])
    met, out = controlla(cartella, libro, profilo, nome)
    ko = sum(1 for r in out if r['esito'] == 'KO')
    righe = [f'# Capitolo {nome} — controlli', '', f'Libro: {libro["titolo"]} — profilo: {libro["profilo"]}.', '',
             f'Parole (metodo unico): {met["parole"]} · frase media: {met["frase_media"]} · '
             f'dialogo: {met["dialogo_percento"]}%', '',
             f'Esito: {ko} KO, {sum(1 for r in out if r["esito"] == "AVVISO")} avvisi.', '']
    righe += tabella(out) if out else ['Nessun KO e nessun avviso.']
    righe += ['', '## Checklist manuale', '',
              'Controlli che il motore non sa fare da solo: li verifica l\'autore.', '',
              '| Controllo | Verificato dall\'autore |', '|---|---|']
    righe += [f'| {c} | [ ] |' for c in CHECKLIST_TIC]
    righe += [f'| {v} | [ ] |' for v in continuita.voci_toccate(cartella, libro, nome)]
    righe += [f'| {v} | [ ] |' for v in libro.get('checklist_capitolo') or []]
    testo = '\n'.join(righe + [''])
    if '--schermo' in argv:
        print(testo)
    else:
        nomefile = f'{int(nome):02d}' if nome.isdigit() else nome.replace(' ', '-')
        print('scritto', comune.scrivi(cartella, f'06-diagnostica/capitoli/{nomefile}.md', testo))
    return 1 if ko else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

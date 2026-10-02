"""Controlli di stile (proposta B.3, B.6, C.2).

Voci con solo_dialogo: true: ammesse solo nelle righe di dialogo (che cominciano con la
lineetta di lingue.yaml); ogni riga fuori dal dialogo che le contiene è KO.

Uso: python3 -B stile.py <libro> [N] [--schermo]
Per ogni unità (o solo la N): frase media e dialogo % (solo capitoli numerati),
voci con pattern (lista nera di base + voci del libro), parole filtro, candidati
similitudine, vincoli per capitolo, nomi vietati prima di un punto del libro.
Esiti: KO (blocca) o AVVISO (da guardare). Report: <libro>/06-diagnostica/stile.md.
"""
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

SIMILITUDINE = re.compile(r'(?i)\bcome (un|una|uno|il|la|lo|l\'|i|gli|le|se)\b|\bsembrava\b|\bpareva\b')


def risultato(unita, controllo, esito, riga=None, dettaglio=''):
    return {'unita': unita, 'controllo': controllo, 'esito': esito, 'riga': riga, 'dettaglio': dettaglio}


def voci_del_libro(libro):
    base = comune.leggi_yaml(os.path.join(comune.radice_motore(), 'dati', 'lista-nera.yaml'))
    return (base.get('voci') or []) + (libro.get('voci') or []), base.get('parole_filtro') or []


def metriche(testo, lingua):
    prosa = comune.righe_prosa(testo)
    tot = sum(len(comune.parole(r)) for _, r in prosa)
    dial = sum(len(comune.parole(r)) for _, r in prosa if r.lstrip().startswith(lingua['lineetta_dialogo']))
    unito = ' '.join(r.strip() for _, r in prosa)
    frasi = [f for f in re.split(r'(?<=[.!?…])\s+', unito) if comune.parole(f)]
    return {
        'parole': tot,
        'frasi': len(frasi),
        'frase_media': round(tot / len(frasi), 1) if frasi else 0.0,
        'dialogo_percento': round(100 * dial / tot, 1) if tot else 0.0,
    }


def occorrenze(prosa, pattern):
    rx = re.compile(pattern)
    return [(n, m.group(0)) for n, r in prosa for m in rx.finditer(r)]


def controlla_unita(nome, testo, profilo, libro, voci, filtro, lingua):
    out = []
    prosa = comune.righe_prosa(testo)
    met = metriche(testo, lingua)
    capitolo = nome.isdigit()
    if capitolo:
        a, b = profilo['frase_media']
        if not a <= met['frase_media'] <= b:
            out.append(risultato(nome, 'frase_media', 'KO', None, f'{met["frase_media"]} fuori da {a}-{b}'))
        a, b = profilo['dialogo_percento']
        if not a <= met['dialogo_percento'] <= b:
            out.append(risultato(nome, 'dialogo', 'KO', None, f'{met["dialogo_percento"]}% fuori da {a}-{b}%'))
        pf = profilo['parole_filtro']
        rx = r'(?i)(?<!\w)(' + '|'.join(re.escape(p) for p in filtro) + r')(?!\w)'
        n_filtro = len(occorrenze(prosa, rx))
        densita = 1000 * n_filtro / met['parole'] if met['parole'] else 0
        met['parole_filtro_per_1000'] = round(densita, 1)
        if densita > pf['massimo_per_1000_parole']:
            esito = 'KO' if pf['modalita'] in ('vieta', 'conta') else 'AVVISO'
            out.append(risultato(nome, 'parole_filtro', esito, None,
                                 f'{densita:.1f} ogni 1000 parole (massimo {pf["massimo_per_1000_parole"]})'))
        n_sim = len(occorrenze(prosa, SIMILITUDINE.pattern))
        met['candidati_similitudine'] = n_sim
        tetto = met['parole'] / profilo['similitudini_max_per_parole']
        if n_sim > tetto:
            out.append(risultato(nome, 'similitudini', 'AVVISO', None,
                                 f'{n_sim} candidati, tetto {tetto:.1f} (una ogni {profilo["similitudini_max_per_parole"]} parole)'))
    for v in voci:
        if v.get('ambito') == 'libro':
            continue
        if v.get('consentito_in_capitoli') is not None and comune.in_elenco(nome, v['consentito_in_capitoli']):
            continue
        occ = occorrenze(prosa, v['pattern'])
        if not occ:
            continue
        if v.get('vietato_in_capitoli') and not comune.in_elenco(nome, v['vietato_in_capitoli']):
            continue
        if v.get('solo_dialogo'):
            # Ammessa solo nel discorso diretto: fuori dal dialogo è KO (una riga per riga di testo);
            # nel dialogo vale la modalità della voce.
            dialogo = {n for n, r in prosa if r.lstrip().startswith(lingua['lineetta_dialogo'])}
            fuori = sorted({n for n, _ in occ if n not in dialogo})
            out += [risultato(nome, f'voce:{v["id"]}:fuori_dialogo', 'KO', n, 'fuori dal discorso diretto')
                    for n in fuori]
            occ = [(n, t) for n, t in occ if n in dialogo]
            if not occ:
                continue
        mod = v['modalita']
        if mod == 'vieta':
            out += [risultato(nome, f'voce:{v["id"]}', 'KO', n, t) for n, t in occ]
        elif mod == 'conta':
            if len(occ) > v.get('massimo', 0):
                out.append(risultato(nome, f'voce:{v["id"]}', 'KO', occ[v.get('massimo', 0)][0],
                                     f'{len(occ)} occorrenze (massimo {v.get("massimo", 0)})'))
        else:
            if 'massimo' in v:
                if len(occ) > v['massimo']:
                    out.append(risultato(nome, f'voce:{v["id"]}', 'AVVISO', occ[v['massimo']][0],
                                         f'{len(occ)} occorrenze (massimo {v["massimo"]})'))
            else:
                out += [risultato(nome, f'voce:{v["id"]}', 'AVVISO', n, t) for n, t in occ]
    for vc in libro.get('vincoli_capitolo') or []:
        occ = occorrenze(prosa, vc['pattern'])
        if not occ:
            continue
        fuori = ((vc.get('consentito_in_capitoli') is not None and not comune.in_elenco(nome, vc['consentito_in_capitoli']))
                 or comune.in_elenco(nome, vc.get('vietato_in_capitoli')))
        if fuori:
            out += [risultato(nome, f'vincolo:{vc["id"]}', 'KO', n, t) for n, t in occ]
    for nv in libro.get('nome_vietato_prima_di') or []:
        occ = occorrenze(prosa, nv['pattern'])
        if comune.in_elenco(nome, nv.get('vietato_in')):
            per_riga = {}
            for n, t in occ:
                per_riga.setdefault(n, []).append(t)
            out += [risultato(nome, f'nome_vietato:{nv["nome"]}', 'KO', n, ', '.join(ts))
                    for n, ts in sorted(per_riga.items())]
        elif comune.in_elenco(nome, nv.get('obbligatorio_in')) and not occ:
            out.append(risultato(nome, f'nome_obbligatorio:{nv["nome"]}', 'KO', None, 'nome assente'))
    return met, out


def controlla_libro(cartella, libro, profilo):
    """{unità: (metriche, risultati)} con le voci ad ambito «libro» cumulate in ordine di lettura."""
    lingua = comune.lingue()[libro['lingua']]
    voci, filtro = voci_del_libro(libro)
    esiti = {}
    contatori = {}
    for nome, p in comune.unita(cartella, libro):
        testo = open(p, encoding='utf-8').read()
        met, out = controlla_unita(nome, testo, profilo, libro, voci, filtro, lingua)
        prosa = comune.righe_prosa(testo)
        for v in voci:
            if v.get('ambito') != 'libro':
                continue
            for n, t in occorrenze(prosa, v['pattern']):
                contatori[v['id']] = contatori.get(v['id'], 0) + 1
                if contatori[v['id']] == v.get('massimo', 0) + 1:
                    esito = 'KO' if v['modalita'] in ('vieta', 'conta') else 'AVVISO'
                    out.append(risultato(nome, f'voce:{v["id"]}', esito, n,
                                         f'superato il massimo di {v.get("massimo", 0)} nel libro'))
        esiti[nome] = (met, out)
    return esiti


def tabella(risultati):
    righe = ['| Unità | Controllo | Esito | Riga | Dettaglio |', '|---|---|---|---|---|']
    for r in risultati:
        righe.append(f'| {r["unita"]} | {r["controllo"]} | {r["esito"]} | {r["riga"] or "—"} | {r["dettaglio"]} |')
    return righe


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: stile.py <libro> [N] [--schermo]')
    cartella, libro, profilo = comune.carica_libro(args[0])
    esiti = controlla_libro(cartella, libro, profilo)
    scelta = [args[1]] if len(args) > 1 else list(esiti)
    righe = ['# Controlli di stile', '', f'Libro: {libro["titolo"]} — profilo: {libro["profilo"]}.', '',
             '| Unità | Parole | Frase media | Dialogo % |', '|---|---|---|---|']
    tutti = []
    for u in scelta:
        if u not in esiti:
            raise comune.ErroreMotore(f'Unità «{u}» inesistente')
        met, out = esiti[u]
        righe.append(f'| {u} | {met["parole"]} | {met["frase_media"]} | {met["dialogo_percento"]} |')
        tutti += out
    righe += ['', '## Esiti', ''] + (tabella(tutti) if tutti else ['Nessun KO e nessun avviso.']) + ['']
    testo = '\n'.join(righe)
    if '--schermo' in argv:
        print(testo)
    else:
        print('scritto', comune.scrivi(cartella, '06-diagnostica/stile.md', testo))
    return 1 if any(r['esito'] == 'KO' for r in tutti) else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

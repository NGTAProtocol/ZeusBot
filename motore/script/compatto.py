"""Stato compatto del libro: <libro>/stato-compatto.md, 15-20 righe (comando «zb compatto <libro>»).

Uso: python3 -B compatto.py <libro>
Lo si legge nelle sessioni nuove al posto dei documenti interi, con la riga «Letto» e la scheda del
capitolo (motore/editoriale/risparmio-token.md). Contiene: fase e gate; ultimo capitolo salvato (con il
commit); stato dei personaggi (dall'ultima capsula); fatti bloccati; promesse aperte (registro delle
capsule); obiettivo del prossimo capitolo (dalla sua scheda); prossimo passo. Lo genera lo script: non si
scrive a mano.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

MASSIMO = 20


def taglia(s, n=150):
    s = ' '.join((s or '').split())
    return s if len(s) <= n else s[:n - 1].rstrip() + '…'


def genera(cartella, libro):
    import capsula
    import fase
    import struttura
    stato = fase.carica_stato(cartella)
    ultimo = stato.get('ultimo_capitolo_scritto') or 0
    u = dict(comune.unita(cartella, libro)).get(str(ultimo)) if ultimo else None
    commit = comune.ultimo_commit(cartella, u) if u else ''
    righe = [f'# Stato compatto — {libro["titolo"]}', '',
             f'- Fase: {stato["fase"]}{" (" + stato["sottofase"] + ")" if stato.get("sottofase") else ""}; '
             f'gate: {stato["gate_in_attesa"] or "nessuno"}.',
             f'- Ultimo capitolo salvato: {ultimo or "—"}' + (f' (commit {commit})' if commit else '') +
             f'; parole {stato["parole"]["scritte"]}/{stato["parole"]["obiettivo"]}.']
    if comune.editoriale(libro):
        nome, _ = struttura.macrostruttura(cartella)
        sf = os.path.join(cartella, comune.STRUTTURA, '09-scelte-fisse.md')
        scelte = [r.strip('- ').strip().rstrip('.') for r in open(sf, encoding='utf-8').read().splitlines()
                  if r.startswith('- ')] if os.path.isfile(sf) else []
        righe.append(f'- Macrostruttura: {nome or "—"}.')
        righe.append(f'- Scelte fisse: {taglia("; ".join(scelte[:3]), 150) or "—"}.')
    righe.append(f'- Gate attivi: {", ".join(fase.gate_attivi(libro))}.')
    righe.append(f'- Libro: {libro.get("lingua")}, profilo {libro["profilo"]}'
                 + (f', traduzioni previste: {", ".join(libro["lingue_target"])}' if libro.get('lingue_target') else '') + '.')
    pers = '—'
    if ultimo and os.path.isfile(os.path.join(cartella, capsula.rel(ultimo))):
        sez = capsula.sezioni_di(open(os.path.join(cartella, capsula.rel(ultimo)), encoding='utf-8').read(),
                                 capsula.lingua(libro))
        pers = sez.get(capsula.SEZIONI[capsula.lingua(libro)][1]) or '—'
    righe.append(f'- Personaggi (capsula {ultimo or "—"}): {taglia(pers)}')
    fb = stato.get('fatti_bloccati') or []
    righe.append(f'- Fatti bloccati: {len(fb)}' + (' (elenco in stato.yaml):' if len(fb) > 5 else ':'))
    righe += [f'  - {taglia(x, 120)}' for x in fb[:5]]
    aperte = []
    if os.path.isdir(os.path.join(cartella, capsula.CARTELLA)):
        aperte, _ = capsula.registro(cartella, libro)
    righe.append(f'- Promesse aperte: {", ".join("@prom:" + a for a in aperte) or "nessuna"}.')
    sk = struttura.schede(cartella).get(str(ultimo + 1)) if comune.editoriale(libro) else None
    if sk:
        righe.append(f'- Prossimo capitolo {ultimo + 1}: {taglia(sk.get("funzione"), 90)}; '
                     f'cambiamento: {taglia(sk.get("cambiamento"), 70)}.')
    else:
        righe.append('- Prossimo capitolo: nessuna scheda (stesura finita o percorso breve).')
    righe.append(f'- Prossimo passo: {taglia(fase.prossimo(stato), 160)}')
    righe.append(f'- Leggi anche: la riga «Letto» di zb avvio e, per scrivere, zb prepara <libro> {ultimo + 1}.')
    righe = righe[:MASSIMO]
    comune.scrivi(cartella, 'stato-compatto.md', '\n'.join(righe) + '\n')
    return len(righe)


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: compatto.py <libro>')
    cartella, libro, _ = comune.carica_libro(args[0])
    n = genera(cartella, libro)
    print(f'Scritto stato-compatto.md ({n} righe).')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

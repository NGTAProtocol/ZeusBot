"""Preparazione di un capitolo per lo scrittore (comando «zb prepara <libro> <N>»).

Uso: python3 -B prepara.py <libro> <N>
Senza ragionamento del modello, raccoglie in <libro>/06-diagnostica/preparazione/NN.md ciò che lo
scrittore deve leggere, e nient'altro:
- la scheda del capitolo N da 03-struttura/05-scaletta.md; si ferma (codice 2) se mancano funzione,
  conflitto, cambiamento, informazione data, gancio, polarità emotiva o sottotesto dei dialoghi;
- i file del codex con i tag della scheda (@char, @loc), e gli avvisi per i tag senza scheda;
- il canone (fatti bloccati di stato.yaml);
- le capsule dei capitoli precedenti e il registro delle promesse; si ferma se manca la capsula N-1;
- le ultime righe del capitolo precedente (per la continuità del ritmo, al massimo 6 righe di prosa);
- il conteggio delle righe da leggere (per «zb consumo»).
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import capsula  # noqa: E402
import codex  # noqa: E402
import struttura  # noqa: E402


def righe(cartella, rel):
    p = os.path.join(cartella, rel)
    return len(open(p, encoding='utf-8').read().splitlines()) if os.path.isfile(p) else 0


def prepara(cartella, libro, n):
    if not comune.editoriale(libro):
        raise comune.ErroreMotore('zb prepara vale per i libri del percorso editoriale.')
    sk = struttura.schede(cartella).get(str(n))
    if not sk:
        raise comune.ErroreMotore(f'05-scaletta.md: nessuna scheda «Capitolo {n}».')
    manca = struttura.campi_mancanti(sk)
    if manca:
        raise comune.ErroreMotore(f'Scheda del capitolo {n} incompleta: {", ".join(manca)}. Si completa la struttura '
                                  '(con «zb riapprova» se è già approvata) prima di scrivere.')
    file_codex, ignoti = codex.filtra(cartella, struttura.tag_di(sk))
    if n > 1:
        p = capsula.problemi_capsula(cartella, libro, n - 1)
        if p:
            raise comune.ErroreMotore('Capsula del capitolo precedente non pronta: ' + '; '.join(p))
    capsule = [capsula.rel(i) for i in range(1, n) if os.path.isfile(os.path.join(cartella, capsula.rel(i)))]
    if capsule:
        capsula.registro(cartella, libro)
        capsule.append(f'{capsula.CARTELLA}/registro.md')
    stato = comune.leggi_yaml(os.path.join(cartella, 'stato.yaml'))
    coda = []
    prec = dict(comune.unita(cartella, libro)).get(str(n - 1))
    if prec:
        prosa = [r for _, r in comune.righe_prosa(open(prec, encoding='utf-8').read()) if r.strip()]
        coda = prosa[-6:]
    leggere = ['03-architettura/manuale-di-stile.md', f'{comune.STRUTTURA}/09-scelte-fisse.md'] + file_codex + capsule
    totale = sum(righe(cartella, r) for r in leggere) + len(sk) + len(coda)
    out = [f'# Preparazione del capitolo {n} — {libro["titolo"]}', '',
           'Generata da «zb prepara»: lo scrittore legge solo questo file e i file elencati.', '',
           f'## Scheda (03-struttura/05-scaletta.md, Capitolo {n}{" - " + sk["_titolo"] if sk.get("_titolo") else ""})', '']
    etichette = {c[0]: c[1] for c in struttura.CAMPI_SCHEDA}
    out += [f'- {etichette[k]}: {v}' for k, v in sk.items() if k in etichette]
    out += ['', '## Canone (fatti bloccati: non si cambiano)', '']
    out += [f'- {x}' for x in stato.get('fatti_bloccati') or []] or ['- nessuno']
    out += ['', '## File da leggere', ''] + [f'- {r}' for r in leggere]
    out += [f'- AVVISO {x}: nessuna scheda nel codex' for x in ignoti]
    if coda:
        out += ['', f'## Ultime righe del capitolo {n - 1}', ''] + coda
    out += ['', f'Righe da leggere in tutto: {totale}.']
    rel = f'06-diagnostica/preparazione/{n:02d}.md'
    comune.scrivi(cartella, rel, '\n'.join(out) + '\n')
    return rel, len(leggere), totale, ignoti


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2 or not args[1].isdigit():
        raise comune.ErroreMotore('Uso: prepara.py <libro> <N>')
    cartella, libro, _ = comune.carica_libro(args[0])
    rel, nfile, totale, ignoti = prepara(cartella, libro, int(args[1]))
    print(f'Preparazione: {rel} ({nfile} file da leggere, {totale} righe in tutto).')
    for x in ignoti:
        print(f'AVVISO {x}: nessuna scheda nel codex')
    print('Scheda completa. Prossimo: agente scrittore-voce sul capitolo, poi «zb esito <libro> N».')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

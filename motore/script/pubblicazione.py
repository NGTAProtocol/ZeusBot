"""Controllo finale prima della pubblicazione (comando «zb finale <libro>», 2026-10-27).

Un libro esce solo senza errori: rifà tutti i controlli oggettivi sul testo e sui file da caricare e li somma.
- aggiornati: il compilato è il manoscritto di oggi e il PDF è stato fatto da quel compilato;
- ortografia: Hunspell 0 parole sconosciute e LanguageTool 0 segnalazioni (entrambi eseguiti davvero);
- tipografia, continuità, riciclo (anche copia dei campioni di voce), verifica del PDF, conformità KDP: 0 KO;
- copertina: fatta su questo PDF dell'interno, senza controlli KO.
Un falso allarme di LanguageTool o della tipografia si accetta solo per iscritto, con il motivo, in
06-diagnostica/correzioni-accettate.yaml ({controllo: "languagetool:REGOLA" | "tipografia:…", dove: "file:riga",
motivo}). Report: 06-pubblicazione/controllo-finale.md. «zb pronto» in chiusura lo riesegue e chiude solo a 0 KO.
"""
import hashlib
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

REPORT = os.path.join('06-pubblicazione', 'controllo-finale.md')
IMPRONTA = os.path.join('05-output', 'impronta-pdf.yaml')  # scritta da impagina: sha256 del compilato usato


def sha_testo(t):
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


def aggiornati(cartella, libro):
    import compila
    nome = comune.nome_file(libro['titolo'])
    md = os.path.join(cartella, '05-output', f'{nome}-completo.md')
    if not os.path.isfile(md):
        return ['manca il compilato: zb compila']
    attuale = open(md, encoding='utf-8').read()
    out = []
    if compila.compila(cartella, libro, []) != attuale:
        out.append('il manoscritto è cambiato dopo zb compila: rifare zb compila e zb impagina')
    imp = os.path.join(cartella, IMPRONTA)
    if not os.path.isfile(os.path.join(cartella, '05-output', f'{nome}.pdf')):
        out.append('manca il PDF di stampa: zb impagina')
    elif not os.path.isfile(imp) or (comune.leggi_yaml(imp) or {}).get('completo_md_sha256') != sha_testo(attuale):
        out.append('il PDF non è stato fatto da questo compilato: rifare zb impagina')
    return out


def ortografia(cartella, libro, acc):
    import ortografia as o
    trovate, errore_h, lt, motivo_lt = o.controlla(cartella, libro)
    comune.scrivi(cartella, os.path.join('06-diagnostica', 'controllo-ortografico.md'),
                  o.report(libro, trovate, errore_h, lt, motivo_lt))
    out = [f'Hunspell non eseguito ({errore_h})'] if errore_h else []
    out += [f'parola sconosciuta «{w}» ({", ".join(dove[:3])}): correggerla o, se giusta, in nomi_propri.txt'
            for w, dove in trovate.items()]
    if lt is None:
        out.append(f'LanguageTool non eseguito ({motivo_lt})')
    else:
        out += [f'{u}:{r} {regola}: {msg} «{fr}»' for u, r, regola, msg, fr in lt
                if (f'languagetool:{regola}', f'{u}:{r}') not in acc]
    return out


def tipografia(cartella, libro):
    import tipografia as t
    trovati = t.controlla_libro(cartella, libro)
    comune.scrivi(cartella, os.path.join('06-diagnostica', 'tipografia.md'), t.report(libro, trovati))
    return [f'{d} {c}: {x}' for c, d, x in trovati]


def ko(risultati):
    return [f'{r.get("unita") or ""}{":" + str(r["riga"]) if r.get("riga") else ""} {r.get("controllo") or ""}: '
            f'{r.get("dettaglio") or ""}'.strip() for r in risultati if r['esito'] == 'KO']


def controlli(cartella, libro):
    """[(nome, [KO])] nell'ordine del report."""
    import continuita
    import conformita_kdp
    import copertina
    import kdp_verifica
    import riciclo
    import tipografia as t
    import verifica_pdf
    acc = t.accettate(cartella)
    out = [('aggiornati', aggiornati(cartella, libro)),
           ('ortografia', ortografia(cartella, libro, acc)),
           ('tipografia', tipografia(cartella, libro)),
           ('continuità', ko(continuita.controlla_libro(cartella, libro)[0])),
           ('riciclo e copia', ko(riciclo.controlla_libro(cartella, libro)))]
    pdf = copertina.pdf_interno(cartella, libro)
    out.append(('PDF', ko(verifica_pdf.verifica(cartella, libro, pdf)[1]) if os.path.isfile(pdf) else ['manca il PDF']))
    S, _ = conformita_kdp.controlla(cartella, libro, [])
    k = [f'sezione {n}: {"; ".join(s.ko)}' for n, s in S.items() if s.esito == 'KO']
    scaduta, msg = kdp_verifica.stato_verifica(comune.oggi([]))
    out.append(('conformità KDP', k + ([msg] if scaduta else [])))
    out.append(('copertina', copertina.coerente(cartella, libro)))
    return out


def report(libro, esiti):
    tot = sum(len(v) for _, v in esiti)
    r = [f'# Controllo finale — {libro["titolo"]}', '',
         f'**{"PRONTO PER LA PUBBLICAZIONE" if not tot else f"NON PUBBLICABILE: {tot} KO"}**', '',
         '| Controllo | KO |', '|---|---|'] + [f'| {n} | {len(v)} |' for n, v in esiti]
    for n, v in esiti:
        if v:
            r += ['', f'## {n}', ''] + [f'- {x}' for x in v[:40]]
            if len(v) > 40:
                r.append(f'- … altri {len(v) - 40} nel report del controllo')
    return '\n'.join(r) + '\n'


def esegui(cartella, libro):
    esiti = controlli(cartella, libro)
    comune.scrivi(cartella, REPORT, report(libro, esiti))
    return esiti


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: zb finale <libro>')
    cartella, libro, _ = comune.carica_libro(args[0])
    esiti = esegui(cartella, libro)
    for n, v in esiti:
        print(f'{"KO" if v else "OK"} {n}: {len(v)}' + (f' (es. {v[0]})' if v else ''))
    tot = sum(len(v) for _, v in esiti)
    print(f'Controllo finale: {"pronto per la pubblicazione" if not tot else f"{tot} KO"}; report in {REPORT}.')
    return 1 if tot else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

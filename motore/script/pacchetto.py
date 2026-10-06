"""Pacchetto di pubblicazione: struttura di <libro>/06-pubblicazione/ (proposta A.5, A.6, A.9, B.4).

Uso: python3 -B pacchetto.py <libro>
Crea, se mancano, i modelli compilati con i dati di libro.yaml: scheda-amazon.md,
quarta.md, brief-copertina.md, conferme-autore.yaml, promemoria-ai.md, checklist.md.
NON scrive testi commerciali: descrizione, quarta di copertina, parole chiave e categorie
li scrive Claude Code nella fase di pubblicazione del libro, e poi passano da
conformita_kdp.py. Un file già presente non viene mai sovrascritto.
"""
import os
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402

NOTA = ('<!-- Compilato dal motore con i dati di libro.yaml. Le parti vuote le scrive Claude Code '
        'nella fase di pubblicazione; poi passano da conformita_kdp.py. -->')


def modelli(libro, cartella):
    t, a = libro['titolo'], libro['autore']
    st = libro.get('sottotitolo') or ''
    serie = libro.get('serie') or {}
    k = comune.kdp()
    pagine = '—'
    pdf = os.path.join(cartella, '05-output', f'{comune.nome_file(t)}.pdf')
    if os.path.isfile(pdf):
        import pymupdf
        with pymupdf.open(pdf) as d:
            pagine = str(d.page_count)
    f = libro['formato']
    anno = libro['copyright'].get('anno', '{anno}')
    out = {}
    out['scheda-amazon.md'] = '\n'.join([
        f'# Scheda Amazon — {t}', '', NOTA, '',
        f'Titolo: {t}', f'Sottotitolo: {st}',
        f'Serie: {serie.get("nome", "")} | {serie.get("numero", "")}' if serie else 'Serie:',
        f'Autore: {a}', 'Editore:', '',
        '## Descrizione', '',
        f'<!-- Massimo {k["metadati"]["descrizione_max_caratteri"]} caratteri. Tag HTML ammessi: '
        f'{" ".join(k["metadati"]["html_ammesso_descrizione"]["tag"])}. Niente link, prezzi, recensioni, '
        'parole chiave, paragoni («per i fan di…»), spoiler. -->', '',
        '## Parole chiave', '',
        f'<!-- Al massimo {k["metadati"]["parole_chiave_max"]}, frasi di 2-3 parole. -->', ''] +
        [f'{i}.' for i in range(1, k['metadati']['parole_chiave_max'] + 1)] +
        ['', '## Categorie', '', f'<!-- Al massimo {k["metadati"]["categorie_max"]}. -->', ''] +
        [f'{i}.' for i in range(1, k['metadati']['categorie_max'] + 1)] + [''])
    out['quarta.md'] = '\n'.join([
        f'# Quarta di copertina — {t}', '', NOTA, '',
        '<!-- 120-180 parole: frase gancio, premessa, posta in gioco, domanda finale (08-pubblicazione r. 23). '
        'Citazioni solo da recensioni reali e autorizzate. -->', '',
        '## Testo', '', '', '## Biografia dell\'autore (2 righe)', '', ''])
    out['brief-copertina.md'] = '\n'.join([
        f'# Brief per la copertina — {t}', '', NOTA, '',
        '| Dato | Valore |', '|---|---|',
        f'| Titolo | {t} |', f'| Sottotitolo | {st or "—"} |', f'| Autore | {a} |',
        f'| Serie | {serie.get("nome", "—")} {serie.get("numero", "")} |',
        f'| Formato | {f["pagina_pollici"][0]} × {f["pagina_pollici"][1]} pollici |',
        f'| Carta | {f.get("carta", "—")} |', f'| Pagine del PDF | {pagine} |', '',
        '- Dimensioni del file: SEMPRE dal calcolatore o dal modello ufficiale KDP (dipendono da formato, pagine e carta).',
        f'- Bleed obbligatorio per il cartaceo ({k["cartaceo"]["bleed_pollici"]}").',
        '- Lasciare libero il riquadro del codice a barre sulla quarta, secondo il modello KDP: '
        'con l\'ISBN gratuito KDP il codice lo mette KDP.',
        '- Titolo, sottotitolo, autore e serie identici ai metadati; nessuna imitazione di copertine esistenti.', '',
        '## Concept (3 alternative)', '', '1.', '2.', '3.', ''])
    out['promemoria-ai.md'] = '\n'.join([f'# Dichiarazione AI — {t}', '', k['dichiarazione_ai']['promemoria'], ''])
    out['checklist.md'] = '\n'.join([
        f'# Checklist prima dell\'upload — {t}', '', '(08-pubblicazione rr. 40-49)', '',
        '- [ ] Tutte le passate di revisione completate',
        '- [ ] Nessun avviso di continuità aperto',
        '- [ ] Registro promesse: tutte ripagate',
        '- [ ] Sommario generato e verificato (verifica_pdf.py)',
        '- [ ] Pagine iniziali e finali complete',
        f'- [ ] Nome autore identico su copertina, frontespizio e scheda: «{a}»',
        '- [ ] Totale parole nel range previsto dal piano (conta.py)',
        '- [ ] Dichiarazione AI preparata (promemoria-ai.md)',
        '- [ ] Controllo di conformità KDP senza KO (conformita_kdp.py)',
        f'- [ ] © {anno} {a}: pagina di copyright presente', ''])
    return out


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: pacchetto.py <libro>')
    cartella, libro, _ = comune.carica_libro(args[0])
    for nome, testo in modelli(libro, cartella).items():
        rel = f'06-pubblicazione/{nome}'
        if os.path.exists(os.path.join(cartella, rel)):
            print(f'già presente, non toccato: {rel}')
            continue
        comune.scrivi(cartella, rel, testo)
        print(f'creato: {rel}')
    rel = '06-pubblicazione/conferme-autore.yaml'
    if os.path.exists(os.path.join(cartella, rel)):
        print(f'già presente, non toccato: {rel}')
    else:
        shutil.copyfile(os.path.join(comune.radice_motore(), 'modelli', 'conferme-autore.yaml'),
                        comune.percorso_in_libro(cartella, rel))
        print(f'creato: {rel}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

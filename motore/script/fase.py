"""Macchina a stati del libro (proposta C.1, adattata al processo del passo 5). Unico script che scrive stato.yaml.

Uso: python3 -B fase.py <libro> <comando> [argomenti]

Comandi dell'autore:
  stato                    mostra lo stato; non scrive nulla
  avanti                   mostra il blocco successivo dei documenti del gate aperto
  ok [lotti da N]          approva il gate aperto (solo dopo aver mostrato tutti i blocchi)
  correggi <istruzione>    registra una correzione; il gate resta aperto
  riapprova <documento> <motivo>   registra una modifica autorizzata a un documento già approvato
                           (nuovo sha256 e commit, con data, motivo e sha256 precedente)
Comandi di Claude Code:
  pronto                   il lavoro della fase è finito: apre il gate (se previsto in libro.yaml) o passa oltre
  esito <N>                esegue capitolo.py sull'unità N e registra l'esito (OK, KO, secondo KO = fermata);
                           a un gate «primi_capitoli» o «lotto» con una correzione registrata, rifà i controlli
                           di un capitolo del gate e aggiorna le parole; il gate resta aperto

Fasi: documenti → pagina_campione → stesura → chiusura → chiuso.
Gate (libro.yaml, campo «gate»; predefiniti documenti, pagina_campione, primi_capitoli):
documenti, pagina_campione, primi_capitoli, lotto; più controllo_fallito, sempre attivo
(stesso controllo fallito due volte di fila sullo stesso capitolo).
Scrive solo <libro>/stato.yaml e <libro>/LEGGIMI.md (e il report di capitolo.py). Nessun commit:
il salvataggio lo fa Claude Code secondo il blocco di salvataggio.
"""
import datetime
import os
import re
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import conta  # noqa: E402
import revisione  # noqa: E402

FASI = ['documenti', 'pagina_campione', 'stesura', 'chiusura', 'chiuso']
GATE_PREDEFINITI = ['documenti', 'pagina_campione', 'primi_capitoli']
CHIUSURA = [('06-diagnostica/continuita.md', 'zb continuita'),
            ('06-diagnostica/controllo-ortografico.md', 'zb ortografia'),
            ('05-output/{nome}-completo.md', 'zb compila'),
            ('05-output/{nome}.pdf', 'zb impagina'),
            ('06-diagnostica/verifica-pdf.md', 'zb pdf'),
            ('06-pubblicazione/checklist.md', 'zb pacchetto'),
            ('06-pubblicazione/conformita-kdp.md', 'zb kdp')]
PAGINA_DA_SCRIVERE = ('# Pagina campione\n\n<!-- Da scrivere secondo 03-architettura/manuale-di-stile.md; '
                      'poi «zb pronto <libro>». -->\n')
SALVA = 'Salva: git add, commit, push, git status -sb, git log -1.'


# ---------------------------------------------------------------- stato

def carica_stato(cartella):
    p = os.path.join(cartella, 'stato.yaml')
    if not os.path.isfile(p):
        raise comune.ErroreMotore(f'stato.yaml mancante in {cartella}')
    stato = comune.leggi_yaml(p)
    errori = comune.valida(stato, comune.carica_schema('stato'), 'stato.yaml')
    if not errori and stato['fase'] not in FASI:
        errori.append(f'stato.yaml.fase: «{stato["fase"]}» non è una fase ({", ".join(FASI)})')
    if errori:
        raise comune.ErroreMotore('stato.yaml non valido:\n- ' + '\n- '.join(errori))
    stato.setdefault('tentativi', {})
    stato.setdefault('correzioni_aperte', [])
    stato.setdefault('ultimo_capitolo_scritto', None)
    return stato


def salva_stato(cartella, stato):
    stato['aggiornato'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    comune.scrivi(cartella, 'stato.yaml', yaml.safe_dump(stato, sort_keys=False, allow_unicode=True, width=120))
    p = os.path.join(cartella, 'LEGGIMI.md')
    if os.path.isfile(p):
        t = open(p, encoding='utf-8').read()
        t = re.sub(r'(?m)^Fase: .*$', f'Fase: {stato["fase"]}; gate in attesa: {stato["gate_in_attesa"] or "nessuno"}', t)
        t = re.sub(r'(?m)^Ultimo capitolo approvato: .*$',
                   f'Ultimo capitolo approvato: {stato["ultimo_capitolo_approvato"] or "—"}', t)
        comune.scrivi(cartella, 'LEGGIMI.md', t)


def gate_attivi(libro):
    return libro['gate'] if libro.get('gate') is not None else GATE_PREDEFINITI


def capitoli_previsti(cartella):
    p = os.path.join(cartella, '03-architettura', 'piano-parole.md')
    if not os.path.isfile(p):
        return 0
    return len(set(re.findall(r'(?m)^\|[^|\n]*\|\s*(\d+)\s*\|', open(p, encoding='utf-8').read())))


def parole_scritte(cartella, libro):
    return sum(conta.conta_testo(open(p, encoding='utf-8').read()) for _, p in comune.unita(cartella, libro))


def prossimo(stato):
    g, f = stato['gate_in_attesa'], stato['fase']
    if g:
        return f'Gate «{g}» aperto: avanti, ok, correggi: … oppure stato.'
    return {'documenti': 'Completa bibbia, cronologia, scaletta e piano parole; poi «zb pronto <libro>».',
            'pagina_campione': 'Scrivi 05-revisioni/pagina-campione.md secondo il manuale; poi «zb pronto <libro>».',
            'stesura': f'Prossimo: {stato["passo"]}. Rileggi manuale e direttive, scrivi, poi «zb esito <libro> N».',
            'chiusura': 'Esegui ' + ', '.join(c for _, c in CHIUSURA) + '; poi «zb pronto <libro>».',
            'chiuso': 'Libro chiuso.'}[f]


# ---------------------------------------------------------------- revisione e approvazione

def apri_gate(cartella, libro, stato, gate, passo=None):
    stato['gate_in_attesa'] = gate
    stato['revisione_in_corso'] = None
    if passo:
        stato['passo'] = passo
    print(f'Gate «{gate}» aperto. Mostro i documenti in blocchi.')
    avanti(cartella, libro, stato)


def avanti(cartella, libro, stato):
    gate = stato['gate_in_attesa']
    if not gate:
        raise comune.ErroreMotore('Nessun gate aperto: «avanti» non ha niente da mostrare. ' + prossimo(stato))
    docs = revisione.documenti_del_gate(cartella, libro, stato, gate)
    b = revisione.blocchi(cartella, docs)
    imp = revisione.impronta(cartella, docs)
    rc = stato.get('revisione_in_corso')
    if rc and rc.get('gate') == gate and rc.get('sha256') == imp:
        n = rc['blocco'] + 1
        if n > len(b):
            print('Fine dei documenti. Scrivi ok o correggi: …')
            return
    else:
        if rc and rc.get('gate') == gate:
            print('Documenti cambiati dall\'ultima lettura: la revisione riparte dal blocco 1.')
        n = 1
    print(revisione.mostra(libro['titolo'], b, n))
    stato['revisione_in_corso'] = {'gate': gate, 'blocco': n, 'blocchi_totali': len(b), 'sha256': imp}
    if n == len(b):
        print('Fine dei documenti. Scrivi ok o correggi: …')


def registra(cartella, stato, documenti, senza_gate=False):
    """Registra sha256 e commit dei documenti approvati; rifiuta documenti non salvati."""
    codice, out, err = comune.git(cartella, 'status', '--porcelain', '--', *documenti)
    if codice != 0:
        raise comune.ErroreMotore(f'git status non riuscito: {err}')
    if out:
        raise comune.ErroreMotore('Documenti con modifiche non salvate:\n' + out +
                                  '\nSalva prima (git add, commit, push), poi ripeti.')
    for rel in documenti:
        commit = comune.ultimo_commit(cartella, rel)
        if not commit:
            raise comune.ErroreMotore(f'{rel} non è mai stato salvato in un commit')
        voce = {'sha256': comune.sha256_file(os.path.join(cartella, rel)), 'commit': commit}
        if senza_gate:
            voce['senza_gate'] = True
        stato['documenti_approvati'][rel] = voce


def chiudi_fase(cartella, libro, stato):
    """Dopo l'approvazione dei documenti o della pagina campione: fase successiva."""
    if stato['fase'] == 'documenti':
        stato.update(fase='pagina_campione', passo='da completare', gate_in_attesa=None)
        if not os.path.isfile(os.path.join(cartella, revisione.PAGINA_CAMPIONE)):
            comune.scrivi(cartella, revisione.PAGINA_CAMPIONE, PAGINA_DA_SCRIVERE)
            print(f'Creato {revisione.PAGINA_CAMPIONE}, da scrivere secondo il manuale.')
    elif stato['fase'] == 'pagina_campione':
        stato.update(fase='stesura', passo='capitolo 1', gate_in_attesa=None)
    stato['revisione_in_corso'] = None


def dopo_capitolo(cartella, libro, stato):
    """Gate e fasi dopo un capitolo accettato."""
    gate = gate_attivi(libro)
    totale = capitoli_previsti(cartella)
    scritto = stato['ultimo_capitolo_scritto'] or 0
    numerici = [int(c) for c in stato['lotto']['capitoli'] if str(c).isdigit()]
    if 'primi_capitoli' in gate and stato['ultimo_capitolo_approvato'] is None and scritto >= min(3, totale or 3):
        apri_gate(cartella, libro, stato, 'primi_capitoli')
        return
    if numerici and (len(numerici) >= stato['lotto']['dimensione'] or (totale and scritto >= totale)):
        if 'lotto' in gate:
            apri_gate(cartella, libro, stato, 'lotto')
            return
        print(f'Lotto completato ({", ".join(map(str, stato["lotto"]["capitoli"]))}): nessuna fermata '
              '(gate «lotto» non attivo in libro.yaml).')
        stato['lotto']['capitoli'] = []
    if totale and scritto >= totale:
        stato.update(fase='chiusura', passo='controlli finali', gate_in_attesa=None)
        print(f'Tutti i {totale} capitoli sono scritti: fase «chiusura».')


# ---------------------------------------------------------------- comandi

def cmd_stato(cartella, libro, stato):
    rc = stato.get('revisione_in_corso')
    codice, sub, _ = comune.git(cartella, 'log', '-1', '--format=%h «%s»')
    c2, conti, _ = comune.git(cartella, 'rev-list', '--left-right', '--count', 'HEAD...@{u}')
    if c2 == 0 and conti.split() == ['0', '0']:
        allineato = 'sì'
    elif c2 == 0:
        a, d = conti.split()
        allineato = f'no (avanti {a}, indietro {d})'
    else:
        allineato = 'nessun ramo remoto collegato'
    righe = [f'Libro: {libro["titolo"]} ({cartella}); modalità {libro.get("modalita", "nuovo")}',
             f'Fase: {stato["fase"]}; passo: {stato["passo"] or "—"}; gate in attesa: {stato["gate_in_attesa"] or "nessuno"}',
             f'Gate attivi (libro.yaml): {", ".join(gate_attivi(libro))}',
             f'Lotto: dimensione {stato["lotto"]["dimensione"]}, capitoli {stato["lotto"]["capitoli"] or "—"}',
             f'Capitoli: scritti fino a {stato["ultimo_capitolo_scritto"] or "—"}, approvati fino a '
             f'{stato["ultimo_capitolo_approvato"] or "—"}, previsti {capitoli_previsti(cartella) or "—"}',
             f'Parole: {stato["parole"]["scritte"]}/{stato["parole"]["obiettivo"]} (metodo unico)',
             'Revisione: ' + (f'blocco {rc["blocco"]} di {rc["blocchi_totali"]} (gate {rc["gate"]})' if rc else 'nessuna'),
             f'Correzioni aperte: {len(stato["correzioni_aperte"])}']
    righe += [f'  - [{c["gate"]}] {c["testo"]}' for c in stato['correzioni_aperte']]
    righe += [f'Controlli falliti di fila: {stato["tentativi"] or "nessuno"}',
              f'Avvisi aperti: {len(stato["avvisi_aperti"])}',
              f'Documenti approvati: {len(stato["documenti_approvati"])}',
              f'Ramo: {comune.ramo(cartella) or "—"}; ultimo commit: {sub if codice == 0 else "—"}; '
              f'allineato a origin: {allineato}',
              prossimo(stato)]
    print('\n'.join(righe))


def cmd_pronto(cartella, libro, stato):
    if stato['gate_in_attesa']:
        raise comune.ErroreMotore(f'Gate «{stato["gate_in_attesa"]}» già aperto: avanti, ok o correggi.')
    fase = stato['fase']
    if fase in ('documenti', 'pagina_campione'):
        docs = revisione.documenti_del_gate(cartella, libro, stato, fase)
        manca = [d for d in docs if not os.path.isfile(os.path.join(cartella, d))]
        if manca:
            raise comune.ErroreMotore('Documenti mancanti: ' + ', '.join(manca))
        pc = os.path.join(cartella, revisione.PAGINA_CAMPIONE)
        if fase == 'pagina_campione' and not conta.conta_testo(open(pc, encoding='utf-8').read()):
            raise comune.ErroreMotore(f'{revisione.PAGINA_CAMPIONE} è ancora vuota: scrivila, poi «zb pronto <libro>».')
        if fase in gate_attivi(libro):
            apri_gate(cartella, libro, stato, fase, passo='in revisione')
        else:
            registra(cartella, stato, docs, senza_gate=True)
            chiudi_fase(cartella, libro, stato)
            print(f'Gate «{fase}» non previsto in libro.yaml: documenti registrati senza fermata; fase «{stato["fase"]}».')
    elif fase == 'chiusura':
        nome = comune.nome_file(libro['titolo'])
        manca = [f'{p.format(nome=nome)} ({c})' for p, c in CHIUSURA
                 if not os.path.isfile(os.path.join(cartella, p.format(nome=nome)))]
        if manca:
            raise comune.ErroreMotore('Chiusura incompleta. Mancano:\n- ' + '\n- '.join(manca))
        stato.update(fase='chiuso', passo=None)
        print('Chiusura completa: libro chiuso.')
    else:
        raise comune.ErroreMotore(f'«pronto» non vale in fase «{fase}». ' + prossimo(stato))


def cmd_ok(cartella, libro, stato, resto):
    gate = stato['gate_in_attesa']
    if not gate:
        raise comune.ErroreMotore('Nessun gate aperto: niente da approvare. ' + prossimo(stato))
    docs = revisione.documenti_del_gate(cartella, libro, stato, gate)
    imp = revisione.impronta(cartella, docs)
    rc = stato.get('revisione_in_corso')
    if not rc or rc.get('gate') != gate or rc.get('sha256') != imp:
        raise comune.ErroreMotore('«ok» vale solo per documenti mostrati per intero: i documenti del gate '
                                  'non sono stati mostrati o sono cambiati. Scrivi avanti.')
    if rc['blocco'] < rc['blocchi_totali']:
        raise comune.ErroreMotore(f'Mancano i blocchi {rc["blocco"] + 1}-{rc["blocchi_totali"]} di '
                                  f'{rc["blocchi_totali"]}: prima li mostro. Scrivi avanti.')
    pendenti = [c for c in stato['correzioni_aperte'] if c['gate'] == gate and c['sha256'] == imp]
    if pendenti:
        raise comune.ErroreMotore('Correzione registrata ma non ancora applicata (documenti invariati): '
                                  + '; '.join(c['testo'] for c in pendenti))
    m = re.search(r'lott\w*\s+da\s+(\d+)', ' '.join(resto))
    registra(cartella, stato, docs)
    stato['correzioni_aperte'] = [c for c in stato['correzioni_aperte'] if c['gate'] != gate]
    if m:
        stato['lotto']['dimensione'] = int(m.group(1))
        print(f'Lotti successivi: {m.group(1)} capitoli.')
    stato['revisione_in_corso'] = None
    stato['gate_in_attesa'] = None
    print(f'Gate «{gate}» approvato: {len(docs)} documenti registrati con sha256 e commit.')
    if gate in ('documenti', 'pagina_campione'):
        chiudi_fase(cartella, libro, stato)
    elif gate in ('primi_capitoli', 'lotto'):
        numerici = [int(c) for c in stato['lotto']['capitoli'] if str(c).isdigit()]
        stato['ultimo_capitolo_approvato'] = max(numerici + [stato['ultimo_capitolo_approvato'] or 0])
        stato['lotto']['capitoli'] = []
        dopo_capitolo(cartella, libro, stato)
    elif gate == 'controllo_fallito':
        n = str(stato['passo']).replace('capitolo ', '')
        stato['tentativi'].pop(n, None)
        print(f'Capitolo {n} accettato così com\'è, per decisione dell\'autore.')
        accetta_capitolo(cartella, libro, stato, n)


def cmd_correggi(cartella, libro, stato, resto):
    gate = stato['gate_in_attesa']
    if not gate:
        raise comune.ErroreMotore('Nessun gate aperto: «correggi» vale solo a un gate. ' + prossimo(stato))
    testo = ' '.join(resto).strip().lstrip(':').strip()
    if not testo:
        raise comune.ErroreMotore('Uso: correggi <istruzione>')
    docs = revisione.documenti_del_gate(cartella, libro, stato, gate)
    stato['correzioni_aperte'].append({'gate': gate, 'testo': testo, 'sha256': revisione.impronta(cartella, docs),
                                       'data': datetime.date.today().isoformat()})
    print(f'Correzione registrata al gate «{gate}»: {testo}\n'
          'Applico solo questa, rieseguo i controlli e mostro le righe cambiate (prima e dopo). '
          'Il gate resta aperto; dopo la correzione «avanti» riparte dal blocco 1.')


def cmd_riapprova(cartella, stato, resto):
    if len(resto) < 2:
        raise comune.ErroreMotore('Uso: riapprova <documento> <motivo>')
    rel, motivo = resto[0], ' '.join(resto[1:]).strip()
    prima = stato['documenti_approvati'].get(rel)
    if not prima:
        raise comune.ErroreMotore(f'«{rel}» non è tra i documenti approvati: ' + ', '.join(stato['documenti_approvati']))
    if comune.sha256_file(os.path.join(cartella, rel)) == prima['sha256']:
        raise comune.ErroreMotore(f'{rel} non è cambiato dall\'approvazione: niente da registrare.')
    registra(cartella, stato, [rel])
    voce = stato['documenti_approvati'][rel]
    voce.update({k: v for k, v in prima.items() if k not in ('sha256', 'commit', 'riapprovazioni')})
    voce['riapprovazioni'] = (prima.get('riapprovazioni') or []) + [
        {'data': datetime.date.today().isoformat(), 'motivo': motivo, 'sha256_precedente': prima['sha256'],
         'commit_precedente': prima['commit']}]
    print(f'Modifica autorizzata registrata: {rel} (commit {voce["commit"]}); motivo: {motivo}.')


def accetta_capitolo(cartella, libro, stato, n):
    if n.isdigit():
        stato['ultimo_capitolo_scritto'] = max(int(n), stato['ultimo_capitolo_scritto'] or 0)
        stato['passo'] = f'capitolo {int(n) + 1}'
    if n not in [str(c) for c in stato['lotto']['capitoli']]:
        stato['lotto']['capitoli'].append(int(n) if n.isdigit() else n)
    stato['parole']['scritte'] = parole_scritte(cartella, libro)
    if stato['gate_in_attesa'] == 'controllo_fallito':
        stato['gate_in_attesa'] = None
        stato['revisione_in_corso'] = None
    dopo_capitolo(cartella, libro, stato)


def cmd_esito(cartella, libro, stato, resto, argv):
    if not resto:
        raise comune.ErroreMotore('Uso: esito <N>')
    n = ' '.join(resto)
    n = str(int(n)) if n.isdigit() else n
    gate = stato['gate_in_attesa']
    if stato['fase'] != 'stesura':
        raise comune.ErroreMotore(f'«esito» vale solo in fase «stesura» (ora: {stato["fase"]}).')
    correzione = (gate in ('primi_capitoli', 'lotto') and n in [str(c) for c in stato['lotto']['capitoli']]
                  and any(c['gate'] == gate for c in stato['correzioni_aperte']))
    if gate and not correzione and not (gate == 'controllo_fallito' and str(stato['passo']) == f'capitolo {n}'):
        raise comune.ErroreMotore(f'Gate «{gate}» aperto: prima ok o correggi.')
    extra = ['--radice', argv[argv.index('--radice') + 1]] if '--radice' in argv else []
    r = subprocess.run([sys.executable, '-B', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capitolo.py'),
                        cartella, *n.split(), *extra], capture_output=True, text=True)
    if r.returncode not in (0, 1):
        raise comune.ErroreMotore(f'capitolo.py {n} non eseguito: {r.stderr.strip() or r.stdout.strip()}')
    if correzione:
        stato['parole']['scritte'] = parole_scritte(cartella, libro)
        print(f'Capitolo {n} corretto al gate «{gate}»: controlli {"OK" if r.returncode == 0 else "KO"}; '
              f'parole del libro aggiornate ({stato["parole"]["scritte"]}). Il gate resta aperto: '
              '«avanti» riparte dal blocco 1.')
        return r.returncode
    if r.returncode == 0:
        stato['tentativi'].pop(n, None)
        print(f'Capitolo {n}: controlli OK.')
        accetta_capitolo(cartella, libro, stato, n)
        return 0
    stato['tentativi'][n] = stato['tentativi'].get(n, 0) + 1
    rep = f'06-diagnostica/capitoli/{revisione.nome_report(n)}.md'
    if stato['tentativi'][n] >= 2:
        print(f'FERMO: capitolo {n}, controlli falliti per la seconda volta di fila. Report: {rep}.\n'
              'Scrivo quale controllo, valore, soglia, file e righe; decide l\'autore (ok = accetta, correggi: …).')
        apri_gate(cartella, libro, stato, 'controllo_fallito', passo=f'capitolo {n}')
    else:
        print(f'Capitolo {n}: controlli KO (primo tentativo). Report: {rep}.\n'
              'Una sola correzione mirata sul punto indicato, poi «zb esito <libro> N» di nuovo.')
    return 1


def main(argv):
    args = [a for i, a in enumerate(argv) if a != '--radice' and (i == 0 or argv[i - 1] != '--radice')]
    if len(args) < 2:
        raise comune.ErroreMotore('Uso: fase.py <libro> stato|avanti|ok|correggi|riapprova|pronto|esito [argomenti]')
    cartella, libro, _ = comune.carica_libro(args[0])
    comando, resto = args[1], args[2:]
    stato = carica_stato(cartella)
    if comando == 'stato':
        cmd_stato(cartella, libro, stato)
        return 0
    codice = 0
    if comando == 'avanti':
        avanti(cartella, libro, stato)
    elif comando == 'ok':
        cmd_ok(cartella, libro, stato, resto)
    elif comando == 'correggi':
        cmd_correggi(cartella, libro, stato, resto)
    elif comando == 'pronto':
        cmd_pronto(cartella, libro, stato)
    elif comando == 'riapprova':
        cmd_riapprova(cartella, stato, resto)
    elif comando == 'esito':
        codice = cmd_esito(cartella, libro, stato, resto, argv)
    else:
        raise comune.ErroreMotore(f'Comando sconosciuto: {comando}. Comandi: stato, avanti, ok, correggi, riapprova, pronto, esito.')
    salva_stato(cartella, stato)
    print(f'Fase: {stato["fase"]}; gate in attesa: {stato["gate_in_attesa"] or "nessuno"}. {prossimo(stato)}')
    print(SALVA)
    return codice


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

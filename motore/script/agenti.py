"""Subagenti e comandi di Claude Code per i rami dei libri (comando «zb agenti»).

Uso: python3 -B agenti.py stato | attiva [--ok] | disattiva [--progetto <radice>]
Fonte unica: motore/editoriale/agenti/*.md (più motore/editoriale/lingue/agenti/*.md, traduzione) e
motore/editoriale/comandi/*.md. «attiva» li copia in <radice>/.claude/agents/ e <radice>/.claude/commands/,
scrivendo negli agenti il campo «model:» preso da motore/dati/modelli-ruoli.yaml (unica fonte dei modelli).
- Solo sui rami dei libri: rifiutato sul ramo «motore» e con il lavoro sul motore in corso
  (sul ramo del motore agenti e comandi restano spenti; la prova lo controlla).
- Senza --ok mostra cosa scriverebbe: l'«ok» lo dà l'autore.
- Non sovrascrive file che non ha scritto lui; «disattiva» toglie solo i propri (riga di firma).
Formato verificato sulla documentazione ufficiale (2026-10-15): agenti con frontmatter name e description
obbligatori, tools e model facoltativi; comandi in .claude/commands/<nome>.md (formato ancora supportato; le
skill in .claude/skills/ sono il formato raccomandato per i comandi nuovi), argomenti con $ARGUMENTS.
"""
import os
import re
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import hook_recinto  # noqa: E402

FIRMA = '<!-- zb: installato da «zb agenti attiva»; fonte: motore/editoriale/ -->'


def sorgenti(motore):
    e = os.path.join(motore, 'editoriale')
    out = []
    for sub, dest in (('agenti', 'agents'), (os.path.join('lingue', 'agenti'), 'agents'), ('comandi', 'commands')):
        d = os.path.join(e, sub)
        if os.path.isdir(d):
            out += [(os.path.join(d, f), dest, f) for f in sorted(os.listdir(d)) if f.endswith('.md')]
    return out


def modelli(motore):
    d = comune.leggi_yaml(os.path.join(motore, 'dati', 'modelli-ruoli.yaml'))
    return {r: d['livelli'][liv] for r, liv in d['ruoli'].items()}, d.get('parallelo_massimo', 3)


def generato(src, dest, mod):
    t = open(src, encoding='utf-8').read()
    if dest == 'agents':
        m = re.match(r'^---\n(.*?)\n---\n', t, re.S)
        if not m:
            raise comune.ErroreMotore(f'{src}: frontmatter mancante')
        fm = yaml.safe_load(m.group(1))
        for k in ('name', 'description'):
            if not fm.get(k):
                raise comune.ErroreMotore(f'{src}: campo obbligatorio «{k}» mancante nel frontmatter')
        nome = fm['name']
        if nome in mod:     # unica fonte dei modelli: dati/modelli-ruoli.yaml (sostituisce un «model:» del file)
            corpo = re.sub(r'(?m)^model:.*\n?', '', m.group(1)).rstrip('\n')
            t = t.replace(m.group(0), f'---\n{corpo}\nmodel: {mod[nome]}\n---\n', 1)
    return t.rstrip('\n') + '\n\n' + FIRMA + '\n'


def piano(rad, motore):
    mod, _ = modelli(motore)
    return [(os.path.join(rad, '.claude', dest, f), generato(src, dest, mod)) for src, dest, f in sorgenti(motore)]


def nostro(p):
    return os.path.isfile(p) and FIRMA in open(p, encoding='utf-8').read()


def main(argv):
    motore = comune.radice_motore()
    rad = os.path.realpath(argv[argv.index('--progetto') + 1]) if '--progetto' in argv else comune.radice_git(motore)
    pulito = [a for i, a in enumerate(argv) if a != '--progetto' and (i == 0 or argv[i - 1] != '--progetto')]
    args = comune.argomenti(pulito)
    azione = args[0] if args else 'stato'
    voci = piano(rad, motore)
    installati = [p for p, _ in voci if nostro(p)]
    if azione == 'stato':
        _, par = modelli(motore)
        print(f'Agenti e comandi installati: {len(installati)} di {len(voci)} in {os.path.join(rad, ".claude")}; '
              f'parallelo massimo {par}.')
        return 0
    ramo = subprocess.run(['git', '-C', rad, 'branch', '--show-current'], capture_output=True, text=True).stdout.strip()
    if azione == 'attiva':
        if ramo == 'motore' or hook_recinto.lavoro(rad) == 'motore':
            raise comune.ErroreMotore('Agenti e comandi si attivano solo sui rami dei libri: sul ramo del motore '
                                      '(o con il lavoro sul motore in corso) restano spenti.')
        estranei = [p for p, _ in voci if os.path.exists(p) and not nostro(p)]
        if estranei:
            raise comune.ErroreMotore('File già presenti e non del motore (non li sovrascrivo):\n- ' + '\n- '.join(estranei))
        if '--ok' not in argv:
            print(f'Creerei {len(voci)} file in {os.path.join(rad, ".claude")} (agents/ e commands/), con i modelli di '
                  'motore/dati/modelli-ruoli.yaml. Valgono per ogni sessione su questo ramo.\n'
                  'Dopo l\'«ok» dell\'autore: zb agenti attiva --ok')
            return 0
        for p, testo in voci:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w', encoding='utf-8') as f:
                f.write(testo)
        print(f'Installati {len(voci)} file in .claude/agents/ e .claude/commands/. Salvali con un commit (zb salva).')
        return 0
    if azione == 'disattiva':
        for p in installati:
            os.remove(p)
        for d in ('agents', 'commands'):
            try:
                os.rmdir(os.path.join(rad, '.claude', d))
            except OSError:
                pass
        print(f'Tolti {len(installati)} file del motore da .claude/. Salva la rimozione con un commit.')
        return 0
    raise comune.ErroreMotore('Uso: agenti stato | attiva [--ok] | disattiva')


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

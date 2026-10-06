"""Hook SessionStart di Claude Code (proposta C.4). Non blocca mai: esce sempre con 0.

Legge da stdin il JSON dell'hook ({session_id, source, …}) e scrive
$CLAUDE_PROJECT_DIR/.zb/sessione-corrente con il session_id (la cartella .zb/ ignora sé stessa).
Con source «compact» (contesto compattato) registra l'ora in .zb/compattato-<session_id>:
da quel momento i marker di avvio precedenti non valgono più e bisogna rieseguire «zb avvio <libro>».
Si attiva solo con «zb hook attiva» (configurazione in motore/dati/hook-settings.esempio.json).
"""
import json
import os
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        dati = json.loads(sys.stdin.read() or '{}')
        sid = str(dati.get('session_id') or '').strip()
        if not sid or '/' in sid:
            return 0
        import comune
        d = comune.prepara_zb(os.environ.get('CLAUDE_PROJECT_DIR') or dati.get('cwd') or os.getcwd())
        with open(os.path.join(d, 'sessione-corrente'), 'w', encoding='utf-8') as f:
            f.write(sid + '\n')
        if dati.get('source') == 'compact':
            with open(os.path.join(d, f'compattato-{sid}'), 'w', encoding='utf-8') as f:
                f.write(f'{time.time()}\n')
            print('Contesto compattato: prima di scrivere nel manoscritto riesegui «zb avvio <libro>».')
    except Exception as e:  # l'hook di sessione non deve mai fermare la sessione
        print(f'hook_sessione: errore ignorato ({e})', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""Ruoli del percorso editoriale: chi può lavorare in quale fase, e la prima riga del suo rapporto.

Uso: python3 -B ruolo.py <libro> <ruolo> [N]     (comando «zb ruolo»; non scrive nulla)
Si ferma (codice 2) se il ruolo non lavora nella fase attuale del libro: è il controllo meccanico di
«la scrittura non include revisione» (line-editor solo in fase «line», correttore-italiano solo in «copy»…).
Per i ruoli di revisione stampa il percorso del rapporto e la prima riga da copiare:
«<!-- zb: ruolo=<ruolo>; su=<impronta> -->», con l'impronta del testo rivisto (struttura, capitolo N o
manoscritto). «zb pronto» rifiuta un rapporto con un'impronta diversa da quella del testo attuale.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import percorso  # noqa: E402


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2:
        raise comune.ErroreMotore('Uso: ruolo.py <libro> <ruolo> [N]. Ruoli: ' + ', '.join(percorso.FASI_RUOLO))
    cartella, libro, _ = comune.carica_libro(args[0])
    ruolo, n = args[1], (args[2] if len(args) > 2 else None)
    if not percorso.attivo(libro):
        raise comune.ErroreMotore('Il libro non segue il percorso editoriale (manca «percorso: editoriale» in libro.yaml).')
    if ruolo not in percorso.FASI_RUOLO:
        raise comune.ErroreMotore(f'Ruolo sconosciuto «{ruolo}». Ruoli: ' + ', '.join(percorso.FASI_RUOLO))
    stato = comune.leggi_yaml(os.path.join(cartella, 'stato.yaml'))
    fs = stato['fase']
    if fs not in percorso.FASI_RUOLO[ruolo]:
        raise comune.ErroreMotore(f'Il ruolo «{ruolo}» non lavora in fase «{fs}» (solo in: '
                                  f'{", ".join(percorso.FASI_RUOLO[ruolo])}). Chi scrive non rivede: ogni revisione '
                                  'ha la sua fase, dopo la stesura.')
    if stato.get('sottofase') == 'applicazione':
        print(f'Fase «{fs}», applicazione: il ruolo «{ruolo}» applica solo le proposte approvate (modifiche puntuali).')
        return 0
    attesi = [r for r in percorso.rapporti(cartella, libro, fs)
              if r[1] == ruolo] if fs in ('struttura', *percorso.REVISIONI) else []
    if fs in ('line', 'copy'):
        if not n:
            raise comune.ErroreMotore(f'Uso: ruolo <libro> {ruolo} <N> (un capitolo alla volta)')
        attesi = [r for r in attesi if r[0].endswith(f'/{percorso.nn(n)}.md')]
        if not attesi:
            raise comune.ErroreMotore(f'Capitolo «{n}» assente in 04-manoscritto')
    if not attesi:
        print(f'Ruolo «{ruolo}» ammesso in fase «{fs}». Nessun rapporto da intestare.')
        return 0
    for rel, _, testi in attesi:
        print(f'Rapporto: {rel}')
        print(f'Prima riga: <!-- zb: ruolo={ruolo}; su={percorso.impronta(cartella, testi)} -->')
        print(f'Testo rivisto: {len(testi)} file ({", ".join(testi[:3])}{"…" if len(testi) > 3 else ""})')
    print('Salva il rapporto in un commit che non tocca il testo rivisto.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)

# Da fornire (autore)

## 1. File di riferimento del livello editoriale
- Né `editoriale_tutto.md` né `editoriale.zip` sono nel repository (cercati in `motore/`, `docs/`, radice
  e in tutti i rami di origin, 2026-10-15).
- Il motore ha 28 file in `motore/editoriale/`: 14 c'erano già (commit e258631), 14 li ho scritti da
  zero in questa sessione perché il resto del lavoro ne dipende: `diagnosi/` (4), `ruoli/00-diagnosta.md`,
  `agenti/` (9), `risparmio-token.md`. I file su diagnosi sono scritti dalla pratica editoriale comune,
  senza aprire né usare testo di terzi con licenza non commerciale.
- Quando fornisci il file: va ricreato sotto `motore/editoriale/` con contenuto esatto; la tua versione
  diventa la base e si integra solo ciò che manca dalla mia (regola 2.2).

## 2. Corpus per il vocabolario anti-IA italiano
- Il catalogo italiano ha i livelli L1-L3 vuoti (regola 6.2). Per riempirli servono due cartelle di
  testi `.md` o `.txt`: (a) prosa italiana scritta da un modello; (b) prosa italiana scritta da persone,
  dello stesso genere e di epoca recente, con diritti d'uso. Poi:
  `python3 motore/zb antiia estrai --ia <cartella a> --umano <cartella b>`.

## 3. Verifica dei dati KDP (passo manuale)
- `motore/dati/kdp.yaml`: `ultima_verifica: null`. Va verificato da te sulle pagine KDP e registrato con
  `python3 motore/zb verifica KDP fatta AAAA-MM-GG`. Il motore non la inventa.

## 4. Nomi vietati
- `motore/dati/nomi_vietati.txt` è vuoto: i nomi dei libri veri li scrivi tu (resta l'unico file del
  ramo motore in cui possono stare). `zb separazione` controlla anche i nomi dei rami di libro su origin
  e gli slug della banca-voci, senza scriverli.

## 5. Licenze
- APODICTIC (CC BY-NC-SA 4.0): nessun testo usato; per usarne di più serve una licenza commerciale
  dall'autore del repository (decisione tua).

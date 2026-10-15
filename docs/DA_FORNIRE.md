# Da fornire o decidere (autore)

## 1. Livello editoriale
- Fornito in chat (`editoriale_tutto.md`) e ricreato esatto: 28 file (commit cc58ae6). Le integrazioni fatte dopo
  sono elencate nel commit cc12973. Contrasti segnalati, decisi in favore della base dove possibile:
  - catalogo anti-IA, sezione B: elenco di formule (la regola 6.2 chiede solo schemi senza liste di parole): tenuto
    come esempio per scrittore e line editor, NON misurato dal motore; da decidere se toglierlo.
  - criteri del correttore, sezione 5: la coppia «avvenire/avvenire» è uguale ai due lati (refuso?): non toccata.
  - editor strutturale: la base scrive `piano-revisione.md`; il motore usa `piano-revisione-struttura.md` e
    `piano-revisione-manoscritto.md` per non sovrascrivere il piano già approvato della struttura.

## 2. Corpus per il vocabolario anti-IA italiano
- I livelli L1-L3 dell'italiano sono vuoti (regola 6.2). Servono due cartelle di testi: (a) prosa italiana scritta da
  un modello; (b) prosa italiana scritta da persone, stesso genere, recente, con diritti d'uso. Poi
  `python3 motore/zb antiia estrai --ia <a> --umano <b>` e `zb antiia taratura --umano <b>`.

## 3. Verifica dei dati KDP (passo manuale)
- `motore/dati/kdp.yaml`: `ultima_verifica: null`. Verificali sulle pagine KDP e registra
  `python3 motore/zb verifica KDP fatta AAAA-MM-GG`. Il motore non la inventa.

## 4. Nomi vietati
- `motore/dati/nomi_vietati.txt` è vuoto. `zb separazione` ora controlla anche `docs/` e `CLAUDE.md`, i nomi dei rami
  di libro su origin e gli slug della banca-voci (con `ZB_BANCA_VOCI`), senza scriverli. Titoli, personaggi e luoghi
  dei libri veri li puoi aggiungere tu nel file.

## 5. Licenze
- APODICTIC (CC BY-NC-SA 4.0): nessun testo usato; per usarne di più serve una licenza commerciale dall'autore.
- DDChen666/translate-book (CC BY-NC-SA 4.0), howells/fiction (licenza non chiara: manca il file LICENSE),
  Book-pipeline e darkautism/ai-novel-translation (nessuna licenza): usate solo idee generali.

## 6. Traduzione
- Confronto sequenza / blocchi con ancora di stile (8.4): lo strumento c'è (`zb traduci … confronta`), ma un confronto
  valido chiede due traduzioni fatte in contesti separati (subagenti); in questa sessione non le ho fatte.
  Raccomandazione: in sequenza, con glossario approvato (osservazione misurata in fredchu/book-translator).
- Edizione commerciale: lettura finale di un madrelingua consigliata. KDP chiede di dichiarare la traduzione fatta con
  l'IA («AI-generated», Content Guidelines, verificato il 2026-10-15).

## 7. Unione nel ramo `motore`
- Il lavoro è sul ramo della sessione `ccr-d1e12273-izx78k` (partito da `origin/motore`): l'unione nel ramo `motore`
  la decidi tu.

## 8. Archivio di quanto tolto da docs/
- `ESPORTAZIONE_COMPLETA_1-6.md` e le versioni precedenti di `INFRASTRUTTURA_COMPLETA.md` e della guida: copia
  verificata (sha256) nell'archivio inviato in chat; restano anche nella storia git (commit 7f97ddb e precedenti).

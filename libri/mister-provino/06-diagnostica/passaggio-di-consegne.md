# Passaggio di consegne — Mister Provino e motore (13 ottobre 2026)

Da incollare all'inizio della nuova chat. Tutto quello che segue è su origin.

## 1. Repository e rami
- Repository: NGTAProtocol/ZeusBot.
- **mister-provino**: il libro, in `libri/mister-provino/`. Ultimo commit: **80bf352**.
- **motore**: il motore, in `motore/`. Ultimo commit: **d4b6fa6**.
- **mister-provino contiene già tutto il motore** (merge di origin/motore senza conflitti).
- Nella sessione vecchia i rami erano in cartelle separate (`/home/user/ZeusBot-mpv` per il libro, `/home/user/ZeusBot-mt` per il motore). Quelle cartelle non sopravvivono: nella nuova chat si riparte dai rami su origin.
- Comandi del motore: `python3 -B motore/zb <comando> libri/mister-provino …`, lanciati dalla radice del repository sul ramo mister-provino.

## 2. Regole fisse dell'autore
- Non toccare `libri/kurgan-giorgi/` né `01-originale/`. Il vecchio testo è un registro dei fatti.
- NON lanciare impagina, pdf, kdp, pacchetto. Il PDF non si crea.
- Il .md completo (`05-output/mister-provino-completo.md`, da `zb compila`) è l'unico file derivato ammesso.
- Risposte brevi, niente codice, niente capitoli in chat.
- Dove si salva:
  - il motore solo in `motore/` sul ramo motore;
  - il libro solo in `libri/mister-provino/` sul ramo mister-provino (`04-manoscritto/`, `06-diagnostica/`, `05-output/`).
- Salvataggio, ogni volta:
  - un commit per blocco;
  - `git add`, `git status -sb`, push con `zb push`;
  - poi `git status -sb` e `git log -1`.
- Se il push fallisce: fermarsi e riportare l'errore. Non dire «fatto» se il lavoro non è su origin.
- Resoconto finale: hash, file, «branch allineato a origin: sì/no» per ogni ramo toccato.
- Se un controllo fallisce due volte per un difetto del motore: fermarsi e dire quale controllo, quale file, quale riga.
- Righe finali dei commit:
  - `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
  - `Claude-Session: https://claude.ai/code/session_01PySnQfqKrcYLQSUgWEeMK5`
- Nessun identificativo di modello nei file del repository.

## 3. Come lavora il motore (le cose che servono)
- **Correzioni con la fase in chiusura.** Si modifica il testo e lo si registra con `zb correggi libri/mister-provino "<unità>: <motivo>"`. Poi `zb esito libri/mister-provino <N>` ricontrolla l'unità senza cambiare la fase.
- **Documenti approvati** (libro.yaml, bibbia, cronologia, manuale, scaletta, piano-parole…):
  1. modifica e commit (anche solo locale);
  2. `zb riapprova libri/mister-provino <percorso, es. 02-bibbia/bibbia.md> "<motivo>"`;
  3. commit di `stato.yaml`.
  - Servono sempre **2 commit**: la riapprovazione registra l'hash del primo.
- **`zb push`** fa fino a 4 tentativi con attesa crescente. Se non bastano, prova un ramo `<ramo>-salvataggio-<data>`, poi crea un git bundle (percorso e sha256 a schermo).
  - GitHub ogni tanto risponde «Internal Server Error». Nel caso: attendere circa 2 minuti e riprovare.
- **`zb conta`** stampa a schermo e non scrive file. Per i report a schermo: `zb continuita` e `zb stile` con `--schermo`.
- **Voci in `libro.yaml`**: `voci` (con `modalita`, `ambito`, `consentito_in_capitoli`, `conta_per`, `escludi_pattern`), `vincoli_capitolo`, `nome_vietato_prima_di`.
- **Campi nuovi in `libro.yaml`:**
  - `fatti_incompatibili`: `{id, a: {pattern, unita}, b: {pattern, unita}, nota}`. Dà un avviso con le due righe se compaiono tutti e due.
  - `stile.eccezioni`: `{unita, controllo, motivo}`. Trasforma l'AVVISO in ECCEZIONE; i KO restano KO.
  - `stile.richiami_ammessi`: frasi ripetute di proposito tra unità, che il controllo anti-riciclo non segnala.
- **Controlli di continuità aggiunti:**
  - tempi relativi («N giorni/settimane/mesi prima/dopo/fa», «la N-esima notte/mattina»), confrontati con le date delle intestazioni, del testo e della cronologia;
  - differenze d'età tra personaggi con data di nascita in `cronologia.yaml`.
- **Limiti noti:**
  - Tempi relativi: l'avviso scatta solo se nessuna data nota coincide. Nei periodi pieni di date un numero sbagliato può cadere su un altro giorno datato e passare inosservato.
  - Differenze d'età: valgono solo per Beniamino e Checco, gli unici con data di nascita completa.
- **`zb prove`**: 422 su 422 OK. 2 prove saltate (LanguageTool, ZB_LANGUAGETOOL non impostata). Sono test su testi inventati, registrati in `motore/prove/attesi.yaml`.

## 4. Stato del libro
- Fase **chiusura**, passo «controlli finali», nessun gate in attesa, 0 avvisi aperti.
- 43 capitoli, più prologo, interludi I-IX ed epilogo, tutti scritti.
- Parole: **77.192** su 78.000 (−1,0%). Il .md completo ne conta 77.569; sha256 69e068b6b36f6c3ce113a73fdcf4275b648b0cadff70a91999ffe42e522a0098.
  - Il .md è stato compilato prima delle ultime modifiche a libro.yaml e bibbia; il testo dei capitoli non è cambiato.
- Il .md completo ha i titoli dei capitoli nella forma «1. Pane e Pomodoro».
- Controlli attuali:
  - continuita: 0 KO, 0 avvisi;
  - stile: 1 avviso, la frase media dell'interludio V (9,9; l'intervallo è 10-13);
  - interludio VI: ECCEZIONE («frasi brevi volute»);
  - epilogo: il budget non dà avvisi; l'eccezione «−9,4%, tagliate frasi deboli» resta registrata;
  - riciclo: 1 avviso, l'eco tra epilogo:33 e 25:39, «cabina in fondo alla via del basso». È un richiamo voluto, ma non è ancora tra i `richiami_ammessi`.
  - «la sera che venne da Michele» (39 ↔ 35) è ammessa e non dà più avviso.

## 5. Lavoro fatto in quest'ultima serie
- Audit del manoscritto intero (ffed613). Correzioni a–l dopo l'audit (009e1a5), tutte registrate con `zb correggi`:
  - Genova: Michele non va più a Genova; le carte arrivano per posta;
  - durate: 11 «quattro giorni», 18 «dodici giorni», 27 «dieci giorni»; 20 «Dopo la quarta notte, il sabato»;
  - età: 25, Saro «con sei anni in più»;
  - fatti: 39 «la sera che venne da Michele»; 3 Checco in falegnameria;
  - coperta militare al posto della tenda (36 e 37); «uagnò» al posto di «uagliò» (36);
  - piccole correzioni: 4 «di cui»; 43 «Questo è olio»; 41 «Fino a ieri»;
  - 14 «la mattina della nave ferma»; riprese del prologo variate nell'interludio IX.
- Voce `guaglio_napoletano` in libro.yaml (e9e2599): «guagliò» ammesso solo nei capitoli 2 e 35.
- Ricontrollo (f4dc0a6): `06-diagnostica/delta.md`, più le proposte **non applicate**:
  - `06-diagnostica/proposte/tetti.md`: orari oltre il tetto nei capitoli 13, 18, 26, 28;
  - `06-diagnostica/proposte/tic.md`: 40 sostituzioni per «mi guardò», «per un momento», «senza dire niente», «con due dita».
- Bibbia §5.7: tolto l'obbligo di dire la cifra «168 e qualcosa» a Genova. In libro.yaml: eccezioni per epilogo e interludio VI, richiamo «la sera che venne da Michele» (0616b09, riapprovazioni in 256a53c).
- Motore:
  - 8c3784a: titoli, tempi relativi, età, fatti incompatibili, `zb push`, `zb conta` senza file, catena degli sha256 delle correzioni;
  - d4b6fa6: eccezioni e richiami ammessi.

## 6. Ancora aperto (decide l'autore)
- Proposte tetti.md e tic.md: da approvare o scartare. Non sono applicate.
- Interludio V: frase media 9,9. Si accorcia meno o si aggiunge un'eccezione?
- Eco «cabina in fondo alla via del basso» (epilogo/25): aggiungerla a `stile.richiami_ammessi`?
- Viaggi di Michele lontano da Bari, righe da tenere d'occhio, oggi coerenti: 16:159, 21:23, 32:87, 34:29, 41:17.
- Possibili `fatti_incompatibili` da dichiarare (per esempio Michele mai oltre Foggia prima del cap. 40). Oggi il libro non ne dichiara nessuno.
- `zb stato` dice «approvati fino a 3» anche se i capitoli scritti sono 43: è il contatore dei primi capitoli approvati al gate, non un errore nuovo.
- Passi finali, quando lo dice l'autore: `zb ortografia`, poi `zb pronto`. Impagina, pdf, kdp e pacchetto **solo su sua richiesta esplicita**.

## 7. Altri rami in questo repository (non toccati qui)
- claude/kurgan-giorgi-thriller-3f6mfq (altro libro: non toccare).
- claude/mister-provino-espansione (vecchio lavoro).
- prova-romance.

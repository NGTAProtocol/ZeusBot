# Passaggio di sessione — Il quaderno nell'ulivo (La Banda della Gravina, 1)

Prompt da incollare in una nuova sessione di Claude Code.

---

LIBRO «Il quaderno nell'ulivo» (La Banda della Gravina, 1) — ripresa dopo il capitolo 25 (fase chiusura)

CONTESTO
- Repository NGTAProtocol/ZeusBot, ramo libro/ulivo-pensante-vol1, cartella libri/ulivo-pensante-vol1/.
  Push solo su quel ramo, sempre esplicito: git push origin libro/ulivo-pensante-vol1. Nessun push forzato.
- motore/ e banca-voci (NGTAProtocol/https-github.com-banca-voci): sola lettura, nessuna modifica.
- Romanzo per ragazzi 9-12 anni, Ginosa e le gravine. Autore F.R. Faraone. 25 capitoli, 12 enigmi con pagina
  «L'enigma della banda» (cap. 2, 4, 6, 8, 9, 11, 13, 15, 17, 19, 21, 23). Voce mistero-ed-epicita, terza persona
  vicina a Pino, dialetto spento, lineetta «—», titoli «# N — Titolo», riga <!-- zb: chiusura=X -->.
- Il vecchio «L'Ulivo Pensante» (materiale/…docx) è solo registro dei fatti.

STATO (dopo il lotto C; ultimo commit: vedi git log -1)
- Tutti i 25 capitoli scritti e accettati dal motore. Fase «chiusura», passo «controlli finali», nessun gate.
  Approvati dal motore 1-3; 4-15 letti e corretti dall'autore; 16-25 da leggere.
- Parole (metodo unico del motore): 1 = 1.366 · 2 = 1.365 · 3 = 1.388 · 4 = 1.320 · 5 = 1.300 · 6 = 1.377 ·
  7 = 1.349 · 8 = 1.225 · 9 = 1.196 · 10 = 1.335 · 11 = 1.160 · 12 = 1.236 · 13 = 1.152 · 14 = 1.187 ·
  15 = 1.216 · 16 = 1.237 · 17 = 1.252 · 18 = 1.170 · 19 = 1.322 · 20 = 1.212 · 21 = 1.307 · 22 = 1.294 ·
  23 = 1.274 · 24 = 1.270 · 25 = 1.249. Totale 31.759 / 32.500 (-2,3%).
- Lotto C: correzioni K1 (cap. 17), K2 (cap. 18), K3-K5 (cap. 19); cap. 21-25 scritti; cap. 24 corretto due
  volte (KO «cifra quaderni» al primo esito; poi la radio «non ancora pronta» per coerenza con il cap. 17).

DECISIONI PRESE (non rimetterle in discussione; registro-fatti D1-D6)
- Guardiano: si rivela nel cap. 22, sul ciglio; «il vicedirettore», senza nome; alto, dritto, capelli grigi alle
  tempie, camicia azzurra, cravatta in tasca; riconosce Tonio e Pino, non li ferma; la corda tolta «senza sapere»;
  la figlia («la piccola») solo per accenni; nel cap. 25 è alla festa con lei.
- Codice dell'allarme: la madre di Checco ha trovato nella borsa un foglietto di Checco e l'ha letto ad alta voce
  in bottega a Gianni (radio non ancora pronta); lo racconta Gianni nel cap. 24. Nessun filo aperto nel cap. 25.
- Rocca Vetere: il nome non compare in nessun capitolo («il muro», «la zona del muro»). La nota dell'autore in
  libro.yaml lo cita ancora: DA RIVEDERE (toglierlo se non verificato su carta).
- «Sviluppo Territoriale Sostenibile S.r.l.» solo nel cap. 25 (dietro il biglietto: «Alla prossima estate.»).
- Archeologia: muro «antico, di grosse pietre squadrate»; solo il funzionario: «Probabilmente di età greca. Ma
  va verificato.» Niente Sparta, niente date. Sette quaderni (più l'ottavo, bianco, regalato a Pino nel cap. 25).
- Pagine enigma: a fine scena 1 quando la soluzione si vede nel capitolo (cap. 4, 8, 9, 13, 15, 17, 19, 21, 23).
- Date: 21-22 sabato 18 luglio (filmato del drone: 19 luglio, 1:24), 23 domenica 19, 24 lunedì 20, 25 sabato 25.

DA VERIFICARE (00-progetto/registro-verifiche.md)
- (a) Piazza dell'Orologio: fontana, portici, bar, tre porte, luci della festa sono invenzione.
- (b) Rocca Vetere: nota dell'autore da rivedere.
- (c) Botanica: esito del 14/10/2026 invariato (iris non verificato).

AVVIO (in quest'ordine)
1. git fetch origin libro/ulivo-pensante-vol1 && git checkout libro/ulivo-pensante-vol1
2. git rev-parse --abbrev-ref @{u} deve dare origin/libro/ulivo-pensante-vol1.
3. Banca-voci in sola lettura in /home/user/https-github.com-banca-voci;
   export ZB_BANCA_VOCI=/home/user/https-github.com-banca-voci
4. python3 motore/zb avvio libri/ulivo-pensante-vol1 → riportare «Letto: …»; python3 motore/zb stato
   libri/ulivo-pensante-vol1 (atteso: «Fase: chiusura; passo: controlli finali; gate in attesa: nessuno»).
5. Leggere questo file, scaletta (cap. 21-25), registro-fatti (N21-N35, D2-D6), registro-verifiche, cap. 21-25.

PRIMA AZIONE NELLA NUOVA SESSIONE
Aspettare la lettura dell'autore dei cap. 16-25 e le sue correzioni. Il motore propone i passi di chiusura
(zb continuita, zb ortografia, zb compila, zb impagina, zb pdf, zb pacchetto, zb kdp, zb pronto): non lanciarli
senza istruzione dell'autore. Da fare prima della chiusura: nota dell'autore (Rocca Vetere), pagina delle
soluzioni dei 12 enigmi e mappa della gravina in fondo al libro (scaletta, cap. 25).

FLUSSO DEL MOTORE E SALVATAGGIO
- Correzioni a capitoli già scritti: modificare, commit, zb correggi libri/ulivo-pensante-vol1 "N: motivo"
  --commit <hash>. Documenti approvati: dopo il commit, zb riapprova libri/ulivo-pensante-vol1 <documento>
  "<motivo>". Entrambi scrivono stato.yaml: secondo commit.
- Misurare prima di zb esito; «sei» vicino a «quaderni» dà KO; anche «uno» vicino a «quaderni» (cap. 24).
- Salvataggio: git add, commit, git push origin libro/ulivo-pensante-vol1, git status -sb, git log -1.

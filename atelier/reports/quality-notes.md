## Note sulle misure (v2)

- **Run singola per profilo.** Lighthouse è stato eseguito una volta per profilo e per sito, perché 24 siti × 2 profili richiedono già circa 75 minuti. Le stesse pagine ripetute oscillano parecchio. Esempio: quota-2100 baseline CINEMATICO ha dato mobile 80 nell'iterazione 1 e 67 nell'iterazione 2, senza modifiche al codice (la ricompilazione ha cambiato solo la presenza del CSS). Differenze di pochi punti tra configurazioni **non** sono significative.
- **Iterazioni:**
  - iterazione 1: tutti i 24 siti (`reports/qa-v2-iter1/`, log `qa-iter1.log`);
  - iterazione 2: Nodo (reticolo corretto) e le 6 baseline (stile corretto), con log `qa-iter2.log`;
  - `reports/qa/` contiene l'ultima misura di ogni sito.
- **Difetto trovato nella baseline e corretto:** Tailwind 4 non scansiona le cartelle in `.gitignore` e `engine/src/generated/` lo è. Per questo **in v1 tutte le baseline uscivano senza stile** (testo nero su bianco, vedi `reports/shots` della v1). Il confronto della v1 era quindi falsato a favore di Atelier. Ora `baseline.css` dichiara `@source "../generated"` e un test verifica che le classi della baseline abbiano CSS.
- **Reticolo (Nodo):**
  - prima versione: centinaia di `gsap.set` e misure per segmento. TBT mobile 1.241 ms (A) e 1.803 ms (C), sotto soglia;
  - riscritto con le coordinate già nell'SVG e scrittura solo dei segmenti che cambiano: TBT 44 ms (A), 265 ms (C), mobile 99 e 94.
- **3D solo dove è la firma:**
  - Three.js entra nel bundle solo in fornace-lume-b e quota-2100-a CINEMATICO (verificato da `npm test`);
  - con il 3D forzato all'avvio (`?force3d`, Web Worker) misurano mobile 99 e 93;
  - le baseline CINEMATICO, con un 3D in loop infinito nel thread principale, misurano 65-88.
- **LCP:** le baseline usano i font di sistema e hanno LCP più basso (0,75 s contro 1,0-1,9 s), ma il CINEMATICO delle baseline perde punti sul TBT.
- **WebGL software:** tutto il 3D è renderizzato con SwiftShader (CPU). Nessuna GPU reale, nessun dispositivo reale.
- **Rilevatore di slop circolare:** controlla le regole che il lint di Atelier già impone. Non vede, nelle baseline, il modulo senza backend e il riquadro segnaposto di Fornace (li ha notati la rubrica).
- **Distanza visiva, misura grezza:** differenza dei pixel a 64×40, dominata dal colore di fondo. Dice comunque una cosa vera: i siti A e C di clienti diversi si somigliano tra loro (fondi chiari, stesso motore e stesso schema di pagina) più di quanto si somiglino le baseline tra loro.

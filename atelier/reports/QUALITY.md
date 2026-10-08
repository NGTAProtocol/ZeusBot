# Report di qualità (generato da scripts/report.mjs)

Misure: Lighthouse 13.5.0 su Chromium headless (rendering WebGL software SwiftShader), server statico locale con gzip, mediana di più run (indicate). Mobile = profilo Lighthouse predefinito (Moto G, rete 4G lenta simulata, CPU 4x); desktop = preset desktop.

## Lighthouse

| Sito | Variante | Perf mobile | Perf desktop | Accessibilità | SEO | LCP mobile | TBT mobile | Peso | Soglie |
|---|---|---|---|---|---|---|---|---|---|
| fornace-lume | BASELINE | 100 (100/100/100) | 100 (100/100/100) | 100 | 100 | 0.75 s | 3 ms | 5 KB | — |
| fornace-lume | BASE | 100 (100/100/100) | 100 (100/100/100) | 100 | 100 | 1.36 s | 0 ms | 73 KB | ✅ |
| fornace-lume | CINEMATIC | 99 (99/98/99) | 100 (100/100/100) | 100 | 100 | 1.82 s | 34 ms | 121 KB | ✅ |
| nodo-sicuro | BASELINE | 100 (100/100/100) | 100 (100/100/100) | 100 | 100 | 0.75 s | 0 ms | 4 KB | — |
| nodo-sicuro | BASE | 100 (100/100/100) | 100 (100/100/100) | 100 | 100 | 1.51 s | 0 ms | 76 KB | ✅ |
| nodo-sicuro | CINEMATIC | 97 (99/97/95) | 100 (100/100/100) | 100 | 100 | 1.89 s | 161 ms | 123 KB | ✅ |
| quota-2100 | BASELINE | 100 (100/100/100) | 100 (100/100/100) | 100 | 100 | 0.76 s | 0 ms | 4 KB | — |
| quota-2100 | BASE | 98 (98/98/98) | 100 (100/100/100) | 100 | 100 | 1.88 s | 0 ms | 152 KB | ✅ |
| quota-2100 | CINEMATIC | 97 (97/97/97) | 99 (99/100/94) | 100 | 100 | 2.26 s | 76 ms | 199 KB | ✅ |

### Costo del 3D avviato subito (`?force3d`), solo CINEMATICO

Nel CINEMATICO il 3D parte al primo gesto dell'utente; Lighthouse non interagisce, quindi la tabella sopra misura la pagina **prima** del 3D. Qui il 3D è forzato al caricamento.

**Attenzione:** il 3D gira in un Web Worker (OffscreenCanvas). Lighthouse non conta né il peso del worker (~133 KB gzip, Three.js incluso) né il suo lavoro CPU, che non blocca il thread principale. Questi numeri misurano quindi solo l'impatto sul thread principale, non il costo totale sul dispositivo. Verificato con Playwright: con `?force3d` il 3D è attivo dopo circa 3,2 s.

| Sito | Perf mobile | TBT mobile | Perf desktop | TBT desktop | Peso desktop (senza il worker) |
|---|---|---|---|---|---|
| fornace-lume | 99 | 69 ms | 100 | 0 ms | 122 KB |
| nodo-sicuro | 99 | 71 ms | 100 | 0 ms | 124 KB |
| quota-2100 | 96 | 100 ms | 94 | 0 ms | 201 KB |

## Controlli automatici (Playwright)

| Sito | Variante | Overflow a 375 | Errori console | Host esterni | Contenuti nascosti dopo lo scroll (375/768/1280) | 3D attivo a 1280 | Fallback reduced-motion | Fallback no-WebGL | Fallback Save-Data |
|---|---|---|---|---|---|---|---|---|---|
| fornace-lume | BASELINE | ✅ no | 0 | nessuno | 0/0/0 | — | n/d, nascosti 0, canvas no | — | — |
| fornace-lume | BASE | ✅ no | 0 | nessuno | 0/0/0 | — | n/d, nascosti 0, canvas no | — | — |
| fornace-lume | CINEMATIC | ✅ no | 0 | nessuno | 0/0/0 | ✅ | reduced-motion, nascosti 0, canvas no | poster sì, canvas no | save-data, canvas no |
| nodo-sicuro | BASELINE | ✅ no | 0 | nessuno | 0/0/0 | — | n/d, nascosti 0, canvas no | — | — |
| nodo-sicuro | BASE | ✅ no | 0 | nessuno | 1/0/0 | — | n/d, nascosti 0, canvas no | — | — |
| nodo-sicuro | CINEMATIC | ✅ no | 0 | nessuno | 0/0/0 | ✅ | reduced-motion, nascosti 0, canvas no | poster sì, canvas no | save-data, canvas no |
| quota-2100 | BASELINE | ✅ no | 0 | nessuno | 0/0/0 | — | n/d, nascosti 0, canvas no | — | — |
| quota-2100 | BASE | ✅ no | 0 | nessuno | 0/0/0 | — | n/d, nascosti 0, canvas no | — | — |
| quota-2100 | CINEMATIC | ✅ no | 0 | nessuno | 0/0/0 | ✅ | reduced-motion, nascosti 0, canvas no | poster sì, canvas no | save-data, canvas no |

## Rubrica 1-10 (AUTOVALUTAZIONE)

**Autovalutazione.** I punteggi sono stati assegnati dallo stesso modello che ha generato sia i siti Atelier sia le baseline, guardando gli screenshot reali a 375/768/1280. Non è un giudizio indipendente: va confermato da un designer o da test con utenti. Le baseline sono state scritte in una sola passata, in buona fede, senza la skill e senza guardare gli screenshot.

### Iterazione 1 (prima build completa, dopo le correzioni funzionali)

| Sito | Variante | Gerarchia | Contrasto | Spazio | Coerenza | Originalità | Movimento | Mobile | Media |
|---|---|---|---|---|---|---|---|---|---|
| fornace-lume | BASELINE | 7 | 8 | 7 | 7 | 3 | 5 | 6 | **6.1** |
| fornace-lume | BASE | 8 | 8 | 7 | 8 | 6 | 6 | 7 | **7.1** |
| fornace-lume | CINEMATICO | 8 | 8 | 7 | 8 | 8 | 8 | 7 | **7.7** |
| quota-2100 | BASELINE | 7 | 8 | 7 | 7 | 3 | 5 | 6 | **6.1** |
| quota-2100 | BASE | 8 | 8 | 7 | 8 | 7 | 6 | 7 | **7.3** |
| quota-2100 | CINEMATICO | 7 | 7 | 6 | 8 | 8 | 8 | 6 | **7.1** |
| nodo-sicuro | BASELINE | 7 | 8 | 7 | 7 | 2 | 5 | 6 | **6.0** |
| nodo-sicuro | BASE | 8 | 9 | 7 | 8 | 6 | 6 | 8 | **7.4** |
| nodo-sicuro | CINEMATICO | 8 | 7 | 6 | 8 | 7 | 7 | 8 | **7.3** |

Punti peggiori emersi:
- Originalità del BASE di Fornace: il poster blob ha bordi spigolosi e sembra una clipart.
- Spazio nel CINEMATICO di Quota: i titoli di sezione con il font esteso arrivano a 5 righe.
- Mobile del CINEMATICO di Quota: hero affollato.
- Contrasto nel CINEMATICO di Nodo: lo scrub di opacità spegneva anche la CTA della sezione contatti (bug).

Nelle baseline:
- originalità bassa: card con emoji, gradienti, hero centrato generico; Nodo usa il gradiente indaco-viola, cliché della lista nera;
- gerarchia e contrasto sono comunque solidi.

### Iterazione 2 (finale)

| Sito | Variante | Gerarchia | Contrasto | Spazio | Coerenza | Originalità | Movimento | Mobile | Media |
|---|---|---|---|---|---|---|---|---|---|
| fornace-lume | BASELINE | 7 | 8 | 7 | 7 | 3 | 5 | 6 | **6.1** |
| fornace-lume | BASE | 8 | 8 | 7 | 8 | 7 | 6 | 7 | **7.3** |
| fornace-lume | CINEMATICO | 8 | 8 | 7 | 8 | 8 | 8 | 7 | **7.7** |
| quota-2100 | BASELINE | 7 | 8 | 7 | 7 | 3 | 5 | 6 | **6.1** |
| quota-2100 | BASE | 8 | 8 | 7 | 8 | 7 | 6 | 7 | **7.3** |
| quota-2100 | CINEMATICO | 8 | 7 | 7 | 8 | 8 | 8 | 6 | **7.4** |
| nodo-sicuro | BASELINE | 7 | 8 | 7 | 7 | 2 | 5 | 6 | **6.0** |
| nodo-sicuro | BASE | 8 | 9 | 7 | 8 | 6 | 6 | 8 | **7.4** |
| nodo-sicuro | CINEMATICO | 8 | 9 | 7 | 8 | 7 | 7 | 8 | **7.7** |

Modifiche dell'''iterazione 2:
- poster SVG con curve lisce (Catmull-Rom);
- titoli di sezione scalati in base alla larghezza media dei caratteri del font;
- scrub di opacità limitato ai soli capitoli (la CTA dei contatti non viene più spenta);
- l'''indice laterale si aggiorna anche risalendo;
- spazio sotto il footer per la barra CTA mobile.

Punti rimasti deboli e non risolvibili con ritocchi:
- Mobile del CINEMATICO di Quota: con un titolo lungo e un font esteso l'''hero resta denso;
- Originalità del BASE di Nodo: la direzione tech scura è la meno distintiva;
- Movimento nel BASE: volutamente minimo (6).


## Note sulle misure
- **Accessibilità delle baseline:** Nodo e Quota hanno ottenuto 90 nell'iterazione 1 (audit `color-contrast`) e 100 nell'iterazione 2 senza alcuna modifica al loro codice. La verifica del contrasto su testo sopra sfondi sfumati e trasparenze oscilla fra un run e l'altro. Dati grezzi in `reports/qa-iter1/` (iterazione 1) e `reports/qa/` (finale).
- **"Contenuti nascosti 1/0/0" nel BASE di Nodo:** non si riproduce in 3 esecuzioni dedicate. È un falso positivo di temporizzazione: con Lighthouse in parallelo, l'observer reagisce dopo la misura.
- **Peso:** le baseline pesano 4-5 KB perché usano i font di sistema e nessuna immagine. I siti Atelier pesano 73-199 KB senza il 3D, di cui la parte maggiore sono i webfont OFL in locale. L'LCP delle baseline (0,75 s) è **migliore** di quello di Atelier (1,4-2,3 s) proprio per i webfont.
- **WebGL software:** tutto il 3D è stato renderizzato con SwiftShader (CPU). Su GPU reali è più leggero, ma **non è stato misurato**.
- **Storia delle prestazioni del CINEMATICO** (misure intermedie):
  - prima versione: mobile 72, desktop 60 (TBT 1,8 s). Causa: verifica di WebGL con un contesto di prova sincrono;
  - dopo la correzione e con il 3D al primo gesto: mobile 97-99, desktop 100;
  - con il 3D forzato all'avvio, ancora nel thread principale: mobile 74, desktop 68;
  - dopo lo spostamento nel Web Worker: mobile 96-99, desktop 94-100 (vedi l'avvertenza sopra).
- **Potatura degli asset (dopo la misura finale):** Astro emetteva i chunk del CINEMATICO (GSAP, Lenis, Three.js) anche nell'output del BASE, senza che la pagina li caricasse. `generate.mjs` ora elimina i `.js` non raggiungibili dall'HTML. Il comportamento e i byte scaricati dal browser non cambiano, quindi le misure restano valide; cambia solo lo spazio su disco del deploy (~1,3 MB in meno per il BASE). Il controllo è in `npm test`.

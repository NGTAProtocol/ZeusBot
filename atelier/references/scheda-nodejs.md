# Scheda — nodejs.org (misurato)

- **Settore:** open source / documentazione tecnica. Non è un sito premiato.
- **Stack rilevato:** Next.js (`/_next/`, `#__next`). GSAP, Lenis, Three.js e Howler non rilevati.
- **Struttura:** nav, main, footer; 2 `<section>`; 1 h1, nessun h2; pagina corta (~980 px di altezza a 1280).
- **Scroll:** nativo, nessun elemento sticky.
- **Rete:** 37 richieste, 20 script. Peso totale secondo Lighthouse: 785 KB.
- **Lighthouse mobile:** performance 70, accessibilità 100, best practices 100, SEO 100 (LCP 4,8 s, TBT 161 ms). Desktop: performance 91.
- **Cosa ne ricavo:** anche un sito con pochissime animazioni sta sotto 75 su mobile quando carica molti script del framework. Per il livello CINEMATICO il budget JS è il vincolo principale.
- Dati grezzi: `references/data/nodejs-org.json`.

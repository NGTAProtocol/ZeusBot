# Scheda — www.anthropic.com (misurato, degradato)

- **Settore:** AI / corporate. Non è un sito scelto per premi, è solo uno dei due raggiungibili.
- **Avvertenza:** i font e le risorse di host terzi sono bloccati dal proxy di questo ambiente. Il sito rende con i font di sistema e solo 7 richieste, quindi peso e prestazioni misurati **non** sono quelli reali.
- **Stack rilevato:** Webflow (attributo `data-wf-site`). GSAP, Lenis, Three.js e Howler non sono stati rilevati, ma con le risorse esterne bloccate il dato potrebbe essere incompleto.
- **Struttura:** header, nav, main, footer; 6 `<section>`; 1 h1, 5 h2, 19 h3; 2 `<canvas>`.
- **Scroll:** nativo (nessuna classe Lenis); 1 elemento fixed/sticky (header).
- **Lighthouse mobile (degradato):** performance 96, accessibilità 92, best practices 73, SEO 92 (LCP 2,2 s, TBT 26 ms). Desktop: 99 / 92 / – / 92.
- **Cosa ne ricavo:** gerarchia di titoli disciplinata (un solo h1, pochi h2, molti h3), poca chrome, un solo elemento fisso.
- Dati grezzi: `references/data/www-anthropic-com.json`.

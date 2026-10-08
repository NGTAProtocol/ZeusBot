# Statistiche di stack sul campione misurato

Campione **effettivamente misurato**: 2 siti su 10 tentati (https://nodejs.org/en, https://www.anthropic.com/).
**Nessuno dei siti premiati è nel campione** (bloccati dalla rete, vedi README). Queste percentuali NON descrivono i siti premiati.

| Libreria / framework | Siti | % |
|---|---|---|
| GSAP | 0/2 | 0% |
| ScrollTrigger | 0/2 | 0% |
| Lenis | 0/2 | 0% |
| Three.js | 0/2 | 0% |
| Howler | 0/2 | 0% |
| React | 0/2 | 0% |
| Next.js | 1/2 | 50% |
| Nuxt | 0/2 | 0% |
| Astro | 0/2 | 0% |
| SvelteKit | 0/2 | 0% |
| Webflow | 1/2 | 50% |
| Framer | 0/2 | 0% |

Regola di rilevamento: global JS (es. `window.gsap`), URL degli script, classi o selettori tipici (es. `html.lenis`, `#__next`, `data-wf-site`). Un risultato negativo con le risorse di terzi bloccate può essere un falso negativo.

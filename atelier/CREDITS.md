# CREDITS

Ogni asset e ogni dipendenza inclusi nei siti generati, con la loro licenza.
Regola di Atelier: **nessun hotlinking, nessuna CDN**. Tutto è servito dal sito stesso.

## Grafica, 3D, shader, testi
| Elemento | Origine | Licenza |
|---|---|---|
| Poster SVG procedurali (`engine/src/lib/poster.js`) | scritti per Atelier | come il progetto |
| Geometrie e shader GLSL dell'hero 3D (`engine/src/scripts/hero3d.js`) | scritti per Atelier. Il rumore a valori e la funzione di hash `fract(sin(dot(...)))` sono formule matematiche di uso comune, riscritte qui, non copiate da file di terzi | come il progetto |
| Grana (filtro SVG `feTurbulence`) | primitiva standard SVG, scritta per Atelier | come il progetto |
| Audio d'ambiente | sintetizzato in tempo reale con WebAudio, nessun file audio | come il progetto |
| Testi dei siti di esempio | scritti per Atelier per attività **fittizie** (Fornace Lume, Quota 2100, Nodo) | come il progetto |
| Immagini fotografiche / stock | **nessuna** | — |
| Modelli 3D | **nessuno** | — |

## Font (tutti SIL Open Font License 1.1, inclusi tramite pacchetti @fontsource da npm)
Young Serif, Hanken Grotesk, Archivo (variabile), Literata, Familjen Grotesk, Newsreader, Fraunces, Manrope, Syne, Work Sans, Cormorant Garamond, Instrument Sans, Bricolage Grotesque, Libre Caslon Text, Space Grotesk, IBM Plex Sans.
Licenza verificata dal campo `license` dei pacchetti npm: `OFL-1.1`.

## Librerie JavaScript incluse nei siti
| Libreria | Versione | Licenza | Note |
|---|---|---|---|
| three | 0.186.1 | MIT | hero 3D (solo livello CINEMATICO) |
| lenis | 1.3.26 | MIT | scorrimento fluido (solo CINEMATICO, solo con puntatore fine) |
| gsap (+ ScrollTrigger) | 3.15.0 | GreenSock "Standard No-Charge License" | vedi avvertenza sotto |

### ⚠️ Licenza GSAP — NON verificata in questa sessione
- Il pacchetto npm dichiara: `Standard 'no charge' license: https://gsap.com/standard-license`. Il README del pacchetto riporta "Copyright (c) 2008-2026, GreenSock. All rights reserved" e rimanda allo stesso URL.
- **Il testo della licenza non è stato letto:** gsap.com è bloccato dalla rete di questo ambiente e il repository GitHub `greensock/GSAP` (commit `13e2b79`) non contiene un file di licenza.
- Da conoscenza generale (da verificare): dopo l'acquisizione da parte di Webflow, GSAP e i suoi plugin sono gratuiti anche per uso commerciale. La licenza però contiene restrizioni per prodotti che **competono con gli strumenti visuali di Webflow** (costruttori di siti/animazioni no-code).
  - I siti consegnati ai clienti dovrebbero rientrare nell'uso consentito.
  - **Atelier come servizio che produce siti** va valutato leggendo il testo ufficiale prima di venderlo.
- Mitigazione già pronta: GSAP è usato solo nel livello CINEMATICO e solo per comparse, scrub e quickTo. Il BASE non lo include. Sostituirlo con un'alternativa MIT richiede di modificare un solo file (`engine/src/scripts/cinematic.js`).

## Strumenti di build/test (non inclusi nei siti)
astro 7.3.7 (MIT), tailwindcss 4.3.3 e @tailwindcss/vite (MIT), lighthouse 13.5.0 (Apache-2.0), playwright 1.56.1 (Apache-2.0), chrome-launcher (Apache-2.0).

## Skill di terzi installate in `.claude/skills/`
Vedi `skills.lock` (repository, commit SHA, licenza) e `audit-skill.md` (esito dell'audit).
- **Apache-2.0:** frontend-design, webapp-testing.
- **MIT:** ai-ui-ux-motion-engine, i 24 pacchetti threejs-* di Impertio, gsap-scrolltrigger, react-three-fiber, threejs-webgl.

Nessun codice delle skill di terzi è copiato nei siti generati.

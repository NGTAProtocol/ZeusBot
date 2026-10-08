# Libreria di pattern (parole mie)

> **Provenienza:** questi pattern NON derivano da misure fatte in questa sessione: i siti premiati erano irraggiungibili (vedi `README.md`). Sono descritti con parole mie a partire da conoscenza generale del settore.
> Nessun codice, testo, immagine, shader, font o layout di terzi è stato copiato. Le implementazioni in `engine/` sono scritte da zero.
>
> **Costo di performance** (stima qualitativa): **B** = basso (CSS/IntersectionObserver), **M** = medio (JS su scroll, GSAP), **A** = alto (WebGL, video).
> "Usato da Atelier" indica se il pattern è implementato nella pipeline.

| # | Nome | Effetto | Tecnica | Costo | Fallback mobile / ridotto | Usato da Atelier |
|---|---|---|---|---|---|---|
| 1 | Racconto a scorrimento (scroll narrativo) | La pagina avanza come capitoli: il titolo di sezione resta fermo mentre il contenuto scorre e cambia | GSAP ScrollTrigger con `pin` + timeline legata allo scroll (`scrub`) | M | Senza pin: capitoli impilati con comparsa semplice; reduced-motion: nessuna animazione | ✅ CINEMATICO |
| 2 | Scorrimento fluido | Inerzia morbida della rotella | Lenis che pilota il ticker di GSAP | B–M | Disattivato su touch, con reduced-motion e con Save-Data | ✅ CINEMATICO |
| 3 | Titolo rivelato per righe | Le righe del titolo emergono da una maschera | Split in righe/parole lato build, `clip-path` o `overflow:hidden` + translate | B | Testo visibile da subito (nessun contenuto nascosto senza JS) | ✅ tutti i livelli |
| 4 | Testo che reagisce al cursore | Le lettere vicine al puntatore cambiano peso/spaziatura | Font variabile + distanza dal puntatore in `requestAnimationFrame`, solo su `pointer:fine` | M | Nessun effetto su touch; reduced-motion: spento | ✅ CINEMATICO |
| 5 | Menu che si trasforma | Il menu esteso si compatta in una "capsula" dopo l'hero; su mobile si apre a pagina intera | Classe di stato su scroll (IntersectionObserver sull'hero) + transizioni CSS | B | Su mobile c'è sempre il pulsante "Menu" con overlay accessibile (focus trap, Esc) | ✅ tutti i livelli |
| 6 | Hero 3D procedurale | Oggetto o campo generato da codice che risponde a scroll e puntatore | Three.js con geometria + `ShaderMaterial` (rumore nei vertici, fresnel); caricato in differita dopo il primo rendering | A | Poster SVG procedurale con la stessa palette se WebGL manca, con dispositivo debole, Save-Data o reduced-motion | ✅ CINEMATICO |
| 7 | Grana e distorsione leggera | Una grana fine unifica 3D e fondi piatti e toglie l'aspetto "vettoriale da template" | Rumore nello shader + overlay SVG `feTurbulence` con `mix-blend-mode` | B | Overlay statico (senza animazione) con reduced-motion | ✅ CINEMATICO (grana statica nel BASE) |
| 8 | Contatori e dati che "si assestano" | I numeri chiave arrivano al valore finale | Interpolazione numerica all'ingresso nel viewport | B | Valore finale subito visibile | ✅ dove ci sono dati |
| 9 | Nastro di testo (marquee) | Una parola chiave scorre in loop | Animazione CSS su traccia duplicata, `aria-hidden` sul duplicato | B | Fermo con reduced-motion | ✅ in alcune direzioni |
| 10 | Transizione di colore tra capitoli | Lo sfondo cambia tono quando si entra in una sezione | ScrollTrigger che aggiorna variabili CSS | B–M | Sezioni con il proprio colore statico | ✅ CINEMATICO |
| 11 | Audio d'ambiente opzionale | Suono di sottofondo attivabile dall'utente | WebAudio procedurale (oscillatori + filtro), **spento di default**, interruttore con stato `aria-pressed` | B | Nessun audio senza un gesto esplicito | ✅ CINEMATICO |
| 12 | Video/sequenza legata allo scroll | Un filmato avanza con lo scroll | Video all-intra o sequenza di frame su canvas | A | Poster + video breve in autoplay muto, oppure solo immagine | ⏸ VIDEO-SCROLL: implementato solo con asset forniti dal cliente (nessun media generato) |
| 13 | Cursore personalizzato | Il puntatore diventa un elemento grafico | Elemento che segue il puntatore | M | — | ❌ escluso: spesso peggiora usabilità e accessibilità |
| 14 | Preloader a percentuale | Schermata di caricamento con contatore | — | – | — | ❌ escluso: ritarda LCP e contenuto |

## Regole trasversali
- Contenuto e azioni devono funzionare **senza JavaScript e senza movimento**: le animazioni partono da uno stato già leggibile.
- Un solo "momento firma" per pagina: l'hero nel CINEMATICO, la tipografia nel BASE. Il resto resta calmo.
- WebGL e GSAP si caricano **dopo** il primo rendering e solo se servono (import dinamico), per proteggere LCP e TBT su mobile.

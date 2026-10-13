# Il tuo sito d'artista: cosa c'è e cosa manca

**Dove si trova:**
- testi in `content/artista-a.json`;
- scelte di stile in `bibbia/artista-a.json`;
- foto in `assets/artista/`;
- sito pronto in `output/artista-a-base/` (consigliato) e `output/artista-a-cinematic/`.

## L'idea
- **Concept:** «Per una vita i quadri sono rimasti girati verso il muro, ed è servita una figlia pittrice per voltarli.»
- **Firma:** il primo quadro appare **dal retro** (telaio e tela grezza) e, mentre si scorre, **si volta** e mostra il dipinto, lo stesso gesto di tua figlia.
- **Stile:**
  - lo sfondo a quadretti richiama la carta millimetrata del geometra;
  - i titoli hanno un lettering tecnico; la storia è in un carattere da libro;
  - i colori vengono dalle tue foto: parete bianca, giacca nera, ocra delle lenti, blu del pannello.

## Da sostituire (segnaposto tra parentesi quadre)
| Dove | Cosa serve |
|---|---|
| Nome (`brand.name`, titolo, alt delle foto, footer) | il tuo nome, o un nome d'arte |
| Contatti (sezione "Vedere un quadro dal vero") | email, telefono o Instagram |
| Città | la tua città o zona |
| `meta.url` | il dominio, quando lo avrai |
| Opera "Senza titolo" | titolo, anno, tecnica, misure |

## Da approvare: la storia è inventata, come hai chiesto
**Fatti tuoi:**
- dipingi da sempre;
- hai il diploma da geometra;
- non hai mai mostrato le opere;
- tua figlia ha la stessa passione e ti ha spinto a mostrarle;
- ora le metti a disposizione della comunità.

**Inventato da me:**
- i disegni sui margini dei quaderni e sul retro delle buste;
- "righello di giorno, colore di sera";
- le tele appoggiate al muro con il dipinto verso l'intonaco;
- tua figlia che le gira «senza chiedermi il permesso»;
- «lo stesso modo di stare in piedi davanti alla tela».

Correggi o togli quello che non è vero. Non ho messo date, numeri né nomi inventati.

## Le foto
- **Le tue 3 immagini erano screenshot del telefono.** Ho tagliato barra di stato e pulsanti e le ho convertite in WebP + JPG in più dimensioni.
- **L'unica opera del sito** è il quadro astratto alle tue spalle nella foto dello studio, ritagliato. È piccolo (311 × 400 px) e in prospettiva: va sostituito con una foto dritta.
- **Il fotomontaggio in piscina** è nella sezione "Anche l'acqua si può dipingere", con la didascalia "Fotomontaggio.".

**Per aggiungere un'opera:**
1. Fotografala dritta, con luce uniforme, senza riflessi.
2. Mandamela, oppure mettila in `assets/artista/` come `opera-02-800.webp` e `opera-02-800.jpg`.
3. Aggiungi la sua voce in `media` e in `items` della sezione "Le opere".

## Pubblicazione gratuita
- **Cartella da pubblicare:** `output/artista-a-base/`, statica e senza servizi esterni.
- **Dove:** Cloudflare Pages, Vercel o GitHub Pages (vedi il README).
- **Modulo di contatto:** nessuno, per ora. Un modulo vero richiede un servizio esterno, e quindi la tua scelta.

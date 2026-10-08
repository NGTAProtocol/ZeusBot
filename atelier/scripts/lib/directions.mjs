// 8 direzioni artistiche originali di Atelier.
// Ogni direzione: palette (verificata AA nei test), coppia di font OFL (max 2 famiglie),
// spaziature, linguaggio di movimento, archetipo di layout, motivo 3D procedurale, tono del testo.

export const DIRECTIONS = [
  {
    id: 'argilla',
    name: 'Argilla notturna',
    fit: ['artigianato', 'ceramica', 'design', 'materia', 'lusso discreto', 'sensoriale', 'caldo'],
    palette: { bg: '#2b1e18', surface: '#3a2a22', ink: '#f1e7da', muted: '#c9b8a6', accent: '#8cc0dc', accent2: '#e2b85c' },
    fonts: {
      display: { family: 'Young Serif', pkg: '@fontsource/young-serif', weights: [400], fallback: 'Georgia, serif' },
      body: { family: 'Hanken Grotesk', pkg: '@fontsource/hanken-grotesk', weights: [400, 600], fallback: 'system-ui, sans-serif' }
    },
    type: { scale: 1.333, displayTracking: '-0.02em', displayLeading: 0.98, bodySize: '1.0625rem', bodyLeading: 1.65 },
    space: { unit: 8, section: 'clamp(6rem, 14vw, 12rem)', gutter: 'clamp(1.25rem, 4vw, 3rem)', measure: '34rem' },
    radius: '2px',
    motion: { language: 'maschera che sale, lenta e pesante come materia', ease: 'expo.out', duration: 1.4, stagger: 0.09, distance: 40 },
    layout: 'editorial',
    hero3d: { motif: 'blob', params: { glaze: true, speed: 0.18, detail: 64 } },
    tone: 'sensoriale e concreto: nomina materiali, gesti e tempi; frasi brevi; niente superlativi'
  },
  {
    id: 'quota',
    name: 'Quota',
    fit: ['montagna', 'outdoor', 'sport', 'turismo', 'avventura', 'tecnico', 'natura'],
    palette: { bg: '#e9eff3', surface: '#d6e1e8', ink: '#102a38', muted: '#3d5566', accent: '#a3370f', accent2: '#1d6fa5' },
    fonts: {
      display: { family: 'Archivo Variable', pkg: '@fontsource-variable/archivo', weights: ['wdth'], variable: true, fallback: 'Arial Narrow, sans-serif' },
      body: { family: 'Literata', pkg: '@fontsource/literata', weights: [400, 600], fallback: 'Georgia, serif' }
    },
    type: { scale: 1.414, displayTracking: '-0.01em', displayLeading: 0.92, bodySize: '1.0625rem', bodyLeading: 1.7, displayStretch: '125%', displayWeight: 800, charWidth: 0.74 },
    space: { unit: 8, section: 'clamp(5rem, 12vw, 10rem)', gutter: 'clamp(1.25rem, 4vw, 3.5rem)', measure: '36rem' },
    radius: '0px',
    motion: { language: 'curve di livello che scorrono; numeri che si assestano come un altimetro', ease: 'power3.inOut', duration: 1.1, stagger: 0.06, distance: 24 },
    layout: 'panels',
    hero3d: { motif: 'terrain', params: { speed: 0.12, contour: 14 } },
    tone: 'tecnico ed essenziale: quote, tempi e condizioni precise; seconda persona; nessuna retorica eroica'
  },
  {
    id: 'cifra',
    name: 'Cifra',
    fit: ['tecnologia', 'sicurezza', 'software', 'b2b', 'consulenza', 'dati', 'preciso'],
    palette: { bg: '#0e1a2b', surface: '#16263c', ink: '#e6edf5', muted: '#a8b6c8', accent: '#ffb547', accent2: '#6fd3c9' },
    fonts: {
      display: { family: 'Familjen Grotesk', pkg: '@fontsource/familjen-grotesk', weights: [500, 700], fallback: 'system-ui, sans-serif' },
      body: { family: 'Newsreader', pkg: '@fontsource/newsreader', weights: [400, 600], fallback: 'Georgia, serif' }
    },
    type: { scale: 1.25, displayTracking: '-0.025em', displayLeading: 1.0, bodySize: '1.125rem', bodyLeading: 1.6, displayWeight: 700 },
    space: { unit: 8, section: 'clamp(5rem, 11vw, 9rem)', gutter: 'clamp(1.25rem, 4vw, 3rem)', measure: '38rem' },
    radius: '6px',
    motion: { language: 'decifrazione: il testo si compone da caratteri casuali; reticolo che si accende per punti', ease: 'power2.out', duration: 0.9, stagger: 0.04, distance: 16 },
    layout: 'index',
    hero3d: { motif: 'points', params: { arrangement: 'lattice', speed: 0.1, count: 2400 } },
    tone: 'calmo e preciso: spiega rischi senza allarmismo, frasi dichiarative, esempi concreti'
  },
  {
    id: 'salmastro',
    name: 'Salmastro',
    fit: ['ristorazione', 'ospitalità', 'mare', 'cibo', 'conviviale', 'vacanza', 'famiglia'],
    palette: { bg: '#dde8e1', surface: '#c8dacf', ink: '#10302b', muted: '#365751', accent: '#9a301b', accent2: '#2f7d6d' },
    fonts: {
      display: { family: 'Fraunces', pkg: '@fontsource/fraunces', weights: [600, 900], fallback: 'Georgia, serif' },
      body: { family: 'Manrope', pkg: '@fontsource/manrope', weights: [400, 600], fallback: 'system-ui, sans-serif' }
    },
    type: { scale: 1.333, displayTracking: '-0.015em', displayLeading: 0.95, bodySize: '1.0625rem', bodyLeading: 1.65, displayWeight: 900 },
    space: { unit: 8, section: 'clamp(5rem, 12vw, 10rem)', gutter: 'clamp(1.25rem, 5vw, 4rem)', measure: '34rem' },
    radius: '18px',
    motion: { language: 'deriva lenta come la risacca; elementi che ondeggiano appena', ease: 'sine.inOut', duration: 1.6, stagger: 0.1, distance: 30 },
    layout: 'panels',
    hero3d: { motif: 'ribbons', params: { speed: 0.16, count: 26 } },
    tone: 'conviviale e caldo: piatti, orari e luoghi con il loro nome; prima persona plurale'
  },
  {
    id: 'manifesto',
    name: 'Manifesto',
    fit: ['moda', 'agenzia', 'creativo', 'musica', 'eventi', 'audace', 'giovane'],
    palette: { bg: '#f0d34a', surface: '#e7c52c', ink: '#1d1b16', muted: '#3b382d', accent: '#1d1b16', accent2: '#9e2a1a' },
    fonts: {
      display: { family: 'Syne', pkg: '@fontsource/syne', weights: [700, 800], fallback: 'system-ui, sans-serif' },
      body: { family: 'Work Sans', pkg: '@fontsource/work-sans', weights: [400, 600], fallback: 'system-ui, sans-serif' }
    },
    type: { scale: 1.5, displayTracking: '-0.03em', displayLeading: 0.88, bodySize: '1.0625rem', bodyLeading: 1.55, displayWeight: 800, charWidth: 0.64 },
    space: { unit: 8, section: 'clamp(4rem, 10vw, 8rem)', gutter: 'clamp(1rem, 3vw, 2.5rem)', measure: '32rem' },
    radius: '0px',
    motion: { language: 'tipografia cinetica a tagli netti; nessuna dissolvenza morbida', ease: 'power4.out', duration: 0.7, stagger: 0.05, distance: 60 },
    layout: 'manifesto',
    hero3d: { motif: 'blob', params: { chrome: true, speed: 0.3, detail: 48 } },
    tone: 'diretto e imperativo: frasi corte, verbi forti, nessuna parola di riempimento'
  },
  {
    id: 'archivio',
    name: 'Archivio',
    fit: ['legale', 'cultura', 'editoria', 'museo', 'storia', 'istituzionale', 'autorevole'],
    palette: { bg: '#dcd9d1', surface: '#cfcbc1', ink: '#23262c', muted: '#474a52', accent: '#7a2232', accent2: '#2f4a6b' },
    fonts: {
      display: { family: 'Cormorant Garamond', pkg: '@fontsource/cormorant-garamond', weights: [500, 700], fallback: 'Garamond, serif' },
      body: { family: 'Instrument Sans', pkg: '@fontsource/instrument-sans', weights: [400, 600], fallback: 'system-ui, sans-serif' }
    },
    type: { scale: 1.414, displayTracking: '-0.01em', displayLeading: 1.0, bodySize: '1.0625rem', bodyLeading: 1.7, displayWeight: 500 },
    space: { unit: 8, section: 'clamp(5rem, 12vw, 10rem)', gutter: 'clamp(1.25rem, 5vw, 4rem)', measure: '36rem' },
    radius: '0px',
    motion: { language: 'voltare pagina: maschere orizzontali lente, nessun rimbalzo', ease: 'power2.inOut', duration: 1.2, stagger: 0.08, distance: 0 },
    layout: 'catalogue',
    hero3d: { motif: 'ribbons', params: { sheets: true, speed: 0.08, count: 14 } },
    tone: 'autorevole e misurato: frasi complete, termini esatti, nessuno slogan'
  },
  {
    id: 'serra',
    name: 'Serra',
    fit: ['benessere', 'botanica', 'salute', 'cura', 'sostenibile', 'lento', 'naturale'],
    palette: { bg: '#22312a', surface: '#2c3e35', ink: '#ecf1e4', muted: '#b9c6b0', accent: '#e6c85e', accent2: '#9ccf8f' },
    fonts: {
      display: { family: 'Bricolage Grotesque', pkg: '@fontsource/bricolage-grotesque', weights: [500, 700], fallback: 'system-ui, sans-serif' },
      body: { family: 'Libre Caslon Text', pkg: '@fontsource/libre-caslon-text', weights: [400, 700], fallback: 'Georgia, serif' }
    },
    type: { scale: 1.333, displayTracking: '-0.02em', displayLeading: 0.98, bodySize: '1.0625rem', bodyLeading: 1.75, displayWeight: 700 },
    space: { unit: 8, section: 'clamp(6rem, 14vw, 12rem)', gutter: 'clamp(1.25rem, 5vw, 4rem)', measure: '32rem' },
    radius: '999px',
    motion: { language: 'crescita: elementi che si aprono dal centro, ritmo di respiro', ease: 'power1.inOut', duration: 1.8, stagger: 0.12, distance: 20 },
    layout: 'monolith',
    hero3d: { motif: 'points', params: { arrangement: 'phyllotaxis', speed: 0.06, count: 1800 } },
    tone: 'lento e caldo: descrive sensazioni e tempi, mai promesse mediche'
  },
  {
    id: 'officina',
    name: 'Officina',
    fit: ['industria', 'ingegneria', 'manifattura', 'architettura', 'logistica', 'concreto', 'costruzioni'],
    palette: { bg: '#1f3fc4', surface: '#2a4bd0', ink: '#f4f6ff', muted: '#d3dbff', accent: '#ffd23f', accent2: '#ffffff' },
    fonts: {
      display: { family: 'Space Grotesk', pkg: '@fontsource/space-grotesk', weights: [500, 700], fallback: 'system-ui, sans-serif' },
      body: { family: 'IBM Plex Sans', pkg: '@fontsource/ibm-plex-sans', weights: [400, 600], fallback: 'system-ui, sans-serif' }
    },
    type: { scale: 1.333, displayTracking: '-0.02em', displayLeading: 0.96, bodySize: '1.0625rem', bodyLeading: 1.6, displayWeight: 700 },
    space: { unit: 8, section: 'clamp(5rem, 11vw, 9rem)', gutter: 'clamp(1.25rem, 4vw, 3rem)', measure: '36rem' },
    radius: '0px',
    motion: { language: 'disegno tecnico: linee che si tracciano, movimenti lineari e precisi', ease: 'none', duration: 0.9, stagger: 0.05, distance: 0 },
    layout: 'blueprint',
    hero3d: { motif: 'rings', params: { speed: 0.14, count: 7 } },
    tone: 'concreto e ingegneristico: misure, tolleranze, tempi di consegna; nessun gergo di marketing'
  }
];

export function getDirection(id) {
  const d = DIRECTIONS.find((x) => x.id === id);
  if (!d) throw new Error(`Direzione sconosciuta: ${id}`);
  return d;
}

/** Sceglie la direzione: esplicita nel brief, altrimenti la più affine a settore + tono. */
export function pickDirection(brief) {
  if (brief.direction) return getDirection(brief.direction);
  const text = [brief.sector, brief.tone, brief.business, brief.audience].join(' ').toLowerCase();
  let best = DIRECTIONS[0];
  let bestScore = -1;
  for (const d of DIRECTIONS) {
    const s = d.fit.reduce((acc, k) => acc + (text.includes(k) ? 1 : 0), 0);
    if (s > bestScore) {
      best = d;
      bestScore = s;
    }
  }
  return best;
}

// ---- contrasto WCAG ----
function lum(hex) {
  const n = hex.replace('#', '');
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(n.slice(i, i + 2), 16) / 255).map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
export function contrast(a, b) {
  const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);
  return (x + 0.05) / (y + 0.05);
}

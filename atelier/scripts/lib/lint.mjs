// Lista nera dei cliché + controlli sui contenuti (struttura e copy).
export const BANNED_PHRASES = [
  /lorem ipsum/i, /dolor sit amet/i,
  /soluzion[ei] innovativ[ei]/i, /a 360 gradi/i, /leader (del|nel) settore/i, /eccellenza/i, /all'avanguardia/i,
  /benvenut[io] (nel|sul) (nostro )?sito/i, /la nostra passione/i, /qualità e professionalità/i, /il partner ideale/i,
  /scopri di più/i, /clicca qui/i, /unlock|seamless|cutting-edge|elevate your/i
];

// ripetizioni tipiche dei siti generati (vedi anche frontend-design)
export const BANNED_PATTERNS = [
  { re: /→\s*$/, why: 'freccia "→" appesa al testo di link/bottoni' },
  { re: /\s·\s.*\s·\s/, why: 'stringhe di metadati unite da punti centrali "A · B · C"' }
];

function walkStrings(obj, path = '', out = []) {
  if (typeof obj === 'string') out.push([path, obj]);
  else if (Array.isArray(obj)) obj.forEach((v, i) => walkStrings(v, `${path}[${i}]`, out));
  else if (obj && typeof obj === 'object') for (const [k, v] of Object.entries(obj)) walkStrings(v, path ? `${path}.${k}` : k, out);
  return out;
}

const IT_WORDS = /\b(il|la|di|che|per|non|una|con|del|della|sono|nel|alla|gli|le)\b/gi;

export function lintContent(c, brief) {
  const problems = [];
  const need = ['meta.title', 'meta.description', 'brand.name', 'cta.label', 'cta.href', 'footer.email', 'footer.closing', 'pages.home.hero.title_lines', 'pages.home.hero.lead', 'pages.home.hero.lead_short', 'pages.home.sections'];
  for (const k of need) {
    const v = k.split('.').reduce((o, p) => (o ? o[p] : undefined), c);
    if (v === undefined || v === '' || (Array.isArray(v) && !v.length)) problems.push(`campo mancante: ${k}`);
  }
  if (problems.length) return problems;
  if (c.meta.lang !== brief.language) problems.push(`meta.lang (${c.meta.lang}) diverso dalla lingua del brief (${brief.language})`);
  if (c.meta.description.length < 70 || c.meta.description.length > 165) problems.push('meta.description: 70-165 caratteri');
  for (const p of brief.pages) if (!c.pages[p]) problems.push(`pagina richiesta dal brief mancante: ${p}`);

  const strings = walkStrings(c);
  for (const [path, s] of strings) {
    for (const re of BANNED_PHRASES) if (re.test(s)) problems.push(`cliché vietato in ${path}: "${s.match(re)[0]}"`);
    for (const { re, why } of BANNED_PATTERNS) if (re.test(s)) problems.push(`${why} in ${path}`);
  }
  // lingua: il testo lungo deve essere nella lingua del cliente
  if (brief.language === 'it') {
    const body = strings.map(([, s]) => s).join(' ');
    const hits = (body.match(IT_WORDS) || []).length;
    const words = body.split(/\s+/).length;
    if (hits / words < 0.08) problems.push('il testo non sembra in italiano');
  }
  // il nome dell'attività deve comparire: copy specifico, non generico
  const all = strings.map(([, s]) => s).join(' ').toLowerCase();
  const name = c.brand.name.toLowerCase();
  if ((all.match(new RegExp(name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length < 3) problems.push('il nome dell\'attività compare meno di 3 volte: copy troppo generico');
  // niente "tre card con icone uguali": tipo di sezione non previsto
  for (const s of c.pages.home.sections) {
    if (['cards', 'features', 'icons'].includes(s.type)) problems.push(`tipo di sezione vietato (cliché a card): ${s.type}`);
    if (s.type === 'offer' && s.items?.length === 3 && s.items.every((i) => i.detail && i.detail.length < 60)) problems.push('offerta con 3 voci brevi e uguali: rischio "tre card"');
  }
  const h = c.pages.home.hero;
  if (h.title_lines.join(' ').length > 70) problems.push('titolo hero oltre 70 caratteri');
  if (h.lead_short.length > 120) problems.push('lead_short oltre 120 caratteri (versione mobile)');
  return problems;
}

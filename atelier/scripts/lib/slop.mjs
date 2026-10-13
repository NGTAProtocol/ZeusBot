// Rilevatore automatico di "slop" sull'HTML COMPILATO (vale per tutte le configurazioni, baseline compresa).
// Conta segnali misurabili della lista nera della Bibbia (§10) e i link finti (§9). Non giudica il gusto.
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const CHECKS = [
  { id: 'testo-gradiente', re: /bg-clip-text|background-clip:\s*text/g },
  { id: 'gradiente-viola-indaco', re: /from-(indigo|purple|violet)-\d+|to-(indigo|purple|violet)-\d+/g },
  { id: 'emoji', re: /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu },
  { id: 'freccia-nei-bottoni', re: />[^<]{0,40}→\s*</g },
  { id: 'eyebrow-maiuscolo', re: /class="[^"]*\buppercase\b[^"]*tracking-(wide|wider|widest)/g },
  { id: 'card-con-ombra-ripetute', re: /class="[^"]*rounded-(xl|2xl|3xl)[^"]*shadow/g },
  { id: 'frasi-vuote', re: /scopri di più|soluzioni innovative|a 360 gradi|eccellenza|la nostra passione|pronto a [a-z]+ (la tua|il tuo)|non aspettare/gi },
  { id: 'animazione-infinita', re: /animation[^;"]*infinite|animate-(pulse|bounce|spin|ping)\b/g }
];

function linkProblems(html) {
  const ids = new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]));
  let fake = 0;
  for (const [, h] of html.matchAll(/<a\b[^>]*\shref="([^"]*)"/g)) {
    if (h === '#' || h === '') fake++;
    else if (h.startsWith('#') && !ids.has(h.slice(1))) fake++;
  }
  return fake;
}

export function slopReport(outDir) {
  const html = readdirSync(outDir, { recursive: true }).filter((f) => f.endsWith('.html')).map((f) => readFileSync(join(outDir, f), 'utf8')).join('\n');
  const hits = Object.fromEntries(CHECKS.map((c) => [c.id, (html.match(c.re) || []).length]));
  hits['link-finti'] = linkProblems(html);
  hits.totale = Object.values(hits).reduce((a, b) => a + b, 0);
  return hits;
}

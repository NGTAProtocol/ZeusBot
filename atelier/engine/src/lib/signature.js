// Firme CSS/SVG procedurali (scritte per Atelier). Ogni firma è un SVG con gruppi [data-sig-part]
// che si muovono SOLO con transform (scroll o puntatore): nel BASE con le animazioni CSS legate allo scroll,
// nel CINEMATICO con GSAP. I parametri vengono dal file Bibbia (signature.params) e dalla palette.
import { rng, seedFrom, noise1 } from './rand.js';

const f = (n) => Number(n.toFixed(1));

function smoothClosed(pts) {
  const n = pts.length;
  let d = `M${f(pts[0][0])} ${f(pts[0][1])}`;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += `C${f(c1[0])} ${f(c1[1])} ${f(c2[0])} ${f(c2[1])} ${f(p2[0])} ${f(p2[1])}`;
  }
  return d + 'Z';
}

// strati sovrapposti (smalti, manto nevoso…) che si separano con lo scroll
function layers(p, r, W, H, q) {
  const count = q.count || 5;
  const cols = [p.accent2, p.surface, p.accent, p.muted, p.ink];
  const out = [];
  const n = noise1(Math.floor(r() * 1e6));
  for (let l = 0; l < count; l++) {
    const k = l / (count - 1 || 1);
    const pts = [];
    const top = H * (0.18 + k * 0.5);
    const amp = H * (q.amp || 0.08) * (1 - k * 0.4);
    for (let i = 0; i <= 24; i++) pts.push([(i / 24) * W, top + (n(i * 0.35 + l * 2.1) - 0.5) * 2 * amp]);
    const d = `M${pts.map(([x, y]) => `${f(x)} ${f(y)}`).join('L')}L${W} ${H + 80}L0 ${H + 80}Z`;
    out.push(`<g data-sig-part style="--rise:${f(-(count - l) * (q.spread || 22))}px"><path d="${d}" fill="${cols[l % cols.length]}" opacity="${f(0.55 + k * 0.45)}"/></g>`);
  }
  return out.join('');
}

// colatura: una fascia di smalto da cui scendono gocce di lunghezza diversa
function drip(p, r, W, H, q) {
  const count = q.count || 14;
  const band = H * (q.band || 0.22);
  const out = [`<path d="M0 0H${W}V${f(band)}H0Z" fill="${p.accent2}"/>`];
  for (let i = 0; i < count; i++) {
    const x = (W / count) * (i + 0.2 + r() * 0.6);
    const w = 14 + r() * (q.width || 34);
    const len = H * (0.25 + r() * 0.55);
    const d = `M${f(x - w / 2)} ${f(band - 2)}V${f(band + len - w / 2)}A${f(w / 2)} ${f(w / 2)} 0 0 0 ${f(x + w / 2)} ${f(band + len - w / 2)}V${f(band - 2)}Z`;
    const col = i % 4 === 0 ? p.accent : p.accent2;
    out.push(`<g data-sig-part style="--from:${f(0.08 + r() * 0.25)}"><path d="${d}" fill="${col}"/></g>`);
  }
  return out.join('');
}

// curve di livello: fasce di isoipse che salgono a velocità diverse (si "guadagna quota")
function contours(p, r, W, H, q) {
  const rows = q.rows || 24;
  const groups = q.groups || 4;
  const n = noise1(Math.floor(r() * 1e6));
  const peakX = W * (q.peak ?? 0.62);
  const parts = Array.from({ length: groups }, () => []);
  for (let j = 0; j < rows; j++) {
    const y0 = H * 0.3 + (j / rows) * H * 0.68;
    const pts = [];
    for (let x = 0; x <= W; x += W / 70) {
      const peak = Math.exp(-(((x - peakX) / (W * 0.22)) ** 2));
      const h = (n(x * 0.011 + j * 0.31) * 0.55 + peak) * H * 0.24 * (1 - (j / rows) * 0.55);
      pts.push(`${f(x)} ${f(y0 - h)}`);
    }
    const major = j % 5 === 0;
    parts[j % groups].push(`<path d="M${pts.join('L')}" fill="none" stroke="${major ? p.accent : p.ink}" stroke-width="${major ? 1.8 : 0.8}" opacity="${major ? 0.95 : 0.5}"/>`);
  }
  return parts.map((g, i) => `<g data-sig-part style="--rise:${f(-(groups - i) * (q.spread || 18))}px">${g.join('')}</g>`).join('');
}

// reticolo: segmenti che partono disordinati e si allineano (scroll) o si orientano verso il puntatore
function lattice(p, r, W, H, q) {
  const cols = q.cols || 22;
  const rows = q.rows || 14;
  const out = [];
  const sx = W / cols;
  const sy = H / rows;
  const len = Math.min(sx, sy) * 0.72;
  for (let y = 0; y < rows; y++)
    for (let x = 0; x < cols; x++) {
      const cx = sx * (x + 0.5);
      const cy = sy * (y + 0.5);
      const hot = r() < (q.hot || 0.06);
      const rot = Math.round((r() - 0.5) * 2 * (q.chaos || 70));
      out.push(`<g data-sig-part style="--rot:${rot}deg"><line x1="${f(cx - len / 2)}" y1="${f(cy)}" x2="${f(cx + len / 2)}" y2="${f(cy)}" stroke="${hot ? p.accent : p.ink}" stroke-width="${hot ? 5 : 2.6}" stroke-linecap="round" opacity="${hot ? 1 : 0.7}"/></g>`);
    }
  return out.join('');
}

export const SIGNATURES = { layers, drip, contours, lattice };

/** SVG della firma CSS `id` (per una firma 3D si passa il suo fallback_id). */
export function signatureSvg(id, palette, seedText, params = {}, { W = 1200, H = 900 } = {}) {
  const draw = SIGNATURES[id] || layers;
  const r = rng(seedFrom(seedText + id));
  return `<svg class="sig sig--${id}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">${draw(palette, r, W, H, params)}</svg>`;
}

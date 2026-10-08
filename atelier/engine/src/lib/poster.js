// Poster SVG procedurale: hero del livello BASE e fallback del CINEMATICO
// (WebGL assente, dispositivo debole, Save-Data, prefers-reduced-motion).
import { rng, seedFrom, noise1 } from './rand.js';

const f = (n) => Number(n.toFixed(1));

// curva chiusa liscia (Catmull-Rom → Bézier cubiche) attraverso i punti
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

function blob(p, r, W, H) {
  const layers = [];
  for (let l = 0; l < 4; l++) {
    const cx = W * (0.55 + (r() - 0.5) * 0.1);
    const cy = H * (0.5 + (r() - 0.5) * 0.1);
    const base = Math.min(W, H) * (0.34 - l * 0.06);
    const n = noise1(Math.floor(r() * 1e6));
    const pts = [];
    for (let i = 0; i < 18; i++) {
      const a = (i / 18) * Math.PI * 2;
      const rad = base * (0.84 + n(i * 0.55 + l * 3) * 0.3);
      pts.push([cx + Math.cos(a) * rad, cy + Math.sin(a) * rad]);
    }
    layers.push(`<path d="${smoothClosed(pts)}" fill="${[p.accent, p.surface, p.accent2, p.muted][l]}" opacity="${[0.9, 0.85, 0.55, 0.25][l]}"/>`);
  }
  return layers.join('');
}

function terrain(p, r, W, H) {
  const lines = [];
  const rows = 26;
  const n = noise1(Math.floor(r() * 1e6));
  for (let j = 0; j < rows; j++) {
    const y0 = H * 0.25 + (j / rows) * H * 0.7;
    const pts = [];
    for (let x = 0; x <= W; x += W / 80) {
      const peak = Math.exp(-(((x - W * 0.6) / (W * 0.25)) ** 2));
      const h = (n(x * 0.012 + j * 0.37) * 0.6 + peak * 0.9) * H * 0.22 * (1 - j / rows * 0.6);
      pts.push(`${f(x)} ${f(y0 - h)}`);
    }
    lines.push(`<path d="M${pts.join('L')}" fill="none" stroke="${j % 5 === 0 ? p.accent : p.ink}" stroke-width="${j % 5 === 0 ? 1.6 : 0.7}" opacity="${j % 5 === 0 ? 0.95 : 0.45}"/>`);
  }
  return lines.join('');
}

function points(p, r, W, H, params) {
  const out = [];
  if (params.arrangement === 'phyllotaxis') {
    const N = 520;
    const cx = W * 0.58;
    const cy = H * 0.5;
    const golden = Math.PI * (3 - Math.sqrt(5));
    for (let i = 0; i < N; i++) {
      const rad = Math.sqrt(i / N) * Math.min(W, H) * 0.42;
      const a = i * golden;
      out.push(`<circle cx="${f(cx + Math.cos(a) * rad)}" cy="${f(cy + Math.sin(a) * rad)}" r="${f(1 + (i / N) * 3.2)}" fill="${i % 7 === 0 ? p.accent : p.accent2}" opacity="${f(0.35 + (i / N) * 0.6)}"/>`);
    }
  } else {
    const n = noise1(Math.floor(r() * 1e6));
    for (let y = 0; y < 22; y++)
      for (let x = 0; x < 36; x++) {
        const px = (x / 35) * W;
        const py = H * 0.12 + (y / 21) * H * 0.8 + n(x * 0.3 + y) * 10;
        const v = n(x * 0.21 + y * 0.53);
        out.push(`<circle cx="${f(px)}" cy="${f(py)}" r="${f(0.8 + v * 2.4)}" fill="${v > 0.78 ? p.accent : p.accent2}" opacity="${f(0.25 + v * 0.7)}"/>`);
      }
  }
  return out.join('');
}

function ribbons(p, r, W, H, params) {
  const out = [];
  const count = params.sheets ? 12 : 22;
  for (let i = 0; i < count; i++) {
    const amp = H * (0.04 + r() * 0.08);
    const ph = r() * Math.PI * 2;
    const y0 = H * 0.2 + (i / count) * H * 0.65;
    const pts = [];
    for (let x = -20; x <= W + 20; x += W / 60) pts.push(`${f(x)} ${f(y0 + Math.sin(x * 0.006 + ph + i * 0.2) * amp)}`);
    out.push(
      params.sheets
        ? `<path d="M${pts.join('L')}L${W + 20} ${H}L-20 ${H}Z" fill="${i % 2 ? p.surface : p.bg}" stroke="${p.ink}" stroke-width="0.6" opacity="0.92"/>`
        : `<path d="M${pts.join('L')}" fill="none" stroke="${i % 6 === 0 ? p.accent : p.accent2}" stroke-width="${i % 6 === 0 ? 2.2 : 1}" opacity="0.8"/>`
    );
  }
  return out.join('');
}

function rings(p, r, W, H, params) {
  const out = [];
  const cx = W * 0.6;
  const cy = H * 0.5;
  for (let i = 0; i < (params.count || 7); i++) {
    const rx = Math.min(W, H) * (0.12 + i * 0.05);
    const ry = rx * (0.35 + r() * 0.5);
    const rot = r() * 180;
    out.push(`<ellipse cx="${f(cx)}" cy="${f(cy)}" rx="${f(rx)}" ry="${f(ry)}" transform="rotate(${f(rot)} ${f(cx)} ${f(cy)})" fill="none" stroke="${i % 3 === 0 ? p.accent : p.accent2}" stroke-width="${i % 3 === 0 ? 2 : 1}" stroke-dasharray="${i % 2 ? '4 6' : 'none'}" opacity="0.9"/>`);
  }
  out.push(`<line x1="0" y1="${f(cy)}" x2="${W}" y2="${f(cy)}" stroke="${p.muted}" stroke-width="0.6" opacity="0.6"/>`);
  out.push(`<line x1="${f(cx)}" y1="0" x2="${f(cx)}" y2="${H}" stroke="${p.muted}" stroke-width="0.6" opacity="0.6"/>`);
  return out.join('');
}

const MOTIFS = { blob, terrain, points, ribbons, rings };

export function posterSvg(direction, seedText) {
  const W = 1200;
  const H = 900;
  const r = rng(seedFrom(seedText + direction.id));
  const p = direction.palette;
  const draw = MOTIFS[direction.hero3d.motif] || blob;
  const body = draw(p, r, W, H, direction.hero3d.params || {});
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">${body}</svg>`;
}

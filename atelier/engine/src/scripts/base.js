// Livello BASE (incluso anche nel CINEMATICO): comparse, nav che si trasforma,
// menu mobile accessibile, barra CTA mobile, contatori. Nessuna libreria esterna.
const root = document.documentElement;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const cinematic = root.classList.contains('is-cinematic');

// --- comparse (nel CINEMATICO le gestisce GSAP, se caricato) ---
function revealWithObserver() {
  const els = document.querySelectorAll('[data-reveal], [data-reveal-lines]');
  if (reduce || !('IntersectionObserver' in window)) {
    els.forEach((el) => el.classList.add('is-in'));
    return;
  }
  const io = new IntersectionObserver(
    (entries) => entries.forEach((e) => {
      if (e.isIntersecting) {
        // una fila scorrevole (es. i dati su mobile) compare tutta insieme: i figli fuori schermo non intersecano mai
        const group = e.target.matches('.facts') ? e.target.querySelectorAll('[data-reveal]') : [e.target];
        group.forEach((el) => el.classList.add('is-in'));
        io.unobserve(e.target);
      }
    }),
    { rootMargin: '0px 0px -8% 0px', threshold: 0.12 }
  );
  els.forEach((el) => { if (!el.closest('.facts')) io.observe(el); });
  document.querySelectorAll('.facts').forEach((row) => io.observe(row));
}
if (!cinematic) revealWithObserver();
// il CINEMATICO lo richiama come ripiego (movimento ridotto / Save-Data)
window.__atelierReveal = revealWithObserver;

// --- nav compatta dopo l'hero + barra CTA mobile ---
const nav = document.querySelector('[data-nav]');
const mcta = document.querySelector('[data-mcta]');
const hero = document.querySelector('[data-hero]');
if (hero && 'IntersectionObserver' in window) {
  new IntersectionObserver(([e]) => {
    const past = !e.isIntersecting;
    nav?.classList.toggle('is-compact', past);
    if (mcta) {
      mcta.classList.toggle('is-on', past);
      mcta.setAttribute('aria-hidden', String(!past));
      mcta.querySelector('a')?.setAttribute('tabindex', past ? '0' : '-1');
    }
  }, { rootMargin: '-35% 0px 0px 0px' }).observe(hero);
} else {
  nav?.classList.add('is-compact');
}

// --- menu a pagina intera (mobile) ---
const menu = document.querySelector('[data-menu]');
const openBtn = document.querySelector('[data-menu-open]');
const closeBtn = document.querySelector('[data-menu-close]');
let lastFocus = null;
function setMenu(open) {
  if (!menu) return;
  if (open) {
    lastFocus = document.activeElement;
    menu.hidden = false;
    requestAnimationFrame(() => menu.classList.add('is-open'));
    openBtn?.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
    closeBtn?.focus();
  } else {
    menu.classList.remove('is-open');
    openBtn?.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
    setTimeout(() => { if (!menu.classList.contains('is-open')) menu.hidden = true; }, reduce ? 0 : 600);
    lastFocus?.focus?.();
  }
}
openBtn?.addEventListener('click', () => setMenu(true));
closeBtn?.addEventListener('click', () => setMenu(false));
menu?.querySelectorAll('[data-menu-link]').forEach((a) => a.addEventListener('click', () => setMenu(false)));
document.addEventListener('keydown', (e) => {
  if (!menu?.classList.contains('is-open')) return;
  if (e.key === 'Escape') setMenu(false);
  if (e.key === 'Tab') {
    const f = menu.querySelectorAll('a, button');
    const first = f[0];
    const last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }
});

// --- contatori: il valore finale è già nel DOM; l'animazione è solo decorativa ---
if (!reduce && 'IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (!e.isIntersecting) return;
    io.unobserve(e.target);
    const raw = e.target.dataset.count;
    const target = parseFloat(String(raw).replace(',', '.'));
    if (!Number.isFinite(target) || /[^\d.,]/.test(raw)) return;
    const decimals = (String(raw).split(/[.,]/)[1] || '').length;
    const t0 = performance.now();
    const step = (t) => {
      const k = Math.min(1, (t - t0) / 1400);
      const v = target * (1 - Math.pow(1 - k, 3));
      e.target.textContent = v.toFixed(decimals).replace('.', raw.includes(',') ? ',' : '.');
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }), { threshold: 0.6 });
  document.querySelectorAll('[data-count]').forEach((el) => io.observe(el));
}

// --- indice di pagina (archetipo "index") ---
const indexLinks = document.querySelectorAll('.page-index a');
if (indexLinks.length && 'IntersectionObserver' in window) {
  const map = new Map([...indexLinks].map((a) => [a.getAttribute('href').slice(1), a]));
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (e.isIntersecting) {
      indexLinks.forEach((a) => a.removeAttribute('aria-current'));
      map.get(e.target.id)?.setAttribute('aria-current', 'true');
    } else if (e.boundingClientRect.top > 0 && map.get(e.target.id)?.hasAttribute('aria-current')) {
      map.get(e.target.id).removeAttribute('aria-current'); // risalendo sopra la sezione
    }
  }), { rootMargin: '-45% 0px -50% 0px' });
  map.forEach((_, id) => { const el = document.getElementById(id); if (el) io.observe(el); });
}

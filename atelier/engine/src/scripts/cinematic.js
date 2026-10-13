// Livello CINEMATICO: Lenis + GSAP/ScrollTrigger che pilotano la FIRMA del sito (dal file Bibbia).
// Three.js si carica solo se la firma è 3D (Bibbia §14.3) e solo al primo gesto dell'utente.
// Regole: solo transform/opacity, nessun loop infinito, tutto parte da scroll o puntatore.

const cfg = JSON.parse(document.getElementById('atelier-dir').textContent);
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const conn = navigator.connection || {};
const saveData = !!conn.saveData || /(^|-)2g$/.test(conn.effectiveType || '');
const lowMemory = typeof navigator.deviceMemory === 'number' && navigator.deviceMemory < 4;
const lowCpu = typeof navigator.hardwareConcurrency === 'number' && navigator.hardwareConcurrency < 4;
const finePointer = matchMedia('(pointer: fine)').matches;
const small = matchMedia('(max-width: 860px)').matches;
// parametri di diagnosi per il QA: ?no3d (niente WebGL), ?force3d (3D subito, senza attendere gesti)
const q = new URLSearchParams(location.search);
const hasWebGL = () => 'WebGLRenderingContext' in window;
const idle = (fn, timeout = 1200) => ('requestIdleCallback' in window ? requestIdleCallback(fn, { timeout }) : setTimeout(fn, 200));
const afterLoad = (fn) => (document.readyState === 'complete' ? fn() : addEventListener('load', fn, { once: true }));

if (reduce || saveData) {
  // ripiego: resta il BASE (contenuto già al suo posto, firma statica)
  window.__atelierReveal?.();
  document.documentElement.dataset.fallback = reduce ? 'reduced-motion' : 'save-data';
} else {
  initMotion();
  const host3d = __ATELIER_3D__ ? document.querySelector('[data-3d]') : null;
  if (__ATELIER_3D__ && host3d) {
    const can3d = hasWebGL() && !lowMemory && !lowCpu && !q.has('no3d');
    if (!can3d) document.documentElement.dataset.fallback = 'no-webgl-or-weak-device';
    else {
      const start = () => afterLoad(() => idle(() => startHero3d(host3d)));
      if (q.has('force3d')) start();
      else {
        let done = false;
        const go = () => { if (!done) { done = true; start(); } };
        ['pointermove', 'touchstart', 'scroll', 'keydown', 'wheel'].forEach((ev) => addEventListener(ev, go, { once: true, passive: true }));
      }
    }
  }
}

async function startHero3d(host) {
  if (!__ATELIER_3D__) return;
  const { mountHero } = await import('./hero3d.js');
  mountHero(host, { palette: cfg.palette, hero3d: { motif: cfg.sig.id, params: cfg.sig.params || {} } }, { mobile: small });
}

async function initMotion() {
  let gsap, ScrollTrigger;
  try {
    [{ gsap }, { ScrollTrigger }] = await Promise.all([import('gsap'), import('gsap/ScrollTrigger')]);
  } catch {
    window.__atelierReveal?.();
    return;
  }
  gsap.registerPlugin(ScrollTrigger);
  const { ease, dur: D, distance, stagger } = cfg.motion;

  if (finePointer) {
    const { default: Lenis } = await import('lenis');
    const lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  }

  // l'hero è leggibile dal primo frame: nessuna animazione al caricamento
  document.querySelector('.hero [data-reveal-lines]')?.classList.add('is-in');

  document.querySelectorAll('[data-reveal-lines]:not(.hero__title)').forEach((el) => {
    const lines = el.querySelectorAll('.mask-line > span');
    gsap.fromTo(lines, { yPercent: 105, y: 0 }, {
      yPercent: 0, y: 0, duration: D, ease, stagger,
      scrollTrigger: { trigger: el, start: 'top 88%', once: true },
      onStart: () => el.classList.add('is-in')
    });
  });
  gsap.utils.toArray('[data-reveal]').forEach((el) => {
    gsap.fromTo(el, { autoAlpha: 0, y: distance }, {
      autoAlpha: 1, y: 0, duration: D * 0.85, ease,
      scrollTrigger: { trigger: el, start: 'top 90%', once: true },
      onStart: () => el.classList.add('is-in')
    });
  });

  // il testo dell'hero cede il passo alla firma mentre si scorre
  const heroInner = document.querySelector('.hero__inner');
  if (heroInner) gsap.to(heroInner, { yPercent: -10, autoAlpha: 0.25, ease: 'none', scrollTrigger: { trigger: '[data-hero]', start: 'top top', end: 'bottom top', scrub: true } });

  // capitoli: il testo si accende man mano che si legge
  if (!small) document.querySelectorAll('.chapter > .chapter__body').forEach((body) => {
    const ps = body.querySelectorAll('p');
    if (ps.length < 2) return;
    gsap.fromTo(ps, { opacity: 0.35 }, { opacity: 1, stagger: 0.5, ease: 'none', scrollTrigger: { trigger: body, start: 'top 70%', end: 'bottom 55%', scrub: true } });
  });

  document.querySelectorAll('[data-sig-scope]').forEach((scope) => signature(gsap, scope));
  // firma "turn": la tela si volta mentre entra nel viewport
  document.querySelectorAll('[data-turn] .turn__card').forEach((card) => {
    gsap.fromTo(card, { rotationY: -180 }, { rotationY: 0, ease: 'none', scrollTrigger: { trigger: card, start: 'top 85%', end: 'center 45%', scrub: 0.6 } });
  });
}

// ---- la firma: un solo momento di movimento d'autore, guidato da scroll (e puntatore per il reticolo) ----
function signature(gsap, scope) {
  const svg = scope.querySelector('svg.sig');
  if (!svg) return;
  const parts = [...svg.querySelectorAll('[data-sig-part]')];
  const inHero = scope.matches('[data-hero-art]');
  const st = inHero
    ? { trigger: scope, start: 'top top', end: 'bottom top', scrub: 0.6 }
    : { trigger: scope, start: 'top 85%', end: 'center 40%', scrub: 0.6 };
  const num = (el, v, d) => parseFloat(getComputedStyle(el).getPropertyValue(v)) || d;
  const id = cfg.sig.kind === '3d' ? cfg.sig.fallback_id : cfg.sig.id;
  if (id === 'drip') {
    parts.forEach((p) => gsap.fromTo(p, { scaleY: num(p, '--from', 0.2) }, { scaleY: 1, ease: 'none', transformOrigin: '50% 0%', scrollTrigger: st }));
  } else if (id === 'layers' || id === 'contours') {
    parts.forEach((p) => gsap.fromTo(p, { y: 0 }, { y: num(p, '--rise', -40) * 2.2, ease: 'none', scrollTrigger: st }));
  } else if (id === 'lattice') {
    lattice(gsap, scope, parts, st);
  }
}

// reticolo: i segmenti partono ruotati in disordine; lo scroll li allinea, il puntatore calma la zona vicina.
// Si calcola solo quando arriva un evento (nessun ciclo continuo).
function lattice(gsap, scope, parts, st) {
  // Costo basso (v2.1): angoli e centri sono già nell'SVG (data-rot, data-c in coordinate del viewBox),
  // quindi niente getComputedStyle/getBoundingClientRect per segmento; si scrive solo style.transform,
  // solo per i segmenti che cambiano, in un unico requestAnimationFrame.
  const svg = scope.querySelector('svg.sig');
  const [, , VW, VH] = svg.getAttribute('viewBox').split(' ').map(Number);
  const base = parts.map((p) => +p.dataset.rot || 0);
  const pts = parts.map((p) => p.dataset.c.split(' ').map(Number));
  const last = new Float32Array(parts.length).fill(NaN);
  let order = 0;
  let px = -1e4;
  let py = -1e4;
  let box = null;
  const measure = () => {
    const r = svg.getBoundingClientRect();
    const k = Math.max(r.width / VW, r.height / VH); // preserveAspectRatio "xMidYMid slice"
    box = { x: r.left + (r.width - VW * k) / 2, y: r.top + scrollY + (r.height - VH * k) / 2, k };
  };
  let raf = 0;
  const draw = () => {
    raf = 0;
    if (!box) measure();
    for (let i = 0; i < parts.length; i++) {
      let near = 0;
      if (finePointer && px > -1e3) {
        const d = Math.hypot(px - (box.x + pts[i][0] * box.k), py - (box.y + pts[i][1] * box.k));
        near = d < 180 ? 1 - d / 180 : 0;
      }
      const a = Math.round(base[i] * (1 - order) * (1 - near));
      if (a !== last[i]) { last[i] = a; parts[i].style.transform = `rotate(${a}deg)`; }
    }
  };
  const ask = () => { if (!raf) raf = requestAnimationFrame(draw); };
  gsap.to({}, { scrollTrigger: { ...st, onUpdate: (self) => { order = self.progress; ask(); }, onRefresh: () => { box = null; ask(); } } });
  addEventListener('resize', () => { box = null; }, { passive: true });
  if (finePointer) scope.closest('section')?.addEventListener('pointermove', (e) => { px = e.clientX; py = e.clientY + scrollY; ask(); }, { passive: true });
}
function num0(v) { return parseFloat(v) || 0; }

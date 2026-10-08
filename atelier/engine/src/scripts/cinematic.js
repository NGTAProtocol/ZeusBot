// Livello CINEMATICO: Lenis + GSAP/ScrollTrigger + hero Three.js procedurale + testo reattivo + audio opzionale.
// Tutto si carica DOPO il primo rendering e solo se le condizioni lo consentono.

const dir = JSON.parse(document.getElementById('atelier-dir').textContent);
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const conn = navigator.connection || {};
const saveData = !!conn.saveData || /(^|-)2g$/.test(conn.effectiveType || '');
const lowMemory = typeof navigator.deviceMemory === 'number' && navigator.deviceMemory < 4;
const lowCpu = typeof navigator.hardwareConcurrency === 'number' && navigator.hardwareConcurrency < 4;
const finePointer = matchMedia('(pointer: fine)').matches;
const small = matchMedia('(max-width: 860px)').matches;
// parametri di diagnosi per il QA: ?no3d (niente WebGL), ?force3d (3D subito, senza attendere gesti)
const q = new URLSearchParams(location.search);

// Controllo economico: il contesto WebGL vero si crea una sola volta, in idle, dentro mountHero
// (che ripiega sul poster SVG se la creazione fallisce).
const hasWebGL = () => 'WebGLRenderingContext' in window;

const idle = (fn, timeout = 1200) => ('requestIdleCallback' in window ? requestIdleCallback(fn, { timeout }) : setTimeout(fn, 200));
const afterLoad = (fn) => (document.readyState === 'complete' ? fn() : addEventListener('load', fn, { once: true }));

// Fallback: con movimento ridotto o Save-Data, niente GSAP/Lenis/WebGL: resta il BASE.
if (reduce || saveData) {
  window.__atelierReveal?.();
  document.documentElement.dataset.fallback = reduce ? 'reduced-motion' : 'save-data';
} else {
  initMotion();
  const can3d = hasWebGL() && !lowMemory && !lowCpu && !q.has('no3d');
  if (!can3d) document.documentElement.dataset.fallback = 'no-webgl-or-weak-device';
  else {
    // Il 3D parte alla prima interazione (mouse, scroll, tocco, tastiera): fino ad allora resta il poster.
    // Protegge LCP/TBT e batteria. ?force3d lo avvia subito (serve al QA per misurarne il costo).
    const start = () => afterLoad(() => idle(startHero3d));
    if (q.has('force3d')) start();
    else {
      let done = false;
      const go = () => { if (!done) { done = true; start(); } };
      ['pointermove', 'touchstart', 'scroll', 'keydown', 'wheel'].forEach((ev) => addEventListener(ev, go, { once: true, passive: true }));
    }
  }
}

async function startHero3d() {
  const host = document.querySelector('[data-hero-art]');
  if (!host) return;
  const { mountHero } = await import('./hero3d.js');
  mountHero(host, dir, { mobile: small });
}

async function initMotion() {
  let gsap, ScrollTrigger;
  try {
    [{ gsap }, { ScrollTrigger }] = await Promise.all([import('gsap'), import('gsap/ScrollTrigger')]);
  } catch {
    window.__atelierReveal?.(); // se GSAP non si carica, il contenuto resta comunque visibile
    return;
  }
  gsap.registerPlugin(ScrollTrigger);
  const ease = dir.motion.ease === 'none' ? 'none' : dir.motion.ease;
  const D = dir.motion.duration;

  // scorrimento fluido solo con puntatore fine (desktop)
  if (finePointer) {
    const { default: Lenis } = await import('lenis');
    const lenis = new Lenis({ lerp: 0.09, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  }

  // ingresso dell'hero: le lettere salgono di poco ma sono visibili dal primo frame (LCP)
  const heroChars = document.querySelectorAll('.hero__title .ch');
  if (heroChars.length) gsap.from(heroChars, { yPercent: 35, duration: D, ease, stagger: { each: 0.018, from: 'start' } });
  document.querySelector('.hero [data-reveal-lines]')?.classList.add('is-in');

  // titoli rivelati per righe
  document.querySelectorAll('[data-reveal-lines]:not(.hero__title)').forEach((el) => {
    const lines = el.querySelectorAll('.mask-line > span');
    gsap.fromTo(lines, { yPercent: 105, y: 0 }, {
      yPercent: 0, y: 0, duration: D, ease, stagger: dir.motion.stagger,
      scrollTrigger: { trigger: el, start: 'top 88%', once: true },
      onStart: () => el.classList.add('is-in')
    });
  });
  // paragrafi ed elementi
  gsap.utils.toArray('[data-reveal]').forEach((el) => {
    gsap.fromTo(el, { autoAlpha: 0, y: dir.motion.distance }, {
      autoAlpha: 1, y: 0, duration: D * 0.85, ease,
      scrollTrigger: { trigger: el, start: 'top 90%', once: true },
      onStart: () => el.classList.add('is-in')
    });
  });

  // l'hero si allontana mentre si scorre
  const heroInner = document.querySelector('.hero__inner');
  if (heroInner) {
    gsap.to(heroInner, { yPercent: -12, autoAlpha: 0.2, ease: 'none', scrollTrigger: { trigger: '[data-hero]', start: 'top top', end: 'bottom top', scrub: true } });
  }

  // capitoli: il corpo del testo si accende progressivamente (scroll narrativo)
  document.querySelectorAll('.chapter > .chapter__body').forEach((body) => {
    const ps = body.querySelectorAll('p');
    if (ps.length < 2 || small) return;
    gsap.fromTo(ps, { opacity: 0.35 }, { opacity: 1, stagger: 0.5, ease: 'none', scrollTrigger: { trigger: body, start: 'top 70%', end: 'bottom 55%', scrub: true } });
  });

  // transizione di colore tra capitoli marcati con data-tone="invert"
  document.querySelectorAll('[data-tone="invert"]').forEach((sec) => {
    ScrollTrigger.create({
      trigger: sec, start: 'top 55%', end: 'bottom 45%',
      onToggle: (self) => document.documentElement.classList.toggle('tone-invert', self.isActive)
    });
  });

  if (finePointer) kineticTitle(gsap);
  audioToggle();
}

// testo che reagisce al cursore (solo desktop)
function kineticTitle(gsap) {
  const title = document.querySelector('.hero__title.kinetic');
  if (!title) return;
  const chars = [...title.querySelectorAll('.ch')];
  let rects = [];
  const measure = () => (rects = chars.map((c) => { const r = c.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2 + scrollY]; }));
  measure();
  addEventListener('resize', measure, { passive: true });
  const setters = chars.map((c) => ({ y: gsap.quickTo(c, 'y', { duration: 0.6, ease: 'power3.out' }), s: gsap.quickTo(c, 'scaleY', { duration: 0.6, ease: 'power3.out' }) }));
  let raf = 0;
  addEventListener('pointermove', (e) => {
    if (raf) return;
    raf = requestAnimationFrame(() => {
      raf = 0;
      const px = e.clientX;
      const py = e.clientY + scrollY;
      rects.forEach(([x, y], i) => {
        const d = Math.hypot(px - x, py - y);
        const k = Math.max(0, 1 - d / 220);
        setters[i].y(-k * 18);
        setters[i].s(1 + k * 0.18);
        chars[i].style.color = k > 0.55 ? 'var(--c-accent)' : '';
      });
    });
  }, { passive: true });
}

// audio d'ambiente procedurale: spento di default, si attiva solo con un clic
function audioToggle() {
  const btn = document.createElement('button');
  btn.className = 'audio-toggle';
  btn.type = 'button';
  btn.setAttribute('aria-pressed', 'false');
  btn.textContent = 'Suono: spento';
  document.body.appendChild(btn);
  let ctx = null;
  let gain = null;
  btn.addEventListener('click', () => {
    const on = btn.getAttribute('aria-pressed') !== 'true';
    btn.setAttribute('aria-pressed', String(on));
    btn.textContent = on ? 'Suono: acceso' : 'Suono: spento';
    if (on && !ctx) {
      ctx = new (window.AudioContext || window.webkitAudioContext)();
      gain = ctx.createGain();
      gain.gain.value = 0;
      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.value = 520;
      const roots = { argilla: 98, quota: 110, cifra: 82.4, salmastro: 130.8, manifesto: 73.4, archivio: 87.3, serra: 116.5, officina: 65.4 };
      const f0 = roots[dir.id] || 98;
      [1, 1.5, 2.01].forEach((m, i) => {
        const o = ctx.createOscillator();
        o.type = i === 0 ? 'sine' : 'triangle';
        o.frequency.value = f0 * m;
        const g = ctx.createGain();
        g.gain.value = [0.5, 0.18, 0.08][i];
        o.connect(g).connect(filter);
        o.start();
      });
      filter.connect(gain).connect(ctx.destination);
    }
    if (ctx) {
      ctx.resume();
      gain.gain.cancelScheduledValues(ctx.currentTime);
      gain.gain.linearRampToValueAtTime(on ? 0.08 : 0, ctx.currentTime + 0.8);
    }
  });
}

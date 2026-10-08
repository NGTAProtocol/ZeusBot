// Monta l'hero 3D: in un Worker con OffscreenCanvas se possibile, altrimenti nel thread principale.
// In caso di errore resta il poster SVG procedurale (fallback).
export async function mountHero(host, direction, { mobile = false } = {}) {
  const fail = () => { document.documentElement.dataset.fallback = 'no-webgl-or-weak-device'; };
  const live = () => host.classList.add('is-live');
  const size = () => [Math.max(1, host.clientWidth), Math.max(1, host.clientHeight)];
  const make = () => {
    const c = document.createElement('canvas');
    c.setAttribute('aria-hidden', 'true');
    host.appendChild(c);
    return c;
  };
  let api = null;
  const canvas = make();
  const [w, h] = size();
  const opts = { mobile, dpr: devicePixelRatio || 1, width: w, height: h };

  if ('transferControlToOffscreen' in canvas && typeof Worker === 'function') {
    const worker = new Worker(new URL('./hero-worker.js', import.meta.url), { type: 'module' });
    const offscreen = canvas.transferControlToOffscreen();
    worker.postMessage({ type: 'init', canvas: offscreen, direction, opts }, [offscreen]);
    worker.onmessage = ({ data }) => { if (data.type === 'ready') live(); else if (data.type === 'error') { worker.terminate(); canvas.remove(); fail(); } };
    worker.onerror = () => { worker.terminate(); canvas.remove(); fail(); };
    api = {
      resize: (a, b) => worker.postMessage({ type: 'resize', w: a, h: b }),
      pointer: (x, y) => worker.postMessage({ type: 'pointer', x, y }),
      scroll: (s) => worker.postMessage({ type: 'scroll', s }),
      visible: (v) => worker.postMessage({ type: 'visible', v })
    };
  } else {
    try {
      const { buildScene } = await import('./scene.js');
      api = buildScene(canvas, direction, { ...opts, onFirstFrame: live });
    } catch {
      canvas.remove();
      fail();
      return;
    }
  }

  new ResizeObserver(() => api.resize(...size())).observe(host);
  new IntersectionObserver(([e]) => api.visible(e.isIntersecting)).observe(host);
  document.addEventListener('visibilitychange', () => api.visible(!document.hidden));
  let raf = 0;
  addEventListener('pointermove', (e) => {
    if (raf) return;
    raf = requestAnimationFrame(() => { raf = 0; api.pointer((e.clientX / innerWidth) * 2 - 1, (e.clientY / innerHeight) * 2 - 1); });
  }, { passive: true });
  addEventListener('scroll', () => api.scroll(Math.min(1, scrollY / Math.max(1, host.clientHeight))), { passive: true });
}

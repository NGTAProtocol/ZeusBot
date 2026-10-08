// Worker dell'hero 3D: contesto WebGL, compilazione shader e rendering fuori dal thread principale.
import { buildScene } from './scene.js';

if (typeof self.requestAnimationFrame !== 'function') {
  self.requestAnimationFrame = (cb) => setTimeout(() => cb(performance.now()), 16);
  self.cancelAnimationFrame = (id) => clearTimeout(id);
}
let api = null;
self.onmessage = ({ data }) => {
  if (data.type === 'init') {
    try {
      api = buildScene(data.canvas, data.direction, { ...data.opts, onFirstFrame: () => self.postMessage({ type: 'ready' }) });
    } catch (err) {
      self.postMessage({ type: 'error', message: String(err && err.message) });
    }
  } else if (api) {
    if (data.type === 'resize') api.resize(data.w, data.h);
    else if (data.type === 'pointer') api.pointer(data.x, data.y);
    else if (data.type === 'scroll') api.scroll(data.s);
    else if (data.type === 'visible') api.visible(data.v);
  }
};

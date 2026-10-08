// Scena Three.js dell'hero: geometrie e shader PROCEDURALI scritti per Atelier.
// Nessun modello, texture o shader di terzi. Funziona sia nel thread principale sia in un Worker (OffscreenCanvas).
import {
  WebGLRenderer, Scene, PerspectiveCamera, Mesh, Points, Group, ShaderMaterial, Color,
  IcosahedronGeometry, PlaneGeometry, TorusGeometry, BufferGeometry, BufferAttribute,
  AdditiveBlending, DoubleSide
} from 'three';

const NOISE = /* glsl */ `
float h31(vec3 p){ return fract(sin(dot(p, vec3(41.3, 289.1, 97.7))) * 23758.5453); }
float vnoise(vec3 x){
  vec3 i = floor(x); vec3 f = fract(x); f = f*f*(3.0-2.0*f);
  float a = mix(h31(i), h31(i+vec3(1,0,0)), f.x);
  float b = mix(h31(i+vec3(0,1,0)), h31(i+vec3(1,1,0)), f.x);
  float c = mix(h31(i+vec3(0,0,1)), h31(i+vec3(1,0,1)), f.x);
  float d = mix(h31(i+vec3(0,1,1)), h31(i+vec3(1,1,1)), f.x);
  return mix(mix(a,b,f.y), mix(c,d,f.y), f.z);
}
float fbm(vec3 p){ float s=0.0, a=0.5; for(int i=0;i<4;i++){ s+=a*vnoise(p); p=p*2.03+1.7; a*=0.5; } return s; }
`;

const GRAIN = /* glsl */ `
float grain(vec2 uv, float t){ return fract(sin(dot(uv*vec2(12.9898,78.233) + t, vec2(1.0,1.7))) * 43758.5453) - 0.5; }
`;

function colors(p) {
  return {
    uBg: { value: new Color(p.bg) }, uSurface: { value: new Color(p.surface) }, uInk: { value: new Color(p.ink) },
    uAccent: { value: new Color(p.accent) }, uAccent2: { value: new Color(p.accent2) }
  };
}

function blob(u, params, mobile) {
  const geo = new IcosahedronGeometry(1.25, mobile ? 32 : params.detail || 56);
  const mat = new ShaderMaterial({
    uniforms: { ...u, uChrome: { value: params.chrome ? 1 : 0 } },
    vertexShader: NOISE + /* glsl */ `
      uniform float uTime, uScroll; uniform vec2 uPointer;
      varying float vD; varying vec3 vN; varying vec3 vView;
      float bigN(vec3 p){ return fbm(p*0.75 + vec3(uTime*0.35, uTime*0.22, uPointer.x*0.3)); }
      vec3 shape(vec3 p){
        vec3 n = normalize(p);
        float fine = vnoise(p*3.2 + vec3(0.0, uTime*0.5, 0.0));
        return p + n * ((bigN(p) - 0.45) * (0.75 + uScroll*0.5) + fine*0.035);
      }
      void main(){
        vec3 p0 = shape(position);
        // normale liscia per differenze finite lungo due tangenti
        vec3 nrm = normalize(position);
        vec3 t1 = normalize(cross(nrm, abs(nrm.y) < 0.99 ? vec3(0.0,1.0,0.0) : vec3(1.0,0.0,0.0)));
        vec3 t2 = cross(nrm, t1);
        float e = 0.02;
        vec3 p1 = shape(position + t1*e);
        vec3 p2 = shape(position + t2*e);
        vec3 n = normalize(cross(p1 - p0, p2 - p0));
        if (dot(n, nrm) < 0.0) n = -n;
        vD = bigN(position);
        vec4 mv = modelViewMatrix * vec4(p0, 1.0);
        vN = normalize(normalMatrix * n); vView = normalize(-mv.xyz);
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: GRAIN + /* glsl */ `
      uniform vec3 uBg, uSurface, uInk, uAccent, uAccent2; uniform float uChrome, uTime;
      varying float vD; varying vec3 vN; varying vec3 vView;
      void main(){
        vec3 n = normalize(vN);
        float ndv = max(dot(n, vView), 0.0);
        float fres = pow(1.0 - ndv, 3.0);
        vec3 L = normalize(vec3(-0.5, 0.8, 0.6));
        float diff = max(dot(n, L), 0.0);
        float spec = pow(max(dot(reflect(-L, n), vView), 0.0), 60.0);
        vec3 col;
        if (uChrome > 0.5) {
          vec3 r = reflect(-vView, n);
          float bands = smoothstep(0.3, 0.7, sin(r.y*6.0 + r.x*2.0)*0.5+0.5);
          col = mix(uInk, uBg, bands);
          col = mix(col, uAccent2, fres*0.8);
          col += spec * 0.8;
        } else {
          // smalto: blu sui rilievi, ocra dove lo smalto si raccoglie (cavità)
          float pool = smoothstep(0.55, 0.30, vD);
          vec3 glaze = mix(uAccent, uAccent2, pool);
          col = glaze * (0.35 + 0.75*diff);
          col = mix(col, uSurface, (1.0 - ndv) * 0.25);
          col += spec * 0.9 + fres * uAccent * 0.25;
        }
        col += grain(gl_FragCoord.xy, uTime) * 0.045;
        gl_FragColor = vec4(col, 1.0);
      }`
  });
  const m = new Mesh(geo, mat);
  m.position.set(mobile ? 0 : 1.25, mobile ? 0.6 : 0.05, 0);
  m.scale.setScalar(mobile ? 0.85 : 0.88);
  return { object: m, tick: (t) => { m.rotation.y = t * 0.1; m.rotation.x = Math.sin(t * 0.17) * 0.25; } };
}

function terrain(u, params, mobile) {
  const seg = mobile ? 90 : 170;
  const geo = new PlaneGeometry(9, 7, seg, seg);
  const mat = new ShaderMaterial({
    uniforms: { ...u, uContour: { value: params.contour || 12 } },
    extensions: { derivatives: true },
    vertexShader: NOISE + /* glsl */ `
      uniform float uTime, uScroll; uniform vec2 uPointer; varying float vH; varying vec2 vUv;
      void main(){
        vec3 p = position;
        float peak = exp(-dot(p.xy - vec2(1.2, 0.6), p.xy - vec2(1.2, 0.6)) * 0.25);
        float h = fbm(vec3(p.xy*0.45, uTime*0.25)) * 1.1 + peak * 1.6;
        p.z = h * (0.8 + uScroll * 0.5);
        vH = h; vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
      }`,
    fragmentShader: GRAIN + /* glsl */ `
      uniform vec3 uBg, uSurface, uInk, uAccent, uAccent2; uniform float uContour, uTime;
      varying float vH; varying vec2 vUv;
      void main(){
        float v = vH * uContour;
        float w = fwidth(v);
        float line = 1.0 - smoothstep(0.0, w*1.4, abs(fract(v) - 0.5) - 0.5 + w);
        float major = mod(floor(v), 5.0) < 0.5 ? 1.0 : 0.0;
        vec3 col = mix(uBg, uSurface, smoothstep(0.2, 1.8, vH));
        col = mix(col, major > 0.5 ? uAccent : uInk, line * (major > 0.5 ? 0.95 : 0.55));
        float fade = smoothstep(0.0, 0.25, vUv.y) * smoothstep(1.0, 0.7, vUv.y);
        col = mix(uBg, col, fade);
        col += grain(gl_FragCoord.xy, uTime) * 0.05;
        gl_FragColor = vec4(col, 1.0);
      }`
  });
  const m = new Mesh(geo, mat);
  m.rotation.x = -1.08;
  m.position.set(0, -0.6, -0.5);
  return { object: m, tick: () => {} };
}

function points(u, params, mobile, dpr = 1) {
  const count = Math.round((params.count || 2000) * (mobile ? 0.5 : 1));
  const pos = new Float32Array(count * 3);
  const seed = new Float32Array(count);
  const golden = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < count; i++) {
    let x, y, z;
    if (params.arrangement === 'phyllotaxis') {
      const r = Math.sqrt(i / count) * 2.4;
      const a = i * golden;
      x = Math.cos(a) * r; y = Math.sin(a) * r; z = -r * r * 0.12;
    } else {
      const side = Math.ceil(Math.cbrt(count));
      x = ((i % side) / side - 0.5) * 5.2;
      y = ((Math.floor(i / side) % side) / side - 0.5) * 3.6;
      z = (Math.floor(i / (side * side)) / side - 0.5) * 2.4;
    }
    pos.set([x, y, z], i * 3);
    seed[i] = (Math.sin(i * 12.9898) * 43758.5453) % 1;
  }
  const geo = new BufferGeometry();
  geo.setAttribute('position', new BufferAttribute(pos, 3));
  geo.setAttribute('aSeed', new BufferAttribute(seed, 1));
  const mat = new ShaderMaterial({
    uniforms: { ...u, uPx: { value: Math.min(dpr, 1.6) } },
    transparent: true, depthWrite: false, blending: AdditiveBlending,
    vertexShader: NOISE + /* glsl */ `
      uniform float uTime, uScroll, uPx; uniform vec2 uPointer; attribute float aSeed; varying float vS; varying float vLit;
      void main(){
        vec3 p = position;
        float n = vnoise(p*0.9 + uTime*0.5);
        p += normalize(p + 0.001) * (n - 0.5) * 0.35;
        p.z += sin(p.x*1.4 + uTime*1.3) * 0.12;
        float lit = smoothstep(0.75, 1.0, vnoise(p*1.6 + vec3(0.0, 0.0, uTime*0.8)));
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        gl_PointSize = (5.0 + lit*9.0 + aSeed*2.5) * uPx * (3.0 / -mv.z);
        vS = aSeed; vLit = lit;
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: /* glsl */ `
      uniform vec3 uAccent, uAccent2; varying float vS; varying float vLit;
      void main(){
        float d = length(gl_PointCoord - 0.5);
        if (d > 0.5) discard;
        vec3 col = mix(uAccent2, uAccent, vLit);
        gl_FragColor = vec4(col, (1.0 - d*2.0) * (0.7 + vLit*0.3));
      }`
  });
  const g = new Group();
  const pts = new Points(geo, mat);
  g.add(pts);
  g.position.set(mobile ? 0 : 1.1, mobile ? 0.5 : 0, 0);
  return { object: g, tick: (t) => { g.rotation.z = t * 0.03; g.rotation.y = Math.sin(t * 0.15) * 0.25; } };
}

function ribbons(u, params, mobile) {
  const g = new Group();
  const count = Math.round((params.count || 20) * (mobile ? 0.6 : 1));
  for (let i = 0; i < count; i++) {
    const geo = new PlaneGeometry(10, params.sheets ? 1.6 : 0.05, mobile ? 80 : 160, 1);
    const mat = new ShaderMaterial({
      uniforms: { ...u, uI: { value: i / count }, uSheets: { value: params.sheets ? 1 : 0 } },
      side: DoubleSide, transparent: true, depthWrite: !params.sheets,
      vertexShader: /* glsl */ `
        uniform float uTime, uScroll, uI; uniform vec2 uPointer; varying float vY; varying vec2 vUv;
        void main(){
          vec3 p = position;
          float ph = uI * 6.2831;
          p.y += sin(p.x*0.7 + uTime*0.9 + ph) * (0.35 + uScroll*0.4) + (uI - 0.5) * 3.2;
          p.z += cos(p.x*0.5 + uTime*0.6 + ph*0.5) * 0.6 + uPointer.y*0.2;
          vY = p.y; vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
        }`,
      fragmentShader: GRAIN + /* glsl */ `
        uniform vec3 uBg, uSurface, uInk, uAccent, uAccent2; uniform float uI, uSheets, uTime; varying float vY; varying vec2 vUv;
        void main(){
          vec3 col; float a;
          if (uSheets > 0.5) {
            col = mix(uSurface, uBg, step(0.5, fract(uI*7.0)));
            float edge = smoothstep(0.96, 1.0, vUv.y);
            col = mix(col, uInk, edge*0.8);
            a = 0.92;
          } else {
            col = mod(floor(uI*20.0), 6.0) < 0.5 ? uAccent : uAccent2;
            a = 0.85 * smoothstep(0.0, 0.1, vUv.x) * smoothstep(1.0, 0.9, vUv.x);
          }
          col += grain(gl_FragCoord.xy, uTime) * 0.05;
          gl_FragColor = vec4(col, a);
        }`
    });
    const m = new Mesh(geo, mat);
    m.position.z = -i * (params.sheets ? 0.18 : 0.05);
    g.add(m);
  }
  g.rotation.z = -0.18;
  g.position.set(mobile ? 0 : 0.6, mobile ? 0.6 : 0, 0);
  return { object: g, tick: (t) => { g.rotation.y = Math.sin(t * 0.1) * 0.15; } };
}

function rings(u, params, mobile) {
  const g = new Group();
  const n = params.count || 7;
  const items = [];
  for (let i = 0; i < n; i++) {
    const geo = new TorusGeometry(0.6 + i * 0.22, 0.012 + (i % 3 === 0 ? 0.01 : 0), 8, mobile ? 120 : 220);
    const mat = new ShaderMaterial({
      uniforms: { ...u, uI: { value: i } },
      transparent: true,
      vertexShader: /* glsl */ `varying vec2 vUv; varying vec3 vN; varying vec3 vV;
        void main(){ vUv = uv; vec4 mv = modelViewMatrix * vec4(position,1.0); vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }`,
      fragmentShader: /* glsl */ `uniform vec3 uInk, uAccent, uAccent2; uniform float uI, uTime; varying vec2 vUv; varying vec3 vN; varying vec3 vV;
        void main(){
          if (mod(uI, 2.0) > 0.5 && fract(vUv.x*48.0 - uTime*0.4) < 0.45) discard;
          float fres = pow(1.0 - abs(dot(vN, vV)), 1.5);
          vec3 col = mod(uI, 3.0) < 0.5 ? uAccent : mix(uAccent2, uInk, 0.15);
          gl_FragColor = vec4(col, 0.55 + fres*0.45);
        }`
    });
    const m = new Mesh(geo, mat);
    m.rotation.set(Math.sin(i * 1.7) * 1.2, Math.cos(i * 2.3) * 1.2, 0);
    items.push(m);
    g.add(m);
  }
  g.position.set(mobile ? 0 : 1.1, mobile ? 0.5 : 0, 0);
  return { object: g, tick: (t, scroll) => items.forEach((m, i) => { m.rotation.x += 0.0015 * (i % 2 ? 1 : -1); m.rotation.y = Math.cos(i * 2.3) * 1.2 + t * 0.05 * (i + 1) * 0.3 + scroll; }) };
}

const MOTIFS = { blob, terrain, points, ribbons, rings };

export function buildScene(canvas, direction, { mobile = false, dpr = 1, width = 1, height = 1, onFirstFrame = () => {} } = {}) {
  const renderer = new WebGLRenderer({ canvas, antialias: !mobile, alpha: true, powerPreference: 'low-power' });
  if (!renderer.getContext()) throw new Error('no-webgl');
  renderer.setPixelRatio(Math.min(dpr, mobile ? 1.25 : 1.6));
  const scene = new Scene();
  const camera = new PerspectiveCamera(40, 1, 0.1, 50);
  camera.position.set(0, 0, 6);
  const uniforms = { uTime: { value: 0 }, uScroll: { value: 0 }, uPointer: { value: { x: 0, y: 0 } }, ...colors(direction.palette) };
  const make = MOTIFS[direction.hero3d.motif] || blob;
  const motif = make(uniforms, direction.hero3d.params || {}, mobile, dpr);
  scene.add(motif.object);

  const state = { visible: true, scroll: 0, ptx: 0, pty: 0, px: 0, py: 0, ready: false, first: true };
  const resize = (w, h) => {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.position.z = w < h ? 8 : 6;
    camera.updateProjectionMatrix();
  };
  resize(width, height);
  // compilazione shader asincrona (KHR_parallel_shader_compile dove disponibile)
  (renderer.compileAsync ? renderer.compileAsync(scene, camera) : Promise.resolve()).catch(() => {}).finally(() => { state.ready = true; });
  const speed = direction.hero3d.params?.speed ?? 0.15;
  const t0 = performance.now();
  renderer.setAnimationLoop(() => {
    if (!state.ready || !state.visible) return;
    const t = ((performance.now() - t0) / 1000) * speed * 6;
    state.px += (state.ptx - state.px) * 0.05;
    state.py += (state.pty - state.py) * 0.05;
    uniforms.uTime.value = t;
    uniforms.uScroll.value = state.scroll;
    uniforms.uPointer.value = { x: state.px, y: state.py };
    camera.position.x = state.px * 0.25;
    camera.position.y = -state.py * 0.15 - state.scroll * 0.6;
    camera.lookAt(0, 0, 0);
    motif.tick(t, state.scroll);
    renderer.render(scene, camera);
    if (state.first) { state.first = false; onFirstFrame(); }
  });
  return {
    resize,
    pointer: (x, y) => { state.ptx = x; state.pty = y; },
    scroll: (s) => { state.scroll = s; },
    visible: (v) => { state.visible = v; }
  };
}

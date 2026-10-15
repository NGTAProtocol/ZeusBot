# Esportazione completa del progetto — parte 3 di 6

Testo integrale, parola per parola. Nessun riassunto, nessuna correzione. Esclusi `libri/` e i manoscritti.


---

## 6. Skill e hook

### `atelier/.claude/skills/threejs-errors-rendering/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-errors-rendering
description: >
  Use when a Three.js scene renders incorrectly: black screen, invisible
  objects, wrong colors, z-fighting, or broken shadows. Prevents the
  common mistake of wrong color space, missing material.side, or
  forgetting updateProjectionMatrix. Covers all common rendering errors
  with diagnosis steps and fix patterns.
  Keywords: black screen, invisible, wrong color, z-fighting, shadow artifact, rendering error, debug, nothing visible, dark, broken, nothing shows, model not appearing, screen is blank.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-errors-rendering

## Debugging Workflow Checklist

When a Three.js scene does not render correctly, ALWAYS follow this sequence:

1. Open the browser console -- check for WebGL errors or Three.js warnings
2. Verify the renderer has a non-zero size (`renderer.getSize(new THREE.Vector2())`)
3. Confirm the canvas is in the DOM and visible (not `display: none`)
4. Check that `renderer.render(scene, camera)` is called (in a loop or at least once)
5. Verify the camera is looking at the scene (position, target, near/far)
6. Confirm at least one light exists for lit materials
7. Check material `side`, `visible`, `opacity`, and `transparent` properties
8. Verify object `visible`, `layers`, and `frustumCulled` properties
9. Inspect color space settings on renderer and textures

---

## Symptom 1: Black Screen (Nothing Visible)

### Cause A: Renderer has zero size

The canvas has 0x0 dimensions. This happens when `setSize()` is called before the container is in the DOM or when the container has no CSS dimensions.

**Fix:**
```javascript
// ALWAYS ensure the container is in the DOM and has dimensions before setSize
document.body.appendChild(renderer.domElement);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
```

### Cause B: Camera is inside the object or facing away

The camera is at `(0, 0, 0)` and the object is also at `(0, 0, 0)`, so the camera is inside the mesh. Or the camera is pointing in the wrong direction.

**Fix:**
```javascript
camera.position.set(0, 2, 5); // ALWAYS move camera away from origin
camera.lookAt(0, 0, 0);
```

### Cause C: Near/far clipping planes exclude the object

Objects closer than `near` or farther than `far` are clipped. Default PerspectiveCamera near is `0.1`, far is `2000`.

**Fix:**
```javascript
const camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
// NEVER set near to 0 -- causes z-fighting and depth buffer issues
// ALWAYS keep far/near ratio below 100000 for stable depth precision
```

### Cause D: No light in the scene

`MeshStandardMaterial`, `MeshPhongMaterial`, and `MeshLambertMaterial` require lights. Without light, they render black. `MeshBasicMaterial` does NOT require lights.

**Fix:**
```javascript
scene.add(new THREE.AmbientLight(0xffffff, 0.5));
scene.add(new THREE.DirectionalLight(0xffffff, 1));
```

### Cause E: render() is never called

The animation loop is not started, or `renderer.render(scene, camera)` is missing.

**Fix:**
```javascript
function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
animate(); // ALWAYS call the function to start the loop
```

### Cause F: Scene or camera is wrong reference

Passing an empty scene or an uninitialized camera to `render()`.

**Diagnosis:** Log `scene.children.length` and `camera.type` before the render call.

---

## Symptom 2: Invisible Objects

### Cause A: Wrong material side

Back faces are culled by default (`FrontSide`). If the camera sees the back of a plane or thin geometry, it is invisible.

**Fix:**
```javascript
const material = new THREE.MeshStandardMaterial({
  side: THREE.DoubleSide // ALWAYS use for planes, leaves, thin objects
});
```

### Cause B: opacity without transparent

Setting `opacity: 0.5` without `transparent: true` has NO effect.

**Fix:**
```javascript
const material = new THREE.MeshStandardMaterial({
  opacity: 0.5,
  transparent: true // ALWAYS pair with opacity < 1
});
```

### Cause C: Object on a different layer

The camera and the object MUST share at least one layer. By default both are on layer 0. If the object is moved to another layer, the camera must enable that layer too.

**Fix:**
```javascript
object.layers.set(1);
camera.layers.enable(1); // camera must see layer 1
```

### Cause D: visible is false (inherited)

`visible = false` on a parent makes ALL descendants invisible. Check the full parent chain.

**Diagnosis:**
```javascript
let node = object;
while (node) {
  if (!node.visible) console.log('Hidden ancestor:', node.name || node.type);
  node = node.parent;
}
```

### Cause E: frustumCulled incorrectly

If the bounding sphere is wrong (e.g., after manual vertex changes without `computeBoundingSphere()`), the object may be culled even when visible.

**Fix:**
```javascript
geometry.computeBoundingSphere(); // ALWAYS call after modifying positions
// Or disable frustum culling for objects that must always render:
mesh.frustumCulled = false;
```

### Cause F: Object at wrong position or scale 0

Object is at a position far from the camera, or `scale.set(0, 0, 0)`.

**Diagnosis:** Log `object.position`, `object.scale`, `object.matrixWorld`.

---

## Symptom 3: Wrong Colors

### Cause A: Color space mismatch

This is the MOST COMMON color error in Three.js r160+.

**Rules:**
- Color/diffuse/emissive textures: ALWAYS set `texture.colorSpace = THREE.SRGBColorSpace`
- Data textures (normal, roughness, metalness, AO, displacement): ALWAYS leave as `THREE.LinearSRGBColorSpace`
- Renderer output: `renderer.outputColorSpace = THREE.SRGBColorSpace` (default in r160+)

**Symptoms of wrong color space:**
- Washed-out colors: data texture incorrectly set to `SRGBColorSpace` (double gamma)
- Over-saturated colors: color texture left in `LinearSRGBColorSpace` (no gamma applied)

**Fix:**
```javascript
const texture = await loader.loadAsync('diffuse.png');
texture.colorSpace = THREE.SRGBColorSpace; // for color textures

const normalMap = await loader.loadAsync('normal.png');
// NEVER set SRGBColorSpace on normal maps -- corrupts surface data
```

### Cause B: Tone mapping not configured

Without tone mapping, HDR values are clamped, producing flat or incorrect colors.

**Fix:**
```javascript
renderer.toneMapping = THREE.ACESFilmicToneMapping; // or AgXToneMapping
renderer.toneMappingExposure = 1.0;
```

### Cause C: Material color set after construction ignored

`material.color.set()` works, but `material.color = new THREE.Color()` after construction also works. The common mistake is setting color as a hex number directly: `material.color = 0xff0000` does NOT work.

**Fix:**
```javascript
material.color.set(0xff0000);      // Correct
material.color = new THREE.Color(0xff0000); // Correct
// material.color = 0xff0000;      // WRONG -- silently fails
```

---

## Symptom 4: Z-Fighting (Flickering Surfaces)

Z-fighting occurs when two surfaces overlap at nearly the same depth, causing the depth buffer to alternate between them.

### Fix A: Polygon offset

```javascript
const material = new THREE.MeshStandardMaterial({
  polygonOffset: true,
  polygonOffsetFactor: -1,
  polygonOffsetUnits: -1
});
```

### Fix B: Logarithmic depth buffer

```javascript
const renderer = new THREE.WebGLRenderer({ logarithmicDepthBuffer: true });
// Trades performance for better depth precision across large near/far ranges
// NEVER use with EffectComposer post-processing -- causes artifacts
```

### Fix C: Position offset

Move one surface slightly:
```javascript
decalMesh.position.z += 0.01; // small offset to prevent overlap
```

### Fix D: Reduce near/far ratio

```javascript
// ALWAYS keep the near plane as large as possible
camera.near = 1;    // not 0.001
camera.far = 1000;  // not 1000000
camera.updateProjectionMatrix();
```

---

## Symptom 5: Shadow Artifacts

For complete shadow configuration, see the `threejs-impl-shadows` skill. Common quick fixes:

- **No shadows at all:** `renderer.shadowMap.enabled = true`, `light.castShadow = true`, `mesh.castShadow = true`, `ground.receiveShadow = true`
- **Shadow acne (stripes):** Increase `light.shadow.bias` (e.g., `-0.005`)
- **Peter panning (shadow detached):** `light.shadow.bias` is too large, reduce it
- **Low-res shadows:** Increase `light.shadow.mapSize.set(2048, 2048)`

---

## Symptom 6: WebGL Context Lost

The browser reclaims the WebGL context under memory pressure or GPU reset.

### Recovery pattern

```javascript
renderer.domElement.addEventListener('webglcontextlost', (event) => {
  event.preventDefault(); // ALWAYS prevent default to allow restoration
  cancelAnimationFrame(animationId);
}, false);

renderer.domElement.addEventListener('webglcontextrestored', () => {
  // Re-initialize materials, textures, render targets
  initScene();
  animate();
}, false);
```

**NEVER** ignore context loss -- the canvas goes black permanently. ALWAYS add both event listeners.

---

## Symptom 7: needsUpdate Missing

### BufferAttribute

After modifying vertex data, the GPU buffer is stale:
```javascript
positions.array[0] = newX;
positions.needsUpdate = true; // ALWAYS set after modifying attribute data
```

### Material

After changing structural properties (adding/removing maps, changing `defines`):
```javascript
material.map = newTexture;
material.needsUpdate = true; // triggers shader recompilation
// NEVER set needsUpdate = true every frame -- causes constant recompilation
```

### Texture

After modifying texture image data:
```javascript
texture.image = newImage;
texture.needsUpdate = true; // triggers GPU re-upload
```

### InstancedMesh

After `setMatrixAt()` or `setColorAt()`:
```javascript
mesh.instanceMatrix.needsUpdate = true; // ALWAYS after setMatrixAt
mesh.instanceColor.needsUpdate = true;  // ALWAYS after setColorAt
```

---

## Symptom 8: updateProjectionMatrix Required

ALWAYS call `camera.updateProjectionMatrix()` after changing:

- `camera.fov`
- `camera.aspect`
- `camera.near`
- `camera.far`
- `camera.zoom`
- `camera.left/right/top/bottom` (OrthographicCamera)

```javascript
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix(); // NEVER forget this
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

---

## Symptom 9: Transparent Object Rendering Issues

Transparent objects render in the wrong order (back-to-front sorting fails).

### Fix A: renderOrder

```javascript
// Force specific rendering order
backgroundMesh.renderOrder = 0;
transparentMesh.renderOrder = 1;
frontMesh.renderOrder = 2;
```

### Fix B: depthWrite

```javascript
const material = new THREE.MeshStandardMaterial({
  transparent: true,
  opacity: 0.5,
  depthWrite: false // prevents transparent objects from writing to depth buffer
});
```

### Fix C: alphaTest instead of transparency

For textures with hard alpha edges (foliage, fences):
```javascript
const material = new THREE.MeshStandardMaterial({
  map: leafTexture,
  alphaTest: 0.5, // discards fragments below threshold
  side: THREE.DoubleSide
  // NEVER set transparent: true for hard-edge alpha -- use alphaTest instead
});
```

---

## Common Console Warnings

| Warning | Cause | Fix |
|---------|-------|-----|
| `THREE.WebGLRenderer: Texture is not power of two` | NPOT texture with repeat wrapping | Use power-of-two textures or `ClampToEdgeWrapping` |
| `THREE.WebGLProgram: shader error` | GLSL compilation failure | Check custom shader code for syntax errors |
| `THREE.PropertyBinding: Can not bind to...` | Animation targets missing property | Ensure skeleton/morph targets match the animation clip |
| `THREE.BufferGeometry: .addAttribute() removed` | Using deprecated API | Use `setAttribute()` instead |
| `GL_INVALID_OPERATION: Feedback loop` | Reading from a texture that is also a render target | Use separate textures for reading and writing |

---

## Reference Links

- [references/methods.md](references/methods.md) -- Fix-related API signatures
- [references/examples.md](references/examples.md) -- Complete fix patterns
- [references/anti-patterns.md](references/anti-patterns.md) -- What NOT to do

### Official Sources

- https://threejs.org/docs/#api/en/renderers/WebGLRenderer
- https://threejs.org/docs/#api/en/cameras/PerspectiveCamera
- https://threejs.org/docs/#api/en/materials/Material
- https://threejs.org/docs/#api/en/core/Object3D
- https://threejs.org/docs/#api/en/core/BufferAttribute
````

### `atelier/.claude/skills/threejs-errors-rendering/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-impl-animation/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-impl-animation
description: >
  Use when playing animations, crossfading between animation states,
  or loading skeletal animations from GLTF in Three.js. Prevents the
  common mistake of not calling mixer.update(delta) every frame,
  wrong crossfade setup, or missing Clock. Covers AnimationMixer,
  AnimationClip, AnimationAction, KeyframeTrack, crossfade, blending.
  Keywords: animation, AnimationMixer, AnimationClip, AnimationAction, crossfade, skeletal, GLTF animation, keyframe, blend, Clock, camera animation, smooth camera, fly to, tween, GSAP.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-impl-animation

## Quick Reference

### Architecture

```
AnimationClip        (data: array of KeyframeTrack objects)
  └── AnimationAction  (playback controller: play, pause, fade, crossfade)
        └── AnimationMixer (master scheduler: one per animated root object)
              └── Clock    (provides delta time for mixer.update)
```

ALWAYS create exactly ONE `AnimationMixer` per animated root object.
ALWAYS call `mixer.update(delta)` every frame inside the render loop.
NEVER instantiate `AnimationAction` directly -- ALWAYS use `mixer.clipAction(clip)`.

### Essential Imports

```js
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
```

### Minimal Animation Setup

```js
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const clock = new THREE.Clock();
let mixer;

const loader = new GLTFLoader();
loader.load('character.glb', (gltf) => {
  scene.add(gltf.scene);
  mixer = new THREE.AnimationMixer(gltf.scene);

  // Play all animations from the GLTF file
  gltf.animations.forEach((clip) => {
    mixer.clipAction(clip).play();
  });
});

function animate() {
  const delta = clock.getDelta();
  if (mixer) mixer.update(delta);
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
```

### Critical Warnings

**NEVER** forget to call `mixer.update(delta)` in the render loop -- animations will NOT play without it.

**NEVER** use `new Date()` or `performance.now()` to compute delta manually -- ALWAYS use `THREE.Clock` or `renderer.setAnimationLoop` which provides stable frame timing.

**NEVER** call `mixer.clipAction(clip)` repeatedly in the render loop -- it caches internally, but the lookup is unnecessary overhead. ALWAYS store the returned action in a variable.

**NEVER** call `.play()` every frame -- call it ONCE to start playback. Calling `.play()` again on an already-playing action has no effect, but it signals misunderstanding.

**ALWAYS** call `.reset()` before `.play()` when restarting a stopped or finished action, or the action may resume from its last position.

**ALWAYS** set `action.clampWhenFinished = true` when using `LoopOnce` -- otherwise the action resets to the first frame when finished.

---

## AnimationMixer

The master scheduler that drives all animation actions for a single object hierarchy.

### Constructor

```js
const mixer = new THREE.AnimationMixer(rootObject);
```

`rootObject` is the root `Object3D` of the animated model (typically `gltf.scene`).

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `.time` | number | `0` | Global mixer time in seconds |
| `.timeScale` | number | `1` | Global speed multiplier; `0` pauses ALL actions |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `.clipAction(clip, root?, blendMode?)` | `AnimationAction` | Returns or creates an action for the clip |
| `.existingAction(clip, root?)` | `AnimationAction \| null` | Returns previously created action or `null` |
| `.update(delta)` | `this` | Advances mixer by delta seconds -- MUST call every frame |
| `.setTime(seconds)` | `this` | Sets global time, updates all actions |
| `.stopAllAction()` | `this` | Deactivates all scheduled actions |
| `.getRoot()` | `Object3D` | Returns the mixer's root object |
| `.uncacheAction(clip, root?)` | `void` | Deallocates cached action |
| `.uncacheClip(clip)` | `void` | Deallocates clip data |
| `.uncacheRoot(root)` | `void` | Deallocates root object data |

### Events

Listen via `mixer.addEventListener(type, callback)`:

| Event | Fires When |
|-------|-----------|
| `'finished'` | Action completes (ONLY with `LoopOnce` + `clampWhenFinished = true`) |
| `'loop'` | Action completes a loop iteration |

Event object properties: `{ action, loopDelta, type }`.

### Blend Modes

Pass as the third argument to `mixer.clipAction(clip, root, blendMode)`:

| Constant | Behavior |
|----------|----------|
| `THREE.NormalAnimationBlendMode` | Standard blending (default) |
| `THREE.AdditiveAnimationBlendMode` | Layered on top of base animation |

---

## AnimationAction

Controls playback of a single animation clip. NEVER instantiate directly.

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `.blendMode` | number | `NormalAnimationBlendMode` | Blending strategy |
| `.clampWhenFinished` | boolean | `false` | Pause at last frame when done |
| `.enabled` | boolean | `true` | Disable without resetting |
| `.loop` | number | `LoopRepeat` | Loop mode |
| `.paused` | boolean | `false` | Freeze playback |
| `.repetitions` | number | `Infinity` | Loop count |
| `.time` | number | `0` | Local time in seconds |
| `.timeScale` | number | `1` | Speed: `0` pauses, negative reverses |
| `.weight` | number | `1` | Blend influence `[0, 1]` |
| `.zeroSlopeAtEnd` | boolean | `true` | Smooth interpolation at loop end |
| `.zeroSlopeAtStart` | boolean | `true` | Smooth interpolation at loop start |

### Loop Modes

| Constant | Behavior |
|----------|----------|
| `THREE.LoopOnce` | Plays once, stops |
| `THREE.LoopRepeat` | Restarts from beginning each loop |
| `THREE.LoopPingPong` | Alternates forward/backward |

### Playback Methods

| Method | Description |
|--------|-------------|
| `.play()` | Start playback |
| `.stop()` | Stop and reset to start |
| `.reset()` | Reset time, weight, speed to initial state |
| `.startAt(mixerTime)` | Delay start until specified mixer time |

### Fading and Crossfade Methods

| Method | Description |
|--------|-------------|
| `.fadeIn(duration)` | Fade weight from `0` to `1` |
| `.fadeOut(duration)` | Fade weight from `1` to `0` |
| `.crossFadeFrom(fadeOutAction, duration, warp)` | Crossfade from another action into this one |
| `.crossFadeTo(fadeInAction, duration, warp)` | Crossfade from this action to another |
| `.stopFading()` | Cancel any active fade |

### Speed and Timing Methods

| Method | Description |
|--------|-------------|
| `.halt(duration)` | Decelerate timeScale to `0` over duration |
| `.warp(startScale, endScale, duration)` | Smoothly transition playback speed |
| `.stopWarping()` | Cancel any active warp |
| `.setDuration(seconds)` | Adjust timeScale so one loop takes exactly `seconds` |
| `.setEffectiveTimeScale(scale)` | Set effective time scale |
| `.setEffectiveWeight(weight)` | Set effective weight |
| `.setLoop(mode, repetitions)` | Set loop mode and count |
| `.syncWith(otherAction)` | Synchronize time with another action |

### Query Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `.isRunning()` | boolean | `true` only if actively playing |
| `.isScheduled()` | boolean | `true` if `.play()` was called |
| `.getClip()` | `AnimationClip` | The associated clip |
| `.getMixer()` | `AnimationMixer` | The owning mixer |
| `.getRoot()` | `Object3D` | The root object |
| `.getEffectiveTimeScale()` | number | Computed time scale |
| `.getEffectiveWeight()` | number | Computed weight |

---

## AnimationClip

A reusable set of keyframe tracks. Typically loaded from GLTF files.

### Constructor

```js
const clip = new THREE.AnimationClip(name, duration, tracks, blendMode);
```

- `name` -- string identifier (GLTF clips use names from the file)
- `duration` -- seconds; `-1` to auto-calculate from tracks
- `tracks` -- array of `KeyframeTrack` objects
- `blendMode` -- optional blend mode constant

### Key Static Methods

| Method | Description |
|--------|-------------|
| `AnimationClip.findByName(arrayOrObject, name)` | Look up clip by name |
| `AnimationClip.CreateFromMorphTargetSequence(name, targets, fps, noLoop)` | Create clip from morph targets |
| `AnimationClip.parse(json)` | Deserialize from JSON |

---

## KeyframeTrack Types

| Track Type | Value Type | Use Case |
|------------|-----------|----------|
| `VectorKeyframeTrack` | Vector3 | Position, scale |
| `QuaternionKeyframeTrack` | Quaternion | Rotation (uses slerp) |
| `NumberKeyframeTrack` | number | Opacity, intensity |
| `BooleanKeyframeTrack` | boolean | Visibility toggles |
| `ColorKeyframeTrack` | Color | Color animation |
| `StringKeyframeTrack` | string | Discrete string values |

### Interpolation Modes

| Constant | Behavior |
|----------|----------|
| `THREE.InterpolateDiscrete` | Step function, no smoothing |
| `THREE.InterpolateLinear` | Linear interpolation (default) |
| `THREE.InterpolateSmooth` | Cubic spline interpolation |

### PropertyBinding Path Format

```
"meshName.position"                    // animate position
"meshName.material.opacity"            // animate material property
"meshName.morphTargetInfluences[0]"    // animate morph target
"boneName.quaternion"                  // animate bone rotation
```

---

## Clock

### Constructor

```js
const clock = new THREE.Clock(autoStart); // autoStart defaults to true
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `.getDelta()` | number | Seconds since last `getDelta()` call |
| `.getElapsedTime()` | number | Total elapsed time in seconds |
| `.start()` | void | Start the clock |
| `.stop()` | void | Stop without resetting |

---

## Crossfade Pattern (Character State Machine)

```js
const actions = {};
gltf.animations.forEach((clip) => {
  actions[clip.name] = mixer.clipAction(clip);
});

let currentAction = actions['Idle'];
currentAction.play();

function switchAction(toName, duration = 0.5) {
  const toAction = actions[toName];
  toAction.reset();
  toAction.setEffectiveTimeScale(1);
  toAction.setEffectiveWeight(1);
  toAction.crossFadeFrom(currentAction, duration, true);
  toAction.play();
  currentAction = toAction;
}
```

ALWAYS call `.reset()` on the incoming action before crossfading.
ALWAYS store the current action reference for the next transition.

---

## Additive Animation Blending

```js
const baseAction = mixer.clipAction(baseClip);
const additiveAction = mixer.clipAction(
  additiveClip, undefined, THREE.AdditiveAnimationBlendMode
);

baseAction.play();
additiveAction.play();
additiveAction.setEffectiveWeight(0.5);
```

Use additive blending for layered effects: breathing, damage reactions, aim offsets.

---

## Morph Target Animation

```js
// Manual control
mesh.morphTargetInfluences[0] = Math.sin(elapsed) * 0.5 + 0.5;

// Via GLTF animation clip (preferred)
const morphAction = mixer.clipAction(morphClip);
morphAction.play();
```

---

## Reference Links

- [references/methods.md](references/methods.md) -- Full API signatures
- [references/examples.md](references/examples.md) -- Working code examples
- [references/anti-patterns.md](references/anti-patterns.md) -- What NOT to do

### Official Sources

- https://threejs.org/docs/#api/en/animation/AnimationMixer
- https://threejs.org/docs/#api/en/animation/AnimationAction
- https://threejs.org/docs/#api/en/animation/AnimationClip
- https://threejs.org/docs/#api/en/animation/KeyframeTrack
- https://threejs.org/docs/#api/en/core/Clock
- https://threejs.org/examples/#webgl_animation_skinning_blending
````

### `atelier/.claude/skills/threejs-impl-animation/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-impl-audio/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-impl-audio
description: >
  Use when adding sound to a Three.js scene: background music, 3D
  spatial audio, or audio visualization. Prevents the common mistake
  of ignoring browser autoplay policy, not attaching AudioListener to
  camera, or wrong distance model. Covers AudioListener, Audio,
  PositionalAudio, AudioAnalyser.
  Keywords: audio, sound, AudioListener, PositionalAudio, 3D audio, spatial audio, music, AudioAnalyser, Web Audio API, play sound, add music, sound in 3D scene.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-impl-audio

## Quick Reference

### Class Hierarchy

```
EventDispatcher
  └── Object3D
        ├── AudioListener    (receiver — attach to camera)
        ├── Audio            (non-positional — background music, UI sounds)
        └── PositionalAudio  (3D spatial — attached to scene objects)
```

Supporting classes:
- `AudioLoader` — loads audio files into `AudioBuffer`
- `AudioAnalyser` — real-time frequency analysis for visualization

### Architecture Overview

| Component | Role | Attach To |
|-----------|------|-----------|
| `AudioListener` | Virtual ear (Web Audio API destination) | Camera (ALWAYS) |
| `Audio` | Non-positional sound (same volume everywhere) | Any Object3D or scene |
| `PositionalAudio` | 3D spatial sound (volume depends on distance) | Mesh or Object3D in scene |
| `AudioLoader` | Async audio file loader | N/A (utility) |
| `AudioAnalyser` | FFT frequency data extractor | Wraps an Audio instance |

### Critical Warnings

**NEVER** call `sound.play()` without first ensuring the `AudioContext` is resumed after user interaction. Modern browsers ALWAYS suspend the AudioContext until a user gesture (click, tap, keypress) occurs.

**NEVER** create more than one `AudioListener` per scene. Multiple listeners produce undefined spatialization behavior.

**NEVER** set `autoplay = true` and expect playback without user interaction. The browser WILL block it silently.

**ALWAYS** attach the `AudioListener` to the camera. If attached to another object, spatial audio calculations use the wrong reference position.

**ALWAYS** call `listener.context.resume()` inside a user interaction handler before playing any audio.

**NEVER** forget to handle the `onError` callback in `AudioLoader.load()`. Missing audio files fail silently without error handling.

---

## AudioListener Setup

The `AudioListener` is the scene's virtual microphone. It wraps the Web Audio API's `AudioContext` and `AudioDestinationNode`.

```js
import * as THREE from 'three';

const listener = new THREE.AudioListener();
camera.add( listener ); // ALWAYS add to camera
```

### Master Volume Control

```js
listener.setMasterVolume( 0.8 ); // range [0, 1]
const vol = listener.getMasterVolume(); // returns 0.8
```

### Global Audio Filter

```js
const filter = listener.context.createBiquadFilter();
filter.type = 'lowpass';
filter.frequency.value = 1000;
listener.setFilter( filter );
// Later: listener.removeFilter();
```

---

## Audio (Non-Positional)

Use `Audio` for background music, ambient soundscapes, and UI feedback sounds. Volume is identical regardless of listener position.

### Loading and Playing

```js
const sound = new THREE.Audio( listener );
const audioLoader = new THREE.AudioLoader();

audioLoader.load( 'music.mp3', ( buffer ) => {
    sound.setBuffer( buffer );
    sound.setLoop( true );
    sound.setVolume( 0.5 );
    // Do NOT call sound.play() here — wait for user interaction
});
```

### Autoplay Policy Compliance (MANDATORY)

```js
document.addEventListener( 'click', () => {
    if ( listener.context.state === 'suspended' ) {
        listener.context.resume();
    }
    if ( !sound.isPlaying ) {
        sound.play();
    }
}, { once: true } );
```

### Playback Control

```js
sound.play();                    // start playback
sound.pause();                   // pause (resume with play())
sound.stop();                    // stop and reset to beginning
sound.setPlaybackRate( 1.5 );   // 1.5x speed
sound.setDetune( -100 );        // pitch down 1 semitone (100 cents)
```

### Alternative Sources

```js
// HTML5 media element (for streaming large files)
const audioEl = new Audio( 'long-track.mp3' );
sound.setMediaElementSource( audioEl );

// Microphone input
navigator.mediaDevices.getUserMedia( { audio: true } ).then( ( stream ) => {
    sound.setMediaStreamSource( stream );
});
```

---

## PositionalAudio (3D Spatial)

Use `PositionalAudio` for sounds that exist at a location in the scene. Volume and stereo panning change based on the listener's distance and orientation.

### Basic Setup

```js
const positionalSound = new THREE.PositionalAudio( listener );

audioLoader.load( 'engine.ogg', ( buffer ) => {
    positionalSound.setBuffer( buffer );
    positionalSound.setRefDistance( 20 );
    positionalSound.setRolloffFactor( 1 );
    positionalSound.setDistanceModel( 'inverse' );
    positionalSound.setLoop( true );
    positionalSound.setVolume( 0.5 );
});

mesh.add( positionalSound ); // sound position follows the mesh
```

### Distance Model Decision Tree

| Model | When to Use | Behavior |
|-------|-------------|----------|
| `'inverse'` (default) | Realistic environments | Gradual rolloff; NEVER reaches zero |
| `'linear'` | Controlled radius (e.g., room-based) | Volume drops to zero at `maxDistance` |
| `'exponential'` | Dramatic close/far contrast | Steep falloff curve |

**Choosing parameters:**

- **`refDistance`** — Distance at which volume is 100%. Set to the "comfortable listening range" in scene units. Typical: `1` to `20`.
- **`maxDistance`** — ONLY matters for `'linear'` model. Ignored by `'inverse'` and `'exponential'`.
- **`rolloffFactor`** — Speed of volume decrease. For `'inverse'`: `1` = realistic. For `'linear'`: `1` = full range. Higher values = faster rolloff.

### Directional Audio Cone

```js
positionalSound.setDirectionalCone( 180, 360, 0.1 );
// coneInnerAngle: 180° — full volume zone
// coneOuterAngle: 360° — transition zone
// coneOuterGain: 0.1  — volume outside outer cone (10%)
```

---

## AudioLoader

ALWAYS use `AudioLoader` to load audio files. It returns an `AudioBuffer` via callback.

```js
const loader = new THREE.AudioLoader();

loader.load(
    'sound.ogg',
    ( buffer ) => { sound.setBuffer( buffer ); },   // onLoad
    ( xhr ) => { console.log( (xhr.loaded / xhr.total * 100) + '% loaded' ); }, // onProgress
    ( err ) => { console.error( 'Audio load failed:', err ); }  // onError — ALWAYS handle
);
```

**Supported formats:** MP3, OGG, WAV, AAC. OGG has the best compression-to-quality ratio but is NOT supported in Safari. ALWAYS provide MP3 as a fallback for cross-browser compatibility.

---

## AudioAnalyser

Wraps the Web Audio API's `AnalyserNode` for real-time frequency visualization.

```js
const analyser = new THREE.AudioAnalyser( sound, 256 );
// fftSize MUST be a power of 2: 32, 64, 128, 256, 512, 1024, 2048

function animate() {
    requestAnimationFrame( animate );

    const data = analyser.getFrequencyData();    // Uint8Array, length = fftSize / 2
    const avg = analyser.getAverageFrequency();  // number (0-255)

    // Drive visuals from audio data
    mesh.scale.y = 1 + avg / 128;
    renderer.render( scene, camera );
}
```

### Frequency Data Details

- `getFrequencyData()` returns a `Uint8Array` with `fftSize / 2` elements
- Each element ranges from `0` to `255` (decibel magnitude)
- Index `0` = lowest frequency, last index = highest frequency
- `getAverageFrequency()` returns the arithmetic mean of all bins

---

## Integration Checklist

1. Create ONE `AudioListener` and add it to the camera
2. Create `Audio` or `PositionalAudio` with the listener
3. Load audio with `AudioLoader`
4. Set buffer, volume, loop, and distance properties
5. Add user interaction handler to resume `AudioContext`
6. Call `play()` ONLY after user interaction
7. For spatial audio: add `PositionalAudio` as child of the target mesh

---

## Reference Links

- [references/methods.md](references/methods.md) -- Complete API signatures for AudioListener, Audio, PositionalAudio, AudioLoader, AudioAnalyser
- [references/examples.md](references/examples.md) -- Working code examples for common audio scenarios
- [references/anti-patterns.md](references/anti-patterns.md) -- What NOT to do with Three.js audio

### Official Sources

- https://threejs.org/docs/#api/en/audio/AudioListener
- https://threejs.org/docs/#api/en/audio/Audio
- https://threejs.org/docs/#api/en/audio/PositionalAudio
- https://threejs.org/docs/#api/en/audio/AudioAnalyser
- https://threejs.org/docs/#api/en/loaders/AudioLoader
````

### `atelier/.claude/skills/threejs-impl-audio/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-impl-drei/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-impl-drei
description: >
  Use when using Drei helper components with React Three Fiber:
  controls, environment maps, text rendering, HTML overlays, or
  performance helpers. Prevents the common mistake of not wrapping
  useGLTF in Suspense, using wrong Environment preset name, or
  forgetting makeDefault on controls. Covers 150+ Drei components
  across controls, environment, text, materials, loaders, performance.
  Keywords: Drei, @react-three/drei, OrbitControls, Environment, useGLTF, useTexture, Html, Text, Stage, ContactShadows, Instances, helper components, ready-made, quick setup React 3D.
license: MIT
compatibility: "Designed for Claude Code. Requires @react-three/drei, @react-three/fiber 8.x+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-impl-drei

## Quick Reference

### Installation

```bash
npm install @react-three/drei @react-three/fiber three
```

### Critical Warnings

**ALWAYS** wrap components that use loader hooks (`useGLTF`, `useTexture`, `useFBX`, `useKTX2`, `useFont`) in `<Suspense fallback={...}>`. Omitting Suspense causes the entire React tree to crash.

**ALWAYS** add `makeDefault` to your primary camera controls (`<OrbitControls makeDefault />`). Without `makeDefault`, Drei controls do NOT integrate with R3F's event system and pointer events break.

**NEVER** use an invalid `Environment` preset name. The ONLY valid presets are: `apartment`, `city`, `dawn`, `forest`, `lobby`, `night`, `park`, `studio`, `sunset`, `warehouse`.

**NEVER** forget to call `.preload()` for critical assets. Use `useGLTF.preload('/model.glb')` at module scope to start loading before component mount.

**ALWAYS** use `<Instances>` for rendering more than 100 identical meshes. Individual meshes cause one draw call each; instances batch them into one.

---

## Controls

### OrbitControls

The most common camera control. Orbit, zoom, and pan around a target.

```jsx
import { OrbitControls } from '@react-three/drei'

<OrbitControls
  makeDefault           // ALWAYS add — integrates with R3F events
  enableDamping         // smooth movement
  dampingFactor={0.05}
  minDistance={2}
  maxDistance={20}
  minPolarAngle={0}
  maxPolarAngle={Math.PI / 2}  // prevent going below ground
/>
```

### Other Controls

| Component | Use Case |
|-----------|----------|
| `CameraControls` | Full-featured camera (recommended for complex scenes) |
| `MapControls` | Top-down map navigation (orbit restricted to vertical axis) |
| `PresentationControls` | Drag-to-rotate with spring physics (product viewers) |
| `ScrollControls` | Scroll-driven animation (`pages` prop sets scroll length) |
| `TransformControls` | Translate/rotate/scale gizmo on selected objects |
| `DragControls` | Drag objects in 3D space |
| `KeyboardControls` | Keyboard input as React context |
| `FaceControls` | Face-tracking camera movement |

### ScrollControls Pattern

```jsx
import { ScrollControls, useScroll } from '@react-three/drei'

<ScrollControls pages={3} damping={0.1}>
  <ScrollScene />
</ScrollControls>

function ScrollScene() {
  const scroll = useScroll()
  useFrame(() => {
    const offset = scroll.offset // 0 to 1
  })
  return <mesh />
}
```

---

## Environment and Staging

### Environment

Loads HDR environment maps for realistic reflections and lighting.

```jsx
import { Environment } from '@react-three/drei'

// Preset (downloads from polyhaven CDN)
<Environment preset="city" background blur={0.5} />

// Custom HDR file
<Environment files="/env.hdr" background />

// Custom environment with Lightformers
<Environment background>
  <Lightformer form="rect" intensity={2} position={[0, 5, -5]} scale={[10, 5, 1]} />
</Environment>
```

**Valid presets:** `apartment`, `city`, `dawn`, `forest`, `lobby`, `night`, `park`, `studio`, `sunset`, `warehouse`.

### Stage

Complete lighting and shadow setup in one component. Ideal for product viewers.

```jsx
import { Stage } from '@react-three/drei'

<Stage preset="rembrandt" intensity={0.5} environment="city" adjustCamera>
  <Model />
</Stage>
```

### Shadow Components

| Component | Use Case | Key Props |
|-----------|----------|-----------|
| `ContactShadows` | Soft ground shadows (no light needed) | `opacity`, `scale`, `blur`, `far`, `resolution`, `color` |
| `AccumulativeShadows` | High-quality baked soft shadows | `frames`, `alphaTest`, `scale`, `opacity` |
| `RandomizedLight` | Child of AccumulativeShadows | `amount`, `radius`, `intensity`, `position` |
| `BakeShadows` | Bake shadow maps once, stop updating | — |
| `SoftShadows` | PCSS soft shadows for real-time lights | — |

### AccumulativeShadows Pattern

```jsx
<AccumulativeShadows temporal frames={100} scale={10} position={[0, -0.5, 0]}>
  <RandomizedLight amount={8} radius={4} position={[5, 5, -10]} />
</AccumulativeShadows>
```

### Atmosphere

| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `Sky` | Procedural sky dome | `sunPosition`, `turbidity`, `rayleigh` |
| `Stars` | Particle starfield | `radius`, `count`, `factor`, `fade` |
| `Sparkles` | Floating particles | `count`, `size`, `speed`, `color` |
| `Cloud` | Volumetric clouds | `opacity`, `speed`, `segments`, `bounds` |

---

## Text and HTML

### Text (SDF)

High-quality 2D text rendered with signed distance fields via troika-three-text.

```jsx
import { Text } from '@react-three/drei'

<Text
  fontSize={0.5}
  color="white"
  anchorX="center"
  anchorY="middle"
  maxWidth={2}
  font="/fonts/Inter-Bold.woff"
>
  Hello World
</Text>
```

### Text3D

Extruded 3D geometry text. Requires a JSON font file (use `facetype.js` to convert).

```jsx
import { Text3D, Center } from '@react-three/drei'

<Center>
  <Text3D font="/fonts/Inter_Bold.json" size={0.75} height={0.2} bevelEnabled bevelSize={0.02}>
    Hello
    <meshStandardMaterial color="orange" />
  </Text3D>
</Center>
```

### Html

Renders DOM elements positioned in 3D space.

```jsx
import { Html } from '@react-three/drei'

<mesh position={[0, 2, 0]}>
  <Html
    transform            // transforms with 3D position
    distanceFactor={10}  // scales with distance
    occlude              // hides behind 3D objects
    center               // centers the HTML element
    className="label"
  >
    <div style={{ color: 'white' }}>Annotation</div>
  </Html>
</mesh>
```

### Billboard

ALWAYS faces the camera. Use for labels and sprites.

```jsx
import { Billboard, Text } from '@react-three/drei'

<Billboard follow={true} lockX={false} lockY={false} lockZ={false}>
  <Text fontSize={0.5}>Always Visible</Text>
</Billboard>
```

### Hud

Renders a heads-up display in a separate orthographic scene.

```jsx
import { Hud, OrthographicCamera } from '@react-three/drei'

<Hud renderPriority={1}>
  <OrthographicCamera makeDefault position={[0, 0, 5]} />
  <Text position={[0, 0, 0]} fontSize={0.1}>HUD Text</Text>
</Hud>
```

---

## Materials

| Component | Purpose |
|-----------|---------|
| `MeshReflectorMaterial` | Reflective floors with blur, distortion, resolution |
| `MeshTransmissionMaterial` | Glass with chromatic aberration, distortion, thickness |
| `MeshRefractionMaterial` | Refraction using environment cube map |
| `MeshWobbleMaterial` | Animated wobble on MeshStandardMaterial |
| `MeshDistortMaterial` | Perlin noise distortion on MeshStandardMaterial |
| `MeshDiscardMaterial` | Renders nothing (shadow-only objects) |
| `shaderMaterial` | Helper to create custom ShaderMaterial as JSX |

### MeshReflectorMaterial Example

```jsx
<mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
  <planeGeometry args={[50, 50]} />
  <MeshReflectorMaterial
    blur={[300, 100]}
    resolution={1024}
    mixBlur={1}
    mixStrength={50}
    roughness={1}
    depthScale={1.2}
    minDepthThreshold={0.4}
    maxDepthThreshold={1.4}
    color="#151515"
    metalness={0.5}
  />
</mesh>
```

### shaderMaterial Helper

```jsx
import { shaderMaterial } from '@react-three/drei'
import { extend } from '@react-three/fiber'

const WaveMaterial = shaderMaterial(
  { uTime: 0, uColor: new THREE.Color(0.2, 0.0, 0.1) },
  /* vertex */ `varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  /* fragment */ `uniform float uTime; uniform vec3 uColor; varying vec2 vUv; void main() { gl_FragColor = vec4(vUv * uColor, 1.0); }`
)
extend({ WaveMaterial })
// Usage: <waveMaterial uTime={clock.elapsedTime} />
```

---

## Loaders

**ALWAYS** wrap loader-consuming components in `<Suspense>`.

| Hook | Returns | Preload |
|------|---------|---------|
| `useGLTF(url)` | `{ nodes, materials, scene, animations }` | `useGLTF.preload(url)` |
| `useTexture(url)` | `THREE.Texture` or map object | `useTexture.preload(url)` |
| `useFBX(url)` | `THREE.Group` | `useFBX.preload(url)` |
| `useKTX2(url)` | Compressed texture | `useKTX2.preload(url)` |
| `useFont(url)` | Font data for Text3D | `useFont.preload(url)` |
| `useAnimations(clips, ref)` | `{ actions, names, mixer, ref }` | — |
| `useVideoTexture(url)` | `THREE.VideoTexture` | — |

### useGLTF Pattern

```jsx
import { useGLTF } from '@react-three/drei'

function Model(props) {
  const { nodes, materials } = useGLTF('/model.glb')
  return (
    <group {...props}>
      <mesh geometry={nodes.Body.geometry} material={materials.Metal} />
    </group>
  )
}
useGLTF.preload('/model.glb')
```

### useTexture with Multiple Maps

```jsx
const textures = useTexture({
  map: '/color.jpg',
  normalMap: '/normal.jpg',
  roughnessMap: '/roughness.jpg',
  aoMap: '/ao.jpg',
})
// Spread directly onto material
<meshStandardMaterial {...textures} />
```

### useAnimations Pattern

```jsx
function AnimatedModel() {
  const group = useRef()
  const { nodes, animations } = useGLTF('/character.glb')
  const { actions } = useAnimations(animations, group)

  useEffect(() => {
    actions['Walk']?.play()
    return () => actions['Walk']?.stop()
  }, [actions])

  return <group ref={group}><primitive object={nodes.Scene} /></group>
}
```

---

## Performance

### Instances

ALWAYS use for large numbers of identical meshes (>100). Reduces draw calls from N to 1.

```jsx
import { Instances, Instance } from '@react-three/drei'

<Instances limit={1000} range={1000}>
  <boxGeometry />
  <meshStandardMaterial />
  {positions.map((pos, i) => (
    <Instance key={i} position={pos} color="orange" />
  ))}
</Instances>
```

### Merged

Merges different geometries into a single draw call.

```jsx
import { Merged } from '@react-three/drei'

function Furniture({ nodes }) {
  return (
    <Merged meshes={[nodes.Chair, nodes.Table, nodes.Lamp]}>
      {(Chair, Table, Lamp) => (
        <>
          <Chair position={[0, 0, 0]} />
          <Table position={[2, 0, 0]} />
          <Lamp position={[1, 1, 0]} />
        </>
      )}
    </Merged>
  )
}
```

### Performance Helpers

| Component | Purpose |
|-----------|---------|
| `Detailed` | LOD — switches geometry based on camera distance |
| `BakeShadows` | Bakes shadows once, stops updating |
| `AdaptiveDpr` | Lowers device pixel ratio during performance drops |
| `AdaptiveEvents` | Reduces event frequency during performance drops |
| `PerformanceMonitor` | Monitors FPS, triggers regression callbacks |
| `Bvh` | BVH-accelerated raycasting for complex meshes |
| `meshBounds` | Fast bounding-box raycasting (replaces per-triangle) |

### PerformanceMonitor Pattern

```jsx
<PerformanceMonitor
  onIncline={() => setDpr(2)}
  onDecline={() => setDpr(1)}
  flipflops={3}
  onFallback={() => setDpr(0.5)}
/>
```

---

## Staging and Layout

| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `Center` | Centers children at origin | `top`, `right`, `bottom`, `left`, `front`, `back` |
| `Float` | Floating hover animation | `speed`, `rotationIntensity`, `floatIntensity` |
| `Bounds` | Auto-fit camera to content | `fit`, `clip`, `observe`, `margin` |
| `Resize` | Normalizes children to unit size | `width`, `height`, `depth` |

---

## Abstractions and Effects

| Component | Purpose |
|-----------|---------|
| `Edges` | Renders wireframe edges |
| `Outlines` | Screen-space outlines |
| `Trail` | Motion trail behind objects |
| `Decal` | Project texture onto mesh surface |
| `Splat` | Gaussian splatting renderer |
| `Clone` | Deep clone with shared geometry/materials |
| `Image` | Texture-mapped plane with shader effects |
| `MeshPortalMaterial` | Portal — renders scene inside mesh surface |
| `GradientTexture` | Procedural gradient texture |

---

## Gizmos

| Component | Purpose |
|-----------|---------|
| `GizmoHelper` | Viewport orientation widget |
| `PivotControls` | Interactive pivot gizmo (translate/rotate/scale) |
| `TransformControls` | Three.js TransformControls wrapper |
| `Grid` | Infinite configurable grid plane |
| `Helper / useHelper` | Visualize light/camera helpers |

---

## Component Selection Guide

| Scenario | Component |
|----------|-----------|
| Product viewer | `Stage` + `OrbitControls` + `Environment` |
| Architectural walkthrough | `CameraControls` + `Environment` + `ContactShadows` |
| Scrolling experience | `ScrollControls` + `useScroll` |
| Data visualization | `Instances` + `Html` + `Billboard` |
| Text labels in 3D | `Text` (2D) or `Text3D` (extruded) + `Billboard` |
| Glass/transparent objects | `MeshTransmissionMaterial` + `Environment` |
| Reflective floors | `MeshReflectorMaterial` |
| Large identical meshes | `Instances` (>100) or `Merged` (mixed geometries) |
| Model loading | `useGLTF` + `Suspense` + `.preload()` |
| HUD / overlay | `Hud` or `Html` with `fullscreen` |

---

## Reference Links

- [references/methods.md](references/methods.md) -- Key component props and hook signatures
- [references/examples.md](references/examples.md) -- Complete working examples
- [references/anti-patterns.md](references/anti-patterns.md) -- Common mistakes and fixes

### Official Sources

- https://drei.docs.pmnd.rs/
- https://github.com/pmndrs/drei
- https://r3f.docs.pmnd.rs/
````

### `atelier/.claude/skills/threejs-impl-drei/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-impl-ifc-viewer/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-impl-ifc-viewer
description: >
  Use when loading and viewing IFC/BIM models in a Three.js scene.
  Prevents the common mistake of using deprecated web-ifc-three,
  ignoring AGPL-3.0 license implications, or loading large IFC files
  without streaming. Covers web-ifc (MIT), @thatopen/components
  (AGPL-3.0), IFC loading, spatial tree, property extraction.
  Keywords: IFC, BIM, web-ifc, IFC viewer, @thatopen/components, building model, architecture, IFC loading, spatial tree, BIM viewer, show IFC in browser, load building, web BIM viewer.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-impl-ifc-viewer

## Quick Reference

### Library Comparison

| Library | License | Level | Status | Use Case |
|---------|---------|-------|--------|----------|
| `web-ifc` | MIT | Low-level WASM parser | Active (v0.77+) | Custom pipelines, full control |
| `@thatopen/components` | MIT (v3.x) | High-level BIM toolkit | Active (v3.3.2+) | Full BIM viewers, rapid prototyping |
| `@thatopen/components-front` | MIT | Browser-specific extensions | Active | UI, advanced visualization |
| `web-ifc-three` | — | Deprecated bridge | **DEAD** | **NEVER use** |
| `openbim-components` (v1) | — | Deprecated toolkit | **DEAD** | **NEVER use** |

### Package Installation

```bash
# Low-level approach (MIT, full control)
npm install web-ifc three

# High-level approach (MIT, batteries-included)
npm install @thatopen/components @thatopen/components-front web-ifc three
```

### Critical Warnings

**LICENSE HISTORY WARNING**: The @thatopen packages (v3.x) are licensed under **MIT**. However, older IFC.js ecosystem packages (openbim-components v1, IFC.js v0.x) used **AGPL-3.0**. ALWAYS verify the license of the exact package version you install. If using any package with AGPL-3.0, your entire application MUST be open-sourced under AGPL-3.0 or a compatible license.

**NEVER** use `web-ifc-three` -- it is deprecated and unmaintained. Use `web-ifc` directly or `@thatopen/components` instead.

**NEVER** use `openbim-components` (v1) -- it is deprecated. Use `@thatopen/components` (v3.x) instead.

**NEVER** load entire IFC geometry at once for files >50MB -- ALWAYS stream or load geometry on demand. WASM memory is limited and cannot be reclaimed without page reload.

**NEVER** forget to call `ifcApi.CloseModel(modelID)` after processing -- WASM memory leaks are permanent until page reload.

**ALWAYS** call `components.dispose()` when unmounting a @thatopen viewer -- failure to do so leaks GPU memory, Three.js objects, and event listeners.

**ALWAYS** initialize `IfcAPI` asynchronously -- `await ifcApi.Init()` MUST complete before any model operations.

---

## Approach 1: web-ifc (Low-Level WASM Parser)

### When to Use

- You need full control over geometry extraction and rendering
- You are building a custom rendering pipeline
- You want MIT-licensed code only
- You need to extract IFC properties without rendering geometry

### WASM Setup

```javascript
import * as WebIFC from 'web-ifc';

const ifcApi = new WebIFC.IfcAPI();
ifcApi.SetWasmPath('./');  // MUST point to directory containing web-ifc.wasm
await ifcApi.Init();       // ALWAYS await before any operations
```

**WASM file requirement**: The `web-ifc.wasm` file MUST be served from a location accessible by the browser. Copy it from `node_modules/web-ifc/` to your public/static directory. Bundlers like Vite require explicit configuration to serve WASM files.

### IfcAPI Core Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `Init()` | `() => Promise<void>` | Initialize WASM module |
| `SetWasmPath(path)` | `(string) => void` | Set directory containing .wasm file |
| `OpenModel(data, settings?)` | `(Uint8Array, object?) => number` | Load IFC data, returns modelID |
| `CloseModel(modelID)` | `(number) => void` | Release model memory |
| `GetGeometry(modelID, expressID)` | `(number, number) => object` | Get geometry for element |
| `GetFlatMesh(modelID, expressID)` | `(number, number) => FlatMesh` | Get flattened mesh data |
| `GetPlacedGeometry(modelID, pg)` | `(number, PlacedGeometry) => MeshData` | Get positioned geometry with transform |
| `GetLine(modelID, expressID, flatten?)` | `(number, number, boolean?) => object` | Read single IFC entity by expressID |
| `GetAllLines(modelID)` | `(number) => number[]` | Get all express IDs in model |
| `GetLineIDsWithType(modelID, type)` | `(number, number) => number[]` | Get IDs by IFC type constant |
| `GetAllTypesOfModel(modelID)` | `(number) => TypeInfo[]` | List all entity types in model |

### Geometry Extraction Pattern

```javascript
const modelID = ifcApi.OpenModel(ifcData); // ifcData: Uint8Array

const wallIDs = ifcApi.GetLineIDsWithType(modelID, WebIFC.IFCWALL);
for (const wallID of wallIDs) {
  const flatMesh = ifcApi.GetFlatMesh(modelID, wallID);
  for (const pg of flatMesh.geometries) {
    const meshData = ifcApi.GetPlacedGeometry(modelID, pg);
    // meshData.vertexData: Float32Array (interleaved position + normal, 6 floats per vertex)
    // meshData.indexData: Uint32Array (triangle indices)
    // pg.flatTransformation: Float64Array (4x4 column-major matrix)
    // pg.color: { x: r, y: g, z: b, w: alpha } (0-1 range)
  }
}

ifcApi.CloseModel(modelID); // ALWAYS release when done
```

### Converting web-ifc Geometry to Three.js

```javascript
import * as THREE from 'three';

function ifcMeshToThree(meshData, placedGeometry) {
  const { vertexData, indexData } = meshData;

  // vertexData is interleaved: [px, py, pz, nx, ny, nz, px, py, pz, nx, ny, nz, ...]
  const posFloats = new Float32Array(vertexData.length / 2);
  const normFloats = new Float32Array(vertexData.length / 2);
  for (let i = 0; i < vertexData.length; i += 6) {
    const j = i / 2;
    posFloats[j]     = vertexData[i];
    posFloats[j + 1] = vertexData[i + 1];
    posFloats[j + 2] = vertexData[i + 2];
    normFloats[j]     = vertexData[i + 3];
    normFloats[j + 1] = vertexData[i + 4];
    normFloats[j + 2] = vertexData[i + 5];
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(posFloats, 3));
  geometry.setAttribute('normal', new THREE.BufferAttribute(normFloats, 3));
  geometry.setIndex(new THREE.BufferAttribute(indexData, 1));

  const { x: r, y: g, z: b, w: a } = placedGeometry.color;
  const material = new THREE.MeshPhongMaterial({
    color: new THREE.Color(r, g, b),
    opacity: a,
    transparent: a < 1,
    side: THREE.DoubleSide,
  });

  const mesh = new THREE.Mesh(geometry, material);

  // Apply the 4x4 transform matrix (column-major)
  const mat = new THREE.Matrix4();
  mat.fromArray(placedGeometry.flatTransformation);
  mesh.applyMatrix4(mat);

  return mesh;
}
```

### IFC Property Extraction

```javascript
// Read a specific entity
const wall = ifcApi.GetLine(modelID, wallExpressID, true); // flatten=true resolves references
console.log(wall.Name?.value);       // "Basic Wall:Generic - 200mm"
console.log(wall.GlobalId?.value);   // IFC GUID

// Get all property sets for an element
const relDefines = ifcApi.GetLineIDsWithType(modelID, WebIFC.IFCRELDEFINESBYPROPERTIES);
for (const relID of relDefines) {
  const rel = ifcApi.GetLine(modelID, relID, false);
  // Check if this relation references our element
  // rel.RelatedObjects contains expressIDs of related elements
  // rel.RelatingPropertyDefinition points to the property set
}
```

### IFC Type Constants

| Constant | IFC Entity |
|----------|-----------|
| `WebIFC.IFCWALL` | Walls |
| `WebIFC.IFCWALLSTANDARDCASE` | Standard walls |
| `WebIFC.IFCSLAB` | Slabs / floors |
| `WebIFC.IFCCOLUMN` | Columns |
| `WebIFC.IFCBEAM` | Beams |
| `WebIFC.IFCDOOR` | Doors |
| `WebIFC.IFCWINDOW` | Windows |
| `WebIFC.IFCROOF` | Roofs |
| `WebIFC.IFCSTAIR` | Stairs |
| `WebIFC.IFCSPACE` | Spaces / rooms |
| `WebIFC.IFCSITE` | Site |
| `WebIFC.IFCBUILDING` | Building |
| `WebIFC.IFCBUILDINGSTOREY` | Storey / floor level |
| `WebIFC.IFCPROJECT` | Project root |
| `WebIFC.IFCRELDEFINESBYPROPERTIES` | Property set relations |
| `WebIFC.IFCPROPERTYSET` | Property sets |
| `WebIFC.IFCPROPERTYSINGLEVALUE` | Individual property values |

---

## Approach 2: @thatopen/components (High-Level BIM Toolkit)

### When to Use

- You need a full-featured BIM viewer quickly
- You want built-in fragment optimization for large models
- You need element highlighting, section planes, or floor plans
- MIT license (v3.x) is acceptable for your project

### Architecture Setup

```javascript
import * as OBC from '@thatopen/components';

const components = new OBC.Components();
const worlds = components.get(OBC.Worlds);
const world = worlds.create();

// Scene
world.scene = new OBC.SimpleScene(components);
world.scene.setup(); // Adds default lights and grid

// Camera
world.camera = new OBC.SimpleCamera(components);
world.camera.controls.setLookAt(10, 10, 10, 0, 0, 0);

// Renderer (container is an HTMLDivElement)
world.renderer = new OBC.SimpleRenderer(components, container);

// ALWAYS call init after setup
components.init();
```

### Loading IFC Files

```javascript
const ifcLoader = components.get(OBC.IfcLoader);
await ifcLoader.setup(); // Downloads and initializes WASM

// Load from file input
const file = event.target.files[0];
const data = new Uint8Array(await file.arrayBuffer());
const model = await ifcLoader.load(data);

// model is added to the active world automatically
// model contains Three.js Group with fragment meshes
```

### Key Components

| Component | Access Pattern | Purpose |
|-----------|---------------|---------|
| `OBC.Components` | `new OBC.Components()` | Central manager for all subsystems |
| `OBC.Worlds` | `components.get(OBC.Worlds)` | Multi-world environment management |
| `OBC.SimpleScene` | Constructor | Three.js scene wrapper with defaults |
| `OBC.SimpleCamera` | Constructor | Camera with built-in orbit controls |
| `OBC.SimpleRenderer` | Constructor | WebGL renderer bound to DOM element |
| `OBC.IfcLoader` | `components.get(OBC.IfcLoader)` | IFC file loading and fragment conversion |
| `OBC.FragmentsManager` | `components.get(OBC.FragmentsManager)` | Efficient batched geometry management |
| `OBC.Highlighter` | `components.get(OBC.Highlighter)` | Element selection and highlighting |
| `OBC.Clipper` | `components.get(OBC.Clipper)` | Section plane tools |
| `OBC.Plans` | `components.get(OBC.Plans)` | Floor plan generation |

### Fragment System

The fragment system converts IFC geometry into batched draw calls. This is critical for performance with large BIM models (10,000+ elements).

- Each IFC type gets batched into a single fragment mesh
- Fragments share materials where possible, minimizing state changes
- Individual elements can still be picked, highlighted, and hidden by expressID
- ALWAYS use fragments for models with >1,000 elements

### Cleanup

```javascript
// ALWAYS dispose when unmounting the viewer
components.dispose();
// This releases: Three.js scene, renderer, geometries, materials, textures,
// WASM memory, event listeners, and all component state
```

---

## IFC Spatial Tree

IFC files follow a hierarchical spatial structure:

```
IFCPROJECT
  └── IFCSITE
        └── IFCBUILDING
              ├── IFCBUILDINGSTOREY (Level 0)
              │     ├── IFCWALL
              │     ├── IFCSLAB
              │     └── IFCSPACE
              └── IFCBUILDINGSTOREY (Level 1)
                    ├── IFCWALL
                    ├── IFCCOLUMN
                    └── IFCDOOR
```

Spatial containment is defined by `IFCRELCONTAINEDINSPATIALSTRUCTURE` and `IFCRELAGGREGATES` relationships. ALWAYS traverse these relationships to build a navigable tree -- do NOT assume flat element lists represent the building structure.

---

## Memory Management for Large IFC Files

| File Size | Strategy |
|-----------|----------|
| <10MB | Load entirely, render all geometry at once |
| 10-50MB | Load entirely, use fragment batching |
| 50-200MB | Stream geometry by storey or type, dispose unused |
| >200MB | Server-side preprocessing into fragments, load on demand |

### Rules

- ALWAYS monitor WASM heap usage -- web-ifc allocates in WASM linear memory which has a hard cap
- ALWAYS dispose geometry that is not currently visible (off-screen storeys, hidden types)
- NEVER keep duplicate geometry in both WASM and JavaScript heap
- ALWAYS use `BufferGeometry` (never legacy `Geometry`)
- ALWAYS call `geometry.dispose()` and `material.dispose()` when removing meshes from scene

---

## Reference Links

- [references/methods.md](references/methods.md) -- Complete API signatures for web-ifc and @thatopen/components
- [references/examples.md](references/examples.md) -- Working code examples for IFC loading and viewing
- [references/anti-patterns.md](references/anti-patterns.md) -- What NOT to do when working with IFC in Three.js

### Official Sources

- https://github.com/IFCjs/web-ifc
- https://github.com/ThatOpen/engine_components
- https://docs.thatopen.com/
- https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/
````

### `atelier/.claude/skills/threejs-impl-ifc-viewer/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-impl-lighting/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-impl-lighting
description: >
  Use when setting up lighting in a Three.js scene: ambient, directional,
  point, spot, area, or environment lighting. Prevents the common mistake
  of too many shadow-casting lights, wrong intensity units, or missing
  environment maps for PBR. Covers all 7 light types, PMREMGenerator,
  HDR environment maps, physically correct intensity, helpers.
  Keywords: lighting, AmbientLight, DirectionalLight, PointLight, SpotLight, RectAreaLight, HemisphereLight, environment map, HDR, IBL, scene too dark, add light, realistic lighting.
  PMREMGenerator, scene.environment.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-impl-lighting

## Quick Reference

### Light Types at a Glance

| Light | Shadows | Direction | Cost | Intensity Unit (r160+) |
|-------|---------|-----------|------|----------------------|
| `AmbientLight` | NO | None (uniform) | Negligible | Unitless multiplier |
| `HemisphereLight` | NO | Vertical gradient | Negligible | Unitless multiplier |
| `DirectionalLight` | YES | Parallel rays | Moderate | Lux |
| `PointLight` | YES (6-pass!) | Omnidirectional | High | Candela |
| `SpotLight` | YES | Cone | High | Candela |
| `RectAreaLight` | NO | Planar emission | Very high | Nits (cd/m2) |
| `LightProbe` | NO | Spherical harmonics | Low | Unitless multiplier |

### Critical Warnings

**NEVER** use `AmbientLight` as the sole light source -- it produces flat, dimensionless rendering. ALWAYS combine it with at least one directional or point light.

**NEVER** forget to add `light.target` to the scene when repositioning a `DirectionalLight` or `SpotLight` target -- the direction vector will NOT update without it.

**NEVER** use `RectAreaLight` without calling `RectAreaLightUniformsLib.init()` first (WebGLRenderer) or `RectAreaLightTexturesLib` (WebGPURenderer) -- the light will render incorrectly or not at all.

**NEVER** use more than 1-2 shadow-casting `PointLight` instances -- each requires 6 shadow map render passes. Use `SpotLight` with shadows as a cheaper alternative.

**ALWAYS** call `pmremGenerator.dispose()` after generating environment maps -- PMREMGenerator allocates significant GPU memory.

**ALWAYS** set `renderer.toneMapping` when using physically correct intensity values -- without tone mapping, high lux/candela values produce blown-out white scenes.

---

## Light Class Hierarchy

All lights inherit from `Light`, which extends `Object3D`:

```
Object3D
  └── Light (abstract: .color, .intensity, .dispose())
        ├── AmbientLight        — uniform fill
        ├── HemisphereLight     — sky/ground gradient
        ├── DirectionalLight    — parallel rays (sun)
        ├── PointLight          — omnidirectional (bulb)
        ├── SpotLight           — cone (flashlight)
        ├── RectAreaLight       — planar (window/panel)
        └── LightProbe          — spherical harmonics (IBL)
```

The `Light` base class provides:
- `.color` (Color) -- light color, default `0xffffff`
- `.intensity` (number) -- strength multiplier, default `1`
- `.isLight` (boolean, readonly) -- ALWAYS `true`
- `.dispose()` -- releases GPU resources

---

## Physically Correct Lighting (r160+)

As of r160+, ALL lighting uses physically based units by default. The legacy `renderer.useLegacyLights` property was removed.

| Light Type | Intensity Unit | Description |
|-----------|---------------|-------------|
| DirectionalLight | **Lux** (lm/m2) | Sunlight: 50,000-100,000 lux |
| PointLight | **Candela** (lm/sr) | 100W bulb: ~1700 cd |
| SpotLight | **Candela** (lm/sr) | Stage spot: ~10,000 cd |
| RectAreaLight | **Nits** (cd/m2) | LED panel: ~500-5000 nits |
| AmbientLight | Unitless | Multiplier, no physical unit |
| HemisphereLight | Unitless | Multiplier, no physical unit |

The `.power` property on PointLight, SpotLight, and RectAreaLight gives luminous power in **lumens**:
- PointLight: `power = intensity * 4 * Math.PI`
- SpotLight: `power = intensity * Math.PI`

**ALWAYS** pair physically correct intensities with tone mapping:

```javascript
import * as THREE from 'three';

renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
```

---

## The 7 Light Types

### AmbientLight

Uniform fill light. NO direction, NO shadows. Use for base illumination only.

```javascript
const ambient = new THREE.AmbientLight(0x404040, 0.5);
scene.add(ambient);
```

### HemisphereLight

Sky-to-ground gradient. NO shadows. Simulates outdoor ambient with sky and ground bounce.

```javascript
const hemi = new THREE.HemisphereLight(0xffffbb, 0x080820, 1.0);
scene.add(hemi);
```

Properties: `.groundColor` (Color) -- lower hemisphere color.

### DirectionalLight

Parallel rays simulating distant light (sun). Direction = `light.position` to `light.target.position`.

```javascript
const sun = new THREE.DirectionalLight(0xffffff, 3);
sun.position.set(5, 10, 7.5);
scene.add(sun);
scene.add(sun.target); // REQUIRED for target repositioning
```

Properties: `.target` (Object3D), `.shadow` (DirectionalLightShadow).

### PointLight

Omnidirectional light from a single point. Shadows cost 6 render passes.

```javascript
const bulb = new THREE.PointLight(0xffaa44, 800, 20, 2);
bulb.position.set(0, 3, 0);
scene.add(bulb);
```

Properties: `.distance` (number, `0`=infinite), `.decay` (number, `2`=physically correct), `.power` (lumens).

### SpotLight

Cone-shaped light. ALWAYS set `penumbra >= 0.1` for realistic soft edges.

```javascript
const spot = new THREE.SpotLight(0xffffff, 1000);
spot.position.set(0, 10, 0);
spot.angle = Math.PI / 6;
spot.penumbra = 0.3;
spot.decay = 2;
scene.add(spot);
scene.add(spot.target); // REQUIRED for target repositioning
```

Properties: `.angle` (max `Math.PI/2`), `.penumbra` (0-1), `.distance`, `.decay`, `.power`, `.map` (cookie texture, REQUIRES `castShadow = true`), `.target`, `.shadow`.

### RectAreaLight

Planar emitter for windows, panels, strip lights. Works ONLY with `MeshStandardMaterial` and `MeshPhysicalMaterial`. CANNOT cast shadows.

```javascript
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';

RectAreaLightUniformsLib.init(); // MUST call before creating any RectAreaLight

const panel = new THREE.RectAreaLight(0xffffff, 5, 4, 10);
panel.position.set(5, 5, 0);
panel.lookAt(0, 0, 0); // Orient using lookAt, NOT rotation
scene.add(panel);
```

Properties: `.width`, `.height`, `.power` (lumens).

### LightProbe

Spherical harmonics-based ambient lighting. Useful for AR and baked environment lighting.

```javascript
import { LightProbeGenerator } from 'three/addons/lights/LightProbeGenerator.js';

const probe = LightProbeGenerator.fromCubeTexture(cubeTexture);
scene.add(probe);
```

---

## Environment Maps (IBL)

Image-Based Lighting (IBL) provides the most realistic ambient illumination for PBR materials. The standard workflow uses `RGBELoader` + `PMREMGenerator`.

### Standard HDR Environment Workflow

```javascript
import * as THREE from 'three';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

const pmremGenerator = new THREE.PMREMGenerator(renderer);
const rgbeLoader = new RGBELoader();

rgbeLoader.load('environment.hdr', (hdrTexture) => {
  const envMap = pmremGenerator.fromEquirectangular(hdrTexture);

  scene.environment = envMap.texture;  // ALL PBR materials auto-use this
  scene.background = envMap.texture;   // Optional: visible HDR background

  hdrTexture.dispose();                // Free source texture
  pmremGenerator.dispose();            // ALWAYS dispose after use
});
```

### scene.environment vs scene.background

| Property | Effect | When to Use |
|----------|--------|-------------|
| `scene.environment` | PBR reflections + ambient lighting on all Standard/Physical materials | ALWAYS for realistic PBR |
| `scene.background` | Visible skybox/backdrop | When you want the HDR visible |
| Both set to same texture | Full IBL with visible environment | Most common for product shots |
| `scene.backgroundBlurriness` | Blur the background (0-1) | Depth-of-field effect on backdrop |
| `scene.environmentIntensity` | Scale IBL contribution | Fine-tune ambient level |
| `scene.environmentRotation` | Rotate the environment map | Adjust light direction without moving lights |

When `scene.environment` is set, ALL `MeshStandardMaterial` and `MeshPhysicalMaterial` instances AUTOMATICALLY use it for reflections and ambient lighting -- no per-material configuration needed.

### PMREMGenerator Methods

| Method | Input | Purpose |
|--------|-------|---------|
| `fromEquirectangular(texture)` | Equirectangular texture | Convert HDR panorama to PMREM |
| `fromScene(scene, sigma?)` | Three.js Scene | Generate PMREM from a 3D scene |
| `fromCubemap(texture)` | CubeTexture | Convert cubemap to PMREM |
| `dispose()` | -- | Free GPU memory (ALWAYS call) |

### EXR Alternative

```javascript
import { EXRLoader } from 'three/addons/loaders/EXRLoader.js';

new EXRLoader().load('environment.exr', (exrTexture) => {
  const envMap = pmremGenerator.fromEquirectangular(exrTexture);
  scene.environment = envMap.texture;
  exrTexture.dispose();
  pmremGenerator.dispose();
});
```

---

## Light Helpers

| Helper | Import | Constructor |
|--------|--------|-------------|
| `DirectionalLightHelper` | `three` | `new DirectionalLightHelper(light, size?, color?)` |
| `SpotLightHelper` | `three` | `new SpotLightHelper(light, color?)` |
| `PointLightHelper` | `three` | `new PointLightHelper(light, sphereSize?, color?)` |
| `HemisphereLightHelper` | `three` | `new HemisphereLightHelper(light, size, color?)` |
| `RectAreaLightHelper` | `three/addons/helpers/RectAreaLightHelper.js` | `new RectAreaLightHelper(light)` |
| `LightProbeHelper` | `three/addons/helpers/LightProbeHelper.js` | `new LightProbeHelper(probe, size)` |

**ALWAYS** call `helper.update()` after changing light properties if the helper does not auto-update.

```javascript
const helper = new THREE.DirectionalLightHelper(dirLight, 5);
scene.add(helper);
// After changing dirLight properties:
helper.update();
```

---

## Performance Budget

| Category | Budget |
|----------|--------|
| Mobile WebGL | Max 4-5 real-time lights total |
| Desktop WebGL | Max 8-16 lights depending on scene |
| Shadow-casting PointLights | Max 1-2 (6 passes each) |
| RectAreaLights | Max 2-3 (expensive LTC evaluation) |

**ALWAYS** prefer baked lighting for static environments over real-time lights.

**ALWAYS** use environment maps (IBL) as the primary ambient source instead of multiple fill lights.

---

## Reference Links

- [references/methods.md](references/methods.md) -- Complete API signatures for all light types and PMREMGenerator
- [references/examples.md](references/examples.md) -- Lighting recipes: outdoor, indoor, studio, product
- [references/anti-patterns.md](references/anti-patterns.md) -- Common lighting mistakes and fixes

### Official Sources

- https://threejs.org/docs/#api/en/lights/AmbientLight
- https://threejs.org/docs/#api/en/lights/DirectionalLight
- https://threejs.org/docs/#api/en/lights/PointLight
- https://threejs.org/docs/#api/en/lights/SpotLight
- https://threejs.org/docs/#api/en/lights/RectAreaLight
- https://threejs.org/docs/#api/en/lights/HemisphereLight
- https://threejs.org/docs/#api/en/lights/LightProbe
- https://threejs.org/docs/#api/en/extras/PMREMGenerator
````

### `atelier/.claude/skills/threejs-impl-lighting/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-impl-physics/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-impl-physics
description: >
  Use when adding physics simulation to a Three.js scene: rigid bodies,
  collisions, constraints, or raycasting. Prevents the common mistake
  of wrong Vec3/Vector3 conversion, missing world.step(), or choosing
  the wrong engine. Covers cannon-es and Rapier with Three.js sync
  patterns, performance comparison.
  Keywords: physics, cannon-es, Rapier, rigid body, collider, collision, gravity, simulation, WASM, constraint, joint, objects fall, collision detection, bouncing, realistic movement.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-impl-physics

## Quick Reference

### Engine Selection Decision Tree

| Criterion | cannon-es | Rapier |
|-----------|-----------|--------|
| Scene size | < 100 bodies | 100–10,000+ bodies |
| Determinism needed | No | Yes (cross-platform) |
| CCD (fast objects) | Limited | Full support |
| Bundle size budget | ~100 KB | ~300–600 KB (WASM) |
| Initialization | Synchronous | Async (MUST `await init()`) |
| Prototyping speed | Faster (simpler API) | Slower (builder pattern) |
| R3F integration | `@react-three/cannon` | `@react-three/rapier` |

**Rule:** ALWAYS use Rapier for production applications requiring determinism, CCD, or > 100 bodies. Use cannon-es for prototyping and simple scenes.

### Critical Warnings

**NEVER** forget to call `world.step()` in the animation loop — physics bodies will NOT move without it.

**NEVER** use `mesh.position.copy(body.position)` with Rapier — Rapier returns plain `{x, y, z}` objects, NOT `CANNON.Vec3`. ALWAYS use `mesh.position.set(pos.x, pos.y, pos.z)`.

**NEVER** use Rapier APIs before `await RAPIER.init()` completes — ALL Rapier classes are undefined until WASM loads.

**NEVER** use `Trimesh` / `trimesh` colliders on dynamic bodies — triangle meshes are STATIC only in both engines. Use `ConvexPolyhedron` / `convexHull` for dynamic concave geometry.

**NEVER** create physics bodies without corresponding Three.js meshes unless intentionally creating invisible colliders — orphaned bodies waste simulation budget.

---

## cannon-es

### World Setup

```js
import * as CANNON from 'cannon-es';

const world = new CANNON.World();
world.gravity.set(0, -9.82, 0);
world.broadphase = new CANNON.SAPBroadphase(world);
world.solver.iterations = 10;
world.allowSleep = true;
```

ALWAYS set `world.allowSleep = true` — sleeping bodies skip simulation and dramatically improve performance.

ALWAYS use `SAPBroadphase` for scenes with > 20 bodies. `NaiveBroadphase` is O(n^2).

### Body Types

| Type | Mass | Behavior |
|------|------|----------|
| `CANNON.Body.DYNAMIC` | > 0 | Affected by forces and collisions |
| `CANNON.Body.STATIC` | 0 | Immovable, infinite mass |
| `CANNON.Body.KINEMATIC` | 0 | Moved programmatically, pushes dynamic bodies |

```js
const body = new CANNON.Body({
  mass: 5,
  position: new CANNON.Vec3(0, 10, 0),
  shape: new CANNON.Box(new CANNON.Vec3(1, 1, 1)), // half-extents
  linearDamping: 0.01,
  angularDamping: 0.01,
});
world.addBody(body);
```

### Shape Types

| Shape | Constructor | Notes |
|-------|------------|-------|
| `Box` | `new CANNON.Box(halfExtents: Vec3)` | Axis-aligned box |
| `Sphere` | `new CANNON.Sphere(radius)` | Cheapest collision shape |
| `Cylinder` | `new CANNON.Cylinder(rTop, rBottom, height, segments)` | Cylinder |
| `Plane` | `new CANNON.Plane()` | Infinite ground plane |
| `ConvexPolyhedron` | `new CANNON.ConvexPolyhedron({vertices, faces})` | Custom convex hull |
| `Trimesh` | `new CANNON.Trimesh(vertices, indices)` | STATIC only |
| `Heightfield` | `new CANNON.Heightfield(data, {elementSize})` | Terrain |
| `Particle` | `new CANNON.Particle()` | Point particle |

### Materials and Contacts

```js
const groundMat = new CANNON.Material('ground');
const ballMat = new CANNON.Material('ball');
const contact = new CANNON.ContactMaterial(groundMat, ballMat, {
  friction: 0.4,
  restitution: 0.6,
});
world.addContactMaterial(contact);

// Assign materials to bodies
groundBody.material = groundMat;
ballBody.material = ballMat;
```

ALWAYS assign materials to bodies after creating ContactMaterial — without assignment, the ContactMaterial has NO effect.

### Constraints

| Constraint | Constructor | Use Case |
|-----------|------------|----------|
| `PointToPointConstraint` | `(bodyA, pivotA, bodyB, pivotB)` | Ball joint |
| `DistanceConstraint` | `(bodyA, bodyB, distance)` | Fixed distance rod |
| `HingeConstraint` | `(bodyA, bodyB, {pivotA, axisA, pivotB, axisB})` | Door hinge |
| `LockConstraint` | `(bodyA, bodyB)` | Rigid lock |
| `ConeTwistConstraint` | `(bodyA, bodyB, options)` | Ragdoll joints |
| `Spring` | `(bodyA, bodyB, options)` | Damped spring |

```js
const hinge = new CANNON.HingeConstraint(bodyA, bodyB, {
  pivotA: new CANNON.Vec3(0, 0, 0),
  axisA: new CANNON.Vec3(0, 1, 0),
  pivotB: new CANNON.Vec3(-2, 0, 0),
  axisB: new CANNON.Vec3(0, 1, 0),
});
world.addConstraint(hinge);
```

### Events

```js
body.addEventListener('collide', (event) => {
  const { contact } = event;
  // contact.ni = contact normal
  // contact.ri = contact point relative to bodyA
  // contact.rj = contact point relative to bodyB
});
body.addEventListener('sleep', () => { /* body went to sleep */ });
body.addEventListener('wakeup', () => { /* body woke up */ });
```

### Stepping

```js
// ALWAYS use three-argument step for deterministic simulation
const fixedTimeStep = 1 / 60;
const maxSubSteps = 3;

function animate() {
  const delta = clock.getDelta();
  world.step(fixedTimeStep, delta, maxSubSteps);
}
```

---

## Rapier

### WASM Initialization

```js
import RAPIER from '@dimforge/rapier3d-compat';

await RAPIER.init(); // MUST await — ALL APIs undefined before this resolves

const gravity = { x: 0.0, y: -9.81, z: 0.0 };
const world = new RAPIER.World(gravity);
```

ALWAYS wrap Rapier usage in an async function or top-level await. Calling ANY Rapier constructor before `init()` resolves throws a runtime error.

### RigidBody Creation (Builder Pattern)

```js
// Dynamic body
const bodyDesc = RAPIER.RigidBodyDesc.dynamic()
  .setTranslation(0, 10, 0)
  .setLinvel(0, 0, 0)
  .setAngvel({ x: 0, y: 0, z: 0 })
  .setLinearDamping(0.01)
  .setAngularDamping(0.01)
  .setCcdEnabled(true);
const rigidBody = world.createRigidBody(bodyDesc);

// Static body
const staticDesc = RAPIER.RigidBodyDesc.fixed().setTranslation(0, 0, 0);
const staticBody = world.createRigidBody(staticDesc);

// Kinematic (position-based)
const kinDesc = RAPIER.RigidBodyDesc.kinematicPositionBased();
const kinBody = world.createRigidBody(kinDesc);

// Kinematic (velocity-based)
const kinVelDesc = RAPIER.RigidBodyDesc.kinematicVelocityBased();
```

### Collider Shapes

```js
const colliderDesc = RAPIER.ColliderDesc.cuboid(1, 1, 1)
  .setRestitution(0.5)
  .setFriction(0.7);
world.createCollider(colliderDesc, rigidBody);
```

| Shape | Constructor | Notes |
|-------|------------|-------|
| `ColliderDesc.cuboid(hx, hy, hz)` | Box half-extents | Most common |
| `ColliderDesc.ball(radius)` | Sphere | Cheapest shape |
| `ColliderDesc.capsule(halfHeight, radius)` | Capsule | Good for characters |
| `ColliderDesc.cylinder(halfHeight, radius)` | Cylinder | |
| `ColliderDesc.cone(halfHeight, radius)` | Cone | |
| `ColliderDesc.convexHull(vertices)` | Convex hull | From Float32Array |
| `ColliderDesc.trimesh(vertices, indices)` | Triangle mesh | STATIC only |
| `ColliderDesc.heightfield(nrows, ncols, heights, scale)` | Terrain | |
| `ColliderDesc.roundCuboid(hx, hy, hz, borderRadius)` | Rounded box | |

### Ray Casting

```js
const ray = new RAPIER.Ray({ x: 0, y: 10, z: 0 }, { x: 0, y: -1, z: 0 });
const hit = world.castRay(ray, 100, true);
if (hit) {
  const hitPoint = ray.pointAt(hit.timeOfImpact);
  const hitCollider = world.getCollider(hit.colliderHandle);
}
```

### CCD (Continuous Collision Detection)

ALWAYS enable CCD on fast-moving bodies to prevent tunneling through thin geometry:

```js
const desc = RAPIER.RigidBodyDesc.dynamic().setCcdEnabled(true);
```

### Collision Events

```js
const eventQueue = new RAPIER.EventQueue(true);
world.step(eventQueue);

eventQueue.drainCollisionEvents((handle1, handle2, started) => {
  // started === true: collision began
  // started === false: collision ended
});

eventQueue.drainContactForceEvents((event) => {
  const force = event.totalForceMagnitude();
});
```

### Debug Rendering

```js
const { vertices, colors } = world.debugRender();
const geometry = new THREE.BufferGeometry();
geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 4));
const material = new THREE.LineBasicMaterial({ vertexColors: true });
const lines = new THREE.LineSegments(geometry, material);
scene.add(lines);
```

---

## Three.js Sync Pattern

### cannon-es Sync

```js
// Store body-mesh pairs
const pairs = [];

function addPhysicsObject(mesh, body) {
  scene.add(mesh);
  world.addBody(body);
  pairs.push({ mesh, body });
}

function updatePhysics(delta) {
  world.step(1 / 60, delta, 3);
  for (const { mesh, body } of pairs) {
    mesh.position.copy(body.position);       // Vec3 → Vector3 (compatible)
    mesh.quaternion.copy(body.quaternion);    // Quaternion → Quaternion (compatible)
  }
}
```

cannon-es `Vec3` and `Quaternion` are directly compatible with Three.js `.copy()`.

### Rapier Sync

```js
const pairs = [];

function addPhysicsObject(mesh, rigidBody) {
  scene.add(mesh);
  pairs.push({ mesh, rigidBody });
}

function updatePhysics() {
  world.step();
  for (const { mesh, rigidBody } of pairs) {
    const pos = rigidBody.translation();   // returns {x, y, z}
    const rot = rigidBody.rotation();      // returns {x, y, z, w}
    mesh.position.set(pos.x, pos.y, pos.z);
    mesh.quaternion.set(rot.x, rot.y, rot.z, rot.w);
  }
}
```

NEVER use `.copy()` with Rapier return values — they are plain objects, NOT Three.js types.

---

## React Three Fiber Integration

### @react-three/rapier

```jsx
import { Physics, RigidBody } from '@react-three/rapier';

function Scene() {
  return (
    <Physics gravity={[0, -9.81, 0]}>
      <RigidBody type="fixed">
        <mesh position={[0, -1, 0]}>
          <boxGeometry args={[20, 1, 20]} />
          <meshStandardMaterial />
        </mesh>
      </RigidBody>
      <RigidBody>
        <mesh position={[0, 5, 0]}>
          <sphereGeometry args={[1]} />
          <meshStandardMaterial />
        </mesh>
      </RigidBody>
    </Physics>
  );
}
```

### @react-three/cannon

```jsx
import { Physics, useBox, useSphere } from '@react-three/cannon';

function Floor() {
  const [ref] = useBox(() => ({ mass: 0, args: [20, 1, 20], position: [0, -1, 0] }));
  return (
    <mesh ref={ref}>
      <boxGeometry args={[20, 1, 20]} />
      <meshStandardMaterial />
    </mesh>
  );
}
```

---

## Performance Comparison

| Feature | cannon-es | Rapier |
|---------|-----------|--------|
| Language | JavaScript | Rust compiled to WASM |
| Real-time bodies | ~1,000 | ~10,000+ |
| Bundle size | ~100 KB | ~300–600 KB |
| CCD | Limited | Full support |
| Deterministic | No | Yes (cross-platform) |
| Debug rendering | Manual | Built-in `world.debugRender()` |
| API style | Constructor-based | Builder pattern |

---

## Reference Links

- [references/methods.md](references/methods.md) — API signatures for cannon-es and Rapier
- [references/examples.md](references/examples.md) — Working integration examples
- [references/anti-patterns.md](references/anti-patterns.md) — Common physics mistakes and fixes

### Official Sources

- https://pmndrs.github.io/cannon-es/docs/
- https://rapier.rs/docs/user_guides/javascript/getting_started
- https://github.com/pmndrs/react-three-rapier
- https://github.com/pmndrs/use-cannon
````

### `atelier/.claude/skills/threejs-impl-physics/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-impl-post-processing/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-impl-post-processing
description: >
  Use when adding post-processing effects like bloom, SSAO, depth of
  field, or anti-aliasing to a Three.js scene. Prevents the common
  mistake of mixing Three.js EffectComposer with pmndrs/postprocessing,
  wrong pass order, or missing RenderPass. Covers EffectComposer,
  27+ passes, pmndrs/postprocessing, custom ShaderPass.
  Keywords: post-processing, EffectComposer, bloom, UnrealBloomPass, SSAO, outline, SMAA, FXAA, postprocessing, effects, render pass, glow effect, blur, cinematic, visual effects.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-impl-post-processing

## Quick Reference

### Architecture Overview

Three.js offers TWO incompatible post-processing systems. NEVER mix them.

| System | Package | Approach | Best For |
|--------|---------|----------|----------|
| Built-in EffectComposer | `three/addons/postprocessing/` | One shader pass per effect | Simple setups, custom ShaderPass |
| pmndrs/postprocessing | `postprocessing` (npm) | Merges effects into single pass | Performance-critical, R3F apps |
| WebGPU PostProcessing | `three/addons/tsl/display/` | Node-based TSL graphs | WebGPU renderer only |

### Standard Pipeline (Built-in EffectComposer)

```js
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const composer = new EffectComposer( renderer );
composer.addPass( new RenderPass( scene, camera ) ); // ALWAYS first
// ... effect passes here ...
composer.addPass( new OutputPass() );                 // ALWAYS last

function animate() {
  composer.render(); // replaces renderer.render( scene, camera )
}
```

### Pass Ordering Rules

1. `RenderPass` MUST be the FIRST pass -- it renders the scene to the internal buffer
2. Effect passes go in the MIDDLE in any order (bloom, SSAO, outline, etc.)
3. Anti-aliasing passes (SMAA, FXAA) go AFTER effect passes
4. `OutputPass` MUST be the LAST pass -- it applies tone mapping and color space conversion
5. NEVER omit `OutputPass` -- without it, colors appear washed out or incorrect

### Critical Warnings

**NEVER** mix `three/addons/postprocessing/EffectComposer` with `pmndrs/postprocessing` `EffectComposer`. They use incompatible buffer formats and will produce rendering artifacts or crashes.

**NEVER** forget to call `composer.setSize()` on window resize. Failing to resize the composer causes blurry or misaligned effects.

**NEVER** call `renderer.render( scene, camera )` when using EffectComposer. ALWAYS call `composer.render()` instead -- calling both renders the scene twice.

**NEVER** use WebGL post-processing passes with the WebGPU renderer. WebGPU uses an entirely separate node-based `PostProcessing` class.

**ALWAYS** include `RenderPass` as the first pass. Without it, subsequent passes receive an empty buffer.

---

## EffectComposer API

### Constructor

```js
new EffectComposer( renderer: WebGLRenderer, renderTarget?: WebGLRenderTarget )
```

- `renderer` -- the WebGLRenderer instance
- `renderTarget` -- optional custom render target; auto-created if omitted

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `.passes` | `Pass[]` | Ordered array of post-processing passes |
| `.readBuffer` | `WebGLRenderTarget` | Internal read buffer |
| `.writeBuffer` | `WebGLRenderTarget` | Internal write buffer |
| `.renderToScreen` | `boolean` | Whether the final pass renders to screen (default `true`) |
| `.renderer` | `WebGLRenderer` | The renderer instance |

### Methods

| Method | Description |
|--------|-------------|
| `.addPass( pass )` | Appends a pass to the end of the chain |
| `.insertPass( pass, index )` | Inserts a pass at a specific position |
| `.removePass( pass )` | Removes a pass from the chain |
| `.render( deltaTime? )` | Executes all enabled passes in order |
| `.setSize( width, height )` | Resizes all internal buffers and passes |
| `.setPixelRatio( ratio )` | Configures device pixel ratio |
| `.swapBuffers()` | Exchanges read/write buffers |
| `.reset( renderTarget? )` | Restores internal state |
| `.dispose()` | Frees all GPU resources |

---

## Available Pass Types

### Core Passes (ALWAYS needed)

| Pass | Import | Purpose |
|------|--------|---------|
| `RenderPass` | `postprocessing/RenderPass.js` | Renders scene to buffer; ALWAYS first |
| `OutputPass` | `postprocessing/OutputPass.js` | Tone mapping + color space; ALWAYS last |

### Effect Passes

| Pass | Constructor | Purpose |
|------|-------------|---------|
| `UnrealBloomPass` | `( resolution, strength?, radius?, threshold? )` | HDR bloom glow |
| `SSAOPass` | `( scene, camera, width?, height? )` | Screen-space ambient occlusion |
| `GTAOPass` | `( scene, camera, width?, height? )` | Ground truth AO (higher quality) |
| `SAOPass` | `( scene, camera )` | Scalable ambient obscurance |
| `OutlinePass` | `( resolution, scene, camera, selectedObjects? )` | Object selection outlines |
| `BokehPass` | `( scene, camera, params )` | Depth of field |
| `SSRPass` | `( params )` | Screen-space reflections |
| `FilmPass` | `( intensity?, grayscale? )` | Film grain / scanlines |
| `GlitchPass` | `( dtSize? )` | Digital glitch effect |
| `HalftonePass` | `( width, height, params )` | Halftone dot pattern |
| `DotScreenPass` | `( center?, angle?, scale? )` | Dot screen overlay |
| `AfterimagePass` | `( damp? )` | Motion trails / ghosting |
| `LUTPass` | `( params )` | Color LUT grading |
| `RenderPixelatedPass` | `( pixelSize, scene, camera )` | Pixelation effect |

### Anti-Aliasing Passes

| Pass | Constructor | Quality | Cost |
|------|-------------|---------|------|
| `FXAAPass` | `()` | Low -- fast approximation | Cheapest |
| `SMAAPass` | `( width, height )` | Medium -- subpixel morphological | Moderate |
| `SSAARenderPass` | `( scene, camera )` | High -- super-sampling | Expensive |
| `TAARenderPass` | `( scene, camera )` | High -- temporal accumulation | Expensive |

### Utility Passes

| Pass | Purpose |
|------|---------|
| `ShaderPass` | Custom GLSL shader effect |
| `MaskPass` | Stencil masking |
| `ClearMaskPass` | Clears stencil mask |
| `ClearPass` | Clears buffer |
| `TexturePass` | Renders a texture |
| `CubeTexturePass` | Renders cubemap background |
| `SavePass` | Saves current buffer to render target |
| `RenderTransitionPass` | Animated transition between two scenes |

ALL passes import from `three/addons/postprocessing/{PassName}.js`.

---

## Key Effect Configuration

### UnrealBloomPass

```js
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

const bloom = new UnrealBloomPass(
  new THREE.Vector2( window.innerWidth, window.innerHeight ),
  1.5,  // strength -- bloom intensity [0, 3+]
  0.4,  // radius -- bloom spread [0, 1]
  0.85  // threshold -- luminance cutoff [0, 1]
);
```

Tone mapping MUST be enabled on the renderer for bloom to work correctly. Selective bloom (per-object) is NOT natively supported -- use the `layers` system with multiple render passes as a workaround.

### SSAOPass / GTAOPass

ALWAYS prefer `GTAOPass` over `SSAOPass` for production quality. Use `SSAOPass` only for prototyping.

```js
// SSAOPass (faster, lower quality)
const ssao = new SSAOPass( scene, camera, width, height );
ssao.kernelRadius = 8;
ssao.minDistance = 0.005;
ssao.maxDistance = 0.1;

// GTAOPass (slower, production quality)
const gtao = new GTAOPass( scene, camera, width, height );
```

### OutlinePass

```js
const outline = new OutlinePass(
  new THREE.Vector2( window.innerWidth, window.innerHeight ),
  scene, camera
);
outline.selectedObjects = [ mesh1, mesh2 ];
outline.edgeStrength = 3;
outline.edgeGlow = 0;
outline.edgeThickness = 1;
outline.visibleEdgeColor.set( 0xffffff );
outline.hiddenEdgeColor.set( 0x190a05 );
```

---

## Custom ShaderPass

```js
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

const myShader = {
  uniforms: {
    tDiffuse: { value: null }, // ALWAYS include -- receives read buffer
    amount: { value: 0.5 }
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform float amount;
    varying vec2 vUv;
    void main() {
      vec4 color = texture2D( tDiffuse, vUv );
      gl_FragColor = mix( color, vec4( 1.0 - color.rgb, color.a ), amount );
    }
  `
};

const customPass = new ShaderPass( myShader );
composer.insertPass( customPass, 1 ); // after RenderPass
```

The `textureID` parameter defaults to `'tDiffuse'`. If your shader uses a different uniform name for the input texture, pass it as the second argument: `new ShaderPass( myShader, 'myInputTexture' )`.

---

## pmndrs/postprocessing

### Architecture

The `pmndrs/postprocessing` library merges multiple effects into a SINGLE shader pass, reducing draw calls significantly compared to the built-in system.

```js
import { EffectComposer, EffectPass, RenderPass, BloomEffect,
         SMAAEffect } from 'postprocessing';

const composer = new EffectComposer( renderer );
composer.addPass( new RenderPass( scene, camera ) );
composer.addPass( new EffectPass( camera, new BloomEffect(), new SMAAEffect() ) );

function animate() {
  composer.render();
}
```

### Key Effects

| Effect | Purpose |
|--------|---------|
| `BloomEffect` | Configurable bloom with mipmaps |
| `SMAAEffect` | Subpixel morphological AA |
| `SSAOEffect` | Screen-space ambient occlusion |
| `DepthOfFieldEffect` | Bokeh depth-of-field |
| `ToneMappingEffect` | Tone mapping operators |
| `VignetteEffect` | Screen edge darkening |
| `ChromaticAberrationEffect` | Color fringing |
| `NoiseEffect` | Film grain |
| `GodRaysEffect` | Volumetric light scattering |

For React Three Fiber, use `@react-three/postprocessing` which wraps these effects as JSX components.

---

## Resize Handling

ALWAYS resize both the renderer AND the composer on window resize:

```js
window.addEventListener( 'resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize( window.innerWidth, window.innerHeight );
  composer.setSize( window.innerWidth, window.innerHeight ); // MUST resize
});
```

---

## WebGPU PostProcessing

The WebGPU renderer uses a SEPARATE node-based system:

```js
import { PostProcessing } from 'three/addons/tsl/display/PostProcessing.js';

const postProcessing = new PostProcessing( renderer );
// Uses TSL (Three Shading Language) node graphs for effects
```

This is entirely incompatible with both the built-in WebGL `EffectComposer` and `pmndrs/postprocessing`.

---

## Reference Links

- [references/methods.md](references/methods.md) -- Complete API signatures for EffectComposer, all passes, and pmndrs effects
- [references/examples.md](references/examples.md) -- Working code examples for common post-processing setups
- [references/anti-patterns.md](references/anti-patterns.md) -- What NOT to do with post-processing

### Official Sources

- https://threejs.org/docs/#examples/en/postprocessing/EffectComposer
- https://threejs.org/examples/?q=postprocessing
- https://github.com/pmndrs/postprocessing
- https://docs.pmnd.rs/react-three-fiber/tutorials/post-processing
````

### `atelier/.claude/skills/threejs-impl-post-processing/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-impl-react-three-fiber/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-impl-react-three-fiber
description: >
  Use when building 3D scenes with React using React Three Fiber (R3F).
  Prevents the common mistake of mixing imperative Three.js code with
  R3F's declarative model, creating objects inside useFrame, or
  forgetting Suspense for loaders. Covers Canvas, useFrame, useThree,
  useLoader, JSX mapping, event system, performance patterns.
  Keywords: React Three Fiber, R3F, Canvas, useFrame, useThree, useLoader, @react-three/fiber, 3D React, declarative Three.js, use Three.js with React, JSX 3D components.
license: MIT
compatibility: "Designed for Claude Code. Requires @react-three/fiber 8.x+, React 18+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-impl-react-three-fiber

## Quick Reference

### Canvas Component Props

| Prop | Type | Default | Purpose |
|------|------|---------|---------|
| `gl` | `Renderer props \| (canvas) => Renderer` | `{}` | WebGL renderer config or factory |
| `camera` | `Camera props \| THREE.Camera` | `{ fov: 75, near: 0.1, far: 1000, position: [0,0,5] }` | Default camera |
| `scene` | `Scene props \| THREE.Scene` | `{}` | Scene configuration |
| `shadows` | `boolean \| ShadowMapType` | `false` | Enable shadow maps |
| `raycaster` | `Raycaster props` | `{}` | Raycaster configuration |
| `frameloop` | `"always" \| "demand" \| "never"` | `"always"` | Render loop strategy |
| `resize` | `ResizeOptions` | `{ scroll: true, debounce: { scroll: 50, resize: 0 } }` | Resize behavior |
| `orthographic` | `boolean` | `false` | Use OrthographicCamera |
| `dpr` | `number \| [min, max]` | `[1, 2]` | Device pixel ratio |
| `linear` | `boolean` | `false` | Linear color space |
| `flat` | `boolean` | `false` | Disable tone mapping |
| `legacy` | `boolean` | `false` | Disable color management |
| `events` | `EventManager` | R3F default | Custom event manager |
| `eventSource` | `HTMLElement \| React.RefObject` | Parent node | Event capture element |
| `eventPrefix` | `string` | `"offset"` | Coordinate prefix |
| `onCreated` | `(state: RootState) => void` | -- | Post-init callback |
| `onPointerMissed` | `(event: PointerEvent) => void` | -- | Click misses all meshes |
| `fallback` | `React.ReactNode` | -- | DOM fallback during init |

### Frameloop Modes

| Mode | Behavior |
|------|----------|
| `"always"` | ALWAYS renders every frame via requestAnimationFrame |
| `"demand"` | ONLY renders when `invalidate()` is called -- use for static scenes |
| `"never"` | NEVER renders automatically -- caller MUST invoke `advance(timestamp)` |

### Critical Warnings

**NEVER** create Three.js objects inside `useFrame` -- this allocates memory every frame and causes GC pressure. ALWAYS create objects outside the callback or use `useMemo`.

**NEVER** forget `<Suspense>` when using `useLoader` -- the component WILL suspend and crash without a Suspense boundary.

**NEVER** add the same Three.js object instance to the scene tree multiple times via `<primitive>` -- Three.js objects can only have one parent.

**NEVER** use `useThree()` without a selector when you only need one property -- the full state object triggers re-renders on every frame. ALWAYS use `useThree((s) => s.camera)`.

**NEVER** mix imperative `scene.add()` calls with R3F's declarative JSX tree -- R3F manages the scene graph and imperative mutations cause desync.

**ALWAYS** use `delta` from `useFrame` for animations -- hardcoded time steps cause speed variations across different frame rates.

**ALWAYS** use `useMemo` for imperatively created geometries and materials -- without it, new objects are allocated on every render.

---

## JSX-to-Three.js Mapping Rules

R3F uses deterministic conventions to translate JSX into Three.js scene graph operations:

1. **Lowercase JSX = Three.js class.** `<mesh />` creates `new THREE.Mesh()`. `<meshStandardMaterial />` creates `new THREE.MeshStandardMaterial()`.

2. **`args` = constructor arguments (array).** `<sphereGeometry args={[1, 32, 32]} />` becomes `new THREE.SphereGeometry(1, 32, 32)`. When `args` changes, the object is destroyed and recreated.

3. **`attach` = parent property binding.** `<meshStandardMaterial attach="material" />` sets `parent.material = this`. Geometries auto-attach to `"geometry"`, materials to `"material"`.

4. **Dash-notation attach for nested paths.** `attach="shadow-camera"` sets `parent.shadow.camera = this`. Array indexing: `attach="material-0"`.

5. **Functional attach.** `attach={(parent, self) => { parent.add(self); return () => parent.remove(self); }}` for custom bind/unbind.

6. **Properties with `.set()` accept shorthand.** `position={[1, 2, 3]}` calls `object.position.set(1, 2, 3)`. `color="hotpink"` calls `object.color.set("hotpink")`.

7. **Scalar shorthand.** `scale={2}` calls `object.scale.setScalar(2)`.

8. **Dash-case pierces nested properties.** `rotation-x={Math.PI}` sets `object.rotation.x = Math.PI`.

---

## Hooks

### useFrame

```typescript
useFrame((state: RootState, delta: number, xrFrame?: XRFrame) => void, priority?: number)
```

Subscribes a callback to the render loop. Executes every frame.

**State object key properties:**

| Property | Type | Description |
|----------|------|-------------|
| `gl` | `THREE.WebGLRenderer` | The renderer |
| `scene` | `THREE.Scene` | The scene |
| `camera` | `THREE.Camera` | Active camera |
| `clock` | `THREE.Clock` | System clock |
| `pointer` | `THREE.Vector2` | Normalized pointer (-1 to +1) |
| `size` | `{ width, height, top, left }` | Canvas dimensions (px) |
| `viewport` | `{ width, height, factor, distance, aspect }` | Camera-relative metrics |
| `invalidate` | `() => void` | Request render in demand mode |
| `advance` | `(timestamp: number) => void` | Advance one tick in never mode |
| `performance` | `{ current, min, max, regress() }` | Adaptive performance |
| `set` | `(state) => void` | Mutate state directly |
| `get` | `() => RootState` | Read state non-reactively |

**Priority system:** Callbacks execute in ascending priority order. When ANY callback has priority > 0, R3F disables automatic `renderer.render()`. The highest-priority subscriber MUST call `state.gl.render(state.scene, state.camera)` manually. Negative priorities do NOT disable auto-rendering.

### useThree

```typescript
const state = useThree()                              // full state (re-renders often)
const camera = useThree((state) => state.camera)      // selector (re-renders only on change)
```

Returns the RootState (same object as useFrame's state). ALWAYS use a selector when only one property is needed.

### useLoader

```typescript
const result = useLoader(LoaderClass, url, extensions?, onProgress?)
const results = useLoader(LoaderClass, [url1, url2], extensions?)
```

Suspense-based asset loading. ALWAYS wrap in `<Suspense fallback={...}>`.

- Assets are cached by URL -- loading the same URL twice returns the cached result.
- `useLoader.preload(LoaderClass, url)` preloads before component mount.
- GLTF results include `{ nodes, materials, scene, animations }`.

### useGraph

```typescript
const { nodes, materials } = useGraph(object3D)
```

Traverses an Object3D hierarchy and returns memoized `{ nodes, materials }` collections keyed by name.

---

## Primitives and extend()

### Primitives

Insert pre-existing Three.js objects into the declarative tree:

```jsx
<primitive object={existingMesh} position={[10, 0, 0]} />
```

- NEVER add the same object instance multiple times -- Three.js objects can have only one parent.
- Primitives do NOT auto-dispose; the caller MUST manage lifecycle.

### extend()

Register custom Three.js classes as JSX elements:

```jsx
import { extend } from '@react-three/fiber'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

extend({ OrbitControls })
// Now usable as <orbitControls args={[camera, domElement]} />
```

The JSX element name is the camelCase version of the registered key.

---

## Event System

R3F implements pointer events via raycasting. Events bubble through the scene graph.

### Supported Events

| Event | Trigger |
|-------|---------|
| `onClick` | Pointer click on mesh |
| `onContextMenu` | Right-click / context menu |
| `onDoubleClick` | Double click |
| `onPointerUp` | Pointer released |
| `onPointerDown` | Pointer pressed |
| `onPointerOver` | Pointer enters mesh (fires continuously) |
| `onPointerOut` | Pointer leaves mesh |
| `onPointerEnter` | Pointer enters mesh (fires once) |
| `onPointerLeave` | Pointer leaves mesh (fires once) |
| `onPointerMove` | Pointer moves over mesh |
| `onPointerMissed` | Click hits no mesh (Canvas-level) |
| `onWheel` | Scroll wheel |
| `onUpdate` | Object receives new props |

### Event Object Properties

| Property | Type | Description |
|----------|------|-------------|
| `object` | `THREE.Object3D` | The mesh actually hit |
| `eventObject` | `THREE.Object3D` | Object with the event handler |
| `point` | `THREE.Vector3` | Intersection in world space |
| `distance` | `number` | Camera-to-intersection distance |
| `uv` | `THREE.Vector2` | UV coordinates at intersection |
| `face` | `THREE.Face` | Intersected face |
| `ray` | `THREE.Ray` | Ray used for intersection |
| `camera` | `THREE.Camera` | Active camera |
| `intersections` | `Intersection[]` | All intersected objects |
| `delta` | `number` | Pixel distance down-to-up |
| `sourceEvent` | `Event` | Original DOM event |
| `stopPropagation()` | `function` | Prevent bubbling to occluded objects |

---

## Performance Patterns

### Disposal

- R3F ALWAYS calls `dispose()` on Three.js objects when components unmount, freeing GPU resources.
- Set `dispose={null}` on an element to PREVENT auto-disposal -- use when objects are shared across components.

### Static Scenes

Use `frameloop="demand"` with `invalidate()` for scenes that do not animate continuously (dashboards, configurators). This saves GPU cycles.

### Portals

```jsx
import { createPortal } from '@react-three/fiber'

createPortal(children, targetScene)
```

Renders children into a different scene/layer without affecting the main scene graph.

### useMemo for Imperative Objects

ALWAYS wrap imperatively created geometries and materials in `useMemo`:

```jsx
const geometry = useMemo(() => new THREE.TorusKnotGeometry(1, 0.3, 128, 32), [])
```

Without `useMemo`, a new object is created on every render.

---

## Reference Links

- [references/methods.md](references/methods.md) -- Hook signatures and Canvas API
- [references/examples.md](references/examples.md) -- Working R3F code examples
- [references/anti-patterns.md](references/anti-patterns.md) -- What NOT to do with R3F

### Official Sources

- https://r3f.docs.pmnd.rs/
- https://r3f.docs.pmnd.rs/api/canvas
- https://r3f.docs.pmnd.rs/api/hooks
- https://r3f.docs.pmnd.rs/api/events
````

### `atelier/.claude/skills/threejs-impl-react-three-fiber/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-impl-shadows/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-impl-shadows
description: >
  Use when enabling shadows in a Three.js scene or debugging shadow
  artifacts like acne, peter panning, or low resolution. Prevents the
  common mistake of wrong shadow camera frustum, too many PointLight
  shadows, or missing castShadow/receiveShadow flags. Covers shadow map
  types, per-light config, bias tuning, CameraHelper debugging.
  Keywords: shadows, shadowMap, shadow acne, peter panning, bias, normalBias, castShadow, receiveShadow, PCFSoftShadowMap, shadow camera, shadows not showing, shadow artifacts, enable shadows.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-impl-shadows

## Quick Reference

### Three-Step Shadow Opt-In

Shadows in Three.js require THREE explicit opt-in steps. Missing ANY step results in no shadows.

```js
import * as THREE from 'three';

// Step 1: Enable shadow maps on the renderer
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// Step 2: Enable shadow casting on the light
light.castShadow = true;

// Step 3: Enable per-mesh shadow behavior
mesh.castShadow = true;       // this mesh casts shadows
ground.receiveShadow = true;  // this mesh receives shadows
```

### Shadow Map Types

| Type | Constant | Quality | Cost | Supports `.radius` |
|------|----------|---------|------|---------------------|
| Basic | `THREE.BasicShadowMap` | Hard edges, aliased | Lowest | No |
| PCF | `THREE.PCFShadowMap` | Slightly softened | Moderate | No |
| PCF Soft | `THREE.PCFSoftShadowMap` | Soft penumbra | Higher | No (ignores it) |
| VSM | `THREE.VSMShadowMap` | Gaussian blur | Moderate | Yes |

- **Default** in r160+: `THREE.PCFShadowMap`
- **PCFSoftShadowMap**: best general-purpose choice; IGNORES the `shadow.radius` property
- **VSMShadowMap**: supports `shadow.radius` and `shadow.blurSamples` but can exhibit light bleeding on thin geometry

### Critical Warnings

**NEVER** forget any of the three opt-in steps -- missing even one produces zero shadows with no error message.

**NEVER** leave the DirectionalLight shadow camera frustum at default size -- it is almost ALWAYS wrong for your scene. ALWAYS configure it manually.

**NEVER** use more than 1-2 shadow-casting PointLights -- each PointLight shadow renders 6 cubemap faces per frame.

**ALWAYS** set `shadow.mapSize` to power-of-two values (512, 1024, 2048, 4096).

**ALWAYS** add `light.target` to the scene when repositioning a DirectionalLight or SpotLight target.

---

## Shadow Map Types -- Detailed Comparison

### BasicShadowMap

No filtering applied. Produces hard, aliased shadow edges. Use ONLY for debugging or stylized rendering where hard shadows are intentional.

### PCFShadowMap (Default)

Percentage-Closer Filtering with a fixed-size kernel. Produces slightly softened edges. Good balance of quality and performance. The `shadow.radius` property has NO effect.

### PCFSoftShadowMap

Uses a variable kernel for softer penumbra simulation. Higher quality than PCF but more expensive. The `shadow.radius` property is IGNORED -- softness is determined automatically by the filter.

### VSMShadowMap

Variance Shadow Maps use a Gaussian blur pass. Supports `shadow.radius` (blur size) and `shadow.blurSamples` (sample count). Produces smooth soft shadows but suffers from **light bleeding** artifacts where thin geometry meets shadow receivers. NEVER use VSM for scenes with many thin overlapping shadow casters.

---

## Per-Light Shadow Configuration

### DirectionalLight Shadows

Uses an **orthographic** shadow camera. The frustum MUST be manually sized to encompass the shadowed area.

```js
const dirLight = new THREE.DirectionalLight(0xffffff, 1);
dirLight.position.set(5, 10, 7.5);
dirLight.castShadow = true;

// Shadow map resolution
dirLight.shadow.mapSize.width = 2048;
dirLight.shadow.mapSize.height = 2048;

// Orthographic frustum -- MUST size manually
dirLight.shadow.camera.near = 0.5;
dirLight.shadow.camera.far = 500;
dirLight.shadow.camera.left = -50;
dirLight.shadow.camera.right = 50;
dirLight.shadow.camera.top = 50;
dirLight.shadow.camera.bottom = -50;

// Anti-acne bias
dirLight.shadow.bias = -0.0001;
dirLight.shadow.normalBias = 0.02;

scene.add(dirLight);
scene.add(dirLight.target); // REQUIRED if repositioning target
```

**Frustum sizing rule**: Make the frustum as TIGHT as possible around the area that needs shadows. A frustum that is too large wastes shadow map resolution; a frustum that is too small clips shadows.

### SpotLight Shadows

Uses a **perspective** shadow camera that auto-configures from the SpotLight `.angle` and `.distance`. Manual frustum configuration is typically unnecessary.

```js
const spotLight = new THREE.SpotLight(0xffffff, 1);
spotLight.position.set(0, 10, 0);
spotLight.angle = Math.PI / 6;
spotLight.penumbra = 0.3;
spotLight.castShadow = true;

spotLight.shadow.mapSize.width = 1024;
spotLight.shadow.mapSize.height = 1024;
spotLight.shadow.bias = -0.0001;

scene.add(spotLight);
scene.add(spotLight.target);
```

SpotLightShadow exposes:
- `.focus` (number, default `1`) -- adjusts shadow camera FOV relative to spotlight FOV, range `[0, 1]`

### PointLight Shadows

Uses a **cubemap** (6 perspective cameras, one per face). This is the MOST expensive shadow type -- rendering the scene 6 times per shadow-casting PointLight per frame.

```js
const pointLight = new THREE.PointLight(0xffffff, 1, 100);
pointLight.position.set(0, 5, 0);
pointLight.castShadow = true;

// Lower resolution to offset the 6x render cost
pointLight.shadow.mapSize.width = 512;
pointLight.shadow.mapSize.height = 512;
pointLight.shadow.bias = -0.001;
pointLight.shadow.camera.near = 0.5;
pointLight.shadow.camera.far = 50;

scene.add(pointLight);
```

**Performance rule**: ALWAYS prefer SpotLight shadows over PointLight shadows. A PointLight shadow costs 6x what a SpotLight shadow costs. Use PointLight shadows ONLY when omnidirectional shadow casting is absolutely required.

---

## Shadow Debugging with CameraHelper

ALWAYS use `CameraHelper` to visualize the shadow camera frustum when configuring shadows:

```js
const shadowHelper = new THREE.CameraHelper(dirLight.shadow.camera);
scene.add(shadowHelper);
```

The helper renders the frustum as wireframe lines. If shadows are clipped, missing, or low resolution, the helper reveals whether the frustum is too small, too large, or misaligned.

**ALWAYS** remove CameraHelper in production builds.

---

## Shadow Artifact Diagnosis Flowchart

```
Shadows not visible?
├── Check renderer.shadowMap.enabled === true
├── Check light.castShadow === true
├── Check mesh.castShadow / ground.receiveShadow === true
├── Check shadow camera frustum encompasses the scene (use CameraHelper)
└── Check shadow.camera.far is large enough

Striped lines on surfaces? (Shadow Acne)
├── Increase shadow.bias (start at -0.0001, go to -0.005)
├── Increase shadow.normalBias (0.02 to 0.1) for curved surfaces
└── Increase shadow.mapSize for more depth precision

Shadows float away from objects? (Peter Panning)
├── Reduce shadow.bias (you over-corrected for acne)
├── Use shadow.normalBias instead of shadow.bias
└── Increase shadow.mapSize resolution

Shadow edges shimmer when camera moves? (Shadow Swimming)
├── Increase shadow.mapSize resolution
├── Snap shadow camera to texel-aligned positions
└── Use Cascaded Shadow Maps (CSM) for large scenes

Light leaks through thin geometry? (Light Bleeding -- VSM only)
├── Switch from VSMShadowMap to PCFSoftShadowMap
├── Increase geometry thickness
└── Reduce shadow.radius value

Shadows on transparent/alpha-tested materials incorrect?
├── Set material.alphaTest threshold
├── Assign customDepthMaterial with matching alpha map
└── For fully transparent objects: use baked shadows or ContactShadows
```

---

## Transparent Material Shadows

By default, shadows treat ALL geometry as fully opaque. For alpha-tested materials (e.g., tree leaves), assign a `customDepthMaterial`:

```js
import * as THREE from 'three';

const alphaMap = new THREE.TextureLoader().load('leaf-alpha.png');

const leafMaterial = new THREE.MeshStandardMaterial({
  map: texture,
  alphaMap: alphaMap,
  alphaTest: 0.5,
  side: THREE.DoubleSide,
});

// Custom depth material for correct shadow casting
const depthMaterial = new THREE.MeshDepthMaterial({
  depthPacking: THREE.RGBADepthPacking,
  map: texture,
  alphaMap: alphaMap,
  alphaTest: 0.5,
});

leafMesh.material = leafMaterial;
leafMesh.customDepthMaterial = depthMaterial;
leafMesh.castShadow = true;
```

**NEVER** expect transparent objects (`opacity < 1` without `alphaTest`) to cast correct real-time shadows. Use baked shadows or screen-space techniques instead.

---

## Static Shadow Optimization

For scenes where lights and shadow casters do NOT move, disable automatic shadow updates:

```js
renderer.shadowMap.autoUpdate = false;
renderer.shadowMap.needsUpdate = true; // render shadows once
```

Set `renderer.shadowMap.needsUpdate = true` ONLY when something changes. This eliminates per-frame shadow map rendering entirely for static scenes.

Per-light control:
```js
light.shadow.autoUpdate = false;
light.shadow.needsUpdate = true; // update this light's shadow once
```

---

## ContactShadows Alternative (Drei / React Three Fiber)

For ground-plane shadows, Drei's `<ContactShadows>` provides high-quality soft shadows at lower cost than shadow maps:

```jsx
import { ContactShadows } from '@react-three/drei';

<ContactShadows
  position={[0, 0, 0]}
  opacity={0.5}
  scale={10}
  blur={1.5}
  far={1}
/>
```

**Limitations**: Works ONLY for ground-plane shadows. Does NOT project onto arbitrary geometry. Does NOT replace shadow maps for complex scenes.

---

## Performance Budget

| Shadow Type | Cost per Frame | Max Recommended |
|-------------|---------------|-----------------|
| DirectionalLight shadow | 1 render pass | 1-2 lights |
| SpotLight shadow | 1 render pass | 2-4 lights |
| PointLight shadow | 6 render passes | 1 light max |

**Shadow map resolution impact**: Doubling `mapSize` quadruples GPU memory usage. NEVER exceed 4096x4096 on mobile; prefer 2048x2048 or lower.

**ALWAYS** profile with `renderer.info.render.calls` to verify shadow pass count does not exceed your frame budget.

---

## Reference Links

- [references/methods.md](references/methods.md) -- LightShadow API signatures and shadow map type constants
- [references/examples.md](references/examples.md) -- Complete shadow setup examples for each light type
- [references/anti-patterns.md](references/anti-patterns.md) -- Shadow artifacts, causes, and fixes

### Official Sources

- https://threejs.org/docs/#api/en/lights/shadows/LightShadow
- https://threejs.org/docs/#api/en/lights/shadows/DirectionalLightShadow
- https://threejs.org/docs/#api/en/lights/shadows/SpotLightShadow
- https://threejs.org/docs/#api/en/lights/shadows/PointLightShadow
- https://threejs.org/docs/#api/en/renderers/WebGLRenderer (shadowMap property)
- https://threejs.org/docs/#api/en/helpers/CameraHelper
````

### `atelier/.claude/skills/threejs-impl-shadows/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-impl-webgpu/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-impl-webgpu
description: >
  Use when using the Three.js WebGPU renderer, node-based materials,
  TSL (Three Shading Language), or compute shaders. Prevents the common
  mistake of not checking browser support, missing async init, or using
  GLSL with WebGPU. Covers WebGPURenderer, node materials, TSL,
  compute shaders, WebGL fallback, migration guide.
  Keywords: WebGPU, WebGPURenderer, TSL, Three Shading Language, node material, compute shader, WGSL, MeshStandardNodeMaterial, next-gen rendering, modern GPU, WebGPU setup.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+. WebGPU: Chrome 113+, Safari 18+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-impl-webgpu

> **EXPERIMENTAL** — The WebGPU renderer and TSL are under active development.
> API surfaces may change between Three.js releases. Pin your Three.js version.

## Quick Reference

### WebGPURenderer Setup

```javascript
import * as THREE from 'three/webgpu';

const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init(); // MUST await before first render
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setAnimationLoop(animate);
document.body.appendChild(renderer.domElement);
```

**ALWAYS** call `await renderer.init()` before the first `renderer.render()` call.
**ALWAYS** use `renderer.setAnimationLoop(callback)` instead of `requestAnimationFrame`.
**NEVER** call `renderer.render()` before `init()` resolves — this throws a runtime error.

### Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 113+ | Full support |
| Edge | 113+ | Full support |
| Safari | 18+ | Supported |
| Firefox | Experimental | Behind flag (`dom.webgpu.enabled`) |

### Feature Detection and Fallback

```javascript
import { WebGPU } from 'three/webgpu';

if (WebGPU.isAvailable()) {
  const renderer = new THREE.WebGPURenderer({ antialias: true });
  await renderer.init();
} else {
  const renderer = new THREE.WebGLRenderer({ antialias: true });
}
```

**ALWAYS** check `WebGPU.isAvailable()` before creating a WebGPURenderer.
**ALWAYS** provide a WebGLRenderer fallback for unsupported browsers.

### Critical Warnings

**NEVER** write raw GLSL or WGSL strings — ALWAYS use TSL functions. WebGPU compiles TSL to WGSL automatically. GLSL is NOT supported by the WebGPU backend.

**NEVER** use `ShaderMaterial` with WebGPURenderer — use `NodeMaterial` with TSL instead.

**NEVER** use `requestAnimationFrame` with WebGPURenderer — ALWAYS use `renderer.setAnimationLoop()`.

**NEVER** use `EffectComposer` (three/examples) with WebGPURenderer — use the `PostProcessing` class with TSL nodes instead.

---

## Node Materials

Every classic Three.js material has a node-based equivalent. Classic materials auto-convert when used with WebGPURenderer, but node materials provide full TSL customization.

### Material Mapping

| Classic Material | Node Material |
|-----------------|---------------|
| `MeshBasicMaterial` | `MeshBasicNodeMaterial` |
| `MeshStandardMaterial` | `MeshStandardNodeMaterial` |
| `MeshPhysicalMaterial` | `MeshPhysicalNodeMaterial` |
| `MeshPhongMaterial` | `MeshPhongNodeMaterial` |
| `MeshLambertMaterial` | `MeshLambertNodeMaterial` |
| `LineBasicMaterial` | `LineBasicNodeMaterial` |
| `LineDashedMaterial` | `LineDashedNodeMaterial` |
| `PointsMaterial` | `PointsNodeMaterial` |
| `SpriteMaterial` | `SpriteNodeMaterial` |

**ALWAYS** import node materials from `'three/webgpu'`, not from `'three'`.

### NodeMaterial Input Properties

All properties accept TSL node values. All are optional and override defaults.

**Common inputs (all node materials):**

| Property | TSL Type | Purpose |
|----------|----------|---------|
| `.colorNode` | `vec4` | Base color |
| `.opacityNode` | `float` | Opacity |
| `.normalNode` | `vec3` | Normal map replacement |
| `.emissiveNode` | `color` | Emissive output |
| `.positionNode` | `vec3` | Vertex displacement |
| `.fragmentNode` | `vec4` | Full fragment shader replacement |
| `.vertexNode` | `vec4` | Full vertex shader replacement |
| `.outputNode` | `vec4` | Final output override |
| `.aoNode` | `float` | Ambient occlusion |
| `.alphaTestNode` | `float` | Alpha test threshold |
| `.depthNode` | `float` | Custom depth |
| `.castShadowNode` | `vec4` | Shadow casting override |

**Standard/Physical inputs:**

| Property | TSL Type | Purpose |
|----------|----------|---------|
| `.metalnessNode` | `float` | Metalness |
| `.roughnessNode` | `float` | Roughness |
| `.envNode` | `color` | Environment map |
| `.lightsNode` | — | Lighting model override |

**Physical-only inputs:** `.clearcoatNode`, `.clearcoatRoughnessNode`, `.clearcoatNormalNode`, `.sheenNode`, `.iridescenceNode`, `.iridescenceIORNode`, `.iridescenceThicknessNode`, `.specularIntensityNode`, `.specularColorNode`, `.iorNode`, `.transmissionNode`, `.thicknessNode`, `.attenuationDistanceNode`, `.attenuationColorNode`, `.dispersionNode`, `.anisotropyNode`.

---

## TSL (Three Shading Language)

TSL is a JavaScript-based node graph system that compiles to GLSL (WebGL2) and WGSL (WebGPU). It replaces raw shader strings entirely.

### Type System

| Category | Functions |
|----------|-----------|
| Scalars | `float()`, `int()`, `uint()`, `bool()` |
| Vectors | `vec2()`, `vec3()`, `vec4()`, `ivec2()`, `ivec3()`, `ivec4()`, `uvec2()`, `uvec3()`, `uvec4()` |
| Matrices | `mat2()`, `mat3()`, `mat4()` |
| Color | `color()` |
| Conversion | `.toFloat()`, `.toVec3()`, `.toColor()` |

### Variables and Uniforms

| Function | Purpose |
|----------|---------|
| `uniform(value)` | GPU-side dynamic value |
| `toVar(node)` | Reusable shader variable |
| `toConst(node)` | Inline constant |
| `varying(node)` | Vertex-to-fragment interpolation |
| `vertexStage(node)` | Force computation in vertex shader |
| `attribute(name, type)` | Access buffer attributes |

Uniforms support callbacks: `.onRenderUpdate(fn)`, `.onFrameUpdate(fn)`, `.onObjectUpdate(fn)`.

### Operators

All operators are chainable on TSL nodes:

- **Arithmetic:** `.add()`, `.sub()`, `.mul()`, `.div()`, `.mod()`
- **Comparison:** `.equal()`, `.notEqual()`, `.lessThan()`, `.greaterThan()`, `.lessThanEqual()`, `.greaterThanEqual()`
- **Logical:** `.and()`, `.or()`, `.not()`, `.xor()`
- **Assignment:** `.assign()`, `.addAssign()`, `.subAssign()`, `.mulAssign()`, `.divAssign()`
- **Bitwise:** `.bitAnd()`, `.bitOr()`, `.bitXor()`, `.shiftLeft()`, `.shiftRight()`

### Geometry Nodes

| Category | Nodes |
|----------|-------|
| Position | `positionGeometry`, `positionLocal`, `positionWorld`, `positionView`, `positionWorldDirection`, `positionViewDirection` |
| Normal | `normalGeometry`, `normalLocal`, `normalView`, `normalWorld` |
| Tangent | `tangentGeometry`, `tangentLocal`, `tangentView`, `tangentWorld` |
| UV | `uv(index)` |
| Screen | `screenUV`, `screenCoordinate`, `screenSize` |
| Viewport | `viewportUV`, `viewportCoordinate`, `viewportSize` |

### Camera and Model Nodes

- **Camera:** `cameraNear`, `cameraFar`, `cameraPosition`, `cameraProjectionMatrix`, `cameraViewMatrix`, `cameraWorldMatrix`, `cameraNormalMatrix`
- **Model:** `modelViewMatrix`, `modelNormalMatrix`, `modelWorldMatrix`, `modelPosition`, `modelScale`, `modelDirection`

### Animation Nodes

| Node | Purpose |
|------|---------|
| `time` | Elapsed seconds since start |
| `deltaTime` | Frame delta in seconds |
| `oscSine(timer)` | Sine oscillator (0-1) |
| `oscSquare(timer)` | Square wave oscillator |
| `oscTriangle(timer)` | Triangle wave oscillator |
| `oscSawtooth(timer)` | Sawtooth oscillator |

### Texture Operations

| Function | Purpose |
|----------|---------|
| `texture(tex, uv, level)` | Sample with interpolation |
| `textureLoad(tex, uv, level)` | Sample without interpolation |
| `textureStore(tex, uv, value)` | Write to storage texture |
| `textureSize(tex, level)` | Get texture dimensions |
| `cubeTexture(tex, uvw, level)` | Sample cube map |
| `triplanarTexture(texX, texY, texZ, scale, position, normal)` | Triplanar mapping |

### Control Flow

**ALWAYS** use capital `If` — lowercase `if` is JavaScript, not TSL.

```javascript
If(condition, () => {
  // true branch
}).ElseIf(otherCondition, () => {
  // else-if branch
}).Else(() => {
  // false branch
});
```

- `select(condition, trueVal, falseVal)` — ternary operator
- `Loop(count, ({ i }) => { })` — GPU loop, supports `Break()`, `Continue()`
- `Switch(value).Case(val, fn).Default(fn)` — no fallthrough
- `Discard()` — discard fragment
- `Return()` — early return

### Function Definition

```javascript
const myFn = Fn(([param1, param2]) => {
  return param1.add(param2);
});
// Call: myFn(nodeA, nodeB)
```

---

## Compute Shaders

WebGPU enables general-purpose GPU compute via TSL. Compute shaders are NOT available in WebGL fallback mode.

### Setup

```javascript
import { compute, storage } from 'three/webgpu';

const computeNode = compute(shaderFn, count, workgroupSize);
await renderer.computeAsync(computeNode);
```

**ALWAYS** use `await renderer.computeAsync()` — compute dispatch is asynchronous.

### Storage and Atomics

- **Storage:** `storage(attribute, type, count)`, `storageTexture(texture)`
- **Atomics:** `atomicAdd()`, `atomicSub()`, `atomicMax()`, `atomicMin()`, `atomicAnd()`, `atomicOr()`, `atomicXor()`, `atomicStore()`, `atomicLoad()`
- **Barriers:** `workgroupBarrier()`, `storageBarrier()`, `textureBarrier()`
- **Built-in IDs:** `workgroupId`, `localId`, `globalId`, `numWorkgroups`, `subgroupSize`

---

## WebGPU Post-Processing

**NEVER** use the WebGL `EffectComposer` with WebGPURenderer. Use the `PostProcessing` class instead.

```javascript
import { PostProcessing } from 'three/webgpu';
import { bloom, renderOutput } from 'three/tsl';

const postProcessing = new PostProcessing(renderer);
const scenePass = renderOutput(scene, camera);
postProcessing.outputNode = bloom(scenePass);
```

### Available Post-Processing Nodes

`bloom()`, `dof()`, `fxaa()`, `smaa()`, `gaussianBlur()`, `ssr()`, `ssgi()`, `ao()`, `chromaticAberration()`, `film()`, `dotScreen()`, `sobel()`, `afterImage()`, `anamorphic()`, `denoise()`, `lut3D()`, `motionBlur()`, `outline()`, `rgbShift()`, `transition()`, `traa()`, `renderOutput()`

### Color Operations

`luminance()`, `saturation()`, `vibrance()`, `hue()`, `posterize()`, `grayscale()`, `sepia()`

### Blend Modes

`blendBurn()`, `blendDodge()`, `blendOverlay()`, `blendScreen()`, `blendColor()`

---

## WebGL to WebGPU Migration

| Step | Action |
|------|--------|
| 1 | Replace `import * as THREE from 'three'` with `import * as THREE from 'three/webgpu'` |
| 2 | Replace `new WebGLRenderer()` with `new WebGPURenderer()` and add `await renderer.init()` |
| 3 | Replace classic materials with NodeMaterial equivalents (or keep classic — they auto-convert) |
| 4 | Replace `EffectComposer` with `PostProcessing` class and TSL post-processing nodes |
| 5 | Replace raw GLSL `ShaderMaterial` with TSL-based `NodeMaterial` |
| 6 | Replace `requestAnimationFrame` with `renderer.setAnimationLoop()` |

**ALWAYS** make the entry point `async` when using WebGPURenderer — `renderer.init()` returns a Promise.

---

## Reference Links

- [references/methods.md](references/methods.md) — API signatures for WebGPURenderer, NodeMaterial, TSL, compute
- [references/examples.md](references/examples.md) — Working code examples for WebGPU scenes
- [references/anti-patterns.md](references/anti-patterns.md) — Common mistakes and how to avoid them

### Official Sources

- https://threejs.org/docs/
- https://github.com/mrdoob/three.js/wiki/Three.js-Shading-Language
- https://threejs.org/examples/?q=webgpu
````

### `atelier/.claude/skills/threejs-impl-webgpu/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-impl-xr/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-impl-xr
description: >
  Use when building VR or AR experiences with Three.js using WebXR.
  Prevents the common mistake of using requestAnimationFrame instead
  of setAnimationLoop, not handling controller events, or wrong
  reference space. Covers WebXRManager, VRButton, ARButton, controllers,
  hand tracking, hit testing, teleportation.
  Keywords: VR, AR, XR, WebXR, VRButton, ARButton, immersive, controller, hand tracking, hit test, teleportation, headset, virtual reality, augmented reality, VR app, AR experience.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-impl-xr

## Quick Reference

### WebXRManager Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enabled` | `boolean` | `false` | Enable XR rendering |
| `isPresenting` | `boolean` | read-only | Whether an XR session is active |
| `cameraAutoUpdate` | `boolean` | `true` | Auto-update camera from XR device pose |

### WebXRManager Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `getSession()` | `() => XRSession \| null` | Current XR session |
| `setSessionInit(options)` | `(XRSessionInit) => void` | Configure session features before entry |
| `setReferenceSpaceType(type)` | `(string) => void` | Set reference space type |
| `getController(index)` | `(number) => Group` | Get controller target ray space |
| `getControllerGrip(index)` | `(number) => Group` | Get controller grip space |
| `getHand(index)` | `(number) => Group` | Get hand tracking group |
| `setFoveation(level)` | `(number) => void` | Set foveated rendering (0.0–1.0) |
| `getFoveation()` | `() => number` | Get current foveation level |
| `getEnvironmentBlendMode()` | `() => string` | Get blend mode (opaque, additive, alpha-blend) |
| `setFramebufferScaleFactor(scale)` | `(number) => void` | Adjust XR render resolution |

### Session Types

| Type | Use Case |
|------|----------|
| `'immersive-vr'` | Full VR headset experience |
| `'immersive-ar'` | AR passthrough on headset or phone |
| `'inline'` | Non-immersive XR in a browser window |

### Reference Space Types

| Type | Origin | Use Case |
|------|--------|----------|
| `'viewer'` | Head position | HUD elements, gaze-locked UI |
| `'local'` | Initial head position | Seated experiences |
| `'local-floor'` | Floor level at start | Standing VR, ALWAYS preferred for room-scale |
| `'bounded-floor'` | Floor with boundary | Room-scale with guardian |
| `'unbounded'` | World origin | Large-scale AR experiences |

### XR Addon Classes

| Class | Import Path | Purpose |
|-------|-------------|---------|
| `VRButton` | `three/addons/webxr/VRButton.js` | Creates "Enter VR" button with feature detection |
| `ARButton` | `three/addons/webxr/ARButton.js` | Creates "Enter AR" button with feature detection |
| `XRControllerModelFactory` | `three/addons/webxr/XRControllerModelFactory.js` | Loads appropriate controller 3D model |
| `XRHandModelFactory` | `three/addons/webxr/XRHandModelFactory.js` | Creates hand tracking visualization |
| `XRHandPrimitiveModel` | `three/addons/webxr/XRHandPrimitiveModel.js` | Simple geometric hand representation |
| `XREstimatedLight` | `three/addons/webxr/XREstimatedLight.js` | AR environment lighting estimation |
| `XRPlanes` | `three/addons/webxr/XRPlanes.js` | AR plane detection visualization |

### Critical Warnings

**NEVER** use `requestAnimationFrame()` for XR rendering — ALWAYS use `renderer.setAnimationLoop()`. The WebXR API requires its own frame timing; `requestAnimationFrame` stops firing when an XR session is active.

**NEVER** apply heavy post-processing in VR — each effect runs TWICE (once per eye), doubling GPU cost. Dropped frames cause motion sickness.

**ALWAYS** target 72fps (Quest) or 90fps (PC VR) — dropped frames cause nausea and discomfort. There is NO acceptable lower target.

**ALWAYS** set `renderer.xr.enabled = true` BEFORE creating VRButton/ARButton — the button checks this property for feature detection.

**NEVER** forget to add controllers to the scene — `getController()` returns a `Group` that MUST be added via `scene.add()` or it will not render or fire events.

---

## VR Setup

### Minimal VR Scene

```javascript
import * as THREE from 'three';
import { VRButton } from 'three/addons/webxr/VRButton.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 100);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

// Enable XR BEFORE creating VRButton
renderer.xr.enabled = true;
renderer.xr.setReferenceSpaceType('local-floor');
document.body.appendChild(VRButton.createButton(renderer));

// MUST use setAnimationLoop — NEVER requestAnimationFrame
renderer.setAnimationLoop((time, frame) => {
  renderer.render(scene, camera);
});
```

### AR Setup

```javascript
import * as THREE from 'three';
import { ARButton } from 'three/addons/webxr/ARButton.js';

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.xr.enabled = true;

// Configure AR features BEFORE creating ARButton
renderer.xr.setSessionInit({
  requiredFeatures: ['hit-test'],
  optionalFeatures: ['dom-overlay'],
  domOverlay: { root: document.getElementById('overlay') }
});

document.body.appendChild(ARButton.createButton(renderer, {
  requiredFeatures: ['hit-test']
}));

renderer.setAnimationLoop((time, frame) => {
  renderer.render(scene, camera);
});
```

---

## Controllers

### Controller Spaces

Three.js exposes THREE distinct spaces per physical controller:

| Method | Space | Use Case |
|--------|-------|----------|
| `getController(index)` | Target ray | Pointing direction, laser pointer |
| `getControllerGrip(index)` | Grip | Where the hand holds the controller |
| `getHand(index)` | Hand | Full hand tracking skeleton |

ALWAYS add ALL spaces you use to the scene. Each returns a `THREE.Group`.

### Controller Events

| Event | Trigger |
|-------|---------|
| `selectstart` | Primary trigger pressed |
| `selectend` | Primary trigger released |
| `select` | Primary trigger press-and-release |
| `squeezestart` | Grip button pressed |
| `squeezeend` | Grip button released |
| `squeeze` | Grip button press-and-release |
| `connected` | Controller detected (event.data = XRInputSource) |
| `disconnected` | Controller lost |

### Controller Models

```javascript
import { XRControllerModelFactory } from 'three/addons/webxr/XRControllerModelFactory.js';

const factory = new XRControllerModelFactory();

// Target ray space — for laser pointer / interaction ray
const controller0 = renderer.xr.getController(0);
controller0.addEventListener('selectstart', onSelectStart);
controller0.addEventListener('selectend', onSelectEnd);
scene.add(controller0);

// Grip space — for rendering the controller model
const grip0 = renderer.xr.getControllerGrip(0);
grip0.add(factory.createControllerModel(grip0));
scene.add(grip0);
```

### Laser Pointer Visual

```javascript
const geometry = new THREE.BufferGeometry().setFromPoints([
  new THREE.Vector3(0, 0, 0),
  new THREE.Vector3(0, 0, -5)
]);
const material = new THREE.LineBasicMaterial({ color: 0xffffff });
const line = new THREE.Line(geometry, material);
controller0.add(line);
```

---

## Hand Tracking

```javascript
import { XRHandModelFactory } from 'three/addons/webxr/XRHandModelFactory.js';

// Request hand-tracking feature
renderer.xr.setSessionInit({
  optionalFeatures: ['hand-tracking']
});

const handFactory = new XRHandModelFactory();

const hand0 = renderer.xr.getHand(0);
hand0.add(handFactory.createHandModel(hand0, 'mesh'));
scene.add(hand0);

const hand1 = renderer.xr.getHand(1);
hand1.add(handFactory.createHandModel(hand1, 'mesh'));
scene.add(hand1);
```

**Hand model profiles:** `'mesh'` (realistic), `'spheres'` (joint spheres), `'boxes'` (joint boxes).

Hand tracking events fire on the hand group:
- `connected` — hand detected
- `disconnected` — hand lost
- `pinchstart` / `pinchend` — thumb-index pinch gesture

---

## AR Hit Testing

Hit testing places virtual objects on real-world surfaces.

```javascript
let hitTestSource = null;
let hitTestSourceRequested = false;
const reticle = new THREE.Mesh(
  new THREE.RingGeometry(0.15, 0.2, 32).rotateX(-Math.PI / 2),
  new THREE.MeshBasicMaterial()
);
reticle.matrixAutoUpdate = false;
reticle.visible = false;
scene.add(reticle);

renderer.setAnimationLoop((time, frame) => {
  if (frame) {
    const session = renderer.xr.getSession();
    const referenceSpace = renderer.xr.getReferenceSpace();

    if (!hitTestSourceRequested) {
      session.requestReferenceSpace('viewer').then((viewerSpace) => {
        session.requestHitTestSource({ space: viewerSpace }).then((source) => {
          hitTestSource = source;
        });
      });
      hitTestSourceRequested = true;
    }

    if (hitTestSource) {
      const results = frame.getHitTestResults(hitTestSource);
      if (results.length > 0) {
        const pose = results[0].getPose(referenceSpace);
        reticle.visible = true;
        reticle.matrix.fromArray(pose.transform.matrix);
      } else {
        reticle.visible = false;
      }
    }
  }
  renderer.render(scene, camera);
});
```

---

## Teleportation Pattern

```javascript
const tempMatrix = new THREE.Matrix4();
const raycaster = new THREE.Raycaster();
const marker = new THREE.Mesh(
  new THREE.CircleGeometry(0.25, 32).rotateX(-Math.PI / 2),
  new THREE.MeshBasicMaterial({ color: 0x00ff00 })
);
scene.add(marker);

const controller = renderer.xr.getController(0);
controller.addEventListener('selectend', () => {
  tempMatrix.identity().extractRotation(controller.matrixWorld);
  raycaster.ray.origin.setFromMatrixPosition(controller.matrixWorld);
  raycaster.ray.direction.set(0, 0, -1).applyMatrix4(tempMatrix);

  const intersects = raycaster.intersectObject(floor);
  if (intersects.length > 0) {
    const point = intersects[0].point;
    // Move the XR camera rig, NOT the camera directly
    cameraRig.position.set(point.x, 0, point.z);
  }
});
scene.add(controller);
```

**ALWAYS** move a camera rig group (containing the camera), NEVER the camera directly — the WebXR API controls camera position relative to its parent.

---

## VR Performance

### Target Frame Rates

| Platform | Target FPS | Notes |
|----------|-----------|-------|
| Meta Quest 2/3 | 72–120 fps | 72 default, 90/120 optional |
| PC VR (SteamVR) | 90 fps | Standard target |
| PSVR2 | 90–120 fps | Platform-dependent |

### Optimization Techniques

1. **Foveated rendering** — `renderer.xr.setFoveation(1.0)` for maximum performance. Range 0.0 (none) to 1.0 (maximum).
2. **Framebuffer scale** — `renderer.xr.setFramebufferScaleFactor(0.75)` to reduce resolution when GPU-bound.
3. **Minimize draw calls** — Use `THREE.InstancedMesh` for repeated objects. Target < 100 draw calls.
4. **Avoid post-processing** — Each effect renders TWICE in stereo. Remove bloom, SSAO, and anti-aliasing passes when possible.
5. **Use baked lighting** — Real-time shadows are expensive at 2x. Pre-bake where possible.
6. **LOD (Level of Detail)** — Use `THREE.LOD` to reduce polygon count for distant objects.
7. **Texture compression** — Use KTX2/Basis textures to reduce GPU memory.

### Camera Rig Pattern

ALWAYS use a camera rig group for VR locomotion:

```javascript
const cameraRig = new THREE.Group();
cameraRig.add(camera);
scene.add(cameraRig);

// Move the rig, not the camera
cameraRig.position.set(0, 0, 5);
```

The WebXR API sets camera position/rotation each frame relative to its parent. Moving the camera directly is overwritten immediately.

---

## XR Estimated Light (AR)

```javascript
import { XREstimatedLight } from 'three/addons/webxr/XREstimatedLight.js';

const xrLight = new XREstimatedLight(renderer);
xrLight.addEventListener('estimationstart', () => {
  scene.add(xrLight);
  scene.environment = xrLight.environment;
  // Remove default lights
});
xrLight.addEventListener('estimationend', () => {
  scene.remove(xrLight);
  scene.environment = null;
  // Restore default lights
});
```

---

## Reference Links

- [references/methods.md](references/methods.md) — Complete API signatures for WebXRManager and XR addon classes
- [references/examples.md](references/examples.md) — Working code examples for VR, AR, controllers, and hand tracking
- [references/anti-patterns.md](references/anti-patterns.md) — What NOT to do in WebXR development

### Official Sources

- https://threejs.org/docs/#api/en/renderers/webxr/WebXRManager
- https://threejs.org/docs/#manual/en/introduction/How-to-create-VR-content
- https://immersiveweb.dev/
- https://developer.mozilla.org/en-US/docs/Web/API/WebXR_Device_API
````

### `atelier/.claude/skills/threejs-impl-xr/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-syntax-controls/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-syntax-controls
description: >
  Use when adding camera controls to a Three.js scene: orbit, pan, zoom,
  fly, first-person, or object manipulation. Prevents the common mistake
  of forgetting controls.update() in the render loop, not calling
  dispose(), or mixing controls. Covers OrbitControls, MapControls,
  FlyControls, PointerLockControls, TransformControls.
  Keywords: OrbitControls, controls, camera controls, orbit, pan, zoom, MapControls, FlyControls, PointerLockControls, TransformControls, rotate view, move camera, mouse controls, drag to rotate.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-syntax-controls

## Quick Reference

### Control Selection Decision Tree

| Use Case | Control | Why |
|----------|---------|-----|
| Inspect a 3D model from all angles | OrbitControls | Orbit/pan/zoom around a target point |
| Top-down map or 2D-style navigation | MapControls | Left-drag pans, right-drag rotates |
| Free-flight editor or space scene | FlyControls | Six degrees of freedom, WASD + mouse |
| First-person game with pointer lock | PointerLockControls | Hides cursor, captures mouse movement |
| First-person without pointer lock | FirstPersonControls | Mouse-look without browser lock API |
| Move/rotate/scale objects via gizmo | TransformControls | Interactive translate/rotate/scale handles |
| Drag objects along a plane | DragControls | Click-and-drag object repositioning |
| Unconstrained rotation (no gimbal lock) | ArcballControls | Full spherical rotation with animation |
| Unconstrained rotation (simpler) | TrackballControls | Like OrbitControls but no pole constraint |

### Import Paths (Three.js r160+)

```javascript
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { MapControls } from 'three/addons/controls/MapControls.js';
import { FlyControls } from 'three/addons/controls/FlyControls.js';
import { FirstPersonControls } from 'three/addons/controls/FirstPersonControls.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { TrackballControls } from 'three/addons/controls/TrackballControls.js';
import { ArcballControls } from 'three/addons/controls/ArcballControls.js';
import { DragControls } from 'three/addons/controls/DragControls.js';
```

**ALWAYS** use `'three/addons/controls/...'` for r160+. The legacy path `'three/examples/jsm/controls/...'` still works but is deprecated.

### Critical Warnings

**ALWAYS** call `controls.update()` in the animation loop when `enableDamping` or `autoRotate` is `true`. Failing to do so causes the camera to freeze after user interaction ends.

**ALWAYS** call `controls.dispose()` when removing controls. Failing to do so leaks DOM event listeners (pointermove, wheel, keydown) that cause memory leaks and ghost interactions.

**NEVER** attach two camera-control classes to the same camera simultaneously without disabling one. OrbitControls + FlyControls on the same camera causes erratic movement.

**ALWAYS** disable OrbitControls while TransformControls is dragging. Listen to the `dragging-changed` event and toggle `orbitControls.enabled`.

**ALWAYS** call `PointerLockControls.lock()` from a user gesture (click handler). Browsers reject pointer lock requests without user interaction.

**ALWAYS** pass `delta` time to `FlyControls.update(delta)`. Passing no argument or passing elapsed time causes speed to depend on frame rate.

---

## Controls Lifecycle

Every control follows the same lifecycle pattern:

```
construct --> configure --> attach to loop --> dispose on cleanup
```

### Step 1: Construct

```javascript
const controls = new OrbitControls(camera, renderer.domElement);
```

**ALWAYS** pass `renderer.domElement` as the second argument. Passing `document` or `document.body` causes controls to capture events globally, breaking UI overlays.

### Step 2: Configure

```javascript
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 2;
controls.maxDistance = 50;
controls.target.set(0, 1, 0);
```

### Step 3: Update in Render Loop

```javascript
function animate() {
  requestAnimationFrame(animate);
  controls.update(); // REQUIRED when enableDamping or autoRotate is true
  renderer.render(scene, camera);
}
animate();
```

### Step 4: Dispose on Cleanup

```javascript
controls.dispose();
```

---

## OrbitControls

The most commonly used control. Orbits, pans, and zooms around a target point.

### Constructor

```javascript
new OrbitControls(camera: THREE.Camera, domElement: HTMLElement)
```

### Key Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enabled` | `boolean` | `true` | Enable/disable all interaction |
| `target` | `Vector3` | `(0,0,0)` | Orbit focus point |
| `enableDamping` | `boolean` | `false` | Smooth inertial movement |
| `dampingFactor` | `number` | `0.05` | Inertia strength (0-1) |
| `autoRotate` | `boolean` | `false` | Auto-rotate around target |
| `autoRotateSpeed` | `number` | `2.0` | Degrees/sec at 60fps |
| `enablePan` | `boolean` | `true` | Allow panning |
| `enableRotate` | `boolean` | `true` | Allow rotation |
| `enableZoom` | `boolean` | `true` | Allow zooming |
| `minDistance` | `number` | `0` | Min zoom distance (PerspectiveCamera) |
| `maxDistance` | `number` | `Infinity` | Max zoom distance (PerspectiveCamera) |
| `minZoom` | `number` | `0` | Min zoom (OrthographicCamera) |
| `maxZoom` | `number` | `Infinity` | Max zoom (OrthographicCamera) |
| `minPolarAngle` | `number` | `0` | Min vertical angle (radians) |
| `maxPolarAngle` | `number` | `Math.PI` | Max vertical angle (radians) |
| `minAzimuthAngle` | `number` | `-Infinity` | Min horizontal angle (radians) |
| `maxAzimuthAngle` | `number` | `Infinity` | Max horizontal angle (radians) |
| `screenSpacePanning` | `boolean` | `true` | Pan in screen plane (true) or horizontal plane (false) |
| `zoomToCursor` | `boolean` | `false` | Zoom towards cursor position |
| `panSpeed` | `number` | `1.0` | Pan speed multiplier |
| `rotateSpeed` | `number` | `1.0` | Rotation speed multiplier |
| `zoomSpeed` | `number` | `1.0` | Zoom speed multiplier |
| `mouseButtons` | `object` | `{LEFT: ROTATE, MIDDLE: DOLLY, RIGHT: PAN}` | Mouse button mapping |
| `touches` | `object` | `{ONE: ROTATE, TWO: DOLLY_PAN}` | Touch gesture mapping |
| `keys` | `object` | `{LEFT, UP, RIGHT, BOTTOM}` | Arrow key codes for panning |

### Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `update(deltaTime?)` | `(number?) => boolean` | Update controls state. MUST call every frame with damping/autoRotate |
| `dispose()` | `() => void` | Remove all event listeners |
| `saveState()` | `() => void` | Save current camera position/target/zoom |
| `reset()` | `() => void` | Restore to last saved state |
| `getDistance()` | `() => number` | Distance from camera to target |
| `getPolarAngle()` | `() => number` | Vertical angle in radians |
| `getAzimuthalAngle()` | `() => number` | Horizontal angle in radians |
| `listenToKeyEvents(el)` | `(HTMLElement) => void` | Enable keyboard panning |
| `stopListenToKeyEvents()` | `() => void` | Disable keyboard panning |

### Events

| Event | Trigger |
|-------|---------|
| `change` | Camera position or target changed |
| `start` | User interaction began (pointerdown) |
| `end` | User interaction ended (pointerup) |

---

## MapControls

Subclass of OrbitControls optimized for top-down map navigation.

| Button | OrbitControls | MapControls |
|--------|--------------|-------------|
| Left mouse | Rotate | Pan |
| Middle mouse | Dolly | Dolly |
| Right mouse | Pan | Rotate |

All properties, methods, and events are identical to OrbitControls. The ONLY differences are the default `mouseButtons` mapping and `screenSpacePanning` defaulting to `true`.

---

## FlyControls

Six-degrees-of-freedom flight camera. WASD for movement, QE for roll, RF for up/down.

### Key Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `movementSpeed` | `number` | `1.0` | Translation speed |
| `rollSpeed` | `number` | `0.005` | Roll rotation speed |
| `dragToLook` | `boolean` | `false` | Require mouse drag to rotate (vs. always follow mouse) |
| `autoForward` | `boolean` | `false` | Move forward automatically |

### Methods

- `update(delta)` -- **ALWAYS** pass `delta` time from the clock. NEVER omit this argument.
- `dispose()` -- Remove event listeners.

---

## PointerLockControls

First-person camera using the Pointer Lock API. Hides and captures the mouse cursor.

### Key Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `isLocked` | `boolean` | read-only | Whether pointer is currently locked |
| `maxPolarAngle` | `number` | `Math.PI` | Max vertical look angle |
| `minPolarAngle` | `number` | `0` | Min vertical look angle |
| `pointerSpeed` | `number` | `1.0` | Mouse sensitivity multiplier |

### Methods

| Method | Description |
|--------|-------------|
| `lock()` | Request pointer lock (MUST call from user gesture) |
| `unlock()` | Exit pointer lock |
| `connect()` | Attach event listeners |
| `disconnect()` | Remove event listeners |
| `dispose()` | Full cleanup (calls disconnect) |
| `getObject()` | Returns the controlled camera |
| `getDirection(target)` | Write look direction into target Vector3 |
| `moveForward(distance)` | Move camera forward |
| `moveRight(distance)` | Move camera sideways |

### Events

| Event | Trigger |
|-------|---------|
| `change` | Camera orientation changed |
| `lock` | Pointer lock acquired |
| `unlock` | Pointer lock released |

**ALWAYS** implement your own WASD movement in the animation loop. PointerLockControls handles look direction only, NOT position.

---

## TransformControls

Interactive gizmo for moving, rotating, and scaling scene objects.

### Key Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `mode` | `string` | `'translate'` | `'translate'`, `'rotate'`, or `'scale'` |
| `space` | `string` | `'world'` | `'world'` or `'local'` coordinate space |
| `showX` | `boolean` | `true` | Show X axis handle |
| `showY` | `boolean` | `true` | Show Y axis handle |
| `showZ` | `boolean` | `true` | Show Z axis handle |
| `size` | `number` | `1` | Gizmo visual scale |
| `translationSnap` | `number|null` | `null` | Snap to grid (units) |
| `rotationSnap` | `number|null` | `null` | Snap rotation (radians) |
| `scaleSnap` | `number|null` | `null` | Snap scale increment |
| `dragging` | `boolean` | read-only | User is currently dragging |

### Methods

| Method | Description |
|--------|-------------|
| `attach(object)` | Attach gizmo to a scene object |
| `detach()` | Remove gizmo from current object |
| `setMode(mode)` | Set transform mode |
| `setSpace(space)` | Set coordinate space |
| `setSize(size)` | Set gizmo scale |
| `setTranslationSnap(snap)` | Set position snap |
| `setRotationSnap(snap)` | Set rotation snap |
| `setScaleSnap(snap)` | Set scale snap |
| `getRaycaster()` | Access internal raycaster |
| `dispose()` | Cleanup |

### Events

| Event | Trigger |
|-------|---------|
| `change` | Gizmo visual changed |
| `dragging-changed` | `event.value` is `true` when dragging starts, `false` when it ends |
| `objectChange` | Attached object's transform was modified |
| `mouseDown` | Pointer pressed on gizmo |
| `mouseUp` | Pointer released from gizmo |

### Critical Integration Pattern

**ALWAYS** disable camera controls during gizmo drag:

```javascript
transformControls.addEventListener('dragging-changed', (event) => {
  orbitControls.enabled = !event.value;
});
```

**ALWAYS** add TransformControls to the scene: `scene.add(transformControls.getHelper())` or `scene.add(transformControls)`.

---

## Brief Overview: Other Controls

### ArcballControls
Unconstrained rotation with animation states. No polar angle limit -- the camera rotates freely in all directions. Best for CAD-style model inspection.

### TrackballControls
Like OrbitControls without the polar angle constraint. The camera can rotate past the poles. Properties: `rotateSpeed`, `zoomSpeed`, `panSpeed`, `staticMoving`, `dynamicDampingFactor`.

### DragControls
Drag scene objects along a plane. Constructor: `new DragControls(objects, camera, domElement)`. Events: `dragstart`, `drag`, `dragend`, `hoveron`, `hoveroff`.

### FirstPersonControls
Mouse-look camera without pointer lock. Properties: `movementSpeed`, `lookSpeed`, `activeLook`, `constrainVertical`, `verticalMin`, `verticalMax`.

---

## Reference Links

- [references/methods.md](references/methods.md) -- Full API signatures for all controls
- [references/examples.md](references/examples.md) -- Working code examples for each control type
- [references/anti-patterns.md](references/anti-patterns.md) -- What NOT to do

### Official Sources

- https://threejs.org/docs/#examples/en/controls/OrbitControls
- https://threejs.org/docs/#examples/en/controls/MapControls
- https://threejs.org/docs/#examples/en/controls/FlyControls
- https://threejs.org/docs/#examples/en/controls/PointerLockControls
- https://threejs.org/docs/#examples/en/controls/TransformControls
````

### `atelier/.claude/skills/threejs-syntax-controls/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-syntax-geometries/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-syntax-geometries
description: >
  Use when creating 3D shapes, custom geometry, or instanced meshes in
  Three.js. Prevents the common mistake of forgetting dispose(), not
  setting needsUpdate on BufferAttribute, or using non-indexed geometry
  when indexed is better. Covers BufferGeometry, BufferAttribute, all
  21 built-in geometries, InstancedMesh, ExtrudeGeometry, custom geometry.
  Keywords: BufferGeometry, BoxGeometry, SphereGeometry, PlaneGeometry, InstancedMesh, BufferAttribute, geometry, shape, extrude, custom mesh, particles, point cloud, particle system, create shape.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-syntax-geometries

## Quick Reference

### BufferGeometry: Core Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `attributes` | `Object` | `{}` | Hash map of named `BufferAttribute` instances |
| `index` | `BufferAttribute \| null` | `null` | Index buffer for indexed rendering |
| `morphAttributes` | `Object` | `{}` | Morph target attribute arrays |
| `morphTargetsRelative` | `Boolean` | `false` | If `true`, morph data = relative offsets |
| `groups` | `Array` | `[]` | `{ start, count, materialIndex }` for multi-material |
| `drawRange` | `Object` | `{ start: 0, count: Infinity }` | Portion of geometry to render |
| `boundingBox` | `Box3 \| null` | `null` | Cached — `null` until `computeBoundingBox()` |
| `boundingSphere` | `Sphere \| null` | `null` | Cached — `null` until `computeBoundingSphere()` |

### BufferGeometry: Key Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `setAttribute(name, attr)` | `this` | Add or replace a named attribute |
| `getAttribute(name)` | `BufferAttribute` | Retrieve attribute by name |
| `deleteAttribute(name)` | `this` | Remove a named attribute |
| `hasAttribute(name)` | `boolean` | Check if attribute exists |
| `setIndex(attr)` | — | Set the index buffer |
| `addGroup(start, count, materialIndex?)` | — | Define a render group for multi-material |
| `clearGroups()` | — | Remove all groups |
| `setDrawRange(start, count)` | — | Limit rendered range |
| `computeVertexNormals()` | — | Compute smooth normals from face topology |
| `computeTangents()` | — | Compute tangent vectors (requires position, normal, uv, index) |
| `computeBoundingBox()` | — | Compute and cache AABB |
| `computeBoundingSphere()` | — | Compute and cache bounding sphere |
| `toNonIndexed()` | new geometry | Create non-indexed copy with duplicated vertices |
| `translate(x, y, z)` | `this` | Translate vertex positions in-place |
| `rotateX/Y/Z(radians)` | `this` | Rotate vertex positions in-place |
| `scale(x, y, z)` | `this` | Scale vertex positions in-place |
| `center()` | `this` | Center geometry at the origin |
| `dispose()` | — | Free GPU resources |

### BufferAttribute: Constructor and Properties

```javascript
import * as THREE from 'three';

new THREE.BufferAttribute(array: TypedArray, itemSize: number, normalized?: boolean)
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `array` | `TypedArray` | — | The underlying data |
| `itemSize` | `number` | — | Values per vertex (1=scalar, 2=UV, 3=position, 4=RGBA) |
| `count` | `number` | computed | `array.length / itemSize` |
| `needsUpdate` | `boolean` | `false` | Set `true` to upload changes to GPU |
| `usage` | `number` | `StaticDrawUsage` | GPU usage hint |

### Typed Convenience Classes

| Class | Underlying Type | Use Case |
|-------|----------------|----------|
| `Float32BufferAttribute` | `Float32Array` | Positions, normals, UVs (most common) |
| `Float16BufferAttribute` | `Float16Array` | Memory-optimized attributes |
| `Uint16BufferAttribute` | `Uint16Array` | Index buffers (<65536 vertices) |
| `Uint32BufferAttribute` | `Uint32Array` | Index buffers (>65536 vertices) |
| `Uint8BufferAttribute` | `Uint8Array` | Byte colors (with `normalized=true`) |
| `Int8/Int16/Int32BufferAttribute` | Respective arrays | Signed integer data |

### Usage Hints

| Constant | When to Use |
|----------|-------------|
| `THREE.StaticDrawUsage` | Data uploaded once, read many times (default) |
| `THREE.DynamicDrawUsage` | Data updated frequently (particles, animated verts) |
| `THREE.StreamDrawUsage` | Data updated every frame and read once |

### Critical Warnings

**NEVER** forget `attribute.needsUpdate = true` after modifying BufferAttribute data via `setX/setXY/setXYZ` or direct array writes. Without this flag, changes will NOT reach the GPU.

**NEVER** assume `boundingBox` or `boundingSphere` are populated automatically. They are `null` until you explicitly call `computeBoundingBox()` / `computeBoundingSphere()`.

**ALWAYS** call `computeVertexNormals()` after building custom geometry if you need lighting. Without normals, `MeshStandardMaterial` and other lit materials render black.

**ALWAYS** call `geometry.dispose()` when removing geometry from the scene permanently. Failing to dispose leaks GPU memory. The garbage collector does NOT free GPU-side buffers.

**NEVER** call `translate()`, `rotateX()`, `scale()`, or other in-place transform methods in an animation loop. These modify the actual vertex data permanently. Use `mesh.position`, `mesh.rotation`, and `mesh.scale` for runtime transforms.

**ALWAYS** set `usage` to `DynamicDrawUsage` BEFORE the first render if you plan to update attribute data every frame. Changing usage after initial upload has no effect on some GPU drivers.

**NEVER** forget `instanceMatrix.needsUpdate = true` after calling `setMatrixAt()` on InstancedMesh. Without this flag, all instances render at the origin.

---

## Indexed vs Non-Indexed Geometry

| Aspect | Indexed | Non-Indexed |
|--------|---------|-------------|
| Memory | Lower (shared vertices) | Higher (duplicated vertices) |
| GPU cache | Better (vertex reuse) | No reuse |
| Flat shading | Requires duplicated normals | Natural per-face normals |
| Wireframe | Clean edges | May show diagonal lines |

**ALWAYS** use indexed geometry for smooth-shaded meshes with shared vertices. Use `geometry.toNonIndexed()` ONLY when you need per-face attributes (flat shading with unique normals).

---

## All 21 Built-in Geometries

### Primitives

| Geometry | Key Parameters |
|----------|---------------|
| `BoxGeometry` | `(width=1, height=1, depth=1, wSeg=1, hSeg=1, dSeg=1)` |
| `SphereGeometry` | `(radius=1, wSeg=32, hSeg=16, phiStart, phiLen, thetaStart, thetaLen)` |
| `PlaneGeometry` | `(width=1, height=1, wSeg=1, hSeg=1)` |
| `CylinderGeometry` | `(radTop=1, radBot=1, height=1, radSeg=32, hSeg=1, open, thetaStart, thetaLen)` |
| `ConeGeometry` | `(radius=1, height=1, radSeg=32, hSeg=1, open, thetaStart, thetaLen)` |
| `CapsuleGeometry` | `(radius=1, length=1, capSeg=4, radSeg=8)` |
| `TorusGeometry` | `(radius=1, tube=0.4, radSeg=12, tubSeg=48, arc=2PI)` |
| `TorusKnotGeometry` | `(radius=1, tube=0.4, tubSeg=64, radSeg=8, p=2, q=3)` |
| `CircleGeometry` | `(radius=1, seg=32, thetaStart=0, thetaLen=2PI)` |
| `RingGeometry` | `(inner=0.5, outer=1, thetaSeg=32, phiSeg=1, thetaStart, thetaLen)` |

### Polyhedra

All accept `(radius=1, detail=0)`. Detail controls subdivision level.

| Geometry | Base Faces |
|----------|-----------|
| `TetrahedronGeometry` | 4 |
| `OctahedronGeometry` | 8 |
| `DodecahedronGeometry` | 12 |
| `IcosahedronGeometry` | 20 |
| `PolyhedronGeometry` | custom (`vertices, indices, radius, detail`) |

### Path-Based

| Geometry | Description |
|----------|-------------|
| `ExtrudeGeometry(shapes, options)` | Extrude 2D Shape into 3D |
| `ShapeGeometry(shapes, curveSegments=12)` | Flat 2D geometry from Shape |
| `LatheGeometry(points, segments=12, phiStart, phiLength)` | Revolve 2D profile around Y axis |
| `TubeGeometry(path, tubSeg=64, radius=1, radSeg=8, closed)` | Tube along a Curve3 |

### Utility

| Geometry | Description |
|----------|-------------|
| `EdgesGeometry(geometry, thresholdAngle=1)` | Edges where angle > threshold (clean outlines) |
| `WireframeGeometry(geometry)` | ALL triangle edges (debug visualization) |

---

## ExtrudeGeometry Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `depth` | `number` | `1` | Extrusion depth |
| `steps` | `number` | `1` | Subdivision steps along depth |
| `bevelEnabled` | `boolean` | `true` | Enable beveled edges |
| `bevelThickness` | `number` | `0.2` | Bevel depth into shape |
| `bevelSize` | `number` | `bevelThickness - 0.1` | Bevel distance from outline |
| `bevelOffset` | `number` | `0` | Bevel offset from edge |
| `bevelSegments` | `number` | `3` | Bevel resolution |
| `curveSegments` | `number` | `12` | Points on curves |
| `extrudePath` | `Curve` | `undefined` | 3D path to extrude along |
| `UVGenerator` | `Object` | `WorldUVGenerator` | Custom UV generation |

---

## Shape Class: 2D Path Drawing

```javascript
import * as THREE from 'three';

const shape = new THREE.Shape();
shape.moveTo(x, y);                                    // Start new subpath
shape.lineTo(x, y);                                    // Straight line
shape.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y);   // Cubic Bezier
shape.quadraticCurveTo(cpx, cpy, x, y);                // Quadratic Bezier
shape.splineThru(points);                               // Smooth spline through Vector2[]
shape.arc(aX, aY, radius, startAngle, endAngle, cw);   // Relative arc
shape.absarc(aX, aY, radius, startAngle, endAngle, cw); // Absolute arc

// Holes
const holePath = new THREE.Path();
holePath.absarc(0, 0, 0.5, 0, Math.PI * 2);
shape.holes.push(holePath);
```

---

## Morph Targets

```javascript
import * as THREE from 'three';

// Define morph target positions
const morphPositions = new Float32Array([/* ... */]);
geometry.morphAttributes.position = [
  new THREE.BufferAttribute(morphPositions, 3)
];

// Control on the mesh
mesh.morphTargetInfluences[0] = 0.5; // 50% blend toward morph target 0

// Named morph targets (from glTF)
mesh.morphTargetDictionary; // { "smile": 0, "frown": 1 }
```

Set `geometry.morphTargetsRelative = true` when morph data represents offsets rather than absolute positions.

---

## InstancedMesh

```javascript
import * as THREE from 'three';

const mesh = new THREE.InstancedMesh(geometry, material, count);
```

| Property | Type | Description |
|----------|------|-------------|
| `instanceMatrix` | `InstancedBufferAttribute` | 4x4 matrices (16 floats per instance) |
| `instanceColor` | `InstancedBufferAttribute \| null` | Per-instance RGB (created on first `setColorAt`) |
| `count` | `number` | Instance count (read-only after construction) |

| Method | Description |
|--------|-------------|
| `setMatrixAt(index, matrix4)` | Set transform for instance |
| `getMatrixAt(index, matrix4)` | Read transform into target |
| `setColorAt(index, color)` | Set per-instance color |
| `getColorAt(index, color)` | Read per-instance color |

### Performance Guidelines

| Instance Count | Recommendation |
|---------------|----------------|
| < 10 | Use individual `Mesh` objects |
| 10 - 100 | Either approach; profile your case |
| 100 - 10,000 | ALWAYS use `InstancedMesh` |
| > 10,000 | Use `InstancedMesh` with spatial subdivision or `BatchedMesh` (r160+) |

### Custom Per-Instance Attributes

```javascript
import * as THREE from 'three';

const phases = new Float32Array(count);
for (let i = 0; i < count; i++) phases[i] = Math.random();
mesh.geometry.setAttribute('aPhase', new THREE.InstancedBufferAttribute(phases, 1));
// Access in vertex shader: attribute float aPhase;
```

---

## Multi-Material with Groups

```javascript
import * as THREE from 'three';

geometry.addGroup(0, 6, 0);    // First 6 indices -> material[0]
geometry.addGroup(6, 6, 1);    // Next 6 indices  -> material[1]
const mesh = new THREE.Mesh(geometry, [materialA, materialB]);
```

---

## InterleavedBuffer

For optimal GPU cache performance on large meshes (10,000+ vertices):

```javascript
import * as THREE from 'three';

const stride = 8; // 3 (position) + 3 (normal) + 2 (uv)
const buffer = new THREE.InterleavedBuffer(new Float32Array(vertexCount * stride), stride);

geometry.setAttribute('position', new THREE.InterleavedBufferAttribute(buffer, 3, 0));
geometry.setAttribute('normal',   new THREE.InterleavedBufferAttribute(buffer, 3, 3));
geometry.setAttribute('uv',       new THREE.InterleavedBufferAttribute(buffer, 2, 6));
```

**ALWAYS** use separate buffers when individual attributes are updated independently. Use interleaved buffers ONLY when all attributes are static or updated together.

---

## Disposal Rules

- **ALWAYS** call `geometry.dispose()` when removing geometry from the scene permanently
- Shared geometries (used by multiple meshes): dispose ONLY after ALL meshes are removed
- Built-in geometries: dispose when the mesh using them is removed
- The JavaScript garbage collector does NOT free GPU-side vertex buffers

---

## Reference Links

- [references/methods.md](references/methods.md) — Complete API signatures for BufferGeometry, BufferAttribute, InstancedMesh
- [references/examples.md](references/examples.md) — Working code examples for custom geometry, instancing, extrusion
- [references/anti-patterns.md](references/anti-patterns.md) — What NOT to do with geometry in Three.js

### Official Sources

- https://threejs.org/docs/#api/en/core/BufferGeometry
- https://threejs.org/docs/#api/en/core/BufferAttribute
- https://threejs.org/docs/#api/en/objects/InstancedMesh
- https://threejs.org/docs/#api/en/geometries/ExtrudeGeometry
- https://threejs.org/docs/#api/en/extras/core/Shape
````

### `atelier/.claude/skills/threejs-syntax-geometries/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-syntax-loaders/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-syntax-loaders
description: >
  Use when loading 3D models (GLTF, FBX, OBJ), textures, or HDR
  environment maps in Three.js. Prevents the common mistake of not
  setting up DRACOLoader, wrong WASM path, or missing error handling.
  Covers GLTFLoader, DRACOLoader, KTX2Loader, TextureLoader, RGBELoader,
  FBXLoader, OBJLoader, LoadingManager.
  Keywords: GLTFLoader, GLTF, GLB, load model, DRACOLoader, texture, FBXLoader, OBJLoader, RGBELoader, HDR, LoadingManager, progress, export, GLTFExporter, save model, download 3D, import 3D file.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-syntax-loaders

## Quick Reference

### Loader Architecture

All Three.js loaders extend the `Loader` base class and share two loading patterns:

```javascript
// Callback style
loader.load(url, onLoad, onProgress, onError);

// Promise style (preferred)
const result = await loader.loadAsync(url, onProgress);
```

### Import Paths

| Loader | Import |
|--------|--------|
| `TextureLoader` | `import { TextureLoader } from 'three';` |
| `CubeTextureLoader` | `import { CubeTextureLoader } from 'three';` |
| `GLTFLoader` | `import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';` |
| `DRACOLoader` | `import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';` |
| `KTX2Loader` | `import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';` |
| `FBXLoader` | `import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';` |
| `OBJLoader` | `import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';` |
| `MTLLoader` | `import { MTLLoader } from 'three/addons/loaders/MTLLoader.js';` |
| `RGBELoader` | `import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';` |
| `MeshoptDecoder` | `import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';` |

### Format Recommendation

**ALWAYS prefer glTF/GLB** over other 3D formats. glTF is the recommended format for Three.js. It supports PBR materials, animations, cameras, lights, and scene hierarchy in a single file. Use `.glb` (binary glTF) for single-file distribution.

### Critical Warnings

**NEVER** call `loader.load()` inside `requestAnimationFrame` or any render loop. Load assets once at initialization and cache the result.

**NEVER** forget to set the DRACOLoader decoder path before loading Draco-compressed models. The path MUST point to a directory containing `draco_decoder.wasm`.

**NEVER** skip error handling on `loadAsync` calls. ALWAYS wrap in try/catch. Failed loads without error handlers crash silently.

**NEVER** forget to dispose loaded models when removing them. GLTF models contain meshes, materials, and textures that ALL require disposal.

**ALWAYS** set `texture.colorSpace = THREE.SRGBColorSpace` on diffuse/color textures (map, emissiveMap). NEVER set SRGBColorSpace on data textures (normalMap, roughnessMap, metalnessMap, aoMap).

**ALWAYS** call `dracoLoader.dispose()` after all Draco-compressed models are loaded to free the WASM decoder memory.

---

## Loader Base Class

Every loader inherits these methods from `Loader`:

| Method | Signature | Purpose |
|--------|-----------|---------|
| `load` | `(url, onLoad, onProgress, onError)` | Callback-based loading |
| `loadAsync` | `(url, onProgress) => Promise` | Promise-based loading |
| `setPath` | `(path: string)` | Set base URL prefix for all loads |
| `setResourcePath` | `(path: string)` | Set resource resolution path |
| `setCrossOrigin` | `(value: string)` | Set CORS mode |
| `setWithCredentials` | `(value: boolean)` | Enable credentials for cross-origin |
| `setRequestHeader` | `(header: object)` | Set custom HTTP headers |

---

## LoadingManager

Coordinates multiple loaders and tracks overall progress.

```javascript
import * as THREE from 'three';

const manager = new THREE.LoadingManager(
  () => { console.log('All assets loaded'); },
  (url, loaded, total) => { console.log(`Progress: ${loaded}/${total}`); },
  (url) => { console.error(`Failed to load: ${url}`); }
);

// Pass manager to any loader
const textureLoader = new THREE.TextureLoader(manager);
const gltfLoader = new GLTFLoader(manager);
```

### Manager Callbacks

| Callback | Signature | When |
|----------|-----------|------|
| `onStart` | `(url, itemsLoaded, itemsTotal)` | First item begins loading |
| `onLoad` | `()` | All items finished |
| `onProgress` | `(url, itemsLoaded, itemsTotal)` | Each item completes |
| `onError` | `(url)` | An item fails |

### Manager Methods

| Method | Purpose |
|--------|---------|
| `itemStart(url)` | Manually register a loading item |
| `itemEnd(url)` | Manually mark item as loaded |
| `itemError(url)` | Manually mark item as failed |
| `resolveURL(url)` | Resolve URL through modifiers |
| `setURLModifier(callback)` | Custom URL rewriting (blob URLs, service workers) |

---

## GLTFLoader

The primary loader for 3D models. glTF 2.0 supports meshes, PBR materials, animations, cameras, lights, and scene hierarchy.

### Setup with Draco Compression

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.6/');

const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);
```

### Setup with KTX2 Textures

```javascript
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';

const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath('/basis/');
ktx2Loader.detectSupport(renderer); // MUST pass renderer instance

gltfLoader.setKTX2Loader(ktx2Loader);
```

### Setup with Meshopt Decoder

```javascript
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

await MeshoptDecoder.ready;
gltfLoader.setMeshoptDecoder(MeshoptDecoder);
```

### Loading a Model

```javascript
try {
  const gltf = await gltfLoader.loadAsync('model.glb');
  scene.add(gltf.scene);
} catch (error) {
  console.error('Failed to load model:', error);
}
```

### GLTF Result Object

```javascript
{
  scene: THREE.Group,                    // Root scene node -- add this to your scene
  scenes: THREE.Group[],                 // All scenes in the file
  cameras: THREE.Camera[],              // Embedded cameras
  animations: THREE.AnimationClip[],    // Animation data for AnimationMixer
  asset: { generator: string, version: string },  // File metadata
  parser: GLTFParser,                    // Internal parser (advanced use)
  userData: {}                           // Custom glTF extensions
}
```

### GLTFLoader Methods

| Method | Signature | Purpose |
|--------|-----------|---------|
| `load` | `(url, onLoad, onProgress, onError)` | Load with callbacks |
| `loadAsync` | `(url, onProgress) => Promise<GLTF>` | Load with Promise |
| `parse` | `(data, path, onLoad, onError)` | Parse ArrayBuffer or JSON directly |
| `setDRACOLoader` | `(dracoLoader: DRACOLoader)` | Enable Draco decompression |
| `setKTX2Loader` | `(ktx2Loader: KTX2Loader)` | Enable KTX2 texture decompression |
| `setMeshoptDecoder` | `(decoder)` | Enable meshopt decompression |
| `register` | `(plugin)` | Register a glTF extension plugin |
| `unregister` | `(plugin)` | Unregister a glTF extension plugin |

---

## DRACOLoader

Decodes Draco-compressed geometry. Reduces mesh file size by 80-90%.

| Method | Signature | Purpose |
|--------|-----------|---------|
| `setDecoderPath` | `(path: string)` | Path to directory containing WASM decoders |
| `setDecoderConfig` | `(config: object)` | `{ type: 'js' \| 'wasm' }` -- WASM is default and faster |
| `preload` | `()` | Pre-fetch decoder WASM before first use |
| `dispose` | `()` | Free WASM decoder memory |

**ALWAYS** call `dracoLoader.dispose()` after loading all Draco-compressed models.

---

## TextureLoader

Loads 2D textures (PNG, JPG, WebP) into `THREE.Texture`.

```javascript
const loader = new THREE.TextureLoader();
const texture = await loader.loadAsync('diffuse.jpg');
texture.colorSpace = THREE.SRGBColorSpace; // ALWAYS for color textures
texture.wrapS = THREE.RepeatWrapping;
texture.wrapT = THREE.RepeatWrapping;
material.map = texture;
```

---

## CubeTextureLoader

Loads six images as a cube map for skyboxes or environment reflections.

```javascript
const cubeLoader = new THREE.CubeTextureLoader();
cubeLoader.setPath('/textures/cube/');
const cubeTexture = cubeLoader.load([
  'px.jpg', 'nx.jpg',  // positive-x, negative-x
  'py.jpg', 'ny.jpg',  // positive-y, negative-y
  'pz.jpg', 'nz.jpg'   // positive-z, negative-z
]);
scene.background = cubeTexture;
scene.environment = cubeTexture;
```

---

## RGBELoader

Loads HDR environment maps in Radiance `.hdr` format.

```javascript
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

const rgbeLoader = new RGBELoader();
rgbeLoader.load('environment.hdr', (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = texture; // PBR environment lighting
  scene.background = texture;  // Optional: visible HDR background
});
```

The RGBELoader sets color space automatically. NEVER manually override the color space on HDR textures.

---

## FBXLoader

Loads Autodesk FBX models. Supports meshes, materials, and skeletal animations.

```javascript
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';

const fbxLoader = new FBXLoader();
const model = await fbxLoader.loadAsync('character.fbx');
scene.add(model);
```

---

## OBJLoader + MTLLoader

Loads Wavefront OBJ geometry with optional MTL material files.

```javascript
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { MTLLoader } from 'three/addons/loaders/MTLLoader.js';

const mtlLoader = new MTLLoader();
const materials = await mtlLoader.loadAsync('model.mtl');
materials.preload();

const objLoader = new OBJLoader();
objLoader.setMaterials(materials);
const model = await objLoader.loadAsync('model.obj');
scene.add(model);
```

**ALWAYS** load the MTL file first, then pass the materials to OBJLoader before loading the OBJ file.

---

## Disposing Loaded Models

**ALWAYS** traverse and dispose ALL resources when removing a loaded model:

```javascript
function disposeModel(model) {
  model.traverse((child) => {
    if (child.isMesh) {
      child.geometry.dispose();
      if (Array.isArray(child.material)) {
        child.material.forEach((mat) => {
          disposeMaterial(mat);
        });
      } else {
        disposeMaterial(child.material);
      }
    }
  });
  model.removeFromParent();
}

function disposeMaterial(material) {
  for (const key of Object.keys(material)) {
    const value = material[key];
    if (value && typeof value === 'object' && 'dispose' in value) {
      value.dispose(); // Disposes textures
    }
  }
  material.dispose();
}
```

---

## Reference Links

- [references/methods.md](references/methods.md) -- Complete API signatures for all loaders
- [references/examples.md](references/examples.md) -- Working code examples for common loading scenarios
- [references/anti-patterns.md](references/anti-patterns.md) -- What NOT to do when loading assets

### Official Sources

- https://threejs.org/docs/#api/en/loaders/Loader
- https://threejs.org/docs/#api/en/loaders/LoadingManager
- https://threejs.org/docs/#api/en/loaders/TextureLoader
- https://threejs.org/docs/#examples/en/loaders/GLTFLoader
- https://threejs.org/docs/#examples/en/loaders/DRACOLoader
- https://threejs.org/docs/#examples/en/loaders/KTX2Loader
- https://threejs.org/docs/#examples/en/loaders/FBXLoader
- https://threejs.org/docs/#examples/en/loaders/OBJLoader
- https://threejs.org/docs/#examples/en/loaders/RGBELoader
````

### `atelier/.claude/skills/threejs-syntax-loaders/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-syntax-materials/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-syntax-materials
description: >
  Use when choosing or configuring materials, loading textures, or setting
  up PBR workflows in Three.js. Prevents the common mistake of wrong
  color space on textures, forgetting material.dispose(), or not calling
  material.needsUpdate after changes. Covers all 15+ material types, PBR
  metalness/roughness, MeshPhysicalMaterial, texture maps, color space.
  Keywords: MeshStandardMaterial, MeshPhysicalMaterial, material, texture, PBR, metalness, roughness, normalMap, color space, SRGBColorSpace, blurry texture, pixelated, texture quality, filtering.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-syntax-materials

## Quick Reference

### Material Type Decision Tree

| Use Case | Material | Why |
|----------|----------|-----|
| UI elements, unlit scenes | `MeshBasicMaterial` | Cheapest, no light computation |
| Matte diffuse (low-end devices) | `MeshLambertMaterial` | Fast diffuse, no specular |
| Legacy specular highlights | `MeshPhongMaterial` | Blinn-Phong model, not physically correct |
| General-purpose 3D (recommended) | `MeshStandardMaterial` | PBR metalness/roughness, industry standard |
| Glass, car paint, fabric, soap bubbles | `MeshPhysicalMaterial` | Advanced PBR (clearcoat, transmission, sheen, iridescence) |
| Cartoon/anime style | `MeshToonMaterial` | Discrete cel-shading steps |
| Sculpting previews, no lights | `MeshMatcapMaterial` | Matcap texture, zero light setup |
| Debug normals | `MeshNormalMaterial` | RGB = surface normal direction |
| Invisible shadow receiver | `ShadowMaterial` | Transparent shadow catcher |
| Solid lines | `LineBasicMaterial` | Simple colored lines |
| Dashed lines | `LineDashedMaterial` | Requires `line.computeLineDistances()` |
| Particles | `PointsMaterial` | Point cloud rendering |
| Billboards | `SpriteMaterial` | Always-facing-camera quads |

### Base Material Properties (All Materials)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `side` | `number` | `FrontSide` | `FrontSide`, `BackSide`, or `DoubleSide` |
| `transparent` | `boolean` | `false` | Enable alpha blending |
| `opacity` | `number` | `1` | Requires `transparent: true` to take effect below 1 |
| `depthWrite` | `boolean` | `true` | Write to depth buffer |
| `depthTest` | `boolean` | `true` | Test against depth buffer |
| `blending` | `number` | `NormalBlending` | `NoBlending`, `AdditiveBlending`, `SubtractiveBlending`, `MultiplyBlending`, `CustomBlending` |
| `alphaTest` | `number` | `0` | Discard fragments with alpha below this value |
| `visible` | `boolean` | `true` | Whether to render this material |
| `wireframe` | `boolean` | `false` | Wireframe rendering mode |
| `fog` | `boolean` | `true` | Affected by scene fog |
| `clippingPlanes` | `Plane[]` | `null` | Array of clipping planes |
| `clipIntersection` | `boolean` | `false` | Clip where ALL planes intersect (vs union) |
| `needsUpdate` | `boolean` | `false` | Set `true` to trigger shader recompilation |
| `toneMapped` | `boolean` | `true` | Apply renderer tone mapping |

### Base Material Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `clone` | `(): Material` | Clone the material |
| `copy` | `(source: Material): Material` | Copy properties from source |
| `dispose` | `(): void` | Free GPU resources -- ALWAYS call when removing |
| `onBeforeCompile` | `(shader, renderer): void` | Hook to modify shader before compilation |
| `setValues` | `(values: Object): void` | Set multiple properties at once |

### Critical Warnings

**NEVER** set `opacity < 1` without `transparent: true` -- the opacity value is silently ignored. ALWAYS pair them together.

**NEVER** use `MeshPhysicalMaterial` when `MeshStandardMaterial` suffices -- Physical compiles a significantly larger shader. ONLY use it when you need clearcoat, transmission, sheen, iridescence, or anisotropy.

**NEVER** set `SRGBColorSpace` on normal maps, roughness maps, metalness maps, or any data texture -- this corrupts the data and causes incorrect lighting. ONLY set `SRGBColorSpace` on diffuse/color/emissive textures.

**NEVER** forget to call `material.dispose()` and `texture.dispose()` when removing objects -- GPU memory leaks accumulate and crash the application.

**NEVER** set `linewidth > 1` on `LineBasicMaterial` -- it is silently ignored on most platforms due to WebGL limitations. ALWAYS use `Line2` + `LineMaterial` from `three/addons/lines/` for thick lines.

**ALWAYS** set `material.needsUpdate = true` after changing properties that affect shader compilation (e.g., toggling `flatShading`, changing `side`, adding/removing texture maps at runtime).

**ALWAYS** set `wrapS` and `wrapT` to `RepeatWrapping` when using `texture.repeat` values other than `(1, 1)` -- the default `ClampToEdgeWrapping` does NOT tile textures.

---

## MeshStandardMaterial (PBR)

The recommended material for most 3D scenes. Uses physically-based metalness/roughness workflow.

```javascript
import { MeshStandardMaterial, TextureLoader, SRGBColorSpace, RepeatWrapping } from 'three';

const loader = new TextureLoader();
const material = new MeshStandardMaterial({
  color: 0xffffff,
  roughness: 0.7,           // 0 = mirror, 1 = fully rough
  metalness: 0.0,           // 0 = dielectric, 1 = metal
  map: null,                // Diffuse/albedo texture
  roughnessMap: null,       // Per-pixel roughness
  metalnessMap: null,       // Per-pixel metalness
  normalMap: null,          // Surface normal perturbation
  normalScale: new Vector2(1, 1),
  aoMap: null,              // Ambient occlusion (requires uv2)
  aoMapIntensity: 1.0,
  emissive: 0x000000,       // Emissive color
  emissiveMap: null,        // Emissive texture
  emissiveIntensity: 1.0,
  envMap: null,             // Environment reflection map
  envMapIntensity: 1.0,
  bumpMap: null,            // Grayscale height map
  bumpScale: 1.0,
  displacementMap: null,    // Vertex displacement map
  displacementScale: 1.0,
  displacementBias: 0.0,
  alphaMap: null,           // Per-pixel transparency
  lightMap: null,           // Baked lighting (requires uv2)
  lightMapIntensity: 1.0,
  flatShading: false,
  wireframe: false,
  fog: true
});
```

---

## MeshPhysicalMaterial (Advanced PBR)

Extends `MeshStandardMaterial` with ALL its properties, plus:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `clearcoat` | `float` | `0.0` | Clear coat layer intensity (0-1) |
| `clearcoatRoughness` | `float` | `0.0` | Clear coat roughness |
| `clearcoatMap` | `Texture` | `null` | Clear coat intensity map |
| `clearcoatNormalMap` | `Texture` | `null` | Clear coat normal map |
| `transmission` | `float` | `0.0` | Physically-based transparency (0-1) |
| `transmissionMap` | `Texture` | `null` | Transmission map |
| `thickness` | `float` | `0.0` | Volume thickness for transmission |
| `thicknessMap` | `Texture` | `null` | Thickness map |
| `ior` | `float` | `1.5` | Index of refraction (1.0-2.333) |
| `attenuationDistance` | `float` | `Infinity` | Light attenuation distance in volume |
| `attenuationColor` | `Color` | `white` | Light attenuation tint |
| `sheen` | `float` | `0.0` | Sheen layer intensity (fabric-like) |
| `sheenColor` | `Color` | `0x000000` | Sheen tint color |
| `sheenRoughness` | `float` | `1.0` | Sheen roughness |
| `iridescence` | `float` | `0.0` | Thin-film interference (0-1) |
| `iridescenceIOR` | `float` | `1.3` | Iridescence index of refraction |
| `iridescenceThicknessRange` | `[float, float]` | `[100, 400]` | Thin-film thickness range (nm) |
| `anisotropy` | `float` | `0.0` | Anisotropic reflection strength |
| `anisotropyRotation` | `float` | `0.0` | Anisotropy rotation (radians) |
| `specularIntensity` | `float` | `1.0` | Specular layer intensity |
| `specularColor` | `Color` | `white` | Specular tint color |
| `dispersion` | `float` | `0.0` | Chromatic dispersion (rainbow effect) |
| `reflectivity` | `float` | `0.5` | Reflectivity at normal incidence |

---

## Texture System

### Color Space Rules (Critical)

| Map Type | Color Space | Channels Used |
|----------|-------------|---------------|
| `map` (diffuse/albedo) | `SRGBColorSpace` | RGB(A) |
| `emissiveMap` | `SRGBColorSpace` | RGB |
| `lightMap` | `SRGBColorSpace` | RGB |
| `envMap` | `SRGBColorSpace` | RGB |
| `sheenColorMap` | `SRGBColorSpace` | RGB |
| `specularColorMap` | `SRGBColorSpace` | RGB |
| `normalMap` | `NoColorSpace` | RGB |
| `roughnessMap` | `NoColorSpace` | G channel |
| `metalnessMap` | `NoColorSpace` | B channel |
| `aoMap` | `NoColorSpace` | R channel |
| `bumpMap` | `NoColorSpace` | R channel |
| `displacementMap` | `NoColorSpace` | R channel |
| `alphaMap` | `NoColorSpace` | R channel |
| `clearcoatMap` | `NoColorSpace` | R channel |
| `clearcoatRoughnessMap` | `NoColorSpace` | R channel |
| `clearcoatNormalMap` | `NoColorSpace` | RGB |
| `transmissionMap` | `NoColorSpace` | R channel |
| `thicknessMap` | `NoColorSpace` | R channel |
| `iridescenceMap` | `NoColorSpace` | R channel |
| `iridescenceThicknessMap` | `NoColorSpace` | R channel |
| `sheenRoughnessMap` | `NoColorSpace` | R channel |
| `anisotropyMap` | `NoColorSpace` | RG channels |
| `specularIntensityMap` | `NoColorSpace` | A channel |

**Rule**: Diffuse/emissive/color textures = `SRGBColorSpace`. ALL data textures = `NoColorSpace`. Getting this wrong causes washed-out or over-saturated rendering.

### Texture Loaders

| Loader | Format | Import |
|--------|--------|--------|
| `TextureLoader` | PNG, JPG, WebP | `three` core |
| `CubeTextureLoader` | 6x PNG/JPG cube maps | `three` core |
| `RGBELoader` | .hdr (Radiance HDR) | `three/addons/loaders/RGBELoader.js` |
| `EXRLoader` | .exr (OpenEXR HDR) | `three/addons/loaders/EXRLoader.js` |
| `KTX2Loader` | .ktx2 (GPU compressed) | `three/addons/loaders/KTX2Loader.js` |

### Wrapping Modes

| Constant | Description |
|----------|-------------|
| `ClampToEdgeWrapping` | Edge texels stretched (default) |
| `RepeatWrapping` | Texture tiles/repeats |
| `MirroredRepeatWrapping` | Tiles with alternating mirror |

### Filter Modes

| Constant | Type | Description |
|----------|------|-------------|
| `NearestFilter` | Mag/Min | Pixelated, crisp (retro, toon gradients) |
| `LinearFilter` | Mag/Min | Smooth interpolation |
| `LinearMipmapLinearFilter` | Min | Trilinear filtering (default, best quality) |

### Texture Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `wrapS` / `wrapT` | `number` | `ClampToEdgeWrapping` | Wrapping mode |
| `magFilter` | `number` | `LinearFilter` | Magnification filter |
| `minFilter` | `number` | `LinearMipmapLinearFilter` | Minification filter |
| `anisotropy` | `number` | `1` | Anisotropic filtering (max = `renderer.capabilities.getMaxAnisotropy()`) |
| `repeat` | `Vector2` | `(1, 1)` | UV repeat count |
| `offset` | `Vector2` | `(0, 0)` | UV offset |
| `rotation` | `number` | `0` | UV rotation in radians |
| `center` | `Vector2` | `(0, 0)` | Center of rotation |
| `flipY` | `boolean` | `true` | Flip vertically on upload |
| `colorSpace` | `string` | `NoColorSpace` | Color space interpretation |
| `generateMipmaps` | `boolean` | `true` | Auto-generate mipmaps |
| `needsUpdate` | `boolean` | `false` | Trigger GPU re-upload |

### flipY Rules

- `flipY = true` (default): Correct for loaded image textures (PNG, JPG)
- `flipY = false`: ALWAYS use for `WebGLRenderTarget` textures, `DataTexture`, and framebuffer textures

---

## Material Disposal

```javascript
// ALWAYS dispose materials and textures when removing objects
function disposeMesh(mesh) {
  if (mesh.material) {
    // Dispose all texture maps
    for (const key of Object.keys(mesh.material)) {
      const value = mesh.material[key];
      if (value && value.isTexture) {
        value.dispose();
      }
    }
    mesh.material.dispose();
  }
  if (mesh.geometry) {
    mesh.geometry.dispose();
  }
}
```

---

## needsUpdate Flag

ALWAYS set `material.needsUpdate = true` after changing these at runtime:
- Toggling `flatShading`
- Changing `side` (FrontSide/BackSide/DoubleSide)
- Adding or removing a texture map (e.g., setting `map` from `null` to a texture)
- Changing `transparent` or `alphaTest`
- Toggling `wireframe`
- Any property that changes the compiled shader variant

NEVER set `needsUpdate = true` every frame -- it forces expensive shader recompilation. ONLY set it once after the property change.

For textures: set `texture.needsUpdate = true` after modifying `texture.image` data to trigger GPU re-upload.

---

## Toon Material Special Rule

When using `MeshToonMaterial`, ALWAYS set `gradientMap.minFilter = NearestFilter` and `gradientMap.magFilter = NearestFilter`. Linear filtering blurs the discrete shading steps into smooth gradients, defeating the toon effect.

---

## Reference Links

- [references/methods.md](references/methods.md) -- All material types with constructor signatures and key properties
- [references/examples.md](references/examples.md) -- Complete working examples (PBR, textures, multi-material)
- [references/anti-patterns.md](references/anti-patterns.md) -- What NOT to do, with explanations

### Official Sources

- https://threejs.org/docs/#api/en/materials/Material
- https://threejs.org/docs/#api/en/materials/MeshStandardMaterial
- https://threejs.org/docs/#api/en/materials/MeshPhysicalMaterial
- https://threejs.org/docs/#api/en/textures/Texture
````

### `atelier/.claude/skills/threejs-syntax-materials/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-syntax-shaders/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-syntax-shaders
description: >
  Use when writing custom GLSL shaders, creating ShaderMaterial or
  RawShaderMaterial, defining uniforms, or patching built-in materials
  with onBeforeCompile. Prevents the common mistake of wrong uniform
  format, missing needsUpdate on uniforms, or not including required
  defines. Covers ShaderMaterial, RawShaderMaterial, GLSL, uniforms,
  ShaderChunk, onBeforeCompile, defines, GLSL3.
  Keywords: ShaderMaterial, RawShaderMaterial, GLSL, vertex shader, fragment shader, uniform, varying, ShaderChunk, onBeforeCompile, custom shader, write shader, custom visual effect, GPU programming.
license: MIT
compatibility: "Designed for Claude Code. Requires Three.js r160+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# threejs-syntax-shaders

## Quick Reference

### ShaderMaterial vs RawShaderMaterial

| Aspect | ShaderMaterial | RawShaderMaterial |
|--------|----------------|-------------------|
| Built-in uniforms | Automatically injected | NONE -- you MUST declare everything |
| Built-in attributes | Automatically declared | NONE -- you MUST declare everything |
| `#include <chunk>` | Supported | NOT supported |
| Precision declaration | Automatic | You MUST add `precision mediump float;` |
| Use case | Extend Three.js rendering | Full shader control, porting external shaders |
| Performance | Slight overhead from unused built-ins | Minimal shader overhead |

### Uniform Type Map

| GLSL Type | JavaScript Value |
|-----------|-----------------|
| `float` | `{ value: 1.0 }` |
| `int` | `{ value: 1 }` |
| `bool` | `{ value: true }` |
| `vec2` | `{ value: new THREE.Vector2() }` |
| `vec3` | `{ value: new THREE.Vector3() }` or `{ value: new THREE.Color() }` |
| `vec4` | `{ value: new THREE.Vector4() }` |
| `mat3` | `{ value: new THREE.Matrix3() }` |
| `mat4` | `{ value: new THREE.Matrix4() }` |
| `sampler2D` | `{ value: texture }` (a `THREE.Texture` instance) |
| `samplerCube` | `{ value: cubeTexture }` |
| `float[]` | `{ value: [1.0, 2.0, 3.0] }` |
| `vec3[]` | `{ value: [new THREE.Vector3(), ...] }` |

### Critical Warnings

**NEVER** pass a bare value as a uniform -- ALWAYS wrap it in `{ value: ... }`. Writing `uniforms: { uTime: 0.0 }` silently fails; ALWAYS write `uniforms: { uTime: { value: 0.0 } }`.

**NEVER** declare built-in uniforms or attributes in a `ShaderMaterial` shader -- Three.js injects them automatically. Redeclaring causes a GLSL compilation error.

**ALWAYS** declare ALL uniforms, attributes, and precision in `RawShaderMaterial` shaders -- nothing is injected for you.

**NEVER** use `gl_FragColor` or `texture2D()` when `glslVersion` is `THREE.GLSL3` -- use a declared `out vec4` variable and `texture()` instead.

**ALWAYS** call `material.needsUpdate = true` after changing `defines` -- defines are compiled into the shader, so changes require recompilation.

---

## ShaderMaterial

### Constructor

```javascript
import * as THREE from 'three';

const material = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0.0 },
    uColor: { value: new THREE.Color(0x00ff00) },
    uTexture: { value: someTexture },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform vec3 uColor;
    varying vec2 vUv;
    void main() {
      gl_FragColor = vec4(uColor * vUv.x, 1.0);
    }
  `,
  transparent: false,
  wireframe: false,
  side: THREE.FrontSide,
});
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `uniforms` | `Object` | `{}` | `{ name: { value: ... } }` format |
| `uniformsGroups` | `Array` | `[]` | Uniform buffer objects (UBO) |
| `vertexShader` | `string` | -- | GLSL vertex shader source |
| `fragmentShader` | `string` | -- | GLSL fragment shader source |
| `defines` | `Object` | `{}` | Preprocessor `#define` directives |
| `extensions` | `Object` | `{}` | GLSL extensions to enable |
| `wireframe` | `boolean` | `false` | Wireframe rendering |
| `lights` | `boolean` | `false` | Pass light uniforms to shader |
| `fog` | `boolean` | `false` | Pass fog uniforms to shader |
| `clipping` | `boolean` | `false` | Enable clipping planes |
| `glslVersion` | `string \| null` | `null` | `null` for GLSL1, `THREE.GLSL3` for GLSL 3.0 ES |
| `defaultAttributeValues` | `Object` | -- | Fallback values for missing attributes |

---

## Built-in Uniforms (ShaderMaterial Only)

These are injected automatically. NEVER declare them yourself.

```glsl
// Transform matrices
uniform mat4 modelMatrix;           // Object -> World
uniform mat4 modelViewMatrix;       // Object -> Camera
uniform mat4 projectionMatrix;      // Camera -> Clip
uniform mat4 viewMatrix;            // World -> Camera
uniform mat3 normalMatrix;          // Transpose inverse of modelViewMatrix

// Camera
uniform vec3 cameraPosition;        // Camera world position

// When lights: true
uniform vec3 ambientLightColor;
// Plus structured arrays for directional, point, spot, hemisphere lights
```

## Built-in Attributes (ShaderMaterial Only)

These are injected automatically. NEVER declare them yourself.

```glsl
attribute vec3 position;    // Vertex position
attribute vec3 normal;      // Vertex normal
attribute vec2 uv;          // Primary UV coordinates
attribute vec2 uv2;         // Secondary UV (for aoMap, lightMap)
attribute vec4 tangent;     // Tangent vector (if computeTangents was called)
attribute vec3 color;       // Vertex color (if geometry has color attribute)
```

---

## RawShaderMaterial

Use when you need full control over the shader source. NOTHING is injected.

```javascript
const material = new THREE.RawShaderMaterial({
  uniforms: {
    uModelViewMatrix: { value: new THREE.Matrix4() },
    uProjectionMatrix: { value: new THREE.Matrix4() },
  },
  vertexShader: `
    precision highp float;
    attribute vec3 position;
    uniform mat4 uModelViewMatrix;
    uniform mat4 uProjectionMatrix;
    void main() {
      gl_Position = uProjectionMatrix * uModelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    precision highp float;
    void main() {
      gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
  `,
});
```

**ALWAYS** add `precision highp float;` (or `mediump`) at the top of both shaders in `RawShaderMaterial`. Omitting precision causes a GLSL compilation error on mobile and some desktop drivers.

---

## ShaderChunk -- Reusing Three.js Shader Code

`THREE.ShaderChunk` contains all internal shader fragments. Use `#include <chunk_name>` in `ShaderMaterial` (NOT `RawShaderMaterial`).

### Common Chunks

| Chunk | Purpose |
|-------|---------|
| `<common>` | Shared constants and functions (PI, saturate, etc.) |
| `<fog_pars_vertex>` / `<fog_vertex>` | Fog support (vertex) |
| `<fog_pars_fragment>` / `<fog_fragment>` | Fog support (fragment) |
| `<shadowmap_pars_vertex>` / `<shadowmap_vertex>` | Shadow support (vertex) |
| `<shadowmap_pars_fragment>` / `<shadowmap_fragment>` | Shadow support (fragment) |
| `<lights_pars_begin>` | Light structure declarations |
| `<begin_vertex>` | Initializes `transformed` variable from `position` |
| `<project_vertex>` | Applies modelViewMatrix and projectionMatrix |
| `<normal_fragment_begin>` | Normal mapping setup |
| `<color_pars_vertex>` / `<color_vertex>` | Vertex color support |

### Accessing Chunks Programmatically

```javascript
// Read the source of any chunk
console.log(THREE.ShaderChunk.common);
console.log(THREE.ShaderChunk.fog_pars_vertex);
```

---

## onBeforeCompile -- Patching Built-in Materials

Modify an existing material's shader at compile time. This preserves PBR lighting, shadows, and all built-in features.

```javascript
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });

material.onBeforeCompile = (shader) => {
  shader.uniforms.uTime = { value: 0.0 };

  shader.vertexShader = shader.vertexShader.replace(
    '#include <begin_vertex>',
    `
    #include <begin_vertex>
    transformed.y += sin(transformed.x * 5.0 + uTime) * 0.5;
    `
  );

  // Store reference for uniform updates
  material.userData.shader = shader;
};

// ALWAYS override customProgramCacheKey when using onBeforeCompile
material.customProgramCacheKey = () => 'my-wavy-material';

// In animation loop
if (material.userData.shader) {
  material.userData.shader.uniforms.uTime.value = clock.getElapsedTime();
}
```

**ALWAYS** override `customProgramCacheKey()` when using `onBeforeCompile` -- without it, Three.js may reuse a cached unpatched shader program, causing your modifications to silently disappear.

**ALWAYS** check `material.userData.shader` exists before accessing uniforms -- the shader object is created lazily on first render and can be recreated when `material.needsUpdate = true`.

---

## Defines -- Preprocessor Directives

```javascript
const material = new THREE.ShaderMaterial({
  defines: {
    USE_FOG: '',           // #define USE_FOG
    MAX_LIGHTS: 4,         // #define MAX_LIGHTS 4
    EPSILON: '0.001',      // #define EPSILON 0.001
  },
  // ...shaders
});
```

Changing defines at runtime:

```javascript
material.defines.MAX_LIGHTS = 8;
material.needsUpdate = true;  // REQUIRED -- triggers recompilation
```

---

## GLSL3 Mode

```javascript
const material = new THREE.ShaderMaterial({
  glslVersion: THREE.GLSL3,
  vertexShader: `
    in vec3 position;           // 'attribute' becomes 'in'
    uniform mat4 modelViewMatrix;
    uniform mat4 projectionMatrix;
    out vec3 vPosition;         // 'varying' becomes 'out'

    void main() {
      vPosition = position;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    precision highp float;
    in vec3 vPosition;          // 'varying' becomes 'in'
    out vec4 fragColor;         // replaces gl_FragColor

    void main() {
      fragColor = vec4(vPosition * 0.5 + 0.5, 1.0);
    }
  `,
});
```

### GLSL1 vs GLSL3 Syntax

| GLSL1 | GLSL3 | Context |
|-------|-------|---------|
| `attribute` | `in` | Vertex shader inputs |
| `varying` (vertex) | `out` | Vertex shader outputs |
| `varying` (fragment) | `in` | Fragment shader inputs |
| `gl_FragColor` | Declared `out vec4` | Fragment shader output |
| `texture2D()` | `texture()` | Texture sampling |
| `textureCube()` | `texture()` | Cube texture sampling |

---

## Uniform Update Pattern

```javascript
// At creation
const material = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0.0 },
    uResolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
    uMouse: { value: new THREE.Vector2() },
  },
  vertexShader: '...',
  fragmentShader: '...',
});

// In animation loop -- update the .value property directly
function animate() {
  material.uniforms.uTime.value = performance.now() / 1000;
  material.uniforms.uMouse.value.set(mouseX, mouseY);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

**NEVER** replace the uniform object itself (e.g., `material.uniforms.uTime = { value: 5 }`). ALWAYS mutate the existing `.value` property. Replacing the object breaks the internal reference.

---

## Reference Links

- [references/methods.md](references/methods.md) -- Complete API signatures
- [references/examples.md](references/examples.md) -- Working code examples
- [references/anti-patterns.md](references/anti-patterns.md) -- What NOT to do

### Official Sources

- https://threejs.org/docs/#api/en/materials/ShaderMaterial
- https://threejs.org/docs/#api/en/materials/RawShaderMaterial
- https://threejs.org/docs/#api/en/renderers/shaders/ShaderChunk
- https://threejs.org/docs/#api/en/renderers/shaders/UniformsLib
````

### `atelier/.claude/skills/threejs-syntax-shaders/ (altri 4 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, references/anti-patterns.md, references/examples.md, references/methods.md

### `atelier/.claude/skills/threejs-webgl/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: threejs-webgl
description: Comprehensive skill for Three.js 3D web development. Use this skill when building interactive 3D scenes, WebGL/WebGPU applications, product configurators, 3D visualizations, or immersive web experiences. Triggers on tasks involving Three.js, 3D rendering, scenes, cameras, meshes, materials, lights, animations, textures, or WebGL/WebGPU rendering.
---

# Three.js WebGL/WebGPU Development

## Overview

Three.js is the industry-standard JavaScript library for creating 3D graphics in web browsers using WebGL and WebGPU. This skill provides comprehensive guidance for building performant, interactive 3D experiences including scenes, cameras, renderers, geometries, materials, lights, textures, and animations.

## Core Concepts

### Scene Graph Architecture

Three.js uses a hierarchical scene graph where all 3D objects are organized in a tree structure:

```javascript
Scene
├── Camera
├── Lights
│   ├── AmbientLight
│   ├── DirectionalLight
│   └── PointLight
├── Meshes
│   ├── Mesh (Geometry + Material)
│   └── InstancedMesh
└── Groups
```

### Essential Components

Every Three.js application requires these core elements:

1. **Scene**: Container for all 3D objects
2. **Camera**: Defines the viewing perspective
3. **Renderer**: Draws the scene to canvas (WebGL or WebGPU)
4. **Geometry**: Defines the shape of objects
5. **Material**: Defines the surface appearance
6. **Mesh**: Combines geometry and material

## Quick Start Pattern

### Basic Scene Setup

```javascript
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// Scene, Camera, Renderer
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x333333);

const camera = new THREE.PerspectiveCamera(
  75, // FOV
  window.innerWidth / window.innerHeight, // Aspect ratio
  0.1, // Near clipping plane
  1000 // Far clipping plane
);
camera.position.set(0, 2, 5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 7.5);
directionalLight.castShadow = true;
scene.add(directionalLight);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Animation Loop
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

animate();

// Handle Resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

### WebGPU Setup (Modern Alternative)

```javascript
import * as THREE from 'three/webgpu';

const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setAnimationLoop(animate);
renderer.toneMapping = THREE.LinearToneMapping;
renderer.toneMappingExposure = 1;
document.body.appendChild(renderer.domElement);
```

## Common Patterns

### 1. Creating Meshes with Materials

```javascript
// Basic Mesh
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({
  color: 0x00ff00,
  roughness: 0.5,
  metalness: 0.5
});
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// Textured Mesh
const loader = new THREE.TextureLoader();
const texture = loader.load('texture.jpg');
texture.colorSpace = THREE.SRGBColorSpace;

const texturedMaterial = new THREE.MeshStandardMaterial({
  map: texture
});
const mesh = new THREE.Mesh(geometry, texturedMaterial);
scene.add(mesh);
```

### 2. Lighting Strategies

```javascript
// Three-Point Lighting Setup
function setupThreePointLight(scene) {
  // Key Light (Main)
  const keyLight = new THREE.DirectionalLight(0xffffff, 3);
  keyLight.position.set(5, 10, 7.5);
  keyLight.castShadow = true;
  scene.add(keyLight);

  // Fill Light (Softens shadows)
  const fillLight = new THREE.DirectionalLight(0xffffff, 1);
  fillLight.position.set(-5, 5, -5);
  scene.add(fillLight);

  // Rim Light (Edge definition)
  const rimLight = new THREE.DirectionalLight(0xffffff, 0.5);
  rimLight.position.set(0, 5, -10);
  scene.add(rimLight);

  // Ambient (Base illumination)
  const ambient = new THREE.AmbientLight(0x404040, 0.5);
  scene.add(ambient);
}

// Physical Light (Realistic)
const bulbLight = new THREE.PointLight(0xffee88, 1, 100, 2);
bulbLight.power = 1700; // Lumens (100W bulb equivalent)
bulbLight.castShadow = true;
scene.add(bulbLight);

// Hemisphere Light (Sky + Ground)
const hemiLight = new THREE.HemisphereLight(
  0xddeeff, // Sky color
  0x0f0e0d, // Ground color
  0.02
);
scene.add(hemiLight);
```

### 3. Instanced Geometry (Performance)

```javascript
// For rendering thousands of similar objects efficiently
const geometry = new THREE.SphereGeometry(0.1, 16, 16);
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
const instancedMesh = new THREE.InstancedMesh(geometry, material, 1000);

const matrix = new THREE.Matrix4();
const color = new THREE.Color();

for (let i = 0; i < 1000; i++) {
  matrix.setPosition(
    Math.random() * 10 - 5,
    Math.random() * 10 - 5,
    Math.random() * 10 - 5
  );
  instancedMesh.setMatrixAt(i, matrix);
  instancedMesh.setColorAt(i, color.setHex(Math.random() * 0xffffff));
}

instancedMesh.instanceMatrix.needsUpdate = true;
scene.add(instancedMesh);
```

### 4. Loading 3D Models (glTF)

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

// Setup loaders
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/');

const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);

// Load model
gltfLoader.load('model.glb', (gltf) => {
  const model = gltf.scene;

  // Enable shadows
  model.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });

  scene.add(model);

  // Handle animations
  if (gltf.animations.length > 0) {
    const mixer = new THREE.AnimationMixer(model);
    const action = mixer.clipAction(gltf.animations[0]);
    action.play();

    // In animation loop:
    // mixer.update(deltaTime);
  }
});
```

### 5. Shadow Configuration

```javascript
// Enable shadows on renderer
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap; // or VSMShadowMap

// Configure light shadows
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
directionalLight.shadow.camera.near = 0.5;
directionalLight.shadow.camera.far = 50;
directionalLight.shadow.camera.left = -10;
directionalLight.shadow.camera.right = 10;
directionalLight.shadow.camera.top = 10;
directionalLight.shadow.camera.bottom = -10;
directionalLight.shadow.radius = 4;
directionalLight.shadow.blurSamples = 8;

// Objects casting/receiving shadows
mesh.castShadow = true;
mesh.receiveShadow = true;
```

### 6. Raycasting (Interaction)

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function onMouseClick(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(scene.children, true);

  if (intersects.length > 0) {
    const object = intersects[0].object;
    object.material.color.set(0xff0000);
  }
}

window.addEventListener('click', onMouseClick);
```

## Integration Patterns

### With GSAP for Animation

```javascript
import gsap from 'gsap';

// Animate camera
gsap.to(camera.position, {
  x: 5,
  y: 3,
  z: 10,
  duration: 2,
  ease: "power2.inOut",
  onUpdate: () => {
    camera.lookAt(scene.position);
  }
});

// Animate mesh properties
gsap.to(mesh.rotation, {
  y: Math.PI * 2,
  duration: 3,
  repeat: -1,
  ease: "none"
});
```

### With React (see react-three-fiber skill)

```javascript
// Three.js integrates naturally with React Three Fiber
// Use the react-three-fiber skill for React integration patterns
```

### With Post-Processing

```javascript
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  1.5, // strength
  0.4, // radius
  0.85 // threshold
);
composer.addPass(bloomPass);

// In animation loop:
composer.render();
```

## Performance Optimization

### 1. Geometry Reuse
```javascript
// Bad: Creates new geometry for each mesh
for (let i = 0; i < 100; i++) {
  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);
}

// Good: Reuse geometry
const sharedGeometry = new THREE.BoxGeometry(1, 1, 1);
for (let i = 0; i < 100; i++) {
  const mesh = new THREE.Mesh(sharedGeometry, material);
  scene.add(mesh);
}
```

### 2. Use InstancedMesh for Repeated Objects
For hundreds/thousands of identical objects, use `InstancedMesh` (see pattern above).

### 3. Texture Optimization
```javascript
// Compress textures
texture.generateMipmaps = true;
texture.minFilter = THREE.LinearMipmapLinearFilter;
texture.magFilter = THREE.LinearFilter;

// Use power-of-two dimensions (512, 1024, 2048)
// Consider texture atlases for multiple small textures
```

### 4. Level of Detail (LOD)
```javascript
const lod = new THREE.LOD();
lod.addLevel(highDetailMesh, 0);    // 0-50 units
lod.addLevel(mediumDetailMesh, 50);  // 50-100 units
lod.addLevel(lowDetailMesh, 100);    // 100+ units
scene.add(lod);
```

### 5. Frustum Culling
Three.js automatically culls objects outside the camera's view. Ensure objects have correct bounding spheres:

```javascript
mesh.geometry.computeBoundingSphere();
```

### 6. Dispose Resources
```javascript
function disposeScene() {
  scene.traverse((object) => {
    if (object.geometry) object.geometry.dispose();
    if (object.material) {
      if (Array.isArray(object.material)) {
        object.material.forEach(material => material.dispose());
      } else {
        object.material.dispose();
      }
    }
  });
  renderer.dispose();
}
```

## Best Practices

### 1. Use Animation Clocks for Consistent Timing
```javascript
const clock = new THREE.Clock();

function animate() {
  const deltaTime = clock.getDelta();
  const elapsedTime = clock.getElapsedTime();

  // Use deltaTime for frame-independent animations
  mesh.rotation.y += deltaTime * Math.PI * 0.5; // 90° per second

  renderer.render(scene, camera);
}
```

### 2. Camera Setup Guidelines
- **FOV**: 45-75° for most applications
- **Near plane**: As far as possible (avoid z-fighting)
- **Far plane**: As close as possible (precision)
- **Aspect ratio**: Always match canvas dimensions

### 3. Material Selection
- **MeshBasicMaterial**: Unlit, flat colors (debugging, UI)
- **MeshLambertMaterial**: Cheap diffuse lighting (mobile)
- **MeshPhongMaterial**: Specular highlights (older standard)
- **MeshStandardMaterial**: PBR, realistic (recommended)
- **MeshPhysicalMaterial**: Advanced PBR (clearcoat, transmission)

### 4. Coordinate System
- Three.js uses right-handed coordinate system
- +Y is up, +Z is toward camera, +X is right
- Rotations use radians (Math.PI = 180°)

### 5. Scene Organization
```javascript
// Group related objects
const building = new THREE.Group();
building.add(walls, roof, windows);
scene.add(building);

// Use meaningful names
mesh.name = 'player-character';
const found = scene.getObjectByName('player-character');
```

## Common Pitfalls

### 1. Not Updating Aspect Ratio on Resize
Always update camera aspect ratio and projection matrix when window resizes.

### 2. Creating New Objects in Animation Loop
```javascript
// Bad: Memory leak
function animate() {
  const geometry = new THREE.BoxGeometry(); // Created every frame!
  // ...
}

// Good: Create once outside loop
const geometry = new THREE.BoxGeometry();
function animate() {
  // Reuse geometry
}
```

### 3. Forgetting to Enable Shadows
Remember to enable shadows on renderer, lights, and objects.

### 4. Z-Fighting (Flickering)
- Increase near plane distance
- Decrease far plane distance
- Avoid overlapping coplanar surfaces
- Use `material.polygonOffset = true` with `material.polygonOffsetFactor`

### 5. Color Space Issues
```javascript
// Always set color space for textures
texture.colorSpace = THREE.SRGBColorSpace;

// Set renderer output encoding
renderer.outputColorSpace = THREE.SRGBColorSpace;
```

### 6. Not Disposing Resources
Always call `.dispose()` on geometries, materials, textures, and renderers when no longer needed.

## Resources

This skill includes bundled resources to accelerate Three.js development:

### references/
- `api_reference.md`: Quick API reference for core classes (Scene, Camera, Renderer, etc.)
- `materials_guide.md`: Comprehensive material types and properties
- `optimization_checklist.md`: Performance optimization strategies

### scripts/
- `setup_scene.py`: Generate boilerplate Three.js scene setup code
- `texture_optimizer.py`: Batch optimize textures for web (resize, compress)
- `gltf_validator.py`: Validate glTF models before use

### assets/
- `starter_scene/`: Complete HTML/JS boilerplate project
- `shaders/`: Custom GLSL shader examples (vertex, fragment)
- `hdri/`: Environment maps for PBR lighting
- `draco/`: DRACO decoder for compressed models

## Advanced Topics

### Custom Shaders (GLSL)
```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0.0 },
    uColor: { value: new THREE.Color(0x00ff00) }
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform vec3 uColor;
    varying vec2 vUv;
    void main() {
      gl_FragColor = vec4(uColor * vUv.x, 1.0);
    }
  `
});
```

### Render Targets (Render-to-Texture)
```javascript
const renderTarget = new THREE.WebGLRenderTarget(512, 512);

// Render scene to texture
renderer.setRenderTarget(renderTarget);
renderer.render(scene, camera);
renderer.setRenderTarget(null);

// Use texture
const material = new THREE.MeshBasicMaterial({
  map: renderTarget.texture
});
```

### GPU Computation (GPGPU)
Use `GPUComputationRenderer` for particle simulations, cloth physics, etc.

## When to Use This Skill

Use this skill when:
- Building interactive 3D web experiences
- Creating product configurators or visualizers
- Implementing WebGL/WebGPU rendering
- Working with 3D models, scenes, or animations
- Optimizing Three.js performance
- Integrating Three.js with other libraries (GSAP, React, etc.)
- Debugging Three.js rendering issues

For React integration, use the **react-three-fiber** skill.
For animation, combine with the **gsap-scrolltrigger** skill.
For UI animations, use the **motion-framer** skill.
````

### `atelier/.claude/skills/threejs-webgl/ (altri 8 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE, assets/starter_scene/README.md, assets/starter_scene/index.html, assets/starter_scene/main.js, references/api_reference.md, references/materials_guide.md, references/optimization_checklist.md, scripts/setup_scene.py

### `atelier/.claude/skills/webapp-testing/SKILL.md`

Origine: ramo ccr-e70de148-ie85hq.

````markdown
---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Use `--help` to see usage, then invoke directly. 
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation
````

### `atelier/.claude/skills/webapp-testing/ (altri 5 file)`

Origine: ramo ccr-e70de148-ie85hq.

> File di supporto (riferimenti, script, licenze, esempi) di una skill di grafica web di terze parti, non legata ai libri; non copiati per dimensione. Elenco: LICENSE.txt, examples/console_logging.py, examples/element_discovery.py, examples/static_html_automation.py, scripts/with_server.py


---

## 7. Programmi, stampa e prove

### `motore/zb`

```python
#!/usr/bin/env python3
"""zb — comandi del motore editoriale (proposta B.4). Uso: python3 motore/zb <comando> [argomenti]

Il libro è sempre un percorso: zb <comando> <libro> [argomenti] (oppure ZB_LIBRO=<libro>).
Ogni comando lancia lo script di motore/script/ con python3 -B e ne restituisce il codice d'uscita.
Elenco completo: python3 motore/zb aiuto
"""
import filecmp
import os
import subprocess
import sys

sys.dont_write_bytecode = True
MOTORE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(MOTORE, 'script')

SCRIPT = {
    'nuovo': 'nuovo.py', 'adotta': 'adotta.py', 'pulizia': 'pulizia.py', 'avvio': 'avvio.py', 'revisione': 'revisione.py',
    'capitolo': 'capitolo.py', 'conta': 'conta.py', 'stile': 'stile.py', 'continuita': 'continuita.py',
    'riciclo': 'riciclo.py', 'compila': 'compila.py', 'impagina': 'impagina.py', 'pdf': 'verifica_pdf.py',
    'kdp': 'conformita_kdp.py', 'pacchetto': 'pacchetto.py', 'prove': 'prove.py',
    'separazione': 'separazione.py', 'recinto': 'recinto.py', 'profili': 'valida_profili.py',
    'ortografia': 'ortografia.py', 'push': 'push.py', 'voce': 'voce.py',
}
FASE = ('stato', 'ok', 'avanti', 'correggi', 'riapprova', 'pronto', 'esito', 'fase')
AIUTO = """Comandi (il libro è sempre un percorso):
  zb nuovo <briefing>              crea il libro dal briefing
  zb adotta <cartella>             bozze di libro.yaml, stato, cronologia, nomi da documenti esistenti
  zb avvio <libro>                 avvio obbligatorio: controlli e riga «Letto: …»
  zb stato <libro>                 stato del libro (non scrive)
  zb pronto <libro>                fine del lavoro di una fase: apre il gate o passa oltre
  zb avanti <libro>                blocco successivo dei documenti del gate
  zb ok <libro> [lotti da N]       approva il gate aperto
  zb correggi <libro> <istruzione> registra una correzione; il gate resta aperto
  zb correggi <libro> <unità>: <motivo> [--commit H]   fuori dal gate: registra data, file, motivo, sha256 precedente
  zb esito <libro> <N>             controlli del capitolo N e registrazione dell'esito
  zb riapprova <libro> <documento> <motivo>   modifica autorizzata a un documento già approvato
  zb fase <libro> stesura --motivo "<testo>"   da «chiusura» a «stesura» se nel piano mancano unità
  zb revisione <libro> <documento|gate> [N]   blocco N di un documento (non scrive)
  zb capitolo|conta|stile|continuita|riciclo|compila|impagina|pdf|kdp|pacchetto <libro>
  zb verifica KDP fatta [AAAA-MM-GG] | zb verifica KDP stato | zb verifica KDP controlla
  zb hook stato | zb hook attiva [--ok] | zb hook disattiva
  zb lavoro stato | zb lavoro motore | zb lavoro libro <slug>   recinto dell'hook (libro attivo o motore)
  zb pulizia <libro> [--applica]   elenco di temporanei, vuote e copie; cancella solo con --applica
  zb voce lista | zb voce mostra <slug> [N] | zb voce verifica <slug>   banca-voci (ZB_BANCA_VOCI)
  zb push [--tentativi 4] [--attesa 2]   push del ramo corrente; poi ramo alternativo, poi git bundle
  zb prove | zb separazione | zb recinto | zb profili"""


def lancia(script, args):
    p = os.path.join(S, script)
    if not os.path.isfile(p):
        print(f'FERMO: {script} non esiste ancora nel motore.', file=sys.stderr)
        return 2
    return subprocess.run([sys.executable, '-B', p, *args]).returncode


def progetto(args):
    if '--progetto' in args:
        return os.path.realpath(args[args.index('--progetto') + 1])
    r = subprocess.run(['git', '-C', MOTORE, 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    return r.stdout.strip() or os.path.dirname(MOTORE)


def hook(args):
    esempio = os.path.join(MOTORE, 'dati', 'hook-settings.esempio.json')
    dest = os.path.join(progetto(args), '.claude', 'settings.json')
    azione = args[0] if args else 'stato'
    nostro = os.path.isfile(dest) and filecmp.cmp(dest, esempio, shallow=False)
    if azione == 'stato':
        mod = next((r.split(':', 1)[1].split('#')[0].strip() for r in open(os.path.join(MOTORE, 'dati', 'hook.yaml'),
                    encoding='utf-8') if r.startswith('modalita:')), 'avviso')
        print(f'Modalità (dati/hook.yaml): {mod}')
        print(f'{dest}: ' + ('attivo (configurazione del motore)' if nostro else
                             'presente ma diverso dal modello del motore' if os.path.isfile(dest) else 'assente: hook non attivi'))
        return 0
    if azione == 'attiva':
        if nostro:
            print(f'Già attivo: {dest}')
            return 0
        if os.path.exists(dest):
            print(f'FERMO: {dest} esiste già con un contenuto diverso; non lo sovrascrivo.', file=sys.stderr)
            return 2
        if '--ok' not in args:
            print(f'Creerei {dest} con questo contenuto (da {os.path.relpath(esempio, os.path.dirname(MOTORE))}):\n')
            print(open(esempio, encoding='utf-8').read())
            print('Vale per ogni sessione su questo ramo e su ogni ramo in cui venga unito.\n'
                  'Per confermare, dopo l\'«ok» dell\'autore: zb hook attiva --ok')
            return 0
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(esempio, encoding='utf-8') as f, open(dest, 'w', encoding='utf-8') as g:
            g.write(f.read())
        print(f'Creato {dest}. Gli hook valgono dalla prossima sessione. Salvalo con un commit a parte.')
        return 0
    if azione == 'disattiva':
        if not os.path.exists(dest):
            print(f'Niente da fare: {dest} non esiste.')
            return 0
        if not nostro:
            print(f'FERMO: {dest} non è quello del motore; non lo tolgo.', file=sys.stderr)
            return 2
        os.remove(dest)
        try:
            os.rmdir(os.path.dirname(dest))
        except OSError:
            pass
        print(f'Tolto {dest}. Salva la rimozione con un commit.')
        return 0
    print('Uso: zb hook stato | attiva [--ok] | disattiva', file=sys.stderr)
    return 2


def main(argv):
    if not argv or argv[0] in ('aiuto', '-h', '--help'):
        print(AIUTO)
        return 0
    cmd, args = argv[0], argv[1:]
    if cmd in FASE:
        if not args and os.environ.get('ZB_LIBRO'):
            args = [os.environ['ZB_LIBRO']]
        if not args:
            print(f'Uso: zb {cmd} <libro> …', file=sys.stderr)
            return 2
        return lancia('fase.py', [args[0], cmd, *args[1:]])
    if cmd == 'verifica':
        resto = [a for a in args if a.upper() != 'KDP']
        return lancia('kdp_verifica.py', resto)
    if cmd == 'hook':
        return hook(args)
    if cmd == 'lavoro':
        return lancia('hook_recinto.py', ['lavoro', *args])
    if cmd in SCRIPT:
        if cmd in ('avvio',) and not args and os.environ.get('ZB_LIBRO'):
            args = [os.environ['ZB_LIBRO']]
        return lancia(SCRIPT[cmd], args)
    print(f'Comando sconosciuto: {cmd}\n\n{AIUTO}', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
```

### `motore/script/adotta.py`

```python
"""Adotta nel motore un libro già avviato (passo 5b).

Uso: python3 -B adotta.py <cartella-del-libro> [--titolo «titolo»]
Per un libro con alcuni documenti già scritti (briefing, manuale di stile, bibbia, scaletta,
piano parole, cronologia) genera in BOZZA libro.yaml, stato.yaml, cronologia.yaml e
nomi_propri.txt, ricavando i valori dai documenti e dal profilo di genere.
- Ogni valore ha la sua fonte (file e riga) in 06-diagnostica/adozione.md.
- Se un documento diverge dal profilo, il valore va in libro.yaml come override con motivo.
- Non sovrascrive mai un file esistente; scrive solo nella cartella indicata.
- In adozione.md elenca ciò che non ha potuto ricavare.
- Se il titolo non si ricava dai documenti si ferma senza scrivere nulla e lo chiede (--titolo).
- Si ferma alla fase «documenti»: apre il gate se tutti i documenti ci sono, altrimenti dice cosa manca.
Riconosce le righe nel formato dei documenti del motore (vedi PROCEDURA.md, «zb adotta»).
"""
import datetime
import os
import re
import sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import nuovo  # noqa: E402
import revisione  # noqa: E402

DOC = {'briefing': '00-progetto/briefing.md', 'manuale': '03-architettura/manuale-di-stile.md',
       'bibbia': '02-bibbia/bibbia.md', 'scaletta': '03-architettura/scaletta.md',
       'piano': '03-architettura/piano-parole.md', 'cronologia': 'cronologia.yaml'}
GENERATI = ['libro.yaml', 'stato.yaml', 'cronologia.yaml', 'nomi_propri.txt', '06-diagnostica/adozione.md']
DATA = r'(\d{4}-\d{2}-\d{2})'


class Raccolta:
    """Valori ricavati con la loro fonte, e voci non ricavate."""

    def __init__(self, cartella):
        self.cartella = cartella
        self.fonti, self.mancano = [], []
        self.righe = {}
        for k, rel in DOC.items():
            p = os.path.join(cartella, rel)
            self.righe[k] = open(p, encoding='utf-8').read().splitlines() if os.path.isfile(p) else None

    def cerca(self, doc, regex, flags=re.I):
        for n, r in enumerate(self.righe.get(doc) or [], 1):
            m = re.search(regex, r, flags)
            if m:
                return m, f'{DOC[doc]}:{n}'
        return None, None

    def primo(self, campo, prove):
        """prove: [(doc, regex, funzione)]; il primo che trova vince."""
        for doc, regex, f in prove:
            m, fonte = self.cerca(doc, regex)
            if m:
                v = f(m)
                self.fonti.append((campo, v, fonte))
                return v
        self.mancano.append(campo)
        return None

    def tutti(self, doc, regex):
        out = []
        for n, r in enumerate(self.righe.get(doc) or [], 1):
            for m in re.finditer(regex, r):
                out.append((m, f'{DOC[doc]}:{n}'))
        return out


def ricava(cartella, titolo_dato=None):
    R = Raccolta(cartella)
    presenti = [k for k in DOC if R.righe[k] is not None]
    if not presenti:
        raise comune.ErroreMotore(f'Nessun documento da adottare in {cartella} (cerco: {", ".join(DOC.values())})')
    g1 = lambda m: m.group(1).strip()
    titolo = R.primo('titolo', [('briefing', r'^Titolo di lavoro:\s*(\S.*)$', g1),
                                ('manuale', r'^#\s*Manuale di stile\s*—\s*(.+)$', g1),
                                ('bibbia', r'^#\s*Bibbia\s*—\s*(.+)$', g1),
                                ('scaletta', r'^#\s*Scaletta\s*—\s*(.+)$', g1)])
    if titolo is None and titolo_dato:
        R.mancano.remove('titolo')
        titolo = titolo_dato
        R.fonti.append(('titolo', titolo, 'indicato con --titolo'))
    autore = R.primo('autore', [('briefing', r'^Autore:\s*(\S.*)$', g1), ('manuale', r'^Autore:\s*(\S.*)$', g1)])
    genere = R.primo('profilo', [('briefing', r'^Genere:\s*([\w-]+)', g1), ('manuale', r'^Genere:\s*([\w-]+)', g1),
                                 ('manuale', r'profilo «([\w-]+)»', g1)])
    if genere and not os.path.isfile(os.path.join(comune.radice_motore(), 'profili', f'{genere}.yaml')):
        R.mancano.append(f'profilo («{genere}» non esiste in motore/profili/)')
        genere = None
    numero = lambda m: int(re.sub(r'\D', '', m.group(1)))
    target = R.primo('parole.target_totale', [('briefing', r'^Lunghezza[^:]*:\s*([\d.]+)', numero),
                                              ('manuale', r'Obiettivo:\s*([\d.]+)\s*parole', numero),
                                              ('piano', r'^Totale:\s*([\d.]+)', numero)])
    originale = os.path.join(cartella, '01-originale')
    precedenti = sorted(f for f in os.listdir(originale) if f.endswith('.md')) if os.path.isdir(originale) else []
    modalita = R.primo('modalita', [('briefing', r'^Modalità:\s*(nuovo|riscrittura)', g1)])
    if modalita is None and precedenti:
        R.mancano.remove('modalita')
        modalita = 'riscrittura'
        R.fonti.append(('modalita', modalita, '01-originale/ (cartella presente)'))
    elif modalita is None:
        R.mancano.remove('modalita')
        modalita = 'nuovo'
        R.fonti.append(('modalita', modalita, 'predefinito: nessun 01-originale'))

    profilo = comune.carica_profilo(genere) if genere else None
    override = []

    def confronta(campo, valore, fonte, attuale):
        if valore is None or profilo is None:
            return
        if valore != attuale:
            override.append({'campo': campo, 'valore': valore,
                             'motivo': f'{fonte} dice {valore}; il profilo «{genere}» dice {attuale}'})

    for campo, regex, conv in (
            ('frase_media', r'Frase media:\s*(\d+)\s*-\s*(\d+)', lambda m: [int(m.group(1)), int(m.group(2))]),
            ('dialogo_percento', r'Dialogo:\s*(\d+)\s*-\s*(\d+)\s*%', lambda m: [int(m.group(1)), int(m.group(2))]),
            ('similitudini_max_per_parole', r'una ogni\s+(\d+)\s+parole', lambda m: int(m.group(1))),
            ('capitoli.minimo', r'Capitolo:\s*minimo\s+(\d+)', lambda m: int(m.group(1))),
            # solo dalla riga «Capitolo:»: «frase media 10-13» o «al massimo 150 parole» altrove non sono capitoli
            ('capitoli.media', r'Capitolo:.*\bmedia\s+(\d+)\s*-\s*(\d+)', lambda m: [int(m.group(1)), int(m.group(2))]),
            ('capitoli.massimo', r'Capitolo:.*\bmassimo\s+(\d+)\s+parole', lambda m: int(m.group(1)))):
        m, fonte = R.cerca('manuale', regex)
        if m:
            v = conv(m)
            R.fonti.append((f'stile.{campo}', v, fonte))
            att = profilo
            for k in campo.split('.'):
                att = (att or {}).get(k) if isinstance(att, dict) else None
            confronta(campo, v, fonte, att)

    voci = []
    for m, fonte in R.tutti('manuale', r'Tetto:\s*«([^»]+)»\s*al massimo\s+(\d+)\s+per\s+(capitolo|libro)'):
        voci.append({'id': nuovo.slug(m.group(1)), 'pattern': r'(?i)(?<!\w)' + re.escape(m.group(1)) + r'(?!\w)',
                     'modalita': 'conta', 'massimo': int(m.group(2)), 'ambito': m.group(3)})
        R.fonti.append((f'voci.{voci[-1]["id"]}', f'tetto {m.group(2)} per {m.group(3)}', fonte))
    for m, fonte in R.tutti('manuale', r'Vietato:\s*«([^»]+)»'):
        voci.append({'id': nuovo.slug(m.group(1))[:40], 'pattern': r'(?i)(?<!\w)' + re.escape(m.group(1)) + r'(?!\w)',
                     'modalita': 'vieta'})
        R.fonti.append((f'voci.{voci[-1]["id"]}', 'vietato', fonte))
    nomi_vincolo = []
    for m, fonte in R.tutti('manuale', r'«([^»]+)»\s*non compare nei capitoli\s+([\d\-, ]+)'):
        elenco = [x.strip() for x in m.group(2).split(',') if x.strip()]
        nomi_vincolo.append({'nome': m.group(1), 'pattern': r'\b' + re.escape(m.group(1)) + r'\b',
                             'vietato_in': elenco, 'obbligatorio_in': []})
        R.fonti.append((f'nome_vietato_prima_di.{m.group(1)}', elenco, fonte))
    sep = R.primo('struttura.separatore_scena', [('manuale', r'Separatore di scena:\s*«([^»]+)»', g1),
                                                 ('briefing', r'^Separatore di scena:\s*(\S.*)$', g1)])
    intest = R.primo('struttura.intestazione_capitolo', [('manuale', r'Intestazione del capitolo:\s*«([^»]+)»', g1),
                                                         ('briefing', r'^Intestazione capitolo:\s*(\S.*)$', g1)])

    # cronologia e nomi
    trovate = R.tutti('bibbia', r'\*\*([^*]+)\*\*.*?\bnat[oa] il\s+' + DATA)
    nascite = [{'chi': m.group(1), 'data': m.group(2)} for m, _ in trovate]
    eventi = []
    for m, fonte in R.tutti('scaletta', r'^\|\s*(\d+)\s*\|\s*' + DATA + r'\s*\|\s*([^|]*)\|'):
        eventi.append({'id': f'capitolo_{m.group(1)}', 'data': m.group(2), 'capitolo': int(m.group(1)),
                       'descrizione': m.group(3).strip()})
    for m, fonte in trovate:
        R.fonti.append((f'cronologia.nascite.{m.group(1)}', m.group(2), fonte))
    for m, fonte in R.tutti('scaletta', r'^\|\s*(\d+)\s*\|\s*' + DATA):
        R.fonti.append((f'cronologia.eventi.capitolo_{m.group(1)}', m.group(2), fonte))
    nomi = sorted({w for m, _ in R.tutti('bibbia', r'\*\*([^*]+)\*\*') for w in m.group(1).split() if w[:1].isupper()})
    if not nomi:
        R.mancano.append('nomi_propri (nessun nome in grassetto nella bibbia)')
    anni = sorted({int(e['data'][:4]) for e in eventi})

    sigle = nuovo.SIGLE[profilo['chiusura_preferita']] if profilo else None
    if profilo is None:
        R.mancano.append('dichiarazioni.chiusura (serve il profilo)')
    libro = {'titolo': titolo, 'sottotitolo': None, 'autore': autore, 'lingua': 'it', 'modalita': modalita}
    if modalita == 'riscrittura':
        libro['testo_precedente'] = f'01-originale/{precedenti[0]}' if precedenti else None
        if not precedenti:
            R.mancano.append('testo_precedente (nessun .md in 01-originale/)')
    libro.update({
        'serie': None, 'ebook': False, 'profilo': genere, 'override': override, 'gate': nuovo.GATE_PREDEFINITI,
        'parole': {'metodo': 'unico', 'target_totale': target},
        'formato': {'pagina_pollici': [5.5, 8.5], 'carta': 'crema', 'bleed': False,
                    'margini_mm': {'alto': 20, 'basso': 20, 'esterno': 16, 'interno_scelto': 16},
                    'font': {'nome': 'EB Garamond', 'corpo_pt': 11.5, 'interlinea': 1.5},
                    'numerazione': {'da': 'capitolo_1', 'pagine_iniziali': 'senza_numero', 'posizione': 'piede_centro'}},
        'voci': voci, 'vincoli_capitolo': [], 'nome_vietato_prima_di': nomi_vincolo,
        'dichiarazioni': {'chiusura': {'sigle': sigle, 'prevista_da': 'scaletta'}},
        'struttura': {'separatore_scena': {'sorgente': sep or '* * *', 'stampa': sep or '* * *'},
                      'intestazione_capitolo': intest or 'Luogo — giorno e data', 'parti': [], 'interludi': []},
        'calendario': {'anni_ammessi': anni},
        'ortografia': {'parole_ammesse_file': 'nomi_propri.txt'},
        'copyright': {'riga': '© {anno} {autore}. Tutti i diritti riservati.', 'anno': datetime.date.today().year,
                      'fantasia': "Quest'opera è frutto di fantasia. Nomi, personaggi, luoghi e fatti sono invenzione "
                                  "dell'autore o usati in modo fittizio; ogni somiglianza con persone, vive o scomparse, "
                                  "o con fatti realmente accaduti è puramente casuale.",
                      'nota_autore': None},
    })
    R.mancano += ['formato (predefinito 5.5 x 8.5: da confermare)', 'copyright.fantasia (testo standard: da confermare)']
    if not anni:
        R.mancano.append('calendario.anni_ammessi (nessuna data in scaletta)')
    cron = {'nascite': nascite, 'eventi': eventi, 'durate': [], 'cifre': [], 'eta_per_capitolo': {'calcolata': True}}
    return R, libro, cron, nomi, presenti


def adotta(percorso, titolo=None):
    cartella = os.path.realpath(percorso)
    if not os.path.isdir(cartella):
        raise comune.ErroreMotore(f'Cartella inesistente: {percorso}')
    R, libro, cron, nomi, presenti = ricava(cartella, titolo)
    if not libro['titolo']:
        raise comune.ErroreMotore('Titolo non trovato nei documenti (briefing «Titolo di lavoro:», oppure '
                                  '«# Manuale di stile — <titolo>», «# Bibbia — <titolo>», «# Scaletta — <titolo>»). '
                                  'Non ho scritto nulla. Qual è il titolo? Indicalo così: '
                                  'zb adotta <cartella> --titolo "<titolo>"')
    scritti, esistenti = [], []

    def scrivi(rel, testo):
        if os.path.exists(os.path.join(cartella, rel)):
            esistenti.append(rel)
        else:
            comune.scrivi(cartella, rel, testo)
            scritti.append(rel)

    intest = '# BOZZA generata da «zb adotta»: ogni valore ha la fonte in 06-diagnostica/adozione.md.\n'
    scrivi('libro.yaml', intest + yaml.safe_dump(libro, sort_keys=False, allow_unicode=True, width=120))
    if True:
        scrivi('cronologia.yaml', '# BOZZA da «zb adotta» (date dalla scaletta, nascite dalla bibbia).\n'
               + yaml.safe_dump(cron, sort_keys=False, allow_unicode=True))
    scrivi('nomi_propri.txt', '\n'.join(nomi) + '\n' if nomi else '')
    stato = comune.leggi_yaml(os.path.join(comune.radice_motore(), 'modelli', 'stato.yaml'))
    docs = revisione.DOCUMENTI
    mancanti_doc = [d for d in docs if not os.path.isfile(os.path.join(cartella, d)) and d not in GENERATI]
    capitoli = [int(n) for n, _ in comune.unita(cartella, libro) if n.isdigit()] if os.path.isdir(
        os.path.join(cartella, '04-manoscritto')) else []
    stato.update({'libro': libro['titolo'], 'fase': 'documenti', 'motore_commit': None,
                  'passo': 'adozione: bozze da approvare' if not mancanti_doc else
                  'adozione: mancano ' + ', '.join(mancanti_doc),
                  'gate_in_attesa': 'documenti' if not mancanti_doc else None,
                  'ultimo_capitolo_scritto': max(capitoli) if capitoli else None,
                  'parole': {'scritte': 0, 'obiettivo': libro['parole']['target_totale'] or 0, 'metodo': 'unico'},
                  'aggiornato': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})
    scrivi('stato.yaml', yaml.safe_dump(stato, sort_keys=False, allow_unicode=True))
    valido = 'sì'
    if 'libro.yaml' in scritti:
        try:
            comune.carica_libro(cartella)
        except comune.ErroreMotore as e:
            valido = 'no — ' + str(e).replace('\n', ' ')
    righe = [f'# Adozione — {libro["titolo"] or "(titolo non ricavato)"}', '',
             'Bozze generate da `zb adotta`. Niente è approvato: si approva al gate «documenti».', '',
             f'Documenti letti: {", ".join(DOC[k] for k in presenti)}.',
             f'File scritti: {", ".join(scritti) or "nessuno"}.',
             f'File già presenti, non toccati: {", ".join(esistenti) or "nessuno"}.',
             f'libro.yaml valido: {valido}.', '', '## Valori e fonti', '',
             '| Campo | Valore | Fonte (file:riga) |', '|---|---|---|']
    righe += [f'| {c} | {v} | {f} |' for c, v, f in R.fonti]
    righe += ['', '## Override rispetto al profilo', '']
    righe += [f'- {o["campo"]}: {o["valore"]} — {o["motivo"]}' for o in libro['override']] or ['- nessuno']
    righe += ['', '## Non ricavato (da completare a mano)', '']
    righe += [f'- {m}' for m in R.mancano] or ['- niente']
    righe += [f'- documento mancante: {d}' for d in mancanti_doc]
    righe += ['', '## Prossimo passo', '',
              'Gate «documenti» aperto: avanti, ok o correggi.' if not mancanti_doc else
              'Completa i documenti mancanti, poi «zb pronto <libro>» apre il gate «documenti».']
    scrivi('06-diagnostica/adozione.md', '\n'.join(righe) + '\n')
    return scritti, esistenti, R.mancano + [f'documento mancante: {d}' for d in mancanti_doc], valido


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: adotta.py <cartella-del-libro> [--titolo «titolo»]')
    titolo = argv[argv.index('--titolo') + 1] if '--titolo' in argv and argv.index('--titolo') + 1 < len(argv) else None
    scritti, esistenti, mancano, valido = adotta(args[0], titolo)
    for s in scritti:
        print(f'scritto: {s}')
    for e in esistenti:
        print(f'già presente, non toccato: {e}')
    for m in mancano:
        print(f'non ricavato: {m}')
    print(f'libro.yaml valido: {valido}')
    print('Fermo alla fase «documenti». Dettagli e fonti: 06-diagnostica/adozione.md')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/avvio.py`

```python
"""Avvio obbligatorio prima di lavorare su un libro (proposta B.4, C.4, C.5).

Uso: python3 -B avvio.py <libro>        (oppure ZB_LIBRO=<libro>)
Si ferma (codice 2) e non scrive nulla da nessuna parte se:
- il percorso non contiene un libro (se c'è un briefing, elenca cosa manca);
- la cartella del libro non è scrivibile o «git push --dry-run» fallisce (errore esatto);
- il ramo non è quello della sessione (ZB_RAMO, se indicato);
- ci sono modifiche non salvate nel libro, o il ramo è avanti o indietro rispetto a origin;
- stato.yaml manca o non è valido, oppure push_in_sospeso è vero;
- in fase «documenti»: briefing incompleto (non per un libro in riscrittura senza briefing nel formato
  del motore, cioè senza la riga «Titolo di lavoro:»: è un libro adottato con i suoi documenti);
- un documento approvato è cambiato fuori procedura (sha256 diverso).
Se tutto va bene stampa la riga «Letto: …» (file, righe, sha256, ultimo commit; libro e motore)
e scrive solo il marker <libro>/.zb/letto-<session_id>.
Con il blocco «voce» in libro.yaml la riga «Letto» include anche il briefing e la scheda della voce
(banca-voci da ZB_BANCA_VOCI); se la voce non verifica (voce.py) stampa un AVVISO, senza fermarsi.
"""
import datetime
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import fase  # noqa: E402
import nuovo  # noqa: E402
import voce  # noqa: E402

DA_LEGGERE = {
    'documenti': ['00-progetto/briefing.md', '02-bibbia/bibbia.md', 'cronologia.yaml',
                  '03-architettura/scaletta.md', '03-architettura/piano-parole.md'],
    'pagina_campione': ['02-bibbia/bibbia.md', '05-revisioni/pagina-campione.md'],
    'stesura': ['03-architettura/scaletta.md', '03-architettura/piano-parole.md', 'cronologia.yaml',
                '02-bibbia/bibbia.md'],
    'chiusura': ['03-architettura/scaletta.md', 'cronologia.yaml'],
    'chiuso': [],
}


def ferma(msg):
    raise comune.ErroreMotore(msg)


def briefing_senza_libro(percorso):
    """Se il percorso non ha libro.yaml ma ha un briefing, elenca cosa manca."""
    p = os.path.realpath(percorso)
    candidati = [p] if os.path.isfile(p) else [os.path.join(p, 'briefing.md'), os.path.join(p, '00-progetto', 'briefing.md')]
    for c in candidati:
        if os.path.isfile(c) and c.endswith('.md'):
            manca = nuovo.mancanze(nuovo.leggi_briefing(c), nuovo.cartella_dal_briefing(c))
            if manca:
                ferma(f'Nessun libro.yaml: c\'è solo il briefing {c}, incompleto. Mancano:\n- ' + '\n- '.join(manca))
            ferma(f'Nessun libro.yaml: il briefing {c} è completo. Per creare il libro: zb nuovo {c}')
    return None


def riga_file(cartella, rel, etichetta=None):
    p = rel if os.path.isabs(rel) else os.path.join(cartella, rel)
    testo = open(p, encoding='utf-8').read()
    commit = comune.ultimo_commit(os.path.dirname(p), p) or 'mai salvato'
    return (f'{etichetta or rel} ({len(testo.splitlines())} righe, sha256 {comune.sha256_file(p)[:12]}, '
            f'commit {commit})'), comune.sha256_file(p)


def controlla(percorso):
    """Tutti i controlli, senza scrivere nulla. Restituisce i dati per il marker."""
    print(f'Percorso indicato: {percorso}')
    try:
        cartella = comune.trova_libro(percorso)
    except comune.ErroreMotore:
        briefing_senza_libro(percorso)
        raise
    print(f'Libro: {cartella}')
    cartella, libro, profilo = comune.carica_libro(cartella)

    # 1. scrivibilità, prima di qualunque scrittura (B.4)
    zb = os.path.join(cartella, '.zb')
    if not os.access(cartella, os.W_OK) or (os.path.exists(zb) and not os.access(zb, os.W_OK)):
        ferma(f'La sessione non può scrivere nella cartella del libro ({cartella}). Non scrivo nulla.')
    if comune.radice_git(cartella) == '/':
        ferma(f'{cartella} non è in un repository git: non posso salvare. Non scrivo nulla.')
    codice, out, err = comune.git(cartella, 'push', '--dry-run')
    if codice != 0:
        ferma(f'git push --dry-run non riuscito nel repository del libro:\n{err or out}\nNon scrivo nulla.')

    # 2. ramo e allineamento
    ramo = comune.ramo(cartella)
    atteso = os.environ.get('ZB_RAMO')
    if atteso and ramo != atteso:
        ferma(f'Checkout del libro sul ramo «{ramo}», ma la sessione lavora su «{atteso}».')
    codice, out, _ = comune.git(cartella, 'status', '--porcelain', '--', '.')
    if out:
        ferma('Modifiche non salvate nel libro (tieni o scarta? non scarto nulla da solo):\n' + out)
    codice, conti, err = comune.git(cartella, 'rev-list', '--left-right', '--count', 'HEAD...@{u}')
    if codice != 0:
        ferma(f'Nessun ramo remoto collegato a «{ramo}»: {err}')
    avanti, indietro = (int(x) for x in conti.split())
    if indietro:
        ferma(f'Il ramo «{ramo}» è indietro di {indietro} commit rispetto a origin: prima git pull.')
    if avanti:
        ferma(f'Il ramo «{ramo}» ha {avanti} commit non pushati: prima git push (C.5).')

    # 3. stato, briefing, documenti approvati
    stato = fase.carica_stato(cartella)
    if stato['push_in_sospeso']:
        ferma('stato.yaml: push_in_sospeso è vero. Prima il push.')
    pb = os.path.join(cartella, '00-progetto', 'briefing.md')
    briefing_motore = os.path.isfile(pb) and re.search(r'(?m)^Titolo di lavoro:', open(pb, encoding='utf-8').read())
    if stato['fase'] == 'documenti' and (libro.get('modalita') != 'riscrittura' or briefing_motore):
        manca = nuovo.mancanze(nuovo.leggi_briefing(os.path.join(cartella, '00-progetto', 'briefing.md')), cartella)
        if manca:
            ferma('Briefing incompleto. Mancano:\n- ' + '\n- '.join(manca))
    cambiati = [rel for rel, v in stato['documenti_approvati'].items()
                if not comune.documento_invariato(os.path.join(cartella, rel), v['sha256'], v.get('commit'))]
    if cambiati:
        ferma('Documenti approvati cambiati fuori procedura (sha256 diverso da quello registrato):\n- '
              + '\n- '.join(cambiati) + '\nSe la modifica è autorizzata dall\'autore: salvala con un commit, poi '
              '«zb riapprova <libro> <documento> <motivo>».')

    # 4. file da leggere
    letti, sha = [], {}
    elenco = ['libro.yaml', 'stato.yaml', 'LEGGIMI.md', '03-architettura/manuale-di-stile.md']
    elenco += DA_LEGGERE[stato['fase']]
    if libro.get('voce'):
        elenco.append('00-progetto/briefing.md')
    if libro.get('modalita') == 'riscrittura':
        elenco.append(libro['testo_precedente'])
    if stato['fase'] == 'stesura' and stato['ultimo_capitolo_scritto']:
        u = dict(comune.unita(cartella, libro)).get(str(stato['ultimo_capitolo_scritto']))
        if u:
            elenco.append(os.path.relpath(u, cartella))
    for rel in dict.fromkeys(elenco):
        if os.path.isfile(os.path.join(cartella, rel)):
            r, s = riga_file(cartella, rel)
            letti.append(r)
            sha[rel] = s
    pp = os.path.join(comune.radice_motore(), 'profili', f'{libro["profilo"]}.yaml')
    r, s = riga_file(cartella, pp, f'profilo {libro["profilo"]}')
    letti.append(r)
    sha[f'profilo {libro["profilo"]}'] = s
    avvisi = []
    if libro.get('voce'):
        avvisi = scheda_voce(libro['voce'], letti, sha)
    libro_commit = comune.git(cartella, 'log', '-1', '--format=%h «%s»')[1]
    motore_commit = comune.git(comune.radice_motore(), 'log', '-1', '--format=%h')[1] or 'fuori da git'
    return cartella, libro, stato, letti, sha, libro_commit, motore_commit, ramo, avvisi


def scheda_voce(v, letti, sha):
    """Aggiunge la scheda della voce a «Letto»; restituisce gli avvisi (mai un fermo)."""
    slug = v['slug']
    try:
        b = voce.banca()
        problemi = voce.problemi(b, slug)
    except comune.ErroreMotore as e:
        return [f'voce «{slug}» non verificata: {e}'.replace('\n', ' ')]
    p = voce.scheda(b, slug)
    if os.path.isfile(p):
        r, s = riga_file(os.path.dirname(p), p, f'scheda della voce {slug}')
        letti.append(r)
        sha[f'voce {slug}'] = s
    return [f'voce «{slug}»: {x}' for x in problemi]


def main(argv):
    args = comune.argomenti(argv)
    percorso = args[0] if args else os.environ.get('ZB_LIBRO')
    if not percorso:
        raise comune.ErroreMotore('Uso: avvio.py <libro> (oppure ZB_LIBRO=<libro>)')
    cartella, libro, stato, letti, sha, libro_commit, motore_commit, ramo, avvisi_voce = controlla(percorso)
    print(f'Ramo: {ramo}; allineato a origin: sì')
    print('Letto: ' + ', '.join(letti) + ';')
    print(f'libro @ {libro_commit}; motore @ {motore_commit}; fase {stato["fase"]}, '
          f'gate {stato["gate_in_attesa"] or "nessuno"}.')
    rc = stato.get('revisione_in_corso')
    print(f'Passo: {stato["passo"] or "—"}; capitoli scritti fino a {stato["ultimo_capitolo_scritto"] or "—"}, '
          f'approvati fino a {stato["ultimo_capitolo_approvato"] or "—"}; '
          f'parole {stato["parole"]["scritte"]}/{stato["parole"]["obiettivo"]}.')
    if rc:
        print(f'Revisione in corso: gate {rc["gate"]}, blocco {rc["blocco"]} di {rc["blocchi_totali"]}.')
    for c in stato['correzioni_aperte']:
        print(f'Correzione aperta [{c["gate"]}]: {c["testo"]}')
    for a in stato['avvisi_aperti']:
        print(f'Avviso aperto: {a}')
    if libro.get('voce'):
        print(f'Voce: {libro["voce"]["slug"]}, ambientazione {libro["voce"].get("ambientazione") or "altro"}. '
              'Prima di ogni capitolo: rileggi la scheda della voce e il briefing.')
    for a in avvisi_voce:
        print(f'AVVISO: {a}')
    for n_int, d in comune.interludi_in_anticipo(cartella, libro):
        print(f'AVVISO: {n_int} in anticipo (va dopo il capitolo {d}, non ancora scritto).')
    print(fase.prossimo(stato))
    # unica scrittura: il marker di sessione dentro il libro
    sid, fonte = comune.sessione_corrente()
    d = comune.prepara_zb(cartella)
    marker = os.path.join(d, f'letto-{sid}')
    corpo = [f'data: {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}',
             f'libro_commit: {libro_commit}', f'motore_commit: {motore_commit}']
    corpo += [f'{k}: {v}' for k, v in sha.items()]
    comune.scrivi(cartella, marker, '\n'.join(corpo) + '\n')
    print(f'Sessione: {sid} ({fonte}); marker {os.path.relpath(marker, cartella)}.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/capitolo.py`

```python
"""Controlli di un capitolo in un colpo solo (proposta C.2).

Uso: python3 -B capitolo.py <libro> <N> [--schermo]
N è il numero del capitolo, oppure il nome di un'unità («prologo», «interludio II»).
Esegue: parole con il metodo unico rispetto a minimo del profilo (KO, solo capitoli)
e budget di piano-parole.md (AVVISO oltre la tolleranza); totale previsto del libro (AVVISO oltre
capitoli.tolleranza_totale, con il budget residuo proposto, vedi conta.py); controlli di stile.py;
continuità di continuita.py; anti-riciclo di riciclo.py; dichiarazioni della riga
nascosta <!-- zb: … --> secondo «dichiarazioni» di libro.yaml; scene (solo capitoli numerati), contate
dal separatore struttura.separatore_scena.sorgente: numero fuori da capitoli.scene_per_capitolo (KO),
scena sotto il minimo di scene.lunghezza (KO) o sopra il massimo (AVVISO). Il sequel è informativo.
Report: <libro>/06-diagnostica/capitoli/NN.md, con la checklist manuale (tic fissi, voci di cronologia
toccate e le voci del libro in checklist_capitolo di libro.yaml). Codice 1 se c'è almeno un KO.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402
import conta  # noqa: E402
import continuita  # noqa: E402
import riciclo  # noqa: E402
import stile  # noqa: E402
from stile import risultato, tabella  # noqa: E402


CHECKLIST_TIC = [
    'Tic: descrizione del meteo all\'inizio del capitolo (05-critica r. 20)',
    'Tic: domande retoriche interiori in serie (05-critica r. 20)',
    'Tic: chiusure di paragrafo con morale o riflessione (05-critica r. 20)',
    'Tic: scena che finisce con un momento di consapevolezza (05-critica r. 20)',
]


def dichiarazioni(cartella, libro, unita, nome):
    """Controlli delle dichiarazioni dell'unità `nome` (lista di (nome, percorso) in ordine)."""
    spec = libro.get('dichiarazioni') or {}
    if not spec or not nome.isdigit():
        return []
    out = []
    scaletta = {r.get('Unità', '').lower(): r for r in
                comune.tabella_md(os.path.join(cartella, '03-architettura', 'scaletta.md'))}
    capitoli = [(n, comune.dichiarazioni_unita(open(p, encoding='utf-8').read()), p)
                for n, p in unita if n.isdigit()]
    idx = [n for n, _, _ in capitoli].index(nome)
    dic, percorso = capitoli[idx][1], capitoli[idx][2]
    for campo, s in spec.items():
        val = dic.get(campo)
        if val is None:
            out.append(risultato(nome, f'dichiarazione:{campo}', 'KO', None, 'campo non dichiarato nella riga zb'))
            continue
        ammessi = s.get('sigle') or s.get('valori')
        if ammessi and val not in [str(a) for a in ammessi]:
            out.append(risultato(nome, f'dichiarazione:{campo}', 'KO', None, f'«{val}» non ammesso ({", ".join(map(str, ammessi))})'))
        if s.get('prevista_da') == 'scaletta':
            prevista = (scaletta.get(nome) or {}).get(campo.capitalize())
            if prevista and prevista != val:
                out.append(risultato(nome, f'dichiarazione:{campo}', 'AVVISO', None,
                                     f'dichiarata {val}, prevista in scaletta {prevista}'))
        for chiave, limite in s.items():
            if chiave.endswith('massimo_consecutivi'):
                sigla = chiave[:-len('_massimo_consecutivi')] if chiave != 'massimo_consecutivi' else None
                if sigla is not None and val != sigla:
                    continue
                k = 0
                for _, d, _ in reversed(capitoli[:idx + 1]):
                    if d.get(campo) == val:
                        k += 1
                    else:
                        break
                if k > limite:
                    out.append(risultato(nome, f'dichiarazione:{campo}', 'KO', None,
                                         f'{k} capitoli di fila con {campo}={val} (massimo {limite})'))
        if 'riga_finale_min_parole' in s:
            prosa = comune.righe_prosa(open(percorso, encoding='utf-8').read())
            if prosa:
                n, r = prosa[-1]
                if len(comune.parole(r)) < s['riga_finale_min_parole']:
                    out.append(risultato(nome, f'dichiarazione:{campo}', 'KO', n,
                                         f'ultima riga di {len(comune.parole(r))} parole: «{r.strip()}»'))
    return out


def scene(testo, libro):
    """[(riga di inizio, parole)] delle scene, separate da struttura.separatore_scena.sorgente."""
    sep = ((libro.get('struttura') or {}).get('separatore_scena') or {}).get('sorgente') or '* * *'
    out, inizio, righe = [], None, []
    for n, r in enumerate(testo.splitlines() + [sep], 1):
        if r.strip() == sep.strip():
            p = conta.conta_testo('\n'.join(righe))
            if p:
                out.append((inizio, p))
            inizio, righe = None, []
        else:
            if inizio is None and r.strip() and not r.strip().startswith(('#', '<!--')) and conta.conta_testo(r):
                inizio = n
            righe.append(r)
    return out


def controlla_scene(nome, testo, libro, profilo):
    sc = scene(testo, libro)
    lo, hi = profilo['capitoli']['scene_per_capitolo']
    mn, mx = profilo['scene']['lunghezza']
    out = []
    if not lo <= len(sc) <= hi:
        out.append(stile.risultato(nome, 'scene_numero', 'KO', None, f'{len(sc)} scene, ammesse {lo}-{hi}'))
    for i, (riga, p) in enumerate(sc, 1):
        if p < mn:
            out.append(stile.risultato(nome, 'scena_minimo', 'KO', riga, f'scena {i}: {p} parole, minimo {mn}'))
        elif p > mx:
            out.append(stile.risultato(nome, 'scena_massimo', 'AVVISO', riga, f'scena {i}: {p} parole, massimo {mx}'))
    return out


def controlla(cartella, libro, profilo, nome):
    unita = comune.unita(cartella, libro)
    nomi = [n for n, _ in unita]
    if nome not in nomi:
        raise comune.ErroreMotore(f'Unità «{nome}» inesistente in 04-manoscritto')
    percorso = dict(unita)[nome]
    testo = open(percorso, encoding='utf-8').read()
    out = []
    n_parole = conta.conta_testo(testo)
    if nome.isdigit() and n_parole < profilo['capitoli']['minimo']:
        out.append(risultato(nome, 'parole_minimo', 'KO', None,
                             f'{n_parole} parole, minimo {profilo["capitoli"]["minimo"]}'))
    bud = conta.budget(cartella).get(nome.lower())
    if bud:
        sc = (n_parole - bud) / bud
        if abs(sc) > profilo['capitoli']['tolleranza_budget']:
            out.append(risultato(nome, 'parole_budget', 'AVVISO', None,
                                 f'{n_parole} parole su {bud} ({sc:+.0%}, tolleranza ±{profilo["capitoli"]["tolleranza_budget"]:.0%})'))
    avviso = conta.totale_previsto(cartella, libro, profilo)[3]
    if avviso:
        out.append(risultato(nome, 'parole_totale', 'AVVISO', None, avviso))
    if nome.isdigit():
        out += controlla_scene(nome, testo, libro, profilo)
    for n_int, d in comune.interludi_in_anticipo(cartella, libro):
        if n_int == nome:
            out.append(risultato(nome, 'posizione', 'AVVISO', None,
                                 f'in anticipo: va dopo il capitolo {d}, non ancora scritto; per ora sta in coda'))
    met, ris_stile = stile.controlla_libro(cartella, libro, profilo)[nome]
    out += ris_stile
    out += [r for r in continuita.controlla_libro(cartella, libro)[0] if r['unita'] == nome]
    out += [r for r in riciclo.controlla_libro(cartella, libro) if r['unita'] == nome]
    out += dichiarazioni(cartella, libro, unita, nome)
    met['parole'] = n_parole
    return met, comune.applica_eccezioni(out, libro)


def main(argv):
    args = comune.argomenti(argv)
    if len(args) < 2:
        raise comune.ErroreMotore('Uso: capitolo.py <libro> <N> [--schermo]')
    cartella, libro, profilo = comune.carica_libro(args[0])
    nome = ' '.join(args[1:])
    met, out = controlla(cartella, libro, profilo, nome)
    ko = sum(1 for r in out if r['esito'] == 'KO')
    righe = [f'# Capitolo {nome} — controlli', '', f'Libro: {libro["titolo"]} — profilo: {libro["profilo"]}.', '',
             f'Parole (metodo unico): {met["parole"]} · frase media: {met["frase_media"]} · '
             f'dialogo: {met["dialogo_percento"]}%', '',
             f'Esito: {ko} KO, {sum(1 for r in out if r["esito"] == "AVVISO")} avvisi.', '']
    righe += tabella(out) if out else ['Nessun KO e nessun avviso.']
    righe += ['', '## Checklist manuale', '',
              'Controlli che il motore non sa fare da solo: li verifica l\'autore.', '',
              '| Controllo | Verificato dall\'autore |', '|---|---|']
    righe += [f'| {c} | [ ] |' for c in CHECKLIST_TIC]
    righe += [f'| {v} | [ ] |' for v in continuita.voci_toccate(cartella, libro, nome)]
    righe += [f'| {v} | [ ] |' for v in libro.get('checklist_capitolo') or []]
    testo = '\n'.join(righe + [''])
    if '--schermo' in argv:
        print(testo)
    else:
        nomefile = f'{int(nome):02d}' if nome.isdigit() else nome.replace(' ', '-')
        print('scritto', comune.scrivi(cartella, f'06-diagnostica/capitoli/{nomefile}.md', testo))
    return 1 if ko else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```

### `motore/script/compila.py`

```python
"""Compone il manoscritto completo di un libro (proposta B.2, B.4).

Uso: python3 -B compila.py <libro>
Scrive <libro>/05-output/<titolo>-completo.md: frontespizio, pagina di copyright
(riga ©, dichiarazione di fantasia, nota dell'autore), sommario, parti e unità
nell'ordine di lettura. Toglie le righe nascoste <!-- zb: … -->, sostituisce il
separatore di scena del sorgente con quello di stampa e intitola le unità
(«N. Titolo» dall'intestazione sorgente «# N — Titolo», «Prologo», «Epilogo», titolo
dell'interludio; un capitolo senza titolo resta «Capitolo N», con un avviso). Le sezioni sono
delimitate da commenti <!-- zb:sezione … --> che impagina.py usa per le pagine.
Titoli interni: nell'unità si scarta solo il primo titolo (l'intestazione «# N — Titolo», che il motore
riscrive); gli altri titoli («## L'enigma…») restano, abbassati di un livello sotto il titolo dell'unità.
Appendici: i file di 05-appendici/ dichiarati in libro.yaml (campo «appendici», in ordine) vengono dopo
l'ultima unità, epilogo compreso, ognuna su pagina nuova e nel sommario. Testo .md; immagini .svg (convertite
in PNG con Chromium, stampa/svg_png.js), .png, .jpg: vanno in 05-output/appendici/ con titolo e didascalia.
Un file di 05-appendici/ non dichiarato dà un avviso, non blocca.
Il risultato è deterministico: stesso libro, stesso file.
"""
import datetime
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune  # noqa: E402


def titolo_capitolo(testo):
    """Titolo dall'intestazione sorgente «# N — Titolo» (anche «## N - Titolo»); None se manca."""
    for r in testo.splitlines():
        if r.strip().startswith('#'):
            m = re.match(r'^#+\s*\d+\s*[—–-]\s*(\S.*?)\s*$', r.strip())
            return m.group(1) if m else None
    return None


def titolo_unita(nome, libro, testo=None, avvisi=None):
    """«N. Titolo» per un capitolo con il titolo nell'intestazione; senza titolo «Capitolo N» e un avviso."""
    if nome.isdigit():
        t = titolo_capitolo(testo or '')
        if t:
            return f'{nome}. {t}'
        if avvisi is not None:
            avvisi.append(f'AVVISO: capitolo {nome} senza titolo nell\'intestazione («# {nome} — Titolo»): resta «Capitolo {nome}».')
        return f'Capitolo {nome}'
    if nome.startswith('interludio '):
        num = nome.split(' ', 1)[1]
        for i in (libro.get('struttura') or {}).get('interludi') or []:
            if str(i['numero']) == num:
                return i['titolo']
        return f'Interludio {num}'
    return nome.capitalize()


def corpo_unita(testo, sep_sorgente, sep_stampa):
    """Corpo dell'unità: senza commenti e senza il primo titolo (l'intestazione, riscritta da compila);
    i titoli successivi restano, abbassati di un livello («## X» diventa «### X»)."""
    righe, in_commento, titolo_visto = [], False, False
    for r in testo.splitlines():
        s = r.strip()
        if in_commento:
            in_commento = '-->' not in s
            continue
        if s.startswith('<!--'):
            in_commento = '-->' not in s
            continue
        if re.match(r'^#{1,6}\s', s) or re.match(r'^#{1,6}$', s):
            if not titolo_visto:
                titolo_visto = True
                continue
            livello = len(s) - len(s.lstrip('#'))
            righe.append('#' * min(livello + 1, 6) + s[livello:])
            continue
        if s and s == sep_sorgente.strip():
            righe.append(f'<p class="scena">{sep_stampa}</p>')
            continue
        righe.append(r.rstrip())
    while righe and not righe[0].strip():
        righe.pop(0)
    while righe and not righe[-1].strip():
        righe.pop()
    return '\n'.join(righe)


IMMAGINI = ('.svg', '.png', '.jpg', '.jpeg')


def immagine_appendice(cartella, sorgente, avvisi):
    """Percorso relativo a 05-output dell'immagine pronta per la stampa (PNG o JPG), o None se non riesce."""
    nome = os.path.basename(sorgente)
    base, est = os.path.splitext(nome)
    dest_dir = comune.percorso_in_libro(cartella, '05-output/appendici')
    os.makedirs(dest_dir, exist_ok=True)
    if est.lower() != '.svg':
        shutil.copyfile(sorgente, os.path.join(dest_dir, nome))
        return f'appendici/{nome}'
    png = os.path.join(dest_dir, base + '.png')
    try:
        import impagina
        env = dict(os.environ, NODE_PATH=impagina.node_path())
        r = subprocess.run(['node', os.path.join(comune.radice_motore(), 'stampa', 'svg_png.js'), sorgente, png],
                           env=env, capture_output=True, text=True)
        ok = r.returncode == 0 and os.path.isfile(png)
        motivo = (r.stderr.strip().splitlines() or ['?'])[-1]
    except FileNotFoundError:
        ok, motivo = False, 'node non trovato'
    if not ok:
        if avvisi is not None:
            avvisi.append(f'AVVISO: appendice {nome}: conversione SVG → PNG non riuscita ({motivo}); '
                          f'l\'immagine manca nel manoscritto compilato.')
        return None
    return f'appendici/{base}.png'


def appendici(cartella, libro, avvisi=None):
    """[(titolo, testo markdown)] delle appendici dichiarate in libro.yaml, nell'ordine dichiarato.
    Un file dichiarato e mancante ferma il motore; un file di 05-appendici/ non dichiarato dà un avviso."""
    dichiarate = libro.get('appendici') or []
    cart = os.path.join(cartella, '05-appendici')
    presenti = sorted(f for f in os.listdir(cart) if not f.startswith('.')) if os.path.isdir(cart) else []
    nomi = [a['file'] for a in dichiarate]
    for f in presenti:
        if f not in nomi and avvisi is not None:
            avvisi.append(f'AVVISO: 05-appendici/{f} non è dichiarato in libro.yaml (appendici): non entra nel libro.')
    out = []
    for a in dichiarate:
        sorgente = os.path.join(cart, a['file'])
        if not os.path.isfile(sorgente):
            raise comune.ErroreMotore(f'Appendice dichiarata in libro.yaml ma assente: 05-appendici/{a["file"]}')
        est = os.path.splitext(a['file'])[1].lower()
        if est == '.md':
            corpo = corpo_unita(open(sorgente, encoding='utf-8').read(), '\0', '')
        elif est in IMMAGINI:
            src = immagine_appendice(cartella, sorgente, avvisi)
            didascalia = (a.get('didascalia') or '').strip()
            if src:
                corpo = (f'<figure class="immagine"><img src="{src}" alt="{a["titolo"]}">'
                         + (f'<figcaption>{didascalia}</figcaption>' if didascalia else '') + '</figure>')
            else:
                corpo = f'<p class="immagine-mancante">[immagine non convertita: {a["file"]}]</p>'
        else:
            raise comune.ErroreMotore(f'Appendice 05-appendici/{a["file"]}: formato non previsto '
                                      f'(ammessi .md, {", ".join(IMMAGINI)})')
        out.append((a['titolo'], corpo))
    return out


def compila(cartella, libro, avvisi=None):
    st = libro.get('struttura') or {}
    sep = st['separatore_scena']
    cop = libro['copyright']
    anno = cop.get('anno') or datetime.date.today().year
    unita = comune.unita(cartella, libro)
    testi = {nome: open(p, encoding='utf-8').read() for nome, p in unita}
    titoli = {nome: titolo_unita(nome, libro, testi[nome], avvisi) for nome, _ in unita}
    parti = {p['capitoli'][0]: p['titolo'] for p in st.get('parti') or []}
    pezzi = ['<!-- zb:sezione frontespizio -->', '', f'# {libro["titolo"]}', '']
    if libro.get('sottotitolo'):
        pezzi += [f'## {libro["sottotitolo"]}', '']
    pezzi += [f'### {libro["autore"]}', '', '<!-- zb:sezione copyright -->', '',
              cop['riga'].replace('{anno}', str(anno)).replace('{autore}', libro['autore']), '',
              cop['fantasia'].strip(), '']
    if cop.get('nota_autore'):
        pezzi += [cop['nota_autore'].strip(), '']
    app = appendici(cartella, libro, avvisi)
    pezzi += ['<!-- zb:sezione sommario -->', '', '## Sommario', '']
    for nome, _ in unita:
        if nome.isdigit() and int(nome) in parti:
            pezzi.append(f'- **{parti[int(nome)]}**')
        pezzi.append(f'- {titoli[nome]}')
    for titolo, _ in app:
        pezzi.append(f'- {titolo}')
    pezzi.append('')
    for nome, p in unita:
        if nome.isdigit() and int(nome) in parti:
            pezzi += ['<!-- zb:sezione parte -->', '', f'# {parti[int(nome)]}', '']
        tipo = 'capitolo' if nome.isdigit() else nome.split()[0]
        pezzi += [f'<!-- zb:sezione {tipo} -->', '', f'## {titoli[nome]}', '',
                  corpo_unita(testi[nome], sep['sorgente'], sep['stampa']), '']
    for titolo, corpo in app:
        pezzi += ['<!-- zb:sezione appendice -->', '', f'## {titolo}', '', corpo, '']
    return '\n'.join(pezzi).rstrip() + '\n'


def main(argv):
    args = comune.argomenti(argv)
    if not args:
        raise comune.ErroreMotore('Uso: compila.py <libro>')
    cartella, libro, _ = comune.carica_libro(args[0])
    avvisi = []
    testo = compila(cartella, libro, avvisi)
    for a in avvisi:
        print(a)
    rel = f'05-output/{comune.nome_file(libro["titolo"])}-completo.md'
    print('scritto', comune.scrivi(cartella, rel, testo))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except comune.ErroreMotore as e:
        comune.esci_con_errore(e)
```


Continua in [parte 4](ESPORTAZIONE_COMPLETA_4.md).

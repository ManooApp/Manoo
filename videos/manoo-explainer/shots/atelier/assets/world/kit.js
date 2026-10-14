// Manoo iso world — shared kit: palette, materials, primitives, easing, seeded random.
import * as THREE from "../vendor/three.module.js";
import { RoundedBoxGeometry } from "../vendor/RoundedBoxGeometry.js";

export { THREE };

// Palette (manoo.fr CSS variables) + derived model tones.
export const C = {
  encre: 0x101619,
  encre2: 0x1a242a,
  filetSombre: 0x2c383f,
  acier: 0x78868f,
  acierClair: 0xa8b4bb,
  papier: 0xf3f2ef,
  papier2: 0xe8e6e1,
  filet: 0xd6d4ce,
  orange: 0xf97316,
  orangeFonce: 0xd95f08,
  // model-only neutrals (tinted toward the paper/steel family)
  pierre: 0xcfccc5, // concrete / stone
  ombre: 0x3a464d, // dark steel parts
  peau: 0xd9cfc4, // figurine skin (neutral warm grey, faceless)
  vitre: 0x24323a, // unlit window glass
  vitreOn: 0xf6e9d6, // lit window glow (warm paper)
};

// ---------- materials ----------
const matCache = new Map();
export function mat(color, { rough = 0.86, metal = 0, emissive = 0x000000, emissiveIntensity = 1 } = {}) {
  const key = `${color}|${rough}|${metal}|${emissive}|${emissiveIntensity}`;
  if (!matCache.has(key)) {
    matCache.set(
      key,
      new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: metal, emissive, emissiveIntensity }),
    );
  }
  return matCache.get(key);
}
export const M = {
  papier: () => mat(C.papier),
  papier2: () => mat(C.papier2),
  pierre: () => mat(C.pierre),
  acier: () => mat(C.acier, { rough: 0.55, metal: 0.35 }),
  acierClair: () => mat(C.acierClair, { rough: 0.7, metal: 0.1 }),
  ombre: () => mat(C.ombre, { rough: 0.6, metal: 0.3 }),
  encre2: () => mat(C.encre2, { rough: 0.95 }),
  filetSombre: () => mat(C.filetSombre, { rough: 0.95 }),
  orange: () => mat(C.orange, { rough: 0.5, metal: 0.25 }),
  orangeMat: () => mat(C.orange, { rough: 0.8 }),
  orangeFonce: () => mat(C.orangeFonce, { rough: 0.8 }),
  peau: () => mat(C.peau, { rough: 0.9 }),
  vitre: () => mat(C.vitre, { rough: 0.35, metal: 0.2 }),
};

// ---------- geometry primitives (cached) ----------
const geoCache = new Map();
function cachedGeo(key, make) {
  if (!geoCache.has(key)) geoCache.set(key, make());
  return geoCache.get(key);
}
function finish(mesh, { cast = true, receive = true } = {}) {
  mesh.castShadow = cast;
  mesh.receiveShadow = receive;
  return mesh;
}
export function box(w, h, d, material, { r = 0.035, seg = 2, cast = true, receive = true } = {}) {
  const rr = Math.min(r, w / 2 - 1e-3, h / 2 - 1e-3, d / 2 - 1e-3);
  const geo =
    rr > 0.004
      ? cachedGeo(`rb${w}|${h}|${d}|${rr}|${seg}`, () => new RoundedBoxGeometry(w, h, d, seg, rr))
      : cachedGeo(`b${w}|${h}|${d}`, () => new THREE.BoxGeometry(w, h, d));
  return finish(new THREE.Mesh(geo, material), { cast, receive });
}
// box whose base sits on y=0 (handy for buildings / furniture)
export function boxUp(w, h, d, material, opts) {
  const m = box(w, h, d, material, opts);
  m.position.y = h / 2;
  const g = new THREE.Group();
  g.add(m);
  return g;
}
export function cyl(rTop, rBot, h, material, seg = 24, opts = {}) {
  const geo = cachedGeo(`c${rTop}|${rBot}|${h}|${seg}`, () => new THREE.CylinderGeometry(rTop, rBot, h, seg));
  return finish(new THREE.Mesh(geo, material), opts);
}
export function sph(r, material, seg = 20, opts = {}) {
  const geo = cachedGeo(`s${r}|${seg}`, () => new THREE.SphereGeometry(r, seg, Math.round(seg * 0.75)));
  return finish(new THREE.Mesh(geo, material), opts);
}
export function capsule(r, len, material, opts = {}) {
  const geo = cachedGeo(`cap${r}|${len}`, () => new THREE.CapsuleGeometry(r, len, 6, 14));
  return finish(new THREE.Mesh(geo, material), opts);
}
export function torus(R, r, arc, material, opts = {}) {
  const geo = cachedGeo(`t${R}|${r}|${arc}`, () => new THREE.TorusGeometry(R, r, 8, 28, arc));
  return finish(new THREE.Mesh(geo, material), opts);
}
// triangular prism (gable roofs, sawtooth roofs): width along x, depth along z, apex height h.
export function prism(w, h, d, material, apexX = 0.5, opts = {}) {
  const geo = cachedGeo(`p${w}|${h}|${d}|${apexX}`, () => {
    const s = new THREE.Shape();
    s.moveTo(-w / 2, 0);
    s.lineTo(w / 2, 0);
    s.lineTo(-w / 2 + w * apexX, h);
    s.lineTo(-w / 2, 0);
    const g = new THREE.ExtrudeGeometry(s, { depth: d, bevelEnabled: false });
    g.translate(0, 0, -d / 2);
    g.computeVertexNormals();
    return g;
  });
  return finish(new THREE.Mesh(geo, material), opts);
}
// flat rounded rectangle extruded along y (phone body, cards, slabs with big corner radii)
export function roundSlab(w, d, h, radius, material, { bevel = 0.04, opts = {} } = {}) {
  const geo = cachedGeo(`rs${w}|${d}|${h}|${radius}|${bevel}`, () => {
    const s = roundedRectShape(w, d, radius);
    const g = new THREE.ExtrudeGeometry(s, {
      depth: Math.max(0.001, h - bevel * 2),
      bevelEnabled: bevel > 0,
      bevelThickness: bevel,
      bevelSize: bevel,
      bevelSegments: 3,
      curveSegments: 12,
    });
    g.rotateX(-Math.PI / 2);
    g.translate(0, bevel, 0);
    g.computeVertexNormals();
    return g;
  });
  return finish(new THREE.Mesh(geo, material), opts);
}
export function roundedRectShape(w, d, r) {
  const s = new THREE.Shape();
  const x = -w / 2;
  const y = -d / 2;
  s.moveTo(x + r, y);
  s.lineTo(x + w - r, y);
  s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + d - r);
  s.quadraticCurveTo(x + w, y + d, x + w - r, y + d);
  s.lineTo(x + r, y + d);
  s.quadraticCurveTo(x, y + d, x, y + d - r);
  s.lineTo(x, y + r);
  s.quadraticCurveTo(x, y, x + r, y);
  return s;
}
// rounded-rect plane lying in XZ with 0..1 UVs (screens). +y facing.
export function roundedPlane(w, d, r, material) {
  const geo = cachedGeo(`rp${w}|${d}|${r}`, () => {
    const g = new THREE.ShapeGeometry(roundedRectShape(w, d, r), 16);
    const pos = g.attributes.position;
    const uv = new Float32Array(pos.count * 2);
    for (let i = 0; i < pos.count; i++) {
      uv[i * 2] = (pos.getX(i) + w / 2) / w;
      uv[i * 2 + 1] = (pos.getY(i) + d / 2) / d;
    }
    g.setAttribute("uv", new THREE.BufferAttribute(uv, 2));
    g.rotateX(-Math.PI / 2);
    return g;
  });
  return new THREE.Mesh(geo, material);
}

export function at(obj, x = 0, y = 0, z = 0, ry = 0) {
  obj.position.set(x, y, z);
  obj.rotation.y = ry;
  return obj;
}
export function grp(...children) {
  const g = new THREE.Group();
  children.forEach((c) => c && g.add(c));
  return g;
}

// ---------- seeded random ----------
export function rng(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ---------- time & easing ----------
export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const lerp = (a, b, p) => a + (b - a) * p;
export const prog = (t, a, b) => (b <= a ? (t >= b ? 1 : 0) : clamp((t - a) / (b - a)));
const easeCache = new Map();
export function ease(name, p) {
  if (!easeCache.has(name)) easeCache.set(name, window.gsap.parseEase(name));
  return easeCache.get(name)(clamp(p));
}
// eased progress of t through [a,b]
export const ep = (t, a, b, name = "power2.inOut") => ease(name, prog(t, a, b));
// a 0→1→0 envelope with in/out ramps (for flashes, labels, glows)
export function env(t, a, b, fadeIn = 0.2, fadeOut = 0.2, inEase = "power2.out", outEase = "power2.in") {
  if (t < a || t > b) return 0;
  const i = fadeIn > 0 ? ease(inEase, (t - a) / fadeIn) : 1;
  const o = fadeOut > 0 ? 1 - ease(outEase, (t - (b - fadeOut)) / fadeOut) : 1;
  return Math.min(i, t > b - fadeOut ? o : 1);
}
// piecewise keyframe track: keys = [[time, value, easeIntoThisKey], ...] (value: number or array)
export function track(keys, t) {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [t1, v1, e = "power2.inOut"] = keys[i];
    const [t0, v0] = keys[i - 1];
    if (t <= t1) {
      const p = ease(e, prog(t, t0, t1));
      if (Array.isArray(v0)) return v0.map((x, k) => lerp(x, v1[k], p));
      return lerp(v0, v1, p);
    }
  }
  return keys[keys.length - 1][1];
}
// deterministic smooth noise in [-1,1] (sum of sines) for flicker / drift
export function wobble(t, seed = 0) {
  return (
    Math.sin(t * 1.7 + seed * 1.3) * 0.5 +
    Math.sin(t * 2.9 + seed * 2.1) * 0.3 +
    Math.sin(t * 5.3 + seed * 0.7) * 0.2
  );
}
export function flicker(t, seed = 0) {
  // fast pseudo-random flicker for the weld arc, deterministic per frame time
  const x = Math.sin((t * 61.7 + seed) * 12.9898) * 43758.5453;
  return x - Math.floor(x);
}

// ---------- canvas helpers ----------
export function makeCanvas(w, h) {
  const c = document.createElement("canvas");
  c.width = w;
  c.height = h;
  return c;
}
export function canvasTexture(canvas) {
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  tex.generateMipmaps = true;
  tex.minFilter = THREE.LinearMipmapLinearFilter;
  return tex;
}
export function hex(c) {
  return "#" + c.toString(16).padStart(6, "0");
}
// soft radial glow sprite texture (shared)
let _glowTex = null;
export function glowTexture() {
  if (_glowTex) return _glowTex;
  const c = makeCanvas(128, 128);
  const g = c.getContext("2d");
  const grad = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  grad.addColorStop(0, "rgba(255,255,255,1)");
  grad.addColorStop(0.18, "rgba(255,255,255,0.75)");
  grad.addColorStop(0.45, "rgba(255,255,255,0.22)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grad;
  g.fillRect(0, 0, 128, 128);
  _glowTex = new THREE.CanvasTexture(c);
  return _glowTex;
}
export function glowSprite(color, size) {
  const m = new THREE.SpriteMaterial({
    map: glowTexture(),
    color,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    toneMapped: false,
  });
  const s = new THREE.Sprite(m);
  s.scale.set(size, size, 1);
  return s;
}

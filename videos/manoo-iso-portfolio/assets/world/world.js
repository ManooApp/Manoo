// Manoo — isometric world. One continuous Three.js scene driven by HyperFrames time (hf-seek).
import {
  THREE, C, M, mat, box, cyl, sph, at, grp, rng, clamp, lerp, prog, ease, ep, env, wobble, flicker,
  makeCanvas, canvasTexture, glowSprite,
} from "./kit.js";
import * as MD from "./models.js";
import * as SC from "./screens.js";
import { RoomEnvironment } from "../vendor/RoomEnvironment.js";

const CU = window.CUES;
const W = 1920;
const H = 1080;
const ASPECT = W / H;
const SQ2 = Math.SQRT2;
const uv2xz = (u, v) => [(u + v) / SQ2, (v - u) / SQ2];
const POS = {
  A: uv2xz(-22, -17), B: uv2xz(0, -17), C: uv2xz(22, -17),
  D: uv2xz(-22, 17), E: uv2xz(0, 17), F: uv2xz(22, 17),
};
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

// ---------------------------------------------------------------------------
// renderer / scene / camera
// ---------------------------------------------------------------------------
const canvas = document.getElementById("world-gl");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.setClearColor(0x000000, 0);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
const envTex = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environment = envTex;
scene.environmentIntensity = 0.22;

const camera = new THREE.OrthographicCamera(-10, 10, 10, -10, -300, 600);
const hemi = new THREE.HemisphereLight(0xf4f4f2, 0x1a242a, 0.85);
scene.add(hemi);
const key = new THREE.DirectionalLight(0xfff6ec, 3.0);
key.castShadow = true;
key.shadow.mapSize.set(4096, 4096);
key.shadow.bias = -0.00035;
key.shadow.normalBias = 0.03;
key.shadow.radius = 3;
scene.add(key, key.target);
const LDIR = V3(0.32, 1.0, 0.62).normalize();

// faint drafting grid far below the islands
{
  const c = makeCanvas(128, 128);
  const g = c.getContext("2d");
  g.fillStyle = "rgba(168,180,187,0.55)";
  g.beginPath();
  g.arc(64, 64, 3.2, 0, Math.PI * 2);
  g.fill();
  const tex = canvasTexture(c);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(160, 160);
  const plane = new THREE.Mesh(
    new THREE.PlaneGeometry(320, 320),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity: 0.28, depthWrite: false, toneMapped: false }),
  );
  plane.rotation.x = -Math.PI / 2;
  plane.position.y = -9;
  plane.renderOrder = -1;
  scene.add(plane);
}

// ---------------------------------------------------------------------------
// island assembly helpers
// ---------------------------------------------------------------------------
function makeIsland(name, floorKind, seed) {
  const g = new THREE.Group();
  g.name = name;
  const parts = [];
  const slab = box(10, 1.3, 10, mat(C.encre2, { rough: 0.95 }), { r: 0.2, seg: 3 });
  slab.position.y = -0.71;
  const slabG = grp(slab);
  g.add(slabG);
  const tex = MD.floorTexture(floorKind, seed);
  const tileMat = new THREE.MeshStandardMaterial({ color: 0xdcd8d0, map: tex, roughness: 0.92 });
  const N = 5;
  const S = 9.7 / N;
  for (let i = 0; i < N; i++)
    for (let j = 0; j < N; j++) {
      const geo = new THREE.BoxGeometry(S - 0.03, 0.12, S - 0.03);
      // per-tile UV offset so the texture is continuous across tiles
      const uvA = geo.attributes.uv;
      for (let k = 0; k < uvA.count; k++) uvA.setXY(k, (uvA.getX(k) + i) / N, (uvA.getY(k) + (N - 1 - j)) / N);
      const tile = new THREE.Mesh(geo, tileMat);
      tile.receiveShadow = true;
      tile.position.set(-4.85 + S / 2 + i * S, -0.06, -4.85 + S / 2 + j * S);
      const tg = grp(tile);
      g.add(tg);
      parts.push({ obj: tg, kind: "tile", order: (i + j) / (2 * (N - 1)) });
    }
  return { g, parts, slab: slabG, tileMat, add(obj, order, kind = "pop") { g.add(obj); parts.push({ obj, kind, order }); return obj; } };
}
function captureBase(isl) {
  isl.parts.forEach((p) => {
    p.base = p.obj.position.clone();
    p.baseScale = p.obj.scale.clone();
  });
}
function assemble(isl, t, t0, t1) {
  const vis = t >= t0 - 0.05;
  isl.g.visible = vis;
  if (!vis) return;
  // slab rises
  const ps = ep(t, t0, t0 + 0.55, "power3.out");
  isl.slab.position.y = lerp(-7, 0, ps);
  const span = t1 - t0;
  for (const p of isl.parts) {
    const st = t0 + 0.15 + p.order * (span - 0.6);
    if (p.kind === "tile") {
      const k = ep(t, st, st + 0.42, "back.out(1.3)");
      p.obj.position.y = p.base.y + (1 - k) * 3.2;
      p.obj.visible = t >= st;
    } else if (p.kind === "rise") {
      const k = ep(t, st, st + 0.6, "back.out(1.2)");
      p.obj.scale.set(p.baseScale.x, Math.max(0.001, p.baseScale.y * k), p.baseScale.z);
      p.obj.visible = t >= st;
    } else {
      const k = ep(t, st, st + 0.5, "back.out(2.0)");
      const s = Math.max(0.001, k);
      p.obj.scale.set(p.baseScale.x * s, p.baseScale.y * s, p.baseScale.z * s);
      p.obj.position.y = p.base.y + (1 - ep(t, st, st + 0.35, "power2.out")) * 1.4;
      p.obj.visible = t >= st;
    }
  }
}

// per-island dimming (audience islands start "unseen")
function islandize(group) {
  const map = new Map();
  group.traverse((o) => {
    if (!o.isMesh) return;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    const next = mats.map((m) => {
      if (!m.isMeshStandardMaterial) return m;
      if (!map.has(m)) {
        const c = m.clone();
        c.userData.base = m.color.clone();
        map.set(m, c);
      }
      return map.get(m);
    });
    o.material = Array.isArray(o.material) ? next : next[0];
  });
  const list = [...map.values()];
  return (k) => list.forEach((m) => m.color.copy(m.userData.base).multiplyScalar(k));
}

// ---------------------------------------------------------------------------
// TRADE ISLANDS
// ---------------------------------------------------------------------------
const islands = {};

// --- A: atelier de métallerie
{
  const isl = makeIsland("A", "tiles", 3);
  const walls = MD.cornerWalls(10, 10, 3.1, { color: C.papier2 });
  isl.add(walls, 0.05, "rise");
  const peg = MD.pegboard(2.6, 1.3);
  at(peg, -1.0, 1.15, -4.55);
  isl.add(peg, 0.25);
  const shelf = MD.shelfUnit(1.6, 2.0);
  at(shelf, -4.25, 0, -2.4, Math.PI / 2);
  isl.add(shelf, 0.3);
  const gas = MD.gasBottles();
  at(gas, -3.5, 0, -3.7, 0.3);
  isl.add(gas, 0.35);
  const rack = MD.barRack();
  at(rack, 2.5, 0, -4.0);
  isl.add(rack, 0.4);
  const bench = MD.workbench({ w: 2.6, d: 1.0 });
  at(bench, -3.0, 0, 1.6, Math.PI / 2);
  isl.add(bench, 0.5);
  const anv = MD.anvil();
  at(anv, 3.5, 0, -0.6, -0.4);
  isl.add(anv, 0.55);
  const gateM = MD.gate();
  at(gateM, 0.0, 0, -1.25);
  isl.add(gateM, 0.62, "rise");
  // métallier
  const fig = MD.figurine({ top: C.acierClair, bottom: C.ombre, mask: true, hair: "short" });
  isl.add(fig.root, 0.7);
  // welding torch in the right hand
  const torch = grp(
    at(cyl(0.035, 0.035, 0.32, mat(C.ombre, { rough: 0.5, metal: 0.4 }), 10), 0, -0.1, 0),
    at(cyl(0.02, 0.012, 0.12, mat(C.acier, { rough: 0.4, metal: 0.6 }), 8), 0, -0.3, 0),
  );
  fig.armR.hand.add(torch);
  isl.g.position.set(POS.A[0], 0, POS.A[1]);
  isl.fig = fig;
  isl.torch = torch;
  isl.gate = gateM;
  isl.extra = { bench, anv, rack };
  islands.A = isl;
}

// --- B: chantier (maçonnerie)
{
  const isl = makeIsland("B", "earth", 5);
  const walls = MD.brickWalls();
  at(walls, -3.3, 0, -3.1);
  isl.add(walls, 0.12, "rise");
  const scaf = MD.scaffolding(4.6, 2.7);
  at(scaf, -3.0, 0, -2.7);
  isl.add(scaf, 0.45);
  const mixer = MD.cementMixer();
  at(mixer, 2.7, 0, 0.6, -0.6);
  isl.add(mixer, 0.5);
  const barrow = MD.wheelbarrow();
  at(barrow, 0.2, 0, 3.1, 0.5);
  isl.add(barrow, 0.55);
  const pal = MD.pallet(true);
  at(pal, 3.0, 0, -2.8, 0.2);
  isl.add(pal, 0.4);
  const pal2 = MD.pallet(true);
  at(pal2, 3.2, 0, 3.2, -0.3);
  isl.add(pal2, 0.6);
  const fig = MD.figurine({ top: C.papier2, bottom: C.acier, hat: "hardhat", hair: "bun" });
  isl.add(fig.root, 0.7);
  isl.g.position.set(POS.B[0], 0, POS.B[1]);
  isl.fig = fig;
  isl.walls = walls;
  isl.extra = { scaf, mixer, pal };
  islands.B = isl;
}

// --- C: atelier d'ébénisterie
{
  const isl = makeIsland("C", "planks", 8);
  const walls = MD.cornerWalls(10, 10, 3.1, { color: C.papier2 });
  isl.add(walls, 0.05, "rise");
  const platform = box(2.6, 0.12, 1.5, mat(C.papier, { rough: 0.9 }), { r: 0.03 });
  platform.position.y = 0.06;
  const plat = grp(platform);
  at(plat, -0.3, 0, -1.6);
  isl.add(plat, 0.4);
  const cab = MD.cabinet();
  at(cab, -0.3, 0.12, -1.6);
  isl.add(cab, 0.62, "rise");
  const bench = MD.workbench({ w: 2.8, d: 1.0, top: C.papier2, legs: C.acier });
  at(bench, -3.0, 0, 1.6, Math.PI / 2);
  isl.add(bench, 0.5);
  const plane = grp(at(box(0.5, 0.14, 0.16, mat(C.ombre, { rough: 0.5, metal: 0.4 }), { r: 0.03 }), 0, 0.07, 0));
  at(plane, -3.0, 1.0, 1.0, 0.4);
  isl.add(plane, 0.58);
  const sh = MD.shavings(9, 16, 1.4);
  at(sh, -2.0, 0, 2.0);
  isl.add(sh, 0.6);
  const rack = MD.lumberRack();
  at(rack, 2.3, 0, -4.1);
  isl.add(rack, 0.35);
  const shelf = MD.shelfUnit(1.4, 1.8);
  at(shelf, -4.25, 0, -2.6, Math.PI / 2);
  isl.add(shelf, 0.3);
  const fig = MD.figurine({ top: C.acierClair, bottom: C.ombre, apron: true, hat: "beanie" });
  isl.add(fig.root, 0.7);
  isl.g.position.set(POS.C[0], 0, POS.C[1]);
  isl.fig = fig;
  isl.cab = cab;
  isl.extra = { bench, rack, plat };
  islands.C = isl;
}

// ---------------------------------------------------------------------------
// AUDIENCE ISLANDS
// ---------------------------------------------------------------------------
function windowMaterial() {
  return new THREE.MeshStandardMaterial({ color: C.vitre, roughness: 0.35, metalness: 0.2, emissive: 0xf6e6cf, emissiveIntensity: 0 });
}
{
  const isl = makeIsland("D", "asphalt", 12);
  const win = windowMaterial();
  const fac = MD.factory(win);
  at(fac, -1.3, 0, -1.9);
  isl.add(fac, 0.1, "rise");
  const p1 = MD.pallet(true);
  at(p1, 3.6, 0, 2.9, 0.3);
  isl.add(p1, 0.5);
  const r1 = MD.figurine({ top: C.papier, bottom: C.ombre, hair: "short" });
  const r2 = MD.figurine({ top: C.acier, bottom: C.encre2, hair: "bun" });
  at(r1.root, 1.6, 0, 2.6, 2.3);
  at(r2.root, 0.4, 0, 3.0, 0.9);
  isl.add(r1.root, 0.62);
  isl.add(r2.root, 0.68);
  isl.g.position.set(POS.D[0], 0, POS.D[1]);
  isl.win = win;
  isl.figs = [r1, r2];
  islands.D = isl;
}
{
  const isl = makeIsland("E", "courtyard", 14);
  const win = windowMaterial();
  const sch = MD.school(win);
  at(sch, -0.6, 0, -2.7);
  isl.add(sch, 0.1, "rise");
  const t1 = MD.tree({ h: 2.6, r: 0.85 });
  at(t1, 3.7, 0, -0.6);
  isl.add(t1, 0.45);
  const t2 = MD.tree({ h: 2.2, r: 0.7, kind: "cone" });
  at(t2, -3.9, 0, 1.2);
  isl.add(t2, 0.5);
  const teacher = MD.figurine({ top: C.ombre, bottom: C.encre2, hair: "short" });
  const s1 = MD.figurine({ top: C.papier, bottom: C.acier, hair: "bun", scale: 1.1 });
  const s2 = MD.figurine({ top: C.acierClair, bottom: C.ombre, hat: "beanie", scale: 1.1 });
  const s3 = MD.figurine({ top: C.papier2, bottom: C.ombre, hair: "short", scale: 1.1 });
  at(teacher.root, 2.6, 0, 1.4, -2.4);
  at(s1.root, 0.9, 0, 2.9, 3.0);
  at(s2.root, -0.2, 0, 2.2, 2.6);
  at(s3.root, -1.3, 0, 3.1, 2.9);
  [teacher, s1, s2, s3].forEach((f, i) => isl.add(f.root, 0.6 + i * 0.05));
  isl.g.position.set(POS.E[0], 0, POS.E[1]);
  isl.win = win;
  isl.figs = [teacher, s1, s2, s3];
  islands.E = isl;
}
{
  const isl = makeIsland("F", "lawn", 16);
  const win = windowMaterial();
  const hs = MD.house(win);
  at(hs, -1.7, 0, -1.8);
  isl.add(hs, 0.1, "rise");
  const fz = MD.fence(8.6, { posts: 10 });
  at(fz, -4.3, 0, 4.45);
  isl.add(fz, 0.4);
  const fx = MD.fence(8.6, { posts: 10 });
  at(fx, 4.45, 0, 4.3, Math.PI / 2);
  isl.add(fx, 0.42);
  const tr = MD.tree({ h: 2.8, r: 0.95 });
  at(tr, 3.0, 0, -3.0);
  isl.add(tr, 0.45);
  const bn = MD.bench();
  at(bn, 2.0, 0, 1.6);
  isl.add(bn, 0.5);
  const client = MD.figurine({ top: C.papier, bottom: C.acier, hair: "bun" });
  at(client.root, 2.0, 0, 1.75);
  isl.add(client.root, 0.62);
  // tablet in the client's hands
  const tab = grp(
    box(0.5, 0.36, 0.03, mat(C.encre, { rough: 0.35, metal: 0.4 }), { r: 0.02 }),
    at(new THREE.Mesh(new THREE.PlaneGeometry(0.44, 0.3), new THREE.MeshBasicMaterial({ color: 0xf3f2ef, toneMapped: false })), 0, 0, -0.017),
  );
  tab.children[1].rotation.y = Math.PI;
  tab.rotation.x = -0.9;
  client.phoneHold.add(tab);
  isl.g.position.set(POS.F[0], 0, POS.F[1]);
  isl.win = win;
  isl.figs = [client];
  islands.F = isl;
}
for (const k of ["D", "E", "F"]) islands[k].setLight = islandize(islands[k].g);
Object.values(islands).forEach((isl) => {
  captureBase(isl);
  scene.add(isl.g);
});

// ---------------------------------------------------------------------------
// HUB: plinth + giant phone + glossy icon bubbles
// ---------------------------------------------------------------------------
const PROFILES = [
  { initials: "JR", name: "Jules R.", trade: "BAC PRO MÉTALLERIE · 2E ANNÉE", label: "MÉTALLERIE" },
  { initials: "LM", name: "Lucas M.", trade: "CAP MAÇONNERIE · 2E ANNÉE", label: "CHANTIER" },
  { initials: "CD", name: "Clara D.", trade: "CAP ÉBÉNISTE · 1RE ANNÉE", label: "ARTISANAT" },
];
const ui = { canvas: null, tex: null };
const hub = new THREE.Group();
const plinth = MD.plinth(7.6, 1.2);
hub.add(plinth);
let phone = null;
scene.add(hub);

const bubbles = [];
function makeBubble(icon, r = 0.78) {
  const g = new THREE.Group();
  const sphMat = new THREE.MeshPhysicalMaterial({
    color: 0xffffff, roughness: 0.16, metalness: 0.0, clearcoat: 1, clearcoatRoughness: 0.06, envMapIntensity: 1.6,
  });
  const s = new THREE.Mesh(new THREE.SphereGeometry(r, 40, 28), sphMat);
  s.castShadow = true;
  g.add(s);
  const face = new THREE.Group();
  const tex = canvasTexture(SC.iconCanvas(icon));
  const disc = new THREE.Mesh(
    new THREE.CircleGeometry(r * 0.62, 40),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true, toneMapped: false, depthWrite: false }),
  );
  disc.position.z = r + 0.02;
  disc.renderOrder = 6;
  face.add(disc);
  g.add(face);
  g.userData.face = face;
  return g;
}
const BUBBLES = [
  ["camera", [3.6, 3.0, -5.6], 0.0],
  ["image", [5.3, 2.4, -2.6], 0.08],
  ["hammer", [-5.7, 1.6, 2.4], 0.16],
  ["bricks", [5.6, 2.6, -0.1], 0.24],
  ["saw", [-4.5, 2.2, 5.3], 0.32],
  ["helmet", [-1.2, 1.4, 7.4], 0.4],
  ["plus", [0.2, 3.6, -7.2], 0.48],
];
BUBBLES.forEach(([icon, p, d], i) => {
  const b = makeBubble(icon, i === 6 ? 0.8 : 1.0);
  b.position.set(...p);
  b.userData.base = V3(...p);
  b.userData.delay = d;
  b.userData.seed = i * 1.7;
  scene.add(b);
  bubbles.push(b);
});

// ---------------------------------------------------------------------------
// photos (render-to-texture at init)
// ---------------------------------------------------------------------------
const photoRT = new THREE.WebGLRenderTarget(960, 720, { samples: 4, colorSpace: THREE.SRGBColorSpace });
const photoCam = new THREE.PerspectiveCamera(36, 960 / 720, 0.1, 200);
const flashLight = new THREE.PointLight(0xffffff, 0, 30, 1.6);
scene.add(flashLight);
function shoot(isl, camLocal, lookLocal, fov = 36) {
  const pos = isl.g.localToWorld(V3(...camLocal));
  const look = isl.g.localToWorld(V3(...lookLocal));
  photoCam.fov = fov;
  photoCam.aspect = 960 / 720;
  photoCam.updateProjectionMatrix();
  photoCam.position.copy(pos);
  photoCam.lookAt(look);
  flashLight.position.copy(pos).add(V3(0, 0.3, 0));
  // flash falls off with distance: keep close-ups from blowing out
  const dist = pos.distanceTo(look);
  flashLight.intensity = Math.min(26, Math.max(3, 2.4 * dist * dist));
  renderer.setRenderTarget(photoRT);
  renderer.setClearColor(0xe9e6e0, 1);
  renderer.clear();
  renderer.render(scene, photoCam);
  const buf = new Uint8Array(960 * 720 * 4);
  renderer.readRenderTargetPixels(photoRT, 0, 0, 960, 720, buf);
  renderer.setRenderTarget(null);
  renderer.setClearColor(0x000000, 0);
  flashLight.intensity = 0;
  const c = makeCanvas(960, 720);
  const g = c.getContext("2d");
  const id = g.createImageData(960, 720);
  for (let y = 0; y < 720; y++) id.data.set(buf.subarray((719 - y) * 960 * 4, (720 - y) * 960 * 4), y * 960 * 4);
  g.putImageData(id, 0, 0);
  return SC.gradePhoto(c);
}

// ---------------------------------------------------------------------------
// FX: sparks, glows, paths, pulse rings, cards
// ---------------------------------------------------------------------------
const weldGlow = glowSprite(0xffd2a6, 1.4);
scene.add(weldGlow);
const weldLight = new THREE.PointLight(0xffb070, 0, 14, 1.4);
scene.add(weldLight);
const camFlash = glowSprite(0xffffff, 2.4);
scene.add(camFlash);

const SPARK_N = 220;
const sparkData = [];
{
  const r = rng(42);
  for (let i = 0; i < SPARK_N; i++) {
    const a = r() * Math.PI * 2;
    const sp = 1.6 + r() * 3.4;
    sparkData.push({
      t0: 4.25 + r() * 1.55,
      life: 0.35 + r() * 0.75,
      vx: Math.cos(a) * sp * 0.75,
      vz: Math.sin(a) * sp * 0.75 + 1.0,
      vy: 0.6 + r() * 3.4,
    });
  }
}
const sparkPos = new Float32Array(SPARK_N * 6);
const sparkCol = new Float32Array(SPARK_N * 6);
const sparkGeo = new THREE.BufferGeometry();
sparkGeo.setAttribute("position", new THREE.BufferAttribute(sparkPos, 3));
sparkGeo.setAttribute("color", new THREE.BufferAttribute(sparkCol, 3));
const sparks = new THREE.LineSegments(
  sparkGeo,
  new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false }),
);
sparks.frustumCulled = false;
scene.add(sparks);
const sparkPtsGeo = new THREE.BufferGeometry();
const sparkPts = new Float32Array(SPARK_N * 3);
const sparkPtsCol = new Float32Array(SPARK_N * 3);
sparkPtsGeo.setAttribute("position", new THREE.BufferAttribute(sparkPts, 3));
sparkPtsGeo.setAttribute("color", new THREE.BufferAttribute(sparkPtsCol, 3));
const sparkPoints = new THREE.Points(
  sparkPtsGeo,
  new THREE.PointsMaterial({ size: 5, sizeAttenuation: false, vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false }),
);
sparkPoints.frustumCulled = false;
scene.add(sparkPoints);

function updateSparks(t, origin) {
  const g = 9.8;
  for (let i = 0; i < SPARK_N; i++) {
    const s = sparkData[i];
    const age = t - s.t0;
    const o6 = i * 6;
    const o3 = i * 3;
    if (age < 0 || age > s.life) {
      sparkPos.fill(0, o6, o6 + 6);
      sparkCol.fill(0, o6, o6 + 6);
      sparkPts.fill(0, o3, o3 + 3);
      sparkPtsCol.fill(0, o3, o3 + 3);
      continue;
    }
    const at = (a) => {
      let y = s.vy * a - 0.5 * g * a * a;
      let x = s.vx * a;
      let z = s.vz * a;
      const groundY = -origin.y;
      if (y < groundY) {
        // single damped bounce
        const tb = (s.vy + Math.sqrt(s.vy * s.vy + 2 * g * -groundY)) / g;
        const a2 = a - tb;
        y = groundY + Math.max(0, s.vy * 0.3 * a2 - 0.5 * g * a2 * a2);
        x = s.vx * tb + s.vx * 0.5 * a2;
        z = s.vz * tb + s.vz * 0.5 * a2;
      }
      return [origin.x + x, origin.y + y, origin.z + z];
    };
    const p1 = at(age);
    const p0 = at(Math.max(0, age - 0.045));
    sparkPos.set(p0, o6);
    sparkPos.set(p1, o6 + 3);
    const f = 1 - age / s.life;
    const c = [1.0 * f + 0.2, 0.62 * f * f + 0.15, 0.22 * f * f * f];
    sparkCol.set([c[0] * 0.4, c[1] * 0.4, c[2] * 0.4], o6);
    sparkCol.set(c, o6 + 3);
    sparkPts.set(p1, o3);
    sparkPtsCol.set(c, o3);
  }
  sparkGeo.attributes.position.needsUpdate = true;
  sparkGeo.attributes.color.needsUpdate = true;
  sparkPtsGeo.attributes.position.needsUpdate = true;
  sparkPtsGeo.attributes.color.needsUpdate = true;
}

// capture cards & audience cards are created after photos exist (init)
const cards = {};
const paths = {};
const pulses = {};

// ---------------------------------------------------------------------------
// camera choreography
// ---------------------------------------------------------------------------
function islandPoint(k, x, y, z) {
  const p = POS[k];
  return [p[0] + x, y, p[1] + z];
}
// pose: [tx, ty, tz, halfHeight, azDeg, elDeg]
let PO = {};
function definePoses() {
  const A = (x, y, z) => islandPoint("A", x, y, z);
  const B = (x, y, z) => islandPoint("B", x, y, z);
  const Cc = (x, y, z) => islandPoint("C", x, y, z);
  PO = {
    aBuild: [...A(0, 0.9, 0), 6.0, 45, 33],
    aBuilt: [...A(0, 1.0, 0), 5.5, 43, 32],
    aMed: [...A(0.7, 1.25, -0.2), 3.35, 36, 29],
    aCard: [...A(0.2, 3.1, 0.6), 4.55, 40, 30],
    b: [...B(0.2, 2.6, 0.6), 5.4, 45, 31],
    c: [...Cc(0.2, 2.6, 0.6), 5.4, 45, 31],
    trades: [...islandPoint("B", 0, 2.4, 0), 17.6, 45, 33],
    hubTilt: [0, 0.5, 0.5, 6.5, 13, 60],
    hubUI: [1.0, 0.5, 0.25, 5.65, 7, 63],
    aud: [...uv2xz(0, 9), 15.6, 45, 33],
    d: [...islandPoint("D", 0.5, 3.0, 0.6), 6.0, 45, 31],
    e: [...islandPoint("E", 0.3, 3.1, 0.4), 6.0, 45, 31],
    f: [...islandPoint("F", 0.6, 2.8, 0.6), 6.0, 45, 31],
    wide: [0, 2.2, 0, 22.5, 45, 33],
    wide2: [0, 2.2, 0, 21.4, 39, 34],
  };
  // fix: aud uses [x, z] from uv2xz → insert y
  PO.aud = [PO.aud[0], 1.6, PO.aud[1], 15.6, 45, 33];
}
// keyframes: [time, poseName | pose, ease]
let CAMKEYS = [];
function defineCamKeys() {
  CAMKEYS = [
    [0, "aBuild"],
    [CU.windowOpen, "aBuild"],
    [5.4, "aBuilt", "power2.out"],
    [8.35, "aMed", "power2.inOut"],
    [8.9, "aMed", "none"],
    [9.6, "aCard", "power3.out"],
    [CU.whipAB, "aCard", "none"],
    [CU.whipAB + 0.26, "b", "power3.inOut"],
    [CU.whipBC, "b", "sine.inOut"],
    [CU.whipBC + 0.24, "c", "power3.inOut"],
    [CU.pullback, "c", "sine.inOut"],
    [13.35, "trades", "power3.inOut"],
    [14.3, "hubTilt", "power3.inOut"],
    [18.95, "hubUI", "sine.inOut"],
    [20.55, "aud", "power3.inOut"],
    [22.45, "aud", "sine.inOut"],
    [22.95, "d", "power4.out"],
    [24.32, "d", "sine.inOut"],
    [24.58, "e", "power3.inOut"],
    [26.42, "e", "sine.inOut"],
    [26.68, "f", "power3.inOut"],
    [27.95, "f", "sine.inOut"],
    [29.2, "wide", "power3.inOut"],
    [33.0, "wide2", "sine.inOut"],
  ];
}
function camState(t) {
  const keys = CAMKEYS;
  const get = (k) => (typeof k === "string" ? PO[k] : k);
  if (t <= keys[0][0]) return get(keys[0][1]).slice();
  for (let i = 1; i < keys.length; i++) {
    if (t <= keys[i][0]) {
      const a = get(keys[i - 1][1]);
      const b = get(keys[i][1]);
      const p = ease(keys[i][2] || "power2.inOut", prog(t, keys[i - 1][0], keys[i][0]));
      // interpolate zoom in log space so dives feel uniform
      const out = a.map((v, j) => lerp(v, b[j], p));
      out[3] = Math.exp(lerp(Math.log(a[3]), Math.log(b[3]), p));
      return out;
    }
  }
  return get(keys[keys.length - 1][1]).slice();
}
const _target = V3(0, 0, 0);
function applyCamera(t) {
  const s = camState(t);
  // micro drift so holds never die (multi-phase-camera)
  const dz = 0.012 * s[3];
  let sx = Math.sin(t * 0.55) * dz;
  let sy = Math.sin(t * 0.55 * 1.3 + 1.1) * dz * 0.6;
  // flash shakes
  for (const ft of [CU.flashA, CU.flashB, CU.flashC]) {
    const a = t - ft;
    if (a > 0 && a < 0.35) {
      const k = (1 - a / 0.35) * 0.035 * s[3];
      sx += Math.sin(a * 90) * k;
      sy += Math.cos(a * 70) * k;
    }
  }
  const az = (s[4] * Math.PI) / 180;
  const el = (s[5] * Math.PI) / 180;
  _target.set(s[0], s[1], s[2]);
  const dir = V3(Math.cos(el) * Math.sin(az), Math.sin(el), Math.cos(el) * Math.cos(az));
  camera.position.copy(_target).addScaledVector(dir, 120);
  camera.up.set(0, 1, 0);
  camera.lookAt(_target);
  // screen-space drift: shift along camera right/up
  const right = V3(1, 0, 0).applyQuaternion(camera.quaternion);
  const up = V3(0, 1, 0).applyQuaternion(camera.quaternion);
  camera.position.addScaledVector(right, sx).addScaledVector(up, sy);
  const hh = s[3];
  camera.left = -hh * ASPECT;
  camera.right = hh * ASPECT;
  camera.top = hh;
  camera.bottom = -hh;
  camera.updateProjectionMatrix();
  camera.updateMatrixWorld();
  // shadow camera follows the view
  const half = hh * ASPECT * 1.25 + 5;
  key.target.position.copy(_target);
  key.position.copy(_target).addScaledVector(LDIR, 60);
  const sc = key.shadow.camera;
  sc.left = -half;
  sc.right = half;
  sc.top = half;
  sc.bottom = -half;
  sc.near = 1;
  sc.far = 160;
  sc.updateProjectionMatrix();
  return s;
}
const _p = V3(0, 0, 0);
function project(v) {
  _p.copy(v).project(camera);
  return [(_p.x * 0.5 + 0.5) * W, (-_p.y * 0.5 + 0.5) * H];
}

// ---------------------------------------------------------------------------
// figure choreography
// ---------------------------------------------------------------------------
const P = MD.POSES;
function poseBlend(seq, t) {
  // seq: [[time, pose], ...] eased transitions between consecutive poses
  let cur = seq[0][1];
  for (let i = 1; i < seq.length; i++) {
    const [t1, p1, dur = 0.45, e = "power2.inOut"] = seq[i];
    if (t >= t1) {
      const k = ease(e, prog(t, t1, t1 + dur));
      cur = MD.lerpPose(cur, p1, k);
    }
  }
  return cur;
}
function faceYaw(fromX, fromZ, toX, toZ) {
  return Math.atan2(toX - fromX, toZ - fromZ);
}
function updateFigures(t) {
  // --- A: métallier
  {
    const isl = islands.A;
    const f = isl.fig;
    const weld = [0.43, 1.12, -1.19];
    const p0 = [1.25, -0.15];
    const p1 = [2.05, 1.05];
    const walk = ep(t, 5.85, 6.55, "power2.inOut");
    const x = lerp(p0[0], p1[0], walk);
    const z = lerp(p0[1], p1[1], walk);
    f.root.position.set(x, 0, z);
    f.root.rotation.y = faceYaw(x, z, weld[0], weld[2]);
    const stride = Math.sin(walk * Math.PI * 3) * 0.45 * Math.sin(walk * Math.PI);
    let pose = poseBlend(
      [
        [0, P.weld],
        [5.75, { ...P.idle, mask: 1, hx: -0.05 }, 0.4],
        [6.45, P.photo, 0.55, "power3.out"],
        [9.15, { ...P.photo, hx: 0.42, rsx: -1.05, lsx: -1.05 }, 0.5],
      ],
      t,
    );
    pose = { ...pose, mask: t < 5.6 ? 0 : ep(t, 5.6, 5.95, "back.out(1.6)") };
    pose.legL += stride;
    pose.legR -= stride;
    if (t < 5.75) {
      pose.lean += wobble(t * 3, 1) * 0.02;
      pose.rsx += wobble(t * 7, 2) * 0.04;
    }
    MD.setPose(f, pose);
    isl.torch.visible = t < 5.95;
    const ph = ep(t, 6.25, 6.5, "back.out(2)");
    f.phone.visible = ph > 0.01;
    f.phone.scale.setScalar(Math.max(0.001, ph));
  }
  // --- B: apprentie maçonne
  {
    const isl = islands.B;
    const f = isl.fig;
    const x = 1.7, z = 1.5;
    f.root.position.set(x, 0, z);
    f.root.rotation.y = faceYaw(x, z, -2.0, -2.2);
    const pose = poseBlend(
      [
        [0, { ...P.idle, hx: 0.25, rsx: -0.7, rel: -0.9 }],
        [CU.chantier - 0.2, P.photo, 0.4, "power3.out"],
        [CU.flashB + 0.55, { ...P.photo, hx: 0.42, rsx: -1.05, lsx: -1.05 }, 0.45],
      ],
      t,
    );
    MD.setPose(f, pose);
    f.phone.visible = true;
  }
  // --- C: ébéniste
  {
    const isl = islands.C;
    const f = isl.fig;
    const x = 1.8, z = 1.3;
    f.root.position.set(x, 0, z);
    f.root.rotation.y = faceYaw(x, z, -0.3, -1.6);
    const pose = poseBlend(
      [
        [0, { ...P.idle, hx: 0.2 }],
        [CU.ouvrage - 0.05, P.photo, 0.4, "power3.out"],
        [CU.flashC + 0.55, { ...P.photo, hx: 0.42, rsx: -1.05, lsx: -1.05 }, 0.45],
      ],
      t,
    );
    MD.setPose(f, pose);
    f.phone.visible = t > CU.ouvrage - 0.1;
  }
  // --- audiences look up at their card
  const look = (isl, tLook, cardLocal, i0 = 0) => {
    isl.figs.forEach((f, i) => {
      const base = f.root.userData.baseYaw ?? (f.root.userData.baseYaw = f.root.rotation.y);
      const tt = tLook + i * 0.08 + i0;
      const k = ep(t, tt, tt + 0.5, "power2.inOut");
      const yaw = faceYaw(f.root.position.x, f.root.position.z, cardLocal[0], cardLocal[2]);
      let d = yaw - base;
      while (d > Math.PI) d -= Math.PI * 2;
      while (d < -Math.PI) d += Math.PI * 2;
      f.root.rotation.y = base + d * k;
    });
  };
  {
    const isl = islands.D;
    look(isl, CU.entreprises + 0.2, CARD_POS.D);
    MD.setPose(isl.figs[0], poseBlend([[0, P.armsCrossed], [CU.entreprises + 0.25, P.lookUp, 0.5]], t));
    MD.setPose(isl.figs[1], poseBlend([[0, P.idle], [CU.entreprises + 0.35, P.lookUp, 0.4], [CU.recrutent, P.point, 0.45, "back.out(1.5)"]], t));
  }
  {
    const isl = islands.E;
    look(isl, CU.lycees + 0.15, CARD_POS.E);
    isl.figs.forEach((f, i) =>
      MD.setPose(f, poseBlend([[0, i === 0 ? P.armsCrossed : P.idle], [CU.lycees + 0.2 + i * 0.07, i === 0 ? P.point : P.lookUp, 0.45]], t)),
    );
  }
  {
    const isl = islands.F;
    const f = isl.figs[0];
    f.root.rotation.y = 0;
    f.body.position.y = -0.4;
    f.body.position.z = -0.12;
    MD.setPose(f, poseBlend([[0, P.tablet], [CU.clients + 0.3, { ...P.tablet, hx: -0.42, lsx: -0.55, rsx: -0.55 }, 0.5]], t));
  }
}

// ---------------------------------------------------------------------------
// DOM overlays inside the world layer
// ---------------------------------------------------------------------------
const $ = (id) => document.getElementById(id);
const dom = {
  flash: $("w-flash"),
  vf: $("w-vf"),
  vfC: ["w-vf-tl", "w-vf-tr", "w-vf-bl", "w-vf-br"].map($),
  vfPill: $("w-vf-pill"),
  vfFocus: $("w-vf-focus"),
  rings: [0, 1, 2, 3].map((i) => $(`w-ring-${i}`)),
  labels: { D: $("w-lab-D"), E: $("w-lab-E"), F: $("w-lab-F") },
  blur: $("w-hblur"),
  portal: $("w-portal"),
};
function setStyle(el, o) {
  for (const k in o) el.style[k] = o[k];
}
function ringBurst(el, t, t0, x, y, scaleMax = 1) {
  const a = (t - t0) / 0.75;
  if (a < 0 || a > 1) {
    el.style.opacity = "0";
    return;
  }
  const s = lerp(0.15, 2.4 * scaleMax, ease("expo.out", a));
  setStyle(el, {
    opacity: String(1 - ease("power2.in", a)),
    transform: `translate(${x - 160}px, ${y - 160}px) scale(${s})`,
  });
  const dots = el.querySelectorAll(".w-dot");
  dots.forEach((d, i) => {
    const ang = (i / dots.length) * Math.PI * 2 + 0.3;
    const r = lerp(40, 190, ease("power3.out", a));
    d.style.transform = `translate(${Math.cos(ang) * r}px, ${Math.sin(ang) * r}px) scale(${1 - a})`;
  });
}

// ---------------------------------------------------------------------------
// init (fonts, photos, cards, UI) → then first render
// ---------------------------------------------------------------------------
const CARD_POS = {
  A: [-0.4, 5.3, 1.2],
  B: [-0.2, 5.4, 1.4],
  C: [-0.3, 5.2, 1.3],
  D: [0.8, 6.3, 1.4],
  E: [0.6, 6.6, 1.2],
  F: [0.4, 6.0, 0.8],
};
let ready = false;
let photos = null;

async function init() {
  await Promise.all([
    document.fonts.load('800 60px "Archivo"'),
    document.fonts.load('700 40px "Archivo"'),
    document.fonts.load('600 40px "Archivo"'),
    document.fonts.load('500 30px "IBM Plex Mono"'),
    document.fonts.load('600 30px "IBM Plex Mono"'),
  ]);
  definePoses();
  defineCamKeys();
  // final assembled state for photos
  Object.values(islands).forEach((isl) => assemble(isl, 100, 0, 1));
  Object.values(islands).forEach((isl) => {
    if (isl.fig) isl.fig.root.visible = false;
    if (isl.figs) isl.figs.forEach((f) => (f.root.visible = false));
  });
  bubbles.forEach((b) => (b.visible = false));
  hub.visible = false;
  sparks.visible = sparkPoints.visible = false;
  hemi.intensity = 0.85;
  key.intensity = 3.0;
  key.target.position.set(0, 0, 0);
  key.position.copy(LDIR).multiplyScalar(60);
  const sc = key.shadow.camera;
  sc.left = sc.bottom = -60;
  sc.right = sc.top = 60;
  sc.updateProjectionMatrix();
  const A = islands.A, B = islands.B, Cc = islands.C;
  photos = {
    A: [
      shoot(A, [1.6, 1.25, 2.6], [0.1, 1.0, -1.25], 38),
      shoot(A, [0.9, 1.45, 0.1], [0.4, 1.35, -1.25], 30),
      shoot(A, [4.2, 1.6, 4.4], [3.1, 0.8, 2.7], 40),
      shoot(A, [3.0, 1.4, -1.6], [2.5, 0.7, -4.0], 42),
    ],
    B: [
      shoot(B, [2.6, 1.7, 2.6], [-2.0, 1.2, -2.1], 46),
      shoot(B, [1.0, 2.4, 0.6], [-1.0, 1.7, -2.6], 44),
      shoot(B, [4.4, 1.5, 2.6], [2.7, 0.7, 0.6], 40),
      shoot(B, [4.6, 1.4, -0.8], [3.0, 0.5, -2.8], 40),
    ],
    C: [
      shoot(Cc, [1.5, 1.4, 1.9], [-0.3, 0.75, -1.6], 38),
      shoot(Cc, [0.5, 0.9, -0.2], [-0.3, 0.65, -1.3], 28),
      shoot(Cc, [-0.6, 1.9, 3.6], [-3.0, 1.0, 1.6], 42),
      shoot(Cc, [0.2, 1.3, 3.2], [-2.0, 0.3, 2.0], 40),
    ],
  };
  Object.values(islands).forEach((isl) => {
    if (isl.fig) isl.fig.root.visible = true;
    if (isl.figs) isl.figs.forEach((f) => (f.root.visible = true));
  });
  hub.visible = true;
  sparks.visible = sparkPoints.visible = true;
  // phone UI
  const titles = {
    A: [["Portail en fer forgé", "12 OCT."], ["Volutes forgées", "28 SEPT."], ["Billot et enclume", "14 SEPT."], ["Débit de barres", "2 SEPT."]],
    B: [["Angle en briques", "10 OCT."], ["Échafaudage monté", "1 OCT."], ["Mortier bâtard", "22 SEPT."], ["Mur en parpaings", "9 SEPT."]],
    C: [["Commode en chêne", "11 OCT."], ["Façade de tiroir", "30 SEPT."], ["Établi restauré", "18 SEPT."], ["Copeaux de rabot", "5 SEPT."]],
  };
  const profs = ["A", "B", "C"].map((k, i) => ({
    ...PROFILES[i],
    items: photos[k].map((ph, j) => ({ photo: ph, title: titles[k][j][0], date: titles[k][j][1] })),
  }));
  ui.ui = new SC.PhoneUI(profs);
  ui.tex = canvasTexture(ui.ui.canvas);
  ui.tex.anisotropy = 16;
  phone = MD.hubPhone(ui.tex);
  hub.add(phone);
  // capture cards
  const mkCard = (k, i) => {
    const cv = SC.captureCard(photos[k][0], PROFILES[i].label, titles[k][0][0]);
    const c = MD.photoCard(canvasTexture(cv), 3.9, (3.9 * 860) / 1000);
    const glow = glowSprite(0xf97316, 6.2);
    glow.material.opacity = 0.32;
    glow.position.z = -0.3;
    glow.renderOrder = 4;
    c.add(glow);
    scene.add(c);
    return c;
  };
  cards.A = mkCard("A", 0);
  cards.B = mkCard("B", 1);
  cards.C = mkCard("C", 2);
  const mkProfile = (k, i) => {
    const cv = SC.profileCard(photos[k][0], { ...PROFILES[i], title: titles[k][0][0] });
    const c = MD.photoCard(canvasTexture(cv), 3.4, (3.4 * 1160) / 1000);
    const glow = glowSprite(0xf97316, 6.6);
    glow.material.opacity = 0.3;
    glow.position.z = -0.3;
    glow.renderOrder = 4;
    c.add(glow);
    scene.add(c);
    return c;
  };
  cards.D = mkProfile("A", 0);
  cards.E = mkProfile("B", 1);
  cards.F = mkProfile("C", 2);
  // light paths hub → audiences, trades → hub
  const hubEdge = (k) => {
    const p = POS[k];
    const d = Math.hypot(p[0], p[1]);
    return V3((p[0] / d) * 6.2, 0.35, (p[1] / d) * 6.2);
  };
  for (const k of ["D", "E", "F"]) {
    const s = hubEdge(k);
    const e = V3(POS[k][0] - (POS[k][0] / Math.hypot(...POS[k])) * 3.2, 0.3, POS[k][1] - (POS[k][1] / Math.hypot(...POS[k])) * 3.2);
    const m = s.clone().lerp(e, 0.5);
    m.y = 4.2;
    paths[k] = MD.lightPath([s, s.clone().lerp(m, 0.5).setY(2.8), m, e.clone().lerp(m, 0.5).setY(2.6), e], { radius: 0.09 });
    scene.add(paths[k]);
    const pr = MD.pulseRing();
    pr.position.set(POS[k][0], 0.08, POS[k][1]);
    scene.add(pr);
    pulses[k] = pr;
  }
  for (const k of ["A", "B", "C"]) {
    const s = V3(POS[k][0] + CARD_POS[k][0], CARD_POS[k][1] - 1.0, POS[k][1] + CARD_POS[k][2]);
    const e = V3(0, 0.6, 0);
    const m = s.clone().lerp(e, 0.5);
    m.y = 6.0;
    paths[k] = MD.lightPath([s, m, e], { radius: 0.06 });
    scene.add(paths[k]);
  }
  ready = true;
}

// ---------------------------------------------------------------------------
// per-frame update
// ---------------------------------------------------------------------------
function phoneUIState(t) {
  const s = { mode: "gallery", page: 0, sheet: 0, land: [0, 0, 0], glow: [0, 0, 0] };
  s.fab = prog(t, 13.62, 13.86);
  s.sheet = t < 15.9 ? prog(t, 13.8, 14.2) : 1 - prog(t, 15.9, 16.2);
  s.photo = prog(t, 13.98, 14.6);
  s.typing = prog(t, CU.unTitre + 0.02, CU.unTitre + 0.72);
  s.caret = t > CU.unTitre - 0.1 && t < CU.unTitre + 1.0 && Math.floor((t - CU.unTitre) * 4) % 2 === 0;
  s.textGlow = env(t, CU.unTitre, 16.1, 0.15, 0.5);
  s.chips = prog(t, CU.unTitre + 0.35, CU.unTitre + 0.95);
  s.press = prog(t, CU.tap, CU.tap + 0.22);
  s.halo = prog(t, CU.tap, CU.tap + 0.5);
  s.land[0] = prog(t, 16.05, 16.65);
  s.glow[0] = env(t, 16.2, 17.6, 0.2, 0.6);
  s.page = ep(t, 16.85, 17.15, "power3.inOut") + ep(t, 17.6, 17.9, "power3.inOut");
  s.land[1] = prog(t, 17.05, 17.6);
  s.glow[1] = env(t, 17.15, 18.3, 0.2, 0.6);
  s.land[2] = prog(t, 17.85, 18.4);
  s.glow[2] = env(t, 17.95, 19.6, 0.2, 0.6);
  if (t > 20.2) {
    s.page = 2 - 2 * ep(t, 20.2, 20.6, "power3.inOut");
    s.land = [1, 1, 1];
  }
  return s;
}

function billboard(obj) {
  obj.quaternion.copy(camera.quaternion);
}

// ----- S1 portal: a white rounded square pops, then opens into the world (canvas clip-path)
const PORTAL_T = 4.4;
function updatePortal(t) {
  const el = dom.portal;
  const pop = ep(t, PORTAL_T, PORTAL_T + 0.24, "back.out(2.2)");
  const open = ep(t, PORTAL_T + 0.22, PORTAL_T + 0.86, "power3.inOut");
  const s0 = 230;
  const w = lerp(s0, W + 8, open);
  const h = lerp(s0, H + 8, open);
  const r = lerp(52, 0, ease("power2.in", open));
  const left = (W - w) / 2;
  const top = (H - h) / 2;
  if (t < PORTAL_T || t > PORTAL_T + 1.1) {
    el.style.opacity = "0";
  } else {
    const fill = 1 - ep(t, PORTAL_T + 0.2, PORTAL_T + 0.36, "power1.out");
    setStyle(el, {
      opacity: String(1 - ep(t, PORTAL_T + 0.75, PORTAL_T + 1.05, "power1.in")),
      left: `${left.toFixed(1)}px`,
      top: `${top.toFixed(1)}px`,
      width: `${w.toFixed(1)}px`,
      height: `${h.toFixed(1)}px`,
      borderRadius: `${r.toFixed(1)}px`,
      transform: `scale(${open > 0 ? 1 : Math.max(0.001, pop)})`,
      background: `rgba(243,242,239,${fill.toFixed(3)})`,
    });
  }
  if (t < PORTAL_T + 0.2) {
    canvas.style.clipPath = "inset(50% 50% 50% 50%)";
  } else if (open < 1) {
    canvas.style.clipPath = `inset(${top.toFixed(1)}px ${left.toFixed(1)}px ${top.toFixed(1)}px ${left.toFixed(1)}px round ${r.toFixed(1)}px)`;
  } else {
    canvas.style.clipPath = "none";
  }
}

// ----- S6: only the glossy bubbles float around the end card
const END_T = 35.55;
const END_SPOTS = [
  [250, 230, 1.15], [1690, 190, 1.0], [180, 820, 0.95], [1730, 860, 1.2], [560, 965, 0.8], [1380, 105, 0.78], [1200, 975, 0.9],
];
function renderEnd(t) {
  canvas.style.clipPath = "none";
  canvas.style.filter = "none";
  canvas.style.opacity = String(ep(t, END_T, END_T + 0.3, "power1.out"));
  dom.portal.style.opacity = "0";
  dom.flash.style.opacity = "0";
  dom.vf.style.opacity = "0";
  dom.rings.forEach((r) => (r.style.opacity = "0"));
  Object.values(dom.labels).forEach((l) => (l.style.opacity = "0"));
  Object.values(islands).forEach((i) => (i.g.visible = false));
  hub.visible = false;
  Object.values(cards).forEach((c) => (c.visible = false));
  Object.values(paths).forEach((p) => (p.visible = false));
  Object.values(pulses).forEach((p) => (p.visible = false));
  sparks.visible = sparkPoints.visible = false;
  weldGlow.visible = camFlash.visible = false;
  weldLight.intensity = flashLight.intensity = 0;
  hemi.intensity = 1.5;
  key.intensity = 3.2;
  scene.environmentIntensity = 0.7;
  // fixed camera
  const hh = 10.5;
  const az = (45 * Math.PI) / 180, el = (33 * Math.PI) / 180;
  _target.set(0, 0, 0);
  camera.position.set(Math.cos(el) * Math.sin(az), Math.sin(el), Math.cos(el) * Math.cos(az)).multiplyScalar(120);
  camera.up.set(0, 1, 0);
  camera.lookAt(_target);
  camera.left = -hh * ASPECT; camera.right = hh * ASPECT; camera.top = hh; camera.bottom = -hh;
  camera.updateProjectionMatrix();
  camera.updateMatrixWorld();
  const right = V3(1, 0, 0).applyQuaternion(camera.quaternion);
  const up = V3(0, 1, 0).applyQuaternion(camera.quaternion);
  const fwd = V3(0, 0, -1).applyQuaternion(camera.quaternion);
  bubbles.forEach((b, i) => {
    const [sx, sy, sc] = END_SPOTS[i % END_SPOTS.length];
    const d = 0.09 * i;
    const kin = ep(t, 36.05 + d, 36.6 + d, "back.out(2)");
    const x = ((sx / W) - 0.5) * 2 * hh * ASPECT;
    const y = -((sy / H) - 0.5) * 2 * hh;
    const bob = Math.sin(t * 1.1 + i * 1.3) * 0.25;
    b.position.copy(_target).addScaledVector(right, x + Math.sin(t * 0.4 + i) * 0.15).addScaledVector(up, y + bob).addScaledVector(fwd, -i * 0.5);
    b.scale.setScalar(Math.max(0.001, kin * sc * 1.15));
    b.visible = kin > 0.002;
    billboard(b.userData.face);
  });
  key.target.position.copy(_target);
  key.position.copy(_target).addScaledVector(LDIR, 60);
  renderer.render(scene, camera);
}

function renderAt(t) {
  if (!ready) return;
  const cam = applyCamera(t);

  // ----- visibility windows of the world layer
  if (t >= END_T) return renderEnd(t);
  const worldOn = t >= PORTAL_T + 0.2 && t < 32.25;
  canvas.style.opacity = String(worldOn ? 1 - ep(t, 31.75, 32.2, "power2.in") : 0);
  updatePortal(t);

  // ----- lights: reveal ramp + S5 dim
  const reveal = ep(t, CU.windowOpen, CU.windowOpen + 0.9, "power2.out");
  const dim = 1 - 0.55 * env(t, 29.1, 32.3, 0.6, 0.4);
  hemi.intensity = lerp(0.22, 0.85, reveal) * dim;
  key.intensity = lerp(0.6, 3.0, reveal) * dim;
  scene.environmentIntensity = 0.22 * dim;

  // ----- islands assembly
  assemble(islands.A, t, 4.42, 5.55);
  assemble(islands.B, t, 9.9, 10.75);
  assemble(islands.C, t, 10.8, 11.6);
  assemble(islands.D, t, 19.05, 20.35);
  assemble(islands.E, t, 19.2, 20.5);
  assemble(islands.F, t, 19.35, 20.65);
  // audience lighting: dim until their path lands, full when their beat starts
  const lit = { D: CU.entreprises - 0.1, E: CU.lycees - 0.1, F: CU.clients - 0.1 };
  for (const k of ["D", "E", "F"]) {
    const arrive = 21.55 + { D: 0, E: 0.12, F: 0.24 }[k];
    const k1 = 0.42 + 0.2 * ep(t, arrive, arrive + 0.3) + 0.38 * ep(t, lit[k], lit[k] + 0.5);
    islands[k].setLight(k1);
    islands[k].win.emissiveIntensity = 1.25 * ep(t, lit[k], lit[k] + 0.4);
  }

  // ----- figures
  updateFigures(t);

  // ----- welding: glow, light, sparks
  const A = islands.A;
  const weldW = A.g.localToWorld(V3(0.43, 1.12, -1.19));
  const welding = t > 4.3 && t < 5.72;
  const fl = welding ? 0.55 + 0.45 * flicker(t, 3) : 0;
  weldGlow.visible = welding;
  weldGlow.position.copy(weldW);
  weldGlow.scale.setScalar(0.9 + fl * 1.1);
  weldGlow.material.opacity = fl;
  weldLight.position.copy(weldW).add(V3(0.2, 0.3, 0.4));
  weldLight.intensity = fl * 14;
  updateSparks(t, weldW);

  // ----- camera flashes (3D light + glow) and DOM flash
  let flashK = 0;
  const flashes = [
    [CU.flashA, islands.A.fig],
    [CU.flashB, islands.B.fig],
    [CU.flashC, islands.C.fig],
  ];
  camFlash.visible = false;
  flashLight.intensity = 0;
  for (const [ft, fig] of flashes) {
    const a = t - ft;
    if (a > -0.02 && a < 0.5) {
      const k = a < 0 ? 0 : Math.exp(-a * 13);
      fig.root.updateMatrixWorld(true);
      const p = fig.flashAnchor.getWorldPosition(V3(0, 0, 0));
      camFlash.visible = true;
      camFlash.position.copy(p);
      camFlash.scale.setScalar(1.2 + 5.5 * k);
      camFlash.material.opacity = k;
      flashLight.position.copy(p);
      flashLight.intensity = 60 * k;
      flashK = Math.max(flashK, k);
    }
  }
  dom.flash.style.opacity = String(0.62 * flashK * flashK);

  // ----- capture cards: pop out of the phone, float, then fly into the hub phone (S3)
  const cardT = { A: CU.flashA, B: CU.flashB, C: CU.flashC };
  const flyT = { A: 13.38, B: 13.48, C: 13.58 };
  const phoneScreenW = V3(0, 0.6, 0);
  for (const k of ["A", "B", "C"]) {
    const c = cards[k];
    const isl = islands[k];
    const t0 = cardT[k] + 0.04;
    const vis = t > t0 && t < flyT[k] + 0.62;
    c.visible = vis;
    if (!vis) continue;
    isl.fig.root.updateMatrixWorld(true);
    const from = isl.fig.flashAnchor.getWorldPosition(V3(0, 0, 0));
    const rest = V3(POS[k][0] + CARD_POS[k][0], CARD_POS[k][1], POS[k][1] + CARD_POS[k][2]);
    const kOut = ep(t, t0, t0 + 0.62, "back.out(1.25)");
    const pos = from.clone().lerp(rest, kOut);
    pos.y += Math.sin(t * 1.6 + k.charCodeAt(0)) * 0.08 * kOut;
    let s = lerp(0.08, 1, ep(t, t0, t0 + 0.55, "back.out(1.7)"));
    // fly into the phone along its path
    const kf = ep(t, flyT[k], flyT[k] + 0.6, "power3.in");
    if (kf > 0) {
      const curve = paths[k].userData.curve;
      pos.copy(curve.getPoint(kf));
      s *= lerp(1, 0.18, kf);
    }
    c.position.copy(pos);
    c.scale.setScalar(Math.max(0.001, s));
    billboard(c);
  }
  // trade → hub trails
  for (const k of ["A", "B", "C"]) {
    const m = paths[k].userData.material;
    const kf = prog(t, flyT[k], flyT[k] + 0.6);
    m.uniforms.uProgress.value = ease("power3.in", kf);
    m.uniforms.uTail.value = t < 28.6 ? Math.max(0, m.uniforms.uProgress.value - 0.14) + ease("power2.in", prog(t, flyT[k] + 0.6, flyT[k] + 0.8)) : 0;
    m.uniforms.uOpacity.value = t < 28.6 ? 1 : 0.95;
    if (t >= 28.6) m.uniforms.uProgress.value = ep(t, 28.7, 29.6, "power2.inOut");
    paths[k].visible = (kf > 0 && t < flyT[k] + 1.1) || t >= 28.6;
  }

  // ----- hub phone rises; UI texture
  const rise = ep(t, 12.95, 13.75, "back.out(1.3)");
  phone.position.y = lerp(-4.5, 0, rise);
  phone.visible = t > 12.9;
  plinth.position.y = lerp(-2.5, 0, ep(t, 12.7, 13.4, "power3.out"));
  hub.visible = t > 12.6;
  if (phone.visible) {
    const st = phoneUIState(t);
    if (ui.ui.draw(st)) ui.tex.needsUpdate = true;
  }

  // ----- glossy bubbles around the phone (S3)
  bubbles.forEach((b) => {
    const d = b.userData.delay;
    const kin = ep(t, 13.95 + d, 14.45 + d, "back.out(2.2)");
    const kout = ep(t, 18.85 + d * 0.5, 19.25 + d * 0.5, "back.in(1.8)");
    const s = Math.max(0.001, kin * (1 - kout));
    b.visible = s > 0.002;
    b.scale.setScalar(s);
    const bp = b.userData.base;
    b.position.set(bp.x, bp.y + Math.sin(t * 1.3 + b.userData.seed) * 0.22, bp.z);
    billboard(b.userData.face);
  });

  // ----- light paths hub → audiences
  for (const [k, d] of [["D", 0], ["E", 0.12], ["F", 0.24]]) {
    const m = paths[k].userData.material;
    const k0 = ep(t, 21.0 + d, 21.6 + d, "power2.inOut");
    m.uniforms.uProgress.value = k0;
    m.uniforms.uTail.value = 0;
    const litT = lit[k];
    m.uniforms.uGlow.value = 0.6 + 0.8 * env(t, litT, litT + 1.4, 0.15, 0.9);
    m.uniforms.uOpacity.value = lerp(0.85, 1, env(t, litT, litT + 1.4, 0.15, 0.9));
    paths[k].visible = t > 21.0 + d && t < 32.3;
    const pr = pulses[k];
    const a = prog(t, litT, litT + 0.9);
    pr.visible = a > 0 && a < 1;
    pr.scale.setScalar(lerp(1.5, 7.5, ease("expo.out", a)));
    pr.material.opacity = 0.9 * (1 - a);
  }

  // ----- audience profile cards
  for (const k of ["D", "E", "F"]) {
    const c = cards[k];
    const t0 = lit[k] + 0.12;
    const kin = ep(t, t0, t0 + 0.6, "back.out(1.6)");
    c.visible = t > t0 && t < 32.3;
    if (!c.visible) continue;
    const base = V3(POS[k][0] + CARD_POS[k][0], CARD_POS[k][1], POS[k][1] + CARD_POS[k][2]);
    c.position.copy(base);
    c.position.y += lerp(-2.4, 0, kin) + Math.sin(t * 1.4 + k.charCodeAt(0)) * 0.1;
    c.scale.setScalar(Math.max(0.001, kin));
    billboard(c);
  }

  // ----- horizontal motion blur on whips (SVG filter on the canvas)
  const dt = 1 / 60;
  const s0 = camState(t - dt);
  const du = (cam[0] - s0[0]) * 0.7071 - (cam[2] - s0[2]) * 0.7071;
  const pxPerUnit = H / (2 * cam[3]);
  const vx = Math.abs(du * pxPerUnit) * 2; // px per frame at 30fps
  const dz = Math.abs(Math.log(cam[3] / s0[3])) * 60;
  const blurX = dz > 2.2 ? 0 : Math.min(64, vx * 0.2);
  if (blurX > 0.8) {
    dom.blur.setAttribute("stdDeviation", `${blurX.toFixed(1)} 0`);
    canvas.style.filter = "url(#w-hblur-f)";
  } else {
    canvas.style.filter = "none";
  }

  // ----- DOM: viewfinders (capture), ring bursts, audience labels
  updateViewfinder(t);
  const ringAt = (i, t0, fig) => {
    if (Math.abs(t - t0 - 0.3) > 0.5) {
      dom.rings[i].style.opacity = "0";
      return;
    }
    fig.root.updateMatrixWorld(true);
    const [x, y] = project(fig.flashAnchor.getWorldPosition(V3(0, 0, 0)));
    ringBurst(dom.rings[i], t, t0, x, y, 1);
  };
  ringAt(0, CU.flashA, islands.A.fig);
  ringAt(1, CU.flashB, islands.B.fig);
  ringAt(2, CU.flashC, islands.C.fig);
  // tap ring on the phone button (S3)
  if (Math.abs(t - CU.tap - 0.35) < 0.5 && phone) {
    const bx = (1080 / 2 + 120) / 1080 - 0.5;
    const bz = 1835 / 2220 - 0.5;
    const wp = V3(bx * 5.2, 0.6, bz * 11.0);
    const [x, y] = project(wp);
    ringBurst(dom.rings[3], t, CU.tap + 0.05, x, y, 0.8);
  } else dom.rings[3].style.opacity = "0";
  for (const k of ["D", "E", "F"]) {
    const el = dom.labels[k];
    const t0 = lit[k] + 0.3;
    const a = env(t, t0, 29.4, 0.35, 0.3);
    const focus = env(t, t0, lit[k] + 1.9, 0.01, 0.4);
    if (a <= 0) {
      el.style.opacity = "0";
      continue;
    }
    const c = cards[k];
    const halfW = (3.4 / 2) * c.scale.x;
    const anchor = c.position.clone().add(V3(1, 0, 0).applyQuaternion(camera.quaternion).multiplyScalar(halfW + 0.35));
    const [x, y] = project(anchor);
    const sc = lerp(0.62, 1, focus);
    setStyle(el, {
      opacity: String(a),
      transform: `translate(${x.toFixed(1)}px, ${(y - 60).toFixed(1)}px) scale(${sc.toFixed(3)})`,
    });
  }

  renderer.render(scene, camera);
}

function updateViewfinder(t) {
  const windows = [
    [CU.photographient, CU.flashA + 0.12, islands.A, [[-1.45, 0.05, -1.25], [1.45, 2.15, -1.25]]],
    [CU.chantier - 0.05, CU.flashB + 0.12, islands.B, [[-3.3, 0.0, -3.0], [1.8, 2.5, -3.0]]],
    [CU.ouvrage + 0.1, CU.flashC + 0.12, islands.C, [[-1.3, 0.1, -1.3], [0.7, 1.45, -1.3]]],
  ];
  let shown = false;
  for (const [t0, t1, isl, [a, b]] of windows) {
    if (t < t0 || t > t1) continue;
    shown = true;
    const pts = [
      V3(a[0], a[1], a[2]), V3(b[0], a[1], b[2]), V3(a[0], b[1], a[2]), V3(b[0], b[1], b[2]),
    ].map((v) => project(isl.g.localToWorld(v)));
    let minX = Math.min(...pts.map((p) => p[0])), maxX = Math.max(...pts.map((p) => p[0]));
    let minY = Math.min(...pts.map((p) => p[1])), maxY = Math.max(...pts.map((p) => p[1]));
    const k = ep(t, t0, t0 + 0.35, "back.out(1.8)");
    const lock = ep(t, t1 - 0.6, t1 - 0.32, "power3.out");
    const pad = lerp(90, 22, k) - lock * 14;
    minX -= pad; maxX += pad; minY -= pad; maxY += pad;
    const o = env(t, t0, t1, 0.12, 0.08);
    dom.vf.style.opacity = String(o);
    const C4 = [[minX, minY], [maxX, minY], [minX, maxY], [maxX, maxY]];
    dom.vfC.forEach((el, i) => (el.style.transform = `translate(${C4[i][0].toFixed(1)}px, ${C4[i][1].toFixed(1)}px)`));
    const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    dom.vfFocus.style.transform = `translate(${cx.toFixed(1)}px, ${cy.toFixed(1)}px) scale(${(1.4 - 0.4 * k - 0.15 * lock).toFixed(3)})`;
    dom.vfPill.style.transform = `translate(${cx.toFixed(1)}px, ${(minY - 54).toFixed(1)}px)`;
  }
  if (!shown) dom.vf.style.opacity = "0";
}

// ---------------------------------------------------------------------------
// HyperFrames wiring
// ---------------------------------------------------------------------------
window.__hf = window.__hf || {};
window.__hf.buildReady = window.__hf.buildReady || {};
let lastT = 0;
const readyP = init().then(() => renderAt(window.__hfThreeTime || lastT));
window.__hf.buildReady["manoo-world"] = readyP;
window.addEventListener("hf-seek", (e) => {
  lastT = e.detail.time;
  renderAt(lastT);
});
window.__manooWorld = { renderAt, camState, project, islands, cards, ready: readyP, get photos() { return photos; } };

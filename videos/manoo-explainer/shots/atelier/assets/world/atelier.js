// Manoo explainer — 3D shot « l'atelier » : Jules finishes his gate, lifts his mask, steps back and
// photographs it (over-the-shoulder push, live viewfinder on the phone, flash). Driven by hf-seek time.
// Also exposes window.__atelierStill(name) for the portfolio photos (tools/export-stills.mjs).
import {
  THREE, C, M, mat, box, cyl, sph, at, grp, rng, clamp, lerp, prog, ease, ep, env, wobble, flicker,
  makeCanvas, canvasTexture, glowSprite,
} from "./kit.js";
import * as MD from "./models.js";
import { RoomEnvironment } from "../vendor/RoomEnvironment.js";

const W = 1920;
const H = 1080;
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const T_FLASH = 2.5;

// ---------------------------------------------------------------------------
const canvas = document.getElementById("gl");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
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
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.3;

const camera = new THREE.PerspectiveCamera(30, W / H, 0.05, 200);
const hemi = new THREE.HemisphereLight(0xf4f4f2, 0x1a242a, 0.95);
scene.add(hemi);
const key = new THREE.DirectionalLight(0xfff6ec, 2.8);
key.position.set(4.5, 11, 6.5);
key.target.position.set(0, 0, -0.5);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.bias = -0.0003;
key.shadow.normalBias = 0.03;
key.shadow.radius = 3;
Object.assign(key.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 30 });
scene.add(key, key.target);
const fill = new THREE.DirectionalLight(0xffe4cc, 0.55);
fill.position.set(-6, 4, 3);
scene.add(fill);

// ---------------------------------------------------------------------------
// the workshop (one island of the maquette)
// ---------------------------------------------------------------------------
const room = new THREE.Group();
scene.add(room);
{
  const RW = 9, RD = 7;
  const slab = box(RW, 1.1, RD, mat(C.encre2, { rough: 0.95 }), { r: 0.2, seg: 3 });
  slab.position.y = -0.61;
  room.add(slab);
  const tex = MD.floorTexture("tiles", 7);
  tex.repeat.set(1.3, 1);
  const floor = box(RW - 0.24, 0.12, RD - 0.24, new THREE.MeshStandardMaterial({ color: 0xdcd8d0, map: tex, roughness: 0.92 }), { r: 0.04, cast: false });
  floor.position.y = -0.06;
  room.add(floor);
  const walls = MD.cornerWalls(RW, RD, 3.3, { windowOnLeft: true });
  room.add(walls);
  room.add(at(MD.workbench({ w: 2.4 }), -2.55, 0, -2.6));
  room.add(at(MD.pegboard(2.3, 1.2), -2.55, 1.15, -3.18));
  room.add(at(MD.gasBottles(), 2.7, 0, -2.75));
  room.add(at(MD.anvil(), -3.0, 0, 0.9, 0.4));
  const rack = MD.barRack();
  room.add(at(rack, 3.55, 0, 0.6, -Math.PI / 2));
  const shelf = MD.shelfUnit(1.4, 2.0);
  room.add(at(shelf, -4.05, 0, -1.2, Math.PI / 2));
}
room.traverse((o) => {
  if (o.isMesh) {
    o.receiveShadow = true;
  }
});

const gate = MD.gate();
at(gate, 0.2, 0, -1.45);
room.add(gate);

// other réalisations, used only for the portfolio stills
function railing() {
  const g = new THREE.Group();
  const om = M.orange();
  const L = 2.6;
  const top = box(L, 0.07, 0.09, om, { r: 0.015 });
  top.position.set(0, 1.05, 0);
  const bot = box(L, 0.05, 0.05, om, { r: 0.01 });
  bot.position.set(0, 0.12, 0);
  g.add(top, bot);
  for (const x of [-L / 2, 0, L / 2]) {
    const p = box(0.08, 1.12, 0.08, om, { r: 0.015 });
    p.position.set(x, 0.56, 0);
    const foot = box(0.2, 0.03, 0.2, mat(C.acier, { rough: 0.6, metal: 0.3 }), { r: 0.008 });
    foot.position.set(x, 0.015, 0);
    g.add(p, foot);
  }
  for (let i = 0; i < 14; i++) {
    const x = -L / 2 + 0.18 + i * ((L - 0.36) / 13);
    const b = box(0.03, 0.9, 0.03, om, { r: 0.005 });
    b.position.set(x, 0.58, 0);
    g.add(b);
  }
  for (const x of [-0.65, 0.65]) {
    const ring = MD.gate ? null : null;
    void ring;
    const t = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.02, 8, 28), om);
    t.position.set(x, 0.58, 0);
    t.castShadow = true;
    g.add(t);
  }
  return g;
}
function staircase() {
  const g = new THREE.Group();
  const om = M.orange();
  const stepM = mat(C.papier, { rough: 0.7 });
  const n = 6;
  for (let i = 0; i < n; i++) {
    const s = box(1.1, 0.06, 0.34, stepM, { r: 0.01 });
    s.position.set(0, 0.22 + i * 0.27, -i * 0.3);
    g.add(s);
  }
  const len = Math.hypot(n * 0.27, n * 0.3) + 0.3;
  const ang = Math.atan2(n * 0.27, n * 0.3);
  for (const x of [-0.6, 0.6]) {
    const str = box(0.07, 0.24, len, om, { r: 0.012 });
    str.position.set(x, 0.8, -0.82);
    str.rotation.x = ang;
    g.add(str);
    const hr = box(0.05, 0.05, len, om, { r: 0.012 });
    hr.position.set(x, 1.75, -0.82);
    hr.rotation.x = ang;
    g.add(hr);
    for (let i = 0; i < n; i += 2) {
      const p = box(0.035, 0.95, 0.035, om, { r: 0.006 });
      p.position.set(x, 0.72 + i * 0.27, -i * 0.3);
      g.add(p);
    }
  }
  return g;
}
const extra = { railing: railing(), staircase: staircase() };
at(extra.railing, 0.2, 0, -1.45);
at(extra.staircase, 0.2, 0, -0.4);
Object.values(extra).forEach((o) => {
  o.visible = false;
  room.add(o);
});

// Jules, apprentice metalworker
const fig = MD.figurine({ top: 0x3b4c56, bottom: 0x2a343a, mask: true, scale: 1.2 });
scene.add(fig.root);
fig.root.rotation.y = Math.PI; // faces the gate (-z)
fig.phone.scale.setScalar(1.55);
// hold the phone up to the right of the face, screen turned toward the over-the-shoulder camera
fig.phoneHold.position.set(-0.13, 0.74, 0.5);
fig.phone.rotation.y = 0.42;
// welding mask rebuilt for close-ups: hinge at the upper forehead, shell rests on the head when raised,
// thin headband ring instead of the flat strap
if (fig.maskPivot) {
  const mp = fig.maskPivot;
  const [shell, visor, strap] = mp.children;
  strap.visible = false;
  mp.position.set(0, 0.26, 0.05);
  shell.position.set(0, -0.08, 0.14);
  visor.position.set(0, -0.04, 0.195);
  const band = new THREE.Mesh(new THREE.TorusGeometry(0.163, 0.014, 8, 32), mat(C.ombre, { rough: 0.6, metal: 0.3 }));
  band.rotation.x = Math.PI / 2 - 0.25;
  band.position.set(0, 0.25, 0.0);
  band.castShadow = true;
  fig.neck.add(band);
}

// live viewfinder on the phone screen: render target from a camera at the lens
const RT_W = 360, RT_H = 694;
const rt = new THREE.WebGLRenderTarget(RT_W, RT_H, { colorSpace: THREE.SRGBColorSpace, samples: 4 });
const phoneCam = new THREE.PerspectiveCamera(64, RT_W / RT_H, 0.05, 60);
const scrMesh = fig.phone.children.find((c) => c.isMesh && c.geometry.type === "PlaneGeometry");
scrMesh.material = new THREE.MeshBasicMaterial({ map: rt.texture, toneMapped: false });
// overlay: camera UI drawn once (shutter ring + focus corners), plus a white flash layer
const uiCan = makeCanvas(280, 540);
{
  const g = uiCan.getContext("2d");
  g.clearRect(0, 0, 280, 540);
  g.strokeStyle = "rgba(255,255,255,0.95)";
  g.lineWidth = 7;
  g.beginPath();
  g.arc(140, 478, 30, 0, Math.PI * 2);
  g.stroke();
  g.fillStyle = "rgba(255,255,255,0.95)";
  g.beginPath();
  g.arc(140, 478, 21, 0, Math.PI * 2);
  g.fill();
  g.strokeStyle = "#f97316";
  g.lineWidth = 6;
  const cx = 140, cy = 230, s = 62, l = 22;
  for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
    g.beginPath();
    g.moveTo(cx + sx * s, cy + sy * (s - l));
    g.lineTo(cx + sx * s, cy + sy * s);
    g.lineTo(cx + sx * (s - l), cy + sy * s);
    g.stroke();
  }
  g.fillStyle = "rgba(16,22,25,0.55)";
  g.fillRect(0, 0, 280, 44);
  g.fillStyle = "#ffd36b";
  g.font = "600 22px Inter, sans-serif";
  g.textAlign = "center";
  g.fillText("PHOTO", 140, 515 - 470);
}
const uiTex = canvasTexture(uiCan);
const uiPlane = new THREE.Mesh(
  new THREE.PlaneGeometry(0.14, 0.27),
  new THREE.MeshBasicMaterial({ map: uiTex, transparent: true, toneMapped: false, depthWrite: false }),
);
uiPlane.position.copy(scrMesh.position);
uiPlane.position.z -= 0.0012;
uiPlane.rotation.y = Math.PI;
fig.phone.add(uiPlane);
const whitePlane = new THREE.Mesh(
  new THREE.PlaneGeometry(0.14, 0.27),
  new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, toneMapped: false, depthWrite: false }),
);
whitePlane.position.copy(scrMesh.position);
whitePlane.position.z -= 0.0024;
whitePlane.rotation.y = Math.PI;
fig.phone.add(whitePlane);

// ---------------------------------------------------------------------------
// FX: weld glow, sparks, camera flash
// ---------------------------------------------------------------------------
const weldGlow = glowSprite(0xffd2a6, 1.2);
scene.add(weldGlow);
const weldLight = new THREE.PointLight(0xffb070, 0, 9, 1.4);
scene.add(weldLight);
const flashGlow = glowSprite(0xffffff, 1.0);
scene.add(flashGlow);
const flashLight = new THREE.PointLight(0xfff4e6, 0, 12, 1.2);
scene.add(flashLight);
const WELD = V3(0.63, 1.12, -1.36);

const SPARK_N = 160;
const sparkData = [];
{
  const r = rng(11);
  for (let i = 0; i < SPARK_N; i++) {
    const a = r() * Math.PI * 2;
    const sp = 1.4 + r() * 3.0;
    sparkData.push({ t0: -0.6 + r() * 1.3, life: 0.3 + r() * 0.6, vx: Math.cos(a) * sp * 0.7, vz: Math.sin(a) * sp * 0.5 + 1.2, vy: 0.5 + r() * 3.0 });
  }
}
const sparkPos = new Float32Array(SPARK_N * 6);
const sparkCol = new Float32Array(SPARK_N * 6);
const sparkGeo = new THREE.BufferGeometry();
sparkGeo.setAttribute("position", new THREE.BufferAttribute(sparkPos, 3));
sparkGeo.setAttribute("color", new THREE.BufferAttribute(sparkCol, 3));
const sparks = new THREE.LineSegments(sparkGeo, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false }));
sparks.frustumCulled = false;
scene.add(sparks);
function updateSparks(t) {
  const g = 9.8;
  for (let i = 0; i < SPARK_N; i++) {
    const s = sparkData[i];
    const age = t - s.t0;
    const o6 = i * 6;
    if (age < 0 || age > s.life || s.t0 > 0.62) {
      sparkPos.fill(0, o6, o6 + 6);
      sparkCol.fill(0, o6, o6 + 6);
      continue;
    }
    const pos = (a) => {
      let y = s.vy * a - 0.5 * g * a * a;
      if (y < -WELD.y) y = -WELD.y + Math.max(0, 0.3 * s.vy * (a - 0.3) - 2 * (a - 0.3) * (a - 0.3));
      return [WELD.x + s.vx * a, WELD.y + y, WELD.z + s.vz * a];
    };
    sparkPos.set(pos(Math.max(0, age - 0.04)), o6);
    sparkPos.set(pos(age), o6 + 3);
    const f = 1 - age / s.life;
    const c = [1.0 * f + 0.2, 0.62 * f * f + 0.15, 0.22 * f * f * f];
    sparkCol.set([c[0] * 0.35, c[1] * 0.35, c[2] * 0.35], o6);
    sparkCol.set(c, o6 + 3);
  }
  sparkGeo.attributes.position.needsUpdate = true;
  sparkGeo.attributes.color.needsUpdate = true;
}

// ---------------------------------------------------------------------------
// choreography
// ---------------------------------------------------------------------------
const P = MD.POSES;
function poseAt(t) {
  // weld → (stop, lift mask) → idle-ish → photo
  let p = MD.lerpPose(P.weld, P.idle, ep(t, 0.72, 1.15, "power2.inOut"));
  p = MD.lerpPose(p, P.photo, ep(t, 1.38, 1.86, "power3.out"));
  p.mask = ep(t, 0.74, 1.08, "back.out(1.6)");
  // little welding jitter + breathing
  if (t < 0.72) {
    p.rsx += wobble(t * 9, 2) * 0.05;
    p.lean += wobble(t * 4, 1) * 0.02;
  }
  p.lean += wobble(t * 1.3, 4) * 0.012;
  // steps while walking back (0.95–1.55)
  const walk = env(t, 0.92, 1.6, 0.1, 0.12);
  const ph = prog(t, 0.92, 1.6) * Math.PI * 3;
  p.legL += Math.sin(ph) * 0.42 * walk;
  p.legR -= Math.sin(ph) * 0.42 * walk;
  return p;
}
function figureAt(t) {
  const z = lerp(-0.42, 1.0, ep(t, 0.92, 1.62, "power2.inOut"));
  const x = lerp(0.82, 0.74, ep(t, 0.92, 1.62));
  fig.root.position.set(x, Math.abs(Math.sin(prog(t, 0.92, 1.6) * Math.PI * 3)) * 0.025, z);
  fig.root.rotation.y = Math.PI + lerp(0.12, 0.0, ep(t, 0.9, 1.5)) - 0.3 * ep(t, 1.3, 2.1, "power2.inOut");
  const pz = poseAt(t);
  MD.setPose(fig, pz);
  if (fig.maskPivot) fig.maskPivot.rotation.x = -1.62 * pz.mask;
  fig.phone.visible = t >= 1.42;
}
// camera: [time, pos, target, fov]
const CAM = [
  [0.0, [3.55, 2.5, 3.1], [0.45, 1.15, -1.0], 32],
  [1.2, [2.7, 2.4, 2.8], [0.5, 1.45, -0.85], 32],
  [2.25, [1.62, 2.46, 2.12], [0.62, 1.84, -0.45], 34],
  [3.4, [1.52, 2.43, 1.94], [0.6, 1.82, -0.45], 34],
];
function camAt(t) {
  let i = 1;
  while (i < CAM.length - 1 && t > CAM[i][0]) i++;
  const [t0, p0, g0, f0] = CAM[i - 1];
  const [t1, p1, g1, f1] = CAM[i];
  const k = ease(i === 2 ? "power3.inOut" : "sine.inOut", prog(t, t0, t1));
  const pos = p0.map((v, j) => lerp(v, p1[j], k));
  const tgt = g0.map((v, j) => lerp(v, g1[j], k));
  // handheld drift
  pos[0] += wobble(t * 0.9, 3) * 0.02;
  pos[1] += wobble(t * 0.8, 5) * 0.015;
  camera.position.set(...pos);
  camera.fov = lerp(f0, f1, k);
  camera.updateProjectionMatrix();
  camera.lookAt(...tgt);
}

let frozen = false;
function renderAt(t) {
  figureAt(t);
  camAt(t);
  // welding
  const welding = t < 0.7;
  const fl = welding ? 0.55 + 0.45 * flicker(t, 3) : 0;
  weldGlow.visible = welding;
  weldGlow.position.copy(WELD);
  weldGlow.scale.setScalar(0.7 + fl * 0.9);
  weldGlow.material.opacity = fl;
  weldLight.position.copy(WELD).add(V3(0.2, 0.3, 0.5));
  weldLight.intensity = fl * 10;
  updateSparks(t);
  // phone viewfinder (live until the flash, then frozen = the photo)
  fig.root.updateMatrixWorld(true);
  const lensPos = fig.flashAnchor.getWorldPosition(V3(0, 0, 0));
  const q = fig.phone.getWorldQuaternion(new THREE.Quaternion());
  const fwd = V3(0, 0, 1).applyQuaternion(q);
  // flash
  const a = t - T_FLASH;
  const fk = a > -0.01 && a < 0.6 ? Math.exp(-Math.max(0, a) * 9) : 0;
  flashGlow.visible = fk > 0.01;
  flashGlow.position.copy(lensPos).add(fwd.clone().multiplyScalar(0.05));
  flashGlow.scale.setScalar(0.4 + 2.2 * fk);
  flashGlow.material.opacity = fk;
  flashLight.position.copy(lensPos).add(fwd.clone().multiplyScalar(0.3));
  flashLight.intensity = 26 * fk;
  whitePlane.material.opacity = a > -0.01 && a < 0.35 ? Math.exp(-Math.max(0, a) * 10) : 0;
  uiPlane.visible = t < T_FLASH + 0.05;
  if (fig.phone.visible && t < T_FLASH + 0.02) {
    phoneCam.position.copy(lensPos);
    phoneCam.lookAt(0.32, 1.12, -1.45);
    fig.root.visible = false;
    const sv = sparks.visible;
    renderer.setRenderTarget(rt);
    renderer.render(scene, phoneCam);
    renderer.setRenderTarget(null);
    fig.root.visible = true;
    sparks.visible = sv;
  }
  renderer.render(scene, camera);
}

// ---------------------------------------------------------------------------
// stills for the portfolio (called by tools/export-stills.mjs)
// ---------------------------------------------------------------------------
const STILLS = {
  "jules-portail": { show: "gate", pos: [2.2, 1.7, 3.6], tgt: [0.2, 1.0, -1.45], fov: 36 },
  "portail-detail": { show: "gate", pos: [1.1, 1.55, 0.2], tgt: [0.35, 1.25, -1.45], fov: 34 },
  "garde-corps": { show: "railing", pos: [1.9, 1.5, 2.6], tgt: [0.1, 0.62, -1.45], fov: 34 },
  "escalier": { show: "staircase", pos: [3.2, 2.2, 2.6], tgt: [0.1, 0.9, -1.1], fov: 36 },
};
window.__atelierStill = function (name, w = 1200, h = 900) {
  const s = STILLS[name];
  gate.visible = s.show === "gate";
  extra.railing.visible = s.show === "railing";
  extra.staircase.visible = s.show === "staircase";
  fig.root.visible = false;
  sparks.visible = weldGlow.visible = flashGlow.visible = false;
  weldLight.intensity = flashLight.intensity = 0;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.fov = s.fov;
  camera.position.set(...s.pos);
  camera.lookAt(...s.tgt);
  camera.updateProjectionMatrix();
  renderer.render(scene, camera);
  return canvas.toDataURL("image/png");
};

// ---------------------------------------------------------------------------
// HyperFrames wiring
// ---------------------------------------------------------------------------
window.__hf = window.__hf || {};
window.__hf.buildReady = window.__hf.buildReady || {};
let lastT = 0;
const readyP = Promise.resolve().then(() => renderAt(lastT));
window.__hf.buildReady["atelier"] = readyP;
window.addEventListener("hf-seek", (e) => {
  lastT = e.detail.time;
  renderAt(lastT);
});
window.__atelier = { renderAt };

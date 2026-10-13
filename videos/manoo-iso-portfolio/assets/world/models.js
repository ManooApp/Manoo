// Manoo iso world — models: figurines, réalisations, workshop props, buildings, phone, cards, paths.
import {
  THREE, C, M, mat, box, boxUp, cyl, sph, capsule, torus, prism, roundSlab, roundedPlane, at, grp, rng,
  makeCanvas, canvasTexture,
} from "./kit.js";

// ============================================================================
// Figurine (architect-model person). Faces +z. Origin on the ground.
// ============================================================================
export function figurine({
  top = C.acierClair,
  bottom = C.ombre,
  skin = C.peau,
  hat = null, // 'hardhat' | 'beanie' | 'cap' | null
  mask = false,
  apron = false,
  hair = null, // 'bun' | 'short' | null
  scale = 1.2,
} = {}) {
  const root = new THREE.Group();
  const body = new THREE.Group();
  root.add(body);
  root.scale.setScalar(scale);
  const mTop = mat(top, { rough: 0.85 });
  const mBottom = mat(bottom, { rough: 0.85 });
  const mSkin = mat(skin, { rough: 0.9 });

  const leg = (side) => {
    const g = new THREE.Group();
    g.position.set(side * 0.105, 0.84, 0);
    const m = capsule(0.088, 0.6, mBottom);
    m.position.y = -0.39;
    g.add(m);
    const foot = box(0.15, 0.08, 0.26, mat(C.ombre), { r: 0.03 });
    foot.position.set(0, -0.8, 0.05);
    g.add(foot);
    body.add(g);
    return g;
  };
  const legL = leg(1);
  const legR = leg(-1);

  const torso = new THREE.Group();
  torso.position.y = 0.84;
  body.add(torso);
  const torsoM = box(0.46, 0.64, 0.28, mTop, { r: 0.11, seg: 3 });
  torsoM.position.y = 0.33;
  torso.add(torsoM);
  if (apron) {
    const ap = box(0.4, 0.78, 0.04, mat(C.papier2), { r: 0.015 });
    ap.position.set(0, 0.18, 0.16);
    torso.add(ap);
  }

  const neck = new THREE.Group();
  neck.position.y = 0.66;
  torso.add(neck);
  const headM = sph(0.168, mSkin, 22);
  headM.position.y = 0.2;
  neck.add(headM);
  if (hair === "bun") {
    const hb = sph(0.172, mat(C.ombre), 20);
    hb.position.set(0, 0.215, -0.02);
    hb.scale.set(1, 0.92, 1);
    neck.add(hb);
    const bun = sph(0.075, mat(C.ombre), 14);
    bun.position.set(0, 0.36, -0.1);
    neck.add(bun);
    headM.position.z = 0.012;
  } else if (hair === "short") {
    const hs = sph(0.172, mat(C.ombre), 20);
    hs.position.set(0, 0.23, -0.015);
    hs.scale.set(1, 0.85, 1);
    neck.add(hs);
    headM.position.z = 0.01;
  }
  let hatMesh = null;
  if (hat === "hardhat") {
    hatMesh = new THREE.Group();
    const dome = new THREE.Mesh(
      new THREE.SphereGeometry(0.19, 22, 12, 0, Math.PI * 2, 0, Math.PI / 2),
      mat(C.papier, { rough: 0.5 }),
    );
    dome.castShadow = true;
    const brim = cyl(0.235, 0.235, 0.025, mat(C.papier, { rough: 0.5 }), 24);
    brim.position.z = 0.03;
    hatMesh.add(dome, brim);
    hatMesh.position.y = 0.27;
    neck.add(hatMesh);
  } else if (hat === "beanie") {
    hatMesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.178, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2),
      mat(C.ombre),
    );
    hatMesh.position.y = 0.25;
    hatMesh.castShadow = true;
    neck.add(hatMesh);
  }
  // welding mask hinged at the top of the head
  let maskPivot = null;
  if (mask) {
    maskPivot = new THREE.Group();
    maskPivot.position.set(0, 0.33, 0.02);
    const shell = box(0.34, 0.36, 0.1, mat(C.ombre, { rough: 0.5, metal: 0.3 }), { r: 0.05 });
    shell.position.set(0, -0.15, 0.17);
    const visor = box(0.2, 0.07, 0.02, mat(0x0b0f12, { rough: 0.2, metal: 0.6 }), { r: 0.01 });
    visor.position.set(0, -0.11, 0.225);
    const strap = box(0.36, 0.05, 0.36, mat(C.ombre), { r: 0.02 });
    strap.position.set(0, -0.02, 0);
    maskPivot.add(shell, visor, strap);
    neck.add(maskPivot);
  }

  const arm = (side) => {
    const sh = new THREE.Group();
    sh.rotation.order = "YXZ";
    sh.position.set(side * 0.29, 0.56, 0);
    torso.add(sh);
    const up = capsule(0.07, 0.2, mTop);
    up.position.y = -0.14;
    sh.add(up);
    const el = new THREE.Group();
    el.position.y = -0.3;
    sh.add(el);
    const fo = capsule(0.064, 0.17, mTop);
    fo.position.y = -0.12;
    el.add(fo);
    const hand = new THREE.Group();
    hand.position.y = -0.27;
    el.add(hand);
    const hm = sph(0.064, mSkin, 14);
    hand.add(hm);
    return { sh, el, hand };
  };
  const armL = arm(1);
  const armR = arm(-1);

  // phone held in front of the face (torso space), shown only when "held"
  const phoneHold = new THREE.Group();
  phoneHold.position.set(0, 0.76, 0.42);
  torso.add(phoneHold);
  const phone = new THREE.Group();
  const pb = box(0.16, 0.3, 0.025, mat(C.encre, { rough: 0.35, metal: 0.4 }), { r: 0.012 });
  const lens = cyl(0.022, 0.022, 0.012, mat(0x0b0f12, { rough: 0.2 }), 12);
  lens.rotation.x = Math.PI / 2;
  lens.position.set(-0.045, 0.1, 0.018);
  const scr = new THREE.Mesh(
    new THREE.PlaneGeometry(0.14, 0.27),
    new THREE.MeshBasicMaterial({ color: 0xf3f2ef, toneMapped: false }),
  );
  scr.position.z = -0.0135;
  scr.rotation.y = Math.PI;
  phone.add(pb, lens, scr);
  phoneHold.add(phone);
  phone.visible = false;

  const fig = {
    root, body, torso, neck, legL, legR, armL, armR, maskPivot, phoneHold, phone, hatMesh,
    // flash anchor = back of the phone, in world space
    flashAnchor: (() => {
      const a = new THREE.Object3D();
      a.position.set(-0.045, 0.1, 0.05);
      phone.add(a);
      return a;
    })(),
  };
  setPose(fig, POSES.idle);
  return fig;
}

// Pose = plain numbers; blended with lerpPose().
export const POSES = {
  idle: { lsx: 0.08, lsy: 0, lsz: 0.06, lel: -0.15, rsx: 0.08, rsy: 0, rsz: -0.06, rel: -0.15, hx: 0, hy: 0, lean: 0, mask: 0, legL: 0, legR: 0 },
  photo: { lsx: -1.38, lsy: -0.56, lsz: 0, lel: -1.12, rsx: -1.38, rsy: 0.56, rsz: 0, rel: -1.12, hx: 0.06, hy: 0, lean: -0.04, mask: 0, legL: 0.06, legR: -0.1 },
  weld: { lsx: -0.55, lsy: -0.2, lsz: 0.1, lel: -0.9, rsx: -0.95, rsy: 0.25, rsz: 0, rel: -0.55, hx: 0.38, hy: 0, lean: 0.22, mask: 0, legL: 0.25, legR: -0.12 },
  lookUp: { lsx: 0.05, lsy: 0, lsz: 0.08, lel: -0.25, rsx: 0.05, rsy: 0, rsz: -0.08, rel: -0.25, hx: -0.38, hy: 0, lean: -0.05, mask: 0, legL: 0, legR: 0 },
  point: { lsx: 0.05, lsy: 0, lsz: 0.08, lel: -0.2, rsx: -2.1, rsy: 0.25, rsz: 0, rel: -0.15, hx: -0.4, hy: 0, lean: -0.06, mask: 0, legL: 0, legR: 0 },
  tablet: { lsx: -0.75, lsy: -0.42, lsz: 0, lel: -1.0, rsx: -0.75, rsy: 0.42, rsz: 0, rel: -1.0, hx: 0.42, hy: 0, lean: 0.05, mask: 0, legL: -1.45, legR: -1.45 },
  sit: { lsx: -0.2, lsy: 0, lsz: 0.08, lel: -0.6, rsx: -0.2, rsy: 0, rsz: -0.08, rel: -0.6, hx: 0, hy: 0, lean: 0, mask: 0, legL: -1.45, legR: -1.45 },
  armsCrossed: { lsx: -0.55, lsy: -0.75, lsz: 0, lel: -1.7, rsx: -0.6, rsy: 0.75, rsz: 0, rel: -1.7, hx: -0.3, hy: 0, lean: -0.03, mask: 0, legL: 0, legR: 0 },
};
export function lerpPose(a, b, p) {
  const o = {};
  for (const k in a) o[k] = a[k] + ((b[k] ?? a[k]) - a[k]) * p;
  return o;
}
export function setPose(fig, p) {
  fig.armL.sh.rotation.set(p.lsx, p.lsy, p.lsz);
  fig.armL.el.rotation.x = p.lel;
  fig.armR.sh.rotation.set(p.rsx, p.rsy, p.rsz);
  fig.armR.el.rotation.x = p.rel;
  fig.neck.rotation.set(p.hx, p.hy, 0);
  fig.torso.rotation.x = p.lean;
  fig.legL.rotation.x = p.legL;
  fig.legR.rotation.x = p.legR;
  if (fig.maskPivot) fig.maskPivot.rotation.x = -2.35 * p.mask;
}

// ============================================================================
// Islands
// ============================================================================
export function island(w = 10, d = 10, { floor = C.papier2, floorTex = null, thickness = 1.3 } = {}) {
  const g = new THREE.Group();
  const slab = box(w, thickness, d, mat(C.encre2, { rough: 0.95 }), { r: 0.18, seg: 3 });
  slab.position.y = -thickness / 2 - 0.06;
  g.add(slab);
  const topMat = floorTex
    ? new THREE.MeshStandardMaterial({ color: floor, map: floorTex, roughness: 0.92 })
    : mat(floor, { rough: 0.92 });
  const top = box(w - 0.24, 0.12, d - 0.24, topMat, { r: 0.04, cast: false });
  top.position.y = -0.06;
  g.add(top);
  return g;
}

export function floorTexture(kind, seed = 1) {
  const c = makeCanvas(512, 512);
  const g = c.getContext("2d");
  const r = rng(seed);
  g.fillStyle = "#ffffff";
  g.fillRect(0, 0, 512, 512);
  if (kind === "tiles" || kind === "courtyard") {
    const n = kind === "tiles" ? 8 : 6;
    const s = 512 / n;
    for (let i = 0; i < n; i++)
      for (let j = 0; j < n; j++) {
        const v = 238 + Math.floor(r() * 12);
        g.fillStyle = `rgb(${v},${v - 1},${v - 3})`;
        g.fillRect(i * s, j * s, s, s);
      }
    g.strokeStyle = "rgba(120,134,143,0.35)";
    g.lineWidth = 3;
    for (let i = 0; i <= n; i++) {
      g.beginPath(); g.moveTo(i * s, 0); g.lineTo(i * s, 512); g.stroke();
      g.beginPath(); g.moveTo(0, i * s); g.lineTo(512, i * s); g.stroke();
    }
  } else if (kind === "planks") {
    const n = 10;
    const s = 512 / n;
    for (let i = 0; i < n; i++) {
      const v = 236 + Math.floor(r() * 14);
      g.fillStyle = `rgb(${v},${v - 3},${v - 8})`;
      g.fillRect(0, i * s, 512, s);
      g.strokeStyle = "rgba(120,110,100,0.3)";
      g.lineWidth = 2;
      g.beginPath(); g.moveTo(0, i * s); g.lineTo(512, i * s); g.stroke();
      const off = r() * 512;
      g.beginPath(); g.moveTo(off, i * s); g.lineTo(off, (i + 1) * s); g.stroke();
    }
  } else if (kind === "earth") {
    for (let i = 0; i < 2600; i++) {
      const v = 200 + Math.floor(r() * 50);
      g.fillStyle = `rgba(${v},${v - 4},${v - 10},0.35)`;
      g.fillRect(r() * 512, r() * 512, 2 + r() * 4, 2 + r() * 4);
    }
  } else if (kind === "asphalt") {
    g.fillStyle = "#d9d9d9";
    g.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 3000; i++) {
      const v = 180 + Math.floor(r() * 60);
      g.fillStyle = `rgba(${v},${v},${v},0.4)`;
      g.fillRect(r() * 512, r() * 512, 2, 2);
    }
    g.fillStyle = "rgba(255,255,255,0.9)";
    for (let i = 0; i < 4; i++) g.fillRect(40 + i * 120, 330, 10, 150);
  } else if (kind === "lawn") {
    g.fillStyle = "#e4e4df";
    g.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 5000; i++) {
      const v = 190 + Math.floor(r() * 50);
      g.fillStyle = `rgba(${v},${v + 4},${v - 2},0.45)`;
      g.fillRect(r() * 512, r() * 512, 2, 3 + r() * 3);
    }
    g.fillStyle = "#f1efea";
    g.fillRect(0, 380, 512, 132); // path
  }
  const tex = canvasTexture(c);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  return tex;
}

// back walls of a cut-away room (far edges of the island: -x and -z)
export function cornerWalls(w = 10, d = 10, h = 3, { color = C.papier2, windowOnLeft = true } = {}) {
  const g = new THREE.Group();
  const t = 0.28;
  const wm = mat(color, { rough: 0.92 });
  const left = box(t, h, d - 0.24, wm, { r: 0.03 });
  left.position.set(-w / 2 + 0.12 + t / 2, h / 2, 0);
  const right = box(w - 0.24, h, t, wm, { r: 0.03 });
  right.position.set(0, h / 2, -d / 2 + 0.12 + t / 2);
  g.add(left, right);
  // skirting + top cap in darker tone for edge definition
  const capM = mat(C.acierClair, { rough: 0.8 });
  const capL = box(t + 0.04, 0.08, d - 0.2, capM, { r: 0.02 });
  capL.position.set(left.position.x, h + 0.04, 0);
  const capR = box(w - 0.2, 0.08, t + 0.04, capM, { r: 0.02 });
  capR.position.set(0, h + 0.04, right.position.z);
  g.add(capL, capR);
  if (windowOnLeft) {
    // window on the left wall: frame + mullions + glass
    const win = new THREE.Group();
    const glass = box(0.06, 1.3, 2.4, M.vitre(), { r: 0.01 });
    const frameM = mat(C.acier, { rough: 0.6, metal: 0.3 });
    win.add(glass);
    for (const z of [-1.2, -0.4, 0.4, 1.2]) {
      const mull = box(0.1, 1.36, 0.06, frameM, { r: 0.01 });
      mull.position.z = z;
      win.add(mull);
    }
    for (const y of [-0.65, 0, 0.65]) {
      const tr = box(0.1, 0.06, 2.46, frameM, { r: 0.01 });
      tr.position.y = y;
      win.add(tr);
    }
    win.position.set(left.position.x + t / 2 + 0.02, 1.75, 1.6);
    g.add(win);
  }
  return g;
}

// ============================================================================
// Réalisations (orange = the work)
// ============================================================================
export function gate() {
  const g = new THREE.Group();
  const om = M.orange();
  const W = 2.6;
  const post = (x) => {
    const p = box(0.1, 2.0, 0.1, om, { r: 0.015 });
    p.position.set(x, 1.0, 0);
    const cap = sph(0.07, om, 12);
    cap.position.set(x, 2.06, 0);
    const foot = box(0.42, 0.05, 0.3, mat(C.acier, { rough: 0.6, metal: 0.3 }), { r: 0.01 });
    foot.position.set(x, 0.025, 0);
    g.add(p, cap, foot);
  };
  post(-W / 2);
  post(W / 2);
  for (const y of [0.18, 1.12, 1.72]) {
    const rail = box(W, 0.075, 0.07, om, { r: 0.012 });
    rail.position.set(0, y, 0);
    g.add(rail);
  }
  const nBars = 11;
  for (let i = 0; i < nBars; i++) {
    const x = -W / 2 + (W / (nBars + 1)) * (i + 1);
    const bar = box(0.036, 1.72, 0.036, om, { r: 0.006 });
    bar.position.set(x, 0.18 + 0.86 + 0.03, 0);
    const tip = new THREE.Mesh(new THREE.ConeGeometry(0.045, 0.14, 4), om);
    tip.position.set(x, 1.98, 0);
    tip.rotation.y = Math.PI / 4;
    tip.castShadow = true;
    g.add(bar, tip);
  }
  // scroll band: rings + C-scrolls between mid and top rails
  for (let i = 0; i < 6; i++) {
    const x = -W / 2 + (W / 6) * (i + 0.5);
    const ring = torus(0.15, 0.018, Math.PI * 2, om);
    ring.position.set(x, 1.42, 0);
    g.add(ring);
    const s1 = torus(0.08, 0.016, Math.PI * 1.4, om);
    s1.position.set(x, 0.5, 0);
    s1.rotation.z = i % 2 ? 0.3 : Math.PI + 0.3;
    g.add(s1);
  }
  g.userData.weldPoint = new THREE.Vector3(0.43, 1.12, 0.06);
  return g;
}

export function brickWalls() {
  const g = new THREE.Group();
  const BL = 0.46, BH = 0.2, BD = 0.22, J = 0.035;
  const course = BH + J;
  const bricks = [];
  const r = rng(7);
  // wall A along +x (length 5) at z=0 ; wall B along +z (length 4) at x=0 (corner at origin)
  const addWall = (len, axis, courses, opening, partialTop) => {
    for (let c = 0; c < courses; c++) {
      const off = c % 2 ? BL / 2 + J / 2 : 0;
      const y = c * course + BH / 2;
      const isTop = c === courses - 1;
      for (let s = -off; s < len - 0.05; s += BL + J) {
        const a = Math.max(0, s);
        const b = Math.min(len, s + BL);
        if (b - a < 0.12) continue;
        const mid = (a + b) / 2;
        if (opening && mid > opening[0] && mid < opening[1] && y > opening[2] && y < opening[3]) continue;
        if (isTop && mid > len * partialTop) continue;
        bricks.push({ axis, mid, len: b - a, y, jitter: r() });
      }
    }
  };
  addWall(5.0, "x", 10, [1.1, 2.5, 0.85, 1.95], 0.62);
  addWall(4.0, "z", 10, [1.4, 2.4, -1, 1.85], 1.0);
  const geo = new THREE.BoxGeometry(1, 1, 1);
  const inst = new THREE.InstancedMesh(geo, mat(C.orange, { rough: 0.85 }), bricks.length);
  const m4 = new THREE.Matrix4();
  const col = new THREE.Color();
  bricks.forEach((b, i) => {
    const sx = b.axis === "x" ? b.len : BD;
    const sz = b.axis === "x" ? BD : b.len;
    const x = b.axis === "x" ? b.mid : BD / 2;
    const z = b.axis === "x" ? BD / 2 : b.mid;
    m4.makeScale(sx, BH, sz);
    m4.setPosition(x, b.y, z);
    inst.setMatrixAt(i, m4);
    const k = 0.86 + b.jitter * 0.2;
    col.setRGB(k, k, k);
    inst.setColorAt(i, col);
  });
  inst.castShadow = true;
  inst.receiveShadow = true;
  g.add(inst);
  // mortar cores (show through the joints)
  const mortar = mat(C.pierre, { rough: 0.95 });
  const coreA = box(4.98, 9 * course + BH, BD * 0.8, mortar, { r: 0.005 });
  coreA.position.set(2.49, (9 * course + BH) / 2, BD / 2);
  const coreB = box(BD * 0.8, 9 * course + BH, 3.98, mortar, { r: 0.005 });
  coreB.position.set(BD / 2, (9 * course + BH) / 2, 1.99);
  g.add(coreA, coreB);
  // concrete lintels over openings
  const lint = box(1.7, 0.16, BD + 0.02, mat(C.pierre), { r: 0.01 });
  lint.position.set(1.8, 2.04, BD / 2);
  g.add(lint);
  const lint2 = box(BD + 0.02, 0.16, 1.3, mat(C.pierre), { r: 0.01 });
  lint2.position.set(BD / 2, 1.94, 1.9);
  g.add(lint2);
  return g;
}

export function cabinet() {
  const g = new THREE.Group();
  const wood = mat(C.orange, { rough: 0.72 });
  const woodDark = mat(C.orangeFonce, { rough: 0.8 });
  const W = 1.7, H = 0.92, D = 0.62, LEG = 0.26;
  const carcass = box(W, H, D, woodDark, { r: 0.02 });
  carcass.position.y = LEG + H / 2;
  const topB = box(W + 0.12, 0.07, D + 0.1, wood, { r: 0.025 });
  topB.position.y = LEG + H + 0.035;
  g.add(carcass, topB);
  for (let i = 0; i < 3; i++) {
    const fh = (H - 0.12) / 3 - 0.03;
    const front = box(W - 0.1, fh, 0.04, wood, { r: 0.012 });
    const y = LEG + 0.06 + fh / 2 + i * (fh + 0.03) + 0.015;
    front.position.set(0, y, D / 2 + 0.012);
    const knobM = mat(C.papier, { rough: 0.35, metal: 0.4 });
    const k1 = sph(0.028, knobM, 10);
    k1.position.set(-0.4, y, D / 2 + 0.05);
    const k2 = sph(0.028, knobM, 10);
    k2.position.set(0.4, y, D / 2 + 0.05);
    g.add(front, k1, k2);
  }
  for (const [x, z] of [[-W / 2 + 0.08, -D / 2 + 0.08], [W / 2 - 0.08, -D / 2 + 0.08], [-W / 2 + 0.08, D / 2 - 0.08], [W / 2 - 0.08, D / 2 - 0.08]]) {
    const leg = cyl(0.045, 0.03, LEG, woodDark, 12);
    leg.position.set(x, LEG / 2, z);
    g.add(leg);
  }
  // a small paper vase on top for staging
  const vase = cyl(0.07, 0.1, 0.28, mat(C.papier, { rough: 0.6 }), 18);
  vase.position.set(0.5, LEG + H + 0.07 + 0.14, -0.05);
  g.add(vase);
  return g;
}

// ============================================================================
// Workshop & site props (paper / steel)
// ============================================================================
export function workbench({ w = 2.6, d = 1.0, top = C.acierClair, legs = C.ombre, vise = true } = {}) {
  const g = new THREE.Group();
  const tm = mat(top, { rough: 0.7, metal: 0.15 });
  const lm = mat(legs, { rough: 0.6, metal: 0.3 });
  const tp = box(w, 0.1, d, tm, { r: 0.02 });
  tp.position.y = 0.95;
  g.add(tp);
  for (const [x, z] of [[-w / 2 + 0.1, -d / 2 + 0.1], [w / 2 - 0.1, -d / 2 + 0.1], [-w / 2 + 0.1, d / 2 - 0.1], [w / 2 - 0.1, d / 2 - 0.1]]) {
    const l = box(0.08, 0.9, 0.08, lm, { r: 0.01 });
    l.position.set(x, 0.45, z);
    g.add(l);
  }
  const shelf = box(w - 0.2, 0.05, d - 0.2, tm, { r: 0.01 });
  shelf.position.y = 0.25;
  g.add(shelf);
  if (vise) {
    const v = grp(
      at(box(0.22, 0.18, 0.28, lm, { r: 0.02 }), 0, 0.09, 0),
      at(box(0.24, 0.1, 0.06, lm, { r: 0.015 }), 0, 0.2, 0.12),
      at(box(0.24, 0.1, 0.06, lm, { r: 0.015 }), 0, 0.2, -0.04),
    );
    v.position.set(w / 2 - 0.3, 1.0, d / 2 - 0.2);
    g.add(v);
  }
  return g;
}
export function anvil() {
  const g = new THREE.Group();
  const m = mat(C.ombre, { rough: 0.45, metal: 0.55 });
  const stump = cyl(0.32, 0.36, 0.55, mat(C.acier, { rough: 0.8 }), 18);
  stump.position.y = 0.275;
  const base = box(0.36, 0.2, 0.26, m, { r: 0.03 });
  base.position.y = 0.65;
  const waist = box(0.2, 0.16, 0.18, m, { r: 0.02 });
  waist.position.y = 0.82;
  const face = box(0.62, 0.14, 0.24, m, { r: 0.025 });
  face.position.y = 0.96;
  const horn = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.36, 14), m);
  horn.rotation.z = Math.PI / 2;
  horn.position.set(0.48, 0.97, 0);
  horn.castShadow = true;
  g.add(stump, base, waist, face, horn);
  return g;
}
export function gasBottles() {
  const g = new THREE.Group();
  const cols = [C.acier, C.ombre];
  [-0.22, 0.22].forEach((x, i) => {
    const m = mat(cols[i], { rough: 0.5, metal: 0.3 });
    const b = cyl(0.17, 0.17, 1.2, m, 18);
    b.position.set(x, 0.6, 0);
    const dome = sph(0.17, m, 16);
    dome.position.set(x, 1.2, 0);
    const valve = cyl(0.04, 0.04, 0.14, mat(C.papier, { rough: 0.4, metal: 0.5 }), 10);
    valve.position.set(x, 1.4, 0);
    g.add(b, dome, valve);
  });
  const welder = box(0.6, 0.5, 0.42, mat(C.acierClair, { rough: 0.6 }), { r: 0.04 });
  welder.position.set(0.85, 0.25, 0.1);
  const panel = box(0.4, 0.2, 0.02, mat(C.ombre), { r: 0.01 });
  panel.position.set(0.85, 0.32, 0.32);
  g.add(welder, panel);
  return g;
}
export function pegboard(w = 2.4, h = 1.3) {
  const g = new THREE.Group();
  const board = box(w, h, 0.05, mat(C.pierre, { rough: 0.95 }), { r: 0.01 });
  board.position.set(0, h / 2, 0);
  g.add(board);
  const tm = mat(C.ombre, { rough: 0.5, metal: 0.4 });
  const r = rng(3);
  for (let i = 0; i < 7; i++) {
    const x = -w / 2 + 0.25 + i * ((w - 0.5) / 6);
    const len = 0.35 + r() * 0.4;
    const handle = box(0.05, len, 0.04, tm, { r: 0.01 });
    handle.position.set(x, h - 0.25 - len / 2, 0.05);
    g.add(handle);
    if (i % 2 === 0) {
      const head = box(0.2, 0.07, 0.05, tm, { r: 0.012 });
      head.position.set(x, h - 0.22, 0.05);
      g.add(head);
    }
  }
  return g;
}
export function barRack() {
  const g = new THREE.Group();
  const fm = mat(C.ombre, { rough: 0.6, metal: 0.3 });
  for (const x of [-1.1, 1.1]) {
    const up = box(0.08, 1.2, 0.5, fm, { r: 0.01 });
    up.position.set(x, 0.6, 0);
    g.add(up);
  }
  const bm = mat(C.acier, { rough: 0.45, metal: 0.5 });
  for (let i = 0; i < 9; i++) {
    const bar = box(2.6, 0.05, 0.05, bm, { r: 0.008 });
    bar.position.set(0, 0.35 + Math.floor(i / 3) * 0.32, -0.15 + (i % 3) * 0.15);
    g.add(bar);
  }
  return g;
}
export function shelfUnit(w = 1.6, h = 2.0) {
  const g = new THREE.Group();
  const fm = mat(C.acier, { rough: 0.6, metal: 0.3 });
  for (const x of [-w / 2, w / 2]) {
    const up = box(0.06, h, 0.5, fm, { r: 0.01 });
    up.position.set(x, h / 2, 0);
    g.add(up);
  }
  const r = rng(11);
  for (let i = 0; i < 4; i++) {
    const s = box(w, 0.04, 0.5, fm, { r: 0.01 });
    s.position.set(0, 0.1 + i * 0.6, 0);
    g.add(s);
    let x = -w / 2 + 0.12;
    while (x < w / 2 - 0.25) {
      const bw = 0.18 + r() * 0.3;
      const bh = 0.15 + r() * 0.3;
      const c = r() > 0.5 ? C.papier : C.acierClair;
      const bx = box(bw, bh, 0.36, mat(c, { rough: 0.9 }), { r: 0.015 });
      bx.position.set(x + bw / 2, 0.12 + i * 0.6 + bh / 2, 0);
      g.add(bx);
      x += bw + 0.05;
    }
  }
  return g;
}
export function scaffolding(len = 4.6, h = 2.7) {
  const g = new THREE.Group();
  const pm = mat(C.acier, { rough: 0.45, metal: 0.5 });
  const bays = 3;
  for (let i = 0; i <= bays; i++) {
    const x = (len / bays) * i;
    for (const z of [0, 0.8]) {
      const p = cyl(0.03, 0.03, h, pm, 8);
      p.position.set(x, h / 2, z);
      g.add(p);
    }
  }
  const plankM = mat(C.papier2, { rough: 0.9 });
  for (const y of [1.2, 2.4]) {
    const plank = box(len + 0.1, 0.05, 0.75, plankM, { r: 0.01 });
    plank.position.set(len / 2, y, 0.4);
    g.add(plank);
    const rail = cyl(0.022, 0.022, len, pm, 8);
    rail.rotation.z = Math.PI / 2;
    rail.position.set(len / 2, y + 0.5, 0.8);
    g.add(rail);
  }
  return g;
}
export function cementMixer() {
  const g = new THREE.Group();
  const fm = mat(C.ombre, { rough: 0.6, metal: 0.3 });
  const dm = mat(C.acierClair, { rough: 0.55, metal: 0.25 });
  const frame = box(0.9, 0.1, 0.5, fm, { r: 0.02 });
  frame.position.y = 0.35;
  const legA = box(0.06, 0.7, 0.06, fm);
  legA.position.set(-0.35, 0.35, 0);
  const wheel = cyl(0.17, 0.17, 0.08, fm, 16);
  wheel.rotation.x = Math.PI / 2;
  wheel.position.set(0.35, 0.17, 0.26);
  const drum = new THREE.Group();
  const d1 = cyl(0.42, 0.32, 0.5, dm, 20);
  const d2 = cyl(0.2, 0.42, 0.34, dm, 20);
  d2.position.y = 0.42;
  drum.add(d1, d2);
  drum.rotation.z = -0.7;
  drum.position.set(0, 0.85, 0);
  g.add(frame, legA, wheel, drum);
  return g;
}
export function wheelbarrow() {
  const g = new THREE.Group();
  const tray = prism(0.9, 0.4, 0.6, mat(C.acierClair, { rough: 0.55, metal: 0.3 }), 0.5);
  tray.rotation.x = Math.PI;
  tray.position.set(0, 0.62, 0);
  const wheel = cyl(0.16, 0.16, 0.07, mat(C.ombre), 14);
  wheel.rotation.x = Math.PI / 2;
  wheel.position.set(0.48, 0.16, 0);
  const h1 = box(0.9, 0.04, 0.04, mat(C.ombre));
  h1.position.set(-0.55, 0.5, 0.22);
  const h2 = h1.clone();
  h2.position.z = -0.22;
  g.add(tray, wheel, h1, h2);
  return g;
}
export function pallet(blocks = true) {
  const g = new THREE.Group();
  const wm = mat(C.papier2, { rough: 0.95 });
  for (const z of [-0.4, 0, 0.4]) {
    const s = box(1.1, 0.12, 0.14, wm, { r: 0.01 });
    s.position.set(0, 0.06, z);
    g.add(s);
  }
  const deck = box(1.2, 0.04, 1.0, wm, { r: 0.01 });
  deck.position.y = 0.14;
  g.add(deck);
  if (blocks) {
    const bm = mat(C.pierre, { rough: 0.95 });
    for (let l = 0; l < 3; l++)
      for (let i = 0; i < 2; i++)
        for (let j = 0; j < 3; j++) {
          const b = box(0.5, 0.2, 0.28, bm, { r: 0.015 });
          b.position.set(-0.27 + i * 0.54, 0.26 + l * 0.22, -0.32 + j * 0.32);
          g.add(b);
        }
  }
  return g;
}
export function lumberRack() {
  const g = new THREE.Group();
  const fm = mat(C.acier, { rough: 0.6, metal: 0.3 });
  for (const x of [-1.0, 0, 1.0]) {
    const up = box(0.07, 1.6, 0.07, fm);
    up.position.set(x, 0.8, -0.2);
    g.add(up);
    for (const y of [0.4, 0.85, 1.3]) {
      const arm = box(0.05, 0.05, 0.5, fm);
      arm.position.set(x, y, 0.05);
      g.add(arm);
    }
  }
  const r = rng(5);
  for (const y of [0.45, 0.9, 1.35]) {
    for (let i = 0; i < 4; i++) {
      const c = r() > 0.4 ? C.papier2 : C.filet;
      const b = box(2.5, 0.06, 0.1, mat(c, { rough: 0.85 }), { r: 0.008 });
      b.position.set(0, y + 0.03 + (i % 2) * 0.06, -0.12 + i * 0.1);
      g.add(b);
    }
  }
  return g;
}
export function shavings(seed = 9, n = 14, spread = 1.0) {
  const g = new THREE.Group();
  const r = rng(seed);
  const m = mat(C.papier, { rough: 0.9 });
  for (let i = 0; i < n; i++) {
    const s = torus(0.05 + r() * 0.04, 0.012, Math.PI * (1 + r()), m);
    s.position.set((r() - 0.5) * spread, 0.02, (r() - 0.5) * spread);
    s.rotation.set(Math.PI / 2 + (r() - 0.5) * 0.6, r() * 6, 0);
    g.add(s);
  }
  return g;
}
export function tree({ h = 2.4, r = 0.8, kind = "round" } = {}) {
  const g = new THREE.Group();
  const trunk = cyl(0.07, 0.1, h * 0.45, mat(C.acier, { rough: 0.9 }), 10);
  trunk.position.y = h * 0.225;
  g.add(trunk);
  const cm = mat(C.acierClair, { rough: 0.95 });
  if (kind === "round") {
    const c1 = sph(r, cm, 16);
    c1.position.y = h * 0.62;
    const c2 = sph(r * 0.7, cm, 14);
    c2.position.set(r * 0.45, h * 0.5, r * 0.2);
    g.add(c1, c2);
  } else {
    const cone = new THREE.Mesh(new THREE.ConeGeometry(r, h * 0.8, 10), cm);
    cone.position.y = h * 0.6;
    cone.castShadow = true;
    g.add(cone);
  }
  return g;
}
export function bench() {
  const g = new THREE.Group();
  const wm = mat(C.papier2, { rough: 0.9 });
  const fm = mat(C.ombre, { rough: 0.6, metal: 0.3 });
  const seat = box(1.4, 0.06, 0.45, wm, { r: 0.015 });
  seat.position.y = 0.45;
  const back = box(1.4, 0.35, 0.05, wm, { r: 0.015 });
  back.position.set(0, 0.72, -0.2);
  g.add(seat, back);
  for (const x of [-0.6, 0.6]) {
    const l = box(0.06, 0.45, 0.42, fm, { r: 0.01 });
    l.position.set(x, 0.225, 0);
    g.add(l);
  }
  return g;
}
export function fence(len, { posts = 8 } = {}) {
  const g = new THREE.Group();
  const m = mat(C.papier, { rough: 0.85 });
  for (let i = 0; i <= posts; i++) {
    const p = box(0.08, 0.6, 0.08, m, { r: 0.01 });
    p.position.set((len / posts) * i, 0.3, 0);
    g.add(p);
  }
  for (const y of [0.22, 0.48]) {
    const rail = box(len, 0.05, 0.04, m, { r: 0.008 });
    rail.position.set(len / 2, y, 0);
    g.add(rail);
  }
  return g;
}

// window grid on a façade: returns {group, material}
export function windowGrid(cols, rows, w, h, gapX, gapY, material) {
  const g = new THREE.Group();
  for (let i = 0; i < cols; i++)
    for (let j = 0; j < rows; j++) {
      const p = box(w, h, 0.05, material, { r: 0.01, cast: false });
      p.position.set((i - (cols - 1) / 2) * (w + gapX), (j - (rows - 1) / 2) * (h + gapY), 0);
      g.add(p);
    }
  return g;
}

// ============================================================================
// Buildings for the three audiences
// ============================================================================
export function factory(winMat) {
  const g = new THREE.Group();
  const wall = mat(C.papier, { rough: 0.9 });
  const wall2 = mat(C.papier2, { rough: 0.9 });
  // hall
  const hall = box(5.6, 2.6, 4.0, wall, { r: 0.04 });
  hall.position.set(0, 1.3, 0);
  g.add(hall);
  // sawtooth roof: 4 teeth along x, glazing faces +x... (glazed vertical side)
  for (let i = 0; i < 4; i++) {
    const tooth = prism(1.4, 0.9, 4.0, wall2, 1.0);
    tooth.position.set(-2.8 + 0.7 + i * 1.4, 2.6, 0);
    g.add(tooth);
    const glaze = box(0.04, 0.8, 3.8, winMat, { r: 0.005, cast: false });
    glaze.position.set(-2.8 + 1.4 + i * 1.4 - 0.03, 3.02, 0);
    g.add(glaze);
  }
  // roller door on the front (+z) face
  const door = box(1.8, 1.9, 0.06, mat(C.acierClair, { rough: 0.7, metal: 0.2 }), { r: 0.01 });
  door.position.set(-1.2, 0.95, 2.02);
  g.add(door);
  for (let i = 0; i < 8; i++) {
    const slat = box(1.8, 0.02, 0.08, mat(C.acier), { r: 0.004, cast: false });
    slat.position.set(-1.2, 0.2 + i * 0.22, 2.04);
    g.add(slat);
  }
  // side windows on +z face
  const wz = windowGrid(3, 1, 0.55, 0.7, 0.2, 0, winMat);
  wz.position.set(1.2, 1.6, 2.03);
  g.add(wz);
  // office block (+x side)
  const office = box(2.4, 4.2, 2.6, wall2, { r: 0.04 });
  office.position.set(3.95, 2.1, 0.5);
  g.add(office);
  const wx = windowGrid(2, 4, 0.7, 0.55, 0.3, 0.38, winMat);
  wx.rotation.y = Math.PI / 2;
  wx.position.set(5.17, 2.25, 0.5);
  g.add(wx);
  const wz2 = windowGrid(2, 4, 0.7, 0.55, 0.3, 0.38, winMat);
  wz2.position.set(3.95, 2.25, 1.82);
  g.add(wz2);
  const roofCap = box(2.5, 0.12, 2.7, mat(C.acierClair), { r: 0.02 });
  roofCap.position.set(3.95, 4.26, 0.5);
  g.add(roofCap);
  return g;
}
export function school(winMat) {
  const g = new THREE.Group();
  const wall = mat(C.papier, { rough: 0.9 });
  const wall2 = mat(C.papier2, { rough: 0.9 });
  const main = box(7.0, 3.4, 2.8, wall, { r: 0.04 });
  main.position.set(0, 1.7, 0);
  g.add(main);
  const roof = box(7.2, 0.14, 3.0, mat(C.acierClair), { r: 0.02 });
  roof.position.set(0, 3.47, 0);
  g.add(roof);
  // two rows of windows on +z face (front)
  for (const y of [1.05, 2.45]) {
    const row = windowGrid(7, 1, 0.6, 0.75, 0.32, 0, winMat);
    row.position.set(0, y, 1.42);
    g.add(row);
  }
  // side (+x) windows
  for (const y of [1.05, 2.45]) {
    const row = windowGrid(2, 1, 0.6, 0.75, 0.4, 0, winMat);
    row.rotation.y = Math.PI / 2;
    row.position.set(3.52, y, 0);
    g.add(row);
  }
  // entrance portico
  const portico = box(2.2, 0.16, 1.1, wall2, { r: 0.02 });
  portico.position.set(-1.2, 2.0, 1.85);
  g.add(portico);
  for (const x of [-2.15, -0.25]) {
    const col = cyl(0.07, 0.07, 1.95, wall2, 12);
    col.position.set(x, 0.98, 2.3);
    g.add(col);
  }
  const door = box(1.0, 1.5, 0.05, mat(C.vitre, { rough: 0.4 }), { r: 0.01 });
  door.position.set(-1.2, 0.75, 1.42);
  g.add(door);
  // pediment block with sign plate (blank, the label lives in the overlay)
  const sign = box(2.6, 0.5, 0.08, mat(C.acierClair), { r: 0.02 });
  sign.position.set(1.3, 3.05, 1.45);
  g.add(sign);
  return g;
}
export function house(winMat) {
  const g = new THREE.Group();
  const wall = mat(C.papier, { rough: 0.9 });
  const main = box(3.6, 2.3, 3.0, wall, { r: 0.04 });
  main.position.set(0, 1.15, 0);
  g.add(main);
  const roof = prism(3.6, 1.4, 3.3, mat(C.acier, { rough: 0.85 }), 0.5);
  roof.rotation.y = Math.PI / 2;
  roof.position.set(0, 2.3, 0);
  roof.scale.set(1, 1, 1.12);
  g.add(roof);
  const gable = prism(3.0, 1.3, 3.58, wall, 0.5);
  gable.rotation.y = Math.PI / 2;
  gable.position.set(0, 2.3, 0);
  g.add(gable);
  const chimney = box(0.4, 1.1, 0.4, mat(C.papier2), { r: 0.02 });
  chimney.position.set(-0.9, 3.1, -0.6);
  g.add(chimney);
  const door = box(0.8, 1.4, 0.05, mat(C.acier, { rough: 0.6 }), { r: 0.01 });
  door.position.set(0.7, 0.7, 1.52);
  g.add(door);
  const w1 = windowGrid(1, 1, 0.8, 0.75, 0, 0, winMat);
  w1.position.set(-0.8, 1.3, 1.52);
  g.add(w1);
  const w2 = windowGrid(2, 1, 0.7, 0.75, 0.35, 0, winMat);
  w2.rotation.y = Math.PI / 2;
  w2.position.set(1.82, 1.3, 0);
  g.add(w2);
  return g;
}

// ============================================================================
// The hub phone (giant, lying flat). Screen texture supplied by caller.
// ============================================================================
export function hubPhone(screenTexture) {
  const g = new THREE.Group();
  const W = 5.6, L = 11.4, T = 0.5;
  const shape = (() => {
    const s = new THREE.Shape();
    const r = 0.8, x = -W / 2, y = -L / 2;
    s.moveTo(x + r, y);
    s.lineTo(x + W - r, y);
    s.quadraticCurveTo(x + W, y, x + W, y + r);
    s.lineTo(x + W, y + L - r);
    s.quadraticCurveTo(x + W, y + L, x + W - r, y + L);
    s.lineTo(x + r, y + L);
    s.quadraticCurveTo(x, y + L, x, y + L - r);
    s.lineTo(x, y + r);
    s.quadraticCurveTo(x, y, x + r, y);
    return s;
  })();
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: T - 0.12, bevelEnabled: true, bevelThickness: 0.06, bevelSize: 0.06, bevelSegments: 3, curveSegments: 16,
  });
  geo.rotateX(-Math.PI / 2);
  geo.translate(0, 0.06, 0);
  const body = new THREE.Mesh(geo, [
    mat(C.encre, { rough: 0.4, metal: 0.3 }),
    mat(C.acier, { rough: 0.35, metal: 0.6 }),
  ]);
  body.castShadow = true;
  body.receiveShadow = true;
  g.add(body);
  const screenMat = new THREE.MeshBasicMaterial({ map: screenTexture, toneMapped: false });
  const screen = roundedPlane(5.2, 11.0, 0.62, screenMat);
  screen.position.y = T + 0.012;
  // ShapeGeometry is built in XY then rotated: the canvas top must land at -z (screen top).
  screen.rotation.y = 0;
  g.add(screen);
  for (const z of [-2.4, -1.4]) {
    const btn = box(0.12, 0.22, 0.6, mat(C.acier, { rough: 0.35, metal: 0.6 }), { r: 0.04 });
    btn.position.set(W / 2 + 0.03, T / 2, z);
    g.add(btn);
  }
  g.userData = { screen, W, L, T };
  return g;
}

export function plinth(radius = 6.8, h = 1.0) {
  const g = new THREE.Group();
  const side = cyl(radius, radius, h, mat(C.encre2, { rough: 0.95 }), 64);
  side.position.y = -h / 2 - 0.06;
  side.receiveShadow = true;
  const top = cyl(radius - 0.14, radius - 0.14, 0.1, mat(C.filetSombre, { rough: 0.9 }), 64, { cast: false });
  top.position.y = -0.05;
  g.add(side, top);
  // fine concentric rings on top (drawn as thin tori in steel) — the "lens"
  for (const r of [radius - 0.6, radius - 1.1]) {
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(r, 0.025, 6, 96),
      mat(C.acier, { rough: 0.6, metal: 0.3 }),
    );
    ring.rotation.x = Math.PI / 2;
    ring.position.y = 0.01;
    g.add(ring);
  }
  return g;
}

// ============================================================================
// Photo card (billboarded plane with a canvas texture)
// ============================================================================
export function photoCard(texture, w = 2.6, h = 2.1) {
  const g = new THREE.Group();
  const m = new THREE.MeshBasicMaterial({ map: texture, transparent: true, toneMapped: false, depthWrite: true });
  const plane = new THREE.Mesh(new THREE.PlaneGeometry(w, h), m);
  plane.renderOrder = 5;
  plane.castShadow = true;
  g.add(plane);
  g.userData = { plane, w, h };
  return g;
}

// ============================================================================
// Light path: a tube along a curve, revealed by uProgress (0..1)
// ============================================================================
export function lightPath(points, { radius = 0.06, color = C.orange, segments = 120 } = {}) {
  const curve = new THREE.CatmullRomCurve3(points, false, "catmullrom", 0.5);
  const geo = new THREE.TubeGeometry(curve, segments, radius, 8, false);
  const material = new THREE.ShaderMaterial({
    uniforms: {
      uProgress: { value: 0 },
      uTail: { value: 0 },
      uColor: { value: new THREE.Color(color) },
      uOpacity: { value: 1 },
      uGlow: { value: 1 },
    },
    vertexShader: `
      varying vec2 vUv;
      void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }
    `,
    fragmentShader: `
      uniform float uProgress; uniform float uTail; uniform vec3 uColor; uniform float uOpacity; uniform float uGlow;
      varying vec2 vUv;
      void main(){
        if (vUv.x > uProgress || vUv.x < uTail) discard;
        float head = smoothstep(uProgress - 0.12, uProgress, vUv.x);
        float tail = smoothstep(uTail, uTail + 0.1, vUv.x);
        vec3 c = mix(uColor, vec3(1.0, 0.86, 0.66), head * 0.7 * uGlow);
        gl_FragColor = vec4(c * (0.85 + 0.6 * uGlow), uOpacity * max(tail, step(uTail, 0.0001)));
        #include <colorspace_fragment>
      }
    `,
    transparent: true,
    depthWrite: false,
    toneMapped: false,
  });
  const mesh = new THREE.Mesh(geo, material);
  mesh.renderOrder = 3;
  // soft additive halo sharing the same uniforms (one writer drives both)
  const haloGeo = new THREE.TubeGeometry(curve, segments, radius * 3.4, 8, false);
  const haloMat = material.clone();
  haloMat.uniforms = { ...material.uniforms, uMul: { value: 0.22 } };
  haloMat.fragmentShader = material.fragmentShader
    .replace("uniform float uGlow;", "uniform float uGlow; uniform float uMul;")
    .replace("uOpacity * max(tail", "uMul * uOpacity * max(tail");
  haloMat.blending = THREE.AdditiveBlending;
  const halo = new THREE.Mesh(haloGeo, haloMat);
  halo.renderOrder = 2;
  mesh.add(halo);
  mesh.userData = { curve, material };
  return mesh;
}

// flat ring decal (pulse when a path arrives)
export function pulseRing(color = C.orange) {
  const m = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0, depthWrite: false, toneMapped: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending });
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.9, 1.0, 96), m);
  ring.rotation.x = -Math.PI / 2;
  ring.renderOrder = 2;
  return ring;
}

// Manoo iso world — 2D canvas artwork: photo grading, cards, the phone UI, bubble icons.
import { makeCanvas, clamp, lerp, ease } from "./kit.js";

export const INK = "#101619";
export const PAPER = "#F3F2EF";
export const PAPER2 = "#E8E6E1";
export const STEEL = "#78868F";
export const STEEL_L = "#A8B4BB";
export const LINE = "#D6D4CE";
export const ORANGE = "#F97316";
export const ORANGE_D = "#D95F08";
const DISPLAY = "Archivo";
const MONO = "IBM Plex Mono";

export function rr(g, x, y, w, h, r) {
  const k = Math.min(r, w / 2, h / 2);
  g.beginPath();
  g.moveTo(x + k, y);
  g.lineTo(x + w - k, y);
  g.quadraticCurveTo(x + w, y, x + w, y + k);
  g.lineTo(x + w, y + h - k);
  g.quadraticCurveTo(x + w, y + h, x + w - k, y + h);
  g.lineTo(x + k, y + h);
  g.quadraticCurveTo(x, y + h, x, y + h - k);
  g.lineTo(x, y + k);
  g.quadraticCurveTo(x, y, x + k, y);
  g.closePath();
}
function drawCover(g, img, x, y, w, h, r = 0) {
  const s = Math.max(w / img.width, h / img.height);
  const iw = img.width * s;
  const ih = img.height * s;
  g.save();
  if (r > 0) {
    rr(g, x, y, w, h, r);
    g.clip();
  }
  g.drawImage(img, x + (w - iw) / 2, y + (h - ih) / 2, iw, ih);
  g.restore();
}
function font(weight, size, fam = DISPLAY) {
  return `${weight} ${size}px "${fam}"`;
}
function tracked(g, text, x, y, tracking) {
  // manual letter-spacing for canvas (letterSpacing support varies)
  let cx = x;
  for (const ch of text) {
    g.fillText(ch, cx, y);
    cx += g.measureText(ch).width + tracking;
  }
  return cx - x - tracking;
}
function trackedWidth(g, text, tracking) {
  let w = 0;
  for (const ch of text) w += g.measureText(ch).width + tracking;
  return w - tracking;
}

// ---------- photo grading: flash photo look (warm, slight vignette, lifted blacks) ----------
export function gradePhoto(src) {
  const c = makeCanvas(src.width, src.height);
  const g = c.getContext("2d");
  g.drawImage(src, 0, 0);
  const id = g.getImageData(0, 0, c.width, c.height);
  const d = id.data;
  const cx = c.width / 2;
  const cy = c.height / 2;
  const maxR = Math.hypot(cx, cy);
  for (let y = 0; y < c.height; y++)
    for (let x = 0; x < c.width; x++) {
      const i = (y * c.width + x) * 4;
      const v = 1 - 0.32 * Math.pow(Math.hypot(x - cx, y - cy) / maxR, 2.2);
      d[i] = clamp((d[i] * 1.04 + 6) * v, 0, 255);
      d[i + 1] = clamp((d[i + 1] * 1.0 + 4) * v, 0, 255);
      d[i + 2] = clamp((d[i + 2] * 0.94 + 4) * v, 0, 255);
    }
  g.putImageData(id, 0, 0);
  return c;
}

// ---------- polaroid capture card ----------
export function captureCard(photo, label, title) {
  const W = 1000, H = 860, P = 34;
  const c = makeCanvas(W, H);
  const g = c.getContext("2d");
  g.save();
  g.shadowColor = "rgba(0,0,0,0.35)";
  g.shadowBlur = 30;
  g.shadowOffsetY = 10;
  g.fillStyle = "#FFFFFF";
  rr(g, P, P, W - 2 * P, H - 2 * P, 34);
  g.fill();
  g.restore();
  drawCover(g, photo, P + 26, P + 26, W - 2 * P - 52, 560, 20);
  // caption
  g.font = font(500, 30, MONO);
  const lw = trackedWidth(g, label, 4.2) + 44;
  g.fillStyle = "rgba(249,115,22,0.12)";
  rr(g, P + 26, P + 610, lw, 54, 27);
  g.fill();
  g.fillStyle = ORANGE_D;
  g.textBaseline = "middle";
  tracked(g, label, P + 48, P + 638, 4.2);
  g.fillStyle = INK;
  g.font = font(800, 50);
  g.textBaseline = "alphabetic";
  g.fillText(title, P + 26, P + 740);
  return c;
}

// ---------- audience profile card (Manoo profile seen by a company / school / client) ----------
export function profileCard(photo, p) {
  const W = 1000, H = 1160, P = 34;
  const c = makeCanvas(W, H);
  const g = c.getContext("2d");
  g.save();
  g.shadowColor = "rgba(0,0,0,0.4)";
  g.shadowBlur = 34;
  g.shadowOffsetY = 12;
  g.fillStyle = "#FFFFFF";
  rr(g, P, P, W - 2 * P, H - 2 * P, 40);
  g.fill();
  g.restore();
  // orange edge (lit)
  g.strokeStyle = ORANGE;
  g.lineWidth = 6;
  rr(g, P + 3, P + 3, W - 2 * P - 6, H - 2 * P - 6, 38);
  g.stroke();
  // header
  g.fillStyle = PAPER2;
  g.beginPath();
  g.arc(P + 100, P + 110, 62, 0, Math.PI * 2);
  g.fill();
  g.fillStyle = INK;
  g.font = font(800, 46);
  g.textAlign = "center";
  g.textBaseline = "middle";
  g.fillText(p.initials, P + 100, P + 112);
  g.textAlign = "left";
  g.textBaseline = "alphabetic";
  g.font = font(800, 54);
  g.fillText(p.name, P + 190, P + 108);
  g.font = font(500, 27, MONO);
  g.fillStyle = STEEL;
  tracked(g, p.trade, P + 192, P + 152, 3);
  // photo
  drawCover(g, photo, P + 34, P + 210, W - 2 * P - 68, 600, 26);
  // title + chip
  g.fillStyle = INK;
  g.font = font(700, 46);
  g.fillText(p.title, P + 40, P + 890);
  g.font = font(500, 26, MONO);
  const lw = trackedWidth(g, p.label, 3.5) + 40;
  g.fillStyle = "rgba(249,115,22,0.12)";
  rr(g, P + 40, P + 920, lw, 50, 25);
  g.fill();
  g.fillStyle = ORANGE_D;
  g.textBaseline = "middle";
  tracked(g, p.label, P + 60, P + 946, 3.5);
  // button
  g.textBaseline = "middle";
  g.strokeStyle = INK;
  g.lineWidth = 4;
  rr(g, P + 40, P + 1000, W - 2 * P - 80, 86, 43);
  g.stroke();
  g.fillStyle = INK;
  g.font = font(700, 36);
  g.textAlign = "center";
  g.fillText("Voir le portfolio", W / 2, P + 1044);
  g.textAlign = "left";
  return c;
}

// ---------- bubble icons (ink pictograms) ----------
export function iconCanvas(name, color = INK) {
  const S = 256;
  const c = makeCanvas(S, S);
  const g = c.getContext("2d");
  g.strokeStyle = color;
  g.fillStyle = color;
  g.lineWidth = 15;
  g.lineCap = "round";
  g.lineJoin = "round";
  g.translate(S / 2, S / 2);
  const P = () => g.beginPath();
  if (name === "camera") {
    rr(g, -78, -46, 156, 108, 22); g.stroke();
    P(); g.moveTo(-34, -46); g.lineTo(-20, -68); g.lineTo(20, -68); g.lineTo(34, -46); g.stroke();
    P(); g.arc(0, 8, 32, 0, Math.PI * 2); g.stroke();
    P(); g.arc(52, -22, 7, 0, Math.PI * 2); g.fill();
  } else if (name === "image") {
    rr(g, -80, -62, 160, 124, 20); g.stroke();
    P(); g.moveTo(-62, 44); g.lineTo(-18, -4); g.lineTo(12, 26); g.lineTo(34, 6); g.lineTo(62, 40); g.stroke();
    P(); g.arc(30, -28, 13, 0, Math.PI * 2); g.fill();
  } else if (name === "hammer") {
    g.rotate(-0.6);
    rr(g, -12, -20, 24, 112, 10); g.fill();
    rr(g, -62, -64, 112, 46, 14); g.fill();
    P(); g.moveTo(50, -60); g.lineTo(76, -74); g.lineTo(76, -10); g.lineTo(50, -24); g.closePath(); g.fill();
  } else if (name === "bricks") {
    const bw = 64, bh = 30, gap = 8;
    for (let row = 0; row < 4; row++) {
      const off = row % 2 ? bw / 2 + gap / 2 : 0;
      for (let x = -112 - off; x < 112; x += bw + gap) {
        const a = Math.max(-96, x), b = Math.min(96, x + bw);
        if (b - a < 14) continue;
        rr(g, a, -76 + row * (bh + gap), b - a, bh, 6);
        g.fill();
      }
    }
  } else if (name === "saw") {
    g.rotate(-0.35);
    P(); g.moveTo(-90, -10); g.lineTo(40, -34); g.lineTo(40, 22); g.lineTo(-90, 22); g.closePath(); g.stroke();
    for (let x = -82; x < 36; x += 16) { P(); g.moveTo(x, 22); g.lineTo(x + 8, 36); g.lineTo(x + 16, 22); g.stroke(); }
    rr(g, 40, -44, 52, 74, 18); g.stroke();
  } else if (name === "helmet") {
    P(); g.arc(0, 20, 70, Math.PI, 0); g.stroke();
    P(); g.moveTo(-96, 22); g.lineTo(96, 22); g.stroke();
    P(); g.moveTo(0, -50); g.lineTo(0, 0); g.stroke();
  } else if (name === "eye") {
    P(); g.moveTo(-90, 0); g.quadraticCurveTo(0, -78, 90, 0); g.quadraticCurveTo(0, 78, -90, 0); g.closePath(); g.stroke();
    P(); g.arc(0, 0, 26, 0, Math.PI * 2); g.fill();
  } else if (name === "briefcase") {
    rr(g, -84, -36, 168, 112, 18); g.stroke();
    rr(g, -32, -66, 64, 30, 10); g.stroke();
    P(); g.moveTo(-84, 6); g.lineTo(84, 6); g.stroke();
  } else if (name === "cap") {
    P(); g.moveTo(0, -60); g.lineTo(96, -20); g.lineTo(0, 20); g.lineTo(-96, -20); g.closePath(); g.fill();
    P(); g.moveTo(-54, 2); g.lineTo(-54, 46); g.quadraticCurveTo(0, 76, 54, 46); g.lineTo(54, 2); g.stroke();
    P(); g.moveTo(84, -16); g.lineTo(84, 40); g.stroke();
  } else if (name === "house") {
    P(); g.moveTo(-84, -6); g.lineTo(0, -78); g.lineTo(84, -6); g.stroke();
    P(); g.moveTo(-60, -22); g.lineTo(-60, 72); g.lineTo(60, 72); g.lineTo(60, -22); g.stroke();
    rr(g, -18, 20, 36, 52, 6); g.fill();
  } else if (name === "plus") {
    P(); g.moveTo(0, -60); g.lineTo(0, 60); g.moveTo(-60, 0); g.lineTo(60, 0); g.lineWidth = 22; g.stroke();
  } else if (name === "spark") {
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2;
      const r0 = i % 2 ? 26 : 18;
      const r1 = i % 2 ? 70 : 88;
      P(); g.moveTo(Math.cos(a) * r0, Math.sin(a) * r0); g.lineTo(Math.cos(a) * r1, Math.sin(a) * r1); g.stroke();
    }
  }
  return c;
}

// ============================================================================
// Phone UI — "Mes réalisations" gallery + "Ajouter au portfolio" sheet
// ============================================================================
export class PhoneUI {
  constructor(profiles, W = 1080, H = 2220) {
    this.W = W;
    this.H = H;
    this.canvas = makeCanvas(W, H);
    this.g = this.canvas.getContext("2d");
    this.profiles = profiles; // [{initials,name,trade, items:[{photo,title,date}], newIndex:0}]
    this.lastKey = "";
  }
  // returns true if the canvas changed
  draw(s) {
    const key = JSON.stringify(s, (k, v) => (typeof v === "number" ? Math.round(v * 400) / 400 : v));
    if (key === this.lastKey) return false;
    this.lastKey = key;
    const { g, W, H } = this;
    g.save();
    g.clearRect(0, 0, W, H);
    g.fillStyle = PAPER;
    g.fillRect(0, 0, W, H);
    if (s.mode === "splash") {
      this.splash(s);
    } else {
      // gallery pages with horizontal swipe (s.page fractional)
      const page = s.page || 0;
      for (let i = 0; i < this.profiles.length; i++) {
        const dx = (i - page) * W;
        if (dx <= -W || dx >= W) continue;
        g.save();
        g.translate(dx, 0);
        this.gallery(this.profiles[i], s, i);
        g.restore();
      }
      if (s.sheet > 0) this.sheet(s);
    }
    this.statusBar(s.mode === "splash");
    g.restore();
    return true;
  }
  statusBar(dark) {
    const { g, W } = this;
    g.fillStyle = INK;
    rr(g, W / 2 - 150, 28, 300, 84, 42);
    g.fill();
    g.fillStyle = dark ? PAPER : INK;
    g.font = font(600, 36, MONO);
    g.textBaseline = "middle";
    g.fillText("9:41", 84, 72);
    // battery
    g.strokeStyle = dark ? PAPER : INK;
    g.lineWidth = 3;
    rr(g, W - 150, 58, 62, 30, 8);
    g.stroke();
    g.fillRect(W - 145, 63, 44, 20);
    g.fillRect(W - 84, 66, 5, 14);
    for (let i = 0; i < 3; i++) {
      g.beginPath();
      g.arc(W - 232 + i * 22, 73, 6, 0, Math.PI * 2);
      g.fill();
    }
    g.fillStyle = dark ? "rgba(243,242,239,0.6)" : "rgba(16,22,25,0.85)";
    rr(g, W / 2 - 150, this.H - 34, 300, 10, 5);
    g.fill();
  }
  gallery(p, s, idx) {
    const { g, W } = this;
    // header
    g.fillStyle = PAPER2;
    g.beginPath();
    g.arc(140, 250, 70, 0, Math.PI * 2);
    g.fill();
    g.fillStyle = INK;
    g.font = font(800, 52);
    g.textAlign = "center";
    g.textBaseline = "middle";
    g.fillText(p.initials, 140, 253);
    g.textAlign = "left";
    g.textBaseline = "alphabetic";
    g.font = font(800, 70);
    g.fillText(p.name, 240, 250);
    g.font = font(500, 30, MONO);
    g.fillStyle = STEEL;
    tracked(g, p.trade, 242, 298, 3.2);
    g.fillStyle = INK;
    g.font = font(800, 58);
    g.fillText("Mes réalisations", 70, 440);
    // chips
    const chips = ["Tout", "Chantiers", "Chef-d'œuvre"];
    let x = 70;
    g.font = font(600, 32);
    chips.forEach((t, i) => {
      const w = g.measureText(t).width + 64;
      g.fillStyle = i === 0 ? ORANGE : PAPER2;
      rr(g, x, 480, w, 72, 36);
      g.fill();
      g.fillStyle = i === 0 ? "#FFFFFF" : INK;
      g.textBaseline = "middle";
      g.fillText(t, x + 32, 517);
      g.textBaseline = "alphabetic";
      x += w + 18;
    });
    // grid — the new item lands at slot 0; older ones shift by one slot as it lands
    const land = s.land ? s.land[idx] || 0 : 0; // 0..1
    const items = p.items;
    const cw = 455, ph = 340, gx = 40, top = 600, rowH = 470;
    const slotPos = (k) => [70 + (k % 2) * (cw + gx), top + Math.floor(k / 2) * rowH];
    // older items: indices 1..n, move from slot (k-1) to slot k as land goes 0→1
    for (let k = 1; k < items.length; k++) {
      const a = slotPos(k - 1);
      const b = slotPos(k);
      const e = ease("power3.inOut", clamp(land * 1.15));
      this.itemCard(items[k], lerp(a[0], b[0], e), lerp(a[1], b[1], e), cw, ph, 0);
    }
    if (land > 0) {
      const e = ease("back.out(1.6)", clamp((land - 0.25) / 0.75));
      const [sx, sy] = slotPos(0);
      g.save();
      g.globalAlpha = clamp((land - 0.2) * 4);
      const sc = lerp(1.25, 1, e);
      g.translate(sx + cw / 2, sy + ph / 2);
      g.scale(sc, sc);
      g.translate(-(sx + cw / 2), -(sy + ph / 2));
      const glow = s.glow ? s.glow[idx] || 0 : 0;
      this.itemCard(items[0], sx, sy, cw, ph, glow);
      g.restore();
    }
    // FAB
    const fabPress = s.fab || 0;
    g.save();
    g.translate(950, 2060);
    const fs = 1 - 0.12 * Math.sin(Math.PI * clamp(fabPress));
    g.scale(fs, fs);
    g.shadowColor = "rgba(249,115,22,0.45)";
    g.shadowBlur = 30;
    g.fillStyle = ORANGE;
    g.beginPath();
    g.arc(0, 0, 84, 0, Math.PI * 2);
    g.fill();
    g.shadowBlur = 0;
    g.strokeStyle = "#FFFFFF";
    g.lineWidth = 12;
    g.lineCap = "round";
    g.beginPath();
    g.moveTo(-30, 0); g.lineTo(30, 0); g.moveTo(0, -30); g.lineTo(0, 30);
    g.stroke();
    g.restore();
  }
  itemCard(it, x, y, w, ph, glow) {
    const { g } = this;
    if (glow > 0) {
      g.save();
      g.shadowColor = `rgba(249,115,22,${0.9 * glow})`;
      g.shadowBlur = 50 * glow;
      g.strokeStyle = `rgba(249,115,22,${glow})`;
      g.lineWidth = 8;
      rr(g, x - 6, y - 6, w + 12, ph + 130, 34);
      g.stroke();
      g.restore();
    }
    g.fillStyle = "#FFFFFF";
    rr(g, x, y, w, ph + 118, 28);
    g.fill();
    drawCover(g, it.photo, x, y, w, ph, 28);
    g.fillStyle = "#FFFFFF";
    g.fillRect(x, y + ph - 28, w, 28);
    g.fillStyle = INK;
    g.font = font(700, 33);
    g.fillText(it.title, x + 22, y + ph + 52, w - 40);
    g.fillStyle = STEEL;
    g.font = font(500, 24, MONO);
    tracked(g, it.date, x + 22, y + ph + 94, 2.6);
  }
  sheet(s) {
    const { g, W, H } = this;
    const p = this.profiles[0];
    const k = ease("power3.out", clamp(s.sheet));
    g.fillStyle = `rgba(16,22,25,${0.38 * k})`;
    g.fillRect(0, 0, W, H);
    const y0 = lerp(H, 470, k);
    g.save();
    g.translate(0, y0 - 470);
    g.fillStyle = "#FFFFFF";
    rr(g, 0, 470, W, H - 470 + 80, 64);
    g.fill();
    g.fillStyle = LINE;
    rr(g, W / 2 - 70, 498, 140, 12, 6);
    g.fill();
    g.fillStyle = INK;
    g.font = font(800, 64);
    g.fillText("Ajouter au portfolio", 70, 620);
    // photo slot
    const sx = 70, sy = 670, sw = W - 140, sh = 640;
    const fill = s.photo || 0;
    if (fill < 1) {
      g.save();
      g.setLineDash([22, 16]);
      g.strokeStyle = STEEL_L;
      g.lineWidth = 5;
      rr(g, sx, sy, sw, sh, 40);
      g.stroke();
      g.restore();
      g.fillStyle = STEEL;
      g.font = font(600, 38);
      g.textAlign = "center";
      g.fillText("Une photo", W / 2, sy + sh / 2 + 70);
      g.textAlign = "left";
      g.drawImage(this.icon || (this.icon = iconCanvas("camera", STEEL)), W / 2 - 64, sy + sh / 2 - 110, 128, 128);
    }
    if (fill > 0) {
      const e = ease("back.out(1.4)", clamp(fill));
      g.save();
      g.globalAlpha = clamp(fill * 3);
      const sc = lerp(0.6, 1, e);
      g.translate(sx + sw / 2, sy + sh / 2 - (1 - e) * 260);
      g.scale(sc, sc);
      g.rotate((1 - e) * -0.12);
      g.translate(-(sx + sw / 2), -(sy + sh / 2));
      drawCover(g, p.items[0].photo, sx, sy, sw, sh, 40);
      g.restore();
    }
    // title field
    g.fillStyle = STEEL;
    g.font = font(500, 28, MONO);
    tracked(g, "TITRE", 74, 1395, 4.5);
    g.fillStyle = "#FBFAF8";
    rr(g, 70, 1420, W - 140, 130, 30);
    g.fill();
    g.strokeStyle = s.typing > 0 && s.typing < 1.2 ? ORANGE : LINE;
    g.lineWidth = 4;
    rr(g, 70, 1420, W - 140, 130, 30);
    g.stroke();
    const full = p.items[0].title;
    const n = Math.floor(clamp(s.typing || 0) * full.length + 1e-6);
    const txt = full.slice(0, n);
    g.font = font(700, 50);
    g.textBaseline = "middle";
    if (s.textGlow > 0) {
      g.save();
      g.shadowColor = `rgba(249,115,22,${s.textGlow})`;
      g.shadowBlur = 36 * s.textGlow;
      g.fillStyle = `rgba(249,115,22,${0.55 * s.textGlow})`;
      g.fillText(txt, 110, 1487);
      g.restore();
    }
    g.fillStyle = INK;
    g.fillText(txt, 110, 1487);
    if (s.caret) {
      const tw = g.measureText(txt).width;
      g.fillStyle = ORANGE;
      g.fillRect(114 + tw, 1452, 5, 70);
    }
    g.textBaseline = "alphabetic";
    // chips (category)
    const chips = [["MÉTALLERIE", true], ["CHEF-D'ŒUVRE", false]];
    let cx = 70;
    chips.forEach(([t, on], i) => {
      const a = clamp((s.chips || 0) * 2 - i);
      if (a <= 0) return;
      g.font = font(500, 28, MONO);
      const w = trackedWidth(g, t, 3.6) + 56;
      g.save();
      const e = ease("back.out(2)", a);
      g.globalAlpha = a;
      g.translate(cx + w / 2, 1640);
      g.scale(e, e);
      g.translate(-(cx + w / 2), -1640);
      g.fillStyle = on ? "rgba(249,115,22,0.13)" : PAPER2;
      rr(g, cx, 1604, w, 72, 36);
      g.fill();
      if (on) {
        g.strokeStyle = ORANGE;
        g.lineWidth = 3;
        rr(g, cx, 1604, w, 72, 36);
        g.stroke();
      }
      g.fillStyle = on ? ORANGE_D : INK;
      g.textBaseline = "middle";
      tracked(g, t, cx + 28, 1641, 3.6);
      g.textBaseline = "alphabetic";
      g.restore();
      cx += w + 18;
    });
    // button + press + halo
    const press = s.press || 0;
    const bs = 1 - 0.05 * Math.sin(Math.PI * clamp(press));
    g.save();
    g.translate(W / 2, 1830);
    g.scale(bs, bs);
    g.translate(-W / 2, -1830);
    g.shadowColor = "rgba(249,115,22,0.5)";
    g.shadowBlur = 40;
    g.fillStyle = press > 0 && press < 1 ? ORANGE_D : ORANGE;
    rr(g, 70, 1760, W - 140, 140, 70);
    g.fill();
    g.shadowBlur = 0;
    g.fillStyle = "#FFFFFF";
    g.font = font(700, 48);
    g.textAlign = "center";
    g.textBaseline = "middle";
    g.fillText("Ajouter au portfolio", W / 2, 1832);
    g.textAlign = "left";
    g.textBaseline = "alphabetic";
    g.restore();
    if (s.halo > 0 && s.halo < 1) {
      const r = lerp(30, 230, ease("power2.out", s.halo));
      g.strokeStyle = `rgba(16,22,25,${0.35 * (1 - s.halo)})`;
      g.lineWidth = 10;
      g.beginPath();
      g.arc(W / 2 + 120, 1835, r, 0, Math.PI * 2);
      g.stroke();
      g.fillStyle = `rgba(16,22,25,${0.18 * (1 - s.halo)})`;
      g.beginPath();
      g.arc(W / 2 + 120, 1835, 46, 0, Math.PI * 2);
      g.fill();
    }
    g.restore();
  }
  splash(s) {
    const { g, W, H } = this;
    g.fillStyle = INK;
    g.fillRect(0, 0, W, H);
    const a = s.splash || 0;
    if (a <= 0) return;
    g.globalAlpha = a;
    g.fillStyle = PAPER;
    g.font = font(800, 150);
    g.textAlign = "left";
    g.textBaseline = "middle";
    const w = trackedWidth(g, "MANOO", -5);
    tracked(g, "MANOO", W / 2 - w / 2 - 22, H / 2, -5);
    g.fillStyle = ORANGE;
    g.beginPath();
    g.arc(W / 2 + w / 2 + 6, H / 2 + 48, 20, 0, Math.PI * 2);
    g.fill();
    g.textAlign = "left";
    g.globalAlpha = 1;
  }
}

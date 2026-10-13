#!/usr/bin/env python3
"""Procedural matter for the Manoo ad.

Bakes deterministic textures (paper, weld bead on steel, tiles, bread crust, light beam)
and particle overlays (sparks, dust, flour) at 1080x1920. Every generator takes a seed,
so the same command always produces the same pixels.

    python3 tools/matter.py            # bake everything into assets/matter/
    python3 tools/matter.py sparks     # bake only the named items
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "matter")


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


ENCRE, PAPIER, ORANGE, ACIER = rgb("#101619"), rgb("#F3F2EF"), rgb("#F97316"), rgb("#78868F")


# ---------------------------------------------------------------- noise & light

def noise(h, w, cy, cx, seed):
    """Bicubic value noise, cell size (cy, cx) in px, roughly in [0, 1]."""
    rng = np.random.default_rng(seed)
    gh, gw = int(math.ceil(h / cy)) + 4, int(math.ceil(w / cx)) + 4
    g = rng.random((gh, gw)).astype(np.float32)
    big = Image.fromarray(g, mode="F").resize((max(1, int(gw * cx)), max(1, int(gh * cy))), Image.BICUBIC)
    oy, ox = int(cy * 1.5), int(cx * 1.5)
    return np.asarray(big, np.float32)[oy:oy + h, ox:ox + w]


def fbm(h, w, cell, octaves, seed, gain=0.5, aniso=(1.0, 1.0)):
    tot, amp, norm, c = np.zeros((h, w), np.float32), 1.0, 0.0, float(cell)
    for i in range(octaves):
        cy, cx = max(1.0, c * aniso[0]), max(1.0, c * aniso[1])
        tot += amp * noise(h, w, cy, cx, seed + 101 * i)
        norm += amp
        amp *= gain
        c /= 2.0
    return tot / norm


def _box(a, r, axis):
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis, dtype=np.float64)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def blur(a, sigma):
    """Gaussian blur approximated by three box passes per axis (sigma in px)."""
    if sigma <= 0:
        return a
    r = max(1, int(round((math.sqrt(12 * sigma * sigma / 3 + 1) - 1) / 2)))
    out = a.astype(np.float32)
    for axis in (0, 1):
        for _ in range(3):
            out = _box(out, r, axis)
    return out


def normals(hgt, strength=1.0):
    gy, gx = np.gradient(hgt)
    n = np.stack([-gx * strength, -gy * strength, np.ones_like(hgt)], -1)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def unit(v):
    v = np.asarray(v, np.float32)
    return v / np.linalg.norm(v)


def lambert(n, L):
    return np.clip((n * unit(L)).sum(-1), 0, 1)


def blinn(n, L, shin):
    hv = unit(unit(L) + np.array([0, 0, 1.0], np.float32))
    return np.clip((n * hv).sum(-1), 0, 1) ** shin


def ramp(t, stops):
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    ps = [p for p, _ in stops]
    cs = [rgb(c) for _, c in stops]
    for ch in range(3):
        out[..., ch] = np.interp(t, ps, [c[ch] for c in cs])
    return out


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def grid():
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    return xs, ys


def save_rgb(a, name, jpg=True):
    os.makedirs(OUT, exist_ok=True)
    img = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    path = os.path.join(OUT, name + (".jpg" if jpg else ".png"))
    img.save(path, quality=92) if jpg else img.save(path, optimize=True)
    print("baked", os.path.relpath(path, ROOT))


def save_rgba(rgb_add, name):
    """Additive light layer -> RGBA PNG usable with mix-blend-mode: screen (alpha = luminance)."""
    a = np.clip(rgb_add, 0, 1)
    alpha = np.clip(a.max(-1), 0, 1)
    col = np.where(alpha[..., None] > 1e-4, a / np.maximum(alpha[..., None], 1e-4), 0)
    out = np.concatenate([col, alpha[..., None]], -1)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".png")
    Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA").save(path, optimize=True)
    print("baked", os.path.relpath(path, ROOT))


# ---------------------------------------------------------------- textures

def paper(seed=11):
    f1 = fbm(H, W, 46, 5, seed, aniso=(0.22, 1.0))
    f2 = fbm(H, W, 46, 5, seed + 7, aniso=(1.0, 0.22))
    fine = noise(H, W, 1.4, 1.4, seed + 3)
    wav = fbm(H, W, 700, 3, seed + 5)
    hgt = wav * 9.0 + (f1 + f2) * 0.55 + fine * 0.12
    d = lambert(normals(hgt), (-0.92, -0.3, 0.5))
    xs = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    tone = (0.87 + 0.17 * d) * (1.0 - 0.08 * xs - 0.04 * yy)
    return PAPIER[None, None, :] * tone[..., None]


def weld(seed=21, A=(-160.0, 1800.0), B=(600.0, 1060.0), hw=66.0):
    """Macro of a TIG bead on brushed steel; the pool at B is white-hot, the bead cools behind it."""
    xs, ys = grid()
    A, B = np.array(A, np.float32), np.array(B, np.float32)
    L = float(np.linalg.norm(B - A))
    u = (B - A) / L
    v = np.array([-u[1], u[0]], np.float32)
    px, py = xs - A[0], ys - A[1]
    s = px * u[0] + py * u[1]
    d = px * v[0] + py * v[1]
    sc = np.clip(s, 0, L)
    dist = np.hypot(px - sc * u[0], py - sc * u[1])

    brushed = fbm(H, W, 260, 6, seed, aniso=(0.04, 1.0))
    plate_h = brushed * 1.4 + noise(H, W, 2, 2, seed + 5) * 0.25
    prof = np.sqrt(np.clip(1 - (dist / hw) ** 2, 0, 1))
    phase = (s + 0.9 * hw * (d / hw) ** 2) / 15.0
    rip = 0.5 + 0.5 * np.cos(2 * np.pi * phase)
    molten = smooth(L - 150, L - 20, s)
    bead_h = prof * (22.0 + 2.6 * rip * (1 - molten))
    hgt = plate_h + bead_h
    n = normals(hgt, 1.0)

    # albedo: dark steel plate, slightly lighter bead with oxide bands
    plate_alb = ramp(brushed, [(0.0, "#222a2f"), (0.5, "#323b41"), (1.0, "#46525a")])
    bead_alb = ramp(rip * 0.35 + noise(H, W, 6, 6, seed + 9) * 0.65, [(0.0, "#3d4244"), (1.0, "#6d7172")])
    m = (prof > 0)[..., None].astype(np.float32)
    alb = plate_alb * (1 - m) + bead_alb * m

    # temperature along the bead, hottest in the pool
    T = np.exp(-np.clip(L - s, 0, None) / 260.0) * smooth(0.0, 0.25, prof)
    T = np.maximum(T, np.clip(1.15 - np.hypot(xs - B[0], ys - B[1]) / (hw * 1.05), 0, 1))
    emis = ramp(T, [(0.0, "#000000"), (0.18, "#2a0902"), (0.42, "#9a2f06"), (0.62, "#F97316"),
                    (0.82, "#FFB866"), (1.0, "#FFF4E2")]) * smooth(0.05, 0.3, T)[..., None]

    # the pool lights the plate (warm point light) + a faint cool ambient from above
    lx, ly = B[0] - xs, B[1] - ys
    r = np.hypot(lx, ly)
    Ld = np.stack([lx, ly, np.full_like(lx, 90.0)], -1)
    Ld /= np.linalg.norm(Ld, axis=-1, keepdims=True)
    diff = np.clip((n * Ld).sum(-1), 0, 1)
    fall = 1.0 / (1.0 + (r / 380.0) ** 2)
    hv = Ld + np.array([0, 0, 1.0], np.float32)
    hv /= np.linalg.norm(hv, axis=-1, keepdims=True)
    spec = np.clip((n * hv).sum(-1), 0, 1) ** 40
    warm = rgb("#FFB070")
    amb = lambert(n, (0.0, -0.6, 0.8)) * 0.12
    col = alb * (amb[..., None] * rgb("#8fa3ae") + (diff * fall * 2.6)[..., None] * warm)
    col += (spec * fall * 1.6)[..., None] * warm
    col += emis
    glow = np.stack([blur(emis[..., c], 18) * 0.9 + blur(emis[..., c], 70) * 0.8 for c in range(3)], -1)
    col += glow
    # vignette toward encre
    vig = smooth(0.35, 1.05, np.hypot((xs - W / 2) / W, (ys - H * 0.6) / H) * 1.6)
    col = col * (1 - 0.7 * vig[..., None]) + ENCRE * 0.7 * vig[..., None]
    return col


def tiles(seed=31, pitch=430, grout=14, origin=(-120, -60)):
    xs, ys = grid()
    gx, gy = xs - origin[0], ys - origin[1]
    ti, tj = np.floor(gx / pitch), np.floor(gy / pitch)
    u, v = gx - ti * pitch, gy - tj * pitch
    inside = (u < pitch - grout) & (v < pitch - grout)
    e = np.minimum(np.minimum(u, pitch - grout - u), np.minimum(v, pitch - grout - v))
    rng = np.random.default_rng(seed)
    tilt = rng.normal(0, 0.006, (64, 64, 2)).astype(np.float32)
    tone = rng.normal(0, 0.035, (64, 64)).astype(np.float32)
    ii, jj = (ti.astype(int) + 8) % 64, (tj.astype(int) + 8) % 64
    lip = tilt[jj, ii, 0] * u + tilt[jj, ii, 1] * v
    micro = fbm(H, W, 24, 4, seed + 3) * 0.9 + noise(H, W, 1.6, 1.6, seed + 4) * 0.35
    sand = noise(H, W, 2.2, 2.2, seed + 6)
    tile_h = 6.0 + lip + smooth(0, 9, e) * 3.0 + micro
    grout_h = 1.0 + sand * 0.8
    hgt = np.where(inside, tile_h, grout_h)
    n = normals(hgt, 1.2)
    speck = noise(H, W, 1.8, 1.8, seed + 8)
    t_alb = ramp(fbm(H, W, 180, 4, seed + 9) * 0.6 + speck * 0.4, [(0.0, "#bdb6aa"), (1.0, "#e4ddd0")])
    t_alb *= (1 + tone[jj, ii])[..., None]
    g_alb = ramp(sand, [(0.0, "#2c2b29"), (1.0, "#46443f")])
    alb = np.where(inside[..., None], t_alb, g_alb)
    Lk = (-0.85, -0.55, 0.26)
    diff = lambert(n, Lk)
    spec = blinn(n, Lk, 60) * 0.35
    col = alb * (0.12 + 2.7 * diff)[..., None] * rgb("#fff1dc") + spec[..., None]
    # raking light falls off toward the bottom-right
    fall = smooth(1.15, 0.1, np.hypot(xs / W, ys / H) * 0.9)
    col = col * (0.12 + 0.88 * fall[..., None]) + ENCRE * (1 - fall[..., None]) * 0.5
    return col


def bread(seed=41, angle=-58.0, radius=150.0, gap=36.0, offset=-160.0):
    """Three scored baguettes, diagonal, warm raking light, flour on the crust."""
    xs, ys = grid()
    th = math.radians(angle)
    ux, uy = math.cos(th), math.sin(th)
    vx, vy = -uy, ux
    cx, cy = W * 0.5, H * 0.5
    s = (xs - cx) * ux + (ys - cy) * uy
    d = (xs - cx) * vx + (ys - cy) * vy + offset
    pitch = 2 * radius + gap
    k = np.floor((d + pitch / 2) / pitch)
    dl = d - k * pitch
    s = s + k * 210.0  # stagger the scores between loaves
    on = np.abs(dl) < radius
    cyl = np.sqrt(np.clip(1 - (dl / radius) ** 2, 0, 1))
    # scores: slashes at ~22deg to the axis, every 300px
    a = math.radians(22.0)
    ss = s * math.cos(a) + dl * math.sin(a)
    sd = -s * math.sin(a) + dl * math.cos(a)
    per = 300.0
    sl = ss - np.round(ss / per) * per
    slash_len, slash_w = 120.0, 34.0
    inslash = (np.abs(sd) < slash_len) & on
    prof_open = np.clip(1 - (sl / slash_w) ** 2, 0, 1) * np.clip(1 - (sd / slash_len) ** 2, 0, 1)
    lip = np.clip(1 - ((sl + slash_w * 1.25) / (slash_w * 0.9)) ** 2, 0, 1) * np.clip(1 - (sd / slash_len) ** 2, 0, 1)
    rng = np.random.default_rng(seed)
    blis = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(blis)
    for _ in range(1400):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 7)
        dr.ellipse([x - r, y - r, x + r, y + r], fill=int(rng.uniform(80, 255)))
    blis = blur(np.asarray(blis, np.float32) / 255.0, 2.2)
    crust = fbm(H, W, 120, 5, seed + 3)
    hgt = on * (cyl * 70 + crust * 5 + blis * 3.5 - prof_open * 26 * inslash + lip * 12 * inslash)
    peel = fbm(H, W, 400, 5, seed + 4, aniso=(1.0, 0.08)) * 3.0
    hgt = np.where(on, hgt, peel)
    n = normals(hgt, 1.0)
    bake = np.clip(0.25 + cyl * 0.45 + crust * 0.35 + blis * 0.12 + lip * 0.35, 0, 1)
    crust_c = ramp(bake, [(0.0, "#d9a45a"), (0.35, "#b9732f"), (0.7, "#7a4219"), (1.0, "#3e1d0b")])
    crumb = ramp(fbm(H, W, 18, 3, seed + 6), [(0.0, "#d6b47c"), (1.0, "#f0dcb4")])
    open_m = smooth(0.05, 0.35, prof_open) * inslash
    alb = crust_c * (1 - open_m[..., None]) + crumb * open_m[..., None]
    flour = smooth(0.6, 0.78, fbm(H, W, 90, 5, seed + 8)) * cyl * 0.8
    flour = np.maximum(flour, (noise(H, W, 1.3, 1.3, seed + 9) > 0.9) * 0.55 * cyl)
    alb = alb * (1 - flour[..., None] * 0.8) + rgb("#f3eee6") * (flour[..., None] * 0.8)
    peel_c = ramp(fbm(H, W, 300, 4, seed + 11, aniso=(1.0, 0.1)), [(0.0, "#1a1410"), (1.0, "#33261c")])
    alb = np.where(on[..., None], alb, peel_c)
    Lk = (0.62, -0.62, 0.42)
    diff = lambert(n, Lk)
    spec = blinn(n, Lk, 22) * 0.1
    warm = rgb("#ffe3c4")
    occl = np.where(on, 0.35 + 0.65 * smooth(-0.15, 0.6, cyl), 0.55)
    col = alb * (0.08 + 1.35 * diff * occl)[..., None] * warm + (spec * occl)[..., None]
    vig = smooth(0.25, 1.0, np.hypot((xs - W * 0.6) / W, (ys - H * 0.42) / H) * 1.45)
    col = col * (1 - 0.8 * vig[..., None]) + ENCRE * 0.8 * vig[..., None]
    return col


def oven(seed=45):
    """The bakery: darkness, the warm mouth of an oven below, flour hanging in its light."""
    xs, ys = grid()
    mouth = np.exp(-(((xs - W * 0.52) / (W * 0.62)) ** 2 + ((ys - H * 1.02) / (H * 0.2)) ** 2))
    glow = mouth ** 0.7
    cloud = fbm(H, W, 380, 6, seed) * np.exp(-(((xs - W * 0.5) / (W * 0.7)) ** 2 + ((ys - H * 0.62) / (H * 0.32)) ** 2))
    cloud = smooth(0.18, 0.62, cloud)
    lit = np.clip(0.12 + 1.2 * np.exp(-((ys - H) / (H * 0.55)) ** 2), 0, 1.2)
    col = ENCRE[None, None, :] * 0.9
    col = col + (glow * 0.9)[..., None] * rgb("#c2450c") + (glow ** 3 * 0.9)[..., None] * rgb("#ffb46a")
    col = col + (cloud * lit * 0.55)[..., None] * rgb("#f3e6d2")
    return col


def beam(seed=51):
    """Darkness with one slanted shaft of light (the room the dust floats in)."""
    xs, ys = grid()
    A, B = np.array([1180.0, -140.0]), np.array([120.0, 2060.0])
    u = (B - A) / np.linalg.norm(B - A)
    px, py = xs - A[0], ys - A[1]
    s = px * u[0] + py * u[1]
    d = px * -u[1] + py * u[0]
    width = 120 + s * 0.22
    I = np.exp(-(d / width) ** 2) * smooth(-100, 500, s) * (1 - 0.45 * s / np.linalg.norm(B - A))
    haze = fbm(H, W, 300, 4, seed) * 0.5 + 0.5
    col = ENCRE[None, None, :] * 0.85 + (I * haze * 0.24)[..., None] * rgb("#fff1dc")
    return col


def crumple(seed=91, size=760, r=285.0, cells=52):
    """The CV sheet crumpled into a ball (RGBA): Voronoi facets tilted off a sphere, sharp creases,
    and the sheet's typed lines surviving on some facets at broken angles."""
    rng = np.random.default_rng(seed)
    ys_, xs_ = np.mgrid[0:size, 0:size].astype(np.float32)
    c = size / 2
    X, Y = (xs_ - c) / r, (ys_ - c) / r
    # seeds spread over the disc (sqrt for uniform area), each with its own silhouette radius
    t = rng.uniform(0, 2 * math.pi, cells)
    q = np.sqrt(rng.uniform(0, 1, cells)) * 0.96
    sx, sy = (q * np.cos(t)).astype(np.float32), (q * np.sin(t)).astype(np.float32)
    best = np.full(X.shape, 1e9, np.float32)
    second = np.full(X.shape, 1e9, np.float32)
    idx = np.zeros(X.shape, np.int32)
    for k in range(cells):
        dk = (X - sx[k]) ** 2 + (Y - sy[k]) ** 2
        closer = dk < best
        second = np.where(closer, best, np.minimum(second, dk))
        idx = np.where(closer, k, idx)
        best = np.where(closer, dk, best)
    rad = rng.uniform(0.9, 1.0, cells).astype(np.float32)
    rr = np.hypot(X, Y)
    inside = rr < rad[idx]
    # facet normals: sphere normal at the seed, tilted at random
    sz = np.sqrt(np.clip(1 - np.minimum(sx ** 2 + sy ** 2, 0.97), 0, 1))
    tilt = rng.normal(0, 0.36, (cells, 3)).astype(np.float32)
    fn = np.stack([sx, sy, sz], -1) + tilt
    fn[:, 2] = np.abs(fn[:, 2]) + 0.25
    fn /= np.linalg.norm(fn, axis=-1, keepdims=True)
    nz = np.sqrt(np.clip(1 - rr ** 2, 0, 1))
    smooth_n = np.stack([X, Y, nz], -1)
    smooth_n /= np.maximum(np.linalg.norm(smooth_n, axis=-1, keepdims=True), 1e-6)
    n = fn[idx] * 0.74 + smooth_n * 0.26
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    Lk = unit((-0.5, -0.72, 0.62))
    diff = np.clip((n * Lk).sum(-1), 0, 1)
    alb = np.zeros(X.shape + (3,), np.float32) + PAPIER
    # typed lines on ~30% of facets, each at its own broken angle
    written = rng.random(cells) < 0.3
    ang = rng.uniform(-1.2, 1.2, cells).astype(np.float32)
    proj = (X * np.cos(ang[idx]) + Y * np.sin(ang[idx])) * r
    stripes = (np.sin(proj / 11.0 * math.pi) > 0.94) & written[idx]
    alb = np.where(stripes[..., None], alb * 0.7 + ENCRE * 0.3, alb)
    col = alb * (0.30 + 0.82 * diff)[..., None] * rgb("#fffaf3")
    # creases: thin bright/dark seams along facet borders
    seam = np.sqrt(second) - np.sqrt(best)
    crease = 1 - smooth(0.0, 0.006, seam)
    col = col * (1 - 0.12 * crease[..., None])
    # contact darkening toward the lower right (self shadow)
    col *= (0.8 + 0.2 * smooth(1.1, -0.2, X * 0.5 + Y * 0.8))[..., None]
    edge = smooth(0.0, 0.006, rad[idx] - rr).astype(np.float32) * inside
    out = np.concatenate([np.clip(col, 0, 1), edge[..., None]], -1)
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(OUT, "crumple.png"), optimize=True)
    print("baked assets/matter/crumple.png")


def grain(seed=99, size=512):
    rng = np.random.default_rng(seed)
    g = rng.normal(0.5, 0.17, (size, size)).astype(np.float32)
    g = 0.65 * g + 0.35 * blur(g, 0.7)
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray((np.clip(g, 0, 1) * 255).astype(np.uint8), "L").save(os.path.join(OUT, "grain.png"), optimize=True)
    print("baked assets/matter/grain.png")


# ---------------------------------------------------------------- particles (additive light)

def _strokes(segs, ss=2):
    """segs: list of (points, width, bin). Returns {bin: float layer} drawn with supersampling."""
    layers = {}
    imgs = {}
    for pts, wdt, b in segs:
        if b not in imgs:
            imgs[b] = Image.new("L", (W * ss, H * ss), 0)
        dr = ImageDraw.Draw(imgs[b])
        sp = [(x * ss, y * ss) for x, y in pts]
        dr.line(sp, fill=255, width=max(1, int(round(wdt * ss))), joint="curve")
        hx, hy = sp[-1]
        r = wdt * ss * 0.75
        dr.ellipse([hx - r, hy - r, hx + r, hy + r], fill=255)
    for b, im in imgs.items():
        layers[b] = np.asarray(im.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    return layers


SPARK_BINS = {0: "#FFF6E8", 1: "#FFC777", 2: "#F97316", 3: "#B8380A"}


def sparks(seed=61, origin=(600.0, 1060.0), n=420, spread=(-176.0, -4.0), speed=(420.0, 1950.0),
           g=1700.0, exposure=0.045, age_max=0.95, gain=1.0):
    rng = np.random.default_rng(seed)
    segs = []
    for _ in range(n):
        th = math.radians(rng.uniform(*spread))
        sp = math.exp(rng.uniform(math.log(speed[0]), math.log(speed[1])))
        vx, vy = sp * math.cos(th), sp * math.sin(th)
        a = age_max * rng.random() ** 1.7
        a0 = max(0.0, a - exposure * rng.uniform(0.6, 1.4))
        pts = []
        for k in range(6):
            t = a0 + (a - a0) * k / 5
            pts.append((origin[0] + vx * t, origin[1] + vy * t + 0.5 * g * t * t))
        br = math.exp(-a / 0.33)
        b = 0 if br > 0.72 else 1 if br > 0.42 else 2 if br > 0.18 else 3
        wdt = rng.uniform(1.6, 3.6) * (0.55 + 0.45 * br)
        segs.append((pts, wdt, b))
    layers = _strokes(segs)
    out = np.zeros((H, W, 3), np.float32)
    for b, lay in layers.items():
        c = rgb(SPARK_BINS[b])
        core = lay
        glow = blur(lay, 3) * 1.4 + blur(lay, 12) * 1.1
        out += (core[..., None] * c * 1.15 + glow[..., None] * c * 0.9) * gain
    # the bright source itself
    xs, ys = grid()
    r = np.hypot(xs - origin[0], ys - origin[1])
    out += (np.exp(-(r / 26.0) ** 2) * 1.3)[..., None] * rgb("#FFF4E2")
    out += (np.exp(-(r / 140.0) ** 2) * 0.35)[..., None] * ORANGE
    return out


def dust(seed=71, n=520, in_beam=True):
    rng = np.random.default_rng(seed)
    A, B = np.array([1180.0, -140.0]), np.array([120.0, 2060.0])
    u = (B - A) / np.linalg.norm(B - A)
    ss = 2
    sharp = Image.new("L", (W * ss, H * ss), 0)
    soft = Image.new("L", (W * ss, H * ss), 0)
    ds, dsf = ImageDraw.Draw(sharp), ImageDraw.Draw(soft)
    for _ in range(n):
        s = rng.uniform(150, 2300)
        width = 120 + s * 0.22
        d = rng.normal(0, width * 0.55) if in_beam else rng.uniform(-900, 900)
        x, y = A[0] + u[0] * s - u[1] * d, A[1] + u[1] * s + u[0] * d
        lum = math.exp(-(d / width) ** 2)
        if rng.random() < 0.82:
            r = rng.uniform(0.6, 2.2)
            ds.ellipse([(x - r) * ss, (y - r) * ss, (x + r) * ss, (y + r) * ss], fill=int(255 * lum * rng.uniform(0.35, 1)))
        else:
            r = rng.uniform(4, 12)
            dsf.ellipse([(x - r) * ss, (y - r) * ss, (x + r) * ss, (y + r) * ss], fill=int(255 * lum * rng.uniform(0.15, 0.4)))
    a = np.asarray(sharp.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    b = blur(np.asarray(soft.resize((W, H), Image.LANCZOS), np.float32) / 255.0, 6)
    return (a * 0.95 + blur(a, 2) * 0.6 + b)[..., None] * rgb("#fff1dc")


def flour(seed=81, n=520):
    rng = np.random.default_rng(seed)
    ss = 2
    sharp = Image.new("L", (W * ss, H * ss), 0)
    soft = Image.new("L", (W * ss, H * ss), 0)
    ds, dsf = ImageDraw.Draw(sharp), ImageDraw.Draw(soft)
    for _ in range(n):
        x, y = rng.uniform(-40, W + 40), rng.uniform(-40, H * 0.9)
        if rng.random() < 0.8:
            ln = rng.uniform(1.5, 12)
            wd = rng.uniform(0.9, 2.2)
            ds.line([(x * ss, y * ss), ((x + rng.normal(0, 1.5)) * ss, (y + ln) * ss)], fill=int(rng.uniform(60, 200)), width=max(1, int(wd * ss)))
        else:
            r = rng.uniform(8, 30)
            dsf.ellipse([(x - r) * ss, (y - r) * ss, (x + r) * ss, (y + r) * ss], fill=int(rng.uniform(18, 50)))
    a = np.asarray(sharp.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    b = blur(np.asarray(soft.resize((W, H), Image.LANCZOS), np.float32) / 255.0, 12)
    xs, ys = grid()
    cloud = fbm(H, W, 260, 5, seed + 3) * np.exp(-(((xs - W * 0.7) / (W * 0.55)) ** 2 + ((ys - H * 0.18) / (H * 0.22)) ** 2))
    cloud = smooth(0.25, 0.75, cloud) * 0.32
    return (a * 0.75 + blur(a, 1.2) * 0.35 + b + cloud)[..., None] * rgb("#f6f1e8")


# ---------------------------------------------------------------- brand

def hammer():
    src = Image.open(os.path.join(ROOT, "assets", "brand", "manoo-marteau-original.png")).convert("RGB")
    a = np.asarray(src, np.float32)
    alpha = np.clip((255.0 - a[..., 2]) / (255.0 - 56.0), 0, 1)
    ys_, xs_ = np.nonzero(alpha > 0.02)
    y0, y1, x0, x1 = ys_.min(), ys_.max(), xs_.min(), xs_.max()
    alpha = alpha[y0:y1 + 1, x0:x1 + 1]
    col = np.zeros(alpha.shape + (3,), np.float32) + ORANGE
    out = np.concatenate([col, alpha[..., None]], -1)
    path = os.path.join(ROOT, "assets", "brand", "manoo-marteau.png")
    Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA").save(path, optimize=True)
    print("baked", os.path.relpath(path, ROOT), alpha.shape)


JOBS = {
    "paper": lambda: save_rgb(paper(), "paper"),
    "weld": lambda: save_rgb(weld(), "weld"),
    "tiles": lambda: save_rgb(tiles(), "tiles"),
    "bread": lambda: save_rgb(bread(), "bread"),
    "beam": lambda: save_rgb(beam(), "beam"),
    "oven": lambda: save_rgb(oven(), "oven"),
    "sparks": lambda: save_rgba(sparks(), "sparks"),
    "sparks-rain": lambda: save_rgba(sparks(seed=62, origin=(860.0, -260.0), n=150, spread=(70.0, 150.0),
                                            speed=(300.0, 900.0), age_max=0.8, gain=0.9), "sparks-rain"),
    "dust": lambda: save_rgba(dust(), "dust"),
    "flour": lambda: save_rgba(flour(), "flour"),
    "hammer": hammer,
    "crumple": crumple,
    "grain": grain,
}

if __name__ == "__main__":
    for name in sys.argv[1:] or list(JOBS):
        JOBS[name]()

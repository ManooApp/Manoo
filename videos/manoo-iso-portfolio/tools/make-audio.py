#!/usr/bin/env python3
"""Procedural music bed + SFX track for the Manoo isometric ad (deterministic, numpy/scipy only).

Outputs
  assets/audio/music/bed.wav       45 s stereo bed, 100 BPM, F major (Fmaj7 · Dm7 · Bbmaj7 · C)
  assets/audio/sfx/sfx-track.wav   every sound effect placed on the film's cue times

Cue times mirror assets/cues.js. Run from the project root: python3 tools/make-audio.py
"""
import json
import re
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

SR = 48000
DUR = 45.0
N = int(SR * DUR)
ROOT = Path(__file__).resolve().parent.parent
rng = np.random.default_rng(7)


def cues():
    txt = (ROOT / "assets/cues.js").read_text()
    body = txt[txt.index("{") : txt.rindex("}") + 1]
    body = re.sub(r"//[^\n]*", "", body)
    body = re.sub(r"(\w+):", r'"\1":', body)
    body = re.sub(r",(\s*[}\]])", r"\1", body)
    return json.loads(body)


CU = cues()
BPM = 100.0
BEAT = 60.0 / BPM
BAR = BEAT * 4


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def t_axis(n):
    return np.arange(n) / SR


def lowpass(x, fc, order=2):
    sos = butter(order, min(fc, SR * 0.45), "low", fs=SR, output="sos")
    return sosfilt(sos, x)


def highpass(x, fc, order=2):
    sos = butter(order, fc, "high", fs=SR, output="sos")
    return sosfilt(sos, x)


def bandpass(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], "band", fs=SR, output="sos")
    return sosfilt(sos, x)


def saw(f, n, phase=0.0):
    t = t_axis(n)
    return 2.0 * ((f * t + phase) % 1.0) - 1.0


def env_adsr(n, a, d, s, r, hold=None):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    hold_n = n - a_n - d_n - r_n if hold is None else int(hold * SR)
    hold_n = max(0, hold_n)
    e = np.concatenate(
        [np.linspace(0, 1, max(1, a_n)), np.linspace(1, s, max(1, d_n)), np.full(hold_n, s), np.linspace(s, 0, max(1, r_n))]
    )
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)))
    return e[:n]


def place(buf, sig, t0, gain=1.0):
    i0 = int(round(t0 * SR))
    if i0 >= len(buf):
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    n = min(len(sig), len(buf) - i0)
    buf[i0 : i0 + n] += sig[:n] * gain


def reverb_ir(seconds=2.4, decay=3.2, seed=3):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = t_axis(n)
    env = np.exp(-decay * t)
    ir_l = r.standard_normal(n) * env
    ir_r = r.standard_normal(n) * env
    ir_l = lowpass(ir_l, 6500)
    ir_r = lowpass(ir_r, 6500)
    ir_l[:200] *= np.linspace(0, 1, 200)
    ir_r[:200] *= np.linspace(0, 1, 200)
    return ir_l / np.abs(ir_l).sum() * 18, ir_r / np.abs(ir_r).sum() * 18


IR = reverb_ir()


def stereo_reverb(mono_or_st, wet=0.3):
    if mono_or_st.ndim == 1:
        l = r = mono_or_st
    else:
        l, r = mono_or_st[:, 0], mono_or_st[:, 1]
    wl = fftconvolve(l, IR[0])[: len(l)]
    wr = fftconvolve(r, IR[1])[: len(r)]
    out = np.stack([l, r], 1) * (1 - wet) + np.stack([wl, wr], 1) * wet
    return out


def segment_gain(t, keys):
    """piecewise-linear gain over film time: keys = [(t, g), ...]"""
    ts = np.array([k[0] for k in keys])
    gs = np.array([k[1] for k in keys])
    return np.interp(t, ts, gs)


# ---------------------------------------------------------------- harmony
CHORDS = [
    ("Fmaj7", 41, [53, 57, 60, 64]),
    ("Dm7", 38, [50, 57, 60, 65]),
    ("Bbmaj7", 34, [50, 53, 57, 58]),
    ("C", 36, [48, 55, 60, 64]),
]


def chord_at(t):
    i = int((t // BAR) % 4)
    return CHORDS[i]


# ---------------------------------------------------------------- music bed
def make_bed():
    t = t_axis(N)
    L = np.zeros(N)
    R = np.zeros(N)

    # --- pad: detuned saws per chord, slow attack, lowpassed (cutoff opens through the film)
    pad = np.zeros((N, 2))
    nbars = int(np.ceil(DUR / BAR)) + 1
    for b in range(nbars):
        t0 = b * BAR
        if t0 >= DUR:
            break
        _, _, notes = CHORDS[b % 4]
        n = int(BAR * SR * 1.15)
        e = env_adsr(n, 0.5, 0.4, 0.85, 0.9)
        for k, m in enumerate(notes):
            for d, pan in ((-0.09, 0.25), (0.0, 0.5), (0.11, 0.75)):
                f = midi(m) * 2 ** (d / 12)
                s = saw(f, n, phase=(k * 0.37 + d) % 1.0) * e * 0.06
                seg = np.zeros((n, 2))
                seg[:, 0] = s * (1 - pan)
                seg[:, 1] = s * pan
                i0 = int(t0 * SR)
                m_ = min(n, N - i0)
                pad[i0 : i0 + m_] += seg[:m_]
    cutoff_keys = [(0, 420), (4.6, 900), (19.6, 1600), (28.7, 700), (32.0, 1300), (36.1, 2400), (45, 1600)]
    # piecewise filtering: process in 2.4 s blocks with the block's cutoff
    out = np.zeros_like(pad)
    blk = int(SR * 0.6)
    for i0 in range(0, N, blk):
        fc = float(np.interp(i0 / SR, [k[0] for k in cutoff_keys], [k[1] for k in cutoff_keys]))
        seg = pad[max(0, i0 - 2400) : i0 + blk]
        f = np.stack([lowpass(seg[:, 0], fc), lowpass(seg[:, 1], fc)], 1)
        out[i0 : i0 + blk] = f[-min(blk, N - i0) :]
    pad = out
    # sidechain pump on beats during the rhythmic sections
    beat_phase = (t % BEAT) / BEAT
    pump = 1 - 0.35 * np.exp(-beat_phase * 7)
    pump_on = segment_gain(t, [(0, 0), (4.5, 0), (4.7, 1), (28.6, 1), (28.8, 0), (31.9, 0), (32.1, 1), (35.4, 1), (35.6, 0), (45, 0)])
    pad *= (1 - pump_on * (1 - pump))[:, None]
    pad_gain = segment_gain(t, [(0, 0.0), (0.3, 0.55), (4.4, 0.75), (4.7, 0.6), (19.6, 0.7), (28.7, 0.85), (32.0, 0.6), (35.55, 0.55), (36.12, 1.0), (43.0, 0.8), (45, 0.0)])
    pad *= pad_gain[:, None]

    # --- drone in the intro (D/A fifths under the weld spark)
    drone_n = int(5.2 * SR)
    de = env_adsr(drone_n, 1.2, 0.5, 0.9, 1.2)
    drone = (saw(midi(38), drone_n) + saw(midi(45), drone_n, 0.3) * 0.7) * de * 0.07
    drone = lowpass(drone, 380)
    place(L, drone, 0.0)
    place(R, drone, 0.0)

    # --- pluck arpeggio (16ths), ping-pong delay
    pluck = np.zeros((N, 2))
    step = BEAT / 4
    pattern = [0, 1, 2, 3, 4, 3, 2, 1]
    arp_on = [(4.6, 28.7), (32.0, 35.5), (36.4, 44.0)]
    nsteps = int(DUR / step)
    for i in range(nsteps):
        ts = i * step
        if not any(a <= ts < b for a, b in arp_on):
            continue
        _, _, notes = chord_at(ts)
        tones = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[3] + 12, notes[0] + 24]
        m = tones[pattern[i % 8]]
        if 13.4 <= ts < 19.6:
            m += 12 if i % 4 == 0 else 0
        n = int(0.32 * SR)
        tt = t_axis(n)
        f = midi(m)
        s = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 30)) * np.exp(-tt * 13)
        s *= 0.085 * (1.0 if i % 2 == 0 else 0.72)
        pan = 0.35 if (i % 2 == 0) else 0.65
        i0 = int(ts * SR)
        k = min(n, N - i0)
        pluck[i0 : i0 + k, 0] += s[:k] * (1 - pan)
        pluck[i0 : i0 + k, 1] += s[:k] * pan
    # ping-pong delay (dotted 8th)
    dly = int(BEAT * 0.75 * SR)
    pl = pluck.copy()
    for tap, g in ((1, 0.38), (2, 0.2), (3, 0.1)):
        sh = dly * tap
        if tap % 2:
            pl[sh:, 0] += pluck[:-sh, 1] * g
            pl[sh:, 1] += pluck[:-sh, 0] * g
        else:
            pl[sh:, 0] += pluck[:-sh, 0] * g
            pl[sh:, 1] += pluck[:-sh, 1] * g
    pluck_gain = segment_gain(t, [(0, 0), (4.6, 0.0), (5.6, 0.8), (13.4, 0.95), (19.6, 1.0), (28.5, 1.0), (28.8, 0.0), (32.0, 0.0), (32.6, 0.7), (35.4, 0.7), (35.55, 0.0), (36.6, 0.0), (37.6, 0.5), (44, 0.3), (45, 0)])
    pl *= pluck_gain[:, None]

    # --- drums
    drums = np.zeros(N)

    def kick():
        n = int(0.45 * SR)
        tt = t_axis(n)
        f = 45 + 95 * np.exp(-tt * 28)
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = np.sin(ph) * np.exp(-tt * 7.5)
        s[:120] += rng.standard_normal(120) * 0.25 * np.linspace(1, 0, 120)
        return s * 0.55

    def hat(open_=False):
        n = int((0.22 if open_ else 0.06) * SR)
        s = highpass(rng.standard_normal(n), 7000) * np.exp(-t_axis(n) * (14 if open_ else 70))
        return s * 0.12

    def clap():
        n = int(0.25 * SR)
        s = bandpass(rng.standard_normal(n), 900, 2600)
        e = np.exp(-t_axis(n) * 22)
        for d in (0.0, 0.012, 0.024):
            sh = int(d * SR)
            e[sh:] = np.maximum(e[sh:], np.exp(-t_axis(n - sh) * 18))
        return s * e * 0.13

    K = kick()
    nb = int(DUR / BEAT)
    for b in range(nb):
        tb = b * BEAT
        sec_a = 4.6 <= tb < 28.6
        sec_d = 32.0 <= tb < 35.4
        if sec_a or sec_d:
            if b % 2 == 0 or (19.6 <= tb < 28.6):
                place(drums, K, tb, 1.0 if not sec_d else 0.7)
            place(drums, hat(), tb + BEAT / 2, 0.9)
            if 13.4 <= tb < 28.6 and b % 2 == 1:
                place(drums, clap(), tb, 1.0)
            if 19.6 <= tb < 28.6:
                place(drums, hat(True), tb + BEAT / 2, 0.6)
                place(drums, hat(), tb + BEAT / 4, 0.45)
                place(drums, hat(), tb + 3 * BEAT / 4, 0.45)

    # --- sub bass in the build
    sub = np.zeros(N)
    for b in range(int(DUR / BAR) + 1):
        tb = b * BAR
        if not (19.6 - BAR < tb < 28.6):
            continue
        _, root, _ = CHORDS[b % 4]
        for q in range(4):
            tq = tb + q * BEAT
            if tq < 19.6 or tq >= 28.6:
                continue
            n = int(BEAT * 0.9 * SR)
            tt = t_axis(n)
            s = np.sin(2 * np.pi * midi(root + 12) * tt) * env_adsr(n, 0.01, 0.1, 0.8, 0.12) * 0.22
            place(sub, s, tq)

    # --- final chord hit at the logo (wide, bright, long)
    hit_n = int(8.0 * SR)
    he = env_adsr(hit_n, 0.02, 1.5, 0.45, 3.5)
    hit = np.zeros(hit_n)
    for m in (41, 53, 57, 60, 64, 67, 72):
        for d in (-0.07, 0.07):
            hit += saw(midi(m) * 2 ** (d / 12), hit_n, phase=(m * 0.13) % 1) * 0.035
    hit = lowpass(hit, 3200) * he
    place(L, hit, CU["manoo"] - 0.02, 0.9)
    place(R, hit, CU["manoo"] - 0.02, 0.9)

    mix = np.stack([L, R], 1) + pad + pl + np.stack([drums, drums], 1) * 0.9 + np.stack([sub, sub], 1)
    mix = stereo_reverb(mix, wet=0.22)
    mix = np.stack([highpass(mix[:, 0], 38), highpass(mix[:, 1], 38)], 1)
    # gentle glue: soft clip + normalise
    mix = np.tanh(mix * 1.4) / 1.4
    fade = segment_gain(t, [(0, 0.0), (0.25, 1.0), (43.6, 1.0), (45.0, 0.0)])
    mix *= fade[:, None]
    peak = np.max(np.abs(mix))
    mix = mix / peak * 0.7
    return mix


# ---------------------------------------------------------------- SFX
SFX_LIB = ROOT.parent.parent / ".claude/skills/media-use/audio/assets/sfx"


def load(name):
    src = ROOT / f"assets/audio/sfx-src/{name}.wav"
    if not src.exists():  # decode from the media-use bundled library on first run
        import subprocess

        src.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(SFX_LIB / f"{name}.mp3"), "-ar", str(SR), "-ac", "2", str(src)], check=True)
    with wave.open(str(src), "rb") as w:
        raw = w.readframes(w.getnframes())
        a = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
        return a.reshape(-1, w.getnchannels())


def shutter():
    """two-blade mechanical shutter click + flash whine tail"""
    n = int(0.35 * SR)
    s = np.zeros(n)
    for d, g in ((0.0, 1.0), (0.055, 0.8)):
        k = int(0.018 * SR)
        burst = bandpass(rng.standard_normal(k), 1800, 7000) * np.exp(-t_axis(k) * 260)
        place(s, burst, d, g)
        thump = np.sin(2 * np.pi * 180 * t_axis(k)) * np.exp(-t_axis(k) * 200) * 0.6
        place(s, thump, d, g)
    whine_n = int(0.3 * SR)
    tt = t_axis(whine_n)
    whine = np.sin(2 * np.pi * (5200 + 2600 * tt) * tt) * np.exp(-tt * 14) * 0.05
    place(s, whine, 0.06)
    return np.stack([s, s], 1) * 0.9


def crackle(seconds, density=240, seed=11):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    s = np.zeros(n)
    nev = int(seconds * density)
    for _ in range(nev):
        i = r.integers(0, n - 400)
        k = r.integers(40, 400)
        s[i : i + k] += highpass(r.standard_normal(k), 2500) * np.exp(-np.arange(k) / (k / 4)) * r.uniform(0.2, 1)
    hum = bandpass(r.standard_normal(n), 90, 240) * 0.25
    return np.stack([s * 0.55 + hum, s * 0.5 + hum], 1)


def make_sfx():
    buf = np.zeros((N, 2))
    S = {k: load(k) for k in ["whoosh", "whoosh-short", "whoosh-cinematic", "pop", "click", "click-soft", "typing", "chime", "sparkle", "ping", "impact-bass-1", "impact-bass-2", "riser", "key-press"]}

    def put(name, t0, g=1.0, sl=None):
        s = S[name] if sl is None else S[name][: int(sl * SR)]
        place(buf, s, t0, g)

    # S1 — spark ignition, word pops, "montre" punch, portal
    put("sparkle", 0.1, 0.35)
    for tw, g in ((CU["savoirFaire"], 0.35), (CU["savoirFaire"] + 0.14, 0.4), (CU["neSe"], 0.3), (CU["raconte"], 0.32), (CU["pas"], 0.38), (CU["ilSe"], 0.32)):
        put("pop", tw - 0.02, g)
    put("whoosh-short", CU["ilSe"] - 0.2, 0.35)
    put("impact-bass-2", CU["montre"] - 0.16, 0.55)
    put("riser", 4.4 - 2.6, 0.12, sl=2.7)
    put("pop", 4.4, 0.5)
    put("whoosh", 4.62, 0.55)
    place(buf, crackle(1.35), 4.45, 0.5)
    # S2 — mask, viewfinder blips, shutters, card pops, whips
    put("click-soft", CU["maskUp"], 0.35)
    for tv in (CU["photographient"], CU["chantier"] - 0.05, CU["ouvrage"] + 0.1):
        put("key-press", tv, 0.3)
    for tf in (CU["flashA"], CU["flashB"], CU["flashC"]):
        place(buf, shutter(), tf - 0.03, 1.0)
        put("pop", tf + 0.08, 0.5)
        put("sparkle", tf + 0.05, 0.22)
    put("whoosh-short", CU["whipAB"] - 0.05, 0.65)
    put("whoosh-short", CU["whipBC"] - 0.05, 0.65)
    put("whoosh", CU["pullback"] + 0.05, 0.5)
    # S3 — cards fly in, phone rises, bubbles, UI
    put("whoosh-cinematic", 13.0, 0.25, sl=2.2)
    for k, tt in enumerate((13.38, 13.48, 13.58)):
        put("whoosh-short", tt, 0.32)
    put("impact-bass-1", 13.62, 0.28)
    for i in range(7):
        put("pop", 13.95 + 0.08 * i, 0.22)
    put("click", 13.62, 0.35)
    put("pop", 13.98, 0.4)
    put("typing", CU["unTitre"] + 0.02, 0.45, sl=0.75)
    put("click", CU["tap"], 0.55)
    put("chime", CU["tap"] + 0.06, 0.32)
    for tl in (16.05, 17.05, 17.85):
        put("pop", tl + 0.15, 0.35)
    put("whoosh-short", 16.85, 0.3)
    put("whoosh-short", 17.6, 0.3)
    put("whoosh", 18.9, 0.45)
    # S4 — audiences assemble, paths, lights
    for i in range(3):
        put("pop", 19.2 + i * 0.15, 0.25)
    put("sparkle", 20.95, 0.4)
    put("whoosh-short", 21.0, 0.3)
    for tk in (CU["entreprises"] - 0.1, CU["lycees"] - 0.1, CU["clients"] - 0.1):
        put("ping", tk, 0.38)
        put("pop", tk + 0.15, 0.35)
    put("whoosh-short", 24.28, 0.55)
    put("whoosh-short", 26.38, 0.55)
    put("whoosh", 27.95, 0.45)
    # S5 — statement, timeline
    put("impact-bass-1", CU["preuve"] - 0.08, 0.35)
    put("whoosh", CU["trace"] - 0.3, 0.45)
    for i, tt in enumerate(np.linspace(32.6, 34.6, 8)):
        put("click-soft", float(tt), 0.18)
    put("riser", 35.55 - 2.0, 0.11, sl=2.05)
    put("whoosh-short", 35.25, 0.45)
    # S6 — logo
    put("pop", 35.55, 0.55)
    put("impact-bass-2", CU["manoo"] - 0.02, 0.7)
    put("sparkle", CU["manoo"] + 0.3, 0.35)
    for i in range(5):
        put("click-soft", CU["manoo"] + 0.42 + 0.055 * i, 0.16)
    put("pop", CU["manoo"] + 0.82, 0.45)
    put("pop", CU["demandez"], 0.45)
    put("click", CU["demandez"] + 0.78, 0.5)
    put("chime", CU["site"] - 0.1, 0.3)
    peak = np.max(np.abs(buf))
    if peak > 0.95:
        buf = buf / peak * 0.95
    return buf


def write(path, a):
    path.parent.mkdir(parents=True, exist_ok=True)
    a = np.clip(a, -1, 1)
    pcm = (a * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    write(ROOT / "assets/audio/music/bed.wav", make_bed())
    write(ROOT / "assets/audio/sfx/sfx-track.wav", make_sfx())
    print("ok")

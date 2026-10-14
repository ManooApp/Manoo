#!/usr/bin/env python3
"""Procedural music bed + SFX track for the Manoo explainer (deterministic, numpy/scipy only).

Outputs
  assets/audio/music/bed.wav       55.5 s stereo bed, 112 BPM, F major (F · Am · Dm · Bb)
  assets/audio/sfx/sfx-track.wav   every sound effect placed on the film's cue times

Cue times come from assets/cues.js (tools/make-cues.py). Run from the project root:
  python3 tools/make-audio.py
SFX samples: the media-use bundled library (see its CREDITS.md), decoded on first run.
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
DUR = 55.5
N = int(SR * DUR)
ROOT = Path(__file__).resolve().parent.parent
rng = np.random.default_rng(7)


def cues():
    txt = (ROOT / "assets/cues.js").read_text()
    body = txt[txt.index("{") : txt.rindex("}") + 1]
    return json.loads(body)


CU = cues()
BPM = 112.0
BEAT = 60.0 / BPM
BAR = BEAT * 4


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def t_axis(n):
    return np.arange(n) / SR


def lowpass(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR * 0.45), "low", fs=SR, output="sos"), x)


def highpass(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def bandpass(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def saw(f, n, phase=0.0):
    return 2.0 * ((f * t_axis(n) + phase) % 1.0) - 1.0


def env_adsr(n, a, d, s, r):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    hold_n = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([np.linspace(0, 1, max(1, a_n)), np.linspace(1, s, max(1, d_n)), np.full(hold_n, s), np.linspace(s, 0, max(1, r_n))])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def place(buf, sig, t0, gain=1.0):
    i0 = int(round(t0 * SR))
    if i0 >= len(buf):
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    n = min(len(sig), len(buf) - i0)
    buf[i0 : i0 + n] += sig[:n] * gain


def reverb_ir(seconds=2.6, decay=3.0, seed=3):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    env = np.exp(-decay * t_axis(n))
    ir = [lowpass(r.standard_normal(n) * env, 7000) for _ in range(2)]
    for x in ir:
        x[:200] *= np.linspace(0, 1, 200)
    return [x / np.abs(x).sum() * 18 for x in ir]


IR = reverb_ir()


def stereo_reverb(st, wet=0.25):
    wl = fftconvolve(st[:, 0], IR[0])[: len(st)]
    wr = fftconvolve(st[:, 1], IR[1])[: len(st)]
    return st * (1 - wet) + np.stack([wl, wr], 1) * wet


def seg(t, keys):
    return np.interp(t, [k[0] for k in keys], [k[1] for k in keys])


# ---------------------------------------------------------------- arrangement (film time)
# sections: groove on/off windows
GROOVE = [(7.95, 22.35), (27.0, 32.5), (32.85, 42.5), (47.4, 53.4)]
CLAPS = [(9.3, 22.35), (27.2, 32.5), (36.0, 42.5), (48.4, 53.4)]
BREAK = [(22.35, 27.0), (42.5, 47.4)]  # pad + soft pulse only
CHORDS = [("F", 41, [53, 57, 60, 64]), ("Am", 45, [52, 57, 60, 64]), ("Dm", 38, [50, 53, 57, 62]), ("Bb", 34, [50, 53, 58, 62])]


def in_any(ts, wins):
    return any(a <= ts < b for a, b in wins)


def make_bed():
    t = t_axis(N)
    out = np.zeros((N, 2))
    nbars = int(np.ceil(DUR / BAR)) + 1

    # --- pad (detuned saws), filter opens with the story
    pad = np.zeros((N, 2))
    for b in range(nbars):
        t0 = b * BAR
        if t0 >= DUR:
            break
        _, _, notes = CHORDS[b % 4]
        n = int(BAR * SR * 1.15)
        e = env_adsr(n, 0.45, 0.4, 0.85, 0.9)
        for k, m in enumerate(notes):
            for d, pan in ((-0.08, 0.2), (0.0, 0.5), (0.1, 0.8)):
                s = saw(midi(m) * 2 ** (d / 12), n, phase=(k * 0.37 + d) % 1.0) * e * 0.05
                i0 = int(t0 * SR)
                k_ = min(n, N - i0)
                pad[i0 : i0 + k_, 0] += s[:k_] * (1 - pan)
                pad[i0 : i0 + k_, 1] += s[:k_] * pan
    cut = [(0, 380), (7.9, 900), (8.25, 2600), (10.0, 1500), (22.35, 650), (26.9, 1200), (27.05, 2800), (30.3, 3400), (32.5, 1400), (42.5, 800), (45.2, 1600), (47.45, 3000), (55.5, 1200)]
    filt = np.zeros_like(pad)
    blk = int(SR * 0.5)
    for i0 in range(0, N, blk):
        fc = float(np.interp(i0 / SR, [k[0] for k in cut], [k[1] for k in cut]))
        sg = pad[max(0, i0 - 2400) : i0 + blk]
        f = np.stack([lowpass(sg[:, 0], fc), lowpass(sg[:, 1], fc)], 1)
        filt[i0 : i0 + blk] = f[-min(blk, N - i0) :]
    pad = filt
    ph = (t % BEAT) / BEAT
    pump_on = np.array([in_any(x, GROOVE) for x in t[::480]]).repeat(480)[:N].astype(float)
    pad *= (1 - pump_on * 0.3 * np.exp(-ph * 7))[:, None]
    pad *= seg(t, [(0, 0.0), (0.4, 0.5), (7.9, 0.6), (8.2, 0.9), (22.35, 0.75), (42.5, 0.9), (47.45, 1.0), (55.5, 0.0)])[:, None]
    out += pad

    # --- pluck arpeggio (16ths) with ping-pong delay
    pl = np.zeros((N, 2))
    step = BEAT / 4
    pattern = [0, 2, 1, 3, 2, 4, 3, 1]
    for i in range(int(DUR / step)):
        ts = i * step
        if not (5.4 <= ts < 22.35 or 24.4 <= ts < 42.5 or 47.45 <= ts < 54.0):
            continue
        _, _, notes = CHORDS[int((ts // BAR) % 4)]
        tones = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[3] + 12, notes[0] + 24]
        m = tones[pattern[i % 8]]
        n = int(0.3 * SR)
        tt = t_axis(n)
        f = midi(m)
        s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 30)) * np.exp(-tt * 14)
        s *= 0.075 * (1.0 if i % 2 == 0 else 0.7)
        pan = 0.32 if i % 2 == 0 else 0.68
        i0 = int(ts * SR)
        k = min(n, N - i0)
        pl[i0 : i0 + k, 0] += s[:k] * (1 - pan)
        pl[i0 : i0 + k, 1] += s[:k] * pan
    dly = int(BEAT * 0.75 * SR)
    pp = pl.copy()
    for tap, g in ((1, 0.35), (2, 0.18), (3, 0.09)):
        sh = dly * tap
        if tap % 2:
            pp[sh:, 0] += pl[:-sh, 1] * g
            pp[sh:, 1] += pl[:-sh, 0] * g
        else:
            pp[sh:] += pl[:-sh] * g
    pp *= seg(t, [(0, 0), (5.4, 0.0), (6.4, 0.7), (8.2, 0.9), (22.35, 0.55), (24.4, 0.35), (27.0, 0.95), (42.5, 0.4), (47.45, 0.9), (54.0, 0.5), (55.5, 0)])[:, None]
    out += pp

    # --- drums
    dr = np.zeros(N)

    def kick():
        n = int(0.42 * SR)
        tt = t_axis(n)
        f = 46 + 100 * np.exp(-tt * 30)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 8)
        s[:120] += rng.standard_normal(120) * 0.25 * np.linspace(1, 0, 120)
        return s * 0.55

    def hat(open_=False):
        n = int((0.2 if open_ else 0.05) * SR)
        return highpass(rng.standard_normal(n), 7200) * np.exp(-t_axis(n) * (15 if open_ else 75)) * 0.11

    def clap():
        n = int(0.24 * SR)
        s = bandpass(rng.standard_normal(n), 900, 2700)
        e = np.exp(-t_axis(n) * 22)
        for d in (0.011, 0.022):
            sh = int(d * SR)
            e[sh:] = np.maximum(e[sh:], np.exp(-t_axis(n - sh) * 18))
        return s * e * 0.13

    def shaker():
        n = int(0.09 * SR)
        return bandpass(rng.standard_normal(n), 4000, 11000) * env_adsr(n, 0.02, 0.03, 0.4, 0.03) * 0.06

    K = kick()
    for b in range(int(DUR / BEAT) + 1):
        tb = b * BEAT
        if in_any(tb, GROOVE):
            place(dr, K, tb, 0.95)
            place(dr, hat(), tb + BEAT / 2, 0.85)
            place(dr, shaker(), tb + BEAT / 4, 0.7)
            place(dr, shaker(), tb + 3 * BEAT / 4, 0.55)
            if in_any(tb, CLAPS) and b % 2 == 1:
                place(dr, clap(), tb, 1.0)
            if (27.2 <= tb < 32.5 or 48.4 <= tb < 53.4) and b % 2 == 0:
                place(dr, hat(True), tb + BEAT / 2, 0.5)
        elif in_any(tb, BREAK) and b % 2 == 0:
            place(dr, K, tb, 0.42)  # heartbeat pulse in the breakdowns

    # --- sub bass (8ths on the root) in the grooves
    sub = np.zeros(N)
    for b in range(nbars):
        tb = b * BAR
        _, root, _ = CHORDS[b % 4]
        for q in range(8):
            tq = tb + q * BEAT / 2
            if not in_any(tq, GROOVE):
                continue
            n = int(BEAT * 0.45 * SR)
            tt = t_axis(n)
            s = np.sin(2 * np.pi * midi(root + 12) * tt) * env_adsr(n, 0.005, 0.08, 0.75, 0.08) * (0.2 if q % 2 == 0 else 0.13)
            place(sub, s, tq)

    # --- risers into the big moments + chord hits
    def riser(dur):
        n = int(dur * SR)
        tt = t_axis(n)
        noise = highpass(rng.standard_normal(n), 1800) * (tt / dur) ** 2 * 0.12
        tone = np.sin(2 * np.pi * (300 * tt + 900 * tt ** 2 / dur)) * (tt / dur) ** 2 * 0.04
        return noise + tone

    for t_hit, d in ((CU["manoo1"], 1.6), (CU["photo"], 2.4), (CU["manoo2"], 1.4)):
        r = riser(d)
        place(sub, r, t_hit - d, 0.9)

    def chord_hit(notes, dur=6.0, gain=0.03):
        n = int(dur * SR)
        h = np.zeros(n)
        for m in notes:
            for d in (-0.07, 0.07):
                h += saw(midi(m) * 2 ** (d / 12), n, phase=(m * 0.13) % 1) * gain
        return lowpass(h, 3600) * env_adsr(n, 0.02, 1.2, 0.4, 3.0)

    H1 = chord_hit([41, 53, 57, 60, 64, 69, 72])
    for th in (CU["manoo1"] - 0.03, CU["photo"] - 0.02, CU["manoo2"] - 0.03):
        place(sub, H1, th, 0.8)

    mix = out + np.stack([dr, dr], 1) * 0.9 + np.stack([sub, sub], 1)
    mix = stereo_reverb(mix, wet=0.22)
    mix = np.stack([highpass(mix[:, 0], 36), highpass(mix[:, 1], 36)], 1)
    mix = np.tanh(mix * 1.4) / 1.4
    mix *= seg(t, [(0, 0.0), (0.2, 1.0), (54.2, 1.0), (55.5, 0.0)])[:, None]
    return mix / np.max(np.abs(mix)) * 0.7


# ---------------------------------------------------------------- SFX
SFX_LIB = Path("/root/.claude/skills/media-use/audio/assets/sfx")


def load(name):
    src = ROOT / f"assets/audio/sfx-src/{name}.wav"
    if not src.exists():
        src.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(SFX_LIB / f"{name}.mp3"), "-ar", str(SR), "-ac", "2", str(src)], check=True)
    with wave.open(str(src), "rb") as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
        return a.reshape(-1, w.getnchannels())


def shutter():
    n = int(0.35 * SR)
    s = np.zeros(n)
    for d, g in ((0.0, 1.0), (0.055, 0.8)):
        k = int(0.018 * SR)
        place(s, bandpass(rng.standard_normal(k), 1800, 7000) * np.exp(-t_axis(k) * 260), d, g)
        place(s, np.sin(2 * np.pi * 180 * t_axis(k)) * np.exp(-t_axis(k) * 200) * 0.6, d, g)
    wn = int(0.3 * SR)
    tt = t_axis(wn)
    place(s, np.sin(2 * np.pi * (5200 + 2600 * tt) * tt) * np.exp(-tt * 14) * 0.05, 0.06)
    return np.stack([s, s], 1) * 0.9


def crackle(seconds, density=260, seed=11):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    s = np.zeros(n)
    for _ in range(int(seconds * density)):
        i = r.integers(0, n - 400)
        k = r.integers(40, 400)
        s[i : i + k] += highpass(r.standard_normal(k), 2500) * np.exp(-np.arange(k) / (k / 4)) * r.uniform(0.2, 1)
    hum = bandpass(r.standard_normal(n), 90, 240) * 0.25
    e = env_adsr(n, 0.05, 0.1, 1.0, 0.25)
    return np.stack([(s * 0.55 + hum) * e, (s * 0.5 + hum) * e], 1)


def make_sfx():
    buf = np.zeros((N, 2))
    names = ["whoosh", "whoosh-short", "whoosh-cinematic", "pop", "click", "click-soft", "typing", "chime", "sparkle", "ping", "impact-bass-1", "impact-bass-2", "key-press", "notification"]
    S = {k: load(k) for k in names}

    def put(name, t0, g=1.0, sl=None):
        s = S[name] if sl is None else S[name][: int(sl * SR)]
        place(buf, s, t0, g)

    c = CU
    # F1 — hook
    put("whoosh-cinematic", 0.0, 0.3, sl=2.0)
    for tw in (c["batiment"], c["artisanat"], c["industrie"]):
        put("pop", tw - 0.12, 0.42)
    put("whoosh-short", 3.15, 0.35)
    put("whoosh-short", 3.35, 0.3)
    put("pop", c["talent"] - 0.2, 0.25)
    put("pop", 4.55, 0.25)
    put("whoosh-short", c["cv1"] - 0.05, 0.5)
    put("impact-bass-1", c["cv1"] + 0.02, 0.32)
    put("whoosh", 5.3, 0.4)
    for i, tt in enumerate((5.5, 5.66, 5.82)):
        put("whoosh-short", tt, 0.3)
    put("sparkle", c["terrain"] - 0.05, 0.3)
    put("whoosh", 7.38, 0.45)
    # F2 — logo, network, portfolio
    put("impact-bass-2", c["manoo1"] - 0.06, 0.5)
    put("sparkle", c["manoo1"] + 0.05, 0.35)
    for i in range(5):
        put("click-soft", c["manoo1"] + 0.12 + 0.05 * i, 0.15)
    put("pop", c["manoo1"] + 0.45, 0.4)
    put("whoosh", c["reseau"] - 0.32, 0.45)
    put("whoosh-short", c["reseau"] - 0.05, 0.4)
    for i in range(12):
        put("pop", c["social"] + 0.07 * i, 0.12)
    put("whoosh-short", c["portfolio1"] - 0.15, 0.35)
    for i in range(3):
        put("pop", c["montrer"] - 0.05 + 0.12 * i, 0.35)
    put("whoosh-short", 14.32, 0.3)
    # F3 — profiles, sign-up
    put("whoosh-short", 14.55, 0.3)
    for cue in ("artisans", "apprentis", "entreprises", "ecoles"):
        put("pop", c[cue] - 0.1, 0.45)
        put("click-soft", c[cue] - 0.08, 0.2)
    put("pop", c["cfa"], 0.3)
    put("whoosh", c["chacun"] - 0.4, 0.4)
    put("click", c["chacun"] - 0.25, 0.4)
    put("typing", c["chacun"] + 0.15, 0.35, sl=0.42)
    put("click", c["cree"] - 0.12, 0.35)
    put("click", c["profil"] - 0.14, 0.35)
    put("click", 21.2, 0.4)
    put("chime", 21.35, 0.3)
    put("whoosh-short", 21.75, 0.3)
    # F4 — Jules: card, atelier, flash, portfolio, publish, network
    put("pop", c["jules"] - 0.1, 0.5)
    put("ping", c["jules"] - 0.05, 0.25)
    put("click-soft", c["apprenti"] - 0.05, 0.3)
    put("click-soft", c["metallier"] - 0.05, 0.3)
    put("whoosh-cinematic", 24.3, 0.35, sl=1.8)
    place(buf, crackle(0.75), 24.53, 0.55)
    put("click-soft", 25.3, 0.25)
    place(buf, shutter(), c["photo"] - 0.03, 1.0)
    put("sparkle", c["photo"] + 0.02, 0.3)
    put("whoosh-short", 27.12, 0.45)
    put("pop", 27.18, 0.3)
    put("pop", c["ajoute"] - 0.05, 0.3)
    put("typing", c["ajoute"] + 0.02, 0.35, sl=0.5)
    put("click", 28.42, 0.5)
    put("chime", c["portfolio2"] - 0.05, 0.3)
    put("whoosh-short", 28.95, 0.3)
    put("pop", 29.05, 0.25)
    put("click", 29.18, 0.4)
    put("typing", 29.24, 0.32, sl=0.42)
    put("click", c["partage"] + 0.02, 0.5)
    put("chime", c["partage"] + 0.25, 0.3)
    put("whoosh", c["tout"] - 0.1, 0.45)
    for i in range(8):
        put("pop", c["tout"] + 0.12 + 0.07 * i, 0.16)
    put("sparkle", c["reseau2"] - 0.05, 0.35)
    for i in range(3):
        put("ping", c["reseau2"] + 0.15 + 0.32 * i, 0.22)
    put("ping", 32.05, 0.35)
    put("whoosh", 32.42, 0.55)
    # F5 — the company side
    put("whoosh-short", 32.62, 0.55)
    put("pop", c["entreprise"], 0.3)
    put("whoosh-short", c["atelier"] - 0.1, 0.25)
    put("click", 35.08, 0.45)
    put("click-soft", 35.12, 0.25)
    put("click", c["metallier2"] + 0.18, 0.45)
    put("click", 35.92, 0.4)
    for i in range(6):
        put("key-press", 35.96 + 0.045 * i, 0.22)
    put("whoosh-short", c["filtre"] - 0.25, 0.3)
    for i in range(3):
        put("pop", c["filtre"] + 0.05 + 0.1 * i, 0.28)
    put("pop", c["decouvre"] - 0.08, 0.45)
    put("ping", c["decouvre"] - 0.02, 0.22)
    put("whoosh-short", c["portail2"] - 0.25, 0.25)
    put("click", c["jules2"] - 0.12, 0.45)
    put("whoosh-short", c["jules2"], 0.3)
    put("click", 40.36, 0.45)
    put("chime", 40.48, 0.28)
    put("click", c["ecrit"] - 0.02, 0.45)
    put("whoosh-short", c["ecrit"] + 0.02, 0.3)
    put("typing", 41.25, 0.35, sl=0.7)
    put("click", 42.06, 0.45)
    put("whoosh-short", 42.1, 0.35)
    put("whoosh", 42.5, 0.5)
    # F6 — the payoff
    put("notification", 43.12, 0.55)
    put("pop", 43.3, 0.35)
    put("pop", c["pas"] - 0.1, 0.2)
    put("whoosh-short", c["cv2"], 0.4)
    put("impact-bass-1", c["cv2"] + 0.03, 0.28)
    put("ping", 44.45, 0.25)
    put("pop", c["travail"] - 0.3, 0.3)
    put("whoosh", 46.72, 0.4)
    # F7 — signature
    put("whoosh-cinematic", 47.0, 0.3, sl=1.6)
    put("impact-bass-2", c["manoo2"] - 0.08, 0.5)
    put("sparkle", c["manoo2"] + 0.05, 0.35)
    for i in range(5):
        put("click-soft", c["manoo2"] + 0.08 + 0.05 * i, 0.15)
    put("pop", c["manoo2"] + 0.42, 0.4)
    put("pop", c["revolution"] - 0.12, 0.2)
    for i in range(4):
        put("pop", c["rejoignez"] - 0.15 + 0.08 * i, 0.25)
    put("pop", c["site"] - 0.45, 0.35)
    for i in range(8):
        put("key-press", c["site"] - 0.25 + 0.075 * i, 0.22)
    put("pop", 52.35, 0.35)
    put("click", 53.05, 0.5)
    put("chime", 53.1, 0.32)
    peak = np.max(np.abs(buf))
    return buf / peak * 0.95 if peak > 0.95 else buf


def write(path, a):
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    write(ROOT / "assets/audio/music/bed.wav", make_bed())
    write(ROOT / "assets/audio/sfx/sfx-track.wav", make_sfx())
    print("ok")

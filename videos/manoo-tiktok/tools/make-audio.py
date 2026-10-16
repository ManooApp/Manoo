#!/usr/bin/env python3
"""Music + sound design for the Manoo TikTok ad (deterministic, numpy/scipy only, no voice).

Outputs
  assets/audio/music/track.wav    43 s stereo, 120 BPM, A minor pop (Am · F · C · G), drops on the cues
  assets/audio/sfx/sfx-track.wav  every sound effect placed on the cue sheet

Cue times come from assets/cues.js. SFX samples: the media-use bundled library (see its CREDITS.md), decoded on
first run into assets/audio/sfx-src/ (not versioned). Run from the project root: python3 tools/make-audio.py
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
ROOT = Path(__file__).resolve().parent.parent
rng = np.random.default_rng(16)


def cues():
    txt = (ROOT / "assets/cues.js").read_text()
    body = txt[txt.index("{") : txt.rindex("}") + 1]
    body = re.sub(r"//[^\n]*", "", body)
    body = re.sub(r"(\w+):", r'"\1":', body)
    body = re.sub(r",(\s*[}\]])", r"\1", body)
    return json.loads(body)


C = cues()
DUR = C["END"]
N = int(SR * DUR)
BPM = 120.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
# Am · F · C · G  (root, chord tones)
CHORDS = [(45, [57, 60, 64, 69]), (41, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])]

INTRO = [(0.0, C["arrow"])]  # muffled groove, filter opening
GROOVE = [(C["logo"], C["zero"] - 0.5), (C["zero"], C["montres"]), (C["slam"], C["click"])]
FILLS = [(C["zero"] - 0.5, C["zero"]), (C["montres"] - 1.0, C["montres"])]  # snare rolls into the hits
BREAK = [(C["montres"], C["slam"])]  # filtered pad + ticks only


def in_any(t, wins):
    return any(a <= t < b for a, b in wins)


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


def env(n, a, d, s, r):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    h = max(0, n - a_n - d_n - r_n)
    e = np.concatenate([np.linspace(0, 1, max(1, a_n)), np.linspace(1, s, max(1, d_n)), np.full(h, s), np.linspace(s, 0, max(1, r_n))])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def place(buf, sig, t0, gain=1.0):
    i0 = int(round(t0 * SR))
    if i0 >= len(buf):
        return
    if i0 < 0:
        sig, i0 = sig[-i0:], 0
    n = min(len(sig), len(buf) - i0)
    buf[i0 : i0 + n] += sig[:n] * gain


def seg(t, keys):
    return np.interp(t, [k[0] for k in keys], [k[1] for k in keys])


def reverb_ir(seconds=2.2, decay=3.4, seed=5):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    e = np.exp(-decay * t_axis(n))
    ir = [lowpass(r.standard_normal(n) * e, 7500) for _ in range(2)]
    for x in ir:
        x[:200] *= np.linspace(0, 1, 200)
    return [x / np.abs(x).sum() * 16 for x in ir]


IR = reverb_ir()


def verb(st, wet):
    wl = fftconvolve(st[:, 0], IR[0])[: len(st)]
    wr = fftconvolve(st[:, 1], IR[1])[: len(st)]
    return st * (1 - wet) + np.stack([wl, wr], 1) * wet


def chord_at(t):
    return CHORDS[int(t // BAR) % 4]


# ------------------------------------------------------------------ instruments
def kick():
    n = int(0.36 * SR)
    tt = t_axis(n)
    f = 48 + 120 * np.exp(-tt * 34)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
    s[:160] += rng.standard_normal(160) * 0.3 * np.linspace(1, 0, 160)
    return np.tanh(s * 1.6) * 0.62


def clap():
    n = int(0.22 * SR)
    s = bandpass(rng.standard_normal(n), 900, 3200)
    e = np.exp(-t_axis(n) * 20)
    for d in (0.009, 0.018, 0.027):
        sh = int(d * SR)
        e[sh:] = np.maximum(e[sh:], np.exp(-t_axis(n - sh) * 17))
    return s * e * 0.17


def snare():
    n = int(0.16 * SR)
    tt = t_axis(n)
    return (bandpass(rng.standard_normal(n), 1200, 6000) * np.exp(-tt * 26) * 0.12
            + np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 30) * 0.08)


def hat(open_=False):
    n = int((0.22 if open_ else 0.045) * SR)
    return highpass(rng.standard_normal(n), 7500) * np.exp(-t_axis(n) * (13 if open_ else 80)) * (0.09 if open_ else 0.07)


def impact(big=True):
    n = int((2.6 if big else 1.4) * SR)
    tt = t_axis(n)
    boom = np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-tt * 9)) / SR) * np.exp(-tt * (2.2 if big else 4))
    crash = highpass(rng.standard_normal(n), 4500) * np.exp(-tt * (1.6 if big else 3)) * 0.18
    s = boom * (0.55 if big else 0.35) + crash
    return np.stack([s, s * 0.96], 1)


def riser(dur):
    n = int(dur * SR)
    tt = t_axis(n)
    k = (tt / dur) ** 2
    noise = highpass(rng.standard_normal(n), 1500) * k * 0.14
    tone = np.sin(2 * np.pi * (220 * tt + 880 * tt ** 2 / dur)) * k * 0.05
    s = noise + tone
    return np.stack([s, s], 1)


def make_track():
    t = t_axis(N)
    out = np.zeros((N, 2))
    nbars = int(DUR / BAR) + 1

    # --- pumping pad (sidechained to the beat in the grooves)
    pad = np.zeros((N, 2))
    for b in range(nbars):
        t0 = b * BAR
        _, notes = CHORDS[b % 4]
        n = int(BAR * SR) + int(0.4 * SR)
        e = env(n, 0.08, 0.3, 0.8, 0.4)
        for k, m in enumerate(notes):
            for d, pan in ((-0.09, 0.15), (0.0, 0.5), (0.11, 0.85)):
                s = saw(midi(m) * 2 ** (d / 12), n, phase=(k * 0.31 + d) % 1.0) * e * 0.032
                place(pad[:, 0], s * (1 - pan), t0)
                place(pad[:, 1], s * pan, t0)
    pad = np.stack([lowpass(pad[:, 0], 2600), lowpass(pad[:, 1], 2600)], 1)
    ph = (t % BEAT) / BEAT
    grooving = np.array([in_any(x, GROOVE) for x in t[::480]]).repeat(480)[:N].astype(float)
    pad *= (1 - grooving * 0.55 * np.exp(-ph * 6))[:, None]
    pad *= seg(t, [(0, 0.5), (C["arrow"], 0.7), (C["logo"], 1.0), (C["montres"], 1.0), (C["slam"], 1.1), (C["click"], 1.2), (DUR - 0.6, 0.9), (DUR, 0.0)])[:, None]
    out += pad

    # --- pluck arpeggio, 16ths, ping-pong delay
    pl = np.zeros((N, 2))
    step = BEAT / 4
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]
    for i in range(int(DUR / step)):
        ts = i * step
        if in_any(ts, BREAK) or ts >= C["click"]:
            continue
        _, notes = chord_at(ts)
        tones = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[3] + 12]
        m = tones[pattern[i % 8]]
        n = int(0.24 * SR)
        tt = t_axis(n)
        f = midi(m)
        s = (np.sin(2 * np.pi * f * tt) + 0.35 * saw(f, n) * np.exp(-tt * 40)) * np.exp(-tt * 16)
        s *= 0.06 * (1.0 if i % 2 == 0 else 0.7)
        pan = 0.3 if i % 2 == 0 else 0.7
        place(pl[:, 0], s * (1 - pan), ts)
        place(pl[:, 1], s * pan, ts)
    dly = int(BEAT * 0.75 * SR)
    pp = pl.copy()
    for tap, g in ((1, 0.32), (2, 0.16)):
        sh = dly * tap
        pp[sh:, 0] += pl[:-sh, 1 if tap % 2 else 0] * g
        pp[sh:, 1] += pl[:-sh, 0 if tap % 2 else 1] * g
    out += pp

    # --- drums
    dr = np.zeros(N)
    K, CL, SN = kick(), clap(), snare()
    for bt in range(int(DUR / BEAT) + 1):
        tb = bt * BEAT
        if in_any(tb, GROOVE):
            place(dr, K, tb, 1.0)
            if bt % 2 == 1:
                place(dr, CL, tb, 1.0)
            for q in range(4):
                place(dr, hat(), tb + q * BEAT / 4, 0.9 if q == 2 else 0.5)
            place(dr, hat(True), tb + BEAT / 2, 0.7)
        elif in_any(tb, INTRO):
            place(dr, K, tb, 0.8)
            place(dr, hat(), tb + BEAT / 2, 0.6)
        elif in_any(tb, BREAK):
            place(dr, hat(), tb, 0.5)
    for a, b in FILLS:
        n16 = int((b - a) / (BEAT / 4))
        for i in range(n16):
            place(dr, SN, a + i * BEAT / 4, 0.4 + 0.6 * i / max(1, n16 - 1))
    # muffled intro: the drum and pad bus is lowpassed, the filter opens into the drop
    intro_n = int(C["arrow"] * SR)
    muf = lowpass(dr[:intro_n], 420)
    open_k = np.clip((t[:intro_n] - (C["arrow"] - 1.5)) / 1.5, 0, 1)[:]  # last 1.5 s: open up
    dr[:intro_n] = muf * (1 - open_k) + dr[:intro_n] * open_k
    out += np.stack([dr, dr], 1)

    # --- bass: offbeat 8ths on the root, pumping
    bs = np.zeros(N)
    for i in range(int(DUR / (BEAT / 2))):
        tq = i * BEAT / 2
        if not in_any(tq, GROOVE) or i % 2 == 0:
            continue
        root, _ = chord_at(tq)
        n = int(BEAT * 0.48 * SR)
        tt = t_axis(n)
        f = midi(root + 12)
        s = (np.sin(2 * np.pi * f * tt) * 0.8 + lowpass(saw(f, n), 700) * 0.4) * env(n, 0.004, 0.06, 0.7, 0.05)
        place(bs, s, tq, 0.42)
    out += np.stack([bs, bs], 1)

    # --- risers, impacts, gap before the first drop
    for t_hit, d in ((C["logo"], 2.0), (C["slam"], 1.0)):
        place(out, riser(d), t_hit - d - (0.5 if t_hit == C["logo"] else 0.0), 0.9)
    for t_hit, big in ((C["logo"], True), (C["title3"], False), (C["zero"], True), (C["split"], False), (C["title6"], False), (C["who"], False), (C["steps"], False), (C["slam"], True), (C["lockup"], False), (C["click"], True)):
        place(out, impact(big), t_hit, 0.9 if big else 0.6)
    gap = (t >= C["arrow"]) & (t < C["logo"])  # half a bar of silence before the logo drops
    out[gap] *= 0.05

    # final chord on the click, long tail
    n = int(2.2 * SR)
    fin = np.zeros(n)
    for m in [45, 57, 60, 64, 69, 72]:
        fin += saw(midi(m), n, phase=(m * 0.17) % 1) * 0.03
    fin = lowpass(fin, 3200) * env(n, 0.01, 0.6, 0.5, 1.4)
    place(out, np.stack([fin, fin], 1), C["click"], 1.0)

    out = verb(out, 0.16)
    out *= seg(t, [(0, 1.0), (DUR - 0.6, 1.0), (DUR, 0.0)])[:, None]
    out = np.tanh(out * 1.3) / np.tanh(1.3)
    peak = np.max(np.abs(out))
    return out / peak * 0.89


# ------------------------------------------------------------------ sound effects
SFX_LIB = Path.home() / ".claude/skills/media-use/audio/assets/sfx"


def load(name):
    src = ROOT / "assets/audio/sfx-src" / f"{name}.wav"
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
    return np.stack([s, s], 1) * 0.9


def make_sfx():
    buf = np.zeros((N, 2))
    names = ["whoosh", "whoosh-short", "whoosh-cinematic", "pop", "click", "click-soft", "chime", "sparkle", "ping",
             "key-press", "notification"]
    S = {k: load(k) for k in names}

    def put(name, t0, g=1.0, sl=None):
        s = S[name] if sl is None else S[name][: int(sl * SR)]
        place(buf, s, t0, g)

    def typing(t0, t1, g=0.22):
        k = 0
        t = t0
        while t < t1:
            put("key-press", t, g * (0.8 + 0.2 * (k % 3) / 2))
            t += 0.06 + 0.02 * (k % 3)
            k += 1

    c = C
    # 01 accroche
    for t in (c["l1"], c["l2"], c["l3"], c["l4"]):
        put("pop", t - 0.02, 0.35)
        put("whoosh-short", t - 0.12, 0.22)
    put("whoosh", c["arrow"] - 0.05, 0.5)
    # 02 manoo
    put("sparkle", c["logo"] + 0.05, 0.4)
    for i in range(5):
        put("click-soft", c["word"] + 0.06 * i, 0.18)
    put("pop", c["sub"], 0.3)
    for t in (c["b1"], c["b2"], c["b3"]):
        put("pop", t, 0.38)
    put("whoosh-short", c["out2"], 0.4)
    # 03 ton portfolio
    put("pop", c["title3"] + 0.02, 0.35)
    put("click", c["toggle3"], 0.55)
    put("whoosh", c["toggle3"] + 0.4, 0.4)
    put("whoosh-short", c["phone3"], 0.35)
    place(buf, shutter(), c["shutter"], 1.0)
    put("pop", c["shutter"] + 0.3, 0.3)
    put("whoosh-short", c["sheet"], 0.3)
    typing(c["type3a"], c["type3b"])
    put("click", c["addTap"], 0.5)
    put("chime", c["toast3"], 0.35)
    put("pop", c["cellNew"], 0.4)
    put("click", c["publish"], 0.5)
    put("pop", c["post"], 0.35)
    for i in range(4):
        put("pop", c["likes"] + 0.25 * i, 0.16)
    put("ping", c["comment"], 0.3)
    put("whoosh", c["out3"], 0.5)
    # 04 0 CV
    put("whoosh-cinematic", c["zero"] - 0.1, 0.35, sl=1.2)
    for i in range(6):
        put("whoosh-short", c["zero"] + 0.08 * i, 0.14)
    put("pop", c["terrain"], 0.35)
    put("whoosh", c["out4"], 0.45)
    # 05 avant / après
    put("whoosh-short", c["split"], 0.4)
    for i in range(5):
        put("pop", c["fill"] + 0.15 * i, 0.2)
    put("pop", c["chip5"], 0.35)
    put("pop", c["heart5"], 0.35)
    put("whoosh", c["out5"], 0.45)
    # 06 côté recruteurs
    put("pop", c["title6"] + 0.02, 0.35)
    put("click", c["toggle6"], 0.55)
    put("whoosh", c["toggle6"] + 0.4, 0.4)
    put("whoosh-short", c["phone6"], 0.35)
    typing(c["type6a"], c["type6b"])
    put("pop", c["rennes"], 0.35)
    for i in range(4):
        put("pop", c["results"] + 0.1 * i, 0.2)
    put("click", c["tapCard"], 0.5)
    put("whoosh-short", c["profile6"], 0.3)
    put("click", c["follow"], 0.5)
    put("ping", c["follow"] + 0.08, 0.25)
    put("click", c["write"], 0.45)  # tap on « Message »
    typing(c["type6c"], c["type6d"], 0.18)
    put("click", c["send"], 0.5)
    put("whoosh-short", c["send"] + 0.14, 0.32)  # whip to Jules' phone
    put("notification", c["notif"], 0.6)
    put("whoosh", c["out6"], 0.45)
    # 07 pour qui
    put("pop", c["who"], 0.3)
    for t in (c["w1"], c["w2"], c["w3"], c["w4"]):
        put("pop", t, 0.38)
    put("sparkle", c["allTrades"], 0.3)
    put("whoosh", c["out7"], 0.45)
    # 08 3 étapes
    put("pop", c["steps"], 0.3)
    for s_, ck in ((c["s1"], c["c1"]), (c["s2"], c["c2"]), (c["s3"], c["c3"])):
        put("pop", s_, 0.35)
        put("ping", ck, 0.3)
    put("whoosh", c["out8"], 0.45)
    # 09 tu montres / on te repère
    put("pop", c["montres"] + 0.02, 0.4)
    put("whoosh-cinematic", c["slam"] - 0.2, 0.4, sl=1.4)
    put("whoosh", c["out9"], 0.45)
    # 10 manoo.fr
    put("whoosh-cinematic", c["fin"], 0.35, sl=1.6)
    for i in range(4):
        put("whoosh-short", c["fin"] + 0.25 * i, 0.16)
    put("sparkle", c["lockup"] + 0.05, 0.35)
    put("pop", c["pill"], 0.35)
    put("click", c["click"], 0.6)
    put("chime", c["click"] + 0.04, 0.4)
    put("pop", c["tagline"], 0.25)
    put("pop", c["cta"], 0.3)
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
    write(ROOT / "assets/audio/music/track.wav", make_track())
    write(ROOT / "assets/audio/sfx/sfx-track.wav", make_sfx())
    print("ok")

#!/usr/bin/env python3
"""Score + sound design for the Manoo LinkedIn / Instagram ad (deterministic, numpy/scipy only).

Outputs
  assets/audio/music/track.wav    ~98 BPM score: A minor while the problem is told, the groove stops on
                                  « Pourtant », builds on the three verbs, falls silent on « Voici » and lands
                                  in C major on « Manoo ». Ducked under the voice (sidechain: assets/audio/vo/vo.wav).
  assets/audio/sfx/sfx-track.wav  every sound effect, placed on the animation cues

Every time comes from assets/cues.js (the voice take's word timings). After a new take:
  python3 tools/vo-build.py && python3 tools/make-audio.py
The bar grid is fitted so both logo hits (« Voici Manoo », « Manoo. Le savoir-faire… ») land on a downbeat.
SFX samples: the media-use bundled library (see its CREDITS.md), decoded on first run into
assets/audio/sfx-src/ (not versioned).
"""
import json
import re
import subprocess
import unicodedata
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
ROOT = Path(__file__).resolve().parent.parent
rng = np.random.default_rng(23)
MUSIC_LUFS = -26.5  # integrated, after ducking (the voice sits at -16)
SFX_LUFS = -25.0

# ------------------------------------------------------------------ cues
VO = json.loads(re.search(r"window\.VO = (\{.*\});", (ROOT / "assets/cues.js").read_text()).group(1))
END = VO["end"]
SC = VO["scenes"]
LINES = {l["id"]: l for l in VO["lines"]}
N = int(SR * END)


def _f(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()))


def W(line, word, n=0):
    return [t for w, t in LINES[line]["words"] if _f(w) == _f(word)][n]


def LS(line):
    return LINES[line]["start"]


def LE(line):
    return LINES[line]["end"]


def S0(scene):
    return SC[scene][0]


def S1(scene):
    return SC[scene][0] + SC[scene][1]


# bar grid: a whole number of bars between the two logo hits
HIT1, HIT2 = W(9, "Manoo"), W(18, "Manoo")
NB = max(4, round((HIT2 - HIT1) / 2.44))
BAR = (HIT2 - HIT1) / NB
BEAT = BAR / 4
K1 = int(HIT1 // BAR)  # bar index of the first hit
GRID0 = HIT1 - K1 * BAR  # first downbeat
K2 = K1 + NB


def bar_t(b):
    return GRID0 + b * BAR


T_TICKS = S0("question")  # a clock starts ticking under the question
T_DRUMS = S0("classiques")  # a dry half-time beat under the list of limits
T_BREAK = LS(7) - 0.12  # « Pourtant » : everything stops but the pad
T_BUILD = bar_t(K1 - 2)  # the build into the reveal
T_GAP = W(9, "Voici") - 0.08  # silence on « Voici »
T_BELLS = S0("communaute")
T_DOWN = bar_t(K2 - 2)  # breakdown under the nuance
T_GAP2 = HIT2 - 0.18
T_BUTTON = min(bar_t(K2 + 2), END - 1.6)  # final chord, once the call to action is said

CH = {
    "Am": (45, [57, 60, 64, 69]),
    "F": (41, [53, 57, 60, 64]),  # Fmaj7, close voicing
    "Dm": (38, [53, 57, 62, 65]),
    "E": (40, [56, 59, 64, 68]),
    "G": (43, [55, 59, 62, 67]),
    "Gsus": (43, [55, 60, 62, 67]),
    "C": (48, [55, 60, 64, 67]),
    "Dm7": (38, [53, 57, 60, 62]),
    "Cadd9": (48, [55, 60, 62, 64, 67, 72]),
}


def chord_plan():
    ev = [(0.0, "Am")]
    prob = ["Am", "F", "Am", "F", "Dm", "Am", "E"]
    ev += [(bar_t(b), prob[b % len(prob)]) for b in range(0, K1 - 2)]
    ev += [(bar_t(K1 - 2), "F"), (bar_t(K1 - 1), "G")]
    ev += [(bar_t(b), ["C", "G", "Am", "F"][(b - K1) % 4]) for b in range(K1, K2 - 2)]
    ev += [(bar_t(K2 - 2), "Dm7"), (bar_t(K2 - 1), "Gsus"), (bar_t(K2 - 1) + 2 * BEAT, "G")]
    ev += [(bar_t(K2), "C"), (bar_t(K2 + 1), "F"), (bar_t(K2 + 1) + 2 * BEAT, "G")]
    ev = [e for e in sorted(ev) if e[0] < T_BUTTON - 1e-6] + [(T_BUTTON, "Cadd9")]
    out = []
    for t, c in ev:
        if out and abs(out[-1][0] - t) < 1e-6:
            out[-1] = (t, c)
        else:
            out.append((t, c))
    return [(t, out[i + 1][0] if i + 1 < len(out) else END + 2.0, c) for i, (t, c) in enumerate(out)]


PLAN = chord_plan()


def chord_at(t):
    for a, b, c in PLAN:
        if a <= t < b:
            return CH[c]
    return CH[PLAN[-1][2]]


# ------------------------------------------------------------------ dsp helpers
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


def place2(buf, sig, t0, gain=1.0, pan=0.5):
    place(buf[:, 0], sig * (1 - pan) * 2 * gain, t0)
    place(buf[:, 1], sig * pan * 2 * gain, t0)


def seg(t, keys):
    return np.interp(t, [k[0] for k in keys], [k[1] for k in keys])


def st2(fn, x):
    return np.stack([fn(x[:, 0]), fn(x[:, 1])], 1)


def reverb_ir(seconds=2.4, decay=3.0, seed=7):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    e = np.exp(-decay * t_axis(n))
    ir = [lowpass(r.standard_normal(n) * e, 6500) for _ in range(2)]
    for x in ir:
        x[:240] *= np.linspace(0, 1, 240)
    return [x / np.abs(x).sum() * 16 for x in ir]


IR = reverb_ir()


def verb(st, wet):
    wl = fftconvolve(st[:, 0], IR[0])[: len(st)]
    wr = fftconvolve(st[:, 1], IR[1])[: len(st)]
    return st * (1 - wet) + np.stack([wl, wr], 1) * wet


def lufs(st):
    """Integrated loudness (BS.1770, gated) measured by ffmpeg's ebur128."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "pipe:0",
                        "-af", "ebur128", "-f", "null", "-"], input=st.astype(np.float32).tobytes(), capture_output=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr.decode())[-1])


# ------------------------------------------------------------------ instruments
def pluck(f, n, bright=1.0, decay=16.0):
    tt = t_axis(n)
    return (np.sin(2 * np.pi * f * tt) + 0.35 * bright * saw(f, n) * np.exp(-tt * 40)) * np.exp(-tt * decay)


def piano(m, dur=2.4, vel=1.0):
    f, n = midi(m), int(dur * SR)
    tt = t_axis(n)
    s = np.zeros(n)
    for k, (a, d) in enumerate([(1.0, 1.8), (0.42, 3.2), (0.2, 4.8), (0.09, 6.5), (0.04, 9.0)], start=1):
        s += a * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * tt + 0.7 * k) * np.exp(-tt * d)
    s *= np.minimum(1, tt / 0.005)
    s += lowpass(rng.standard_normal(n), 900) * np.exp(-tt * 70) * 0.04  # felt hammer
    s *= np.minimum(1, (dur - tt) / 0.05)
    return lowpass(s, 4200) * vel * 0.22


def bell(m, dur=1.8, vel=1.0):
    f, n = midi(m), int(dur * SR)
    tt = t_axis(n)
    s = (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 2.6) + 0.5 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 4.5)
         + 0.22 * np.sin(2 * np.pi * f * 3.01 * tt) * np.exp(-tt * 8) + 0.1 * np.sin(2 * np.pi * f * 4.17 * tt) * np.exp(-tt * 12))
    return s * np.minimum(1, tt / 0.003) * vel * 0.2


def kick(level=1.0):
    n = int(0.42 * SR)
    tt = t_axis(n)
    s = np.sin(2 * np.pi * np.cumsum(46 + 110 * np.exp(-tt * 30)) / SR) * np.exp(-tt * 8)
    s += highpass(rng.standard_normal(n), 2500) * np.exp(-tt * 320) * 0.08
    return np.tanh(s * 1.4) * 0.58 * level


def clap():
    n = int(0.22 * SR)
    s = bandpass(rng.standard_normal(n), 900, 3400)
    e = np.exp(-t_axis(n) * 20)
    for d in (0.009, 0.018, 0.027):
        sh = int(d * SR)
        e[sh:] = np.maximum(e[sh:], np.exp(-t_axis(n - sh) * 17))
    return s * e * 0.16


def rim():
    n = int(0.08 * SR)
    tt = t_axis(n)
    return bandpass(rng.standard_normal(n), 1500, 4500) * np.exp(-tt * 90) * 0.22 + np.sin(2 * np.pi * 820 * tt) * np.exp(-tt * 110) * 0.1


def snare():
    n = int(0.16 * SR)
    tt = t_axis(n)
    return bandpass(rng.standard_normal(n), 1200, 6000) * np.exp(-tt * 26) * 0.11 + np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 30) * 0.07


def hat(open_=False):
    n = int((0.24 if open_ else 0.045) * SR)
    return highpass(rng.standard_normal(n), 7500) * np.exp(-t_axis(n) * (12 if open_ else 80)) * (0.075 if open_ else 0.06)


def shaker():
    n = int(0.09 * SR)
    tt = t_axis(n)
    return highpass(rng.standard_normal(n), 5500) * np.minimum(1, tt / 0.012) * np.exp(-tt * 45) * 0.055


def bass_note(m, dur):
    n = int(dur * SR)
    tt = t_axis(n)
    f = midi(m)
    return (np.sin(2 * np.pi * f * tt) * 0.8 + lowpass(saw(f, n), 650) * 0.35) * env(n, 0.005, 0.08, 0.7, 0.06)


def sub_pulse(m):
    n = int(0.45 * SR)
    tt = t_axis(n)
    return np.sin(2 * np.pi * midi(m) * tt) * np.exp(-tt * 6) * np.minimum(1, tt / 0.004) * 0.5


def impact(big=True):
    n = int((2.8 if big else 1.4) * SR)
    tt = t_axis(n)
    boom = np.sin(2 * np.pi * np.cumsum(36 + 72 * np.exp(-tt * 9)) / SR) * np.exp(-tt * (2.0 if big else 4))
    crash = highpass(rng.standard_normal(n), 4800) * np.exp(-tt * (1.5 if big else 3)) * 0.13
    s = boom * (0.55 if big else 0.32) + crash
    return np.stack([s, s * 0.96], 1)


def riser(dur):
    n = int(dur * SR)
    tt = t_axis(n)
    k = (tt / dur) ** 2
    s = highpass(rng.standard_normal(n), 1500) * k * 0.12 + np.sin(2 * np.pi * (220 * tt + 880 * tt ** 2 / dur)) * k * 0.035
    s *= np.minimum(1, (dur - tt) / 0.02)
    return np.stack([s, s], 1)


def swell(dur):
    """Reversed cymbal: sucks the air in to the next downbeat."""
    n = int(dur * SR)
    tt = t_axis(n)
    s = lowpass(highpass(rng.standard_normal(n), 2500), 9000) * (tt / dur) ** 3 * 0.28
    s *= np.minimum(1, (dur - tt) / 0.006)
    return np.stack([s, s * 0.94], 1)


def crash():
    n = int(2.4 * SR)
    tt = t_axis(n)
    s = highpass(rng.standard_normal(n), 5200) * np.exp(-tt * 1.6) * 0.1
    return np.stack([s, s * 0.93], 1)


# ------------------------------------------------------------------ the score
def make_track():
    t = t_axis(N)
    bed = np.zeros((N, 2))  # ducked under the voice
    fx = np.zeros((N, 2))  # hits, risers, the button: never ducked
    ph = ((t - GRID0) % BEAT) / BEAT
    grooving = ((t >= HIT1) & (t < T_DOWN)) | ((t >= HIT2) & (t < T_BUTTON))
    pump = 1 - grooving * 0.3 * np.exp(-ph * 6)

    # --- pad: dark while the problem is told, opening up into the reveal
    raw = np.zeros((N, 2))
    for a, b, name in PLAN:
        if name == "Cadd9":
            continue
        _, notes = CH[name]
        n = int((b - a + 0.6) * SR)
        e = env(n, 0.2, 0.4, 0.85, 0.6)
        for k, m in enumerate(notes):
            for d, pan in ((-0.08, 0.2), (0.0, 0.5), (0.09, 0.8)):
                place2(raw, saw(midi(m) * 2 ** (d / 12), n, phase=(k * 0.31 + d) % 1.0) * e * 0.015, a, pan=pan)
    dark = st2(lambda x: lowpass(x, 1100, 2), raw)
    bright = st2(lambda x: lowpass(x, 2900, 4), raw)
    w = seg(t, [(0, 0.2), (T_BREAK, 0.25), (T_BREAK + 0.4, 0.4), (T_BUILD, 0.45), (T_GAP, 0.8), (HIT1, 0.85), (T_DOWN, 0.85), (T_DOWN + 0.6, 0.6),
                (T_GAP2, 0.7), (HIT2, 1.0), (END, 1.0)])[:, None]
    g = seg(t, [(0, 0.0), (0.35, 2.2), (T_BREAK - 0.05, 2.2), (T_BREAK + 0.3, 2.6), (T_BUILD, 2.4), (T_GAP - 0.03, 1.4), (T_GAP, 0.0),
                (HIT1 - 0.001, 0.0), (HIT1, 0.75), (T_DOWN, 0.75), (T_DOWN + 0.4, 1.5), (T_GAP2 - 0.03, 1.5), (T_GAP2, 0.0),
                (HIT2 - 0.001, 0.0), (HIT2, 0.8), (T_BUTTON - 0.02, 0.8), (T_BUTTON, 0.0)])
    bed += (dark * (1 - w) + bright * w) * (g * pump)[:, None]

    # --- the problem: a muted ostinato (8ths), a heartbeat, then a clock and a dry half-time beat
    step = BEAT / 2
    pu = np.zeros((N, 2))
    i = 0
    while GRID0 + i * step < T_BREAK - 0.05:
        ts = GRID0 + i * step
        root, _ = chord_at(ts + 1e-4)
        m = [root + 12, root + 19, root + 24, root + 19][i % 4]
        place2(pu, pluck(midi(m), int(0.36 * SR), bright=0.6, decay=14), ts, 0.16 if i % 2 == 0 else 0.11, 0.42 if i % 2 == 0 else 0.58)
        i += 1
    bed += st2(lambda x: lowpass(x, 2400), pu)
    first_kick = GRID0 + np.ceil((T_DRUMS - GRID0) / (2 * BEAT)) * 2 * BEAT  # beats 1 and 3
    dr = np.zeros(N)
    K, KS, CL, RM, SN = kick(), kick(0.75), clap(), rim(), snare()
    for bt in range(int((END - GRID0) / BEAT) + 1):
        tb = GRID0 + bt * BEAT
        if tb >= T_BREAK - 0.05:
            break
        if bt % 2 == 0 and tb < first_kick - 1e-3:
            place(dr, sub_pulse(chord_at(tb + 1e-4)[0]), tb, 0.45)
        if tb >= first_kick - 1e-3:
            if bt % 2 == 0:
                place(dr, KS, tb)
            else:
                place(dr, RM, tb, 0.9)
        if tb >= T_TICKS:
            place(dr, hat(), tb, 0.8)
            place(dr, hat(), tb + BEAT / 2, 0.45)
    # --- the build (bar K1-2: 8ths, bar K1-1: 16ths, a snare roll into the silence)
    ar = np.zeros((N, 2))
    for b in (K1 - 2, K1 - 1):
        sub = 2 if b == K1 - 2 else 4
        for j in range(4 * sub):
            ts = bar_t(b) + j * BEAT / sub
            if ts >= T_GAP - 0.02:
                break
            _, notes = chord_at(ts + 1e-4)
            m = (notes + [x + 12 for x in notes])[j % 8]
            place2(ar, pluck(midi(m), int(0.26 * SR), bright=0.8), ts, 0.045 + 0.02 * (j / (4 * sub)), 0.3 if j % 2 else 0.7)
            place(dr, shaker(), ts, 0.8)
        for q in range(4):
            tb = bar_t(b) + q * BEAT
            if tb < T_GAP - 0.02 and (b == K1 - 1 or q % 2 == 0):
                place(dr, K, tb, 0.85)
    roll0 = bar_t(K1 - 1) + 2 * BEAT
    nroll = int((T_GAP - 0.02 - roll0) / (BEAT / 4))
    for j in range(max(0, nroll)):
        place(dr, SN, roll0 + j * BEAT / 4, 0.3 + 0.7 * j / max(1, nroll - 1))

    # --- the groove: from « Manoo » to the nuance, then again under the signature
    bs = np.zeros(N)
    bells = np.zeros((N, 2))
    for bt in range(int((END - GRID0) / BEAT) + 1):
        tb = GRID0 + bt * BEAT
        if not ((HIT1 - 1e-3 <= tb < T_DOWN - 1e-3) or (HIT2 - 1e-3 <= tb < T_BUTTON - 1e-3)):
            continue
        q = bt % 4
        place(dr, K, tb)
        if q in (1, 3):
            place(dr, CL, tb)
        for s16 in range(4):
            place(dr, shaker(), tb + s16 * BEAT / 4, 1.0 if s16 == 2 else 0.55)
        if tb >= HIT1 + BAR - 1e-3:
            place(dr, hat(True), tb + BEAT / 2, 0.75)
        root, notes = chord_at(tb + 1e-4)
        for e8 in range(2):
            m = root + (12 if (q * 2 + e8) % 4 == 2 else 0)
            place(bs, bass_note(m, BEAT * 0.46), tb + e8 * BEAT / 2, 0.36)
        if tb >= T_BELLS - 1e-3:
            m = notes[[3, 2, 1, 2][q]] + 12
            place2(bells, bell(m, 1.4, 0.9 if q == 0 else 0.6), tb, 1.0, 0.35 if q % 2 else 0.65)
        for s16 in range(4):
            ts = tb + s16 * BEAT / 4
            m = notes[[0, 2, 1, 3, 2, 1, 3, 2][(q * 4 + s16) % 8]] + 12
            place2(ar, pluck(midi(m), int(0.24 * SR)), ts, 0.032 if s16 % 2 == 0 else 0.022, 0.3 if s16 % 2 == 0 else 0.7)
    dly = int(BEAT * 0.75 * SR)
    pp = ar.copy()
    for tap, gn in ((1, 0.3), (2, 0.15)):
        sh = dly * tap
        pp[sh:, 0] += ar[:-sh, 1 if tap % 2 else 0] * gn
        pp[sh:, 1] += ar[:-sh, 0 if tap % 2 else 1] * gn
    bed += pp + bells * 0.8
    bed += np.stack([bs * pump, bs * pump], 1)

    # --- breakdown under the nuance: felt piano, a held bass, a shaker coming back
    pn = np.zeros((N, 2))
    for b in (K2 - 2, K2 - 1):
        a = bar_t(b)
        root, notes = chord_at(a + 1e-4)
        for k, m in enumerate(notes):
            place2(pn, piano(m, 2.6, 1.4), a + 0.012 * k, 1.0, 0.35 + 0.1 * k)
        for q in (1, 2, 3):
            place2(pn, piano(notes[[1, 2, 3][q - 1]] + 12, 1.6, 0.8), a + q * BEAT, 1.0, 0.6)
        place2(bed, bass_note(root, BAR * 0.92), a, 0.12, 0.5)
        if b == K2 - 1:
            for j in range(8):
                ts = a + j * BEAT / 2
                if ts < T_GAP2 - 0.02:
                    place(dr, shaker(), ts, 0.3 + 0.5 * j / 7)
    # piano chords lift the final bars too
    for b in (K2, K2 + 1):
        a = bar_t(b)
        if a < T_BUTTON - 0.1:
            for k, m in enumerate(chord_at(a + 1e-4)[1]):
                place2(pn, piano(m, 2.4, 0.5), a + 0.01 * k, 1.0, 0.4 + 0.08 * k)
    bed += pn
    bed += np.stack([dr, dr], 1)

    # --- fx: an anchor on the first frame, the burst, the three verbs, risers, swells and hits
    place(fx, impact(False), 0.0, 0.45)
    place(fx, impact(False), W(7, "tiennent") - 0.06, 0.35)
    for word, (hi, lo) in (("voient", (69, 65)), ("partagent", (72, 69)), ("démontrent", (74, 71))):
        tw = W(8, word)
        for m, v in ((hi, 1.0), (lo, 0.6), (hi - 12, 0.5)):
            place2(fx, bell(m, 2.0, v), tw, 1.0, 0.5)
            place2(fx, pluck(midi(m), int(0.4 * SR), bright=0.6, decay=9), tw, 0.05 * v, 0.5)
    place(fx, riser(T_GAP - bar_t(K1 - 1)), bar_t(K1 - 1), 0.85)
    place(fx, swell(0.42), HIT1 - 0.42, 0.9)
    place(fx, impact(True), HIT1, 0.95)
    place(fx, crash(), HIT1, 0.8)
    r2 = bar_t(K2 - 1) + BEAT
    place(fx, riser(T_GAP2 - r2), r2, 0.7)
    place(fx, swell(0.34), HIT2 - 0.34, 0.85)
    place(fx, impact(True), HIT2, 0.9)
    place(fx, crash(), HIT2, 0.7)
    # the button: one long C add9, struck after « manoo.fr »
    n = int((END - T_BUTTON + 0.1) * SR)
    fin = np.zeros((n, 2))
    for k, m in enumerate(CH["Cadd9"][1]):
        for d, pan in ((-0.07, 0.25), (0.08, 0.75)):
            place2(fin, saw(midi(m) * 2 ** (d / 12), n, phase=(m * 0.17 + d) % 1) * 0.012, 0.0, pan=pan)
        place2(fin, piano(m, END - T_BUTTON + 0.1, 0.75), 0.008 * k, 1.0, 0.3 + 0.07 * k)
    fin = st2(lambda x: lowpass(x, 3000, 4), fin) * env(n, 0.01, 0.5, 0.6, 1.2)[:, None]
    sp = np.pad(sub_pulse(36), (0, max(0, n - int(0.45 * SR))))[:n] * 0.8
    fin += np.stack([sp, sp], 1)
    place(fx, fin, T_BUTTON, 1.0)
    place(fx, impact(False), T_BUTTON, 0.55)
    place(fx, crash(), T_BUTTON, 0.6)

    # --- ducking: the bed steps back 7 dB while the voice speaks (60 ms look-ahead, 350 ms release)
    bed = verb(bed, 0.14) * duck_curve(t, 7.0)[:, None]
    out = bed + verb(fx, 0.22)
    out *= seg(t, [(0, 0.0), (0.01, 1.0), (END - 0.5, 1.0), (END, 0.0)])[:, None]
    out = np.tanh(out * 1.2) / np.tanh(1.2)
    return out


def duck_curve(t, depth_db):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / "assets/audio/vo/vo.wav"), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True, check=True)
    v = np.frombuffer(p.stdout, dtype=np.float32).astype(np.float64)
    hop = SR // 100
    nh = len(v) // hop
    rms = np.sqrt(np.mean(v[: nh * hop].reshape(nh, hop) ** 2, 1) + 1e-12)
    act = (20 * np.log10(rms) > -45).astype(float)
    act = np.concatenate([act[6:], np.zeros(6)])  # look-ahead
    sm = np.zeros(nh)
    a_att, a_rel = np.exp(-1 / 5.0), np.exp(-1 / 35.0)
    y = 0.0
    for i, x in enumerate(act):
        y = (a_att if x > y else a_rel) * y + (1 - (a_att if x > y else a_rel)) * x
        sm[i] = y
    gain_db = -depth_db * sm
    return 10 ** (np.interp(t, (np.arange(nh) + 0.5) * hop / SR, gain_db) / 20)


# ------------------------------------------------------------------ sound effects
SFX_LIB = Path.home() / ".claude/skills/media-use/audio/assets/sfx"
TRIM = {"sparkle": 0.25, "whoosh-cinematic": 0.3}  # these two are mastered ~12 dB hotter than the rest of the library


def load(name):
    src = ROOT / "assets/audio/sfx-src" / f"{name}.wav"
    if not src.exists():
        src.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(SFX_LIB / f"{name}.mp3"), "-ar", str(SR), "-ac", "2", str(src)], check=True)
    with wave.open(str(src), "rb") as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
        return a.reshape(-1, w.getnchannels()) * TRIM.get(name, 1.0)


def pitched(a, st):
    r = 2 ** (st / 12)
    x = np.arange(int(len(a) / r)) * r
    return np.stack([np.interp(x, np.arange(len(a)), a[:, k]) for k in range(a.shape[1])], 1)


def shutter():
    n = int(0.35 * SR)
    s = np.zeros(n)
    for d, g in ((0.0, 1.0), (0.055, 0.8)):
        k = int(0.018 * SR)
        place(s, bandpass(rng.standard_normal(k), 1800, 7000) * np.exp(-t_axis(k) * 260), d, g)
        place(s, np.sin(2 * np.pi * 180 * t_axis(k)) * np.exp(-t_axis(k) * 200) * 0.6, d, g)
    return np.stack([s, s], 1) * 0.9


def stamp():
    n = int(0.3 * SR)
    tt = t_axis(n)
    thump = np.sin(2 * np.pi * np.cumsum(70 + 90 * np.exp(-tt * 40)) / SR) * np.exp(-tt * 22) * 0.9
    slap = bandpass(rng.standard_normal(n), 400, 2500) * np.exp(-tt * 70) * 0.5
    s = np.tanh((thump + slap) * 1.2) * 0.8
    return np.stack([s, s], 1)


def rec_beep():
    n = int(0.25 * SR)
    s = np.zeros(n)
    k = int(0.06 * SR)
    tk = t_axis(k)
    b = np.sin(2 * np.pi * 1320 * tk) * np.minimum(1, tk / 0.004) * np.minimum(1, (0.06 - tk) / 0.006) * 0.35
    place(s, b, 0.0)
    place(s, b, 0.12, 0.8)
    return np.stack([s, s], 1)


def shimmer(dur):
    n = int(dur * SR)
    tt = t_axis(n)
    e = np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 2
    noise = rng.standard_normal(n)
    k = tt / dur
    s = (bandpass(noise, 2500, 5000) * (1 - k) + bandpass(noise, 5000, 11000) * k) * e * 0.08
    s += sum(np.sin(2 * np.pi * f * tt) for f in (2093, 2637, 3136, 4186)) * e * 0.012
    return np.stack([s, s * 0.9], 1)


def make_sfx():
    buf = np.zeros((N, 2))
    names = ["whoosh", "whoosh-short", "whoosh-cinematic", "pop", "click", "click-soft", "chime", "sparkle", "ping",
             "key-press", "notification"]
    S = {k: load(k) for k in names}
    POP = [pitched(S["pop"], st) for st in (0, 2, 4, 7, 9, 12, 14, 16)]  # a rising major pentatonic

    def put(name, t0, g=1.0, sl=None):
        s = S[name] if sl is None else S[name][: int(sl * SR)]
        place(buf, s, t0, g)

    def pops(times, g, start=0):
        for i, t0 in enumerate(times):
            place(buf, POP[min(len(POP) - 1, start + i)], t0, g)

    # 01 accroche — the phone, then the CV and the photos squeezed into one line
    put("whoosh-short", 0.0, 0.35)
    put("whoosh", W(2, "Et") - 0.22, 0.3)
    put("whoosh-short", W(2, "Et"), 0.28)
    put("whoosh-short", W(2, "Une") - 0.2, 0.25)
    pops([W(2, "Une") - 0.14 + i * 0.05 for i in range(6)], 0.16)
    put("whoosh-short", W(2, "ligne") - 0.06, 0.2, sl=0.35)
    put("pop", W(2, "ligne"), 0.3)
    # 02 question — the trades gather, the question is typed
    put("whoosh", S0("question") - 0.02, 0.3)
    for word, tw in LINES[3]["words"]:
        for k in range(min(4, max(1, len(word) // 3))):
            put("key-press", tw - 0.03 + k * 0.05, 0.2 * (0.85 + 0.15 * (k % 2)))
    put("pop", W(3, "avant"), 0.3)
    put("whoosh-short", S1("question") - 0.3, 0.35)
    # 03 classiques — a carousel of the usual ways, each stamped with its limit
    put("whoosh-short", S0("classiques") + 0.08, 0.35)
    place(buf, stamp(), W(4, "bureaux"), 0.5)
    put("whoosh", LS(5) - 0.2, 0.38)
    place(buf, stamp(), W(5, "CV"), 0.5)
    put("pop", W(5, "CV") + 0.02, 0.2)
    put("whoosh", LS(6) - 0.2, 0.38)
    place(buf, stamp(), W(6, "ponctuel"), 0.5)
    put("whoosh-short", S1("classiques") - 0.32, 0.35)
    # 04 pivot — the work bursts out of the CV, three verbs
    put("whoosh-short", S0("pivot") + 0.12, 0.3)
    put("whoosh-cinematic", W(7, "tiennent") - 0.12, 0.3, sl=1.2)
    pops([W(7, "tiennent") - 0.06 + i * 0.04 for i in range(6)], 0.15)
    put("click-soft", W(7, "CV"), 0.3)
    put("click-soft", W(7, "CV") + 0.1, 0.25)
    put("whoosh", LE(7) + 0.04, 0.32)
    pops([W(8, "voient"), W(8, "partagent"), W(8, "démontrent")], 0.28, start=2)
    put("whoosh-short", S1("pivot") - 0.28, 0.3)
    # 05 revelation — « Voici », the logo
    put("whoosh-cinematic", W(9, "Voici") - 0.1, 0.32, sl=0.9)
    put("sparkle", HIT1 + 0.1, 0.4)
    for i in range(5):
        put("click-soft", HIT1 + 0.16 + 0.045 * i, 0.12)
    put("whoosh", S0("demo") - 0.45, 0.24)
    # 06 demo — the job done, the photo, the post, the portfolio
    put("whoosh-short", S0("demo") + 0.02, 0.28)
    place(buf, shutter(), W(10, "Photos") - 0.02, 0.9)
    place(buf, rec_beep(), W(10, "vidéos") - 0.04, 0.4)
    put("whoosh", W(10, "publies") - 0.42, 0.3)
    put("click", W(10, "publies") + 0.14, 0.55)
    put("whoosh-short", LS(11) - 0.1, 0.28)
    put("chime", LS(11) + 0.02, 0.32)
    put("pop", LS(11) + 0.2, 0.38)
    pops([W(11, "devient") - 0.1 + i * 0.12 for i in range(4)], 0.28)
    put("sparkle", W(11, "vitrine") - 0.04, 0.35)
    put("whoosh-short", S1("demo") - 0.26, 0.3)
    # 07 communaute — the network forms, a question, answers, a tip
    put("pop", S0("communaute") + 0.08, 0.32)
    pops([S0("communaute") + 0.25 + i * 0.09 for i in range(8)], 0.14)
    put("sparkle", W(12, "communauté") - 0.1, 0.32)
    put("ping", W(12, "communauté") + 0.6, 0.25)
    put("whoosh-short", LE(12) + 0.06, 0.28)
    put("whoosh-short", LS(13) - 0.12, 0.22)
    put("pop", LS(13) - 0.06, 0.25)
    pops([W(13, "pros") - 0.04, W(13, "répondent") - 0.04], 0.32, start=3)
    put("whoosh-short", min(LE(13) + 0.06, LS(14) - 0.34), 0.28)
    put("whoosh-short", LS(14) - 0.04, 0.22)
    put("pop", W(14, "astuces"), 0.35)
    put("click", W(14, "terrain"), 0.42)
    put("whoosh-short", S1("communaute") - 0.26, 0.3)
    # 08 entreprises — the company, its posts, the map, the like, the message
    put("whoosh-short", W(15, "entreprises") - 0.1, 0.3)
    pops([W(15, w) - 0.08 for w in ("chantiers", "équipes", "coulisses")], 0.32, start=1)
    put("whoosh", W(15, "près") - 0.14, 0.32)
    put("pop", W(15, "près") + 0.08, 0.42)
    put("ping", W(15, "près") + 0.12, 0.22)
    put("whoosh", LS(16) - 0.22, 0.32)
    put("pop", W(16, "plaît") - 0.06, 0.42)
    put("sparkle", W(16, "plaît"), 0.18)
    put("whoosh-short", W(16, "Elles") - 0.1, 0.22)
    put("notification", W(16, "Elles"), 0.36)
    put("whoosh-short", S1("entreprises") - 0.26, 0.3)
    # 09 nuance — the CV kept, the portfolio slides out
    put("whoosh-short", S0("nuance") + 0.08, 0.28)
    put("ping", W(17, "CV") - 0.02, 0.3)
    put("click", W(17, "CV"), 0.25)
    put("whoosh", W(17, "Il") - 0.2, 0.36)
    put("pop", W(17, "Il") + 0.2, 0.38)
    pops([W(17, "montre") + i * 0.09 for i in range(4)], 0.18, start=2)
    for i in range(4):
        put("click-soft", W(17, "dit") - 0.1 + i * 0.07, 0.16)
    put("whoosh-cinematic", S0("fin") - 0.4, 0.3, sl=1.0)
    # 10 fin — the lockup, the beam on the signature, the address
    put("sparkle", HIT2 - 0.1, 0.4)
    for i in range(5):
        put("click-soft", HIT2 - 0.04 + 0.045 * i, 0.12)
    for a, b in ((W(18, "Le"), W(18, "savoir-faire")), (W(18, "enfin"), W(18, "visible"))):
        place(buf, shimmer(max(0.35, b - a + 0.25)), a - 0.06, 0.8)
    put("pop", W(19, "manoo.fr"), 0.4)
    put("chime", W(19, "manoo.fr") + 0.3, 0.28)
    return buf


def write(path, a):
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def to_lufs(a, target, ceiling=0.89):
    g = 10 ** ((target - lufs(a)) / 20)
    a = a * g
    peak = np.max(np.abs(a))
    return a * (ceiling / peak) if peak > ceiling else a


if __name__ == "__main__":
    print(f"grid: {60 / BEAT:.2f} BPM, first downbeat {GRID0:.3f} s, hits on bars {K1} and {K2}, button {T_BUTTON:.2f} s")
    music = to_lufs(make_track(), MUSIC_LUFS)
    sfx = to_lufs(make_sfx(), SFX_LUFS, 0.95)
    write(ROOT / "assets/audio/music/track.wav", music)
    write(ROOT / "assets/audio/sfx/sfx-track.wav", sfx)
    print(f"music {lufs(music):.1f} LUFS, sfx {lufs(sfx):.1f} LUFS")

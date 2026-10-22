#!/usr/bin/env python3
"""Sound effects for the Instagram film, placed on the beats of assets/cues.js.

  python3 tools/make-sfx.py        # → assets/audio/sfx.wav (48 kHz stereo, true peak about -1.5 dBFS)

The reference ad is silent: these effects stay light (air on the moves, UI ticks, one shutter, one chime) so the
film plays with sound on, and the same render without its audio track is the silent cut. Samples come from the
media-use library (Pixabay licence), decoded once into assets/audio/sfx-src/; the shutter is synthesised here.
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
LIB = Path.home() / ".claude/skills/media-use/audio/assets/sfx"
rng = np.random.default_rng(7)

src = (ROOT / "assets/cues.js").read_text()
T = json.loads(re.sub(r"//[^\n]*", "", re.search(r"window\.T = (\{.*?\});", src, flags=re.S).group(1)))
N = int(round(T["END"] * SR))


# ------------------------------------------------------------------ samples
def load(name):
    """Stereo float samples, scaled so their loudest 50 ms sit at -14 dBFS RMS (the library's levels vary by 20 dB)."""
    cache = ROOT / "assets/audio/sfx-src" / f"{name}.wav"
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(LIB / f"{name}.mp3"), "-ar", str(SR), "-ac", "2", str(cache)], check=True)
    with wave.open(str(cache), "rb") as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64).reshape(-1, 2) / 32768.0
    hop = SR // 20
    n = max(1, len(a) // hop)
    rms = np.sqrt(np.mean(a[: n * hop].reshape(n, hop, 2) ** 2, axis=(1, 2)) + 1e-12)
    return a * (10 ** (-14 / 20) / rms.max())


def peak_time(a):
    hop = SR // 100
    n = max(1, len(a) // hop)
    return (np.argmax(np.mean(a[: n * hop].reshape(n, hop, 2) ** 2, axis=(1, 2))) + 0.5) * hop / SR


def pitched(a, semitones):
    r = 2 ** (semitones / 12)
    x = np.arange(int(len(a) / r)) * r
    return np.stack([np.interp(x, np.arange(len(a)), a[:, k]) for k in range(2)], 1)


def fade(a, fin=0.0, fout=0.0):
    a = a.copy()
    if fin > 0:
        k = min(len(a), int(fin * SR))
        a[:k] *= np.linspace(0, 1, k)[:, None]
    if fout > 0:
        k = min(len(a), int(fout * SR))
        a[-k:] *= np.linspace(1, 0, k)[:, None]
    return a


buf = np.zeros((N, 2))


def put(a, t0, db=0.0, pan=0.0):
    """Add a at time t0 (s), gain in dB, pan -1 (left) .. 1 (right), constant power."""
    g = 10 ** (db / 20)
    th = (pan + 1) * np.pi / 4
    a = a * g * np.array([np.cos(th), np.sin(th)]) * np.sqrt(2)
    i0 = int(round(t0 * SR))
    if i0 < 0:
        a, i0 = a[-i0:], 0
    n = min(len(a), N - i0)
    if n > 0:
        buf[i0: i0 + n] += a[:n]


def put_peak(a, t_peak, db=0.0, pan=0.0):
    """Place a so that its loudest moment lands on t_peak."""
    put(a, t_peak - peak_time(a), db, pan)


def shutter():
    """Two dry mechanical clicks (curtain open / close) with a short low body."""
    n = int(0.3 * SR)
    s = np.zeros(n)
    bp = butter(2, [1800, 7500], "band", fs=SR, output="sos")
    for d, g in ((0.0, 1.0), (0.06, 0.75)):
        k = int(0.02 * SR)
        tt = np.arange(k) / SR
        burst = sosfilt(bp, rng.standard_normal(k)) * np.exp(-tt * 240) + np.sin(2 * np.pi * 170 * tt) * np.exp(-tt * 180) * 0.5
        i = int(d * SR)
        s[i: i + k] += burst * g
    s = s / np.abs(s).max() * 0.5
    return np.stack([s, s], 1)


S = {k: load(k) for k in ["whoosh", "pop", "click", "click-soft", "chime", "sparkle", "impact-bass-1"]}

# ------------------------------------------------------------------ the phone
put_peak(fade(S["whoosh"], 0, 0.05), T["rise"] + 0.02, -6)                       # the phone rises into frame
put(S["click-soft"], T["tap"] - 0.05, -9)                                       # tap on the Manoo icon
put_peak(fade(pitched(S["whoosh"], 6), 0, 0.04), T["open"] + 0.08, -17)          # the camera opens out of the icon
put_peak(fade(pitched(S["whoosh"], -4), 0, 0.06), T["pill"] + 0.1, -5, -0.4)  # the pill flies in from the left…
put_peak(fade(pitched(S["whoosh"], -8), 0, 0.08), T["pill"] + 0.36, -8, 0.1)    # …while the camera dives to the shutter
put(pitched(S["pop"], -6), T["land"] - 0.01, -8)                                 # the pill seats in the shutter
put(S["click"], T["press"], -10)                                                # one press
put(shutter(), T["flash"], -4)                                                  # the photo
put_peak(fade(pitched(S["whoosh"], 2), 0, 0.05), T["swing"] + 0.16, -10, 0.3)    # the camera swings back up
put(pitched(S["pop"], 3), T["banner"] + 0.04, -13)                               # the island opens
put(fade(S["chime"][int(0.38 * SR):], 0, 0.6), T["done"], -11)                # added to the portfolio (the file opens on 0.4 s of silence)
put(pitched(S["pop"], 8), T["cell"] + 0.06, -17, 0.2)                            # the photo lands in the grid
put(pitched(S["pop"], -2), T["collapse"] + 0.12, -16)                            # the island folds back
# ------------------------------------------------------------------ the white end
put_peak(fade(pitched(S["whoosh"], -3)[::-1], 0.05, 0), T["words"] + 0.12, -21)  # air under the first words
put_peak(fade(pitched(S["whoosh"], 1), 0, 0.05), T["wordsOut"] + 0.14, -20)      # the line blurs away
put(fade(S["impact-bass-1"][: int(0.9 * SR)], 0, 0.6), T["mark"], -21)        # the mark lands (a short low bloom)
put(fade(S["sparkle"], 0, 0.4), T["mark"] + 0.04, -21, 0.15)
put_peak(fade(pitched(S["whoosh"], 4), 0, 0.05), T["expand"] + 0.2, -15)         # the mark opens into the wordmark
put(fade(S["sparkle"], 0, 0.6), T["expand"] + 0.26, -19, -0.15)

# ------------------------------------------------------------------ master: gentle clip, peak at -1.5 dBFS, short tail fade
tail = int(0.3 * SR)
buf[-tail:] *= np.linspace(1, 0, tail)[:, None]
buf = np.tanh(buf * 1.1) / 1.1
buf *= 10 ** (-1.5 / 20) / max(1e-9, np.abs(buf).max())
out = ROOT / "assets/audio/sfx.wav"
out.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(buf, -1, 1) * 32767).astype(np.int16).tobytes())
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
summary = r.stderr[r.stderr.rfind("Summary:"):]
lufs = re.search(r"I:\s+(-?[\d.]+) LUFS", summary)
tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summary)
print(f"{out.relative_to(ROOT)}: {T['END']} s, integrated {lufs.group(1) if lufs else '?'} LUFS, true peak {tp.group(1) if tp else '?'} dBFS")

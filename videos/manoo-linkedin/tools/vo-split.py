#!/usr/bin/env python3
"""Cut one continuous voice-over take into the SCRIPT.md lines, ready for `vo-build.py --lines DIR`.

For a take read in one go (e.g. the text of `python3 tools/vo-elevenlabs.py --text`, generated on the ElevenLabs
website with the Hugo voice and downloaded as one MP3):

  python3 tools/vo-split.py take.mp3                      # → assets/audio/vo/take/L01.wav … L19.wav
  python3 tools/vo-build.py --lines assets/audio/vo/take
  python3 tools/make-audio.py

The take is transcribed by whisper.cpp, the transcript is aligned to the script letter by letter, and each cut falls
on the quietest 30 ms between one line's last word and the next line's first word (vo-build trims the silences).
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
WHISPER = Path.home() / ".cache/hyperframes/whisper/whisper.cpp/build/bin/whisper-cli"
WMODEL = Path.home() / ".cache/hyperframes/whisper/models/ggml-small.bin"

ap = argparse.ArgumentParser()
ap.add_argument("take", type=Path)
ap.add_argument("--out", type=Path, default=ROOT / "assets/audio/vo/take")
args = ap.parse_args()


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", s.encode("ascii", "ignore").decode())


def spoken(text):  # what the voice reads (same rule as vo-elevenlabs.py)
    text = re.sub(r"manoo\.fr", "manou point F R", text, flags=re.I)
    return text.replace("Manoo", "Manou")


LINES = []
for m in re.finditer(r"^## Line (\d+)[^\n]*\n(.*?)(?=^## Line |\Z)", (ROOT / "SCRIPT.md").read_text(), flags=re.M | re.S):
    LINES.append({"id": int(m.group(1)), "say": spoken(re.search(r"^    (\S.*)$", m.group(2), flags=re.M).group(1).strip())})

pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(args.take), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                     check=True, capture_output=True).stdout
x = np.frombuffer(pcm, dtype=np.float32).copy()
print(f"take: {len(x) / SR:.2f} s, {len(LINES)} lines to find")

# ------------------------------------------------------------------ transcript with word start / end
with tempfile.TemporaryDirectory() as tmp:
    w16 = Path(tmp) / "take-16k.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(args.take), "-ac", "1", "-ar", "16000", str(w16)], check=True)
    subprocess.run([str(WHISPER), "--model", str(WMODEL), "--output-json-full", "--output-file", str(Path(tmp) / "take"),
                    "--dtw", "small", "-nfa", "--suppress-nst", "--language", "fr", str(w16)], check=True, capture_output=True)
    segs = json.loads((Path(tmp) / "take.json").read_text())["transcription"]
words = []  # [text, start, end]
for seg in segs:
    for tk in seg["tokens"]:
        tx = tk["text"]
        if tx.startswith("[_") or tx.startswith("<|") or not tx.strip():
            continue
        a, b = tk["offsets"]["from"] / 1000.0, tk["offsets"]["to"] / 1000.0
        dtw = tk.get("t_dtw", -1)
        if dtw is not None and dtw >= 0:
            a = dtw / 100.0
        if tx.startswith(" ") or not words:
            words.append([tx.strip(), a, b])
        else:
            words[-1][0] += tx
            words[-1][2] = b

# ------------------------------------------------------------------ which words belong to which line
S, s_line = "", []
for i, L in enumerate(LINES):
    n = norm(L["say"])
    S += n
    s_line += [i] * len(n)
T, t_word = "", []
for j, (w, _, _) in enumerate(words):
    n = norm(w)
    T += n
    t_word += [j] * len(n)
votes = {}
for a, b, size in difflib.SequenceMatcher(None, S, T, autojunk=False).get_matching_blocks():
    for k in range(size):
        key = (t_word[b + k], s_line[a + k])
        votes[key] = votes.get(key, 0) + 1
owner = {}
for (j, i), v in votes.items():
    if v > owner.get(j, (None, 0))[1]:
        owner[j] = (i, v)
spans = {}
for j, (i, _) in owner.items():
    lo, hi = spans.get(i, (j, j))
    spans[i] = (min(lo, j), max(hi, j))
missing = [LINES[i]["id"] for i in range(len(LINES)) if i not in spans]
if missing:
    sys.exit(f"lines not found in the take: {missing} — the take must read every line, in order")
order = [spans[i] for i in range(len(LINES))]
if any(order[i][0] <= order[i - 1][1] for i in range(1, len(order))):
    print("warning: lines overlap in the transcript; cuts fall between the nearest words")

# ------------------------------------------------------------------ cut in the quietest place between two lines
hop = SR // 100
nh = len(x) // hop
rms = np.sqrt(np.mean(x[: nh * hop].reshape(nh, hop) ** 2, 1) + 1e-12)
smooth = np.convolve(rms, np.ones(3) / 3, mode="same")
cuts = [0]
for i in range(len(LINES) - 1):
    end_i = words[order[i][1]][2]
    start_n = words[order[i + 1][0]][1]
    a, b = sorted((end_i, start_n))
    ha, hb = max(0, int(a * 100) - 5), min(nh - 1, int(b * 100) + 5)
    cuts.append((ha + int(np.argmin(smooth[ha: hb + 1]))) * hop)
cuts.append(len(x))

args.out.mkdir(parents=True, exist_ok=True)
for i, L in enumerate(LINES):
    seg = x[cuts[i]: cuts[i + 1]]
    with wave.open(str(args.out / f"L{L['id']:02d}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(seg, -1, 1) * 32767).astype(np.int16).tobytes())
    heard = " ".join(words[j][0] for j in range(order[i][0], order[i][1] + 1))
    print(f"  L{L['id']:02d} {cuts[i] / SR:6.2f}-{cuts[i + 1] / SR:6.2f}  {heard}")
out = args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out
print(f"next: python3 tools/vo-build.py --lines {out} && python3 tools/make-audio.py")

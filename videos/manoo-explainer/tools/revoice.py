#!/usr/bin/env python3
"""Put a new voice take on the film without re-authoring the animation.

    python3 tools/revoice.py --lines v/L1.wav v/L2.wav ... v/L7.wav   # one file per script line (Gemini, any TTS)
    python3 tools/revoice.py --take take.mp3                         # one file, the seven lines in order
        [--lead 0.13] [--lufs -16] [--tempo L4=1.04 ...] [--dry-run]

Every timing in the film was authored on the Holden take: assets/cues.js (tools/make-cues.py) and the literal
times in the compositions. This tool
  1. brings the new audio to --lufs (one gain for the whole voice, peaks held by a limiter at -1.5 dBFS);
  2. finds every SCRIPT.md word in it: whisper.cpp DTW onsets minus --lead, matched letter by letter;
  3. places line N so that its first word starts where Holden's did, trims it, and writes
     assets/audio/vo/LN.wav and the vo-N start/duration in index.html;
  4. writes assets/retime.js: one [Holden time, new time] pair per word. window.RETIME (every composition's L())
     and tools/make-audio.py use it, so each gesture, cue and sound effect lands on the same word of the new take;
  5. re-times the atelier shot in frame 4 so its camera flash still lands on « photo ».
Then: python3 tools/make-audio.py, re-carve the music (VOIX.md), npx hyperframes check, render.
--dry-run prints the placement and the moved cues without writing anything.
"""
import argparse
import difflib
import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
HOLDEN_LEAD = 0.15  # what tools/make-cues.py subtracted from Holden's DTW onsets
WHISPER = Path.home() / ".cache/hyperframes/whisper/whisper.cpp/build/bin/whisper-cli"
WMODEL = Path.home() / ".cache/hyperframes/whisper/models/ggml-small.bin"
# atelier shot in frame 4 as authored: host start, clip start (local), clip length, flash time inside the clip
ATELIER = {"host": 22.4, "start": 2.13, "dur": 3.4, "flash": 2.5}

ap = argparse.ArgumentParser()
src = ap.add_mutually_exclusive_group(required=True)
src.add_argument("--lines", nargs=7, metavar="WAV")
src.add_argument("--take")
ap.add_argument("--lead", type=float, default=0.13)
ap.add_argument("--lufs", type=float, default=-16.0)
ap.add_argument("--tempo", nargs="*", default=[], help="LN=rate, e.g. L4=1.04 (pitch kept)")
ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--verbose", action="store_true", help="print every word: Holden time, new time")
args = ap.parse_args()
tempo = {k: float(v) for k, v in (t.split("=") for t in args.tempo)}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", s.encode("ascii", "ignore").decode())


# ------------------------------------------------------------------ script, authored cues and clips
script = re.findall(r"^## Line (\d+)[^\n]*\n(?:.*\n)*?    (\S.*)$", (ROOT / "SCRIPT.md").read_text(), flags=re.M)
LINES = [[t for t in text.split() if re.search(r"\w", t)] for _, text in script]
assert len(LINES) == 7, len(LINES)
mc = (ROOT / "tools/make-cues.py").read_text()
CLIPS = [(float(a), float(b), float(s)) for _, a, b, s in re.findall(r'\("L(\d)", ([\d.]+), ([\d.]+), ([\d.]+)\)', mc)]
cues_txt = (ROOT / "assets/cues.js").read_text()
CU = json.loads(cues_txt[cues_txt.index("{") : cues_txt.rindex("}") + 1])


def align(tokens, words):
    """words: [(text, onset)] -> onset per token (None when the token has no word of its own)."""
    S, starts = "", []
    for t in tokens:
        starts.append(len(S))
        S += norm(t)
    W, owner = "", []
    for i, (w, _) in enumerate(words):
        n = norm(w)
        W += n
        owner += [i] * len(n)
    m = {}
    for a, b, size in difflib.SequenceMatcher(None, S, W, autojunk=False).get_matching_blocks():
        for k in range(size):
            m[a + k] = b + k
    out, used = [], set()
    for t, st in zip(tokens, starts):
        wi = next((owner[m[c]] for c in range(st, st + len(norm(t))) if c in m), None)
        if wi is None or wi in used:  # unmatched, or merged into the previous token's word
            out.append(None)
            continue
        used.add(wi)
        out.append(words[wi][1])
    return out


# authored side: Holden's full-take DTW words, mapped to film time like make-cues.py does
hw = json.loads((ROOT / "assets/audio/vo-src/words.json").read_text())
old_film = []
for k, (a, b, s) in enumerate(CLIPS):
    ws = [w for w in hw if a <= (w["dtw"] if w["dtw"] is not None else w["a"]) <= b]  # whisper's word start can sit before the cut
    on = [(w["w"], max((w["dtw"] if w["dtw"] is not None else w["a"]) - HOLDEN_LEAD, w["a"] - 0.05)) for w in ws]
    old_film.append([None if t is None else round(t - a + s, 3) for t in align(LINES[k], on)])


# ------------------------------------------------------------------ new audio
def decode(path, extra=""):
    chain = f"{extra}," if extra else ""
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-af", chain + "aresample=48000", "-ac", "1",
                          "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(pcm, dtype=np.float32).copy()


def lufs_of(x):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", "ebur128", "-f", "null", "-"], input=x.astype(np.float32).tobytes(), capture_output=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr.decode())[-1])


def limit(x, gain_db):
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af",
                        f"volume={gain_db:.2f}dB,alimiter=limit=0.84:attack=5:release=60:level=disabled",
                        "-f", "f32le", "-"], input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32).copy()


tmp = Path(tempfile.mkdtemp(prefix="revoice-"))


def words_of(x, tag):
    """[(text, onset s, start s)] from whisper.cpp DTW, or from `hyperframes transcribe` when it is missing."""
    wav = tmp / f"{tag}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-ar", "16000",
                    "-c:a", "pcm_s16le", str(wav)], input=x.astype(np.float32).tobytes(), check=True)
    if WHISPER.exists() and WMODEL.exists():
        subprocess.run([str(WHISPER), "--model", str(WMODEL), "--output-json-full", "--output-file", str(tmp / tag),
                        "--dtw", "small", "-nfa", "--suppress-nst", "--language", "fr", str(wav)],
                       check=True, capture_output=True)
        out = []
        for seg in json.loads((tmp / f"{tag}.json").read_text())["transcription"]:
            cur = None
            for tk in seg["tokens"]:
                t = tk["text"]
                if t.startswith("[_") or t.startswith("<|"):
                    continue
                dtw = tk.get("t_dtw", -1)
                on = dtw / 100.0 if dtw is not None and dtw >= 0 else tk["offsets"]["from"] / 1000.0
                if t.startswith(" ") or cur is None:
                    if cur:
                        out.append(cur)
                    cur = [t.strip(), on, tk["offsets"]["from"] / 1000.0]
                else:
                    cur[0] += t
            if cur:
                out.append(cur)
        return [(w, max(on - args.lead, st - 0.05), st) for w, on, st in out]
    # fallback: the CLI's transcriber (word starts, no DTW lag to remove)
    d = tmp / f"{tag}-tr"
    d.mkdir()
    subprocess.run(["npx", "--yes", "hyperframes", "transcribe", str(wav), "--dir", str(d), "--language", "fr",
                    "--model", "large-v3"], check=True, capture_output=True)
    tr = json.loads(next(d.glob("*.json")).read_text())
    words = tr if isinstance(tr, list) else tr.get("words", [])
    return [(w["text"], float(w["start"]), float(w["start"])) for w in words]


if args.lines:
    parts = [decode(p) for p in args.lines]
else:
    parts = [decode(args.take)]
lin = lufs_of(np.concatenate(parts))
gain = args.lufs - lin
parts = [limit(p, gain) for p in parts]
print(f"voice {lin:.1f} LUFS -> {args.lufs:.1f} LUFS ({gain:+.1f} dB, limiter -1.5 dBFS)")

hop = SR // 100


def envelope(x):
    return np.sqrt(np.convolve(x**2, np.ones(hop) / hop, mode="same"))[::hop]


segs = []  # per line: (audio, onsets per token)
if args.lines:
    for k, x in enumerate(parts):
        segs.append((x, align(LINES[k], [(w, on) for w, on, _ in words_of(x, f"L{k + 1}")])))
else:
    x = parts[0]
    ws = words_of(x, "take")
    flat = [t for line in LINES for t in line]
    on = align(flat, [(w, o) for w, o, _ in ws])
    env = envelope(x)
    per, i = [], 0
    for line in LINES:
        per.append(on[i : i + len(line)])
        i += len(line)
    cuts = [0.0]
    for k in range(1, 7):
        last = max(t for t in per[k - 1] if t is not None)
        first = min(t for t in per[k] if t is not None)
        a, b = int((last + 0.25) * 100), max(int((last + 0.25) * 100) + 1, int((first - 0.03) * 100))
        cuts.append((a + int(np.argmin(env[a:b]))) / 100.0)
    cuts.append(len(x) / SR)
    for k in range(7):
        a, b = cuts[k], cuts[k + 1]
        segs.append((x[int(a * SR) : int(b * SR)], [None if t is None else t - a for t in per[k]]))

# optional per-line tempo (pitch kept), onsets scale with it
for k, (x, on) in enumerate(segs):
    r = tempo.get(f"L{k + 1}")
    if r:
        y = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af",
                            f"atempo={r}", "-f", "f32le", "-"], input=x.tobytes(), capture_output=True, check=True).stdout
        segs[k] = (np.frombuffer(y, dtype=np.float32).copy(), [None if t is None else t / r for t in on])

# ------------------------------------------------------------------ placement
placed, points, report = [], [], []
for k, (x, on) in enumerate(segs):
    env = envelope(x)
    first_i = next(i for i, t in enumerate(on) if t is not None and old_film[k][i] is not None)
    t_first = on[first_i]
    loud = np.nonzero(env > 10 ** (-45 / 20))[0]
    speech_end = loud[-1] / 100.0
    pre = min(0.25, t_first)
    src_in = t_first - pre
    src_out = min(len(x) / SR, speech_end + 0.25)
    film0 = old_film[k][first_i] - (t_first - src_in)
    placed.append([round(film0, 3), round(src_in, 3), round(src_out, 3)])
    for i, t in enumerate(on):
        if t is not None and old_film[k][i] is not None:
            points.append([old_film[k][i], round(film0 + t - src_in, 3)])
    old_last = max(t for t in old_film[k] if t is not None)
    new_last = max(film0 + t - src_in for t in on if t is not None)
    if args.verbose:
        print(f"L{k + 1} first={LINES[k][first_i]!r} t_first={t_first:.2f} pre={pre:.2f} src_in={src_in:.2f}")
        print("   ", " ".join(f"{w}[{'-' if o is None else f'{o:.2f}'}|{'-' if t is None else f'{film0 + t - src_in:.2f}'}]" for w, o, t in zip(LINES[k], old_film[k], on)))
    report.append(f"  L{k + 1}: film {film0:6.2f} -> {film0 + src_out - src_in:6.2f}  last word {old_last:6.2f} -> {new_last:6.2f} ({new_last - old_last:+.2f})")
for k in range(6):
    end = placed[k][0] + placed[k][2] - placed[k][1]
    if end > placed[k + 1][0] - 0.05:
        report.append(f"  !! L{k + 1} overlaps L{k + 2} by {end - placed[k + 1][0] + 0.05:.2f}s: shorten its tail or use --tempo L{k + 1}=…")

# strictly increasing on both axes
points.sort()
clean = []
for p in points:
    if not clean or (p[0] > clean[-1][0] + 1e-3 and p[1] > clean[-1][1] + 1e-3):
        clean.append(p)


def rt(t):
    P = clean
    if t <= P[0][0]:
        return t + P[0][1] - P[0][0]
    if t >= P[-1][0]:
        return t + P[-1][1] - P[-1][0]
    for (a0, a1), (b0, b1) in zip(P, P[1:]):
        if a0 <= t <= b0:
            return a1 + (t - a0) * (b1 - a1) / (b0 - a0)


print("lines:")
print("\n".join(report))
moved = sorted(((k, v, rt(v)) for k, v in CU.items() if isinstance(v, (int, float)) and k != "END"), key=lambda r: r[1])
print("cues (Holden -> new):", "  ".join(f"{k} {v:.2f}->{n:.2f}" for k, v, n in moved))
fl0 = ATELIER["host"] + ATELIER["start"]
a0, a1 = rt(fl0), rt(fl0 + ATELIER["flash"])
rate = ATELIER["flash"] / (a1 - a0)
print(f"atelier shot: start {fl0:.2f} -> {a0:.2f}, flash {fl0 + ATELIER['flash']:.2f} -> {a1:.2f}, rate {rate:.3f}")
if args.dry_run:
    shutil.rmtree(tmp, ignore_errors=True)
    raise SystemExit(0)

# ------------------------------------------------------------------ write
vo = ROOT / "assets/audio/vo"
for k, ((x, _), (film0, a, b)) in enumerate(zip(segs, placed)):
    y = x[int(a * SR) : int(b * SR)].copy()
    f = int(0.008 * SR)
    y[:f] *= np.linspace(0, 1, f)
    y[-f:] *= np.linspace(1, 0, f)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a",
                    "pcm_s16le", str(vo / f"L{k + 1}.wav")], input=y.astype(np.float32).tobytes(), check=True)
html_p = ROOT / "index.html"
html = html_p.read_text()
for k, (film0, a, b) in enumerate(placed):
    def fix(m):
        tag = re.sub(r'data-start="[\d.]+"', f'data-start="{film0}"', m.group(0))
        return re.sub(r'data-duration="[\d.]+"', f'data-duration="{round(b - a, 3)}"', tag)
    html, n = re.subn(rf'<audio\b[^>]*\bid="vo-{k + 1}"[^>]*>', fix, html)
    assert n == 1, k
html_p.write_text(html)
rj = ROOT / "assets/retime.js"
rj.write_text(re.sub(r"window\.RETIME_POINTS = \[.*?\];", "window.RETIME_POINTS = " + json.dumps(clean) + ";",
                     rj.read_text(), flags=re.S))
f4 = ROOT / "compositions/frames/04-jeune-pro.html"
s4 = f4.read_text()
def fix_vid(m):
    tag = re.sub(r'\s*data-playback-rate="[\d.]+"', "", m.group(0))
    tag = re.sub(r'data-start="[\d.]+"', f'data-start="{round(a0 - ATELIER["host"], 3)}"', tag)
    tag = re.sub(r'data-duration="[\d.]+"', f'data-duration="{round(ATELIER["dur"] / rate, 3)}"', tag)
    if abs(rate - 1) > 0.005:
        tag = tag.replace(" data-start=", f' data-playback-rate="{rate:.3f}" data-start=')
    return tag
s4, n = re.subn(r'<video\b[^>]*\bid="j-vid"[^>]*>', fix_vid, s4)
assert n == 1
f4.write_text(s4)
(vo / "voice-take.json").write_text(json.dumps({
    "source": args.lines or [args.take], "lufs_in": lin, "gain_db": round(gain, 2), "lead": args.lead,
    "tempo": tempo, "clips": {f"L{k + 1}": p for k, p in enumerate(placed)}, "retime_points": len(clean)}, indent=1))
shutil.rmtree(tmp, ignore_errors=True)
print(f"wrote 7 clips, index.html vo timings, assets/retime.js ({len(clean)} points), atelier shot timing")

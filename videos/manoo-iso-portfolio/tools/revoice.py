#!/usr/bin/env python3
"""Re-voice the film with a new take: cut the six line clips and move every cue to the same word.

    python3 tools/revoice.py --take assets/audio/vo/<take>.mp3 --words <whisper DTW words.json> [--lead 0.11]

- Line slots are kept: each vo-N clip starts at the same film time (index.html data-start); only its
  data-duration changes. The take is cut at the quietest point between two lines.
- Word cues (WORDS: cue -> line, word index) land on that word's onset in the new take. Gesture cues keep
  their offset to the nearest word cue of their line, as tuned on the previous take. Scene cues (s2…s6) stay
  with the fixed frame hosts.
- words.json is a list of {"w": text, "t": DTW onset}; DTW onsets land ~0.1 s after the acoustic onset, so
  --lead is subtracted. Writes the clips, the new transcript, assets/cues.js and the clip durations.
Run from the project root, then: python3 tools/make-audio.py, re-run the carve, check, render.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
SCENE_CUES = {"s2", "s3", "s4", "s5", "s6"}
# cue -> (line, word index in that line); the six lines of SCRIPT.md, words as whisper splits them
WORDS = {
    "savoirFaire": (0, 1), "neSe": (0, 2), "raconte": (0, 4), "pas": (0, 5), "ilSe": (0, 6), "montre": (0, 8),
    "avec": (1, 0), "photographient": (1, 5), "piece": (1, 9), "metallerie": (1, 11), "chantier": (1, 13),
    "ouvrage": (1, 15), "artisanat": (1, 16),
    "unePhoto": (2, 0), "unTitre": (2, 2), "chaque": (2, 4), "rejoint": (2, 6), "portfolio": (2, 8), "visuel": (2, 9),
    "leurTravail": (3, 0), "vu": (3, 4), "comptent": (3, 8), "entreprises": (3, 10), "recrutent": (3, 12),
    "lycees": (3, 14), "forment": (3, 17), "clients": (3, 19), "choisissent": (3, 21),
    "chaqueReal": (4, 0), "devient": (4, 2), "preuve": (4, 4), "trace": (4, 6), "carriere": (4, 12),
    "manoo": (5, 0), "regard": (5, 4), "demandez": (5, 5), "site": (5, 9),
}

ap = argparse.ArgumentParser()
ap.add_argument("--take", required=True)
ap.add_argument("--words", required=True)
ap.add_argument("--lead", type=float, default=0.11)
args = ap.parse_args()


def parse_cues(txt):
    body = txt[txt.index("{") : txt.rindex("}") + 1]
    body = re.sub(r"//[^\n]*", "", body)
    body = re.sub(r"(\w+):", r'"\1":', body)
    body = re.sub(r",(\s*[}\]])", r"\1", body)
    return json.loads(body)


cues_path = ROOT / "assets/cues.js"
cues_txt = cues_path.read_text()
CU = parse_cues(cues_txt)
old_vo = CU["VO"]
old_words = json.loads((ROOT / "assets/audio/vo/transcript.json").read_text())
old_lines = [[w for w in old_words if a <= w["start"] < b] for _, a, b in old_vo]

# new take: decode once at 48 kHz mono
take = Path(args.take)
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(take), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                     check=True, capture_output=True).stdout
x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
take_dur = len(x) / SR
new_words = [{"text": w["w"], "start": round(max(0.0, w["t"] - args.lead), 3)} for w in json.loads(Path(args.words).read_text())]
assert len(new_words) == len(old_words), f"word count differs: {len(new_words)} vs {len(old_words)}"
new_lines, i = [], 0
for line in old_lines:
    new_lines.append(new_words[i : i + len(line)])
    i += len(line)

# 10 ms RMS envelope, used to cut in the quietest spot between lines
hop = SR // 100
env = np.sqrt(np.convolve(x**2, np.ones(hop) / hop, mode="same"))[::hop]


def quietest(a, b):
    ia, ib = int(a * 100), max(int(a * 100) + 1, int(b * 100))
    return (ia + int(np.argmin(env[ia:ib]))) / 100.0


cuts = [0.0]
for k in range(1, len(new_lines)):
    prev_last = new_lines[k - 1][-1]["start"]
    first = new_lines[k][0]["start"]
    cuts.append(quietest(prev_last + 0.3, first - 0.03))
# end of speech: last frame above -45 dBFS, plus a short tail
loud = np.nonzero(env > 10 ** (-45 / 20))[0]
cuts.append(min(take_dur, loud[-1] / 100.0 + 0.25))

slots = [v[0] for v in old_vo]
windows = [slots[k + 1] - slots[k] for k in range(len(slots) - 1)] + [CU["END"] - slots[-1]]
new_vo = []
vo_dir = ROOT / "assets/audio/vo"
for k in range(len(new_lines)):
    a, b = cuts[k], cuts[k + 1]
    b = min(b, a + windows[k] - 0.05)
    seg = x[int(a * SR) : int(b * SR)].copy()
    f = int(0.008 * SR)
    seg[:f] *= np.linspace(0, 1, f)
    seg[-f:] *= np.linspace(1, 0, f)
    out = vo_dir / f"L{k + 1}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "pcm_s16le", str(out)], input=seg.astype(np.float32).tobytes(), check=True)
    new_vo.append([slots[k], round(a, 3), round(b, 3)])

# move cues
film_new = lambda k, t: new_vo[k][0] + (t - new_vo[k][1])
line_of = lambda t: max([i for i, v in enumerate(old_vo) if v[0] <= t + 1e-6] or [0])
new_cu, report = {}, []
for key, (k, j) in WORDS.items():
    new_cu[key] = round(film_new(k, new_lines[k][j]["start"]), 2)
    report.append(f"  {key:15s} {CU[key]:6.2f} -> {new_cu[key]:6.2f}  (word «{new_lines[k][j]['text']}»)")
for key, t in CU.items():
    if key in ("END", "VO") or key in SCENE_CUES or key in WORDS:
        continue
    k = line_of(t)
    named = [c for c, (lk, _) in WORDS.items() if lk == k]
    anchor = min(named, key=lambda c: abs(CU[c] - t))
    new_cu[key] = round(new_cu[anchor] + (t - CU[anchor]), 2)
    report.append(f"  {key:15s} {t:6.2f} -> {new_cu[key]:6.2f}  ({t - CU[anchor]:+.2f} from {anchor})")
missing = [c for c in CU if c not in new_cu and c not in ("END", "VO") and c not in SCENE_CUES]
assert not missing, missing

# write cues.js in place (keeps comments and order)
txt = cues_txt
vo_block = "VO: [\n" + "".join(f"    [{a}, {s}, {e}],\n" for a, s, e in new_vo) + "  ],"
txt = re.sub(r"VO: \[.*?\n  \],", vo_block, txt, flags=re.S)
for key, v in new_cu.items():
    txt, n = re.subn(rf"(\n  {key}: )[\d.]+", rf"\g<1>{v}", txt)
    assert n == 1, key
txt = re.sub(r"^// Film cue sheet.*?\n(?=window\.CUES)",
             f"// Film cue sheet (seconds, film time). Source: {take.name} (assets/audio/vo/), cut into six line clips\n"
             "// placed at fixed slots (see index.html) by tools/revoice.py. Word times come from\n"
             "// assets/audio/vo/transcript.json (whisper DTW onsets), shifted by each clip's offset.\n", txt, flags=re.S)
cues_path.write_text(txt)

# new source transcript (same shape as before; end = next onset, capped)
flat = [w for line in new_lines for w in line]
trans = []
for n, w in enumerate(flat):
    end = flat[n + 1]["start"] if n + 1 < len(flat) else w["start"] + 0.6
    trans.append({"text": w["text"], "start": w["start"], "end": round(min(end, w["start"] + 1.2), 3), "id": f"w{n}"})
(vo_dir / "transcript.json").write_text(json.dumps(trans, ensure_ascii=False, indent=1))

# clip durations in index.html
html_path = ROOT / "index.html"
html = html_path.read_text()
for k, (a, s, e) in enumerate(new_vo):
    html, n = re.subn(rf'(<audio\b[^>]*\bid="vo-{k + 1}"[^>]*\bdata-duration=")[\d.]+(")', rf"\g<1>{round(e - s, 3)}\g<2>", html)
    assert n == 1, k
html_path.write_text(html)

print("clips:", " ".join(f"L{k + 1} {s:.2f}-{e:.2f} ({e - s:.2f}s / slot {windows[k]:.2f}s)" for k, (a, s, e) in enumerate(new_vo)))
print("\n".join(report))

#!/usr/bin/env python3
"""Tighten the music carve's broadband level lane (run after carve.mjs).

carve.mjs releases slowly (~4.5 dB/s), so the bed never comes back up in the short breaths between
lines and stays ~12 dB down on the end card. This rebuilds that lane: inside each voice clip the carve's
own values are kept; 0.3 s after a clip ends the bed returns to 0 dB and stays there until 0.25 s before
the next clip. Run from the project root: python3 tools/fix-carve.py
"""
import html, json, re

p = "index.html"
s = open(p).read()
clips = sorted((float(a), float(a) + float(d)) for a, d in re.findall(r'<audio id="vo-\d"[^>]*data-start="([\d.]+)" data-duration="([\d.]+)"', s))
m = re.search(r'(id="music"[^>]*data-automation=")([^"]*)(")', s)
auto = json.loads(html.unescape(m.group(2)))
lanes = auto["lanes"]
# the broadband level lane is the one with the deepest average cut
lvl = min(lanes, key=lambda l: sum(p["v"] for p in l["points"]) / len(l["points"]))
pts = lvl["points"]
def inside(t):
    return any(a - 0.12 <= t <= b + 0.05 for a, b in clips)
new = [p for p in pts if inside(p["t"])]
for i, (a, b) in enumerate(clips):
    nxt = clips[i + 1][0] if i + 1 < len(clips) else None
    new.append({"t": round(b + 0.3, 3), "v": 0})
    if nxt is not None and nxt - 0.25 > b + 0.3:
        new.append({"t": round(nxt - 0.25, 3), "v": 0})
if clips[0][0] - 0.25 > 0:
    new.append({"t": 0, "v": 0})
    new.append({"t": round(clips[0][0] - 0.25, 3), "v": 0})
new.append({"t": 55.5, "v": 0})
new = sorted({p["t"]: p for p in new}.values(), key=lambda p: p["t"])
lvl["points"] = new
enc = html.escape(json.dumps(auto, separators=(",", ":")), quote=True)
s = s[: m.start(2)] + enc + s[m.end(2) :]
open(p, "w").write(s)
print("level lane", lvl["target"], len(pts), "->", len(new), "points;", len(clips), "voice clips")

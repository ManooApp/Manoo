#!/usr/bin/env python3
"""Tighten the music carve's broadband level lane (run after carve.mjs).

carve.mjs releases slowly (~4.5 dB/s), so the bed never comes back up in the short breaths between
lines and stays ~12 dB down on the end card. This rebuilds that lane: inside each voice clip the carve's
own values are kept; 0.3 s after a clip ends the bed returns to 0 dB and stays there until 0.25 s before
the next clip. After the last line the bed swells by END_LIFT_DB to carry the end card.
Run from the project root: python3 tools/fix-carve.py
"""
import html, json, re

END = 55.5
END_LIFT_DB = 5.0  # music-only end card: lift the bed back toward the voice sections
END_LIFT_RAMP = 0.36  # seconds from 0 dB (last line + 0.3 s) to the full lift

p = "index.html"
s = open(p).read()
def attr(tag, name):
    return float(re.search(r'\b' + name + r'="([\d.]+)"', tag).group(1))
vo_tags = re.findall(r'<audio\b[^>]*\bid="vo-\d+"[^>]*>', s)
clips = sorted((attr(t, "data-start"), attr(t, "data-start") + attr(t, "data-duration")) for t in vo_tags)
m = re.search(r'(id="music"[^>]*data-automation=")([^"]*)(")', s)
auto = json.loads(html.unescape(m.group(2)))
lanes = auto["lanes"]
# the broadband level lane drives the chain's gain node (fallback: the deepest average cut)
chain = json.loads(html.unescape(re.search(r'id="music"[^>]*data-fx-chain="([^"]*)"', s).group(1)))
gain_ids = [n["id"] for n in chain["nodes"] if n["type"] == "gain"]
by_target = [l for l in lanes if gain_ids and l["target"] == "fx." + gain_ids[-1] + ".gain"]
lvl = by_target[0] if by_target else min(lanes, key=lambda l: sum(p["v"] for p in l["points"]) / len(l["points"]))
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
last_end = round(clips[-1][1] + 0.3, 3)
new = [p for p in new if p["t"] <= last_end]
new.append({"t": round(last_end + END_LIFT_RAMP, 3), "v": END_LIFT_DB})
new.append({"t": END, "v": END_LIFT_DB})
new = sorted({p["t"]: p for p in new}.values(), key=lambda p: p["t"])
lvl["points"] = new
enc = html.escape(json.dumps(auto, separators=(",", ":")), quote=True)
s = s[: m.start(2)] + enc + s[m.end(2) :]
open(p, "w").write(s)
print("level lane", lvl["target"], len(pts), "->", len(new), "points;", len(clips), "voice clips")

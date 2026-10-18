#!/usr/bin/env python3
"""Voice-over for the Manoo LinkedIn / Instagram ad.

One file per SCRIPT.md line, laid on the film at the line gaps, every word timed from whisper.cpp DTW onsets, then
written to assets/cues.js so the captions and the animation follow the voice. Swapping the voice is one command:

  python3 tools/vo-build.py                 # Kokoro ff_siwis (local): synthesize missing / changed lines, then time
  python3 tools/vo-build.py --lines DIR     # any other take cut into DIR/L01.wav ... L20.wav (ElevenLabs, Gemini, a human)

Outputs: assets/audio/vo/src/LNN.wav (raw Kokoro lines), assets/audio/vo/vo.wav (48 kHz mono, loudness-normalized),
assets/audio/vo/words.json (inspection) and assets/cues.js (window.VO, window.CUES, window.W).
"""
import argparse
import difflib
import hashlib
import json
import re
import subprocess
import tempfile
import unicodedata
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
LEAD = 0.30  # first word lands right after the first frame
TAIL = 2.3  # hold after the last line (logo + address on screen)
VOICE, SPEED, HF = "ff_siwis", "1.05", "hyperframes@0.8.172"
WHISPER = Path.home() / ".cache/hyperframes/whisper/whisper.cpp/build/bin/whisper-cli"
WMODEL = Path.home() / ".cache/hyperframes/whisper/models/ggml-small.bin"
DTW_LAG = 0.12  # whisper.cpp DTW onsets land ~0.1 s late on Kokoro ff_siwis; measure it again for another voice

ap = argparse.ArgumentParser()
ap.add_argument("--lines", type=Path, help="directory with L01.wav ... LNN.wav from another voice")
ap.add_argument("--lufs", type=float, default=-16.0)
ap.add_argument("--dtw-lag", type=float, default=DTW_LAG, help="seconds the whisper DTW onsets land late on this voice")
args = ap.parse_args()


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", s.encode("ascii", "ignore").decode())


# ------------------------------------------------------------------ SCRIPT.md
LINES = []
for m in re.finditer(r"^## Line (\d+)[^\n]*\n(.*?)(?=^## Line |\Z)", (ROOT / "SCRIPT.md").read_text(), flags=re.M | re.S):
    body = m.group(2)
    text = re.search(r"^    (\S.*)$", body, flags=re.M).group(1).strip()
    tts = re.search(r"^tts:\s*(.+)$", body, flags=re.M)
    gap = re.search(r"gap\s+([0-9.]+)", body)
    LINES.append({"id": int(m.group(1)), "text": text, "tts": tts.group(1).strip() if tts else text,
                  "gap": float(gap.group(1)) if gap else 0.0})
print(f"{len(LINES)} lines")


# ------------------------------------------------------------------ audio helpers
def decode(path):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(pcm, dtype=np.float32).copy()


def trim(x, floor_db=-45.0, pad=0.04):
    win = SR // 100
    n = len(x) // win
    rms = np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1) + 1e-12)
    on = np.where(20 * np.log10(rms) > floor_db)[0]
    if len(on) == 0:
        return x
    a = max(0, on[0] * win - int(pad * SR))
    b = min(len(x), (on[-1] + 1) * win + int(pad * SR))
    return x[a:b]


def lufs(x):
    tmp = Path(tempfile.mkstemp(suffix=".wav")[1])
    write_wav(tmp, x)
    out = subprocess.run(["ffmpeg", "-nostats", "-i", str(tmp), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    tmp.unlink()
    return float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", out)[-1])


def write_wav(path, x, sr=SR):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


# ------------------------------------------------------------------ 1 · the lines
src = ROOT / "assets/audio/vo/src"
src.mkdir(parents=True, exist_ok=True)
manifest_p = src / "manifest.json"
manifest = json.loads(manifest_p.read_text()) if manifest_p.exists() else {}
paths = []
for L in LINES:
    name = f"L{L['id']:02d}.wav"
    if args.lines:
        paths.append(args.lines / name)
        continue
    key = hashlib.sha1(f"{VOICE}|{SPEED}|{L['tts']}".encode()).hexdigest()
    p = src / name
    if not p.exists() or manifest.get(name) != key:
        print(f"  tts {name}: {L['tts']}")
        subprocess.run(["npx", "--yes", HF, "tts", L["tts"], "-v", VOICE, "-s", SPEED, "-o", str(p)],
                       check=True, capture_output=True)
        manifest[name] = key
    paths.append(p)
manifest_p.write_text(json.dumps(manifest, indent=1))

parts = [trim(decode(p)) for p in paths]
gain = args.lufs - lufs(np.concatenate(parts))
parts = [p * 10 ** (gain / 20) for p in parts]
peak = max(float(np.max(np.abs(p))) for p in parts)
if peak > 0.84:  # keep 1.5 dB of headroom for the mix
    parts = [p * (0.84 / peak) for p in parts]
print(f"voice normalized ({gain:+.1f} dB), peak {20 * np.log10(max(float(np.max(np.abs(p))) for p in parts)):.1f} dBFS")

# ------------------------------------------------------------------ 2 · lay the lines on the film
t, starts = LEAD, []
for L, x in zip(LINES, parts):
    starts.append(t)
    t += len(x) / SR + L["gap"]
end_voice = starts[-1] + len(parts[-1]) / SR
END = round(end_voice + TAIL, 2)
vo = np.zeros(int(END * SR) + SR)
for s, x in zip(starts, parts):
    i = int(round(s * SR))
    vo[i: i + len(x)] += x
vo = vo[: int(END * SR)]
out_dir = ROOT / "assets/audio/vo"
write_wav(out_dir / "vo.wav", vo)
print(f"vo.wav: {END:.2f} s (voice ends {end_voice:.2f} s)")


# ------------------------------------------------------------------ 3 · time every word
def whisper_words(x, tag, tmp):
    wav = tmp / f"{tag}.wav"
    write_wav(wav, x)
    w16 = tmp / f"{tag}-16k.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-ar", "16000", str(w16)], check=True)
    subprocess.run([str(WHISPER), "--model", str(WMODEL), "--output-json-full", "--output-file", str(tmp / tag),
                    "--dtw", "small", "-nfa", "--suppress-nst", "--language", "fr", str(w16)],
                   check=True, capture_output=True)
    out, cur = [], None
    for seg in json.loads((tmp / f"{tag}.json").read_text())["transcription"]:
        for tk in seg["tokens"]:
            tx = tk["text"]
            if tx.startswith("[_") or tx.startswith("<|"):
                continue
            dtw = tk.get("t_dtw", -1)
            st = tk["offsets"]["from"] / 1000.0
            on = dtw / 100.0 - args.dtw_lag if dtw is not None and dtw >= 0 else st
            if tx.startswith(" ") or cur is None:
                if cur:
                    out.append(cur)
                cur = [tx.strip(), max(0.0, on)]
            else:
                cur[0] += tx
    if cur:
        out.append(cur)
    return out


def align(tokens, words):
    """tokens: display words; words: [(text, onset)] from whisper -> onset per token (None when unmatched)."""
    S, st = "", []
    for tk in tokens:
        st.append(len(S))
        S += tk
    W, owner = "", []
    for i, (w, _) in enumerate(words):
        n = norm(w)
        W += n
        owner += [i] * len(n)
    m = {}
    for a, b, size in difflib.SequenceMatcher(None, S, W, autojunk=False).get_matching_blocks():
        for k in range(size):
            m[a + k] = b + k
    res, used = [], set()
    for tk, s0 in zip(tokens, st):
        wi = next((owner[m[c]] for c in range(s0, s0 + len(tk)) if c in m), None)
        if wi is None or wi in used:
            res.append(None)
            continue
        used.add(wi)
        res.append(words[wi][1])
    return res


def voice_onset(x):
    """First 5 ms frame within 30 dB of the line's peak: where the voice really starts in a trimmed line."""
    win = SR // 200
    n = len(x) // win
    db = 20 * np.log10(np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1)) + 1e-9)
    hit = np.where(db > db.max() - 30)[0]
    return hit[0] * win / SR if len(hit) else 0.04


def rise_after_pause(sig, t, look=0.3, pause=0.07):
    """Where the signal comes back after the last >= 70 ms stretch under -40 dBFS that ends before t (None if none)."""
    win = SR // 200
    i1, i0 = int(t * SR) // win, max(0, int((t - look) * SR) // win)
    if i1 - i0 < 4:
        return None
    seg = sig[i0 * win: i1 * win]
    db = 20 * np.log10(np.sqrt(np.mean(seg[: (len(seg) // win) * win].reshape(-1, win) ** 2, axis=1)) + 1e-9)
    quiet = db < -40
    k = len(db) - 1
    while k >= 0 and not quiet[k]:
        k -= 1
    run_end = k
    while k >= 0 and quiet[k]:
        k -= 1
    if run_end < 0 or (run_end - k) * win / SR < pause:
        return None
    rise = next((j for j in range(run_end + 1, len(db)) if db[j] > -35), None)
    return None if rise is None else (i0 + rise) * win / SR


def after_pause(x, xv, t):
    """A word that follows a pause starts where the voice comes back: whisper's DTW onsets land up to ~0.15 s late on
    soft consonants (« Manou » after « Voici »). A true silence in the full band is trusted first (its rise keeps a
    word's leading « s »); otherwise a pause in the voicing band (80-1000 Hz) right before the word, which a breathy
    tail on the previous word can hide from the full band. Stop closures are shorter than 70 ms and are left alone."""
    for sig, near in ((x, 0.25), (xv, 0.2)):
        r = rise_after_pause(sig, t)
        if r is not None and t - near <= r < t:
            return r
    return t


tmp = Path(tempfile.mkdtemp(prefix="vo-build-"))
out_lines = []
for k, (L, x, s) in enumerate(zip(LINES, parts, starts)):
    ww = whisper_words(x, f"L{L['id']:02d}", tmp)
    disp = [d for d in L["text"].split() if norm(d)]
    # the voice reads « Manou » for « Manoo »: align on what was spoken
    keys = [norm(d).replace("manoofr", "manoupointfr").replace("manoo", "manou") for d in disp]
    on = align(keys, ww)
    dur = len(x) / SR
    # fill gaps: first word at the line start, others between their neighbours
    # whisper lands a soft first consonant late (« Manou », « Voici »): the first word starts where the voice does
    v0 = voice_onset(x)
    xv = sosfilt(butter(4, [80, 1000], "band", fs=SR, output="sos"), x)
    if on and (on[0] is None or on[0] > v0 + 0.05):
        on[0] = round(v0, 3)
    for i in range(1, len(on)):
        if on[i] is None:
            nxt = next((on[j] for j in range(i + 1, len(on)) if on[j] is not None), dur - 0.1)
            on[i] = round(on[i - 1] + (nxt - on[i - 1]) / 2, 3)
        else:
            on[i] = round(after_pause(x, xv, on[i]), 3)
        on[i] = max(on[i], on[i - 1] + 0.05)
    words = [[d, round(s + o, 3)] for d, o in zip(disp, on)]
    heard = " ".join(w for w, _ in ww)
    out_lines.append({"id": L["id"], "start": round(s, 3), "end": round(s + dur, 3), "text": L["text"], "words": words,
                      "heard": heard})
    print(f"  L{L['id']:02d} {s:6.2f}-{s + dur:6.2f}  {heard}")

(out_dir / "words.json").write_text(json.dumps(out_lines, ensure_ascii=False, indent=1))

# ------------------------------------------------------------------ 4 · scenes cut from the voice
# each scene opens a little before its first line; the cut sits in the silence before the next scene's first line
SCENE_DEFS = [  # (id, composition file, first line, lead before that line)
    ("accroche", "01-accroche", 1, None), ("question", "02-question", 3, 0.2), ("classiques", "03-classiques", 4, 0.25),
    ("pivot", "04-pivot", 7, 0.25), ("revelation", "05-revelation", 9, 0.3), ("demo", "06-demo", 10, 0.3),
    ("communaute", "07-communaute", 12, 0.3), ("entreprises", "08-entreprises", 15, 0.3), ("nuance", "09-nuance", 17, 0.3),
    ("fin", "10-fin", 18, 0.35)]
by_id = {L["id"]: L for L in out_lines}
cuts = [0.0 if lead is None else round(by_id[first]["start"] - lead, 2) for _, _, first, lead in SCENE_DEFS] + [END]
SCENES = {sid: [cuts[i], round(cuts[i + 1] - cuts[i], 2)] for i, (sid, _, _, _) in enumerate(SCENE_DEFS)}
idx = ROOT / "index.html"
if idx.exists():
    html = idx.read_text()
    a, b = html.find("<!-- scenes:begin -->"), html.find("<!-- scenes:end -->")
    if a >= 0 and b > a:
        rows = []
        for sid, comp, _, _ in SCENE_DEFS:
            st, du = SCENES[sid]
            rows.append(f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/scenes/{comp}.html" '
                        f'data-start="{st}" data-duration="{du}" data-track-index="1" data-track-kind="graphics" '
                        f'data-width="1080" data-height="1920"></div>')
        html = html[: a + len("<!-- scenes:begin -->")] + "\n" + "\n".join(rows) + "\n      " + html[b:]
        html = re.sub(r'(data-composition-id="main"[^>]*data-duration=")[0-9.]+', lambda m: m.group(1) + f"{END}", html)
        html = re.sub(r'(<(?:audio|div)[^>]*data-whole="1"[^>]*data-duration=")[0-9.]+', lambda m: m.group(1) + f"{END}", html)
        idx.write_text(html)
        print("index.html scenes updated")
# the atelier clip (06-demo, assets/video/atelier-hold.mp4: 3.4 s of footage + 2 s held on the last frame): its
# in-camera flash (media 2.5 s) lands on « Photos », and it plays until the card has left (0.5 s before « publies »,
# 0.42 s exit)
demo = ROOT / "compositions/scenes/06-demo.html"
if demo.exists():
    d0 = SCENES["demo"][0]
    w10 = {norm(t): s for t, s in by_id[10]["words"]}
    media_start = round(max(0.0, 2.5 - (w10["photos"] - d0)), 2)
    clip = round(min(w10["publies"] - 0.08 - d0, 5.4 - media_start), 2)
    html = demo.read_text()
    html = re.sub(r'(<video[^>]*id="d-vid"[^>]*?data-duration=")[0-9.]+', lambda m: m.group(1) + f"{clip}", html)
    html = re.sub(r'(<video[^>]*id="d-vid"[^>]*?data-media-start=")[0-9.]+', lambda m: m.group(1) + f"{media_start}", html)
    demo.write_text(html)
    print(f"atelier clip: media {media_start} s on, {clip} s long")
vo_js = {"lead": LEAD, "end": END, "voiceEnd": round(end_voice, 3), "scenes": SCENES,
         "lines": [{k: v for k, v in L.items() if k != "heard"} for L in out_lines]}
(ROOT / "assets/cues.js").write_text(
    "// generated by tools/vo-build.py from SCRIPT.md and the voice take — do not edit by hand\n"
    f"window.VO = {json.dumps(vo_js, ensure_ascii=False)};\n"
    "window.CUES = { END: window.VO.end, L: window.VO.lines.map((l) => [l.start, l.end]), S: window.VO.scenes };\n"
    "// start / end of a line\n"
    "window.LS = (line) => window.VO.lines.find((x) => x.id === line).start;\n"
    "window.LE = (line) => window.VO.lines.find((x) => x.id === line).end;\n"
    "// time of the n-th word of a line whose letters match `word` (accents and punctuation ignored)\n"
    "window.W = function (line, word, n) {\n"
    "  const f = (s) => s.toLowerCase().normalize('NFD').replace(/[^a-z0-9]/g, '');\n"
    "  const l = window.VO.lines.find((x) => x.id === line);\n"
    "  const hits = l.words.filter((w) => f(w[0]) === f(word));\n"
    "  const h = hits[n || 0];\n"
    "  if (!h) throw new Error('cue: no word ' + word + ' in line ' + line);\n"
    "  return h[1];\n"
    "};\n")
print(f"cues.js written: END {END}")

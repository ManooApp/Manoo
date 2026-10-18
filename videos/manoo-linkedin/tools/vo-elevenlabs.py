#!/usr/bin/env python3
"""Voice-over lines from ElevenLabs — by default « Hugo » (voice DbbNuBL7lf62XwY7arQb: Paris, grave, made for ads).

One file per SCRIPT.md line, each requested with its neighbours as context so the tone carries from line to line:

  python3 tools/vo-elevenlabs.py                                  # → assets/audio/vo/elevenlabs/L01.wav … L19.wav
  python3 tools/vo-build.py --lines assets/audio/vo/elevenlabs    # timing, captions, scenes
  python3 tools/make-audio.py                                     # music and effects follow the new timing

The API key is read from the ELEVENLABS_API_KEY environment variable and only sent to api.elevenlabs.io, through
curl's stdin (never on a command line, never written to disk). Unchanged lines are not requested again
(manifest.json). A voice from the public Voice Library that the account does not hold yet is added to it first.
The text sent is the on-screen line with « Manoo » spelled « Manou » and « manoo.fr » read « manou point F R »;
`--text` prints it, one paragraph per line, for reading it on the ElevenLabs website instead (see tools/vo-split.py).
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.elevenlabs.io"

ap = argparse.ArgumentParser()
ap.add_argument("--voice", default="DbbNuBL7lf62XwY7arQb", help="ElevenLabs voice_id (default: Hugo)")
ap.add_argument("--library-search", default="Hugo", help="name to look the voice up by in the public Voice Library")
ap.add_argument("--model", default="eleven_multilingual_v2")
ap.add_argument("--out", type=Path, default=ROOT / "assets/audio/vo/elevenlabs")
ap.add_argument("--stability", type=float, default=0.5)
ap.add_argument("--similarity", type=float, default=0.8)
ap.add_argument("--style", type=float, default=0.15)
ap.add_argument("--speed", type=float, default=1.0)
ap.add_argument("--seed", type=int, default=2026)
ap.add_argument("--text", action="store_true", help="print the text to read and exit")
args = ap.parse_args()


def spoken(text):
    text = re.sub(r"manoo\.fr", "manou point F R", text, flags=re.I)
    return text.replace("Manoo", "Manou")


LINES = []
for m in re.finditer(r"^## Line (\d+)[^\n]*\n(.*?)(?=^## Line |\Z)", (ROOT / "SCRIPT.md").read_text(), flags=re.M | re.S):
    text = re.search(r"^    (\S.*)$", m.group(2), flags=re.M).group(1).strip()
    LINES.append({"id": int(m.group(1)), "say": spoken(text)})

if args.text:
    print("\n\n".join(L["say"] for L in LINES))
    sys.exit(0)

KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()
if not KEY:
    sys.exit("ELEVENLABS_API_KEY is not set: add it to the environment (a new session picks it up), "
             "or read the text on the ElevenLabs website and cut the take with tools/vo-split.py.")


def call(method, path, body=None, accept="application/json", out=None):
    """One API request through curl; returns (HTTP status, response bytes or None when written to `out`)."""
    with tempfile.TemporaryDirectory() as tmp:
        dst = out or Path(tmp) / "resp"
        cmd = ["curl", "-sS", "--max-time", "120", "-K", "-", "-X", method, "-o", str(dst), "-w", "%{http_code}", API + path]
        if body is not None:
            (Path(tmp) / "body.json").write_text(json.dumps(body, ensure_ascii=False))
            cmd += ["-H", "Content-Type: application/json", "--data-binary", f"@{Path(tmp) / 'body.json'}"]
        cfg = f'header = "xi-api-key: {KEY}"\nheader = "Accept: {accept}"\n'
        r = subprocess.run(cmd, input=cfg, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"curl failed ({r.returncode}): {r.stderr.strip()}")
        status = int(r.stdout.strip() or 0)
        data = None if out else dst.read_bytes()
        if out and status != 200:
            data = dst.read_bytes()
            dst.unlink()
        return status, data


def detail(data):
    """The API's error as « status: message » (falls back to the raw body)."""
    try:
        d = json.loads(data)["detail"]
        return f"{d.get('status', '')}: {d.get('message', '')}" if isinstance(d, dict) else str(d)
    except Exception:
        return (data or b"")[:300].decode("utf-8", "replace")


def add_from_library(voice_id):
    """Add a shared Voice Library voice to the account; returns the voice_id to use for speech."""
    owner = None
    for page in range(5):
        st, data = call("GET", f"/v1/shared-voices?page_size=100&page={page}&search={args.library_search}")
        if st != 200:
            sys.exit(f"Voice Library search refused ({st}): {detail(data)}")
        d = json.loads(data)
        owner = next((v["public_owner_id"] for v in d.get("voices", []) if v.get("voice_id") == voice_id), None)
        if owner or not d.get("has_more"):
            break
    if not owner:
        sys.exit(f"voice {voice_id} not found in the Voice Library under « {args.library_search} »: "
                 "add it to « My Voices » on the ElevenLabs website, then run this again")
    st, data = call("POST", f"/v1/voices/add/{owner}/{voice_id}", {"new_name": f"{args.library_search} (Manoo)"})
    if st != 200:
        sys.exit(f"adding the voice to the account was refused ({st}): {detail(data)}")
    vid = json.loads(data)["voice_id"]
    print(f"voice added to the account as {vid}")
    return vid


args.out.mkdir(parents=True, exist_ok=True)
manifest_p = args.out / "manifest.json"
manifest = json.loads(manifest_p.read_text()) if manifest_p.exists() else {}
settings = {"stability": args.stability, "similarity_boost": args.similarity, "style": args.style,
            "use_speaker_boost": True, "speed": args.speed}
voice = manifest.get("_voice_in_account", {}).get(args.voice, args.voice)
chars = 0
for i, L in enumerate(LINES):
    name = f"L{L['id']:02d}.wav"
    body = {"text": L["say"], "model_id": args.model, "voice_settings": settings, "seed": args.seed}
    if args.model != "eleven_v3":  # request stitching: the neighbouring lines set the intonation
        if i > 0:
            body["previous_text"] = LINES[i - 1]["say"]
        if i + 1 < len(LINES):
            body["next_text"] = LINES[i + 1]["say"]
    if args.model in ("eleven_turbo_v2_5", "eleven_flash_v2_5"):
        body["language_code"] = "fr"
    key = hashlib.sha1(json.dumps([args.voice, body], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if (args.out / name).exists() and manifest.get(name) == key:
        continue
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = Path(tmp) / "line.mp3"
        for attempt in range(2):
            st, data = call("POST", f"/v1/text-to-speech/{voice}?output_format=mp3_44100_128", body, "audio/mpeg", mp3)
            if st == 200:
                break
            msg = detail(data)
            if attempt == 0 and st in (400, 404) and "not_found" in msg.replace(" ", "_").lower():
                voice = add_from_library(args.voice)
                manifest.setdefault("_voice_in_account", {})[args.voice] = voice
                continue
            hint = {401: "key refused", 402: "plan or quota", 403: "key without text-to-speech permission",
                    429: "rate limit or quota"}.get(st, "")
            sys.exit(f"{name}: ElevenLabs answered {st} {hint}: {msg}")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ac", "1", "-ar", "48000", str(args.out / name)],
                       check=True)
    chars += len(L["say"])
    manifest[name] = key
    manifest_p.write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    print(f"  {name}  {L['say']}")
print(f"{len(LINES)} lines in {args.out.relative_to(ROOT)} ({chars} characters requested this run)")
print(f"next: python3 tools/vo-build.py --lines {args.out.relative_to(ROOT)} && python3 tools/make-audio.py")

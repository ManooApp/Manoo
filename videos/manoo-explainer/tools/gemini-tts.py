#!/usr/bin/env python3
"""Fallback Gemini voice generation (generateContent, prebuilt voices) when the media-use audio engine is missing.

    python3 tools/gemini-tts.py                         # the seven lines of audio_request.json -> assets/voice/LN.wav
    python3 tools/gemini-tts.py --voice Algieba         # another prebuilt voice
    python3 tools/gemini-tts.py --sample Charon Algieba Achird Iapetus   # line 1 in several voices, to choose

Reads the key from GEMINI_API_KEY or GOOGLE_API_KEY (set as an environment secret, never in a file).
Default model: gemini-2.5-pro-preview-tts, which returns mono 16-bit PCM at 24 kHz; it is wrapped as WAV.
The preferred route is the media-use engine (VOIX.md); this script exists so the work never blocks on it.
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
req = json.loads((ROOT / "audio_request.json").read_text())

ap = argparse.ArgumentParser()
ap.add_argument("--voice", default=req.get("voice", "Charon"))
ap.add_argument("--model", default="gemini-2.5-pro-preview-tts")
ap.add_argument("--out", default="assets/voice")
ap.add_argument("--sample", nargs="*", help="voices to try on line 1 (writes assets/voice/sample-<voice>.wav)")
args = ap.parse_args()

key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not key:
    sys.exit("No GEMINI_API_KEY / GOOGLE_API_KEY in the environment (add it as an environment secret, then start a new session).")


def speak(text, voice, style):
    body = {
        "contents": [{"parts": [{"text": f"{style}\n\n{text}"}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
        },
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{args.model}:generateContent"
    for attempt in range(4):
        r = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                   headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(r, timeout=180) as resp:
                data = json.loads(resp.read())
            part = data["candidates"][0]["content"]["parts"][0]["inlineData"]
            rate = int(part.get("mimeType", "rate=24000").split("rate=")[-1].split(";")[0] or 24000)
            return base64.b64decode(part["data"]), rate
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 503) and attempt < 3:
                time.sleep(2 ** (attempt + 2))
                continue
            sys.exit(f"Gemini error {e.code}: {msg}")


def save(pcm, rate, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    print(f"{path}  {len(pcm) / 2 / rate:.2f}s")


style = "Read the following French text aloud. " + req["style"]
out = ROOT / args.out
if args.sample:
    for v in args.sample:
        pcm, rate = speak(req["lines"][0]["text"], v, style)
        save(pcm, rate, out / f"sample-{v}.wav")
else:
    for line in req["lines"]:
        pcm, rate = speak(line["text"], args.voice, line.get("style", style))
        save(pcm, rate, out / f"{line['id']}.wav")

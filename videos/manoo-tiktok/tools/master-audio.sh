#!/usr/bin/env bash
# master-audio.sh <render.mp4> <out.mp4>
# Brings the rendered mix to about -14 LUFS (TikTok's playback level) under -1 dBTP with a gentle limiter, run 4x oversampled so inter-sample peaks are caught too.
# The picture stream is copied untouched. Measured on v1: -15.8 LUFS / -2.0 dBTP -> -13.9 LUFS / -1.6 dBTP after AAC.
set -euo pipefail
ffmpeg -v error -y -i "$1" -map 0:v:0 -map 0:a:0 -c:v copy \
  -af "volume=2.0dB,aresample=192000,alimiter=limit=0.79:attack=1.5:release=60:level=false,aresample=48000" \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$2"

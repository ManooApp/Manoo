#!/usr/bin/env bash
# master-audio.sh <render.mp4> <out.mp4>
# Brings the rendered mix to about -14 LUFS (LinkedIn / Instagram playback level) under -1 dBTP with a gentle limiter,
# run 4x oversampled so inter-sample peaks are caught too. The picture stream is copied untouched.
# GAIN_DB defaults to the gap measured on v1 (render -18.1 LUFS -> -14.0 LUFS, -1.8 dBTP after AAC); re-measure after a remix.
set -euo pipefail
GAIN_DB="${GAIN_DB:-4.3}"
ffmpeg -v error -y -i "$1" -map 0:v:0 -map 0:a:0 -c:v copy \
  -af "volume=${GAIN_DB}dB,aresample=192000,alimiter=limit=0.79:attack=1.5:release=60:level=false,aresample=48000" \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$2"

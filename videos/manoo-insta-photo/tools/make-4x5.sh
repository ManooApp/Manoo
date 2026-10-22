#!/usr/bin/env bash
# make-4x5.sh <master-9x16.mp4> <out-4x5.mp4>
# Instagram feed version (1080 × 1350) of the 9:16 master: the band y 260 → 1610, a plain crop since the film is on
# white. The phone's top, the island banner, the shutter close-up, the line and the logo all sit inside it.
# The audio stream (if any) is copied untouched.
set -euo pipefail
ffmpeg -v error -y -i "$1" -vf "crop=1080:1350:0:260,format=yuv420p" -map 0:v:0 -map 0:a:0? \
  -c:v libx264 -crf 16 -preset slow -profile:v high -c:a copy -movflags +faststart "$2"

#!/usr/bin/env bash
# make-4x5.sh <master-9x16.mp4> <out-4x5.mp4>
# Feed version (1080 × 1350) of the 9:16 master. The band y 255 → 1705 holds every caption and UI block (only the
# bezel of the demo phone bleeds); it is scaled to 1350 px high (93 %) and centred on a blurred, stretched copy of
# itself, so the 37 px side margins take the colour of whichever world (black or white) is on screen. The picture's
# left and right edges fade into that background over 28 px, so a card sliding off-canvas leaves no seam.
# The audio stream is copied untouched (run it on the mastered file).
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
ffmpeg -v error -y -f lavfi -i "color=c=white:s=1006x1350:d=1" -frames:v 1 \
  -vf "format=gray,geq=lum='255*clip(min(X\,W-1-X)/28\,0\,1)'" "$tmp/mask.png"
ffmpeg -v error -y -i "$1" -loop 1 -i "$tmp/mask.png" -filter_complex \
  "[0:v]crop=1080:1450:0:255,split=2[a][b];[a]scale=1006:1350:flags=lanczos,format=yuva444p[fg0];[1:v]format=gray[m];[fg0][m]alphamerge[fg];[b]scale=1080:1350,boxblur=40:3[bg];[bg][fg]overlay=(W-w)/2:0:shortest=1,format=yuv420p[v]" \
  -map "[v]" -map 0:a:0 -c:v libx264 -crf 17 -preset slow -profile:v high -c:a copy -shortest -movflags +faststart "$2"

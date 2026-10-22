#!/usr/bin/env bash
# make-planche.sh <film.mp4> <out.jpg> [cols]
# Contact sheet of the film's beats (times from the storyboard), each still stamped with its time.
set -euo pipefail
cols=${3:-5}
times=(0.12 0.9 1.3 1.9 2.15 2.7 3.02 3.33 3.6 4.2 5.0 6.2 7.5 9.4 11.5)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
w=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$1")
tw=$((w * 36 / 100))
i=0
for t in "${times[@]}"; do
  ffmpeg -v error -y -ss "$t" -i "$1" -frames:v 1 \
    -vf "scale=${tw}:-2,drawbox=x=0:y=0:w=118:h=40:color=black@0.55:t=fill,drawtext=text='${t} s':x=12:y=9:fontsize=24:fontcolor=white" \
    "$tmp/$(printf %02d $i).png"
  i=$((i + 1))
done
rows=$(( (i + cols - 1) / cols ))
ffmpeg -v error -y -pattern_type glob -i "$tmp/*.png" -vf "tile=${cols}x${rows}:padding=8:margin=8:color=0x1c1c1c" -frames:v 1 -q:v 3 "$2"

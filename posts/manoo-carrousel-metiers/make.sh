#!/usr/bin/env bash
# Builds the carousel: 2x screenshots (render.cjs), then exports/manoo-metiers-0N.png (1080 × 1350, Instagram)
# and exports/manoo-metiers-carrousel.pdf (one page per slide, for a LinkedIn document post).
set -euo pipefail
cd "$(dirname "$0")"
NODE_PATH="${NODE_PATH:-/opt/node-tools/node_modules}" node render.cjs
python3 - <<'PY'
from pathlib import Path
from PIL import Image
out = Path("exports")
pages = []
for src in sorted((out / "2x").glob("s*.png"), key=lambda p: int(p.stem[1:])):
    im = Image.open(src).convert("RGB").resize((1080, 1350), Image.LANCZOS)
    dst = out / f"manoo-metiers-{int(src.stem[1:]):02d}.png"
    im.save(dst, optimize=True)
    pages.append(im)
    print(dst, im.size)
pages[0].save(out / "manoo-metiers-carrousel.pdf", save_all=True, append_images=pages[1:], resolution=72)
print(out / "manoo-metiers-carrousel.pdf", len(pages), "pages")
PY

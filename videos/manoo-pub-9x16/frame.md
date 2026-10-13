---
version: 1
name: Manoo — Frame (pub 9:16)
description: >
  Frame-scale design system for the Manoo ad. Dark ink ground, one orange accent, paper as the
  only light surface, real matter (sparks, dust, flour) with film grain. Archivo for display,
  IBM Plex Mono for chrome. Tokens come from the founder's brief (2026-10-13), not from memory.
unit: the frame — 1080×1920 primary (9:16); 1920×1080 later
principle: un seul accent · la matière avant le décor · le produit est le cadre, pas le héros

colors:
  encre: "#101619"        # ground of every frame, text on paper
  papier: "#F3F2EF"       # light surface: the CV sheet, primary text on encre
  orange: "#F97316"       # the ONLY accent — sparks, the logotype dot, one focal per frame
  acier: "#78868F"        # secondary text, labels, struck-out words
  encre-2: "#182126"      # raised surface on encre (phone UI cards) — derived: encre +4% L
  hairline: "#2A3439"     # 1px rules on encre — derived from acier at low contrast

typography:
  display:  { fontFamily: "Archivo", weight: 800, tracking: "-0.035em", lineHeight: 0.92 }
  headline: { fontFamily: "Archivo", weight: 700, tracking: "-0.025em", lineHeight: 1.0 }
  body:     { fontFamily: "Archivo", weight: 500, tracking: "-0.005em", lineHeight: 1.3 }
  label:    { fontFamily: "IBM Plex Mono", weight: 500, tracking: "0.14em", upper: true }
  type-cv:  { fontFamily: "IBM Plex Mono", weight: 400, tracking: "0.02em" }   # the paper CV's typed lines
  ramp-cqw: { display: 15, headline: 9.5, body: 4.2, label: 2.6 }               # on a 1080-wide frame

spacing:
  pad-x: "7.4cqw"     # 80px
  pad-y: "7.4cqw"
  safe-top: "12cqh"   # keep clear of the TikTok/Reels top chrome
  safe-bottom: "20cqh" # captions + platform UI band — no key content below 80% height
  safe-right: "14cqw" # platform action rail

components:
  phone:
    body: "{colors.encre} with a 1px {colors.hairline} edge and a thin steel highlight; no glossy reflections"
    screen: "the real Manoo UI from captures — never redrawn from memory"
    placement: "centered, ~62% of frame height; it frames the work, it is never the hero"
  label:
    typography: "{typography.label}"
    color: "{colors.acier} (default) / {colors.orange} for the one live label"
    description: "Mono catalogue chrome: plate numbers, trade names, '2 ANS → 2 LIGNES'."
  plate:
    description: "Full-bleed macro of real work (photo) under grain + matter particles; label bottom-left in mono."
  logotype:
    description: "MANOO in Archivo 800 caps, tight tracking, followed by an orange dot — the dot is the film's last spark."
  grain:
    description: "Animated film grain over every frame (seeded, deterministic), ~6–9% opacity; slight vignette."
---

# Manoo — Frame

## Overview

The film is a documentary ad. Contrast does the work: **dark ink, raw matter, one orange spark**. The
paper CV is the only light object in the world — clean, empty, polite — and everything that matters
(the welding bead, the tile, the bread, the profile full of work) arrives as **matter with grain**.

## Rules

- **One accent.** Orange `#F97316` appears only as fire/sparks, the logotype dot and at most one live
  label per frame. The logo hammer is re-coloured from `#EA8A38` to `#F97316` (pending founder OK).
- **Encre is the ground of every frame.** Papier is a surface (the CV sheet, type), never a background.
- **Matter, not decoration.** Particles are physical: sparks fall with gravity and die, sawdust hangs
  in a light beam, flour drifts down. No floating bokeh, no glow orbs, no gradients.
- **Grain everywhere**, including on UI frames (lighter there), so the product sits in the same world.
- **Dry cuts.** Hard cuts on voice cues; the only "moves" are physical (the paper crumples, the hammer
  strikes). No soft crossfades, no slow drifting camera.
- **Type**: Archivo display tight and big, sentence case; IBM Plex Mono uppercase for chrome.
- **Safe zones (9:16 social):** key content between 12% and 80% of the height and clear of the right
  action rail.

## Do / Don't

- Do: macro, raking light, real textures, the phone steady at center.
- Don't: pastel or smooth plastic 3D, purple/blue "tech" gradients, gradient text, stock handshakes,
  cursor arrows, invented UI, any notification bell, chat bubble, map pin or "match %" badge.

---
name: manoo-linkedin
source: bespoke — the codes of the reference « Pulse » (Abdullah.A) carried onto Manoo's brand
canvas: "#070809"
---

# Manoo LinkedIn / Instagram — design system

Two worlds and one accent, exactly like the reference: a deep black stage where the story is told (problem, question,
reveal, ending) and a bright white stage where Manoo's interface floats in space (demo, community, companies). The
orange of Manoo is the only colour: it fills the key word's pill, glows behind the black scenes and rises from the
bottom of the white ones.

## Colors

| Role | Value | Use |
| --- | --- | --- |
| night | `#070809` | black world (scenes 1–5 and 10) |
| night-2 | `#121517` | cards and tiles on the black world |
| day | `#FAFAF8` | white world (scenes 6–9) |
| ink | `#0E1012` | text on the white world |
| snow | `#F5F4F1` | text on the black world |
| mute-dark | `#6B7378` | lead words on black (≥ 3:1 at display size) |
| mute-light | `#8A9297` | lead words on white (≥ 3:1 at display size) |
| accent | `#F97316` | ONE per moment: the key word's pill, glows, ripples, the cursor, the final pill |
| app | Manoo UI kit (`assets/ui/manoo-ui.css`, primary `#E36E2D`) | inside phones and cards only |

## Typography

- **Inter Display** 600 for every caption, letter-spacing −0.035 em, line-height 1.06; sentence case, no shouting.
- Caption size 84 px (two to four words per line, two lines max, three only when the voice lists).
- Key word: white Inter Display 700 inside an accent pill (radius 18, padding 2 × 20 px) — or accent-coloured text
  when a pill would crowd the line.
- Giant words (« Voici », the triad) 150–230 px, gradient snow → accent with a soft glow on black.
- UI keeps the kit's Inter sizes; phones and cards are scaled as objects.

## Captions (the reference's core mechanic)

- The caption is the voice's key phrase, revealed **word by word at the instant each word is spoken** (times from
  `assets/cues.js`, built by `tools/vo-build.py` from the take).
- Word in: opacity 0 → 1, blur 10 px → 0, y +0.22 em → 0, 0.22 s `power2.out`. Pill: background scales 0.6 → 1 and
  fades in with its first word; its words reveal inside it.
- Caption out: blur 10 px + opacity 0, 0.2 s, just before the next line.
- One typed line (the question) with a caret, like « But which video… ».

## Components

- **Floating card**: white, radius 28, shadow `0 40px 90px rgba(0,0,0,0.18)`; on black, a faint 1 px border
  `rgba(255,255,255,0.08)` and an accent halo behind.
- **Phone**: the kit's `.phone` scaled 1.3–1.5, soft drop shadow; tilts a few degrees in 3D and drifts.
- **Video card**: 16:9 footage in a radius-32 card (the atelier shot), like the reference's footage cards.
- **Node graph**: avatars of trades linked to the Manoo icon by drawn lines (the reference's « drag your sources »).
- **Ripple**: accent rings expanding from the centre; **bloom**: radial accent glow that turns into the white world.
- **Light beam**: a soft accent band sweeping across the logo to reveal the signature.

## Motion

- Slow push on every shot (scale 1 → 1.04 over the scene), UI floats with a slight perspective tilt.
- Entrances from blur and depth (scale 0.9 → 1, blur 14 → 0), `power3.out` 0.4–0.6 s; exits blur out 0.2–0.3 s.
- Taps: finger disc + accent ring; cursor clicks scale 0.86 yoyo.
- Cuts land in the silences between lines; nothing important changes while a word is being spoken.

## Layout (9:16 master, 4:5 inside)

- Canvas 1080 × 1920. All key content inside the band **y 255 → 1705** (captions start at y 330, the demo phone's
  bezel may bleed); the feed version scales that band to 1080 × 1350 over a blurred extension (tools/make-4x5.sh).
- Captions in the upper zone **y 330 → 640**, centred, 64 px side margins; UI and visuals in **y 660 → 1560**.
- Reels/Stories: nothing important right of x 990 or below y 1560.

---
name: manoo-tiktok
source: bespoke — adapted from the reference https://x.com/1600Agency/status/2092063895275888661 (taap.it film) onto Manoo's brand
canvas: "#FAFAF7"
---

# Manoo TikTok — design system

A clean product film on a bright stage, one accent, fast and precise. Everything is white paper and ink; the
orange of Manoo is the only colour and it is spent on the word, the tap or the slam that matters.

## Colors

| Role | Value | Use |
| --- | --- | --- |
| canvas | `#FAFAF7` | the stage (warm white), always with the grid |
| grid | `rgba(16, 22, 25, 0.05)` lines, 72 px | very faint, masked to the centre |
| ink | `#101619` | key words, wordmark, dark stage of the finale |
| mute | `#8A9297` | lead words of a two-tone line (lighter weight); darker than the reference grey so large text keeps 3:1 on the canvas |
| ghost | `#EEEDE9` | the giant word behind a section title |
| accent | `#F97316` | ONE per moment: a key letter or word, a toggle, a check, the slam, the address pill |
| dark | `#101619` + grid `rgba(243, 242, 239, 0.05)` | finale stage |
| app | the Manoo UI kit (`assets/ui/manoo-ui.css`, primary `#E36E2D`) | inside the phone only |

## Typography

- Display: **Inter Display** 800 / 700 for key words, letter-spacing −0.04 em.
- Lead: **Inter Display** 500 in `mute`, same size as the key word (two-tone line: « Des CV **partout…** »).
- Sizes (1080 × 1920): two-tone line 96 px · section title 64 px bold + ghost word 300 px · giant statement 330 px ·
  caption above the phone 46 px (step number in an orange disc) · labels 34 px.
- App UI keeps the kit's Inter sizes (the phone is scaled as one object).

## Components

- **Floating tile**: white rounded square (radius 36), soft shadow `0 24px 50px rgba(16,22,25,0.10)`, a Lucide icon
  in ink or accent; depth by scale + blur (far tiles 6–10 px blur).
- **Phone**: the kit's `.phone` (430 × 888) scaled 1.45–1.6, centred, soft drop shadow, no glow.
- **Cursor**: arrow with ink fill and white outline (finale: accent fill) · **finger tap**: white disc + accent ring.
- **Toggle**: pill 150 × 84, grey track → accent track, white knob slides on the click.
- **Section card**: small bold title (64 px) centred on a giant ghost word; toggle under it.
- **Split**: left half `ink` stage « Avant », right half canvas « Après · Manoo », one phone in each.
- **Statement**: giant word or symbol with one accent glyph, surrounded by a collage of réalisation cards that fly
  in with motion blur.
- **Check row**: three icons with labels, an accent check disc pops under each.
- **Address pill**: rounded pill outline on the dark stage, clicked by the accent cursor, fills with accent.

## Motion

- Everything lands on the 120 BPM grid (beat 0.5 s).
- Text in: blur 14 px → 0, y +30 → 0, opacity 0 → 1, `power3.out` 0.4 s, letters or words staggered 0.03–0.06 s.
- Text out: blur → 12 px, y −24, `power2.in` 0.25 s.
- Whip between scenes: x or y ±500 with blur 16 px, `power3.in` 0.3 s, the next scene enters with the mirror move.
- Pops: `back.out(1.8)`; taps: scale 0.94 yoyo 0.1 s + ring burst.
- No grain, no glow on the light stage; the finale may glow the accent pill.

## Layout (TikTok safe zones)

- Key text between y = 220 and y = 1450, centred; nothing important right of x = 960 or under y = 1500.
- Captions above the phone at y ≈ 250–330; the phone centred around y ≈ 1000.

---
version: 1
name: Manoo — Frame (pub isométrique 16:9)
description: >
  Frame-scale design system for the Manoo isometric ad. One continuous isometric world built like an
  architect's white model (maquette) floating in ink: paper and steel volumes, soft raking light, film grain.
  The only colour is orange, and orange means one thing: the work. Every réalisation (the gate, the brick
  wall, the cabinet) is orange; when it is photographed, the orange travels into the portfolio and out to
  the people who look at it. Tokens come from the Manoo site (manoo.fr CSS variables), not from memory.
unit: the frame — 1920×1080 (16:9)
principle: un seul accent = le travail · la maquette avant le décor · le regard comme lumière

colors:
  encre: "#101619"         # the void / page ground of every frame
  encre-2: "#1A242A"       # island slab sides, raised UI on ink
  filet-sombre: "#2C383F"  # island tops in shadow, hairlines on ink
  acier: "#78868F"         # secondary text, labels, steel volumes
  acier-clair: "#A8B4BB"   # lit steel, figurine clothes
  papier: "#F3F2EF"        # lit tops of the maquette, primary text on ink
  papier-2: "#E8E6E1"      # maquette side faces
  filet: "#D6D4CE"         # hairlines on paper
  orange: "#F97316"        # the ONLY accent — the réalisations, the light paths, the logotype dot
  orange-fonce: "#D95F08"  # shaded faces of orange volumes only
  derived:                 # tones derived from the palette for the 3D maquette, light and UI (not new hues)
    pierre: "#CFCCC5"      # concrete, mortar
    ombre: "#3A464D"       # dark steel parts, tools
    peau: "#D9CFC4"        # faceless figurine skin
    vitre: "#24323A"       # unlit glass ; lit glass glows "#F6E9D6" / "#F6E6CF"
    sol: "#DCD8D0"         # floor tint multiplied on the tile textures (#E4E4DF lawn, #F1EFEA path, #D9D9D9 asphalt)
    fond: ["#1B262D", "#141C21", "#0D1215"]  # radial ink background of the stage
    lumiere: ["#FFF6EC", "#F4F4F2"]          # key and fill light
    etincelle: ["#FFD9B8", "#FFD2A6", "#FFB070", "#FFB27A", "#FFFAF2"]  # weld spark, camera flash (orange family)
    ui-blanc: ["#FFFFFF", "#FBFAF8"]         # app cards and inputs, as drawn on manoo.fr
    noir-optique: "#0B0F12"                   # welding visor, lens glass

typography:
  display:  { fontFamily: "Archivo", weight: 800, tracking: "-0.035em", lineHeight: 0.95 }
  headline: { fontFamily: "Archivo", weight: 700, tracking: "-0.025em", lineHeight: 1.02 }
  body:     { fontFamily: "Archivo", weight: 500, tracking: "-0.005em", lineHeight: 1.3 }
  label:    { fontFamily: "IBM Plex Mono", weight: 500, tracking: "0.14em", upper: true }
  ramp-px:  { display: 112, headline: 72, body: 36, label: 24 }   # 16:9, in-feed safe (LinkedIn)

spacing:
  pad-x: "96px"
  pad-y: "84px"
  title-safe: "10% inset on every edge (192px × 108px)"

components:
  maquette:
    description: "Every building, tool and figurine is a matte model volume: papier tops, papier-2/acier sides, encre-2 slabs. Beveled edges, no textures except grain; soft key light from top-left + hemisphere fill; real shadows."
  realisation:
    description: "The work is the only orange object in its island: metallic-satin orange for the gate, orange bricks for the wall, orange wood for the cabinet (orange-fonce on shaded faces)."
  island:
    description: "A floating encre-2 slab (thick, beveled) with a filet-sombre/papier-2 top; each holds one place: atelier, chantier, atelier d'ébénisterie, entreprise, lycée pro, maison du client."
  phone:
    description: "The hub: a giant phone lying flat at the centre of the world; its screen carries the Manoo UI as drawn on manoo.fr (light UI, orange chips, 2-column réalisations grid, orange + button)."
  light-path:
    description: "An orange ribbon of light that travels on the ground from the phone to a place, then lights that place's screen. It is the regard, made visible."
  label:
    typography: "{typography.label}"
    color: "{colors.acier} by default, {colors.orange} for the chapter number"
    description: "Catalogue chrome like the site: '01 — CAPTURER', '02 — PUBLIER', '03 — ÊTRE VU'; place names anchored to islands."
  logotype:
    description: "MANOO in Archivo 800 caps, tight tracking, followed by an orange dot; with the hammer mark from the brief."
  grain:
    description: "Animated film grain over every frame (seeded, deterministic), ~7% opacity, plus a soft vignette."
---

# Manoo — Frame (isométrique)

## Overview

A premium, architectural film: a white model of the world of manual trades, lit like a maquette on a
drafting table at night. The world is calm and monochrome; **orange is the savoir-faire**. It starts as a
weld spark, becomes a gate, a wall, a cabinet; a camera flash captures it; it flies into the portfolio; then
it travels as light to the companies, the vocational schools and the clients, and finally becomes the dot of
the logotype.

## Rules

- **One accent, one meaning.** Orange is only the work (and the light that carries it). Never decoration.
- **One world.** The camera never cuts to another world: it travels, dives, tilts and pulls back across the
  same maquette. Whatever persists across a move must not jump.
- **Matte model, not plastic toy.** No pastel, no glossy toy shading, no gradients on volumes; beveled edges,
  real shadows, grain on top.
- **Type sits on ink, not on the model.** Headlines live in the title-safe area over the void, left-anchored
  or bottom-anchored; labels anchor to islands in mono.
- **Product truth.** The phone shows only real features: profile (photo, métier, formation), « Ajouter au
  portfolio » (une photo + un titre), the réalisations gallery seen by companies. No notification, chat, map
  pin, matching or score.

## Do / Don't

- Do: raking light, long soft shadows, decisive camera legs (power4.out landings, power3.inOut whips with
  horizontal motion blur), words that pop with a blur-in, glossy white icon bubbles (after the reference).
- Glow is orange only and only where light is the story: weld spark, camera flash ring, light paths, the
  orange edge of a seen réalisation, the logotype dot.
- Don't: neon / cyan / purple glows, blue tech gradients, gradient text, cursor arrows (taps are halos),
  stock handshakes, fake logos of real companies or schools.

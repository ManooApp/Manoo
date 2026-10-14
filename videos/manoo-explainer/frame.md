---
version: 1
name: Manoo — Frame (pub explicative 16:9)
description: >
  Frame-scale design system for the Manoo explainer. Dark SaaS motion-graphics stage (ink gradient, slow
  orange aurora light, glossy glass bubbles) on which the REAL Manoo app lives: light UI rebuilt from
  manoo.fr (orange gradient header, white rounded cards, Inter, orange pills, coloured profile tiles),
  shown on a 3D-tilted phone for the young pro and a desktop browser for the company. Orange is the only
  accent on the stage; inside the app, the app's own palette rules. Bespoke spec (no shipped preset fits
  the dark-glow reference the user sent); tokens come from manoo.fr CSS and the user's brand notes.
unit: the frame — 1920×1080 (16:9)
principle: l'app réelle au centre · un seul accent orange sur scène · chaque mot de la voix a son geste

colors:
  encre: "#101619"          # stage ground (brand ink)
  encre-2: "#172128"        # raised stage surfaces, glass base
  encre-3: "#0B1013"        # stage vignette edge
  filet: "#2A363D"          # hairlines / orbit rings on ink
  papier: "#F3F2EF"         # primary text on ink
  acier: "#A8B4BB"          # secondary text on ink (AA on encre)
  orange: "#F97316"         # the ONLY stage accent: highlight words, glows, rings, logotype dot
  orange-clair: "#FFB27A"   # glow cores, spark highlights
  app:                      # manoo.fr UI palette (computed from its Tailwind oklch tokens)
    header-top: "#E4702E"
    header-bottom: "#FD8B3A"
    primary: "#E36E2D"      # buttons « Créer une publication », « Publier »
    primary-strong: "#C15729" # « Choisir → » links, chip text
    chip-bg: "#FFF6EC"
    chip-text: "#9B4325"
    canvas: "#FCFAF7"
    canvas-glow: "#FDF3E9"
    card: "#FFFFFF"
    border: "#ECE7E1"
    input-border: "#DCD5CC"
    text: "#1E1813"
    text-strong: "#0E0A07"
    text-muted: "#807368"
    text-soft: "#5D5248"
    avatar-bg: "#F3F1EE"
    black-button: "#0E0A07"
    tile-artisan: "#FF6B35"
    tile-etudiant: "#4ECDC4"
    tile-entreprise: "#45B7D1"
    tile-ecole: "#96CEB4"
    success: "#16A34A"

typography:
  display:  { fontFamily: "Inter Display", weight: 800, tracking: "-0.035em", lineHeight: 0.98 }
  headline: { fontFamily: "Inter Display", weight: 700, tracking: "-0.03em", lineHeight: 1.04 }
  body:     { fontFamily: "Inter", weight: 500, tracking: "-0.01em", lineHeight: 1.35 }
  label:    { fontFamily: "Inter", weight: 600, tracking: "0.16em", upper: true }
  ui:       { fontFamily: "Inter", weights: [400, 500, 600, 700], note: "the app's own font stack resolves to Inter" }
  ramp-px:  { display: 120, headline: 76, body: 34, label: 22 }

spacing:
  pad-x: "120px"
  pad-y: "96px"
  title-safe: "10% inset on every edge (192px × 108px)"

components:
  stage:
    description: "Radial ink ground (#1B262D centre → #101619 → #0B1013 edge), 2–3 huge blurred orange light blobs drifting slowly (aurora), optional faint grid, animated grain + vignette on top of everything."
  headline:
    typography: "{typography.headline} / {typography.display}"
    description: "Two-tone kinetic type: papier words with one orange highlight phrase. Words pop in from blur (scale 0.92→1, blur 14→0) on the voice beat; lines swap fast (reference: Pinterest SaaS explainer)."
  bubble:
    description: "Glossy glass sphere (radial gradients + top-left specular + rim light + soft glow) holding a line icon (Lucide). Orange glass for the work and Manoo, white glass for trades/people. Orbit on thin concentric rings."
  phone:
    description: "Modern phone, dark titanium frame, 390×844 logical screen scaled ~1.7×, dynamic island, iOS status bar; 3D tilt with perspective, soft long shadow + orange rim glow. Screen = real Manoo UI."
  browser:
    description: "Desktop browser window (traffic lights, URL pill manoo.fr/…), 3D-tilted like the reference dashboards, orange glow edge; desktop Manoo layout (orange header + centered white cards)."
  app-ui:
    description: "Rebuilt from manoo.fr: orange gradient header with the hammer icon in a white rounded square + 'Manoo'; search field 'Mots-clés, tags, contenu...'; white cards radius 28px with #ECE7E1 border; post = avatar tile, name, 'Métier • il y a…', type chip (Réalisation hammer / Emploi briefcase) on #FFF6EC, photo radius 16px, actions ♥ 💬 ↗; bottom nav Feed · Recherche · Messages · Notifs · Profil."
  tap:
    description: "Touch / click feedback: element squash 0.94, orange ring halo expanding, small dot burst (reference ring VFX). Desktop uses a white cursor arrow."
  pop-out:
    description: "A UI element lifts out of its screen (z, scale 1.15–1.4, deeper shadow, orange rim) to be read, then settles back."
  logotype:
    description: "Hammer app icon in white rounded square + MANOO in Inter Display 800 caps followed by an orange dot."
---

# Manoo — Frame (explicatif)

## Overview

Un film explicatif « SaaS » premium, dans le langage de la référence Pinterest envoyée par l'utilisateur :
scène sombre en dégradé avec lumière orange qui respire, typographie cinétique bicolore, bulles de verre
brillantes en orbite, interface inclinée en 3D, zooms et clics, URL tapée en fin de film. La différence : ce
qui est montré est l'app Manoo réelle, reconstruite écran par écran depuis manoo.fr, claire et chaleureuse,
posée sur la scène sombre. Le jeune pro vit sur un téléphone, l'entreprise sur un navigateur.

## Rules

- Un seul accent sur scène : l'orange. Les couleurs des tuiles de profils n'existent qu'à l'intérieur de l'UI.
- Textes de l'UI = textes réels de l'app (« Votre feed », « Créer une publication », « Ajouter au portfolio »,
  « Trouvez les publications qui comptent », « Type de post », « Métier », « Envoyer un message », « Suivre » /
  « Abonné », « Dispo immédiate », « Carte d'identité métier »…). Contenus (noms, titres) fictifs.
- Chaque phrase de la voix déclenche un geste visible ; pas de plan figé de plus de ~1,5 s.
- Titres dans le cadre « title-safe » ; l'UI peut déborder du cadre pendant les zooms.
- Contraste : texte papier sur encre ; sur l'orange, texte encre.

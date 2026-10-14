---
format: 1920x1080
duration: 55.5s
message: "Manoo est le réseau social des métiers manuels : on y montre son travail en photos dans un portfolio, et les entreprises le découvrent et vous contactent, sans CV."
arc: Accroche → Ce qu'est Manoo → Pour qui → Côté jeune pro → Côté entreprise → Le travail parle → Signature
audience: jeunes pros, apprentis, artisans ; entreprises qui recrutent ; écoles et CFA
mode: autonomous
reference: https://pin.it/744ojryHD (pub SaaS « Motion graphic explainer », TaskIP) + https://lnkd.in/p/eUZXdW26
music: bed procédural lumineux ~118 BPM (pulsation, pluck, nappe) + sound design UI (taps, whooshs, déclencheur, notification)
version: v1
---

# Storyboard v1 — Manoo, « Le travail parle »

Ce film explique en 55 s ce qu'est Manoo, à qui il sert et comment il marche, en suivant une réalisation de
bout en bout : Jules photographie son portail, le publie, et un atelier le découvre et lui écrit.

## Decisions

- **Route** product-launch-video, mode autonome. Système de design sur mesure (frame.md) : aucun preset livré ne
  correspond à la scène sombre et lumineuse de la référence. Les frames sont construites par l'orchestrateur en
  une passe (pas de workers parallèles) parce que le téléphone, l'UI et la lumière continuent d'une frame à
  l'autre : une seule main garde le monde cohérent.
- **L'app réelle** : chaque écran est reconstruit en HTML depuis manoo.fr (textes, couleurs, rayons, icônes),
  contenus fictifs (Jules Moreau, Atelier Morvan).
- **Terrain** : un plan 3D court (maquette de l'atelier, même kit que le film isométrique) montre Jules
  photographier son portail ; rendu à part en vidéo (shots/atelier) puis posé dans une carte lumineuse.
- **Calques** : fond (compositions/bg.html) → frames (compositions/frames/0N-*.html) → finition grain/vignette
  (compositions/finish.html). Audio : 7 clips voix (groupe voiceover), bed musical creusé sous la voix, piste SFX.
- **Cues** : assets/cues.js (généré par tools/make-cues.py depuis les temps DTW de whisper) ; chaque frame cale
  ses gestes sur les mots.

- **Couche « téléphone de Jules »** (compositions/device.html, 7.6–47.5 s) : le même téléphone traverse les
  séquences 2 à 6 (feed → portfolio → accueil → inscription → profil → « Ajouter au portfolio » → « Créer une
  publication » → feed → notification). Les éléments qui « sortent » de l'écran (vignettes, cartes de profils,
  carte de Jules, photo, publication, grande notification) vivent dans cette couche, au-dessus des scènes.

## Video direction

- **Rythme** : un geste par mot clé, plans de 1 à 2 s comme la référence ; seules les fins de phrases respirent.
- **Caméra** : l'UI est filmée comme un objet 3D (perspective 1800px) — bascules, poussées vers un bouton,
  sorties d'éléments (pop-out). `power3.out` / `expo.out` pour les arrivées, `power2.inOut` pour les trajets.
- **Typo** : Inter Display, bicolore papier + orange, apparition depuis le flou ; balayage rapide entre lignes.
- **Lumière** : aurore orange lente derrière tout ; halos orange sur les taps ; grain + vignette sur tout le film.

## Frame 1 — Accroche (0.0–7.95s)

- scene: Lumière orange qui s'ouvre ; « Bâtiment · Artisanat · Industrie » en bulles brillantes ; un CV papier apparaît et tombe ; trois photos de réalisations le remplacent : « Il se voit sur le terrain. »
- duration: 7.95s
- transition_in: cut
- status: animated
- src: compositions/frames/01-accroche.html
- voiceover: "Dans le bâtiment, l'artisanat ou l'industrie, le talent ne tient pas sur un CV. Il se voit sur le terrain."
- asset_candidates: assets/photos/A0.jpg, assets/photos/B0.jpg, assets/photos/C0.jpg
- blueprint: kinetic-type-beats

0.0–0.9 aurore qui s'allume · 0.97 / 1.67 / 2.58 trois bulles (briques, marteau, engrenage) + mots ·
3.2–5.0 les bulles s'écartent, CV papier au centre, « Le talent ne tient pas sur un CV. » · 5.03 le CV est barré
et chute · 5.4–7.9 trois photos de réalisations en 3D + « Il se voit sur le terrain. » (« terrain » orange) ·
7.6 les photos convergent vers un orbe orange (handoff F2).

## Frame 2 — Ce qu'est Manoo (7.95–14.95s)

- scene: L'orbe porte l'icône Manoo et MANOO. ; il s'ouvre sur un téléphone incliné (le feed réel) entouré de bulles de métiers en orbite ; « Le réseau social des métiers manuels » puis « Un portfolio numérique pour montrer son savoir-faire » sur la grille portfolio.
- duration: 7.0s
- transition_in: continuous (orb handoff)
- status: animated
- src: compositions/frames/02-manoo.html
- voiceover: "Manou, c'est le réseau social des métiers manuels : un portfolio numérique pour montrer son savoir-faire."
- asset_candidates: assets/brand/manoo-marteau.png, assets/photos/*
- blueprint: logo-assemble-lockup → constellation-hub → device-surface-showcase

8.23 icône + MANOO. dans l'orbe · 9.33 l'orbe devient portail, téléphone (feed) · 9.8–10.6 titre bicolore +
bulles de métiers en orbite · 11.83 l'écran passe au portfolio · 13.25 les vignettes sortent de l'écran.

## Frame 3 — Pour qui (14.95–22.45s)

- scene: Écran « Bienvenue sur Manoo » ; les quatre cartes de profils sortent du téléphone sur chaque mot (Artisan, Étudiant / Apprenti, Entreprise, École / CFA) ; puis l'inscription en 3 étapes défile.
- duration: 7.5s
- transition_in: continuous (same phone)
- status: animated
- src: compositions/frames/03-profils.html
- voiceover: "Artisans, apprentis, entreprises, écoles et CFA : chacun y crée son profil."
- asset_candidates: none (UI)
- blueprint: device-surface-showcase (pop-out cards)

15.21 / 16.19 / 16.97 / 17.85 cartes qui sortent (artisan, apprenti, entreprise, école/CFA) · 18.69 « CFA » ·
19.85–21.4 étapes 1/3 → 2/3 → 3/3 · 21.9 profil de Jules prêt.

## Frame 4 — Côté jeune pro (22.45–32.85s)

- scene: Carte de profil de Jules ; plan 3D de l'atelier (il photographie son portail, flash) ; la photo vole dans le téléphone : « Ajouter au portfolio », titre tapé, ajouté ; « Créer une publication » → Publier ; la publication rayonne vers le réseau (avatars en orbite).
- duration: 10.4s
- transition_in: cut
- status: animated
- src: compositions/frames/04-jeune-pro.html
- voiceover: "Jules, apprenti métallier, termine un portail. Il le prend en photo, l'ajoute à son portfolio… et le partage avec tout le réseau."
- asset_candidates: assets/video/atelier.mp4, assets/photos/jules-portail.jpg
- blueprint: device-surface-showcase + constellation-hub

22.69 carte Jules · 23.5–23.9 puces « Étudiant / Apprenti » « Serrurier / Métallier » · 24.6 plan atelier ·
27.03 flash · 27.2–30.1 repère à gauche « La photo → Le portfolio → Le réseau » · 27.7–28.7 Ajouter au
portfolio (photo, titre, tap, 4/5 médias) · 29.0–30.4 Créer une publication,
Publier, toast · 30.4–32.8 la publication au centre, le réseau s'allume autour (avatars, ♥, 💬).

## Frame 5 — Côté entreprise (32.85–43.05s)

- scene: Navigateur incliné (manoo.fr/search, compte Atelier Morvan) : filtres Métier « Serrurier / Métallier » et ville « Rennes », résultats, la carte de Jules sort de la liste, profil + portfolio, Suivre → Abonné, message envoyé.
- duration: 10.2s
- transition_in: whip
- status: animated
- src: compositions/frames/05-entreprise.html
- voiceover: "Côté entreprise, un atelier cherche un métallier près de Rennes. Il filtre par métier, découvre le portail de Jules… et lui écrit directement."
- asset_candidates: assets/photos/jules-portail.jpg, assets/photos/garde-corps.jpg, assets/photos/banc.jpg
- blueprint: device-surface-showcase (browser tour) + pop-out row

32.98 fenêtre + « CÔTÉ ENTREPRISE » · 34.4–36.1 Métier choisi, « Rennes » tapé · 37.2–37.9 résultats ·
38.6–39.8 la carte de Jules sort, clic, profil · 40.3 Suivre → Abonné · 40.9–42.6 message tapé et envoyé.

## Frame 6 — Le travail parle (43.05–47.15s)

- scene: Le téléphone de Jules reçoit « Nouveau message · Atelier Morvan » ; « Pas besoin de CV. » (CV barré) ; « Son travail a parlé pour lui. »
- duration: 4.1s
- transition_in: whip
- status: animated
- src: compositions/frames/06-travail.html
- voiceover: "Pas besoin de CV : son travail a parlé pour lui."
- asset_candidates: assets/photos/jules-portail.jpg
- blueprint: kinetic-type-beats

43.1 notification + anneau, 43.3 la notification sort du téléphone en grand (message de l'Atelier Morvan) ·
43.99 « CV » barré · 44.45 « Atelier Morvan vous suit » · 45.09 « Son travail a parlé pour lui. »

## Frame 7 — Signature (47.15–55.5s)

- scene: Orbe + icône + MANOO. ; « La révolution du regard. » ; quatre puces de publics ; URL « manoo.fr » tapée dans une pastille lumineuse ; bouton « Créer mon compte ».
- duration: 8.35s
- transition_in: continuous
- status: animated
- src: compositions/frames/07-signature.html
- voiceover: "Manou. La révolution du regard. Rejoignez le réseau sur manou point F R."
- asset_candidates: assets/brand/manoo-marteau.png
- blueprint: logo-assemble-lockup

47.45 logo · 48.41 slogan · 50.25 publics · 51.49 URL tapée · 52.4 Créer mon compte (tap) · tenue jusqu'à 55.5.

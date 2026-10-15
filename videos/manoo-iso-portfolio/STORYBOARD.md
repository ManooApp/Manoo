---
format: 1920x1080
duration: 45s
message: "Avec Manoo, chaque réalisation devient une preuve en images : le savoir-faire se montre, et les entreprises, les lycées pros et les clients le voient."
arc: Manifeste → Capturer → Publier → Être vu → La preuve → Signature
audience: décideurs des entreprises et des établissements de formation (LinkedIn, site, rendez-vous)
mode: autonomous
reference: https://lnkd.in/p/eUZXdW26 (InVideo AI concept ad, Rajwadi Motions)
music: bed procédural discret (pulsation chaude ~96 BPM) + sound design de matière (soudure, déclencheur, souffles, lumière)
version: v2
---

# Storyboard v1 — Manoo, « Le savoir-faire se montre »

Ce film dit aux décideurs des entreprises et des établissements de formation qu'avec Manoo, chaque
réalisation devient une preuve en images, vue par ceux qui recrutent, forment et choisissent.

## Decisions

- **Un seul monde isométrique** (Three.js, caméra orthographique) : une maquette blanche flottant dans l'encre.
  Six îlots autour d'un téléphone géant : à gauche les trois métiers (métallerie, chantier, ébénisterie), à
  droite les trois publics (entreprise, lycée pro, client). La caméra voyage, plonge, bascule et recule ; elle ne
  coupe jamais vers un autre monde.
- **Fil conducteur (spine)** : l'orange = le travail. Étincelle de soudure → portail orange → flash → carte photo →
  portfolio → ruban de lumière vers chaque public → point orange du logotype.
- **Calque monde** : `compositions/world.html` (canvas WebGL + étiquettes ancrées aux îlots), toute la durée.
  **Calques texte** : un sous-composition par chapitre (`compositions/frames/0N-*.html`).
- **Vérité produit** : l'écran du téléphone reprend l'app telle que manoo.fr la dessine (« Mes réalisations »,
  grille 2 colonnes, bouton + orange, « Ajouter au portfolio » = une photo + un titre). Aucun « validé », score,
  notification, messagerie, carte ou matching.
- **Voix** : témoin locale pour le montage ; voix premium après validation du texte (SCRIPT.md).

## Video direction

- **Rythme** : ouverture serrée et lente (macro de soudure) → trois flashs coupés sur les mots → plongée qui
  aplatit le monde sur l'écran → trois rubans de lumière, un par public → grand recul tenu → plongée finale dans
  le téléphone qui devient la carte de fin.
- **Lois de caméra** : `power4.out` sur les plongées et atterrissages, `power2.inOut` sur les déplacements ; une
  micro-dérive sinusoïdale permanente pour que les plans tenus restent vivants.
- **Matière** : grain animé + vignettage sur tout le film ; étincelles et flashs en lumière réelle (3D).

## Round 2 — 2026-10-13 · alignement sur la référence

- L'utilisateur impose un rendu « comme celui-ci » (lien LinkedIn ci-dessus). Le film garde le monde
  isométrique mais adopte le langage de la référence : typo cinétique floutée qui « pop », carré blanc qui
  s'ouvre en portail, viseur + flash + anneau lumineux, panoramiques fouettés avec flou de mouvement, téléphone 3D
  entouré d'icônes brillantes, interface « Ajouter au portfolio » qui se monte (photo, titre tapé avec lueur,
  puces, appui avec halo), frise carrière façon timeline de montage, logo final avec icône d'app.
- Voix : Holden (choix de l'utilisateur), prise 1 découpée en 6 phrases (assets/cues.js = la feuille de temps).
- Frames 2 et 4 vivent dans le calque monde (compositions/world.html) : leurs étiquettes suivent la caméra.

## Round 3 — 2026-10-13 · rendu v2

- Rendu complet `renders/manoo-iso-v2.mp4` (45,0 s, 1920×1080, 30 i/s, −15 LUFS) + aperçu web
  `renders/manoo-iso-v2-apercu.mp4` (24,5 Mo) envoyé à l'utilisateur pour validation.
- `hyperframes check` : 0 erreur sur toutes les tranches (contrôle par plages, le monde 3D est trop lourd
  pour une passe unique dans le délai du check).

## Frame 1 — Manifeste (0.0–4.6s, ~4.6s)

- scene: Noir. Un arc de soudure s'allume en macro ; gerbe d'étincelles. La lumière monte, la caméra recule en continu et révèle l'atelier de métallerie, îlot flottant dans l'encre, et le portail orange.
- duration: 4.6s
- transition_in: cut
- status: built
- src: compositions/frames/01-manifeste.html
- voiceover: "Le savoir-faire ne se raconte pas. Il se montre."
- type: hook
- blueprint: zoom-out-workspace-reveal (Adapt — macro de l'arc → îlot entier) + kinetic-type-beats (texte)

## Frame 2 — Capturer (4.6–14.2s, ~9.6s)

- scene: Le métallier relève son masque, cadre le portail avec son téléphone : flash. La caméra glisse vers le chantier (flash sur le mur de briques) puis vers l'atelier d'ébénisterie (flash sur la commode). Chaque flash éjecte une carte photo.
- duration: 9.6s
- transition_in: continuous camera
- status: built
- src: compositions/world.html
- voiceover: "Avec Manoo, artisans et apprentis photographient leurs réalisations : une pièce de métallerie, un chantier, un ouvrage d'artisanat."
- type: feature_showcase
- blueprint: spatial-pan-stations (Adapt — trois stations, flash sur chaque mot)

## Frame 3 — Publier (14.2–20.0s, ~5.8s)

- scene: Les trois cartes s'envolent vers le centre où le téléphone géant se lève ; la caméra plonge et bascule à la verticale : l'écran remplit le cadre. « Ajouter au portfolio » : la photo, le titre qui se tape, l'appui ; puis les galeries des trois profils reçoivent leur réalisation.
- duration: 5.8s
- transition_in: continuous camera (tilt-to-flatten)
- status: built
- src: compositions/frames/03-publier.html
- voiceover: "Une photo, un titre : chaque réalisation rejoint leur portfolio visuel."
- type: product_intro
- blueprint: camera-journey (B — plongée + aplatissement) + device-surface-showcase (stepwise flow)

## Frame 4 — Être vu (20.0–30.2s, ~10.2s)

- scene: Recul et retour à l'isométrie : trois rubans de lumière partent du téléphone vers l'entreprise, le lycée pro et la maison du client ; chaque lieu s'éclaire et affiche la réalisation sur son écran, regardée par des figurines.
- duration: 10.2s
- transition_in: continuous camera
- status: built
- src: compositions/world.html
- voiceover: "Leur travail est enfin vu par ceux qui comptent : les entreprises qui recrutent, les lycées professionnels qui forment, les clients qui choisissent."
- type: benefit_highlight
- blueprint: constellation-hub (Adapt — le téléphone au centre, trois satellites qui s'allument)

## Frame 5 — La preuve (30.2–36.3s, ~6.1s)

- scene: Grand recul : tout le monde est visible et relié, métiers à gauche, publics à droite. Plan tenu, dérive lente.
- duration: 6.1s
- transition_in: continuous camera
- status: built
- src: compositions/frames/05-preuve.html
- voiceover: "Chaque réalisation devient une preuve. Une trace qui les suit toute leur carrière."
- type: benefit_highlight
- blueprint: zoom-out-workspace-reveal (payoff d'échelle) + kinetic-type-beats

## Frame 6 — Signature (36.3–45.0s, ~8.7s)

- scene: La caméra plonge dans le téléphone central ; l'écran devient la carte de fin : MANOO. (point orange), « La révolution du regard. », « Demandez une présentation — manoo.fr ».
- duration: 8.7s
- transition_in: continuous camera (dive)
- status: built
- src: compositions/frames/06-signature.html
- voiceover: "Manoo. La révolution du regard. Demandez une présentation sur manoo.fr."
- type: cta
- blueprint: logo-assemble-lockup (Adapt — le point orange atterrit en dernier)

## Rounds

- **v3 (test de voix)** — voix Grady (Higgsfield, Eleven v4 Turbo) à la place de Holden, texte inchangé.
  `tools/revoice.py` découpe la prise en six clips posés aux mêmes créneaux et place chaque repère sur le même mot
  (temps DTW de whisper) ; les gestes entre les mots gardent leur écart au mot voisin. Musique et bruitages
  régénérés sur les nouveaux repères, creusement de la musique relâché vite entre les phrases et remontée de
  +5 dB sur le plan final (`tools/fix-carve.py`). CLI épinglé 0.8.153 → 0.8.162. Le `check` passe sur 0–7,5 s et
  22,5–45 s ; entre 7,5 et 22,5 s il dépasse son délai (monde 3D en rendu logiciel, déjà le cas avant, aussi en
  0.8.153), ces scènes sont vérifiées sur les images du rendu. La prise Grady sortait à -25,5 LUFS : elle est
  ramenée à -16 LUFS (limiteur à -1,5 dBFS) avant découpe ; film rendu à -15,9 LUFS, crête -1,5 dBTP
  (`renders/manoo-iso-v3-grady.mp4`, non versionné). Rendu avec `PRODUCER_PLAYER_READY_TIMEOUT_MS=300000` et
  2 navigateurs : le monde 3D met plus de 45 s à s'initialiser sur cette machine.

---
workflow: general-video
flow: automation
storyboard: no
message: "Avec Manoo, chaque réalisation devient une preuve en images : le savoir-faire se montre, et les entreprises, les lycées pros et les clients le voient."
destination: linkedin-site-presentations
aspect: 1920x1080
language: fr
audience: "Décideurs des entreprises (artisans, PME du BTP et de l'industrie) et des établissements de formation (lycées professionnels, CFA) ; vidéo vitrine pour LinkedIn, le site et les rendez-vous de présentation."
length: 45s
angle: "Un seul monde isométrique continu : la caméra suit une réalisation, de l'établi au portfolio, puis jusqu'au regard de ceux qui recrutent, forment et choisissent."
narration: yes
voice: "Holden (Higgsfield · text2speech_v2 · ElevenLabs, preset 3c9d6053-6334-592c-8997-4e325286af3f), choisi par l'utilisateur — prise 1 (1,8 crédit)."
---

## Intent

Publicité en motion design, style 3D isométrique, pour Manoo — « la plateforme de référence pour valoriser
les métiers manuels ». Elle illustre le système de portfolio numérique : un artisan ou un jeune professionnel
prend en photo ses réalisations (une pièce de métallerie, un chantier, un ouvrage d'artisanat), les met en
ligne sur son profil visuel, et voit ces réalisations mises en valeur auprès des entreprises, des lycées pros
et des clients.

Mots de l'utilisateur : « comme si c'était une vidéo qui allait faire partie de ton portfolio et qui allait
convaincre des entreprises ou des établissements de formation d'avoir envie de faire appel à Manoo pour
digitaliser le savoir-faire. […] je compte sur toi pour faire quelque chose d'impressionnant, avec des zooms,
des illustrations, des animations. »

## Assets

- assets/brand/manoo-marteau-original.png — icône du logo (marteau orange sur fond blanc), reprise du projet manoo-pub-9x16 ; plan de fin.
- Logotype : MANOO en capitales Archivo 800 suivi d'un point orange (site manoo.fr / manooapp.netlify.app).
- Textes du site vitrine (capturés dans ../manoo-pub-9x16/capture/vitrine) : « Le portfolio visuel des métiers manuels », « Manoo remplace le CV par la preuve en images », CTA « Demander une présentation ».

## Customizations

- Style 3D isométrique (demande explicite), avec zooms, illustrations et animations.
- Référence de rendu imposée par l'utilisateur (« je veux vraiment un rendu comme celui-ci ») :
  https://lnkd.in/p/eUZXdW26 — pub motion design « InVideo AI » par Rajwadi Motions (11 s). Langage repris :
  rythme rapide (un temps fort toutes les 1-2 s), appareil 3D incliné entouré d'icônes 3D brillantes, interface
  qui se monte (puces, texte tapé avec lueur, appui avec halo, éclat en anneau), typo cinétique à lignes de base
  décalées, flou de mouvement sur les déplacements rapides, frise de montage, logo final.
- Voix off : Holden (preset choisi par l'utilisateur), prise unique découpée en 6 phrases calées sur les plans.
- Musique : nappe procédurale (tools/make-audio.py), creusée sous la voix (hyperframes-audio carve, force 0,6).
- Bruitages : bibliothèque media-use (whoosh, pop, click, typing, chime, sparkle, ping, impacts, riser) + déclencheur photo synthétisé.

## Notes

- Fonctionnalités réelles seules à l'écran : profil (photo, métier, formation) ; « Ajouter au portfolio » (une photo + un titre) ;
  profil = galerie de réalisations consultable par les entreprises. Jamais : notifications, messagerie, carte / géolocalisation, matching, scores.
- Ne citer aucun concurrent. Pas de faux logos d'entreprises ou d'établissements réels.
- Charte du site : encre #101619 · papier #F3F2EF · orange #F97316 (un seul accent) · acier #78868F ; Archivo + IBM Plex Mono.
- Goût déjà exprimé par l'utilisateur (pub 9:16) : contraste, un seul accent orange, de la matière et du grain ; « pas de 3D lisse et pastel ».
- Slogan : « La révolution du regard ». CTA B2B : « Demandez une présentation — manoo.fr ».

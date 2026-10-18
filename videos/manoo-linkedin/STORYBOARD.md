---
format: 1080x1920
duration: 53.6s
message: "Dans les métiers manuels, les compétences ne se résument pas à un CV : elles se voient, se partagent et se démontrent. Manoo les rend visibles et rapproche les pros des entreprises."
arc: Accroche (galerie → une ligne de CV) → Question → Approches classiques → Pivot « se voient / se partagent / se démontrent » → Voici Manoo → Démo (chantier → photo, vidéo → portfolio → vitrine) → Communauté (questions, astuces) → Entreprises (chantiers, équipes, coulisses, local → contact) → Nuance (ne remplace pas le CV) → Signature + manoo.fr
audience: pros des métiers manuels et entreprises, sur LinkedIn et Instagram
mode: autonomous
reference: https://x.com/abdullah4204k/status/2111150845358444902 (« Pulse », Abdullah.A)
music: score original ~98 BPM (tools/make-audio.py) — la mineur sur le problème, coupure sur « Pourtant », montée sur les trois verbes, silence sur « Voici », do majeur dès « Manoo » ; baissé de 7 dB sous la voix
narration: SCRIPT.md (Kokoro ff_siwis, provisoire) — timings réels dans assets/cues.js
version: v1
---

# Storyboard v1 — Manoo LinkedIn / Instagram, « Ça se voit »

53,6 s, 9:16, avec une version 4:5 pour le fil (bande y 255 → 1705, voir Build notes). Chaque scène démarre et s'arrête sur la voix : les
débuts de scène sont calculés par `tools/vo-build.py` (index.html, bloc `scenes`) et chaque mot apparaît quand il est
dit (`assets/kt.js`).

## Decisions

- **Nouveau projet** (videos/manoo-linkedin) : autre référence, autre format et autre public que les trois pubs
  précédentes.
- **Codes de la référence** transposés : sous-titres mot à mot avec pastille d'accent, monde noir / monde blanc,
  « Voici » géant + onde → logo, interface qui flotte, graphe de nœuds, notification avec halo, chaîne de pastilles,
  second public introduit par une question, signature au faisceau lumineux.
- **Voix** : Kokoro ff_siwis (seule voix française locale), prononciation « Manou » ; remplaçable sans retoucher
  l'animation (une commande).
- **Pas de marques tierces** : réseaux pros, sites d'emploi, intérim décrits par des cartes génériques grises.
- **Construit par l'orchestrateur** (comme les pubs précédentes) : une seule main pour le système de sous-titres, le
  kit d'interface et la synchronisation.

## Frame 1 — Accroche (0 – 5.16 s, L1–L2)

- src: compositions/scenes/01-accroche.html · blueprint: hook-statement + device-gallery · status: animated
- asset_candidates: assets/photos/*.jpg (galerie), assets/ui/manoo-ui.css (téléphone)

Monde noir. Une galerie photo de téléphone pleine de réalisations défile, inclinée, halo orange derrière.
« Tes plus belles réalisations dorment dans ta **galerie photo**. » Puis les photos volent vers une feuille de CV
blanche : « Et sur ton CV ? Une seule **ligne.** » — une seule ligne surlignée « Serrurier-métallier — 3 ans ».

## Frame 2 — La question (5.16 – 8.23 s, L3)

- src: compositions/scenes/02-question.html · blueprint: typed-question · status: animated
- asset_candidates: icônes de métiers (soudure, peinture, cuisine, maçonnerie, coiffure, menuiserie)

Noir. Phrase tapée avec curseur « Comment montrer ce que tu sais faire, **avant l'entretien ?** » ; six tuiles de
métiers flottent floues autour.

## Frame 3 — Approches classiques (8.23 – 15.75 s, L4–L6)

- src: compositions/scenes/03-classiques.html · blueprint: card-carousel (« This one? Or this one? ») · status: animated

Trois cartes grises génériques arrivent l'une après l'autre : profil de réseau pro (« Pensés d'abord pour les
**bureaux.** »), offre d'emploi + CV.pdf (« Une annonce, **un CV.** »), mission d'intérim 2 semaines
(« Utile, mais souvent **ponctuel.** »).

## Frame 4 — Pivot (15.75 – 21.63 s, L7–L8)

- src: compositions/scenes/04-pivot.html · blueprint: statement-stack · status: animated

« Pourtant, tes compétences ne tiennent pas **dans un CV.** » — un CV d'où débordent des réalisations. Puis la triade
empilée : « Elles se **voient.** / Elles se **partagent.** / Elles se **démontrent.** » avec photos, avatars et coches.

## Frame 5 — Voici Manoo (21.63 – 23.44 s, L9)

- src: compositions/scenes/05-revelation.html · blueprint: logo-reveal-ripple · status: animated

« Voici » géant lumineux, onde orange, icône + « Manoo » ; le monde blanc éclot depuis le logo.

## Frame 6 — Démo (23.44 – 28.52 s, L10–L11)

- src: compositions/scenes/06-demo.html · blueprint: footage-card → device · status: animated
- asset_candidates: assets/video/atelier.mp4, assets/photos/jules-portail.jpg, kit d'interface

Monde blanc. Carte vidéo de l'atelier (Jules finit son portail, le photographie — flash sur « Photos »), puis le
téléphone : mode vidéo (REC), « Publier » tapé, la réalisation rejoint le portfolio. « Ton profil devient une vraie
**vitrine.** » : recul, le profil de Jules entouré de cartes flottantes (compétences, dispo, réalisations).

## Frame 7 — Communauté (28.52 – 35.15 s, L12–L14)

- src: compositions/scenes/07-communaute.html · blueprint: node-graph → feed-cards · status: animated

Graphe : avatars de métiers reliés à l'icône Manoo. Puis une publication « Question » (soudure de l'inox) et des
réponses de pros qui arrivent ; puis une publication « Conseil » (serrure : graphite, pas d'huile) qui se fait aimer
et enregistrer.

## Frame 8 — Entreprises (35.15 – 42.50 s, L15–L16)

- src: compositions/scenes/08-entreprises.html · blueprint: profile-showcase → notification · status: animated

Profil « Atelier Morvan · Métallerie · Rennes » : publications chantier, équipe (bienvenue à Léa, alternante),
coulisses (vidéo) ; puce « près de chez toi » sur une mini-carte. « Ton travail leur plaît ? » : l'entreprise ouvre le
portfolio de Jules, envoie un message ; la notification arrive avec un halo orange.

## Frame 9 — Nuance (42.50 – 46.35 s, L17)

- src: compositions/scenes/09-nuance.html · blueprint: side-by-side · status: animated

Le CV (gardé, coché) et, glissant de derrière lui, le portfolio Manoo : « Manoo ne remplace pas **le CV.** Il montre
**ce qu'il ne dit pas.** »

## Frame 10 — Signature (46.35 – 53.61 s, L18–L19)

- src: compositions/scenes/10-fin.html · blueprint: logo-beam-cta · status: animated

Noir, onde, logo ; un faisceau orange dévoile « Le savoir-faire, enfin visible. » ; puis « Crée ton portfolio sur
**manoo.fr** », tenue.

## Build notes (v1)

- **Voix → tout le reste.** `tools/vo-build.py` lit SCRIPT.md, synthétise les répliques modifiées (Kokoro ff_siwis,
  vitesse 1.05), les aligne mot à mot (whisper.cpp) et écrit `assets/audio/vo/vo.wav`, `assets/cues.js` (débuts de
  scène, temps de chaque mot) et le bloc `scenes` d'index.html. `tools/make-audio.py` relit ces temps : la grille
  musicale est calée pour que les deux logos (« Voici Manoo », « Manoo. Le savoir-faire… ») tombent sur un premier
  temps (98,5 BPM, 10 mesures entre les deux), et chaque bruitage suit son animation. Changer de voix :
  `python3 tools/vo-build.py --lines <dossier de prises>` puis `python3 tools/make-audio.py`.
- **Sous-titres** (`assets/kt.js`) : chaque mot apparaît flouté → net quand il est dit ; la ligne en cours reste
  centrée et glisse à mesure qu'elle grandit ; la pastille s'élargit avec ses mots ; un sous-titre a disparu avant
  le premier mot du suivant. Les scènes se construisent dans `document.fonts.ready` et mesurent leurs éléments même
  masqués (`KT.withLayout`).
- **Mix** : voix −17 LUFS (stéréo), musique −26,5 LUFS intégrés (≈ 11 dB sous la voix quand elle parle), bruitages
  −27 LUFS. `tools/master-audio.sh` amène le rendu à ≈ −14 LUFS / −1 dBTP.
- **Contrôle** (`check`, 43 instants) : marqueurs volontaires — l'éventail des publications de l'entreprise
  (`data-layout-allow-overlap` sur `#e-posts`, occlusion autorisée sur les deux premières cartes), le compositeur
  poussé sous l'écran profil (navigation façon iOS). Les contrastes restants concernent des éléments volontairement
  estompés (cartes latérales du carrousel, fond flouté de la carte) et les puces du kit d'interface de l'app.
- **Couleurs** : les pastilles utilisent #F0650F (un cran plus soutenu que l'accent #F97316) pour que le texte blanc
  passe 3:1 ; tampons des cartes classiques #E2590B.
- **4:5** : un recadrage pur (y 285 → 1635) collait les sous-titres au bord haut et coupait le téléphone de la démo
  (contenu mesuré de y 325 à 1716). `tools/make-4x5.sh` prend la bande y 255 → 1705, la réduit à 93 % et complète
  les 37 px de chaque côté par un fond flou étendu, qui prend la couleur du monde à l'écran (fondu de 28 px aux
  bords : une carte qui sort du cadre ne laisse pas de couture).
- **Livrables v1** (renders/, hors git) : `manoo-linkedin-v1.mp4` 1080 × 1920, 53,6 s, 30 i/s, −14,0 LUFS / −1,8 dBTP
  (rendu brut −18,1 LUFS : le moteur applique −1,1 dB identique aux trois pistes) ; `manoo-linkedin-v1-4x5.mp4`
  1080 × 1350 ; planches de contrôle des deux.


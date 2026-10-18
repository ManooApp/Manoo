# SCRIPT — manoo-linkedin « Ça se voit »

**Voice:** Hugo (ElevenLabs, voix `DbbNuBL7lf62XwY7arQb` — Parisien, grave, « pour la publicité »), choisie le
2026-10-18. Deux façons de l'obtenir, puis `python3 tools/vo-build.py --lines <dossier>` et `python3 tools/make-audio.py` :
- automatique : `python3 tools/vo-elevenlabs.py` (clé `ELEVENLABS_API_KEY` dans l'environnement) → `assets/audio/vo/elevenlabs/` ;
- à la main : lire d'une traite le texte de `python3 tools/vo-elevenlabs.py --text` sur le site ElevenLabs, puis
  `python3 tools/vo-split.py prise.mp3` → `assets/audio/vo/take/`.
Prise actuellement montée (v1) : Kokoro `ff_siwis` (local, provisoire).
**Voice settings:** vitesse 1.05 · une réplique = un fichier · silences posés entre les répliques (colonne `gap`).
**Voice direction:** Chaleureuse, assurée, proche — on parle à un pro de terrain, pas à un DRH. Comme la référence :
des phrases courtes, une idée par phrase, un léger appui sur le mot qui apparaît dans la pastille.

Prononciation : la synthèse lit mal « Manoo » ; le texte envoyé à la voix l'écrit « Manou » (et « manou point F R »),
l'écran garde « Manoo » et « manoo.fr ». Colonne `tts:` ci-dessous : réglages propres à Kokoro (ElevenLabs lit le
texte affiché, avec la même substitution).

---

## Line 1 — Accroche (Frame 1)

**Time:** 0.0 – 3.3s · gap 0.25
**Delivery:** Constat intime, presque complice.

    Tes plus belles réalisations dorment dans ta galerie photo.

## Line 2 — Accroche, la chute (Frame 1)

**Time:** 3.3 – 5.8s · gap 0.4
**Delivery:** Petit temps après « CV ? », chute sèche.

    Et sur ton CV ? Une seule ligne.

## Line 3 — La question (Frame 2)

**Time:** 5.8 – 9.2s · gap 0.45
**Delivery:** Vraie question, l'appui sur « avant l'entretien ».

    Comment montrer ce que tu sais faire, avant l'entretien ?

## Line 4 — Approches classiques (Frame 3)

**Time:** 9.2 – 11.8s · gap 0.25
**Delivery:** Factuel, sans moquerie.

    Les réseaux pros ? Pensés d'abord pour les bureaux.

## Line 5 — Approches classiques (Frame 3)

**Time:** 11.8 – 14.0s · gap 0.25

tts: Les sites d'emploi ? Une annonce. Un CV.

    Les sites d'emploi ? Une annonce, un CV.

## Line 6 — Approches classiques (Frame 3)

**Time:** 14.0 – 16.2s · gap 0.5
**Delivery:** Nuancé : « utile » est sincère.

    L'intérim ? Utile, mais souvent ponctuel.

## Line 7 — Le pivot (Frame 4)

**Time:** 16.2 – 19.2s · gap 0.3
**Delivery:** On change de ton : convaincu.

    Pourtant, tes compétences ne tiennent pas dans un CV.

## Line 8 — Le message central (Frame 4)

**Time:** 19.2 – 22.6s · gap 0.6
**Delivery:** Trois temps, trois appuis.

    Elles se voient. Elles se partagent. Elles se démontrent.

## Line 9 — Révélation (Frame 5)

**Time:** 22.6 – 24.0s · gap 1.0
**Delivery:** Sourire dans la voix.
tts: Voici Manou.

    Voici Manoo.

## Line 10 — Démonstration (Frame 6)

**Time:** 24.0 – 27.3s · gap 0.2

    Tu termines un chantier ? Photos, vidéos : tu publies.

## Line 11 — Démonstration (Frame 6)

**Time:** 27.3 – 29.3s · gap 0.45

    Ton profil devient une vraie vitrine.

## Line 12 — Communauté (Frame 7)

**Time:** 29.3 – 31.2s · gap 0.25
tts: Manou, c'est aussi une communauté.

    Manoo, c'est aussi une communauté.

## Line 13 — Communauté (Frame 7)

**Time:** 31.2 – 34.4s · gap 0.25

    Une question ? Des pros de ton métier te répondent.

## Line 14 — Communauté (Frame 7)

**Time:** 34.4 – 36.6s · gap 0.5

    Tu partages tes astuces de terrain.

## Line 15 — Entreprises, le local (Frame 8)

**Time:** 34.6 – 39.6s · gap 0.35
**Delivery:** On élargit : l'autre côté. Petit temps avant « près de chez toi ».
tts: Les entreprises, elles, montrent leurs chantiers, leurs équipes, leurs coulisses, près de chez toi.

    Les entreprises, elles, montrent leurs chantiers, leurs équipes, leurs coulisses… près de chez toi.

## Line 16 — La rencontre (Frame 8)

**Time:** 41.4 – 44.6s · gap 0.6

    Ton travail leur plaît ? Elles te contactent.

## Line 17 — La nuance (Frame 9)

**Time:** 44.6 – 49.0s · gap 0.7
**Delivery:** Posé, honnête.
tts: Manou ne remplace pas le CV. Il montre ce qu'il ne dit pas.

    Manoo ne remplace pas le CV. Il montre ce qu'il ne dit pas.

## Line 18 — Signature (Frame 10)

**Time:** 49.0 – 51.4s · gap 0.35
tts: Manou, le savoir-faire, enfin visible.

    Manoo. Le savoir-faire, enfin visible.

## Line 19 — Appel à l'action (Frame 10)

**Time:** 51.4 – 53.6s
tts: Crée ton portfolio sur manou point F R.

    Crée ton portfolio sur manoo.fr.

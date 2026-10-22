---
duration: 12.6
music: none
---

# Manoo — « Publie ton chantier en une photo. » (Instagram, 9:16)

Tous les temps sont dans `assets/cues.js` (les compositions et `tools/make-sfx.py` les lisent).

## Video direction

Fond blanc, un seul objet : le téléphone, vrai volume 3D (tranches empilées, boutons) sous une caméra en perspective
(`compositions/phone.html`). La caméra suit des poses calculées (`aim()` place un point du téléphone à un endroit de
l'image) et le flou de mouvement vient de la vitesse à l'écran de quelques points du téléphone : flou vertical à la
montée, mixte à la plongée et au retour. La pastille Manoo vole dans l'espace de l'image, en avant de tout, et se pose
exactement sur le disque du déclencheur tel qu'il est vu à cet instant. Typo de fin : Inter Medium, encre sur blanc ;
logo : marteau Manoo + « Manoo » en Inter Display Bold, orange.

## Frames

1. **0 → 1,1 s — montée.** Le téléphone surgit du bas (flou vertical) et se cale serré sur le haut : écran d'accueil
   orange, icônes génériques, icône Manoo, widgets « Atelier » et « Rappels — Chantier ».
2. **1,12 → 1,7 s — Manoo.** Tap sur l'icône, l'appareil photo s'ouvre depuis l'icône (le portail en fer forgé dans le
   viseur).
3. **1,75 → 2,5 s — la pastille.** La pastille orange au marteau entre en haut à gauche, grande et floue, descend puis
   se rabat sur le déclencheur pendant que la caméra plonge et pivote vers le bas du téléphone.
4. **2,5 → 3,18 s — une pression.** Le déclencheur est devenu orange, il s'allume ; mise au point, pression, flash.
5. **3,18 → 3,8 s — retour.** La caméra remonte de face (flou), l'image figée file dans l'encoche qui s'ouvre ; derrière,
   le profil Manoo de Jules.
6. **3,8 → 5,45 s — publié.** Bandeau : vignette, « Portail en fer forgé », « Envoi… % » avec l'anneau, puis
   « Ajouté à ton portfolio » ✓ ; la réalisation entre en tête de la grille, Réalisations 4 → 5.
7. **5,45 → 6,55 s — compact.** L'encoche se replie : marteau à gauche, coche à droite, l'heure revient.
8. **6,55 s — coupe au blanc.**
9. **6,65 → 8,9 s — la phrase.** « Publie ton chantier / en une photo. », mot à mot depuis un flou gris, puis tout se
   floute.
10. **9,0 → 12,6 s — le logo.** Le marteau apparaît (net depuis un flou), puis s'ouvre en « Manoo » : le mot se dévoile
    à droite du marteau pendant que l'ensemble rétrécit et se recentre ; tenue jusqu'à la fin.

## Build notes

- Les durées des deux timelines couvrent toute la scène (`tl.to({}, {duration})`) : la caméra, l'encoche, la photo
  figée et le logo sont posés image par image dans le `onUpdate`, qui ne tourne que tant que la timeline avance.
- Les formes de l'encoche, de la fenêtre de l'appareil photo et de la photo figée sont des `clip-path` calculés à
  chaque image : le navigateur réécrit les `inset()` (valeurs égales fusionnées), ce qui casse l'interpolation en texte.
- Les trois écrans portent `data-layout-ignore` : ce sont l'interface du téléphone et les couleurs de l'app Manoo
  (blanc sur l'en-tête orange), reproduites telles quelles ; le bandeau de l'encoche et les textes de fin restent
  contrôlés.
- Version muette = le même rendu sans piste audio ; 4:5 = `tools/make-4x5.sh`.

---
workflow: product-launch-video
flow: automation
storyboard: no
message: "Publie ton chantier en une photo."
destination: instagram
aspect: 1080x1920
safe_area: "4:5 — la déclinaison fil Instagram (1080 × 1350) est la bande y 260 → 1610 du master (tools/make-4x5.sh) ; téléphone, encoche, déclencheur, phrase et logo y tiennent"
language: fr
audience: "Pros des métiers manuels (artisans, apprentis, jeunes pros) sur Instagram (Reels, Stories, fil)."
length: 12.6s
angle: "Reprise du style de la pub Circleback « Record with one press » (téléphone sur fond blanc, flou de mouvement, pastille de marque qui vient se poser sur un bouton, encoche qui devient un bandeau, coupe au blanc, phrase mot à mot, logo qui se déploie), transposée à une vraie fonction de Manoo : ajouter la photo d'une réalisation à son portfolio."
narration: no
music: none
sfx: light
---

## Intent

Demande (2026-10-22) : « Je veux que tu me fasses une pub pour Instagram. Donc tu mets la bonne résolution, toujours en
rapport avec Manoo, et je t'ai mis le lien sur lequel tu dois copier-coller le style. »
→ master 9:16 1080 × 1920 à 60 i/s (Reels, Stories), plus une déclinaison 4:5 1080 × 1350 pour le fil.

## Reference (analysée le 2026-10-22)

https://x.com/circlebackai/status/2112945316274299335 — pub Circleback, 12,6 s, 16:9 1920 × 1080, 60 i/s, sans son.
Récupérée via l'API de syndication X, planches toutes les 0,1 s sur les transitions. Rythme relevé :

| temps | référence | ici |
| --- | --- | --- |
| 0 → 0,8 s | le téléphone monte du bas, gros flou vertical, cadrage serré sur le haut | idem, écran d'accueil orange |
| 0,8 → 1,75 s | écran d'accueil fixe | idem, tap sur l'icône Manoo à 1,12 s, l'appareil photo s'ouvre depuis l'icône |
| 1,75 → 2,5 s | la pastille « C. » entre en haut à gauche, énorme et floue, la caméra pivote vers la tranche | la pastille Manoo (marteau) entre en haut à gauche, la caméra plonge et pivote vers le déclencheur |
| 2,5 → 3,2 s | la pastille est devenue le bouton Action, il s'allume, on appuie | la pastille est devenue le déclencheur, il s'allume, on appuie (3,0 s : la photo) |
| 3,2 → 3,45 s | retour de face, gros flou horizontal | idem ; derrière, le profil Manoo |
| 3,45 → 5,45 s | l'encoche s'ouvre en bandeau « Design brainstorm 0:00 » | l'encoche s'ouvre, la photo y file : « Portail en fer forgé — Envoi… % » puis « Ajouté à ton portfolio » ✓ ; la réalisation entre dans la grille (4 → 5) |
| 5,45 → 6,55 s | l'encoche se replie en pastille compacte | idem : marteau + coche |
| 6,55 s | coupe sèche au blanc | idem |
| 6,65 → 8,9 s | « Record with one press », mot à mot depuis un flou, puis tout se floute | « Publie ton chantier en une photo. » |
| 9,0 → 12,6 s | le « C. » apparaît, puis s'ouvre en « Circleback. » | le marteau apparaît, puis s'ouvre en « Manoo » |

## Honnêteté

- La photo est prise avec l'appareil photo du téléphone, ouvert depuis Manoo (« Ajouter au portfolio » sur mobile propose
  de prendre une photo) : le film raccourcit ce chemin (icône → appareil photo) ; la pastille sur le déclencheur est une
  image de marque, pas un bouton réel.
- Le bandeau dans l'encoche (Dynamic Island) est une mise en scène reprise de la référence : dans l'app web, la
  confirmation « Ajouté à ton portfolio » s'affiche en bandeau dans la page.
- Profil fictif (Jules Moreau, serrurier-métallier, Rennes, CAP 2e année) déjà utilisé dans les films précédents ;
  photos 3D du dossier des films précédents. Aucun chiffre sur Manoo.
- Icônes de l'écran d'accueil génériques (dessinées ici ou Lucide, licence ISC), pas celles d'Apple ; aucune marque tierce.
- Sons : bibliothèque media-use (licence Pixabay, usage commercial sans attribution) et un déclencheur synthétisé.

---
format: 1080x1920
duration: 61s
message: "Pour un métier manuel, on montre le travail, pas un CV papier."
arc: Accroche → Problème → Le travail est là → Bascule (le CV devient Manoo) → Démonstration → Le regard de l'entreprise → Pour qui → Signature
audience: apprentis 16-20 ans et artisans sur Instagram / TikTok ; partenaires institutionnels
mode: collaborative
music: none (proposé en option : bruitages de matière + nappe discrète)
version: v1
---

# Storyboard v1 — Manoo, « La révolution du regard »

## Decisions

- **Message** : pour un métier manuel, on montre le travail, pas un CV papier.
- **Public et arc** : apprentis 16-20 ans et artisans (Instagram, TikTok). Arc PAS documentaire :
  accroche → problème → le travail existe → bascule → démonstration → regard de l'entreprise → pour qui → signature.
- **Format** : 1080×1920, ~61 s, voix off oui (féminine, documentaire), musique : non par défaut (proposée en option).
  Sous-titres incrustés proposés en option (zone 12 %–80 % de la hauteur réservée au contenu).
- **Fil conducteur (spine)** : **une étincelle orange**. Elle naît du geste (la soudure, plan 1), reste la seule
  couleur vive du film, et finit en **point orange du logotype « MANOO. »** (plan 10). Le CV papier est l'objet
  témoin : il apparaît vide (plan 2), revient et se froisse pour laisser place au téléphone (plan 4).
- **Marque** : Encre #101619 · Papier #F3F2EF · Orange #F97316 · Acier #78868F ; Archivo 800 serré + IBM Plex Mono
  (source : brief du fondateur, voir `frame.md`).
- **Interdits** : 3D pastel/lisse ; dégradés « tech » ; texte en dégradé ; curseur flèche ; poignées de main de banque
  d'images ; toute fonctionnalité absente (notifications, messagerie, géolocalisation, matching) ; aucun concurrent
  cité. Deux échecs de mouvement à éviter : le diaporama (tout arrive d'un coup puis se fige) et l'économiseur
  d'écran (tout flotte sans raison).
- **Plan tenu** : la fin du plan 9 (« …mais déjà un savoir-faire à montrer. ») — rien ne bouge, la phrase se pose.
- **Vérité** : les écrans de l'app viennent de vraies captures (à fournir). Les photos de réalisations sont de vraies
  photos de travail (à fournir, ou générées / stylisées si l'utilisateur le choisit — signalé dans le plan).

## Video direction

- **Palette** : fond encre partout ; papier = la feuille de CV et le texte ; orange = le feu et un seul point focal par plan.
- **Grammaire de mouvement** : coupes sèches sur les mots de la voix ; chaque élément apparaît quand la voix le nomme,
  jamais avant. Les seuls « mouvements » sont physiques : étincelles (gravité), poussière dans un rai de lumière,
  farine qui tombe, papier qui se froisse, marteau qui frappe. Caméra : poussées courtes et nettes, pas de dérive.
- **Rythme** : staccato (1) → plan fixe inconfortable (2) → trois coupes franches (3) → un geste physique (4) →
  téléphone stable, écrans coupés sur les mots (5-7) → zoom du regard (8) → défilé rapide puis PLAN TENU (9) →
  frappe + tenue finale (10).
- **Matière** : grain animé sur tout le film ; vignettage léger ; particules déterministes (seed fixe).

## Frame 1 — Étincelle (0.0–4.4s, ~4.4s)

- scene: Noir. Un cordon de soudure s'allume en macro, gerbe d'étincelles orange ; coupe sèche sur une feuille blanche vide en lumière rasante.
- duration: 4.4s
- transition_in: cut
- status: outline
- src: compositions/frames/01-etincelle.html
- voiceover: "Comment montrer un geste… sur une feuille de papier ?"
- type: hook
- blueprint: kinetic-type-beats (Adapt)
- asset_candidates: PHOTO soudure macro (à fournir) — sinon cordon + étincelles générés en code

Scene 1 (0.0–2.2s) : noir total, une étincelle naît au centre ; le cordon s'embrase, gerbe d'étincelles (gravité, rebond).
« un geste » en Archivo 800 papier, centré, tombe sur le mot « geste ».
Scene 2 (2.2–4.4s) : COUPE sèche sur « feuille » : feuille de papier vide, grain du papier, lumière rasante ; « sur une
feuille de papier ? » en encre sur le papier. Le silence visuel répond au feu.
Pourquoi : l'accroche oppose le feu (le geste) et le papier (le CV) dès la première seconde.

## Frame 2 — Deux lignes (4.4–9.0s, ~4.6s)

- scene: La feuille devient un CV : deux lignes tapées à la machine, le reste vide.
- duration: 4.6s
- transition_in: cut
- status: outline
- src: compositions/frames/02-deux-lignes.html
- voiceover: "Sur un CV, deux ans d'apprentissage tiennent en deux lignes."
- type: pain_point
- blueprint: typewriter-reveal (Adapt)

Scene 1 (0.0–2.0s) : en-tête « CURRICULUM VITAE » en mono ; poussée lente et courte sur la feuille.
Scene 2 (2.0–4.6s) : sur « deux lignes », deux lignes se tapent : « FORMATION — CAP Maçonnerie » / « EXPÉRIENCE — Stage, 3 semaines ».
Dessous : des lignes vides. Label acier en marge : « 2 ANS → 2 LIGNES ». Plan fixe, inconfortable.
Pourquoi : le problème, montré sans le dire — tout le savoir-faire réduit à deux lignes.

## Frame 3 — Le travail est là (9.0–16.4s, ~7.4s)

- scene: Coupe vers le noir puis trois plans macro plein cadre, coupés sur chaque mot : soudure, carrelage, pain.
- duration: 7.4s
- transition_in: cut
- status: outline
- src: compositions/frames/03-le-travail.html
- voiceover: "Pourtant, le travail est là. Une soudure. Un carrelage posé. Un pain qui sort du four."
- type: benefit_highlight
- blueprint: kinetic-type-beats (Adapt — les mots deviennent des plans)
- asset_candidates: PHOTOS soudure, carrelage posé, pain sorti du four (à fournir)

Scene 1 (0.0–1.8s) : « Pourtant, le travail est là. » — noir, poussière qui flotte dans un rai de lumière.
Scene 2 (1.8–3.6s) : SOUDURE — plan macro, étincelles en surimpression ; label « 01 — SOUDURE ».
Scene 3 (3.6–5.4s) : CARRELAGE — lumière rasante sur des joints frais, poussière ; label « 02 — CARRELAGE ».
Scene 4 (5.4–7.4s) : BOULANGERIE — croûte en gros plan, farine qui tombe ; label « 03 — BOULANGERIE ».
Pourquoi : la preuve que le travail existe — et qu'il est visuel, pas textuel.

## Frame 4 — On le montre (16.4–23.0s, ~6.6s)

- scene: Le CV du plan 2 revient, se froisse en boule et tombe ; coupe : le téléphone au centre, écran Manoo.
- duration: 6.6s
- transition_in: cut
- status: outline
- src: compositions/frames/04-on-le-montre.html
- voiceover: "Manoo remplace le CV papier. On ne raconte plus son travail. On le montre."
- type: product_intro
- blueprint: compose (froissage physique + révélation du téléphone)
- asset_candidates: CAPTURE écran d'accueil Manoo (à fournir) ; logo

Scene 1 (0.0–2.6s) : « Manoo remplace le CV papier » — la feuille se froisse (vraie déformation 3D texturée), tombe hors champ.
Scene 2 (2.6–4.6s) : coupe : téléphone sobre au centre, écran d'accueil Manoo. « Raconter. » en acier, barré.
Scene 3 (4.6–6.6s) : « On le montre. » — « Montrer. » en papier, avec le point orange.
Pourquoi : la bascule du film — le fil rouge validé (la feuille devient le profil).

## Frame 5 — Le profil (23.0–27.0s, ~4.0s)

- scene: Téléphone au centre : choix « Apprenti / Étudiant », puis profil (photo, métier, formation).
- duration: 4.0s
- transition_in: cut
- status: outline
- src: compositions/frames/05-profil.html
- voiceover: "L'apprenti crée son profil : son métier, sa formation."
- type: feature_showcase
- blueprint: device-surface-showcase (Reproduce)
- asset_candidates: CAPTURES choix du type de profil + configuration du profil (à fournir)

Scene 1 (0.0–1.6s) : écran « type de profil » ; appui (léger enfoncement, pas de curseur) sur « Apprenti / Étudiant ».
Scene 2 (1.6–4.0s) : écran profil : sur « métier », le champ Métier se remplit (« Maçonnerie ») ; sur « formation », la formation (« CAP Maçonnerie »).
Pourquoi : montrer que l'entrée est simple, et uniquement ce qui existe.

## Frame 6 — Une photo, un titre (27.0–34.6s, ~7.6s)

- scene: « Ajouter au portfolio » trois fois, coupé sur « chantier », « pièce », « fournée » ; puis la photo et le titre.
- duration: 7.6s
- transition_in: cut
- status: outline
- src: compositions/frames/06-ajouter.html
- voiceover: "Puis, à chaque chantier, chaque pièce, chaque fournée, il ajoute une réalisation. Une photo, un titre."
- type: feature_showcase
- blueprint: device-surface-showcase (Adapt — trois boucles courtes)
- asset_candidates: CAPTURE « Ajouter au portfolio » (à fournir) ; PHOTOS mur maçonné, pièce soudée, fournée

Scene 1 (0.0–1.4s) : CHANTIER — la photo d'un mur maçonné entre dans l'emplacement photo.
Scene 2 (1.4–2.8s) : PIÈCE — une pièce soudée.
Scene 3 (2.8–4.4s) : FOURNÉE — des pains sur une grille.
Scene 4 (4.4–7.6s) : « Une photo, un titre » — le titre se tape (« Mur en briques — chantier école ») ; appui sur le bouton d'ajout.
Pourquoi : la fonctionnalité centrale, répétable pour tous les métiers.

## Frame 7 — La galerie (34.6–39.2s, ~4.6s)

- scene: Le profil défile : une grille de réalisations ; recul : la grille déborde du téléphone et remplit le cadre.
- duration: 4.6s
- transition_in: cut
- status: outline
- src: compositions/frames/07-galerie.html
- voiceover: "Son profil devient la galerie de ce qu'il sait faire."
- type: benefit_highlight
- blueprint: zoom-out-workspace-reveal (Adapt)
- asset_candidates: CAPTURE profil / galerie (à fournir) ; 6 à 9 PHOTOS de réalisations

Scene 1 (0.0–2.2s) : le profil défile, la grille de photos se remplit ligne par ligne.
Scene 2 (2.2–4.6s) : recul net ; la grille sort du téléphone et devient un mur de travail plein cadre ; label « 12 RÉALISATIONS ».
Pourquoi : la preuve s'accumule — le profil, c'est le travail.

## Frame 8 — Le regard (39.2–44.8s, ~5.6s)

- scene: Vu par une entreprise : le même profil ; zoom sur une réalisation ; le diplôme, petit, en dessous.
- duration: 5.6s
- transition_in: cut
- status: outline
- src: compositions/frames/08-regard.html
- voiceover: "Et l'artisan qui recrute voit le geste, la motivation… avant le diplôme."
- type: benefit_highlight
- blueprint: compose (zoom vers la cible)
- asset_candidates: CAPTURE vue entreprise d'un profil (à fournir)

Scene 1 (0.0–2.4s) : label « COMPTE ENTREPRISE » ; le profil s'ouvre.
Scene 2 (2.4–4.2s) : sur « le geste », zoom franc dans une photo de réalisation (le geste en gros plan).
Scene 3 (4.2–5.6s) : sur « avant le diplôme », recul : la ligne « CAP Maçonnerie » apparaît, petite, sous les photos.
Pourquoi : « la révolution du regard » — où l'œil de l'entreprise se pose en premier.

## Frame 9 — Savoir-faire (44.8–54.0s, ~9.2s)

- scene: « Pensé pour l'alternance » fixe ; les métiers défilent dessous ; puis PLAN TENU sur la phrase-clé.
- duration: 9.2s
- transition_in: cut
- status: outline
- src: compositions/frames/09-savoir-faire.html
- voiceover: "Manoo est pensé pour l'alternance. Pour ceux qui n'ont pas encore d'expérience à raconter… mais déjà un savoir-faire à montrer."
- type: benefit_highlight
- blueprint: fixed-anchor-cycle (Adapt)
- asset_candidates: matières par métier (photos ou générées)

Scene 1 (0.0–3.4s) : « Pensé pour l'alternance. » ancré ; dessous, coupés vite : BTP · MÉCANIQUE · MÉTIERS DE BOUCHE ·
ESTHÉTIQUE · PROTHÈSE DENTAIRE, chacun avec un éclat de sa matière (poussière, acier, farine…).
Scene 2 (3.4–6.4s) : « Pas encore d'expérience à raconter… » en acier.
Scene 3 (6.4–9.2s) : « …mais déjà un savoir-faire à montrer. » en papier — PLAN TENU, rien ne bouge.
Pourquoi : la deuxième différence — fait pour l'alternance dans les métiers manuels.

## Frame 10 — La révolution du regard (54.0–61.0s, ~7.0s)

- scene: Le marteau frappe une fois ; la dernière étincelle devient le point orange de « MANOO. » ; slogan, appel à l'action.
- duration: 7.0s
- transition_in: cut
- status: outline
- src: compositions/frames/10-signature.html
- voiceover: "Manoo. La révolution du regard. Inscrivez-vous sur manoo.fr."
- type: cta
- blueprint: logo-assemble-lockup (Adapt)
- asset_candidates: assets/brand/manoo-marteau-original.png — icône marteau

Scene 1 (0.0–1.6s) : le marteau (icône) frappe ; une étincelle part et se pose : « MANOO. » se tamponne, le point = l'étincelle.
Scene 2 (1.6–4.0s) : « La révolution du regard. » en Archivo papier.
Scene 3 (4.0–7.0s) : « Inscrivez-vous sur manoo.fr » en mono ; tenue jusqu'à la fin, l'étincelle-point respire à peine.
Pourquoi : signature et appel à l'action demandés mot pour mot.

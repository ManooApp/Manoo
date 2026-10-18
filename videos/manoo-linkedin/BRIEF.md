---
workflow: product-launch-video
flow: automation
storyboard: no
message: "Dans les métiers manuels, les compétences ne se résument pas à un CV : elles se voient, se partagent et se démontrent. Manoo rapproche les pros et les entreprises par le savoir-faire, les portfolios visuels et la communauté."
destination: linkedin-instagram
aspect: 1080x1920
safe_area: "4:5 — tout le contenu clé tient dans la bande y 255 → 1705 ; la déclinaison fil Instagram / LinkedIn (1080 × 1350) la réduit à 93 % sur un fond flou étendu (tools/make-4x5.sh)"
language: fr
audience: "Pros des métiers manuels (artisans, soudeurs, peintres, cuisiniers, jeunes pros, apprentis) et entreprises qui recrutent ou veulent valoriser leurs équipes localement — sur LinkedIn et Instagram."
length: 50-58s
angle: "Pub narrative au style de la référence « Pulse » (Abdullah.A) : accroche à la deuxième personne, question, limites des approches classiques, pivot « elles se voient / se partagent / se démontrent », révélation, démonstration dans l'interface, communauté, entreprises, nuance « ne remplace pas le CV », signature."
narration: yes
vo_mode: restructured
voice: "Hugo (ElevenLabs DbbNuBL7lf62XwY7arQb), demandée le 2026-10-18 — v1 montée avec Kokoro ff_siwis en attendant la prise ElevenLabs (tools/vo-elevenlabs.py ou tools/vo-split.py)"
---

## Intent

Publicité en motion design pour Manoo (manoo.fr), diffusée sur LinkedIn et Instagram, 30 à 60 s. Pas une
présentation de l'app ni un tuto d'inscription : une histoire qui part d'un problème réel (le savoir-faire manuel ne
tient pas dans un CV ; les réseaux pros classiques, les sites d'annonces et l'intérim ne permettent pas de le montrer)
pour présenter une nouvelle approche — rendre les compétences manuelles visibles. Mots de l'utilisateur : « Dans les
métiers manuels, les compétences ne se résument pas à un CV. Elles se voient, se partagent et se démontrent. »
Manoo est aussi un réseau communautaire (questions, conseils, échanges entre pros) et une vitrine locale pour les
entreprises (chantiers, salariés, alternants, coulisses). Ne pas présenter Manoo comme ayant tout résolu : une
alternative complémentaire. Rendu « professionnel, humain et accessible », prêt à diffuser.

## Reference (analysée le 2026-10-18)

https://x.com/abdullah4204k/status/2111150845358444902 — film de lancement « Pulse », 52 s, 16:9, voix off masculine
naturelle (~150 mots/min), musique électronique discrète. Récupérée via l'API de syndication X (MP4 1080p), planches
toutes les 0,5 s et transcription Whisper complète. Codes repris :

- texte à l'écran = la phrase clé de la voix, révélée mot à mot à l'instant où elle est dite ; un mot clé dans une
  pastille pleine de la couleur d'accent (ou en couleur d'accent) ; parfois un curseur de saisie ;
- deux mondes : scène noire avec halos et ondes de la couleur d'accent (accroche, révélation, fin) et scène blanche où
  l'interface flotte en perspective (démonstration, bénéfices), avec un halo d'accent qui monte du bas ;
- accroche à la deuxième personne avec compteur dans une pastille, puis question (« But which video actually sent
  them? ») et cartes qui défilent (« This one? Or this one? ») ;
- « Meet » géant lumineux → onde → logo ; à la fin, logo + faisceau lumineux qui dévoile la signature, puis appel à
  l'action avec pastille ;
- interface mise en scène : poussée lente, panoramiques, curseur qui clique et glisse, ligne mise en avant avec un
  halo, notification qui arrive, chaîne de pastilles (parcours d'un contact) ;
- un second public introduit par une question (« Own a content agency? ») ; rythme : une idée toutes les 2 à 3 s.

## Assets

- ../manoo-tiktok/assets/ui/ — kit d'interface Manoo (reconstruit depuis manoo.fr et les captures fournies), icônes.
- ../manoo-tiktok/assets/photos/ — réalisations rendues depuis la maquette 3D de l'atelier ; ../manoo-explainer/assets/video/atelier.mp4.
- ../manoo-tiktok/assets/brand/manoo-marteau.png, fonts Inter / Inter Display, gsap.
- capture/ — capture de manoo.fr du 2026-10-14 (reprise de la pub explicative : la recapture du 2026-10-18 a échoué,
  le navigateur sans interface refusant le certificat du proxy ; le site répond bien en HTTPS direct). Le fil public
  confirme les types de publication (Projet, Conseil, Question, Emploi), les accès « Salariés » et « Patrons »
  (entreprises, recruteurs, CFA, écoles) et des messages d'entreprises « Pas besoin de CV : envoie-nous ton portfolio ».

## Customizations

- 9:16 maître (1080 × 1920) + version 4:5 (1080 × 1350) tirée de la bande centrale : la référence est en 16:9, mais
  les fils mobiles LinkedIn et Instagram favorisent le vertical et le 4:5.
- Voix off française naturelle demandée « si possible » : pas de crédits Higgsfield (0,10 crédit ; 0,11 pour une seule
  phrase de test) ni de clé Gemini, donc voix locale Kokoro (ff_siwis) via HyperFrames, comme l'autorise la demande.
  Chaîne prête pour une autre prise (une ligne = un fichier, repères recalculés depuis la voix).
- Approches classiques décrites sans nom ni logo (« Les réseaux pros », « Les sites d'emploi », « L'intérim ») : la pub
  sera diffusée sur LinkedIn, et l'utilisateur demande d'expliquer des limites, pas de dénigrer.

## Notes

- Noms fictifs : Jules Moreau (apprenti serrurier-métallier, Rennes), Atelier Morvan (métallerie, Rennes), Inès,
  Malo, Léa… ; aucun chiffre inventé présenté comme une donnée (seuls des compteurs d'interface fictifs).
- Pas de prises de vues réelles de personnes : aucune vidéo fournie, banques d'images inaccessibles depuis
  l'environnement (protection anti-robot), pas de crédits de génération. L'humain passe par les personnages, la voix,
  les échanges ; les rendus 3D de l'atelier servent de terrain.
- Couleurs : noir profond, blanc, orange Manoo #F97316 (accent unique), UI de l'app #E36E2D. Les pastilles des sous-titres
  prennent un cran plus soutenu (#F0650F) pour que le texte blanc reste lisible (contraste 3:1).
- Son : musique originale composée par `tools/make-audio.py` (aucune piste sous licence) ; bruitages de la
  bibliothèque media-use (Pixabay Content License, usage commercial sans attribution).

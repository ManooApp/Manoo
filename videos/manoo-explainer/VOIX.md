# Changer la voix off de la pub explicative

La pub est calée sur la voix Holden, mais elle suit n'importe quelle nouvelle prise : `tools/revoice.py` retrouve
chaque mot dans la nouvelle voix, place les sept phrases et écrit `assets/retime.js`. Toutes les animations, les
repères, le plan 3D de l'atelier, la musique et les bruitages passent par cette table (vide = film d'origine).
Le texte est celui de SCRIPT.md (« Manou » et « manou point F R » pour la prononciation).

## 1. Obtenir la voix (une des deux voies)

**Voix Google (gratuite)** : il faut une clé `GEMINI_API_KEY` dans les secrets de l'environnement cloud (créée sur
aistudio.google.com → Get API key ; jamais collée dans le chat ; une nouvelle session la lit au démarrage).

    npx hyperframes skills update media-use          # si le skill n'est pas installé
    node ~/.claude/skills/media-use/audio/scripts/audio.mjs \
      --request ./audio_request.json --hyperframes . --out ./audio_meta.json --only tts
    # -> assets/voice/L1.wav … L7.wav (vérifier qu'il y a bien 7 fichiers et que la consigne n'est pas lue)

Voix par défaut : Charon (narrateur posé). Pour comparer avant de tout générer :
`python3 tools/gemini-tts.py --sample Charon Algieba Achird Iapetus` (ligne 1 dans chaque voix), puis changer
`voice` dans audio_request.json. `tools/gemini-tts.py` remplace aussi le moteur media-use s'il manque.

**Voix Higgsfield (ElevenLabs)** : Grady (preset e2a2d2e6-9ed2-59cd-82af-feaa27f8a678) en `elevenlabs_v4_turbo`
coûte 2,10 crédits, en `elevenlabs_v4` 3,22 crédits. Un seul appel `generate_audio` avec un `dialogue` de sept
tours (un par ligne de SCRIPT.md, même voix), puis télécharger le mp3 dans `assets/audio/vo-src/`.

## 2. Poser la voix

    python3 tools/revoice.py --lines assets/voice/L1.wav … assets/voice/L7.wav --dry-run   # Google : 7 fichiers
    python3 tools/revoice.py --take assets/audio/vo-src/<prise>.mp3 --dry-run              # Higgsfield : 1 fichier

Le dry-run affiche le placement des phrases et le déplacement de chaque repère. Une ligne « !! … overlaps » veut
dire qu'une phrase déborde sur la suivante : relancer avec `--tempo L4=1.04` (par exemple) pour l'accélérer un
peu. Puis sans `--dry-run` : clips `assets/audio/vo/LN.wav` (ramenés à -16 LUFS), timings des `vo-N` dans
index.html, `assets/retime.js`, vitesse et départ du plan de l'atelier dans la séquence 4.

whisper.cpp (DTW) donne les temps de mots les plus justes. S'il manque dans le conteneur :

    cd ~/.cache/hyperframes/whisper && git clone --depth 1 https://github.com/ggml-org/whisper.cpp && cd whisper.cpp
    cmake -B build -DGGML_NATIVE=OFF -DGGML_AVX=ON -DGGML_AVX2=ON -DGGML_FMA=ON -DGGML_F16C=ON -DGGML_AVX512=OFF -DCMAKE_BUILD_TYPE=Release
    cmake --build build -j4 --target whisper-cli
    mkdir -p ../models && curl -L -o ../models/ggml-small.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin

Sinon l'outil passe par `npx hyperframes transcribe` (moins précis).

## 3. Son, contrôle, rendu

    python3 tools/make-audio.py
    node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp ./index.html --bed music --strength 0.6
    python3 tools/fix-carve.py
    npx hyperframes check --samples 24 --timeout 60000
    npx hyperframes render --quality high --workers 3 --output renders/manoo-explainer-v2.mp4

Vérifier ensuite quelques images (flash photo du plan 3D sur « photo », carte de Jules, notification) et le niveau
(-16 à -14 LUFS, crête sous -1 dBTP). Pour revenir à Holden : `git checkout` des fichiers de la voix et remettre
`window.RETIME_POINTS = [];`.

// Film cue sheet (seconds, film time), 120 BPM: beat 0.5 s, bar 2 s. Every scene and tools/make-audio.py read it,
// so a retimed moment moves its picture and its sound together.
window.CUES = {
  END: 43.0,
  // 01 accroche
  l1: 0.1, l2: 1.55, l3: 3.05, l4: 4.05, arrow: 5.5,
  // 02 manoo
  logo: 6.0, word: 6.35, sub: 7.0, b1: 8.0, b2: 8.25, b3: 8.5, out2: 8.75,
  // 03 ton portfolio
  title3: 9.0, toggle3: 9.5, phone3: 10.1, shutter: 11.0, sheet: 11.8, type3a: 12.2, type3b: 12.9, addTap: 13.15,
  toast3: 13.3, grid: 13.6, cellNew: 13.8, publish: 14.6, post: 14.9, likes: 15.2, comment: 15.8, out3: 16.6,
  // 04 0 CV
  zero: 17.0, terrain: 17.95, out4: 18.8,
  // 05 avant / après
  split: 19.0, fill: 19.6, chip5: 20.2, scroll5: 20.8, heart5: 21.6, out5: 22.6,
  // 06 côté recruteurs
  title6: 23.0, toggle6: 23.5, phone6: 24.1, type6a: 24.4, type6b: 24.9, rennes: 25.1, results: 25.4, discover: 26.0,
  tapCard: 26.3, profile6: 26.5, follow: 27.3, write: 27.8, type6c: 28.0, type6d: 28.9, send: 29.0, notif: 29.5, out6: 30.7,
  // 07 pour qui
  who: 31.0, w1: 31.25, w2: 31.5, w3: 31.75, w4: 32.0, allTrades: 32.4, out7: 32.75,
  // 08 3 étapes
  steps: 33.0, s1: 33.3, c1: 33.6, s2: 33.9, c2: 34.2, s3: 34.5, c3: 34.8, out8: 35.6,
  // 09 tu montres / on te repère
  montres: 36.0, slam: 37.0, out9: 38.3,
  // 10 manoo.fr
  fin: 38.5, lockup: 39.8, pill: 40.2, click: 41.0, tagline: 41.3, cta: 41.7,
};

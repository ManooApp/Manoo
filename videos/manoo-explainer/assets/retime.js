// Voice retiming. Every timing in the film (cues in assets/cues.js and the literal times in the compositions)
// was authored on the Holden take; RETIME maps such a film time to the matching moment of the current take.
// POINTS are [authored time, current time] pairs on the voice's words, written by tools/revoice.py.
// No points = identity: the film plays exactly as authored.
window.RETIME_POINTS = [];
window.RETIME = function (t) {
  const P = window.RETIME_POINTS;
  if (!P.length) return t;
  if (t <= P[0][0]) return t + (P[0][1] - P[0][0]);
  const n = P.length - 1;
  if (t >= P[n][0]) return t + (P[n][1] - P[n][0]);
  let lo = 0, hi = n;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (P[mid][0] <= t) lo = mid; else hi = mid;
  }
  const [a0, a1] = P[lo], [b0, b1] = P[hi];
  return a1 + ((t - a0) * (b1 - a1)) / (b0 - a0);
};

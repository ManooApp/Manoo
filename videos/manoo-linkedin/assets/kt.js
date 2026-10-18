// Manoo LinkedIn — kinetic captions: every word appears at the instant the voice says it (window.VO, assets/cues.js).
// Markup: <div class="kt" data-line="3">Comment montrer <span class="pill">avant l'entretien ?</span></div>
// KT.prep(el) splits the text into .kw spans (pills get their .pb background) and times each word from the line(s)
// named in data-line ("4" or "4,5"); words that the voice does not say take the time of the word before them.
(function () {
  const f = (s) => s.toLowerCase().normalize("NFD").replace(/[^a-z0-9]/g, "");

  function split(el) {
    const words = [];
    const walk = (node) => {
      for (const ch of Array.from(node.childNodes)) {
        if (ch.nodeType === 3) {
          const frag = document.createDocumentFragment();
          for (const p of ch.textContent.split(/\s+/)) {
            if (!p) continue;
            const s = document.createElement("span");
            s.className = "kw";
            s.textContent = p;
            frag.appendChild(s);
            words.push(s);
          }
          node.replaceChild(frag, ch);
        } else if (ch.nodeType === 1 && ch.tagName !== "BR" && !ch.classList.contains("pb")) {
          walk(ch);
        }
      }
    };
    walk(el);
    el.querySelectorAll(".pill").forEach((p) => {
      if (!p.querySelector(".pb")) {
        const b = document.createElement("span");
        b.className = "pb";
        p.insertBefore(b, p.firstChild);
      }
    });
    return words;
  }

  function prep(el) {
    const words = split(el);
    const ids = String(el.dataset.line || "").split(",").map((x) => parseInt(x, 10)).filter((x) => x > 0);
    const vo = [];
    ids.forEach((id) => {
      const l = window.VO.lines.find((x) => x.id === id);
      if (l) l.words.forEach((w) => vo.push({ k: f(w[0]), t: w[1] }));
    });
    let j = 0;
    if (el.dataset.from) {  // a caption that starts mid-sentence: match from that word on
      const k0 = f(el.dataset.from);
      const i0 = vo.findIndex((v) => v.k === k0);
      if (i0 >= 0) j = i0;
    }
    let last = vo.length ? vo[j].t : 0;
    words.forEach((w) => {
      const k = f(w.textContent);
      let hit = -1;
      for (let i = j; i < Math.min(vo.length, j + 8); i++) {
        if (vo[i].k === k || (k.length > 3 && (vo[i].k.startsWith(k) || k.startsWith(vo[i].k)))) { hit = i; break; }
      }
      if (hit >= 0) {
        last = vo[hit].t;
        j = hit + 1;
      }
      w.dataset.t = String(k ? last : last);
    });
    return words;
  }

  // wrap each visual line (tokens between <br>) in a .ln so a growing line can stay centred
  function lines(el) {
    if (el.__ln) return el.__ln;
    const out = [];
    let cur = null;
    for (const ch of Array.from(el.childNodes)) {
      if (ch.nodeType === 1 && ch.tagName === "BR") { cur = null; continue; }
      if (!cur) {
        cur = document.createElement("span");
        cur.className = "ln";
        el.insertBefore(cur, ch);
        out.push(cur);
      }
      cur.appendChild(ch);
    }
    el.__ln = out;
    return out;
  }

  // run fn with every hidden ancestor of el laid out (the runtime hides scenes outside their window, which zeroes
  // every measurement); styles are restored exactly afterwards
  function withLayout(el, fn) {
    const saved = [];
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      if (getComputedStyle(n).display === "none") {
        saved.push([n, n.style.getPropertyValue("display"), n.style.getPropertyPriority("display"), n.style.getPropertyValue("visibility"), n.style.getPropertyPriority("visibility")]);
        n.style.setProperty("display", "block", "important");
        n.style.setProperty("visibility", "hidden", "important");
      }
    }
    try {
      return fn();
    } finally {
      for (const [n, d, dp, v, vp] of saved) {
        if (d) n.style.setProperty("display", d, dp); else n.style.removeProperty("display");
        if (v) n.style.setProperty("visibility", v, vp); else n.style.removeProperty("visibility");
      }
    }
  }

  // word-by-word reveal on timeline tl (times are film seconds; T0 = the scene's start).
  // grow: the line being spoken stays centred (it slides as words arrive) and pills widen with their words.
  function animate(tl, el, T0, opts) {
    return withLayout(el, () => animateLaid(tl, el, T0, opts));
  }

  function animateLaid(tl, el, T0, opts) {
    const o = Object.assign({ dur: 0.22, blur: 10, rise: 0.22, out: null, outDur: 0.2, lead: 0.03, grow: true, caret: false }, opts || {});
    const words = el.__kt || (el.__kt = prep(el));
    const lns = lines(el);
    const T = (w) => Math.max(0, +(parseFloat(w.dataset.t) - T0 - o.lead).toFixed(3));
    gsap.set(words, { opacity: 0 });
    words.forEach((w) => {
      tl.fromTo(w, { opacity: 0, y: `${o.rise}em`, filter: `blur(${o.blur}px)` }, { opacity: 1, y: 0, filter: "blur(0px)", duration: o.dur, ease: "power2.out", immediateRender: false }, T(w));
    });
    // measured once at build time, before anything moves, in layout pixels (independent of any preview scaling)
    const pillFr = new Map();
    el.querySelectorAll(".pill").forEach((p) => {
      const ws = Array.from(p.querySelectorAll(".kw"));
      const pr = p.getBoundingClientRect();
      const pad = 0.12 * parseFloat(getComputedStyle(p).fontSize) * (pr.width / (p.offsetWidth || pr.width));
      pillFr.set(p, ws.map((w, i) => (i === ws.length - 1 ? 1 : Math.min(1, (w.getBoundingClientRect().right - pr.left + pad) / pr.width))));
    });
    const centred = getComputedStyle(el).textAlign === "center";
    const carets = [];
    lns.forEach((ln) => {
      const lr = ln.getBoundingClientRect();
      const k = lr.width ? ln.offsetWidth / lr.width : 1;
      const lw = ln.offsetWidth;
      const ws = words.filter((w) => ln.contains(w));
      if (o.grow && centred && ws.length > 1) {
        const right = (w) => {
          const pill = w.closest(".pill");
          const last = pill && w === Array.from(pill.querySelectorAll(".kw")).pop();
          const r = (last ? pill : w).getBoundingClientRect();
          return (r.right - lr.left) * k;
        };
        const rights = ws.map(right); // measure everything before the line moves
        gsap.set(ln, { x: (lw - rights[0]) / 2 });
        ws.forEach((w, i) => {
          if (i === 0) return;
          tl.to(ln, { x: Math.max(0, (lw - rights[i]) / 2), duration: 0.24, ease: "power2.out" }, T(w));
        });
        if (o.caret) carets.push({ ln, ws, rights, lw });
      }
    });
    el.querySelectorAll(".pill").forEach((p) => {
      const pb = p.querySelector(".pb");
      const ws = Array.from(p.querySelectorAll(".kw"));
      const fr = pillFr.get(p);
      const frac = (w, i) => fr[i];
      gsap.set(pb, { opacity: 0, scaleX: frac(ws[0], 0) * 0.6, transformOrigin: "0% 50%" });
      ws.forEach((w, i) => {
        const at = Math.max(0, T(w) - (i === 0 ? 0.04 : 0));
        if (i === 0) tl.fromTo(pb, { opacity: 0, scaleX: frac(w, 0) * 0.6 }, { opacity: 1, scaleX: frac(w, 0), duration: 0.24, ease: "power3.out", immediateRender: false }, at);
        else tl.to(pb, { scaleX: frac(w, i), duration: 0.24, ease: "power3.out" }, at);
      });
    });
    // a typing caret riding the right edge of the words already spoken
    if (o.caret && carets.length) {
      const c = document.createElement("span");
      c.className = "caret-k";
      el.appendChild(c);
      const fs = parseFloat(getComputedStyle(el).fontSize);
      gsap.set(c, { opacity: 0 });
      let lastT = 0;
      carets.forEach(({ ln, ws, rights, lw }, li) => {
        const x0 = ln.offsetLeft;
        const y = ln.offsetTop + fs * 0.1;
        ws.forEach((w, i) => {
          const x = x0 + (lw - rights[i]) / 2 + rights[i] + fs * 0.06;
          if (i === 0) tl.set(c, { x, y, opacity: 1 }, T(w));
          else tl.to(c, { x, duration: 0.24, ease: "power2.out" }, T(w));
          lastT = T(w);
        });
      });
      tl.to(c, { opacity: 0, duration: 0.01, yoyo: true, repeat: 5, repeatDelay: 0.24, ease: "none" }, lastT + 0.4);
      if (o.out != null) tl.set(c, { opacity: 0 }, +(o.out - T0).toFixed(3));
    }
    if (o.out != null) {
      tl.to(el, { opacity: 0, filter: "blur(10px)", y: -18, duration: o.outDur, ease: "power2.in" }, +(o.out - T0).toFixed(3));
    }
    return words;
  }

  // time (film s) of the first word of a caption whose text matches `word`
  function at(el, word) {
    const words = el.__kt || (el.__kt = prep(el));
    const w = words.find((x) => f(x.textContent) === f(word));
    return w ? parseFloat(w.dataset.t) : null;
  }

  window.KT = { prep, animate, at, norm: f, withLayout };
})();

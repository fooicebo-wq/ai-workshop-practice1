/*
 * 集思影片工作室：影片模板引擎
 * 同一份程式同時給「工作室預覽頁」和「HyperFrames 輸出影片」使用，預覽看到的就是輸出的結果。
 * 需要先載入 gsap.min.js 與 assets.js（window.JISI_ASSETS）。
 */
(function (global) {
  "use strict";

  const PALETTE = [
    { name: "墨綠", hex: "#3F4A45", dark: false },
    { name: "品牌棕褐", hex: "#A28A6C", dark: false },
    { name: "鼠尾草綠", hex: "#5F7D63", dark: false },
    { name: "池水藍", hex: "#4F7A92", dark: false },
    { name: "薰衣草紫", hex: "#766FA8", dark: false },
    { name: "睡蓮粉", hex: "#C07A8A", dark: false },
    { name: "灰色", hex: "#8A8A8A", dark: false },
    { name: "黑色", hex: "#231815", dark: false },
    { name: "白色", hex: "#FFFFFF", dark: true },
    { name: "金色", hex: "#AA8620", dark: true },
  ];
  const SIZES = { landscape: [1920, 1080], portrait: [1080, 1920], square: [1080, 1080] };
  const TEMPLATES = {
    palette: { name: "Logo 色版輪播", duration: 12 },
    intro: { name: "Logo 開場", duration: 6 },
  };
  const MUSIC = {
    none: { name: "不加配樂", file: null },
    light: { name: "輕爽（木吉他＋鋼琴）", file: "light" },
    calm: { name: "沉穩（柔和鋼琴）", file: "calm" },
    cello: { name: "大提琴", file: "cello" },
  };
  const CREAM = "#F3F0E7";
  const DARK_BG = "radial-gradient(ellipse at 50% 42%, #4d5953 0%, #3F4A45 55%, #2f3834 100%)";
  const LOGO_W = 1014, LOGO_H = 354;
  const DEFAULTS = { template: "palette", ratio: "landscape", colors: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], tagline: "空間 · 設計 · 生活", music: "light" };

  function normalize(cfg) {
    const c = Object.assign({}, DEFAULTS, cfg || {});
    if (!SIZES[c.ratio]) c.ratio = DEFAULTS.ratio;
    if (!TEMPLATES[c.template]) c.template = DEFAULTS.template;
    if (!MUSIC[c.music]) c.music = DEFAULTS.music;
    c.colors = (c.colors || []).filter((i) => PALETTE[i]);
    if (c.template === "palette" && c.colors.length < 2) c.colors = DEFAULTS.colors.slice();
    if (c.template === "intro" && c.colors.length < 1) c.colors = [9];
    c.width = SIZES[c.ratio][0];
    c.height = SIZES[c.ratio][1];
    c.duration = TEMPLATES[c.template].duration;
    return c;
  }

  function installFonts() {
    const A = global.JISI_ASSETS;
    if (!A || document.getElementById("jisi-fonts")) return;
    const st = document.createElement("style");
    st.id = "jisi-fonts";
    st.textContent =
      '@font-face{font-family:"JisiSerif";src:url(' + A.serif700 + ') format("woff2");font-weight:700}' +
      '@font-face{font-family:"JisiSerif";src:url(' + A.serif400 + ') format("woff2");font-weight:400}';
    document.head.appendChild(st);
  }

  function el(tag, style, parent, opts) {
    const e = tag === "svg" || tag === "path" || tag === "line" || tag === "rect"
      ? document.createElementNS("http://www.w3.org/2000/svg", tag)
      : document.createElement(tag);
    if (style) Object.assign(e.style, style);
    if (opts) for (const k in opts) e.setAttribute(k, opts[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  // HyperFrames needs each top-level visual to be a timed clip
  function clip(e, dur, track) {
    e.classList.add("clip");
    e.setAttribute("data-start", "0");
    e.setAttribute("data-duration", String(dur));
    e.setAttribute("data-track-index", String(track));
    return e;
  }

  function logoLayer(parent, hex, opacity) {
    const mask = "url(" + global.JISI_ASSETS.mask + ") center / contain no-repeat";
    return el("div", { position: "absolute", inset: "0", background: hex, webkitMask: mask, mask: mask, opacity: String(opacity) }, parent);
  }

  // Left-to-right "brush" reveal using only transforms: a clipping window slides in while
  // its content slides the opposite way, so the logo stays put on any background.
  function revealer(parent) {
    const outer = el("div", { position: "absolute", inset: "0", overflow: "hidden" }, parent);
    const inner = el("div", { position: "absolute", inset: "0" }, outer);
    return {
      inner,
      animate(tl, w, at, dur) {
        tl.fromTo(outer, { x: -w }, { x: 0, duration: dur, ease: "power2.inOut" }, at);
        tl.fromTo(inner, { x: w }, { x: 0, duration: dur, ease: "power2.inOut" }, at);
      },
    };
  }

  function buildPalette(root, c) {
    const W = c.width, H = c.height, D = c.duration;
    const cols = c.colors.map((i) => PALETTE[i]);
    const n = cols.length;
    const s = Math.min(1, (W * 0.8) / LOGO_W);
    const lw = LOGO_W * s, lh = LOGO_H * s;
    const ds = H >= W ? s * 1.35 : s;   // bigger dots on portrait / square canvases
    const DOT = 56 * ds, dot = 28 * ds, ring = 40 * ds, gap = 156 * s;
    const top = (H - (lh + gap + ring)) / 2 - 20 * s;
    const lx = (W - lw) / 2;
    const startDark = cols[0].dark, endDark = cols[n - 1].dark;

    const darkbg = clip(el("div", { position: "absolute", inset: "0", background: DARK_BG, opacity: startDark ? "1" : "0" }, root), D, 0);
    const wrap = clip(el("div", { position: "absolute", left: lx + "px", top: top + "px", width: lw + "px", height: lh + "px" }, root), D, 1);
    const rv = revealer(wrap);
    const logos = cols.map((col, i) => logoLayer(rv.inner, col.hex, i === 0 ? 1 : 0));

    const dots = clip(el("div", { position: "absolute", left: "0", top: top + lh + gap + "px", width: W + "px", height: ring + "px" }, root), D, 2);
    const X0 = W / 2 - ((n - 1) * DOT) / 2;
    cols.forEach((col, i) => {
      el("i", {
        position: "absolute", left: X0 + i * DOT - dot / 2 + "px", top: (ring - dot) / 2 + "px", width: dot + "px", height: dot + "px",
        borderRadius: "50%", background: col.hex, boxShadow: "0 0 0 1px rgba(201,196,182,0.6)",
      }, dots);
    });
    const ringEl = el("div", {
      position: "absolute", left: X0 - ring / 2 + "px", top: "0", width: ring + "px", height: ring + "px",
      borderRadius: "50%", border: Math.max(1.5, 2 * s) + "px solid #8A8A8A", boxSizing: "border-box",
    }, dots);
    const tagline = clip(el("div", {
      position: "absolute", left: "0", width: W + "px", top: top + lh + gap * 0.75 + "px", textAlign: "center",
      fontSize: 40 * s + "px", fontWeight: "400", letterSpacing: "0.7em", paddingLeft: "0.7em",
      color: endDark ? "#E8D9A8" : "#3F4A45", opacity: "0", whiteSpace: "nowrap",
    }, root), D, 4);
    tagline.textContent = c.tagline;

    const tl = gsap.timeline({ paused: true });
    rv.animate(tl, lw, 0.3, 1.6);
    tl.fromTo(wrap, { scale: 0.96 }, { scale: 1, duration: 2.0, ease: "power2.out" }, 0.3);
    tl.fromTo(dots, { opacity: 0, y: 20 * s }, { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }, 1.6);

    // Every color change lands on a 0.72 s music beat; fewer colors = more beats per color
    const START = 2.6, BEAT = 0.72;
    const STEP = BEAT * Math.max(1, Math.floor(9 / (n - 1)));
    for (let i = 1; i < n; i++) {
      const t = START + (i - 1) * STEP;
      tl.to(logos[i - 1], { opacity: 0, duration: 0.5, ease: "sine.inOut" }, t);
      tl.to(logos[i], { opacity: 1, duration: 0.5, ease: "sine.inOut" }, t);
      tl.to(ringEl, { x: i * DOT, duration: 0.5, ease: "sine.inOut" }, t);
      if (cols[i].dark !== cols[i - 1].dark) tl.to(darkbg, { opacity: cols[i].dark ? 1 : 0, duration: 0.5, ease: "power1.inOut" }, t);
    }
    const END = 9.08;
    tl.to(dots, { opacity: 0, duration: 0.5, ease: "power1.in" }, END + 0.6);
    tl.fromTo(tagline, { opacity: 0, y: 16 * s }, { opacity: 1, y: 0, duration: 0.8, ease: "power2.out" }, END + 1.0);
    tl.to(wrap, { scale: 1.04, duration: 1.4, ease: "sine.inOut", yoyo: true, repeat: 1 }, END + 0.6);
    tl.to(root, { opacity: 0, duration: 0.5, ease: "power1.in" }, D - 0.5);
    return tl;
  }

  function buildIntro(root, c) {
    const W = c.width, H = c.height, D = c.duration;
    const col = PALETTE[c.colors[0]];
    const s = Math.min(1, (W * 0.8) / LOGO_W);
    const lw = LOGO_W * s, lh = LOGO_H * s;
    const hs = 0.62 * s, hw = 520 * hs, hh = 360 * hs;
    const tagH = 40 * s;
    const blockH = hh + 50 * s + lh + 70 * s + tagH;
    const top = (H - blockH) / 2;
    const line = col.hex === "#FFFFFF" ? "#E8D9A8" : col.hex;

    clip(el("div", { position: "absolute", inset: "0", background: col.dark ? DARK_BG : CREAM }, root), D, 0);
    const svg = clip(el("svg", { position: "absolute", left: (W - hw) / 2 + "px", top: top + "px" }, root,
      { width: hw, height: hh, viewBox: "0 0 520 360" }), D, 1);
    const shapes = [
      ["path", { d: "M40 170 L260 30 L480 170" }, 4],
      ["path", { d: "M80 150 L80 330 L440 330 L440 150" }, 4],
      ["line", { x1: 80, y1: 240, x2: 250, y2: 240 }, 2],
      ["line", { x1: 250, y1: 170, x2: 250, y2: 330 }, 2],
      ["line", { x1: 330, y1: 240, x2: 440, y2: 240 }, 2],
      ["rect", { x: 300, y: 270, width: 50, height: 60 }, 2],
      ["rect", { x: 130, y: 180, width: 70, height: 40 }, 2],
    ].map(([tag, attrs, w]) => {
      const e = el(tag, null, svg, Object.assign({ fill: "none", stroke: line, "stroke-width": w, "stroke-linecap": "round", "stroke-linejoin": "round", opacity: w === 2 ? 0.7 : 1 }, attrs));
      return e;
    });
    const wrap = clip(el("div", { position: "absolute", left: (W - lw) / 2 + "px", top: top + hh + 50 * s + "px", width: lw + "px", height: lh + "px" }, root), D, 2);
    const rv = revealer(wrap);
    const logo = logoLayer(rv.inner, col.hex, 1);
    const tagline = clip(el("div", {
      position: "absolute", left: "0", width: W + "px", top: top + hh + 50 * s + lh + 70 * s + "px", textAlign: "center",
      fontSize: 40 * s + "px", fontWeight: "400", letterSpacing: "0.7em", paddingLeft: "0.7em",
      color: col.dark ? "#E8D9A8" : "#3F4A45", opacity: "0", whiteSpace: "nowrap",
    }, root), D, 3);
    tagline.textContent = c.tagline;

    const tl = gsap.timeline({ paused: true });
    shapes.forEach((e) => {
      const len = e.getTotalLength();
      gsap.set(e, { strokeDasharray: len, strokeDashoffset: len });
    });
    tl.to(shapes[0], { strokeDashoffset: 0, duration: 0.9, ease: "power2.inOut" }, 0.2);
    tl.to(shapes[1], { strokeDashoffset: 0, duration: 0.9, ease: "power2.inOut" }, 0.5);
    tl.to(shapes.slice(2), { strokeDashoffset: 0, duration: 0.6, ease: "power1.out", stagger: 0.1 }, 1.1);
    rv.animate(tl, lw, 1.7, 1.4);
    tl.fromTo(logo, { opacity: 0.4 }, { opacity: 1, duration: 1.0, ease: "power1.out" }, 1.7);
    tl.fromTo(tagline, { opacity: 0, y: 16 * s }, { opacity: 1, y: 0, duration: 0.8, ease: "power2.out" }, 3.3);
    tl.to([svg, wrap], { scale: 1.03, duration: 1.1, ease: "sine.inOut", yoyo: true, repeat: 1 }, 3.2);
    tl.to(root, { opacity: 0, duration: 0.5, ease: "power1.in" }, D - 0.5);
    return tl;
  }

  function build(root, cfg) {
    const c = normalize(cfg);
    installFonts();
    root.innerHTML = "";
    gsap.set(root, { clearProps: "opacity" });
    Object.assign(root.style, {
      position: "relative", width: c.width + "px", height: c.height + "px", overflow: "hidden",
      background: CREAM, fontFamily: '"JisiSerif", "Noto Serif TC", "Songti TC", serif',
    });
    const tl = c.template === "intro" ? buildIntro(root, c) : buildPalette(root, c);
    return { timeline: tl, config: c };
  }

  global.JisiVideo = { PALETTE, SIZES, TEMPLATES, MUSIC, DEFAULTS, normalize, build };
})(window);

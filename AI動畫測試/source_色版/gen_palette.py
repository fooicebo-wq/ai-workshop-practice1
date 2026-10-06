import sys, json
out = sys.argv[1]
C = [("墨綠","#3F4A45",0),("品牌棕褐","#A28A6C",0),("鼠尾草綠","#5F7D63",0),("池水藍","#4F7A92",0),
     ("薰衣草紫","#766FA8",0),("睡蓮粉","#C07A8A",0),("灰色","#8A8A8A",0),("黑色","#231815",0),
     ("白色","#FFFFFF",1),("金色","#AA8620",1)]
N=len(C); DOT=56; X0=960-(N-1)*DOT/2
logos="".join(f'<div class="logo clip" id="lg{i}" style="background:{c}" data-start="0" data-duration="12" data-track-index="{10+i}"></div>\n' for i,(n,c,d) in enumerate(C))
labels="".join(f'<div class="label clip" id="lb{i}" style="color:{"#F3F0E7" if d else "#3F4A45"}" data-start="0" data-duration="12" data-track-index="{30+i}"><b>{n}</b><span>{c}</span></div>\n' for i,(n,c,d) in enumerate(C))
dots="".join(f'<i style="left:{X0+i*DOT-14}px;background:{c};"></i>' for i,(n,c,d) in enumerate(C))
html=f'''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<script src="gsap.min.js"></script>
<style>
@font-face {{ font-family: "JisiSerif"; src: url("serif700.woff2") format("woff2"); font-weight: 700; }}
@font-face {{ font-family: "JisiSerif"; src: url("serif400.woff2") format("woff2"); font-weight: 400; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #F3F0E7; }}
#root {{ position: relative; width: 100%; height: 100%; background: #F3F0E7; font-family: "JisiSerif", serif; }}
#darkbg {{ position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 42%, #4d5953 0%, #3F4A45 55%, #2f3834 100%); opacity: 0; }}
#logo-wrap {{ position: absolute; left: 453px; top: 250px; width: 1014px; height: 354px; }}
.logo {{ position: absolute; inset: 0; -webkit-mask: url("logo_mask.png") center / contain no-repeat; mask: url("logo_mask.png") center / contain no-repeat; opacity: 0; }}
#lg0 {{ opacity: 1; }}
#brush {{ position: absolute; left: -80px; top: -40px; width: 1300px; height: 434px; background: linear-gradient(90deg, rgba(243,240,231,0) 0px, #F3F0E7 120px); }}
.label {{ position: absolute; top: 700px; width: 100%; text-align: center; opacity: 0; }}
.label b {{ display: block; font-size: 54px; font-weight: 700; letter-spacing: 0.3em; padding-left: 0.3em; }}
.label span {{ display: block; margin-top: 10px; font-size: 30px; font-weight: 400; letter-spacing: 0.25em; padding-left: 0.25em; opacity: 0.75; }}
#dots {{ position: absolute; left: 0; top: 900px; width: 100%; height: 40px; }}
#dots i {{ position: absolute; top: 6px; width: 28px; height: 28px; border-radius: 50%; box-shadow: 0 0 0 1px rgba(201,196,182,0.6); }}
#ring {{ position: absolute; top: 894px; left: {X0-20}px; width: 40px; height: 40px; border-radius: 50%; border: 2px solid #8A8A8A; }}
#tagline {{ position: absolute; top: 720px; width: 100%; text-align: center; font-size: 40px; font-weight: 400; letter-spacing: 0.7em; padding-left: 0.7em; color: #E8D9A8; opacity: 0; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="12" data-width="1920" data-height="1080">
<div id="darkbg" class="clip" data-start="0" data-duration="12" data-track-index="0"></div>
<div id="logo-wrap" class="clip" data-start="0" data-duration="12" data-track-index="1">
{logos}<div id="brush"></div>
</div>
{labels}<div id="dots" class="clip" data-start="0" data-duration="12" data-track-index="2">{dots}</div>
<div id="ring" class="clip" data-start="0" data-duration="12" data-track-index="3"></div>
<div id="tagline" class="clip" data-start="0" data-duration="12" data-track-index="4">空間 · 設計 · 生活</div>
</div>
<script>
const N = {N}, DOT = {DOT}, DARK = {json.dumps([d for _,_,d in C])};
const tl = gsap.timeline({{ paused: true }});

// 1. Brush-stroke reveal of the 墨綠 logo (cream panel slides off to the right)
tl.fromTo("#brush", {{ x: 0 }}, {{ x: 1250, duration: 1.6, ease: "power2.inOut" }}, 0.3);
tl.set("#brush", {{ opacity: 0 }}, 2.0);
tl.fromTo("#logo-wrap", {{ scale: 0.96 }}, {{ scale: 1, duration: 2.0, ease: "power2.out" }}, 0.3);
tl.fromTo("#dots, #ring", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }}, 1.6);
tl.fromTo("#lb0", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 1.7);

// 2. Cycle through every color version
const START = 2.6, STEP = 0.72;
for (let i = 1; i < N; i++) {{
  const t = START + (i - 1) * STEP;
  tl.to("#lg" + (i - 1), {{ opacity: 0, duration: 0.35, ease: "power1.inOut" }}, t);
  tl.to("#lg" + i, {{ opacity: 1, duration: 0.35, ease: "power1.inOut" }}, t);
  tl.to("#lb" + (i - 1), {{ opacity: 0, y: -16, duration: 0.25, ease: "power1.in" }}, t);
  tl.fromTo("#lb" + i, {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }}, t + 0.12);
  tl.to("#ring", {{ x: i * DOT, duration: 0.4, ease: "power3.inOut" }}, t);
  if (DARK[i] && !DARK[i - 1]) tl.to("#darkbg", {{ opacity: 1, duration: 0.5, ease: "power1.inOut" }}, t);
}}

// 3. Finale: 金色 on 墨綠, swap the label for the tagline, breathe, fade out
const END = START + (N - 1) * STEP;
tl.to("#lb" + (N - 1) + ", #dots, #ring", {{ opacity: 0, duration: 0.5, ease: "power1.in" }}, END + 0.6);
tl.fromTo("#tagline", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.8, ease: "power2.out" }}, END + 1.0);
tl.to("#logo-wrap", {{ scale: 1.04, duration: 1.4, ease: "sine.inOut", yoyo: true, repeat: 1 }}, END + 0.6);
tl.to("#root", {{ opacity: 0, duration: 0.5, ease: "power1.in" }}, 11.5);

window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body>
</html>
'''
open(out,"w").write(html)

#!/usr/bin/env python3
"""集思影片工作室：依設定檔輸出影片。

用法：
    python3 render_video.py 設定.json 輸出.mp4

設定檔由「集思影片工作室.html」的「下載設定檔」產生，例如：
    {"template": "palette", "ratio": "portrait", "colors": [0, 2, 3, 9],
     "tagline": "空間 · 設計 · 生活", "music": "light"}

需要 Node.js、FFmpeg；第一次執行會透過 npx 下載 HyperFrames 和 Chrome。
"""
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

STUDIO = os.path.dirname(os.path.abspath(__file__))
HYPERFRAMES = "hyperframes@0.8.135"
SIZES = {"landscape": (1920, 1080), "portrait": (1080, 1920), "square": (1080, 1080)}
DURATIONS = {"palette": 12, "intro": 6}
MUSIC = {"light": "light.wav", "calm": "calm.wav", "cello": "cello.wav"}

PAGE = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={w}, height={h}" />
<script src="gsap.min.js"></script>
<script src="assets.js"></script>
<script src="fonts.js"></script>
<script src="jisi-video.js"></script>
<style>* {{ margin: 0; padding: 0; box-sizing: border-box; }} html, body {{ width: {w}px; height: {h}px; overflow: hidden; background: #F3F0E7; }}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{d}" data-width="{w}" data-height="{h}"></div>
{audio}
<script>
  const result = JisiVideo.build(document.getElementById("root"), {cfg});
  window.__timelines["main"] = result.timeline;
  result.timeline.seek(0);
</script>
</body>
</html>
"""


def fetch_font(text, weight):
    """Download a Noto Serif TC subset covering `text` from Google Fonts as a data URI (None on failure)."""
    try:
        q = urllib.parse.quote(text)
        req = urllib.request.Request(
            f"https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@{weight}&text={q}",
            headers={"User-Agent": "Mozilla/5.0 Chrome/120"},
        )
        css = urllib.request.urlopen(req, timeout=15).read().decode()
        url = re.search(r"url\((https://fonts\.gstatic\.com[^)]+)\)", css).group(1)
        data = urllib.request.urlopen(url, timeout=15).read()
        return "data:font/woff2;base64," + base64.b64encode(data).decode()
    except Exception as e:  # keep rendering with the bundled subset
        print("字型下載失敗，改用內建字型：", e)
        return None


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    cfg_path, out_path = sys.argv[1], os.path.abspath(sys.argv[2])
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    template = cfg.get("template", "palette")
    w, h = SIZES.get(cfg.get("ratio", "landscape"), SIZES["landscape"])
    d = DURATIONS.get(template, 12)
    music = MUSIC.get(cfg.get("music", "light"))

    work = tempfile.mkdtemp(prefix="jisi-render-")
    try:
        for name in ("gsap.min.js", "assets.js", "jisi-video.js"):
            shutil.copy(os.path.join(STUDIO, name), work)
        # The bundled font only covers the default text; fetch glyphs for a custom tagline
        tagline = cfg.get("tagline", "")
        fonts = {"serif400": fetch_font(tagline, 400)} if tagline.strip() else {}
        with open(os.path.join(work, "fonts.js"), "w", encoding="utf-8") as f:
            for key, uri in fonts.items():
                if uri:
                    f.write(f'window.JISI_ASSETS.{key} = "{uri}";\n')
        audio = ""
        if music:
            shutil.copy(os.path.join(STUDIO, "music", music), os.path.join(work, "bgm.wav"))
            fade = ' data-fade-out="1"' if d < 12 else ""
            audio = f'<audio id="bgm" class="clip" src="bgm.wav" data-start="0" data-duration="{d}" data-track-index="50" data-volume="1"{fade}></audio>'
        with open(os.path.join(work, "index.html"), "w", encoding="utf-8") as f:
            f.write(PAGE.format(w=w, h=h, d=d, audio=audio, cfg=json.dumps(cfg, ensure_ascii=False)))
        with open(os.path.join(work, "hyperframes.json"), "w", encoding="utf-8") as f:
            json.dump({"name": "jisi-studio"}, f)
        env = dict(os.environ, HYPERFRAMES_SKIP_SKILLS="1")
        npx = "npx.cmd" if os.name == "nt" else "npx"
        subprocess.run([npx, "--yes", HYPERFRAMES, "render", "-q", "delivery", "-o", out_path], cwd=work, env=env, check=True)
        print("完成：", out_path)
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

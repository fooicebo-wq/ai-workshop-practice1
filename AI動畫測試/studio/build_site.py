#!/usr/bin/env python3
"""把集思影片工作室打包成可直接部署到 Vercel 的靜態網站。

用法（在專案根目錄）：
    python3 AI動畫測試/studio/build_site.py

輸出到 jisi-video-studio/：
    index.html            工作室頁面
    studio/*.js           動畫引擎與內嵌素材
    studio/music/*.mp3    配樂（由 wav 轉成 mp3 縮小檔案）
    videos/*.mp4          作品庫影片（改成英文檔名，網址比較穩定）
需要 FFmpeg。
"""
import os
import shutil
import subprocess

STUDIO = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(STUDIO)                       # AI動畫測試/
ROOT = os.path.dirname(SRC)                         # repo root
OUT = os.path.join(ROOT, "jisi-video-studio")

VIDEOS = {
    "集思Logo色版輪播_輕爽版.mp4": "palette-light.mp4",
    "集思Logo色版輪播.mp4": "palette-calm.mp4",
    "集思Logo色版輪播_大提琴版.mp4": "palette-cello.mp4",
    "範例_Logo開場.mp4": "intro-gold.mp4",
    "範例_直式色版輪播.mp4": "palette-portrait.mp4",
    "範例_方形色版輪播.mp4": "palette-square.mp4",
    "集思Logo開場動畫.mp4": "intro-v1.mp4",
}


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "studio", "music"))
    os.makedirs(os.path.join(OUT, "videos"))

    for name in ("gsap.min.js", "assets.js", "jisi-video.js"):
        shutil.copy(os.path.join(STUDIO, name), os.path.join(OUT, "studio", name))

    for wav in sorted(os.listdir(os.path.join(STUDIO, "music"))):
        if wav.endswith(".wav"):
            mp3 = os.path.join(OUT, "studio", "music", wav[:-4] + ".mp3")
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(STUDIO, "music", wav),
                            "-codec:a", "libmp3lame", "-b:a", "160k", mp3], check=True)

    with open(os.path.join(SRC, "集思影片工作室.html"), encoding="utf-8") as f:
        html = f.read()
    for src, dst in VIDEOS.items():
        shutil.copy(os.path.join(SRC, src), os.path.join(OUT, "videos", dst))
        html = html.replace('src="' + src + '"', 'src="videos/' + dst + '"')
    replacements = [
        ('MUSIC_EXT = ".wav"', 'MUSIC_EXT = ".mp3"'),
        ('把指令貼給 Claude，或在電腦上執行 <code>python3 studio/render_video.py 設定.json 輸出.mp4</code>',
         '把指令貼給 Claude 即可輸出 MP4；設定檔也可以在專案的 <code>AI動畫測試/studio/render_video.py</code> 自行輸出'),
    ]
    for a, b in replacements:
        assert a in html, a
        html = html.replace(a, b)
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    with open(os.path.join(OUT, "vercel.json"), "w", encoding="utf-8") as f:
        f.write('{\n  "cleanUrls": true,\n  "headers": [\n    { "source": "/videos/(.*)", "headers": [{ "key": "Cache-Control", "value": "public, max-age=86400" }] },\n'
                '    { "source": "/studio/music/(.*)", "headers": [{ "key": "Cache-Control", "value": "public, max-age=86400" }] }\n  ]\n}\n')
    print("完成：", OUT)


if __name__ == "__main__":
    main()

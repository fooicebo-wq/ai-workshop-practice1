# 影片剪輯 Skill 研究筆記

- 整理日期：2026-10-07
- 來源：網路搜尋（Claude Skill 登錄站、GitHub 原始 SKILL.md）、Anthropic 外掛目錄
- 目的：找出能讓 Claude 協助剪輯影片的 skill，整理用法，作為之後打造「集思專屬剪輯 skill」的參考

## 目錄

1. [核心觀念](#1-核心觀念)
2. [現成 Skill／外掛清單](#2-現成-skill外掛清單)
3. [標準剪輯流程（六層）](#3-標準剪輯流程六層)
4. [FFmpeg 常用指令速查](#4-ffmpeg-常用指令速查)
5. [社群平台尺寸](#5-社群平台尺寸)
6. [自動剪短影音（Auto-Clipper）做法](#6-自動剪短影音auto-clipper做法)
7. [Remotion：用程式做片頭、字卡、動畫](#7-remotion用程式做片頭字卡動畫)
8. [與本工作區的關聯](#8-與本工作區的關聯)
9. [待確認項目](#9-待確認項目)

---

## 1. 核心觀念

- **Skill = 一個資料夾**，裡面有 `SKILL.md`（教 Claude 怎麼做某件事的說明書）＋輔助腳本。安裝方式通常是複製到 `~/.claude/skills/`，之後可用 `/指令名稱` 呼叫。
- **AI 剪輯的價值是「壓縮與整理」，不是「憑空生成」**：讓 Claude 讀逐字稿、找出精華段落、產生剪輯指令；最後的節奏與美感仍由人決定。
- **FFmpeg 是骨幹**：裁切、合併、轉檔、音量標準化都靠它（本環境已安裝 `/usr/bin/ffmpeg`）。

## 2. 現成 Skill／外掛清單

| 名稱 | 類型 | 用途 | 執行位置 / 需求 |
|---|---|---|---|
| video-editing（affaan-m/everything-claude-code） | Skill | 完整剪輯流程：逐字稿 → FFmpeg 剪接 → Remotion 疊字 → 配音 → CapCut 收尾 | 本機，需 FFmpeg |
| Remotion Agent Skills（remotion-dev/skills） | Skill 套件（12 個） | 用 React 程式做片頭、字卡、字幕、地圖動畫並算圖 | 本機，需 Node.js；`npx skills add remotion-dev/skills` |
| auto-clipper（clipper） | Skill | 長影片自動切成 9:16 短影音，含評分挑精華 | 本機，FFmpeg + faster-whisper，免 API Key |
| ffmpeg-media / ffmpeg-cli / edit-cut-video-ffmpeg | Skill | FFmpeg 指令產生、轉檔、修剪、音畫同步修正 | 本機 |
| stitch-videos-ffmpeg | Skill | 多段影片拼接 | 本機 |
| AI Video Editor & Timeline（ManyMotions） | 外掛 | 多軌時間軸、轉場、燒字幕、匯出 MP4 | 雲端，需 ManyMotions 帳號 |
| Video Cleanup | 外掛 | 語音降噪、音量、畫質、Logo 浮水印、名字字卡、片尾卡 | 本機，需 Python + FFmpeg |
| ffmpeg-llm | 外掛 | 中文描述 → 產生 FFmpeg 指令 | 本機 |
| videodb | 外掛 | 上傳、搜尋、剪輯、字幕、智慧轉直式 | 雲端，需 VideoDB API Key |
| video-shotcraft | 外掛 | Remotion 產品宣傳片鏡頭範本 | 本機 |
| watch-video | 外掛 | 讓 Claude「看」影片：關鍵影格 + 語音轉文字 | 本機 |

## 3. 標準剪輯流程（六層）

摘自 `video-editing` skill，原則是「每一層做一件事，不要跳層」。

| # | 層級 | 工具 | 工作內容 |
|---|---|---|---|
| 1 | 素材收集 | 手機／相機／螢幕錄影 | 原始檔案集中 |
| 2 | 整理規劃 | Claude | 逐字稿、標記主題、找出廢段、產出剪輯清單（時間碼） |
| 3 | 確定性剪接 | FFmpeg | 裁切、合併、做 Proxy、抽音軌、音量標準化 |
| 4 | 程式化合成 | Remotion | 片頭、字卡、Logo、名字條、數據動畫 |
| 5 | 補充素材 | ElevenLabs／fal.ai | 旁白配音、背景音樂、音效、B-roll（只補缺的） |
| 6 | 人工收尾 | CapCut／Descript | 節奏、字幕校對、調色、混音、匯出 |

**六大原則**：剪輯而非生成、先結構後風格、FFmpeg 是骨幹、重複做的事寫成 Remotion 元件、選擇性生成、品味留給人。

## 4. FFmpeg 常用指令速查

| 用途 | 指令 |
|---|---|
| 依時間碼裁一段 | `ffmpeg -i raw.mp4 -ss 00:12:30 -to 00:15:45 -c copy seg01.mp4` |
| 合併多段 | `for f in segments/*.mp4; do echo "file '$f'"; done > concat.txt` 後 `ffmpeg -f concat -safe 0 -i concat.txt -c copy out.mp4` |
| 做低解析 Proxy | `ffmpeg -i raw.mp4 -vf "scale=960:-2" -c:v libx264 -preset ultrafast -crf 28 proxy.mp4` |
| 抽音軌（給語音辨識） | `ffmpeg -i raw.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav` |
| 音量標準化 | `ffmpeg -i in.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:v copy out.mp4` |
| 偵測換景 | `ffmpeg -i in.mp4 -vf "select='gt(scene,0.3)',showinfo" -vsync vfr -f null - 2>&1 \| grep showinfo` |
| 偵測靜音（剪掉空白） | `ffmpeg -i in.mp4 -af silencedetect=noise=-30dB:d=2 -f null - 2>&1 \| grep silence` |
| 16:9 轉 9:16（置中裁切） | `ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" vertical.mp4` |
| 16:9 轉 1:1 | `ffmpeg -i in.mp4 -vf "crop=ih:ih,scale=1080:1080" square.mp4` |

批次剪接（`cuts.txt` 每行：`開始,結束,名稱`）：

```bash
while IFS=, read -r start end label; do
  ffmpeg -i raw.mp4 -ss "$start" -to "$end" -c copy "segments/${label}.mp4"
done < cuts.txt
```

> 注意：`-c copy` 速度快但只能切在關鍵影格，若要精準到影格，需改成重新編碼（`-c:v libx264 -crf 18`）。

## 5. 社群平台尺寸

| 平台 | 比例 | 解析度 |
|---|---|---|
| YouTube | 16:9 | 1920×1080 |
| TikTok／Reels／Shorts | 9:16 | 1080×1920 |
| Instagram 貼文 | 1:1 | 1080×1080 |
| X | 16:9 或 1:1 | 1280×720／720×720 |

## 6. 自動剪短影音（Auto-Clipper）做法

| 步驟 | 內容 |
|---|---|
| 1. 逐字稿 | faster-whisper 本機轉錄，取得「逐字」時間碼 |
| 2. 評分 | 每個候選片段依評分表打分（見下表） |
| 3. 精準剪 | 依逐字時間碼切，不切到半句話 |
| 4. 轉直式 | 人臉追蹤裁切，或「pad 模式」：16:9 原畫置中、背景放模糊版 |
| 5. 輸出規格 | 1080×1920、24fps、H.264 CRF 18、音量 -14 LUFS |

| 評分項目 | 配分 |
|---|---|
| 開頭吸引力（Hook） | 30 |
| 能否獨立看懂 | 25 |
| 情緒張力 | 20 |
| 節奏 | 15 |
| 結尾收束 | 10 |

## 7. Remotion：用程式做片頭、字卡、動畫

- 安裝：`npx skills add remotion-dev/skills`（或 `bun create video` 建專案時勾選）
- 概念：影片 = React 元件，畫面是「第幾格」的函數；`<Sequence>` 安排時間軸、`<Video>` 放素材
- 算圖：`npx remotion render src/index.ts 組合名稱 output.mp4`
- 適合：片頭片尾、Logo、名字條、數據動畫、可重複套用的模板；**不適合**一般實拍剪輯

| 子 Skill | 用途 |
|---|---|
| /remotion-best-practices | 總合，不確定用哪個時用它 |
| /remotion-create | 建立新專案／組合 |
| /remotion-markup | 動畫、排版、字型、音訊等寫法 |
| /remotion-captions | 字幕 |
| /remotion-render | 算圖輸出 |
| /remotion-studio | 開啟預覽 |
| /remotion-maps | 地圖、路線動畫 |
| /remotion-docs | 查官方文件 |

## 8. 與本工作區的關聯

- 現有 `jisi-video-studio/` 已用 **GSAP + 網頁** 做出片頭與色票影片（`videos/intro-gold.mp4`、`palette-*.mp4`），概念與 Remotion 相同（程式化動畫），可延續。
- 建議的「集思專屬剪輯 skill」雛形：
  1. 施工紀錄影片 → Claude 讀逐字稿／換景點，產出剪輯清單
  2. FFmpeg 批次剪接 + 音量標準化
  3. 套用 `jisi-video-studio` 的片頭與 Logo
  4. 依平台輸出 16:9／9:16／1:1 三種版本

## 9. 待確認項目

| # | 項目 | 說明 |
|---|---|---|
| 1 | 主要剪輯題材 | 施工紀錄？完工介紹？社群短影音？決定 skill 方向 |
| 2 | 部分網站無法讀取 | tella.com、vibeindex.ai、openskillindex.com 被網路政策擋住，auto-clipper 內容取自搜尋摘要，未讀到原始 SKILL.md |
| 3 | 外掛安全性 | 目錄中外掛多為社群作者發布，啟用前需確認 |
| 4 | 語音辨識 | faster-whisper 尚未安裝，需要時再裝 |

---

**參考來源**
- [affaan-m/everything-claude-code：video-editing SKILL.md](https://github.com/affaan-m/everything-claude-code)
- [remotion-dev/skills](https://github.com/remotion-dev/skills)、[Remotion Agent Skills 文件](https://www.remotion.dev/docs/ai/skills)
- [Claude Code skills for video（Tella）](https://www.tella.com/skills)
- [claudskills.com：ffmpeg-media](https://claudskills.com/skills/ffmpeg-media/)、[edit-cut-video-ffmpeg](https://claudskills.com/skills/edit-cut-video-ffmpeg/)
- [claudeskills.info：stitch-videos-ffmpeg](https://claudeskills.info/zh-hant/skills/gooseworks-ai/goose-skills/stitch-videos-ffmpeg/)、[video-processing](https://claudeskills.info/zh-hant/skills/guia-matthieu/clawfu-skills/video-processing/)
- [openskillindex.com：auto-clipper](https://openskillindex.com/skills/clawdbot-skills-auto-clipper)
- [OpenReplay：Making videos with Claude Code + Remotion](https://blog.openreplay.com/making-videos-claude-code-remotion/)

*整理工具：Claude Code｜整理日期：2026-10-07*

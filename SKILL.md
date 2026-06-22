---
name: audio-to-obsidian
description: Download audio from B站/YouTube/Xiaoyuzhou/Douyin/any public URL, transcribe with faster-whisper, produce structured learning notes, save into Obsidian, and optionally export as PDF. Use when the user wants to convert any spoken content into text notes.
platforms: [windows, linux, macos]
---

# Audio / Video → Obsidian Study Notes ( + PDF )

Turn any public audio or video into a structured learning note in Obsidian. Optionally export as a clean PDF.

## When To Use

User provides:
- A URL (B站, YouTube, Xiaoyuzhou, Douyin, or any public audio link)
- A local audio/video file
- And wants structured notes in their Obsidian vault

## Step 0 — Bootstrap (first-run self-check)

**BEFORE touching any URL, check that all tools are available. Install what's missing.**

### 0.1 — Check Python + venv

```bash
python3 --version   # or python --version on Windows
```

If < 3.10: tell user "需要 Python 3.10+，当前版本不满足。去 python.org 下载安装。"

### 0.2 — Check ffmpeg

```bash
ffmpeg -version 2>&1 | head -1
```

If missing:
- **macOS**: `brew install ffmpeg`
- **Linux**: `apt install ffmpeg` / `dnf install ffmpeg`
- **Windows**: Guide user to download from [ffmpeg.org](https://ffmpeg.org), or auto-download the essentials build:

```bash
# Auto-install ffmpeg essentials on Windows (portable, no admin needed)
curl -L -o ffmpeg.zip "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
unzip -q ffmpeg.zip && mv ffmpeg-*-essentials_build ffmpeg_build
export PATH="$PWD/ffmpeg_build/bin:$PATH"
```

If auto-install fails or user prefers manual: tell them "需要 ffmpeg，去 https://ffmpeg.org 下载。把 bin 目录加入 PATH 即可。"

### 0.3 — Check Python tools (faster-whisper, yt-dlp, you-get)

```bash
# Check each in one sweep
python3 -c "import faster_whisper; print('faster-whisper OK')" 2>&1
yt-dlp --version 2>&1 | head -1
you-get --version 2>&1 | head -1
```

If any missing, create venv (if not already) and install:

```bash
# Create venv if needed
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install all Python deps
pip install faster-whisper yt-dlp you-get
```

### 0.4 — Check pandoc (optional — for PDF export)

```bash
pandoc --version 2>&1 | head -1
```

If missing and user wants PDF:
- **macOS**: `brew install pandoc wkhtmltopdf`
- **Linux**: `apt install pandoc wkhtmltopdf`
- **Windows**: `winget install Pandoc.Pandoc` + manual wkhtmltopdf from https://wkhtmltopdf.org

If pandoc is unavailable, skip PDF export silently — the .md note is the primary deliverable. PDF is an optional bonus.

### 0.5 — HuggingFace model cache

On first transcription run, faster-whisper auto-downloads the model from HuggingFace Hub (~75MB for `tiny`, cached to `~/.cache/huggingface/`).

**Proxy note** (mainland China): if HuggingFace is blocked, set proxy before transcribing:
```bash
export HTTPS_PROXY=http://127.0.0.1:7897
```

### 0.6 — Obsidian Vault config

The agent needs to know where to save notes. Ask the user once, or read from `.env`:

```
OBSIDIAN_VAULT=/path/to/Obsidian/vault
PODCAST_NOTES_DIR=<OBSIDIAN_VAULT>/Podcast Notes
```

Default convention: `Podcast Notes/` is a top-level folder inside the vault.

**Only after all checks pass** → proceed to the main workflow. This bootstrap runs ONCE — on subsequent runs, tools are already installed and you skip directly to Step 1.

## Workflow

### Step 1 — Identify Source & Get Audio

Determine what the user gave you:

#### A. B站 (bilibili.com)

**Primary tool**: `you-get` (yt-dlp is blocked by HTTP 412 WBI anti-bot for single videos).

```bash
# 1. Check available formats
you-get --info "<B站_URL>"

# 2. Pick smallest DASH stream — prefer HEVC (dash-flv360-HEVC)
you-get --format=dash-flv360-HEVC -o ./work "<URL>"

# 3. Extract audio from mp4
ffmpeg -i "<video.mp4>" -vn -acodec libmp3lame -q:a 2 "<output.mp3>" -y

# 4. DELETE video immediately after audio extraction succeeds
rm "<video.mp4>"
```

- **Without B站 login**, only video-only DASH streams (360P/480P). No audio-only track.
- **AV1 format sometimes hangs** — prefer HEVC. Fall back to AVC.
- Audio quality from 360P is sufficient for `tiny` model transcription.
- If user provides B站 cookies: `you-get --cookies cookies.txt "<URL>"` unlocks higher quality.

For B站 series/collections, skip to 「Series Batch Processing」 section below.

#### B. YouTube / Douyin

Use yt-dlp for audio-only extraction:
```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 \
  -o "./work/%(title).100s.%(ext)s" "<URL>"
```

Douyin has no anti-bot issues with yt-dlp (confirmed).

#### C. Xiaoyuzhou (小宇宙)

Episode pages embed the audio URL in `<meta property="og:audio">`:
```bash
curl -sL -A "Mozilla/5.0 (compatible; podcast-to-obsidian/1.0)" "<URL>" \
  | grep -oP 'property="og:audio"\s+content="\K[^"]+'
```
Then download: `curl -L -o ./work/audio.mp3 "<AUDIO_URL>"`

See `references/xiaoyuzhou-extraction.md` for details.

#### D. Direct audio URL

```bash
curl -L -o "./work/audio.mp3" "<URL>"
```

#### E. Local file

Use the path directly. Skip download.

### Step 2 — Transcribe

```bash
python3 transcribe.py \
  --audio "<AUDIO_FILE>" \
  --out-dir "./work/<slug>" \
  --model tiny \
  --language zh
```

For English content:
```bash
python3 transcribe.py --audio "<FILE>" --out-dir "./work/<slug>" --model tiny --language en
```

**Progress monitoring**: stdout shows progress every 3 minutes of audio processed.

**Model selection**:
- `tiny` (~75MB): fastest, 3-8x realtime, adequate for clean audio
- `small` (~500MB): 2-3x slower, better for noisy audio or mixed-language content
- `medium` (~1.5GB): significantly slower, use only when accuracy is critical

**First-run note**: model downloads from HuggingFace on first use. Proxy may be needed.

### Step 3 — Summarize

Read the transcript and write a structured study note. **Depth expectation**: book-breakdown level, not a surface TL;DR.

**What to KEEP (all substantive content)**:
- Every framework, formula, model, or numbered list
- Every named concept (e.g. "债券型人生", "心理账户")
- Every specific example, case study, or story used to illustrate a point
- Every concrete number or data point
- Every dialogue exchange where the interviewer challenges or redirects
- Every definition and explanation
- Every philosophical reflection or worldview statement

**What to REMOVE (noise only)**:
- Greetings, introductions, sign-offs
- Repeated filler words, false starts
- Sponsor reads, channel promotions, like-and-subscribe calls
- Side chatter that doesn't advance any topic

**Semantic review**: After reading the full transcript, scan for phrases that don't make semantic sense. For each suspect phrase, append `[?]` and add to a "待确认" section at the bottom:
```markdown
## 待确认
- 「可疑短语」→ 可能应为「推测的正确短语」（依据）
```

**Do NOT silently guess corrections** — mark and surface to the user.

**Tiny model known failure modes** (Chinese): near-homophones like shùfù→shūběn, zhuānkuài→zhuāngkuài. Use context to identify these but flag rather than fix.

**Note template**:
```markdown
# <Episode Title>

**来源**: <URL>
**播客/频道**: <Show Name>
**嘉宾**: <Guests>
**时长**: <Duration>
**整理日期**: <Today>
**转写模型**: faster-whisper <model>

## 一句话
<One sentence thesis>

## 对话结构

### 第一阶段：<Phase Title>（timestamp range）
<Dialogue excerpts + analysis>

**金句**
- 「...」

[... more phases ...]

## 核心洞察

### 1. <Insight Title>
<Analysis>

## 可落地的动作
- <concrete, framework-level action>

## 思考题
1. <open question drawn from the episode's tensions>
2. ...
```

**Required footer**: Every note MUST end with both **可落地的动作** (3-5 concrete actions) and **思考题** (5-7 open questions).

### Step 4 — Save to Obsidian

**Folder structure** — shows get a folder; each episode gets its own subfolder:

```
<PODCAST_NOTES_DIR>/
├── _Index.md
├── <Show Name>/
│   └── <Episode Title>/
│       ├── <Episode Title>.md           ← study note
│       └── <Episode Title> transcript.md ← full transcript
```

**Critical rules**:
- One folder per episode (not one folder per show with flat files)
- Transcript filename = `<title> transcript.md` (never just `transcript.md`)
- Episode folder matches the note title exactly

**Update global index**: Append to `_Index.md`:
```markdown
- [[<Show Name>/<Episode Title>/<Episode Title>]]：<one-line summary>
```

### Step 4.5 — Export PDF (optional)

If the user asked for PDF output, or says "导出 PDF", render the study note as a clean PDF.

**Requirements**: `pandoc` + `wkhtmltopdf` (checked in bootstrap 0.4). If unavailable, skip and tell user.

```bash
pandoc "<note.md>" \
  --pdf-engine=wkhtmltopdf \
  --metadata title="<Episode Title>" \
  -V lang=zh \
  -V mainfont="Noto Sans CJK SC" \
  -o "<note.pdf>"
```

**For Chinese PDF**: wkhtmltopdf handles CJK fonts natively. If Chinese characters render as boxes, install Noto CJK fonts:
- macOS: `brew install font-noto-sans-cjk-sc`
- Linux: `apt install fonts-noto-cjk`
- Windows: already supported via system fonts

**PDF placement**: same folder as the .md note:
```
<Episode Title>/
├── <Episode Title>.md
├── <Episode Title>.pdf          ← exported PDF
└── <Episode Title> transcript.md
```

### Step 5 — Cleanup

Only after user confirms the note is satisfactory:
```bash
rm -rf ./work/*
```

## Series Batch Processing

When the user provides a B站 合集/series URL or YouTube playlist:

### B站 collections

```bash
yt-dlp --flat-playlist --dump-json "https://space.bilibili.com/<uid>/lists/<id>?type=season"
```

Returns all videos with `id` (BV), `url`, `playlist_index`. Order is oldest→newest (index 1 = first video). Works without anti-bot issues.

### YouTube playlists

```bash
yt-dlp --flat-playlist --dump-json "<playlist_URL>"
```

**Processing flow**:
1. Extract all video URLs
2. Present the list to user for confirmation
3. Process one by one: download → extract audio → transcribe → write note
4. Each episode in its own subfolder

See `references/bilibili-batch-retrieval.md` for detailed findings.

## Platform-Specific Notes

### B站 (bilibili.com)
- yt-dlp blocked by HTTP 412 WBI anti-bot for single videos — use `you-get`
- `you-get` can appear stuck with zero stdout for 1-3 minutes; do NOT kill prematurely
- AV1 format sometimes hangs → prefer HEVC
- `you-get --info` may also hang on some videos → skip and try direct download
- CC subtitles often require login (`need_login_subtitle: True`) — see `references/bilibili-subtitle-login.md`
- B站 page HTML is gzip-compressed (magic bytes `1f 8b`)
- `.cmt.xml` file from you-get is danmaku, NOT CC subtitles

### Xiaoyuzhou (小宇宙)
- Audio in `<meta property="og:audio">` — direct curl extraction for public episodes
- Hosted on `media.xyzcdn.net` — MP3 format

### YouTube
- `yt-dlp` works. May need `--extractor-args "youtube:player_client=web"` for some videos

### 抖音 (douyin.com)
- `yt-dlp` works directly. No anti-bot issues observed.

## References

- `references/xiaoyuzhou-extraction.md` — detailed 小宇宙 audio extraction
- `references/bilibili-anti-bot.md` — B站 anti-bot diagnostics & workarounds
- `references/bilibili-batch-retrieval.md` — B站 series batch scraping
- `references/bilibili-subtitle-login.md` — B站 CC subtitle login wall

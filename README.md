# 🎧 Audio → Obsidian ( + PDF )

**Any public audio or video → structured learning notes in Obsidian. Optionally export as a clean PDF.**

Turn B站 videos, YouTube episodes, 小宇宙 podcasts, 抖音 clips — any public audio URL — into clean, structured notes powered by local [faster-whisper](https://github.com/SYSTRAN/faster-whisper) transcription. No API keys. No paywalls. Your notes, your vault, your PDF.

---

## What It Does

```
URL (B站 / YT / 小宇宙 / 抖音 / any public audio)
  → download audio
    → transcribe locally (faster-whisper tiny)
      → produce structured learning note (.md)
        → save to Obsidian + update index
          → optionally export as clean PDF
```

### Output per episode

```
Podcast Notes/
├── _Index.md                              ← global index
├── 姜Dora/
│   └── 收入配置法 大卫翁/
│       ├── 收入配置法 大卫翁.md           ← study note
│       ├── 收入配置法 大卫翁.pdf           ← optional PDF export
│       └── 收入配置法 大卫翁 transcript.md ← full transcript
```

Every note includes:

- **Dialogue excerpts** with speaker labels — not just AI paraphrasing
- **Golden sentences (金句)** pulled from the conversation
- **Core insights** — thematic synthesis across the full episode
- **Thinking questions (思考题)** — open questions to provoke reflection
- **Actionable steps (可落地的动作)** — concrete things to do tomorrow

**PDF export** renders the study note as a clean, print-ready document — suitable for sharing, archiving, or reading offline. Uses [Pandoc](https://pandoc.org) with `wkhtmltopdf` or LaTeX backend.

---

## Platforms Tested

| Platform | Method | Status |
|----------|--------|--------|
| B站 | `you-get` download → ffmpeg extract | ✅ |
| YouTube | `yt-dlp` audio extraction | ✅ |
| 小宇宙 | curl `og:audio` → direct download | ✅ |
| 抖音 | `yt-dlp` direct download | ✅ |
| Any public audio URL | curl → transcribe | ✅ |

B站 series/collection batch processing also supported: paste a 合集 URL and extract all episodes at once.

---

## Quick Start

### 1. Prerequisites

- **Python 3.10+**
- **ffmpeg** (in PATH)
- **Obsidian** vault (or any folder-based note system)
- **Pandoc** (optional — for PDF export)

### 2. Install

**Option A — Let the AI agent bootstrap itself**

If you're using this with an AI coding agent (Codex / Claude Code / Hermes), just load the skill and paste a URL. The agent auto-detects missing tools and installs them before processing. Zero manual setup.

**Option B — Manual install**

```bash
git clone https://github.com/YOUR_USER/audio-to-obsidian.git
cd audio-to-obsidian

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install faster-whisper yt-dlp you-get
```

For PDF export:
```bash
# macOS
brew install pandoc wkhtmltopdf

# Linux
apt install pandoc wkhtmltopdf

# Windows
winget install Pandoc.Pandoc
# + install wkhtmltopdf from https://wkhtmltopdf.org
```

### 3. Transcribe

```bash
python transcribe.py \
  --audio episode.mp3 \
  --out-dir ./work/my-episode \
  --model tiny \
  --language zh
```

Output: `transcript.md` + `transcript.json`

### 4. Use with AI (Codex / Claude Code / Hermes)

This repo includes a `SKILL.md` — a structured prompt that teaches AI agents the full pipeline. Load it into any AI coding agent:

- **Codex**: Place SKILL.md in your skills directory
- **Claude Code**: Add to `.claude/skills/`
- **Hermes Agent**: `hermes skills install audio-to-obsidian`

The agent handles everything: tool bootstrap → platform detection → download → transcription → summarization → Obsidian save → optional PDF export. You just paste a URL.

### 5. Export PDF (optional)

```bash
pandoc "study-note.md" \
  --pdf-engine=wkhtmltopdf \
  --css=references/pdf-style.css \
  -o "study-note.pdf"
```

Or let the AI agent do it — say "导出 PDF" after the note is written.

---

## Configuration

Before first use, set Obsidian vault path in the SKILL.md or tell your AI agent:

```
OBSIDIAN_VAULT=/Users/you/Obsidian/
PODCAST_NOTES_DIR=<OBSIDIAN_VAULT>/Podcast Notes/
```

For proxy users (中国大陆):

```bash
export HTTPS_PROXY=http://127.0.0.1:7897
# Needed for HuggingFace model download on first run
```

---

## transcribe.py

A single-file CLI (104 lines) wrapping faster-whisper:

```
usage: transcribe.py [-h] --audio AUDIO --out-dir OUT_DIR
                     [--model {tiny,small,medium,large-v3}]
                     [--language {zh,en,ja,...}]
```

- Progress printed every 3 minutes of audio processed
- Output: `transcript.md` (timestamped segments) + `transcript.json` (machine-readable)
- `tiny` model: ~75MB, 3-8x realtime on CPU
- Runs entirely offline after first model download

---

## Notes on Quality

- **tiny model** is fast but imperfect for Chinese — especially near-homophones (shùfù → shūběn, zhuānkuài → zhuāngkuài). The skill includes a semantic review step with `[?]` flagging for uncertain phrases.
- For higher accuracy, use `--model small` (2-3x slower, better Chinese recognition).
- B站 CC subtitles may require login — the skill documents how to check and handle this.

---

## License

MIT

---

## Author

Built for people who prefer reading over listening, and structured notes over raw transcripts.

If you find this useful, ⭐ the repo.

# B站 Anti-Bot Diagnostics

## Error Patterns & Solutions

### HTTP 412 Precondition Failed (yt-dlp blocked)
```
ERROR: [BiliBili] <id>: Unable to download JSON metadata: HTTP Error 412
```
**Cause**: WBI signing anti-bot. yt-dlp's playurl API request rejected.
**Fix**: Switch to `you-get`. Do NOT retry yt-dlp — it will keep failing.

### yt-dlp --flat-playlist for Season/Collection URLs (WORKS)
```bash
yt-dlp --flat-playlist --dump-json "https://space.bilibili.com/<uid>/lists/<id>?type=season"
```
**Works without anti-bot**. Returns all videos with `id` (BV), `url`, `playlist_index`, `playlist_count`.
**Caveats**:
- Titles show as "NA" in flat mode — get real titles with `you-get --info` per BV
- Playlist order is **oldest→newest** (index 1 = first video, highest index = latest)
- Flat mode `epoch` is the fetch time, not upload date

### CC Subtitles Require Login
```json
{need_login_subtitle: True, subtitles: []}
```
**B站 CC字幕需要登录才能访问**。Without cookies, subtitle data is inaccessible via API. If user reports a transcription error against original subtitles, you cannot verify programmatically — ask user to confirm from the video.

### Chrome Cookie Extraction on Windows
```
PermissionError: Cookies file locked by Chrome
```
**Chrome locks the Cookies SQLite database on Windows**. `win32crypt`+`CryptUnprotectData` approach works for decryption but the file copy often fails due to lock. Workarounds: close Chrome, use Chrome remote debugging, or ask user to export cookies manually.

### AV1 Format Hangs (Use HEVC Instead)
```bash
# AV1 sometimes produces zero output for 4+ minutes — process hangs
you-get --format=dash-flv360-AV1 ...  # ❌ unreliable

# HEVC is more reliable
you-get --format=dash-flv360-HEVC ... # ✅ preferred
```
**Default to HEVC**. If HEVC not available, fall back to AVC.

### you-get Silent Startup (DON'T KILL PREMATURELY)
```
Symptom: you-get process runs with zero stdout for 1-3 minutes, then suddenly shows progress.
```
**Cause**: you-get takes time to resolve the video page, extract formats, and start the download. During `--info` or the initial connection phase, no output is produced.
**Fix**: Wait at least **3 minutes** before concluding it's stuck. Poll with `process(action='poll')` and check `uptime_seconds`. If it exceeds 180s with zero output AND zero files in the work directory, only then consider it hung.
**Key lesson from session**: A `you-get` process at 105s uptime with zero output was assumed stuck and killed — but it had actually finished downloading by the time the kill signal arrived. The progress bars appeared AFTER the initial silent phase.

### you-get --info Hangs
```
you-get --info <URL> produces only the "need login cookies" warning, then hangs indefinitely.
```
**Fix**: Skip `--info`. Try downloading directly without `--format` first — you-get will pick the default (usually lowest quality). If a specific format is needed, try common ones: `dash-flv360-AV1`, `dash-flv480-AVC`.
**Fallback**: If `--format=dash-flv360-AV1` hangs, try omitting `--format` entirely.
- yt-dlp flags tried without success: `--user-agent`, `--add-header Referer`, `--extractor-args "bilibili:player_client=android"`, `--cookies-from-browser`
- This suggests B站 has updated their WBI signing requirements beyond what the current yt-dlp version handles.

### Gzip-Compressed HTML
```
curl output appears as binary garbage (magic bytes 1f 8b)
```
**Fix**: Use `curl --compressed` to auto-decompress, or pipe through `gunzip`.

### you-get Login Required for HD
```
you-get: You will need login cookies for 720p formats or above.
```
**Not a blocker**: For transcription, 360P/480P video audio quality is sufficient for faster-whisper (tiny). Higher bitrate audio doesn't improve transcription accuracy.

### you-get Only Shows Video Streams
```
[DASH] dash-flv360-AV1, dash-flv480-AVC, etc. — no audio-only format
```
**Normal behavior without login**: B站 DASH separates audio/video. Without login, you-get can only access video-only DASH streams. Audio-only streams require authentication.
**Workflow**: Download smallest DASH video → ffmpeg extract audio → delete video.

### Workaround Flow
1. `you-get --info` → identify smallest format (usually `dash-flv360-AV1`)
2. `you-get --format=dash-flv360-AV1 -o . <URL>` → download in background
3. `ffmpeg -i <video.mp4> -vn -acodec libmp3lame -q:a 2 <output.mp3> -y` → extract audio
4. `rm <video.mp4>` → mandatory cleanup

# Xiaoyuzhou (小宇宙) Podcast Extraction

## Audio URL Extraction

小宇宙 episode pages embed the audio URL in two locations:
```html
<meta property="og:audio" content="https://media.xyzcdn.net/...mp3">
```
and
```html
<link rel="enclosure" ... url="https://media.xyzcdn.net/...mp3">
```

```bash
curl -sL --proxy http://127.0.0.1:7897 "<episode_URL>" \
  -H "User-Agent: Mozilla/5.0 (compatible; hermes-podcast/1.0)" \
  | grep -oP 'property="og:audio"\s+content="\K[^"]+'
```

## Audio Hosting

小宇宙 audio is hosted on `media.xyzcdn.net`. Files are MP3 format, typically:
- 60-min episode: ~83MB
- Download speed depends on proxy, usually 1-3 MB/s

## Long Podcast Transcription

For 60+ minute podcasts:
- `tiny` model: ~5-8x realtime on this machine (60 min → ~8-12 min)
- 9139 lines / 108KB for a 60-min episode
- Reading full transcript takes significant context — use `delegate_task` for synthesis or read in 500-line chunks
- First 3-minute progress mark may show very few segments (model warmup); accelerates after

## Download Command
```bash
curl -L --proxy http://127.0.0.1:7897 -o "<output.mp3>" "<audio_url>"
```

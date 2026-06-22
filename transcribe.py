#!/usr/bin/env python3
"""Transcribe audio with faster-whisper. Called from Hermes podcast skill."""

import argparse
import json
import sys
from pathlib import Path

def format_time(seconds: float) -> str:
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def transcribe(audio: Path, out_dir: Path, model: str, language: str) -> None:
    from faster_whisper import WhisperModel

    model_path = Path(model)
    model_arg = str(model_path) if model_path.exists() else model

    whisper = WhisperModel(model_arg, device="cpu", compute_type="int8")
    segments_iter, info = whisper.transcribe(
        str(audio),
        language=language,
        beam_size=5,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    segments = []
    transcript_md = out_dir / "transcript.md"
    total_duration = info.duration
    last_report_at = 0.0
    REPORT_INTERVAL = 180.0  # seconds — report progress every 3 min of audio

    with transcript_md.open("w", encoding="utf-8") as md:
        md.write("# Transcript\n\n")
        md.write(f"- language: {info.language}\n")
        md.write(f"- language_probability: {info.language_probability:.4f}\n")
        md.write(f"- duration: {format_time(total_duration)}\n")
        md.write(f"- model: {model}\n\n")
        for seg in segments_iter:
            text = seg.text.strip()
            segments.append({"start": seg.start, "end": seg.end, "text": text})
            md.write(f"## {format_time(seg.start)} - {format_time(seg.end)}\n\n")
            md.write(text + "\n\n")

            # Progress to stderr (unbuffered, visible in real-time)
            if seg.end - last_report_at >= REPORT_INTERVAL:
                pct = seg.end / total_duration * 100 if total_duration > 0 else 0
                print(
                    f"[TRANSCRIBE] {format_time(seg.end)} / {format_time(total_duration)} "
                    f"({pct:.1f}%) — {len(segments)} segments",
                    file=sys.stderr,
                    flush=True,
                )
                last_report_at = seg.end

    (out_dir / "transcript.json").write_text(
        json.dumps(
            {
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "model": model,
                "segments": segments,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"TRANSCRIPT_MD={transcript_md}")
    print(f"TRANSCRIPT_JSON={out_dir / 'transcript.json'}")
    print(f"SEGMENTS={len(segments)}")
    print(f"DURATION={format_time(info.duration)}")
    print(f"LANGUAGE={info.language} (p={info.language_probability:.4f})")


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio with faster-whisper")
    parser.add_argument("--audio", required=True, help="Path to audio file (.m4a, .mp3, .wav, etc.)")
    parser.add_argument("--out-dir", required=True, help="Output directory for transcript files")
    parser.add_argument("--model", default="tiny", help="faster-whisper model: tiny, small, medium, large-v3")
    parser.add_argument("--language", default="zh", help="Whisper language code (zh, en, ja, etc.)")
    args = parser.parse_args()

    audio = Path(args.audio)
    if not audio.exists():
        print(f"ERROR: audio file not found: {audio}", file=sys.stderr)
        return 1

    try:
        transcribe(audio, Path(args.out_dir), args.model, args.language)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

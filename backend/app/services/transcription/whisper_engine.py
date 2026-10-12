import os
import re
import json
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class TranscriptionError(Exception):
    pass

def parse_time_vtt_srt(t_str: str) -> float:
    """Converts 00:01:23.456 or 01:23.456 into floating-point seconds."""
    t_str = t_str.strip().replace(',', '.')
    parts = t_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
        return float(h) * 3600 + float(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return float(m) * 60 + float(s)
    return float(parts[0])

def parse_subtitle_file(sub_path: Path) -> List[Dict[str, Any]]:
    """Parses SRT or VTT files into chronological timestamped segments."""
    if not sub_path.exists():
        return []

    try:
        with open(sub_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        pattern = re.compile(
            r'(\d{1,2}:\d{2}:\d{2}[\.,]\d{3}|\d{2}:\d{2}[\.,]\d{3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[\.,]\d{3}|\d{2}:\d{2}[\.,]\d{3})[^\n]*\n(.*?)(?=\n\s*(?:\d+[\r\n]+)?\d{1,2}:|\Z)',
            re.DOTALL
        )

        segments = []
        seen = set()
        for match in pattern.finditer(content):
            start_str, end_str, raw_text = match.groups()
            start = parse_time_vtt_srt(start_str)
            end = parse_time_vtt_srt(end_str)

            # Strip HTML/VTT formatting tags
            clean_text = re.sub(r'<[^>]+>', '', raw_text)
            clean_text = re.sub(r'[\r\n]+', ' ', clean_text).strip()

            if clean_text and clean_text not in seen:
                seen.add(clean_text)
                segments.append({
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "text": clean_text
                })
        return segments
    except Exception as e:
        logger.warning(f"Error parsing subtitle file {sub_path}: {e}")
        return []

def extract_audio_wav(video_path: Path, output_wav_path: Path) -> None:
    """Extracts 16kHz mono PCM WAV stream efficiently using FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path.resolve()),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_wav_path.resolve())
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise TranscriptionError(f"Failed to extract audio from video: {res.stderr.strip()}")

def transcribe_with_whisper(
    audio_path: Path,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> List[Dict[str, Any]]:
    """Runs faster-whisper with CPU INT8 quantization, or falls back to openai-whisper."""
    model_size = settings.whisper_model or "tiny"
    download_root = str(settings.models_dir)

    try:
        from faster_whisper import WhisperModel
        compute_type = settings.whisper_compute_type or "int8"
        if progress_callback:
            progress_callback(30, f"Loading faster-whisper model ({model_size}, {compute_type})...")
        logger.info(f"Loading faster-whisper model '{model_size}' (compute={compute_type}, threads={settings.cpu_threads})")
        model = WhisperModel(
            model_size,
            device="cpu",
            compute_type=compute_type,
            cpu_threads=settings.cpu_threads,
            download_root=download_root
        )
        if progress_callback:
            progress_callback(40, "Transcribing speech on CPU with faster-whisper...")

        segments_gen, info = model.transcribe(
            str(audio_path.resolve()),
            beam_size=5,
            word_timestamps=True,
            vad_filter=True,
            language=None if settings.transcription_language == "auto" else settings.transcription_language
        )
        results = []
        for s in segments_gen:
            results.append({
                "start": round(s.start, 2),
                "end": round(s.end, 2),
                "text": s.text.strip(),
                "words": [
                    {"word": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)}
                    for w in (s.words or [])
                ] if hasattr(s, "words") and s.words else []
            })
        return results

    except ImportError:
        logger.info("faster-whisper not found, falling back to pre-installed openai-whisper.")
        import whisper
        cache_dir = Path.home() / ".cache" / "whisper"
        load_root = str(cache_dir) if (cache_dir / f"{model_size}.pt").exists() else download_root
        model = whisper.load_model(model_size, download_root=load_root)
        if progress_callback:
            progress_callback(40, "Transcribing speech on CPU with Whisper...")
        lang = None if settings.transcription_language == "auto" else settings.transcription_language
        res = model.transcribe(str(audio_path.resolve()), language=lang)
        results = []
        for s in res.get("segments", []):
            results.append({
                "start": round(s["start"], 2),
                "end": round(s["end"], 2),
                "text": s["text"].strip(),
                "words": []
            })
        return results

def transcribe_media(
    video_path: Path,
    subtitle_path: Optional[Path] = None,
    cache_path: Optional[Path] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> List[Dict[str, Any]]:
    """
    Main transcription entry point:
    1. Checks cached JSON transcript.
    2. Checks pre-existing official subtitle file if supplied.
    3. Falls back to faster-whisper on CPU INT8.
    """
    if cache_path and cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if cached:
                    logger.info("Using cached transcript segments.")
                    return cached
        except Exception:
            pass

    # Step 1: Pre-existing subtitles
    if subtitle_path and subtitle_path.exists():
        if progress_callback:
            progress_callback(25, "Reading pre-extracted subtitles...")
        segs = parse_subtitle_file(subtitle_path)
        if len(segs) >= 5:
            if cache_path:
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(segs, f, indent=2)
            return segs

    # Step 2: Extract audio and transcribe
    wav_path = video_path.with_suffix(".tmp.wav")
    try:
        if progress_callback:
            progress_callback(25, "Extracting audio track for speech recognition...")
        extract_audio_wav(video_path, wav_path)

        segs = transcribe_with_whisper(wav_path, progress_callback)
        if not segs:
            raise TranscriptionError("No speech detected in audio stream.")

        if cache_path:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(segs, f, indent=2)

        return segs
    finally:
        if wav_path.exists():
            wav_path.unlink()

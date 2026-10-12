import re
from pathlib import Path
from typing import List, Dict, Any

SUBTITLE_STYLES = {
    "hormozi_yellow": {
        "font_name": "Arial",
        "font_size": 24,
        "primary_colour": "&H0000FFFF",  # Bright Yellow in BGR (&HAABBGGRR)
        "secondary_colour": "&H00FFFFFF",
        "outline_colour": "&H00000000",  # Black outline
        "back_colour": "&H80000000",
        "bold": 1,
        "outline": 2.5,
        "shadow": 1.0,
        "alignment": 2,  # Bottom Center
        "margin_v": 120
    },
    "clean_white": {
        "font_name": "Arial",
        "font_size": 22,
        "primary_colour": "&H00FFFFFF",  # Pure White
        "secondary_colour": "&H0000FFFF",
        "outline_colour": "&H00000000",
        "back_colour": "&H80000000",
        "bold": 1,
        "outline": 2.0,
        "shadow": 1.0,
        "alignment": 2,
        "margin_v": 120
    },
    "minimal_box": {
        "font_name": "Arial",
        "font_size": 20,
        "primary_colour": "&H00FFFFFF",
        "secondary_colour": "&H00FFFFFF",
        "outline_colour": "&H00000000",
        "back_colour": "&H60000000",
        "bold": 0,
        "outline": 1.5,
        "shadow": 0.0,
        "alignment": 2,
        "margin_v": 110
    }
}

def format_ass_time(seconds: float) -> str:
    """Formats float seconds into ASS timestamp: H:MM:SS.cs"""
    seconds = max(0.0, seconds)
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    csecs = int(round((seconds - int(seconds)) * 100))
    if csecs >= 100:
        csecs = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{csecs:02d}"

def format_srt_time(seconds: float) -> str:
    """Formats float seconds into SRT timestamp: HH:MM:SS,mmm"""
    seconds = max(0.0, seconds)
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int(round((seconds - int(seconds)) * 1000))
    if msecs >= 1000:
        msecs = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"

def format_vtt_time(seconds: float) -> str:
    """Formats float seconds into VTT timestamp: HH:MM:SS.mmm"""
    return format_srt_time(seconds).replace(',', '.')

def generate_subtitle_files(
    clip_segments: List[Dict[str, Any]],
    clip_start_time: float,
    base_output_path: Path,
    style_name: str = "hormozi_yellow"
) -> Dict[str, Path]:
    """
    Generates .ass, .srt, and .vtt subtitle files with timestamps normalized
    relative to the clip's 0.0s starting point.
    """
    style = SUBTITLE_STYLES.get(style_name, SUBTITLE_STYLES["hormozi_yellow"])
    
    ass_path = base_output_path.with_suffix(".ass")
    srt_path = base_output_path.with_suffix(".srt")
    vtt_path = base_output_path.with_suffix(".vtt")

    # 1. ASS file creation
    ass_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 0",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,{style['font_name']},{style['font_size']},{style['primary_colour']},{style['secondary_colour']},{style['outline_colour']},{style['back_colour']},{style['bold']},0,0,0,100,100,0,0,1,{style['outline']},{style['shadow']},{style['alignment']},40,40,{style['margin_v']},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    srt_lines = []
    vtt_lines = ["WEBVTT", ""]

    srt_idx = 1
    for seg in clip_segments:
        # Normalize time relative to clip start
        seg_st = max(0.0, seg["start"] - clip_start_time)
        seg_et = max(seg_st + 0.5, seg["end"] - clip_start_time)
        text = seg["text"].strip().replace("\n", " ")

        if not text:
            continue

        # Split longer sentences into 3-5 word readable lines
        words = text.split()
        chunk_size = 5
        word_chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        
        # Sub-divide duration evenly across chunks
        duration_per_chunk = (seg_et - seg_st) / max(len(word_chunks), 1)

        for c_idx, chunk in enumerate(word_chunks):
            c_st = seg_st + (c_idx * duration_per_chunk)
            c_et = c_st + duration_per_chunk

            # ASS Event
            ass_lines.append(f"Dialogue: 0,{format_ass_time(c_st)},{format_ass_time(c_et)},Default,,0,0,0,,{chunk}")

            # SRT Event
            srt_lines.append(str(srt_idx))
            srt_lines.append(f"{format_srt_time(c_st)} --> {format_srt_time(c_et)}")
            srt_lines.append(chunk)
            srt_lines.append("")

            # VTT Event
            vtt_lines.append(f"{format_vtt_time(c_st)} --> {format_vtt_time(c_et)}")
            vtt_lines.append(chunk)
            vtt_lines.append("")

            srt_idx += 1

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ass_lines))

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

    with open(vtt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(vtt_lines))

    return {
        "ass": ass_path,
        "srt": srt_path,
        "vtt": vtt_path
    }

import os
import shutil
import subprocess
import pytest
from pathlib import Path
from backend.app.services.media.inspector import inspect_media_file
from backend.app.services.rendering.renderer import render_clip_video
from backend.app.services.clip_selection.selector import find_candidate_clips

@pytest.fixture(scope="module")
def synthetic_video(tmp_path_factory):
    """
    Creates a real 75-second synthetic MP4 video using FFmpeg for testing media inspection and clipping.
    Contains test pattern and synthetic sine audio.
    """
    tmp_dir = tmp_path_factory.mktemp("media_test")
    video_path = tmp_dir / "synthetic_test_75s.mp4"

    # Command to generate 75s synthetic video with audio
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc=duration=75:size=640x360:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=75",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac",
        "-shortest",
        str(video_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0 or not video_path.exists():
        pytest.skip("FFmpeg is not available to generate synthetic video fixture.")

    return video_path

def test_inspect_media_file(synthetic_video):
    meta = inspect_media_file(synthetic_video)
    assert meta["duration_seconds"] >= 74.0
    assert meta["width"] == 640
    assert meta["height"] == 360
    assert meta["has_audio"] is True
    assert meta["file_size_bytes"] > 0

def test_render_clip_pipeline(synthetic_video, tmp_path):
    output_dir = tmp_path / "rendered_output"
    
    dummy_segments = [
        {"start": 5.0, "end": 10.0, "text": "Welcome to ClipForge AI testing."},
        {"start": 10.0, "end": 35.0, "text": "This tests autonomous vertical reframing and captions."},
        {"start": 35.0, "end": 65.0, "text": "The final clip duration must be at least sixty seconds."}
    ]

    res = render_clip_video(
        source_video_path=synthetic_video,
        output_dir=output_dir,
        clip_id="test_clip_1",
        clip_index=1,
        start_time=5.0,
        end_time=66.0,  # 61.0s duration (>= 60s)
        aspect_ratio="9:16",
        subtitle_style="hormozi_yellow",
        burn_subtitles=True,
        clip_segments=dummy_segments
    )

    out_file = Path(res["video_path"])
    assert out_file.exists()
    assert out_file.stat().st_size > 0
    assert res["duration"] >= 60.0, f"Rendered clip duration ({res['duration']}) is less than 60s!"
    assert Path(res["srt_path"]).exists()
    assert Path(res["vtt_path"]).exists()
    if res["thumbnail_path"]:
        assert Path(res["thumbnail_path"]).exists()

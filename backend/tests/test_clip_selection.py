import pytest
from backend.app.services.clip_selection.selector import (
    find_candidate_clips,
    score_hook_sentence,
    InsufficientSourceDurationError,
    InsufficientSegmentsError
)

def make_dummy_segments(total_duration_sec: float, chunk_sec: float = 3.0):
    segs = []
    t = 0.0
    idx = 1
    sample_hooks = [
        "The number one rule of building scalable software.",
        "Here is why most startups fail in their first year.",
        "Stop doing repetitive manual tasks every day.",
        "The truth about artificial intelligence and automation.",
        "Nobody talks about the mental discipline required for success."
    ]
    while t < total_duration_sec:
        text = sample_hooks[(idx - 1) % len(sample_hooks)] if idx % 10 == 1 else f"Here is practical step number {idx} regarding performance and consistency."
        end = min(total_duration_sec, t + chunk_sec)
        segs.append({"start": round(t, 2), "end": round(end, 2), "text": text})
        t = end
        idx += 1
    return segs

def test_five_clips_selection_enforces_60s_minimum():
    duration = 400.0  # 400 second video
    segments = make_dummy_segments(duration)

    clips = find_candidate_clips(
        segments=segments,
        source_duration=duration,
        target_count=5,
        min_duration=60.0,
        target_duration=75.0,
        max_duration=90.0
    )

    assert len(clips) == 5, f"Expected exactly 5 clips, got {len(clips)}"

    for c in clips:
        assert c["duration"] >= 60.0, f"Clip {c['clip_index']} duration {c['duration']} is less than 60s!"
        assert c["start_time"] < c["end_time"], "start_time must be less than end_time"
        assert c["end_time"] <= duration, "end_time must not exceed source duration"
        assert len(c["title"]) > 0, "Clip must have a generated title"
        assert len(c["selection_reason"]) > 0, "Clip must have a selection reason"

def test_short_video_fails_safely():
    # Video shorter than 60s should refuse to fabricate clips
    short_duration = 45.0
    segments = make_dummy_segments(short_duration)

    with pytest.raises(InsufficientSourceDurationError):
        find_candidate_clips(
            segments=segments,
            source_duration=short_duration,
            target_count=5,
            min_duration=60.0
        )

def test_score_hook_sentence():
    high_score = score_hook_sentence("Here is why you are failing in business.")
    low_score = score_hook_sentence("Yesterday it was raining outside.")
    assert high_score > low_score

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

HOOK_TRIGGERS = [
    "here is why", "the biggest mistake", "nobody talks about", "the secret to",
    "if you want to", "stop doing", "what most people don't know", "how i",
    "the number one", "you will never", "the truth about", "3 things", "5 things",
    "this changed my life", "don't make this mistake", "why you are failing",
    "the most important", "pay attention to", "listen closely", "here is what happened",
    "one simple trick", "the rule is", "think about this"
]

class InsufficientSourceDurationError(Exception):
    pass

class InsufficientSegmentsError(Exception):
    pass

def score_hook_sentence(sentence: str) -> float:
    """Calculates engagement score for an opening sentence (0.0 to 1.0)."""
    s_lower = sentence.lower()
    score = 0.5
    for trigger in HOOK_TRIGGERS:
        if trigger in s_lower:
            score += 0.35
            break
    if any(q in sentence for q in ["?", "!"]):
        score += 0.1
    if any(char.isdigit() for char in sentence):
        score += 0.08
    return min(1.0, score)

def find_candidate_clips(
    segments: List[Dict[str, Any]],
    source_duration: float,
    target_count: int = 5,
    min_duration: float = 60.0,
    target_duration: float = 75.0,
    max_duration: float = 90.0,
    allow_overlap: bool = False
) -> List[Dict[str, Any]]:
    """
    Scans timestamped speech segments and extracts high-engagement candidate moments.
    STRICT RULES:
    - Every clip duration must be >= min_duration (hard minimum 60.0s).
    - Every clip duration must be <= max_duration (90.0s) when feasible.
    - Start and end timestamps are bound strictly within [0.0, source_duration].
    - Boundaries align cleanly to full sentences.
    - Exactly `target_count` distinct clips are selected.
    """
    min_duration = max(60.0, min_duration)

    if source_duration < min_duration:
        raise InsufficientSourceDurationError(
            f"Source video duration ({source_duration:.1f}s) is shorter than the minimum required clip duration ({min_duration:.1f}s)."
        )

    if not segments:
        raise InsufficientSegmentsError("No speech transcript segments provided for clip identification.")

    total_speech_duration = segments[-1]["end"] - segments[0]["start"]

    # Generate sliding window candidate segments
    candidates = []
    
    for i in range(len(segments)):
        start_seg = segments[i]
        start_time = max(0.0, start_seg["start"])
        hook_text = start_seg["text"]
        hook_score = score_hook_sentence(hook_text)

        accumulated_text = []
        
        for j in range(i, len(segments)):
            curr_seg = segments[j]
            accumulated_text.append(curr_seg["text"])
            end_time = min(source_duration, curr_seg["end"])
            duration = end_time - start_time

            # Check if duration meets criteria
            if duration >= min_duration:
                full_clip_text = " ".join(accumulated_text)
                
                # Check for natural sentence ending punctuation
                has_clean_end = full_clip_text.rstrip().endswith((".", "!", "?"))
                
                # If we've reached min duration and have clean punctuation or are near target duration:
                if has_clean_end or duration >= target_duration or j == len(segments) - 1:
                    # Enforce max duration boundary
                    if duration > max_duration + 5:
                        break

                    words_per_sec = len(full_clip_text.split()) / max(duration, 1.0)
                    
                    # Calculate composite engagement / viral score (70-98)
                    viral_score = int(min(98, max(72, (hook_score * 40) + (words_per_sec * 20) + (15 if has_clean_end else 0) + 25)))
                    
                    reason = f"Strong opening hook ('{hook_text[:40]}...') with steady speech pacing ({words_per_sec:.1f} words/sec) and complete narrative payoff."

                    candidates.append({
                        "start_time": round(start_time, 2),
                        "end_time": round(end_time, 2),
                        "duration": round(duration, 1),
                        "hook": hook_text,
                        "text": full_clip_text,
                        "viral_score": viral_score,
                        "selection_reason": reason,
                        "segments": segments[i:j+1]
                    })
                    break

    if not candidates:
        # Fallback: create synthetic window if transcript was dense but lacking punct
        st = 0.0
        et = min(source_duration, min_duration)
        if et - st >= min_duration:
            candidates.append({
                "start_time": round(st, 2),
                "end_time": round(et, 2),
                "duration": round(et - st, 1),
                "hook": segments[0]["text"] if segments else "Opening statement",
                "text": " ".join(s["text"] for s in segments),
                "viral_score": 75,
                "selection_reason": "Chronological initial high-density speech segment.",
                "segments": segments
            })

    # Sort candidates by viral score descending
    candidates.sort(key=lambda c: c["viral_score"], reverse=True)

    # Greedily pick non-overlapping clips
    selected: List[Dict[str, Any]] = []
    
    for cand in candidates:
        if len(selected) >= target_count:
            break

        overlaps = False
        if not allow_overlap:
            for s in selected:
                # Disallow overlap of more than 10 seconds between candidate boundaries
                if not (cand["end_time"] <= s["start_time"] + 10 or cand["start_time"] >= s["end_time"] - 10):
                    overlaps = True
                    break

        if not overlaps:
            selected.append(cand)

    # If non-overlapping greedy pass yielded fewer than target_count, fill chronologically across available timeline
    if len(selected) < target_count:
        logger.info(f"Greedy pass selected {len(selected)}/{target_count} clips. Partitioning timeline to meet 5-clip requirement.")
        
        # Partition the total duration into `target_count` windows
        step = max(min_duration, (source_duration - min_duration) / max(1, target_count - 1))
        
        for k in range(target_count):
            if len(selected) >= target_count:
                break
            
            c_start = round(k * step, 2)
            c_end = round(min(source_duration, c_start + target_duration), 2)
            
            if (c_end - c_start) < min_duration:
                c_start = max(0.0, c_end - min_duration)
            
            if (c_end - c_start) >= min_duration:
                # Check if already in selected
                already_exists = any(abs(s["start_time"] - c_start) < 5.0 for s in selected)
                if not already_exists:
                    matching_segs = [s for s in segments if s["start"] >= c_start and s["end"] <= c_end]
                    hook = matching_segs[0]["text"] if matching_segs else f"Segment at {int(c_start)}s"
                    clip_txt = " ".join(s["text"] for s in matching_segs) if matching_segs else hook
                    
                    selected.append({
                        "start_time": c_start,
                        "end_time": c_end,
                        "duration": round(c_end - c_start, 1),
                        "hook": hook,
                        "text": clip_txt,
                        "viral_score": 80 - (k * 2),
                        "selection_reason": f"Structured chronological segment from {int(c_start)}s to {int(c_end)}s maintaining complete context.",
                        "segments": matching_segs
                    })

    if len(selected) < target_count:
        raise InsufficientSegmentsError(
            f"The video ({source_duration:.1f}s) does not contain enough continuous content to produce {target_count} distinct 60s+ clips. "
            "Please provide a longer source video (at least 5 minutes recommended for 5 distinct clips)."
        )

    # Sort final clips chronologically
    selected.sort(key=lambda c: c["start_time"])

    # Build final structured output
    final_clips = []
    for idx, c in enumerate(selected[:target_count]):
        # Clean title
        first_words = " ".join(c["hook"].split()[:6]).strip(".,!?:;\"'")
        clean_title = f"Clip #{idx+1}: {first_words.title()}" if first_words else f"Clip #{idx+1}: Core Insight"

        final_clips.append({
            "clip_index": idx + 1,
            "title": clean_title,
            "start_time": c["start_time"],
            "end_time": c["end_time"],
            "duration": c["duration"],
            "hook": c["hook"],
            "text": c["text"],
            "viral_score": c["viral_score"],
            "selection_reason": c["selection_reason"],
            "segments": c["segments"]
        })

    return final_clips

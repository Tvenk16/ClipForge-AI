"""
ClipAgent: selects viral-worthy clip timestamps from transcript.

Uses LLMService when configured to pick 3 short-form clip ideas with:
- start time
- end time
- title
- why the segment is compelling

Falls back to a simple heuristic splitter when no LLM API key is present.
"""

from typing import Optional, List, Dict

from app.services.llm_service import LLMService


class ClipAgent:
    """Selects clip time ranges from transcript text and timing metadata."""

    def __init__(self):
        self._llm = LLMService()

    def _infer_duration_from_segments(self, segments: List[Dict]) -> Optional[float]:
        if not segments:
            return None
        last = segments[-1]
        return float(last.get("start", 0.0)) + float(last.get("duration", 0.0))

    def _heuristic_ideas_from_segments(self, segments: List[Dict]) -> list[dict]:
        """
        Transcript-based fallback clip ideas when no LLM output is available.
        Picks segments with the richest text payload and builds 20-50s windows.
        """
        if not segments:
            return []
        ranked = sorted(
            segments,
            key=lambda s: len((s.get("text") or "").strip()),
            reverse=True,
        )
        ideas: list[dict] = []
        for idx, seg in enumerate(ranked[:3]):
            start = max(0.0, float(seg.get("start", 0.0)) - 5.0)
            duration = float(seg.get("duration", 0.0))
            end = start + max(20.0, min(50.0, duration + 20.0))
            text = (seg.get("text") or "").strip()
            title = (text[:42] + "...") if len(text) > 45 else (text or f"Clip {idx + 1}")
            ideas.append(
                {
                    "start_seconds": round(start, 2),
                    "end_seconds": round(end, 2),
                    "title": title,
                    "reason": "High-information transcript segment selected heuristically.",
                }
            )
        ideas.sort(key=lambda x: x["start_seconds"])
        return ideas

    def run(self, transcript: str, *, segments: Optional[List[Dict]] = None) -> list[dict]:
        """
        Return list of clip definitions:
        { start_seconds, end_seconds, title, reason }.

        When LLM credentials are available, calls into LLMService.generate_clip_ideas
        with the full transcript and approximate duration. Otherwise, it uses a
        heuristic splitter but still derives timings from the transcript length.
        """
        if not transcript:
            return []

        total_seconds = self._infer_duration_from_segments(segments or [])
        ideas = self._llm.generate_clip_ideas(transcript, total_seconds=total_seconds)
        if not ideas:
            ideas = self._heuristic_ideas_from_segments(segments or [])

        clips: list[dict] = []
        for idea in ideas:
            start = max(0.0, float(idea.get("start_seconds", 0.0)))
            end = float(idea.get("end_seconds", start + 30.0))
            # Shorts-friendly constraint: cap to 60 seconds per clip
            if end - start > 60.0:
                end = start + 60.0
            if end <= start:
                end = start + 15.0
            clips.append(
                {
                    "start_seconds": round(start, 2),
                    "end_seconds": round(end, 2),
                    "title": idea.get("title", "Clip"),
                    "reason": idea.get("reason", "Compelling moment"),
                }
            )
        return clips[:3]  # Focus on the top 3 strongest clips

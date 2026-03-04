"""
ClipAgent: selects viral-worthy clip timestamps from transcript.
Mock timestamp logic for starter; TODO: viral scoring model.
"""

from app.services.llm_service import LLMService


class ClipAgent:
    """Selects clip time ranges from transcript (mock logic)."""

    def __init__(self):
        self._llm = LLMService()

    def run(self, transcript: str) -> list[dict]:
        """
        Return list of clip definitions: { start_seconds, end_seconds, reason }.
        Uses LLM for ideas when API key present; otherwise mock timestamps.
        """
        ideas = self._llm.generate_clip_ideas(transcript)
        # Normalize to max 60s for Shorts; ensure end > start
        clips = []
        for idea in ideas:
            start = max(0.0, float(idea.get("start_seconds", 0)))
            end = min(start + 60.0, float(idea.get("end_seconds", start + 30)))
            if end <= start:
                end = start + 30.0
            clips.append({
                "start_seconds": start,
                "end_seconds": end,
                "reason": idea.get("reason", "clip"),
            })
        return clips[:5]  # Cap at 5 clips per job

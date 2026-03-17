"""
LLM abstraction layer: switch between OpenAI and Claude.
Stub methods with placeholder logic when API key is not present.
"""

from typing import Optional

from app.config import get_settings


class LLMService:
    """
    Abstract LLM provider for generating clip ideas and captions.
    TODO: Wire real OpenAI/Claude API calls when keys are set.
    """

    def __init__(self):
        self._settings = get_settings()
        self._provider = (self._settings.LLM_PROVIDER or "openai").lower()
        self._openai_key = self._settings.OPENAI_API_KEY
        self._claude_key = self._settings.CLAUDE_API_KEY

    def _has_api_key(self) -> bool:
        if self._provider == "openai":
            return bool(self._openai_key)
        if self._provider == "claude":
            return bool(self._claude_key)
        return False

    def generate_clip_ideas(self, transcript: str, total_seconds: float | None = None) -> list[dict]:
        """
        Generate clip ideas from transcript (timestamps + rationale).
        Returns list of
        { start_seconds, end_seconds, title, reason }.
        TODO: Real API - send transcript to LLM, parse structured output.
        """
        if not self._has_api_key():
            # Heuristic fallback when no LLM credentials are configured.
            # Split the transcript into up to 3 evenly-spaced windows across the
            # approximate duration (if known), or default to 3x30s chunks.
            if not transcript:
                return []
            approx_duration = float(total_seconds or 90.0)
            window = approx_duration / 3.0
            ideas: list[dict] = []
            for i in range(3):
                start = window * i
                end = min(start + window, approx_duration)
                ideas.append(
                    {
                        "start_seconds": round(start, 2),
                        "end_seconds": round(end, 2),
                        "title": f"Clip {i + 1}",
                        "reason": "Heuristic segment based on transcript length.",
                    }
                )
            return ideas

        # TODO: Production - call OpenAI/Claude with a structured prompt such as:
        #  - System: "You are an editor selecting short-form video clips."
        #  - User: "Given this transcript, return 3 high-impact short clips..."
        # The LLM should respond with JSON that we parse into the shape below.
        #
        # For now we still return a simple static structure, but callers treat it
        # as LLM output.
        return [
            {
                "start_seconds": 0.0,
                "end_seconds": 30.0,
                "title": "Hook",
                "reason": "High-energy opening hook.",
            },
            {
                "start_seconds": 45.0,
                "end_seconds": 75.0,
                "title": "Key Insight",
                "reason": "Most compelling teaching moment.",
            },
            {
                "start_seconds": 90.0,
                "end_seconds": 120.0,
                "title": "Call to Action",
                "reason": "Strong CTA and takeaway.",
            },
        ]

    def generate_caption(self, text: str, *, title: str | None = None) -> dict:
        """
        Generate hook, caption, and hashtags for a clip.
        Returns { hook, caption, hashtags }.
        TODO: Real API - call LLM with clip context.
        """
        if not self._has_api_key():
            base_caption = text[:200] + ("..." if len(text) > 200 else "")
            return {
                "hook": title or "You won't believe this.",
                "caption": base_caption,
                "hashtags": ["#shorts", "#viral", "#clipforge", "#content"],
            }
        # TODO: Production - call OpenAI/Claude for caption generation with a prompt
        # that includes the segment text and optional title, asking for a hook,
        # caption, and hashtag set tailored for short-form content.
        base_caption = text[:200] + ("..." if len(text) > 200 else "")
        return {
            "hook": title or "Save this for later.",
            "caption": base_caption,
            "hashtags": ["#shorts", "#viral", "#productivity"],
        }

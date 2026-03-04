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

    def generate_clip_ideas(self, transcript: str) -> list[dict]:
        """
        Generate clip ideas from transcript (timestamps + rationale).
        Returns list of { start_seconds, end_seconds, reason }.
        TODO: Real API - send transcript to LLM, parse structured output.
        """
        if not self._has_api_key():
            # Placeholder: return mock clip ideas
            return [
                {"start_seconds": 0.0, "end_seconds": 30.0, "reason": "Hook / intro"},
                {"start_seconds": 45.0, "end_seconds": 75.0, "reason": "Tip 1-2"},
                {"start_seconds": 120.0, "end_seconds": 150.0, "reason": "Tip 4-5"},
            ]
        # TODO: Production - call OpenAI/Claude with prompt to extract viral clips
        return [
            {"start_seconds": 0.0, "end_seconds": 30.0, "reason": "Hook"},
            {"start_seconds": 45.0, "end_seconds": 75.0, "reason": "Key insight"},
        ]

    def generate_caption(self, text: str) -> dict:
        """
        Generate hook, caption, and hashtags for a clip.
        Returns { hook, caption, hashtags }.
        TODO: Real API - call LLM with clip context.
        """
        if not self._has_api_key():
            return {
                "hook": "You won't believe this.",
                "caption": text[:200] + ("..." if len(text) > 200 else ""),
                "hashtags": ["#shorts", "#viral", "#tips", "#productivity"],
            }
        # TODO: Production - call OpenAI/Claude for caption generation
        return {
            "hook": "Save this for later.",
            "caption": text[:200] + ("..." if len(text) > 200 else ""),
            "hashtags": ["#shorts", "#viral", "#productivity"],
        }

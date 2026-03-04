"""
CaptionAgent: generates hook, caption, and hashtags via LLM.
"""

from app.services.llm_service import LLMService


class CaptionAgent:
    """Generates captions for each selected clip."""

    def __init__(self):
        self._llm = LLMService()

    def run(self, clip_text: str) -> dict:
        """
        Generate hook, caption, hashtags for a clip segment text.
        Returns { hook, caption, hashtags }.
        """
        return self._llm.generate_caption(clip_text)

    def run_for_clips(self, transcript: str, clips: list[dict]) -> list[dict]:
        """
        Generate caption for each clip. Uses slice of transcript by time (mock slice).
        Returns list of { start_seconds, end_seconds, hook, caption, hashtags }.
        """
        results = []
        for clip in clips:
            # Mock: use first 200 chars of transcript as clip context
            # TODO: Production - extract transcript segment by start/end time
            clip_text = transcript[:300] if transcript else "No transcript."
            caption_data = self.run(clip_text)
            results.append({
                "start_seconds": clip.get("start_seconds"),
                "end_seconds": clip.get("end_seconds"),
                "hook": caption_data["hook"],
                "caption": caption_data["caption"],
                "hashtags": caption_data["hashtags"],
            })
        return results

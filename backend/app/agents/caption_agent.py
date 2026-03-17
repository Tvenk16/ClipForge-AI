"""
CaptionAgent: generates hook, caption, and hashtags via LLM.

Captions are based on the actual transcript text corresponding to each
clip's time window when transcript segments are available.
"""

from typing import List, Dict, Optional

from app.services.llm_service import LLMService


class CaptionAgent:
    """Generates captions for each selected clip."""

    def __init__(self):
        self._llm = LLMService()

    def _text_for_window(
        self,
        segments: List[Dict],
        start_seconds: float,
        end_seconds: float,
    ) -> str:
        """Concatenate transcript segments that overlap the given time window."""
        if not segments:
            return ""
        parts: list[str] = []
        for seg in segments:
            s = float(seg.get("start", 0.0))
            d = float(seg.get("duration", 0.0))
            e = s + d
            if e < start_seconds or s > end_seconds:
                continue
            text = seg.get("text", "").strip()
            if text:
                parts.append(text)
        return " ".join(parts).strip()

    def run(self, clip_text: str, *, title: Optional[str] = None) -> dict:
        """
        Generate hook, caption, hashtags for a clip segment text.
        Returns { hook, caption, hashtags }.
        """
        return self._llm.generate_caption(clip_text, title=title)

    def run_for_clips(
        self,
        transcript: str,
        clips: list[dict],
        *,
        segments: Optional[List[Dict]] = None,
    ) -> list[dict]:
        """
        Generate caption for each clip based on its actual transcript segment.

        Returns list of:
        { start_seconds, end_seconds, hook, caption, hashtags }.
        """
        results = []
        for clip in clips:
            start = float(clip.get("start_seconds", 0.0))
            end = float(clip.get("end_seconds", start + 30.0))

            if segments:
                clip_text = self._text_for_window(segments, start, end)
            else:
                # Graceful fallback: derive from overall transcript
                clip_text = transcript[:600] if transcript else "No transcript."

            if not clip_text:
                clip_text = "No transcript available for this segment."

            caption_data = self.run(clip_text, title=clip.get("title"))
            results.append(
                {
                    "start_seconds": start,
                    "end_seconds": end,
                    "hook": caption_data["hook"],
                    "caption": caption_data["caption"],
                    "hashtags": caption_data["hashtags"],
                }
            )
        return results

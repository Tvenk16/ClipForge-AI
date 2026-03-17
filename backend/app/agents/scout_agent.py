"""
ScoutAgent: fetches video metadata and transcript.
First step in the pipeline.
"""

from app.services.youtube_service import YouTubeService


class ScoutAgent:
    """Fetches metadata and transcript for a YouTube URL."""

    def __init__(self):
        self._youtube = YouTubeService()

    def run(self, youtube_url: str) -> dict:
        """
        Fetch metadata and transcript.

        Returns dict with:
        - transcript: full transcript text
        - metadata: basic metadata dict
        - segments: raw transcript segments with timings (for downstream agents)
        """
        metadata = self._youtube.fetch_metadata(youtube_url)
        transcript, segments = self._youtube.fetch_transcript(youtube_url)

        # Derive approximate duration from transcript segments when missing
        if metadata.get("duration_seconds") is None and segments:
            last = segments[-1]
            metadata["duration_seconds"] = float(last.get("start", 0.0)) + float(
                last.get("duration", 0.0)
            )

        return {
            "transcript": transcript,
            "metadata": metadata,
            "segments": segments,
        }

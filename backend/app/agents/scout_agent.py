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
        Fetch metadata and transcript. Returns dict with transcript and metadata.
        """
        metadata = self._youtube.fetch_metadata(youtube_url)
        transcript = self._youtube.fetch_transcript(youtube_url)
        return {
            "transcript": transcript,
            "metadata": metadata,
        }

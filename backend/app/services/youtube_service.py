"""
YouTube metadata and transcript service.
TODO: Integrate real YouTube Data API + transcript extraction (youtube-transcript-api or similar).
"""

from typing import Optional

# TODO: Production - use youtube-transcript-api or YouTube Data API
# from youtube_transcript_api import YouTubeTranscriptApi


class YouTubeService:
    """Fetches video metadata and transcript. Mock implementation for local run."""

    def get_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        if "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        if "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        return None

    def fetch_metadata(self, url: str) -> dict:
        """Fetch video metadata (title, duration, etc.). Mock for now."""
        video_id = self.get_video_id(url)
        if not video_id:
            return {"error": "Invalid YouTube URL", "video_id": None}
        # TODO: Production - call YouTube Data API v3 for snippet, contentDetails
        return {
            "video_id": video_id,
            "title": f"Mock Video {video_id[:8]}",
            "duration_seconds": 600,
        }

    def fetch_transcript(self, url: str) -> str:
        """
        Fetch transcript for the video. Returns plain text.
        Mock: returns a deterministic mock transcript for development.
        """
        video_id = self.get_video_id(url)
        if not video_id:
            return ""
        # TODO: Production - use YouTubeTranscriptApi.get_transcript(video_id)
        # and concatenate text from segments
        mock_transcript = (
            "Welcome to this video. Here we discuss the top five tips for productivity. "
            "First, wake up early. Second, plan your day. Third, eliminate distractions. "
            "Fourth, take breaks. Fifth, review your progress. Thanks for watching."
        )
        return mock_transcript

"""
YouTube metadata and transcript service.
Uses youtube-transcript-api to fetch real transcripts when available.
"""

from typing import Optional, Tuple, List, Dict
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)


class YouTubeService:
    """Fetches video metadata and transcript using youtube-transcript-api."""

    def get_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.

        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://www.youtube.com/shorts/VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        """
        parsed = urlparse(url)
        if "youtu" not in parsed.netloc:
            return None

        # Standard watch URL: https://www.youtube.com/watch?v=VIDEO_ID
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            vid = qs.get("v", [None])[0]
            if vid:
                return vid

        # Short URL: https://youtu.be/VIDEO_ID
        if parsed.netloc.startswith("youtu.be"):
            path = parsed.path.lstrip("/")
            return path or None

        # Embed URL: https://www.youtube.com/embed/VIDEO_ID
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/embed/")[1].split("/")[0]

        # Shorts URL: https://www.youtube.com/shorts/VIDEO_ID
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/shorts/")[1].split("/")[0]

        return None

    def fetch_metadata(self, url: str) -> dict:
        """
        Fetch video metadata.

        NOTE: We avoid the YouTube Data API here to keep setup simple.
        We derive an approximate duration from the transcript segments instead.
        """
        video_id = self.get_video_id(url)
        if not video_id:
            return {"error": "Invalid YouTube URL", "video_id": None}
        # Title is unknown without Data API; we keep a placeholder.
        return {
            "video_id": video_id,
            "title": f"Video {video_id[:8]}",
            "duration_seconds": None,  # Filled later from transcript segments when available
        }

    def fetch_transcript(
        self, url: str
    ) -> Tuple[str, List[Dict]]:
        """
        Fetch transcript for the video.

        Returns a tuple of:
        - transcript_text: full concatenated transcript
        - segments: list of segments from youtube-transcript-api

        Gracefully falls back to empty values when transcripts are not available
        (e.g., disabled, private, or region-locked videos).
        """
        video_id = self.get_video_id(url)
        if not video_id:
            return "", []

        try:
            segments = YouTubeTranscriptApi.get_transcript(video_id)
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
            # Transcript unavailable – return empty but do not break the pipeline
            return "", []
        except Exception:
            # Any other unexpected error; keep the system resilient
            return "", []

        transcript_text = " ".join(seg.get("text", "") for seg in segments).strip()
        return transcript_text, segments

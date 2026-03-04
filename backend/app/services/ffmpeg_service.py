"""
FFmpeg service for clipping video. Uses subprocess to call ffmpeg.
Assumes local file exists; mock download for now.
"""

import subprocess
from pathlib import Path


class FFmpegService:
    """
    Video clipping via FFmpeg. Expects local input file.
    TODO: Production - integrate with download step (yt-dlp or similar).
    """

    def clip_video(
        self,
        input_path: str,
        start_time: float,
        end_time: float,
        output_path: str,
    ) -> bool:
        """
        Extract clip from input_path from start_time to end_time into output_path.
        Returns True on success, False on failure.
        """
        input_p = Path(input_path)
        if not input_p.exists():
            # Mock: do not fail in dev when file does not exist
            # TODO: Production - require real file and fail clearly
            return False
        duration = end_time - start_time
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),
            "-i", str(input_path),
            "-t", str(duration),
            "-c", "copy",
            str(output_path),
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            # FileNotFoundError when ffmpeg not installed
            # TODO: Production - log and surface error
            return False

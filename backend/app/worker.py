"""
Background worker: polls for queued jobs, runs agent pipeline, updates Redis.
Retry logic: 3 attempts with exponential backoff.
"""

import time
import traceback

from app.agents import ScoutAgent, ClipAgent, CaptionAgent
from app.config import get_settings
from app.models.job import JobStatus
from app.services.redis_service import RedisService


def run_pipeline(job_id: str, youtube_url: str) -> None:
    """Run scout -> clip -> caption agents and persist results."""
    redis_svc = RedisService()
    scout = ScoutAgent()
    clip_agent = ClipAgent()
    caption_agent = CaptionAgent()

    try:
        # Scout: transcript + metadata
        scout_result = scout.run(youtube_url)
        transcript = scout_result.get("transcript", "") or ""
        redis_svc.update_job(job_id, transcript=transcript)

        # Clip: timestamps
        clips = clip_agent.run(transcript)
        redis_svc.update_job(job_id, clips=clips)

        # Caption: hook, caption, hashtags per clip
        captions = caption_agent.run_for_clips(transcript, clips)
        redis_svc.update_job(job_id, captions=captions, status=JobStatus.COMPLETED)
    except Exception as e:
        redis_svc.update_job(
            job_id,
            status=JobStatus.FAILED,
            error=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}",
        )
        raise


def worker_loop() -> None:
    """Poll for queued jobs and process with retries."""
    settings = get_settings()
    redis_svc = RedisService()
    max_retries = settings.WORKER_MAX_RETRIES
    base_backoff = settings.WORKER_BACKOFF_BASE_SEC
    poll_interval = settings.WORKER_POLL_INTERVAL_SEC

    while True:
        job_id = redis_svc.get_next_queued_job_id()
        if job_id:
            job = redis_svc.get_job(job_id)
            url = job.get("youtube_url", "") if job else ""
            for attempt in range(max_retries):
                try:
                    run_pipeline(job_id, url)
                    break
                except Exception:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(base_backoff ** (attempt + 1))
        time.sleep(poll_interval)


if __name__ == "__main__":
    worker_loop()

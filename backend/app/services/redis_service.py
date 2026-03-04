"""
Redis service for job persistence, intermediate state, and caching.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Optional

from app.config import get_settings
from app.models.job import JobStatus


class RedisService:
    """Handles all Redis operations for jobs and cache."""

    KEY_JOBS = "clipforge:jobs"
    KEY_JOB_PREFIX = "clipforge:job:"
    KEY_JOB_IDS = "clipforge:job_ids"

    def __init__(self):
        self._client = None
        self._settings = get_settings()

    @property
    def client(self):
        """Lazy Redis connection."""
        if self._client is None:
            try:
                import redis
                self._client = redis.Redis(
                    host=self._settings.REDIS_HOST,
                    port=self._settings.REDIS_PORT,
                    db=self._settings.REDIS_DB,
                    password=self._settings.REDIS_PASSWORD,
                    decode_responses=True,
                )
            except Exception as e:
                raise RuntimeError(f"Redis connection failed: {e}") from e
        return self._client

    def create_job(self, youtube_url: str) -> str:
        """Create a new job with status queued. Returns job ID."""
        job_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        job = {
            "id": job_id,
            "status": JobStatus.QUEUED.value,
            "youtube_url": youtube_url,
            "transcript": None,
            "clips": None,
            "captions": None,
            "error": None,
            "created_at": now,
            "updated_at": now,
        }
        key = f"{self.KEY_JOB_PREFIX}{job_id}"
        self.client.set(key, json.dumps(job))
        self.client.sadd(self.KEY_JOB_IDS, job_id)
        return job_id

    def get_job(self, job_id: str) -> Optional[dict[str, Any]]:
        """Fetch a single job by ID."""
        key = f"{self.KEY_JOB_PREFIX}{job_id}"
        raw = self.client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def get_all_job_ids(self) -> list[str]:
        """Return all job IDs (for listing)."""
        return list(self.client.smembers(self.KEY_JOB_IDS))

    def get_all_jobs(self) -> list[dict[str, Any]]:
        """Return all jobs, newest first."""
        ids = self.get_all_job_ids()
        jobs = []
        for jid in ids:
            job = self.get_job(jid)
            if job:
                jobs.append(job)
        jobs.sort(key=lambda j: j.get("created_at", ""), reverse=True)
        return jobs

    def update_job(
        self,
        job_id: str,
        *,
        status: Optional[JobStatus] = None,
        transcript: Optional[str] = None,
        clips: Optional[list] = None,
        captions: Optional[list] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update job fields. Merges with existing job."""
        job = self.get_job(job_id)
        if not job:
            return
        if status is not None:
            job["status"] = status.value
        if transcript is not None:
            job["transcript"] = transcript
        if clips is not None:
            job["clips"] = clips
        if captions is not None:
            job["captions"] = captions
        if error is not None:
            job["error"] = error
        job["updated_at"] = datetime.utcnow().isoformat() + "Z"
        key = f"{self.KEY_JOB_PREFIX}{job_id}"
        self.client.set(key, json.dumps(job))

    def get_next_queued_job_id(self) -> Optional[str]:
        """Return one queued job ID and mark as processing (simple poll)."""
        for jid in self.get_all_job_ids():
            job = self.get_job(jid)
            if job and job.get("status") == JobStatus.QUEUED.value:
                self.update_job(jid, status=JobStatus.PROCESSING)
                return jid
        return None

    def set_caption_cache(self, cache_key: str, value: str) -> None:
        """Cache generated caption (e.g. by transcript hash). TODO: TTL in production."""
        self.client.set(f"clipforge:caption:{cache_key}", value)

    def get_caption_cache(self, cache_key: str) -> Optional[str]:
        """Retrieve cached caption."""
        return self.client.get(f"clipforge:caption:{cache_key}")

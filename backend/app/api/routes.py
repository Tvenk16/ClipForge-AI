"""
FastAPI job routes: create and list jobs, get job by ID.
"""

import redis

from fastapi import APIRouter, HTTPException

from app.models.job import JobCreate, JobResponse, JobStatus
from app.services.redis_service import RedisService

router = APIRouter(prefix="/jobs", tags=["jobs"])
redis_svc = RedisService()


def _handle_redis_error():
    raise HTTPException(
        status_code=503,
        detail="Redis unavailable. Start Redis (e.g. redis-server) and retry.",
    )


@router.post("", response_model=dict)
def create_job(body: JobCreate) -> dict:
    """Create a job with status queued. Returns job ID."""
    try:
        job_id = redis_svc.create_job(body.youtube_url)
        return {"id": job_id, "status": JobStatus.QUEUED.value}
    except redis.exceptions.ConnectionError:
        _handle_redis_error()


@router.get("", response_model=list[JobResponse])
def list_jobs() -> list[JobResponse]:
    """Return all jobs from Redis."""
    try:
        jobs = redis_svc.get_all_jobs()
        return [JobResponse(**j) for j in jobs]
    except redis.exceptions.ConnectionError:
        return []


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    """Return job details by ID."""
    try:
        job = redis_svc.get_job(job_id)
    except redis.exceptions.ConnectionError:
        _handle_redis_error()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(**job)

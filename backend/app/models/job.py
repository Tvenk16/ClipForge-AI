"""
Job and pipeline data models.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job lifecycle states."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ClipTimestamp(BaseModel):
    """A single clip time range."""

    start_seconds: float
    end_seconds: float
    label: Optional[str] = None


class CaptionOutput(BaseModel):
    """Generated caption components from CaptionAgent."""

    hook: str
    caption: str
    hashtags: list[str] = Field(default_factory=list)


class JobCreate(BaseModel):
    """Request body for creating a job."""

    youtube_url: str = Field(..., description="YouTube video URL to process")


class JobResponse(BaseModel):
    """Job as returned by API."""

    id: str
    status: JobStatus
    youtube_url: str
    transcript: Optional[str] = None
    clips: Optional[list[dict[str, Any]]] = None
    captions: Optional[list[dict[str, Any]]] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.scanpy import JobStatus


class TimestampSchema(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobStatusSchema(BaseModel):
    """Job status response"""
    status: JobStatus
    current_step: Optional[str] = None
    progress_percent: int = 0
    error_message = Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
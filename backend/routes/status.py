"""
Status routes for tracking video generation progress
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

# In-memory job status storage
job_status: Dict[str, Dict[str, Any]] = {}

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    message: str
    result: dict | None = None

def update_job_status(job_id: str, status: str, progress: float, message: str, result: dict = None):
    """Update the status of a job"""
    job_status[job_id] = {
        "status": status,
        "progress": progress,
        "message": message,
        "result": result
    }

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the current status of a video generation job"""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job_id,
        **job_status[job_id]
    )

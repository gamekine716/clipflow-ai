"""
Job status and clip management endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.core.logger import log

router = APIRouter()

class Clip(BaseModel):
    id: str
    start_time: float
    end_time: float
    title: str
    viral_score: float
    viral_score_reason: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    clips: List[Clip] = []

@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job processing status"""
    log.info("job_status_requested", job_id=job_id)
    
    # TODO: Implement actual status checking in Phase 5
    return {
        "job_id": job_id,
        "status": "processing",
        "progress": 0,
        "message": "Video queued for processing",
        "clips": []
    }

@router.get("/jobs/{job_id}/clips", response_model=List[Clip])
async def get_job_clips(job_id: str):
    """Get detected clips for a job"""
    log.info("clips_requested", job_id=job_id)
    
    # TODO: Implement actual clip fetching in Phase 2
    return []

@router.get("/download/{clip_id}")
async def download_clip(clip_id: str):
    """Download processed clip"""
    log.info("download_requested", clip_id=clip_id)
    
    # TODO: Implement actual download in Phase 3
    raise HTTPException(status_code=404, detail="Clip not found")

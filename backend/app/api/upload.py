"""
Video upload endpoints
"""

from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from app.core.logger import log

router = APIRouter()

class UploadResponse(BaseModel):
    job_id: str
    status: str
    message: str

@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    file: Optional[UploadFile] = File(None),
    youtube_url: Optional[str] = Form(None)
):
    """
    Upload video for processing.
    Either file OR youtube_url must be provided.
    """
    log.info("upload_requested", has_file=file is not None, has_url=youtube_url is not None)
    
    if not file and not youtube_url:
        return {"job_id": "", "status": "error", "message": "Either file or youtube_url required"}
    
    # TODO: Implement actual upload logic in Phase 1
    job_id = "temp_job_123"
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Upload received, processing started"
    }

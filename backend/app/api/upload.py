"""
Video upload endpoints
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
import uuid

from app.core.logger import log
from app.services.youtube import YouTubeParser, YouTubeVideoError
from app.config import settings

router = APIRouter()

class UploadResponse(BaseModel):
    job_id: str
    status: str
    message: str
    video_id: Optional[str] = None
    title: Optional[str] = None
    duration: Optional[int] = None

class YouTubeMetadataResponse(BaseModel):
    video_id: str
    title: str
    duration: int
    uploader: str
    view_count: int
    thumbnail: str

@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    file: Optional[UploadFile] = File(None),
    youtube_url: Optional[str] = Form(None)
):
    """
    Upload video for processing.
    Either file OR youtube_url must be provided.
    
    Args:
        file: MP4/MOV file upload
        youtube_url: YouTube video URL
        
    Returns:
        Job details with processing status
    """
    try:
        log.info("upload_requested", has_file=file is not None, has_url=youtube_url is not None)
        
        if not file and not youtube_url:
            raise HTTPException(
                status_code=400,
                detail="Either file or youtube_url required"
            )
        
        job_id = str(uuid.uuid4())
        youtube_parser = YouTubeParser()
        
        if youtube_url:
            # Validate YouTube URL
            if not YouTubeParser.is_youtube_url(youtube_url):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid YouTube URL"
                )
            
            try:
                # Fetch metadata to validate URL
                metadata = await youtube_parser.get_video_metadata(youtube_url)
                
                log.info(
                    "youtube_upload_initiated",
                    job_id=job_id,
                    video_id=metadata.get('video_id'),
                    title=metadata.get('title'),
                    duration=metadata.get('duration')
                )
                
                return {
                    "job_id": job_id,
                    "status": "pending",
                    "message": f"YouTube video queued for processing: {metadata.get('title')}",
                    "video_id": metadata.get('video_id'),
                    "title": metadata.get('title'),
                    "duration": metadata.get('duration'),
                }
            except YouTubeVideoError as e:
                log.error("youtube_validation_error", error=str(e), url=youtube_url)
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to access YouTube video: {str(e)}"
                )
        
        else:  # file upload
            # Validate file type
            if file.content_type not in ["video/mp4", "video/quicktime", "video/x-msvideo"]:
                raise HTTPException(
                    status_code=400,
                    detail="Only MP4, MOV, and AVI files allowed"
                )
            
            # Check file size
            file_size = file.size or 0
            max_size = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024
            if file_size > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds {settings.MAX_VIDEO_SIZE_MB}MB limit"
                )
            
            log.info(
                "file_upload_initiated",
                job_id=job_id,
                filename=file.filename,
                size_mb=file_size / (1024 * 1024)
            )
            
            # TODO: Phase 1b - Implement actual file storage
            return {
                "job_id": job_id,
                "status": "pending",
                "message": f"File upload queued: {file.filename}",
                "title": file.filename,
            }
    
    except HTTPException:
        raise
    except Exception as e:
        log.error("upload_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal server error during upload"
        )

@router.post("/youtube/metadata", response_model=YouTubeMetadataResponse)
async def get_youtube_metadata(youtube_url: str):
    """
    Get metadata for a YouTube video without downloading
    
    Args:
        youtube_url: YouTube video URL
        
    Returns:
        Video metadata
    """
    try:
        if not YouTubeParser.is_youtube_url(youtube_url):
            raise HTTPException(
                status_code=400,
                detail="Invalid YouTube URL"
            )
        
        youtube_parser = YouTubeParser()
        metadata = await youtube_parser.get_video_metadata(youtube_url)
        
        return {
            "video_id": metadata.get('video_id'),
            "title": metadata.get('title'),
            "duration": metadata.get('duration'),
            "uploader": metadata.get('uploader'),
            "view_count": metadata.get('view_count', 0),
            "thumbnail": metadata.get('thumbnail'),
        }
    except YouTubeVideoError as e:
        log.error("youtube_metadata_error", error=str(e), url=youtube_url)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch metadata: {str(e)}"
        )
    except Exception as e:
        log.error("metadata_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

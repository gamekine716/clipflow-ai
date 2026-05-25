"""
Local file upload and video handling service
"""

import os
import shutil
import asyncio
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import mimetypes
from fastapi import UploadFile
import aiofiles

from app.config import settings
from app.core.logger import log

class FileUploadError(Exception):
    """File upload processing error"""
    pass

class LocalFileUploader:
    """
    Handles local file uploads with validation, storage, and metadata extraction
    """
    
    # Supported video formats
    SUPPORTED_FORMATS = {
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo',
        '.mkv': 'video/x-matroska',
        '.flv': 'video/x-flv',
        '.wmv': 'video/x-ms-wmv',
        '.webm': 'video/webm',
    }
    
    # Max file size in bytes (from config)
    MAX_FILE_SIZE = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024
    
    def __init__(self, upload_dir: str = "/tmp/clipflow/uploads"):
        """
        Initialize file uploader
        
        Args:
            upload_dir: Directory to store uploaded files
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.logger = log
    
    @staticmethod
    def is_supported_format(filename: str) -> bool:
        """
        Check if file format is supported
        
        Args:
            filename: File name to check
            
        Returns:
            True if format is supported
        """
        ext = Path(filename).suffix.lower()
        return ext in LocalFileUploader.SUPPORTED_FORMATS
    
    @staticmethod
    def get_file_size_mb(file_size_bytes: int) -> float:
        """
        Convert bytes to MB
        
        Args:
            file_size_bytes: Size in bytes
            
        Returns:
            Size in MB
        """
        return file_size_bytes / (1024 * 1024)
    
    def validate_upload(self, filename: str, file_size: int) -> tuple[bool, str]:
        """
        Validate file before upload
        
        Args:
            filename: File name
            file_size: File size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check format
        if not self.is_supported_format(filename):
            supported = ', '.join(self.SUPPORTED_FORMATS.keys())
            return False, f"Unsupported format. Supported: {supported}"
        
        # Check size
        if file_size > self.MAX_FILE_SIZE:
            max_mb = settings.MAX_VIDEO_SIZE_MB
            return False, f"File size exceeds {max_mb}MB limit"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, ""
    
    async def save_upload(
        self,
        upload_file: UploadFile,
        upload_id: str
    ) -> Dict:
        """
        Save uploaded file to disk
        
        Args:
            upload_file: FastAPI UploadFile object
            upload_id: Unique upload identifier (e.g., job_id)
            
        Returns:
            Dictionary with file info and path
            
        Raises:
            FileUploadError: If upload or validation fails
        """
        try:
            # Create upload directory for this job
            job_dir = self.upload_dir / upload_id
            job_dir.mkdir(parents=True, exist_ok=True)
            
            # Read file content to check size
            file_content = await upload_file.read()
            file_size = len(file_content)
            
            # Validate
            is_valid, error_msg = self.validate_upload(upload_file.filename, file_size)
            if not is_valid:
                raise FileUploadError(error_msg)
            
            # Save file
            file_path = job_dir / upload_file.filename
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            self.logger.info(
                "file_upload_complete",
                upload_id=upload_id,
                filename=upload_file.filename,
                size_mb=self.get_file_size_mb(file_size),
                path=str(file_path)
            )
            
            return {
                'upload_id': upload_id,
                'filename': upload_file.filename,
                'file_path': str(file_path),
                'file_size_bytes': file_size,
                'file_size_mb': self.get_file_size_mb(file_size),
                'content_type': upload_file.content_type,
                'uploaded_at': datetime.utcnow().isoformat(),
                'success': True,
            }
        
        except FileUploadError as e:
            self.logger.error(
                "file_upload_validation_error",
                error=str(e),
                filename=upload_file.filename
            )
            raise
        
        except Exception as e:
            self.logger.error(
                "file_upload_error",
                error=str(e),
                filename=upload_file.filename
            )
            raise FileUploadError(f"Upload failed: {str(e)}")
    
    async def stream_upload(
        self,
        upload_file: UploadFile,
        upload_id: str,
        chunk_size: int = 1024 * 1024  # 1MB chunks
    ) -> Dict:
        """
        Stream large file upload to avoid memory issues
        
        Args:
            upload_file: FastAPI UploadFile object
            upload_id: Unique upload identifier
            chunk_size: Size of chunks to read (default 1MB)
            
        Returns:
            Dictionary with file info and path
            
        Raises:
            FileUploadError: If upload fails
        """
        try:
            # Validate format first
            if not self.is_supported_format(upload_file.filename):
                raise FileUploadError("Unsupported file format")
            
            # Create job directory
            job_dir = self.upload_dir / upload_id
            job_dir.mkdir(parents=True, exist_ok=True)
            file_path = job_dir / upload_file.filename
            
            total_size = 0
            
            self.logger.info(
                "stream_upload_started",
                upload_id=upload_id,
                filename=upload_file.filename
            )
            
            # Stream and save in chunks
            async with aiofiles.open(file_path, 'wb') as f:
                while True:
                    chunk = await upload_file.read(chunk_size)
                    if not chunk:
                        break
                    
                    total_size += len(chunk)
                    
                    # Check size limit during upload
                    if total_size > self.MAX_FILE_SIZE:
                        # Clean up partial file
                        await f.close()
                        file_path.unlink()
                        raise FileUploadError(f"File exceeds {settings.MAX_VIDEO_SIZE_MB}MB limit")
                    
                    await f.write(chunk)
            
            self.logger.info(
                "stream_upload_complete",
                upload_id=upload_id,
                filename=upload_file.filename,
                size_mb=self.get_file_size_mb(total_size)
            )
            
            return {
                'upload_id': upload_id,
                'filename': upload_file.filename,
                'file_path': str(file_path),
                'file_size_bytes': total_size,
                'file_size_mb': self.get_file_size_mb(total_size),
                'uploaded_at': datetime.utcnow().isoformat(),
                'success': True,
            }
        
        except FileUploadError as e:
            self.logger.error("stream_upload_error", error=str(e))
            raise
        except Exception as e:
            self.logger.error("stream_upload_exception", error=str(e))
            raise FileUploadError(f"Stream upload failed: {str(e)}")
    
    def get_upload_info(self, upload_id: str, filename: str) -> Optional[Dict]:
        """
        Get info about uploaded file
        
        Args:
            upload_id: Upload identifier
            filename: File name
            
        Returns:
            File info or None if not found
        """
        file_path = self.upload_dir / upload_id / filename
        
        if file_path.exists():
            stat = file_path.stat()
            return {
                'filename': filename,
                'file_path': str(file_path),
                'file_size_bytes': stat.st_size,
                'file_size_mb': self.get_file_size_mb(stat.st_size),
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        
        return None
    
    def cleanup_upload(self, upload_id: str) -> bool:
        """
        Delete uploaded files for an upload ID
        
        Args:
            upload_id: Upload identifier to cleanup
            
        Returns:
            True if cleanup successful
        """
        try:
            upload_dir = self.upload_dir / upload_id
            if upload_dir.exists():
                shutil.rmtree(upload_dir)
                self.logger.info("upload_cleanup_complete", upload_id=upload_id)
                return True
        except Exception as e:
            self.logger.error("upload_cleanup_error", upload_id=upload_id, error=str(e))
        
        return False


# Singleton instance
_uploader: Optional[LocalFileUploader] = None

def get_file_uploader() -> LocalFileUploader:
    """Get or create file uploader singleton"""
    global _uploader
    if _uploader is None:
        _uploader = LocalFileUploader()
    return _uploader

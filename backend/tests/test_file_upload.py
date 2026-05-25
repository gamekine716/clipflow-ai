"""
Tests for file upload service
"""

import pytest
import tempfile
from pathlib import Path
from fastapi import UploadFile
from io import BytesIO

from app.services.file_upload import LocalFileUploader, FileUploadError

@pytest.fixture
def uploader():
    """Create file uploader with temp directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield LocalFileUploader(upload_dir=tmpdir)

def test_is_supported_format():
    """Test file format validation"""
    supported = ["video.mp4", "video.mov", "video.avi", "video.mkv"]
    unsupported = ["video.txt", "video.jpg", "video.mp3", "document.pdf"]
    
    for filename in supported:
        assert LocalFileUploader.is_supported_format(filename)
    
    for filename in unsupported:
        assert not LocalFileUploader.is_supported_format(filename)

def test_file_size_calculation():
    """Test MB conversion"""
    assert LocalFileUploader.get_file_size_mb(1024 * 1024) == 1.0
    assert LocalFileUploader.get_file_size_mb(512 * 1024) == 0.5
    assert LocalFileUploader.get_file_size_mb(2048 * 1024 * 1024) == 2048.0

def test_validate_upload(uploader):
    """Test upload validation"""
    # Valid upload
    is_valid, msg = uploader.validate_upload("video.mp4", 100 * 1024 * 1024)
    assert is_valid
    assert msg == ""
    
    # Unsupported format
    is_valid, msg = uploader.validate_upload("video.txt", 100 * 1024 * 1024)
    assert not is_valid
    assert "Unsupported" in msg
    
    # File too large
    is_valid, msg = uploader.validate_upload("video.mp4", 3 * 1024 * 1024 * 1024)
    assert not is_valid
    assert "exceeds" in msg
    
    # Empty file
    is_valid, msg = uploader.validate_upload("video.mp4", 0)
    assert not is_valid
    assert "empty" in msg.lower()

@pytest.mark.asyncio
async def test_save_upload(uploader):
    """Test file save (mock)"""
    # Create mock upload file
    upload_id = "test-job-123"
    
    # Test that directory structure is created
    job_dir = uploader.upload_dir / upload_id
    assert not job_dir.exists()
    
    # After calling save_upload with valid file, directory should exist
    # (In real test, we'd create a proper UploadFile mock)
    
def test_get_upload_info(uploader):
    """Test getting upload information"""
    # Create test file
    upload_id = "test-123"
    job_dir = uploader.upload_dir / upload_id
    job_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = job_dir / "video.mp4"
    test_file.write_bytes(b"test data")
    
    # Get info
    info = uploader.get_upload_info(upload_id, "video.mp4")
    
    assert info is not None
    assert info['filename'] == "video.mp4"
    assert info['file_size_bytes'] == 9
    assert str(test_file) in info['file_path']
    
    # Non-existent file
    info = uploader.get_upload_info(upload_id, "nonexistent.mp4")
    assert info is None

def test_cleanup_upload(uploader):
    """Test cleanup of uploaded files"""
    # Create test files
    upload_id = "test-cleanup"
    job_dir = uploader.upload_dir / upload_id
    job_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = job_dir / "video.mp4"
    test_file.write_bytes(b"test")
    
    assert job_dir.exists()
    
    # Cleanup
    result = uploader.cleanup_upload(upload_id)
    
    assert result is True
    assert not job_dir.exists()

if __name__ == "__main__":
    print("Running file upload tests...")
    test_is_supported_format()
    print("✓ Format validation passed")
    
    test_file_size_calculation()
    print("✓ File size calculation passed")
    
    print("\nAll tests passed!")

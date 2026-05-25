"""
Audio extraction from video using FFmpeg
Extracts MP3 audio for Gemini transcription and subtitle generation
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Optional
import asyncio
from datetime import datetime

from app.config import settings
from app.core.logger import log

class AudioExtractionError(Exception):
    """Audio extraction error"""
    pass

class AudioExtractor:
    """
    Extract audio from video files using FFmpeg
    Supports MP3, WAV, and AAC formats
    """
    
    # Supported output formats
    OUTPUT_FORMATS = ['mp3', 'wav', 'aac', 'flac']
    
    # FFmpeg path
    FFMPEG_PATH = settings.FFMPEG_PATH
    
    def __init__(self, ffmpeg_path: Optional[str] = None):
        """
        Initialize audio extractor
        
        Args:
            ffmpeg_path: Path to ffmpeg executable (defaults to settings)
        """
        self.ffmpeg_path = ffmpeg_path or self.FFMPEG_PATH
        self.logger = log
        
        # Verify FFmpeg is available
        if not self._check_ffmpeg():
            raise AudioExtractionError(
                f"FFmpeg not found at {self.ffmpeg_path}. "
                "Please install FFmpeg: https://ffmpeg.org/download.html"
            )
    
    def _check_ffmpeg(self) -> bool:
        """
        Check if FFmpeg is available
        
        Returns:
            True if FFmpeg is available
        """
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _get_video_duration(self, video_path: str) -> Optional[float]:
        """
        Get video duration in seconds using FFmpeg
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds or None if unable to get
        """
        try:
            cmd = [
                self.ffmpeg_path,
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1:noprint_wrappers=1',
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except Exception as e:
            self.logger.warning(
                "duration_extraction_failed",
                video_path=video_path,
                error=str(e)
            )
        
        return None
    
    async def extract_audio(
        self,
        video_path: str,
        output_format: str = 'mp3',
        audio_quality: str = '192k',
        output_dir: Optional[str] = None
    ) -> Dict:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to video file
            output_format: Output audio format (mp3, wav, aac, flac)
            audio_quality: Audio bitrate (e.g., '192k', '320k')
            output_dir: Output directory (defaults to video directory)
            
        Returns:
            Dictionary with audio file info
            
        Raises:
            AudioExtractionError: If extraction fails
        """
        try:
            video_path = Path(video_path)
            
            if not video_path.exists():
                raise AudioExtractionError(f"Video file not found: {video_path}")
            
            if output_format not in self.OUTPUT_FORMATS:
                raise AudioExtractionError(
                    f"Unsupported format. Supported: {', '.join(self.OUTPUT_FORMATS)}"
                )
            
            # Set output directory
            if output_dir is None:
                output_dir = video_path.parent
            else:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            output_filename = f"{video_path.stem}_audio.{output_format}"
            output_path = output_dir / output_filename
            
            self.logger.info(
                "audio_extraction_started",
                video_path=str(video_path),
                output_path=str(output_path),
                quality=audio_quality
            )
            
            # Get video duration for reference
            duration = self._get_video_duration(str(video_path))
            
            # FFmpeg command
            cmd = [
                self.ffmpeg_path,
                '-i', str(video_path),  # Input file
                '-q:a', '0',             # Best quality for given bitrate
                '-b:a', audio_quality,   # Audio bitrate
                '-ar', '16000',          # Sample rate (16kHz for speech recognition)
                '-ac', '1',              # Mono (mono is better for speech)
                '-y',                    # Overwrite output file
                str(output_path)
            ]
            
            # Run FFmpeg async
            loop = asyncio.get_event_loop()
            process = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=settings.PROCESSING_TIMEOUT_SECONDS
                )
            )
            
            if process.returncode != 0:
                error_msg = process.stderr.decode('utf-8', errors='ignore')
                raise AudioExtractionError(f"FFmpeg error: {error_msg}")
            
            # Check output file
            if not output_path.exists():
                raise AudioExtractionError("Output audio file was not created")
            
            audio_size = output_path.stat().st_size
            
            self.logger.info(
                "audio_extraction_complete",
                output_path=str(output_path),
                size_mb=audio_size / (1024 * 1024),
                duration=duration
            )
            
            return {
                'video_path': str(video_path),
                'audio_path': str(output_path),
                'format': output_format,
                'quality': audio_quality,
                'file_size_bytes': audio_size,
                'file_size_mb': audio_size / (1024 * 1024),
                'duration': duration,
                'extracted_at': datetime.utcnow().isoformat(),
                'success': True,
            }
        
        except AudioExtractionError as e:
            self.logger.error("audio_extraction_error", error=str(e))
            raise
        except Exception as e:
            self.logger.error(
                "audio_extraction_exception",
                error=str(e),
                video_path=str(video_path)
            )
            raise AudioExtractionError(f"Audio extraction failed: {str(e)}")
    
    async def extract_audio_segment(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_format: str = 'mp3',
        output_dir: Optional[str] = None
    ) -> Dict:
        """
        Extract audio segment from video (for specific clip)
        
        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            end_time: End time in seconds
            output_format: Output format
            output_dir: Output directory
            
        Returns:
            Dictionary with segment audio info
            
        Raises:
            AudioExtractionError: If extraction fails
        """
        try:
            video_path = Path(video_path)
            
            if not video_path.exists():
                raise AudioExtractionError(f"Video file not found: {video_path}")
            
            if output_dir is None:
                output_dir = video_path.parent
            else:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename with timestamp
            output_filename = f"{video_path.stem}_segment_{start_time}_{end_time}.{output_format}"
            output_path = output_dir / output_filename
            
            duration = end_time - start_time
            
            self.logger.info(
                "audio_segment_extraction_started",
                video_path=str(video_path),
                segment=(start_time, end_time),
                duration=duration
            )
            
            # FFmpeg command for segment
            cmd = [
                self.ffmpeg_path,
                '-i', str(video_path),
                '-ss', str(start_time),           # Start time
                '-to', str(end_time),             # End time
                '-q:a', '0',
                '-b:a', '192k',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                str(output_path)
            ]
            
            loop = asyncio.get_event_loop()
            process = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=min(settings.PROCESSING_TIMEOUT_SECONDS, int(duration) + 10)
                )
            )
            
            if process.returncode != 0:
                error_msg = process.stderr.decode('utf-8', errors='ignore')
                raise AudioExtractionError(f"FFmpeg error: {error_msg}")
            
            if not output_path.exists():
                raise AudioExtractionError("Segment audio file not created")
            
            audio_size = output_path.stat().st_size
            
            self.logger.info(
                "audio_segment_extraction_complete",
                output_path=str(output_path),
                size_mb=audio_size / (1024 * 1024)
            )
            
            return {
                'video_path': str(video_path),
                'audio_path': str(output_path),
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'format': output_format,
                'file_size_mb': audio_size / (1024 * 1024),
                'success': True,
            }
        
        except AudioExtractionError as e:
            self.logger.error("audio_segment_extraction_error", error=str(e))
            raise
        except Exception as e:
            self.logger.error("audio_segment_exception", error=str(e))
            raise AudioExtractionError(f"Segment extraction failed: {str(e)}")
    
    def cleanup_audio(self, audio_path: str) -> bool:
        """
        Delete extracted audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if cleanup successful
        """
        try:
            audio_path = Path(audio_path)
            if audio_path.exists():
                audio_path.unlink()
                self.logger.info("audio_cleanup_complete", audio_path=str(audio_path))
                return True
        except Exception as e:
            self.logger.error("audio_cleanup_error", audio_path=str(audio_path), error=str(e))
        
        return False


# Singleton instance
_extractor: Optional[AudioExtractor] = None

def get_audio_extractor(ffmpeg_path: Optional[str] = None) -> AudioExtractor:
    """Get or create audio extractor singleton"""
    global _extractor
    if _extractor is None:
        _extractor = AudioExtractor(ffmpeg_path)
    return _extractor

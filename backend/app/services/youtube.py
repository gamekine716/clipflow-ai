"""
YouTube video downloader service using yt-dlp
"""

import os
import re
import asyncio
import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import yt_dlp

from app.config import settings
from app.core.logger import log

class YouTubeVideoError(Exception):
    """YouTube video processing error"""
    pass

class YouTubeParser:
    """
    YouTube URL parser and video downloader
    Extracts metadata and downloads video files for processing
    """
    
    # Supported YouTube URL patterns
    YOUTUBE_URL_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&\s]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([^\s?]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/@[\w-]+/?(?:\?.*)?$',  # Channel URL
        r'(?:https?://)?(?:www\.)?youtube\.com/channel/[\w-]+/?(?:\?.*)?$',  # Channel ID URL
    ]
    
    def __init__(self, output_dir: str = "/tmp/clipflow/videos"):
        """
        Initialize YouTube parser
        
        Args:
            output_dir: Directory to store downloaded videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = log
        
    @staticmethod
    def is_youtube_url(url: str) -> bool:
        """
        Validate if URL is a YouTube link
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL is a valid YouTube URL
        """
        return any(re.match(pattern, url) for pattern in YouTubeParser.YOUTUBE_URL_PATTERNS)
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID or None if not found
        """
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&\s]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([^\s?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def get_video_metadata(self, url: str) -> Dict:
        """
        Fetch video metadata from YouTube without downloading
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with video metadata
            
        Raises:
            YouTubeVideoError: If metadata extraction fails
        """
        try:
            self.logger.info("fetching_youtube_metadata", url=url)
            
            ydl_opts = {
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                'socket_timeout': 30,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Run in executor to avoid blocking
                loop = asyncio.get_event_loop()
                info = await loop.run_in_executor(
                    None,
                    lambda: ydl.extract_info(url, download=False)
                )
            
            return {
                'video_id': info.get('id'),
                'title': info.get('title'),
                'duration': info.get('duration'),  # in seconds
                'upload_date': info.get('upload_date'),
                'uploader': info.get('uploader'),
                'description': info.get('description'),
                'thumbnail': info.get('thumbnail'),
                'view_count': info.get('view_count'),
                'url': info.get('webpage_url'),
                'format_available': True,
            }
        except Exception as e:
            self.logger.error("youtube_metadata_error", error=str(e), url=url)
            raise YouTubeVideoError(f"Failed to fetch metadata: {str(e)}")
    
    async def download_video(
        self,
        url: str,
        quality: str = "best",
        audio_only: bool = False
    ) -> Dict:
        """
        Download video from YouTube
        
        Args:
            url: YouTube video URL
            quality: Video quality ('best', '720p', '480p', etc.)
            audio_only: If True, extract only audio
            
        Returns:
            Dictionary with download info and file paths
            
        Raises:
            YouTubeVideoError: If download fails
        """
        try:
            self.logger.info(
                "downloading_youtube_video",
                url=url,
                quality=quality,
                audio_only=audio_only
            )
            
            video_id = self.extract_video_id(url)
            if not video_id:
                raise YouTubeVideoError(f"Could not extract video ID from URL: {url}")
            
            # Create subdirectory for this video
            video_dir = self.output_dir / video_id
            video_dir.mkdir(parents=True, exist_ok=True)
            
            if audio_only:
                # Download audio only
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': str(video_dir / '%(title)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'socket_timeout': 60,
                }
            else:
                # Download video + audio
                format_opts = {
                    'best': 'bestvideo+bestaudio/best',
                    '720p': 'bestvideo[height<=720]+bestaudio/best',
                    '480p': 'bestvideo[height<=480]+bestaudio/best',
                    '360p': 'bestvideo[height<=360]+bestaudio/best',
                }
                
                ydl_opts = {
                    'format': format_opts.get(quality, 'bestvideo+bestaudio/best'),
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4'
                    }],
                    'outtmpl': str(video_dir / '%(title)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'socket_timeout': 60,
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                loop = asyncio.get_event_loop()
                info = await loop.run_in_executor(
                    None,
                    lambda: ydl.extract_info(url, download=True)
                )
            
            # Get the actual file path
            video_files = list(video_dir.glob('*'))
            if not video_files:
                raise YouTubeVideoError("No video files found after download")
            
            video_file = max(video_files, key=lambda x: x.stat().st_size)
            
            self.logger.info(
                "youtube_download_complete",
                video_id=video_id,
                file_path=str(video_file),
                size_mb=video_file.stat().st_size / (1024 * 1024)
            )
            
            return {
                'video_id': video_id,
                'title': info.get('title'),
                'file_path': str(video_file),
                'file_size_bytes': video_file.stat().st_size,
                'duration': info.get('duration'),
                'url': url,
                'success': True,
            }
            
        except Exception as e:
            self.logger.error(
                "youtube_download_error",
                error=str(e),
                url=url
            )
            raise YouTubeVideoError(f"Download failed: {str(e)}")
    
    async def get_channel_videos(
        self,
        channel_url: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Fetch list of videos from a YouTube channel
        
        Args:
            channel_url: YouTube channel URL
            limit: Maximum number of videos to fetch
            
        Returns:
            List of video metadata dictionaries
            
        Raises:
            YouTubeVideoError: If fetching fails
        """
        try:
            self.logger.info(
                "fetching_channel_videos",
                channel_url=channel_url,
                limit=limit
            )
            
            ydl_opts = {
                'quiet': False,
                'no_warnings': False,
                'extract_flat': True,
                'playlistend': limit,
                'socket_timeout': 30,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                loop = asyncio.get_event_loop()
                info = await loop.run_in_executor(
                    None,
                    lambda: ydl.extract_info(channel_url, download=False)
                )
            
            videos = []
            for entry in info.get('entries', [])[:limit]:
                if entry:
                    videos.append({
                        'video_id': entry.get('id'),
                        'title': entry.get('title'),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'duration': entry.get('duration'),
                        'upload_date': entry.get('upload_date'),
                    })
            
            self.logger.info(
                "channel_videos_fetched",
                channel_url=channel_url,
                count=len(videos)
            )
            
            return videos
            
        except Exception as e:
            self.logger.error(
                "channel_fetch_error",
                error=str(e),
                channel_url=channel_url
            )
            raise YouTubeVideoError(f"Failed to fetch channel videos: {str(e)}")
    
    def cleanup_video(self, video_id: str) -> bool:
        """
        Delete downloaded video and its directory
        
        Args:
            video_id: Video ID to cleanup
            
        Returns:
            True if cleanup successful
        """
        try:
            video_dir = self.output_dir / video_id
            if video_dir.exists():
                import shutil
                shutil.rmtree(video_dir)
                self.logger.info("video_cleanup_complete", video_id=video_id)
                return True
        except Exception as e:
            self.logger.error("video_cleanup_error", video_id=video_id, error=str(e))
        return False


# Singleton instance
_youtube_parser: Optional[YouTubeParser] = None

def get_youtube_parser() -> YouTubeParser:
    """Get or create YouTube parser singleton"""
    global _youtube_parser
    if _youtube_parser is None:
        _youtube_parser = YouTubeParser()
    return _youtube_parser

"""
Tests for YouTube parser service
"""

import pytest
import asyncio
from app.services.youtube import YouTubeParser, YouTubeVideoError

@pytest.fixture
def youtube_parser():
    """Create YouTube parser instance"""
    return YouTubeParser(output_dir="/tmp/test_clipflow")

def test_is_youtube_url():
    """Test YouTube URL validation"""
    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/@Ai_Song_Hindi20",
        "https://www.youtube.com/channel/UCxxxxxx",
        "youtube.com/watch?v=dQw4w9WgXcQ",
    ]
    
    invalid_urls = [
        "https://www.google.com",
        "https://vimeo.com/123",
        "not-a-url",
    ]
    
    for url in valid_urls:
        assert YouTubeParser.is_youtube_url(url), f"Failed to recognize: {url}"
    
    for url in invalid_urls:
        assert not YouTubeParser.is_youtube_url(url), f"False positive: {url}"

def test_extract_video_id(youtube_parser):
    """Test video ID extraction"""
    # Standard URL
    url1 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert YouTubeParser.extract_video_id(url1) == "dQw4w9WgXcQ"
    
    # Shortened URL
    url2 = "https://youtu.be/dQw4w9WgXcQ"
    assert YouTubeParser.extract_video_id(url2) == "dQw4w9WgXcQ"
    
    # Channel URL (should return None)
    url3 = "https://www.youtube.com/@Ai_Song_Hindi20"
    assert YouTubeParser.extract_video_id(url3) is None

@pytest.mark.asyncio
async def test_get_video_metadata(youtube_parser):
    """Test fetching video metadata (requires internet)"""
    # Using a well-known short video for testing
    url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    
    try:
        metadata = await youtube_parser.get_video_metadata(url)
        assert metadata['video_id'] == "jNQXAC9IVRw"
        assert metadata['title']
        assert metadata['duration']
        assert metadata['format_available'] == True
    except YouTubeVideoError as e:
        pytest.skip(f"YouTube API not accessible: {e}")

@pytest.mark.asyncio
async def test_channel_videos_fetch(youtube_parser):
    """Test fetching videos from channel"""
    channel_url = "https://www.youtube.com/@Ai_Song_Hindi20"
    
    try:
        videos = await youtube_parser.get_channel_videos(channel_url, limit=5)
        assert isinstance(videos, list)
        assert len(videos) > 0
        
        # Check structure
        first_video = videos[0]
        assert 'video_id' in first_video
        assert 'title' in first_video
        assert 'url' in first_video
    except YouTubeVideoError as e:
        pytest.skip(f"Channel fetch failed: {e}")

if __name__ == "__main__":
    # Quick validation test
    print("Testing YouTube URL validation...")
    test_is_youtube_url()
    print("✓ URL validation passed")
    
    parser = YouTubeParser()
    print(f"\nTesting video ID extraction...")
    test_extract_video_id(parser)
    print("✓ Video ID extraction passed")

#!/usr/bin/env python
"""
Test script for YouTube parser
Usage: python test_youtube_parser.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from app.services.youtube import YouTubeParser, YouTubeVideoError

async def test_with_real_channel():
    """
    Test YouTube parser with real channel
    """
    print("\n" + "="*60)
    print("🎬 ClipFlow AI - YouTube Parser Test")
    print("="*60 + "\n")
    
    parser = YouTubeParser(output_dir="./test_videos")
    
    # Test Channel URL
    channel_url = "https://www.youtube.com/@Ai_Song_Hindi20"
    
    print(f"📍 Testing Channel: {channel_url}\n")
    
    # Test 1: Validate URL
    print("[Test 1] URL Validation")
    is_valid = YouTubeParser.is_youtube_url(channel_url)
    print(f"  ✓ URL is valid: {is_valid}")
    
    # Test 2: Fetch channel videos
    print("\n[Test 2] Fetch Channel Videos (limit: 5)")
    try:
        videos = await parser.get_channel_videos(channel_url, limit=5)
        print(f"  ✓ Found {len(videos)} videos")
        
        for i, video in enumerate(videos, 1):
            duration_min = (video.get('duration', 0) or 0) // 60
            print(f"    {i}. {video.get('title', 'N/A')[:50]}...")
            print(f"       Duration: {duration_min}m | URL: {video.get('url')}")
            
            # Test metadata fetch on first video
            if i == 1:
                print(f"\n[Test 3] Fetch Video Metadata")
                try:
                    metadata = await parser.get_video_metadata(video.get('url'))
                    print(f"  ✓ Video ID: {metadata.get('video_id')}")
                    print(f"  ✓ Title: {metadata.get('title')}")
                    print(f"  ✓ Duration: {metadata.get('duration')} seconds")
                    print(f"  ✓ Uploader: {metadata.get('uploader')}")
                    print(f"  ✓ Views: {metadata.get('view_count', 'N/A')}")
                except YouTubeVideoError as e:
                    print(f"  ✗ Error: {e}")
        
        print(f"\n✅ Channel Test Passed!\n")
        
    except YouTubeVideoError as e:
        print(f"  ✗ Error fetching videos: {e}")
        return False
    
    # Test 4: Test with specific video ID
    print("[Test 4] Video ID Extraction")
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
    ]
    
    for url in test_urls:
        vid_id = YouTubeParser.extract_video_id(url)
        print(f"  ✓ {url[:40]}... → {vid_id}")
    
    print("\n" + "="*60)
    print("✨ All tests completed successfully!")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_with_real_channel())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

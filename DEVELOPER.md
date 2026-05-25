# ClipFlow AI - Developer Quick Start

## 🚀 What's Been Built (Phase 1A)

Your ClipFlow AI backend foundation is ready with **3 core services**:

### 1️⃣ YouTube Parser Service
```python
from app.services.youtube import YouTubeParser

parser = YouTubeParser()

# Get channel videos
videos = await parser.get_channel_videos(
    "https://www.youtube.com/@Ai_Song_Hindi20",
    limit=10
)

# Get video metadata
metadata = await parser.get_video_metadata(
    "https://www.youtube.com/watch?v=..."
)

# Download video
result = await parser.download_video(
    url="https://www.youtube.com/watch?v=...",
    quality="720p"
)
```

### 2️⃣ Local File Upload Service
```python
from app.services.file_upload import LocalFileUploader
from fastapi import UploadFile

uploader = LocalFileUploader()

# Stream large files
result = await uploader.stream_upload(upload_file, job_id)

# Validate before upload
is_valid, error = uploader.validate_upload(
    filename="video.mp4",
    file_size=100 * 1024 * 1024  # 100MB
)
```

### 3️⃣ Audio Extraction Service
```python
from app.services.audio_extractor import AudioExtractor

extractor = AudioExtractor()  # Requires FFmpeg installed

# Extract full audio
audio_info = await extractor.extract_audio(
    video_path="/path/to/video.mp4",
    output_format="mp3",
    audio_quality="192k"
)

# Extract segment (for clip audio)
segment = await extractor.extract_audio_segment(
    video_path="/path/to/video.mp4",
    start_time=30.0,
    end_time=90.0
)
```

## 🌀 API Endpoints (Ready to Use)

### Upload Video
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "youtube_url=https://www.youtube.com/watch?v=..." 

# Response
{
  "job_id": "uuid-here",
  "status": "pending",
  "message": "YouTube video queued",
  "video_id": "...",
  "title": "...",
  "duration": 3600
}
```

### Get Video Metadata
```bash
curl -X POST "http://localhost:8000/api/v1/youtube/metadata" \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=..."}'

# Response
{
  "video_id": "...",
  "title": "Video Title",
  "duration": 3600,
  "uploader": "Channel Name",
  "view_count": 1000000,
  "thumbnail": "https://..."
}
```

## 💻 System Requirements

- **Python 3.10+**
- **Node.js 18+**
- **FFmpeg** (for audio extraction)
  - Windows: `choco install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Linux: `apt-get install ffmpeg`
- **Docker & Docker Compose** (for containerized dev)

## 🎨 Project Structure

```
backend/
├── app/
│   ├── api/                # REST endpoints
│   │   ├── upload.py        # Video upload endpoints
│   │   ├── jobs.py          # Job status endpoints (Phase 5)
│   │   └── health.py        # Health checks
│   ├── services/        # Business logic
│   │   ├── youtube.py       # YouTube parsing
│   │   ├── file_upload.py   # File upload handling
│   │   ├── audio_extractor.py # Audio extraction
│   │   └── gemini_transcriber.py (Phase 2)
│   ├── core/            # Shared utilities
│   │   └── logger.py        # Logging config
│   ├── tasks/           # Celery async tasks
│   └── config.py        # Settings/environment
├── tests/             # Test suite
├── requirements.txt    # Python dependencies
└── Dockerfile         # Container definition

frontend/
├── src/
│   ├── pages/           # Next.js pages
│   ├── components/      # React components (Phase 4)
│   └── hooks/           # Custom hooks (Phase 4)
├── public/            # Static assets
├── package.json
└── Dockerfile.dev
```

## 💵 Dependencies Included

**Backend:**
- `fastapi` - Async web framework
- `uvicorn` - ASGI server
- `yt-dlp` - YouTube downloader
- `celery` - Task queue
- `redis` - Message broker
- `google-generativeai` - Gemini API (Phase 2)
- `firebase-admin` - Firebase (Phase 1e)
- `opencv-python` - Video processing (Phase 3)
- `mediapipe` - Face detection (Phase 3)

**Frontend:**
- `next` - React framework
- `typescript` - Type safety
- `tailwindcss` - CSS framework
- `axios` - HTTP client

## 🚀 Quick Start

### Option 1: Local Development

```bash
# 1. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. In new terminal: Setup frontend
cd frontend
npm install
npm run dev

# API: http://localhost:8000
# Frontend: http://localhost:3000
# Docs: http://localhost:8000/docs (Swagger UI)
```

### Option 2: Docker Compose

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (optional for Phase 1)

# Run all services
docker-compose up --build

# API: http://localhost:8000
# Frontend: http://localhost:3000
# Redis: localhost:6379
```

## 💡 Usage Examples

### Example 1: Test YouTube Parser

```bash
python test_youtube_parser.py
```

This tests the provided channel: `https://www.youtube.com/@Ai_Song_Hindi20`

### Example 2: Upload via Python

```python
import asyncio
import aiofiles
import httpx

async def upload_file():
    async with aiofiles.open('video.mp4', 'rb') as f:
        file_content = await f.read()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://localhost:8000/api/v1/upload',
            files={'file': ('video.mp4', file_content, 'video/mp4')}
        )
        return response.json()

result = asyncio.run(upload_file())
print(result)
```

### Example 3: Extract Audio

```python
from app.services.audio_extractor import AudioExtractor

extractor = AudioExtractor()

result = await extractor.extract_audio(
    video_path='downloaded_video.mp4',
    output_format='mp3'
)

print(f"Audio saved to: {result['audio_path']}")
print(f"Size: {result['file_size_mb']:.2f} MB")
```

## 🛠️ Environment Variables

```bash
# Required (Phase 0-1)
FFMPEG_PATH=ffmpeg                    # Path to FFmpeg executable
MAX_VIDEO_SIZE_MB=2048                # Max upload size

# Coming (Phase 1d)
GCS_BUCKET=clipflow-videos-prod       # Google Cloud Storage bucket
GCS_PROJECT_ID=your-gcp-project

# Coming (Phase 1e)
FIREBASE_CREDENTIALS=base64_encoded   # Firebase service account JSON

# Coming (Phase 2)
GEMINI_API_KEY=your-api-key          # Google Gemini API key

# Coming (Phase 5)
REDIS_URL=redis://redis:6379/0        # Redis connection
STRIPE_SECRET_KEY=sk_test_...         # Stripe API key
```

## 💪 Extending the Services

### Add New Video Source (Phase 1)

```python
# backend/app/services/vimeo.py
class VimeoParser:
    async def get_video_metadata(self, url: str):
        # Implementation
        pass
```

Then use in `/api/v1/upload` endpoint.

### Add Video Processing (Phase 3)

```python
# backend/app/services/video_processor.py
class VideoProcessor:
    async def crop_to_9_16(self, video_path: str):
        # FFmpeg cropping logic
        pass
    
    async def add_subtitles(self, video_path: str, srt_path: str):
        # Subtitle burn-in
        pass
```

## 👀 Monitoring & Logs

### View Logs
```bash
# Backend
uvicorn app.main:app --reload --log-level=debug

# Docker
docker-compose logs backend -f
docker-compose logs celery_worker -f
```

### Health Checks
```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/ready
```

## 🐞 Testing

```bash
# Run unit tests
cd backend
pytest tests/

# Run with coverage
pytest tests/ --cov=app

# Run YouTube tests specifically
pytest tests/test_youtube.py -v
```

## ⚠️ Common Issues

### "FFmpeg not found"
```bash
# Install FFmpeg
Windows: choco install ffmpeg
macOS: brew install ffmpeg  
Linux: apt-get install ffmpeg

# Or set custom path in .env
FFMPEG_PATH=/usr/local/bin/ffmpeg
```

### "Connection refused" (Redis)
```bash
# Make sure Redis is running
docker-compose up redis

# Or install locally and run
redis-server
```

### "yt-dlp format error"
```bash
# Update yt-dlp
pip install --upgrade yt-dlp
```

## 📋 Architecture Diagrams

### Phase 1A Complete

```
☉️ User Upload Request
    ⬇️
[FastAPI Endpoint]
    ⬇️
    / \
   /   \
[YouTube Parser]  [File Uploader]
   |                  |
   v                  v
[GCS Upload]*    [Local Storage]
   |                  |
   +--------+--------+
            |
            v
     [Audio Extractor]
            |
            v
    [MP3 File Ready]
            |
            v
   [Gemini API]* (Phase 2)
            |
            v
   [Clip Detection]*
   
* = Next phase
```

## 🛹 Development Tips

1. **Use FastAPI's automatic docs**: `http://localhost:8000/docs`
2. **Async/await everywhere**: No blocking I/O
3. **Structured logging**: Include job IDs for tracing
4. **Error-specific exceptions**: Not generic Exception
5. **Type hints**: For IDE autocomplete and validation
6. **Docstrings**: Especially async functions

## 📃 Contributing

1. Pull latest from main
2. Create feature branch: `git checkout -b phase-1d-gcs`
3. Make changes following code style
4. Add tests for new functionality
5. Push and create PR

## 🤟 Support

For issues or questions:
1. Check PROGRESS.md for status
2. Review service docstrings
3. Run test scripts
4. Check Docker logs

---

**Next**: Phase 1D (GCS) → Phase 2 (Gemini) → Phase 3 (FFmpeg)  
**Repository**: https://github.com/gamekine716/clipflow-ai  
**Last Updated**: May 25, 2026

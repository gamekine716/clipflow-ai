# ClipFlow AI - MVP Edition

AI-powered micro-SaaS converting long-form videos (podcasts, webinars, YT) into viral short-form content (TikToks, Reels, Shorts).

## 🎯 MVP Scope (Phase 1.0)

- ✅ YouTube URL + local video upload (MP4, MOV)
- ✅ Gemini 1.5 Pro: Auto-transcription + viral clip detection (top 3)
- ✅ FFmpeg: Smart 9:16 cropping + word-by-word subtitle burn-in
- ✅ MP4 download with clip metadata
- ⏳ Social scheduling (Phase 2)

## 🏗️ Architecture

```
clipflow-ai/
├── backend/          (FastAPI + Celery)
│   ├── app/
│   ├── tasks/        (Celery jobs)
│   ├── services/     (Gemini, FFmpeg, GCS)
│   └── requirements.txt
├── frontend/         (Next.js Dashboard)
│   ├── src/
│   ├── public/
│   └── package.json
├── docker-compose.yml
└── .env.example
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- GCP credentials (Firebase, GCS, Gemini API)

### Environment Setup

```bash
# Copy example env
cp .env.example .env

# Fill in:
# - FIREBASE_CREDENTIALS (base64 encoded)
# - GEMINI_API_KEY
# - GCS_BUCKET
# - STRIPE_KEY (optional for MVP)
```

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Docker Compose

```bash
docker-compose up --build
```

## 📊 API Endpoints (MVP)

| Method | Endpoint | Purpose |
|--------|----------|----------|
| POST | `/api/v1/upload` | Upload video or YouTube URL |
| GET | `/api/v1/jobs/{job_id}` | Check processing status |
| GET | `/api/v1/jobs/{job_id}/clips` | Fetch detected clips |
| GET | `/api/v1/download/{clip_id}` | Download processed clip |

## 🔧 Development Phases

- **Phase 0**: ✅ Foundation (repo, Docker, CI/CD)
- **Phase 1**: Video ingestion + storage
- **Phase 2**: Gemini integration (transcription, hook detection)
- **Phase 3**: FFmpeg processing (cropping, subtitles)
- **Phase 4**: Next.js dashboard
- **Phase 5**: FastAPI backend + Celery
- **Phase 6**: Testing + deployment

## 📝 License

Proprietary - ClipFlow AI

"""
ClipFlow AI - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api import health, upload, jobs
from app.core.logger import setup_logging

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 ClipFlow AI Backend Starting...")
    yield
    # Shutdown
    print("🛑 ClipFlow AI Backend Shutdown")

app = FastAPI(
    title="ClipFlow AI",
    description="AI-powered short-form video generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

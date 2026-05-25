"""
Configuration management
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "ClipFlow AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Backend
    BACKEND_PORT: int = 8000
    BACKEND_ENV: str = "development"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Firebase & GCP
    FIREBASE_CREDENTIALS: str = ""
    GCS_BUCKET: str = "clipflow-videos-prod"
    GCS_PROJECT_ID: str = ""
    
    # Gemini API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # Processing
    MAX_VIDEO_SIZE_MB: int = 2048
    PROCESSING_TIMEOUT_SECONDS: int = 300
    FFMPEG_PATH: str = "ffmpeg"
    MEDIAPIPE_MODELS_PATH: str = "/app/models"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

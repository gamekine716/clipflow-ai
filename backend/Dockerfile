FROM python:3.10-slim

WORKDIR /app

# System dependencies (FFmpeg, MediaPipe, etc.)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Download MediaPipe models
RUN python -c "import mediapipe as mp; mp.solutions.face_detection"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

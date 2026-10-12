FROM python:3.11-slim

# Install system dependencies: FFmpeg for video processing and audio extraction, curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code into /app/backend
COPY . /app/backend/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV STORAGE_ROOT=/app/storage

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

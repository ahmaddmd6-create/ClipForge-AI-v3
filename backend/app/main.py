import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.db.session import init_db
from backend.app.api.routes import jobs, clips, storage, health

logger = logging.getLogger("clipforge")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist
    logger.info("Initializing database schema on startup...")
    init_db()
    yield
    # Shutdown logic if any
    logger.info("Shutting down ClipForge API...")

app = FastAPI(
    title="ClipForge AI API",
    description="Production-grade AI Video Processing & Autonomous 60s+ Short-Form Clipping Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(jobs.router)
app.include_router(clips.router)
app.include_router(storage.router)

# Mount outputs storage directory for direct static streaming if accessed directly
outputs_path = settings.outputs_dir
outputs_path.mkdir(parents=True, exist_ok=True)
app.mount("/storage/outputs", StaticFiles(directory=str(outputs_path)), name="storage_outputs")

@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

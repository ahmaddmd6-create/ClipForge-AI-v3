import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    app_name: str = Field(default="ClipForge AI", alias="APP_NAME")
    app_secret_key: str = Field(default="dev_secret_change_in_production", alias="APP_SECRET_KEY")
    frontend_origin: str = Field(default="http://localhost:8080", alias="FRONTEND_ORIGIN")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Database & Redis
    database_url: str = Field(
        default="postgresql+psycopg://clipforge:clipforge_secure_postgres_pass_2026@db:5432/clipforge",
        alias="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    # Storage paths
    storage_root: str = Field(default="./storage", alias="STORAGE_ROOT")
    max_upload_size_mb: int = Field(default=2048, alias="MAX_UPLOAD_SIZE_MB")
    max_source_duration_seconds: int = Field(default=14400, alias="MAX_SOURCE_DURATION_SECONDS")
    output_retention_days: int = Field(default=30, alias="OUTPUT_RETENTION_DAYS")

    # Clip parameters
    default_clip_count: int = Field(default=5, alias="DEFAULT_CLIP_COUNT")
    min_clip_duration_seconds: float = Field(default=60.0, alias="MIN_CLIP_DURATION_SECONDS")
    target_clip_duration_seconds: float = Field(default=75.0, alias="TARGET_CLIP_DURATION_SECONDS")
    max_clip_duration_seconds: float = Field(default=90.0, alias="MAX_CLIP_DURATION_SECONDS")
    default_aspect_ratio: str = Field(default="9:16", alias="DEFAULT_ASPECT_RATIO")

    # Concurrency and CPU optimization
    max_concurrent_jobs: int = Field(default=1, alias="MAX_CONCURRENT_JOBS")
    max_parallel_renders: int = Field(default=1, alias="MAX_PARALLEL_RENDERS")
    cpu_threads: int = Field(default=2, alias="CPU_THREADS")

    # Transcription
    transcription_provider: str = Field(default="faster-whisper", alias="TRANSCRIPTION_PROVIDER")
    whisper_model: str = Field(default="small", alias="WHISPER_MODEL")
    whisper_compute_type: str = Field(default="int8", alias="WHISPER_COMPUTE_TYPE")
    transcription_language: str = Field(default="auto", alias="TRANSCRIPTION_LANGUAGE")

    # AI Model Adapter
    ai_provider: str = Field(default="local", alias="AI_PROVIDER")
    ai_base_url: Optional[str] = Field(default=None, alias="AI_BASE_URL")
    ai_model: Optional[str] = Field(default=None, alias="AI_MODEL")
    ai_api_key: Optional[str] = Field(default=None, alias="AI_API_KEY")

    # YouTube metadata (optional)
    youtube_api_key: Optional[str] = Field(default=None, alias="YOUTUBE_API_KEY")

    # Security & CORS
    enable_auth: bool = Field(default=False, alias="ENABLE_AUTH")
    cors_allowed_origins: str = Field(
        default="http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ALLOWED_ORIGINS"
    )
    analytics_enabled: bool = Field(default=False, alias="ANALYTICS_ENABLED")

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    @property
    def storage_path(self) -> Path:
        p = Path(self.storage_root)
        if not p.is_absolute():
            # Resolve relative to repo root
            p = (Path(__file__).resolve().parent.parent.parent.parent / p).resolve()
        return p

    @property
    def inputs_dir(self) -> Path:
        d = self.storage_path / "inputs"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def outputs_dir(self) -> Path:
        d = self.storage_path / "outputs"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def models_dir(self) -> Path:
        d = self.storage_path / "models"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def thumbnails_dir(self) -> Path:
        d = self.storage_path / "thumbnails"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def temporary_dir(self) -> Path:
        d = self.storage_path / "temporary"
        d.mkdir(parents=True, exist_ok=True)
        return d

settings = Settings()

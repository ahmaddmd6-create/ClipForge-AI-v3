import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine():
    db_url = settings.database_url
    try:
        if "postgresql" in db_url:
            eng = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                connect_args={"connect_timeout": 5}
            )
            # Test connection
            with eng.connect() as conn:
                pass
            logger.info("Connected to PostgreSQL database successfully.")
            return eng
        else:
            return create_engine(db_url, connect_args={"check_same_thread": False})
    except Exception as e:
        logger.warning(f"Could not connect to configured DB ({db_url}): {e}. Falling back to SQLite local database.")
        sqlite_path = settings.storage_path / "clipforge.db"
        sqlite_url = f"sqlite:///{sqlite_path.as_posix()}"
        return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.app.models.job import Job
    from backend.app.models.source_asset import SourceAsset
    from backend.app.models.clip import Clip
    from backend.app.models.transcript import TranscriptSegment
    from backend.app.models.rendering import RenderingAttempt

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/initialized.")

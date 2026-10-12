from fastapi import APIRouter
from backend.app.schemas.storage import StorageStatsResponse
from backend.app.services.storage.storage_manager import get_storage_stats

router = APIRouter(prefix="/api/storage", tags=["Storage & Settings"])

@router.get("", response_model=StorageStatsResponse)
def get_system_storage():
    """Returns local storage metrics, directories, retention policies, and worker limits."""
    stats = get_storage_stats()
    return stats

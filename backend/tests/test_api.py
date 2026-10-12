import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "ClipForge AI" in data["service"]

def test_storage_endpoint():
    res = client.get("/api/storage")
    assert res.status_code == 200
    data = res.json()
    assert "total_used_mb" in data
    assert "outputs_directory" in data

def test_jobs_list_endpoint():
    res = client.get("/api/jobs")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_job_create_validation():
    # Attempting creation with min_duration < 60s should fail with 400 or 422
    res = client.post(
        "/api/jobs",
        data={
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "source_type": "youtube",
            "rights_declared": "true",
            "min_duration": "45.0"  # Invalid! Must be >= 60.0
        }
    )
    assert res.status_code in (400, 422)

    # Attempting creation without rights_declared should fail
    res2 = client.post(
        "/api/jobs",
        data={
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "source_type": "youtube",
            "rights_declared": "false"
        }
    )
    assert res2.status_code == 400

# ==============================================================================
# ClipForge AI - Local Launch Script (PowerShell)
# Starts Docker services (DB, Redis, Frontend) + Native API & Worker
# ==============================================================================

Write-Host ">>> [1/4] Ensuring local storage directories exist..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path `
  storage/inputs, `
  storage/outputs, `
  storage/models, `
  storage/thumbnails, `
  storage/temporary | Out-Null

Write-Host ">>> [2/4] Starting Docker infrastructure (PostgreSQL, Redis, Frontend)..." -ForegroundColor Cyan
docker compose up -d

Write-Host ">>> [3/4] Verifying database schema..." -ForegroundColor Cyan
$env:PYTHONPATH = "."
python -c "from backend.app.db.session import init_db; init_db()"

Write-Host ">>> [4/4] Starting FastAPI backend on port 8005 & Worker daemon..." -ForegroundColor Cyan
# Start API in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='.'; python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8005"
# Start Worker in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='.'; python -m backend.app.worker"

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host " ClipForge AI is up and running!" -ForegroundColor Green
Write-Host " Frontend Web App:      http://localhost:8080" -ForegroundColor Yellow
Write-Host " Backend API Docs:      http://localhost:8005/docs" -ForegroundColor Yellow
Write-Host " Outputs Directory:     .\storage\outputs" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Green

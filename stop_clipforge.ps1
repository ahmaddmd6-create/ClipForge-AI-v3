# ==============================================================================
# ClipForge AI - Stop Script (PowerShell)
# Stops background Python processes and Docker services cleanly
# ==============================================================================

Write-Host ">>> Stopping ClipForge Python background workers and API..." -ForegroundColor Cyan
Get-CimInstance Win32_Process | Where-Object { 
    $_.CommandLine -like "*backend.app.main:app*" -or 
    $_.CommandLine -like "*backend.app.worker*" 
} | ForEach-Object {
    Write-Host "Stopping process $($_.ProcessId): $($_.CommandLine)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

Write-Host ">>> Stopping Docker containers (frontend, redis, db)..." -ForegroundColor Cyan
docker compose stop

Write-Host ">>> ClipForge AI stopped. Persistent storage and database are preserved." -ForegroundColor Green

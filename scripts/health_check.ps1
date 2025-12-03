# Quick health check script for Windows PowerShell

Write-Host "Checking Auto-Remediation Platform Health..." -ForegroundColor Cyan
Write-Host ""

# Check if containers are running
Write-Host "=== Container Status ===" -ForegroundColor Yellow
docker ps --filter "name=ar_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

# Check app health
Write-Host "=== Application Health ===" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method Get
    $health | ConvertTo-Json -Depth 5
} catch {
    Write-Host "App not responding" -ForegroundColor Red
}
Write-Host ""

# Check database connection
Write-Host "=== Database Connection ===" -ForegroundColor Yellow
$dbCheck = docker exec ar_postgres pg_isready -U remediation_user 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Database is ready" -ForegroundColor Green
} else {
    Write-Host "Database not ready" -ForegroundColor Red
}
Write-Host ""

# Check recent incidents
Write-Host "=== Recent Incidents (last 5) ===" -ForegroundColor Yellow
try {
    $incidents = Invoke-RestMethod -Uri "http://localhost:5000/api/incidents?limit=5" -Method Get
    $incidents.incidents | Select-Object type, severity, status, timestamp | Format-Table
} catch {
    Write-Host "Cannot fetch incidents" -ForegroundColor Red
}
Write-Host ""

# Check remediation actions
Write-Host "=== Recent Remediation Actions (last 5) ===" -ForegroundColor Yellow
try {
    $actions = Invoke-RestMethod -Uri "http://localhost:5000/api/remediation/history?limit=5" -Method Get
    $actions.actions | Select-Object action_type, target, success, timestamp | Format-Table
} catch {
    Write-Host "Cannot fetch remediation history" -ForegroundColor Red
}
Write-Host ""

Write-Host "Health check complete!" -ForegroundColor Green

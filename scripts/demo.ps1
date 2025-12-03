# Demo script for Windows PowerShell
# Auto-Remediation Bot - Demo Scenarios

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Auto-Remediation Bot - Demo Scenarios" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$APP_URL = "http://localhost:5000"

function Wait-ForUser {
    Write-Host ""
    Write-Host "Press Enter to continue..." -ForegroundColor Yellow
    Read-Host
}

function Check-Health {
    Write-Host "Current health status:" -ForegroundColor Green
    try {
        $response = Invoke-RestMethod -Uri "$APP_URL/api/health" -Method Get
        $response | ConvertTo-Json -Depth 10
    } catch {
        Write-Host "Failed to get health status: $_" -ForegroundColor Red
    }
    Write-Host ""
}

# Scenario 1: Application crash
Write-Host "=== Scenario 1: Application Crash ===" -ForegroundColor Yellow
Write-Host "This will crash the main application container."
Write-Host "Watch the bot detect the failure and restart the container."
Wait-ForUser

Write-Host "Triggering crash..." -ForegroundColor Red
try {
    Invoke-RestMethod -Uri "$APP_URL/crash" -Method Post
} catch {
    # Expected to fail as app crashes
}
Write-Host ""
Write-Host "Application crashed! Watch bot logs for remediation..."
Write-Host ""
Write-Host "Run: docker logs -f ar_bot" -ForegroundColor Cyan
Wait-ForUser

# Scenario 2: CPU spike
Write-Host "=== Scenario 2: CPU Spike ===" -ForegroundColor Yellow
Write-Host "This will simulate a CPU spike for 15 seconds."
Write-Host "Watch the bot detect high CPU and start a replica."
Wait-ForUser

Check-Health

Write-Host "Triggering CPU spike (15 seconds)..." -ForegroundColor Red
try {
    Invoke-RestMethod -Uri "$APP_URL/spike/cpu?duration=15" -Method Post
    Write-Host ""
    Write-Host "CPU spike triggered! Monitor with: docker stats" -ForegroundColor Cyan
    Write-Host "Watch bot start replica container." -ForegroundColor Cyan
} catch {
    Write-Host "Failed to trigger CPU spike: $_" -ForegroundColor Red
}
Wait-ForUser

# Scenario 3: Error rate spike
Write-Host "=== Scenario 3: High Error Rate ===" -ForegroundColor Yellow
Write-Host "This will simulate increased error rate for 20 seconds."
Write-Host "Watch the bot detect high errors and take action."
Wait-ForUser

Check-Health

Write-Host "Triggering error spike (20 seconds)..." -ForegroundColor Red
try {
    Invoke-RestMethod -Uri "$APP_URL/spike/errors?duration=20" -Method Post
    Write-Host ""
    Write-Host "Error spike triggered! Sending requests to accumulate errors..." -ForegroundColor Cyan
    
    # Send some requests to trigger errors
    1..50 | ForEach-Object {
        Start-Job -ScriptBlock {
            param($url)
            try { Invoke-RestMethod -Uri $url -Method Get } catch {}
        } -ArgumentList $APP_URL
    } | Out-Null
    
    Get-Job | Wait-Job | Remove-Job
    
    Write-Host "Requests sent. Watch bot logs for remediation." -ForegroundColor Cyan
} catch {
    Write-Host "Failed to trigger error spike: $_" -ForegroundColor Red
}
Wait-ForUser

# Scenario 4: Manual health check
Write-Host "=== Scenario 4: Current System State ===" -ForegroundColor Yellow
Write-Host "Checking current health and incidents..."
Write-Host ""

Check-Health

Write-Host "Recent incidents:" -ForegroundColor Green
try {
    $incidents = Invoke-RestMethod -Uri "$APP_URL/api/incidents?limit=5" -Method Get
    $incidents.incidents | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Failed to get incidents: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "Remediation history:" -ForegroundColor Green
try {
    $history = Invoke-RestMethod -Uri "$APP_URL/api/remediation/history?limit=5" -Method Get
    $history.actions | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Failed to get remediation history: $_" -ForegroundColor Red
}
Write-Host ""

# Scenario 5: Container status
Write-Host "=== Scenario 5: Container Status ===" -ForegroundColor Yellow
Write-Host "Checking Docker container status..."
Write-Host ""

docker ps -a --filter "name=ar_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

Write-Host "Demo complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  - View bot logs:    docker logs -f ar_bot"
Write-Host "  - View app logs:    docker logs -f ar_app"
Write-Host "  - Check health:     Invoke-RestMethod http://localhost:5000/api/health"
Write-Host "  - View incidents:   Invoke-RestMethod http://localhost:5000/api/incidents"
Write-Host "  - Container stats:  docker stats"
Write-Host "  - Stop all:         docker compose down"
Write-Host ""

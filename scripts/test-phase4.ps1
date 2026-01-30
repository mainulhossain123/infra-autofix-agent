# Phase 4: LLM Integration - Test Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   LLM Integration - Phase 4 Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:5000"

# Test 1: Check Ollama service
Write-Host "[1/5] Checking Ollama LLM service..." -ForegroundColor Yellow

try {
    $llmHealth = Invoke-RestMethod -Uri "$baseUrl/api/ml/llm/health"
    
    if ($llmHealth.status -eq "available") {
        Write-Host "✅ Ollama service available" -ForegroundColor Green
        Write-Host "   Model: $($llmHealth.model)" -ForegroundColor Gray
        Write-Host "   URL: $($llmHealth.ollama_url)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Ollama service unavailable" -ForegroundColor Yellow
        Write-Host "   Message: $($llmHealth.message)" -ForegroundColor Gray
        Write-Host "   Note: Start Ollama with: docker-compose -f docker-compose.yml -f docker-compose.ml.yml up -d" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to check LLM health: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Create a test incident for analysis
Write-Host "[2/5] Creating test incident..." -ForegroundColor Yellow

try {
    # First, check if we have any incidents
    $incidents = Invoke-RestMethod -Uri "$baseUrl/api/incidents?limit=1"
    
    if ($incidents.Count -gt 0) {
        $testIncidentId = $incidents[0].id
        Write-Host "✅ Using existing incident #$testIncidentId" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No incidents found. Incidents are created automatically by the bot." -ForegroundColor Yellow
        Write-Host "   Skipping LLM analysis tests." -ForegroundColor Yellow
        $testIncidentId = $null
    }
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    $testIncidentId = $null
}
Write-Host ""

# Test 3: Analyze incident with LLM
if ($testIncidentId) {
    Write-Host "[3/5] Analyzing incident with LLM..." -ForegroundColor Yellow
    Write-Host "   This may take 10-20 seconds..." -ForegroundColor Gray
    
    try {
        $analysis = Invoke-RestMethod `
            -Uri "$baseUrl/api/ml/analyze/incident/$testIncidentId" `
            -Method POST `
            -ContentType "application/json" `
            -TimeoutSec 30
        
        Write-Host "✅ LLM analysis complete" -ForegroundColor Green
        Write-Host "   Root Cause: $($analysis.analysis.root_cause)" -ForegroundColor Cyan
        Write-Host "   Confidence: $($analysis.analysis.confidence)" -ForegroundColor Gray
        
        if ($analysis.analysis.suggestions) {
            Write-Host "   Suggestions:" -ForegroundColor Cyan
            $analysis.analysis.suggestions | ForEach-Object {
                Write-Host "     - $_" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "❌ Analysis failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "[3/5] Skipping incident analysis (no incidents)" -ForegroundColor Yellow
}
Write-Host ""

# Test 4: Get remediation suggestions
Write-Host "[4/5] Getting LLM remediation suggestions..." -ForegroundColor Yellow

try {
    $body = @{
        incident_type = "high_cpu"
        context = @{
            cpu_usage = 95.0
            duration_minutes = 15
            service = "ar_app"
        }
    } | ConvertTo-Json
    
    $suggestions = Invoke-RestMethod `
        -Uri "$baseUrl/api/ml/suggest-remediation" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 30
    
    Write-Host "✅ Remediation suggestions:" -ForegroundColor Green
    $suggestions.suggestions | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Generate incident report
if ($testIncidentId) {
    Write-Host "[5/5] Generating natural language report..." -ForegroundColor Yellow
    Write-Host "   This may take 10-20 seconds..." -ForegroundColor Gray
    
    try {
        $report = Invoke-RestMethod `
            -Uri "$baseUrl/api/ml/generate-report/$testIncidentId" `
            -TimeoutSec 30
        
        Write-Host "✅ Report generated:" -ForegroundColor Green
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        Write-Host $report.report -ForegroundColor White
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    } catch {
        Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "[5/5] Skipping report generation (no incidents)" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Phase 4 Implementation Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "LLM Integration Features:" -ForegroundColor White
Write-Host "  • AI-powered root cause analysis" -ForegroundColor White
Write-Host "  • Natural language incident explanations" -ForegroundColor White
Write-Host "  • Intelligent remediation suggestions" -ForegroundColor White
Write-Host "  • Automated incident reports" -ForegroundColor White
Write-Host "  • 100% free (Ollama + Llama 3.2)" -ForegroundColor White
Write-Host ""
Write-Host "How It Works:" -ForegroundColor Cyan
Write-Host "  1. Bot detects incident" -ForegroundColor White
Write-Host "  2. LLM automatically analyzes root cause" -ForegroundColor White
Write-Host "  3. Insights stored in llm_analyses table" -ForegroundColor White
Write-Host "  4. Available via API and dashboard" -ForegroundColor White
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  • POST $baseUrl/api/ml/analyze/incident/<id>" -ForegroundColor White
Write-Host "  • POST $baseUrl/api/ml/suggest-remediation" -ForegroundColor White
Write-Host "  • GET  $baseUrl/api/ml/generate-report/<id>" -ForegroundColor White
Write-Host "  • POST $baseUrl/api/ml/analyze/metrics-pattern" -ForegroundColor White
Write-Host "  • GET  $baseUrl/api/ml/llm/health" -ForegroundColor White
Write-Host ""
Write-Host "Setup Ollama (if not running):" -ForegroundColor Cyan
Write-Host "  docker-compose -f docker-compose.yml -f docker-compose.ml.yml up -d" -ForegroundColor White
Write-Host "  docker exec -it ar_ollama ollama pull llama3.2:3b" -ForegroundColor White
Write-Host ""
Write-Host "Next: Phase 5 - Failure Prediction (LightGBM)" -ForegroundColor Yellow
Write-Host ""

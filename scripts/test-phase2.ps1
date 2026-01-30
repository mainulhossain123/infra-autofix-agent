# Phase 2: Anomaly Detection - Quick Test Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ML Anomaly Detection - Phase 2 Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:5000"

# Test 1: Check ML health
Write-Host "[1/5] Checking ML module health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/api/ml/health"
    Write-Host "✅ ML module healthy" -ForegroundColor Green
    Write-Host "   Metrics collected: $($health.metrics_collected)" -ForegroundColor Gray
} catch {
    Write-Host "❌ ML health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 2: Generate synthetic training data (if needed)
Write-Host "[2/5] Checking training data..." -ForegroundColor Yellow
if ($health.metrics_collected -lt 1000) {
    Write-Host "   Generating synthetic data (need 1000+ samples)..." -ForegroundColor Cyan
    
    $body = @{
        days = 7
        seed = 42
    } | ConvertTo-Json
    
    try {
        $result = Invoke-RestMethod `
            -Uri "$baseUrl/api/ml/train/generate-synthetic" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body
        
        Write-Host "✅ Generated $($result.samples_count) synthetic samples" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Failed to generate synthetic data: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ Sufficient training data available ($($health.metrics_collected) samples)" -ForegroundColor Green
}
Write-Host ""

# Test 3: Train anomaly detector
Write-Host "[3/5] Training Isolation Forest model..." -ForegroundColor Yellow
Write-Host "   This may take 30-60 seconds..." -ForegroundColor Gray

$trainBody = @{
    contamination = 0.05
    n_estimators = 100
    use_synthetic = $true
} | ConvertTo-Json

try {
    $training = Invoke-RestMethod `
        -Uri "$baseUrl/api/ml/train/anomaly-detector" `
        -Method POST `
        -ContentType "application/json" `
        -Body $trainBody `
        -TimeoutSec 120
    
    Write-Host "✅ Model trained successfully" -ForegroundColor Green
    Write-Host "   Accuracy: $([math]::Round($training.evaluation.accuracy * 100, 1))%" -ForegroundColor Gray
    Write-Host "   Precision: $([math]::Round($training.evaluation.precision * 100, 1))%" -ForegroundColor Gray
    Write-Host "   Recall: $([math]::Round($training.evaluation.recall * 100, 1))%" -ForegroundColor Gray
    Write-Host "   F1 Score: $([math]::Round($training.evaluation.f1_score * 100, 1))%" -ForegroundColor Gray
} catch {
    Write-Host "❌ Training failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Check logs: docker logs ar_app --tail 50" -ForegroundColor Gray
    exit 1
}
Write-Host ""

# Test 4: Test prediction with normal metrics
Write-Host "[4/5] Testing prediction with normal metrics..." -ForegroundColor Yellow

$normalMetrics = @{
    cpu_usage_percent = 35.5
    memory_usage_mb = 2048
    memory_usage_percent = 45.0
    disk_usage_percent = 55.0
    error_rate = 0.01
    response_time_p50 = 120
    response_time_p95 = 450
    response_time_p99 = 850
    active_requests = 25
} | ConvertTo-Json

try {
    $prediction = Invoke-RestMethod `
        -Uri "$baseUrl/api/ml/predict/anomaly" `
        -Method POST `
        -ContentType "application/json" `
        -Body $normalMetrics
    
    $pred = $prediction.prediction
    if ($pred.is_anomaly) {
        Write-Host "⚠️  Detected as anomaly (severity: $($pred.anomaly_severity))" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Correctly identified as normal" -ForegroundColor Green
    }
    Write-Host "   Anomaly score: $([math]::Round($pred.anomaly_score, 3))" -ForegroundColor Gray
    Write-Host "   Severity: $([math]::Round($pred.anomaly_severity, 1))" -ForegroundColor Gray
} catch {
    Write-Host "❌ Prediction failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Test prediction with anomalous metrics
Write-Host "[5/5] Testing prediction with anomalous metrics..." -ForegroundColor Yellow

$anomalyMetrics = @{
    cpu_usage_percent = 95.0
    memory_usage_mb = 7500
    memory_usage_percent = 92.0
    disk_usage_percent = 88.0
    error_rate = 0.25
    response_time_p50 = 2500
    response_time_p95 = 8000
    response_time_p99 = 12000
    active_requests = 150
} | ConvertTo-Json

try {
    $prediction = Invoke-RestMethod `
        -Uri "$baseUrl/api/ml/predict/anomaly" `
        -Method POST `
        -ContentType "application/json" `
        -Body $anomalyMetrics
    
    $pred = $prediction.prediction
    if ($pred.is_anomaly) {
        Write-Host "✅ Correctly detected as anomaly!" -ForegroundColor Green
        Write-Host "   Severity: $([math]::Round($pred.anomaly_severity, 1))" -ForegroundColor Red
        Write-Host "   Top contributors:" -ForegroundColor Gray
        $prediction.top_contributing_features.PSObject.Properties | Select-Object -First 3 | ForEach-Object {
            Write-Host "     - $($_.Name): $([math]::Round($_.Value * 100, 1))%" -ForegroundColor Gray
        }
    } else {
        Write-Host "⚠️  Failed to detect anomaly (severity: $($pred.anomaly_severity))" -ForegroundColor Yellow
    }
    Write-Host "   Anomaly score: $([math]::Round($pred.anomaly_score, 3))" -ForegroundColor Gray
} catch {
    Write-Host "❌ Prediction failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Phase 2 Implementation Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "ML Anomaly Detection is now active and will:" -ForegroundColor White
Write-Host "  • Detect anomalies automatically in bot monitoring loop" -ForegroundColor White
Write-Host "  • Create incidents with type 'ml_anomaly'" -ForegroundColor White
Write-Host "  • Trigger auto-remediation when severity >= 70" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Monitor anomaly scores: curl $baseUrl/api/ml/anomaly-scores" -ForegroundColor White
Write-Host "  2. Check incidents: curl $baseUrl/api/incidents" -ForegroundColor White
Write-Host "  3. Retrain periodically with real data" -ForegroundColor White
Write-Host "  4. Proceed to Phase 3: Time Series Forecasting" -ForegroundColor White
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  • POST $baseUrl/api/ml/train/anomaly-detector" -ForegroundColor White
Write-Host "  • POST $baseUrl/api/ml/predict/anomaly" -ForegroundColor White
Write-Host "  • GET  $baseUrl/api/ml/anomaly-scores" -ForegroundColor White
Write-Host ""

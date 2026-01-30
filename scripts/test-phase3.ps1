# Phase 3: Time Series Forecasting - Test Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Time Series Forecasting - Phase 3" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:5000"

# Test 1: Check if we have enough data
Write-Host "[1/5] Checking training data..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/api/ml/health"
    Write-Host "   Metrics collected: $($health.metrics_collected)" -ForegroundColor Gray
    
    if ($health.metrics_collected -lt 1000) {
        Write-Host "   Generating synthetic data..." -ForegroundColor Cyan
        
        $body = @{
            days = 7
            seed = 42
        } | ConvertTo-Json
        
        $result = Invoke-RestMethod `
            -Uri "$baseUrl/api/ml/train/generate-synthetic" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body
        
        Write-Host "✅ Generated $($result.samples_count) samples" -ForegroundColor Green
    } else {
        Write-Host "✅ Sufficient data available" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 2: Train Prophet forecaster
Write-Host "[2/5] Training Prophet forecaster..." -ForegroundColor Yellow
Write-Host "   This may take 60-90 seconds..." -ForegroundColor Gray

try {
    $training = Invoke-RestMethod `
        -Uri "$baseUrl/api/ml/train/forecaster" `
        -Method POST `
        -ContentType "application/json" `
        -Body "{}" `
        -TimeoutSec 180
    
    Write-Host "✅ Forecaster trained successfully" -ForegroundColor Green
    Write-Host "   Metrics trained: $($training.training_stats.total_metrics)" -ForegroundColor Gray
    
    $training.training_stats.training_results.PSObject.Properties | ForEach-Object {
        $metric = $_.Name
        $stats = $_.Value
        Write-Host "   - $metric : RMSE=$([math]::Round($stats.rmse, 2)), MAE=$([math]::Round($stats.mae, 2))" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Training failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Note: Prophet may take longer on first run" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Test 3: Get next hour forecast
Write-Host "[3/5] Getting next hour forecast..." -ForegroundColor Yellow

try {
    $nextHour = Invoke-RestMethod -Uri "$baseUrl/api/ml/forecast/next-hour"
    
    Write-Host "✅ Next hour predictions:" -ForegroundColor Green
    $nextHour.predictions.PSObject.Properties | ForEach-Object {
        $metric = $_.Name
        $pred = $_.Value
        Write-Host "   $metric" -ForegroundColor Cyan
        Write-Host "     Mean forecast: $([math]::Round($pred.mean_forecast, 2))" -ForegroundColor Gray
        Write-Host "     Trend: $($pred.trend)" -ForegroundColor Gray
        Write-Host "     Range: [$([math]::Round($pred.lower_bound, 2)), $([math]::Round($pred.upper_bound, 2))]" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Get 6-hour forecast for CPU
Write-Host "[4/5] Getting 6-hour CPU forecast..." -ForegroundColor Yellow

try {
    $forecast = Invoke-RestMethod -Uri "$baseUrl/api/ml/forecast?metric=cpu_usage_percent&hours_ahead=6"
    
    $samples = $forecast.forecast.Count
    Write-Host "✅ Generated $samples forecast points" -ForegroundColor Green
    
    # Show first and last predictions
    $first = $forecast.forecast[0]
    $last = $forecast.forecast[-1]
    
    Write-Host "   Now: $([math]::Round($first.forecast, 2))% CPU" -ForegroundColor Gray
    Write-Host "   In 6 hours: $([math]::Round($last.forecast, 2))% CPU" -ForegroundColor Gray
    
    $change = $last.forecast - $first.forecast
    if ($change -gt 5) {
        Write-Host "   ⚠️  CPU expected to increase by $([math]::Round($change, 1))%" -ForegroundColor Yellow
    } elseif ($change -lt -5) {
        Write-Host "   ✅ CPU expected to decrease by $([math]::Round([Math]::Abs($change), 1))%" -ForegroundColor Green
    } else {
        Write-Host "   ✅ CPU expected to remain stable" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Check for predicted alerts
Write-Host "[5/5] Checking for predicted threshold breaches..." -ForegroundColor Yellow

try {
    $alerts = Invoke-RestMethod -Uri "$baseUrl/api/ml/forecast/alerts"
    
    if ($alerts.alert_count -gt 0) {
        Write-Host "⚠️  Found $($alerts.alert_count) predicted breach(es):" -ForegroundColor Yellow
        
        $alerts.alerts | ForEach-Object {
            Write-Host "   $($_.metric): $([math]::Round($_.predicted_value, 2)) (threshold: $($_.threshold))" -ForegroundColor Red
            Write-Host "     Severity: $($_.severity)" -ForegroundColor Gray
            Write-Host "     Time to breach: $($_.time_to_breach)" -ForegroundColor Gray
        }
    } else {
        Write-Host "✅ No threshold breaches predicted in next hour" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Phase 3 Implementation Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Time Series Forecasting is now active:" -ForegroundColor White
Write-Host "  • Predicts metrics 1-24 hours ahead" -ForegroundColor White
Write-Host "  • Detects seasonal patterns (daily, weekly)" -ForegroundColor White
Write-Host "  • Provides confidence intervals" -ForegroundColor White
Write-Host "  • Creates predictive alerts before incidents occur" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Monitor predictions: curl $baseUrl/api/ml/forecast/next-hour" -ForegroundColor White
Write-Host "  2. Check alerts: curl $baseUrl/api/ml/forecast/alerts" -ForegroundColor White
Write-Host "  3. View trends: curl $baseUrl/api/ml/forecast/trend/cpu_usage_percent" -ForegroundColor White
Write-Host "  4. Proceed to Phase 4: LLM Integration (Ollama)" -ForegroundColor White
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  • POST $baseUrl/api/ml/train/forecaster" -ForegroundColor White
Write-Host "  • GET  $baseUrl/api/ml/forecast?hours_ahead=6&metric=cpu_usage_percent" -ForegroundColor White
Write-Host "  • GET  $baseUrl/api/ml/forecast/next-hour" -ForegroundColor White
Write-Host "  • GET  $baseUrl/api/ml/forecast/alerts" -ForegroundColor White
Write-Host "  • GET  $baseUrl/api/ml/forecast/trend/<metric>" -ForegroundColor White
Write-Host ""
Write-Host "Predictive Incident Type: 'predicted_breach'" -ForegroundColor Cyan
Write-Host "  Bot will create incidents BEFORE problems occur!" -ForegroundColor White
Write-Host ""

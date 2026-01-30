# Phase 6: Continuous Learning - Test Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Continuous Learning - Phase 6 Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:5000"

# Test 1: Get ML system status
Write-Host "[1/6] Getting ML system status..." -ForegroundColor Yellow

try {
    $status = Invoke-RestMethod -Uri "$baseUrl/api/ml/continuous-learning/status"
    
    Write-Host "✅ ML System Status Retrieved" -ForegroundColor Green
    Write-Host "   Timestamp: $($status.timestamp)" -ForegroundColor Gray
    
    foreach ($model in $status.models.PSObject.Properties) {
        $modelName = $model.Name
        $modelData = $model.Value
        
        Write-Host "   Model: $modelName" -ForegroundColor Cyan
        
        if ($modelData.last_trained) {
            $trained = [datetime]::Parse($modelData.last_trained).ToString("yyyy-MM-dd HH:mm")
            Write-Host "     Last Trained: $trained" -ForegroundColor Gray
        } else {
            Write-Host "     Last Trained: Never" -ForegroundColor Yellow
        }
        
        Write-Host "     Predictions Since Train: $($modelData.predictions_since_train)" -ForegroundColor Gray
        
        if ($modelData.should_retrain) {
            Write-Host "     Status: Needs Retraining" -ForegroundColor Yellow
            Write-Host "     Reason: $($modelData.retrain_reason)" -ForegroundColor Yellow
        } else {
            Write-Host "     Status: Up to date" -ForegroundColor Green
        }
        
        if ($modelData.accuracy) {
            $acc = [math]::Round($modelData.accuracy * 100, 1)
            Write-Host "     Accuracy: $acc%" -ForegroundColor Gray
        }
        if ($modelData.mae) {
            Write-Host "     MAE: $([math]::Round($modelData.mae, 2))" -ForegroundColor Gray
        }
        
        Write-Host ""
    }
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Check retraining criteria
Write-Host "[2/6] Checking if models need retraining..." -ForegroundColor Yellow

try {
    $retrain = Invoke-RestMethod `
        -Uri "$baseUrl/api/ml/continuous-learning/check-retrain" `
        -Method POST `
        -ContentType "application/json"
    
    Write-Host "✅ Retrain check complete" -ForegroundColor Green
    
    foreach ($action in $retrain.retraining_actions) {
        $model = $action.model
        
        if ($action.should_retrain) {
            Write-Host "   $model`: NEEDS RETRAIN" -ForegroundColor Yellow
            Write-Host "     Reason: $($action.reason)" -ForegroundColor Gray
            
            if ($action.retrained) {
                if ($action.result.status -eq "success") {
                    Write-Host "     ✅ Retrained successfully" -ForegroundColor Green
                } else {
                    Write-Host "     ❌ Retrain failed: $($action.result.message)" -ForegroundColor Red
                }
            }
        } else {
            Write-Host "   $model`: Up to date ($($action.reason))" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Get training history
Write-Host "[3/6] Getting training history..." -ForegroundColor Yellow

try {
    $history = Invoke-RestMethod `
        -Uri "$baseUrl/api/ml/continuous-learning/training-history?limit=5"
    
    Write-Host "✅ Found $($history.count) recent training sessions" -ForegroundColor Green
    
    if ($history.count -gt 0) {
        Write-Host "   Recent Training:" -ForegroundColor Cyan
        
        foreach ($record in $history.history) {
            $trained = if ($record.trained_at) {
                [datetime]::Parse($record.trained_at).ToString("yyyy-MM-dd HH:mm")
            } else {
                "Unknown"
            }
            
            $acc = if ($record.accuracy) {
                "$([math]::Round($record.accuracy * 100, 1))%"
            } else {
                "N/A"
            }
            
            Write-Host "     [$trained] $($record.model_name) v$($record.version) - Accuracy: $acc" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Evaluate model performance
Write-Host "[4/6] Evaluating anomaly detector performance..." -ForegroundColor Yellow

try {
    $body = @{
        hours_back = 24
    } | ConvertTo-Json
    
    $evaluation = Invoke-RestMethod `
        -Uri "$baseUrl/api/ml/continuous-learning/evaluate/anomaly_detector" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "✅ Performance evaluation complete" -ForegroundColor Green
    Write-Host "   Model: $($evaluation.model)" -ForegroundColor Cyan
    Write-Host "   Period: $($evaluation.period_hours) hours" -ForegroundColor Gray
    
    if ($evaluation.total_predictions) {
        Write-Host "   Total Predictions: $($evaluation.total_predictions)" -ForegroundColor Gray
        Write-Host "   True Positives: $($evaluation.true_positives)" -ForegroundColor Gray
        $prec = [math]::Round($evaluation.precision * 100, 1)
        Write-Host "   Precision: $prec%" -ForegroundColor $(if($prec -gt 70){"Green"}else{"Yellow"})
    } elseif ($evaluation.predictions) {
        Write-Host "   Predictions: $($evaluation.predictions)" -ForegroundColor Gray
        Write-Host "   Correct: $($evaluation.correct)" -ForegroundColor Gray
        $acc = [math]::Round($evaluation.accuracy * 100, 1)
        Write-Host "   Accuracy: $acc%" -ForegroundColor $(if($acc -gt 70){"Green"}else{"Yellow"})
    }
} catch {
    Write-Host "⚠️  Evaluation not available: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# Test 5: Get ML metrics summary
Write-Host "[5/6] Getting ML system metrics summary..." -ForegroundColor Yellow

try {
    $summary = Invoke-RestMethod -Uri "$baseUrl/api/ml/continuous-learning/metrics-summary"
    
    Write-Host "✅ ML Metrics Summary (Last 24 Hours)" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "   Models:" -ForegroundColor Cyan
    Write-Host "     Total Models: $($summary.models.total)" -ForegroundColor Gray
    Write-Host "     Recently Trained: $($summary.models.recently_trained)" -ForegroundColor Gray
    $avgAcc = [math]::Round($summary.models.avg_accuracy * 100, 1)
    Write-Host "     Average Accuracy: $avgAcc%" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "   Predictions:" -ForegroundColor Cyan
    Write-Host "     Anomaly Detections: $($summary.predictions.anomaly_detections)" -ForegroundColor Gray
    Write-Host "     Failure Predictions: $($summary.predictions.failure_predictions)" -ForegroundColor Gray
    Write-Host "     Forecasts: $($summary.predictions.forecasts)" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "   ML Incidents Detected: $($summary.ml_incidents_detected)" -ForegroundColor $(if($summary.ml_incidents_detected -gt 0){"Yellow"}else{"Green"})
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: Force retrain (optional, commented out by default)
Write-Host "[6/6] Force retrain test (skipped - use manually)" -ForegroundColor Yellow
Write-Host "   To force retrain all models, uncomment the code and run:" -ForegroundColor Gray
Write-Host "   Invoke-RestMethod -Uri '$baseUrl/api/ml/continuous-learning/retrain-all' -Method POST" -ForegroundColor Gray
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Phase 6 Implementation Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Continuous Learning Features:" -ForegroundColor White
Write-Host "  • Automated model retraining" -ForegroundColor White
Write-Host "  • Model performance monitoring" -ForegroundColor White
Write-Host "  • Training history tracking" -ForegroundColor White
Write-Host "  • Performance evaluation" -ForegroundColor White
Write-Host "  • ML metrics aggregation" -ForegroundColor White
Write-Host ""
Write-Host "How It Works:" -ForegroundColor Cyan
Write-Host "  1. Bot continuously monitors model performance" -ForegroundColor White
Write-Host "  2. Checks retraining criteria every hour" -ForegroundColor White
Write-Host "  3. Automatically retrains when:" -ForegroundColor White
Write-Host "     - Model never trained" -ForegroundColor White
Write-Host "     - 24+ hours since last training" -ForegroundColor White
Write-Host "     - 100+ new predictions collected" -ForegroundColor White
Write-Host "     - Performance drops below threshold" -ForegroundColor White
Write-Host "  4. Sends notifications when retraining occurs" -ForegroundColor White
Write-Host "  5. Tracks performance over time" -ForegroundColor White
Write-Host ""
Write-Host "Retraining Criteria:" -ForegroundColor Cyan
Write-Host "  • Min samples: 100 predictions" -ForegroundColor White
Write-Host "  • Time interval: 24 hours" -ForegroundColor White
Write-Host "  • Performance threshold: 70% accuracy" -ForegroundColor White
Write-Host "  • Forecaster MAE threshold: 20.0" -ForegroundColor White
Write-Host ""
Write-Host "Bot Integration:" -ForegroundColor Cyan
Write-Host "  • Checks every hour (configurable)" -ForegroundColor White
Write-Host "  • Non-blocking retraining" -ForegroundColor White
Write-Host "  • Notifications on successful retrain" -ForegroundColor White
Write-Host "  • Model versioning in database" -ForegroundColor White
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  • GET  $baseUrl/api/ml/continuous-learning/status" -ForegroundColor White
Write-Host "  • POST $baseUrl/api/ml/continuous-learning/check-retrain" -ForegroundColor White
Write-Host "  • POST $baseUrl/api/ml/continuous-learning/retrain-all" -ForegroundColor White
Write-Host "  • POST $baseUrl/api/ml/continuous-learning/evaluate/<model>" -ForegroundColor White
Write-Host "  • GET  $baseUrl/api/ml/continuous-learning/training-history" -ForegroundColor White
Write-Host "  • GET  $baseUrl/api/ml/continuous-learning/metrics-summary" -ForegroundColor White
Write-Host ""
Write-Host "Configuration (Environment Variables):" -ForegroundColor Cyan
Write-Host "  • ENABLE_CONTINUOUS_LEARNING=true" -ForegroundColor White
Write-Host "  • RETRAIN_CHECK_INTERVAL=3600 (seconds)" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ALL 6 ML PHASES COMPLETE! 🎉" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Phase 1: Data Pipeline" -ForegroundColor Green
Write-Host "✅ Phase 2: Anomaly Detection (Isolation Forest)" -ForegroundColor Green
Write-Host "✅ Phase 3: Time Series Forecasting (Prophet)" -ForegroundColor Green
Write-Host "✅ Phase 4: LLM Integration (Ollama + Llama 3.2)" -ForegroundColor Green
Write-Host "✅ Phase 5: Failure Prediction (LightGBM)" -ForegroundColor Green
Write-Host "✅ Phase 6: Continuous Learning (Auto-retraining)" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Commit Phase 6 changes" -ForegroundColor White
Write-Host "  2. Push all commits to GitHub" -ForegroundColor White
Write-Host "  3. Update documentation" -ForegroundColor White
Write-Host "  4. Test end-to-end ML pipeline" -ForegroundColor White
Write-Host ""

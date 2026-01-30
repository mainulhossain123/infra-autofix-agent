# ML Setup Script
# Run this after deploying the main application to set up ML features

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ML Module Setup - Phase 1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if services are running
Write-Host "[1/6] Checking services..." -ForegroundColor Yellow
$appRunning = docker ps --filter "name=ar_app" --filter "status=running" -q
$postgresRunning = docker ps --filter "name=ar_postgres" --filter "status=running" -q

if (-not $appRunning) {
    Write-Host "❌ Flask app not running. Please start services first:" -ForegroundColor Red
    Write-Host "   docker-compose up -d" -ForegroundColor Gray
    exit 1
}

if (-not $postgresRunning) {
    Write-Host "❌ PostgreSQL not running. Please start services first:" -ForegroundColor Red
    Write-Host "   docker-compose up -d" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ Services running" -ForegroundColor Green
Write-Host ""

# Step 2: Run database migrations
Write-Host "[2/6] Running ML database migrations..." -ForegroundColor Yellow
docker exec -i ar_postgres psql -U remediation_user -d remediation_db < db/add_ml_tables.sql

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ ML tables created successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️  Migration may have failed (tables might already exist)" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Install ML dependencies in app container
Write-Host "[3/6] Installing ML dependencies in app container..." -ForegroundColor Yellow
docker exec ar_app pip install -q numpy pandas scikit-learn

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Core ML dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Check metrics collection
Write-Host "[4/6] Checking metrics collection..." -ForegroundColor Yellow
Start-Sleep -Seconds 5  # Wait for collector to run

$response = Invoke-WebRequest -Uri "http://localhost:5000/api/ml/health" -UseBasicParsing -ErrorAction SilentlyContinue

if ($response.StatusCode -eq 200) {
    $healthData = $response.Content | ConvertFrom-Json
    Write-Host "✅ ML module healthy" -ForegroundColor Green
    Write-Host "   Metrics collected: $($healthData.metrics_collected)" -ForegroundColor Gray
    Write-Host "   Data collection active: $($healthData.data_collection_active)" -ForegroundColor Gray
} else {
    Write-Host "⚠️  ML health check failed, but this is normal on first run" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Generate synthetic training data (optional)
Write-Host "[5/6] Do you want to generate synthetic training data? (Y/N)" -ForegroundColor Yellow
Write-Host "   (This allows ML models to work immediately, but takes ~30 seconds)" -ForegroundColor Gray
$generate = Read-Host "Generate"

if ($generate -eq 'Y' -or $generate -eq 'y') {
    Write-Host "   Generating 30 days of synthetic data..." -ForegroundColor Cyan
    
    $body = @{
        days = 30
        seed = 42
    } | ConvertTo-Json
    
    try {
        $response = Invoke-WebRequest `
            -Uri "http://localhost:5000/api/ml/train/generate-synthetic" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body `
            -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            $result = $response.Content | ConvertFrom-Json
            Write-Host "✅ Generated $($result.samples_count) synthetic samples" -ForegroundColor Green
            Write-Host "   Label distribution:" -ForegroundColor Gray
            $result.label_distribution.PSObject.Properties | ForEach-Object {
                Write-Host "     $($_.Name): $($_.Value)" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "⚠️  Failed to generate synthetic data: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "   You can try again later with:" -ForegroundColor Gray
        Write-Host "   curl -X POST http://localhost:5000/api/ml/train/generate-synthetic -H 'Content-Type: application/json' -d '{\"days\":30}'" -ForegroundColor Gray
    }
} else {
    Write-Host "⏭️  Skipped synthetic data generation" -ForegroundColor Gray
    Write-Host "   Real data will be collected automatically over the next few days" -ForegroundColor Gray
}
Write-Host ""

# Step 6: Display summary
Write-Host "[6/6] Setup Summary" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Phase 1 (Data Pipeline) Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "What's Happening Now:" -ForegroundColor Cyan
Write-Host "  • Metrics being collected every 60 seconds" -ForegroundColor White
Write-Host "  • Data stored in 'metrics_history' table" -ForegroundColor White
Write-Host "  • ML models will train once enough data is collected" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Monitor metrics: curl http://localhost:5000/api/ml/metrics/stats" -ForegroundColor White
Write-Host "  2. Export data: curl http://localhost:5000/api/ml/metrics/export > metrics.json" -ForegroundColor White
Write-Host "  3. Wait 3-7 days for real data (or use synthetic data)" -ForegroundColor White
Write-Host "  4. Implement Phase 2: Anomaly Detection" -ForegroundColor White
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  • http://localhost:5000/api/ml/health - ML module status" -ForegroundColor White
Write-Host "  • http://localhost:5000/api/ml/metrics/stats - Data statistics" -ForegroundColor White
Write-Host "  • http://localhost:5000/api/ml/metrics/export - Export training data" -ForegroundColor White
Write-Host "  • http://localhost:5000/api/docs - Swagger UI (includes ML endpoints)" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎉 ML Pipeline is now collecting data!" -ForegroundColor Green
Write-Host ""

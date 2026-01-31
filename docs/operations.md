# Operations & Configuration Guide

> **Quick Links**: [Kubernetes Ops](kubernetes.md#monitoring--troubleshooting) | [ML Setup](ml-setup.md) | [API Docs](http://localhost:5000/api/docs)

## 🔗 Service URLs

### Docker Compose (Development)
```
Main Dashboard:        http://localhost:3000
Swagger API Docs:      http://localhost:5000/api/docs  ⭐
REST API:              http://localhost:5000
Health Check:          http://localhost:5000/health
WebSocket:             ws://localhost:5000/ws
Grafana:               http://localhost:3001 (admin/admin)
Prometheus:            http://localhost:9090
Loki:                  http://localhost:3100
Ollama LLM:            http://localhost:11434
```

### Kubernetes (Production)
```
Main Dashboard:        http://localhost (LoadBalancer)
Swagger API Docs:      http://localhost:5000/api/docs  ⭐
REST API:              http://localhost:5000
Health Check:          http://localhost:5000/health
Grafana:               http://localhost:3000 (admin/admin)
Prometheus:            http://localhost:9090
```

### ML/AI API Endpoints
```
ML System Status:      GET  /api/ml/continuous-learning/status
LLM Health:            GET  /api/ml/llm/health
Anomaly Detection:     POST /api/ml/anomaly/predict
Time Series Forecast:  POST /api/ml/forecast/predict
Failure Prediction:    POST /api/ml/failure-prediction/predict
Incident Analysis:     POST /api/ml/analyze/incident/<id>
Model Retraining:      POST /api/ml/continuous-learning/check-retrain
```

## 🚀 Quick Health Verification

### Docker Compose
```powershell
# Check all services
docker compose ps

# Test core endpoints
curl http://localhost:5000/health
curl http://localhost:3000
curl http://localhost:3001/api/health

# Test ML services (if enabled)
curl http://localhost:5000/api/ml/llm/health
curl http://localhost:5000/api/ml/continuous-learning/status
```

### Kubernetes
```powershell
# Check all pods
kubectl get pods -n infra-autofix

# Verify LoadBalancer services
kubectl get svc -n infra-autofix

# Test endpoints
curl http://localhost/
curl http://localhost:5000/health

# Watch pods in real-time
kubectl get pods -n infra-autofix --watch
```

## ⚙️ Configuration Management

### Environment Variables

**Core Settings (`.env` file):**
```bash
# Application
FLASK_ENV=production
FLASK_DEBUG=false
LOG_LEVEL=INFO

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=remediation_db
POSTGRES_USER=remediation_user
POSTGRES_PASSWORD=remediation_pass

# Monitoring
POLL_INTERVAL=60              # Bot check interval (seconds)
DATA_RETENTION_DAYS=180       # Database cleanup (days)
CLEANUP_INTERVAL_HOURS=24     # Cleanup frequency

# Circuit Breaker
MAX_RESTARTS_PER_5MIN=3       # Max remediation actions
COOLDOWN_SECONDS=300          # Cooldown period

# ML/AI Features
ENABLE_FAILURE_PREDICTION=true
FAILURE_CHECK_INTERVAL=300    # Check every 5 minutes
ENABLE_CONTINUOUS_LEARNING=true
RETRAIN_CHECK_INTERVAL=3600   # Check hourly
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2:3b
```

### Dynamic Configuration via API

Update thresholds without redeploying:

```bash
# Get current config
curl http://localhost:5000/api/config

# Update threshold
curl -X PUT http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "key": "error_rate_threshold",
    "value": 0.10
  }'

# Available config keys:
# - cpu_threshold (0-100)
# - memory_threshold (0-100)
# - error_rate_threshold (0-1)
# - latency_threshold_ms (milliseconds)
```

### ML Model Configuration

Check and manage ML models:

```bash
# Check ML system status
curl http://localhost:5000/api/ml/continuous-learning/status

# View model performance
curl http://localhost:5000/api/ml/continuous-learning/metrics-summary

# Force model retraining (careful - takes time!)
curl -X POST http://localhost:5000/api/ml/continuous-learning/retrain-all

# Check specific model
curl http://localhost:5000/api/ml/failure-prediction/model-info
```

## 🔧 Common Operations

### Start/Stop Services

**Docker Compose:**
```powershell
# Start all services
docker compose up -d

# Start with ML features
docker compose -f docker-compose.yml -f docker-compose.ml.yml up -d

# Stop all services
docker compose down

# Restart specific service
docker compose restart ar_bot

# View logs
docker compose logs -f ar_bot
docker compose logs --tail=100 ar_app
```

**Kubernetes:**
```powershell
# Scale deployment
kubectl scale deployment ar-app --replicas=3 -n infra-autofix

# Restart deployment
kubectl rollout restart deployment ar-app -n infra-autofix

# View logs
kubectl logs -f deployment/ar-app -n infra-autofix
kubectl logs --tail=100 deployment/ar-bot -n infra-autofix

# Delete everything
kubectl delete namespace infra-autofix
```

### Database Operations

```powershell
# Connect to PostgreSQL
docker exec -it ar_postgres psql -U remediation_user -d remediation_db

# Run SQL query
docker exec -it ar_postgres psql -U remediation_user -d remediation_db \
  -c "SELECT COUNT(*) FROM incidents WHERE created_at > NOW() - INTERVAL '24 hours';"

# Backup database
docker exec ar_postgres pg_dump -U remediation_user remediation_db > backup.sql

# Restore database
docker exec -i ar_postgres psql -U remediation_user remediation_db < backup.sql
```

### ML Model Management

```powershell
# Download LLM model (one-time)
docker exec -it ar_ollama ollama pull llama3.2:3b

# List available models
docker exec -it ar_ollama ollama list

# Check model size
docker exec -it ar_ollama ollama show llama3.2:3b

# Test LLM directly
docker exec -it ar_ollama ollama run llama3.2:3b "Hello, test message"

# Run ML test scripts
.\scripts\test-phase4.ps1   # LLM Integration
.\scripts\test-phase5.ps1   # Failure Prediction
.\scripts\test-phase6.ps1   # Continuous Learning
```

## 🐛 Troubleshooting

### Common Issues

**Port Conflicts:**
```powershell
# Check what's using port 3000
netstat -ano | findstr :3000

# Kill process (Windows)
taskkill /PID <pid> /F

# Or use different ports in docker-compose.yml
```

**Database Connection Issues:**
```powershell
# Wait for PostgreSQL to be ready (usually 10-20s on first start)
docker compose logs postgres

# Check if database is accessible
docker exec ar_postgres pg_isready -U remediation_user

# Restart database
docker compose restart postgres
```

**ML Services Not Working:**
```powershell
# Check if Ollama is running
docker ps | findstr ollama

# Check Ollama logs
docker logs ar_ollama

# Verify LLM model is downloaded
docker exec -it ar_ollama ollama list

# Download model if missing
docker exec -it ar_ollama ollama pull llama3.2:3b

# Test ML health endpoint
curl http://localhost:5000/api/ml/llm/health
curl http://localhost:5000/api/ml/continuous-learning/status
```

**Frontend Not Loading:**
```powershell
# Check if frontend is running
docker compose logs ar_frontend

# Rebuild frontend
docker compose build ar_frontend
docker compose up -d ar_frontend

# Clear browser cache or try incognito
```

**High Memory Usage:**
```powershell
# Check container resource usage
docker stats

# Restart memory-heavy services
docker compose restart ar_ollama  # LLM service uses ~4GB
docker compose restart ar_bot

# Reduce Ollama memory limit in docker-compose.ml.yml
```

### Debug Commands

```powershell
# View all container logs
docker compose logs --tail=50

# Follow specific service logs
docker compose logs -f ar_app
docker compose logs -f ar_bot

# Check container health
docker compose ps
docker inspect ar_app | findstr Health

# Exec into container
docker exec -it ar_app /bin/bash
docker exec -it ar_bot /bin/sh

# Check environment variables
docker exec ar_app env
docker exec ar_bot env | findstr ML
```

### Performance Issues

```powershell
# Check system resources
docker stats

# Scale down ML features if needed
docker compose -f docker-compose.yml up -d  # Without ML services

# Check database size
docker exec -it ar_postgres psql -U remediation_user -d remediation_db \
  -c "SELECT pg_size_pretty(pg_database_size('remediation_db'));"

# Clean up old data
curl -X POST http://localhost:5000/api/cleanup/run-now
```

### Getting Help

- **Documentation**: Check all guides in [docs/](.) folder
- **API Reference**: http://localhost:5000/api/docs (interactive Swagger UI)
- **Logs**: Always check logs first: `docker compose logs --tail=100`
- **GitHub Issues**: https://github.com/mainulhossain123/infra-autofix-agent/issues
- **Health Checks**: `/health` and `/api/ml/*/health` endpoints

### Quick Fixes

```powershell
# Nuclear option - restart everything
docker compose down
docker compose -f docker-compose.yml -f docker-compose.ml.yml up -d

# Clean rebuild (removes volumes!)
docker compose down -v
docker compose build --no-cache
docker compose up -d

# Check if ML database tables exist
docker exec -it ar_postgres psql -U remediation_user -d remediation_db \
  -c "\dt"  # Should show ml_models, anomaly_scores, etc.
```

---

**Related Documentation:**
- [Quick Start Guide](quick-start.md) - Initial setup
- [ML Setup Guide](ml-setup.md) - Detailed ML configuration
- [Kubernetes Guide](kubernetes.md) - K8s operations
- [Observability](observability.md) - Monitoring and metrics
- [API Reference](API.md) - Endpoint documentation

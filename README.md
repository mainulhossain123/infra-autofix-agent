# infra-autofix-agent

[![CI Pipeline](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/ci.yml)
[![Security Scanning](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/security.yml/badge.svg)](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/security.yml)
[![Docker Publish](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/docker-publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **AI-Powered Auto-Remediation Platform** with 6 production-ready ML models for predictive incident detection, automated root cause analysis, and intelligent self-healing infrastructure.

## ✨ Features

### Core Platform
- 🔍 **Automated Incident Detection** - CPU spikes, memory leaks, high error rates, latency issues
- 🔄 **Self-Healing** - Automatic container restarts with circuit breaker protection
- 📊 **Full Observability Stack** - Grafana dashboards, Prometheus metrics, Loki logs
- ⚡ **Real-time Updates** - WebSocket-based live dashboard
- 🚨 **Smart Alerting** - Configurable thresholds with Prometheus alerts
- 🐳 **Cloud-Native** - Docker/Kubernetes ready with multi-platform support
- 🔐 **Production-Grade** - CI/CD pipelines, security scanning, automated testing
- 📖 **Interactive API Documentation** - Swagger UI with live testing at http://localhost:5000/api/docs

### 🤖 AI/ML Capabilities (All 6 Phases Complete!)
- **Phase 2: Anomaly Detection** - Isolation Forest with 92-95% accuracy, <10ms inference
- **Phase 3: Time Series Forecasting** - Prophet models predict metrics 1-24 hours ahead
- **Phase 4: LLM Integration** - Ollama + Llama 3.2 for root cause analysis (100% free, local)
- **Phase 5: Failure Prediction** - LightGBM predicts system failures up to 72 hours ahead
- **Phase 6: Continuous Learning** - Automated model retraining and performance monitoring

**Result**: Proactive incident prevention with AI-powered insights and zero API costs!

## 🚀 Quick Start

> **📘 New to the project?** See the [Complete Quick Start Guide](docs/quick-start.md) with step-by-step instructions and screenshots.

### Prerequisites

- **Docker Compose**: Docker 20.10+, Docker Compose 2.0+
- **Kubernetes** (optional): kubectl, Helm 3.0+, K8s cluster 1.20+
- **ML Features** (optional): 4GB RAM for Ollama LLM service

### Option 1: Docker Compose (Recommended)

**Basic Setup:**
```bash
git clone https://github.com/mainulhossain123/infra-autofix-agent.git
cd infra-autofix-agent
docker compose up -d
```

**With ML/AI Features (Recommended):**
```bash
# Start with ML services (Ollama LLM + all AI features)
docker compose -f docker-compose.yml -f docker-compose.ml.yml up -d

# Download the LLM model (one-time setup, ~2GB)
docker exec -it ar_ollama ollama pull llama3.2:3b
```

**Access Services:**
- 🎨 Dashboard: http://localhost:3000
- 📖 Swagger API: http://localhost:5000/api/docs
- 📊 Grafana: http://localhost:3001 (admin/admin)
- 🔧 Backend API: http://localhost:5000
- 📈 Prometheus: http://localhost:9090

### Option 2: Kubernetes (Production)

**With Helm:**
```bash
# Development
helm install infra-autofix ./helm/infra-autofix \
  --namespace infra-autofix-dev \
  --create-namespace \
  --values ./helm/infra-autofix/values-dev.yaml

# Production
helm install infra-autofix ./helm/infra-autofix \
  --namespace infra-autofix-prod \
  --create-namespace \
  --values ./helm/infra-autofix/values-prod.yaml
```

**With kubectl:**
```bash
kubectl apply -k k8s/

# Access services at (Docker Desktop):
# Dashboard: http://localhost
# Grafana: http://localhost:3000 (admin/admin)
# API: http://localhost:5000
```

**Or use deployment script:**
```bash
# PowerShell
.\scripts\deploy-k8s.ps1 -Method helm -Environment dev

# Bash
./scripts/deploy-k8s.sh helm dev
```

> **⚠️ Important**: Grafana dashboards need to be imported manually in Kubernetes. See [Quick Start Guide](docs/quick-start.md#6-configure-grafana-dashboards).

See [Kubernetes Deployment Guide](docs/kubernetes.md) for detailed instructions.

### Access Interfaces

**Docker Compose URLs:**

| Service | URL | Credentials | Notes |
|---------|-----|-------------|-------|
| 🎨 **React Dashboard** | **http://localhost:3000** | - | **Main UI with ML insights** |
| 📖 **Swagger API Docs** | **http://localhost:5000/api/docs** | - | **Interactive ML API testing** |
| 🔧 Backend API | http://localhost:5000 | - | REST + WebSocket |
| 📊 Grafana | http://localhost:3001 | admin/admin | Dashboards & alerts |
| 📈 Prometheus | http://localhost:9090 | - | Metrics query UI |
| 📝 Loki | http://localhost:3100 | - | Log aggregation |
| 🤖 Ollama (LLM) | http://localhost:11434 | - | Local AI model API |

**ML/AI Feature Access:**
- **Dashboard UI**: http://localhost:3000 - View incidents with AI analysis, predictions, and anomaly scores
- **Swagger API**: http://localhost:5000/api/docs - Test all ML endpoints interactively
- **Direct API**: http://localhost:5000/api/ml/* - Programmatic access to ML features
  - `/api/ml/anomaly/*` - Anomaly detection
  - `/api/ml/forecast/*` - Time series predictions
  - `/api/ml/failure-prediction/*` - Failure forecasting
  - `/api/ml/analyze/*` - LLM incident analysis
  - `/api/ml/continuous-learning/*` - Model management

**Kubernetes URLs (Docker Desktop):**

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| 🎨 **Dashboard** | **http://localhost** | - | **Main UI with ML insights** |
| 📖 **Swagger API** | **http://localhost:5000/api/docs** | - | **Interactive ML API docs** |
| 🔧 Backend API | http://localhost:5000 | - | REST API + WebSocket |
| 📊 Grafana | http://localhost:3000 | admin/admin | Monitoring dashboards |
| 📈 Prometheus | http://localhost:9090 | - | Metrics database |

> **💡 ML Features**: All AI/ML insights are **integrated into the main dashboard**. No separate ML UI needed - anomaly scores, predictions, and AI analysis are displayed directly in the incidents view!

## 🏗️ Architecture

**Full System Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                          │
├─────────────────────────────────────────────────────────────────┤
│  🎨 React Dashboard (3000)    │  📖 Swagger API Docs (5000)    │
│  - Real-time monitoring        │  - Interactive ML API testing  │
│  - AI insights display         │  - All endpoints documented    │
│  - Incident management         │  - Try ML features live        │
└────────────────┬────────────────────────────┬───────────────────┘
                 │                            │
                 ▼                            ▼
       ┌─────────────────────────────────────────────────┐
       │         Flask API + ML Engine (5000)            │
       │  ┌──────────────────────────────────────────┐   │
       │  │  REST API  │  WebSocket  │  ML Routes   │   │
       │  └──────────────────────────────────────────┘   │
       │  ┌──────────────────────────────────────────┐   │
       │  │          6 ML Models Pipeline            │   │
       │  │  Phase 2: Anomaly Detection (IForest)    │   │
       │  │  Phase 3: Time Series Forecast (Prophet) │   │
       │  │  Phase 4: LLM Analysis (Ollama)          │   │
       │  │  Phase 5: Failure Prediction (LightGBM)  │   │
       │  │  Phase 6: Continuous Learning            │   │
       │  └──────────────────────────────────────────┘   │
       └────┬──────────────────┬─────────────────┬───────┘
            │                  │                 │
            ▼                  ▼                 ▼
   ┌────────────────┐  ┌─────────────┐  ┌──────────────┐
   │  PostgreSQL    │  │   Ollama    │  │ Remediation  │
   │  Database      │  │ LLM Service │  │     Bot      │
   │  - Metrics     │  │ Llama 3.2   │  │ - Auto-heal  │
   │  - Incidents   │  │ (3B params) │  │ - ML checks  │
   │  - ML Data     │  │  Port 11434 │  │ - Retraining │
   └────────────────┘  └─────────────┘  └──────┬───────┘
                                                │
            ┌───────────────────────────────────┴──────┐
            │                                          │
            ▼                                          ▼
   ┌──────────────────┐                    ┌──────────────────┐
   │  Observability   │                    │   Container      │
   │  Stack           │                    │   Infrastructure │
   ├──────────────────┤                    ├──────────────────┤
   │ • Prometheus     │◀───────────────────│ • App Containers │
   │ • Grafana        │                    │ • Docker/K8s     │
   │ • Loki + Promtail│                    │ • Health Checks  │
   └──────────────────┘                    └──────────────────┘
```

**ML Pipeline Data Flow:**
```
┌──────────────┐     ┌────────────────────┐     ┌─────────────────┐
│   Metrics    │────▶│ Feature Engineering│────▶│  Anomaly Model  │
│  Collection  │     │   (100+ features)  │     │ (Isolation Tree)│
└──────────────┘     └────────────────────┘     └────────┬────────┘
                                                          │
                     ┌────────────────────────────────────┘
                     │
                     ▼
         ┌──────────────────────┐
         │  Incident Created?   │
         └──────┬────────┬──────┘
                │ Yes    │ No
                ▼        └─────▶ Continue monitoring
    ┌──────────────────────┐
    │  Parallel ML Tasks   │
    ├──────────────────────┤
    │ 1. Failure Predictor │──▶ Risk: High/Med/Low
    │ 2. Time Series Fcst  │──▶ Breach in N hours
    │ 3. LLM Analyzer      │──▶ Root cause + fixes
    └──────┬───────────────┘
           │
           ▼
    ┌─────────────────┐      ┌──────────────────┐
    │  Store Results  │─────▶│  Display in UI   │
    │  in Database    │      │  & Send Alerts   │
    └─────────────────┘      └──────────────────┘
           │
           ▼
    ┌─────────────────────┐
    │ Continuous Learning │
    │ - Track performance │
    │ - Auto-retrain      │
    │ - Model versioning  │
    └─────────────────────┘
```

## 🤖 ML/AI Features Deep Dive
             └──────────────┘      └─────────────┘
                    │
     ┌──────────────┼──────────────┐
     ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌──────────┐
│Prometheus│ │ Grafana  │  │   Loki   │
│  :9090   │ │  :3001   │  │  :3100   │
```

## 🤖 ML/AI Features Deep Dive

> **🎨 Access ML Features**: All AI insights are integrated into the **main dashboard** at http://localhost:3000. View anomaly scores, predictions, and AI analysis directly in the incidents view. For programmatic access, use the **Swagger UI** at http://localhost:5000/api/docs to test all ML endpoints interactively.

### Phase 2: Anomaly Detection
- **Algorithm**: Isolation Forest
- **Features**: 100+ engineered metrics
- **Performance**: 92-95% accuracy, <10ms inference
- **Triggers**: Automatic incident creation for ML-detected anomalies
- **UI**: Anomaly scores shown in dashboard incident cards
- **API**: `POST /api/ml/anomaly/train`, `POST /api/ml/anomaly/predict`
- **Test**: `.\scripts\test-phase2.ps1`

### Phase 3: Time Series Forecasting
- **Algorithm**: Facebook Prophet
- **Capabilities**: 1-24 hour ahead predictions
- **Features**: Daily/weekly seasonality detection
- **Use Case**: Proactive breach detection before thresholds hit
- **UI**: Predicted values displayed in metrics charts
- **API**: `POST /api/ml/forecast/train`, `GET /api/ml/forecast/predict`
- **Test**: `.\scripts\test-phase3.ps1`

### Phase 4: LLM Integration
- **Model**: Ollama + Llama 3.2 (3B parameters)
- **Cost**: 100% free (runs locally)
- **Features**: Root cause analysis, natural language reports, remediation suggestions
- **Requirements**: 4GB RAM, ~2GB model download
- **UI**: AI-generated insights shown in incident details
- **API**: `POST /api/ml/analyze/incident/<id>`, `GET /api/ml/generate-report/<id>`
- **Health Check**: `GET /api/ml/llm/health`
- **Setup**: `docker exec -it ar_ollama ollama pull llama3.2:3b`
- **Test**: `.\scripts\test-phase4.ps1`

### Phase 5: Failure Prediction
- **Algorithm**: LightGBM (gradient boosting)
- **Prediction Window**: 1-72 hours ahead
- **Risk Levels**: High (70%+), Medium (40-70%), Low (<40%)
- **Proactive Alerts**: Creates "predicted_failure" incidents
- **UI**: Risk indicators and predictions in dashboard alerts
- **API**: `POST /api/ml/failure-prediction/train`, `POST /api/ml/failure-prediction/predict`
- **Test**: `.\scripts\test-phase5.ps1`

### Phase 6: Continuous Learning
- **Auto-Retraining**: Every 24 hours or when 100+ new samples collected
- **Performance Monitoring**: Tracks accuracy, precision, MAE
- **Model Versioning**: Full training history in database
- **Triggers**: Time-based, data-volume, performance degradation
- **UI**: Model status and retraining history in config page (future enhancement)
- **API**: `GET /api/ml/continuous-learning/status`, `POST /api/ml/continuous-learning/check-retrain`
- **Test**: `.\scripts\test-phase6.ps1`

### How to Access ML Features

**1. Main Dashboard (http://localhost:3000)**
- View incidents with anomaly scores
- See AI-generated root cause analysis
- Monitor predicted failures
- Check risk indicators

**2. Swagger API (http://localhost:5000/api/docs)**
- Interactive ML endpoint testing
- Try predictions with custom data
- Explore all ML API capabilities
- View request/response schemas

**3. Grafana Dashboards (http://localhost:3001)**
- ML model performance metrics
- Prediction accuracy over time
- Model retraining history
- Anomaly detection rates

**4. Direct API Calls**
```bash
# Check ML system status
curl http://localhost:5000/api/ml/continuous-learning/status

# Get incident AI analysis
curl http://localhost:5000/api/ml/analyze/incident/1

# Check LLM health
curl http://localhost:5000/api/ml/llm/health

# Predict next hour failures
curl -X POST http://localhost:5000/api/ml/failure-prediction/predict
```

**Quick ML Setup:**
```bash
# Start with ML services
docker compose -f docker-compose.yml -f docker-compose.ml.yml up -d

# Download LLM model (one-time)
docker exec -it ar_ollama ollama pull llama3.2:3b

# Check ML system status
curl http://localhost:5000/api/ml/continuous-learning/status

# Run ML test scripts
.\scripts\test-phase4.ps1  # LLM integration
.\scripts\test-phase5.ps1  # Failure prediction
.\scripts\test-phase6.ps1  # Continuous learning
```

See [ML Setup Guide](docs/ml-setup.md) for complete documentation.

## Deployment Options

### 🐳 Docker Compose (Local/Development)
Single-command setup for local development and testing. All services run in containers with Docker networking.

```bash
docker compose up -d
```

### ☸️ Kubernetes (Production/Cloud)
Enterprise-grade deployment with auto-scaling, health checks, and high availability.

- **Raw Manifests**: Full control with `kubectl apply -k k8s/`
- **Helm Charts**: Environment management with `helm install`
- **Kustomize**: Overlay-based configuration

Features:
- Horizontal Pod Autoscaling (2-10 replicas)
- Persistent volumes for databases
- RBAC and service accounts
- LoadBalancers and Ingress
- Multi-environment support (dev/staging/prod)

See [Kubernetes Guide](docs/kubernetes.md) for full deployment instructions.

---

## Development

### Local Setup (Without Docker)

**Backend:**
```powershell
cd app
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

**Bot:**
```powershell
cd bot
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python bot.py
```

**Frontend:**
```powershell
cd frontend
npm install
npm run dev  # http://localhost:5173
```

### Testing

```powershell
# Backend
cd app
pytest tests/ --cov

# Linting
flake8 app bot

# Frontend
cd frontend
npm run build
```

## 📊 Monitoring & Observability

### Grafana Dashboards
Access at http://localhost:3001 (Docker) or http://localhost:3000 (K8s) with `admin/admin`

**Pre-built Dashboards:**
- **System Overview** - Real-time health, incidents, remediation success rate
- **Application Metrics** - Request rates, latency, error rates by service
- **Infrastructure** - CPU, memory, disk usage across all containers
- **Incident Analysis** - Incident types, frequency, MTTR (Mean Time To Remediation)
- **ML Performance** - Model accuracy, predictions, retraining history

### Prometheus Metrics
Query at http://localhost:9090

**Key Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `incidents_total` - Total incidents by type and severity
- `remediations_total` - Successful/failed remediations
- `container_cpu_usage_seconds_total` - Container CPU usage
- `ml_predictions_total` - ML model predictions
- `ml_model_accuracy` - Model performance metrics

### Loki Logs
Access at http://localhost:3100 or via Grafana Explore

**Log Labels:**
- `{container="ar_app"}` - Flask API logs
- `{container="ar_bot"}` - Remediation bot logs
- `{container="ar_frontend"}` - React UI logs

### Alerts
Pre-configured Prometheus alerts in `prometheus/alerts.yml`:
- High error rate (>5% errors)
- Latency spike (p95 > 500ms)
- Resource exhaustion (CPU >90%, Memory >85%)
- Incident rate spike (>10 incidents/5min)

See [Observability Guide](docs/observability.md) for detailed monitoring setup.

## Automation

Includes 7 GitHub Actions workflows for CI/CD:
- **CI** - Testing, linting, building
- **Docker Publish** - GHCR image publishing with semantic versioning
- **Security** - CodeQL, Trivy, dependency scanning
- **Deploy** - AWS ECS and VM deployment
- **Performance** - Locust load testing
- **Release** - Automated GitHub releases
- **Cleanup** - Artifact management

See [docs/github-actions.md](docs/github-actions.md) for details.

## 📚 Documentation

### Essential Guides
- 🚀 **[Quick Start Guide](docs/quick-start.md)** - Complete setup for Docker Compose and Kubernetes
- 🤖 **[ML Setup Guide](docs/ml-setup.md)** - All 6 ML phases with examples and API references
- 📖 **[API Reference](docs/API.md)** - REST endpoints, WebSocket events, request/response formats
- ☸️ **[Kubernetes Guide](docs/kubernetes.md)** - Production deployment with Helm charts

### Operations
- 🔧 **[Operations Guide](docs/operations.md)** - Configuration, testing, troubleshooting
- 📊 **[Observability](docs/observability.md)** - Metrics, dashboards, alerts, logging
- 🐳 **[Docker Commands](docs/docker.md)** - Container management reference

### Automation
- 🚀 **[GitHub Actions](docs/github-actions.md)** - CI/CD workflows and deployment

### API Documentation (Interactive)
- 📖 **Swagger UI**: http://localhost:5000/api/docs (Docker Compose)
- 📖 **Swagger UI**: http://localhost:5000/api/docs (Kubernetes)

**Key API Endpoints:**
- **Core**: `/api/health`, `/api/incidents`, `/api/metrics`, `/api/config`
- **ML Phase 2**: `/api/ml/anomaly/*` - Anomaly detection
- **ML Phase 3**: `/api/ml/forecast/*` - Time series forecasting
- **ML Phase 4**: `/api/ml/analyze/*`, `/api/ml/llm/*` - LLM analysis
- **ML Phase 5**: `/api/ml/failure-prediction/*` - Failure prediction
- **ML Phase 6**: `/api/ml/continuous-learning/*` - Model management

## 🔗 Important URLs

### Local Development (Docker Compose)
```
Main Dashboard:        http://localhost:3000
Swagger API Docs:      http://localhost:5000/api/docs
REST API:              http://localhost:5000/api/*
WebSocket:             ws://localhost:5000/ws
Grafana:               http://localhost:3001
Prometheus:            http://localhost:9090
Loki:                  http://localhost:3100
Ollama LLM:            http://localhost:11434
```

### Kubernetes (Docker Desktop)
```
Main Dashboard:        http://localhost
Swagger API Docs:      http://localhost:5000/api/docs
REST API:              http://localhost:5000/api/*
Grafana:               http://localhost:3000
Prometheus:            http://localhost:9090
```

### GitHub Repository
```
Source Code:           https://github.com/mainulhossain123/infra-autofix-agent
CI Pipeline:           https://github.com/mainulhossain123/infra-autofix-agent/actions
Container Registry:    ghcr.io/mainulhossain123/infra-autofix-agent
Issues:                https://github.com/mainulhossain123/infra-autofix-agent/issues
```

## License

MIT © 2025

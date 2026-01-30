# infra-autofix-agent

[![CI Pipeline](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/ci.yml)
[![Security Scanning](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/security.yml/badge.svg)](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/security.yml)
[![Docker Publish](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/mainulhossain123/infra-autofix-agent/actions/workflows/docker-publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Production-ready auto-remediation platform for containerized infrastructure with real-time monitoring, intelligent incident detection, and automated recovery.

## Features

- 🔍 **Automated Incident Detection** - CPU spikes, memory leaks, high error rates, latency issues
- 🔄 **Self-Healing** - Automatic container restarts with circuit breaker protection
- 📊 **Full Observability Stack** - Grafana dashboards, Prometheus metrics, Loki logs
- ⚡ **Real-time Updates** - WebSocket-based live dashboard
- 🚨 **Smart Alerting** - Configurable thresholds with Prometheus alerts
- 🐳 **Cloud-Native** - Docker/Kubernetes ready with multi-platform support
- 🔐 **Production-Grade** - CI/CD pipelines, security scanning, automated testing

## Quick Start

> **📘 New to the project?** See the [Complete Quick Start Guide](docs/quick-start.md) with step-by-step instructions, screenshots, and troubleshooting.

### Prerequisites

- **Docker Compose**: Docker 20.10+, Docker Compose 2.0+
- **Kubernetes** (optional): kubectl, Helm 3.0+, K8s cluster 1.20+
- **Local Development** (optional): Python 3.11+, Node.js 18+

### Option 1: Run with Docker Compose (Recommended for First-Time Users)

```bash
git clone https://github.com/mainulhossain123/infra-autofix-agent.git
cd infra-autofix-agent
docker compose up -d

# Access services at:
# Dashboard: http://localhost:3000
# Grafana: http://localhost:3001 (admin/admin)
# API: http://localhost:5000
```

### Option 2: Deploy to Kubernetes (Production-Ready)

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

**Docker Compose (Local Development):**

| Service | URL | Credentials |
|---------|-----|-------------|
| React Dashboard | http://localhost:3000 | - |
| **Swagger API Docs** | **http://localhost:5000/api/docs** | - |
| Grafana | http://localhost:3001 | admin/admin |
| Backend API | http://localhost:5000 | - |
| Prometheus | http://localhost:9090 | - |
| Loki | http://localhost:3100 | - |

**Kubernetes (Docker Desktop):**

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| Frontend Dashboard | http://localhost | - | Main monitoring UI |
| **Swagger API Docs** | **http://localhost:5000/api/docs** | - | **Interactive API documentation** |
| Backend API | http://localhost:5000 | - | REST API + WebSocket |
| Grafana | http://localhost:3000 | admin/admin | Dashboards & alerting |
| Prometheus | http://localhost:9090 | - | Metrics database |

> **Note**: Kubernetes on Docker Desktop automatically maps LoadBalancer services to localhost. No port-forwarding needed!

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  React          │────▶│  Flask API   │────▶│  PostgreSQL │
│  Dashboard      │     │  (Python)    │     │  Database   │
│  (Port 3000)    │     │  (Port 5000) │     │  (Port 5432)│
└─────────────────┘     └──────────────┘     └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ Remediation  │
                        │     Bot      │
                        │  (Python)    │
                        └──────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
 ┌─────────────┐      ┌──────────────┐      ┌─────────────┐
 │ Prometheus  │      │   Grafana    │      │    Loki     │
 │  Metrics    │      │  Dashboards  │      │    Logs     │
 └─────────────┘      └──────────────┘      └─────────────┘
```

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

## Monitoring Stack

**Grafana** - Pre-built dashboards at http://localhost:3001 (admin/admin)  
**Prometheus** - Metrics collection at http://localhost:9090  
**Loki + Promtail** - Centralized logging at http://localhost:3100  
**Alerting** - Production-ready rules in `prometheus/alerts.yml`

Key metrics: request rates, latency, incidents, remediations, CPU/memory usage.

**Kubernetes Monitoring:**
- Automatic pod discovery and scraping
- Kubernetes metrics via ServiceMonitor CRDs
- DaemonSet log collection across all nodes

See [docs/observability.md](docs/observability.md) for detailed monitoring guide.

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

## Documentation

- � **[Quick Start Guide](docs/quick-start.md)** - Step-by-step setup for both Docker Compose and Kubernetes
- 📖 [API Reference](docs/API.md) - REST API endpoints and WebSocket events
- 🐳 [Docker Commands](docs/docker.md) - Container management and troubleshooting
- ☸️ [Kubernetes Deployment](docs/kubernetes.md) - K8s manifests, Helm charts, and production best practices
- 🔧 [Operations Guide](docs/operations.md) - Configuration, testing, and maintenance
- 📊 [Observability](docs/observability.md) - Metrics, logs, dashboards, alerts, and troubleshooting
- 🚀 [GitHub Actions](docs/github-actions.md) - CI/CD workflows and deployment pipelines
- 🤝 [Contributing](CONTRIBUTING.md) - Development guidelines and workflow

## License

MIT © 2025

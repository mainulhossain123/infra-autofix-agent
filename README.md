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

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- (Optional) Python 3.11+, Node.js 18+

### Run with Docker

```bash
git clone https://github.com/mainulhossain123/infra-autofix-agent.git
cd infra-autofix-agent
docker compose up --build -d
```

### Access Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| React Dashboard | http://localhost:3000 | - |
| Grafana | http://localhost:3001 | admin/admin |
| API Docs | http://localhost:5000 | - |
| Prometheus | http://localhost:9090 | - |
| Loki | http://localhost:3100 | - |

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

- 📖 [API Reference](docs/API.md) - REST API endpoints and WebSocket events
- 🐳 [Docker Commands](docs/docker.md) - Container management and troubleshooting
- 🔧 [Operations Guide](docs/operations.md) - Configuration and maintenance
- 📊 [Observability](docs/observability.md) - Metrics, logs, dashboards, alerts
- 🚀 [GitHub Actions](docs/github-actions.md) - CI/CD workflows and deployment
- 🤝 [Contributing](CONTRIBUTING.md) - Development guidelines and workflow

## License

MIT © 2025

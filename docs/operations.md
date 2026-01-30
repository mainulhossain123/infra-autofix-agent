# Operations & Troubleshooting

> **For Kubernetes operations**, see [kubernetes.md](kubernetes.md#monitoring--troubleshooting)

## Deployment Testing

### Quick Health Verification

**Docker Compose:**
```powershell
# Check all services are running
docker-compose ps

# Test endpoints
curl http://localhost:3000  # Frontend
curl http://localhost:5000/health  # Backend API
curl http://localhost:3001  # Grafana
curl http://localhost:9090/-/healthy  # Prometheus
```

**Kubernetes (Docker Desktop):**
```powershell
# Check all pods are running
kubectl get pods -n infra-autofix

# Verify services have localhost endpoints
kubectl get svc -n infra-autofix

# Test endpoints
curl http://localhost/  # Frontend Dashboard
curl http://localhost:5000/health  # Backend API
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:9090/-/healthy  # Prometheus

# Watch real-time status
kubectl get pods -n infra-autofix --watch
```

## Service Endpoints

**Docker Compose:**
- Dashboard: http://localhost:3000
- API: http://localhost:5000
- **Swagger API Docs**: http://localhost:5000/api/docs
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090

**Kubernetes (Docker Desktop):**
- Frontend Dashboard: http://localhost (port 80)
- Backend API: http://localhost:5000
- **Swagger API Docs**: http://localhost:5000/api/docs
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## Common issues
- Port conflicts: ensure 3000/5000/9090 are free
- Database not ready: wait 10–20s; backend retries
- Health check failing: check `ar_app` logs; verify `.env`

## Updating configuration
Use API to update thresholds without redeploying.
```json
PUT /api/config
{
  "key": "error_rate_threshold",
  "value": 0.10
}
```
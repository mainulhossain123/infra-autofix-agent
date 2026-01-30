# Quick Start Guide

Choose your deployment method based on your needs:

## 🐳 Option 1: Docker Compose (Recommended for Local Development)

**Best for:** Quick testing, local development, learning the system

### Prerequisites
- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- 8GB RAM available
- Ports available: 3000, 3001, 5000, 5432, 8000, 9090, 3100

### 1. Start All Services

```powershell
# Clone the repository
git clone https://github.com/mainulhossain123/infra-autofix-agent.git
cd infra-autofix-agent

# Start everything with one command
docker-compose up -d

# Check all services are running
docker-compose ps
```

**Expected output:**
```
NAME               STATUS    PORTS
ar_app             Up        0.0.0.0:5000->5000/tcp
ar_bot             Up        0.0.0.0:8000->8000/tcp
ar_frontend        Up        0.0.0.0:3000->80/tcp
ar_grafana         Up        0.0.0.0:3001->3000/tcp
ar_loki            Up        0.0.0.0:3100->3100/tcp
ar_postgres        Up        0.0.0.0:5432->5432/tcp
ar_prometheus      Up        0.0.0.0:9090->9090/tcp
ar_promtail        Up
```

### 2. Access Services

| Service | URL | Credentials | Description |
|---------|-----|-------------|-------------|
| **React Dashboard** | [http://localhost:3000](http://localhost:3000) | None | Main monitoring UI, incidents, remediation history |
| **Backend API** | [http://localhost:5000](http://localhost:5000) | None | REST API, health endpoints, metrics |
| **API Documentation** | [http://localhost:5000/api/docs](http://localhost:5000/api/docs) | None | **Swagger UI** - Interactive API docs & testing |
| **API Health** | [http://localhost:5000/health](http://localhost:5000/health) | None | Backend health check |
| **Prometheus Metrics** | [http://localhost:5000/metrics](http://localhost:5000/metrics) | None | Application metrics endpoint |
| **Grafana** | [http://localhost:3001](http://localhost:3001) | admin / admin | Dashboards, visualization, alerting |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | None | Metrics database, PromQL queries |
| **Loki** | [http://localhost:3100](http://localhost:3100) | None | Log aggregation API |

### 3. Verify Everything Works

```powershell
# Test backend API
Invoke-WebRequest http://localhost:5000/health

# Test frontend
Invoke-WebRequest http://localhost:3000

# Test Grafana
Invoke-WebRequest http://localhost:3001/api/health

# Test Prometheus
Invoke-WebRequest http://localhost:9090/-/healthy
```

All should return `StatusCode : 200`

### 4. Explore the System

**A. Open the React Dashboard**
1. Go to [http://localhost:3000](http://localhost:3000)
2. View real-time metrics on the Dashboard page
3. Check Incidents for any detected issues
4. View Remediation History to see bot actions

**B. Open Grafana Dashboards**
1. Go to [http://localhost:3001](http://localhost:3001)
2. Login with: `admin` / `admin`
3. Navigate to **Dashboards** → Browse
4. Open **System Overview** dashboard
5. Open **Incidents Dashboard** for detailed analytics

**C. Explore API with Swagger UI**
1. Go to [http://localhost:5000/api/docs](http://localhost:5000/api/docs)
2. Browse all available endpoints organized by category
3. Click **Try it out** on any endpoint
4. Fill in parameters and click **Execute**
5. See real-time request/response data
6. Test incidents, configuration, and trigger endpoints

**D. Query Prometheus**
1. Go to [http://localhost:9090](http://localhost:9090)
2. Try these queries:
   - `up` - See which services are up
   - `cpu_usage_percent` - Current CPU usage
   - `error_rate` - Application error rate
   - `response_time_ms` - API response times

### 5. Trigger a Test Incident

```powershell
# Simulate CPU spike
Invoke-WebRequest -Uri "http://localhost:5000/api/trigger/cpu-spike?duration=60" -Method POST

# Watch the dashboard: http://localhost:3000
# Watch in Grafana: http://localhost:3001
# See metrics in Prometheus: http://localhost:9090
```

The bot should detect the issue and log remediation actions!

### 6. View Logs

```powershell
# View all logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f app       # Backend application
docker-compose logs -f bot       # Remediation bot
docker-compose logs -f frontend  # React dashboard
```

### 7. Stop Services

```powershell
# Stop all services (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

---

## ☸️ Option 2: Kubernetes (Recommended for Production)

**Best for:** Production deployments, cloud environments, auto-scaling, high availability

### Prerequisites
- Kubernetes cluster 1.20+ running
  - **Local**: Docker Desktop with Kubernetes enabled, Minikube, or Kind
  - **Cloud**: AWS EKS, Google GKE, or Azure AKS
- `kubectl` CLI installed and configured
- Helm 3.0+ installed (for Helm deployment method)
- 4GB RAM available per node

### Setup Docker Desktop Kubernetes

If using Docker Desktop:

1. Open **Docker Desktop Settings**
2. Go to **Kubernetes** tab
3. Check **Enable Kubernetes**
4. Select **Kubeadm** (simpler than kind)
5. Click **Apply & Restart**
6. Wait 2-5 minutes for Kubernetes to start

Verify it's running:
```powershell
kubectl cluster-info
kubectl get nodes
```

### 1. Deploy with Helm (Recommended)

```powershell
# Clone the repository (if not done)
git clone https://github.com/mainulhossain123/infra-autofix-agent.git
cd infra-autofix-agent

# Deploy to development environment
helm install infra-autofix ./helm/infra-autofix `
  --namespace infra-autofix `
  --create-namespace `
  --values ./helm/infra-autofix/values.yaml

# OR use the deployment script
.\scripts\deploy-k8s.ps1 -Method helm -Environment dev
```

**Expected output:**
```
NAME: infra-autofix
LAST DEPLOYED: ...
NAMESPACE: infra-autofix
STATUS: deployed
REVISION: 1
```

### 2. Wait for Pods to Start

```powershell
# Watch pods starting up
kubectl get pods -n infra-autofix --watch

# Wait for all pods to be Running
kubectl wait --for=condition=ready pod --all -n infra-autofix --timeout=300s
```

**Expected output (after ~2 minutes):**
```
NAME                        READY   STATUS    RESTARTS   AGE
app-xxxxxxxxxx-xxxxx        1/1     Running   0          2m
app-xxxxxxxxxx-xxxxx        1/1     Running   0          2m
bot-xxxxxxxxxx-xxxxx        1/1     Running   0          2m
frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
grafana-xxxxxxxxxx-xxxxx    1/1     Running   0          2m
loki-0                      1/1     Running   0          2m
postgres-0                  1/1     Running   0          2m
prometheus-0                1/1     Running   0          2m
promtail-xxxxx              1/1     Running   0          2m
```

### 3. Access Services (Docker Desktop)

Docker Desktop automatically maps LoadBalancer services to `localhost`:

```powershell
# Verify services are exposed
kubectl get svc -n infra-autofix
```

**Expected output:**
```
NAME         TYPE           EXTERNAL-IP   PORT(S)
app          LoadBalancer   localhost     5000:xxxxx/TCP
frontend     LoadBalancer   localhost     80:xxxxx/TCP
grafana      LoadBalancer   localhost     3000:xxxxx/TCP
prometheus   LoadBalancer   localhost     9090:xxxxx/TCP
```

### Service URLs (Docker Desktop)

| Service | URL | Credentials | Description |
|---------|-----|-------------|-------------|
| **React Dashboard** | [http://localhost](http://localhost) | None | Main monitoring UI (port 80) |
| **Backend API** | [http://localhost:5000](http://localhost:5000) | None | REST API, WebSocket server |
| **API Documentation** | [http://localhost:5000/api/docs](http://localhost:5000/api/docs) | None | **Swagger UI** - Interactive API docs |
| **API Health** | [http://localhost:5000/health](http://localhost:5000/health) | None | Backend health check |
| **Prometheus Metrics** | [http://localhost:5000/metrics](http://localhost:5000/metrics) | None | Application metrics |
| **Grafana** | [http://localhost:3000](http://localhost:3000) | admin / admin | Dashboards, alerting |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | None | Metrics database |

> **Note:** No port-forwarding needed with Docker Desktop! Services are directly accessible.

### 4. Access Services (Other Kubernetes Providers)

If using Minikube, Kind, or cloud providers where LoadBalancer shows `<pending>`:

```powershell
# Terminal 1: Forward frontend
kubectl port-forward svc/frontend 80:80 -n infra-autofix

# Terminal 2: Forward backend API
kubectl port-forward svc/app 5000:5000 -n infra-autofix

# Terminal 3: Forward Grafana
kubectl port-forward svc/grafana 3000:3000 -n infra-autofix

# Terminal 4: Forward Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n infra-autofix
```

Then access same URLs as above.

### 5. Verify Everything Works

```powershell
# Check all pods are running
kubectl get pods -n infra-autofix

# Check persistent volumes are bound
kubectl get pvc -n infra-autofix

# Test endpoints
Invoke-WebRequest http://localhost/
Invoke-WebRequest http://localhost:5000/health
Invoke-WebRequest http://localhost:3000/api/health
Invoke-WebRequest http://localhost:9090/-/healthy
```

All should return `StatusCode : 200`

### 6. Configure Grafana Dashboards

**First-time setup** (Dashboards need to be created manually in K8s):

1. Go to [http://localhost:3000](http://localhost:3000)
2. Login: `admin` / `admin`
3. Click **+** → **Import dashboard**
4. Upload the dashboard JSON files from `grafana/dashboards/`:
   - `overview.json` - System overview
   - `incidents.json` - Incidents analytics
5. Datasources (Prometheus & Loki) are auto-configured!

### 7. Explore the System

Same as Docker Compose section above - all features work identically!

### 8. View Logs

```powershell
# View application logs
kubectl logs -f deployment/app -n infra-autofix

# View bot logs
kubectl logs -f deployment/bot -n infra-autofix

# View Grafana logs
kubectl logs -f deployment/grafana -n infra-autofix

# View all logs from app pods
kubectl logs -l app=app -n infra-autofix --tail=100
```

### 9. Scale Services

```powershell
# Scale app manually
kubectl scale deployment app --replicas=5 -n infra-autofix

# Check HPA (auto-scaling)
kubectl get hpa -n infra-autofix

# HPA will automatically scale between 2-10 replicas based on CPU/memory
```

### 10. Cleanup

```powershell
# Delete using Helm
helm uninstall infra-autofix -n infra-autofix

# Delete namespace (removes everything including data)
kubectl delete namespace infra-autofix
```

---

## 🔍 Comparison: Which Should I Use?

### Use Docker Compose When:
- ✅ Learning the system for the first time
- ✅ Local development and testing
- ✅ Quick prototyping or demos
- ✅ Single machine deployment
- ✅ Don't need auto-scaling or HA
- ✅ Want fastest startup (~30 seconds)

### Use Kubernetes When:
- ✅ Production deployments
- ✅ Need auto-scaling (2-10 replicas based on load)
- ✅ High availability required
- ✅ Multi-node clusters
- ✅ Cloud environments (AWS/GCP/Azure)
- ✅ Advanced monitoring/observability
- ✅ Rolling updates and zero-downtime deployments

---

## 🎯 Next Steps

### After Successful Deployment

1. **Read the Architecture** - [README.md](../README.md#architecture)
2. **Explore Observability** - [docs/observability.md](observability.md)
3. **Try Manual Controls** - [docs/operations.md](operations.md)
4. **Understand Kubernetes** - [docs/kubernetes.md](kubernetes.md) (if using K8s)
5. **Check API Documentation** - [docs/API.md](API.md)

### Common Issues

See [docs/kubernetes.md](kubernetes.md#troubleshooting) for detailed troubleshooting.

**Docker Compose:**
- Port conflicts → Check if ports 3000, 5000, etc. are free
- Services not starting → Check logs: `docker-compose logs`
- Database not ready → Wait 30s for PostgreSQL to initialize

**Kubernetes:**
- Pods Pending → Check PVC status: `kubectl get pvc -n infra-autofix`
- Services not accessible → Verify LoadBalancer: `kubectl get svc -n infra-autofix`
- Dashboard errors → Check API is reachable: `curl http://localhost:5000/health`

---

## 📞 Support

- **Documentation**: [docs/](../docs/)
- **Issues**: [GitHub Issues](https://github.com/mainulhossain123/infra-autofix-agent/issues)
- **Operations Guide**: [docs/operations.md](operations.md)

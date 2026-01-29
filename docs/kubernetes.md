# Kubernetes Deployment Guide

Complete guide to deploying infra-autofix-agent on Kubernetes with raw manifests or Helm.

> **💡 Docker Desktop Users**: This deployment is optimized for Docker Desktop Kubernetes. All services use LoadBalancer type which Docker Desktop maps to `localhost` automatically. No port-forwarding needed!

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster 1.20+ (local: Minikube, Kind, Docker Desktop; cloud: GKE, EKS, AKS)
- `kubectl` CLI installed and configured
- (For Helm) Helm 3.0+ installed
- (Optional) Ingress controller (nginx-ingress recommended)

#### Docker Desktop Setup

1. Open Docker Desktop Settings
2. Go to **Kubernetes** tab
3. Check **Enable Kubernetes**
4. Select **Kubeadm** (recommended for simplicity)
5. Click **Apply & Restart**
6. Wait 2-5 minutes for Kubernetes to start
7. Verify: `kubectl cluster-info`

### Verify Cluster Access

```powershell
# Check cluster connection
kubectl cluster-info

# Check nodes
kubectl get nodes

# Ensure you have admin permissions
kubectl auth can-i create deployments --all-namespaces
```

---

## Method 1: Deploy with Raw Kubernetes Manifests

**Best for**: Learning, customization, GitOps workflows

### Step 1: Create Namespace

```powershell
kubectl apply -f k8s/namespace.yaml
```

### Step 2: Deploy Configuration

```powershell
# Create ConfigMap and Secrets
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Verify
kubectl get configmap -n infra-autofix
kubectl get secrets -n infra-autofix
```

### Step 3: Deploy Database

```powershell
# Deploy PostgreSQL
kubectl apply -f k8s/postgres.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n infra-autofix --timeout=120s

# Check status
kubectl get statefulset postgres -n infra-autofix
kubectl get pods -n infra-autofix
```

### Step 4: Deploy Application & Bot

```powershell
# Deploy app and bot
kubectl apply -f k8s/app.yaml
kubectl apply -f k8s/bot.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=app -n infra-autofix --timeout=120s
kubectl wait --for=condition=ready pod -l app=bot -n infra-autofix --timeout=120s

# Check deployment status
kubectl get deployments -n infra-autofix
kubectl get pods -n infra-autofix
```

### Step 5: Deploy Frontend

```powershell
# Deploy frontend
kubectl apply -f k8s/frontend.yaml

# Get LoadBalancer IP (may take a few minutes)
kubectl get svc frontend -n infra-autofix --watch
```

### Step 6: Deploy Observability Stack

```powershell
# Deploy Prometheus
kubectl apply -f k8s/prometheus.yaml

# Deploy Grafana
kubectl apply -f k8s/grafana.yaml

# Deploy Loki and Promtail
kubectl apply -f k8s/loki-promtail.yaml

# Wait for all observability pods
kubectl wait --for=condition=ready pod -l app=prometheus -n infra-autofix --timeout=120s
kubectl wait --for=condition=ready pod -l app=grafana -n infra-autofix --timeout=120s
kubectl wait --for=condition=ready pod -l app=loki -n infra-autofix --timeout=120s

# Check status
kubectl get all -n infra-autofix
```

### Step 7: Access Applications

```powershell
# Get external IPs (Docker Desktop maps to localhost)
kubectl get svc -n infra-autofix
```

**Docker Desktop - Direct Access (No Port-Forwarding Needed!):**

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|----------|
| **Frontend Dashboard** | http://localhost | - | Main monitoring UI, incidents, remediation |
| **Backend API** | http://localhost:5000 | - | REST API, WebSocket, metrics |
| **Grafana** | http://localhost:3000 | admin/admin | Dashboards, visualization, alerting |
| **Prometheus** | http://localhost:9090 | - | Metrics database, PromQL queries |

```powershell
# Open in browser
start http://localhost        # Frontend Dashboard
start http://localhost:3000   # Grafana
start http://localhost:9090   # Prometheus
start http://localhost:5000/health  # API Health Check
```

**Other Kubernetes Providers (Minikube, Cloud):**

If LoadBalancer shows `<pending>`, use port-forwarding:

```powershell
kubectl port-forward svc/frontend 80:80 -n infra-autofix &
kubectl port-forward svc/app 5000:5000 -n infra-autofix &
kubectl port-forward svc/grafana 3000:3000 -n infra-autofix &
kubectl port-forward svc/prometheus 9090:9090 -n infra-autofix &
```

### Step 8: Setup Grafana Dashboards (First-Time Only)

> **⚠️ Important**: Unlike Docker Compose, Kubernetes deployment requires manual dashboard import.

Grafana datasources (Prometheus & Loki) are automatically configured, but dashboards need to be imported:

**Method 1: Import via UI (Recommended)**

1. Open Grafana: http://localhost:3000
2. Login with: `admin` / `admin` (change password when prompted)
3. Click **+** (plus icon) → **Import dashboard**
4. Click **Upload JSON file**
5. Import both dashboards from your local `grafana/dashboards/` folder:
   - `overview.json` - System Overview Dashboard
   - `incidents.json` - Incidents Analytics Dashboard
6. Select **Prometheus** as the datasource when prompted
7. Click **Import**

**Method 2: Copy Dashboards to Pod**

```powershell
# Get Grafana pod name
$GRAFANA_POD = kubectl get pods -n infra-autofix -l app=grafana -o jsonpath='{.items[0].metadata.name}'

# Copy dashboards to pod
kubectl cp ./grafana/dashboards/overview.json $GRAFANA_POD:/var/lib/grafana/dashboards/ -n infra-autofix
kubectl cp ./grafana/dashboards/incidents.json $GRAFANA_POD:/var/lib/grafana/dashboards/ -n infra-autofix

# Restart Grafana to pick up dashboards
kubectl rollout restart deployment/grafana -n infra-autofix
```

**Verify Dashboards:**

1. Go to Grafana → **Dashboards** → **Browse**
2. You should see:
   - **System Overview** - Real-time metrics, service health, resource usage
   - **Incidents Dashboard** - Incident trends, remediation actions, error analysis

---

## Method 2: Deploy with Helm (Recommended)

**Best for**: Production deployments, easy upgrades, environment management

### Step 1: Install Helm Chart

**Development environment:**
```powershell
helm install infra-autofix ./helm/infra-autofix \
  --namespace infra-autofix-dev \
  --create-namespace \
  --values ./helm/infra-autofix/values-dev.yaml
```

**Staging environment:**
```powershell
helm install infra-autofix ./helm/infra-autofix \
  --namespace infra-autofix-staging \
  --create-namespace \
  --values ./helm/infra-autofix/values-staging.yaml
```

**Production environment:**
```powershell
helm install infra-autofix ./helm/infra-autofix \
  --namespace infra-autofix-prod \
  --create-namespace \
  --values ./helm/infra-autofix/values-prod.yaml
```

### Step 2: Check Deployment Status

```powershell
# Check Helm release
helm list -n infra-autofix-prod

# Check all resources
kubectl get all -n infra-autofix-prod

# Check pods status
kubectl get pods -n infra-autofix-prod --watch
```

### Step 3: Access Applications

```powershell
# Get service endpoints
kubectl get svc -n infra-autofix-prod

# Port forward (if needed)
kubectl port-forward svc/frontend 3000:80 -n infra-autofix-prod
```

### Upgrade Deployment

```powershell
# Update values or images
helm upgrade infra-autofix ./helm/infra-autofix \
  --namespace infra-autofix-prod \
  --values ./helm/infra-autofix/values-prod.yaml \
  --reuse-values
```

### Rollback Deployment

```powershell
# View revision history
helm history infra-autofix -n infra-autofix-prod

# Rollback to previous version
helm rollback infra-autofix -n infra-autofix-prod

# Rollback to specific revision
helm rollback infra-autofix 2 -n infra-autofix-prod
```

### Uninstall

```powershell
# Uninstall Helm release
helm uninstall infra-autofix -n infra-autofix-prod

# Delete namespace (removes all resources including PVCs)
kubectl delete namespace infra-autofix-prod
```

---

## Custom Configuration

### Update Database Credentials

```powershell
# Create new secret
kubectl create secret generic app-secrets \
  --from-literal=POSTGRES_USER=myuser \
  --from-literal=POSTGRES_PASSWORD=mypassword \
  --from-literal=GRAFANA_ADMIN_USER=admin \
  --from-literal=GRAFANA_ADMIN_PASSWORD=strongpassword \
  --namespace infra-autofix \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new secrets
kubectl rollout restart deployment/app -n infra-autofix
kubectl rollout restart deployment/bot -n infra-autofix
```

### Scale Applications

```powershell
# Manual scaling
kubectl scale deployment app --replicas=5 -n infra-autofix
kubectl scale deployment frontend --replicas=3 -n infra-autofix

# Check HPA (if enabled)
kubectl get hpa -n infra-autofix

# Edit HPA
kubectl edit hpa app-hpa -n infra-autofix
```

### Update Images

```powershell
# Update to specific version
kubectl set image deployment/app app=ghcr.io/mainulhossain123/infra-autofix-agent-app:v1.2.0 -n infra-autofix

# Check rollout status
kubectl rollout status deployment/app -n infra-autofix

# View rollout history
kubectl rollout history deployment/app -n infra-autofix

# Rollback if needed
kubectl rollout undo deployment/app -n infra-autofix
```

---

## Monitoring & Troubleshooting

### Docker Desktop Specific Issues

**PersistentVolumeClaims Stuck in Pending:**

Docker Desktop uses `hostpath` StorageClass by default. Our manifests are configured for this.

```powershell
# Check StorageClass
kubectl get storageclass
# Should show: hostpath (default)

# Check PVC status
kubectl get pvc -n infra-autofix
# All should show STATUS: Bound

# If PVCs are Pending, check the storageClassName in manifests
kubectl describe pvc postgres-pvc -n infra-autofix
```

**Services Not Accessible:**

```powershell
# Verify services have EXTERNAL-IP set to localhost
kubectl get svc -n infra-autofix

# For LoadBalancer services, Docker Desktop should show:
# EXTERNAL-IP: localhost

# If showing <pending>, the service type needs to be LoadBalancer:
kubectl patch svc app -n infra-autofix -p '{"spec":{"type":"LoadBalancer"}}'
kubectl patch svc prometheus -n infra-autofix -p '{"spec":{"type":"LoadBalancer"}}'
```

**Frontend Can't Reach Backend API:**

Ensure the app service is type LoadBalancer (not ClusterIP):

```powershell
kubectl get svc app -n infra-autofix
# Should show: TYPE=LoadBalancer, EXTERNAL-IP=localhost, PORT(S)=5000:xxxxx/TCP

# Test API from your machine
curl http://localhost:5000/health
# Should return: {"status":"healthy",...}
```

### Check Pod Logs

```powershell
# View logs for specific pod
kubectl logs <pod-name> -n infra-autofix

# Follow logs in real-time
kubectl logs -f deployment/app -n infra-autofix

# View previous container logs (if crashed)
kubectl logs <pod-name> --previous -n infra-autofix

# View logs from all pods with label
kubectl logs -l app=app -n infra-autofix --tail=50
```

### Check Pod Status

```powershell
# Get detailed pod information
kubectl describe pod <pod-name> -n infra-autofix

# Check events
kubectl get events -n infra-autofix --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n infra-autofix
kubectl top nodes
```

### Verify Local Testing

**Quick Health Check (PowerShell):**

```powershell
# Test all services
Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing
Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing
Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing
Invoke-WebRequest -Uri "http://localhost:9090/-/healthy" -UseBasicParsing

# All should return: StatusCode 200
```

**Test Data Flow:**

```powershell
# 1. Check if metrics are being collected
curl http://localhost:5000/metrics

# 2. Query Prometheus for app metrics
curl "http://localhost:9090/api/v1/query?query=up"

# 3. Check Grafana datasources
curl -u admin:admin http://localhost:3000/api/datasources

# 4. Trigger a test incident (CPU spike)
curl -X POST "http://localhost:5000/api/trigger/cpu-spike?duration=30"

# 5. Watch in Grafana: http://localhost:3000
```

**Watch Deployment in Real-Time:**

```powershell
# Terminal 1: Watch pods
kubectl get pods -n infra-autofix --watch

# Terminal 2: Watch services
kubectl get svc -n infra-autofix --watch

# Terminal 3: Follow app logs
kubectl logs -f deployment/app -n infra-autofix

# Terminal 4: Follow bot logs  
kubectl logs -f deployment/bot -n infra-autofix
```

### Debug Failing Pods

```powershell
# Get pod status
kubectl get pods -n infra-autofix

# Describe pod to see errors
kubectl describe pod <pod-name> -n infra-autofix

# Check logs
kubectl logs <pod-name> -n infra-autofix

# Execute shell in pod
kubectl exec -it <pod-name> -n infra-autofix -- /bin/sh

# Check environment variables
kubectl exec <pod-name> -n infra-autofix -- env
```

### Test Database Connectivity

```powershell
# Connect to PostgreSQL pod
kubectl exec -it postgres-0 -n infra-autofix -- psql -U remediation_user -d remediation_db

# Test from app pod
kubectl exec -it deployment/app -n infra-autofix -- python -c "
import psycopg2
conn = psycopg2.connect('postgresql://remediation_user:remediation_pass@postgres:5432/remediation_db')
print('Connection successful!')
conn.close()
"
```

### Check Service Connectivity

```powershell
# Test service DNS
kubectl run test-pod --image=busybox -n infra-autofix --restart=Never -- sleep 3600
kubectl exec test-pod -n infra-autofix -- nslookup app
kubectl exec test-pod -n infra-autofix -- wget -O- http://app:5000/health

# Cleanup
kubectl delete pod test-pod -n infra-autofix
```

---

## Production Best Practices

### 1. Resource Limits

Always set resource requests and limits to prevent resource exhaustion:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### 2. Health Checks

Configure liveness and readiness probes:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/health
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 5
```

### 3. Persistent Storage

Use StorageClasses appropriate for your environment:

```powershell
# List available storage classes
kubectl get storageclass

# Set default storage class
kubectl patch storageclass <storage-class-name> -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

### 4. Backup Databases

```powershell
# Backup PostgreSQL
kubectl exec postgres-0 -n infra-autofix -- pg_dump -U remediation_user remediation_db > backup.sql

# Restore PostgreSQL
cat backup.sql | kubectl exec -i postgres-0 -n infra-autofix -- psql -U remediation_user remediation_db
```

### 5. Enable Autoscaling

HPA is pre-configured in manifests:

```powershell
# Check HPA status
kubectl get hpa -n infra-autofix

# Watch HPA in action
kubectl get hpa -n infra-autofix --watch

# Test autoscaling with load
kubectl run -i --tty load-generator --image=busybox -n infra-autofix --restart=Never -- /bin/sh
# Inside pod: while true; do wget -q -O- http://app:5000/health; done
```

### 6. Security

```powershell
# Use secrets for sensitive data
kubectl create secret generic app-secrets \
  --from-literal=POSTGRES_PASSWORD=$(openssl rand -base64 32) \
  --namespace infra-autofix

# Enable RBAC (already configured in manifests)
kubectl get serviceaccount -n infra-autofix
kubectl get role -n infra-autofix
kubectl get rolebinding -n infra-autofix

# Use network policies (example)
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
  namespace: infra-autofix
spec:
  podSelector:
    matchLabels:
      app: app
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 5000
EOF
```

---

## Cloud Provider Specific Notes

### AWS (EKS)

```powershell
# Use EBS for persistent volumes
# StorageClass: gp3 (recommended) or gp2

# Enable LoadBalancer with ALB
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json
```

### Google Cloud (GKE)

```powershell
# Use GCE persistent disks
# StorageClass: standard-rwo or premium-rwo

# Get external IP
kubectl get svc frontend -n infra-autofix
```

### Azure (AKS)

```powershell
# Use Azure Disks
# StorageClass: managed-premium or default

# Enable Azure monitoring
az aks enable-addons --resource-group <rg> --name <cluster> --addons monitoring
```

---

## Complete Testing Checklist

### ✅ Pre-Deployment Verification

```powershell
# 1. Verify Kubernetes cluster is running
kubectl cluster-info
kubectl get nodes

# 2. Check available storage classes (Docker Desktop should show 'hostpath')
kubectl get storageclass

# 3. Ensure correct context
kubectl config current-context
```

### ✅ Post-Deployment Verification

```powershell
# 1. Check all pods are Running (1/1 READY)
kubectl get pods -n infra-autofix

# 2. Verify all PVCs are Bound
kubectl get pvc -n infra-autofix

# 3. Check services have correct EXTERNAL-IP (localhost for Docker Desktop)
kubectl get svc -n infra-autofix

# 4. Test each service endpoint
Invoke-WebRequest http://localhost/ -UseBasicParsing              # Frontend (200 OK)
Invoke-WebRequest http://localhost:5000/health -UseBasicParsing   # API (200 OK)
Invoke-WebRequest http://localhost:3000/api/health -UseBasicParsing  # Grafana (200 OK)
Invoke-WebRequest http://localhost:9090/-/healthy -UseBasicParsing   # Prometheus (200 OK)

# 5. Verify metrics collection
curl http://localhost:5000/metrics  # Should return Prometheus metrics

# 6. Check Prometheus targets
# Open http://localhost:9090/targets
# All targets should show UP status

# 7. Verify Grafana datasources
curl -u admin:admin http://localhost:3000/api/datasources
# Should list Prometheus and Loki

# 8. Test incident flow
curl -X POST "http://localhost:5000/api/trigger/cpu-spike?duration=30"
# Watch in dashboard: http://localhost

# 9. Check logs are flowing to Loki
# Open Grafana → Explore → Select Loki → Run query: {app="app"}

# 10. Verify HPA is working
kubectl get hpa -n infra-autofix
# Should show current CPU/memory metrics
```

### ✅ Troubleshooting Failed Checks

**Pods not Running:**
```powershell
kubectl describe pod <pod-name> -n infra-autofix
kubectl logs <pod-name> -n infra-autofix
kubectl get events -n infra-autofix --sort-by='.lastTimestamp'
```

**PVCs Pending:**
```powershell
# Check if StorageClass exists
kubectl get storageclass

# For Docker Desktop, ensure manifests use 'hostpath'
kubectl describe pvc <pvc-name> -n infra-autofix
```

**Services not accessible:**
```powershell
# Ensure services are LoadBalancer type with localhost
kubectl get svc -n infra-autofix -o wide

# If needed, patch to LoadBalancer
kubectl patch svc <service-name> -n infra-autofix -p '{"spec":{"type":"LoadBalancer"}}'
```

**Frontend shows "Error Loading Dashboard":**
```powershell
# Check if backend API is accessible from your browser
curl http://localhost:5000/health

# Verify app service is LoadBalancer (not ClusterIP)
kubectl get svc app -n infra-autofix
# Must show: TYPE=LoadBalancer, EXTERNAL-IP=localhost
```

---

## Next Steps

- 📊 [Set up monitoring dashboards](observability.md)
- 🔐 [Configure TLS/SSL with cert-manager](https://cert-manager.io/)
- 🚀 [Set up CI/CD with ArgoCD](https://argo-cd.readthedocs.io/)
- 📈 [Configure HPA with custom metrics](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

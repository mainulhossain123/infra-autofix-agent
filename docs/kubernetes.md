# Kubernetes Deployment Guide

Complete guide to deploying infra-autofix-agent on Kubernetes with raw manifests or Helm.

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster 1.20+ (local: Minikube, Kind, Docker Desktop; cloud: GKE, EKS, AKS)
- `kubectl` CLI installed and configured
- (For Helm) Helm 3.0+ installed
- (Optional) Ingress controller (nginx-ingress recommended)

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
# Get external IPs
kubectl get svc -n infra-autofix

# Port forward for local access (if LoadBalancer not available)
kubectl port-forward svc/frontend 3000:80 -n infra-autofix &
kubectl port-forward svc/app 5000:5000 -n infra-autofix &
kubectl port-forward svc/grafana 3001:3000 -n infra-autofix &
kubectl port-forward svc/prometheus 9090:9090 -n infra-autofix &

# Open in browser
start http://localhost:3000  # Frontend
start http://localhost:3001  # Grafana
start http://localhost:9090  # Prometheus
```

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

## Next Steps

- 📊 [Set up monitoring dashboards](observability.md)
- 🔐 [Configure TLS/SSL with cert-manager](https://cert-manager.io/)
- 🚀 [Set up CI/CD with ArgoCD](https://argo-cd.readthedocs.io/)
- 📈 [Configure HPA with custom metrics](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

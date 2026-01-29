#!/usr/bin/env pwsh
# Kubernetes deployment script for infra-autofix-agent
# Usage: .\deploy-k8s.ps1 [-Method manifest|helm] [-Environment dev|staging|prod]
#
# Examples:
#   .\deploy-k8s.ps1                                    # Default: Helm, dev environment
#   .\deploy-k8s.ps1 -Method helm -Environment dev      # Helm deployment to dev
#   .\deploy-k8s.ps1 -Method manifest                   # Raw K8s manifests
#
# After deployment, access services:
#   Docker Desktop: http://localhost (Frontend), http://localhost:5000 (API)
#                   http://localhost:3000 (Grafana), http://localhost:9090 (Prometheus)
#   Other K8s: Use port-forwarding (see docs/kubernetes.md)

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('manifest', 'helm')]
    [string]$Method = 'helm',
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('dev', 'staging', 'prod')]
    [string]$Environment = 'dev'
)

Write-Host "🚀 Deploying infra-autofix-agent to Kubernetes" -ForegroundColor Green
Write-Host "Method: $Method" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Cyan

# Check prerequisites
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

# Check kubectl
try {
    kubectl version --client --short | Out-Null
    Write-Host "✅ kubectl found" -ForegroundColor Green
} catch {
    Write-Host "❌ kubectl not found. Please install kubectl first." -ForegroundColor Red
    exit 1
}

# Check cluster connection
try {
    kubectl cluster-info | Out-Null
    Write-Host "✅ Connected to Kubernetes cluster" -ForegroundColor Green
} catch {
    Write-Host "❌ Cannot connect to Kubernetes cluster" -ForegroundColor Red
    exit 1
}

if ($Method -eq 'helm') {
    # Check Helm
    try {
        helm version --short | Out-Null
        Write-Host "✅ Helm found" -ForegroundColor Green
    } catch {
        Write-Host "❌ Helm not found. Please install Helm 3.0+ first." -ForegroundColor Red
        exit 1
    }
}

if ($Method -eq 'manifest') {
    Write-Host "`n🔧 Deploying with raw Kubernetes manifests..." -ForegroundColor Yellow
    
    # Create namespace
    Write-Host "Creating namespace..." -ForegroundColor Cyan
    kubectl apply -f k8s/namespace.yaml
    
    # Apply configuration
    Write-Host "Applying configuration..." -ForegroundColor Cyan
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/secrets.yaml
    
    # Deploy database
    Write-Host "Deploying PostgreSQL..." -ForegroundColor Cyan
    kubectl apply -f k8s/postgres.yaml
    Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Cyan
    kubectl wait --for=condition=ready pod -l app=postgres -n infra-autofix --timeout=180s
    
    # Deploy application
    Write-Host "Deploying application..." -ForegroundColor Cyan
    kubectl apply -f k8s/app.yaml
    kubectl wait --for=condition=ready pod -l app=app -n infra-autofix --timeout=180s
    
    # Deploy bot
    Write-Host "Deploying bot..." -ForegroundColor Cyan
    kubectl apply -f k8s/bot.yaml
    kubectl wait --for=condition=ready pod -l app=bot -n infra-autofix --timeout=180s
    
    # Deploy frontend
    Write-Host "Deploying frontend..." -ForegroundColor Cyan
    kubectl apply -f k8s/frontend.yaml
    
    # Deploy observability
    Write-Host "Deploying observability stack..." -ForegroundColor Cyan
    kubectl apply -f k8s/prometheus.yaml
    kubectl apply -f k8s/grafana.yaml
    kubectl apply -f k8s/loki-promtail.yaml
    
    $namespace = "infra-autofix"
} elseif ($Method -eq 'helm') {
    Write-Host "`n🎯 Deploying with Helm..." -ForegroundColor Yellow
    
    $namespace = "infra-autofix-$Environment"
    $valuesFile = "helm/infra-autofix/values-$Environment.yaml"
    
    # Check if values file exists
    if (-not (Test-Path $valuesFile)) {
        Write-Host "❌ Values file not found: $valuesFile" -ForegroundColor Red
        exit 1
    }
    
    # Install or upgrade
    Write-Host "Installing/upgrading Helm release..." -ForegroundColor Cyan
    helm upgrade --install infra-autofix ./helm/infra-autofix `
        --namespace $namespace `
        --create-namespace `
        --values $valuesFile `
        --wait `
        --timeout 10m
}

Write-Host "`n✅ Deployment complete!" -ForegroundColor Green

# Display status
Write-Host "`n📊 Deployment Status:" -ForegroundColor Yellow
kubectl get all -n $namespace

# Get service endpoints
Write-Host "`n🌐 Service Endpoints:" -ForegroundColor Yellow
kubectl get svc -n $namespace

Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Check pod status: kubectl get pods -n $namespace" -ForegroundColor White
Write-Host "2. View logs: kubectl logs -l app=app -n $namespace" -ForegroundColor White
Write-Host "3. Port forward: kubectl port-forward svc/frontend 3000:80 -n $namespace" -ForegroundColor White
Write-Host "4. Access Grafana: kubectl port-forward svc/grafana 3001:3000 -n $namespace" -ForegroundColor White
Write-Host "5. View monitoring: kubectl port-forward svc/prometheus 9090:9090 -n $namespace" -ForegroundColor White

Write-Host "`n🎉 Happy monitoring!" -ForegroundColor Green

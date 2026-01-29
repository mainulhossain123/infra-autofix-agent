#!/bin/bash
# Kubernetes deployment script for infra-autofix-agent
# Usage: ./deploy-k8s.sh [manifest|helm] [dev|staging|prod]

METHOD=${1:-helm}
ENVIRONMENT=${2:-dev}

echo "🚀 Deploying infra-autofix-agent to Kubernetes"
echo "Method: $METHOD"
echo "Environment: $ENVIRONMENT"

# Check prerequisites
echo ""
echo "📋 Checking prerequisites..."

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi
echo "✅ kubectl found"

# Check cluster connection
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi
echo "✅ Connected to Kubernetes cluster"

if [ "$METHOD" == "helm" ]; then
    # Check Helm
    if ! command -v helm &> /dev/null; then
        echo "❌ Helm not found. Please install Helm 3.0+ first."
        exit 1
    fi
    echo "✅ Helm found"
fi

if [ "$METHOD" == "manifest" ]; then
    echo ""
    echo "🔧 Deploying with raw Kubernetes manifests..."
    
    # Create namespace
    echo "Creating namespace..."
    kubectl apply -f k8s/namespace.yaml
    
    # Apply configuration
    echo "Applying configuration..."
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/secrets.yaml
    
    # Deploy database
    echo "Deploying PostgreSQL..."
    kubectl apply -f k8s/postgres.yaml
    echo "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n infra-autofix --timeout=180s
    
    # Deploy application
    echo "Deploying application..."
    kubectl apply -f k8s/app.yaml
    kubectl wait --for=condition=ready pod -l app=app -n infra-autofix --timeout=180s
    
    # Deploy bot
    echo "Deploying bot..."
    kubectl apply -f k8s/bot.yaml
    kubectl wait --for=condition=ready pod -l app=bot -n infra-autofix --timeout=180s
    
    # Deploy frontend
    echo "Deploying frontend..."
    kubectl apply -f k8s/frontend.yaml
    
    # Deploy observability
    echo "Deploying observability stack..."
    kubectl apply -f k8s/prometheus.yaml
    kubectl apply -f k8s/grafana.yaml
    kubectl apply -f k8s/loki-promtail.yaml
    
    NAMESPACE="infra-autofix"
    
elif [ "$METHOD" == "helm" ]; then
    echo ""
    echo "🎯 Deploying with Helm..."
    
    NAMESPACE="infra-autofix-$ENVIRONMENT"
    VALUES_FILE="helm/infra-autofix/values-$ENVIRONMENT.yaml"
    
    # Check if values file exists
    if [ ! -f "$VALUES_FILE" ]; then
        echo "❌ Values file not found: $VALUES_FILE"
        exit 1
    fi
    
    # Install or upgrade
    echo "Installing/upgrading Helm release..."
    helm upgrade --install infra-autofix ./helm/infra-autofix \
        --namespace $NAMESPACE \
        --create-namespace \
        --values $VALUES_FILE \
        --wait \
        --timeout 10m
fi

echo ""
echo "✅ Deployment complete!"

# Display status
echo ""
echo "📊 Deployment Status:"
kubectl get all -n $NAMESPACE

# Get service endpoints
echo ""
echo "🌐 Service Endpoints:"
kubectl get svc -n $NAMESPACE

echo ""
echo "📝 Next Steps:"
echo "1. Check pod status: kubectl get pods -n $NAMESPACE"
echo "2. View logs: kubectl logs -l app=app -n $NAMESPACE"
echo "3. Port forward: kubectl port-forward svc/frontend 3000:80 -n $NAMESPACE"
echo "4. Access Grafana: kubectl port-forward svc/grafana 3001:3000 -n $NAMESPACE"
echo "5. View monitoring: kubectl port-forward svc/prometheus 9090:9090 -n $NAMESPACE"

echo ""
echo "🎉 Happy monitoring!"
